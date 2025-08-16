"""
CreditsService: simple credits/billing tracker backed by Redis.

Units: 1 credit = $0.001 USD. Prices in price_table remain USD per 1k tokens.
This service exposes read APIs used by admin endpoints and provides
helpers for recording usage. In production, replace with persistent billing.
"""

from __future__ import annotations

import os
import json
import time
from typing import Any, Dict, List, Optional
import logging

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class CreditsService:
    def __init__(self, redis_url: Optional[str] = None):
        url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self._r = aioredis.from_url(url, decode_responses=True)
        # Defaults per tier (credits per day)
        self._tier_limits = {
            "free": 500,          # ~$0.50/day
            "pro": 5000,          # ~$5/day
            "enterprise": 50000   # ~$50/day
        }

    async def get_user_tier(self, user_id: str) -> str:
        tier = await self._r.get(f"credits:tier:{user_id}")
        return tier or os.getenv("DEFAULT_CREDITS_TIER", "free")

    def _today_key(self) -> str:
        return time.strftime("%Y-%m-%d")

    async def get_daily_limit(self, user_id: str) -> int:
        tier = await self.get_user_tier(user_id)
        return int(self._tier_limits.get(tier, self._tier_limits["free"]))

    async def get_remaining_today(self, user_id: str) -> int:
        today = self._today_key()
        used = await self._r.get(f"credits:used:{user_id}:{today}")
        used_int = int(used) if used and str(used).isdigit() else 0
        pending = await self._r.get(f"credits:pending:{user_id}:{today}")
        pending_int = int(pending) if pending and str(pending).isdigit() else 0
        limit = await self.get_daily_limit(user_id)
        return max(0, limit - used_int - pending_int)

    async def get_balance(self, user_id: str) -> Dict[str, Any]:
        tier = await self.get_user_tier(user_id)
        daily_limit = await self.get_daily_limit(user_id)
        remaining = await self.get_remaining_today(user_id)
        return {
            "user_id": user_id,
            "tier": tier,
            "daily_limit_credits": daily_limit,
            "remaining_today_credits": remaining,
        }

    async def set_user_tier(self, user_id: str, tier: str) -> None:
        allowed = set(self._tier_limits.keys())
        if tier not in allowed:
            raise ValueError(f"Invalid tier '{tier}'. Allowed: {sorted(allowed)}")
        await self._r.set(f"credits:tier:{user_id}", tier)

    async def record_usage(
        self,
        user_id: str,
        *,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        credits: int,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append a usage line item and increment today's usage. Safe to call best-effort."""
        try:
            today = self._today_key()
            await self._r.incrby(f"credits:used:{user_id}:{today}", int(credits))
            item = {
                "ts": time.time(),
                "model": model,
                "input_tokens": int(input_tokens),
                "output_tokens": int(output_tokens),
                "cost_usd": float(cost_usd),
                "credits": int(credits),
            }
            if meta:
                item["meta"] = meta
            await self._r.lpush(f"credits:usage:{user_id}", json.dumps(item))
            # Cap history length
            await self._r.ltrim(f"credits:usage:{user_id}", 0, 199)
        except Exception as e:
            logger.warning(f"Credits record_usage failed: {e}")

    async def get_recent_usage(self, user_id: str, limit: int = 25) -> List[Dict[str, Any]]:
        try:
            raw = await self._r.lrange(f"credits:usage:{user_id}", 0, max(0, limit - 1))
            out: List[Dict[str, Any]] = []
            for r in raw:
                try:
                    out.append(json.loads(r))
                except Exception:
                    continue
            return out
        except Exception as e:
            logger.warning(f"Credits get_recent_usage failed: {e}")
            return []

    # Reservation workflow -------------------------------------------------
    async def reserve_credits(self, user_id: str, trace_id: str, credits: int, ttl_seconds: int = 600) -> bool:
        """Reserve credits if available; returns True if reserved."""
        if credits <= 0:
            return True
        remaining = await self.get_remaining_today(user_id)
        if remaining < credits:
            return False
        today = self._today_key()
        # Increment pending and set reservation key
        await self._r.incrby(f"credits:pending:{user_id}:{today}", credits)
        await self._r.setex(f"credits:resv:{user_id}:{trace_id}", ttl_seconds, str(credits))
        return True

    async def commit_reservation(
        self,
        user_id: str,
        trace_id: str,
        *,
        final_credits: int,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Commit a reservation: move reserved -> used, adjust pending, and store item. Returns updated balance info."""
        today = self._today_key()
        try:
            reserved_raw = await self._r.get(f"credits:resv:{user_id}:{trace_id}")
            reserved = int(reserved_raw) if reserved_raw and reserved_raw.isdigit() else 0
        except Exception:
            reserved = 0
        # Decrement pending by reserved
        if reserved:
            try:
                await self._r.decrby(f"credits:pending:{user_id}:{today}", reserved)
            except Exception:
                pass

        # Record final usage
        await self.record_usage(
            user_id=user_id,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            credits=final_credits,
            meta=meta,
        )

        # Cleanup reservation key
        try:
            await self._r.delete(f"credits:resv:{user_id}:{trace_id}")
        except Exception:
            pass

        # Return updated remaining
        remaining = await self.get_remaining_today(user_id)
        return {"remaining_today_credits": remaining, "final_credits": final_credits}

    async def release_reservation(self, user_id: str, trace_id: str) -> None:
        """Release a reservation back to remaining (e.g., on error)."""
        today = self._today_key()
        try:
            reserved_raw = await self._r.get(f"credits:resv:{user_id}:{trace_id}")
            reserved = int(reserved_raw) if reserved_raw and reserved_raw.isdigit() else 0
            if reserved:
                try:
                    await self._r.decrby(f"credits:pending:{user_id}:{today}", reserved)
                except Exception:
                    pass
            await self._r.delete(f"credits:resv:{user_id}:{trace_id}")
        except Exception as e:
            logger.warning(f"Credits release_reservation failed: {e}")


_credits_singleton: Optional[CreditsService] = None


def get_credits_service() -> CreditsService:
    global _credits_singleton
    if _credits_singleton is None:
        _credits_singleton = CreditsService()
    return _credits_singleton
