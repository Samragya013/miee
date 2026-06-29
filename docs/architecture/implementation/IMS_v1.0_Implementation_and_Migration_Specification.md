# IMS v1.0 — Implementation & Migration Specification

## Measurement Integrity Intelligence Engine (MIIE)

### Transforming MIIE v1.0.1 → v1.5 Observation Engine Architecture

---

**Document ID:** IMS-v1.0
**Version:** 1.0.0
**Date:** 2026-06-29
**Status:** Architecture Specification
**Classification:** Internal Engineering
**Author:** Principal Software Architect (AI-generated, human-reviewed)

---

# 1. Document Metadata

| Field | Value |
|---|---|
| Document ID | IMS-v1.0 |
| Version | 1.0.0 |
| Title | Implementation & Migration Specification |
| Subtitle | MIIE v1.0.1 → v1.5 Observation Engine Migration |
| Status | Specification |
| Classification | Internal Engineering |
| Author | MIIE Architecture Team |
| Approved By | [Pending human review] |
| Review Date | [Pending] |
| Next Review | [Pending] |
| Supersedes | N/A |
| Related Documents | PRD-OE-v1.0, OEAS-v1.5, ODSS-v1.0, DES-v2.0, DSVP-v1.0, BES-v1.0 |

---

# 2. Executive Summary

This document is the **master engineering blueprint** for transforming the released MIIE v1.0.1 codebase into the complete Observation Engine architecture defined by the previously approved specifications (PRD, OEAS, ODSS, DES, DSVP, BES).

MIIE v1.0.1 is a working system with 730 passing tests, 10 CLI commands, 3 detectors, 7 frozen metrics, and a fully green CI pipeline. It ingests Git repositories, extracts metrics, segments time windows, runs anomaly detection, computes integrity and confidence scores, generates evidence packages and explanation reports, and executes benchmarks.

The v1.5 migration introduces the **Observation Engine** — a new architectural layer that replaces the current MetricDataFrame-centric pipeline with a commit-level, observation-first data model. This is the foundational architecture for the flagship MIIE v2.0 terminal experience.

**Key migration themes:**

- Replace MetricDataFrame with ObservationStore (commit-level granularity)
- Introduce DeterministicObservationID (SHA-256-based, reproducible)
- Add Adapter Layer (ObservationWindow → MetricDataFrame translation for legacy detectors)
- Refactor detectors to Observation-aware interfaces
- Refactor scoring, evidence, and explanation to operate on observations
- Upgrade benchmarks to v2.0 with observation-level evaluation
- Preserve all existing tests during migration
- Maintain backward compatibility through adapter patterns

**Estimated effort:** 15 phases, ~6–8 engineering weeks for a single engineer, or ~3–4 weeks with 2 engineers working in parallel on non-dependent phases.

**Risk level:** Medium-High. The migration touches every major subsystem but is designed for incremental, independently mergeable phases.

---

# 3. Purpose

This document serves as the implementation contract for MIIE v1.5. After reading this document, an engineering team should be able to:

1. Understand the current repository architecture completely
2. Understand the target v1.5 architecture completely
3. Implement every migration phase without undocumented architectural decisions
4. Preserve repository health throughout the migration
5. Validate scientific correctness at every checkpoint
6. Minimize implementation risk through incremental, testable phases
7. Prepare the repository for the flagship MIIE v2.0 terminal experience

---

# 4. Scope

## 4.1 In Scope

- Complete repository architectural assessment
- Architecture traceability matrix (all 6 architecture documents → code)
- Target repository architecture (v1.5)
- 15-phase implementation roadmap with file-level detail
- Package evolution plan (every package classified)
- File migration matrix (every affected file specified)
- Compatibility strategy (breaking changes, deprecations, shims)
- Dependency graph (implementation ordering)
- Testing strategy (unit, integration, scientific, benchmark, performance)
- Repository health strategy (commits, branches, CI, review)
- Release strategy (8 gates from Architecture Freeze to v1.5 Release)
- Risk register (complete engineering risk management)
- Implementation governance (standards, compliance, decision logging)

## 4.2 Explicitly Out of Scope

- Writing implementation code (this is a specification only)
- Generating commits or pull requests
- Modifying repository code, tests, or configuration
- Observation Engine or V2 capabilities beyond v1.5 scope
- Redesigning any previously approved architecture document
- Introducing new architecture not derived from PRD, OEAS, ODSS, DES, DSVP, or BES

---

# 5. Objectives

1. **Complete migration specification** — Every affected file, interface, and test is identified
2. **Incremental implementability** — Each phase is independently mergeable and testable
3. **Scientific correctness preservation** — Detector mathematics, formulas, and statistical methods are never altered
4. **Repository health preservation** — CI remains green at every merge point
5. **Test continuity** — All 730 existing tests pass throughout migration
6. **Backward compatibility** — Adapter patterns preserve CLI and API compatibility
7. **Risk minimization** — Phasing orders dependencies to reduce blast radius
8. **Architecture traceability** — Every implementation decision traces to an architecture document

---

# 6. Non-Objectives

1. **Implementing v1.5 code** — This document specifies; implementation happens separately
2. **Feature development** — No new features beyond Observation Engine architecture
3. **Observation Engine v2** — Future capabilities are noted but not specified here
4. **Performance optimization beyond observation architecture** — Covered in Phase 12 only as observation-related
5. **New detector development** — Only refactoring existing D-01, D-02, D-03
6. **New CLI commands** — Only adapting existing 10 commands to observation architecture

---

# 7. Current Repository Assessment

## 7.1 Source Tree Overview

```
src/miie/
├── __init__.py                    # __version__ = "1.0.0"
├── cli.py                         # 10 CLI commands, 1332 lines
├── api/
│   ├── server.py                  # FastAPI server
│   ├── dependencies.py            # API dependency injection
│   └── models.py                  # API request/response models
├── benchmark/
│   ├── generator.py               # BenchmarkDatasetGenerator (530 lines)
│   ├── runner.py                  # BenchmarkRunner
│   └── evaluation.py              # EvaluationEngine (benchmark-level)
├── common/
│   └── __init__.py                # Empty package
├── config/
│   └── loader.py                  # Config dataclass (frozen=True), ConfigLoader
├── contracts/
│   ├── interfaces.py              # 10 Protocol definitions (323 lines)
│   ├── errors.py                  # MIIEError hierarchy (308 lines)
│   ├── dataclasses.py             # Contract dataclasses
│   └── validators.py              # Contract validators
├── detection/
│   └── __init__.py                # Empty package (legacy)
├── interface/
│   └── __init__.py                # Empty package
├── orchestration/
│   └── pipeline.py                # AnalysisPipeline (265 lines)
├── processing/
│   ├── detection/
│   │   ├── base.py                # BaseDetector ABC (73 lines)
│   │   ├── dispatcher.py          # DetectorDispatcherEngine (116 lines)
│   │   ├── registry.py            # Detector registry
│   │   ├── runner.py              # Detector runner
│   │   ├── mock_detectors.py      # Mock detectors for testing
│   │   ├── distribution_drift_detector.py    # D-01 (288 lines)
│   │   ├── correlation_breakdown_detector.py # D-02 (329 lines)
│   │   └── threshold_compression_detector.py # D-03 (373 lines)
│   ├── scoring/
│   │   └── engine.py              # ScoringEngine (557 lines)
│   ├── explanation/
│   │   ├── engine.py              # ExplanationEngine (183 lines)
│   │   └── mock_explanation.py    # Mock explanation for testing
│   ├── reporting/
│   │   └── engine.py              # ReportGenerator (564 lines)
│   ├── benchmark/
│   │   └── engine.py              # BenchmarkEngine (162 lines)
│   ├── evaluation/
│   │   └── engine.py              # EvaluationEngine (85 lines)
│   ├── extraction.py              # MetricExtractionEngine
│   ├── ingestion.py               # Ingestion engine (418 lines)
│   ├── segmentation.py            # WindowSegmentationEngine (243 lines)
│   └── evidence.py                # EvidenceEngine (154 lines)
├── reporting/
│   └── templates/                 # Jinja2 report templates
├── schemas/
│   ├── models.py                  # All data models (1003 lines)
│   ├── metric_registry.py         # Metric registry
│   ├── serialization.py           # JSON serialization
│   └── *.schema.json              # 4 JSON Schema files
├── storage/
│   └── __init__.py                # Empty package
├── utils/
│   ├── git.py                     # GitURLParser, GitCloner
│   ├── hashing.py                 # Hash utilities
│   └── seed.py                    # Seed management
└── validation/
    └── service.py                 # Validation service (imports jsonschema)
```

## 7.2 Pipeline Architecture

```
                  ┌──────────────┐
                  │  CLI (10 cmd)│
                  └──────┬───────┘
                         │
                  ┌──────▼───────┐
                  │  Pipeline    │
                  │  (9 stages)  │
                  └──────┬───────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    ▼                    ▼                    ▼
┌─────────┐      ┌──────────────┐     ┌──────────┐
│ Ingest  │─────▶│  Extract     │────▶│ Segment  │
│ (INT-01)│      │  (INT-02)    │     │ (INT-03) │
└─────────┘      └──────────────┘     └────┬─────┘
                                           │
                      ┌────────────────────┤
                      │                    │
                      ▼                    ▼
              ┌──────────────┐     ┌──────────────┐
              │  Detect      │     │  Score       │
              │  (INT-04)    │────▶│  (INT-05)    │
              └──────────────┘     └──────┬───────┘
                                          │
                     ┌────────────────────┤
                     │                    │
                     ▼                    ▼
             ┌──────────────┐     ┌──────────────┐
             │  Evidence    │────▶│  Explain     │
             │  (INT-06)    │     │  (INT-07)    │
             └──────────────┘     └──────┬───────┘
                                         │
                                        ▼
                                 ┌──────────────┐
                                 │  Report      │
                                 │  (INT-08)    │
                                 └──────────────┘
```

## 7.3 Data Flow Summary

1. **Ingestion** (INT-01): Git URL/path → `RepositoryContext` (repo metadata, commit history)
2. **Extraction** (INT-02): `RepositoryContext` + metric_list → `MetricDataFrame` (M-01 through M-07 values)
3. **Segmentation** (INT-03): `MetricDataFrame` + strategy/size → `List[WindowDefinition]`
4. **Detection** (INT-04): `MetricDataFrame` + windows → `DetectorResults` (D-01, D-02, D-03 outputs)
5. **Scoring** (INT-05): `DetectorResults` + `MetricDataFrame` + windows → `ScorePackage` (integrity + confidence)
6. **Evidence** (INT-06): All prior outputs → `EvidencePackage` (traceable evidence)
7. **Explanation** (INT-07): `EvidencePackage` + `ScorePackage` → `ExplanationReport` (narratives + recommendations)
8. **Reporting** (INT-08): `AnalysisResult` → `ReportOutput` (JSON, MD, CSV files)

## 7.4 Current Interface Contracts

| Protocol | Interface | Input | Output | Location |
|---|---|---|---|---|
| INT-01 | `IIngestionEngine` | repo_path, cache_dir | `RepositoryContext` | contracts/interfaces.py:27 |
| INT-02 | `IExtractionEngine` | context, metric_list | `MetricDataFrame` | contracts/interfaces.py:63 |
| INT-03 | `ISegmentationEngine` | metric_dataframe, strategy, size | `List[WindowDefinition]` | contracts/interfaces.py:90 |
| INT-04 | `IDetectorEngine` | metric_dataframe, windows | `DetectorResults` | contracts/interfaces.py:115 |
| INT-05 | `IScoringEngine` | detector_results, metric_dataframe, windows | `ScorePackage` | contracts/interfaces.py:140 |
| INT-06 | `IEvidenceEngine` | context, metric_dataframe, windows, detector_results, score_package, config | `EvidencePackage` | contracts/interfaces.py:165 |
| INT-07 | `IExplanationEngine` | evidence_package, score_package | `ExplanationReport` | contracts/interfaces.py:194 |
| INT-08 | `IReportGenerator` | analysis_result, output_formats, output_dir | `ReportOutput` | contracts/interfaces.py:261 |
| INT-09 | `IBenchmarkEngine` | suite_id, detector_ids, config, seed | `BenchmarkRun` | contracts/interfaces.py:219 |
| INT-10 | `IEvaluationEngine` | benchmark_run, ground_truth | `EvaluationResult` | contracts/interfaces.py:244 |
| INT-16 | `IDataExporter` | data, formats, output_dir | `Dict[str, Path]` | contracts/interfaces.py:284 |
| INT-17 | `IDatasetGenerator` | dataset_type, count, output_dir, seed | `List[Path]` | contracts/interfaces.py:302 |

