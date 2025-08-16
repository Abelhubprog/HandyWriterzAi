"""
Revolutionary Security Service for HandyWriterz.
Production-ready authentication, authorization, input validation, and rate limiting.
"""

import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Dict, Any, List, Set
from functools import wraps
from dataclasses import dataclass

import jwt
import redis.asyncio as redis
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cryptography.fernet import Fernet


logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int = 10


class SecurityConfig:
    """Security configuration constants."""
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    
    # Rate limiting
    RATE_LIMITS = {
        "free": RateLimitConfig(5, 50, 200, 10),
        "premium": RateLimitConfig(20, 500, 2000, 50),
        "admin": RateLimitConfig(100, 5000, 20000, 200)
    }
    
    # Input validation
    MAX_PROMPT_LENGTH = 10000
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES = {".pdf", ".docx", ".txt", ".md"}
    
    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }


class InputValidationError(Exception):
    """Custom exception for input validation errors."""
    pass


class RevolutionarySecurityService:
    """Production-ready security service with comprehensive protection."""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379"),
            decode_responses=True
        )
        self.security_config = SecurityConfig()
        self.blocked_ips: Set[str] = set()
        self.suspicious_patterns = self._init_suspicious_patterns()
        
        # Initialize encryption
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if not encryption_key:
            encryption_key = Fernet.generate_key()
            env = (os.getenv("ENV") or os.getenv("APP_ENV") or os.getenv("PYTHON_ENV") or "development").lower()
            # Lower severity in local/dev to reduce noise
            msg = "No ENCRYPTION_KEY found; generated ephemeral key for this process"
            if env in ("prod", "production"):
                logger.warning(msg)
            else:
                logger.info(msg)
        
        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        
        logger.info("Revolutionary Security Service initialized")
    
    def _init_suspicious_patterns(self) -> List[re.Pattern]:
        """Initialize patterns for detecting suspicious input."""
        patterns = [
            # SQL Injection
            re.compile(r"(union|select|insert|update|delete|drop|create|alter)\s+", re.IGNORECASE),
            re.compile(r"['\"];?\s*(or|and)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+", re.IGNORECASE),
            
            # XSS
            re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
            re.compile(r"javascript:", re.IGNORECASE),
            re.compile(r"on\w+\s*=", re.IGNORECASE),
            
            # Command Injection
            re.compile(r"[;&|`$]", re.IGNORECASE),
            re.compile(r"(rm|cat|ls|ps|kill|wget|curl)\s+", re.IGNORECASE),
            
            # Path Traversal
            re.compile(r"\.\./"),
            re.compile(r"\\.\\.\\"),
            
            # LDAP Injection
            re.compile(r"[()&|]"),
            
            # NoSQL Injection
            re.compile(r"\$\w+:"),
        ]
        return patterns
    
    async def validate_request_security(self, request: Request) -> Dict[str, Any]:
        """Comprehensive request security validation."""
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        security_data = {
            "client_ip": client_ip,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow().isoformat(),
            "security_checks": {}
        }
        
        # Check blocked IPs
        if client_ip in self.blocked_ips:
            security_data["security_checks"]["ip_blocked"] = True
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied from this IP address"
            )
        
        # Check for suspicious patterns in headers
        for header_name, header_value in request.headers.items():
            if self._contains_suspicious_patterns(header_value):
                security_data["security_checks"]["suspicious_headers"] = True
                await self._log_security_event("suspicious_headers", {
                    "ip": client_ip,
                    "header": header_name,
                    "value": header_value[:100]
                })
        
        # Rate limiting check
        rate_limit_result = await self._check_rate_limits(client_ip, "general")
        security_data["security_checks"]["rate_limit"] = rate_limit_result
        
        if not rate_limit_result["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(rate_limit_result["retry_after"])}
            )
        
        return security_data
    
    async def validate_input_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive input data validation."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "sanitized_data": {}
        }
        
        for key, value in data.items():
            try:
                if isinstance(value, str):
                    # Length validation
                    if key == "prompt" and len(value) > self.security_config.MAX_PROMPT_LENGTH:
                        validation_result["errors"].append(
                            f"Prompt too long: {len(value)} > {self.security_config.MAX_PROMPT_LENGTH}"
                        )
                        validation_result["valid"] = False
                        continue
                    
                    # Suspicious pattern detection
                    if self._contains_suspicious_patterns(value):
                        validation_result["errors"].append(f"Suspicious content detected in {key}")
                        validation_result["valid"] = False
                        await self._log_security_event("suspicious_input", {
                            "field": key,
                            "content_preview": value[:100]
                        })
                        continue
                    
                    # Sanitize and store
                    validation_result["sanitized_data"][key] = self._sanitize_string(value)
                
                elif isinstance(value, (dict, list)):
                    # Recursive validation for nested structures
                    if isinstance(value, dict):
                        nested_result = await self.validate_input_data(value)
                        if not nested_result["valid"]:
                            validation_result["errors"].extend(nested_result["errors"])
                            validation_result["valid"] = False
                        else:
                            validation_result["sanitized_data"][key] = nested_result["sanitized_data"]
                    else:
                        validation_result["sanitized_data"][key] = value
                
                else:
                    validation_result["sanitized_data"][key] = value
                    
            except Exception as e:
                validation_result["errors"].append(f"Validation error for {key}: {str(e)}")
                validation_result["valid"] = False
        
        return validation_result
    
    async def validate_jwt_token(self, credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
        """Validate JWT token and extract user information."""
        try:
            # Decode JWT token
            payload = jwt.decode(
                credentials.credentials,
                self.security_config.JWT_SECRET_KEY,
                algorithms=[self.security_config.JWT_ALGORITHM]
            )
            
            # Check expiration
            if payload.get("exp", 0) < time.time():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )
            
            # Extract user data
            user_data = {
                "user_id": payload.get("user_id"),
                "wallet_address": payload.get("wallet_address"),
                "user_type": payload.get("user_type", "student"),
                "subscription_tier": payload.get("subscription_tier", "free"),
                "exp": payload.get("exp"),
                "iat": payload.get("iat")
            }
            
            return user_data
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def generate_jwt_token(self, user_data: Dict[str, Any]) -> str:
        """Generate JWT token for authenticated user."""
        payload = {
            "user_id": str(user_data.get("id")),
            "wallet_address": user_data.get("wallet_address"),
            "user_type": user_data.get("user_type", "student"),
            "subscription_tier": user_data.get("subscription_tier", "free"),
            "iat": int(time.time()),
            "exp": int(time.time() + (self.security_config.JWT_EXPIRATION_HOURS * 3600))
        }
        
        token = jwt.encode(
            payload,
            self.security_config.JWT_SECRET_KEY,
            algorithm=self.security_config.JWT_ALGORITHM
        )
        
        return token
    
    async def check_user_authorization(self, user_data: Dict[str, Any], required_action: str) -> bool:
        """Check if user is authorized for specific action."""
        user_type = user_data.get("user_type", "student")
        subscription_tier = user_data.get("subscription_tier", "free")
        
        # Define permissions
        permissions = {
            "create_document": ["student", "premium", "admin"],
            "upload_file": ["student", "premium", "admin"],
            "access_premium_features": ["premium", "admin"],
            "admin_access": ["admin"],
            "bulk_operations": ["premium", "admin"]
        }
        
        allowed_types = permissions.get(required_action, [])
        
        if user_type not in allowed_types:
            return False
        
        # Additional subscription checks
        if required_action == "access_premium_features" and subscription_tier == "free":
            return False
        
        return True
    
    async def apply_rate_limiting(self, client_ip: str, action: str, user_tier: str = "free") -> bool:
        """Apply rate limiting based on user tier and action."""
        rate_limit_result = await self._check_rate_limits(client_ip, action, user_tier)
        
        if not rate_limit_result["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for {action}",
                headers={"Retry-After": str(rate_limit_result["retry_after"])}
            )
        
        return True
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    async def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events for monitoring."""
        await self._log_security_event(event_type, details)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _contains_suspicious_patterns(self, text: str) -> bool:
        """Check if text contains suspicious patterns."""
        for pattern in self.suspicious_patterns:
            if pattern.search(text):
                return True
        return False
    
    def _sanitize_string(self, text: str) -> str:
        """Sanitize string input."""
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove potential XSS
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        return text
    
    async def _check_rate_limits(self, client_ip: str, action: str, user_tier: str = "free") -> Dict[str, Any]:
        """Check rate limits for client."""
        rate_config = self.security_config.RATE_LIMITS.get(user_tier, self.security_config.RATE_LIMITS["free"])
        
        current_time = int(time.time())
        minute_key = f"rate_limit:{client_ip}:{action}:minute:{current_time // 60}"
        hour_key = f"rate_limit:{client_ip}:{action}:hour:{current_time // 3600}"
        day_key = f"rate_limit:{client_ip}:{action}:day:{current_time // 86400}"
        
        try:
            # Check limits
            minute_count = await self.redis_client.get(minute_key) or 0
            hour_count = await self.redis_client.get(hour_key) or 0
            day_count = await self.redis_client.get(day_key) or 0
            
            minute_count = int(minute_count)
            hour_count = int(hour_count)
            day_count = int(day_count)
            
            # Check against limits
            if minute_count >= rate_config.requests_per_minute:
                return {"allowed": False, "retry_after": 60, "limit_type": "minute"}
            
            if hour_count >= rate_config.requests_per_hour:
                return {"allowed": False, "retry_after": 3600, "limit_type": "hour"}
            
            if day_count >= rate_config.requests_per_day:
                return {"allowed": False, "retry_after": 86400, "limit_type": "day"}
            
            # Increment counters
            pipe = self.redis_client.pipeline()
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)
            pipe.incr(day_key)
            pipe.expire(day_key, 86400)
            await pipe.execute()
            
            return {
                "allowed": True,
                "remaining": {
                    "minute": rate_config.requests_per_minute - minute_count - 1,
                    "hour": rate_config.requests_per_hour - hour_count - 1,
                    "day": rate_config.requests_per_day - day_count - 1
                }
            }
            
        except Exception as e:
            logger.error(f"Rate limiting check failed: {e}")
            # Fail open for availability
            return {"allowed": True, "remaining": {"minute": 0, "hour": 0, "day": 0}}
    
    async def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security events."""
        try:
            event_data = {
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details,
                "severity": "medium"
            }
            
            # Store in Redis
            await self.redis_client.lpush(
                "security_events",
                json.dumps(event_data)
            )
            await self.redis_client.ltrim("security_events", 0, 9999)  # Keep last 10k events
            
            # Log to application logs
            logger.warning(f"Security event [{event_type}]: {details}")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")


