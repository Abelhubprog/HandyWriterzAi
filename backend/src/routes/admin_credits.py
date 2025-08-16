"""
Admin Credits API: fetch balances and recent usage for a user.
"""

from typing import Any, Dict
from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.services.credits_service import get_credits_service
from src.services.security_service import require_authorization

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/credits", tags=["admin", "credits"])


@router.get("/{user_id}")
async def get_user_credits(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_authorization("admin_access"))
):
    """Return credits balance and recent usage for the given user."""
    try:
        svc = get_credits_service()
        balance = await svc.get_balance(user_id)
        recent = await svc.get_recent_usage(user_id, limit=25)
        return {
            "success": True,
            "data": {
                **balance,
                "recent_usage": recent,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to fetch credits for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch credits: {str(e)}",
        )


class TierUpdateRequest(BaseModel):
    tier: str = Field(..., pattern=r"^(free|pro|enterprise)$")


@router.put("/{user_id}/tier")
async def set_user_tier(
    user_id: str,
    body: TierUpdateRequest,
    current_user: Dict[str, Any] = Depends(require_authorization("admin_access"))
):
    """Set a user's credits tier (free|pro|enterprise)."""
    try:
        svc = get_credits_service()
        await svc.set_user_tier(user_id, body.tier)
        balance = await svc.get_balance(user_id)
        return {
            "success": True,
            "data": balance,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to set tier for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update tier")
