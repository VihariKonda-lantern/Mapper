# --- mapping_enhancements.py ---
"""Mapping enhancement features."""
import streamlit as st
import pandas as pd
import json
import os
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import hashlib

st: Any = st
pd: Any = pd


def track_mapping_suggestions(field: str, suggestion: Dict[str, Any], 
                             mapping_history: List[Dict[str, Any]]) -> None:
    """Track AI mapping suggestions over time.
    
    Args:
        field: Field name
        suggestion: Suggestion details
        mapping_history: History list to append to
    """
    mapping_history.append({
        "field": field,
        "suggestion": suggestion,
        "timestamp": datetime.now().isoformat(),
        "type": "ai_suggestion"
    })


def get_mapping_confidence_score(mapping: Dict[str, Dict[str, Any]], 
                                 ai_suggestions: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
    """Calculate confidence scores for mappings.
    
    Args:
        mapping: Current mapping dictionary
        ai_suggestions: AI suggestions dictionary
        
    Returns:
        Dictionary mapping field names to confidence scores
    """
    confidence_scores = {}
    
    for field, mapping_info in mapping.items():
        if not mapping_info.get("value"):
            confidence_scores[field] = 0.0
            continue
        
        # Base confidence from AI suggestion if available
        if field in ai_suggestions:
            ai_confidence = ai_suggestions[field].get("score", 0) / 100.0
            confidence_scores[field] = ai_confidence
        else:
            # Manual mapping gets medium confidence
            confidence_scores[field] = 0.5
    
    return confidence_scores


def validate_mapping_before_processing(mapping: Dict[str, Dict[str, Any]], 
                                       layout_df: pd.DataFrame,
                                       claims_df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Pre-validate mappings before processing.
    
    Args:
        mapping: Mapping dictionary
        layout_df: Layout DataFrame
        claims_df: Claims DataFrame
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if claims_df is None or claims_df.empty:
        errors.append("Claims DataFrame is empty")
        return False, errors
    
    if layout_df is None or layout_df.empty:
        errors.append("Layout DataFrame is empty")
        return False, errors
    
    # Check if mapped columns exist in claims_df
    for field, mapping_info in mapping.items():
        source_col = mapping_info.get("value")
        if source_col and source_col not in claims_df.columns:
            errors.append(f"Field '{field}' mapped to non-existent column '{source_col}'")
    
    # Check required fields are mapped
    if "Usage" in layout_df.columns:
        required_fields = layout_df[layout_df["Usage"].astype(str).str.lower() == "required"]["Internal Field"].tolist()
        for req_field in required_fields:
            if req_field not in mapping or not mapping[req_field].get("value"):
                errors.append(f"Required field '{req_field}' is not mapped")
    
    return len(errors) == 0, errors


def create_mapping_rule(rule_name: str, rule_type: str, pattern: str, 
                       transformation: Optional[str] = None) -> Dict[str, Any]:
    """Create a custom mapping rule.
    
    Args:
        rule_name: Name of the rule
        rule_type: Type ('regex', 'contains', 'exact', 'transform')
        pattern: Pattern to match
        transformation: Optional transformation to apply
        
    Returns:
        Rule dictionary
    """
    return {
        "name": rule_name,
        "type": rule_type,
        "pattern": pattern,
        "transformation": transformation,
        "created_at": datetime.now().isoformat()
    }


def apply_mapping_rule(column: pd.Series, rule: Dict[str, Any]) -> pd.Series:
    """Apply a mapping rule to a column.
    
    Args:
        column: Pandas Series
        rule: Rule dictionary
        
    Returns:
        Transformed Series
    """
    import re
    
    rule_type = rule.get("type")
    pattern = rule.get("pattern")
    transformation = rule.get("transformation")
    
    if rule_type == "regex":
        if transformation:
            return column.astype(str).str.replace(pattern, transformation, regex=True)
        else:
            return column.astype(str).str.extract(pattern, expand=False)
    elif rule_type == "contains":
        return column.astype(str).str.contains(pattern, case=False, na=False)
    elif rule_type == "exact":
        return column.astype(str) == pattern
    elif rule_type == "transform" and transformation:
        # Apply transformation function (simplified - would need eval or function registry)
        return column.astype(str).apply(lambda x: transformation.format(value=x))
    else:
        return column


def get_mapping_version(mapping: Dict[str, Dict[str, Any]]) -> str:
    """Get version hash for a mapping.
    
    Args:
        mapping: Mapping dictionary
        
    Returns:
        Version hash string
    """
    mapping_str = json.dumps(mapping, sort_keys=True)
    return hashlib.md5(mapping_str.encode()).hexdigest()[:8]


def compare_mapping_versions(mapping1: Dict[str, Dict[str, Any]], 
                             mapping2: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Compare two mapping versions and show differences.
    
    Args:
        mapping1: First mapping
        mapping2: Second mapping
        
    Returns:
        Dictionary with differences
    """
    all_fields = set(mapping1.keys()) | set(mapping2.keys())
    
    differences = {
        "added": [],
        "removed": [],
        "changed": [],
        "unchanged": []
    }
    
    for field in all_fields:
        if field not in mapping1:
            differences["added"].append(field)
        elif field not in mapping2:
            differences["removed"].append(field)
        else:
            val1 = mapping1[field].get("value", "")
            val2 = mapping2[field].get("value", "")
            if val1 != val2:
                differences["changed"].append({
                    "field": field,
                    "old_value": val1,
                    "new_value": val2
                })
            else:
                differences["unchanged"].append(field)
    
    return differences


def export_mapping_template_for_sharing(mapping: Dict[str, Dict[str, Any]], 
                                        metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Export mapping template in shareable format.
    
    Args:
        mapping: Mapping dictionary
        metadata: Metadata (name, description, author, etc.)
        
    Returns:
        Shareable template dictionary
    """
    return {
        "version": "1.0",
        "metadata": {
            **metadata,
            "created_at": datetime.now().isoformat(),
            "mapping_version": get_mapping_version(mapping)
        },
        "mapping": mapping
    }


def import_mapping_template_from_shareable(template_data: Dict[str, Any]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    """Import mapping template from shareable format.
    
    Args:
        template_data: Shareable template dictionary
        
    Returns:
        Tuple of (mapping, metadata)
    """
    mapping = template_data.get("mapping", {})
    metadata = template_data.get("metadata", {})
    return mapping, metadata

