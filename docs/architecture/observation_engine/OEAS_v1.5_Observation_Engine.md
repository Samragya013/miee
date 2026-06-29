# MIIE v1.5 — Observation Engine Architecture Specification

**Document:** OEAS-v1.5
**Version:** 1.0.0
**Date:** 2026-06-29
**Classification:** Internal Engineering Architecture Specification
**Status:** Canonical Architecture Standard
**Baseline:** v1.0.1 (tag `4c4d5e6`)

---

## Table of Contents

1. [Document Metadata](#1-document-metadata)
2. [Purpose](#2-purpose)
3. [Scope](#3-scope)
4. [Objectives](#4-objectives)
5. [Non-Objectives](#5-non-objectives)
6. [Architectural Principles](#6-architectural-principles)
7. [Architecture Drivers](#7-architecture-drivers)
8. [Current Architecture Analysis](#8-current-architecture-analysis)
9. [Architectural Constraints](#9-architectural-constraints)
10. [System Context Diagram](#10-system-context-diagram)
11. [Container Diagram](#11-container-diagram)
12. [Component Diagram](#12-component-diagram)
13. [Observation Engine Layered Architecture](#13-observation-engine-layered-architecture)
14. [Observation Engine Internal Components](#14-observation-engine-internal-components)
15. [Observation Lifecycle](#15-observation-lifecycle)
16. [Observation Object](#16-observation-object)
17. [Observation Store Architecture](#17-observation-store-architecture)
18. [Observation Window Architecture](#18-observation-window-architecture)
19. [Detector Integration Architecture](#19-detector-integration-architecture)
20. [Pipeline Evolution](#20-pipeline-evolution)
21. [Interface Contracts](#21-interface-contracts)
22. [Architectural Invariants](#22-architectural-invariants)
23. [Error Handling Architecture](#23-error-handling-architecture)
24. [Performance Architecture](#24-performance-architecture)
25. [Concurrency Architecture](#25-concurrency-architecture)
26. [Security Architecture](#26-security-architecture)
27. [Compatibility Architecture](#27-compatibility-architecture)
28. [Configuration Architecture](#28-configuration-architecture)
29. [Extension Architecture](#29-extension-architecture)
30. [Architectural Decision Records](#30-architectural-decision-records)
31. [Tradeoff Analysis](#31-tradeoff-analysis)
32. [Risk Analysis](#32-risk-analysis)
33. [Implementation Boundaries](#33-implementation-boundaries)
34. [Validation Strategy](#34-validation-strategy)
35. [Acceptance Criteria](#35-acceptance-criteria)
36. [Glossary](#36-glossary)
37. [Appendix](#37-appendix)

---

## 1. Document Metadata

| Field | Value |
|-------|-------|
| Document ID | OEAS-v1.5 |
| Version | 1.0.0 |
| Date | 2026-06-29 |
| Classification | Internal Engineering Architecture Specification |
| Status | Canonical Architecture Standard |
| Baseline | v1.0.1 (tag `4c4d5e6`) |
| Supersedes | None (first version) |
| Dependencies | PRD-v1.5-OE (Observation Engine PRD) |
| Related Documents | RELEASE_BASELINE.md, BASELINE_CHANGE_POLICY.md, V1_5_DEVELOPMENT_ENTRY.md |

### Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-06-29 | Lead Software Architect | Initial specification |

---

## 2. Purpose

This document specifies the canonical architecture of the MIIE v1.5 Observation Engine. It defines:

- The layered architecture of the Observation Engine
- Every component, its responsibilities, interfaces, and failure modes
- The observation lifecycle from creation to archival
- The storage model, indexing strategy, and query interface
- The window construction algorithms
- The detector integration architecture and adapter layer
- The pipeline evolution from v1.0 to v1.5
- Every interface contract with inputs, outputs, and guarantees
- The architectural invariants that implementations must preserve
- The error handling, performance, concurrency, and security architectures
- The extension points for future detectors and observation types

This document is implementation-independent. It specifies *what* must exist and *why*, not *how* to code it. An engineer implementing the Observation Engine must follow this specification precisely. Deviations require an Architecture Decision Record (ADR) and approval from the architecture owner.

---

## 3. Scope

### 3.1 In Scope

| Component | Scope |
|-----------|-------|
| Observation extraction | Per-commit, per-file, per-PR, per-issue metric extraction |
| Observation storage | In-memory store with indexing and query |
| Observation windowing | Temporal, commit-count, hybrid window construction |
| Observation aggregation | Distribution, paired, summary aggregation for detectors |
| Detector integration | Adapter layer for backward-compatible detector execution |
| Pipeline integration | New pipeline stages, orchestration flow |
| Interface contracts | All new interfaces and their guarantees |
| Configuration | New configuration options for observation extraction |
| Error handling | Error types, failure modes, recovery |
| Reproducibility | Deterministic extraction, serialization, verification |

### 3.2 Out of Scope

| Component | Reason | Target |
|-----------|--------|--------|
| Detector algorithm changes | Detectors use new data, not new math | v1.5 unchanged |
| CLI redesign | Frozen per baseline | v2.0 |
| Scoring formula changes | Frozen per baseline | v2.0 |
| Reporting format changes | Frozen per baseline | v2.0 |
| Real-time monitoring | Requires streaming infrastructure | v2.0 |
| Multi-repo analysis | Requires workspace management | v1.6 |
| Web dashboard | Requires API expansion | v2.0 |
| Database-backed storage | Over-engineered for current needs | v2.0 |

---

## 4. Objectives

| ID | Objective | Priority | Verification |
|----|-----------|----------|-------------|
| O-1 | Supply observation-level data to all detectors | HIGH | D-01/D-02/D-03 execute on real distributions |
| O-2 | Preserve determinism for same seed + config | HIGH | Byte-identical JSON output |
| O-3 | Maintain backward compatibility via adapter | HIGH | All 730 tests pass |
| O-4 | Support ≥10 observations per metric per window | HIGH | Integration test on 100+ commit repos |
| O-5 | Enable cross-metric correlation via shared source IDs | MEDIUM | D-02 computes Pearson r on paired data |
| O-6 | Track observation provenance for reproducibility | MEDIUM | Observation IDs deterministic from source |
| O-7 | Support extensibility for future observation types | MEDIUM | Plugin interface for new extractors |
| O-8 | Maintain CLI-first philosophy | HIGH | Same CLI interface, same output format |
| O-9 | Preserve benchmark reproducibility | HIGH | Existing benchmarks produce valid results |
| O-10 | Enable streaming extraction for large repos | LOW | Memory bounded for 100K+ commits |

---

## 5. Non-Objectives

| ID | Non-Objective | Reason |
|----|--------------|--------|
| NO-1 | Redesign detector algorithms | Detectors receive new data, not new math |
| NO-2 | Redesign CLI interface | Frozen per v1.0.1 baseline |
| NO-3 | Redesign scoring formulas | Frozen per v1.0.1 baseline |
| NO-4 | Redesign reporting formats | Frozen per v1.0.1 baseline |
| NO-5 | Implement real-time monitoring | Deferred to v2.0 |
| NO-6 | Implement multi-repo analysis | Deferred to v1.6 |
| NO-7 | Implement cloud deployment | Deferred to v2.0 |
| NO-8 | Implement ML-based detectors | Requires training data infrastructure |
| NO-9 | Implement web dashboard | Requires API expansion |
| NO-10 | Implement REPL/interactive mode | UX overhaul deferred |

---

## 6. Architectural Principles

### 6.1 Observation First

**Statement:** Individual data points are first-class citizens. All analysis begins with observations, not aggregated summaries.

**Rationale:** Detectors are designed to perform statistical tests on distributions. Aggregated values destroy distributional information irrecoverably.

**Implementation:** Extraction produces `Observation` objects. Aggregation occurs only at the adapter boundary, after storage and windowing.

**Tradeoff:** Higher storage overhead (50–500 observations vs. 1 aggregated value per metric per window) in exchange for statistical validity.

### 6.2 Deterministic by Design

**Statement:** Given identical inputs (repository state, configuration, seed), the Observation Engine produces byte-identical output.

**Rationale:** Reproducibility is a scientific requirement. Non-deterministic extraction undermines the validity of integrity assessments.

**Implementation:** Deterministic observation IDs (SHA-256 of source metadata), sorted extraction order, seed-controlled random operations.

**Tradeoff:** Deterministic extraction requires sorted iteration (O(n log n)) instead of hash-set iteration (O(n)), but the performance cost is negligible for typical repository sizes.

### 6.3 Immutable Observations

**Statement:** Once created, an Observation object is never mutated. All state transitions produce new objects.

**Rationale:** Immutability prevents accidental data corruption, enables safe concurrent access, and simplifies reasoning about state.

**Implementation:** Observation dataclass is frozen. Window assignment creates new `ObservationWindow` objects containing references to existing observations.

**Tradeoff:** Higher memory allocation (new objects per transition) in exchange for safety and debuggability.

### 6.4 Minimal Coupling

**Statement:** Components depend only on the interfaces they consume, not on concrete implementations.

**Rationale:** Loose coupling enables independent testing, replacement, and evolution of components.

**Implementation:** All engine interfaces defined as `Protocol` (structural subtyping). Detectors depend on `MetricDataFrame` interface, not on `ObservationStore` directly.

**Tradeoff:** Additional indirection (adapter layer) in exchange for decoupling and backward compatibility.

### 6.5 Backward Compatibility

**Statement:** Existing detectors, CLI commands, config files, and report formats work without modification.

**Rationale:** The v1.0.1 baseline is publicly released. Breaking changes require major version bumps and migration guides.

**Implementation:** Adapter layer translates `ObservationWindow` to `MetricDataFrame`. Existing interface contracts preserved.

**Tradeoff:** Adapter overhead (O(n) translation) in exchange for zero-migration cost.

### 6.6 Single Responsibility

**Statement:** Each component has exactly one reason to change.

**Rationale:** Focused components are easier to test, understand, and maintain.

**Implementation:** Extraction (data acquisition), Storage (persistence and query), Windowing (temporal grouping), Aggregation (format translation) are separate components.

**Tradeoff:** More components (higher architectural complexity) in exchange for focused, testable units.

### 6.7 Repository Independence

**Statement:** The Observation Engine operates on any Git repository without requiring special repository structure or tooling.

**Rationale:** MIIE must analyze diverse repositories without imposing constraints on repository organization.

**Implementation:** Extraction from standard Git commands (`git log`, `git diff`). No dependency on CI systems, hosting platforms, or repository conventions.

**Tradeoff:** Limited to Git-native metrics without external data sources (e.g., CI coverage data requires API integration).

### 6.8 Scientific Reproducibility

**Statement:** Any analysis can be reproduced exactly by re-running with the same seed and configuration.

**Rationale:** Scientific integrity requires reproducibility. Findings must be verifiable by independent parties.

**Implementation:** Deterministic extraction, serialized observation stores, config hashes, dependency hashes.

**Tradeoff:** Larger storage footprint (serialized stores) in exchange for reproducibility.

---

## 7. Architecture Drivers

### 7.1 Functional Drivers

| Driver | Description | Impact |
|--------|-------------|--------|
| FD-1 | Detectors require distributions, not summaries | Core architectural change |
| FD-2 | Cross-metric correlation requires paired observations | Shared source IDs |
| FD-3 | Bootstrap requires empirical distributions | Per-observation extraction |
| FD-4 | Trend detection requires temporal resolution | Per-commit timestamps |
| FD-5 | Existing CLI must continue working | Adapter layer |

### 7.2 Non-Functional Drivers

| Driver | Description | Impact |
|--------|-------------|--------|
| NFD-1 | Deterministic extraction for reproducibility | Seed-controlled operations |
| NFD-2 | Offline-first operation | No external API dependencies |
| NFD-3 | CLI-first philosophy | Same interface, same output |
| NFD-4 | Performance for 100K+ commit repos | Streaming extraction |
| NFD-5 | Memory efficiency | Bounded memory usage |

### 7.3 Scientific Drivers

| Driver | Description | Impact |
|--------|-------------|--------|
| SD-1 | Statistical test power requires n ≥ 10 | Minimum observation count |
| SD-2 | Correlation analysis requires matched pairs | Cross-metric linking |
| SD-3 | Bootstrap requires resampling from distribution | Full observation sets |
| SD-4 | Trend analysis requires temporal ordering | Timestamp-preserving extraction |
| SD-5 | Reproducibility requires deterministic operations | Deterministic IDs and ordering |

### 7.4 Performance Drivers

| Driver | Description | Impact |
|--------|-------------|--------|
| PD-1 | 1000-commit repo extraction < 30 seconds | Efficient git operations |
| PD-2 | 100K-commit repo extraction < 30 minutes | Streaming extraction |
| PD-3 | Memory usage < 500 MB for 1000-commit repo | Bounded observation storage |
| PD-4 | Observation query < 1ms | Indexed store |

### 7.5 Scalability Drivers

| Driver | Description | Impact |
|--------|-------------|--------|
| SD-1 | Support repos with 100K+ commits | Streaming, chunked processing |
| SD-2 | Support repos with 500+ contributors | Metadata handling |
| SD-3 | Support 10+ year repo histories | Temporal windowing |

### 7.6 Maintainability Drivers

| Driver | Description | Impact |
|--------|-------------|--------|
| MD-1 | Components independently testable | Interface-based design |
| MD-2 | Future detectors must integrate without modifying existing code | Extension points |
| MD-3 | Configuration must be extensible | Schema versioning |

---

## 8. Current Architecture Analysis

### 8.1 v1.0 Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Layer                                │
│  miie analyze <repo> --metrics M-02,M-06 --window-strategy time │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Pipeline Stages                              │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Ingestion│→ │Validation│→ │Extraction│→ │Segmentation│      │
│  │          │  │          │  │          │  │           │       │
│  │ Git clone│  │ No-op    │  │ Git log  │  │ Window    │       │
│  │ + context│  │          │  │ + parse  │  │ boundaries│       │
│  └──────────┘  └──────────┘  └────┬─────┘  └─────┬─────┘       │
│                                   │               │             │
│                                   ▼               ▼             │
│                             ┌──────────┐  ┌──────────┐          │
│                             │MetricData│← │Re-extract│          │
│                             │Frame     │  │per-window│          │
│                             └────┬─────┘  └──────────┘          │
│                                  │                              │
│                                  ▼                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Reporting │← │Explanation│← │Evidence  │← │ Scoring  │       │
│  │          │  │          │  │          │  │          │       │
│  │ 4 formats│  │Narratives│  │Package   │  │ IS + CS  │       │
│  └──────────┘  └──────────┘  └──────────┘  └────┬─────┘       │
│                                                  │             │
│                                                  ▼             │
│                                            ┌──────────┐        │
│                                            │Detection │        │
│                                            │          │        │
│                                            │ D-01/D-02│        │
│                                            │ /D-03    │        │
│                                            └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Data Model: MetricDataFrame

```
MetricDataFrame
├── repo_id: str
├── run_id: str
├── timestamp: datetime
└── metrics: Dict[str, Dict[str, List[Optional[float]]]]
        │               │           │
        │               │           └── Always single-element list
        │               │               e.g. [143.0]
        │               │
        │               └── Window ID
        │                   e.g. "w00", "w01"
        │
        └── Metric ID
            e.g. "M-02", "M-06"
```

### 8.3 The Architectural Problem

**Root cause:** The extraction engine produces **aggregated summary statistics** — one number per metric per window — and stores them as single-element lists.

**Example:**
```
MetricDataFrame.metrics = {
    "M-02": {                    # Commit Frequency
        "w00": [143.0],          # ← ONE value: total commits in window
        "w01": [166.0],          # ← ONE value: total commits in window
    },
    "M-06": {                    # Code Churn
        "w00": [5420.0],         # ← ONE value: total lines changed
        "w01": [3890.0],         # ← ONE value: total lines changed
    }
}
```

**Detector impact:**

| Detector | Input Required | Input Received | Status |
|----------|---------------|----------------|--------|
| D-01 (KS test) | Two distributions (n ≥ 10 each) | Two single values (n = 1) | ALWAYS SKIPPED |
| D-02 (Pearson) | Paired observations (n ≥ 10) | Two single values (n = 1) | UNDEFINED |
| D-03 (Bootstrap) | Empirical distribution | Single value (n = 1) | DEGENERATE |

### 8.4 Pipeline Execution Trace

```
CLI: miie analyze /path/to/repo --window-strategy time --window-size 7

1. Ingestion:    RepositoryIngestionEngine.ingest(repo_path)
                 → RepositoryContext (repo_id, local_path, total_commits=500)

2. Extraction:   MetricExtractionEngine.extract(context, ["M-02","M-06"])
                 → MetricDataFrame (M-02: {w00: [143]}, M-06: {w00: [5420]})

3. Segmentation: WindowSegmentationEngine.segment(metric_df, "time", 7)
                 → [WindowDefinition(w00, 2025-06-22, 2025-06-29)]

4. Re-extract:   MetricExtractionEngine.extract(context, windows=[w00])
                 → MetricDataFrame (same structure, single values)

5. Detection:    DetectorDispatcherEngine.invoke(metric_df, windows)
                 → D-01: SKIPPED (n=1 < 10)
                 → D-02: SKIPPED (n=1, need ≥2 metrics with n≥10)
                 → D-03: DEGENERATE (single-point CDF)

6. Scoring:      ScoringEngine.compute_integrity_score(detector_results)
                 → ScorePackage (integrity=1.0, confidence=0.0)

7. Evidence:     EvidenceEngine.generate(...)
                 → EvidencePackage (all inputs bundled)

8. Explanation:  ExplanationEngine.generate(evidence, scores)
                 → ExplanationReport (narratives, recommendations)

9. Reporting:    ReportGenerator.generate(analysis_result)
                 → ReportOutput (json, md, csv, txt)
```

### 8.5 Why This Matters

The system reports integrity scores and confidence bands that appear statistically rigorous. But the underlying detectors either:

1. **Skip entirely** (D-01: sample size < 10)
2. **Produce undefined results** (D-02: Pearson on n=1)
3. **Produce degenerate results** (D-03: CDF of a single point)

The scores are derived from detector outputs that are either absent or statistically meaningless.

---

## 9. Architectural Constraints

### 9.1 Hard Constraints

| ID | Constraint | Source | Rationale |
|----|-----------|--------|-----------|
| HC-1 | Existing CLI interface unchanged | v1.0.1 baseline | Public release, user scripts |
| HC-2 | Existing config format unchanged | v1.0.1 baseline | Existing config files |
| HC-3 | Existing report format unchanged | v1.0.1 baseline | Downstream consumers |
| HC-4 | Existing error hierarchy preserved | v1.0.1 baseline | Error handling code |
| HC-5 | All 730 tests must pass | v1.0.1 baseline | Regression prevention |
| HC-6 | Deterministic extraction | Scientific requirement | Reproducibility |
| HC-7 | Offline-first operation | Design philosophy | No external dependencies |
| HC-8 | Python 3.10+ compatibility | pyproject.toml | Runtime requirement |

### 9.2 Soft Constraints

| ID | Constraint | Source | Rationale |
|----|-----------|--------|-----------|
| SC-1 | No new external dependencies | Minimize footprint | Dependency management |
| SC-2 | No database backend | Simplicity | Offline-first |
| SC-3 | No async/await in core pipeline | Determinism | Reproducibility |
| SC-4 | Memory usage < 8GB for 100K commits | Performance | Hardware limits |

---

## 10. System Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        MIIE System                              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  Observation Engine                     │    │
│  │                                                         │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │    │
│  │  │Extraction│→ │ Storage  │→ │ Windowing│             │    │
│  │  └──────────┘  └──────────┘  └──────────┘             │    │
│  │       ↑                            │                    │    │
│  │       │                            ▼                    │    │
│  │  ┌──────────┐              ┌──────────┐                │    │
│  │  │ Repository│              │ Adapter  │                │    │
│  │  │   Data    │              │  Layer   │                │    │
│  │  └──────────┘              └────┬─────┘                │    │
│  │                                 │                       │    │
│  └─────────────────────────────────┼───────────────────────┘    │
│                                    │                            │
│                                    ▼                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Detection │→ │ Scoring  │→ │ Evidence │→ │Reporting │       │
│  │ D-01/D-02│  │ IS + CS  │  │ Package  │  │ 4 formats│       │
│  │ /D-03    │  │          │  │          │  │          │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         ↑                                    │
         │                                    ▼
┌────────┴─────────┐                ┌─────────────────────┐
│   Git Repository  │                │    CLI / User       │
│                   │                │                     │
│  - Commits        │                │  miie analyze ...   │
│  - Files          │                │  --window-strategy  │
│  - PRs (optional) │                │  --metrics M-02,M-06│
│  - Issues (opt.)  │                │                     │
└──────────────────┘                └─────────────────────┘
```

---

## 11. Container Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Container Diagram                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  CLI Container                          │    │
│  │                                                         │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │    │
│  │  │  Click    │  │  Config  │  │ Progress │             │    │
│  │  │  CLI     │  │  Loader  │  │ Reporter │             │    │
│  │  └──────────┘  └──────────┘  └──────────┘             │    │
│  └───────────────────────────┬─────────────────────────────┘    │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Observation Engine Container               │    │
│  │                                                         │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │    │
│  │  │Extractor │  │  Store   │  │ Window   │             │    │
│  │  │  Pool    │  │          │  │ Builder  │             │    │
│  │  └──────────┘  └──────────┘  └──────────┘             │    │
│  │       │              │              │                    │    │
│  │       ▼              ▼              ▼                    │    │
│  │  ┌──────────────────────────────────────┐              │    │
│  │  │         Adapter Layer                │              │    │
│  │  │    (ObservationWindow → MetricDF)    │              │    │
│  │  └──────────────────────────────────────┘              │    │
│  └───────────────────────────┬─────────────────────────────┘    │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │               Detection Container                       │    │
│  │                                                         │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │    │
│  │  │  D-01    │  │  D-02    │  │  D-03    │             │    │
│  │  │  D-04    │  │  D-05    │  │  D-06    │             │    │
│  │  │  D-07    │  │          │  │          │             │    │
│  │  └──────────┘  └──────────┘  └──────────┘             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 12. Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Component Diagram                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                Observation Engine                       │    │
│  │                                                         │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │            Extraction Layer                     │    │    │
│  │  │                                                 │    │    │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐       │    │    │
│  │  │  │  Commit   │ │ Coverage │ │  Review  │       │    │    │
│  │  │  │Extractor │ │Extractor │ │Extractor │       │    │    │
│  │  │  └──────────┘ └──────────┘ └──────────┘       │    │    │
│  │  │  ┌──────────┐ ┌──────────┐                     │    │    │
│  │  │  │  Issue    │ │Complexity│                     │    │    │
│  │  │  │Extractor │ │Extractor │                     │    │    │
│  │  │  └──────────┘ └──────────┘                     │    │    │
│  │  └─────────────────────┬───────────────────────────┘    │    │
│  │                        │                                │    │
│  │                        ▼                                │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │            Storage Layer                        │    │    │
│  │  │                                                 │    │    │
│  │  │  ┌──────────────────────────────────────────┐   │    │    │
│  │  │  │           ObservationStore               │   │    │    │
│  │  │  │                                          │   │    │    │
│  │  │  │  Index: metric_id → [observation_ids]    │   │    │    │
│  │  │  │  Index: timestamp  → [observation_ids]   │   │    │    │
│  │  │  │  Index: source_id  → [observation_ids]   │   │    │    │
│  │  │  └──────────────────────────────────────────┘   │    │    │
│  │  └─────────────────────┬───────────────────────────┘    │    │
│  │                        │                                │    │
│  │                        ▼                                │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │            Window Layer                         │    │    │
│  │  │                                                 │    │    │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐       │    │    │
│  │  │  │ Temporal  │ │  Commit  │ │  Hybrid  │       │    │    │
│  │  │  │ Builder   │ │ Builder  │ │ Builder  │       │    │    │
│  │  │  └──────────┘ └──────────┘ └──────────┘       │    │    │
│  │  └─────────────────────┬───────────────────────────┘    │    │
│  │                        │                                │    │
│  │                        ▼                                │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │            Adapter Layer                        │    │    │
│  │  │                                                 │    │    │
│  │  │  ┌──────────────────────────────────────────┐   │    │    │
│  │  │  │         DetectorAdapter                  │   │    │    │
│  │  │  │                                          │   │    │    │
│  │  │  │  ObservationWindow → MetricDataFrame     │   │    │    │
│  │  │  │  ObservationStore  → MetricDataFrame     │   │    │    │
│  │  │  └──────────────────────────────────────────┘   │    │    │
│  │  └─────────────────────────────────────────────────┘    │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 13. Observation Engine Layered Architecture

### 13.1 Layer Definitions

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 7: Detector Layer                                         │
│   Receives aggregated distributions from adapter                │
│   Produces DetectorResults                                      │
├─────────────────────────────────────────────────────────────────┤
│ Layer 6: Scoring Layer                                          │
│   Computes IntegrityScore and ConfidenceScore                   │
│   Produces ScorePackage                                         │
├─────────────────────────────────────────────────────────────────┤
│ Layer 5: Adapter Layer                                          │
│   Translates ObservationWindow to MetricDataFrame               │
│   Provides backward-compatible detector interface               │
├─────────────────────────────────────────────────────────────────┤
│ Layer 4: Window Layer                                           │
│   Groups observations into temporal/commit windows              │
│   Produces List[ObservationWindow]                              │
├─────────────────────────────────────────────────────────────────┤
│ Layer 3: Storage Layer                                          │
│   Stores, indexes, queries observations                         │
│   Provides ObservationStore interface                            │
├─────────────────────────────────────────────────────────────────┤
│ Layer 2: Observation Layer                                      │
│   Defines Observation, ObservationWindow, ObservationStore      │
│   Establishes observation contracts and invariants              │
├─────────────────────────────────────────────────────────────────┤
│ Layer 1: Extraction Layer                                       │
│   Extracts observations from repository data sources            │
│   One extractor per metric type                                 │
├─────────────────────────────────────────────────────────────────┤
│ Layer 0: Repository Layer                                       │
│   Git operations, file system access, API calls                 │
│   Provides raw data to extraction layer                         │
└─────────────────────────────────────────────────────────────────┘
```

### 13.2 Layer Responsibilities

| Layer | Responsibility | Input | Output | Dependencies |
|-------|---------------|-------|--------|-------------|
| L0: Repository | Raw data access | Repository path | Git log, file contents | None |
| L1: Extraction | Observation creation | RepositoryContext | List[Observation] | L0 |
| L2: Observation | Data model definitions | None | Type contracts | None |
| L3: Storage | Persistence and query | List[Observation] | ObservationStore | L2 |
| L4: Windowing | Temporal grouping | ObservationStore | List[ObservationWindow] | L2, L3 |
| L5: Adapter | Format translation | ObservationWindow | MetricDataFrame | L2, L4 |
| L6: Scoring | Score computation | DetectorResults | ScorePackage | L2 |
| L7: Detection | Anomaly detection | MetricDataFrame | DetectorResults | L5 |

### 13.3 Layer Interaction Rules

| Rule | Description |
|------|-------------|
| L(n) depends only on L(n-1) and L(n-2) | No upward dependencies |
| L0 never imported by L3+ | Repository access only through extraction |
| L5 is the only bidirectional adapter | Translates between old and new models |
| L7 receives only MetricDataFrame | Detectors unaware of observation layer |
| L2 has zero runtime dependencies | Pure data model definitions |

---

## 14. Observation Engine Internal Components

### 14.1 CommitExtractor

**Purpose:** Extract per-commit observations for M-02 (commit frequency) and M-06 (code churn).

**Responsibilities:**
- Execute `git log` to retrieve commit list with metadata
- Execute `git diff --numstat` per commit for churn data
- Create Observation objects with deterministic IDs
- Preserve temporal ordering

**Interface:**
```
Input:  RepositoryContext + extraction config
Output: List[Observation]  (metric_id ∈ {M-02, M-06})
```

**Dependencies:** Repository layer (git commands)

**Failure Modes:**
| Failure | Impact | Recovery |
|---------|--------|----------|
| git log fails | ExtractionError raised | Abort analysis |
| parse error on commit | Skip commit, log warning | Continue with reduced N |
| empty repository | Empty observation list | Pipeline continues |

**Extension Points:**
- Custom date filters (since/until)
- Bot exclusion logic
- Merge commit handling

**Complexity:** O(n) where n = number of commits

### 14.2 CoverageExtractor

**Purpose:** Extract per-commit coverage observations for M-01.

**Responsibilities:**
- Parse coverage artifacts (coverage.xml, lcov.info, .coverage)
- Estimate per-commit coverage delta from file changes
- Create Observation objects

**Interface:**
```
Input:  RepositoryContext + coverage artifact path
Output: List[Observation]  (metric_id = M-01)
```

**Dependencies:** Repository layer (file parsing)

**Failure Modes:**
| Failure | Impact | Recovery |
|---------|--------|----------|
| No coverage artifact | Empty observation list | M-01 unavailable |
| Parse error | Skip file, log warning | Reduced sample size |

**Extension Points:**
- CI API integration for precise coverage
- Multi-tool support (coverage.py, lcov, cobertura)

**Complexity:** O(f) where f = number of source files

### 14.3 ReviewExtractor

**Purpose:** Extract per-PR observations for M-03 (review participation) and M-04 (review latency).

**Responsibilities:**
- Parse PR export JSON or GitHub API data
- Compute per-PR metric values
- Create Observation objects with PR metadata

**Interface:**
```
Input:  RepositoryContext + PR export path (or GitHub API token)
Output: List[Observation]  (metric_id ∈ {M-03, M-04})
```

**Dependencies:** Repository layer (API access or file parsing)

**Failure Modes:**
| Failure | Impact | Recovery |
|---------|--------|----------|
| No PR data available | Empty observation list | M-03/M-04 unavailable |
| API rate limit | Partial extraction | Retry with backoff |
| Parse error | Skip PR, log warning | Reduced sample size |

**Extension Points:**
- GitLab PR support
- Bitbucket PR support
- Custom review event types

**Complexity:** O(p) where p = number of PRs

### 14.4 IssueExtractor

**Purpose:** Extract per-issue observations for M-05 (issue resolution time).

**Responsibilities:**
- Parse issue export JSON or GitHub API data
- Compute per-issue resolution time
- Create Observation objects

**Interface:**
```
Input:  RepositoryContext + issue export path (or GitHub API token)
Output: List[Observation]  (metric_id = M-05)
```

**Dependencies:** Repository layer (API access or file parsing)

**Failure Modes:**
| Failure | Impact | Recovery |
|---------|--------|----------|
| No issue data available | Empty observation list | M-05 unavailable |
| API rate limit | Partial extraction | Retry with backoff |

**Extension Points:**
- GitLab issues, Jira integration
- Custom issue event types

**Complexity:** O(i) where i = number of issues

### 14.5 ComplexityExtractor

**Purpose:** Extract per-file complexity observations for M-07.

**Responsibilities:**
- Run lizard or radon on source files
- Compute per-file mean complexity
- Create Observation objects

**Interface:**
```
Input:  RepositoryContext + source files
Output: List[Observation]  (metric_id = M-07)
```

**Dependencies:** Repository layer (file access), external tools (lizard/radon)

**Failure Modes:**
| Failure | Impact | Recovery |
|---------|--------|----------|
| lizard/radon not installed | Empty observation list | M-07 unavailable |
| Unsupported language | Skip file, log warning | Reduced sample size |

**Extension Points:**
- Additional complexity tools
- Language-specific analyzers

**Complexity:** O(f × l) where f = files, l = avg functions per file

### 14.6 ObservationStore

**Purpose:** Store, index, and query observations.

**Responsibilities:**
- Store observations in memory with indexing
- Provide query interface by metric, time range, source
- Serialize to/from JSON for reproducibility
- Enforce observation immutability

**Interface:**
```
Input:  List[Observation]  (via add/batch_add)
Output: Query results      (via query/get/count)
```

**Dependencies:** Observation data model

**Failure Modes:**
| Failure | Impact | Recovery |
|---------|--------|----------|
| Memory exhaustion | ExtractionError | Reduce batch size |
| Duplicate observation ID | Raise ValueError | Abort |
| Serialization error | Log warning, continue in-memory | No persistent record |

**Extension Points:**
- Disk-backed storage
- Database backend
- Distributed storage

**Complexity:** Add O(1), Query O(log n), Serialize O(n)

### 14.7 WindowBuilder

**Purpose:** Group observations into analysis windows.

**Responsibilities:**
- Apply windowing strategy (temporal, commit, hybrid)
- Assign observations to windows
- Enforce minimum observation counts
- Produce ObservationWindow objects

**Interface:**
```
Input:  ObservationStore + WindowConfig
Output: List[ObservationWindow]
```

**Dependencies:** ObservationStore, Observation data model

**Failure Modes:**
| Failure | Impact | Recovery |
|---------|--------|----------|
| Insufficient observations | Warning logged | Continue with reduced windows |
| Empty windows | Skip empty windows | Log warning |
| Non-overlapping constraint violated | Raise ValueError | Abort |

**Extension Points:**
- Custom windowing strategies
- Overlapping windows
- Adaptive window sizes

**Complexity:** O(n log n) where n = observation count

### 14.8 DetectorAdapter

**Purpose:** Translate between Observation Engine and legacy detector interfaces.

**Responsibilities:**
- Convert ObservationWindow to MetricDataFrame
- Pair observations across metrics for correlation
- Provide summary statistics for confidence factors
- Preserve backward compatibility

**Interface:**
```
Input:  List[ObservationWindow] + ObservationStore
Output: MetricDataFrame  (backward-compatible format)
```

**Dependencies:** ObservationWindow, ObservationStore, MetricDataFrame schema

**Failure Modes:**
| Failure | Impact | Recovery |
|---------|--------|----------|
| No observations for metric | Empty list in MetricDataFrame | Detector skips metric |
| Pairing fails | Empty paired lists | D-02 skips pair |

**Extension Points:**
- New detector interfaces
- Streaming translation
- Chunked processing

**Complexity:** O(n) where n = observation count

---

## 15. Observation Lifecycle

### 15.1 Lifecycle States

```
                    ┌──────────┐
                    │ Created  │
                    └────┬─────┘
                         │ validation passes
                         ▼
                    ┌──────────┐
                    │ Extracted│
                    └────┬─────┘
                         │ store.add()
                         ▼
                    ┌──────────┐
                    │  Stored  │
                    └────┬─────┘
                         │ window_builder.build()
                         ▼
                    ┌──────────┐
                    │ Windowed │
                    └────┬─────┘
                         │ adapter.to_metric_dataframe()
                         ▼
                    ┌──────────┐
                    │ Consumed │
                    └────┬─────┘
                         │ analysis completes
                         ▼
                    ┌──────────┐
                    │ Archived │
                    └──────────┘
```

### 15.2 State Definitions

| State | Description | Data |
|-------|-------------|------|
| Created | Object instantiated, not yet validated | observation_id, timestamp, metric_id, value |
| Extracted | Value computed, validation passed | All fields populated |
| Stored | Persisted in ObservationStore | Indexed by metric, time, source |
| Windowed | Assigned to one or more windows | Window membership recorded |
| Consumed | Read by detector via adapter | Values accessed for statistical tests |
| Archived | Serialized to JSON for reproducibility | Written to disk |

### 15.3 State Transitions

| Transition | Trigger | Precondition | Postcondition |
|-----------|---------|-------------|--------------|
| Created → Extracted | Extraction completes | value is not None, not NaN, not Inf | observation_id deterministic |
| Extracted → Stored | store.add() called | observation_id not in store | Indexed by metric, time, source |
| Stored → Windowed | WindowBuilder.build() | observation within window bounds | Assigned to window |
| Windowed → Consumed | Adapter reads | observation count ≥ 1 | Values accessible |
| Consumed → Archived | Analysis completes | Serializable to JSON | JSON written |

### 15.4 Failure Transitions

```
                    ┌──────────┐
                    │ Created  │
                    └────┬─────┘
                         │ validation fails
                         ▼
                    ┌──────────┐
                    │  Failed  │ → logged, skipped
                    └──────────┘
```

| Failure | State | Action |
|---------|-------|--------|
| Value is NaN/Inf | Created | Skip, log warning |
| Duplicate ID | Created | Skip, log warning |
| Store full | Extracted | Raise ExtractionError |
| Window bounds violated | Stored | Skip, log warning |
| Serialization fails | Consumed | Log warning, continue |

---

## 16. Observation Object

### 16.1 Architecture

The Observation object is the atomic unit of data in the Observation Engine. It represents a single data point extracted from a repository source.

```
┌─────────────────────────────────────────┐
│              Observation                │
├─────────────────────────────────────────┤
│ observation_id: str     (deterministic) │
│ timestamp: datetime     (source time)   │
│ metric_id: str          (M-01..M-07)    │
│ value: float            (numeric)       │
│ source_type: str        (commit/pr/...) │
│ source_id: str          (SHA/number)    │
│ repo_id: str            (repository)    │
│ metadata: Dict[str,Any] (source detail) │
└─────────────────────────────────────────┘
```

### 16.2 Invariants

| Invariant | Description |
|-----------|-------------|
| I-1 | observation_id is deterministic from (source_type, source_id, metric_id) |
| I-2 | value is finite (not NaN, not Inf) |
| I-3 | timestamp is a valid datetime |
| I-4 | metric_id matches pattern M-[0-9]{2} |
| I-5 | source_type is in ALLOWED_SOURCE_TYPES |
| I-6 | Object is immutable after creation |

### 16.3 Deterministic ID Computation

```
observation_id = SHA-256(source_type + ":" + source_id + ":" + metric_id)[:16]
```

This ensures:
- Same source produces same ID (reproducibility)
- No randomness (determinism)
- 128-bit collision resistance

### 16.4 Metadata Schema

| source_type | metadata fields |
|-------------|----------------|
| commit | author, message, files_changed, insertions, deletions, parents |
| coverage | file_path, line_coverage, branch_coverage, tool |
| pr | number, author, reviewers, created_at, merged_at |
| issue | number, author, created_at, closed_at, labels |
| complexity | file_path, function_name, language, cc_score, lines |

### 16.5 Reference to ODSS

The complete observation data schema is defined in the Observation Data Schema Specification (ODSS). This section defines the architectural properties only.

---

## 17. Observation Store Architecture

### 17.1 Memory Model

```
ObservationStore
├── _observations: Dict[str, Observation]
│   └── Primary index: observation_id → Observation
│
├── _by_metric: Dict[str, List[str]]
│   └── Secondary index: metric_id → [observation_ids]
│
├── _by_time: List[str]
│   └── Temporal index: observation_ids sorted by timestamp
│
├── _by_source: Dict[str, List[str]]
│   └── Source index: source_type → [observation_ids]
│
└── _by_source_id: Dict[str, List[str]]
    └── Cross-metric index: source_id → [observation_ids]
```

### 17.2 Indexing Strategy

| Index | Key | Value | Purpose |
|-------|-----|-------|---------|
| Primary | observation_id | Observation | Direct lookup |
| Metric | metric_id | List[observation_id] | Filter by metric |
| Temporal | (sorted) | List[observation_id] | Range queries |
| Source Type | source_type | List[observation_id] | Filter by source |
| Cross-Metric | source_id | List[observation_id] | Paired correlation |

### 17.3 Query Interface

```
query(metric_id?, source_type?, since?, until?) → List[Observation]
get(observation_id) → Optional[Observation]
count(metric_id?) → int
get_values(metric_id, window?) → List[float]
get_paired(metric_i, metric_j, join_on) → Tuple[List[float], List[float]]
```

### 17.4 Query Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| add | O(1) amortized | Dict insert + index update |
| get | O(1) | Direct lookup |
| query (metric) | O(log n + k) | Index lookup + filter |
| query (time range) | O(log n + k) | Binary search + filter |
| count | O(1) | Cached per metric |
| get_values | O(k) | Filter + extract |
| get_paired | O(n log n) | Sort + join |

### 17.5 Serialization

The store serializes to JSON for reproducibility:

```json
{
  "store_version": "1.0.0",
  "repo_id": "abc123",
  "observation_count": 1234,
  "metric_counts": {"M-02": 500, "M-06": 500},
  "observations": [...]
}
```

### 17.6 Caching

| Cache | Scope | Invalidation |
|-------|-------|-------------|
| count_cache | Per-metric count | On add() |
| values_cache | Per-metric values | On add() |
| query_cache | Per-query result | TTL-based (no write invalidation needed for immutable observations) |

---

## 18. Observation Window Architecture

### 18.1 Window Model

```
ObservationWindow
├── window_id: str              ("w00", "w01", ...)
├── start_date: datetime.date
├── end_date: datetime.date
├── observations: List[Observation]
├── metric_counts: Dict[str, int]
└── source_counts: Dict[str, int]
```

### 18.2 Temporal Windowing

**Algorithm:**
```
Input:  store (ObservationStore), window_size_days (int)
Output: List[ObservationWindow]

1. min_ts ← min(obs.timestamp for obs in store)
2. max_ts ← max(obs.timestamp for obs in store)
3. windows ← []
4. window_start ← min_ts.date()
5. window_id ← 0
6. WHILE window_start < max_ts.date():
7.   window_end ← window_start + timedelta(days=window_size_days)
8.   observations ← [obs for obs in store
                      WHERE obs.timestamp.date() >= window_start
                      AND obs.timestamp.date() < window_end]
9.   IF |observations| > 0:
10.    windows.append(ObservationWindow(
             window_id=f"w{window_id:02d}",
             start_date=window_start,
             end_date=window_end,
             observations=observations))
11.    window_id ← window_id + 1
12.  window_start ← window_end
13. RETURN windows
```

**Properties:**
- Windows are mutually exclusive (no overlap)
- Windows are contiguous (no gaps)
- Empty windows are skipped
- Window IDs are sequential starting from w00

### 18.3 Commit-Count Windowing

**Algorithm:**
```
Input:  store (ObservationStore), commits_per_window (int)
Output: List[ObservationWindow]

1. commit_obs ← store.query(metric_id="M-02")
2. commit_obs ← sorted(commit_obs, key=lambda o: o.timestamp)
3. window_boundaries ← [commit_obs[i].timestamp
                         for i in range(0, len(commit_obs), commits_per_window)]
4. windows ← []
5. FOR i IN range(len(window_boundaries) - 1):
6.   t_start ← window_boundaries[i]
7.   t_end ← window_boundaries[i + 1]
8.   observations ← [obs for obs in store
                      WHERE obs.timestamp >= t_start AND obs.timestamp < t_end]
9.   windows.append(ObservationWindow(...))
10. RETURN windows
```

### 18.4 Hybrid Windowing

**Algorithm:**
```
Input:  store, window_size_days, min_commits_per_window
Output: List[ObservationWindow]

1. windows ← build_temporal_windows(store, window_size_days)
2. merged ← []
3. current ← windows[0]
4. FOR window IN windows[1:]:
5.   IF current.metric_counts.get("M-02", 0) < min_commits_per_window:
6.     current ← merge(current, window)
7.   ELSE:
8.     merged.append(current)
9.     current ← window
10. merged.append(current)
11. RETURN renumber(merged)
```

### 18.5 Window Constraints

| Constraint | Value | Rationale |
|-----------|-------|-----------|
| Minimum observations per window | 10 | Statistical test power |
| Minimum windows | 2 | Cross-window comparison |
| Window overlap | None | Mutually exclusive |
| Empty windows between non-empty | 0 | No gaps |
| Window ID format | w[0-9]+ | Regex-validated |

---

## 19. Detector Integration Architecture

### 19.1 Adapter Layer Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Adapter Layer                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              DetectorAdapter                        │    │
│  │                                                     │    │
│  │  to_metric_dataframe(windows, store) → MetricDF    │    │
│  │                                                     │    │
│  │  ┌──────────────────────────────────────────────┐   │    │
│  │  │  Translation Logic                           │   │    │
│  │  │                                              │   │    │
│  │  │  FOR each window:                            │   │    │
│  │  │    FOR each metric:                          │   │    │
│  │  │      values ← [obs.value                     │   │    │
│  │  │                 FOR obs IN window.observations│   │    │
│  │  │                 WHERE obs.metric_id == metric]│   │    │
│  │  │      metric_df.metrics[metric][window_id]    │   │    │
│  │  │             ← values                         │   │    │
│  │  └──────────────────────────────────────────────┘   │    │
│  │                                                     │    │
│  │  to_paired_observations(window, mi, mj) → Pair     │    │
│  │                                                     │    │
│  │  ┌──────────────────────────────────────────────┐   │    │
│  │  │  Cross-Metric Pairing                        │   │    │
│  │  │                                              │   │    │
│  │  │  obs_i ← {obs FOR obs IN window WHERE m=m_i}│   │    │
│  │  │  obs_j ← {obs FOR obs IN window WHERE m=m_j}│   │    │
│  │  │  paired ← JOIN obs_i, obs_j ON source_id    │   │    │
│  │  │  RETURN ([obs_i.value], [obs_j.value])       │   │    │
│  │  └──────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Existing Detectors (unchanged)              │    │
│  │                                                     │    │
│  │  D-01 receives MetricDataFrame with N values/wndw  │    │
│  │  D-02 receives MetricDataFrame with N values/wndw  │    │
│  │  D-03 receives MetricDataFrame with N values/wndw  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 19.2 Translation Output

**Before (v1.0):**
```
MetricDataFrame.metrics = {
    "M-02": {"w00": [143.0]},        # 1 value
    "M-06": {"w00": [5420.0]}        # 1 value
}
```

**After (v1.5):**
```
MetricDataFrame.metrics = {
    "M-02": {"w00": [1.0, 1.0, 1.0, ..., 1.0]},  # 143 values
    "M-06": {"w00": [45, 120, 8, ..., 67]}         # 143 values
}
```

### 19.3 Detector Behavior Change

| Detector | v1.0 Behavior | v1.5 Behavior |
|----------|---------------|---------------|
| D-01 | `len(vals) = 1 < 10` → SKIP | `len(vals) = 143 ≥ 10` → KS TEST EXECUTES |
| D-02 | `n = 1` → Pearson undefined | `n = 143` → Pearson r computed |
| D-03 | Single-point CDF → degenerate | N-point CDF → bootstrap feasible |

### 19.4 Legacy Compatibility

The adapter ensures backward compatibility:

1. **Same interface:** `to_metric_dataframe()` returns `MetricDataFrame`
2. **Same structure:** `Dict[str, Dict[str, List[float]]]`
3. **Same semantics:** Each list contains float values per metric per window
4. **Extended semantics:** Lists now contain N values instead of 1
5. **No detector changes:** Detectors operate on the same `MetricDataFrame` type

---

## 20. Pipeline Evolution

### 20.1 v1.0 Pipeline (Current)

```
CLI
  ↓
RepositoryIngestionEngine.ingest()
  → RepositoryContext
  ↓
MetricExtractionEngine.extract()
  → MetricDataFrame (1 value per metric per window)
  ↓
WindowSegmentationEngine.segment()
  → List[WindowDefinition]
  ↓
MetricExtractionEngine.extract(windows=)
  → MetricDataFrame (re-extracted, same single values)
  ↓
DetectorDispatcherEngine.invoke()
  → DetectorResults (D-01 SKIPPED, D-02 UNDEFINED, D-03 DEGENERATE)
  ↓
ScoringEngine.compute_integrity_score()
  → ScorePackage
  ↓
EvidenceEngine.generate()
  → EvidencePackage
  ↓
ExplanationEngine.generate()
  → ExplanationReport
  ↓
ReportGenerator.generate()
  → ReportOutput
```

### 20.2 v1.5 Pipeline (New)

```
CLI
  ↓
RepositoryIngestionEngine.ingest()
  → RepositoryContext
  ↓
┌─────────────────────────────────────────────┐
│         Observation Engine                  │
│                                             │
│  CommitExtractor.extract()    ─┐           │
│  CoverageExtractor.extract()   │ parallel  │
│  ReviewExtractor.extract()     │           │
│  IssueExtractor.extract()      │           │
│  ComplexityExtractor.extract() ┘           │
│  ↓                                         │
│  List[Observation]                         │
│  ↓                                         │
│  ObservationStore.add(all)                 │
│  → ObservationStore                        │
│  ↓                                         │
│  WindowBuilder.build(store, config)        │
│  → List[ObservationWindow]                 │
│  ↓                                         │
│  DetectorAdapter.to_metric_dataframe()     │
│  → MetricDataFrame (N values per window)   │
│                                             │
└─────────────────────┬───────────────────────┘
                      ↓
DetectorDispatcherEngine.invoke()
  → DetectorResults (D-01 EXECUTES, D-02 EXECUTES, D-03 EXECUTES)
  ↓
ScoringEngine.compute_integrity_score()
  → ScorePackage
  ↓
EvidenceEngine.generate()
  → EvidencePackage
  ↓
ExplanationEngine.generate()
  → ExplanationReport
  ↓
ReportGenerator.generate()
  → ReportOutput
```

### 20.3 Pipeline Comparison

| Aspect | v1.0 | v1.5 |
|--------|------|------|
| Extraction | Single engine, aggregated | Multiple extractors, observation-level |
| Data model | MetricDataFrame | Observation → ObservationStore → MetricDataFrame |
| Windowing | After extraction, windows unknown | After storage, windows from observations |
| Re-extraction | Required (Step 3b) | Not required (observations already extracted) |
| Detector input | 1 value per metric per window | N values per metric per window |
| Cross-metric | Not possible | Via shared source_id |
| Re-extraction step | Required | Eliminated |

### 20.4 Elimination of Re-extraction

The v1.0 pipeline extracts metrics twice: once for initial data, once after windows are defined. The v1.5 pipeline eliminates this redundancy:

- **v1.0:** Extract → Segment → Re-extract (to get per-window data)
- **v1.5:** Extract (all observations) → Store → Window (group observations)

The re-extraction step is eliminated because observations are already per-commit. Windowing groups existing observations rather than re-extracting data.

---

## 21. Interface Contracts

### 21.1 IObservationExtractor

```
Interface: IObservationExtractor

Methods:
  extract(context: RepositoryContext, config: ExtractionConfig) → List[Observation]

Guarantees:
  - Returns finite list (may be empty)
  - All observations have deterministic IDs
  - All observations pass validation
  - Output is deterministic for same input + seed

Failure Conditions:
  - Repository inaccessible → ExtractionError
  - External tool missing → Empty list (metric unavailable)
  - Parse error → Skip individual items, log warnings

Complexity: O(n) where n = data items processed
```

### 21.2 IObservationStore

```
Interface: IObservationStore

Methods:
  add(observation: Observation) → None
  batch_add(observations: List[Observation]) → None
  get(observation_id: str) → Optional[Observation]
  query(metric_id?: str, source_type?: str, since?: datetime, until?: datetime) → List[Observation]
  count(metric_id?: str) → int
  get_values(metric_id: str) → List[float]
  get_source_ids(metric_id: str) → List[str]
  serialize() → str
  deserialize(data: str) → None

Guarantees:
  - add() is O(1) amortized
  - query() is O(log n + k)
  - All operations thread-safe for reads
  - Serialization is deterministic

Failure Conditions:
  - Duplicate observation_id → ValueError
  - Memory full → ExtractionError
  - Deserialization error → SerializationError

Complexity: See individual methods
```

### 21.3 IWindowBuilder

```
Interface: IWindowBuilder

Methods:
  build(store: ObservationStore, config: WindowConfig) → List[ObservationWindow]

Guarantees:
  - Windows are mutually exclusive
  - Windows are contiguous (no gaps)
  - Empty windows are excluded
  - Window IDs are sequential (w00, w01, ...)
  - Minimum observation count enforced

Failure Conditions:
  - Insufficient observations → Warning, partial windows
  - Invalid config → ValueError

Complexity: O(n log n) where n = observation count
```

### 21.4 IDetectorAdapter

```
Interface: IDetectorAdapter

Methods:
  to_metric_dataframe(windows: List[ObservationWindow], store: ObservationStore) → MetricDataFrame
  to_paired_observations(window: ObservationWindow, metric_i: str, metric_j: str) → Tuple[List[float], List[float]]

Guarantees:
  - Output MetricDataFrame is valid (passes schema validation)
  - All windows present in output
  - All metrics present in output
  - Paired observations joined by source_id

Failure Conditions:
  - No observations for metric → Empty list in output
  - No matching source_ids → Empty paired lists

Complexity: O(n) where n = observation count
```

### 21.5 IObservationEngine

```
Interface: IObservationEngine

Methods:
  extract_and_store(context: RepositoryContext, config: ObservationConfig) → ObservationStore
  build_windows(store: ObservationStore, config: WindowConfig) → List[ObservationWindow]
  to_detector_input(windows: List[ObservationWindow], store: ObservationStore) → MetricDataFrame
  full_pipeline(context: RepositoryContext, config: Config) → MetricDataFrame

Guarantees:
  - full_pipeline() produces valid MetricDataFrame
  - Deterministic for same input + seed
  - All intermediate states accessible for debugging

Failure Conditions:
  - Any extractor fails → Partial store with warnings
  - Store full → ExtractionError
  - Window building fails → ValueError

Complexity: O(n log n) where n = total observations
```

---

## 22. Architectural Invariants

### 22.1 Observation Immutability

**Invariant:** Once created, an Observation object is never mutated.

**Enforcement:** Observation dataclass is frozen (if using dataclasses) or has no setter methods.

**Rationale:** Prevents accidental corruption, enables safe concurrent access.

**Violation consequence:** Undefined behavior in detectors, broken reproducibility.

### 22.2 Deterministic Extraction

**Invariant:** Given identical (repository_state, config, seed), extraction produces byte-identical observations.

**Enforcement:** Deterministic IDs (SHA-256), sorted extraction order, seed-controlled random.

**Rationale:** Reproducibility requirement.

**Violation consequence:** Non-reproducible results, broken scientific validity.

### 22.3 Stable Ordering

**Invariant:** Observations are stored in deterministic order. Query results are deterministic.

**Enforcement:** Sorted by (timestamp, source_id, metric_id) as tiebreaker.

**Rationale:** Deterministic output requires deterministic ordering.

**Violation consequence:** Non-deterministic JSON serialization.

### 22.4 Window Purity

**Invariant:** Each observation belongs to at most one window. Windows are mutually exclusive.

**Enforcement:** WindowBuilder assigns based on timestamp, no overlap in ranges.

**Rationale:** Prevents double-counting in detectors.

**Violation consequence:** Inflated sample sizes, biased statistical tests.

### 22.5 Detector Isolation

**Invariant:** Each detector operates independently. Detector failures do not affect other detectors.

**Enforcement:** Per-detector try/except in dispatcher.

**Rationale:** Fault tolerance, independent execution.

**Violation consequence:** Single detector failure aborts entire analysis.

### 22.6 Reproducibility

**Invariant:** Stored observations can reproduce the analysis exactly.

**Enforcement:** Serialized store + config hash + seed.

**Rationale:** Scientific integrity.

**Violation consequence:** Findings cannot be verified.

### 22.7 No Aggregation Before Persistence

**Invariant:** Raw observations are stored before any aggregation occurs.

**Enforcement:** Extraction → Storage → Windowing → Aggregation pipeline order.

**Rationale:** Preserves distributional information for detectors.

**Violation consequence:** Information loss, detector degeneracy (same as v1.0).

### 22.8 Schema Forward Compatibility

**Invariant:** New fields added to Observation do not break existing code.

**Enforcement:** All new fields have default values. Existing code ignores unknown fields.

**Rationale:** Enables evolution without breaking changes.

**Violation consequence:** Version lock, inability to extend.

---

## 23. Error Handling Architecture

### 23.1 Error Hierarchy Extension

```
MIIEError (existing)
├── ObservationExtractionError (NEW)
│   ├── CommitExtractionError
│   ├── CoverageExtractionError
│   ├── ReviewExtractionError
│   ├── IssueExtractionError
│   └── ComplexityExtractionError
├── ObservationStoreError (NEW)
│   ├── DuplicateObservationError
│   ├── StoreFullError
│   └── SerializationError
├── WindowBuilderError (NEW)
│   ├── InsufficientObservationsError
│   ├── InvalidWindowConfigError
│   └── EmptyWindowError
├── AdapterError (NEW)
│   ├── TranslationError
│   └── PairingError
└── (existing errors unchanged)
```

### 23.2 Error Propagation Rules

| Rule | Description |
|------|-------------|
| Extraction errors | Logged as warnings, do not abort pipeline |
| Store errors | Raise immediately (data integrity) |
| Window errors | Logged as warnings, partial results returned |
| Adapter errors | Logged as warnings, empty lists in output |
| Detector errors | Per-detector try/except (existing behavior) |

### 23.3 Missing Data Policy

| Scenario | v1.0 Behavior | v1.5 Behavior |
|----------|---------------|---------------|
| Metric unavailable | None in list | Empty observation list |
| Window has no data | None in list | Window skipped |
| Source not accessible | Skip metric | Skip extractor, log warning |
| Tool not installed | Skip metric | Skip extractor, log warning |

---

## 24. Performance Architecture

### 24.1 Memory Architecture

```
Memory Budget (1000-commit repo):
├── Observations: ~5000 objects × 200 bytes ≈ 1 MB
├── Indices: ~5000 entries × 50 bytes ≈ 250 KB
├── Git output: ~5000 lines × 100 bytes ≈ 500 KB
├── MetricDataFrame: ~50 lists × 1000 floats ≈ 400 KB
├── Detector results: ~100 KB
└── Total: < 5 MB

Memory Budget (100K-commit repo):
├── Observations: ~500K objects × 200 bytes ≈ 100 MB
├── Indices: ~500K entries × 50 bytes ≈ 25 MB
├── Git output: ~500K lines × 100 bytes ≈ 50 MB
├── MetricDataFrame: ~50 lists × 100K floats ≈ 40 MB
├── Detector results: ~10 MB
└── Total: < 250 MB
```

### 24.2 CPU Architecture

| Operation | Complexity | Target (1K commits) | Target (100K commits) |
|-----------|-----------|---------------------|----------------------|
| Git log | O(n) | < 1s | < 30s |
| Git diff (per commit) | O(n × f) | < 10s | < 5min |
| Observation creation | O(n) | < 1s | < 30s |
| Store indexing | O(n) | < 1s | < 30s |
| Window building | O(n log n) | < 1s | < 30s |
| Adapter translation | O(n) | < 100ms | < 10s |
| Total extraction | O(n × f) | < 30s | < 30min |

### 24.3 Git Operations

| Operation | Frequency | Optimization |
|-----------|-----------|-------------|
| git log --format=%H\|%aI | Once per extraction | Single call, stream parsing |
| git diff --numstat | Once per commit | Parallel execution |
| git rev-list --count | Once | Cached |

### 24.4 Caching Strategy

| Cache | Key | TTL | Size Limit |
|-------|-----|-----|-----------|
| Commit list | repo_id + hash | Session | Unbounded |
| File stats | commit_sha | Session | Unbounded |
| Metric values | metric_id + window | Session | Unbounded |

### 24.5 Streaming Architecture

For repositories exceeding memory budget:

```
for commit_batch in get_commits(repo_path, batch_size=1000):
    observations = extract_observations(commit_batch)
    store.batch_add(observations)
    if store.count() > MAX_OBSERVATIONS:
        raise StoreFullError
```

---

## 25. Concurrency Architecture

### 25.1 Parallel Extraction

```
┌──────────────┐
│CommitExtractor│──────┐
└──────────────┘      │
                      │
┌──────────────┐      │      ┌──────────────┐
│CoverageExtractor│───┼─────→│ Observation  │
└──────────────┘      │      │    Store     │
                      │      └──────────────┘
┌──────────────┐      │             ↑
│ReviewExtractor│─────┤             │
└──────────────┘      │             │
                      │             │
┌──────────────┐      │             │
│IssueExtractor│──────┤             │
└──────────────┘      │             │
                      │             │
┌──────────────┐      │             │
│ComplexityExtractor│─┘             │
└──────────────┘                    │
                                    │
                    ┌───────────────┘
                    │
              ┌─────┴─────┐
              │   Batch   │
              │    Add    │
              └───────────┘
```

### 25.2 Synchronization Rules

| Resource | Access Pattern | Synchronization |
|----------|---------------|-----------------|
| ObservationStore | Write: extractors, Read: windows | Thread-safe add (dict is thread-safe in CPython) |
| Git operations | Read-only | No synchronization needed |
| WindowBuilder | Read from store, write windows | Sequential (after all extraction complete) |
| Adapter | Read windows + store | Read-only, no synchronization |

### 25.3 Thread Safety

| Component | Thread-Safe | Reason |
|-----------|-------------|--------|
| ObservationStore.add() | Yes (CPython) | GIL + dict operations |
| ObservationStore.query() | Yes | Read-only after extraction |
| WindowBuilder.build() | Yes (sequential) | Runs after extraction |
| DetectorAdapter | Yes (read-only) | No mutation |
| Extractors | Yes (independent) | No shared state |

---

## 26. Security Architecture

### 26.1 Data Sensitivity

| Data | Sensitivity | Handling |
|------|-------------|----------|
| Commit SHAs | LOW | Stored as source_id |
| Commit messages | LOW | Stored in metadata |
| Author names | MEDIUM | Stored in metadata, filtered if --exclude-bots |
| File contents | HIGH | NOT extracted (only metrics) |
| API tokens | CRITICAL | Never stored, loaded from .env only |
| Repository paths | LOW | Filtered from output unless --forensic |

### 26.2 Token Handling

```
Token priority:
  1. --auth-token CLI argument
  2. GITHUB_TOKEN environment variable
  3. .env file (via python-dotenv)

Token is NEVER:
  - Stored in observation metadata
  - Written to observation store JSON
  - Included in evidence packages
  - Logged in debug output
```

### 26.3 Observation Store Security

The observation store contains no secrets:
- Commit SHAs (public in most repos)
- Metric values (derived from public data)
- Timestamps (from git log)
- Author names (from git log)

---

## 27. Compatibility Architecture

### 27.1 Backward Compatibility

| Interface | v1.0 Contract | v1.5 Contract | Compatible? |
|-----------|--------------|--------------|-------------|
| CLI `analyze` | Same arguments | Same arguments | Yes |
| Config format | Same schema | Same schema + extensions | Yes |
| MetricDataFrame | 1 value per window | N values per window | Yes (superset) |
| DetectorResults | Dict-based output | Dict-based output | Yes (identical) |
| ScorePackage | IS + CS | IS + CS | Yes (identical) |
| EvidencePackage | Provenance + data | Provenance + data | Yes (extended) |
| Report format | 4 formats | 4 formats | Yes (identical) |

### 27.2 Forward Compatibility

| Mechanism | Description |
|-----------|-------------|
| Schema versioning | Observation.store_version field |
| Default values | All new fields have defaults |
| Unknown field handling | Existing code ignores unknown fields |
| Extension points | Extractors, window builders, adapters are pluggable |

### 27.3 Migration Path

```
Phase 1: Observation Engine runs alongside existing extraction
Phase 2: Pipeline routes through Observation Engine + adapter
Phase 3: Verify all 730 tests pass
Phase 4: Remove old extraction path
Phase 5: Update documentation
```

---

## 28. Configuration Architecture

### 28.1 New Configuration Fields

```yaml
# Existing fields (unchanged)
repo: "/path/to/repo"
metrics: ["M-02", "M-06"]
window_strategy: "time"
window_size: 7

# New fields (v1.5)
observation:
  extraction:
    parallel: true              # Enable parallel extraction
    batch_size: 1000            # Streaming batch size
    max_observations: 1000000   # Maximum observations per metric
    commit_metadata: true       # Extract commit metadata
  store:
    persist: false              # Persist store to disk
    persist_path: null          # Path for store JSON
  window:
    min_observations: 10        # Minimum per window
    hybrid_min_commits: 20      # Minimum commits for hybrid
```

### 28.2 Configuration Validation

| Rule | Description |
|------|-------------|
| min_observations ≥ 10 | Statistical test power |
| batch_size ≥ 100 | Efficiency |
| max_observations ≥ 1000 | Minimum viable analysis |
| persist_path writable | If persist=true |

### 28.3 Backward-Compatible Defaults

All new fields have defaults that produce v1.0-compatible behavior:
- `parallel: true` (performance improvement, no behavior change)
- `persist: false` (in-memory only, same as v1.0)
- `min_observations: 10` (matches detector requirements)

---

## 29. Extension Architecture

### 29.1 Future Detectors

| Detector | Data Requirements | Observation Types |
|----------|------------------|-------------------|
| D-04 (Bimodality) | Distribution shape | Commit-level values |
| D-05 (Multivariate) | Multi-metric observations | Paired cross-metric |
| D-06 (Trend Breakpoint) | Temporal series | Timestamp-ordered |
| D-07 (Seasonal) | Periodic data | High-frequency observations |

### 29.2 Future Observation Types

| Type | Source | Metric |
|------|--------|--------|
| File-level | git diff per file | M-06, M-07 |
| Hunk-level | git diff per hunk | M-06 |
| Developer-event | GitHub API | M-03, M-04, M-05 |
| CI-event | CI API | M-01 |
| Dependency-event | dependency files | New metric |

### 29.3 Plugin Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Extension Points                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  IObservationExtractor (Protocol)               │    │
│  │                                                 │    │
│  │  New extractors implement this interface         │    │
│  │  Registered via ObservationEngine.register()    │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  IWindowBuilder (Protocol)                      │    │
│  │                                                 │    │
│  │  New windowing strategies implement this         │    │
│  │  Registered via WindowBuilder.register()        │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  IDetectorAdapter (Protocol)                    │    │
│  │                                                 │    │
│  │  New adapter formats implement this interface    │    │
│  │  Registered via AdapterRegistry.register()      │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 29.4 External Provider Architecture

```
┌─────────────────────────────────────────────────────────┐
│              External Data Sources                      │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ GitHub   │  │ GitLab   │  │  CI/CD   │             │
│  │   API    │  │   API    │  │   API    │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │              │              │                    │
│       ▼              ▼              ▼                    │
│  ┌─────────────────────────────────────────────────┐    │
│  │         Provider Adapter Layer                  │    │
│  │                                                 │    │
│  │  Normalizes external data to Observation format │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 30. Architectural Decision Records

### ADR-001: Commit-Level Observation Granularity

**Status:** Accepted

**Context:** The Observation Engine needs a granularity for extracting observations from repositories.

**Decision:** Commit-level granularity (one observation per commit per metric).

**Alternatives considered:**
- File-level: Higher granularity but 10x storage overhead
- Hunk-level: Highest granularity but excessive complexity
- Developer-event: Interesting but requires identity resolution

**Rationale:** Commit-level provides adequate sample sizes (50–500 per window) with manageable storage. Git-native metrics naturally produce per-commit data.

**Consequences:**
- Positive: Simple extraction, adequate sample sizes
- Negative: File-level patterns not directly visible
- Mitigation: File metadata stored in observation metadata

### ADR-002: In-Memory Store with Optional Persistence

**Status:** Accepted

**Context:** The Observation Engine needs to store observations for querying and windowing.

**Decision:** In-memory store as primary, with optional JSON serialization for persistence.

**Alternatives considered:**
- SQLite: More powerful but adds dependency
- PostgreSQL: Over-engineered for current needs
- File-per-observation: Excessive I/O

**Rationale:** In-memory provides O(1) add and O(1) query for typical sizes. JSON serialization enables reproducibility without external dependencies.

**Consequences:**
- Positive: No new dependencies, fast operations
- Negative: Memory-limited for very large repos
- Mitigation: Streaming extraction with bounded batch sizes

### ADR-003: Adapter Layer for Backward Compatibility

**Status:** Accepted

**Context:** Existing detectors expect `MetricDataFrame` but the Observation Engine produces `ObservationWindow`.

**Decision:** Adapter layer translates `ObservationWindow` to `MetricDataFrame`.

**Alternatives considered:**
- Modify detector interfaces: Breaking change, requires major version bump
- Dual-path pipeline: Complexity, maintenance burden
- Deprecation period: Slow migration, unclear benefits

**Rationale:** Adapter preserves all existing contracts. Zero migration cost for users. Clean separation of concerns.

**Consequences:**
- Positive: All 730 tests pass, no user impact
- Negative: Translation overhead (O(n)), indirection layer
- Mitigation: Translation is simple list extraction, negligible cost

### ADR-004: Deterministic Observation IDs

**Status:** Accepted

**Context:** Observations need unique identifiers for storage and reproducibility.

**Decision:** Deterministic IDs computed as `SHA-256(source_type:source_id:metric_id)[:16]`.

**Alternatives considered:**
- UUID4: Non-deterministic, breaks reproducibility
- Sequential integers: Non-deterministic across runs
- Content hash: Deterministic but slow to compute

**Rationale:** Deterministic IDs ensure same source always produces same observation. SHA-256 provides collision resistance.

**Consequences:**
- Positive: Reproducible across runs, no randomness
- Negative: IDs not human-readable
- Mitigation: IDs are internal, not user-facing

### ADR-005: Elimination of Re-extraction Step

**Status:** Accepted

**Context:** The v1.0 pipeline extracts metrics twice (once for initial data, once after windows).

**Decision:** Eliminate re-extraction. Extract all observations first, then window.

**Alternatives considered:**
- Keep re-extraction: Wasteful but backward-compatible
- Lazy extraction: Complex, hard to reason about

**Rationale:** Re-extraction was needed because v1.0 extraction was window-agnostic. The Observation Engine extracts all data first, making re-extraction unnecessary.

**Consequences:**
- Positive: Simpler pipeline, faster execution
- Negative: All data extracted even if only subset needed
- Mitigation: Future optimization via lazy extraction

### ADR-006: Parallel Extractor Execution

**Status:** Accepted

**Context:** Multiple metric extractors need to run efficiently.

**Decision:** Extractors run in parallel after CommitExtractor completes (which provides the commit list).

**Alternatives considered:**
- Sequential: Simpler but slower
- Fully parallel: Commit extractor has no dependencies but others depend on its output

**Rationale:** CommitExtractor produces the commit list that other extractors need. After it completes, remaining extractors are independent.

**Consequences:**
- Positive: Faster extraction for multi-metric analysis
- Negative: Slightly more complex orchestration
- Mitigation: Simple thread pool or multiprocessing

---

## 31. Tradeoff Analysis

### 31.1 Granularity vs. Storage

| Choice | Granularity | Storage (1K commits) | Detector Compatibility |
|--------|-------------|---------------------|----------------------|
| Commit-level | Per-commit | ~1 MB | HIGH |
| File-level | Per-file | ~10 MB | MEDIUM |
| Hunk-level | Per-hunk | ~100 MB | LOW |

**Decision:** Commit-level. Optimal balance.

### 31.2 Memory vs. Persistence

| Choice | Memory | Reproducibility | Startup Time |
|--------|--------|-----------------|--------------|
| In-memory only | HIGH | LOW | LOW |
| Disk-backed | LOW | HIGH | MEDIUM |
| Hybrid | MEDIUM | HIGH | LOW |

**Decision:** Hybrid. Best of both worlds.

### 31.3 Compatibility vs. Innovation

| Choice | Compatibility | Innovation | Migration |
|--------|---------------|------------|-----------|
| Full adapter | HIGH | LOW | NONE |
| New interface | LOW | HIGH | HIGH |
| Gradual migration | MEDIUM | MEDIUM | MEDIUM |

**Decision:** Full adapter. Zero migration cost.

### 31.4 Determinism vs. Performance

| Choice | Determinism | Performance | Complexity |
|--------|-------------|-------------|------------|
| Fully deterministic | HIGH | MEDIUM | HIGH |
| Seed-controlled | HIGH | HIGH | MEDIUM |
| Mostly deterministic | MEDIUM | HIGH | LOW |

**Decision:** Seed-controlled. Deterministic for same seed.

---

## 32. Risk Analysis

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| R-1 | Observation count exceeds memory | MEDIUM | HIGH | Streaming extraction, bounded batch |
| R-2 | Extraction too slow for large repos | MEDIUM | MEDIUM | Parallel extraction, caching |
| R-3 | Non-deterministic extraction | LOW | HIGH | Deterministic IDs, sorted order |
| R-4 | Backward incompatibility | LOW | HIGH | Adapter layer, comprehensive testing |
| R-5 | Detector accuracy regression | LOW | MEDIUM | Benchmark validation, A/B testing |
| R-6 | Storage format instability | LOW | MEDIUM | Schema versioning |
| R-7 | Cross-platform inconsistency | MEDIUM | LOW | Path normalization, UTF-8 |
| R-8 | Insufficient sample for small repos | HIGH | MEDIUM | Graceful degradation, warnings |
| R-9 | Adapter translation error | LOW | HIGH | Comprehensive unit tests |
| R-10 | Observation ID collision | VERY LOW | LOW | SHA-256, 128-bit IDs |

---

## 33. Implementation Boundaries

### 33.1 What This Document Defines

| Element | Defined Here |
|---------|-------------|
| Architecture layers | Layer responsibilities and dependencies |
| Component contracts | Interface signatures, inputs, outputs |
| Observation lifecycle | State transitions, invariants |
| Storage model | Memory model, indexing, querying |
| Window algorithms | Temporal, commit-count, hybrid |
| Adapter logic | Translation rules, pairing strategy |
| Error hierarchy | New error types and propagation |
| Performance targets | Memory, CPU, timing budgets |
| Security model | Data sensitivity, token handling |
| Extension points | Plugin interfaces, future detectors |

### 33.2 What Belongs in Implementation

| Element | Belongs In |
|---------|-----------|
| Git command syntax | Implementation code |
| JSON serialization format | ODSS document |
| Specific library choices | Implementation discretion |
| Test case definitions | Test specification |
| CI/CD integration | DevOps configuration |
| Documentation examples | User guide |
| Benchmark suite design | Benchmark specification |

---

## 34. Validation Strategy

### 34.1 Architecture Compliance Tests

| Test | Description | Pass Criteria |
|------|-------------|--------------|
| AC-1 | Observation immutability | Cannot set attributes after creation |
| AC-2 | Deterministic IDs | Same input → same ID |
| AC-3 | Store indexing | Query returns correct results |
| AC-4 | Window purity | No observation in multiple windows |
| AC-5 | Adapter output | Valid MetricDataFrame |
| AC-6 | Pipeline end-to-end | All 730 tests pass |
| AC-7 | Reproducibility | Same seed → byte-identical JSON |
| AC-8 | Performance | Within timing budgets |

### 34.2 Statistical Validation

| Test | Description | Pass Criteria |
|------|-------------|--------------|
| SV-1 | D-01 executes on observations | KS test produces valid p-value |
| SV-2 | D-02 computes correlation | Pearson r in [-1, 1] |
| SV-3 | D-03 bootstrap | CI coverage ≥ 90% |
| SV-4 | Cross-metric pairing | Matched pairs have same source_id |

### 34.3 Regression Validation

| Test | Description | Pass Criteria |
|------|-------------|--------------|
| RV-1 | Existing benchmarks | Accuracy within ±5% |
| RV-2 | CLI output format | Identical structure |
| RV-3 | Config compatibility | Same configs produce valid results |
| RV-4 | Error handling | Same error codes for same failures |

---

## 35. Acceptance Criteria

### 35.1 Functional Acceptance

| ID | Criterion | Verification |
|----|-----------|-------------|
| F-1 | D-01 executes KS test (not skipped) | Unit test |
| F-2 | D-02 computes Pearson r on paired observations | Unit test |
| F-3 | D-03 performs bootstrap on observation data | Unit test |
| F-4 | All 730 existing tests pass | Test suite |
| F-5 | CLI output format unchanged | Integration test |
| F-6 | Observation IDs deterministic | Unit test |
| F-7 | Serialization produces identical JSON | Unit test |
| F-8 | Cross-metric correlation computed | Unit test |

### 35.2 Non-Functional Acceptance

| ID | Criterion | Target |
|----|-----------|--------|
| NF-1 | Extraction time (1K commits) | < 30 seconds |
| NF-2 | Memory usage (1K commits) | < 500 MB |
| NF-3 | Observation query time | < 1ms |
| NF-4 | Adapter translation time | < 100ms |
| NF-5 | JSON serialization (10K observations) | < 1 second |

### 35.3 Scientific Acceptance

| ID | Criterion | Verification |
|----|-----------|-------------|
| S-1 | D-01 KS test produces valid p-values | Statistical validation |
| S-2 | D-02 Pearson r in [-1, 1] | Statistical validation |
| S-3 | D-03 bootstrap CI coverage ≥ 90% | Simulation study |
| S-4 | Cross-metric pairing works | Unit test |
| S-5 | Temporal ordering preserved | Unit test |

---

## 36. Glossary

| Term | Definition |
|------|-----------|
| Observation | A single data point extracted from a repository source |
| ObservationStore | In-memory container for observations with indexing |
| ObservationWindow | A collection of observations within a time/commit window |
| Adapter Layer | Translation shim between Observation Engine and legacy detectors |
| MetricDataFrame | v1.0 data container (aggregated values, replaced by observations) |
| Deterministic extraction | Same input produces same output, always |
| Seed-controlled | Random operations use a fixed seed for reproducibility |
| Window purity | Each observation belongs to at most one window |
| Cross-metric linking | Joining observations from different metrics by shared source_id |
| Observation ID | Deterministic identifier computed from source metadata |

---

## 37. Appendix

### 37.1 Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| PRD-v1.5-OE | docs/architecture/observation_engine/ | Product Requirements |
| RELEASE_BASELINE.md | docs/architecture/ | v1.0.1 baseline |
| V1_5_DEVELOPMENT_ENTRY.md | docs/roadmap/ | v1.5 development plan |
| BASELINE_CHANGE_POLICY.md | docs/governance/ | Change management |

### 37.2 Interface Summary

| Interface | ID | Methods |
|-----------|-----|---------|
| IObservationExtractor | EXT-01 | extract() |
| IObservationStore | STR-01 | add(), get(), query(), count(), serialize() |
| IWindowBuilder | WIN-01 | build() |
| IDetectorAdapter | ADP-01 | to_metric_dataframe(), to_paired_observations() |
| IObservationEngine | OBE-01 | extract_and_store(), build_windows(), to_detector_input(), full_pipeline() |

### 37.3 Schema Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-29 | Initial specification |

---

*End of Document*
