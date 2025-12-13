# --- repositories/file_repository.py ---
"""Repository for file operations."""
from typing import Any, Optional
import pandas as pd
from abc import ABC, abstractmethod
from models import FileMetadata
from exceptions import FileError
from decorators import log_execution, handle_errors


class FileRepository(ABC):
    """Abstract base class for file repositories."""
    
    @abstractmethod
    def load_file(self, file_path: str) -> pd.DataFrame:
        """Load a file into a DataFrame."""
        pass
    
    @abstractmethod
    def save_file(self, df: pd.DataFrame, file_path: str) -> None:
        """Save a DataFrame to a file."""
        pass
    
    @abstractmethod
    def get_metadata(self, file_path: str) -> FileMetadata:
        """Get file metadata."""
        pass


class StreamlitFileRepository(FileRepository):
    """File repository implementation for Streamlit file uploads."""
    
    @log_execution(log_args=False)
    @handle_errors(error_message="Failed to load file")
    def load_file(self, file_obj: Any) -> pd.DataFrame:
        """
        Load a file from Streamlit file uploader.
        
        Args:
            file_obj: Streamlit UploadedFile object
        
        Returns:
            Loaded DataFrame
        
        Raises:
            FileError: If file cannot be loaded
        """
        if file_obj is None:
            raise FileError("No file provided", error_code="FILE_NOT_FOUND")
        
        try:
            import io
            if file_obj.name.endswith('.csv') or file_obj.name.endswith('.txt'):
                return pd.read_csv(io.BytesIO(file_obj.read()))
            elif file_obj.name.endswith('.xlsx') or file_obj.name.endswith('.xls'):
                return pd.read_excel(io.BytesIO(file_obj.read()))
            else:
                raise FileError(
                    f"Unsupported file type: {file_obj.name}",
                    error_code="INVALID_FILE_FORMAT"
                )
        except Exception as e:
            raise FileError(
                f"Error loading file: {str(e)}",
                error_code="FILE_LOAD_ERROR"
            ) from e
    
    def save_file(self, df: pd.DataFrame, file_path: str) -> None:
        """
        Save a DataFrame to a file.
        
        Args:
            df: DataFrame to save
            file_path: Target file path
        
        Raises:
            FileError: If file cannot be saved
        """
        try:
            if file_path.endswith('.csv'):
                df.to_csv(file_path, index=False)
            elif file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
            else:
                raise FileError(
                    f"Unsupported file type: {file_path}",
                    error_code="INVALID_FILE_FORMAT"
                )
        except Exception as e:
            raise FileError(
                f"Error saving file: {str(e)}",
                error_code="FILE_SAVE_ERROR"
            ) from e
    
    def get_metadata(self, file_obj: Any) -> FileMetadata:
        """
        Get metadata from a Streamlit file uploader object.
        
        Args:
            file_obj: Streamlit UploadedFile object
        
        Returns:
            FileMetadata object
        """
        from datetime import datetime
        
        if file_obj is None:
            raise FileError("No file provided", error_code="FILE_NOT_FOUND")
        
        # Try to determine file type
        file_type = "unknown"
        if file_obj.name.endswith('.csv'):
            file_type = "csv"
        elif file_obj.name.endswith('.txt'):
            file_type = "txt"
        elif file_obj.name.endswith('.xlsx') or file_obj.name.endswith('.xls'):
            file_type = "excel"
        
        return FileMetadata(
            filename=file_obj.name,
            size_bytes=file_obj.size,
            uploaded_at=datetime.now(),
            file_type=file_type
        )

