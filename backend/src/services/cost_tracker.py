"""
Lightweight cost tracking utility used by the LLM gateway.

In development it acts as a no-op recorder to avoid DB dependencies.
"""

from typing import Dict, Any
import threading


class CostTracker:
    """In-memory cost tracker (dev-safe)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._totals: Dict[str, float] = {}
        self._requests: int = 0

    def record(self, *, user_id: str, model: str, input_tokens: int, output_tokens: int, cost_usd: float) -> None:
        with self._lock:
            self._requests += 1
            self._totals[model] = self._totals.get(model, 0.0) + float(cost_usd)

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "requests": self._requests,
                "by_model_usd": dict(self._totals),
                "total_usd": sum(self._totals.values()),
            }

    def reset(self) -> None:
        with self._lock:
            self._requests = 0
            self._totals.clear()

