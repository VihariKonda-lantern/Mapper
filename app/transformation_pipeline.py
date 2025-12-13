# --- transformation_pipeline.py ---
"""Transformation pipeline with history tracking and rollback capability."""
from typing import Any, Dict, List, Optional, Callable
import pandas as pd
from datetime import datetime
from dataclasses import dataclass, field
from models import Mapping
from decorators import log_execution, handle_errors
from exceptions import ProcessingError


@dataclass
class TransformationStep:
    """Represents a single transformation step."""
    step_id: str
    transformation_name: str
    timestamp: datetime
    input_hash: str
    output_hash: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "transformation_name": self.transformation_name,
            "timestamp": self.timestamp.isoformat(),
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "parameters": self.parameters,
            "metadata": self.metadata
        }


class TransformationPipeline:
    """Pipeline for managing multiple transformations with history."""
    
    def __init__(self):
        self.steps: List[TransformationStep] = []
        self.data_snapshots: Dict[str, pd.DataFrame] = {}
        self.max_history: int = 50
    
    @log_execution(log_args=False)
    def add_step(
        self,
        transformation_name: str,
        transform_func: Callable[[pd.DataFrame, Dict[str, Any]], pd.DataFrame],
        df: pd.DataFrame,
        parameters: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Add a transformation step to the pipeline.
        
        Args:
            transformation_name: Name of the transformation
            transform_func: Function to apply the transformation
            df: Input DataFrame
            parameters: Transformation parameters
        
        Returns:
            Transformed DataFrame
        """
        import hashlib
        parameters = parameters or {}
        
        # Create input hash
        input_hash = hashlib.md5(str(df.values.tolist()).encode()).hexdigest()
        
        # Apply transformation
        try:
            result_df = transform_func(df, parameters)
        except Exception as e:
            raise ProcessingError(
                f"Transformation '{transformation_name}' failed: {str(e)}",
                error_code="TRANSFORMATION_ERROR",
                context={"transformation": transformation_name, "parameters": parameters}
            ) from e
        
        # Create output hash
        output_hash = hashlib.md5(str(result_df.values.tolist()).encode()).hexdigest()
        
        # Create step
        step = TransformationStep(
            step_id=f"step_{len(self.steps) + 1}",
            transformation_name=transformation_name,
            timestamp=datetime.now(),
            input_hash=input_hash,
            output_hash=output_hash,
            parameters=parameters,
            metadata={
                "input_rows": len(df),
                "output_rows": len(result_df),
                "input_cols": len(df.columns),
                "output_cols": len(result_df.columns)
            }
        )
        
        # Store snapshot
        self.data_snapshots[step.step_id] = df.copy()
        
        # Add step
        self.steps.append(step)
        
        # Limit history
        if len(self.steps) > self.max_history:
            oldest_step = self.steps.pop(0)
            if oldest_step.step_id in self.data_snapshots:
                del self.data_snapshots[oldest_step.step_id]
        
        return result_df
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get transformation history."""
        return [step.to_dict() for step in self.steps]
    
    def rollback(self, step_id: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Rollback to a previous transformation step.
        
        Args:
            step_id: Step ID to rollback to (None for previous step)
        
        Returns:
            DataFrame at the rollback point, or None if step not found
        """
        if not self.steps:
            return None
        
        if step_id is None:
            # Rollback to previous step
            if len(self.steps) > 1:
                target_step = self.steps[-2]
            else:
                return None
        else:
            # Find target step
            target_step = None
            for step in self.steps:
                if step.step_id == step_id:
                    target_step = step
                    break
            
            if target_step is None:
                return None
        
        # Get snapshot
        if target_step.step_id in self.data_snapshots:
            # Remove steps after target
            target_index = self.steps.index(target_step)
            self.steps = self.steps[:target_index + 1]
            
            # Clean up snapshots
            removed_steps = [s.step_id for s in self.steps[target_index + 1:]]
            for sid in removed_steps:
                if sid in self.data_snapshots:
                    del self.data_snapshots[sid]
            
            return self.data_snapshots[target_step.step_id].copy()
        
        return None
    
    def get_lineage(self) -> Dict[str, Any]:
        """
        Get data lineage information.
        
        Returns:
            Dictionary with lineage information
        """
        return {
            "total_steps": len(self.steps),
            "steps": [step.to_dict() for step in self.steps],
            "data_flow": [
                {
                    "from": step.input_hash[:8],
                    "to": step.output_hash[:8],
                    "transformation": step.transformation_name
                }
                for step in self.steps
            ]
        }
    
    def clear_history(self) -> None:
        """Clear transformation history."""
        self.steps.clear()
        self.data_snapshots.clear()


class TransformationTemplate:
    """Template for reusable transformations."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_step(
        self,
        transformation_name: str,
        parameters: Dict[str, Any]
    ) -> None:
        """Add a step to the template."""
        self.steps.append({
            "transformation_name": transformation_name,
            "parameters": parameters
        })
        self.updated_at = datetime.now()
    
    def apply(
        self,
        df: pd.DataFrame,
        pipeline: TransformationPipeline
    ) -> pd.DataFrame:
        """Apply template transformations to DataFrame."""
        result_df = df
        for step in self.steps:
            # This would need actual transformation functions
            # For now, just return the DataFrame
            pass
        return result_df
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class TransformationTemplateManager:
    """Manager for transformation templates."""
    
    def __init__(self):
        self.templates: Dict[str, TransformationTemplate] = {}
    
    def save_template(self, template: TransformationTemplate) -> None:
        """Save a transformation template."""
        self.templates[template.name] = template
    
    def load_template(self, name: str) -> Optional[TransformationTemplate]:
        """Load a transformation template."""
        return self.templates.get(name)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all templates."""
        return [template.to_dict() for template in self.templates.values()]


# Global pipeline instance
transformation_pipeline = TransformationPipeline()
template_manager = TransformationTemplateManager()

