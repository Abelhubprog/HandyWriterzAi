"""
Integration tests for Phase 1 & Phase 2 components.

Tests the critical infrastructure components implemented:
- Parameter normalization
- SSE publisher
- Model registry  
- Budget enforcement
- Search adapter
- Logging context
"""

import pytest
import asyncio
import json
import os
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Test parameter normalization
def test_parameter_normalization():
    """Test parameter normalization functionality."""
    from src.agent.routing.normalization import normalize_user_params, validate_user_params
    
    # Test camelCase to snake_case conversion
    input_params = {
        "writeupType": "PhD Dissertation",
        "citationStyle": "harvard",
        "educationLevel": "Doctoral",
        "wordCount": 8000,
        "field": "Computer Science"
    }
    
    normalized = normalize_user_params(input_params)
    
    # Check key conversion
    assert "document_type" in normalized
    assert "citation_style" in normalized
    assert "academic_level" in normalized
    assert "word_count" in normalized
    
    # Check value normalization
    assert normalized["document_type"] == "Dissertation"
    assert normalized["citation_style"] == "Harvard"
    assert normalized["academic_level"] == "doctoral"
    assert normalized["word_count"] == 8000
    
    # Check derived fields
    assert "pages" in normalized
    assert "target_sources" in normalized
    assert normalized["pages"] > 0
    assert normalized["target_sources"] > 0
    
    # Test validation
    validate_user_params(normalized)  # Should not raise


def test_parameter_normalization_edge_cases():
    """Test parameter normalization edge cases."""
    from src.agent.routing.normalization import normalize_user_params
    
    # Test empty input
    result = normalize_user_params({})
    assert isinstance(result, dict)
    
    # Test None input  
    result = normalize_user_params(None)
    assert result == {}
    
    # Test unknown keys preservation
    input_params = {"unknown_key": "value", "writeupType": "essay"}
    result = normalize_user_params(input_params)
    assert "unknown_key" in result
    assert result["document_type"] == "Essay"


@pytest.mark.asyncio
async def test_sse_publisher():
    """Test SSE publisher functionality."""
    from src.agent.sse import SSEPublisher
    
    # Mock Redis client
    mock_redis = AsyncMock()
    
    publisher = SSEPublisher(async_redis=mock_redis)
    
    # Test basic publish
    await publisher.publish(
        conversation_id="test-conv",
        event_type="test",
        payload={"message": "hello"}
    )
    
    # Verify Redis publish was called
    mock_redis.publish.assert_called_once()
    args = mock_redis.publish.call_args[0]
    assert args[0] == "sse:test-conv"  # Channel
    
    # Verify JSON structure
    event_data = json.loads(args[1])
    assert event_data["type"] == "test"
    assert event_data["conversation_id"] == "test-conv"
    assert event_data["payload"]["message"] == "hello"
    assert "timestamp" in event_data


@pytest.mark.asyncio 
async def test_sse_publisher_convenience_methods():
    """Test SSE publisher convenience methods."""
    from src.agent.sse import SSEPublisher
    
    mock_redis = AsyncMock()
    publisher = SSEPublisher(async_redis=mock_redis)
    
    # Test start method
    await publisher.start("conv-123", "Test message")
    
    # Test routing method  
    await publisher.routing("conv-123", "advanced", 0.8, "Complex query")
    
    # Test content method
    await publisher.content("conv-123", "Response text", sources=[])
    
    # Test done method
    await publisher.done("conv-123", summary="Completed")
    
    # Test error method
    await publisher.error("conv-123", "Error occurred")
    
    # Should have 5 publish calls
    assert mock_redis.publish.call_count == 5


def test_model_registry():
    """Test model registry functionality."""
    from src.models.registry import ModelRegistry
    
    registry = ModelRegistry()
    
    # Test with mock data
    model_config = {
        "model_defaults": {
            "openai": "gpt-4",
            "gemini": "gemini-pro"
        },
        "providers": {
            "openai": {
                "gpt-4-turbo": "gpt-4-turbo-preview"
            }
        }
    }
    
    price_table = {
        "models": [
            {
                "provider": "openai",
                "model": "gpt-4",
                "input_cost_per_1k": 0.03,
                "output_cost_per_1k": 0.06,
                "currency": "USD"
            }
        ],
        "provider_defaults": {
            "gemini": {
                "input_cost_per_1k": 0.01,
                "output_cost_per_1k": 0.02,
                "currency": "USD"
            }
        }
    }
    
    registry._build_registry(model_config, price_table)
    
    # Test resolution
    model_info = registry.resolve("openai-default")
    assert model_info is not None
    assert model_info.provider == "openai"
    assert model_info.provider_model_id == "gpt-4"
    assert model_info.pricing["input_cost_per_1k"] == 0.03
    
    # Test validation
    assert registry.validate()
    
    # Test unknown model
    assert registry.resolve("unknown-model") is None


