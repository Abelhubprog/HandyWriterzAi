import asyncio
import json
import os
import sys
import pytest

# Ensure 'src' package is importable when running tests directly
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.services.sse_service import SSEService


class FakeRedis:
    def __init__(self):
        self.published = []  # list of (channel, message)

    async def publish(self, channel, message):
        self.published.append((channel, message))


@pytest.mark.asyncio
async def test_publish_event_adds_ts_and_channel_namespace():
    fake = FakeRedis()
    svc = SSEService(fake)  # type: ignore[arg-type]

    await svc.publish_event("cid-123", "content", {"token": "hello"})

    assert len(fake.published) == 1
    channel, msg = fake.published[0]
    assert channel == "sse:unified:cid-123"
    data = json.loads(msg)
    assert data["type"] == "content"
    assert data["token"] == "hello"
    assert "ts" in data


@pytest.mark.asyncio
async def test_publish_file_processing_helper_builds_payload():
    fake = FakeRedis()
    svc = SSEService(fake)  # type: ignore[arg-type]

    await svc.publish_file_processing("abc", status="processing_files", extra={"count": 2})

    assert len(fake.published) == 1
    channel, msg = fake.published[0]
    assert channel == "sse:unified:abc"
    data = json.loads(msg)
    assert data["type"] == "files:status"
    assert data["status"] == "processing_files"
    assert data["extra"]["count"] == 2
    assert "ts" in data
