# --- performance_scalability.py ---
"""Performance and scalability enhancements."""
import streamlit as st
import pandas as pd
from typing import Any, Dict, List, Optional, Callable, Iterator
from datetime import datetime
import multiprocessing
from functools import lru_cache
import hashlib

st: Any = st
pd: Any = pd


def process_files_parallel(file_list: List[Any], process_func: Callable,
                          max_workers: Optional[int] = None) -> List[Any]:
    """Process multiple files in parallel.
    
    Args:
        file_list: List of files to process
        process_func: Function to process each file
        max_workers: Maximum number of worker processes
        
    Returns:
        List of processed results
    """
    if max_workers is None:
        max_workers = min(multiprocessing.cpu_count(), len(file_list))
    
    try:
        with multiprocessing.Pool(processes=max_workers) as pool:
            results = pool.map(process_func, file_list)
        return results
    except Exception as e:
        # Fallback to sequential processing
        return [process_func(f) for f in file_list]


def stream_process_large_file(file_path: str, chunk_size: int = 10000,
                             process_chunk: Optional[Callable] = None) -> Iterator[pd.DataFrame]:
    """Process large file in chunks without loading full file into memory.
    
    Args:
        file_path: Path to file
        chunk_size: Number of rows per chunk
        process_chunk: Optional function to process each chunk
        
    Yields:
        Processed DataFrame chunks
    """
    try:
        # Determine file type
        if file_path.endswith('.csv') or file_path.endswith('.txt'):
            chunk_iterator = pd.read_csv(file_path, chunksize=chunk_size)
        elif file_path.endswith('.xlsx'):
            # Excel files need to be read differently
            chunk_iterator = [pd.read_excel(file_path)]
        else:
            chunk_iterator = [pd.read_csv(file_path, chunksize=chunk_size)]
        
        for chunk in chunk_iterator:
            if process_chunk:
                yield process_chunk(chunk)
            else:
                yield chunk
    except Exception as e:
        st.error(f"Error streaming file: {str(e)}")
        yield pd.DataFrame()


def optimize_memory_usage(df: pd.DataFrame) -> pd.DataFrame:
    """Optimize DataFrame memory usage.
    
    Args:
        df: DataFrame
        
    Returns:
        Optimized DataFrame
    """
    if df is None or df.empty:
        return df
    
    optimized_df = df.copy()
    
    # Downcast numeric types
    for col in optimized_df.select_dtypes(include=['int64']).columns:
        optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='integer')
    
    for col in optimized_df.select_dtypes(include=['float64']).columns:
        optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='float')
    
    # Convert object columns to category if beneficial
    for col in optimized_df.select_dtypes(include=['object']).columns:
        num_unique_values = len(optimized_df[col].unique())
        num_total_values = len(optimized_df[col])
        if num_unique_values / num_total_values < 0.5:  # Less than 50% unique
            optimized_df[col] = optimized_df[col].astype('category')
    
    return optimized_df


def clear_unused_state() -> None:
    """Clear unused session state to free memory."""
    # Keep essential state
    essential_keys = {
        "final_mapping", "layout_df", "claims_df", "audit_log",
        "user_preferences", "recent_files", "favorites"
    }
    
    # Get all state keys
    all_keys = list(st.session_state.keys())
    
    # Clear non-essential large objects
    for key in all_keys:
        if key not in essential_keys:
            obj = st.session_state.get(key)
            if isinstance(obj, pd.DataFrame) and len(obj) > 10000:
                # Clear large DataFrames that aren't essential
                if key not in ["layout_df", "claims_df"]:
                    del st.session_state[key]


@lru_cache(maxsize=128)
def cached_validation_result(data_hash: str, validation_func_name: str) -> Optional[Any]:
    """Cache validation results (simplified - would need proper serialization).
    
    Args:
        data_hash: Hash of input data
        validation_func_name: Name of validation function
        
    Returns:
        Cached result or None
    """
    cache_key = f"{validation_func_name}_{data_hash}"
    if "validation_cache" not in st.session_state:
        st.session_state.validation_cache = {}
    
    return st.session_state.validation_cache.get(cache_key)


def store_validation_result_in_cache(data_hash: str, validation_func_name: str, result: Any) -> None:
    """Store validation result in cache.
    
    Args:
        data_hash: Hash of input data
        validation_func_name: Name of validation function
        result: Validation result
    """
    cache_key = f"{validation_func_name}_{data_hash}"
    if "validation_cache" not in st.session_state:
        st.session_state.validation_cache = {}
    
    st.session_state.validation_cache[cache_key] = result
    
    # Limit cache size
    if len(st.session_state.validation_cache) > 100:
        # Remove oldest entries (simple FIFO)
        oldest_key = next(iter(st.session_state.validation_cache))
        del st.session_state.validation_cache[oldest_key]


def run_background_job(job_name: str, job_func: Callable, *args, **kwargs) -> str:
    """Schedule a background job (simplified - would need proper job queue).
    
    Args:
        job_name: Name of job
        job_func: Function to run
        *args, **kwargs: Arguments for job function
        
    Returns:
        Job ID
    """
    job_id = f"{job_name}_{datetime.now().timestamp()}"
    
    if "background_jobs" not in st.session_state:
        st.session_state.background_jobs = {}
    
    # In a real implementation, this would use a proper job queue
    # For now, just store job info
    st.session_state.background_jobs[job_id] = {
        "name": job_name,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "func": job_func.__name__ if hasattr(job_func, '__name__') else str(job_func)
    }
    
    return job_id

