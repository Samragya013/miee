# Dependency Rules

## Layer Interaction Model

MIIE v1.0 follows a strict layered architecture where dependencies flow downward through layers, except for the Storage and Common layers which are shared dependencies.

```
┌─────────────────┐
│  INTERFACE      │←───────────────┐
└─────────────────┘                │
          ▼                        │
┌─────────────────┐                │
│ ORCHESTRATION   │                │
└─────────────────┘                │
          ▼                        │
┌─────────────────┐                │
│  PROCESSING     │◄───────────────┘
└─────────────────┘
          ▲
          │
┌─────────────────┐
│   STORAGE       │◄───────────────┐
└─────────────────┘                │
          ▲                        │
┌─────────────────┐                │
│    COMMON       │◄───────────────┘
└─────────────────┘
```

## Allowed Import Directions

1. **Interface Layer** → Orchestration Layer, Common Layer
2. **Orchestration Layer** → Processing Layer, Storage Layer, Common Layer
3. **Processing Layer** → Storage Layer, Detection Layer, Schemas Layer, Contracts Layer, Common Layer
4. **Benchmark Subsystem** → Processing Layer, Storage Layer, Detection Layer, Schemas Layer, Contracts Layer, Common Layer
5. **Storage Layer** → Common Layer
6. **Detection Layer** → Schemas Layer, Contracts Layer, Common Layer
7. **Contracts Layer** → Schemas Layer, Common Layer
8. **Schemas Layer** → Common Layer
9. **Reporting Layer** → Schemas Layer, Contracts Layer, Common Layer
10. **Common Layer** → None (independent)

## Forbidden Import Directions

1. **Orchestration Layer** → Interface Layer (creates circular dependency)
2. **Processing Layer** → Interface Layer, Orchestration Layer (violates layer separation)
3. **Processing Layer** → Benchmark Subsystem (should be independent subsystems)
4. **Benchmark Subsystem** → Interface Layer, Orchestration Layer (wrong direction)
5. **Storage Layer** → Interface Layer, Orchestration Layer, Processing Layer, Benchmark Subsystem, Detection Layer, Contracts Layer, Schemas Layer, Reporting Layer (storage should be dependency-free)
6. **Detection Layer** → Interface Layer, Orchestration Layer, Processing Layer, Benchmark Subsystem, Storage Layer (wrong direction)
7. **Contracts Layer** → Interface Layer, Orchestration Layer, Processing Layer, Benchmark Subsystem, Storage Layer, Detection Layer, Reporting Layer (contracts should be dependency-free downward)
8. **Schemas Layer** → Interface Layer, Orchestration Layer, Processing Layer, Benchmark Subsystem, Storage Layer, Detection Layer, Contracts Layer, Reporting Layer (schemas should be dependency-free)
9. **Reporting Layer** → Interface Layer, Orchestration Layer, Processing Layer, Benchmark Subsystem, Storage Layer, Detection Layer (should receive data, not access logic directly)
10. **Common Layer** → Any other layer (creates reverse dependencies)

## Circular Dependency Policy

- **Strictly Prohibited:** No circular dependencies allowed between any modules
- **Detection:** Circular dependencies are detected through static analysis in CI
- **Prevention:** Use dependency injection and interface-based programming to break potential cycles
- **Validation:** Architecture tests enforce this policy (see test_no_circular_imports.py)

## Architecture Governance Rules

1. **Review Requirement:** All new modules or significant structural changes must be reviewed against this document
2. **Dependency Changes:** Any change to allowed/forbidden dependencies requires architecture review
3. **Layer Violations:** Direct layer skipping (e.g., Interface → Processing) is prohibited without architecture approval
4. **Dependency Declaration:** All external dependencies must be declared in pyproject.toml with pinned versions
5. **Interface Stability:** Once published, interfaces in Contracts and Schemas layers should maintain backward compatibility within v1.0.x

## Explicit Examples

### ✅ ALLOWED: Proper Layer Dependencies
```python
# In src/miie/orchestration/pipeline.py (Orchestration Layer)
from miie.processing.ingestion import ingest_repository  # Processing Layer ✓
from miie.storage.cache import get_cache_path           # Storage Layer ✓
from miie.common.helpers import generate_run_id         # Common Layer ✓

# In src/miie/processing/extraction.py (Processing Layer)
from miie.schemas.repository import RepositoryContext   # Schemas Layer ✓
from miie.contracts.requests import IngestionRequest    # Contracts Layer ✓
from miie.detection.base import BaseDetector            # Detection Layer ✓
from miie.common.validation import validate_repo_path   # Common Layer ✓
```

### ❌ FORBIDDEN: Improper Layer Dependencies
```python
# In src/miie/processing/ingestion.py (Processing Layer)
from miie.interface.cli import cli                      # Interface Layer ✗ (Wrong direction)
from miie.orchestration.pipeline import PipelineController # Orchestration Layer ✗ (Wrong direction)

# In src/miie/storage/cache.py (Storage Layer)
from miie.processing.pipeline import PipelineController   # Processing Layer ✗ (Storage should be independent)
from miie.detection.detector_01 import DriftDetector     # Detection Layer ✗ (Storage should be independent)

# In src/miie/common/helpers.py (Common Layer)
from miie.interface.cli import cli                       # Interface Layer ✗ (Common should be independent)
from miie.processing.ingestion import ingest_repository  # Processing Layer ✗ (Common should be independent)
```

### ❌ FORBIDDEN: Layer Skipping
```python
# In src/miie/interface/cli.py (Interface Layer)
from miie.processing.extraction import extract_metrics   # Processing Layer ✗ (Should go through Orchestration)
from miie.detection.detector_01 import detect_drift      # Detection Layer ✗ (Should go through Orchestration→Processing)
```

## Enforcement Mechanism

1. **Static Analysis:** Custom pytest enforces import rules (see tests/architecture/)
2. **Code Review:** All PRs checked for layer compliance
3. **CI Validation:** Architecture tests run on every commit
4. **Documentation:** This file serves as the canonical reference