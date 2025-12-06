# pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import pandas as pd  # type: ignore[import-not-found]
from typing import Any, cast

pd = cast(Any, pd)
from typing import Dict, Any, Optional

def transform_claims_data(claims_df: Any, final_mapping: Dict[str, Dict[str, Any]]) -> Any:
    """
    Transforms claims file based on final_mapping.
    Standardizes dates, strips strings, and cleans ID fields.
    """
    transformed: Any = pd.DataFrame()

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
            s = transformed[col]
            # Handle Excel serial dates (numeric > 40000) and general parsing vectorized
            numeric = pd.to_numeric(s, errors='coerce')  # type: ignore[no-untyped-call]
            mask_excel = numeric.notna() & (numeric > 40000)
            result = pd.Series(index=s.index, dtype='datetime64[ns]')
            result.loc[mask_excel] = pd.to_datetime('1899-12-30') + pd.to_timedelta(numeric.loc[mask_excel].astype(int), unit='D')  # type: ignore[no-untyped-call]
            mask_other = ~mask_excel
            result.loc[mask_other] = pd.to_datetime(s.loc[mask_other], errors='coerce')  # type: ignore[no-untyped-call]
            # Match previous behaviour: invalids as None (not NaT)
            result_obj = result.astype('object')
            result_obj[pd.isna(result_obj)] = None  # type: ignore[no-untyped-call]
            transformed[col] = result_obj

        if any(key in col.lower() for key in ["ssn", "npi", "zip", "cpt", "hcpcs"]):
            series = transformed[col].astype(str)  # type: ignore[no-untyped-call]
            cleaned = series.str.replace(r'[^0-9A-Za-z]', '', regex=True)  # type: ignore[no-untyped-call]
            cleaned = cleaned.replace('', pd.NA)  # type: ignore[no-untyped-call]
            cleaned_obj = cleaned.astype('object')  # type: ignore[no-untyped-call]
            cleaned_obj[pd.isna(cleaned_obj)] = None  # type: ignore[no-untyped-call]
            transformed[col] = cleaned_obj

    return transformed

def standardize_date(val: Any) -> Optional[Any]:
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
