# --- security_utils.py ---
"""Security utilities for input sanitization, validation, and rate limiting."""
from typing import Any, Optional
import re
import html
from datetime import datetime, timedelta
import time
from core.exceptions import ClaimsMapperError


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
    """Utility class for file validation with magic number checking."""
    
    # Magic numbers for common file types (first few bytes)
    MAGIC_NUMBERS = {
        # CSV/TXT files - no specific magic number, but we can check for text
        '.csv': None,  # Text-based, check encoding
        '.txt': None,
        '.tsv': None,
        
        # Excel files
        '.xlsx': b'PK\x03\x04',  # ZIP signature (XLSX is a ZIP file)
        '.xls': b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1',  # OLE2 signature
        
        # JSON
        '.json': None,  # Text-based
        
        # Parquet
        '.parquet': b'PAR1',
        
        # Compressed files
        '.gz': b'\x1f\x8b',
        '.bz2': b'BZ',
        '.zip': b'PK\x03\x04',
    }
    
    @staticmethod
    def validate_file_content(file_obj: Any, expected_extension: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """
        Validate file content using magic number checking.
        
        Args:
            file_obj: File-like object to validate
            expected_extension: Expected file extension (e.g., '.csv', '.xlsx')
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not hasattr(file_obj, 'read'):
            return False, "File object does not support reading"
        
        try:
            # Read first few bytes for magic number checking
            current_pos = file_obj.tell()
            file_obj.seek(0)
            magic_bytes = file_obj.read(8)  # Read first 8 bytes
            file_obj.seek(current_pos)  # Restore position
            
            if not magic_bytes:
                return False, "File appears to be empty"
            
            if expected_extension:
                expected_extension = expected_extension.lower()
                expected_magic = FileValidator.MAGIC_NUMBERS.get(expected_extension)
                
                if expected_magic is not None:
                    # Check magic number
                    if not magic_bytes.startswith(expected_magic):
                        return False, (
                            f"File content does not match expected format for {expected_extension}. "
                            f"Expected magic number: {expected_magic.hex()}, "
                            f"Found: {magic_bytes[:len(expected_magic)].hex()}"
                        )
                elif expected_extension in ['.csv', '.txt', '.tsv', '.json']:
                    # For text files, check if content is valid text
                    try:
                        magic_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        # Try other encodings
                        try:
                            magic_bytes.decode('latin-1')
                        except UnicodeDecodeError:
                            return False, f"File does not appear to be a valid text file ({expected_extension})"
            
            # Additional validation based on file type
            if expected_extension == '.xlsx':
                # XLSX files should start with ZIP signature
                if not magic_bytes.startswith(b'PK\x03\x04'):
                    return False, "File does not appear to be a valid XLSX file (missing ZIP signature)"
            
            elif expected_extension == '.xls':
                # XLS files should start with OLE2 signature
                if not magic_bytes.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
                    return False, "File does not appear to be a valid XLS file (missing OLE2 signature)"
            
            elif expected_extension == '.parquet':
                # Parquet files should start with PAR1
                if not magic_bytes.startswith(b'PAR1'):
                    return False, "File does not appear to be a valid Parquet file (missing PAR1 signature)"
            
            elif expected_extension in ['.gz']:
                if not magic_bytes.startswith(b'\x1f\x8b'):
                    return False, "File does not appear to be a valid GZIP file"
            
            elif expected_extension in ['.bz2']:
                if not magic_bytes.startswith(b'BZ'):
                    return False, "File does not appear to be a valid BZIP2 file"
            
            return True, None
            
        except Exception as e:
            return False, f"Error validating file content: {str(e)}"
    
    @staticmethod
    def detect_file_type(file_obj: Any) -> Optional[str]:
        """
        Detect file type from magic number.
        
        Args:
            file_obj: File-like object
        
        Returns:
            Detected file extension or None
        """
        try:
            current_pos = file_obj.tell()
            file_obj.seek(0)
            magic_bytes = file_obj.read(8)
            file_obj.seek(current_pos)
            
            if not magic_bytes:
                return None
            
            # Check against known magic numbers
            for ext, magic in FileValidator.MAGIC_NUMBERS.items():
                if magic and magic_bytes.startswith(magic):
                    return ext
            
            # Check for text files
            try:
                magic_bytes.decode('utf-8')
                # Could be CSV, TXT, TSV, or JSON - need filename or content analysis
                return None
            except UnicodeDecodeError:
                pass
            
            return None
            
        except Exception:
            return None


class FileValidator:
    """Utility class for file validation with magic number checking."""
    
    ALLOWED_EXTENSIONS = {'.csv', '.txt', '.xlsx', '.xls', '.parquet', '.json', '.tsv'}
    MAX_FILE_SIZE_MB = 500
    
    # Magic numbers for common file types (first few bytes)
    MAGIC_NUMBERS = {
        # CSV/TXT files - no specific magic number, but we can check for text
        '.csv': None,  # Text-based, check encoding
        '.txt': None,
        '.tsv': None,
        
        # Excel files
        '.xlsx': b'PK\x03\x04',  # ZIP signature (XLSX is a ZIP file)
        '.xls': b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1',  # OLE2 signature
        
        # JSON
        '.json': None,  # Text-based
        
        # Parquet
        '.parquet': b'PAR1',
        
        # Compressed files
        '.gz': b'\x1f\x8b',
        '.bz2': b'BZ',
        '.zip': b'PK\x03\x04',
    }
    
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
    def validate_file_content(file_obj: Any, expected_extension: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """
        Validate file content using magic number checking.
        
        Args:
            file_obj: File-like object to validate
            expected_extension: Expected file extension (e.g., '.csv', '.xlsx')
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not hasattr(file_obj, 'read'):
            return False, "File object does not support reading"
        
        try:
            # Read first few bytes for magic number checking
            current_pos = file_obj.tell()
            file_obj.seek(0)
            magic_bytes = file_obj.read(8)  # Read first 8 bytes
            file_obj.seek(current_pos)  # Restore position
            
            if not magic_bytes:
                return False, "File appears to be empty"
            
            if expected_extension:
                expected_extension = expected_extension.lower()
                expected_magic = FileValidator.MAGIC_NUMBERS.get(expected_extension)
                
                if expected_magic is not None:
                    # Check magic number
                    if not magic_bytes.startswith(expected_magic):
                        return False, (
                            f"File content does not match expected format for {expected_extension}. "
                            f"Expected magic number: {expected_magic.hex()}, "
                            f"Found: {magic_bytes[:len(expected_magic)].hex()}"
                        )
                elif expected_extension in ['.csv', '.txt', '.tsv', '.json']:
                    # For text files, check if content is valid text
                    try:
                        magic_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        # Try other encodings
                        try:
                            magic_bytes.decode('latin-1')
                        except UnicodeDecodeError:
                            return False, f"File does not appear to be a valid text file ({expected_extension})"
            
            # Additional validation based on file type
            if expected_extension == '.xlsx':
                # XLSX files should start with ZIP signature
                if not magic_bytes.startswith(b'PK\x03\x04'):
                    return False, "File does not appear to be a valid XLSX file (missing ZIP signature)"
            
            elif expected_extension == '.xls':
                # XLS files should start with OLE2 signature
                if not magic_bytes.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
                    return False, "File does not appear to be a valid XLS file (missing OLE2 signature)"
            
            elif expected_extension == '.parquet':
                # Parquet files should start with PAR1
                if not magic_bytes.startswith(b'PAR1'):
                    return False, "File does not appear to be a valid Parquet file (missing PAR1 signature)"
            
            elif expected_extension in ['.gz']:
                if not magic_bytes.startswith(b'\x1f\x8b'):
                    return False, "File does not appear to be a valid GZIP file"
            
            elif expected_extension in ['.bz2']:
                if not magic_bytes.startswith(b'BZ'):
                    return False, "File does not appear to be a valid BZIP2 file"
            
            return True, None
            
        except Exception as e:
            return False, f"Error validating file content: {str(e)}"
    
    @staticmethod
    def detect_file_type(file_obj: Any) -> Optional[str]:
        """
        Detect file type from magic number.
        
        Args:
            file_obj: File-like object
        
        Returns:
            Detected file extension or None
        """
        try:
            current_pos = file_obj.tell()
            file_obj.seek(0)
            magic_bytes = file_obj.read(8)
            file_obj.seek(current_pos)
            
            if not magic_bytes:
                return None
            
            # Check against known magic numbers
            for ext, magic in FileValidator.MAGIC_NUMBERS.items():
                if magic and magic_bytes.startswith(magic):
                    return ext
            
            # Check for text files
            try:
                magic_bytes.decode('utf-8')
                # Could be CSV, TXT, TSV, or JSON - need filename or content analysis
                return None
            except UnicodeDecodeError:
                pass
            
            return None
            
        except Exception:
            return None


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

