from __future__ import annotations

import os
import logging
from typing import Any, Dict, Mapping, List, TypedDict, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class _Aliases(TypedDict):
    aliases: List[str]

# Canonical keys we aim to use across Analyzer, Router, and Graphs
_CANONICAL_KEYS: Dict[str, _Aliases] = {
    "document_type": {"aliases": ["writeupType", "writeup_type", "doc_type", "documentType", "writing_type", "writingType", "type"]},
    "citation_style": {"aliases": ["referenceStyle", "reference_style", "style", "citationStyle"]},
    "academic_level": {"aliases": ["educationLevel", "education_level", "level", "academicLevel"]},
    "word_count": {"aliases": ["words", "target_words", "wordCount"]},
    "field": {"aliases": ["academicField", "academic_field", "discipline", "subject"]},
    "region": {"aliases": ["geo", "locale"]},
    "language": {"aliases": ["lang"]},
    "tone": {"aliases": []},
    "pages": {"aliases": ["page_count", "pageCount"]},
    "target_sources": {"aliases": ["sources", "num_sources", "numSources"]},
    "quality_tier": {"aliases": ["quality", "qualityTier", "tier", "quality_level"]},
    "topic": {"aliases": ["title", "subject_matter", "prompt"]},
    "deadline_hours": {"aliases": ["deadline", "due_date", "dueDate"]},
    "special_instructions": {"aliases": ["instructions", "specialInstructions", "notes", "requirements"]},
}

_ENUM_NORMALIZERS: Dict[str, Dict[str, str]] = {
    "citation_style": {
        "apa": "APA",
        "mla": "MLA",
        "chicago": "Chicago",
        "harvard": "Harvard",
        "ieee": "IEEE",
        "vancouver": "Vancouver",
        "ama": "AMA",
        "oxford": "Oxford",
        "asa": "ASA",
        "turabian": "Turabian",
        # Aliases
        "american_psychological": "APA",
        "modern_language": "MLA",
        "chicago_manual": "Chicago",
        "harv": "Harvard",
        "ieee_style": "IEEE",
        "vancouver_style": "Vancouver",
        "american_medical": "AMA",
        "oxford_style": "Oxford",
        "american_sociological": "ASA",
    },
    "document_type": {
        "essay": "Essay",
        "comparative_essay": "ComparativeEssay",
        "case_study": "CaseStudy",
        "technical_report": "TechnicalReport",
        "reflection": "Reflection",
        "dissertation": "Dissertation",
        "thesis": "Thesis",
        "research_paper": "ResearchPaper",
        "literature_review": "LiteratureReview",
        "book_report": "BookReport",
        "lab_report": "LabReport",
        "argumentative_essay": "ArgumentativeEssay",
        "analytical_essay": "AnalyticalEssay",
        # Aliases
        "academic_paper": "ResearchPaper",
        "paper": "ResearchPaper",
        "research": "ResearchPaper",
        "phd_dissertation": "Dissertation",
        "doctoral_dissertation": "Dissertation",
        "masters_thesis": "Thesis",
        "bachelor_thesis": "Thesis",
        "bachelors_thesis": "Thesis",
        "tech_report": "TechnicalReport",
        "report": "TechnicalReport",
        "lit_review": "LiteratureReview",
        "literature_survey": "LiteratureReview",
        "review": "LiteratureReview",
        "case": "CaseStudy",
        "study": "CaseStudy",
        "book_review": "BookReport",
        "lab": "LabReport",
        "laboratory_report": "LabReport",
        "compare": "ComparativeEssay",
        "comparison": "ComparativeEssay",
        "argue": "ArgumentativeEssay",
        "argument": "ArgumentativeEssay",
        "analyze": "AnalyticalEssay",
        "analysis": "AnalyticalEssay",
    },
    "academic_level": {
        "high_school": "HighSchool",
        "undergraduate": "Undergraduate",
        "masters": "Masters",
        "postgraduate": "Postgraduate",
        "phd": "PhD",
        "professional": "Professional",
        # Aliases
        "hs": "HighSchool",
        "high": "HighSchool",
        "secondary": "HighSchool",
        "undergrad": "Undergraduate",
        "bachelor": "Undergraduate",
        "bachelors": "Undergraduate",
        "college": "Undergraduate",
        "university": "Undergraduate",
        "master": "Masters",
        "graduate": "Masters",
        "grad": "Masters",
        "postgrad": "Postgraduate",
        "post_graduate": "Postgraduate",
        "doctoral": "PhD",
        "doctorate": "PhD",
        "prof": "Professional",
        "work": "Professional",
    },
    "quality_tier": {
        "basic": "Basic",
        "standard": "Standard",
        "premium": "Premium",
        # Aliases
        "low": "Basic",
        "regular": "Standard",
        "normal": "Standard",
        "medium": "Standard",
        "high": "Premium",
        "best": "Premium",
        "professional": "Premium",
        "enterprise": "Premium",
    },
    "region": {
        "us": "US",
        "usa": "US",
        "uk": "UK",
        "gb": "UK",
        "eu": "EU",
        "europe": "EU",
        "canada": "CA",
        "ca": "CA",
        "australia": "AU",
        "au": "AU",
    },
}

