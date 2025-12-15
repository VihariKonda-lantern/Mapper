"""Dask integration for very large files (>1GB)."""
from typing import Any, Optional, Union
import pandas as pd
from pathlib import Path

try:
    import dask.dataframe as dd
    DASK_AVAILABLE = True
except ImportError:
    DASK_AVAILABLE = False
    dd = None  # type: ignore

from core.exceptions import FileError


def is_dask_available() -> bool:
    """Check if Dask is available."""
    return DASK_AVAILABLE


def load_large_file_with_dask(
    file_path: Union[str, Path],
    file_type: str = 'csv',
    chunk_size: Optional[int] = None,
    **kwargs: Any
) -> Any:
    """
    Load very large file using Dask if available, fallback to pandas.
    
    Args:
        file_path: Path to file
        file_type: File type ('csv', 'parquet', 'json')
        chunk_size: Chunk size for reading (Dask handles this automatically)
        **kwargs: Additional arguments for file reading
    
    Returns:
        Dask DataFrame if available, otherwise pandas DataFrame
    """
    if not DASK_AVAILABLE:
        # Fallback to pandas with chunking
        if file_type == 'csv':
            return pd.read_csv(file_path, chunksize=chunk_size or 100000, **kwargs)
        elif file_type == 'parquet':
            return pd.read_parquet(file_path, **kwargs)
        elif file_type == 'json':
            return pd.read_json(file_path, lines=True, chunksize=chunk_size or 100000, **kwargs)
        else:
            raise FileError(f"Unsupported file type: {file_type}", error_code="UNSUPPORTED_FILE_TYPE")
    
    file_path_str = str(file_path)
    
    try:
        if file_type == 'csv':
            return dd.read_csv(file_path_str, blocksize=chunk_size or '256MB', **kwargs)
        elif file_type == 'parquet':
            return dd.read_parquet(file_path_str, **kwargs)
        elif file_type == 'json':
            return dd.read_json(file_path_str, **kwargs)
        else:
            raise FileError(f"Unsupported file type: {file_type}", error_code="UNSUPPORTED_FILE_TYPE")
    except Exception as e:
        raise FileError(
            f"Error loading file with Dask: {str(e)}",
            error_code="DASK_LOAD_ERROR"
        ) from e


def process_large_dataframe_dask(
    df: Any,
    process_func: Any,
    partition_size: Optional[int] = None
) -> Any:
    """
    Process large DataFrame using Dask.
    
    Args:
        df: Dask DataFrame
        process_func: Function to apply to each partition
        partition_size: Size of partitions
    
    Returns:
        Processed Dask DataFrame
    """
    if not DASK_AVAILABLE:
        raise FileError("Dask is not available", error_code="DASK_NOT_AVAILABLE")
    
    if not isinstance(df, dd.DataFrame):
        # Convert pandas DataFrame to Dask
        df = dd.from_pandas(df, npartitions=partition_size or 4)
    
    # Apply function to each partition
    return df.map_partitions(process_func, meta=df)


def compute_dask_dataframe(df: Any, sample: bool = False) -> pd.DataFrame:
    """
    Compute Dask DataFrame to pandas DataFrame.
    
    Args:
        df: Dask DataFrame
        sample: If True, return sample instead of full computation
    
    Returns:
        Pandas DataFrame
    """
    if not DASK_AVAILABLE:
        if isinstance(df, pd.DataFrame):
            return df
        raise FileError("Dask is not available", error_code="DASK_NOT_AVAILABLE")
    
    if not isinstance(df, dd.DataFrame):
        return df
    
    if sample:
        # Return sample
        return df.head(1000).compute()
    
    return df.compute()


def get_dask_info(df: Any) -> dict:
    """
    Get information about Dask DataFrame.
    
    Args:
        df: Dask DataFrame
    
    Returns:
        Dictionary with Dask DataFrame info
    """
    if not DASK_AVAILABLE or not isinstance(df, dd.DataFrame):
        return {"type": "pandas", "available": False}
    
    return {
        "type": "dask",
        "available": True,
        "npartitions": df.npartitions,
        "columns": list(df.columns),
        "dtypes": df.dtypes.to_dict(),
        "divisions": df.divisions if hasattr(df, 'divisions') else None
    }


def should_use_dask(file_size: int, threshold: int = 1024 * 1024 * 1024) -> bool:
    """
    Determine if Dask should be used based on file size.
    
    Args:
        file_size: File size in bytes
        threshold: Threshold in bytes (default: 1GB)
    
    Returns:
        True if Dask should be used
    """
    return DASK_AVAILABLE and file_size > threshold

