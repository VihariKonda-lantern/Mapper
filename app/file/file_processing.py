# --- file_processing.py ---
"""Enhanced file processing with progress tracking and chunked reading."""
import streamlit as st
from typing import Any, Optional, Callable, Iterator, Tuple
import pandas as pd
import io
import os
from pathlib import Path
from ui.progress_indicators import ProgressIndicator

st: Any = st


def read_file_with_progress(
    file_obj: Any,
    file_size: Optional[int] = None,
    chunk_size: int = 1024 * 1024,  # 1MB chunks
    progress_callback: Optional[Callable[[float], None]] = None
) -> bytes:
    """Read file with progress tracking.
    
    Args:
        file_obj: File-like object to read
        file_size: Total file size in bytes (if known)
        chunk_size: Size of chunks to read
        progress_callback: Optional callback function(progress_percent)
    
    Returns:
        File content as bytes
    """
    file_obj.seek(0)
    content = b""
    
    if file_size is None:
        # Try to get file size
        try:
            if hasattr(file_obj, 'size'):
                file_size = file_obj.size
            elif hasattr(file_obj, 'seek') and hasattr(file_obj, 'tell'):
                current_pos = file_obj.tell()
                file_obj.seek(0, os.SEEK_END)
                file_size = file_obj.tell()
                file_obj.seek(current_pos)
        except Exception:
            file_size = None
    
    if file_size:
        # Read in chunks with progress
        bytes_read = 0
        while True:
            chunk = file_obj.read(chunk_size)
            if not chunk:
                break
            content += chunk
            bytes_read += len(chunk)
            
            if progress_callback:
                progress = (bytes_read / file_size) * 100
                progress_callback(progress)
    else:
        # Read all at once if size unknown
        content = file_obj.read()
        if progress_callback:
            progress_callback(100.0)
    
    file_obj.seek(0)
    return content


def load_csv_with_progress(
    file_obj: Any,
    delimiter: Optional[str] = None,
    has_header: bool = True,
    chunk_size: int = 10000,
    show_progress: bool = True
) -> pd.DataFrame:
    """Load CSV file with progress tracking.
    
    Args:
        file_obj: File-like object
        delimiter: CSV delimiter
        has_header: Whether file has header row
        chunk_size: Number of rows to read per chunk
        show_progress: Whether to show progress indicator
    
    Returns:
        DataFrame with all data
    """
    if not show_progress:
        # Simple load without progress
        file_obj.seek(0)
        return pd.read_csv(
            file_obj,
            delimiter=delimiter,
            header=0 if has_header else None,
            on_bad_lines='skip'
        )
    
    # Load with progress tracking
    file_obj.seek(0)
    
    # First, count total rows (approximate)
    total_rows = 0
    file_obj.seek(0)
    for _ in file_obj:
        total_rows += 1
    file_obj.seek(0)
    
    # Create progress indicator
    indicator = ProgressIndicator(
        total_steps=total_rows,
        message="Loading CSV file...",
        show_time=True
    )
    
    # Read in chunks
    chunks = []
    rows_read = 0
    
    try:
        for chunk_df in pd.read_csv(
            file_obj,
            delimiter=delimiter,
            header=0 if has_header else None,
            chunksize=chunk_size,
            on_bad_lines='skip'
        ):
            chunks.append(chunk_df)
            rows_read += len(chunk_df)
            indicator.update(rows_read, f"Loaded {rows_read:,} rows...")
        
        # Combine chunks
        indicator.update(total_rows, "Combining chunks...")
        result_df = pd.concat(chunks, ignore_index=True)
        indicator.complete(f"Loaded {len(result_df):,} rows successfully")
        
        return result_df
    except Exception as e:
        indicator.error(f"Error loading file: {str(e)}")
        raise


