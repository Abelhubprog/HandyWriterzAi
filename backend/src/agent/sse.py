import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

try:
    # Prefer asyncio redis if available
    from redis.asyncio import Redis as AsyncRedis  # type: ignore
except Exception:  # pragma: no cover
    AsyncRedis = None  # type: ignore

try:
    # Fallback to sync redis (used only if double-publish enabled)
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SSEPublisher:
    """
    Unified SSE JSON publisher. Ensures all frames are strict JSON and carry
    canonical envelope fields: type, timestamp, conversation_id, payload, run_id.

    It publishes to Redis pub/sub channel: sse:{conversation_id}.
    When feature.double_publish_sse is enabled, it also publishes to
    sse_legacy:{conversation_id} using a sync client if available.
    """

    def __init__(
        self,
        async_redis: Optional["AsyncRedis"] = None,
        legacy_redis: Optional["redis.Redis"] = None,
        *,
        channel_prefix: str = "sse:",
        legacy_channel_prefix: str = "sse_legacy:",
        enable_double_publish: Optional[bool] = None,
    ) -> None:
        self.async_redis = async_redis
        self.legacy_redis = legacy_redis
        self.channel_prefix = channel_prefix
        self.legacy_channel_prefix = legacy_channel_prefix

        if enable_double_publish is None:
            # read from environment flag; default false
            enable_double_publish = os.getenv("FEATURE_DOUBLE_PUBLISH_SSE", "false").lower() == "true"
        self.enable_double_publish = enable_double_publish

    def _envelope(
        self,
        conversation_id: str,
        event_type: str,
        payload: Dict[str, Any],
        *,
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "type": event_type,
            "timestamp": _iso_now(),
            "conversation_id": conversation_id,
            "run_id": run_id,
            "payload": payload or {},
        }

    async def publish(
        self,
        conversation_id: str,
        event_type: str,
        payload: Dict[str, Any],
        *,
        run_id: Optional[str] = None,
    ) -> None:
        """
        Publish a canonical SSE frame to Redis. Uses asyncio client when available.
        Optionally double-publishes to a legacy channel for shadowing.
        """
        frame = self._envelope(conversation_id, event_type, payload, run_id=run_id)
        data = json.dumps(frame, ensure_ascii=False)

        # async path
        if self.async_redis is not None:
            await self.async_redis.publish(f"{self.channel_prefix}{conversation_id}", data)

        # optional legacy shadow publish
        if self.enable_double_publish and self.legacy_redis is not None:  # pragma: no cover
            try:
                self.legacy_redis.publish(f"{self.legacy_channel_prefix}{conversation_id}", data)
            except Exception:
                # Do not raise; logging is handled by caller or global logger
                pass

    # Convenience helpers
    async def start(self, conversation_id: str, message_preview: Optional[str] = None, *, run_id: Optional[str] = None) -> None:
        await self.publish(
            conversation_id,
            "start",
            {"messagePreview": (message_preview or "")[:200]},
            run_id=run_id,
        )

    async def routing(
        self,
        conversation_id: str,
        route: str,
        score: float,
        rationale: str,
        estimated_processing_seconds: Optional[float] = None,
        *,
        run_id: Optional[str] = None,
    ) -> None:
        await self.publish(
            conversation_id,
            "routing",
            {
                "route": route,
                "score": score,
                "rationale": rationale,
                "estimated_processing_seconds": estimated_processing_seconds,
            },
            run_id=run_id,
        )

    async def content(
        self,
        conversation_id: str,
        text: str,
        *,
        sources: Optional[list] = None,
        role: str = "assistant",
        run_id: Optional[str] = None,
    ) -> None:
        await self.publish(
            conversation_id,
            "content",
            {
                "text": text,
                "role": role,
                "sources": sources or [],
            },
            run_id=run_id,
        )

    async def done(
        self,
        conversation_id: str,
        *,
        summary: Optional[str] = None,
        tokens_used: Optional[Dict[str, int]] = None,
        run_id: Optional[str] = None,
    ) -> None:
        await self.publish(
            conversation_id,
            "done",
            {
                "final": True,
                "summary": (summary or "")[:500],
                "tokens_used": tokens_used or {},
            },
            run_id=run_id,
        )

    async def error(
        self,
        conversation_id: str,
        message: str,
        *,
        kind: str = "internal",
        retryable: bool = False,
        run_id: Optional[str] = None,
    ) -> None:
        await self.publish(
            conversation_id,
            "error",
            {
                "message": message,
                "kind": kind,
                "retryable": retryable,
            },
            run_id=run_id,
        )
