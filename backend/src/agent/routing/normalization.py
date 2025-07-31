from __future__ import annotations

from typing import Any, Dict, Mapping, List, TypedDict

class _Aliases(TypedDict):
    aliases: List[str]

# Canonical keys we aim to use across Analyzer, Router, and Graphs
_CANONICAL_KEYS: Dict[str, _Aliases] = {
    "document_type": {"aliases": ["writeupType", "writeup_type", "doc_type", "documentType"]},
    "citation_style": {"aliases": ["referenceStyle", "reference_style", "style"]},
    "academic_level": {"aliases": ["educationLevel", "education_level", "level"]},
    "word_count": {"aliases": ["words", "target_words"]},
    "field": {"aliases": ["academicField", "academic_field", "discipline", "subject"]},
    "region": {"aliases": ["geo", "locale"]},
    "language": {"aliases": ["lang"]},
    "tone": {"aliases": []},
    "pages": {"aliases": []},
    "target_sources": {"aliases": ["sources", "num_sources"]},
}

_ENUM_NORMALIZERS: Dict[str, Dict[str, str]] = {
    "citation_style": {
        "apa": "APA",
        "mla": "MLA",
        "chicago": "Chicago",
        "harvard": "Harvard",
    },
    "document_type": {
        "essay": "Essay",
        "comparative_essay": "ComparativeEssay",
        "case_study": "CaseStudy",
        "technical_report": "TechnicalReport",
        "reflection": "Reflection",
        "dissertation": "Dissertation",
    },
    "region": {
        "us": "US",
        "usa": "US",
        "uk": "UK",
        "gb": "UK",
        "eu": "EU",
        "europe": "EU",
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

def _derive_target_sources(document_type: str | None, academic_level: str | None) -> int | None:
    # very lightweight heuristic; can be replaced with role-aware policy later
    doc = (document_type or "").lower()
    if "dissertation" in doc:
        return 25
    if "comparative" in doc or "technical" in doc:
        return 12
    if "case" in doc:
        return 10
    # default by level
    lvl = (academic_level or "").lower()
    if "phd" in lvl or "doctor" in lvl:
        return 18
    if "master" in lvl:
        return 12
    if "undergrad" in lvl or "bachelor" in lvl:
        return 8
    return 8

def normalize_user_params(inp: Mapping[str, Any] | None) -> Dict[str, Any]:
    """
    Accepts an input mapping with arbitrary casing/aliases and produces a canonical dict:
      - keys harmonized to snake_case canonical names from _CANONICAL_KEYS
      - enums normalized to expected values when known
      - derives pages and target_sources if missing
    """
    result: Dict[str, Any] = {}
    if not inp:
        return result

    # 1) harmonize keys
    for k, v in inp.items():
        canon = _resolve_key(k)
        result[canon] = v

    # 2) normalize enums
    for name in ("citation_style", "document_type", "region"):
        if name in result:
            result[name] = _normalize_enum(name, result[name])

    # 3) value coercions
    # word_count/pages coercion
    wc = None
    if "word_count" in result:
        try:
            wc = int(result["word_count"])
        except Exception:
            wc = None
        result["word_count"] = wc

    # derive pages if missing
    if "pages" not in result or result.get("pages") in (None, "", 0):
        derived_pages = _derive_pages(result.get("word_count"))
        if derived_pages is not None:
            result["pages"] = derived_pages

    # derive target_sources if missing
    if "target_sources" not in result or result.get("target_sources") in (None, "", 0):
        result["target_sources"] = _derive_target_sources(
            result.get("document_type"),
            result.get("academic_level"),
        )

    return result

def validate_user_params(params: Mapping[str, Any]) -> None:
    """
    Lightweight validation; raise ValueError on hard mismatches
    """
    # Accept any Mapping; avoid over-strict type complaints from static analyzer
    if "citation_style" in params and isinstance(params.get("citation_style"), str):
        norm = _normalize_enum("citation_style", params["citation_style"])
        if norm not in _ENUM_NORMALIZERS["citation_style"].values():
            raise ValueError(f"Unsupported citation_style: {params['citation_style']}")

    # Optional: check document_type when present
    if "document_type" in params and isinstance(params.get("document_type"), str):
        norm = _normalize_enum("document_type", params["document_type"])
        if norm not in _ENUM_NORMALIZERS["document_type"].values():
            raise ValueError(f"Unsupported document_type: {params['document_type']}")
