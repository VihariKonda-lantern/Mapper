# --- data_quality_config.py ---
"""Configurable data quality thresholds and settings."""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from core.config import (
    DATA_QUALITY_THRESHOLD,
    COMPLETENESS_THRESHOLD,
    UNIQUENESS_THRESHOLD,
    CONSISTENCY_THRESHOLD,
    VALIDITY_THRESHOLD,
    TIMELINESS_THRESHOLD
)


@dataclass
class QualityThresholds:
    """Configurable quality thresholds."""
    overall: float = DATA_QUALITY_THRESHOLD
    completeness: float = COMPLETENESS_THRESHOLD
    uniqueness: float = UNIQUENESS_THRESHOLD
    consistency: float = CONSISTENCY_THRESHOLD
    validity: float = VALIDITY_THRESHOLD
    timeliness: float = TIMELINESS_THRESHOLD
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "overall": self.overall,
            "completeness": self.completeness,
            "uniqueness": self.uniqueness,
            "consistency": self.consistency,
            "validity": self.validity,
            "timeliness": self.timeliness
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "QualityThresholds":
        """Create from dictionary."""
        return cls(**data)


class QualityThresholdManager:
    """Manager for quality thresholds with alerting."""
    
    def __init__(self, thresholds: Optional[QualityThresholds] = None):
        self.thresholds = thresholds or QualityThresholds()
        self.alert_history: list[Dict[str, Any]] = []
    
    def check_threshold(
        self,
        metric_name: str,
        value: float,
        raise_alert: bool = True
    ) -> tuple[bool, Optional[str]]:
        """
        Check if value meets threshold.
        
        Args:
            metric_name: Name of the quality metric
            value: Current value
            raise_alert: Whether to raise an alert if threshold not met
        
        Returns:
            Tuple of (meets_threshold, alert_message)
        """
        threshold = getattr(self.thresholds, metric_name, self.thresholds.overall)
        meets_threshold = value >= threshold
        
        if not meets_threshold and raise_alert:
            alert_msg = (
                f"Quality metric '{metric_name}' ({value:.2%}) "
                f"is below threshold ({threshold:.2%})"
            )
            self.alert_history.append({
                "metric": metric_name,
                "value": value,
                "threshold": threshold,
                "timestamp": str(__import__("datetime").datetime.now())
            })
            return False, alert_msg
        
        return meets_threshold, None
    
    def check_all_thresholds(self, quality_scores: Dict[str, float]) -> Dict[str, tuple[bool, Optional[str]]]:
        """
        Check all quality thresholds.
        
        Args:
            quality_scores: Dictionary of quality metric scores
        
        Returns:
            Dictionary mapping metric names to (meets_threshold, alert_message)
        """
        results = {}
        for metric, value in quality_scores.items():
            results[metric] = self.check_threshold(metric, value)
        return results
    
    def get_alerts(self) -> list[Dict[str, Any]]:
        """Get recent alerts."""
        return self.alert_history[-10:]  # Last 10 alerts
    
    def clear_alerts(self) -> None:
        """Clear alert history."""
        self.alert_history.clear()
    
    def update_thresholds(self, thresholds: QualityThresholds) -> None:
        """Update quality thresholds."""
        self.thresholds = thresholds


# Global threshold manager instance
quality_threshold_manager = QualityThresholdManager()

