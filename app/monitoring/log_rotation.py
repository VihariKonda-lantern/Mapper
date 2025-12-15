"""Log rotation utilities."""
from typing import Optional
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime


class LogRotator:
    """Manages log rotation for application logs."""
    
    @staticmethod
    def setup_rotating_file_handler(
        log_file: Path,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        level: int = logging.INFO
    ) -> RotatingFileHandler:
        """
        Setup rotating file handler based on file size.
        
        Args:
            log_file: Path to log file
            max_bytes: Maximum file size before rotation
            backup_count: Number of backup files to keep
            level: Logging level
        
        Returns:
            RotatingFileHandler
        """
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = RotatingFileHandler(
            str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        handler.setLevel(level)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        return handler
    
    @staticmethod
    def setup_timed_rotating_handler(
        log_file: Path,
        when: str = 'midnight',
        interval: int = 1,
        backup_count: int = 30,
        level: int = logging.INFO
    ) -> TimedRotatingFileHandler:
        """
        Setup time-based rotating file handler.
        
        Args:
            log_file: Path to log file
            when: When to rotate ('S', 'M', 'H', 'D', 'midnight')
            interval: Interval for rotation
            backup_count: Number of backup files to keep
            level: Logging level
        
        Returns:
            TimedRotatingFileHandler
        """
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = TimedRotatingFileHandler(
            str(log_file),
            when=when,
            interval=interval,
            backupCount=backup_count
        )
        handler.setLevel(level)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        return handler
    
    @staticmethod
    def cleanup_old_logs(
        log_dir: Path,
        pattern: str = "*.log.*",
        max_age_days: int = 30
    ) -> int:
        """
        Clean up old log files.
        
        Args:
            log_dir: Directory containing logs
            pattern: File pattern to match
            max_age_days: Maximum age in days
        
        Returns:
            Number of files deleted
        """
        if not log_dir.exists():
            return 0
        
        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        
        for log_file in log_dir.glob(pattern):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    deleted_count += 1
                except Exception:
                    pass
        
        return deleted_count

