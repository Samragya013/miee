# Repository Audit Report

**Document:** REPOSITORY_AUDIT_REPORT.md
**Phase:** Phase 1 — Repository Audit & Implementation Kickoff
**Source:** Automated codebase scan (2026-06-29)
**Status:** COMPLETE

---

## 1. Executive Summary

The MIIE v1.0.1 repository contains **60 Python source files** (~9,390 lines) and **67 test files** (~9,500 lines) across **17 packages**. The codebase is functional, passes all 730 tests, and has a green CI pipeline. However, several structural observations have been identified that affect v1.5 Observation Engine implementation planning.

**Overall Health:** GOOD — 13/17 packages are active and functional. 2 empty packages to delete, 1 reserved for v2.0.

---

## 2. Source Tree Inventory

### 2.1 Package-Level Summary

| Package | Files | Lines | Status | Notes |
|---------|-------|-------|--------|-------|
| api | 5 | ~400 | ✅ ACTIVE | FastAPI server, endpoints, dependencies, models, middleware |
| benchmark | 5 | ~800 | ✅ ACTIVE | Generator, runner, evaluation, candidates, utils |
| cli | 1 | 1,332 | ✅ ACTIVE | 10 CLI commands, main entry point |
| common | 1 | 13 | ⚠️ EMPTY | Only `__init__.py` — **DELETE** |
| config | 3 | ~200 | ✅ ACTIVE | Loader (frozen dataclass), defaults, logging |
| contracts | 5 | ~500 | ✅ ACTIVE | Interfaces (10 Protocols), errors, dataclasses, validators |
| detection | 1 | 13 | ⚠️ EMPTY | Only `__init__.py` — **DELETE** (detection logic in processing/detection/) |
| interface | 1 | 13 | ⚠️ EMPTY | Only `__init__.py` — **DELETE** |
| miie (root) | 4 | ~2,200 | ✅ ACTIVE | `__init__.py`, `cli.py`, `api.py`, `version.py` |
| orchestration | 2 | ~400 | ✅ ACTIVE | Pipeline, CLI integration |
| processing | 1 | 53 | ✅ ACTIVE | `__init__.py` (aggregates subpackages) |
| reporting | 1 | 13 | ⚠️ EMPTY | Only `__init__.py` — reporting logic in processing/reporting/ |
| schemas | 6 | ~1,800 | ✅ ACTIVE | Models (1003 lines), registry, serialization, 4 JSON schemas |
| storage | 1 | 13 | 🔒 RESERVED | Reserved for v2.0 — do not modify |
| tests | 3 | ~100 | ✅ ACTIVE | Conftest, fixtures, factories |
| utils | 3 | ~400 | ✅ ACTIVE | Git (GitURLParser, GitCloner), hashing, seed |
| validation | 1 | ~80 | ✅ ACTIVE | Validation service |

### 2.2 Processing Subpackage Deep Dive

The `processing/` package is the core engine — **14 Python files, ~6,000+ lines**:

| Subpackage | Files | Key Classes | Lines |
|------------|-------|-------------|-------|
| processing/ | 1 | `ProcessingModule` | 53 |
| processing/detection/ | 8 | `BaseDetector`, `DetectorDispatcherEngine`, D-01/D-02/D-03, registry, runner, mock | ~1,600 |
| processing/scoring/ | 3 | `ScoringEngine`, mock | ~600 |
| processing/explanation/ | 3 | `ExplanationEngine`, mock | ~250 |
| processing/reporting/ | 3 | `ReportGenerator`, formatter, utils | ~700 |
| processing/benchmark/ | 1 | BenchmarkEngine | 162 |
| processing/evaluation/ | 1 | EvaluationEngine | 85 |
| processing/ | 1 | ExtractionEngine | (in extraction.py) |
| processing/ | 1 | IngestionEngine | (in ingestion.py) |
| processing/ | 1 | SegmentationEngine | (in segmentation.py) |
| processing/ | 1 | EvidenceEngine | (in evidence.py) |

### 2.3 Contracts & Interfaces

**10 Protocol interfaces** defined in `src/miie/contracts/interfaces.py`:

| Protocol | Method | Purpose |
|----------|--------|---------|
| `IIngestionEngine` | `ingest(path)` → `RepositoryContext` | Path/URL → RepositoryContext |
| `IExtractionEngine` | `extract(context, metrics, windows?)` → `MetricDataFrame` | Metric extraction |
| `ISegmentationEngine` | `segment(df, strategy)` → `list[dict]` | Window segmentation |
| `IDetectionEngine` | `detect(df, config)` → `DetectorResult` | Single-detector execution |
| `IScoringEngine` | `score(df, config)` → `ScorePackage` | Risk scoring |
| `IExplanationEngine` | `explain(df, config)` → `ExplanationReport` | Natural language |
| `IReportingEngine` | `report(df, config)` → `ReportOutput` | Final report |
| `IBenchmarkEngine` | `run(candidate, ground_truth, config)` → `BenchmarkRun` | Benchmark execution |
| `IEvaluationEngine` | `evaluate(results, thresholds)` → `EvaluationResult` | Threshold evaluation |
| `IDetectorEngine` | (implied) | Full detector pipeline |

