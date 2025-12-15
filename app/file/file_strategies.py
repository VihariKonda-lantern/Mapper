# --- file_strategies.py ---
"""Strategy pattern for different file types."""
from abc import ABC, abstractmethod
from typing import Any, List, Optional
import pandas as pd
import io
import gzip
import bz2
from pathlib import Path
from core.exceptions import FileError
from decorators import log_execution, handle_errors


class FileStrategy(ABC):
    """Abstract base class for file handling strategies."""
    
    @abstractmethod
    def can_handle(self, filename: str) -> bool:
        """Check if this strategy can handle the file."""
        pass
    
    @abstractmethod
    def load(self, file_obj: Any) -> pd.DataFrame:
        """Load file into DataFrame."""
        pass
    
    @abstractmethod
    def save(self, df: pd.DataFrame, file_path: str) -> None:
        """Save DataFrame to file."""
        pass


class CSVFileStrategy(FileStrategy):
    """Strategy for handling CSV files."""
    
    def can_handle(self, filename: str) -> bool:
        """Check if file is CSV."""
        return filename.lower().endswith(('.csv', '.txt'))
    
    @log_execution(log_args=False)
    @handle_errors(error_message="Failed to load CSV file")
    def load(self, file_obj: Any) -> pd.DataFrame:
        """Load CSV file."""
        try:
            return pd.read_csv(io.BytesIO(file_obj.read()))
        except Exception as e:
            raise FileError(
                f"Error loading CSV: {str(e)}",
                error_code="CSV_LOAD_ERROR"
            ) from e
    
    def save(self, df: pd.DataFrame, file_path: str) -> None:
        """Save DataFrame as CSV."""
        df.to_csv(file_path, index=False)


class ExcelFileStrategy(FileStrategy):
    """Strategy for handling Excel files."""
    
    def can_handle(self, filename: str) -> bool:
        """Check if file is Excel."""
        return filename.lower().endswith(('.xlsx', '.xls'))
    
    @log_execution(log_args=False)
    @handle_errors(error_message="Failed to load Excel file")
    def load(self, file_obj: Any) -> pd.DataFrame:
        """Load Excel file."""
        try:
            return pd.read_excel(io.BytesIO(file_obj.read()))
        except Exception as e:
            raise FileError(
                f"Error loading Excel: {str(e)}",
                error_code="EXCEL_LOAD_ERROR"
            ) from e
    
    def save(self, df: pd.DataFrame, file_path: str) -> None:
        """Save DataFrame as Excel."""
        df.to_excel(file_path, index=False)


class ParquetFileStrategy(FileStrategy):
    """Strategy for handling Parquet files."""
    
    def can_handle(self, filename: str) -> bool:
        """Check if file is Parquet."""
        return filename.lower().endswith('.parquet')
    
    @log_execution(log_args=False)
    @handle_errors(error_message="Failed to load Parquet file")
    def load(self, file_obj: Any) -> pd.DataFrame:
        """Load Parquet file."""
        try:
            return pd.read_parquet(io.BytesIO(file_obj.read()))
        except Exception as e:
            raise FileError(
                f"Error loading Parquet: {str(e)}",
                error_code="PARQUET_LOAD_ERROR"
            ) from e
    
    def save(self, df: pd.DataFrame, file_path: str) -> None:
        """Save DataFrame as Parquet."""
        df.to_parquet(file_path, index=False)


