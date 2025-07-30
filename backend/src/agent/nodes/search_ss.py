import os
from typing import Dict, Any, List, Optional
from urllib.parse import quote
import httpx

from .search_base import BaseSearchNode, SearchResult
from ..handywriterz_state import HandyWriterzState

class SearchSS(BaseSearchNode):
    """
    A search node that queries the Semantic Scholar API for academic papers.
    """

    def __init__(self):
        api_key = os.getenv("SEMANTIC_SCHOLAR_KEY")
        super().__init__(
            name="SearchSS",
            api_key=api_key,
            max_results=20,
            rate_limit_delay=0.5
        )
        if not api_key:
            self.logger.warning("SEMANTIC_SCHOLAR_KEY not found. Semantic Scholar search will be skipped.")

    async def _optimize_query_for_provider(self, query: str, state: HandyWriterzState) -> str:
        """
        Optimizes the search query for the Semantic Scholar API.
        """
        fields = "title,authors,year,journal,abstract,url,externalIds,citationCount"
        return f"https://api.semanticscholar.org/graph/v1/paper/search?query={quote(query)}&limit={self.max_results}&fields={fields}"

    async def _perform_search(self, query: str, state: HandyWriterzState) -> List[Dict[str, Any]]:
        """
        Performs the actual search operation using the Semantic Scholar API.
        """
        if not self.api_key:
            return []
            
        try:
            headers = {"x-api-key": self.api_key}
            response = await self.client.get(query, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error occurred during Semantic Scholar search: {e}")
            return []
        except Exception as e:
            self.logger.error(f"An error occurred during Semantic Scholar search: {e}")
            return []

    async def _convert_to_search_result(self, raw_result: Dict[str, Any], state: HandyWriterzState) -> Optional[SearchResult]:
        """
        Converts a raw result from the Semantic Scholar API into a standardized SearchResult object.
        """
        try:
            title = raw_result.get("title")
            if not title:
                return None

            authors = [author["name"] for author in raw_result.get("authors", [])]

            return SearchResult(
                title=title,
                authors=authors,
                abstract=raw_result.get("abstract", ""),
                url=raw_result.get("url"),
                publication_date=f"{raw_result.get('year')}-01-01" if raw_result.get('year') else None,
                doi=raw_result.get("externalIds", {}).get("DOI"),
                citation_count=raw_result.get("citationCount", 0),
                source_type="journal",  # Semantic Scholar is primarily journals
                raw_data=raw_result
            )
        except Exception as e:
            self.logger.warning(f"Failed to convert Semantic Scholar result: {e}")
            return None