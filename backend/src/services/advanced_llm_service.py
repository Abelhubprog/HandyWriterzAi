"""
Advanced LLM Service with connection pooling, caching, circuit breakers, and adaptive routing.
"""

import asyncio
import os
import time
from typing import Dict, Any, Optional, List, Union, AsyncIterator
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
import redis
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    GROQ = "groq"
    CLAUDE = "claude"

@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    provider: ModelProvider
    model_name: str
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    max_retries: int = 3
    cost_per_token: float = 0.0
    rate_limit_rpm: int = 60
    rate_limit_tpm: int = 10000
    max_concurrent_requests: int = 5
    priority: int = 1  # Lower numbers = higher priority

@dataclass
class RequestMetrics:
    """Metrics for tracking request performance."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    avg_response_time: float = 0.0
    last_request_time: Optional[datetime] = None
    current_concurrent_requests: int = 0

@dataclass
class CircuitBreakerState:
    """State for circuit breaker pattern."""
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    failure_threshold: int = 5
    recovery_timeout: int = 60

class StreamingCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for streaming responses."""
    
    def __init__(self, callback_func):
        self.callback_func = callback_func
        self.tokens = []
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Handle new token generation."""
        self.tokens.append(token)
        if self.callback_func:
            self.callback_func(token)

class AdvancedLLMService:
    """Advanced LLM service with enterprise-grade features."""
    
    def __init__(self, redis_url: str = None):
        self.models: Dict[str, ModelConfig] = {}
        self.clients: Dict[str, Any] = {}
        self.metrics: Dict[str, RequestMetrics] = {}
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.rate_limiters: Dict[str, Dict] = {}
        self.connection_pools: Dict[str, Any] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Initialize Redis for caching
        self.redis_client = None
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
        
        # Initialize model configurations
        self._initialize_models()
        
        # Background tasks
        self._monitoring_task = None
        self._cleanup_task = None
    
    def _initialize_models(self):
        """Initialize model configurations."""
        self.models = {
            "gemini-1.5-flash": ModelConfig(
                provider=ModelProvider.GEMINI,
                model_name="gemini-1.5-flash",
                max_tokens=8192,
                temperature=0.7,
                timeout=30,
                max_retries=3,
                cost_per_token=0.000075,
                rate_limit_rpm=1000,
                rate_limit_tpm=1000000,
                max_concurrent_requests=10,
                priority=1
            ),
            "gemini-1.5-pro": ModelConfig(
                provider=ModelProvider.GEMINI,
                model_name="gemini-1.5-pro",
                max_tokens=8192,
                temperature=0.7,
                timeout=60,
                max_retries=3,
                cost_per_token=0.0035,
                rate_limit_rpm=360,
                rate_limit_tpm=120000,
                max_concurrent_requests=5,
                priority=2
            ),
            "gpt-4o": ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4o",
                max_tokens=4096,
                temperature=0.7,
                timeout=45,
                max_retries=3,
                cost_per_token=0.06,
                rate_limit_rpm=500,
                rate_limit_tpm=150000,
                max_concurrent_requests=3,
                priority=3
            ),
            "gpt-4o-mini": ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4o-mini",
                max_tokens=4096,
                temperature=0.7,
                timeout=30,
                max_retries=3,
                cost_per_token=0.00015,
                rate_limit_rpm=1000,
                rate_limit_tpm=200000,
                max_concurrent_requests=8,
                priority=1
            ),
            "mixtral-8x7b": ModelConfig(
                provider=ModelProvider.GROQ,
                model_name="mixtral-8x7b-32768",
                max_tokens=32768,
                temperature=0.7,
                timeout=20,
                max_retries=3,
                cost_per_token=0.00024,
                rate_limit_rpm=30,
                rate_limit_tpm=14400,
                max_concurrent_requests=2,
                priority=2
            ),
        }
        
        # Initialize metrics and circuit breakers
        for model_name in self.models.keys():
            self.metrics[model_name] = RequestMetrics()
            self.circuit_breakers[model_name] = CircuitBreakerState()
            self.rate_limiters[model_name] = {
                "requests": [],
                "tokens": [],
            }
    
    def _get_client(self, model_name: str) -> Any:
        """Get or create a client for the specified model."""
        if model_name not in self.clients:
            config = self.models[model_name]
            
            if config.provider == ModelProvider.GEMINI:
                self.clients[model_name] = ChatGoogleGenerativeAI(
                    model=config.model_name,
                    api_key=os.getenv("GEMINI_API_KEY"),
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout
                )
            elif config.provider == ModelProvider.OPENAI:
                self.clients[model_name] = ChatOpenAI(
                    model=config.model_name,
                    api_key=os.getenv("OPENAI_API_KEY"),
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout
                )
            elif config.provider == ModelProvider.GROQ:
                self.clients[model_name] = ChatGroq(
                    model=config.model_name,
                    api_key=os.getenv("GROQ_API_KEY"),
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout
                )
            else:
                raise ValueError(f"Unsupported provider: {config.provider}")
        
        return self.clients[model_name]
    
    def _check_rate_limit(self, model_name: str, estimated_tokens: int = 0) -> bool:
        """Check if request is within rate limits."""
        config = self.models[model_name]
        rate_limiter = self.rate_limiters[model_name]
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        rate_limiter["requests"] = [
            req_time for req_time in rate_limiter["requests"]
            if current_time - req_time < 60
        ]
        rate_limiter["tokens"] = [
            (req_time, tokens) for req_time, tokens in rate_limiter["tokens"]
            if current_time - req_time < 60
        ]
        
        # Check request rate limit
        if len(rate_limiter["requests"]) >= config.rate_limit_rpm:
            return False
        
        # Check token rate limit
        total_tokens = sum(tokens for _, tokens in rate_limiter["tokens"])
        if total_tokens + estimated_tokens > config.rate_limit_tpm:
            return False
        
        return True
    
    def _update_rate_limit(self, model_name: str, tokens_used: int):
        """Update rate limit counters."""
        current_time = time.time()
        rate_limiter = self.rate_limiters[model_name]
        
        rate_limiter["requests"].append(current_time)
        rate_limiter["tokens"].append((current_time, tokens_used))
    
    def _check_circuit_breaker(self, model_name: str) -> bool:
        """Check if circuit breaker allows request."""
        circuit_breaker = self.circuit_breakers[model_name]
        current_time = datetime.now()
        
        if circuit_breaker.state == "OPEN":
            if (current_time - circuit_breaker.last_failure_time).seconds > circuit_breaker.recovery_timeout:
                circuit_breaker.state = "HALF_OPEN"
                circuit_breaker.failure_count = 0
                return True
            return False
        
        return True
    
    def _update_circuit_breaker(self, model_name: str, success: bool):
        """Update circuit breaker state."""
        circuit_breaker = self.circuit_breakers[model_name]
        
        if success:
            circuit_breaker.failure_count = 0
            circuit_breaker.state = "CLOSED"
        else:
            circuit_breaker.failure_count += 1
            circuit_breaker.last_failure_time = datetime.now()
            
            if circuit_breaker.failure_count >= circuit_breaker.failure_threshold:
                circuit_breaker.state = "OPEN"
    
    def _update_metrics(self, model_name: str, success: bool, tokens_used: int, response_time: float, cost: float):
        """Update model metrics."""
        metrics = self.metrics[model_name]
        
        metrics.total_requests += 1
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
        
        metrics.total_tokens += tokens_used
        metrics.total_cost += cost
        
        # Update average response time
        if metrics.total_requests > 1:
            metrics.avg_response_time = (
                (metrics.avg_response_time * (metrics.total_requests - 1) + response_time) / 
                metrics.total_requests
            )
        else:
            metrics.avg_response_time = response_time
        
        metrics.last_request_time = datetime.now()
    
    def _get_cache_key(self, messages: List[BaseMessage], model_name: str, **kwargs) -> str:
        """Generate cache key for request."""
        content = json.dumps([
            {"role": msg.type, "content": msg.content} for msg in messages
        ], sort_keys=True)
        
        cache_input = f"{model_name}:{content}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get response from cache."""
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(f"llm_cache:{cache_key}")
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
        
        return None
    
    def _set_cache(self, cache_key: str, response: Dict[str, Any], ttl: int = 3600):
        """Set response in cache."""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.setex(
                f"llm_cache:{cache_key}",
                ttl,
                json.dumps(response)
            )
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    def _select_best_model(self, task: str, preferred_model: str = None) -> str:
        """Select the best model for the task based on availability and performance."""
        if preferred_model and preferred_model in self.models:
            if self._check_circuit_breaker(preferred_model):
                return preferred_model
        
        # Get available models sorted by priority and performance
        available_models = []
        for model_name, config in self.models.items():
            if self._check_circuit_breaker(model_name):
                metrics = self.metrics[model_name]
                success_rate = (
                    metrics.successful_requests / max(metrics.total_requests, 1)
                )
                
                score = (
                    success_rate * 0.4 +
                    (1 / max(metrics.avg_response_time, 0.1)) * 0.3 +
                    (1 / max(config.priority, 1)) * 0.3
                )
                
                available_models.append((model_name, score))
        
        if not available_models:
            # Fallback to the first available model
            for model_name in self.models.keys():
                if self._check_circuit_breaker(model_name):
                    return model_name
            
            # If all models are circuit broken, use the most recently failed one
            return min(
                self.circuit_breakers.keys(),
                key=lambda x: self.circuit_breakers[x].last_failure_time or datetime.min
            )
        
        # Return the best scoring model
        return max(available_models, key=lambda x: x[1])[0]
    
    async def generate_response(
        self,
        messages: List[BaseMessage],
        task: str = "general",
        preferred_model: str = None,
        use_cache: bool = True,
        stream: bool = False,
        **kwargs
    ) -> Union[str, AsyncIterator[str]]:
        """Generate response using the best available model."""
        
        # Select model
        model_name = self._select_best_model(task, preferred_model)
        config = self.models[model_name]
        
        # Check rate limits
        estimated_tokens = sum(len(msg.content.split()) for msg in messages) * 1.3
        if not self._check_rate_limit(model_name, int(estimated_tokens)):
            # Try fallback models
            for fallback_model in self.models.keys():
                if (fallback_model != model_name and 
                    self._check_rate_limit(fallback_model, int(estimated_tokens)) and
                    self._check_circuit_breaker(fallback_model)):
                    model_name = fallback_model
                    config = self.models[model_name]
                    break
            else:
                raise Exception("Rate limit exceeded for all models")
        
        # Check cache
        cache_key = None
        if use_cache and not stream:
            cache_key = self._get_cache_key(messages, model_name, **kwargs)
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                return cached_response["content"]
        
        # Update concurrent requests
        self.metrics[model_name].current_concurrent_requests += 1
        
        start_time = time.time()
        success = False
        tokens_used = 0
        cost = 0.0
        
        try:
            # Get client
            client = self._get_client(model_name)
            
            # Execute request
            if stream:
                return self._stream_response(client, messages, model_name, **kwargs)
            else:
                response = await self._execute_request(client, messages, **kwargs)
                
                # Calculate metrics
                tokens_used = len(response.split()) * 1.3  # Rough estimate
                cost = tokens_used * config.cost_per_token
                success = True
                
                # Cache response
                if use_cache and cache_key:
                    self._set_cache(cache_key, {
                        "content": response,
                        "model": model_name,
                        "timestamp": datetime.now().isoformat()
                    })
                
                return response
                
        except Exception as e:
            logger.error(f"Request failed for model {model_name}: {e}")
            self._update_circuit_breaker(model_name, False)
            raise
        
        finally:
            # Update metrics
            response_time = time.time() - start_time
            self._update_metrics(model_name, success, int(tokens_used), response_time, cost)
            self._update_rate_limit(model_name, int(tokens_used))
            self.metrics[model_name].current_concurrent_requests -= 1
    
    async def _execute_request(self, client: Any, messages: List[BaseMessage], **kwargs) -> str:
        """Execute the actual request to the model."""
        loop = asyncio.get_event_loop()
        
        def _sync_call():
            try:
                response = client.invoke(messages, **kwargs)
                return response.content
            except Exception as e:
                logger.error(f"Model invocation failed: {e}")
                raise
        
        return await loop.run_in_executor(self.executor, _sync_call)
    
    async def _stream_response(self, client: Any, messages: List[BaseMessage], model_name: str, **kwargs) -> AsyncIterator[str]:
        """Stream response from model."""
        tokens_generated = 0
        
        async def token_generator():
            nonlocal tokens_generated
            
            def callback(token: str):
                nonlocal tokens_generated
                tokens_generated += 1
                return token
            
            callback_handler = StreamingCallbackHandler(callback)
            
            try:
                loop = asyncio.get_event_loop()
                
                def _sync_stream():
                    response = client.stream(messages, callbacks=[callback_handler], **kwargs)
                    return response
                
                response_stream = await loop.run_in_executor(self.executor, _sync_stream)
                
                for chunk in response_stream:
                    if hasattr(chunk, 'content') and chunk.content:
                        yield chunk.content
                
            except Exception as e:
                logger.error(f"Streaming failed for model {model_name}: {e}")
                raise
        
        async for token in token_generator():
            yield token
    
    def get_model_metrics(self, model_name: str = None) -> Dict[str, Any]:
        """Get metrics for a specific model or all models."""
        if model_name:
            metrics = self.metrics.get(model_name, {})
            circuit_breaker = self.circuit_breakers.get(model_name, {})
            
            return {
                "model": model_name,
                "metrics": metrics,
                "circuit_breaker": circuit_breaker,
                "rate_limiter": self.rate_limiters.get(model_name, {})
            }
        else:
            return {
                model_name: {
                    "metrics": metrics,
                    "circuit_breaker": self.circuit_breakers[model_name],
                    "rate_limiter": self.rate_limiters[model_name]
                }
                for model_name, metrics in self.metrics.items()
            }
    
    def reset_circuit_breaker(self, model_name: str):
        """Manually reset circuit breaker for a model."""
        if model_name in self.circuit_breakers:
            self.circuit_breakers[model_name].state = "CLOSED"
            self.circuit_breakers[model_name].failure_count = 0
            self.circuit_breakers[model_name].last_failure_time = None
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all models."""
        health_status = {}
        
        for model_name in self.models.keys():
            try:
                test_message = [HumanMessage(content="Hello, this is a health check.")]
                response = await self.generate_response(
                    test_message,
                    preferred_model=model_name,
                    use_cache=False
                )
                
                health_status[model_name] = {
                    "status": "healthy",
                    "response_length": len(response),
                    "circuit_breaker": self.circuit_breakers[model_name].state
                }
            except Exception as e:
                health_status[model_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "circuit_breaker": self.circuit_breakers[model_name].state
                }
        
        return health_status
    
    async def __aenter__(self):
        """Async context manager entry."""
        # Start background monitoring tasks
        self._monitoring_task = asyncio.create_task(self._monitor_performance())
        self._cleanup_task = asyncio.create_task(self._cleanup_resources())
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cancel background tasks
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
    
    async def _monitor_performance(self):
        """Background task to monitor model performance."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Log performance metrics
                for model_name, metrics in self.metrics.items():
                    if metrics.total_requests > 0:
                        success_rate = metrics.successful_requests / metrics.total_requests
                        logger.info(f"Model {model_name}: {success_rate:.2%} success rate, "
                                  f"{metrics.avg_response_time:.2f}s avg response time")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
    
    async def _cleanup_resources(self):
        """Background task to cleanup resources."""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
                # Clear old rate limit data
                current_time = time.time()
                for model_name, rate_limiter in self.rate_limiters.items():
                    rate_limiter["requests"] = [
                        req_time for req_time in rate_limiter["requests"]
                        if current_time - req_time < 60
                    ]
                    rate_limiter["tokens"] = [
                        (req_time, tokens) for req_time, tokens in rate_limiter["tokens"]
                        if current_time - req_time < 60
                    ]
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Resource cleanup error: {e}")

# Global instance
_llm_service = None

def get_advanced_llm_service() -> AdvancedLLMService:
    """Get global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        _llm_service = AdvancedLLMService(redis_url)
    return _llm_service

# Legacy compatibility
def get_llm_client(task: str, model_preference: str = None):
    """Legacy function for backward compatibility."""
    service = get_advanced_llm_service()
    model_name = service._select_best_model(task, model_preference)
    return service._get_client(model_name)