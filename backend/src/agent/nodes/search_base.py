
"""
Production-ready base search node for HandyWriterz.
Provides robust foundation for all search implementations.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import httpx
from langchain_core.runnables import RunnableConfig

from ..base import BaseNode, NodeError
from ..handywriterz_state import HandyWriterzState
from src.utils.file_utils import get_file_summary
from .error_handling import (
    with_error_handling, RetryConfig, ErrorCategory, NodeErrorHandler
)

logger = logging.getLogger(__name__)


class SearchResult:
    """Standardized search result format across all search providers."""
    
    def __init__(
        self,
        title: str,
        authors: List[str],
        abstract: str,
        url: str,
        publication_date: Optional[str] = None,
        doi: Optional[str] = None,
        citation_count: int = 0,
        source_type: str = "unknown",
        credibility_score: float = 0.5,
        relevance_score: float = 0.5,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.url = url
        self.publication_date = publication_date
        self.doi = doi
        self.citation_count = citation_count
        self.source_type = source_type
        self.credibility_score = credibility_score
        self.relevance_score = relevance_score
        self.raw_data = raw_data or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "url": self.url,
            "publication_date": self.publication_date,
            "doi": self.doi,
            "citation_count": self.citation_count,
            "source_type": self.source_type,
            "credibility_score": self.credibility_score,
            "relevance_score": self.relevance_score,
            "raw_data": self.raw_data
        }


class BaseSearchNode(BaseNode, ABC):
    """
    Production-ready base class for all search nodes.
    Provides robust error handling, caching, and standardized interfaces.
    """
    
    def __init__(
        self,
        name: str,
        api_key: Optional[str] = None,
        max_results: int = 10,
        timeout: int = 30,
        retry_attempts: int = 3,
        rate_limit_delay: float = 1.0
    ):
        super().__init__(name=name)
        self.api_key = api_key
        self.max_results = max_results
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.rate_limit_delay = rate_limit_delay
        
        # HTTP client with proper configuration
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        
        # Rate limiting
        self._last_request_time = 0.0
        
    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute search with robust error handling and progress tracking."""
        
        self.logger.info(f"Starting {self.name} search")
        self._broadcast_progress(state, f"Initiating {self.name} search...")
        
        start_time = time.time()
        
        try:
            # Build search query from state
            query = await self._build_search_query(state)
            if not query:
                raise NodeError("Could not build search query from state", self.name)
            
            self.logger.info(f"Search query: {query}")
            self._broadcast_progress(state, f"Searching for: {query[:100]}...")
            
            # Execute search with retries
            results = await self._search_with_retries(query, state)
            
            # Process and validate results
            processed_results = await self._process_results(results, state)
            
            # Update state
            search_results = state.get("raw_search_results", [])
            search_results.extend([r.to_dict() for r in processed_results])
            
            duration = time.time() - start_time
            self.logger.info(
                f"{self.name} completed in {duration:.2f}s, found {len(processed_results)} results"
            )
            
            self._broadcast_progress(
                state, 
                f"Found {len(processed_results)} relevant sources from {self.name}"
            )
            
            return {
                "raw_search_results": search_results,
                f"{self.name.lower()}_results": [r.to_dict() for r in processed_results],
                f"{self.name.lower()}_metadata": {
                    "query": query,
                    "result_count": len(processed_results),
                    "search_duration": duration,
                    "provider": self.name
                }
            }
            
        except Exception as e:
            error_msg = f"{self.name} search failed: {str(e)}"
            self.logger.error(error_msg)
            self._broadcast_progress(state, f"⚠️ {self.name} search encountered issues")
            
            # Don't fail the entire workflow, return empty results
            return {
                "raw_search_results": state.get("raw_search_results", []),
                f"{self.name.lower()}_results": [],
                f"{self.name.lower()}_metadata": {
                    "error": error_msg,
                    "provider": self.name,
                    "search_duration": time.time() - start_time
                }
            }
    
    async def _build_search_query(self, state: HandyWriterzState) -> str:
        """Build search query from state parameters, including file context."""
        
        # Extract search parameters
        user_params = state.get("user_params", {})
        messages = state.get("messages", [])
        uploaded_files = state.get("uploaded_files", [])
        
        # Get the main topic/question
        topic = ""
        if messages:
            topic = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        
        # Get field and other parameters
        field = user_params.get("field", "")
        writeup_type = user_params.get("writeupType", "essay")
        
        # --- Integrate File Context ---
        file_context = ""
        if uploaded_files:
            file_summaries = [get_file_summary(file) for file in uploaded_files]
            file_context = " ".join(file_summaries)

        # Build intelligent query
        query_parts = []
        
        if topic:
            # Clean and extract key terms from topic
            topic_clean = self._extract_key_terms(topic)
            query_parts.append(topic_clean)

        if file_context:
            file_context_clean = self._extract_key_terms(file_context)
            query_parts.append(file_context_clean)
        
        if field and field != "general":
            query_parts.append(field)
        
        # Add academic context based on writeup type
        if writeup_type in ["research_paper", "dissertation", "thesis"]:
            query_parts.append("research academic study")
        elif writeup_type == "literature_review":
            query_parts.append("review systematic meta-analysis")
        
        query = " ".join(query_parts)
        
        # Apply provider-specific query optimization
        return await self._optimize_query_for_provider(query, state)
    
    def _extract_key_terms(self, text: str) -> str:
        """Extract key terms from text for search query."""
        import re
        
        # Remove common words and clean text
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'can',
            'write', 'essay', 'paper', 'about', 'discuss', 'analyze', 'examine'
        }
        
        # Extract words and filter
        words = re.findall(r'\b\w+\b', text.lower())
        key_terms = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Take most important terms (first part of query usually contains main topic)
        return " ".join(key_terms[:10])
    
    async def _search_with_retries(
        self, 
        query: str, 
        state: HandyWriterzState
    ) -> List[Dict[str, Any]]:
        """Execute search with retry logic and rate limiting."""
        
        for attempt in range(self.retry_attempts):
            try:
                # Rate limiting
                await self._apply_rate_limit()
                
                # Execute actual search
                results = await self._perform_search(query, state)
                
                if results:
                    return results
                
                if attempt < self.retry_attempts - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.warning(
                        f"{self.name} attempt {attempt + 1} failed, retrying in {wait_time}s"
                    )
                    await asyncio.sleep(wait_time)
                    
            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise
                
                wait_time = 2 ** attempt
                self.logger.warning(
                    f"{self.name} attempt {attempt + 1} error: {e}, retrying in {wait_time}s"
                )
                await asyncio.sleep(wait_time)
        
        return []
    
    async def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self._last_request_time = time.time()
    
    async def _process_results(
        self, 
        raw_results: List[Dict[str, Any]], 
        state: HandyWriterzState
    ) -> List[SearchResult]:
        """Process and standardize search results."""
        
        processed = []
        
        for result in raw_results[:self.max_results]:
            try:
                # Convert to standardized format
                search_result = await self._convert_to_search_result(result, state)
                
                if search_result:
                    # Calculate relevance and credibility scores
                    search_result.relevance_score = await self._calculate_relevance(
                        search_result, state
                    )
                    search_result.credibility_score = await self._calculate_credibility(
                        search_result, state
                    )
                    
                    processed.append(search_result)
                    
            except Exception as e:
                self.logger.warning(f"Failed to process result: {e}")
                continue
        
        # Sort by combined relevance and credibility
        processed.sort(
            key=lambda x: (x.relevance_score + x.credibility_score) / 2, 
            reverse=True
        )
        
        return processed
    
    async def _calculate_relevance(
        self, 
        result: SearchResult, 
        state: HandyWriterzState
    ) -> float:
        """Calculate relevance score for a search result."""
        
        score = 0.5  # Base score
        
        # Extract query terms from state
        user_params = state.get("user_params", {})
        messages = state.get("messages", [])
        
        query_terms = set()
        if messages:
            topic = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
            query_terms.update(self._extract_key_terms(topic).split())
        
        if user_params.get("field"):
            query_terms.add(user_params["field"].lower())
        
        # Check term matches in title and abstract
        title_lower = result.title.lower()
        abstract_lower = result.abstract.lower()
        
        title_matches = sum(1 for term in query_terms if term in title_lower)
        abstract_matches = sum(1 for term in query_terms if term in abstract_lower)
        
        if query_terms:
            title_score = title_matches / len(query_terms) * 0.6
            abstract_score = abstract_matches / len(query_terms) * 0.4
            score = min(1.0, title_score + abstract_score)
        
        return score
    
    async def _calculate_credibility(
        self, 
        result: SearchResult, 
        state: HandyWriterzState
    ) -> float:
        """Calculate credibility score for a search result."""
        
        score = 0.5  # Base score
        
        # Factor in citation count
        if result.citation_count > 0:
            score += min(0.3, result.citation_count / 100)
        
        # Factor in source type
        source_scores = {
            "journal": 0.9,
            "conference": 0.8,
            "book": 0.8,
            "preprint": 0.6,
            "web": 0.4,
            "unknown": 0.5
        }
        score = source_scores.get(result.source_type, 0.5)
        
        # Factor in DOI presence
        if result.doi:
            score += 0.1
        
        # Factor in publication date (prefer recent)
        if result.publication_date:
            try:
                from datetime import datetime
                pub_date = datetime.fromisoformat(result.publication_date.replace('Z', '+00:00'))
                years_old = (datetime.now().year - pub_date.year)
                if years_old <= 5:
                    score += 0.1
                elif years_old <= 10:
                    score += 0.05
            except:
                pass
        
        return min(1.0, score)
    
    # Abstract methods that subclasses must implement
    
    @abstractmethod
    async def _optimize_query_for_provider(
        self, 
        query: str, 
        state: HandyWriterzState
    ) -> str:
        """Optimize query for specific search provider."""
        pass
    
    @abstractmethod
    async def _perform_search(
        self, 
        query: str, 
        state: HandyWriterzState
    ) -> List[Dict[str, Any]]:
        """Perform the actual search operation."""
        pass
    
    @abstractmethod
    async def _convert_to_search_result(
        self, 
        raw_result: Dict[str, Any], 
        state: HandyWriterzState
    ) -> Optional[SearchResult]:
        """Convert provider-specific result to SearchResult."""
        pass
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
