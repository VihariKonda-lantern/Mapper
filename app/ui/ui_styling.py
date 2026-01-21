# --- ui_styling.py ---
"""UI styling and JavaScript injection functions."""
import streamlit as st
from typing import Any

st: Any = st


def inject_summary_card_css():
    """Inject CSS for modern, symmetrical summary cards and all UX enhancements."""
    st.markdown("""
    <style>
    /* Modern Page Styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Modern Headings */
    h1, h2, h3 {
        color: #1f2937 !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    h2 {
        font-size: 1.75rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }
    
    h3 {
        font-size: 1.5rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    /* Modern Expanders */
    .streamlit-expanderHeader {
        background-color: #f9fafb !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        border: 1px solid #e5e7eb !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #f3f4f6 !important;
        border-color: #d1d5db !important;
    }
    
    .streamlit-expanderContent {
        padding: 1rem !important;
        background-color: #ffffff !important;
        border-radius: 0 0 8px 8px !important;
        border: 1px solid #e5e7eb !important;
        border-top: none !important;
    }
    
    /* Modern Buttons - All Grey with White Text */
    .stButton > button,
    button[data-baseweb="button"],
    .stDownloadButton > button,
    button[type="button"],
    button[type="submit"] {
        background-color: #6b7280 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }
    
    .stButton > button:hover,
    button[data-baseweb="button"]:hover,
    .stDownloadButton > button:hover,
    button[type="button"]:hover,
    button[type="submit"]:hover {
        background-color: #4b5563 !important;
        color: white !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        transform: translateY(-1px);
    }
    
    .stButton > button:disabled,
    button[data-baseweb="button"]:disabled,
    .stDownloadButton > button:disabled,
    button[type="button"]:disabled,
    button[type="submit"]:disabled {
        background-color: #9ca3af !important;
        color: white !important;
        cursor: not-allowed !important;
        opacity: 0.6 !important;
    }
    
    /* Form Submit Buttons */
    .stForm > div > button {
        background-color: #6b7280 !important;
        color: white !important;
    }
    
    .stForm > div > button:hover {
        background-color: #4b5563 !important;
        color: white !important;
    }
    
    /* Primary buttons (type="primary") - also grey */
    .stButton > button[kind="primary"],
    button[kind="primary"],
    button[data-baseweb="button"][kind="primary"] {
        background-color: #6b7280 !important;
        color: white !important;
    }
    
    .stButton > button[kind="primary"]:hover,
    button[kind="primary"]:hover,
    button[data-baseweb="button"][kind="primary"]:hover {
        background-color: #4b5563 !important;
        color: white !important;
    }
    
    /* Modern Input Fields */
    .stTextInput > div > div > input {
        border-radius: 6px !important;
        border: 1px solid #d1d5db !important;
        padding: 0.5rem 0.75rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6b7280 !important;
        box-shadow: 0 0 0 3px rgba(107, 114, 128, 0.1) !important;
        outline: none !important;
    }
    
    /* Modern Selectbox */
    .stSelectbox > div > div {
        border-radius: 6px !important;
        border: 1px solid #d1d5db !important;
    }
    
    /* Modern Progress Bar Container */
    div[style*="position: sticky"] {
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    
    /* Modern Dataframes */
    .stDataFrame {
        border-radius: 8px !important;
        overflow: hidden !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }
    
    /* Modern Forms */
    .stForm {
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
        background-color: #f9fafb !important;
    }
    
    /* Force columns to display side by side - prevent wrapping */
    .upload-columns-container {
        display: flex !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        gap: 1rem !important;
    }
    
    .upload-columns-container ~ div [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        flex: 1 1 0 !important;
        min-width: 0 !important;
        max-width: 100% !important;
    }
    
    /* Ensure columns display side by side */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        flex: 1 1 0 !important;
        min-width: 0 !important;
        max-width: 100% !important;
    }
    
    /* Ensure columns have equal heights for file uploaders */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        padding: 0.5rem !important;
        min-height: 120px !important;
    }
    
    /* Center and constrain upload columns container */
    .upload-columns-container {
        max-width: 70% !important;
        margin: 0 auto !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    .upload-columns-container [data-testid="column"] {
        flex: 1 1 0 !important;
        max-width: 100% !important;
    }
    
    /* Make all file uploaders the same size */
    [data-testid="column"] .stFileUploader {
        flex: 1 !important;
        min-height: 120px !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    
    /* Prevent file uploaders from breaking column layout */
    .stFileUploader {
        border: 2px dashed #d1d5db !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        background-color: #f9fafb !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        box-sizing: border-box !important;
        min-width: 0 !important;
        min-height: 120px !important;
    }
    
    .stFileUploader:hover {
        border-color: #6b7280 !important;
        background-color: #f3f4f6 !important;
    }
    
    /* Ensure file uploader inner content is centered */
    .stFileUploader > div {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        min-height: 80px !important;
        height: 100% !important;
    }
    
    /* Hide file size limit and file type text in uploaders - be specific to avoid hiding labels */
    .stFileUploader small {
        display: none !important;
    }
    
    /* Ensure labels are always visible */
    .stFileUploader label {
        display: block !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Hide markdown containers that contain file size/type info, but preserve label containers */
    .stFileUploader [data-testid="stMarkdownContainer"] {
        /* Will be handled by JavaScript to check content */
    }
    
    /* Hide any text containing file size or type info using more aggressive selectors */
    .stFileUploader * {
        font-size: inherit;
    }
    
    /* Ensure file uploader labels and content fit properly */
    [data-testid="column"] .stFileUploader label,
    .stFileUploader label {
        font-size: 0.9rem !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        text-align: center !important;
        margin-bottom: 0.5rem !important;
        display: block !important;
        font-weight: 500 !important;
    }
    
    /* Ensure label containers are visible */
    .stFileUploader [data-testid="stMarkdownContainer"]:has(label),
    .stFileUploader > div:has(label) {
        display: block !important;
    }
    
    /* Ensure file uploader containers don't overflow */
    [data-testid="column"] > div {
        width: 100% !important;
        min-width: 0 !important;
        overflow: hidden !important;
        flex: 1 !important;
        display: flex !important;
        flex-direction: column !important;
    }
    
    /* Make file uploader drag area consistent */
    .stFileUploader [data-baseweb="file-uploader"] {
        width: 100% !important;
        min-height: 80px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Modern Alerts/Info Boxes */
    .stAlert {
        border-radius: 8px !important;
        border-left: 4px solid !important;
        padding: 1rem !important;
    }
    
    /* Info boxes - grey instead of blue */
    .stInfo {
        background-color: #f3f4f6 !important;
        border-left-color: #6b7280 !important;
    }
    
    .stInfo > div {
        color: #1f2937 !important;
    }
    
    /* Override Streamlit's default notification/alert boxes */
    div[data-baseweb="notification"] {
        background-color: #f3f4f6 !important;
    }
    
    /* Info alert boxes specifically - grey */
    div[data-baseweb="notification"][data-kind="info"],
    div[data-baseweb="notification"].stAlert[data-baseweb="notification"] {
        background-color: #f3f4f6 !important;
        border-left-color: #6b7280 !important;
    }
    
    /* Ensure all info boxes have grey text */
    .stInfo p,
    .stInfo div,
    .stInfo span,
    div[data-baseweb="notification"][data-kind="info"] p,
    div[data-baseweb="notification"][data-kind="info"] div {
        color: #1f2937 !important;
    }
    
    /* Style summary cards wrapper - target all columns */
    .summary-cards-wrapper [data-testid="column"] {
        background: white;
        border-radius: 12px;
        padding: 1.5rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e8e8e8;
        min-height: 450px;
        display: flex;
        flex-direction: column;
        transition: all 0.3s ease;
    }
    
    /* Ensure equal heights using flexbox */
    .summary-cards-wrapper [data-testid="column"] > div {{
        display: flex;
        flex-direction: column;
        flex: 1;
    }}
    
    /* Style headings within cards */
    .summary-cards-wrapper h4 {
        margin-top: 0 !important;
        margin-bottom: 1rem !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #1a1a1a !important;
    }
    
    /* Consistent spacing for text in cards */
    .summary-cards-wrapper .stMarkdown p {
        margin-bottom: 0.5rem !important;
        line-height: 1.6 !important;
        color: #1a1a1a !important;
    }
    
    /* Reduce spacing in Layout and Lookup summaries to match Claims File Summary */
    .summary-cards-wrapper [data-testid="column"]:nth-child(2) .stMarkdown,
    .summary-cards-wrapper [data-testid="column"]:nth-child(3) .stMarkdown {
        margin-bottom: 0.75rem !important;
        margin-top: 0.1rem !important;
    }
    
    .summary-cards-wrapper [data-testid="column"]:nth-child(2) .stMarkdown p,
    .summary-cards-wrapper [data-testid="column"]:nth-child(3) .stMarkdown p {
        margin-bottom: 0.75rem !important;
        line-height: 1.2 !important;
    }
    
    /* Style expanders in cards - ensure consistent spacing */
    .summary-cards-wrapper .streamlit-expanderHeader {
        font-size: 14px !important;
        font-weight: 500 !important;
        margin-top: 0.5rem !important;
        color: #1a1a1a !important;
    }
    
    .summary-cards-wrapper .streamlit-expander {{
        margin-top: 0.25rem !important;
    }}
    
    /* Add bottom margin to last expander to balance spacing */
    .summary-cards-wrapper [data-testid="column"] .streamlit-expander:last-child {{
        margin-bottom: 0.5rem !important;
    }}
    
    /* Style info boxes */
    .summary-cards-wrapper .stAlert {{
        margin-top: 1rem !important;
    }}
    
    /* Compact spacing for file description line */
    .summary-cards-wrapper [data-testid="column"] .stMarkdown:first-of-type p {{
        margin-bottom: 0.5rem !important;
    }}
    
    /* Reduce spacing between title and first content */
    .summary-cards-wrapper h4 + .stMarkdown {{
        margin-top: -0.5rem !important;
    }}
    
    /* Tooltip Styles */
    .tooltip-wrapper {{
        position: relative;
        display: inline-block;
        cursor: help;
    }}
    
    .tooltip-text {{
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
    }}
    
    .tooltip-wrapper:hover .tooltip-text {{
        visibility: visible;
        opacity: 1;
    }}
    
    /* Visual Indicators */
    .status-indicator {{
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 6px;
        animation: pulse 2s infinite;
    }}
    
    .status-mapped {{ background-color: #4caf50; }}
    .status-unmapped {{ background-color: #f44336; }}
    .status-suggested {{ background-color: #ff9800; }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    
    /* Progress Indicators */
    .progress-container {{
        position: relative;
        width: 100%;
        height: 20px;
        background-color: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin: 10px 0;
    }}
    
    .progress-bar {{
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }}
    
    /* Drag and Drop Styles */
    .drag-drop-zone {{
        border: 2px dashed #4caf50;
        border-radius: 8px;
        padding: 40px;
        text-align: center;
        background-color: rgba(76, 175, 80, 0.05);
        transition: all 0.3s ease;
    }}
    
    .drag-drop-zone.dragover {{
        border-color: #2e7d32;
        background-color: rgba(76, 175, 80, 0.1);
    }}
    
    /* Search/Filter Styles */
    .search-box {
        padding: 10px;
        border: 1px solid #e8e8e8;
        border-radius: 6px;
        width: 100%;
        margin-bottom: 10px;
        background-color: white;
        color: #1a1a1a;
    }
    
    /* Keyboard Shortcut Hints */
    .shortcut-hint {{
        font-size: 11px;
        color: #888;
        font-style: italic;
        margin-left: 8px;
    }}
    
    /* Auto-save Indicator */
    .autosave-indicator {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #4caf50;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        z-index: 1000;
        opacity: 0;
        transition: opacity 0.3s;
    }}
    
    .autosave-indicator.show {{
        opacity: 1;
    }}
    
    /* Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: #f9fafb;
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #6b7280;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Modern Divider */
    hr {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 2rem 0;
    }
    
    /* Smooth Transitions */
    * {
        transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
    }
    
    /* Modern Code Blocks */
    .stCodeBlock {
        border-radius: 6px !important;
        border: 1px solid #e5e7eb !important;
    }
    
    /* Spacing Improvements */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Modern Container for Tools */
    .streamlit-expanderHeader[aria-expanded="true"] {
        background-color: #f3f4f6 !important;
        border-color: #6b7280 !important;
    }
    
    /* Responsive Design - Mobile/Tablet Support */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            max-width: 100% !important;
        }
        
        [data-testid="column"] {
            flex-direction: column !important;
            width: 100% !important;
            margin-bottom: 1rem !important;
        }
        
        .upload-columns-container {
            flex-direction: column !important;
            max-width: 100% !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 1rem !important;
            font-size: 0.85rem !important;
        }
        
        h1 { font-size: 1.25rem !important; }
        h2 { font-size: 1.1rem !important; }
        h3 { font-size: 1rem !important; }
        
        .stDataFrame {
            font-size: 0.8rem !important;
        }
        
        .stButton > button {
            padding: 0.4rem 0.8rem !important;
            font-size: 0.85rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .main .block-container {
            padding-left: 0.25rem !important;
            padding-right: 0.25rem !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.4rem 0.8rem !important;
            font-size: 0.75rem !important;
        }
    }
    
    /* Column Resizing for Data Tables */
    .stDataFrame table {
        table-layout: auto !important;
    }
    
    .stDataFrame th {
        min-width: 100px !important;
        max-width: 300px !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    
    .stDataFrame td {
        min-width: 80px !important;
        max-width: 250px !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    </style>
    """, unsafe_allow_html=True)


