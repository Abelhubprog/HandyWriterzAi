"""
User-facing credits endpoint: returns current user's credits balance and recent usage.
"""

from typing import Any, Dict
from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.services.credits_service import get_credits_service
from src.services.security_service import get_optional_user, get_current_user
from src.services.model_selector import get_model_selector, SelectionContext, SelectionStrategy

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/credits", tags=["credits"])


@router.get("/me")
async def get_my_credits(current_user: Dict[str, Any] = Depends(get_optional_user)):
    try:
        user_id = str(current_user.get("id") or current_user.get("user_id") or "anonymous")
        svc = get_credits_service()
        balance = await svc.get_balance(user_id)
        recent = await svc.get_recent_usage(user_id, limit=10)
        return {
            "success": True,
            "data": {**balance, "recent_usage": recent},
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to fetch credits for current user: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch credits")


class EstimateMessage(BaseModel):
    role: str = Field(..., pattern=r"^(user|assistant|system)$")
    content: str


class EstimateRequest(BaseModel):
    node_name: str = Field("chat_stream")
    messages: list[EstimateMessage]
    capabilities: list[str] = Field(default_factory=list)
    max_output_tokens: int | None = Field(default=None, ge=1, le=64000)
    strategy: SelectionStrategy = SelectionStrategy.BALANCED


@router.post("/estimate")
async def estimate_credits(
    body: EstimateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Estimate tokens, cost, credits, and whether the user has enough remaining today."""
    try:
        user_id = str(current_user.get("id") or current_user.get("user_id") or "anonymous")

        # Rough token estimate: chars/4
        total_chars = sum(len(m.content or "") for m in body.messages)
        est_input_tokens = max(1, total_chars // 4)
        est_output_tokens = body.max_output_tokens or 1000

        # Select model based on node/capabilities and token context
        selector = get_model_selector()
        sel = await selector.select_model(
            SelectionContext(
                node_name=body.node_name,
                capabilities=body.capabilities,
                user_id=user_id,
                strategy=body.strategy,
                estimated_tokens=est_input_tokens + est_output_tokens,
            )
        )
        model = sel.selected_model

        # Cost estimate
        input_cost = (est_input_tokens * model.input_cost_per_1k) / 1000.0
        output_cost = (est_output_tokens * model.output_cost_per_1k) / 1000.0
        est_cost_usd = float(input_cost + output_cost)
        credits_needed = int(est_cost_usd / 0.001 + 0.999) if est_cost_usd > 0 else 0

        # Remaining credits
        svc = get_credits_service()
        balance = await svc.get_balance(user_id)
        remaining = int(balance.get("remaining_today_credits", 0))
        allowed = remaining >= credits_needed

        return {
            "success": True,
            "data": {
                "model": {
                    "logical_id": model.logical_id,
                    "provider": model.provider.value,
                    "provider_model_id": model.provider_model_id,
                    "context_window": model.context_window,
                    "input_cost_per_1k": model.input_cost_per_1k,
                    "output_cost_per_1k": model.output_cost_per_1k,
                },
                "estimated": {
                    "input_tokens": est_input_tokens,
                    "output_tokens": est_output_tokens,
                    "cost_usd": est_cost_usd,
                    "credits": credits_needed,
                    "allowed": allowed,
                    "remaining_today_credits": remaining,
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to estimate credits: {e}")
        raise HTTPException(status_code=500, detail="Failed to estimate credits")
