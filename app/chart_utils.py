# --- chart_utils.py ---
"""Interactive chart utilities using Plotly and Altair."""
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

# Try to import visualization libraries
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    px = None
    go = None

try:
    import altair as alt
    ALTAIR_AVAILABLE = True
except ImportError:
    ALTAIR_AVAILABLE = False
    alt = None

st: Any = st


def render_data_quality_chart(quality_scores: Dict[str, float], chart_type: str = "bar") -> None:
    """
    Render data quality scores as interactive chart.
    
    Args:
        quality_scores: Dictionary of quality metric scores
        chart_type: Type of chart ("bar", "radar", "gauge")
    """
    if not quality_scores:
        st.warning("No quality scores to display")
        return
    
    if chart_type == "bar" and PLOTLY_AVAILABLE:
        df = pd.DataFrame({
            "Metric": list(quality_scores.keys()),
            "Score": list(quality_scores.values())
        })
        
        fig = px.bar(
            df,
            x="Metric",
            y="Score",
            title="Data Quality Scores",
            color="Score",
            color_continuous_scale="RdYlGn",
            range_y=[0, 100]
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "radar" and PLOTLY_AVAILABLE:
        categories = list(quality_scores.keys())
        values = list(quality_scores.values())
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Quality Score'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="Data Quality Radar Chart",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    elif ALTAIR_AVAILABLE:
        # Fallback to Altair
        df = pd.DataFrame({
            "metric": list(quality_scores.keys()),
            "score": list(quality_scores.values())
        })
        
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("metric", sort="-y"),
            y=alt.Y("score", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("score", scale=alt.Scale(scheme="redyellowgreen"))
        ).properties(
            title="Data Quality Scores",
            height=400
        )
        st.altair_chart(chart, use_container_width=True)
    
    else:
        # Fallback to simple bar chart using Streamlit
        st.bar_chart(pd.DataFrame(quality_scores, index=[0]).T)


def render_validation_results_chart(validation_results: List[Dict[str, Any]]) -> None:
    """
    Render validation results as interactive chart.
    
    Args:
        validation_results: List of validation result dictionaries
    """
    if not validation_results:
        st.info("No validation results to display")
        return
    
    # Count by status
    status_counts = {}
    for result in validation_results:
        status = result.get("status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if PLOTLY_AVAILABLE:
        df = pd.DataFrame({
            "Status": list(status_counts.keys()),
            "Count": list(status_counts.values())
        })
        
        colors = {
            "Pass": "#4CAF50",
            "Warning": "#FF9800",
            "Fail": "#F44336",
            "Error": "#9C27B0"
        }
        
        fig = px.pie(
            df,
            values="Count",
            names="Status",
            title="Validation Results Distribution",
            color="Status",
            color_discrete_map=colors
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    elif ALTAIR_AVAILABLE:
        df = pd.DataFrame({
            "status": list(status_counts.keys()),
            "count": list(status_counts.values())
        })
        
        chart = alt.Chart(df).mark_arc().encode(
            theta=alt.Theta("count:Q"),
            color=alt.Color("status:N", scale=alt.Scale(
                domain=["Pass", "Warning", "Fail", "Error"],
                range=["#4CAF50", "#FF9800", "#F44336", "#9C27B0"]
            ))
        ).properties(
            title="Validation Results Distribution",
            height=400
        )
        st.altair_chart(chart, use_container_width=True)
    
    else:
        st.bar_chart(pd.DataFrame(status_counts, index=[0]).T)


def render_field_mapping_visualization(mapping: Dict[str, Dict[str, Any]]) -> None:
    """
    Render field mapping as visual diagram.
    
    Args:
        mapping: Mapping dictionary
    """
    if not mapping:
        st.info("No mappings to visualize")
        return
    
    # Create a simple visualization showing source -> target mappings
    if PLOTLY_AVAILABLE:
        source_fields = []
        target_fields = []
        
        for target, mapping_info in mapping.items():
            source = mapping_info.get("value", "")
            if source:
                source_fields.append(source)
                target_fields.append(target)
        
        if source_fields:
            # Create sankey diagram
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    label=list(set(source_fields + target_fields)),
                    color=["#2196F3"] * len(set(source_fields)) + ["#4CAF50"] * len(set(target_fields))
                ),
                link=dict(
                    source=[list(set(source_fields + target_fields)).index(s) for s in source_fields],
                    target=[list(set(source_fields + target_fields)).index(t) for t in target_fields],
                    value=[1] * len(source_fields)
                )
            )])
            
            fig.update_layout(title="Field Mapping Flow", height=600)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No active mappings to visualize")
    else:
        # Fallback to simple text representation
        st.markdown("### Field Mappings")
        for target, mapping_info in mapping.items():
            source = mapping_info.get("value", "")
            if source:
                st.markdown(f"**{source}** → {target}")