**New interfaces needed for v1.5:**
- `IObservationStore` — Observation persistence layer
- `IAdapterLayer` — ObservationWindow → MetricDataFrame translation

### 2.4 Schema Models

**30+ dataclasses** in `src/miie/schemas/models.py` (1,003 lines):

Core models: `RepositoryContext`, `MetricDataFrame`, `DetectorResult`, `DetectorResults`, `D01Output`, `D02Output`, `D03Output`, `WindowDefinition`, `ScorePackage`, `EvidencePackage`, `ExplanationReport`, `AnalysisResult`, `ReportOutput`, `BenchmarkRun`, `EvaluationResult`, `PipelineConfig`, `PipelineState`, `MetricDefinition`, `ExtractionOptions`, `GitIngestionSource`, `URLIngestionSource`, `RepositoryIngestionSource`, `DetectorsConfig`, `ReportingOptions`, `SegmentationConfig`.

**New models needed for v1.5:**
- `Observation` (per-commit per-metric record)
- `ObservationWindow` (subset of observations)
- `ObservationCollection` (group of windows)
- `CommitMetadata` (author, timestamp, files changed)
- `ExtractionResult` (adapter output)
- `MetricValue` (atomic metric reading)

### 2.5 Error Hierarchy

`src/miie/contracts/errors.py` (308 lines):
- `MIIEError` (base)
- `ConfigError`, `PipelineError`, `ValidationError`, `ExportError`, `BenchmarkError`, `IngestionError`, `ExtractionError`, `SegmentationError`, `DetectionError`, `ScoringError`, `ExplanationError`, `ReportingError`

**New error types needed for v1.5:**
- `ObservationError`
- `ObservationStoreError`

---

## 3. Test Inventory

### 3.1 Test Directory Structure

| Directory | Files | Lines | Focus |
|-----------|-------|-------|-------|
| tests/unit/ | 29 | ~6,000 | Per-module unit tests |
| tests/integration/ | 9 | ~1,500 | Cross-module integration |
| tests/benchmark/ | 9 | ~1,200 | D-01/D-02/D-03 validation |
| tests/contract/ | 7 | ~800 | Interface conformance |
| tests/schema/ | 7 | ~700 | Model validation |
| tests/regression/ | 1 | ~150 | Backward compatibility |
| tests/architecture/ | (dirs) | (empty) | Reserved |
| tests/workflow/ | (dirs) | (empty) | Reserved |
| tests/performance/ | (dirs) | (empty) | Reserved |
| tests/reproducibility/ | (dirs) | (empty) | Reserved |

### 3.2 Test Counts by Category

- **Unit tests:** 667
- **Integration/Regression:** 63
- **Total:** 730 — **ALL PASSING**

### 3.3 Key Test Files

| File | Tests | Covers |
|------|-------|--------|
| `test_cli.py` | ~150 | All 10 CLI commands |
| `test_cli_options.py` | ~20 | --auth-token, --verbose, --forensic, --json |
| `test_cli_privacy.py` | ~15 | Privacy filtering, Windows user path detection |
| `test_cli_progress.py` | ~20 | 7-stage progress display |
| `test_pipeline.py` | ~30 | End-to-end pipeline |
| `test_pipeline_e2e.py` | ~20 | Full pipeline with git repos |
| `test_scoring_engine.py` | ~30 | ScorePackage handling |
| `test_explanation_engine.py` | ~15 | Explanation generation |
| `test_distribution_drift.py` | ~30 | D-01 detection |
| `test_correlation_breakdown.py` | ~30 | D-02 detection |
| `test_threshold_compression.py` | ~30 | D-03 detection |
| `test_evidence_engine.py` | ~15 | Evidence serialization |
| `test_git.py` | ~20 | Git URL parsing, git log parsing |
| `test_ingestion.py` | ~20 | Ingestion engine |
| `test_segmentation.py` | ~15 | Window segmentation |
| `test_interfaces.py` | ~10 | Protocol conformance |
| `test_dataset_generator.py` | ~20 | Benchmark data generation |
| `test_benchmark_runner.py` | ~15 | Benchmark execution |

### 3.4 Test Patterns

- **Fixture-based**: Heavy use of `pytest.fixture` with `tmp_path`, `sample_repo`, `mock_git`
- **Parameterized**: D-01/D-02/D-03 tests use `@pytest.mark.parametrize` for edge cases
- **Contract tests**: `tests/contract/` validates all Protocol implementations
- **Schema tests**: `tests/schema/` validates JSON schema against dataclass serialization
- **No mocking frameworks**: Tests use `unittest.mock` and `pytest-mock` minimally
- **CI integration**: Tests run via `poetry run pytest` in all 9 CI jobs

