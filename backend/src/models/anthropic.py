"""
Anthropic Claude Provider Implementation
"""

import asyncio
from typing import List, Optional, AsyncGenerator
from anthropic import AsyncAnthropic

from .base import BaseProvider, ChatMessage, ChatResponse, ModelRole


class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider implementation"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.client = AsyncAnthropic(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def available_models(self) -> List[str]:
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]

    def get_default_model(self, role: ModelRole = ModelRole.GENERAL) -> str:
        """Get the best Anthropic model for each role"""
        role_models = {
            ModelRole.JUDGE: "claude-3-5-sonnet-20241022",  # Best reasoning
            ModelRole.LAWYER: "claude-3-5-sonnet-20241022",  # Complex reasoning
            ModelRole.RESEARCHER: "claude-3-5-haiku-20241022",  # Fast research
            ModelRole.WRITER: "claude-3-5-sonnet-20241022",  # Best for writing
            ModelRole.REVIEWER: "claude-3-5-sonnet-20241022",  # Detailed analysis
            ModelRole.SUMMARIZER: "claude-3-5-haiku-20241022",  # Fast summarization
            ModelRole.GENERAL: "claude-3-5-sonnet-20241022"  # Best overall
        }
        return role_models.get(role, "claude-3-5-sonnet-20241022")

    def _convert_messages(self, messages: List[ChatMessage]) -> tuple:
        """Convert our standard messages to Anthropic format"""
        system_message = ""
        conversation_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message += f"{msg.content}\n\n"
            else:
                conversation_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        return system_message.strip(), conversation_messages

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResponse:
        """Send chat messages to Anthropic and get response"""

        model_name = model or self.get_default_model()
        system_message, conversation_messages = self._convert_messages(messages)

        try:
            # Prepare request parameters
            request_params = {
                "model": model_name,
                "messages": conversation_messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096,
            }

            if system_message:
                request_params["system"] = system_message

            # Add any additional kwargs
            request_params.update(kwargs)

            # Make the API call
            response = await self.client.messages.create(**request_params)

            # Extract usage information
            usage = {}
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                }

            return ChatResponse(
                content=response.content[0].text,
                model=model_name,
                provider=self.provider_name,
                usage=usage,
                metadata={
                    "stop_reason": response.stop_reason,
                    "response_id": response.id
                }
            )

        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    async def stream_chat(
        self,
        messages: List[ChatMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from Anthropic"""

        model_name = model or self.get_default_model()
        system_message, conversation_messages = self._convert_messages(messages)

        try:
            # Prepare request parameters
            request_params = {
                "model": model_name,
                "messages": conversation_messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096,
                "stream": True,
            }

            if system_message:
                request_params["system"] = system_message

            # Add any additional kwargs
            request_params.update(kwargs)

            # Stream the response
            async with self.client.messages.stream(**request_params) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            raise Exception(f"Anthropic streaming error: {str(e)}")
