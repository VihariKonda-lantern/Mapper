# --- advanced_validation.py ---
"""Advanced validation features."""
import streamlit as st
import pandas as pd
from typing import Any, Dict, List, Optional, Callable, Tuple
from datetime import datetime
import time

st: Any = st
pd: Any = pd


def validate_cross_field_relationship(df: pd.DataFrame, field1: str, field2: str,
                                     relationship: str, expected_value: Any = None) -> Dict[str, Any]:
    """Validate relationship between two fields.
    
    Args:
        df: DataFrame
        field1: First field name
        field2: Second field name
        relationship: Relationship type ('equals', 'greater_than', 'less_than', 'sum_equals', 'conditional')
        expected_value: Expected value for the relationship
        
    Returns:
        Validation result dictionary
    """
    if field1 not in df.columns or field2 not in df.columns:
        return {
            "status": "Fail",
            "message": f"Fields {field1} or {field2} not found",
            "fail_count": 0,
            "fail_pct": 0.0
        }
    
    valid_count = 0
    total_count = len(df)
    failures = []
    
    for idx, row in df.iterrows():
        val1 = row[field1]
        val2 = row[field2]
        
        is_valid = False
        
        if relationship == "equals":
            is_valid = val1 == val2
        elif relationship == "greater_than":
            is_valid = pd.notna(val1) and pd.notna(val2) and val1 > val2
        elif relationship == "less_than":
            is_valid = pd.notna(val1) and pd.notna(val2) and val1 < val2
        elif relationship == "sum_equals":
            if expected_value is not None:
                is_valid = pd.notna(val1) and pd.notna(val2) and (val1 + val2) == expected_value
        elif relationship == "conditional":
            # If field1 has value, field2 must also have value
            is_valid = pd.isna(val1) or pd.notna(val2)
        
        if is_valid:
            valid_count += 1
        else:
            failures.append(idx)
    
    fail_count = total_count - valid_count
    fail_pct = (fail_count / total_count * 100) if total_count > 0 else 0
    
    status = "Pass" if fail_count == 0 else ("Warning" if fail_pct < 5 else "Fail")
    
    return {
        "status": status,
        "message": f"Cross-field validation: {field1} {relationship} {field2}",
        "fail_count": fail_count,
        "fail_pct": round(fail_pct, 2),
        "total_count": total_count,
        "valid_count": valid_count,
        "failures": failures[:10]  # Limit to first 10
    }


def create_business_rule(rule_name: str, condition: str, action: str,
                        description: Optional[str] = None) -> Dict[str, Any]:
    """Create a business rule (if-then-else logic).
    
    Args:
        rule_name: Name of the rule
        condition: Condition expression (e.g., "field1 > 100 AND field2 == 'Active'")
        action: Action to take if condition is true (e.g., "REJECT", "WARN", "TRANSFORM")
        description: Optional description
        
    Returns:
        Rule dictionary
    """
    return {
        "name": rule_name,
        "condition": condition,
        "action": action,
        "description": description,
        "created_at": datetime.now().isoformat()
    }


