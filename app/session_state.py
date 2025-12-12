# --- session_state.py ---
"""Session state management for undo/redo and history."""
import streamlit as st
from typing import Dict, Any, Optional

st: Any = st

# Constants
MAPPING_HISTORY_MAX_SIZE = 50


def initialize_undo_redo():
    """Initialize undo/redo history for mappings."""
    if "mapping_history" not in st.session_state:
        st.session_state.mapping_history = []
    if "history_index" not in st.session_state:
        st.session_state.history_index = -1


def save_to_history(final_mapping: Dict[str, Dict[str, Any]]):
    """Save current mapping state to history.
    
    Uses shallow copy for performance - mapping structure is dict[str, dict[str, Any]]
    which doesn't require deep copying since inner dicts are simple value containers.
    """
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

