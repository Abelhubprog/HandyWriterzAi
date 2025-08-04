"""
Unified LLM Gateway with provider abstraction, tracing, retries, and streaming.
Compatible with existing HandyWriterz architecture.
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, AsyncIterator, Any, Union
from contextlib import asynccontextmanager

import openai
import httpx
from anthropic import AsyncAnthropic
from google.generativeai import configure as configure_gemini
import google.generativeai as genai

from ..config.settings import get_settings
from ..services.budget import BudgetGuard, CostLevel
from ..services.cost_tracker import CostTracker
from .tracing import DistributedTracer, TraceContext


logger = logging.getLogger(__name__)


class ProviderType(str, Enum):
    """Supported provider types"""
    OPENROUTER = "openrouter"
    DIRECT_OPENAI = "direct_openai"
    DIRECT_ANTHROPIC = "direct_anthropic"
    DIRECT_GEMINI = "direct_gemini"
    DIRECT_PERPLEXITY = "direct_perplexity"


@dataclass
class ModelCapability:
    """Model capability specification"""
    streaming: bool = False
    function_calling: bool = False
    vision: bool = False
    reasoning: bool = False
    web_search: bool = False
    long_context: bool = False
    creative_writing: bool = False
    code_generation: bool = False
    json_mode: bool = False


@dataclass
class ModelSpec:
    """Complete model specification"""
    logical_id: str
    provider: ProviderType
    provider_model_id: str
    capabilities: ModelCapability
    cost_tier: CostLevel
    context_window: int
    input_cost_per_1k: float
    output_cost_per_1k: float
    fallback_models: List[str] = None
    admin_overridable: bool = True
    
    def __post_init__(self):
        if self.fallback_models is None:
            self.fallback_models = []


@dataclass
class LLMRequest:
    """Standardized LLM request"""
    messages: List[Dict[str, str]]
    model_spec: ModelSpec
    node_name: str
    trace_id: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    capabilities: List[str] = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    model_used: str
    provider: str
    tokens_used: Dict[str, int]
    cost_usd: float
    latency_ms: int
    trace_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ProviderGateway(ABC):
    """Abstract base for all provider gateways"""
    
    @abstractmethod
    async def chat(self, request: LLMRequest) -> LLMResponse:
        """Execute chat completion"""
        pass
    
    @abstractmethod
    async def stream_chat(self, request: LLMRequest) -> AsyncIterator[Dict[str, Any]]:
        """Execute streaming chat completion"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health"""
        pass


