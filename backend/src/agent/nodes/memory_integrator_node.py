"""
Enhanced Memory Integrator Node for HandyWriterz Graph System.
Provides intelligent memory retrieval and writing within the agent workflow.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base import BaseNode
from ..handywriterz_state import HandyWriterzState
from ...services.memory_integrator import get_memory_integrator
from ...db.models import MemoryType

logger = logging.getLogger(__name__)


class MemoryIntegratorNode(BaseNode):
    """Enhanced memory integration node with retrieval and contextual augmentation."""
    
    def __init__(self, name: str = "memory_integrator"):
        super().__init__(name)
        self.memory_service = get_memory_integrator()
        self.max_context_length = 2000  # Max context tokens for memory
    
    async def execute(self, state: HandyWriterzState) -> Dict[str, Any]:
        """
        Execute memory integration: retrieve relevant memories and augment context.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with memory context
        """
        try:
            user_id = state.get("user_id")
            conversation_id = state.get("conversation_id")
            user_params = state.get("user_params", {})
            
            if not user_id:
                logger.warning("No user_id found in state, skipping memory integration")
                return {"memory_context": None}
            
            # Extract query context from multiple sources
            query_context = self._extract_query_context(state, user_params)
            
            if not query_context:
                logger.info("No query context found, skipping memory retrieval")
                return {"memory_context": None}
            
            # Determine memory types to search based on task context
            memory_types = self._determine_relevant_memory_types(user_params)
            
            # Retrieve relevant memories
            relevant_memories = await self.memory_service.retrieve_memories(
                user_id=user_id,
                query=query_context,
                conversation_id=conversation_id,
                memory_types=memory_types,
                k=8,  # Retrieve up to 8 memories
                importance_threshold=0.3,
                include_context=True
            )
            
            # Format memory context for LLM consumption
            memory_context = self._format_memory_context(relevant_memories)
            
            # Store memories in state for downstream nodes
            return {
                "memory_context": memory_context,
                "retrieved_memories": relevant_memories,
                "memory_retrieval_stats": {
                    "count": len(relevant_memories),
                    "avg_importance": sum(m["importance_score"] for m in relevant_memories) / len(relevant_memories) if relevant_memories else 0,
                    "query_context": query_context[:200]  # First 200 chars for logging
                }
            }
            
        except Exception as e:
            logger.error(f"Memory integration failed: {e}")
            return {"memory_context": None, "memory_integration_error": str(e)}
    
    def _extract_query_context(self, state: HandyWriterzState, user_params: Dict[str, Any]) -> str:
        """Extract relevant query context from state and user parameters."""
        context_parts = []
        
        # User prompt/query
        if user_prompt := user_params.get("user_prompt") or user_params.get("prompt"):
            context_parts.append(user_prompt.strip())
        
        # Writing mode context
        if mode := user_params.get("mode"):
            context_parts.append(f"Writing mode: {mode}")
        
        # Research agenda if available
        if research_agenda := state.get("research_agenda"):
            if isinstance(research_agenda, list):
                context_parts.extend(research_agenda[:3])  # First 3 research questions
            elif isinstance(research_agenda, str):
                context_parts.append(research_agenda)
        
        # Current draft context (for refinement tasks)
        if current_draft := state.get("current_draft"):
            # Use first 300 chars of current draft for context
            context_parts.append(f"Current draft context: {current_draft[:300]}")
        
        # Outline context
        if outline := state.get("outline"):
            if isinstance(outline, dict):
                # Extract main sections from outline
                sections = outline.get("sections", [])
                if sections:
                    section_titles = [s.get("title", "") for s in sections[:5]]  # First 5 sections
                    context_parts.append(f"Outline sections: {', '.join(section_titles)}")
        
        return " | ".join(context_parts)
    
    def _determine_relevant_memory_types(self, user_params: Dict[str, Any]) -> List[MemoryType]:
        """Determine which memory types are most relevant for the current task."""
        mode = user_params.get("mode", "").lower()
        
        # Task-specific memory type prioritization
        if mode in ["dissertation", "thesis", "research_paper"]:
            return [MemoryType.SEMANTIC, MemoryType.PREFERENCE, MemoryType.PROCEDURAL]
        elif mode in ["essay", "coursework"]:
            return [MemoryType.PREFERENCE, MemoryType.SEMANTIC, MemoryType.EPISODIC]
        elif "outline" in mode or "planning" in mode:
            return [MemoryType.PROCEDURAL, MemoryType.SEMANTIC, MemoryType.PREFERENCE]
        else:
            # Default: prioritize preferences and semantic knowledge
            return [MemoryType.PREFERENCE, MemoryType.SEMANTIC, MemoryType.PROCEDURAL]
    
    def _format_memory_context(self, memories: List[Dict[str, Any]]) -> Optional[str]:
        """Format retrieved memories for LLM context injection."""
        if not memories:
            return None
        
        context_parts = []
        context_parts.append("=== RELEVANT USER MEMORIES ===")
        
        # Group memories by type for better organization
        memory_groups = {}
        for memory in memories:
            mem_type = memory["memory_type"]
            if mem_type not in memory_groups:
                memory_groups[mem_type] = []
            memory_groups[mem_type].append(memory)
        
        # Format each group
        type_labels = {
            "preference": "User Preferences",
            "semantic": "Knowledge & Facts", 
            "procedural": "Skills & Processes",
            "episodic": "Past Experiences",
            "contextual": "Context-Specific Info"
        }
        
        for mem_type, mem_list in memory_groups.items():
            if mem_list:
                context_parts.append(f"\n{type_labels.get(mem_type, mem_type.title())}:")
                for memory in mem_list[:3]:  # Max 3 memories per type
                    importance = memory["importance_score"]
                    similarity = memory["similarity_score"]
                    content = memory["content"]
                    
                    # Truncate long memories
                    if len(content) > 200:
                        content = content[:200] + "..."
                    
                    context_parts.append(
                        f"- {content} (importance: {importance:.2f}, relevance: {similarity:.2f})"
                    )
        
        # Add tags summary if available
        all_tags = []
        for memory in memories:
            all_tags.extend(memory.get("tags", []))
        
        if all_tags:
            unique_tags = list(set(all_tags))[:10]  # Top 10 unique tags
            context_parts.append(f"\nRelevant tags: {', '.join(unique_tags)}")
        
        context_parts.append("=== END MEMORIES ===\n")
        
        full_context = "\n".join(context_parts)
        
        # Truncate if too long
        if len(full_context) > self.max_context_length:
            full_context = full_context[:self.max_context_length] + "... [truncated]"
        
        return full_context


class MemoryWriterNode(BaseNode):
    """Enhanced memory writer node for storing insights from workflow execution."""
    
    def __init__(self, name: str = "memory_writer"):
        super().__init__(name)
        self.memory_service = get_memory_integrator()
    
    async def execute(self, state: HandyWriterzState) -> Dict[str, Any]:
        """
        Execute memory writing: extract and store valuable insights from workflow.
        
        Args:
            state: Current workflow state
            
        Returns:
            Memory writing results
        """
        try:
            user_id = state.get("user_id")
            conversation_id = state.get("conversation_id")
            
            if not user_id:
                logger.warning("No user_id found in state, skipping memory writing")
                return {"memory_writing_result": None}
            
            # Extract insights to memorize
            insights = await self._extract_workflow_insights(state)
            
            # Write memories
            created_memory_ids = []
            for insight in insights:
                try:
                    memory_id = await self.memory_service.write_memory(
                        user_id=user_id,
                        content=insight["content"],
                        memory_type=insight["memory_type"],
                        conversation_id=conversation_id,
                        importance_score=insight.get("importance_score"),
                        tags=insight.get("tags", []),
                        context=insight.get("context"),
                        source_summary="Workflow execution insight"
                    )
                    created_memory_ids.append(memory_id)
                except Exception as e:
                    logger.warning(f"Failed to write memory insight: {e}")
            
            # Perform reflection if this is a completed workflow
            reflection_memories = []
            if state.get("workflow_status") == "completed":
                try:
                    reflection_memories = await self._perform_reflection(state, user_id, conversation_id)
                except Exception as e:
                    logger.warning(f"Reflection failed: {e}")
            
            return {
                "memory_writing_result": {
                    "insights_stored": len(created_memory_ids),
                    "reflection_memories": len(reflection_memories),
                    "created_memory_ids": created_memory_ids + reflection_memories
                }
            }
            
        except Exception as e:
            logger.error(f"Memory writing failed: {e}")
            return {"memory_writing_result": None, "memory_writing_error": str(e)}
    
    async def _extract_workflow_insights(self, state: HandyWriterzState) -> List[Dict[str, Any]]:
        """Extract valuable insights from workflow execution."""
        insights = []
        user_params = state.get("user_params", {})
        
        # User preference insights
        if mode := user_params.get("mode"):
            insights.append({
                "content": f"User frequently uses {mode} writing mode",
                "memory_type": MemoryType.PREFERENCE,
                "importance_score": 0.6,
                "tags": ["writing_mode", mode, "preference"],
                "context": {"source": "user_params", "frequency": 1}
            })
        
        # Citation style preference
        if citation_style := user_params.get("citation_style"):
            insights.append({
                "content": f"User prefers {citation_style} citation style",
                "memory_type": MemoryType.PREFERENCE,
                "importance_score": 0.7,
                "tags": ["citation", citation_style, "preference"],
                "context": {"source": "user_params"}
            })
        
        # Research methodology insights
        if research_agenda := state.get("research_agenda"):
            if isinstance(research_agenda, list) and research_agenda:
                research_focus = research_agenda[0] if research_agenda else ""
                insights.append({
                    "content": f"User's research focuses on: {research_focus}",
                    "memory_type": MemoryType.SEMANTIC,
                    "importance_score": 0.5,
                    "tags": ["research", "methodology", "academic_focus"],
                    "context": {"source": "research_agenda", "topic": research_focus}
                })
        
        # Writing quality patterns
        if evaluation_results := state.get("evaluation_results"):
            if isinstance(evaluation_results, dict):
                quality_score = evaluation_results.get("overall_score", 0)
                if quality_score > 0.8:  # High quality work
                    insights.append({
                        "content": f"User produces high-quality academic work (score: {quality_score:.2f})",
                        "memory_type": MemoryType.EPISODIC,
                        "importance_score": 0.6,
                        "tags": ["quality", "academic_writing", "performance"],
                        "context": {"score": quality_score, "source": "evaluation"}
                    })
        
        # Document structure preferences
        if outline := state.get("outline"):
            if isinstance(outline, dict) and outline.get("sections"):
                section_count = len(outline["sections"])
                insights.append({
                    "content": f"User prefers documents with {section_count} main sections",
                    "memory_type": MemoryType.PREFERENCE,
                    "importance_score": 0.4,
                    "tags": ["structure", "outline", "sections"],
                    "context": {"section_count": section_count, "source": "outline"}
                })
        
        return insights
    
    async def _perform_reflection(
        self, 
        state: HandyWriterzState, 
        user_id: str, 
        conversation_id: str
    ) -> List[str]:
        """Perform AI reflection on completed workflow."""
        try:
            # Build conversation context
            context_parts = []
            
            if user_params := state.get("user_params"):
                context_parts.append(f"User request: {user_params.get('user_prompt', '')}")
            
            if final_draft := state.get("final_draft_content"):
                context_parts.append(f"Final output: {final_draft[-1000:]}")  # Last 1000 chars
            
            if evaluation_results := state.get("evaluation_results"):
                context_parts.append(f"Quality evaluation: {str(evaluation_results)[:500]}")
            
            conversation_context = "\n".join(context_parts)
            
            # Perform reflection
            reflection_memory_ids = await self.memory_service.reflect_and_extract_memories(
                user_id=user_id,
                conversation_id=conversation_id,
                conversation_context=conversation_context,
                user_response=state.get("final_draft_content", "")
            )
            
            return reflection_memory_ids
            
        except Exception as e:
            logger.error(f"Workflow reflection failed: {e}")
            return []


class MemoryMaintenanceNode(BaseNode):
    """Node for performing memory maintenance operations."""
    
    def __init__(self, name: str = "memory_maintenance"):
        super().__init__(name)
        self.memory_service = get_memory_integrator()
    
    async def execute(self, state: HandyWriterzState) -> Dict[str, Any]:
        """Execute memory maintenance for the current user."""
        try:
            user_id = state.get("user_id")
            
            if not user_id:
                return {"maintenance_result": "No user_id provided"}
            
            # Perform maintenance
            await self.memory_service.maintain_memories(user_id=user_id)
            
            # Get updated statistics
            stats = await self.memory_service.get_memory_statistics(user_id)
            
            return {
                "maintenance_result": "completed",
                "memory_statistics": stats
            }
            
        except Exception as e:
            logger.error(f"Memory maintenance failed: {e}")
            return {"maintenance_result": f"failed: {str(e)}"}