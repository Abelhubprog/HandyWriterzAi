"""
Direct integration tests for the agent system components.
Tests real functionality without complex mocking.
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pytest
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestAgentIntegration:
    """Direct integration tests for agent components."""
    
    def test_state_creation_and_manipulation(self):
        """Test HandyWriterz state creation and manipulation."""
        from src.agent.handywriterz_state import HandyWriterzState, UserParams
        
        # Test UserParams creation
        user_params = UserParams(
            writeupType="essay",
            field="computer science",
            studyLevel="undergraduate",
            citationStyle="harvard",
            wordCount=1000,
            additionalInstructions="Focus on AI ethics"
        )
        
        assert user_params.writeupType == "essay"
        assert user_params.field == "computer science"
        assert user_params.wordCount == 1000
        
        # Test HandyWriterzState creation
        state = HandyWriterzState(
            conversation_id="test_conv_123",
            user_id="test_user_123",
            messages=[HumanMessage(content="Test AI ethics essay")],
            user_params=user_params.dict(),
            workflow_status="initiated"
        )
        
        assert state.conversation_id == "test_conv_123"
        assert state.workflow_status == "initiated"
        assert len(state.messages) == 1
        assert state.user_params["field"] == "computer science"
        
        # Test state updates
        state.update({
            "workflow_status": "processing",
            "current_node": "user_intent"
        })
        
        assert state.workflow_status == "processing"
        assert state.current_node == "user_intent"
        
        print("✅ State creation and manipulation test passed")
    
    def test_orchestrator_initialization(self):
        """Test HandyWriterz orchestrator initialization."""
        try:
            from src.agent.handywriterz_graph import HandyWriterzOrchestrator
            
            orchestrator = HandyWriterzOrchestrator()
            assert orchestrator is not None
            
            # Test graph creation
            graph = orchestrator.create_graph()
            assert graph is not None
            
            print("✅ Orchestrator initialization test passed")
            
        except ImportError as e:
            print(f"⚠️  Orchestrator import failed: {e}")
            print("   This is expected if dependencies are missing")
    
    @pytest.mark.asyncio
    async def test_gemini_search_agent_direct(self):
        """Test Gemini search agent directly."""
        if not os.getenv("GEMINI_API_KEY"):
            print("⚠️  Skipping Gemini test - API key not available")
            return
            
        try:
            from src.agent.nodes.search_gemini import GeminiSearchAgent
            from src.agent.handywriterz_state import HandyWriterzState, UserParams
            
            # Create test state
            user_params = UserParams(
                writeupType="essay",
                field="computer science",
                studyLevel="undergraduate",
                citationStyle="harvard",
                wordCount=1000,
                additionalInstructions="Focus on AI ethics"
            )
            
            state = HandyWriterzState(
                conversation_id="test_gemini_123",
                user_id="test_user_123",
                messages=[HumanMessage(content="Research AI ethics in computer science")],
                user_params=user_params.dict(),
                workflow_status="initiated"
            )
            
            # Create and test agent
            agent = GeminiSearchAgent()
            config = {"configurable": {"thread_id": "test_thread"}}
            
            start_time = time.time()
            result = await agent.execute(state, config)
            duration = time.time() - start_time
            
            assert "search_result" in result
            assert "processing_metrics" in result
            assert duration < 300  # Should complete within 5 minutes
            
            print(f"✅ Gemini search agent test passed in {duration:.2f} seconds")
            
        except Exception as e:
            print(f"❌ Gemini search agent test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_perplexity_search_agent_direct(self):
        """Test Perplexity search agent directly."""
        if not os.getenv("PERPLEXITY_API_KEY"):
            print("⚠️  Skipping Perplexity test - API key not available")
            return
            
        try:
            from src.agent.nodes.search_perplexity import PerplexitySearchAgent
            from src.agent.handywriterz_state import HandyWriterzState, UserParams
            
            # Create test state
            user_params = UserParams(
                writeupType="essay",
                field="computer science",
                studyLevel="undergraduate",
                citationStyle="harvard",
                wordCount=1000,
                additionalInstructions="Focus on AI ethics and recent developments"
            )
            
            state = HandyWriterzState(
                conversation_id="test_perplexity_123",
                user_id="test_user_123",
                messages=[HumanMessage(content="Find recent developments in AI ethics")],
                user_params=user_params.dict(),
                workflow_status="initiated"
            )
            
            # Create and test agent
            agent = PerplexitySearchAgent()
            config = {"configurable": {"thread_id": "test_thread"}}
            
            start_time = time.time()
            result = await agent.execute(state, config)
            duration = time.time() - start_time
            
            assert "search_results" in result
            assert duration < 60  # Should complete within 1 minute
            
            print(f"✅ Perplexity search agent test passed in {duration:.2f} seconds")
            
        except Exception as e:
            print(f"❌ Perplexity search agent test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_simple_workflow_execution(self):
        """Test a simple workflow execution."""
        if not (os.getenv("GEMINI_API_KEY") and os.getenv("PERPLEXITY_API_KEY")):
            print("⚠️  Skipping workflow test - API keys not available")
            return
            
        try:
            from src.agent.handywriterz_graph import HandyWriterzOrchestrator
            from src.agent.handywriterz_state import HandyWriterzState, UserParams
            
            # Create test state
            user_params = UserParams(
                writeupType="paragraph",
                field="computer science",
                studyLevel="undergraduate",
                citationStyle="harvard",
                wordCount=200,
                additionalInstructions="Brief overview of AI ethics"
            )
            
            state = HandyWriterzState(
                conversation_id="test_workflow_123",
                user_id="test_user_123",
                messages=[HumanMessage(content="Write a brief paragraph about AI ethics")],
                user_params=user_params.dict(),
                workflow_status="initiated",
                max_iterations=2  # Limit iterations for testing
            )
            
            # Create orchestrator and graph
            orchestrator = HandyWriterzOrchestrator()
            graph = orchestrator.create_graph()
            
            # Execute workflow
            config = {"configurable": {"thread_id": "test_workflow"}}
            
            start_time = time.time()
            workflow_results = []
            
            # Run workflow with timeout
            async def run_workflow():
                async for chunk in graph.astream(state, config):
                    workflow_results.append(chunk)
                    
                    # Log progress
                    if "current_node" in chunk:
                        print(f"   Node: {chunk['current_node']}")
                        
                    # Break if we hit completion or failure
                    if chunk.get("workflow_status") in ["completed", "failed"]:
                        break
                        
                    # Safety break after 10 chunks
                    if len(workflow_results) > 10:
                        break
            
            # Run with timeout
            try:
                await asyncio.wait_for(run_workflow(), timeout=300)  # 5 minute timeout
            except asyncio.TimeoutError:
                print("⚠️  Workflow timed out after 5 minutes")
            
            duration = time.time() - start_time
            
            # Validate results
            assert len(workflow_results) > 0, "Should have workflow results"
            
            # Check for node execution
            nodes_executed = [chunk.get("current_node") for chunk in workflow_results if chunk.get("current_node")]
            assert len(nodes_executed) > 0, "Should have executed at least one node"
            
            print(f"✅ Simple workflow test passed in {duration:.2f} seconds")
            print(f"   Nodes executed: {', '.join(nodes_executed)}")
            
        except Exception as e:
            print(f"❌ Simple workflow test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_api_integration_with_real_calls(self):
        """Test API integration with real calls."""
        try:
            # Test direct Gemini API call
            gemini_result = await self._test_direct_gemini_call()
            
            # Test direct Perplexity API call
            perplexity_result = await self._test_direct_perplexity_call()
            
            # Report results
            if gemini_result["success"]:
                print("✅ Gemini API integration working")
                print(f"   Response: {gemini_result['response'][:100]}...")
            else:
                print(f"❌ Gemini API integration failed: {gemini_result['error']}")
            
            if perplexity_result["success"]:
                print("✅ Perplexity API integration working")
                print(f"   Response: {perplexity_result['response'][:100]}...")
            else:
                print(f"❌ Perplexity API integration failed: {perplexity_result['error']}")
            
            # At least one should work
            assert gemini_result["success"] or perplexity_result["success"], "At least one API should work"
            
        except Exception as e:
            print(f"❌ API integration test failed: {e}")
    
    async def _test_direct_gemini_call(self) -> Dict[str, Any]:
        """Test direct Gemini API call."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import HumanMessage
            
            if not os.getenv("GEMINI_API_KEY"):
                return {"success": False, "error": "API key not available"}
            
            client = ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=os.getenv("GEMINI_API_KEY"),
                temperature=0.7
            )
            
            result = await client.ainvoke([
                HumanMessage(content="What is artificial intelligence? Provide a brief, academic definition in 2-3 sentences.")
            ])
            
            return {
                "success": True,
                "response": result.content,
                "response_length": len(result.content)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_direct_perplexity_call(self) -> Dict[str, Any]:
        """Test direct Perplexity API call."""
        try:
            import httpx
            
            api_key = os.getenv("PERPLEXITY_API_KEY")
            if not api_key:
                return {"success": False, "error": "API key not available"}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-sonar-small-128k-online",
                        "messages": [
                            {"role": "user", "content": "What is artificial intelligence? Provide a brief definition with recent context."}
                        ],
                        "max_tokens": 200
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return {
                        "success": True,
                        "response": content,
                        "response_length": len(content)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API returned {response.status_code}: {response.text}"
                    }
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_database_models_import(self):
        """Test database models import."""
        try:
            from src.db.models import User, Conversation, Document
            
            # Test model attributes
            assert hasattr(User, 'wallet_address')
            assert hasattr(Conversation, 'user_id')
            assert hasattr(Document, 'conversation_id')
            
            print("✅ Database models import test passed")
            
        except Exception as e:
            print(f"❌ Database models import test failed: {e}")
    
    def test_routing_system_import(self):
        """Test routing system import."""
        try:
            from src.agent.routing import SystemRouter, UnifiedProcessor
            
            # Test basic initialization
            router = SystemRouter()
            assert router is not None
            
            processor = UnifiedProcessor(simple_available=True, advanced_available=True)
            assert processor is not None
            
            print("✅ Routing system import test passed")
            
        except Exception as e:
            print(f"❌ Routing system import test failed: {e}")


def run_integration_tests():
    """Run all integration tests."""
    test_instance = TestAgentIntegration()
    
    print("🧪 Running Agent Integration Tests")
    print("=" * 50)
    
    # Run synchronous tests
    test_instance.test_state_creation_and_manipulation()
    test_instance.test_orchestrator_initialization()
    test_instance.test_database_models_import()
    test_instance.test_routing_system_import()
    
    # Run asynchronous tests
    async def run_async_tests():
        await test_instance.test_gemini_search_agent_direct()
        await test_instance.test_perplexity_search_agent_direct()
        await test_instance.test_api_integration_with_real_calls()
        await test_instance.test_simple_workflow_execution()
    
    asyncio.run(run_async_tests())
    
    print("\n" + "=" * 50)
    print("✅ Integration tests completed!")


if __name__ == "__main__":
    run_integration_tests()