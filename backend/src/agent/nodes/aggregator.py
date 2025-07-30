from typing import Dict, Any, List
from ..base import BaseNode
from ..handywriterz_state import HandyWriterzState
from .search_base import SearchResult

class AggregatorNode(BaseNode):
    """
    An agent that aggregates and deduplicates search results from various sources.
    """

    def __init__(self):
        super().__init__("Aggregator")

    async def execute(self, state: HandyWriterzState, config: dict) -> Dict[str, Any]:
        """
        Aggregates search results from all search agents and removes duplicates.
        """
        self.logger.info("Aggregating and deduplicating search results...")
        
        raw_results = state.get("raw_search_results", [])
        
        if not raw_results:
            self.logger.warning("No search results to aggregate.")
            return {"aggregated_sources": []}

        # --- Deduplication Logic ---
        unique_sources: Dict[str, SearchResult] = {}
        seen_identifiers = set()

        for result_dict in raw_results:
            result = SearchResult(**result_dict)
            
            # Use DOI as the primary unique identifier
            if result.doi and result.doi not in seen_identifiers:
                identifier = result.doi
            # Fallback to URL if no DOI
            elif result.url and result.url not in seen_identifiers:
                identifier = result.url
            # If no unique identifier, use a combination of title and authors
            else:
                author_str = "".join(sorted(result.authors)).lower()
                identifier = f"{result.title.lower()}_{author_str}"

            if identifier not in seen_identifiers:
                unique_sources[identifier] = result
                seen_identifiers.add(identifier)
            else:
                # If we've seen this identifier before, we might want to merge
                # information, but for now, we'll just keep the first one.
                pass

        aggregated_sources = [result.to_dict() for result in unique_sources.values()]
        
        self.logger.info(f"Aggregated {len(raw_results)} raw results into {len(aggregated_sources)} unique sources.")

        return {"aggregated_sources": aggregated_sources}