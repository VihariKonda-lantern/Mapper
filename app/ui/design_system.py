"""Unified Design System - Golden Rules of UI/UX.
Based on: https://uxplaybook.org/articles/ui-fundamentals-best-practices-for-ux-designers"""
import streamlit as st
from typing import Any, Optional

st: Any = st


# Design Tokens - Single Source of Truth
class DesignTokens:
    """Centralized design tokens for consistent UI."""
    
    # Typography Scale (8px base, consistent scale)
    FONT_SIZES = {
        'xs': '11px',      # Captions, hints
        'sm': '12px',      # Small text, labels
        'base': '13px',    # Body text (default)
        'md': '14px',      # Medium emphasis
        'lg': '16px',      # Subheadings
        'xl': '18px',      # Section headings
        '2xl': '20px',     # Page titles
        '3xl': '24px',     # Main titles
    }
    
    # Font Weights
    FONT_WEIGHTS = {
        'normal': '400',
        'medium': '500',
        'semibold': '600',
        'bold': '700',
    }
    
    # Spacing Scale (Tight spacing - reduced by ~60%)
    SPACING = {
        'xs': '2px',       # Very tight
        'sm': '4px',       # Small spacing
        'md': '8px',       # Medium spacing (default)
        'lg': '12px',      # Large spacing
        'xl': '16px',      # Extra large
        '2xl': '20px',     # 2x large
        '3xl': '24px',     # 3x large
    }
    
    # Border Radius (consistent rounding)
    RADIUS = {
        'none': '0px',
        'sm': '4px',       # Small elements
        'md': '6px',       # Medium elements (default)
        'lg': '8px',       # Large elements
        'xl': '12px',      # Cards, containers
        'full': '9999px',  # Pills, badges
    }
    
    # Container Sizes
    CONTAINERS = {
        'sm': '640px',     # Small containers
        'md': '768px',     # Medium containers
        'lg': '1024px',    # Large containers
        'xl': '1280px',    # Extra large
        '2xl': '1400px',   # Maximum width (default)
        'full': '100%',    # Full width
    }
    
    # Component Heights (consistent touch targets)
    HEIGHTS = {
        'input': '36px',   # Input fields, selectboxes
        'button': '36px',  # Buttons
        'button-lg': '44px', # Large buttons
        'icon': '20px',    # Icons
        'avatar': '40px',  # Avatars
    }
    
    # Chart Heights (consistent across all tabs)
    CHART_HEIGHTS = {
        'standard': 350,   # Standard charts (bar, line, pie, donut)
        'gauge': 400,      # Gauge charts
        'radar': 450,      # Radar charts
        'large': 500,      # Large charts (heatmaps, complex visualizations)
        'compact': 300,    # Compact charts (small visualizations)
    }
    
    # Colors (greys and shades of greys only)
    COLORS = {
        'primary': '#6b7280',      # Primary actions (medium grey)
        'primary-hover': '#4b5563', # Darker grey on hover
        'secondary': '#9ca3af',    # Secondary actions (lighter grey)
        'secondary-hover': '#6b7280', # Medium grey on hover
        'text': '#1f2937',         # Main text (dark grey)
        'text-muted': '#6b7280',   # Muted text (medium grey)
        'text-light': '#9ca3af',   # Light text (light grey)
        'border': '#e5e7eb',       # Borders (light grey)
        'border-light': '#f3f4f6', # Light borders (very light grey)
        'background': '#ffffff',   # Main background (white)
        'background-alt': '#f9fafb', # Alternate background (very light grey)
        'background-hover': '#f3f4f6', # Hover states (light grey)
        'success': '#6b7280',      # Success (medium grey)
        'error': '#374151',        # Error (dark grey)
        'warning': '#9ca3af',      # Warning (light grey)
        'info': '#6b7280',         # Info (medium grey)
    }
    
    # Shadows (consistent elevation)
    SHADOWS = {
        'none': 'none',
        'sm': '0 1px 2px rgba(0,0,0,0.05)',
        'md': '0 2px 4px rgba(0,0,0,0.1)',
        'lg': '0 4px 8px rgba(0,0,0,0.1)',
        'xl': '0 8px 16px rgba(0,0,0,0.15)',
    }


