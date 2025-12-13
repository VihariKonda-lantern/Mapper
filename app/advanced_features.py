# --- advanced_features.py ---
"""Advanced features: keyboard shortcuts, dark mode, templates, etc."""
import streamlit as st
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import pandas as pd

st: Any = st
pd: Any = pd


def init_dark_mode() -> None:
    """Initialize dark mode toggle in session state."""
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False


def toggle_dark_mode() -> None:
    """Toggle dark mode."""
    st.session_state.dark_mode = not st.session_state.dark_mode


def get_dark_mode_css() -> str:
    """Get CSS for dark mode with improved readability."""
    if st.session_state.get("dark_mode", False):
        return """
        <style>
        /* Main app background - lighter gray for better visibility */
        .stApp {
            background-color: #1e1e1e !important;
            color: #e0e0e0 !important;
        }
        
        /* Main content area */
        .main .block-container {
            background-color: #1e1e1e !important;
            color: #e0e0e0 !important;
        }
        
        /* All text elements */
        .stMarkdown, .stText, p, span, div, label, h1, h2, h3, h4, h5, h6 {
            color: #e0e0e0 !important;
        }
        
        /* Headers */
        [data-testid="stHeader"] {
            background-color: #2d2d2d !important;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #252525 !important;
        }
        
        /* Sidebar text */
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div {
            color: #e0e0e0 !important;
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select {
            background-color: #2d2d2d !important;
            color: #e0e0e0 !important;
            border-color: #404040 !important;
        }
        
        /* Selectboxes and dropdowns */
        .stSelectbox label,
        .stTextInput label,
        .stTextArea label {
            color: #e0e0e0 !important;
        }
        
        /* Buttons - All Grey */
        .stButton > button,
        button[data-baseweb="button"],
        .stDownloadButton > button,
        button[type="button"],
        button[type="submit"] {
            background-color: #6b7280 !important;
            color: white !important;
            border-color: #4b5563 !important;
        }
        
        .stButton > button:hover,
        button[data-baseweb="button"]:hover,
        .stDownloadButton > button:hover,
        button[type="button"]:hover,
        button[type="submit"]:hover {
            background-color: #4b5563 !important;
            color: white !important;
        }
        
        /* Primary buttons - also grey */
        .stButton > button[kind="primary"],
        button[kind="primary"],
        button[data-baseweb="button"][kind="primary"] {
            background-color: #6b7280 !important;
            color: white !important;
        }
        
        .stButton > button[kind="primary"]:hover,
        button[kind="primary"]:hover,
        button[data-baseweb="button"][kind="primary"]:hover {
            background-color: #4b5563 !important;
            color: white !important;
        }
        
        /* Disabled buttons */
        .stButton > button:disabled,
        button[data-baseweb="button"]:disabled,
        .stDownloadButton > button:disabled {
            background-color: #9ca3af !important;
            color: white !important;
            opacity: 0.6 !important;
        }
        
        /* Dataframes */
        .stDataFrame {
            background-color: #2d2d2d !important;
            color: #e0e0e0 !important;
        }
        
        /* Tables */
        table {
            background-color: #2d2d2d !important;
            color: #e0e0e0 !important;
        }
        
        table th {
            background-color: #3d3d3d !important;
            color: #e0e0e0 !important;
        }
        
        table td {
            background-color: #2d2d2d !important;
            color: #e0e0e0 !important;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            background-color: #2d2d2d !important;
            color: #e0e0e0 !important;
        }
        
        /* Info/Warning/Error boxes */
        .stAlert {
            background-color: #2d2d2d !important;
            border-color: #404040 !important;
        }
        
        .stAlert p, .stAlert div {
            color: #e0e0e0 !important;
        }
        
        /* Code blocks */
        code, pre {
            background-color: #2d2d2d !important;
            color: #e0e0e0 !important;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #e0e0e0 !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #b0b0b0 !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            background-color: #2d2d2d !important;
            color: #e0e0e0 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #3d3d3d !important;
            color: #e0e0e0 !important;
        }
        
        /* File uploader */
        .stFileUploader {
            background-color: #2d2d2d !important;
            border-color: #404040 !important;
        }
        
        .stFileUploader label {
            color: #e0e0e0 !important;
        }
        
        /* Checkboxes and radio buttons */
        .stCheckbox label,
        .stRadio label {
            color: #e0e0e0 !important;
        }
        
        /* Dividers */
        hr {
            border-color: #404040 !important;
        }
        
        /* Summary cards */
        .summary-cards-wrapper {
            background-color: transparent !important;
        }
        
        /* Custom cards */
        [class*="card"], [class*="Card"] {
            background-color: #2d2d2d !important;
            color: #e0e0e0 !important;
            border-color: #404040 !important;
        }
        </style>
        """
    return ""