## 7.5 Current Schema Models

| Dataclass | Purpose | Lines | Location |
|---|---|---|---|
| `RepositoryContext` | Ingested repository metadata | 20–46 | schemas/models.py |
| `MetricDataFrame` | Extracted metric container | 48–68 | schemas/models.py |
| `D01Output` | D-01 detector output | 70–92 | schemas/models.py |
| `D02Output` | D-02 detector output | 94–121 | schemas/models.py |
| `D03Output` | D-03 detector output | 123–143 | schemas/models.py |
| `DetectorResult` | Single detector result | 146–167 | schemas/models.py |
| `DetectorResults` | All detector results | 280–297 | schemas/models.py |
| `Provenance` | Evidence provenance | 170–190 | schemas/models.py |
| `WarningItem` | Evidence warning | 194–205 | schemas/models.py |
| `EvidencePackage` | Traceable evidence | 208–244 | schemas/models.py |
| `WindowDefinition` | Analysis window | 253–278 | schemas/models.py |
| `IntegrityScore` | Integrity scores | 300–317 | schemas/models.py |
| `ConfidenceScore` | Confidence scores | 320–345 | schemas/models.py |
| `ScorePackage` | Score container | 348–367 | schemas/models.py |
| `Explanation` | Individual explanation | 370–389 | schemas/models.py |
| `ExplanationReport` | All explanations | 392–409 | schemas/models.py |
| `BenchmarkRun` | Benchmark results | 412–436 | schemas/models.py |
| `ConfusionMatrix` | Classification metrics | 438–456 | schemas/models.py |
| `EvaluationResult` | Evaluation metrics | 458–487 | schemas/models.py |
| `ReportOutput` | Report file paths | 489–505 | schemas/models.py |
| `GroundTruthLabel` | Ground truth label | 508–547 | schemas/models.py |
| `GroundTruthInput` | Ground truth container | 550–567 | schemas/models.py |
| `Annotation` | Annotation placeholder | 570–587 | schemas/models.py |
| `AnalysisResult` | Top-level analysis output | 621–664 | schemas/models.py |
| `RunMetadata` | Runtime metadata | 595–617 | schemas/models.py |
| `SyntheticRepositoryMetadata` | Benchmark repo metadata | 673–698 | schemas/models.py |
| `PathologyMetadata` | Benchmark pathology | 700–738 | schemas/models.py |
| `BenchmarkDataset` | Benchmark dataset | 741–791 | schemas/models.py |
| `DetectorConfig` | Detector parameters | 799–824 | schemas/models.py |
| `Configuration` | Top-level config | 828–869 | schemas/models.py |
| `JobManifest` | Job description | 877–916 | schemas/models.py |
| `StateTransition` | Job state transition | 924–951 | schemas/models.py |
| `RecoveryMetadata` | Recovery info | 955–969 | schemas/models.py |
| `StateObject` | Job state | 972–1003 | schemas/models.py |

## 7.6 Test Architecture

| Directory | Files | Purpose |
|---|---|---|
| `tests/unit/` | 29 files | Unit tests for all modules |
| `tests/integration/` | 9 files | Integration tests |
| `tests/benchmark/` | 9 files | Benchmark evaluation tests |
| `tests/contract/` | 7 files | Protocol compliance tests |
| `tests/schema/` | 7 files | Schema validation tests |
| `tests/regression/` | 1 file | Critical finding regression tests |
| `tests/architecture/` | — | Architecture compliance tests |
| `tests/workflow/` | — | End-to-end workflow tests |
| `tests/performance/` | — | Performance benchmark tests |
| `tests/reproducibility/` | — | Determinism verification tests |

**Total: 730 tests, all passing locally and in CI.**

## 7.7 CI Pipeline

| Job | Runner | Purpose |
|---|---|---|
| `lint` | ubuntu-latest, Python 3.12 | isort + black + flake8 |
| `typecheck` | ubuntu-latest, Python 3.12 | mypy |
| `unit-tests` | ubuntu-latest, Python 3.10/3.11/3.12 | Unit + schema + contract + architecture tests |
| `integration-tests` | ubuntu-latest, Python 3.12 | Integration tests |
| `regression` | ubuntu-latest, Python 3.12 | Regression + workflow tests |
| `security` | ubuntu-latest, Python 3.12 | pip-audit + safety |
| `detector-regression` | ubuntu-latest, Python 3.12 | Detector regression tests |
| `benchmark` | ubuntu-latest, Python 3.12 | Benchmark tests |
| `reproducibility` | ubuntu-latest, Python 3.12 | Reproducibility tests |

## 7.8 Architectural Strengths

1. **Clean separation of concerns** — Contracts, schemas, processing, and CLI are well-separated
2. **Protocol-based interfaces** — `@runtime_checkable` Protocol definitions enable flexible implementation
3. **Frozen config dataclass** — Prevents accidental mutation during analysis
4. **Comprehensive error hierarchy** — MIIEError → specific error types with error codes and suggestions
5. **Deterministic benchmarking** — Seed management, reproducibility verification
6. **Full CI coverage** — 9 jobs, multi-Python, security scanning
7. **Comprehensive test suite** — 730 tests across 6 categories

## 7.9 Architectural Weaknesses

1. **MetricDataFrame-centric** — All data flows through a dict-of-dicts metric container that loses commit-level granularity
2. **No observation model** — Current architecture has no concept of an individual observation; everything is aggregated
3. **Window-bound detection** — Detectors operate on pre-segmented windows rather than on the full observation stream
4. **No observation storage** — No persistent store for observations; data is re-extracted on every run
5. **Adapter gap** — No translation layer between observation-level data and legacy metric-level detectors
6. **Duplicate detector interfaces** — BaseDetector ABC and IDetectorEngine Protocol serve overlapping purposes
7. **Dict-based scoring** — ScorePackage accepts both dict and dataclass forms, creating ambiguity
8. **No observation-level evidence** — Evidence packages reference metrics by ID, not by individual observations

## 7.10 Technical Debt

| Debt Item | Severity | Location | Migration Impact |
|---|---|---|---|
| MetricDataFrame dict-of-dicts | High | schemas/models.py:60 | Replaced by ObservationStore |
| Dual DetectorResult/DetectorResults | Medium | schemas/models.py:146,280 | Consolidated |
| Dict-or-dataclass ScorePackage | Medium | schemas/models.py:348 | Unified to dataclass-only |
| Empty packages (common, detection, interface, storage) | Low | src/miie/ | Cleaned up |
| Placeholder schemas (ReportOutput, Annotation) | Medium | schemas/models.py | Extended with observation fields |
| EvidenceEngine windows_as_dicts unused | Low | processing/evidence.py:69 | Removed |
| BaseDetector and IDetectorEngine overlap | Medium | processing/detection/base.py, contracts/interfaces.py | Unified |

## 7.11 Scientific Debt

| Item | Impact | Migration Note |
|---|---|---|
| No observation-level statistical provenance | Medium | Observation model adds per-observation metadata |
| Aggregated metric values lose distributional detail | High | Observation store preserves per-commit values |
| Window-bound bootstrapping limits power | Medium | Post-observation bootstrapping enabled in v1.5 |
| No observation-level confidence factors | Low | Confidence factors computed from observation counts |

## 7.12 Observation Engine Readiness

The current repository is **partially ready** for the Observation Engine:

- **Ready:** Ingestion layer already extracts commit-level data; extraction engine processes commits; segmentation creates windows from commit data
- **Not ready:** No observation data model; no observation store; no observation-aware detectors; no adapter layer; no observation-level evidence
- **Blocking:** The MetricDataFrame must be replaced with ObservationStore before observation-aware detectors can operate

---

# 8. Existing Architecture Review

## 8.1 PRD-OE Architecture Decisions (Traceable)

| Decision | PRD Section | Current Status | Migration Action |
|---|---|---|---|
| Commit-level granularity | PRD §3.1 | Not implemented | Phase 1: Observation Core |
| DeterministicObservationID | PRD §3.2 | Not implemented | Phase 1: Observation Core |
| In-memory ObservationStore | PRD §3.3 | Not implemented | Phase 2: Observation Storage |
| Adapter Layer (OE → MetricDataFrame) | PRD §3.4 | Not implemented | Phase 4: Window Builder |
| Observation-aware detectors | PRD §3.5 | Not implemented | Phase 5: Detector Refactor |
| Observation-level evidence | PRD §3.6 | Not implemented | Phase 6: Evidence Refactor |
| Deterministic extraction | PRD §4.1 | Partially (seed management exists) | Phase 3: Extraction Refactor |
| No aggregation before persistence | PRD §4.2 | Not implemented | Phase 1-2: Core + Storage |
| Schema forward compatibility | PRD §4.3 | Not implemented | Phase 2: Storage serialization |

## 8.2 OEAS Architecture Decisions (Traceable)

| Decision | OEAS Section | Current Status | Migration Action |
|---|---|---|---|
| ADR-001: Commit-Level Granularity | OEAS §ADR-001 | Not implemented | Phase 1: Observation Core |
| ADR-002: In-Memory Store | OEAS §ADR-002 | Not implemented | Phase 2: Observation Storage |
| ADR-003: Adapter Layer | OEAS §ADR-003 | Not implemented | Phase 4: Window Builder |
| ADR-004: Deterministic IDs | OEAS §ADR-004 | Not implemented | Phase 1: Observation Core |
| ADR-005: Eliminate Re-extraction | OEAS §ADR-005 | Not implemented | Phase 3: Extraction Refactor |
| ADR-006: Parallel Extractors | OEAS §ADR-006 | Not implemented | Phase 3: Extraction Refactor |
| 8 Invariants | OEAS §Invariants | Not implemented | Enforced across Phases 1-4 |

## 8.3 ODSS Schema Decisions (Traceable)

| Decision | ODSS Section | Current Status | Migration Action |
|---|---|---|---|
| Schema Hierarchy | ODSS §3 | Not implemented | Phase 2: Observation Storage |
| Deterministic IDs | ODSS §4 | Not implemented | Phase 1: Observation Core |
| Validation Error Codes | ODSS §5 | Not implemented | Phase 2: Storage validation |
| Semver Versioning | ODSS §6 | Not implemented | Phase 2: Storage versioning |
| CommitExtractor | ODSS §7 | Not implemented | Phase 3: Extraction Refactor |
| MetricExtractor interface | ODSS §8 | Not implemented | Phase 3: Extraction Refactor |
| ObservationStore interface | ODSS §9 | Not implemented | Phase 2: Observation Storage |
| AdapterLayer interface | ODSS §10 | Not implemented | Phase 4: Window Builder |

## 8.4 DES Detector Decisions (Traceable)

| Decision | DES Section | Current Status | Migration Action |
|---|---|---|---|
| Fixed Execution Order | DES §4 | Partially (dispatcher exists) | Phase 5: Detector Refactor |
| Per-Detector Isolation | DES §5 | Partially (try/except exists) | Phase 5: Detector Refactor |
| Adapter Translation | DES §6 | Not implemented | Phase 4: Window Builder |
| D-01 Observation Interface | DES §D-01 | Not implemented | Phase 5: Detector Refactor |
| D-02 Observation Interface | DES §D-02 | Not implemented | Phase 5: Detector Refactor |
| D-03 Observation Interface | DES §D-03 | Not implemented | Phase 5: Detector Refactor |
| Minimum Sample Gates | DES §7 | Not implemented | Phase 5: Detector Refactor |