---

## 4. Configuration & Dependencies

### 4.1 pyproject.toml

- **Python:** ^3.10, <3.13
- **Version:** 1.0.0
- **Dependencies:** click, rich, pydantic, pyyaml, gitpython, numpy, pandas, scipy, networkx, tabulate, tqdm, jsonschema, packaging, pygments
- **Dev dependencies:** pytest, pytest-cov, pytest-mock, black, isort, flake8 (with bugbear), mypy, pre-commit
- **Entry points:** `miie = "miie.cli:cli"`, `miie-api = "miie.api.server:main"`

### 4.2 CI Pipeline

`.github/workflows/ci.yml` — **9 jobs, ALL GREEN:**

| Job | Purpose | Status |
|-----|---------|--------|
| lint | Black, isort, flake8, mypy | ✅ |
| test | Unit tests (Python 3.10/3.11/3.12) | ✅ |
| integration | Integration tests | ✅ |
| contract | Contract validation | ✅ |
| schema | Schema validation | ✅ |
| benchmark | D-01/D-02/D-03 benchmarks | ✅ |
| security | Bandit, pip-audit | ✅ |
| docs | Documentation build | ✅ |
| release | Release readiness | ✅ |

---

## 5. Structural Observations

### 5.1 Empty Packages (DELETE Candidates)

| Package | Location | Reason |
|---------|----------|--------|
| common | `src/miie/common/` | Only `__init__.py`, no code |
| detection | `src/miie/detection/` | Only `__init__.py`, detection logic in `processing/detection/` |
| interface | `src/miie/interface/` | Only `__init__.py`, no code |

### 5.2 Reserved Packages (DO NOT TOUCH)

| Package | Location | Reason |
|---------|----------|--------|
| storage | `src/miie/storage/` | Reserved for v2.0 |

### 5.3 Legacy Patterns (v1.0 Technical Debt)

1. **Dual detector interfaces**: `BaseDetector` ABC (processing/detection/base.py) and `IDetectorEngine` Protocol (contracts/interfaces.py) overlap
2. **ScorePackage ambiguity**: Can be dict or dataclass depending on code path
3. **DetectorResult/DetectorResults naming**: Confusing singular/plural distinction
4. **No observation layer**: MetricDataFrame loses commit-level granularity
5. **Extraction coupling**: `MetricExtractionEngine` directly produces aggregated MetricDataFrame without intermediate observation storage

### 5.4 Files Requiring Modification for v1.5

| File | Modification | Impact |
|------|-------------|--------|
| `processing/extraction.py` | Refactor to produce Observation objects | HIGH |
| `processing/segmentation.py` | Adapt to accept ObservationStore | MEDIUM |
| `processing/detection/base.py` | Adapter layer integration | MEDIUM |
| `schemas/models.py` | Add Observation models | HIGH |
| `contracts/interfaces.py` | Add IObservationStore, IAdapterLayer | MEDIUM |
| `contracts/errors.py` | Add ObservationError types | LOW |
| `orchestration/pipeline.py` | Wire observation store into pipeline | HIGH |
| `cli.py` | Add observation-level flags | LOW |
| `config/loader.py` | Add observation config options | LOW |

### 5.5 Files Requiring NO Modification

- All detector implementations (D-01, D-02, D-03) — adapter layer handles translation
- All scoring/explanation/reporting engines — adapter layer handles translation
- All test files — existing tests preserved
- All benchmark files — benchmark evolution deferred
- `storage/` — reserved for v2.0
- `common/`, `detection/`, `interface/` — to be deleted, not modified

---

## 6. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Observation store serialization at scale | HIGH | Design with lazy evaluation; batch commits |
| Adapter layer translation overhead | MEDIUM | Profile before optimizing; keep translation simple |
| Test coverage regression | HIGH | Every change must pass existing 730 tests |
| Breaking import paths | HIGH | Only add new modules; never move existing ones |
| CI regression | MEDIUM | Run full CI suite after each PR |
| Extraction refactoring scope creep | HIGH | Strict phase gating; no feature additions |

---

## 7. Recommendations

1. **Delete empty packages** (`common/`, `detection/`, `interface/`) in a cleanup commit before v1.5 work begins
2. **Create observation package** (`processing/observation/`) as new code — no refactoring of existing modules
3. **Adapter layer as translation shim** — existing detectors continue to receive MetricDataFrame
4. **Observation store as in-memory primary** — optional JSON serialization for reproducibility
5. **Incremental PR strategy** — one PR per IMS phase, each passing all 730 tests

---

*Generated by Phase 1 Repository Audit — 2026-06-29*
