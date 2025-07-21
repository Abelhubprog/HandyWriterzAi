"""
Academic Tone Agent for HandyWriterz Writing Excellence Swarm.

This micro-agent ensures that the generated content has an appropriate
academic tone, making it professional and suitable for an academic audience.
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from src.agent.base import BaseNode
from ...handywriterz_state import HandyWriterzState

class AcademicToneAgent(BaseNode):
    """
    A specialized agent for ensuring an academic tone in text.
    """

    def __init__(self):
        super().__init__(name="AcademicToneAgent")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the academic tone adjustment process.
        """
        self.logger.info("Initiating academic tone adjustment.")
        self._broadcast_progress(state, "Adjusting for academic tone...")

        content_to_adjust = state.get("enhanced_content", "")
        if not content_to_adjust:
            return {"academic_tone_analysis": {}}

        adjusted_content = await self._adjust_tone(content_to_adjust)

        self.logger.info("Academic tone adjustment complete.")
        self._broadcast_progress(state, "Completed academic tone adjustment.")

        return {"final_content": adjusted_content}

    async def _adjust_tone(self, content: str) -> str:
        """
        Adjusts the tone of the content to be more academic using an LLM.
        """
        prompt = f"""
        Please analyze the tone of the following text and rewrite it to have
        a more formal and objective academic tone. Consider the following:
        - Is there any informal language or slang?
        - Are there any overly subjective or emotional statements?
        - Is the tone appropriate for a formal academic paper?

        Text to analyze and rewrite:
        "{content}"

        Return only the rewritten text with an improved academic tone.
        """
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            self.logger.error(f"LLM call failed during academic tone adjustment: {e}")
            return content # Return original content on failure

academic_tone_agent_node = AcademicToneAgent()
