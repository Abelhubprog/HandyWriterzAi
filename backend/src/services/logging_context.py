import logging
import uuid
import contextvars
from contextlib import contextmanager
from typing import Optional

# Context variable to store the current correlation ID
_correlation_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("correlation_id", default=None)


def get_correlation_id() -> Optional[str]:
    """Retrieve the current correlation ID, if any."""
    return _correlation_id.get()


@contextmanager
def with_correlation_context(correlation_id: Optional[str] = None):
    """
    Context manager that sets a correlation ID for the duration of the block.
    If no ID is provided, a new UUID4 string is generated.
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    token = _correlation_id.set(correlation_id)
    try:
        yield
    finally:
        _correlation_id.reset(token)


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter that injects the current correlation ID into log records.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id() or "N/A"
        return True


def setup_correlation_logging(level: int = logging.INFO):
    """
    Configure the root logger (or any logger) to include correlation IDs.
    Adds a filter and a simple formatter that prints the correlation ID.
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    # Ensure the filter is added only once
    if not any(isinstance(f, CorrelationIdFilter) for f in logger.filters):
        logger.addFilter(CorrelationIdFilter())

    # Simple formatter that includes correlation ID
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(correlation_id)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Attach formatter to all existing handlers or create a default StreamHandler
    if logger.handlers:
        for handler in logger.handlers:
            handler.setFormatter(formatter)
    else:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
