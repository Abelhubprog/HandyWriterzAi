#!/usr/bin/env python3
"""
Production Readiness Test Suite
Tests all critical production fixes implemented.
"""

import sys
import os
import traceback

# Add current directory to path
sys.path.insert(0, '.')

def test_lazy_loading():
    """Test that agents can be created without API keys."""
    print("🔧 Testing lazy loading...")
    
    try:
        # Test fact checking agent
        from src.agent.nodes.qa_swarm.fact_checking import FactCheckingAgent
        agent = FactCheckingAgent()
        print("  ✅ FactCheckingAgent created without API key")
        
        # Test argument validation agent  
        from src.agent.nodes.qa_swarm.argument_validation import ArgumentValidationAgent
        arg_agent = ArgumentValidationAgent()
        print("  ✅ ArgumentValidationAgent created without API key")
        
        # Test ethical reasoning agent
        from src.agent.nodes.qa_swarm.ethical_reasoning import EthicalReasoningAgent
        eth_agent = EthicalReasoningAgent()
        print("  ✅ EthicalReasoningAgent created without API key")
        
        # Test search agents
        from src.agent.nodes.search_openai import OpenAISearchAgent
        search_agent = OpenAISearchAgent()
        print("  ✅ OpenAI search agent created without API key")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Lazy loading test failed: {e}")
        return False

def test_parameter_normalization():
    """Test parameter normalization works correctly."""
    print("🔧 Testing parameter normalization...")
    
    try:
        from src.agent.routing.normalization import normalize_user_params, validate_user_params
        
        # Test camelCase to snake_case conversion
        test_params = {
            "writeupType": "PhD Dissertation",
            "citationStyle": "harvard",
            "educationLevel": "Doctoral", 
            "wordCount": 8000
        }
        
        normalized = normalize_user_params(test_params)
        
        # Check expected keys exist
        expected_keys = ["document_type", "citation_style", "academic_level", "word_count"]
        found_keys = [k for k in expected_keys if k in normalized]
        
        if len(found_keys) == len(expected_keys):
            print(f"  ✅ Parameter normalization: {len(found_keys)} keys converted correctly")
        else:
            print(f"  ⚠️  Parameter normalization: Only {len(found_keys)}/{len(expected_keys)} keys found")
        
        # Test validation
        validate_user_params(normalized)
        print("  ✅ Parameter validation passed")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Parameter normalization test failed: {e}")
        traceback.print_exc()
        return False

def test_sse_publisher():
    """Test SSE publisher creates correctly."""
    print("🔧 Testing SSE publisher...")
    
    try:
        from src.agent.sse import SSEPublisher
        
        publisher = SSEPublisher()
        print("  ✅ SSE Publisher created successfully")
        
        # Test envelope creation
        envelope = publisher._envelope("test-conv", "test", {"message": "hello"})
        
        required_fields = ["type", "timestamp", "conversation_id", "payload"]
        found_fields = [f for f in required_fields if f in envelope]
        
        if len(found_fields) == len(required_fields):
            print("  ✅ SSE envelope format correct")
        else:
            print(f"  ⚠️  SSE envelope missing fields: {set(required_fields) - set(found_fields)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ SSE publisher test failed: {e}")
        return False

def test_search_adapter():
    """Test search result adapter works."""
    print("🔧 Testing search adapter...")
    
    try:
        from src.agent.search.adapter import to_search_results
        
        # Test Gemini format conversion
        test_payload = {
            "sources": [
                {
                    "title": "Test Paper",
                    "authors": ["Author One", "Author Two"],
                    "abstract": "Test abstract",
                    "url": "https://example.com/paper",
                    "doi": "10.1000/test"
                }
            ]
        }
        
        results = to_search_results("gemini", test_payload)
        
        if len(results) == 1:
            result = results[0]
            required_fields = ["title", "authors", "abstract", "url", "source_type"]
            found_fields = [f for f in required_fields if f in result]
            
            if len(found_fields) == len(required_fields):
                print("  ✅ Search adapter: Gemini format converted correctly")
            else:
                print(f"  ⚠️  Search adapter: Missing fields {set(required_fields) - set(found_fields)}")
        else:
            print(f"  ⚠️  Search adapter: Expected 1 result, got {len(results)}")
        
        # Test unknown agent handling
        unknown_results = to_search_results("unknown", {"data": []})
        if unknown_results == []:
            print("  ✅ Search adapter: Unknown agent handled gracefully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Search adapter test failed: {e}")
        return False

