# --- performance_utils.py ---
"""Performance optimization utilities."""
import streamlit as st
import pandas as pd
from typing import Any, List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

st: Any = st
pd: Any = pd


def chunk_dataframe(df: Any, chunk_size: int = 10000) -> List[Any]:
    """Split a large dataframe into chunks."""
    chunks = []
    for i in range(0, len(df), chunk_size):
        chunks.append(df.iloc[i:i+chunk_size])
    return chunks


def process_chunks_parallel(chunks: List[Any], func: Any, max_workers: int = 4) -> List[Any]:
    """Process dataframe chunks in parallel."""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_chunk = {executor.submit(func, chunk): chunk for chunk in chunks}
        for future in as_completed(future_to_chunk):
            results.append(future.result())
    return results


@st.cache_data(show_spinner=False)
def cached_validation_results(data_hash: str, validation_func: Any, *args, **kwargs) -> List[Dict[str, Any]]:
    """Cache validation results based on data hash."""
    return validation_func(*args, **kwargs)


def get_data_hash(df: Any, mapping: Dict[str, Any]) -> str:
    """Generate a hash of data and mapping for cache invalidation."""
    data_str = f"{df.shape}{df.columns.tolist()}{str(mapping)}"
    return hashlib.md5(data_str.encode()).hexdigest()


def paginate_dataframe(df: Any, page_size: int = 100) -> Tuple[Any, int, int]:
    """Paginate a dataframe for display."""
    total_pages = (len(df) + page_size - 1) // page_size if len(df) > 0 else 1
    page_num = st.session_state.get("current_page", 1)
    
    if "prev_page" in st.session_state:
        if st.session_state.prev_page:
            page_num = max(1, page_num - 1)
            st.session_state.current_page = page_num
            del st.session_state.prev_page
    
    if "next_page" in st.session_state:
        if st.session_state.next_page:
            page_num = min(total_pages, page_num + 1)
            st.session_state.current_page = page_num
            del st.session_state.next_page
    
    start_idx = (page_num - 1) * page_size
    end_idx = start_idx + page_size
    paginated_df = df.iloc[start_idx:end_idx]
    
    return paginated_df, page_num, total_pages

