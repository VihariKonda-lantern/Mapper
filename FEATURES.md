# Claims Mapper and Validator - Complete Feature Documentation

## Overview

The Claims Mapper and Validator is a comprehensive Streamlit-based web application for mapping, validating, and transforming healthcare claims data. It provides intelligent field mapping, data quality analysis, validation, anonymization, and batch processing capabilities.

## Main Application Tabs

### 1. Setup Tab
**Purpose**: Upload and configure input files

**Features**:
- **File Upload**:
  - Layout file upload (Excel/CSV) - defines internal field structure
  - Claims file upload (CSV, TXT, TSV, XLSX, JSON, Parquet)
  - Lookup files upload (diagnosis codes, etc.)
  - Header file upload (for files without headers)
  - Header specification file support (for fixed-width files)

- **Intelligent File Detection**:
  - Automatic delimiter detection for text files
  - Automatic header detection using CSV sniffer
  - Fixed-width file detection and column position detection
  - Encoding detection and fallback handling

- **File Processing**:
  - Progress indicators for file loading
  - File validation (size limits, format checks)
  - Metadata capture (format, separator, header status)
  - Claims file preview and summary

- **Lookup File Support**:
  - Diagnosis code lookup file processing
  - Lookup file summary display

### 2. Field Mapping Tab
**Purpose**: Map source columns to internal fields

**Features**:
- **Manual Field Mapping**:
  - Grouped field mapping by field groups
  - Dual input field selection (dropdown + text input)
  - Required vs optional field indicators
  - Mapping progress tracking (X/Y fields mapped)
  - Undo/Redo functionality (Ctrl+Z, Ctrl+Y)
  - Mapping history tracking

- **AI Auto-Mapping**:
  - Enhanced automap with confidence scores
  - Automatic mapping for high-confidence matches (≥80%)
  - AI suggestion display with confidence percentages
  - Accept/override individual suggestions
  - Batch accept multiple suggestions
  - Tooltips explaining AI confidence scores

- **Mapping Tools**:
  - Mapping validation before processing
  - Mapping confidence scores display
  - Mapping version control
  - Export/import mapping templates
  - Save/load mapping templates locally
  - Mapping template marketplace (shareable format)

- **Mapping Enhancements**:
  - Duplicate mapping detection
  - Required field validation
  - Mapping completeness checking
  - Unit test generation for mappings

### 3. Preview & Validate Tab
**Purpose**: Preview transformed data and run validations

**Features**:
- **Data Preview**:
  - Transformed data preview (first rows)
  - Sample data display
  - Lazy loading for large datasets (pagination)
  - Sortable and filterable tables

- **Validation Engine**:
  - Required field validation
  - Data type validation
  - Format validation (dates, numbers, etc.)
  - Cross-field validation
  - Custom validation rules builder
  - Dynamic validation rules
  - Validation performance tracking

- **Validation Results**:
  - Validation summary dashboard
  - Detailed validation results (paginated)
  - Field-level validation status
  - File-level validation summary
  - Mandatory fields analysis
  - Validation error explanations
  - Rejection explanations

- **Custom Validation Rules**:
  - Create custom validation rules
  - Save/load validation rule templates
  - Rule builder interface
  - Rule execution and results

### 4. Downloads Tab
**Purpose**: Generate and download output files

**Features**:
- **Output Generation**:
  - Anonymized claims file generation
  - Mapping table generation
  - Multiple export formats (CSV, TXT, XLSX, JSON, Parquet)
  - Batch processing (multiple files)
  - ZIP file generation with all outputs

- **Batch Processing**:
  - Process multiple claims files
  - Apply same mapping to multiple files
  - Batch output generation
  - Progress tracking for batch operations

- **Output Options**:
  - Optional attachments (header files, original claims, notes)
  - Custom notes addition
  - Download all outputs as ZIP
  - Individual file downloads

### 5. Data Quality Tab
**Purpose**: Analyze data quality and completeness

**Features**:
- **Data Quality Metrics**:
  - Overall data quality score calculation
  - Data profiling dashboard
  - Column statistics (count, unique, nulls, types)
  - Data completeness matrix
  - Duplicate detection and analysis
  - Outlier detection
  - Data sampling

- **Data Analysis**:
  - Statistical summaries per column
  - Missing data analysis
  - Data distribution insights
  - Pattern detection

### 6. Tools & Analytics Tab
**Purpose**: System monitoring, analytics, and utilities

**Sub-tabs**:

#### System Health
- CPU usage monitoring
- Memory usage tracking (RSS, VMS)
- Thread count
- Operation performance metrics
- Error statistics
- Log export functionality

#### Usage Analytics
- Feature usage tracking
- Usage statistics dashboard
- Operation frequency analysis

#### Testing & QA
- Unit test creation and execution
- Test data generation (from actual file patterns)
- Regression testing
- Mapping validation tests
- Test results display

#### Help & Documentation
- In-app help content
- Contextual help
- FAQ section
- Onboarding tour

## Core Modules & Functionality

### Data Processing Modules

