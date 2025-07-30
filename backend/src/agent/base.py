"""Base classes and utilities for HandyWriterz agent nodes."""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Dict, Optional, TypeVar, Callable

import redis
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

# Type variable for generic state
StateType = TypeVar("StateType", bound=Dict[str, Any])

# Redis client for SSE broadcasting
import os
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

logger = logging.getLogger(__name__)


class NodeError(Exception):
    """Base exception for node execution errors."""
    
    def __init__(self, message: str, node_name: str, recoverable: bool = True):
        self.message = message
        self.node_name = node_name
        self.recoverable = recoverable
        super().__init__(message)


class NodeTimeout(NodeError):
    """Exception raised when a node execution times out."""
    
    def __init__(self, node_name: str, timeout_seconds: float):
        super().__init__(
            f"Node {node_name} timed out after {timeout_seconds} seconds",
            node_name,
            recoverable=True
        )


def with_timeout(timeout_seconds: float = 30.0):
    """Decorator to add timeout functionality to async node functions."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                node_name = getattr(func, '__name__', 'unknown')
                raise NodeTimeout(node_name, timeout_seconds)
        return wrapper
    return decorator


def with_retry(max_retries: int = 3, backoff_factor: float = 1.0):
    """Decorator to add retry functionality to node functions."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        wait_time = backoff_factor * (2 ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {wait_time} seconds..."
                        )
                        if asyncio.iscoroutinefunction(func):
                            await asyncio.sleep(wait_time)
                        else:
                            time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            
            raise last_error
        return wrapper
    return decorator


def broadcast_sse_event(conversation_id: str, event_type: str, data: Dict[str, Any]):
    """Broadcast an SSE event to the frontend via Redis pub/sub."""
    try:
        event_data = {
            "type": event_type,
            "timestamp": time.time(),
            "data": data
        }
        redis_client.publish(f"sse:{conversation_id}", str(event_data))
        logger.debug(f"Broadcasted SSE event {event_type} for conversation {conversation_id}")
    except Exception as e:
        logger.error(f"Failed to broadcast SSE event: {e}")


