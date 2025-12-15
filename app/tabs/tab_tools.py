# --- tab_tools.py ---
"""Tools & Analytics tab handler."""
import streamlit as st
from typing import Any
import pandas as pd
from core.state_manager import SessionStateManager
from utils.improvements_utils import (
    render_empty_state,
    DEBOUNCE_DELAY_SECONDS,
    get_memory_usage
)
from performance.performance_utils import render_lazy_dataframe
from ui.ui_improvements import render_tooltip, show_toast, show_confirmation_dialog
from monitoring.monitoring_logging import (
    get_system_health,
    get_error_statistics,
    export_logs,
    get_usage_statistics
)
from validation.advanced_validation import get_validation_performance_stats
from testing_qa import create_mapping_unit_tests, run_unit_tests
import time

# Optional imports for features that may not be available
try:
    from test_data_generator import generate_test_data_from_claims, generate_test_data_from_layout
except ImportError:
    generate_test_data_from_claims = None
    generate_test_data_from_layout = None

try:
    from help_system import get_help_content, global_search
except ImportError:
    def get_help_content(topic: str) -> str:
        return f"Help content for {topic} is not available."
    def global_search(query: str) -> dict:
        return {}

try:
    from notification_system import get_notifications, mark_notification_read, clear_notifications
except ImportError:
    def get_notifications(unread_only: bool = False) -> list:
        return []
    def mark_notification_read(index: int) -> None:
        pass
    def clear_notifications() -> None:
        pass

st: Any = st


