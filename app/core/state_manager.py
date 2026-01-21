# --- state_manager.py ---
"""Session state management with typed getters and setters."""
import streamlit as st
from typing import Any, Dict, List, Optional, TypedDict, cast
from datetime import datetime

st: Any = st


class SessionStateSchema(TypedDict, total=False):
    """Schema for session state structure."""
    # File data
    claims_df: Any
    layout_df: Any
    claims_file_obj: Any
    layout_file_obj: Any
    lookup_file_obj: Any
    claims_file_metadata: Dict[str, Any]
    
    # Mapping data
    final_mapping: Dict[str, Dict[str, Any]]
    mapping_history: List[Dict[str, Dict[str, Any]]]
    history_index: int
    
    # Processing data
    transformed_df: Any
    anonymized_df: Any
    mapping_table: Any
    validation_results: List[Dict[str, Any]]
    
    # Lookup data
    msk_codes: set
    bar_codes: set
    
    # UI state
    dark_mode: bool
    active_tab: str
    needs_refresh: bool
    
    # Audit and logging
    audit_log: List[Dict[str, Any]]
    error_log: List[Dict[str, Any]]
    
    # File tracking
    last_logged_layout_file: Optional[str]
    last_logged_claims_file: Optional[str]
    last_logged_lookup_file: Optional[str]
    
    # User preferences
    user_preferences: Dict[str, Any]
    
    # Notifications
    notifications: List[Dict[str, Any]]


