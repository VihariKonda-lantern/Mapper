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
import time
# Removed unused matplotlib import

# --- Constants ---
AUDIT_LOG_MAX_SIZE = 100
MAPPING_HISTORY_MAX_SIZE = 50
AI_CONFIDENCE_THRESHOLD = 80
VALIDATION_PAGE_SIZES = [25, 50, 100, 200]
DEFAULT_VALIDATION_PAGE_SIZE = 50

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
from ui_components import render_progress_bar, _notify, confirm_action  # type: ignore[import-untyped]
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
from upload_handlers import capture_claims_file_metadata  # type: ignore[import-untyped]
from advanced_features import (  # type: ignore[import-untyped]
    init_dark_mode,
    toggle_dark_mode,
    get_dark_mode_css,
    inject_keyboard_shortcuts,
    save_mapping_template,
    load_mapping_template,
    list_saved_templates,
)
from performance_utils import paginate_dataframe, get_data_hash  # type: ignore[import-untyped]
from validation_builder import (  # type: ignore[import-untyped]
    CustomValidationRule,
    save_custom_rule,
    load_custom_rules,
    run_custom_validations,
)

# --- New Feature Modules ---
from data_quality import (  # type: ignore[import-untyped]
    calculate_data_quality_score,
    detect_duplicates,
    get_column_statistics,
    sample_data,
    detect_outliers,
    create_completeness_matrix,
    generate_data_profile
)
from mapping_enhancements import (  # type: ignore[import-untyped]
    get_mapping_confidence_score,
    validate_mapping_before_processing,
    get_mapping_version,
    export_mapping_template_for_sharing,
    import_mapping_template_from_shareable
)
from user_experience import (  # type: ignore[import-untyped]
    init_user_preferences,
    save_user_preference,
    load_user_preferences,
    add_recent_file,
    get_recent_files,
    get_favorites,
    get_notifications,
    mark_notification_read,
    clear_notifications,
    get_help_content,
    global_search
)
from advanced_validation import (  # type: ignore[import-untyped]
    track_validation_performance,
    get_validation_performance_stats,
)
from monitoring_logging import (  # type: ignore[import-untyped]
    get_error_statistics,
    track_feature_usage,
    get_usage_statistics,
    get_system_health,
    export_logs
)
from testing_qa import (  # type: ignore[import-untyped]
    generate_test_data,
    generate_test_data_from_claims,
    generate_test_data_from_layout,
    create_mapping_unit_tests,
    run_unit_tests,
)

