"""
Registry-Enhanced Routing Adapter

Integrates the model registry with the existing UnifiedProcessor to provide:
- Budget-aware model selection
- Intelligent fallback strategies  
- Provider health monitoring
- Cost optimization
- Deterministic routing with registry constraints
"""

import os
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Registry imports with graceful fallback
try:
    from src.services.model_registry import (
        ModelRegistry, ModelSpec, ModelCapability, BudgetConstraint,
        get_model_registry, initialize_model_registry
    )
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Model registry not available, using fallback routing")

# Existing routing imports
try:
    from .system_router import SystemRouter
    from .normalization import normalize_user_params
except ImportError:
    SystemRouter = None
    normalize_user_params = lambda x: x

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    COST_OPTIMIZED = "cost_optimized"
    QUALITY_OPTIMIZED = "quality_optimized" 
    BALANCED = "balanced"
    SPEED_OPTIMIZED = "speed_optimized"


@dataclass
class RoutingContext:
    """Enhanced routing context with registry information."""
    
    # Request context
    message: str
    files: List[Dict[str, Any]]
    user_params: Dict[str, Any]
    user_id: Optional[str]
    conversation_id: str
    
    # Budget context
    budget_tier: str = "default"
    max_cost: Optional[float] = None
    
    # Routing preferences
    strategy: RoutingStrategy = RoutingStrategy.BALANCED
    required_capabilities: List[ModelCapability] = None
    preferred_providers: List[str] = None
    fallback_enabled: bool = True
    
    # Estimation context
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    
    def __post_init__(self):
        if self.required_capabilities is None:
            self.required_capabilities = [ModelCapability.TEXT_GENERATION]
        if self.preferred_providers is None:
            self.preferred_providers = []


@dataclass 
class RoutingDecision:
    """Enhanced routing decision with registry information."""
    
    # Primary routing decision
    system: str  # simple, advanced, hybrid
    complexity: float
    reason: str
    confidence: float
    
    # Registry-enhanced information
    selected_model: Optional[ModelSpec] = None
    fallback_models: List[ModelSpec] = None
    estimated_cost: float = 0.0
    budget_status: str = "within_budget"
    provider_health: Dict[str, Any] = None
    
    # Alternative options
    alternative_routes: List[Dict[str, Any]] = None
    cost_breakdown: Dict[str, float] = None
    
    def __post_init__(self):
        if self.fallback_models is None:
            self.fallback_models = []
        if self.alternative_routes is None:
            self.alternative_routes = []
        if self.cost_breakdown is None:
            self.cost_breakdown = {}
        if self.provider_health is None:
            self.provider_health = {}


