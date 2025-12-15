# --- type_guards.py ---
"""Type guard functions for runtime type checking."""
from typing import Any, TypeGuard, Union
import pandas as pd
from pathlib import Path


def is_dataframe(obj: Any) -> TypeGuard[pd.DataFrame]:
    """Type guard to check if object is a pandas DataFrame."""
    return isinstance(obj, pd.DataFrame)


def is_series(obj: Any) -> TypeGuard[pd.Series]:
    """Type guard to check if object is a pandas Series."""
    return isinstance(obj, pd.Series)


def is_dict_str_any(obj: Any) -> TypeGuard[dict[str, Any]]:
    """Type guard to check if object is dict[str, Any]."""
    return isinstance(obj, dict) and all(isinstance(k, str) for k in obj.keys())


def is_list_dict_any(obj: Any) -> TypeGuard[list[dict[str, Any]]]:
    """Type guard to check if object is list[dict[str, Any]]."""
    return (
        isinstance(obj, list) and
        all(isinstance(item, dict) for item in obj)
    )


def is_mapping_dict(obj: Any) -> TypeGuard[dict[str, dict[str, Any]]]:
    """Type guard to check if object is a mapping dictionary."""
    return (
        isinstance(obj, dict) and
        all(isinstance(k, str) for k in obj.keys()) and
        all(isinstance(v, dict) for v in obj.values())
    )


def is_pathlike(obj: Any) -> TypeGuard[Union[str, Path]]:
    """Type guard to check if object is path-like."""
    return isinstance(obj, (str, Path))


def is_numeric(obj: Any) -> TypeGuard[Union[int, float]]:
    """Type guard to check if object is numeric."""
    return isinstance(obj, (int, float))


def is_string_or_none(obj: Any) -> TypeGuard[Union[str, None]]:
    """Type guard to check if object is string or None."""
    return obj is None or isinstance(obj, str)


def is_list_string(obj: Any) -> TypeGuard[list[str]]:
    """Type guard to check if object is list[str]."""
    return isinstance(obj, list) and all(isinstance(item, str) for item in obj)


def is_valid_file_extension(filename: str, extensions: list[str]) -> bool:
    """Check if filename has a valid extension."""
    if not isinstance(filename, str):
        return False
    ext = Path(filename).suffix.lower()
    return ext in [e.lower() for e in extensions]


def is_valid_mapping_structure(obj: Any) -> TypeGuard[dict[str, dict[str, Any]]]:
    """Type guard to check if object is a valid mapping structure."""
    if not isinstance(obj, dict):
        return False
    
    for key, value in obj.items():
        if not isinstance(key, str):
            return False
        if not isinstance(value, dict):
            return False
        # Check if value dict has expected structure
        if "value" not in value:
            return False
    
    return True


def is_validation_result(obj: Any) -> bool:
    """Check if object is a validation result dictionary."""
    if not isinstance(obj, dict):
        return False
    
    required_keys = ["status", "check"]
    return all(key in obj for key in required_keys)


def is_file_metadata(obj: Any) -> bool:
    """Check if object is file metadata dictionary."""
    if not isinstance(obj, dict):
        return False
    
    required_keys = ["filename", "size"]
    return all(key in obj for key in required_keys)

