"""
pyright: reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownMemberType=false
"""
# --- diagnosis_loader.py ---
from typing import Tuple, Set, Any
import pandas as pd  # type: ignore[import-not-found]
import streamlit as st  # type: ignore[import-not-found]

st: Any = st  # type: ignore[assignment]
pd: Any = pd  # type: ignore[assignment]
import io


@st.cache_data(show_spinner=False)
def _load_msk_bar_lookups_cached(content: bytes) -> Tuple[Set[str], Set[str]]:
    try:
        xls = pd.ExcelFile(io.BytesIO(content))
        sheets = xls.sheet_names
    except Exception as e:
        raise ValueError("Unable to read Diagnosis Lookup file.") from e

    required_sheets = ["MSK", "BAR"]
    missing_sheets = [sheet for sheet in required_sheets if sheet not in sheets]
    if missing_sheets:
        raise ValueError(f"Missing required sheets: {', '.join(missing_sheets)}")

    try:
        msk_df = pd.read_excel(io.BytesIO(content), sheet_name="MSK", dtype=str)  # type: ignore[no-untyped-call]
        bar_df = pd.read_excel(io.BytesIO(content), sheet_name="BAR", dtype=str)  # type: ignore[no-untyped-call]

        msk_codes = set(msk_df.iloc[:, 0].dropna().str.strip())
        bar_codes = set(bar_df.iloc[:, 0].dropna().str.strip())

        return msk_codes, bar_codes

    except Exception as e:
        raise ValueError("Error parsing Diagnosis Lookup sheets.") from e

def load_msk_bar_lookups(file: Any) -> Tuple[Set[str], Set[str]]:
    """
    Loads the Diagnosis Lookup file and extracts MSK and BAR code sets.

    Args:
        file: Uploaded Streamlit file-like object (.xlsx)

    Returns:
        Tuple containing:
        - Set of MSK diagnosis codes
        - Set of BAR diagnosis codes

    Raises:
        ValueError: If expected sheets or columns are missing
    """
    file.seek(0)
    content = file.read()
    file.seek(0)
    return _load_msk_bar_lookups_cached(content)
