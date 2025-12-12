# --- main.py ---
"""
pyright: reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownAttributeType=false
"""
import streamlit as st  # type: ignore[import-not-found]
import pandas as pd  # type: ignore[import-not-found]
from typing import Any, List, Dict, Callable, cast
from datetime import datetime

st: Any = st  # type: ignore[assignment]
pd: Any = pd  # type: ignore[assignment]
import zipfile
import io
import hashlib
import os
import json
# Removed unused matplotlib import

# --- App Modules ---
from layout_loader import (
    get_required_fields,
    render_layout_summary_section
)
from mapping_engine import get_enhanced_automap
from utils import render_claims_file_summary
from transformer import transform_claims_data
from validation_engine import (
    run_validations,
    dynamic_run_validations,
)
from anonymizer import anonymize_claims_data

# --- UI Modules ---
from ui_styling import inject_summary_card_css, inject_ux_javascript  # type: ignore[import-untyped]
from ui_components import render_progress_bar, render_title, _notify, show_progress_with_status, confirm_action  # type: ignore[import-untyped]
from upload_ui import (  # type: ignore[import-untyped]
    render_upload_and_claims_preview,
    render_lookup_summary_section,
)
from mapping_ui import (  # type: ignore[import-untyped]
    render_field_mapping_tab,
    generate_mapping_table
)
from output_generator import generate_all_outputs  # type: ignore[import-untyped]
from session_state import initialize_undo_redo, save_to_history, undo_mapping, redo_mapping  # type: ignore[import-untyped]
from cache_utils import load_layout_cached, load_lookups_cached  # type: ignore[import-untyped]
from file_handler import (  # type: ignore[import-untyped]
    is_fixed_width,
    infer_fixed_width_positions,
    parse_header_specification_file,
    detect_delimiter,
    has_header,
    read_claims_with_header_option,
)
from upload_handlers import capture_claims_file_metadata  # type: ignore[import-untyped]
from advanced_features import (  # type: ignore[import-untyped]
    init_dark_mode,
    toggle_dark_mode,
    get_dark_mode_css,
    inject_keyboard_shortcuts,
    save_mapping_template,
    load_mapping_template,
    list_saved_templates,
    export_validation_results_csv,
    export_validation_results_excel,
    bulk_map_similar_fields,
)
from performance_utils import paginate_dataframe, get_data_hash  # type: ignore[import-untyped]
from batch_processor import compare_mappings, generate_mapping_diff_view  # type: ignore[import-untyped]
from validation_builder import (  # type: ignore[import-untyped]
    CustomValidationRule,
    save_custom_rule,
    load_custom_rules,
    run_custom_validations,
)

