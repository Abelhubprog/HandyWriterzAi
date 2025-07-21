#!/usr/bin/env python3
"""
Simple test server for HandyWriterz backend to test basic functionality.
"""

import sys
import os
import time
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config import get_settings

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="HandyWriterz Test Server",
    version="2.0.0",
    description="Simple test server for HandyWriterz backend"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "HandyWriterz Backend is running!", "version": "2.0.0"}

@app.get("/api/config")
async def get_app_config(request: Request):
    """OpenWebUI-compatible config endpoint."""
    return {
        "status": True,
        "name": "HandyWriterz",
        "version": "2.0.0",
        "default_locale": "en-US",
        "images": {
            "url": "/images",
            "enabled": True
        },
        "ui": {
            "prompt_suggestions": [
                {
                    "title": ["Help me study", "Help me study"],
                    "content": "Help me create comprehensive study materials for my upcoming exam"
                },
                {
                    "title": ["Write a paper", "Write a paper"],
                    "content": "Help me write an academic paper on a specific topic with proper citations"
                },
                {
                    "title": ["Research assistance", "Research assistance"],
                    "content": "Help me find and analyze relevant academic sources for my research"
                }
            ]
        },
        "oauth": {
            "providers": {}
        },
        "audio": {
            "stt": {
                "engine": ""
            },
            "tts": {
                "engine": ""
            }
        },
        "features": {
            "auth": True,
            "enable_signup": True,
            "enable_login_form": True,
            "enable_web_search": True,
            "enable_image_generation": False,
            "enable_community_sharing": False
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "port": settings.api_port
    }

@app.get("/api/version")
async def get_version():
    """Get application version."""
    return {"version": "2.0.0"}

@app.get("/api/auth")
async def get_auth_status():
    """Get authentication status."""
    return {"enabled": False, "required": False}

@app.get("/api/models")
async def get_models():
    """Get available models."""
    return {
        "data": [
            {"id": "handywriterz", "name": "HandyWriterz Multi-Agent", "type": "academic"},
            {"id": "claude-3.5-sonnet", "name": "Claude 3.5 Sonnet", "type": "general"},
            {"id": "gpt-4o", "name": "GPT-4o", "type": "general"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "type": "general"}
        ]
    }

@app.post("/api/chat/completions")
async def chat_completions(request: dict):
    """Handle chat completions."""
    try:
        messages = request.get("messages", [])
        if not messages:
            return {"error": "No messages provided"}
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Simulate academic AI response
        response = {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "handywriterz",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"""Thank you for using HandyWriterz! 🎓

I'm your AI academic writing assistant, powered by a revolutionary multi-agent system. I can help you with:

📝 **Academic Writing**: Essays, research papers, dissertations
🔍 **Research**: Academic source discovery and analysis  
📚 **Citations**: Proper academic formatting and references
✅ **Quality Assurance**: Bias detection, fact-checking, originality verification

**Your request**: "{user_message}"

To provide the best assistance, please specify:
- Type of academic work (essay, research paper, etc.)
- Academic field/subject  
- Word count requirement
- Citation style (APA, Harvard, MLA)

The full multi-agent workflow is currently being deployed. For now, I can provide general academic writing guidance and will soon offer comprehensive research and writing assistance.

How can I help with your academic writing today?"""
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": 100,
                "total_tokens": len(user_message.split()) + 100
            }
        }
        
        return response
        
    except Exception as e:
        return {"error": f"Chat completion failed: {str(e)}"}

@app.post("/api/test-workflow")
async def test_workflow(request: dict):
    """Test basic workflow with available agents."""
    try:
        # Extract user input
        user_input = request.get("message", "")
        if not user_input:
            return {"error": "No message provided"}
        
        # Simulate basic workflow response
        response = {
            "message": f"HandyWriterz received your request: '{user_input}'",
            "status": "processing",
            "workflow_steps": [
                "✅ User intent analyzed",
                "✅ Academic planner initialized", 
                "⏳ Multi-agent search in progress",
                "⏳ AI writing generation pending",
                "⏳ Quality assurance pending"
            ],
            "available_agents": [
                "Enhanced User Intent Agent",
                "Master Orchestrator Agent", 
                "Perplexity Search Agent",
                "Revolutionary Writer Agent",
                "Academic Planner"
            ],
            "next_steps": "Full multi-agent workflow will be available when all agents are connected",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return response
        
    except Exception as e:
        return {"error": f"Workflow test failed: {str(e)}"}

if __name__ == "__main__":
    print(f"🚀 Starting HandyWriterz test server on {settings.api_host}:{settings.api_port}")
    print(f"📝 Environment: {settings.environment}")
    print(f"🔗 Frontend should connect to: http://localhost:{settings.api_port}")
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=False
    )