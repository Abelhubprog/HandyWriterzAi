"""
Production-ready LLM service with comprehensive error handling, load balancing,
cost tracking, and advanced routing capabilities.
"""

import os
import json
import time
import asyncio
import hashlib
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

import redis.asyncio as redis
from langchain_core.messages import BaseMessage
from langchain_core.language_models import BaseLanguageModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq

from src.config.model_config import get_model_config
from src.services.error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    PERPLEXITY = "perplexity"

class ModelTier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class RequestPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ModelConfig:
    """Configuration for an LLM model"""
    name: str
    provider: ModelProvider
    tier: ModelTier
    max_tokens: int
    cost_per_input_token: float
    cost_per_output_token: float
    rate_limit_per_minute: int
    context_window: int
    supports_streaming: bool = True
    supports_function_calling: bool = False
    temperature_range: tuple = (0.0, 2.0)
    fallback_models: List[str] = None

@dataclass
class LLMRequest:
    """Standardized LLM request format"""
    messages: List[BaseMessage]
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    user_id: Optional[str] = None
    priority: RequestPriority = RequestPriority.NORMAL
    timeout: float = 30.0
    retries: int = 3
    metadata: Dict[str, Any] = None

@dataclass
class LLMResponse:
    """Standardized LLM response format"""
    content: str
    model: str
    provider: str
    tokens_used: int
    input_tokens: int
    output_tokens: int
    cost: float
    response_time: float
    cached: bool = False
    request_id: str = None
    metadata: Dict[str, Any] = None

@dataclass
class ModelMetrics:
    """Metrics for model performance tracking"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    average_response_time: float = 0.0
    error_rate: float = 0.0
    rate_limit_hits: int = 0
    last_updated: datetime = None

class LoadBalancer:
    """Intelligent load balancer for LLM requests"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.request_queues: Dict[str, asyncio.Queue] = {}
        self.model_metrics: Dict[str, ModelMetrics] = {}
        
    async def select_model(
        self, 
        requested_model: str, 
        task_type: str, 
        user_tier: ModelTier,
        priority: RequestPriority = RequestPriority.NORMAL
    ) -> str:
        """Select optimal model based on load, performance, and user tier"""
        
        # Get available models for the task
        available_models = self._get_available_models(task_type, user_tier)
        
        if requested_model in available_models:
            # Check if requested model is available
            if await self._is_model_available(requested_model):
                return requested_model
        
        # Find best alternative
        best_model = await self._find_best_model(available_models, priority)
        
        if best_model != requested_model:
            logger.info(f"Routing from {requested_model} to {best_model} due to load balancing")
            
        return best_model
    
    async def _is_model_available(self, model: str) -> bool:
        """Check if model is available and not rate limited"""
        rate_limit_key = f"rate_limit:{model}"
        current_requests = await self.redis.get(rate_limit_key)
        
        if current_requests is None:
            return True
            
        model_config = PRODUCTION_MODEL_CONFIGS.get(model)
        if not model_config:
            return False
            
        return int(current_requests) < model_config.rate_limit_per_minute
    
    async def _find_best_model(self, available_models: List[str], priority: RequestPriority) -> str:
        """Find the best available model based on current load and performance"""
        best_model = None
        best_score = -1
        
        for model in available_models:
            if not await self._is_model_available(model):
                continue
                
            score = await self._calculate_model_score(model, priority)
            
            if score > best_score:
                best_score = score
                best_model = model
        
        return best_model or available_models[0]  # Fallback to first available
    
    async def _calculate_model_score(self, model: str, priority: RequestPriority) -> float:
        """Calculate model score based on performance, cost, and load"""
        metrics = self.model_metrics.get(model, ModelMetrics())
        config = PRODUCTION_MODEL_CONFIGS.get(model)
        
        if not config:
            return 0.0
        
        # Base score from success rate and response time
        success_rate = (metrics.successful_requests / max(metrics.total_requests, 1))
        response_time_score = 1.0 / (metrics.average_response_time + 1.0)
        
        # Cost efficiency (lower cost = higher score)
        cost_score = 1.0 / (config.cost_per_input_token + config.cost_per_output_token + 0.001)
        
        # Load score (less loaded = higher score)
        load_score = await self._get_load_score(model)
        
        # Priority multiplier
        priority_multiplier = priority.value
        
        total_score = (
            success_rate * 0.4 +
            response_time_score * 0.3 +
            cost_score * 0.2 +
            load_score * 0.1
        ) * priority_multiplier
        
        return total_score
    
    async def _get_load_score(self, model: str) -> float:
        """Get current load score for a model"""
        rate_limit_key = f"rate_limit:{model}"
        current_requests = await self.redis.get(rate_limit_key)
        
        if current_requests is None:
            return 1.0
            
        config = PRODUCTION_MODEL_CONFIGS.get(model)
        if not config:
            return 0.0
            
        load_ratio = int(current_requests) / config.rate_limit_per_minute
        return max(0.0, 1.0 - load_ratio)
    
    def _get_available_models(self, task_type: str, user_tier: ModelTier) -> List[str]:
        """Get available models for task type and user tier"""
        task_config = get_model_config(task_type)
        
        if isinstance(task_config, dict):
            models = [task_config.get("primary")]
            if "fallback" in task_config:
                models.extend(task_config["fallback"])
        else:
            models = [task_config]
        
        # Filter by user tier
        available_models = []
        for model in models:
            if model and model in PRODUCTION_MODEL_CONFIGS:
                config = PRODUCTION_MODEL_CONFIGS[model]
                if self._is_model_available_for_tier(config, user_tier):
                    available_models.append(model)
        
        return available_models
    
    def _is_model_available_for_tier(self, config: ModelConfig, user_tier: ModelTier) -> bool:
        """Check if model is available for user tier"""
        tier_hierarchy = {
            ModelTier.FREE: [ModelTier.FREE],
            ModelTier.PRO: [ModelTier.FREE, ModelTier.PRO],
            ModelTier.ENTERPRISE: [ModelTier.FREE, ModelTier.PRO, ModelTier.ENTERPRISE]
        }
        
        return config.tier in tier_hierarchy.get(user_tier, [])