class CompressedFileStrategy(FileStrategy):
    """Strategy for handling compressed files (gzip, bz2)."""
    
    def __init__(self, base_strategy: FileStrategy, compression_type: str):
        """
        Initialize compressed file strategy.
        
        Args:
            base_strategy: Base file strategy (CSV, JSON, etc.)
            compression_type: Type of compression ('gz', 'bz2')
        """
        self.base_strategy = base_strategy
        self.compression_type = compression_type
    
    def can_handle(self, filename: str) -> bool:
        """Check if file is compressed."""
        filename_lower = filename.lower()
        if self.compression_type == 'gz':
            return filename_lower.endswith('.gz') or filename_lower.endswith('.gzip')
        elif self.compression_type == 'bz2':
            return filename_lower.endswith('.bz2')
        return False
    
    @log_execution(log_args=False)
    @handle_errors(error_message="Failed to load compressed file")
    def load(self, file_obj: Any) -> pd.DataFrame:
        """Load compressed file."""
        try:
            # Read compressed content
            compressed_content = file_obj.read()
            
            # Decompress based on type
            if self.compression_type == 'gz':
                decompressed = gzip.decompress(compressed_content)
            elif self.compression_type == 'bz2':
                decompressed = bz2.decompress(compressed_content)
            else:
                raise FileError(
                    f"Unsupported compression type: {self.compression_type}",
                    error_code="UNSUPPORTED_COMPRESSION"
                )
            
            # Determine base file type from original filename (without compression extension)
            original_name = Path(file_obj.name).stem if hasattr(file_obj, 'name') else "file"
            
            # Create a new file-like object with decompressed content
            decompressed_file = io.BytesIO(decompressed)
            decompressed_file.name = original_name  # Set name for strategy detection
            
            # Use base strategy to load
            return self.base_strategy.load(decompressed_file)
            
        except Exception as e:
            raise FileError(
                f"Error loading compressed file: {str(e)}",
                error_code="COMPRESSED_FILE_LOAD_ERROR"
            ) from e
    
    def save(self, df: pd.DataFrame, file_path: str) -> None:
        """Save DataFrame as compressed file."""
        # Create temporary file for base strategy
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_path).suffix.replace('.gz', '').replace('.bz2', '')) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Save using base strategy
            self.base_strategy.save(df, tmp_path)
            
            # Read and compress
            with open(tmp_path, 'rb') as f:
                content = f.read()
            
            if self.compression_type == 'gz':
                compressed = gzip.compress(content)
            elif self.compression_type == 'bz2':
                compressed = bz2.compress(content)
            else:
                raise FileError(
                    f"Unsupported compression type: {self.compression_type}",
                    error_code="UNSUPPORTED_COMPRESSION"
                )
            
            # Write compressed content
            with open(file_path, 'wb') as f:
                f.write(compressed)
        finally:
            # Clean up temp file
            import os
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class FileStrategyFactory:
    """Factory for creating file strategies."""
    
    _strategies: List[FileStrategy] = [
        CSVFileStrategy(),
        ExcelFileStrategy(),
        ParquetFileStrategy()
    ]
    
    @classmethod
    def _detect_compression(cls, filename: str) -> Optional[str]:
        """Detect compression type from filename."""
        filename_lower = filename.lower()
        if filename_lower.endswith('.gz') or filename_lower.endswith('.gzip'):
            return 'gz'
        elif filename_lower.endswith('.bz2'):
            return 'bz2'
        return None
    
    @classmethod
    def get_strategy(cls, filename: str) -> Optional[FileStrategy]:
        """Get appropriate strategy for a file."""
        # Check for compression first
        compression_type = cls._detect_compression(filename)
        
        if compression_type:
            # Get base filename without compression extension
            base_filename = filename
            if compression_type == 'gz':
                base_filename = filename.replace('.gz', '').replace('.gzip', '')
            elif compression_type == 'bz2':
                base_filename = filename.replace('.bz2', '')
            
            # Find base strategy
            base_strategy = None
            for strategy in cls._strategies:
                if strategy.can_handle(base_filename):
                    base_strategy = strategy
                    break
            
            if base_strategy:
                return CompressedFileStrategy(base_strategy, compression_type)
            return None
        
        # No compression, find regular strategy
        for strategy in cls._strategies:
            if strategy.can_handle(filename):
                return strategy
        return None
    
    @classmethod
    def load_file(cls, file_obj: Any) -> pd.DataFrame:
        """Load file using appropriate strategy."""
        if file_obj is None:
            raise FileError("No file provided", error_code="FILE_NOT_FOUND")
        
        strategy = cls.get_strategy(file_obj.name)
        if strategy is None:
            raise FileError(
                f"Unsupported file type: {file_obj.name}",
                error_code="INVALID_FILE_FORMAT"
            )
        
        return strategy.load(file_obj)