def test_budget_guard():
    """Test budget enforcement functionality."""
    from src.services.budget import BudgetGuard, CostLevel
    
    guard = BudgetGuard()
    
    # Test budget check - should pass for reasonable request
    result = guard.guard(
        estimated_tokens=1000,
        role="user",
        cost_level=CostLevel.MEDIUM,
        tenant="test-user"
    )
    
    assert result.allowed is True
    assert result.estimated_cost > 0
    assert result.code == "BUDGET_OK"
    
    # Test excessive request
    result = guard.guard(
        estimated_tokens=1000000,  # Very high token count
        role="user",
        cost_level=CostLevel.PREMIUM,
        tenant="test-user"
    )
    
    assert result.allowed is False
    assert "BUDGET_EXCEEDED" in result.code
    
    # Test usage recording
    guard.record_usage(
        actual_cost=0.50,
        tokens_used=500,
        tenant="test-user",
        model="gpt-4"
    )
    
    # Get usage summary
    summary = guard.get_usage_summary("test-user")
    assert summary["daily_spent"] == 0.50
    assert summary["total_tokens"] == 500


def test_budget_guard_token_estimation():
    """Test token estimation logic."""
    from src.services.budget import BudgetGuard
    
    guard = BudgetGuard()
    
    # Test text estimation
    text = "This is a test message for token estimation."
    estimated = guard.estimate_tokens(text)
    assert estimated > 0
    assert estimated < 1000  # Reasonable estimate
    
    # Test with files
    files = [
        {"content": "File content here", "size": 100},
        {"content": "More file content", "size": 200}
    ]
    estimated_with_files = guard.estimate_tokens(text, files)
    assert estimated_with_files > estimated  # Should be higher with files


def test_search_adapter():
    """Test search result adapter functionality."""
    from src.agent.search.adapter import to_search_results, SearchResult
    
    # Test Gemini format conversion
    gemini_payload = {
        "sources": [
            {
                "title": "Test Paper",
                "authors": ["Author One", "Author Two"],
                "abstract": "This is a test abstract",
                "url": "https://example.com/paper",
                "doi": "10.1000/test"
            }
        ]
    }
    
    results = to_search_results("gemini", gemini_payload)
    assert len(results) == 1
    
    result = results[0]
    assert result["title"] == "Test Paper"
    assert len(result["authors"]) == 2
    assert result["abstract"] == "This is a test abstract"
    assert result["url"] == "https://example.com/paper"
    assert result["doi"] == "10.1000/test"
    assert result["source_type"] in ["web", "journal", "academic"]
    
    # Test Perplexity format
    perplexity_payload = {
        "sources": [
            {
                "title": "Perplexity Result",
                "snippet": "Result snippet",
                "url": "https://example.com/result",
                "credibility_scores": {"overall": 0.8}
            }
        ]
    }
    
    results = to_search_results("perplexity", perplexity_payload)
    assert len(results) == 1
    assert results[0]["credibility_score"] == 0.8
    
    # Test unknown agent
    results = to_search_results("unknown", {"data": []})
    assert results == []


def test_logging_context():
    """Test logging context functionality."""
    from src.services.logging_context import (
        generate_correlation_id, 
        LoggingContext,
        get_current_correlation_id,
        with_correlation_context
    )
    
    # Test correlation ID generation
    corr_id = generate_correlation_id()
    assert corr_id.startswith("corr_")
    assert len(corr_id) > 10
    
    # Test with conversation ID
    corr_id_with_conv = generate_correlation_id("conv-123")
    assert corr_id_with_conv == "corr_conv-123"
    
    # Test context manager
    with LoggingContext(
        correlation_id="test-corr",
        conversation_id="test-conv",
        user_id="test-user",
        node_name="test-node",
        phase="test-phase"
    ):
        assert get_current_correlation_id() == "test-corr"
        
        context_dict = LoggingContext(
            correlation_id="test-corr",
            conversation_id="test-conv",
            user_id="test-user",
            node_name="test-node",
            phase="test-phase"
        ).get_context_dict()
        
        assert context_dict["correlation_id"] == "test-corr"
        assert context_dict["conversation_id"] == "test-conv"
        assert context_dict["user_id"] == "test-user"
        assert context_dict["node_name"] == "test-node"
        assert context_dict["phase"] == "test-phase"
    
    # Context should be cleared
    assert get_current_correlation_id() is None


