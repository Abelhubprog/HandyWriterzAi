"""
Dynamic Agent Swarm Coordination System
Handles adaptive pipeline branching, writer swarms, and cross-agent memory sharing.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any, Set, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import redis.asyncio as redis
from pydantic import BaseModel
import logging
from collections import defaultdict
import networkx as nx

from .agent_pool import AgentPool, AgentType, AgentInstance
from .resource_manager import ResourceManager
from .distributed_coordinator import Task, TaskStatus, TaskPriority, Workflow

logger = logging.getLogger(__name__)

class SwarmStrategy(Enum):
    PARALLEL = "parallel"  # All agents work simultaneously
    SEQUENTIAL = "sequential"  # Agents work in order
    COMPETITIVE = "competitive"  # Best result wins
    COLLABORATIVE = "collaborative"  # Agents share state
    HIERARCHICAL = "hierarchical"  # Lead agent coordinates others

class ContentType(Enum):
    ACADEMIC_PAPER = "academic_paper"
    DISSERTATION = "dissertation"
    TECHNICAL_REPORT = "technical_report"
    MARKET_RESEARCH = "market_research"
    COMPARATIVE_ESSAY = "comparative_essay"
    CASE_STUDY = "case_study"
    LITERATURE_REVIEW = "literature_review"

@dataclass
class SwarmConfig:
    strategy: SwarmStrategy
    max_agents: int = 5
    timeout_seconds: int = 300
    quality_threshold: float = 0.8
    consensus_threshold: float = 0.7
    memory_sharing: bool = True
    cross_validation: bool = False

@dataclass
class SwarmMemory:
    """Shared memory across swarm agents"""
    terminology: Dict[str, str] = field(default_factory=dict)  # term -> definition
    citations: Set[str] = field(default_factory=set)  # shared citation pool
    context: Dict[str, Any] = field(default_factory=dict)  # shared context
    style_guide: Dict[str, Any] = field(default_factory=dict)  # consistent styling
    decision_log: List[Dict[str, Any]] = field(default_factory=list)  # decision history

@dataclass
class SwarmTask:
    task_id: str
    swarm_id: str
    content_type: ContentType
    section_type: str  # e.g., "introduction", "methodology", "results"
    requirements: Dict[str, Any]
    assigned_agents: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)  # agent_id -> result
    final_result: Optional[Dict[str, Any]] = None
    quality_scores: Dict[str, float] = field(default_factory=dict)  # agent_id -> score
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)

class SwarmCoordinator:
    """Coordinates dynamic agent swarms for parallel content generation"""
    
    def __init__(self, redis_client: redis.Redis, agent_pool: AgentPool, resource_manager: ResourceManager):
        self.redis = redis_client
        self.agent_pool = agent_pool
        self.resource_manager = resource_manager
        
        # Active swarms
        self.active_swarms: Dict[str, Dict[str, Any]] = {}
        self.swarm_memories: Dict[str, SwarmMemory] = {}
        
        # Content type configurations
        self.swarm_configs = self._initialize_swarm_configs()
        
        # Pipeline templates
        self.pipeline_templates = self._initialize_pipeline_templates()
        
        # Quality evaluators
        self.quality_evaluators: Dict[str, Callable] = {}
        
    def _initialize_swarm_configs(self) -> Dict[ContentType, SwarmConfig]:
        """Initialize swarm configurations for different content types"""
        return {
            ContentType.ACADEMIC_PAPER: SwarmConfig(
                strategy=SwarmStrategy.COLLABORATIVE,
                max_agents=4,
                timeout_seconds=600,
                quality_threshold=0.85,
                memory_sharing=True,
                cross_validation=True
            ),
            ContentType.DISSERTATION: SwarmConfig(
                strategy=SwarmStrategy.HIERARCHICAL,
                max_agents=6,
                timeout_seconds=1200,
                quality_threshold=0.9,
                memory_sharing=True,
                cross_validation=True
            ),
            ContentType.TECHNICAL_REPORT: SwarmConfig(
                strategy=SwarmStrategy.PARALLEL,
                max_agents=3,
                timeout_seconds=400,
                quality_threshold=0.8,
                memory_sharing=True,
                cross_validation=False
            ),
            ContentType.MARKET_RESEARCH: SwarmConfig(
                strategy=SwarmStrategy.COMPETITIVE,
                max_agents=4,
                timeout_seconds=500,
                quality_threshold=0.8,
                memory_sharing=False,
                cross_validation=True
            ),
            ContentType.COMPARATIVE_ESSAY: SwarmConfig(
                strategy=SwarmStrategy.COLLABORATIVE,
                max_agents=3,
                timeout_seconds=400,
                quality_threshold=0.85,
                memory_sharing=True,
                cross_validation=True
            ),
            ContentType.CASE_STUDY: SwarmConfig(
                strategy=SwarmStrategy.SEQUENTIAL,
                max_agents=4,
                timeout_seconds=500,
                quality_threshold=0.8,
                memory_sharing=True,
                cross_validation=False
            ),
            ContentType.LITERATURE_REVIEW: SwarmConfig(
                strategy=SwarmStrategy.HIERARCHICAL,
                max_agents=5,
                timeout_seconds=800,
                quality_threshold=0.85,
                memory_sharing=True,
                cross_validation=True
            )
        }
    
    def _initialize_pipeline_templates(self) -> Dict[ContentType, Dict[str, Any]]:
        """Initialize adaptive pipeline templates"""
        return {
            ContentType.ACADEMIC_PAPER: {
                "sections": ["abstract", "introduction", "methodology", "results", "discussion", "conclusion"],
                "parallel_sections": [["introduction", "methodology"], ["results", "discussion"]],
                "dependencies": {
                    "abstract": ["introduction", "methodology", "results", "discussion", "conclusion"],
                    "results": ["methodology"],
                    "discussion": ["results"],
                    "conclusion": ["discussion"]
                },
                "agent_specializations": {
                    "introduction": ["reasoning", "literature"],
                    "methodology": ["technical", "structured"],
                    "results": ["analysis", "visualization"],
                    "discussion": ["reasoning", "synthesis"],
                    "conclusion": ["synthesis", "academic"]
                }
            },
            ContentType.DISSERTATION: {
                "sections": ["abstract", "introduction", "literature_review", "methodology", "results", "discussion", "conclusion"],
                "parallel_sections": [["introduction", "literature_review"], ["results", "discussion"]],
                "dependencies": {
                    "abstract": ["literature_review", "methodology", "results", "discussion", "conclusion"],
                    "methodology": ["literature_review"],
                    "results": ["methodology"],
                    "discussion": ["results", "literature_review"],
                    "conclusion": ["discussion"]
                },
                "agent_specializations": {
                    "literature_review": ["research", "synthesis", "citation"],
                    "methodology": ["technical", "structured", "academic"],
                    "results": ["analysis", "statistics", "visualization"],
                    "discussion": ["reasoning", "synthesis", "academic"],
                    "conclusion": ["synthesis", "academic", "future_work"]
                }
            },
            ContentType.TECHNICAL_REPORT: {
                "sections": ["executive_summary", "introduction", "technical_analysis", "implementation", "recommendations"],
                "parallel_sections": [["technical_analysis", "implementation"]],
                "dependencies": {
                    "executive_summary": ["technical_analysis", "implementation", "recommendations"],
                    "recommendations": ["technical_analysis", "implementation"]
                },
                "agent_specializations": {
                    "technical_analysis": ["technical", "analysis", "code"],
                    "implementation": ["technical", "code", "structured"],
                    "recommendations": ["business", "technical", "structured"]
                }
            }
        }
    
    async def create_swarm(
        self,
        swarm_id: str,
        content_type: ContentType,
        requirements: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> str:
        """Create a new agent swarm for content generation"""
        
        config = self.swarm_configs[content_type]
        template = self.pipeline_templates.get(content_type, {})
        
        # Initialize swarm memory
        self.swarm_memories[swarm_id] = SwarmMemory()
        
        # Create swarm metadata
        swarm_data = {
            "swarm_id": swarm_id,
            "content_type": content_type.value,
            "config": asdict(config),
            "template": template,
            "requirements": requirements,
            "user_id": user_id,
            "status": "initializing",
            "created_at": datetime.utcnow().isoformat(),
            "tasks": {}
        }
        
        self.active_swarms[swarm_id] = swarm_data
        
        # Store in Redis
        await self.redis.hset(
            "handywriterz:swarms",
            swarm_id,
            json.dumps(swarm_data, default=str)
        )
        
        logger.info(f"Created swarm {swarm_id} for content type {content_type.value}")
        return swarm_id
    
    async def generate_adaptive_pipeline(
        self,
        swarm_id: str,
        complexity_score: float,
        file_count: int = 0,
        special_requirements: List[str] = None
    ) -> List[SwarmTask]:
        """Generate an adaptive pipeline based on complexity and requirements"""
        
        if swarm_id not in self.active_swarms:
            raise ValueError(f"Swarm {swarm_id} not found")
        
        swarm_data = self.active_swarms[swarm_id]
        content_type = ContentType(swarm_data["content_type"])
        template = swarm_data["template"]
        requirements = swarm_data["requirements"]
        special_requirements = special_requirements or []
        
        # Base sections from template
        sections = template.get("sections", ["introduction", "body", "conclusion"])
        parallel_sections = template.get("parallel_sections", [])
        dependencies = template.get("dependencies", {})
        agent_specializations = template.get("agent_specializations", {})
        
        # Adapt pipeline based on complexity
        if complexity_score > 8.0:
            # High complexity: add more specialized sections
            if "detailed_analysis" not in sections:
                sections.insert(-1, "detailed_analysis")  # Before conclusion
            if "validation" not in sections:
                sections.insert(-1, "validation")
        elif complexity_score < 4.0:
            # Low complexity: simplify pipeline
            sections = [s for s in sections if s not in ["detailed_analysis", "validation"]]
        
        # Adapt based on file count
        if file_count > 10:
            if "file_synthesis" not in sections:
                sections.insert(1, "file_synthesis")  # After introduction
        
        # Adapt based on special requirements
        if "multilingual" in special_requirements:
            sections.append("translation_review")
        if "plagiarism_check" in special_requirements:
            sections.append("originality_verification")
        if "citation_audit" in special_requirements:
            sections.append("citation_validation")
        
        # Create swarm tasks
        tasks = []
        for section in sections:
            task = SwarmTask(
                task_id=f"{swarm_id}_{section}_{uuid.uuid4().hex[:8]}",
                swarm_id=swarm_id,
                content_type=content_type,
                section_type=section,
                requirements={
                    **requirements,
                    "section_focus": section,
                    "specializations": agent_specializations.get(section, []),
                    "dependencies": dependencies.get(section, []),
                    "complexity_score": complexity_score
                }
            )
            tasks.append(task)
        
        # Store tasks in swarm data
        swarm_data["tasks"] = {task.task_id: asdict(task) for task in tasks}
        swarm_data["pipeline"] = {
            "sections": sections,
            "parallel_sections": parallel_sections,
            "dependencies": dependencies,
            "adapted_for": {
                "complexity": complexity_score,
                "file_count": file_count,
                "special_requirements": special_requirements
            }
        }
        
        # Update Redis
        await self.redis.hset(
            "handywriterz:swarms",
            swarm_id,
            json.dumps(swarm_data, default=str)
        )
        
        logger.info(f"Generated adaptive pipeline for swarm {swarm_id}: {len(tasks)} tasks")
        return tasks
    
    async def execute_swarm_strategy(
        self,
        swarm_id: str,
        tasks: List[SwarmTask]
    ) -> Dict[str, Any]:
        """Execute swarm tasks using the configured strategy"""
        
        if swarm_id not in self.active_swarms:
            raise ValueError(f"Swarm {swarm_id} not found")
        
        swarm_data = self.active_swarms[swarm_id]
        config = SwarmConfig(**swarm_data["config"])
        content_type = ContentType(swarm_data["content_type"])
        
        swarm_data["status"] = "executing"
        
        try:
            if config.strategy == SwarmStrategy.PARALLEL:
                results = await self._execute_parallel_strategy(swarm_id, tasks, config)
            elif config.strategy == SwarmStrategy.SEQUENTIAL:
                results = await self._execute_sequential_strategy(swarm_id, tasks, config)
            elif config.strategy == SwarmStrategy.COMPETITIVE:
                results = await self._execute_competitive_strategy(swarm_id, tasks, config)
            elif config.strategy == SwarmStrategy.COLLABORATIVE:
                results = await self._execute_collaborative_strategy(swarm_id, tasks, config)
            elif config.strategy == SwarmStrategy.HIERARCHICAL:
                results = await self._execute_hierarchical_strategy(swarm_id, tasks, config)
            else:
                raise ValueError(f"Unknown swarm strategy: {config.strategy}")
            
            swarm_data["status"] = "completed"
            swarm_data["completed_at"] = datetime.utcnow().isoformat()
            swarm_data["results"] = results
            
            logger.info(f"Swarm {swarm_id} completed using {config.strategy.value} strategy")
            return results
            
        except Exception as e:
            swarm_data["status"] = "failed"
            swarm_data["error"] = str(e)
            logger.error(f"Swarm {swarm_id} failed: {e}")
            raise
        
        finally:
            # Update Redis
            await self.redis.hset(
                "handywriterz:swarms",
                swarm_id,
                json.dumps(swarm_data, default=str)
            )
    
    async def _execute_parallel_strategy(
        self,
        swarm_id: str,
        tasks: List[SwarmTask],
        config: SwarmConfig
    ) -> Dict[str, Any]:
        """Execute tasks in parallel for maximum speed"""
        
        # Group tasks that can run in parallel
        dependency_graph = self._build_dependency_graph(tasks)
        execution_levels = self._get_execution_levels(dependency_graph)
        
        results = {}
        
        for level, level_tasks in execution_levels.items():
            logger.info(f"Executing level {level} with {len(level_tasks)} tasks")
            
            # Execute all tasks in this level concurrently
            level_coroutines = []
            for task in level_tasks:
                coro = self._execute_single_task(swarm_id, task, config)
                level_coroutines.append(coro)
            
            # Wait for all tasks in this level to complete
            level_results = await asyncio.gather(*level_coroutines, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(level_results):
                task = level_tasks[i]
                if isinstance(result, Exception):
                    logger.error(f"Task {task.task_id} failed: {result}")
                    task.status = TaskStatus.FAILED
                    task.error_message = str(result)
                else:
                    task.status = TaskStatus.COMPLETED
                    task.final_result = result
                    results[task.section_type] = result
                    
                    # Update swarm memory if enabled
                    if config.memory_sharing:
                        await self._update_swarm_memory(swarm_id, task, result)
        
        return results
    
    async def _execute_collaborative_strategy(
        self,
        swarm_id: str,
        tasks: List[SwarmTask],
        config: SwarmConfig
    ) -> Dict[str, Any]:
        """Execute tasks with agents collaborating and sharing context"""
        
        results = {}
        swarm_memory = self.swarm_memories[swarm_id]
        
        # Sort tasks by dependencies
        sorted_tasks = self._topological_sort(tasks)
        
        for task in sorted_tasks:
            logger.info(f"Collaboratively executing task {task.task_id}")
            
            # Enhance task requirements with shared context
            task.requirements.update({
                "shared_terminology": swarm_memory.terminology,
                "shared_citations": list(swarm_memory.citations),
                "shared_context": swarm_memory.context,
                "style_guide": swarm_memory.style_guide,
                "previous_decisions": swarm_memory.decision_log[-5:]  # Last 5 decisions
            })
            
            # Execute with multiple agents for collaboration
            agent_count = min(3, config.max_agents)  # Max 3 agents for collaboration
            agent_results = []
            
            for i in range(agent_count):
                try:
                    result = await self._execute_single_task(swarm_id, task, config, agent_index=i)
                    agent_results.append(result)
                except Exception as e:
                    logger.warning(f"Agent {i} failed for task {task.task_id}: {e}")
            
            if not agent_results:
                raise Exception(f"All agents failed for task {task.task_id}")
            
            # Synthesize results from multiple agents
            final_result = await self._synthesize_collaborative_results(
                task, agent_results, swarm_memory
            )
            
            task.status = TaskStatus.COMPLETED
            task.final_result = final_result
            results[task.section_type] = final_result
            
            # Update swarm memory with consensus
            await self._update_swarm_memory(swarm_id, task, final_result)
        
        return results
    
    async def _execute_competitive_strategy(
        self,
        swarm_id: str,
        tasks: List[SwarmTask],
        config: SwarmConfig
    ) -> Dict[str, Any]:
        """Execute tasks competitively with multiple agents, best result wins"""
        
        results = {}
        
        for task in tasks:
            logger.info(f"Competitively executing task {task.task_id}")
            
            # Run multiple agents competitively
            agent_count = min(config.max_agents, 4)  # Max 4 for competition
            competitive_coroutines = []
            
            for i in range(agent_count):
                coro = self._execute_single_task(swarm_id, task, config, agent_index=i)
                competitive_coroutines.append(coro)
            
            # Wait for all agents to complete
            agent_results = await asyncio.gather(*competitive_coroutines, return_exceptions=True)
            
            # Filter successful results
            valid_results = []
            for i, result in enumerate(agent_results):
                if not isinstance(result, Exception):
                    # Evaluate quality
                    quality_score = await self._evaluate_result_quality(task, result)
                    valid_results.append((quality_score, result, i))
            
            if not valid_results:
                raise Exception(f"All agents failed for competitive task {task.task_id}")
            
            # Select best result
            valid_results.sort(key=lambda x: x[0], reverse=True)
            best_score, best_result, winning_agent = valid_results[0]
            
            logger.info(f"Agent {winning_agent} won for task {task.task_id} with score {best_score:.3f}")
            
            task.status = TaskStatus.COMPLETED
            task.final_result = best_result
            task.quality_scores = {f"agent_{i}": score for score, _, i in valid_results}
            results[task.section_type] = best_result
        
        return results
    
    async def _execute_hierarchical_strategy(
        self,
        swarm_id: str,
        tasks: List[SwarmTask],
        config: SwarmConfig
    ) -> Dict[str, Any]:
        """Execute tasks with a lead agent coordinating specialist agents"""
        
        results = {}
        
        # Designate lead agent (highest capability agent)
        lead_agent = await self.agent_pool.get_best_agent(
            AgentType.SPECIALIST,
            capabilities={"reasoning", "coordination", "synthesis"}
        )
        
        if not lead_agent:
            # Fallback to collaborative strategy
            return await self._execute_collaborative_strategy(swarm_id, tasks, config)
        
        for task in tasks:
            logger.info(f"Hierarchically executing task {task.task_id} with lead agent {lead_agent.agent_id}")
            
            # Lead agent creates subtasks and coordination plan
            coordination_plan = await self._create_coordination_plan(lead_agent, task, config)
            
            # Execute subtasks with specialist agents
            subtask_results = {}
            for subtask_id, subtask_spec in coordination_plan.get("subtasks", {}).items():
                specialist_result = await self._execute_specialist_subtask(
                    swarm_id, subtask_spec, config
                )
                subtask_results[subtask_id] = specialist_result
            
            # Lead agent synthesizes final result
            final_result = await self._synthesize_hierarchical_result(
                lead_agent, task, subtask_results, coordination_plan
            )
            
            task.status = TaskStatus.COMPLETED
            task.final_result = final_result
            results[task.section_type] = final_result
        
        return results
    
    def _build_dependency_graph(self, tasks: List[SwarmTask]) -> nx.DiGraph:
        """Build a dependency graph from tasks"""
        graph = nx.DiGraph()
        
        # Add all tasks as nodes
        for task in tasks:
            graph.add_node(task.task_id, task=task)
        
        # Add dependency edges
        for task in tasks:
            for dep in task.requirements.get("dependencies", []):
                # Find dependent task
                dep_task = next((t for t in tasks if t.section_type == dep), None)
                if dep_task:
                    graph.add_edge(dep_task.task_id, task.task_id)
        
        return graph
    
    def _get_execution_levels(self, graph: nx.DiGraph) -> Dict[int, List[SwarmTask]]:
        """Get tasks grouped by execution level (topological levels)"""
        levels = {}
        
        # Get topological generations
        for level, node_set in enumerate(nx.topological_generations(graph)):
            levels[level] = [graph.nodes[node_id]["task"] for node_id in node_set]
        
        return levels
    
    def _topological_sort(self, tasks: List[SwarmTask]) -> List[SwarmTask]:
        """Sort tasks topologically based on dependencies"""
        graph = self._build_dependency_graph(tasks)
        sorted_nodes = list(nx.topological_sort(graph))
        return [graph.nodes[node_id]["task"] for node_id in sorted_nodes]
    
    async def _execute_single_task(
        self,
        swarm_id: str,
        task: SwarmTask,
        config: SwarmConfig,
        agent_index: int = 0
    ) -> Dict[str, Any]:
        """Execute a single task with an assigned agent"""
        
        # Select appropriate agent based on task requirements
        required_capabilities = set(task.requirements.get("specializations", []))
        
        async with self.agent_pool.acquire_agent_context(
            AgentType.WRITER,  # Default to writer type
            task.task_id,
            required_capabilities
        ) as agent:
            
            task.assigned_agents.append(agent.agent_id)
            
            # Get optimal provider for this agent/task combination
            provider_result = await self.resource_manager.select_optimal_provider(
                AgentType.WRITER,
                required_capabilities=list(required_capabilities),
                max_cost=config.timeout_seconds * 0.01  # Rough cost estimate
            )
            
            if not provider_result:
                raise Exception("No suitable provider available")
            
            provider, model = provider_result
            
            # Execute task (this would call the actual agent implementation)
            # For now, return a mock result
            start_time = datetime.utcnow()
            
            # Simulate agent execution
            await asyncio.sleep(0.1)  # Simulate processing time
            
            result = {
                "content": f"Generated {task.section_type} content for {task.content_type.value}",
                "agent_id": agent.agent_id,
                "provider": provider,
                "model": model,
                "execution_time": (datetime.utcnow() - start_time).total_seconds(),
                "quality_indicators": {
                    "word_count": 500,
                    "coherence_score": 0.85,
                    "relevance_score": 0.90,
                    "academic_tone": 0.88
                }
            }
            
            # Record usage
            await self.resource_manager.record_request(
                provider=provider,
                model=model,
                cost=0.01,  # Mock cost
                success=True,
                response_time=result["execution_time"]
            )
            
            return result
    
    async def _update_swarm_memory(
        self,
        swarm_id: str,
        task: SwarmTask,
        result: Dict[str, Any]
    ):
        """Update shared swarm memory with task results"""
        
        if swarm_id not in self.swarm_memories:
            return
        
        memory = self.swarm_memories[swarm_id]
        
        # Extract and store terminology
        terminology = result.get("terminology", {})
        memory.terminology.update(terminology)
        
        # Extract and store citations
        citations = result.get("citations", [])
        memory.citations.update(citations)
        
        # Update shared context
        context_updates = result.get("context", {})
        memory.context.update(context_updates)
        
        # Update style guide
        style_updates = result.get("style_guide", {})
        memory.style_guide.update(style_updates)
        
        # Log decision
        decision = {
            "task_id": task.task_id,
            "section_type": task.section_type,
            "timestamp": datetime.utcnow().isoformat(),
            "key_decisions": result.get("decisions", [])
        }
        memory.decision_log.append(decision)
        
        # Keep only last 20 decisions
        if len(memory.decision_log) > 20:
            memory.decision_log = memory.decision_log[-20:]
        
        logger.debug(f"Updated swarm memory for {swarm_id}")
    
    async def _synthesize_collaborative_results(
        self,
        task: SwarmTask,
        agent_results: List[Dict[str, Any]],
        swarm_memory: SwarmMemory
    ) -> Dict[str, Any]:
        """Synthesize results from multiple collaborative agents"""
        
        # Simple synthesis - in practice, this would use LLM for intelligent merging
        best_result = max(agent_results, 
                         key=lambda r: r.get("quality_indicators", {}).get("coherence_score", 0))
        
        # Merge insights from all agents
        merged_insights = []
        for result in agent_results:
            merged_insights.extend(result.get("insights", []))
        
        best_result["insights"] = list(set(merged_insights))  # Remove duplicates
        best_result["collaboration_score"] = len(agent_results)
        
        return best_result
    
    async def _evaluate_result_quality(self, task: SwarmTask, result: Dict[str, Any]) -> float:
        """Evaluate the quality of a task result"""
        
        quality_indicators = result.get("quality_indicators", {})
        
        # Weight different quality factors
        weights = {
            "coherence_score": 0.3,
            "relevance_score": 0.3,
            "academic_tone": 0.2,
            "completeness": 0.2
        }
        
        total_score = 0.0
        for indicator, weight in weights.items():
            score = quality_indicators.get(indicator, 0.5)  # Default middle score
            total_score += score * weight
        
        return total_score
    
    async def _create_coordination_plan(
        self,
        lead_agent: AgentInstance,
        task: SwarmTask,
        config: SwarmConfig
    ) -> Dict[str, Any]:
        """Create a coordination plan for hierarchical execution"""
        
        # Mock coordination plan - in practice, lead agent would generate this
        plan = {
            "strategy": "divide_and_conquer",
            "subtasks": {
                "research": {
                    "type": "research",
                    "requirements": {"focus": "background", "depth": "detailed"}
                },
                "structure": {
                    "type": "structure",
                    "requirements": {"format": "academic", "sections": ["intro", "body", "conclusion"]}
                },
                "content": {
                    "type": "content",
                    "requirements": {"tone": "academic", "style": "formal"}
                }
            },
            "coordination_points": ["research_complete", "structure_approved"],
            "quality_gates": ["coherence_check", "citation_validation"]
        }
        
        return plan
    
    async def _execute_specialist_subtask(
        self,
        swarm_id: str,
        subtask_spec: Dict[str, Any],
        config: SwarmConfig
    ) -> Dict[str, Any]:
        """Execute a specialist subtask"""
        
        # Mock specialist execution
        return {
            "subtask_type": subtask_spec["type"],
            "result": f"Completed {subtask_spec['type']} subtask",
            "quality_score": 0.85,
            "execution_time": 5.0
        }
    
    async def _synthesize_hierarchical_result(
        self,
        lead_agent: AgentInstance,
        task: SwarmTask,
        subtask_results: Dict[str, Any],
        coordination_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize final result from hierarchical execution"""
        
        # Mock synthesis by lead agent
        synthesized_result = {
            "content": f"Hierarchically generated {task.section_type}",
            "lead_agent": lead_agent.agent_id,
            "subtask_count": len(subtask_results),
            "coordination_strategy": coordination_plan["strategy"],
            "quality_indicators": {
                "coherence_score": 0.88,
                "relevance_score": 0.92,
                "academic_tone": 0.90,
                "completeness": 0.85
            },
            "subtask_results": subtask_results
        }
        
        return synthesized_result
    
    async def get_swarm_status(self, swarm_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a swarm"""
        
        if swarm_id in self.active_swarms:
            return self.active_swarms[swarm_id]
        
        # Try to load from Redis
        swarm_data = await self.redis.hget("handywriterz:swarms", swarm_id)
        if swarm_data:
            return json.loads(swarm_data)
        
        return None
    
    async def cancel_swarm(self, swarm_id: str) -> bool:
        """Cancel a running swarm"""
        
        if swarm_id not in self.active_swarms:
            return False
        
        swarm_data = self.active_swarms[swarm_id]
        swarm_data["status"] = "cancelled"
        swarm_data["cancelled_at"] = datetime.utcnow().isoformat()
        
        # Update Redis
        await self.redis.hset(
            "handywriterz:swarms",
            swarm_id,
            json.dumps(swarm_data, default=str)
        )
        
        # Clean up memory
        if swarm_id in self.swarm_memories:
            del self.swarm_memories[swarm_id]
        
        logger.info(f"Cancelled swarm {swarm_id}")
        return True