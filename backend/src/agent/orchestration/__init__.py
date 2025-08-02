"""
Advanced Multi-Agent Orchestration System
Enterprise-grade agent coordination with distributed processing, intelligent resource management,
dynamic swarm coordination, advanced caching, and comprehensive monitoring.
"""

from .agent_pool import (
    AgentPool,
    AgentType,
    AgentInstance,
    AgentStatus,
    AgentMetrics,
    CircuitBreaker
)

from .distributed_coordinator import (
    DistributedCoordinator,
    Task,
    TaskStatus,
    TaskPriority,
    Workflow
)

from .resource_manager import (
    ResourceManager,
    BudgetConfig,
    ProviderConfig,
    RateLimitConfig,
    ProviderStatus,
    UsageMetrics,
    TokenBucket
)

from .swarm_coordinator import (
    SwarmCoordinator,
    SwarmStrategy,
    ContentType,
    SwarmConfig,
    SwarmMemory,
    SwarmTask
)

from .cache_manager import (
    CacheManager,
    CacheLevel,
    CacheStrategy,
    CacheEntry,
    CacheStats,
    LRUCache
)

from .monitoring import (
    MonitoringSystem,
    DistributedTracer,
    MetricsCollector,
    AlertManager,
    MetricType,
    AlertLevel,
    TraceSpan,
    SystemMetrics,
    Alert
)

from .integration import (
    AdvancedOrchestrationSystem,
    OrchestrationConfig,
    create_orchestration_system
)

__all__ = [
    # Agent Pool
    "AgentPool",
    "AgentType", 
    "AgentInstance",
    "AgentStatus",
    "AgentMetrics",
    "CircuitBreaker",
    
    # Distributed Coordination
    "DistributedCoordinator",
    "Task",
    "TaskStatus", 
    "TaskPriority",
    "Workflow",
    
    # Resource Management
    "ResourceManager",
    "BudgetConfig",
    "ProviderConfig",
    "RateLimitConfig",
    "ProviderStatus",
    "UsageMetrics",
    "TokenBucket",
    
    # Swarm Coordination
    "SwarmCoordinator",
    "SwarmStrategy",
    "ContentType",
    "SwarmConfig",
    "SwarmMemory",
    "SwarmTask",
    
    # Caching
    "CacheManager",
    "CacheLevel",
    "CacheStrategy", 
    "CacheEntry",
    "CacheStats",
    "LRUCache",
    
    # Monitoring
    "MonitoringSystem",
    "DistributedTracer",
    "MetricsCollector",
    "AlertManager",
    "MetricType",
    "AlertLevel",
    "TraceSpan",
    "SystemMetrics",
    "Alert",
    
    # Integration
    "AdvancedOrchestrationSystem",
    "OrchestrationConfig",
    "create_orchestration_system"
]

# Version info
__version__ = "1.0.0"
__author__ = "HandyWriterzAI Team"
__description__ = "Advanced Multi-Agent Orchestration System for Academic Writing"