"""
Perplexity Provider Implementation
Access to Perplexity's research-focused models
"""

import asyncio
from typing import List, Optional, AsyncGenerator
from openai import AsyncOpenAI

from .base import BaseProvider, ChatMessage, ChatResponse, ModelRole


class PerplexityProvider(BaseProvider):
    """Perplexity provider implementation - research-focused AI"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        # Perplexity uses OpenAI-compatible API
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )

    @property
    def provider_name(self) -> str:
        return "perplexity"

    @property
    def available_models(self) -> List[str]:
        return [
            "llama-3.1-sonar-small-128k-online",
            "llama-3.1-sonar-large-128k-online",
            "llama-3.1-sonar-huge-128k-online",
            "llama-3.1-8b-instruct",
            "llama-3.1-70b-instruct",
            "mixtral-8x7b-instruct",
        ]

    def get_default_model(self, role: ModelRole = ModelRole.GENERAL) -> str:
        """Get the best Perplexity model for each role"""
        role_models = {
            ModelRole.JUDGE: "llama-3.1-sonar-large-128k-online",  # Research with reasoning
            ModelRole.LAWYER: "llama-3.1-sonar-large-128k-online",  # Legal research
            ModelRole.RESEARCHER: "llama-3.1-sonar-huge-128k-online",  # Best for research
            ModelRole.WRITER: "llama-3.1-70b-instruct",  # Writing without web search
            ModelRole.REVIEWER: "llama-3.1-sonar-large-128k-online",  # Research for review
            ModelRole.SUMMARIZER: "llama-3.1-sonar-small-128k-online",  # Fast research summaries
            ModelRole.GENERAL: "llama-3.1-sonar-large-128k-online"  # Good balance
        }
        return role_models.get(role, "llama-3.1-sonar-large-128k-online")

    def _convert_messages(self, messages: List[ChatMessage]) -> List[dict]:
        """Convert our standard messages to Perplexity format"""
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResponse:
        """Send chat messages to Perplexity and get response"""

        model_name = model or self.get_default_model()
        perplexity_messages = self._convert_messages(messages)

        try:
            # Prepare request parameters
            request_params = {
                "model": model_name,
                "messages": perplexity_messages,
                "temperature": temperature,
            }

            if max_tokens:
                request_params["max_tokens"] = max_tokens

            # Add any additional kwargs
            request_params.update(kwargs)

            # Make the API call
            response = await self.client.chat.completions.create(**request_params)

            # Extract usage information
            usage = {}
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }

            return ChatResponse(
                content=response.choices[0].message.content,
                model=model_name,
                provider=self.provider_name,
                usage=usage,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "response_id": response.id,
                    "has_web_search": "online" in model_name
                }
            )

        except Exception as e:
            raise Exception(f"Perplexity API error: {str(e)}")

    async def stream_chat(
        self,
        messages: List[ChatMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from Perplexity"""

        model_name = model or self.get_default_model()
        perplexity_messages = self._convert_messages(messages)

        try:
            # Prepare request parameters
            request_params = {
                "model": model_name,
                "messages": perplexity_messages,
                "temperature": temperature,
                "stream": True,
            }

            if max_tokens:
                request_params["max_tokens"] = max_tokens

            # Add any additional kwargs
            request_params.update(kwargs)

            # Stream the response
            async for chunk in await self.client.chat.completions.create(**request_params):
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise Exception(f"Perplexity streaming error: {str(e)}")
