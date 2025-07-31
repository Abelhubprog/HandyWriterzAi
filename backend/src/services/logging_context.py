"""
Logging Context Service for HandyWriterzAI

Provides correlation ID generation and request-scoped logging context
for improved debugging and monitoring.
"""

import logging
import uuid
import contextvars
from typing import Dict, Any, Optional
from datetime import datetime

# Context variables for request-scoped data
correlation_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'correlation_id', default=None
)
conversation_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'conversation_id', default=None
)
user_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'user_id', default=None
)
node_name_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'node_name', default=None
)
phase_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'phase', default=None
)


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter that adds correlation context to log records.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation context to log record."""
        
        # Get context values
        correlation_id = correlation_id_var.get()
        conversation_id = conversation_id_var.get()
        user_id = user_id_var.get()
        node_name = node_name_var.get()
        phase = phase_var.get()
        
        # Add to log record
        record.correlation_id = correlation_id or "unknown"
        record.conversation_id = conversation_id or "unknown"
        record.user_id = user_id or "anonymous"
        record.node_name = node_name or "system"
        record.phase = phase or "general"
        
        return True


class LoggingContext:
    """
    Context manager for request-scoped logging context.
    """
    
    def __init__(
        self,
        correlation_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        node_name: Optional[str] = None,
        phase: Optional[str] = None
    ):
        self.correlation_id = correlation_id or generate_correlation_id()
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.node_name = node_name
        self.phase = phase
        
        # Store previous values for restoration
        self._prev_correlation_id = None
        self._prev_conversation_id = None
        self._prev_user_id = None
        self._prev_node_name = None
        self._prev_phase = None
    
    def __enter__(self):
        """Enter context and set context variables."""
        self._prev_correlation_id = correlation_id_var.get()
        self._prev_conversation_id = conversation_id_var.get()
        self._prev_user_id = user_id_var.get()
        self._prev_node_name = node_name_var.get()
        self._prev_phase = phase_var.get()
        
        correlation_id_var.set(self.correlation_id)
        if self.conversation_id:
            conversation_id_var.set(self.conversation_id)
        if self.user_id:
            user_id_var.set(self.user_id)
        if self.node_name:
            node_name_var.set(self.node_name)
        if self.phase:
            phase_var.set(self.phase)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore previous values."""
        correlation_id_var.set(self._prev_correlation_id)
        conversation_id_var.set(self._prev_conversation_id)
        user_id_var.set(self._prev_user_id)
        node_name_var.set(self._prev_node_name)
        phase_var.set(self._prev_phase)
    
    def get_context_dict(self) -> Dict[str, Any]:
        """Get current context as dictionary."""
        return {
            "correlation_id": self.correlation_id,
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "node_name": self.node_name,
            "phase": self.phase,
            "timestamp": datetime.utcnow().isoformat()
        }


def generate_correlation_id(conversation_id: Optional[str] = None) -> str:
    """
    Generate correlation ID from conversation ID or create new UUID.
    
    Args:
        conversation_id: Optional conversation ID to derive from
        
    Returns:
        Correlation ID string
    """
    if conversation_id:
        # Use conversation ID as base for correlation
        return f"corr_{conversation_id}"
    else:
        # Generate new UUID
        return f"corr_{uuid.uuid4().hex[:12]}"


def get_current_correlation_id() -> Optional[str]:
    """Get current correlation ID from context."""
    return correlation_id_var.get()


def get_current_conversation_id() -> Optional[str]:
    """Get current conversation ID from context."""
    return conversation_id_var.get()


def get_current_context() -> Dict[str, Any]:
    """Get all current context variables."""
    return {
        "correlation_id": correlation_id_var.get(),
        "conversation_id": conversation_id_var.get(),
        "user_id": user_id_var.get(),
        "node_name": node_name_var.get(),
        "phase": phase_var.get(),
        "timestamp": datetime.utcnow().isoformat()
    }


