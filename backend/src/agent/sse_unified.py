"""
Unified SSE Publisher with Schema Validation and Backpressure Control
Ensures consistent, validated event streaming across all multi-agent workflows.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Set, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import redis.asyncio as redis
from pydantic import BaseModel, ValidationError
import logging
from contextlib import asynccontextmanager
import jsonschema
from collections import deque
import os

logger = logging.getLogger(__name__)

class EventType(Enum):
    START = "start"
    ROUTING = "routing"
    NODE_START = "node_start"
    CONTENT = "content"
    NODE_END = "node_end"
    PROGRESS = "progress"
    COST_UPDATE = "cost_update"
    ERROR = "error"
    DONE = "done"

class Phase(Enum):
    INIT = "init"
    RESEARCH = "research"
    AGGREGATION = "aggregation"
    WRITING = "writing"
    EVALUATION = "evaluation"
    FORMATTING = "formatting"
    COMPLETE = "complete"

@dataclass
class SSEEvent:
    """Unified SSE event structure"""
    version: str = "v1"
    event_type: EventType = EventType.CONTENT
    correlation_id: str = ""
    trace_id: Optional[str] = None
    timestamp: str = ""
    seq: int = 0
    node_name: Optional[str] = None
    phase: Optional[Phase] = None
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        if self.data is None:
            self.data = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with enum serialization"""
        result = asdict(self)
        result["event_type"] = self.event_type.value
        if self.phase:
            result["phase"] = self.phase.value
        return result

