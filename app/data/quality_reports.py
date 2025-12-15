# --- quality_reports.py ---
"""Generate detailed data quality reports."""
import streamlit as st
from typing import Any, Dict, List, Optional
from datetime import datetime
import pandas as pd
from pathlib import Path
import json

st: Any = st


class QualityReportGenerator:
    """Generate detailed data quality reports."""
    
    @staticmethod
    def generate_report(
        quality_score: Dict[str, Any],
        claims_df: pd.DataFrame,
        column_stats: Optional[Dict[str, Dict[str, Any]]] = None,
        duplicates: Optional[pd.DataFrame] = None,
        outliers: Optional[pd.DataFrame] = None,
        completeness_matrix: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive quality report.
        
        Args:
            quality_score: Quality score dictionary
            claims_df: Claims DataFrame
            column_stats: Optional column statistics
            duplicates: Optional duplicate records
            outliers: Optional outlier records
            completeness_matrix: Optional completeness matrix
        
        Returns:
            Dictionary with report data
        """
        breakdown = quality_score.get("breakdown", {})
        
        report = {
            "report_id": f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "overall_score": quality_score.get("overall_score", 0),
                "record_count": len(claims_df),
                "column_count": len(claims_df.columns),
                "completeness": breakdown.get("completeness", 0),
                "uniqueness": breakdown.get("uniqueness", 0),
                "consistency": breakdown.get("consistency", 0),
                "validity": breakdown.get("validity", 0),
                "timeliness": breakdown.get("timeliness", 0)
            },
            "details": {
                "column_statistics": column_stats or {},
                "duplicate_count": len(duplicates) if duplicates is not None and not duplicates.empty else 0,
                "outlier_count": len(outliers) if outliers is not None and not outliers.empty else 0,
                "completeness_matrix_available": completeness_matrix is not None and not completeness_matrix.empty
            },
            "recommendations": []
        }
        
        # Generate recommendations
        if breakdown.get("completeness", 100) < 85:
            report["recommendations"].append({
                "priority": "high",
                "category": "completeness",
                "message": "Data completeness is below 85%. Review missing data patterns.",
                "action": "Check completeness matrix for fields with high null rates"
            })
        
        if breakdown.get("uniqueness", 100) < 90:
            report["recommendations"].append({
                "priority": "medium",
                "category": "uniqueness",
                "message": "Data uniqueness is below 90%. Duplicate records detected.",
                "action": "Review duplicate detection results"
            })
        
        if breakdown.get("consistency", 100) < 80:
            report["recommendations"].append({
                "priority": "high",
                "category": "consistency",
                "message": "Data consistency is below 80%. Data format issues detected.",
                "action": "Review validation results for format inconsistencies"
            })
        
        if quality_score.get("overall_score", 0) < 75:
            report["recommendations"].append({
                "priority": "critical",
                "category": "overall",
                "message": "Overall quality score is below 75%. Data quality needs improvement.",
                "action": "Review all quality metrics and address issues systematically"
            })
        
        return report
    
    @staticmethod
    def render_report(report: Dict[str, Any]) -> None:
        """Render quality report in Streamlit.
        
        Args:
            report: Report dictionary from generate_report
        """
        st.markdown("## 📋 Data Quality Report")
        
        # Summary section
        st.markdown("### Summary")
        summary = report.get("summary", {})
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Overall Score", f"{summary.get('overall_score', 0):.1f}/100")
        with col2:
            st.metric("Records", f"{summary.get('record_count', 0):,}")
        with col3:
            st.metric("Columns", summary.get("column_count", 0))
        with col4:
            st.metric("Completeness", f"{summary.get('completeness', 0):.1f}%")
        
        # Quality breakdown
        st.markdown("### Quality Breakdown")
        breakdown_data = {
            "Metric": ["Completeness", "Uniqueness", "Consistency", "Validity", "Timeliness"],
            "Score": [
                summary.get("completeness", 0),
                summary.get("uniqueness", 0),
                summary.get("consistency", 0),
                summary.get("validity", 0),
                summary.get("timeliness", 0)
            ]
        }
        breakdown_df = pd.DataFrame(breakdown_data)
        st.dataframe(breakdown_df, use_container_width=True)
        
        # Recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            st.markdown("### Recommendations")
            for rec in recommendations:
                priority_icon = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(rec.get("priority", "medium"), "🟡")
                
                st.markdown(f"""
                {priority_icon} **{rec.get('category', 'General').title()}** - {rec.get('priority', 'medium').upper()}
                
                {rec.get('message', '')}
                
                💡 **Action:** {rec.get('action', 'Review data quality metrics')}
                """)
        
        # Details section
        details = report.get("details", {})
        if details:
            st.markdown("### Additional Details")
            with st.expander("View Details", expanded=False):
                st.json(details)
    
    @staticmethod
    def export_report(report: Dict[str, Any], format: str = "json") -> bytes:
        """Export quality report to file.
        
        Args:
            report: Report dictionary
            format: Export format ("json", "csv")
        
        Returns:
            File content as bytes
        """
        if format == "json":
            return json.dumps(report, indent=2, default=str).encode('utf-8')
        elif format == "csv":
            # Export summary as CSV
            summary = report.get("summary", {})
            df = pd.DataFrame([summary])
            return df.to_csv(index=False).encode('utf-8')
        else:
            raise ValueError(f"Unsupported format: {format}")


# Global instance
quality_report_generator = QualityReportGenerator()

