# Contributing to MIIE

Thank you for your interest in contributing to MIIE! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- Poetry

### Setup Steps

```bash
# Clone the repository
git clone https://github.com/Samragya013/miie.git
cd miie

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Run tests to verify setup
poetry run pytest tests/unit/ -x -q
```

## Branching Strategy

- `main` — Stable release branch
- `develop` — Active development branch
- `feature/*` — Feature branches
- `fix/*` — Bug fix branches
- `release/*` — Release preparation branches

### Workflow

1. Create a feature branch from `develop`
2. Make your changes
3. Add tests
4. Ensure CI passes
5. Submit a pull request to `develop`

## Coding Conventions

### Style

- Follow PEP 8
- Use type hints for all public functions
- Write docstrings for public functions and classes
- Maximum line length: 88 characters (Black default)

### Code Quality

```bash
# Format code
poetry run black src/ tests/

# Sort imports
poetry run isort src/ tests/

# Lint
poetry run flake8 src/ tests/

# Type check
poetry run mypy src/miie/ --ignore-missing-imports
```

### Naming Conventions

- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- Prefix private methods with `_`

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest tests/

# Run unit tests only
poetry run pytest tests/unit/

# Run with coverage
poetry run pytest tests/ --cov=src/miie --cov-report=term-missing

# Run specific test file
poetry run pytest tests/unit/test_scoring_engine.py
```

### Writing Tests

- Write tests for all new features
- Aim for ≥90% code coverage
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Mock external dependencies

### Test Structure

```
tests/
├── unit/           # Unit tests (isolated, fast)
├── schema/         # Schema validation tests
├── contract/       # Interface contract tests
├── architecture/   # Architecture compliance tests
├── integration/    # Integration tests
├── workflow/       # End-to-end workflow tests
├── regression/     # Regression tests
├── performance/    # Performance tests
└── benchmark/      # Benchmark validation tests
```

## Pull Request Process

### Before Submitting

1. Ensure all tests pass: `poetry run pytest tests/`
2. Format code: `poetry run black src/ tests/`
3. Sort imports: `poetry run isort src/ tests/`
4. Lint: `poetry run flake8 src/ tests/`
5. Update documentation if needed

### PR Template

```markdown
## Description
[Describe your changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added (if applicable)
- [ ] Coverage maintained/improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. Submit PR to `develop` branch
2. CI must pass
3. At least one approval required
4. Address review comments
5. Merge via squash or rebase

## Architecture

MIIE follows a 9-stage pipeline architecture:

```
Ingestion → Extraction → Segmentation → Detection → Scoring → Evidence → Explanation → Reporting
```

### Key Principles

- **Deterministic**: Same input → same output
- **Offline-first**: No external API calls during analysis
- **Evidence-based**: All claims backed by executable evidence
- **Frozen architecture**: Changes require RFC process

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
