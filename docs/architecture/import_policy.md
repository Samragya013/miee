# Import Governance Policy

## Purpose
This document defines the import policy for the MIIE codebase to maintain architectural integrity, prevent circular dependencies, and ensure layer separation as defined in TRD §2.1 and ADR-001-project-foundations.md.

## Scope
This policy applies to all Python source files in the `src/miie/` directory and its subdirectories.

## Import Categories

### 1. Absolute Imports (Preferred)
All imports within the MIIE package should use absolute imports from the `miie` root.

**✅ CORRECT:**
```python
from miie.processing.ingestion import ingest_repository
from miie.schemas.repository import RepositoryContext
from miie.common.helpers import generate_run_id
```

**❌ INCORRECT:**
```python
# Relative imports that create tight coupling
from ..processing.ingestion import ingest_repository
from .schemas.repository import RepositoryContext
```

### 2. Standard Library Imports
Standard library imports should be grouped at the top, followed by third-party imports, then MIIE imports.

**✅ CORRECT:**
```python
# Standard library imports
import json
import os
from pathlib import Path
from typing import List, Optional, Dict

# Third-party imports
import click
import numpy as np
import pandas as pd

# MIIE imports
from miie.processing.ingestion import ingest_repository
from miie.schemas.repository import RepositoryContext
```

### 3. Local Imports (Within Same Package)
Imports within the same package may use relative imports but absolute imports are preferred for clarity.

**✅ ACCEPTABLE (Same Package):**
```python
# Absolute import (preferred)
from miie.common.helpers import validate_path

# Relative import (acceptable but less clear)
from .helpers import validate_path
```

## Import Rules by Layer

### Interface Layer
- **Allowed:** 
  - Orchestration layer (absolute)
  - Common layer (absolute)
  - Standard library
  - Third-party (click, fastapi, etc.)
- **Forbidden:**
  - Processing layer (direct)
  - Benchmark subsystem (direct)
  - Storage layer (direct)
  - Detection layer (direct)
  - Schemas layer (direct)
  - Contracts layer (direct)
  - Reporting layer (direct)

### Orchestration Layer
- **Allowed:**
  - Processing layer (absolute)
  - Storage layer (absolute)
  - Common layer (absolute)
  - Interface layer (for callbacks - rare)
  - Standard library
  - Third-party
- **Forbidden:**
  - Interface layer (primary direction - creates wrong dependencies)
  - Benchmark subsystem (should go through workflows)
  - Detection layer (should go through processing)
  - Schemas layer (should go through processing)
  - Contracts layer (should go through processing)
  - Reporting layer (should be final step)

### Processing Layer
- **Allowed:**
  - Storage layer (absolute)
  - Detection layer (absolute)
  - Schemas layer (absolute)
  - Contracts layer (absolute)
  - Common layer (absolute)
  - Orchestration layer (for callbacks - rare)
- **Forbidden:**
  - Interface layer (violates layer separation)
  - Orchestration layer (primary flow direction)
  - Benchmark subsystem (separate concern)
  - Reporting layer (should be final step)

### Benchmark Subsystem
- **Allowed:**
  - Processing layer (for detector usage)
  - Storage layer (absolute)
  - Detection layer (for detector definitions)
  - Schemas layer (absolute)
  - Contracts layer (absolute)
  - Common layer (absolute)
- **Forbidden:**
  - Interface layer (wrong direction)
  - Orchestration layer (wrong direction - should be independent)
  - Reporting layer (benchmark has separate reporting)

### Storage Layer
- **Allowed:**
  - Common layer (absolute)
  - Standard library (os, pathlib, etc.)
  - Third-party (if absolutely necessary and approved)
- **Forbidden:**
  - ALL OTHER MIIE LAYERS (storage should be dependency-free)

### Detection Layer
- **Allowed:**
  - Schemas layer (absolute)
  - Contracts layer (absolute)
  - Common layer (absolute)
  - Standard library (numpy, scipy, etc.)
  - Third-party statistical libraries
- **Forbidden:**
  - Interface layer
  - Orchestration layer
  - Processing layer (should be called, not call)
  - Benchmark subsystem (should be independent)
  - Storage layer (should use storage abstraction)
  - Reporting layer

