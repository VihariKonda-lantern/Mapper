# --- ux_enhancements.py ---
"""UX Enhancement Components - Tooltips, Validation Feedback, Empty States, etc."""
import streamlit as st
from typing import Any, Optional, Dict, List, Callable
from core.state_manager import SessionStateManager

st: Any = st


def render_help_tooltip(help_text: str, key: Optional[str] = None) -> None:
    """Render a ? icon with contextual help tooltip.
    
    Args:
        help_text: The tooltip text to display
        key: Optional unique key for the tooltip
    """
    tooltip_key = key or f"help_{hash(help_text)}"
    st.markdown(f"""
    <div class="help-tooltip-wrapper" style="display: inline-block; position: relative; margin-left: 4px;">
        <span class="help-icon" style="
            display: inline-block;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background-color: #6b7280;
            color: white;
            text-align: center;
            line-height: 16px;
            font-size: 11px;
            font-weight: bold;
            cursor: help;
            vertical-align: middle;
        " title="{help_text}">?</span>
        <div class="help-tooltip" style="
            visibility: hidden;
            opacity: 0;
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background-color: #1f2937;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            white-space: nowrap;
            z-index: 1000;
            margin-bottom: 5px;
            pointer-events: none;
            transition: opacity 0.2s;
            max-width: 300px;
            white-space: normal;
        ">{help_text}</div>
    </div>
    <style>
        .help-tooltip-wrapper:hover .help-tooltip {{
            visibility: visible;
            opacity: 1;
        }}
        .help-tooltip-wrapper:hover .help-icon {{
            background-color: #4b5563;
        }}
    </style>
    """, unsafe_allow_html=True)


def render_field_with_help(
    label: str,
    help_text: str,
    widget_func: Callable,
    *args,
    **kwargs
) -> Any:
    """Render a field with a help tooltip next to the label.
    
    Args:
        label: Field label
        help_text: Help tooltip text
        widget_func: Streamlit widget function (e.g., st.text_input, st.selectbox)
        *args, **kwargs: Arguments to pass to widget_func
        
    Returns:
        The return value of widget_func
    """
    col1, col2 = st.columns([1, 20])
    with col1:
        st.markdown(f"<div style='height: 38px; display: flex; align-items: center;'>{label}</div>", unsafe_allow_html=True)
    with col2:
        render_help_tooltip(help_text, key=f"help_{label}")
        return widget_func(*args, **kwargs)


