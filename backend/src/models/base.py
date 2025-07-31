"""
Base Provider Interface for Multi-Provider AI Architecture
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum


class ModelRole(Enum):
    """Roles that different models can play in the system"""
    JUDGE = "judge"
    LAWYER = "lawyer"
    RESEARCHER = "researcher"
    WRITER = "writer"
    REVIEWER = "reviewer"
    SUMMARIZER = "summarizer"
    GENERAL = "general"


@dataclass
class ChatMessage:
    """Standardized message format across all providers"""
    role: str  # "user", "assistant", "system"
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatResponse:
    """Standardized response format across all providers"""
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseProvider(ABC):
    """
    Abstract base class for all AI providers.

    This ensures all providers have the same interface, making them
    pluggable and interchangeable.
    """

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider"""
        pass

    @property
    @abstractmethod
    def available_models(self) -> List[str]:
        """Return list of available models for this provider"""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResponse:
        """
        Send chat messages and get response.

        Args:
            messages: List of chat messages
            model: Model to use (provider-specific)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters

        Returns:
            ChatResponse with standardized format
        """
        pass

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[ChatMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response.

        Args:
            messages: List of chat messages
            model: Model to use (provider-specific)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters

        Yields:
            Chunks of response text
        """
        pass

    @abstractmethod
    def get_default_model(self, role: ModelRole = ModelRole.GENERAL) -> str:
        """
        Get the default model for a specific role.

        Args:
            role: The role this model will play

        Returns:
            Model identifier for this provider
        """
        pass

    def validate_config(self) -> bool:
        """
        Validate provider configuration.

        Returns:
            True if configuration is valid
        """
        return bool(self.api_key)

    async def health_check(self) -> bool:
        """
        Check if provider is healthy and accessible.

        Returns:
            True if provider is healthy
        """
        try:
            # Simple test message
            test_messages = [ChatMessage(role="user", content="Hello")]
            response = await self.chat(test_messages, max_tokens=10)
            return bool(response.content)
        except Exception:
            return False
