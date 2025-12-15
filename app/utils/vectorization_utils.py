# --- vectorization_utils.py ---
"""Utilities for optimizing pandas operations with vectorization."""
from typing import Any, Callable, Dict, List, Optional
import pandas as pd
import numpy as np
from core.exceptions import ProcessingError


def vectorize_operation(
    df: pd.DataFrame,
    column: str,
    operation: Callable[[Any], Any],
    use_vectorized: bool = True
) -> pd.Series:
    """
    Apply operation to a column using vectorized operations when possible.
    
    Args:
        df: DataFrame
        column: Column name
        operation: Operation function
        use_vectorized: Whether to attempt vectorization
    
    Returns:
        Result Series
    """
    if column not in df.columns:
        raise ProcessingError(
            f"Column '{column}' not found",
            error_code="COLUMN_NOT_FOUND"
        )
    
    if use_vectorized:
        # Try to use vectorized operations
        try:
            # Check if operation can be vectorized
            if hasattr(operation, '__vectorized__'):
                return operation(df[column])
            
            # Try numpy vectorization
            if isinstance(df[column].dtype, (np.integer, np.floating)):
                return pd.Series(operation(df[column].values), index=df.index)
        except Exception:
            # Fallback to apply
            pass
    
    # Fallback to apply
    return df[column].apply(operation)


def vectorize_conditional(
    df: pd.DataFrame,
    condition: Callable[[pd.Series], pd.Series],
    true_value: Any,
    false_value: Any
) -> pd.Series:
    """
    Apply conditional logic using vectorized operations.
    
    Args:
        df: DataFrame
        condition: Condition function that returns boolean Series
        true_value: Value when condition is True
        false_value: Value when condition is False
    
    Returns:
        Result Series
    """
    mask = condition(df)
    result = pd.Series(false_value, index=df.index)
    result[mask] = true_value
    return result


def vectorize_string_operations(
    df: pd.DataFrame,
    column: str,
    operations: List[Dict[str, Any]]
) -> pd.Series:
    """
    Apply multiple string operations in a vectorized way.
    
    Args:
        df: DataFrame
        column: Column name
        operations: List of operation dictionaries with 'type' and 'params'
    
    Returns:
        Result Series
    """
    if column not in df.columns:
        raise ProcessingError(
            f"Column '{column}' not found",
            error_code="COLUMN_NOT_FOUND"
        )
    
    result = df[column].astype(str)
    
    for op in operations:
        op_type = op.get('type')
        params = op.get('params', {})
        
        if op_type == 'strip':
            result = result.str.strip()
        elif op_type == 'lower':
            result = result.str.lower()
        elif op_type == 'upper':
            result = result.str.upper()
        elif op_type == 'replace':
            result = result.str.replace(
                params.get('old', ''),
                params.get('new', ''),
                regex=params.get('regex', False)
            )
        elif op_type == 'extract':
            result = result.str.extract(
                params.get('pattern', ''),
                expand=False
            )
        elif op_type == 'contains':
            result = result.str.contains(
                params.get('pattern', ''),
                case=params.get('case', True),
                na=params.get('na', False)
            )
    
    return result


def optimize_column_operations(
    df: pd.DataFrame,
    operations: Dict[str, Callable[[pd.Series], pd.Series]]
) -> pd.DataFrame:
    """
    Apply multiple column operations efficiently.
    
    Args:
        df: DataFrame
        operations: Dictionary mapping column names to operation functions
    
    Returns:
        DataFrame with operations applied
    """
    result_df = df.copy()
    
    for column, operation in operations.items():
        if column in result_df.columns:
            result_df[column] = vectorize_operation(result_df, column, operation)
    
    return result_df


def batch_apply_vectorized(
    df: pd.DataFrame,
    func: Callable[[pd.DataFrame], pd.DataFrame],
    batch_size: int = 10000
) -> pd.DataFrame:
    """
    Apply function to DataFrame in batches using vectorized operations.
    
    Args:
        df: DataFrame
        func: Function to apply
        batch_size: Size of batches
    
    Returns:
        Processed DataFrame
    """
    if len(df) <= batch_size:
        return func(df)
    
    results = []
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i + batch_size]
        processed_batch = func(batch)
        results.append(processed_batch)
    
    return pd.concat(results, ignore_index=True)


def replace_apply_with_vectorized(
    df: pd.DataFrame,
    column: str,
    operation_type: str,
    **kwargs: Any
) -> pd.Series:
    """
    Replace .apply() calls with vectorized alternatives.
    
    Args:
        df: DataFrame
        column: Column name
        operation_type: Type of operation ('map', 'transform', 'filter', etc.)
        **kwargs: Operation-specific parameters
    
    Returns:
        Result Series
    """
    if column not in df.columns:
        raise ProcessingError(
            f"Column '{column}' not found",
            error_code="COLUMN_NOT_FOUND"
        )
    
    series = df[column]
    
    if operation_type == 'map':
        # Use .map() instead of .apply() for mapping
        mapping = kwargs.get('mapping', {})
        return series.map(mapping)
    
    elif operation_type == 'transform':
        # Use vectorized transform operations
        transform_type = kwargs.get('transform_type', 'numeric')
        if transform_type == 'numeric':
            # Numeric transformations
            if kwargs.get('log'):
                return np.log1p(series)
            elif kwargs.get('sqrt'):
                return np.sqrt(series)
            elif kwargs.get('square'):
                return series ** 2
        elif transform_type == 'string':
            # String transformations
            if kwargs.get('upper'):
                return series.astype(str).str.upper()
            elif kwargs.get('lower'):
                return series.astype(str).str.lower()
            elif kwargs.get('strip'):
                return series.astype(str).str.strip()
    
    elif operation_type == 'filter':
        # Use boolean indexing instead of .apply()
        condition = kwargs.get('condition')
        if condition:
            return series[condition(series)]
        return series
    
    elif operation_type == 'aggregate':
        # Use built-in aggregation
        agg_func = kwargs.get('agg_func', 'mean')
        if hasattr(series, agg_func):
            return getattr(series, agg_func)()
        return series
    
    # Fallback to apply if no vectorized alternative
    operation = kwargs.get('operation')
    if operation:
        return series.apply(operation)
    
    return series


def optimize_dataframe_operations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize DataFrame by replacing inefficient operations.
    
    Args:
        df: DataFrame to optimize
    
    Returns:
        Optimized DataFrame
    """
    # This would analyze the DataFrame and suggest optimizations
    # For now, return as-is
    return df.copy()


# Performance comparison utilities
def compare_apply_vs_vectorized(
    df: pd.DataFrame,
    column: str,
    apply_func: Callable[[Any], Any],
    vectorized_func: Optional[Callable[[pd.Series], pd.Series]] = None
) -> Dict[str, Any]:
    """
    Compare performance of .apply() vs vectorized operations.
    
    Args:
        df: DataFrame
        column: Column name
        apply_func: Function for .apply()
        vectorized_func: Vectorized alternative
    
    Returns:
        Performance comparison results
    """
    import time
    
    # Time .apply()
    start = time.time()
    apply_result = df[column].apply(apply_func)
    apply_time = time.time() - start
    
    vectorized_time = None
    if vectorized_func:
        start = time.time()
        vectorized_result = vectorized_func(df[column])
        vectorized_time = time.time() - start
    
    return {
        "apply_time": apply_time,
        "vectorized_time": vectorized_time,
        "speedup": apply_time / vectorized_time if vectorized_time else None,
        "apply_result_length": len(apply_result),
        "vectorized_result_length": len(vectorized_result) if vectorized_func else None
    }

