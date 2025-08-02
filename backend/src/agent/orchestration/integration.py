"""
Integration Module for Advanced Multi-Agent Orchestration
Ties together all orchestration components for seamless operation.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime
import redis.asyncio as redis
import asyncpg
import logging

from .agent_pool import AgentPool, AgentType, AgentInstance
from .distributed_coordinator import (
    DistributedCoordinator, 
    Task, 
    TaskStatus, 
    TaskPriority, 
    Workflow
)
from .resource_manager import ResourceManager, BudgetConfig
from .swarm_coordinator import (
    SwarmCoordinator, 
    ContentType, 
    SwarmStrategy,
    SwarmConfig
)
from .cache_manager import CacheManager
from .monitoring import MonitoringSystem

logger = logging.getLogger(__name__)

@dataclass
class OrchestrationConfig:
    redis_url: str = "redis://localhost:6379"
    postgres_url: Optional[str] = None
    instance_id: Optional[str] = None
    enable_monitoring: bool = True
    enable_caching: bool = True
    enable_swarm_coordination: bool = True
    budget_config: Optional[BudgetConfig] = None

class AdvancedOrchestrationSystem:
    """
    Advanced Multi-Agent Orchestration System
    Integrates all components for production-ready agent coordination
    """
    
    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.redis: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        
        # Core components
        self.agent_pool: Optional[AgentPool] = None
        self.distributed_coordinator: Optional[DistributedCoordinator] = None
        self.resource_manager: Optional[ResourceManager] = None
        self.swarm_coordinator: Optional[SwarmCoordinator] = None
        self.cache_manager: Optional[CacheManager] = None
        self.monitoring_system: Optional[MonitoringSystem] = None
        
        # System state
        self.running = False
        self.startup_time: Optional[datetime] = None
        
    async def initialize(self):
        """Initialize all orchestration components"""
        logger.info("Initializing Advanced Orchestration System...")
        
        # Initialize Redis connection
        self.redis = redis.from_url(self.config.redis_url)
        await self.redis.ping()
        logger.info("Redis connection established")
        
        # Initialize PostgreSQL connection pool if configured
        if self.config.postgres_url:
            self.db_pool = await asyncpg.create_pool(self.config.postgres_url)
            logger.info("PostgreSQL connection pool established")
            
            # Ensure database schema exists
            await self._ensure_database_schema()
        
        # Initialize core components
        self.agent_pool = AgentPool(self.redis)
        
        self.distributed_coordinator = DistributedCoordinator(
            self.redis, 
            self.config.instance_id
        )
        
        self.resource_manager = ResourceManager(
            self.redis,
            self.config.budget_config or BudgetConfig()
        )
        
        if self.config.enable_swarm_coordination:
            self.swarm_coordinator = SwarmCoordinator(
                self.redis,
                self.agent_pool,
                self.resource_manager
            )
        
        if self.config.enable_caching:
            self.cache_manager = CacheManager(self.redis, self.db_pool)
        
        if self.config.enable_monitoring:
            self.monitoring_system = MonitoringSystem(self.redis)
        
        # Register task handlers
        await self._register_task_handlers()
        
        logger.info("All components initialized successfully")
    
    async def start(self):
        """Start the orchestration system"""
        if self.running:
            logger.warning("Orchestration system is already running")
            return
        
        logger.info("Starting Advanced Orchestration System...")
        
        # Start distributed coordinator
        await self.distributed_coordinator.start()
        
        # Start cache manager
        if self.cache_manager:
            await self.cache_manager.start()
        
        # Start monitoring system
        if self.monitoring_system:
            await self.monitoring_system.start()
        
        self.running = True
        self.startup_time = datetime.utcnow()
        
        logger.info("Advanced Orchestration System started successfully")
    
    async def stop(self):
        """Stop the orchestration system"""
        if not self.running:
            return
        
        logger.info("Stopping Advanced Orchestration System...")
        
        # Stop monitoring system
        if self.monitoring_system:
            await self.monitoring_system.stop()
        
        # Stop cache manager
        if self.cache_manager:
            await self.cache_manager.stop()
        
        # Stop distributed coordinator
        if self.distributed_coordinator:
            await self.distributed_coordinator.stop()
        
        # Close database connections
        if self.db_pool:
            await self.db_pool.close()
        
        # Close Redis connection
        if self.redis:
            await self.redis.close()
        
        self.running = False
        logger.info("Advanced Orchestration System stopped")
    
    async def submit_academic_writing_request(
        self,
        user_id: str,
        content_type: ContentType,
        requirements: Dict[str, Any],
        files: List[Dict[str, Any]] = None,
        complexity_score: float = 5.0
    ) -> str:
        """Submit a complete academic writing request"""
        
        workflow_id = f"workflow_{user_id}_{int(datetime.utcnow().timestamp())}"
        
        # Create workflow
        workflow = Workflow(
            workflow_id=workflow_id,
            user_id=user_id,
            workflow_type=content_type.value,
            metadata={
                "requirements": requirements,
                "files": files or [],
                "complexity_score": complexity_score
            }
        )
        
        if self.swarm_coordinator:
            # Use advanced swarm coordination
            swarm_id = f"swarm_{workflow_id}"
            
            # Create swarm
            await self.swarm_coordinator.create_swarm(
                swarm_id=swarm_id,
                content_type=content_type,
                requirements=requirements,
                user_id=user_id
            )
            
            # Generate adaptive pipeline
            tasks = await self.swarm_coordinator.generate_adaptive_pipeline(
                swarm_id=swarm_id,
                complexity_score=complexity_score,
                file_count=len(files) if files else 0,
                special_requirements=requirements.get("special_requirements", [])
            )
            
            # Convert swarm tasks to workflow tasks
            workflow_tasks = []
            for swarm_task in tasks:
                task = Task(
                    task_id=swarm_task.task_id,
                    workflow_id=workflow_id,
                    agent_type=AgentType.WRITER,  # Default, will be refined
                    payload={
                        "swarm_id": swarm_id,
                        "swarm_task": swarm_task,
                        "requirements": requirements
                    },
                    priority=TaskPriority.MEDIUM
                )
                workflow_tasks.append(task)
            
            workflow.tasks = workflow_tasks
            
            # Execute swarm strategy
            asyncio.create_task(
                self._execute_swarm_workflow(swarm_id, tasks)
            )
        
        else:
            # Use traditional linear pipeline
            workflow.tasks = await self._create_linear_workflow_tasks(
                workflow_id, content_type, requirements, complexity_score
            )
        
        # Submit workflow to distributed coordinator
        await self.distributed_coordinator.submit_workflow(workflow)
        
        logger.info(f"Submitted academic writing request: {workflow_id}")
        return workflow_id
    
    async def _execute_swarm_workflow(self, swarm_id: str, tasks: List[Any]):
        """Execute swarm workflow asynchronously"""
        try:
            results = await self.swarm_coordinator.execute_swarm_strategy(swarm_id, tasks)
            logger.info(f"Swarm workflow {swarm_id} completed with {len(results)} sections")
        except Exception as e:
            logger.error(f"Swarm workflow {swarm_id} failed: {e}")
    
    async def _create_linear_workflow_tasks(
        self,
        workflow_id: str,
        content_type: ContentType,
        requirements: Dict[str, Any],
        complexity_score: float
    ) -> List[Task]:
        """Create traditional linear workflow tasks"""
        
        tasks = []
        
        # Research phase
        research_task = Task(
            task_id=f"{workflow_id}_research",
            workflow_id=workflow_id,
            agent_type=AgentType.SEARCH,
            payload={
                "query": requirements.get("topic", ""),
                "content_type": content_type.value,
                "depth": "comprehensive" if complexity_score > 7 else "standard"
            },
            priority=TaskPriority.HIGH
        )
        tasks.append(research_task)
        
        # Aggregation phase
        aggregation_task = Task(
            task_id=f"{workflow_id}_aggregation",
            workflow_id=workflow_id,
            agent_type=AgentType.AGGREGATOR,
            payload={
                "research_results": "from_research_task",
                "synthesis_type": "academic"
            },
            dependencies=[research_task.task_id],
            priority=TaskPriority.MEDIUM
        )
        tasks.append(aggregation_task)
        
        # Writing phase
        writing_task = Task(
            task_id=f"{workflow_id}_writing",
            workflow_id=workflow_id,
            agent_type=AgentType.WRITER,
            payload={
                "content_type": content_type.value,
                "requirements": requirements,
                "research_data": "from_aggregation_task"
            },
            dependencies=[aggregation_task.task_id],
            priority=TaskPriority.HIGH
        )
        tasks.append(writing_task)
        
        # Evaluation phase
        evaluation_task = Task(
            task_id=f"{workflow_id}_evaluation",
            workflow_id=workflow_id,
            agent_type=AgentType.EVALUATOR,
            payload={
                "content": "from_writing_task",
                "evaluation_criteria": ["academic_quality", "coherence", "citations"]
            },
            dependencies=[writing_task.task_id],
            priority=TaskPriority.MEDIUM
        )
        tasks.append(evaluation_task)
        
        return tasks
    
    async def _register_task_handlers(self):
        """Register task handlers with the distributed coordinator"""
        
        # Search task handler
        async def search_handler(agent: AgentInstance, payload: Dict[str, Any]):
            start_time = datetime.utcnow()
            
            # Get optimal provider
            provider_result = await self.resource_manager.select_optimal_provider(
                AgentType.SEARCH,
                required_capabilities=["search", "web"],
                user_id=payload.get("user_id")
            )
            
            if not provider_result:
                raise Exception("No suitable search provider available")
            
            provider, model = provider_result
            
            # Simulate search execution
            query = payload.get("query", "")
            depth = payload.get("depth", "standard")
            
            # Check cache first
            if self.cache_manager:
                cached_result = await self.cache_manager.get(
                    "search_results",
                    query=query,
                    depth=depth
                )
                if cached_result:
                    logger.info(f"Cache hit for search query: {query}")
                    return cached_result
            
            # Execute search (mock implementation)
            await asyncio.sleep(2.0)  # Simulate search time
            
            result = {
                "query": query,
                "results": [
                    {"title": f"Search result {i}", "content": f"Content {i}"}
                    for i in range(5)
                ],
                "provider": provider,
                "model": model,
                "execution_time": (datetime.utcnow() - start_time).total_seconds()
            }
            
            # Cache result
            if self.cache_manager:
                await self.cache_manager.set(
                    "search_results",
                    result,
                    ttl_seconds=3600,
                    query=query,
                    depth=depth
                )
            
            # Record metrics
            if self.monitoring_system:
                await self.monitoring_system.metrics_collector.record_agent_request(
                    agent_id=agent.agent_id,
                    agent_type=agent.agent_type.value,
                    provider=provider,
                    model=model,
                    duration_seconds=result["execution_time"],
                    cost_usd=0.01,  # Mock cost
                    success=True,
                    quality_score=0.85
                )
            
            return result
        
        # Writer task handler
        async def writer_handler(agent: AgentInstance, payload: Dict[str, Any]):
            start_time = datetime.utcnow()
            
            # Check if this is a swarm task
            if "swarm_task" in payload:
                swarm_task = payload["swarm_task"]
                # Handle swarm-specific writing
                content_type = swarm_task.content_type
                section_type = swarm_task.section_type
            else:
                content_type = ContentType(payload.get("content_type", "academic_paper"))
                section_type = "full_document"
            
            # Get optimal provider
            provider_result = await self.resource_manager.select_optimal_provider(
                AgentType.WRITER,
                required_capabilities=["reasoning", "academic", "structured_output"],
                user_id=payload.get("user_id")
            )
            
            if not provider_result:
                raise Exception("No suitable writing provider available")
            
            provider, model = provider_result
            
            # Execute writing (mock implementation)
            await asyncio.sleep(5.0)  # Simulate writing time
            
            result = {
                "content": f"Generated {section_type} for {content_type.value}",
                "section_type": section_type,
                "word_count": 1500,
                "provider": provider,
                "model": model,
                "quality_indicators": {
                    "coherence_score": 0.88,
                    "academic_tone": 0.90,
                    "citation_count": 12
                },
                "execution_time": (datetime.utcnow() - start_time).total_seconds()
            }
            
            # Record metrics
            if self.monitoring_system:
                await self.monitoring_system.metrics_collector.record_agent_request(
                    agent_id=agent.agent_id,
                    agent_type=agent.agent_type.value,
                    provider=provider,
                    model=model,
                    duration_seconds=result["execution_time"],
                    cost_usd=0.05,  # Mock cost
                    success=True,
                    quality_score=result["quality_indicators"]["coherence_score"]
                )
            
            return result
        
        # Register handlers
        self.distributed_coordinator.register_task_handler(AgentType.SEARCH, search_handler)
        self.distributed_coordinator.register_task_handler(AgentType.WRITER, writer_handler)
        
        logger.info("Task handlers registered successfully")
    
    async def _ensure_database_schema(self):
        """Ensure required database schema exists"""
        if not self.db_pool:
            return
        
        async with self.db_pool.acquire() as conn:
            # Create cache entries table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key VARCHAR(255) PRIMARY KEY,
                    value BYTEA NOT NULL,
                    expires_at TIMESTAMP,
                    tags TEXT[],
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_entries_expires_at 
                ON cache_entries (expires_at)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_entries_tags 
                ON cache_entries USING GIN (tags)
            """)
            
            logger.info("Database schema ensured")
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive workflow status"""
        if not self.distributed_coordinator:
            return None
        
        # Get basic workflow status
        workflow_status = await self.distributed_coordinator.get_workflow_status(workflow_id)
        
        if not workflow_status:
            return None
        
        # Enhance with swarm information if available
        if self.swarm_coordinator:
            swarm_id = f"swarm_{workflow_id}"
            swarm_status = await self.swarm_coordinator.get_swarm_status(swarm_id)
            if swarm_status:
                workflow_status["swarm_coordination"] = swarm_status
        
        # Add performance metrics
        if self.monitoring_system:
            # Get workflow metrics from monitoring
            workflow_status["performance_metrics"] = {
                "tracked": True,
                "monitoring_active": True
            }
        
        return workflow_status
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "system": {
                "running": self.running,
                "startup_time": self.startup_time.isoformat() if self.startup_time else None,
                "uptime_seconds": (
                    (datetime.utcnow() - self.startup_time).total_seconds() 
                    if self.startup_time else 0
                )
            },
            "components": {
                "agent_pool": self.agent_pool is not None,
                "distributed_coordinator": self.distributed_coordinator is not None,
                "resource_manager": self.resource_manager is not None,
                "swarm_coordinator": self.swarm_coordinator is not None,
                "cache_manager": self.cache_manager is not None,
                "monitoring_system": self.monitoring_system is not None
            }
        }
        
        # Get detailed component status
        if self.distributed_coordinator:
            coordinator_stats = await self.distributed_coordinator.get_system_stats()
            status["distributed_coordination"] = coordinator_stats
        
        if self.resource_manager:
            budget_status = await self.resource_manager.get_budget_status()
            provider_metrics = await self.resource_manager.get_provider_metrics()
            status["resource_management"] = {
                "budget": budget_status,
                "providers": provider_metrics
            }
        
        if self.cache_manager:
            cache_stats = await self.cache_manager.get_cache_stats()
            status["caching"] = cache_stats
        
        if self.monitoring_system:
            dashboard = await self.monitoring_system.get_system_dashboard()
            status["monitoring"] = dashboard
        
        return status
    
    async def register_agent(
        self,
        agent_type: AgentType,
        provider: str,
        model: str,
        capabilities: Set[str] = None,
        max_concurrent: int = 1
    ) -> str:
        """Register a new agent with the system"""
        
        agent_id = f"{agent_type.value}_{provider}_{model}_{int(datetime.utcnow().timestamp())}"
        
        agent_instance = AgentInstance(
            agent_id=agent_id,
            agent_type=agent_type,
            provider=provider,
            model=model,
            capabilities=capabilities or set(),
            max_concurrent=max_concurrent
        )
        
        success = await self.agent_pool.register_agent(agent_instance)
        
        if success:
            logger.info(f"Registered new agent: {agent_id}")
            return agent_id
        else:
            raise Exception(f"Failed to register agent: {agent_id}")
    
    # Context manager support
    async def __aenter__(self):
        await self.initialize()
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


# Factory function for easy initialization
async def create_orchestration_system(
    redis_url: str = "redis://localhost:6379",
    postgres_url: Optional[str] = None,
    enable_all_features: bool = True,
    budget_config: Optional[BudgetConfig] = None
) -> AdvancedOrchestrationSystem:
    """Factory function to create and initialize orchestration system"""
    
    config = OrchestrationConfig(
        redis_url=redis_url,
        postgres_url=postgres_url,
        enable_monitoring=enable_all_features,
        enable_caching=enable_all_features,
        enable_swarm_coordination=enable_all_features,
        budget_config=budget_config
    )
    
    system = AdvancedOrchestrationSystem(config)
    await system.initialize()
    
    return system