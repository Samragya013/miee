# Production Source Tree Definition — PR-1A

**Date:** 2026-06-29
**Scope:** Official repository structure for MIIE v1.5

---

## Repository Layout

```
miie/
├── src/
│   └── miie/
│       ├── __init__.py                 # Version: 1.0.0
│       ├── cli.py                      # CLI entry point (10 commands)
│       ├── api/                        # FastAPI server
│       │   ├── __init__.py
│       │   ├── server.py
│       │   ├── dependencies.py
│       │   └── models.py
│       ├── benchmark/                  # Benchmark evaluation
│       │   ├── __init__.py
│       │   ├── generator.py
│       │   ├── runner.py
│       │   └── evaluation.py
│       ├── config/                     # Configuration
│       │   ├── __init__.py
│       │   └── loader.py
│       ├── contracts/                  # Protocol definitions & errors
│       │   ├── __init__.py
│       │   ├── interfaces.py           # 11 Protocols (10 + IObservationStore)
│       │   ├── errors.py               # MIIEError hierarchy (32 error types)
│       │   ├── dataclasses.py
│       │   └── validators.py
│       ├── orchestration/              # Pipeline orchestration
│       │   ├── __init__.py
│       │   └── pipeline.py
│       ├── processing/                 # Core processing
│       │   ├── __init__.py
│       │   ├── ingestion.py
│       │   ├── extraction.py
│       │   ├── segmentation.py
│       │   ├── evidence.py
│       │   ├── detection/              # Detectors
│       │   │   ├── __init__.py
│       │   │   ├── base.py
│       │   │   ├── dispatcher.py
│       │   │   ├── registry.py
│       │   │   ├── runner.py
│       │   │   ├── distribution_drift_detector.py
│       │   │   ├── correlation_breakdown_detector.py
│       │   │   ├── threshold_compression_detector.py
│       │   │   └── mock_detectors.py
│       │   ├── observation/            # v1.5 Observation Core
│       │   │   ├── __init__.py
│       │   │   ├── models.py           # ODSS observation models
│       │   │   └── store.py            # InMemoryObservationStore
│       │   ├── scoring/
│       │   ├── explanation/
│       │   ├── reporting/
│       │   ├── benchmark/
│       │   └── evaluation/
│       ├── reporting/                  # Report generation
│       │   └── __init__.py
│       ├── schemas/                    # Data models & schemas
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── metric_registry.py
│       │   ├── serialization.py
│       │   └── *.schema.json
│       ├── storage/                    # Reserved for v2.0
│       │   └── __init__.py
│       ├── utils/                      # Utilities
│       │   ├── __init__.py
│       │   ├── git.py
│       │   ├── hashing.py
│       │   └── seed.py
│       └── validation/                 # Validation service
│           ├── __init__.py
│           └── service.py
├── tests/
│   ├── unit/                           # 31 files, ~700+ tests
│   ├── integration/                    # 9 files, ~63 tests
│   ├── benchmark/                      # 9 files
│   ├── contract/                       # 7 files
│   ├── schema/                         # 7 files
│   ├── regression/                     # 1 file
│   ├── architecture/                   # Package structure tests
│   └── conftest.py
├── benchmarks/                         # Benchmark datasets & ground truth
├── docs/                               # Architecture documentation
├── scripts/                            # Developer utilities (excluded from tooling)
├── archive/                            # Historical outputs (gitignored)
├── pyproject.toml                      # Project config
├── setup.cfg                           # Tool config (flake8, mypy, pytest)
├── .pre-commit-config.yaml             # Pre-commit hooks
├── .gitignore                          # Git ignore rules
├── README.md
├── LICENSE
└── poetry.lock
```

---

## Key Metrics

| Metric | Value |
|---|---|
| Production Python files (src/) | 62 |
| Test files (tests/) | 77 |
| Total tests | 1010 |
| Test pass rate | 100% |
| CLI commands | 10 |
| Protocol interfaces | 11 |
| Error types | 32 |
| Detectors | 3 |
| Frozen metrics | 7 (M-01 through M-07) |
| Packages | 14 active |
