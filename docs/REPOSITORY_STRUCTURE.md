# Repository Structure — MIIE v1.5.0

**Date:** 2026-07-02

---

## Directory Tree

```
MIIE/
├── .github/                    # GitHub configuration
│   └── workflows/              # CI/CD workflows
├── archive/                    # Historical, experimental, and temporary files
│   ├── debug/                  # Debug scripts and outputs
│   ├── experimental/           # Experimental features
│   ├── legacy/                 # Legacy code
│   └── temporary/              # Temporary benchmark outputs
├── assets/                     # Static assets (templates, fixtures)
├── benchmarks/                 # Benchmark evaluation system
│   ├── annotations/            # Annotation workflow
│   ├── datasets/               # Candidate datasets (120 repos)
│   ├── ground_truth/           # Ground truth data
│   ├── metadata/               # Benchmark metadata
│   └── runners/                # Benchmark runner code
├── docs/                       # Documentation
│   ├── adr/                    # Architecture Decision Records
│   ├── architecture/           # Technical specifications
│   ├── release/                # Release engineering documents
│   ├── specifications/         # Scientific specifications (OEAS, ODSS, DES, etc.)
│   └── validation/             # Validation and audit reports
├── examples/                   # Usage examples
├── reports/                    # Generated reports
│   ├── benchmarking/           # Benchmark evaluation results
│   ├── implementation/         # Implementation reports
│   ├── release/                # Release engineering reports
│   └── validation/             # Validation campaign outputs
├── scripts/                    # Developer scripts and utilities
├── src/                        # Source code
│   └── miie/                   # Main package
│       ├── api/                # REST API
│       ├── benchmark/          # Benchmark evaluation
│       ├── config/             # Configuration loader
│       ├── contracts/          # Data contracts
│       ├── orchestration/      # Pipeline orchestration
│       ├── processing/         # Core processing
│       │   ├── detection/      # Anomaly detectors
│       │   ├── evaluation/     # Evaluation engine
│       │   ├── explanation/    # Explanation engine
│       │   ├── extraction/     # Data extraction
│       │   ├── observation/    # Observation storage
│       │   ├── reporting/      # Report generation
│       │   └── scoring/        # Scoring engine
│       ├── reporting/          # Report generation
│       │   └── templates/      # Jinja2 templates
│       ├── sampling/           # Sampling framework (NEW)
│       ├── schemas/            # Data schemas
│       ├── scientific/         # Scientific readiness (NEW)
│       ├── storage/            # Storage
│       ├── utils/              # Utilities
│       └── validation/         # Validation service
├── tests/                      # Test suite
│   ├── api/                    # API tests
│   ├── architecture/           # Architecture tests
│   ├── benchmark/              # Benchmark tests
│   ├── contract/               # Contract tests
│   ├── fixtures/               # Test fixtures
│   ├── integration/            # Integration tests
│   ├── performance/            # Performance tests
│   ├── regression/             # Regression tests
│   ├── reproducibility/        # Reproducibility tests
│   ├── schema/                 # Schema tests
│   ├── unit/                   # Unit tests
│   └── workflow/               # Workflow tests
└── tools/                      # Developer tools
```

---

## Top-Level Directory Purposes

| Directory | Purpose | Contents |
|---|---|---|
| `.github/` | CI/CD configuration | GitHub Actions workflows |
| `archive/` | Historical preservation | Debug scripts, temporary outputs, legacy code |
| `assets/` | Static assets | Templates, fixtures, sample data |
| `benchmarks/` | Benchmark evaluation | 120 candidate repos, ground truth, evaluation scripts |
| `docs/` | Documentation | Architecture specs, scientific specs, validation reports |
| `examples/` | Usage examples | Sample code and configurations |
| `reports/` | Generated outputs | Benchmark results, validation outputs, release reports |
| `scripts/` | Developer scripts | Debug tools, validation scripts, utilities |
| `src/` | Source code | Production Python package |
| `tests/` | Test suite | Unit, integration, architecture, and regression tests |
| `tools/` | Developer tools | Development utilities |

---

## Documentation Folder Purposes

| Folder | Purpose |
|---|---|
| `docs/adr/` | Architecture Decision Records (ADRs) |
| `docs/architecture/` | Technical specifications and design documents |
| `docs/release/` | Release engineering documents (changelog, release notes, migration guide) |
| `docs/specifications/` | Scientific specifications (OEAS, ODSS, DES, DSVP, IMS, BES, PRD) |
| `docs/validation/` | Validation reports, audit reports, signoff documents |

---

## Report Folder Purposes

| Folder | Purpose |
|---|---|
| `reports/benchmarking/` | Benchmark evaluation results (D-01, D-02, D-03, summary) |
| `reports/implementation/` | Implementation reports (day-by-day execution) |
| `reports/release/` | Release engineering reports |
| `reports/validation/` | Validation campaign outputs (scientific, sampling) |

---

## Validation Outputs

| Folder | Purpose |
|---|---|
| `reports/validation/` | Scientific validation outputs (17 files) |
| `benchmarks/datasets/` | Benchmark candidate datasets (120 repos) |

---

## Navigation Guide

### For Contributors

1. Start with `README.md` for project overview
2. Read `docs/adr/` for architectural decisions
3. Check `docs/specifications/` for scientific specifications
4. Review `CONTRIBUTING.md` for contribution guidelines

### For Developers

1. Source code: `src/miie/`
2. Tests: `tests/`
3. Scripts: `scripts/`
4. Configuration: `pyproject.toml`, `.gitignore`

### For Release Engineers

1. Release docs: `docs/release/`
2. Validation reports: `docs/validation/`
3. Benchmark results: `reports/benchmarking/`
4. Release checklist: `docs/release/COMMIT_READINESS_REPORT.md`

### For Researchers

1. Scientific specs: `docs/specifications/`
2. Validation outputs: `reports/validation/`
3. Benchmark datasets: `benchmarks/datasets/`
4. Ground truth: `benchmarks/ground_truth/`
