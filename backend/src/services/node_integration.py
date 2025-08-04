"""
Node Integration Layer for LangGraph compatibility with the new LLM Gateway.
Provides seamless integration without breaking existing agent nodes.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncIterator
from contextlib import asynccontextmanager

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks import CallbackManagerForLLMRun, BaseCallbackHandler
from langchain.schema import LLMResult

from .gateway import UnifiedLLMGateway, LLMRequest, get_llm_gateway
from .model_selector import ModelSelector, SelectionContext, SelectionStrategy, get_model_selector
from .model_policy import get_model_policy_registry
from ..services.budget import CostLevel
from ..config.settings import get_settings


logger = logging.getLogger(__name__)


class CapabilityAwareChatModel(BaseChatModel):
    """
    LangChain-compatible chat model that uses the new gateway system.
    Replaces direct provider instantiation in agent nodes.
    """
    
    def __init__(
        self,
        node_name: str,
        capabilities: List[str] = None,
        strategy: SelectionStrategy = SelectionStrategy.BALANCED,
        cost_tier_override: Optional[CostLevel] = None,
        trace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.node_name = node_name
        self.capabilities = capabilities or []
        self.strategy = strategy
        self.cost_tier_override = cost_tier_override
        self.trace_id = trace_id
        self.user_id = user_id
        
        # Initialize services
        self.gateway = get_llm_gateway()
        self.selector = get_model_selector()
        self.policy_registry = get_model_policy_registry()
        
        # Cache selected model to avoid re-selection on streaming
        self._cached_model = None
        self._cache_context = None
    
    @property
    def _llm_type(self) -> str:
        return "capability_aware_chat"
    
    def _convert_messages_to_dict(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """Convert LangChain messages to gateway format"""
        converted = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            elif isinstance(msg, SystemMessage):
                role = "system"
            else:
                role = "user"  # Default fallback
            
            converted.append({
                "role": role,
                "content": msg.content
            })
        
        return converted
    
    async def _select_model(self) -> Any:
        """Select appropriate model based on capabilities and context"""
        context = SelectionContext(
            node_name=self.node_name,
            capabilities=self.capabilities,
            user_id=self.user_id,
            cost_tier_override=self.cost_tier_override,
            strategy=self.strategy,
            trace_id=self.trace_id
        )
        
        # Check if we can reuse cached selection
        if (self._cached_model and 
            self._cache_context and 
            self._cache_context.node_name == context.node_name and
            self._cache_context.capabilities == context.capabilities):
            return self._cached_model
        
        # Select new model
        selection_result = await self.selector.select_model(context)
        
        self._cached_model = selection_result.selected_model
        self._cache_context = context
        
        logger.info(f"Selected model for {self.node_name}: {selection_result.selected_model.logical_id}")
        
        return selection_result.selected_model
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Async generation using the gateway"""
        
        try:
            # Select model
            model_spec = await self._select_model()
            
            # Convert messages
            gateway_messages = self._convert_messages_to_dict(messages)
            
            # Create request
            request = LLMRequest(
                messages=gateway_messages,
                model_spec=model_spec,
                node_name=self.node_name,
                trace_id=self.trace_id,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens"),
                capabilities=self.capabilities,
                user_id=self.user_id
            )
            
            # Execute via gateway
            response = await self.gateway.execute(request)
            
            # Record performance metrics
            await self.selector.record_model_performance(
                model_id=model_spec.logical_id,
                success=True,
                latency_ms=response.latency_ms,
                cost_usd=response.cost_usd,
                tokens_used=response.tokens_used["total"]
            )
            
            # Convert back to LangChain format
            ai_message = AIMessage(content=response.content)
            generation = ChatGeneration(
                message=ai_message,
                generation_info={
                    "model": response.model_used,
                    "provider": response.provider,
                    "tokens_used": response.tokens_used,
                    "cost_usd": response.cost_usd,
                    "trace_id": response.trace_id
                }
            )
            
            return ChatResult(generations=[generation])
            
        except Exception as e:
            logger.error(f"Generation failed for {self.node_name}: {e}")
            
            # Record failure
            if hasattr(self, '_cached_model') and self._cached_model:
                await self.selector.record_model_performance(
                    model_id=self._cached_model.logical_id,
                    success=False,
                    latency_ms=0,
                    cost_usd=0.0,
                    tokens_used=0
                )
            
            raise
    
    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGeneration]:
        """Async streaming using the gateway"""
        
        try:
            # Select model
            model_spec = await self._select_model()
            
            # Convert messages
            gateway_messages = self._convert_messages_to_dict(messages)
            
            # Create streaming request
            request = LLMRequest(
                messages=gateway_messages,
                model_spec=model_spec,
                node_name=self.node_name,
                trace_id=self.trace_id,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens"),
                stream=True,
                capabilities=self.capabilities,
                user_id=self.user_id
            )
            
            # Stream via gateway
            full_content = ""
            async for chunk in self.gateway.stream_execute(request):
                if chunk.get("type") == "content":
                    token = chunk.get("token", "")
                    full_content += token
                    
                    # Yield LangChain-compatible generation
                    ai_message = AIMessage(content=token)
                    yield ChatGeneration(
                        message=ai_message,
                        generation_info={
                            "model": chunk.get("model"),
                            "provider": chunk.get("provider"),
                            "streaming": True
                        }
                    )
                elif chunk.get("type") == "error":
                    logger.error(f"Streaming error: {chunk.get('error')}")
                    raise Exception(chunk.get("error"))
            
            # Record successful streaming
            await self.selector.record_model_performance(
                model_id=model_spec.logical_id,
                success=True,
                latency_ms=0,  # Streaming latency is harder to measure
                cost_usd=0.0,  # Cost calculation deferred
                tokens_used=len(full_content.split())  # Rough estimate
            )
            
        except Exception as e:
            logger.error(f"Streaming failed for {self.node_name}: {e}")
            
            # Record failure
            if hasattr(self, '_cached_model') and self._cached_model:
                await self.selector.record_model_performance(
                    model_id=self._cached_model.logical_id,
                    success=False,
                    latency_ms=0,
                    cost_usd=0.0,
                    tokens_used=0
                )
            
            raise


