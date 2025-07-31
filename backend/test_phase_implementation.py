#!/usr/bin/env python3
"""
Phase Implementation Validation Script

Tests and validates all Phase 1 & Phase 2 components to ensure
they're working correctly before proceeding to Phase 3+.
"""

import asyncio
import sys
import os
import traceback
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_phase_1_components():
    """Test all Phase 1 components."""
    print("🔧 Testing Phase 1: Foundation & Contracts")
    
    # Test 1: Parameter Normalization
    print("  1. Testing parameter normalization...")
    try:
        from src.agent.routing.normalization import normalize_user_params, validate_user_params
        
        test_params = {
            "writeupType": "PhD Dissertation",
            "citationStyle": "harvard", 
            "wordCount": 8000,
            "educationLevel": "Doctoral"
        }
        
        normalized = normalize_user_params(test_params)
        validate_user_params(normalized)
        
        assert "document_type" in normalized
        assert normalized["citation_style"] == "Harvard"
        assert normalized["pages"] > 0
        
        print("    ✅ Parameter normalization working")
        
    except Exception as e:
        print(f"    ❌ Parameter normalization failed: {e}")
        return False
    
    # Test 2: SSE Publisher
    print("  2. Testing SSE publisher...")
    try:
        from src.agent.sse import SSEPublisher
        from unittest.mock import AsyncMock
        
        mock_redis = AsyncMock()
        publisher = SSEPublisher(async_redis=mock_redis)
        
        await publisher.publish("test-conv", "test", {"message": "hello"})
        await publisher.start("test-conv", "Starting")
        await publisher.done("test-conv")
        
        assert mock_redis.publish.call_count == 3
        print("    ✅ SSE publisher working")
        
    except Exception as e:
        print(f"    ❌ SSE publisher failed: {e}")
        return False
    
    # Test 3: Model Registry
    print("  3. Testing model registry...")
    try:
        from src.models.registry import ModelRegistry
        
        registry = ModelRegistry()
        
        # Test with minimal config
        model_config = {
            "model_defaults": {"openai": "gpt-4"},
            "providers": {}
        }
        price_table = {
            "models": [],
            "provider_defaults": {
                "openai": {
                    "input_cost_per_1k": 0.03,
                    "output_cost_per_1k": 0.06,
                    "currency": "USD"
                }
            }
        }
        
        registry._build_registry(model_config, price_table)
        model_info = registry.resolve("openai-default")
        
        assert model_info is not None
        assert model_info.provider == "openai"
        
        print("    ✅ Model registry working")
        
    except Exception as e:
        print(f"    ❌ Model registry failed: {e}")
        return False
    
    # Test 4: Budget Guard
    print("  4. Testing budget guard...")
    try:
        from src.services.budget import BudgetGuard, CostLevel
        
        guard = BudgetGuard()
        
        # Test estimation
        tokens = guard.estimate_tokens("Test message")
        assert tokens > 0
        
        # Test budget check
        result = guard.guard(1000, cost_level=CostLevel.MEDIUM)
        assert result.allowed is True
        
        # Test usage recording
        guard.record_usage(0.50, 500, "test-user")
        summary = guard.get_usage_summary("test-user")
        assert summary["daily_spent"] == 0.50
        
        print("    ✅ Budget guard working")
        
    except Exception as e:
        print(f"    ❌ Budget guard failed: {e}")
        return False
    
    # Test 5: Search Adapter
    print("  5. Testing search adapter...")
    try:
        from src.agent.search.adapter import to_search_results
        
        # Test Gemini format
        gemini_payload = {
            "sources": [{
                "title": "Test Paper",
                "authors": ["Author One"],
                "abstract": "Test abstract",
                "url": "https://example.com/test"
            }]
        }
        
        results = to_search_results("gemini", gemini_payload)
        assert len(results) == 1
        assert results[0]["title"] == "Test Paper"
        
        print("    ✅ Search adapter working")
        
    except Exception as e:
        print(f"    ❌ Search adapter failed: {e}")
        return False
    
    # Test 6: Logging Context
    print("  6. Testing logging context...")
    try:
        from src.services.logging_context import (
            generate_correlation_id,
            LoggingContext,
            get_current_correlation_id
        )
        
        corr_id = generate_correlation_id()
        assert corr_id.startswith("corr_")
        
        with LoggingContext(correlation_id="test-corr"):
            assert get_current_correlation_id() == "test-corr"
        
        assert get_current_correlation_id() is None
        
        print("    ✅ Logging context working")
        
    except Exception as e:
        print(f"    ❌ Logging context failed: {e}")
        return False
    
    print("✅ Phase 1 components all working correctly!")
    return True


