# --- tab_validation.py ---
"""Preview & Validate tab handler."""
import streamlit as st
from typing import Any, List, Dict
import hashlib
import time
import statistics
import pandas as pd
from core.state_manager import SessionStateManager
from core.config_loader import DEFAULT_VALIDATION_PAGE_SIZE, VALIDATION_PAGE_SIZES
from utils.improvements_utils import (
    render_empty_state,
    render_loading_skeleton,
)
from ui.ui_components import (
    render_sortable_table,
    render_tooltip,
    show_toast,
    render_filterable_table
)
from core.error_handling import get_user_friendly_error
from validation.validation_engine import run_validations, dynamic_run_validations
from data.layout_loader import get_required_fields
from validation.advanced_validation import track_validation_performance
try:
    from utils.performance_utils import paginate_dataframe, render_lazy_dataframe
except (ImportError, KeyError, ModuleNotFoundError):
    # Fallback if performance_utils is not available
    def paginate_dataframe(df: Any, page_size: int = 100) -> tuple:
        """Fallback pagination function."""
        return df, 1, 1
    
    def render_lazy_dataframe(df: Any, key: str = "lazy_df", page_size: int = 1000, max_rows_before_pagination: int = 1000) -> None:
        """Fallback lazy dataframe renderer."""
        if df is None or (hasattr(df, 'empty') and df.empty):
            st.info("No data to display")
            return
        st.dataframe(df, use_container_width=True)
from ui.ui_components import _notify
from utils.audit_logger import log_event

st: Any = st