class SessionStateManager:
    """Manages session state with typed access and validation."""
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get a value from session state with optional default.
        
        Args:
            key: Session state key
            default: Default value if key doesn't exist
            
        Returns:
            Value from session state or default
        """
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any) -> None:
        """Set a value in session state.
        
        Args:
            key: Session state key
            value: Value to set
        """
        st.session_state[key] = value
    
    @staticmethod
    def setdefault(key: str, default: Any) -> Any:
        """Set default value if key doesn't exist.
        
        Args:
            key: Session state key
            default: Default value
            
        Returns:
            Value from session state or default
        """
        return st.session_state.setdefault(key, default)
    
    @staticmethod
    def has(key: str) -> bool:
        """Check if key exists in session state.
        
        Args:
            key: Session state key
            
        Returns:
            True if key exists, False otherwise
        """
        return key in st.session_state
    
    @staticmethod
    def delete(key: str) -> None:
        """Delete a key from session state.
        
        Args:
            key: Session state key to delete
        """
        if key in st.session_state:
            del st.session_state[key]
    
    # Generic getters (domain-agnostic)
    @staticmethod
    def get_source_df(config: Optional[Any] = None) -> Optional[Any]:
        """Get source DataFrame (domain-agnostic).
        
        Args:
            config: DomainConfig instance. If None, uses default.
        
        Returns:
            Source DataFrame or None.
        """
        if config is None:
            from core.domain_config import get_domain_config
            config = get_domain_config()
        key = config.source_dataframe_key
        return st.session_state.get(key)
    
    @staticmethod
    def get_target_layout_df() -> Optional[Any]:
        """Get target layout DataFrame (domain-agnostic).
        
        Returns:
            Target layout DataFrame or None.
        """
        return st.session_state.get("layout_df")
    
    # Typed getters for common values (backward compatibility - claims-specific)
    @staticmethod
    def get_claims_df() -> Optional[Any]:
        """Get claims DataFrame (backward compatibility).
        
        Note: This is an alias for get_source_df() for backward compatibility.
        """
        return SessionStateManager.get_source_df()
    
    @staticmethod
    def get_layout_df() -> Optional[Any]:
        """Get layout DataFrame (backward compatibility).
        
        Note: This is an alias for get_target_layout_df() for backward compatibility.
        """
        return SessionStateManager.get_target_layout_df()
    
    @staticmethod
    def get_final_mapping() -> Dict[str, Dict[str, Any]]:
        """Get final mapping dictionary."""
        return st.session_state.get("final_mapping", {})
    
    @staticmethod
    def set_final_mapping(mapping: Dict[str, Dict[str, Any]]) -> None:
        """Set final mapping dictionary."""
        st.session_state["final_mapping"] = mapping
    
    @staticmethod
    def get_transformed_df() -> Optional[Any]:
        """Get transformed DataFrame."""
        return st.session_state.get("transformed_df")
    
    @staticmethod
    def set_transformed_df(df: Any) -> None:
        """Set transformed DataFrame."""
        st.session_state["transformed_df"] = df
    
    @staticmethod
    def get_validation_results() -> List[Dict[str, Any]]:
        """Get validation results."""
        return st.session_state.get("validation_results", [])
    
    @staticmethod
    def set_validation_results(results: List[Dict[str, Any]]) -> None:
        """Set validation results."""
        st.session_state["validation_results"] = results
    
    @staticmethod
    def get_audit_log() -> List[Dict[str, Any]]:
        """Get audit log."""
        return st.session_state.setdefault("audit_log", [])
    
    @staticmethod
    def add_audit_event(event_type: str, message: str) -> None:
        """Add event to audit log.
        
        Args:
            event_type: Type of event
            message: Event message
        """
        audit_log = SessionStateManager.get_audit_log()
        audit_log.append({
            "event_type": event_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last N events
        from core.config_loader import AUDIT_LOG_MAX_SIZE
        if len(audit_log) > AUDIT_LOG_MAX_SIZE:
            del audit_log[:len(audit_log) - AUDIT_LOG_MAX_SIZE]
    
    @staticmethod
    def clear_audit_log() -> None:
        """Clear audit log."""
        st.session_state["audit_log"] = []
    
    @staticmethod
    def get_dark_mode() -> bool:
        """Get dark mode setting."""
        return st.session_state.get("dark_mode", False)
    
    @staticmethod
    def set_dark_mode(enabled: bool) -> None:
        """Set dark mode."""
        st.session_state["dark_mode"] = enabled
    
    @staticmethod
    def needs_refresh() -> bool:
        """Check if refresh is needed."""
        return st.session_state.get("needs_refresh", False)
    
    @staticmethod
    def set_needs_refresh(value: bool = True) -> None:
        """Set refresh flag."""
        st.session_state["needs_refresh"] = value
    
    @staticmethod
    def clear_refresh_flag() -> None:
        """Clear refresh flag."""
        if SessionStateManager.needs_refresh():
            st.session_state["needs_refresh"] = False


# --- Undo/Redo Functions (migrated from session_state.py) ---

def initialize_undo_redo() -> None:
    """Initialize undo/redo history for mappings."""
    if "mapping_history" not in st.session_state:
        st.session_state.mapping_history = []
    if "history_index" not in st.session_state:
        st.session_state.history_index = -1


def save_to_history(final_mapping: Dict[str, Dict[str, Any]]) -> None:
    """Save current mapping state to history.
    
    Uses shallow copy for performance - mapping structure is dict[str, dict[str, Any]]
    which doesn't require deep copying since inner dicts are simple value containers.
    """
    from core.config_loader import MAPPING_HISTORY_MAX_SIZE
    initialize_undo_redo()
    # Remove any future history if we're not at the end
    if st.session_state.history_index < len(st.session_state.mapping_history) - 1:
        st.session_state.mapping_history = st.session_state.mapping_history[:st.session_state.history_index + 1]
    # Add new state - use dict comprehension for shallow copy (faster than deepcopy)
    # This works because mapping structure is dict[str, dict[str, Any]] where inner dicts
    # only contain simple values (strings, not nested objects)
    st.session_state.mapping_history.append({k: dict(v) if isinstance(v, dict) else v for k, v in final_mapping.items()})
    st.session_state.history_index = len(st.session_state.mapping_history) - 1
    # Limit history size
    if len(st.session_state.mapping_history) > MAPPING_HISTORY_MAX_SIZE:
        st.session_state.mapping_history.pop(0)
        st.session_state.history_index -= 1


def undo_mapping() -> Optional[Dict[str, Dict[str, Any]]]:
    """Undo last mapping change."""
    initialize_undo_redo()
    if st.session_state.history_index > 0:
        st.session_state.history_index -= 1
        return st.session_state.mapping_history[st.session_state.history_index]
    return None


def redo_mapping() -> Optional[Dict[str, Dict[str, Any]]]:
    """Redo last undone mapping change."""
    initialize_undo_redo()
    if st.session_state.history_index < len(st.session_state.mapping_history) - 1:
        st.session_state.history_index += 1
        return st.session_state.mapping_history[st.session_state.history_index]
    return None

