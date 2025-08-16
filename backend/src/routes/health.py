import os
import time
import logging
from typing import Dict

from fastapi import APIRouter

from src.services.sse_service import get_sse_service
from src.db.database import db_manager

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def health_ready() -> Dict[str, str]:
    redis_status = "error"
    db_status = "error"

    # Redis check via SSEService
    try:
        sse = get_sse_service()
        ok = await sse.ping()
        redis_status = "ok" if ok else "error"
    except Exception as e:
        logger.warning(f"Health redis ping failed: {e}")
        redis_status = "error"

    # DB check
    try:
        db_ok = db_manager.health_check()
        db_status = "ok" if db_ok else "error"
    except Exception as e:
        logger.warning(f"Health DB check failed: {e}")
        db_status = "error"

    version = os.getenv("COMMIT_SHA") or os.getenv("RELEASE") or "dev"

    return {"redis": redis_status, "db": db_status, "version": version}

