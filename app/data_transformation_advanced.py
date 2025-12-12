# --- data_transformation_advanced.py ---
"""Advanced data transformation features."""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
import re

st: Any = st
pd: Any = pd
np: Any = np


def create_data_cleaning_pipeline(steps: List[Dict[str, Any]]) -> Callable:
    """Create a data cleaning pipeline with multiple steps.
    
    Args:
        steps: List of cleaning step dictionaries
        
    Returns:
        Pipeline function
    """
    def pipeline(df: pd.DataFrame) -> pd.DataFrame:
        result_df = df.copy()
        for step in steps:
            step_type = step.get("type")
            if step_type == "remove_duplicates":
                result_df = result_df.drop_duplicates()
            elif step_type == "fill_missing":
                column = step.get("column")
                method = step.get("method", "forward")
                if column and column in result_df.columns:
                    if method == "forward":
                        result_df[column] = result_df[column].fillna(method='ffill')
                    elif method == "backward":
                        result_df[column] = result_df[column].fillna(method='bfill')
                    elif method == "mean" and pd.api.types.is_numeric_dtype(result_df[column]) and not pd.api.types.is_categorical_dtype(result_df[column]):
                        try:
                            result_df[column] = result_df[column].fillna(result_df[column].mean())
                        except (TypeError, ValueError):
                            # Skip if mean calculation fails
                            pass
                    elif method == "median" and pd.api.types.is_numeric_dtype(result_df[column]) and not pd.api.types.is_categorical_dtype(result_df[column]):
                        try:
                            result_df[column] = result_df[column].fillna(result_df[column].median())
                        except (TypeError, ValueError):
                            # Skip if median calculation fails
                            pass
            elif step_type == "remove_outliers":
                column = step.get("column")
                method = step.get("method", "zscore")
                threshold = step.get("threshold", 3.0)
                if column and column in result_df.columns and pd.api.types.is_numeric_dtype(result_df[column]) and not pd.api.types.is_categorical_dtype(result_df[column]):
                    from data_quality import detect_outliers
                    outliers_df = detect_outliers(result_df, column, method, threshold)
                    outlier_indices = outliers_df.index
                    result_df = result_df.drop(outlier_indices)
        return result_df
    
    return pipeline


def enrich_data(df: pd.DataFrame, enrichment_source: Dict[str, Any],
               join_key: str) -> pd.DataFrame:
    """Enrich data with external sources.
    
    Args:
        df: DataFrame to enrich
        enrichment_source: External data source (DataFrame or dict)
        join_key: Key column to join on
        
    Returns:
        Enriched DataFrame
    """
    if isinstance(enrichment_source, dict):
        enrichment_df = pd.DataFrame([enrichment_source])
    else:
        enrichment_df = enrichment_source
    
    if join_key not in df.columns or join_key not in enrichment_df.columns:
        return df
    
    enriched = df.merge(enrichment_df, on=join_key, how="left")
    return enriched


def normalize_data_format(df: pd.DataFrame, column: str, format_type: str) -> pd.DataFrame:
    """Normalize data formats (dates, numbers, text).
    
    Args:
        df: DataFrame
        column: Column to normalize
        format_type: Type of normalization (date, number, text, phone, email)
        
    Returns:
        DataFrame with normalized column
    """
    if column not in df.columns:
        return df
    
    result_df = df.copy()
    
    if format_type == "date":
        # Try multiple date formats
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y%m%d"]:
            try:
                result_df[column] = pd.to_datetime(result_df[column], format=fmt, errors='coerce')
                break
            except Exception:
                continue
        else:
            result_df[column] = pd.to_datetime(result_df[column], errors='coerce')
    
    elif format_type == "number":
        result_df[column] = pd.to_numeric(result_df[column], errors='coerce')
    
    elif format_type == "text":
        result_df[column] = result_df[column].astype(str).str.strip().str.lower()
    
    elif format_type == "phone":
        # Remove non-digit characters
        result_df[column] = result_df[column].astype(str).str.replace(r'\D', '', regex=True)
    
    elif format_type == "email":
        # Validate and normalize email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        result_df[column] = result_df[column].astype(str).str.lower()
        result_df[column] = result_df[column].apply(
            lambda x: x if re.match(email_pattern, x) else None
        )
    
    return result_df


def deduplicate_data(df: pd.DataFrame, strategy: str = "keep_first",
                    subset: Optional[List[str]] = None) -> pd.DataFrame:
    """Remove duplicates with various strategies.
    
    Args:
        df: DataFrame
        strategy: Strategy (keep_first, keep_last, remove_all)
        subset: Columns to consider for duplicates
        
    Returns:
        DataFrame with duplicates removed
    """
    if strategy == "keep_first":
        return df.drop_duplicates(subset=subset, keep='first')
    elif strategy == "keep_last":
        return df.drop_duplicates(subset=subset, keep='last')
    elif strategy == "remove_all":
        # Remove all rows that have duplicates
        duplicates = df[df.duplicated(subset=subset, keep=False)]
        return df.drop(duplicates.index)
    else:
        return df.drop_duplicates(subset=subset)


def aggregate_data(df: pd.DataFrame, group_by: List[str],
                  aggregations: Dict[str, List[str]]) -> pd.DataFrame:
    """Aggregate data by groups/categories.
    
    Args:
        df: DataFrame
        group_by: Columns to group by
        aggregations: Dictionary mapping columns to aggregation functions
        
    Returns:
        Aggregated DataFrame
    """
    group_cols = [col for col in group_by if col in df.columns]
    if not group_cols:
        return df
    
    agg_dict = {}
    for col, funcs in aggregations.items():
        if col in df.columns:
            # Skip categorical columns for numeric aggregations
            is_categorical = pd.api.types.is_categorical_dtype(df[col])
            for func in funcs:
                if func == "sum" and (pd.api.types.is_numeric_dtype(df[col]) or is_categorical):
                    agg_dict[col] = "sum"
                elif func == "mean" and pd.api.types.is_numeric_dtype(df[col]) and not is_categorical:
                    agg_dict[col] = "mean"
                elif func == "count":
                    agg_dict[col] = "count"
                elif func == "min":
                    agg_dict[col] = "min"
                elif func == "max":
                    agg_dict[col] = "max"
    
    if agg_dict:
        return df.groupby(group_cols).agg(agg_dict).reset_index()
    else:
        return df.groupby(group_cols).size().reset_index(name='count')

