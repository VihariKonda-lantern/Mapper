"""Virtual scrolling and progressive loading for large tables."""
from typing import Any, Callable, Dict, List, Optional, Tuple
import pandas as pd
import streamlit as st


class VirtualScroller:
    """Virtual scrolling for large DataFrames."""
    
    def __init__(
        self,
        df: pd.DataFrame,
        page_size: int = 100,
        key_prefix: str = "virtual_scroll"
    ):
        """
        Initialize virtual scroller.
        
        Args:
            df: DataFrame to display
            page_size: Number of rows per page
            key_prefix: Prefix for session state keys
        """
        self.df = df
        self.page_size = page_size
        self.key_prefix = key_prefix
        self.total_rows = len(df)
        self.total_pages = (self.total_rows + page_size - 1) // page_size
    
    def get_current_page(self) -> int:
        """Get current page number."""
        key = f"{self.key_prefix}_page"
        return st.session_state.get(key, 1)
    
    def set_current_page(self, page: int) -> None:
        """Set current page number."""
        key = f"{self.key_prefix}_page"
        st.session_state[key] = max(1, min(page, self.total_pages))
    
    def get_page_data(self, page: Optional[int] = None) -> pd.DataFrame:
        """Get data for a specific page."""
        if page is None:
            page = self.get_current_page()
        
        start_idx = (page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        
        return self.df.iloc[start_idx:end_idx]
    
    def render(
        self,
        render_func: Optional[Callable[[pd.DataFrame], None]] = None,
        show_pagination: bool = True
    ) -> None:
        """
        Render virtual scrolled table.
        
        Args:
            render_func: Function to render DataFrame (default: st.dataframe)
            show_pagination: Whether to show pagination controls
        """
        current_page = self.get_current_page()
        page_data = self.get_page_data(current_page)
        
        # Render data
        if render_func:
            render_func(page_data)
        else:
            st.dataframe(page_data, use_container_width=True)
        
        # Pagination controls
        if show_pagination and self.total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⏮ First", key=f"{self.key_prefix}_first"):
                    self.set_current_page(1)
                    st.rerun()
            
            with col2:
                if st.button("◀ Prev", key=f"{self.key_prefix}_prev", disabled=(current_page == 1)):
                    self.set_current_page(current_page - 1)
                    st.rerun()
            
            with col3:
                st.write(f"Page {current_page} of {self.total_pages} ({self.total_rows} rows)")
            
            with col4:
                if st.button("Next ▶", key=f"{self.key_prefix}_next", disabled=(current_page == self.total_pages)):
                    self.set_current_page(current_page + 1)
                    st.rerun()
            
            with col5:
                if st.button("Last ⏭", key=f"{self.key_prefix}_last"):
                    self.set_current_page(self.total_pages)
                    st.rerun()
            
            # Page jump
            jump_page = st.number_input(
                "Jump to page:",
                min_value=1,
                max_value=self.total_pages,
                value=current_page,
                key=f"{self.key_prefix}_jump"
            )
            if jump_page != current_page:
                self.set_current_page(int(jump_page))
                st.rerun()


class ProgressiveLoader:
    """Progressive loading for large datasets."""
    
    def __init__(
        self,
        data_source: Callable[[int, int], pd.DataFrame],
        total_rows: int,
        initial_load: int = 1000,
        increment: int = 500,
        key_prefix: str = "progressive_load"
    ):
        """
        Initialize progressive loader.
        
        Args:
            data_source: Function that returns data for given range (start, end)
            total_rows: Total number of rows
            initial_load: Initial number of rows to load
            increment: Rows to load on each "load more"
            key_prefix: Prefix for session state keys
        """
        self.data_source = data_source
        self.total_rows = total_rows
        self.initial_load = initial_load
        self.increment = increment
        self.key_prefix = key_prefix
    
    def get_loaded_count(self) -> int:
        """Get number of rows currently loaded."""
        key = f"{self.key_prefix}_loaded"
        return st.session_state.get(key, self.initial_load)
    
    def set_loaded_count(self, count: int) -> None:
        """Set number of rows loaded."""
        key = f"{self.key_prefix}_loaded"
        st.session_state[key] = min(count, self.total_rows)
    
    def load_more(self) -> None:
        """Load more rows."""
        current = self.get_loaded_count()
        self.set_loaded_count(current + self.increment)
    
    def get_data(self) -> pd.DataFrame:
        """Get currently loaded data."""
        loaded_count = self.get_loaded_count()
        return self.data_source(0, loaded_count)
    
    def render(
        self,
        render_func: Optional[Callable[[pd.DataFrame], None]] = None,
        show_load_more: bool = True
    ) -> None:
        """
        Render progressively loaded data.
        
        Args:
            render_func: Function to render DataFrame
            show_load_more: Whether to show "Load More" button
        """
        data = self.get_data()
        loaded_count = self.get_loaded_count()
        
        # Render data
        if render_func:
            render_func(data)
        else:
            st.dataframe(data, use_container_width=True)
        
        # Load more button
        if show_load_more and loaded_count < self.total_rows:
            remaining = self.total_rows - loaded_count
            if st.button(
                f"Load More ({min(self.increment, remaining)} rows)",
                key=f"{self.key_prefix}_load_more"
            ):
                self.load_more()
                st.rerun()
            
            st.caption(f"Loaded {loaded_count:,} of {self.total_rows:,} rows ({remaining:,} remaining)")


class ComponentMemoizer:
    """Memoization for rendered components."""
    
    @staticmethod
    def memoize(
        key: str,
        data_hash: Optional[str] = None,
        render_func: Optional[Callable[[], None]] = None
    ) -> bool:
        """
        Check if component should be re-rendered.
        
        Args:
            key: Unique key for component
            data_hash: Hash of data (if None, always render)
            render_func: Function to render if needed
        
        Returns:
            True if component was rendered, False if cached
        """
        cache_key = f"_memo_cache_{key}"
        cached_hash = st.session_state.get(cache_key)
        
        if cached_hash == data_hash and data_hash is not None:
            return False  # Use cached version
        
        # Update cache and render
        if data_hash:
            st.session_state[cache_key] = data_hash
        
        if render_func:
            render_func()
        
        return True
    
    @staticmethod
    def clear_cache(key: Optional[str] = None) -> None:
        """Clear memoization cache."""
        if key:
            cache_key = f"_memo_cache_{key}"
            if cache_key in st.session_state:
                del st.session_state[cache_key]
        else:
            # Clear all memo caches
            keys_to_remove = [k for k in st.session_state.keys() if k.startswith("_memo_cache_")]
            for k in keys_to_remove:
                del st.session_state[k]


class RequestBatcher:
    """Batch multiple state updates into single rerun."""
    
    def __init__(self, key_prefix: str = "batch_updates"):
        """
        Initialize request batcher.
        
        Args:
            key_prefix: Prefix for session state keys
        """
        self.key_prefix = key_prefix
        self.pending_updates: List[Tuple[str, Any]] = []
    
    def add_update(self, key: str, value: Any) -> None:
        """Add state update to batch."""
        self.pending_updates.append((key, value))
    
    def apply_updates(self) -> None:
        """Apply all pending updates."""
        for key, value in self.pending_updates:
            st.session_state[key] = value
        self.pending_updates = []
    
    def batch_update(self, updates: Dict[str, Any]) -> None:
        """Batch multiple updates at once."""
        for key, value in updates.items():
            self.add_update(key, value)
        self.apply_updates()


def render_virtual_table(
    df: pd.DataFrame,
    page_size: int = 100,
    key: str = "virtual_table"
) -> None:
    """Convenience function to render virtual scrolled table."""
    scroller = VirtualScroller(df, page_size=page_size, key_prefix=key)
    scroller.render()


def render_progressive_table(
    data_source: Callable[[int, int], pd.DataFrame],
    total_rows: int,
    initial_load: int = 1000,
    key: str = "progressive_table"
) -> None:
    """Convenience function to render progressively loaded table."""
    loader = ProgressiveLoader(data_source, total_rows, initial_load=initial_load, key_prefix=key)
    loader.render()