class OpenRouterGateway(ProviderGateway):
    """OpenRouter unified gateway implementation"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = openai.AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.settings.openrouter_api_key,
            default_headers={
                "HTTP-Referer": self.settings.app_url,
                "X-Title": "HandyWriterz AI Platform"
            }
        )
        
        # OpenRouter model mapping - SOTA models March 2025+ (Accurate Names)
        self.model_mapping = {
            # Google SOTA Models
            "gemini-2.5-pro": "google/gemini-2.5-pro-exp",
            "gemini-2.5-flash": "google/gemini-2.5-flash",
            
            # OpenAI SOTA Models (Corrected Names)
            "chatgpt-o3": "openai/o3",
            "chatgpt-4.1": "openai/gpt-4.1-turbo", 
            "o4-mini": "openai/o4-mini-2025-04-16",  # Corrected: not "4o-mini-high"
            "gpt-4o-mini": "openai/gpt-4o-mini",
            "chatgpt-4o": "openai/gpt-4o",
            
            # Anthropic SOTA Models
            "claude-4-sonnet": "anthropic/claude-4-sonnet",
            "claude-4-opus": "anthropic/claude-4-opus",
            
            # Specialized SOTA Models
            "deepseek-r1": "deepseek/deepseek-r1",
            "perplexity-deepresearch": "perplexity/deepresearch",
            "qwen-3": "qwen/qwen-3",
            "glm-4.5": "zhipuai/glm-4.5",
            "kimi-k2": "moonshot/kimi-k2",
            
            # New Open Source SOTA Model
            "xbai-04": "metastonetec/xbai-04",
            
            # OpenRouter Stealth Models (Free, Always SOTA)
            "horizon-alpha": "openrouter/horizon-alpha",
            "optimus-alpha": "openrouter/optimus-alpha", 
            "cypher-alpha": "openrouter/cypher-alpha",
            
            # Latest Free Models
            "llama-4-maverick": "meta/llama-4-maverick-400b",
            "llama-4-scout": "meta/llama-4-scout-109b",
            "mistral-small-3.1": "mistralai/mistral-small-3.1"
        }
    
    def _map_model_id(self, logical_id: str) -> str:
        """Map logical model ID to OpenRouter model ID"""
        return self.model_mapping.get(logical_id, logical_id)
    
    async def chat(self, request: LLMRequest) -> LLMResponse:
        """Execute chat completion via OpenRouter"""
        start_time = time.time()
        
        try:
            openrouter_model = self._map_model_id(request.model_spec.logical_id)
            
            response = await self.client.chat.completions.create(
                model=openrouter_model,
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=False
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Calculate costs (OpenRouter provides usage info)
            tokens_used = {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
            
            cost_usd = self._calculate_cost(
                openrouter_model, 
                tokens_used["input"], 
                tokens_used["output"]
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model_used=openrouter_model,
                provider="openrouter",
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                latency_ms=latency_ms,
                trace_id=request.trace_id,
                metadata={"openrouter_id": response.id}
            )
            
        except Exception as e:
            logger.error(f"OpenRouter chat error: {e}")
            raise
    
    async def stream_chat(self, request: LLMRequest) -> AsyncIterator[Dict[str, Any]]:
        """Execute streaming chat completion via OpenRouter"""
        try:
            openrouter_model = self._map_model_id(request.model_spec.logical_id)
            
            stream = await self.client.chat.completions.create(
                model=openrouter_model,
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield {
                        "type": "content",
                        "token": chunk.choices[0].delta.content,
                        "model": openrouter_model,
                        "provider": "openrouter"
                    }
                    
        except Exception as e:
            logger.error(f"OpenRouter streaming error: {e}")
            yield {
                "type": "error",
                "error": str(e),
                "provider": "openrouter"
            }
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on SOTA model pricing (March 2025+)"""
        cost_per_1k = {
            # Google SOTA Models
            "google/gemini-2.5-pro-exp": {"input": 0.00125, "output": 0.005},
            "google/gemini-2.5-flash": {"input": 0.000075, "output": 0.0003},
            
            # OpenAI SOTA Models (Corrected)
            "openai/o3": {"input": 0.015, "output": 0.06},
            "openai/gpt-4.1-turbo": {"input": 0.0075, "output": 0.025},
            "openai/o4-mini-2025-04-16": {"input": 0.00015, "output": 0.0006},  # Corrected pricing
            "openai/gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "openai/gpt-4o": {"input": 0.005, "output": 0.015},
            
            # Anthropic SOTA Models
            "anthropic/claude-4-sonnet": {"input": 0.003, "output": 0.015},
            "anthropic/claude-4-opus": {"input": 0.015, "output": 0.075},
            
            # Specialized SOTA Models
            "deepseek/deepseek-r1": {"input": 0.00055, "output": 0.0022},
            "perplexity/deepresearch": {"input": 0.005, "output": 0.005},
            "qwen/qwen-3": {"input": 0.0008, "output": 0.0008},
            "zhipuai/glm-4.5": {"input": 0.001, "output": 0.001},
            "moonshot/kimi-k2": {"input": 0.00012, "output": 0.00012},
            
            # New Open Source Model
            "metastonetec/xbai-04": {"input": 0.0005, "output": 0.0015},
            
            # OpenRouter Stealth Models (FREE!)
            "openrouter/horizon-alpha": {"input": 0.0, "output": 0.0},
            "openrouter/optimus-alpha": {"input": 0.0, "output": 0.0},
            "openrouter/cypher-alpha": {"input": 0.0, "output": 0.0},
            
            # Latest Free Models
            "meta/llama-4-maverick-400b": {"input": 0.0, "output": 0.0},
            "meta/llama-4-scout-109b": {"input": 0.0, "output": 0.0},
            "mistralai/mistral-small-3.1": {"input": 0.0, "output": 0.0}
        }
        
        pricing = cost_per_1k.get(model, {"input": 0.001, "output": 0.003})
        return (input_tokens * pricing["input"] / 1000) + (output_tokens * pricing["output"] / 1000)
    
    def get_available_models(self) -> List[str]:
        """Get available SOTA models"""
        return list(self.model_mapping.keys())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check OpenRouter health"""
        try:
            # Simple health check with free SOTA model
            response = await self.client.chat.completions.create(
                model="openrouter/horizon-alpha",
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5
            )
            return {
                "status": "healthy",
                "latency_ms": 0,  # Could track actual latency
                "available_models": len(self.model_mapping)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


class DirectOpenAIGateway(ProviderGateway):
    """Direct OpenAI provider gateway"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = openai.AsyncOpenAI(api_key=self.settings.openai_api_key)
    
    async def chat(self, request: LLMRequest) -> LLMResponse:
        """Execute chat completion via direct OpenAI"""
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=request.model_spec.provider_model_id,
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            tokens_used = {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
            
            cost_usd = (tokens_used["input"] * request.model_spec.input_cost_per_1k / 1000) + \
                      (tokens_used["output"] * request.model_spec.output_cost_per_1k / 1000)
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model_used=request.model_spec.provider_model_id,
                provider="direct_openai",
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                latency_ms=latency_ms,
                trace_id=request.trace_id
            )
            
        except Exception as e:
            logger.error(f"Direct OpenAI error: {e}")
            raise
    
    async def stream_chat(self, request: LLMRequest) -> AsyncIterator[Dict[str, Any]]:
        """Execute streaming chat completion via direct OpenAI"""
        try:
            stream = await self.client.chat.completions.create(
                model=request.model_spec.provider_model_id,
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield {
                        "type": "content",
                        "token": chunk.choices[0].delta.content,
                        "model": request.model_spec.provider_model_id,
                        "provider": "direct_openai"
                    }
                    
        except Exception as e:
            logger.error(f"Direct OpenAI streaming error: {e}")
            yield {
                "type": "error",
                "error": str(e),
                "provider": "direct_openai"
            }
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI SOTA models"""
        return ["chatgpt-o3", "chatgpt-4.1", "o4-mini", "gpt-4o-mini", "chatgpt-4o"]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check OpenAI health"""
        try:
            models = await self.client.models.list()
            return {
                "status": "healthy",
                "available_models": len(models.data)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


class UnifiedLLMGateway:
    """Main gateway orchestrating all providers with tracing, retries, and streaming"""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Initialize provider gateways
        self.gateways = {
            ProviderType.OPENROUTER: OpenRouterGateway(),
            ProviderType.DIRECT_OPENAI: DirectOpenAIGateway(),
            # Add other providers as needed
        }
        
        # Initialize supporting services
        self.tracer = DistributedTracer()
        self.budget_guard = BudgetGuard()
        self.cost_tracker = CostTracker()
        
        # Configuration
        self.max_retries = 3
        self.retry_delay = 1.0
        
    @asynccontextmanager
    async def _trace_execution(self, request: LLMRequest):
        """Trace execution context"""
        trace_context = TraceContext(
            trace_id=request.trace_id,
            operation=f"llm_call_{request.node_name}",
            metadata={
                "model": request.model_spec.logical_id,
                "provider": request.model_spec.provider,
                "node": request.node_name
            }
        )
        
        async with self.tracer.span(trace_context):
            yield trace_context
    
    async def _check_budget(self, request: LLMRequest) -> None:
        """Check budget constraints before execution"""
        estimated_cost = self._estimate_cost(request)
        
        await self.budget_guard.check_request_budget(
            user_id=request.user_id or "system",
            estimated_cost=estimated_cost,
            cost_level=request.model_spec.cost_tier
        )
    
    def _estimate_cost(self, request: LLMRequest) -> float:
        """Estimate request cost for budget checking"""
        # Rough estimation based on message length
        total_chars = sum(len(msg.get("content", "")) for msg in request.messages)
        estimated_tokens = total_chars // 4  # Rough token estimation
        
        return (estimated_tokens * request.model_spec.input_cost_per_1k / 1000) + \
               ((request.max_tokens or 1000) * request.model_spec.output_cost_per_1k / 1000)
    
    async def _execute_with_retry(self, request: LLMRequest, gateway: ProviderGateway) -> LLMResponse:
        """Execute request with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                if request.stream:
                    # Streaming handled separately
                    raise ValueError("Use stream_execute for streaming requests")
                
                return await gateway.chat(request)
                
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    
        raise last_error
    
    async def _try_fallback_models(self, request: LLMRequest) -> LLMResponse:
        """Try fallback models if primary fails"""
        for fallback_model in request.model_spec.fallback_models:
            try:
                # Create new request with fallback model
                fallback_request = LLMRequest(
                    messages=request.messages,
                    model_spec=await self._get_model_spec(fallback_model),  # Need to implement
                    node_name=request.node_name,
                    trace_id=request.trace_id,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    capabilities=request.capabilities,
                    user_id=request.user_id
                )
                
                gateway = self.gateways[fallback_request.model_spec.provider]
                return await self._execute_with_retry(fallback_request, gateway)
                
            except Exception as e:
                logger.warning(f"Fallback model {fallback_model} failed: {e}")
                continue
                
        raise Exception("All fallback models failed")
    
    async def execute(self, request: LLMRequest) -> LLMResponse:
        """Main execution method with full error handling and tracing"""
        async with self._trace_execution(request) as trace_context:
            try:
                # Pre-execution checks
                await self._check_budget(request)
                
                # Get appropriate gateway
                gateway = self.gateways[request.model_spec.provider]
                
                # Execute with retries
                try:
                    response = await self._execute_with_retry(request, gateway)
                except Exception as primary_error:
                    logger.error(f"Primary model failed: {primary_error}")
                    
                    # Try fallback models
                    if request.model_spec.fallback_models:
                        response = await self._try_fallback_models(request)
                    else:
                        raise primary_error
                
                # Post-execution tracking
                await self._track_usage(response)
                
                # Update trace with results
                trace_context.metadata.update({
                    "tokens_used": response.tokens_used["total"],
                    "cost_usd": response.cost_usd,
                    "latency_ms": response.latency_ms
                })
                
                return response
                
            except Exception as e:
                trace_context.metadata["error"] = str(e)
                logger.error(f"Gateway execution failed: {e}")
                raise
    
    async def stream_execute(self, request: LLMRequest) -> AsyncIterator[Dict[str, Any]]:
        """Execute streaming request with tracing"""
        async with self._trace_execution(request) as trace_context:
            try:
                await self._check_budget(request)
                
                gateway = self.gateways[request.model_spec.provider]
                
                total_tokens = 0
                async for chunk in gateway.stream_chat(request):
                    if chunk.get("type") == "content":
                        total_tokens += 1  # Rough token counting
                    yield chunk
                
                # Update trace with streaming metrics
                trace_context.metadata.update({
                    "tokens_streamed": total_tokens,
                    "streaming": True
                })
                
            except Exception as e:
                trace_context.metadata["error"] = str(e)
                yield {
                    "type": "error",
                    "error": str(e),
                    "provider": request.model_spec.provider
                }
    
    async def _track_usage(self, response: LLMResponse) -> None:
        """Track usage and costs"""
        await self.cost_tracker.track_usage(
            model=response.model_used,
            provider=response.provider,
            tokens_used=response.tokens_used["total"],
            cost_usd=response.cost_usd,
            trace_id=response.trace_id
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all providers"""
        results = {}
        
        for provider_type, gateway in self.gateways.items():
            try:
                results[provider_type.value] = await gateway.health_check()
            except Exception as e:
                results[provider_type.value] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "overall_status": "healthy" if all(
                r.get("status") == "healthy" for r in results.values()
            ) else "degraded",
            "providers": results
        }


# Global gateway instance for easy access
_gateway_instance = None

def get_llm_gateway() -> UnifiedLLMGateway:
    """Get global LLM gateway instance"""
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = UnifiedLLMGateway()
    return _gateway_instance