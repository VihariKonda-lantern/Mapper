# --- tab_data_quality.py ---
"""Data Quality tab handler."""
import streamlit as st
from typing import Any
import pandas as pd
from state_manager import SessionStateManager
from improvements_utils import (
    render_empty_state,
    render_loading_skeleton,
)
from ui_improvements import (
    render_tooltip,
    render_sortable_table,
    render_filterable_table,
)
from performance_utils import render_lazy_dataframe
from error_handling import get_user_friendly_error
from data_quality import (
    calculate_data_quality_score,
    detect_duplicates,
    get_column_statistics,
    sample_data,
    detect_outliers,
    create_completeness_matrix,
    generate_data_profile
)

st: Any = st


def render_data_quality_tab() -> None:
    """Render the Data Quality & Analysis tab content."""
    st.markdown("## 📊 Data Quality & Analysis")
    claims_df_tab5 = SessionStateManager.get_claims_df()
    layout_df_tab5 = SessionStateManager.get_layout_df()
    
    if claims_df_tab5 is None or claims_df_tab5.empty:
        render_empty_state(
            icon="📊",
            title="No Data Available",
            message="Upload a claims file to analyze data quality.",
            action_label="Go to Setup Tab",
            action_callback=lambda: SessionStateManager.set("active_tab", "Setup")
        )
    else:
        # Data Quality Score
        st.markdown("### Overall Data Quality Score")
        required_fields_tab5 = []
        if layout_df_tab5 is not None and "Usage" in layout_df_tab5.columns:
            required_fields_tab5 = layout_df_tab5[
                layout_df_tab5["Usage"].astype(str).str.lower() == "mandatory"
            ]["Internal Field"].tolist()
        
        try:
            with st.spinner("Calculating data quality score..."):
                quality_score = calculate_data_quality_score(claims_df_tab5, required_fields_tab5)
        except Exception as e:
            error_msg = get_user_friendly_error(e)
            st.error(f"Error calculating data quality score: {error_msg}")
            quality_score = {"overall_score": 0, "breakdown": {"completeness": 0, "uniqueness": 0, "consistency": 0}}
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Overall Score", f"{quality_score['overall_score']:.1f}/100")
        with col2:
            breakdown_dict_col2: Any = quality_score.get('breakdown', {})
            completeness_val: Any = breakdown_dict_col2.get('completeness', 0) if isinstance(breakdown_dict_col2, dict) else 0
            completeness: float = float(completeness_val) if isinstance(completeness_val, (int, float)) else 0.0
            st.metric("Completeness", f"{completeness:.1f}%")
        with col3:
            breakdown_dict_col3: Any = quality_score.get('breakdown', {})
            uniqueness_val: Any = breakdown_dict_col3.get('uniqueness', 0) if isinstance(breakdown_dict_col3, dict) else 0
            uniqueness: float = float(uniqueness_val) if isinstance(uniqueness_val, (int, float)) else 0.0
            st.metric("Uniqueness", f"{uniqueness:.1f}%")
        with col4:
            breakdown_dict_col4: Any = quality_score.get('breakdown', {})
            consistency_val: Any = breakdown_dict_col4.get('consistency', 0) if isinstance(breakdown_dict_col4, dict) else 0
            consistency: float = float(consistency_val) if isinstance(consistency_val, (int, float)) else 0.0
            st.metric("Consistency", f"{consistency:.1f}%")
        
        # Data Profiling
        with st.expander("📈 Data Profile", expanded=False):
            render_tooltip(
                "Comprehensive data profile including statistics, distributions, and patterns",
                "This analysis provides insights into your data structure, completeness, and quality metrics."
            )
            try:
                with st.spinner("Generating data profile..."):
                    render_loading_skeleton(rows=3, cols=2)
                    profile = generate_data_profile(claims_df_tab5)
                st.json(profile)
            except Exception as e:
                error_msg = get_user_friendly_error(e)
                st.error(f"Error generating data profile: {error_msg}")
        
        # Column Statistics
        st.markdown("### Column Statistics")
        render_tooltip(
            "Detailed statistics for individual columns",
            "Select a column to see comprehensive statistics including mean, median, mode, null counts, and data types."
        )
        selected_col = st.selectbox("Select column to analyze", claims_df_tab5.columns.tolist(), key="col_stats_select")
        if selected_col:
            try:
                with st.spinner("Calculating column statistics..."):
                    render_loading_skeleton(rows=2, cols=1)
                    col_stats = get_column_statistics(claims_df_tab5, selected_col)
                st.json(col_stats)
            except Exception as e:
                error_msg = get_user_friendly_error(e)
                st.error(f"Error calculating column statistics: {error_msg}")
        
        # Duplicate Detection
        with st.expander("🔍 Duplicate Detection", expanded=False):
            dup_method = st.selectbox("Detection Method", ["exact", "key_based"], key="dup_method")
            dup_columns = st.multiselect("Columns to check", claims_df_tab5.columns.tolist(), key="dup_columns")
            if st.button("Detect Duplicates", key="detect_dups"):
                if dup_columns:
                    render_tooltip(
                        "Detect duplicate records in your data",
                        "Choose columns to check for duplicates and select the detection method (exact match or fuzzy)."
                    )
                    try:
                        with st.spinner("Detecting duplicates..."):
                            render_loading_skeleton(rows=2, cols=1)
                            duplicates = detect_duplicates(claims_df_tab5, dup_columns, dup_method)
                        if not duplicates.empty:
                            render_filterable_table(duplicates, key="duplicates_table")
                            st.info(f"Found {len(duplicates)} duplicate records")
                        else:
                            st.success("No duplicates found!")
                    except Exception as e:
                        error_msg = get_user_friendly_error(e)
                        st.error(f"Error detecting duplicates: {error_msg}")
        
        # Outlier Detection
        numeric_cols = claims_df_tab5.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            with st.expander("📊 Outlier Detection", expanded=False):
                outlier_col = st.selectbox("Select numeric column", numeric_cols, key="outlier_col")
                outlier_method = st.selectbox("Method", ["zscore", "iqr"], key="outlier_method")
                outlier_threshold = st.slider("Threshold", 1.0, 5.0, 3.0, 0.1, key="outlier_threshold")
                render_tooltip(
                    "Detect statistical outliers in your data",
                    "Outliers are values that deviate significantly from the mean. Adjust the threshold to control sensitivity."
                )
                if st.button("Detect Outliers", key="detect_outliers"):
                    try:
                        with st.spinner("Detecting outliers..."):
                            render_loading_skeleton(rows=2, cols=1)
                            outliers = detect_outliers(claims_df_tab5, outlier_col, outlier_method, outlier_threshold)
                        if not outliers.empty:
                            render_filterable_table(outliers, key="outliers_table")
                            st.info(f"Found {len(outliers)} outliers")
                        else:
                            st.success("✅ No outliers detected!")
                    except Exception as e:
                        error_msg = get_user_friendly_error(e)
                        st.error(f"Error detecting outliers: {error_msg}")
        
        # Completeness Matrix
        with st.expander("📋 Data Completeness Matrix", expanded=False):
            render_tooltip(
                "Visual matrix showing data completeness across all fields",
                "This matrix shows which fields have missing data and helps identify patterns in data completeness."
            )
            try:
                with st.spinner("Calculating completeness matrix..."):
                    render_loading_skeleton(rows=3, cols=3)
                    completeness_matrix = create_completeness_matrix(claims_df_tab5)
                if completeness_matrix.empty:
                    render_empty_state(
                        icon="📋",
                        title="No Data Available",
                        message="Unable to generate completeness matrix."
                    )
                else:
                    render_sortable_table(completeness_matrix, key="completeness_table")
            except Exception as e:
                error_msg = get_user_friendly_error(e)
                st.error(f"Error calculating completeness matrix: {error_msg}")
        
        # Data Sampling
        with st.expander("🎲 Data Sampling", expanded=False):
            sample_method = st.selectbox("Sampling Method", ["random", "first", "last"], key="sample_method")
            sample_size = st.number_input("Sample Size", 100, min(10000, len(claims_df_tab5)), 1000, key="sample_size")
            if st.button("Generate Sample", key="generate_sample"):
                sample_df: pd.DataFrame = sample_data(claims_df_tab5, sample_method, sample_size)
                render_lazy_dataframe(sample_df, key="sample_dataframe", max_rows_before_pagination=1000)
                csv_data: bytes = sample_df.to_csv(index=False).encode('utf-8')
                st.download_button("Download Sample", 
                                 csv_data,
                                 "sample_data.csv",
                                 "text/csv",
                                 key="download_sample")

