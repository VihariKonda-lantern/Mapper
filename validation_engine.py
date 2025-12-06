# pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import pandas as pd  # type: ignore[import-not-found]
from datetime import datetime
from typing import List, Dict, Any, cast
import streamlit as st  # type: ignore[import-not-found]

st = cast(Any, st)
pd = cast(Any, pd)

# ================================================================
# 📄 FIELD-LEVEL VALIDATIONS (Row-by-Row Checks)
# ================================================================

def check_required_fields_completeness(df: Any, final_mapping: Dict[str, Dict[str, Any]]) -> float:
    """Calculates % completeness for required fields."""
    required_fields = [field for field, mapping in final_mapping.items() if mapping.get("value")]
    if not required_fields:
        return 0.0

    total_cells = df[required_fields].shape[0] * len(required_fields)
    filled_cells = df[required_fields].notnull().sum().sum()  # type: ignore[no-untyped-call]
    completeness: float = (filled_cells / total_cells) * 100 if total_cells > 0 else 0.0
    return completeness

def check_age_validation(df: Any) -> float:
    """Checks percentage of patients 18+ based on Patient_DOB."""
    if "Patient_DOB" not in df.columns:
        return 0.0

    today = datetime.today()
    dob = pd.to_datetime(df["Patient_DOB"], errors="coerce")  # type: ignore[no-untyped-call]
    age = (today - dob).dt.days / 365.25
    over_18 = age >= 18
    valid_count = over_18.sum()
    return (valid_count / len(df)) * 100 if len(df) > 0 else 0.0

def check_date_range(df: Any) -> float:
    """Checks if Begin_Date is within last 6 months."""
    if "Begin_Date" not in df.columns:
        return 0.0

    today = datetime.today()
    six_months_ago = today - pd.DateOffset(months=6)
    begin_date = pd.to_datetime(df["Begin_Date"], errors="coerce")  # type: ignore[no-untyped-call]
    valid_dates = begin_date >= six_months_ago
    valid_count = valid_dates.sum()
    return (valid_count / len(df)) * 100 if len(df) > 0 else 0.0

def check_required_fields(df: Any, required_fields: List[str]) -> List[Dict[str, Any]]:
    """Check if required fields are non-null for all rows."""
    results: List[Dict[str, Any]] = []
    for field in required_fields:
        if field in df.columns:
            missing = df[field].isnull().sum()
            if missing > 0:
                results.append({
                    "field": field,
                    "check": "Required Field Check",
                    "status": "Fail",
                    "message": f"{missing} missing values"
                })
            else:
                results.append({
                    "field": field,
                    "check": "Required Field Check",
                    "status": "Pass",
                    "message": "No missing values"
                })
    return results

def check_date_validity(df: Any, date_fields: List[str]) -> List[Dict[str, Any]]:
    """Check that dates are valid and not way out of range."""
    results: List[Dict[str, Any]] = []
    for field in date_fields:
        if field in df.columns:
            invalid_dates = df[field].isnull().sum()
            if invalid_dates > 0:
                results.append({
                    "field": field,
                    "check": "Date Validity Check",
                    "status": "Warning",
                    "message": f"{invalid_dates} invalid/missing dates"
                })
            else:
                results.append({
                    "field": field,
                    "check": "Date Validity Check",
                    "status": "Pass",
                    "message": "All dates valid"
                })
    return results

def check_age_over_18(df: Any, dob_field: str) -> List[Dict[str, Any]]:
    """Check that patients are over 18 years old."""
    results: List[Dict[str, Any]] = []
    if dob_field in df.columns:
        today = pd.Timestamp.today()
        df["calculated_age"] = (today - pd.to_datetime(df[dob_field], errors='coerce')).dt.days // 365  # type: ignore[no-untyped-call]
        underage = df[df["calculated_age"] < 18].shape[0]

        if underage > 0:
            results.append({
                "field": dob_field,
                "check": "Age ≥ 18 Check",
                "status": "Fail",
                "message": f"{underage} patients under 18"
            })
        else:
            results.append({
                "field": dob_field,
                "check": "Age ≥ 18 Check",
                "status": "Pass",
                "message": "All patients 18 or older"
            })

        df.drop(columns=["calculated_age"], inplace=True)

    return results

def check_fill_rate(df: Any, mapped_fields: List[str]) -> List[Dict[str, Any]]:
    """Check that mapped fields have a decent fill rate (warn if too sparse)."""
    results: List[Dict[str, Any]] = []
    for field in mapped_fields:
        if field in df.columns:
            fill_rate = 100 * df[field].notnull().sum() / len(df)
            if fill_rate < 50:
                results.append({
                    "field": field,
                    "check": "Fill Rate Check",
                    "status": "Warning",
                    "message": f"Low fill rate: {fill_rate:.1f}%"
                })
            else:
                results.append({
                    "field": field,
                    "check": "Fill Rate Check",
                    "status": "Pass",
                    "message": f"Fill rate: {fill_rate:.1f}%"
                })
    return results

