# --- tab_validation.py ---
"""Preview & Validate tab handler."""
import streamlit as st
from typing import Any, List, Dict
import hashlib
import time
import statistics
import pandas as pd
from state_manager import SessionStateManager
from config import DEFAULT_VALIDATION_PAGE_SIZE, VALIDATION_PAGE_SIZES
from improvements_utils import (
    render_empty_state,
    render_loading_skeleton,
)
from ui_improvements import (
    render_sortable_table,
    render_tooltip
)
from error_handling import get_user_friendly_error
from ui_improvements import show_toast
from validation_engine import run_validations, dynamic_run_validations
from layout_loader import get_required_fields
from advanced_validation import track_validation_performance
from validation_builder import CustomValidationRule, save_custom_rule, load_custom_rules, run_custom_validations
from performance_utils import paginate_dataframe
from ui_components import _notify
from audit_logger import log_event

st: Any = st


def render_validation_tab() -> None:
    """Render the Preview & Validate tab content."""
    transformed_df = SessionStateManager.get_transformed_df()
    final_mapping = SessionStateManager.get_final_mapping()
    layout_df = SessionStateManager.get_layout_df()

    if transformed_df is None or not final_mapping:
        render_empty_state(
            icon="📋",
            title="Mapping Required",
            message="Please complete field mappings and preview transformed data first.",
            action_label="Go to Field Mapping Tab",
            action_callback=lambda: SessionStateManager.set("active_tab", "Field Mapping")
        )
        st.stop()
    else:
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

    # --- Validation Metrics Summary ---
    st.markdown("#### Validation Summary")
    validation_results_summary: List[Dict[str, Any]] = st.session_state.get("validation_results", [])

    fails: List[Dict[str, Any]] = [r for r in validation_results_summary if r.get("status") == "Fail"]
    warnings: List[Dict[str, Any]] = [r for r in validation_results_summary if r.get("status") == "Warning"]
    passes: List[Dict[str, Any]] = [r for r in validation_results_summary if r.get("status") == "Pass"]
    
    # Initialize other_failures and other_warnings early to avoid scope issues
    other_failures: List[Dict[str, Any]] = []
    other_warnings: List[Dict[str, Any]] = []

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Checks", value=len(validation_results_summary))
    with col2:
        st.metric(label="✅ Passes", value=len(passes))
    with col3:
        st.metric(label="⚠️ Warnings / ❌ Fails", value=len(warnings) + len(fails))

    st.divider()

    # --- Custom Validation Rules Builder ---
    with st.expander("🔧 Custom Validation Rules Builder", expanded=False):
        st.markdown("Create custom validation rules for your data")
        rule_name = st.text_input("Rule Name:", key="custom_rule_name", placeholder="e.g., 'Email Format Check'")
        rule_field = st.selectbox(
            "Field to Validate:",
            options=[""] + (transformed_df.columns.tolist() if transformed_df is not None else []),
            key="custom_rule_field"
        )
        rule_type = st.selectbox(
            "Rule Type:",
            options=["null_check", "min_value", "max_value", "pattern_match"],
            key="custom_rule_type",
            help="null_check: Check null percentage\nmin_value: Minimum value threshold\nmax_value: Maximum value threshold\npattern_match: Pattern matching (coming soon)"
        )
        if rule_type in ["null_check", "min_value", "max_value"]:
            rule_threshold = st.number_input(
                "Threshold:",
                min_value=0.0,
                max_value=100.0 if rule_type == "null_check" else float('inf'),
                value=10.0,
                key="custom_rule_threshold"
            )
        else:
            rule_threshold = 0.0
        if st.button("Add Custom Rule", key="add_custom_rule"):
            if rule_name and rule_field:
                rule = CustomValidationRule(rule_name, rule_field, rule_type, rule_threshold)
                save_custom_rule(rule)
                show_toast(f"Custom rule '{rule_name}' added!", "✅")
                st.session_state.needs_refresh = True
            else:
                st.warning("Please provide both rule name and field")
        custom_rules = load_custom_rules()
        if custom_rules:
            st.markdown("**Existing Custom Rules:**")
            for i, rule in enumerate(custom_rules):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"- **{rule['name']}**: {rule['field']} ({rule['rule_type']}, threshold: {rule['threshold']})")
                with col2:
                    if st.button("Remove", key=f"remove_rule_{i}"):
                        st.session_state.custom_validation_rules.pop(i)
                        show_toast("Custom rule removed", "🗑️")
                        st.session_state.needs_refresh = True
            if st.button("Run Custom Validations", key="run_custom_validations"):
                if transformed_df is not None:
                    custom_results = run_custom_validations(transformed_df, custom_rules)
                    current_validation_results: List[Dict[str, Any]] = st.session_state.get("validation_results", [])
                    current_validation_results.extend(custom_results)
                    st.session_state.validation_results = current_validation_results
                    show_toast(f"Ran {len(custom_results)} custom validation(s)", "✅")
                    st.session_state.needs_refresh = True

    st.divider()

    # --- Detailed Validation Table ---
    st.markdown("#### Detailed Validation Results")
    if validation_results_summary:
        if len(validation_results_summary) > DEFAULT_VALIDATION_PAGE_SIZE:
            default_index = VALIDATION_PAGE_SIZES.index(DEFAULT_VALIDATION_PAGE_SIZE) if DEFAULT_VALIDATION_PAGE_SIZE in VALIDATION_PAGE_SIZES else 1
            page_size = st.selectbox("Results per page:", VALIDATION_PAGE_SIZES, index=default_index, key="validation_page_size")
            paginated_results, page_num, total_pages = paginate_dataframe(
                pd.DataFrame(validation_results_summary),
                page_size=page_size
            )
            st.caption(f"Page {page_num} of {total_pages} ({len(validation_results_summary)} total results)")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Previous", key="prev_validation_page", disabled=page_num == 1):
                    st.session_state.validation_page_num = max(1, page_num - 1)
                if st.button("Next →", key="next_validation_page", disabled=page_num == total_pages):
                    st.session_state.validation_page_num = min(total_pages, page_num + 1)
            validation_df = paginated_results
        else:
            validation_df = pd.DataFrame(validation_results_summary)
        if validation_df.empty:
            render_empty_state(
                icon="✅",
                title="No Validation Issues",
                message="All validations passed! Your data looks good."
            )
        else:
            render_sortable_table(validation_df, key="validation_results_table")

        val_csv = validation_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Validation Report",
            data=val_csv,
            file_name="validation_report.csv",
            mime="text/csv",
            key="download_validation_report",
            on_click=lambda: _notify("✅ Validation Report Ready!")
        )
    else:
        st.info("No validation results to display. Click 'Run Validation' to perform checks.")

    st.divider()

    # --- Final Verdict Block with Threshold Analysis ---
    st.markdown("#### File Status & Validation Summary")

    if not validation_results_summary:
        st.info("No validations have been run yet.")
    else:
        # Analyze validation results to calculate thresholds and stats
        if layout_df is None:
            required_fields_tab3: List[str] = []
        else:
            cache_key_tab3 = f"required_fields_{id(layout_df)}"
            if cache_key_tab3 in st.session_state:
                required_fields_tab3 = st.session_state[cache_key_tab3]
            else:
                usage_normalized = layout_df["Usage"].astype(str).str.strip().str.lower()
                required_fields_tab3 = layout_df[usage_normalized == "mandatory"]["Internal Field"].tolist()
                st.session_state[cache_key_tab3] = required_fields_tab3
        
        unmapped_required_fields_tab3: List[str] = []
        for field in required_fields_tab3:
            mapping = final_mapping.get(field)
            if not mapping or not mapping.get("value") or str(mapping.get("value")).strip() == "":
                unmapped_required_fields_tab3.append(field)
        
        total_records = len(transformed_df) if transformed_df is not None else 0
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
            null_percentages: List[float] = [float(s["null_percentage"]) for s in required_field_null_stats]
            avg_null_pct: float = sum(null_percentages) / len(null_percentages) if null_percentages else 0.0
            max_null_pct: float = max(null_percentages) if null_percentages else 0.0
            if len(null_percentages) > 1:
                try:
                    std_dev: float = statistics.stdev(null_percentages)
                    suggested_threshold: float = min(max(avg_null_pct + (2 * std_dev), 1.0), 15.0)
                except (statistics.StatisticsError, ValueError):
                    suggested_threshold = min(max(avg_null_pct + 3.0, 2.0), 10.0)
            else:
                suggested_threshold = min(max(avg_null_pct + 3.0, 2.0), 10.0)
        else:
            avg_null_pct = 0.0
            max_null_pct = 0.0
            suggested_threshold = 5.0
        
        fields_exceeding_threshold: List[Dict[str, Any]] = []
        for stat_item in required_field_null_stats:
            stat_dict: Dict[str, Any] = stat_item
            if float(stat_dict.get("null_percentage", 0)) > suggested_threshold:
                fields_exceeding_threshold.append(stat_dict)
        
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
        
        is_rejected = len(unmapped_required_fields_tab3) > 0
        has_critical_issues = len(fields_exceeding_threshold) > 0
        has_warnings = len(other_failures) > 0
        
        # --- Status Display ---
        if is_rejected:
            st.markdown(
                """
                <div style='background-color:#f5f5f5; padding: 0.75rem 1rem; border-radius: 4px; margin-bottom: 0.5rem; border: 1px solid #ddd;'>
                <strong style='color: #000000; font-size: 1rem;'>❌ File Status: Rejected</strong>
                <p style='color: #000000; margin-top: 0.25rem; margin-bottom: 0; font-size: 13px;'>Mandatory fields are missing from the file.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif has_critical_issues:
            st.markdown(
                """
                <div style='background-color:#f5f5f5; padding: 0.75rem 1rem; border-radius: 4px; margin-bottom: 0.5rem; border: 1px solid #ddd;'>
                <strong style='color: #000000; font-size: 1rem;'>⚠️ File Status: Needs Review</strong>
                <p style='color: #000000; margin-top: 0.25rem; margin-bottom: 0; font-size: 13px;'>Some required fields have high null rates that exceed recommended thresholds.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif has_warnings:
            st.markdown(
                """
                <div style='background-color:#f5f5f5; padding: 0.75rem 1rem; border-radius: 4px; margin-bottom: 0.5rem; border: 1px solid #ddd;'>
                <strong style='color: #000000; font-size: 1rem;'>ℹ️ File Status: Approved with Warnings</strong>
                <p style='color: #000000; margin-top: 0.25rem; margin-bottom: 0; font-size: 13px;'>File meets requirements but has some data quality issues to review.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style='background-color:#f5f5f5; padding: 0.75rem 1rem; border-radius: 4px; margin-bottom: 0.5rem; border: 1px solid #ddd;'>
                <strong style='color: #000000; font-size: 1rem;'>✅ File Status: Approved</strong>
                <p style='color: #000000; margin-top: 0.25rem; margin-bottom: 0; font-size: 13px;'>All validation checks passed. File is ready for processing.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # --- Detailed Status Summary (Collapsible Sections) ---
        with st.expander("📋 Mandatory Fields Status", expanded=False):
            if unmapped_required_fields_tab3:
                field_list = ", ".join(f"`{f}`" for f in unmapped_required_fields_tab3)
                st.error(f"**Missing Fields:** {field_list}")
                st.caption("These mandatory fields must be present in the source file and properly mapped.")
            else:
                st.success(f"✅ All {len(required_fields_tab3)} required fields are mapped and available in the file.")
        
        if required_field_null_stats:
            with st.expander("📊 Mandatory Fields Analysis", expanded=False):
                total_records = len(transformed_df) if transformed_df is not None else 0
                fields_with_no_nulls: List[Dict[str, Any]] = [s for s in required_field_null_stats if s["null_percentage"] == 0.0]
                fields_with_low_nulls: List[Dict[str, Any]] = [s for s in required_field_null_stats if 0 < s["null_percentage"] <= suggested_threshold]
                fields_with_high_nulls = fields_exceeding_threshold
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Mandatory Fields", len(required_field_null_stats))
                with col2:
                    st.metric("Perfect Fields (0% null)", len(fields_with_no_nulls))
                with col3:
                    st.metric("Fields Within Threshold", len(fields_with_low_nulls))
                with col4:
                    st.metric("Fields Exceeding Threshold", len(fields_with_high_nulls))
                st.markdown("---")
                st.markdown("#### 📈 Key Insights")
                if len(fields_with_no_nulls) == len(required_field_null_stats):
                    st.success(f"**Excellent Data Quality:** All {len(required_field_null_stats)} mandatory fields have zero null values. This file demonstrates exceptional data completeness.")
                elif len(fields_with_high_nulls) == 0:
                    completeness_pct = ((len(fields_with_no_nulls) + len(fields_with_low_nulls)) / len(required_field_null_stats) * 100) if required_field_null_stats else 0
                    st.success(f"**Good Data Quality:** {completeness_pct:.1f}% of mandatory fields ({len(fields_with_no_nulls) + len(fields_with_low_nulls)}/{len(required_field_null_stats)}) are within acceptable null rate thresholds.")
                else:
                    st.warning(f"**Data Quality Concerns:** {len(fields_with_high_nulls)} out of {len(required_field_null_stats)} mandatory fields ({len(fields_with_high_nulls)/len(required_field_null_stats)*100:.1f}%) exceed the recommended null rate threshold.")
                st.markdown(f"""
                <div style='background-color:#f3f4f6; padding: 1rem; border-radius: 6px; margin-top: 1rem; margin-bottom: 1rem; border-left: 3px solid #6b7280;'>
                <strong>📋 Recommended Threshold: {suggested_threshold:.1f}%</strong><br>
                Based on statistical analysis of this file's data, the recommended null rate threshold for mandatory fields is <strong>{suggested_threshold:.1f}%</strong>. 
                This is calculated from the average null rate ({avg_null_pct:.2f}%) plus 2 standard deviations, ensuring data quality while accounting for expected variations.
                </div>
                """, unsafe_allow_html=True)
                if fields_exceeding_threshold:
                    st.markdown("#### ⚠️ Fields Requiring Attention")
                    st.markdown("The following mandatory fields have null rates that exceed the recommended threshold:")
                    list_items: List[str] = []
                    for field_stat in sorted(fields_exceeding_threshold, key=lambda x: x["null_percentage"], reverse=True):
                        field_name = field_stat["field"]
                        null_pct = field_stat["null_percentage"]
                        null_count = field_stat["null_count"]
                        fill_rate = 100 - null_pct
                        list_items.append(f"- **{field_name}**: {null_pct:.2f}% null ({null_count:,} of {total_records:,} records) - Fill rate: {fill_rate:.2f}%")
                    st.markdown("\n".join(list_items))
                    worst_field = max(fields_exceeding_threshold, key=lambda x: x["null_percentage"])
                    st.info(f"""
                    **💡 Recommendation:** Focus on improving data collection for **{worst_field['field']}** first, as it has the highest null rate ({worst_field['null_percentage']:.2f}%). 
                    This field affects {worst_field['null_count']:,} records ({worst_field['null_percentage']:.2f}% of the file).
                    """)
                else:
                    st.success(f"✅ **All mandatory fields meet quality standards.** All {len(required_field_null_stats)} fields have null rates below the recommended {suggested_threshold:.1f}% threshold.")
                st.markdown("<details><summary>📋 View All Mandatory Fields Breakdown</summary>", unsafe_allow_html=True)
                sorted_stats: List[Dict[str, Any]] = sorted(required_field_null_stats, key=lambda x: x["null_percentage"], reverse=True)
                breakdown_items: List[str] = []
                for stat in sorted_stats:
                    field_name: str = str(stat["field"])
                    null_pct: float = float(stat["null_percentage"])
                    null_count: int = int(stat["null_count"])
                    fill_rate: float = 100 - null_pct
                    status_icon = "✅" if null_pct <= suggested_threshold else "⚠️"
                    breakdown_items.append(f"{status_icon} **{field_name}**: {null_pct:.2f}% null ({fill_rate:.2f}% filled) - {null_count:,} null records")
                st.markdown("\n\n".join(breakdown_items))
                st.markdown("</details>", unsafe_allow_html=True)
        
        if other_failures or other_warnings:
            with st.expander("⚠️ Other Mandatory Field Validations", expanded=False):
                if other_failures:
                    st.markdown("**Critical Issues:**")
                    failure_list: List[str] = []
                    for issue in other_failures:
                        check_name = issue.get("check", "Unknown Check")
                        field = issue.get("field", "")
                        message = issue.get("message", "")
                        if field:
                            failure_list.append(f"- **{check_name}** ({field}): {message}")
                        else:
                            failure_list.append(f"- **{check_name}**: {message}")
                    st.markdown("\n".join(failure_list))
                if other_warnings:
                    st.markdown("**Warnings:**")
                    warning_list: List[str] = []
                    for issue in other_warnings:
                        check_name = issue.get("check", "Unknown Check")
                        field = issue.get("field", "")
                        message = issue.get("message", "")
                        if field:
                            warning_list.append(f"- **{check_name}** ({field}): {message}")
                        else:
                            warning_list.append(f"- **{check_name}**: {message}")
                    st.markdown("\n".join(warning_list))
        
        file_level_results = [r for r in validation_results_summary if not r.get("field")]
        if file_level_results:
            with st.expander("📈 File-Level Summary", expanded=False):
                for result in file_level_results:
                    check_name = result.get("check", "Unknown")
                    message = result.get("message", "")
                    status = result.get("status", "")
                    if check_name == "Required Fields Completeness":
                        if "%" in message:
                            st.metric("Mandatory Fields Completeness", message)
                        else:
                            if status == "Pass":
                                st.success(f"✅ **{check_name}**: {message}")
                            else:
                                st.error(f"❌ **{check_name}**: {message}")
                    else:
                        if status == "Pass":
                            st.success(f"✅ **{check_name}**: {message}")
                        elif status == "Warning":
                            st.warning(f"⚠️ **{check_name}**: {message}")
                        else:
                            st.error(f"❌ **{check_name}**: {message}")
        
        if is_rejected:
            with st.expander("❌ Rejection Explanation", expanded=False):
                field_list = ", ".join(f"`{f}`" for f in unmapped_required_fields_tab3)
                rejection_text = (
                    f"This file has been **rejected** because the following mandatory fields required for Targeted Marketing setup are missing: {field_list}. "
                    f"These fields must be present in the source file and properly mapped before the file can be processed. "
                    f"Please ensure these fields are included in your source data and re-upload the file."
                )
                st.markdown(rejection_text)
                if has_critical_issues or has_warnings:
                    additional_issues: List[str] = []
                    if has_critical_issues:
                        additional_issues.append(f"{len(fields_exceeding_threshold)} required field(s) with high null rates")
                    if other_failures:
                        additional_issues.append(f"{len(other_failures)} other validation failure(s)")
                    if other_warnings:
                        additional_issues.append(f"{len(other_warnings)} warning(s)")
                    st.markdown("---")
                    st.markdown(f"""
                    <div style='background-color:#fff3cd; padding: 1rem; border-radius: 6px;'>
                    <strong>Additional Issues to Address:</strong> Once the mandatory fields are added, please also review: {', '.join(additional_issues)}.
                    </div>
                    """, unsafe_allow_html=True)

