# --- decorators.py ---
"""Common decorators for error handling, logging, and caching."""
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, cast
import time
from cache_manager import CacheManager
from structured_logging import StructuredLogger
from error_context import error_context
from exceptions import ClaimsMapperError

logger = StructuredLogger("decorators")
cache = CacheManager()

F = TypeVar('F', bound=Callable[..., Any])


def handle_errors(
    error_message: Optional[str] = None,
    return_value: Any = None,
    log_error: bool = True
) -> Callable[[F], F]:
    """
    Decorator for error handling with optional logging and fallback value.
    
    Args:
        error_message: Custom error message to log
        return_value: Value to return if error occurs
        log_error: Whether to log the error
    
    Example:
        @handle_errors(error_message="Failed to process data", return_value=[])
        def process_data():
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                msg = error_message or f"Error in {func.__name__}"
                if log_error:
                    logger.log_error(msg, {"function": func.__name__, "error": str(e)})
                if return_value is not None:
                    return return_value
                raise
        return cast(F, wrapper)
    return decorator


def log_execution(
    log_args: bool = False,
    log_result: bool = False
) -> Callable[[F], F]:
    """
    Decorator for logging function execution.
    
    Args:
        log_args: Whether to log function arguments
        log_result: Whether to log function result
    
    Example:
        @log_execution(log_args=True)
        def process_file(filename):
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            log_data: Dict[str, Any] = {"function": func.__name__}
            
            if log_args:
                log_data["args"] = str(args)[:200]  # Limit length
                log_data["kwargs"] = str(kwargs)[:200]
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                log_data["execution_time"] = execution_time
                log_data["status"] = "success"
                
                if log_result:
                    log_data["result"] = str(result)[:200]
                
                logger.log_info(f"Function {func.__name__} executed successfully", log_data)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                log_data["execution_time"] = execution_time
                log_data["status"] = "error"
                log_data["error"] = str(e)
                logger.log_error(f"Function {func.__name__} failed", log_data)
                raise
        return cast(F, wrapper)
    return decorator


def cache_result(
    ttl: Optional[int] = None,
    key_prefix: Optional[str] = None
) -> Callable[[F], F]:
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds (None for default)
        key_prefix: Prefix for cache key
    
    Example:
        @cache_result(ttl=3600, key_prefix="data")
        def expensive_operation(param):
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            prefix = key_prefix or func.__name__
            key_parts = [prefix]
            if args:
                key_parts.append(str(hash(str(args))))
            if kwargs:
                key_parts.append(str(hash(str(sorted(kwargs.items())))))
            cache_key = "_".join(key_parts)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.log_debug(f"Cache hit for {func.__name__}", {"cache_key": cache_key})
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            logger.log_debug(f"Cached result for {func.__name__}", {"cache_key": cache_key})
            return result
        return cast(F, wrapper)
    return decorator


def measure_performance(
    operation_name: Optional[str] = None
) -> Callable[[F], F]:
    """
    Decorator for measuring function performance.
    
    Args:
        operation_name: Name of the operation (defaults to function name)
    
    Example:
        @measure_performance("data_processing")
        def process_large_dataset():
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            op_name = operation_name or func.__name__
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.log_info(
                    f"Performance: {op_name}",
                    {
                        "operation": op_name,
                        "execution_time": execution_time,
                        "status": "success"
                    }
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.log_error(
                    f"Performance: {op_name} failed",
                    {
                        "operation": op_name,
                        "execution_time": execution_time,
                        "status": "error",
                        "error": str(e)
                    }
                )
                raise
        return cast(F, wrapper)
    return decorator


def validate_input(
    validator: Callable[[Any], bool],
    error_message: str = "Validation failed"
) -> Callable[[F], F]:
    """
    Decorator for input validation.
    
    Args:
        validator: Function that returns True if input is valid
        error_message: Error message if validation fails
    
    Example:
        @validate_input(lambda x: x > 0, "Value must be positive")
        def process_positive(value):
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Validate all arguments
            for arg in args:
                if not validator(arg):
                    raise ClaimsMapperError(
                        error_message,
                        error_code="VALIDATION_ERROR",
                        context={"argument": str(arg)}
                    )
            for value in kwargs.values():
                if not validator(value):
                    raise ClaimsMapperError(
                        error_message,
                        error_code="VALIDATION_ERROR",
                        context={"argument": str(value)}
                    )
            return func(*args, **kwargs)
        return cast(F, wrapper)
    return decorator


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable[[F], F]:
    """
    Decorator for retry logic on function failures.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry on
    
    Example:
        @retry_on_failure(max_retries=3, delay=1.0)
        def unreliable_api_call():
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.log_warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__}",
                            {"attempt": attempt + 1, "error": str(e)}
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.log_error(
                            f"All retries exhausted for {func.__name__}",
                            {"max_retries": max_retries, "error": str(e)}
                        )
            
            if last_exception:
                raise last_exception
            return None  # Should never reach here
        return cast(F, wrapper)
    return decorator

