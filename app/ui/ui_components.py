# --- ui_components.py ---
"""Reusable UI components and user experience utilities.
Consolidates functionality from ui_improvements.py and user_experience.py."""
import streamlit as st
from typing import Any, Optional, Callable, Dict, List
import time
import json
import os
from datetime import datetime
from core.state_manager import SessionStateManager

st: Any = st


def render_tooltip(text: str, help_text: str, key: Optional[str] = None) -> None:
    """Render text with a tooltip (enhanced version).
    
    Args:
        text: Text to display
        help_text: Tooltip text
        key: Optional unique key
    """
    tooltip_key = key or f"tooltip_{hash(text)}"
    st.markdown(f"""
    <div class="tooltip-wrapper" style="display: inline-block;">
        <span>{text}</span>
        <span class="tooltip-text" style="visibility: hidden; opacity: 0; transition: opacity 0.3s;">
            {help_text}
        </span>
    </div>
    """, unsafe_allow_html=True)


def render_status_indicator(status: str) -> str:
    """Generate HTML for status indicator."""
    status_class = {
        "mapped": "status-mapped",
        "unmapped": "status-unmapped",
        "suggested": "status-suggested"
    }.get(status, "status-unmapped")
    return f'<span class="status-indicator {status_class}"></span>'


def render_progress_bar(percent: int, label: str = "", text_color: Optional[str] = None) -> str:
    """Generate HTML for animated progress bar with consistent styling."""
    from ui.design_system import DesignTokens
    tokens = DesignTokens
    text_color = text_color or tokens.COLORS['text']
    # Extract values to avoid nested quotes in f-strings
    spacing_sm = tokens.SPACING['sm']
    background_alt = tokens.COLORS['background-alt']
    radius_full = tokens.RADIUS['full']
    color_primary = tokens.COLORS['primary']
    font_size_sm = tokens.FONT_SIZES['sm']
    return (
        f'<div class="progress-container" style="margin-top: {spacing_sm}; margin-bottom: {spacing_sm}; '
        f'background-color: {background_alt}; border-radius: {radius_full}; '
        f'height: 8px; overflow: hidden;"><div style="width: {percent}%; background: {color_primary} !important; '
        f'height: 100%; border-radius: {radius_full}; transition: width 0.5s ease;"></div></div>'
        f'<small style="color: {text_color}; font-size: {font_size_sm}; display: block; margin-top: {spacing_sm};">{label}</small>'
    )


def render_title():
    """Renders the app title with consistent styling."""
    from ui.design_system import DesignTokens
    tokens = DesignTokens
    # Extract values to avoid nested quotes in f-strings
    font_size_2xl = tokens.FONT_SIZES['2xl']
    font_weight_semibold = tokens.FONT_WEIGHTS['semibold']
    spacing_md = tokens.SPACING['md']
    color_text = tokens.COLORS['text']
    st.markdown(
        f"<div style='font-size: {font_size_2xl}; font-weight: {font_weight_semibold}; margin-bottom: {spacing_md}; color: {color_text};'>Claims File Mapper and Validator</div>",
        unsafe_allow_html=True
    )


def _notify(msg: str) -> None:
    """Show a toast notification."""
    st.toast(msg)


def show_action_feedback(
    action: str,
    success: bool = True,
    message: Optional[str] = None,
    duration: int = 2
) -> None:
    """Show immediate visual feedback for actions."""
    from ui.progress_indicators import show_action_feedback as _show_action_feedback
    _show_action_feedback(action, success, message, duration)


