"""
Intelligent Model Selector with capability matching, cost optimization, and performance tracking.
Integrates with existing HandyWriterz routing and budget systems.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta

import redis.asyncio as redis
from ..config.settings import get_settings
from ..services.budget import BudgetGuard, CostLevel
from .model_policy import ModelPolicyRegistry, get_model_policy_registry, NodeCapabilityRequirement
from .gateway import ModelSpec, LLMRequest, UnifiedLLMGateway, get_llm_gateway


logger = logging.getLogger(__name__)


class SelectionStrategy(str, Enum):
    """Model selection strategies"""
    COST_OPTIMIZED = "cost_optimized"        # Choose cheapest viable model
    PERFORMANCE_OPTIMIZED = "performance_optimized"  # Choose best performing model
    BALANCED = "balanced"                     # Balance cost and performance
    ADMIN_PREFERRED = "admin_preferred"      # Prefer admin-configured models
    CAPABILITY_STRICT = "capability_strict"  # Strict capability matching only


class SelectionTier(str, Enum):
    """Selection tiers for progressive fallback"""
    PREMIUM = "premium"      # Best models regardless of cost
    STANDARD = "standard"    # Good models with reasonable cost
    ECONOMY = "economy"      # Cheapest viable models
    EMERGENCY = "emergency"  # Last resort fallbacks


@dataclass
class ModelPerformanceMetrics:
    """Performance metrics for model selection"""
    success_rate: float = 0.0
    avg_latency_ms: float = 0.0
    avg_cost_per_token: float = 0.0
    total_requests: int = 0
    recent_failures: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    
    def calculate_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        if self.total_requests == 0:
            return 50.0  # Neutral score for untested models
        
        # Success rate component (0-40 points)
        success_score = self.success_rate * 40
        
        # Latency component (0-30 points, lower latency = higher score)
        if self.avg_latency_ms > 0:
            latency_score = max(0, 30 - (self.avg_latency_ms / 1000) * 10)
        else:
            latency_score = 15  # Neutral
        
        # Recent reliability (0-30 points)
        reliability_score = max(0, 30 - (self.recent_failures * 5))
        
        return min(100.0, success_score + latency_score + reliability_score)


@dataclass
class SelectionContext:
    """Context for model selection decisions"""
    node_name: str
    capabilities: List[str]
    user_id: Optional[str] = None
    cost_tier_override: Optional[CostLevel] = None
    strategy: SelectionStrategy = SelectionStrategy.BALANCED
    tier: SelectionTier = SelectionTier.STANDARD
    budget_remaining: Optional[float] = None
    previous_failures: List[str] = field(default_factory=list)
    trace_id: Optional[str] = None


@dataclass
class SelectionResult:
    """Result of model selection with reasoning"""
    selected_model: ModelSpec
    reasoning: str
    alternatives: List[ModelSpec] = field(default_factory=list)
    estimated_cost: float = 0.0
    confidence_score: float = 0.0
    fallback_chain: List[str] = field(default_factory=list)


class ModelSelector:
    """Intelligent model selector with performance tracking and cost optimization"""
    
    def __init__(self):
        self.settings = get_settings()
        self.policy_registry = get_model_policy_registry()
        self.llm_gateway = get_llm_gateway()
        self.budget_guard = BudgetGuard()
        
        # Performance tracking
        self.redis_client = None
        self._initialize_redis()
        self.performance_metrics: Dict[str, ModelPerformanceMetrics] = {}
        
        # Configuration
        self.metrics_ttl = 7 * 24 * 3600  # 7 days
        self.performance_window = timedelta(hours=24)
        
    def _initialize_redis(self):
        """Initialize Redis for performance metrics"""
        try:
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis not available for performance tracking: {e}")
            self.redis_client = None
    
    async def select_model(self, context: SelectionContext) -> SelectionResult:
        """Select optimal model based on context and strategy"""
        
        logger.info(f"Selecting model for {context.node_name} with strategy {context.strategy}")
        
        try:
            # Load performance metrics
            await self._load_performance_metrics()
            
            # Get base policy from registry
            base_policy = await self.policy_registry.get_policy_for_node(
                context.node_name,
                context.capabilities,
                context.cost_tier_override
            )
            
            # Apply selection strategy
            if context.strategy == SelectionStrategy.COST_OPTIMIZED:
                result = await self._select_cost_optimized(context, base_policy)
            elif context.strategy == SelectionStrategy.PERFORMANCE_OPTIMIZED:
                result = await self._select_performance_optimized(context, base_policy)
            elif context.strategy == SelectionStrategy.CAPABILITY_STRICT:
                result = await self._select_capability_strict(context, base_policy)
            elif context.strategy == SelectionStrategy.ADMIN_PREFERRED:
                result = await self._select_admin_preferred(context, base_policy)
            else:  # BALANCED (default)
                result = await self._select_balanced(context, base_policy)
            
            # Validate budget constraints
            if context.budget_remaining is not None:
                if result.estimated_cost > context.budget_remaining:
                    logger.warning(f"Selected model exceeds budget, trying cheaper alternatives")
                    result = await self._select_budget_constrained(context, result)
            
            logger.info(f"Selected {result.selected_model.logical_id}: {result.reasoning}")
            return result
            
        except Exception as e:
            logger.error(f"Model selection failed: {e}")
            # Return emergency fallback
            return await self._emergency_fallback(context)
    
    async def _select_cost_optimized(self, context: SelectionContext, base_policy: ModelSpec) -> SelectionResult:
        """Select cheapest viable model"""
        
        # Get all viable models
        viable_models = await self._get_viable_models(context)
        
        if not viable_models:
            return SelectionResult(
                selected_model=base_policy,
                reasoning="No alternative models found, using base policy",
                confidence_score=0.5
            )
        
        # Sort by cost (cheapest first)
        viable_models.sort(key=lambda m: (
            m.cost_tier.value,
            m.input_cost_per_1k + m.output_cost_per_1k
        ))
        
        # Filter out models that failed recently
        viable_models = [m for m in viable_models if m.logical_id not in context.previous_failures]
        
        selected = viable_models[0] if viable_models else base_policy
        
        return SelectionResult(
            selected_model=selected,
            reasoning=f"Cost-optimized selection: {selected.cost_tier.value} tier",
            alternatives=viable_models[1:5],  # Top 4 alternatives
            estimated_cost=self._estimate_cost(selected, context),
            confidence_score=0.8,
            fallback_chain=[m.logical_id for m in viable_models[1:3]]
        )
    
    async def _select_performance_optimized(self, context: SelectionContext, base_policy: ModelSpec) -> SelectionResult:
        """Select best performing model regardless of cost"""
        
        viable_models = await self._get_viable_models(context)
        
        if not viable_models:
            return SelectionResult(
                selected_model=base_policy,
                reasoning="No alternative models found, using base policy",
                confidence_score=0.5
            )
        
        # Score models by performance
        scored_models = []
        for model in viable_models:
            if model.logical_id in context.previous_failures:
                continue
                
            metrics = self.performance_metrics.get(model.logical_id, ModelPerformanceMetrics())
            score = metrics.calculate_score()
            
            # Boost score for premium models
            if model.cost_tier == CostLevel.PREMIUM:
                score += 10
            elif model.cost_tier == CostLevel.HIGH:
                score += 5
            
            scored_models.append((score, model))
        
        if not scored_models:
            scored_models = [(50.0, base_policy)]
        
        # Sort by score (highest first)
        scored_models.sort(key=lambda x: x[0], reverse=True)
        selected = scored_models[0][1]
        
        return SelectionResult(
            selected_model=selected,
            reasoning=f"Performance-optimized: score {scored_models[0][0]:.1f}",
            alternatives=[m for _, m in scored_models[1:5]],
            estimated_cost=self._estimate_cost(selected, context),
            confidence_score=min(1.0, scored_models[0][0] / 100),
            fallback_chain=[m.logical_id for _, m in scored_models[1:3]]
        )
    
    async def _select_balanced(self, context: SelectionContext, base_policy: ModelSpec) -> SelectionResult:
        """Balance cost and performance"""
        
        viable_models = await self._get_viable_models(context)
        
        if not viable_models:
            return SelectionResult(
                selected_model=base_policy,
                reasoning="No alternative models found, using base policy",
                confidence_score=0.5
            )
        
        # Calculate balanced scores
        scored_models = []
        for model in viable_models:
            if model.logical_id in context.previous_failures:
                continue
            
            metrics = self.performance_metrics.get(model.logical_id, ModelPerformanceMetrics())
            performance_score = metrics.calculate_score()
            
            # Cost efficiency score (lower cost = higher score)
            cost_score = {
                CostLevel.LOW: 100,
                CostLevel.MEDIUM: 75,
                CostLevel.HIGH: 50,
                CostLevel.PREMIUM: 25
            }.get(model.cost_tier, 50)
            
            # Weighted balanced score (60% performance, 40% cost)
            balanced_score = (performance_score * 0.6) + (cost_score * 0.4)
            
            scored_models.append((balanced_score, model))
        
        if not scored_models:
            scored_models = [(50.0, base_policy)]
        
        scored_models.sort(key=lambda x: x[0], reverse=True)
        selected = scored_models[0][1]
        
        return SelectionResult(
            selected_model=selected,
            reasoning=f"Balanced selection: {scored_models[0][0]:.1f} score (perf+cost)",
            alternatives=[m for _, m in scored_models[1:5]],
            estimated_cost=self._estimate_cost(selected, context),
            confidence_score=min(1.0, scored_models[0][0] / 100),
            fallback_chain=[m.logical_id for _, m in scored_models[1:3]]
        )
    
    async def _select_capability_strict(self, context: SelectionContext, base_policy: ModelSpec) -> SelectionResult:
        """Strict capability matching only"""
        
        # Only consider models that exactly match ALL required capabilities
        required_caps = set(context.capabilities)
        
        matching_models = []
        for model_id, model in self.policy_registry.policies.items():
            if model.logical_id in context.previous_failures:
                continue
                
            model_caps = set(attr for attr, enabled in model.capabilities.__dict__.items() if enabled)
            
            if required_caps.issubset(model_caps):
                matching_models.append(model)
        
        if not matching_models:
            return SelectionResult(
                selected_model=base_policy,
                reasoning="No models with exact capability match, using base policy",
                confidence_score=0.3
            )
        
        # Select cheapest among exact matches
        matching_models.sort(key=lambda m: m.cost_tier.value)
        selected = matching_models[0]
        
        return SelectionResult(
            selected_model=selected,
            reasoning=f"Strict capability match: {len(required_caps)} capabilities",
            alternatives=matching_models[1:3],
            estimated_cost=self._estimate_cost(selected, context),
            confidence_score=0.9,
            fallback_chain=[m.logical_id for m in matching_models[1:2]]
        )
    
    async def _select_admin_preferred(self, context: SelectionContext, base_policy: ModelSpec) -> SelectionResult:
        """Use admin-configured preferences"""
        
        # Admin overrides are already handled in policy registry
        # This strategy respects those overrides with high confidence
        
        return SelectionResult(
            selected_model=base_policy,
            reasoning="Admin-configured model selection",
            estimated_cost=self._estimate_cost(base_policy, context),
            confidence_score=1.0,
            fallback_chain=base_policy.fallback_models[:2]
        )
    
    async def _select_budget_constrained(self, context: SelectionContext, original_result: SelectionResult) -> SelectionResult:
        """Select model within budget constraints"""
        
        viable_models = await self._get_viable_models(context)
        
        # Filter by budget
        affordable_models = []
        for model in viable_models:
            estimated_cost = self._estimate_cost(model, context)
            if estimated_cost <= context.budget_remaining:
                affordable_models.append((estimated_cost, model))
        
        if not affordable_models:
            # Emergency: use cheapest model regardless
            cheapest = min(viable_models, key=lambda m: m.cost_tier.value)
            return SelectionResult(
                selected_model=cheapest,
                reasoning="Emergency budget selection: cheapest available",
                estimated_cost=self._estimate_cost(cheapest, context),
                confidence_score=0.2
            )
        
        # Sort by cost and select cheapest
        affordable_models.sort(key=lambda x: x[0])
        selected = affordable_models[0][1]
        
        return SelectionResult(
            selected_model=selected,
            reasoning=f"Budget-constrained: ${affordable_models[0][0]:.4f} < ${context.budget_remaining:.4f}",
            alternatives=[m for _, m in affordable_models[1:3]],
            estimated_cost=affordable_models[0][0],
            confidence_score=0.7
        )
    
    async def _get_viable_models(self, context: SelectionContext) -> List[ModelSpec]:
        """Get all viable models for the given context"""
        
        required_caps = set(context.capabilities) if context.capabilities else set()
        node_req = self.policy_registry.node_requirements.get(context.node_name)
        
        if node_req:
            required_caps.update(node_req.required_capabilities)
        
        viable_models = []
        
        for model_id, model in self.policy_registry.policies.items():
            # Check capability match
            model_caps = set(attr for attr, enabled in model.capabilities.__dict__.items() if enabled)
            
            if not required_caps.issubset(model_caps):
                continue
            
            # Check cost tier constraints
            if node_req and model.cost_tier.value > node_req.max_cost_tier.value:
                continue
            
            # Check context window
            if node_req and model.context_window < node_req.min_context_window:
                continue
            
            # Check reasoning requirement
            if node_req and node_req.reasoning_required and not model.capabilities.reasoning:
                continue
            
            viable_models.append(model)
        
        return viable_models
    
    def _estimate_cost(self, model: ModelSpec, context: SelectionContext) -> float:
        """Estimate cost for model based on context"""
        # Simple estimation - in production, use more sophisticated prediction
        base_tokens = 1000  # Rough estimate
        
        if context.capabilities:
            if "long_context" in context.capabilities:
                base_tokens *= 2
            if "reasoning" in context.capabilities:
                base_tokens *= 1.5
        
        input_cost = (base_tokens * model.input_cost_per_1k) / 1000
        output_cost = (base_tokens * 0.5 * model.output_cost_per_1k) / 1000  # Assume 50% output ratio
        
        return input_cost + output_cost
    
    async def _emergency_fallback(self, context: SelectionContext) -> SelectionResult:
        """Emergency fallback when all else fails"""
        
        # Try to find any model with basic capabilities
        for model_id, model in self.policy_registry.policies.items():
            if model.logical_id not in context.previous_failures:
                return SelectionResult(
                    selected_model=model,
                    reasoning="Emergency fallback: first available model",
                    confidence_score=0.1
                )
        
        # Absolute last resort: use any model
        if self.policy_registry.policies:
            fallback_model = list(self.policy_registry.policies.values())[0]
            return SelectionResult(
                selected_model=fallback_model,
                reasoning="Critical fallback: using any available model",
                confidence_score=0.05
            )
        
        raise Exception("No models available - system configuration error")
    
    async def _load_performance_metrics(self):
        """Load performance metrics from Redis"""
        if not self.redis_client:
            return
        
        try:
            # Load metrics for all models
            for model_id in self.policy_registry.policies.keys():
                metrics_key = f"model_metrics:{model_id}"
                metrics_data = await self.redis_client.hgetall(metrics_key)
                
                if metrics_data:
                    self.performance_metrics[model_id] = ModelPerformanceMetrics(
                        success_rate=float(metrics_data.get("success_rate", 0)),
                        avg_latency_ms=float(metrics_data.get("avg_latency_ms", 0)),
                        avg_cost_per_token=float(metrics_data.get("avg_cost_per_token", 0)),
                        total_requests=int(metrics_data.get("total_requests", 0)),
                        recent_failures=int(metrics_data.get("recent_failures", 0)),
                        last_success=datetime.fromisoformat(metrics_data["last_success"]) if metrics_data.get("last_success") else None,
                        last_failure=datetime.fromisoformat(metrics_data["last_failure"]) if metrics_data.get("last_failure") else None
                    )
        except Exception as e:
            logger.warning(f"Failed to load performance metrics: {e}")
    
    async def record_model_performance(
        self, 
        model_id: str, 
        success: bool, 
        latency_ms: int, 
        cost_usd: float, 
        tokens_used: int
    ):
        """Record model performance metrics"""
        
        if not self.redis_client:
            return
        
        try:
            metrics_key = f"model_metrics:{model_id}"
            
            # Get current metrics
            current = await self.redis_client.hgetall(metrics_key)
            
            # Calculate updated metrics
            total_requests = int(current.get("total_requests", 0)) + 1
            
            if success:
                success_count = int(current.get("success_count", 0)) + 1
                success_rate = success_count / total_requests
                
                # Update latency (running average)
                current_avg_latency = float(current.get("avg_latency_ms", 0))
                new_avg_latency = ((current_avg_latency * (total_requests - 1)) + latency_ms) / total_requests
                
                # Update cost per token
                current_avg_cost = float(current.get("avg_cost_per_token", 0))
                cost_per_token = cost_usd / tokens_used if tokens_used > 0 else 0
                new_avg_cost = ((current_avg_cost * (total_requests - 1)) + cost_per_token) / total_requests
                
                # Reset recent failures on success
                recent_failures = 0
                last_success = datetime.now().isoformat()
                last_failure = current.get("last_failure")
                
            else:
                success_count = int(current.get("success_count", 0))
                success_rate = success_count / total_requests
                new_avg_latency = float(current.get("avg_latency_ms", 0))
                new_avg_cost = float(current.get("avg_cost_per_token", 0))
                recent_failures = min(10, int(current.get("recent_failures", 0)) + 1)
                last_success = current.get("last_success")
                last_failure = datetime.now().isoformat()
            
            # Update Redis
            await self.redis_client.hmset(metrics_key, {
                "success_rate": success_rate,
                "success_count": success_count,
                "avg_latency_ms": new_avg_latency,
                "avg_cost_per_token": new_avg_cost,
                "total_requests": total_requests,
                "recent_failures": recent_failures,
                "last_success": last_success or "",
                "last_failure": last_failure or ""
            })
            
            # Set expiration
            await self.redis_client.expire(metrics_key, self.metrics_ttl)
            
        except Exception as e:
            logger.error(f"Failed to record performance metrics: {e}")
    
    async def get_model_recommendations(self, node_name: str) -> Dict[str, Any]:
        """Get model recommendations for a node"""
        
        await self._load_performance_metrics()
        
        context = SelectionContext(
            node_name=node_name,
            capabilities=[],
            strategy=SelectionStrategy.BALANCED
        )
        
        # Get recommendations for different strategies
        recommendations = {}
        
        for strategy in SelectionStrategy:
            try:
                context.strategy = strategy
                result = await self.select_model(context)
                recommendations[strategy.value] = {
                    "model": result.selected_model.logical_id,
                    "reasoning": result.reasoning,
                    "confidence": result.confidence_score,
                    "estimated_cost": result.estimated_cost
                }
            except Exception as e:
                recommendations[strategy.value] = {"error": str(e)}
        
        return {
            "node_name": node_name,
            "recommendations": recommendations,
            "performance_data": {
                model_id: {
                    "score": metrics.calculate_score(),
                    "success_rate": metrics.success_rate,
                    "avg_latency_ms": metrics.avg_latency_ms,
                    "total_requests": metrics.total_requests
                }
                for model_id, metrics in self.performance_metrics.items()
            }
        }
    
    async def optimize_fleet_costs(self) -> Dict[str, Any]:
        """Analyze and recommend cost optimizations across all nodes"""
        
        await self._load_performance_metrics()
        
        current_assignments = await self.policy_registry.get_current_assignments()
        recommendations = {}
        total_savings = 0.0
        
        for node_name in current_assignments.keys():
            try:
                # Get current model cost
                current_model_id = current_assignments[node_name]
                if current_model_id.startswith("ERROR"):
                    continue
                
                current_model = self.policy_registry.policies.get(current_model_id)
                if not current_model:
                    continue
                
                current_cost = self._estimate_cost(current_model, SelectionContext(node_name=node_name, capabilities=[]))
                
                # Get cost-optimized recommendation
                context = SelectionContext(
                    node_name=node_name,
                    capabilities=[],
                    strategy=SelectionStrategy.COST_OPTIMIZED
                )
                
                optimized = await self.select_model(context)
                optimized_cost = self._estimate_cost(optimized.selected_model, context)
                
                savings = current_cost - optimized_cost
                
                if savings > 0.001:  # Meaningful savings
                    recommendations[node_name] = {
                        "current_model": current_model_id,
                        "recommended_model": optimized.selected_model.logical_id,
                        "current_cost": current_cost,
                        "optimized_cost": optimized_cost,
                        "savings": savings,
                        "confidence": optimized.confidence_score
                    }
                    total_savings += savings
                    
            except Exception as e:
                logger.error(f"Cost optimization failed for {node_name}: {e}")
        
        return {
            "total_nodes_analyzed": len(current_assignments),
            "optimization_opportunities": len(recommendations),
            "estimated_savings_per_request": total_savings,
            "recommendations": recommendations
        }


# Global selector instance
_selector_instance = None

def get_model_selector() -> ModelSelector:
    """Get global model selector instance"""
    global _selector_instance
    if _selector_instance is None:
        _selector_instance = ModelSelector()
    return _selector_instance