def _snake_like(key: str) -> str:
    # minimal snake/camel harmonization
    out: List[str] = []
    for ch in key:
        if ch.isupper():
            out.append("_")
            out.append(ch.lower())
        else:
            out.append(ch)
    s = "".join(out)
    return s.lstrip("_")

def _resolve_key(k: str) -> str:
    if k in _CANONICAL_KEYS:
        return k
    snake = _snake_like(k)
    for canon, meta in _CANONICAL_KEYS.items():
        if snake == canon:
            return canon
        for alias in meta["aliases"]:
            if snake == _snake_like(alias):
                return canon
    return snake

def _normalize_enum(name: str, value: Any) -> Any:
    if not isinstance(value, str):
        return value
    table = _ENUM_NORMALIZERS.get(name)
    if not table:
        return value
    key = value.strip().lower()
    return table.get(key, value)

def _derive_pages(word_count: int | None) -> int | None:
    if not word_count or word_count <= 0:
        return None
    # 300 words ≈ 1 page default academic density
    return max(1, round(word_count / 300))

def _derive_target_sources(document_type: str | None, academic_level: str | None, pages: int | None = None) -> int | None:
    """Enhanced heuristic for target sources based on document type, level, and length"""
    doc = (document_type or "").lower()
    lvl = (academic_level or "").lower()
    page_count = pages or 5
    
    # Base sources by document type
    type_base = {
        "dissertation": 40,
        "thesis": 25,
        "literature_review": 30,
        "literaturereview": 30,
        "research_paper": 15,
        "researchpaper": 15,
        "technical_report": 12,
        "technicalreport": 12,
        "comparative_essay": 10,
        "comparativeessay": 10,
        "case_study": 8,
        "casestudy": 8,
        "argumentative_essay": 8,
        "argumentativeessay": 8,
        "analytical_essay": 10,
        "analyticalessay": 10,
        "lab_report": 6,
        "labreport": 6,
        "book_report": 3,
        "bookreport": 3,
        "essay": 5,
    }
    
    base_sources = type_base.get(doc.replace(" ", "").replace("_", ""), 8)
    
    # Adjust by academic level
    level_multipliers = {
        "phd": 1.5,
        "doctoral": 1.5,
        "doctorate": 1.5,
        "postgraduate": 1.3,
        "postgrad": 1.3,
        "masters": 1.2,
        "master": 1.2,
        "graduate": 1.2,
        "undergraduate": 1.0,
        "undergrad": 1.0,
        "bachelor": 1.0,
        "college": 1.0,
        "high_school": 0.7,
        "highschool": 0.7,
        "high": 0.7,
        "secondary": 0.7,
        "professional": 1.1,
    }
    
    multiplier = 1.0
    for level_key, mult in level_multipliers.items():
        if level_key in lvl:
            multiplier = mult
            break
    
    # Adjust by page length (rough heuristic: 1 source per 2-3 pages minimum)
    page_factor = max(0.5, page_count / 10.0)  # More pages = more sources needed
    
    final_sources = int(base_sources * multiplier * page_factor)
    return max(3, min(final_sources, 100))  # Reasonable bounds

