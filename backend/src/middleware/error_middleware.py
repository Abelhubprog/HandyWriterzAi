"""
Revolutionary Error Middleware for HandyWriterz.
Production-ready error handling middleware with comprehensive error management.
"""

import logging
import time
import uuid
from typing import Dict, Any, Callable
from datetime import datetime

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.services.error_handler import (
    error_handler, ErrorContext, ErrorCategory, ErrorSeverity
)

logger = logging.getLogger(__name__)


class RevolutionaryErrorMiddleware(BaseHTTPMiddleware):
    """Production-ready error middleware with comprehensive error handling."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.error_handler = error_handler
        self.request_counter = 0
        self.error_counter = 0
        self.start_time = datetime.utcnow()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle request with comprehensive error management."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Request metrics
        start_time = time.time()
        self.request_counter += 1
        
        # Create error context
        context = ErrorContext(
            request_id=request_id,
            additional_data={
                "method": request.method,
                "url": str(request.url),
                "user_agent": request.headers.get("user-agent", ""),
                "client_ip": request.client.host if request.client else "",
                "request_counter": self.request_counter
            }
        )
        
        try:
            # Execute request
            response = await call_next(request)
            
            # Log successful request
            duration = time.time() - start_time
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"[{response.status_code}] in {duration:.3f}s [ID: {request_id}]"
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            
            return response
            
        except Exception as e:
            # Handle all exceptions
            self.error_counter += 1
            duration = time.time() - start_time
            
            # Classify error
            error_category, error_severity = self._classify_error(e)
            
            # Update context with error information
            context.additional_data.update({
                "error_type": type(e).__name__,
                "duration": duration,
                "error_counter": self.error_counter
            })
            
            # Handle error through error handler
            error_data = await self.error_handler.handle_error(
                e, context, error_category, error_severity
            )
            
            # Generate appropriate response
            response = await self._generate_error_response(e, error_data, request_id)
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            response.headers["X-Error-ID"] = error_data.get("error_id", "unknown")
            
            return response
    
    def _classify_error(self, error: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """Classify error by category and severity."""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Classification logic
        if isinstance(error, RequestValidationError):
            return ErrorCategory.VALIDATION, ErrorSeverity.LOW
        
        elif isinstance(error, HTTPException):
            if error.status_code == 401:
                return ErrorCategory.AUTHENTICATION, ErrorSeverity.MEDIUM
            elif error.status_code == 403:
                return ErrorCategory.AUTHORIZATION, ErrorSeverity.MEDIUM
            elif error.status_code == 429:
                return ErrorCategory.API_LIMIT, ErrorSeverity.MEDIUM
            elif 400 <= error.status_code < 500:
                return ErrorCategory.VALIDATION, ErrorSeverity.LOW
            else:
                return ErrorCategory.SYSTEM, ErrorSeverity.HIGH
        
        elif "connection" in error_message or "timeout" in error_message:
            return ErrorCategory.NETWORK, ErrorSeverity.MEDIUM
        
        elif "database" in error_message or "sql" in error_message:
            return ErrorCategory.DATABASE, ErrorSeverity.HIGH
        
        elif "openai" in error_message or "anthropic" in error_message or "api" in error_message:
            return ErrorCategory.EXTERNAL_SERVICE, ErrorSeverity.MEDIUM
        
        elif "agent" in error_message or "workflow" in error_message:
            return ErrorCategory.AGENT_FAILURE, ErrorSeverity.HIGH
        
        elif "redis" in error_message:
            return ErrorCategory.SYSTEM, ErrorSeverity.MEDIUM
        
        elif error_type in ["KeyError", "AttributeError", "IndexError", "TypeError"]:
            return ErrorCategory.SYSTEM, ErrorSeverity.HIGH
        
        elif error_type in ["ValueError", "AssertionError"]:
            return ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM
        
        elif error_type in ["MemoryError", "ResourceWarning"]:
            return ErrorCategory.SYSTEM, ErrorSeverity.CRITICAL
        
        else:
            return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM
    
    async def _generate_error_response(
        self,
        error: Exception,
        error_data: Dict[str, Any],
        request_id: str
    ) -> JSONResponse:
        """Generate appropriate error response."""
        error_type = type(error).__name__
        
        # Base error response
        response_data = {
            "error": True,
            "error_type": error_type,
            "message": "An error occurred while processing your request",
            "request_id": request_id,
            "error_id": error_data.get("error_id"),
            "timestamp": datetime.utcnow().isoformat(),
            "support_message": "Please contact support if this error persists"
        }
        
        # Determine status code and user message
        if isinstance(error, HTTPException):
            status_code = error.status_code
            response_data["message"] = error.detail
            
        elif isinstance(error, RequestValidationError):
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            response_data["message"] = "Invalid request data"
            response_data["validation_errors"] = [
                {
                    "field": ".".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"]
                }
                for err in error.errors()
            ]
            
        elif error_data.get("category") == "validation":
            status_code = status.HTTP_400_BAD_REQUEST
            response_data["message"] = "Invalid input data"
            
        elif error_data.get("category") == "authentication":
            status_code = status.HTTP_401_UNAUTHORIZED
            response_data["message"] = "Authentication required"
            
        elif error_data.get("category") == "authorization":
            status_code = status.HTTP_403_FORBIDDEN
            response_data["message"] = "Access denied"
            
        elif error_data.get("category") == "api_limit":
            status_code = status.HTTP_429_TOO_MANY_REQUESTS
            response_data["message"] = "Rate limit exceeded. Please try again later."
            response_data["retry_after"] = 60
            
        elif error_data.get("category") == "network":
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            response_data["message"] = "Service temporarily unavailable due to network issues"
            
        elif error_data.get("category") == "database":
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            response_data["message"] = "Database service temporarily unavailable"
            
        elif error_data.get("category") == "external_service":
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            response_data["message"] = "External service temporarily unavailable"
            
        elif error_data.get("category") == "agent_failure":
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            response_data["message"] = "AI agent temporarily unavailable. Please try again."
            
        elif error_data.get("severity") == "critical":
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response_data["message"] = "Critical system error. Support has been notified."
            
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            response_data["message"] = "Internal server error"
        
        # Add recovery information for recoverable errors
        if error_data.get("recovery_strategy"):
            recovery = error_data["recovery_strategy"]
            if recovery.get("retry_recommended"):
                response_data["retry_recommended"] = True
                response_data["estimated_recovery_time"] = recovery.get("estimated_recovery_time")
            
            if recovery.get("user_action_required"):
                response_data["user_action_required"] = True
                response_data["recommended_action"] = recovery.get("recommended_action")
        
        # Add additional context for development
        if logger.isEnabledFor(logging.DEBUG):
            response_data["debug_info"] = {
                "error_category": error_data.get("category"),
                "error_severity": error_data.get("severity"),
                "stack_trace": error_data.get("stack_trace"),
                "context": error_data.get("context")
            }
        
        return JSONResponse(
            content=response_data,
            status_code=status_code
        )
    
    async def get_middleware_stats(self) -> Dict[str, Any]:
        """Get middleware statistics."""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self.request_counter,
            "total_errors": self.error_counter,
            "error_rate": self.error_counter / max(self.request_counter, 1),
            "requests_per_second": self.request_counter / max(uptime, 1),
            "errors_per_second": self.error_counter / max(uptime, 1)
        }


class GlobalExceptionHandler:
    """Global exception handler for specific exception types."""
    
    def __init__(self):
        self.error_handler = error_handler
    
    async def handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions."""
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        
        context = ErrorContext(
            request_id=request_id,
            additional_data={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "url": str(request.url),
                "method": request.method
            }
        )
        
        category = ErrorCategory.SYSTEM
        severity = ErrorSeverity.MEDIUM
        
        if exc.status_code == 401:
            category = ErrorCategory.AUTHENTICATION
        elif exc.status_code == 403:
            category = ErrorCategory.AUTHORIZATION
        elif exc.status_code == 429:
            category = ErrorCategory.API_LIMIT
        elif 400 <= exc.status_code < 500:
            category = ErrorCategory.VALIDATION
            severity = ErrorSeverity.LOW
        elif exc.status_code >= 500:
            severity = ErrorSeverity.HIGH
        
        error_data = await self.error_handler.handle_error(
            exc, context, category, severity
        )
        
        return JSONResponse(
            content={
                "error": True,
                "error_type": "HTTPException",
                "message": exc.detail,
                "status_code": exc.status_code,
                "request_id": request_id,
                "error_id": error_data.get("error_id"),
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=exc.status_code
        )
    
    async def handle_validation_exception(self, request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle validation exceptions."""
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        
        context = ErrorContext(
            request_id=request_id,
            additional_data={
                "validation_errors": exc.errors(),
                "url": str(request.url),
                "method": request.method
            }
        )
        
        error_data = await self.error_handler.handle_error(
            exc, context, ErrorCategory.VALIDATION, ErrorSeverity.LOW
        )
        
        return JSONResponse(
            content={
                "error": True,
                "error_type": "ValidationError",
                "message": "Invalid request data",
                "validation_errors": [
                    {
                        "field": ".".join(str(loc) for loc in err["loc"]),
                        "message": err["msg"],
                        "type": err["type"]
                    }
                    for err in exc.errors()
                ],
                "request_id": request_id,
                "error_id": error_data.get("error_id"),
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


# Global instances
error_middleware = RevolutionaryErrorMiddleware
global_exception_handler = GlobalExceptionHandler()