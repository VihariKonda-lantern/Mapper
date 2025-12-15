# --- lazy_imports.py ---
"""Lazy import utilities for heavy modules."""
from typing import Any, Optional, Callable
import importlib
import sys


class LazyModule:
    """Lazy loading wrapper for modules."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self._module: Optional[Any] = None
    
    def __getattr__(self, name: str) -> Any:
        """Lazy load module on first attribute access."""
        if self._module is None:
            self._module = importlib.import_module(self.module_name)
        return getattr(self._module, name)
    
    def __repr__(self) -> str:
        """String representation."""
        if self._module is None:
            return f"<LazyModule '{self.module_name}' (not loaded)>"
        return f"<LazyModule '{self.module_name}' (loaded)>"


class LazyImport:
    """Context manager for lazy imports."""
    
    def __init__(self, *module_names: str):
        self.module_names = module_names
        self.modules: dict[str, Any] = {}
    
    def __enter__(self) -> dict[str, Any]:
        """Enter context - modules are loaded on access."""
        for module_name in self.module_names:
            self.modules[module_name] = LazyModule(module_name)
        return self.modules
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context."""
        pass


def lazy_import(module_name: str) -> LazyModule:
    """
    Create a lazy import wrapper for a module.
    
    Args:
        module_name: Name of the module to import
    
    Returns:
        LazyModule wrapper
    
    Example:
        plotly = lazy_import('plotly.express')
        # Module is not loaded until first use
        fig = plotly.bar(...)  # Now module is loaded
    """
    return LazyModule(module_name)


def import_on_demand(module_name: str, fallback: Optional[Any] = None) -> Callable:
    """
    Create a decorator that imports a module only when the function is called.
    
    Args:
        module_name: Name of the module to import
        fallback: Optional fallback value if import fails
    
    Returns:
        Decorator function
    
    Example:
        @import_on_demand('plotly.express', None)
        def create_chart():
            import plotly.express as px
            return px.bar(...)
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                module = importlib.import_module(module_name)
                # Inject module into function's globals
                func.__globals__[module_name.split('.')[-1]] = module
                return func(*args, **kwargs)
            except ImportError:
                if fallback is not None:
                    return fallback
                raise
        return wrapper
    return decorator


# Common lazy imports for heavy modules
def get_plotly() -> LazyModule:
    """Get lazy-loaded Plotly module."""
    return lazy_import('plotly.express')


def get_plotly_go() -> LazyModule:
    """Get lazy-loaded Plotly graph_objects module."""
    return lazy_import('plotly.graph_objects')


def get_altair() -> LazyModule:
    """Get lazy-loaded Altair module."""
    return lazy_import('altair')


def get_pandas() -> Any:
    """Get pandas (usually already imported, but can be lazy)."""
    try:
        import pandas as pd
        return pd
    except ImportError:
        return lazy_import('pandas')


def get_numpy() -> Any:
    """Get numpy (usually already imported, but can be lazy)."""
    try:
        import numpy as np
        return np
    except ImportError:
        return lazy_import('numpy')


def get_psutil() -> Optional[LazyModule]:
    """Get lazy-loaded psutil module (optional dependency)."""
    try:
        return lazy_import('psutil')
    except ImportError:
        return None


# Usage example in code:
# Instead of: import plotly.express as px
# Use: px = get_plotly()
# The module will only be loaded when px is first accessed