def render_tools_tab() -> None:
    """Render the Tools & Analytics tab content."""
    st.markdown("## 🛠️ Tools & Analytics")
    tool_tab1, tool_tab2, tool_tab3, tool_tab4 = st.tabs([
        "System Health",
        "Usage Analytics",
        "Testing & QA",
        "Help & Documentation"
    ])
    
    with tool_tab1:
        st.markdown("### 💻 System Health & Performance")
        health = get_system_health()
        memory_usage = get_memory_usage()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            cpu_usage = health.get('cpu_percent', 0)
            st.metric("CPU Usage", f"{cpu_usage:.1f}%")
            if cpu_usage > 80:
                st.warning("⚠️ High CPU usage")
        with col2:
            memory_mb = health.get('memory_mb', 0)
            st.metric("Memory Usage", f"{memory_mb:.0f} MB")
            if memory_mb > 1000:
                st.warning("⚠️ High memory usage")
        with col3:
            memory_pct = health.get('memory_percent', 0)
            st.metric("Memory %", f"{memory_pct:.1f}%")
            if memory_pct > 80:
                st.warning("⚠️ High memory percentage")
        with col4:
            st.metric("Threads", health.get('threads', 0))
        
        st.markdown("#### 📊 Detailed Memory Information")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("RSS Memory", f"{memory_usage.get('rss_mb', 0):.1f} MB")
        with col2:
            st.metric("VMS Memory", f"{memory_usage.get('vms_mb', 0):.1f} MB")
        
        st.markdown("#### ⚡ Operation Performance")
        perf_stats = get_validation_performance_stats()
        if perf_stats and perf_stats.get('operations'):
            perf_df = pd.DataFrame(perf_stats['operations'])
            if not perf_df.empty:
                slow_ops = perf_df[perf_df['avg_time'] > 5.0] if 'avg_time' in perf_df.columns else pd.DataFrame()
                if not slow_ops.empty:
                    st.warning("⚠️ Slow Operations Detected (>5 seconds):")
                    render_lazy_dataframe(slow_ops[['operation', 'avg_time', 'count']], key="slow_ops_table", max_rows_before_pagination=100)
                else:
                    st.success("✅ All operations are performing well (<5 seconds)")
                if 'avg_time' in perf_df.columns:
                    st.bar_chart(perf_df.set_index('operation')['avg_time'])
        
        st.markdown("#### ⚠️ Error Statistics")
        error_stats = get_error_statistics()
        if error_stats:
            st.json(error_stats)
        else:
            st.info("No errors recorded")
        
        st.markdown("### 📥 Export Logs")
        log_type = st.selectbox("Log Type", ["audit", "error", "usage"], key="export_log_type")
        log_format = st.selectbox("Format", ["json", "csv"], key="export_log_format")
        if st.button("Export Logs", key="export_logs"):
            log_data: str = export_logs(log_type, log_format)
            st.download_button("Download", log_data.encode('utf-8'),
                             f"{log_type}_log.{log_format}",
                             "text/plain" if log_format == "json" else "text/csv",
                             key="download_logs")
    
    with tool_tab2:
        st.markdown("### 📊 Usage Analytics Dashboard")
        usage_stats = get_usage_statistics()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Actions", usage_stats.get("total_actions", 0))
        with col2:
            st.metric("Unique Features", len(usage_stats.get("features_used", {})))
        with col3:
            st.metric("Session Duration", f"{usage_stats.get('session_duration_minutes', 0):.1f} min")
        
        st.markdown("#### 📈 Features Used")
        features_used = usage_stats.get("features_used", {})
        if features_used:
            features_df = pd.DataFrame(list(features_used.items()), columns=["Feature", "Count"])
            features_df = features_df.sort_values("Count", ascending=False)
            st.bar_chart(features_df.set_index("Feature"))
            st.markdown("#### 🏆 Top 5 Most Used Features")
            top_features = features_df.head(5)
            for idx, row in top_features.iterrows():
                st.markdown(f"**{row['Feature']}**: {row['Count']} times")
        else:
            st.info("No usage data yet. Start using the app to see analytics!")
        
        st.markdown("#### ⚡ Validation Performance Summary")
        perf_stats = get_validation_performance_stats()
        if perf_stats and perf_stats.get('summary'):
            summary = perf_stats['summary']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Validation Time", f"{summary.get('avg_time', 0):.2f}s")
            with col2:
                st.metric("Total Validations", summary.get('total_validations', 0))
            with col3:
                st.metric("Records Processed", summary.get('total_records', 0))
        
        if perf_stats and perf_stats.get('operations'):
            st.markdown("#### 📊 Performance Trends")
            perf_df = pd.DataFrame(perf_stats['operations'])
            if not perf_df.empty and 'avg_time' in perf_df.columns:
                st.line_chart(perf_df.set_index('operation')['avg_time'])
    
    with tool_tab3:
        st.markdown("### 🧪 Testing & Quality Assurance")
        with st.expander("Generate Test Data", expanded=False):
            claims_df = SessionStateManager.get_claims_df()
            layout_df = SessionStateManager.get_layout_df()
            if claims_df is None and layout_df is None:
                st.info("Please upload a claims file or layout file first to generate test data based on its structure.")
            else:
                test_data_type = st.selectbox("Data Type", 
                    [opt for opt in ["claims", "layout"] if (opt == "claims" and claims_df is not None) or (opt == "layout" and layout_df is not None)],
                    key="test_data_type")
            test_data_count = st.number_input("Record Count", 10, 10000, 100, key="test_data_count")
            if st.button("Generate Test Data", key="generate_test_data"):
                if generate_test_data_from_claims is None or generate_test_data_from_layout is None:
                    st.error("Test data generator is not available. Please install the test_data_generator module.")
                    st.stop()
                test_df = None
                test_data_type = st.session_state.get("test_data_type", "claims")
                if test_data_type == "claims" and claims_df is not None:
                    test_df = generate_test_data_from_claims(claims_df, test_data_count)
                elif test_data_type == "layout" and layout_df is not None:
                    test_df = generate_test_data_from_layout(layout_df, test_data_count)
                else:
                    st.error("Unable to generate test data. Please ensure the required file is uploaded.")
                    st.stop()
                if test_df is not None:
                    render_lazy_dataframe(test_df, key="test_dataframe", max_rows_before_pagination=1000)
                    csv_data: bytes = test_df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Test Data",
                                 csv_data,
                                 f"test_{test_data_type}.csv",
                                 "text/csv",
                                 key="download_test_data")
        
        st.markdown("#### 🧪 Unit Test Results")
        st.caption("Unit tests run automatically when mappings are applied. Results are shown below.")
        final_mapping = SessionStateManager.get_final_mapping()
        mappings_ready = st.session_state.get("mappings_ready", False)
        if not mappings_ready or not final_mapping:
            st.info("Complete your field mappings first. Tests will run automatically when mappings are applied.")
        else:
            unit_test_results = st.session_state.get("unit_test_results")
            if unit_test_results:
                total = unit_test_results.get("total", 0)
                passed = unit_test_results.get("passed", 0)
                failed = unit_test_results.get("failed", 0)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Tests", total)
                with col2:
                    st.metric("Passed", passed, delta=f"{int((passed/total*100) if total > 0 else 0)}%")
                with col3:
                    st.metric("Failed", failed, delta=f"{int((failed/total*100) if total > 0 else 0)}%")
                if st.button("🔄 Re-run Tests", key="rerun_tests_tools_tab", use_container_width=True):
                    with st.spinner("Running unit tests..."):
                        try:
                            claims_df = SessionStateManager.get_claims_df()
                            layout_df = SessionStateManager.get_layout_df()
                            tests = create_mapping_unit_tests(final_mapping, claims_df, layout_df)
                            test_results = run_unit_tests(tests)
                            st.session_state.unit_test_results = test_results
                            st.session_state.last_mapping_hash = str(hash(str(final_mapping)))
                            st.success(f"Tests completed: {test_results['passed']}/{test_results['total']} passed")
                            st.session_state.needs_refresh = True
                        except Exception as e:
                            st.error(f"Error running tests: {e}")
                st.divider()
                if unit_test_results.get("test_results"):
                    st.markdown("##### Detailed Results")
                    for result in unit_test_results["test_results"]:
                        test_name = result.get("name", "Unknown")
                        passed_status = result.get("passed", False)
                        icon = "✅" if passed_status else "❌"
                        st.markdown(f"{icon} **{test_name}**")
                        if not passed_status:
                            error = result.get("error", "")
                            expected = result.get("expected", "")
                            actual = result.get("actual", "")
                            if error:
                                st.error(f"Error: {error}")
                            else:
                                st.warning(f"Expected: {expected}, Got: {actual}")
            else:
                st.info("Unit tests are running automatically. Results will appear here once mappings are applied.")
    
    with tool_tab4:
        st.markdown("### 📚 Help & Documentation")
        help_topic = st.selectbox("Select Topic", 
                                 ["file_upload", "mapping", "validation", "outputs"],
                                 key="help_topic")
        help_content = get_help_content(help_topic)
        if help_content:
            st.markdown(help_content)
        
        st.markdown("### 🔍 Global Search")
        render_tooltip(
            "Search across all tabs, fields, mappings, and data",
            "This search looks through field names, mappings, validation results, and more."
        )
        raw_search_input = st.text_input("Search across all tabs", key="global_search_input_raw", placeholder="Type to search...")
        
        current_time = time.time()
        last_search_time = st.session_state.get("global_search_last_time", 0)
        debounced_search = st.session_state.get("global_search_input", "")
        
        if raw_search_input != st.session_state.get("global_search_input_raw_prev", ""):
            st.session_state.global_search_input_raw_prev = raw_search_input
            if current_time - last_search_time >= DEBOUNCE_DELAY_SECONDS:
                debounced_search = raw_search_input
                st.session_state.global_search_input = debounced_search
                st.session_state.global_search_last_time = current_time
            else:
                st.session_state.global_search_pending = raw_search_input
        
        if "global_search_pending" in st.session_state:
            if current_time - last_search_time >= DEBOUNCE_DELAY_SECONDS:
                debounced_search = st.session_state.global_search_pending
                st.session_state.global_search_input = debounced_search
                st.session_state.global_search_last_time = current_time
                del st.session_state.global_search_pending
        
        search_query = debounced_search
        if search_query:
            search_results = global_search(search_query)
            if any(search_results.values()):
                for scope, results in search_results.items():
                    if results:
                        st.markdown(f"#### {scope.title()}")
                        st.write(results)
            else:
                render_empty_state(
                    icon="🔍",
                    title="No Results Found",
                    message=f"No matches found for '{search_query}'. Try different search terms."
                )
        
        st.markdown("### 🔔 Notification Center")
        notifications = get_notifications(unread_only=True)
        if notifications:
            for i, notif in enumerate(notifications[:10]):
                severity = notif.get("severity", "info")
                if severity == "error":
                    st.error(f"{notif.get('message', '')}")
                elif severity == "warning":
                    st.warning(f"{notif.get('message', '')}")
                elif severity == "success":
                    st.success(f"{notif.get('message', '')}")
                else:
                    st.info(f"{notif.get('message', '')}")
                if st.button("Mark as Read", key=f"read_notif_{i}"):
                    mark_notification_read(i)
                    show_toast("Notification marked as read", "✅")
                    st.session_state.needs_refresh = True
        else:
            st.info("No unread notifications")
        if st.button("Clear All Notifications", key="clear_notifications"):
            if show_confirmation_dialog(
                "Clear All Notifications",
                "Are you sure you want to clear all notifications?",
                confirm_label="Yes, Clear",
                cancel_label="Cancel",
                key="clear_notifications_confirm"
            ):
                clear_notifications()
                show_toast("All notifications cleared", "🗑️")
                st.session_state.needs_refresh = True

