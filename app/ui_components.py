# --- ui_components.py ---
"""Reusable UI components."""
import streamlit as st
from typing import Any

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


def render_progress_bar(percent: int, label: str = "") -> str:
    """Generate HTML for animated progress bar."""
    return f'<div class="progress-container" style="margin-top: 0.75rem; margin-bottom: 0.5rem; background-color: rgba(255,255,255,0.2); border-radius: 4px; height: 8px; overflow: hidden;"><div style="width: {percent}%; background: transparent !important; height: 100%; border-radius: 4px; transition: width 0.5s ease;"></div></div><small style="color: rgba(255,255,255,0.9); font-size: 0.9rem; display: block; margin-top: 0.5rem;">{label}</small>'


def render_title():
    """Renders the app title."""
    st.markdown("<div style='font-size: 22px; font-weight: 600; margin-bottom: 10px;'>Claims File Mapper and Validator</div>", unsafe_allow_html=True)


def _notify(msg: str) -> None:
    """Show a toast notification."""
    st.toast(msg)