def inject_keyboard_shortcuts() -> None:
    """Inject JavaScript for keyboard shortcuts."""
    shortcuts_js = """
    <script>
    document.addEventListener('keydown', function(e) {
        // Ctrl+S or Cmd+S: Save mapping
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const saveBtn = document.querySelector('[data-testid="baseButton-secondary"][aria-label*="Save"]');
            if (saveBtn) saveBtn.click();
        }
        
        // Ctrl+Z: Undo
        if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
            e.preventDefault();
            const undoBtn = document.querySelector('[data-testid="baseButton-secondary"][aria-label*="Undo"]');
            if (undoBtn) undoBtn.click();
        }
        
        // Ctrl+Y or Ctrl+Shift+Z: Redo
        if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
            e.preventDefault();
            const redoBtn = document.querySelector('[data-testid="baseButton-secondary"][aria-label*="Redo"]');
            if (redoBtn) redoBtn.click();
        }
        
        // Ctrl+A: Apply All Mappings
        if ((e.ctrlKey || e.metaKey) && e.key === 'a' && !e.shiftKey) {
            e.preventDefault();
            const applyAllBtn = document.querySelector('button:has-text("Accept All AI")');
            if (applyAllBtn) applyAllBtn.click();
        }
        
        // Ctrl+Shift+C: Clear All
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
            e.preventDefault();
            const clearAllBtn = document.querySelector('button:has-text("Clear All")');
            if (clearAllBtn) clearAllBtn.click();
        }
        
        // Ctrl+D: Download
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            const downloadBtn = document.querySelector('[data-testid="baseButton-secondary"][aria-label*="Download"]');
            if (downloadBtn) downloadBtn.click();
        }
        
        // Ctrl+ArrowRight: Next Tab
        if ((e.ctrlKey || e.metaKey) && e.key === 'ArrowRight') {
            e.preventDefault();
            const tabs = document.querySelectorAll('[data-baseweb="tab"]');
            const activeTab = document.querySelector('[data-baseweb="tab"][aria-selected="true"]');
            if (activeTab && tabs.length > 0) {
                const currentIndex = Array.from(tabs).indexOf(activeTab);
                if (currentIndex < tabs.length - 1) {
                    tabs[currentIndex + 1].click();
                }
            }
        }
        
        // Ctrl+ArrowLeft: Previous Tab
        if ((e.ctrlKey || e.metaKey) && e.key === 'ArrowLeft') {
            e.preventDefault();
            const tabs = document.querySelectorAll('[data-baseweb="tab"]');
            const activeTab = document.querySelector('[data-baseweb="tab"][aria-selected="true"]');
            if (activeTab && tabs.length > 0) {
                const currentIndex = Array.from(tabs).indexOf(activeTab);
                if (currentIndex > 0) {
                    tabs[currentIndex - 1].click();
                }
            }
        }
        
        // Ctrl+F: Focus Search
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            const searchInput = document.querySelector('input[placeholder*="Search"], input[placeholder*="search"]');
            if (searchInput) searchInput.focus();
        }
    });
    </script>
    """
    st.markdown(shortcuts_js, unsafe_allow_html=True)


def save_mapping_template(mapping: Dict[str, Any], filename: str = None) -> str:
    """Save mapping as a template file."""
    if filename is None:
        filename = f"mapping_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    template = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "mapping": mapping
    }
    
    templates_dir = "templates"
    os.makedirs(templates_dir, exist_ok=True)
    filepath = os.path.join(templates_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(template, f, indent=2)
    
    return filepath


def load_mapping_template(filepath: str) -> Optional[Dict[str, Any]]:
    """Load a mapping template from file."""
    try:
        with open(filepath, 'r') as f:
            template = json.load(f)
        return template.get("mapping", template)
    except Exception:
        return None


def list_saved_templates() -> List[str]:
    """List all saved mapping templates."""
    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        return []
    
    templates = []
    for filename in os.listdir(templates_dir):
        if filename.endswith('.json'):
            templates.append(os.path.join(templates_dir, filename))
    
    return sorted(templates, reverse=True)  # Most recent first


def export_validation_results_csv(validation_results: List[Dict[str, Any]]) -> bytes:
    """Export validation results as CSV."""
    df = pd.DataFrame(validation_results)
    return df.to_csv(index=False).encode('utf-8')


def export_validation_results_excel(validation_results: List[Dict[str, Any]]) -> bytes:
    """Export validation results as Excel."""
    import io
    df = pd.DataFrame(validation_results)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Validation Results')
    return output.getvalue()


def bulk_map_similar_fields(
    claims_df: Any,
    internal_fields: List[str],
    pattern: str = None,
    field_type: str = None
) -> Dict[str, str]:
    """Bulk map fields based on pattern or type."""
    suggestions = {}
    source_columns = claims_df.columns.tolist()
    
    for internal_field in internal_fields:
        best_match = None
        best_score = 0
        
        # Pattern-based matching
        if pattern:
            import re
            pattern_lower = pattern.lower()
            for col in source_columns:
                if pattern_lower in col.lower():
                    score = len(pattern_lower) / len(col)
                    if score > best_score:
                        best_score = score
                        best_match = col
        
        # Type-based matching
        elif field_type:
            for col in source_columns:
                if field_type.lower() in col.lower():
                    score = 0.5
                    if score > best_score:
                        best_score = score
                        best_match = col
        
        # Fuzzy matching fallback
        else:
            import difflib
            for col in source_columns:
                score = difflib.SequenceMatcher(None, internal_field.lower(), col.lower()).ratio()
                if score > best_score and score > 0.6:
                    best_score = score
                    best_match = col
        
        if best_match:
            suggestions[internal_field] = best_match
    
    return suggestions