def inject_main_layout_css():
    """Inject CSS for main content container and optimized layout."""
    st.markdown("""
    <style>
        /* Maximize horizontal space and reduce margins */
        .main .block-container {
            padding-top: 0.1rem !important;
            padding-bottom: 0.25rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 1400px;
        }
        /* Reduce font sizes globally */
        body, .main {
            font-size: 13px !important;
        }
        /* Consistent header sizing - enforce same size for all headers of same level */
        h1 {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
        }
        h2 {
            font-size: 1.25rem !important;
            font-weight: 600 !important;
        }
        h3 {
            font-size: 1.1rem !important;
            font-weight: 600 !important;
        }
        h4 {
            font-size: 1rem !important;
            font-weight: 600 !important;
        }
        h5 {
            font-size: 0.9rem !important;
            font-weight: 600 !important;
        }
        h6 {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
        }
        /* Override any inline styles in markdown headers */
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3,
        .stMarkdown h4,
        .stMarkdown h5,
        .stMarkdown h6 {
            font-size: inherit !important;
            font-weight: 600 !important;
        }
        /* Ensure markdown headers use consistent sizing */
        .stMarkdown h1 { font-size: 1.5rem !important; }
        .stMarkdown h2 { font-size: 1.25rem !important; }
        .stMarkdown h3 { font-size: 1.1rem !important; }
        .stMarkdown h4 { font-size: 1rem !important; }
        .stMarkdown h5 { font-size: 0.9rem !important; }
        .stMarkdown h6 { font-size: 0.85rem !important; }
        p, div, span, label {
            font-size: 13px !important;
        }
        /* Reduce excessive vertical spacing */
        h1, h2, h3, h4, h5, h6 {
            margin-top: 0.25rem !important;
            margin-bottom: 0.125rem !important;
        }
        /* Tighter spacing for tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.125rem !important;
            margin-bottom: 0.125rem !important;
        }
        /* Reduce spacing for dividers */
        hr {
            margin: 0.25rem 0 !important;
        }
        /* Tighter spacing between elements */
        .element-container {
            margin-bottom: 0.125rem !important;
        }
        /* Reduce spacing in columns */
        .stColumn {
            gap: 0.25rem !important;
        }
        /* Tighter spacing for expanders */
        [data-testid="stExpander"] {
            margin-bottom: 0.25rem !important;
        }
        [data-testid="stExpander"] > div {
            padding-top: 0.25rem !important;
            padding-bottom: 0.25rem !important;
        }
        /* Reduce spacing in file uploader */
        [data-testid="stFileUploader"] {
            margin-bottom: 0.25rem !important;
        }
        /* Tighter spacing for buttons */
        .stButton {
            margin-bottom: 0.125rem !important;
            font-size: 13px !important;
        }
        /* Reduce spacing in forms */
        [data-testid="stForm"] {
            margin-bottom: 0.25rem !important;
        }
        /* Tighter spacing for dataframes */
        [data-testid="stDataFrame"] {
            margin-bottom: 0.25rem !important;
            font-size: 12px !important;
        }
        /* Reduce spacing for metrics */
        [data-testid="stMetricContainer"] {
            margin-bottom: 0.125rem !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.25rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
        }
        /* Tighter spacing for info/warning/error messages */
        .stAlert {
            margin-bottom: 0.25rem !important;
            padding: 0.375rem 0.75rem !important;
            font-size: 13px !important;
        }
        /* Reduce spacing for selectboxes and inputs */
        .stSelectbox, .stTextInput, .stNumberInput, .stTextArea, .stMultiselect, .stDateInput, .stTimeInput {
            margin-bottom: 0.5rem !important;
        }
        /* Ensure proper spacing for input containers */
        .stSelectbox > div,
        .stTextInput > div,
        .stTextArea > div,
        .stNumberInput > div,
        .stMultiselect > div,
        .stDateInput > div,
        .stTimeInput > div {
            margin-bottom: 0.5rem !important;
        }
        /* Tighter spacing for captions */
        .stCaption {
            margin-top: 0.0625rem !important;
            margin-bottom: 0.0625rem !important;
            font-size: 11px !important;
        }
        /* Reduce spacing in sidebar */
        .css-1d391kg {
            padding-top: 0.5rem !important;
        }
        /* Tighter spacing for markdown blocks */
        .stMarkdown {
            margin-bottom: 0.125rem !important;
            font-size: 13px !important;
        }
        /* Reduce spacing between containers */
        .stContainer {
            margin-bottom: 0.25rem !important;
        }
        /* Tighter spacing for download buttons */
        [data-testid="stDownloadButton"] {
            margin-bottom: 0.125rem !important;
            font-size: 13px !important;
        }
        /* Reduce spacing for progress bars */
        [data-testid="stProgressBar"] {
            margin-bottom: 0.125rem !important;
        }
        /* Tighter spacing for code blocks */
        .stCodeBlock {
            margin-bottom: 0.25rem !important;
            font-size: 12px !important;
        }
        /* Reduce spacing for JSON displays */
        [data-testid="stJson"] {
            margin-bottom: 0.25rem !important;
            font-size: 12px !important;
        }
        /* Tighter overall page spacing */
        .main {
            padding-top: 0.25rem !important;
        }
        /* Reduce spacing in summary cards */
        .summary-cards-wrapper {
            margin-bottom: 0.25rem !important;
        }
        /* Tighter spacing for data editor */
        [data-testid="stDataEditor"] {
            margin-bottom: 0.25rem !important;
            font-size: 12px !important;
        }
        /* Additional tight spacing rules */
        .stCheckbox, .stRadio {
            margin-bottom: 0.125rem !important;
            font-size: 13px !important;
        }
        /* Reduce spacing in multi-select */
        [data-testid="stMultiSelect"] {
            margin-bottom: 0.125rem !important;
            font-size: 13px !important;
        }
        /* Tighter spacing for sliders */
        [data-testid="stSlider"] {
            margin-bottom: 0.125rem !important;
        }
        /* Reduce spacing for date inputs */
        [data-testid="stDateInput"] {
            margin-bottom: 0.125rem !important;
            font-size: 13px !important;
        }
        /* Tighter spacing for time inputs */
        [data-testid="stTimeInput"] {
            margin-bottom: 0.125rem !important;
            font-size: 13px !important;
        }
        /* Reduce spacing for color pickers */
        [data-testid="stColorPicker"] {
            margin-bottom: 0.125rem !important;
        }
        /* Tighter spacing for file uploader dropzone */
        [data-testid="stFileUploader"] > div {
            padding: 0.5rem !important;
            font-size: 13px !important;
        }
        /* Reduce spacing in columns wrapper */
        [data-testid="column"] {
            gap: 0.25rem !important;
        }
        /* Tighter spacing for empty states */
        .stEmpty {
            margin-bottom: 0.25rem !important;
            font-size: 13px !important;
        }
        /* Reduce spacing for success messages */
        .stSuccess {
            margin-bottom: 0.25rem !important;
            padding: 0.375rem 0.75rem !important;
            font-size: 13px !important;
        }
        /* Tighter spacing for error messages */
        .stError {
            margin-bottom: 0.25rem !important;
            padding: 0.375rem 0.75rem !important;
            font-size: 13px !important;
        }
        /* Reduce spacing for warning messages */
        .stWarning {
            margin-bottom: 0.25rem !important;
            padding: 0.375rem 0.75rem !important;
            font-size: 13px !important;
        }
        /* Tighter spacing for info messages */
        .stInfo {
            margin-bottom: 0.25rem !important;
            padding: 0.375rem 0.75rem !important;
            font-size: 13px !important;
        }
        /* Remove all gradient backgrounds */
        * {
            background-image: none !important;
        }
        /* UI/UX Best Practices - Golden Rules */
        /* 1. Visual Hierarchy - Primary vs Secondary Actions */
        .stButton > button[type="primary"],
        button[data-baseweb="button"][kind="primary"] {
            background-color: #495057 !important;
            color: white !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        }
        .stButton > button:not([type="primary"]):not(:disabled) {
            background-color: #6c757d !important;
            color: white !important;
        }
        /* 2. Accessibility - Focus States */
        .stButton > button:focus,
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div:focus,
        .stTextArea > div > div > textarea:focus,
        button[data-baseweb="button"]:focus {
            outline: 2px solid #495057 !important;
            outline-offset: 2px !important;
            box-shadow: 0 0 0 3px rgba(73, 80, 87, 0.2) !important;
        }
        /* 3. Clear Affordances - Hover States */
        .stButton > button:not(:disabled):hover,
        button[data-baseweb="button"]:not(:disabled):hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 3px 6px rgba(0,0,0,0.2) !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button:not(:disabled):active,
        button[data-baseweb="button"]:not(:disabled):active {
            transform: translateY(0) !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.15) !important;
        }
        /* 4. Input Field Feedback */
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div:focus {
            border-color: #495057 !important;
            box-shadow: 0 0 0 2px rgba(73, 80, 87, 0.1) !important;
        }
        .stTextInput > div > div > input:hover,
        .stTextArea > div > div > textarea:hover,
        .stSelectbox > div > div:hover {
            border-color: #adb5bd !important;
        }
        /* 5. Clear Disabled States */
        .stButton > button:disabled,
        button[data-baseweb="button"]:disabled {
            opacity: 0.5 !important;
            cursor: not-allowed !important;
            transform: none !important;
        }
        /* 6. Better Contrast for Accessibility */
        .stMarkdown, p, span, div, label {
            color: #212529 !important;
        }
        /* 7. Clear Interactive Elements */
        [data-testid="stExpander"]:hover .streamlit-expanderHeader {
            background-color: #e9ecef !important;
            cursor: pointer !important;
        }
        /* 8. Loading States - Spinner Visibility */
        .stSpinner > div {
            border-color: #495057 !important;
            border-top-color: transparent !important;
        }
        /* 9. Better Empty States */
        .stEmpty, .stInfo:empty {
            padding: 1rem !important;
            text-align: center !important;
            color: #6c757d !important;
        }
        /* 10. Form Validation Feedback */
        .stTextInput > div > div > input:invalid,
        .stTextArea > div > div > textarea:invalid {
            border-color: #dc3545 !important;
        }
        /* 11. Clear Clickable Areas - Minimum Touch Target */
        .stButton > button,
        button[data-baseweb="button"],
        .stDownloadButton > button {
            min-height: 2rem !important;
            min-width: 2.5rem !important;
        }
        /* 12. Better Table/DataFrame Readability */
        .stDataFrame table {
            border-collapse: collapse !important;
        }
        .stDataFrame th {
            background-color: #f8f9fa !important;
            font-weight: 600 !important;
            border-bottom: 2px solid #dee2e6 !important;
        }
        .stDataFrame td {
            border-bottom: 1px solid #e9ecef !important;
        }
        .stDataFrame tr:hover {
            background-color: #f8f9fa !important;
        }
        /* 13. Improved Metrics Display */
        [data-testid="stMetricContainer"] {
            border: 1px solid #e9ecef !important;
            border-radius: 4px !important;
            padding: 0.5rem !important;
            background-color: #f8f9fa !important;
        }
        /* 14. Better Progress Indicators */
        [data-testid="stProgressBar"] > div > div {
            background-color: #495057 !important;
        }
        /* 15. Clear Section Separators */
        hr {
            border-top: 1px solid #dee2e6 !important;
            margin: 0.75rem 0 !important;
        }
        /* 16. Improved Alert/Message Visibility */
        .stAlert {
            border-left-width: 3px !important;
            border-left-style: solid !important;
        }
        .stSuccess {
            border-left-color: #6b7280 !important;
        }
        .stError {
            border-left-color: #374151 !important;
        }
        .stWarning {
            border-left-color: #9ca3af !important;
        }
        .stInfo {
            border-left-color: #6b7280 !important;
        }
        /* 17. Better Tab Navigation */
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #f8f9fa !important;
        }
        .stTabs [aria-selected="true"] {
            border-bottom: 2px solid #495057 !important;
            font-weight: 600 !important;
        }
        /* 18. Improved File Uploader Affordance */
        .stFileUploader:hover {
            border-color: #495057 !important;
            background-color: #f8f9fa !important;
        }
        /* 19. Better Checkbox/Radio Visibility */
        .stCheckbox label,
        .stRadio label {
            cursor: pointer !important;
            user-select: none !important;
        }
        /* 20. Better Link/Clickable Text */
        a, [role="link"] {
            color: #495057 !important;
            text-decoration: underline !important;
            cursor: pointer !important;
        }
        a:hover, [role="link"]:hover {
            color: #212529 !important;
        }
        /* 22. Improved Code Block Readability */
        .stCodeBlock, code, pre {
            background-color: #f8f9fa !important;
            border: 1px solid #e9ecef !important;
            color: #212529 !important;
        }
        /* 23. Better JSON Display */
        [data-testid="stJson"] {
            background-color: #f8f9fa !important;
            border: 1px solid #e9ecef !important;
            border-radius: 4px !important;
            padding: 0.5rem !important;
        }
        /* 24. Clear Visual Feedback for Actions */
        .stButton > button:not(:disabled) {
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }
        /* 25. Improved Spacing for Readability */
        .stMarkdown p {
            line-height: 1.5 !important;
        }
        /* 26. Better List Styling */
        ul, ol {
            padding-left: 1.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        li {
            margin-bottom: 0.25rem !important;
            line-height: 1.5 !important;
        }
        /* 27. Improved Caption Readability */
        .stCaption {
            color: #6c757d !important;
            font-style: italic !important;
        }
        /* 28. Better Tooltip Visibility */
        [title], [data-tooltip] {
            cursor: help !important;
        }
        /* 29. Clear Visual Grouping */
        .stContainer {
            border: 1px solid #e9ecef !important;
            border-radius: 4px !important;
            padding: 0.75rem !important;
            background-color: #ffffff !important;
        }
        /* 30. Improved Scrollbar Styling (where applicable) */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        ::-webkit-scrollbar-thumb {
            background: #adb5bd;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #868e96;
        }
        /* 31. Better Form Layout */
        .stForm {
            background-color: #ffffff !important;
            border: 1px solid #e9ecef !important;
            border-radius: 4px !important;
            padding: 1rem !important;
        }
        /* 32. Improved Data Editor */
        [data-testid="stDataEditor"] {
            border: 1px solid #e9ecef !important;
            border-radius: 4px !important;
        }
        /* 33. Better Metric Cards */
        [data-testid="stMetricValue"] {
            font-weight: 600 !important;
            color: #212529 !important;
        }
        [data-testid="stMetricLabel"] {
            color: #6c757d !important;
            font-weight: 500 !important;
        }
        /* 34. Clear Visual States for Validation */
        [data-testid="stDataFrame"] tr[data-status="error"] {
            background-color: #f3f4f6 !important;
        }
        [data-testid="stDataFrame"] tr[data-status="warning"] {
            background-color: #f3f4f6 !important;
        }
        [data-testid="stDataFrame"] tr[data-status="success"] {
            background-color: #f3f4f6 !important;
        }
        /* 35. Better Mobile Responsiveness */
        @media (max-width: 768px) {
            .stButton > button {
                width: 100% !important;
                margin-bottom: 0.5rem !important;
            }
        }
        /* 36. Improved Loading Spinner */
        .stSpinner {
            color: #495057 !important;
        }
        /* 37. Better Placeholder Text */
        input::placeholder,
        textarea::placeholder {
            color: #adb5bd !important;
            opacity: 1 !important;
        }
        /* 38. Clear Visual Hierarchy in Cards */
        .summary-cards-wrapper [data-testid="column"] {
            transition: box-shadow 0.2s ease !important;
        }
        .summary-cards-wrapper [data-testid="column"]:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
        }
        /* 39. Better Error Message Styling */
        .stError {
            background-color: #f3f4f6 !important;
            border-left-color: #374151 !important;
        }
        /* 40. Improved Success Message Styling */
        .stSuccess {
            background-color: #f3f4f6 !important;
            border-left-color: #6b7280 !important;
        }
        /* 41. Better Warning Message Styling */
        .stWarning {
            background-color: #f3f4f6 !important;
            border-left-color: #9ca3af !important;
        }
        /* 42. Improved Info Message Styling - All Grey */
        .stInfo {
            background-color: #f3f4f6 !important;
            border-left-color: #6b7280 !important;
        }
        
        .stInfo > div {
            color: #1f2937 !important;
        }
        
        /* Override all Streamlit alert boxes to use grey for info boxes */
        div[data-baseweb="notification"] {
            background-color: #f3f4f6 !important;
        }
        
        /* Info alert boxes specifically */
        div[data-baseweb="notification"][data-kind="info"] {
            background-color: #f3f4f6 !important;
            border-left-color: #6b7280 !important;
        }
        /* 43. Better Required Field Indicators (handled via label styling) */
        /* 44. Better Pagination Controls */
        .stButton > button:disabled {
            opacity: 0.4 !important;
        }
        /* 45. Improved Sidebar Styling */
        [data-testid="stSidebar"] {
            border-right: 1px solid #e9ecef !important;
        }
        /* 46. Better Toggle/Switch Visibility */
        .stCheckbox input[type="checkbox"]:checked + label::before {
            background-color: #495057 !important;
        }
        /* 47. Clear Visual Separation for Sections */
        .stMarkdown h2,
        .stMarkdown h3 {
            border-bottom: 1px solid #e9ecef !important;
            padding-bottom: 0.25rem !important;
            margin-bottom: 0.5rem !important;
        }
        /* 48. Better Slider Visibility */
        [data-testid="stSlider"] {
            margin: 0.5rem 0 !important;
        }
        /* 49. Improved Date/Time Input Styling */
        [data-testid="stDateInput"] > div,
        [data-testid="stTimeInput"] > div {
            border: 1px solid #ddd !important;
            border-radius: 4px !important;
        }
        /* 50. Better Multiselect Display */
        [data-testid="stMultiSelect"] > div > div {
            min-height: 2.5rem !important;
        }
        /* Ensure no gradient colors in any elements */
        [style*="gradient"], [style*="linear-gradient"] {
            background: #f5f5f5 !important;
            background-image: none !important;
        }
        /* Override ui_styling.py conflicting styles - enforce consistent neutral theme */
        .stButton > button,
        button[data-baseweb="button"],
        .stDownloadButton > button {
            background-color: #6c757d !important;
            color: white !important;
            border: 1px solid #5a6268 !important;
            border-radius: 4px !important;
            padding: 0.375rem 0.75rem !important;
            font-weight: 500 !important;
            font-size: 13px !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
        }
        .stButton > button:hover,
        button[data-baseweb="button"]:hover,
        .stDownloadButton > button:hover {
            background-color: #5a6268 !important;
            color: white !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
        }
        .stButton > button:disabled,
        button[data-baseweb="button"]:disabled {
            background-color: #c6c8ca !important;
            color: #6c757d !important;
            cursor: not-allowed !important;
        }
        /* Consistent status boxes - neutral gray theme */
        div[style*="background-color:#fdecea"],
        div[style*="background-color:#fff3cd"],
        div[style*="background-color:#d1ecf1"],
        div[style*="background-color:#d4edda"] {
            background-color: #f5f5f5 !important;
            border: 1px solid #ddd !important;
            color: #000000 !important;
        }
        div[style*="color: #b02a37"],
        div[style*="color: #856404"],
        div[style*="color: #0c5460"],
        div[style*="color: #155724"] {
            color: #000000 !important;
        }
        /* Consistent activity log styling */
        div[style*="background-color: #f5f5f5"] {
            background-color: #f5f5f5 !important;
            border: 1px solid #ddd !important;
        }
        /* Override expander styles for consistency */
        .streamlit-expanderHeader {
            background-color: #f5f5f5 !important;
            border: 1px solid #ddd !important;
            border-radius: 4px !important;
            padding: 0.5rem 0.75rem !important;
            font-size: 13px !important;
            font-weight: 500 !important;
        }
        .streamlit-expanderContent {
            padding: 0.5rem 0.75rem !important;
            background-color: #ffffff !important;
            border: 1px solid #ddd !important;
            border-top: none !important;
            border-radius: 0 0 4px 4px !important;
        }
        /* Consistent input field styling */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            border: 1px solid #ddd !important;
            border-radius: 4px !important;
            padding: 0.375rem 0.5rem !important;
            font-size: 13px !important;
            background-color: white !important;
        }
        /* Fix selectbox labels - ensure they're not cut off */
        .stSelectbox label,
        .stTextInput label,
        .stTextArea label,
        .stNumberInput label,
        .stMultiselect label,
        .stDateInput label,
        .stTimeInput label {
            font-size: 13px !important;
            line-height: 1.4 !important;
            padding-bottom: 0.25rem !important;
            margin-bottom: 0.25rem !important;
            white-space: normal !important;
            word-wrap: break-word !important;
            overflow: visible !important;
            height: auto !important;
            min-height: auto !important;
        }
        /* Ensure selectbox container has enough space */
        .stSelectbox > div,
        .stTextInput > div,
        .stTextArea > div,
        .stNumberInput > div,
        .stMultiselect > div,
        .stDateInput > div,
        .stTimeInput > div {
            margin-bottom: 0.5rem !important;
            min-height: auto !important;
        }
        /* Fix selectbox dropdown itself */
        .stSelectbox > div > div > div {
            min-height: 2rem !important;
            padding: 0.375rem 0.5rem !important;
            font-size: 13px !important;
        }
        /* Ensure multiselect has proper sizing */
        [data-testid="stMultiSelect"] > div {
            min-height: 2rem !important;
        }
        [data-testid="stMultiSelect"] label {
            font-size: 13px !important;
            line-height: 1.4 !important;
            padding-bottom: 0.25rem !important;
            white-space: normal !important;
        }
        /* Consistent tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #f5f5f5 !important;
            border-bottom: 1px solid #ddd !important;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent !important;
            color: #000000 !important;
            font-size: 13px !important;
            padding: 0.5rem 1rem !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: white !important;
            color: #000000 !important;
            font-weight: 600 !important;
            border-bottom: 2px solid #666 !important;
        }
        /* Consistent file uploader */
        .stFileUploader {
            border: 1px dashed #ddd !important;
            border-radius: 4px !important;
            background-color: #fafafa !important;
            padding: 0.5rem !important;
        }
        /* Remove all colored borders and backgrounds from status indicators */
        div[style*="border-left: 3px solid"] {
            border-left: 2px solid #999 !important;
        }
        /* Consistent summary cards */
        .summary-cards-wrapper [data-testid="column"] {
            background: white !important;
            border: 1px solid #ddd !important;
            border-radius: 4px !important;
            padding: 0.75rem !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        }
        /* Override any large font sizes in status messages */
        strong[style*="font-size: 1.2rem"],
        strong[style*="font-size"] {
            font-size: 1rem !important;
        }
        /* Consistent padding for all status boxes */
        div[style*="padding: 1.5rem"] {
            padding: 0.75rem 1rem !important;
        }
        /* Ensure all inline styles respect our font sizes */
        [style*="font-size"] {
            font-size: 13px !important;
        }
        [style*="font-size: 0.85rem"],
        [style*="font-size: 0.75rem"],
        [style*="font-size: 0.7rem"] {
            font-size: 12px !important;
        }
        [style*="font-size: 1.2rem"],
        [style*="font-size: 1.1rem"] {
            font-size: 1rem !important;
        }
        /* Consistent colors - remove all bright colors */
        [style*="color: #b02a37"],
        [style*="color: #721c24"],
        [style*="color: #856404"],
        [style*="color: #0c5460"],
        [style*="color: #155724"] {
            color: #000000 !important;
        }
        /* Make all colored backgrounds neutral */
        [style*="background-color:#fdecea"],
        [style*="background-color:#fff3cd"],
        [style*="background-color:#d1ecf1"],
        [style*="background-color:#d4edda"] {
            background-color: #f5f5f5 !important;
        }
    </style>
    """, unsafe_allow_html=True)


