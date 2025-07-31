"""
Multi-Provider AI Model Architecture for HandyWriterz
Supports Gemini, OpenAI, Anthropic, OpenRouter, and Perplexity providers
"""

from .factory import get_provider, ModelProvider, ProviderFactory, initialize_factory
from .base import BaseProvider, ChatMessage, ChatResponse, ModelRole
from .openrouter import OpenRouterProvider
from .perplexity import PerplexityProvider

__all__ = [
    "get_provider",
    "ModelProvider",
    "BaseProvider",
    "ProviderFactory",
    "initialize_factory",
    "ChatMessage",
    "ChatResponse",
    "ModelRole",
    "OpenRouterProvider",
    "PerplexityProvider"
]