class RegistryEnhancedRouter:
    """
    Enhanced router that integrates model registry for intelligent routing decisions.
    
    Provides budget-aware, health-conscious routing with intelligent fallbacks.
    """
    
    def __init__(
        self, 
        redis_client,
        fallback_router: Optional[SystemRouter] = None,
        enable_registry: bool = None
    ):
        self.redis = redis_client
        self.fallback_router = fallback_router
        
        # Feature flags
        self.enable_registry = (
            enable_registry if enable_registry is not None 
            else os.getenv("FEATURE_MODEL_REGISTRY", "true").lower() == "true"
        )
        
        self.enable_cost_optimization = os.getenv("FEATURE_COST_OPTIMIZATION", "true").lower() == "true"
        self.enable_health_routing = os.getenv("FEATURE_HEALTH_ROUTING", "true").lower() == "true"
        self.enable_intelligent_fallback = os.getenv("FEATURE_INTELLIGENT_FALLBACK", "true").lower() == "true"
        
        # Initialize registry if available
        self.registry: Optional[ModelRegistry] = None
        if self.enable_registry and REGISTRY_AVAILABLE:
            try:
                self.registry = get_model_registry()
                if not self.registry:
                    self.registry = initialize_model_registry(redis_client)
                logger.info("Registry-enhanced router initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize model registry: {e}")
                self.registry = None
        
        # Routing strategy mappings
        self.strategy_mappings = {
            RoutingStrategy.COST_OPTIMIZED: {
                "system_preference": "simple",
                "quality_threshold": 0.6,
                "cost_weight": 0.7,
                "speed_weight": 0.2,
                "quality_weight": 0.1
            },
            RoutingStrategy.QUALITY_OPTIMIZED: {
                "system_preference": "advanced", 
                "quality_threshold": 0.9,
                "cost_weight": 0.1,
                "speed_weight": 0.2,
                "quality_weight": 0.7
            },
            RoutingStrategy.BALANCED: {
                "system_preference": "hybrid",
                "quality_threshold": 0.7,
                "cost_weight": 0.3,
                "speed_weight": 0.3,
                "quality_weight": 0.4
            },
            RoutingStrategy.SPEED_OPTIMIZED: {
                "system_preference": "simple",
                "quality_threshold": 0.5,
                "cost_weight": 0.2,
                "speed_weight": 0.6,
                "quality_weight": 0.2
            }
        }
    
    async def analyze_and_route(self, context: RoutingContext) -> RoutingDecision:
        """
        Enhanced routing analysis with registry integration.
        
        Provides intelligent routing based on:
        - Budget constraints and cost optimization
        - Provider health and availability  
        - Model capabilities and requirements
        - Performance preferences and fallback strategies
        """
        
        # Start with fallback routing if registry unavailable
        if not self.registry:
            return await self._fallback_routing(context)
        
        try:
            # Step 1: Estimate token usage for cost calculations
            input_tokens, output_tokens = await self._estimate_tokens(context)
            context.estimated_input_tokens = input_tokens
            context.estimated_output_tokens = output_tokens
            
            # Step 2: Determine routing strategy from user params
            strategy = self._determine_strategy(context)
            
            # Step 3: Select optimal model using registry
            model_selection_result = await self._select_optimal_model(context, strategy)
            
            if not model_selection_result["success"]:
                logger.warning(f"Model selection failed: {model_selection_result['reason']}")
                return await self._fallback_routing(context)
            
            selected_model = model_selection_result["model"]
            
            # Step 4: Determine system routing based on selected model and strategy
            system_choice = self._determine_system_from_model(selected_model, strategy)
            
            # Step 5: Calculate complexity and confidence
            complexity = self._calculate_complexity(context, selected_model)
            confidence = self._calculate_confidence(context, selected_model, system_choice)
            
            # Step 6: Get fallback chain if enabled
            fallback_models = []
            if context.fallback_enabled and self.enable_intelligent_fallback:
                fallback_models = await self.registry.get_fallback_chain(
                    selected_model.model_id,
                    context.required_capabilities,
                    context.budget_tier,
                    max_fallbacks=3
                )
                fallback_models = fallback_models[1:]  # Remove primary model
            
            # Step 7: Calculate costs and check budget
            estimated_cost = selected_model.calculate_cost(input_tokens, output_tokens)
            budget_status = await self._check_budget_status(context, estimated_cost)
            
            # Step 8: Get provider health information
            provider_health = {}
            if self.enable_health_routing:
                health = await self.registry.get_provider_health(selected_model.provider)
                if health:
                    provider_health = {
                        "status": health.status.value,
                        "success_rate": health.success_rate,
                        "response_time_ms": health.response_time_ms,
                        "is_healthy": health.is_healthy()
                    }
            
            # Step 9: Generate alternative routes for transparency
            alternatives = await self._generate_alternatives(context, selected_model)
            
            # Step 10: Create enhanced routing decision
            decision = RoutingDecision(
                system=system_choice,
                complexity=complexity,
                reason=self._generate_routing_reason(context, selected_model, system_choice, strategy),
                confidence=confidence,
                selected_model=selected_model,
                fallback_models=fallback_models,
                estimated_cost=estimated_cost,
                budget_status=budget_status,
                provider_health=provider_health,
                alternative_routes=alternatives,
                cost_breakdown={
                    "input_tokens": input_tokens * selected_model.cost_per_input_token,
                    "output_tokens": output_tokens * selected_model.cost_per_output_token,
                    "total": estimated_cost
                }
            )
            
            logger.info(f"Registry routing: {system_choice} via {selected_model.model_id} (${estimated_cost:.6f})")
            return decision
            
        except Exception as e:
            logger.error(f"Registry routing failed: {e}")
            return await self._fallback_routing(context)
    
    async def _estimate_tokens(self, context: RoutingContext) -> Tuple[int, int]:
        """Estimate input and output tokens for the request."""
        # Simple estimation - could be enhanced with actual tokenizer
        message_tokens = len(context.message.split()) * 1.3  # Rough approximation
        
        # Add file tokens if present
        file_tokens = 0
        for file in context.files:
            if file.get("type", "").startswith("text"):
                content = file.get("content", "")
                file_tokens += len(content.split()) * 1.3
            elif file.get("type", "").startswith("image"):
                file_tokens += 1000  # Approximate for vision models
        
        input_tokens = int(message_tokens + file_tokens)
        
        # Estimate output tokens based on document type and complexity
        doc_type = context.user_params.get("document_type", "essay")
        word_count = context.user_params.get("word_count", 1000)
        
        if word_count:
            output_tokens = int(word_count * 1.3)  # Words to tokens approximation
        else:
            # Default estimates by document type
            type_estimates = {
                "essay": 1500,
                "research_paper": 3000,
                "thesis": 8000,
                "dissertation": 15000,
                "technical_report": 2500,
                "case_study": 2000
            }
            output_tokens = type_estimates.get(doc_type, 1500)
        
        return input_tokens, output_tokens
    
    def _determine_strategy(self, context: RoutingContext) -> RoutingStrategy:
        """Determine routing strategy from user parameters and preferences."""
        # Check explicit strategy in user params
        strategy_param = context.user_params.get("routing_strategy", "").lower()
        if strategy_param:
            strategy_map = {
                "cost": RoutingStrategy.COST_OPTIMIZED,
                "quality": RoutingStrategy.QUALITY_OPTIMIZED,
                "speed": RoutingStrategy.SPEED_OPTIMIZED,
                "balanced": RoutingStrategy.BALANCED
            }
            if strategy_param in strategy_map:
                return strategy_map[strategy_param]
        
        # Infer from quality tier
        quality_tier = context.user_params.get("quality_tier", "standard").lower()
        if quality_tier in ["premium", "enterprise"]:
            return RoutingStrategy.QUALITY_OPTIMIZED
        elif quality_tier == "basic":
            return RoutingStrategy.COST_OPTIMIZED
        
        # Infer from document type complexity
        doc_type = context.user_params.get("document_type", "").lower()
        complex_types = ["dissertation", "thesis", "research_paper", "technical_report"]
        if any(t in doc_type for t in complex_types):
            return RoutingStrategy.QUALITY_OPTIMIZED
        
        # Default to balanced
        return context.strategy
    
    async def _select_optimal_model(self, context: RoutingContext, strategy: RoutingStrategy) -> Dict[str, Any]:
        """Select optimal model using registry with strategy preferences."""
        try:
            # Determine quality preference based on strategy
            strategy_config = self.strategy_mappings[strategy]
            quality_preference = "quality" if strategy == RoutingStrategy.QUALITY_OPTIMIZED else \
                               "cost" if strategy == RoutingStrategy.COST_OPTIMIZED else \
                               "balanced"
            
            # Select model using registry
            selected_model = await self.registry.select_model(
                required_capabilities=context.required_capabilities,
                budget_tier=context.budget_tier,
                quality_preference=quality_preference,
                estimated_tokens=(context.estimated_input_tokens, context.estimated_output_tokens),
                fallback_chain=context.fallback_enabled
            )
            
            if selected_model:
                return {
                    "success": True,
                    "model": selected_model,
                    "reason": f"Selected optimal model for {strategy.value} strategy"
                }
            else:
                return {
                    "success": False,
                    "reason": "No suitable model found in registry",
                    "model": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "reason": f"Model selection error: {str(e)}",
                "model": None
            }
    
    def _determine_system_from_model(self, model: ModelSpec, strategy: RoutingStrategy) -> str:
        """Determine system routing based on selected model and strategy."""
        strategy_config = self.strategy_mappings[strategy]
        
        # Check model capabilities for system requirements
        advanced_capabilities = {
            ModelCapability.REASONING, 
            ModelCapability.ANALYSIS,
            ModelCapability.CODE_GENERATION
        }
        
        has_advanced_caps = bool(model.capabilities & advanced_capabilities)
        is_premium_model = model.quality_tier == "premium"
        
        # Apply strategy preferences
        preferred_system = strategy_config["system_preference"]
        
        if preferred_system == "simple":
            return "simple"
        elif preferred_system == "advanced" and (has_advanced_caps or is_premium_model):
            return "advanced"
        elif preferred_system == "hybrid":
            return "hybrid"
        
        # Fallback logic
        if has_advanced_caps and is_premium_model:
            return "advanced"
        elif has_advanced_caps:
            return "hybrid"
        else:
            return "simple"
    
    def _calculate_complexity(self, context: RoutingContext, model: ModelSpec) -> float:
        """Calculate complexity score for the routing decision."""
        base_complexity = 0.3
        
        # Document type complexity
        doc_type = context.user_params.get("document_type", "").lower()
        type_complexity = {
            "essay": 0.2,
            "case_study": 0.4,
            "research_paper": 0.6,
            "technical_report": 0.7,
            "thesis": 0.8,
            "dissertation": 0.9
        }
        base_complexity += type_complexity.get(doc_type, 0.3)
        
        # File complexity
        if context.files:
            base_complexity += min(0.3, len(context.files) * 0.1)
        
        # Model capability complexity
        advanced_caps = len(model.capabilities & {
            ModelCapability.REASONING, ModelCapability.ANALYSIS, ModelCapability.CODE_GENERATION
        })
        base_complexity += advanced_caps * 0.1
        
        # Word count complexity
        word_count = context.user_params.get("word_count", 1000)
        if word_count > 5000:
            base_complexity += 0.2
        elif word_count > 2000:
            base_complexity += 0.1
        
        return min(1.0, base_complexity)
    
    def _calculate_confidence(self, context: RoutingContext, model: ModelSpec, system: str) -> float:
        """Calculate confidence score for the routing decision."""
        base_confidence = 0.7
        
        # Model reliability boost
        base_confidence += model.reliability_score * 0.2
        
        # Provider health boost
        if self.enable_health_routing:
            # This would check actual provider health
            base_confidence += 0.1  # Assume healthy for now
        
        # Capability match boost
        required_caps = set(context.required_capabilities)
        available_caps = model.capabilities
        match_ratio = len(required_caps & available_caps) / len(required_caps)
        base_confidence += match_ratio * 0.1
        
        # System alignment boost
        if system == "advanced" and model.quality_tier == "premium":
            base_confidence += 0.05
        elif system == "simple" and model.speed_tier == "fast":
            base_confidence += 0.05
        
        return min(1.0, base_confidence)
    
    async def _check_budget_status(self, context: RoutingContext, estimated_cost: float) -> str:
        """Check budget status for the estimated cost."""
        if not self.enable_cost_optimization:
            return "budget_disabled"
        
        try:
            usage_stats = await self.registry.get_usage_stats("hour")
            current_usage = usage_stats.get("current_usage", 0.0)
            budget_limit = usage_stats.get("budget_limit", 10.0)
            
            if current_usage + estimated_cost > budget_limit:
                return "over_budget"
            elif (current_usage + estimated_cost) / budget_limit > 0.8:
                return "near_budget"
            else:
                return "within_budget"
                
        except Exception as e:
            logger.warning(f"Budget check failed: {e}")
            return "budget_check_failed"
    
    async def _generate_alternatives(self, context: RoutingContext, selected_model: ModelSpec) -> List[Dict[str, Any]]:
        """Generate alternative routing options for transparency."""
        alternatives = []
        
        try:
            # Get models with same capabilities
            alternative_models = self.registry.list_models(
                capabilities=context.required_capabilities
            )
            
            # Remove selected model and limit to top 3 alternatives
            alternative_models = [m for m in alternative_models if m.model_id != selected_model.model_id]
            alternative_models = alternative_models[:3]
            
            for model in alternative_models:
                cost = model.calculate_cost(context.estimated_input_tokens, context.estimated_output_tokens)
                alternatives.append({
                    "model_id": model.model_id,
                    "provider": model.provider,
                    "estimated_cost": cost,
                    "quality_tier": model.quality_tier,
                    "speed_tier": model.speed_tier,
                    "system": self._determine_system_from_model(model, context.strategy)
                })
        
        except Exception as e:
            logger.warning(f"Failed to generate alternatives: {e}")
        
        return alternatives
    
    def _generate_routing_reason(
        self, 
        context: RoutingContext, 
        model: ModelSpec, 
        system: str,
        strategy: RoutingStrategy
    ) -> str:
        """Generate human-readable routing reason."""
        reasons = []
        
        # Strategy reason
        reasons.append(f"Using {strategy.value} strategy")
        
        # Model selection reason
        reasons.append(f"Selected {model.display_name} for {model.quality_tier} quality")
        
        # System routing reason
        system_reasons = {
            "simple": "routing to simple system for efficiency",
            "advanced": "routing to advanced system for comprehensive processing", 
            "hybrid": "routing to hybrid system for balanced approach"
        }
        reasons.append(system_reasons.get(system, "unknown system selection"))
        
        # Cost consideration
        estimated_cost = model.calculate_cost(context.estimated_input_tokens, context.estimated_output_tokens)
        if estimated_cost < 0.01:
            reasons.append("cost-effective option")
        elif estimated_cost > 0.10:
            reasons.append("premium processing justified by requirements")
        
        return "; ".join(reasons)
    
    async def _fallback_routing(self, context: RoutingContext) -> RoutingDecision:
        """Fallback to original routing logic when registry unavailable."""
        if self.fallback_router:
            try:
                # Use original SystemRouter logic
                original_result = await self.fallback_router.analyze_request(
                    context.message, 
                    context.files, 
                    context.user_params
                )
                
                return RoutingDecision(
                    system=original_result.get("system", "simple"),
                    complexity=original_result.get("complexity", 0.5),
                    reason=original_result.get("reason", "Fallback routing") + " (registry unavailable)",
                    confidence=original_result.get("confidence", 0.5),
                    budget_status="registry_unavailable"
                )
            except Exception as e:
                logger.error(f"Fallback routing failed: {e}")
        
        # Ultimate fallback - simple deterministic routing
        complexity = 0.3
        if context.files or len(context.message) > 1000:
            complexity = 0.7
            system = "advanced"
        else:
            system = "simple"
        
        return RoutingDecision(
            system=system,
            complexity=complexity,
            reason="Emergency fallback routing",
            confidence=0.3,
            budget_status="fallback_mode"
        )


