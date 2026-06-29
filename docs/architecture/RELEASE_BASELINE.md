# MIIE v1.0.1 — Release Baseline

**Date:** 2026-06-29
**Status:** Frozen Engineering Baseline
**Tag:** v1.0.1
**Purpose:** Establish the immutable engineering baseline from which v1.5 scientific development will begin.

---

## 1. Purpose

This document defines the frozen engineering baseline for MIIE v1.0.1. It serves as the single source of truth for what is guaranteed stable, what is frozen, and what may change in v1.5. Any deviation from this baseline requires a formal version bump and baseline update.

---

## 2. Repository Snapshot

| Attribute | Value |
|-----------|-------|
| Repository | `Samragya013/miie` |
| Latest Tag | `v1.0.1` |
| Release Date | 2026-06-27 |
| License | MIT |
| Python | ^3.10, <3.13 |
| Package Manager | Poetry 2.4.1 |
| CI/CD | GitHub Actions (9 jobs) |
| Test Count | 730 (667 unit + 63 integration/regression) |
| Lint | black, isort, flake8, mypy |
| Pre-commit | 5 hooks (black, isort, flake8, mypy, whitespace) |

### Git Tags

| Tag | Commit | Date | Purpose |
|-----|--------|------|---------|
| `v1.0.0` | `aa599b4` | 2026-06-27 | First public release |
| `v1.0.1` | `4c4d5e6` | 2026-06-27 | CI stabilization and release certification |

### Commits Since v1.0.0

```
4c4d5e6 fix(ci): add missing jsonschema dep + fix cross-platform integration test
d524d3b fix(ci): resolve GitHub Actions failures
de7991a fix(ci): regenerate poetry.lock and stabilize GitHub Actions
a7229d8 fix(ci): regenerate poetry.lock to match pyproject.toml
b6bcf94 fix(ci): resolve lint and typecheck failures for CI certification
```

---

## 3. Architecture Snapshot

### Package Structure

```
src/miie/
├── __init__.py          # Package version
├── __main__.py          # CLI entry point
├── cli.py               # 10 CLI commands (1332 lines)
├── api/                 # REST API (6 endpoints)
├── benchmark/           # Benchmark generation and running
├── common/              # Shared utilities
├── config/              # Configuration loading (YAML/JSON)
├── contracts/           # Error model, interfaces
├── detection/           # (Legacy module path)
├── interface/           # (Legacy module path)
├── orchestration/       # Pipeline controller
├── processing/          # Core processing engines
│   ├── benchmark/
│   ├── detection/       # 3 anomaly detectors
│   ├── evaluation/
│   ├── explanation/
│   ├── reporting/
│   └── scoring/
├── reporting/           # (Legacy module path)
├── schemas/             # Data models (Pydantic/dataclass)
├── storage/             # State management
├── utils/               # Git operations, utilities
└── validation/          # Schema validation
```

### Pipeline Architecture

```
CLI (10 commands, 3-tier output)
    │
    ▼
Pipeline (9 stages)
    │  Ingestion → Extraction → Segmentation → Detection
    │  → Scoring → Evidence → Explanation → Reporting
    │
    ▼
Detectors (3 frozen)
    │  D-01: Distribution Drift (KS test, PSI)
    │  D-02: Correlation Breakdown (Pearson/Spearman/Fisher-z)
    │  D-03: Threshold Compression (Excess Mass, Dip test)
    │
    ▼
Output (JSON, Text, Forensic evidence packages)
```

### Entry Points

| Entry Point | Target |
|-------------|--------|
| `miie` | `miie.cli:cli` |
| `miie-api` | `miie.api.server:main` |
| `python -m miie` | `miie.cli:cli` |

---

## 4. Current Detector Architecture

### D-01: Distribution Drift Detector

| Property | Value |
|----------|-------|
| Statistical Test | Kolmogorov-Smirnov two-sample test |
| Supplementary | Population Stability Index (PSI) |
| Threshold | α=0.05 (KS), PSI=0.25 |
| Minimum Sample | n≥10 per window |
| Module | `processing/detection/distribution_drift_detector.py` |

### D-02: Correlation Breakdown Detector

| Property | Value |
|----------|-------|
| Statistical Tests | Pearson r, Spearman ρ, Fisher-z transform |
| Breakdown Types | sudden_drop, sign_reversal, gradual_erosion, confidence_exclusion |
| Minimum Sample | n≥10 |
| Module | `processing/detection/correlation_breakdown_detector.py` |

### D-03: Threshold Compression Detector

| Property | Value |
|----------|-------|
| Statistical Tests | Excess Mass, Hartigan's Dip Test (KS approximation) |
| Threshold | z=1.645 (one-sided) |
| Minimum Sample | n≥20 |
| Module | `processing/detection/threshold_compression_detector.py` |

---

## 5. Current Observation Model

### Frozen Metrics (7)