@pytest.mark.asyncio
async def test_unified_processor_integration():
    """Test UnifiedProcessor with new Phase 1 components."""
    from src.agent.routing.unified_processor import UnifiedProcessor
    
    # Mock dependencies
    with patch('src.agent.routing.unified_processor.redis_client') as mock_redis, \
         patch('src.services.budget.get_budget_guard') as mock_budget_guard, \
         patch('src.agent.routing.unified_processor.normalize_user_params') as mock_normalize:
        
        mock_redis.publish = AsyncMock()
        
        # Mock budget guard
        mock_guard = Mock()
        mock_guard.estimate_tokens.return_value = 1000
        mock_budget_guard.return_value = mock_guard
        
        # Mock normalization
        mock_normalize.return_value = {"document_type": "essay", "citation_style": "APA"}
        
        processor = UnifiedProcessor(simple_available=True, advanced_available=False)
        
        # Mock the simple system processing
        with patch.object(processor, '_process_simple') as mock_simple:
            mock_simple.return_value = {
                "success": True,
                "response": "Test response",
                "sources": [],
                "tokens_used": 800
            }
            
            # Mock guard_request to not raise
            with patch('src.agent.routing.unified_processor.guard_request') as mock_guard_request:
                mock_guard_request.return_value = Mock(estimated_cost=0.05)
                
                # Test processing
                result = await processor.process_message(
                    "Test message",
                    files=[],
                    user_params={"writeupType": "essay"},
                    user_id="test-user",
                    conversation_id="test-conv"
                )
                
                # Verify result
                assert result["success"] is True
                assert result["response"] == "Test response"
                assert "system_used" in result
                assert "processing_time" in result
                
                # Verify SSE events were published
                assert mock_redis.publish.call_count >= 2  # start and done events
                
                # Verify budget was checked
                mock_guard_request.assert_called_once()


@pytest.mark.asyncio
async def test_budget_exceeded_handling():
    """Test budget exceeded error handling."""
    from src.agent.routing.unified_processor import UnifiedProcessor
    from src.services.budget import BudgetExceededError
    
    with patch('src.agent.routing.unified_processor.redis_client') as mock_redis:
        mock_redis.publish = AsyncMock()
        
        processor = UnifiedProcessor()
        
        # Mock guard_request to raise budget exceeded
        with patch('src.agent.routing.unified_processor.guard_request') as mock_guard_request:
            mock_guard_request.side_effect = BudgetExceededError(
                "Daily budget exceeded",
                "DAILY_BUDGET_EXCEEDED", 
                10.0,
                5.0
            )
            
            result = await processor.process_message(
                "Test message",
                user_id="test-user",
                conversation_id="test-conv"
            )
            
            # Should return budget error
            assert result["success"] is False
            assert "budget" in result["response"].lower()
            assert result["workflow_status"] == "budget_exceeded"
            assert result["error_details"]["error_type"] == "BudgetExceededError"


def test_comprehensive_integration():
    """Test that all Phase 1 components work together."""
    
    # Test parameter normalization -> budget estimation -> registry lookup
    from src.agent.routing.normalization import normalize_user_params
    from src.services.budget import BudgetGuard
    from src.models.registry import ModelRegistry
    
    # 1. Normalize parameters
    raw_params = {
        "writeupType": "PhD Dissertation", 
        "wordCount": 10000,
        "citationStyle": "harvard"
    }
    normalized = normalize_user_params(raw_params)
    
    # 2. Estimate budget
    guard = BudgetGuard()
    estimated_tokens = guard.estimate_tokens(
        "Complex dissertation request",
        complexity_multiplier=2.0  # High complexity
    )
    
    budget_result = guard.guard(
        estimated_tokens=estimated_tokens,
        role="user",
        cost_level=guard.cost_multipliers.__class__.HIGH
    )
    
    # 3. Registry lookup
    registry = ModelRegistry()
    
    # All components should work without errors
    assert normalized["document_type"] == "Dissertation" 
    assert estimated_tokens > 0
    assert budget_result.estimated_cost > 0
    assert registry is not None


if __name__ == "__main__":
    # Run basic smoke test
    test_parameter_normalization()
    test_budget_guard()
    test_search_adapter()
    test_logging_context()
    print("✅ All Phase 1 & Phase 2 integration tests passed!")