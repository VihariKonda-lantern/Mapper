# --- progress_indicators.py ---
"""Enhanced progress indicators with time estimates and action feedback."""
import streamlit as st
from typing import Any, Optional, Callable, Dict
from datetime import datetime, timedelta
import time

st: Any = st


class ProgressIndicator:
    """Enhanced progress indicator with time estimation."""
    
    def __init__(
        self,
        total_steps: int = 100,
        message: str = "Processing...",
        show_time: bool = True,
        show_percentage: bool = True
    ):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = datetime.now()
        self.message = message
        self.show_time = show_time
        self.show_percentage = show_percentage
        
        # Create UI elements
        self.progress_bar = st.progress(0)
        self.status_container = st.empty()
        self.time_container = st.empty() if show_time else None
        
        self._update_display()
    
    def update(self, step: int, status: str = "", custom_message: Optional[str] = None) -> None:
        """Update progress indicator."""
        self.current_step = min(step, self.total_steps)
        if custom_message:
            self.message = custom_message
        elif status:
            self.message = status
        
        self._update_display()
    
    def increment(self, amount: int = 1, status: str = "") -> None:
        """Increment progress by amount."""
        self.update(self.current_step + amount, status)
    
    def _update_display(self) -> None:
        """Update the display elements."""
        progress = min(100, int((self.current_step / self.total_steps) * 100))
        self.progress_bar.progress(progress)
        
        # Build status message
        status_parts = []
        if self.show_percentage:
            status_parts.append(f"{progress}%")
        status_parts.append(self.message)
        
        self.status_container.markdown(" | ".join(status_parts))
        
        # Update time estimate
        if self.time_container and self.current_step > 0:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            if self.current_step > 0:
                avg_time_per_step = elapsed / self.current_step
                remaining_steps = self.total_steps - self.current_step
                estimated_remaining = avg_time_per_step * remaining_steps
                
                if estimated_remaining < 60:
                    time_str = f"~{int(estimated_remaining)}s remaining"
                elif estimated_remaining < 3600:
                    time_str = f"~{int(estimated_remaining / 60)}m remaining"
                else:
                    time_str = f"~{int(estimated_remaining / 3600)}h remaining"
                
                self.time_container.caption(f"⏱️ {time_str}")
    
    def complete(self, message: str = "Complete!") -> None:
        """Mark progress as complete."""
        self.update(self.total_steps, message)
        time.sleep(0.3)
        self.progress_bar.empty()
        self.status_container.empty()
        if self.time_container:
            self.time_container.empty()
    
    def error(self, message: str = "Error occurred") -> None:
        """Mark progress as error."""
        self.status_container.error(f"❌ {message}")
        time.sleep(2)
        self.progress_bar.empty()
        self.status_container.empty()
        if self.time_container:
            self.time_container.empty()


def show_action_feedback(
    action: str,
    success: bool = True,
    message: Optional[str] = None,
    duration: int = 2
) -> None:
    """Show immediate visual feedback for actions."""
    if success:
        icon = "✅"
        default_msg = f"{action} completed successfully"
        feedback_func = st.success
    else:
        icon = "❌"
        default_msg = f"{action} failed"
        feedback_func = st.error
    
    msg = message or default_msg
    feedback_func(f"{icon} {msg}")
    
    # Also show toast
    try:
        st.toast(f"{icon} {msg}", duration=duration)
    except Exception:
        pass


def show_loading_state(
    message: str = "Loading...",
    show_spinner: bool = True
) -> Any:
    """Show a loading state with optional spinner."""
    if show_spinner:
        return st.spinner(message)
    else:
        status = st.empty()
        status.info(f"⏳ {message}")
        return status


def render_workflow_progress(
    current_step: int,
    total_steps: int,
    step_names: Optional[list[str]] = None
) -> None:
    """Render overall workflow progress indicator."""
    if step_names is None:
        step_names = [
            "Setup",
            "Field Mapping",
            "Preview & Validate",
            "Downloads"
        ]
    
    progress = min(100, int((current_step / total_steps) * 100))
    
    # Create progress bar
    st.progress(progress)
    
    # Show step names
    cols = st.columns(total_steps)
    for i, (col, step_name) in enumerate(zip(cols, step_names[:total_steps])):
        with col:
            if i < current_step:
                status = "✅"
                color = "#4CAF50"
            elif i == current_step:
                status = "🔄"
                color = "#FF9800"
            else:
                status = "⏸️"
                color = "#9E9E9E"
            
            st.markdown(
                f'<div style="text-align: center; color: {color}; font-weight: {"600" if i == current_step else "400"};">'
                f'{status}<br>{step_name}</div>',
                unsafe_allow_html=True
            )


def with_progress_indicator(
    total_steps: int = 100,
    message: str = "Processing..."
):
    """Decorator to add progress indicator to a function."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            indicator = ProgressIndicator(total_steps, message)
            
            # Add indicator to kwargs if function accepts it
            if 'progress' in func.__code__.co_varnames:
                kwargs['progress'] = indicator
            
            try:
                result = func(*args, **kwargs)
                indicator.complete()
                return result
            except Exception as e:
                indicator.error(str(e))
                raise
        
        return wrapper
    return decorator

