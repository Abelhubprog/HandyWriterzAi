"""
Advanced Security Middleware for HandyWriterz.
Production-ready security middleware with comprehensive protection layers,
threat detection, and advanced validation.
"""

import logging
import time
from typing import Dict, Any, Callable

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.services.security_service import security_service, SecurityConfig
from src.services.error_handler import error_handler, ErrorContext, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class RevolutionarySecurityMiddleware(BaseHTTPMiddleware):
    """Production-ready security middleware with multi-layer protection."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_service = security_service
        self.security_config = SecurityConfig()
        self.requests_processed = 0
        self.security_events = 0
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply comprehensive security checks to all requests."""
        start_time = time.time()
        self.requests_processed += 1
        
        try:
            # Skip security checks for health endpoints
            if request.url.path in ["/health", "/health/detailed", "/docs", "/redoc", "/openapi.json"]:
                response = await call_next(request)
                return self._add_security_headers(response)
            
            # 1. Basic request validation
            await self._validate_request_basics(request)
            
            # 2. Comprehensive security validation
            security_data = await self.security_service.validate_request_security(request)
            request.state.security_data = security_data
            
            # 3. Content-Length validation
            await self._validate_content_length(request)
            
            # 4. URL and path validation
            await self._validate_url_path(request)
            
            # 5. Headers validation
            await self._validate_headers(request)
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            response = self._add_security_headers(response)
            
            # Log successful security check
            duration = time.time() - start_time
            logger.debug(f"Security check passed for {request.method} {request.url.path} in {duration:.3f}s")
            
            return response
            
        except HTTPException:
            # Re-raise HTTP exceptions (already handled)
            raise
            
        except Exception as e:
            # Handle security-related errors
            self.security_events += 1
            
            context = ErrorContext(
                request_id=getattr(request.state, 'request_id', 'unknown'),
                additional_data={
                    "url": str(request.url),
                    "method": request.method,
                    "client_ip": self.security_service._get_client_ip(request),
                    "user_agent": request.headers.get("user-agent", ""),
                    "security_middleware": True
                }
            )
            
            await error_handler.handle_error(
                e, context, ErrorCategory.SYSTEM, ErrorSeverity.HIGH
            )
            
            # Log security event
            await self.security_service.log_security_event("middleware_error", {
                "error": str(e),
                "url": str(request.url),
                "method": request.method
            })
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Security validation error"
            )
    
    async def _validate_request_basics(self, request: Request):
        """Validate basic request properties."""
        # Check HTTP method
        allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]
        if request.method not in allowed_methods:
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail=f"Method {request.method} not allowed"
            )
        
        # Check protocol
        if request.url.scheme not in ["http", "https"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid protocol"
            )
    
    async def _validate_content_length(self, request: Request):
        """Validate content length to prevent large payload attacks."""
        content_length = request.headers.get("content-length")
        
        if content_length:
            try:
                length = int(content_length)
                max_size = 50 * 1024 * 1024  # 50MB max
                
                if length > max_size:
                    await self.security_service.log_security_event("large_payload", {
                        "content_length": length,
                        "max_allowed": max_size,
                        "client_ip": self.security_service._get_client_ip(request)
                    })
                    
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Request payload too large"
                    )
                    
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid content-length header"
                )
    
    async def _validate_url_path(self, request: Request):
        """Validate URL path for security issues."""
        path = request.url.path
        
        # Check for path traversal attempts
        if ".." in path or "\\" in path:
            await self.security_service.log_security_event("path_traversal", {
                "path": path,
                "client_ip": self.security_service._get_client_ip(request)
            })
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid path"
            )
        
        # Check for suspicious patterns in path
        suspicious_patterns = [
            "/.env", "/config", "/.git", "/admin", "/wp-admin",
            "/phpmyadmin", "/.well-known", "/robots.txt"
        ]
        
        for pattern in suspicious_patterns:
            if pattern in path.lower():
                await self.security_service.log_security_event("suspicious_path", {
                    "path": path,
                    "pattern": pattern,
                    "client_ip": self.security_service._get_client_ip(request)
                })
                break
        
        # Check path length
        if len(path) > 2048:
            raise HTTPException(
                status_code=status.HTTP_414_REQUEST_URI_TOO_LONG,
                detail="Request URI too long"
            )
    
    async def _validate_headers(self, request: Request):
        """Validate request headers for security issues."""
        # Check for required headers on certain endpoints
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            
            # Ensure proper content type for data endpoints
            if request.url.path.startswith("/api/") and not any([
                "application/json" in content_type,
                "multipart/form-data" in content_type,
                "application/x-www-form-urlencoded" in content_type
            ]):
                if request.url.path not in ["/api/upload"]:  # Upload endpoint allows different types
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail="Unsupported content type"
                    )
        
        # Check for malicious headers
        for header_name, header_value in request.headers.items():
            header_name_lower = header_name.lower()
            
            # Check header length
            if len(header_value) > 8192:  # 8KB max per header
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Header {header_name} too long"
                )
            
            # Check for null bytes
            if '\x00' in header_value:
                await self.security_service.log_security_event("null_byte_header", {
                    "header": header_name,
                    "client_ip": self.security_service._get_client_ip(request)
                })
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid header content"
                )
            
            # Check for suspicious user agents
            if header_name_lower == "user-agent":
                suspicious_agents = [
                    "sqlmap", "nikto", "nmap", "masscan", "zap",
                    "burp", "wget", "curl", "python-requests"
                ]
                
                if any(agent in header_value.lower() for agent in suspicious_agents):
                    await self.security_service.log_security_event("suspicious_user_agent", {
                        "user_agent": header_value,
                        "client_ip": self.security_service._get_client_ip(request)
                    })
    
    def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response."""
        for header_name, header_value in self.security_config.SECURITY_HEADERS.items():
            response.headers[header_name] = header_value
        
        # Add custom headers
        response.headers["X-Security-Middleware"] = "HandyWriterz-v2.0"
        response.headers["X-Requests-Processed"] = str(self.requests_processed)
        
        # Remove sensitive headers
        sensitive_headers = ["server", "x-powered-by", "x-aspnet-version"]
        for header in sensitive_headers:
            if header in response.headers:
                del response.headers[header]
        
        return response
    
    async def get_security_stats(self) -> Dict[str, Any]:
        """Get security middleware statistics."""
        return {
            "requests_processed": self.requests_processed,
            "security_events": self.security_events,
            "security_headers_applied": len(self.security_config.SECURITY_HEADERS),
            "middleware_version": "2.0.0"
        }


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware for state-changing operations."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.csrf_exempt_paths = {
            "/health", "/health/detailed", "/docs", "/redoc", "/openapi.json",
            "/api/webhook/dynamic", "/api/webhook/turnitin"  # Webhook endpoints
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply CSRF protection to state-changing requests."""
        # Skip CSRF check for safe methods and exempt paths
        if (request.method in ["GET", "HEAD", "OPTIONS"] or 
            request.url.path in self.csrf_exempt_paths):
            return await call_next(request)
        
        # Check for CSRF token in header
        csrf_token = request.headers.get("X-CSRF-Token")
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")
        
        # For API endpoints, require either:
        # 1. Valid CSRF token
        # 2. Valid origin/referer from allowed domains
        # 3. Valid JWT token (for API access)
        
        if request.url.path.startswith("/api/"):
            # Check for JWT token (API authentication)
            authorization = request.headers.get("authorization")
            
            if authorization and authorization.startswith("Bearer "):
                # API request with JWT - allow
                return await call_next(request)
            
            # Check origin/referer for web requests
            if origin or referer:
                allowed_origins = [
                    "http://localhost:3000",
                    "http://localhost:3001", 
                    "https://handywriterz.vercel.app",
                    "https://handywriterz.com"
                ]
                
                check_url = origin or referer
                if any(check_url.startswith(allowed) for allowed in allowed_origins):
                    return await call_next(request)
            
            # If no valid authentication method found
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF protection: Invalid or missing token"
            )
        
        return await call_next(request)


# Global middleware instances
security_middleware = RevolutionarySecurityMiddleware
csrf_middleware = CSRFProtectionMiddleware