class CostTracker:
    """Track and manage LLM costs"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    async def track_usage(
        self, 
        user_id: str, 
        model: str, 
        input_tokens: int, 
        output_tokens: int, 
        cost: float
    ):
        """Track token usage and cost for a user"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Daily usage
        daily_key = f"usage:{user_id}:{today}"
        await self.redis.hincrby(daily_key, "tokens", input_tokens + output_tokens)
        await self.redis.hincrbyfloat(daily_key, "cost", cost)
        await self.redis.expire(daily_key, 86400 * 7)  # Keep for 7 days
        
        # Model-specific usage
        model_key = f"usage:{user_id}:{model}:{today}"
        await self.redis.hincrby(model_key, "requests", 1)
        await self.redis.hincrby(model_key, "input_tokens", input_tokens)
        await self.redis.hincrby(model_key, "output_tokens", output_tokens)
        await self.redis.hincrbyfloat(model_key, "cost", cost)
        await self.redis.expire(model_key, 86400 * 7)
    
    async def get_daily_usage(self, user_id: str) -> Dict[str, Any]:
        """Get daily usage for a user"""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_key = f"usage:{user_id}:{today}"
        
        usage = await self.redis.hgetall(daily_key)
        
        return {
            "tokens": int(usage.get("tokens", 0)),
            "cost": float(usage.get("cost", 0.0)),
            "date": today
        }
    
    async def check_budget_limit(self, user_id: str, user_tier: ModelTier) -> bool:
        """Check if user has exceeded budget limits"""
        daily_usage = await self.get_daily_usage(user_id)
        
        # Budget limits by tier
        budget_limits = {
            ModelTier.FREE: 0.50,
            ModelTier.PRO: 5.00,
            ModelTier.ENTERPRISE: 50.00
        }
        
        limit = budget_limits.get(user_tier, 0.50)
        return daily_usage["cost"] < limit