def evaluate_business_rule(df: pd.DataFrame, rule: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate a business rule on a DataFrame.
    
    Args:
        df: DataFrame
        rule: Rule dictionary
        
    Returns:
        Evaluation result dictionary
    """
    condition = rule.get("condition", "")
    action = rule.get("action", "WARN")
    
    try:
        # Simple condition evaluation (would need more sophisticated parser in production)
        # For now, support basic comparisons
        matches = df.eval(condition, engine='python')
        match_count = matches.sum()
        total_count = len(df)
        match_pct = (match_count / total_count * 100) if total_count > 0 else 0
        
        status = "Pass"
        if action == "REJECT" and match_count > 0:
            status = "Fail"
        elif action == "WARN" and match_pct > 10:
            status = "Warning"
        
        return {
            "status": status,
            "message": f"Business rule '{rule['name']}': {match_count} rows match condition",
            "match_count": int(match_count),
            "match_pct": round(match_pct, 2),
            "total_count": total_count,
            "action": action
        }
    except Exception as e:
        return {
            "status": "Fail",
            "message": f"Error evaluating rule: {str(e)}",
            "match_count": 0,
            "match_pct": 0.0,
            "total_count": len(df),
            "action": action
        }


def get_validation_rule_templates() -> Dict[str, Dict[str, Any]]:
    """Get pre-built validation rule templates.
    
    Returns:
        Dictionary of rule templates
    """
    return {
        "required_fields_present": {
            "name": "Required Fields Present",
            "description": "Check that all required fields have values",
            "type": "completeness"
        },
        "date_range_valid": {
            "name": "Date Range Valid",
            "description": "Check that dates are within valid range",
            "type": "date_validation"
        },
        "numeric_range": {
            "name": "Numeric Range",
            "description": "Check that numeric values are within specified range",
            "type": "numeric_validation"
        },
        "format_validation": {
            "name": "Format Validation",
            "description": "Check that values match expected format (email, phone, etc.)",
            "type": "format_validation"
        },
        "referential_integrity": {
            "name": "Referential Integrity",
            "description": "Check that foreign key relationships are valid",
            "type": "relationship_validation"
        }
    }


def track_validation_performance(validation_name: str, execution_time: float,
                                record_count: int, result_count: int) -> None:
    """Track validation execution performance.
    
    Args:
        validation_name: Name of validation
        execution_time: Execution time in seconds
        record_count: Number of records validated
        result_count: Number of validation results
    """
    if "validation_performance" not in st.session_state:
        st.session_state.validation_performance = []
    
    performance_record = {
        "validation_name": validation_name,
        "execution_time": execution_time,
        "record_count": record_count,
        "result_count": result_count,
        "records_per_second": record_count / execution_time if execution_time > 0 else 0,
        "timestamp": datetime.now().isoformat()
    }
    
    st.session_state.validation_performance.append(performance_record)
    
    # Keep only last 100 records
    if len(st.session_state.validation_performance) > 100:
        st.session_state.validation_performance = st.session_state.validation_performance[-100:]


def get_validation_performance_stats() -> Dict[str, Any]:
    """Get validation performance statistics.
    
    Returns:
        Performance statistics dictionary
    """
    if "validation_performance" not in st.session_state or not st.session_state.validation_performance:
        return {
            "total_validations": 0,
            "avg_execution_time": 0,
            "avg_records_per_second": 0
        }
    
    perf_records = st.session_state.validation_performance
    
    avg_execution_time = sum(r["execution_time"] for r in perf_records) / len(perf_records)
    avg_records_per_second = sum(r["records_per_second"] for r in perf_records) / len(perf_records)
    
    return {
        "total_validations": len(perf_records),
        "avg_execution_time": round(avg_execution_time, 3),
        "avg_records_per_second": round(avg_records_per_second, 2),
        "total_records_validated": sum(r["record_count"] for r in perf_records)
    }


def incremental_validation(df: pd.DataFrame, previous_hash: str,
                          validation_func: Callable) -> Tuple[Dict[str, Any], str]:
    """Perform incremental validation on changed data only.
    
    Args:
        df: DataFrame
        previous_hash: Hash of previous data state
        validation_func: Validation function to run
        
    Returns:
        Tuple of (validation_results, new_hash)
    """
    import hashlib
    
    # Calculate current hash
    current_hash = hashlib.md5(str(df.shape).encode() + str(df.columns.tolist()).encode()).hexdigest()
    
    # If hash matches, return cached results
    if current_hash == previous_hash and "cached_validation_results" in st.session_state:
        return st.session_state.cached_validation_results, current_hash
    
    # Run validation
    start_time = time.time()
    results = validation_func(df)
    execution_time = time.time() - start_time
    
    # Cache results
    st.session_state.cached_validation_results = results
    st.session_state.cached_validation_hash = current_hash
    
    return results, current_hash


def schedule_validation(validation_id: str, schedule: str,
                       validation_func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Schedule automatic validation (simplified - would need scheduler in production).
    
    Args:
        validation_id: Unique validation identifier
        schedule: Schedule string (e.g., "daily", "weekly", "on_file_upload")
        validation_func: Validation function
        *args, **kwargs: Arguments for validation function
        
    Returns:
        Schedule dictionary
    """
    schedule_obj = {
        "id": validation_id,
        "schedule": schedule,
        "validation_func": validation_func.__name__ if hasattr(validation_func, '__name__') else str(validation_func),
        "args": args,
        "kwargs": kwargs,
        "created_at": datetime.now().isoformat(),
        "last_run": None,
        "next_run": None,
        "enabled": True
    }
    
    if "validation_schedules" not in st.session_state:
        st.session_state.validation_schedules = []
    
    # Remove existing schedule with same ID
    st.session_state.validation_schedules = [
        s for s in st.session_state.validation_schedules if s["id"] != validation_id
    ]
    
    st.session_state.validation_schedules.append(schedule_obj)
    return schedule_obj