# --- Improvement Modules ---
from improvements_utils import (  # type: ignore[import-untyped]
    debounce,
    show_progress_with_callback,
    render_empty_state,
    render_loading_skeleton,
    get_user_friendly_error,
    validate_file_upload,
    check_session_timeout,
    update_activity_time,
    check_rate_limit,
    sanitize_input,
    track_operation_time,
    get_memory_usage,
    compress_dataframe,
    backup_session_state,
    restore_session_state,
    MAX_FILE_SIZE_MB,
    SESSION_TIMEOUT_MINUTES,
)
from ui_improvements import (  # type: ignore[import-untyped]
    show_confirmation_dialog,
    show_toast,
    show_undo_redo_feedback,
    render_tooltip,
    show_onboarding_tour,
    show_contextual_help,
    render_enhanced_search,
    render_sortable_table,
    render_filterable_table,
    export_table_view,
    render_drag_drop_upload,
    render_file_preview,
    save_bookmark,
    load_bookmark,
    list_bookmarks,
    render_version_history,
    render_comparison_view,
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
        # Keep only last N events to prevent memory bloat - use del for better memory efficiency
        if len(audit_log) > AUDIT_LOG_MAX_SIZE:
            # Delete oldest entries instead of creating new list slice
            del audit_log[:len(audit_log) - AUDIT_LOG_MAX_SIZE]
    except Exception as e:
        # Log to console for debugging instead of silently failing
        import sys
        print(f"Error logging event: {e}", file=sys.stderr)

# --- Streamlit Setup ---
st.set_page_config(page_title="Claims Mapper and Validator", layout="wide")

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

# --- Sticky Top Bar with Title and Breadcrumb ---
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
            <div style='font-size: 11px; opacity: 0.8;'>
                <span>1) Setup</span> <span style='margin: 0 4px;'>→</span>
                <span>2) Mapping</span> <span style='margin: 0 4px;'>→</span>
                <span>3) Preview & Validate</span> <span style='margin: 0 4px;'>→</span>
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
            padding-top: 0.1rem !important;
            padding-bottom: 0.25rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 1400px;
        }
        
        /* Reduce font sizes globally */
        body, .main {
            font-size: 13px !important;
        }
        
        /* Consistent header sizing - enforce same size for all headers of same level */
        h1 {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
        }
        
        h2 {
            font-size: 1.25rem !important;
            font-weight: 600 !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
            font-weight: 600 !important;
        }
        
        h4 {
            font-size: 1rem !important;
            font-weight: 600 !important;
        }
        
        h5 {
            font-size: 0.9rem !important;
            font-weight: 600 !important;
        }
        
        h6 {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
        }
        
        /* Override any inline styles in markdown headers */
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3,
        .stMarkdown h4,
        .stMarkdown h5,
        .stMarkdown h6 {
            font-size: inherit !important;
            font-weight: 600 !important;
        }
        
        /* Ensure markdown headers use consistent sizing */
        .stMarkdown h1 { font-size: 1.5rem !important; }
        .stMarkdown h2 { font-size: 1.25rem !important; }
        .stMarkdown h3 { font-size: 1.1rem !important; }
        .stMarkdown h4 { font-size: 1rem !important; }
        .stMarkdown h5 { font-size: 0.9rem !important; }
        .stMarkdown h6 { font-size: 0.85rem !important; }
        
        p, div, span, label {
            font-size: 13px !important;
        }
        
        /* Reduce excessive vertical spacing */
        h1, h2, h3, h4, h5, h6 {
            margin-top: 0.25rem !important;
            margin-bottom: 0.125rem !important;
        }
        
        /* Tighter spacing for tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.125rem !important;
            margin-bottom: 0.125rem !important;
        }
        
        /* Reduce spacing for dividers */
        hr {
            margin: 0.25rem 0 !important;
        }
        
        /* Tighter spacing between elements */
        .element-container {
            margin-bottom: 0.125rem !important;
        }
        
        /* Reduce spacing in columns */
        .stColumn {
            gap: 0.25rem !important;
        }
        
        /* Tighter spacing for expanders */
        [data-testid="stExpander"] {
            margin-bottom: 0.25rem !important;
        }
        
        [data-testid="stExpander"] > div {
            padding-top: 0.25rem !important;
            padding-bottom: 0.25rem !important;
        }
        
        /* Reduce spacing in file uploader */
        [data-testid="stFileUploader"] {
            margin-bottom: 0.25rem !important;
        }
        
        /* Tighter spacing for buttons */
        .stButton {
            margin-bottom: 0.125rem !important;
            font-size: 13px !important;
        }
        
        /* Reduce spacing in forms */
        [data-testid="stForm"] {
            margin-bottom: 0.25rem !important;
        }
        
        /* Tighter spacing for dataframes */
        [data-testid="stDataFrame"] {
            margin-bottom: 0.25rem !important;
            font-size: 12px !important;
        }
        
        /* Reduce spacing for metrics */
        [data-testid="stMetricContainer"] {
            margin-bottom: 0.125rem !important;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
        }
        
        /* Tighter spacing for info/warning/error messages */
        .stAlert {
            margin-bottom: 0.25rem !important;
            padding: 0.375rem 0.75rem !important;
            font-size: 13px !important;
        }
        
        /* Reduce spacing for selectboxes and inputs */
        .stSelectbox, .stTextInput, .stNumberInput, .stTextArea, .stMultiselect, .stDateInput, .stTimeInput {
            margin-bottom: 0.5rem !important;
        }
        
        /* Ensure proper spacing for input containers */
        .stSelectbox > div,
        .stTextInput > div,
        .stTextArea > div,
        .stNumberInput > div,
        .stMultiselect > div,
        .stDateInput > div,
        .stTimeInput > div {
            margin-bottom: 0.5rem !important;
        }
        
        /* Tighter spacing for captions */
        .stCaption {
            margin-top: 0.0625rem !important;
            margin-bottom: 0.0625rem !important;
            font-size: 11px !important;
        }
        
        /* Reduce spacing in sidebar */
        .css-1d391kg {
            padding-top: 0.5rem !important;
        }
        
        /* Tighter spacing for markdown blocks */
        .stMarkdown {
            margin-bottom: 0.125rem !important;
            font-size: 13px !important;
        }
        
        /* Reduce spacing between containers */
        .stContainer {
            margin-bottom: 0.25rem !important;
        }
        
        /* Tighter spacing for download buttons */
        [data-testid="stDownloadButton"] {
            margin-bottom: 0.125rem !important;
            font-size: 13px !important;
        }
        
        /* Reduce spacing for progress bars */
        [data-testid="stProgressBar"] {
            margin-bottom: 0.125rem !important;
        }
        
        /* Tighter spacing for code blocks */
        .stCodeBlock {
            margin-bottom: 0.25rem !important;
            font-size: 12px !important;
        }
        
        /* Reduce spacing for JSON displays */
        [data-testid="stJson"] {
            margin-bottom: 0.25rem !important;
            font-size: 12px !important;
        }
        
        /* Tighter overall page spacing */
        .main {
            padding-top: 0.25rem !important;
        }
        
        /* Reduce spacing in summary cards */
        .summary-cards-wrapper {
            margin-bottom: 0.25rem !important;
        }
        
        /* Tighter spacing for data editor */
        [data-testid="stDataEditor"] {
            margin-bottom: 0.25rem !important;
            font-size: 12px !important;
        }
        
        /* Additional tight spacing rules */
        .stCheckbox, .stRadio {
            margin-bottom: 0.125rem !important;
            font-size: 13px !important;
        }
        
        /* Reduce spacing in multi-select */
        [data-testid="stMultiSelect"] {
            margin-bottom: 0.125rem !important;
            font-size: 13px !important;
        }
        
        /* Tighter spacing for sliders */
        [data-testid="stSlider"] {
            margin-bottom: 0.125rem !important;
        }
        
        /* Reduce spacing for date inputs */
        [data-testid="stDateInput"] {
            margin-bottom: 0.125rem !important;
            font-size: 13px !important;
        }
        
        /* Tighter spacing for time inputs */
        [data-testid="stTimeInput"] {
            margin-bottom: 0.125rem !important;
            font-size: 13px !important;
        }
        
        /* Reduce spacing for color pickers */
        [data-testid="stColorPicker"] {
            margin-bottom: 0.125rem !important;
        }
        
        /* Tighter spacing for file uploader dropzone */
        [data-testid="stFileUploader"] > div {
            padding: 0.5rem !important;
            font-size: 13px !important;
        }
        
        /* Reduce spacing in columns wrapper */
        [data-testid="column"] {
            gap: 0.25rem !important;
        }
        
        /* Tighter spacing for empty states */
        .stEmpty {
            margin-bottom: 0.25rem !important;
            font-size: 13px !important;
        }
        
        /* Reduce spacing for success messages */
        .stSuccess {
            margin-bottom: 0.25rem !important;
            padding: 0.375rem 0.75rem !important;
            font-size: 13px !important;
        }
        
        /* Tighter spacing for error messages */
        .stError {
            margin-bottom: 0.25rem !important;
            padding: 0.375rem 0.75rem !important;
            font-size: 13px !important;
        }
        
        /* Reduce spacing for warning messages */
        .stWarning {
            margin-bottom: 0.25rem !important;
            padding: 0.375rem 0.75rem !important;
            font-size: 13px !important;
        }
        
        /* Tighter spacing for info messages */
        .stInfo {
            margin-bottom: 0.25rem !important;
            padding: 0.375rem 0.75rem !important;
            font-size: 13px !important;
        }
        
        /* Remove all gradient backgrounds */
        * {
            background-image: none !important;
        }
        
        /* UI/UX Best Practices - Golden Rules */
        
        /* 1. Visual Hierarchy - Primary vs Secondary Actions */
        .stButton > button[type="primary"],
        button[data-baseweb="button"][kind="primary"] {
            background-color: #495057 !important;
            color: white !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        }
        
        .stButton > button:not([type="primary"]):not(:disabled) {
            background-color: #6c757d !important;
            color: white !important;
        }
        
        /* 2. Accessibility - Focus States */
        .stButton > button:focus,
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div:focus,
        .stTextArea > div > div > textarea:focus,
        button[data-baseweb="button"]:focus {
            outline: 2px solid #495057 !important;
            outline-offset: 2px !important;
            box-shadow: 0 0 0 3px rgba(73, 80, 87, 0.2) !important;
        }
        
        /* 3. Clear Affordances - Hover States */
        .stButton > button:not(:disabled):hover,
        button[data-baseweb="button"]:not(:disabled):hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 3px 6px rgba(0,0,0,0.2) !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton > button:not(:disabled):active,
        button[data-baseweb="button"]:not(:disabled):active {
            transform: translateY(0) !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.15) !important;
        }
        
        /* 4. Input Field Feedback */
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div:focus {
            border-color: #495057 !important;
            box-shadow: 0 0 0 2px rgba(73, 80, 87, 0.1) !important;
        }
        
        .stTextInput > div > div > input:hover,
        .stTextArea > div > div > textarea:hover,
        .stSelectbox > div > div:hover {
            border-color: #adb5bd !important;
        }
        
        /* 5. Clear Disabled States */
        .stButton > button:disabled,
        button[data-baseweb="button"]:disabled {
            opacity: 0.5 !important;
            cursor: not-allowed !important;
            transform: none !important;
        }
        
        /* 6. Better Contrast for Accessibility */
        .stMarkdown, p, span, div, label {
            color: #212529 !important;
        }
        
        /* 7. Clear Interactive Elements */
        [data-testid="stExpander"]:hover .streamlit-expanderHeader {
            background-color: #e9ecef !important;
            cursor: pointer !important;
        }
        
        /* 8. Loading States - Spinner Visibility */
        .stSpinner > div {
            border-color: #495057 !important;
            border-top-color: transparent !important;
        }
        
        /* 9. Better Empty States */
        .stEmpty, .stInfo:empty {
            padding: 1rem !important;
            text-align: center !important;
            color: #6c757d !important;
        }
        
        /* 10. Form Validation Feedback */
        .stTextInput > div > div > input:invalid,
        .stTextArea > div > div > textarea:invalid {
            border-color: #dc3545 !important;
        }
        
        /* 11. Clear Clickable Areas - Minimum Touch Target */
        .stButton > button,
        button[data-baseweb="button"],
        .stDownloadButton > button {
            min-height: 2rem !important;
            min-width: 2.5rem !important;
        }
        
        /* 12. Better Table/DataFrame Readability */
        .stDataFrame table {
            border-collapse: collapse !important;
        }
        
        .stDataFrame th {
            background-color: #f8f9fa !important;
            font-weight: 600 !important;
            border-bottom: 2px solid #dee2e6 !important;
        }
        
        .stDataFrame td {
            border-bottom: 1px solid #e9ecef !important;
        }
        
        .stDataFrame tr:hover {
            background-color: #f8f9fa !important;
        }
        
        /* 13. Improved Metrics Display */
        [data-testid="stMetricContainer"] {
            border: 1px solid #e9ecef !important;
            border-radius: 4px !important;
            padding: 0.5rem !important;
            background-color: #f8f9fa !important;
        }
        
        /* 14. Better Progress Indicators */
        [data-testid="stProgressBar"] > div > div {
            background-color: #495057 !important;
        }
        
        /* 15. Clear Section Separators */
        hr {
            border-top: 1px solid #dee2e6 !important;
            margin: 0.75rem 0 !important;
        }
        
        /* 16. Improved Alert/Message Visibility */
        .stAlert {
            border-left-width: 3px !important;
            border-left-style: solid !important;
        }
        
        .stSuccess {
            border-left-color: #28a745 !important;
        }
        
        .stError {
            border-left-color: #dc3545 !important;
        }
        
        .stWarning {
            border-left-color: #ffc107 !important;
        }
        
        .stInfo {
            border-left-color: #17a2b8 !important;
        }
        
        /* 17. Better Tab Navigation */
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #f8f9fa !important;
        }
        
        .stTabs [aria-selected="true"] {
            border-bottom: 2px solid #495057 !important;
            font-weight: 600 !important;
        }
        
        /* 18. Improved File Uploader Affordance */
        .stFileUploader:hover {
            border-color: #495057 !important;
            background-color: #f8f9fa !important;
        }
        
        /* 19. Better Checkbox/Radio Visibility */
        .stCheckbox label,
        .stRadio label {
            cursor: pointer !important;
            user-select: none !important;
        }
        
        /* 20. Better Link/Clickable Text */
        a, [role="link"] {
            color: #495057 !important;
            text-decoration: underline !important;
            cursor: pointer !important;
        }
        
        a:hover, [role="link"]:hover {
            color: #212529 !important;
        }
        
        /* 22. Improved Code Block Readability */
        .stCodeBlock, code, pre {
            background-color: #f8f9fa !important;
            border: 1px solid #e9ecef !important;
            color: #212529 !important;
        }
        
        /* 23. Better JSON Display */
        [data-testid="stJson"] {
            background-color: #f8f9fa !important;
            border: 1px solid #e9ecef !important;
            border-radius: 4px !important;
            padding: 0.5rem !important;
        }
        
        /* 24. Clear Visual Feedback for Actions */
        .stButton > button:not(:disabled) {
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }
        
        /* 25. Improved Spacing for Readability */
        .stMarkdown p {
            line-height: 1.5 !important;
        }
        
        /* 26. Better List Styling */
        ul, ol {
            padding-left: 1.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        li {
            margin-bottom: 0.25rem !important;
            line-height: 1.5 !important;
        }
        
        /* 27. Improved Caption Readability */
        .stCaption {
            color: #6c757d !important;
            font-style: italic !important;
        }
        
        /* 28. Better Tooltip Visibility */
        [title], [data-tooltip] {
            cursor: help !important;
        }
        
        /* 29. Clear Visual Grouping */
        .stContainer {
            border: 1px solid #e9ecef !important;
            border-radius: 4px !important;
            padding: 0.75rem !important;
            background-color: #ffffff !important;
        }
        
        /* 30. Improved Scrollbar Styling (where applicable) */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #adb5bd;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #868e96;
        }
        
        /* 31. Better Form Layout */
        .stForm {
            background-color: #ffffff !important;
            border: 1px solid #e9ecef !important;
            border-radius: 4px !important;
            padding: 1rem !important;
        }
        
        /* 32. Improved Data Editor */
        [data-testid="stDataEditor"] {
            border: 1px solid #e9ecef !important;
            border-radius: 4px !important;
        }
        
        /* 33. Better Metric Cards */
        [data-testid="stMetricValue"] {
            font-weight: 600 !important;
            color: #212529 !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #6c757d !important;
            font-weight: 500 !important;
        }
        
        /* 34. Clear Visual States for Validation */
        [data-testid="stDataFrame"] tr[data-status="error"] {
            background-color: #fff5f5 !important;
        }
        
        [data-testid="stDataFrame"] tr[data-status="warning"] {
            background-color: #fffbf0 !important;
        }
        
        [data-testid="stDataFrame"] tr[data-status="success"] {
            background-color: #f0fff4 !important;
        }
        
        /* 35. Better Mobile Responsiveness */
        @media (max-width: 768px) {
            .stButton > button {
                width: 100% !important;
                margin-bottom: 0.5rem !important;
            }
        }
        
        /* 36. Improved Loading Spinner */
        .stSpinner {
            color: #495057 !important;
        }
        
        /* 37. Better Placeholder Text */
        input::placeholder,
        textarea::placeholder {
            color: #adb5bd !important;
            opacity: 1 !important;
        }
        
        /* 38. Clear Visual Hierarchy in Cards */
        .summary-cards-wrapper [data-testid="column"] {
            transition: box-shadow 0.2s ease !important;
        }
        
        .summary-cards-wrapper [data-testid="column"]:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
        }
        
        /* 39. Better Error Message Styling */
        .stError {
            background-color: #fff5f5 !important;
            border-left-color: #dc3545 !important;
        }
        
        /* 40. Improved Success Message Styling */
        .stSuccess {
            background-color: #f0fff4 !important;
            border-left-color: #28a745 !important;
        }
        
        /* 41. Better Warning Message Styling */
        .stWarning {
            background-color: #fffbf0 !important;
            border-left-color: #ffc107 !important;
        }
        
        /* 42. Improved Info Message Styling */
        .stInfo {
            background-color: #e7f3ff !important;
            border-left-color: #17a2b8 !important;
        }
        
        /* 43. Better Required Field Indicators (handled via label styling) */
        
        /* 44. Better Pagination Controls */
        .stButton > button:disabled {
            opacity: 0.4 !important;
        }
        
        /* 45. Improved Sidebar Styling */
        [data-testid="stSidebar"] {
            border-right: 1px solid #e9ecef !important;
        }
        
        /* 46. Better Toggle/Switch Visibility */
        .stCheckbox input[type="checkbox"]:checked + label::before {
            background-color: #495057 !important;
        }
        
        /* 47. Clear Visual Separation for Sections */
        .stMarkdown h2,
        .stMarkdown h3 {
            border-bottom: 1px solid #e9ecef !important;
            padding-bottom: 0.25rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* 48. Better Slider Visibility */
        [data-testid="stSlider"] {
            margin: 0.5rem 0 !important;
        }
        
        /* 49. Improved Date/Time Input Styling */
        [data-testid="stDateInput"] > div,
        [data-testid="stTimeInput"] > div {
            border: 1px solid #ddd !important;
            border-radius: 4px !important;
        }
        
        /* 50. Better Multiselect Display */
        [data-testid="stMultiSelect"] > div > div {
            min-height: 2.5rem !important;
        }
        
        /* Ensure no gradient colors in any elements */
        [style*="gradient"], [style*="linear-gradient"] {
            background: #f5f5f5 !important;
            background-image: none !important;
        }
        
        /* Override ui_styling.py conflicting styles - enforce consistent neutral theme */
        .stButton > button,
        button[data-baseweb="button"],
        .stDownloadButton > button {
            background-color: #6c757d !important;
            color: white !important;
            border: 1px solid #5a6268 !important;
            border-radius: 4px !important;
            padding: 0.375rem 0.75rem !important;
            font-weight: 500 !important;
            font-size: 13px !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
        }
        
        .stButton > button:hover,
        button[data-baseweb="button"]:hover,
        .stDownloadButton > button:hover {
            background-color: #5a6268 !important;
            color: white !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
        }
        
        .stButton > button:disabled,
        button[data-baseweb="button"]:disabled {
            background-color: #c6c8ca !important;
            color: #6c757d !important;
            cursor: not-allowed !important;
        }
        
        /* Consistent status boxes - neutral gray theme */
        div[style*="background-color:#fdecea"],
        div[style*="background-color:#fff3cd"],
        div[style*="background-color:#d1ecf1"],
        div[style*="background-color:#d4edda"] {
            background-color: #f5f5f5 !important;
            border: 1px solid #ddd !important;
            color: #000000 !important;
        }
        
        div[style*="color: #b02a37"],
        div[style*="color: #856404"],
        div[style*="color: #0c5460"],
        div[style*="color: #155724"] {
            color: #000000 !important;
        }
        
        /* Consistent activity log styling */
        div[style*="background-color: #f5f5f5"] {
            background-color: #f5f5f5 !important;
            border: 1px solid #ddd !important;
        }
        
        /* Override expander styles for consistency */
        .streamlit-expanderHeader {
            background-color: #f5f5f5 !important;
            border: 1px solid #ddd !important;
            border-radius: 4px !important;
            padding: 0.5rem 0.75rem !important;
            font-size: 13px !important;
            font-weight: 500 !important;
        }
        
        .streamlit-expanderContent {
            padding: 0.5rem 0.75rem !important;
            background-color: #ffffff !important;
            border: 1px solid #ddd !important;
            border-top: none !important;
            border-radius: 0 0 4px 4px !important;
        }
        
        /* Consistent input field styling */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            border: 1px solid #ddd !important;
            border-radius: 4px !important;
            padding: 0.375rem 0.5rem !important;
            font-size: 13px !important;
            background-color: white !important;
        }
        
        /* Fix selectbox labels - ensure they're not cut off */
        .stSelectbox label,
        .stTextInput label,
        .stTextArea label,
        .stNumberInput label,
        .stMultiselect label,
        .stDateInput label,
        .stTimeInput label {
            font-size: 13px !important;
            line-height: 1.4 !important;
            padding-bottom: 0.25rem !important;
            margin-bottom: 0.25rem !important;
            white-space: normal !important;
            word-wrap: break-word !important;
            overflow: visible !important;
            height: auto !important;
            min-height: auto !important;
        }
        
        /* Ensure selectbox container has enough space */
        .stSelectbox > div,
        .stTextInput > div,
        .stTextArea > div,
        .stNumberInput > div,
        .stMultiselect > div,
        .stDateInput > div,
        .stTimeInput > div {
            margin-bottom: 0.5rem !important;
            min-height: auto !important;
        }
        
        /* Fix selectbox dropdown itself */
        .stSelectbox > div > div > div {
            min-height: 2rem !important;
            padding: 0.375rem 0.5rem !important;
            font-size: 13px !important;
        }
        
        /* Ensure multiselect has proper sizing */
        [data-testid="stMultiSelect"] > div {
            min-height: 2rem !important;
        }
        
        [data-testid="stMultiSelect"] label {
            font-size: 13px !important;
            line-height: 1.4 !important;
            padding-bottom: 0.25rem !important;
            white-space: normal !important;
        }
        
        /* Consistent tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #f5f5f5 !important;
            border-bottom: 1px solid #ddd !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: transparent !important;
            color: #000000 !important;
            font-size: 13px !important;
            padding: 0.5rem 1rem !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: white !important;
            color: #000000 !important;
            font-weight: 600 !important;
            border-bottom: 2px solid #666 !important;
        }
        
        /* Consistent file uploader */
        .stFileUploader {
            border: 1px dashed #ddd !important;
            border-radius: 4px !important;
            background-color: #fafafa !important;
            padding: 0.5rem !important;
        }
        
        /* Remove all colored borders and backgrounds from status indicators */
        div[style*="border-left: 3px solid"] {
            border-left: 2px solid #999 !important;
        }
        
        /* Consistent summary cards */
        .summary-cards-wrapper [data-testid="column"] {
            background: white !important;
            border: 1px solid #ddd !important;
            border-radius: 4px !important;
            padding: 0.75rem !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        }
        
        /* Override any large font sizes in status messages */
        strong[style*="font-size: 1.2rem"],
        strong[style*="font-size"] {
            font-size: 1rem !important;
        }
        
        /* Consistent padding for all status boxes */
        div[style*="padding: 1.5rem"] {
            padding: 0.75rem 1rem !important;
        }
        
        /* Ensure all inline styles respect our font sizes */
        [style*="font-size"] {
            font-size: 13px !important;
        }
        
        [style*="font-size: 0.85rem"],
        [style*="font-size: 0.75rem"],
        [style*="font-size: 0.7rem"] {
            font-size: 12px !important;
        }
        
        [style*="font-size: 1.2rem"],
        [style*="font-size: 1.1rem"] {
            font-size: 1rem !important;
        }
        
        /* Consistent colors - remove all bright colors */
        [style*="color: #b02a37"],
        [style*="color: #721c24"],
        [style*="color: #856404"],
        [style*="color: #0c5460"],
        [style*="color: #155724"] {
            color: #000000 !important;
        }
        
        /* Make all colored backgrounds neutral */
        [style*="background-color:#fdecea"],
        [style*="background-color:#fff3cd"],
        [style*="background-color:#d1ecf1"],
        [style*="background-color:#d4edda"] {
            background-color: #f5f5f5 !important;
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

# Handle refresh flag at the start
if st.session_state.get("needs_refresh", False):
    st.session_state.needs_refresh = False
    st.rerun()

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
                    track_feature_usage("file_upload", "layout_file_uploaded", {"file": layout_file_name.name})
                except NameError:
                    pass  # Function not available yet
                st.session_state.last_logged_layout_file = layout_file_name.name
                add_recent_file(layout_file_name.name, "layout", {})
    
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
                    track_feature_usage("file_upload", "claims_file_uploaded", {"file": claims_file_name.name, "rows": row_count})
                except NameError:
                    pass  # Function not available yet
                st.session_state.last_logged_claims_file = claims_file_name.name
                add_recent_file(claims_file_name.name, "claims", {"rows": row_count, "columns": col_count})
    
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
                    track_feature_usage("file_upload", "lookup_file_uploaded", {"file": lookup_file_name.name})
                except NameError:
                    pass  # Function not available yet
                st.session_state.last_logged_lookup_file = lookup_file_name.name
                add_recent_file(lookup_file_name.name, "lookup", {"msk": msk_count, "bar": bar_count})
    
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
    # Cache frequently accessed session state values
    layout_df = st.session_state.get("layout_df")
    claims_df = st.session_state.get("claims_df")
    final_mapping = st.session_state.get("final_mapping", {})

    if layout_df is None or claims_df is None:
        render_empty_state(
            icon="📁",
            title="Files Required",
            message="Please upload both layout and claims files to begin mapping.",
            action_label="Go to Setup Tab",
            action_callback=lambda: st.session_state.setdefault("active_tab", "Setup")
        )
        st.stop()
    
    # --- Sticky Mapping Progress Bar ---
    # Cache required fields calculation to avoid recomputing on every rerun
    if layout_df is not None:
        cache_key = f"required_fields_{id(layout_df)}"
        if cache_key not in st.session_state:
            # Normalize Usage column once and cache
            # Note: Layout uses "Mandatory" (capitalized), so we check for "mandatory" when lowercased
            usage_normalized = layout_df["Usage"].astype(str).str.strip().str.lower()
            required_fields = layout_df[usage_normalized == "mandatory"]["Internal Field"].tolist()  # type: ignore[no-untyped-call]
            st.session_state[cache_key] = required_fields
        else:
            required_fields = st.session_state[cache_key]
    else:
        required_fields = []
    
    total_required = len(required_fields) if required_fields else 0
    mapped_required = [f for f in required_fields if f in final_mapping and final_mapping[f].get("value")]
    mapped_count = len(mapped_required)
    percent_complete = int((mapped_count / total_required) * 100) if total_required > 0 else 0

    progress_html = render_progress_bar(percent_complete, f"{mapped_count} / {total_required} fields mapped ({percent_complete}%)")
    st.markdown(
        f'<div style="position: sticky; top: 0; background: #f5f5f5; color: #000000; z-index: 999; padding: 0.5rem 1rem; border-radius: 4px; margin-bottom: 0.5rem; box-shadow: 0 1px 2px rgba(0,0,0,0.1); border: 1px solid #ddd;"><b style="font-size: 0.875rem; color: #000000;">📌 Required Field Mapping Progress</b>{progress_html}</div>',
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
                # final_mapping already cached above
                
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
                        # Use dict() constructor for shallow copy of dict structure (faster than deepcopy)
                        # v is always dict[str, Any] based on type, but check for safety
                        st.session_state.final_mapping = {k: dict(v) for k, v in undone.items()}
                        # Clear auto_mapping to force refresh
                        if "auto_mapping" in st.session_state:
                            del st.session_state.auto_mapping
                        # Get field name for feedback
                        field_name = list(undone.keys())[0] if undone else None
                        show_undo_redo_feedback("Undone", field_name)
                        st.session_state.needs_refresh = True
                
                if st.button("↷ Redo", key="redo_btn", use_container_width=True, disabled=not can_redo, help="Redo last undone change (Ctrl+Y)"):
                    redone = redo_mapping()
                    if redone is not None:
                        # Use dict() constructor for shallow copy of dict structure (faster than deepcopy)
                        # v is always dict[str, Any] based on type, but check for safety
                        st.session_state.final_mapping = {k: dict(v) for k, v in redone.items()}
                        # Clear auto_mapping to force refresh
                        if "auto_mapping" in st.session_state:
                            del st.session_state.auto_mapping
                        # Get field name for feedback
                        field_name = list(redone.keys())[0] if redone else None
                        show_undo_redo_feedback("Redone", field_name)
                        st.session_state.needs_refresh = True
            
        with col2:
            st.markdown("**Bulk Actions**")
            ai_suggestions = st.session_state.get("auto_mapping", {})
            # final_mapping already cached above
            if st.button("✅ Accept All AI (≥80%)", key="bulk_accept_ai", use_container_width=True):
                accepted = 0
                for field, info in ai_suggestions.items():
                    score = info.get("score", 0)
                    if score >= AI_CONFIDENCE_THRESHOLD and (field not in final_mapping or not final_mapping[field].get("value")):
                        final_mapping[field] = {"mode": "auto", "value": info["value"]}
                        accepted += 1
                if accepted > 0:
                    st.session_state.final_mapping = final_mapping
                    save_to_history(final_mapping)
                    show_toast(f"Accepted {accepted} AI suggestions!", "✅")
                    st.session_state.needs_refresh = True
            if st.button("🔄 Clear All", key="bulk_clear", use_container_width=True):
                if show_confirmation_dialog(
                    "Clear All Mappings",
                    "⚠️ Are you sure you want to clear all mappings? This action cannot be undone.",
                    confirm_label="Yes, Clear All",
                    cancel_label="Cancel",
                    key="clear_all_confirm"
                ):
                    final_mapping.clear()
                    st.session_state.final_mapping = {}
                    save_to_history({})
                    show_toast("All mappings cleared!", "🔄")
                    log_event("mapping", "Cleared all mappings")
                    st.session_state.needs_refresh = True
        
        with col3:
            st.markdown("**Utilities**")
            if st.button("📋 Copy Mapping", key="bulk_copy", use_container_width=True):
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
                                show_toast(f"Template loaded: {selected_template}", "✅")
                                log_event("template", f"Loaded mapping template: {selected_template}")
                                st.session_state.needs_refresh = True
                    else:
                        st.info("No saved templates")

    # --- Mapping Enhancements Section ---
    with st.expander("🔧 Mapping Tools & Enhancements", expanded=False):
        # Mapping Validation
        if st.button("Validate Mapping Before Processing", key="validate_mapping_btn"):
            is_valid, errors = validate_mapping_before_processing(final_mapping, layout_df, claims_df)
            if is_valid:
                st.success("✅ Mapping is valid and ready for processing!")
            else:
                st.error("❌ Mapping validation failed:")
                for error in errors:
                    st.error(f"- {error}")
        
        # Mapping Confidence Scores
        ai_suggestions_tab2 = st.session_state.get("auto_mapping", {})
        if ai_suggestions_tab2:
            confidence_scores = get_mapping_confidence_score(final_mapping, ai_suggestions_tab2)
            st.markdown("#### Mapping Confidence Scores")
            confidence_df = pd.DataFrame(list(confidence_scores.items()), columns=["Field", "Confidence"])
            confidence_df["Confidence"] = (confidence_df["Confidence"] * 100).round(1)
            st.dataframe(confidence_df, use_container_width=True)
        
        # Mapping Version Control
        st.markdown("#### Mapping Version Control")
        mapping_version = get_mapping_version(final_mapping)
        st.code(f"Current Version: {mapping_version}")
        
        # Export/Import for Sharing
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export Mapping for Sharing", key="export_mapping_share"):
                shareable = export_mapping_template_for_sharing(final_mapping, {
                    "name": "Current Mapping",
                    "description": "Exported mapping",
                    "author": "User"
                })
                st.download_button("Download Shareable Template",
                                 json.dumps(shareable, indent=2).encode('utf-8'),
                                 "mapping_template_shareable.json",
                                 "application/json",
                                 key="download_shareable")
        
        with col2:
            uploaded_template = st.file_uploader("Import Shareable Template",
                                                type=["json"],
                                                key="import_shareable_template")
            if uploaded_template:
                try:
                    template_data = json.load(uploaded_template)
                    imported_mapping, metadata = import_mapping_template_from_shareable(template_data)
                    if st.button("Apply Imported Mapping", key="apply_imported"):
                        st.session_state.final_mapping = imported_mapping
                        show_toast(f"Imported mapping from: {metadata.get('name', 'Unknown')}", "✅")
                        st.session_state.needs_refresh = True
                except Exception as e:
                    error_msg = get_user_friendly_error(e)
                    st.error(f"Error importing template: {error_msg}")
    
    # --- Main Mapping Section ---
    st.markdown("#### Manual Field Mapping")
    # Gate heavy mapping updates behind a form submit to avoid recomputation on every rerun
    with st.form("mapping_form"):
        render_field_mapping_tab()
        apply_mappings = st.form_submit_button("Apply Mappings")
        if apply_mappings:
            st.session_state["mappings_ready"] = True
            # Save to history when form is submitted
            # final_mapping already cached above
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
                
                # Automatically run unit tests in the background when mappings are applied
                try:
                    tests = create_mapping_unit_tests(final_mapping, claims_df, layout_df)
                    test_results = run_unit_tests(tests)
                    st.session_state.unit_test_results = test_results
                except Exception as e:
                    # Silently fail - tests will be available when user clicks button
                        pass

    st.divider()
    
    # --- Test Mapping Section (Auto-run only, results shown in Tools & Analytics tab) ---
    if st.session_state.get("mappings_ready") and final_mapping:
        # Check if we need to run tests (if mappings changed or tests don't exist)
        mapping_hash = str(hash(str(final_mapping)))
        last_hash = st.session_state.get("last_mapping_hash")
        
        # Run tests automatically if mappings changed or tests don't exist
        if last_hash != mapping_hash or not st.session_state.get("unit_test_results"):
            # Run tests automatically in background
            try:
                tests = create_mapping_unit_tests(final_mapping, claims_df, layout_df)
                test_results = run_unit_tests(tests)
                st.session_state.unit_test_results = test_results
                st.session_state.last_mapping_hash = mapping_hash
            except Exception as e:
                # Silently fail - tests will be available in Tools & Analytics tab
                pass

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
            # Read edited table and update final_mapping using vectorized operations
            # Use itertuples for better performance than iterrows
            updated_mapping: Dict[str, Dict[str, Any]] = final_mapping.copy()  # Start with existing mappings
            
            # Process edited rows using itertuples (faster than iterrows)
            for row in edited_df.itertuples(index=False):
                internal_field = str(row[0])  # Internal Field column
                source_col = str(row[1]).strip() if pd.notna(row[1]) else ""  # Source Column column
                
                # Only update mapping if source column is provided
                if source_col and source_col != "":
                    # Preserve existing mode if field was already mapped, otherwise set to manual
                    existing_mapping = updated_mapping.get(internal_field, {})
                    mode = existing_mapping.get("mode", "manual")
                    
                    # If source column changed, mark as manual
                    if existing_mapping.get("value") != source_col:
                        mode = "manual"
                    
                    updated_mapping[internal_field] = {
                        "mode": mode,
                        "value": source_col
                    }
                elif internal_field in updated_mapping:
                    # If source column is empty, remove the mapping
                    del updated_mapping[internal_field]
            
            # Update session state (merge with existing, don't overwrite)
            st.session_state.final_mapping = updated_mapping
            
            # Save to history
            if updated_mapping:
                save_to_history(updated_mapping)
            
            # Regenerate outputs
            if claims_df is not None and updated_mapping:
                st.session_state.transformed_df = transform_claims_data(claims_df, updated_mapping)
                generate_all_outputs()
                
                # Automatically run unit tests when mappings are updated
                try:
                    tests = create_mapping_unit_tests(updated_mapping, claims_df, layout_df)
                    test_results = run_unit_tests(tests)
                    st.session_state.unit_test_results = test_results
                    st.session_state.last_mapping_hash = str(hash(str(updated_mapping)))
                except Exception:
                    # Silently fail - tests will be available when user clicks button
                    pass
            
            st.success("✅ Mappings updated successfully!")
            # Only log manual mappings (exclude AI auto-mapped fields)
            manual_mapped_count = len([f for f in updated_mapping.keys() 
                                     if updated_mapping[f].get("value") and updated_mapping[f].get("mode") == "manual"])
            if manual_mapped_count > 0:
                try:
                    log_event("mapping", f"Manual mappings updated via review table ({manual_mapped_count} fields mapped)")
                except NameError:
                    pass
            show_toast("Mappings updated successfully!", "✅")
            st.session_state.needs_refresh = True

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
            
            with st.expander("📋 Auto-Mapped Fields (≥80% confidence) - Click to Override", expanded=False):
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
                                show_toast(f"Override applied for {field}", "✅")
                                st.session_state.needs_refresh = True
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
                    # final_mapping already cached in tab scope
                    if claims_df is not None and final_mapping:
                        st.session_state.transformed_df = transform_claims_data(claims_df, final_mapping)
                        st.session_state["transformed_ready"] = True

    else:
        render_empty_state(
            icon="🤖",
            title="No AI Suggestions",
            message="No additional AI mapping suggestions available. All fields may already be mapped or AI confidence is below threshold."
        )

with tab3:
    # Cache frequently accessed session state values
    transformed_df = st.session_state.get("transformed_df")
    final_mapping = st.session_state.get("final_mapping", {})
    layout_df = st.session_state.get("layout_df")

    if transformed_df is None or not final_mapping:
        render_empty_state(
            icon="📋",
            title="Mapping Required",
            message="Please complete field mappings and preview transformed data first.",
            action_label="Go to Field Mapping Tab",
            action_callback=lambda: st.session_state.setdefault("active_tab", "Field Mapping")
        )
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
                start_time = time.time()
                field_level_results = run_validations(transformed_df, required_fields, all_mapped_internal_fields)
                
                # Run file-level validations (summary/aggregate checks)
                file_level_results = dynamic_run_validations(transformed_df, final_mapping)
                
                # Combine both types of validation results
                validation_results = field_level_results + file_level_results
                execution_time = time.time() - start_time
                
                # Track validation performance
                track_validation_performance("full_validation", execution_time, len(transformed_df), len(validation_results))
                
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
    
    # validation_results already set above in the validation block
    if "validation_results" not in st.session_state:
        validation_results: List[Dict[str, Any]] = []
    else:
        validation_results = st.session_state.validation_results

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
                show_toast(f"Custom rule '{rule_name}' added!", "✅")
                st.session_state.needs_refresh = True
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
                        show_toast("Custom rule removed", "🗑️")
                        st.session_state.needs_refresh = True
            
            # Run custom validations
            if st.button("Run Custom Validations", key="run_custom_validations"):
                if transformed_df is not None:
                    custom_results = run_custom_validations(transformed_df, custom_rules)
                    # Add to validation results
                    validation_results.extend(custom_results)
                    st.session_state.validation_results = validation_results
                    show_toast(f"Ran {len(custom_results)} custom validation(s)", "✅")
                    st.session_state.needs_refresh = True

    st.divider()

    # --- Detailed Validation Table ---
    st.markdown("#### Detailed Validation Results")
    if validation_results:
        # Add pagination for large result sets
        if len(validation_results) > DEFAULT_VALIDATION_PAGE_SIZE:
            default_index = VALIDATION_PAGE_SIZES.index(DEFAULT_VALIDATION_PAGE_SIZE) if DEFAULT_VALIDATION_PAGE_SIZE in VALIDATION_PAGE_SIZES else 1
            page_size = st.selectbox("Results per page:", VALIDATION_PAGE_SIZES, index=default_index, key="validation_page_size")
            paginated_results, page_num, total_pages = paginate_dataframe(
                pd.DataFrame(validation_results),
                page_size=page_size
            )
            st.caption(f"Page {page_num} of {total_pages} ({len(validation_results)} total results)")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Previous", key="prev_validation_page", disabled=page_num == 1):
                    st.session_state.validation_page_num = max(1, page_num - 1)
                if st.button("Next →", key="next_validation_page", disabled=page_num == total_pages):
                    st.session_state.validation_page_num = min(total_pages, page_num + 1)
            
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
            # layout_df and final_mapping already cached above
            
            # Extract required fields from layout (use cached version if available)
            if layout_df is None:
                required_fields_tab3: List[str] = []
            else:
                # Use cached required fields if available
                cache_key_tab3 = f"required_fields_{id(layout_df)}"
                if cache_key_tab3 in st.session_state:
                    required_fields_tab3 = st.session_state[cache_key_tab3]
                else:
                    usage_normalized = layout_df["Usage"].astype(str).str.strip().str.lower()
                    required_fields_tab3 = layout_df[usage_normalized == "mandatory"]["Internal Field"].tolist()  # type: ignore[no-untyped-call]
                    st.session_state[cache_key_tab3] = required_fields_tab3
            
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
                    <div style='background-color:#f5f5f5; padding: 0.75rem 1rem; border-radius: 4px; margin-bottom: 0.5rem; border: 1px solid #ddd;'>
                    <strong style='color: #000000; font-size: 1rem;'>❌ File Status: Rejected</strong>
                    <p style='color: #000000; margin-top: 0.25rem; margin-bottom: 0; font-size: 13px;'>Mandatory fields are missing from the file.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif has_critical_issues:
                st.markdown(
                    """
                    <div style='background-color:#f5f5f5; padding: 0.75rem 1rem; border-radius: 4px; margin-bottom: 0.5rem; border: 1px solid #ddd;'>
                    <strong style='color: #000000; font-size: 1rem;'>⚠️ File Status: Needs Review</strong>
                    <p style='color: #000000; margin-top: 0.25rem; margin-bottom: 0; font-size: 13px;'>Some required fields have high null rates that exceed recommended thresholds.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            elif has_warnings:
                st.markdown(
                    """
                    <div style='background-color:#f5f5f5; padding: 0.75rem 1rem; border-radius: 4px; margin-bottom: 0.5rem; border: 1px solid #ddd;'>
                    <strong style='color: #000000; font-size: 1rem;'>ℹ️ File Status: Approved with Warnings</strong>
                    <p style='color: #000000; margin-top: 0.25rem; margin-bottom: 0; font-size: 13px;'>File meets requirements but has some data quality issues to review.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """
                    <div style='background-color:#f5f5f5; padding: 0.75rem 1rem; border-radius: 4px; margin-bottom: 0.5rem; border: 1px solid #ddd;'>
                    <strong style='color: #000000; font-size: 1rem;'>✅ File Status: Approved</strong>
                    <p style='color: #000000; margin-top: 0.25rem; margin-bottom: 0; font-size: 13px;'>All validation checks passed. File is ready for processing.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # --- Detailed Status Summary (Collapsible Sections) ---
            
            # Mandatory Fields Status (Collapsible)
            with st.expander("📋 Mandatory Fields Status", expanded=False):
                if unmapped_required_fields_tab3:
                    field_list = ", ".join(f"`{f}`" for f in unmapped_required_fields_tab3)
                    st.error(f"**Missing Fields:** {field_list}")
                    st.caption("These mandatory fields must be present in the source file and properly mapped.")
                else:
                    st.success(f"✅ All {len(required_fields_tab3)} required fields are mapped and available in the file.")
            
            # Required Fields Analysis (Collapsible)
            if required_field_null_stats:
                with st.expander("📊 Mandatory Fields Analysis", expanded=False):
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
                    
                    # Use double newlines for proper line breaks in markdown
                    st.markdown("\n\n".join(breakdown_items))
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
                with st.expander("❌ Rejection Explanation", expanded=False):
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
            if show_confirmation_dialog(
                "Clear Activity Log",
                "Are you sure you want to clear the activity log? This action cannot be undone.",
                confirm_label="Yes, Clear",
                cancel_label="Cancel",
                key="clear_activity_confirm"
            ):
                st.session_state.audit_log = []
                show_toast("Activity log cleared", "🗑️")
                st.session_state.needs_refresh = True
    else:
        st.info("No activity logged yet. Events will appear here as you use the app.")
    
    st.divider()

    # Cache frequently accessed session state values
    final_mapping = st.session_state.get("final_mapping", {})
    if not final_mapping:
        st.info("Complete required field mappings to generate outputs.")
    else:
        layout_df = st.session_state.get("layout_df")
        claims_df = st.session_state.get("claims_df")
        anonymized_df = st.session_state.get("anonymized_df")
        mapping_table = st.session_state.get("mapping_table")
        transformed_df = st.session_state.get("transformed_df")

        if any(x is None for x in [anonymized_df, mapping_table, transformed_df]):
            st.warning("Outputs not fully generated yet. Please complete mapping and preview steps.")
        else:
            # --- Anonymized Claims File Section ---
            with st.expander("Anonymized Claims Preview", expanded=False):
                # anonymized_df already cached above
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
                            # claims_df and final_mapping already cached above
                            if claims_df is not None:
                                st.session_state.anonymized_df = anonymize_claims_data(
                                    claims_df,
                                    final_mapping
                                )
                            _notify("✅ Anonymized file regenerated!")

            # --- Field Mapping Table Section ---
            with st.expander("Field Mapping Table Preview", expanded=False):
                mapping_table = st.session_state.get("mapping_table")
                
                # Generate CSV for download (needed in both branches)
                mapping_csv = mapping_table.to_csv(index=False).encode('utf-8')  # type: ignore[no-untyped-call]
                
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
                        if st.button("Next →", key="next_mapping_table", disabled=page_num * table_page_size >= len(mapping_table)):
                            st.session_state.mapping_table_page = page_num + 1
                    
                    st.dataframe(paginated_table, use_container_width=True)  # type: ignore[no-untyped-call]
                else:
                    st.dataframe(mapping_table, use_container_width=True)  # type: ignore[no-untyped-call]
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
                                # layout_df, claims_df, and final_mapping already cached above
                                if layout_df is not None and claims_df is not None:
                                    st.session_state.mapping_table = generate_mapping_table(
                                        layout_df,
                                        final_mapping,
                                        claims_df
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
                        # claims_df, layout_df, and final_mapping already cached above
                        if claims_df is not None:
                            st.session_state.anonymized_df = anonymize_claims_data(claims_df, final_mapping)
                        if layout_df is not None and claims_df is not None:
                            st.session_state.mapping_table = generate_mapping_table(layout_df, final_mapping, claims_df)
                        _notify("✅ All outputs regenerated!")
                        show_toast("All outputs regenerated!", "✅")
                        st.session_state.needs_refresh = True

# --- Tab 5: Data Quality & Analysis ---
with tab5:
    st.markdown("## 📊 Data Quality & Analysis")
    
    # Cache frequently accessed session state values
    claims_df_tab5 = st.session_state.get("claims_df")
    layout_df_tab5 = st.session_state.get("layout_df")
    
    if claims_df_tab5 is None or claims_df_tab5.empty:
        render_empty_state(
            icon="📊",
            title="No Data Available",
            message="Upload a claims file to analyze data quality.",
            action_label="Go to Setup Tab",
            action_callback=lambda: st.session_state.setdefault("active_tab", "Setup")
        )
    else:
        # Data Quality Score
        st.markdown("### Overall Data Quality Score")
        required_fields_tab5 = []
        if layout_df_tab5 is not None and "Usage" in layout_df_tab5.columns:
            required_fields_tab5 = layout_df_tab5[
                layout_df_tab5["Usage"].astype(str).str.lower() == "mandatory"
            ]["Internal Field"].tolist()
        
        quality_score = calculate_data_quality_score(claims_df_tab5, required_fields_tab5)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Overall Score", f"{quality_score['overall_score']:.1f}/100")
        with col2:
            st.metric("Completeness", f"{quality_score['breakdown'].get('completeness', 0):.1f}%")
        with col3:
            st.metric("Uniqueness", f"{quality_score['breakdown'].get('uniqueness', 0):.1f}%")
        with col4:
            st.metric("Consistency", f"{quality_score['breakdown'].get('consistency', 0):.1f}%")
        
        # Data Profiling
        with st.expander("📈 Data Profile", expanded=False):
            profile = generate_data_profile(claims_df_tab5)
            st.json(profile)
        
        # Column Statistics
        st.markdown("### Column Statistics")
        selected_col = st.selectbox("Select column to analyze", claims_df_tab5.columns.tolist(), key="col_stats_select")
        if selected_col:
            col_stats = get_column_statistics(claims_df_tab5, selected_col)
            st.json(col_stats)
        
        # Duplicate Detection
        with st.expander("🔍 Duplicate Detection", expanded=False):
            dup_method = st.selectbox("Detection Method", ["exact", "key_based"], key="dup_method")
            dup_columns = st.multiselect("Columns to check", claims_df_tab5.columns.tolist(), key="dup_columns")
            if st.button("Detect Duplicates", key="detect_dups"):
                if dup_columns:
                    duplicates = detect_duplicates(claims_df_tab5, dup_columns, dup_method)
                    if not duplicates.empty:
                        st.dataframe(duplicates, use_container_width=True)
                        st.info(f"Found {len(duplicates)} duplicate records")
                    else:
                        st.success("No duplicates found!")
        
        # Outlier Detection
        numeric_cols = claims_df_tab5.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            with st.expander("📊 Outlier Detection", expanded=False):
                outlier_col = st.selectbox("Select numeric column", numeric_cols, key="outlier_col")
                outlier_method = st.selectbox("Method", ["zscore", "iqr"], key="outlier_method")
                outlier_threshold = st.slider("Threshold", 1.0, 5.0, 3.0, 0.1, key="outlier_threshold")
                if st.button("Detect Outliers", key="detect_outliers"):
                    outliers = detect_outliers(claims_df_tab5, outlier_col, outlier_method, outlier_threshold)
                    if not outliers.empty:
                        st.dataframe(outliers, use_container_width=True)
                        st.info(f"Found {len(outliers)} outliers")
                    else:
                        st.success("✅ No outliers detected!")
        
        # Completeness Matrix
        with st.expander("📋 Data Completeness Matrix", expanded=False):
            completeness_matrix = create_completeness_matrix(claims_df_tab5)
            st.dataframe(completeness_matrix, use_container_width=True)
        
        # Data Sampling
        with st.expander("🎲 Data Sampling", expanded=False):
            sample_method = st.selectbox("Sampling Method", ["random", "first", "last"], key="sample_method")
            sample_size = st.number_input("Sample Size", 100, min(10000, len(claims_df_tab5)), 1000, key="sample_size")
            if st.button("Generate Sample", key="generate_sample"):
                sample_df = sample_data(claims_df_tab5, sample_method, sample_size)
                st.dataframe(sample_df, use_container_width=True)
                st.download_button("Download Sample", 
                                 sample_df.to_csv(index=False).encode('utf-8'),
                                 "sample_data.csv",
                                 "text/csv",
                                 key="download_sample")

# --- Tab 6: Tools & Analytics ---
with tab6:
    st.markdown("## 🛠️ Tools & Analytics")
    
    # Sub-tabs for different tool categories
    tool_tab1, tool_tab2, tool_tab3, tool_tab4 = st.tabs([
        "System Health",
        "Usage Analytics",
        "Testing & QA",
        "Help & Documentation"
    ])
    
    with tool_tab1:
        st.markdown("### 💻 System Health")
        
        health = get_system_health()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("CPU Usage", f"{health.get('cpu_percent', 0):.1f}%")
        with col2:
            st.metric("Memory Usage", f"{health.get('memory_mb', 0):.0f} MB")
        with col3:
            st.metric("Memory %", f"{health.get('memory_percent', 0):.1f}%")
        with col4:
            st.metric("Threads", health.get('threads', 0))
        
        # Error Statistics
        st.markdown("### ⚠️ Error Statistics")
        error_stats = get_error_statistics()
        st.json(error_stats)
        
        # Export Logs
        st.markdown("### 📥 Export Logs")
        log_type = st.selectbox("Log Type", ["audit", "error", "usage"], key="export_log_type")
        log_format = st.selectbox("Format", ["json", "csv"], key="export_log_format")
        if st.button("Export Logs", key="export_logs"):
            log_data = export_logs(log_type, log_format)
            st.download_button("Download", log_data.encode('utf-8'),
                             f"{log_type}_log.{log_format}",
                             "text/plain" if log_format == "json" else "text/csv",
                             key="download_logs")
    
    with tool_tab2:
        st.markdown("### 📊 Usage Analytics")
        
        usage_stats = get_usage_statistics()
        
        st.metric("Total Actions", usage_stats.get("total_actions", 0))
        
        st.markdown("#### Features Used")
        features_used = usage_stats.get("features_used", {})
        if features_used:
            features_df = pd.DataFrame(list(features_used.items()), columns=["Feature", "Count"])
            st.bar_chart(features_df.set_index("Feature"))
        else:
            st.info("No usage data yet")
        
        # Validation Performance
        st.markdown("### ⚡ Validation Performance")
        perf_stats = get_validation_performance_stats()
        st.json(perf_stats)
    
    with tool_tab3:
        st.markdown("### 🧪 Testing & Quality Assurance")
        
        # Test Data Generator
        with st.expander("Generate Test Data", expanded=False):
            claims_df = st.session_state.get("claims_df")
            layout_df = st.session_state.get("layout_df")
            
            if claims_df is None and layout_df is None:
                st.info("Please upload a claims file or layout file first to generate test data based on its structure.")
            else:
                test_data_type = st.selectbox("Data Type", 
                    [opt for opt in ["claims", "layout"] if (opt == "claims" and claims_df is not None) or (opt == "layout" and layout_df is not None)],
                    key="test_data_type")
                test_data_count = st.number_input("Record Count", 10, 10000, 100, key="test_data_count")
                
                if st.button("Generate Test Data", key="generate_test_data"):
                    test_df = None
                    if test_data_type == "claims" and claims_df is not None:
                        # Replicate claims file structure with dummy data
                        test_df = generate_test_data_from_claims(claims_df, test_data_count)
                    elif test_data_type == "layout" and layout_df is not None:
                        # Replicate layout schema with dummy data
                        test_df = generate_test_data_from_layout(layout_df, test_data_count)
                    else:
                        st.error("Unable to generate test data. Please ensure the required file is uploaded.")
                        st.stop()
                    
                    if test_df is not None:
                        st.dataframe(test_df, use_container_width=True)
                        st.download_button("Download Test Data",
                                         test_df.to_csv(index=False).encode('utf-8'),
                                         f"test_{test_data_type}.csv",
                                         "text/csv",
                                         key="download_test_data")
        
        # Unit Test Results - shows background test results
        st.markdown("#### 🧪 Unit Test Results")
        st.caption("Unit tests run automatically when mappings are applied. Results are shown below.")
        
        final_mapping = st.session_state.get("final_mapping", {})
        mappings_ready = st.session_state.get("mappings_ready", False)
        
        if not mappings_ready or not final_mapping:
            st.info("Complete your field mappings first. Tests will run automatically when mappings are applied.")
        else:
            unit_test_results = st.session_state.get("unit_test_results")
            if unit_test_results:
                # Summary metrics
                total = unit_test_results.get("total", 0)
                passed = unit_test_results.get("passed", 0)
                failed = unit_test_results.get("failed", 0)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Tests", total)
                with col2:
                    st.metric("Passed", passed, delta=f"{int((passed/total*100) if total > 0 else 0)}%")
                with col3:
                    st.metric("Failed", failed, delta=f"{int((failed/total*100) if total > 0 else 0)}%")
                
                # Re-run button
                if st.button("🔄 Re-run Tests", key="rerun_tests_tools_tab", use_container_width=True):
                    with st.spinner("Running unit tests..."):
                        try:
                            claims_df = st.session_state.get("claims_df")
                            layout_df = st.session_state.get("layout_df")
                            tests = create_mapping_unit_tests(final_mapping, claims_df, layout_df)
                            test_results = run_unit_tests(tests)
                            st.session_state.unit_test_results = test_results
                            st.session_state.last_mapping_hash = str(hash(str(final_mapping)))
                            st.success(f"Tests completed: {test_results['passed']}/{test_results['total']} passed")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error running tests: {e}")
                
                st.divider()
                
                # Detailed results
                if unit_test_results.get("test_results"):
                    st.markdown("##### Detailed Results")
                    for result in unit_test_results["test_results"]:
                        test_name = result.get("name", "Unknown")
                        passed_status = result.get("passed", False)
                        icon = "✅" if passed_status else "❌"
                        st.markdown(f"{icon} **{test_name}**")
                        if not passed_status:
                            error = result.get("error", "")
                            expected = result.get("expected", "")
                            actual = result.get("actual", "")
                            if error:
                                st.error(f"Error: {error}")
                            else:
                                st.warning(f"Expected: {expected}, Got: {actual}")
            else:
                st.info("Unit tests are running automatically. Results will appear here once mappings are applied.")
    
    with tool_tab4:
        st.markdown("### 📚 Help & Documentation")
        
        help_topic = st.selectbox("Select Topic", 
                                 ["file_upload", "mapping", "validation", "outputs"],
                                 key="help_topic")
        
        help_content = get_help_content(help_topic)
        if help_content:
            st.markdown(help_content)
        
        # Global Search
        st.markdown("### 🔍 Global Search")
        search_query = st.text_input("Search across all tabs", key="global_search_input")
        if search_query:
            search_results = global_search(search_query)
            for scope, results in search_results.items():
                if results:
                    st.markdown(f"#### {scope.title()}")
                    st.write(results)
        
        # Notification Center
        st.markdown("### 🔔 Notification Center")
        notifications = get_notifications(unread_only=True)
        if notifications:
            for i, notif in enumerate(notifications[:10]):
                severity = notif.get("severity", "info")
                if severity == "error":
                    st.error(f"{notif.get('message', '')}")
                elif severity == "warning":
                    st.warning(f"{notif.get('message', '')}")
                elif severity == "success":
                    st.success(f"{notif.get('message', '')}")
                else:
                    st.info(f"{notif.get('message', '')}")
                
                if st.button("Mark as Read", key=f"read_notif_{i}"):
                    mark_notification_read(i)
                    show_toast("Notification marked as read", "✅")
                    st.session_state.needs_refresh = True
        else:
            st.info("No unread notifications")
        
        if st.button("Clear All Notifications", key="clear_notifications"):
            if show_confirmation_dialog(
                "Clear All Notifications",
                "Are you sure you want to clear all notifications?",
                confirm_label="Yes, Clear",
                cancel_label="Cancel",
                key="clear_notifications_confirm"
            ):
                clear_notifications()
                show_toast("All notifications cleared", "🗑️")
                st.session_state.needs_refresh = True