class ProductionLLMService:
    """Production-ready LLM service with comprehensive capabilities"""
    
    def __init__(self):
        self.redis = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        self.load_balancer = LoadBalancer(self.redis)
        self.cost_tracker = CostTracker(self.redis)
        self.error_handler = ErrorHandler()
        self.clients: Dict[str, BaseLanguageModel] = {}
        self.request_cache: Dict[str, LLMResponse] = {}
        
        # Initialize model clients
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize LLM clients for all configured models"""
        for model_name, config in PRODUCTION_MODEL_CONFIGS.items():
            try:
                client = self._create_client(model_name, config)
                self.clients[model_name] = client
                logger.info(f"Initialized client for {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize client for {model_name}: {e}")
    
    def _create_client(self, model_name: str, config: ModelConfig) -> BaseLanguageModel:
        """Create LLM client based on provider"""
        if config.provider == ModelProvider.OPENAI:
            return ChatOpenAI(
                model=model_name,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.7,
                max_tokens=config.max_tokens,
                timeout=30.0
            )
        elif config.provider == ModelProvider.ANTHROPIC:
            return ChatAnthropic(
                model=model_name,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                temperature=0.7,
                max_tokens=config.max_tokens,
                timeout=30.0
            )
        elif config.provider == ModelProvider.GOOGLE:
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.7,
                max_tokens=config.max_tokens,
                timeout=30.0
            )
        elif config.provider == ModelProvider.GROQ:
            return ChatGroq(
                model=model_name,
                groq_api_key=os.getenv("GROQ_API_KEY"),
                temperature=0.7,
                max_tokens=config.max_tokens,
                timeout=30.0
            )
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")
    
    async def generate(
        self,
        request: LLMRequest,
        task_type: str = "general",
        user_tier: ModelTier = ModelTier.FREE
    ) -> LLMResponse:
        """Generate response with comprehensive error handling and optimization"""
        
        start_time = time.time()
        request_id = self._generate_request_id()
        
        try:
            # Check budget limits
            if request.user_id:
                if not await self.cost_tracker.check_budget_limit(request.user_id, user_tier):
                    raise Exception("Budget limit exceeded")
            
            # Select optimal model
            selected_model = await self.load_balancer.select_model(
                request.model, 
                task_type, 
                user_tier, 
                request.priority
            )
            
            # Check cache
            cache_key = self._generate_cache_key(request, selected_model)
            cached_response = await self._get_cached_response(cache_key)
            
            if cached_response:
                logger.info(f"Cache hit for request {request_id}")
                return cached_response
            
            # Rate limiting
            await self._apply_rate_limit(selected_model)
            
            # Generate response
            response = await self._generate_with_retry(
                request, 
                selected_model, 
                request_id
            )
            
            # Track costs and usage
            if request.user_id:
                await self.cost_tracker.track_usage(
                    request.user_id,
                    selected_model,
                    response.input_tokens,
                    response.output_tokens,
                    response.cost
                )
            
            # Cache response
            await self._cache_response(cache_key, response)
            
            # Update metrics
            await self._update_metrics(selected_model, response, True)
            
            logger.info(f"Generated response for request {request_id} in {time.time() - start_time:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in generate for request {request_id}: {e}")
            await self._update_metrics(request.model, None, False)
            raise
    
    async def _generate_with_retry(
        self, 
        request: LLMRequest, 
        model: str, 
        request_id: str
    ) -> LLMResponse:
        """Generate response with retry logic"""
        
        last_error = None
        
        for attempt in range(request.retries + 1):
            try:
                return await self._generate_single(request, model, request_id)
            except Exception as e:
                last_error = e
                
                if attempt < request.retries:
                    # Exponential backoff
                    wait_time = (2 ** attempt) * 1.0
                    await asyncio.sleep(wait_time)
                    logger.warning(f"Retry {attempt + 1} for request {request_id} after {wait_time}s")
                else:
                    logger.error(f"All retries exhausted for request {request_id}")
        
        raise last_error
    
    async def _generate_single(
        self, 
        request: LLMRequest, 
        model: str, 
        request_id: str
    ) -> LLMResponse:
        """Generate single response"""
        
        client = self.clients.get(model)
        if not client:
            raise ValueError(f"No client available for model: {model}")
        
        config = PRODUCTION_MODEL_CONFIGS.get(model)
        if not config:
            raise ValueError(f"No configuration found for model: {model}")
        
        start_time = time.time()
        
        # Prepare request
        kwargs = {
            "temperature": request.temperature,
            "max_tokens": request.max_tokens or config.max_tokens,
        }
        
        # Generate response
        if request.stream:
            # Handle streaming
            response_chunks = []
            async for chunk in client.astream(request.messages, **kwargs):
                response_chunks.append(chunk.content)
            
            content = "".join(response_chunks)
        else:
            # Regular generation
            response = await client.ainvoke(request.messages, **kwargs)
            content = response.content
        
        response_time = time.time() - start_time
        
        # Calculate tokens and cost
        input_tokens = self._estimate_tokens(request.messages)
        output_tokens = self._estimate_tokens([content])
        cost = self._calculate_cost(config, input_tokens, output_tokens)
        
        return LLMResponse(
            content=content,
            model=model,
            provider=config.provider.value,
            tokens_used=input_tokens + output_tokens,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            response_time=response_time,
            request_id=request_id,
            metadata=request.metadata
        )
    
    def _estimate_tokens(self, messages: Union[List[BaseMessage], List[str]]) -> int:
        """Estimate token count for messages"""
        if isinstance(messages, list) and len(messages) > 0:
            if isinstance(messages[0], BaseMessage):
                text = " ".join([msg.content for msg in messages])
            else:
                text = " ".join(messages)
        else:
            text = str(messages)
        
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def _calculate_cost(self, config: ModelConfig, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage"""
        input_cost = input_tokens * config.cost_per_input_token / 1000
        output_cost = output_tokens * config.cost_per_output_token / 1000
        return input_cost + output_cost
    
    async def _apply_rate_limit(self, model: str):
        """Apply rate limiting for model"""
        rate_limit_key = f"rate_limit:{model}"
        
        # Increment request count
        pipe = self.redis.pipeline()
        pipe.incr(rate_limit_key)
        pipe.expire(rate_limit_key, 60)  # 1 minute window
        await pipe.execute()
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        return f"req_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
    
    def _generate_cache_key(self, request: LLMRequest, model: str) -> str:
        """Generate cache key for request"""
        messages_str = json.dumps([msg.content for msg in request.messages])
        key_data = f"{model}:{messages_str}:{request.temperature}:{request.max_tokens}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _get_cached_response(self, cache_key: str) -> Optional[LLMResponse]:
        """Get cached response if available"""
        cached_data = await self.redis.get(f"cache:{cache_key}")
        
        if cached_data:
            try:
                data = json.loads(cached_data)
                return LLMResponse(**data)
            except Exception as e:
                logger.error(f"Error deserializing cached response: {e}")
        
        return None
    
    async def _cache_response(self, cache_key: str, response: LLMResponse):
        """Cache response with TTL"""
        try:
            response_data = asdict(response)
            response_data["cached"] = True
            
            await self.redis.setex(
                f"cache:{cache_key}",
                300,  # 5 minutes TTL
                json.dumps(response_data)
            )
        except Exception as e:
            logger.error(f"Error caching response: {e}")
    
    async def _update_metrics(self, model: str, response: Optional[LLMResponse], success: bool):
        """Update model metrics"""
        metrics_key = f"metrics:{model}"
        
        pipe = self.redis.pipeline()
        pipe.hincrby(metrics_key, "total_requests", 1)
        
        if success and response:
            pipe.hincrby(metrics_key, "successful_requests", 1)
            pipe.hincrby(metrics_key, "total_tokens", response.tokens_used)
            pipe.hincrbyfloat(metrics_key, "total_cost", response.cost)
            pipe.hincrbyfloat(metrics_key, "total_response_time", response.response_time)
        else:
            pipe.hincrby(metrics_key, "failed_requests", 1)
        
        pipe.expire(metrics_key, 86400)  # 1 day TTL
        await pipe.execute()