class NodeClientFactory:
    """
    Factory for creating LangChain-compatible clients for agent nodes.
    Replaces direct provider client instantiation.
    """
    
    def __init__(self):
        self.settings = get_settings()
    
    def create_client(
        self,
        node_name: str,
        capabilities: List[str] = None,
        strategy: SelectionStrategy = SelectionStrategy.BALANCED,
        **kwargs
    ) -> CapabilityAwareChatModel:
        """Create a capability-aware chat model for a node"""
        
        return CapabilityAwareChatModel(
            node_name=node_name,
            capabilities=capabilities or [],
            strategy=strategy,
            **kwargs
        )
    
    def create_writer_client(self, node_name: str = "writer", **kwargs) -> CapabilityAwareChatModel:
        """Create client optimized for writing tasks"""
        return self.create_client(
            node_name=node_name,
            capabilities=["streaming", "creative_writing", "long_context"],
            strategy=SelectionStrategy.BALANCED,
            **kwargs
        )
    
    def create_researcher_client(self, node_name: str = "researcher", **kwargs) -> CapabilityAwareChatModel:
        """Create client optimized for research tasks"""
        return self.create_client(
            node_name=node_name,
            capabilities=["web_search", "reasoning", "long_context"],
            strategy=SelectionStrategy.PERFORMANCE_OPTIMIZED,
            **kwargs
        )
    
    def create_evaluator_client(self, node_name: str = "evaluator", **kwargs) -> CapabilityAwareChatModel:
        """Create client optimized for evaluation tasks"""
        return self.create_client(
            node_name=node_name,
            capabilities=["reasoning", "function_calling"],
            strategy=SelectionStrategy.PERFORMANCE_OPTIMIZED,
            **kwargs
        )
    
    def create_formatter_client(self, node_name: str = "formatter", **kwargs) -> CapabilityAwareChatModel:
        """Create client optimized for formatting tasks"""
        return self.create_client(
            node_name=node_name,
            capabilities=["streaming", "function_calling"],
            strategy=SelectionStrategy.COST_OPTIMIZED,
            **kwargs
        )


