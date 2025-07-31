from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class Preferences:
    exclude_quotes: bool = True
    exclude_bibliography: bool = True


@dataclass
class JobMetadata:
    job_id: str
    requester_id: Optional[str] = None
    callback_url: Optional[str] = None
    email_to: List[str] = field(default_factory=list)
    preferences: Preferences = field(default_factory=Preferences)


@dataclass
class Artifacts:
    input_doc_uri: str
    plag_pdf_uri: Optional[str] = None
    ai_pdf_uri: Optional[str] = None
    hashes: Dict[str, str] = field(default_factory=dict)
    sizes: Dict[str, int] = field(default_factory=dict)


@dataclass
class Manifest:
    job_id: str
    created_at: datetime
    preferences: Preferences
    artifacts: Artifacts
    summary: Dict[str, Optional[str]] = field(default_factory=dict)


@dataclass
class SessionStatus:
    healthy: bool
    reason: Optional[str] = None
