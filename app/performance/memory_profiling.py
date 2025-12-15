# --- memory_profiling.py ---
"""Memory profiling utilities for tracking memory usage during operations."""
import sys
from typing import Any, Optional, Dict, Callable
from contextlib import contextmanager
from functools import wraps
import time

try:
    import psutil  # type: ignore[import-not-found]
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage statistics.
    
    Returns:
        Dictionary with memory usage information
    """
    if not HAS_PSUTIL:
        return {
            "available": False,
            "message": "psutil not installed. Install with: pip install psutil"
        }
    
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        system_memory = psutil.virtual_memory()
        
        return {
            "available": True,
            "rss_mb": round(memory_info.rss / (1024 * 1024), 2),  # Resident Set Size
            "vms_mb": round(memory_info.vms / (1024 * 1024), 2),  # Virtual Memory Size
            "percent": process.memory_percent(),
            "system_total_gb": round(system_memory.total / (1024 * 1024 * 1024), 2),
            "system_available_gb": round(system_memory.available / (1024 * 1024 * 1024), 2),
            "system_percent": system_memory.percent
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }


@contextmanager
def track_memory_usage(operation_name: str = "Operation"):
    """Context manager to track memory usage during an operation.
    
    Args:
        operation_name: Name of the operation being tracked
    
    Yields:
        Dictionary with memory tracking information
    """
    if not HAS_PSUTIL:
        yield {"available": False}
        return
    
    try:
        process = psutil.Process()
        start_memory = process.memory_info()
        start_time = time.time()
        
        tracking_info = {
            "operation": operation_name,
            "start_memory_mb": round(start_memory.rss / (1024 * 1024), 2),
            "start_time": start_time
        }
        
        yield tracking_info
        
        end_memory = process.memory_info()
        end_time = time.time()
        
        memory_delta = end_memory.rss - start_memory.rss
        time_delta = end_time - start_time
        
        tracking_info.update({
            "end_memory_mb": round(end_memory.rss / (1024 * 1024), 2),
            "end_time": end_time,
            "memory_delta_mb": round(memory_delta / (1024 * 1024), 2),
            "duration_seconds": round(time_delta, 2),
            "memory_per_second_mb": round((memory_delta / (1024 * 1024)) / time_delta, 2) if time_delta > 0 else 0
        })
    except Exception as e:
        tracking_info["error"] = str(e)
        yield tracking_info


def profile_memory(func: Callable) -> Callable:
    """Decorator to profile memory usage of a function.
    
    Usage:
        @profile_memory
        def my_function():
            # function code
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        func_name = f"{func.__module__}.{func.__name__}"
        with track_memory_usage(func_name) as memory_info:
            result = func(*args, **kwargs)
            memory_info["result"] = result
            return result
    return wrapper


def format_memory_size(bytes_size: int) -> str:
    """Format memory size in human-readable format.
    
    Args:
        bytes_size: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB", "2.3 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def get_memory_summary() -> str:
    """Get a human-readable summary of current memory usage.
    
    Returns:
        Formatted string with memory information
    """
    usage = get_memory_usage()
    if not usage.get("available"):
        return usage.get("message", "Memory profiling not available")
    
    return (
        f"Memory: {usage['rss_mb']} MB RSS | "
        f"{usage['percent']:.1f}% of process | "
        f"System: {usage['system_available_gb']:.1f} GB available "
        f"({usage['system_percent']:.1f}% used)"
    )

