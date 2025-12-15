# --- validation_history.py ---
"""Validation history tracking over time."""
import streamlit as st
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path

st: Any = st


@dataclass
class ValidationHistoryEntry:
    """Single validation history entry."""
    timestamp: datetime
    validation_id: str
    total_checks: int
    passes: int
    warnings: int
    fails: int
    execution_time: float
    record_count: int
    data_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "validation_id": self.validation_id,
            "total_checks": self.total_checks,
            "passes": self.passes,
            "warnings": self.warnings,
            "fails": self.fails,
            "execution_time": self.execution_time,
            "record_count": self.record_count,
            "data_hash": self.data_hash,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationHistoryEntry":
        """Create from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            validation_id=data["validation_id"],
            total_checks=data["total_checks"],
            passes=data["passes"],
            warnings=data["warnings"],
            fails=data["fails"],
            execution_time=data["execution_time"],
            record_count=data["record_count"],
            data_hash=data["data_hash"],
            metadata=data.get("metadata", {})
        )


class ValidationHistoryTracker:
    """Track validation history over time."""
    
    def __init__(self, max_entries: int = 100):
        self.max_entries = max_entries
        self.history_key = "validation_history"
    
    def add_validation_result(
        self,
        validation_results: List[Dict[str, Any]],
        execution_time: float,
        record_count: int,
        data_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a validation result to history.
        
        Args:
            validation_results: List of validation result dictionaries
            execution_time: Time taken to run validation
            record_count: Number of records validated
            data_hash: Hash of the data being validated
            metadata: Optional additional metadata
        
        Returns:
            Validation ID
        """
        if self.history_key not in st.session_state:
            st.session_state[self.history_key] = []
        
        # Calculate summary
        passes = len([r for r in validation_results if r.get("status") == "Pass"])
        warnings = len([r for r in validation_results if r.get("status") == "Warning"])
        fails = len([r for r in validation_results if r.get("status") == "Fail"])
        
        validation_id = f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        entry = ValidationHistoryEntry(
            timestamp=datetime.now(),
            validation_id=validation_id,
            total_checks=len(validation_results),
            passes=passes,
            warnings=warnings,
            fails=fails,
            execution_time=execution_time,
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
        
        return validation_id
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get validation history.
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of validation history entries
        """
        if self.history_key not in st.session_state:
            return []
        
        history = st.session_state[self.history_key]
        if limit:
            return history[-limit:]
        return history
    
    def get_trends(self) -> Dict[str, Any]:
        """Get validation trends over time.
        
        Returns:
            Dictionary with trend data
        """
        history = self.get_history()
        if not history:
            return {
                "available": False,
                "message": "No validation history available"
            }
        
        # Convert to entries
        entries = [ValidationHistoryEntry.from_dict(h) for h in history]
        
        # Calculate trends
        if len(entries) > 1:
            recent = entries[-1]
            previous = entries[-2] if len(entries) > 1 else entries[0]
            
            pass_rate_change = (
                (recent.passes / recent.total_checks * 100) - 
                (previous.passes / previous.total_checks * 100)
                if recent.total_checks > 0 and previous.total_checks > 0 else 0
            )
            
            fail_rate_change = (
                (recent.fails / recent.total_checks * 100) - 
                (previous.fails / previous.total_checks * 100)
                if recent.total_checks > 0 and previous.total_checks > 0 else 0
            )
        else:
            pass_rate_change = 0
            fail_rate_change = 0
        
        # Calculate averages
        avg_pass_rate = sum(
            e.passes / e.total_checks * 100 if e.total_checks > 0 else 0
            for e in entries
        ) / len(entries)
        
        avg_fail_rate = sum(
            e.fails / e.total_checks * 100 if e.total_checks > 0 else 0
            for e in entries
        ) / len(entries)
        
        avg_execution_time = sum(e.execution_time for e in entries) / len(entries)
        
        return {
            "available": True,
            "total_validations": len(entries),
            "avg_pass_rate": round(avg_pass_rate, 2),
            "avg_fail_rate": round(avg_fail_rate, 2),
            "avg_execution_time": round(avg_execution_time, 2),
            "pass_rate_change": round(pass_rate_change, 2),
            "fail_rate_change": round(fail_rate_change, 2),
            "recent_entry": entries[-1].to_dict() if entries else None,
            "entries": [e.to_dict() for e in entries]
        }
    
    def clear_history(self) -> None:
        """Clear validation history."""
        if self.history_key in st.session_state:
            st.session_state[self.history_key] = []
    
    def export_history(self, file_path: Optional[str] = None) -> str:
        """Export validation history to JSON file.
        
        Args:
            file_path: Optional file path (defaults to timestamped file)
        
        Returns:
            Path to exported file
        """
        history = self.get_history()
        
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"validation_history_{timestamp}.json"
        
        export_path = Path(file_path)
        with open(export_path, 'w') as f:
            json.dump(history, f, indent=2, default=str)
        
        return str(export_path)


class ValidationScheduler:
    """Schedule validations to run automatically."""
    
    def __init__(self):
        self.schedules_key = "validation_schedules"
    
    def schedule_validation(
        self,
        validation_id: str,
        schedule_type: str,  # "on_file_upload", "daily", "weekly", "on_data_change"
        schedule_value: Optional[str] = None,  # Time for daily, day for weekly
        validation_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Schedule a validation to run automatically.
        
        Args:
            validation_id: Unique validation identifier
            schedule_type: Type of schedule
            schedule_value: Optional schedule value (time, day, etc.)
            validation_config: Validation configuration
        
        Returns:
            Schedule dictionary
        """
        if self.schedules_key not in st.session_state:
            st.session_state[self.schedules_key] = {}
        
        schedule = {
            "id": validation_id,
            "schedule_type": schedule_type,
            "schedule_value": schedule_value,
            "validation_config": validation_config or {},
            "created_at": datetime.now().isoformat(),
            "last_run": None,
            "next_run": None,
            "enabled": True,
            "run_count": 0
        }
        
        # Calculate next run time
        if schedule_type == "daily" and schedule_value:
            try:
                hour, minute = map(int, schedule_value.split(":"))
                now = datetime.now()
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    from datetime import timedelta
                    next_run += timedelta(days=1)
                schedule["next_run"] = next_run.isoformat()
            except Exception:
                pass
        
        st.session_state[self.schedules_key][validation_id] = schedule
        return schedule
    
    def get_schedules(self) -> Dict[str, Dict[str, Any]]:
        """Get all validation schedules."""
        if self.schedules_key not in st.session_state:
            return {}
        return st.session_state[self.schedules_key].copy()
    
    def get_schedule(self, validation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific schedule."""
        schedules = self.get_schedules()
        return schedules.get(validation_id)
    
    def enable_schedule(self, validation_id: str) -> bool:
        """Enable a schedule."""
        schedule = self.get_schedule(validation_id)
        if schedule:
            schedule["enabled"] = True
            st.session_state[self.schedules_key][validation_id] = schedule
            return True
        return False
    
    def disable_schedule(self, validation_id: str) -> bool:
        """Disable a schedule."""
        schedule = self.get_schedule(validation_id)
        if schedule:
            schedule["enabled"] = False
            st.session_state[self.schedules_key][validation_id] = schedule
            return True
        return False
    
    def delete_schedule(self, validation_id: str) -> bool:
        """Delete a schedule."""
        if self.schedules_key in st.session_state:
            if validation_id in st.session_state[self.schedules_key]:
                del st.session_state[self.schedules_key][validation_id]
                return True
        return False
    
    def check_and_run_schedules(self, trigger: str = "manual") -> List[Dict[str, Any]]:
        """Check schedules and run validations if needed.
        
        Args:
            trigger: Trigger type ("manual", "file_upload", "data_change", "time_based")
        
        Returns:
            List of validation results that were run
        """
        schedules = self.get_schedules()
        results = []
        
        for validation_id, schedule in schedules.items():
            if not schedule.get("enabled", False):
                continue
            
            schedule_type = schedule.get("schedule_type")
            should_run = False
            
            if trigger == "file_upload" and schedule_type == "on_file_upload":
                should_run = True
            elif trigger == "data_change" and schedule_type == "on_data_change":
                should_run = True
            elif trigger == "time_based":
                if schedule_type == "daily":
                    # Check if it's time to run
                    next_run_str = schedule.get("next_run")
                    if next_run_str:
                        try:
                            next_run = datetime.fromisoformat(next_run_str)
                            if datetime.now() >= next_run:
                                should_run = True
                        except Exception:
                            pass
            
            if should_run:
                # Run validation
                validation_config = schedule.get("validation_config", {})
                try:
                    # This would trigger the actual validation
                    # For now, we'll just mark it as run
                    schedule["last_run"] = datetime.now().isoformat()
                    schedule["run_count"] = schedule.get("run_count", 0) + 1
                    
                    # Calculate next run
                    if schedule_type == "daily" and schedule.get("schedule_value"):
                        try:
                            hour, minute = map(int, schedule["schedule_value"].split(":"))
                            now = datetime.now()
                            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                            from datetime import timedelta
                            if next_run <= now:
                                next_run += timedelta(days=1)
                            schedule["next_run"] = next_run.isoformat()
                        except Exception:
                            pass
                    
                    st.session_state[self.schedules_key][validation_id] = schedule
                    results.append({
                        "validation_id": validation_id,
                        "status": "run",
                        "timestamp": schedule["last_run"]
                    })
                except Exception as e:
                    results.append({
                        "validation_id": validation_id,
                        "status": "error",
                        "error": str(e)
                    })
        
        return results


class ValidationComparator:
    """Compare validation results between different runs or files."""
    
    def compare_results(
        self,
        results1: List[Dict[str, Any]],
        results2: List[Dict[str, Any]],
        comparison_type: str = "full"  # "full", "summary", "by_check"
    ) -> Dict[str, Any]:
        """Compare two validation result sets.
        
        Args:
            results1: First validation results
            results2: Second validation results
            comparison_type: Type of comparison
        
        Returns:
            Comparison results
        """
        # Create lookup dictionaries
        results1_dict = {r.get("check", ""): r for r in results1}
        results2_dict = {r.get("check", ""): r for r in results2}
        
        all_checks = set(results1_dict.keys()) | set(results2_dict.keys())
        
        comparison = {
            "comparison_type": comparison_type,
            "results1_count": len(results1),
            "results2_count": len(results2),
            "common_checks": [],
            "only_in_results1": [],
            "only_in_results2": [],
            "status_changes": [],
            "improvements": [],
            "regressions": []
        }
        
        for check in all_checks:
            r1 = results1_dict.get(check)
            r2 = results2_dict.get(check)
            
            if r1 and r2:
                # Both have this check
                comparison["common_checks"].append(check)
                
                status1 = r1.get("status", "Unknown")
                status2 = r2.get("status", "Unknown")
                
                if status1 != status2:
                    comparison["status_changes"].append({
                        "check": check,
                        "status1": status1,
                        "status2": status2,
                        "field": r1.get("field")
                    })
                    
                    # Determine if improvement or regression
                    status_order = {"Pass": 0, "Warning": 1, "Fail": 2, "Error": 3}
                    order1 = status_order.get(status1, 99)
                    order2 = status_order.get(status2, 99)
                    
                    if order2 < order1:
                        comparison["improvements"].append({
                            "check": check,
                            "from": status1,
                            "to": status2,
                            "field": r1.get("field")
                        })
                    elif order2 > order1:
                        comparison["regressions"].append({
                            "check": check,
                            "from": status1,
                            "to": status2,
                            "field": r1.get("field")
                        })
                
                # Compare fail counts
                fail_count1 = r1.get("fail_count", 0)
                fail_count2 = r2.get("fail_count", 0)
                if fail_count1 != fail_count2:
                    comparison["status_changes"].append({
                        "check": check,
                        "type": "fail_count_change",
                        "fail_count1": fail_count1,
                        "fail_count2": fail_count2,
                        "field": r1.get("field")
                    })
            
            elif r1:
                comparison["only_in_results1"].append({
                    "check": check,
                    "status": r1.get("status"),
                    "field": r1.get("field")
                })
            elif r2:
                comparison["only_in_results2"].append({
                    "check": check,
                    "status": r2.get("status"),
                    "field": r2.get("field")
                })
        
        # Calculate summary statistics
        comparison["summary"] = {
            "total_checks": len(all_checks),
            "common_checks_count": len(comparison["common_checks"]),
            "status_changes_count": len(comparison["status_changes"]),
            "improvements_count": len(comparison["improvements"]),
            "regressions_count": len(comparison["regressions"]),
            "new_checks": len(comparison["only_in_results2"]),
            "removed_checks": len(comparison["only_in_results1"])
        }
        
        return comparison
    
    def compare_history_entries(
        self,
        entry_id1: str,
        entry_id2: str
    ) -> Dict[str, Any]:
        """Compare two validation history entries.
        
        Args:
            entry_id1: First validation history entry ID
            entry_id2: Second validation history entry ID
        
        Returns:
            Comparison results
        """
        tracker = ValidationHistoryTracker()
        history = tracker.get_history()
        
        entry1 = next((e for e in history if e.get("validation_id") == entry_id1), None)
        entry2 = next((e for e in history if e.get("validation_id") == entry_id2), None)
        
        if not entry1 or not entry2:
            return {
                "error": "One or both entries not found",
                "entry1_found": entry1 is not None,
                "entry2_found": entry2 is not None
            }
        
        # Get full validation results from metadata if available
        results1 = entry1.get("metadata", {}).get("validation_results", [])
        results2 = entry2.get("metadata", {}).get("validation_results", [])
        
        if not results1 or not results2:
            # Fallback to entry-level comparison
            return {
                "comparison_type": "summary",
                "entry1": {
                    "validation_id": entry_id1,
                    "timestamp": entry1.get("timestamp"),
                    "passes": entry1.get("passes", 0),
                    "warnings": entry1.get("warnings", 0),
                    "fails": entry1.get("fails", 0)
                },
                "entry2": {
                    "validation_id": entry_id2,
                    "timestamp": entry2.get("timestamp"),
                    "passes": entry2.get("passes", 0),
                    "warnings": entry2.get("warnings", 0),
                    "fails": entry2.get("fails", 0)
                },
                "differences": {
                    "pass_change": entry2.get("passes", 0) - entry1.get("passes", 0),
                    "warning_change": entry2.get("warnings", 0) - entry1.get("warnings", 0),
                    "fail_change": entry2.get("fails", 0) - entry1.get("fails", 0)
                }
            }
        
        return self.compare_results(results1, results2)


# Global instances
validation_history = ValidationHistoryTracker()
validation_scheduler = ValidationScheduler()
validation_comparator = ValidationComparator()

