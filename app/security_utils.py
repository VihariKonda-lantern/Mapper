# --- security_utils.py ---
"""Security utilities for input sanitization, validation, and rate limiting."""
from typing import Any, Optional
import re
import html
from datetime import datetime, timedelta
import time
from exceptions import ClaimsMapperError


class InputSanitizer:
    """Utility class for input sanitization."""
    
    # Dangerous patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"<iframe[^>]*>.*?</iframe>",
        r"javascript:",
        r"on\w+\s*=",
    ]
    
    @staticmethod
    def sanitize_text(
        text: str,
        max_length: int = 1000,
        allow_html: bool = False,
        strip_whitespace: bool = True
    ) -> str:
        """
        Sanitize text input.
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            allow_html: Whether to allow HTML (if False, escapes HTML)
            strip_whitespace: Whether to strip leading/trailing whitespace
        
        Returns:
            Sanitized text
        """
        if not isinstance(text, str):
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
        
        # Escape HTML if not allowed
        if not allow_html:
            text = html.escape(text)
        
        # Strip whitespace if requested
        if strip_whitespace:
            text = text.strip()
        
        return text
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other issues.
        
        Args:
            filename: Original filename
        
        Returns:
            Sanitized filename
        """
        if not isinstance(filename, str):
            return "file"
        
        # Remove path components
        filename = filename.replace("..", "").replace("/", "_").replace("\\", "_")
        
        # Remove dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Ensure it's not empty
        if not filename:
            filename = "file"
        
        return filename
    
    @staticmethod
    def check_sql_injection(text: str) -> bool:
        """
        Check for SQL injection patterns.
        
        Args:
            text: Text to check
        
        Returns:
            True if SQL injection pattern detected
        """
        text_upper = text.upper()
        for pattern in InputSanitizer.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_upper, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def check_xss(text: str) -> bool:
        """
        Check for XSS patterns.
        
        Args:
            text: Text to check
        
        Returns:
            True if XSS pattern detected
        """
        for pattern in InputSanitizer.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def validate_and_sanitize(
        text: str,
        max_length: int = 1000,
        check_sql: bool = True,
        check_xss: bool = True
    ) -> tuple[str, Optional[str]]:
        """
        Validate and sanitize text input.
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            check_sql: Whether to check for SQL injection
            check_xss: Whether to check for XSS
        
        Returns:
            Tuple of (sanitized_text, error_message)
        """
        if check_sql and InputSanitizer.check_sql_injection(text):
            return "", "Potential SQL injection detected"
        
        if check_xss and InputSanitizer.check_xss(text):
            return "", "Potential XSS attack detected"
        
        sanitized = InputSanitizer.sanitize_text(text, max_length)
        return sanitized, None


class FileValidator:
    """Utility class for file validation."""
    
    ALLOWED_EXTENSIONS = {'.csv', '.txt', '.xlsx', '.xls', '.parquet', '.json'}
    MAX_FILE_SIZE_MB = 500
    
    @staticmethod
    def validate_file_extension(filename: str) -> tuple[bool, Optional[str]]:
        """
        Validate file extension.
        
        Args:
            filename: File name
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename:
            return False, "No filename provided"
        
        ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in FileValidator.ALLOWED_EXTENSIONS:
            return False, f"File extension '{ext}' not allowed. Allowed: {', '.join(FileValidator.ALLOWED_EXTENSIONS)}"
        
        return True, None
    
    @staticmethod
    def validate_file_size(size_bytes: int) -> tuple[bool, Optional[str]]:
        """
        Validate file size.
        
        Args:
            size_bytes: File size in bytes
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        max_bytes = FileValidator.MAX_FILE_SIZE_MB * 1024 * 1024
        if size_bytes > max_bytes:
            size_mb = size_bytes / (1024 * 1024)
            return False, f"File size ({size_mb:.2f} MB) exceeds maximum ({FileValidator.MAX_FILE_SIZE_MB} MB)"
        
        return True, None
    
    @staticmethod
    def validate_file_content(file_obj: Any) -> tuple[bool, Optional[str]]:
        """
        Validate file content (basic check).
        
        Args:
            file_obj: File object
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Read first few bytes to check if file is readable
            if hasattr(file_obj, 'read'):
                file_obj.seek(0)
                sample = file_obj.read(1024)
                file_obj.seek(0)
                if not sample:
                    return False, "File appears to be empty"
        except Exception as e:
            return False, f"Error reading file: {str(e)}"
        
        return True, None


class RateLimiter:
    """Rate limiting utility."""
    
    def __init__(self, max_calls: int = 10, window_seconds: int = 60):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls: list[float] = []
    
    def check_rate_limit(self, action: str = "default") -> tuple[bool, Optional[str]]:
        """
        Check if action is within rate limit.
        
        Args:
            action: Action identifier (for logging)
        
        Returns:
            Tuple of (is_allowed, error_message)
        """
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        # Remove old calls
        self.calls = [call_time for call_time in self.calls if call_time > window_start]
        
        if len(self.calls) >= self.max_calls:
            return False, f"Rate limit exceeded. Maximum {self.max_calls} calls per {self.window_seconds} seconds"
        
        self.calls.append(current_time)
        return True, None
    
    def reset(self) -> None:
        """Reset rate limiter."""
        self.calls.clear()


# Global rate limiters for different actions
file_upload_limiter = RateLimiter(max_calls=5, window_seconds=60)
api_call_limiter = RateLimiter(max_calls=100, window_seconds=60)
validation_limiter = RateLimiter(max_calls=20, window_seconds=60)

