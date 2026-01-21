# pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import pandas as pd  # type: ignore[import-not-found]
from typing import Any, cast, Dict, Optional
import streamlit as st  # type: ignore[import-not-found]
import hashlib
import json

pd = cast(Any, pd)
st = cast(Any, st)

@st.cache_data(show_spinner=False)
def transform_source_data(
    source_df: Any, 
    final_mapping: Dict[str, Dict[str, Any]]
) -> Any:
    """Transform source data into target layout columns using mappings.

    Copies mapped columns, fills missing columns with `None`, and applies
    simple cleaning rules: trim strings, standardize date-like columns,
    and normalize ID-like fields.

    Args:
        source_df: Source DataFrame-like.
        final_mapping: Mapping dict `{target_field: {"value": source_col}}`.

    Returns:
        Transformed DataFrame-like aligned to target fields.
    """
    return _transform_source_data_internal(source_df, final_mapping)


def transform_claims_data(
    claims_df: Any, 
    final_mapping: Dict[str, Dict[str, Any]]
) -> Any:
    """Transform claims data into internal layout columns using mappings.
    
    Note: This is an alias for transform_source_data() for backward compatibility.
    
    Args:
        claims_df: Source claims DataFrame-like.
        final_mapping: Mapping dict `{internal_field: {"value": source_col}}`.

    Returns:
        Transformed DataFrame-like aligned to internal fields.
    """
    return transform_source_data(claims_df, final_mapping)


def _transform_source_data_internal(source_df: Any, final_mapping: Dict[str, Dict[str, Any]]) -> Any:
    """Internal transformation function (without pipeline)."""
    transformed: Any = pd.DataFrame()

    for target_field, mapping in final_mapping.items():
        source_column = mapping.get("value")
        if source_column and source_column in source_df.columns:
            transformed[target_field] = source_df[source_column]
        else:
            transformed[target_field] = None

    # --- Basic Cleaning Rules ---
    for col in transformed.columns:
        if transformed[col].dtype == object:
            transformed[col] = transformed[col].astype(str).str.strip()  # type: ignore[no-untyped-call]

        if "date" in col.lower():
            s = transformed[col]
            # Convert to string first to handle various input types
            s_str = s.astype(str).str.strip()  # type: ignore[no-untyped-call]
            
            # Try to detect Excel serial dates vs other formats
            numeric = pd.to_numeric(s, errors='coerce')  # type: ignore[no-untyped-call]
            
            # Excel serial dates: typically between 1 and 100000 (covers dates from 1900 to ~2174)
            # Values like 20250916 are YYYYMMDD format (8 digits), not Excel serial dates
            # Check if value looks like YYYYMMDD using vectorized operations
            # Must be exactly 8 digits, all numeric
            is_8_digits = (s_str.str.len() == 8) & (s_str.str.isdigit())  # type: ignore[no-untyped-call]
            # Extract year (first 4 digits) and check if in reasonable range (1900-2100)
            year_str = s_str.str[:4]  # type: ignore[no-untyped-call]
            year_numeric = pd.to_numeric(year_str, errors='coerce')  # type: ignore[no-untyped-call]
            valid_year = (year_numeric >= 1900) & (year_numeric <= 2100)  # type: ignore[operator]
            # Extract month and day for basic validation
            month_str = s_str.str[4:6]  # type: ignore[no-untyped-call]
            day_str = s_str.str[6:8]  # type: ignore[no-untyped-call]
            month_numeric = pd.to_numeric(month_str, errors='coerce')  # type: ignore[no-untyped-call]
            day_numeric = pd.to_numeric(day_str, errors='coerce')  # type: ignore[no-untyped-call]
            valid_month = (month_numeric >= 1) & (month_numeric <= 12)  # type: ignore[operator]
            valid_day = (day_numeric >= 1) & (day_numeric <= 31)  # type: ignore[operator]
            
            # Identify YYYYMMDD format values
            mask_yyyymmdd = is_8_digits & valid_year & valid_month & valid_day  # type: ignore[operator]
            
            # Excel serial dates: between 1 and 100000, and not YYYYMMDD format
            mask_excel = numeric.notna() & (numeric >= 1) & (numeric <= 100000) & ~mask_yyyymmdd  # type: ignore[operator]
            
            result = pd.Series(index=s.index, dtype='object')
            
            # Process YYYYMMDD format first
            if mask_yyyymmdd.any():
                yyyymmdd_values = s_str.loc[mask_yyyymmdd]
                # Parse YYYYMMDD format
                parsed = pd.to_datetime(yyyymmdd_values, format='%Y%m%d', errors='coerce')  # type: ignore[no-untyped-call]
                result.loc[mask_yyyymmdd] = parsed
            
            # Process Excel serial dates
            if mask_excel.any():
                try:
                    excel_dates = pd.to_datetime('1899-12-30') + pd.to_timedelta(numeric.loc[mask_excel].astype(int), unit='D')  # type: ignore[no-untyped-call]
                    result.loc[mask_excel] = excel_dates
                except (OverflowError, ValueError, pd.errors.OutOfBoundsTimedelta):
                    # If Excel conversion fails (overflow), treat as regular date string
                    # Fall back to string parsing
                    result.loc[mask_excel] = pd.to_datetime(s_str.loc[mask_excel], errors='coerce')  # type: ignore[no-untyped-call]
            
            # Process other values as regular date strings
            mask_other = ~mask_excel & ~mask_yyyymmdd
            if mask_other.any():
                # Try parsing as various date formats
                result.loc[mask_other] = pd.to_datetime(s_str.loc[mask_other], errors='coerce')  # type: ignore[no-untyped-call]
            
            # Convert NaT to None
            result = result.where(pd.notna(result), None)  # type: ignore[no-untyped-call]
            transformed[col] = result

        if any(key in col.lower() for key in ["ssn", "npi", "zip", "cpt", "hcpcs"]):
            series = transformed[col].astype(str)  # type: ignore[no-untyped-call]
            cleaned = series.str.replace(r'[^0-9A-Za-z]', '', regex=True)  # type: ignore[no-untyped-call]
            cleaned = cleaned.replace('', pd.NA)  # type: ignore[no-untyped-call]
            cleaned_obj = cleaned.astype('object')  # type: ignore[no-untyped-call]
            cleaned_obj[pd.isna(cleaned_obj)] = None  # type: ignore[no-untyped-call]
            transformed[col] = cleaned_obj

    return transformed

def standardize_date(val: Any) -> Optional[Any]:
    """Standardize a date value from diverse inputs.

    Supports Excel serial dates (values > 40000) and string/parsed timestamps,
    returning `None` for invalids.

    Args:
        val: Input value possibly representing a date.

    Returns:
        Parsed timestamp-like object or `None`.
    """
    if pd.isnull(val) or val == '':
        return None
    try:
        if isinstance(val, (int, float)) and val > 40000:
            return pd.to_datetime('1899-12-30') + pd.to_timedelta(int(val), unit='D')  # type: ignore[no-untyped-call]
        else:
            ts = pd.to_datetime(val, errors='coerce')  # type: ignore[no-untyped-call]
            return ts if not pd.isna(ts) else None
    except Exception:
        return None

def clean_id(val: str) -> Optional[str]:
    """Normalize an identifier by stripping non-alphanumeric characters.

    Args:
        val: Raw identifier string.

    Returns:
        Cleaned alphanumeric identifier or `None` if empty.
    """
    val_clean = ''.join(filter(str.isalnum, val))
    return val_clean if val_clean else None