def set_node_context(node_name: str, phase: Optional[str] = None) -> None:
    """
    Set node name and optional phase in current context.
    
    Args:
        node_name: Name of the current node/component
        phase: Optional phase within the node
    """
    node_name_var.set(node_name)
    if phase:
        phase_var.set(phase)


def set_phase(phase: str) -> None:
    """
    Set phase in current context.
    
    Args:
        phase: Current phase/stage of processing
    """
    phase_var.set(phase)


def create_structured_logger(name: str) -> logging.Logger:
    """
    Create logger with correlation context formatting.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Add correlation filter if not already present
    if not any(isinstance(f, CorrelationIdFilter) for f in logger.filters):
        logger.addFilter(CorrelationIdFilter())
    
    return logger


def setup_correlation_logging():
    """
    Setup correlation ID logging for the root logger.
    """
    root_logger = logging.getLogger()
    
    # Add correlation filter to root logger
    correlation_filter = CorrelationIdFilter()
    root_logger.addFilter(correlation_filter)
    
    # Update formatter to include correlation fields
    for handler in root_logger.handlers:
        if handler.formatter:
            # Get current format string
            current_format = handler.formatter._fmt
            if current_format and "correlation_id" not in current_format:
                # Add correlation fields to format
                new_format = (
                    "%(asctime)s - %(name)s - %(levelname)s - "
                    "[%(correlation_id)s] [%(conversation_id)s] "
                    "[%(node_name)s:%(phase)s] - %(message)s"
                )
                handler.setFormatter(logging.Formatter(new_format))


# Context manager aliases for convenience
def with_correlation_context(
    correlation_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    user_id: Optional[str] = None,
    node_name: Optional[str] = None,
    phase: Optional[str] = None
) -> LoggingContext:
    """
    Create logging context manager.
    
    Args:
        correlation_id: Correlation ID (auto-generated if None)
        conversation_id: Conversation ID
        user_id: User ID
        node_name: Node/component name
        phase: Processing phase
        
    Returns:
        LoggingContext manager
    """
    return LoggingContext(
        correlation_id=correlation_id,
        conversation_id=conversation_id,
        user_id=user_id,
        node_name=node_name,
        phase=phase
    )


def with_node_context(node_name: str, phase: Optional[str] = None) -> LoggingContext:
    """
    Create logging context for a specific node.
    
    Args:
        node_name: Name of the node/component
        phase: Optional processing phase
        
    Returns:
        LoggingContext manager
    """
    return LoggingContext(
        correlation_id=get_current_correlation_id(),
        conversation_id=get_current_conversation_id(),
        user_id=user_id_var.get(),
        node_name=node_name,
        phase=phase
    )


def with_phase_context(phase: str) -> LoggingContext:
    """
    Create logging context for a specific phase.
    
    Args:
        phase: Processing phase
        
    Returns:
        LoggingContext manager
    """
    return LoggingContext(
        correlation_id=get_current_correlation_id(),
        conversation_id=get_current_conversation_id(),
        user_id=user_id_var.get(),
        node_name=node_name_var.get(),
        phase=phase
    )


# Decorator for automatic correlation context
def with_correlation(
    node_name: Optional[str] = None,
    phase: Optional[str] = None
):
    """
    Decorator to automatically set correlation context for functions.
    
    Args:
        node_name: Node name to set in context
        phase: Phase to set in context
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract conversation_id from args/kwargs if available
            conversation_id = None
            
            # Check common parameter names
            for arg_name in ['conversation_id', 'conv_id', 'trace_id']:
                if arg_name in kwargs:
                    conversation_id = kwargs[arg_name]
                    break
            
            # Check if first arg is a dict with conversation_id
            if args and isinstance(args[0], dict) and 'conversation_id' in args[0]:
                conversation_id = args[0]['conversation_id']
            
            with LoggingContext(
                correlation_id=generate_correlation_id(conversation_id),
                conversation_id=conversation_id,
                node_name=node_name or func.__name__,
                phase=phase
            ):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator