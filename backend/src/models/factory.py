"""
Provider Factory for Multi-Provider AI Architecture
"""

import logging
from typing import Dict, Optional, List, Any
from enum import Enum

from .base import BaseProvider, ModelRole
from .gemini import GeminiProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .openrouter import OpenRouterProvider
from .perplexity import PerplexityProvider

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Available AI providers"""
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    PERPLEXITY = "perplexity"
    GROQ = "groq"  # Can be added later


class ProviderFactory:
    """
    Factory class for managing AI providers.

    Handles provider instantiation, configuration, and routing
    based on roles and availability.
    """

    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self._providers: Dict[str, BaseProvider] = {}
        self._role_mappings: Dict[ModelRole, str] = {}
        self._initialize_providers()
        self._setup_default_role_mappings()

    def _initialize_providers(self):
        """Initialize available providers based on API keys"""

        # Initialize Gemini
        if self.api_keys.get("gemini"):
            try:
                self._providers["gemini"] = GeminiProvider(self.api_keys["gemini"])
                logger.info("✅ Gemini provider initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini provider: {e}")

        # Initialize OpenAI
        if self.api_keys.get("openai"):
            try:
                self._providers["openai"] = OpenAIProvider(self.api_keys["openai"])
                logger.info("✅ OpenAI provider initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI provider: {e}")

        # Initialize Anthropic
        if self.api_keys.get("anthropic"):
            try:
                self._providers["anthropic"] = AnthropicProvider(self.api_keys["anthropic"])
                logger.info("✅ Anthropic provider initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Anthropic provider: {e}")

        # Initialize OpenRouter
        if self.api_keys.get("openrouter"):
            try:
                self._providers["openrouter"] = OpenRouterProvider(self.api_keys["openrouter"])
                logger.info("✅ OpenRouter provider initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenRouter provider: {e}")

        # Initialize Perplexity
        if self.api_keys.get("perplexity"):
            try:
                self._providers["perplexity"] = PerplexityProvider(self.api_keys["perplexity"])
                logger.info("✅ Perplexity provider initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Perplexity provider: {e}")

        logger.info(f"🔧 Initialized {len(self._providers)} AI providers: {list(self._providers.keys())}")

    def _setup_default_role_mappings(self):
        """Setup default provider mappings for each role"""

        # Priority order: Anthropic > OpenAI > Gemini
        available_providers = list(self._providers.keys())

        if not available_providers:
            logger.error("❌ No AI providers available!")
            return

        # Default role mappings based on provider strengths with new providers
        default_mappings = {
            ModelRole.JUDGE: ["anthropic", "openrouter", "openai", "gemini"],  # Best reasoning
            ModelRole.LAWYER: ["anthropic", "openrouter", "openai", "gemini"],  # Complex reasoning
            ModelRole.RESEARCHER: ["perplexity", "openrouter", "gemini", "openai"],  # Research with web access
            ModelRole.WRITER: ["anthropic", "openrouter", "openai", "gemini"],  # Best writing
            ModelRole.REVIEWER: ["openrouter", "anthropic", "openai", "gemini"],  # Access to specialized models
            ModelRole.SUMMARIZER: ["openai", "openrouter", "gemini", "anthropic"],  # Fast summarization
            ModelRole.GENERAL: ["openrouter", "anthropic", "gemini", "openai"]  # Access to Kimi K2, Qwen 3, GLM 4.5
        }

        # Assign first available provider for each role
        for role, preferred_providers in default_mappings.items():
            for provider in preferred_providers:
                if provider in available_providers:
                    self._role_mappings[role] = provider
                    break

        logger.info(f"🎯 Role mappings configured: {dict(self._role_mappings)}")

    def get_provider(self, provider_name: str = None, role: ModelRole = None) -> BaseProvider:
        """
        Get a provider instance.

        Args:
            provider_name: Specific provider to use
            role: Role-based provider selection

        Returns:
            Provider instance

        Raises:
            ValueError: If provider not available
        """

        # If specific provider requested
        if provider_name:
            if provider_name not in self._providers:
                available = list(self._providers.keys())
                raise ValueError(f"Provider '{provider_name}' not available. Available: {available}")
            return self._providers[provider_name]

        # If role-based selection
        if role:
            provider_name = self._role_mappings.get(role)
            if not provider_name:
                # Fallback to any available provider
                provider_name = next(iter(self._providers.keys()))
            return self._providers[provider_name]

        # Default: return first available provider
        if not self._providers:
            raise ValueError("No AI providers available")

        return next(iter(self._providers.values()))

    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return list(self._providers.keys())

    def get_role_mapping(self, role: ModelRole) -> Optional[str]:
        """Get the provider assigned to a specific role"""
        return self._role_mappings.get(role)

    def set_role_mapping(self, role: ModelRole, provider_name: str):
        """
        Set provider for a specific role.

        Args:
            role: The role to map
            provider_name: Provider to assign to this role

        Raises:
            ValueError: If provider not available
        """
        if provider_name not in self._providers:
            available = list(self._providers.keys())
            raise ValueError(f"Provider '{provider_name}' not available. Available: {available}")

        self._role_mappings[role] = provider_name
        logger.info(f"🔄 Role mapping updated: {role.value} -> {provider_name}")

    async def health_check_all(self) -> Dict[str, bool]:
        """
        Check health of all providers.

        Returns:
            Dict mapping provider names to health status
        """
        health_status = {}

        for name, provider in self._providers.items():
            try:
                is_healthy = await provider.health_check()
                health_status[name] = is_healthy
                logger.info(f"🏥 {name} health check: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
            except Exception as e:
                health_status[name] = False
                logger.error(f"🏥 {name} health check failed: {e}")

        return health_status

    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics about providers and their configurations"""
        stats = {
            "total_providers": len(self._providers),
            "available_providers": list(self._providers.keys()),
            "role_mappings": {role.value: provider for role, provider in self._role_mappings.items()},
            "provider_models": {}
        }

        for name, provider in self._providers.items():
            stats["provider_models"][name] = {
                "available_models": provider.available_models,
                "default_models": {
                    role.value: provider.get_default_model(role)
                    for role in ModelRole
                }
            }

        return stats


# Global factory instance
_factory_instance: Optional[ProviderFactory] = None


def initialize_factory(api_keys: Dict[str, str]) -> ProviderFactory:
    """
    Initialize the global provider factory.

    Args:
        api_keys: Dictionary of provider API keys

    Returns:
        ProviderFactory instance
    """
    global _factory_instance
    _factory_instance = ProviderFactory(api_keys)
    return _factory_instance


def get_provider(provider_name: str = None, role: ModelRole = None) -> BaseProvider:
    """
    Get a provider instance from the global factory.

    Args:
        provider_name: Specific provider to use
        role: Role-based provider selection

    Returns:
        Provider instance

    Raises:
        RuntimeError: If factory not initialized
        ValueError: If provider not available
    """
    if _factory_instance is None:
        raise RuntimeError("Provider factory not initialized. Call initialize_factory() first.")

    return _factory_instance.get_provider(provider_name, role)


def get_factory() -> ProviderFactory:
    """
    Get the global factory instance.

    Returns:
        ProviderFactory instance

    Raises:
        RuntimeError: If factory not initialized
    """
    if _factory_instance is None:
        raise RuntimeError("Provider factory not initialized. Call initialize_factory() first.")

    return _factory_instance
