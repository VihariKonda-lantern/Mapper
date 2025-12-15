# pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import streamlit as st  # type: ignore[import-not-found]
import pandas as pd  # type: ignore[import-not-found]
from typing import Any, Optional, cast
from file.file_handler import detect_delimiter, read_claims_with_header_option

# Help the type checker understand dynamic Streamlit/Pandas attributes
st = cast(Any, st)
pd = cast(Any, pd)

# Removed duplicate function - use detect_delimiter from file_handler instead

def capture_claims_file_metadata(file: Any, has_header: bool) -> None:
    """Record basic metadata for an uploaded claims file in session state.

    Determines format by extension and estimates separator when relevant.

    Args:
        file: Streamlit-uploaded file-like object.
        has_header: Whether the file appears to contain a header row.

    Side Effects:
        Sets `st.session_state.claims_file_metadata` with format, sep, header,
        and a default date format.
    """
    filename = file.name.lower()

    if filename.endswith(".csv") or filename.endswith(".txt") or filename.endswith(".tsv"):
        format_detected = "csv"
        sep = detect_delimiter(file)
    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        format_detected = "excel"
        sep = None  # Excel doesn't need sep
    elif filename.endswith(".json"):
        format_detected = "json"
        sep = None
    elif filename.endswith(".parquet"):
        format_detected = "parquet"
        sep = None
    else:
        format_detected = "csv"
        sep = ','

    st.session_state.claims_file_metadata = {
        "format": format_detected,
        "sep": sep,
        "header": has_header,
        "dateFormat": "yyyyMd"  # can enhance later
    }

def render_file_upload_section() -> None:
    """Render the upload UI and manage file-related session state.

    Provides inputs for layout, diagnosis lookup, claims file, and optional
    external header file, updating `st.session_state` accordingly.
    """
    st.markdown("#### Step 1: Upload Required Files")
    layout_col, claims_col, lookup_col = st.columns(3)

    # Layout file upload
    with layout_col:
        st.markdown("**Upload Internal Layout File (.xlsx)**", unsafe_allow_html=True)
        layout_file: Optional[Any] = st.file_uploader("Choose Layout File", type=["xlsx"], key="layout_file")
        if layout_file:
            st.session_state.layout_file_obj = layout_file

    # Claims file upload
    with claims_col:
        st.markdown("**Upload Claims File (CSV, TXT, TSV, XLSX, XLS, JSON, PARQUET)**", unsafe_allow_html=True)
        claims_file: Optional[Any] = st.file_uploader("Choose Claims File", key="claims_file")

    # Lookup file upload
    with lookup_col:
        st.markdown("**Upload Diagnosis Lookup File (.xlsx)**", unsafe_allow_html=True)
        lookup_file: Optional[Any] = st.file_uploader("Choose Lookup File", type=["xlsx"], key="lookup_file")
        if lookup_file:
            st.session_state.lookup_file_obj = lookup_file

    st.session_state.setdefault("claims_df", None)

    # --- Now handle claims file loading ---
    if "claims_df" not in st.session_state:
        if claims_file:
            ext = claims_file.name.lower()

            # Check if user already decided on header question
            header_confirm: Optional[str] = st.session_state.get("header_confirm_radio")

            if header_confirm is None:
                # Step 1: show preview + ask header question
                try:
                    if ext.endswith((".csv", ".txt", ".tsv")):
                        delimiter = detect_delimiter(claims_file)
                        claims_file.seek(0)
                        preview_df = pd.read_csv(claims_file, nrows=5, header=None, delimiter=delimiter, on_bad_lines='skip')  # type: ignore[no-untyped-call]
                    elif ext.endswith((".xlsx", ".xls")):
                        preview_df = pd.read_excel(claims_file, nrows=5, header=None)  # type: ignore[no-untyped-call]
                    else:
                        st.error("Unsupported file type.")
                        st.stop()
                    st.dataframe(preview_df, use_container_width=True)  # type: ignore[no-untyped-call]
                except Exception as e:
                    st.error(f"Error previewing claims file: {e}")
                    st.stop()

                st.radio("Does this file have headers?", ["Yes", "No"], index=0, horizontal=True, key="header_confirm_radio")
                st.stop()  # 🔥 STOP here after asking the question
            
            # Now based on header_confirm
            header_file: Optional[Any] = None
            if header_confirm == "No":
                header_file = st.file_uploader("Upload External Header File (CSV, TXT, XLSX)", type=["csv", "txt", "xlsx"], key="external_header_upload")
                if header_file is None:
                    st.warning("⚠️ Please upload an external header file to continue.")
                    st.stop()

            # Now we have everything needed, proceed to read claims file
            try:
                claims_file.seek(0)
                delimiter: Optional[str] = detect_delimiter(claims_file) if ext.endswith((".csv", ".txt", ".tsv")) else None
                claims_file.seek(0)

                claims_df: Any = read_claims_with_header_option(
                    claims_file,
                    headerless=(header_confirm == "No"),
                    header_file=header_file,
                    delimiter=delimiter
                )

                st.session_state.claims_df = claims_df

                if header_confirm == "Yes":
                    st.success("✅ Claims file loaded with headers.")
                else:
                    st.success("✅ Claims file loaded using external header.")

            except Exception as e:
                st.error(f"Error loading claims file: {e}")

        else:
            st.info("Please upload a claims file first.")
    else:
        st.success("✅ Claims file already loaded and ready.")


