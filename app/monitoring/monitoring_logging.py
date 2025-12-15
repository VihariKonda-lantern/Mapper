# --- monitoring_logging.py ---
"""Monitoring and logging features."""
import streamlit as st
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import traceback

st: Any = st


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

