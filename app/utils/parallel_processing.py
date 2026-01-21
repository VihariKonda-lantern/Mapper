# --- parallel_processing.py ---
"""Enhanced parallel processing utilities for batch operations."""
from typing import Any, Callable, Dict, List, Optional, Iterator
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import multiprocessing
from functools import partial
import pandas as pd
from core.exceptions import ProcessingError


class ParallelProcessor:
    """Enhanced parallel processor for batch operations."""
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        use_threads: bool = False,
        chunk_size: Optional[int] = None
    ):
        """
        Initialize parallel processor.
        
        Args:
            max_workers: Maximum number of workers (default: CPU count)
            use_threads: Use threads instead of processes (for I/O-bound tasks)
            chunk_size: Size of chunks for processing
        """
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.use_threads = use_threads
        self.chunk_size = chunk_size
        self.executor_class = ThreadPoolExecutor if use_threads else ProcessPoolExecutor
    
    def process_batch(
        self,
        items: List[Any],
        process_func: Callable[[Any], Any],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Any]:
        """
        Process a batch of items in parallel.
        
        Args:
            items: List of items to process
            process_func: Function to process each item
            progress_callback: Optional callback(completed, total)
        
        Returns:
            List of processed results
        """
        if not items:
            return []
        
        results = []
        total = len(items)
        
        with self.executor_class(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(process_func, item): item
                for item in items
            }
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_item):
                completed += 1
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Store error result
                    item = future_to_item[future]
                    results.append({
                        "error": str(e),
                        "item": item,
                        "success": False
                    })
                
                if progress_callback:
                    progress_callback(completed, total)
        
        return results
    
    def process_chunks(
        self,
        data: Any,
        chunk_func: Callable[[Any], Any],
        combine_func: Optional[Callable[[List[Any]], Any]] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Any:
        """
        Process data in chunks in parallel.
        
        Args:
            data: Data to process (DataFrame, list, etc.)
            chunk_func: Function to process each chunk
            combine_func: Function to combine results (default: list)
            progress_callback: Optional progress callback
        
        Returns:
            Combined results
        """
        # Split into chunks
        if isinstance(data, pd.DataFrame):
            chunks = self._chunk_dataframe(data)
        elif isinstance(data, list):
            chunks = self._chunk_list(data)
        else:
            chunks = [data]
        
        # Process chunks in parallel
        results = self.process_batch(chunks, chunk_func, progress_callback)
        
        # Combine results
        if combine_func:
            return combine_func(results)
        return results
    
    def _chunk_dataframe(self, df: pd.DataFrame) -> List[pd.DataFrame]:
        """Split DataFrame into chunks."""
        if self.chunk_size is None:
            # Auto-calculate chunk size
            self.chunk_size = max(1, len(df) // self.max_workers)
        
        chunks = []
        for i in range(0, len(df), self.chunk_size):
            chunks.append(df.iloc[i:i + self.chunk_size])
        return chunks
    
    def _chunk_list(self, items: List[Any]) -> List[List[Any]]:
        """Split list into chunks."""
        if self.chunk_size is None:
            self.chunk_size = max(1, len(items) // self.max_workers)
        
        chunks = []
        for i in range(0, len(items), self.chunk_size):
            chunks.append(items[i:i + self.chunk_size])
        return chunks


def process_files_parallel_enhanced(
    files: List[Any],
    process_func: Callable[[Any], Any],
    max_workers: Optional[int] = None,
    use_threads: bool = False,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> List[Any]:
    """
    Process multiple files in parallel with enhanced features.
    
    Args:
        files: List of files to process
        process_func: Function to process each file
        max_workers: Maximum number of workers
        use_threads: Use threads instead of processes
        progress_callback: Optional progress callback
    
    Returns:
        List of processed results
    """
    processor = ParallelProcessor(
        max_workers=max_workers,
        use_threads=use_threads
    )
    return processor.process_batch(files, process_func, progress_callback)


def process_dataframe_parallel(
    df: pd.DataFrame,
    process_func: Callable[[pd.DataFrame], pd.DataFrame],
    chunk_size: Optional[int] = None,
    max_workers: Optional[int] = None,
    combine_func: Optional[Callable[[List[pd.DataFrame]], pd.DataFrame]] = None
) -> pd.DataFrame:
    """
    Process DataFrame in parallel chunks.
    
    Args:
        df: DataFrame to process
        process_func: Function to process each chunk
        chunk_size: Size of chunks
        max_workers: Maximum number of workers
        combine_func: Function to combine chunks (default: pd.concat)
    
    Returns:
        Processed DataFrame
    """
    processor = ParallelProcessor(
        max_workers=max_workers,
        chunk_size=chunk_size
    )
    
    if combine_func is None:
        def default_combine(chunks: List[pd.DataFrame]) -> pd.DataFrame:
            return pd.concat(chunks, ignore_index=True)
        combine_func = default_combine
    
    return processor.process_chunks(df, process_func, combine_func)


def batch_validate_parallel(
    validation_func: Callable[[pd.DataFrame], List[Dict[str, Any]]],
    data_chunks: List[pd.DataFrame],
    max_workers: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Run validations in parallel on multiple data chunks.
    
    Args:
        validation_func: Validation function
        data_chunks: List of DataFrame chunks
        max_workers: Maximum number of workers
    
    Returns:
        Combined validation results
    """
    processor = ParallelProcessor(max_workers=max_workers)
    
    def process_chunk(chunk: pd.DataFrame) -> List[Dict[str, Any]]:
        return validation_func(chunk)
    
    results = processor.process_batch(data_chunks, process_chunk)
    
    # Flatten results
    flattened = []
    for result in results:
        if isinstance(result, list):
            flattened.extend(result)
        else:
            flattened.append(result)
    
    return flattened


# Global processor instance
_global_processor: Optional[ParallelProcessor] = None


def get_parallel_processor(
    max_workers: Optional[int] = None,
    use_threads: bool = False
) -> ParallelProcessor:
    """Get or create global parallel processor."""
    global _global_processor
    if _global_processor is None:
        _global_processor = ParallelProcessor(max_workers=max_workers, use_threads=use_threads)
    return _global_processor

