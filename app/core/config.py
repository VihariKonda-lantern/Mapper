# --- config.py ---
"""Application configuration and constants."""
from typing import List

# --- Audit & History Settings ---
AUDIT_LOG_MAX_SIZE: int = 100
MAPPING_HISTORY_MAX_SIZE: int = 50

# --- AI & Validation Settings ---
AI_CONFIDENCE_THRESHOLD: int = 80
VALIDATION_PAGE_SIZES: List[int] = [25, 50, 100, 200]
DEFAULT_VALIDATION_PAGE_SIZE: int = 50

# --- File Processing Settings ---
MAX_FILE_SIZE_MB: int = 100  # Maximum file size in MB
SUPPORTED_FILE_FORMATS: List[str] = ['.csv', '.txt', '.tsv', '.xlsx', '.xls', '.json', '.parquet']

# --- UI Settings ---
DEFAULT_PAGE_SIZE: int = 50
MAX_PREVIEW_ROWS: int = 1000

# --- Performance Settings ---
CACHE_TTL_SECONDS: int = 3600  # Cache time-to-live in seconds
LAZY_LOAD_THRESHOLD: int = 1000  # Number of rows before lazy loading kicks in

# --- Data Quality Settings ---
DATA_QUALITY_THRESHOLD: float = 80.0  # Minimum acceptable data quality score
NULL_RATE_THRESHOLD: float = 15.0  # Default null rate threshold for mandatory fields
COMPLETENESS_THRESHOLD: float = 85.0  # Completeness threshold percentage

# --- Session Settings ---
SESSION_TIMEOUT_MINUTES: int = 30  # Session timeout in minutes
ACTIVITY_CHECK_INTERVAL: int = 60  # Activity check interval in seconds