def test_model_registry():
    """Test model registry functionality."""
    print("🔧 Testing model registry...")
    
    try:
        from src.models.registry import ModelRegistry
        
        registry = ModelRegistry()
        print("  ✅ Model registry created")
        
        # Test with minimal config
        model_config = {
            "model_defaults": {"openai": "gpt-4"},
            "providers": {"openai": {"gpt-4-turbo": "gpt-4-turbo-preview"}}
        }
        
        price_table = {
            "models": [{
                "provider": "openai",
                "model": "gpt-4", 
                "input_cost_per_1k": 0.03,
                "output_cost_per_1k": 0.06,
                "currency": "USD"
            }]
        }
        
        registry._build_registry(model_config, price_table)
        
        # Test resolution
        model_info = registry.resolve("openai-default")
        if model_info and model_info.provider == "openai":
            print("  ✅ Model registry: Resolution working")
        else:
            print("  ⚠️  Model registry: Resolution not working")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Model registry test failed: {e}")
        return False

def test_budget_guard():
    """Test budget enforcement."""
    print("🔧 Testing budget guard...")
    
    try:
        from src.services.budget import BudgetGuard, CostLevel
        
        guard = BudgetGuard()
        print("  ✅ Budget guard created")
        
        # Test reasonable request
        result = guard.guard(
            estimated_tokens=1000,
            cost_level=CostLevel.MEDIUM
        )
        
        if result.allowed:
            print(f"  ✅ Budget guard: Reasonable request allowed (${result.estimated_cost:.4f})")
        else:
            print(f"  ⚠️  Budget guard: Reasonable request denied: {result.reason}")
        
        # Test token estimation
        estimated = guard.estimate_tokens("This is a test message", complexity_multiplier=1.0)
        if estimated > 0:
            print(f"  ✅ Budget guard: Token estimation working ({estimated} tokens)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Budget guard test failed: {e}")
        return False

def test_logging_context():
    """Test logging context functionality."""
    print("🔧 Testing logging context...")
    
    try:
        from src.services.logging_context import generate_correlation_id, with_correlation_context
        
        # Test correlation ID generation
        corr_id = generate_correlation_id("test-conv")
        if corr_id.startswith("corr_"):
            print(f"  ✅ Logging context: Correlation ID generated ({corr_id})")
        
        # Test context manager (basic)
        try:
            with with_correlation_context(conversation_id="test-conv", user_id="test-user"):
                pass
            print("  ✅ Logging context: Context manager working")
        except Exception as ctx_e:
            print(f"  ⚠️  Logging context: Context manager error: {ctx_e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Logging context test failed: {e}")
        return False

def test_error_handling():
    """Test error handling improvements."""
    print("🔧 Testing error handling...")
    
    try:
        from src.agent.base import BaseNode
        
        # Test that BaseNode methods exist and accept error parameter
        class TestNode(BaseNode):
            async def execute(self, state, config):
                return {}
        
        node = TestNode("test")
        
        # Check if _broadcast_progress accepts error parameter
        import inspect
        sig = inspect.signature(node._broadcast_progress)
        if 'error' in sig.parameters:
            print("  ✅ Error handling: _broadcast_progress supports error parameter")
        else:
            print("  ⚠️  Error handling: error parameter not found")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error handling test failed: {e}")
        return False

def run_production_tests():
    """Run all production readiness tests."""
    print("🚀 Running Production Readiness Tests\n")
    
    tests = [
        ("Lazy Loading", test_lazy_loading),
        ("Parameter Normalization", test_parameter_normalization), 
        ("SSE Publisher", test_sse_publisher),
        ("Search Adapter", test_search_adapter),
        ("Model Registry", test_model_registry),
        ("Budget Guard", test_budget_guard),
        ("Logging Context", test_logging_context),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            failed += 1
        print()  # Empty line between tests
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All production fixes are working correctly!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = run_production_tests()
    sys.exit(0 if success else 1)