"""
Revolutionary Error Handler Service for HandyWriterz.
Production-ready error handling with circuit breakers, retries, and fallbacks.
Enhanced with SSE integration, registry awareness, and comprehensive observability.
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import traceback
import hashlib
from functools import wraps
from contextlib import asynccontextmanager
import redis.asyncio as redis
import os

# Import enhanced components with graceful fallback
try:
    from .model_registry import get_model_registry, ModelSpec
    REGISTRY_AVAILABLE = True
except ImportError:
    REGISTRY_AVAILABLE = False

try:
    from ..agent.sse_unified import get_sse_publisher, EventType, Phase
    SSE_AVAILABLE = True
except ImportError:
    SSE_AVAILABLE = False

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for systematic handling."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    API_LIMIT = "api_limit"
    NETWORK = "network"
    DATABASE = "database"
    EXTERNAL_SERVICE = "external_service"
    AGENT_FAILURE = "agent_failure"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Comprehensive error context for analysis."""
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    node_name: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CircuitBreakerState:
    """Circuit breaker state management."""
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    failure_threshold: int = 5
    timeout: int = 60  # seconds
    success_threshold: int = 3  # for half-open state


class RevolutionaryErrorHandler:
    """Production-ready error handler with advanced resilience patterns."""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379"),
            decode_responses=True
        )
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.error_stats: Dict[str, Dict[str, Any]] = {}
        self.retry_configs: Dict[str, Dict[str, Any]] = self._init_retry_configs()
        self.fallback_handlers: Dict[str, Callable] = {}
        
        # Initialize monitoring
        self.error_count = 0
        self.critical_errors = 0
        self.start_time = datetime.utcnow()
        
        logger.info("Revolutionary Error Handler initialized with circuit breakers")
    
    def _init_retry_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize retry configurations for different error types."""
        return {
            "api_limit": {
                "max_retries": 3,
                "base_delay": 1.0,
                "max_delay": 60.0,
                "backoff_factor": 2.0,
                "jitter": True
            },
            "network": {
                "max_retries": 5,
                "base_delay": 0.5,
                "max_delay": 30.0,
                "backoff_factor": 1.5,
                "jitter": True
            },
            "database": {
                "max_retries": 3,
                "base_delay": 0.2,
                "max_delay": 10.0,
                "backoff_factor": 2.0,
                "jitter": False
            },
            "external_service": {
                "max_retries": 4,
                "base_delay": 1.0,
                "max_delay": 45.0,
                "backoff_factor": 1.8,
                "jitter": True
            },
            "agent_failure": {
                "max_retries": 2,
                "base_delay": 2.0,
                "max_delay": 120.0,
                "backoff_factor": 3.0,
                "jitter": True
            },
            "default": {
                "max_retries": 3,
                "base_delay": 1.0,
                "max_delay": 30.0,
                "backoff_factor": 2.0,
                "jitter": True
            }
        }
    
    async def handle_error(
        self,
        error: Exception,
        context: ErrorContext,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recoverable: bool = True
    ) -> Dict[str, Any]:
        """Handle errors with comprehensive analysis and recovery."""
        try:
            # Generate error ID
            error_id = f"err_{int(time.time() * 1000)}"
            
            # Classify error
            error_type = type(error).__name__
            error_message = str(error)
            
            # Enhanced error data
            error_data = {
                "error_id": error_id,
                "error_type": error_type,
                "error_message": error_message,
                "category": category.value,
                "severity": severity.value,
                "recoverable": recoverable,
                "context": {
                    "conversation_id": context.conversation_id,
                    "user_id": context.user_id,
                    "node_name": context.node_name,
                    "request_id": context.request_id,
                    "timestamp": context.timestamp.isoformat(),
                    "additional_data": context.additional_data
                },
                "stack_trace": traceback.format_exc(),
                "system_info": {
                    "handler_uptime": (datetime.utcnow() - self.start_time).total_seconds(),
                    "total_errors": self.error_count,
                    "critical_errors": self.critical_errors
                }
            }
            
            # Update statistics
            self._update_error_stats(error_type, category, severity)
            
            # Log error based on severity
            if severity == ErrorSeverity.CRITICAL:
                logger.critical(f"CRITICAL ERROR [{error_id}]: {error_message}", extra=error_data)
                self.critical_errors += 1
                await self._alert_critical_error(error_data)
            elif severity == ErrorSeverity.HIGH:
                logger.error(f"HIGH SEVERITY ERROR [{error_id}]: {error_message}", extra=error_data)
            elif severity == ErrorSeverity.MEDIUM:
                logger.warning(f"MEDIUM SEVERITY ERROR [{error_id}]: {error_message}", extra=error_data)
            else:
                logger.info(f"LOW SEVERITY ERROR [{error_id}]: {error_message}", extra=error_data)
            
            # Store error in Redis for monitoring
            await self._store_error_data(error_id, error_data)
            
            # Determine recovery strategy
            recovery_strategy = await self._determine_recovery_strategy(error, category, context)
            error_data["recovery_strategy"] = recovery_strategy
            
            # Broadcast error to monitoring systems
            await self._broadcast_error_event(error_data)
            
            return error_data
            
        except Exception as handler_error:
            logger.critical(f"Error handler itself failed: {handler_error}")
            return {
                "error_id": f"handler_fail_{int(time.time() * 1000)}",
                "error_type": "ErrorHandlerFailure",
                "error_message": str(handler_error),
                "original_error": str(error),
                "severity": "critical",
                "recoverable": False
            }
    
    async def with_circuit_breaker(
        self,
        operation_name: str,
        operation: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute operation with circuit breaker pattern."""
        breaker = self._get_circuit_breaker(operation_name)
        
        # Check circuit breaker state
        if breaker.state == "OPEN":
            if datetime.utcnow() - breaker.last_failure_time > timedelta(seconds=breaker.timeout):
                # Try to move to half-open state
                breaker.state = "HALF_OPEN"
                logger.info(f"Circuit breaker [{operation_name}] moving to HALF_OPEN state")
            else:
                # Circuit is still open
                raise Exception(f"Circuit breaker [{operation_name}] is OPEN - operation blocked")
        
        try:
            # Execute operation
            result = await operation(*args, **kwargs)
            
            # Success - reset failure count
            if breaker.state == "HALF_OPEN":
                breaker.success_threshold -= 1
                if breaker.success_threshold <= 0:
                    breaker.state = "CLOSED"
                    breaker.failure_count = 0
                    logger.info(f"Circuit breaker [{operation_name}] returned to CLOSED state")
            elif breaker.state == "CLOSED":
                breaker.failure_count = 0
            
            return result
            
        except Exception:
            # Operation failed
            breaker.failure_count += 1
            breaker.last_failure_time = datetime.utcnow()
            
            if breaker.failure_count >= breaker.failure_threshold:
                breaker.state = "OPEN"
                logger.warning(f"Circuit breaker [{operation_name}] opened due to {breaker.failure_count} failures")
            elif breaker.state == "HALF_OPEN":
                breaker.state = "OPEN"
                logger.warning(f"Circuit breaker [{operation_name}] returned to OPEN state")
            
            raise
    
    async def with_retry(
        self,
        operation: Callable,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[ErrorContext] = None,
        *args,
        **kwargs
    ) -> Any:
        """Execute operation with intelligent retry logic."""
        config = self.retry_configs.get(error_category.value, self.retry_configs["default"])
        
        last_exception = None
        for attempt in range(config["max_retries"] + 1):
            try:
                return await operation(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                
                if attempt == config["max_retries"]:
                    # Final attempt failed
                    if context:
                        await self.handle_error(e, context, error_category, ErrorSeverity.HIGH)
                    raise
                
                # Calculate delay for next attempt
                delay = min(
                    config["base_delay"] * (config["backoff_factor"] ** attempt),
                    config["max_delay"]
                )
                
                # Add jitter if configured
                if config.get("jitter", False):
                    import random
                    delay *= (0.5 + random.random() * 0.5)
                
                logger.warning(f"Retry attempt {attempt + 1}/{config['max_retries']} after {delay:.2f}s delay: {e}")
                await asyncio.sleep(delay)
        
        # Should not reach here, but just in case
        raise last_exception
    
    async def with_fallback(
        self,
        primary_operation: Callable,
        fallback_operation: Callable,
        operation_name: str,
        context: Optional[ErrorContext] = None,
        *args,
        **kwargs
    ) -> Any:
        """Execute operation with fallback mechanism."""
        try:
            return await primary_operation(*args, **kwargs)
            
        except Exception as e:
            logger.warning(f"Primary operation [{operation_name}] failed, using fallback: {e}")
            
            if context:
                await self.handle_error(e, context, ErrorCategory.SYSTEM, ErrorSeverity.MEDIUM)
            
            try:
                result = await fallback_operation(*args, **kwargs)
                logger.info(f"Fallback operation [{operation_name}] succeeded")
                return result
                
            except Exception as fallback_error:
                logger.error(f"Fallback operation [{operation_name}] also failed: {fallback_error}")
                
                if context:
                    await self.handle_error(fallback_error, context, ErrorCategory.SYSTEM, ErrorSeverity.HIGH)
                
                raise
    
    def _get_circuit_breaker(self, operation_name: str) -> CircuitBreakerState:
        """Get or create circuit breaker for operation."""
        if operation_name not in self.circuit_breakers:
            self.circuit_breakers[operation_name] = CircuitBreakerState()
        return self.circuit_breakers[operation_name]
    
    def _update_error_stats(self, error_type: str, category: ErrorCategory, severity: ErrorSeverity):
        """Update error statistics for monitoring."""
        self.error_count += 1
        
        if error_type not in self.error_stats:
            self.error_stats[error_type] = {
                "count": 0,
                "categories": {},
                "severities": {},
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat()
            }
        
        stats = self.error_stats[error_type]
        stats["count"] += 1
        stats["last_seen"] = datetime.utcnow().isoformat()
        
        # Update category stats
        if category.value not in stats["categories"]:
            stats["categories"][category.value] = 0
        stats["categories"][category.value] += 1
        
        # Update severity stats
        if severity.value not in stats["severities"]:
            stats["severities"][severity.value] = 0
        stats["severities"][severity.value] += 1
    
    async def _store_error_data(self, error_id: str, error_data: Dict[str, Any]):
        """Store error data in Redis for monitoring."""
        try:
            # Store individual error
            await self.redis_client.setex(
                f"error:{error_id}",
                3600,  # 1 hour TTL
                json.dumps(error_data, default=str)
            )
            
            # Add to error list
            await self.redis_client.lpush("errors:recent", error_id)
            await self.redis_client.ltrim("errors:recent", 0, 999)  # Keep last 1000
            
        except Exception as e:
            logger.error(f"Failed to store error data: {e}")
    
    async def _broadcast_error_event(self, error_data: Dict[str, Any]):
        """Broadcast error event for real-time monitoring."""
        try:
            await self.redis_client.publish(
                "error_events",
                json.dumps(error_data, default=str)
            )
        except Exception as e:
            logger.error(f"Failed to broadcast error event: {e}")
    
    async def _alert_critical_error(self, error_data: Dict[str, Any]):
        """Alert for critical errors (integration point for external alerting)."""
        try:
            # Store critical error
            await self.redis_client.setex(
                f"critical_error:{error_data['error_id']}",
                86400,  # 24 hours TTL
                json.dumps(error_data, default=str)
            )
            
            # Broadcast critical alert
            await self.redis_client.publish(
                "critical_alerts",
                json.dumps(error_data, default=str)
            )
            
            logger.critical(f"CRITICAL ERROR ALERT: {error_data['error_id']}")
            
        except Exception as e:
            logger.error(f"Failed to alert critical error: {e}")
    
    async def _determine_recovery_strategy(
        self,
        error: Exception,
        category: ErrorCategory,
        context: ErrorContext
    ) -> Dict[str, Any]:
        """Determine appropriate recovery strategy based on error analysis."""
        strategy = {
            "recommended_action": "unknown",
            "retry_recommended": False,
            "fallback_available": False,
            "user_action_required": False,
            "estimated_recovery_time": "unknown"
        }
        
        # Category-specific strategies
        if category == ErrorCategory.API_LIMIT:
            strategy.update({
                "recommended_action": "rate_limit_backoff",
                "retry_recommended": True,
                "estimated_recovery_time": "1-5 minutes"
            })
        elif category == ErrorCategory.NETWORK:
            strategy.update({
                "recommended_action": "network_retry",
                "retry_recommended": True,
                "estimated_recovery_time": "30 seconds - 2 minutes"
            })
        elif category == ErrorCategory.DATABASE:
            strategy.update({
                "recommended_action": "database_reconnect",
                "retry_recommended": True,
                "estimated_recovery_time": "10-30 seconds"
            })
        elif category == ErrorCategory.EXTERNAL_SERVICE:
            strategy.update({
                "recommended_action": "service_fallback",
                "retry_recommended": True,
                "fallback_available": True,
                "estimated_recovery_time": "1-10 minutes"
            })
        elif category == ErrorCategory.VALIDATION:
            strategy.update({
                "recommended_action": "user_input_correction",
                "retry_recommended": False,
                "user_action_required": True,
                "estimated_recovery_time": "immediate"
            })
        elif category == ErrorCategory.AUTHENTICATION:
            strategy.update({
                "recommended_action": "reauthentication",
                "retry_recommended": False,
                "user_action_required": True,
                "estimated_recovery_time": "immediate"
            })
        elif category == ErrorCategory.AGENT_FAILURE:
            strategy.update({
                "recommended_action": "agent_restart",
                "retry_recommended": True,
                "fallback_available": True,
                "estimated_recovery_time": "2-5 minutes"
            })
        
        return strategy
    
    async def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        return {
            "total_errors": self.error_count,
            "critical_errors": self.critical_errors,
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "error_breakdown": self.error_stats,
            "circuit_breaker_states": {
                name: {
                    "state": breaker.state,
                    "failure_count": breaker.failure_count,
                    "last_failure": breaker.last_failure_time.isoformat() if breaker.last_failure_time else None
                }
                for name, breaker in self.circuit_breakers.items()
            }
        }
    
    async def reset_circuit_breaker(self, operation_name: str):
        """Reset circuit breaker for testing/recovery."""
        if operation_name in self.circuit_breakers:
            breaker = self.circuit_breakers[operation_name]
            breaker.state = "CLOSED"
            breaker.failure_count = 0
            breaker.last_failure_time = None
            logger.info(f"Circuit breaker [{operation_name}] reset to CLOSED state")


# Decorators for easy integration
def with_error_handling(
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    recoverable: bool = True
):
    """Decorator for automatic error handling."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    node_name=func.__name__,
                    additional_data={"args": str(args), "kwargs": str(kwargs)}
                )
                
                error_data = await error_handler.handle_error(e, context, category, severity, recoverable)
                
                if not recoverable:
                    raise
                
                return {"error": True, "error_data": error_data}
        return wrapper
    return decorator


def with_circuit_breaker(operation_name: str):
    """Decorator for circuit breaker pattern."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await error_handler.with_circuit_breaker(
                operation_name, func, *args, **kwargs
            )
        return wrapper
    return decorator


def with_retry(category: ErrorCategory = ErrorCategory.UNKNOWN):
    """Decorator for retry pattern."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            context = ErrorContext(node_name=func.__name__)
            return await error_handler.with_retry(
                func, category, context, *args, **kwargs
            )
        return wrapper
    return decorator


# Global error handler instance
error_handler = RevolutionaryErrorHandler()


# Dependency injection for FastAPI
def get_error_handler() -> RevolutionaryErrorHandler:
    """Get error handler instance."""
    return error_handler