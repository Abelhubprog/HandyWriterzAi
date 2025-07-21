#!/usr/bin/env python3
"""
Real Agent Workflow Test - Tests the actual MultiAgentWriterz system end-to-end
"""

import asyncio
import os
import sys
import time
from pathlib import Path
import traceback

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv()

async def test_real_agent_workflow():
    """Test the real agent workflow with actual APIs."""
    
    print("🚀 MultiAgentWriterz - Real Agent Workflow Test")
    print("=" * 60)
    
    # Test 1: Basic imports and setup
    print("\n1. Testing Basic System Setup...")
    try:
        from src.main import app
        from src.agent.handywriterz_state import HandyWriterzState, UserParams
        from langchain_core.messages import HumanMessage
        print("✅ Basic imports successful")
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False
    
    # Test 2: API availability
    print("\n2. Checking API Availability...")
    gemini_key = os.getenv("GEMINI_API_KEY")
    perplexity_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not gemini_key and not perplexity_key:
        print("❌ No API keys available")
        return False
    
    available_apis = []
    if gemini_key:
        available_apis.append("Gemini")
    if perplexity_key:
        available_apis.append("Perplexity")
    
    print(f"✅ Available APIs: {', '.join(available_apis)}")
    
    # Test 3: FastAPI Application
    print("\n3. Testing FastAPI Application...")
    try:
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        health_response = client.get("/health")
        if health_response.status_code != 200:
            print(f"❌ Health endpoint failed: {health_response.status_code}")
            return False
        
        # Test system status
        status_response = client.get("/api/status")
        if status_response.status_code != 200:
            print(f"❌ Status endpoint failed: {status_response.status_code}")
            return False
        
        print("✅ FastAPI application working")
        
    except Exception as e:
        print(f"❌ FastAPI test failed: {e}")
        return False
    
    # Test 4: Real API Integration Test
    print("\n4. Testing Real API Integration...")
    
    # Test Gemini API
    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            client = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=gemini_key,
                temperature=0.7
            )
            
            result = await client.ainvoke([
                HumanMessage(content="What is artificial intelligence? Answer in exactly 2 sentences.")
            ])
            
            if len(result.content) > 20:
                print("✅ Gemini API working")
            else:
                print("❌ Gemini API returned insufficient content")
                
        except Exception as e:
            print(f"❌ Gemini API test failed: {e}")
    
    # Test Perplexity API
    if perplexity_key:
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {perplexity_key}",
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
                    if len(content) > 20:
                        print("✅ Perplexity API working")
                    else:
                        print("❌ Perplexity API returned insufficient content")
                else:
                    print(f"❌ Perplexity API failed: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Perplexity API test failed: {e}")
    
    # Test 5: Real Agent Workflow
    print("\n5. Testing Real Agent Workflow...")
    
    try:
        # Create proper user parameters
        user_params = UserParams(
            word_count=500,
            document_type="essay",
            citation_style="harvard",
            academic_field="computer-science",
            academic_level="undergraduate",
            special_instructions="Focus on AI ethics and provide a brief overview"
        )
        
        # Create state
        state = HandyWriterzState(
            conversation_id="test_real_workflow",
            user_id="test_user",
            messages=[HumanMessage(content="Write a 500-word essay about AI ethics in computer science")],
            user_params=user_params.dict(),
            workflow_status="initiated",
            max_iterations=3  # Limit for testing
        )
        
        print("✅ Agent state created successfully")
        
        # Test the unified chat endpoint
        chat_request = {
            "prompt": "Write a 500-word essay about AI ethics in computer science",
            "user_params": user_params.dict(),
            "file_ids": []
        }
        
        start_time = time.time()
        chat_response = client.post("/api/chat", json=chat_request)
        duration = time.time() - start_time
        
        if chat_response.status_code in [200, 202]:
            chat_data = chat_response.json()
            
            if chat_data.get("success", False):
                response_content = chat_data.get("response", "")
                system_used = chat_data.get("system_used", "unknown")
                
                print("✅ Agent workflow completed successfully!")
                print(f"   System used: {system_used}")
                print(f"   Response length: {len(response_content)} characters")
                print(f"   Duration: {duration:.2f} seconds")
                print(f"   Preview: {response_content[:100]}...")
                
                # Validate response quality
                if len(response_content) > 100:
                    print("✅ Response quality acceptable")
                else:
                    print("❌ Response too short")
                    
            else:
                print(f"❌ Agent workflow failed: {chat_data.get('response', 'Unknown error')}")
                return False
        else:
            print(f"❌ Chat endpoint failed: {chat_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Agent workflow test failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 6: Test File Upload Functionality
    print("\n6. Testing File Upload Functionality...")
    
    try:
        # Create a test file
        test_content = b"This is a test document about AI ethics in computer science. It discusses various ethical considerations and challenges in the field."
        
        files = {"file": ("test_document.txt", test_content, "text/plain")}
        
        upload_response = client.post("/api/files/upload", files=files)
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            print(f"✅ File upload successful: {upload_data.get('file_id', 'N/A')}")
        else:
            print(f"⚠️  File upload not available: {upload_response.status_code}")
            
    except Exception as e:
        print(f"⚠️  File upload test failed: {e}")
    
    # Test 7: Test Authentication Flow
    print("\n7. Testing Authentication Flow...")
    
    try:
        auth_request = {
            "wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
        }
        
        auth_response = client.post("/api/auth/login", json=auth_request)
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            if "access_token" in auth_data:
                print("✅ Authentication flow working")
            else:
                print("❌ Authentication response missing token")
        else:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
    
    # Test 8: Test Agent Node Execution (if possible)
    print("\n8. Testing Individual Agent Nodes...")
    
    if gemini_key:
        try:
            from src.agent.nodes.search_gemini import GeminiSearchAgent
            
            agent = GeminiSearchAgent()
            config = {"configurable": {"thread_id": "test_node"}}
            
            # Test with limited state
            result = await agent.execute(state, config)
            
            if "search_result" in result:
                print("✅ Gemini search agent working")
            else:
                print("❌ Gemini search agent failed")
                
        except Exception as e:
            print(f"⚠️  Gemini search agent test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 REAL AGENT WORKFLOW TEST COMPLETED!")
    print("=" * 60)
    
    return True

def main():
    """Run the real agent workflow test."""
    success = asyncio.run(test_real_agent_workflow())
    
    if success:
        print("\n✅ All critical tests passed - System is working!")
        return 0
    else:
        print("\n❌ Some tests failed - Please check the issues above")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)