#### `file_handler.py`
- File format detection (CSV, TXT, TSV, XLSX, JSON, Parquet)
- Delimiter detection
- Header detection using CSV sniffer
- Encoding detection with fallbacks
- Fixed-width file parsing
- Header specification file parsing
- Claims file reading with header options

#### `layout_loader.py`
- Layout file loading and caching
- Field group extraction
- Required/optional field identification
- Layout summary rendering

#### `transformer.py`
- Claims data transformation
- Field mapping application
- Data type conversion
- Cached transformation results

#### `anonymizer.py`
- Data anonymization
- PII removal
- Anonymized data generation

### Mapping Modules

#### `mapping_engine.py`
- Enhanced automap algorithm
- Field name similarity matching
- Data pattern matching
- Column type guessing
- Confidence score calculation

#### `mapping_ui.py`
- Field mapping UI rendering
- Dual input field component
- Mapping progress calculation
- Mapping table generation

#### `mapping_enhancements.py`
- Mapping confidence scores
- Mapping validation
- Mapping version control
- Mapping template export/import
- Mapping rules engine

### Validation Modules

#### `validation_engine.py`
- Required field validation
- Data type validation
- Format validation
- Cross-field validation
- Dynamic validation execution

#### `validation_builder.py`
- Custom validation rule creation
- Rule templates
- Rule execution
- Rule storage and loading

#### `advanced_validation.py`
- Cross-field relationship validation
- Business rule engine
- Validation rule templates
- Validation performance tracking
- Incremental validation
- Validation scheduling

### UI/UX Modules

#### `ui_components.py`
- Progress bars with status
- Toast notifications
- Confirmation dialogs
- Status indicators
- Tooltips

#### `ui_improvements.py`
- Onboarding tour
- Contextual help
- Session timeout management
- Activity tracking

#### `ui_styling.py`
- Dark mode support
- Responsive design CSS
- Custom styling injection
- UX JavaScript enhancements

#### `advanced_features.py`
- Dark mode toggle
- Keyboard shortcuts (Ctrl+Z, Ctrl+Y, Ctrl+A, etc.)
- Mapping template management
- Theme management

### Data Quality Modules

#### `data_quality.py`
- Data quality score calculation (cached)
- Duplicate detection (cached)
- Column statistics (cached)
- Outlier detection (cached)
- Completeness matrix (cached)
- Data profile generation (cached)
- Data sampling

### Performance Modules

#### `performance_utils.py`
- Lazy DataFrame rendering (pagination)
- Data caching with hash-based invalidation
- DataFrame pagination utilities
- Performance optimization utilities

#### `performance_scalability.py`
- Parallel file processing
- Streaming processing for large files
- Memory optimization
- Background job execution
- Result caching

### User Experience Modules

#### `user_experience.py`
- User preferences management
- Recent files tracking
- Favorites/bookmarks
- Global search across all tabs
- Notification center
- Help content management

### Monitoring & Logging Modules

#### `monitoring_logging.py`
- Persistent audit log (file-based)
- Error tracking and statistics
- Usage analytics tracking
- System health monitoring
- Log export functionality

### Testing & QA Modules

#### `testing_qa.py`
- Unit test creation and execution
- Test data generation (analyzes actual file patterns)
- Regression testing
- Mapping validation tests
- Test data generation from claims/layout files

### Collaboration Modules

#### `collaboration.py`
- Comments and annotations
- Approval workflow
- Change tracking
- Mapping documentation generation

### Data Transformation Modules

#### `data_transformation_advanced.py`
- Data cleaning pipeline
- Data enrichment
- Data normalization
- Data deduplication
- Data aggregation

### Visualization Modules

#### `visualization_reporting.py`
- Interactive charts
- Validation dashboard
- Mapping visualization
- Data flow diagrams
- Comparison views

### Batch Processing Modules

#### `batch_processor.py`
- Multiple file processing
- Batch mapping application
- Batch output generation

### Utility Modules

#### `utils.py`
- Claims file summary rendering
- General utility functions

#### `session_state.py`
- Undo/redo functionality
- Mapping history management
- Session state initialization

#### `cache_utils.py`
- Layout file caching
- Lookup file caching
- Cache management

#### `upload_handlers.py`
- File upload handling
- Metadata capture
- File validation

#### `upload_ui.py`
- Upload UI rendering
- Claims preview rendering
- Lookup summary rendering

#### `output_generator.py`
- Output file generation
- ZIP file creation
- Template management

#### `improvements_utils.py`
- Debouncing utilities
- Progress indicators
- Error handling utilities
- Input validation
- Empty state rendering
- Loading skeleton rendering

## UI/UX Features

### User Interface Enhancements
- **Dark Mode**: Full dark mode support with toggle
- **Responsive Design**: Mobile and tablet support via CSS media queries
- **Keyboard Shortcuts**:
  - Ctrl+Z: Undo
  - Ctrl+Y: Redo
  - Ctrl+A: Apply All Mappings
  - Ctrl+Shift+C: Clear All
  - Ctrl+D: Download
  - Ctrl+Arrow: Navigate tabs
