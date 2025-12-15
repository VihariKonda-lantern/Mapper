# --- base_classes.py ---
"""Base classes for common functionality."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import pandas as pd
from decorators import log_execution, handle_errors
from core.exceptions import ClaimsMapperError


class BaseProcessor(ABC):
    """Base class for data processors."""
    
    def __init__(self, name: str):
        self.name = name
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def process(self, data: Any, **kwargs: Any) -> Any:
        """Process data and return result."""
        pass
    
    @log_execution(log_args=False)
    @handle_errors(error_message="Processing failed")
    def execute(self, data: Any, **kwargs: Any) -> Any:
        """Execute processing with error handling and logging."""
        try:
            result = self.process(data, **kwargs)
            self.metadata["last_execution"] = "success"
            return result
        except Exception as e:
            self.metadata["last_execution"] = "error"
            self.metadata["last_error"] = str(e)
            raise
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get processor metadata."""
        return {
            "name": self.name,
            **self.metadata
        }


class BaseTransformer(BaseProcessor):
    """Base class for data transformers."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.transformation_history: List[Dict[str, Any]] = []
    
    @abstractmethod
    def transform(self, df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        """Transform DataFrame."""
        pass
    
    def process(self, data: Any, **kwargs: Any) -> Any:
        """Process data using transform method."""
        if not isinstance(data, pd.DataFrame):
            raise ClaimsMapperError(
                f"{self.name} requires a DataFrame",
                error_code="INVALID_INPUT_TYPE"
            )
        return self.transform(data, **kwargs)
    
    def apply_transformation(self, df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
        """Apply transformation and track history."""
        result = self.transform(df, **kwargs)
        self.transformation_history.append({
            "transformation": self.name,
            "input_rows": len(df),
            "output_rows": len(result),
            "kwargs": kwargs
        })
        return result


class BaseValidator(BaseProcessor):
    """Base class for validators."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.validation_results: List[Dict[str, Any]] = []
    
    @abstractmethod
    def validate(self, df: pd.DataFrame, **kwargs: Any) -> Dict[str, Any]:
        """Validate DataFrame."""
        pass
    
    def process(self, data: Any, **kwargs: Any) -> Any:
        """Process data using validate method."""
        if not isinstance(data, pd.DataFrame):
            raise ClaimsMapperError(
                f"{self.name} requires a DataFrame",
                error_code="INVALID_INPUT_TYPE"
            )
        return self.validate(data, **kwargs)
    
    def run_validation(self, df: pd.DataFrame, **kwargs: Any) -> Dict[str, Any]:
        """Run validation and track results."""
        result = self.validate(df, **kwargs)
        self.validation_results.append({
            "validation": self.name,
            "timestamp": str(__import__("datetime").datetime.now()),
            "result": result
        })
        return result


class BaseMapper(BaseProcessor):
    """Base class for field mappers."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.mapping_history: List[Dict[str, Any]] = []
    
    @abstractmethod
    def map_fields(
        self,
        source_df: pd.DataFrame,
        target_fields: List[str],
        **kwargs: Any
    ) -> Dict[str, str]:
        """Map source fields to target fields."""
        pass
    
    def process(self, data: Any, **kwargs: Any) -> Any:
        """Process data using map_fields method."""
        if not isinstance(data, pd.DataFrame):
            raise ClaimsMapperError(
                f"{self.name} requires a DataFrame",
                error_code="INVALID_INPUT_TYPE"
            )
        target_fields = kwargs.get("target_fields", [])
        return self.map_fields(data, target_fields, **kwargs)
    
    def create_mapping(
        self,
        source_df: pd.DataFrame,
        target_fields: List[str],
        **kwargs: Any
    ) -> Dict[str, str]:
        """Create mapping and track history."""
        mapping = self.map_fields(source_df, target_fields, **kwargs)
        self.mapping_history.append({
            "mapping": self.name,
            "source_columns": list(source_df.columns),
            "target_fields": target_fields,
            "mapping": mapping,
            "kwargs": kwargs
        })
        return mapping


class BaseFileHandler(ABC):
    """Base class for file handlers."""
    
    def __init__(self, file_type: str):
        self.file_type = file_type
        self.supported_extensions: List[str] = []
    
    @abstractmethod
    def can_handle(self, filename: str) -> bool:
        """Check if handler can process the file."""
        pass
    
    @abstractmethod
    def load(self, file_obj: Any) -> pd.DataFrame:
        """Load file into DataFrame."""
        pass
    
    @abstractmethod
    def save(self, df: pd.DataFrame, file_path: str) -> None:
        """Save DataFrame to file."""
        pass
    
    def get_file_info(self, file_obj: Any) -> Dict[str, Any]:
        """Get file information."""
        return {
            "file_type": self.file_type,
            "filename": getattr(file_obj, "name", "unknown"),
            "size": getattr(file_obj, "size", 0)
        }

