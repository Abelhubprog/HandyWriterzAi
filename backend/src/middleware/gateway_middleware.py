"""
Middleware for LLM Gateway trace propagation, cost logging, and performance monitoring.
Integrates with existing FastAPI middleware stack.
"""

import time
import uuid
import json
import logging
from typing import Callable, Optional, Dict, Any
from datetime import datetime

from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..services.tracing import get_tracer, TraceContext
from ..services.cost_tracker import CostTracker
from ..config.settings import get_settings


logger = logging.getLogger(__name__)


class GatewayMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive middleware for LLM Gateway operations.
    Handles trace propagation, cost tracking, and performance monitoring.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
        self.tracer = get_tracer()
        self.cost_tracker = CostTracker()
        
        # Configure which paths to trace
        self.traced_paths = {
            "/api/chat/",
            "/api/agent/",
            "/api/admin/gateway/",
            "/api/stream/"
        }
        
        # Configure which paths to exclude from detailed logging
        self.excluded_paths = {
            "/health",
            "/metrics",
            "/favicon.ico",
            "/static/"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware dispatch logic"""
        
        # Skip middleware for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Generate or extract trace ID
        trace_id = self._get_or_create_trace_id(request)
        
        # Check if this is a traceable request
        should_trace = any(request.url.path.startswith(path) for path in self.traced_paths)
        
        if should_trace:
            return await self._traced_dispatch(request, call_next, trace_id)
        else:
            return await self._simple_dispatch(request, call_next, trace_id)
    
    def _get_or_create_trace_id(self, request: Request) -> str:
        """Get trace ID from headers or create new one"""
        
        # Check various trace ID headers
        trace_headers = [
            "x-trace-id",
            "x-request-id", 
            "trace-id",
            "request-id"
        ]
        
        for header in trace_headers:
            trace_id = request.headers.get(header)
            if trace_id:
                return trace_id
        
        # Generate new trace ID
        return str(uuid.uuid4())
    
    async def _traced_dispatch(self, request: Request, call_next: Callable, trace_id: str) -> Response:
        """Dispatch with full tracing enabled"""
        
        start_time = time.time()
        
        # Create trace context
        trace_context = TraceContext(
            trace_id=trace_id,
            operation=f"{request.method} {request.url.path}",
            metadata={
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "user_agent": request.headers.get("user-agent", "unknown"),
                "client_ip": self._get_client_ip(request),
                "user_id": await self._extract_user_id(request)
            }
        )
        
        # Add trace ID to request state for downstream usage
        request.state.trace_id = trace_id
        
        try:
            async with self.tracer.span(trace_context) as ctx:
                # Execute request
                response = await call_next(request)
                
                # Calculate response metrics
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Update trace context with response info
                ctx.metadata.update({
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "response_size": self._get_response_size(response)
                })
                
                # Add trace ID to response headers
                response.headers["x-trace-id"] = trace_id
                
                # Log request completion
                logger.info(
                    f"Request completed: {request.method} {request.url.path} ({duration_ms}ms)",
                    extra={
                        "trace_id": trace_id,
                        "duration_ms": duration_ms,
                        "status_code": response.status_code,
                        "user_id": ctx.metadata.get("user_id")
                    }
                )
                
                # Track costs if this was an LLM request
                await self._track_request_costs(request, response, trace_id, duration_ms)
                
                return response
                
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Update trace context with error info
            trace_context.metadata.update({
                "error": str(e),
                "duration_ms": duration_ms,
                "status": "error"
            })
            
            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path} ({duration_ms}ms): {e}",
                extra={
                    "trace_id": trace_id,
                    "duration_ms": duration_ms,
                    "error": str(e)
                }
            )
            
            raise
    
    async def _simple_dispatch(self, request: Request, call_next: Callable, trace_id: str) -> Response:
        """Simple dispatch without full tracing"""
        
        # Add trace ID to request state
        request.state.trace_id = trace_id
        
        # Execute request
        response = await call_next(request)
        
        # Add trace ID to response headers
        response.headers["x-trace-id"] = trace_id
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        
        # Check forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request"""
        
        try:
            # Try to extract from JWT or session
            # This depends on your auth implementation
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # Would decode JWT here in real implementation
                return "user_from_jwt"
            
            # Try to extract from session cookie
            session_cookie = request.cookies.get("session")
            if session_cookie:
                return "user_from_session"
                
        except Exception as e:
            logger.warning(f"Failed to extract user ID: {e}")
        
        return None
    
    def _get_response_size(self, response: Response) -> Optional[int]:
        """Get response size if available"""
        
        try:
            if hasattr(response, "body") and response.body:
                return len(response.body)
            
            content_length = response.headers.get("content-length")
            if content_length:
                return int(content_length)
                
        except Exception:
            pass
        
        return None
    
    async def _track_request_costs(self, request: Request, response: Response, trace_id: str, duration_ms: int):
        """Track costs for LLM requests"""
        
        try:
            # Only track costs for chat/LLM endpoints
            if not any(request.url.path.startswith(path) for path in ["/api/chat/", "/api/agent/"]):
                return
            
            # Extract cost information from response if available
            if hasattr(response, "body") and response.body:
                try:
                    # For regular JSON responses
                    body_data = json.loads(response.body.decode())
                    cost_usd = body_data.get("cost_usd", 0.0)
                    tokens_used = body_data.get("tokens_used", {}).get("total", 0)
                    model_used = body_data.get("model_used", "unknown")
                    
                    if cost_usd > 0:
                        await self.cost_tracker.track_request_cost(
                            trace_id=trace_id,
                            model=model_used,
                            cost_usd=cost_usd,
                            tokens_used=tokens_used,
                            duration_ms=duration_ms,
                            endpoint=request.url.path
                        )
                        
                except json.JSONDecodeError:
                    # Not JSON response, skip cost tracking
                    pass
            
            # For streaming responses, costs are tracked elsewhere
            
        except Exception as e:
            logger.warning(f"Failed to track request costs: {e}")


class StreamingMiddleware:
    """
    Specialized middleware for handling streaming responses with tracing.
    Used as a wrapper around streaming generators.
    """
    
    def __init__(self):
        self.tracer = get_tracer()
        self.cost_tracker = CostTracker()
    
    async def wrap_streaming_response(
        self,
        generator,
        trace_id: str,
        operation: str,
        metadata: Dict[str, Any] = None
    ):
        """Wrap streaming generator with tracing"""
        
        if metadata is None:
            metadata = {}
        
        trace_context = TraceContext(
            trace_id=trace_id,
            operation=f"stream_{operation}",
            metadata={
                **metadata,
                "streaming": True
            }
        )
        
        total_chunks = 0
        total_tokens = 0
        
        try:
            async with self.tracer.span(trace_context) as ctx:
                async for chunk in generator:
                    total_chunks += 1
                    
                    # Track token count if available
                    if isinstance(chunk, dict) and chunk.get("data"):
                        try:
                            chunk_data = json.loads(chunk["data"])
                            if chunk_data.get("type") == "content":
                                total_tokens += len(chunk_data.get("token", "").split())
                        except (json.JSONDecodeError, KeyError):
                            pass
                    
                    yield chunk
                
                # Update trace with streaming metrics
                ctx.metadata.update({
                    "total_chunks": total_chunks,
                    "total_tokens": total_tokens,
                    "stream_completed": True
                })
                
        except Exception as e:
            # Update trace with error
            trace_context.metadata.update({
                "error": str(e),
                "total_chunks": total_chunks,
                "stream_failed": True
            })
            
            logger.error(f"Streaming failed for {operation}: {e}")
            raise


class CostTrackingMiddleware(BaseHTTPMiddleware):
    """
    Lightweight middleware focused on cost tracking and rate limiting.
    Can be used independently or with GatewayMiddleware.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.cost_tracker = CostTracker()
        
        # Rate limiting configuration
        self.rate_limits = {
            "/api/chat/": {"requests_per_minute": 60, "cost_per_minute": 1.0},
            "/api/agent/": {"requests_per_minute": 10, "cost_per_minute": 5.0}
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Cost tracking dispatch"""
        
        # Check rate limits before processing
        user_id = await self._get_user_id(request)
        if user_id:
            await self._check_rate_limits(request, user_id)
        
        # Process request
        response = await call_next(request)
        
        # Track costs after processing
        await self._track_endpoint_usage(request, response, user_id)
        
        return response
    
    async def _get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID for rate limiting"""
        # Simplified - would integrate with your auth system
        return request.headers.get("x-user-id") or "anonymous"
    
    async def _check_rate_limits(self, request: Request, user_id: str):
        """Check if user is within rate limits"""
        
        for path_prefix, limits in self.rate_limits.items():
            if request.url.path.startswith(path_prefix):
                # Would implement actual rate limiting logic here
                # For now, just log the check
                logger.debug(f"Rate limit check for {user_id} on {path_prefix}")
                break
    
    async def _track_endpoint_usage(self, request: Request, response: Response, user_id: Optional[str]):
        """Track endpoint usage patterns"""
        
        try:
            usage_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "endpoint": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "user_agent": request.headers.get("user-agent", "unknown")
            }
            
            # Track usage (would store in database or analytics system)
            logger.info("Endpoint usage", extra=usage_data)
            
        except Exception as e:
            logger.warning(f"Failed to track endpoint usage: {e}")


# Factory functions for easy middleware setup
def create_gateway_middleware() -> GatewayMiddleware:
    """Create gateway middleware instance"""
    return GatewayMiddleware


def create_cost_tracking_middleware() -> CostTrackingMiddleware:
    """Create cost tracking middleware instance"""
    return CostTrackingMiddleware


def get_streaming_middleware() -> StreamingMiddleware:
    """Get streaming middleware instance"""
    return StreamingMiddleware()