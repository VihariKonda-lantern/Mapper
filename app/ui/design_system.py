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
    
    # Spacing Scale (Ultra-tight, compact spacing - reduced by ~80%)
    SPACING = {
        'xs': '1px',       # Minimal spacing
        'sm': '2px',       # Very small spacing
        'md': '4px',       # Medium spacing (default) - ultra compact
        'lg': '6px',       # Large spacing
        'xl': '8px',       # Extra large
        '2xl': '12px',     # 2x large
        '3xl': '16px',     # 3x large
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
        
        /* 1. VISUAL HIERARCHY - Ultra-tight vertical spacing (0.5px) */
        .element-container {
            margin-bottom: {spacing_value} !important;
            margin-top: 0 !important;
        }
        
        /* Consistent heading hierarchy with 0.5px vertical spacing */
        h1, .stMarkdown h1 {
            margin-top: {spacing_value} !important;
            margin-bottom: {spacing_value} !important;
            font-weight: 600 !important;
            color: #1f2937 !important;
            letter-spacing: -0.02em !important;
        }
        h2, .stMarkdown h2 {
            margin-top: {spacing_value} !important;
            margin-bottom: {spacing_value} !important;
            font-weight: 600 !important;
            color: #1f2937 !important;
            letter-spacing: -0.02em !important;
        }
        h3, .stMarkdown h3 {
            margin-top: {spacing_value} !important;
            margin-bottom: {spacing_value} !important;
            font-weight: 600 !important;
            color: #374151 !important;
            letter-spacing: -0.01em !important;
        }
        h4, .stMarkdown h4 {
            margin-top: {spacing_value} !important;
            margin-bottom: {spacing_value} !important;
            font-weight: 600 !important;
            color: #4b5563 !important;
        }
        h5, .stMarkdown h5 {
            margin-top: {spacing_value} !important;
            margin-bottom: {spacing_value} !important;
            font-weight: 600 !important;
            color: #4b5563 !important;
        }
        h6, .stMarkdown h6 {
            margin-top: {spacing_value} !important;
            margin-bottom: {spacing_value} !important;
            font-weight: 500 !important;
            color: #6b7280 !important;
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
        
        /* 4. CONSISTENCY - Ultra-tight vertical spacing for form elements (0.5px) */
        [data-testid="stSelectbox"], 
        [data-testid="stTextInput"], 
        [data-testid="stTextArea"],
        [data-testid="stNumberInput"],
        [data-testid="stMultiselect"] {
            margin-top: {spacing_value} !important;
            margin-bottom: {spacing_value} !important;
        }
        
        /* 5. PROGRESSIVE DISCLOSURE - Ultra-tight vertical spacing for expanders (0.5px) */
        [data-testid="stExpander"] {
            border: 1px solid #e5e7eb !important;
            border-radius: 6px !important;
            margin-bottom: {spacing_value} !important;
            margin-top: {spacing_value} !important;
            background: #ffffff !important;
        }
        [data-testid="stExpander"]:hover {
            border-color: #d1d5db !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        }
        
        /* 6. METRICS - Ultra-tight vertical spacing (0.5px) */
        [data-testid="stMetric"] {
            margin-bottom: {spacing_value} !important;
            margin-top: {spacing_value} !important;
            padding: 4px 8px !important;
            background: #f9fafb !important;
            border-radius: 6px !important;
            border: 1px solid #e5e7eb !important;
        }
        
        /* 7. JSON/CODE - Ultra-tight vertical spacing (0.5px) */
        [data-testid="stJson"] {
            margin-top: {spacing_value} !important;
            margin-bottom: {spacing_value} !important;
            border-radius: 6px !important;
            border: 1px solid #e5e7eb !important;
            padding: 4px !important;
        }
        
        /* 8. RADIO - Ultra-tight vertical spacing (0.5px) */
        [data-testid="stRadio"] {
            margin-bottom: {spacing_value} !important;
            margin-top: {spacing_value} !important;
        }
        
        /* 9. MARKDOWN - Ultra-tight vertical spacing (0.5px) */
        [data-testid="stMarkdownContainer"] {
            margin-bottom: {spacing_value} !important;
            margin-top: 0 !important;
        }
        
        /* Ultra-tight paragraph vertical margins (0.5px) */
        .stMarkdown p,
        p {
            margin-top: 0 !important;
            margin-bottom: {spacing_value} !important;
        }
        
        /* 10. LOADING STATES - Better spinner visibility */
        [data-testid="stSpinner"] {
            color: #6b7280 !important;
        }
        
        /* 11. ALERTS - Ultra-tight vertical spacing (0.5px) */
        .stAlert {
            border-radius: 6px !important;
            border-left-width: 3px !important;
            padding: 4px 8px !important;
            margin-bottom: {spacing_value} !important;
            margin-top: {spacing_value} !important;
        }
        
        /* 12. TABLES - Better readability */
        [data-testid="stDataFrame"] {
            border-radius: 8px !important;
            overflow: hidden !important;
        }
        
        /* 13. EMPTY STATES - Ultra-tight vertical spacing (0.5px) */
        .empty-state-container {
            text-align: center !important;
            padding: 0.5rem !important;
            color: #6b7280 !important;
            margin: {spacing_value} 0 !important;
        }
        
        /* 14. MICRO-INTERACTIONS - Smooth transitions */
        * {
            transition: background-color 0.2s ease, border-color 0.2s ease !important;
        }
        
        /* 15. REMOVE EMPTY CONTAINERS - Compact UI - Keep only 1 standard spacing */
        /* Standard spacing: Keep first empty container, hide all subsequent duplicates */
        /* Hide empty element containers that come after another empty one (keep only 1) */
        [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty,
        [data-testid="stElementContainer"]:has(> :empty:only-child) + [data-testid="stElementContainer"]:has(> :empty:only-child),
        [data-testid="stElementContainer"]:has(> div:empty:only-child) + [data-testid="stElementContainer"]:has(> div:empty:only-child),
        .element-container:empty + .element-container:empty,
        .element-container:has(> :empty:only-child) + .element-container:has(> :empty:only-child) {
            display: none !important;
            margin: 0 !important;
            padding: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
        }
        
        /* Hide all empty containers after the first one in any sequence */
        [data-testid="stElementContainer"]:empty ~ [data-testid="stElementContainer"]:empty {
            display: none !important;
            margin: 0 !important;
            padding: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
        }
        
        /* Hide duplicate empty markdown containers - keep only 1 standard spacing */
        [data-testid="stMarkdownContainer"]:empty + [data-testid="stMarkdownContainer"]:empty,
        [data-testid="stMarkdownContainer"]:has(> :empty:only-child) + [data-testid="stMarkdownContainer"]:has(> :empty:only-child),
        [data-testid="stMarkdownContainer"]:has(> p:empty:only-child) + [data-testid="stMarkdownContainer"]:has(> p:empty:only-child),
        [data-testid="stMarkdownContainer"]:has(> div:empty:only-child) + [data-testid="stMarkdownContainer"]:has(> div:empty:only-child),
        [data-testid="stMarkdownContainer"]:empty ~ [data-testid="stMarkdownContainer"]:empty {
            display: none !important;
            margin: 0 !important;
            padding: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
        }
        
        /* Remove duplicate empty vertical blocks - keep only 1 standard spacing */
        .stVerticalBlock:empty + .stVerticalBlock:empty,
        .stVerticalBlock:has(> :empty:only-child) + .stVerticalBlock:has(> :empty:only-child),
        .stVerticalBlock:has(> [data-testid="stElementContainer"]:empty:only-child) + .stVerticalBlock:has(> [data-testid="stElementContainer"]:empty:only-child),
        [class*="stVerticalBlock"]:empty + [class*="stVerticalBlock"]:empty,
        .stVerticalBlock:empty ~ .stVerticalBlock:empty {
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
        
        /* Remove ALL consecutive empty containers - keep only 1 standard spacing */
        /* Hide all empty containers except the first one in a sequence */
        [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty,
        [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty,
        [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty,
        [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Remove empty containers between non-empty ones - keep only 1 standard spacing */
        [data-testid="stElementContainer"]:not(:empty) ~ [data-testid="stElementContainer"]:empty {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Hide all empty containers except the first in any sequence */
        [data-testid="stElementContainer"]:empty ~ [data-testid="stElementContainer"]:empty {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Standard spacing: Only allow 1 empty container between non-empty elements */
        [data-testid="stElementContainer"]:not(:empty) + [data-testid="stElementContainer"]:empty + [data-testid="stElementContainer"]:empty {
            display: none !important;
        }
        
        /* Hide multiple empty markdown containers - keep only 1 */
        [data-testid="stMarkdownContainer"]:empty + [data-testid="stMarkdownContainer"]:empty,
        [data-testid="stMarkdownContainer"]:empty + [data-testid="stMarkdownContainer"]:empty + [data-testid="stMarkdownContainer"]:empty {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Hide multiple empty vertical blocks - keep only 1 */
        .stVerticalBlock:empty + .stVerticalBlock:empty,
        .stVerticalBlock:empty + .stVerticalBlock:empty + .stVerticalBlock:empty {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
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
        
        /* Hide ALL empty containers with 8px height - aggressive removal */
        [data-testid="stElementContainer"][height="8px"],
        [data-testid="stElementContainer"]:has(> div[style*="height: 8px"]),
        [data-testid="stElementContainer"]:has(> div[style*="height:8px"]),
        .element-container[style*="height: 8px"],
        .element-container[style*="height:8px"],
        [data-testid="stElementContainer"][style*="height: 8px"],
        [data-testid="stElementContainer"][style*="height:8px"] {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            visibility: hidden !important;
        }
        
        /* Hide ALL empty element containers - no exceptions */
        [data-testid="stElementContainer"]:empty {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            visibility: hidden !important;
        }
        
        /* Hide empty containers that have only whitespace or invisible content */
        [data-testid="stElementContainer"]:has(> :empty:only-child),
        [data-testid="stElementContainer"]:has(> div:empty:only-child),
        [data-testid="stElementContainer"]:has(> span:empty:only-child),
        [data-testid="stElementContainer"]:has(> p:empty:only-child) {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Standard spacing: Keep only 1 empty container, hide all duplicates */
        /* Hide all empty containers that follow another empty container */
        [data-testid="stElementContainer"]:empty ~ [data-testid="stElementContainer"]:empty {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Hide all empty vertical blocks after the first one */
        .stVerticalBlock:empty ~ .stVerticalBlock:empty {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Hide ALL empty vertical blocks that contain only empty element containers */
        .stVerticalBlock:has(> [data-testid="stElementContainer"]:empty:only-child),
        .stVerticalBlock:has(> [data-testid="stElementContainer"]:empty) {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* AGGRESSIVE: Hide ALL containers with height 8px or less (including 4px) - regardless of content */
        [data-testid="stElementContainer"][style*="height: 8px"],
        [data-testid="stElementContainer"][style*="height:8px"],
        [data-testid="stElementContainer"][style*="height: 4px"],
        [data-testid="stElementContainer"][style*="height:4px"],
        [data-testid="stElementContainer"]:has(> div[style*="height: 8px"]),
        [data-testid="stElementContainer"]:has(> div[style*="height:8px"]),
        [data-testid="stElementContainer"]:has(> div[style*="height: 4px"]),
        [data-testid="stElementContainer"]:has(> div[style*="height:4px"]) {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            visibility: hidden !important;
        }
        
        /* STANDARD: Remove empty containers between section titles and content */
        /* Hide empty containers that appear immediately after headings */
        h1 + [data-testid="stElementContainer"]:empty,
        h2 + [data-testid="stElementContainer"]:empty,
        h3 + [data-testid="stElementContainer"]:empty,
        h4 + [data-testid="stElementContainer"]:empty,
        h5 + [data-testid="stElementContainer"]:empty,
        h6 + [data-testid="stElementContainer"]:empty,
        .stMarkdown h1 + [data-testid="stElementContainer"]:empty,
        .stMarkdown h2 + [data-testid="stElementContainer"]:empty,
        .stMarkdown h3 + [data-testid="stElementContainer"]:empty,
        .stMarkdown h4 + [data-testid="stElementContainer"]:empty,
        .stMarkdown h5 + [data-testid="stElementContainer"]:empty,
        .stMarkdown h6 + [data-testid="stElementContainer"]:empty,
        [data-testid="stMarkdownContainer"]:has(> h1) + [data-testid="stElementContainer"]:empty,
        [data-testid="stMarkdownContainer"]:has(> h2) + [data-testid="stElementContainer"]:empty,
        [data-testid="stMarkdownContainer"]:has(> h3) + [data-testid="stElementContainer"]:empty,
        [data-testid="stMarkdownContainer"]:has(> h4) + [data-testid="stElementContainer"]:empty,
        [data-testid="stMarkdownContainer"]:has(> h5) + [data-testid="stElementContainer"]:empty,
        [data-testid="stMarkdownContainer"]:has(> h6) + [data-testid="stElementContainer"]:empty {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Hide empty containers after markdown containers that contain headings */
        [data-testid="stMarkdownContainer"]:has(> h1) ~ [data-testid="stElementContainer"]:empty:first-of-type,
        [data-testid="stMarkdownContainer"]:has(> h2) ~ [data-testid="stElementContainer"]:empty:first-of-type,
        [data-testid="stMarkdownContainer"]:has(> h3) ~ [data-testid="stElementContainer"]:empty:first-of-type,
        [data-testid="stMarkdownContainer"]:has(> h4) ~ [data-testid="stElementContainer"]:empty:first-of-type,
        [data-testid="stMarkdownContainer"]:has(> h5) ~ [data-testid="stElementContainer"]:empty:first-of-type,
        [data-testid="stMarkdownContainer"]:has(> h6) ~ [data-testid="stElementContainer"]:empty:first-of-type {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Hide empty vertical blocks after headings */
        h1 + .stVerticalBlock:empty,
        h2 + .stVerticalBlock:empty,
        h3 + .stVerticalBlock:empty,
        h4 + .stVerticalBlock:empty,
        [data-testid="stMarkdownContainer"]:has(> h1) + .stVerticalBlock:empty,
        [data-testid="stMarkdownContainer"]:has(> h2) + .stVerticalBlock:empty,
        [data-testid="stMarkdownContainer"]:has(> h3) + .stVerticalBlock:empty,
        [data-testid="stMarkdownContainer"]:has(> h4) + .stVerticalBlock:empty {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Hide empty markdown containers after headings */
        h1 + [data-testid="stMarkdownContainer"]:empty,
        h2 + [data-testid="stMarkdownContainer"]:empty,
        h3 + [data-testid="stMarkdownContainer"]:empty,
        h4 + [data-testid="stMarkdownContainer"]:empty,
        [data-testid="stMarkdownContainer"]:has(> h1) + [data-testid="stMarkdownContainer"]:empty,
        [data-testid="stMarkdownContainer"]:has(> h2) + [data-testid="stMarkdownContainer"]:empty,
        [data-testid="stMarkdownContainer"]:has(> h3) + [data-testid="stMarkdownContainer"]:empty,
        [data-testid="stMarkdownContainer"]:has(> h4) + [data-testid="stMarkdownContainer"]:empty {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Ultra-compact: Remove all margins between headings and content */
        h1, h2, h3, h4, h5, h6,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            margin-bottom: 2px !important;
            margin-top: 4px !important;
        }
        
        /* Remove all spacing between sections */
        .stVerticalBlock {
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Ultra-compact: Remove all default margins and padding */
        * {
            margin-top: 0 !important;
        }
        
        /* Minimal bottom margins for visual separation (2px minimum for proper rendering) */
        div[data-testid="stElementContainer"]:not(:empty) {
            margin-bottom: 2px !important;
        }
        
        /* Ultra-minimal spacing for tabs - reduce gap after tabs to almost zero */
        .stTabs {
            margin-bottom: 0 !important;
            margin-top: 4px !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 6px 12px !important;
            margin: 0 2px !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px !important;
            padding: 4px !important;
            margin-bottom: 0 !important;
        }
        
        /* Remove spacing between tabs and content that follows */
        .stTabs ~ div,
        .stTabs + div,
        .stTabs + [data-testid="stElementContainer"],
        .stTabs ~ [data-testid="stElementContainer"],
        .stTabs ~ [data-testid="stVerticalBlock"] {
            margin-top: 0 !important;
        }
        
        /* Remove spacing after tab panel content */
        [data-baseweb="tab-panel"] {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        [data-baseweb="tab-panel"] > div {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        /* Minimal vertical spacing for headings that come after tabs (2px minimum for proper rendering) */
        .stTabs ~ h1,
        .stTabs ~ h2,
        .stTabs ~ h3,
        .stTabs ~ h4,
        .stTabs ~ h5,
        .stTabs ~ h6,
        .stTabs ~ .stMarkdown h1,
        .stTabs ~ .stMarkdown h2,
        .stTabs ~ .stMarkdown h3,
        .stTabs ~ .stMarkdown h4 {
            margin-top: 2px !important;
        }
        
        /* Minimal vertical spacing for headings in tab panels (2px minimum for proper rendering) */
        [data-baseweb="tab-panel"] h1,
        [data-baseweb="tab-panel"] h2,
        [data-baseweb="tab-panel"] h3,
        [data-baseweb="tab-panel"] h4 {
            margin-top: 2px !important;
        }
        
        /* Minimal vertical spacing for first element in tab panel (2px minimum for proper rendering) */
        [data-baseweb="tab-panel"] > *:first-child {
            margin-top: 2px !important;
            padding-top: 0 !important;
        }
        
        /* SPECIFIC: Downloads tab - ultra-minimal spacing */
        /* Target elements with "Downloads & Outputs" text and reduce spacing */
        div[style*="margin-bottom: 0.5rem"]:has(h2),
        div:has(> h2[style*="Downloads & Outputs"]) {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
        }
        
        /* Remove spacing from h2 with Downloads & Outputs */
        h2[style*="Downloads & Outputs"],
        h2:has-text("Downloads & Outputs") {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
        }
        
        /* Remove spacing after Downloads heading - target next sibling tabs */
        div:has(> h2[style*="Downloads & Outputs"]) + .stTabs,
        div:has(> h2[style*="Downloads & Outputs"]) ~ .stTabs {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }
        
        /* Minimal vertical spacing in Downloads tab panels (2px minimum for proper rendering) */
        .stTabs [data-baseweb="tab-panel"] {
            margin-top: 2px !important;
            padding-top: 0 !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] > div {
            margin-top: 2px !important;
            padding-top: 0 !important;
        }
        
        /* Minimal vertical spacing from headings in Downloads tab panels (2px minimum for proper rendering) */
        .stTabs [data-baseweb="tab-panel"] h3,
        .stTabs [data-baseweb="tab-panel"] h4 {
            margin-top: 2px !important;
            margin-bottom: 2px !important;
        }
        
        /* Minimal vertical spacing from expanders in Downloads tab (2px minimum for proper rendering) */
        .stTabs [data-baseweb="tab-panel"] [data-testid="stExpander"] {
            margin-top: 2px !important;
            margin-bottom: 2px !important;
        }
        
        /* Minimal vertical spacing from markdown in Downloads tab (2px minimum for proper rendering) */
        .stTabs [data-baseweb="tab-panel"] .stMarkdown {
            margin-top: 2px !important;
            margin-bottom: 2px !important;
        }
        
        /* Minimal vertical spacing from containers in Downloads tab (2px minimum for proper rendering) */
        .stTabs [data-baseweb="tab-panel"] [data-testid="stElementContainer"] {
            margin-top: 2px !important;
            margin-bottom: 2px !important;
        }
        
        /* Minimal vertical spacing for expander headers (2px minimum for proper rendering) */
        .streamlit-expanderHeader {
            padding: 4px 8px !important;
            margin-bottom: 2px !important;
            margin-top: 2px !important;
        }
        
        /* Minimal vertical spacing for expander content (2px minimum for proper rendering) */
        .streamlit-expanderContent {
            padding: 4px 8px !important;
            margin-top: 0 !important;
            margin-bottom: 2px !important;
        }
        
        /* Minimal vertical spacing for buttons (2px minimum for proper rendering) */
        [data-testid="stButton"] {
            margin-bottom: 2px !important;
            margin-top: 2px !important;
        }
        
        /* Minimal vertical spacing for file uploaders (2px minimum for proper rendering) */
        [data-testid="stFileUploader"] {
            margin-bottom: 2px !important;
            margin-top: 2px !important;
            padding: 4px !important;
        }
        
        /* Minimal vertical spacing for dataframes (2px minimum for proper rendering) */
        [data-testid="stDataFrame"] {
            margin-bottom: 2px !important;
            margin-top: 2px !important;
        }
        
        /* Keep horizontal gaps in columns, only reduce vertical (0.5px) */
        [data-testid="column"] {
            gap: 0.5rem !important;
            padding: 0.5rem 0.5rem !important;
        }
        
        /* ULTRA-COMPACT: Remove ALL empty spaces - aggressive cleanup */
        /* Hide any container with height <= 8px (including 4px) that appears empty */
        [data-testid="stElementContainer"]:empty,
        [data-testid="stElementContainer"]:has(> :empty:only-child),
        [data-testid="stElementContainer"]:has(> div:empty:only-child),
        [data-testid="stElementContainer"]:has(> span:empty:only-child),
        [data-testid="stElementContainer"]:has(> p:empty:only-child) {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            visibility: hidden !important;
        }
        
        /* Hide containers with height 4px specifically */
        [data-testid="stElementContainer"][style*="height: 4px"],
        [data-testid="stElementContainer"][style*="height:4px"] {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Minimal vertical spacing for vertical blocks (2px minimum for proper rendering) */
        .stVerticalBlock {
            margin: 2px 0 !important;
            padding: 0 !important;
        }
        
        /* Minimal vertical spacing for markdown containers (2px minimum for proper rendering) */
        [data-testid="stMarkdownContainer"] {
            margin: 2px 0 !important;
            padding: 0 !important;
        }
        
        /* Minimal vertical padding from Streamlit components (2px minimum for proper rendering) */
        .main .block-container {
            padding-top: 2px !important;
            padding-bottom: 2px !important;
        }
        
        /* Minimal vertical spacing between tabs and content (2px minimum for proper rendering) */
        .stTabs ~ div,
        .stTabs ~ [data-testid="stElementContainer"],
        .stTabs ~ [data-testid="stVerticalBlock"] {
            margin-top: 2px !important;
        }
        
        /* Minimal vertical spacing in tab panels (2px minimum for proper rendering) */
        [data-baseweb="tab-panel"] {
            margin-top: 2px !important;
            padding-top: 0 !important;
        }
        
        [data-baseweb="tab-panel"] > div {
            margin-top: 2px !important;
            padding-top: 0 !important;
        }
        
        [data-baseweb="tab-panel"] > *:first-child {
            margin-top: 2px !important;
            padding-top: 0 !important;
        }
        
        /* Consistent line-height spacing */
        p, div, span {
            line-height: 1.3 !important;
        }
        
        /* Minimal vertical spacing for all sections (2px minimum for proper rendering) */
        section,
        .main > div,
        .block-container > div {
            margin-top: 2px !important;
            margin-bottom: 2px !important;
        }
        
        /* Minimal vertical spacing for all content blocks (2px minimum for proper rendering) */
        [data-testid="stElementContainer"]:not(:empty) {
            margin-top: 2px !important;
            margin-bottom: 2px !important;
        }
        
        /* Minimal vertical spacing between titles and their content (2px minimum for proper rendering) */
        h1 + *,
        h2 + *,
        h3 + *,
        h4 + * {
            margin-top: 2px !important;
        }
        
        /* Ultra-compact table spacing */
        table {
            border-spacing: 0 !important;
            border-collapse: collapse !important;
        }
        
        /* Remove all unnecessary whitespace */
        br {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # JavaScript-based removal of 8px containers as fallback
    # This will run after page load to catch any containers missed by CSS
    st.markdown("""
        <script>
        (function() {
            function remove8pxContainers() {
                const containers = document.querySelectorAll('[data-testid="stElementContainer"]');
                containers.forEach(container => {
                    const rect = container.getBoundingClientRect();
                    // Remove ALL containers that are 8px or less (including 4px) and appear empty
                    if (rect.height <= 8 && rect.height > 0) {
                        const hasVisibleContent = container.textContent.trim() !== '' || 
                                                  container.querySelector('button, input, select, textarea, [data-testid*="st"], iframe, img, svg, canvas, video, audio, hr, table, tr, td, th');
                        if (!hasVisibleContent) {
                            container.style.display = 'none';
                            container.style.height = '0';
                            container.style.margin = '0';
                            container.style.padding = '0';
                            container.style.visibility = 'hidden';
                            container.style.minHeight = '0';
                            container.style.maxHeight = '0';
                        }
                    }
                    // Also remove any empty containers regardless of height
                    if (container.children.length === 0 && container.textContent.trim() === '') {
                        container.style.display = 'none';
                        container.style.height = '0';
                        container.style.margin = '0';
                        container.style.padding = '0';
                    }
                });
                
                // Remove empty vertical blocks (including 4px ones)
                const verticalBlocks = document.querySelectorAll('.stVerticalBlock');
                verticalBlocks.forEach(block => {
                    const rect = block.getBoundingClientRect();
                    if (rect.height <= 8 && rect.height > 0 && block.children.length === 0) {
                        block.style.display = 'none';
                        block.style.height = '0';
                        block.style.margin = '0';
                        block.style.padding = '0';
                    }
                });
            }
            // Run immediately and after delays to catch dynamically added containers
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', remove8pxContainers);
            } else {
                remove8pxContainers();
            }
            setTimeout(remove8pxContainers, 100);
            setTimeout(remove8pxContainers, 500);
            setTimeout(remove8pxContainers, 1000);
            // Also run on mutations to catch dynamically added containers
            const observer = new MutationObserver(function(mutations) {
                remove8pxContainers();
            });
            if (document.body) {
                observer.observe(document.body, { childList: true, subtree: true });
            }
        })();
        </script>
    """, unsafe_allow_html=True)


def inject_unified_design_system(
    font_family: str = "Arial, sans-serif",
    font_size: str = "13px",
    spacing_value: str = "0.5px"
):
    """Inject unified design system CSS following UI/UX golden rules.
    
    Args:
        font_family: Font family to use (e.g., "Arial, sans-serif", "Georgia, serif")
        font_size: Base font size (e.g., "13px", "14px")
        spacing_value: Vertical spacing value in px (e.g., "0.5px", "2px")
    """
    tokens = DesignTokens
    
    st.markdown(f"""
    <style>
    /* ============================================
       UNIFIED DESIGN SYSTEM - GOLDEN RULES
       ============================================ */
    
    /* 1. TYPOGRAPHY - Consistent Font Sizes */
    /* Base font size for all text */
    body, .main, .stMarkdown, p, div, span, label {{
        font-family: {font_family} !important;
        font-size: {font_size} !important;
        line-height: 1.5 !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    /* Heading Hierarchy - Dynamic vertical spacing */
    h1, .stMarkdown h1 {{
        font-family: {font_family} !important;
        font-size: {tokens.FONT_SIZES['3xl']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        line-height: 1.2 !important;
        margin-top: {spacing_value} !important;
        margin-bottom: {spacing_value} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    h2, .stMarkdown h2 {{
        font-family: {font_family} !important;
        font-size: {tokens.FONT_SIZES['2xl']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        line-height: 1.3 !important;
        margin-top: {spacing_value} !important;
        margin-bottom: {spacing_value} !important;
        color: {tokens.COLORS['text']} !important;
        border-bottom: 1px solid {tokens.COLORS['border-light']} !important;
        padding-bottom: {tokens.SPACING['xs']} !important;
    }}
    
    h3, .stMarkdown h3 {{
        font-family: {font_family} !important;
        font-size: {tokens.FONT_SIZES['xl']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        line-height: 1.4 !important;
        margin-top: {spacing_value} !important;
        margin-bottom: {spacing_value} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    h4, .stMarkdown h4 {{
        font-family: {font_family} !important;
        font-size: {tokens.FONT_SIZES['lg']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        line-height: 1.4 !important;
        margin-top: {spacing_value} !important;
        margin-bottom: {spacing_value} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    h5, .stMarkdown h5 {{
        font-family: {font_family} !important;
        font-size: {tokens.FONT_SIZES['md']} !important;
        font-weight: {tokens.FONT_WEIGHTS['medium']} !important;
        line-height: 1.4 !important;
        margin-top: {spacing_value} !important;
        margin-bottom: {spacing_value} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    h6, .stMarkdown h6 {{
        font-family: {font_family} !important;
        font-size: {tokens.FONT_SIZES['sm']} !important;
        font-weight: {tokens.FONT_WEIGHTS['medium']} !important;
        line-height: 1.4 !important;
        margin-top: {spacing_value} !important;
        margin-bottom: {spacing_value} !important;
        color: {tokens.COLORS['text-muted']} !important;
    }}
    
    /* Captions and small text - Dynamic vertical spacing */
    .stCaption, small, .caption {{
        font-family: {font_family} !important;
        font-size: {tokens.FONT_SIZES['xs']} !important;
        color: {tokens.COLORS['text-muted']} !important;
        line-height: 1.4 !important;
        margin-top: {spacing_value} !important;
        margin-bottom: {spacing_value} !important;
    }}
    
    /* 2. CONTAINER SIZES - Ultra-compact Layout */
    .main .block-container {{
        max-width: {tokens.CONTAINERS['2xl']} !important;
        padding-top: {tokens.SPACING['sm']} !important;
        padding-bottom: {tokens.SPACING['sm']} !important;
        padding-left: {tokens.SPACING['sm']} !important;
        padding-right: {tokens.SPACING['sm']} !important;
    }}
    
    /* 3. SPACING - Dynamic vertical spacing */
    /* Minimal vertical margins between elements */
    .element-container {{
        margin-bottom: {spacing_value} !important;
        margin-top: 0 !important;
    }}
    
    /* Keep horizontal padding, dynamic vertical margins */
    .stContainer {{
        padding: 0.5rem !important;
        margin-bottom: {spacing_value} !important;
        margin-top: {spacing_value} !important;
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
    
    /* 6. ALERTS - Ultra-tight vertical spacing (0.5px) */
    .stAlert {{
        padding: {tokens.SPACING['xs']} {tokens.SPACING['sm']} !important;
        margin-bottom: {spacing_value} !important;
        margin-top: {spacing_value} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        border-left: 3px solid !important;
        font-size: {tokens.FONT_SIZES['base']} !important;
        line-height: 1.4 !important;
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
    
    /* 7. EXPANDERS - Ultra-tight vertical spacing (0.5px) */
    .streamlit-expanderHeader {{
        padding: {tokens.SPACING['xs']} {tokens.SPACING['sm']} !important;
        font-size: {tokens.FONT_SIZES['base']} !important;
        font-weight: {tokens.FONT_WEIGHTS['medium']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        background-color: {tokens.COLORS['background-alt']} !important;
        border: 1px solid {tokens.COLORS['border-light']} !important;
        margin-bottom: {spacing_value} !important;
        margin-top: {spacing_value} !important;
    }}
    
    .streamlit-expanderContent {{
        padding: {tokens.SPACING['xs']} {tokens.SPACING['sm']} !important;
        background-color: {tokens.COLORS['background']} !important;
        border: 1px solid {tokens.COLORS['border-light']} !important;
        border-top: none !important;
        border-radius: 0 0 {tokens.RADIUS['md']} {tokens.RADIUS['md']} !important;
        margin-bottom: {spacing_value} !important;
    }}
    
    /* 8. DATA TABLES - Ultra-tight vertical spacing (0.5px) */
    .stDataFrame {{
        margin-bottom: {spacing_value} !important;
        margin-top: {spacing_value} !important;
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
        padding: {tokens.SPACING['xs']} {tokens.SPACING['sm']} !important;
        border-bottom: 2px solid {tokens.COLORS['border']} !important;
    }}
    
    .stDataFrame td {{
        padding: {tokens.SPACING['xs']} {tokens.SPACING['sm']} !important;
        border-bottom: 1px solid {tokens.COLORS['border-light']} !important;
        font-size: {tokens.FONT_SIZES['sm']} !important;
    }}
    
    .stDataFrame tr:hover {{
        background-color: {tokens.COLORS['background-hover']} !important;
    }}
    
    /* 9. METRICS - Ultra-tight vertical spacing (0.5px) */
    [data-testid="stMetricContainer"] {{
        padding: {tokens.SPACING['xs']} {tokens.SPACING['sm']} !important;
        margin-bottom: {spacing_value} !important;
        margin-top: {spacing_value} !important;
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
    
    /* 10. TABS - Ultra-tight vertical spacing (0.5px) */
    .stTabs [data-baseweb="tab-list"] {{
        gap: {tokens.SPACING['sm']} !important;
        background-color: {tokens.COLORS['background-alt']} !important;
        padding: {tokens.SPACING['sm']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        margin-bottom: {spacing_value} !important;
        margin-top: {tokens.SPACING['xs']} !important;
    }}
    
    /* Ultra-tight vertical spacing for tab panel content (0.5px) */
    .stTabs [data-baseweb="tab-panel"] {{
        margin-top: {spacing_value} !important;
        padding-top: 0 !important;
    }}
    
    .stTabs [data-baseweb="tab-panel"] > div {{
        margin-top: {spacing_value} !important;
        padding-top: 0 !important;
    }}
    
    .stTabs [data-baseweb="tab-panel"] > *:first-child {{
        margin-top: {spacing_value} !important;
        padding-top: 0 !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        padding: {tokens.SPACING['sm']} {tokens.SPACING['md']} !important;
        font-size: {tokens.FONT_SIZES['base']} !important;
        font-weight: {tokens.FONT_WEIGHTS['medium']} !important;
        border-radius: {tokens.RADIUS['sm']} !important;
        color: {tokens.COLORS['text']} !important;
        transition: all 0.2s ease !important;
        margin: 0 {tokens.SPACING['xs']} !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {tokens.COLORS['background']} !important;
        color: {tokens.COLORS['text']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        box-shadow: {tokens.SHADOWS['sm']} !important;
        border-bottom: 2px solid {tokens.COLORS['primary']} !important;
    }}
    
    /* 11. FILE UPLOADERS - Ultra-tight vertical spacing (0.5px) */
    .stFileUploader {{
        border: 2px dashed {tokens.COLORS['border']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        padding: {tokens.SPACING['sm']} !important;
        background-color: {tokens.COLORS['background-alt']} !important;
        margin-bottom: {spacing_value} !important;
        margin-top: {spacing_value} !important;
        min-height: 100px !important;
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
    
    /* 12. SUMMARY CARDS - Ultra-tight vertical spacing (0.5px) */
    .summary-cards-wrapper [data-testid="column"] {{
        background: {tokens.COLORS['background']} !important;
        border: 1px solid {tokens.COLORS['border-light']} !important;
        border-radius: {tokens.RADIUS['lg']} !important;
        padding: {tokens.SPACING['sm']} !important;
        box-shadow: {tokens.SHADOWS['sm']} !important;
        margin-bottom: {spacing_value} !important;
        margin-top: {spacing_value} !important;
        min-height: auto !important;
    }}
    
    .summary-cards-wrapper h4 {{
        font-size: {tokens.FONT_SIZES['lg']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        margin-top: 0 !important;
        margin-bottom: {spacing_value} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    .summary-cards-wrapper .stMarkdown p {{
        font-size: {tokens.FONT_SIZES['base']} !important;
        line-height: 1.4 !important;
        margin-bottom: {spacing_value} !important;
        margin-top: 0 !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    /* 13. FORMS - Ultra-tight vertical spacing (0.5px) */
    .stForm {{
        padding: {tokens.SPACING['xs']} {tokens.SPACING['sm']} !important;
        margin-bottom: {spacing_value} !important;
        margin-top: {spacing_value} !important;
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
    
    /* 16. DIVIDERS - Ultra-tight vertical spacing (0.5px) */
    hr {{
        border: none !important;
        border-top: 1px solid {tokens.COLORS['border-light']} !important;
        margin: {spacing_value} 0 !important;
    }}
    
    /* 17. COLUMNS - Keep horizontal gap, reduce vertical spacing (0.5px) */
    [data-testid="column"] {{
        gap: 0.5rem !important;
        padding: 0.5rem !important;
    }}
    
    /* 18. CHECKBOXES & RADIOS - Ultra-tight vertical spacing (0.5px) */
    .stCheckbox, .stRadio {{
        margin-bottom: {spacing_value} !important;
        margin-top: {spacing_value} !important;
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
    
    /* 27. ULTRA-TIGHT MARKDOWN VERTICAL SPACING (0.5px) */
    .stMarkdown {{
        margin-bottom: {spacing_value} !important;
        margin-top: {spacing_value} !important;
    }}
    
    .stMarkdown p {{
        margin-bottom: {spacing_value} !important;
        margin-top: 0 !important;
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
    
    /* 31. ULTRA-TIGHT VERTICAL SPACING FOR ALL SECTIONS (0.5px) */
    /* Apply 0.5px vertical spacing to all main content areas */
    .main .block-container > div,
    .main .block-container > section {{
        margin-top: {spacing_value} !important;
        margin-bottom: {spacing_value} !important;
    }}
    
    /* Ultra-tight vertical spacing for all content blocks */
    [data-testid="stElementContainer"]:not(:empty) {{
        margin-top: {spacing_value} !important;
        margin-bottom: {spacing_value} !important;
    }}
    
    /* Ultra-tight vertical spacing between titles and their content */
    h1 + *,
    h2 + *,
    h3 + *,
    h4 + *,
    h5 + *,
    h6 + * {{
        margin-top: {spacing_value} !important;
    }}
    
    /* Ultra-tight vertical spacing for all Streamlit components */
    [data-testid="stSelectbox"],
    [data-testid="stTextInput"],
    [data-testid="stTextArea"],
    [data-testid="stNumberInput"],
    [data-testid="stMultiselect"],
    [data-testid="stCheckbox"],
    [data-testid="stRadio"],
    [data-testid="stButton"],
    [data-testid="stDownloadButton"] {{
        margin-top: {spacing_value} !important;
        margin-bottom: {spacing_value} !important;
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
    # Extract values to avoid nested quotes in f-strings
    radius_md = tokens.RADIUS['md']
    font_weight_semibold = tokens.FONT_WEIGHTS['semibold']
    font_size_base = tokens.FONT_SIZES['base']
    font_size_sm = tokens.FONT_SIZES['sm']
    
    card_html = f"""
    <div style='
        background: {style['bg']};
        border-left: 4px solid {style['border']};
        border-radius: {radius_md};
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    '>
        <div style='
            font-weight: {font_weight_semibold};
            color: {style['text']};
            font-size: {font_size_base};
            margin-bottom: 0.25rem;
        '>{icon_text}{title}</div>
        <div style='
            color: {style['text']};
            font-size: {font_size_sm};
            line-height: 1.5;
        '>{content}</div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

