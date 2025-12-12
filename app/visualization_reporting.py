# --- visualization_reporting.py ---
"""Visualization and reporting features."""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional
from datetime import datetime

st: Any = st
pd: Any = pd
np: Any = np


def create_validation_dashboard(validation_results: List[Dict[str, Any]]) -> None:
    """Create visual validation dashboard with key metrics.
    
    Args:
        validation_results: List of validation results
    """
    if not validation_results:
        st.info("No validation results to display")
        return
    
    # Calculate metrics
    total_validations = len(validation_results)
    passed = len([r for r in validation_results if r.get("status") == "Pass"])
    failed = len([r for r in validation_results if r.get("status") == "Fail"])
    warnings = len([r for r in validation_results if r.get("status") == "Warning"])
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Validations", total_validations)
    with col2:
        st.metric("Passed", passed, delta=f"{(passed/total_validations*100):.1f}%")
    with col3:
        st.metric("Failed", failed, delta=f"-{(failed/total_validations*100):.1f}%", delta_color="inverse")
    with col4:
        st.metric("Warnings", warnings, delta=f"{(warnings/total_validations*100):.1f}%")
    
    # Status distribution chart
    if st.checkbox("Show Status Distribution", value=True):
        status_counts = pd.Series([r.get("status", "Unknown") for r in validation_results]).value_counts()
        st.bar_chart(status_counts)


def visualize_mapping(mapping: Dict[str, Dict[str, Any]], 
                      layout_df: Optional[pd.DataFrame] = None) -> None:
    """Create visual representation of field mappings.
    
    Args:
        mapping: Mapping dictionary
        layout_df: Optional layout DataFrame
    """
    # Create mapping visualization data
    mapping_data = []
    for field, mapping_info in mapping.items():
        mapping_data.append({
            "Internal Field": field,
            "Source Column": mapping_info.get("value", ""),
            "Mode": mapping_info.get("mode", "manual"),
            "Mapped": "Yes" if mapping_info.get("value") else "No"
        })
    
    if mapping_data:
        df = pd.DataFrame(mapping_data)
        
        # Show mapping status
        mapped_count = len(df[df["Mapped"] == "Yes"])
        total_count = len(df)
        
        st.metric("Mapping Coverage", f"{mapped_count}/{total_count}", 
                 delta=f"{(mapped_count/total_count*100):.1f}%")
        
        # Show mode distribution
        if "Mode" in df.columns:
            mode_counts = df["Mode"].value_counts()
            st.bar_chart(mode_counts)


def create_data_flow_diagram(mapping: Dict[str, Dict[str, Any]],
                            claims_df: Optional[pd.DataFrame] = None) -> str:
    """Generate data flow diagram visualization.
    
    Args:
        mapping: Mapping dictionary
        claims_df: Optional claims DataFrame
        
    Returns:
        Mermaid diagram string
    """
    diagram_lines = ["graph LR"]
    diagram_lines.append("    A[Claims File] --> B[Field Mapping]")
    diagram_lines.append("    B --> C[Data Transformation]")
    diagram_lines.append("    C --> D[Validation]")
    diagram_lines.append("    D --> E[Anonymization]")
    diagram_lines.append("    E --> F[Output Files]")
    
    # Add field mappings
    mapped_fields = [f for f, info in mapping.items() if info.get("value")]
    if mapped_fields:
        diagram_lines.append("    B --> G[{} Fields Mapped]".format(len(mapped_fields)))
    
    return "\n".join(diagram_lines)


def create_comparison_view(data1: Dict[str, Any], data2: Dict[str, Any],
                          comparison_type: str = "mapping") -> None:
    """Create side-by-side comparison view.
    
    Args:
        data1: First dataset
        data2: Second dataset
        comparison_type: Type of comparison (mapping, validation, file)
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Version 1")
        if comparison_type == "mapping":
            st.json(data1)
        else:
            st.dataframe(pd.DataFrame([data1]))
    
    with col2:
        st.subheader("Version 2")
        if comparison_type == "mapping":
            st.json(data2)
        else:
            st.dataframe(pd.DataFrame([data2]))
    
    # Show differences
    st.subheader("Differences")
    if comparison_type == "mapping":
        from mapping_enhancements import compare_mapping_versions
        differences = compare_mapping_versions(data1, data2)
        
        if differences["added"]:
            st.write("**Added:**", ", ".join(differences["added"]))
        if differences["removed"]:
            st.write("**Removed:**", ", ".join(differences["removed"]))
        if differences["changed"]:
            st.write("**Changed:**")
            for change in differences["changed"][:10]:  # Limit to 10
                st.write(f"- {change['field']}: '{change['old_value']}' → '{change['new_value']}'")


def create_interactive_charts(df: pd.DataFrame, chart_type: str = "distribution") -> None:
    """Create interactive charts for data visualization.
    
    Args:
        df: DataFrame
        chart_type: Type of chart (distribution, trend, correlation)
    """
    if df is None or df.empty:
        st.info("No data to visualize")
        return
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if chart_type == "distribution" and numeric_cols:
        selected_col = st.selectbox("Select column", numeric_cols)
        if selected_col:
            st.hist_chart(df[selected_col].dropna())
    
    elif chart_type == "trend" and numeric_cols:
        selected_col = st.selectbox("Select column", numeric_cols)
        date_col = st.selectbox("Select date column", df.columns.tolist())
        if selected_col and date_col:
            try:
                df[date_col] = pd.to_datetime(df[date_col])
                trend_df = df[[date_col, selected_col]].set_index(date_col)
                st.line_chart(trend_df)
            except Exception:
                st.error("Could not create trend chart")
    
    elif chart_type == "correlation" and len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        st.dataframe(corr_matrix)

