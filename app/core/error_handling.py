# --- error_handling.py ---
"""Enhanced error handling with error codes, suggestions, and user-friendly messages."""
from typing import Any, Dict, List, Optional
from core.exceptions import (
    ClaimsMapperError,
    FileError,
    ValidationError,
    MappingError,
    ProcessingError
)

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
    if "FileNotFound" in error_type or "FileNotFoundError" in error_type:
        error_code = "FILE_NOT_FOUND"
    elif "Permission" in error_type or "PermissionError" in error_type:
        error_code = "PERMISSION_ERROR"
    elif "ValueError" in error_type:
        error_code = "VALIDATION_ERROR"
    elif "KeyError" in error_type:
        error_code = "MISSING_REQUIRED_FIELD"
    else:
        error_code = "UNEXPECTED_ERROR"
    
    registry_entry = ERROR_REGISTRY.get(error_code, ERROR_REGISTRY["UNEXPECTED_ERROR"])
    
    return {
        "error_code": error_code,
        "message": registry_entry.get("message", str(error)),
        "suggestions": registry_entry.get("suggestions", []),
        "help_url": registry_entry.get("help_url", "/help"),
        "technical_details": str(error),
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

