"""
Agent Pool Management System for Distributed Multi-Agent Orchestration
Handles dynamic scaling, load balancing, and fault tolerance for agent instances.
"""

import asyncio
from typing import Dict, List, Optional, Any, Set, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import redis.asyncio as redis
from pydantic import BaseModel
import json
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class AgentType(Enum):
    SEARCH = "search"
    WRITER = "writer"
    EVALUATOR = "evaluator"
    AGGREGATOR = "aggregator"
    SPECIALIST = "specialist"

@dataclass
class AgentMetrics:
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    total_requests: int = 0
    failed_requests: int = 0
    last_activity: datetime = field(default_factory=datetime.utcnow)
    cost_per_request: float = 0.0

@dataclass
class AgentInstance:
    agent_id: str
    agent_type: AgentType
    provider: str
    model: str
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    metrics: AgentMetrics = field(default_factory=AgentMetrics)
    capabilities: Set[str] = field(default_factory=set)
    max_concurrent: int = 1
    current_load: int = 0

class AgentPool:
    """Manages a pool of agent instances with dynamic scaling and load balancing"""
    
    def __init__(self, redis_client: redis.Redis, pool_name: str = "handywriterz"):
        self.redis = redis_client
        self.pool_name = pool_name
        self.agents: Dict[str, AgentInstance] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
    async def register_agent(self, agent: AgentInstance) -> bool:
        """Register a new agent instance in the pool"""
        try:
            self.agents[agent.agent_id] = agent
            self.circuit_breakers[agent.agent_id] = CircuitBreaker(
                failure_threshold=5,
                timeout=30
            )
            
            # Store in Redis for distributed coordination
            await self.redis.hset(
                f"{self.pool_name}:agents",
                agent.agent_id,
                json.dumps({
                    "type": agent.agent_type.value,
                    "provider": agent.provider,
                    "model": agent.model,
                    "status": agent.status.value,
                    "capabilities": list(agent.capabilities),
                    "max_concurrent": agent.max_concurrent,
                    "registered_at": datetime.utcnow().isoformat()
                })
            )
            
            logger.info(f"Registered agent {agent.agent_id} ({agent.agent_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent.agent_id}: {e}")
            return False
    
    async def get_best_agent(
        self, 
        agent_type: AgentType,
        capabilities: Optional[Set[str]] = None,
        exclude_agents: Optional[Set[str]] = None
    ) -> Optional[AgentInstance]:
        """Select the best available agent based on load, performance, and capabilities"""
        
        available_agents = [
            agent for agent in self.agents.values()
            if (agent.agent_type == agent_type and
                agent.status == AgentStatus.IDLE and
                agent.current_load < agent.max_concurrent and
                (not capabilities or capabilities.issubset(agent.capabilities)) and
                (not exclude_agents or agent.agent_id not in exclude_agents) and
                self.circuit_breakers[agent.agent_id].can_execute())
        ]
        
        if not available_agents:
            return None
            
        # Score agents based on multiple factors
        scored_agents = []
        for agent in available_agents:
            score = self._calculate_agent_score(agent)
            scored_agents.append((score, agent))
            
        # Return the highest scoring agent
        scored_agents.sort(key=lambda x: x[0], reverse=True)
        return scored_agents[0][1]
    
    def _calculate_agent_score(self, agent: AgentInstance) -> float:
        """Calculate agent selection score based on performance metrics"""
        metrics = agent.metrics
        
        # Base score from success rate (0-1)
        success_score = metrics.success_rate
        
        # Load score (prefer less loaded agents)
        load_score = 1.0 - (agent.current_load / agent.max_concurrent)
        
        # Response time score (prefer faster agents)
        time_score = max(0, 1.0 - (metrics.avg_response_time / 10.0))  # 10s baseline
        
        # Cost efficiency score (prefer cheaper agents)
        cost_score = max(0, 1.0 - (metrics.cost_per_request / 0.10))  # $0.10 baseline
        
        # Recency score (prefer recently active agents)
        hours_since_activity = (datetime.utcnow() - metrics.last_activity).total_seconds() / 3600
        recency_score = max(0, 1.0 - (hours_since_activity / 24))  # 24h baseline
        
        # Weighted combination
        total_score = (
            success_score * 0.3 +
            load_score * 0.25 +
            time_score * 0.2 +
            cost_score * 0.15 +
            recency_score * 0.1
        )
        
        return total_score
    
    async def acquire_agent(self, agent_id: str, task_id: str) -> bool:
        """Acquire an agent for a specific task"""
        if agent_id not in self.agents:
            return False
            
        agent = self.agents[agent_id]
        
        if agent.current_load >= agent.max_concurrent:
            return False
            
        agent.current_load += 1
        agent.current_task = task_id
        agent.status = AgentStatus.BUSY if agent.current_load == agent.max_concurrent else AgentStatus.IDLE
        
        # Update Redis
        await self.redis.hset(
            f"{self.pool_name}:agents:{agent_id}",
            "current_load",
            agent.current_load
        )
        
        return True
    
    async def release_agent(self, agent_id: str, success: bool = True, response_time: float = 0.0, cost: float = 0.0):
        """Release an agent after task completion"""
        if agent_id not in self.agents:
            return
            
        agent = self.agents[agent_id]
        agent.current_load = max(0, agent.current_load - 1)
        agent.current_task = None
        agent.status = AgentStatus.IDLE
        
        # Update metrics
        metrics = agent.metrics
        metrics.total_requests += 1
        if not success:
            metrics.failed_requests += 1
            await self.circuit_breakers[agent_id].record_failure()
        else:
            await self.circuit_breakers[agent_id].record_success()
            
        metrics.success_rate = 1.0 - (metrics.failed_requests / metrics.total_requests)
        
        if response_time > 0:
            # Exponential moving average for response time
            alpha = 0.1
            metrics.avg_response_time = (alpha * response_time + 
                                       (1 - alpha) * metrics.avg_response_time)
        
        if cost > 0:
            # Exponential moving average for cost
            alpha = 0.1
            metrics.cost_per_request = (alpha * cost + 
                                      (1 - alpha) * metrics.cost_per_request)
        
        metrics.last_activity = datetime.utcnow()
        
        # Update Redis
        await self.redis.hset(
            f"{self.pool_name}:agents:{agent_id}",
            mapping={
                "current_load": agent.current_load,
                "status": agent.status.value,
                "success_rate": metrics.success_rate,
                "avg_response_time": metrics.avg_response_time,
                "total_requests": metrics.total_requests
            }
        )
    
    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get comprehensive pool statistics"""
        stats = {
            "total_agents": len(self.agents),
            "by_type": {},
            "by_status": {},
            "by_provider": {},
            "total_load": 0,
            "total_capacity": 0,
            "avg_success_rate": 0.0,
            "avg_response_time": 0.0
        }
        
        for agent in self.agents.values():
            # By type
            type_key = agent.agent_type.value
            if type_key not in stats["by_type"]:
                stats["by_type"][type_key] = 0
            stats["by_type"][type_key] += 1
            
            # By status
            status_key = agent.status.value
            if status_key not in stats["by_status"]:
                stats["by_status"][status_key] = 0
            stats["by_status"][status_key] += 1
            
            # By provider
            if agent.provider not in stats["by_provider"]:
                stats["by_provider"][agent.provider] = 0
            stats["by_provider"][agent.provider] += 1
            
            # Load and capacity
            stats["total_load"] += agent.current_load
            stats["total_capacity"] += agent.max_concurrent
            
            # Performance metrics
            stats["avg_success_rate"] += agent.metrics.success_rate
            stats["avg_response_time"] += agent.metrics.avg_response_time
        
        # Calculate averages
        if len(self.agents) > 0:
            stats["avg_success_rate"] /= len(self.agents)
            stats["avg_response_time"] /= len(self.agents)
            stats["utilization"] = stats["total_load"] / stats["total_capacity"] if stats["total_capacity"] > 0 else 0
        
        return stats
    
    @asynccontextmanager
    async def acquire_agent_context(self, agent_type: AgentType, task_id: str, capabilities: Optional[Set[str]] = None):
        """Context manager for acquiring and releasing agents"""
        agent = await self.get_best_agent(agent_type, capabilities)
        if not agent:
            raise RuntimeError(f"No available agents for type {agent_type.value}")
        
        success = await self.acquire_agent(agent.agent_id, task_id)
        if not success:
            raise RuntimeError(f"Failed to acquire agent {agent.agent_id}")
        
        start_time = datetime.utcnow()
        try:
            yield agent
            # Record success
            response_time = (datetime.utcnow() - start_time).total_seconds()
            await self.release_agent(agent.agent_id, success=True, response_time=response_time)
        except Exception as e:
            # Record failure
            response_time = (datetime.utcnow() - start_time).total_seconds()
            await self.release_agent(agent.agent_id, success=False, response_time=response_time)
            raise

class CircuitBreaker:
    """Circuit breaker pattern for agent fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def record_failure(self):
        """Record a failure"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    async def record_success(self):
        """Record a success"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            if (self.last_failure_time and 
                datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.timeout)):
                self.state = "HALF_OPEN"
                return True
            return False
        
        # HALF_OPEN state
        return True