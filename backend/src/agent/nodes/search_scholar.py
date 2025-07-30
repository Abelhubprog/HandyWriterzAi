import os
from typing import Dict, Any
from unpaywall import UnpaywallClient
from src.agent.base import BaseNode
from ...agent.handywriterz_state import HandyWriterzState

class ScholarSearchAgent(BaseNode):
    """An agent that searches for scholarly articles using the Unpaywall API."""

    def __init__(self):
        super().__init__("scholar_search")
        self.unpaywall_client = UnpaywallClient(os.getenv("UNPAYWALL_EMAIL"))

    async def execute(self, state: HandyWriterzState, config: dict) -> Dict[str, Any]:
        """
        Executes the scholar search agent.

        Args:
            state: The current state of the HandyWriterz workflow.
            config: The configuration for the agent.

        Returns:
            A dictionary containing the search results.
        """
        query = self._construct_query(state)
        self.logger.info(f"Executing scholar search with query: {query}")

        try:
            response = self.unpaywall_client.search(query=query, is_oa=True)
            
            results = []
            for article in response:
                results.append({
                    "doi": article.doi,
                    "title": article.title,
                    "authors": [author.get("given", "") + " " + author.get("family", "") for author in article.z_authors],
                    "journal_name": article.journal_name,
                    "published_date": article.published_date,
                    "pdf_url": article.best_oa_location.url_for_pdf if article.best_oa_location else None,
                })

            return {"scholar_articles": results}
        except Exception as e:
            self.logger.error(f"Scholar search error: {e}")
            return {"scholar_articles": [], "error_message": str(e)}

    def _construct_query(self, state: HandyWriterzState) -> str:
        """Constructs a scholar search query from the state."""
        # This is a simplified example. A more robust implementation would
        # use an LLM to generate the query based on the user's prompt.
        user_prompt = state.get("messages", [{}])[0].get("content", "")
        
        # Extract keywords from the prompt
        # This is a naive implementation and should be improved.
        keywords = ["Synthetic Embryo Models", "Regenerative Medicine", "UK/EU Regulatory Landscape", "Ethical Implications"]
        
        return " AND ".join(f'"{keyword}"' for keyword in keywords)
