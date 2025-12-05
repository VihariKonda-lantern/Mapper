# --- diagnosis_loader.py ---
import pandas as pd
from typing import Tuple, Set, Any


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
    try:
        xls = pd.ExcelFile(file)
        sheets = xls.sheet_names
    except Exception as e:
        raise ValueError("Unable to read Diagnosis Lookup file.") from e

    required_sheets = ["MSK", "BAR"]
    missing_sheets = [sheet for sheet in required_sheets if sheet not in sheets]
    if missing_sheets:
        raise ValueError(f"Missing required sheets: {', '.join(missing_sheets)}")

    try:
        msk_df = pd.read_excel(file, sheet_name="MSK", dtype=str)  # type: ignore[no-untyped-call]
        bar_df = pd.read_excel(file, sheet_name="BAR", dtype=str)  # type: ignore[no-untyped-call]

        msk_codes = set(msk_df.iloc[:, 0].dropna().str.strip())
        bar_codes = set(bar_df.iloc[:, 0].dropna().str.strip())

        return msk_codes, bar_codes

    except Exception as e:
        raise ValueError("Error parsing Diagnosis Lookup sheets.") from e