# --- Audit Log Helper Function (defined early to ensure availability) ---
def log_event(event_type: str, message: str) -> None:
    """Log an event to the in-memory audit log.

    Args:
        event_type: Type of event (e.g., "file_upload", "mapping", "validation", "output")
        message: Descriptive message about the event
    """
    try:
        audit_log = st.session_state.setdefault("audit_log", [])
        audit_log.append({
            "event_type": event_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last 100 events to prevent memory bloat
        if len(audit_log) > 100:
            audit_log[:] = audit_log[-100:]
    except Exception:
        # Silently fail if logging is not available
        pass

# --- Streamlit Setup ---
st.set_page_config(page_title="Claims Mapper and Validator", layout="wide")

# Initialize dark mode
init_dark_mode()

# Inject dark mode CSS
st.markdown(get_dark_mode_css(), unsafe_allow_html=True)

# Inject keyboard shortcuts
inject_keyboard_shortcuts()

# --- Removed: Functions moved to ui_styling.py ---
# inject_summary_card_css() - now in ui_styling.py
# inject_ux_javascript() - now in ui_styling.py

# --- Removed: Functions moved to ui_components.py ---
# _notify() - now in ui_components.py
# render_tooltip() - now in ui_components.py
# render_status_indicator() - now in ui_components.py
# render_progress_bar() - now in ui_components.py
# render_title() - now in ui_components.py

# --- Removed: Functions moved to session_state.py ---
# initialize_undo_redo() - now in session_state.py
# save_to_history() - now in session_state.py
# undo_mapping() - now in session_state.py
# redo_mapping() - now in session_state.py

# --- Removed: Functions moved to cache_utils.py ---
# load_layout_cached() - now in cache_utils.py
# load_lookups_cached() - now in cache_utils.py

# --- Removed: Functions moved to upload_ui.py ---
# render_lookup_summary_section() - now in upload_ui.py
# render_upload_and_claims_preview() - now in upload_ui.py
# render_claims_file_deep_dive() - now in upload_ui.py

# --- Removed: Functions moved to mapping_ui.py ---
# dual_input_field() - now in mapping_ui.py
# generate_mapping_table() - now in mapping_ui.py
# calculate_mapping_progress() - now in mapping_ui.py
# render_field_mapping_tab() - now in mapping_ui.py

# --- Removed: Functions moved to output_generator.py ---
# save_mapping_template() - now in output_generator.py
# load_mapping_template() - now in output_generator.py
# generate_all_outputs() - now in output_generator.py

# --- App Layout ---
# Inject UX JavaScript and CSS
inject_ux_javascript()

# --- Sticky Top Bar with Title and Breadcrumb ---
st.markdown("""
    <div style='
        position: sticky;
        top: 0;
        z-index: 1000;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        margin: -1rem -1rem 1rem -1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    '>
        <div style='display: flex; justify-content: space-between; align-items: center; max-width: 1400px; margin: 0 auto;'>
            <div style='font-size: 18px; font-weight: 600;'>Claims Mapper & Validator</div>
            <div style='font-size: 13px; opacity: 0.95;'>
                <span>1) Setup</span> <span style='margin: 0 6px;'>→</span>
                <span>2) Mapping</span> <span style='margin: 0 6px;'>→</span>
                <span>3) Preview & Validate</span> <span style='margin: 0 6px;'>→</span>
                <span>4) Outputs</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Main Content Container with Optimized Layout ---
st.markdown("""
    <style>
        /* Maximize horizontal space and reduce margins */
        .main .block-container {
            padding-top: 0.5rem;
            padding-bottom: 1rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1400px;
        }
        
        /* Reduce excessive vertical spacing */
        h1, h2, h3, h4 {
            margin-top: 0.75rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Tighter spacing for tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        /* Reduce spacing for dividers */
        hr {
            margin: 0.75rem 0 !important;
        }
        
        /* Tighter spacing between elements */
        .element-container {
            margin-bottom: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar: Activity Log Panel ---
# --- Sidebar with Settings ---
with st.sidebar:
    # Dark Mode Toggle
    dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.get("dark_mode", False), key="dark_mode_toggle")
    if dark_mode != st.session_state.get("dark_mode", False):
        toggle_dark_mode()
        st.rerun()
    
    st.divider()
    st.markdown("### 📋 Activity Log")
    audit_log = st.session_state.setdefault("audit_log", [])
    
    if audit_log:
        # Show last 10 events in reverse chronological order
        recent_events = audit_log[-10:][::-1]
        for event in recent_events:
            event_type = event.get("event_type", "unknown")
            message = event.get("message", "")
            timestamp = event.get("timestamp", "")
            
            # Format timestamp for display
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%H:%M:%S")
            except Exception:
                time_str = timestamp[:8] if len(timestamp) >= 8 else timestamp
            
            # Color code by event type
            color_map = {
                "file_upload": "#4CAF50",
                "mapping": "#2196F3",
                "validation": "#FF9800",
                "output": "#9C27B0"
            }
            color = color_map.get(event_type, "#757575")
            
            st.markdown(f"""
                <div style="
                    background-color: #f5f5f5;
                    padding: 0.5rem;
                    border-radius: 4px;
                    margin-bottom: 0.5rem;
                    border-left: 3px solid {color};
                    font-size: 0.85rem;
                ">
                    <div style="color: {color}; font-weight: 600; font-size: 0.75rem;">{event_type.upper()}</div>
                    <div style="color: #333; margin-top: 0.25rem;">{message}</div>
                    <div style="color: #999; font-size: 0.7rem; margin-top: 0.25rem;">{time_str}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No activity yet. Events will appear here as you use the app.")
    
    # Clear log button
    if st.button("Clear Log", key="clear_audit_log", use_container_width=True):
        st.session_state.audit_log = []
        st.rerun()

# Wrap tabs in container for better layout control
main_container = st.container()
with main_container:
    tab1, tab2, tab3, tab4 = st.tabs(["Setup", "Field Mapping", "Preview & Validate", "Downloads Tab"])

with tab1:
    render_upload_and_claims_preview()
    
    # Log file upload events if files were just loaded
    if "layout_df" in st.session_state and st.session_state.get("layout_df") is not None:
        layout_file_name = st.session_state.get("layout_file_obj")
        if layout_file_name and hasattr(layout_file_name, "name"):
            # Check if we should log (only once per file)
            last_logged_layout = st.session_state.get("last_logged_layout_file")
            if last_logged_layout != layout_file_name.name:
                try:
                    log_event("file_upload", f"Layout file loaded: {layout_file_name.name}")
                except NameError:
                    pass  # Function not available yet
                st.session_state.last_logged_layout_file = layout_file_name.name
    
    if "claims_df" in st.session_state and st.session_state.get("claims_df") is not None:
        claims_file_name = st.session_state.get("claims_file_obj")
        if claims_file_name and hasattr(claims_file_name, "name"):
            # Check if we should log (only once per file)
            last_logged_claims = st.session_state.get("last_logged_claims_file")
            if last_logged_claims != claims_file_name.name:
                claims_df = st.session_state.get("claims_df")
                row_count = len(claims_df) if claims_df is not None else 0
                col_count = len(claims_df.columns) if claims_df is not None else 0
                try:
                    log_event("file_upload", f"Claims file loaded: {claims_file_name.name} ({row_count:,} rows, {col_count} columns)")
                except NameError:
                    pass  # Function not available yet
                st.session_state.last_logged_claims_file = claims_file_name.name
    
    if "msk_codes" in st.session_state or "bar_codes" in st.session_state:
        lookup_file_name = st.session_state.get("lookup_file_obj")
        if lookup_file_name and hasattr(lookup_file_name, "name"):
            # Check if we should log (only once per file)
            last_logged_lookup = st.session_state.get("last_logged_lookup_file")
            if last_logged_lookup != lookup_file_name.name:
                msk_count = len(st.session_state.get("msk_codes", set()))
                bar_count = len(st.session_state.get("bar_codes", set()))
                try:
                    log_event("file_upload", f"Lookup file loaded: {lookup_file_name.name} (MSK: {msk_count}, BAR: {bar_count})")
                except NameError:
                    pass  # Function not available yet
                st.session_state.last_logged_lookup_file = lookup_file_name.name
    
    # Inject CSS for modern cards
    inject_summary_card_css()
    
    # Dynamic summary cards based on upload order
    upload_order = cast(List[str], st.session_state.get("upload_order", []))
    
    # Build list of summaries to render based on upload order
    summary_functions_tab1: List[Callable[[], None]] = []
    summary_map_tab1: Dict[str, Callable[[], None]] = {
        "layout": render_layout_summary_section,
        "lookup": render_lookup_summary_section,
        "claims": render_claims_file_summary
    }
    
    # Add summaries in upload order if available
    for file_type in upload_order:
        if file_type in summary_map_tab1:
            # Verify file is still uploaded
            if file_type == "layout" and "layout_file_obj" in st.session_state:
                summary_functions_tab1.append(summary_map_tab1[file_type])
            elif file_type == "lookup" and "lookup_file_obj" in st.session_state:
                summary_functions_tab1.append(summary_map_tab1[file_type])
            elif file_type == "claims" and "claims_file_obj" in st.session_state:
                summary_functions_tab1.append(summary_map_tab1[file_type])
    
    # Also add summaries for files that exist but might not be in upload_order
    # (fallback to ensure stats are always shown when files are uploaded)
    if "layout_file_obj" in st.session_state and "layout" not in upload_order:
        if "layout" not in [f.__name__ if hasattr(f, "__name__") else "" for f in summary_functions_tab1]:
            summary_functions_tab1.append(summary_map_tab1["layout"])
    if "lookup_file_obj" in st.session_state and "lookup" not in upload_order:
        if "lookup" not in [f.__name__ if hasattr(f, "__name__") else "" for f in summary_functions_tab1]:
            summary_functions_tab1.append(summary_map_tab1["lookup"])
    if "claims_file_obj" in st.session_state and "claims" not in upload_order:
        if "claims" not in [f.__name__ if hasattr(f, "__name__") else "" for f in summary_functions_tab1]:
            summary_functions_tab1.append(summary_map_tab1["claims"])
    
    # Render summaries dynamically - always show if files are uploaded
    # Check if we have any uploaded files
    has_uploaded_files = (
        "layout_file_obj" in st.session_state or 
        "lookup_file_obj" in st.session_state or 
        "claims_file_obj" in st.session_state
    )
    
    # If we have files but no summaries in list, add them
    if not summary_functions_tab1 and has_uploaded_files:
        if "layout_file_obj" in st.session_state:
            summary_functions_tab1.append(summary_map_tab1["layout"])
        if "lookup_file_obj" in st.session_state:
            summary_functions_tab1.append(summary_map_tab1["lookup"])
        if "claims_file_obj" in st.session_state:
            summary_functions_tab1.append(summary_map_tab1["claims"])
    
    if summary_functions_tab1:
        st.markdown('<div class="summary-cards-wrapper">', unsafe_allow_html=True)
        num_summaries = len(summary_functions_tab1)
        
        # Create columns based on number of summaries (1, 2, or 3)
        if num_summaries == 1:
            cols = st.columns(1, gap="large")
        elif num_summaries == 2:
            cols = st.columns(2, gap="large")
        else:
            cols = st.columns(3, gap="large")
        
        # Render each summary in its column
        for i, summary_func in enumerate(summary_functions_tab1):
            with cols[i]:
                summary_func()
        
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    layout_df = st.session_state.get("layout_df")
    claims_df = st.session_state.get("claims_df")
    final_mapping = st.session_state.get("final_mapping", {})

    if layout_df is None or claims_df is None:
        st.info("Upload both layout and claims files to begin mapping.")
        st.stop()
    
    # --- Sticky Mapping Progress Bar ---
    # Guard layout_df and string operations
    required_fields = layout_df[layout_df["Usage"].astype(str).str.lower() == "required"]["Internal Field"].tolist()  # type: ignore[no-untyped-call]
    total_required = len(required_fields) if required_fields else 0
    mapped_required = [f for f in required_fields if f in final_mapping and final_mapping[f].get("value")]
    mapped_count = len(mapped_required)
    percent_complete = int((mapped_count / total_required) * 100) if total_required > 0 else 0

    progress_html = render_progress_bar(percent_complete, f"{mapped_count} / {total_required} fields mapped ({percent_complete}%)")
    st.markdown(
        f'<div style="position: sticky; top: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; z-index: 999; padding: 1rem 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><b style="font-size: 1.1rem;">📌 Required Field Mapping Progress</b>{progress_html}</div>',
        unsafe_allow_html=True
    )

    # --- UX Tools (Collapsible Container) ---
    with st.expander("⚙️ Tools & Actions", expanded=False):
        # Search field at the top of the container
        search_query = st.text_input("🔍 Search Fields", placeholder="Type to filter fields... (Ctrl+F)", key="field_search_tools")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
                st.markdown("**History**")
                # Initialize undo/redo
                initialize_undo_redo()
                final_mapping = st.session_state.get("final_mapping", {})
                
                # Initialize history with current state if empty
                if len(st.session_state.mapping_history) == 0:
                    if final_mapping:
                        save_to_history(final_mapping)
                    else:
                        # Save empty state as initial state
                        save_to_history({})
                
                # Check if undo/redo is possible
                can_undo = st.session_state.history_index > 0
                can_redo = st.session_state.history_index < len(st.session_state.mapping_history) - 1
                
                if st.button("↶ Undo", key="undo_btn", use_container_width=True, disabled=not can_undo, help="Undo last mapping change (Ctrl+Z)"):
                    undone = undo_mapping()
                    if undone is not None:
                        import copy
                        st.session_state.final_mapping = copy.deepcopy(undone)
                        # Clear auto_mapping to force refresh
                        if "auto_mapping" in st.session_state:
                            del st.session_state.auto_mapping
                        st.rerun()
                
                if st.button("↷ Redo", key="redo_btn", use_container_width=True, disabled=not can_redo, help="Redo last undone change (Ctrl+Y)"):
                    redone = redo_mapping()
                    if redone is not None:
                        import copy
                        st.session_state.final_mapping = copy.deepcopy(redone)
                        # Clear auto_mapping to force refresh
                        if "auto_mapping" in st.session_state:
                            del st.session_state.auto_mapping
                        st.rerun()
            
        with col2:
            st.markdown("**Bulk Actions**")
            ai_suggestions = st.session_state.get("auto_mapping", {})
            final_mapping = st.session_state.get("final_mapping", {})
            if st.button("✅ Accept All AI (≥80%)", key="bulk_accept_ai", use_container_width=True):
                accepted = 0
                for field, info in ai_suggestions.items():
                    score = info.get("score", 0)
                    if score >= 80 and (field not in final_mapping or not final_mapping[field].get("value")):
                        final_mapping[field] = {"mode": "auto", "value": info["value"]}
                        accepted += 1
                if accepted > 0:
                    st.session_state.final_mapping = final_mapping
                    save_to_history(final_mapping)
                    st.success(f"Accepted {accepted} AI suggestions!")
                    st.rerun()
            if st.button("🔄 Clear All", key="bulk_clear", use_container_width=True):
                if confirm_action("⚠️ Are you sure you want to clear all mappings? This action cannot be undone.", "clear_all_mappings"):
                    st.session_state.final_mapping = {}
                    save_to_history({})
                    if "confirm_clear_all_mappings" in st.session_state:
                        del st.session_state["confirm_clear_all_mappings"]
                    st.success("All mappings cleared!")
                    log_event("mapping", "Cleared all mappings")
                    st.rerun()
        
        with col3:
            st.markdown("**Utilities**")
            if st.button("📋 Copy Mapping", key="bulk_copy", use_container_width=True):
                import json
                mapping_str = json.dumps(final_mapping, indent=2)
                st.code(mapping_str, language="json")
                st.info("Right-click and copy the JSON above")
            
            # Export mapping as JSON file
            if final_mapping:
                mapping_json = json.dumps(final_mapping, indent=2).encode('utf-8')
                st.download_button(
                    label="💾 Export Mapping (JSON)",
                    data=mapping_json,
                    file_name="mapping_template.json",
                    mime="application/json",
                    key="export_mapping_json",
                    use_container_width=True,
                    help="Download current mapping as JSON template"
                )
            
            # Save/Load Mapping Templates
            st.markdown("**Mapping Templates**")
            template_col1, template_col2 = st.columns(2)
            with template_col1:
                if st.button("💾 Save Template", key="save_template", use_container_width=True):
                    if final_mapping:
                        filename = save_mapping_template(final_mapping)
                        st.success(f"Template saved: {os.path.basename(filename)}")
                        log_event("template", f"Saved mapping template: {os.path.basename(filename)}")
                    else:
                        st.warning("No mapping to save")
                
                with template_col2:
                    saved_templates = list_saved_templates()
                    if saved_templates:
                        template_names = [os.path.basename(t) for t in saved_templates]
                        selected_template = st.selectbox(
                            "Load Template",
                            options=[""] + template_names,
                            key="load_template_select",
                            help="Select a saved template to load"
                        )
                        if selected_template and selected_template != "":
                            template_path = os.path.join("templates", selected_template)
                            loaded_mapping = load_mapping_template(template_path)
                            if loaded_mapping:
                                st.session_state.final_mapping = loaded_mapping
                                save_to_history(loaded_mapping)
                                st.success(f"Template loaded: {selected_template}")
                                log_event("template", f"Loaded mapping template: {selected_template}")
                                st.rerun()
                    else:
                        st.info("No saved templates")

    # --- Main Mapping Section ---
    st.markdown("#### Manual Field Mapping")
    # Gate heavy mapping updates behind a form submit to avoid recomputation on every rerun
    with st.form("mapping_form"):
        render_field_mapping_tab()
        apply_mappings = st.form_submit_button("Apply Mappings")
        if apply_mappings:
            st.session_state["mappings_ready"] = True
            # Save to history when form is submitted
            final_mapping = st.session_state.get("final_mapping", {})
            if final_mapping:
                save_to_history(final_mapping)
                # Only log manual mappings (exclude AI auto-mapped fields)
                manual_mapped_count = len([f for f in final_mapping.keys() 
                                         if final_mapping[f].get("value") and final_mapping[f].get("mode") == "manual"])
                if manual_mapped_count > 0:
                    try:
                        log_event("mapping", f"Manual field mappings committed via form ({manual_mapped_count} fields mapped)")
                    except NameError:
                        pass

    st.divider()

    # --- Review & Adjust Mappings Section ---
    if st.session_state.get("mappings_ready") and final_mapping:
        st.markdown("#### Review & Adjust Mappings")
        st.caption("Review and edit your mappings in the table below. Click 'Apply Edited Mappings' to save changes.")
        
        # Get all internal fields from layout
        all_internal_fields = layout_df["Internal Field"].dropna().unique().tolist()  # type: ignore[no-untyped-call]
        
        # Get required fields to mark which are required
        required_fields_df = get_required_fields(layout_df)
        required_fields_list = required_fields_df["Internal Field"].tolist() if isinstance(required_fields_df, pd.DataFrame) else []
        required_fields_set = set(required_fields_list)
        
        # Get available source columns for validation
        available_source_columns = claims_df.columns.tolist()
        
        # Build review table data
        review_data: List[Dict[str, Any]] = []
        for field in all_internal_fields:
            mapping_info = final_mapping.get(field, {})
            source_col = mapping_info.get("value", "")
            is_required = "Yes" if field in required_fields_set else "No"
            
            review_data.append({
                "Internal Field": field,
                "Source Column": source_col,
                "Is Required": is_required
            })
        
        # Create DataFrame for data editor
        review_df = pd.DataFrame(review_data)
        
        # Sort: Required fields first, then alphabetically by Internal Field
        review_df["_sort_key"] = review_df["Is Required"].apply(lambda x: 0 if x == "Yes" else 1)  # type: ignore[no-untyped-call]
        review_df = review_df.sort_values(by=["_sort_key", "Internal Field"]).drop(columns=["_sort_key"])  # type: ignore[no-untyped-call]
        
        # Configure column editing - only Source Column should be editable
        column_config = {
            "Internal Field": st.column_config.TextColumn(
                "Internal Field",
                disabled=True,
                help="Internal field name (cannot be edited)"
            ),
            "Source Column": st.column_config.TextColumn(
                "Source Column",
                help="Type or edit the source column name. Available columns: " + ", ".join(available_source_columns[:10]) + ("..." if len(available_source_columns) > 10 else ""),
                required=False
            ),
            "Is Required": st.column_config.TextColumn(
                "Is Required",
                disabled=True,
                help="Whether this field is mandatory"
            )
        }
        
        # Display data editor
        edited_df = st.data_editor(
            review_df,
            column_config=column_config,
            use_container_width=True,
            num_rows="fixed",
            key="mapping_review_editor",
            hide_index=True
        )
        
        # Apply Edited Mappings button
        if st.button("Apply Edited Mappings", key="apply_edited_mappings", use_container_width=True, type="primary"):
            # Read edited table and update final_mapping
            updated_mapping: Dict[str, Dict[str, Any]] = {}
            
            for _, row in edited_df.iterrows():
                internal_field = str(row["Internal Field"])
                source_col = str(row["Source Column"]).strip()
                
                # Only add to mapping if source column is provided
                if source_col and source_col != "":
                    # Preserve existing mode if field was already mapped, otherwise set to manual
                    existing_mapping = final_mapping.get(internal_field, {})
                    mode = existing_mapping.get("mode", "manual")
                    
                    # If source column changed, mark as manual
                    if existing_mapping.get("value") != source_col:
                        mode = "manual"
                    
                    updated_mapping[internal_field] = {
                        "mode": mode,
                        "value": source_col
                    }
            
            # Update session state
            st.session_state.final_mapping = updated_mapping
            
            # Save to history
            if updated_mapping:
                save_to_history(updated_mapping)
            
            # Regenerate outputs
            if claims_df is not None and updated_mapping:
                from transformer import transform_claims_data
                st.session_state.transformed_df = transform_claims_data(claims_df, updated_mapping)
                generate_all_outputs()
            
            st.success("✅ Mappings updated successfully!")
            # Only log manual mappings (exclude AI auto-mapped fields)
            manual_mapped_count = len([f for f in updated_mapping.keys() 
                                     if updated_mapping[f].get("value") and updated_mapping[f].get("mode") == "manual"])
            if manual_mapped_count > 0:
                try:
                    log_event("mapping", f"Manual mappings updated via review table ({manual_mapped_count} fields mapped)")
                except NameError:
                    pass
            st.rerun()

    st.divider()

    # --- AI Suggestions Section ---
    st.markdown("#### AI Auto-Mapping Suggestions")

    # Compute AI suggestions only when needed
    if "auto_mapping" not in st.session_state and st.session_state.get("mappings_ready"):
        with st.spinner("Running AI mapping suggestions..."):
            st.session_state.auto_mapping = get_enhanced_automap(layout_df, claims_df)

    ai_suggestions = st.session_state.get("auto_mapping", {})
    auto_mapped_fields = st.session_state.get("auto_mapped_fields", [])

    if ai_suggestions:
        # Show auto-mapped fields (≥80% confidence) so users can override them
        auto_mapped_high_confidence = [
            (field, info) for field, info in ai_suggestions.items()
            if field in auto_mapped_fields and info.get("score", 0) >= 80
        ]
        
        if auto_mapped_high_confidence:
            st.info("Fields with AI confidence ≥ 80% have already been auto-mapped. You can override them manually below.")
            
            with st.expander("📋 Auto-Mapped Fields (≥80% confidence) - Click to Override", expanded=True):
                st.caption("These fields were automatically mapped. You can change them in the mapping form below.")
                for field, info in auto_mapped_high_confidence:
                    col1, col2, col3 = st.columns([3, 3, 2])
                    with col1:
                        st.markdown(f"**{field}**")
                    with col2:
                        mapped_value = final_mapping.get(field, {}).get("value", "")
                        st.code(mapped_value if mapped_value else "Not mapped", language="plaintext")
                        if "score" in info:
                            st.caption(f"AI Confidence: {info['score']}%")
                    with col3:
                        if st.button("Override", key=f"override_{field}", use_container_width=True):
                            # Clear the auto-mapping so user can manually select
                            if field in final_mapping:
                                final_mapping[field] = {"mode": "manual", "value": ""}
                                st.session_state.final_mapping = final_mapping
                                st.rerun()
                st.divider()

        with st.expander("🔍 View and Commit Additional Suggestions", expanded=False):
            selected_fields_tab2: List[str] = []

            for field, info in ai_suggestions.items():
                if field in auto_mapped_fields:
                    continue

                col1, col2, col3 = st.columns([3, 3, 1])
                with col1:
                    st.markdown(f"**{field}**")
                with col2:
                    st.code(info["value"], language="plaintext")
                    if "score" in info:
                        st.caption(f"Confidence: {info['score']}%")
                with col3:
                    selected = st.checkbox("Accept", key=f"ai_accept_{field}")
                    if selected:
                            selected_fields_tab2.append(field)

                    if selected_fields_tab2 and st.button("✅ Commit Selected Suggestions"):
                        for field in selected_fields_tab2:
                            st.session_state.final_mapping[field] = {
                                "mode": "auto",
                                "value": ai_suggestions[field]["value"]
                            }
                        
                        with st.spinner("Applying selected suggestions..."):
                            st.success(f"Committed {len(selected_fields_tab2)} suggestion(s).")
                        generate_all_outputs()
                        # Note: Not logging AI suggestions - only manual changes are logged

                        # --- Refresh transformed dataframe ---
                        claims_df = st.session_state.get("claims_df")
                        final_mapping = st.session_state.get("final_mapping", {})
                        if claims_df is not None and final_mapping:
                            st.session_state.transformed_df = transform_claims_data(claims_df, final_mapping)
                            st.session_state["transformed_ready"] = True

    else:
        st.info("No additional AI mapping suggestions available.")

with tab3:
    transformed_df = st.session_state.get("transformed_df")
    final_mapping = st.session_state.get("final_mapping", {})
    layout_df = st.session_state.get("layout_df")

    if transformed_df is None or not final_mapping:
        st.info("Please complete field mappings and preview transformed data first.")
        st.stop()
    else:
        # --- Auto-run validation (cached to avoid re-running on every rerun) ---
        # Create a hash of the data to detect changes
        data_hash = hashlib.md5(
            (str(final_mapping) + str(transformed_df.shape) + str(transformed_df.columns.tolist())).encode()
        ).hexdigest()
        
        # Check if we need to re-run validations
        cached_hash = st.session_state.get("validation_data_hash")
        validation_results = st.session_state.get("validation_results", [])
        
        if cached_hash != data_hash or not validation_results:
            with st.spinner("Running validation checks..."):
                # Get required fields from layout file, not from mapping
                if layout_df is not None:
                    required_fields_df = get_required_fields(layout_df)
                    required_fields = required_fields_df["Internal Field"].tolist() if isinstance(required_fields_df, pd.DataFrame) else []
                else:
                    # Fallback: use all mapped fields as required
                    required_fields = list(final_mapping.keys())
                
                # Get ALL mapped internal fields (both required and optional)
                all_mapped_internal_fields = [field for field in final_mapping.keys() if final_mapping[field].get("value")]
                
                # Get mapped field values (source column names) for reference
                mapped_fields = [mapping["value"] for mapping in final_mapping.values() if mapping.get("value")]
                
                # Run field-level validations (row-by-row checks)
                # Pass all mapped internal fields to ensure comprehensive validation
                field_level_results = run_validations(transformed_df, required_fields, all_mapped_internal_fields)
                
                # Run file-level validations (summary/aggregate checks)
                file_level_results = dynamic_run_validations(transformed_df, final_mapping)
                
                # Combine both types of validation results
                validation_results = field_level_results + file_level_results
                st.session_state.validation_results = validation_results
                st.session_state.validation_data_hash = data_hash
                
                # Log validation completion
                fail_count = len([r for r in validation_results if r.get("status") == "Fail"])
                warning_count = len([r for r in validation_results if r.get("status") == "Warning"])
                pass_count = len([r for r in validation_results if r.get("status") == "Pass"])
                try:
                    log_event("validation", f"Validation completed: {pass_count} passed, {warning_count} warnings, {fail_count} failed")
                except NameError:
                    pass

    # --- Validation Metrics Summary ---
    st.markdown("#### Validation Summary")
    
    validation_results: List[Dict[str, Any]] = st.session_state.get("validation_results", [])

    fails = [r for r in validation_results if r["status"] == "Fail"]
    warnings = [r for r in validation_results if r["status"] == "Warning"]
    passes = [r for r in validation_results if r["status"] == "Pass"]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Total Checks", value=len(validation_results))
    with col2:
        st.metric(label="✅ Passes", value=len(passes))
    with col3:
        st.metric(label="⚠️ Warnings / ❌ Fails", value=len(warnings) + len(fails))

    st.divider()

    # --- Custom Validation Rules Builder ---
    with st.expander("🔧 Custom Validation Rules Builder", expanded=False):
        st.markdown("Create custom validation rules for your data")
        
        rule_name = st.text_input("Rule Name:", key="custom_rule_name", placeholder="e.g., 'Email Format Check'")
        rule_field = st.selectbox(
            "Field to Validate:",
            options=[""] + (transformed_df.columns.tolist() if transformed_df is not None else []),
            key="custom_rule_field"
        )
        rule_type = st.selectbox(
            "Rule Type:",
            options=["null_check", "min_value", "max_value", "pattern_match"],
            key="custom_rule_type",
            help="null_check: Check null percentage\nmin_value: Minimum value threshold\nmax_value: Maximum value threshold\npattern_match: Pattern matching (coming soon)"
        )
        
        if rule_type in ["null_check", "min_value", "max_value"]:
            rule_threshold = st.number_input(
                "Threshold:",
                min_value=0.0,
                max_value=100.0 if rule_type == "null_check" else float('inf'),
                value=10.0,
                key="custom_rule_threshold"
            )
        else:
            rule_threshold = 0.0
        
        if st.button("Add Custom Rule", key="add_custom_rule"):
            if rule_name and rule_field:
                rule = CustomValidationRule(rule_name, rule_field, rule_type, rule_threshold)
                save_custom_rule(rule)
                st.success(f"Custom rule '{rule_name}' added!")
                st.rerun()
            else:
                st.warning("Please provide both rule name and field")
        
        # Show existing custom rules
        custom_rules = load_custom_rules()
        if custom_rules:
            st.markdown("**Existing Custom Rules:**")
            for i, rule in enumerate(custom_rules):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"- **{rule['name']}**: {rule['field']} ({rule['rule_type']}, threshold: {rule['threshold']})")
                with col2:
                    if st.button("Remove", key=f"remove_rule_{i}"):
                        st.session_state.custom_validation_rules.pop(i)
                        st.rerun()
            
            # Run custom validations
            if st.button("Run Custom Validations", key="run_custom_validations"):
                if transformed_df is not None:
                    custom_results = run_custom_validations(transformed_df, custom_rules)
                    # Add to validation results
                    validation_results.extend(custom_results)
                    st.session_state.validation_results = validation_results
                    st.success(f"Ran {len(custom_results)} custom validation(s)")
                    st.rerun()

    st.divider()

    # --- Detailed Validation Table ---
    st.markdown("#### Detailed Validation Results")
    if validation_results:
        # Add pagination for large result sets
        if len(validation_results) > 50:
            page_size = st.selectbox("Results per page:", [25, 50, 100, 200], index=1, key="validation_page_size")
            paginated_results, page_num, total_pages = paginate_dataframe(
                pd.DataFrame(validation_results),
                page_size=page_size
            )
            st.caption(f"Page {page_num} of {total_pages} ({len(validation_results)} total results)")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Previous", key="prev_validation_page", disabled=page_num == 1):
                    st.session_state.prev_page = True
                    st.rerun()
            with col2:
                if st.button("Next →", key="next_validation_page", disabled=page_num == total_pages):
                    st.session_state.next_page = True
                    st.rerun()
            
            validation_df = paginated_results
        else:
            validation_df = pd.DataFrame(validation_results)
        
        st.dataframe(validation_df, use_container_width=True)  # type: ignore[no-untyped-call]

        val_csv = validation_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Validation Report",
            data=val_csv,
            file_name="validation_report.csv",
            mime="text/csv",
            key="download_validation_report",
            on_click=lambda: _notify("✅ Validation Report Ready!")
        )
    else:
        st.info("No validation results to display. Click 'Run Validation' to perform checks.")

    st.divider()

    # --- Final Verdict Block with Threshold Analysis ---
    st.markdown("#### File Status & Validation Summary")

    if not validation_results:
        st.info("No validations have been run yet.")
    else:
            # Analyze validation results to calculate thresholds and stats
            layout_df = st.session_state.get("layout_df")
            final_mapping = st.session_state.get("final_mapping", {})
            
            # Extract required fields from layout
            if layout_df is None:
                required_fields_tab3: List[str] = []
            else:
                required_fields_tab3 = layout_df[layout_df["Usage"].astype(str).str.lower() == "required"]["Internal Field"].tolist()  # type: ignore[no-untyped-call]
            
            # Check for missing mandatory fields (this is the only rejection reason)
            unmapped_required_fields_tab3: List[str] = []
            for field in required_fields_tab3:
                mapping = final_mapping.get(field)
                if not mapping or not mapping.get("value") or str(mapping.get("value")).strip() == "":
                    unmapped_required_fields_tab3.append(field)
            
            # Analyze validation results for thresholds and stats
            total_records = len(transformed_df) if transformed_df is not None else 0
            
            # Calculate null check statistics for required fields
            required_field_null_stats: List[Dict[str, Any]] = []
            
            for result in validation_results:
                if result.get("check") == "Required Field Check":
                    field = result.get("field", "")
                    status = result.get("status", "")
                    # Handle both string and numeric values
                    fail_pct_str = result.get("fail_pct", "0")
                    fail_pct = float(fail_pct_str) if fail_pct_str else 0.0
                    fail_count_str = result.get("fail_count", "0")
                    fail_count = int(float(fail_count_str)) if fail_count_str else 0
                    
                    required_field_null_stats.append({
                        "field": field,
                        "null_percentage": fail_pct,
                        "null_count": fail_count,
                        "status": status
                    })
            
            # Calculate baseline threshold based on actual data
            # Use median + 2 standard deviations approach for more robust threshold
            if required_field_null_stats:
                null_percentages = [s["null_percentage"] for s in required_field_null_stats]
                avg_null_pct = sum(null_percentages) / len(null_percentages)
                max_null_pct = max(null_percentages)
                
                # Calculate standard deviation if we have enough data points
                if len(null_percentages) > 1:
                    import statistics
                    try:
                        std_dev = statistics.stdev(null_percentages)
                        # Threshold = average + 2*std_dev, but with reasonable bounds
                        suggested_threshold = min(max(avg_null_pct + (2 * std_dev), 1.0), 15.0)
                    except (statistics.StatisticsError, ValueError):
                        # Fallback if std_dev calculation fails
                        suggested_threshold = min(max(avg_null_pct + 3.0, 2.0), 10.0)
                else:
                    # If only one field, use a conservative threshold
                    suggested_threshold = min(max(avg_null_pct + 3.0, 2.0), 10.0)
            else:
                avg_null_pct = 0.0
                max_null_pct = 0.0
                suggested_threshold = 5.0
            
            # Find fields that actually exceed the calculated threshold (not just status="Fail")
            fields_exceeding_threshold: List[Dict[str, Any]] = []
            for stat in required_field_null_stats:
                if stat["null_percentage"] > suggested_threshold:
                    fields_exceeding_threshold.append(stat)
            
            # Count other validation issues (excluding optional field checks - user doesn't care about those)
            other_failures = [
                r for r in fails 
                if r.get("check") != "Required Field Check" 
                and r.get("check") != "Optional Field Check"
                and r.get("check") != "Fill Rate Check"
            ]
            other_warnings = [
                r for r in warnings 
                if r.get("check") != "Required Field Check"
                and r.get("check") != "Optional Field Check"
                and r.get("check") != "Fill Rate Check"
            ]
            
            # Determine file status
            is_rejected = len(unmapped_required_fields_tab3) > 0
            has_critical_issues = len(fields_exceeding_threshold) > 0
            has_warnings = len(other_failures) > 0  # Only care about non-optional issues
            
            # --- Status Display ---
            if is_rejected:
                st.markdown(
                """
                    <div style='background-color:#fdecea; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
                    <strong style='color: #b02a37; font-size: 1.2rem;'>❌ File Status: Rejected</strong>
                    <p style='color: #721c24; margin-top: 0.5rem; margin-bottom: 0;'>Mandatory fields are missing from the file.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            elif has_critical_issues:
                st.markdown(
                    """
                    <div style='background-color:#fff3cd; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
                    <strong style='color: #856404; font-size: 1.2rem;'>⚠️ File Status: Needs Review</strong>
                    <p style='color: #856404; margin-top: 0.5rem; margin-bottom: 0;'>Some required fields have high null rates that exceed recommended thresholds.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif has_warnings:
                st.markdown(
                    """
                    <div style='background-color:#d1ecf1; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
                    <strong style='color: #0c5460; font-size: 1.2rem;'>ℹ️ File Status: Approved with Warnings</strong>
                    <p style='color: #0c5460; margin-top: 0.5rem; margin-bottom: 0;'>File meets requirements but has some data quality issues to review.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style='background-color:#d4edda; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
                    <strong style='color: #155724; font-size: 1.2rem;'>✅ File Status: Approved</strong>
                    <p style='color: #155724; margin-top: 0.5rem; margin-bottom: 0;'>All validation checks passed. File is ready for processing.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # --- Detailed Status Summary (Collapsible Sections) ---
            
            # Mandatory Fields Status (Collapsible)
            with st.expander("📋 Mandatory Fields Status", expanded=True):
                if unmapped_required_fields_tab3:
                    field_list = ", ".join(f"`{f}`" for f in unmapped_required_fields_tab3)
                    st.error(f"**Missing Fields:** {field_list}")
                    st.caption("These mandatory fields must be present in the source file and properly mapped.")
                else:
                    st.success(f"✅ All {len(required_fields_tab3)} required fields are mapped and available in the file.")
            
            # Required Fields Analysis (Collapsible)
            if required_field_null_stats:
                with st.expander("📊 Mandatory Fields Analysis", expanded=True):
                    # Calculate insights
                    total_records = len(transformed_df) if transformed_df is not None else 0
                    fields_with_no_nulls = [s for s in required_field_null_stats if s["null_percentage"] == 0.0]
                    fields_with_low_nulls = [s for s in required_field_null_stats if 0 < s["null_percentage"] <= suggested_threshold]
                    fields_with_high_nulls = fields_exceeding_threshold
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Mandatory Fields", len(required_field_null_stats))
                    with col2:
                        st.metric("Perfect Fields (0% null)", len(fields_with_no_nulls))
                    with col3:
                        st.metric("Fields Within Threshold", len(fields_with_low_nulls))
                    with col4:
                        st.metric("Fields Exceeding Threshold", len(fields_with_high_nulls))
                    
                    st.markdown("---")
                    
                    # Key Insights Section
                    st.markdown("#### 📈 Key Insights")
                    
                    # Insight 1: Overall data quality
                    if len(fields_with_no_nulls) == len(required_field_null_stats):
                        st.success(f"**Excellent Data Quality:** All {len(required_field_null_stats)} mandatory fields have zero null values. This file demonstrates exceptional data completeness.")
                    elif len(fields_with_high_nulls) == 0:
                        completeness_pct = ((len(fields_with_no_nulls) + len(fields_with_low_nulls)) / len(required_field_null_stats) * 100) if required_field_null_stats else 0
                        st.success(f"**Good Data Quality:** {completeness_pct:.1f}% of mandatory fields ({len(fields_with_no_nulls) + len(fields_with_low_nulls)}/{len(required_field_null_stats)}) are within acceptable null rate thresholds.")
                    else:
                        st.warning(f"**Data Quality Concerns:** {len(fields_with_high_nulls)} out of {len(required_field_null_stats)} mandatory fields ({len(fields_with_high_nulls)/len(required_field_null_stats)*100:.1f}%) exceed the recommended null rate threshold.")
                    
                    # Insight 2: Threshold recommendation
                    st.markdown(f"""
                    <div style='background-color:#e7f3ff; padding: 1rem; border-radius: 6px; margin-top: 1rem; margin-bottom: 1rem;'>
                    <strong>📋 Recommended Threshold: {suggested_threshold:.1f}%</strong><br>
                    Based on statistical analysis of this file's data, the recommended null rate threshold for mandatory fields is <strong>{suggested_threshold:.1f}%</strong>. 
                    This is calculated from the average null rate ({avg_null_pct:.2f}%) plus 2 standard deviations, ensuring data quality while accounting for expected variations.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Fields Exceeding Threshold (only if any exist)
                    if fields_exceeding_threshold:
                        st.markdown("#### ⚠️ Fields Requiring Attention")
                        st.markdown("The following mandatory fields have null rates that exceed the recommended threshold:")
                        
                        # Create a clean table-like list
                        list_items = []
                        for field_stat in sorted(fields_exceeding_threshold, key=lambda x: x["null_percentage"], reverse=True):
                            field_name = field_stat["field"]
                            null_pct = field_stat["null_percentage"]
                            null_count = field_stat["null_count"]
                            fill_rate = 100 - null_pct
                            list_items.append(f"- **{field_name}**: {null_pct:.2f}% null ({null_count:,} of {total_records:,} records) - Fill rate: {fill_rate:.2f}%")
                        
                        st.markdown("\n".join(list_items))
                        
                        # Actionable recommendation
                        worst_field = max(fields_exceeding_threshold, key=lambda x: x["null_percentage"])
                        st.info(f"""
                        **💡 Recommendation:** Focus on improving data collection for **{worst_field['field']}** first, as it has the highest null rate ({worst_field['null_percentage']:.2f}%). 
                        This field affects {worst_field['null_count']:,} records ({worst_field['null_percentage']:.2f}% of the file).
                        """)
                    else:
                        st.success(f"✅ **All mandatory fields meet quality standards.** All {len(required_field_null_stats)} fields have null rates below the recommended {suggested_threshold:.1f}% threshold.")
                    
                    # Show all mandatory fields breakdown (using details HTML since expanders can't be nested)
                    st.markdown("<details><summary>📋 View All Mandatory Fields Breakdown</summary>", unsafe_allow_html=True)
                    # Sort by null percentage
                    sorted_stats = sorted(required_field_null_stats, key=lambda x: x["null_percentage"], reverse=True)
                    breakdown_items = []
                    for stat in sorted_stats:
                        field_name = stat["field"]
                        null_pct = stat["null_percentage"]
                        null_count = stat["null_count"]
                        fill_rate = 100 - null_pct
                        status_icon = "✅" if null_pct <= suggested_threshold else "⚠️"
                        breakdown_items.append(f"{status_icon} **{field_name}**: {null_pct:.2f}% null ({fill_rate:.2f}% filled) - {null_count:,} null records")
                    
                    st.markdown("\n".join(breakdown_items))
                    st.markdown("</details>", unsafe_allow_html=True)
            
            # Other Mandatory Field Validation Issues (Collapsible) - Only show non-optional issues
            if other_failures or other_warnings:
                with st.expander("⚠️ Other Mandatory Field Validations", expanded=False):
                    if other_failures:
                        st.markdown("**Critical Issues:**")
                        failure_list = []
                        for issue in other_failures:
                            check_name = issue.get("check", "Unknown Check")
                            field = issue.get("field", "")
                            message = issue.get("message", "")
                            if field:
                                failure_list.append(f"- **{check_name}** ({field}): {message}")
                            else:
                                failure_list.append(f"- **{check_name}**: {message}")
                        st.markdown("\n".join(failure_list))
                    
                    if other_warnings:
                        st.markdown("**Warnings:**")
                        warning_list = []
                        for issue in other_warnings:
                            check_name = issue.get("check", "Unknown Check")
                            field = issue.get("field", "")
                            message = issue.get("message", "")
                            if field:
                                warning_list.append(f"- **{check_name}** ({field}): {message}")
                            else:
                                warning_list.append(f"- **{check_name}**: {message}")
                        st.markdown("\n".join(warning_list))
            
            # File-Level Statistics (Collapsible) - Focus on mandatory fields insights
            file_level_results = [r for r in validation_results if not r.get("field")]
            if file_level_results:
                with st.expander("📈 File-Level Summary", expanded=False):
                    # Parse and display meaningful statistics
                    for result in file_level_results:
                        check_name = result.get("check", "Unknown")
                        message = result.get("message", "")
                        status = result.get("status", "")
                        
                        if check_name == "Required Fields Completeness":
                            # Extract percentage from message
                            if "%" in message:
                                st.metric("Mandatory Fields Completeness", message)
                            else:
                                if status == "Pass":
                                    st.success(f"✅ **{check_name}**: {message}")
                                else:
                                    st.error(f"❌ **{check_name}**: {message}")
                        else:
                            # Other file-level checks
                            if status == "Pass":
                                st.success(f"✅ **{check_name}**: {message}")
                            elif status == "Warning":
                                st.warning(f"⚠️ **{check_name}**: {message}")
                            else:
                                st.error(f"❌ **{check_name}**: {message}")
            
            # --- Rejection Explanation (only if rejected, Collapsible) ---
            if is_rejected:
                with st.expander("❌ Rejection Explanation", expanded=True):
                    field_list = ", ".join(f"`{f}`" for f in unmapped_required_fields_tab3)
                    rejection_text = (
                        f"This file has been **rejected** because the following mandatory fields required for Targeted Marketing setup are missing: {field_list}. "
                        f"These fields must be present in the source file and properly mapped before the file can be processed. "
                        f"Please ensure these fields are included in your source data and re-upload the file."
                    )
                    st.markdown(rejection_text)
                    
                    # Additional context if there are other issues
                    if has_critical_issues or has_warnings:
                        additional_issues = []
                        if has_critical_issues:
                            additional_issues.append(f"{len(fields_exceeding_threshold)} required field(s) with high null rates")
                        if other_failures:
                            additional_issues.append(f"{len(other_failures)} other validation failure(s)")
                        if other_warnings:
                            additional_issues.append(f"{len(other_warnings)} warning(s)")
                        
                        st.markdown("---")
                        st.markdown(f"""
                        <div style='background-color:#fff3cd; padding: 1rem; border-radius: 6px;'>
                        <strong>Additional Issues to Address:</strong> Once the mandatory fields are added, please also review: {', '.join(additional_issues)}.
                        </div>
                        """, unsafe_allow_html=True)

with tab4:
    st.markdown("#### Final Outputs and Downloads")
    
    # --- Batch Processing Section ---
    with st.expander("📦 Batch Processing (Multiple Files)", expanded=False):
        st.markdown("Process multiple claims files with the same mapping configuration")
        batch_files = st.file_uploader(
            "Upload multiple claims files:",
            accept_multiple_files=True,
            key="batch_files",
            help="Select multiple files to process with the current mapping"
        )
        
        if batch_files and final_mapping:
            if st.button("Process Batch Files", key="process_batch"):
                with st.spinner("Processing batch files..."):
                    from batch_processor import process_multiple_claims_files
                    results = process_multiple_claims_files(
                        batch_files,
                        layout_df,
                        final_mapping,
                        st.session_state.get("lookup_df")
                    )
                    
                    st.success(f"Processed {len(batch_files)} file(s)")
                    for file_name, result in results.items():
                        if result.get("status") == "processed":
                            st.info(f"✅ {file_name}: {result.get('rows', 0)} rows processed")
                        else:
                            st.error(f"❌ {file_name}: {result.get('error', 'Unknown error')}")
        elif batch_files and not final_mapping:
            st.warning("Please complete field mappings first before batch processing")

    # --- Activity Log Section ---
    st.markdown("### 📋 Activity Log")
    audit_log = st.session_state.setdefault("audit_log", [])
    
    if audit_log:
        # Show last 20 events in reverse chronological order
        recent_events = audit_log[-20:][::-1]
        
        # Create DataFrame for display
        log_data = []
        for event in recent_events:
            event_type = event.get("event_type", "unknown")
            message = event.get("message", "")
            timestamp = event.get("timestamp", "")
            
            # Format timestamp for display
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                time_str = timestamp
            
            log_data.append({
                "Time": time_str,
                "Type": event_type.upper(),
                "Message": message
            })
        
        log_df = pd.DataFrame(log_data)
        st.dataframe(log_df, use_container_width=True, hide_index=True)
        
        # Clear log button
        if st.button("Clear Activity Log", key="clear_activity_log_tab4"):
            st.session_state.audit_log = []
            st.rerun()
    else:
        st.info("No activity logged yet. Events will appear here as you use the app.")
    
    st.divider()

    if "final_mapping" not in st.session_state or not st.session_state.final_mapping:
        st.info("Complete required field mappings to generate outputs.")
    else:
        final_mapping = st.session_state.get("final_mapping", {})
        layout_df = st.session_state.get("layout_df")
        claims_df = st.session_state.get("claims_df")
        anonymized_df = st.session_state.get("anonymized_df")
        mapping_table = st.session_state.get("mapping_table")
        transformed_df = st.session_state.get("transformed_df")

        if any(x is None for x in [anonymized_df, mapping_table, transformed_df]):
            st.warning("Outputs not fully generated yet. Please complete mapping and preview steps.")
        else:
            # --- Anonymized Claims File Section ---
            with st.expander("Anonymized Claims Preview", expanded=True):
                anonymized_df = st.session_state.get("anonymized_df")
                st.dataframe(anonymized_df.head(), use_container_width=True)  # type: ignore[no-untyped-call]

                st.markdown("**Customize Anonymized File Output**")
                col1, col2, col3 = st.columns(3)

                with col1:
                    file_name_input = st.text_input("File Name (without extension)", value="anonymized_claims")
                with col2:
                    file_type = st.selectbox("File Type", options=[".csv", ".txt", ".xlsx"], index=0)
                with col3:
                    delimiter = st.selectbox("Delimiter", options=["Comma", "Tab", "Pipe"], index=0)

                delim_char = {
                    "Comma": ",",
                    "Tab": "\t",
                    "Pipe": "|"
                }[delimiter]

                if file_type == ".xlsx":
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        anonymized_df.to_excel(writer, index=False)  # type: ignore[no-untyped-call]
                    anonymized_data = output.getvalue()
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                else:
                    anonymized_data = anonymized_df.to_csv(index=False, sep=delim_char).encode('utf-8')  # type: ignore[no-untyped-call]
                    mime = "text/plain" if file_type == ".txt" else "text/csv"

                full_filename = f"{file_name_input.strip() or 'anonymized_claims'}{file_type}"

                # ✅ Save to session state for ZIP bundling
                st.session_state.anonymized_data = anonymized_data
                st.session_state.anonymized_filename = full_filename

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label=f"Download {file_type.upper()}",
                        data=anonymized_data,
                        file_name=full_filename,
                        mime=mime,
                        key="download_anon",
                        on_click=lambda: _notify("✅ Anonymized File Ready!")
                    )
                with col2:
                    if st.button("Regenerate Anonymized File"):
                        with st.spinner("Regenerating anonymized data..."):
                            claims_df_local = st.session_state.get("claims_df")
                            final_mapping_local = st.session_state.get("final_mapping", {})
                            if claims_df_local is not None:
                                st.session_state.anonymized_df = anonymize_claims_data(
                                    claims_df_local,
                                    final_mapping_local
                                )
                            _notify("✅ Anonymized file regenerated!")

            # --- Field Mapping Table Section ---
            with st.expander("Field Mapping Table Preview", expanded=True):
                mapping_table = st.session_state.get("mapping_table")
                
                # Add pagination for large tables
                if mapping_table is not None and len(mapping_table) > 100:
                    table_page_size = st.slider("Rows per page:", 25, min(500, len(mapping_table)), 100, key="mapping_table_page_size")
                    page_num = st.session_state.get("mapping_table_page", 1)
                    
                    start_idx = (page_num - 1) * table_page_size
                    end_idx = start_idx + table_page_size
                    paginated_table = mapping_table.iloc[start_idx:end_idx]
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col1:
                        if st.button("← Previous", key="prev_mapping_table", disabled=page_num == 1):
                            st.session_state.mapping_table_page = max(1, page_num - 1)
                            st.rerun()
                    with col2:
                        st.caption(f"Page {page_num} of {(len(mapping_table) + table_page_size - 1) // table_page_size} ({len(mapping_table)} total rows)")
                    with col3:
                        if st.button("Next →", key="next_mapping_table", disabled=page_num * table_page_size >= len(mapping_table)):
                            st.session_state.mapping_table_page = page_num + 1
                            st.rerun()
                    
                    st.dataframe(paginated_table, use_container_width=True)  # type: ignore[no-untyped-call]
                else:
                    st.dataframe(mapping_table, use_container_width=True)  # type: ignore[no-untyped-call]
                mapping_csv = mapping_table.to_csv(index=False).encode('utf-8')  # type: ignore[no-untyped-call]
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download Mapping Table",
                        data=mapping_csv,
                        file_name="field_mapping_table.csv",
                        mime="text/csv",
                        key="download_mapping",
                        on_click=lambda: _notify("✅ Field Mapping Table Ready!")
                    )
                with col2:
                    if st.button("Regenerate Mapping Table"):
                        with st.spinner("Regenerating mapping table..."):
                            layout_df_local = st.session_state.get("layout_df")
                            claims_df_local = st.session_state.get("claims_df")
                            final_mapping_local = st.session_state.get("final_mapping", {})
                            if layout_df_local is not None and claims_df_local is not None:
                                st.session_state.mapping_table = generate_mapping_table(
                                    layout_df_local,
                                    final_mapping_local,
                                    claims_df_local
                                )
                            _notify("✅ Mapping table regenerated!")

            # --- Optional Attachments Section ---
            st.markdown("### Optional Attachments to Include in ZIP")
            uploaded_attachments = st.file_uploader(
                "Attach any additional files (e.g., header file, original claims, notes)",
                accept_multiple_files=True,
                key="zip_attachments"
            )

            # --- Custom Notes Section ---
            st.markdown("### Add Custom Notes (Optional)")
            notes_text = st.text_area("Include any notes or instructions to be added in the README file:", key="readme_notes")

            # --- Download All as ZIP ---
            st.divider()
            st.markdown("### Download All Outputs as ZIP")

            readme_text = notes_text.strip() if notes_text else "No additional notes provided."
            anon_file_name = st.session_state.get("anonymized_filename", "anonymized_claims.csv")
            anonymized_data = st.session_state.get("anonymized_data", b"")

            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w") as zip_file:
                zip_file.writestr(anon_file_name, anonymized_data)
                zip_file.writestr("field_mapping_table.csv", mapping_csv)
                zip_file.writestr("readme.txt", readme_text)
                for attachment in uploaded_attachments or []:  # type: ignore[var-annotated]
                    att_name: Any = attachment.name  # type: ignore[attr-defined]
                    att_bytes: Any = attachment.getvalue()  # type: ignore[call-arg]
                    zip_file.writestr(att_name, att_bytes)  # type: ignore[arg-type]

            buffer.seek(0)

            col1, col2 = st.columns(2)
            with col1:
                def on_zip_download():
                    try:
                        log_event("output", "ZIP file generated and downloaded (all_outputs.zip)")
                    except NameError:
                        pass
                    _notify("✅ ZIP file ready!")
                
                st.download_button(
                    label="Download All Files (ZIP)",
                    data=buffer,
                    file_name="all_outputs.zip",
                    mime="application/zip",
                    key="download_zip",
                    on_click=on_zip_download
                )
            with col2:
                if st.button("Regenerate All Outputs"):
                    with st.spinner("Regenerating all outputs..."):
                        if claims_df is not None:
                            st.session_state.anonymized_df = anonymize_claims_data(claims_df, final_mapping)
                        if layout_df is not None and claims_df is not None:
                            st.session_state.mapping_table = generate_mapping_table(layout_df, final_mapping, claims_df)
                        _notify("✅ All outputs regenerated!")
                        st.rerun()
