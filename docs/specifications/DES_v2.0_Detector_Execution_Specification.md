# Detector Execution Specification (DES) v2.0

**MIIE v1.5 — Detector Subsystem Engineering Specification**

| Field | Value |
|-------|-------|
| Document ID | DES-v2.0 |
| Version | 2.0.0 |
| Status | Canonical |
| Date | 2026-06-29 |
| Authors | MIIE Engineering |
| Approved By | Repository Governance |
| Derived From | PRD-v1.5-OE, OEAS-v1.5, ODSS-v1.0 |
| Supersedes | DES-v1.0 (implicit in v1.0.1 codebase) |
| Scope | Detector execution architecture over Observation Engine |
| Classification | Definition-only (no implementation code) |

---

## Table of Contents

1. [Document Metadata](#1-document-metadata)
2. [Purpose](#2-purpose)
3. [Scope](#3-scope)
4. [Objectives](#4-objectives)
5. [Non-Objectives](#5-non-objectives)
6. [Detector Philosophy](#6-detector-philosophy)
7. [Detector Design Principles](#7-detector-design-principles)
8. [Scientific Principles](#8-scientific-principles)
9. [Detector Framework Overview](#9-detector-framework-overview)
10. [Detector Lifecycle](#10-detector-lifecycle)
11. [Detector Dispatcher](#11-detector-dispatcher)
12. [Detector Context](#12-detector-context)
13. [Observation Query Model](#13-observation-query-model)
14. [Window Resolution](#14-window-resolution)
15. [Execution Pipeline](#15-execution-pipeline)
16. [Detector Input Contracts](#16-detector-input-contracts)
17. [Detector Output Contracts](#17-detector-output-contracts)
18. [Evidence Contracts](#18-evidence-contracts)
19. [Confidence Contracts](#19-confidence-contracts)
20. [Execution Environment](#20-execution-environment)
21. [D-01 Execution Specification](#21-d-01-execution-specification)
22. [D-02 Execution Specification](#22-d-02-execution-specification)
23. [D-03 Execution Specification](#23-d-03-execution-specification)
24. [Cross-Detector Coordination](#24-cross-detector-coordination)
25. [Shared Utilities](#25-shared-utilities)
26. [Performance Targets](#26-performance-targets)
27. [Complexity Analysis](#27-complexity-analysis)
28. [Parallel Execution Strategy](#28-parallel-execution-strategy)
29. [Caching Strategy](#29-caching-strategy)
30. [Failure Handling](#30-failure-handling)
31. [Recovery Strategy](#31-recovery-strategy)
32. [Logging Requirements](#32-logging-requirements)
33. [Validation Requirements](#33-validation-requirements)
34. [Compatibility with v1.0.1](#34-compatibility-with-v101)
35. [Migration Strategy](#35-migration-strategy)
36. [Future Detector Support](#36-future-detector-support)
37. [Architectural Invariants](#37-architectural-invariants)
38. [Trade-off Analysis](#38-trade-off-analysis)
39. [Risk Register](#39-risk-register)
40. [Acceptance Criteria](#40-acceptance-criteria)
41. [Future Evolution](#41-future-evolution)
42. [Glossary](#42-glossary)
43. [Appendix](#43-appendix)

---

## 1. Document Metadata

| Field | Value |
|-------|-------|
| Document ID | DES-v2.0 |
| Version | 2.0.0 |
| Date | 2026-06-29 |
| Classification | Internal Engineering Specification |
| Status | Canonical |
| Baseline | v1.0.1 (tag `4c4d5e6`) |
| Supersedes | Implicit v1.0 detector logic in codebase |
| Dependencies | PRD-v1.5-OE, OEAS-v1.5, ODSS-v1.0 |
| Related Documents | RELEASE_BASELINE.md, BASELINE_CHANGE_POLICY.md |

### Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-06-29 | MIIE Engineering | Initial implicit detector logic in codebase |
| 2.0.0 | 2026-06-29 | MIIE Engineering | Complete re-specification over Observation Engine |

---

## 2. Purpose

This document defines the **complete detector execution architecture** for MIIE v1.5. It specifies how every detector executes inside the Observation Engine — from observation retrieval through evidence generation and result packaging.

The DES exists because MIIE v1.0 detectors execute over aggregated `MetricDataFrame` objects that contain a single value per metric per window. This causes D-01 to always skip (n=1 < 10), D-02 Pearson to be undefined (n=1), and D-03 to produce degenerate CDFs. The v1.5 Observation Engine replaces aggregated extraction with per-commit observation-level extraction, and this document specifies how detectors consume that new data.

This document is implementation-independent. It specifies *what* must exist and *why*, not *how* to code it. An engineer implementing the detector subsystem must follow this specification precisely. Deviations require an Architecture Decision Record (ADR) and approval from the architecture owner.

---

## 3. Scope

### 3.1 In Scope

| Component | Scope |
|-----------|-------|
| Detector lifecycle | Initialization through cleanup |
| Detector dispatching | Routing observations to detectors |
| Detector context | Per-detector execution context |
| Observation query | How detectors retrieve observations |
| Window resolution | How windows are prepared for detectors |
| Execution pipeline | Stage-by-stage execution flow |
| Input contracts | What detectors receive |
| Output contracts | What detectors produce |
| Evidence contracts | What evidence detectors generate |
| Confidence contracts | How confidence is estimated |
| D-01 execution | Complete specification for Distribution Drift |
| D-02 execution | Complete specification for Correlation Breakdown |
| D-03 execution | Complete specification for Threshold Compression |
| Cross-detector coordination | How detectors share information |
| Shared utilities | Common statistical functions |
| Performance targets | Latency and throughput requirements |
| Complexity analysis | Time and space complexity per detector |
| Parallel execution | Concurrent detector execution |
| Caching | Result caching strategy |
| Failure handling | Error types and recovery |
| Future extensibility | Plugin detectors, streaming, hybrid |

### 3.2 Out of Scope

| Component | Reason | Target |
|-----------|--------|--------|
| Detector algorithms | Algorithms remain unchanged from v1.0 | v1.5 unchanged |
| Scoring formulas | Frozen per baseline | v2.0 |
| Evidence engine | Separate specification | v1.5 separate |
| Explanation engine | Separate specification | v1.5 separate |
| Reporting engine | Separate specification | v1.5 unchanged |
| CLI interface | Frozen per baseline | v2.0 |
| Observation extraction | Defined in OEAS | OEAS scope |
| Observation storage | Defined in OEAS | OEAS scope |
| Window construction | Defined in OEAS | OEAS scope |

---

## 4. Objectives

| ID | Objective | Priority | Verification |
|----|-----------|----------|-------------|
| OBJ-1 | Every detector receives sufficient observations for statistical validity | HIGH | D-01/D-02/D-03 execute on ≥10 observations per window |
| OBJ-2 | Detectors execute over ObservationCollections, not aggregated MetricDataFrames | HIGH | Adapter translates observations → detector input |
| OBJ-3 | Detector mathematics remain scientifically correct | HIGH | Same algorithms, same thresholds, same output semantics |
| OBJ-4 | Backward compatibility preserved via adapter layer | HIGH | All 730 existing tests pass |
| OBJ-5 | Deterministic execution for same seed + config | HIGH | Byte-identical detector outputs |
| OBJ-6 | Per-detector failure isolation | HIGH | One detector failure does not affect others |
| OBJ-7 | Evidence provenance tracked for every detector result | MEDIUM | Every result linked to observations used |
| OBJ-8 | Extensibility for future detectors | MEDIUM | Plugin interface for new detectors |
| OBJ-9 | Performance bounded for 100K+ observations | LOW | Execution completes within time budget |

---

## 5. Non-Objectives

| ID | Non-Objective | Reason |
|----|--------------|--------|
| NO-1 | Redesign detector algorithms | Algorithms are scientifically validated; change requires re-validation |
| NO-2 | Redesign scoring formulas | Frozen per v1.0.1 baseline |
| NO-3 | Implement ML-based detectors | Requires training data infrastructure (v2.0) |
| NO-4 | Implement streaming detectors | Requires streaming infrastructure (v2.0) |
| NO-5 | Implement cross-repo detectors | Requires workspace management (v1.6) |
| CLI-6 | Change CLI interface | Frozen per v1.0.1 baseline |

---

## 6. Detector Philosophy

### 6.1 Observations First

Detectors operate on observations — individual data points extracted from repository sources. A detector receives a collection of observations organized into windows and produces results that characterize the statistical properties of those observations.

### 6.2 Statistical Validity

Every detector must have sufficient sample size to produce statistically meaningful results. Detectors must never operate on fewer observations than their statistical method requires. When sample size is insufficient, detectors must report this explicitly rather than producing misleading results.

### 6.3 Deterministic Execution

Given identical observations, identical windows, and identical configuration, a detector must produce identical results. Determinism is enforced through:
- Sorted observation iteration (stable ordering)
- Seed-controlled random operations (bootstrap, sampling)
- Deterministic statistical functions (no floating-point non-determinism)

### 6.4 Failure Isolation

Each detector executes in isolation. A failure in one detector must not prevent other detectors from executing. The dispatcher captures failures and reports them as detector-level errors without affecting the overall pipeline.

### 6.5 Evidence Provenance

Every detector result must be traceable to the specific observations, windows, and parameters that produced it. This enables reproducibility, debugging, and audit trails.

---

## 7. Detector Design Principles

### 7.1 Principle: Single Responsibility

Each detector has one responsibility: detecting one class of statistical anomaly. D-01 detects distributional drift. D-02 detects correlation breakdown. D-03 detects threshold compression. Detectors must not combine multiple detection concerns.

### 7.2 Principle: Open-Closed

Detectors are open for extension (new detectors can be registered) but closed for modification (existing detector algorithms are not changed). The dispatcher and registry support new detectors without modifying existing code.

### 7.3 Principle: Dependency Inversion

Detectors depend on abstractions (interfaces), not concrete implementations. The `IDetector` interface defines the contract. Detectors do not depend on `ObservationStore`, `ObservationCollection`, or any other implementation detail.

### 7.4 Principle: Interface Segregation

Detectors receive only the data they need. D-01 receives distributional data per metric per window. D-02 receives paired observation data per metric pair per window. D-03 receives threshold-proximity data per metric per window. No detector receives more data than required.

### 7.5 Principle: Least Knowledge

Detectors do not know how observations were extracted, how windows were constructed, or how other detectors execute. They operate solely on the data provided by the adapter layer.

---

## 8. Scientific Principles

### 8.1 Statistical Test Validity

| Detector | Statistical Test | Minimum Sample Size | Consequence of Violation |
|----------|-----------------|---------------------|------------------------|
| D-01 | Kolmogorov-Smirnov two-sample | 10 per window | Test loses power; false negatives |
| D-01 | Population Stability Index | 10 per window | Bin proportions unreliable |
| D-02 | Pearson correlation | 10 paired observations | Correlation undefined |
| D-02 | Spearman rank correlation | 10 paired observations | Rank correlation unreliable |
| D-02 | Fisher z-transform CI | 10 paired observations | CI width explodes |
| D-03 | Excess Mass z-test | 20 per window | z-test loses power |
| D-03 | Dip test (bootstrap) | 20 per window | Bootstrap unreliable |

### 8.2 Multiple Comparison Correction

D-02 analyzes O(K²) metric pairs across K windows. When K is large, the number of statistical tests grows quadratically. The current implementation does not apply Bonferroni or FDR correction. This is documented as a known limitation and is not changed in v1.5.

### 8.3 Bootstrap Determinism

D-03 dip test uses bootstrap resampling with a fixed seed. This ensures reproducibility: the same observations always produce the same p-value. The seed is part of the detector configuration and is recorded in provenance.

### 8.4 Distribution-Free Tests

D-01 uses the Kolmogorov-Smirnov test, which is distribution-free (makes no assumption about the underlying distribution). This is appropriate because MIIE metrics do not follow known parametric distributions.

---

## 9. Detector Framework Overview

### 9.1 System Context Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MIIE v1.5 Pipeline                               │
│                                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────────┐    │
│  │Ingestion │──▶│Extraction│──▶│ Windowing│──▶│Observation Engine│    │
│  │  Engine   │   │  Engine  │   │  Engine  │   │  (OEAS L0-L4)    │    │
│  └──────────┘   └──────────┘   └──────────┘   └────────┬─────────┘    │
│                                                          │              │
│                                         ┌────────────────┼───────────┐  │
│                                         │  ObservationCollection     │  │
│                                         │  + ObservationWindows      │  │
│                                         └────────────────┬───────────┘  │
│                                                          │              │
│                                         ┌────────────────▼───────────┐  │
│                                         │    Detector Dispatcher     │  │
│                                         │    (DES §11)               │  │
│                                         └────────────────┬───────────┘  │
│                                                          │              │
│                           ┌──────────────────────────────┼──────┐      │
│                           │              │               │      │      │
│                    ┌──────▼──────┐ ┌─────▼─────┐ ┌──────▼────┐ │      │
│                    │    D-01     │ │    D-02    │ │    D-03   │ │      │
│                    │  Drift      │ │ Correlation│ │ Threshold │ │      │
│                    └──────┬──────┘ └─────┬─────┘ └──────┬────┘ │      │
│                           │              │               │      │      │
│                           └──────────────┼───────────────┘      │      │
│                                          │                      │      │
│                                         ┌▼──────────────────────▼┐     │
│                                         │    DetectorResults     │     │
│                                         └────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Component Summary

| Component | Responsibility | Location |
|-----------|---------------|----------|
| ObservationCollection | Holds all observations | OEAS L3 Storage |
| ObservationWindow | Groups observations by time/commit | OEAS L4 Window |
| Detector Dispatcher | Routes observations to detectors | DES §11 |
| Detector Context | Per-detector execution state | DES §12 |
| D-01 | Distributional drift detection | DES §21 |
| D-02 | Correlation breakdown detection | DES §22 |
| D-03 | Threshold compression detection | DES §23 |
| Adapter Layer | Translates observations → detector input | OEAS L5 |
| Detector Results | Aggregated detector outputs | DES §17 |

---

## 10. Detector Lifecycle

### 10.1 Lifecycle States

```
┌────────────┐     ┌──────────────┐     ┌──────────────┐
│Registered  │────▶│  Initialized │────▶│  Validating  │
└────────────┘     └──────────────┘     └──────┬───────┘
                                                │
                         ┌──────────────────────┤
                         │                      │
                    ┌────▼────┐            ┌────▼────┐
                    │  Ready  │            │ Skipped │
                    └────┬────┘            └─────────┘
                         │
                    ┌────▼────┐
                    │Executing│
                    └────┬────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
         ┌────▼───┐ ┌───▼────┐ ┌───▼────┐
         │Completed│ │  Error │ │Partial │
         └────────┘ └────────┘ └────────┘
```

### 10.2 State Definitions

| State | Description |
|-------|-------------|
| Registered | Detector is registered in the registry but not yet used |
| Initialized | Detector has been instantiated with configuration |
| Validating | Detector is validating its input data |
| Ready | Input validated; detector is ready to execute |
| Skipped | Input validation failed; detector will not execute |
| Executing | Detector is running its statistical methods |
| Completed | Detector finished successfully |
| Error | Detector encountered an unrecoverable error |
| Partial | Detector completed but some windows were skipped |

### 10.3 Lifecycle Transitions

| From | To | Trigger |
|------|----|---------|
| Registered | Initialized | Dispatcher calls init with config |
| Initialized | Validating | Dispatcher calls validate_input() |
| Validating | Ready | All preconditions satisfied |
| Validating | Skipped | Insufficient data or metrics |
| Ready | Executing | Dispatcher calls execute() |
| Executing | Completed | All windows processed |
| Executing | Error | Unrecoverable exception |
| Executing | Partial | Some windows skipped due to sample size |

### 10.4 State Transition Rules

| Rule | Description |
|------|-------------|
| R-1 | A detector cannot execute without passing validation |
| R-2 | A detector cannot transition from Error to Executing |
| R-3 | A detector cannot transition from Completed back to Executing |
| R-4 | Skipped detectors produce no output but are recorded in dispatch summary |
| R-5 | Partial detectors produce output for successful windows only |

---

## 11. Detector Dispatcher

### 11.1 Purpose

The Detector Dispatcher is the orchestrator that manages detector execution. It routes observations to detectors, manages the lifecycle, handles failures, and collects results.

### 11.2 Responsibilities

| Responsibility | Description |
|---------------|-------------|
| Routing | Select which detectors to invoke based on enabled list |
| Lifecycle management | Manage state transitions for each detector |
| Input preparation | Use adapter to prepare detector-specific input |
| Execution | Invoke detector.execute() for each enabled detector |
| Failure isolation | Catch and record per-detector failures |
| Result collection | Aggregate results from all detectors |
| Dispatch summary | Record what was dispatched, skipped, failed |

### 11.3 Dispatch Algorithm

```
INPUT:  ObservationCollection, Config, EnabledDetectors
OUTPUT: DetectorResults, DispatchSummary

1. FOR each detector_id in EnabledDetectors:
2.   detector ← registry.get(detector_id)
3.   context ← DetectorContext(detector_id, collection, config)
4.   validation_result ← detector.validate_input(context)
5.   IF validation_result == PASSED:
6.     result ← detector.execute(context)
7.     results[detector_id] ← result
8.     summary.record_completed(detector_id)
9.   ELSE IF validation_result == INSUFFICIENT_DATA:
10.    summary.record_skipped(detector_id, reason)
11.  ELSE:
12.    summary.record_error(detector_id, error)
13. RETURN results, summary
```

### 11.4 Dispatch Summary

| Field | Type | Description |
|-------|------|-------------|
| total_detectors | integer | Number of detectors considered |
| completed | list<string> | Detector IDs that completed successfully |
| skipped | list<string> | Detector IDs skipped due to insufficient data |
| errors | list<string> | Detector IDs that failed with errors |
| skipped_reasons | map<string, string> | Reason for each skip |
| error_details | map<string, string> | Error message for each failure |
| dispatch_timestamp | ISO-8601 datetime | When dispatch completed |
| total_execution_ms | integer | Total execution time |

---

## 12. Detector Context

### 12.1 Purpose

The Detector Context encapsulates everything a detector needs to execute. It is created by the dispatcher and passed to the detector. The detector does not create its own context.

### 12.2 Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| detector_id | string | Yes | Identifier of the detector |
| detector_version | string | Yes | Version of the detector |
| observation_collection | ObservationCollection | Yes | Full observation collection |
| windows | list<ObservationWindow> | Yes | Windows to analyze |
| config | Config | Yes | Analysis configuration |
| metric_list | list<string> | Yes | Metrics available for this detector |
| seed | integer | Yes | Random seed for reproducibility |
| start_time | ISO-8601 datetime | Yes | When execution started |
| provenance | Provenance | Yes | Execution provenance |

### 12.3 Context Query Methods

The context provides convenience methods for detectors to query observations:

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| get_observations(window_id, metric_id) | window_id, metric_id | list<Observation> | All observations in a window for a metric |
| get_window(window_id) | window_id | ObservationWindow | Full window object |
| get_all_windows() | — | list<ObservationWindow> | All windows |
| get_metric_values(window_id, metric_id) | window_id, metric_id | list<float> | Values only (for statistical tests) |
| get_paired_values(window_id, mi, mj) | window_id, mi, mj | tuple<list<float>, list<float>> | Paired values for correlation |
| get_window_count() | — | integer | Number of windows |
| get_observation_count(window_id) | window_id | integer | Number of observations in window |

### 12.4 Context Immutability

The context is read-only from the detector's perspective. Detectors cannot modify the observation collection, windows, or configuration through the context. This ensures that one detector's execution cannot affect another's.

---

## 13. Observation Query Model

### 13.1 Purpose

The Observation Query Model defines how detectors retrieve observations from the collection. This is the interface between the adapter layer and the detector.

### 13.2 Query Types

| Query Type | Input | Output | Used By |
|-----------|-------|--------|---------|
| Distribution query | window_id, metric_id | list<float> | D-01 |
| Paired query | window_id, metric_i, metric_j | tuple<list<float>, list<float>> | D-02 |
| Threshold query | window_id, metric_id, threshold, epsilon | list<float> (filtered) | D-03 |
| Source query | source_type, source_id | list<Observation> | Adapter |

### 13.3 Query Execution

```
DISTRIBUTION QUERY:
  Input:  window_id = "w00", metric_id = "M-02"
  Process:
    1. window ← collection.get_window(window_id)
    2. observations ← window.observations WHERE metric_id == "M-02"
    3. values ← [obs.value FOR obs IN observations WHERE obs.quality == "complete"]
  Output: [143.0, 156.0, 129.0, ...]

PAIRED QUERY:
  Input:  window_id = "w00", metric_i = "M-02", metric_j = "M-06"
  Process:
    1. obs_i ← collection.get_observations(window_id, metric_i)
    2. obs_j ← collection.get_observations(window_id, metric_j)
    3. paired_i, paired_j ← align_by_source_id(obs_i, obs_j)
  Output: ([143.0, 156.0, ...], [0.75, 0.82, ...])

THRESHOLD QUERY:
  Input:  window_id = "w00", metric_id = "M-02", threshold = 100, epsilon = 5
  Process:
    1. values ← distribution_query(window_id, metric_id)
    2. filtered ← [v FOR v IN values IF |v - threshold| <= epsilon]
  Output: [98.0, 102.0, 100.0, ...]
```

### 13.4 Quality Filtering

All queries apply quality filtering before returning values:

| Quality | Treatment |
|---------|-----------|
| complete | Included in results |
| estimated | Included but flagged |
| missing | Excluded |
| derived | Included with provenance tracking |

### 13.5 Alignment for Paired Queries

D-02 requires paired observations — observations from the same source (commit) for two different metrics. The adapter aligns observations by source_id:

```
ALIGNMENT ALGORITHM:
  Input:  observations_i, observations_j
  Process:
    1. index_i ← {obs.source_id: obs FOR obs IN observations_i}
    2. index_j ← {obs.source_id: obs FOR obs IN observations_j}
    3. common_sources ← INTERSECT(keys(index_i), keys(index_j))
    4. paired_i ← [index_i[sid].value FOR sid IN SORTED(common_sources)]
    5. paired_j ← [index_j[sid].value FOR sid IN SORTED(common_sources)]
  Output: paired_i, paired_j
```

---

## 14. Window Resolution

### 14.1 Purpose

Window Resolution prepares windows for detector execution. It validates window boundaries, checks minimum sample sizes, and flags windows that cannot be analyzed.

### 14.2 Resolution Steps

| Step | Description |
|------|-------------|
| 1 | Receive windows from Observation Engine |
| 2 | Sort windows by window_id (stable ordering) |
| 3 | For each window, count observations per metric |
| 4 | Flag windows with < minimum sample size |
| 5 | For D-01, flag windows with < 2 windows (need pairs) |
| 6 | For D-02, flag windows with < 10 paired observations |
| 7 | For D-03, flag windows with < 20 observations |
| 8 | Return resolved windows with flags |

### 14.3 Minimum Sample Size Gates

| Detector | Minimum Per Window | Minimum Windows | Consequence |
|----------|-------------------|-----------------|-------------|
| D-01 | 10 observations per metric | 2 windows | Skip window pair if insufficient |
| D-02 | 10 paired observations per metric pair | 2 windows | Skip window if insufficient |
| D-03 | 20 observations per metric | 1 window | Skip window if insufficient |

### 14.4 Window Pair Generation (D-01)

D-01 analyzes consecutive window pairs. The window resolver generates pairs:

```
WINDOW PAIR GENERATION:
  Input:  windows = [w00, w01, w02, w03]
  Process:
    1. pairs ← [(w00,w01), (w01,w02), (w02,w03)]
  Output: 3 pairs
```

### 14.5 Window Pair Generation (D-02)

D-02 analyzes all windows for each metric pair. The window resolver generates per-pair trajectories:

```
WINDOW TRAJECTORY GENERATION:
  Input:  windows = [w00, w01, w02, w03], metric_pair = (M-01, M-02)
  Process:
    1. FOR each window in windows:
    2.   paired_i, paired_j ← paired_query(window, M-01, M-02)
    3.   IF len(paired_i) >= 10:
    4.     trajectory.append((pearson(paired_i, paired_j), spearman(paired_i, paired_j)))
    5.   ELSE:
    6.     trajectory.append((None, None))
  Output: trajectory of length len(windows)
```

---

## 15. Execution Pipeline

### 15.1 Pipeline Stages

```
┌──────────────────────────────────────────────────────────────────────┐
│                     DETECTOR EXECUTION PIPELINE                       │
│                                                                       │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌──────┐ │
│  │ Stage 1 │──▶│ Stage 2 │──▶│ Stage 3 │──▶│ Stage 4 │──▶│Stage5│ │
│  │ Context │   │ Resolve │   │Validate │   │Execute  │   │Result│ │
│  │Creation │   │ Windows │   │  Input  │   │ Detector│   │Packag│ │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   └──────┘ │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ Stage 6: Evidence Collection                                    │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ Stage 7: Confidence Estimation                                  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ Stage 8: Result Packaging                                       │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

### 15.2 Stage Definitions

| Stage | Name | Description |
|-------|------|-------------|
| 1 | Context Creation | Dispatcher creates DetectorContext for each detector |
| 2 | Window Resolution | Prepare windows, check sample sizes, generate pairs |
| 3 | Input Validation | Detector validates that required metrics and samples exist |
| 4 | Execute Detector | Run detector's statistical methods on resolved data |
| 5 | Result Packaging | Format output as DetectorResult |
| 6 | Evidence Collection | Collect evidence for each detection event |
| 7 | Confidence Estimation | Estimate confidence in each result |
| 8 | Result Packaging | Final packaging with metadata, provenance, timing |

### 15.3 Stage Timing

Each stage records timing information:

| Field | Type | Description |
|-------|------|-------------|
| stage_name | string | Name of the stage |
| start_time | ISO-8601 datetime | When stage started |
| end_time | ISO-8601 datetime | When stage completed |
| duration_ms | integer | Duration in milliseconds |
| status | string | "completed", "skipped", "error" |

---

## 16. Detector Input Contracts

### 16.1 Purpose

The Detector Input Contract specifies exactly what data each detector receives. This is the contract between the adapter layer and the detector.

### 16.2 Common Input

All detectors receive:

| Field | Type | Description |
|-------|------|-------------|
| detector_id | string | Detector identifier |
| detector_version | string | Detector version |
| windows | list<ObservationWindow> | Resolved windows |
| metric_list | list<string> | Available metrics |
| config | Config | Analysis configuration |
| seed | integer | Random seed |
| provenance | Provenance | Execution provenance |

### 16.3 D-01 Input Contract

| Field | Type | Description |
|-------|------|-------------|
| distributions | map<string, map<string, list<float>>> | metric_id → window_id → values |
| window_pairs | list<tuple<string, string>> | Consecutive window pairs |
| ks_p_value_threshold | float | Significance threshold (default: 0.05) |
| psi_threshold | float | PSI threshold (default: 0.25) |
| min_sample_size | integer | Minimum observations per window (default: 10) |

### 16.4 D-02 Input Contract

| Field | Type | Description |
|-------|------|-------------|
| paired_trajectories | map<string, list<tuple<list<float>, list<float>>>> | pair_key → per-window paired values |
| metric_pairs | list<tuple<string, string>> | All metric pairs |
| window_ids | list<string> | Ordered window IDs |
| sudden_drop_threshold | float | Delta-r threshold (default: 0.3) |
| sign_reversal_min_correlation | float | Minimum |r| for sign reversal (default: 0.2) |
| gradual_erosion_slope_threshold | float | Slope threshold (default: -0.1) |
| min_paired_observations | integer | Minimum paired obs per window (default: 10) |

### 16.5 D-03 Input Contract

| Field | Type | Description |
|-------|------|-------------|
| distributions | map<string, map<string, list<float>>> | metric_id → window_id → values |
| thresholds | map<string, list<float>> | metric_id → candidate thresholds |
| excess_mass_z_threshold | float | z-score threshold (default: 1.645) |
| dip_test_p_threshold | float | p-value threshold (default: 0.05) |
| dip_test_bootstrap_samples | integer | Bootstrap iterations (default: 1000) |
| min_sample_size | integer | Minimum observations per window (default: 20) |

---

## 17. Detector Output Contracts

### 17.1 Purpose

The Detector Output Contract specifies exactly what each detector produces. This is the contract between the detector and the scoring/explanation engines.

### 17.2 Common Output

All detectors produce:

| Field | Type | Description |
|-------|------|-------------|
| detector_id | string | Detector identifier |
| detector_version | string | Detector version |
| status | string | "completed", "skipped", "error", "partial" |
| execution_time_ms | integer | Execution time in milliseconds |
| warnings | list<string> | Warnings generated during execution |

### 17.3 D-01 Output Contract

| Field | Type | Description |
|-------|------|-------------|
| drift_detected | boolean | Whether any drift was detected |
| drift_magnitude | float | Average normalized KS statistic [0, 1] |
| metrics_analyzed | list<string> | Metrics that were analyzed |
| drift_events | list<DriftEvent> | Individual drift events |
| ks_statistics | map<string, float> | KS statistic per (metric, window_pair) |
| psi_values | map<string, float> | PSI value per (metric, window_pair) |
| drift_directions | map<string, string> | Direction per (metric, window_pair) |
| window_pairs_analyzed | list<tuple<string, string>> | Pairs that were analyzed |

#### DriftEvent

| Field | Type | Description |
|-------|------|-------------|
| metric | string | Metric where drift was detected |
| window_pair | tuple<string, string> | Window pair (start, end) |
| ks_statistic | float | KS test statistic |
| ks_p_value | float | KS test p-value |
| psi_value | float | PSI value |
| direction | string | "mean_shift", "variance_collapse", "shape_change" |
| sample_sizes | tuple<int, int> | Sample sizes for the two windows |

### 17.4 D-02 Output Contract

| Field | Type | Description |
|-------|------|-------------|
| breakdown_detected | boolean | Whether any breakdown was detected |
| breakdown_type | string | Highest-priority breakdown type |
| metric_pairs_analyzed | list<string> | Pairs that were analyzed |
| breakdown_events | list<BreakdownEvent> | Individual breakdown events |
| pearson_trajectories | map<string, list<optional<float>>> | Pearson r per window per pair |
| spearman_trajectories | map<string, list<optional<float>>> | Spearman rho per window per pair |
| confidence_intervals | map<string, tuple<float, float>> | Fisher-z CI per (pair, window) |
| window_pairs_flagged | list<tuple<string, string>> | Pairs with breakdowns |

#### BreakdownEvent

| Field | Type | Description |
|-------|------|-------------|
| metric_pair | tuple<string, string> | Metric pair where breakdown occurred |
| breakdown_type | string | Type of breakdown |
| window_pair | tuple<string, string> | Window pair |
| delta_pearson | float | Change in Pearson r (for sudden_drop) |
| pearson_values | tuple<float, float> | Pearson r values (for sign_reversal) |
| slope | float | Regression slope (for gradual_erosion) |
| confidence_intervals | tuple<tuple, tuple> | CIs (for confidence_exclusion) |

### 17.5 D-03 Output Contract

| Field | Type | Description |
|-------|------|-------------|
| compression_detected | boolean | Whether compression was detected |
| compression_index | float | Average compression index across events |
| metrics_analyzed | list<string> | Metrics analyzed |
| compression_events | list<CompressionEvent> | Individual compression events |
| thresholds_used | map<string, list<float>> | Thresholds per metric |
| excess_mass_z_scores | map<string, float> | z-score per (metric, threshold, window) |
| dip_test_statistics | map<string, float> | Dip statistic per (metric, threshold, window) |
| dip_test_p_values | map<string, float> | Dip p-value per (metric, threshold, window) |
| windows_analyzed | list<string> | Windows that were analyzed |

#### CompressionEvent

| Field | Type | Description |
|-------|------|-------------|
| metric | string | Metric with compression |
| threshold | float | Threshold where compression detected |
| window | string | Window ID |
| compression_index | float | Proportion of values in band (p_hat) |
| excess_mass_z_score | float | Excess Mass z-score |
| dip_test_statistic | float | Dip test statistic |
| dip_test_p_value | float | Dip test p-value |
| epsilon | float | Band width |
| sample_size | integer | Number of observations |
| hypothesized_cause | string | Rule-based cause inference |

---

## 18. Evidence Contracts

### 18.1 Purpose

Evidence Contracts define what evidence each detector produces for the Evidence Engine. Evidence is the raw data that supports detector findings.

### 18.2 Evidence Types

| Type | Description | Generated By |
|------|-------------|-------------|
| Distribution comparison | Before/after distributions | D-01 |
| Correlation trajectory | Correlation over time | D-02 |
| Threshold proximity | Value clustering around thresholds | D-03 |
| Sample size metadata | How many observations supported each finding | All |
| Statistical metadata | Test parameters, p-values, effect sizes | All |

### 18.3 D-01 Evidence

| Evidence Field | Type | Description |
|---------------|------|-------------|
| window_pair | tuple<string, string> | Windows compared |
| metric | string | Metric analyzed |
| distribution_before | list<float> | Values in earlier window |
| distribution_after | list<float> | Values in later window |
| ks_statistic | float | Test statistic |
| ks_p_value | float | Significance |
| psi_value | float | Population stability |
| direction | string | Drift direction |
| sample_sizes | tuple<int, int> | Sample sizes |

### 18.4 D-02 Evidence

| Evidence Field | Type | Description |
|---------------|------|-------------|
| metric_pair | tuple<string, string> | Metrics correlated |
| pearson_r | float | Pearson correlation per window |
| spearman_rho | float | Spearman correlation per window |
| fisher_z_ci | tuple<float, float> | 95% CI for Pearson r |
| trajectory | list<optional<float>> | Correlation over all windows |
| breakdown_type | string | Type of breakdown detected |
| window_pair | tuple<string, string> | Windows where breakdown occurred |

### 18.5 D-03 Evidence

| Evidence Field | Type | Description |
|---------------|------|-------------|
| metric | string | Metric analyzed |
| threshold | float | Candidate threshold |
| window | string | Window ID |
| excess_mass_z | float | Excess Mass z-score |
| dip_statistic | float | Dip test statistic |
| dip_p_value | float | Dip test p-value |
| compression_index | float | Proportion in band |
| epsilon | float | Band width |
| values | list<float> | Observation values |
| hypothesized_cause | string | Inferred cause |

---

## 19. Confidence Contracts

### 19.1 Purpose

Confidence Contracts define how detectors estimate confidence in their results. Confidence reflects the reliability of the detection, not the severity of the finding.

### 19.2 Confidence Factors

| Factor | Description | Range |
|--------|-------------|-------|
| Sample size | More observations → higher confidence | [0, 1] |
| Effect size | Larger effect → higher confidence | [0, 1] |
| Statistical significance | Lower p-value → higher confidence | [0, 1] |
| Consistency | Same finding across windows → higher confidence | [0, 1] |

### 19.3 D-01 Confidence

```
CONFIDENCE_D01 = f_sample_size * f_effect_size * f_significance

WHERE:
  f_sample_size = min(1.0, min(n_before, n_after) / 30)
  f_effect_size = min(1.0, ks_statistic / 0.5)
  f_significance = 1.0 - ks_p_value
```

### 19.4 D-02 Confidence

```
CONFIDENCE_D02 = f_sample_size * f_effect_size * f_consistency

WHERE:
  f_sample_size = min(1.0, n_paired / 30)
  f_effect_size = min(1.0, abs(delta_r) / 0.5)
  f_consistency = count(windows with same breakdown_type) / total_windows
```

### 19.5 D-03 Confidence

```
CONFIDENCE_D03 = f_sample_size * f_effect_size * f_significance

WHERE:
  f_sample_size = min(1.0, n / 50)
  f_effect_size = min(1.0, compression_index)
  f_significance = 1.0 - dip_p_value
```

---

## 20. Execution Environment

### 20.1 Runtime Requirements

| Requirement | Value |
|-------------|-------|
| Python version | ≥ 3.10, < 3.13 |
| NumPy version | ≥ 1.26.0 |
| SciPy version | ≥ 1.12.0 |
| Memory | ≤ 100MB for 10,000 observations |
| CPU | Single-threaded (GIL-bound) |
| Disk | No disk I/O during execution |

### 20.2 Seed Management

| Property | Value |
|----------|-------|
| Default seed | 42 |
| Seed source | Config object |
| Seed propagation | Passed to all random operations |
| Seed recording | Recorded in provenance |
| Seed determinism | Same seed → same results always |

### 20.3 Floating-Point Precision

| Property | Value |
|----------|-------|
| Precision | IEEE 754 double (64-bit) |
| NaN handling | Replace with 0.0, flag as quality="estimated" |
| Inf handling | Replace with bounded value, flag as quality="estimated" |
| Epsilon | 1e-10 (for division-by-zero avoidance) |
| Rounding | Not applied; full precision preserved |

---

## 21. D-01 Execution Specification

### 21.1 Purpose

D-01 detects distributional drift — significant changes in the distribution of metric values between consecutive windows.

### 21.2 Responsibilities

| Responsibility | Description |
|---------------|-------------|
| Distribution comparison | Compare value distributions between consecutive windows |
| KS testing | Compute Kolmogorov-Smirnov two-sample test |
| PSI computation | Compute Population Stability Index |
| Drift direction | Classify drift as mean_shift, variance_collapse, or shape_change |
| Evidence generation | Produce drift evidence for each detected event |

### 21.3 Inputs

| Input | Type | Source |
|-------|------|--------|
| distributions | map<metric_id, map<window_id, list<float>>> | Adapter via context |
| window_pairs | list<tuple<window_id, window_id>> | Window resolver |
| ks_p_value_threshold | float | Config (default: 0.05) |
| psi_threshold | float | Config (default: 0.25) |
| min_sample_size | integer | Config (default: 10) |

### 21.4 Outputs

| Output | Type | Description |
|--------|------|-------------|
| DetectorResult | DetectorResult | Standard detector output |
| drift_events | list<DriftEvent> | Individual drift events |
| ks_statistics | map<string, float> | KS statistic per pair |
| psi_values | map<string, float> | PSI per pair |
| drift_directions | map<string, string> | Direction per pair |

### 21.5 Observation Dependencies

| Dependency | Description |
|-----------|-------------|
| Complete observations only | Missing-quality observations excluded |
| At least 2 windows | Need pairs for comparison |
| At least 10 observations per window | KS test power requirement |

### 21.6 Window Dependencies

| Dependency | Description |
|-----------|-------------|
| Consecutive pairs | Windows compared in order (w00→w01, w01→w02, ...) |
| Non-overlapping | Windows must not overlap |
| Sorted | Windows sorted by window_id |

### 21.7 Evidence Produced

| Evidence | Description |
|----------|-------------|
| Distribution comparison | Before/after value distributions |
| KS test results | Statistic and p-value |
| PSI values | Population stability |
| Drift direction | Mean shift, variance collapse, or shape change |
| Sample sizes | How many observations supported each comparison |

### 21.8 Statistical Preconditions

| Precondition | Requirement | Consequence |
|--------------|-------------|-------------|
| Sample size | ≥ 10 per window | Skip window pair if insufficient |
| Window count | ≥ 2 | Skip if fewer than 2 windows |
| Value variance | At least some variation | KS test may produce 0.0 statistic |

### 21.9 Execution Steps

```
D-01 EXECUTION ALGORITHM:

1. FOR each metric in metrics_analyzed:
2.   FOR each consecutive window pair (w_i, w_{i+1}):
3.     vals_before ← distributions[metric][w_i]
4.     vals_after ← distributions[metric][w_{i+1}]
5.     
6.     # Sample size gate
7.     IF len(vals_before) < min_sample_size OR len(vals_after) < min_sample_size:
8.       SKIP (record in warnings)
9.       CONTINUE
10.    
11.    # KS test
12.    ks_stat, ks_p ← ks_2samp(vals_before, vals_after)
13.    ks_statistics[(metric, w_i, w_{i+1})] ← ks_stat
14.    
15.    # PSI computation
16.    psi ← compute_psi(vals_before, vals_after)
17.    psi_values[(metric, w_i, w_{i+1})] ← psi
18.    
19.    # Drift detection
20.    drift_detected ← (ks_p < ks_p_value_threshold) OR (psi > psi_threshold)
21.    
22.    IF drift_detected:
23.      direction ← classify_drift_direction(vals_before, vals_after, ks_stat, psi)
24.      drift_events.append(DriftEvent(...))
25.      drift_directions[(metric, w_i, w_{i+1})] ← direction
26.    
27. # Aggregate results
28. drift_magnitude ← mean(normalized_ks_statistics)
29. RETURN DetectorResult(...)
```

### 21.10 Failure Modes

| Failure Mode | Cause | Recovery |
|-------------|-------|----------|
| All windows skipped | Insufficient sample size in all windows | Report drift_detected=False, empty events |
| NaN in KS statistic | All values identical | KS statistic = 0.0, p-value = 1.0 |
| Division by zero in PSI | All values identical | PSI = 0.0 |
| Empty distribution | No observations for metric | Skip metric, record warning |

### 21.11 Recovery Behavior

| Scenario | Behavior |
|----------|----------|
| Partial failure | Continue with remaining metrics and window pairs |
| Complete failure | Return empty result with status="error" |
| NaN propagation | Replace NaN with 0.0, flag in warnings |

### 21.12 Computational Complexity

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|-----------------|
| KS test per pair | O(n log n) | O(n) |
| PSI per pair | O(n) | O(n) |
| Drift direction | O(n) | O(1) |
| Total per metric | O(K × n log n) | O(n) |
| Total D-01 | O(M × K × n log n) | O(M × n) |

Where M = number of metrics, K = number of window pairs, n = observations per window.

### 21.13 Memory Complexity

| Component | Memory |
|-----------|--------|
| Distribution storage | O(M × K × n) |
| KS statistics | O(M × K) |
| PSI values | O(M × K) |
| Drift events | O(M × K) worst case |
| **Total** | **O(M × K × n)** |

---

## 22. D-02 Execution Specification

### 22.1 Purpose

D-02 detects correlation breakdown — significant changes in correlation between metric pairs across windows.

### 22.2 Responsibilities

| Responsibility | Description |
|---------------|-------------|
| Paired observation alignment | Align observations by source_id across metrics |
| Pearson correlation | Compute Pearson r per window per metric pair |
| Spearman correlation | Compute Spearman rho per window per metric pair |
| Fisher z-transform | Compute 95% CI for Pearson r |
| Breakdown detection | Detect sudden_drop, sign_reversal, gradual_erosion, confidence_exclusion |
| Evidence generation | Produce breakdown evidence |

### 22.3 Inputs

| Input | Type | Source |
|-------|------|--------|
| paired_trajectories | map<pair_key, list<tuple<list<float>, list<float>>>> | Adapter via context |
| metric_pairs | list<tuple<string, string>> | All combinations of metrics |
| window_ids | list<string> | Ordered window IDs |
| sudden_drop_threshold | float | Config (default: 0.3) |
| sign_reversal_min_correlation | float | Config (default: 0.2) |
| gradual_erosion_slope_threshold | float | Config (default: -0.1) |
| min_paired_observations | integer | Config (default: 10) |

### 22.4 Outputs

| Output | Type | Description |
|--------|------|-------------|
| DetectorResult | DetectorResult | Standard detector output |
| breakdown_detected | boolean | Whether any breakdown detected |
| breakdown_type | string | Highest-priority type |
| breakdown_events | list<BreakdownEvent> | Individual events |
| pearson_trajectories | map<string, list<optional<float>>> | Pearson r per window |
| spearman_trajectories | map<string, list<optional<float>>> | Spearman rho per window |
| confidence_intervals | map<string, tuple<float, float>> | Fisher-z CI |

### 22.5 Observation Dependencies

| Dependency | Description |
|-----------|-------------|
| Paired observations | Observations with same source_id for both metrics |
| At least 10 paired observations | Correlation requires sufficient pairs |
| At least 2 metrics | Need pairs to compute correlation |

### 22.6 Window Dependencies

| Dependency | Description |
|-----------|-------------|
| All windows analyzed | Correlation computed for each window |
| Chronological order | Breakdown detection requires ordered windows |
| Minimum 2 windows | Need at least 2 for comparison |
| Minimum 4 windows | Required for gradual_erosion detection |

### 22.7 Evidence Produced

| Evidence | Description |
|----------|-------------|
| Pearson trajectory | Correlation over time |
| Spearman trajectory | Rank correlation over time |
| Fisher-z CI | Confidence interval for each correlation |
| Breakdown events | What broke, when, how |
| Alignment metadata | How many observations were paired |

### 22.8 Statistical Preconditions

| Precondition | Requirement | Consequence |
|--------------|-------------|-------------|
| Paired observations | ≥ 10 per window | Skip window if insufficient |
| Metric count | ≥ 2 metrics | Skip if fewer than 2 metrics |
| Window count | ≥ 2 | Need pairs for comparison |
| Gradual erosion | ≥ 4 windows | Cannot detect gradual erosion |

### 22.9 Execution Steps

```
D-02 EXECUTION ALGORITHM:

1. FOR each metric pair (metric_i, metric_j):
2.   pearson_values ← []
3.   spearman_values ← []
4.   
5.   FOR each window_id in window_ids:
6.     paired_i, paired_j ← paired_trajectories[pair_key][window_index]
7.     
8.     n ← min(len(paired_i), len(paired_j))
9.     IF n < min_paired_observations:
10.      pearson_values.append(None)
11.      spearman_values.append(None)
12.      CONTINUE
13.    
14.    # Pearson correlation
15.    pearson_r ← corrcoef(paired_i[:n], paired_j[:n])[0,1]
16.    pearson_values.append(pearson_r)
17.    
18.    # Spearman rank correlation
19.    x_ranked ← rankdata(paired_i[:n], method="average")
20.    y_ranked ← rankdata(paired_j[:n], method="average")
21.    spearman_rho ← corrcoef(x_ranked, y_ranked)[0,1]
22.    spearman_values.append(spearman_rho)
23.    
24.    # Fisher z-transform CI
25.    z ← 0.5 * ln((1 + pearson_r) / (1 - pearson_r + ε))
26.    se ← 1 / sqrt(n - 3)
27.    ci ← (tanh(z - 1.96*se), tanh(z + 1.96*se))
28.    confidence_intervals[(pair_key, window_id)] ← ci
29.  
30.  # Detect breakdowns
31.  pair_breakdowns ← detect_breakdowns(metric_i, metric_j, window_ids, pearson_values, ...)
32.  breakdown_events.extend(pair_breakdowns)
33.  
34.  pearson_trajectories[pair_key] ← pearson_values
35.  spearman_trajectories[pair_key] ← spearman_values
36.
37. # Determine highest-priority breakdown type
38. breakdown_type ← min(types, key=priority)
39. RETURN DetectorResult(...)
```

### 22.10 Breakdown Detection Algorithm

```
BREAKDOWN DETECTION:

FOR each metric pair:

  # Type 1: Sudden drop
  FOR k in range(K-1):
    IF pearson[k] != None AND pearson[k+1] != None:
      delta ← abs(pearson[k+1] - pearson[k])
      IF delta > sudden_drop_threshold:
        RECORD breakdown_type="sudden_drop"

  # Type 2: Sign reversal
  FOR k in range(K-1):
    IF pearson[k] != None AND pearson[k+1] != None:
      IF sign(pearson[k]) != sign(pearson[k+1])
         AND abs(pearson[k]) > sign_reversal_min_correlation
         AND abs(pearson[k+1]) > sign_reversal_min_correlation:
        RECORD breakdown_type="sign_reversal"

  # Type 3: Gradual erosion (requires K >= 4)
  IF K >= 4:
    IF pearson[0] > 0.3 AND pearson[-1] < 0.1:
      slope ← linear_regression_slope(pearson_values)
      IF slope < gradual_erosion_slope_threshold:
        RECORD breakdown_type="gradual_erosion"

  # Type 4: Confidence interval exclusion
  FOR k in range(K-1):
    IF ci[k] AND ci[k+1] NOT OVERLAP:
      RECORD breakdown_type="confidence_exclusion"

PRIORITY: sign_reversal > sudden_drop > gradual_erosion > confidence_exclusion
```

### 22.11 Failure Modes

| Failure Mode | Cause | Recovery |
|-------------|-------|----------|
| All pairs skipped | Insufficient paired observations | Report breakdown_detected=False |
| NaN in Pearson | All values identical | Pearson = 0.0, skip CI |
| Division by zero in Fisher z | Pearson = ±1.0 | Replace with ε offset |
| Empty trajectory | No valid windows for pair | Skip pair, record warning |

### 22.12 Recovery Behavior

| Scenario | Behavior |
|----------|----------|
| Partial failure | Continue with remaining pairs |
| Complete failure | Return empty result with status="error" |
| NaN propagation | Replace NaN with 0.0, flag in warnings |

### 22.13 Computational Complexity

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|-----------------|
| Pearson per window | O(n) | O(n) |
| Spearman per window | O(n log n) | O(n) |
| Fisher z CI | O(1) | O(1) |
| Breakdown detection | O(K) | O(K) |
| Total per pair | O(K × n log n) | O(K × n) |
| Total D-02 | O(P × K × n log n) | O(P × K × n) |

Where P = number of metric pairs = M×(M-1)/2, K = number of windows, n = observations per window.

### 22.14 Memory Complexity

| Component | Memory |
|-----------|--------|
| Paired trajectories | O(P × K × n) |
| Pearson values | O(P × K) |
| Spearman values | O(P × K) |
| Confidence intervals | O(P × K) |
| Breakdown events | O(P × K) worst case |
| **Total** | **O(P × K × n)** |

---

## 23. D-03 Execution Specification

### 23.1 Purpose

D-03 detects threshold compression — artificial clustering of values around specific thresholds, suggesting gaming or manipulation.

### 23.2 Responsibilities

| Responsibility | Description |
|---------------|-------------|
| Threshold discovery | Auto-discover candidate thresholds from data |
| Excess Mass test | Test for excess observations near thresholds |
| Dip test | Test for multimodality (supporting evidence) |
| Compression index | Compute proportion of values in threshold band |
| Cause inference | Rule-based inference of hypothesized cause |
| Evidence generation | Produce compression evidence |

### 23.3 Inputs

| Input | Type | Source |
|-------|------|--------|
| distributions | map<metric_id, map<window_id, list<float>>> | Adapter via context |
| thresholds | map<metric_id, list<float>> | Auto-threshold detection |
| excess_mass_z_threshold | float | Config (default: 1.645) |
| dip_test_p_threshold | float | Config (default: 0.05) |
| dip_test_bootstrap_samples | integer | Config (default: 1000) |
| min_sample_size | integer | Config (default: 20) |

### 23.4 Outputs

| Output | Type | Description |
|--------|------|-------------|
| DetectorResult | DetectorResult | Standard detector output |
| compression_detected | boolean | Whether compression detected |
| compression_index | float | Average compression index |
| compression_events | list<CompressionEvent> | Individual events |
| thresholds_used | map<string, list<float>> | Thresholds per metric |
| excess_mass_z_scores | map<string, float> | z-scores |
| dip_test_statistics | map<string, float> | Dip statistics |
| dip_test_p_values | map<string, float> | Dip p-values |

### 23.5 Observation Dependencies

| Dependency | Description |
|-----------|-------------|
| Complete observations only | Missing-quality observations excluded |
| At least 20 observations | Excess Mass test requires sufficient data |
| At least 1 metric | Need values to test |

### 23.6 Window Dependencies

| Dependency | Description |
|-----------|-------------|
| Each window analyzed independently | No cross-window comparison needed |
| At least 1 window | Need at least one window |

### 23.7 Evidence Produced

| Evidence | Description |
|----------|-------------|
| Excess Mass z-score | How much excess near threshold |
| Dip test statistic | Multimodality evidence |
| Compression index | Proportion in band |
| Threshold band | Band definition (T-ε, T+ε) |
| Cause inference | Hypothesized cause |

### 23.8 Statistical Preconditions

| Precondition | Requirement | Consequence |
|--------------|-------------|-------------|
| Sample size | ≥ 20 per window | Skip window if insufficient |
| Value range | > 0 | Cannot test if all values identical |
| Thresholds | At least 1 candidate | Skip metric if no thresholds |

### 23.9 Execution Steps

```
D-03 EXECUTION ALGORITHM:

1. FOR each metric in metrics_analyzed:
2.   thresholds ← auto_threshold_detection(distributions[metric])
3.   
4.   FOR each threshold in thresholds:
5.     FOR each window_id in window_ids:
6.       vals ← distributions[metric][window_id]
7.       
8.       # Sample size gate
9.       IF len(vals) < min_sample_size:
10.        SKIP
11.        CONTINUE
12.      
13.      # Excess Mass test
14.      epsilon ← max(0.02 × |threshold|, 0.01 × (max(vals) - min(vals)))
15.      p0 ← 2×epsilon / (max(vals) - min(vals))
16.      p ← count(|v - threshold| <= epsilon) / n
17.      z ← (p - p0) / sqrt(p0×(1-p0)/n)
18.      
19.      # Dip test
20.      dip_stat, dip_p ← dip_test(vals, bootstrap_samples, seed)
21.      
22.      # Compression detection
23.      excess_mass_flag ← z > excess_mass_z_threshold
24.      multimodal_flag ← dip_p < dip_test_p_threshold
25.      
26.      IF excess_mass_flag AND (multimodal_flag OR p > 0.5):
27.        cause ← infer_cause(metric, threshold)
28.        compression_events.append(CompressionEvent(...))
29.      
30.      excess_mass_z_scores[(metric, threshold, window_id)] ← z
31.      dip_test_statistics[(metric, threshold, window_id)] ← dip_stat
32.      dip_test_p_values[(metric, threshold, window_id)] ← dip_p
33.  
34. # Aggregate results
35. compression_index ← mean(compression_indices)
36. RETURN DetectorResult(...)
```

### 23.10 Auto-Threshold Detection

```
AUTO-THRESHOLD DETECTION:

1. all_vals ← union of all values across windows for this metric
2. min_val ← min(all_vals)
3. max_val ← max(all_vals)
4. auto_thresholds ← {}

5. # Candidate thresholds (round numbers in range)
6. FOR T IN [1, 5, 10, 20, 25, 50, 75, 80, 90, 95, 100, 1000]:
7.   IF min_val <= T <= max_val:
8.     auto_thresholds.add(T)

9. # Percentile-based thresholds (round to nearest 0.5)
10. FOR percentile IN [10, 25, 50, 75, 90]:
11.   T ← percentile(all_vals, percentile)
12.   T_rounded ← round(T, 1)
13.   IF T_rounded is round (last digit 0 or 5):
14.     auto_thresholds.add(T_rounded)

15. RETURN sorted(auto_thresholds)
```

### 23.11 Failure Modes

| Failure Mode | Cause | Recovery |
|-------------|-------|----------|
| All windows skipped | Insufficient sample size | Report compression_detected=False |
| No thresholds | All values identical | Skip metric, record warning |
| Division by zero | val_range = 0 | Skip threshold, record warning |
| NaN in z-score | p0 = 0 or 1 | Return z = 0.0 |
| Bootstrap failure | Insufficient data | Return dip_p = 1.0 |

### 23.12 Recovery Behavior

| Scenario | Behavior |
|----------|----------|
| Partial failure | Continue with remaining metrics and thresholds |
| Complete failure | Return empty result with status="error" |
| NaN propagation | Replace NaN with 0.0, flag in warnings |

### 23.13 Computational Complexity

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|-----------------|
| Auto-threshold | O(n) | O(n) |
| Excess Mass per (threshold, window) | O(n) | O(n) |
| Dip test per (threshold, window) | O(n × B) | O(n) |
| Compression detection | O(1) | O(1) |
| Total per metric | O(T × W × n × B) | O(n) |
| Total D-03 | O(M × T × W × n × B) | O(M × n) |

Where M = metrics, T = thresholds per metric, W = windows, n = observations, B = bootstrap samples.

### 23.14 Memory Complexity

| Component | Memory |
|-----------|--------|
| Distribution storage | O(M × W × n) |
| Threshold storage | O(M × T) |
| z-scores | O(M × T × W) |
| Dip statistics | O(M × T × W) |
| Compression events | O(M × T × W) worst case |
| Bootstrap samples | O(n × B) temporary |
| **Total** | **O(M × T × W + n × B)** |

---

## 24. Cross-Detector Coordination

### 24.1 Purpose

Cross-Detector Coordination defines how detectors share information and how the dispatcher orchestrates multi-detector execution.

### 24.2 Isolation Model

| Property | Description |
|----------|-------------|
| Data isolation | Each detector receives only its required data |
| Execution isolation | One detector's failure does not affect others |
| State isolation | Detectors share no mutable state |
| Result independence | Detector results are collected independently |

### 24.3 Shared Context

| Shared Resource | Access | Mutability |
|----------------|--------|-----------|
| ObservationCollection | Read-only | Immutable |
| Config | Read-only | Immutable |
| Seed | Read-only | Immutable |
| Provenance | Read-only | Immutable |

### 24.4 Execution Order

| Order | Detector | Rationale |
|-------|----------|-----------|
| 1 | D-01 | Analyzes individual metrics; no cross-metric dependency |
| 2 | D-02 | Analyzes metric pairs; can use D-01's observations |
| 3 | D-03 | Analyzes individual metrics; can use D-01's observations |

The execution order is fixed and does not change. D-01 executes first because it analyzes individual metric distributions. D-02 executes second because it analyzes cross-metric correlations. D-03 executes last because it analyzes threshold patterns.

### 24.5 Result Aggregation

```
RESULT AGGREGATION:

1. detector_results ← {}
2. FOR each detector in execution_order:
3.   result ← detector.execute(context)
4.   detector_results[detector.detector_id] ← result
5. 
6. # Package results
7. RETURN DetectorResults(detector_outputs=detector_results)
```

---

## 25. Shared Utilities

### 25.1 Purpose

Shared Utilities provide common statistical functions used by multiple detectors. These functions are deterministic, well-tested, and documented.

### 25.2 Utility Functions

| Function | Used By | Description |
|----------|---------|-------------|
| ks_2samp | D-01 | Kolmogorov-Smirnov two-sample test |
| compute_psi | D-01 | Population Stability Index |
| corrcoef | D-02 | Pearson correlation coefficient |
| rankdata | D-02 | Rank data for Spearman correlation |
| fisher_z | D-02 | Fisher z-transform |
| fisher_z_inverse | D-02 | Inverse Fisher z-transform |
| excess_mass_test | D-03 | Excess Mass z-test |
| dip_test | D-03 | Dip test (KS approximation) |
| auto_threshold | D-03 | Auto-threshold detection |

### 25.3 Determinism Guarantees

| Function | Determinism Mechanism |
|----------|----------------------|
| ks_2samp | Sorted iteration, unique values |
| compute_psi | Fixed bin count (10), sorted data |
| corrcoef | Deterministic matrix operations |
| rankdata | Average ranking method (deterministic ties) |
| fisher_z | Direct formula, ε offset for edge cases |
| dip_test | Seed-controlled bootstrap |
| auto_threshold | Deterministic percentile computation |

---

## 26. Performance Targets

### 26.1 Latency Targets

| Detector | Target Latency | Measurement |
|----------|---------------|-------------|
| D-01 | < 500ms for 1000 obs/metric × 10 windows | Time to complete all metrics |
| D-02 | < 2s for 7 metrics × 10 windows | Time to complete all pairs |
| D-03 | < 5s for 1000 obs/metric × 10 windows × 10 thresholds | Time to complete all metrics |
| Dispatcher | < 100ms overhead | Time for dispatch logic only |

### 26.2 Throughput Targets

| Metric | Target |
|--------|--------|
| Observations per second | > 10,000 |
| D-01 observations/second | > 5,000 |
| D-02 paired observations/second | > 2,000 |
| D-03 observations/second | > 1,000 (including bootstrap) |

### 26.3 Memory Targets

| Metric | Target |
|--------|--------|
| Peak memory (10000 obs) | < 100MB |
| D-01 working memory | < 50MB |
| D-02 working memory | < 80MB |
| D-03 working memory | < 60MB |

---

## 27. Complexity Analysis

### 27.1 Summary Table

| Detector | Time | Space | Bottleneck |
|----------|------|-------|-----------|
| D-01 | O(M × K × n log n) | O(M × K × n) | KS test sorting |
| D-02 | O(P × K × n log n) | O(P × K × n) | Metric pair count |
| D-03 | O(M × T × W × n × B) | O(M × T × W + n × B) | Bootstrap loop |

### 27.2 Scaling Analysis

| Factor | D-01 Impact | D-02 Impact | D-03 Impact |
|--------|-------------|-------------|-------------|
| Double observations (n) | 2× time | 2× time | 2× time |
| Double windows (K) | 2× time | 2× time | 2× time |
| Double metrics (M) | 2× time | 4× time (pairs) | 2× time |
| Double thresholds (T) | N/A | N/A | 2× time |
| Double bootstrap (B) | N/A | N/A | 2× time |

### 27.3 Bottleneck Analysis

| Bottleneck | Detector | Mitigation |
|-----------|----------|------------|
| KS test sorting | D-01 | Pre-sort once, reuse |
| Metric pair count | D-02 | Limit to supported pairs |
| Bootstrap loop | D-03 | Vectorized operations |
| Fisher z edge cases | D-02 | ε offset, clamp values |

---

## 28. Parallel Execution Strategy

### 28.1 Current Constraints

| Constraint | Description |
|-----------|-------------|
| Python GIL | True parallelism limited for CPU-bound work |
| Sequential detectors | D-01 → D-02 → D-03 execution order |
| Shared collection | Read-only, but cannot be modified during execution |

### 28.2 Parallelism Opportunities

| Opportunity | Description | Benefit |
|------------|-------------|---------|
| Metric-level parallelism | D-01 processes metrics independently | 2-4× speedup with thread pool |
| Pair-level parallelism | D-02 processes pairs independently | 2-4× speedup with thread pool |
| Window-level parallelism | D-03 processes windows independently | 2-4× speedup with thread pool |
| Detector parallelism | D-01, D-02, D-03 are independent | Limited by GIL; may not help |

### 28.3 Thread Safety

| Component | Thread Safety | Mechanism |
|-----------|--------------|-----------|
| ObservationCollection | Read-only | Immutable during detection |
| Detector results | Independent writes | Separate result objects per thread |
| Shared utilities | Stateless functions | No mutable state |
| Random number generator | Per-thread instance | Seed-controlled, independent RNG |

---

## 29. Caching Strategy

### 29.1 Cache Points

| Cache Point | What | When | Invalidation |
|------------|------|------|-------------|
| Distribution query | metric values per window | First query | Never (immutable) |
| Paired query | aligned observations | First query | Never (immutable) |
| KS statistic | KS result per pair | Computation | Never (deterministic) |
| Fisher z CI | CI per (pair, window) | Computation | Never (deterministic) |

### 29.2 Cache Policy

| Policy | Description |
|--------|-------------|
| Write-once | Cache is written once, never updated |
| No eviction | Cache lives for the duration of detection |
| Thread-safe | Cache is read-only after write |
| Deterministic | Same input always produces same cache entry |

---

## 30. Failure Handling

### 30.1 Error Taxonomy

| Error Code | Description | Severity | Recovery |
|-----------|-------------|----------|----------|
| DET-001 | Invalid detector ID | Critical | Skip detector |
| DET-002 | Input validation failed | Warning | Skip detector |
| DET-003 | Statistical test failed | Warning | Skip window/pair |
| DET-004 | NaN in result | Warning | Replace with 0.0 |
| DET-005 | Division by zero | Warning | Use ε offset |
| DET-006 | Memory limit exceeded | Critical | Abort detector |
| DET-007 | Timeout exceeded | Critical | Abort detector |
| DET-008 | Invalid configuration | Critical | Skip detector |

### 30.2 Error Handling Rules

| Rule | Description |
|------|-------------|
| R-1 | Per-detector errors do not affect other detectors |
| R-2 | Per-window errors do not affect other windows |
| R-3 | Per-metric errors do not affect other metrics |
| R-4 | NaN values are replaced with 0.0 and flagged |
| R-5 | Division by zero uses ε offset |
| R-6 | All errors are recorded in dispatch summary |
| R-7 | Partial results are returned when possible |

### 30.3 Error Propagation

```
ERROR PROPAGATION:

1. TRY:
2.   result ← detector.execute(context)
3. CATCH StatisticalTestError:
4.   record_warning(detector_id, "Statistical test failed for window")
5.   result ← partial_result (successful windows only)
6. CATCH MemoryError:
7.   record_error(detector_id, "Memory limit exceeded")
8.   result ← empty_result
9. CATCH TimeoutError:
10.  record_error(detector_id, "Timeout exceeded")
11.  result ← empty_result
12. CATCH Exception AS e:
13.  record_error(detector_id, str(e))
14.  result ← empty_result
15. RETURN result
```

---

## 31. Recovery Strategy

### 31.1 Recovery Levels

| Level | Description | Action |
|-------|-------------|--------|
| Window skip | Single window failed | Continue with next window |
| Metric skip | Single metric failed | Continue with next metric |
| Pair skip | Single pair failed | Continue with next pair |
| Detector skip | Entire detector failed | Continue with next detector |
| Pipeline abort | All detectors failed | Abort pipeline, report error |

### 31.2 Recovery Procedures

| Scenario | Recovery Procedure |
|----------|-------------------|
| D-01 window pair skipped | Record warning, continue with next pair |
| D-02 metric pair skipped | Record warning, continue with next pair |
| D-03 window skipped | Record warning, continue with next window |
| D-01 complete failure | Return drift_detected=False, empty events |
| D-02 complete failure | Return breakdown_detected=False, empty events |
| D-03 complete failure | Return compression_detected=False, empty events |
| All detectors failed | Return empty DetectorResults with error status |

---

## 32. Logging Requirements

### 32.1 Log Levels

| Level | Use |
|-------|-----|
| DEBUG | Detailed execution traces |
| INFO | Detector start, completion, timing |
| WARNING | Sample size warnings, partial results |
| ERROR | Detector failures, statistical errors |
| CRITICAL | Pipeline abort, memory limit |

### 32.2 Required Log Events

| Event | Level | Fields |
|-------|-------|--------|
| detector_start | INFO | detector_id, timestamp |
| detector_complete | INFO | detector_id, duration_ms, status |
| detector_skip | WARNING | detector_id, reason |
| detector_error | ERROR | detector_id, error_message |
| window_skip | WARNING | detector_id, window_id, reason |
| sample_size_warning | WARNING | detector_id, metric_id, window_id, actual_size, required_size |
| statistical_test_error | WARNING | detector_id, test_name, error_message |
| dispatch_complete | INFO | total_detectors, completed, skipped, errors |

---

## 33. Validation Requirements

### 33.1 Input Validation

| Validation | Detector | Rule | Action on Failure |
|-----------|----------|------|-------------------|
| Metric presence | All | At least 1 supported metric | Skip detector |
| Window count | D-01 | ≥ 2 windows | Skip detector |
| Window count | D-02 | ≥ 2 windows | Skip detector |
| Window count | D-03 | ≥ 1 window | Skip detector |
| Sample size | D-01 | ≥ 10 per window | Skip window pair |
| Sample size | D-02 | ≥ 10 paired per window | Skip window |
| Sample size | D-03 | ≥ 20 per window | Skip window |
| Metric count | D-02 | ≥ 2 metrics | Skip detector |
| Thresholds | D-03 | ≥ 1 threshold per metric | Skip metric |

### 33.2 Output Validation

| Validation | Detector | Rule | Action on Failure |
|-----------|----------|------|-------------------|
| Status | All | Must be completed/skipped/error/partial | Reject result |
| Drift events | D-01 | Events must have valid window_pair | Reject event |
| Breakdown events | D-02 | Events must have valid metric_pair | Reject event |
| Compression events | D-03 | Events must have valid threshold | Reject event |
| NaN check | All | No NaN in key statistics | Replace with 0.0 |

---

## 34. Compatibility with v1.0.1

### 34.1 Backward Compatibility

| Aspect | v1.0.1 | v1.5 | Compatible? |
|--------|--------|------|-------------|
| Input format | MetricDataFrame | ObservationWindow | Adapter translates |
| Output format | DetectorResult | DetectorResult | Identical |
| Detector IDs | D-01, D-02, D-03 | D-01, D-02, D-03 | Identical |
| Statistical methods | Same | Same | Identical |
| Thresholds | Same | Same | Identical |
| CLI interface | Same | Same | Identical |
| Exit codes | Same | Same | Identical |

### 34.2 Adapter Layer

The adapter layer translates between Observation-based data and legacy MetricDataFrame format:

| Translation | Direction | Method |
|------------|-----------|--------|
| Observation → MetricDataFrame | Observation → Legacy | to_metric_dataframe() |
| Observation → Paired | Observation → D-02 input | to_paired_observations() |
| MetricDataFrame → Observation | Legacy → Observation | N/A (not needed) |

### 34.3 Test Compatibility

| Test Type | v1.0.1 Count | v1.5 Target | Status |
|-----------|-------------|-------------|--------|
| Unit tests | 667 | 667+ | Pass |
| Integration tests | 63 | 63+ | Pass |
| Regression tests | Full | Full | Pass |
| Benchmark tests | D-01/D-02/D-03 | D-01/D-02/D-03 | Pass |

---

## 35. Migration Strategy

### 35.1 Migration Phases

| Phase | Description | Duration |
|-------|-------------|----------|
| Phase 1 | Implement adapter layer | 1 week |
| Phase 2 | Implement detector context | 1 week |
| Phase 3 | Update dispatcher | 1 week |
| Phase 4 | Validate all tests pass | 1 week |
| Phase 5 | Benchmark validation | 1 week |

### 35.2 Migration Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Adapter translation errors | Medium | High | Comprehensive test suite |
| Performance regression | Low | Medium | Benchmark before/after |
| Statistical result changes | Low | High | Same algorithms, same thresholds |
| Test failures | Medium | High | Fix tests to match new data |

### 35.3 Rollback Plan

| Step | Action |
|------|--------|
| 1 | Disable Observation Engine |
| 2 | Restore v1.0.1 extraction pipeline |
| 3 | Run full test suite |
| 4 | Verify benchmark results |

---

## 36. Future Detector Support

### 36.1 Plugin Detectors

| Property | Description |
|----------|-------------|
| Interface | Implement IDetector protocol |
| Registration | Register via DetectorRegistry |
| Validation | Must pass input validation |
| Execution | Must produce DetectorResult |
| Isolation | Plugin failure does not affect other detectors |

### 36.2 Streaming Detectors

| Property | Description |
|----------|-------------|
| Trigger | v2.0 streaming infrastructure |
| Input | Continuous observation stream |
| Processing | Sliding window analysis |
| Output | Real-time anomaly alerts |
| State | Maintains running statistics |

### 36.3 Hybrid Detectors

| Property | Description |
|----------|-------------|
| Trigger | v1.6 multi-source data |
| Input | Observations from multiple sources |
| Processing | Cross-source correlation |
| Output | Cross-source anomaly detection |
| Complexity | Higher than single-source detectors |

### 36.4 Future Statistical Engines

| Engine | Trigger | Description |
|--------|---------|-------------|
| Bayesian changepoint | v2.0 | Probabilistic changepoint detection |
| ML anomaly detection | v2.0 | Isolation forest, autoencoder |
| Causal inference | v2.0 | Directed dependency analysis |
| Time series forecasting | v2.0 | ARIMA, Prophet integration |

---

## 37. Architectural Invariants

### 37.1 Detector Invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| INV-D1 | Each detector receives only its required data | Adapter filters by detector needs |
| INV-D2 | Detector failure does not affect other detectors | Per-detector try/except |
| INV-D3 | Detectors share no mutable state | Stateless execution |
| INV-D4 | Same observations → same results | Deterministic algorithms, seed control |
| INV-D5 | Detectors produce DetectorResult format | Output validation |
| INV-D6 | Evidence traces to observations | Provenance tracking |

### 37.2 Dispatcher Invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| INV-Disp1 | Dispatcher does not perform detection | Only routing and orchestration |
| INV-Disp2 | Dispatcher does not modify observations | Read-only access |
| INV-Disp3 | All enabled detectors are attempted | Iteration over enabled list |
| INV-Disp4 | Failures are captured, not propagated | Per-detector error handling |

### 37.3 Context Invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| INV-Ctx1 | Context is read-only | No mutation methods |
| INV-Ctx2 | Context is created by dispatcher | Not by detector |
| INV-Ctx3 | Context contains complete execution state | All required fields |

---

## 38. Trade-off Analysis

### 38.1 Architecture Trade-offs

| Decision | Benefit | Cost | Rationale |
|----------|---------|------|-----------|
| Adapter layer | Backward compatibility | Translation overhead | Protects existing test suite |
| Per-detector isolation | Fault tolerance | Slightly more complex | Prevents cascading failures |
| Fixed execution order | Predictability | Less parallelism | Matches data dependencies |
| Seed-controlled | Determinism | Slightly slower | Scientific reproducibility requirement |
| In-memory execution | Performance | Memory bounded | Current scale is manageable |

### 38.2 Statistical Trade-offs

| Decision | Benefit | Cost | Rationale |
|----------|---------|------|-----------|
| KS test (non-parametric) | No distribution assumption | Less powerful than parametric | Metrics have unknown distributions |
| No multiple comparison correction | Simpler interpretation | More false positives | Documented limitation, v2.0 enhancement |
| Bootstrap dip test | Approximate p-value | Not exact | True dip test not available in scipy |
| Fixed thresholds | Deterministic | Not adaptive | Per-repo calibration deferred to v2.0 |

---

## 39. Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|----|------|------------|--------|-----------|
| R-1 | Adapter translation errors break detectors | Medium | High | Comprehensive test suite |
| R-2 | Performance regression with observation data | Low | Medium | Benchmark before/after |
| R-3 | Statistical results change due to more data | Low | High | Same algorithms, same thresholds |
| R-4 | Memory exhaustion with large repos | Low | High | Streaming extraction, bounded memory |
| R-5 | Non-deterministic results | Low | High | Seed control, sorted iteration |
| R-6 | Plugin detectors cause instability | Medium | Medium | Isolation, validation |
| R-7 | Future detectors require new interfaces | Medium | Low | Open-closed principle |
| R-8 | Bootstrap produces different results across platforms | Low | Medium | Same numpy/scipy versions |

---

## 40. Acceptance Criteria

### 40.1 Functional Criteria

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-1 | D-01 executes on all metrics with ≥10 observations per window | Unit test |
| AC-2 | D-02 executes on all metric pairs with ≥10 paired observations | Unit test |
| AC-3 | D-03 executes on all metrics with ≥20 observations per window | Unit test |
| AC-4 | Detector outputs match v1.0.1 format exactly | Integration test |
| AC-5 | All 730 existing tests pass | Full test suite |
| AC-6 | Benchmark results meet or exceed v1.0.1 targets | Benchmark suite |

### 40.2 Performance Criteria

| ID | Criterion | Measurement |
|----|-----------|-------------|
| AC-7 | D-01 latency < 500ms for 1000 obs × 10 windows | Timing test |
| AC-8 | D-02 latency < 2s for 7 metrics × 10 windows | Timing test |
| AC-9 | D-03 latency < 5s for 1000 obs × 10 windows × 10 thresholds | Timing test |
| AC-10 | Peak memory < 100MB for 10000 observations | Memory profiling |

### 40.3 Quality Criteria

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-11 | All detector failures are captured in dispatch summary | Error injection test |
| AC-12 | All warnings are logged with detector_id and context | Log inspection |
| AC-13 | No NaN values in detector output (replaced with 0.0) | Output validation |
| AC-14 | Evidence traces to specific observations | Provenance check |

---

## 41. Future Evolution

### 41.1 v1.6 Planned Extensions

| Feature | Description | Dependencies |
|---------|-------------|-------------|
| M-08: Developer churn | Per-developer behavior tracking | Identity resolution |
| D-04: Developer behavior | Detect anomalous developer patterns | M-08 |
| Auto-threshold calibration | Per-repo threshold calibration | Observation history |
| Bonferroni correction | Multiple comparison correction | None |

### 41.2 v2.0 Planned Capabilities

| Feature | Description | Dependencies |
|---------|-------------|-------------|
| Streaming detectors | Real-time anomaly detection | Streaming infrastructure |
| ML-based detectors | Isolation forest, autoencoder | Training data |
| Bayesian changepoint | Probabilistic changepoint detection | Bayesian framework |
| Cross-repo detectors | Multi-repository analysis | Workspace management |
| Causal inference | Directed dependency analysis | Cross-metric observations |
| Dashboard integration | Interactive detector explorer | Web dashboard |

### 41.3 Deprecation Schedule

| Feature | v1.5 | v1.6 | v2.0 |
|---------|------|------|------|
| Adapter layer | Required | Required | Optional |
| MetricDataFrame input | Supported via adapter | Deprecated | Removed |
| Single-value extraction | Fallback | Removed | N/A |
| In-memory execution | Default | Default | Streaming |

---

## 42. Glossary

| Term | Definition |
|------|-----------|
| Observation | Single data point extracted from one source at one time |
| ObservationCollection | Indexed container of all observations for one repository |
| ObservationWindow | Time-bounded or commit-bounded group of observations |
| Detector | Statistical method that analyzes observations for anomalies |
| Detector Dispatcher | Orchestrator that manages detector execution |
| Detector Context | Per-detector execution state passed by dispatcher |
| Detector Result | Output container for detector findings |
| DriftEvent | D-01 finding: distributional change between windows |
| BreakdownEvent | D-02 finding: correlation change between windows |
| CompressionEvent | D-03 finding: value clustering around threshold |
| Adapter Layer | Translation shim between Observation Engine and detectors |
| MetricDataFrame | v1.0 data container (aggregated values) |
| Sample Size Gate | Minimum observation count required for statistical validity |
| Bootstrap | Resampling technique for estimating p-values |
| Fisher z-transform | Transform for computing confidence intervals for correlation |
| Excess Mass | Test statistic for detecting clustering around thresholds |
| Dip Test | Test for multimodality in a distribution |
| PSI | Population Stability Index for measuring distributional change |
| KS Test | Kolmogorov-Smirnov two-sample test for distributional difference |

---

## 43. Appendix

### A. Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| PRD-v1.5-OE | docs/architecture/observation_engine/PRD_v1.5_Observation_Engine.md | Parent requirement |
| OEAS-v1.5 | docs/architecture/observation_engine/OEAS_v1.5_Observation_Engine.md | Architecture specification |
| ODSS-v1.0 | docs/architecture/observation_engine/ODSS_v1.0_Observation_Data_Schema_Specification.md | Data schema |
| RELEASE_BASELINE | docs/architecture/RELEASE_BASELINE.md | v1.0.1 baseline |
| V1_5_DEVELOPMENT_ENTRY | docs/roadmap/V1_5_DEVELOPMENT_ENTRY.md | Development plan |

### B. Error Code Reference

| Code | Description |
|------|-------------|
| DET-001 | Invalid detector ID |
| DET-002 | Input validation failed |
| DET-003 | Statistical test failed |
| DET-004 | NaN in result |
| DET-005 | Division by zero |
| DET-006 | Memory limit exceeded |
| DET-007 | Timeout exceeded |
| DET-008 | Invalid configuration |

### C. Detector Summary Table

| Detector | Purpose | Input | Output | Min Sample | Statistical Tests |
|----------|---------|-------|--------|-----------|-------------------|
| D-01 | Distributional drift | Distribution per window | Drift events | 10/window | KS, PSI |
| D-02 | Correlation breakdown | Paired observations | Breakdown events | 10 paired/window | Pearson, Spearman, Fisher-z |
| D-03 | Threshold compression | Distribution per window | Compression events | 20/window | Excess Mass, Dip |

### D. Execution Order Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    DETECTOR EXECUTION ORDER                    │
│                                                               │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐             │
│  │   D-01   │────▶│   D-02   │────▶│   D-03   │             │
│  │  Drift   │     │Correlation│     │Threshold │             │
│  │          │     │          │     │          │             │
│  │ Per-metric│     │ Per-pair  │     │ Per-metric│             │
│  │ per-window│     │ per-window│     │ per-window│             │
│  └──────────┘     └──────────┘     └──────────┘             │
│                                                               │
│  Each detector receives its own context from the dispatcher. │
│  Each detector produces DetectorResult independently.        │
│  Failure in one detector does not affect others.             │
└──────────────────────────────────────────────────────────────┘
```

### E. State Machine Diagram

```
                         ┌───────────────┐
                         │   Registered  │
                         └───────┬───────┘
                                 │ init()
                         ┌───────▼───────┐
                         │  Initialized  │
                         └───────┬───────┘
                                 │ validate_input()
                    ┌────────────┼────────────┐
                    │                         │
             ┌──────▼──────┐           ┌──────▼──────┐
             │    Ready    │           │   Skipped   │
             └──────┬──────┘           └─────────────┘
                    │ execute()
             ┌──────▼──────┐
             │  Executing  │
             └──────┬──────┘
                    │
         ┌──────────┼──────────┐
         │          │          │
   ┌─────▼────┐ ┌──▼─────┐ ┌──▼─────┐
   │Completed │ │ Error  │ │Partial │
   └──────────┘ └────────┘ └────────┘
```

---

*End of Document*

---

**Document History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.0.0 | 2026-06-29 | MIIE Engineering | Complete detector execution specification over Observation Engine |

**Approval**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Engineering Lead | | | |
| Science Lead | | | |
| Governance | | | |
