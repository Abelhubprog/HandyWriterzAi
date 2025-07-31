from typing import Dict, Any, List, Optional, cast
from ..base import BaseNode
from .search_base import SearchResult

class AggregatorNode(BaseNode):
    """
    Aggregates and deduplicates search results from various sources.
    Production-safe: tolerant of partial shapes and missing fields.
    """

    def __init__(self):
        super().__init__("Aggregator", timeout_seconds=30.0, max_retries=1)

    async def execute(self, state: Dict[str, Any], config: Optional[dict] = None) -> Dict[str, Any]:
        """
        Aggregates search results from all search agents and removes duplicates.
        """
        self.logger.info("Aggregating and deduplicating search results...")
        raw_results: List[Dict[str, Any]] = cast(List[Dict[str, Any]], state.get("raw_search_results", []))

        if not raw_results:
            self.logger.warning("No search results to aggregate.")
            return {"aggregated_sources": []}

        # Deduplication Logic
        unique_sources: Dict[str, SearchResult] = {}
        seen_identifiers = set()

        for result_dict in raw_results:
            try:
                # Normalize minimal required fields with safe defaults
                normalized = {
                    "title": result_dict.get("title") or "",
                    "authors": result_dict.get("authors") or [],
                    "abstract": result_dict.get("abstract") or result_dict.get("snippet") or "",
                    "url": result_dict.get("url") or "",
                    "publication_date": result_dict.get("publication_date") or result_dict.get("published_date"),
                    "doi": result_dict.get("doi"),
                    "citation_count": int(result_dict.get("citation_count", 0) or 0),
                    "source_type": result_dict.get("source_type") or "unknown",
                    "credibility_score": float(result_dict.get("credibility_score", 0.5) or 0.5),
                    "relevance_score": float(result_dict.get("relevance_score", 0.5) or 0.5),
                    "raw_data": result_dict,
                }
                result = SearchResult(**normalized)
            except Exception as e:
                self.logger.debug(f"Skipping malformed search result: {e}")
                continue

            identifier = None
            if result.doi and result.doi not in seen_identifiers:
                identifier = result.doi
            elif result.url and result.url not in seen_identifiers:
                identifier = result.url
            else:
                author_str = "".join(sorted(result.authors or [])).lower()
                identifier = f"{(result.title or '').lower()}_{author_str}"

            if identifier not in seen_identifiers:
                unique_sources[identifier] = result
                seen_identifiers.add(identifier)
            else:
                # Potential future merge: choose higher credibility/relevance
                existing = unique_sources.get(identifier)
                if existing:
                    pick_new = (
                        (result.credibility_score + result.relevance_score)
                        > (existing.credibility_score + existing.relevance_score)
                    )
                    if pick_new:
                        unique_sources[identifier] = result

        aggregated_sources = [r.to_dict() for r in unique_sources.values()]
        self.logger.info(
            f"Aggregated {len(raw_results)} raw results into {len(aggregated_sources)} unique sources."
        )
        return {"aggregated_sources": aggregated_sources}