| ID | Name | Unit | Range |
|----|------|------|-------|
| M-01 | Code Coverage | % | [0, 100] |
| M-02 | Commit Frequency | commits/day | [0, ∞) |
| M-03 | Code Churn | lines/commit | [0, ∞) |
| M-04 | Review Participation | reviewers/PR | [0, ∞) |
| M-05 | Review Latency | hours | [0, ∞) |
| M-06 | Issue Resolution Time | days | [0, ∞) |
| M-07 | Cyclomatic Complexity | count | [0, ∞) |

### Scoring Model

| Component | Formula | Range |
|-----------|---------|-------|
| Integrity Score (IS) | Weighted combination of detector severities | [0.0, 1.0] |
| Confidence Score (CS) | Factor-based reliability assessment | Band: high/medium/low/critical |
| Detector Weights | D-01=0.40, D-02=0.35, D-03=0.25 | Fixed |

### Confidence Factors

| Factor | Description |
|--------|-------------|
| sample_size | Per-window sample size adequacy |
| variance | Cross-window variance stability |
| missing_data | Missing data impact |
| window_balance | Balance across time windows |
| detector_success | Detector execution success rate |

### Window Strategies

| Strategy | Description | Default |
|----------|-------------|---------|
| `time` | Fixed time intervals (7-day windows) | Default |
| `commit` | Commit-count-based windows | `--window-strategy commit --window-size 100` |

---

## 6. Known Scientific Limitations

| Limitation | Impact | v1.5 Direction |
|------------|--------|----------------|
| 3 detectors only | Cannot detect all anomaly types | New detector modules |
| 7 metrics only | Limited metric coverage | Extensible metric registry |
| Correlation only | No causal inference | Causal analysis engine |
| Point-in-time | No continuous monitoring | Observation Engine |
| Single-repo only | No cross-repo comparison | Batch analysis |
| KS approximation of dip test | Statistically approximate | True Hartigan's dip test |
| No metric relationships | Detectors operate independently | Cross-metric analysis |
| Bootstrap not used | D-03 uses z-score approximation | Full bootstrap confidence |
| No adaptive thresholds | Fixed α values | Per-repo calibration |
| No trend analysis | Static window comparison | Longitudinal analysis |

---

## 7. Known UX Limitations

| Limitation | Impact | v1.5 Direction |
|------------|--------|----------------|
| CLI only | No GUI | Web dashboard |
| No REPL | No interactive exploration | Interactive mode |
| No progress bars on all commands | Some commands show no progress | Universal progress |
| No colored output in JSON mode | JSON output is plain | Structured JSON with colors |
| No batch processing | One repo at a time | Multi-repo pipeline |
| No resume capability | Long analyses must restart | Checkpoint/resume |
| No workspace management | No project-level config | Workspace concept |

---

## 8. Guaranteed Stable Components

The following components are **guaranteed stable** in v1.0.x. They will not change behavior, interface, or output format.

| Component | Stability Guarantee |
|-----------|-------------------|
| CLI command names | `analyze`, `ingest`, `detect`, `explain`, `export`, `evaluate`, `generate`, `benchmark`, `validate`, `status` |
| CLI exit codes | 0=success, 1=integrity<1.0, 2=system error, 3=validation error, 4=benchmark failure |
| CLI output format | Default/Verbose/Forensic 3-tier output |
| JSON output schema | EvidencePackage, ScorePackage, AnalysisResult schemas |
| Detector IDs | D-01, D-02, D-03 |
| Metric IDs | M-01 through M-07 |
| Scoring formula | Weighted integrity + factor-based confidence |
| Error hierarchy | MIIEError → specific error types |
| Pipeline stages | 9-stage pipeline (ingest through report) |
| Config format | YAML/JSON configuration files |
| API endpoints | 6 REST endpoints under `/v1/` |

---

## 9. Components Frozen

These components are frozen for v1.0.x. Changes require version bump to v1.1.0.

| Component | Freeze Scope |
|-----------|-------------|
| Detector algorithms | D-01, D-02, D-03 statistical methods |
| Scoring formula | IS and CS computation |
| Metric definitions | M-01 through M-07 definitions and ranges |
| Schema definitions | All data models (Pydantic/dataclass) |
| Pipeline stages | 9-stage pipeline order and interface |
| CLI interface | Command names, options, exit codes |
| API endpoints | REST API contract |
| Config format | YAML/JSON schema |
| Error model | Error hierarchy and codes |
| Benchmark suites | B-01, B-02, B-03 ground truth |

---

## 10. Components Allowed to Change

These components may change in v1.0.x patches without version bump.

| Component | Allowed Changes |
|-----------|----------------|
| Internal implementation | Bug fixes, performance improvements |
| Documentation | Corrections, clarifications, additions |
| Test coverage | Additional tests |
| CI/CD | Pipeline improvements |
| Dependencies | Patch version updates |
| Error messages | Clarity improvements |
| Logging | Debug information additions |
| Comments | Code documentation |

---

## 11. Components Forbidden to Change

