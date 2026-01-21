# --- main.py ---
"""
pyright: reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUnknownAttributeType=false
"""
# --- Standard Library Imports ---
from datetime import datetime
from typing import Any

# --- Third-Party Imports ---
import pandas as pd  # type: ignore[import-not-found]
import streamlit as st  # type: ignore[import-not-found]

st: Any = st  # type: ignore[assignment]
pd: Any = pd  # type: ignore[assignment]

# --- Streamlit Setup (MUST BE FIRST STREAMLIT COMMAND) ---
# Get UI labels for page title (defaults to claims for backward compatibility)
from core.ui_labels import get_ui_labels  # type: ignore[import-untyped]
ui_labels = get_ui_labels()
st.set_page_config(page_title=ui_labels.app_title, layout="wide")

# --- Configuration ---
# Config values used in tabs, not in main.py

# --- UI Modules ---
from ui.ui_styling import inject_ux_javascript  # type: ignore[import-untyped]
from ui.design_system import inject_unified_design_system  # type: ignore[import-untyped]
# UI functions (render_upload_and_claims_preview, render_lookup_summary_section, 
# render_field_mapping_tab, generate_mapping_table) - used in tabs, not in main.py
# generate_all_outputs, initialize_undo_redo, save_to_history, undo_mapping, redo_mapping,
# load_layout_cached, load_lookups_cached, capture_claims_file_metadata - used in tabs, not in main.py
from advanced_features import (  # type: ignore[import-untyped]
    inject_keyboard_shortcuts,
    # save_mapping_template, load_mapping_template, list_saved_templates,  # Used in tab_mapping.py, not main.py
)
# Performance utils, data quality, mapping enhancements, validation builder functions 
# removed from main.py - used directly in tabs, not in main.py

# --- UI Components ---
from ui.ui_components import (  # type: ignore[import-untyped]
    init_user_preferences,
    show_confirmation_dialog,  # type: ignore[assignment]
    show_toast,
    show_onboarding_tour,
    # Other UI components used in tabs, not in main.py
)

# --- Improvement Modules ---
from utils.improvements_utils import (  # type: ignore[import-untyped]
    check_session_timeout,
    update_activity_time,
    # Other utils used in tabs, not in main.py
)

# --- State Management ---
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

# Check session timeout
if check_session_timeout():
    st.warning("⚠️ Your session has timed out due to inactivity. Please refresh the page.")
    st.stop()

# Update activity time
update_activity_time()

# Show onboarding tour for first-time users
show_onboarding_tour()

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

# --- Sticky Top Bar with Title ---
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

# --- Main Content Container with Optimized Layout ---
# Unified Design System - Golden Rules of UI/UX
inject_unified_design_system()

# --- Sidebar: Activity Log Panel ---
with st.sidebar:
    with st.expander("Activity Log", expanded=False):
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
    tab1, tab2, tab3, tab4 = st.tabs([
        "Setup", 
        "Field Mapping", 
        "Preview & Validate", 
        "Downloads Tab"
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


