# --- quality_trends.py ---
"""Data quality trends tracking over time."""
import streamlit as st
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path

st: Any = st


@dataclass
class QualityTrendEntry:
    """Single quality trend entry."""
    timestamp: datetime
    quality_id: str
    overall_score: float
    completeness: float
    uniqueness: float
    consistency: float
    validity: float
    timeliness: float
    record_count: int
    data_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "quality_id": self.quality_id,
            "overall_score": self.overall_score,
            "completeness": self.completeness,
            "uniqueness": self.uniqueness,
            "consistency": self.consistency,
            "validity": self.validity,
            "timeliness": self.timeliness,
            "record_count": self.record_count,
            "data_hash": self.data_hash,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QualityTrendEntry":
        """Create from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            quality_id=data["quality_id"],
            overall_score=data["overall_score"],
            completeness=data.get("completeness", 0),
            uniqueness=data.get("uniqueness", 0),
            consistency=data.get("consistency", 0),
            validity=data.get("validity", 0),
            timeliness=data.get("timeliness", 0),
            record_count=data["record_count"],
            data_hash=data["data_hash"],
            metadata=data.get("metadata", {})
        )


class QualityTrendsTracker:
    """Track data quality trends over time."""
    
    def __init__(self, max_entries: int = 100):
        self.max_entries = max_entries
        self.history_key = "quality_trends_history"
    
    def add_quality_score(
        self,
        quality_score: Dict[str, Any],
        record_count: int,
        data_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a quality score to trends.
        
        Args:
            quality_score: Quality score dictionary from calculate_data_quality_score
            record_count: Number of records analyzed
            data_hash: Hash of the data being analyzed
            metadata: Optional additional metadata
        
        Returns:
            Quality ID
        """
        if self.history_key not in st.session_state:
            st.session_state[self.history_key] = []
        
        breakdown = quality_score.get("breakdown", {})
        
        quality_id = f"quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        entry = QualityTrendEntry(
            timestamp=datetime.now(),
            quality_id=quality_id,
            overall_score=quality_score.get("overall_score", 0),
            completeness=breakdown.get("completeness", 0),
            uniqueness=breakdown.get("uniqueness", 0),
            consistency=breakdown.get("consistency", 0),
            validity=breakdown.get("validity", 0),
            timeliness=breakdown.get("timeliness", 0),
            record_count=record_count,
            data_hash=data_hash,
            metadata=metadata or {}
        )
        
        history = st.session_state[self.history_key]
        history.append(entry.to_dict())
        
        # Keep only the latest entries
        if len(history) > self.max_entries:
            history = history[-self.max_entries:]
        
        st.session_state[self.history_key] = history
        
        return quality_id
    
    def get_trends(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get quality trends.
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of quality trend entries
        """
        if self.history_key not in st.session_state:
            return []
        
        history = st.session_state[self.history_key]
        if limit:
            return history[-limit:]
        return history
    
    def get_trend_analysis(self) -> Dict[str, Any]:
        """Get quality trend analysis.
        
        Returns:
            Dictionary with trend analysis data
        """
        history = self.get_trends()
        if not history:
            return {
                "available": False,
                "message": "No quality history available"
            }
        
        # Convert to entries
        entries = [QualityTrendEntry.from_dict(h) for h in history]
        
        # Calculate trends
        if len(entries) > 1:
            recent = entries[-1]
            previous = entries[-2] if len(entries) > 1 else entries[0]
            
            overall_change = recent.overall_score - previous.overall_score
            completeness_change = recent.completeness - previous.completeness
            uniqueness_change = recent.uniqueness - previous.uniqueness
        else:
            overall_change = 0
            completeness_change = 0
            uniqueness_change = 0
        
        # Calculate averages
        avg_overall = sum(e.overall_score for e in entries) / len(entries)
        avg_completeness = sum(e.completeness for e in entries) / len(entries)
        avg_uniqueness = sum(e.uniqueness for e in entries) / len(entries)
        avg_consistency = sum(e.consistency for e in entries) / len(entries)
        
        return {
            "available": True,
            "total_analyses": len(entries),
            "avg_overall_score": round(avg_overall, 2),
            "avg_completeness": round(avg_completeness, 2),
            "avg_uniqueness": round(avg_uniqueness, 2),
            "avg_consistency": round(avg_consistency, 2),
            "overall_change": round(overall_change, 2),
            "completeness_change": round(completeness_change, 2),
            "uniqueness_change": round(uniqueness_change, 2),
            "recent_entry": entries[-1].to_dict() if entries else None,
            "entries": [e.to_dict() for e in entries]
        }
    
    def clear_history(self) -> None:
        """Clear quality trends history."""
        if self.history_key in st.session_state:
            st.session_state[self.history_key] = []
    
    def export_history(self, file_path: Optional[str] = None) -> str:
        """Export quality trends to JSON file.
        
        Args:
            file_path: Optional file path (defaults to timestamped file)
        
        Returns:
            Path to exported file
        """
        history = self.get_trends()
        
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"quality_trends_{timestamp}.json"
        
        export_path = Path(file_path)
        with open(export_path, 'w') as f:
            json.dump(history, f, indent=2, default=str)
        
        return str(export_path)


# Global instance
quality_trends = QualityTrendsTracker()

