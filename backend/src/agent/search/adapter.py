"""
Enhanced Search Result Adapter Layer for HandyWriterzAI

Provides standardized conversion of heterogeneous search agent outputs
into consistent SearchResult dictionaries for downstream processing.
Includes comprehensive deduplication, credibility scoring, and quality filtering.
"""

import logging
import hashlib
import os
from typing import Dict, List, Any, Optional, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse
import re
import json

logger = logging.getLogger(__name__)

class SourceType(Enum):
    ACADEMIC = "academic"
    JOURNAL = "journal"
    CONFERENCE = "conference"
    PREPRINT = "preprint"
    THESIS = "thesis"
    BOOK = "book"
    REPORT = "report"
    NEWS = "news"
    WEB = "web"
    CODE = "code"
    DATASET = "dataset"
    PATENT = "patent"
    GOVERNMENT = "government"

class AccessType(Enum):
    OPEN = "open"
    SUBSCRIPTION = "subscription"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"

@dataclass
class SearchResult:
    """Enhanced standardized search result schema with comprehensive metadata."""
    
    # Core fields (required)
    title: str
    authors: List[str]
    abstract: str
    url: str
    
    # Identifiers
    doi: Optional[str] = None
    pmid: Optional[str] = None
    arxiv_id: Optional[str] = None
    isbn: Optional[str] = None
    
    # Publication metadata
    publication_date: Optional[str] = None
    publication_year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    
    # Quality metrics
    citation_count: Optional[int] = None
    h_index: Optional[int] = None
    impact_factor: Optional[float] = None
    
    # Computed scores
    source_type: SourceType = SourceType.WEB
    credibility_score: float = 0.5
    relevance_score: float = 0.5
    recency_score: float = 0.5
    composite_score: float = 0.5
    
    # Access and licensing
    access_type: AccessType = AccessType.UNKNOWN
    license: Optional[str] = None
    
    # Content metadata
    language: str = "en"
    keywords: List[str] = field(default_factory=list)
    subjects: List[str] = field(default_factory=list)
    
    # Provider information
    provider: str = ""
    search_query: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    # Processing metadata
    normalized_at: datetime = field(default_factory=datetime.utcnow)
    content_hash: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Generate content hash for deduplication
        content = f"{self.title}|{self.doi or ''}|{self.url}"
        self.content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Extract publication year if not set
        if not self.publication_year and self.publication_date:
            year_match = re.search(r'\b(19|20)\d{2}\b', self.publication_date)
            if year_match:
                self.publication_year = int(year_match.group())
        
        # Calculate recency score
        self.recency_score = self._calculate_recency_score()
        
        # Calculate composite score
        self.composite_score = (
            self.relevance_score * 0.4 +
            self.credibility_score * 0.4 +
            self.recency_score * 0.2
        )
    
    def _calculate_recency_score(self) -> float:
        """Calculate recency score based on publication date"""
        if not self.publication_year:
            return 0.3  # Neutral score for unknown dates
        
        current_year = datetime.now().year
        years_ago = current_year - self.publication_year
        
        if years_ago <= 1:
            return 1.0
        elif years_ago <= 3:
            return 0.8
        elif years_ago <= 5:
            return 0.6
        elif years_ago <= 10:
            return 0.4
        else:
            return max(0.1, 1.0 - (years_ago - 10) * 0.05)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format with enum serialization."""
        result = {
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "url": self.url,
            "doi": self.doi,
            "pmid": self.pmid,
            "arxiv_id": self.arxiv_id,
            "isbn": self.isbn,
            "publication_date": self.publication_date,
            "publication_year": self.publication_year,
            "journal": self.journal,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "citation_count": self.citation_count,
            "h_index": self.h_index,
            "impact_factor": self.impact_factor,
            "source_type": self.source_type.value,
            "credibility_score": self.credibility_score,
            "relevance_score": self.relevance_score,
            "recency_score": self.recency_score,
            "composite_score": self.composite_score,
            "access_type": self.access_type.value,
            "license": self.license,
            "language": self.language,
            "keywords": self.keywords,
            "subjects": self.subjects,
            "provider": self.provider,
            "search_query": self.search_query,
            "raw_data": self.raw_data,
            "normalized_at": self.normalized_at.isoformat(),
            "content_hash": self.content_hash
        }
        return result

class SearchResultNormalizer:
    """Enhanced search result normalizer with comprehensive deduplication and quality filtering"""
    
    def __init__(self):
        self.feature_flags = {
            "enhanced_deduplication": os.getenv("FEATURE_ENHANCED_DEDUPLICATION", "true").lower() == "true",
            "quality_filtering": os.getenv("FEATURE_QUALITY_FILTERING", "true").lower() == "true",
            "credibility_scoring": os.getenv("FEATURE_CREDIBILITY_SCORING", "true").lower() == "true",
        }
        
        # High-quality domain patterns for credibility scoring
        self.high_quality_domains = {
            # Top-tier journals
            "nature.com": 1.0,
            "science.org": 1.0,
            "cell.com": 1.0,
            "nejm.org": 1.0,
            "thelancet.com": 1.0,
            
            # Academic databases
            "pubmed.ncbi.nlm.nih.gov": 0.9,
            "scholar.google.com": 0.8,
            "arxiv.org": 0.7,
            "semanticscholar.org": 0.8,
            
            # Professional organizations
            "ieee.org": 0.9,
            "acm.org": 0.9,
            "aps.org": 0.9,
            
            # Publishers
            "springer.com": 0.8,
            "elsevier.com": 0.8,
            "wiley.com": 0.8,
            "sage.com": 0.7,
            
            # Government/institutional
            "nih.gov": 0.9,
            "cdc.gov": 0.9,
            "who.int": 0.9,
            "europa.eu": 0.8,
            
            # Preprint servers
            "biorxiv.org": 0.6,
            "medrxiv.org": 0.6,
            "chemrxiv.org": 0.6,
        }
    
    def normalize_results(self, agent_name: str, payload: Any, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Main entry point for result normalization with enhanced processing"""
        try:
            # Convert using provider-specific logic
            results = self._convert_by_provider(agent_name, payload, search_query)
            
            if self.feature_flags["enhanced_deduplication"]:
                results = self._deduplicate_results(results)
            
            if self.feature_flags["quality_filtering"]:
                results = self._filter_and_rank_results(results)
                
            logger.info(f"Normalized {len(results)} results from {agent_name}")
            return [r.to_dict() for r in results]
            
        except Exception as e:
            logger.error(f"Failed to normalize {agent_name} results: {e}")
            return []
    
    def _convert_by_provider(self, agent_name: str, payload: Any, search_query: Optional[str] = None) -> List[SearchResult]:
        """Convert results based on provider with enhanced SearchResult objects"""
        provider_map = {
            "gemini": self._convert_gemini_results,
            "perplexity": self._convert_perplexity_results,
            "openai": self._convert_openai_results,
            "o3": self._convert_openai_results,
            "claude": self._convert_claude_results,
            "crossref": self._convert_crossref_results,
            "pmc": self._convert_pmc_results,
            "scholar": self._convert_scholar_results,
            "arxiv": self._convert_arxiv_results,
        }
        
        converter = provider_map.get(agent_name.lower(), self._convert_generic_results)
        return converter(payload, search_query)
    
    def _convert_gemini_results(self, payload: Any, search_query: Optional[str] = None) -> List[SearchResult]:
        """Convert Gemini search results with enhanced metadata extraction"""
        results = []
        
        if not payload or not isinstance(payload, (dict, list)):
            return results
        
        # Handle different Gemini output formats
        sources = self._extract_sources_from_payload(payload)
        
        for source in sources:
            if not isinstance(source, dict):
                continue
            
            try:
                result = SearchResult(
                    title=self._extract_field(source, ["title", "name", "heading"]) or "Untitled",
                    authors=self._extract_authors(source),
                    abstract=self._extract_field(source, ["abstract", "summary", "snippet", "content"])[:500] or "",
                    url=self._extract_field(source, ["url", "link"]) or "",
                    doi=self._extract_doi(source),
                    publication_date=self._extract_field(source, ["publication_date", "published_date", "date", "year"]),
                    citation_count=self._safe_int(source.get("citation_count") or source.get("citations")),
                    source_type=self._infer_source_type(source),
                    credibility_score=self._calculate_enhanced_credibility(source),
                    relevance_score=float(source.get("relevance_score", 0.5)),
                    provider="gemini",
                    search_query=search_query,
                    keywords=self._extract_keywords(source),
                    language=source.get("language", "en"),
                    raw_data={"agent": "gemini", "original": source}
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to normalize Gemini result: {e}")
                continue
        
        return results
    
    def _convert_perplexity_results(self, payload: Any, search_query: Optional[str] = None) -> List[SearchResult]:
        """Convert Perplexity search results"""
        results = []
        
        if not payload or not isinstance(payload, dict):
            return results
        
        sources = payload.get("sources", [])
        
        for source in sources:
            if not isinstance(source, dict):
                continue
            
            try:
                # Perplexity specific processing
                credibility_scores = source.get("credibility_scores", {})
                credibility_score = float(credibility_scores.get("overall", 0.5))
                
                result = SearchResult(
                    title=source.get("title", "Untitled"),
                    authors=self._extract_authors(source),
                    abstract=source.get("snippet", "")[:500],
                    url=source.get("url", ""),
                    source_type=self._infer_source_type(source),
                    credibility_score=credibility_score,
                    relevance_score=0.7,
                    provider="perplexity",
                    search_query=search_query,
                    raw_data={"agent": "perplexity", "original": source}
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to normalize Perplexity result: {e}")
                continue
        
        return results
    
    def _convert_crossref_results(self, payload: Any, search_query: Optional[str] = None) -> List[SearchResult]:
        """Enhanced CrossRef conversion with comprehensive metadata"""
        results = []
        
        if not payload or not isinstance(payload, dict):
            return results
        
        items = payload.get("message", {}).get("items", [])
        
        for item in items:
            if not isinstance(item, dict):
                continue
            
            try:
                # Extract CrossRef metadata
                title_parts = item.get("title", [])
                title = title_parts[0] if title_parts else "Untitled"
                
                # Enhanced author extraction
                authors = []
                for author in item.get("author", []):
                    if isinstance(author, dict):
                        given = author.get("given", "")
                        family = author.get("family", "")
                        full_name = f"{given} {family}".strip()
                        if full_name:
                            authors.append(full_name)
                
                # Extract publication date
                pub_date = self._extract_crossref_date(item)
                
                result = SearchResult(
                    title=title,
                    authors=authors,
                    abstract=item.get("abstract", ""),
                    url=item.get("URL", ""),
                    doi=item.get("DOI"),
                    publication_date=pub_date,
                    journal=item.get("container-title", [None])[0],
                    volume=item.get("volume"),
                    issue=item.get("issue"),
                    pages=item.get("page"),
                    citation_count=item.get("is-referenced-by-count"),
                    source_type=self._infer_crossref_source_type(item),
                    credibility_score=0.9,  # CrossRef is highly credible
                    relevance_score=item.get("score", 0.8) / 100.0,  # Normalize score
                    access_type=self._infer_access_type(item),
                    provider="crossref",
                    search_query=search_query,
                    subjects=item.get("subject", []),
                    raw_data={"agent": "crossref", "original": item}
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to normalize CrossRef result: {e}")
                continue
        
        return results
    
    def _convert_arxiv_results(self, payload: Any, search_query: Optional[str] = None) -> List[SearchResult]:
        """Convert arXiv results with preprint-specific handling"""
        results = []
        
        if not payload:
            return results
        
        papers = self._extract_sources_from_payload(payload, ["papers", "results"])
        
        for paper in papers:
            if not isinstance(paper, dict):
                continue
            
            try:
                arxiv_id = paper.get("id", "").split("/")[-1]
                
                result = SearchResult(
                    title=paper.get("title", "Untitled"),
                    authors=self._extract_authors(paper),
                    abstract=paper.get("summary", paper.get("abstract", ""))[:500],
                    url=f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else paper.get("link", ""),
                    arxiv_id=arxiv_id,
                    publication_date=paper.get("published", paper.get("updated")),
                    source_type=SourceType.PREPRINT,
                    credibility_score=0.6,  # Preprints have moderate credibility
                    relevance_score=0.8,   # But usually highly relevant
                    access_type=AccessType.OPEN,
                    provider="arxiv",
                    search_query=search_query,
                    subjects=paper.get("categories", []),
                    keywords=self._extract_keywords(paper),
                    raw_data={"agent": "arxiv", "original": paper}
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to normalize arXiv result: {e}")
                continue
        
        return results
    
    def _convert_pmc_results(self, payload: Any, search_query: Optional[str] = None) -> List[SearchResult]:
        """Convert PubMed Central results"""
        results = []
        
        if not payload:
            return results
        
        articles = self._extract_sources_from_payload(payload, ["articles", "results"])
        
        for article in articles:
            if not isinstance(article, dict):
                continue
            
            try:
                pmcid = article.get("pmcid", "")
                pmid = article.get("pmid", "")
                
                result = SearchResult(
                    title=article.get("title", "Untitled"),
                    authors=self._extract_authors(article),
                    abstract=article.get("abstract", "")[:500],
                    url=f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/" if pmcid else "",
                    pmid=pmid,
                    doi=article.get("doi"),
                    publication_date=article.get("pub_date"),
                    journal=article.get("journal"),
                    source_type=SourceType.JOURNAL,
                    credibility_score=0.95,  # PMC is very credible
                    relevance_score=0.8,
                    access_type=AccessType.OPEN,
                    provider="pmc",
                    search_query=search_query,
                    keywords=article.get("mesh_terms", []),
                    raw_data={"agent": "pmc", "original": article}
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to normalize PMC result: {e}")
                continue
        
        return results
    
    def _convert_scholar_results(self, payload: Any, search_query: Optional[str] = None) -> List[SearchResult]:
        """Convert Google Scholar results"""
        results = []
        
        if not payload:
            return results
        
        sources = self._extract_sources_from_payload(payload, ["results", "papers"])
        
        for source in sources:
            if not isinstance(source, dict):
                continue
            
            try:
                result = SearchResult(
                    title=source.get("title", "Untitled"),
                    authors=self._extract_authors(source),
                    abstract=source.get("snippet", source.get("abstract", ""))[:500],
                    url=source.get("url", source.get("link", "")),
                    publication_date=str(source.get("year", "")) if source.get("year") else None,
                    citation_count=self._safe_int(source.get("cited_by", 0)),
                    source_type=SourceType.ACADEMIC,
                    credibility_score=0.8,  # Scholar results are generally credible
                    relevance_score=0.7,
                    provider="scholar",
                    search_query=search_query,
                    raw_data={"agent": "scholar", "original": source}
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to normalize Scholar result: {e}")
                continue
        
        return results
    
    def _convert_openai_results(self, payload: Any, search_query: Optional[str] = None) -> List[SearchResult]:
        """Convert OpenAI/O3 search results"""
        results = []
        
        if not payload:
            return results
        
        sources = self._extract_sources_from_payload(payload)
        
        for source in sources:
            if not isinstance(source, dict):
                continue
            
            try:
                result = SearchResult(
                    title=source.get("title", source.get("name", "Untitled")),
                    authors=self._extract_authors(source),
                    abstract=source.get("abstract", source.get("summary", ""))[:500],
                    url=source.get("url", source.get("link", "")),
                    source_type=self._infer_source_type(source),
                    credibility_score=0.6,  # Default for OpenAI results
                    relevance_score=0.6,
                    provider="openai",
                    search_query=search_query,
                    raw_data={"agent": "openai", "original": source}
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to normalize OpenAI result: {e}")
                continue
        
        return results
    
    def _convert_claude_results(self, payload: Any, search_query: Optional[str] = None) -> List[SearchResult]:
        """Convert Claude search results"""
        results = []
        
        if not payload:
            return results
        
        sources = self._extract_sources_from_payload(payload, ["sources", "citations"])
        
        for source in sources:
            if not isinstance(source, dict):
                continue
            
            try:
                result = SearchResult(
                    title=source.get("title", "Untitled"),
                    authors=self._extract_authors(source),
                    abstract=source.get("excerpt", source.get("summary", ""))[:500],
                    url=source.get("url", ""),
                    source_type=self._infer_source_type(source),
                    credibility_score=0.7,  # Claude tends to find quality sources
                    relevance_score=0.7,
                    provider="claude",
                    search_query=search_query,
                    raw_data={"agent": "claude", "original": source}
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to normalize Claude result: {e}")
                continue
        
        return results
    
    def _convert_generic_results(self, payload: Any, search_query: Optional[str] = None) -> List[SearchResult]:
        """Enhanced generic converter with comprehensive field extraction"""
        results = []
        
        if not payload:
            return results
        
        sources = self._extract_sources_from_payload(payload)
        
        for source in sources:
            if not isinstance(source, dict):
                continue
            
            try:
                result = SearchResult(
                    title=self._extract_field(source, ["title", "name", "heading", "label"]) or "Untitled",
                    authors=self._extract_authors(source),
                    abstract=self._extract_field(source, ["abstract", "snippet", "description", "content", "summary", "text"])[:500] or "",
                    url=self._extract_field(source, ["url", "link", "href", "uri"]) or "",
                    doi=self._extract_doi(source),
                    publication_date=self._extract_field(source, ["date", "published", "publication_date"]),
                    citation_count=self._safe_int(self._extract_field(source, ["citations", "citation_count"])),
                    source_type=self._infer_source_type(source),
                    credibility_score=0.3,  # Lower score for generic results
                    relevance_score=0.3,
                    provider="generic",
                    search_query=search_query,
                    raw_data={"agent": "generic", "original": source}
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to normalize generic result: {e}")
                continue
        
        return results
    
    # Helper methods
    
    def _extract_sources_from_payload(self, payload: Any, source_keys: List[str] = None) -> List[Dict[str, Any]]:
        """Extract sources from various payload formats"""
        if source_keys is None:
            source_keys = ["sources", "results", "search_results", "citations", "data", "items", "papers", "articles"]
        
        sources = []
        if isinstance(payload, dict):
            for key in source_keys:
                if key in payload and isinstance(payload[key], list):
                    sources = payload[key]
                    break
            
            # Handle nested structures
            if not sources and "data" in payload:
                data = payload["data"]
                if isinstance(data, dict):
                    for key in source_keys:
                        if key in data and isinstance(data[key], list):
                            sources = data[key]
                            break
                elif isinstance(data, list):
                    sources = data
        elif isinstance(payload, list):
            sources = payload
        
        return sources
    
    def _extract_field(self, source: Dict[str, Any], field_names: List[str]) -> Optional[str]:
        """Extract field value trying multiple field names"""
        for field_name in field_names:
            value = source.get(field_name)
            if value:
                return str(value).strip()
        return None
    
    def _extract_authors(self, source: Dict[str, Any]) -> List[str]:
        """Enhanced author extraction with better name parsing"""
        authors = []
        
        # Check various author field formats
        author_fields = ["authors", "author", "creator", "by", "contributors"]
        for field in author_fields:
            if field in source:
                author_data = source[field]
                if isinstance(author_data, str):
                    authors = self._parse_author_string(author_data)
                elif isinstance(author_data, list):
                    authors = self._parse_author_list(author_data)
                break
        
        # Clean and validate author names
        cleaned_authors = []
        for author in authors[:15]:  # Limit to 15 authors
            if isinstance(author, dict):
                name = self._format_author_name(author)
            else:
                name = str(author).strip()
            
            if name and len(name) > 1 and name not in cleaned_authors:
                cleaned_authors.append(name)
        
        return cleaned_authors
    
    def _parse_author_string(self, author_string: str) -> List[str]:
        """Parse author string with various delimiters"""
        separators = [" and ", ", ", "; ", " & ", "\n"]
        authors = [author_string]
        
        for sep in separators:
            new_authors = []
            for author in authors:
                new_authors.extend(author.split(sep))
            authors = new_authors
        
        return [a.strip() for a in authors if a.strip()]
    
    def _parse_author_list(self, author_list: List[Any]) -> List[str]:
        """Parse list of author objects or strings"""
        authors = []
        for author in author_list:
            if isinstance(author, dict):
                name = self._format_author_name(author)
                if name:
                    authors.append(name)
            else:
                authors.append(str(author))
        return authors
    
    def _format_author_name(self, author_dict: Dict[str, Any]) -> str:
        """Format author name from structured data"""
        if "name" in author_dict:
            return author_dict["name"]
        
        first = author_dict.get("given", author_dict.get("firstName", ""))
        last = author_dict.get("family", author_dict.get("lastName", ""))
        
        if first and last:
            return f"{first} {last}"
        elif last:
            return last
        elif first:
            return first
        
        return ""
    
    def _extract_doi(self, source: Dict[str, Any]) -> Optional[str]:
        """Enhanced DOI extraction with validation"""
        # Check direct DOI field
        doi = source.get("doi", source.get("DOI"))
        if doi:
            return self._clean_doi(doi)
        
        # Extract from URL
        url = source.get("url", source.get("link", ""))
        if "doi.org/" in url:
            doi_part = url.split("doi.org/")[-1]
            return self._clean_doi(doi_part)
        
        # Extract from identifiers object
        identifiers = source.get("identifiers", source.get("externalIds", {}))
        if isinstance(identifiers, dict):
            doi = identifiers.get("doi", identifiers.get("DOI"))
            if doi:
                return self._clean_doi(doi)
        
        return None
    
    def _clean_doi(self, doi: str) -> str:
        """Clean and validate DOI format"""
        doi = doi.strip()
        
        # Remove common prefixes
        prefixes = ["doi:", "https://doi.org/", "http://doi.org/", "DOI:"]
        for prefix in prefixes:
            if doi.lower().startswith(prefix.lower()):
                doi = doi[len(prefix):]
                break
        
        # Basic DOI format validation
        if re.match(r'^10\.\d+/.+', doi):
            return doi
        
        return doi  # Return as-is if doesn't match standard format
    
    def _extract_keywords(self, source: Dict[str, Any]) -> List[str]:
        """Extract keywords from various fields"""
        keywords = []
        
        keyword_fields = ["keywords", "tags", "subjects", "topics", "categories", "mesh_terms", "fieldsOfStudy"]
        for field in keyword_fields:
            if field in source:
                field_data = source[field]
                if isinstance(field_data, list):
                    keywords.extend([str(k).strip() for k in field_data])
                elif isinstance(field_data, str):
                    keywords.extend([k.strip() for k in field_data.split(",")])
        
        # Remove duplicates and empty keywords
        return list(set([k for k in keywords if k and len(k) > 1]))[:20]  # Limit to 20
    
    def _extract_crossref_date(self, item: Dict[str, Any]) -> Optional[str]:
        """Extract publication date from CrossRef format"""
        date_parts = item.get("published-print", item.get("published-online", {})).get("date-parts")
        if date_parts and date_parts[0]:
            year, month, day = date_parts[0] + [1, 1]  # Pad with defaults
            return f"{year:04d}-{month:02d}-{day:02d}"
        return None
    
    def _infer_source_type(self, source: Dict[str, Any]) -> SourceType:
        """Enhanced source type inference"""
        # Check explicit type field
        explicit_type = source.get("type", source.get("source_type", "")).lower()
        if explicit_type:
            type_mapping = {
                "academic": SourceType.ACADEMIC,
                "journal": SourceType.JOURNAL,
                "conference": SourceType.CONFERENCE,
                "book": SourceType.BOOK,
                "news": SourceType.NEWS,
                "preprint": SourceType.PREPRINT,
                "thesis": SourceType.THESIS,
                "report": SourceType.REPORT,
                "dataset": SourceType.DATASET,
                "patent": SourceType.PATENT,
                "government": SourceType.GOVERNMENT,
            }
            if explicit_type in type_mapping:
                return type_mapping[explicit_type]
        
        # URL-based inference
        url = source.get("url", source.get("link", "")).lower()
        if "arxiv.org" in url or "biorxiv.org" in url:
            return SourceType.PREPRINT
        elif "pubmed" in url or "scholar.google" in url:
            return SourceType.ACADEMIC
        elif "github.com" in url:
            return SourceType.CODE
        elif ".gov" in url:
            return SourceType.GOVERNMENT
        elif "news" in url:
            return SourceType.NEWS
        
        # Content-based inference
        title = source.get("title", "").lower()
        if "conference" in title or "proceedings" in title:
            return SourceType.CONFERENCE
        elif "thesis" in title or "dissertation" in title:
            return SourceType.THESIS
        
        return SourceType.WEB
    
    def _infer_crossref_source_type(self, item: Dict[str, Any]) -> SourceType:
        """Infer source type from CrossRef metadata"""
        work_type = item.get("type", "").lower()
        
        type_mapping = {
            "journal-article": SourceType.JOURNAL,
            "book-chapter": SourceType.BOOK,
            "book": SourceType.BOOK,
            "proceedings-article": SourceType.CONFERENCE,
            "report": SourceType.REPORT,
            "thesis": SourceType.THESIS,
            "patent": SourceType.PATENT,
            "dataset": SourceType.DATASET,
        }
        
        return type_mapping.get(work_type, SourceType.ACADEMIC)
    
    def _infer_access_type(self, source: Dict[str, Any]) -> AccessType:
        """Infer access type from metadata"""
        # Check license information
        license_info = source.get("license", [])
        if license_info:
            license_url = license_info[0].get("URL", "").lower() if isinstance(license_info, list) else ""
            if "creativecommons" in license_url or "open" in license_url:
                return AccessType.OPEN
        
        # Check if open access
        is_oa = source.get("is-open-access", False)
        if is_oa:
            return AccessType.OPEN
        
        return AccessType.UNKNOWN
    
    def _calculate_enhanced_credibility(self, source: Dict[str, Any]) -> float:
        """Enhanced credibility scoring with multiple factors"""
        if not self.feature_flags["credibility_scoring"]:
            return 0.5
        
        score = 0.3  # Base score
        
        # DOI presence (indicates formal publication)
        if source.get("doi") or source.get("DOI") or "doi.org" in source.get("url", ""):
            score += 0.15
        
        # Citation count factor
        citations = source.get("citations", source.get("citation_count", source.get("is-referenced-by-count", 0)))
        if isinstance(citations, int) and citations > 0:
            import math
            citation_score = min(0.25, math.log(citations + 1) / 10.0)
            score += citation_score
        
        # Domain reputation
        url = source.get("url", "").lower()
        for domain, domain_score in self.high_quality_domains.items():
            if domain in url:
                score += domain_score * 0.2
                break
        
        # Publication metadata completeness
        metadata_fields = ["authors", "publication_date", "journal", "abstract"]
        present_fields = sum(1 for field in metadata_fields if source.get(field))
        score += (present_fields / len(metadata_fields)) * 0.1
        
        # Peer review indicators
        content = f"{source.get('title', '')} {source.get('abstract', '')}".lower()
        peer_review_keywords = ["peer-reviewed", "peer reviewed", "refereed", "journal", "reviewed"]
        if any(keyword in content for keyword in peer_review_keywords):
            score += 0.1
        
        return min(1.0, score)
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to integer"""
        if value is None:
            return None
        
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Enhanced deduplication based on content hash, DOI, and URL"""
        seen_hashes = set()
        seen_dois = set()
        seen_urls = set()
        deduplicated = []
        
        for result in results:
            # Skip if we've seen this exact content before
            if result.content_hash in seen_hashes:
                continue
            
            # Skip if we've seen this DOI before (DOI is most reliable identifier)
            if result.doi and result.doi in seen_dois:
                continue
            
            # Skip if we've seen this URL before
            normalized_url = self._normalize_url(result.url)
            if normalized_url and normalized_url in seen_urls:
                continue
            
            # Add to seen sets
            seen_hashes.add(result.content_hash)
            if result.doi:
                seen_dois.add(result.doi)
            if normalized_url:
                seen_urls.add(normalized_url)
            
            deduplicated.append(result)
        
        return deduplicated
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication"""
        if not url:
            return ""
        
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc
            if domain.startswith("www."):
                domain = domain[4:]
            return f"{parsed.scheme}://{domain}{parsed.path}"
        except:
            return url.lower()
    
    def _filter_and_rank_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Filter and rank results by quality and relevance"""
        # Filter out very low quality results
        filtered = [r for r in results if r.credibility_score >= 0.2 and r.relevance_score >= 0.2]
        
        # Sort by composite score
        filtered.sort(key=lambda x: x.composite_score, reverse=True)
        
        return filtered


# Global normalizer instance
_normalizer: Optional[SearchResultNormalizer] = None

def get_search_normalizer() -> SearchResultNormalizer:
    """Get or create the global search result normalizer"""
    global _normalizer
    if _normalizer is None:
        _normalizer = SearchResultNormalizer()
    return _normalizer

def to_search_results(agent_name: str, payload: Any, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convert agent-specific payload to standardized SearchResult list with enhanced processing.
    
    Args:
        agent_name: Name of the search agent
        payload: Raw output from the search agent
        search_query: Original search query for context
        
    Returns:
        List of enhanced SearchResult dictionaries
    """
    normalizer = get_search_normalizer()
    return normalizer.normalize_results(agent_name, payload, search_query)

# Backwards compatibility - delegate to enhanced normalizer
def normalize_search_results(agent_name: str, payload: Any, search_query: Optional[str] = None) -> List[Dict[str, Any]]:
    """Legacy function name for backwards compatibility"""
    return to_search_results(agent_name, payload, search_query)