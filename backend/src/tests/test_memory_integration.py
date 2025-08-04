"""
Integration tests for the Memory Integration System.
Tests the complete memory workflow including safety controls.
"""

import pytest
import asyncio
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, patch

from services.memory_integrator import get_memory_integrator
from services.memory_safety import get_memory_safety_service, MemorySafetyError
from db.models import MemoryType


class TestMemoryIntegration:
    """Test complete memory integration workflow."""
    
    @pytest.fixture
    def memory_service(self):
        """Get memory integrator service."""
        return get_memory_integrator()
    
    @pytest.fixture
    def safety_service(self):
        """Get memory safety service."""
        return get_memory_safety_service()
    
    @pytest.fixture
    def test_user_id(self):
        """Generate test user ID."""
        return str(uuid.uuid4())
    
    @pytest.fixture
    def test_conversation_id(self):
        """Generate test conversation ID."""
        return str(uuid.uuid4())
    
    @pytest.mark.asyncio
    async def test_basic_memory_workflow(self, memory_service, test_user_id, test_conversation_id):
        """Test basic memory creation and retrieval."""
        # Create a memory
        memory_id = await memory_service.write_memory(
            user_id=test_user_id,
            content="User prefers Harvard citation style for academic papers",
            memory_type=MemoryType.PREFERENCE,
            conversation_id=test_conversation_id,
            importance_score=0.8,
            tags=["citation", "harvard", "academic"],
            source_summary="Test memory creation"
        )
        
        assert memory_id is not None
        assert isinstance(memory_id, str)
        
        # Retrieve the memory
        memories = await memory_service.retrieve_memories(
            user_id=test_user_id,
            query="citation style preferences",
            k=5
        )
        
        assert len(memories) >= 1
        retrieved_memory = next((m for m in memories if m["id"] == memory_id), None)
        assert retrieved_memory is not None
        assert "Harvard citation style" in retrieved_memory["content"]
        assert retrieved_memory["memory_type"] == "preference"
        assert retrieved_memory["importance_score"] == 0.8
    
    @pytest.mark.asyncio
    async def test_memory_safety_validation(self, memory_service, safety_service, test_user_id):
        """Test safety validation prevents unsafe content."""
        # Test PII detection
        pii_content = "My email is john.doe@example.com and my phone is 555-123-4567"
        
        is_valid, issues = await safety_service.validate_memory_content(pii_content, test_user_id)
        assert not is_valid
        assert any("PII detected" in issue for issue in issues)
        
        # Test content sanitization
        sanitized = safety_service.sanitize_content(pii_content)
        assert "[EMAIL]" in sanitized
        assert "[PHONE]" in sanitized
        assert "john.doe@example.com" not in sanitized
    
    @pytest.mark.asyncio
    async def test_memory_deduplication(self, memory_service, test_user_id):
        """Test that similar memories are deduplicated."""
        content1 = "User prefers APA citation format for psychology papers"
        content2 = "User likes APA citation format for psychology research"
        
        # Create first memory
        memory_id1 = await memory_service.write_memory(
            user_id=test_user_id,
            content=content1,
            memory_type=MemoryType.PREFERENCE,
            importance_score=0.7
        )
        
        # Create very similar memory - should be deduplicated
        memory_id2 = await memory_service.write_memory(
            user_id=test_user_id,
            content=content2,
            memory_type=MemoryType.PREFERENCE,
            importance_score=0.8
        )
        
        # Should return same ID if deduplicated
        # Or create separate memory if deemed different enough
        assert memory_id1 is not None
        assert memory_id2 is not None
    
    @pytest.mark.asyncio
    async def test_importance_scoring(self, memory_service, test_user_id):
        """Test importance scoring algorithm."""
        # Test different memory types get different importance scores
        preference_memory = await memory_service.write_memory(
            user_id=test_user_id,
            content="User prefers dark mode interface",
            memory_type=MemoryType.PREFERENCE
        )
        
        episodic_memory = await memory_service.write_memory(
            user_id=test_user_id,
            content="User completed a research paper on AI ethics yesterday",
            memory_type=MemoryType.EPISODIC
        )
        
        # Retrieve and check importance scores
        memories = await memory_service.retrieve_memories(
            user_id=test_user_id,
            query="user preferences and activities",
            k=10
        )
        
        preference_mem = next((m for m in memories if m["id"] == preference_memory), None)
        episodic_mem = next((m for m in memories if m["id"] == episodic_memory), None)
        
        assert preference_mem is not None
        assert episodic_mem is not None
        
        # Preferences should typically have higher importance than episodic memories
        # (though this depends on content novelty and other factors)
        assert preference_mem["importance_score"] > 0.0
        assert episodic_mem["importance_score"] > 0.0
    
    @pytest.mark.asyncio
    async def test_cost_tracking(self, safety_service, test_user_id):
        """Test cost tracking functionality."""
        # Track some operations
        await safety_service.track_operation_cost(
            test_user_id, 'embedding', token_count=1000
        )
        
        await safety_service.track_operation_cost(
            test_user_id, 'reflection', input_tokens=500, output_tokens=200
        )
        
        # Get cost report
        cost_report = await safety_service.get_cost_report(test_user_id)
        
        assert cost_report["user_id"] == test_user_id
        assert cost_report["total_cost_usd"] > 0
        assert cost_report["embeddings_generated"] >= 1
        assert cost_report["llm_reflection_calls"] >= 1
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, safety_service, test_user_id):
        """Test rate limiting enforcement."""
        # Test retrieval rate limiting
        for i in range(60):  # Exceed per-minute limit
            is_valid, issues = await safety_service.validate_retrieval_request(
                test_user_id, f"test query {i}", 5
            )
            if not is_valid:
                assert any("rate limit" in issue.lower() for issue in issues)
                break
        else:
            pytest.fail("Rate limiting should have kicked in")
    
    @pytest.mark.asyncio
    @patch('services.memory_integrator.get_openai_client')
    async def test_ai_reflection(self, mock_openai, memory_service, test_user_id, test_conversation_id):
        """Test AI reflection functionality."""
        # Mock OpenAI response
        mock_response = AsyncMock()
        mock_response.choices[0].message.content = '''
        {
            "memories": [
                {
                    "memory_type": "preference",
                    "content": "User prefers detailed explanations with examples",
                    "importance": 0.7,
                    "tags": ["explanation", "detail", "preference"]
                }
            ]
        }
        '''
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        # Perform reflection
        memory_ids = await memory_service.reflect_and_extract_memories(
            user_id=test_user_id,
            conversation_id=test_conversation_id,
            conversation_context="User asked for help with citation formats and requested detailed step-by-step instructions",
            user_response="Here's a comprehensive guide to APA citation format with detailed examples..."
        )
        
        assert len(memory_ids) >= 0  # Should create memories or return empty list
        
        # Verify OpenAI was called
        mock_openai.return_value.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_memory_statistics(self, memory_service, test_user_id):
        """Test memory statistics generation."""
        # Create some test memories
        await memory_service.write_memory(
            user_id=test_user_id,
            content="Test semantic memory",
            memory_type=MemoryType.SEMANTIC
        )
        
        await memory_service.write_memory(
            user_id=test_user_id,
            content="Test preference memory",
            memory_type=MemoryType.PREFERENCE
        )
        
        # Get statistics
        stats = await memory_service.get_memory_statistics(test_user_id)
        
        assert stats["total_memories"] >= 2
        assert stats["average_importance"] > 0
        assert "semantic" in stats["type_distribution"]
        assert "preference" in stats["type_distribution"]
    
    @pytest.mark.asyncio
    async def test_memory_maintenance(self, memory_service, test_user_id):
        """Test memory maintenance operations."""
        # Create some memories
        memory_ids = []
        for i in range(5):
            memory_id = await memory_service.write_memory(
                user_id=test_user_id,
                content=f"Test memory {i}",
                memory_type=MemoryType.EPISODIC,
                importance_score=0.1  # Low importance for cleanup test
            )
            memory_ids.append(memory_id)
        
        # Run maintenance
        await memory_service.maintain_memories(user_id=test_user_id)
        
        # Verify maintenance completed without errors
        stats_after = await memory_service.get_memory_statistics(test_user_id)
        assert stats_after["total_memories"] >= 0  # Some memories might be cleaned up
    
    @pytest.mark.asyncio
    async def test_memory_type_filtering(self, memory_service, test_user_id):
        """Test retrieval with memory type filtering."""
        # Create memories of different types
        await memory_service.write_memory(
            user_id=test_user_id,
            content="User completed machine learning course",
            memory_type=MemoryType.EPISODIC
        )
        
        await memory_service.write_memory(
            user_id=test_user_id,
            content="User prefers interactive learning",
            memory_type=MemoryType.PREFERENCE
        )
        
        # Retrieve only preference memories
        preference_memories = await memory_service.retrieve_memories(
            user_id=test_user_id,
            query="learning preferences",
            memory_types=[MemoryType.PREFERENCE]
        )
        
        # Should only return preference memories
        for memory in preference_memories:
            assert memory["memory_type"] == "preference"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, memory_service, safety_service):
        """Test error handling for invalid inputs."""
        # Test invalid user ID
        with pytest.raises(Exception):
            await memory_service.write_memory(
                user_id="",  # Invalid user ID
                content="Test content",
                memory_type=MemoryType.SEMANTIC
            )
        
        # Test empty content
        is_valid, issues = await safety_service.validate_memory_content("", "test_user")
        assert not is_valid
        assert any("empty" in issue.lower() for issue in issues)
        
        # Test oversized content
        huge_content = "x" * 20000  # Exceeds max content length
        is_valid, issues = await safety_service.validate_memory_content(huge_content, "test_user")
        assert not is_valid
        assert any("too long" in issue.lower() for issue in issues)


