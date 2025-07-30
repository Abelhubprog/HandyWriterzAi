"""
Bias Detection Agent for HandyWriterz QA Swarm.

This micro-agent identifies and flags potential biases in the generated
content, ensuring fairness and academic integrity.
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from ...base import BaseNode
from ...handywriterz_state import HandyWriterzState

class BiasDetectionAgent(BaseNode):
    """
    A specialized agent for detecting and analyzing potential biases in text.
    """

    def __init__(self):
        super().__init__(name="BiasDetectionAgent")
        self.llm = None  # Initialize lazily

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the bias detection analysis.
        """
        self.logger.info("Initiating bias detection analysis.")
        self._broadcast_progress(state, "Analyzing content for potential biases...")

        # For this example, we'll assume the content to analyze is in the
        # 'synthesized_result' field from the research swarm.
        content_to_analyze = state.get("synthesized_result", "")
        if not content_to_analyze:
            return {"bias_analysis": {}}

        analysis = await self._analyze_content_for_bias(content_to_analyze)

        self.logger.info("Bias detection analysis complete.")
        self._broadcast_progress(state, "Completed bias detection analysis.")

        return {"bias_analysis": analysis}

    async def _analyze_content_for_bias(self, content: str) -> Dict[str, Any]:
        """
        Analyzes the content for potential biases using an LLM.
        """
        prompt = f"""
        Please analyze the following text for potential biases. Look for any
        language or framing that might be biased in terms of gender, race,
        political affiliation, or other sensitive attributes.

        Text to analyze:
        "{content}"

        Provide a structured analysis that includes:
        1.  A list of any potentially biased phrases or sentences.
        2.  For each identified issue, explain the nature of the potential bias.
        3.  Suggestions for rephrasing to be more neutral and objective.
        4.  An overall bias score from 0 (neutral) to 10 (highly biased).
        """
        try:
            response = await self.llm.ainvoke(prompt)
            # A more robust implementation would parse this into a Pydantic model.
            return {"analysis": response.content}
        except Exception as e:
            self.logger.error(f"LLM call failed during bias analysis: {e}")
            return {"analysis": "Could not perform bias analysis."}

bias_detection_agent_node = BiasDetectionAgent()
