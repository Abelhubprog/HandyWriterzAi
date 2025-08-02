"""
Enhanced Search Agent Output Normalization

This module provides comprehensive search result processing with:
- Multi-provider result normalization
- Intelligent deduplication (exact + semantic)
- Quality scoring and filtering
- Credibility assessment
- Provider reputation scoring
- Configurable processing pipeline

The module includes both the original adapter and enhanced adapter with
comprehensive metadata extraction and processing capabilities.
"""

# Primary enhanced adapter (recommended)
from .adapter_enhanced import (
    SearchResult as EnhancedSearchResult,
    SearchResultNormalizer,
    SourceType,
    AccessType,
    get_search_normalizer,
    to_search_results,
    normalize_search_results
)

# Legacy adapter for backwards compatibility
from .adapter import (
    SearchResult,
    SearchAdapterConfig,
    EnhancedSearchAdapter,
    get_search_adapter,
    to_search_results as legacy_to_search_results
)

# Export enhanced versions as primary API
__all__ = [
    # Enhanced API (recommended)
    "EnhancedSearchResult",
    "SearchResultNormalizer", 
    "SourceType",
    "AccessType",
    "get_search_normalizer",
    "to_search_results",
    "normalize_search_results",
    
    # Legacy API (backwards compatibility)
    "SearchResult",
    "SearchAdapterConfig",
    "EnhancedSearchAdapter", 
    "get_search_adapter",
    "legacy_to_search_results"
]