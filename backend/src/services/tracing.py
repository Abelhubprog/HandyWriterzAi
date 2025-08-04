"""
Distributed tracing system for LLM gateway operations.
Compatible with OpenTelemetry and existing HandyWriterz logging.
"""

import asyncio
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional, AsyncContextManager
from datetime import datetime, timezone

import redis.asyncio as redis
from ..config.settings import get_settings


logger = logging.getLogger(__name__)


@dataclass
class TraceContext:
    """Trace context for distributed tracing"""
    trace_id: str
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    parent_span_id: Optional[str] = None
    operation: str = ""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "started"  # started, completed, error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    def duration_ms(self) -> Optional[int]:
        """Get duration in milliseconds"""
        if self.end_time:
            return int((self.end_time - self.start_time) * 1000)
        return None


class DistributedTracer:
    """Distributed tracing system for LLM operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_client = None
        self._initialize_redis()
        
        # Trace configuration
        self.trace_sampling_rate = 1.0  # Sample all traces in dev
        self.max_trace_retention_hours = 24
        
    def _initialize_redis(self):
        """Initialize Redis connection for trace storage"""
        try:
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis not available for tracing: {e}")
            self.redis_client = None
    
    def generate_trace_id(self) -> str:
        """Generate a new trace ID"""
        return str(uuid.uuid4())
    
    async def _store_trace(self, trace_context: TraceContext):
        """Store trace data in Redis"""
        if not self.redis_client:
            return
            
        try:
            trace_key = f"trace:{trace_context.trace_id}:{trace_context.span_id}"
            trace_data = trace_context.to_dict()
            
            # Store with expiration
            await self.redis_client.setex(
                trace_key,
                self.max_trace_retention_hours * 3600,
                json.dumps(trace_data, default=str)
            )
            
            # Also store in trace index for querying
            index_key = f"trace_index:{trace_context.trace_id}"
            await self.redis_client.sadd(index_key, trace_context.span_id)
            await self.redis_client.expire(index_key, self.max_trace_retention_hours * 3600)
            
        except Exception as e:
            logger.error(f"Failed to store trace: {e}")
    
    @asynccontextmanager
    async def span(
        self, 
        trace_context: TraceContext
    ) -> AsyncContextManager[TraceContext]:
        """Create a traced span context"""
        
        # Start the span
        trace_context.start_time = time.time()
        trace_context.status = "started"
        
        # Log span start
        logger.info(
            f"Starting span: {trace_context.operation}",
            extra={
                "trace_id": trace_context.trace_id,
                "span_id": trace_context.span_id,
                "operation": trace_context.operation
            }
        )
        
        try:
            yield trace_context
            
            # Span completed successfully
            trace_context.end_time = time.time()
            trace_context.status = "completed"
            
            logger.info(
                f"Span completed: {trace_context.operation} ({trace_context.duration_ms()}ms)",
                extra={
                    "trace_id": trace_context.trace_id,
                    "span_id": trace_context.span_id,
                    "duration_ms": trace_context.duration_ms(),
                    "metadata": trace_context.metadata
                }
            )
            
        except Exception as e:
            # Span failed with error
            trace_context.end_time = time.time()
            trace_context.status = "error"
            trace_context.metadata["error"] = str(e)
            
            logger.error(
                f"Span failed: {trace_context.operation} ({trace_context.duration_ms()}ms): {e}",
                extra={
                    "trace_id": trace_context.trace_id,
                    "span_id": trace_context.span_id,
                    "duration_ms": trace_context.duration_ms(),
                    "error": str(e)
                }
            )
            raise
            
        finally:
            # Store trace data
            await self._store_trace(trace_context)
    
    async def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve complete trace by ID"""
        if not self.redis_client:
            return None
            
        try:
            # Get all span IDs for this trace
            index_key = f"trace_index:{trace_id}"
            span_ids = await self.redis_client.smembers(index_key)
            
            if not span_ids:
                return None
            
            # Retrieve all spans
            spans = []
            for span_id in span_ids:
                trace_key = f"trace:{trace_id}:{span_id}"
                span_data = await self.redis_client.get(trace_key)
                if span_data:
                    spans.append(json.loads(span_data))
            
            # Sort spans by start time
            spans.sort(key=lambda s: s.get("start_time", 0))
            
            return {
                "trace_id": trace_id,
                "spans": spans,
                "total_duration_ms": max(
                    (span.get("end_time", 0) - span.get("start_time", 0)) * 1000
                    for span in spans
                ) if spans else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve trace {trace_id}: {e}")
            return None
    
    async def get_recent_traces(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent traces for monitoring"""
        if not self.redis_client:
            return []
            
        try:
            # Get trace index keys (limited scan)
            trace_keys = []
            async for key in self.redis_client.scan_iter(match="trace_index:*"):
                trace_keys.append(key)
                if len(trace_keys) >= limit:
                    break
            
            # Get trace summaries
            traces = []
            for key in trace_keys[-limit:]:  # Most recent
                trace_id = key.split(":", 2)[2]
                trace = await self.get_trace(trace_id)
                if trace:
                    traces.append(trace)
            
            return sorted(traces, key=lambda t: t.get("spans", [{}])[0].get("start_time", 0), reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to get recent traces: {e}")
            return []
    
    async def get_trace_metrics(self, hours: int = 1) -> Dict[str, Any]:
        """Get trace metrics for monitoring"""
        if not self.redis_client:
            return {"error": "Redis not available"}
            
        try:
            # This is a simplified implementation
            # In production, you'd want proper time-based indexing
            recent_traces = await self.get_recent_traces(100)
            
            if not recent_traces:
                return {"total_traces": 0}
            
            # Calculate metrics
            total_traces = len(recent_traces)
            successful_traces = sum(1 for t in recent_traces 
                                  if all(s.get("status") == "completed" 
                                        for s in t.get("spans", [])))
            
            avg_duration = sum(t.get("total_duration_ms", 0) for t in recent_traces) / total_traces if total_traces > 0 else 0
            
            # Operation breakdown
            operations = {}
            for trace in recent_traces:
                for span in trace.get("spans", []):
                    op = span.get("operation", "unknown")
                    if op not in operations:
                        operations[op] = {"count": 0, "avg_duration": 0, "errors": 0}
                    operations[op]["count"] += 1
                    operations[op]["avg_duration"] += span.get("duration_ms", 0)
                    if span.get("status") == "error":
                        operations[op]["errors"] += 1
            
            # Calculate averages
            for op_data in operations.values():
                if op_data["count"] > 0:
                    op_data["avg_duration"] /= op_data["count"]
            
            return {
                "total_traces": total_traces,
                "successful_traces": successful_traces,
                "error_rate": 1 - (successful_traces / total_traces) if total_traces > 0 else 0,
                "avg_duration_ms": avg_duration,
                "operations": operations,
                "time_range_hours": hours
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate metrics: {e}")
            return {"error": str(e)}


class LLMTraceWrapper:
    """Wrapper to easily add tracing to LLM operations"""
    
    def __init__(self, tracer: DistributedTracer):
        self.tracer = tracer
    
    @asynccontextmanager
    async def trace_llm_call(
        self,
        operation: str,
        model: str,
        provider: str,
        trace_id: Optional[str] = None
    ):
        """Context manager for tracing LLM calls"""
        if not trace_id:
            trace_id = self.tracer.generate_trace_id()
        
        trace_context = TraceContext(
            trace_id=trace_id,
            operation=operation,
            metadata={
                "model": model,
                "provider": provider,
                "component": "llm_gateway"
            }
        )
        
        async with self.tracer.span(trace_context) as ctx:
            yield ctx


# Global tracer instance
_tracer_instance = None

def get_tracer() -> DistributedTracer:
    """Get global tracer instance"""
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = DistributedTracer()
    return _tracer_instance


def get_llm_trace_wrapper() -> LLMTraceWrapper:
    """Get LLM trace wrapper"""
    return LLMTraceWrapper(get_tracer())