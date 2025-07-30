"""
Argument Validation Agent for HandyWriterz QA Swarm.

This micro-agent analyzes the logical structure of arguments in the
generated content, ensuring the writing is logically sound and persuasive.
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from src.agent.base import BaseNode
from ...handywriterz_state import HandyWriterzState

class ArgumentValidationAgent(BaseNode):
    """
    A specialized agent for validating the logical structure of arguments.
    """

    def __init__(self):
        super().__init__(name="ArgumentValidationAgent")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the argument validation process.
        """
        self.logger.info("Initiating argument validation.")
        self._broadcast_progress(state, "Analyzing the logical structure of arguments...")

        content_to_analyze = state.get("synthesized_result", "")
        if not content_to_analyze:
            return {"argument_validation_analysis": {}}

        analysis = await self._analyze_arguments(content_to_analyze)

        self.logger.info("Argument validation complete.")
        self._broadcast_progress(state, "Completed argument validation.")

        return {"argument_validation_analysis": analysis}

    async def _analyze_arguments(self, content: str) -> Dict[str, Any]:
        """
        Analyzes the arguments in the text for logical soundness.
        """
        prompt = f"""
        Please analyze the logical structure of the arguments in the following text.
        Identify the main claims, the supporting evidence, and the underlying
        assumptions. Also, please identify any potential logical fallacies.

        Text to analyze:
        "{content}"

        Provide a structured analysis that includes:
        1.  A list of the main arguments.
        2.  For each argument, an analysis of its logical structure.
        3.  A list of any identified logical fallacies, with explanations.
        4.  An overall assessment of the logical soundness of the text.
        """
        try:
            response = await self.llm.ainvoke(prompt)
            # A more robust implementation would parse this into a Pydantic model.
            return {"analysis": response.content}
        except Exception as e:
            self.logger.error(f"LLM call failed during argument analysis: {e}")
            return {"analysis": "Could not perform argument analysis."}

argument_validation_agent_node = ArgumentValidationAgent()
