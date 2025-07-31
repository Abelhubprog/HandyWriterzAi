"""
OpenRouter Provider Implementation
Access to multiple models through OpenRouter API
"""

import asyncio
from typing import List, Optional, AsyncGenerator
from openai import AsyncOpenAI

from .base import BaseProvider, ChatMessage, ChatResponse, ModelRole


class OpenRouterProvider(BaseProvider):
    """OpenRouter provider implementation - access to multiple models"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        # OpenRouter uses OpenAI-compatible API
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

    @property
    def provider_name(self) -> str:
        return "openrouter"

    @property
    def available_models(self) -> List[str]:
        return [
            # New high-performance models (valid OpenRouter IDs)
            "moonshot-v1-8k",                 # Kimi (Kimi K2 general)
            "qwen/qwen-2.5-72b-instruct",     # Qwen 2.5 72B Instruct (use qwen-3 if available on your org)
            "zhipuai/glm-4-5",                # GLM 4.5

            # Top tier models
            "anthropic/claude-3.5-sonnet",
            "openai/gpt-4o",
            "google/gemini-pro-1.5",
            "meta-llama/llama-3.1-405b-instruct",

            # Fast and efficient
            "anthropic/claude-3-haiku",
            "openai/gpt-4o-mini",
            "google/gemini-flash-1.5",
            "qwen/qwen-2.5-7b-instruct",

            # Specialized models
            "perplexity/llama-3.1-sonar-large-128k-online",
            "deepseek/deepseek-chat",
            "mistralai/mistral-large",
        ]

    def get_default_model(self, role: ModelRole = ModelRole.GENERAL) -> str:
        """Get the best OpenRouter model for each role"""
        role_models = {
            ModelRole.JUDGE: "anthropic/claude-3.5-sonnet",                         # Best reasoning
            ModelRole.LAWYER: "anthropic/claude-3.5-sonnet",                        # Complex legal reasoning
            ModelRole.RESEARCHER: "perplexity/llama-3.1-sonar-large-128k-online",   # Research with web access
            ModelRole.WRITER: "anthropic/claude-3.5-sonnet",                        # Best writing
            ModelRole.REVIEWER: "qwen/qwen-2.5-72b-instruct",                        # Detailed analysis
            ModelRole.SUMMARIZER: "openai/gpt-4o-mini",                              # Fast summarization
            ModelRole.GENERAL: "moonshot-v1-8k"                                      # Kimi - excellent general performance
        }
        return role_models.get(role, "moonshot-v1-8k")

    def _convert_messages(self, messages: List[ChatMessage]) -> List[dict]:
        """Convert our standard messages to OpenRouter format"""
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
        """Send chat messages to OpenRouter and get response"""

        model_name = model or self.get_default_model()
        openrouter_messages = self._convert_messages(messages)

        try:
            # Prepare request parameters
            request_params = {
                "model": model_name,
                "messages": openrouter_messages,
                "temperature": temperature,
            }

            if max_tokens:
                request_params["max_tokens"] = max_tokens

            # Add OpenRouter specific headers
            request_params.update({
                "extra_headers": {
                    "HTTP-Referer": "https://handywriterz.com",
                    "X-Title": "HandyWriterz AI Platform"
                }
            })

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
            raise Exception(f"OpenRouter API error: {str(e)}")

    async def stream_chat(
        self,
        messages: List[ChatMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from OpenRouter"""

        model_name = model or self.get_default_model()
        openrouter_messages = self._convert_messages(messages)

        try:
            # Prepare request parameters
            request_params = {
                "model": model_name,
                "messages": openrouter_messages,
                "temperature": temperature,
                "stream": True,
            }

            if max_tokens:
                request_params["max_tokens"] = max_tokens

            # Add OpenRouter specific headers
            request_params.update({
                "extra_headers": {
                    "HTTP-Referer": "https://handywriterz.com",
                    "X-Title": "HandyWriterz AI Platform"
                }
            })

            # Add any additional kwargs
            request_params.update(kwargs)

            # Stream the response
            async for chunk in await self.client.chat.completions.create(**request_params):
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise Exception(f"OpenRouter streaming error: {str(e)}")
