import pandas as pd
from typing import Dict, Any, Optional

def transform_claims_data(claims_df: pd.DataFrame, final_mapping: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """
    Transforms claims file based on final_mapping.
    Standardizes dates, strips strings, and cleans ID fields.
    """
    transformed: pd.DataFrame = pd.DataFrame()

    for internal_field, mapping in final_mapping.items():
        source_column = mapping.get("value")
        if source_column and source_column in claims_df.columns:
            transformed[internal_field] = claims_df[source_column]
        else:
            transformed[internal_field] = None

    # --- Basic Cleaning Rules ---
    for col in transformed.columns:
        if transformed[col].dtype == object:
            transformed[col] = transformed[col].astype(str).str.strip()  # type: ignore[no-untyped-call]

        if "date" in col.lower():
            transformed[col] = transformed[col].apply(lambda x: standardize_date(x))  # type: ignore[no-untyped-call]

        if any(key in col.lower() for key in ["ssn", "npi", "zip", "cpt", "hcpcs"]):
            transformed[col] = transformed[col].apply(lambda x: clean_id(str(x)))  # type: ignore[no-untyped-call]

    return transformed

def standardize_date(val: Any) -> Optional[pd.Timestamp]:
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
    val_clean = ''.join(filter(str.isalnum, val))  # Keep only alphanumeric
    return val_clean if val_clean else None
