#!/usr/bin/env python3
"""
Minimal test server to verify chat API integration is working.
This bypasses all the complex systems and just tests the basic API contract.
"""

import os
import uuid
import time
from typing import List, Literal
from pydantic import BaseModel, Field
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Simple schemas matching the main API
class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=16000)
    mode: Literal[
        "general","essay","report","dissertation","case_study","case_scenario",
        "critical_review","database_search","reflection","document_analysis",
        "presentation","poster","exam_prep"
    ]
    file_ids: List[str] = Field(default_factory=list)
    user_params: dict = Field(default_factory=dict)

class ChatResponse(BaseModel):
    success: bool
    trace_id: str
    response: str
    sources: List[dict]
    workflow_status: str
    system_used: str
    complexity_score: float
    routing_reason: str
    processing_time: float

# Create minimal FastAPI app
app = FastAPI(title="HandyWriterz Minimal Test API")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/api/chat")
def minimal_chat_endpoint(req: ChatRequest):
    """
    Minimal chat endpoint to test frontend integration.
    Returns a mock response with correct format.
    """
    print(f"Received chat request: {req.prompt[:100]}...")
    
    # Generate trace_id as expected by frontend
    trace_id = str(uuid.uuid4())
    
    # Mock response that matches expected format
    response = ChatResponse(
        success=True,
        trace_id=trace_id,
        response=f"Mock response for: {req.prompt[:50]}... (Mode: {req.mode})",
        sources=[],
        workflow_status="completed",
        system_used="minimal_test",
        complexity_score=1.0,
        routing_reason="test_endpoint",
        processing_time=0.1
    )
    
    print(f"Returning response with trace_id: {trace_id}")
    return response

if __name__ == "__main__":
    import uvicorn
    print("Starting minimal test server...")
    print("This will test if the chat API integration works without complex dependencies.")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)