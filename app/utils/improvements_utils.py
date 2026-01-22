# --- improvements_utils.py ---
"""Utility functions for UI/UX improvements."""
import streamlit as st
import pandas as pd
from typing import Any, Dict, List, Optional, Callable, Tuple
from datetime import datetime, timedelta
import time
import hashlib
import json

st: Any = st
pd: Any = pd


# --- Constants ---
MAX_FILE_SIZE_MB = 500
SESSION_TIMEOUT_MINUTES = 60
DEBOUNCE_DELAY_SECONDS = 0.5


# --- Debounce Decorator ---
def debounce(wait: float = DEBOUNCE_DELAY_SECONDS):
    """Debounce function calls to prevent excessive execution."""
    def decorator(func: Callable) -> Callable:
        last_call_time = {}
        
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_id = id(func)
            current_time = time.time()
            
            if func_id in last_call_time:
                elapsed = current_time - last_call_time[func_id]
                if elapsed < wait:
                    return None
            
            last_call_time[func_id] = current_time
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# --- Progress Indicator ---
def show_progress_with_callback(total: int, callback: Callable, *args: Any, **kwargs: Any) -> Any:
    """Show progress bar while executing callback."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        result = callback(*args, **kwargs)
        progress_bar.progress(1.0)
        status_text.empty()
        return result
    except Exception as e:
        progress_bar.empty()
        status_text.error(f"Error: {str(e)}")
        raise


# --- Empty State Helper ---
def render_empty_state(
    icon: str = "📭",
    title: str = "No Data Available",
    message: str = "Upload files to get started.",
    action_label: Optional[str] = None,
    action_callback: Optional[Callable] = None
) -> None:
    """Render a consistent empty state."""
    st.markdown(f"""
    <div style='text-align: center; padding: 2rem; color: #000000;'>
        <div style='font-size: 3rem; margin-bottom: 1rem;'>{icon}</div>
        <h3 style='color: #000000; margin-bottom: 0.5rem;'>{title}</h3>
        <p style='color: #000000;'>{message}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if action_label and action_callback:
        if st.button(action_label, use_container_width=True):
            action_callback()


# --- Loading Skeleton ---
def render_loading_skeleton(rows: int = 5, cols: int = 3) -> None:
    """Render a loading skeleton placeholder."""
    st.markdown("""
    <style>
    .skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: 4px;
        height: 20px;
        margin-bottom: 0.5rem;
    }
    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    for _ in range(rows):
        cols_html = "".join(['<div class="skeleton" style="width: 100%;"></div>'] * cols)
        st.markdown(f'<div style="display: flex; gap: 1rem;">{cols_html}</div>', unsafe_allow_html=True)


# --- User-Friendly Error Messages ---
ERROR_MESSAGES: Dict[str, str] = {
    "FileNotFoundError": "The file you're looking for wasn't found. Please check the file path and try again.",
    "PermissionError": "You don't have permission to access this file. Please check file permissions.",
    "ValueError": "The data format is incorrect. Please check your file and try again.",
    "KeyError": "A required field is missing from your data. Please verify all required fields are present.",
    "TypeError": "There's a type mismatch in your data. Please check data types and try again.",
    "UnicodeDecodeError": "The file encoding is not supported. Please save your file as UTF-8 and try again.",
    "pd.errors.EmptyDataError": "The file appears to be empty. Please upload a file with data.",
    "pd.errors.ParserError": "The file format is invalid. Please check the file format and delimiter.",
}


def get_user_friendly_error(error: Exception) -> str:
    """
    Get a user-friendly error message from an exception.
    
    Uses enhanced error handling if available, otherwise falls back to basic handling.
    
    Args:
        error: The exception that occurred
    
    Returns:
        User-friendly error message
    """
    # Try to use enhanced error handling
    try:
        from core.error_handling import get_user_friendly_error as _enhanced
        return _enhanced(error)
    except (ImportError, Exception):
        # Fallback to basic error message handling
        error_type = type(error).__name__
        error_message = str(error)
        
        # Check for specific error messages
        if error_type in ERROR_MESSAGES:
            return ERROR_MESSAGES[error_type]
        
        # Check for common error patterns
        if "encoding" in error_message.lower():
            return "File encoding issue. Please save your file as UTF-8 and try again."
        if "delimiter" in error_message.lower():
            return "Could not detect the file delimiter. Please specify the delimiter manually."
        if "memory" in error_message.lower():
            return "File is too large to process. Please split the file into smaller chunks."
        
        # Default fallback
        return f"An error occurred: {error_message}. Please try again or contact support if the issue persists."


# --- Input Validation ---
def validate_file_upload(file_obj: Any, max_size_mb: int = MAX_FILE_SIZE_MB) -> Tuple[bool, Optional[str]]:
    """Validate uploaded file."""
    if file_obj is None:
        return False, "No file uploaded."
    
    # Check file size
    file_size_mb = file_obj.size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return False, f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb} MB)."
    
    # Check file extension
    file_name = file_obj.name.lower()
    allowed_extensions = ['.csv', '.txt', '.xlsx', '.xls', '.parquet']
    if not any(file_name.endswith(ext) for ext in allowed_extensions):
        return False, f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
    
    return True, None


# --- Session Timeout ---
def check_session_timeout() -> bool:
    """Check if session has timed out."""
    last_activity = st.session_state.get("last_activity_time")
    if last_activity is None:
        st.session_state.last_activity_time = datetime.now()
        return False
    
    elapsed = datetime.now() - last_activity
    if elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        return True
    
    return False


def update_activity_time() -> None:
    """Update last activity time."""
    st.session_state.last_activity_time = datetime.now()


# --- Rate Limiting ---
def check_rate_limit(action: str, max_calls: int = 10, window_seconds: int = 60) -> bool:
    """Check if action is within rate limit."""
    if "rate_limits" not in st.session_state:
        st.session_state.rate_limits = {}
    
    action_key = f"{action}_calls"
    action_time = f"{action}_time"
    
    if action_key not in st.session_state.rate_limits:
        st.session_state.rate_limits[action_key] = []
        st.session_state.rate_limits[action_time] = time.time()
    
    current_time = time.time()
    window_start = current_time - window_seconds
    
    # Clean old calls
    calls = st.session_state.rate_limits[action_key]
    calls = [call_time for call_time in calls if call_time > window_start]
    
    if len(calls) >= max_calls:
        return False
    
    calls.append(current_time)
    st.session_state.rate_limits[action_key] = calls
    
    return True


# --- Data Sanitization ---
def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input."""
    if not isinstance(text, str):
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '&', '"', "'"]
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()


