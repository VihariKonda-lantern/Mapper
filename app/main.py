# --- main.py ---
"""
pyright: reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUnknownAttributeType=false
"""
# --- Standard Library Imports ---
import hashlib
import io
import json
import os
import time
import zipfile
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, cast

# --- Third-Party Imports ---
import pandas as pd  # type: ignore[import-not-found]
import streamlit as st  # type: ignore[import-not-found]

st: Any = st  # type: ignore[assignment]
pd: Any = pd  # type: ignore[assignment]

# --- Streamlit Setup (MUST BE FIRST STREAMLIT COMMAND) ---
st.set_page_config(page_title="Claims Mapper and Validator", layout="wide")

# --- Configuration ---
from core.config import (
    AI_CONFIDENCE_THRESHOLD,
    DEFAULT_VALIDATION_PAGE_SIZE,
    VALIDATION_PAGE_SIZES
)

# --- App Modules ---
from file.layout_loader import (
    get_required_fields,
    render_layout_summary_section
)
from mapping.mapping_engine import get_enhanced_automap
from utils.utils import render_claims_file_summary
from data.transformer import transform_claims_data
from validation.validation_engine import (
    run_validations,
    dynamic_run_validations,
)
from data.anonymizer import anonymize_claims_data

# --- UI Modules ---
from ui.ui_styling import inject_summary_card_css, inject_ux_javascript, inject_main_layout_css  # type: ignore[import-untyped]
from ui.ui_components import render_progress_bar, _notify, confirm_action  # type: ignore[import-untyped]
from ui.upload_ui import (  # type: ignore[import-untyped]
    render_upload_and_claims_preview,
    render_lookup_summary_section,
)
from ui.mapping_ui import (  # type: ignore[import-untyped]
    render_field_mapping_tab,
    generate_mapping_table
)
from data.output_generator import generate_all_outputs  # type: ignore[import-untyped]
from core.session_state import initialize_undo_redo, save_to_history, undo_mapping, redo_mapping  # type: ignore[import-untyped]
from performance.cache_utils import load_layout_cached, load_lookups_cached  # type: ignore[import-untyped]
from file.upload_handlers import capture_claims_file_metadata  # type: ignore[import-untyped]
from advanced_features import (  # type: ignore[import-untyped]
    init_dark_mode,
    toggle_dark_mode,
    get_dark_mode_css,
    inject_keyboard_shortcuts,
    save_mapping_template,
    load_mapping_template,
    list_saved_templates,
)
from performance.performance_utils import paginate_dataframe, get_data_hash, render_lazy_dataframe  # type: ignore[import-untyped]
from validation.validation_builder import (  # type: ignore[import-untyped]
    CustomValidationRule,
    save_custom_rule,
    load_custom_rules,
    run_custom_validations,
)

# --- New Feature Modules ---
from data.data_quality import (  # type: ignore[import-untyped]
    calculate_data_quality_score,
    detect_duplicates,
    get_column_statistics,
    sample_data,  # type: ignore[assignment]
    detect_outliers,
    create_completeness_matrix,
    generate_data_profile
)
from mapping.mapping_enhancements import (  # type: ignore[import-untyped]
    get_mapping_confidence_score,
    validate_mapping_before_processing,  # type: ignore[assignment]
    get_mapping_version,
    export_mapping_template_for_sharing,
    import_mapping_template_from_shareable
)
from ui.user_experience import (  # type: ignore[import-untyped]
    init_user_preferences,
    add_recent_file,
    get_notifications,
    mark_notification_read,
    clear_notifications,
    get_help_content,
    global_search
)
from validation.advanced_validation import (  # type: ignore[import-untyped]
    track_validation_performance,
    get_validation_performance_stats,
)
from monitoring.monitoring_logging import (  # type: ignore[import-untyped]
    get_error_statistics,
    track_feature_usage,
    get_usage_statistics,
    get_system_health,
    export_logs
)
from testing_qa import (  # type: ignore[import-untyped]
    generate_test_data_from_claims,  # type: ignore[assignment]
    generate_test_data_from_layout,  # type: ignore[assignment]
    create_mapping_unit_tests,
    run_unit_tests,
)

# --- Improvement Modules ---
from utils.improvements_utils import (  # type: ignore[import-untyped]
    render_empty_state,  # type: ignore[assignment]
    render_loading_skeleton,
    get_user_friendly_error,
    check_session_timeout,
    update_activity_time,
    get_memory_usage,
)
from ui.ui_improvements import (  # type: ignore[import-untyped]
    show_confirmation_dialog,  # type: ignore[assignment]
    show_toast,
    show_undo_redo_feedback,
    render_tooltip,
    show_onboarding_tour,
    render_sortable_table,
)
from performance.performance_utils import render_lazy_dataframe  # type: ignore[import-untyped]
from ui.progress_indicators import render_workflow_progress  # type: ignore[import-untyped]
from ui.wizard_mode import WizardMode, render_quick_actions  # type: ignore[import-untyped]
from core.state_manager import SessionStateManager  # type: ignore[import-untyped]

