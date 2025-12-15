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
