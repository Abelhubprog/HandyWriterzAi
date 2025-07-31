"""
Google Gemini Provider Implementation
"""

import asyncio
from typing import List, Optional, AsyncGenerator
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from .base import BaseProvider, ChatMessage, ChatResponse, ModelRole


class GeminiProvider(BaseProvider):
    """Google Gemini provider implementation"""

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        genai.configure(api_key=api_key)

        # Configure safety settings to be less restrictive for academic content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def available_models(self) -> List[str]:
        return [
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro"
        ]

    def get_default_model(self, role: ModelRole = ModelRole.GENERAL) -> str:
        """Get the best Gemini model for each role"""
        role_models = {
            ModelRole.JUDGE: "gemini-1.5-pro",  # Best reasoning for evaluation
            ModelRole.LAWYER: "gemini-1.5-pro",  # Complex legal reasoning
            ModelRole.RESEARCHER: "gemini-2.0-flash-exp",  # Fast research with search
            ModelRole.WRITER: "gemini-1.5-pro",  # Best for long-form writing
            ModelRole.REVIEWER: "gemini-1.5-pro",  # Detailed analysis
            ModelRole.SUMMARIZER: "gemini-1.5-flash",  # Fast summarization
            ModelRole.GENERAL: "gemini-2.0-flash-exp"  # Latest and fastest
        }
        return role_models.get(role, "gemini-2.0-flash-exp")

    def _convert_messages(self, messages: List[ChatMessage]) -> List[dict]:
        """Convert our standard messages to Gemini format"""
        gemini_messages = []

        for msg in messages:
            # Gemini uses 'user' and 'model' roles
            role = "model" if msg.role == "assistant" else msg.role
            if role == "system":
                # Gemini doesn't have system role, prepend to first user message
                continue

            gemini_messages.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })

        # Handle system messages by prepending to first user message
        system_content = ""
        for msg in messages:
            if msg.role == "system":
                system_content += f"{msg.content}\n\n"

        if system_content and gemini_messages:
            first_user_msg = next((msg for msg in gemini_messages if msg["role"] == "user"), None)
            if first_user_msg:
                first_user_msg["parts"][0]["text"] = system_content + first_user_msg["parts"][0]["text"]

        return gemini_messages

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatResponse:
        """Send chat messages to Gemini and get response"""

        model_name = model or self.get_default_model()
        gemini_messages = self._convert_messages(messages)

        try:
            # Configure the model
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
            }

            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            # Create model instance
            model_instance = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=self.safety_settings
            )

            # For single message, use generate_content
            if len(gemini_messages) == 1:
                response = await asyncio.to_thread(
                    model_instance.generate_content,
                    gemini_messages[0]["parts"][0]["text"]
                )
            else:
                # For conversation, use chat
                chat = model_instance.start_chat(history=gemini_messages[:-1])
                response = await asyncio.to_thread(
                    chat.send_message,
                    gemini_messages[-1]["parts"][0]["text"]
                )

            # Extract usage information if available
            usage = {}
            if hasattr(response, 'usage_metadata'):
                usage = {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0)
                }

            return ChatResponse(
                content=response.text,
                model=model_name,
                provider=self.provider_name,
                usage=usage,
                metadata={"safety_ratings": getattr(response, 'safety_ratings', [])}
            )

        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    async def stream_chat(
        self,
        messages: List[ChatMessage],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chat response from Gemini"""

        model_name = model or self.get_default_model()
        gemini_messages = self._convert_messages(messages)

        try:
            # Configure the model
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
            }

            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens

            # Create model instance
            model_instance = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                safety_settings=self.safety_settings
            )

            # Stream response
            if len(gemini_messages) == 1:
                response_stream = model_instance.generate_content(
                    gemini_messages[0]["parts"][0]["text"],
                    stream=True
                )
            else:
                chat = model_instance.start_chat(history=gemini_messages[:-1])
                response_stream = chat.send_message(
                    gemini_messages[-1]["parts"][0]["text"],
                    stream=True
                )

            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            raise Exception(f"Gemini streaming error: {str(e)}")