# --- Performance Metrics ---
def track_operation_time(operation_name: str) -> Callable:
    """Decorator to track operation execution time."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                if "performance_metrics" not in st.session_state:
                    st.session_state.performance_metrics = []
                
                st.session_state.performance_metrics.append({
                    "operation": operation_name,
                    "duration": elapsed,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Keep only last 100 metrics
                if len(st.session_state.performance_metrics) > 100:
                    st.session_state.performance_metrics = st.session_state.performance_metrics[-100:]
                
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                if "performance_metrics" not in st.session_state:
                    st.session_state.performance_metrics = []
                
                st.session_state.performance_metrics.append({
                    "operation": operation_name,
                    "duration": elapsed,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                raise
        
        return wrapper
    return decorator


# --- Memory Usage Tracking ---
def get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage statistics."""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / (1024 * 1024),
            "vms_mb": memory_info.vms / (1024 * 1024),
            "percent": process.memory_percent()
        }
    except ImportError:
        return {
            "rss_mb": 0,
            "vms_mb": 0,
            "percent": 0,
            "error": "psutil not installed"
        }


# --- Data Compression ---
def compress_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Compress DataFrame to reduce memory usage."""
    if df is None or df.empty:
        return df
    
    compressed_df = df.copy()
    
    # Downcast integers
    for col in compressed_df.select_dtypes(include=['int64']).columns:
        compressed_df[col] = pd.to_numeric(compressed_df[col], downcast='integer')
    
    # Downcast floats
    for col in compressed_df.select_dtypes(include=['float64']).columns:
        compressed_df[col] = pd.to_numeric(compressed_df[col], downcast='float')
    
    # Convert object columns to category if beneficial
    for col in compressed_df.select_dtypes(include=['object']).columns:
        num_unique = compressed_df[col].nunique()
        num_total = len(compressed_df[col])
        if num_unique / num_total < 0.5:  # Less than 50% unique
            compressed_df[col] = compressed_df[col].astype('category')
    
    return compressed_df


# --- Backup & Restore Session State ---
def backup_session_state() -> Dict[str, Any]:
    """Create a backup of critical session state."""
    critical_keys = [
        "final_mapping",
        "claims_df",
        "layout_df",
        "lookup_df",
        "transformed_df",
        "validation_results",
        "user_preferences"
    ]
    
    backup = {}
    for key in critical_keys:
        if key in st.session_state:
            try:
                # Convert to JSON-serializable format
                value = st.session_state[key]
                if isinstance(value, pd.DataFrame):
                    backup[key] = value.to_dict()
                elif isinstance(value, dict):
                    backup[key] = value
                else:
                    backup[key] = str(value)
            except Exception:
                pass
    
    return backup


def restore_session_state(backup: Dict[str, Any]) -> None:
    """Restore session state from backup."""
    for key, value in backup.items():
        try:
            if isinstance(value, dict) and key.endswith("_df"):
                st.session_state[key] = pd.DataFrame(value)
            else:
                st.session_state[key] = value
        except Exception:
            pass

