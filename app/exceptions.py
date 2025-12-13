# --- exceptions.py ---
"""Custom exception classes for the application."""

from typing import Optional, Dict, Any


class ClaimsMapperError(Exception):
    """Base exception for all application errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context
        }


class FileError(ClaimsMapperError):
    """Errors related to file operations."""
    pass


class FileNotFoundError(FileError):
    """File not found error."""
    
    def __init__(self, file_path: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"File not found: {file_path}",
            error_code="FILE_NOT_FOUND",
            context={"file_path": file_path, **(context or {})}
        )


class FileFormatError(FileError):
    """Unsupported or invalid file format error."""
    
    def __init__(self, file_format: str, supported_formats: Optional[list] = None, context: Optional[Dict[str, Any]] = None):
        supported = supported_formats or []
        super().__init__(
            f"Unsupported file format: {file_format}. Supported formats: {', '.join(supported)}",
            error_code="FILE_FORMAT_ERROR",
            context={"file_format": file_format, "supported_formats": supported, **(context or {})}
        )


class FileSizeError(FileError):
    """File size exceeds limit error."""
    
    def __init__(self, file_size: int, max_size: int, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)",
            error_code="FILE_SIZE_ERROR",
            context={"file_size": file_size, "max_size": max_size, **(context or {})}
        )


class EncodingError(FileError):
    """File encoding error."""
    
    def __init__(self, encoding: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Unable to decode file with encoding: {encoding}",
            error_code="ENCODING_ERROR",
            context={"encoding": encoding, **(context or {})}
        )


class ValidationError(ClaimsMapperError):
    """Errors related to data validation."""
    pass


class FieldValidationError(ValidationError):
    """Field-level validation error."""
    
    def __init__(self, field: str, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Validation failed for field '{field}': {message}",
            error_code="FIELD_VALIDATION_ERROR",
            context={"field": field, "message": message, **(context or {})}
        )


class FileValidationError(ValidationError):
    """File-level validation error."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"File validation failed: {message}",
            error_code="FILE_VALIDATION_ERROR",
            context={"message": message, **(context or {})}
        )


class MappingError(ClaimsMapperError):
    """Errors related to field mapping."""
    pass


class MappingNotFoundError(MappingError):
    """Mapping not found error."""
    
    def __init__(self, field: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Mapping not found for field: {field}",
            error_code="MAPPING_NOT_FOUND",
            context={"field": field, **(context or {})}
        )


class MappingValidationError(MappingError):
    """Mapping validation error."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Mapping validation failed: {message}",
            error_code="MAPPING_VALIDATION_ERROR",
            context={"message": message, **(context or {})}
        )


class TransformationError(ClaimsMapperError):
    """Errors related to data transformation."""
    pass


class CacheError(ClaimsMapperError):
    """Errors related to caching."""
    pass


class ConfigurationError(ClaimsMapperError):
    """Errors related to configuration."""
    pass


class StateError(ClaimsMapperError):
    """Errors related to session state."""
    pass


class ProcessingError(ClaimsMapperError):
    """Errors related to data processing operations."""
    pass

