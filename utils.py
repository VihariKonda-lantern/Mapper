# pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import streamlit as st  # type: ignore[import-not-found]
import pandas as pd  # type: ignore[import-not-found]
from typing import Any, cast, List, Dict

st = cast(Any, st)
pd = cast(Any, pd)

def detect_encoding_issues(claims_df: Any) -> None:
    """Check object columns for potential UTF-8 encoding issues.

    Attempts to encode non-null values in object-typed columns; if any
    exception occurs, the column is flagged and a warning is shown.

    Args:
        claims_df: Claims DataFrame-like object.

    Side Effects:
        Emits a Streamlit warning when suspect columns are found.
    """
    issue_columns: List[str] = []
    for col in claims_df.select_dtypes(include="object").columns:
        try:
            _ = claims_df[col].dropna().apply(lambda x: str(x).encode('utf-8')).tolist()  # type: ignore[no-untyped-call]
        except Exception:
            issue_columns.append(col)
    if issue_columns:
        st.warning(f"⚠️ Possible encoding issues detected in: {', '.join(issue_columns)}")

# --- Helper Function ---
def infer_date_format(sample: str) -> str:
    """Infer a likely date format string from a sample value.

    Args:
        sample: Example date string.

    Returns:
        A format descriptor like "YYYY-MM-DD", "MM/DD/YYYY", or "Unknown".
    """
    sample = sample.strip()

    if "-" in sample:
        if len(sample.split("-")[0]) == 4:
            return "YYYY-MM-DD"
        else:
            return "MM-DD-YYYY"
    elif "/" in sample:
        parts = sample.split("/")
        if len(parts[2]) == 4:
            return "MM/DD/YYYY"
        else:
            return "MM/DD/YY"
    elif len(sample) == 8:
        if sample[:4].isdigit() and sample[4:].isdigit():
            return "YYYYMMDD"
        elif sample[:2].isdigit() and sample[2:].isdigit():
            return "MMDDYYYY"
    elif len(sample) == 6:
        return "YYMMDD"
    return "Unknown"

# --- Main Summary Function ---
def render_claims_file_summary() -> None:
    """Render a detailed summary for the uploaded claims file.

    Shows file metadata, row/column counts, date fields and ranges, data types
    overview, and potential encoding issues.
    """
    claims_df = st.session_state.get("claims_df")
    metadata = st.session_state.get("claims_file_metadata", {})
    claims_file = st.session_state.get("claims_file_obj")

    if claims_df is not None:
        st.subheader("🔎 Claims File Summary")

        if claims_file:
            st.write(f"**File Name:** {claims_file.name}")  # type: ignore[no-untyped-call]
        
        if metadata:
            st.write(f"**Format Detected:** {metadata.get('format', 'Unknown')}")  # type: ignore[no-untyped-call]
            if metadata.get("sep"):
                st.write(f"**Delimiter:** `{metadata.get('sep')}`")  # type: ignore[no-untyped-call]
            st.write(f"**Header Present:** {'Yes' if metadata.get('header') else 'No'}")  # type: ignore[no-untyped-call]

        st.write(f"**Total Rows:** {len(claims_df)}")  # type: ignore[no-untyped-call]
        st.write(f"**Total Columns:** {len(claims_df.columns)}")  # type: ignore[no-untyped-call]

        st.divider()

        # --- Date Fields Summary ---
        date_cols = [col for col in claims_df.columns if "date" in col.lower()]
        if date_cols:
            st.markdown("**Date Fields Detected**")

            date_format_rows: List[Dict[str, Any]] = []

            for col in date_cols:
                sample_value = claims_df[col].dropna().astype(str).iloc[0] if not claims_df[col].dropna().empty else ""  # type: ignore[no-untyped-call]
                detected_format = infer_date_format(sample_value) if sample_value else "Unknown"

                date_format_rows.append({
                    "Column Name": col,
                    "Example Value": sample_value,
                    "Detected Format": detected_format
                })

            date_formats_df = pd.DataFrame(date_format_rows)
            st.dataframe(date_formats_df, use_container_width=True)  # type: ignore[no-untyped-call]

        st.divider()

        # --- Begin_Date Range ---
        if "Begin_Date" in claims_df.columns:
            try:
                begin_dates = pd.to_datetime(claims_df["Begin_Date"], errors="coerce")  # type: ignore[no-untyped-call]
                st.write(f"**Begin_Date Range:** {begin_dates.min().date()} ➔ {begin_dates.max().date()}")  # type: ignore[no-untyped-call]
            except Exception:
                st.warning("⚠️ Could not parse Begin_Date column properly.")

        st.divider()

        # --- Unusual Data Types ---
        st.markdown("**Data Types Overview**")
        type_summary = claims_df.dtypes.value_counts().to_frame(name="Count")
        st.dataframe(type_summary, use_container_width=True)  # type: ignore[no-untyped-call]

        object_cols = claims_df.select_dtypes(include="object").columns.tolist()
        if object_cols:
            st.info(f"🔎 {len(object_cols)} columns are text (object type): {', '.join(object_cols[:10])}")

        st.divider()

        # --- Encoding Issues (Optional) ---
        try:
            detect_encoding_issues(claims_df)
        except Exception as e:
            st.warning(f"Encoding check skipped: {e}")

    else:
        st.info("Upload claims file to view summary.")



