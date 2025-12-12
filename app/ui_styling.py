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
    
    /* Modern Buttons - All Blue with White Text */
    .stButton > button,
    button[data-baseweb="button"],
    .stDownloadButton > button {
        background-color: #3b82f6 !important;
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
    .stDownloadButton > button:hover {
        background-color: #2563eb !important;
        color: white !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        transform: translateY(-1px);
    }
    
    .stButton > button:disabled,
    button[data-baseweb="button"]:disabled,
    .stDownloadButton > button:disabled {
        background-color: #9ca3af !important;
        color: white !important;
        cursor: not-allowed !important;
    }
    
    /* Form Submit Buttons */
    .stForm > div > button {
        background-color: #3b82f6 !important;
        color: white !important;
    }
    
    .stForm > div > button:hover {
        background-color: #2563eb !important;
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
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
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
        min-height: 200px !important;
    }
    
    /* Make all file uploaders the same size */
    [data-testid="column"] .stFileUploader {
        flex: 1 !important;
        min-height: 200px !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }
    
    /* Prevent file uploaders from breaking column layout */
    .stFileUploader {
        border: 2px dashed #d1d5db !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
        background-color: #f9fafb !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        box-sizing: border-box !important;
        min-width: 0 !important;
        min-height: 200px !important;
    }
    
    .stFileUploader:hover {
        border-color: #3b82f6 !important;
        background-color: #eff6ff !important;
    }
    
    /* Ensure file uploader inner content is centered */
    .stFileUploader > div {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        min-height: 150px !important;
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
        min-height: 150px !important;
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
        color: #3b82f6;
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
        background-color: #eff6ff !important;
        border-color: #3b82f6 !important;
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