# Authentication dependency
security_scheme = HTTPBearer()
optional_security_scheme = HTTPBearer(auto_error=False)
security_service = RevolutionarySecurityService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> Dict[str, Any]:
    """Get current authenticated user."""
    return await security_service.validate_jwt_token(credentials)


async def get_optional_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_security_scheme),
) -> Dict[str, Any]:
    """Get current user if Authorization is provided; otherwise return anonymous.

    Also accepts an optional 'X-User-Id' header for lightweight identification in dev.
    """
    try:
        if credentials is not None:
            return await security_service.validate_jwt_token(credentials)
    except HTTPException:
        # Invalid token → treat as anonymous rather than failing hard for optional paths
        pass

    # Fallback: accept X-User-Id header for non-auth flows
    try:
        x_uid = request.headers.get('x-user-id') or request.headers.get('X-User-Id')
        if x_uid:
            return {"user_id": x_uid}
    except Exception:
        pass

    return {"user_id": "anonymous"}


from typing import Union, List

def require_authorization(action: Union[str, List[str]]):
    """Dependency for requiring specific authorization.

    Accepts a single action string or a list of actions (any-of semantics).
    Usage:
      current_user: Dict[str, Any] = Depends(require_authorization("admin"))
      current_user: Dict[str, Any] = Depends(require_authorization(["checker", "admin"]))
    """
    async def check_auth(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        try:
            if isinstance(action, list):
                allowed = False
                for a in action:
                    if await security_service.check_user_authorization(user, a):
                        allowed = True
                        break
                if not allowed:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions; requires one of: {', '.join(map(str, action))}"
                    )
            else:
                if not await security_service.check_user_authorization(user, action):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions for {action}"
                    )
            return user
        except HTTPException:
            raise
        except Exception as e:
            # Fail closed on unexpected errors
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Authorization error: {e}")
    return check_auth


# Security decorators
def require_rate_limit(action: str):
    """Decorator for rate limiting."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request:
                client_ip = security_service._get_client_ip(request)
                await security_service.apply_rate_limiting(client_ip, action)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def validate_input():
    """Decorator for input validation."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request data in kwargs
            for key, value in kwargs.items():
                if hasattr(value, 'dict') and callable(getattr(value, 'dict')):
                    # Pydantic model
                    data = value.dict()
                    validation_result = await security_service.validate_input_data(data)
                    
                    if not validation_result["valid"]:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Input validation failed: {validation_result['errors']}"
                        )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Global security service instance
def get_security_service() -> RevolutionarySecurityService:
    """Get security service instance."""
    return security_service
