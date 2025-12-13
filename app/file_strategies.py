# --- file_strategies.py ---
"""Strategy pattern for different file types."""
from abc import ABC, abstractmethod
from typing import Any, Optional
import pandas as pd
import io
from exceptions import FileError
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


class FileStrategyFactory:
    """Factory for creating file strategies."""
    
    _strategies: List[FileStrategy] = [
        CSVFileStrategy(),
        ExcelFileStrategy(),
        ParquetFileStrategy()
    ]
    
    @classmethod
    def get_strategy(cls, filename: str) -> Optional[FileStrategy]:
        """Get appropriate strategy for a file."""
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

