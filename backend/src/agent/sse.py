"""
Unified SSE Publisher (Phase 0 scaffolding)

Non-breaking shim to standardize event publishing while keeping legacy Redis JSON strings.
Feature-gated usage occurs in UnifiedProcessor; this module must be import-safe.
"""

from __future__ import annotations
from typing import Any, Dict, Optional
import json
import time

try:
    import redis.asyncio as redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


class SSEPublisher:
    """
    Unified SSE publisher interface.

    In this initial scaffold:
    - If async_redis is provided, we also publish to a namespaced channel to support consumers
      that expect a unified envelope. Legacy publishing remains in callers.
    - If async_redis is None, publish() becomes a no-op to avoid breaking imports.
    """

    def __init__(self, async_redis: Optional["redis.Redis"] = None, namespace: str = "sse"):  # type: ignore[name-defined]
        self._r = async_redis
        self._ns = namespace

    async def publish(self, conversation_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """
        Publish a JSON event envelope to a unified channel.

        Envelope:
          {
            "type": "<event_type>",
            "timestamp": <epoch_seconds>,
            "data": { ...original data... }
          }
        """
        if not self._r:
            return

        channel = f"{self._ns}:{conversation_id}"
        envelope = {
            "type": event_type,
            "timestamp": time.time(),
            "data": data or {},
        }
        try:
            await self._r.publish(channel, json.dumps(envelope))
        except Exception:
            # Non-fatal: preserve do-not-harm behavior
            return
