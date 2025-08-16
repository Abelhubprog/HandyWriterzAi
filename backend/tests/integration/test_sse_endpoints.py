"""Integration tests for SSE endpoints."""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from typing import Dict, Any, AsyncGenerator
import redis.asyncio as redis

from backend.src.agent.sse import SSEPublisher
from backend.src.agent.sse_unified import SSEPublisher as UnifiedSSEPublisher
from backend.src.services.sse_service import SSEService


class TestSSEEndpoints:
    """Test SSE endpoint functionality."""

    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        return AsyncMock()

    @pytest.fixture
    def sse_publisher(self, mock_redis):
        """Create an SSE publisher instance."""
        return SSEPublisher(async_redis=mock_redis)

    @pytest.fixture
    def unified_sse_publisher(self, mock_redis):
        """Create a unified SSE publisher instance."""
        return UnifiedSSEPublisher(redis_client=mock_redis)

    @pytest.fixture
    def sse_service(self, mock_redis):
        """Create an SSE service instance."""
        with patch('backend.src.services.sse_service.redis.asyncio.from_url', return_value=mock_redis):
            service = SSEService()
            service._client = mock_redis
            return service

    @pytest.mark.asyncio
    async def test_sse_publisher_basic_publish(self, sse_publisher, mock_redis):
        """Test basic SSE publishing functionality."""
        conversation_id = "test-conversation-123"
        event_type = "test_event"
        data = {"message": "Hello, World!", "count": 42}

        await sse_publisher.publish(conversation_id, event_type, data)

        # Verify Redis publish was called
        mock_redis.publish.assert_called_once()
        args, kwargs = mock_redis.publish.call_args
        channel, message = args

        assert channel == f"sse:test-conversation-123"

        # Verify message content
        parsed_message = json.loads(message)
        assert parsed_message["type"] == event_type
        assert parsed_message["data"] == data
        assert "timestamp" in parsed_message

    @pytest.mark.asyncio
    async def test_sse_publisher_no_redis(self):
        """Test SSE publisher behavior when Redis is not available."""
        publisher = SSEPublisher(async_redis=None)
        # Should not raise an exception
        await publisher.publish("test-conversation", "test_event", {"message": "test"})

    @pytest.mark.asyncio
    async def test_unified_sse_publisher_event_publish(self, unified_sse_publisher, mock_redis):
        """Test unified SSE publisher event publishing."""
        conversation_id = "test-conversation-456"

        # Test start event
        result = await unified_sse_publisher.publish_start(
            correlation_id=conversation_id,
            workflow_id="test-workflow",
            content_type="essay",
            complexity_score=0.8
        )

        # Should return True for successful queueing
        assert result is True

    @pytest.mark.asyncio
    async def test_unified_sse_publisher_content_publish(self, unified_sse_publisher, mock_redis):
        """Test unified SSE publisher content streaming."""
        conversation_id = "test-conversation-789"

        result = await unified_sse_publisher.publish_content(
            correlation_id=conversation_id,
            content="This is a test content chunk.",
            node_name="writer",
            phase="writing"
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_sse_service_publish(self, sse_service, mock_redis):
        """Test SSE service publish functionality."""
        conversation_id = "test-conversation-101"

        await sse_service.publish_event(
            conversation_id=conversation_id,
            event_type="content",
            data={"message": "Test message"}
        )

        # Verify Redis publish was called
        mock_redis.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_sse_service_heartbeat(self, sse_service, mock_redis):
        """Test SSE service heartbeat functionality."""
        conversation_id = "test-conversation-102"

        await sse_service.publish_heartbeat(conversation_id)

        # Verify Redis publish was called
        mock_redis.publish.assert_called_once()
        args, kwargs = mock_redis.publish.call_args
        channel, message = args

        assert channel == f"sse:{conversation_id}"
        parsed_message = json.loads(message)
        assert parsed_message["type"] == "heartbeat"

    @pytest.mark.asyncio
    async def test_sse_service_error_publish(self, sse_service, mock_redis):
        """Test SSE service error publishing."""
        conversation_id = "test-conversation-103"

        await sse_service.publish_error(
            conversation_id=conversation_id,
            error_code="TEST_ERROR",
            message="This is a test error message"
        )

        # Verify Redis publish was called
        mock_redis.publish.assert_called_once()
        args, kwargs = mock_redis.publish.call_args
        channel, message = args

        assert channel == f"sse:{conversation_id}"
        parsed_message = json.loads(message)
        assert parsed_message["type"] == "error"
        assert parsed_message["data"]["error_code"] == "TEST_ERROR"
        assert parsed_message["data"]["message"] == "This is a test error message"

    def test_sse_publisher_initialization(self):
        """Test SSE publisher initialization."""
        # Test with Redis
        mock_redis = Mock()
        publisher = SSEPublisher(async_redis=mock_redis)
        assert publisher._r == mock_redis

        # Test without Redis
        publisher = SSEPublisher(async_redis=None)
        assert publisher._r is None

    @pytest.mark.asyncio
    async def test_unified_sse_publisher_initialization(self, mock_redis):
        """Test unified SSE publisher initialization."""
        publisher = UnifiedSSEPublisher(
            redis_client=mock_redis,
            schema_validation=False,
            enable_legacy_publish=True
        )

        assert publisher.redis == mock_redis
        assert publisher.enable_legacy_publish is True

    @pytest.mark.asyncio
    async def test_sse_service_initialization(self):
        """Test SSE service initialization."""
        with patch('backend.src.services.sse_service.redis.asyncio.from_url') as mock_redis_from_url:
            mock_redis_client = AsyncMock()
            mock_redis_from_url.return_value = mock_redis_client

            service = SSEService()

            # Verify Redis client was created
            mock_redis_from_url.assert_called_once()
            assert service._client is None  # Lazy initialization

    @pytest.mark.asyncio
    async def test_sse_publisher_concurrent_publish(self, sse_publisher, mock_redis):
        """Test concurrent SSE publishing."""
        conversation_id = "test-conversation-concurrent"

        # Publish multiple events concurrently
        tasks = []
        for i in range(5):
            task = sse_publisher.publish(
                conversation_id,
                f"event_{i}",
                {"message": f"Message {i}", "index": i}
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(result is None for result in results)
        assert mock_redis.publish.call_count == 5

    @pytest.mark.asyncio
    async def test_unified_sse_publisher_metrics(self, unified_sse_publisher):
        """Test unified SSE publisher metrics."""
        metrics = await unified_sse_publisher.get_metrics()

        assert "events_published" in metrics
        assert "active_streams" in metrics
        assert "active_queues" in metrics
        assert "schema_validation_enabled" in metrics


if __name__ == "__main__":
    pytest.main([__file__])
