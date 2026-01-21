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


# --- Monitoring and Analytics Functions (migrated from monitoring_logging.py) ---
import os
import traceback
from typing import List


def save_audit_log_to_file(log_file: str = "audit_log.json") -> None:
    """Save audit log to persistent file.
    
    Args:
        log_file: Log file path
    """
    if "audit_log" not in st.session_state:
        return
    
    try:
        # Load existing logs
        existing_logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                existing_logs = json.load(f)
        
        # Append new logs
        new_logs = st.session_state.audit_log
        all_logs = existing_logs + new_logs
        
        # Keep only last 1000 entries
        all_logs = all_logs[-1000:]
        
        # Save to file
        with open(log_file, 'w') as f:
            json.dump(all_logs, f, indent=2)
    except Exception:
        pass  # Silently fail


def load_audit_log_from_file(log_file: str = "audit_log.json") -> List[Dict[str, Any]]:
    """Load audit log from file.
    
    Args:
        log_file: Log file path
        
    Returns:
        List of log entries
    """
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    
    return []


def track_error(error_type: str, error_message: str, 
               context: Optional[Dict[str, Any]] = None) -> None:
    """Track an error.
    
    Args:
        error_type: Type of error
        error_message: Error message
        context: Optional context information
    """
    error_record = {
        "type": error_type,
        "message": error_message,
        "context": context or {},
        "timestamp": datetime.now().isoformat(),
        "traceback": traceback.format_exc() if traceback else None
    }
    
    if "error_log" not in st.session_state:
        st.session_state.error_log = []
    
    st.session_state.error_log.append(error_record)
    
    # Keep only last 100 errors
    if len(st.session_state.error_log) > 100:
        st.session_state.error_log = st.session_state.error_log[-100:]


def get_error_statistics() -> Dict[str, Any]:
    """Get error statistics.
    
    Returns:
        Error statistics dictionary
    """
    if "error_log" not in st.session_state:
        return {
            "total_errors": 0,
            "errors_by_type": {},
            "recent_errors": []
        }
    
    errors = st.session_state.error_log
    
    errors_by_type = {}
    for error in errors:
        error_type = error.get("type", "unknown")
        errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1
    
    return {
        "total_errors": len(errors),
        "errors_by_type": errors_by_type,
        "recent_errors": errors[-10:]  # Last 10 errors
    }


def track_feature_usage(feature_name: str, action: str,
                       metadata: Optional[Dict[str, Any]] = None) -> None:
    """Track feature usage.
    
    Args:
        feature_name: Name of feature
        action: Action performed
        metadata: Optional metadata
    """
    usage_record = {
        "feature": feature_name,
        "action": action,
        "metadata": metadata or {},
        "timestamp": datetime.now().isoformat()
    }
    
    if "usage_analytics" not in st.session_state:
        st.session_state.usage_analytics = []
    
    st.session_state.usage_analytics.append(usage_record)
    
    # Keep only last 500 records
    if len(st.session_state.usage_analytics) > 500:
        st.session_state.usage_analytics = st.session_state.usage_analytics[-500:]


def get_usage_statistics() -> Dict[str, Any]:
    """Get usage statistics.
    
    Returns:
        Usage statistics dictionary
    """
    if "usage_analytics" not in st.session_state:
        return {
            "total_actions": 0,
            "features_used": {},
            "actions_by_feature": {}
        }
    
    analytics = st.session_state.usage_analytics
    
    features_used = {}
    actions_by_feature = {}
    
    for record in analytics:
        feature = record.get("feature", "unknown")
        action = record.get("action", "unknown")
        
        features_used[feature] = features_used.get(feature, 0) + 1
        
        if feature not in actions_by_feature:
            actions_by_feature[feature] = {}
        actions_by_feature[feature][action] = actions_by_feature[feature].get(action, 0) + 1
    
    return {
        "total_actions": len(analytics),
        "features_used": features_used,
        "actions_by_feature": actions_by_feature
    }


def get_system_health() -> Dict[str, Any]:
    """Get system health metrics.
    
    Returns:
        Health metrics dictionary
    """
    import sys
    
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_mb": memory_info.rss / 1024 / 1024,
            "memory_percent": process.memory_percent(),
            "threads": process.num_threads(),
            "python_version": sys.version.split()[0]
        }
    except ImportError:
        # psutil not installed - return default values
        return {
            "cpu_percent": 0,
            "memory_mb": 0,
            "memory_percent": 0,
            "threads": 0,
            "python_version": sys.version.split()[0] if 'sys' in locals() else "unknown"
        }
    except Exception:
        # Other errors - return default values
        return {
            "cpu_percent": 0,
            "memory_mb": 0,
            "memory_percent": 0,
            "threads": 0,
            "python_version": sys.version.split()[0] if 'sys' in locals() else "unknown"
        }


def export_logs(log_type: str = "audit", format: str = "json") -> str:
    """Export logs in specified format.
    
    Args:
        log_type: Type of log (audit, error, usage)
        format: Export format (json, csv)
        
    Returns:
        Exported log data as string
    """
    logs = []
    
    if log_type == "audit" and "audit_log" in st.session_state:
        logs = st.session_state.audit_log
    elif log_type == "error" and "error_log" in st.session_state:
        logs = st.session_state.error_log
    elif log_type == "usage" and "usage_analytics" in st.session_state:
        logs = st.session_state.usage_analytics
    
    if format == "json":
        return json.dumps(logs, indent=2)
    elif format == "csv":
        import pandas as pd
        if logs:
            df = pd.DataFrame(logs)
            return df.to_csv(index=False)
        return ""
    
    return ""