# Convenience functions for integration
async def create_routing_context(
    message: str,
    files: List[Dict[str, Any]] = None,
    user_params: Dict[str, Any] = None,
    user_id: Optional[str] = None,
    conversation_id: str = None,
    **kwargs
) -> RoutingContext:
    """Create a routing context from request parameters."""
    files = files or []
    user_params = user_params or {}
    conversation_id = conversation_id or f"conv_{int(time.time())}"
    
    # Normalize parameters if available
    try:
        user_params = normalize_user_params(user_params)
    except Exception:
        pass
    
    # Infer capabilities from user parameters
    required_capabilities = [ModelCapability.TEXT_GENERATION]
    
    doc_type = user_params.get("document_type", "").lower()
    if "research" in doc_type or "technical" in doc_type:
        required_capabilities.append(ModelCapability.ANALYSIS)
    if "code" in doc_type or user_params.get("include_code", False):
        required_capabilities.append(ModelCapability.CODE_GENERATION)
    if files:
        for file in files:
            if file.get("type", "").startswith("image"):
                required_capabilities.append(ModelCapability.VISION)
    
    # Determine budget tier
    quality_tier = user_params.get("quality_tier", "standard").lower()
    budget_tier_map = {
        "basic": "default",
        "standard": "default", 
        "premium": "premium",
        "enterprise": "research"
    }
    budget_tier = budget_tier_map.get(quality_tier, "default")
    
    return RoutingContext(
        message=message,
        files=files,
        user_params=user_params,
        user_id=user_id,
        conversation_id=conversation_id,
        budget_tier=budget_tier,
        required_capabilities=required_capabilities,
        **kwargs
    )


def get_registry_router(redis_client, fallback_router=None) -> RegistryEnhancedRouter:
    """Get or create a registry-enhanced router instance."""
    return RegistryEnhancedRouter(
        redis_client=redis_client,
        fallback_router=fallback_router
    )