"""
Production Error Handling for Agent Nodes
Provides robust error handling with retry logic, circuit breakers, and structured error reporting.
"""

import logging
import time
import asyncio
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union, Type
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ErrorSeverity(str, Enum):
    """Error severity levels for agent node failures."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(str, Enum):
    """Error categories for structured error reporting."""
    NETWORK = "network"
    API_LIMIT = "api_limit"
    VALIDATION = "validation"
    PROCESSING = "processing"
    EXTERNAL_SERVICE = "external_service"
    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"

@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_backoff: bool = True
    retry_on_exceptions: tuple = (Exception,)
    circuit_breaker_threshold: int = 5

class NodeError(BaseModel):
    """Structured error information for agent nodes."""
    error_code: str = Field(..., description="Error code for categorization")
    error_message: str = Field(..., description="Human-readable error message")
    severity: ErrorSeverity = Field(..., description="Error severity level")
    category: ErrorCategory = Field(..., description="Error category")
    node_name: str = Field(..., description="Name of the node that failed")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    recoverable: bool = Field(default=True, description="Whether error is recoverable")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional error context")
    timestamp: float = Field(default_factory=time.time, description="Error timestamp")

class CircuitBreaker:
    """Circuit breaker for agent nodes to prevent cascading failures."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info(f"Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception(f"Circuit breaker OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                logger.info(f"Circuit breaker CLOSED - service recovered")
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(f"Circuit breaker OPEN - failure threshold exceeded")
            
            raise e

# Global circuit breakers for different node types
_circuit_breakers: Dict[str, CircuitBreaker] = {}

def get_circuit_breaker(node_name: str) -> CircuitBreaker:
    """Get or create circuit breaker for node."""
    if node_name not in _circuit_breakers:
        _circuit_breakers[node_name] = CircuitBreaker()
    return _circuit_breakers[node_name]

def with_error_handling(
    node_name: str,
    retry_config: Optional[RetryConfig] = None,
    error_category: ErrorCategory = ErrorCategory.PROCESSING,
    use_circuit_breaker: bool = True
):
    """
    Decorator for production-grade error handling in agent nodes.
    
    Args:
        node_name: Name of the agent node
        retry_config: Retry configuration
        error_category: Default error category
        use_circuit_breaker: Whether to use circuit breaker
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(state: Any, config: Any = None, *args, **kwargs):
            return await _execute_with_error_handling(
                func, state, config, node_name, retry_config, 
                error_category, use_circuit_breaker, *args, **kwargs
            )
        
        @wraps(func)
        def sync_wrapper(state: Any, config: Any = None, *args, **kwargs):
            return asyncio.run(_execute_with_error_handling(
                func, state, config, node_name, retry_config,
                error_category, use_circuit_breaker, *args, **kwargs
            ))
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

async def _execute_with_error_handling(
    func: Callable,
    state: Any,
    config: Any,
    node_name: str,
    retry_config: Optional[RetryConfig],
    error_category: ErrorCategory,
    use_circuit_breaker: bool,
    *args,
    **kwargs
) -> Any:
    """Execute function with comprehensive error handling."""
    
    if retry_config is None:
        retry_config = RetryConfig()
    
    circuit_breaker = get_circuit_breaker(node_name) if use_circuit_breaker else None
    last_error = None
    
    for attempt in range(retry_config.max_attempts):
        try:
            # Execute with circuit breaker if enabled
            if circuit_breaker:
                if asyncio.iscoroutinefunction(func):
                    result = await circuit_breaker.call(func, state, config, *args, **kwargs)
                else:
                    result = circuit_breaker.call(func, state, config, *args, **kwargs)
            else:
                if asyncio.iscoroutinefunction(func):
                    result = await func(state, config, *args, **kwargs)
                else:
                    result = func(state, config, *args, **kwargs)
            
            # Success - log recovery if this was a retry
            if attempt > 0:
                logger.info(f"Node {node_name} recovered after {attempt} retries")
            
            return result
            
        except Exception as e:
            last_error = e
            
            # Determine if we should retry
            should_retry = (
                attempt < retry_config.max_attempts - 1 and
                any(isinstance(e, exc_type) for exc_type in retry_config.retry_on_exceptions)
            )
            
            # Create structured error
            node_error = _create_node_error(
                e, node_name, error_category, attempt, should_retry
            )
            
            # Log error with appropriate level
            _log_node_error(node_error, should_retry)
            
            # Add error to state if possible
            _add_error_to_state(state, node_error)
            
            if not should_retry:
                break
            
            # Calculate retry delay
            delay = _calculate_retry_delay(retry_config, attempt)
            if delay > 0:
                logger.info(f"Retrying {node_name} in {delay:.2f}s (attempt {attempt + 2}/{retry_config.max_attempts})")
                await asyncio.sleep(delay)
    
    # All retries exhausted - create final error
    final_error = _create_node_error(
        last_error, node_name, error_category, retry_config.max_attempts - 1, False
    )
    
    logger.error(f"Node {node_name} failed after {retry_config.max_attempts} attempts")
    _add_error_to_state(state, final_error)
    
    # Return modified state with error information
    return state

def _create_node_error(
    exception: Exception,
    node_name: str,
    category: ErrorCategory,
    retry_count: int,
    recoverable: bool
) -> NodeError:
    """Create structured node error from exception."""
    
    # Determine severity based on exception type and retry count
    severity = ErrorSeverity.MEDIUM
    if isinstance(exception, (ConnectionError, TimeoutError)):
        severity = ErrorSeverity.HIGH if retry_count > 2 else ErrorSeverity.MEDIUM
    elif isinstance(exception, (PermissionError, AuthenticationError)):
        severity = ErrorSeverity.CRITICAL
    elif isinstance(exception, ValueError):
        severity = ErrorSeverity.LOW
    
    # Generate error code
    error_code = f"{node_name.upper()}_{type(exception).__name__.upper()}"
    
    return NodeError(
        error_code=error_code,
        error_message=str(exception),
        severity=severity,
        category=category,
        node_name=node_name,
        retry_count=retry_count,
        recoverable=recoverable,
        context={
            "exception_type": type(exception).__name__,
            "exception_module": type(exception).__module__,
        }
    )

def _log_node_error(error: NodeError, is_retry: bool):
    """Log node error with appropriate level."""
    
    log_level = {
        ErrorSeverity.LOW: logging.INFO,
        ErrorSeverity.MEDIUM: logging.WARNING,
        ErrorSeverity.HIGH: logging.ERROR,
        ErrorSeverity.CRITICAL: logging.CRITICAL
    }.get(error.severity, logging.ERROR)
    
    action = "retrying" if is_retry else "failed permanently"
    logger.log(
        log_level,
        f"Node {error.node_name} {action}: {error.error_message} "
        f"(severity: {error.severity}, category: {error.category})"
    )

def _add_error_to_state(state: Any, error: NodeError):
    """Add error information to state if possible."""
    try:
        if hasattr(state, 'processing_errors'):
            if not isinstance(state.processing_errors, list):
                state.processing_errors = []
            state.processing_errors.append(error.dict())
        elif hasattr(state, '__dict__'):
            # Add to arbitrary state object
            if not hasattr(state, 'processing_errors'):
                state.processing_errors = []
            state.processing_errors.append(error.dict())
    except Exception as e:
        logger.warning(f"Failed to add error to state: {e}")

def _calculate_retry_delay(config: RetryConfig, attempt: int) -> float:
    """Calculate retry delay with exponential backoff."""
    if not config.exponential_backoff:
        return config.base_delay
    
    delay = config.base_delay * (2 ** attempt)
    return min(delay, config.max_delay)

# Custom exception for authentication errors
class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass

# Production-ready node error handler for common use cases
class NodeErrorHandler:
    """Centralized error handling for agent nodes."""
    
    @staticmethod
    def handle_api_error(error: Exception, node_name: str, api_name: str) -> NodeError:
        """Handle API-related errors."""
        category = ErrorCategory.EXTERNAL_SERVICE
        
        if "rate limit" in str(error).lower():
            category = ErrorCategory.API_LIMIT
        elif "unauthorized" in str(error).lower() or "forbidden" in str(error).lower():
            category = ErrorCategory.AUTHENTICATION
        elif "timeout" in str(error).lower():
            category = ErrorCategory.NETWORK
        
        return _create_node_error(error, node_name, category, 0, True)
    
    @staticmethod
    def handle_validation_error(error: Exception, node_name: str) -> NodeError:
        """Handle validation errors."""
        return _create_node_error(error, node_name, ErrorCategory.VALIDATION, 0, False)
    
    @staticmethod
    def handle_processing_error(error: Exception, node_name: str) -> NodeError:
        """Handle general processing errors."""
        return _create_node_error(error, node_name, ErrorCategory.PROCESSING, 0, True)