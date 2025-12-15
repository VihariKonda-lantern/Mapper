# --- docstring_utils.py ---
"""Utilities for docstring validation and formatting."""
from typing import Any, Callable, Optional
import inspect
from enum import Enum


class DocstringStyle(Enum):
    """Docstring style formats."""
    GOOGLE = "google"
    NUMPY = "numpy"
    SPHINX = "sphinx"
    PLAIN = "plain"


def validate_docstring(func: Callable[..., Any], style: DocstringStyle = DocstringStyle.GOOGLE) -> tuple[bool, Optional[str]]:
    """
    Validate that a function has a proper docstring.
    
    Args:
        func: Function to validate
        style: Expected docstring style
    
    Returns:
        Tuple of (has_docstring, error_message)
    """
    doc = inspect.getdoc(func)
    if not doc:
        return False, f"Function {func.__name__} is missing a docstring"
    
    # Basic validation - check for common sections
    if style == DocstringStyle.GOOGLE:
        # Check for Args section
        if "Args:" in doc or "Parameters:" in doc:
            return True, None
        # Check for Returns section
        if "Returns:" in doc:
            return True, None
        # If it's a simple docstring, that's okay too
        if len(doc.strip()) > 10:
            return True, None
    
    return True, None


def get_docstring_summary(docstring: str) -> str:
    """
    Extract summary line from docstring.
    
    Args:
        docstring: Full docstring
    
    Returns:
        Summary line (first line or first sentence)
    """
    if not docstring:
        return ""
    
    lines = docstring.strip().split('\n')
    first_line = lines[0].strip()
    
    # If first line ends with period, it's likely a complete sentence
    if first_line.endswith('.'):
        return first_line
    
    # Otherwise, take first line up to first period
    if '.' in first_line:
        return first_line.split('.')[0] + '.'
    
    return first_line


def format_docstring_args(args: dict[str, str]) -> str:
    """
    Format Args section for Google-style docstring.
    
    Args:
        args: Dictionary mapping parameter names to descriptions
    
    Returns:
        Formatted Args section
    """
    if not args:
        return ""
    
    lines = ["Args:"]
    for param, desc in args.items():
        lines.append(f"    {param}: {desc}")
    
    return "\n".join(lines)


def format_docstring_returns(return_desc: str) -> str:
    """
    Format Returns section for Google-style docstring.
    
    Args:
        return_desc: Return value description
    
    Returns:
        Formatted Returns section
    """
    if not return_desc:
        return ""
    
    return f"Returns:\n    {return_desc}"


def format_docstring_raises(raises: dict[str, str]) -> str:
    """
    Format Raises section for Google-style docstring.
    
    Args:
        raises: Dictionary mapping exception types to descriptions
    
    Returns:
        Formatted Raises section
    """
    if not raises:
        return ""
    
    lines = ["Raises:"]
    for exc_type, desc in raises.items():
        lines.append(f"    {exc_type}: {desc}")
    
    return "\n".join(lines)


def generate_docstring_template(
    func: Callable[..., Any],
    description: str = "",
    args: Optional[dict[str, str]] = None,
    returns: Optional[str] = None,
    raises: Optional[dict[str, str]] = None
) -> str:
    """
    Generate a Google-style docstring template for a function.
    
    Args:
        func: Function to generate docstring for
        description: Function description
        args: Parameter descriptions
        returns: Return value description
        raises: Exception descriptions
    
    Returns:
        Generated docstring
    """
    parts = []
    
    # Description
    if description:
        parts.append(description)
    else:
        parts.append(f"{func.__name__} function.")
    
    parts.append("")  # Blank line
    
    # Args
    if args:
        parts.append(format_docstring_args(args))
        parts.append("")
    
    # Returns
    if returns:
        parts.append(format_docstring_returns(returns))
        parts.append("")
    
    # Raises
    if raises:
        parts.append(format_docstring_raises(raises))
    
    return "\n".join(parts).strip()


def check_module_docstrings(module_path: str) -> dict[str, Any]:
    """
    Check docstring coverage for a module.
    
    Args:
        module_path: Path to module file
    
    Returns:
        Dictionary with coverage statistics
    """
    import importlib.util
    import os
    
    if not os.path.exists(module_path):
        return {"error": "Module not found"}
    
    spec = importlib.util.spec_from_file_location("module", module_path)
    if not spec or not spec.loader:
        return {"error": "Could not load module"}
    
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        return {"error": f"Error loading module: {str(e)}"}
    
    functions = []
    classes = []
    
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and obj.__module__ == module.__name__:
            functions.append((name, obj))
        elif inspect.isclass(obj) and obj.__module__ == module.__name__:
            classes.append((name, obj))
    
    total = len(functions) + len(classes)
    with_docs = 0
    
    for name, obj in functions + classes:
        if inspect.getdoc(obj):
            with_docs += 1
    
    coverage = (with_docs / total * 100) if total > 0 else 0.0
    
    return {
        "total": total,
        "with_docs": with_docs,
        "without_docs": total - with_docs,
        "coverage": coverage,
        "functions": len(functions),
        "classes": len(classes)
    }

