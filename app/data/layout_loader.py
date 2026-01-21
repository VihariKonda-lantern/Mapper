# pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import pandas as pd  # type: ignore[import-not-found]
from typing import List, Any, cast, Optional
import streamlit as st  # type: ignore[import-not-found]
from typing import Any as _Any

st = cast(_Any, st)
pd = cast(_Any, pd)

# Default required columns (for backward compatibility)
DEFAULT_REQUIRED_COLUMNS = ["Data Field", "Usage", "Category"]

def load_internal_layout(file: Any, config: Optional[Any] = None) -> Any:
    """Load and normalize the internal layout file.

    Supports all file formats (CSV, TXT, TSV, XLSX, XLS, JSON, PARQUET).
    Validates required columns, trims and standardizes string fields, renames
    to canonical column names, and returns a cleaned DataFrame-like object.

    Args:
        file: Uploaded layout file (any supported format).
        config: DomainConfig instance. If None, uses default claims config
            for backward compatibility.

    Returns:
        Cleaned layout with columns: `Internal Field`, `Usage`, `Category`
        (or configured internal names).

    Raises:
        ValueError: If file format is unsupported, reading fails, or required
            columns are missing.
    """
    # Get domain config
    if config is None:
        from core.domain_config import get_domain_config
        config = get_domain_config()
    
    # Use generic file loader to support all formats
    try:
        from data.file_handler import load_source_file
        df, has_header = load_source_file(file)
        
        # Ensure all columns are strings for consistency
        df = df.astype(str)  # type: ignore[no-untyped-call]
    except Exception as e:
        raise ValueError(f"Unable to read layout file: {e}")

    # --- Clean and Standardize ---
    df.columns = [col.strip() for col in df.columns]

    # --- Get required columns from config ---
    required_columns = [
        config.layout_columns.get("field_name", "Data Field"),
        config.layout_columns.get("usage", "Usage"),
        config.layout_columns.get("category", "Category")
    ]

    # --- Check Required Columns ---
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Layout file missing required column(s): {', '.join(missing)}")

    # --- Normalize all values ---
    df = df.applymap(lambda x: str(x).strip() if pd.notnull(x) else "")  # type: ignore[no-untyped-call]

    # --- Rename for internal consistency using config ---
    rename_map = {
        config.layout_columns.get("field_name", "Data Field"): config.internal_field_name,
        config.layout_columns.get("usage", "Usage"): config.internal_usage_name,
        config.layout_columns.get("category", "Category"): config.internal_category_name,
    }
    df = df.rename(columns=rename_map)  # type: ignore[no-untyped-call]

    # --- Normalize 'Usage' values using config ---
    usage_col = config.internal_usage_name
    df[usage_col] = df[usage_col].astype(str).str.strip()  # type: ignore[no-untyped-call]
    
    # Normalize using domain config mappings
    for idx, row in df.iterrows():
        usage_value = str(row[usage_col]).strip()
        normalized = config.normalize_usage_value(usage_value)
        df.at[idx, usage_col] = normalized  # type: ignore[no-untyped-call]

    # --- Normalize Other Fields ---
    field_col = config.internal_field_name
    category_col = config.internal_category_name
    df[field_col] = df[field_col].astype(str).str.strip()  # type: ignore[no-untyped-call]
    df[category_col] = df[category_col].astype(str).str.strip().str.title()  # type: ignore[no-untyped-call]

    # --- Drop Rows with Blank 'Internal Field' ---
    df = df.loc[df[field_col] != ""]  # type: ignore[no-untyped-call]
    # df is a DataFrame already; the cast is unnecessary for runtime
    # but harmless; leaving as-is to satisfy type expectations
    df = cast(Any, df)

    # --- Final Sanity Check ---
    if df.empty:
        raise ValueError("Layout file appears empty after cleaning. Please check the file contents.")

    return df

def get_required_fields(layout_df: Any, config: Optional[Any] = None) -> Any:
    """Return a filtered view with only mandatory fields.

    Args:
        layout_df: Cleaned internal layout DataFrame-like object.
        config: DomainConfig instance. If None, uses default.

    Returns:
        DataFrame-like with rows where `Usage == "Mandatory"`.
    """
    if config is None:
        from core.domain_config import get_domain_config
        config = get_domain_config()
    
    usage_col = config.internal_usage_name
    return layout_df[layout_df[usage_col] == "Mandatory"].copy()


def get_optional_fields(layout_df: Any, config: Optional[Any] = None) -> Any:
    """Return a filtered view with only optional fields.

    Args:
        layout_df: Cleaned internal layout DataFrame-like object.
        config: DomainConfig instance. If None, uses default.

    Returns:
        DataFrame-like with rows where `Usage == "Optional"`.
    """
    if config is None:
        from core.domain_config import get_domain_config
        config = get_domain_config()
    
    usage_col = config.internal_usage_name
    return layout_df[layout_df[usage_col] == "Optional"].copy()


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

        st.markdown(f"**Total Fields:** {total_fields}", unsafe_allow_html=True)
        st.markdown(f"**Required Fields:** {required_fields}", unsafe_allow_html=True)
        st.markdown(f"**Optional Fields:** {optional_fields}", unsafe_allow_html=True)

        with st.expander("Field Categories", expanded=False):
            for cat, count in category_counts.items():
                st.write(f"- {cat}: {count}")  # type: ignore[no-untyped-call]

        with st.expander("View Layout Table", expanded=False):
            st.dataframe(layout_df[["Internal Field", "Usage", "Category"]], use_container_width=True)  # type: ignore[no-untyped-call]
    elif st.session_state.get("layout_upload_attempted", False):
        # Only show info if user has attempted to upload a file
        st.info("Layout file not uploaded yet.")