def show_progress_with_status(message: str, total_steps: int = 100):
    """Context manager for showing progress with status updates."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    class ProgressContext:
        def __init__(self, pb: Any, st: Any, total: int):
            self.progress_bar = pb
            self.status_text = st
            self.total = total
            self.current = 0
        
        def update(self, step: int, status: str = ""):
            self.current = step
            progress = min(100, int((step / self.total) * 100))
            self.progress_bar.progress(progress)
            if status:
                self.status_text.text(status)
        
        def complete(self, message: str = "Complete!"):
            self.progress_bar.progress(100)
            self.status_text.text(message)
            time.sleep(0.5)
            self.progress_bar.empty()
            self.status_text.empty()
    
    return ProgressContext(progress_bar, status_text, total_steps)


def confirm_action(message: str, key: str) -> bool:
    """Show a confirmation dialog for destructive actions."""
    if st.session_state.get(f"confirm_{key}", False):
        return True
    st.warning(message)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm", key=f"confirm_yes_{key}"):
            st.session_state[f"confirm_{key}"] = True
            st.session_state.needs_refresh = True
    with col2:
        if st.button("Cancel", key=f"confirm_no_{key}"):
            st.session_state[f"confirm_{key}"] = False
    return False


def render_quick_actions() -> None:
    """Render quick action buttons for common tasks in a collapsible expander."""
    with st.expander("Quick Actions", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Load Template", key="quick_load_template", use_container_width=True):
                st.session_state.active_tab = "Field Mapping"
                st.info("Go to Field Mapping tab to load a saved template")
        
        with col2:
            if st.button("Save Mapping", key="quick_save_mapping", use_container_width=True):
                mapping = SessionStateManager.get_final_mapping()
                if mapping:
                    show_toast("Mapping saved!", "")
                else:
                    st.warning("No mapping to save. Complete field mapping first.")
        
        with col3:
            if st.button("View Quality", key="quick_view_quality", use_container_width=True):
                st.session_state.active_tab = "Data Quality"
                st.rerun()
        
        with col4:
            if st.button("Reset All", key="quick_reset", use_container_width=True):
                if show_confirmation_dialog(
                    "Reset All Data",
                    "Are you sure you want to reset all data? This will clear all uploaded files and mappings.",
                    confirm_label="Yes, Reset",
                    cancel_label="Cancel",
                    key="reset_confirm"
                ):
                    # Clear session state
                    for key in list(st.session_state.keys()):
                        if key not in ["needs_refresh"]:
                            del st.session_state[key]
                    st.session_state.active_tab = "Setup"
                    show_toast("All data reset", "")
                    st.rerun()


# --- UI Improvements Functions (migrated from ui_improvements.py) ---

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


def show_toast(message: str, icon: str = "✅", duration: int = 3) -> None:
    """Show a toast notification."""
    try:
        st.toast(f"{icon} {message}", duration=duration)
    except Exception:
        # Fallback to success message
        st.success(message)


def show_undo_redo_feedback(action: str, field_name: Optional[str] = None) -> None:
    """Show feedback for undo/redo actions."""
    if field_name:
        show_toast(f"{action}: {field_name}", "↶" if action == "Undone" else "↷")
    else:
        show_toast(f"Action {action.lower()}", "↶" if action == "Undone" else "↷")


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


def show_onboarding_tour() -> None:
    """Show onboarding tour in the sidebar."""
    with st.sidebar:
        with st.expander("Welcome! Quick Tour", expanded=True):
            st.markdown("""
            ### 🚀 Welcome to Claims Mapper & Validator!
            
            **Transform your claims data with intelligent mapping and validation.**
            
            **📋 Your Workflow:**
            
            **1️⃣ Setup** → Upload your Layout, Lookup, and Claims files to get started
            
            **2️⃣ Field Mapping** → Let AI suggest mappings (≥80% confidence) or map manually. Our intelligent engine learns from your patterns.
            
            **3️⃣ Preview & Validate** → Review data quality, catch errors early, and ensure compliance before processing
            
            **4️⃣ Downloads** → Export anonymized claims, mapping tables, test data, and onboarding scripts in one click
            
            **💡 Pro Tips:**
            - **AI-Powered Mapping**: Accept suggestions with ≥80% confidence for instant mapping
            - **Batch Processing**: Process multiple files with the same mapping configuration
            - **Test Data Generation**: Create realistic test scenarios for validation
            
            **⌨️ Quick Actions:**
            - `Ctrl+Z` / `Ctrl+Y` → Undo/Redo your mapping changes
            - `Ctrl+F` → Quick search across fields
            """)


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


# --- User Experience Functions (migrated from user_experience.py) ---

def init_user_preferences() -> None:
    """Initialize user preferences in session state."""
    if "user_preferences" not in st.session_state:
        st.session_state.user_preferences = {
            "default_page_size": 100,
            "auto_save_mappings": True,
            "show_tooltips": True,
            "theme": "light",
            "notifications_enabled": True,
            "recent_files_limit": 10
        }


def save_user_preference(key: str, value: Any) -> None:
    """Save a user preference.
    
    Args:
        key: Preference key
        value: Preference value
    """
    init_user_preferences()
    st.session_state.user_preferences[key] = value
    
    # Persist to file
    try:
        prefs_file = "user_preferences.json"
        with open(prefs_file, 'w') as f:
            json.dump(st.session_state.user_preferences, f, indent=2)
    except Exception:
        pass  # Silently fail if can't write


def load_user_preferences() -> Dict[str, Any]:
    """Load user preferences from file.
    
    Returns:
        Preferences dictionary
    """
    init_user_preferences()
    
    try:
        prefs_file = "user_preferences.json"
        if os.path.exists(prefs_file):
            with open(prefs_file, 'r') as f:
                saved_prefs = json.load(f)
                st.session_state.user_preferences.update(saved_prefs)
    except Exception:
        pass  # Use defaults if can't load
    
    return st.session_state.user_preferences


def add_recent_file(file_path: str, file_type: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """Add a file to recent files list.
    
    Args:
        file_path: File path or name
        file_type: Type of file (layout, lookup, claims)
        metadata: Optional metadata
    """
    if "recent_files" not in st.session_state:
        st.session_state.recent_files = []
    
    recent_file = {
        "path": file_path,
        "type": file_type,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    # Remove duplicates
    st.session_state.recent_files = [
        f for f in st.session_state.recent_files 
        if not (f["path"] == file_path and f["type"] == file_type)
    ]
    
    # Add to front
    st.session_state.recent_files.insert(0, recent_file)
    
    # Limit size
    limit = st.session_state.user_preferences.get("recent_files_limit", 10) if "user_preferences" in st.session_state else 10
    st.session_state.recent_files = st.session_state.recent_files[:limit]


def get_recent_files(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get recent files list.
    
    Args:
        limit: Maximum number of files to return
        
    Returns:
        List of recent files
    """
    if "recent_files" not in st.session_state:
        return []
    
    files = st.session_state.recent_files
    if limit:
        files = files[:limit]
    
    return files