def render_validation_tab() -> None:
    """Render the Preview & Validate tab content with clean, organized layout."""
    # Inject tight spacing CSS (uses shared design system)
    from ui.design_system import inject_tight_spacing_css
    inject_tight_spacing_css()
    
    # Check for files first
    layout_df = SessionStateManager.get_layout_df()
    claims_df = SessionStateManager.get_claims_df()
    
    if layout_df is None or claims_df is None:
        render_empty_state(
            icon="📁",
            title="Files Required",
            message="Please start from the Setup tab to upload both layout and claims files before validation.",
            action_label="Go to Setup Tab",
            action_callback=lambda: SessionStateManager.set("active_tab", "Setup")
        )
        st.stop()
    
    # Check for mappings
    final_mapping = SessionStateManager.get_final_mapping()
    
    if not final_mapping:
        render_empty_state(
            icon="📋",
            title="Mapping Required",
            message="Please complete field mappings first.",
            action_label="Go to Field Mapping Tab",
            action_callback=lambda: SessionStateManager.set("active_tab", "Field Mapping")
        )
        st.stop()
    
    # Generate transformed_df if it doesn't exist but mappings do
    transformed_df = SessionStateManager.get_transformed_df()
    if transformed_df is None:
        # Auto-generate transformed_df from mappings
        from data.transformer import transform_claims_data
        transformed_df = transform_claims_data(claims_df, final_mapping)
        if transformed_df is not None:
            SessionStateManager.set_transformed_df(transformed_df)
        else:
            render_empty_state(
                icon="⚠️",
                title="Transformation Error",
                message="Could not transform data. Please check your mappings.",
                action_label="Go to Field Mapping Tab",
                action_callback=lambda: SessionStateManager.set("active_tab", "Field Mapping")
            )
            st.stop()
    
    # --- Auto-run validation (cached to avoid re-running on every rerun) ---
    data_hash = hashlib.md5(
        (str(final_mapping) + str(transformed_df.shape) + str(transformed_df.columns.tolist())).encode()
    ).hexdigest()
    cached_hash = st.session_state.get("validation_data_hash")
    validation_results_cached: List[Dict[str, Any]] = st.session_state.get("validation_results", [])
    
    if cached_hash != data_hash or not validation_results_cached:
        render_loading_skeleton(rows=3, cols=4)
        with st.spinner("Running validation checks..."):
            if layout_df is not None:
                required_fields_df = get_required_fields(layout_df)
                required_fields: List[str] = required_fields_df["Internal Field"].tolist() if isinstance(required_fields_df, pd.DataFrame) else []
            else:
                required_fields = list(final_mapping.keys())
            all_mapped_internal_fields = [field for field in final_mapping.keys() if final_mapping[field].get("value")]
            start_time = time.time()
            try:
                with st.spinner("Running field-level validations..."):
                    field_level_results = run_validations(transformed_df, required_fields, all_mapped_internal_fields)
            except Exception as e:
                error_msg = get_user_friendly_error(e)
                st.error(f"Error during field-level validation: {error_msg}")
                field_level_results = []
            try:
                with st.spinner("Running file-level validations..."):
                    file_level_results = dynamic_run_validations(transformed_df, final_mapping)
            except Exception as e:
                error_msg = get_user_friendly_error(e)
                st.error(f"Error during file-level validation: {error_msg}")
                file_level_results = []
            validation_results_new: List[Dict[str, Any]] = field_level_results + file_level_results
            execution_time = time.time() - start_time
            track_validation_performance("full_validation", execution_time, len(transformed_df), len(validation_results_new))
            st.session_state.validation_results = validation_results_new
            st.session_state.validation_data_hash = data_hash
            fail_count = len([r for r in validation_results_new if r.get("status") == "Fail"])
            warning_count = len([r for r in validation_results_new if r.get("status") == "Warning"])
            pass_count = len([r for r in validation_results_new if r.get("status") == "Pass"])
            
            try:
                log_event("validation", f"Validation completed: {pass_count} passed, {warning_count} warnings, {fail_count} failed")
            except NameError:
                pass

    # Get validation results
    validation_results_summary: List[Dict[str, Any]] = st.session_state.get("validation_results", [])

    if not validation_results_summary:
        st.info("No validation results available. Run validation to see results.")
        st.stop()
    
    # Get mandatory fields
    mandatory_fields: List[str] = []
    if layout_df is not None:
        required_fields_df = get_required_fields(layout_df)
        mandatory_fields = required_fields_df["Internal Field"].tolist() if isinstance(required_fields_df, pd.DataFrame) else []
    
    # Calculate file status
    fails: List[Dict[str, Any]] = [r for r in validation_results_summary if r.get("status") == "Fail"]
    warnings: List[Dict[str, Any]] = [r for r in validation_results_summary if r.get("status") == "Warning"]
    passes: List[Dict[str, Any]] = [r for r in validation_results_summary if r.get("status") == "Pass"]
    
    # Check for unmapped required fields
    unmapped_required_fields: List[str] = []
    if layout_df is not None:
        usage_normalized = layout_df["Usage"].astype(str).str.strip().str.lower()
        required_fields_list = layout_df[usage_normalized == "mandatory"]["Internal Field"].tolist()
        for field in required_fields_list:
            mapping = final_mapping.get(field)
            if not mapping or not mapping.get("value") or str(mapping.get("value")).strip() == "":
                if field not in unmapped_required_fields:
                    unmapped_required_fields.append(field)
    
    # Determine file status
    is_rejected = len(unmapped_required_fields) > 0
    has_critical_issues = len(fails) > 0
    has_warnings = len(warnings) > 0
    
    # ============================================
    # MAIN VALIDATION DASHBOARD
    # ============================================
    if validation_results_summary:
        st.dataframe(pd.DataFrame(validation_results_summary))
    
    # ============================================
    # FILE STATUS SECTION
    # ============================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='margin-bottom: 0.5rem;'>
            <h2 style='color: #111827; font-size: 1.25rem; font-weight: 600; margin-bottom: 0.125rem; letter-spacing: -0.025em;'>File Status</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Status card
    if is_rejected:
        status_color = "#dc3545"
        status_icon = "❌"
        status_text = "Rejected"
        status_message = "Mandatory fields are missing from the file."
    elif has_critical_issues:
        status_color = "#ffc107"
        status_icon = "⚠️"
        status_text = "Needs Review"
        status_message = "Some validation checks failed. Please review the issues below."
    elif has_warnings:
        status_color = "#17a2b8"
        status_icon = "ℹ️"
        status_text = "Approved with Warnings"
        status_message = "File meets requirements but has some data quality issues to review."
    else:
        status_color = "#28a745"
        status_icon = "✅"
        status_text = "Approved"
        status_message = "All validation checks passed. File is ready for processing."
    
    st.markdown(f"""
        <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 6px; border-left: 4px solid {status_color}; margin-bottom: 0.5rem;'>
            <div style='display: flex; align-items: center; gap: 0.5rem;'>
                <span style='font-size: 1.5rem;'>{status_icon}</span>
                <div>
                    <strong style='color: #111827; font-size: 1rem;'>{status_text}</strong>
                    <p style='color: #6b7280; margin: 0.25rem 0 0 0; font-size: 0.875rem;'>{status_message}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # ============================================
    # DETAILED ANALYSIS SECTION (TABS)
    # ============================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='margin-bottom: 0.75rem;'>
            <h2 style='color: #111827; font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; letter-spacing: -0.025em;'>Detailed Analysis</h2>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Mandatory Fields", "Data Quality", "Advanced Analysis"])
    
    # Tab 1: Mandatory Fields
    with tab1:
        if unmapped_required_fields:
            st.error(f"**Missing Fields:** {', '.join(f'`{f}`' for f in unmapped_required_fields)}")
            st.caption("These mandatory fields must be present in the source file and properly mapped.")
        
        # Required field null statistics
        required_field_null_stats: List[Dict[str, Any]] = []
        for result in validation_results_summary:
            if result.get("check") == "Required Field Check":
                field = result.get("field", "")
                status = result.get("status", "")
                fail_pct_str = result.get("fail_pct", "0")
                fail_pct = float(fail_pct_str) if fail_pct_str else 0.0
                fail_count_str = result.get("fail_count", "0")
                fail_count = int(float(fail_count_str)) if fail_count_str else 0
                required_field_null_stats.append({
                    "field": field,
                    "null_percentage": fail_pct,
                    "null_count": fail_count,
                    "status": status
                })
        
        if required_field_null_stats:
            # Calculate threshold
            null_percentages: List[float] = [float(s["null_percentage"]) for s in required_field_null_stats]
            avg_null_pct: float = sum(null_percentages) / len(null_percentages) if null_percentages else 0.0
            if len(null_percentages) > 1:
                try:
                    std_dev: float = statistics.stdev(null_percentages)
                    suggested_threshold: float = min(max(avg_null_pct + (2 * std_dev), 1.0), 15.0)
                except (statistics.StatisticsError, ValueError):
                    suggested_threshold = min(max(avg_null_pct + 3.0, 2.0), 10.0)
            else:
                suggested_threshold = min(max(avg_null_pct + 3.0, 2.0), 10.0)
            
            fields_with_no_nulls = [s for s in required_field_null_stats if s["null_percentage"] == 0.0]
            fields_with_low_nulls = [s for s in required_field_null_stats if 0 < s["null_percentage"] <= suggested_threshold]
            fields_exceeding_threshold = [s for s in required_field_null_stats if s["null_percentage"] > suggested_threshold]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Mandatory Fields", len(required_field_null_stats))
            with col2:
                st.metric("Perfect Fields (0% null)", len(fields_with_no_nulls))
            with col3:
                st.metric("Fields Within Threshold", len(fields_with_low_nulls))
            with col4:
                st.metric("Fields Exceeding Threshold", len(fields_exceeding_threshold))
            
            if fields_exceeding_threshold:
                st.markdown("""
                    <div style='margin-bottom: 0.5rem;'>
                        <h4 style='color: #111827; font-size: 1rem; font-weight: 600; margin: 0;'>Fields Requiring Attention</h4>
                    </div>
                """, unsafe_allow_html=True)
                total_records = len(transformed_df) if transformed_df is not None else 0
                for field_stat in sorted(fields_exceeding_threshold, key=lambda x: x["null_percentage"], reverse=True):
                    field_name = field_stat["field"]
                    null_pct = field_stat["null_percentage"]
                    null_count = field_stat["null_count"]
                    fill_rate = 100 - null_pct
                    st.markdown(f"- **{field_name}**: {null_pct:.2f}% null ({null_count:,} of {total_records:,} records) - Fill rate: {fill_rate:.2f}%")
        
        # Other mandatory field validations
        other_failures = [
            r for r in fails 
            if r.get("check") != "Required Field Check" 
            and r.get("check") != "Optional Field Check"
            and r.get("check") != "Fill Rate Check"
        ]
        other_warnings = [
            r for r in warnings 
            if r.get("check") != "Required Field Check"
            and r.get("check") != "Optional Field Check"
            and r.get("check") != "Fill Rate Check"
        ]
        
        if other_failures or other_warnings:
            if other_failures:
                st.markdown("**Critical Issues:**")
                for issue in other_failures:
                    check_name = issue.get("check", "Unknown Check")
                    field = issue.get("field", "")
                    message = issue.get("message", "")
                    if field:
                        st.error(f"- **{check_name}** ({field}): {message}")
                    else:
                        st.error(f"- **{check_name}**: {message}")
            if other_warnings:
                st.markdown("**Warnings:**")
                for issue in other_warnings:
                    check_name = issue.get("check", "Unknown Check")
                    field = issue.get("field", "")
                    message = issue.get("message", "")
                    if field:
                        st.warning(f"- **{check_name}** ({field}): {message}")
                    else:
                        st.warning(f"- **{check_name}**: {message}")
    
    # --- Tab 2: Data Quality ---
    with tab2:
        # Use claims_df from top-level check (already validated)
        if claims_df is not None and not claims_df.empty:
            # Data Quality Score
            required_fields_quality = []
            if layout_df is not None and "Usage" in layout_df.columns:
                required_fields_quality = layout_df[
                    layout_df["Usage"].astype(str).str.lower() == "mandatory"
                ]["Internal Field"].tolist()
            
            try:
                with st.spinner("Calculating data quality score..."):
                    from data.data_quality import calculate_data_quality_score
                    quality_score = calculate_data_quality_score(claims_df, required_fields_quality)
                    
                    # Track quality trends
                    from data.quality_trends import quality_trends
                    data_hash_quality = hashlib.md5(str(claims_df.columns.tolist()).encode()).hexdigest()
                    quality_trends.add_quality_score(
                        quality_score,
                        len(claims_df),
                        data_hash_quality,
                        metadata={"file": SessionStateManager.get("claims_file_obj")}
                    )
            except Exception as e:
                error_msg = get_user_friendly_error(e)
                st.error(f"Error calculating data quality score: {error_msg}")
                quality_score = {"overall_score": 0, "breakdown": {"completeness": 0, "uniqueness": 0, "consistency": 0}}
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Overall Score", f"{quality_score['overall_score']:.1f}/100")
            with col2:
                breakdown = quality_score.get('breakdown', {})
                completeness = float(breakdown.get('completeness', 0)) if isinstance(breakdown, dict) else 0.0
                st.metric("Completeness", f"{completeness:.1f}%")
            with col3:
                uniqueness = float(breakdown.get('uniqueness', 0)) if isinstance(breakdown, dict) else 0.0
                st.metric("Uniqueness", f"{uniqueness:.1f}%")
            with col4:
                consistency = float(breakdown.get('consistency', 0)) if isinstance(breakdown, dict) else 0.0
                st.metric("Consistency", f"{consistency:.1f}%")
            
            # Quality visualization
            breakdown = quality_score.get('breakdown', {})
            if breakdown:
                st.json(breakdown)
            
            # Column Statistics
            st.markdown("""
                <div style='margin-bottom: 0.5rem;'>
                    <h4 style='color: #111827; font-size: 1rem; font-weight: 600; margin: 0;'>Column Statistics</h4>
                </div>
            """, unsafe_allow_html=True)
            selected_col = st.selectbox("Select column to analyze", claims_df.columns.tolist(), key="col_stats_select")
            if selected_col:
                try:
                    from data.data_quality import get_column_statistics
                    col_stats = get_column_statistics(claims_df, selected_col)
                    st.json(col_stats)
                except Exception as e:
                    error_msg = get_user_friendly_error(e)
                    st.error(f"Error calculating column statistics: {error_msg}")
        else:
            st.info("No source data available for quality analysis.")
    
    # --- Tab 3: Advanced Analysis ---
    with tab3:
        # Use claims_df from top-level check (already validated)
        if claims_df is not None and not claims_df.empty:
            # Duplicate Detection
            with st.expander("🔍 Duplicate Detection", expanded=True):
                from data.data_quality import detect_duplicates
                dup_method = st.selectbox("Detection Method", ["exact", "key_based"], key="dup_method")
                dup_columns = st.multiselect("Columns to check", claims_df.columns.tolist(), key="dup_columns")
                if st.button("Detect Duplicates", key="detect_dups"):
                    if dup_columns:
                        try:
                            with st.spinner("Detecting duplicates..."):
                                duplicates = detect_duplicates(claims_df, dup_columns, dup_method)
                            if not duplicates.empty:
                                render_filterable_table(duplicates, key="duplicates_table")
                                st.info(f"Found {len(duplicates)} duplicate records")
                            else:
                                st.success("No duplicates found!")
                        except Exception as e:
                            error_msg = get_user_friendly_error(e)
                            st.error(f"Error detecting duplicates: {error_msg}")
            
            # Outlier Detection
            numeric_cols = claims_df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                with st.expander("Outlier Detection", expanded=False):
                    from data.data_quality import detect_outliers
                    outlier_col = st.selectbox("Select numeric column", numeric_cols, key="outlier_col")
                    outlier_method = st.selectbox("Method", ["zscore", "iqr"], key="outlier_method")
                    outlier_threshold = st.slider("Threshold", 1.0, 5.0, 3.0, 0.1, key="outlier_threshold")
                    if st.button("Detect Outliers", key="detect_outliers"):
                        try:
                            with st.spinner("Detecting outliers..."):
                                outliers = detect_outliers(claims_df, outlier_col, outlier_method, outlier_threshold)
                            if not outliers.empty:
                                render_filterable_table(outliers, key="outliers_table")
                                st.info(f"Found {len(outliers)} outliers")
                            else:
                                st.success("No outliers detected!")
                        except Exception as e:
                            error_msg = get_user_friendly_error(e)
                            st.error(f"Error detecting outliers: {error_msg}")
            
            # Completeness Matrix
            with st.expander("Data Completeness Matrix", expanded=False):
                try:
                    with st.spinner("Calculating completeness matrix..."):
                        from data.data_quality import create_completeness_matrix
                        completeness_matrix = create_completeness_matrix(claims_df)
                    if completeness_matrix.empty:
                        st.info("Unable to generate completeness matrix.")
                    else:
                        render_sortable_table(completeness_matrix, key="completeness_table")
                except Exception as e:
                    error_msg = get_user_friendly_error(e)
                    st.error(f"Error calculating completeness matrix: {error_msg}")
            
            # Data Sampling
            with st.expander("🎲 Data Sampling", expanded=False):
                from data.data_quality import sample_data
                sample_method = st.selectbox("Sampling Method", ["random", "first", "last"], key="sample_method")
                sample_size = st.number_input("Sample Size", 100, min(10000, len(claims_df)), 1000, key="sample_size")
                if st.button("Generate Sample", key="generate_sample"):
                    sample_df: pd.DataFrame = sample_data(claims_df, sample_method, sample_size)
                    render_lazy_dataframe(sample_df, key="sample_dataframe", max_rows_before_pagination=1000)
                    csv_data: bytes = sample_df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Sample", 
                                     csv_data,
                                     "sample_data.csv",
                                     "text/csv",
                                     key="download_sample")
        else:
            st.info("No source data available for advanced analysis.")
    