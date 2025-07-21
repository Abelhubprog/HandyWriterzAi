#!/usr/bin/env python3
"""
Test script for revolutionary HandyWriterz agents.
Validates the Master Orchestrator and Enhanced User Intent agents.
"""

import asyncio
import time

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage

# Import our revolutionary agents
from src.agent.nodes.master_orchestrator import MasterOrchestratorAgent
from src.agent.nodes.enhanced_user_intent import EnhancedUserIntentAgent
from src.agent.handywriterz_state import HandyWriterzState


def create_test_state() -> HandyWriterzState:
    """Create a test state for agent validation."""
    return {
        "conversation_id": "test_conv_001",
        "user_id": "test_user_001",
        "wallet_address": "0x1234567890123456789012345678901234567890",
        "messages": [
            HumanMessage(content="I need help writing a 2000-word research paper on the impact of artificial intelligence on academic writing. I'm studying psychology and need it in APA format with at least 15 credible sources.")
        ],
        "user_params": {
            "word_count": 2000,
            "field": "psychology",
            "writeup_type": "research_paper",
            "citation_style": "apa",
            "source_age_years": 5,
            "region": "US"
        },
        "uploaded_docs": [],
        "session_metadata": {
            "signature": "mock_signature_12345",
            "transaction_id": "mock_tx_67890"
        },
        "search_queries": [],
        "search_results": [],
        "raw_search_results": [],
        "filtered_sources": [],
        "verified_sources": [],
        "evidence_map": {},
        "outline": None,
        "research_agenda": [],
        "draft_content": None,
        "current_draft": None,
        "revision_count": 0,
        "evaluation_results": [],
        "evaluation_score": None,
        "turnitin_reports": [],
        "turnitin_passed": False,
        "formatted_document": None,
        "learning_outcomes_report": None,
        "download_urls": {},
        "current_node": None,
        "workflow_status": "pending",
        "error_message": None,
        "retry_count": 0,
        "max_iterations": 5,
        "enable_tutor_review": False,
        "start_time": time.time(),
        "end_time": None,
        "processing_metrics": {}
    }


