"""
pyright: reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false
"""
# --- diagnosis_loader.py ---
from typing import Tuple, Set, Any, Optional
import pandas as pd  # type: ignore[import-not-found]
import streamlit as st  # type: ignore[import-not-found]
import os
import json

st: Any = st  # type: ignore[assignment]
pd: Any = pd  # type: ignore[assignment]
import io


@st.cache_data(show_spinner=False)
def _load_msk_bar_lookups_cached(content: bytes, file_ext: str) -> Tuple[Set[str], Set[str]]:
    """Parse MSK and BAR diagnosis codes from a file buffer.

    Supports all file formats (CSV, TXT, TSV, XLSX, XLS, JSON, PARQUET).
    For Excel files, uses sheets ("MSK" and "BAR"). For other formats,
    expects columns named "MSK" and "BAR" or first two columns.

    This function is cached via Streamlit to avoid repeated parsing.

    Args:
        content: Raw bytes of the uploaded file.
        file_ext: File extension (e.g., ".xlsx", ".csv").

    Returns:
        A tuple of (`msk_codes`, `bar_codes`) as sets of strings.

    Raises:
        ValueError: If the file cannot be read, or required data is missing.
    """
    file_ext_lower = file_ext.lower()
    file_like = io.BytesIO(content)
    
    try:
        if file_ext_lower in ['.xlsx', '.xls']:
            # Excel format - look for MSK and BAR sheets
            xls = pd.ExcelFile(file_like)
            sheets = xls.sheet_names
            
            required_sheets = ["MSK", "BAR"]
            missing_sheets = [sheet for sheet in required_sheets if sheet not in sheets]
            if missing_sheets:
                raise ValueError(f"Missing required sheets: {', '.join(missing_sheets)}")
            
            msk_df = pd.read_excel(io.BytesIO(content), sheet_name="MSK", dtype=str)  # type: ignore[no-untyped-call]
            bar_df = pd.read_excel(io.BytesIO(content), sheet_name="BAR", dtype=str)  # type: ignore[no-untyped-call]
            
            msk_codes = set(msk_df.iloc[:, 0].dropna().astype(str).str.strip())
            bar_codes = set(bar_df.iloc[:, 0].dropna().astype(str).str.strip())
            
        elif file_ext_lower in ['.csv', '.tsv', '.txt']:
            # CSV/TSV/TXT format - look for MSK and BAR columns
            from data.file_handler import detect_delimiter, has_header
            file_like.seek(0)
            delimiter = detect_delimiter(file_like)
            file_like.seek(0)
            has_hdr = has_header(file_like, delimiter)
            header = 0 if has_hdr else None
            
            df = pd.read_csv(io.BytesIO(content), delimiter=delimiter, header=header, dtype=str)  # type: ignore[no-untyped-call]
            
            # Try to find MSK and BAR columns
            if "MSK" in df.columns and "BAR" in df.columns:
                msk_codes = set(df["MSK"].dropna().astype(str).str.strip())
                bar_codes = set(df["BAR"].dropna().astype(str).str.strip())
            elif len(df.columns) >= 2:
                # Use first two columns
                msk_codes = set(df.iloc[:, 0].dropna().astype(str).str.strip())
                bar_codes = set(df.iloc[:, 1].dropna().astype(str).str.strip())
            else:
                raise ValueError("Lookup file must have at least 2 columns (MSK and BAR codes)")
                
        elif file_ext_lower == '.json':
            # JSON format
            data = json.load(io.TextIOWrapper(io.BytesIO(content), encoding="utf-8"))
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.json_normalize(data)  # type: ignore[no-untyped-call]
            
            if "MSK" in df.columns and "BAR" in df.columns:
                msk_codes = set(df["MSK"].dropna().astype(str).str.strip())
                bar_codes = set(df["BAR"].dropna().astype(str).str.strip())
            elif len(df.columns) >= 2:
                msk_codes = set(df.iloc[:, 0].dropna().astype(str).str.strip())
                bar_codes = set(df.iloc[:, 1].dropna().astype(str).str.strip())
            else:
                raise ValueError("Lookup file must have at least 2 columns (MSK and BAR codes)")
                
        elif file_ext_lower == '.parquet':
            # Parquet format
            df = pd.read_parquet(io.BytesIO(content))  # type: ignore[no-untyped-call]
            
            if "MSK" in df.columns and "BAR" in df.columns:
                msk_codes = set(df["MSK"].dropna().astype(str).str.strip())
                bar_codes = set(df["BAR"].dropna().astype(str).str.strip())
            elif len(df.columns) >= 2:
                msk_codes = set(df.iloc[:, 0].dropna().astype(str).str.strip())
                bar_codes = set(df.iloc[:, 1].dropna().astype(str).str.strip())
            else:
                raise ValueError("Lookup file must have at least 2 columns (MSK and BAR codes)")
        else:
            raise ValueError(f"Unsupported file format for lookup file: {file_ext}")
        
        return msk_codes, bar_codes

    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Unable to read Lookup file: {e}") from e

def load_msk_bar_lookups(file: Any) -> Tuple[Set[str], Set[str]]:
    """Load the Lookup file and extract MSK/BAR code sets.

    Supports all file formats (CSV, TXT, TSV, XLSX, XLS, JSON, PARQUET).
    For Excel files, expects "MSK" and "BAR" sheets.
    For other formats, expects "MSK" and "BAR" columns or uses first two columns.

    Args:
        file: Streamlit-uploaded file-like object for the lookup file.

    Returns:
        A tuple of (`msk_codes`, `bar_codes`) as sets of strings.

    Raises:
        ValueError: If required data is missing or file cannot be read.
    """
    file.seek(0)
    content = file.read()
    file.seek(0)
    
    ext = os.path.splitext(file.name)[-1].lower()
    return _load_msk_bar_lookups_cached(content, ext)
