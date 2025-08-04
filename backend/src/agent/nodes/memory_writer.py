import json
from datetime import datetime
from typing import Dict, Any
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

from ..base import BaseNode
from ..handywriterz_state import HandyWriterzState
from ...services.memory_integrator import get_memory_integrator
from ...db.models import MemoryType

class MemoryWriter(BaseNode):
    """
    Enhanced memory writer node that analyzes final drafts and conversations
    to create comprehensive long-term memories with importance scoring.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.memory_service = get_memory_integrator()

    async def execute(self, state: HandyWriterzState) -> Dict[str, Any]:
        """
        Analyzes the draft and conversation to create structured memories.
        """
        with tracer.start_as_current_span("enhanced_memory_writer_node") as span:
            span.set_attribute("user_id", state.get("user_id"))
            print("🧠 Executing Enhanced MemoryWriter Node")
            
        final_draft = state.get("final_draft_content")
        user_id = state.get("user_id")
        conversation_id = state.get("conversation_id")
        user_params = state.get("user_params", {})

        if not final_draft or not user_id:
            print("⚠️ MemoryWriter: Missing final_draft or user_id, skipping.")
            return {}

        try:
            # Extract writing fingerprint metrics (legacy compatibility)
            fingerprint = self._calculate_fingerprint(final_draft)
            
            # Create structured memories from workflow
            created_memories = await self._create_workflow_memories(
                state, user_id, conversation_id, user_params, final_draft
            )
            
            # Perform AI reflection if workflow is complete
            reflection_memories = []
            if state.get("workflow_status") == "completed":
                reflection_memories = await self._perform_reflection(
                    state, user_id, conversation_id, final_draft
                )
            
            print(f"✅ Created {len(created_memories)} workflow memories and {len(reflection_memories)} reflection memories")
            
            return {
                "writing_fingerprint": fingerprint,  # Legacy compatibility
                "created_memories": created_memories,
                "reflection_memories": reflection_memories,
                "total_memories_created": len(created_memories) + len(reflection_memories)
            }

        except Exception as e:
            print(f"❌ Enhanced MemoryWriter Error: {e}")
            return {"writing_fingerprint": None, "memory_error": str(e)}

    async def _create_workflow_memories(
        self, 
        state: HandyWriterzState, 
        user_id: str, 
        conversation_id: str,
        user_params: Dict[str, Any], 
        final_draft: str
    ) -> list:
        """Create memories from workflow execution."""
        created_memories = []
        
        try:
            # User preference memories
            if mode := user_params.get("mode"):
                memory_id = await self.memory_service.write_memory(
                    user_id=user_id,
                    content=f"User frequently requests {mode} type documents",
                    memory_type=MemoryType.PREFERENCE,
                    conversation_id=conversation_id,
                    importance_score=0.7,
                    tags=["writing_mode", mode, "preference"],
                    source_summary="User parameter analysis"
                )
                created_memories.append(memory_id)
            
            # Citation style preference
            if citation_style := user_params.get("citation_style"):
                memory_id = await self.memory_service.write_memory(
                    user_id=user_id,
                    content=f"User prefers {citation_style} citation style for academic work",
                    memory_type=MemoryType.PREFERENCE,
                    conversation_id=conversation_id,
                    importance_score=0.8,
                    tags=["citation", citation_style, "academic"],
                    source_summary="Citation style selection"
                )
                created_memories.append(memory_id)
            
            # Research methodology insights
            if research_agenda := state.get("research_agenda"):
                if isinstance(research_agenda, list) and research_agenda:
                    research_focus = research_agenda[0]
                    memory_id = await self.memory_service.write_memory(
                        user_id=user_id,
                        content=f"User's research interests include: {research_focus}",
                        memory_type=MemoryType.SEMANTIC,
                        conversation_id=conversation_id,
                        importance_score=0.6,
                        tags=["research", "academic_focus", "interests"],
                        source_summary="Research agenda analysis"
                    )
                    created_memories.append(memory_id)
            
            # Writing quality assessment
            if evaluation_results := state.get("evaluation_results"):
                if isinstance(evaluation_results, dict):
                    quality_score = evaluation_results.get("overall_score", 0)
                    if quality_score > 0.8:
                        memory_id = await self.memory_service.write_memory(
                            user_id=user_id,
                            content=f"User produces high-quality academic writing (quality score: {quality_score:.2f})",
                            memory_type=MemoryType.EPISODIC,
                            conversation_id=conversation_id,
                            importance_score=0.6,
                            tags=["quality", "performance", "academic_writing"],
                            context={"quality_score": quality_score, "evaluation_date": datetime.now().isoformat()},
                            source_summary="Quality evaluation analysis"
                        )
                        created_memories.append(memory_id)
            
            # Document structure preferences
            if outline := state.get("outline"):
                if isinstance(outline, dict) and outline.get("sections"):
                    section_count = len(outline["sections"])
                    memory_id = await self.memory_service.write_memory(
                        user_id=user_id,
                        content=f"User typically structures documents with {section_count} main sections",
                        memory_type=MemoryType.PREFERENCE,
                        conversation_id=conversation_id,
                        importance_score=0.5,
                        tags=["structure", "outline", "organization"],
                        context={"section_count": section_count},
                        source_summary="Document structure analysis"
                    )
                    created_memories.append(memory_id)
            
            # Word count and length preferences
            word_count = len(final_draft.split())
            if word_count > 1000:
                length_category = "long-form" if word_count > 5000 else "medium-length"
                memory_id = await self.memory_service.write_memory(
                    user_id=user_id,
                    content=f"User typically produces {length_category} documents (approx. {word_count} words)",
                    memory_type=MemoryType.PREFERENCE,
                    conversation_id=conversation_id,
                    importance_score=0.4,
                    tags=["length", "word_count", length_category],
                    context={"word_count": word_count},
                    source_summary="Document length analysis"
                )
                created_memories.append(memory_id)
            
        except Exception as e:
            print(f"⚠️ Error creating workflow memories: {e}")
        
        return created_memories

    async def _perform_reflection(
        self, 
        state: HandyWriterzState, 
        user_id: str, 
        conversation_id: str, 
        final_draft: str
    ) -> list:
        """Perform AI reflection to extract additional memories."""
        try:
            # Build conversation context
            context_parts = []
            
            user_params = state.get("user_params", {})
            if user_prompt := user_params.get("user_prompt") or user_params.get("prompt"):
                context_parts.append(f"User request: {user_prompt}")
            
            if research_agenda := state.get("research_agenda"):
                context_parts.append(f"Research focus: {str(research_agenda)[:500]}")
            
            if evaluation_results := state.get("evaluation_results"):
                context_parts.append(f"Quality metrics: {str(evaluation_results)[:300]}")
            
            conversation_context = "\n".join(context_parts)
            
            # Use the memory service's reflection capability
            reflection_memory_ids = await self.memory_service.reflect_and_extract_memories(
                user_id=user_id,
                conversation_id=conversation_id,
                conversation_context=conversation_context,
                user_response=final_draft[-1500:]  # Last 1500 chars
            )
            
            return reflection_memory_ids
            
        except Exception as e:
            print(f"⚠️ Reflection failed: {e}")
            return []

    def _calculate_fingerprint(self, text: str) -> Dict[str, Any]:
        """Calculates writing style metrics from a given text (legacy compatibility)."""
        words = text.split()
        sentences = text.split('.')
        word_count = len(words)
        sentence_count = len(sentences)

        if word_count == 0 or sentence_count == 0:
            return {
                "avg_sentence_len": 0,
                "lexical_diversity": 0,
                "citation_density": 0,
            }

        # Average sentence length
        avg_sentence_len = word_count / sentence_count

        # Lexical diversity (Type-Token Ratio)
        lexical_diversity = len(set(words)) / word_count if word_count > 0 else 0
        
        # Citation density (simple placeholder)
        citations = text.count("(") + text.count("[")
        citation_density = citations / sentence_count if sentence_count > 0 else 0

        return {
            "avg_sentence_len": round(avg_sentence_len, 2),
            "lexical_diversity": round(lexical_diversity, 3),
            "citation_density": round(citation_density, 3),
        }