@st.cache_data(show_spinner=False)
def run_validations(transformed_df: Any, required_fields: List[str], mapped_fields: List[str]) -> List[Dict[str, Any]]:
    """Runs all validations and returns a list of validation results."""
    results: List[Dict[str, Any]] = []
    results.extend(check_required_fields(transformed_df, required_fields))

    date_fields = [col for col in transformed_df.columns if "date" in col.lower()]
    results.extend(check_date_validity(transformed_df, date_fields))

    dob_field = None
    if "Patient_DOB" in transformed_df.columns:
        dob_field = "Patient_DOB"
    elif "Insured_DOB" in transformed_df.columns:
        dob_field = "Insured_DOB"

    if dob_field:
        results.extend(check_age_over_18(transformed_df, dob_field))

    results.extend(check_fill_rate(transformed_df, mapped_fields))

    return results

# ================================================================
# 📄 FILE-LEVEL VALIDATIONS (File Completeness / Range Checks)
# ================================================================

def run_required_field_check(df: Any, final_mapping: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Check overall required field completeness % for the file."""
    required_fields = list(final_mapping.keys())
    missing_values = df[required_fields].isnull().sum().sum()  # type: ignore[no-untyped-call]
    total_cells = df[required_fields].shape[0] * len(required_fields)
    completeness = (total_cells - missing_values) / total_cells * 100 if total_cells > 0 else 0.0
    status = "Pass" if completeness >= 98 else "Fail"

    return {
        "check": "Required Fields Completeness",
        "status": status,
        "message": f"{completeness:.1f}% fields filled"
    }

def run_age_check(df: Any, dob_field: str) -> Dict[str, Any]:
    """Check if 90%+ patients are 18+."""
    today = pd.Timestamp.today()
    dob = pd.to_datetime(df[dob_field], errors="coerce")  # type: ignore[no-untyped-call]
    age = (today - dob).dt.days / 365.25
    over_18_pct = (age >= 18).sum() / len(df) * 100 if len(df) > 0 else 0.0
    status = "Pass" if over_18_pct >= 90 else "Fail"

    return {
        "check": "Age Validation (18+)",
        "status": status,
        "message": f"{over_18_pct:.1f}% patients are 18+"
    }

def run_date_range_check(df: Any, date_field: str) -> Dict[str, Any]:
    """Check if 80%+ claims fall within last 6 months."""
    today = pd.Timestamp.today()
    six_months_ago = today - pd.DateOffset(months=6)
    service_dates = pd.to_datetime(df[date_field], errors="coerce")  # type: ignore[no-untyped-call]
    valid_dates_pct = (service_dates >= six_months_ago).sum() / len(df) * 100 if len(df) > 0 else 0.0
    status = "Pass" if valid_dates_pct >= 80 else "Warning"

    return {
        "check": "Service Date Range (Last 6 Months)",
        "status": status,
        "message": f"{valid_dates_pct:.1f}% claims within last 6 months"
    }

def run_diagnosis_code_summary(df: Any, dx_fields: List[str]) -> Dict[str, Any]:
    """Summarizes MSK/BAR diagnosis code presence."""
    total_dx: int = 0
    msk_count: int = 0
    bar_count: int = 0
    other_count: int = 0

    msk_keywords = ["M", "S", "K"]
    bar_keywords = ["B", "A", "R"]

    for field in dx_fields:
        if field in df.columns:
            values = df[field].dropna().astype(str)
            total_dx += len(values)
            msk_count += values.str.contains('|'.join(msk_keywords)).sum()  # type: ignore[no-untyped-call]
            bar_count += values.str.contains('|'.join(bar_keywords)).sum()  # type: ignore[no-untyped-call]
            other_count += len(values) - (msk_count + bar_count)

    if total_dx == 0:
        message = "No diagnosis codes found"
        status = "Warning"
    else:
        msk_pct = (msk_count / total_dx) * 100
        bar_pct = (bar_count / total_dx) * 100
        message = f"MSK: {msk_pct:.1f}% | BAR: {bar_pct:.1f}%"
        status = "Pass" if msk_pct + bar_pct > 0 else "Warning"

    return {
        "check": "Diagnosis Code Presence (MSK/BAR)",
        "status": status,
        "message": message
    }

def dynamic_run_validations(transformed_df: Any, final_mapping: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Dynamically runs overall file-level validations."""
    results: List[Dict[str, Any]] = []

    results.append(run_required_field_check(transformed_df, final_mapping))

    if "Patient_DOB" in transformed_df.columns:
        results.append(run_age_check(transformed_df, "Patient_DOB"))
    elif "Insured_DOB" in transformed_df.columns:
        results.append(run_age_check(transformed_df, "Insured_DOB"))

    if "Begin_Date" in transformed_df.columns:
        results.append(run_date_range_check(transformed_df, "Begin_Date"))

    dx_fields = [col for col in transformed_df.columns if col.lower().startswith("dx_code")]
    if dx_fields:
        results.append(run_diagnosis_code_summary(transformed_df, dx_fields))

    return results
