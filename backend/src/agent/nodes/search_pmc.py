from typing import Dict, Any, List, Optional
from urllib.parse import quote
import httpx

from .search_base import BaseSearchNode, SearchResult
from ..handywriterz_state import HandyWriterzState

class SearchPMC(BaseSearchNode):
    """
    A search node that queries the Europe PMC API for biomedical and life sciences literature.
    """

    def __init__(self):
        super().__init__(
            name="SearchPMC",
            api_key=None,  # Europe PMC API is public
            max_results=25,
            rate_limit_delay=0.5
        )

    async def _optimize_query_for_provider(self, query: str, state: HandyWriterzState) -> str:
        """
        Optimizes the search query for the Europe PMC API.
        """
        return f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={quote(query)}&format=json&resultType=core&pageSize={self.max_results}"

    async def _perform_search(self, query: str, state: HandyWriterzState) -> List[Dict[str, Any]]:
        """
        Performs the actual search operation using the Europe PMC API.
        """
        try:
            response = await self.client.get(query)
            response.raise_for_status()
            data = response.json()
            return data.get("resultList", {}).get("result", [])
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error occurred during PMC search: {e}")
            return []
        except Exception as e:
            self.logger.error(f"An error occurred during PMC search: {e}")
            return []

    async def _convert_to_search_result(self, raw_result: Dict[str, Any], state: HandyWriterzState) -> Optional[SearchResult]:
        """
        Converts a raw result from the Europe PMC API into a standardized SearchResult object.
        """
        try:
            title = raw_result.get("title")
            if not title:
                return None

            # Authors are a single string, split them
            authors = [author.strip() for author in raw_result.get("authorString", "").split(",") if author.strip()]

            return SearchResult(
                title=title,
                authors=authors,
                abstract=raw_result.get("abstractText", ""),
                url=raw_result.get("fullTextUrlList", {}).get("fullTextUrl", [{}])[0].get("url"),
                publication_date=f"{raw_result.get('pubYear')}-01-01" if raw_result.get('pubYear') else None,
                doi=raw_result.get("doi"),
                citation_count=raw_result.get("citedByCount", 0),
                source_type="journal",  # PMC is primarily journals
                raw_data=raw_result
            )
        except Exception as e:
            self.logger.warning(f"Failed to convert PMC result: {e}")
            return None