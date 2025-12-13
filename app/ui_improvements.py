# --- ui_improvements.py ---
"""UI/UX improvement components."""
import streamlit as st
from typing import Any, Optional, Callable, Dict, List
from datetime import datetime

st: Any = st


# --- Confirmation Dialog ---
def show_confirmation_dialog(
    title: str,
    message: str,
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel",
    on_confirm: Optional[Callable] = None,
    on_cancel: Optional[Callable] = None,
    key: Optional[str] = None
) -> bool:
    """Show a confirmation dialog."""
    dialog_key = f"confirm_dialog_{key}" if key else "confirm_dialog"
    
    if dialog_key not in st.session_state:
        st.session_state[dialog_key] = False
    
    if not st.session_state[dialog_key]:
        st.warning(f"**{title}**\n\n{message}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(confirm_label, key=f"{dialog_key}_confirm", use_container_width=True, type="primary"):
                st.session_state[dialog_key] = True
                if on_confirm:
                    on_confirm()
                return True
        with col2:
            if st.button(cancel_label, key=f"{dialog_key}_cancel", use_container_width=True):
                if on_cancel:
                    on_cancel()
                return False
        return False
    
    return True


# --- Toast Notification Wrapper ---
def show_toast(message: str, icon: str = "✅", duration: int = 3) -> None:
    """Show a toast notification."""
    try:
        st.toast(f"{icon} {message}", duration=duration)
    except Exception:
        # Fallback to success message
        st.success(message)


# --- Undo/Redo Feedback ---
def show_undo_redo_feedback(action: str, field_name: Optional[str] = None) -> None:
    """Show feedback for undo/redo actions."""
    if field_name:
        show_toast(f"{action}: {field_name}", "↶" if action == "Undone" else "↷")
    else:
        show_toast(f"Action {action.lower()}", "↶" if action == "Undone" else "↷")


# --- Enhanced Tooltips ---
def render_tooltip(text: str, tooltip: str, key: Optional[str] = None) -> None:
    """Render text with a tooltip."""
    tooltip_key = key or f"tooltip_{hash(text)}"
    st.markdown(f"""
    <div class="tooltip-wrapper" style="display: inline-block;">
        <span>{text}</span>
        <span class="tooltip-text" style="visibility: hidden; opacity: 0; transition: opacity 0.3s;">
            {tooltip}
        </span>
    </div>
    """, unsafe_allow_html=True)


# --- Onboarding Tour ---
def show_onboarding_tour() -> None:
    """Show first-time user onboarding tour."""
    if "onboarding_completed" not in st.session_state:
        st.session_state.onboarding_completed = False
    
    if not st.session_state.onboarding_completed:
        with st.expander("🎯 Welcome! Quick Tour", expanded=False):
            st.markdown("""
            ### Welcome to Claims Mapper & Validator!
            
            **Getting Started:**
            1. **Setup Tab**: Upload your Layout, Lookup, and Claims files
            2. **Field Mapping Tab**: Map your source columns to required fields
            3. **Preview & Validate Tab**: Review validation results
            4. **Downloads Tab**: Download your processed files
            
            **Tips:**
            - Use AI suggestions (≥80% confidence) for faster mapping
            - Review validation results before downloading
            - Save mapping templates for reuse
            
            **Keyboard Shortcuts:**
            - `Ctrl+Z`: Undo
            - `Ctrl+Y`: Redo
            - `Ctrl+F`: Search fields
            """)
            
            if st.button("Got it! Start using the app", key="complete_onboarding"):
                st.session_state.onboarding_completed = True
                st.session_state.needs_refresh = True


# --- Contextual Help ---
def show_contextual_help(context: str) -> None:
    """Show contextual help based on current page/action."""
    help_content: Dict[str, str] = {
        "setup": """
        **Setup Tab Help:**
        - Upload Layout file: Defines required fields and their formats
        - Upload Lookup file: Contains reference data for validation
        - Upload Claims file: Your source data to be processed
        - All files are required before proceeding to mapping
        """,
        "mapping": """
        **Field Mapping Tab Help:**
        - Map each required field to a column in your claims file
        - AI suggestions appear automatically (≥80% confidence)
        - Use manual entry for fields not detected by AI
        - Review mapping progress at the top
        """,
        "validation": """
        **Preview & Validate Tab Help:**
        - Review validation results for data quality
        - Check mandatory fields status
        - Review warnings and errors
        - Custom validation rules can be added
        """,
        "downloads": """
        **Downloads Tab Help:**
        - Download anonymized claims file
        - Download mapping table
        - Download all outputs as ZIP
        - Customize file formats and names
        """
    }
    
    if context in help_content:
        with st.expander("ℹ️ Help", expanded=False):
            st.markdown(help_content[context])


# --- Enhanced Search & Filter ---
def render_enhanced_search(
    placeholder: str = "Search...",
    key: Optional[str] = None,
    debounce: bool = True
) -> str:
    """Render enhanced search with debouncing."""
    search_key = key or "enhanced_search"
    return st.text_input(
        "🔍 Search",
        placeholder=placeholder,
        key=search_key,
        help="Type to filter results (searches across all fields)"
    )


# --- Sortable Table Wrapper ---
def render_sortable_table(
    data: Any,
    sort_column: Optional[str] = None,
    sort_direction: str = "asc",
    key: Optional[str] = None
) -> None:
    """Render a table with sorting capabilities."""
    if data is None or (hasattr(data, 'empty') and data.empty):
        st.info("No data to display")
        return
    
    # Add sort controls
    if hasattr(data, 'columns'):
        col1, col2 = st.columns([3, 1])
        with col1:
            sort_col = st.selectbox(
                "Sort by:",
                options=["None"] + list(data.columns),
                key=f"{key}_sort_col" if key else "sort_col"
            )
        with col2:
            sort_dir = st.selectbox(
                "Direction:",
                options=["Ascending", "Descending"],
                key=f"{key}_sort_dir" if key else "sort_dir"
            )
        
        if sort_col != "None" and sort_col in data.columns:
            ascending = sort_dir == "Ascending"
            data = data.sort_values(by=sort_col, ascending=ascending)
    
    st.dataframe(data, use_container_width=True)


# --- Filterable Table ---
def render_filterable_table(
    data: Any,
    filter_columns: Optional[List[str]] = None,
    key: Optional[str] = None
) -> Any:
    """Render a table with filtering capabilities."""
    if data is None or (hasattr(data, 'empty') and data.empty):
        st.info("No data to display")
        return data
    
    if not hasattr(data, 'columns'):
        st.dataframe(data, use_container_width=True)
        return data
    
    if filter_columns is None:
        filter_columns = list(data.columns)[:5]  # Limit to first 5 columns
    
    filters = {}
    for col in filter_columns:
        if col in data.columns:
            unique_vals = data[col].dropna().unique().tolist()
            if len(unique_vals) <= 20:  # Only show filter if reasonable number of values
                selected = st.multiselect(
                    f"Filter {col}:",
                    options=unique_vals,
                    key=f"{key}_filter_{col}" if key else f"filter_{col}"
                )
                if selected:
                    filters[col] = selected
    
    # Apply filters
    filtered_data = data.copy()
    for col, values in filters.items():
        filtered_data = filtered_data[filtered_data[col].isin(values)]
    
    st.dataframe(filtered_data, use_container_width=True)
    return filtered_data


# --- Export Table View ---
def export_table_view(data: Any, filename: str = "table_export") -> bytes:
    """Export current table view to CSV."""
    if data is None:
        return b""
    
    if hasattr(data, 'to_csv'):
        return data.to_csv(index=False).encode('utf-8')
    
    return str(data).encode('utf-8')


# --- Drag & Drop File Upload ---
def render_drag_drop_upload(
    label: str,
    accept_types: List[str],
    key: Optional[str] = None,
    help_text: Optional[str] = None
) -> Any:
    """Render enhanced file upload with drag & drop styling."""
    st.markdown("""
    <style>
    .upload-area {
        border: 2px dashed #ddd;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        background-color: #fafafa;
        transition: all 0.3s ease;
    }
    .upload-area:hover {
        border-color: #495057;
        background-color: #f0f0f0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    return st.file_uploader(
        label,
        type=accept_types,
        key=key,
        help=help_text or "Drag and drop your file here or click to browse"
    )


# --- File Preview ---
def render_file_preview(file_obj: Any, max_rows: int = 10) -> None:
    """Preview file before processing."""
    if file_obj is None:
        return
    
    try:
        import pandas as pd
        file_name = file_obj.name.lower()
        
        if file_name.endswith('.csv') or file_name.endswith('.txt'):
            # Try to read as CSV
            df = pd.read_csv(file_obj, nrows=max_rows)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Preview of first {min(max_rows, len(df))} rows")
        elif file_name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_obj, nrows=max_rows)
            st.dataframe(df, use_container_width=True)
            st.caption(f"Preview of first {min(max_rows, len(df))} rows")
        else:
            st.info("File preview not available for this file type")
    except Exception as e:
        st.warning(f"Could not preview file: {str(e)}")


# --- Bookmark System ---
def save_bookmark(name: str, data: Dict[str, Any]) -> None:
    """Save a bookmark."""
    if "bookmarks" not in st.session_state:
        st.session_state.bookmarks = []
    
    bookmark = {
        "name": name,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    st.session_state.bookmarks.append(bookmark)
    
    # Keep only last 20 bookmarks
    if len(st.session_state.bookmarks) > 20:
        st.session_state.bookmarks = st.session_state.bookmarks[-20:]


def load_bookmark(name: str) -> Optional[Dict[str, Any]]:
    """Load a bookmark."""
    if "bookmarks" not in st.session_state:
        return None
    
    for bookmark in st.session_state.bookmarks:
        if bookmark["name"] == name:
            return bookmark["data"]
    
    return None


def list_bookmarks() -> List[Dict[str, Any]]:
    """List all bookmarks."""
    return st.session_state.get("bookmarks", [])


# --- Version Control Display ---
def render_version_history(versions: List[Dict[str, Any]]) -> None:
    """Render version history."""
    if not versions:
        st.info("No version history available")
        return
    
    for i, version in enumerate(versions):
        with st.expander(f"Version {i+1} - {version.get('timestamp', 'Unknown')}", expanded=False):
            st.json(version.get("data", {}))


# --- Comparison View ---
def render_comparison_view(data1: Any, data2: Any, label1: str = "Version 1", label2: str = "Version 2") -> None:
    """Render side-by-side comparison."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**{label1}**")
        if hasattr(data1, 'to_dict'):
            st.json(data1.to_dict())
        else:
            st.write(data1)
    
    with col2:
        st.markdown(f"**{label2}**")
        if hasattr(data2, 'to_dict'):
            st.json(data2.to_dict())
        else:
            st.write(data2)

