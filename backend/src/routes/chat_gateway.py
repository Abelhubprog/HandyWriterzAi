"""
Enhanced Chat and Stream endpoints using the new LLM Gateway system.
Compatible with existing frontend while providing improved model selection.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sse_starlette import EventSourceResponse

from ..auth.auth import get_current_user
from ..services.gateway import get_llm_gateway, LLMRequest
from ..services.model_selector import get_model_selector, SelectionContext, SelectionStrategy
from ..services.model_policy import get_model_policy_registry
from ..services.tracing import get_tracer
from ..services.budget import get_budget_guard


chat_gateway_router = APIRouter(prefix="/api/chat", tags=["chat", "gateway"])


# Pydantic Models
class ChatMessage(BaseModel):
    """Chat message"""
    role: str = Field(..., regex="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    """Enhanced chat request with capability hints"""
    messages: List[ChatMessage]
    node_name: Optional[str] = "chat_completion"
    capabilities: List[str] = Field(default_factory=list)
    strategy: SelectionStrategy = SelectionStrategy.BALANCED
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, gt=0, le=8000)
    stream: bool = False
    user_context: Optional[Dict[str, Any]] = None


class StreamRequest(BaseModel):
    """Enhanced streaming request"""
    messages: List[ChatMessage]
    node_name: Optional[str] = "chat_stream"
    capabilities: List[str] = Field(default_factory=list)
    strategy: SelectionStrategy = SelectionStrategy.BALANCED
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, gt=0, le=8000)
    user_context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Chat response with metadata"""
    content: str
    model_used: str
    provider: str
    tokens_used: Dict[str, int]
    cost_usd: float
    latency_ms: int
    trace_id: str
    conversation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StreamChunk(BaseModel):
    """Streaming response chunk"""
    type: str  # "content", "metadata", "error", "done"
    token: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    trace_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Chat Completion Endpoint
