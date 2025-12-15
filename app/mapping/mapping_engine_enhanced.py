"""Enhanced mapping engine with multiple algorithms, tuning, caching, and batch matching."""
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import difflib
from enum import Enum
from functools import lru_cache
import hashlib
import json

from core.exceptions import MappingError
from performance.cache_manager import CacheManager


class MatchingAlgorithm(Enum):
    """Available matching algorithms."""
    FUZZY = "fuzzy"
    EXACT = "exact"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class MappingEngineEnhanced:
    """Enhanced mapping engine with multiple algorithms and optimizations."""
    
    def __init__(
        self,
        algorithm: MatchingAlgorithm = MatchingAlgorithm.HYBRID,
        fuzzy_threshold: float = 0.6,
        cache_enabled: bool = True,
        cache_ttl: int = 3600
    ):
        """
        Initialize enhanced mapping engine.
        
        Args:
            algorithm: Matching algorithm to use
            fuzzy_threshold: Threshold for fuzzy matching
            cache_enabled: Whether to enable caching
            cache_ttl: Cache TTL in seconds
        """
        self.algorithm = algorithm
        self.fuzzy_threshold = fuzzy_threshold
        self.cache_enabled = cache_enabled
        self.cache = CacheManager(ttl=cache_ttl) if cache_enabled else None
        self._tuning_params: Dict[str, Any] = {
            "fuzzy_weight": 0.4,
            "semantic_weight": 0.3,
            "context_weight": 0.2,
            "pattern_weight": 0.1
        }
    
    def set_tuning_params(self, params: Dict[str, Any]) -> None:
        """
        Set tuning parameters.
        
        Args:
            params: Dictionary of tuning parameters
        """
        self._tuning_params.update(params)
    
    def _generate_cache_key(
        self,
        internal_field: str,
        source_columns: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate cache key for mapping."""
        key_data = {
            "field": internal_field,
            "columns": sorted(source_columns),
            "algorithm": self.algorithm.value,
            "threshold": self.fuzzy_threshold,
            "context": context or {}
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _fuzzy_match(
        self,
        internal_field: str,
        source_columns: List[str],
        threshold: Optional[float] = None
    ) -> List[Tuple[str, float]]:
        """Fuzzy string matching."""
        threshold = threshold or self.fuzzy_threshold
        scores = []
        internal_lower = internal_field.lower()
        
        for col in source_columns:
            col_lower = col.lower()
            ratio = difflib.SequenceMatcher(None, internal_lower, col_lower).ratio()
            if ratio >= threshold:
                scores.append((col, ratio))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)
    
    def _exact_match(
        self,
        internal_field: str,
        source_columns: List[str]
    ) -> List[Tuple[str, float]]:
        """Exact string matching."""
        internal_lower = internal_field.lower()
        matches = []
        
        for col in source_columns:
            if col.lower() == internal_lower:
                matches.append((col, 1.0))
        
        return matches
    
    def _semantic_match(
        self,
        internal_field: str,
        source_columns: List[str],
        field_descriptions: Optional[Dict[str, str]] = None
    ) -> List[Tuple[str, float]]:
        """Semantic matching (simplified - would use embeddings in production)."""
        # Placeholder for semantic matching
        # In production, this would use word embeddings
        scores = []
        internal_lower = internal_field.lower()
        
        # Simple keyword-based semantic matching
        keywords = internal_lower.split('_')
        
        for col in source_columns:
            col_lower = col.lower()
            matches = sum(1 for kw in keywords if kw in col_lower)
            if matches > 0:
                score = matches / len(keywords)
                scores.append((col, score))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)
    
    def _hybrid_match(
        self,
        internal_field: str,
        source_columns: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float]]:
        """Hybrid matching combining multiple algorithms."""
        all_scores: Dict[str, float] = {}
        
        # Fuzzy matching
        fuzzy_results = self._fuzzy_match(internal_field, source_columns)
        for col, score in fuzzy_results:
            if col not in all_scores:
                all_scores[col] = 0.0
            all_scores[col] += score * self._tuning_params["fuzzy_weight"]
        
        # Semantic matching
        field_descriptions = context.get("descriptions", {}) if context else {}
        semantic_results = self._semantic_match(internal_field, source_columns, field_descriptions)
        for col, score in semantic_results:
            if col not in all_scores:
                all_scores[col] = 0.0
            all_scores[col] += score * self._tuning_params["semantic_weight"]
        
        # Context matching
        if context:
            context_results = self._context_match(internal_field, source_columns, context)
            for col, score in context_results:
                if col not in all_scores:
                    all_scores[col] = 0.0
                all_scores[col] += score * self._tuning_params["context_weight"]
        
        # Normalize scores
        if all_scores:
            max_score = max(all_scores.values())
            if max_score > 0:
                all_scores = {k: v / max_score for k, v in all_scores.items()}
        
        return sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
    
    def _context_match(
        self,
        internal_field: str,
        source_columns: List[str],
        context: Dict[str, Any]
    ) -> List[Tuple[str, float]]:
        """Context-aware matching."""
        scores = []
        internal_lower = internal_field.lower()
        
        field_groups = context.get("groups", {})
        field_types = context.get("types", {})
        
        internal_group = field_groups.get(internal_field, "").lower()
        internal_type = field_types.get(internal_field, "").lower()
        
        for col in source_columns:
            col_lower = col.lower()
            score = 0.0
            
            # Group matching
            col_group = field_groups.get(col, "").lower()
            if internal_group and col_group == internal_group:
                score += 0.3
            
            # Type matching
            col_type = field_types.get(col, "").lower()
            if internal_type and col_type == internal_type:
                score += 0.2
            
            # Keyword matching
            keywords = ['id', 'name', 'date', 'amount', 'code']
            for keyword in keywords:
                if keyword in internal_lower and keyword in col_lower:
                    score += 0.1
            
            if score > 0:
                scores.append((col, score))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)
    
    def suggest_mapping(
        self,
        internal_field: str,
        source_columns: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Suggest mapping for a field.
        
        Args:
            internal_field: Internal field name
            source_columns: Available source columns
            context: Optional context (descriptions, groups, types)
        
        Returns:
            Mapping suggestion with confidence
        """
        # Check cache
        if self.cache_enabled and self.cache:
            cache_key = self._generate_cache_key(internal_field, source_columns, context)
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        # Perform matching based on algorithm
        if self.algorithm == MatchingAlgorithm.EXACT:
            results = self._exact_match(internal_field, source_columns)
        elif self.algorithm == MatchingAlgorithm.FUZZY:
            results = self._fuzzy_match(internal_field, source_columns)
        elif self.algorithm == MatchingAlgorithm.SEMANTIC:
            field_descriptions = context.get("descriptions", {}) if context else {}
            results = self._semantic_match(internal_field, source_columns, field_descriptions)
        else:  # HYBRID
            results = self._hybrid_match(internal_field, source_columns, context)
        
        # Get best match
        if results:
            best_col, best_score = results[0]
            suggestion = {
                "value": best_col,
                "confidence": best_score,
                "algorithm": self.algorithm.value
            }
            
            # Cache result
            if self.cache_enabled and self.cache:
                cache_key = self._generate_cache_key(internal_field, source_columns, context)
                self.cache.set(cache_key, suggestion)
            
            return suggestion
        
        return None
    
    def batch_match(
        self,
        internal_fields: List[str],
        source_columns: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Batch matching for multiple fields.
        
        Args:
            internal_fields: List of internal field names
            source_columns: Available source columns
            context: Optional context
        
        Returns:
            Dictionary of field -> mapping suggestion
        """
        results = {}
        
        for field in internal_fields:
            suggestion = self.suggest_mapping(field, source_columns, context)
            if suggestion:
                results[field] = suggestion
        
        return results
    
    def clear_cache(self) -> None:
        """Clear matching cache."""
        if self.cache:
            # Clear all cache entries (would need cache key pattern)
            pass

