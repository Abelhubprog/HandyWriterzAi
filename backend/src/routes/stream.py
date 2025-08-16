from fastapi import APIRouter, Depends
from sse_starlette import EventSourceResponse
from typing import AsyncGenerator, Dict, Any, Optional
import asyncio
import json
import time
import logging

import redis.asyncio as aioredis
from ..services.sse_service import initialize_redis
from datetime import datetime
import uuid as _uuid
import io, csv
try:
    from src.db.database import db_manager  # type: ignore
    from src.db.models import TimelineEventModel  # type: ignore
except Exception:
    db_manager = None  # type: ignore
    TimelineEventModel = None  # type: ignore

router = APIRouter(prefix="/api/stream", tags=["stream"])
logger = logging.getLogger(__name__)

# In-memory replay buffer per conversation (simple ring)
REPLAY_MAX = 50
_replay_buffers: Dict[str, list[str]] = {}


def _normalize_payload(conversation_id: str, data: str) -> str:
    """Normalize incoming message JSON string to minimal envelope and inject conversation_id.

    - Flattens legacy envelopes of shape {type, timestamp, data: {...}}
    - Ensures 'conversation_id' is present in the final object
    - Returns a JSON string; on parse errors returns original data
    """
    try:
        obj = json.loads(data)
        if isinstance(obj, dict) and "data" in obj and isinstance(obj.get("data"), dict):
            flat = {"type": obj.get("type", "content"), **obj["data"]}
            ts = obj.get("timestamp") or obj.get("ts")
            if ts is not None:
                flat["ts"] = ts
            obj = flat
        if isinstance(obj, dict) and "conversation_id" not in obj:
            obj["conversation_id"] = conversation_id
        return json.dumps(obj)
    except Exception:
        return data


async def _subscribe_and_stream(conversation_id: str) -> AsyncGenerator[str, None]:
    client: aioredis.Redis = await initialize_redis()
    unified_channel = f"sse:unified:{conversation_id}"
    legacy_channel = f"sse:{conversation_id}"

    pubsub = client.pubsub()
    await pubsub.subscribe(unified_channel, legacy_channel)

    last_emit_ts = time.time()
    heartbeat_interval = 20.0

    # Send connected event and flush replay buffer (include conversation_id)
    yield json.dumps({"type": "connected", "ts": time.time(), "conversation_id": conversation_id})
    # First attempt to pull from Redis replay list
    try:
        replay = await client.lrange(f"sse:replay:{conversation_id}", 0, REPLAY_MAX - 1)
        for m in reversed(replay):  # Oldest first
            try:
                yield _normalize_payload(conversation_id, m)
            except Exception:
                yield m
    except Exception:
        pass
    # Then include in-memory buffer if any
    buf = _replay_buffers.get(conversation_id, [])
    if buf:
        for m in buf[-REPLAY_MAX:]:
            yield m

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            now = time.time()

            if message and message.get("type") == "message":
                raw = message.get("data")
                # Ensure string
                data = (
                    raw if isinstance(raw, str)
                    else raw.decode("utf-8") if isinstance(raw, (bytes, bytearray))
                    else json.dumps(raw)
                )
                # Normalize to minimal envelope and inject conversation_id
                data = _normalize_payload(conversation_id, data)
                # Cache to replay buffer
                rb = _replay_buffers.setdefault(conversation_id, [])
                rb.append(data)
                if len(rb) > REPLAY_MAX:
                    del rb[0:len(rb)-REPLAY_MAX]

                last_emit_ts = now
                yield data
                continue

            # Heartbeat when idle
            if now - last_emit_ts >= heartbeat_interval:
                last_emit_ts = now
                yield json.dumps({"type": "heartbeat", "ts": now, "conversation_id": conversation_id})

            await asyncio.sleep(0.05)

    except asyncio.CancelledError:
        # Client disconnected
        pass
    except Exception as e:
        logger.error(f"SSE stream error for {conversation_id}: {e}")
        yield json.dumps({"type": "error", "message": str(e), "ts": time.time(), "conversation_id": conversation_id})
    finally:
        try:
            await pubsub.unsubscribe(unified_channel, legacy_channel)
            await pubsub.close()
        except Exception:
            pass


@router.get("/{conversation_id}")
async def stream(conversation_id: str):
    async def event_generator():
        async for msg in _subscribe_and_stream(conversation_id):
            # The SSE protocol expects 'data:' lines per event; EventSourceResponse wraps automatically
            yield {
                "event": "message",
                "data": msg,
            }

    return EventSourceResponse(event_generator())


@router.get("/{conversation_id}/replay")
async def get_replay(conversation_id: str, limit: int = 200):
    """Return a JSON array of recent normalized events for the conversation.

    Useful for clients that want a snapshot without opening SSE.
    """
    client: aioredis.Redis = await initialize_redis()
    try:
        raw = await client.lrange(f"sse:replay:{conversation_id}", 0, max(0, min(limit, REPLAY_MAX) - 1))
        out = []
        for m in reversed(raw):
            try:
                out.append(json.loads(_normalize_payload(conversation_id, m)))
            except Exception:
                try:
                    out.append(json.loads(m))
                except Exception:
                    out.append({"type": "raw", "data": m, "conversation_id": conversation_id})
        return {"conversation_id": conversation_id, "events": out}
    except Exception as e:
        logger.error(f"Failed to get replay for {conversation_id}: {e}")
        return {"conversation_id": conversation_id, "events": []}
