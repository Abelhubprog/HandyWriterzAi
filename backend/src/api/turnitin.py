from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, AnyHttpUrl
from typing import Optional, Dict, Any
from ..turnitin.models import JobMetadata, Preferences
from ..turnitin.orchestrator import get_orchestrator

router = APIRouter(prefix="/api/turnitin", tags=["turnitin"])


class StartTurnitinBody(BaseModel):
    input_doc_uri: AnyHttpUrl
    job: JobMetadata
    preferences: Optional[Preferences] = None
    extra: Optional[Dict[str, Any]] = None


@router.post("/start")
async def start_turnitin(payload: StartTurnitinBody):
    try:
        orchestrator = get_orchestrator()
        manifest = await orchestrator.start_turnitin_check(
            job=payload.job,
            input_doc_uri=str(payload.input_doc_uri),
            preferences=payload.preferences or Preferences(),
        )
        return {"ok": True, "manifest": manifest.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
