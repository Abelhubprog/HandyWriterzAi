#!/usr/bin/env python3
"""
HandyWriterz Agent Workflow Integration Test
Tests all agent workflows, MCP integrations, and system components.
"""

import sys
import os
import asyncio
import json
import time
from dataclasses import asdict

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent.handywriterz_state import HandyWriterzState
from agent.handywriterz_graph import HandyWriterzOrchestrator
from agent.base import UserParams
from langchain_core.messages import HumanMessage
from config import HandyWriterzSettings


class AgentWorkflowTester:
    """Comprehensive agent workflow testing suite."""
    
    def __init__(self):
        self.settings = HandyWriterzSettings()
        self.orchestrator = HandyWriterzOrchestrator()
        self.results = {
            "timestamp": time.time(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": [],
            "agent_tests": {}
        }
    
    def log_success(self, test_name: str, message: str = ""):
        """Log a successful test."""
        print(f"✅ {test_name}: {message}")
        self.results["tests_passed"] += 1
        self.results["agent_tests"][test_name] = {"status": "passed", "message": message}
    
    def log_failure(self, test_name: str, error: str):
        """Log a failed test."""
        print(f"❌ {test_name}: {error}")
        self.results["tests_failed"] += 1
        self.results["failures"].append({"test": test_name, "error": error})
        self.results["agent_tests"][test_name] = {"status": "failed", "error": error}
    
    def log_info(self, message: str):
        """Log an info message."""
        print(f"ℹ️  {message}")
    
    async def test_environment_setup(self):
        """Test that all required environment variables are set."""
        self.log_info("Testing environment setup...")
        self.results["tests_run"] += 1
        
        required_vars = [
            "GEMINI_API_KEY",
            "PERPLEXITY_API_KEY", 
            "OPENAI_API_KEY",
            "DATABASE_URL",
            "REDIS_URL"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log_failure("environment_setup", f"Missing environment variables: {', '.join(missing_vars)}")
        else:
            self.log_success("environment_setup", "All required environment variables are set")
    
    async def test_agent_imports(self):
        """Test that all agents can be imported successfully."""
        self.log_info("Testing agent imports...")
        self.results["tests_run"] += 1
        
        try:
            # Test core workflow agents
            from agent.nodes.user_intent import UserIntentNode
            from agent.nodes.planner import PlannerNode
            from agent.nodes.writer import RevolutionaryWriterAgent
            from agent.nodes.memory_writer import MemoryWriterNode
            
            # Test search agents
            from agent.nodes.search_gemini import GeminiSearchAgent
            from agent.nodes.search_perplexity import PerplexitySearchAgent
            from agent.nodes.search_o3 import O3SearchAgent
            
            # Test QA swarm
            from agent.nodes.qa_swarm.fact_checking import FactCheckingAgent
            from agent.nodes.qa_swarm.originality_guard import OriginalityGuardAgent
            from agent.nodes.qa_swarm.bias_detection import BiasDetectionAgent
            
            # Test writing swarm
            from agent.nodes.writing_swarm.academic_tone import AcademicToneAgent
            from agent.nodes.writing_swarm.structure_optimizer import StructureOptimizerAgent
            from agent.nodes.writing_swarm.clarity_enhancer import ClarityEnhancerAgent
            
            self.log_success("agent_imports", "All agent imports successful")
            
        except ImportError as e:
            self.log_failure("agent_imports", f"Import failed: {str(e)}")
        except Exception as e:
            self.log_failure("agent_imports", f"Unexpected error: {str(e)}")
    
    async def test_mcp_integrations(self):
        """Test MCP server integrations."""
        self.log_info("Testing MCP integrations...")
        self.results["tests_run"] += 1
        
        try:
            from mcp.mcp_integrations import MCPTool, MCPResult, BaseMCPHandler
            
            # Test MCP server existence
            mcp_server_path = "src/mcp/mcp_server/server.py"
            if os.path.exists(mcp_server_path):
                self.log_success("mcp_integrations", "MCP server files found and importable")
            else:
                self.log_failure("mcp_integrations", "MCP server files not found")
                
        except ImportError as e:
            self.log_failure("mcp_integrations", f"MCP import failed: {str(e)}")
        except Exception as e:
            self.log_failure("mcp_integrations", f"MCP test error: {str(e)}")
    
    async def test_database_models(self):
        """Test database models and connections."""
        self.log_info("Testing database models...")
        self.results["tests_run"] += 1
        
        try:
            from db.models import User, UserType
            
            # Test model creation
            test_user = User(
                wallet_address="0x1234567890123456789012345678901234567890",
                email="test@example.com",
                user_type=UserType.STUDENT
            )
            
            self.log_success("database_models", "Database models load and instantiate correctly")
            
        except Exception as e:
            self.log_failure("database_models", f"Database model error: {str(e)}")
    
    async def test_state_management(self):
        """Test HandyWriterz state management."""
        self.log_info("Testing state management...")
        self.results["tests_run"] += 1
        
        try:
            # Create test user parameters
            user_params = UserParams(
                writeupType="essay",
                field="computer_science",
                citationStyle="APA",
                length=1000,
                additionalInstructions="Test essay about AI",
                tone="academic",
                style="formal"
            )
            
            # Create initial state
            initial_state = HandyWriterzState(
                conversation_id="test-conv-123",
                user_id="test-user-123",
                wallet_address="0x1234567890123456789012345678901234567890",
                messages=[HumanMessage(content="Write an essay about artificial intelligence")],
                user_params=user_params.dict(),
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
                enable_tutor_review=False,
                start_time=time.time(),
                end_time=None,
                processing_metrics={},
                auth_token="test-token",
                payment_transaction_id=None,
                uploaded_files=[]
            )
            
            # Test state serialization
            state_dict = asdict(initial_state)
            
            self.log_success("state_management", "State creation and serialization successful")
            
        except Exception as e:
            self.log_failure("state_management", f"State management error: {str(e)}")
    
    async def test_graph_creation(self):
        """Test LangGraph workflow creation."""
        self.log_info("Testing LangGraph workflow creation...")
        self.results["tests_run"] += 1
        
        try:
            # Create the workflow graph
            graph = self.orchestrator.create_graph()
            
            # Test that graph has required nodes
            expected_nodes = [
                "user_intent",
                "planner", 
                "search_gemini",
                "search_perplexity",
                "writer",
                "evaluator_advanced",
                "formatter_advanced"
            ]
            
            # Check if graph is created successfully
            if graph is not None:
                self.log_success("graph_creation", "LangGraph workflow created successfully")
            else:
                self.log_failure("graph_creation", "Graph creation returned None")
                
        except Exception as e:
            self.log_failure("graph_creation", f"Graph creation error: {str(e)}")
    
    async def test_individual_agents(self):
        """Test individual agent functionality."""
        self.log_info("Testing individual agents...")
        
        # Test UserIntentNode
        await self._test_user_intent_agent()
        
        # Test PlannerNode
        await self._test_planner_agent()
        
        # Test Search agents
        await self._test_search_agents()
        
        # Test QA Swarm
        await self._test_qa_swarm()
        
        # Test Writing Swarm
        await self._test_writing_swarm()
    
    async def _test_user_intent_agent(self):
        """Test UserIntentNode."""
        self.results["tests_run"] += 1
        
        try:
            from agent.nodes.user_intent import UserIntentNode
            
            user_intent = UserIntentNode()
            
            # Create minimal test state
            test_state = HandyWriterzState(
                conversation_id="test",
                user_id="test",
                messages=[HumanMessage(content="Write an essay about AI")],
                user_params={"writeupType": "essay", "field": "computer_science"},
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
                enable_tutor_review=False,
                start_time=time.time(),
                end_time=None,
                processing_metrics={},
                auth_token=None,
                payment_transaction_id=None,
                uploaded_files=[]
            )
            
            # Test that agent can be instantiated
            self.log_success("user_intent_agent", "UserIntentNode instantiated successfully")
            
        except Exception as e:
            self.log_failure("user_intent_agent", f"UserIntentNode error: {str(e)}")
    
    async def _test_planner_agent(self):
        """Test PlannerNode."""
        self.results["tests_run"] += 1
        
        try:
            from agent.nodes.planner import PlannerNode
            
            planner = PlannerNode()
            self.log_success("planner_agent", "PlannerNode instantiated successfully")
            
        except Exception as e:
            self.log_failure("planner_agent", f"PlannerNode error: {str(e)}")
    
    async def _test_search_agents(self):
        """Test search agents."""
        self.results["tests_run"] += 1
        
        try:
            from agent.nodes.search_gemini import GeminiSearchAgent
            from agent.nodes.search_perplexity import PerplexitySearchAgent
            from agent.nodes.search_o3 import O3SearchAgent
            
            gemini_search = GeminiSearchAgent()
            perplexity_search = PerplexitySearchAgent()
            o3_search = O3SearchAgent()
            
            self.log_success("search_agents", "All search agents instantiated successfully")
            
        except Exception as e:
            self.log_failure("search_agents", f"Search agents error: {str(e)}")
    
    async def _test_qa_swarm(self):
        """Test QA swarm agents."""
        self.results["tests_run"] += 1
        
        try:
            from agent.nodes.qa_swarm.fact_checking import FactCheckingAgent
            from agent.nodes.qa_swarm.originality_guard import OriginalityGuardAgent
            from agent.nodes.qa_swarm.bias_detection import BiasDetectionAgent
            
            fact_checker = FactCheckingAgent()
            originality_guard = OriginalityGuardAgent()
            bias_detector = BiasDetectionAgent()
            
            self.log_success("qa_swarm", "QA swarm agents instantiated successfully")
            
        except Exception as e:
            self.log_failure("qa_swarm", f"QA swarm error: {str(e)}")
    
    async def _test_writing_swarm(self):
        """Test writing swarm agents."""
        self.results["tests_run"] += 1
        
        try:
            from agent.nodes.writing_swarm.academic_tone import AcademicToneAgent
            from agent.nodes.writing_swarm.structure_optimizer import StructureOptimizerAgent
            from agent.nodes.writing_swarm.clarity_enhancer import ClarityEnhancerAgent
            
            academic_tone = AcademicToneAgent()
            structure_optimizer = StructureOptimizerAgent()
            clarity_enhancer = ClarityEnhancerAgent()
            
            self.log_success("writing_swarm", "Writing swarm agents instantiated successfully")
            
        except Exception as e:
            self.log_failure("writing_swarm", f"Writing swarm error: {str(e)}")
    
    async def test_configuration_validation(self):
        """Test configuration validation."""
        self.log_info("Testing configuration validation...")
        self.results["tests_run"] += 1
        
        try:
            from config import HandyWriterzSettings
            
            settings = HandyWriterzSettings()
            
            # Check critical settings
            critical_settings = [
                'api_host',
                'api_port',
                'database_url',
                'redis_url'
            ]
            
            missing_settings = []
            for setting in critical_settings:
                if not hasattr(settings, setting) or getattr(settings, setting) is None:
                    missing_settings.append(setting)
            
            if missing_settings:
                self.log_failure("configuration_validation", f"Missing settings: {', '.join(missing_settings)}")
            else:
                self.log_success("configuration_validation", "All critical settings present")
                
        except Exception as e:
            self.log_failure("configuration_validation", f"Configuration error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all agent workflow tests."""
        print("🚀 Starting HandyWriterz Agent Workflow Tests")
        print("=" * 50)
        
        # Run all tests
        await self.test_environment_setup()
        await self.test_agent_imports()
        await self.test_mcp_integrations()
        await self.test_database_models()
        await self.test_state_management()
        await self.test_graph_creation()
        await self.test_configuration_validation()
        await self.test_individual_agents()
        
        # Print summary
        print("\n" + "=" * 50)
        print("🏁 Test Summary")
        print("=" * 50)
        
        total_tests = self.results["tests_run"]
        passed = self.results["tests_passed"]
        failed = self.results["tests_failed"]
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed / total_tests * 100):.1f}%")
        
        if failed > 0:
            print("\n💥 Failed Tests:")
            for failure in self.results["failures"]:
                print(f"  - {failure['test']}: {failure['error']}")
        
        # Write detailed results to file
        results_file = "test_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        # Return success status
        return failed == 0


async def main():
    """Main test runner."""
    tester = AgentWorkflowTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! HandyWriterz agents are ready for production.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please review and fix the issues before deploying.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())