"""
Ethical Reasoning Agent for HandyWriterz QA Swarm.

This micro-agent analyzes the ethical implications of the generated content,
ensuring the writing is responsible and ethically sound.
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from src.agent.base import BaseNode
from ...handywriterz_state import HandyWriterzState

class EthicalReasoningAgent(BaseNode):
    """
    A specialized agent for analyzing the ethical implications of text.
    """

    def __init__(self):
        super().__init__(name="EthicalReasoningAgent")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the ethical reasoning analysis.
        """
        self.logger.info("Initiating ethical reasoning analysis.")
        self._broadcast_progress(state, "Analyzing the ethical implications of the content...")

        content_to_analyze = state.get("synthesized_result", "")
        if not content_to_analyze:
            return {"ethical_reasoning_analysis": {}}

        analysis = await self._analyze_for_ethical_issues(content_to_analyze)

        self.logger.info("Ethical reasoning analysis complete.")
        self._broadcast_progress(state, "Completed ethical reasoning analysis.")

        return {"ethical_reasoning_analysis": analysis}

    async def _analyze_for_ethical_issues(self, content: str) -> Dict[str, Any]:
        """
        Analyzes the content for potential ethical issues using an LLM.
        """
        prompt = f"""
        Please analyze the following text for any potential ethical issues.
        Consider the following:
        - Does the text promote harmful stereotypes?
        - Does it use inflammatory or biased language?
        - Does it discuss sensitive topics without appropriate context or nuance?
        - Does it present opinions as facts?
        - Are there any other ethical concerns?

        Text to analyze:
        "{content}"

        Provide a structured analysis that includes:
        1.  A list of any identified ethical issues.
        2.  For each issue, an explanation of the ethical concern.
        3.  Suggestions for revision to address the ethical concerns.
        4.  An overall assessment of the ethical soundness of the text.
        """
        try:
            response = await self.llm.ainvoke(prompt)
            # A more robust implementation would parse this into a Pydantic model.
            return {"analysis": response.content}
        except Exception as e:
            self.logger.error(f"LLM call failed during ethical reasoning analysis: {e}")
            return {"analysis": "Could not perform ethical reasoning analysis."}

ethical_reasoning_agent_node = EthicalReasoningAgent()
