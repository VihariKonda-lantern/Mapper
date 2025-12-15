"""Lazy evaluation utilities for large data processing."""
from typing import Any, Callable, Generator, Iterator, List, Optional, TypeVar
import pandas as pd
from functools import wraps

T = TypeVar('T')
R = TypeVar('R')


class LazyDataFrame:
    """Lazy wrapper for DataFrame operations."""
    
    def __init__(self, generator: Generator[pd.DataFrame, None, None], metadata: Optional[dict] = None):
        """
        Initialize lazy DataFrame.
        
        Args:
            generator: Generator that yields DataFrame chunks
            metadata: Optional metadata about the data
        """
        self._generator = generator
        self._metadata = metadata or {}
        self._cached: Optional[pd.DataFrame] = None
        self._exhausted = False
    
    def __iter__(self) -> Iterator[pd.DataFrame]:
        """Iterate over DataFrame chunks."""
        if self._cached is not None:
            yield self._cached
            return
        
        for chunk in self._generator:
            yield chunk
    
    def collect(self) -> pd.DataFrame:
        """Collect all chunks into a single DataFrame."""
        if self._cached is not None:
            return self._cached
        
        chunks = list(self._generator)
        if chunks:
            self._cached = pd.concat(chunks, ignore_index=True)
            return self._cached
        return pd.DataFrame()
    
    def map(self, func: Callable[[pd.DataFrame], pd.DataFrame]) -> 'LazyDataFrame':
        """Apply function to each chunk lazily."""
        def mapped_generator():
            for chunk in self._generator:
                yield func(chunk)
        return LazyDataFrame(mapped_generator(), self._metadata)
    
    def filter(self, predicate: Callable[[pd.DataFrame], bool]) -> 'LazyDataFrame':
        """Filter chunks based on predicate."""
        def filtered_generator():
            for chunk in self._generator:
                if predicate(chunk):
                    yield chunk
        return LazyDataFrame(filtered_generator(), self._metadata)
    
    def reduce(self, func: Callable[[Any, pd.DataFrame], Any], initial: Any = None) -> Any:
        """Reduce chunks to a single value."""
        accumulator = initial
        for chunk in self._generator:
            if accumulator is None:
                accumulator = chunk
            else:
                accumulator = func(accumulator, chunk)
        return accumulator
    
    def take(self, n: int) -> pd.DataFrame:
        """Take first n chunks and combine."""
        chunks = []
        for i, chunk in enumerate(self._generator):
            if i >= n:
                break
            chunks.append(chunk)
        
        if chunks:
            return pd.concat(chunks, ignore_index=True)
        return pd.DataFrame()
    
    @property
    def metadata(self) -> dict:
        """Get metadata."""
        return self._metadata


def lazy_map(func: Callable[[T], R]) -> Callable[[Iterator[T]], Generator[R, None, None]]:
    """Create a lazy map function."""
    def lazy_mapper(iterable: Iterator[T]) -> Generator[R, None, None]:
        for item in iterable:
            yield func(item)
    return lazy_mapper


def lazy_filter(predicate: Callable[[T], bool]) -> Callable[[Iterator[T]], Generator[T, None, None]]:
    """Create a lazy filter function."""
    def lazy_filter_func(iterable: Iterator[T]) -> Generator[T, None, None]:
        for item in iterable:
            if predicate(item):
                yield item
    return lazy_filter_func


def chunked_apply(
    df: pd.DataFrame,
    func: Callable[[pd.DataFrame], pd.DataFrame],
    chunk_size: int = 10000
) -> Generator[pd.DataFrame, None, None]:
    """
    Apply function to DataFrame in chunks lazily.
    
    Args:
        df: DataFrame to process
        func: Function to apply to each chunk
        chunk_size: Size of each chunk
    
    Yields:
        Processed DataFrame chunks
    """
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i + chunk_size]
        yield func(chunk)


def lazy_groupby(
    df: pd.DataFrame,
    by: str,
    chunk_size: int = 10000
) -> Generator[tuple, None, None]:
    """
    Lazy groupby operation for large DataFrames.
    
    Args:
        df: DataFrame to group
        by: Column name to group by
        chunk_size: Size of chunks for processing
    
    Yields:
        (group_key, group_df) tuples
    """
    # Sort by group key first
    sorted_df = df.sort_values(by)
    
    current_key = None
    current_group = []
    
    for i in range(0, len(sorted_df), chunk_size):
        chunk = sorted_df.iloc[i:i + chunk_size]
        
        for _, row in chunk.iterrows():
            key = row[by]
            
            if current_key is None:
                current_key = key
                current_group = [row]
            elif key == current_key:
                current_group.append(row)
            else:
                # Yield previous group
                if current_group:
                    group_df = pd.DataFrame(current_group)
                    yield (current_key, group_df)
                
                # Start new group
                current_key = key
                current_group = [row]
    
    # Yield last group
    if current_group:
        group_df = pd.DataFrame(current_group)
        yield (current_key, group_df)


def lazy_join(
    left_gen: Generator[pd.DataFrame, None, None],
    right_gen: Generator[pd.DataFrame, None, None],
    on: str,
    how: str = 'inner'
) -> Generator[pd.DataFrame, None, None]:
    """
    Lazy join operation for large DataFrames.
    
    Args:
        left_gen: Generator of left DataFrame chunks
        right_gen: Generator of right DataFrame chunks
        on: Column name to join on
        how: Join type ('inner', 'left', 'right', 'outer')
    
    Yields:
        Joined DataFrame chunks
    """
    # Collect right side (usually smaller)
    right_chunks = list(right_gen)
    right_df = pd.concat(right_chunks, ignore_index=True) if right_chunks else pd.DataFrame()
    
    # Join each left chunk with right
    for left_chunk in left_gen:
        if not right_df.empty:
            joined = left_chunk.merge(right_df, on=on, how=how)
            yield joined
        elif how in ['left', 'outer']:
            yield left_chunk


def generator_to_lazy_dataframe(
    generator: Generator[pd.DataFrame, None, None],
    metadata: Optional[dict] = None
) -> LazyDataFrame:
    """Convert a generator to LazyDataFrame."""
    return LazyDataFrame(generator, metadata)


def lazy_aggregate(
    generator: Generator[pd.DataFrame, None, None],
    agg_func: Callable[[pd.DataFrame], dict],
    combine_func: Optional[Callable[[List[dict]], dict]] = None
) -> dict:
    """
    Lazy aggregation over DataFrame chunks.
    
    Args:
        generator: Generator of DataFrame chunks
        agg_func: Function to aggregate each chunk
        combine_func: Function to combine chunk results
    
    Returns:
        Aggregated result
    """
    results = []
    for chunk in generator:
        result = agg_func(chunk)
        results.append(result)
    
    if combine_func:
        return combine_func(results)
    
    # Default: merge dictionaries
    combined = {}
    for result in results:
        for key, value in result.items():
            if key not in combined:
                combined[key] = []
            combined[key].append(value)
    
    # Sum numeric values, concatenate others
    final = {}
    for key, values in combined.items():
        if all(isinstance(v, (int, float)) for v in values):
            final[key] = sum(values)
        else:
            final[key] = values
    
    return final

