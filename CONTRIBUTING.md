# Contributing to MIIE

Thank you for your interest in contributing to MIIE! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.10-3.13
- Git
- Poetry (recommended) or pip

### Setup

```bash
# Clone the repository
git clone https://github.com/Samragya013/miie.git
cd miie

# Install with Poetry (recommended)
poetry install
poetry run pre-commit install

# Or with pip
pip install -e ".[dev]"
pip install pre-commit
pre-commit install
```

### Verify Setup

```bash
# Run tests
make test-unit

# Run linting
make lint

# Run type checking
make typecheck
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow existing code style
- Add tests for new functionality
- Update documentation if needed

### 3. Run Quality Checks

```bash
# Run all checks
make check

# Or run individually
make lint
make typecheck
make test-unit
```

### 4. Commit

```bash
git add .
git commit -m "feat: add new feature"
```

We use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `test:` — Tests
- `refactor:` — Code refactoring
- `chore:` — Maintenance

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Create a pull request on GitHub with:
- Clear description of changes
- Link to related issues
- Test results

## Code Style

### Python

- Line length: 120 characters
- Formatter: black
- Import sorting: isort (profile: black)
- Linting: flake8 + flake8-bugbear
- Type checking: mypy

### Running Formatters

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check without modifying
black --check src/ tests/
isort --check-only src/ tests/
```

## Testing

### Test Structure

```
tests/
├── unit/           # Individual module tests
├── integration/    # End-to-end pipeline tests
├── contract/       # Interface compliance tests
├── architecture/   # Layer dependency tests
├── benchmark/      # Benchmark execution tests
├── schema/         # Schema validation tests
└── regression/     # Regression tests
```

### Writing Tests

```python
# tests/unit/test_my_feature.py
import pytest
from miie.my_module import my_function


def test_my_function_basic():
    """Test basic functionality."""
    result = my_function(input)
    assert result == expected


def test_my_function_edge_case():
    """Test edge case."""
    with pytest.raises(ValueError):
        my_function(bad_input)
```

### Running Tests

```bash
# All tests
make test-all

# Unit tests only
make test-unit

# Specific test file
pytest tests/unit/test_my_feature.py -v

# With coverage
pytest tests/ --cov=miie --cov-report=html
```

## Frozen Core

Some components are **frozen** and cannot be modified without explicit justification. See `docs/architecture/FROZEN_CORE_RATIONALE.md` for details.

### What's Frozen?

- Statistical methods (D-01, D-02, D-03)
- Confidence scoring parameters
- Integrity scoring parameters
- Evidence generation logic

### How to Modify Frozen Components

1. Document the reason
2. Provide evidence
3. Get approval from two maintainers
4. Version the change
5. Update `FROZEN_CORE_RATIONALE.md`

## Documentation

### Building Docs

```bash
# If using MkDocs
mkdocs serve
```

### Writing Docs

- Use clear, concise language
- Include code examples
- Update the table of contents

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/Samragya013/miie/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Samragya013/miie/discussions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