class NodeMetrics(BaseModel):
    """Metrics tracking for node execution."""
    
    node_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def finish(self, success: bool = True, error_message: Optional[str] = None):
        """Mark the node execution as finished."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.error_message = error_message


class BaseNode(ABC):
    """Base class for all HandyWriterz agent nodes."""
    
    def __init__(self, name: str, timeout_seconds: float = 30.0, max_retries: int = 3):
        self.name = name
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.logger = logging.getLogger(f"agent.{name}")
    
    def _get_conversation_id(self, state: StateType) -> str:
        """Extract conversation ID from state."""
        return state.get("conversation_id", "unknown")
    
    def _broadcast_start(self, state: StateType):
        """Broadcast node start event."""
        conversation_id = self._get_conversation_id(state)
        broadcast_sse_event(
            conversation_id,
            "node_start",
            {"node": self.name, "status": "starting"}
        )
    
    def _broadcast_progress(self, state: StateType, message: str, progress: float = None):
        """Broadcast node progress event."""
        conversation_id = self._get_conversation_id(state)
        data = {"node": self.name, "message": message}
        if progress is not None:
            data["progress"] = progress
        broadcast_sse_event(conversation_id, "node_progress", data)
    
    def _broadcast_complete(self, state: StateType, result: Dict[str, Any] = None):
        """Broadcast node completion event."""
        conversation_id = self._get_conversation_id(state)
        data = {"node": self.name, "status": "completed"}
        if result:
            data["result"] = result
        broadcast_sse_event(conversation_id, "node_complete", data)
    
    def _broadcast_error(self, state: StateType, error: Exception):
        """Broadcast node error event."""
        conversation_id = self._get_conversation_id(state)
        broadcast_sse_event(
            conversation_id,
            "node_error",
            {
                "node": self.name,
                "error": str(error),
                "recoverable": getattr(error, 'recoverable', True)
            }
        )
    
    @abstractmethod
    async def execute(self, state: StateType, config: RunnableConfig) -> Dict[str, Any]:
        """Execute the node logic. Must be implemented by subclasses."""
        pass
    
    async def __call__(self, state: StateType, config: RunnableConfig) -> Dict[str, Any]:
        """Main entry point for node execution with error handling and metrics."""
        metrics = NodeMetrics(node_name=self.name, start_time=time.time())
        
        try:
            self.logger.info(f"Starting execution of {self.name}")
            self._broadcast_start(state)
            
            # Execute with timeout and retry logic
            result = await self._execute_with_safeguards(state, config)
            
            metrics.finish(success=True)
            self._broadcast_complete(state, {"execution_time": metrics.duration})
            
            self.logger.info(f"Completed {self.name} in {metrics.duration:.2f}s")
            return result
            
        except Exception as e:
            metrics.finish(success=False, error_message=str(e))
            self._broadcast_error(state, e)
            
            self.logger.error(f"Failed to execute {self.name}: {e}")
            
            # Re-raise the exception to be handled by the graph
            raise NodeError(
                message=str(e),
                node_name=self.name,
                recoverable=getattr(e, 'recoverable', True)
            )
    
    @with_retry(max_retries=3, backoff_factor=1.0)
    @with_timeout(timeout_seconds=30.0)
    async def _execute_with_safeguards(self, state: StateType, config: RunnableConfig) -> Dict[str, Any]:
        """Execute the node with timeout and retry safeguards."""
        return await self.execute(state, config)


class StreamingNode(BaseNode):
    """Base class for nodes that stream output tokens."""
    
    def _broadcast_token(self, state: StateType, token: str):
        """Broadcast a streaming token."""
        conversation_id = self._get_conversation_id(state)
        broadcast_sse_event(
            conversation_id,
            "token",
            {"node": self.name, "token": token}
        )
    
    def _broadcast_chunk(self, state: StateType, chunk: str):
        """Broadcast a text chunk."""
        conversation_id = self._get_conversation_id(state)
        broadcast_sse_event(
            conversation_id,
            "chunk",
            {"node": self.name, "chunk": chunk}
        )


class UserParams(BaseModel):
    """User parameters for academic writing requests."""
    
    word_count: int = Field(default=1000, ge=250, le=10000)
    field: str = Field(default="general")
    writeup_type: str = Field(default="essay")
    source_age_years: int = Field(default=10, ge=1, le=20)
    region: str = Field(default="UK")
    language: str = Field(default="English")
    citation_style: str = Field(default="Harvard")
    
    @property
    def target_sources(self) -> int:
        """Calculate target number of sources based on word count."""
        return max(5, self.word_count // 100)
    
    @property
    def target_pages(self) -> int:
        """Calculate target number of pages based on word count."""
        return max(1, self.word_count // 275)


class DocumentChunk(BaseModel):
    """Represents a processed document chunk."""
    
    chunk_id: str
    document_id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[list[float]] = None
    
    @property
    def token_count(self) -> int:
        """Estimate token count (rough approximation)."""
        return len(self.content.split()) * 1.3


class Source(BaseModel):
    """Represents a research source with metadata."""
    
    url: str
    title: str
    author: Optional[str] = None
    year: Optional[int] = None
    abstract: Optional[str] = None
    credibility_score: float = Field(default=0.0, ge=0.0, le=1.0)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    citation: Optional[str] = None
    doi: Optional[str] = None


class EvaluationResult(BaseModel):
    """Result from the evaluation nodes."""
    
    score: float = Field(ge=0.0, le=100.0)
    feedback: str
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    grade_level: str = Field(default="C")


class TurnitinReport(BaseModel):
    """Turnitin analysis report."""
    
    similarity_score: float = Field(ge=0.0, le=100.0)
    ai_score: float = Field(ge=0.0, le=100.0) 
    highlighted_sections: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    passed: bool = False
    
    @property
    def needs_revision(self) -> bool:
        """Check if the document needs revision."""
        return self.similarity_score > 10.0 or self.ai_score > 0.0