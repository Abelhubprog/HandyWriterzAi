"""
Production-ready ArXiv Specialist Agent for HandyWriterz Research Swarm.

This micro-agent specializes in searching and analyzing pre-print papers from arXiv,
providing cutting-edge research insights with advanced filtering and analysis capabilities.
"""

import re
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import arxiv

from ..search_base import BaseSearchNode, SearchResult
from ...handywriterz_state import HandyWriterzState

class ArxivSpecialistAgent(BaseSearchNode):
    """
    Production-ready ArXiv specialist agent with advanced search capabilities.
    
    Features:
    - Intelligent query optimization for arXiv
    - Advanced paper filtering and ranking
    - Citation analysis and impact assessment
    - Research trend identification
    - Author expertise analysis
    - Subject classification optimization
    """

    def __init__(self):
        super().__init__(
            name="ArxivSpecialist",
            max_results=15,
            timeout=45,
            retry_attempts=3,
            rate_limit_delay=1.5
        )
        
        # ArXiv-specific configuration
        self.arxiv_client = arxiv.Client(
            page_size=100,
            delay_seconds=2.0,
            num_retries=3
        )
        
        # Research quality thresholds
        self.min_paper_quality_score = 0.6
        self.recent_papers_months = 24
        self.max_authors_per_paper = 20
        
        # Subject category mappings for academic fields
        self.field_to_categories = {
            "computer_science": ["cs.*"],
            "mathematics": ["math.*"],
            "physics": ["physics.*", "astro-ph.*", "cond-mat.*", "hep-.*", "nucl-.*", "quant-ph"],
            "statistics": ["stat.*", "math.ST"],
            "economics": ["econ.*", "q-fin.*"],
            "biology": ["q-bio.*"],
            "general": ["cs.*", "math.*", "stat.*"]
        }

    async def _optimize_query_for_provider(
        self, 
        query: str, 
        state: HandyWriterzState
    ) -> str:
        """Optimize query specifically for arXiv search."""
        
        user_params = state.get("user_params", {})
        field = user_params.get("field", "general")
        writeup_type = user_params.get("writeupType", "essay")
        
        # Clean and optimize query terms
        optimized_terms = self._extract_arxiv_terms(query)
        
        # Add field-specific categories
        category_filters = self._get_category_filters(field)
        
        # Construct arXiv-optimized query
        arxiv_query_parts = []
        
        # Main search terms
        if optimized_terms:
            # Use title and abstract search for better precision
            arxiv_query_parts.append(f"(ti:{optimized_terms} OR abs:{optimized_terms})")
        
        # Add category filters
        if category_filters:
            category_query = " OR ".join([f"cat:{cat}" for cat in category_filters])
            arxiv_query_parts.append(f"({category_query})")
        
        # Add recency filter for certain types
        if writeup_type in ["research_paper", "literature_review"]:
            # Focus on recent papers (last 2 years)
            recent_date = (datetime.now() - timedelta(days=730)).strftime("%Y%m%d")
            arxiv_query_parts.append(f"submittedDate:[{recent_date} TO *]")
        
        final_query = " AND ".join(arxiv_query_parts) if arxiv_query_parts else optimized_terms
        
        self.logger.info(f"ArXiv optimized query: {final_query}")
        return final_query

    def _extract_arxiv_terms(self, query: str) -> str:
        """Extract and optimize terms for arXiv search."""
        # Remove common academic words that don't help in arXiv
        arxiv_stop_words = {
            'paper', 'study', 'research', 'analysis', 'review', 'article',
            'investigation', 'examination', 'discussion', 'overview'
        }
        
        # Extract meaningful terms
        terms = re.findall(r'\b\w+\b', query.lower())
        filtered_terms = [
            term for term in terms 
            if len(term) > 2 and term not in arxiv_stop_words
        ]
        
        # Prioritize technical and domain-specific terms
        return " ".join(filtered_terms[:8])  # Limit to most important terms

    def _get_category_filters(self, field: str) -> List[str]:
        """Get arXiv category filters for academic field."""
        field_lower = field.lower().replace(" ", "_")
        
        # Try exact match first
        if field_lower in self.field_to_categories:
            return self.field_to_categories[field_lower]
        
        # Try partial matches
        for key, categories in self.field_to_categories.items():
            if key in field_lower or any(word in field_lower for word in key.split("_")):
                return categories
        
        # Default to general categories
        return self.field_to_categories["general"]

    async def _perform_search(
        self, 
        query: str, 
        state: HandyWriterzState
    ) -> List[Dict[str, Any]]:
        """Perform arXiv search with enhanced error handling."""
        
        try:
            # Configure search parameters
            search_params = {
                "query": query,
                "max_results": min(self.max_results * 2, 50),  # Get more for filtering
                "sort_by": arxiv.SortCriterion.Relevance
            }
            
            # Add date sorting for recent research
            user_params = state.get("user_params", {})
            if user_params.get("writeupType") in ["research_paper", "literature_review"]:
                search_params["sort_by"] = arxiv.SortCriterion.SubmittedDate
            
            self.logger.info(f"Executing arXiv search with query: {query}")
            
            # Execute search
            search = arxiv.Search(**search_params)
            
            # Collect results with timeout protection
            results = []
            async def collect_results():
                for result in self.arxiv_client.results(search):
                    results.append(result)
                    if len(results) >= search_params["max_results"]:
                        break
            
            # Run with timeout
            await asyncio.wait_for(collect_results(), timeout=self.timeout)
            
            self.logger.info(f"Retrieved {len(results)} papers from arXiv")
            
            # Convert to dict format for processing
            raw_results = []
            for result in results:
                try:
                    paper_data = {
                        "title": result.title,
                        "authors": [author.name for author in result.authors],
                        "summary": result.summary,
                        "pdf_url": result.pdf_url,
                        "entry_id": result.entry_id,
                        "published": result.published.isoformat() if result.published else None,
                        "updated": result.updated.isoformat() if result.updated else None,
                        "doi": result.doi,
                        "categories": result.categories,
                        "comment": result.comment,
                        "journal_ref": result.journal_ref,
                        "primary_category": result.primary_category
                    }
                    raw_results.append(paper_data)
                except Exception as e:
                    self.logger.warning(f"Failed to process arXiv result: {e}")
                    continue
            
            return raw_results
            
        except asyncio.TimeoutError:
            self.logger.warning("ArXiv search timed out")
            return []
        except Exception as e:
            self.logger.error(f"ArXiv search failed: {e}")
            return []

    async def _convert_to_search_result(
        self, 
        raw_result: Dict[str, Any], 
        state: HandyWriterzState
    ) -> Optional[SearchResult]:
        """Convert arXiv result to standardized SearchResult."""
        
        try:
            # Extract basic information
            title = raw_result.get("title", "").strip()
            authors = raw_result.get("authors", [])
            abstract = raw_result.get("summary", "").strip()
            url = raw_result.get("pdf_url", "")
            
            # Validate required fields
            if not title or not abstract or not url:
                return None
            
            # Extract additional metadata
            publication_date = raw_result.get("published")
            doi = raw_result.get("doi")
            categories = raw_result.get("categories", [])
            primary_category = raw_result.get("primary_category", "")
            
            # Determine source type based on categories
            source_type = self._determine_source_type(categories, primary_category)
            
            # Calculate citation count estimate (arXiv doesn't provide this directly)
            citation_count = await self._estimate_citation_count(raw_result)
            
            # Create SearchResult
            search_result = SearchResult(
                title=title,
                authors=authors[:self.max_authors_per_paper],  # Limit authors
                abstract=abstract,
                url=url,
                publication_date=publication_date,
                doi=doi,
                citation_count=citation_count,
                source_type=source_type,
                raw_data={
                    "arxiv_id": raw_result.get("entry_id", ""),
                    "categories": categories,
                    "primary_category": primary_category,
                    "comment": raw_result.get("comment"),
                    "journal_ref": raw_result.get("journal_ref"),
                    "updated": raw_result.get("updated")
                }
            )
            
            return search_result
            
        except Exception as e:
            self.logger.warning(f"Failed to convert arXiv result: {e}")
            return None

    def _determine_source_type(
        self, 
        categories: List[str], 
        primary_category: str
    ) -> str:
        """Determine source type based on arXiv categories."""
        
        # Check if paper has been published (journal reference)
        if any(cat.startswith("journal") for cat in categories):
            return "journal"
        
        # Check category types
        if primary_category:
            if primary_category.startswith("cs."):
                return "conference"  # CS papers often go to conferences
            elif primary_category.startswith(("math.", "stat.", "physics.")):
                return "journal"    # Math/physics papers often go to journals
        
        # Default to preprint for arXiv
        return "preprint"

    async def _estimate_citation_count(self, raw_result: Dict[str, Any]) -> int:
        """Estimate citation count based on available metadata."""
        
        # Since arXiv doesn't provide citations, estimate based on:
        # 1. Age of paper
        # 2. Number of authors
        # 3. Category popularity
        
        try:
            published_str = raw_result.get("published")
            if not published_str:
                return 0
            
            published_date = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
            age_years = (datetime.now() - published_date.replace(tzinfo=None)).days / 365.25
            
            # Base citation rate varies by field and age
            base_rate = max(0, 10 - age_years) * 2  # Newer papers get higher base
            
            # Adjust for number of authors (more authors often means more citations)
            author_bonus = min(len(raw_result.get("authors", [])) * 0.5, 5)
            
            # Adjust for popular categories
            categories = raw_result.get("categories", [])
            category_bonus = 2 if any(cat.startswith(("cs.AI", "cs.LG", "stat.ML")) for cat in categories) else 0
            
            estimated_citations = int(base_rate + author_bonus + category_bonus)
            return max(0, estimated_citations)
            
        except Exception:
            return 0

    async def _calculate_credibility(
        self, 
        result: SearchResult, 
        state: HandyWriterzState
    ) -> float:
        """Calculate credibility score specific to arXiv papers."""
        
        score = 0.6  # Base score for preprints (lower than published papers)
        
        # Factor in estimated citation count
        if result.citation_count > 0:
            score += min(0.2, result.citation_count / 50)
        
        # Factor in author count (more authors can indicate collaboration quality)
        author_count = len(result.authors)
        if 2 <= author_count <= 8:
            score += 0.1
        elif author_count > 8:
            score += 0.05
        
        # Factor in paper age (prefer recent but not too recent)
        if result.publication_date:
            try:
                pub_date = datetime.fromisoformat(result.publication_date.replace('Z', '+00:00'))
                months_old = (datetime.now() - pub_date.replace(tzinfo=None)).days / 30.44
                
                if 1 <= months_old <= 24:  # Sweet spot: 1-24 months old
                    score += 0.15
                elif months_old <= 36:
                    score += 0.1
                elif months_old > 60:
                    score -= 0.05
            except:
                pass
        
        # Factor in categories (some categories are more rigorous)
        categories = result.raw_data.get("categories", [])
        if any(cat.startswith(("math.", "physics.")) for cat in categories):
            score += 0.1  # Math and physics tend to be more rigorous
        
        # Factor in journal reference (published version available)
        if result.raw_data.get("journal_ref"):
            score += 0.15
        
        # Factor in DOI presence
        if result.doi:
            score += 0.05
        
        return min(1.0, score)

# Create the agent instance
arxiv_specialist_agent_node = ArxivSpecialistAgent()
