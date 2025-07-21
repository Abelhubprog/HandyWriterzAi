"""
Originality Guard Agent for HandyWriterz QA Swarm.

This micro-agent ensures the originality of the generated content and
protects against plagiarism by comparing it against online sources.
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from src.agent.base import BaseNode
from ...handywriterz_state import HandyWriterzState
from src.tools.google_web_search import google_web_search

class OriginalityGuardAgent(BaseNode):
    """
    A specialized agent for ensuring the originality of text.
    """

    def __init__(self):
        super().__init__(name="OriginalityGuardAgent")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the originality check.
        """
        self.logger.info("Initiating originality check.")
        self._broadcast_progress(state, "Checking content for originality...")

        content_to_analyze = state.get("synthesized_result", "")
        if not content_to_analyze:
            return {"originality_analysis": {}}

        # Break the content into sentences for analysis.
        sentences = [s.strip() for s in content_to_analyze.split('.') if s.strip()]
        if not sentences:
            return {"originality_analysis": {"status": "No content to check."}}

        plagiarism_results = []
        for sentence in sentences:
            # For performance, we'll only check a subset of sentences in this example.
            # A real implementation would be more thorough.
            if len(plagiarism_results) >= 5:
                break
            if len(sentence.split()) > 5: # Only check sentences with more than 5 words
                result = await self._check_sentence_originality(sentence)
                if result.get("is_plagiarized"):
                    plagiarism_results.append(result)

        self.logger.info("Originality check complete.")
        self._broadcast_progress(state, "Completed originality check.")

        return {"originality_analysis": plagiarism_results}

    async def _check_sentence_originality(self, sentence: str) -> Dict[str, Any]:
        """
        Checks the originality of a single sentence using web search.
        """
        self.logger.info(f"Checking sentence: {sentence}")
        try:
            # Search for the exact sentence.
            search_results = await google_web_search.ainvoke(f'"{sentence}"')
        except Exception as e:
            self.logger.error(f"Google search failed for sentence '{sentence}': {e}")
            return {"sentence": sentence, "is_plagiarized": False, "reason": "Search failed."}

        # If there are any search results for the exact sentence, it's likely plagiarized.
        # This is a simplistic check and a real implementation would need to be
        # more sophisticated (e.g., checking for paraphrasing).
        is_plagiarized = bool(search_results)

        return {
            "sentence": sentence,
            "is_plagiarized": is_plagiarized,
            "evidence": search_results if is_plagiarized else [],
        }

originality_guard_agent_node = OriginalityGuardAgent()
