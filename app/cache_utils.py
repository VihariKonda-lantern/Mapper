# --- cache_utils.py ---
"""Caching utilities for file loading."""
import streamlit as st
from typing import Any
from layout_loader import load_internal_layout
from diagnosis_loader import load_msk_bar_lookups

st: Any = st


@st.cache_data(show_spinner=False)
def load_layout_cached(file: Any) -> Any:
    """Load layout file with caching."""
    return load_internal_layout(file)


@st.cache_data(show_spinner=False)
def load_lookups_cached(file: Any):
    """Load lookup file with caching."""
    return load_msk_bar_lookups(file)