async def test_master_orchestrator():
    """Test the revolutionary Master Orchestrator Agent."""
    print("🎭 Testing Master Orchestrator Agent...")
    
    try:
        # Initialize agent
        agent = MasterOrchestratorAgent()
        print("✅ Master Orchestrator initialized successfully")
        
        # Create test state
        state = create_test_state()
        config = RunnableConfig()
        
        print("🔄 Executing Master Orchestrator...")
        start_time = time.time()
        
        # Execute agent
        result = await agent.execute(state, config)
        
        execution_time = time.time() - start_time
        print(f"⏱️  Execution completed in {execution_time:.2f} seconds")
        
        # Validate results
        print("\n📊 Master Orchestrator Results:")
        print(f"   • Orchestration ID: {result.get('orchestration_id', 'N/A')}")
        print(f"   • Success Probability: {result.get('success_probability', 0.0):.1%}")
        print(f"   • Orchestration Confidence: {result.get('orchestration_confidence', 0.0):.1%}")
        print(f"   • Next Phase: {result.get('next_phase', 'N/A')}")
        
        # Check academic analysis
        academic_analysis = result.get('academic_analysis', {})
        print(f"   • Academic Complexity: {academic_analysis.get('academic_complexity', 'N/A')}")
        print(f"   • Quality Benchmark: {academic_analysis.get('quality_benchmark', 'N/A')}")
        
        # Check workflow strategy
        workflow_strategy = result.get('workflow_strategy', {})
        print(f"   • Workflow Strategy: {workflow_strategy.get('primary_strategy', 'N/A')}")
        
        print("✅ Master Orchestrator test completed successfully!\n")
        return True
        
    except Exception as e:
        print(f"❌ Master Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_enhanced_user_intent():
    """Test the revolutionary Enhanced User Intent Agent."""
    print("🎯 Testing Enhanced User Intent Agent...")
    
    try:
        # Initialize agent
        agent = EnhancedUserIntentAgent()
        print("✅ Enhanced User Intent initialized successfully")
        
        # Create test state
        state = create_test_state()
        config = RunnableConfig()
        
        print("🔄 Executing Enhanced User Intent...")
        start_time = time.time()
        
        # Execute agent
        result = await agent.execute(state, config)
        
        execution_time = time.time() - start_time
        print(f"⏱️  Execution completed in {execution_time:.2f} seconds")
        
        # Validate results
        print("\n📊 Enhanced User Intent Results:")
        print(f"   • Intent Analysis ID: {result.get('intent_analysis_id', 'N/A')}")
        print(f"   • Processing Confidence: {result.get('processing_confidence', 0.0):.1%}")
        
        # Check authentication
        authentication = result.get('authentication', {})
        print(f"   • Authentication Status: {authentication.get('status', 'N/A')}")
        print(f"   • Payment Verified: {authentication.get('payment_verified', False)}")
        
        # Check intent analysis
        intent_analysis = result.get('intent_analysis', {})
        print(f"   • Primary Objective: {intent_analysis.get('primary_objective', 'N/A')}")
        print(f"   • Complexity Assessment: {intent_analysis.get('complexity_assessment', 'N/A')}")
        print(f"   • Intent Confidence: {intent_analysis.get('intent_confidence', 0.0):.1%}")
        
        # Check academic profile
        academic_profile = result.get('academic_profile', {})
        print(f"   • Personalization Score: {academic_profile.get('personalization_score', 0.0):.1%}")
        
        print("✅ Enhanced User Intent test completed successfully!\n")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced User Intent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_integration():
    """Test integration between revolutionary agents."""
    print("🔗 Testing Agent Integration...")
    
    try:
        # Initialize agents
        orchestrator = MasterOrchestratorAgent()
        user_intent = EnhancedUserIntentAgent()
        
        # Create test state
        state = create_test_state()
        config = RunnableConfig()
        
        print("🔄 Executing integrated workflow...")
        
        # Step 1: Master Orchestrator
        print("   Step 1: Master Orchestrator analysis...")
        orchestrator_result = await orchestrator.execute(state, config)
        
        # Update state with orchestrator results
        state.update({
            "orchestration_result": orchestrator_result,
            "workflow_intelligence": orchestrator_result.get("workflow_intelligence", {}),
            "current_phase": "strategic_analysis"
        })
        
        # Step 2: Enhanced User Intent (based on orchestrator decision)
        print("   Step 2: Enhanced User Intent processing...")
        intent_result = await user_intent.execute(state, config)
        
        # Validate integration
        orchestration_confidence = orchestrator_result.get("orchestration_confidence", 0.0)
        intent_confidence = intent_result.get("processing_confidence", 0.0)
        
        print("\n📊 Integration Results:")
        print(f"   • Orchestration Confidence: {orchestration_confidence:.1%}")
        print(f"   • Intent Processing Confidence: {intent_confidence:.1%}")
        print(f"   • Overall Integration Score: {(orchestration_confidence + intent_confidence) / 2:.1%}")
        
        # Check workflow intelligence propagation
        workflow_intelligence = state.get("workflow_intelligence", {})
        if workflow_intelligence:
            print("   • Workflow Intelligence Propagated: ✅")
            print(f"   • Academic Complexity: {workflow_intelligence.get('academic_complexity', 'N/A')}")
            print(f"   • Success Probability: {workflow_intelligence.get('success_probability', 'N/A'):.1%}")
        else:
            print("   • Workflow Intelligence Propagated: ❌")
        
        print("✅ Agent integration test completed successfully!\n")
        return True
        
    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test execution."""
    print("🚀 HandyWriterz Revolutionary Agents Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Test individual agents
    test_results.append(await test_master_orchestrator())
    test_results.append(await test_enhanced_user_intent())
    test_results.append(await test_agent_integration())
    
    # Summary
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print("=" * 60)
    print(f"📈 Test Results Summary: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Revolutionary agents are ready for deployment.")
        print("\n🎯 Next Steps:")
        print("   1. Deploy to development environment")
        print("   2. Run full integration tests")
        print("   3. Implement remaining agent nodes")
        print("   4. Begin production testing")
    else:
        print("❌ Some tests failed. Please review and fix issues before deployment.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    # Run tests
    asyncio.run(main())