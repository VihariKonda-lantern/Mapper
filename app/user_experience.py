# --- user_experience.py ---
"""User Experience enhancements."""
import streamlit as st
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

st: Any = st


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
    limit = st.session_state.user_preferences.get("recent_files_limit", 10)
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


def create_onboarding_step(step_id: str, title: str, content: str, 
                          target_element: Optional[str] = None) -> Dict[str, Any]:
    """Create an onboarding tutorial step.
    
    Args:
        step_id: Unique step identifier
        title: Step title
        content: Step content/instructions
        target_element: Optional target element selector
        
    Returns:
        Step dictionary
    """
    return {
        "id": step_id,
        "title": title,
        "content": content,
        "target_element": target_element
    }


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

