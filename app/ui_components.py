# --- ui_components.py ---
"""Reusable UI components."""
import streamlit as st
from typing import Any, Optional, Callable
import time

st: Any = st


def render_tooltip(text: str, help_text: str) -> str:
    """Generate HTML for tooltip."""
    return f'<span class="tooltip-wrapper" title="{help_text}">{text}</span>'


def render_status_indicator(status: str) -> str:
    """Generate HTML for status indicator."""
    status_class = {
        "mapped": "status-mapped",
        "unmapped": "status-unmapped",
        "suggested": "status-suggested"
    }.get(status, "status-unmapped")
    return f'<span class="status-indicator {status_class}"></span>'


def render_progress_bar(percent: int, label: str = "", text_color: str = "#000000") -> str:
    """Generate HTML for animated progress bar."""
    return f'<div class="progress-container" style="margin-top: 0.75rem; margin-bottom: 0.5rem; background-color: rgba(0,0,0,0.1); border-radius: 4px; height: 8px; overflow: hidden;"><div style="width: {percent}%; background: #007bff !important; height: 100%; border-radius: 4px; transition: width 0.5s ease;"></div></div><small style="color: {text_color}; font-size: 0.9rem; display: block; margin-top: 0.5rem;">{label}</small>'


def render_title():
    """Renders the app title."""
    st.markdown("<div style='font-size: 22px; font-weight: 600; margin-bottom: 10px;'>Claims File Mapper and Validator</div>", unsafe_allow_html=True)


def _notify(msg: str) -> None:
    """Show a toast notification."""
    st.toast(msg)


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

