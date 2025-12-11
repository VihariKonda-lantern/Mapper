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
def anonymize_claims_data(df: Any, final_mapping: Dict[str, Dict[str, Any]]) -> Any:
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
            def fake_name(row: Dict[str, Any]) -> str:
                base = _safe_row_get(row, insured_id_col) or _safe_row_get(row, patient_id_col) or _safe_row_get(row, source_col) or ""
                seed_val = hash_seed(str(base))
                if "First" in field:
                    return generate_fake_first_name(seed_val)
                elif "Last" in field:
                    return generate_fake_last_name(seed_val)
                elif "Middle" in field:
                    return generate_fake_middle_initial(seed_val)
                else:
                    return "X"
            df_copy[source_col] = df_copy.apply(fake_name, axis=1)  # type: ignore[no-untyped-call]

        elif field in SSN_FIELDS:
            def fake_ssn(row: Dict[str, Any]) -> str:
                base = _safe_row_get(row, insured_id_col) or _safe_row_get(row, patient_id_col) or _safe_row_get(row, source_col) or ""
                seed_val = hash_seed(str(base))
                return generate_fake_ssn(seed_val)
            df_copy[source_col] = df_copy.apply(fake_ssn, axis=1)  # type: ignore[no-untyped-call]

    return df_copy
