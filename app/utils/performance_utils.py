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


def render_lazy_dataframe(df: Any, key: str = "lazy_df", page_size: int = 1000, max_rows_before_pagination: int = 1000) -> None:
    """Render a dataframe with lazy loading for large datasets.
    
    Args:
        df: DataFrame to display
        key: Unique key for this dataframe's pagination state
        page_size: Number of rows per page
        max_rows_before_pagination: Only paginate if dataframe has more rows than this
    """
    if df is None or (hasattr(df, 'empty') and df.empty):
        st.info("No data to display")
        return
    
    total_rows = len(df) if hasattr(df, '__len__') else 0
    
    # Only paginate if dataframe is large
    if total_rows > max_rows_before_pagination:
        page_key = f"{key}_page"
        page_size_key = f"{key}_page_size"
        
        # Page size selector
        page_size = st.selectbox(
            "Rows per page:",
            options=[100, 500, 1000, 2000, 5000],
            index=2,  # Default to 1000
            key=page_size_key
        )
        
        # Calculate pagination
        total_pages = (total_rows + page_size - 1) // page_size if total_rows > 0 else 1
        current_page = st.session_state.get(page_key, 1)
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← Previous", key=f"{key}_prev", disabled=current_page == 1):
                st.session_state[page_key] = max(1, current_page - 1)
                st.session_state.needs_refresh = True
        with col2:
            st.markdown(f"**Page {current_page} of {total_pages}** ({total_rows:,} total rows)", unsafe_allow_html=True)
        with col3:
            if st.button("Next →", key=f"{key}_next", disabled=current_page >= total_pages):
                st.session_state[page_key] = min(total_pages, current_page + 1)
                st.session_state.needs_refresh = True
        
        # Display current page
        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_df = df.iloc[start_idx:end_idx]
        st.dataframe(paginated_df, use_container_width=True)
        st.caption(f"Showing rows {start_idx + 1:,} to {min(end_idx, total_rows):,} of {total_rows:,}")
    else:
        # Small dataframe - display directly
        st.dataframe(df, use_container_width=True)