These components CANNOT change without a major version bump (v2.0.0).

| Component | Reason |
|-----------|--------|
| Detector statistical methods | Would break reproducibility |
| Scoring formula | Would break scoring consistency |
| Schema definitions | Would break serialization |
| CLI command names | Would break user scripts |
| API endpoint paths | Would break client integrations |
| Error hierarchy | Would break error handling |
| Pipeline stage order | Would break analysis flow |
| Metric definitions | Would break metric registry |
| Exit codes | Would break automation scripts |

---

## 12. Branching Strategy

| Branch | Purpose | Protection |
|--------|---------|------------|
| `main` | Stable release branch | Protected, requires CI pass |
| `develop` | Active development | Feature merge target |
| `feature/*` | Feature branches | From develop |
| `fix/*` | Bug fix branches | From develop or main |
| `release/*` | Release preparation | From develop |

### Workflow

1. Create feature branch from `develop`
2. Implement changes with tests
3. Ensure CI passes
4. Submit PR to `develop`
5. Merge via squash or rebase
6. For releases: `develop` → `main` with version tag

---

## 13. Migration Strategy

### From v1.0.1 to v1.5

1. **Branch**: Create `v1.5-dev` from `v1.0.1` tag
2. **Baseline**: This document is the reference point
3. **Scientific work**: New detectors, metrics, and engines in v1.5-dev
4. **Backward compatibility**: v1.0.1 output format remains valid
5. **Schema evolution**: New fields added (not removed) in v1.5
6. **Deprecation**: v1.0.x features deprecated for 2 minor versions before removal

### Version Bumping Rules

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| Bug fix | Patch (1.0.x) | Fix detector edge case |
| New feature | Minor (1.x.0) | Add new detector |
| Breaking change | Major (x.0.0) | Change scoring formula |

---

## 14. Dependencies

### Runtime

| Package | Version Constraint | Purpose |
|---------|-------------------|---------|
| Python | ^3.10, <3.13 | Runtime |
| numpy | ^1.26.0 | Numerical computation |
| pandas | ^2.1.0 | Data manipulation |
| scipy | ^1.12.0 | Statistical tests |
| jinja2 | 3.1.2 | Template rendering |
| click | 8.1.3 | CLI framework |
| pyyaml | 6.0.1 | Config parsing |
| jsonschema | >=4.17.0 | Schema validation |
| fastapi | 0.100.0 | REST API framework |

### Dev

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | ^7.0.0 | Testing |
| pytest-cov | ^4.0.0 | Coverage |
| black | ^23.0.0 | Formatting |
| isort | ^5.12.0 | Import sorting |
| flake8 | ^6.0.0 | Linting |
| mypy | ^1.0.0 | Type checking |
| pre-commit | ^3.0.0 | Git hooks |

---

## 15. CI/CD Pipeline

| Job | Python | Purpose | Status |
|-----|--------|---------|--------|
| lint | 3.12 | black, isort, flake8 | ✅ PASS |
| typecheck | 3.12 | mypy | ✅ PASS |
| unit-tests (3.10) | 3.10 | Unit tests | ✅ PASS |
| unit-tests (3.11) | 3.11 | Unit tests | ✅ PASS |
| unit-tests (3.12) | 3.12 | Unit tests | ✅ PASS |
| integration-tests | 3.12 | Integration tests | ✅ PASS |
| regression | 3.12 | Regression tests | ✅ PASS |
| detector-regression | 3.12 | Detector regression | ✅ PASS |
| security | 3.12 | pip-audit, safety | ✅ PASS |

---

## 16. Version Consistency Status

### FINDING: Version Mismatch

The `v1.0.1` tag exists on the repository but the version strings throughout the codebase remain at `1.0.0`. This was a CI stabilization release (jsonschema dep fix, cross-platform test fix) that did not warrant a code version bump.

| Location | Expected | Actual | Status |
|----------|----------|--------|--------|
| `pyproject.toml` | 1.0.1 | 1.0.0 | ⚠️ DEFERRED |
| `src/miie/__init__.py` | 1.0.1 | 1.0.0 | ⚠️ DEFERRED |
| `src/miie/api/__init__.py` | 1.0.1 | 1.0.0 | ⚠️ DEFERRED |
| CLI `--version` | 1.0.1 | 1.0.0 | ⚠️ DEFERRED |
| README badge | v1.0.1 | v1.0.0 | ⚠️ DEFERRED |
| Hardcoded strings | 1.0.1 | 1.0.0 | ⚠️ DEFERRED |
| Git tag | v1.0.1 | v1.0.1 | ✅ CORRECT |

**Decision**: v1.0.1 tag is a CI stabilization release. Version strings remain at 1.0.0 intentionally — the v1.0.1 tag marks the CI-stable commit, not a new software version. This baseline treats the code version as 1.0.0 and the tag as the CI stabilization marker.

---

*This baseline is authoritative. All v1.5 development begins from this point.*