class LegacyCompatibilityAdapter:
    """
    Compatibility adapter for existing nodes that use direct provider access.
    Allows gradual migration without breaking existing code.
    """
    
    def __init__(self):
        self.client_factory = NodeClientFactory()
        self.gateway = get_llm_gateway()
    
    async def get_model_client(self, agent_name: str, **kwargs) -> CapabilityAwareChatModel:
        """
        Drop-in replacement for existing get_model_client calls.
        Compatible with existing agent node patterns.
        """
        
        # Map common agent names to appropriate capabilities
        capability_mapping = {
            "writer": ["streaming", "creative_writing", "long_context"],
            "formatter": ["streaming", "function_calling"],
            "formatter_advanced": ["streaming", "function_calling"],
            "evaluator": ["reasoning", "function_calling"],
            "evaluator_advanced": ["reasoning", "function_calling"],
            "search_gemini": ["streaming", "web_search"],
            "search_perplexity": ["web_search", "reasoning"],
            "search_openai": ["function_calling", "reasoning"],
            "search_claude": ["reasoning", "function_calling"],
            "qa_evaluator": ["reasoning", "function_calling"],
            "citation_master": ["function_calling", "reasoning"],
            "academic_tone": ["creative_writing", "streaming"],
            "clarity_enhancer": ["creative_writing", "streaming"],
            "structure_optimizer": ["function_calling", "reasoning"]
        }
        
        capabilities = capability_mapping.get(agent_name, ["streaming"])
        
        return self.client_factory.create_client(
            node_name=agent_name,
            capabilities=capabilities,
            **kwargs
        )
    
    async def create_openai_client(self, model: str = None, **kwargs):
        """Legacy OpenAI client creation"""
        logger.warning("Using legacy OpenAI client - consider migrating to capability-aware client")
        return await self.get_model_client("legacy_openai", **kwargs)
    
    async def create_anthropic_client(self, model: str = None, **kwargs):
        """Legacy Anthropic client creation"""
        logger.warning("Using legacy Anthropic client - consider migrating to capability-aware client")
        return await self.get_model_client("legacy_anthropic", **kwargs)
    
    async def create_gemini_client(self, model: str = None, **kwargs):
        """Legacy Gemini client creation"""
        logger.warning("Using legacy Gemini client - consider migrating to capability-aware client")
        return await self.get_model_client("legacy_gemini", **kwargs)


# Integration helper for existing service layer
class ModelServiceIntegration:
    """
    Integration layer for existing model service patterns.
    Maintains compatibility with current llm_service.py patterns.
    """
    
    def __init__(self):
        self.adapter = LegacyCompatibilityAdapter()
        self.gateway = get_llm_gateway()
        self.selector = get_model_selector()
    
    async def get_model_client(self, agent_name: str, **kwargs):
        """Compatible with existing llm_service.get_model_client"""
        return await self.adapter.get_model_client(agent_name, **kwargs)
    
    async def chat_completion(
        self,
        agent_name: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """Direct chat completion compatible with existing patterns"""
        
        client = await self.get_model_client(agent_name, **kwargs)
        
        # Convert to LangChain messages
        langchain_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:
                langchain_messages.append(HumanMessage(content=content))
        
        # Execute
        result = await client._agenerate(langchain_messages, **kwargs)
        
        # Return in expected format
        return {
            "content": result.generations[0].message.content,
            "model": result.generations[0].generation_info.get("model"),
            "provider": result.generations[0].generation_info.get("provider"),
            "tokens_used": result.generations[0].generation_info.get("tokens_used", {}),
            "cost_usd": result.generations[0].generation_info.get("cost_usd", 0.0)
        }
    
    async def stream_completion(
        self,
        agent_name: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """Streaming completion compatible with existing patterns"""
        
        client = await self.get_model_client(agent_name, **kwargs)
        
        # Convert to LangChain messages
        langchain_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:
                langchain_messages.append(HumanMessage(content=content))
        
        # Stream
        async for generation in client._astream(langchain_messages, **kwargs):
            yield {
                "token": generation.message.content,
                "model": generation.generation_info.get("model"),
                "provider": generation.generation_info.get("provider"),
                "streaming": True
            }


# Global instances for easy access
_client_factory = None
_legacy_adapter = None
_model_service_integration = None

def get_node_client_factory() -> NodeClientFactory:
    """Get global node client factory"""
    global _client_factory
    if _client_factory is None:
        _client_factory = NodeClientFactory()
    return _client_factory

def get_legacy_adapter() -> LegacyCompatibilityAdapter:
    """Get legacy compatibility adapter"""
    global _legacy_adapter
    if _legacy_adapter is None:
        _legacy_adapter = LegacyCompatibilityAdapter()
    return _legacy_adapter

def get_model_service_integration() -> ModelServiceIntegration:
    """Get model service integration layer"""
    global _model_service_integration
    if _model_service_integration is None:
        _model_service_integration = ModelServiceIntegration()
    return _model_service_integration