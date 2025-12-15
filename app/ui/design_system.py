"""Unified Design System - Golden Rules of UI/UX."""
import streamlit as st
from typing import Any

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
    
    # Spacing Scale (8px grid system)
    SPACING = {
        'xs': '4px',       # 0.5 * 8px
        'sm': '8px',       # 1 * 8px
        'md': '16px',      # 2 * 8px
        'lg': '24px',      # 3 * 8px
        'xl': '32px',      # 4 * 8px
        '2xl': '40px',     # 5 * 8px
        '3xl': '48px',     # 6 * 8px
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
    
    # Colors (neutral, professional palette)
    COLORS = {
        'primary': '#495057',      # Primary actions
        'primary-hover': '#343a40',
        'secondary': '#6c757d',    # Secondary actions
        'secondary-hover': '#5a6268',
        'text': '#212529',         # Main text
        'text-muted': '#6c757d',   # Muted text
        'text-light': '#adb5bd',   # Light text
        'border': '#dee2e6',       # Borders
        'border-light': '#e9ecef', # Light borders
        'background': '#ffffff',   # Main background
        'background-alt': '#f8f9fa', # Alternate background
        'background-hover': '#f1f3f5', # Hover states
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107',
        'info': '#6b7280',         # Neutral grey for info
    }
    
    # Shadows (consistent elevation)
    SHADOWS = {
        'none': 'none',
        'sm': '0 1px 2px rgba(0,0,0,0.05)',
        'md': '0 2px 4px rgba(0,0,0,0.1)',
        'lg': '0 4px 8px rgba(0,0,0,0.1)',
        'xl': '0 8px 16px rgba(0,0,0,0.15)',
    }


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
        margin-top: {tokens.SPACING['lg']} !important;
        margin-bottom: {tokens.SPACING['md']} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    h2, .stMarkdown h2 {{
        font-size: {tokens.FONT_SIZES['2xl']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        line-height: 1.3 !important;
        margin-top: {tokens.SPACING['xl']} !important;
        margin-bottom: {tokens.SPACING['md']} !important;
        color: {tokens.COLORS['text']} !important;
        border-bottom: 1px solid {tokens.COLORS['border-light']} !important;
        padding-bottom: {tokens.SPACING['sm']} !important;
    }}
    
    h3, .stMarkdown h3 {{
        font-size: {tokens.FONT_SIZES['xl']} !important;
        font-weight: {tokens.FONT_WEIGHTS['semibold']} !important;
        line-height: 1.4 !important;
        margin-top: {tokens.SPACING['lg']} !important;
        margin-bottom: {tokens.SPACING['sm']} !important;
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
        padding-top: {tokens.SPACING['lg']} !important;
        padding-bottom: {tokens.SPACING['lg']} !important;
        padding-left: {tokens.SPACING['lg']} !important;
        padding-right: {tokens.SPACING['lg']} !important;
    }}
    
    /* 3. SPACING - 8px Grid System */
    /* Consistent margins between elements */
    .element-container {{
        margin-bottom: {tokens.SPACING['md']} !important;
    }}
    
    /* Consistent padding in containers */
    .stContainer {{
        padding: {tokens.SPACING['md']} !important;
        margin-bottom: {tokens.SPACING['md']} !important;
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
        padding: {tokens.SPACING['md']} !important;
        margin-bottom: {tokens.SPACING['md']} !important;
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
        background-color: #fffbf0 !important;
        border-left-color: {tokens.COLORS['warning']} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    .stError {{
        background-color: #fff5f5 !important;
        border-left-color: {tokens.COLORS['error']} !important;
        color: {tokens.COLORS['text']} !important;
    }}
    
    /* 7. EXPANDERS - Consistent Sizing */
    .streamlit-expanderHeader {{
        padding: {tokens.SPACING['sm']} {tokens.SPACING['md']} !important;
        font-size: {tokens.FONT_SIZES['base']} !important;
        font-weight: {tokens.FONT_WEIGHTS['medium']} !important;
        border-radius: {tokens.RADIUS['md']} !important;
        background-color: {tokens.COLORS['background-alt']} !important;
        border: 1px solid {tokens.COLORS['border-light']} !important;
        margin-bottom: {tokens.SPACING['xs']} !important;
    }}
    
    .streamlit-expanderContent {{
        padding: {tokens.SPACING['md']} !important;
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
        padding: {tokens.SPACING['lg']} !important;
        box-shadow: {tokens.SHADOWS['sm']} !important;
        margin-bottom: {tokens.SPACING['md']} !important;
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
        padding: {tokens.SPACING['lg']} !important;
        margin-bottom: {tokens.SPACING['md']} !important;
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
        margin: {tokens.SPACING['lg']} 0 !important;
    }}
    
    /* 17. COLUMNS - Consistent Gaps */
    [data-testid="column"] {{
        gap: {tokens.SPACING['md']} !important;
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