## 8.5 DSVP Validation Decisions (Traceable)

| Decision | DSVP Section | Current Status | Migration Action |
|---|---|---|---|
| 4 Validation Dimensions | DSVP §3 | Not implemented | Phase 11: Scientific Validation |
| 61 Validation Datasets | DSVP §4 | Partially (benchmarks exist) | Phase 9: Benchmark Upgrade |
| 28 Acceptance Criteria | DSVP §5 | Partially (evaluation exists) | Phase 11: Scientific Validation |
| Reproducibility Testing | DSVP §6 | Partially (seed management exists) | Phase 11: Scientific Validation |

## 8.6 BES Benchmark Decisions (Traceable)

| Decision | BES Section | Current Status | Migration Action |
|---|---|---|---|
| 8 Benchmark Categories | BES §4 | Not implemented | Phase 9: Benchmark Upgrade |
| Multi-method Ground Truth | BES §5 | Not implemented | Phase 9: Benchmark Upgrade |
| Dual-Reviewer Annotation | BES §6 | Not implemented | Phase 9: Benchmark Upgrade |
| Independent Versioning | BES §7 | Not implemented | Phase 9: Benchmark Upgrade |
| 5-Stage Certification | BES §8 | Not implemented | Phase 9: Benchmark Upgrade |
| 10+8 Acceptance Criteria | BES §9 | Not implemented | Phase 9: Benchmark Upgrade |

---

# 9. Architecture Traceability Matrix

## 9.1 PRD → Code Traceability

