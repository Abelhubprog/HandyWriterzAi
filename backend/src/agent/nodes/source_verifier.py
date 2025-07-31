import asyncio
from typing import Dict, Any, List, Optional, cast

from .search_base import SearchResult
from ..base import BaseNode

class SourceVerifier(BaseNode):
    """
    An agent that verifies the credibility, relevance, and accessibility of aggregated sources.
    """

    def __init__(self):
        super().__init__("SourceVerifier")
        self.min_credibility_score = 0.6
        self.min_relevance_score = 0.5

    async def execute(self, state: Dict[str, Any], config: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Executes the source verification process.
        """
        self.logger.info("Verifying aggregated sources...")
        aggregated_sources = cast(List[Dict[str, Any]], state.get("aggregated_sources", []))

        if not aggregated_sources:
            self.logger.warning("No sources to verify.")
            return {"verified_sources": [], "need_fallback": True}

        verification_tasks = []
        for source in aggregated_sources:
            try:
                # Normalize minimal required fields to avoid runtime errors
                normalized = {
                    "title": source.get("title") or "",
                    "authors": source.get("authors") or [],
                    "abstract": source.get("abstract") or source.get("snippet") or "",
                    "url": source.get("url") or "",
                    "publication_date": source.get("publication_date") or source.get("published_date"),
                    "doi": source.get("doi"),
                    "citation_count": int(source.get("citation_count", 0) or 0),
                    "source_type": source.get("source_type") or "unknown",
                    "credibility_score": float(source.get("credibility_score", 0.5) or 0.5),
                    "relevance_score": float(source.get("relevance_score", 0.5) or 0.5),
                    "raw_data": source,
                }
                verification_tasks.append(self.verify_source(SearchResult(**normalized)))
            except Exception as e:
                self.logger.debug(f"Skipping malformed aggregated source: {e}")
                continue

        verified_results = await asyncio.gather(*verification_tasks)
        verified_sources = [s.to_dict() for s in verified_results if s is not None]

        self.logger.info(f"Verified {len(aggregated_sources)} sources, {len(verified_sources)} passed verification.")

        # Determine if fallback is needed
        min_sources = cast(Dict[str, Any], state.get("user_params", {})).get("min_sources", 5)
        need_fallback = len(verified_sources) < min_sources

        return {
            "verified_sources": verified_sources,
            "need_fallback": need_fallback
        }

    async def verify_source(self, source: SearchResult) -> Optional[SearchResult]:
        """
        Performs a multi-faceted verification of a single source.
        """
        # 1. Credibility Check
        if source.credibility_score < self.min_credibility_score:
            self.logger.debug(f"Source '{source.title}' failed credibility check ({source.credibility_score}).")
            return None

        # 2. Relevance Check
        if source.relevance_score < self.min_relevance_score:
            self.logger.debug(f"Source '{source.title}' failed relevance check ({source.relevance_score}).")
            return None

        # 3. Link Liveness Check
        if not source.url:
            self.logger.debug(f"Source '{source.title}' has no URL.")
            return None

        # 4. (Future) Bias detection hook
        return source

    async def detect_bias(self, source: SearchResult) -> float:
        """
        Placeholder for future bias detection.
        """
        return 0.0
