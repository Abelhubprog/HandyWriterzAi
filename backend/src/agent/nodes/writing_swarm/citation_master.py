"""
Citation Master Agent for HandyWriterz Writing Excellence Swarm.

This micro-agent ensures that all claims in the text are properly cited
and that the citations are formatted according to the specified style.
"""

from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from src.agent.base import BaseNode
from ...handywriterz_state import HandyWriterzState
from src.tools.google_web_search import google_web_search

class CitationMasterAgent(BaseNode):
    """
    A specialized agent for managing citations.
    """

    def __init__(self):
        super().__init__(name="CitationMasterAgent")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the citation management process.
        """
        self.logger.info("Initiating citation management.")
        self._broadcast_progress(state, "Managing citations...")

        content_to_cite = state.get("adapted_content", "")
        if not content_to_cite:
            return {"citation_management_analysis": {}}

        claims_to_cite = await self._identify_claims_needing_citation(content_to_cite)
        if not claims_to_cite:
            return {"citation_management_analysis": {"status": "No claims need citation."}}

        cited_content = content_to_cite
        citations = []
        for claim in claims_to_cite:
            citation = await self._find_and_format_citation(claim, state)
            if citation:
                # This is a simplistic way to add a citation. A real implementation
                # would be more sophisticated.
                cited_content = cited_content.replace(claim, f"{claim} {citation['formatted_citation']}")
                citations.append(citation)

        self.logger.info("Citation management complete.")
        self._broadcast_progress(state, "Completed citation management.")

        return {"cited_content": cited_content, "citations": citations}

    async def _identify_claims_needing_citation(self, content: str) -> List[str]:
        """
        Identifies claims in the text that require a citation.
        """
        prompt = f"""
        Please identify the specific claims in the following text that
        require a citation. A claim that requires a citation is a statement
        of fact that is not common knowledge.

        Text to analyze:
        "{content}"

        Return a numbered list of the claims that need a citation.
        """
        try:
            response = await self.llm.ainvoke(prompt)
            return [line.strip() for line in response.content.split('\n') if line.strip()]
        except Exception as e:
            self.logger.error(f"LLM call failed during claim identification: {e}")
            return []

    async def _find_and_format_citation(self, claim: str, state: HandyWriterzState) -> Dict[str, Any]:
        """
        Finds a source for a claim and formats the citation.
        """
        self.logger.info(f"Finding citation for claim: {claim}")
        try:
            search_results = await google_web_search.ainvoke(claim)
            if not search_results:
                return None

            # For this example, we'll just use the first search result.
            # A real implementation would analyze the results more carefully.
            first_result = search_results[0]
            citation_style = state.get("user_params", {}).get("citation_style", "APA")

            # Use an LLM to format the citation.
            prompt = f"""
            Please format the following source information into a citation in the
            {citation_style} style.

            Source Information:
            Title: {first_result.get('title', '')}
            URL: {first_result.get('link', '')}
            Snippet: {first_result.get('snippet', '')}

            Return only the formatted citation.
            """
            response = await self.llm.ainvoke(prompt)
            return {
                "claim": claim,
                "source": first_result,
                "formatted_citation": response.content,
            }

        except Exception as e:
            self.logger.error(f"Error finding or formatting citation for '{claim}': {e}")
            return None

citation_master_agent_node = CitationMasterAgent()