def normalize_user_params(inp: Mapping[str, Any] | None, enable_audit_logging: bool = False) -> Dict[str, Any]:
    """
    Enhanced parameter normalization with feature flag support.
    Accepts an input mapping with arbitrary casing/aliases and produces a canonical dict:
      - keys harmonized to snake_case canonical names from _CANONICAL_KEYS
      - enums normalized to expected values when known
      - derives pages, target_sources, and complexity metrics if missing
      - supports feature flags for staged rollout
    """
    result: Dict[str, Any] = {}
    if not inp:
        return result

    # Feature flags
    feature_flags = {
        "params_normalization": os.getenv("FEATURE_PARAMS_NORMALIZATION", "true").lower() == "true",
        "enhanced_derivation": os.getenv("FEATURE_ENHANCED_DERIVATION", "true").lower() == "true",
        "strict_validation": os.getenv("FEATURE_STRICT_VALIDATION", "false").lower() == "true",
    }
    
    if enable_audit_logging:
        logger.info(f"Normalizing user params with flags: {feature_flags}")
        logger.debug(f"Input params: {dict(inp)}")

    # 1) harmonize keys
    for k, v in inp.items():
        canon = _resolve_key(k)
        result[canon] = v

    # 2) normalize enums with expanded coverage
    enum_fields = ["citation_style", "document_type", "academic_level", "quality_tier", "region"]
    for name in enum_fields:
        if name in result and result[name]:
            normalized_value = _normalize_enum(name, result[name])
            result[name] = normalized_value
            if enable_audit_logging and normalized_value != result.get(name):
                logger.debug(f"Normalized {name}: {result[name]} -> {normalized_value}")

    # 3) Enhanced value coercions and derivations
    if feature_flags["params_normalization"]:
        # word_count/pages coercion with validation
        wc = None
        if "word_count" in result and result["word_count"]:
            try:
                wc = int(result["word_count"])
                if wc <= 0:
                    wc = None
                elif wc > 125000:  # Cap at reasonable maximum
                    wc = 125000
                    if enable_audit_logging:
                        logger.warning(f"Word count capped at 125000")
            except (ValueError, TypeError):
                wc = None
            result["word_count"] = wc

        # Enhanced pages derivation
        if "pages" not in result or result.get("pages") in (None, "", 0):
            derived_pages = _derive_pages(result.get("word_count"))
            if derived_pages is not None:
                result["pages"] = derived_pages
                if enable_audit_logging:
                    logger.debug(f"Derived pages from word_count: {derived_pages}")
        else:
            # Validate existing pages
            try:
                pages = int(result["pages"])
                result["pages"] = max(1, min(pages, 500))  # Reasonable bounds
            except (ValueError, TypeError):
                result["pages"] = _derive_pages(result.get("word_count")) or 5

        # Enhanced target_sources derivation
        if "target_sources" not in result or result.get("target_sources") in (None, "", 0):
            result["target_sources"] = _derive_target_sources(
                result.get("document_type"),
                result.get("academic_level"),
                result.get("pages")
            )

        # Derive complexity weight if enhanced derivation is enabled
        if feature_flags["enhanced_derivation"]:
            result["complexity_weight"] = _calculate_complexity_weight(
                result.get("document_type"),
                result.get("academic_level"),
                result.get("pages", 5)
            )
            
            result["research_depth"] = _derive_research_depth(
                result.get("document_type"),
                result.get("academic_level"),
                result.get("pages", 5)
            )

        # Normalize topic/title
        if "topic" in result and result["topic"]:
            topic = str(result["topic"]).strip()
            if len(topic) > 500:
                topic = topic[:500] + "..."
                if enable_audit_logging:
                    logger.warning("Topic truncated to 500 characters")
            result["topic"] = topic
        elif feature_flags["strict_validation"]:
            raise ValueError("Topic/title is required")

        # Normalize deadline to hours
        if "deadline_hours" in result and result["deadline_hours"]:
            result["deadline_hours"] = _normalize_deadline_to_hours(result["deadline_hours"])

    # Store normalization metadata
    result["_normalization_meta"] = {
        "version": "1.1",
        "feature_flags": feature_flags,
        "normalized_fields": list(result.keys()),
    }

    if enable_audit_logging:
        logger.info(f"Normalization complete. Output keys: {list(result.keys())}")

    return result

def validate_user_params(params: Mapping[str, Any], strict: bool = False) -> None:
    """
    Enhanced validation with strict mode support.
    Validates normalized parameters and raises ValueError on critical mismatches.
    """
    # Validate citation_style
    if "citation_style" in params and isinstance(params.get("citation_style"), str):
        norm = _normalize_enum("citation_style", params["citation_style"])
        if strict and norm not in _ENUM_NORMALIZERS["citation_style"].values():
            raise ValueError(f"Unsupported citation_style: {params['citation_style']}")

    # Validate document_type
    if "document_type" in params and isinstance(params.get("document_type"), str):
        norm = _normalize_enum("document_type", params["document_type"])
        if strict and norm not in _ENUM_NORMALIZERS["document_type"].values():
            raise ValueError(f"Unsupported document_type: {params['document_type']}")
    
    # Validate academic_level
    if "academic_level" in params and isinstance(params.get("academic_level"), str):
        norm = _normalize_enum("academic_level", params["academic_level"])
        if strict and norm not in _ENUM_NORMALIZERS["academic_level"].values():
            raise ValueError(f"Unsupported academic_level: {params['academic_level']}")
    
    # Validate numeric fields
    if "pages" in params:
        pages = params["pages"]
        if pages is not None and (not isinstance(pages, int) or pages <= 0 or pages > 500):
            if strict:
                raise ValueError(f"Pages must be between 1 and 500, got: {pages}")
    
    if "word_count" in params:
        wc = params["word_count"]
        if wc is not None and (not isinstance(wc, int) or wc <= 0 or wc > 125000):
            if strict:
                raise ValueError(f"Word count must be between 1 and 125000, got: {wc}")
    
    if "target_sources" in params:
        sources = params["target_sources"]
        if sources is not None and (not isinstance(sources, int) or sources < 0 or sources > 100):
            if strict:
                raise ValueError(f"Target sources must be between 0 and 100, got: {sources}")

    # Validate required fields in strict mode
    if strict:
        if not params.get("topic"):
            raise ValueError("Topic is required")
        if not params.get("document_type"):
            raise ValueError("Document type is required")


