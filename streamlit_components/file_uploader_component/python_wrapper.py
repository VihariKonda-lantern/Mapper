"""
Python wrapper for the React file uploader component.
"""
import streamlit.components.v1 as components
import os
import base64
from typing import Optional, Dict, Any

# Get the path to the component's dist folder
_COMPONENT_PATH = os.path.join(os.path.dirname(__file__), "dist")

# Declare the component
_file_uploader_component = components.declare_component(
    "file_uploader",
    path=_COMPONENT_PATH if os.path.exists(_COMPONENT_PATH) else None,
    url="http://localhost:3001" if not os.path.exists(_COMPONENT_PATH) else None,
)


def file_uploader(
    label: str,
    sublabel: str = "Drag & drop or browse",
    accept: str = ".csv,.txt,.xlsx",
    compact: bool = False,
    selected_file_name: Optional[str] = None,
    selected_file_size: Optional[int] = None,
    key: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    React-based file uploader component for Streamlit.
    
    Args:
        label: Label text for the uploader
        sublabel: Subtitle text (only shown in full mode)
        accept: Comma-separated list of file extensions
        compact: If True, shows compact version
        selected_file_name: Name of currently selected file (for success state)
        selected_file_size: Size of currently selected file in bytes
        key: Unique key for the component
    
    Returns:
        Dictionary with file data if file is selected, None otherwise.
        Contains: fileName, fileSize, fileType, fileContent (base64)
    """
    result = _file_uploader_component(
        label=label,
        sublabel=sublabel,
        accept=accept,
        compact=compact,
        selectedFileName=selected_file_name,
        selectedFileSize=selected_file_size,
        key=key,
        default=None,
    )
    
    return result

