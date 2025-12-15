# --- structured_logging.py ---
"""Structured logging with proper log levels and JSON format."""
import json
import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path
import streamlit as st

st: Any = st

# Log levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


class StructuredLogger:
    """Structured logger that outputs JSON formatted logs."""
    
    def __init__(self, name: str, log_file: Optional[Path] = None):
        """Initialize structured logger.
        
        Args:
            name: Logger name
            log_file: Optional log file path
        """
        self.name = name
        self.log_file = log_file
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler with JSON formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(console_handler)
        
        # File handler if log file specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(file_handler)
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """Internal logging method.
        
        Args:
            level: Log level
            message: Log message
            **kwargs: Additional context
        """
        extra = {
            "timestamp": datetime.now().isoformat(),
            "logger": self.name,
            **kwargs
        }
        log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
        self.logger.log(log_level, message, extra=extra)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._log("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._log("CRITICAL", message, **kwargs)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record
            
        Returns:
            JSON formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": record.created,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str)


# Global logger instance
_app_logger: Optional[StructuredLogger] = None


def get_logger(name: str = "claims_mapper") -> StructuredLogger:
    """Get or create a structured logger.
    
    Args:
        name: Logger name
        
    Returns:
        StructuredLogger instance
    """
    global _app_logger
    if _app_logger is None:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        _app_logger = StructuredLogger(name, log_file)
    return _app_logger


def log_performance(operation: str, duration: float, **kwargs) -> None:
    """Log performance metrics.
    
    Args:
        operation: Operation name
        duration: Duration in seconds
        **kwargs: Additional context
    """
    logger = get_logger()
    logger.info(
        f"Performance: {operation}",
        operation=operation,
        duration_seconds=duration,
        **kwargs
    )


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log an error with context.
    
    Args:
        error: Exception object
        context: Additional context
    """
    logger = get_logger()
    logger.error(
        f"Error: {str(error)}",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {}
    )