def _normalize_deadline_to_hours(deadline: Any) -> Optional[int]:
    """Normalize various deadline formats to hours"""
    if not deadline:
        return None
    
    try:
        if isinstance(deadline, (int, float)):
            return max(1, min(int(deadline), 8760))  # Cap at 1 year
        
        if isinstance(deadline, str):
            deadline = deadline.lower().strip()
            
            # Parse relative deadlines with regex
            import re
            patterns = [
                (r'(\d+)\s*hour?s?', 1),
                (r'(\d+)\s*day?s?', 24),
                (r'(\d+)\s*week?s?', 168),
                (r'(\d+)\s*month?s?', 720),  # 30 days
            ]
            
            for pattern, multiplier in patterns:
                match = re.search(pattern, deadline)
                if match:
                    number = int(match.group(1))
                    return max(1, min(number * multiplier, 8760))
        
        return None
    except (ValueError, TypeError):
        return None


def _calculate_complexity_weight(document_type: str | None, academic_level: str | None, pages: int) -> float:
    """Calculate complexity weight for routing decisions"""
    doc = (document_type or "").lower()
    lvl = (academic_level or "").lower()
    
    # Base weights by document type
    type_weights = {
        "essay": 1.0,
        "researchpaper": 1.6,
        "research_paper": 1.6,
        "dissertation": 3.2,
        "thesis": 2.8,
        "technicalreport": 2.0,
        "technical_report": 2.0,
        "literaturereview": 2.4,
        "literature_review": 2.4,
        "casestudy": 1.8,
        "case_study": 1.8,
        "bookreport": 1.2,
        "book_report": 1.2,
        "labreport": 1.5,
        "lab_report": 1.5,
        "comparativeessay": 1.4,
        "comparative_essay": 1.4,
        "argumentativeessay": 1.3,
        "argumentative_essay": 1.3,
        "analyticalessay": 1.7,
        "analytical_essay": 1.7,
    }
    
    # Level multipliers
    level_multipliers = {
        "high_school": 0.7,
        "highschool": 0.7,
        "high": 0.7,
        "secondary": 0.7,
        "undergraduate": 1.0,
        "undergrad": 1.0,
        "bachelor": 1.0,
        "college": 1.0,
        "masters": 1.4,
        "master": 1.4,
        "graduate": 1.4,
        "postgraduate": 1.7,
        "postgrad": 1.7,
        "phd": 2.2,
        "doctoral": 2.2,
        "doctorate": 2.2,
        "professional": 1.3,
    }
    
    # Get base weight
    doc_clean = doc.replace(" ", "").replace("_", "")
    base_weight = type_weights.get(doc_clean, 1.0)
    
    # Get level multiplier
    level_mult = 1.0
    for level_key, mult in level_multipliers.items():
        if level_key in lvl:
            level_mult = mult
            break
    
    # Page complexity factor (logarithmic scaling)
    import math
    page_factor = 1.0 + math.log(max(1, pages / 5.0)) * 0.3
    page_factor = max(0.5, min(page_factor, 4.0))
    
    weight = base_weight * level_mult * page_factor
    return round(weight, 3)


def _derive_research_depth(document_type: str | None, academic_level: str | None, pages: int) -> str:
    """Derive research depth requirement"""
    doc = (document_type or "").lower().replace(" ", "").replace("_", "")
    lvl = (academic_level or "").lower()
    
    # Comprehensive research requirements
    if doc in ["dissertation", "thesis", "literaturereview"]:
        return "comprehensive"
    
    if any(level in lvl for level in ["phd", "doctoral", "postgraduate", "postgrad"]):
        if pages > 15:
            return "comprehensive"
        elif pages > 8:
            return "standard"
    
    if doc == "researchpaper" and pages > 12:
        return "comprehensive"
    
    # Minimal research requirements
    if doc in ["essay", "bookreport"] and pages < 4:
        return "minimal"
    
    if any(level in lvl for level in ["high_school", "highschool", "high", "secondary"]) and pages < 6:
        return "minimal"
    
    return "standard"