def load_excel_with_progress(
    file_obj: Any,
    sheet_name: Optional[str] = None,
    has_header: bool = True,
    show_progress: bool = True
) -> pd.DataFrame:
    """Load Excel file with progress tracking.
    
    Args:
        file_obj: File-like object
        sheet_name: Sheet name to load (None for first sheet)
        has_header: Whether file has header row
        show_progress: Whether to show progress indicator
    
    Returns:
        DataFrame with all data
    """
    if not show_progress:
        file_obj.seek(0)
        return pd.read_excel(
            file_obj,
            sheet_name=sheet_name,
            header=0 if has_header else None
        )
    
    # Load with progress
    indicator = ProgressIndicator(
        total_steps=100,
        message="Loading Excel file...",
        show_time=True
    )
    
    try:
        indicator.update(10, "Reading file structure...")
        file_obj.seek(0)
        
        indicator.update(30, "Parsing Excel data...")
        df = pd.read_excel(
            file_obj,
            sheet_name=sheet_name,
            header=0 if has_header else None
        )
        
        indicator.update(80, f"Processing {len(df):,} rows...")
        indicator.complete(f"Loaded {len(df):,} rows successfully")
        
        return df
    except Exception as e:
        indicator.error(f"Error loading Excel file: {str(e)}")
        raise


def process_file_with_progress(
    file_obj: Any,
    file_type: Optional[str] = None,
    **kwargs: Any
) -> pd.DataFrame:
    """Process file with appropriate progress tracking based on file type.
    
    Args:
        file_obj: File-like object
        file_type: File type (csv, xlsx, json, parquet) - auto-detected if None
        **kwargs: Additional arguments for file loading
    
    Returns:
        DataFrame with file data
    """
    if file_type is None:
        filename = getattr(file_obj, 'name', '')
        ext = os.path.splitext(filename)[-1].lower()
        file_type = ext.lstrip('.')
    
    show_progress = kwargs.pop('show_progress', True)
    
    if file_type in ['csv', 'txt', 'tsv']:
        return load_csv_with_progress(
            file_obj,
            delimiter=kwargs.get('delimiter'),
            has_header=kwargs.get('has_header', True),
            show_progress=show_progress
        )
    elif file_type in ['xlsx', 'xls']:
        return load_excel_with_progress(
            file_obj,
            sheet_name=kwargs.get('sheet_name'),
            has_header=kwargs.get('has_header', True),
            show_progress=show_progress
        )
    elif file_type == 'json':
        indicator = ProgressIndicator(
            total_steps=100,
            message="Loading JSON file...",
            show_time=True
        )
        try:
            indicator.update(50, "Parsing JSON...")
            file_obj.seek(0)
            df = pd.read_json(file_obj)
            indicator.complete(f"Loaded {len(df):,} rows successfully")
            return df
        except Exception as e:
            indicator.error(f"Error loading JSON: {str(e)}")
            raise
    elif file_type == 'parquet':
        indicator = ProgressIndicator(
            total_steps=100,
            message="Loading Parquet file...",
            show_time=True
        )
        try:
            indicator.update(50, "Reading Parquet data...")
            file_obj.seek(0)
            df = pd.read_parquet(file_obj)
            indicator.complete(f"Loaded {len(df):,} rows successfully")
            return df
        except Exception as e:
            indicator.error(f"Error loading Parquet: {str(e)}")
            raise
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def get_file_info(file_obj: Any) -> dict[str, Any]:
    """Get file information including size and type.
    
    Args:
        file_obj: File-like object
    
    Returns:
        Dictionary with file information
    """
    info = {
        "name": getattr(file_obj, 'name', 'Unknown'),
        "type": None,
        "size": None,
        "size_mb": None
    }
    
    # Get file name and extension
    filename = info["name"]
    if filename:
        ext = os.path.splitext(filename)[-1].lower()
        info["type"] = ext.lstrip('.')
    
    # Get file size
    try:
        if hasattr(file_obj, 'size'):
            info["size"] = file_obj.size
        elif hasattr(file_obj, 'seek') and hasattr(file_obj, 'tell'):
            current_pos = file_obj.tell()
            file_obj.seek(0, os.SEEK_END)
            info["size"] = file_obj.tell()
            file_obj.seek(current_pos)
        
        if info["size"]:
            info["size_mb"] = round(info["size"] / (1024 * 1024), 2)
    except Exception:
        pass
    
    return info

