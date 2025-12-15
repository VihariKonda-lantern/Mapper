# Architecture Documentation

This directory contains architecture decision records (ADRs) and system architecture documentation.

## Architecture Decision Records (ADRs)

ADRs document important architectural decisions made in this project. Each ADR follows a standard format and includes:
- Context: The situation that led to the decision
- Decision: The architectural decision
- Consequences: Positive and negative impacts

### ADR Template

See `adr-template.md` for the standard ADR template.

## System Architecture

### Overview

The Claims Mapper App follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│    (UI Components, Tabs, Views)     │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│          Business Logic Layer        │
│   (Services, View Models, Handlers)  │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│           Data Access Layer          │
│   (Repositories, File Handlers)     │
└─────────────────────────────────────┘
                  │
┌─────────────────────────────────────┐
│            Data Layer                │
│   (DataFrames, Models, Storage)     │
└─────────────────────────────────────┘
```

### Key Components

1. **Core Layer** (`app/core/`)
   - Configuration management
   - State management
   - Dependency injection
   - Event system
   - Base classes and protocols

2. **Services Layer** (`app/services/`)
   - Business logic services
   - Mapping service
   - Validation service

3. **Data Layer** (`app/data/`)
   - Data transformation
   - Data quality
   - Output generation

4. **UI Layer** (`app/ui/`)
   - UI components
   - Styling
   - User experience utilities

5. **File Layer** (`app/file/`)
   - File handling
   - File processing
   - File strategies

6. **Validation Layer** (`app/validation/`)
   - Validation engine
   - Validation rules
   - Validation templates

7. **Mapping Layer** (`app/mapping/`)
   - Mapping engine
   - Mapping management
   - Mapping enhancements

### Design Patterns

- **Repository Pattern**: Data access abstraction
- **Service Layer Pattern**: Business logic encapsulation
- **Factory Pattern**: Dynamic object creation
- **Strategy Pattern**: Algorithm selection
- **Observer Pattern**: Event handling
- **View Model Pattern**: UI/business logic separation

### Data Flow

1. User uploads files → File Handler
2. Files processed → Data Transformation
3. Field mapping → Mapping Engine
4. Validation → Validation Engine
5. Results displayed → UI Components

### Technology Stack

- **Framework**: Streamlit
- **Data Processing**: Pandas
- **Type Checking**: mypy
- **Testing**: pytest
- **Code Quality**: Black, Ruff, isort