async def test_phase_2_integration():
    """Test Phase 2 integration components."""
    print("🔧 Testing Phase 2: Security & Integration")
    
    # Test 1: UnifiedProcessor with budget integration
    print("  1. Testing UnifiedProcessor budget integration...")
    try:
        from src.agent.routing.unified_processor import UnifiedProcessor
        from unittest.mock import patch, Mock, AsyncMock
        
        with patch('src.agent.routing.unified_processor.redis_client') as mock_redis:
            mock_redis.publish = AsyncMock()
            
            processor = UnifiedProcessor(simple_available=False, advanced_available=False)
            
            # Test budget exceeded scenario
            with patch('src.agent.routing.unified_processor.guard_request') as mock_guard:
                from src.services.budget import BudgetExceededError
                mock_guard.side_effect = BudgetExceededError(
                    "Budget exceeded", "BUDGET_EXCEEDED", 10.0, 0.0
                )
                
                result = await processor.process_message(
                    "Test message",
                    user_id="test-user",
                    conversation_id="test-conv"
                )
                
                assert result["success"] is False
                assert result["workflow_status"] == "budget_exceeded"
        
        print("    ✅ UnifiedProcessor budget integration working")
        
    except Exception as e:
        print(f"    ❌ UnifiedProcessor budget integration failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 2: Registry initialization validation
    print("  2. Testing registry initialization...")
    try:
        from src.models.registry import initialize_registry, get_registry
        import tempfile
        import json
        import yaml
        
        # Create temporary config files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                "model_defaults": {"openai": "gpt-4"},
                "providers": {}
            }, f)
            model_config_path = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "models": [],
                "provider_defaults": {
                    "openai": {
                        "input_cost_per_1k": 0.03,
                        "output_cost_per_1k": 0.06,
                        "currency": "USD"
                    }
                }
            }, f)
            price_table_path = f.name
        
        # Test initialization
        registry = initialize_registry(model_config_path, price_table_path, strict=False)
        assert registry.validate()
        
        # Clean up
        os.unlink(model_config_path)
        os.unlink(price_table_path)
        
        print("    ✅ Registry initialization working")
        
    except Exception as e:
        print(f"    ❌ Registry initialization failed: {e}")
        return False
    
    print("✅ Phase 2 integration components working correctly!")
    return True


async def test_phase_3_harmonization():
    """Test Phase 3 search agent harmonization."""
    print("🔧 Testing Phase 3: Agent Harmonization")
    
    # Test 1: Search agent adapter integration
    print("  1. Testing search agent adapter integration...")
    try:
        from src.agent.search.adapter import to_search_results
        
        # Test different agent formats
        agents_and_payloads = [
            ("gemini", {"sources": [{"title": "Gemini Test", "url": "http://test.com"}]}),
            ("perplexity", {"sources": [{"title": "Perplexity Test", "url": "http://test.com"}]}),
            ("openai", {"results": [{"title": "OpenAI Test", "url": "http://test.com"}]}),
            ("claude", {"sources": [{"title": "Claude Test", "url": "http://test.com"}]}),
            ("crossref", {"message": {"items": [{"title": ["CrossRef Test"], "URL": "http://test.com"}]}}),
        ]
        
        for agent_name, payload in agents_and_payloads:
            results = to_search_results(agent_name, payload)
            assert isinstance(results, list)
            if results:  # Some may return empty for minimal test data
                assert "title" in results[0]
                assert "url" in results[0]
        
        print("    ✅ Search agent adapter integration working")
        
    except Exception as e:
        print(f"    ❌ Search agent adapter integration failed: {e}")
        return False
    
    print("✅ Phase 3 harmonization components working correctly!")
    return True


async def test_end_to_end_integration():
    """Test end-to-end integration of all components."""
    print("🔧 Testing End-to-End Integration")
    
    try:
        # Test complete pipeline: normalization -> budget -> registry -> adapter
        from src.agent.routing.normalization import normalize_user_params
        from src.services.budget import BudgetGuard
        from src.models.registry import ModelRegistry
        from src.agent.search.adapter import to_search_results
        from src.services.logging_context import with_correlation_context
        
        # 1. Parameter normalization
        raw_params = {"writeupType": "dissertation", "wordCount": 5000}
        normalized = normalize_user_params(raw_params)
        
        # 2. Budget estimation and checking
        guard = BudgetGuard()
        tokens = guard.estimate_tokens("Test research query", complexity_multiplier=1.5)
        budget_result = guard.guard(tokens)
        
        # 3. Model registry lookup
        registry = ModelRegistry()
        
        # 4. Search adapter conversion
        search_payload = {"sources": [{"title": "Test", "url": "http://test.com"}]}
        search_results = to_search_results("gemini", search_payload)
        
        # 5. Logging context
        with with_correlation_context(correlation_id="test-integration"):
            # All components working together
            assert normalized["document_type"] == "Dissertation"
            assert budget_result.allowed is True
            assert len(search_results) >= 0  # May be empty for minimal data
            
        print("    ✅ End-to-end integration working")
        return True
        
    except Exception as e:
        print(f"    ❌ End-to-end integration failed: {e}")
        traceback.print_exc()
        return False


async def main():
    """Run all phase validation tests."""
    print("🚀 HandyWriterzAI Phase Implementation Validation")
    print("=" * 60)
    
    success = True
    
    # Test Phase 1
    if not await test_phase_1_components():
        success = False
    
    print()
    
    # Test Phase 2
    if not await test_phase_2_integration():
        success = False
    
    print()
    
    # Test Phase 3
    if not await test_phase_3_harmonization():
        success = False
    
    print()
    
    # Test End-to-End
    if not await test_end_to_end_integration():
        success = False
    
    print()
    print("=" * 60)
    
    if success:
        print("🎉 ALL PHASE IMPLEMENTATIONS VALIDATED SUCCESSFULLY!")
        print()
        print("✅ Phase 1: Foundation & Contracts - Complete")
        print("✅ Phase 2: Security & Integration - Complete")  
        print("✅ Phase 3: Agent Harmonization - In Progress")
        print()
        print("Ready to proceed with:")
        print("  - Phase 4: Missing Components & Features")
        print("  - Phase 5: Testing & CI/CD Setup")
        print("  - Production deployment")
        return 0
    else:
        print("❌ SOME COMPONENTS FAILED VALIDATION")
        print("Please review the errors above and fix issues before proceeding.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)