class SSEPublisher:
    """
    Unified SSE Publisher with schema validation, backpressure control, and feature flag support.
    Handles both Redis pub/sub and direct WebSocket streaming.
    """
    
    def __init__(
        self,
        redis_client: redis.Redis,
        schema_validation: bool = False,
        max_queue_size: int = 1000,
        enable_legacy_publish: bool = False
    ):
        self.redis = redis_client
        self.schema_validation = schema_validation
        self.max_queue_size = max_queue_size
        self.enable_legacy_publish = enable_legacy_publish
        
        # Event queues per conversation
        self.event_queues: Dict[str, asyncio.Queue] = {}
        self.sequence_counters: Dict[str, int] = {}
        
        # Schema validator
        self.schema: Optional[Dict[str, Any]] = None
        if schema_validation:
            self._load_schema()
        
        # Metrics
        self.metrics = {
            "events_published": 0,
            "events_dropped": 0,
            "validation_errors": 0,
            "queue_overflows": 0
        }
        
        # Active streams tracking
        self.active_streams: Set[str] = set()
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.running = False
    
    def _load_schema(self):
        """Load and parse the SSE schema"""
        try:
            schema_path = os.path.join(os.path.dirname(__file__), "../schemas/sse_v1.json")
            
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    self.schema = json.load(f)
                logger.info("SSE schema loaded for validation")
            else:
                logger.warning("SSE schema file not found, validation disabled")
                self.schema_validation = False
        except Exception as e:
            logger.error(f"Failed to load SSE schema: {e}")
            self.schema_validation = False
    
    async def start(self):
        """Start the publisher and background tasks"""
        self.running = True
        
        # Start background queue processors
        self.background_tasks = [
            asyncio.create_task(self._queue_processor()),
            asyncio.create_task(self._metrics_reporter())
        ]
        
        logger.info("SSE Publisher started")
    
    async def stop(self):
        """Stop the publisher and cleanup resources"""
        self.running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Clear queues
        self.event_queues.clear()
        self.sequence_counters.clear()
        self.active_streams.clear()
        
        logger.info("SSE Publisher stopped")
    
    async def publish_event(
        self,
        correlation_id: str,
        event_type: EventType,
        data: Dict[str, Any],
        node_name: Optional[str] = None,
        phase: Optional[Phase] = None,
        trace_id: Optional[str] = None
    ) -> bool:
        """
        Publish a unified SSE event with validation and queuing.
        Returns True if event was queued successfully, False if dropped.
        """
        
        # Get next sequence number
        seq = self.sequence_counters.get(correlation_id, 0)
        self.sequence_counters[correlation_id] = seq + 1
        
        # Create event
        event = SSEEvent(
            event_type=event_type,
            correlation_id=correlation_id,
            trace_id=trace_id,
            seq=seq,
            node_name=node_name,
            phase=phase,
            data=data
        )
        
        # Validate if enabled
        if self.schema_validation and not self._validate_event(event):
            self.metrics["validation_errors"] += 1
            logger.warning(f"Event validation failed for {correlation_id}:{event_type.value}")
            return False
        
        # Check queue capacity and add to queue
        if correlation_id not in self.event_queues:
            self.event_queues[correlation_id] = asyncio.Queue(maxsize=self.max_queue_size)
        
        queue = self.event_queues[correlation_id]
        
        try:
            # Non-blocking put with overflow handling
            queue.put_nowait(event)
            return True
            
        except asyncio.QueueFull:
            # Handle backpressure
            await self._handle_queue_overflow(correlation_id, event)
            return False
    
    def _validate_event(self, event: SSEEvent) -> bool:
        """Validate event against JSON schema"""
        if not self.schema:
            return True
        
        try:
            event_dict = event.to_dict()
            jsonschema.validate(event_dict, self.schema)
            return True
        except jsonschema.ValidationError as e:
            logger.debug(f"Schema validation error: {e.message}")
            return False
        except Exception as e:
            logger.warning(f"Unexpected validation error: {e}")
            return False
    
    async def _handle_queue_overflow(self, correlation_id: str, event: SSEEvent):
        """Handle queue overflow with intelligent backpressure"""
        self.metrics["queue_overflows"] += 1
        
        queue = self.event_queues[correlation_id]
        
        # Strategy 1: Drop older progress events in favor of new ones
        if event.event_type in [EventType.PROGRESS, EventType.CONTENT]:
            dropped_count = 0
            temp_events = []
            
            # Extract all events
            while not queue.empty():
                try:
                    old_event = queue.get_nowait()
                    if old_event.event_type == EventType.PROGRESS and event.event_type == EventType.PROGRESS:
                        # Drop old progress events
                        dropped_count += 1
                    else:
                        temp_events.append(old_event)
                except asyncio.QueueEmpty:
                    break
            
            # Put back non-progress events and new event
            for old_event in temp_events:
                try:
                    queue.put_nowait(old_event)
                except asyncio.QueueFull:
                    break
            
            try:
                queue.put_nowait(event)
                if dropped_count > 0:
                    logger.debug(f"Dropped {dropped_count} old progress events for {correlation_id}")
            except asyncio.QueueFull:
                # Still couldn't fit, emit flow control warning
                await self._emit_flow_control_warning(correlation_id)
        
        else:
            # For critical events, emit flow control warning
            await self._emit_flow_control_warning(correlation_id)
    
    async def _emit_flow_control_warning(self, correlation_id: str):
        """Emit a flow control warning event"""
        warning_event = SSEEvent(
            event_type=EventType.ERROR,
            correlation_id=correlation_id,
            seq=self.sequence_counters.get(correlation_id, 0),
            data={
                "error_type": "system",
                "error_code": "FLOW_CONTROL",
                "message": "Event queue overflow, some events may be dropped",
                "retryable": False
            }
        )
        
        # Try to publish warning (bypass normal queue)
        await self._direct_publish(warning_event)
    
    async def _queue_processor(self):
        """Background task to process event queues"""
        while self.running:
            try:
                # Process all active queues
                for correlation_id in list(self.event_queues.keys()):
                    queue = self.event_queues[correlation_id]
                    
                    # Process up to 10 events per queue per iteration
                    for _ in range(10):
                        try:
                            event = queue.get_nowait()
                            await self._direct_publish(event)
                            self.metrics["events_published"] += 1
                            
                        except asyncio.QueueEmpty:
                            break
                        except Exception as e:
                            logger.error(f"Error processing event for {correlation_id}: {e}")
                            self.metrics["events_dropped"] += 1
                
                # Cleanup empty queues
                empty_queues = [
                    cid for cid, queue in self.event_queues.items()
                    if queue.empty() and cid not in self.active_streams
                ]
                
                for cid in empty_queues:
                    del self.event_queues[cid]
                    if cid in self.sequence_counters:
                        del self.sequence_counters[cid]
                
                await asyncio.sleep(0.01)  # 10ms processing interval
                
            except Exception as e:
                logger.error(f"Queue processor error: {e}")
                await asyncio.sleep(1)
    
    async def _direct_publish(self, event: SSEEvent):
        """Directly publish event to Redis and WebSocket channels"""
        event_dict = event.to_dict()
        event_json = json.dumps(event_dict)
        
        # Unified channel publish
        unified_channel = f"sse:unified:{event.correlation_id}"
        await self.redis.publish(unified_channel, event_json)
        
        # Legacy publish if enabled (for canary deployments)
        if self.enable_legacy_publish:
            legacy_channel = f"sse:legacy:{event.correlation_id}"
            legacy_data = {
                "type": event.event_type.value,
                "data": event.data
            }
            await self.redis.publish(legacy_channel, json.dumps(legacy_data))
    
    async def _metrics_reporter(self):
        """Background task to report metrics"""
        while self.running:
            try:
                # Store metrics in Redis for monitoring
                await self.redis.hset(
                    "handywriterz:sse_metrics",
                    mapping=self.metrics
                )
                
                await asyncio.sleep(60)  # Report every minute
                
            except Exception as e:
                logger.error(f"Metrics reporter error: {e}")
                await asyncio.sleep(60)
    
    def register_stream(self, correlation_id: str):
        """Register an active stream to prevent queue cleanup"""
        self.active_streams.add(correlation_id)
    
    def unregister_stream(self, correlation_id: str):
        """Unregister a stream when client disconnects"""
        self.active_streams.discard(correlation_id)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get publisher metrics"""
        return {
            **self.metrics,
            "active_streams": len(self.active_streams),
            "active_queues": len(self.event_queues),
            "schema_validation_enabled": self.schema_validation,
            "legacy_publish_enabled": self.enable_legacy_publish
        }
    
    # Convenience methods for common event types
    
    async def publish_start(
        self,
        correlation_id: str,
        workflow_id: str,
        content_type: str,
        complexity_score: float,
        estimated_duration: Optional[float] = None,
        trace_id: Optional[str] = None
    ):
        """Publish workflow start event"""
        return await self.publish_event(
            correlation_id=correlation_id,
            event_type=EventType.START,
            phase=Phase.INIT,
            trace_id=trace_id,
            data={
                "workflow_id": workflow_id,
                "content_type": content_type,
                "complexity_score": complexity_score,
                "estimated_duration": estimated_duration
            }
        )
    
    async def publish_routing(
        self,
        correlation_id: str,
        system: str,
        reason: str,
        complexity_score: float,
        estimated_cost: Optional[float] = None,
        trace_id: Optional[str] = None
    ):
        """Publish routing decision event"""
        return await self.publish_event(
            correlation_id=correlation_id,
            event_type=EventType.ROUTING,
            phase=Phase.INIT,
            trace_id=trace_id,
            data={
                "system": system,
                "reason": reason,
                "complexity_score": complexity_score,
                "estimated_cost": estimated_cost
            }
        )
    
    async def publish_content(
        self,
        correlation_id: str,
        content: str,
        section: Optional[str] = None,
        is_partial: bool = False,
        node_name: Optional[str] = None,
        phase: Optional[Phase] = None,
        trace_id: Optional[str] = None
    ):
        """Publish content streaming event"""
        return await self.publish_event(
            correlation_id=correlation_id,
            event_type=EventType.CONTENT,
            node_name=node_name,
            phase=phase,
            trace_id=trace_id,
            data={
                "content": content,
                "content_type": "text",
                "section": section,
                "is_partial": is_partial,
                "word_count": len(content.split()) if content else 0
            }
        )
    
    async def publish_progress(
        self,
        correlation_id: str,
        progress: float,
        stage: str,
        eta_seconds: Optional[float] = None,
        completed_tasks: Optional[int] = None,
        total_tasks: Optional[int] = None,
        phase: Optional[Phase] = None,
        trace_id: Optional[str] = None
    ):
        """Publish progress update event"""
        return await self.publish_event(
            correlation_id=correlation_id,
            event_type=EventType.PROGRESS,
            phase=phase,
            trace_id=trace_id,
            data={
                "progress": progress,
                "stage": stage,
                "eta_seconds": eta_seconds,
                "completed_tasks": completed_tasks,
                "total_tasks": total_tasks
            }
        )
    
    async def publish_error(
        self,
        correlation_id: str,
        error_type: str,
        message: str,
        retryable: bool = False,
        error_code: Optional[str] = None,
        retry_after_seconds: Optional[float] = None,
        node_name: Optional[str] = None,
        phase: Optional[Phase] = None,
        trace_id: Optional[str] = None
    ):
        """Publish error event"""
        return await self.publish_event(
            correlation_id=correlation_id,
            event_type=EventType.ERROR,
            node_name=node_name,
            phase=phase,
            trace_id=trace_id,
            data={
                "error_type": error_type,
                "error_code": error_code,
                "message": message,
                "retryable": retryable,
                "retry_after_seconds": retry_after_seconds
            }
        )
    
    async def publish_done(
        self,
        correlation_id: str,
        success: bool,
        total_duration_ms: float,
        total_cost: float,
        word_count: Optional[int] = None,
        quality_metrics: Optional[Dict[str, float]] = None,
        output_sections: Optional[List[str]] = None,
        trace_id: Optional[str] = None
    ):
        """Publish workflow completion event"""
        return await self.publish_event(
            correlation_id=correlation_id,
            event_type=EventType.DONE,
            phase=Phase.COMPLETE,
            trace_id=trace_id,
            data={
                "success": success,
                "total_duration_ms": total_duration_ms,
                "total_cost": total_cost,
                "word_count": word_count,
                "quality_metrics": quality_metrics,
                "output_sections": output_sections
            }
        )


# Global publisher instance (initialized by application)
sse_publisher: Optional[SSEPublisher] = None

def get_sse_publisher() -> Optional[SSEPublisher]:
    """Get the global SSE publisher instance"""
    return sse_publisher

def initialize_sse_publisher(
    redis_client: redis.Redis,
    schema_validation: bool = False,
    enable_legacy_publish: bool = False
) -> SSEPublisher:
    """Initialize the global SSE publisher"""
    global sse_publisher
    sse_publisher = SSEPublisher(
        redis_client=redis_client,
        schema_validation=schema_validation,
        enable_legacy_publish=enable_legacy_publish
    )
    return sse_publisher