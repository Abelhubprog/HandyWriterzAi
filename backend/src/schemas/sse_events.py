"""
Typed SSE Event Schema with Versioning
Production-grade SSE events with strict type safety and backwards compatibility.
"""

from enum import Enum
from typing import Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime
import time

class SSEEventType(str, Enum):
    """SSE event types for different stages of processing."""
    CONTENT = "content"
    ROUTING = "routing" 
    THINKING = "thinking"
    RESEARCH = "research"
    WRITING = "writing"
    FORMATTING = "formatting"
    DONE = "done"
    ERROR = "error"
    COST = "cost"
    METRICS = "metrics"

class SSEEventVersion(str, Enum):
    """SSE event schema versions for backwards compatibility."""
    V1 = "v1"
    V2 = "v2"  # Future version

class BaseSSEEvent(BaseModel):
    """Base SSE event with version and timestamp."""
    version: SSEEventVersion = Field(default=SSEEventVersion.V1, description="Event schema version")
    type: SSEEventType = Field(..., description="Event type")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp")
    conversation_id: Optional[str] = Field(None, description="Conversation identifier")
    
    class Config:
        use_enum_values = True

class ContentEvent(BaseSSEEvent):
    """Content streaming event."""
    type: Literal[SSEEventType.CONTENT] = SSEEventType.CONTENT
    message: str = Field(..., description="Content message or text chunk")
    is_complete: bool = Field(default=False, description="Whether content is complete")
    word_count: Optional[int] = Field(None, description="Current word count")

class RoutingEvent(BaseSSEEvent):
    """System routing decision event."""
    type: Literal[SSEEventType.ROUTING] = SSEEventType.ROUTING
    system: str = Field(..., description="Selected system (advanced)")
    complexity: float = Field(..., description="Complexity score 1-10")
    reason: str = Field(..., description="Routing decision reason")
    confidence: float = Field(..., description="Routing confidence 0-1")

class ThinkingEvent(BaseSSEEvent):
    """Agent reasoning/thinking event."""
    type: Literal[SSEEventType.THINKING] = SSEEventType.THINKING  
    agent: str = Field(..., description="Agent name generating the thought")
    thought: str = Field(..., description="Agent's reasoning or plan")
    step: Optional[int] = Field(None, description="Step number in reasoning chain")

class ResearchEvent(BaseSSEEvent):
    """Research progress event."""
    type: Literal[SSEEventType.RESEARCH] = SSEEventType.RESEARCH
    query: str = Field(..., description="Search query being processed")
    sources_found: int = Field(..., description="Number of sources discovered")
    agent: str = Field(..., description="Research agent (arxiv, scholar, etc)")
    status: str = Field(..., description="Research status")

class WritingEvent(BaseSSEEvent):
    """Writing progress event."""
    type: Literal[SSEEventType.WRITING] = SSEEventType.WRITING
    section: str = Field(..., description="Section being written")
    progress: float = Field(..., description="Progress percentage 0-100")
    word_count: int = Field(..., description="Current word count")
    agent: str = Field(..., description="Writing agent")

class FormattingEvent(BaseSSEEvent):
    """Document formatting event."""
    type: Literal[SSEEventType.FORMATTING] = SSEEventType.FORMATTING
    stage: str = Field(..., description="Formatting stage")
    citations_added: int = Field(default=0, description="Citations processed")
    quality_score: Optional[float] = Field(None, description="Quality score 0-10")

class DoneEvent(BaseSSEEvent):
    """Processing completion event."""
    type: Literal[SSEEventType.DONE] = SSEEventType.DONE
    message: str = Field(default="Processing completed", description="Completion message")
    final_word_count: Optional[int] = Field(None, description="Final document word count")
    processing_time: Optional[float] = Field(None, description="Total processing time in seconds")
    system_used: str = Field(default="advanced", description="System that processed the request")

class ErrorEvent(BaseSSEEvent):
    """Error event with structured error information."""
    type: Literal[SSEEventType.ERROR] = SSEEventType.ERROR
    error_code: str = Field(..., description="Error code for categorization")
    error_message: str = Field(..., description="Human-readable error message")
    retry_possible: bool = Field(default=True, description="Whether retry is possible")
    recovery_suggestion: Optional[str] = Field(None, description="Suggested recovery action")

class CostEvent(BaseSSEEvent):
    """Cost tracking event."""
    type: Literal[SSEEventType.COST] = SSEEventType.COST
    estimated_cost: float = Field(..., description="Estimated cost in USD")
    tokens_used: int = Field(..., description="Tokens consumed")
    model_used: str = Field(..., description="Model identifier")
    cost_breakdown: Optional[Dict[str, float]] = Field(None, description="Detailed cost breakdown")

class MetricsEvent(BaseSSEEvent):
    """System metrics event."""
    type: Literal[SSEEventType.METRICS] = SSEEventType.METRICS
    agent_metrics: Dict[str, Any] = Field(default_factory=dict, description="Agent performance metrics")
    system_metrics: Dict[str, Any] = Field(default_factory=dict, description="System resource metrics")
    quality_metrics: Dict[str, Any] = Field(default_factory=dict, description="Output quality metrics")

# Union type for all possible SSE events
SSEEvent = Union[
    ContentEvent,
    RoutingEvent, 
    ThinkingEvent,
    ResearchEvent,
    WritingEvent,
    FormattingEvent,
    DoneEvent,
    ErrorEvent,
    CostEvent,
    MetricsEvent
]

class SSEEventFactory:
    """Factory for creating typed SSE events."""
    
    @staticmethod
    def create_event(event_type: SSEEventType, **kwargs) -> SSEEvent:
        """Create a typed SSE event from event type and parameters."""
        event_classes = {
            SSEEventType.CONTENT: ContentEvent,
            SSEEventType.ROUTING: RoutingEvent,
            SSEEventType.THINKING: ThinkingEvent,
            SSEEventType.RESEARCH: ResearchEvent,
            SSEEventType.WRITING: WritingEvent,
            SSEEventType.FORMATTING: FormattingEvent,
            SSEEventType.DONE: DoneEvent,
            SSEEventType.ERROR: ErrorEvent,
            SSEEventType.COST: CostEvent,
            SSEEventType.METRICS: MetricsEvent,
        }
        
        event_class = event_classes.get(event_type)
        if not event_class:
            raise ValueError(f"Unknown event type: {event_type}")
        
        return event_class(**kwargs)
    
    @staticmethod
    def serialize_event(event: SSEEvent) -> str:
        """Serialize event to SSE format."""
        return f"data: {event.json()}\n\n"
    
    @staticmethod
    def deserialize_event(data: str) -> SSEEvent:
        """Deserialize SSE data back to typed event."""
        import json
        
        # Parse the event data
        if data.startswith("data: "):
            data = data[6:]  # Remove "data: " prefix
        
        event_dict = json.loads(data.strip())
        event_type = SSEEventType(event_dict.get("type"))
        
        return SSEEventFactory.create_event(event_type, **event_dict)

# Legacy compatibility functions
def create_legacy_event(event_type: str, **kwargs) -> Dict[str, Any]:
    """Create legacy event format for backwards compatibility."""
    try:
        sse_event_type = SSEEventType(event_type)
        event = SSEEventFactory.create_event(sse_event_type, **kwargs)
        return event.dict()
    except (ValueError, TypeError):
        # Fallback for unknown event types
        return {
            "version": "v1",
            "type": event_type,
            "timestamp": time.time(),
            **kwargs
        }