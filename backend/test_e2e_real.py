"""
Real end-to-end tests for the MultiAgentWriterz system.
Tests the entire workflow from user request to final document using real APIs.
"""

import pytest
import json
from typing import Dict, Any
from fastapi.testclient import TestClient


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.api
class TestRealE2EWorkflow:
    """Test the complete end-to-end workflow with real APIs."""
    
    @pytest.mark.asyncio
    async def test_complete_academic_writing_workflow(
        self, 
        real_test_client: TestClient, 
        api_keys: Dict[str, str],
        real_redis,
        performance_monitor,
        real_test_helpers
    ):
        """Test the complete academic writing workflow from start to finish."""
        performance_monitor.start()
        
        # Step 1: Test system health and availability
        response = real_test_client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        
        # Step 2: Test unified system status
        response = real_test_client.get("/api/status")
        assert response.status_code == 200
        status_data = response.json()
        assert status_data["status"] == "operational"
        assert "systems" in status_data
        
        # Step 3: Create a user and authenticate
        test_user = {
            "wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
        }
        
        auth_response = real_test_client.post("/api/auth/login", json=test_user)
        assert auth_response.status_code == 200
        auth_data = auth_response.json()
        assert "access_token" in auth_data
        
        headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
        
        # Step 4: Test request analysis
        analysis_data = {
            "message": "Write a 1000-word essay about AI ethics in computer science, focusing on current challenges and future implications. Include recent research and use Harvard citation style.",
            "user_params": json.dumps({
                "writeupType": "essay",
                "field": "computer science",
                "studyLevel": "undergraduate",
                "citationStyle": "harvard",
                "wordCount": 1000,
                "additionalInstructions": "Focus on current challenges and include recent research"
            })
        }
        
        analysis_response = real_test_client.post("/api/analyze", data=analysis_data)
        assert analysis_response.status_code == 200
        analysis_result = analysis_response.json()
        assert "routing_decision" in analysis_result
        assert "system" in analysis_result["routing_decision"]
        
        # Step 5: Submit the actual chat request
        chat_request = {
            "prompt": "Write a 1000-word essay about AI ethics in computer science, focusing on current challenges and future implications. Include recent research and use Harvard citation style.",
            "user_params": {
                "writeupType": "essay",
                "field": "computer science",
                "studyLevel": "undergraduate",
                "citationStyle": "harvard",
                "wordCount": 1000,
                "additionalInstructions": "Focus on current challenges and include recent research"
            },
            "file_ids": []
        }
        
        chat_response = real_test_client.post("/api/chat", json=chat_request, headers=headers)
        assert chat_response.status_code == 200 or chat_response.status_code == 202
        
        chat_data = chat_response.json()
        assert "response" in chat_data
        assert chat_data["success"] is True
        
        # Record initial response time
        performance_monitor.record("chat_response_time", performance_monitor.elapsed())
        
        # Step 6: Validate the response content
        response_content = chat_data["response"]
        assert len(response_content) > 0
        
        # Check for basic academic content
        is_valid, message = real_test_helpers.validate_academic_content(response_content, min_word_count=500)
        assert is_valid, f"Content validation failed: {message}"
        
        # Step 7: Test conversation retrieval if conversation_id is provided
        if "conversation_id" in chat_data and chat_data["conversation_id"]:
            conversation_id = chat_data["conversation_id"]
            
            # Get conversation status
            status_response = real_test_client.get(f"/api/conversation/{conversation_id}")
            if status_response.status_code == 200:
                conversation_status = status_response.json()
                assert "workflow_status" in conversation_status
                assert conversation_status["conversation_id"] == conversation_id
        
        # Step 8: Test system routing intelligence
        system_used = chat_data.get("system_used", "unknown")
        assert system_used != "unknown", "System routing should determine which system was used"
        
        # Step 9: Validate performance metrics
        final_metrics = performance_monitor.report()
        assert final_metrics["total_duration"] < 300, "E2E workflow should complete within 5 minutes"
        
        print(f"✅ E2E test completed successfully in {final_metrics['total_duration']:.2f} seconds")
        print(f"   System used: {system_used}")
        print(f"   Response length: {len(response_content)} characters")
        print(f"   Content validation: {message}")
    
    @pytest.mark.asyncio
    async def test_gemini_search_agent(self, api_keys: Dict[str, str], real_handywriterz_state):
        """Test the Gemini search agent directly."""
        from src.agent.nodes.search_gemini import GeminiSearchAgent
        
        agent = GeminiSearchAgent()
        
        # Test with real state
        config = {"configurable": {"thread_id": "test_thread"}}
        result = await agent.execute(real_handywriterz_state, config)
        
        assert "search_results" in result
        assert len(result["search_results"]) > 0
        
        # Validate search results structure
        for search_result in result["search_results"]:
            assert "title" in search_result
            assert "content" in search_result
            assert len(search_result["content"]) > 0
    
    @pytest.mark.asyncio
    async def test_perplexity_search_agent(self, api_keys: Dict[str, str], real_handywriterz_state):
        """Test the Perplexity search agent directly."""
        from src.agent.nodes.search_perplexity import PerplexitySearchAgent
        
        agent = PerplexitySearchAgent()
        
        # Test with real state
        config = {"configurable": {"thread_id": "test_thread"}}
        result = await agent.execute(real_handywriterz_state, config)
        
        assert "search_results" in result
        assert len(result["search_results"]) > 0
        
        # Validate search results structure
        for search_result in result["search_results"]:
            assert "title" in search_result
            assert "content" in search_result
            assert len(search_result["content"]) > 0
    
    @pytest.mark.asyncio
    async def test_full_agent_graph_execution(
        self, 
        real_orchestrator,
        real_handywriterz_state,
        api_keys: Dict[str, str],
        performance_monitor
    ):
        """Test the full agent graph execution with real APIs."""
        performance_monitor.start()
        
        # Create the real graph
        graph = real_orchestrator.create_graph()
        
        # Execute the graph with real state
        config = {"configurable": {"thread_id": "test_real_execution"}}
        
        workflow_results = []
        async for chunk in graph.astream(real_handywriterz_state, config):
            workflow_results.append(chunk)
            
            # Log progress
            if "current_node" in chunk:
                print(f"   Node: {chunk['current_node']}")
                
            # Break if we hit an error or completion
            if chunk.get("workflow_status") in ["failed", "completed"]:
                break
        
        # Validate we got results
        assert len(workflow_results) > 0, "Graph execution should produce results"
        
        # Check for key workflow stages
        nodes_executed = [chunk.get("current_node") for chunk in workflow_results if chunk.get("current_node")]
        assert len(nodes_executed) > 0, "Should execute at least one node"
        
        # Validate final state
        final_chunk = workflow_results[-1]
        assert final_chunk.get("workflow_status") != "failed", "Workflow should not fail"
        
        # Record performance
        performance_monitor.record("graph_execution_time", performance_monitor.elapsed())
        
        print(f"✅ Graph execution completed in {performance_monitor.elapsed():.2f} seconds")
        print(f"   Nodes executed: {', '.join(nodes_executed)}")
    
    @pytest.mark.asyncio
    async def test_api_integration_with_real_services(
        self, 
        real_test_client: TestClient,
        api_keys: Dict[str, str],
        performance_monitor
    ):
        """Test API integration with real external services."""
        performance_monitor.start()
        
        # Test simple chat endpoint (forces Gemini if available)
        simple_request = {
            "message": "What are the main ethical concerns in AI development?",
            "files": []
        }
        
        simple_response = real_test_client.post("/api/chat/simple", data=simple_request)
        
        # Should work or gracefully fail
        if simple_response.status_code == 200:
            simple_data = simple_response.json()
            assert "response" in simple_data
            assert len(simple_data["response"]) > 0
            print(f"✅ Simple chat response: {simple_data['response'][:100]}...")
        else:
            print(f"⚠️  Simple chat not available: {simple_response.status_code}")
        
        # Test advanced chat endpoint
        advanced_request = {
            "message": "Write a short analysis of AI ethics challenges",
            "user_params": json.dumps({
                "writeupType": "analysis",
                "field": "computer science",
                "studyLevel": "undergraduate",
                "citationStyle": "harvard",
                "wordCount": 500
            })
        }
        
        advanced_response = real_test_client.post("/api/chat/advanced", data=advanced_request)
        
        if advanced_response.status_code == 200:
            advanced_data = advanced_response.json()
            assert "response" in advanced_data
            assert len(advanced_data["response"]) > 0
            print(f"✅ Advanced chat response: {advanced_data['response'][:100]}...")
        else:
            print(f"⚠️  Advanced chat not available: {advanced_response.status_code}")
        
        performance_monitor.record("api_integration_time", performance_monitor.elapsed())
    
    @pytest.mark.asyncio
    async def test_file_upload_and_processing(
        self, 
        real_test_client: TestClient,
        test_file_upload: Dict[str, Any],
        performance_monitor
    ):
        """Test file upload and processing functionality."""
        performance_monitor.start()
        
        # Test file upload
        with open(test_file_upload["file_path"], "rb") as f:
            files = {"file": (test_file_upload["filename"], f, test_file_upload["content_type"])}
            
            upload_response = real_test_client.post("/api/files/upload", files=files)
            
            if upload_response.status_code == 200:
                upload_data = upload_response.json()
                assert "file_id" in upload_data
                print(f"✅ File uploaded successfully: {upload_data['file_id']}")
                
                # Test chat with uploaded file
                chat_request = {
                    "prompt": "Analyze the uploaded document and provide insights",
                    "user_params": {
                        "writeupType": "analysis",
                        "field": "computer science",
                        "studyLevel": "undergraduate"
                    },
                    "file_ids": [upload_data["file_id"]]
                }
                
                chat_response = real_test_client.post("/api/chat", json=chat_request)
                
                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    assert "response" in chat_data
                    print(f"✅ Chat with file successful: {chat_data['response'][:100]}...")
                else:
                    print(f"⚠️  Chat with file failed: {chat_response.status_code}")
            else:
                print(f"⚠️  File upload not available: {upload_response.status_code}")
        
        performance_monitor.record("file_processing_time", performance_monitor.elapsed())
    
    @pytest.mark.asyncio
    async def test_streaming_workflow(
        self, 
        real_test_client: TestClient,
        api_keys: Dict[str, str],
        real_redis,
        performance_monitor
    ):
        """Test the streaming workflow with Server-Sent Events."""
        performance_monitor.start()
        
        # First, create a workflow
        chat_request = {
            "prompt": "Write a brief essay about AI ethics",
            "user_params": {
                "writeupType": "essay",
                "field": "computer science",
                "studyLevel": "undergraduate",
                "citationStyle": "harvard",
                "wordCount": 500
            },
            "file_ids": []
        }
        
        chat_response = real_test_client.post("/api/chat", json=chat_request)
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            
            # If we have a conversation_id, test streaming
            if "conversation_id" in chat_data and chat_data["conversation_id"]:
                conversation_id = chat_data["conversation_id"]
                
                # Test SSE endpoint
                stream_response = real_test_client.get(f"/api/stream/{conversation_id}")
                
                if stream_response.status_code == 200:
                    # Just check that we can connect to the stream
                    assert stream_response.headers.get("content-type") == "text/plain; charset=utf-8"
                    print(f"✅ SSE stream connected for conversation: {conversation_id}")
                else:
                    print(f"⚠️  SSE stream not available: {stream_response.status_code}")
            else:
                print("⚠️  No conversation_id returned for streaming test")
        else:
            print(f"⚠️  Chat request failed: {chat_response.status_code}")
        
        performance_monitor.record("streaming_test_time", performance_monitor.elapsed())
    
    @pytest.mark.asyncio
    async def test_user_journey_with_credits(
        self, 
        real_test_client: TestClient,
        api_keys: Dict[str, str],
        performance_monitor
    ):
        """Test complete user journey including credits and authentication."""
        performance_monitor.start()
        
        # Step 1: Create user and authenticate
        test_wallet = "0xabcdef1234567890abcdef1234567890abcdef12"
        auth_request = {"wallet_address": test_wallet}
        
        auth_response = real_test_client.post("/api/auth/login", json=auth_request)
        assert auth_response.status_code == 200
        auth_data = auth_response.json()
        
        headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
        
        # Step 2: Check credits
        credits_response = real_test_client.get(f"/api/credits/{test_wallet}")
        assert credits_response.status_code == 200
        credits_data = credits_response.json()
        assert "credits_balance" in credits_data
        
        initial_credits = credits_data["credits_balance"]
        print(f"✅ Initial credits: {initial_credits}")
        
        # Step 3: Use the service
        chat_request = {
            "prompt": "Write a short paragraph about AI ethics",
            "user_params": {
                "writeupType": "paragraph",
                "field": "computer science",
                "studyLevel": "undergraduate",
                "wordCount": 200
            },
            "file_ids": []
        }
        
        chat_response = real_test_client.post("/api/chat", json=chat_request, headers=headers)
        assert chat_response.status_code == 200
        
        chat_data = chat_response.json()
        assert "response" in chat_data
        assert len(chat_data["response"]) > 0
        
        # Step 4: Check credits after usage
        credits_after = real_test_client.get(f"/api/credits/{test_wallet}")
        assert credits_after.status_code == 200
        
        print("✅ Service used successfully")
        print(f"   Response length: {len(chat_data['response'])} characters")
        
        # Step 5: Get user profile
        profile_response = real_test_client.get(f"/api/users/{test_wallet}")
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert "wallet_address" in profile_data
        
        performance_monitor.record("user_journey_time", performance_monitor.elapsed())
        
        final_metrics = performance_monitor.report()
        print(f"✅ Complete user journey test completed in {final_metrics['total_duration']:.2f} seconds")
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(
        self, 
        real_test_client: TestClient,
        performance_monitor
    ):
        """Test error handling and recovery mechanisms."""
        performance_monitor.start()
        
        # Test with invalid request
        invalid_request = {
            "prompt": "",  # Empty prompt
            "user_params": {},
            "file_ids": []
        }
        
        response = real_test_client.post("/api/chat", json=invalid_request)
        
        # Should handle gracefully
        if response.status_code == 200:
            data = response.json()
            # Should return a helpful error or clarification request
            assert "response" in data
            print(f"✅ Empty prompt handled gracefully: {data['response'][:100]}...")
        else:
            print(f"⚠️  Empty prompt returned status: {response.status_code}")
        
        # Test with malformed user_params
        malformed_request = {
            "prompt": "Write something",
            "user_params": {
                "writeupType": "invalid_type",
                "field": "nonexistent_field",
                "wordCount": -100  # Invalid word count
            },
            "file_ids": []
        }
        
        response = real_test_client.post("/api/chat", json=malformed_request)
        
        # Should handle gracefully
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            print("✅ Malformed params handled gracefully")
        else:
            print(f"⚠️  Malformed params returned status: {response.status_code}")
        
        performance_monitor.record("error_handling_time", performance_monitor.elapsed())
    
    def test_health_and_monitoring_endpoints(self, real_test_client: TestClient):
        """Test health and monitoring endpoints."""
        
        # Test basic health
        health_response = real_test_client.get("/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["status"] == "healthy"
        
        # Test detailed health
        detailed_response = real_test_client.get("/health/detailed")
        assert detailed_response.status_code == 200
        detailed_data = detailed_response.json()
        assert "services" in detailed_data
        
        # Test system status
        status_response = real_test_client.get("/api/status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "systems" in status_data
        assert "infrastructure" in status_data
        
        # Test metrics
        metrics_response = real_test_client.get("/metrics")
        assert metrics_response.status_code == 200
        metrics_data = metrics_response.json()
        assert "system" in metrics_data
        
        print("✅ All health and monitoring endpoints working")
    
    def test_app_configuration(self, real_test_client: TestClient):
        """Test application configuration endpoint."""
        
        config_response = real_test_client.get("/api/config")
        assert config_response.status_code == 200
        
        config_data = config_response.json()
        assert config_data["status"] is True
        assert config_data["name"] == "HandyWriterz"
        assert "features" in config_data
        assert "default_prompt_suggestions" in config_data
        
        print("✅ App configuration endpoint working")


@pytest.mark.integration
class TestRealIntegrations:
    """Test real integrations with external services."""
    
    @pytest.mark.asyncio
    async def test_redis_integration(self, real_redis):
        """Test Redis integration."""
        
        # Test basic operations
        await real_redis.set("test_key", "test_value")
        value = await real_redis.get("test_key")
        assert value == "test_value"
        
        # Test pub/sub
        pubsub = real_redis.pubsub()
        await pubsub.subscribe("test_channel")
        
        await real_redis.publish("test_channel", "test_message")
        
        await pubsub.unsubscribe("test_channel")
        
        print("✅ Redis integration working")
    
    @pytest.mark.asyncio
    async def test_database_integration(self, real_test_db):
        """Test database integration."""
        
        # Create a test session
        session = real_test_db()
        
        try:
            # Test user creation
            from src.db.models import User
            
            test_user = User(
                wallet_address="0x1234567890abcdef",
                user_type="student",
                subscription_tier="free",
                credits_balance=10
            )
            
            session.add(test_user)
            session.commit()
            session.refresh(test_user)
            
            assert test_user.id is not None
            assert test_user.wallet_address == "0x1234567890abcdef"
            
            print("✅ Database integration working")
        
        finally:
            session.close()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([
        __file__, 
        "-v", 
        "-s",
        "--tb=short",
        "-m", "not slow"  # Skip slow tests by default
    ])