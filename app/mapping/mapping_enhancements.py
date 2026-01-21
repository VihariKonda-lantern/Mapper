"""Enhanced mapping features: multiple suggestions, context awareness, embeddings."""
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import difflib
import re

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from core.exceptions import MappingError


class MappingSuggester:
    """Enhanced mapping suggestion engine with multiple algorithms."""
    
    def __init__(
        self,
        use_embeddings: bool = True,
        use_context: bool = True,
        top_n: int = 3
    ):
        """
        Initialize mapping suggester.
    
    Args:
            use_embeddings: Whether to use word embeddings (requires sklearn)
            use_context: Whether to consider field context
            top_n: Number of top suggestions to return
        """
        self.use_embeddings = use_embeddings and SKLEARN_AVAILABLE
        self.use_context = use_context
        self.top_n = top_n
        self._vectorizer = None
    
    def _fuzzy_match(
        self,
        internal_field: str,
        source_columns: List[str],
        threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        """Fuzzy string matching."""
        scores = []
        internal_lower = internal_field.lower()
        
        for col in source_columns:
            col_lower = col.lower()
            ratio = difflib.SequenceMatcher(None, internal_lower, col_lower).ratio()
            if ratio >= threshold:
                scores.append((col, ratio))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)
    
    def _embedding_match(
        self,
        internal_field: str,
        source_columns: List[str],
        field_descriptions: Optional[Dict[str, str]] = None
    ) -> List[Tuple[str, float]]:
        """Semantic matching using embeddings."""
        if not self.use_embeddings:
            return []
        
        try:
            # Prepare texts
            texts = [internal_field]
            if field_descriptions and internal_field in field_descriptions:
                texts[0] = f"{internal_field} {field_descriptions[internal_field]}"
            
            for col in source_columns:
                col_text = col
                if field_descriptions and col in field_descriptions:
                    col_text = f"{col} {field_descriptions[col]}"
                texts.append(col_text)
            
            # Vectorize
            if self._vectorizer is None:
                self._vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            
            vectors = self._vectorizer.fit_transform(texts)
            
            # Calculate similarities
            similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
            
            # Return top matches
            scores = [(source_columns[i], float(sim)) for i, sim in enumerate(similarities)]
            return sorted(scores, key=lambda x: x[1], reverse=True)
        except Exception:
            return []
    
    def _context_match(
        self,
        internal_field: str,
        source_columns: List[str],
        field_groups: Optional[Dict[str, str]] = None,
        field_types: Optional[Dict[str, str]] = None
    ) -> List[Tuple[str, float]]:
        """Context-aware matching."""
        if not self.use_context:
            return []
        
        scores = []
        internal_lower = internal_field.lower()
        
        # Extract context from field name
        internal_group = None
        internal_type = None
        
        if field_groups and internal_field in field_groups:
            internal_group = field_groups[internal_field].lower()
        
        if field_types and internal_field in field_types:
            internal_type = field_types[internal_field].lower()
        
        for col in source_columns:
            col_lower = col.lower()
            score = 0.0
            
            # Group matching
            if field_groups and col in field_groups:
                col_group = field_groups[col].lower()
                if internal_group and col_group == internal_group:
                    score += 0.3
            
            # Type matching
            if field_types and col in field_types:
                col_type = field_types[col].lower()
                if internal_type and col_type == internal_type:
                    score += 0.2
            
            # Keyword matching
            keywords = ['id', 'name', 'date', 'amount', 'code', 'address']
            for keyword in keywords:
                if keyword in internal_lower and keyword in col_lower:
                    score += 0.1
            
            if score > 0:
                scores.append((col, score))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)
    
    def suggest_mappings(
        self,
        internal_field: str,
        source_columns: List[str],
        field_descriptions: Optional[Dict[str, str]] = None,
        field_groups: Optional[Dict[str, str]] = None,
        field_types: Optional[Dict[str, str]] = None,
        sample_values: Optional[Dict[str, List[str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get multiple mapping suggestions for a field.
    
    Args:
            internal_field: Internal field name
            source_columns: Available source columns
            field_descriptions: Optional field descriptions
            field_groups: Optional field groups
            field_types: Optional field types
            sample_values: Optional sample values for each column
        
    Returns:
            List of suggestions with confidence scores
        """
        suggestions: Dict[str, float] = {}
        
        # Fuzzy matching
        fuzzy_results = self._fuzzy_match(internal_field, source_columns)
        for col, score in fuzzy_results:
            if col not in suggestions:
                suggestions[col] = 0.0
            suggestions[col] += score * 0.4  # Weight: 40%
        
        # Embedding matching
        if self.use_embeddings:
            embedding_results = self._embedding_match(internal_field, source_columns, field_descriptions)
            for col, score in embedding_results:
                if col not in suggestions:
                    suggestions[col] = 0.0
                suggestions[col] += score * 0.3  # Weight: 30%
        
        # Context matching
        if self.use_context:
            context_results = self._context_match(internal_field, source_columns, field_groups, field_types)
            for col, score in context_results:
                if col not in suggestions:
                    suggestions[col] = 0.0
                suggestions[col] += score * 0.2  # Weight: 20%
        
        # Value pattern matching
        if sample_values:
            pattern_score = self._pattern_match(internal_field, source_columns, sample_values)
            for col, score in pattern_score:
                if col not in suggestions:
                    suggestions[col] = 0.0
                suggestions[col] += score * 0.1  # Weight: 10%
        
        # Normalize scores
        if suggestions:
            max_score = max(suggestions.values())
            if max_score > 0:
                suggestions = {k: v / max_score for k, v in suggestions.items()}
        
        # Sort and return top N
        sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                "value": col,
                "confidence": score,
                "algorithm": "multi"
            }
            for col, score in sorted_suggestions[:self.top_n]
        ]
    
    def _pattern_match(
        self,
        internal_field: str,
        source_columns: List[str],
        sample_values: Dict[str, List[str]]
    ) -> List[Tuple[str, float]]:
        """Match based on value patterns."""
        scores = []
        internal_lower = internal_field.lower()
        
        # Detect expected pattern from field name
        expected_pattern = None
        if 'date' in internal_lower or 'dob' in internal_lower:
            expected_pattern = 'date'
        elif 'zip' in internal_lower:
            expected_pattern = 'zip'
        elif 'npi' in internal_lower:
            expected_pattern = 'npi'
        elif 'cpt' in internal_lower:
            expected_pattern = 'cpt'
        elif 'icd' in internal_lower:
            expected_pattern = 'icd'
        
        if not expected_pattern:
            return []
        
        for col in source_columns:
            if col not in sample_values:
                continue
            
            values = sample_values[col][:10]  # Sample first 10
            matches = 0
            
            for val in values:
                val_str = str(val).strip()
                
                if expected_pattern == 'date':
                    if re.match(r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$', val_str):
                        matches += 1
                elif expected_pattern == 'zip':
                    if re.match(r'^\d{5}(-\d{4})?$', val_str):
                        matches += 1
                elif expected_pattern == 'npi':
                    if re.match(r'^\d{10}$', val_str):
                        matches += 1
                elif expected_pattern == 'cpt':
                    if re.match(r'^\d{5}$', val_str):
                        matches += 1
                elif expected_pattern == 'icd':
                    if re.match(r'^[A-TV-Z][0-9][0-9A-TV-Z].*$', val_str, re.IGNORECASE):
                        matches += 1
            
            if values:
                score = matches / len(values)
                if score > 0.5:  # At least 50% match
                    scores.append((col, score))
        
        return scores


class MappingLearner:
    """Learn from user corrections to improve suggestions."""
    
    def __init__(self):
        """Initialize mapping learner."""
        self.corrections: List[Dict[str, Any]] = []
        self.patterns: Dict[str, Dict[str, float]] = {}
    
    def record_correction(
        self,
        internal_field: str,
        suggested: str,
        corrected: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a user correction.
        
        Args:
            internal_field: Internal field name
            suggested: Originally suggested column
            corrected: User's correction
            context: Optional context (field type, group, etc.)
        """
        self.corrections.append({
            "internal_field": internal_field,
            "suggested": suggested,
            "corrected": corrected,
            "context": context or {}
        })
        
        # Update patterns
        if internal_field not in self.patterns:
            self.patterns[internal_field] = {}
        
        # Learn from correction
        if corrected not in self.patterns[internal_field]:
            self.patterns[internal_field][corrected] = 0.0
        
        self.patterns[internal_field][corrected] += 1.0
    
    def get_learned_suggestion(
        self,
        internal_field: str,
        source_columns: List[str]
    ) -> Optional[str]:
        """
        Get suggestion based on learned patterns.
        
        Args:
            internal_field: Internal field name
            source_columns: Available source columns
        
        Returns:
            Best matching column based on learning, or None
        """
        if internal_field not in self.patterns:
            return None
        
        field_patterns = self.patterns[internal_field]
        
        # Find best match in available columns
        best_match = None
        best_score = 0.0
        
        for col in source_columns:
            if col in field_patterns:
                score = field_patterns[col]
                if score > best_score:
                    best_score = score
                    best_match = col
        
        return best_match if best_score > 0 else None
    
    def get_confidence_boost(
        self,
        internal_field: str,
        column: str
    ) -> float:
        """
        Get confidence boost from learning.
    
    Args:
            internal_field: Internal field name
            column: Column name
        
    Returns:
            Confidence boost (0.0 to 1.0)
        """
        if internal_field not in self.patterns:
            return 0.0
        
        field_patterns = self.patterns[internal_field]
        if column not in field_patterns:
            return 0.0
        
        # Normalize boost (max 0.3 boost)
        count = field_patterns[column]
        return min(0.3, count / 10.0)


# Convenience functions for backward compatibility
def get_mapping_confidence_score(
    final_mapping: Dict[str, Any],
    ai_suggestions: Optional[Dict[str, Any]] = None
) -> Dict[str, float]:
    """
    Get confidence scores for mappings by comparing final mapping with AI suggestions.
    
    Args:
        final_mapping: Final mapping dictionary {field: {"value": col, ...}}
        ai_suggestions: Optional AI suggestions dictionary {field: {"value": col, "confidence": float, ...}}
        
    Returns:
        Dictionary of {field: confidence_score} where confidence is 0.0 to 1.0
    """
    confidence_scores = {}
    
    if ai_suggestions:
        # Compare final mapping with AI suggestions
        for field, mapping_data in final_mapping.items():
            if field in ai_suggestions:
                # Get confidence from AI suggestions
                ai_data = ai_suggestions[field]
                if isinstance(ai_data, dict):
                    confidence = ai_data.get('confidence', 0.0)
                else:
                    confidence = 0.0
                confidence_scores[field] = confidence
            else:
                # Field not in AI suggestions, default to 0.0
                confidence_scores[field] = 0.0
    else:
        # No AI suggestions, extract confidence from mapping if available
        for field, mapping_data in final_mapping.items():
            if isinstance(mapping_data, dict):
                confidence = mapping_data.get('confidence', 0.0)
            else:
                confidence = 0.0
            confidence_scores[field] = confidence
    
    return confidence_scores


def validate_mapping_before_processing(mapping: Dict[str, Dict[str, Any]]) -> tuple[bool, Optional[str]]:
    """
    Validate mapping before processing.
    
    Args:
        mapping: Mapping dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not mapping:
        return False, "Mapping is empty"
    
    for field, mapping_info in mapping.items():
        if 'value' not in mapping_info:
            return False, f"Missing 'value' for field: {field}"
    
    return True, None


def get_mapping_version(mapping: Dict[str, Any]) -> str:
    """
    Get mapping version.
    
    Args:
        mapping: Mapping dictionary
        
    Returns:
        Version string
    """
    return mapping.get('version', '1.0')


def export_mapping_template_for_sharing(mapping: Dict[str, Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Export mapping template for sharing.
    
    Args:
        mapping: Mapping dictionary
        metadata: Optional metadata
        
    Returns:
        Shareable mapping template
    """
    return {
        'mapping': mapping,
        'metadata': metadata or {},
        'version': get_mapping_version(mapping),
        'exported_at': __import__('datetime').datetime.now().isoformat()
    }


def import_mapping_template_from_shareable(template: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Import mapping template from shareable format.
    
    Args:
        template: Shareable mapping template
        
    Returns:
        Mapping dictionary
    """
    return template.get('mapping', {})


# --- Learning Helper Functions ---
# These functions help record mapping corrections for learning

def record_mapping_correction(
    internal_field: str,
    suggested_column: Optional[str],
    corrected_column: str,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Record a mapping correction for learning.
    
    This should be called whenever a user manually changes a mapping,
    especially when they override an AI suggestion.
    
    Args:
        internal_field: The internal field name
        suggested_column: The originally suggested column (from AI or previous mapping)
        corrected_column: The column the user actually selected
        context: Optional context (field type, group, etc.)
    """
    # Skip if no suggestion (first-time mapping)
    if not suggested_column:
        return
    
    # Skip if user selected the same as suggested (no correction)
    if suggested_column == corrected_column:
        return
    
    # Get or create learner instance (requires streamlit)
    try:
        import streamlit as st
        if "mapping_learner" not in st.session_state:
            st.session_state.mapping_learner = MappingLearner()
        
        learner = st.session_state.mapping_learner
        learner.record_correction(internal_field, suggested_column, corrected_column, context)
    except ImportError:
        # Streamlit not available (e.g., in tests)
        pass


def record_bulk_mapping_changes(
    old_mapping: Dict[str, Dict[str, Any]],
    new_mapping: Dict[str, Dict[str, Any]]
) -> None:
    """
    Record corrections when mappings are changed in bulk.
    
    Args:
        old_mapping: Previous mapping state
        new_mapping: New mapping state
    """
    for field, new_info in new_mapping.items():
        new_col = new_info.get("value")
        if not new_col:
            continue
        
        old_info = old_mapping.get(field, {})
        old_col = old_info.get("value")
        
        # Record correction if column changed
        if old_col and old_col != new_col:
            mode = new_info.get("mode", "manual")
            # Only record if it was an AI suggestion that was overridden
            if old_info.get("mode") == "auto" or mode == "manual":
                record_mapping_correction(field, old_col, new_col)