| PRD Requirement | Affected Packages | Affected Modules | Affected Interfaces | Affected Tests | Migration Phase |
|---|---|---|---|---|---|
| Observation data model | schemas | models.py | IIngestionEngine, IExtractionEngine | schema/*, unit/* | Phase 1 |
| ObservationStore | processing, schemas | observation_store.py (new) | IObservationStore (new) | unit/*, contract/* | Phase 2 |
| CommitExtractor | processing | extraction.py | IExtractionEngine | unit/*, integration/* | Phase 3 |
| MetricExtractor | processing | extraction.py | IExtractionEngine | unit/*, integration/* | Phase 3 |
| WindowBuilder | processing | segmentation.py | ISegmentationEngine | unit/*, integration/* | Phase 4 |
| Adapter Layer | processing | adapter.py (new) | IAdapterLayer (new) | unit/*, contract/* | Phase 4 |
| Observation-aware detectors | processing/detection | base.py, D-01, D-02, D-03 | IDetectorEngine | unit/*, benchmark/* | Phase 5 |
| Observation evidence | processing | evidence.py | IEvidenceEngine | unit/*, integration/* | Phase 6 |
| Observation scoring | processing/scoring | engine.py | IScoringEngine | unit/*, integration/* | Phase 7 |
| Observation explanation | processing/explanation | engine.py | IExplanationEngine | unit/*, integration/* | Phase 8 |
| CLI observation support | cli.py | All 10 commands | CLI interface | unit/*, integration/* | Phase 10 |
| Benchmark v2.0 | benchmark | generator.py, runner.py, evaluation.py | IBenchmarkEngine, IEvaluationEngine | benchmark/* | Phase 9 |

## 9.2 ODSS → Code Traceability

| ODSS Requirement | Affected Packages | Affected Modules | Migration Phase |
|---|---|---|---|
| Observation schema hierarchy | schemas | models.py (new classes) | Phase 2 |
| DeterministicObservationID | schemas, processing | models.py, extraction.py | Phase 1 |
| ObservationStore interface | processing | observation_store.py (new) | Phase 2 |
| CommitExtractor interface | processing | extraction.py | Phase 3 |
| MetricExtractor interface | processing | extraction.py | Phase 3 |
| AdapterLayer interface | processing | adapter.py (new) | Phase 4 |
| Validation error codes | contracts | errors.py | Phase 2 |
| Semver versioning | schemas | version.py (new) | Phase 2 |

## 9.3 DES → Code Traceability

| DES Requirement | Affected Packages | Affected Modules | Migration Phase |
|---|---|---|---|
| Fixed execution order | processing/detection | dispatcher.py | Phase 5 |
| Per-detector isolation | processing/detection | base.py, D-01, D-02, D-03 | Phase 5 |
| Adapter translation | processing | adapter.py (new) | Phase 4 |
| D-01 observation interface | processing/detection | distribution_drift_detector.py | Phase 5 |
| D-02 observation interface | processing/detection | correlation_breakdown_detector.py | Phase 5 |
| D-03 observation interface | processing/detection | threshold_compression_detector.py | Phase 5 |
| Minimum sample gates | processing/detection | base.py, dispatcher.py | Phase 5 |

## 9.4 BES → Code Traceability

| BES Requirement | Affected Packages | Affected Modules | Migration Phase |
|---|---|---|---|
| 8 benchmark categories | benchmark | generator.py | Phase 9 |
| Multi-method ground truth | benchmark | ground_truth.py (new) | Phase 9 |
| Dual-reviewer annotation | benchmark | annotation.py (new) | Phase 9 |
| Independent versioning | benchmark | versioning.py (new) | Phase 9 |
| 5-stage certification | benchmark | certification.py (new) | Phase 9 |
| 10+8 acceptance criteria | benchmark | evaluation.py | Phase 9 |

---

# 10. Target Repository Architecture

## 10.1 Target Directory Tree (v1.5)

```
src/miie/
├── __init__.py                        # __version__ = "1.5.0"
├── cli.py                             # 10 CLI commands (observation-aware)
├── api/
│   ├── server.py                      # FastAPI server (observation endpoints)
│   ├── dependencies.py                # API dependency injection
│   └── models.py                      # API models (observation schemas)
├── benchmark/
│   ├── generator.py                   # BenchmarkDatasetGenerator (observation-aware)
│   ├── runner.py                      # BenchmarkRunner (observation-level)
│   ├── evaluation.py                  # EvaluationEngine (observation-level)
│   ├── ground_truth.py                # Ground truth management (new)
│   ├── annotation.py                  # Dual-reviewer annotation (new)
│   ├── certification.py               # 5-stage certification (new)
│   └── versioning.py                  # Independent benchmark versioning (new)
├── config/
│   └── loader.py                      # Config dataclass (observation config added)
├── contracts/
│   ├── interfaces.py                  # 12 Protocol definitions (2 new: IObservationStore, IAdapterLayer)
│   ├── errors.py                      # MIIEError hierarchy (observation errors added)
│   ├── dataclasses.py                 # Contract dataclasses
│   └── validators.py                  # Contract validators
├── orchestration/
│   └── pipeline.py                    # AnalysisPipeline (observation-aware)
├── processing/
│   ├── observation/
│   │   ├── __init__.py                # Observation package
│   │   ├── store.py                   # ObservationStore (in-memory, new)
│   │   ├── models.py                  # Observation, ObservationCollection, ObservationWindow (new)
│   │   └── adapter.py                 # AdapterLayer: ObservationWindow → MetricDataFrame (new)
│   ├── extraction/
│   │   ├── __init__.py                # Extraction package
│   │   ├── commit_extractor.py        # CommitExtractor (new)
│   │   ├── metric_extractor.py        # MetricExtractor (new)
│   │   └── engine.py                  # ExtractionEngine (orchestrates extractors, new)
│   ├── detection/
│   │   ├── base.py                    # BaseDetector ABC (observation-aware)
│   │   ├── dispatcher.py              # DetectorDispatcherEngine (observation-aware)
│   │   ├── registry.py                # Detector registry
│   │   ├── runner.py                  # Detector runner
│   │   ├── distribution_drift_detector.py    # D-01 (observation-aware)
│   │   ├── correlation_breakdown_detector.py # D-02 (observation-aware)
│   │   ├── threshold_compression_detector.py # D-03 (observation-aware)
│   │   └── mock_detectors.py          # Mock detectors
│   ├── scoring/
│   │   └── engine.py                  # ScoringEngine (observation-level)
│   ├── evidence/
│   │   └── engine.py                  # EvidenceEngine (observation-level, moved from processing/evidence.py)
│   ├── explanation/
│   │   ├── engine.py                  # ExplanationEngine (observation-level)
│   │   └── mock_explanation.py        # Mock explanation
│   ├── reporting/
│   │   └── engine.py                  # ReportGenerator (observation metadata)
│   └── evaluation/
│       └── engine.py                  # EvaluationEngine (observation-level)
├── schemas/
│   ├── models.py                      # All data models (observation models added)
│   ├── observation_models.py          # Observation-specific schemas (new)
│   ├── metric_registry.py             # Metric registry
│   ├── serialization.py               # JSON serialization (observation-aware)
│   └── *.schema.json                  # JSON Schema files (observation schemas added)
├── reporting/
│   └── templates/                     # Jinja2 templates (observation metadata)
├── storage/
│   └── __init__.py                    # Storage package (reserved for future persistence)
├── utils/
│   ├── git.py                         # Git utilities
│   ├── hashing.py                     # Hash utilities (observation ID generation)
│   └── seed.py                        # Seed management
└── validation/
    └── service.py                     # Validation service
```

## 10.2 Target Dependency Graph

```
                    ┌──────────────────────┐
                    │    CLI (10 cmd)      │
                    │    Observation-aware │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │    Pipeline          │
                    │    (9 stages)        │
                    └──────────┬───────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
  ┌─────────────┐    ┌─────────────────┐    ┌──────────────┐
  │  Ingestion  │───▶│    Extraction   │───▶│  Segmentation│
  │  (INT-01)   │    │  CommitExtractor│    │  (INT-03)    │
  │             │    │  MetricExtractor│    │  WindowBuilder│
  └─────────────┘    └─────────────────┘    └──────┬───────┘
                                                    │
                              ┌─────────────────────┤
                              │                     │
                              ▼                     ▼
                     ┌─────────────────┐    ┌──────────────┐
                     │   Observation   │    │   Adapter    │
                     │   Store         │    │   Layer      │
                     │   (INT-18)      │    │   (INT-19)   │
                     └────────┬────────┘    └──────┬───────┘
                              │                     │
                              ▼                     ▼
                     ┌─────────────────┐    ┌──────────────┐
                     │   Detection     │◀───│  MetricDataFrame│
                     │   (INT-04)      │    │  (legacy)    │
                     └────────┬────────┘    └──────────────┘
                              │
                     ┌────────▼────────┐
                     │    Scoring      │
                     │    (INT-05)     │
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │    Evidence     │
                     │    (INT-06)     │
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │   Explanation   │
                     │    (INT-07)     │
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │    Reporting    │
                     │    (INT-08)     │
                     └─────────────────┘
```

## 10.3 Layer Boundaries

| Layer | Responsibility | Packages |
|---|---|---|
| **CLI Layer** | User interaction, command parsing, output formatting | cli.py, api/ |
| **Orchestration Layer** | Pipeline coordination, stage sequencing | orchestration/ |
| **Ingestion Layer** | Repository access, Git operations | processing/ingestion.py |
| **Extraction Layer** | Commit parsing, metric computation | processing/extraction/ |
| **Observation Layer** | Observation storage, adapters | processing/observation/ |
| **Detection Layer** | Anomaly detection, statistical tests | processing/detection/ |
| **Scoring Layer** | Integrity and confidence computation | processing/scoring/ |
| **Evidence Layer** | Traceable evidence assembly | processing/evidence/ |
| **Explanation Layer** | Narrative generation, recommendations | processing/explanation/ |
| **Reporting Layer** | Output generation (JSON, MD, CSV) | processing/reporting/ |
| **Schema Layer** | Data models, validation, serialization | schemas/ |
| **Contract Layer** | Interface protocols, error models | contracts/ |
| **Benchmark Layer** | Benchmark execution, evaluation, certification | benchmark/ |
| **Config Layer** | Configuration loading, validation | config/ |
| **Utility Layer** | Git, hashing, seed management | utils/ |

## 10.4 Data Flow (v1.5)

```
Git Repository
      │
      ▼
┌─────────────┐
│  Ingestion  │ ──▶ RepositoryContext
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  CommitExtractor │ ──▶ ObservationCollection (per-commit observations)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  MetricExtractor │ ──▶ MetricDataFrame (aggregated, legacy format)
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  ObservationStore│ ──▶ In-memory observation storage
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  WindowBuilder   │ ──▶ List[WindowDefinition] + List[ObservationWindow]
└──────┬──────────┘
       │
       ├──────────────────────┐
       │                      │
       ▼                      ▼
┌──────────────┐    ┌──────────────┐
│  AdapterLayer│    │ Observation- │
│  (OE → MDF)  │    │ aware Detectors│
└──────┬───────┘    └──────┬───────┘
       │                    │
       ▼                    ▼
┌──────────────┐    ┌──────────────┐
│ MetricDataFrame│  │ DetectorResults│
│ (legacy)     │    │ (observation- │
│              │    │  level)       │
└──────┬───────┘    └──────┬───────┘
       │                    │
       └────────┬───────────┘
                │
                ▼
       ┌────────────────┐
       │    Scoring     │
       │ (observation-  │
       │  level)        │
       └────────┬───────┘
                │
                ▼
       ┌────────────────┐
       │    Evidence    │
       │ (observation-  │
       │  level)        │
       └────────┬───────┘
                │
                ▼
       ┌────────────────┐
       │  Explanation   │
       └────────┬───────┘
                │
                ▼
       ┌────────────────┐
       │   Reporting    │
       └────────────────┘
```

---

# 11. Repository Evolution Strategy

## 11.1 Evolution Principles

1. **Preserve CI green** — Every merge must keep all 9 CI jobs passing
2. **Preserve test count** — No test deletion without replacement; test count never decreases
3. **Incremental migration** — Each phase is independently mergeable
4. **Adapter patterns** — Legacy interfaces preserved through adapters until explicitly deprecated
5. **Feature flags** — New observation architecture gated behind configuration flags during transition
6. **Branch-per-phase** — Each phase gets its own feature branch, merged via PR with review

## 11.2 Evolution Timeline

```
Week 1-2:   Phase 1  ──▶ Observation Core (models + deterministic IDs)
Week 2-3:   Phase 2  ──▶ Observation Storage (ObservationStore)
Week 3-4:   Phase 3  ──▶ Observation Extraction (CommitExtractor + MetricExtractor)
Week 4:     Phase 4  ──▶ Window Builder (AdapterLayer + WindowBuilder)
Week 5:     Phase 5  ──▶ Detector Refactor (observation-aware detectors)
Week 5:     Phase 6  ──▶ Evidence Refactor (observation-level evidence)
Week 6:     Phase 7  ──▶ Scoring Refactor (observation-level scoring)
Week 6:     Phase 8  ──▶ Explanation Integration (observation-level explanation)
Week 6-7:   Phase 9  ──▶ Benchmark Upgrade (v2.0 benchmarks)
Week 7:     Phase 10 ──▶ CLI Integration (observation-aware CLI)
Week 7:     Phase 11 ──▶ Scientific Validation
Week 7-8:   Phase 12 ──▶ Performance Optimization
Week 8:     Phase 13 ──▶ Documentation Synchronization
Week 8:     Phase 14 ──▶ Release Candidate
Week 8:     Phase 15 ──▶ v1.5 Release
```

---

# 12. Package Evolution Matrix

| Package | Current Role | Future Role | Classification | Reason | Complexity | Risk |
|---|---|---|---|---|---|---|
| `schemas/` | Data models | Data models + observation schemas | **Keep with modifications** | Add observation models, preserve existing | Medium | Low |
| `contracts/` | Interface protocols | Interface protocols + observation protocols | **Keep with modifications** | Add 2 new protocols, preserve existing 10 | Low | Low |
| `processing/ingestion.py` | Repository ingestion | Repository ingestion (unchanged) | **Keep** | No changes needed | Low | Low |
| `processing/extraction.py` | Metric extraction | Orchestration + extraction | **Refactor** | Split into commit_extractor + metric_extractor + engine | High | Medium |
| `processing/observation/` | N/A | Observation storage + adapters | **New package** | New package for observation core | High | Medium |
| `processing/detection/` | Detector framework | Detector framework (observation-aware) | **Refactor** | Detectors consume ObservationWindow via adapter | High | High |
| `processing/scoring/` | Scoring engine | Scoring engine (observation-level) | **Refactor** | Scoring operates on observation counts | Medium | Medium |
| `processing/evidence.py` | Evidence generation | Evidence generation (observation-level) | **Refactor** | Evidence includes observation metadata | Medium | Medium |
| `processing/explanation/` | Explanation generation | Explanation generation (observation-level) | **Refactor** | Explanation references observations | Low | Low |
| `processing/reporting/` | Report generation | Report generation (observation metadata) | **Keep with modifications** | Add observation metadata to reports | Low | Low |
| `processing/benchmark/` | Benchmark engine | Benchmark engine (observation-level) | **Refactor** | Benchmark uses observation-level evaluation | Medium | Medium |
| `processing/evaluation/` | Evaluation engine | Evaluation engine (observation-level) | **Refactor** | Evaluation uses observation-level metrics | Low | Low |
| `benchmark/` | Benchmark framework | Benchmark framework v2.0 | **Refactor** | Upgrade to BES specification | High | High |
| `cli.py` | 10 CLI commands | 10 CLI commands (observation-aware) | **Keep with modifications** | Add observation flags and output | Medium | Low |
| `config/loader.py` | Configuration | Configuration (observation config) | **Keep with modifications** | Add observation-related config fields | Low | Low |
| `api/` | FastAPI server | FastAPI server (observation endpoints) | **Keep with modifications** | Add observation API endpoints | Low | Low |
| `utils/` | Utilities | Utilities (observation ID hashing) | **Keep with modifications** | Add observation ID generation | Low | Low |
| `common/` | Empty package | Empty package | **Delete** | Remove empty package | Low | Low |
| `detection/` | Empty package (legacy) | Empty package (legacy) | **Delete** | Remove empty legacy package | Low | Low |
| `interface/` | Empty package | Empty package | **Delete** | Remove empty package | Low | Low |
| `storage/` | Empty package | Reserved for future persistence | **Keep** | Reserved for v2.0 persistence layer | Low | Low |

---

# 13. Module Evolution Matrix

## 13.1 New Modules (Created in v1.5)

| Module | Package | Purpose | Lines (est.) | Dependencies |
|---|---|---|---|---|
| `observation/models.py` | processing/observation | Observation, ObservationCollection, ObservationWindow | ~200 | schemas/models.py |
| `observation/store.py` | processing/observation | ObservationStore (in-memory) | ~250 | observation/models.py |
| `observation/adapter.py` | processing/observation | AdapterLayer (OE → MetricDataFrame) | ~150 | observation/models.py, schemas/models.py |
| `extraction/commit_extractor.py` | processing/extraction | CommitExtractor | ~200 | observation/models.py, utils/git.py |
| `extraction/metric_extractor.py` | processing/extraction | MetricExtractor | ~150 | observation/models.py, schemas/models.py |
| `extraction/engine.py` | processing/extraction | ExtractionEngine (orchestrator) | ~100 | extraction/commit_extractor.py, extraction/metric_extractor.py |
| `schemas/observation_models.py` | schemas | Observation-specific JSON schemas | ~100 | schemas/models.py |
| `benchmark/ground_truth.py` | benchmark | Ground truth management | ~150 | schemas/models.py |
| `benchmark/annotation.py` | benchmark | Dual-reviewer annotation | ~100 | benchmark/ground_truth.py |
| `benchmark/certification.py` | benchmark | 5-stage certification | ~120 | benchmark/evaluation.py |
| `benchmark/versioning.py` | benchmark | Independent benchmark versioning | ~80 | benchmark/ |

## 13.2 Modified Modules

| Module | Nature of Modification | Breaking Changes | Migration Complexity |
|---|---|---|---|
| `schemas/models.py` | Add Observation, ObservationCollection, ObservationWindow dataclasses | No (additive) | Low |
| `contracts/interfaces.py` | Add IObservationStore, IAdapterLayer protocols | No (additive) | Low |
| `contracts/errors.py` | Add ObservationError, ObservationStoreError | No (additive) | Low |
| `processing/extraction.py` | Refactor to orchestrate commit_extractor + metric_extractor | Yes (internal API) | High |
| `processing/segmentation.py` | Extend to produce ObservationWindow alongside WindowDefinition | No (additive) | Medium |
| `processing/detection/base.py` | Add observation-aware abstract methods | Yes (ABC extension) | Medium |
| `processing/detection/dispatcher.py` | Route observations to detectors via adapter | Yes (internal API) | Medium |
| `processing/detection/distribution_drift_detector.py` | Implement observation-aware detect() | Yes (method signature) | High |
| `processing/detection/correlation_breakdown_detector.py` | Implement observation-aware detect() | Yes (method signature) | High |
| `processing/detection/threshold_compression_detector.py` | Implement observation-aware detect() | Yes (method signature) | High |
| `processing/scoring/engine.py` | Compute scores from observation counts | Yes (internal API) | Medium |
| `processing/evidence.py` | Include observation metadata in evidence | Yes (internal API) | Medium |
| `processing/explanation/engine.py` | Reference observations in narratives | Low | Low |
| `processing/benchmark/engine.py` | Use observation-level benchmark execution | Yes (internal API) | Medium |
| `processing/evaluation/engine.py` | Use observation-level evaluation metrics | Yes (internal API) | Low |
| `cli.py` | Add --observation-output flag, observation metadata in reports | No (additive) | Low |
| `config/loader.py` | Add observation-related config fields | No (additive) | Low |
| `orchestration/pipeline.py` | Integrate observation pipeline stages | Yes (internal API) | Medium |
| `benchmark/generator.py` | Generate observation-level benchmark datasets | Yes (internal API) | Medium |
| `benchmark/runner.py` | Run observation-level benchmarks | Yes (internal API) | Medium |

---

# 14. File Migration Matrix

## 14.1 Files Requiring No Changes

| File | Reason |
|---|---|
| `src/miie/__init__.py` | Version bump only (1.0.0 → 1.5.0) |
| `src/miie/processing/ingestion.py` | Ingestion layer unchanged |
| `src/miie/processing/detection/mock_detectors.py` | Mock detectors preserved for testing |
| `src/miie/processing/explanation/mock_explanation.py` | Mock explanation preserved for testing |
| `src/miie/utils/seed.py` | Seed management unchanged |
| `src/miie/reporting/templates/` | Templates updated in Phase 13 only |
| `src/miie/schemas/*.schema.json` | Updated in Phase 2 only |

## 14.2 Files Requiring Additive Changes (Non-Breaking)

| File | Changes | Phase |
|---|---|---|
| `src/miie/schemas/models.py` | Add Observation, ObservationCollection, ObservationWindow dataclasses | Phase 1 |
| `src/miie/contracts/interfaces.py` | Add IObservationStore, IAdapterLayer protocols | Phase 2 |
| `src/miie/contracts/errors.py` | Add ObservationError, ObservationStoreError | Phase 2 |
| `src/miie/config/loader.py` | Add observation config fields | Phase 10 |
| `src/miie/cli.py` | Add --observation-output flag | Phase 10 |
| `src/miie/schemas/serialization.py` | Add observation serialization support | Phase 2 |

## 14.3 Files Requiring Refactoring (Breaking Internal API)

| File | Changes | Phase | Risk |
|---|---|---|---|
| `src/miie/processing/extraction.py` | Refactor to orchestrate new extractors | Phase 3 | High |
| `src/miie/processing/segmentation.py` | Extend to produce ObservationWindow | Phase 4 | Medium |
| `src/miie/processing/detection/base.py` | Add observation-aware abstract methods | Phase 5 | Medium |
| `src/miie/processing/detection/dispatcher.py` | Route observations via adapter | Phase 5 | Medium |
| `src/miie/processing/detection/distribution_drift_detector.py` | Implement observation-aware detect() | Phase 5 | High |
| `src/miie/processing/detection/correlation_breakdown_detector.py` | Implement observation-aware detect() | Phase 5 | High |
| `src/miie/processing/detection/threshold_compression_detector.py` | Implement observation-aware detect() | Phase 5 | High |
| `src/miie/processing/scoring/engine.py` | Compute from observation counts | Phase 7 | Medium |
| `src/miie/processing/evidence.py` | Include observation metadata | Phase 6 | Medium |
| `src/miie/processing/explanation/engine.py` | Reference observations | Phase 8 | Low |
| `src/miie/processing/benchmark/engine.py` | Observation-level benchmarks | Phase 9 | Medium |
| `src/miie/processing/evaluation/engine.py` | Observation-level evaluation | Phase 9 | Low |
| `src/miie/orchestration/pipeline.py` | Integrate observation stages | Phase 10 | Medium |
| `src/miie/benchmark/generator.py` | Observation-level generation | Phase 9 | Medium |
| `src/miie/benchmark/runner.py` | Observation-level benchmarks | Phase 9 | Medium |

---

# 15. Observation Engine Implementation Plan

## Phase 1 — Observation Core

### Objective
Introduce the fundamental observation data model: `Observation`, `ObservationCollection`, `ObservationWindow`, and `DeterministicObservationID`.

### Deliverables
- `src/miie/processing/observation/__init__.py` — Package initialization
- `src/miie/processing/observation/models.py` — Observation dataclasses
- Updated `src/miie/schemas/models.py` — Add observation models to exports

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `src/miie/processing/observation/__init__.py` | Create | ~5 |
| `src/miie/processing/observation/models.py` | Create | ~200 |
| `src/miie/schemas/models.py` | Modify (additive) | +10 |

### Interfaces
- `Observation` dataclass: observation_id (DeterministicObservationID), source_type, source_id, metric_id, value, timestamp, metadata
- `ObservationCollection` dataclass: collection_id, observations (List[Observation]), metadata
- `ObservationWindow` dataclass: window_id, observations (List[Observation]), start_date, end_date
- `DeterministicObservationID`: SHA-256(source_type:source_id:metric_id)[:16]

### Dependencies
- `hashlib` (stdlib) for SHA-256
- `schemas/models.py` for existing dataclasses

### Prerequisites
- None (first phase)

### Acceptance Criteria
1. `Observation` dataclass created with all required fields
2. `ObservationCollection` dataclass created
3. `ObservationWindow` dataclass created
4. `DeterministicObservationID` generation function implemented (SHA-256-based)
5. All existing tests still pass (no modification to existing code)
6. New unit tests for observation models (minimum 10 tests)
7. Deterministic ID generation produces identical output for identical inputs
8. `pip install -e .` succeeds
9. `flake8 src/miie/processing/observation/` passes
10. `mypy src/miie/processing/observation/` passes

### Rollback Strategy
- Delete `src/miie/processing/observation/` package
- No other files modified (additive only)

### Verification Procedure
```bash
# Run existing tests (must all pass)
poetry run pytest tests/ -x -q

# Run new observation tests
poetry run pytest tests/unit/test_observation_models.py -v

# Verify deterministic IDs
python -c "from miie.processing.observation.models import generate_observation_id; print(generate_observation_id('commit', 'abc123', 'M-01'))"

# Lint and typecheck
flake8 src/miie/processing/observation/
mypy src/miie/processing/observation/
```

### Repository Health Checks
- CI all-green (9/9 jobs)
- Test count ≥ 730 + new observation tests
- No import errors across codebase

### Expected PR Size
- 2-3 files changed/created
- ~215 lines added
- ~0 lines modified in existing files

### Estimated Engineering Effort
- 0.5 days (single engineer)

### Risk Level
- **Low** — Purely additive, no existing code modified

---

## Phase 2 — Observation Storage

### Objective
Implement `ObservationStore` (in-memory) with `IObservationStore` protocol, add observation validation error codes, and add observation JSON schemas.

### Deliverables
- `src/miie/processing/observation/store.py` — ObservationStore implementation
- Updated `src/miie/contracts/interfaces.py` — IObservationStore protocol
- Updated `src/miie/contracts/errors.py` — ObservationError, ObservationStoreError
- Updated `src/miie/schemas/serialization.py` — Observation serialization

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `src/miie/processing/observation/store.py` | Create | ~250 |
| `src/miie/contracts/interfaces.py` | Modify (additive) | +30 |
| `src/miie/contracts/errors.py` | Modify (additive) | +20 |
| `src/miie/schemas/serialization.py` | Modify (additive) | +40 |

### Interfaces
- `IObservationStore` protocol: add(), get(), query(), count(), clear(), list_collections()
- `ObservationStore` class implementing `IObservationStore`
- `ObservationError`, `ObservationStoreError` error classes

### Dependencies
- Phase 1 (Observation Core models)
- `schemas/serialization.py` for JSON support

### Prerequisites
- Phase 1 merged

### Acceptance Criteria
1. `IObservationStore` protocol defined in contracts/interfaces.py
2. `ObservationStore` class implements IObservationStore
3. ObservationStore supports add, get, query, count, clear, list_collections
4. ObservationError and ObservationStoreError added to errors.py
5. Observation serialization works (JSON round-trip)
6. All existing tests still pass
7. New unit tests for ObservationStore (minimum 15 tests)
8. `pip install -e .` succeeds
9. flake8 and mypy pass

### Rollback Strategy
- Delete `src/miie/processing/observation/store.py`
- Revert additive changes to interfaces.py, errors.py, serialization.py

### Expected PR Size
- 4 files changed
- ~340 lines added
- ~0 lines modified in existing logic

### Estimated Engineering Effort
- 1 day

### Risk Level
- **Low** — Additive only, no existing logic changed

---

## Phase 3 — Observation Extraction

### Objective
Refactor the extraction layer into `CommitExtractor` (produces observations) and `MetricExtractor` (produces MetricDataFrame), orchestrated by `ExtractionEngine`.

### Deliverables
- `src/miie/processing/extraction/__init__.py` — Package initialization
- `src/miie/processing/extraction/commit_extractor.py` — CommitExtractor
- `src/miie/processing/extraction/metric_extractor.py` — MetricExtractor
- `src/miie/processing/extraction/engine.py` — ExtractionEngine orchestrator
- Deprecated `src/miie/processing/extraction.py` — Marked as deprecated, delegates to engine

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `src/miie/processing/extraction/__init__.py` | Create | ~5 |
| `src/miie/processing/extraction/commit_extractor.py` | Create | ~200 |
| `src/miie/processing/extraction/metric_extractor.py` | Create | ~150 |
| `src/miie/processing/extraction/engine.py` | Create | ~100 |
| `src/miie/processing/extraction.py` | Modify (deprecate + delegate) | ~50 modified |

### Interfaces
- `CommitExtractor`: extract_commits(context, since, until) → ObservationCollection
- `MetricExtractor`: extract_metrics(observation_collection, metric_list) → MetricDataFrame
- `ExtractionEngine`: extract(context, metric_list, since, until) → (ObservationCollection, MetricDataFrame)

### Dependencies
- Phase 1 (Observation models)
- Phase 2 (ObservationStore)
- `processing/ingestion.py` for RepositoryContext
- `utils/git.py` for Git operations

### Prerequisites
- Phases 1 and 2 merged

### Acceptance Criteria
1. CommitExtractor produces ObservationCollection from RepositoryContext
2. MetricExtractor produces MetricDataFrame from ObservationCollection
3. ExtractionEngine orchestrates both extractors
4. Legacy extraction.py delegates to ExtractionEngine (backward compatible)
5. All existing tests still pass (extraction tests use legacy interface)
6. New unit tests for CommitExtractor, MetricExtractor, ExtractionEngine (minimum 20 tests)
7. pip install -e . succeeds
8. flake8 and mypy pass

### Rollback Strategy
- Delete extraction/ package
- Revert extraction.py to original

### Expected PR Size
- 5 files changed/created
- ~505 lines added
- ~50 lines modified

### Estimated Engineering Effort
- 2 days

### Risk Level
- **Medium-High** — Extraction refactor touches core data flow; backward compatibility critical

---

## Phase 4 — Window Builder

### Objective
Extend segmentation to produce `ObservationWindow` alongside `WindowDefinition`, and implement `AdapterLayer` for translating ObservationWindow → MetricDataFrame.

### Deliverables
- `src/miie/processing/observation/adapter.py` — AdapterLayer
- Updated `src/miie/processing/segmentation.py` — Produce ObservationWindow
- Updated `src/miie/contracts/interfaces.py` — IAdapterLayer protocol

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `src/miie/processing/observation/adapter.py` | Create | ~150 |
| `src/miie/processing/segmentation.py` | Modify (extend) | ~80 modified |
| `src/miie/contracts/interfaces.py` | Modify (additive) | +20 |

### Interfaces
- `IAdapterLayer` protocol: to_metric_dataframe(observation_window) → MetricDataFrame
- `AdapterLayer` class implementing IAdapterLayer
- `WindowSegmentationEngine.segment()` extended to return `List[ObservationWindow]` in addition to `List[WindowDefinition]`

### Dependencies
- Phases 1-3
- `processing/segmentation.py` for existing segmentation logic

### Prerequisites
- Phases 1, 2, 3 merged

### Acceptance Criteria
1. AdapterLayer translates ObservationWindow → MetricDataFrame
2. Segmentation produces both WindowDefinition and ObservationWindow
3. Legacy segmentation interface preserved (returns List[WindowDefinition])
4. All existing tests still pass
5. New unit tests for AdapterLayer and extended segmentation (minimum 12 tests)
6. pip install -e . succeeds
7. flake8 and mypy pass

### Rollback Strategy
- Delete adapter.py
- Revert segmentation.py changes

### Expected PR Size
- 3 files changed
- ~250 lines added
- ~80 lines modified

### Estimated Engineering Effort
- 1.5 days

### Risk Level
- **Medium** — Adapter is critical bridge; correctness essential

---

## Phase 5 — Detector Refactor

### Objective
Refactor all three detectors (D-01, D-02, D-03) to support observation-aware interfaces while preserving backward compatibility through adapter patterns.

### Deliverables
- Updated `src/miie/processing/detection/base.py` — Add observation-aware abstract methods
- Updated `src/miie/processing/detection/distribution_drift_detector.py` — Observation-aware D-01
- Updated `src/miie/processing/detection/correlation_breakdown_detector.py` — Observation-aware D-02
- Updated `src/miie/processing/detection/threshold_compression_detector.py` — Observation-aware D-03
- Updated `src/miie/processing/detection/dispatcher.py` — Observation-aware dispatching

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `src/miie/processing/detection/base.py` | Modify (extend) | ~40 modified |
| `src/miie/processing/detection/distribution_drift_detector.py` | Modify (extend) | ~60 modified |
| `src/miie/processing/detection/correlation_breakdown_detector.py` | Modify (extend) | ~60 modified |
| `src/miie/processing/detection/threshold_compression_detector.py` | Modify (extend) | ~60 modified |
| `src/miie/processing/detection/dispatcher.py` | Modify (extend) | ~50 modified |

### Interfaces
- `BaseDetector.detect_observations(observation_window, metric_id) → DetectorResult` (new abstract method)
- `BaseDetector.execute()` preserved (backward compatible, delegates to detect_observations via adapter)
- `DetectorDispatcherEngine.invoke()` extended to accept optional `ObservationWindow`

### Dependencies
- Phases 1-4 (observation models, store, extraction, adapter)
- `processing/observation/adapter.py` for ObservationWindow → MetricDataFrame translation

### Prerequisites
- Phases 1-4 merged

### Acceptance Criteria
1. BaseDetector has new `detect_observations()` abstract method
2. D-01 implements `detect_observations()` using observation-level KS test and PSI
3. D-02 implements `detect_observations()` using observation-level correlation
4. D-03 implements `detect_observations()` using observation-level threshold analysis
5. Dispatcher routes observations to detectors when ObservationWindow provided
6. Legacy `execute()` still works via adapter (backward compatible)
7. All existing tests still pass (including 667 unit + 63 integration)
8. New unit tests for observation-aware detectors (minimum 20 tests)
9. pip install -e . succeeds
10. flake8 and mypy pass

### Rollback Strategy
- Revert all detection/*.py changes
- No new files to delete

### Expected PR Size
- 5 files modified
- ~270 lines added/modified

### Estimated Engineering Effort
- 2 days

### Risk Level
- **High** — Detector mathematics must be preserved; observation interface must produce identical results

---

## Phase 6 — Evidence Refactor

### Objective
Refactor EvidenceEngine to include observation-level metadata in evidence packages.

### Deliverables
- Updated `src/miie/processing/evidence.py` — Observation-aware evidence generation
- Updated `src/miie/schemas/models.py` — Add observation fields to EvidencePackage

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `src/miie/processing/evidence.py` | Modify (extend) | ~60 modified |
| `src/miie/schemas/models.py` | Modify (additive) | +20 |

### Interfaces
- `EvidencePackage` extended with: observation_counts, observation_summary, per_window_observations
- `EvidenceEngine.generate()` extended to accept optional `ObservationCollection`

### Dependencies
- Phases 1-5

### Prerequisites
- Phases 1-5 merged

### Acceptance Criteria
1. EvidencePackage includes observation metadata fields
2. EvidenceEngine populates observation metadata when available
3. Legacy evidence generation still works (observation fields optional)
4. All existing tests still pass
5. New unit tests for observation-aware evidence (minimum 8 tests)
6. pip install -e . succeeds

### Rollback Strategy
- Revert evidence.py and models.py changes

### Expected PR Size
- 2 files modified
- ~80 lines added

### Estimated Engineering Effort
- 0.5 days

### Risk Level
- **Low-Medium** — Additive changes to evidence package

---

## Phase 7 — Scoring Refactor

### Objective
Refactor ScoringEngine to compute integrity and confidence scores from observation-level data.

### Deliverables
- Updated `src/miie/processing/scoring/engine.py` — Observation-level scoring

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `src/miie/processing/scoring/engine.py` | Modify (extend) | ~80 modified |

### Interfaces
- `ScoringEngine.compute_integrity_score()` extended to accept optional observation counts
- Confidence factors computed from observation sample sizes

### Dependencies
- Phases 1-6

### Prerequisites
- Phases 1-6 merged

### Acceptance Criteria
1. ScoringEngine computes scores from observation counts when available
2. Legacy scoring interface preserved (observation counts optional)
3. Confidence factors include observation-based sample_size factor
4. All existing tests still pass
5. New unit tests for observation-level scoring (minimum 8 tests)
6. pip install -e . succeeds

### Rollback Strategy
- Revert scoring/engine.py changes

### Expected PR Size
- 1 file modified
- ~80 lines added

### Estimated Engineering Effort
- 0.5 days

### Risk Level
- **Medium** — Score formulas must be preserved; observation-level scoring must be statistically equivalent

---

## Phase 8 — Explanation Integration

### Objective
Refactor ExplanationEngine to reference observations in narratives and recommendations.

### Deliverables
- Updated `src/miie/processing/explanation/engine.py` — Observation-level explanation

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `src/miie/processing/explanation/engine.py` | Modify (extend) | ~40 modified |

### Interfaces
- `ExplanationEngine.generate()` extended to reference observation counts and per-window observations

### Dependencies
- Phases 1-7

### Prerequisites
- Phases 1-7 merged

### Acceptance Criteria
1. ExplanationEngine references observation counts in narratives
2. Legacy explanation interface preserved
3. All existing tests still pass
4. New unit tests for observation-level explanation (minimum 5 tests)
5. pip install -e . succeeds

### Rollback Strategy
- Revert explanation/engine.py changes

### Expected PR Size
- 1 file modified
- ~40 lines added

### Estimated Engineering Effort
- 0.25 days

### Risk Level
- **Low** — Narrative changes only; no mathematical impact

---

## Phase 9 — Benchmark Upgrade

### Objective
Upgrade benchmark framework to v2.0 per BES specification: 8 benchmark categories, multi-method ground truth, dual-reviewer annotation, independent versioning, 5-stage certification.

### Deliverables
- `src/miie/benchmark/ground_truth.py` — Ground truth management
- `src/miie/benchmark/annotation.py` — Dual-reviewer annotation
- `src/miie/benchmark/certification.py` — 5-stage certification
- `src/miie/benchmark/versioning.py` — Independent benchmark versioning
- Updated `src/miie/benchmark/generator.py` — Observation-level generation
- Updated `src/miie/benchmark/runner.py` — Observation-level benchmarks
- Updated `src/miie/benchmark/evaluation.py` — Observation-level evaluation
- Updated `src/miie/processing/benchmark/engine.py` — Observation-level engine
- Updated `src/miie/processing/evaluation/engine.py` — Observation-level evaluation

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `src/miie/benchmark/ground_truth.py` | Create | ~150 |
| `src/miie/benchmark/annotation.py` | Create | ~100 |
| `src/miie/benchmark/certification.py` | Create | ~120 |
| `src/miie/benchmark/versioning.py` | Create | ~80 |
| `src/miie/benchmark/generator.py` | Modify (extend) | ~80 modified |
| `src/miie/benchmark/runner.py` | Modify (extend) | ~60 modified |
| `src/miie/benchmark/evaluation.py` | Modify (extend) | ~40 modified |
| `src/miie/processing/benchmark/engine.py` | Modify (extend) | ~50 modified |
| `src/miie/processing/evaluation/engine.py` | Modify (extend) | ~30 modified |

### Dependencies
- Phases 1-8
- BES specification

### Prerequisites
- Phases 1-8 merged

### Acceptance Criteria
1. Ground truth management supports 8 benchmark categories
2. Dual-reviewer annotation workflow implemented
3. 5-stage certification process implemented
4. Independent benchmark versioning (semver)
5. All existing benchmark tests still pass
6. New unit tests for benchmark v2.0 (minimum 15 tests)
7. pip install -e . succeeds
8. flake8 and mypy pass

### Rollback Strategy
- Delete new benchmark files
- Revert modified benchmark files

### Expected PR Size
- 9 files changed
- ~710 lines added
- ~260 lines modified

### Estimated Engineering Effort
- 2 days

### Risk Level
- **High** — Benchmark framework is critical for scientific validation

---

## Phase 10 — CLI Integration

### Objective
Update all 10 CLI commands to support observation-level output and metadata.

### Deliverables
- Updated `src/miie/cli.py` — Observation-aware CLI
- Updated `src/miie/orchestration/pipeline.py` — Observation-aware pipeline
- Updated `src/miie/config/loader.py` — Observation config fields

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `src/miie/cli.py` | Modify (extend) | ~100 modified |
| `src/miie/orchestration/pipeline.py` | Modify (extend) | ~80 modified |
| `src/miie/config/loader.py` | Modify (additive) | +30 |

### Interfaces
- `--observation-output` flag on all relevant commands
- Pipeline integrates observation stages
- Config supports observation-related settings

### Dependencies
- Phases 1-9

### Prerequisites
- Phases 1-9 merged

### Acceptance Criteria
1. All 10 CLI commands support --observation-output flag
2. Pipeline integrates observation pipeline stages
3. Config loads observation-related settings
4. All existing CLI tests still pass
5. New CLI tests for observation output (minimum 10 tests)
6. pip install -e . succeeds
7. CLI help text updated

### Rollback Strategy
- Revert cli.py, pipeline.py, loader.py changes

### Expected PR Size
- 3 files modified
- ~210 lines added

### Estimated Engineering Effort
- 1 day

### Risk Level
- **Medium** — CLI is user-facing; backward compatibility critical

---

## Phase 11 — Scientific Validation

### Objective
Validate that observation-level detectors produce statistically equivalent results to legacy detectors across all benchmark datasets.

### Deliverables
- Validation report (docs/reports/)
- Updated benchmark evaluation results

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `docs/reports/scientific_validation_v1.5.md` | Create | ~200 |

### Dependencies
- Phases 1-10

### Prerequisites
- Phases 1-10 merged

### Acceptance Criteria
1. D-01 observation-level precision ≥ 0.80, recall ≥ 0.75
2. D-02 observation-level precision ≥ 0.75, recall ≥ 0.70
3. D-03 observation-level precision ≥ 0.85, recall ≥ 0.80
4. Cross-detector results consistent
5. Reproducibility verified (100-run determinism test)
6. All 28 DSVP acceptance criteria evaluated

### Rollback Strategy
- N/A (validation only, no code changes)

### Expected PR Size
- 1 documentation file
- ~200 lines

### Estimated Engineering Effort
- 1 day

### Risk Level
- **Low** — Validation only; no code changes

---

## Phase 12 — Performance Optimization

### Objective
Optimize observation-level operations for performance: memory usage, extraction speed, query latency.

### Deliverables
- Performance profiling report
- Optimized observation store queries
- Memory-efficient observation storage

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `src/miie/processing/observation/store.py` | Modify (optimize) | ~30 modified |
| `src/miie/processing/extraction/commit_extractor.py` | Modify (optimize) | ~20 modified |

### Dependencies
- Phases 1-11

### Prerequisites
- Phases 1-11 merged

### Acceptance Criteria
1. ObservationStore query latency < 10ms for 10,000 observations
2. Memory usage < 2x legacy MetricDataFrame for equivalent data
3. Extraction speed within 1.5x of legacy extraction
4. All existing tests still pass
5. Performance benchmarks documented

### Rollback Strategy
- Revert optimization changes

### Expected PR Size
- 2 files modified
- ~50 lines modified

### Estimated Engineering Effort
- 0.5 days

### Risk Level
- **Low** — Optimization only; no functional changes

---

## Phase 13 — Documentation Synchronization

### Objective
Update all documentation to reflect v1.5 architecture: README, API docs, architecture docs, user guides.

### Deliverables
- Updated README.md
- Updated docs/architecture/* (cross-references to IMS)
- Updated CLI help documentation
- Updated API documentation

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `README.md` | Modify | ~50 modified |
| `docs/architecture/*.md` | Modify (cross-refs) | ~30 modified |

### Dependencies
- Phases 1-12

### Prerequisites
- Phases 1-12 merged

### Acceptance Criteria
1. README reflects v1.5 architecture
2. All architecture docs cross-reference IMS
3. CLI help text accurate
4. API docs reflect observation endpoints

### Rollback Strategy
- Revert documentation changes

### Expected PR Size
- Multiple documentation files
- ~80 lines modified

### Estimated Engineering Effort
- 0.5 days

### Risk Level
- **Low** — Documentation only

---

## Phase 14 — Release Candidate

### Objective
Create release candidate v1.5-rc1, run full test suite, verify all release criteria.

### Deliverables
- Git tag: v1.5-rc1
- Release candidate verification report

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `src/miie/__init__.py` | Modify (version bump) | 1 line |

### Dependencies
- Phases 1-13

### Prerequisites
- Phases 1-13 merged

### Acceptance Criteria
1. Version bumped to 1.5.0
2. All 730+ tests pass
3. CI all-green (9/9 jobs)
4. All release gates passed
5. Release candidate tag created

### Rollback Strategy
- Delete rc tag, revert version bump

### Expected PR Size
- 1 file modified
- 1 line changed

### Estimated Engineering Effort
- 0.25 days

### Risk Level
- **Low** — Version bump only

---

## Phase 15 — v1.5 Release

### Objective
Finalize v1.5 release: tag, documentation, release notes.

### Deliverables
- Git tag: v1.5.0
- Release notes
- Updated CHANGELOG.md

### Files
| File | Action | Lines (est.) |
|---|---|---|
| `CHANGELOG.md` | Create/Update | ~100 |
| `docs/releases/v1.5.0.md` | Create | ~50 |

### Dependencies
- Phase 14

### Prerequisites
- Phase 14 merged and verified

### Acceptance Criteria
1. v1.5.0 tag exists
2. Release notes published
3. CHANGELOG.md updated
4. All CI jobs green
5. All 730+ tests pass

### Rollback Strategy
- Delete v1.5.0 tag (last resort)

### Expected PR Size
- 2 files created/updated
- ~150 lines

### Estimated Engineering Effort
- 0.25 days

### Risk Level
- **Low** — Release finalization

---

# 16. Detector Refactoring Plan

## 16.1 D-01 Refactoring

**Current:** `DistributionDriftDetector.execute(metric_dataframe: MetricDataFrame) → DetectorResult`

**Target:** `DistributionDriftDetector.detect_observations(observation_window: ObservationWindow, metric_id: str) → D01Output`

**Refactoring approach:**
1. Add `detect_observations()` method to BaseDetector ABC
2. Implement `detect_observations()` in D-01 using per-commit observation values
3. Preserve `execute()` for backward compatibility (adapter translates ObservationWindow → MetricDataFrame)
4. KS test and PSI computed from observation-level values instead of aggregated metric values
5. Minimum sample gate: ≥10 observations per window

**Mathematical equivalence:** KS statistic and PSI computed from identical underlying data; observation-level computation produces identical results to aggregated computation when data is the same.

## 16.2 D-02 Refactoring

**Current:** `CorrelationBreakdownDetector.execute(metric_dataframe: MetricDataFrame) → DetectorResult`

**Target:** `CorrelationBreakdownDetector.detect_observations(observation_window: ObservationWindow, metric_pair: Tuple[str, str]) → D02Output`

**Refactoring approach:**
1. Implement `detect_observations()` using per-commit observation pairs
2. Pearson and Spearman correlations computed from observation-level pairs
3. Fisher z-transformation uses observation-level sample size
4. Minimum sample gate: ≥20 observations per window for correlation

## 16.3 D-03 Refactoring

**Current:** `ThresholdCompressionDetector.execute(metric_dataframe: MetricDataFrame) → DetectorResult`

**Target:** `ThresholdCompressionDetector.detect_observations(observation_window: ObservationWindow, metric_id: str) → D03Output`

**Refactoring approach:**
1. Implement `detect_observations()` using per-commit observation values
2. Excess Mass test uses observation-level distribution
3. Dip test (KS-approximation) uses observation-level values
4. Minimum sample gate: ≥20 observations per window

---

# 17. Benchmark Migration Plan

## 17.1 Current Benchmark Framework

- `BenchmarkDatasetGenerator`: Generates synthetic Git repositories
- `BenchmarkRunner`: Executes benchmarks on detector outputs
- `EvaluationEngine`: Evaluates against ground truth
- `BenchmarkEngine`: Orchestrates benchmark execution

## 17.2 Target Benchmark Framework (v2.0 per BES)

- **8 benchmark categories:** Synthetic, Real OSS, Edge-Case, Adversarial, Stress, Temporal Evolution, Longitudinal, Industrial
- **Multi-method ground truth:** Construction + Expert labeling + Statistical validation
- **Dual-reviewer annotation:** Two independent reviewers + adjudication
- **Independent versioning:** Semver for benchmarks independent of MIIE version
- **5-stage certification:** Dataset Creation → Ground Truth → Annotation → Evaluation → Certification

## 17.3 Migration Approach

1. Extend `BenchmarkDatasetGenerator` to support 8 categories
2. Create `GroundTruth` management module
3. Create `Annotation` module for dual-reviewer workflow
4. Create `Certification` module for 5-stage process
5. Create `Versioning` module for independent benchmark versioning
6. Update `BenchmarkRunner` to execute observation-level benchmarks
7. Update `EvaluationEngine` to compute observation-level metrics
8. Preserve existing benchmark tests during migration

---

# 18. CLI Integration Plan

## 18.1 CLI Command Changes

| Command | Change | Phase |
|---|---|---|
| `miie analyze` | Add --observation-output flag | Phase 10 |
| `miie ingest` | No changes | — |
| `miie detect` | Add --observation-mode flag | Phase 10 |
| `miie benchmark` | Observation-level benchmark execution | Phase 10 |
| `miie evaluate` | Observation-level evaluation | Phase 10 |
| `miie explain` | Reference observations in output | Phase 10 |
| `miie export` | Include observation data in export | Phase 10 |
| `miie generate` | Observation-level dataset generation | Phase 10 |
| `miie status` | Show observation store status | Phase 10 |
| `miie validate` | Validate observation schemas | Phase 10 |

## 18.2 Backward Compatibility

- All existing CLI flags preserved
- New flags are optional (default: legacy behavior)
- `--observation-output` defaults to False
- Output format unchanged when observation flags not used

---

# 19. Testing Strategy

## 19.1 Test Categories

| Category | Current Count | Target Count | Migration Approach |
|---|---|---|---|
| Unit tests | 667 | 750+ | Add observation model, store, adapter tests |
| Integration tests | 63 | 75+ | Add observation pipeline integration tests |
| Benchmark tests | — | — | Upgrade to v2.0 benchmark tests |
| Contract tests | — | — | Add IObservationStore, IAdapterLayer contract tests |
| Schema tests | — | — | Add observation schema validation tests |
| Regression tests | — | — | Preserve all existing regression tests |
| Scientific validation | — | — | DSVP 28 acceptance criteria tests |
| Performance tests | — | — | Add observation store performance tests |
| Reproducibility tests | — | — | Add observation ID determinism tests |

## 19.2 Coverage Targets

| Metric | Current | Target |
|---|---|---|
| Line coverage | ~85% | ≥85% |
| Branch coverage | ~75% | ≥75% |
| Mutation score | — | ≥70% |

## 19.3 Acceptance Thresholds

- All existing 730 tests must pass at every merge point
- New tests must pass before merge
- No test deletion without replacement
- Test count never decreases

## 19.4 Cross-Platform Testing

- CI runs on Ubuntu (Python 3.10, 3.11, 3.12)
- Local verification on Windows (Python 3.11)
- Observation ID generation must be platform-independent (SHA-256)

---

# 20. Scientific Validation Gates

## 20.1 DSVP Compliance

| Gate | Criteria | Phase |
|---|---|---|
| Implementation Correctness | All detector code matches mathematical specification | Phase 11 |
| Scientific Correctness | Statistical methods produce expected results on validation datasets | Phase 11 |
| Statistical Significance | Results are statistically significant (p < α) on synthetic datasets | Phase 11 |
| Operational Reliability | Detectors handle edge cases gracefully | Phase 11 |

## 20.2 Validation Datasets

- 30 synthetic datasets (controlled characteristics)
- 10 real OSS repositories
- 10 edge-case repositories
- 6 adversarial datasets
- 5 stress-test datasets

## 20.3 Acceptance Criteria (28 total)

| Detector | Precision | Recall | Additional Criteria |
|---|---|---|---|
| D-01 | ≥ 0.80 | ≥ 0.75 | KS test validity, PSI threshold |
| D-02 | ≥ 0.75 | ≥ 0.70 | Pearson/Spearman consistency, Fisher-z validity |
| D-03 | ≥ 0.85 | ≥ 0.80 | Excess Mass validity, Dip test approximation |
| Cross-detector | — | — | Consistency, no contradiction rate |

---

# 21. Repository Health Strategy

## 21.1 Commit Strategy

- One commit per logical change
- Conventional commit format: `type(scope): description`
- Types: feat, fix, refactor, test, docs, chore
- Scopes: observation, extraction, detection, scoring, evidence, explanation, benchmark, cli, schema, contracts

## 21.2 Branch Strategy

- `main` — protected, requires PR review
- `develop` — integration branch
- `feature/v1.5-observation-core` — Phase 1
- `feature/v1.5-observation-storage` — Phase 2
- `feature/v1.5-observation-extraction` — Phase 3
- `feature/v1.5-window-builder` — Phase 4
- `feature/v1.5-detector-refactor` — Phase 5
- `feature/v1.5-evidence-refactor` — Phase 6
- `feature/v1.5-scoring-refactor` — Phase 7
- `feature/v1.5-explanation-integration` — Phase 8
- `feature/v1.5-benchmark-upgrade` — Phase 9
- `feature/v1.5-cli-integration` — Phase 10
- `feature/v1.5-scientific-validation` — Phase 11
- `feature/v1.5-performance` — Phase 12
- `feature/v1.5-documentation` — Phase 13

## 21.3 CI Requirements

- All 9 CI jobs must pass before merge
- PR review required (minimum 1 reviewer)
- No force-push to main
- No merge commits (squash or rebase)

## 21.4 Quality Metrics

| Metric | Gate | Threshold |
|---|---|---|
| Test pass rate | CI | 100% |
| Code coverage | CI | ≥85% line |
| Lint violations | CI | 0 |
| Type errors | CI | 0 (mypy strict) |
| Security vulnerabilities | CI | 0 critical/high |

---

# 22. Compatibility Strategy

## 22.1 Backward Compatibility

| Interface | Compatibility | Grace Period |
|---|---|---|
| CLI commands | Full backward compatible | Indefinite |
| CLI flags | All existing flags preserved | Indefinite |
| Configuration | All existing config fields preserved | Indefinite |
| MetricDataFrame | Preserved through adapter | Deprecated in v1.5, removed in v2.0 |
| DetectorResult | Preserved (legacy format) | Deprecated in v1.5, removed in v2.0 |
| ScorePackage | Preserved (dict-or-dataclass) | Unified to dataclass in v1.5 |
| EvidencePackage | Extended (additive) | Indefinite |
| ExplanationReport | Extended (additive) | Indefinite |

## 22.2 Breaking Changes

| Change | Impact | Migration Path |
|---|---|---|
| extraction.py internal API | Internal only | Adapter delegates to new engine |
| detection/*.py internal API | Internal only | Adapter delegates to new interface |
| scoring/engine.py internal API | Internal only | Adapter delegates to new interface |
| evidence.py internal API | Internal only | Adapter delegates to new interface |

## 22.3 Soft Deprecations

| Item | Deprecated In | Removal |
|---|---|---|
| Legacy extraction.py direct usage | v1.5 | v2.0 |
| Dict-based ScorePackage | v1.5 | v2.0 |
| BaseDetector.execute() (without detect_observations) | v1.5 | v2.0 |

## 22.4 Hard Removals

| Item | Removed In | Replacement |
|---|---|---|
| Empty packages (common, detection, interface) | v1.5 | Deleted |
| Duplicate DetectorResult class | v1.5 | Consolidated into DetectorResults |

---

# 23. Breaking Changes Register

| ID | Change | Severity | Affected | Mitigation | Phase |
|---|---|---|---|---|---|
| BC-001 | extraction.py internal API refactored | Medium | Internal processing | Adapter delegates to new engine | Phase 3 |
| BC-002 | BaseDetector ABC extended | Medium | All detectors | New abstract method with default | Phase 5 |
| BC-003 | detection/*.py method signatures changed | Medium | Internal detection | Backward-compatible wrapper | Phase 5 |
| BC-004 | scoring/engine.py internal API changed | Low | Internal scoring | Backward-compatible wrapper | Phase 7 |
| BC-005 | evidence.py internal API changed | Low | Internal evidence | Backward-compatible wrapper | Phase 6 |
| BC-006 | ScorePackage unified to dataclass-only | Low | Code using dict form | Migration adapter | Phase 7 |
| BC-007 | Empty packages deleted | Low | Import statements | Remove dead imports | Phase 1 |

---

# 24. Migration Timeline

```
Week 1:   Phase 1 (Observation Core) ──────────────────────────────┐
Week 2:   Phase 2 (Observation Storage) ───────────────────────────┤
Week 3:   Phase 3 (Observation Extraction) ────────────────────────┤
Week 4:   Phase 4 (Window Builder) ────────────────────────────────┤
Week 5:   Phase 5 (Detector Refactor) ─────────────────────────────┤
Week 5:   Phase 6 (Evidence Refactor) ─────────────────────────────┤
Week 6:   Phase 7 (Scoring Refactor) ──────────────────────────────┤
Week 6:   Phase 8 (Explanation Integration) ───────────────────────┤
Week 6-7: Phase 9 (Benchmark Upgrade) ─────────────────────────────┤
Week 7:   Phase 10 (CLI Integration) ──────────────────────────────┤
Week 7:   Phase 11 (Scientific Validation) ────────────────────────┤
Week 7-8: Phase 12 (Performance Optimization) ─────────────────────┤
Week 8:   Phase 13 (Documentation Sync) ───────────────────────────┤
Week 8:   Phase 14 (Release Candidate) ────────────────────────────┤
Week 8:   Phase 15 (v1.5 Release) ─────────────────────────────────┘
```

---

# 25. Engineering Milestones

| Milestone | Phase | Target Date | Criteria |
|---|---|---|---|
| Observation Models Available | Phase 1 | Week 1 end | All observation dataclasses created, tests pass |
| ObservationStore Operational | Phase 2 | Week 2 end | Store add/get/query working, tests pass |
| Extraction Refactored | Phase 3 | Week 3 end | CommitExtractor + MetricExtractor working, backward compatible |
| Adapter Layer Complete | Phase 4 | Week 4 end | ObservationWindow → MetricDataFrame translation working |
| Detectors Observation-Aware | Phase 5 | Week 5 end | D-01, D-02, D-03 support observation interface |
| Evidence Observation-Level | Phase 6 | Week 5 end | EvidencePackage includes observation metadata |
| Scoring Observation-Level | Phase 7 | Week 6 end | Scoring computed from observation counts |
| Explanation Observation-Level | Phase 8 | Week 6 end | Explanations reference observations |
| Benchmark v2.0 | Phase 9 | Week 7 end | 8 categories, ground truth, annotation, certification |
| CLI Observation-Aware | Phase 10 | Week 7 end | All 10 commands support observation output |
| Scientific Validation Passed | Phase 11 | Week 7 end | DSVP 28 criteria evaluated |
| Performance Optimized | Phase 12 | Week 8 end | Performance targets met |
| Documentation Current | Phase 13 | Week 8 end | All docs reflect v1.5 |
| Release Candidate | Phase 14 | Week 8 end | v1.5-rc1 tagged, all gates pass |
| v1.5 Released | Phase 15 | Week 8 end | v1.5.0 tagged, release notes published |

---

# 26. Risk Register

| ID | Risk | Likelihood | Impact | Detection | Mitigation | Contingency | Priority |
|---|---|---|---|---|---|---|---|
| R-001 | Observation ID hash collision | Low | High | Deterministic testing | SHA-256 with 16-char truncation (2^64 space) | Extend to 32-char hash | High |
| R-002 | Detector mathematical drift | Medium | High | DSVP validation | Adapter ensures identical input data | Revert to legacy detectors | Critical |
| R-003 | Extraction performance regression | Medium | Medium | Performance benchmarks | Phase 12 optimization | Accept 1.5x slowdown | Medium |
| R-004 | Test count decrease | Low | High | CI gate | No test deletion without replacement | Restore deleted tests | High |
| R-005 | Backward compatibility break | Medium | High | Integration tests | Adapter patterns, feature flags | Hotfix patch release | High |
| R-006 | Observation store memory pressure | Medium | Medium | Memory profiling | In-memory only, no persistence | Limit observation count | Medium |
| R-007 | CI pipeline failure | Low | High | CI monitoring | Incremental merges, branch protection | Revert problematic commit | High |
| R-008 | Scientific validation failure | Medium | Critical | DSVP validation | Statistical equivalence testing | Adjust detection thresholds | Critical |
| R-009 | Benchmark v2.0 incompatibility | Medium | High | Benchmark tests | Independent versioning | Maintain v1.0 benchmarks alongside | Medium |
| R-010 | Cross-platform ID inconsistency | Low | High | Reproducibility tests | SHA-256 is platform-independent | Use UUID fallback | Medium |

---

# 27. Rollback Strategy

## 27.1 Phase-Level Rollback

Each phase has a defined rollback strategy (see Phase specifications above). Rollback is executed by:

1. Reverting the phase's feature branch
2. Re-running all CI jobs
3. Verifying test count preserved
4. Documenting rollback reason

## 27.2 Full Migration Rollback

If the entire v1.5 migration needs to be rolled back:

1. Revert all v1.5 feature branches
2. Restore v1.0.1 as the release version
3. Remove observation packages and modules
4. Revert contracts, schemas, and CLI changes
5. Verify all 730 tests pass
6. Re-tag v1.0.1 as the latest release

## 27.3 Rollback Conditions

- CI fails for > 2 consecutive merges
- Test count decreases
- Scientific validation fails
- Critical security vulnerability introduced
- Performance regression > 2x

---

# 28. Release Readiness Checklist

## 28.1 Architecture Freeze

- [ ] All 6 architecture documents approved
- [ ] IMS specification approved
- [ ] No pending architecture changes

## 28.2 Implementation Freeze

- [ ] All 15 phases merged
- [ ] No pending feature branches
- [ ] All TODOs resolved or documented

## 28.3 Scientific Freeze

- [ ] DSVP 28 acceptance criteria evaluated
- [ ] Statistical equivalence verified
- [ ] Reproducibility verified (100-run test)

## 28.4 Documentation Freeze

- [ ] README updated
- [ ] Architecture docs cross-referenced
- [ ] CLI help text accurate
- [ ] API docs current

## 28.5 Validation Freeze

- [ ] All 730+ tests pass
- [ ] CI all-green (9/9 jobs)
- [ ] No security vulnerabilities
- [ ] Performance targets met

## 28.6 Release Candidate

- [ ] v1.5-rc1 tagged
- [ ] Release candidate tested on multiple platforms
- [ ] Release notes drafted

## 28.7 Release Verification

- [ ] v1.5.0 tag created
- [ ] Release notes published
- [ ] CHANGELOG.md updated
- [ ] All CI jobs green on release commit

## 28.8 Post-Release Monitoring

- [ ] Monitor CI for 48 hours post-release
- [ ] Monitor issue tracker for regression reports
- [ ] Ready to publish hotfix if needed

---

# 29. Success Metrics

| Metric | Target | Measurement |
|---|---|---|
| Test count | ≥ 730 (never decreases) | pytest count |
| CI pass rate | 100% | GitHub Actions |
| Code coverage | ≥ 85% line | coverage report |
| D-01 precision | ≥ 0.80 | Benchmark evaluation |
| D-01 recall | ≥ 0.75 | Benchmark evaluation |
| D-02 precision | ≥ 0.75 | Benchmark evaluation |
| D-02 recall | ≥ 0.70 | Benchmark evaluation |
| D-03 precision | ≥ 0.85 | Benchmark evaluation |
| D-03 recall | ≥ 0.80 | Benchmark evaluation |
| Observation ID determinism | 100% | 100-run reproducibility test |
| CLI backward compatibility | 100% | Integration tests |
| Documentation currency | 100% | Manual review |

---

# 30. Architecture Compliance Checklist

- [ ] Every implementation phase traces to an architecture document
- [ ] Every new interface has a Protocol definition
- [ ] Every new dataclass has validation constraints
- [ ] Every detector preserves mathematical formulas
- [ ] Every adapter produces identical output to legacy interface
- [ ] Every benchmark category per BES is supported
- [ ] Every CLI flag is backward compatible
- [ ] Every configuration field is optional with defaults
- [ ] Every error has an error code and human-readable message
- [ ] Every test verifies both positive and negative cases

---

# 31. Future Transition to v2.0

## 31.1 v2.0 Preview

The v1.5 Observation Engine architecture is the foundation for MIIE v2.0, which will introduce:

- **Terminal Experience:** Interactive TUI for real-time observation analysis
- **Observation Persistence:** SQLite/PostgreSQL backend for observation storage
- **Observation Streaming:** Real-time observation ingestion from Git webhooks
- **Observation API:** REST API for observation CRUD operations
- **Observation Visualization:** Charts and dashboards for observation trends
- **Multi-repository Analysis:** Cross-repository observation correlation
- **Observation Alerting:** Threshold-based alerts on observation patterns

## 31.2 Migration Path v1.5 → v2.0

- ObservationStore interface designed for future persistence backend
- AdapterLayer pattern preserved for v2.0 observation-native detectors
- CLI observation flags extended for TUI integration
- Benchmark v2.0 framework supports v2.0 benchmark categories

---

# 32. Glossary

| Term | Definition |
|---|---|
| Observation | A single data point derived from a specific commit, metric, and source |
| ObservationCollection | A set of observations sharing a common source or context |
| ObservationWindow | Observations within a defined temporal or commit-based window |
| DeterministicObservationID | SHA-256-based unique identifier for an observation |
| ObservationStore | In-memory storage for observations |
| AdapterLayer | Translation layer between observation-level and metric-level data |
| CommitExtractor | Extracts observations from individual commits |
| MetricExtractor | Aggregates observations into MetricDataFrame format |
| WindowBuilder | Segments observations into analysis windows |
| Legacy Interface | v1.0.1 MetricDataFrame-based interface |
| Observation Interface | v1.5 observation-based interface |
| DSVP | Detector Scientific Validation Protocol |
| BES | Benchmark Evolution Specification |
| OEAS | Observation Engine Architecture Specification |
| ODSS | Observation Data Schema Specification |
| DES | Detector Execution Specification |

---

# 33. Appendix

## 33.1 Architecture Document References

| Document | Path | Status |
|---|---|---|
| PRD-OE v1.0 | docs/architecture/observation_engine/PRD_v1.5_Observation_Engine.md | Approved |
| OEAS v1.5 | docs/architecture/observation_engine/OEAS_v1.5_Observation_Engine.md | Approved |
| ODSS v1.0 | docs/architecture/observation_engine/ODSS_v1.0_Observation_Data_Schema_Specification.md | Approved |
| DES v2.0 | docs/architecture/detectors/DES_v2.0_Detector_Execution_Specification.md | Approved |
| DSVP v1.0 | docs/architecture/detectors/DSVP_v1.0_Detector_Scientific_Validation_Protocol.md | Approved |
| BES v1.0 | docs/architecture/benchmarking/BES_v1.0_Benchmark_Evolution_Specification.md | Approved |
| IMS v1.0 | docs/architecture/implementation/IMS_v1.0_Implementation_and_Migration_Specification.md | This document |

## 33.2 Release Baseline

| Artifact | Path | Status |
|---|---|---|
| RELEASE_BASELINE.md | docs/architecture/RELEASE_BASELINE.md | Active |
| V1_5_DEVELOPMENT_ENTRY.md | docs/roadmap/V1_5_DEVELOPMENT_ENTRY.md | Active |
| BASELINE_CHANGE_POLICY.md | docs/governance/BASELINE_CHANGE_POLICY.md | Active |

## 33.3 CI Pipeline Status

| Job | Status | Last Run |
|---|---|---|
| lint | ✅ Green | Run #28286741090 |
| typecheck | ✅ Green | Run #28286741090 |
| unit-tests (3.10) | ✅ Green | Run #28286741090 |
| unit-tests (3.11) | ✅ Green | Run #28286741090 |
| unit-tests (3.12) | ✅ Green | Run #28286741090 |
| integration-tests | ✅ Green | Run #28286741090 |
| regression | ✅ Green | Run #28286741090 |
| security | ✅ Green | Run #28286741090 |
| benchmark | ✅ Green | Run #28286741090 |

## 33.4 Git Tags

| Tag | Commit | Date |
|---|---|---|
| v1.0.0 | aa599b4 | [Release date] |
| v1.0.1 | 4c4d5e6 | [Release date] |
| v1.5.0 | [Pending] | [Pending] |

---

**END OF DOCUMENT**

*IMS v1.0 — Implementation & Migration Specification*
*MIIE v1.0.1 → v1.5 Observation Engine Migration*
*Document ID: IMS-v1.0 | Version: 1.0.0 | Status: Specification*
