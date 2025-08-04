from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.db.database import get_db
# VectorEvidenceMap actually lives in vector storage service schema
from src.services.vector_storage import VectorEvidenceMap

router = APIRouter(
    prefix="/api",
    tags=["evidence"],
)

@router.get("/evidence")
def get_evidence(citeKey: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Fetches evidence for a given citation key.
    """
    evidence = db.query(VectorEvidenceMap).filter(VectorEvidenceMap.source_id == citeKey).first()

    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    return {
        "title": "Placeholder Title",  # TODO: join with documents table to fetch real title
        "paragraph": evidence.evidence_text,
        "url": "http://example.com"  # TODO: include actual source URL if available
    }
