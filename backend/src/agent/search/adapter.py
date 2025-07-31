"""
Search Result Adapter Layer for HandyWriterzAI

Provides standardized conversion of heterogeneous search agent outputs
into consistent SearchResult dictionaries for downstream processing.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class SearchResult:
    """Standardized search result schema."""
    
    def __init__(
        self,
        title: str,
        authors: List[str],
        abstract: str,
        url: str,
        doi: Optional[str] = None,
        publication_date: Optional[str] = None,
        citation_count: Optional[int] = None,
        source_type: str = "web",
        credibility_score: float = 0.5,
        relevance_score: float = 0.5,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.url = url
        self.doi = doi
        self.publication_date = publication_date
        self.citation_count = citation_count
        self.source_type = source_type
        self.credibility_score = credibility_score
        self.relevance_score = relevance_score
        self.raw_data = raw_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "url": self.url,
            "doi": self.doi,
            "publication_date": self.publication_date,
            "citation_count": self.citation_count,
            "source_type": self.source_type,
            "credibility_score": self.credibility_score,
            "relevance_score": self.relevance_score,
            "raw_data": self.raw_data
        }


def to_search_results(agent_name: str, payload: Any) -> List[Dict[str, Any]]:
    """
    Convert agent-specific payload to standardized SearchResult list.
    
    Args:
        agent_name: Name of the search agent
        payload: Raw output from the search agent
        
    Returns:
        List of SearchResult dictionaries
    """
    try:
        if agent_name.lower() == "gemini":
            return _convert_gemini_results(payload)
        elif agent_name.lower() == "perplexity":
            return _convert_perplexity_results(payload)
        elif agent_name.lower() == "o3" or agent_name.lower() == "openai":
            return _convert_openai_results(payload)
        elif agent_name.lower() == "claude":
            return _convert_claude_results(payload)
        elif agent_name.lower() == "crossref":
            return _convert_crossref_results(payload)
        elif agent_name.lower() == "pmc":
            return _convert_pmc_results(payload)
        elif agent_name.lower() == "scholar":
            return _convert_scholar_results(payload)
        elif agent_name.lower() == "arxiv":
            return _convert_arxiv_results(payload)
        else:
            logger.warning(f"Unknown agent type: {agent_name}")
            return _convert_generic_results(payload)
    
    except Exception as e:
        logger.error(f"Failed to convert {agent_name} results: {e}")
        return []


def _convert_gemini_results(payload: Any) -> List[Dict[str, Any]]:
    """Convert Gemini search results."""
    results = []
    
    if not payload or not isinstance(payload, (dict, list)):
        return results
    
    # Handle different Gemini output formats
    sources = []
    if isinstance(payload, dict):
        # Check various possible keys
        sources = (
            payload.get("sources", []) or
            payload.get("search_results", []) or
            payload.get("results", []) or
            payload.get("citations", [])
        )
        
        # Handle nested structures
        if not sources and "data" in payload:
            data = payload["data"]
            if isinstance(data, dict):
                sources = data.get("sources", []) or data.get("results", [])
            elif isinstance(data, list):
                sources = data
    elif isinstance(payload, list):
        sources = payload
    
    for source in sources:
        if not isinstance(source, dict):
            continue
        
        # Extract standardized fields
        title = (
            source.get("title", "") or
            source.get("name", "") or
            source.get("heading", "") or
            "Untitled"
        )
        
        authors = _extract_authors(source.get("authors", []) or source.get("author", ""))
        
        abstract = (
            source.get("abstract", "") or
            source.get("summary", "") or
            source.get("snippet", "") or
            source.get("content", "")
        )[:500]  # Limit abstract length
        
        url = source.get("url", "") or source.get("link", "")
        
        doi = source.get("doi", "")
        
        publication_date = _normalize_date(
            source.get("publication_date") or
            source.get("published_date") or
            source.get("date") or
            source.get("year")
        )
        
        citation_count = _safe_int(source.get("citation_count") or source.get("citations"))
        
        # Determine source type
        source_type = _determine_source_type(url, title)
        
        # Calculate scores
        credibility_score = _calculate_credibility_score(source, source_type)
        relevance_score = float(source.get("relevance_score", 0.5))
        
        result = SearchResult(
            title=title,
            authors=authors,
            abstract=abstract,
            url=url,
            doi=doi,
            publication_date=publication_date,
            citation_count=citation_count,
            source_type=source_type,
            credibility_score=credibility_score,
            relevance_score=relevance_score,
            raw_data={"agent": "gemini", "original": source}
        )
        
        results.append(result.to_dict())
    
    return results


def _convert_perplexity_results(payload: Any) -> List[Dict[str, Any]]:
    """Convert Perplexity search results."""
    results = []
    
    if not payload or not isinstance(payload, dict):
        return results
    
    # Perplexity typically has 'sources' array
    sources = payload.get("sources", [])
    
    for source in sources:
        if not isinstance(source, dict):
            continue
        
        title = source.get("title", "Untitled")
        authors = _extract_authors(source.get("authors", []))
        abstract = source.get("snippet", "")[:500]
        url = source.get("url", "")
        
        # Perplexity specific fields
        credibility_scores = source.get("credibility_scores", {})
        credibility_score = float(credibility_scores.get("overall", 0.5))
        
        result = SearchResult(
            title=title,
            authors=authors,
            abstract=abstract,
            url=url,
            source_type=_determine_source_type(url, title),
            credibility_score=credibility_score,
            relevance_score=0.7,  # Perplexity results are generally relevant
            raw_data={"agent": "perplexity", "original": source}
        )
        
        results.append(result.to_dict())
    
    return results


def _convert_openai_results(payload: Any) -> List[Dict[str, Any]]:
    """Convert OpenAI/O3 search results."""
    results = []
    
    if not payload:
        return results
    
    # Handle different OpenAI output formats
    sources = []
    if isinstance(payload, dict):
        sources = (
            payload.get("sources", []) or
            payload.get("results", []) or
            payload.get("search_results", [])
        )
    elif isinstance(payload, list):
        sources = payload
    
    for source in sources:
        if not isinstance(source, dict):
            continue
        
        title = source.get("title", source.get("name", "Untitled"))
        authors = _extract_authors(source.get("authors", []))
        abstract = source.get("abstract", source.get("summary", ""))[:500]
        url = source.get("url", source.get("link", ""))
        
        result = SearchResult(
            title=title,
            authors=authors,
            abstract=abstract,
            url=url,
            source_type=_determine_source_type(url, title),
            credibility_score=0.6,  # Default for OpenAI results
            relevance_score=0.6,
            raw_data={"agent": "openai", "original": source}
        )
        
        results.append(result.to_dict())
    
    return results


def _convert_claude_results(payload: Any) -> List[Dict[str, Any]]:
    """Convert Claude search results."""
    results = []
    
    if not payload:
        return results
    
    # Claude typically returns structured content
    sources = []
    if isinstance(payload, dict):
        sources = payload.get("sources", []) or payload.get("citations", [])
    elif isinstance(payload, list):
        sources = payload
    
    for source in sources:
        if not isinstance(source, dict):
            continue
        
        title = source.get("title", "Untitled")
        authors = _extract_authors(source.get("authors", []))
        abstract = source.get("excerpt", source.get("summary", ""))[:500]
        url = source.get("url", "")
        
        result = SearchResult(
            title=title,
            authors=authors,
            abstract=abstract,
            url=url,
            source_type=_determine_source_type(url, title),
            credibility_score=0.7,  # Claude tends to find quality sources
            relevance_score=0.7,
            raw_data={"agent": "claude", "original": source}
        )
        
        results.append(result.to_dict())
    
    return results


def _convert_crossref_results(payload: Any) -> List[Dict[str, Any]]:
    """Convert CrossRef search results."""
    results = []
    
    if not payload or not isinstance(payload, dict):
        return results
    
    # CrossRef has specific structure
    items = payload.get("message", {}).get("items", [])
    
    for item in items:
        if not isinstance(item, dict):
            continue
        
        title = ""
        if "title" in item and item["title"]:
            title = item["title"][0] if isinstance(item["title"], list) else str(item["title"])
        
        # Extract authors from CrossRef format
        authors = []
        if "author" in item:
            for author in item["author"]:
                if isinstance(author, dict):
                    given = author.get("given", "")
                    family = author.get("family", "")
                    if given and family:
                        authors.append(f"{given} {family}")
                    elif family:
                        authors.append(family)
        
        abstract = item.get("abstract", "")
        url = item.get("URL", "")
        doi = item.get("DOI", "")
        
        # Extract publication date
        pub_date = None
        if "published-print" in item:
            date_parts = item["published-print"].get("date-parts", [[]])[0]
            if date_parts:
                pub_date = f"{date_parts[0]}" + (f"-{date_parts[1]:02d}" if len(date_parts) > 1 else "")
        
        citation_count = item.get("is-referenced-by-count", 0)
        
        result = SearchResult(
            title=title,
            authors=authors,
            abstract=abstract,
            url=url,
            doi=doi,
            publication_date=pub_date,
            citation_count=citation_count,
            source_type="journal",
            credibility_score=0.9,  # CrossRef is highly credible
            relevance_score=0.8,
            raw_data={"agent": "crossref", "original": item}
        )
        
        results.append(result.to_dict())
    
    return results


def _convert_pmc_results(payload: Any) -> List[Dict[str, Any]]:
    """Convert PubMed Central search results."""
    results = []
    
    if not payload:
        return results
    
    # PMC typically has articles array
    articles = []
    if isinstance(payload, dict):
        articles = payload.get("articles", []) or payload.get("results", [])
    elif isinstance(payload, list):
        articles = payload
    
    for article in articles:
        if not isinstance(article, dict):
            continue
        
        title = article.get("title", "Untitled")
        authors = _extract_authors(article.get("authors", []))
        abstract = article.get("abstract", "")[:500]
        
        # PMC specific URL construction
        pmcid = article.get("pmcid", "")
        url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/" if pmcid else ""
        
        doi = article.get("doi", "")
        publication_date = article.get("pub_date", "")
        
        result = SearchResult(
            title=title,
            authors=authors,
            abstract=abstract,
            url=url,
            doi=doi,
            publication_date=publication_date,
            source_type="journal",
            credibility_score=0.95,  # PMC is very credible
            relevance_score=0.8,
            raw_data={"agent": "pmc", "original": article}
        )
        
        results.append(result.to_dict())
    
    return results


def _convert_scholar_results(payload: Any) -> List[Dict[str, Any]]:
    """Convert Google Scholar search results."""
    results = []
    
    if not payload:
        return results
    
    sources = []
    if isinstance(payload, dict):
        sources = payload.get("results", []) or payload.get("papers", [])
    elif isinstance(payload, list):
        sources = payload
    
    for source in sources:
        if not isinstance(source, dict):
            continue
        
        title = source.get("title", "Untitled")
        authors = _extract_authors(source.get("authors", []))
        abstract = source.get("snippet", source.get("abstract", ""))[:500]
        url = source.get("url", source.get("link", ""))
        
        citation_count = _safe_int(source.get("cited_by", 0))
        year = source.get("year", "")
        
        result = SearchResult(
            title=title,
            authors=authors,
            abstract=abstract,
            url=url,
            publication_date=str(year) if year else None,
            citation_count=citation_count,
            source_type="academic",
            credibility_score=0.8,  # Scholar results are generally credible
            relevance_score=0.7,
            raw_data={"agent": "scholar", "original": source}
        )
        
        results.append(result.to_dict())
    
    return results


def _convert_arxiv_results(payload: Any) -> List[Dict[str, Any]]:
    """Convert arXiv search results."""
    results = []
    
    if not payload:
        return results
    
    papers = []
    if isinstance(payload, dict):
        papers = payload.get("papers", []) or payload.get("results", [])
    elif isinstance(payload, list):
        papers = payload
    
    for paper in papers:
        if not isinstance(paper, dict):
            continue
        
        title = paper.get("title", "Untitled")
        authors = _extract_authors(paper.get("authors", []))
        abstract = paper.get("summary", paper.get("abstract", ""))[:500]
        
        # arXiv specific URL
        arxiv_id = paper.get("id", "")
        url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""
        
        publication_date = paper.get("published", "")
        
        result = SearchResult(
            title=title,
            authors=authors,
            abstract=abstract,
            url=url,
            publication_date=publication_date,
            source_type="preprint",
            credibility_score=0.7,  # arXiv is preprint, lower credibility
            relevance_score=0.8,   # But usually highly relevant
            raw_data={"agent": "arxiv", "original": paper}
        )
        
        results.append(result.to_dict())
    
    return results


def _convert_generic_results(payload: Any) -> List[Dict[str, Any]]:
    """Generic converter for unknown agent types."""
    results = []
    
    if not payload:
        return results
    
    # Try to extract data from common structures
    sources = []
    if isinstance(payload, dict):
        for key in ["sources", "results", "data", "items", "papers", "articles"]:
            if key in payload and isinstance(payload[key], list):
                sources = payload[key]
                break
    elif isinstance(payload, list):
        sources = payload
    
    for source in sources:
        if not isinstance(source, dict):
            continue
        
        # Extract common fields with fallbacks
        title = (
            source.get("title") or
            source.get("name") or
            source.get("heading") or
            "Untitled"
        )
        
        authors = _extract_authors(
            source.get("authors") or
            source.get("author") or
            []
        )
        
        abstract = (
            source.get("abstract") or
            source.get("summary") or
            source.get("snippet") or
            source.get("description") or
            ""
        )[:500]
        
        url = (
            source.get("url") or
            source.get("link") or
            source.get("href") or
            ""
        )
        
        result = SearchResult(
            title=title,
            authors=authors,
            abstract=abstract,
            url=url,
            source_type=_determine_source_type(url, title),
            credibility_score=0.5,  # Default credibility
            relevance_score=0.5,   # Default relevance
            raw_data={"agent": "generic", "original": source}
        )
        
        results.append(result.to_dict())
    
    return results


def _extract_authors(authors_data: Any) -> List[str]:
    """Extract author list from various formats."""
    if not authors_data:
        return []
    
    if isinstance(authors_data, str):
        # Handle comma-separated string
        return [author.strip() for author in authors_data.split(",") if author.strip()]
    
    if isinstance(authors_data, list):
        author_list = []
        for author in authors_data:
            if isinstance(author, str):
                author_list.append(author)
            elif isinstance(author, dict):
                # Handle structured author objects
                name = ""
                if "name" in author:
                    name = author["name"]
                elif "given" in author and "family" in author:
                    name = f"{author['given']} {author['family']}"
                elif "first" in author and "last" in author:
                    name = f"{author['first']} {author['last']}"
                
                if name:
                    author_list.append(name)
        
        return author_list
    
    return []


def _normalize_date(date_value: Any) -> Optional[str]:
    """Normalize publication date to YYYY-MM-DD format."""
    if not date_value:
        return None
    
    if isinstance(date_value, (int, float)):
        # Assume it's a year
        return str(int(date_value))
    
    if isinstance(date_value, str):
        # Try to extract year from string
        year_match = re.search(r'\b(19|20)\d{2}\b', date_value)
        if year_match:
            return year_match.group()
    
    return str(date_value)


def _safe_int(value: Any) -> Optional[int]:
    """Safely convert value to integer."""
    if value is None:
        return None
    
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def _determine_source_type(url: str, title: str) -> str:
    """Determine source type based on URL and title."""
    if not url:
        return "unknown"
    
    url_lower = url.lower()
    title_lower = title.lower()
    
    # Academic sources
    if any(domain in url_lower for domain in [
        "arxiv.org", "pubmed", "ncbi.nlm.nih.gov", "jstor.org",
        "ieee.org", "acm.org", "springer.com", "sciencedirect.com",
        "nature.com", "science.org", "plos.org"
    ]):
        return "journal"
    
    # Government sources
    if any(domain in url_lower for domain in [".gov", ".edu"]):
        return "government"
    
    # News sources
    if any(domain in url_lower for domain in [
        "news", "cnn.com", "bbc.com", "reuters.com", "ap.org"
    ]):
        return "news"
    
    # Preprint servers
    if any(domain in url_lower for domain in ["arxiv.org", "biorxiv.org", "medrxiv.org"]):
        return "preprint"
    
    # Default to web
    return "web"


def _calculate_credibility_score(source: Dict[str, Any], source_type: str) -> float:
    """Calculate credibility score based on source characteristics."""
    base_score = {
        "journal": 0.9,
        "government": 0.85,
        "preprint": 0.7,
        "academic": 0.8,
        "news": 0.6,
        "web": 0.4,
        "unknown": 0.3
    }.get(source_type, 0.5)
    
    # Adjust based on source characteristics
    if source.get("doi"):
        base_score += 0.1
    
    if source.get("citation_count", 0) > 10:
        base_score += 0.05
    
    if source.get("publication_date"):
        # Prefer recent sources
        try:
            year = int(str(source["publication_date"])[:4])
            current_year = datetime.now().year
            if current_year - year <= 5:
                base_score += 0.05
        except (ValueError, TypeError):
            pass
    
    return min(1.0, max(0.0, base_score))