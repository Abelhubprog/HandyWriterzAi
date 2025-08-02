"""
Intelligent Resource Management & Load Balancing System
Handles budget-aware routing, API rate limiting, and smart agent selection across providers.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import redis.asyncio as redis
from pydantic import BaseModel
import logging
from collections import defaultdict, deque
import math

from .agent_pool import AgentPool, AgentType, AgentInstance

logger = logging.getLogger(__name__)

class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"

@dataclass
class BudgetConfig:
    daily_limit: float = 100.0  # USD
    hourly_limit: float = 20.0  # USD
    per_request_limit: float = 5.0  # USD
    warning_threshold: float = 0.8  # 80% of limit
    user_daily_limit: float = 10.0  # USD per user

@dataclass
class UsageMetrics:
    total_requests: int = 0
    total_cost: float = 0.0
    avg_cost_per_request: float = 0.0
    success_rate: float = 1.0
    avg_response_time: float = 0.0
    last_request: Optional[datetime] = None

@dataclass
class RateLimitConfig:
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_allowance: int = 10

@dataclass
class ProviderConfig:
    provider_name: str
    models: Dict[str, Dict[str, Any]]  # model_name -> config
    rate_limits: RateLimitConfig
    cost_multiplier: float = 1.0  # Cost adjustment factor
    priority: int = 1  # Higher = preferred
    health_check_url: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)

class TokenBucket:
    """Thread-safe token bucket for rate limiting"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = float(capacity)
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket"""
        async with self._lock:
            now = time.time()
            # Add tokens based on elapsed time
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    async def get_wait_time(self, tokens: int = 1) -> float:
        """Get estimated wait time for tokens to be available"""
        async with self._lock:
            if self.tokens >= tokens:
                return 0.0
            needed_tokens = tokens - self.tokens
            return needed_tokens / self.refill_rate

class ResourceManager:
    """Manages resources, budgets, and load balancing across AI providers"""
    
    def __init__(self, redis_client: redis.Redis, budget_config: BudgetConfig = None):
        self.redis = redis_client
        self.budget_config = budget_config or BudgetConfig()
        
        # Provider configurations
        self.providers: Dict[str, ProviderConfig] = {}
        self.provider_status: Dict[str, ProviderStatus] = {}
        self.provider_metrics: Dict[str, UsageMetrics] = defaultdict(UsageMetrics)
        
        # Rate limiting
        self.rate_limiters: Dict[str, Dict[str, TokenBucket]] = defaultdict(dict)  # provider -> limit_type -> bucket
        
        # Budget tracking
        self.hourly_usage: deque = deque(maxlen=24)  # Last 24 hours
        self.daily_usage: float = 0.0
        
        # Load balancing
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Initialize default providers
        self._initialize_default_providers()
    
    def _initialize_default_providers(self):
        """Initialize default provider configurations"""
        providers = {
            "openai": ProviderConfig(
                provider_name="openai",
                models={
                    "gpt-4o": {"cost_per_1k_tokens": 0.03, "max_tokens": 128000, "capabilities": ["reasoning", "code", "analysis"]},
                    "gpt-4o-mini": {"cost_per_1k_tokens": 0.0015, "max_tokens": 128000, "capabilities": ["fast", "cheap"]},
                    "o1": {"cost_per_1k_tokens": 0.15, "max_tokens": 200000, "capabilities": ["reasoning", "complex"]}
                },
                rate_limits=RateLimitConfig(requests_per_minute=500, requests_per_hour=10000),
                priority=3,
                capabilities=["text", "code", "reasoning", "structured_output"]
            ),
            "anthropic": ProviderConfig(
                provider_name="anthropic",
                models={
                    "claude-3-5-sonnet": {"cost_per_1k_tokens": 0.003, "max_tokens": 200000, "capabilities": ["reasoning", "code", "analysis"]},
                    "claude-3-haiku": {"cost_per_1k_tokens": 0.00025, "max_tokens": 200000, "capabilities": ["fast", "cheap"]}
                },
                rate_limits=RateLimitConfig(requests_per_minute=300, requests_per_hour=5000),
                priority=4,
                capabilities=["text", "code", "reasoning", "long_context"]
            ),
            "google": ProviderConfig(
                provider_name="google",
                models={
                    "gemini-2.0-flash-exp": {"cost_per_1k_tokens": 0.0005, "max_tokens": 1000000, "capabilities": ["multimodal", "fast", "cheap"]},
                    "gemini-pro": {"cost_per_1k_tokens": 0.001, "max_tokens": 2000000, "capabilities": ["multimodal", "reasoning"]}
                },
                rate_limits=RateLimitConfig(requests_per_minute=1000, requests_per_hour=20000),
                priority=2,
                capabilities=["text", "multimodal", "long_context", "cheap"]
            ),
            "perplexity": ProviderConfig(
                provider_name="perplexity",
                models={
                    "llama-3.1-sonar-small": {"cost_per_1k_tokens": 0.0002, "max_tokens": 131072, "capabilities": ["search", "web", "cheap"]},
                    "llama-3.1-sonar-large": {"cost_per_1k_tokens": 0.001, "max_tokens": 131072, "capabilities": ["search", "web", "reasoning"]}
                },
                rate_limits=RateLimitConfig(requests_per_minute=200, requests_per_hour=2000),
                priority=1,
                capabilities=["search", "web", "realtime"]
            )
        }
        
        for provider_name, config in providers.items():
            self.register_provider(config)
    
    def register_provider(self, config: ProviderConfig):
        """Register a new provider configuration"""
        self.providers[config.provider_name] = config
        self.provider_status[config.provider_name] = ProviderStatus.HEALTHY
        
        # Initialize rate limiters
        rate_limits = config.rate_limits
        self.rate_limiters[config.provider_name] = {
            "minute": TokenBucket(rate_limits.requests_per_minute, rate_limits.requests_per_minute / 60.0),
            "hour": TokenBucket(rate_limits.requests_per_hour, rate_limits.requests_per_hour / 3600.0),
            "day": TokenBucket(rate_limits.requests_per_day, rate_limits.requests_per_day / 86400.0)
        }
        
        logger.info(f"Registered provider {config.provider_name} with {len(config.models)} models")
    
    async def select_optimal_provider(
        self,
        agent_type: AgentType,
        required_capabilities: List[str] = None,
        max_cost: Optional[float] = None,
        user_id: Optional[str] = None,
        exclude_providers: List[str] = None
    ) -> Optional[Tuple[str, str]]:  # (provider, model)
        """Select the optimal provider and model based on multiple factors"""
        
        # Check budget constraints
        if not await self._check_budget_constraints(max_cost, user_id):
            logger.warning("Budget constraints exceeded")
            return None
        
        exclude_providers = exclude_providers or []
        required_capabilities = required_capabilities or []
        
        # Get available providers
        candidates = []
        
        for provider_name, config in self.providers.items():
            if (provider_name in exclude_providers or 
                self.provider_status[provider_name] == ProviderStatus.UNAVAILABLE):
                continue
            
            # Check if provider supports required capabilities
            if required_capabilities and not all(cap in config.capabilities for cap in required_capabilities):
                continue
            
            # Check rate limits
            if not await self._check_rate_limits(provider_name):
                continue
            
            # Evaluate each model
            for model_name, model_config in config.models.items():
                # Check model capabilities
                if required_capabilities and not all(cap in model_config.get("capabilities", []) for cap in required_capabilities):
                    continue
                
                # Check cost constraints
                estimated_cost = self._estimate_request_cost(provider_name, model_name)
                if max_cost and estimated_cost > max_cost:
                    continue
                
                score = await self._calculate_provider_score(provider_name, model_name, agent_type)
                candidates.append((score, provider_name, model_name, estimated_cost))
        
        if not candidates:
            logger.warning(f"No suitable providers found for agent type {agent_type.value}")
            return None
        
        # Sort by score (highest first)
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        # Select the best candidate
        _, provider, model, cost = candidates[0]
        
        logger.info(f"Selected {provider}:{model} for {agent_type.value} (score: {candidates[0][0]:.3f}, cost: ${cost:.4f})")
        return provider, model
    
    async def _calculate_provider_score(self, provider: str, model: str, agent_type: AgentType) -> float:
        """Calculate a comprehensive score for provider selection"""
        config = self.providers[provider]
        model_config = config.models[model]
        metrics = self.provider_metrics[provider]
        
        # Base score components
        scores = {}
        
        # 1. Cost efficiency (lower cost = higher score)
        cost = model_config.get("cost_per_1k_tokens", 0.01)
        scores["cost"] = max(0, 1.0 - (cost / 0.1))  # Normalize against $0.10/1k baseline
        
        # 2. Performance (success rate and response time)
        scores["performance"] = (metrics.success_rate * 0.7 + 
                               max(0, 1.0 - (metrics.avg_response_time / 10.0)) * 0.3)
        
        # 3. Provider priority (configured preference)
        scores["priority"] = config.priority / 5.0  # Normalize to 0-1
        
        # 4. Current load (prefer less loaded providers)
        recent_requests = len([t for t in self.request_history[provider] 
                              if time.time() - t < 300])  # Last 5 minutes
        load_factor = min(1.0, recent_requests / 50.0)  # 50 requests/5min baseline
        scores["load"] = 1.0 - load_factor
        
        # 5. Provider health status
        status_scores = {
            ProviderStatus.HEALTHY: 1.0,
            ProviderStatus.DEGRADED: 0.5,
            ProviderStatus.UNAVAILABLE: 0.0
        }
        scores["health"] = status_scores[self.provider_status[provider]]
        
        # 6. Model capabilities match
        model_caps = set(model_config.get("capabilities", []))
        agent_preferences = {
            AgentType.SEARCH: {"search", "web", "fast"},
            AgentType.WRITER: {"reasoning", "long_context", "structured_output"},
            AgentType.EVALUATOR: {"reasoning", "analysis", "structured_output"},
            AgentType.AGGREGATOR: {"fast", "cheap", "structured_output"},
            AgentType.SPECIALIST: {"reasoning", "complex", "analysis"}
        }
        
        preferred_caps = agent_preferences.get(agent_type, set())
        if preferred_caps:
            capability_match = len(model_caps.intersection(preferred_caps)) / len(preferred_caps)
            scores["capabilities"] = capability_match
        else:
            scores["capabilities"] = 0.5
        
        # Weighted combination
        weights = {
            "cost": 0.25,
            "performance": 0.25,
            "priority": 0.15,
            "load": 0.15,
            "health": 0.15,
            "capabilities": 0.05
        }
        
        total_score = sum(scores[key] * weights[key] for key in weights)
        
        logger.debug(f"Provider {provider}:{model} scores: {scores}, total: {total_score:.3f}")
        return total_score
    
    def _estimate_request_cost(self, provider: str, model: str, tokens: int = 1000) -> float:
        """Estimate the cost of a request"""
        config = self.providers[provider]
        model_config = config.models[model]
        
        cost_per_1k = model_config.get("cost_per_1k_tokens", 0.01)
        base_cost = (tokens / 1000.0) * cost_per_1k
        
        # Apply provider cost multiplier
        adjusted_cost = base_cost * config.cost_multiplier
        
        return adjusted_cost
    
    async def _check_budget_constraints(self, max_cost: Optional[float], user_id: Optional[str]) -> bool:
        """Check if request is within budget constraints"""
        # Check global daily budget
        current_daily = await self.redis.get("handywriterz:budget:daily") or "0"
        if float(current_daily) >= self.budget_config.daily_limit:
            return False
        
        # Check global hourly budget
        current_hour = datetime.utcnow().hour
        hourly_key = f"handywriterz:budget:hourly:{current_hour}"
        current_hourly = await self.redis.get(hourly_key) or "0"
        if float(current_hourly) >= self.budget_config.hourly_limit:
            return False
        
        # Check per-request limit
        if max_cost and max_cost > self.budget_config.per_request_limit:
            return False
        
        # Check user daily limit
        if user_id:
            user_key = f"handywriterz:budget:user:{user_id}:daily"
            user_daily = await self.redis.get(user_key) or "0"
            if float(user_daily) >= self.budget_config.user_daily_limit:
                return False
        
        return True
    
    async def _check_rate_limits(self, provider: str) -> bool:
        """Check if provider is within rate limits"""
        limiters = self.rate_limiters.get(provider, {})
        
        # Check all rate limits
        for limit_type, bucket in limiters.items():
            if not await bucket.consume(1):
                logger.debug(f"Rate limit exceeded for {provider} ({limit_type})")
                return False
        
        return True
    
    async def record_request(
        self,
        provider: str,
        model: str,
        cost: float,
        success: bool,
        response_time: float,
        user_id: Optional[str] = None
    ):
        """Record a completed request for metrics and billing"""
        
        # Update provider metrics
        metrics = self.provider_metrics[provider]
        metrics.total_requests += 1
        if not success:
            metrics.success_rate = (metrics.success_rate * (metrics.total_requests - 1)) / metrics.total_requests
        
        # Update average cost and response time
        alpha = 0.1  # Exponential moving average factor
        metrics.avg_cost_per_request = (alpha * cost + (1 - alpha) * metrics.avg_cost_per_request)
        metrics.avg_response_time = (alpha * response_time + (1 - alpha) * metrics.avg_response_time)
        metrics.last_request = datetime.utcnow()
        
        # Record request timestamp for load tracking
        self.request_history[provider].append(time.time())
        
        # Update budget tracking in Redis
        current_date = datetime.utcnow().date().isoformat()
        current_hour = datetime.utcnow().hour
        
        # Daily budget
        daily_key = f"handywriterz:budget:daily:{current_date}"
        await self.redis.incrbyfloat(daily_key, cost)
        await self.redis.expire(daily_key, 86400 * 2)  # Keep for 2 days
        
        # Hourly budget
        hourly_key = f"handywriterz:budget:hourly:{current_hour}"
        await self.redis.incrbyfloat(hourly_key, cost)
        await self.redis.expire(hourly_key, 3600 * 2)  # Keep for 2 hours
        
        # User budget
        if user_id:
            user_key = f"handywriterz:budget:user:{user_id}:daily:{current_date}"
            await self.redis.incrbyfloat(user_key, cost)
            await self.redis.expire(user_key, 86400 * 7)  # Keep for 7 days
        
        # Store detailed request log
        request_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "provider": provider,
            "model": model,
            "cost": cost,
            "success": success,
            "response_time": response_time,
            "user_id": user_id
        }
        
        await self.redis.lpush(
            "handywriterz:request_log",
            json.dumps(request_log)
        )
        await self.redis.ltrim("handywriterz:request_log", 0, 10000)  # Keep last 10k requests
        
        logger.debug(f"Recorded request: {provider}:{model}, cost: ${cost:.4f}, success: {success}")
    
    async def get_budget_status(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current budget status"""
        current_date = datetime.utcnow().date().isoformat()
        current_hour = datetime.utcnow().hour
        
        # Global budgets
        daily_spent = float(await self.redis.get(f"handywriterz:budget:daily:{current_date}") or "0")
        hourly_spent = float(await self.redis.get(f"handywriterz:budget:hourly:{current_hour}") or "0")
        
        status = {
            "global": {
                "daily": {
                    "spent": daily_spent,
                    "limit": self.budget_config.daily_limit,
                    "remaining": max(0, self.budget_config.daily_limit - daily_spent),
                    "utilization": daily_spent / self.budget_config.daily_limit
                },
                "hourly": {
                    "spent": hourly_spent,
                    "limit": self.budget_config.hourly_limit,
                    "remaining": max(0, self.budget_config.hourly_limit - hourly_spent),
                    "utilization": hourly_spent / self.budget_config.hourly_limit
                }
            }
        }
        
        # User budget
        if user_id:
            user_spent = float(await self.redis.get(f"handywriterz:budget:user:{user_id}:daily:{current_date}") or "0")
            status["user"] = {
                "daily": {
                    "spent": user_spent,
                    "limit": self.budget_config.user_daily_limit,
                    "remaining": max(0, self.budget_config.user_daily_limit - user_spent),
                    "utilization": user_spent / self.budget_config.user_daily_limit
                }
            }
        
        return status
    
    async def get_provider_metrics(self) -> Dict[str, Any]:
        """Get comprehensive provider performance metrics"""
        metrics = {}
        
        for provider_name, provider_metrics in self.provider_metrics.items():
            recent_requests = len([t for t in self.request_history[provider_name] 
                                 if time.time() - t < 3600])  # Last hour
            
            metrics[provider_name] = {
                "status": self.provider_status[provider_name].value,
                "total_requests": provider_metrics.total_requests,
                "success_rate": provider_metrics.success_rate,
                "avg_response_time": provider_metrics.avg_response_time,
                "avg_cost_per_request": provider_metrics.avg_cost_per_request,
                "last_request": provider_metrics.last_request.isoformat() if provider_metrics.last_request else None,
                "recent_requests_per_hour": recent_requests,
                "models": list(self.providers[provider_name].models.keys()) if provider_name in self.providers else []
            }
        
        return metrics
    
    async def health_check(self):
        """Perform health checks on all providers"""
        for provider_name, config in self.providers.items():
            try:
                # Simple health check based on recent success rate
                metrics = self.provider_metrics[provider_name]
                
                if metrics.total_requests > 10:  # Only check if we have enough data
                    if metrics.success_rate < 0.5:  # Less than 50% success rate
                        self.provider_status[provider_name] = ProviderStatus.UNAVAILABLE
                    elif metrics.success_rate < 0.8:  # Less than 80% success rate
                        self.provider_status[provider_name] = ProviderStatus.DEGRADED
                    else:
                        self.provider_status[provider_name] = ProviderStatus.HEALTHY
                
                logger.debug(f"Health check: {provider_name} = {self.provider_status[provider_name].value}")
                
            except Exception as e:
                logger.error(f"Health check failed for {provider_name}: {e}")
                self.provider_status[provider_name] = ProviderStatus.UNAVAILABLE