def add_favorite(item_type: str, item_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """Add an item to favorites/bookmarks.
    
    Args:
        item_type: Type of item (mapping, template, validation_rule)
        item_id: Item identifier
        metadata: Optional metadata
    """
    if "favorites" not in st.session_state:
        st.session_state.favorites = []
    
    favorite = {
        "type": item_type,
        "id": item_id,
        "added_at": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    # Check if already favorited
    if not any(f["type"] == item_type and f["id"] == item_id for f in st.session_state.favorites):
        st.session_state.favorites.append(favorite)


def remove_favorite(item_type: str, item_id: str) -> None:
    """Remove an item from favorites.
    
    Args:
        item_type: Type of item
        item_id: Item identifier
    """
    if "favorites" not in st.session_state:
        return
    
    st.session_state.favorites = [
        f for f in st.session_state.favorites 
        if not (f["type"] == item_type and f["id"] == item_id)
    ]


def get_favorites(item_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get favorites list.
    
    Args:
        item_type: Optional filter by type
        
    Returns:
        List of favorites
    """
    if "favorites" not in st.session_state:
        return []
    
    favorites = st.session_state.favorites
    if item_type:
        favorites = [f for f in favorites if f["type"] == item_type]
    
    return favorites


def add_notification(notification_type: str, message: str, 
                    severity: str = "info", persistent: bool = False) -> None:
    """Add a notification to the notification center.
    
    Args:
        notification_type: Type of notification
        message: Notification message
        severity: Severity level (info, warning, error, success)
        persistent: Whether notification should persist
    """
    if "notifications" not in st.session_state:
        st.session_state.notifications = []
    
    notification = {
        "type": notification_type,
        "message": message,
        "severity": severity,
        "timestamp": datetime.now().isoformat(),
        "persistent": persistent,
        "read": False
    }
    
    st.session_state.notifications.insert(0, notification)
    
    # Limit size
    if len(st.session_state.notifications) > 50:
        st.session_state.notifications = st.session_state.notifications[:50]


def get_notifications(unread_only: bool = False) -> List[Dict[str, Any]]:
    """Get notifications.
    
    Args:
        unread_only: Only return unread notifications
        
    Returns:
        List of notifications
    """
    if "notifications" not in st.session_state:
        return []
    
    notifications = st.session_state.notifications
    if unread_only:
        notifications = [n for n in notifications if not n.get("read", False)]
    
    return notifications


def mark_notification_read(notification_index: int) -> None:
    """Mark a notification as read.
    
    Args:
        notification_index: Index of notification
    """
    if "notifications" not in st.session_state:
        return
    
    if 0 <= notification_index < len(st.session_state.notifications):
        st.session_state.notifications[notification_index]["read"] = True


def clear_notifications() -> None:
    """Clear all notifications."""
    st.session_state.notifications = []


def get_help_content(topic: str) -> Optional[str]:
    """Get help content for a topic.
    
    Args:
        topic: Topic identifier
        
    Returns:
        Help content string or None
    """
    help_content = {
        "file_upload": """
# File Upload Help

## Supported File Types
- **Layout File**: Excel (.xlsx) or CSV files containing field definitions
- **Lookup File**: Excel or CSV files with diagnosis code mappings
- **Claims File**: CSV, TXT, TSV, or Excel files with claims data

## Tips
- Files can be headerless - the app will detect this automatically
- For fixed-width files, upload a header specification file
- Maximum file size: 200MB per file
        """,
        "mapping": """
# Field Mapping Help

## How Mapping Works
1. Required fields are shown first
2. AI suggestions appear automatically (≥80% confidence)
3. You can manually override any mapping
4. Use search to quickly find fields

## Best Practices
- Review AI suggestions before accepting
- Map all required fields before proceeding
- Use the review table to adjust multiple mappings at once
        """,
        "validation": """
# Validation Help

## Validation Types
- **Field-level**: Checks individual field values
- **File-level**: Checks overall file quality
- **Custom Rules**: User-defined validation rules

## Understanding Results
- ✅ Pass: Validation check passed
- ⚠️ Warning: Issue detected but not critical
- ❌ Fail: Critical issue requiring attention
        """,
        "outputs": """
# Outputs Help

## Available Outputs
- **Anonymized Claims**: De-identified claims data
- **Mapping Table**: Complete field mapping documentation
- **Validation Report**: Detailed validation results
- **ZIP Archive**: All outputs bundled together

## Download Options
- Individual file downloads
- Complete ZIP archive
- Custom notes can be included in README
        """
    }
    
    return help_content.get(topic)


def global_search(query: str, search_scope: List[str] = None) -> Dict[str, List[Any]]:
    """Perform global search across all tabs.
    
    Args:
        query: Search query
        search_scope: List of scopes to search (None = all)
        
    Returns:
        Dictionary with search results by scope
    """
    if search_scope is None:
        search_scope = ["mappings", "validations", "files", "templates"]
    
    results = {}
    
    # Search mappings
    if "mappings" in search_scope:
        mapping = st.session_state.get("final_mapping", {})
        matching_fields = [
            field for field in mapping.keys() 
            if query.lower() in field.lower()
        ]
        results["mappings"] = matching_fields
    
    # Search validations
    if "validations" in search_scope:
        validation_results = st.session_state.get("validation_results", [])
        matching_validations = [
            v for v in validation_results
            if query.lower() in str(v).lower()
        ]
        results["validations"] = matching_validations
    
    # Search files
    if "files" in search_scope:
        recent_files = get_recent_files()
        matching_files = [
            f for f in recent_files
            if query.lower() in f.get("path", "").lower()
        ]
        results["files"] = matching_files
    
    # Search templates
    if "templates" in search_scope:
        # Would need to load templates from storage
        results["templates"] = []
    
    return results