@chat_gateway_router.post("/complete", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Enhanced chat completion using intelligent model selection"""
    
    trace_id = str(uuid.uuid4())
    
    try:
        # Initialize services
        gateway = get_llm_gateway()
        selector = get_model_selector()
        budget_guard = get_budget_guard()
        
        # Check user budget (basic check)
        user_id = user.get("id", "anonymous")
        await budget_guard.check_user_budget(user_id)
        
        # Create selection context
        selection_context = SelectionContext(
            node_name=request.node_name,
            capabilities=request.capabilities,
            user_id=user_id,
            strategy=request.strategy,
            trace_id=trace_id
        )
        
        # Select optimal model
        selection_result = await selector.select_model(selection_context)
        
        # Convert messages to gateway format
        gateway_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Create LLM request
        llm_request = LLMRequest(
            messages=gateway_messages,
            model_spec=selection_result.selected_model,
            node_name=request.node_name,
            trace_id=trace_id,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            capabilities=request.capabilities,
            user_id=user_id
        )
        
        # Execute via gateway
        response = await gateway.execute(llm_request)
        
        # Record performance in background
        background_tasks.add_task(
            _record_chat_performance,
            selection_result.selected_model.logical_id,
            True,
            response.latency_ms,
            response.cost_usd,
            response.tokens_used["total"]
        )
        
        return ChatResponse(
            content=response.content,
            model_used=response.model_used,
            provider=response.provider,
            tokens_used=response.tokens_used,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms,
            trace_id=response.trace_id
        )
        
    except Exception as e:
        # Record failure in background
        if 'selection_result' in locals():
            background_tasks.add_task(
                _record_chat_performance,
                selection_result.selected_model.logical_id,
                False,
                0,
                0.0,
                0
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat completion failed: {str(e)}"
        )


# Streaming Chat Endpoint
@chat_gateway_router.post("/stream")
async def chat_stream(
    request: StreamRequest,
    user: dict = Depends(get_current_user)
):
    """Enhanced streaming chat using intelligent model selection"""
    
    trace_id = str(uuid.uuid4())
    
    async def generate_stream():
        try:
            # Initialize services
            gateway = get_llm_gateway()
            selector = get_model_selector()
            budget_guard = get_budget_guard()
            
            # Check user budget
            user_id = user.get("id", "anonymous")
            await budget_guard.check_user_budget(user_id)
            
            # Create selection context
            selection_context = SelectionContext(
                node_name=request.node_name,
                capabilities=request.capabilities,
                user_id=user_id,
                strategy=request.strategy,
                trace_id=trace_id
            )
            
            # Select optimal model
            selection_result = await selector.select_model(selection_context)
            
            # Send initial metadata
            yield {
                "event": "metadata",
                "data": json.dumps({
                    "type": "metadata",
                    "model": selection_result.selected_model.logical_id,
                    "provider": selection_result.selected_model.provider.value,
                    "reasoning": selection_result.reasoning,
                    "trace_id": trace_id,
                    "estimated_cost": selection_result.estimated_cost
                })
            }
            
            # Convert messages
            gateway_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ]
            
            # Create streaming request
            llm_request = LLMRequest(
                messages=gateway_messages,
                model_spec=selection_result.selected_model,
                node_name=request.node_name,
                trace_id=trace_id,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
                capabilities=request.capabilities,
                user_id=user_id
            )
            
            # Stream content
            full_content = ""
            chunk_count = 0
            
            async for chunk in gateway.stream_execute(llm_request):
                if chunk.get("type") == "content":
                    token = chunk.get("token", "")
                    full_content += token
                    chunk_count += 1
                    
                    yield {
                        "event": "content",
                        "data": json.dumps({
                            "type": "content",
                            "token": token,
                            "model": chunk.get("model"),
                            "provider": chunk.get("provider"),
                            "trace_id": trace_id
                        })
                    }
                    
                    # Send progress every 50 chunks
                    if chunk_count % 50 == 0:
                        yield {
                            "event": "progress",
                            "data": json.dumps({
                                "type": "progress",
                                "tokens_generated": len(full_content.split()),
                                "chunk_count": chunk_count
                            })
                        }
                
                elif chunk.get("type") == "error":
                    yield {
                        "event": "error",
                        "data": json.dumps({
                            "type": "error",
                            "error": chunk.get("error"),
                            "provider": chunk.get("provider")
                        })
                    }
                    return
            
            # Send completion event
            yield {
                "event": "done",
                "data": json.dumps({
                    "type": "done",
                    "total_tokens": len(full_content.split()),
                    "chunk_count": chunk_count,
                    "trace_id": trace_id
                })
            }
            
            # Record performance (fire and forget)
            asyncio.create_task(
                _record_chat_performance(
                    selection_result.selected_model.logical_id,
                    True,
                    0,  # Streaming latency is harder to measure
                    selection_result.estimated_cost,
                    len(full_content.split())
                )
            )
            
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({
                    "type": "error",
                    "error": str(e),
                    "trace_id": trace_id
                })
            }
            
            # Record failure
            if 'selection_result' in locals():
                asyncio.create_task(
                    _record_chat_performance(
                        selection_result.selected_model.logical_id,
                        False,
                        0,
                        0.0,
                        0
                    )
                )
    
    return EventSourceResponse(generate_stream())


# Legacy compatibility endpoint for existing frontend
@chat_gateway_router.post("/send")
async def send_message(
    request: Dict[str, Any],
    user: dict = Depends(get_current_user)
):
    """Legacy compatibility endpoint"""
    
    try:
        # Convert legacy request to new format
        messages = request.get("messages", [])
        if isinstance(messages, str):
            # Handle single message format
            messages = [{"role": "user", "content": messages}]
        
        # Extract capabilities from mode or type
        mode = request.get("mode", "general")
        capabilities = _infer_capabilities_from_mode(mode)
        
        chat_request = ChatRequest(
            messages=[ChatMessage(**msg) for msg in messages],
            node_name=f"legacy_{mode}",
            capabilities=capabilities,
            temperature=request.get("temperature", 0.7),
            max_tokens=request.get("max_tokens"),
            stream=request.get("stream", False)
        )
        
        if chat_request.stream:
            return await chat_stream(
                StreamRequest(**chat_request.dict()),
                user=user
            )
        else:
            # Create background tasks dummy for compatibility
            class DummyBackgroundTasks:
                def add_task(self, func, *args, **kwargs):
                    asyncio.create_task(func(*args, **kwargs))
            
            return await chat_completion(
                chat_request,
                background_tasks=DummyBackgroundTasks(),
                user=user
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Legacy request processing failed: {str(e)}"
        )


# Model selection endpoint for frontend hints
@chat_gateway_router.post("/select-model")
async def preview_model_selection(
    node_name: str,
    capabilities: List[str] = [],
    strategy: SelectionStrategy = SelectionStrategy.BALANCED,
    user: dict = Depends(get_current_user)
):
    """Preview model selection without executing"""
    
    try:
        selector = get_model_selector()
        
        selection_context = SelectionContext(
            node_name=node_name,
            capabilities=capabilities,
            user_id=user.get("id", "anonymous"),
            strategy=strategy
        )
        
        result = await selector.select_model(selection_context)
        
        return {
            "selected_model": result.selected_model.logical_id,
            "provider": result.selected_model.provider.value,
            "reasoning": result.reasoning,
            "confidence_score": result.confidence_score,
            "estimated_cost": result.estimated_cost,
            "alternatives": [alt.logical_id for alt in result.alternatives],
            "capabilities": {
                attr: getattr(result.selected_model.capabilities, attr)
                for attr in result.selected_model.capabilities.__dict__
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model selection preview failed: {str(e)}"
        )


# Capabilities discovery endpoint
@chat_gateway_router.get("/capabilities")
async def get_available_capabilities():
    """Get available capabilities for frontend"""
    
    return {
        "capabilities": [
            {
                "name": "streaming",
                "description": "Real-time token streaming",
                "category": "interaction"
            },
            {
                "name": "function_calling",
                "description": "Tool/function calling support",
                "category": "advanced"
            },
            {
                "name": "vision",
                "description": "Image analysis and understanding",
                "category": "multimodal"
            },
            {
                "name": "reasoning",
                "description": "Advanced reasoning and analysis",
                "category": "intelligence"
            },
            {
                "name": "web_search",
                "description": "Real-time web search integration",
                "category": "research"
            },
            {
                "name": "long_context",
                "description": "Extended context window support",
                "category": "context"
            },
            {
                "name": "creative_writing",
                "description": "Creative and academic writing",
                "category": "creativity"
            },
            {
                "name": "code_generation",
                "description": "Code generation and analysis",
                "category": "programming"
            },
            {
                "name": "json_mode",
                "description": "Structured JSON output",
                "category": "formatting"
            }
        ],
        "strategies": [
            {
                "name": "cost_optimized",
                "description": "Choose cheapest viable model"
            },
            {
                "name": "performance_optimized",
                "description": "Choose best performing model"
            },
            {
                "name": "balanced",
                "description": "Balance cost and performance"
            },
            {
                "name": "admin_preferred",
                "description": "Use admin-configured preferences"
            }
        ]
    }


# Helper Functions
async def _record_chat_performance(
    model_id: str,
    success: bool,
    latency_ms: int,
    cost_usd: float,
    tokens_used: int
):
    """Record chat performance metrics"""
    try:
        selector = get_model_selector()
        await selector.record_model_performance(
            model_id=model_id,
            success=success,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            tokens_used=tokens_used
        )
    except Exception as e:
        # Don't fail the request if metrics recording fails
        print(f"Failed to record performance metrics: {e}")


def _infer_capabilities_from_mode(mode: str) -> List[str]:
    """Infer capabilities from legacy mode strings"""
    mode_capabilities = {
        "research": ["web_search", "reasoning", "long_context"],
        "writing": ["creative_writing", "streaming", "long_context"],
        "analysis": ["reasoning", "function_calling"],
        "code": ["code_generation", "function_calling"],
        "creative": ["creative_writing", "streaming"],
        "general": ["streaming"],
        "academic": ["creative_writing", "reasoning", "long_context"]
    }
    
    return mode_capabilities.get(mode.lower(), ["streaming"])