- **Progress Indicators**: Visual feedback for long operations
- **Toast Notifications**: Non-intrusive success/error messages
- **Confirmation Dialogs**: Prevent accidental actions
- **Tooltips**: Contextual help for complex features
- **Empty States**: Informative messages when no data available
- **Loading Skeletons**: Placeholder UI during data loading
- **Lazy Loading**: Paginated tables for large datasets
- **Sortable Tables**: Click column headers to sort
- **Filterable Tables**: Search and filter table data
- **Debouncing**: Reduced unnecessary processing on rapid input

### User Experience Features
- **Onboarding Tour**: First-time user guidance
- **Session Timeout**: Automatic session management
- **Activity Log**: Real-time activity tracking in sidebar
- **Global Search**: Search across all tabs and data
- **Notification Center**: Centralized notifications
- **Recent Files**: Quick access to recently used files
- **Favorites**: Bookmark frequently used items
- **Help System**: Contextual help and FAQ

## Performance & Optimization Features

### Caching
- Layout file caching (`@st.cache_data`)
- Lookup file caching (`@st.cache_data`)
- Validation results caching
- Data quality calculations caching (6 functions)
- Transformation results caching

### Performance Optimizations
- Lazy loading for large DataFrames
- Pagination for validation results
- Debounced user inputs
- Reduced `st.rerun()` calls (using state flags)
- Memory optimization utilities
- Background job processing

### Scalability Features
- Parallel file processing
- Streaming processing for large files
- Memory usage monitoring
- CPU usage tracking
- Performance metrics collection

## Data Quality Features

### Quality Metrics
- Overall data quality score (0-100)
- Completeness percentage
- Uniqueness analysis
- Consistency checks
- Accuracy validation

### Analysis Tools
- Duplicate detection with details
- Outlier detection with statistics
- Column statistics (count, unique, nulls, types)
- Data completeness matrix
- Data profiling dashboard
- Data sampling

## Validation Features

### Built-in Validations
- Required field validation
- Data type validation
- Format validation (dates, numbers, etc.)
- Cross-field validation
- Mandatory field compliance

### Custom Validations
- Custom validation rule builder
- Rule templates
- Rule execution engine
- Validation performance tracking

### Validation Results
- Summary dashboard
- Detailed results (paginated)
- Field-level status
- File-level summary
- Error explanations
- Rejection reasons

## Testing & QA Features

### Test Generation
- Test data generation from actual file patterns
- Pattern analysis (formats, ranges, lengths)
- Realistic data generation matching actual structure
- Test data from claims file
- Test data from layout file

### Test Execution
- Unit test creation
- Unit test runner
- Regression testing
- Mapping validation tests
- Test results display

## Security & Privacy Features

### Data Protection
- Data anonymization
- PII removal
- Secure file handling
- Session timeout
- Audit logging

## Export & Import Features

### Export Formats
- CSV
- TXT
- XLSX
- JSON
- Parquet

### Export Options
- Anonymized claims file
- Mapping table
- Validation results
- Data quality reports
- Audit logs
- ZIP file with all outputs

### Import Features
- Mapping template import
- Layout file import
- Claims file import
- Lookup file import
- Header file import

## Technical Details

### Supported File Formats
- **Input**: CSV, TXT, TSV, XLSX, XLS, JSON, Parquet
- **Output**: CSV, TXT, XLSX, JSON, Parquet, ZIP

### Technologies
- **Framework**: Streamlit
- **Data Processing**: Pandas
- **File Handling**: Built-in Python libraries
- **Caching**: Streamlit cache_data
- **UI**: Streamlit components + custom CSS/JavaScript

### Architecture
- Modular design with separate modules for each feature
- Cached operations for performance
- Session state management
- Event-driven updates
- Error handling throughout

## Recent Improvements

### Test Data Generator Enhancement
- Analyzes actual file patterns (formats, ranges, lengths)
- Generates realistic test data matching actual structure
- Preserves data formats (date formats, ID patterns, etc.)
- Uses actual value distributions when available

### UI/UX Improvements
- Lazy loading for large tables
- Debouncing for search inputs
- Caching for data quality functions
- Empty states throughout app
- Loading skeletons
- Tooltips for complex features

### Bug Fixes
- Fixed `render_tooltip` import error
- Removed redundant preview rows
- Fixed all syntax errors
- Improved error handling

## Dependencies

Key Python packages required:
- streamlit
- pandas
- openpyxl (for Excel files)
- psutil (for system health monitoring)

## Usage Workflow

1. **Setup**: Upload layout file, claims file, and optional lookup files
2. **Mapping**: Map source columns to internal fields (manual or AI-assisted)
3. **Preview & Validate**: Review transformed data and run validations
4. **Data Quality**: Analyze data quality and completeness
5. **Downloads**: Generate and download output files
6. **Tools & Analytics**: Monitor system health and usage

## Notes

- All major features are implemented and functional
- Performance optimizations are in place (caching, lazy loading)
- UI/UX improvements enhance user experience
- Comprehensive error handling throughout
- Extensive validation capabilities
- Robust data quality analysis tools

