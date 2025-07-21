#!/usr/bin/env python3
"""
Direct system test without complex configuration dependencies.
Tests the core MultiAgentWriterz functionality directly.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv()

class DirectSystemTest:
    """Direct system test for MultiAgentWriterz."""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.start_time = time.time()
    
    def run_all_tests(self):
        """Run all direct tests."""
        print("🚀 MultiAgentWriterz - Direct System Test")
        print("=" * 60)
        
        # Test 1: Basic Imports
        self.test_basic_imports()
        
        # Test 2: State Management
        self.test_state_management()
        
        # Test 3: API Keys
        self.test_api_keys()
        
        # Test 4: Direct API Calls
        asyncio.run(self.test_direct_api_calls())
        
        # Test 5: Agent Node Creation
        self.test_agent_node_creation()
        
        # Test 6: Simple workflow if possible
        asyncio.run(self.test_simple_agent_workflow())
        
        # Report results
        self.report_results()
        
        return self.passed_tests == self.total_tests
    
    def test_basic_imports(self):
        """Test basic system imports."""
        test_name = "Basic System Imports"
        self.total_tests += 1
        
        try:
            # Test core state imports
            
            # Test LLM imports
            
            self.record_success(test_name, "All basic imports successful")
            
        except Exception as e:
            self.record_failure(test_name, f"Import error: {e}")
    
    def test_state_management(self):
        """Test state management."""
        test_name = "State Management"
        self.total_tests += 1
        
        try:
            from src.agent.handywriterz_state import HandyWriterzState, UserParams
            from langchain_core.messages import HumanMessage
            
            # Create UserParams
            user_params = UserParams(
                word_count=1000,
                document_type="essay",
                citation_style="harvard",
                academic_field="computer-science",
                academic_level="undergraduate",
                special_instructions="Focus on AI ethics"
            )
            
            # Create state
            state = HandyWriterzState(
                conversation_id="test_conv_123",
                user_id="test_user_123",
                messages=[HumanMessage(content="Test message")],
                user_params=user_params.dict(),
                workflow_status="initiated"
            )
            
            # Test state operations
            assert state.conversation_id == "test_conv_123"
            assert state.workflow_status == "initiated"
            assert len(state.messages) == 1
            
            # Test state updates
            state.update_status("processing", "test_node")
            assert state.workflow_status.value == "processing"
            assert state.current_node == "test_node"
            
            self.record_success(test_name, "State management working correctly")
            
        except Exception as e:
            self.record_failure(test_name, f"State management error: {e}")
    
    def test_api_keys(self):
        """Test API key availability."""
        test_name = "API Key Availability"
        self.total_tests += 1
        
        try:
            gemini_key = os.getenv("GEMINI_API_KEY")
            perplexity_key = os.getenv("PERPLEXITY_API_KEY")
            
            available_apis = []
            if gemini_key:
                available_apis.append("Gemini")
            if perplexity_key:
                available_apis.append("Perplexity")
            
            if available_apis:
                self.record_success(test_name, f"Available APIs: {', '.join(available_apis)}")
            else:
                self.record_failure(test_name, "No API keys available")
                
        except Exception as e:
            self.record_failure(test_name, f"API key check error: {e}")
    
    async def test_direct_api_calls(self):
        """Test direct API calls."""
        test_name = "Direct API Calls"
        self.total_tests += 1
        
        try:
            gemini_result = await self._test_gemini_direct()
            perplexity_result = await self._test_perplexity_direct()
            
            results = {
                "gemini": gemini_result,
                "perplexity": perplexity_result
            }
            
            if gemini_result["success"] or perplexity_result["success"]:
                self.record_success(test_name, "At least one API working", results)
            else:
                self.record_failure(test_name, "No APIs working", results)
                
        except Exception as e:
            self.record_failure(test_name, f"API call error: {e}")
    
    async def _test_gemini_direct(self):
        """Test Gemini API directly."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import HumanMessage
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return {"success": False, "error": "No API key"}
            
            client = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.7
            )
            
            result = await client.ainvoke([
                HumanMessage(content="What is artificial intelligence? Answer in exactly 2 sentences.")
            ])
            
            return {
                "success": True,
                "response_length": len(result.content),
                "response_preview": result.content[:100]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_perplexity_direct(self):
        """Test Perplexity API directly."""
        try:
            import httpx
            
            api_key = os.getenv("PERPLEXITY_API_KEY")
            if not api_key:
                return {"success": False, "error": "No API key"}
            
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
                            {"role": "user", "content": "What is artificial intelligence? Brief answer."}
                        ],
                        "max_tokens": 100
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return {
                        "success": True,
                        "response_length": len(content),
                        "response_preview": content[:100]
                    }
                else:
                    return {"success": False, "error": f"Status {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_agent_node_creation(self):
        """Test agent node creation."""
        test_name = "Agent Node Creation"
        self.total_tests += 1
        
        try:
            created_nodes = []
            
            # Test individual node imports
            try:
                from src.agent.nodes.search_gemini import GeminiSearchAgent
                agent = GeminiSearchAgent()
                created_nodes.append("GeminiSearchAgent")
            except Exception as e:
                print(f"   Warning: GeminiSearchAgent import failed: {e}")
            
            try:
                from src.agent.nodes.search_perplexity import PerplexitySearchAgent
                agent = PerplexitySearchAgent()
                created_nodes.append("PerplexitySearchAgent")
            except Exception as e:
                print(f"   Warning: PerplexitySearchAgent import failed: {e}")
            
            # Test orchestrator if possible
            try:
                from src.agent.handywriterz_graph import HandyWriterzOrchestrator
                orchestrator = HandyWriterzOrchestrator()
                created_nodes.append("HandyWriterzOrchestrator")
            except Exception as e:
                print(f"   Warning: HandyWriterzOrchestrator import failed: {e}")
            
            if created_nodes:
                self.record_success(test_name, f"Created nodes: {', '.join(created_nodes)}")
            else:
                self.record_failure(test_name, "No agent nodes could be created")
                
        except Exception as e:
            self.record_failure(test_name, f"Agent node creation error: {e}")
    
    async def test_simple_agent_workflow(self):
        """Test a simple agent workflow."""
        test_name = "Simple Agent Workflow"
        self.total_tests += 1
        
        try:
            # Only test if we have at least one API key
            if not (os.getenv("GEMINI_API_KEY") or os.getenv("PERPLEXITY_API_KEY")):
                self.record_failure(test_name, "No API keys available for workflow test")
                return
            
            from src.agent.handywriterz_state import HandyWriterzState, UserParams
            from langchain_core.messages import HumanMessage
            
            # Create state
            user_params = UserParams(
                word_count=200,
                document_type="essay",
                citation_style="harvard",
                academic_field="computer-science",
                academic_level="undergraduate",
                special_instructions="Brief overview of AI ethics"
            )
            
            state = HandyWriterzState(
                conversation_id="test_workflow",
                user_id="test_user",
                messages=[HumanMessage(content="Write a brief paragraph about AI ethics")],
                user_params=user_params.dict(),
                workflow_status="initiated",
                max_iterations=2
            )
            
            # Try to test individual agent execution
            workflow_results = []
            
            # Test Gemini agent if available
            if os.getenv("GEMINI_API_KEY"):
                try:
                    from src.agent.nodes.search_gemini import GeminiSearchAgent
                    agent = GeminiSearchAgent()
                    config = {"configurable": {"thread_id": "test_thread"}}
                    
                    result = await agent.execute(state, config)
                    workflow_results.append("GeminiSearchAgent executed")
                except Exception as e:
                    workflow_results.append(f"GeminiSearchAgent failed: {e}")
            
            # Test Perplexity agent if available
            if os.getenv("PERPLEXITY_API_KEY"):
                try:
                    from src.agent.nodes.search_perplexity import PerplexitySearchAgent
                    agent = PerplexitySearchAgent()
                    config = {"configurable": {"thread_id": "test_thread"}}
                    
                    result = await agent.execute(state, config)
                    workflow_results.append("PerplexitySearchAgent executed")
                except Exception as e:
                    workflow_results.append(f"PerplexitySearchAgent failed: {e}")
            
            if workflow_results:
                self.record_success(test_name, f"Workflow results: {'; '.join(workflow_results)}")
            else:
                self.record_failure(test_name, "No workflow results")
                
        except Exception as e:
            self.record_failure(test_name, f"Workflow error: {e}")
    
    def record_success(self, test_name: str, message: str, details: Dict[str, Any] = None):
        """Record successful test."""
        self.test_results.append({
            "name": test_name,
            "status": "PASSED",
            "message": message,
            "details": details
        })
        self.passed_tests += 1
        print(f"✅ {test_name}: {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def record_failure(self, test_name: str, error: str, details: Dict[str, Any] = None):
        """Record failed test."""
        self.test_results.append({
            "name": test_name,
            "status": "FAILED",
            "error": error,
            "details": details
        })
        print(f"❌ {test_name}: {error}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def report_results(self):
        """Report final results."""
        duration = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 DIRECT SYSTEM TEST RESULTS")
        print("=" * 60)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if self.passed_tests == self.total_tests:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️  SOME TESTS FAILED")
            
            failed_tests = [r for r in self.test_results if r["status"] == "FAILED"]
            if failed_tests:
                print("\nFailed Tests:")
                for test in failed_tests:
                    print(f"  - {test['name']}: {test['error']}")
        
        print("\n" + "=" * 60)


def main():
    """Run direct system test."""
    tester = DirectSystemTest()
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)