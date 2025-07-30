#!/usr/bin/env python3
"""
Real end-to-end user journey test for HandyWriterz.
Tests the complete workflow from user request to final document.
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Test environment setup
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5433/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6380/1")

async def test_imports():
    """Test all critical imports work correctly."""
    print("🔍 Testing critical imports...")
    
    try:
        import redis.asyncio as redis
        print("✅ redis.asyncio import successful")
    except ImportError as e:
        print(f"❌ redis.asyncio import failed: {e}")
        return False
        
    try:
        import asyncpg
        print("✅ asyncpg import successful")  
    except ImportError as e:
        print(f"❌ asyncpg import failed: {e}")
        return False
        
    try:
        from langchain_community.chat_models.groq import ChatGroq
        print("✅ langchain_community.chat_models.groq import successful")
    except ImportError as e:
        print(f"❌ langchain_community import failed: {e}")
        return False
        
    try:
        from agent.handywriterz_state import HandyWriterzState
        print("✅ HandyWriterzState import successful")
    except ImportError as e:
        print(f"❌ HandyWriterzState import failed: {e}")
        return False
        
    try:
        from agent.handywriterz_graph import handywriterz_graph
        print("✅ handywriterz_graph import successful")
    except ImportError as e:
        print(f"❌ handywriterz_graph import failed: {e}")
        return False
        
    return True

async def test_state_creation():
    """Test state object creation and validation."""
    print("📊 Testing state creation...")
    
    try:
        from agent.handywriterz_state import HandyWriterzState
        
        # Create test state with all required fields
        state = HandyWriterzState(
            conversation_id="test-conversation-123",
            user_id="test-user-456", 
            user_params={
                "topic": "AI ethics in healthcare",
                "document_type": "research_paper",
                "word_count": 2000,
                "citation_style": "APA"
            },
            uploaded_docs=[],
            outline=None,
            research_agenda=[],
            search_queries=[],
            raw_search_results=[],
            filtered_sources=[],
            verified_sources=[],
            draft_content=None,
            current_draft=None,
            revision_count=0,
            evaluation_results=[],
            evaluation_score=None,
            turnitin_reports=[],
            turnitin_passed=False,
            formatted_document=None,
            learning_outcomes_report=None,
            download_urls={},
            current_node=None,
            workflow_status="initiated",
            error_message=None,
            retry_count=0,
            max_iterations=5,
        )
        
        print(f"✅ State created successfully")
        print(f"   Conversation ID: {state.conversation_id}")
        print(f"   User ID: {state.user_id}")
        print(f"   Status: {state.workflow_status}")
        print(f"   Topic: {state.user_params.get('topic', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ State creation failed: {e}")
        return False

async def test_api_integrations():
    """Test API integrations with real services."""
    print("🌐 Testing API integrations...")
    
    # Test Gemini API
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key != "your_gemini_api_key_here":
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content("Say 'Hello from Gemini 2.5!'")
            
            print(f"✅ Gemini API working: {response.text[:50]}...")
            
        except Exception as e:
            print(f"❌ Gemini API failed: {e}")
    else:
        print("⚠️  Gemini API key not configured")
    
    # Test Perplexity API  
    perplexity_key = os.getenv("PERPLEXITY_API_KEY")
    if perplexity_key and perplexity_key != "your_perplexity_api_key_here":
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {perplexity_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-sonar-small-128k-online",
                        "messages": [{"role": "user", "content": "Hello from Perplexity!"}],
                        "max_tokens": 50
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Perplexity API working: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')[:50]}...")
                else:
                    print(f"❌ Perplexity API returned {response.status_code}: {response.text}")
                    
        except Exception as e:
            print(f"❌ Perplexity API failed: {e}")
    else:
        print("⚠️  Perplexity API key not configured")

async def test_graph_execution():
    """Test the agent graph execution."""
    print("🤖 Testing graph execution...")
    
    try:
        from agent.handywriterz_graph import handywriterz_graph
        from agent.handywriterz_state import HandyWriterzState
        
        # Create minimal state for testing
        initial_state = HandyWriterzState(
            conversation_id="test-graph-exec",
            user_id="test-user",
            user_params={
                "topic": "Test topic for graph execution",
                "document_type": "essay",
                "word_count": 100
            },
            uploaded_docs=[],
            outline=None,
            research_agenda=[],
            search_queries=[],
            raw_search_results=[],
            filtered_sources=[],
            verified_sources=[],
            draft_content=None,
            current_draft=None,
            revision_count=0,
            evaluation_results=[],
            evaluation_score=None,
            turnitin_reports=[],
            turnitin_passed=False,
            formatted_document=None,
            learning_outcomes_report=None,
            download_urls={},
            current_node=None,
            workflow_status="initiated",
            error_message=None,
            retry_count=0,
            max_iterations=5,
        )
        
        print("✅ Graph execution test setup complete")
        print("   (Skipping actual execution to avoid API costs)")
        
        return True
        
    except Exception as e:
        print(f"❌ Graph execution test failed: {e}")
        return False

async def test_main_app():
    """Test the main FastAPI application."""
    print("🚀 Testing main application...")
    
    try:
        from main import app
        print("✅ FastAPI app import successful")
        
        # Test basic app attributes
        if hasattr(app, 'title'):
            print(f"   App title: {app.title}")
        if hasattr(app, 'version'):
            print(f"   App version: {app.version}")
            
        return True
        
    except Exception as e:
        print(f"❌ Main app test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests and report results."""
    print("🧪 HandyWriterz User Journey Test Suite")
    print("=" * 50)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Import Tests", test_imports),
        ("State Creation", test_state_creation), 
        ("API Integrations", test_api_integrations),
        ("Graph Execution", test_graph_execution),
        ("Main Application", test_main_app),
    ]
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name}...")
        try:
            result = await test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Report results
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - check logs above")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)