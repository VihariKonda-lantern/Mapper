# Code Style Guide

This project uses automated code formatting and linting tools to maintain code quality and consistency.

## Tools

- **Black**: Code formatter
- **Ruff**: Fast Python linter
- **isort**: Import sorter
- **mypy**: Static type checker
- **pre-commit**: Git hooks for automatic checks

## Setup

### Install Tools

```bash
pip install black ruff isort mypy pre-commit
```

### Install Pre-commit Hooks

```bash
pre-commit install
```

This will automatically run checks before each commit.

## Usage

### Format Code

```bash
# Format all Python files
black .

# Format specific file
black app/main.py
```

### Lint Code

```bash
# Run ruff linter
ruff check .

# Auto-fix issues
ruff check . --fix
```

### Sort Imports

```bash
# Sort imports in all files
isort .

# Sort imports in specific file
isort app/main.py
```

### Type Checking

```bash
# Run mypy type checker
mypy app/
```

### Run All Checks

```bash
# Run pre-commit on all files
pre-commit run --all-files
```

## Configuration

Configuration files:
- `pyproject.toml` - Black, Ruff, isort, mypy, pylint settings
- `.pre-commit-config.yaml` - Pre-commit hooks configuration

## IDE Integration

### VS Code

Add to `.vscode/settings.json`:

```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### PyCharm

1. Install Black, Ruff, isort plugins
2. Configure formatter: Settings → Tools → Black
3. Enable format on save

## Code Style Rules

### Line Length
- Maximum line length: 100 characters

### Imports
- Standard library imports first
- Third-party imports second
- Local imports last
- Use absolute imports when possible

### Type Hints
- Use type hints for function parameters and return values
- Use `Optional[T]` for nullable types
- Use `Any` sparingly

### Docstrings
- Use Google-style docstrings
- Include Args, Returns, Raises sections

### Naming
- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

## Continuous Integration

These tools can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Black
  run: black --check .

- name: Run Ruff
  run: ruff check .

- name: Run isort
  run: isort --check-only .

- name: Run mypy
  run: mypy app/
```

