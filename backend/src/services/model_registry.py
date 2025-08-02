"""
Provider/Model Registry with Budget Integration and Fallback Strategy

This module provides comprehensive model and provider management with:
- Model capability validation
- Cost-aware routing and budget enforcement
- Intelligent fallback strategies
- Provider health monitoring
- Feature flag support for staged rollout
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import redis.asyncio as redis
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    MAINTENANCE = "maintenance"


class ModelCapability(Enum):
    TEXT_GENERATION = "text_generation"
    REASONING = "reasoning"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    EMBEDDING = "embedding"
    VISION = "vision"
    AUDIO = "audio"


class CostTier(Enum):
    FREE = "free"
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class ModelSpec:
    """Comprehensive model specification with capabilities and constraints."""
    
    # Identity
    model_id: str
    provider: str
    display_name: str
    
    # Capabilities
    capabilities: Set[ModelCapability]
    max_tokens: int
    context_window: int
    supports_streaming: bool = True
    supports_function_calling: bool = False
    supports_vision: bool = False
    supports_audio: bool = False
    
    # Performance characteristics
    speed_tier: str = "standard"  # fast, standard, slow
    quality_tier: str = "standard"  # basic, standard, premium
    reliability_score: float = 0.8
    
    # Cost information
    cost_per_input_token: float = 0.0
    cost_per_output_token: float = 0.0 
    cost_per_image: float = 0.0
    cost_per_audio_minute: float = 0.0
    cost_tier: CostTier = CostTier.STANDARD
    
    # Availability
    available_regions: List[str] = field(default_factory=lambda: ["global"])
    rate_limits: Dict[str, int] = field(default_factory=dict)  # requests per minute/hour
    
    # Integration metadata
    api_endpoint: Optional[str] = None
    auth_method: str = "bearer"
    required_env_vars: List[str] = field(default_factory=list)
    
    # Feature flags
    is_experimental: bool = False
    is_deprecated: bool = False
    sunset_date: Optional[str] = None
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, images: int = 0, audio_minutes: float = 0.0) -> float:
        """Calculate total cost for a request."""
        cost = (
            input_tokens * self.cost_per_input_token +
            output_tokens * self.cost_per_output_token +
            images * self.cost_per_image +
            audio_minutes * self.cost_per_audio_minute
        )
        return round(cost, 6)
    
    def supports_capability(self, capability: ModelCapability) -> bool:
        """Check if model supports a specific capability."""
        return capability in self.capabilities
    
    def is_available(self, region: str = "global") -> bool:
        """Check if model is available in a specific region."""
        return region in self.available_regions or "global" in self.available_regions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "model_id": self.model_id,
            "provider": self.provider,
            "display_name": self.display_name,
            "capabilities": [c.value for c in self.capabilities],
            "max_tokens": self.max_tokens,
            "context_window": self.context_window,
            "supports_streaming": self.supports_streaming,
            "supports_function_calling": self.supports_function_calling,
            "supports_vision": self.supports_vision,
            "supports_audio": self.supports_audio,
            "speed_tier": self.speed_tier,
            "quality_tier": self.quality_tier,
            "reliability_score": self.reliability_score,
            "cost_per_input_token": self.cost_per_input_token,
            "cost_per_output_token": self.cost_per_output_token,
            "cost_per_image": self.cost_per_image,
            "cost_per_audio_minute": self.cost_per_audio_minute,
            "cost_tier": self.cost_tier.value,
            "available_regions": self.available_regions,
            "rate_limits": self.rate_limits,
            "api_endpoint": self.api_endpoint,
            "auth_method": self.auth_method,
            "required_env_vars": self.required_env_vars,
            "is_experimental": self.is_experimental,
            "is_deprecated": self.is_deprecated,
            "sunset_date": self.sunset_date
        }


@dataclass
class ProviderHealth:
    """Provider health status and metrics."""
    
    provider: str
    status: ProviderStatus
    last_check: datetime
    response_time_ms: float
    error_rate: float
    success_rate: float
    active_models: List[str]
    recent_errors: List[Dict[str, Any]] = field(default_factory=list)
    downtime_periods: List[Dict[str, Any]] = field(default_factory=list)
    
    def is_healthy(self) -> bool:
        """Check if provider is healthy enough for routing."""
        return (
            self.status in [ProviderStatus.HEALTHY, ProviderStatus.DEGRADED] and
            self.success_rate >= 0.8 and
            self.error_rate <= 0.2
        )
    
    def should_fallback(self) -> bool:
        """Check if should trigger fallback due to health issues."""
        return (
            self.status == ProviderStatus.DOWN or
            self.success_rate < 0.5 or
            self.error_rate > 0.5
        )


@dataclass
class BudgetConstraint:
    """Budget constraint configuration."""
    
    max_cost_per_request: float
    max_cost_per_hour: float
    max_cost_per_day: float
    priority_boost_factor: float = 1.0
    emergency_budget_multiplier: float = 2.0
    
    def is_within_budget(self, cost: float, current_hourly: float, current_daily: float) -> bool:
        """Check if request is within budget constraints."""
        return (
            cost <= self.max_cost_per_request and
            current_hourly + cost <= self.max_cost_per_hour and
            current_daily + cost <= self.max_cost_per_day
        )


class ModelRegistry:
    """
    Comprehensive model registry with budget integration and intelligent fallback.
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.models: Dict[str, ModelSpec] = {}
        self.provider_health: Dict[str, ProviderHealth] = {}
        self.budget_constraints: Dict[str, BudgetConstraint] = {}
        
        # Feature flags
        self.feature_flags = {
            "budget_enforcement": os.getenv("FEATURE_BUDGET_ENFORCEMENT", "true").lower() == "true",
            "health_monitoring": os.getenv("FEATURE_HEALTH_MONITORING", "true").lower() == "true",
            "intelligent_fallback": os.getenv("FEATURE_INTELLIGENT_FALLBACK", "true").lower() == "true",
            "cost_optimization": os.getenv("FEATURE_COST_OPTIMIZATION", "true").lower() == "true",
        }
        
        # Load configurations
        self._load_model_specifications()
        self._load_budget_constraints()
        
        # Background monitoring
        self._monitoring_task: Optional[asyncio.Task] = None
        self._health_check_interval = 300  # 5 minutes
    
    async def start(self):
        """Start the registry and background monitoring."""
        if self.feature_flags["health_monitoring"]:
            self._monitoring_task = asyncio.create_task(self._health_monitor_loop())
        
        logger.info(f"Model registry started with {len(self.models)} models")
    
    async def stop(self):
        """Stop the registry and cleanup resources."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Model registry stopped")
    
    def _load_model_specifications(self):
        """Load model specifications from configuration."""
        # Load from environment or config file
        config_path = os.getenv("MODEL_REGISTRY_CONFIG", "config/models.json")
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    for model_data in config.get("models", []):
                        model = self._create_model_spec(model_data)
                        self.models[model.model_id] = model
                logger.info(f"Loaded {len(self.models)} models from {config_path}")
            except Exception as e:
                logger.error(f"Failed to load model config from {config_path}: {e}")
                self._load_default_models()
        else:
            self._load_default_models()
    
    def _load_default_models(self):
        """Load default model specifications."""
        default_models = [
            # Gemini models
            {
                "model_id": "gemini-2.0-flash-exp",
                "provider": "google",
                "display_name": "Gemini 2.0 Flash (Experimental)",
                "capabilities": ["text_generation", "reasoning", "code_generation", "vision"],
                "max_tokens": 8192,
                "context_window": 1000000,
                "cost_per_input_token": 0.000000075,
                "cost_per_output_token": 0.0000003,
                "speed_tier": "fast",
                "quality_tier": "premium",
                "is_experimental": True,
                "required_env_vars": ["GOOGLE_API_KEY"]
            },
            {
                "model_id": "gemini-1.5-pro",
                "provider": "google", 
                "display_name": "Gemini 1.5 Pro",
                "capabilities": ["text_generation", "reasoning", "analysis", "vision"],
                "max_tokens": 8192,
                "context_window": 2000000,
                "cost_per_input_token": 0.00000125,
                "cost_per_output_token": 0.000005,
                "speed_tier": "standard",
                "quality_tier": "premium",
                "required_env_vars": ["GOOGLE_API_KEY"]
            },
            
            # OpenAI models
            {
                "model_id": "gpt-4o-mini",
                "provider": "openai",
                "display_name": "GPT-4o mini",
                "capabilities": ["text_generation", "reasoning", "code_generation"],
                "max_tokens": 16384,
                "context_window": 128000,
                "cost_per_input_token": 0.00000015,
                "cost_per_output_token": 0.0000006,
                "speed_tier": "fast",
                "quality_tier": "standard",
                "required_env_vars": ["OPENAI_API_KEY"]
            },
            {
                "model_id": "o3-mini",
                "provider": "openai",
                "display_name": "o3-mini",
                "capabilities": ["reasoning", "analysis", "code_generation"],
                "max_tokens": 65536,
                "context_window": 128000,
                "cost_per_input_token": 0.0000006,
                "cost_per_output_token": 0.0000024,
                "speed_tier": "slow",
                "quality_tier": "premium",
                "required_env_vars": ["OPENAI_API_KEY"]
            },
            
            # Anthropic models
            {
                "model_id": "claude-3-5-sonnet-20241022",
                "provider": "anthropic",
                "display_name": "Claude 3.5 Sonnet",
                "capabilities": ["text_generation", "reasoning", "analysis", "code_generation"],
                "max_tokens": 8192,
                "context_window": 200000,
                "cost_per_input_token": 0.000003,
                "cost_per_output_token": 0.000015,
                "speed_tier": "standard",
                "quality_tier": "premium",
                "required_env_vars": ["ANTHROPIC_API_KEY"]
            },
            
            # Perplexity models
            {
                "model_id": "llama-3.1-sonar-large-128k-online",
                "provider": "perplexity",
                "display_name": "Perplexity Sonar Large",
                "capabilities": ["text_generation", "analysis", "summarization"],
                "max_tokens": 127072,
                "context_window": 127072,
                "cost_per_input_token": 0.000001,
                "cost_per_output_token": 0.000001,
                "speed_tier": "standard",
                "quality_tier": "standard",
                "required_env_vars": ["PERPLEXITY_API_KEY"]
            }
        ]
        
        for model_data in default_models:
            model = self._create_model_spec(model_data)
            self.models[model.model_id] = model
        
        logger.info(f"Loaded {len(default_models)} default models")
    
    def _create_model_spec(self, model_data: Dict[str, Any]) -> ModelSpec:
        """Create ModelSpec from configuration data."""
        capabilities = set()
        for cap_str in model_data.get("capabilities", []):
            try:
                capabilities.add(ModelCapability(cap_str))
            except ValueError:
                logger.warning(f"Unknown capability: {cap_str}")
        
        cost_tier = CostTier.STANDARD
        try:
            if "cost_tier" in model_data:
                cost_tier = CostTier(model_data["cost_tier"])
        except ValueError:
            pass
        
        return ModelSpec(
            model_id=model_data["model_id"],
            provider=model_data["provider"],
            display_name=model_data["display_name"],
            capabilities=capabilities,
            max_tokens=model_data.get("max_tokens", 4096),
            context_window=model_data.get("context_window", 8192),
            supports_streaming=model_data.get("supports_streaming", True),
            supports_function_calling=model_data.get("supports_function_calling", False),
            supports_vision=model_data.get("supports_vision", False),
            supports_audio=model_data.get("supports_audio", False),
            speed_tier=model_data.get("speed_tier", "standard"),
            quality_tier=model_data.get("quality_tier", "standard"),
            reliability_score=model_data.get("reliability_score", 0.8),
            cost_per_input_token=model_data.get("cost_per_input_token", 0.0),
            cost_per_output_token=model_data.get("cost_per_output_token", 0.0),
            cost_per_image=model_data.get("cost_per_image", 0.0),
            cost_per_audio_minute=model_data.get("cost_per_audio_minute", 0.0),
            cost_tier=cost_tier,
            available_regions=model_data.get("available_regions", ["global"]),
            rate_limits=model_data.get("rate_limits", {}),
            api_endpoint=model_data.get("api_endpoint"),
            auth_method=model_data.get("auth_method", "bearer"),
            required_env_vars=model_data.get("required_env_vars", []),
            is_experimental=model_data.get("is_experimental", False),
            is_deprecated=model_data.get("is_deprecated", False),
            sunset_date=model_data.get("sunset_date")
        )
    
    def _load_budget_constraints(self):
        """Load budget constraints from configuration."""
        default_constraints = {
            "default": BudgetConstraint(
                max_cost_per_request=float(os.getenv("MAX_COST_PER_REQUEST", "0.10")),
                max_cost_per_hour=float(os.getenv("MAX_COST_PER_HOUR", "10.0")),
                max_cost_per_day=float(os.getenv("MAX_COST_PER_DAY", "100.0"))
            ),
            "premium": BudgetConstraint(
                max_cost_per_request=1.0,
                max_cost_per_hour=50.0,
                max_cost_per_day=500.0,
                priority_boost_factor=2.0
            ),
            "research": BudgetConstraint(
                max_cost_per_request=5.0,
                max_cost_per_hour=100.0,
                max_cost_per_day=1000.0,
                priority_boost_factor=3.0
            )
        }
        
        self.budget_constraints = default_constraints
        logger.info(f"Loaded {len(self.budget_constraints)} budget constraint tiers")
    
    async def select_model(
        self, 
        required_capabilities: List[ModelCapability],
        budget_tier: str = "default",
        region: str = "global",
        quality_preference: str = "balanced",  # cost, balanced, quality
        estimated_tokens: Tuple[int, int] = (1000, 1000),  # (input, output)
        fallback_chain: bool = True
    ) -> Optional[ModelSpec]:
        """
        Intelligent model selection with budget awareness and fallback.
        
        Args:
            required_capabilities: List of required model capabilities
            budget_tier: Budget constraint tier to apply
            region: Target region for availability
            quality_preference: Optimization preference (cost/balanced/quality)
            estimated_tokens: Estimated (input_tokens, output_tokens) for cost calculation
            fallback_chain: Whether to use fallback chain if primary fails
            
        Returns:
            Selected ModelSpec or None if no suitable model found
        """
        
        # Get budget constraints
        budget = self.budget_constraints.get(budget_tier, self.budget_constraints["default"])
        
        # Filter models by capabilities and availability
        candidates = []
        for model in self.models.values():
            # Check capabilities
            if not all(model.supports_capability(cap) for cap in required_capabilities):
                continue
            
            # Check availability
            if not model.is_available(region):
                continue
            
            # Check if deprecated or experimental (unless explicitly allowed)
            if model.is_deprecated and not os.getenv("ALLOW_DEPRECATED_MODELS", "false").lower() == "true":
                continue
            
            # Check provider health
            if self.feature_flags["health_monitoring"]:
                provider_health = self.provider_health.get(model.provider)
                if provider_health and not provider_health.is_healthy():
                    if not fallback_chain:
                        continue
            
            candidates.append(model)
        
        if not candidates:
            logger.warning(f"No models found for capabilities: {[c.value for c in required_capabilities]}")
            return None
        
        # Apply budget filtering if enabled
        if self.feature_flags["budget_enforcement"]:
            candidates = await self._filter_by_budget(candidates, budget, estimated_tokens)
        
        if not candidates:
            logger.warning("No models within budget constraints")
            return None
        
        # Rank and select best model
        selected = self._rank_and_select(candidates, quality_preference, estimated_tokens)
        
        if selected:
            logger.info(f"Selected model: {selected.model_id} for capabilities: {[c.value for c in required_capabilities]}")
        
        return selected
    
    async def _filter_by_budget(
        self, 
        candidates: List[ModelSpec], 
        budget: BudgetConstraint,
        estimated_tokens: Tuple[int, int]
    ) -> List[ModelSpec]:
        """Filter models by budget constraints."""
        input_tokens, output_tokens = estimated_tokens
        
        # Get current usage
        current_hourly = await self._get_current_usage("hour")
        current_daily = await self._get_current_usage("day")
        
        affordable_models = []
        for model in candidates:
            estimated_cost = model.calculate_cost(input_tokens, output_tokens)
            
            if budget.is_within_budget(estimated_cost, current_hourly, current_daily):
                affordable_models.append(model)
        
        return affordable_models
    
    def _rank_and_select(
        self, 
        candidates: List[ModelSpec],
        quality_preference: str,
        estimated_tokens: Tuple[int, int]
    ) -> ModelSpec:
        """Rank candidates and select the best one."""
        input_tokens, output_tokens = estimated_tokens
        
        def calculate_score(model: ModelSpec) -> float:
            cost = model.calculate_cost(input_tokens, output_tokens)
            
            # Base scoring factors
            cost_score = 1.0 / (cost + 0.001)  # Lower cost = higher score
            quality_score = {"basic": 0.5, "standard": 0.7, "premium": 1.0}.get(model.quality_tier, 0.7)
            speed_score = {"slow": 0.5, "standard": 0.7, "fast": 1.0}.get(model.speed_tier, 0.7)
            reliability_score = model.reliability_score
            
            # Apply preference weighting
            if quality_preference == "cost":
                weights = {"cost": 0.5, "quality": 0.2, "speed": 0.2, "reliability": 0.1}
            elif quality_preference == "quality":
                weights = {"cost": 0.1, "quality": 0.5, "speed": 0.2, "reliability": 0.2}
            else:  # balanced
                weights = {"cost": 0.25, "quality": 0.25, "speed": 0.25, "reliability": 0.25}
            
            # Provider health bonus
            provider_health = self.provider_health.get(model.provider)
            health_bonus = 1.0
            if provider_health:
                health_bonus = provider_health.success_rate
            
            total_score = (
                cost_score * weights["cost"] +
                quality_score * weights["quality"] +
                speed_score * weights["speed"] +
                reliability_score * weights["reliability"]
            ) * health_bonus
            
            return total_score
        
        # Sort by score (highest first)
        candidates.sort(key=calculate_score, reverse=True)
        return candidates[0]
    
    async def get_fallback_chain(
        self, 
        primary_model_id: str,
        required_capabilities: List[ModelCapability],
        budget_tier: str = "default",
        max_fallbacks: int = 3
    ) -> List[ModelSpec]:
        """
        Get intelligent fallback chain for a primary model.
        
        Returns list of models in fallback order, including the primary model first.
        """
        primary_model = self.models.get(primary_model_id)
        if not primary_model:
            return []
        
        fallback_chain = [primary_model]
        
        if not self.feature_flags["intelligent_fallback"]:
            return fallback_chain
        
        # Find alternative models with similar capabilities
        alternatives = []
        for model_id, model in self.models.items():
            if model_id == primary_model_id:
                continue
            
            # Must support required capabilities
            if not all(model.supports_capability(cap) for cap in required_capabilities):
                continue
            
            # Prefer same provider for consistency
            provider_bonus = 1.0 if model.provider == primary_model.provider else 0.8
            
            # Calculate similarity score
            similarity = self._calculate_model_similarity(primary_model, model) * provider_bonus
            alternatives.append((model, similarity))
        
        # Sort by similarity and add to fallback chain
        alternatives.sort(key=lambda x: x[1], reverse=True)
        
        for model, _ in alternatives[:max_fallbacks]:
            fallback_chain.append(model)
        
        logger.info(f"Generated fallback chain for {primary_model_id}: {[m.model_id for m in fallback_chain]}")
        return fallback_chain
    
    def _calculate_model_similarity(self, model1: ModelSpec, model2: ModelSpec) -> float:
        """Calculate similarity score between two models."""
        # Capability overlap
        common_caps = len(model1.capabilities & model2.capabilities)
        total_caps = len(model1.capabilities | model2.capabilities)
        capability_similarity = common_caps / total_caps if total_caps > 0 else 0
        
        # Quality tier similarity
        quality_tiers = ["basic", "standard", "premium"]
        q1_idx = quality_tiers.index(model1.quality_tier) if model1.quality_tier in quality_tiers else 1
        q2_idx = quality_tiers.index(model2.quality_tier) if model2.quality_tier in quality_tiers else 1
        quality_similarity = 1.0 - abs(q1_idx - q2_idx) / len(quality_tiers)
        
        # Cost similarity (inverse of cost difference)
        cost1 = model1.cost_per_input_token + model1.cost_per_output_token
        cost2 = model2.cost_per_input_token + model2.cost_per_output_token
        cost_diff = abs(cost1 - cost2) / max(cost1, cost2, 0.000001)
        cost_similarity = 1.0 - min(cost_diff, 1.0)
        
        # Weighted average
        return (
            capability_similarity * 0.5 +
            quality_similarity * 0.3 +
            cost_similarity * 0.2
        )
    
    async def _get_current_usage(self, period: str) -> float:
        """Get current usage for budget calculations."""
        try:
            usage_key = f"handywriterz:cost_usage:{period}:{datetime.now().strftime('%Y%m%d' if period == 'day' else '%Y%m%d%H')}"
            usage_str = await self.redis.get(usage_key)
            return float(usage_str) if usage_str else 0.0
        except Exception as e:
            logger.error(f"Failed to get current usage: {e}")
            return 0.0
    
    async def record_usage(self, model_id: str, cost: float, tokens_used: Dict[str, int]):
        """Record model usage for budget tracking."""
        if not self.feature_flags["budget_enforcement"]:
            return
        
        try:
            now = datetime.now()
            
            # Update hourly and daily usage
            hour_key = f"handywriterz:cost_usage:hour:{now.strftime('%Y%m%d%H')}"
            day_key = f"handywriterz:cost_usage:day:{now.strftime('%Y%m%d')}"
            
            pipe = self.redis.pipeline()
            pipe.incrbyfloat(hour_key, cost)
            pipe.expire(hour_key, 3600)  # 1 hour
            pipe.incrbyfloat(day_key, cost)
            pipe.expire(day_key, 86400)  # 24 hours
            
            # Store usage details
            usage_record = {
                "timestamp": now.isoformat(),
                "model_id": model_id,
                "cost": cost,
                "tokens": tokens_used
            }
            
            usage_detail_key = f"handywriterz:usage_details:{now.strftime('%Y%m%d')}"
            pipe.lpush(usage_detail_key, json.dumps(usage_record))
            pipe.ltrim(usage_detail_key, 0, 1000)  # Keep last 1000 records
            pipe.expire(usage_detail_key, 86400)
            
            await pipe.execute()
            
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")
    
    async def _health_monitor_loop(self):
        """Background health monitoring loop."""
        while True:
            try:
                await self._check_provider_health()
                await asyncio.sleep(self._health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _check_provider_health(self):
        """Check health of all providers."""
        providers = set(model.provider for model in self.models.values())
        
        for provider in providers:
            try:
                health = await self._check_single_provider_health(provider)
                self.provider_health[provider] = health
                
                # Store in Redis for persistence
                health_key = f"handywriterz:provider_health:{provider}"
                health_data = {
                    "status": health.status.value,
                    "last_check": health.last_check.isoformat(),
                    "response_time_ms": health.response_time_ms,
                    "error_rate": health.error_rate,
                    "success_rate": health.success_rate
                }
                await self.redis.setex(health_key, 600, json.dumps(health_data))
                
            except Exception as e:
                logger.error(f"Failed to check health for provider {provider}: {e}")
    
    async def _check_single_provider_health(self, provider: str) -> ProviderHealth:
        """Check health of a single provider."""
        # This would integrate with actual provider health check APIs
        # For now, return mock health data
        
        # Get models for this provider
        provider_models = [m.model_id for m in self.models.values() if m.provider == provider]
        
        # Mock health check - in reality this would ping provider APIs
        import random
        
        success_rate = random.uniform(0.8, 1.0)
        error_rate = 1.0 - success_rate
        response_time = random.uniform(100, 1000)
        
        if success_rate >= 0.95:
            status = ProviderStatus.HEALTHY
        elif success_rate >= 0.8:
            status = ProviderStatus.DEGRADED
        else:
            status = ProviderStatus.DOWN
        
        return ProviderHealth(
            provider=provider,
            status=status,
            last_check=datetime.now(),
            response_time_ms=response_time,
            error_rate=error_rate,
            success_rate=success_rate,
            active_models=provider_models
        )
    
    # Public API methods
    
    def get_model(self, model_id: str) -> Optional[ModelSpec]:
        """Get model specification by ID."""
        return self.models.get(model_id)
    
    def list_models(
        self, 
        provider: Optional[str] = None,
        capabilities: Optional[List[ModelCapability]] = None,
        include_deprecated: bool = False
    ) -> List[ModelSpec]:
        """List models with optional filtering."""
        models = list(self.models.values())
        
        if provider:
            models = [m for m in models if m.provider == provider]
        
        if capabilities:
            models = [m for m in models if all(m.supports_capability(cap) for cap in capabilities)]
        
        if not include_deprecated:
            models = [m for m in models if not m.is_deprecated]
        
        return models
    
    def get_providers(self) -> List[str]:
        """Get list of all providers."""
        return list(set(model.provider for model in self.models.values()))
    
    async def get_provider_health(self, provider: str) -> Optional[ProviderHealth]:
        """Get health status for a provider."""
        return self.provider_health.get(provider)
    
    async def get_usage_stats(self, period: str = "day") -> Dict[str, Any]:
        """Get usage statistics for budget monitoring."""
        try:
            if period == "day":
                usage_key = f"handywriterz:cost_usage:day:{datetime.now().strftime('%Y%m%d')}"
            else:
                usage_key = f"handywriterz:cost_usage:hour:{datetime.now().strftime('%Y%m%d%H')}"
            
            current_usage = await self.redis.get(usage_key)
            current_usage = float(current_usage) if current_usage else 0.0
            
            # Get budget limits
            budget = self.budget_constraints.get("default")
            
            return {
                "period": period,
                "current_usage": current_usage,
                "budget_limit": budget.max_cost_per_day if period == "day" else budget.max_cost_per_hour,
                "usage_percentage": (current_usage / (budget.max_cost_per_day if period == "day" else budget.max_cost_per_hour)) * 100,
                "budget_remaining": (budget.max_cost_per_day if period == "day" else budget.max_cost_per_hour) - current_usage
            }
        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}")
            return {"error": str(e)}


# Global registry instance
_model_registry: Optional[ModelRegistry] = None

def get_model_registry() -> Optional[ModelRegistry]:
    """Get the global model registry instance."""
    return _model_registry

def initialize_model_registry(redis_client: redis.Redis) -> ModelRegistry:
    """Initialize the global model registry."""
    global _model_registry
    _model_registry = ModelRegistry(redis_client)
    return _model_registry