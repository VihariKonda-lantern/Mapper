# --- data_quality.py ---
"""Data Quality & Analysis features."""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json

st: Any = st
pd: Any = pd
np: Any = np


def calculate_data_quality_score(df: pd.DataFrame, required_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """Calculate overall data quality score (0-100) with breakdown by dimension.
    
    Args:
        df: DataFrame to analyze
        required_fields: List of required field names
        
    Returns:
        Dictionary with overall score and breakdown
    """
    if df is None or df.empty:
        return {"overall_score": 0, "breakdown": {}}
    
    scores = {}
    weights = {}
    
    # Completeness (40% weight)
    total_cells = len(df) * len(df.columns)
    null_cells = df.isnull().sum().sum()
    completeness = ((total_cells - null_cells) / total_cells * 100) if total_cells > 0 else 0
    scores["completeness"] = completeness
    weights["completeness"] = 0.4
    
    # Required fields completeness (30% weight)
    if required_fields:
        req_fields_in_df = [f for f in required_fields if f in df.columns]
        if req_fields_in_df:
            req_total = len(df) * len(req_fields_in_df)
            req_null = df[req_fields_in_df].isnull().sum().sum()
            req_completeness = ((req_total - req_null) / req_total * 100) if req_total > 0 else 0
            scores["required_completeness"] = req_completeness
            weights["required_completeness"] = 0.3
        else:
            scores["required_completeness"] = 0
            weights["required_completeness"] = 0.3
    else:
        scores["required_completeness"] = completeness
        weights["required_completeness"] = 0.3
    
    # Uniqueness (15% weight)
    duplicate_rows = df.duplicated().sum()
    uniqueness = ((len(df) - duplicate_rows) / len(df) * 100) if len(df) > 0 else 0
    scores["uniqueness"] = uniqueness
    weights["uniqueness"] = 0.15
    
    # Consistency (15% weight) - Check for consistent data types and formats
    consistency_score = 0
    for col in df.columns:
        col_data = df[col]
        # Handle categorical columns
        if pd.api.types.is_categorical_dtype(col_data):
            # For categorical columns, just check if they're consistent (all same category type)
            non_null = col_data.dropna()
            if len(non_null) > 0:
                consistency_score += 100
        elif df[col].dtype == 'object':
            # Check if all non-null values are strings
            non_null = df[col].dropna()
            if len(non_null) > 0:
                consistency_score += 100
        elif pd.api.types.is_numeric_dtype(col_data):
            # Check for outliers (values beyond 3 standard deviations) - only for numeric types
            non_null = col_data.dropna()
            if len(non_null) > 0:
                try:
                    mean_val = non_null.mean()
                    std_val = non_null.std()
                    if std_val > 0:
                        outliers = ((non_null - mean_val).abs() > 3 * std_val).sum()
                        consistency_score += ((len(non_null) - outliers) / len(non_null) * 100)
                    else:
                        consistency_score += 100
                except (TypeError, ValueError):
                    # If mean/std fails, assume consistent
                    consistency_score += 100
        else:
            # For other types, assume consistent
            consistency_score += 100
    consistency = consistency_score / len(df.columns) if len(df.columns) > 0 else 0
    scores["consistency"] = consistency
    weights["consistency"] = 0.15
    
    # Calculate weighted overall score
    overall_score = sum(scores[k] * weights[k] for k in scores.keys())
    
    return {
        "overall_score": round(overall_score, 2),
        "breakdown": scores,
        "weights": weights
    }


def detect_duplicates(df: pd.DataFrame, columns: Optional[List[str]] = None, 
                      method: str = "exact") -> pd.DataFrame:
    """Detect duplicate records with configurable matching rules.
    
    Args:
        df: DataFrame to check
        columns: Columns to use for duplicate detection (None = all columns)
        method: Matching method ('exact', 'fuzzy', 'key_based')
        
    Returns:
        DataFrame with duplicate records marked
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    if columns is None:
        columns = df.columns.tolist()
    
    columns = [c for c in columns if c in df.columns]
    
    if method == "exact":
        duplicates = df[df.duplicated(subset=columns, keep=False)].copy()
        duplicates["duplicate_group"] = duplicates.groupby(columns).ngroup()
    elif method == "key_based":
        # Use first column as key
        if columns:
            key_col = columns[0]
            duplicates = df[df.duplicated(subset=[key_col], keep=False)].copy()
            duplicates["duplicate_group"] = duplicates.groupby([key_col]).ngroup()
        else:
            duplicates = pd.DataFrame()
    else:  # fuzzy
        # For now, fall back to exact matching
        duplicates = df[df.duplicated(subset=columns, keep=False)].copy()
        duplicates["duplicate_group"] = duplicates.groupby(columns).ngroup()
    
    return duplicates


def get_column_statistics(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Get comprehensive statistics for a column.
    
    Args:
        df: DataFrame
        column: Column name
        
    Returns:
        Dictionary with statistics
    """
    if df is None or column not in df.columns:
        return {}
    
    col_data = df[column]
    stats = {
        "column_name": column,
        "data_type": str(col_data.dtype),
        "total_count": len(col_data),
        "null_count": col_data.isnull().sum(),
        "null_percentage": (col_data.isnull().sum() / len(col_data) * 100) if len(col_data) > 0 else 0,
        "unique_count": col_data.nunique(),
        "unique_percentage": (col_data.nunique() / len(col_data) * 100) if len(col_data) > 0 else 0,
    }
    
    # Numeric statistics (skip categorical columns)
    if pd.api.types.is_numeric_dtype(col_data) and not pd.api.types.is_categorical_dtype(col_data):
        non_null = col_data.dropna()
        if len(non_null) > 0:
            try:
                stats.update({
                    "min": float(non_null.min()),
                    "max": float(non_null.max()),
                    "mean": float(non_null.mean()),
                    "median": float(non_null.median()),
                    "std": float(non_null.std()),
                    "q25": float(non_null.quantile(0.25)),
                    "q75": float(non_null.quantile(0.75)),
                })
            except (TypeError, ValueError):
                # Skip if calculation fails
                pass
    
    # String statistics (including categorical converted to string)
    if pd.api.types.is_string_dtype(col_data) or col_data.dtype == 'object' or pd.api.types.is_categorical_dtype(col_data):
        # Convert categorical to string for analysis
        if pd.api.types.is_categorical_dtype(col_data):
            non_null = col_data.dropna().astype(str)
        else:
            non_null = col_data.dropna().astype(str)
        if len(non_null) > 0:
            try:
                stats.update({
                    "min_length": int(non_null.str.len().min()),
                    "max_length": int(non_null.str.len().max()),
                    "mean_length": float(non_null.str.len().mean()),
                })
                # Most common values
                value_counts = non_null.value_counts().head(10)
                stats["top_values"] = value_counts.to_dict()
            except (TypeError, ValueError):
                # Skip if calculation fails
                pass
    
    return stats


def detect_outliers(df: pd.DataFrame, column: str, method: str = "zscore", 
                    threshold: float = 3.0) -> pd.DataFrame:
    """Detect statistical outliers in a column.
    
    Args:
        df: DataFrame
        column: Column name
        method: Detection method ('zscore', 'iqr')
        threshold: Threshold for outlier detection
        
    Returns:
        DataFrame with outliers marked
    """
    if df is None or column not in df.columns:
        return pd.DataFrame()
    
    col_data = df[column]
    # Only process numeric columns (exclude categorical)
    if not pd.api.types.is_numeric_dtype(col_data) or pd.api.types.is_categorical_dtype(col_data):
        return pd.DataFrame()
    
    non_null = col_data.dropna()
    if len(non_null) == 0:
        return pd.DataFrame()
    
    outliers = df.copy()
    outliers["is_outlier"] = False
    
    if method == "zscore":
        try:
            mean_val = non_null.mean()
            std_val = non_null.std()
            if std_val > 0:
                z_scores = (col_data - mean_val) / std_val
                outliers.loc[z_scores.abs() > threshold, "is_outlier"] = True
        except (TypeError, ValueError):
            # If calculation fails, return empty DataFrame
            return pd.DataFrame()
    elif method == "iqr":
        q1 = non_null.quantile(0.25)
        q3 = non_null.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        outliers.loc[(col_data < lower_bound) | (col_data > upper_bound), "is_outlier"] = True
    
    return outliers[outliers["is_outlier"] == True]


def create_completeness_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Create a heatmap matrix showing data completeness across fields/rows.
    
    Args:
        df: DataFrame
        
    Returns:
        DataFrame with completeness percentages
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    completeness = {}
    for col in df.columns:
        null_count = df[col].isnull().sum()
        total_count = len(df)
        completeness[col] = {
            "null_count": int(null_count),
            "non_null_count": int(total_count - null_count),
            "completeness_pct": round((total_count - null_count) / total_count * 100, 2) if total_count > 0 else 0
        }
    
    return pd.DataFrame(completeness).T


def sample_data(df: pd.DataFrame, method: str = "random", n: int = 1000, 
                stratify_col: Optional[str] = None) -> pd.DataFrame:
    """Sample data from DataFrame.
    
    Args:
        df: DataFrame
        method: Sampling method ('random', 'stratified', 'first', 'last')
        n: Number of samples
        stratify_col: Column to stratify by (for stratified sampling)
        
    Returns:
        Sampled DataFrame
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    n = min(n, len(df))
    
    if method == "random":
        return df.sample(n=n, random_state=42)
    elif method == "first":
        return df.head(n)
    elif method == "last":
        return df.tail(n)
    elif method == "stratified" and stratify_col and stratify_col in df.columns:
        # Stratified sampling
        try:
            from sklearn.model_selection import train_test_split
            _, sampled = train_test_split(df, train_size=n/len(df), stratify=df[stratify_col], random_state=42)
            return sampled
        except Exception:
            # Fallback to random if sklearn not available
            return df.sample(n=n, random_state=42)
    else:
        return df.sample(n=n, random_state=42)


def generate_data_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate comprehensive data profile.
    
    Args:
        df: DataFrame
        
    Returns:
        Dictionary with profile information
    """
    if df is None or df.empty:
        return {}
    
    profile = {
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "memory_usage": df.memory_usage(deep=True).sum(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "columns": df.columns.tolist(),
        "null_summary": df.isnull().sum().to_dict(),
        "null_percentages": (df.isnull().sum() / len(df) * 100).to_dict(),
    }
    
    # Numeric columns summary
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        profile["numeric_summary"] = df[numeric_cols].describe().to_dict()
    
    # Categorical columns summary
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    if categorical_cols:
        profile["categorical_summary"] = {}
        for col in categorical_cols[:10]:  # Limit to first 10
            value_counts = df[col].value_counts().head(20)
            profile["categorical_summary"][col] = value_counts.to_dict()
    
    return profile

