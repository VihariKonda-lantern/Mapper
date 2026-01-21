# pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import pandas as pd  # type: ignore[import-not-found]
import streamlit as st  # type: ignore[import-not-found]
import random
import hashlib
from typing import Any, Dict, Optional, cast

st = cast(Any, st)
pd = cast(Any, pd)

# local helper to safely read a possibly-None key
def _safe_row_get(row: Dict[str, Any], key: Optional[str]) -> Any:
    if key is None:
        return None
    return row.get(key)

# --- Constants ---
NAME_FIELDS = [
    "Insured_First_Name", "Insured_Last_Name", "Insured_Middle_Initial",
    "Patient_First_Name", "Patient_Last_Name", "Patient_Middle_Initial"
]

SSN_FIELDS = ["Insured_SSN", "Patient_SSN"]

FIRST_SYLLABLES = ["Jo", "Mi", "Ra", "Ka", "De", "El", "Sa", "Lu", "Ti", "Zo"]
LAST_SYLLABLES = ["lin", "den", "von", "mar", "tis", "berg", "ton", "sor", "ley", "vick"]

# Seed offsets for generating different fake data from same base
LAST_NAME_SEED_OFFSET = 42
MIDDLE_INITIAL_SEED_OFFSET = 99

# --- Helper functions ---
def hash_seed(value: str) -> int:
    return int(hashlib.sha256(value.encode()).hexdigest(), 16) % (10 ** 8)

def generate_fake_first_name(seed_val: int) -> str:
    random.seed(seed_val)
    return random.choice(FIRST_SYLLABLES) + random.choice(FIRST_SYLLABLES)

def generate_fake_last_name(seed_val: int) -> str:
    random.seed(seed_val + LAST_NAME_SEED_OFFSET)
    return random.choice(LAST_SYLLABLES).capitalize() + random.choice(LAST_SYLLABLES)

def generate_fake_middle_initial(seed_val: int) -> str:
    random.seed(seed_val + MIDDLE_INITIAL_SEED_OFFSET)
    return random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def generate_fake_ssn(seed_val: int) -> str:
    random.seed(seed_val)
    return f"{random.randint(100, 899)}-{random.randint(10, 89):02}-{random.randint(1000, 9999):04}"

# --- Main function ---
@st.cache_data(show_spinner=False)
def anonymize_source_data(df: Any, final_mapping: Dict[str, Dict[str, Any]], config: Optional[Any] = None) -> Any:
    """Anonymize source data by replacing sensitive fields with fake data.
    
    Generic version that can be configured per domain. For backward compatibility,
    defaults to healthcare-specific fields (names, SSNs).
    
    Args:
        df: Source DataFrame to anonymize.
        final_mapping: Mapping dictionary.
        config: DomainConfig instance. If None, uses default healthcare fields.
    
    Returns:
        Anonymized DataFrame.
    """
    # For now, use healthcare-specific logic (backward compatible)
    # In future, can make this configurable via domain config
    return anonymize_claims_data(df, final_mapping)


@st.cache_data(show_spinner=False)
def anonymize_claims_data(df: Any, final_mapping: Dict[str, Dict[str, Any]]) -> Any:
    """Anonymize claims data by replacing sensitive fields with fake data.
    
    Note: This is a healthcare-specific implementation. For generic use,
    see anonymize_source_data().
    
    Args:
        df: Source DataFrame to anonymize.
        final_mapping: Mapping dictionary.
    
    Returns:
        Anonymized DataFrame.
    """
    df_copy = df.copy()

    insured_id_col: Optional[str] = None
    patient_id_col: Optional[str] = None

    for field, mapping_info in final_mapping.items():
        if mapping_info.get("value"):
            if field == "Insured_ID":
                insured_id_col = mapping_info["value"]
            elif field == "Patient_ID":
                patient_id_col = mapping_info["value"]

    for field, mapping_info in final_mapping.items():
        source_col = mapping_info.get("value")
        if not source_col or source_col not in df_copy.columns:
            continue

        if field in NAME_FIELDS:
            # Vectorized approach: create base values using pandas operations
            # Get base column (prefer insured_id, then patient_id, then source_col itself)
            base_series = pd.Series("", index=df_copy.index, dtype=str)
            if insured_id_col and insured_id_col in df_copy.columns:
                # Handle categorical columns by converting to string first
                col_data = df_copy[insured_id_col]
                if pd.api.types.is_categorical_dtype(col_data):
                    base_series = col_data.astype(str).fillna("")
                else:
                    base_series = col_data.fillna("").astype(str)
            elif patient_id_col and patient_id_col in df_copy.columns:
                # Handle categorical columns by converting to string first
                col_data = df_copy[patient_id_col]
                if pd.api.types.is_categorical_dtype(col_data):
                    base_series = col_data.astype(str).fillna("")
                else:
                    base_series = col_data.fillna("").astype(str)
            else:
                # Handle categorical columns by converting to string first
                col_data = df_copy[source_col]
                if pd.api.types.is_categorical_dtype(col_data):
                    base_series = col_data.astype(str).fillna("")
                else:
                    base_series = col_data.fillna("").astype(str)
            
            # Vectorized hash calculation and fake name generation
            def generate_names_vectorized(base_str: str, field_name: str) -> str:
                if not base_str:
                    return ""
                seed_val = hash_seed(base_str)
                if "First" in field_name:
                    return generate_fake_first_name(seed_val)
                elif "Last" in field_name:
                    return generate_fake_last_name(seed_val)
                elif "Middle" in field_name:
                    return generate_fake_middle_initial(seed_val)
                else:
                    return "X"
            
            # Apply vectorized function (still uses apply but on Series, which is faster)
            df_copy[source_col] = base_series.apply(lambda x: generate_names_vectorized(x, field))  # type: ignore[no-untyped-call]

        elif field in SSN_FIELDS:
            # Vectorized approach for SSN
            base_series = pd.Series("", index=df_copy.index, dtype=str)
            if insured_id_col and insured_id_col in df_copy.columns:
                # Handle categorical columns by converting to string first
                col_data = df_copy[insured_id_col]
                if pd.api.types.is_categorical_dtype(col_data):
                    base_series = col_data.astype(str).fillna("")
                else:
                    base_series = col_data.fillna("").astype(str)
            elif patient_id_col and patient_id_col in df_copy.columns:
                # Handle categorical columns by converting to string first
                col_data = df_copy[patient_id_col]
                if pd.api.types.is_categorical_dtype(col_data):
                    base_series = col_data.astype(str).fillna("")
                else:
                    base_series = col_data.fillna("").astype(str)
            else:
                # Handle categorical columns by converting to string first
                col_data = df_copy[source_col]
                if pd.api.types.is_categorical_dtype(col_data):
                    base_series = col_data.astype(str).fillna("")
                else:
                    base_series = col_data.fillna("").astype(str)
            
            # Vectorized SSN generation
            df_copy[source_col] = base_series.apply(lambda x: generate_fake_ssn(hash_seed(x)) if x else "")  # type: ignore[no-untyped-call]

    return df_copy
