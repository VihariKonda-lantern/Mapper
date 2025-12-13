# --- batch_scheduler.py ---
"""Batch job scheduling and monitoring."""
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from exceptions import ProcessingError


class JobStatus(Enum):
    """Batch job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchJob:
    """Represents a batch processing job."""
    job_id: str
    job_name: str
    job_type: str
    config: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "job_id": self.job_id,
            "job_name": self.job_name,
            "job_type": self.job_type,
            "config": self.config,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }


@dataclass
class Schedule:
    """Schedule for batch jobs."""
    schedule_id: str
    job_config: Dict[str, Any]
    schedule_type: str  # "once", "daily", "weekly", "monthly", "cron"
    schedule_value: str  # Time, day, or cron expression
    enabled: bool = True
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    
    def calculate_next_run(self) -> Optional[datetime]:
        """Calculate next run time based on schedule."""
        now = datetime.now()
        
        if self.schedule_type == "once":
            if self.next_run and self.next_run > now:
                return self.next_run
            return None
        
        elif self.schedule_type == "daily":
            # Parse time (e.g., "14:30")
            try:
                hour, minute = map(int, self.schedule_value.split(":"))
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                return next_run
            except Exception:
                return None
        
        elif self.schedule_type == "weekly":
            # schedule_value is day of week (0-6, Monday=0)
            try:
                target_day = int(self.schedule_value)
                days_ahead = target_day - now.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                next_run = now + timedelta(days=days_ahead)
                return next_run.replace(hour=0, minute=0, second=0, microsecond=0)
            except Exception:
                return None
        
        # Add more schedule types as needed
        return None


class BatchScheduler:
    """Scheduler for batch jobs."""
    
    def __init__(self):
        self.jobs: Dict[str, BatchJob] = {}
        self.schedules: Dict[str, Schedule] = {}
        self.job_templates: Dict[str, Dict[str, Any]] = {}
    
    def create_job(
        self,
        job_name: str,
        job_type: str,
        config: Dict[str, Any],
        max_retries: int = 3
    ) -> BatchJob:
        """
        Create a new batch job.
        
        Args:
            job_name: Name of the job
            job_type: Type of job
            config: Job configuration
            max_retries: Maximum retry attempts
        
        Returns:
            Created BatchJob
        """
        job_id = f"job_{len(self.jobs) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        job = BatchJob(
            job_id=job_id,
            job_name=job_name,
            job_type=job_type,
            config=config,
            max_retries=max_retries
        )
        self.jobs[job_id] = job
        return job
    
    def schedule_job(
        self,
        job_config: Dict[str, Any],
        schedule_type: str,
        schedule_value: str
    ) -> Schedule:
        """
        Schedule a batch job.
        
        Args:
            job_config: Job configuration
            schedule_type: Type of schedule ("once", "daily", "weekly", "monthly", "cron")
            schedule_value: Schedule value (time, day, or cron expression)
        
        Returns:
            Created Schedule
        """
        schedule_id = f"schedule_{len(self.schedules) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        schedule = Schedule(
            schedule_id=schedule_id,
            job_config=job_config,
            schedule_type=schedule_type,
            schedule_value=schedule_value
        )
        schedule.next_run = schedule.calculate_next_run()
        self.schedules[schedule_id] = schedule
        return schedule
    
    def get_jobs(
        self,
        status: Optional[JobStatus] = None,
        job_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get jobs with optional filtering."""
        jobs = list(self.jobs.values())
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        if job_type:
            jobs = [j for j in jobs if j.job_type == job_type]
        
        return [j.to_dict() for j in jobs]
    
    def get_job(self, job_id: str) -> Optional[BatchJob]:
        """Get a specific job."""
        return self.jobs.get(job_id)
    
    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: Optional[float] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> None:
        """Update job status."""
        job = self.jobs.get(job_id)
        if not job:
            return
        
        job.status = status
        
        if status == JobStatus.RUNNING and not job.started_at:
            job.started_at = datetime.now()
        
        if status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            job.completed_at = datetime.now()
        
        if progress is not None:
            job.progress = progress
        
        if result is not None:
            job.result = result
        
        if error is not None:
            job.error = error
    
    def retry_job(self, job_id: str) -> bool:
        """Retry a failed job."""
        job = self.jobs.get(job_id)
        if not job or job.status != JobStatus.FAILED:
            return False
        
        if job.retry_count >= job.max_retries:
            return False
        
        job.retry_count += 1
        job.status = JobStatus.PENDING
        job.error = None
        job.progress = 0.0
        return True
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get jobs that are due to run."""
        now = datetime.now()
        due_jobs = []
        
        for schedule in self.schedules.values():
            if not schedule.enabled:
                continue
            
            if schedule.next_run and schedule.next_run <= now:
                due_jobs.append({
                    "schedule_id": schedule.schedule_id,
                    "job_config": schedule.job_config,
                    "next_run": schedule.next_run.isoformat()
                })
        
        return due_jobs
    
    def save_template(
        self,
        template_name: str,
        job_config: Dict[str, Any]
    ) -> None:
        """Save a batch processing template."""
        self.job_templates[template_name] = job_config.copy()
    
    def load_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Load a batch processing template."""
        return self.job_templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        """List all templates."""
        return list(self.job_templates.keys())
    
    def generate_report(self, job_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate batch processing report.
        
        Args:
            job_id: Specific job ID, or None for summary
        
        Returns:
            Report dictionary
        """
        if job_id:
            job = self.get_job(job_id)
            if not job:
                return {"error": "Job not found"}
            
            return {
                "job_id": job.job_id,
                "job_name": job.job_name,
                "status": job.status.value,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "duration": (
                    (job.completed_at - job.started_at).total_seconds()
                    if job.started_at and job.completed_at
                    else None
                ),
                "progress": job.progress,
                "result": job.result,
                "error": job.error,
                "retry_count": job.retry_count
            }
        else:
            # Summary report
            total_jobs = len(self.jobs)
            completed = len([j for j in self.jobs.values() if j.status == JobStatus.COMPLETED])
            failed = len([j for j in self.jobs.values() if j.status == JobStatus.FAILED])
            running = len([j for j in self.jobs.values() if j.status == JobStatus.RUNNING])
            pending = len([j for j in self.jobs.values() if j.status == JobStatus.PENDING])
            
            return {
                "total_jobs": total_jobs,
                "completed": completed,
                "failed": failed,
                "running": running,
                "pending": pending,
                "success_rate": (completed / total_jobs * 100) if total_jobs > 0 else 0.0
            }


# Global scheduler instance
batch_scheduler = BatchScheduler()

