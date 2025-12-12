# --- batch_processor.py ---
"""Batch processing utilities for multiple files."""
import streamlit as st
import pandas as pd
from typing import Any, List, Dict, Optional
from pathlib import Path
import zipfile
import io

st: Any = st
pd: Any = pd


def process_multiple_claims_files(
    files: List[Any],
    layout_df: Any,
    final_mapping: Dict[str, Dict[str, Any]],
    lookup_df: Any = None
) -> Dict[str, Any]:
    """Process multiple claims files with the same mapping.
    
    Args:
        files: List of uploaded file objects
        layout_df: Layout DataFrame
        final_mapping: Field mapping dictionary
        lookup_df: Optional lookup DataFrame
        
    Returns:
        Dictionary with results for each file
    """
    results = {}
    
    for file in files:
        try:
            file_name = file.name
            file_bytes = file.getvalue()
            
            # Process file (simplified - would need full file_handler integration)
            # This is a placeholder for batch processing logic
            results[file_name] = {
                "status": "processed",
                "rows": 0,  # Would be actual row count
                "errors": []
            }
        except Exception as e:
            results[file.name] = {
                "status": "error",
                "error": str(e)
            }
    
    return results


def compare_mappings(mapping1: Dict[str, Dict[str, Any]], mapping2: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Compare two mapping configurations and return differences.
    
    Args:
        mapping1: First mapping
        mapping2: Second mapping
        
    Returns:
        Dictionary with comparison results
    """
    all_fields = set(mapping1.keys()) | set(mapping2.keys())
    
    differences = {
        "added": [],
        "removed": [],
        "changed": [],
        "unchanged": []
    }
    
    for field in all_fields:
        val1 = mapping1.get(field, {}).get("value")
        val2 = mapping2.get(field, {}).get("value")
        
        if field not in mapping1:
            differences["added"].append(field)
        elif field not in mapping2:
            differences["removed"].append(field)
        elif val1 != val2:
            differences["changed"].append({
                "field": field,
                "old": val1,
                "new": val2
            })
        else:
            differences["unchanged"].append(field)
    
    return differences


def generate_mapping_diff_view(differences: Dict[str, Any]) -> str:
    """Generate a visual diff view of mapping differences.
    
    Args:
        differences: Output from compare_mappings
        
    Returns:
        HTML string for diff view
    """
    html_parts = []
    
    if differences["added"]:
        html_parts.append(f"<h4>➕ Added Fields ({len(differences['added'])})</h4>")
        html_parts.append("<ul>")
        for field in differences["added"]:
            html_parts.append(f"<li style='color: green;'>{field}</li>")
        html_parts.append("</ul>")
    
    if differences["removed"]:
        html_parts.append(f"<h4>➖ Removed Fields ({len(differences['removed'])})</h4>")
        html_parts.append("<ul>")
        for field in differences["removed"]:
            html_parts.append(f"<li style='color: red;'>{field}</li>")
        html_parts.append("</ul>")
    
    if differences["changed"]:
        html_parts.append(f"<h4>🔄 Changed Mappings ({len(differences['changed'])})</h4>")
        html_parts.append("<table style='width: 100%; border-collapse: collapse;'>")
        html_parts.append("<tr><th>Field</th><th>Old Mapping</th><th>New Mapping</th></tr>")
        for change in differences["changed"]:
            html_parts.append(f"""
                <tr>
                    <td>{change['field']}</td>
                    <td style='color: red;'>{change['old'] or '(unmapped)'}</td>
                    <td style='color: green;'>{change['new'] or '(unmapped)'}</td>
                </tr>
            """)
        html_parts.append("</table>")
    
    if differences["unchanged"]:
        html_parts.append(f"<h4>✓ Unchanged ({len(differences['unchanged'])})</h4>")
        html_parts.append(f"<p>{', '.join(differences['unchanged'][:10])}")
        if len(differences["unchanged"]) > 10:
            html_parts.append(f" and {len(differences['unchanged']) - 10} more...</p>")
        else:
            html_parts.append("</p>")
    
    return "".join(html_parts)