# --- Audit Log Helper Function (using State Manager) ---
def log_event(event_type: str, message: str) -> None:
    """Log an event to the in-memory audit log.

    Args:
        event_type: Type of event (e.g., "file_upload", "mapping", "validation", "output")
        message: Descriptive message about the event
    """
    from core.state_manager import SessionStateManager
    try:
        SessionStateManager.add_audit_event(event_type, message)
    except Exception as e:
        # Log to console for debugging instead of silently failing
        import sys
        print(f"Error logging event: {e}", file=sys.stderr)

# Initialize user preferences (must be done early)
init_user_preferences()

# Initialize dark mode
init_dark_mode()

# Check session timeout
if check_session_timeout():
    st.warning("⚠️ Your session has timed out due to inactivity. Please refresh the page.")
    st.stop()

# Update activity time
update_activity_time()

# Show onboarding tour for first-time users
show_onboarding_tour()

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

# --- Sticky Top Bar with Title and Workflow Progress ---
# Determine current workflow step
current_workflow_step = 0
if SessionStateManager.get_transformed_df() is not None:
    current_workflow_step = 3
elif SessionStateManager.get_final_mapping() and len(SessionStateManager.get_final_mapping()) > 0:
    current_workflow_step = 2
elif SessionStateManager.get_layout_df() is not None and SessionStateManager.get_claims_df() is not None:
    current_workflow_step = 1

st.markdown("""
    <div style='
        position: sticky;
        top: 0;
        z-index: 1000;
        background: #f0f0f0;
        color: #000000;
        padding: 0.5rem 1rem;
        margin: -1rem -1rem 1rem -1rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        border-bottom: 1px solid #ddd;
    '>
        <div style='display: flex; justify-content: space-between; align-items: center; max-width: 1400px; margin: 0 auto;'>
            <div style='font-size: 14px; font-weight: 600;'>Claims Mapper & Validator</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Show workflow progress
render_workflow_progress(current_workflow_step, 4)

# Show wizard mode if enabled
WizardMode.render_wizard_header()

# Show quick actions in sidebar
with st.sidebar:
    st.divider()
    render_quick_actions()

# --- Main Content Container with Optimized Layout ---
# CSS moved to ui_styling.py inject_main_layout_css()
inject_main_layout_css()

# --- Sidebar: Activity Log Panel ---
# --- Sidebar with Settings ---
with st.sidebar:
    # Dark Mode Toggle
    dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.get("dark_mode", False), key="dark_mode_toggle")
    if dark_mode != st.session_state.get("dark_mode", False):
        toggle_dark_mode()
        show_toast("Dark mode toggled", "🌙")
        st.session_state.needs_refresh = True
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
                    border-left: 2px solid #999;
                    font-size: 13px;
                ">
                    <div style="color: #000000; font-weight: 600; font-size: 12px;">{event_type.upper()}</div>
                    <div style="color: #000000; margin-top: 0.25rem; font-size: 13px;">{message}</div>
                    <div style="color: #000000; font-size: 11px; margin-top: 0.25rem;">{time_str}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No activity yet. Events will appear here as you use the app.")
    # Clear log button
    if st.button("Clear Log", key="clear_audit_log", use_container_width=True):
        if show_confirmation_dialog(
            "Clear Activity Log",
            "Are you sure you want to clear the activity log?",
            confirm_label="Yes, Clear",
            cancel_label="Cancel",
            key="clear_log_confirm"
        ):
            st.session_state.audit_log = []
            show_toast("Activity log cleared", "🗑️")
            st.session_state.needs_refresh = True

# Handle refresh flag at the start - use state flag instead of rerun
if st.session_state.get("needs_refresh", False):
    st.session_state.needs_refresh = False
    # Don't rerun - let Streamlit's natural rerun cycle handle updates

# Wrap tabs in container for better layout control
main_container = st.container()
with main_container:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Setup", 
        "Field Mapping", 
        "Preview & Validate", 
        "Downloads Tab",
        "Data Quality",
        "Tools & Analytics"
    ])

with tab1:
    from tabs.tab_setup import render_setup_tab
    render_setup_tab()

with tab2:
    from tabs.tab_mapping import render_mapping_tab
    render_mapping_tab()

with tab3:
    from tabs.tab_validation import render_validation_tab
    render_validation_tab()

with tab4:
    from tabs.tab_downloads import render_downloads_tab
    render_downloads_tab()

with tab5:
    from tabs.tab_data_quality import render_data_quality_tab
    render_data_quality_tab()

with tab6:
    from tabs.tab_tools import render_tools_tab
    render_tools_tab()