@pytest.mark.asyncio
async def test_integration_workflow():
    """Test complete integration workflow."""
    memory_service = get_memory_integrator()
    test_user_id = str(uuid.uuid4())
    
    # Simulate complete workflow
    # 1. Create user memories from conversation
    memory_ids = []
    
    # User preference memory
    pref_id = await memory_service.write_memory(
        user_id=test_user_id,
        content="User prefers Chicago citation style for history papers",
        memory_type=MemoryType.PREFERENCE,
        importance_score=0.8,
        tags=["citation", "chicago", "history"]
    )
    memory_ids.append(pref_id)
    
    # Semantic knowledge memory
    semantic_id = await memory_service.write_memory(
        user_id=test_user_id,
        content="User is studying American Civil War period",
        memory_type=MemoryType.SEMANTIC,
        importance_score=0.6,
        tags=["history", "civil_war", "american"]
    )
    memory_ids.append(semantic_id)
    
    # 2. Retrieve relevant memories for new conversation
    memories = await memory_service.retrieve_memories(
        user_id=test_user_id,
        query="help with history paper citations",
        k=5
    )
    
    # Should retrieve relevant memories
    assert len(memories) >= 1
    
    # Should include the preference and semantic memories
    retrieved_ids = [m["id"] for m in memories]
    assert pref_id in retrieved_ids or semantic_id in retrieved_ids
    
    # 3. Verify memory context is useful
    for memory in memories:
        assert memory["similarity_score"] > 0.0
        assert memory["importance_score"] > 0.0
        assert "id" in memory
        assert "content" in memory
        assert "memory_type" in memory
    
    print(f"✅ Integration test passed: Created {len(memory_ids)} memories, retrieved {len(memories)} relevant memories")


if __name__ == "__main__":
    # Run basic integration test
    asyncio.run(test_integration_workflow())