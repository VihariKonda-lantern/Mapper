# --- tab_router.py ---
"""Tab router using registry pattern for dynamic tab loading."""
from typing import Any, Dict, Callable, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import streamlit as st


class TabOrder(Enum):
    """Tab display order."""
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    LAST = 99


@dataclass
class TabInfo:
    """Information about a tab."""
    name: str
    display_name: str
    render_func: Callable[[], None]
    order: int = TabOrder.LAST.value
    icon: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other: "TabInfo") -> bool:
        """Compare tabs by order."""
        return self.order < other.order


class TabRegistry:
    """Registry for managing tabs."""
    
    def __init__(self):
        self._tabs: Dict[str, TabInfo] = {}
        self._default_tab: Optional[str] = None
    
    def register(
        self,
        name: str,
        display_name: str,
        render_func: Callable[[], None],
        order: int = TabOrder.LAST.value,
        icon: Optional[str] = None,
        description: Optional[str] = None,
        enabled: bool = True,
        is_default: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a tab.
        
        Args:
            name: Internal tab name (unique identifier)
            display_name: Display name shown in UI
            render_func: Function to render tab content
            order: Display order (lower numbers appear first)
            icon: Optional icon for the tab
            description: Optional tab description
            enabled: Whether tab is enabled
            is_default: Whether this is the default tab
            metadata: Optional metadata dictionary
        """
        tab_info = TabInfo(
            name=name,
            display_name=display_name,
            render_func=render_func,
            order=order,
            icon=icon,
            description=description,
            enabled=enabled,
            metadata=metadata or {}
        )
        
        self._tabs[name] = tab_info
        
        if is_default or self._default_tab is None:
            self._default_tab = name
    
    def unregister(self, name: str) -> None:
        """Unregister a tab."""
        if name in self._tabs:
            del self._tabs[name]
            if self._default_tab == name:
                self._default_tab = None
    
    def get_tab(self, name: str) -> Optional[TabInfo]:
        """Get tab information."""
        return self._tabs.get(name)
    
    def list_tabs(self, enabled_only: bool = True) -> List[TabInfo]:
        """
        List all registered tabs.
        
        Args:
            enabled_only: Whether to return only enabled tabs
        
        Returns:
            List of tab info objects, sorted by order
        """
        tabs = list(self._tabs.values())
        if enabled_only:
            tabs = [t for t in tabs if t.enabled]
        return sorted(tabs)
    
    def get_default_tab(self) -> Optional[str]:
        """Get default tab name."""
        return self._default_tab
    
    def set_default_tab(self, name: str) -> None:
        """Set default tab."""
        if name in self._tabs:
            self._default_tab = name
    
    def enable_tab(self, name: str) -> None:
        """Enable a tab."""
        if name in self._tabs:
            self._tabs[name].enabled = True
    
    def disable_tab(self, name: str) -> None:
        """Disable a tab."""
        if name in self._tabs:
            self._tabs[name].enabled = False


class TabRouter:
    """Router for managing and rendering tabs."""
    
    def __init__(self, registry: Optional[TabRegistry] = None):
        self.registry = registry or TabRegistry()
        self._current_tab: Optional[str] = None
    
    def register_tab(
        self,
        name: str,
        display_name: str,
        render_func: Callable[[], None],
        **kwargs: Any
    ) -> None:
        """Register a tab (convenience method)."""
        self.registry.register(name, display_name, render_func, **kwargs)
    
    def render_tabs(self, use_streamlit_tabs: bool = True) -> None:
        """
        Render all registered tabs.
        
        Args:
            use_streamlit_tabs: Whether to use Streamlit's tab component
        """
        tabs = self.registry.list_tabs(enabled_only=True)
        
        if not tabs:
            st.warning("No tabs registered")
            return
        
        # Get current tab from session state or use default
        default_tab = self.registry.get_default_tab()
        if default_tab:
            current_tab = st.session_state.get("active_tab", default_tab)
        else:
            current_tab = tabs[0].name
        
        if use_streamlit_tabs:
            # Use Streamlit's native tabs
            tab_names = [f"{tab.icon} {tab.display_name}" if tab.icon else tab.display_name for tab in tabs]
            selected_tabs = st.tabs(tab_names)
            
            for idx, tab_info in enumerate(tabs):
                with selected_tabs[idx]:
                    try:
                        tab_info.render_func()
                        # Remember last active tab
                        st.session_state["active_tab"] = tab_info.name
                    except Exception as e:
                        st.error(f"Error rendering tab '{tab_info.display_name}': {str(e)}")
        else:
            # Use custom sidebar navigation
            st.sidebar.title("Navigation")
            
            for tab_info in tabs:
                if st.sidebar.button(
                    f"{tab_info.icon} {tab_info.display_name}" if tab_info.icon else tab_info.display_name,
                    key=f"tab_{tab_info.name}",
                    use_container_width=True
                ):
                    st.session_state["active_tab"] = tab_info.name
            
            # Render current tab
            current_tab_info = self.registry.get_tab(current_tab)
            if current_tab_info:
                current_tab_info.render_func()
    
    def get_current_tab(self) -> Optional[str]:
        """Get current active tab name."""
        return st.session_state.get("active_tab")
    
    def set_current_tab(self, name: str) -> None:
        """Set current active tab."""
        if self.registry.get_tab(name):
            st.session_state["active_tab"] = name


# Global tab router instance
tab_router = TabRouter()


# Convenience decorator for registering tabs
def register_tab(
    name: str,
    display_name: str,
    order: int = TabOrder.LAST.value,
    icon: Optional[str] = None,
    description: Optional[str] = None,
    is_default: bool = False
):
    """
    Decorator to register a tab.
    
    Args:
        name: Internal tab name
        display_name: Display name
        order: Display order
        icon: Optional icon
        description: Optional description
        is_default: Whether this is the default tab
    
    Example:
        @register_tab("setup", "Setup", order=1, icon="📁", is_default=True)
        def render_setup():
            ...
    """
    def decorator(func: Callable[[], None]) -> Callable[[], None]:
        tab_router.register_tab(
            name=name,
            display_name=display_name,
            render_func=func,
            order=order,
            icon=icon,
            description=description,
            is_default=is_default
        )
        return func
    return decorator


# Register default tabs
def register_default_tabs() -> None:
    """Register default tabs from the tabs module."""
    try:
        from tabs.tab_setup import render_setup_tab
        from tabs.tab_mapping import render_mapping_tab
        from tabs.tab_validation import render_validation_tab
        from tabs.tab_downloads import render_downloads_tab
        from tabs.tab_data_quality import render_data_quality_tab
        from tabs.tab_tools import render_tools_tab
        
        tab_router.register_tab(
            name="setup",
            display_name="Setup",
            render_func=render_setup_tab,
            order=TabOrder.FIRST.value,
            icon="📁",
            description="Upload files and configure settings",
            is_default=True
        )
        
        tab_router.register_tab(
            name="mapping",
            display_name="Field Mapping",
            render_func=render_mapping_tab,
            order=TabOrder.SECOND.value,
            icon="🔗",
            description="Map source fields to target fields"
        )
        
        tab_router.register_tab(
            name="validation",
            display_name="Preview & Validate",
            render_func=render_validation_tab,
            order=TabOrder.THIRD.value,
            icon="✅",
            description="Preview transformed data and run validations"
        )
        
        tab_router.register_tab(
            name="downloads",
            display_name="Downloads",
            render_func=render_downloads_tab,
            order=TabOrder.FOURTH.value,
            icon="📥",
            description="Download transformed data and reports"
        )
        
        tab_router.register_tab(
            name="data_quality",
            display_name="Data Quality & Analysis",
            render_func=render_data_quality_tab,
            order=TabOrder.FIFTH.value,
            icon="📊",
            description="Analyze data quality metrics"
        )
        
        tab_router.register_tab(
            name="tools",
            display_name="Tools & Analytics",
            render_func=render_tools_tab,
            order=TabOrder.SIXTH.value,
            icon="🛠️",
            description="Additional tools and analytics"
        )
    except ImportError:
        # Silently fail if tabs module isn't available
        pass


# Auto-register defaults on import
try:
    register_default_tabs()
except Exception:
    pass

