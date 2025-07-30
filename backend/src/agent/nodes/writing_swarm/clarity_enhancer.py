"""
Clarity Enhancer Agent for HandyWriterz Writing Excellence Swarm.

This micro-agent ensures that the generated content is clear, concise,
and easy to understand, improving the overall readability of the paper.
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from src.agent.base import BaseNode
from ...handywriterz_state import HandyWriterzState

class ClarityEnhancerAgent(BaseNode):
    """
    A specialized agent for enhancing the clarity of text.
    """

    def __init__(self):
        super().__init__(name="ClarityEnhancerAgent")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the clarity enhancement process.
        """
        self.logger.info("Initiating clarity enhancement.")
        self._broadcast_progress(state, "Enhancing content clarity...")

        content_to_enhance = state.get("optimized_content", "")
        if not content_to_enhance:
            return {"clarity_enhancement_analysis": {}}

        enhanced_content = await self._enhance_clarity(content_to_enhance)

        self.logger.info("Clarity enhancement complete.")
        self._broadcast_progress(state, "Completed clarity enhancement.")

        return {"enhanced_content": enhanced_content}

    async def _enhance_clarity(self, content: str) -> str:
        """
        Enhances the clarity of the content using an LLM.
        """
        prompt = f"""
        Please analyze the following text for clarity and rewrite it to be
        more clear, concise, and easy to understand. Consider the following:
        - Is there any jargon that could be replaced with simpler language?
        - Are there any convoluted sentences that could be simplified?
        - Is there any ambiguous language that could be clarified?

        Text to analyze and rewrite:
        "{content}"

        Return only the rewritten text with enhanced clarity.
        """
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            self.logger.error(f"LLM call failed during clarity enhancement: {e}")
            return content # Return original content on failure

clarity_enhancer_agent_node = ClarityEnhancerAgent()