def render_completeness_matrix(df: pd.DataFrame, columns: Optional[List[str]] = None) -> None:
    """
    Render data completeness matrix as heatmap.
    
    Args:
        df: DataFrame to analyze
        columns: Optional list of columns to include
    """
    if df is None or df.empty:
        st.warning("No data to display")
        return
    
    columns = columns or df.columns.tolist()
    
    # Calculate completeness percentage for each column
    completeness = {}
    for col in columns:
        if col in df.columns:
            non_null = df[col].notna().sum()
            total = len(df)
            completeness[col] = (non_null / total * 100) if total > 0 else 0
    
    if PLOTLY_AVAILABLE:
        # Create heatmap
        completeness_df = pd.DataFrame({
            "Column": list(completeness.keys()),
            "Completeness": list(completeness.values())
        })
        
        fig = px.bar(
            completeness_df,
            x="Column",
            y="Completeness",
            title="Data Completeness by Column",
            color="Completeness",
            color_continuous_scale="RdYlGn",
            range_y=[0, 100]
        )
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    elif ALTAIR_AVAILABLE:
        completeness_df = pd.DataFrame({
            "column": list(completeness.keys()),
            "completeness": list(completeness.values())
        })
        
        chart = alt.Chart(completeness_df).mark_bar().encode(
            x=alt.X("column", sort="-y"),
            y=alt.Y("completeness", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("completeness", scale=alt.Scale(scheme="redyellowgreen"))
        ).properties(
            title="Data Completeness by Column",
            height=400
        )
        st.altair_chart(chart, use_container_width=True)
    
    else:
        st.bar_chart(pd.DataFrame(completeness, index=[0]).T)


def render_trend_analysis(data: List[Dict[str, Any]], x_field: str, y_field: str, title: str = "Trend Analysis") -> None:
    """
    Render trend analysis chart.
    
    Args:
        data: List of data points
        x_field: Field name for x-axis
        y_field: Field name for y-axis
        title: Chart title
    """
    if not data:
        st.info("No data for trend analysis")
        return
    
    df = pd.DataFrame(data)
    
    if x_field not in df.columns or y_field not in df.columns:
        st.error(f"Fields '{x_field}' or '{y_field}' not found in data")
        return
    
    if PLOTLY_AVAILABLE:
        fig = px.line(
            df,
            x=x_field,
            y=y_field,
            title=title,
            markers=True
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    elif ALTAIR_AVAILABLE:
        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X(x_field, type='temporal' if 'date' in x_field.lower() or 'time' in x_field.lower() else 'ordinal'),
            y=alt.Y(y_field, type='quantitative')
        ).properties(
            title=title,
            height=400
        )
        st.altair_chart(chart, use_container_width=True)
    
    else:
        st.line_chart(df.set_index(x_field)[y_field])


def render_validation_dashboard(validation_results: List[Dict[str, Any]]) -> None:
    """
    Render comprehensive validation dashboard.
    
    Args:
        validation_results: List of validation result dictionaries
    """
    if not validation_results:
        st.info("No validation results to display")
        return
    
    # Summary metrics
    total = len(validation_results)
    passes = len([r for r in validation_results if r.get("status") == "Pass"])
    warnings = len([r for r in validation_results if r.get("status") == "Warning"])
    fails = len([r for r in validation_results if r.get("status") == "Fail"])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Checks", total)
    with col2:
        st.metric("Passed", passes, delta=f"{(passes/total*100):.1f}%")
    with col3:
        st.metric("Warnings", warnings, delta=f"{(warnings/total*100):.1f}%")
    with col4:
        st.metric("Failed", fails, delta=f"{(fails/total*100):.1f}%")
    
    # Charts
    st.markdown("### Validation Results Visualization")
    render_validation_results_chart(validation_results)
    
    # Group by field
    if PLOTLY_AVAILABLE:
        field_results = {}
        for result in validation_results:
            field = result.get("field", "Unknown")
            if field not in field_results:
                field_results[field] = {"Pass": 0, "Warning": 0, "Fail": 0}
            status = result.get("status", "Unknown")
            if status in field_results[field]:
                field_results[field][status] += 1
        
        if field_results:
            df = pd.DataFrame(field_results).T
            fig = px.bar(
                df,
                title="Validation Results by Field",
                barmode='group'
            )
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)


def check_visualization_libraries() -> Dict[str, bool]:
    """
    Check which visualization libraries are available.
    
    Returns:
        Dictionary with library availability
    """
    return {
        "plotly": PLOTLY_AVAILABLE,
        "altair": ALTAIR_AVAILABLE
    }

