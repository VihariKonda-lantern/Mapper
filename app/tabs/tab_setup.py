# --- tab_setup.py ---
"""Setup tab handler - file upload and preview."""
import streamlit as st
from typing import Any, List, Dict, Callable, cast
from ui.upload_ui import (
    render_upload_and_claims_preview,
    render_lookup_summary_section,
)
from utils.utils import render_claims_file_summary
from file.layout_loader import render_layout_summary_section
from ui.design_system import inject_unified_design_system
from monitoring.monitoring_logging import track_feature_usage
from ui.user_experience import add_recent_file
from core.state_manager import SessionStateManager

st: Any = st


def render_setup_tab() -> None:
    """Render the Setup tab content."""
    render_upload_and_claims_preview()
    
    # Log file upload events if files were just loaded
    layout_df = SessionStateManager.get_layout_df()
    if layout_df is not None:
        layout_file_name = SessionStateManager.get("layout_file_obj")
        if layout_file_name and hasattr(layout_file_name, "name"):
            last_logged_layout = SessionStateManager.get("last_logged_layout_file")
            if last_logged_layout != layout_file_name.name:
                try:
                    from monitoring.audit_logger import log_event
                    log_event("file_upload", f"Layout file loaded: {layout_file_name.name}")
                    track_feature_usage("file_upload", "layout_file_uploaded", {"file": layout_file_name.name})
                except (NameError, ImportError, AttributeError):
                    pass
                SessionStateManager.set("last_logged_layout_file", layout_file_name.name)
                add_recent_file(layout_file_name.name, "layout", {})
    
    claims_df = SessionStateManager.get_claims_df()
    if claims_df is not None:
        claims_file_name = SessionStateManager.get("claims_file_obj")
        if claims_file_name and hasattr(claims_file_name, "name"):
            last_logged_claims = SessionStateManager.get("last_logged_claims_file")
            if last_logged_claims != claims_file_name.name:
                row_count = len(claims_df) if claims_df is not None else 0
                col_count = len(claims_df.columns) if claims_df is not None else 0
                try:
                    from monitoring.audit_logger import log_event
                    log_event("file_upload", f"Claims file loaded: {claims_file_name.name} ({row_count:,} rows, {col_count} columns)")
                    track_feature_usage("file_upload", "claims_file_uploaded", {"file": claims_file_name.name, "rows": row_count})
                except (NameError, ImportError, AttributeError):
                    pass
                SessionStateManager.set("last_logged_claims_file", claims_file_name.name)
                add_recent_file(claims_file_name.name, "claims", {"rows": row_count, "columns": col_count})
    
    if SessionStateManager.has("msk_codes") or SessionStateManager.has("bar_codes"):
        lookup_file_name = SessionStateManager.get("lookup_file_obj")
        if lookup_file_name and hasattr(lookup_file_name, "name"):
            last_logged_lookup = SessionStateManager.get("last_logged_lookup_file")
            if last_logged_lookup != lookup_file_name.name:
                msk_count = len(SessionStateManager.get("msk_codes", set()))
                bar_count = len(SessionStateManager.get("bar_codes", set()))
                try:
                    from monitoring.audit_logger import log_event
                    log_event("file_upload", f"Lookup file loaded: {lookup_file_name.name} (MSK: {msk_count}, BAR: {bar_count})")
                    track_feature_usage("file_upload", "lookup_file_uploaded", {"file": lookup_file_name.name})
                except (NameError, ImportError, AttributeError):
                    pass
                SessionStateManager.set("last_logged_lookup_file", lookup_file_name.name)
                add_recent_file(lookup_file_name.name, "lookup", {"msk": msk_count, "bar": bar_count})
    
    # Unified design system is already injected in main.py
    
    # Dynamic summary cards based on upload order
    upload_order = cast(List[str], SessionStateManager.get("upload_order", []))
    summary_functions: List[Callable[[], None]] = []
    summary_map: Dict[str, Callable[[], None]] = {
        "layout": render_layout_summary_section,
        "lookup": render_lookup_summary_section,
        "claims": render_claims_file_summary
    }
    
    # Add summaries in upload order if available
    for file_type in upload_order:
        if file_type in summary_map:
            if file_type == "layout" and SessionStateManager.has("layout_file_obj"):
                summary_functions.append(summary_map[file_type])
            elif file_type == "lookup" and SessionStateManager.has("lookup_file_obj"):
                summary_functions.append(summary_map[file_type])
            elif file_type == "claims" and SessionStateManager.has("claims_file_obj"):
                summary_functions.append(summary_map[file_type])
    
    # Fallback for files not in upload_order
    if SessionStateManager.has("layout_file_obj") and "layout" not in upload_order:
        if "layout" not in [f.__name__ if hasattr(f, "__name__") else "" for f in summary_functions]:
            summary_functions.append(summary_map["layout"])
    if SessionStateManager.has("lookup_file_obj") and "lookup" not in upload_order:
        if "lookup" not in [f.__name__ if hasattr(f, "__name__") else "" for f in summary_functions]:
            summary_functions.append(summary_map["lookup"])
    if SessionStateManager.has("claims_file_obj") and "claims" not in upload_order:
        if "claims" not in [f.__name__ if hasattr(f, "__name__") else "" for f in summary_functions]:
            summary_functions.append(summary_map["claims"])
    
    # If we have files but no summaries, add them
    has_uploaded_files = (
        SessionStateManager.has("layout_file_obj") or 
        SessionStateManager.has("lookup_file_obj") or 
        SessionStateManager.has("claims_file_obj")
    )
    if not summary_functions and has_uploaded_files:
        if SessionStateManager.has("layout_file_obj"):
            summary_functions.append(summary_map["layout"])
        if SessionStateManager.has("lookup_file_obj"):
            summary_functions.append(summary_map["lookup"])
        if SessionStateManager.has("claims_file_obj"):
            summary_functions.append(summary_map["claims"])
    
    if summary_functions:
        st.markdown('<div class="summary-cards-wrapper">', unsafe_allow_html=True)
        num_summaries = len(summary_functions)
        if num_summaries == 1:
            cols = st.columns(1, gap="large")
        elif num_summaries == 2:
            cols = st.columns(2, gap="large")
        else:
            cols = st.columns(3, gap="large")
        
        for i, summary_func in enumerate(summary_functions):
            with cols[i]:
                summary_func()
        st.markdown('</div>', unsafe_allow_html=True)

