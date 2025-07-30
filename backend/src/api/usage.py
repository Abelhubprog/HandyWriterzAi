import logging
from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..services.security_service import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

class DailyUsage(BaseModel):
    date: str
    usd: float
    tokens: int

class UsageData(BaseModel):
    daily: List[DailyUsage]

@router.get("/usage", response_model=UsageData)
async def get_usage_data(
    window: str = "30d",
    current_user: dict = Depends(get_current_user)
):
    """Get usage data for the current user."""
    # Placeholder implementation
    logger.info(f"Fetching usage data for user {current_user.get('id')} with window {window}")
    return UsageData(
        daily=[
            DailyUsage(date="2025-07-17", usd=2.50, tokens=50000),
            DailyUsage(date="2025-07-16", usd=1.75, tokens=35000)
        ]
    )
