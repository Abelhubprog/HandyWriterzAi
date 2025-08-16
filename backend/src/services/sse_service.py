import os
import json
from typing import Any, Optional, Dict
import logging

import redis.asyncio as aioredis
from datetime import datetime
try:
    from src.db.database import db_manager  # type: ignore
    from src.db.models import TimelineEventModel  # type: ignore
except Exception:
    db_manager = None  # type: ignore
    TimelineEventModel = None  # type: ignore

logger = logging.getLogger(__name__)

# Global Redis client instance (singleton)
_redis_client: Optional[aioredis.Redis] = None
_sse_service_singleton: Optional["SSEService"] = None
_warned_default_redis_url = False

def _get_redis_url() -> str:
    """Retrieve Redis URL from environment; default to localhost in dev.

    Falls back to "redis://localhost:6379" if REDIS_URL is not set, logging once.
    """
    global _warned_default_redis_url
    url = os.getenv("REDIS_URL")
    if url:
        return url
    # Default for developer convenience
    url = "redis://localhost:6379"
    if not _warned_default_redis_url:
        logger.warning("[SSEService] REDIS_URL not set; defaulting to redis://localhost:6379")
        _warned_default_redis_url = True
    return url

async def initialize_redis() -> aioredis.Redis:
    """Create and cache a Redis client instance (idempotent)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(_get_redis_url(), decode_responses=True)
        try:
            await _redis_client.ping()
        except Exception as e:
            logger.warning(f"[SSEService] Redis ping failed during init: {e}")
    return _redis_client

async def close_redis():
    """Close the Redis connection gracefully."""
    global _redis_client
    if _redis_client is not None:
        try:
            await _redis_client.close()
        finally:
            _redis_client = None

class SSEService:
    """Simple wrapper around Redis Pub/Sub for SSE events."""

    def __init__(self, redis_client: aioredis.Redis):
        self._client = redis_client

    async def ping(self) -> bool:
        """Ping Redis to verify connectivity."""
        try:
            await self._client.ping()
            return True
        except Exception as e:
            logger.warning(f"[SSEService] ping failed: {e}")
            return False

    async def close(self) -> None:
        """Close underlying Redis client."""
        try:
            await self._client.close()
        except Exception as e:
            logger.warning(f"[SSEService] close encountered an issue: {e}")

    async def publish(self, channel: str, message: str) -> None:
        """Publish a raw message to a Redis channel."""
        try:
            await self._client.publish(channel, message)
        except Exception as e:
            logger.error(f"[SSEService] Failed to publish to {channel}: {e}")

    async def publish_event(self, conversation_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        """Publish a canonical event envelope to unified channel, include ts if missing."""
        evt = {
            "type": event_type,
            **payload,
        }
        if "ts" not in evt:
            import time
            evt["ts"] = time.time()
        channel = f"sse:unified:{conversation_id}"
        data = json.dumps(evt)
        await self.publish(channel, data)
        # Append to a small Redis replay list for the conversation
        try:
            replay_key = f"sse:replay:{conversation_id}"
            # Keep last 200 events
            await self._client.lpush(replay_key, data)
            await self._client.ltrim(replay_key, 0, 199)
        except Exception as e:
            logger.debug(f"[SSEService] replay buffer write failed: {e}")
        # Persist to DB for long-lived audit (best-effort, non-blocking)
        try:
            if db_manager and TimelineEventModel:
                with db_manager.get_db_context() as db:
                    ts_val = evt.get('ts')
                    ts_dt = None
                    try:
                        if isinstance(ts_val, (int, float)):
                            ts_dt = datetime.utcfromtimestamp(ts_val if ts_val > 1e12 else ts_val)
                        elif isinstance(ts_val, str):
                            ts_dt = datetime.fromisoformat(ts_val)
                    except Exception:
                        ts_dt = datetime.utcnow()
                    rec = TimelineEventModel(
                        conversation_id=conversation_id,
                        type=str(evt.get('type')),
                        agent=evt.get('agent'),
                        node=evt.get('node'),
                        ts=ts_dt or datetime.utcnow(),
                        payload=evt
                    )
                    db.add(rec)
        except Exception as e:
            logger.debug(f"[SSEService] DB persist failed: {e}")

    async def publish_workflow_progress(self, conversation_id: str, payload: Dict[str, Any]) -> None:
        """Helper to publish namespaced progress events."""
        evt_type = payload.get("type", "progress:update")
        await self.publish_event(conversation_id, evt_type, payload)

    async def publish_file_processing(self, conversation_id: str, *, status: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Publish standardized file-processing status events used by main.py.

        Args:
            conversation_id: Trace or conversation id used for SSE channel
            status: A status string like 'processing_files', 'files_processed', 'file_processing_error'
            extra: Optional dict with additional info to include
        """
        payload: Dict[str, Any] = {"status": status}
        if extra:
            payload["extra"] = extra
        await self.publish_event(conversation_id, "files:status", payload)

def get_sse_service() -> SSEService:
    """Return a singleton SSEService instance. Safe to call from sync/async contexts."""
    global _sse_service_singleton
    if _sse_service_singleton is None:
        # Create client without awaiting; the first async caller can call initialize_redis()
        client = aioredis.from_url(_get_redis_url(), decode_responses=True)
        _sse_service_singleton = SSEService(client)
    return _sse_service_singleton
