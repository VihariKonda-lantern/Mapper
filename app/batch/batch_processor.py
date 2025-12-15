# --- batch_processor.py ---
"""Batch processing utilities for multiple files."""
import streamlit as st
import pandas as pd
from typing import Any, List, Dict, Optional, Callable
from pathlib import Path
import zipfile
import io

# Import enhanced parallel processing
from performance.parallel_processing import ParallelProcessor, process_files_parallel_enhanced
from file.file_strategies import FileStrategyFactory
from file.file_handler import load_claims_file
from data.transformer import transform_claims_data
from core.exceptions import FileError

st: Any = st
pd: Any = pd


def process_multiple_claims_files(
    files: List[Any],
    layout_df: Any,
    final_mapping: Dict[str, Dict[str, Any]],
    lookup_df: Any = None,
    use_parallel: bool = True,
    max_workers: Optional[int] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> Dict[str, Any]:
    """Process multiple claims files with the same mapping.
    
    Args:
        files: List of uploaded file objects
        layout_df: Layout DataFrame
        final_mapping: Field mapping dictionary
        lookup_df: Optional lookup DataFrame
        use_parallel: Whether to use parallel processing
        max_workers: Maximum number of parallel workers
        progress_callback: Optional progress callback (completed, total)
        
    Returns:
        Dictionary with results for each file
    """
    def process_single_file(file_obj: Any) -> Dict[str, Any]:
        """Process a single file."""
        try:
            file_name = file_obj.name
            
            # Load file using FileStrategyFactory or load_claims_file
            try:
                claims_df, _ = load_claims_file(file_obj)
            except Exception:
                # Fallback to FileStrategyFactory
                claims_df = FileStrategyFactory.load_file(file_obj)
            
            # Transform using mapping
            transformed_df = transform_claims_data(
                claims_df,
                final_mapping,
                layout_df,
                lookup_df
            )
            
            return {
                "status": "processed",
                "rows": len(transformed_df),
                "errors": [],
                "file_name": file_name
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "file_name": file_obj.name if hasattr(file_obj, 'name') else "unknown"
            }
    
    # Process files
    if use_parallel and len(files) > 1:
        results_list = process_files_parallel_enhanced(
            files,
            process_single_file,
            max_workers=max_workers,
            progress_callback=progress_callback
        )
    else:
        results_list = [process_single_file(f) for f in files]
        if progress_callback:
            for i, _ in enumerate(results_list, 1):
                progress_callback(i, len(results_list))
    
    # Convert to dictionary
    results = {}
    for result in results_list:
        file_name = result.get("file_name", "unknown")
        results[file_name] = result
    
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

