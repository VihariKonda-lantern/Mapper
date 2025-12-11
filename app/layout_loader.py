# pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import pandas as pd  # type: ignore[import-not-found]
from typing import List, Any, cast
import streamlit as st  # type: ignore[import-not-found]
from typing import Any as _Any

st = cast(_Any, st)
pd = cast(_Any, pd)

REQUIRED_COLUMNS = ["Data Field", "Usage", "Category"]

def load_internal_layout(file: Any) -> Any:
    """Load and normalize the internal layout Excel file.

    Validates required columns, trims and standardizes string fields, renames
    to canonical column names, and returns a cleaned DataFrame-like object.

    Args:
        file: Uploaded Excel layout file.

    Returns:
        Cleaned layout with columns: `Internal Field`, `Usage`, `Category`.

    Raises:
        ValueError: If file format is unsupported, reading fails, or required
            columns are missing.
    """
    try:
        if not file.name.endswith(".xlsx"):
            raise ValueError("Unsupported file format. Please upload a .xlsx Excel file.")

        df = pd.read_excel(file, dtype=str)  # type: ignore[no-untyped-call]
    except Exception as e:
        raise ValueError(f"Unable to read internal layout file: {e}")

    # --- Clean and Standardize ---
    df.columns = [col.strip() for col in df.columns]

    # --- Check Required Columns ---
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Layout file missing required column(s): {', '.join(missing)}")

    # --- Normalize all values ---
    df = df.applymap(lambda x: str(x).strip() if pd.notnull(x) else "")  # type: ignore[no-untyped-call]

    # --- Rename for internal consistency ---
    df = df.rename(columns={  # type: ignore[no-untyped-call]
        "Data Field": "Internal Field",
        "Usage": "Usage",
        "Category": "Category"
    })

    # --- Normalize 'Usage' values ---
    df["Usage"] = df["Usage"].astype(str).str.strip().str.title()  # type: ignore[no-untyped-call]
    df["Usage"] = df["Usage"].replace({  # type: ignore[no-untyped-call]
        "Yes": "Mandatory",
        "No": "Optional"
    })

    # --- Normalize Other Fields ---
    df["Internal Field"] = df["Internal Field"].astype(str).str.strip()  # type: ignore[no-untyped-call]
    df["Category"] = df["Category"].astype(str).str.strip().str.title()  # type: ignore[no-untyped-call]

    # --- Drop Rows with Blank 'Internal Field' ---
    df = df.loc[df["Internal Field"] != ""]  # type: ignore[no-untyped-call]
    # df is a DataFrame already; the cast is unnecessary for runtime
    # but harmless; leaving as-is to satisfy type expectations
    df = cast(Any, df)

    # --- Final Sanity Check ---
    if df.empty:
        raise ValueError("Layout file appears empty after cleaning. Please check the file contents.")

    return df

def get_required_fields(layout_df: Any) -> Any:
    """Return a filtered view with only mandatory fields.

    Args:
        layout_df: Cleaned internal layout DataFrame-like object.

    Returns:
        DataFrame-like with rows where `Usage == "Mandatory"`.
    """
    return layout_df[layout_df["Usage"] == "Mandatory"].copy()


def get_optional_fields(layout_df: Any) -> Any:
    """Return a filtered view with only optional fields.

    Args:
        layout_df: Cleaned internal layout DataFrame-like object.

    Returns:
        DataFrame-like with rows where `Usage == "Optional"`.
    """
    return layout_df[layout_df["Usage"] == "Optional"].copy()


def get_field_groups(layout_df: Any) -> List[str]:
    """Extract distinct field categories from the layout.

    Args:
        layout_df: Cleaned internal layout DataFrame-like object.

    Returns:
        Sorted list of non-empty category names.
    """
    # Get unique categories, drop NaN, convert to string, filter empty strings, and sort
    cats = layout_df["Category"].dropna().astype(str).unique().tolist()  # type: ignore[no-untyped-call]
    return sorted([c for c in cats if c])


def render_layout_summary_section() -> None:
    """Render a summary of the internal layout currently loaded in session.

    Displays counts for total/required/optional fields, category breakdown,
    and a compact data table preview.
    """
    layout_df = st.session_state.get("layout_df")

    if layout_df is not None:
        st.markdown("#### Internal Layout Summary")

        total_fields = len(layout_df)
        required_fields = layout_df[layout_df["Usage"].str.lower() == "mandatory"].shape[0]
        optional_fields = layout_df[layout_df["Usage"].str.lower() == "optional"].shape[0]
        category_counts = layout_df["Category"].value_counts().to_dict()

        st.write(f"**Total Fields:** {total_fields}")  # type: ignore[no-untyped-call]
        st.write(f"**Required Fields:** {required_fields}")  # type: ignore[no-untyped-call]
        st.write(f"**Optional Fields:** {optional_fields}")  # type: ignore[no-untyped-call]

        with st.expander("Field Categories"):
            for cat, count in category_counts.items():
                st.write(f"- {cat}: {count}")  # type: ignore[no-untyped-call]

        with st.expander("View Layout Table"):
            st.dataframe(layout_df[["Internal Field", "Usage", "Category"]], use_container_width=True)  # type: ignore[no-untyped-call]
    elif st.session_state.get("layout_upload_attempted", False):
        # Only show info if user has attempted to upload a file
        st.info("Layout file not uploaded yet.")

