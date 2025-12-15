# --- error_context.py ---
"""Error context managers for better error tracking and recovery."""
from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional
from core.exceptions import ClaimsMapperError
from monitoring.structured_logging import StructuredLogger

logger = StructuredLogger("error_context")


@contextmanager
def error_context(
    operation: str,
    context: Optional[Dict[str, Any]] = None,
    raise_on_error: bool = True
) -> Generator[None, None, None]:
    """
    Context manager for error tracking with context.
    
    Args:
        operation: Name of the operation being performed
        context: Additional context information
        raise_on_error: Whether to re-raise the exception
    
    Example:
        with error_context("file_upload", {"filename": "data.csv"}):
            process_file("data.csv")
    """
    context = context or {}
    try:
        yield
    except ClaimsMapperError as e:
        logger.log_error(
            f"Error in {operation}",
            {
                "operation": operation,
                "error_code": e.error_code,
                "context": {**context, **e.context}
            }
        )
        if raise_on_error:
            raise
    except Exception as e:
        logger.log_error(
            f"Unexpected error in {operation}",
            {
                "operation": operation,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "context": context
            }
        )
        if raise_on_error:
            raise ClaimsMapperError(
                f"Unexpected error in {operation}: {str(e)}",
                error_code="UNEXPECTED_ERROR",
                context=context
            ) from e


@contextmanager
def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Generator[None, None, None]:
    """
    Context manager for retry logic on transient failures.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry on
    
    Example:
        with retry_on_error(max_retries=3, delay=1.0):
            api_call()
    """
    import time
    current_delay = delay
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            yield
            return
        except exceptions as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.log_warning(
                    f"Retry attempt {attempt + 1}/{max_retries}",
                    {
                        "attempt": attempt + 1,
                        "max_retries": max_retries,
                        "error": str(e),
                        "retry_delay": current_delay
                    }
                )
                time.sleep(current_delay)
                current_delay *= backoff
            else:
                logger.log_error(
                    f"All retry attempts exhausted",
                    {
                        "max_retries": max_retries,
                        "final_error": str(e)
                    }
                )
    
    if last_exception:
        raise last_exception


@contextmanager
def graceful_degradation(
    fallback_value: Any = None,
    log_warning: bool = True
) -> Generator[None, None, None]:
    """
    Context manager for graceful degradation when non-critical errors occur.
    
    Args:
        fallback_value: Value to return if operation fails
        log_warning: Whether to log a warning on failure
    
    Example:
        with graceful_degradation(fallback_value=[]):
            result = expensive_operation()
    """
    try:
        yield
    except Exception as e:
        if log_warning:
            logger.log_warning(
                "Operation failed, using fallback",
                {"error": str(e), "fallback_value": str(fallback_value)}
            )
        # Don't raise, allow execution to continue with fallback


class ErrorAggregator:
    """Collects multiple errors and reports them together."""
    
    def __init__(self) -> None:
        self.errors: list[Dict[str, Any]] = []
    
    def add_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Add an error to the collection."""
        self.errors.append({
            "error": error,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        })
    
    def has_errors(self) -> bool:
        """Check if any errors were collected."""
        return len(self.errors) > 0
    
    def raise_if_errors(self) -> None:
        """Raise an aggregated error if any errors were collected."""
        if self.has_errors():
            error_messages = [e["error_message"] for e in self.errors]
            raise ClaimsMapperError(
                f"Multiple errors occurred: {', '.join(error_messages)}",
                error_code="AGGREGATED_ERRORS",
                context={"error_count": len(self.errors), "errors": self.errors}
            )
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected errors."""
        return {
            "total_errors": len(self.errors),
            "errors": [
                {
                    "type": e["error_type"],
                    "message": e["error_message"],
                    "context": e["context"]
                }
                for e in self.errors
            ]
        }

