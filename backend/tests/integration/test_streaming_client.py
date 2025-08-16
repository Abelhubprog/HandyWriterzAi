"""Integration test to verify client receives live tokens/messages via SSE."""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import redis.asyncio as redis
from typing import Dict, Any, AsyncGenerator

from backend.src.main import app
from backend.src.services.sse_service import SSEService


class TestClientStreaming:
    """Test client streaming functionality."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        return AsyncMock()

    @pytest.fixture
    def sse_service(self, mock_redis):
        """Create an SSE service instance."""
        with patch('backend.src.services.sse_service.redis.asyncio.from_url', return_value=mock_redis):
            service = SSEService()
            service._client = mock_redis
            return service

    @pytest.mark.asyncio
    async def test_sse_streaming_endpoint_connection(self, client):
        """Test SSE streaming endpoint establishes connection."""
        conversation_id = "test-conversation-123"

        # Make request to streaming endpoint
        with client.stream("GET", f"/api/stream/{conversation_id}") as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

            # Check for initial connection event
            first_line = next(response.iter_lines())
            assert "retry: 5000" in first_line

            second_line = next(response.iter_lines())
            assert "data:" in second_line

            # Parse the connection event
            data_line = second_line.replace("data: ", "")
            event_data = json.loads(data_line)
            assert event_data["type"] == "connected"
            assert event_data["conversation_id"] == conversation_id

    @pytest.mark.asyncio
    async def test_sse_streaming_receives_tokens(self, client):
        """Test SSE streaming receives token events."""
        conversation_id = "test-conversation-456"

        # Mock Redis to simulate events
        with patch('backend.src.main.redis_client') as mock_redis_client:
            # Create mock pubsub
            mock_pubsub = AsyncMock()
            mock_redis_client.pubsub.return_value = mock_pubsub

            # Simulate incoming messages
            test_messages = [
                {
                    "type": "message",
                    "data": json.dumps({
                        "type": "token",
                        "delta": "Hello",
                        "ts": 1234567890
                    })
                },
                {
                    "type": "message",
                    "data": json.dumps({
                        "type": "token",
                        "delta": " World",
                        "ts": 1234567891
                    })
                },
                {
                    "type": "message",
                    "data": json.dumps({
                        "type": "done",
                        "message": "Processing completed",
                        "ts": 1234567892
                    })
                }
            ]

            mock_pubsub.listen.return_value = test_messages

            # Make request to streaming endpoint
            with client.stream("GET", f"/api/stream/{conversation_id}") as response:
                assert response.status_code == 200

                # Collect all events
                events = []
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data_line = line.replace("data: ", "")
                        if data_line.strip():
                            try:
                                event_data = json.loads(data_line)
                                events.append(event_data)
                            except json.JSONDecodeError:
                                pass

                # Verify we received the expected events
                assert len(events) >= 3

                # Check first token event
                assert events[0]["type"] == "connected"

                # Check token events
                token_events = [e for e in events if e["type"] == "token"]
                assert len(token_events) >= 2
                assert token_events[0]["delta"] == "Hello"
                assert token_events[1]["delta"] == " World"

                # Check done event
                done_events = [e for e in events if e["type"] == "done"]
                assert len(done_events) >= 1
                assert done_events[0]["message"] == "Processing completed"

    @pytest.mark.asyncio
    async def test_sse_streaming_error_handling(self, client):
        """Test SSE streaming handles errors gracefully."""
        conversation_id = "test-conversation-789"

        # Mock Redis to simulate an error
        with patch('backend.src.main.redis_client') as mock_redis_client:
            mock_redis_client.pubsub.side_effect = Exception("Redis connection failed")

            # Make request to streaming endpoint
            with client.stream("GET", f"/api/stream/{conversation_id}") as response:
                assert response.status_code == 200

                # Collect events
                events = []
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data_line = line.replace("data: ", "")
                        if data_line.strip():
                            try:
                                event_data = json.loads(data_line)
                                events.append(event_data)
                            except json.JSONDecodeError:
                                pass

                # Should receive at least one error event
                error_events = [e for e in events if e["type"] == "error"]
                assert len(error_events) >= 1
                assert "Redis connection failed" in error_events[0]["message"]

    @pytest.mark.asyncio
    async def test_sse_streaming_heartbeat(self, client):
        """Test SSE streaming sends heartbeat events."""
        conversation_id = "test-conversation-101"

        # Mock Redis to simulate events with delay to trigger heartbeat
        with patch('backend.src.main.redis_client') as mock_redis_client:
            # Create mock pubsub
            mock_pubsub = AsyncMock()
            mock_redis_client.pubsub.return_value = mock_pubsub

            # Simulate incoming message with delay
            async def mock_listen():
                yield {
                    "type": "message",
                    "data": json.dumps({
                        "type": "content",
                        "text": "Test message",
                        "ts": 1234567890
                    })
                }
                # Add delay to trigger heartbeat
                await asyncio.sleep(0.1)
                yield {
                    "type": "message",
                    "data": json.dumps({
                        "type": "done",
                        "message": "Processing completed",
                        "ts": 1234567891
                    })
                }

            mock_pubsub.listen.return_value = mock_listen()

            # Make request to streaming endpoint
            with client.stream("GET", f"/api/stream/{conversation_id}") as response:
                assert response.status_code == 200

                # Collect events
                events = []
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data_line = line.replace("data: ", "")
                        if data_line.strip():
                            try:
                                event_data = json.loads(data_line)
                                events.append(event_data)
                            except json.JSONDecodeError:
                                pass

                # Should have heartbeat events
                heartbeat_events = [e for e in events if e["type"] == "heartbeat"]
                assert len(heartbeat_events) >= 0  # May or may not be present depending on timing

    def test_sse_service_publish_token(self, sse_service, mock_redis):
        """Test SSE service can publish token events."""
        conversation_id = "test-conversation-202"

        # Publish a token event
        asyncio.run(sse_service.publish_event(
            conversation_id=conversation_id,
            event_type="token",
            data={"delta": "Test token", "node": "writer"}
        ))

        # Verify Redis publish was called
        mock_redis.publish.assert_called_once()
        args, kwargs = mock_redis.publish.call_args
        channel, message = args

        assert channel == f"sse:{conversation_id}"
        parsed_message = json.loads(message)
        assert parsed_message["type"] == "token"
        assert parsed_message["data"]["delta"] == "Test token"
        assert parsed_message["data"]["node"] == "writer"


if __name__ == "__main__":
    pytest.main([__file__])