def inject_tight_spacing_css():
    """Inject enhanced UI/UX CSS following best practices from UX Playbook."""
    st.markdown("""
        <style>
        /* ============================================
           ENHANCED UI/UX - BEST PRACTICES
           Based on: https://uxplaybook.org/articles/ui-fundamentals-best-practices-for-ux-designers
           ============================================ */
        
        /* 1. VISUAL HIERARCHY - Size, Color, Contrast */
        .element-container {
            margin-bottom: 0.25rem !important;
        }
        
        /* Consistent heading hierarchy with proper contrast */
        h2, .stMarkdown h2 {
            margin-top: 0.5rem !important;
            margin-bottom: 0.25rem !important;
            font-weight: 600 !important;
            color: #1f2937 !important;
            letter-spacing: -0.02em !important;
        }
        h3, .stMarkdown h3 {
            margin-top: 0.5rem !important;
            margin-bottom: 0.25rem !important;
            font-weight: 600 !important;
            color: #374151 !important;
            letter-spacing: -0.01em !important;
        }
        h4, .stMarkdown h4 {
            margin-top: 0.5rem !important;
            margin-bottom: 0.125rem !important;
            font-weight: 600 !important;
            color: #4b5563 !important;
        }
        
        /* 2. ACCESSIBILITY - Better contrast and focus states */
        [data-testid="stSelectbox"] > div > div,
        [data-testid="stTextInput"] > div > div > input,
        [data-testid="stTextArea"] > div > div > textarea {
            border: 1px solid #d1d5db !important;
            border-radius: 6px !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stSelectbox"] > div > div:focus-within,
        [data-testid="stTextInput"] > div > div > input:focus,
        [data-testid="stTextArea"] > div > div > textarea:focus {
            border-color: #6b7280 !important;
            box-shadow: 0 0 0 3px rgba(107, 114, 128, 0.1) !important;
            outline: none !important;
        }
        
        /* 3. FEEDBACK - Button hover states and transitions */
        [data-testid="stButton"] > button {
            transition: all 0.2s ease !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
        }
        [data-testid="stButton"] > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        }
        [data-testid="stButton"] > button:active {
            transform: translateY(0) !important;
        }
        
        /* 4. CONSISTENCY - Form elements spacing */
        [data-testid="stSelectbox"], 
        [data-testid="stTextInput"], 
        [data-testid="stTextArea"] {
            margin-top: 0.125rem !important;
            margin-bottom: 0.25rem !important;
        }
        
        /* 5. PROGRESSIVE DISCLOSURE - Expander styling */
        [data-testid="stExpander"] {
            border: 1px solid #e5e7eb !important;
            border-radius: 8px !important;
            margin-bottom: 0.5rem !important;
            background: #ffffff !important;
        }
        [data-testid="stExpander"]:hover {
            border-color: #d1d5db !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        }
        
        /* 6. METRICS - Consistent card styling */
        [data-testid="stMetric"] {
            margin-bottom: 0.25rem !important;
            padding: 0.75rem !important;
            background: #f9fafb !important;
            border-radius: 8px !important;
            border: 1px solid #e5e7eb !important;
        }
        
        /* 7. JSON/CODE - Better readability */
        [data-testid="stJson"] {
            margin-top: 0.125rem !important;
            margin-bottom: 0.25rem !important;
            border-radius: 6px !important;
            border: 1px solid #e5e7eb !important;
        }
        
        /* 8. RADIO - Better spacing */
        [data-testid="stRadio"] {
            margin-bottom: 0.25rem !important;
        }
        
        /* 9. MARKDOWN - Consistent spacing */
        [data-testid="stMarkdownContainer"] {
            margin-bottom: 0.25rem !important;
        }
        
        /* 10. LOADING STATES - Better spinner visibility */
        [data-testid="stSpinner"] {
            color: #6b7280 !important;
        }
        
        /* 11. ALERTS - Better contrast and hierarchy */
        .stAlert {
            border-radius: 8px !important;
            border-left-width: 4px !important;
            padding: 0.75rem 1rem !important;
        }
        
        /* 12. TABLES - Better readability */
        [data-testid="stDataFrame"] {
            border-radius: 8px !important;
            overflow: hidden !important;
        }
        
        /* 13. EMPTY STATES - Better visual hierarchy */
        .empty-state-container {
            text-align: center !important;
            padding: 2rem !important;
            color: #6b7280 !important;
        }
        
        /* 14. MICRO-INTERACTIONS - Smooth transitions */
        * {
            transition: background-color 0.2s ease, border-color 0.2s ease !important;
        }
        
        /* 15. REMOVE EMPTY CONTAINERS - Compact UI - Aggressive cleanup */
        /* Hide all empty element containers */
        [data-testid="stElementContainer"]:empty,
        [data-testid="stElementContainer"]:has(> :empty:only-child),
        [data-testid="stElementContainer"]:has(> div:empty:only-child),
        .element-container:empty,
        .element-container:has(> :empty:only-child) {
            display: none !important;
            margin: 0 !important;
            padding: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
        }
        
        /* Hide empty markdown containers */
        [data-testid="stMarkdownContainer"]:empty,
        [data-testid="stMarkdownContainer"]:has(> :empty:only-child),
        [data-testid="stMarkdownContainer"]:has(> p:empty:only-child),
        [data-testid="stMarkdownContainer"]:has(> div:empty:only-child) {
            display: none !important;
            margin: 0 !important;
            padding: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
        }
        
        /* Remove unnecessary spacing from empty vertical blocks */
        .stVerticalBlock:empty,
        .stVerticalBlock:has(> :empty:only-child),
        .stVerticalBlock:has(> [data-testid="stElementContainer"]:empty:only-child),
        [class*="stVerticalBlock"]:empty {
            display: none !important;
            margin: 0 !important;
            padding: 0 !important;
            height: 0 !important;
        }
        
        /* Compact form spacing */
        [data-testid="stForm"] {
            margin-bottom: 0 !important;
        }
        
        /* Remove empty info/alert containers */
        [data-testid="stAlert"]:empty {
            display: none !important;
        }
        
        /* Remove nested empty containers - prevent multiple nested empty containers */
        [data-testid="stElementContainer"] [data-testid="stElementContainer"]:empty,
        [data-testid="stElementContainer"] [data-testid="stElementContainer"]:has(> :empty:only-child),
        [data-testid="stElementContainer"] [data-testid="stElementContainer"] [data-testid="stElementContainer"]:empty,
        .stVerticalBlock .stVerticalBlock:empty,
        .stVerticalBlock .stVerticalBlock:has(> :empty:only-child),
        .stVerticalBlock .stVerticalBlock .stVerticalBlock:empty {
            display: none !important;
        }
        
        /* Hide containers with only whitespace or invisible content */
        [data-testid="stElementContainer"]:has(> :only-child:is(div:empty, p:empty, span:empty, br:only-child)),
        [data-testid="stElementContainer"]:has(> br:only-child) {
            display: none !important;
        }
        
        /* Remove consecutive empty containers - only allow one at a time */
        [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty,
        [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty {
            display: none !important;
        }
        
        /* Remove empty containers between non-empty ones */
        [data-testid="stElementContainer"]:not(:empty) ~ [data-testid="stElementContainer"]:empty {
            display: none !important;
        }
        
        /* Hide empty containers in columns */
        [data-testid="column"] [data-testid="stElementContainer"]:empty,
        [data-testid="column"] .element-container:empty {
            display: none !important;
        }
        
        /* Remove empty expander content containers */
        [data-testid="stExpander"] [data-testid="stElementContainer"]:empty,
        [data-testid="stExpander"] .element-container:empty {
            display: none !important;
        }
        
        /* Hide empty spinner containers */
        [data-testid="stSpinner"]:empty,
        [data-testid="stSpinner"] + [data-testid="stElementContainer"]:empty,
        [data-testid="stSpinner"] ~ [data-testid="stElementContainer"]:empty {
            display: none !important;
        }
        
        /* Hide skeleton loader containers when empty */
        .skeleton:empty,
        [class*="skeleton"]:empty {
            display: none !important;
        }
        
        /* Remove empty containers after selectboxes when no content follows */
        [data-testid="stSelectbox"] ~ [data-testid="stElementContainer"]:empty,
        [data-testid="stSelectbox"] + [data-testid="stElementContainer"]:empty,
        [data-testid="stSelectbox"] + [data-testid="stElementContainer"] + [data-testid="stElementContainer"]:empty,
        [data-testid="stSelectbox"] + [data-testid="stElementContainer"] + [data-testid="stElementContainer"] + [data-testid="stElementContainer"]:empty,
        [data-testid="stSelectbox"] + [data-testid="stElementContainer"] + [data-testid="stElementContainer"] + [data-testid="stElementContainer"] + [data-testid="stElementContainer"]:empty {
            display: none !important;
        }
        
        /* Aggressive: Hide any empty container that follows a selectbox until we hit non-empty content */
        [data-testid="stSelectbox"] ~ [data-testid="stElementContainer"]:empty:not(:has(+ [data-testid="stElementContainer"]:not(:empty))) {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)


def inject_unified_design_system():
    """Inject unified design system CSS following UI/UX golden rules."""
    tokens = DesignTokens
    
    st.markdown(f"""
    <style>
    /* ============================================
       UNIFIED DESIGN SYSTEM - GOLDEN RULES
       ============================================ */
    
    /* 1. TYPOGRAPHY - Consistent Font Sizes */
    /* Base font size for all text */
    body, .main, .stMarkdown, p, div, span, label {{
        font-size: {tokens.FONT_SIZES['base']} !important;
        line-height: 1.5 !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    /* Heading Hierarchy - Consistent Sizes */
    h1, .stMarkdown h1 {{
        font-size: {tokens.FONT_SIZES['3xl']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        line-height: 1.2 !important;
        margin-top: {tokens.SPACING['md']} !important;
        margin-bottom: {tokens.SPACING['sm']} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    h2, .stMarkdown h2 {{
        font-size: {tokens.FONT_SIZES['2xl']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        line-height: 1.3 !important;
        margin-top: {tokens.SPACING['md']} !important;
        margin-bottom: {tokens.SPACING['sm']} !important;
        color: {tokens.COLORS['text']} !important;
        border-bottom: 1px solid {tokens.COLORS['border-light']} !important;
        padding-bottom: {tokens.SPACING['xs']} !important;
    }}
    
    h3, .stMarkdown h3 {{
        font-size: {tokens.FONT_SIZES['xl']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        line-height: 1.4 !important;
        margin-top: {tokens.SPACING['md']} !important;
        margin-bottom: {tokens.SPACING['xs']} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    h4, .stMarkdown h4 {{
        font-size: {tokens.FONT_SIZES['lg']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        line-height: 1.4 !important;
        margin-top: {tokens.SPACING['md']} !important;
        margin-bottom: {tokens.SPACING['sm']} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    h5, .stMarkdown h5 {{
        font-size: {tokens.FONT_SIZES['md']} !important;
        font-weight: {tokens.FONT_WEIGHTS['medium']} !important;
        line-height: 1.4 !important;
        margin-top: {tokens.SPACING['md']} !important;
        margin-bottom: {tokens.SPACING['xs']} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    h6, .stMarkdown h6 {{
        font-size: {tokens.FONT_SIZES['sm']} !important;
        font-weight: {tokens.FONT_WEIGHTS['medium']} !important;
        line-height: 1.4 !important;
        margin-top: {tokens.SPACING['sm']} !important;
        margin-bottom: {tokens.SPACING['xs']} !important;
        color: {tokens.COLORS['text-muted']} !important;
    }}
    
    /* Captions and small text */
    .stCaption, small, .caption {{
        font-size: {tokens.FONT_SIZES['xs']} !important;
        color: {tokens.COLORS['text-muted']} !important;
        line-height: 1.4 !important;
        margin-top: {tokens.SPACING['xs']} !important;
        margin-bottom: {tokens.SPACING['xs']} !important;
    }}
    
    /* 2. CONTAINER SIZES - Consistent Layout */
    .main .block-container {{
        max-width: {tokens.CONTAINERS['2xl']} !important;
        padding-top: {tokens.SPACING['md']} !important;
        padding-bottom: {tokens.SPACING['md']} !important;
        padding-left: {tokens.SPACING['md']} !important;
        padding-right: {tokens.SPACING['md']} !important;
    }}
    
    /* 3. SPACING - Tight Grid System */
    /* Consistent margins between elements */
    .element-container {{
        margin-bottom: {tokens.SPACING['sm']} !important;
    }}
    
    /* Consistent padding in containers */
    .stContainer {{
        padding: {tokens.SPACING['sm']} !important;
        margin-bottom: {tokens.SPACING['sm']} !important;
    }}
    
    /* 4. BUTTONS - Consistent Sizes */
    .stButton > button,
    button[data-baseweb="button"],
    .stDownloadButton > button {{
        height: {tokens.HEIGHTS['button']} !important;
        min-height: {tokens.HEIGHTS['button']} !important;
        padding: {tokens.SPACING['xs']} {tokens.SPACING['md']} !important;
        font-size: {tokens.FONT_SIZES['base']} !important;
        font-weight: {tokens.FONT_WEIGHTS['medium']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        background-color: {tokens.COLORS['secondary']} !important;
        color: white !important;
        border: none !important;
        box-shadow: {tokens.SHADOWS['sm']} !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }}
    
    .stButton > button:hover,
    button[data-baseweb="button"]:hover,
    .stDownloadButton > button:hover {{
        background-color: {tokens.COLORS['secondary-hover']} !important;
        box-shadow: {tokens.SHADOWS['md']} !important;
        transform: translateY(-1px) !important;
    }}
    
    .stButton > button:disabled,
    button[data-baseweb="button"]:disabled {{
        background-color: {tokens.COLORS['border-light']} !important;
        color: {tokens.COLORS['text-muted']} !important;
        opacity: 0.6 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }}
    
    /* Primary buttons */
    .stButton > button[kind="primary"],
    button[kind="primary"] {{
        background-color: {tokens.COLORS['primary']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background-color: {tokens.COLORS['primary-hover']} !important;
    }}
    
    /* 5. INPUT FIELDS - Consistent Heights */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input,
    .stMultiselect > div > div {{
        height: {tokens.HEIGHTS['input']} !important;
        min-height: {tokens.HEIGHTS['input']} !important;
        padding: {tokens.SPACING['xs']} {tokens.SPACING['sm']} !important;
        font-size: {tokens.FONT_SIZES['base']} !important;
        border: 1px solid {tokens.COLORS['border']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        background-color: {tokens.COLORS['background']} !important;
        color: {tokens.COLORS['text']} !important;
        transition: all 0.2s ease !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div:focus {{
        border-color: {tokens.COLORS['primary']} !important;
        box-shadow: 0 0 0 3px rgba(73, 80, 87, 0.1) !important;
        outline: none !important;
    }}
    
    .stTextInput > div > div > input:hover,
    .stTextArea > div > div > textarea:hover,
    .stSelectbox > div > div:hover {{
        border-color: {tokens.COLORS['border']} !important;
    }}
    
    /* Input labels */
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stNumberInput label,
    .stMultiselect label,
    .stDateInput label,
    .stTimeInput label {{
        font-size: {tokens.FONT_SIZES['sm']} !important;
        font-weight: {tokens.FONT_WEIGHTS['medium']} !important;
        color: {tokens.COLORS['text']} !important;
        margin-bottom: {tokens.SPACING['xs']} !important;
        line-height: 1.4 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
    }}
    
    /* 6. ALERTS - Consistent Styling */
    .stAlert {{
        padding: {tokens.SPACING['sm']} !important;
        margin-bottom: {tokens.SPACING['sm']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        border-left: 3px solid !important;
        font-size: {tokens.FONT_SIZES['base']} !important;
        line-height: 1.5 !important;
    }}
    
    .stInfo {{
        background-color: {tokens.COLORS['background-alt']} !important;
        border-left-color: {tokens.COLORS['info']} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    .stSuccess {{
        background-color: #f0fff4 !important;
        border-left-color: {tokens.COLORS['success']} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    .stWarning {{
        background-color: #f3f4f6 !important;
        border-left-color: {tokens.COLORS['warning']} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    .stError {{
        background-color: #f3f4f6 !important;
        border-left-color: {tokens.COLORS['error']} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    /* 7. EXPANDERS - Consistent Sizing */
    .streamlit-expanderHeader {{
        padding: {tokens.SPACING['xs']} {tokens.SPACING['sm']} !important;
        font-size: {tokens.FONT_SIZES['base']} !important;
        font-weight: {tokens.FONT_WEIGHTS['medium']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        background-color: {tokens.COLORS['background-alt']} !important;
        border: 1px solid {tokens.COLORS['border-light']} !important;
        margin-bottom: {tokens.SPACING['xs']} !important;
    }}
    
    .streamlit-expanderContent {{
        padding: {tokens.SPACING['sm']} !important;
        background-color: {tokens.COLORS['background']} !important;
        border: 1px solid {tokens.COLORS['border-light']} !important;
        border-top: none !important;
        border-radius: 0 0 {tokens.RADIUS['md']} {tokens.RADIUS['md']} !important;
    }}
    
    /* 8. DATA TABLES - Consistent Styling */
    .stDataFrame {{
        margin-bottom: {tokens.SPACING['md']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        border: 1px solid {tokens.COLORS['border-light']} !important;
        overflow: hidden !important;
        font-size: {tokens.FONT_SIZES['sm']} !important;
    }}
    
    .stDataFrame table {{
        border-collapse: collapse !important;
    }}
    
    .stDataFrame th {{
        background-color: {tokens.COLORS['background-alt']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        font-size: {tokens.FONT_SIZES['sm']} !important;
        padding: {tokens.SPACING['sm']} !important;
        border-bottom: 2px solid {tokens.COLORS['border']} !important;
    }}
    
    .stDataFrame td {{
        padding: {tokens.SPACING['sm']} !important;
        border-bottom: 1px solid {tokens.COLORS['border-light']} !important;
        font-size: {tokens.FONT_SIZES['sm']} !important;
    }}
    
    .stDataFrame tr:hover {{
        background-color: {tokens.COLORS['background-hover']} !important;
    }}
    
    /* 9. METRICS - Consistent Display */
    [data-testid="stMetricContainer"] {{
        padding: {tokens.SPACING['md']} !important;
        margin-bottom: {tokens.SPACING['md']} !important;
        border: 1px solid {tokens.COLORS['border-light']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        background-color: {tokens.COLORS['background-alt']} !important;
    }}
    
    [data-testid="stMetricValue"] {{
        font-size: {tokens.FONT_SIZES['2xl']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        font-size: {tokens.FONT_SIZES['sm']} !important;
        font-weight: {tokens.FONT_WEIGHTS['normal']} !important;
        color: {tokens.COLORS['text-muted']} !important;
    }}
    
    /* 10. TABS - Consistent Navigation */
    .stTabs [data-baseweb="tab-list"] {{
        gap: {tokens.SPACING['xs']} !important;
        background-color: {tokens.COLORS['background-alt']} !important;
        padding: {tokens.SPACING['xs']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        margin-bottom: {tokens.SPACING['md']} !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        padding: {tokens.SPACING['sm']} {tokens.SPACING['md']} !important;
        font-size: {tokens.FONT_SIZES['base']} !important;
        font-weight: {tokens.FONT_WEIGHTS['medium']} !important;
        border-radius: {tokens.RADIUS['sm']} !important;
        color: {tokens.COLORS['text']} !important;
        transition: all 0.2s ease !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {tokens.COLORS['background']} !important;
        color: {tokens.COLORS['text']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        box-shadow: {tokens.SHADOWS['sm']} !important;
        border-bottom: 2px solid {tokens.COLORS['primary']} !important;
    }}
    
    /* 11. FILE UPLOADERS - Consistent Sizing */
    .stFileUploader {{
        border: 2px dashed {tokens.COLORS['border']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        padding: {tokens.SPACING['md']} !important;
        background-color: {tokens.COLORS['background-alt']} !important;
        margin-bottom: {tokens.SPACING['md']} !important;
        min-height: 120px !important;
        transition: all 0.2s ease !important;
    }}
    
    .stFileUploader:hover {{
        border-color: {tokens.COLORS['primary']} !important;
        background-color: {tokens.COLORS['background-hover']} !important;
    }}
    
    .stFileUploader label {{
        font-size: {tokens.FONT_SIZES['sm']} !important;
        font-weight: {tokens.FONT_WEIGHTS['medium']} !important;
        color: {tokens.COLORS['text']} !important;
        margin-bottom: {tokens.SPACING['sm']} !important;
    }}
    
    /* 12. SUMMARY CARDS - Consistent Container */
    .summary-cards-wrapper [data-testid="column"] {{
        background: {tokens.COLORS['background']} !important;
        border: 1px solid {tokens.COLORS['border-light']} !important;
        border-radius: {tokens.RADIUS['lg']} !important;
        padding: {tokens.SPACING['md']} !important;
        box-shadow: {tokens.SHADOWS['sm']} !important;
        margin-bottom: {tokens.SPACING['sm']} !important;
        min-height: auto !important;
    }}
    
    .summary-cards-wrapper h4 {{
        font-size: {tokens.FONT_SIZES['lg']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        margin-top: 0 !important;
        margin-bottom: {tokens.SPACING['md']} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    .summary-cards-wrapper .stMarkdown p {{
        font-size: {tokens.FONT_SIZES['base']} !important;
        line-height: 1.5 !important;
        margin-bottom: {tokens.SPACING['sm']} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    /* 13. FORMS - Consistent Layout */
    .stForm {{
        padding: {tokens.SPACING['md']} !important;
        margin-bottom: {tokens.SPACING['sm']} !important;
        border: 1px solid {tokens.COLORS['border-light']} !important;
        border-radius: {tokens.RADIUS['lg']} !important;
        background-color: {tokens.COLORS['background-alt']} !important;
    }}
    
    /* 14. PROGRESS BARS - Consistent Styling */
    [data-testid="stProgressBar"] {{
        margin-bottom: {tokens.SPACING['sm']} !important;
        height: 8px !important;
        border-radius: {tokens.RADIUS['full']} !important;
    }}
    
    [data-testid="stProgressBar"] > div > div {{
        background-color: {tokens.COLORS['primary']} !important;
        border-radius: {tokens.RADIUS['full']} !important;
    }}
    
    /* 15. CODE BLOCKS - Consistent Styling */
    .stCodeBlock, code, pre {{
        font-size: {tokens.FONT_SIZES['sm']} !important;
        padding: {tokens.SPACING['md']} !important;
        margin-bottom: {tokens.SPACING['md']} !important;
        border: 1px solid {tokens.COLORS['border-light']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        background-color: {tokens.COLORS['background-alt']} !important;
    }}
    
    /* 16. DIVIDERS - Consistent Spacing */
    hr {{
        border: none !important;
        border-top: 1px solid {tokens.COLORS['border-light']} !important;
        margin: {tokens.SPACING['md']} 0 !important;
    }}
    
    /* 17. COLUMNS - Consistent Gaps */
    [data-testid="column"] {{
        gap: {tokens.SPACING['sm']} !important;
        padding: {tokens.SPACING['xs']} !important;
    }}
    
    /* 18. CHECKBOXES & RADIOS - Consistent Sizing */
    .stCheckbox, .stRadio {{
        margin-bottom: {tokens.SPACING['sm']} !important;
        font-size: {tokens.FONT_SIZES['base']} !important;
    }}
    
    .stCheckbox label, .stRadio label {{
        font-size: {tokens.FONT_SIZES['base']} !important;
        cursor: pointer !important;
    }}
    
    /* 19. SELECTBOXES - Consistent Dropdown */
    .stSelectbox > div > div > div {{
        min-height: {tokens.HEIGHTS['input']} !important;
        padding: {tokens.SPACING['xs']} {tokens.SPACING['sm']} !important;
        font-size: {tokens.FONT_SIZES['base']} !important;
    }}
    
    /* 20. MULTISELECT - Consistent Display */
    [data-testid="stMultiSelect"] > div {{
        min-height: {tokens.HEIGHTS['input']} !important;
    }}
    
    /* 21. ACCESSIBILITY - Focus States */
    .stButton > button:focus,
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus,
    button[data-baseweb="button"]:focus {{
        outline: 2px solid {tokens.COLORS['primary']} !important;
        outline-offset: 2px !important;
        box-shadow: 0 0 0 3px rgba(73, 80, 87, 0.2) !important;
    }}
    
    /* 22. RESPONSIVE DESIGN */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-left: {tokens.SPACING['sm']} !important;
            padding-right: {tokens.SPACING['sm']} !important;
        }}
        
        h1 {{ font-size: {tokens.FONT_SIZES['2xl']} !important; }}
        h2 {{ font-size: {tokens.FONT_SIZES['xl']} !important; }}
        h3 {{ font-size: {tokens.FONT_SIZES['lg']} !important; }}
        
        .stButton > button {{
            width: 100% !important;
            margin-bottom: {tokens.SPACING['sm']} !important;
        }}
    }}
    
    /* 23. REMOVE ALL INLINE STYLE OVERRIDES */
    /* Override any inline font-size styles */
    [style*="font-size"] {{
        font-size: {tokens.FONT_SIZES['base']} !important;
    }}
    
    /* Override large font sizes */
    [style*="font-size: 1.2rem"],
    [style*="font-size: 1.1rem"],
    [style*="font-size: 22px"],
    [style*="font-size: 20px"] {{
        font-size: {tokens.FONT_SIZES['lg']} !important;
    }}
    
    /* Override small font sizes to be consistent */
    [style*="font-size: 0.9rem"],
    [style*="font-size: 0.85rem"],
    [style*="font-size: 0.75rem"] {{
        font-size: {tokens.FONT_SIZES['sm']} !important;
    }}
    
    /* 24. CONSISTENT COLORS - Remove bright colors */
    [style*="color: #b02a37"],
    [style*="color: #721c24"],
    [style*="color: #856404"],
    [style*="color: #0c5460"],
    [style*="color: #155724"] {{
        color: {tokens.COLORS['text']} !important;
    }}
    
    [style*="background-color:#fdecea"],
    [style*="background-color:#fff3cd"],
    [style*="background-color:#d1ecf1"],
    [style*="background-color:#d4edda"] {{
        background-color: {tokens.COLORS['background-alt']} !important;
    }}
    
    /* 25. SCROLLBARS - Consistent Styling */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {tokens.COLORS['background-alt']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {tokens.COLORS['border']};
        border-radius: {tokens.RADIUS['full']};
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {tokens.COLORS['text-muted']};
    }}
    
    /* 26. REMOVE GRADIENTS */
    * {{
        background-image: none !important;
    }}
    
    /* 27. CONSISTENT MARKDOWN SPACING */
    .stMarkdown {{
        margin-bottom: {tokens.SPACING['md']} !important;
    }}
    
    .stMarkdown p {{
        margin-bottom: {tokens.SPACING['sm']} !important;
    }}
    
    /* 28. CONSISTENT UPLOAD COLUMNS */
    .upload-columns-container {{
        max-width: 100% !important;
        margin: 0 auto !important;
        gap: {tokens.SPACING['md']} !important;
    }}
    
    .upload-columns-container [data-testid="column"] {{
        flex: 1 1 0 !important;
        min-width: 0 !important;
    }}
    
    /* 29. CONSISTENT JSON DISPLAY */
    [data-testid="stJson"] {{
        font-size: {tokens.FONT_SIZES['sm']} !important;
        padding: {tokens.SPACING['md']} !important;
        margin-bottom: {tokens.SPACING['md']} !important;
        border: 1px solid {tokens.COLORS['border-light']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        background-color: {tokens.COLORS['background-alt']} !important;
    }}
    
    /* 30. CONSISTENT DATA EDITOR */
    [data-testid="stDataEditor"] {{
        font-size: {tokens.FONT_SIZES['sm']} !important;
        margin-bottom: {tokens.SPACING['md']} !important;
        border: 1px solid {tokens.COLORS['border-light']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def get_font_size(size_key: str = 'base') -> str:
    """Get font size from design tokens."""
    return DesignTokens.FONT_SIZES.get(size_key, DesignTokens.FONT_SIZES['base'])


def get_spacing(size_key: str = 'md') -> str:
    """Get spacing from design tokens."""
    return DesignTokens.SPACING.get(size_key, DesignTokens.SPACING['md'])


def get_radius(size_key: str = 'md') -> str:
    """Get border radius from design tokens."""
    return DesignTokens.RADIUS.get(size_key, DesignTokens.RADIUS['md'])


def render_section_header(
    title: str,
    level: int = 4,
    description: Optional[str] = None,
    icon: Optional[str] = None,
    margin_top: str = "0.5rem",
    margin_bottom: str = "0.25rem"
) -> None:
    """
    Render a consistent section header following UI/UX best practices.
    
    Based on: https://uxplaybook.org/articles/ui-fundamentals-best-practices-for-ux-designers
    
    Args:
        title: Section title
        level: Heading level (2-4)
        description: Optional description text
        icon: Optional icon emoji
        margin_top: Top margin
        margin_bottom: Bottom margin
    """
    tokens = DesignTokens
    icon_text = f"{icon} " if icon else ""
    
    # Determine font size based on level
    font_sizes = {
        2: tokens.FONT_SIZES['2xl'],
        3: tokens.FONT_SIZES['xl'],
        4: tokens.FONT_SIZES['lg']
    }
    font_size = font_sizes.get(level, tokens.FONT_SIZES['lg'])
    
    # Build header HTML
    header_html = f"""
    <div style='
        margin-top: {margin_top};
        margin-bottom: {margin_bottom};
    '>
        <h{level} style='
            margin: 0;
            padding: 0;
            font-size: {font_size};
            font-weight: {tokens.FONT_WEIGHTS['semibold']};
            color: {tokens.COLORS['text']};
            letter-spacing: -0.01em;
            line-height: 1.3;
        '>{icon_text}{title}</h{level}>
    """
    
    if description:
        header_html += f"""
        <p style='
            margin: 0.25rem 0 0 0;
            padding: 0;
            font-size: {tokens.FONT_SIZES['sm']};
            color: {tokens.COLORS['text-muted']};
            line-height: 1.4;
        '>{description}</p>
        """
    
    header_html += "</div>"
    
    st.markdown(header_html, unsafe_allow_html=True)


def render_enhanced_button(
    label: str,
    key: str,
    variant: str = "primary",
    use_container_width: bool = False,
    help_text: Optional[str] = None
) -> bool:
    """
    Render an enhanced button with better visual feedback.
    
    Args:
        label: Button label
        key: Unique key
        variant: Button variant (primary, secondary, success, danger)
        use_container_width: Use full width
        help_text: Optional tooltip
        
    Returns:
        True if button was clicked
    """
    tokens = DesignTokens
    
    # Color mapping for variants
    variant_colors = {
        "primary": tokens.COLORS['primary'],
        "secondary": tokens.COLORS['secondary'],
        "success": tokens.COLORS['success'],
        "danger": tokens.COLORS['error']
    }
    
    button_color = variant_colors.get(variant, tokens.COLORS['primary'])
    
    return st.button(
        label,
        key=key,
        use_container_width=use_container_width,
        help=help_text,
        type="primary" if variant == "primary" else "secondary"
    )


def render_info_card(
    title: str,
    content: str,
    variant: str = "info",
    icon: Optional[str] = None
) -> None:
    """
    Render a consistent info card with proper visual hierarchy.
    
    Args:
        title: Card title
        content: Card content
        variant: Card variant (info, success, warning, error)
        icon: Optional icon
    """
    tokens = DesignTokens
    
    variant_styles = {
        "info": {
            "bg": "#f9fafb",
            "border": "#6b7280",
            "text": "#374151"
        },
        "success": {
            "bg": "#f3f4f6",
            "border": "#6b7280",
            "text": "#1f2937"
        },
        "warning": {
            "bg": "#f3f4f6",
            "border": "#9ca3af",
            "text": "#374151"
        },
        "error": {
            "bg": "#f3f4f6",
            "border": "#374151",
            "text": "#1f2937"
        }
    }
    
    style = variant_styles.get(variant, variant_styles["info"])
    icon_text = f"{icon} " if icon else ""
    
    card_html = f"""
    <div style='
        background: {style['bg']};
        border-left: 4px solid {style['border']};
        border-radius: {tokens.RADIUS['md']};
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    '>
        <div style='
            font-weight: {tokens.FONT_WEIGHTS['semibold']};
            color: {style['text']};
            font-size: {tokens.FONT_SIZES['base']};
            margin-bottom: 0.25rem;
        '>{icon_text}{title}</div>
        <div style='
            color: {style['text']};
            font-size: {tokens.FONT_SIZES['sm']};
            line-height: 1.5;
        '>{content}</div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

