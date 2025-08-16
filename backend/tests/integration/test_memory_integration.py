"""Integration tests for memory persistence functionality."""

import pytest
import asyncio
from unittest.mock import Mock, patch
from typing import Dict, Any

from backend.src.agent.nodes.memory_demo_agent import MemoryDemoAgent
from backend.src.agent.handywriterz_state import HandyWriterzState


class TestMemoryIntegration:
    """Test memory integration functionality."""

    @pytest.fixture
    def sample_state(self) -> HandyWriterzState:
        """Create a sample state for testing."""
        return HandyWriterzState(
            conversation_id="test-conversation-123",
            user_id="test-user-456",
            user_params={
                "user_prompt": "Write an essay about AI ethics",
                "word_count": 1000,
                "field": "computer_science"
            },
            retrieved_memories=[
                {"content": "User prefers technical writing style", "importance_score": 0.8},
                {"content": "User has background in ethics", "importance_score": 0.7}
            ]
        )

    @pytest.mark.asyncio
    async def test_memory_demo_agent_receive_input(self, sample_state: HandyWriterzState):
        """Test that the memory demo agent correctly receives input."""
        agent = MemoryDemoAgent()

        input_data = await agent.receive_input(sample_state)

        assert input_data["user_id"] == "test-user-456"
        assert input_data["conversation_id"] == "test-conversation-123"
        assert input_data["user_prompt"] == "Write an essay about AI ethics"
        assert len(input_data["previous_memories"]) == 2

    @pytest.mark.asyncio
    async def test_memory_demo_agent_process(self):
        """Test that the memory demo agent correctly processes input."""
        agent = MemoryDemoAgent()

        input_data = {
            "user_id": "test-user-456",
            "conversation_id": "test-conversation-123",
            "user_prompt": "Write an essay about AI ethics",
            "previous_memories": [
                {"content": "User prefers technical writing style", "importance_score": 0.8}
            ]
        }

        processed_data = await agent.process(input_data)

        assert "demo_memory_content" in processed_data
        assert "User interaction: Write an essay about AI ethics" in processed_data["demo_memory_content"]
        assert "Previous context: 1 memories retrieved" in processed_data["demo_memory_content"]
        assert processed_data["memory_type"] == "episodic"

    @pytest.mark.asyncio
    async def test_memory_demo_agent_emit_output(self, sample_state: HandyWriterzState):
        """Test that the memory demo agent correctly emits output."""
        agent = MemoryDemoAgent()

        processed_data = {
            "demo_memory_content": "User interaction: Write an essay about AI ethics | Previous context: 2 memories retrieved",
            "user_id": "test-user-456",
            "conversation_id": "test-conversation-123",
            "memory_type": "episodic"
        }

        output_data = await agent.emit_output(processed_data, sample_state)

        assert output_data["memory_demo_complete"] is True
        assert "demo_memory_result" in output_data
        assert "User interaction: Write an essay about AI ethics" in output_data["demo_memory_result"]
        assert output_data["memory_type"] == "episodic"

    @pytest.mark.asyncio
    async def test_memory_demo_agent_full_execution(self, sample_state: HandyWriterzState):
        """Test the full execution flow of the memory demo agent."""
        agent = MemoryDemoAgent()

        result = await agent.execute(sample_state, {})

        assert result["memory_demo_complete"] is True
        assert "demo_memory_result" in result
        assert "User interaction:" in result["demo_memory_result"]
        assert result["memory_type"] == "episodic"


if __name__ == "__main__":
    pytest.main([__file__])
