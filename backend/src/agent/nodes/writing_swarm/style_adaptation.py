"""
Style Adaptation Agent for HandyWriterz Writing Excellence Swarm.

This micro-agent adapts the writing style to different academic disciplines
and user preferences, creating a personalized writing experience.
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from src.agent.base import BaseNode
from ...handywriterz_state import HandyWriterzState

class StyleAdaptationAgent(BaseNode):
    """
    A specialized agent for adapting writing style.
    """

    def __init__(self):
        super().__init__(name="StyleAdaptationAgent")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7) # Higher temperature for more creative style adaptation

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the style adaptation process.
        """
        self.logger.info("Initiating writing style adaptation.")
        self._broadcast_progress(state, "Adapting writing style...")

        content_to_adapt = state.get("synthesized_research", "")
        if not content_to_adapt:
            return {"style_adaptation_analysis": {}}

        # In a real implementation, we would analyze the user's uploaded
        # documents to determine their writing style. For this example,
        # we'll use the user's prompt as a proxy for their style.
        user_style_proxy = state.get("messages", [{}])[-1].get("content", "")

        adapted_content = await self._adapt_style(content_to_adapt, user_style_proxy)

        self.logger.info("Style adaptation complete.")
        self._broadcast_progress(state, "Completed style adaptation.")

        return {"adapted_content": adapted_content}

    async def _adapt_style(self, content: str, style_proxy: str) -> str:
        """
        Adapts the writing style of the content based on the user's style proxy.
        """
        prompt = f"""
        Please rewrite the following text to better match the writing style
        of the provided example. Pay attention to tone, sentence structure,
        and vocabulary.

        Example of desired style:
        "{style_proxy}"

        Text to adapt:
        "{content}"

        Return only the adapted text.
        """
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            self.logger.error(f"LLM call failed during style adaptation: {e}")
            return content # Return original content on failure

style_adaptation_agent_node = StyleAdaptationAgent()
