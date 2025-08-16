"""Budget enforcement utilities for Autonomy V2.

Enforces token/time budgets based on settings. On exceed, routes END via caller.
"""

import time
from typing import Any, Dict, Optional
from backend.src.config import get_settings  # type: ignore
from ..memory.episodic_repo import EpisodicRepo


class BudgetGuard:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.start_ts = time.time()
        s = get_settings()
        self.limit_tokens = int(getattr(s, "v2_budget_tokens", 0)) or 200_000
        self.limit_seconds = int(getattr(s, "v2_budget_seconds", 0)) or 900
        self.limit_usd = float(getattr(s, "v2_budget_usd", 0.0)) or 0.0

    async def tick(self, state: Any, tokens_used: int = 0, usd_used: float = 0.0) -> bool:
        """Update counters and return True if still under budget, else False."""
        # Update state counters
        state.budget_tokens = int((state.budget_tokens or 0) + tokens_used)
        elapsed = time.time() - self.start_ts
        state.budget_seconds = int(elapsed)
        try:
            state.budget_usd = float((state.budget_usd or 0.0) + float(usd_used))
        except Exception:
            pass

        exceeded = False
        if state.budget_tokens > self.limit_tokens or state.budget_seconds > self.limit_seconds:
            exceeded = True
        if self.limit_usd and (state.budget_usd or 0.0) > self.limit_usd:
            exceeded = True

        if exceeded:
            # Log event
            try:
                await EpisodicRepo(run_id=self.run_id).write_event(self.run_id, "note", {
                    "event": "budget_exceeded",
                    "tokens": state.budget_tokens,
                    "seconds": state.budget_seconds,
                    "usd": state.budget_usd,
                })
            except Exception:
                pass
            return False
        return True
