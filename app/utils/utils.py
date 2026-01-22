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
    Optimized to use vectorized operations where possible.

    Args:
        claims_df: Claims DataFrame-like object.

    Side Effects:
        Emits a Streamlit warning when suspect columns are found.
    """
    issue_columns: List[str] = []
    object_cols = claims_df.select_dtypes(include="object").columns
    for col in object_cols:
        try:
            # Use vectorized string operations instead of apply
            non_null_series = claims_df[col].dropna().astype(str)
            if len(non_null_series) > 0:
                # Sample first 1000 values for performance
                sample = non_null_series.head(1000)
                _ = sample.str.encode('utf-8', errors='strict').tolist()  # type: ignore[no-untyped-call]
        except (UnicodeEncodeError, UnicodeError):
            issue_columns.append(col)
        except Exception:
            # Other exceptions might indicate encoding issues too
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

    Shows file metadata, row/column counts, date fields, and data types
    in a compact card format matching other summaries.
    """
    claims_df = st.session_state.get("claims_df")
    metadata = st.session_state.get("claims_file_metadata", {})
    claims_file = st.session_state.get("claims_file_obj")

    # Show summary if file is uploaded (even if not processed yet)
    if claims_file is not None:
        st.markdown("#### Claims File Summary")
        
        # Show basic file info if not processed yet
        if claims_df is None:
            # Basic file information
            file_name = claims_file.name
            file_size = claims_file.size / (1024 * 1024)  # Size in MB
            file_ext = file_name.split('.')[-1].upper() if '.' in file_name else "Unknown"
            
            st.markdown(f"<p style='margin-bottom: 0.25rem;'>File: **{file_name}** ({file_size:.2f} MB, {file_ext} format)</p>", unsafe_allow_html=True)
            
            with st.expander("📄 File Information", expanded=False):
                st.write(f"**File Name:** {file_name}")  # type: ignore[no-untyped-call]
                st.write(f"**File Size:** {file_size:.2f} MB")  # type: ignore[no-untyped-call]
                st.write(f"**File Format:** {file_ext}")  # type: ignore[no-untyped-call]
                st.info("⏳ File will be processed automatically when all required files (Layout, Lookup, Claims) are uploaded.")
            return

    if claims_df is not None:
        # Header already shown above, don't repeat it

        # File info in intelligent single line (compact, outside collapsible)
        date_cols = [col for col in claims_df.columns if "date" in col.lower()]
        type_counts = claims_df.dtypes.value_counts()
        type_summary_text = ", ".join([f"{str(dtype)}: {count}" for dtype, count in type_counts.items()])
        
        # Build intelligent file description in consistent format (compact spacing)
        if metadata:
            format_type = metadata.get('format', 'unknown format')
            
            # Format delimiter for display
            delim_display = ""
            if metadata.get("sep"):
                delim = metadata.get('sep')
                if delim == ',':
                    delim_display = ','
                elif delim == '\t':
                    delim_display = 'tab'
                elif delim == '|':
                    delim_display = '|'
                elif delim == ';':
                    delim_display = ';'
                else:
                    delim_display = delim
            
            # Build description: "File is csv with , delimiter; file has headers"
            header_text = "file has headers" if metadata.get('header') else "file has no headers"
            
            if delim_display:
                file_description = f"File is {format_type} with {delim_display} delimiter; {header_text}"
            else:
                file_description = f"File is {format_type}; {header_text}"
            
            st.markdown(f"<p style='margin-bottom: 0.25rem;'>{file_description}</p>", unsafe_allow_html=True)
        
        # Summary metrics in collapsible section (matching structure of other cards)
        with st.expander("📄 File Information", expanded=False):
            st.write(f"**Total Rows:** {len(claims_df):,}")  # type: ignore[no-untyped-call]
            st.write(f"**Total Columns:** {len(claims_df.columns)}")  # type: ignore[no-untyped-call]

            if date_cols:
                st.write(f"**Date Fields:** {len(date_cols)}")  # type: ignore[no-untyped-call]
            st.write(f"**Data Types:** {type_summary_text}")  # type: ignore[no-untyped-call]

        # Two expandable sections (matching other cards)
        with st.expander("Date Fields Details", expanded=False):
            if date_cols:
                date_format_rows: List[Dict[str, Any]] = []
                for col in date_cols:
                    sample_value = claims_df[col].dropna().astype(str).iloc[0] if not claims_df[col].dropna().empty else ""  # type: ignore[no-untyped-call]
                    detected_format = infer_date_format(sample_value) if sample_value else "Unknown"
                    date_format_rows.append({
                        "Column Name": col,
                        "Example Value": sample_value,
                        "Detected Format": detected_format
                    })
                if date_format_rows:
                    date_formats_df = pd.DataFrame(date_format_rows)
                    st.dataframe(date_formats_df, use_container_width=True)  # type: ignore[no-untyped-call]
                else:
                    st.write("No date fields detected.")  # type: ignore[no-untyped-call]
            else:
                st.write("No date fields detected.")  # type: ignore[no-untyped-call]

        with st.expander("Text Columns & Data Types", expanded=False):
            object_cols = claims_df.select_dtypes(include="object").columns.tolist()
            if object_cols:
                st.write(f"**Text Columns ({len(object_cols)}):**")  # type: ignore[no-untyped-call]
                st.write(", ".join(object_cols[:20]))  # type: ignore[no-untyped-call]
                if len(object_cols) > 20:
                    st.write(f"... and {len(object_cols) - 20} more")  # type: ignore[no-untyped-call]
            else:
                st.write("No text columns found.")  # type: ignore[no-untyped-call]
            
            type_summary = claims_df.dtypes.value_counts().to_frame(name="Count")
            st.dataframe(type_summary, use_container_width=True)  # type: ignore[no-untyped-call]

    elif st.session_state.get("claims_upload_attempted", False):
        # Only show info if user has attempted to upload a file
        st.info("Upload claims file to view summary.")