### Contracts Layer
- **Allowed:**
  - Schemas layer (absolute)
  - Common layer (absolute)
  - Standard library (typing, dataclasses, etc.)
- **Forbidden:**
  - ALL OTHER MIIE LAYERS (contracts should be dependency-free downstream)

### Schemas Layer
- **Allowed:**
  - Common layer (absolute)
  - Standard library (typing, dataclasses, json, etc.)
- **Forbidden:**
  - ALL OTHER MIIE LAYERS (schemas should be dependency-free)

### Reporting Layer
- **Allowed:**
  - Schemas layer (absolute)
  - Contracts layer (absolute)
  - Common layer (absolute)
  - Standard library (json, datetime, etc.)
  - Third-party (jinja2 for templates)
- **Forbidden:**
  - Interface layer
  - Orchestration layer (should receive data, not call)
  - Processing layer (should receive processed data)
  - Benchmark subsystem (should have separate reporting if needed)
  - Storage layer (should receive data, not access files directly)
  - Detection layer (should receive results, not access logic)

### Common Layer
- **Allowed:**
  - Standard library only
  - Third-party utilities (if thoroughly vetted)
- **Forbidden:**
  - ALL OTHER MIIE LAYERS (common should be independent by definition)

## Import Statement Formatting

### 1. Import Organization
Group imports in this order with blank lines between groups:
1. Standard library imports
2. Third-party imports
3. MIIE imports (grouped by layer)
4. Local application imports (same package)

### 2. Import Style
- Use `from module import item` for specific items
- Use `import module` for modules when accessing multiple items
- Avoid `from module import *` (star imports)
- Keep imports alphabetized within each group when practical

### 3. Line Length
Adhere to 79-character limit (PEP 8) for import statements. Use line continuation for long imports:
```python
from miie.processing.ingestion import (
    ingest_repository,
    validate_repository,
    extract_repository_metadata
)
```

## Review Process

### 1. Pre-Commit Checks
- Import compliance is verified by pre-commit hooks
- Architecture tests run on every commit
- CI pipeline fails on import violations

### 2. Pull Request Review
- Reviewers must check for import policy compliance
- Architectural layer violations must be addressed before merge
- Import-related technical debt should be documented in issues

### 3. Ongoing Compliance
- Architecture compliance scans run weekly
- Import violations are tracked as technical debt
- Semi-annual architecture review evaluates policy effectiveness

## Violation Handling

### 1. Immediate Violations
- Must be fixed before code can be merged
- Blocked by CI/CD pipeline
- Requires architectural review if policy exception is needed

### 2. Exceptions
- Exceptions to this policy require:
  - Written justification
  - Architecture review approval
  - Documentation in ADR-XXX-import-exception.md
  - Compensating controls to maintain system integrity

### 3. Legacy Code
- Existing violations should be fixed opportunistically
- When modifying a file with import violations, fix the violations in that file
- Technical debt sprints should address import violations

## Tools and Automation

### 1. Pre-Commit Hooks
- `flake8` with custom import ordering plugin
- Custom import validation script
- Architecture test suite

### 2. IDE Integration
- Recommended: Configure IDE to flag import policy violations
- Suggested settings for common IDEs in `.vscode/settings.json`

### 3. Documentation
- This policy is documentation in `docs/architecture/import_policy.md`
- Referenced in CONTRIBUTING.md
- Included in onboarding materials

## Compliance Metrics

### 1. Target
- 100% import policy compliance for new code
- ≤ 5% import debt in existing code (measured by violations/KLOC)

### 2. Measurement
- Architecture test suite (`tests/architecture/`)
- Custom import validation scripts
- Dependency graph analysis tools

### 3. Reporting
- Monthly architecture compliance report
- Trend analysis of import violations over time
- Executive summary for technical leadership

## References
- TRD_MIIE_v1.0.md §2.1 (Layer Responsibilities)
- ADR-001-project-foundations.md (Architectural Foundations)
- dependency_rules.md (Formal Dependency Specifications)
- PEP 8 -- Style Guide for Python Code
- PEP 328 -- Imports: Multi-Line and Absolute/Relative