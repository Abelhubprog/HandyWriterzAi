"""
Memory API endpoints for HandyWriterzAI.
Provides REST API access to the memory integration system.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from uuid import UUID

from ..services.memory_integrator import get_memory_integrator
from ..db.models import MemoryType
from ..db.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/memory", tags=["memory"])

# Request/Response Models

class MemoryCreateRequest(BaseModel):
    content: str = Field(..., description="Memory content text")
    memory_type: MemoryType = Field(..., description="Type of memory")
    conversation_id: Optional[str] = Field(None, description="Associated conversation ID")
    importance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Importance score (0-1)")
    tags: Optional[List[str]] = Field(default_factory=list, description="Memory tags")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    source_summary: Optional[str] = Field(None, description="How this memory was created")

class MemoryRetrieveRequest(BaseModel):
    query: str = Field(..., description="Search query")
    memory_types: Optional[List[MemoryType]] = Field(None, description="Filter by memory types")
    conversation_id: Optional[str] = Field(None, description="Conversation context")
    k: Optional[int] = Field(8, ge=1, le=20, description="Number of memories to retrieve")
    importance_threshold: Optional[float] = Field(0.3, ge=0.0, le=1.0, description="Minimum importance")
    include_context: bool = Field(True, description="Include memory context")

class MemoryResponse(BaseModel):
    id: str
    content: str
    memory_type: str
    importance_score: float
    similarity_score: Optional[float] = None
    access_frequency: int
    last_accessed: str
    created_at: str
    tags: List[str]
    rank_position: Optional[int] = None
    context: Optional[Dict[str, Any]] = None

class MemoryCreateResponse(BaseModel):
    memory_id: str
    success: bool
    message: str

class MemoryRetrieveResponse(BaseModel):
    memories: List[MemoryResponse]
    count: int
    query: str

class MemoryStatsResponse(BaseModel):
    total_memories: int
    average_importance: float
    max_importance: float
    total_accesses: int
    type_distribution: Dict[str, int]

class ReflectionRequest(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID")
    conversation_context: str = Field(..., description="Full conversation context")
    user_response: str = Field(..., description="Assistant response to reflect on")

class ReflectionResponse(BaseModel):
    created_memory_ids: List[str]
    count: int
    success: bool


# API Endpoints

@router.post("/create", response_model=MemoryCreateResponse)
async def create_memory(
    user_id: str,
    request: MemoryCreateRequest,
    memory_service = Depends(get_memory_integrator)
):
    """Create a new memory for a user."""
    try:
        memory_id = await memory_service.write_memory(
            user_id=user_id,
            content=request.content,
            memory_type=request.memory_type,
            conversation_id=request.conversation_id,
            importance_score=request.importance_score,
            tags=request.tags,
            context=request.context,
            source_summary=request.source_summary
        )
        
        return MemoryCreateResponse(
            memory_id=memory_id,
            success=True,
            message="Memory created successfully"
        )
        
    except Exception as e:
        logger.error(f"Memory creation failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Memory creation failed: {str(e)}")


@router.post("/retrieve", response_model=MemoryRetrieveResponse)
async def retrieve_memories(
    user_id: str,
    request: MemoryRetrieveRequest,
    memory_service = Depends(get_memory_integrator)
):
    """Retrieve relevant memories for a user based on query."""
    try:
        memories = await memory_service.retrieve_memories(
            user_id=user_id,
            query=request.query,
            conversation_id=request.conversation_id,
            memory_types=request.memory_types,
            k=request.k,
            importance_threshold=request.importance_threshold,
            include_context=request.include_context
        )
        
        memory_responses = [
            MemoryResponse(**memory) for memory in memories
        ]
        
        return MemoryRetrieveResponse(
            memories=memory_responses,
            count=len(memory_responses),
            query=request.query
        )
        
    except Exception as e:
        logger.error(f"Memory retrieval failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Memory retrieval failed: {str(e)}")


@router.get("/stats", response_model=MemoryStatsResponse)
async def get_memory_statistics(
    user_id: str,
    memory_service = Depends(get_memory_integrator)
):
    """Get memory statistics for a user."""
    try:
        stats = await memory_service.get_memory_statistics(user_id)
        return MemoryStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Memory statistics failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")


@router.post("/reflect", response_model=ReflectionResponse)
async def perform_reflection(
    user_id: str,
    request: ReflectionRequest,
    memory_service = Depends(get_memory_integrator)
):
    """Perform AI reflection to extract memories from conversation."""
    try:
        memory_ids = await memory_service.reflect_and_extract_memories(
            user_id=user_id,
            conversation_id=request.conversation_id,
            conversation_context=request.conversation_context,
            user_response=request.user_response
        )
        
        return ReflectionResponse(
            created_memory_ids=memory_ids,
            count=len(memory_ids),
            success=True
        )
        
    except Exception as e:
        logger.error(f"Memory reflection failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Reflection failed: {str(e)}")


@router.post("/maintain")
async def maintain_memories(
    user_id: Optional[str] = None,
    batch_size: int = Query(1000, ge=100, le=5000),
    memory_service = Depends(get_memory_integrator)
):
    """Perform memory maintenance (admin endpoint)."""
    try:
        await memory_service.maintain_memories(user_id=user_id, batch_size=batch_size)
        
        return {
            "success": True,
            "message": f"Memory maintenance completed for {'all users' if not user_id else f'user {user_id}'}"
        }
        
    except Exception as e:
        logger.error(f"Memory maintenance failed: {e}")
        raise HTTPException(status_code=500, detail=f"Maintenance failed: {str(e)}")


@router.get("/search")
async def search_memories(
    user_id: str,
    query: str = Query(..., description="Search query"),
    memory_types: Optional[List[str]] = Query(None, description="Filter by memory types"),
    k: int = Query(5, ge=1, le=20, description="Number of results"),
    importance_threshold: float = Query(0.3, ge=0.0, le=1.0, description="Minimum importance"),
    memory_service = Depends(get_memory_integrator)
):
    """Simple memory search endpoint (GET request)."""
    try:
        # Convert string memory types to enum
        parsed_memory_types = None
        if memory_types:
            parsed_memory_types = [MemoryType(mt) for mt in memory_types]
        
        memories = await memory_service.retrieve_memories(
            user_id=user_id,
            query=query,
            memory_types=parsed_memory_types,
            k=k,
            importance_threshold=importance_threshold,
            include_context=False  # Lighter response for search
        )
        
        return {
            "memories": memories,
            "count": len(memories),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Memory search failed for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/types")
async def get_memory_types():
    """Get available memory types."""
    return {
        "memory_types": [
            {
                "value": mt.value,
                "name": mt.value.replace("_", " ").title(),
                "description": _get_memory_type_description(mt)
            }
            for mt in MemoryType
        ]
    }


def _get_memory_type_description(memory_type: MemoryType) -> str:
    """Get description for memory type."""
    descriptions = {
        MemoryType.EPISODIC: "Specific experiences and events",
        MemoryType.SEMANTIC: "Facts, concepts, and knowledge",
        MemoryType.PROCEDURAL: "Skills and processes",
        MemoryType.PREFERENCE: "User preferences and patterns",
        MemoryType.CONTEXTUAL: "Context-dependent information"
    }
    return descriptions.get(memory_type, "Unknown memory type")


# Health check endpoint
@router.get("/health")
async def memory_health_check(memory_service = Depends(get_memory_integrator)):
    """Health check for memory service."""
    try:
        # Simple health check - try to get service instance
        return {
            "status": "healthy",
            "service": "memory_integrator",
            "timestamp": str(datetime.utcnow())
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Memory service unhealthy: {str(e)}")


from datetime import datetime