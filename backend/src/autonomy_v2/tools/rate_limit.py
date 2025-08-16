"""Adaptive rate limiting stubs (no external effects)."""

from time import monotonic


class TokenBucket:
    def __init__(self, rate_per_sec: float, capacity: float):
        self.rate = float(rate_per_sec)
        self.capacity = float(capacity)
        self.tokens = float(capacity)
        self.last = monotonic()

    def allow(self, cost: float = 1.0) -> bool:
        now = monotonic()
        delta = now - self.last
        self.last = now
        self.tokens = min(self.capacity, self.tokens + delta * self.rate)
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

