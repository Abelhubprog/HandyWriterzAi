# NOTE: Example hook usage (reference only):
# from src.turnitin.orchestrator import get_orchestrator
# async def on_document_finalized(job, output_uri: str):
#     # from src.turnitin.models import JobMetadata
#     # await get_orchestrator().start_turnitin_check(job=JobMetadata(**job), input_doc_uri=output_uri)
"""
Production server runner that bypasses configuration issues
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append('src')

# Set minimal required environment variables to avoid parsing issues
os.environ.setdefault('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:3001')
os.environ.setdefault('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3001')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/handywriterz')
os.environ.setdefault('JWT_SECRET_KEY', 'handywriterz_super_secret_jwt_key_2024_minimum_32_characters_long_for_production_security')

# Import and run the main application
try:
    from main import app

    print("Starting HandyWriterz Production Server...")
    print("Multi-Provider AI Architecture Enabled")
    print("Available endpoints:")
    print("  - GET  /api/providers/status")
    print("  - POST /api/chat")
    print("  - POST /api/chat/provider/{provider_name}")
    print("  - POST /api/chat/role/{role}")
    print("  - POST /api/upload")
    print("  - GET  /health")
    print("  - GET  /docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

except Exception as e:
    print(f"Failed to start server: {e}")
    print("Trying alternative approach...")

    # Alternative: Run with minimal FastAPI setup
    from fastapi import FastAPI, UploadFile, File, Form
    from fastapi.middleware.cors import CORSMiddleware
    from typing import List, Optional

    # Initialize our multi-provider system
    try:
        from models.factory import initialize_factory, get_provider
        from models.base import ChatMessage, ModelRole

        # Initialize AI providers
        api_keys = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "gemini": os.getenv("GEMINI_API_KEY"),
            "openrouter": os.getenv("OPENROUTER_API_KEY"),
            "perplexity": os.getenv("PERPLEXITY_API_KEY")
        }

        # Filter out None values
        api_keys = {k: v for k, v in api_keys.items() if v}

        if api_keys:
            ai_factory = initialize_factory(api_keys)
            print(f"AI Factory initialized with providers: {ai_factory.get_available_providers()}")
        else:
            ai_factory = None
            print("No AI providers available")

    except Exception as e:
        print(f"AI Factory initialization failed: {e}")
        ai_factory = None

    # Create minimal FastAPI app
    app = FastAPI()\n\n# Register Turnitin API\ntry:\n    from src.api.turnitin import router as turnitin_router\n    app.include_router(turnitin_router)\nexcept Exception:\n    # Keep app booting even if turnitin module is incomplete\n    pass

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {
            "message": "HandyWriterz Multi-Provider API",
            "status": "operational",
            "providers": ai_factory.get_available_providers() if ai_factory else [],
            "architecture": "multi-provider",
            "version": "1.0.0"
        }

    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "providers": len(ai_factory.get_available_providers()) if ai_factory else 0
        }

    @app.get("/api/providers/status")
    async def providers_status():
        if not ai_factory:
            return {"error": "AI factory not initialized"}

        try:
            stats = ai_factory.get_provider_stats()
            health = await ai_factory.health_check_all()

            return {
                "status": "operational",
                "providers": stats["available_providers"],
                "role_mappings": stats["role_mappings"],
                "health_status": health,
                "total_providers": stats["total_providers"]
            }
        except Exception as e:
            return {"error": f"Failed to get provider status: {e}"}

    @app.post("/api/chat")
    async def chat_endpoint(
        message: str = Form(...),
        provider: Optional[str] = Form(None),
        role: Optional[str] = Form(None)
    ):
        if not ai_factory:
            return {"error": "AI providers not available"}

        try:
            # Get provider based on role or specific provider
            if role:
                try:
                    model_role = ModelRole(role.lower())
                    ai_provider = get_provider(role=model_role)
                except ValueError:
                    available_roles = [r.value for r in ModelRole]
                    return {"error": f"Invalid role. Available: {available_roles}"}
            elif provider:
                ai_provider = get_provider(provider_name=provider)
            else:
                ai_provider = get_provider()  # Default provider

            # Create message
            messages = [ChatMessage(role="user", content=message)]

            # Get response
            response = await ai_provider.chat(messages=messages, max_tokens=500)

            return {
                "success": True,
                "response": response.content,
                "provider": response.provider,
                "model": response.model,
                "usage": response.usage
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.post("/api/upload")
    async def upload_file(
        files: List[UploadFile] = File(...),
        message: Optional[str] = Form(None)
    ):
        try:
            uploaded_files = []

            for file in files:
                content = await file.read()

                if file.content_type and file.content_type.startswith("text"):
                    text_content = content.decode('utf-8', errors='ignore')
                else:
                    text_content = f"Binary file: {file.filename} ({len(content)} bytes)"

                uploaded_files.append({
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": len(content),
                    "content_preview": text_content[:500] + "..." if len(text_content) > 500 else text_content
                })

            # Process with AI if message provided
            ai_response = None
            if message and ai_factory:
                try:
                    ai_provider = get_provider()

                    file_context = f"User uploaded {len(files)} file(s): " + ", ".join([f["filename"] for f in uploaded_files])
                    full_message = f"{file_context}\n\nUser message: {message}"

                    messages = [ChatMessage(role="user", content=full_message)]
                    response = await ai_provider.chat(messages=messages, max_tokens=500)

                    ai_response = {
                        "response": response.content,
                        "provider": response.provider,
                        "model": response.model
                    }
                except Exception as e:
                    ai_response = {"error": f"AI processing failed: {e}"}

            return {
                "success": True,
                "message": "Files uploaded successfully",
                "files": uploaded_files,
                "ai_response": ai_response
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    print("Starting minimal HandyWriterz server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
