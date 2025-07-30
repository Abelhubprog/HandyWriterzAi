from typing import Dict, Any, List, Optional
from urllib.parse import quote
import httpx

from .search_base import BaseSearchNode, SearchResult
from ..handywriterz_state import HandyWriterzState

class SearchCrossRef(BaseSearchNode):
    """
    A search node that queries the CrossRef API for academic publications.
    """

    def __init__(self):
        super().__init__(
            name="SearchCrossRef",
            api_key=None,  # CrossRef API is public
            max_results=20,
            rate_limit_delay=0.5  # Be polite to the public API
        )

    async def _optimize_query_for_provider(self, query: str, state: HandyWriterzState) -> str:
        """
        Optimizes the search query for the CrossRef API.
        """
        # CrossRef works well with bibliographic queries
        return f"https://api.crossref.org/works?query.bibliographic={quote(query)}&rows={self.max_results}&sort=relevance"

    async def _perform_search(self, query: str, state: HandyWriterzState) -> List[Dict[str, Any]]:
        """
        Performs the actual search operation using the CrossRef API.
        """
        try:
            response = await self.client.get(query)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("items", [])
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error occurred during CrossRef search: {e}")
            return []
        except Exception as e:
            self.logger.error(f"An error occurred during CrossRef search: {e}")
            return []

    async def _convert_to_search_result(self, raw_result: Dict[str, Any], state: HandyWriterzState) -> Optional[SearchResult]:
        """
        Converts a raw result from the CrossRef API into a standardized SearchResult object.
        """
        try:
            title = raw_result.get("title", [None])[0]
            if not title:
                return None

            authors = [f"{author.get('given', '')} {author.get('family', '')}".strip() for author in raw_result.get("author", [])]
            
            # Extract publication date
            pub_date_parts = raw_result.get("published-print", {}).get("date-parts", [[]])[0]
            if not pub_date_parts:
                 pub_date_parts = raw_result.get("created", {}).get("date-parts", [[]])[0]
            
            publication_date = "-".join(map(str, pub_date_parts)) if pub_date_parts else None

            return SearchResult(
                title=title,
                authors=authors,
                abstract=raw_result.get("abstract", ""),
                url=raw_result.get("URL"),
                publication_date=publication_date,
                doi=raw_result.get("DOI"),
                citation_count=raw_result.get("is-referenced-by-count", 0),
                source_type="journal",  # CrossRef primarily has journal articles
                raw_data=raw_result
            )
        except Exception as e:
            self.logger.warning(f"Failed to convert CrossRef result: {e}")
            return None