def render_validation_feedback(
    is_valid: bool,
    error_message: Optional[str] = None,
    success_message: Optional[str] = None
) -> None:
    """Render inline validation feedback with visual indicators.
    
    Args:
        is_valid: Whether the field is valid
        error_message: Error message to display if invalid
        success_message: Success message to display if valid
    """
    if is_valid:
        icon = "✅"
        message = success_message or "Valid"
        color = "#10b981"
        border_color = "#10b981"
    else:
        icon = "❌"
        message = error_message or "Invalid"
        color = "#ef4444"
        border_color = "#ef4444"
    
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 4px;
        font-size: 12px;
        color: {color};
    ">
        <span>{icon}</span>
        <span>{message}</span>
    </div>
    """, unsafe_allow_html=True)


def render_empty_state(
    title: str,
    description: str,
    action_label: Optional[str] = None,
    action_func: Optional[Callable] = None,
    icon: str = "📋"
) -> None:
    """Render an enhanced empty state with actionable guidance.
    
    Args:
        title: Empty state title
        description: Description text
        action_label: Label for the action button
        action_func: Function to call when button is clicked
        icon: Icon to display
    """
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 3rem 2rem;
        background-color: #f9fafb;
        border-radius: 8px;
        border: 2px dashed #e5e7eb;
        margin: 2rem 0;
    ">
        <div style="font-size: 48px; margin-bottom: 1rem;">{icon}</div>
        <h3 style="color: #1f2937; font-size: 18px; font-weight: 600; margin-bottom: 0.5rem;">{title}</h3>
        <p style="color: #6b7280; font-size: 14px; margin-bottom: 1.5rem; max-width: 500px; margin-left: auto; margin-right: auto;">{description}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if action_label and action_func:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_label, use_container_width=True, type="primary"):
                action_func()


def render_success_with_next_steps(
    success_message: str,
    next_step_message: str,
    next_step_action: Optional[Callable] = None,
    next_step_label: Optional[str] = None
) -> None:
    """Render success confirmation with suggested next steps.
    
    Args:
        success_message: Success message to display
        next_step_message: Message about the next step
        next_step_action: Function to call for next step
        next_step_label: Label for the next step button
    """
    st.success(f"✅ {success_message}")
    
    if next_step_message:
        st.info(f"💡 {next_step_message}")
    
    if next_step_action and next_step_label:
        if st.button(next_step_label, type="primary", use_container_width=True):
            next_step_action()


def render_data_preview_comparison(
    source_df: Any,
    transformed_df: Any,
    max_rows: int = 10
) -> None:
    """Render side-by-side comparison of source vs transformed data.
    
    Args:
        source_df: Source DataFrame
        transformed_df: Transformed DataFrame
        max_rows: Maximum number of rows to display
    """
    st.markdown("### 📊 Data Preview: Source vs Transformed")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Source Data**")
        st.dataframe(source_df.head(max_rows), use_container_width=True)
    
    with col2:
        st.markdown("**Transformed Data**")
        st.dataframe(transformed_df.head(max_rows), use_container_width=True)
    
    # Highlight differences
    if len(source_df.columns) == len(transformed_df.columns):
        st.markdown("**Changes Detected:**")
        changes = []
        for col in source_df.columns:
            if col in transformed_df.columns:
                if not source_df[col].equals(transformed_df[col]):
                    changes.append(col)
        
        if changes:
            st.info(f"Modified columns: {', '.join(changes)}")
        else:
            st.success("No changes detected - data matches source format")


def render_global_search(
    placeholder: str = "Search across all tabs...",
    key: str = "global_search"
) -> str:
    """Render a global search input with recent searches dropdown.
    
    Args:
        placeholder: Placeholder text
        key: Unique key for the search widget
        
    Returns:
        Search query string
    """
    # Get recent searches from session state
    recent_searches = SessionStateManager.get("recent_searches", [])
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        search_query = st.text_input(
            "🔍 Global Search",
            placeholder=placeholder,
            key=key,
            help="Search across all tabs, fields, and data"
        )
    
    with col2:
        if recent_searches:
            selected_recent = st.selectbox(
                "Recent",
                [""] + recent_searches[-5:][::-1],  # Show last 5, most recent first
                key=f"{key}_recent",
                label_visibility="collapsed"
            )
            if selected_recent:
                st.session_state[key] = selected_recent
                search_query = selected_recent
    
    # Save to recent searches if query is not empty
    if search_query and search_query not in recent_searches:
        recent_searches.append(search_query)
        if len(recent_searches) > 10:  # Keep only last 10
            recent_searches.pop(0)
        SessionStateManager.set("recent_searches", recent_searches)
    
    return search_query or ""


def render_accessibility_controls() -> Dict[str, Any]:
    """Render accessibility controls (high contrast mode, font size).
    
    Returns:
        Dictionary with accessibility settings
    """
    with st.sidebar.expander("♿ Accessibility", expanded=False):
        # High contrast mode
        high_contrast = st.checkbox(
            "High Contrast Mode",
            value=SessionStateManager.get("high_contrast_mode", False),
            key="accessibility_high_contrast",
            help="Increase contrast for better visibility"
        )
        
        # Font size adjustment
        font_size = st.selectbox(
            "Font Size",
            options=["Small", "Medium", "Large", "Extra Large"],
            index=["Small", "Medium", "Large", "Extra Large"].index(
                SessionStateManager.get("font_size", "Medium")
            ),
            key="accessibility_font_size",
            help="Adjust text size for better readability"
        )
        
        # Save settings
        SessionStateManager.set("high_contrast_mode", high_contrast)
        SessionStateManager.set("font_size", font_size)
        
        return {
            "high_contrast": high_contrast,
            "font_size": font_size
        }


def inject_accessibility_css(high_contrast: bool = False, font_size: str = "Medium") -> None:
    """Inject accessibility CSS based on user preferences.
    
    Args:
        high_contrast: Whether high contrast mode is enabled
        font_size: Font size preference
    """
    font_size_map = {
        "Small": "12px",
        "Medium": "13px",
        "Large": "16px",
        "Extra Large": "20px"
    }
    
    base_font_size = font_size_map.get(font_size, "13px")
    
    contrast_css = ""
    if high_contrast:
        contrast_css = """
        /* High Contrast Mode */
        body, .main, .stMarkdown, p, div, span, label {
            color: #000000 !important;
            background-color: #ffffff !important;
        }
        .stButton > button {
            border: 2px solid #000000 !important;
        }
        [data-testid="stTextInput"] > div > div > input,
        [data-testid="stSelectbox"] > div > div {
            border: 2px solid #000000 !important;
        }
        """
    
    st.markdown(f"""
    <style>
    /* Accessibility: Font Size */
    body, .main, .stMarkdown, p, div, span, label {{
        font-size: {base_font_size} !important;
    }}
    
    {contrast_css}
    
    /* Accessibility: ARIA Labels */
    [data-testid="stTextInput"] > div > div > input {{
        aria-label: "Text input field";
    }}
    [data-testid="stSelectbox"] > div > div {{
        aria-label: "Select dropdown";
    }}
    [data-testid="stButton"] > button {{
        aria-label: "Button";
    }}
    </style>
    """, unsafe_allow_html=True)
