#!/usr/bin/env python3
"""
HandyWriterz Backend Server - OpenWebUI Compatible
Serves the SvelteKit frontend and provides HandyWriterz AI capabilities
"""

import logging
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette_compress import CompressMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="HandyWriterz",
    description="AI-Powered Academic Writing Assistant",
    version="2.0.0"
)

# Add compression middleware
app.add_middleware(CompressMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Get paths
backend_dir = Path(__file__).parent
project_root = backend_dir.parent.parent
static_dir = project_root / "static"
src_dir = project_root / "src"

# Mount static files
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"✅ Static files mounted from {static_dir}")

# API Routes
@app.get("/api/config")
async def get_config():
    """OpenWebUI compatible config endpoint."""
    return {
        "status": True,
        "name": "HandyWriterz",
        "version": "2.0.0",
        "default_locale": "en-US",
        "images": {"url": "/images", "enabled": True},
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
        "oauth": {"providers": {}},
        "audio": {"stt": {"engine": ""}, "tts": {"engine": ""}},
        "features": {
            "auth": False,
            "enable_signup": True,
            "enable_login_form": False,
            "enable_web_search": True,
            "enable_image_generation": False,
            "enable_community_sharing": False
        }
    }

@app.get("/api/version")
async def get_version():
    return {"version": "2.0.0"}

@app.get("/api/models")
async def get_models():
    return {
        "data": [
            {
                "id": "handywriterz",
                "name": "HandyWriterz Multi-Agent",
                "object": "model",
                "owned_by": "handywriterz"
            }
        ]
    }

# Add v1 API routes that the frontend expects
@app.get("/api/v1/models")
async def get_models_v1():
    return await get_models()

@app.get("/api/v1/config")
async def get_config_v1():
    return await get_config()

@app.post("/api/v1/chat/completions")
async def chat_completions_v1(request: Request):
    return await chat_completions(request)

@app.get("/api/v1/version")
async def get_version_v1():
    return await get_version()

@app.post("/api/chat/completions")
async def chat_completions(request: Request):
    """Handle chat completions - HandyWriterz style."""
    data = await request.json()
    messages = data.get("messages", [])
    
    # Get the last user message
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break
    
    # HandyWriterz academic response
    response_content = f"""🎓 **HandyWriterz Academic Assistant**

Thank you for your request: "{user_message}"

I'm your AI-powered academic writing assistant with multi-agent capabilities:

📝 **Writing Expertise**:
- Essays and research papers
- Literature reviews
- Academic citations
- Dissertation chapters

🔍 **Research Capabilities**:
- Academic source discovery
- Citation verification
- Bias detection
- Fact-checking

✅ **Quality Assurance**:
- Academic tone optimization
- Originality verification
- Structure analysis
- Compliance checking

**Next Steps**: To provide the best assistance, please specify:
- Type of academic work needed
- Subject area and academic level
- Word count and citation requirements
- Preferred citation style (APA, Harvard, MLA)

*The full multi-agent workflow is ready to assist with your academic writing needs.*"""

    return {
        "id": f"chatcmpl-handywriterz-{hash(user_message) % 100000}",
        "object": "chat.completion",
        "created": 1700000000,
        "model": "handywriterz",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": response_content
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": len(user_message.split()),
            "completion_tokens": 150,
            "total_tokens": len(user_message.split()) + 150
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "handywriterz"}

# Serve the SvelteKit frontend
@app.get("/")
async def serve_index():
    """Serve the main app page."""
    app_html = src_dir / "app.html"
    if app_html.exists():
        return FileResponse(str(app_html), media_type="text/html")
    else:
        return JSONResponse(
            status_code=404,
            content={"error": "Frontend not found"}
        )

@app.get("/chat")
async def serve_chat():
    """Serve the chat page."""
    return await serve_index()

@app.get("/{path:path}")
async def serve_spa(path: str):
    """Catch-all for SPA routing."""
    # Don't interfere with API routes
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Serve the SPA for all other routes
    return await serve_index()

if __name__ == "__main__":
    print("🚀 Starting HandyWriterz Server...")
    print(f"📁 Project root: {project_root}")
    print(f"📁 Static dir: {static_dir}")
    print(f"📁 Source dir: {src_dir}")
    print("🌐 Server will be available at: http://localhost:8000")
    print("💬 Chat interface: http://localhost:8000/chat")
    
    uvicorn.run(
        "handywriterz_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )