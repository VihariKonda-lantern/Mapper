# ADR-001: View Model Pattern for Tab Separation

**Status**: Accepted  
**Date**: 2025-01-XX  
**Deciders**: Development Team  
**Tags**: [architecture, ui, separation-of-concerns]

## Context

The application had UI logic mixed with business logic in tab render functions. This made:
- Testing difficult
- Code reuse challenging
- Maintenance complex
- Business logic tightly coupled to Streamlit UI

We needed a way to separate concerns while maintaining the existing Streamlit-based UI.

## Decision

We adopted a View Model pattern where:
- Each tab has a corresponding ViewModel class
- ViewModels handle business logic and state management
- Tab render functions use ViewModels for data and actions
- ViewModels are testable without Streamlit dependencies

Implementation:
- Created `TabViewModel` base class
- Implemented `SetupTabViewModel`, `MappingTabViewModel`, `ValidationTabViewModel`
- ViewModels provide `get_view_data()` and `handle_action()` methods

## Consequences

### Positive
- Business logic is now testable independently
- UI and logic are clearly separated
- Code is more maintainable
- Easier to add new tabs following the pattern

### Negative
- Additional abstraction layer
- Slight learning curve for developers
- Migration of existing tabs requires refactoring

### Neutral
- Backward compatibility maintained
- Gradual migration possible

## Alternatives Considered

### Alternative 1: MVC Pattern
- More complex structure
- Overkill for Streamlit app
- Rejected: Too heavyweight

### Alternative 2: Keep Current Structure
- No separation of concerns
- Difficult to test
- Rejected: Doesn't solve the problem

## References

- View Model Pattern: https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel
- Implementation: `app/core/view_models.py`

