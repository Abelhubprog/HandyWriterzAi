"""
OpenAI Provider Implementation
"""

import asyncio
from typing import List, Optional, AsyncGenerator
from openai import AsyncOpenAI

from .base import BaseProvider, ChatMessage, ChatResponse, ModelRole


class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = AsyncOpenAI(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def available_models(self) -> List[str]:
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]

    def get_default_model(self, role: ModelRole = ModelRole.GENERAL) -> str:
        """Get the best OpenAI model for each role"""
        role_models = {
            ModelRole.JUDGE: "gpt-4o",  # Best reasoning for evaluation
            ModelRole.LAWYER: "gpt-4o",  # Complex legal reasoning
            ModelRole.RESEARCHER: "gpt-4o-mini",  # Fast research
            ModelRole.WRITER: "gpt-4o",  # Best for long-form writing
            ModelRole.REVIEWER: "gpt-4o",  # Detailed analysis
            ModelRole.SUMMARIZER: "gpt-4o-mini",  # Fast summarization
            ModelRole.GENERAL: "gpt-4o-mini"  # Good balance of speed/quality
        }
        return role_models.get(role, "gpt-4o-mini")

    def _convert_messages(self, messages: List[ChatMessage]) -> List[dict]:
        """Convert our standard messages to OpenAI format"""
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
        """Send chat messages to OpenAI and get response"""

        model_name = model or self.get_default_model()
        openai_messages = self._convert_messages(messages)

        try:
            # Prepare request parameters
            request_params = {
                "model": model_name,
                "messages": openai_messages,
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
                    "response_id": response.id
                }
            )

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def stream_chat(
        self,
        messages: List[ChatMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from OpenAI"""

        model_name = model or self.get_default_model()
        openai_messages = self._convert_messages(messages)

        try:
            # Prepare request parameters
            request_params = {
                "model": model_name,
                "messages": openai_messages,
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
            raise Exception(f"OpenAI streaming error: {str(e)}")