def inject_ux_javascript():
    """Inject JavaScript for UX enhancements and hide file uploader size/type text."""
    st.markdown("""
    <script>
    (function() {
        // Keyboard Shortcuts
        document.addEventListener('keydown', function(e) {
            // Tab navigation (Ctrl/Cmd + Arrow keys)
            if ((e.ctrlKey || e.metaKey) && e.key === 'ArrowRight') {
                e.preventDefault();
                const tabs = document.querySelectorAll('[data-baseweb="tab"]');
                const activeTab = document.querySelector('[data-baseweb="tab"][aria-selected="true"]');
                if (activeTab && tabs.length > 0) {
                    const currentIndex = Array.from(tabs).indexOf(activeTab);
                    if (currentIndex < tabs.length - 1) {
                        tabs[currentIndex + 1].click();
                    }
                }
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'ArrowLeft') {
                e.preventDefault();
                const tabs = document.querySelectorAll('[data-baseweb="tab"]');
                const activeTab = document.querySelector('[data-baseweb="tab"][aria-selected="true"]');
                if (activeTab && tabs.length > 0) {
                    const currentIndex = Array.from(tabs).indexOf(activeTab);
                    if (currentIndex > 0) {
                        tabs[currentIndex - 1].click();
                    }
                }
            }
            // Search (Ctrl/Cmd + F)
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                const searchInput = document.querySelector('input[placeholder*="Search"]');
                if (searchInput) searchInput.focus();
            }
        });
        
        // Hide file size limit and file type text in uploaders (but preserve labels)
        function hideFileUploaderText() {
            document.querySelectorAll('.stFileUploader').forEach(function(uploader) {
                // Hide small tags (file size/type info)
                uploader.querySelectorAll('small').forEach(function(el) {
                    el.style.display = 'none';
                });
                // Hide markdown containers with file size/type info (but not if they contain a label)
                uploader.querySelectorAll('[data-testid="stMarkdownContainer"]').forEach(function(el) {
                    // Don't hide if it contains a label element or emoji/icon (likely a title)
                    if (el.querySelector('label') || el.textContent.includes('📄') || 
                        el.textContent.includes('📋') || el.textContent.includes('📊') ||
                        el.textContent.includes('📝') || el.textContent.includes('Upload')) {
                        return;
                    }
                    const text = el.textContent || '';
                    if (text.includes('Limit') || text.includes('MB') || text.includes('XLSX') || 
                        text.includes('CSV') || text.includes('TXT') || text.includes('TSV') ||
                        text.includes('JSON') || text.includes('PARQUET')) {
                        el.style.display = 'none';
                    }
                });
                // Hide any paragraph that contains file size/type info (but not if it's part of a label)
                uploader.querySelectorAll('p').forEach(function(el) {
                    // Don't hide if it's inside a label or contains strong/bold text (likely a title)
                    if (el.closest('label') || el.querySelector('strong') || el.querySelector('b')) {
                        return;
                    }
                    const text = el.textContent || '';
                    if (text.includes('Limit') || text.includes('MB') || text.includes('XLSX') || 
                        text.includes('CSV') || text.includes('TXT') || text.includes('TSV') ||
                        text.includes('JSON') || text.includes('PARQUET')) {
                        el.style.display = 'none';
                    }
                });
            });
        }
        
        // Run immediately and on mutations
        hideFileUploaderText();
        setTimeout(hideFileUploaderText, 500);
        setTimeout(hideFileUploaderText, 1000);
        
        // Watch for new elements being added
        const observer = new MutationObserver(function(mutations) {
            hideFileUploaderText();
        });
        observer.observe(document.body, { childList: true, subtree: true });
        
        // Drag and Drop Enhancement
        setTimeout(function() {
            document.querySelectorAll('input[type="file"]').forEach(function(input) {
                const parent = input.closest('.stFileUploader');
                if (parent) {
                    parent.addEventListener('dragover', function(e) {
                        e.preventDefault();
                        parent.style.border = '2px dashed #4caf50';
                        parent.style.backgroundColor = 'rgba(76, 175, 80, 0.1)';
                    });
                    parent.addEventListener('dragleave', function(e) {
                        e.preventDefault();
                        parent.style.border = '';
                        parent.style.backgroundColor = '';
                    });
                    parent.addEventListener('drop', function(e) {
                        e.preventDefault();
                        parent.style.border = '';
                        parent.style.backgroundColor = '';
                    });
                }
            });
        }, 500);
    })();
    </script>
    """, unsafe_allow_html=True)

