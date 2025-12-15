"""Async utilities for I/O operations."""
from typing import Any, Awaitable, Callable, Coroutine, List, Optional, TypeVar
import asyncio
from functools import wraps
import aiofiles
from pathlib import Path

T = TypeVar('T')


async def read_file_async(file_path: Path, encoding: str = 'utf-8') -> str:
    """
    Read file asynchronously.
    
    Args:
        file_path: Path to file
        encoding: File encoding
    
    Returns:
        File contents as string
    """
    try:
        async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
            return await f.read()
    except ImportError:
        # Fallback to synchronous if aiofiles not available
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()


async def write_file_async(file_path: Path, content: str, encoding: str = 'utf-8') -> None:
    """
    Write file asynchronously.
    
    Args:
        file_path: Path to file
        content: Content to write
        encoding: File encoding
    """
    try:
        async with aiofiles.open(file_path, 'w', encoding=encoding) as f:
            await f.write(content)
    except ImportError:
        # Fallback to synchronous if aiofiles not available
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)


async def process_files_async(
    files: List[Path],
    process_func: Callable[[Path], Awaitable[Any]],
    max_concurrent: int = 5
) -> List[Any]:
    """
    Process multiple files asynchronously.
    
    Args:
        files: List of file paths
        process_func: Async function to process each file
        max_concurrent: Maximum concurrent operations
    
    Returns:
        List of results
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_with_semaphore(file_path: Path) -> Any:
        async with semaphore:
            return await process_func(file_path)
    
    tasks = [process_with_semaphore(f) for f in files]
    return await asyncio.gather(*tasks)


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """
    Run async coroutine in sync context.
    
    Args:
        coro: Coroutine to run
    
    Returns:
        Result of coroutine
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create new task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create new one
        return asyncio.run(coro)


def async_to_sync(async_func: Callable[..., Awaitable[T]]) -> Callable[..., T]:
    """
    Decorator to convert async function to sync.
    
    Args:
        async_func: Async function
    
    Returns:
        Sync wrapper function
    """
    @wraps(async_func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return run_async(async_func(*args, **kwargs))
    return wrapper

