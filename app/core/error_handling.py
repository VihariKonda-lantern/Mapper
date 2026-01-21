# --- error_handling.py ---
"""Enhanced error handling with error codes, suggestions, and user-friendly messages.
Also includes error context managers (migrated from error_context.py)."""
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional
from core.exceptions import (
    ClaimsMapperError,
    FileError,
    ValidationError,
    MappingError,
    ProcessingError
)

# --- Error Context Managers (migrated from error_context.py) ---
from contextlib import contextmanager
from typing import Generator
from utils.structured_logging import StructuredLogger

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
    from utils.structured_logging import StructuredLogger
    logger = StructuredLogger("error_context")
    context = context or {}
    try:
        yield
    except ClaimsMapperError as e:
        logger.error(
            f"Error in {operation}",
            operation=operation,
            error_code=e.error_code,
            context={**context, **e.context}
        )
        if raise_on_error:
            raise
    except Exception as e:
        logger.error(
            f"Unexpected error in {operation}",
            operation=operation,
            error_type=type(e).__name__,
            error_message=str(e),
            context=context
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
    from utils.structured_logging import StructuredLogger
    import time
    logger = StructuredLogger("error_context")
    current_delay = delay
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            yield
            return
        except exceptions as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warning(
                    f"Retry attempt {attempt + 1}/{max_retries}",
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    error=str(e),
                    retry_delay=current_delay
                )
                time.sleep(current_delay)
                current_delay *= backoff
            else:
                logger.error(
                    f"All retry attempts exhausted",
                    max_retries=max_retries,
                    final_error=str(e)
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
    from utils.structured_logging import StructuredLogger
    logger = StructuredLogger("error_context")
    try:
        yield
    except Exception as e:
        if log_warning:
            logger.warning(
                "Operation failed, using fallback",
                error=str(e),
                fallback_value=str(fallback_value)
            )
        # Don't raise, allow execution to continue with fallback


class ErrorAggregator:
    """Collects multiple errors and reports them together."""
    
    def __init__(self) -> None:
        self.errors: List[Dict[str, Any]] = []
    
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


# Error code registry with user-friendly messages and suggestions
ERROR_REGISTRY: Dict[str, Dict[str, Any]] = {
    "FILE_NOT_FOUND": {
        "message": "The file you're trying to access could not be found.",
        "suggestions": [
            "Check if the file path is correct",
            "Verify the file exists in the specified location",
            "Ensure you have read permissions for the file"
        ],
        "help_url": "/help/file_upload"
    },
    "FILE_TOO_LARGE": {
        "message": "The uploaded file is too large.",
        "suggestions": [
            "Try splitting the file into smaller chunks",
            "Check the maximum file size limit",
            "Consider compressing the file before upload"
        ],
        "help_url": "/help/file_upload"
    },
    "INVALID_FILE_FORMAT": {
        "message": "The file format is not supported.",
        "suggestions": [
            "Ensure the file is in CSV, Excel, or JSON format",
            "Check the file extension matches the content",
            "Verify the file is not corrupted"
        ],
        "help_url": "/help/file_upload"
    },
    "MISSING_REQUIRED_FIELD": {
        "message": "A required field is missing from your data.",
        "suggestions": [
            "Check the layout file for required fields",
            "Ensure all mandatory fields are present in your source data",
            "Review the field mapping to verify required fields are mapped"
        ],
        "help_url": "/help/mapping"
    },
    "MAPPING_VALIDATION_FAILED": {
        "message": "The field mapping validation failed.",
        "suggestions": [
            "Review the mapping configuration",
            "Check that all required fields are mapped",
            "Verify source column names match your data"
        ],
        "help_url": "/help/mapping"
    },
    "VALIDATION_ERROR": {
        "message": "Data validation failed.",
        "suggestions": [
            "Review the validation results for details",
            "Check data quality metrics",
            "Fix data issues and re-validate"
        ],
        "help_url": "/help/validation"
    },
    "TRANSFORMATION_ERROR": {
        "message": "An error occurred while transforming the data.",
        "suggestions": [
            "Check the mapping configuration",
            "Verify source data format",
            "Review transformation logs for details"
        ],
        "help_url": "/help/validation"
    },
    "UNEXPECTED_ERROR": {
        "message": "An unexpected error occurred.",
        "suggestions": [
            "Try refreshing the page",
            "Check if all required files are uploaded",
            "Contact support if the issue persists"
        ],
        "help_url": "/help/troubleshooting"
    },
    "AGGREGATED_ERRORS": {
        "message": "Multiple errors occurred during processing.",
        "suggestions": [
            "Review all error messages below",
            "Address errors one by one",
            "Check the error summary for patterns"
        ],
        "help_url": "/help/troubleshooting"
    }
}


def get_error_info(error: Exception) -> Dict[str, Any]:
    """
    Get comprehensive error information including code, message, and suggestions.
    
    Args:
        error: The exception that occurred
    
    Returns:
        Dictionary with error_code, message, suggestions, and help_url
    """
    if isinstance(error, ClaimsMapperError):
        error_code = error.error_code
        registry_entry = ERROR_REGISTRY.get(error_code, {})
        
        return {
            "error_code": error_code,
            "message": registry_entry.get("message", error.message),
            "suggestions": registry_entry.get("suggestions", []),
            "help_url": registry_entry.get("help_url", "/help"),
            "technical_details": str(error),
            "context": error.context
        }
    
    # Handle standard exceptions
    error_type = type(error).__name__
    error_str = str(error)
    
    if "FileNotFound" in error_type or "FileNotFoundError" in error_type:
        error_code = "FILE_NOT_FOUND"
    elif "Permission" in error_type or "PermissionError" in error_type:
        error_code = "PERMISSION_ERROR"
    elif "ValueError" in error_type:
        error_code = "VALIDATION_ERROR"
        # For ValueError, show the actual error message
        return {
            "error_code": error_code,
            "message": error_str if error_str else "Validation error occurred",
            "suggestions": ERROR_REGISTRY.get("VALIDATION_ERROR", {}).get("suggestions", []),
            "help_url": ERROR_REGISTRY.get("VALIDATION_ERROR", {}).get("help_url", "/help"),
            "technical_details": error_str,
            "context": {}
        }
    elif "ImportError" in error_type or "ModuleNotFoundError" in error_type:
        error_code = "MISSING_DEPENDENCY"
        # For ImportError, show the actual error message directly
        return {
            "error_code": error_code,
            "message": error_str if error_str else "A required package is missing",
            "suggestions": [
                "Install the missing package using pip",
                "Check that all dependencies from requirements.txt are installed",
                "Try: pip install -r requirements.txt"
            ],
            "help_url": "/help/installation",
            "technical_details": error_str,
            "context": {}
        }
    elif "KeyError" in error_type:
        error_code = "MISSING_REQUIRED_FIELD"
    elif "AttributeError" in error_type:
        error_code = "UNEXPECTED_ERROR"
        # For AttributeError, show more details
        return {
            "error_code": error_code,
            "message": f"Configuration error: {error_str}" if error_str else "An unexpected configuration error occurred",
            "suggestions": ERROR_REGISTRY.get("UNEXPECTED_ERROR", {}).get("suggestions", []),
            "help_url": ERROR_REGISTRY.get("UNEXPECTED_ERROR", {}).get("help_url", "/help"),
            "technical_details": error_str,
            "context": {}
        }
    else:
        error_code = "UNEXPECTED_ERROR"
    
    registry_entry = ERROR_REGISTRY.get(error_code, ERROR_REGISTRY["UNEXPECTED_ERROR"])
    
    # For unexpected errors, try to show the actual error message if it's informative
    message = registry_entry.get("message", "An unexpected error occurred")
    if error_code == "UNEXPECTED_ERROR" and error_str and len(error_str) < 200:
        # If the error message is short and informative, show it directly instead of prefixing
        message = error_str
    
    return {
        "error_code": error_code,
        "message": message,
        "suggestions": registry_entry.get("suggestions", []),
        "help_url": registry_entry.get("help_url", "/help"),
        "technical_details": error_str,
        "context": {}
    }


def get_user_friendly_error(error: Exception) -> str:
    """
    Get a user-friendly error message from an exception.
    
    Args:
        error: The exception that occurred
    
    Returns:
        User-friendly error message
    """
    error_info = get_error_info(error)
    return error_info["message"]


def get_error_suggestions(error: Exception) -> List[str]:
    """
    Get actionable suggestions for resolving an error.
    
    Args:
        error: The exception that occurred
    
    Returns:
        List of suggestion strings
    """
    error_info = get_error_info(error)
    return error_info["suggestions"]


def format_error_for_display(error: Exception) -> Dict[str, Any]:
    """
    Format error information for display in the UI.
    
    Args:
        error: The exception that occurred
    
    Returns:
        Dictionary formatted for UI display
    """
    error_info = get_error_info(error)
    
    return {
        "title": "Error",
        "message": error_info["message"],
        "error_code": error_info["error_code"],
        "suggestions": error_info["suggestions"],
        "help_url": error_info["help_url"],
        "show_technical_details": False,
        "technical_details": error_info["technical_details"] if error_info.get("context") else None
    }


class ErrorHistory:
    """Track recent errors with resolution steps."""
    
    def __init__(self, max_size: int = 50) -> None:
        self.errors: List[Dict[str, Any]] = []
        self.max_size = max_size
    
    def add_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Add an error to the history."""
        error_info = get_error_info(error)
        error_entry = {
            "timestamp": str(__import__("datetime").datetime.now()),
            "error_code": error_info["error_code"],
            "message": error_info["message"],
            "suggestions": error_info["suggestions"],
            "context": context or {},
            "resolved": False
        }
        
        self.errors.append(error_entry)
        if len(self.errors) > self.max_size:
            self.errors.pop(0)
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors."""
        return self.errors[-limit:][::-1]
    
    def mark_resolved(self, error_code: str) -> None:
        """Mark errors with a specific code as resolved."""
        for error in self.errors:
            if error["error_code"] == error_code:
                error["resolved"] = True
    
    def get_unresolved_errors(self) -> List[Dict[str, Any]]:
        """Get unresolved errors."""
        return [e for e in self.errors if not e["resolved"]]


# Global error history instance
error_history = ErrorHistory()

