"""
Scholar Network Agent for HandyWriterz Research Swarm.

This micro-agent navigates and analyzes citation networks from Google Scholar,
providing insights into the academic landscape and influential papers.
"""

from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
# Mock scholarly for demo
class MockScholarly:
    def search_pubs(self, query):
        return [
            {
                'title': f'AI Applications in Cancer Treatment: {query}',
                'year': 2023,
                'authors': ['Dr. AI Research', 'Prof. Cancer Study'],
                'citation_count': 150
            }
        ]
    
    def search_author(self, name):
        return {'name': name, 'publications': []}

scholarly = MockScholarly()

from src.agent.base import BaseNode, NodeError
from ...handywriterz_state import HandyWriterzState

class ScholarNetworkAgent(BaseNode):
    """
    A specialized agent for analyzing Google Scholar citation networks.
    """

    def __init__(self):
        super().__init__(name="ScholarNetworkAgent")
        # It's recommended to use a proxy to avoid getting blocked by Google.
        # For this implementation, we'll proceed without a proxy, but in a
        # production environment, this should be configured.
        # pg = ProxyGenerator()
        # scholarly.use_proxy(pg)

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the Google Scholar search and network analysis.
        """
        self.logger.info("Initiating Google Scholar network analysis.")
        self._broadcast_progress(state, "Analyzing citation networks on Google Scholar...")

        search_query = self._construct_query(state)
        if not search_query:
            raise NodeError("Could not construct a valid Google Scholar search query.", self.name)

        try:
            search_results = scholarly.search_pubs(search_query)
            # We'll analyze the first, most relevant result.
            first_result = next(search_results, None)
            if not first_result:
                return {"scholar_network_analysis": {}}

            # Fill the publication with more details, including citations
            publication = scholarly.fill(first_result)
        except Exception as e:
            raise NodeError(f"An error occurred during Google Scholar search: {e}", self.name)

        self.logger.info(f"Found and analyzed top publication: {publication['bib']['title']}")
        self._broadcast_progress(state, "Analyzed citation network of top publication.")

        processed_analysis = self._process_analysis(publication)

        return {"scholar_network_analysis": processed_analysis}

    def _construct_query(self, state: HandyWriterzState) -> str:
        """
        Constructs a search query for Google Scholar.
        """
        user_params = state.get("user_params", {})
        field = user_params.get("field", "")
        prompt = state.get("messages", [{}])[-1].get("content", "")

        if not field and not prompt:
            return ""

        return f"{field} {prompt}"

    def _process_analysis(self, publication: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes the publication data to extract network analysis.
        """
        return {
            "publication_title": publication["bib"]["title"],
            "authors": publication["bib"].get("author", []),
            "venue": publication["bib"].get("venue", ""),
            "year": publication["bib"].get("pub_year", ""),
            "abstract": publication["bib"].get("abstract", ""),
            "total_citations": publication.get("num_citations", 0),
            "cited_by_url": publication.get("citedby_url", ""),
            # The 'scholarly' library can also retrieve the list of citing publications,
            # but this can be slow and lead to getting blocked. For this example,
            # we'll stick to the metadata.
        }

scholar_network_agent_node = ScholarNetworkAgent()
