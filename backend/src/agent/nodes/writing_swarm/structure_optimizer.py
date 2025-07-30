"""
Structure Optimizer Agent for HandyWriterz Writing Excellence Swarm.

This micro-agent ensures that the generated content is well-organized
and easy to follow, improving the overall structure of the academic paper.
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from src.agent.base import BaseNode
from ...handywriterz_state import HandyWriterzState

class StructureOptimizerAgent(BaseNode):
    """
    A specialized agent for optimizing the structure of text.
    """

    def __init__(self):
        super().__init__(name="StructureOptimizerAgent")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the structure optimization process.
        """
        self.logger.info("Initiating structure optimization.")
        self._broadcast_progress(state, "Optimizing content structure...")

        content_to_optimize = state.get("cited_content", "")
        if not content_to_optimize:
            return {"structure_optimization_analysis": {}}

        optimized_content = await self._optimize_structure(content_to_optimize)

        self.logger.info("Structure optimization complete.")
        self._broadcast_progress(state, "Completed structure optimization.")

        return {"optimized_content": optimized_content}

    async def _optimize_structure(self, content: str) -> str:
        """
        Optimizes the structure of the content using an LLM.
        """
        prompt = f"""
        Please analyze the structure of the following text and rewrite it
        to improve its organization and flow. Consider the following:
        - Is there a clear introduction, body, and conclusion?
        - Are the paragraphs well-organized and focused on a single idea?
        - Is there a logical flow of ideas between paragraphs?
        - Can the structure be improved to make the text more persuasive?

        Text to analyze and rewrite:
        "{content}"

        Return only the rewritten text with the improved structure.
        """
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            self.logger.error(f"LLM call failed during structure optimization: {e}")
            return content # Return original content on failure

structure_optimizer_agent_node = StructureOptimizerAgent()