# Production model configurations
PRODUCTION_MODEL_CONFIGS = {
    "gemini-2.5-pro": ModelConfig(
        name="gemini-2.5-pro",
        provider=ModelProvider.GOOGLE,
        tier=ModelTier.PRO,
        max_tokens=8192,
        cost_per_input_token=0.00125,
        cost_per_output_token=0.00375,
        rate_limit_per_minute=60,
        context_window=1000000,
        supports_streaming=True,
        fallback_models=["gpt-4o", "claude-3-sonnet"]
    ),
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        provider=ModelProvider.OPENAI,
        tier=ModelTier.PRO,
        max_tokens=4096,
        cost_per_input_token=0.005,
        cost_per_output_token=0.015,
        rate_limit_per_minute=50,
        context_window=128000,
        supports_streaming=True,
        supports_function_calling=True,
        fallback_models=["gpt-4o-mini", "claude-3-haiku"]
    ),
    "claude-3-sonnet": ModelConfig(
        name="claude-3-sonnet",
        provider=ModelProvider.ANTHROPIC,
        tier=ModelTier.PRO,
        max_tokens=4096,
        cost_per_input_token=0.003,
        cost_per_output_token=0.015,
        rate_limit_per_minute=40,
        context_window=200000,
        supports_streaming=True,
        fallback_models=["claude-3-haiku", "gpt-4o-mini"]
    ),
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        provider=ModelProvider.OPENAI,
        tier=ModelTier.FREE,
        max_tokens=4096,
        cost_per_input_token=0.00015,
        cost_per_output_token=0.0006,
        rate_limit_per_minute=100,
        context_window=128000,
        supports_streaming=True,
        supports_function_calling=True,
        fallback_models=["claude-3-haiku"]
    ),
    "claude-3-haiku": ModelConfig(
        name="claude-3-haiku",
        provider=ModelProvider.ANTHROPIC,
        tier=ModelTier.FREE,
        max_tokens=4096,
        cost_per_input_token=0.00025,
        cost_per_output_token=0.00125,
        rate_limit_per_minute=80,
        context_window=200000,
        supports_streaming=True,
        fallback_models=["gpt-4o-mini"]
    )
}

# Singleton instance
production_llm_service = ProductionLLMService()

# Export for use in other modules
__all__ = [
    "ProductionLLMService",
    "LLMRequest",
    "LLMResponse",
    "ModelConfig",
    "ModelProvider",
    "ModelTier",
    "RequestPriority",
    "production_llm_service"
]