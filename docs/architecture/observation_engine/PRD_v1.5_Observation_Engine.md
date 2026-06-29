# MIIE v1.5 — Observation Engine Product Requirements Document

**Document:** PRD-v1.5-OE
**Version:** 1.0.0
**Date:** 2026-06-29
**Classification:** Internal Engineering Architecture Document
**Baseline:** v1.0.1 (tag `4c4d5e6`)
**Status:** For Implementation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State of MIIE](#2-current-state-of-miie)
3. [Existing Scientific Pipeline](#3-existing-scientific-pipeline)
4. [Current Detector Architecture](#4-current-detector-architecture)
5. [Existing Observation Model](#5-existing-observation-model)
6. [Existing Data Flow](#6-existing-data-flow)
7. [Root Cause Analysis](#7-root-cause-analysis)
8. [Scientific Problem Statement](#8-scientific-problem-statement)
9. [Motivation](#9-motivation)
10. [Research Background](#10-research-background)
11. [Design Goals](#11-design-goals)
12. [Non-Goals](#12-non-goals)
13. [Engineering Principles](#13-engineering-principles)
14. [Scientific Principles](#14-scientific-principles)
15. [Candidate Observation Models](#15-candidate-observation-models)
16. [Comparative Evaluation](#16-comparative-evaluation)
17. [Selected Architecture](#17-selected-architecture)
18. [Observation Engine Overview](#18-observation-engine-overview)
19. [Observation Lifecycle](#19-observation-lifecycle)
20. [Observation Object Definition](#20-observation-object-definition)
21. [Observation Pipeline](#21-observation-pipeline)
22. [Observation Storage Strategy](#22-observation-storage-strategy)
23. [Observation Window Model](#23-observation-window-model)
24. [Observation Aggregation](#24-observation-aggregation)
25. [Detector Integration](#25-detector-integration)
26. [Compatibility with Existing Modules](#26-compatibility-with-existing-modules)
27. [Migration Strategy](#27-migration-strategy)
28. [Repository Compatibility](#28-repository-compatibility)
29. [Performance Targets](#29-performance-targets)
30. [Determinism Requirements](#30-determinism-requirements)
31. [Reproducibility Requirements](#31-reproducibility-requirements)
32. [Failure Recovery](#32-failure-recovery)
33. [Scalability Strategy](#33-scalability-strategy)
34. [Security Considerations](#34-security-considerations)
35. [Risk Register](#35-risk-register)
36. [Trade-off Analysis](#36-trade-off-analysis)
37. [Acceptance Criteria](#37-acceptance-criteria)
38. [Success Metrics](#38-success-metrics)
39. [Future Evolution](#39-future-evolution)
40. [Decision Log](#40-decision-log)
41. [Open Questions](#41-open-questions)
42. [Appendix](#42-appendix)

---

## 1. Executive Summary

### 1.1 Purpose

This document defines the engineering architecture for the MIIE v1.5 Observation Engine — a next-generation data foundation that supplies statistically meaningful observational datasets to every detector in the MIIE system.

### 1.2 Problem

The current MIIE v1.0 pipeline extracts metrics as **aggregated summary statistics** (one number per metric per window). This means detectors receive single values rather than distributions, making statistical tests like KS, Spearman correlation, and bootstrap confidence intervals either inapplicable or meaningless. The architecture fundamentally prevents detectors from operating at their designed statistical power.

### 1.3 Solution

Replace the current aggregated MetricDataFrame with an **Observation Engine** that extracts, stores, and serves **individual data points** (per-commit, per-file, per-PR observations) to detectors. Detectors will receive collections of observations per window, enabling proper statistical testing with adequate sample sizes.

### 1.4 Scope

The Observation Engine covers:

- Observation extraction from repository data sources
- Observation storage and retrieval
- Window construction from observation timestamps
- Aggregation of observations into detector-ready formats
- Backward-compatible interfaces for existing detectors

The Observation Engine does NOT cover:

- Detector algorithm redesign (detectors use new data, not new math)
- CLI redesign
- Scoring formula changes
- Reporting format changes
- Real-time monitoring (deferred to v2.0)

### 1.5 Key Outcomes

| Outcome | Current (v1.0) | Target (v1.5) |
|---------|----------------|---------------|
| Data per metric per window | 1 aggregated value | N individual observations |
| D-01 sample size | Always < 10 (skipped) | 50–500 observations per window |
| D-02 paired observations | N/A (single values) | 50–500 paired observations per window |
| D-03 bootstrap feasible | No (single values) | Yes (empirical distribution) |
| Cross-metric correlation | Impossible | Pearson/Spearman on paired observations |
| Trend detection | Impossible | Mann-Kendall on observation time series |

---

## 2. Current State of MIIE

### 2.1 Release Status

| Attribute | Value |
|-----------|-------|
| Version | 1.0.1 (tag), 1.0.0 (code) |
| Release Date | 2026-06-27 |
| License | MIT |
| Repository | Samragya013/miie |
| Test Count | 730 (667 unit + 63 integration) |
| CI Status | All 9 jobs green |
| CLI Commands | 10 (analyze, ingest, detect, explain, export, evaluate, generate, benchmark, validate, status) |

### 2.2 Frozen Components

The following components are frozen per the v1.0.1 baseline and will not change in v1.5 unless the Observation Engine requires interface modifications:

| Component | Status |
|-----------|--------|
| Pipeline orchestration | Frozen — 9-stage pipeline |
| Scoring engine | Frozen — IS/CS formulas |
| Evidence engine | Frozen — package assembly |
| Explanation engine | Frozen — narrative generation |
| Report generator | Frozen — 4 output formats |
| Benchmark framework | Frozen — 3 suites, ground truth |
| CLI interface | Frozen — 10 commands, 3-tier output |
| Error hierarchy | Frozen — MIIEError tree |
| Config format | Frozen — YAML/JSON schema |
| API endpoints | Frozen — 6 REST endpoints |

### 2.3 Changeable Components

| Component | v1.5 Change |
|-----------|-------------|
| Metric extraction | Major rewrite — observation-level extraction |
| MetricDataFrame | Replaced by ObservationStore |
| Window segmentation | New — window-from-observations |
| Detector input interface | Extended — receives ObservationWindow |
| Detector registry | Extended — new detector IDs (D-04+) |
| Schema definitions | Extended — new observation types |

---

## 3. Existing Scientific Pipeline

### 3.1 Pipeline Stages

The current pipeline executes 9 stages sequentially:

```
Stage 1: Ingestion     → RepositoryContext
Stage 2: Validation    → (no-op placeholder)
Stage 3: Extraction    → MetricDataFrame
Stage 4: Segmentation  → List[WindowDefinition]
Stage 4b: Re-extraction → MetricDataFrame (per-window)
Stage 5: Detection     → DetectorResults
Stage 6: Scoring       → ScorePackage
Stage 7: Evidence      → EvidencePackage
Stage 8: Explanation   → ExplanationReport
Stage 9: Reporting     → ReportOutput
```

### 3.2 Pipeline Implementation

The pipeline is implemented in two forms:

1. **`AnalysisPipeline` class** (`orchestration/pipeline.py`) — formal orchestrator with injected engine interfaces. Not used by CLI.
2. **`_run_pipeline()` function** (`cli.py:331-811`) — inline implementation used by CLI. Calls engines directly.

Both follow the same flow but the CLI version includes additional logic for progress reporting, privacy filtering, and terminal output.

### 3.3 Data Structures Between Stages

| Stage | Output | Key Fields |
|-------|--------|------------|
| Ingestion | `RepositoryContext` | repo_id, local_path, total_commits, first/last_commit_date |
| Extraction | `MetricDataFrame` | metrics: Dict[str, Dict[str, List[Optional[float]]]] |
| Segmentation | `List[WindowDefinition]` | window_id, start_date, end_date, commits |
| Detection | `DetectorResults` | d_01, d_02, d_03, detector_outputs |
| Scoring | `ScorePackage` | integrity: IntegrityScore, confidence: ConfidenceScore |
| Evidence | `EvidencePackage` | provenance, windows, metrics, detector_outputs, scores |
| Explanation | `ExplanationReport` | explanations, summary, recommendations, narratives |
| Reporting | `ReportOutput` | report_paths, manifest_path, checksums |

---

## 4. Current Detector Architecture

### 4.1 Detector Interface

All detectors implement `BaseDetector`:

```python
class BaseDetector(ABC):
    def __init__(self, detector_id, detector_name, supported_metrics)
    
    @abstractmethod
    def validate_input(self, metric_dataframe: MetricDataFrame) -> bool
    
    @abstractmethod
    def execute(self, metric_dataframe: MetricDataFrame) -> DetectorResult
```

**Contract:** Each detector receives the full `MetricDataFrame` and returns a `DetectorResult` containing a `detector_outputs` dict keyed by detector ID.

### 4.2 D-01: Distribution Drift Detector

**Statistical Method:** Kolmogorov-Smirnov two-sample test + Population Stability Index (PSI)

**Input Processing:**
1. Gets `vals_start` and `vals_end` from `metric_dataframe.metrics[metric][window_start]` and `[window_end]`
2. Each is a `List[float]` — the raw values for that metric in that window
3. Checks `len(vals_start) < 10 or len(vals_end) < 10` → skips if insufficient
4. Computes KS statistic and PSI
5. Classifies drift direction (mean_shift, variance_collapse, shape_change)

**Critical Finding:** The values in `metric_dataframe.metrics[metric][window]` are **aggregated summary statistics**, not individual observations. For M-02 (commit frequency), this is a single number: the total commit count in that window. The `len(vals)` check always returns 1 (single value), which is always < 10, so D-01 **always skips** drift detection.

### 4.3 D-02: Correlation Breakdown Detector

**Statistical Method:** Pearson r, Spearman ρ, Fisher-z transform, breakdown detection

**Input Processing:**
1. Generates all metric pairs via `itertools.combinations`
2. For each pair (M-i, M-j) in each window: gets `vals_i`, `vals_j`
3. Truncates to `min(len(vals_i), len(vals_j))`
4. Computes Pearson r, Spearman ρ, Fisher-z CI
5. Detects breakdowns across windows

**Critical Finding:** Same as D-01 — `vals_i` and `vals_j` are single aggregated values per window. Pearson correlation on two single values is undefined (requires n ≥ 2). D-02 **cannot compute correlations** in the current architecture.

### 4.4 D-03: Threshold Compression Detector

**Statistical Method:** Excess Mass test, Hartigan's Dip Test (KS approximation)

**Input Processing:**
1. For each metric, generates auto-thresholds from the data range
2. For each threshold × window: computes excess mass z-score and dip test
3. Uses bootstrap (1000 iterations) for p-value estimation

**Critical Finding:** With single values per window, the empirical CDF is a step function at one point. The excess mass test and dip test have no meaningful distribution to analyze. D-03 **produces statistically degenerate results**.

---

## 5. Existing Observation Model

### 5.1 MetricDataFrame Structure

```python
@dataclass
class MetricDataFrame:
    repo_id: str
    run_id: str
    timestamp: datetime.datetime
    metrics: Dict[str, Dict[str, List[Optional[float]]]]
    # e.g. {"M-02": {"w00": [142.0], "w01": [98.0]}}
```

The `metrics` dict maps:
- **Level 1:** Metric ID (M-01 through M-07)
- **Level 2:** Window ID (w00, w01, ...)
- **Level 3:** List of float values

### 5.2 How Values Are Populated

| Metric | Extraction Method | Values per Window |
|--------|------------------|-------------------|
| M-01 (Coverage) | Parses coverage.xml/lcov.info | 1 (percentage) |
| M-02 (Commit Freq) | `git rev-list --count` | 1 (total count) |
| M-03 (Review Part) | PR export JSON average | 1 (avg reviewers/PR) |
| M-04 (Review Latency) | PR export JSON mean | 1 (avg hours) |
| M-05 (Issue Resolution) | Issue export JSON mean | 1 (avg days) |
| M-06 (Code Churn) | `git log --numstat` sum | 1 (total lines) |
| M-07 (Complexity) | lizard/radon average | 1 (avg CC score) |

**Every metric produces exactly 1 value per window.** The `List[float]` wrapper is always a single-element list.

### 5.3 Why This Matters

The detectors are designed to receive **distributions** of observations. D-01 needs multiple data points to compute a KS test. D-02 needs paired observations to compute correlation. D-03 needs an empirical distribution to test for compression. The current model provides none of this.

---

## 6. Existing Data Flow

### 6.1 Complete Data Flow

```
CLI arguments
  ↓
validate_cli_analyze_inputs()
  ↓
RepositoryIngestionEngine.ingest()
  → RepositoryContext
  ↓
MetricExtractionEngine.extract()
  → MetricDataFrame {metrics: {M-XX: {wXX: [single_value]}}}
  ↓
WindowSegmentationEngine.segment()
  → List[WindowDefinition]
  ↓
MetricExtractionEngine.extract(windows=)  [RE-EXTRACTION]
  → MetricDataFrame {metrics: {M-XX: {wXX: [single_value]}}}
  ↓
DetectorDispatcherEngine.invoke()
  → DetectorResults
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
  ↓
Terminal 3-tier output
```

### 6.2 Key Observations

1. **Double extraction:** The pipeline extracts metrics twice — once for initial data, once after windows are defined. Both produce the same single-value-per-window result.

2. **Window-agnostic extraction:** The extraction engine does not know about windows until the re-extraction step. It operates on the full repository history.

3. **Detector isolation:** Each detector independently filters the MetricDataFrame to its supported metrics. No cross-detector data sharing.

4. **No observation persistence:** Extracted data is held in memory only. No observation store or cache.

5. **No raw data access:** Detectors never see individual commits, files, or PRs — only aggregated numbers.

---

## 7. Root Cause Analysis

### 7.1 Architectural Limitations

| Limitation | Origin | Impact |
|-----------|--------|--------|
| Single value per metric per window | Data model (MetricDataFrame) | All statistical tests degenerate |
| Extraction is window-agnostic | Extraction pipeline design | No per-observation windowing |
| No observation identity | Data model | Cannot track individual data points |
| Aggregation before detection | Pipeline ordering | Information loss before detectors run |
| No cross-metric observation linking | Data model | Cannot compute cross-metric correlations |

### 7.2 Statistical Limitations

| Limitation | Origin | Impact |
|-----------|--------|--------|
| KS test on n=1 | Sample size from extraction | Always skips (len < 10) |
| Pearson on n=1 | Sample size from extraction | Undefined (variance = 0) |
| Bootstrap on n=1 | Sample size from extraction | All samples identical |
| PSI on n=1 | Sample size from extraction | No distribution to compare |
| No variance estimation | Aggregation | Cannot assess measurement uncertainty |

### 7.3 Observational Limitations

| Limitation | Origin | Impact |
|-----------|--------|--------|
| No per-commit metrics | Extraction granularity | Cannot detect commit-level anomalies |
| No per-file metrics | Extraction granularity | Cannot detect file-level patterns |
| No per-developer metrics | Extraction granularity | Cannot detect contributor anomalies |
| No temporal resolution | Window aggregation | Cannot detect intra-window dynamics |
| No provenance per observation | Data model | Cannot trace findings to source |

### 7.4 Aggregation Limitations

| Limitation | Origin | Impact |
|-----------|--------|--------|
| Mean-only aggregation | Extraction design | Loses distribution shape |
| No quantile information | Extraction design | Cannot detect tail behavior |
| No outlier detection pre-aggregation | Pipeline design | Outliers masked by averaging |
| No robust statistics | Extraction design | Sensitive to extreme values |

### 7.5 Window Limitations

| Limitation | Origin | Impact |
|-----------|--------|--------|
| Fixed window sizes | Segmentation design | Cannot adapt to repository activity |
| Windows defined after extraction | Pipeline ordering | Extraction unaware of windows |
| No overlapping windows | Segmentation design | Cannot detect gradual changes |
| Minimum 2 windows required | Pipeline gate | Short analyses fail |

### 7.6 Sampling Limitations

| Limitation | Origin | Impact |
|-----------|--------|--------|
| No sampling strategy | Extraction design | All-or-nothing extraction |
| No stratified sampling | Extraction design | Cannot ensure metric coverage |
| No power analysis | Extraction design | Cannot determine required sample size |
| No confidence intervals | Extraction design | Point estimates only |

### 7.7 Implementation vs. Architecture

**Implementation problems** (fixable without architectural change):
- D-01 sample size check could be relaxed
- Bootstrap iterations could be reduced
- Error handling could be improved

**Architectural problems** (require fundamental redesign):
- MetricDataFrame stores aggregated values, not observations
- Extraction produces single values per window
- Pipeline ordering prevents observation-level analysis
- No observation identity or provenance
- No cross-metric observation linking

**Conclusion:** The limitations are architectural, not implementation. The MetricDataFrame data model and extraction pipeline design fundamentally prevent detectors from operating correctly.

---

## 8. Scientific Problem Statement

### 8.1 Core Problem

MIIE v1.0 extracts metrics as **aggregated summary statistics** (one number per metric per window), but its detectors are designed to perform **statistical tests on distributions of observations**. This mismatch means:

1. **D-01 (Distribution Drift)** cannot detect distributional changes because it receives single values, not distributions.
2. **D-02 (Correlation Breakdown)** cannot compute correlations because it receives single values per metric, not paired observations.
3. **D-03 (Threshold Compression)** cannot test for compression because it has no empirical distribution to analyze.

### 8.2 Consequence

The current system reports integrity scores and confidence bands that are **derived from detectors that cannot execute their designed statistical tests**. The scores are computed from detector outputs that are either:
- Skipped entirely (sample size < 10)
- Computed on degenerate inputs (n=1)
- Based on single-point comparisons rather than distributional analysis

### 8.3 Required Transformation

The system must be transformed so that:

1. **Extraction** produces individual observations (per-commit, per-file, per-PR data points)
2. **Storage** preserves observation identity and provenance
3. **Windowing** groups observations by time or commit boundaries
4. **Detection** receives collections of observations per window, enabling proper statistical testing
5. **Aggregation** happens after detection, not before

---

## 9. Motivation

### 9.1 Scientific Integrity

The current architecture produces results that appear statistically rigorous but are derived from detectors that cannot execute their designed tests. This undermines the scientific validity of MIIE's integrity assessments.

### 9.2 Detector Utilization

The three frozen detectors (D-01, D-02, D-03) were designed with specific statistical assumptions about input data. The current architecture prevents these assumptions from being satisfied. The Observation Engine will unlock the full capability of existing detectors without changing their algorithms.

### 9.3 Extensibility

New detectors (D-04 through D-07 planned for v1.5) require observation-level data:
- **D-04 (Bimodality)** requires distribution shape analysis → needs multiple observations
- **D-05 (Multivariate Anomaly)** requires multivariate observations → needs per-entity data
- **D-06 (Trend Breakpoint)** requires time-series data → needs temporal observations
- **D-07 (Seasonal Decomposition)** requires periodic data → needs high-frequency observations

### 9.4 Research Foundation

The Observation Engine establishes the data foundation for future research capabilities:
- Cross-metric causal analysis
- Longitudinal trend detection
- Adaptive threshold calibration
- Developer behavior analysis
- Repository health monitoring

---

## 10. Research Background

### 10.1 Statistical Process Control (SPC)

SPC methods monitor process behavior through control charts. Key principles:
- Individual observations are plotted over time
- Control limits are derived from process variability
- Out-of-control signals indicate process changes

**Relevance:** MIIE's integrity monitoring is analogous to SPC. The Observation Engine enables SPC-style monitoring of software metrics.

### 10.2 Observational Studies

In observational studies, individual data points are collected and analyzed without experimental intervention. Key requirements:
- Individual observation identity
- Temporal ordering
- Covariate measurement
- Confounding control

**Relevance:** Repository analysis is inherently observational. The Observation Engine provides the data infrastructure for rigorous observational analysis.

### 10.3 Time Series Analysis

Time series methods analyze temporal patterns in sequential observations. Key requirements:
- Regular or irregular temporal spacing
- Multiple observations per time period
- Stationarity or trend modeling
- Seasonal decomposition

**Relevance:** Repository metrics are time series. The Observation Engine enables time series analysis of software development patterns.

### 10.4 Change Point Detection

Change point detection identifies abrupt shifts in time series properties. Methods include:
- PELT (Pruned Exact Linear Time)
- Binary Segmentation
- CUSUM (Cumulative Sum)
- Bayesian Online Change Point Detection

**Relevance:** MIIE's drift detection is a change point problem. The Observation Engine provides the temporal resolution needed for change point algorithms.

---

## 11. Design Goals

| ID | Goal | Priority | Rationale |
|----|------|----------|-----------|
| G-1 | Observation-level extraction | HIGH | Core architectural change |
| G-2 | Per-commit metric values | HIGH | Enables distributional analysis |
| G-3 | Temporal observation identity | HIGH | Enables time series analysis |
| G-4 | Cross-metric observation linking | MEDIUM | Enables correlation analysis |
| G-5 | Backward-compatible detector interface | HIGH | Existing detectors must work unchanged |
| G-6 | Observation provenance tracking | MEDIUM | Traceability and debugging |
| G-7 | Efficient storage and retrieval | MEDIUM | Performance for large repositories |
| G-8 | Deterministic extraction | HIGH | Reproducibility requirement |
| G-9 | Incremental extraction | LOW | Performance optimization |
| G-10 | Extensible observation types | MEDIUM | Future detector support |

---

## 12. Non-Goals

| ID | Non-Goal | Reason |
|----|----------|--------|
| NG-1 | Redesign detector algorithms | Detectors use new data, not new math |
| NG-2 | Redesign CLI interface | Frozen per baseline |
| NG-3 | Redesign scoring formulas | Frozen per baseline |
| NG-4 | Redesign reporting formats | Frozen per baseline |
| NG-5 | Real-time monitoring | Deferred to v2.0 |
| NG-6 | Multi-repo analysis | Deferred to v1.6 |
| NG-7 | Cloud deployment | Deferred to v2.0 |
| NG-8 | ML-based detectors | Requires training data |
| NG-9 | Web dashboard | Requires API expansion |
| NG-10 | REPL/interactive mode | UX overhaul deferred |

---

## 13. Engineering Principles

| Principle | Description | Application |
|-----------|-------------|-------------|
| Observation-first | Individual data points are first-class citizens | MetricDataFrame replaced by ObservationStore |
| Extraction before windowing | Extract observations, then group into windows | Pipeline ordering changed |
| Deterministic extraction | Same input → same output, always | Seed-controlled extraction, sorted outputs |
| Backward compatibility | Existing detectors work without modification | Adapter layer translates observations to MetricDataFrame |
| Provenance tracking | Every observation traces to its source | Observation objects carry source metadata |
| Fail-safe defaults | Missing data produces empty observations, not errors | Detectors receive empty collections, not exceptions |
| Minimal surface area | New interfaces are narrow and well-defined | IObservationStore has 5 methods, not 50 |
| Separation of concerns | Extraction, storage, windowing are independent | Each stage is independently testable |

---

## 14. Scientific Principles

| Principle | Description | Application |
|-----------|-------------|-------------|
| Distribution over summary | Preserve distributional information | Per-commit values, not averages |
| Temporal ordering | Respect causal time structure | Observations carry timestamps |
| Sample size adequacy | Ensure statistical tests have power | Minimum observation counts enforced |
| Deterministic reproducibility | Same repo + config → same observations | Seed-controlled extraction |
| Provenance integrity | Trace every finding to raw data | Observation IDs link to source commits |
| Multiple testing awareness | Account for multiple comparisons | Bonferroni/BH correction in detectors |
| Robustness | Handle outliers and missing data | Trimmed statistics, complete-case analysis |
| Transparency | All intermediate data is inspectable | Observation store is queryable |

---

## 15. Candidate Observation Models

### 15.1 Model A: Commit-Level Observations

**Description:** Each git commit produces one observation per metric. For M-02 (commit frequency), each commit is a count of 1. For M-06 (code churn), each commit contributes its insertions + deletions.

**Structure:**
```
Observation {
    observation_id: str
    timestamp: datetime
    source_type: "commit"
    source_id: str  # commit SHA
    metric_id: str
    value: float
    metadata: Dict  # author, files_changed, etc.
}
```

**Advantages:**
- Natural temporal ordering
- One observation per commit → large sample sizes
- Direct link to source code changes
- Enables commit-level anomaly detection

**Disadvantages:**
- M-01 (coverage) not naturally per-commit
- M-03/M-04/M-05 (review metrics) not commit-derived
- High observation count (1000s per repo)
- Storage overhead for metadata

### 15.2 Model B: File-Level Observations

**Description:** Each file change produces one observation per metric. For M-06 (churn), each modified file contributes its line changes. For M-07 (complexity), each file contributes its complexity score.

**Structure:**
```
Observation {
    observation_id: str
    timestamp: datetime
    source_type: "file_change"
    source_id: str  # file path + commit
    metric_id: str
    value: float
    metadata: Dict  # file path, language, size, etc.
}
```

**Advantages:**
- Fine-grained analysis
- File-level anomaly detection
- Language-aware analysis

**Disadvantages:**
- Very high observation count (10,000s per repo)
- Not all metrics are file-natural
- Storage overhead significant
- Complex aggregation required

### 15.3 Model C: Developer-Event Observations

**Description:** Each developer action (commit, PR, review, issue close) produces observations. Metrics are derived from developer behavior patterns.

**Structure:**
```
Observation {
    observation_id: str
    timestamp: datetime
    source_type: "developer_event"
    source_id: str  # event ID
    metric_id: str
    value: float
    metadata: Dict  # developer, event_type, etc.
}
```

**Advantages:**
- Developer behavior analysis
- Social dimension of integrity
- Multi-source observations

**Disadvantages:**
- Requires developer identity resolution
- Privacy concerns
- Complex event model
- Not all metrics are developer-natural

### 15.4 Model D: Hybrid Commit-File Observations

**Description:** Commit-level observations as primary, with file-level metadata enrichment. Each commit produces one observation per applicable metric, with file-level details stored as metadata.

**Structure:**
```
Observation {
    observation_id: str
    timestamp: datetime
    source_type: "commit"
    source_id: str  # commit SHA
    metric_id: str
    value: float
    metadata: Dict  # author, files_changed, insertions, deletions, etc.
}
```

**Advantages:**
- Commit-level temporal resolution
- File-level metadata available
- Manageable observation count
- Natural fit for git-derived metrics

**Disadvantages:**
- M-01/M-03/M-04/M-05 still need separate extraction
- Metadata extraction adds complexity
- Storage for metadata overhead

### 15.5 Model E: Time-Series Event Stream

**Description:** All repository events (commits, PRs, issues, reviews) are captured as a unified event stream. Each event contributes to one or more metrics.

**Structure:**
```
Event {
    event_id: str
    timestamp: datetime
    event_type: str  # commit, pr_created, pr_reviewed, issue_closed
    metric_values: Dict[str, float]  # metric_id -> value
    metadata: Dict
}
```

**Advantages:**
- Unified event model
- Cross-event correlations possible
- Temporal resolution at event granularity

**Disadvantages:**
- Complex event normalization
- Requires event type taxonomy
- High storage overhead
- Over-engineered for current needs

---

## 16. Comparative Evaluation

### 16.1 Comparison Matrix

| Criterion | A: Commit | B: File | C: Developer | D: Hybrid | E: Event Stream |
|-----------|-----------|---------|--------------|-----------|-----------------|
| Statistical validity | HIGH | HIGH | MEDIUM | HIGH | HIGH |
| Sample size per window | 50-500 | 500-5000 | 10-100 | 50-500 | 100-1000 |
| Temporal resolution | Commit-time | File-change time | Event-time | Commit-time | Event-time |
| Storage overhead | LOW | HIGH | MEDIUM | LOW-MEDIUM | HIGH |
| Implementation complexity | LOW | MEDIUM | HIGH | MEDIUM | HIGH |
| Detector compatibility | HIGH | MEDIUM | LOW | HIGH | MEDIUM |
| Benchmark compatibility | HIGH | MEDIUM | LOW | HIGH | MEDIUM |
| Determinism | HIGH | HIGH | MEDIUM | HIGH | MEDIUM |
| Research value | MEDIUM | HIGH | HIGH | MEDIUM | HIGH |
| Extensibility | MEDIUM | HIGH | HIGH | MEDIUM | HIGH |
| Backward compatibility | HIGH | LOW | LOW | HIGH | LOW |

### 16.2 Evaluation Notes

**Model A (Commit-Level):** Best fit for current detector requirements. Git-native metrics (M-02, M-06) naturally produce per-commit observations. Adequate sample sizes (50-500 per window for active repos). Lowest implementation complexity.

**Model B (File-Level):** Highest granularity but excessive storage and complexity. File-level observations are valuable for D-05 (multivariate) but not required for existing detectors.

**Model C (Developer-Event):** Interesting for research but requires developer identity resolution, which is unreliable across repos. Privacy concerns with developer tracking.

**Model D (Hybrid):** Best balance of granularity, complexity, and compatibility. Commit-level observations with file-level metadata provides extensibility without excessive overhead.

**Model E (Event Stream):** Over-engineered for current needs. Valuable for future research but requires significant infrastructure investment.

### 16.3 Recommendation

**Selected: Model D (Hybrid Commit-File Observations)**

Rationale:
1. Commit-level observations satisfy all existing detector requirements
2. File-level metadata enables future detectors without separate extraction
3. Manageable storage overhead (50-500 observations per metric per window)
4. Natural fit for git-derived metrics
5. Extensible to file-level analysis when needed
6. Backward-compatible through adapter layer

---

## 17. Selected Architecture

### 17.1 Architecture Overview

The Observation Engine follows a **layered extraction-storage-windowing** architecture:

```
Repository Data Sources
  ↓
Observation Extractors (per metric)
  ↓
Observation Store (in-memory + optional disk)
  ↓
Window Builder (temporal/commit grouping)
  ↓
Observation Windows (collections of observations)
  ↓
Detector Adapter Layer (compatibility shim)
  ↓
Detectors (D-01 through D-07)
```

### 17.2 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Observation granularity | Commit-level | Best balance of sample size and complexity |
| Storage model | In-memory with optional serialization | Performance + reproducibility |
| Window construction | From observation timestamps | Decouples extraction from windowing |
| Cross-metric linking | Via shared commit SHA | Enables correlation analysis |
| Backward compatibility | Adapter layer | Existing detectors work unchanged |
| Determinism | Seed-controlled extraction | Reproducible results |

---

## 18. Observation Engine Overview

### 18.1 Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Observation Engine                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Extraction   │  │    Store     │  │    Window    │  │
│  │   Layer       │  │    Layer     │  │    Builder   │  │
│  │              │  │              │  │              │  │
│  │  - Commit    │  │  - InMemory  │  │  - Temporal  │  │
│  │  - Coverage  │  │  - Indexed   │  │  - Commit    │  │
│  │  - Review    │  │  - Queryable │  │  - Custom    │  │
│  │  - Issue     │  │              │  │              │  │
│  │  - Complexity│  │              │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
│         └─────────────────┼─────────────────┘           │
│                           │                             │
│                    ┌──────┴───────┐                     │
│                    │   Adapter    │                     │
│                    │    Layer     │                     │
│                    │              │                     │
│                    │  - MetricDF  │                     │
│                    │  - Windows   │                     │
│                    │  - Detectors │                     │
│                    └──────────────┘                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 18.2 Component Responsibilities

| Component | Responsibility | Input | Output |
|-----------|---------------|-------|--------|
| Extraction Layer | Extract observations from repo data | RepositoryContext | List[Observation] |
| Store Layer | Store, index, query observations | List[Observation] | ObservationStore |
| Window Builder | Group observations into windows | ObservationStore + WindowConfig | List[ObservationWindow] |
| Adapter Layer | Translate to/from existing formats | ObservationWindow | MetricDataFrame |

### 18.3 Data Flow

```
RepositoryContext
  ↓
Extraction Layer
  → List[Observation]  (all observations, all metrics)
  ↓
Store Layer
  → ObservationStore  (indexed, queryable)
  ↓
Window Builder
  → List[ObservationWindow]  (grouped by time/commit)
  ↓
Adapter Layer
  → MetricDataFrame  (backward-compatible format)
  ↓
Detectors
  → DetectorResults
```

---

## 19. Observation Lifecycle

### 19.1 Lifecycle States

```
Created → Extracted → Stored → Windowed → Consumed → Archived
```

| State | Description | Location |
|-------|-------------|----------|
| Created | Observation object instantiated | Memory |
| Extracted | Value computed from source data | Memory |
| Stored | Persisted in ObservationStore | Memory/Disk |
| Windowed | Assigned to one or more windows | Memory |
| Consumed | Read by detector via adapter | Memory |
| Archived | Serialized for reproducibility | Disk |

### 19.2 Lifecycle Transitions

| Transition | Trigger | Validation |
|-----------|---------|------------|
| Created → Extracted | Extraction completes | value is not None |
| Extracted → Stored | Store.add() called | observation_id unique |
| Stored → Windowed | WindowBuilder.build() called | observation within window bounds |
| Windowed → Consumed | Detector reads via adapter | observation count ≥ detector minimum |
| Consumed → Archived | Analysis completes | Serializable to JSON |

### 19.3 Failure States

| Failure | Recovery | Impact |
|---------|----------|--------|
| Extraction fails | Skip observation, log warning | Reduced sample size |
| Storage full | Fail with ExtractionError | Analysis aborts |
| Window assignment fails | Skip observation, log warning | Reduced sample size |
| Consumption fails | Detector skips, logs reason | No detection for that metric |
| Archival fails | Log warning, continue | No persistent record |

---

## 20. Observation Object Definition

### 20.1 Core Observation

```python
@dataclass
class Observation:
    """A single data point extracted from a repository."""
    
    observation_id: str          # UUID, deterministic from (source_id, metric_id)
    timestamp: datetime          # When the observation was made
    metric_id: str               # M-01 through M-07 (or extended)
    value: float                 # The observed value
    source_type: str             # "commit", "coverage", "pr", "issue", "complexity"
    source_id: str               # Commit SHA, PR number, file path, etc.
    repo_id: str                 # Repository identifier
    metadata: Dict[str, Any]     # Source-specific details
```

### 20.2 Observation Metadata by Source Type

| Source Type | metadata Fields |
|-------------|----------------|
| commit | author, message, files_changed, insertions, deletions, parents |
| coverage | file_path, line_coverage, branch_coverage, coverage_tool |
| pr | number, author, reviewers, created_at, merged_at, title |
| issue | number, author, created_at, closed_at, labels, milestone |
| complexity | file_path, function_name, language, cc_score, lines |

### 20.3 Deterministic Observation IDs

Observation IDs are computed deterministically from source metadata:

```python
def compute_observation_id(source_type: str, source_id: str, metric_id: str) -> str:
    """Deterministic observation ID from source metadata."""
    content = f"{source_type}:{source_id}:{metric_id}"
    return sha256(content.encode())[:16]
```

This ensures:
- Same source → same observation ID (reproducibility)
- No UUID randomness (determinism)
- Collision-resistant (SHA-256)

### 20.4 Observation Validation

```python
@dataclass
class Observation:
    def __post_init__(self):
        if not (0.0 <= self.timestamp.timestamp() <= 2**31):
            raise ValueError("timestamp out of range")
        if not re.match(r"^M-[0-9]{2}$", self.metric_id):
            raise ValueError(f"invalid metric_id: {self.metric_id}")
        if math.isnan(self.value) or math.isinf(self.value):
            raise ValueError(f"invalid value: {self.value}")
        if self.source_type not in ALLOWED_SOURCE_TYPES:
            raise ValueError(f"invalid source_type: {self.source_type}")
```

---

## 21. Observation Pipeline

### 21.1 Extraction Pipeline

```
RepositoryContext
  ↓
┌─────────────────────────────────────────────┐
│ Metric Extractors (parallel execution)      │
│                                             │
│  CommitExtractor ──→ M-02, M-06 observations│
│  CoverageExtractor ──→ M-01 observations    │
│  ReviewExtractor ──→ M-03, M-04 observations│
│  IssueExtractor ──→ M-05 observations       │
│  ComplexityExtractor ──→ M-07 observations  │
│                                             │
└─────────────────────┬───────────────────────┘
                      ↓
              List[Observation]
                      ↓
              ObservationStore
```

### 21.2 CommitExtractor (M-02, M-06)

**Input:** RepositoryContext (local_path, since, until, exclude_bots)

**Process:**
1. Run `git log --format=%H|%aI|%s --no-merges` to get commit list
2. For each commit:
   - M-02 observation: value = 1.0 (commit as unit of frequency)
   - M-06 observation: parse `git diff --numstat <parent> <sha>` → insertions + deletions
3. Create Observation objects with deterministic IDs

**Output:** List[Observation] where metric_id ∈ {M-02, M-06}

**Sample Size:** Number of commits in the analysis window (typically 50-2000)

### 21.3 CoverageExtractor (M-01)

**Input:** RepositoryContext + coverage artifact path

**Process:**
1. Parse coverage.xml (Cobertura), lcov.info, or .coverage JSON
2. For each commit that modified source files:
   - Estimate coverage delta based on lines changed
   - Or: use CI coverage data if available
3. Create Observation objects

**Output:** List[Observation] where metric_id = M-01

**Note:** Per-commit coverage estimation is approximate. Future versions may use CI API integration for precise coverage data.

### 21.4 ReviewExtractor (M-03, M-04)

**Input:** PR export JSON or GitHub API

**Process:**
1. For each PR in the time range:
   - M-03 observation: value = len(reviewers) / max(1, len(commits_in_PR))
   - M-04 observation: value = (first_review_at - created_at).total_seconds() / 3600
2. Create Observation objects with PR metadata

**Output:** List[Observation] where metric_id ∈ {M-03, M-04}

### 21.5 IssueExtractor (M-05)

**Input:** Issue export JSON or GitHub API

**Process:**
1. For each closed issue in the time range:
   - M-05 observation: value = (closed_at - created_at).total_days()
2. Create Observation objects with issue metadata

**Output:** List[Observation] where metric_id = M-05

### 21.6 ComplexityExtractor (M-07)

**Input:** RepositoryContext + source files

**Process:**
1. For each source file modified in each commit:
   - Run lizard/radon to compute function-level complexity
   - M-07 observation: value = mean(CC scores) for the file
2. Create Observation objects

**Output:** List[Observation] where metric_id = M-07

### 21.7 Extraction Ordering

Extractors execute in dependency order:
1. CommitExtractor (no dependencies, produces commit list)
2. CoverageExtractor (depends on commit list for file changes)
3. ReviewExtractor (independent, requires PR data)
4. IssueExtractor (independent, requires issue data)
5. ComplexityExtractor (depends on commit list for file changes)

All extractors can be parallelized after CommitExtractor completes.

---

## 22. Observation Storage Strategy

### 22.1 In-Memory Store

```python
class ObservationStore:
    """In-memory observation store with indexing."""
    
    def __init__(self):
        self._observations: Dict[str, Observation] = {}  # observation_id → Observation
        self._by_metric: Dict[str, List[str]] = {}       # metric_id → [observation_ids]
        self._by_time: List[str] = []                     # sorted by timestamp
        self._by_source: Dict[str, List[str]] = {}       # source_type → [observation_ids]
    
    def add(self, observation: Observation) -> None: ...
    def get(self, observation_id: str) -> Optional[Observation]: ...
    def query(self, metric_id: str = None, since: datetime = None, 
              until: datetime = None) -> List[Observation]: ...
    def count(self, metric_id: str = None) -> int: ...
    def to_dataframe(self, metric_id: str) -> List[float]: ...
```

### 22.2 Indexing Strategy

| Index | Purpose | Structure |
|-------|---------|-----------|
| Primary | observation_id lookup | Dict[str, Observation] |
| Metric | Filter by metric_id | Dict[str, List[str]] |
| Temporal | Range queries by timestamp | Sorted List[str] |
| Source | Filter by source_type | Dict[str, List[str]] |

### 22.3 Query Interface

```python
# Get all observations for a metric in a time range
store.query(metric_id="M-02", since=datetime(2025,1,1), until=datetime(2025,6,30))

# Get all observations for a source type
store.query(source_type="commit")

# Get observation count per metric
{metric_id: store.count(metric_id) for metric_id in ["M-01", "M-02", ...]}
```

### 22.4 Serialization

For reproducibility, the store serializes to JSON:

```json
{
  "store_version": "1.0.0",
  "repo_id": "...",
  "observation_count": 1234,
  "observations": [
    {
      "observation_id": "abc123...",
      "timestamp": "2025-03-15T10:30:00Z",
      "metric_id": "M-02",
      "value": 1.0,
      "source_type": "commit",
      "source_id": "def456...",
      "repo_id": "...",
      "metadata": {"author": "...", "files_changed": 5}
    }
  ]
}
```

---

## 23. Observation Window Model

### 23.1 Window Construction from Observations

Unlike v1.0 (windows defined first, then data extracted), v1.5 extracts data first, then constructs windows:

```
ObservationStore (all observations)
  ↓
Window Builder (applies windowing strategy)
  ↓
List[ObservationWindow] (observations grouped by window)
```

### 23.2 ObservationWindow

```python
@dataclass
class ObservationWindow:
    """A collection of observations within a time/commit window."""
    
    window_id: str                    # w00, w01, ...
    start_date: datetime.date
    end_date: datetime.date
    observations: List[Observation]   # all observations in this window
    metric_counts: Dict[str, int]     # metric_id → observation count
```

### 23.3 Windowing Strategies

| Strategy | Grouping | Use Case |
|----------|----------|----------|
| temporal | Fixed time intervals | Default, most general |
| commit | Commit-count intervals | Activity-based analysis |
| hybrid | Time intervals with minimum commit count | Balanced approach |
| custom | User-defined boundaries | Research use cases |

### 23.4 Temporal Windowing

```python
def build_temporal_windows(
    store: ObservationStore,
    window_size_days: int,
    start_date: datetime.date = None,
    end_date: datetime.date = None,
) -> List[ObservationWindow]:
    """
    Construct windows by partitioning the observation time range.
    
    Algorithm:
    1. Determine min/max timestamps from observations
    2. Create fixed-width intervals (window_size_days)
    3. Assign each observation to its interval
    4. Skip empty windows
    5. Return non-empty windows with sequential IDs
    """
```

### 23.5 Commit-Count Windowing

```python
def build_commit_windows(
    store: ObservationStore,
    commits_per_window: int,
) -> List[ObservationWindow]:
    """
    Construct windows by partitioning the commit sequence.
    
    Algorithm:
    1. Get all commit observations (M-02) sorted by timestamp
    2. Every commits_per_window commits → new window
    3. Assign all observations (all metrics) to windows by timestamp
    4. Return non-empty windows
    """
```

### 23.6 Minimum Window Requirements

| Requirement | Value | Rationale |
|-------------|-------|-----------|
| Minimum observations per window | 10 | Statistical test power |
| Minimum windows | 2 | Cross-window comparison |
| Maximum empty windows between non-empty | 1 | No gaps in analysis |
| Window overlap | None | Mutually exclusive windows |

---

## 24. Observation Aggregation

### 24.1 Aggregation for Detectors

Detectors that cannot work with raw observations (legacy detectors) receive aggregated data via the adapter layer. Aggregation preserves distributional information:

```python
@dataclass
class AggregatedMetric:
    """Aggregated metric data for a window, preserving distributional information."""
    
    metric_id: str
    window_id: str
    observations: List[float]        # raw values (for KS test, etc.)
    summary: AggregatedSummary       # summary statistics
    
@dataclass
class AggregatedSummary:
    n: int                           # sample size
    mean: float                      # arithmetic mean
    std: float                       # standard deviation
    min: float                       # minimum
    max: float                       # maximum
    median: float                    # median
    q25: float                       # 25th percentile
    q75: float                       # 75th percentile
    cv: float                        # coefficient of variation
```

### 24.2 Aggregation Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| Full distribution | All raw observations | D-01 (KS test), D-03 (empirical CDF) |
| Paired distribution | Paired observations across metrics | D-02 (correlation) |
| Summary statistics | Mean, std, quantiles | Confidence score factors |
| Temporal series | Observations ordered by time | Trend detection |

### 24.3 Cross-Metric Aggregation

For D-02 (correlation), the adapter produces paired observations:

```python
def aggregate_paired(
    store: ObservationWindow,
    metric_i: str,
    metric_j: str,
    join_on: str = "source_id",  # join by commit SHA
) -> Tuple[List[float], List[float]]:
    """
    Produce paired observations for correlation analysis.
    
    Joins observations from metric_i and metric_j by their shared source_id
    (e.g., commit SHA), producing aligned value pairs.
    """
```

---

## 25. Detector Integration

### 25.1 Adapter Layer

The adapter layer translates between the new Observation Engine and existing detector interfaces:

```python
class DetectorAdapter:
    """Translates ObservationWindow to MetricDataFrame for legacy detectors."""
    
    def to_metric_dataframe(
        self,
        windows: List[ObservationWindow],
        store: ObservationStore,
    ) -> MetricDataFrame:
        """Convert ObservationWindows to backward-compatible MetricDataFrame."""
        
    def to_detector_results(
        self,
        legacy_results: DetectorResults,
    ) -> DetectorResults:
        """Passthrough for detector results (no translation needed)."""
```

### 25.2 Adapter Translation

```python
def to_metric_dataframe(windows, store) -> MetricDataFrame:
    """
    Translation logic:
    1. For each window, get all observations
    2. Group by metric_id
    3. Extract values as List[float]
    4. Build Dict[str, Dict[str, List[float]]] structure
    
    Result: MetricDataFrame with N values per metric per window
    (where N = observation count, not 1)
    """
    metrics = {}
    for window in windows:
        for metric_id in window.metric_counts:
            if metric_id not in metrics:
                metrics[metric_id] = {}
            obs_values = [o.value for o in window.observations if o.metric_id == metric_id]
            metrics[metric_id][window.window_id] = obs_values
    return MetricDataFrame(
        repo_id=store.repo_id,
        run_id=str(uuid4()),
        timestamp=datetime.now(timezone.utc),
        metrics=metrics,
    )
```

### 25.3 Detector Behavior with New Data

| Detector | v1.0 Behavior | v1.5 Behavior |
|----------|---------------|---------------|
| D-01 | Always skips (n=1 < 10) | KS test on N observations (N=50-500) |
| D-02 | Cannot compute (n=1) | Pearson/Spearman on N paired observations |
| D-03 | Degenerate CDF (n=1) | Bootstrap on N observations |
| D-04 (new) | N/A | Hartigan's dip test on N observations |
| D-05 (new) | N/A | Mahalanobis distance on N×p observations |
| D-06 (new) | N/A | PELT on N temporal observations |
| D-07 (new) | N/A | STL decomposition on N periodic observations |

### 25.4 Minimum Sample Size Enforcement

```python
MIN_OBSERVATIONS_PER_WINDOW = 10  # per metric per window

def validate_window_observations(
    window: ObservationWindow,
    metric_id: str,
) -> bool:
    """Check if a window has enough observations for a metric."""
    count = sum(1 for o in window.observations if o.metric_id == metric_id)
    return count >= MIN_OBSERVATIONS_PER_WINDOW
```

---

## 26. Compatibility with Existing Modules

### 26.1 Interface Compatibility

| Module | Interface | Compatibility |
|--------|-----------|--------------|
| CLI | `analyze` command | Unchanged — same arguments, same output |
| Pipeline | `AnalysisPipeline` | Extended — new stage for observation extraction |
| Scoring | `ScoringEngine` | Unchanged — receives DetectorResults as before |
| Evidence | `EvidenceEngine` | Extended — includes observation summary |
| Explanation | `ExplanationEngine` | Unchanged — receives EvidencePackage as before |
| Reporting | `ReportGenerator` | Unchanged — receives AnalysisResult as before |
| Benchmarks | `BenchmarkRunner` | Extended — new benchmark suites for observation-based detectors |

### 26.2 Data Model Compatibility

| Model | v1.0 | v1.5 | Compatibility |
|-------|------|------|--------------|
| MetricDataFrame | Aggregated values | Observation lists | Backward-compatible (adapter) |
| DetectorResults | Dict-based output | Dict-based output | Identical |
| ScorePackage | IS + CS | IS + CS | Identical |
| EvidencePackage | Provenance + data | Provenance + data | Extended (observation summary) |
| ExplanationReport | Narratives | Narratives | Identical |

### 26.3 CLI Compatibility

The CLI `analyze` command produces the same output format. The only change is that detectors now have more data to work with, potentially producing different (more accurate) results.

```bash
# v1.0 command — still works in v1.5
miie analyze /path/to/repo --window-strategy commit --window-size 100

# v1.5 additions — new options
miie analyze /path/to/repo --observation-store ./obs_store.json  # persist observations
miie analyze /path/to/repo --extraction-detail full               # verbose extraction
```

---

## 27. Migration Strategy

### 27.1 Migration Approach

**Adaptive migration:** The Observation Engine runs alongside the existing extraction pipeline. Detectors receive data from whichever source is available.

```
v1.0 Path: CLI → Extraction → MetricDataFrame → Detectors
v1.5 Path: CLI → Observation Engine → Adapter → MetricDataFrame → Detectors
```

### 27.2 Migration Steps

1. **Phase 1:** Implement Observation Engine alongside existing extraction
2. **Phase 2:** Route pipeline through Observation Engine + adapter
3. **Phase 3:** Verify all 730 tests pass with new data path
4. **Phase 4:** Remove old extraction path (after verification)
5. **Phase 5:** Update documentation and benchmarks

### 27.3 Rollback Plan

If the Observation Engine causes issues:
1. Disable Observation Engine flag
2. Fall back to v1.0 extraction path
3. All detectors receive aggregated data as before
4. No data loss (both paths produce valid MetricDataFrame)

### 27.4 Backward Compatibility Guarantee

- Existing CLI commands produce identical output format
- Existing config files work without modification
- Existing report formats are preserved
- Existing benchmark suites remain valid
- New data improves accuracy but does not change interface

---

## 28. Repository Compatibility

### 28.1 Supported Repository Types

| Type | Support Level | Notes |
|------|--------------|-------|
| Git (local) | Full | Primary use case |
| GitHub (remote) | Full | Via GitURLParser + clone |
| GitLab (remote) | Partial | Via generic Git URL |
| Mercurial | None | Not supported |
| SVN | None | Not supported |

### 28.2 Repository Size Limits

| Metric | Minimum | Recommended | Maximum |
|--------|---------|-------------|---------|
| Total commits | 10 | 100+ | 100,000+ |
| Contributors | 1 | 5+ | 500+ |
| Time span | 7 days | 90+ days | 10+ years |
| File count | 1 | 50+ | 100,000+ |

### 28.3 Data Availability Matrix

| Metric | Git Native | GitHub API | PR Export | Issue Export |
|--------|-----------|------------|-----------|--------------|
| M-01 | No (needs CI) | No | No | No |
| M-02 | Yes | Yes | No | No |
| M-03 | No | Yes | Yes | No |
| M-04 | No | Yes | Yes | No |
| M-05 | No | Yes | No | Yes |
| M-06 | Yes | Yes | No | No |
| M-07 | Yes (needs tools) | No | No | No |

---

## 29. Performance Targets

### 29.1 Extraction Performance

| Repository Size | Target Extraction Time | Target Memory |
|----------------|----------------------|---------------|
| 100 commits | < 5 seconds | < 100 MB |
| 1,000 commits | < 30 seconds | < 500 MB |
| 10,000 commits | < 5 minutes | < 2 GB |
| 100,000 commits | < 30 minutes | < 8 GB |

### 29.2 Storage Performance

| Operation | Target |
|-----------|--------|
| Add observation | O(1) amortized |
| Query by metric | O(log n) |
| Query by time range | O(log n + k) where k = results |
| Serialize to JSON | O(n) |
| Deserialize from JSON | O(n) |

### 29.3 Window Construction Performance

| Operation | Target |
|-----------|--------|
| Temporal windowing | O(n log n) |
| Commit-count windowing | O(n log n) |
| Observation assignment | O(n log w) where w = windows |

### 29.4 Adapter Performance

| Operation | Target |
|-----------|--------|
| to_metric_dataframe | O(n) |
| Cross-metric pairing | O(n log n) |

---

## 30. Determinism Requirements

### 30.1 Deterministic Extraction

Given the same repository state and configuration, the Observation Engine must produce identical observations:

| Factor | Deterministic? | Mechanism |
|--------|---------------|-----------|
| Commit ordering | Yes | Git SHA-based sort |
| Observation values | Yes | Computed from commit data |
| Observation IDs | Yes | SHA-256 of source metadata |
| Window assignment | Yes | Timestamp-based assignment |
| Random operations | Yes | Seed-controlled (config.seed) |

### 30.2 Non-Deterministic Factors

| Factor | Non-Deterministic? | Mitigation |
|--------|-------------------|------------|
| File system timestamps | Yes | Ignored — use git timestamps |
| Clone depth | Yes | Full clone for analysis |
| Network latency | Yes | Retry with timeout |
| External API responses | Yes | Cache and retry |

### 30.3 Reproducibility Contract

```python
# This assertion must always hold:
store_a = extract_observations(repo, config, seed=42)
store_b = extract_observations(repo, config, seed=42)
assert store_a.to_json() == store_b.to_json()  # byte-identical JSON
```

---

## 31. Reproducibility Requirements

### 31.1 Reproducibility Levels

| Level | Description | Mechanism |
|-------|-------------|-----------|
| Level 1 | Same results on same machine | Deterministic extraction |
| Level 2 | Same results across machines | Git-based data, no OS dependencies |
| Level 3 | Same results across versions | Schema versioning, format stability |
| Level 4 | Same results with different tools | Tool-independent extraction |

### 31.2 Reproducibility Artifacts

| Artifact | Content | Purpose |
|----------|---------|---------|
| Observation store JSON | All observations | Re-run detectors without re-extraction |
| Config hash | SHA-256 of configuration | Verify same parameters |
| Seed | Random seed | Reproducible sampling |
| Dependency hash | SHA-256 of dependencies | Verify same libraries |

### 31.3 Reproducibility Verification

```python
def verify_reproducibility(
    repo_path: str,
    config: Config,
    store_path: str,
) -> bool:
    """
    Verify that stored observations match fresh extraction.
    
    1. Load stored observations
    2. Re-extract from repository
    3. Compare observation counts, values, and IDs
    4. Return True if identical
    """
```

---

## 32. Failure Recovery

### 32.1 Failure Modes

| Failure | Probability | Impact | Recovery |
|---------|-------------|--------|----------|
| Git clone fails | LOW | Analysis cannot start | Retry, suggest shallow clone |
| Extraction timeout | MEDIUM | Partial observations | Resume from checkpoint |
| Memory exhaustion | LOW | Analysis aborts | Reduce window count |
| Invalid observation | LOW | Skip observation | Log warning, continue |
| JSON serialization fails | VERY LOW | No persistent store | Log error, continue in-memory |

### 32.2 Checkpoint Strategy

```python
@dataclass
class ExtractionCheckpoint:
    """Checkpoint for resuming interrupted extraction."""
    
    repo_id: str
    last_extracted_commit: str
    observation_count: int
    extraction_phase: str  # "commits", "coverage", "reviews", "issues", "complexity"
    timestamp: str
```

### 32.3 Recovery Procedure

1. Load checkpoint from disk
2. Resume extraction from `last_extracted_commit`
3. Merge new observations with existing store
4. Continue extraction pipeline
5. Update checkpoint after each phase

---

## 33. Scalability Strategy

### 33.1 Vertical Scaling

| Resource | Current | v1.5 Target | Strategy |
|----------|---------|-------------|----------|
| Memory | 2 GB | 8 GB | Streaming extraction |
| CPU | 1 core | 4 cores | Parallel extractors |
| Disk | 1 GB | 10 GB | Optional observation persistence |

### 33.2 Horizontal Scaling

For v1.5, horizontal scaling is NOT a goal. The system operates on a single repository at a time.

### 33.3 Streaming Extraction

For large repositories, observations are extracted in batches:

```python
def extract_streaming(
    repo_path: str,
    batch_size: int = 1000,
) -> Iterator[List[Observation]]:
    """Extract observations in batches to manage memory."""
    for commit_batch in get_commit_batches(repo_path, batch_size):
        yield extract_observations_from_commits(commit_batch)
```

---

## 34. Security Considerations

### 34.1 Data Sensitivity

| Data | Sensitivity | Handling |
|------|-------------|----------|
| Commit messages | LOW | Stored as metadata |
| Author names | MEDIUM | Stored as metadata, filtered if --exclude-bots |
| File contents | HIGH | NOT extracted — only metrics |
| API tokens | CRITICAL | Never stored, loaded from .env only |
| Repository paths | LOW | Filtered from output unless --forensic |

### 34.2 Token Handling

```python
# Token priority:
# 1. --auth-token CLI argument
# 2. GITHUB_TOKEN environment variable
# 3. .env file (via python-dotenv)

# Token is NEVER:
# - Stored in observation metadata
# - Written to observation store JSON
# - Included in evidence packages
# - Logged in debug output
```

### 34.3 Observation Store Security

The observation store contains no secrets. It contains:
- Commit SHAs (public in most repos)
- Metric values (derived from public data)
- Timestamps (from git log)
- Author names (from git log)

---

## 35. Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| R-1 | Observation count too large for memory | MEDIUM | HIGH | Streaming extraction, disk-backed store |
| R-2 | Extraction too slow for large repos | MEDIUM | MEDIUM | Parallel extraction, caching |
| R-3 | Non-deterministic extraction | LOW | HIGH | Seed-controlled operations, sorted outputs |
| R-4 | Backward incompatibility | LOW | HIGH | Adapter layer, comprehensive testing |
| R-5 | Detector accuracy regression | LOW | MEDIUM | Benchmark validation, A/B testing |
| R-6 | Storage format instability | LOW | MEDIUM | Schema versioning, backward compatibility |
| R-7 | Cross-platform inconsistency | MEDIUM | LOW | Path normalization, UTF-8 encoding |
| R-8 | External API rate limiting | MEDIUM | LOW | Caching, retry with backoff |
| R-9 | Insufficient sample size for small repos | HIGH | MEDIUM | Graceful degradation, warning messages |
| R-10 | Observation ID collisions | VERY LOW | LOW | SHA-256, 128-bit IDs |

---

## 36. Trade-off Analysis

### 36.1 Granularity vs. Storage

| Choice | Granularity | Storage | Performance | Detector Compatibility |
|--------|-------------|---------|-------------|----------------------|
| Commit-level | Per-commit | LOW | HIGH | HIGH |
| File-level | Per-file | HIGH | MEDIUM | MEDIUM |
| Hunk-level | Per-hunk | VERY HIGH | LOW | LOW |

**Decision:** Commit-level. Optimal balance of granularity, storage, and compatibility.

### 36.2 Memory vs. Persistence

| Choice | Memory Usage | Reproducibility | Startup Time |
|--------|-------------|-----------------|--------------|
| In-memory only | HIGH | LOW (must re-extract) | LOW |
| Disk-backed | LOW | HIGH (persisted) | MEDIUM |
| Hybrid | MEDIUM | HIGH | LOW |

**Decision:** Hybrid. In-memory primary with optional disk persistence.

### 36.3 Compatibility vs. Innovation

| Choice | Compatibility | Innovation | Migration Cost |
|--------|---------------|------------|----------------|
| Full adapter | HIGH | LOW | LOW |
| New interface | LOW | HIGH | HIGH |
| Gradual migration | MEDIUM | MEDIUM | MEDIUM |

**Decision:** Full adapter for v1.5. New interfaces in v2.0.

### 36.4 Determinism vs. Performance

| Choice | Determinism | Performance | Complexity |
|--------|-------------|-------------|------------|
| Fully deterministic | HIGH | MEDIUM | HIGH |
| Mostly deterministic | MEDIUM | HIGH | LOW |
| Seed-controlled | HIGH | HIGH | MEDIUM |

**Decision:** Seed-controlled. Deterministic for same seed, performant for parallel extraction.

---

## 37. Acceptance Criteria

### 37.1 Functional Criteria

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-1 | Each commit produces M-02 and M-06 observations | Unit test |
| AC-2 | Observation count per metric per window ≥ 10 for repos with 100+ commits | Integration test |
| AC-3 | D-01 executes KS test (not skipped) on observation data | Unit test |
| AC-4 | D-02 computes Pearson r on paired observations | Unit test |
| AC-5 | D-03 performs bootstrap on observation data | Unit test |
| AC-6 | Adapter produces valid MetricDataFrame from observations | Unit test |
| AC-7 | All 730 existing tests pass | Test suite |
| AC-8 | Observation IDs are deterministic for same input | Unit test |
| AC-9 | Serialization produces identical JSON for same observations | Unit test |
| AC-10 | CLI output format unchanged | Integration test |

### 37.2 Non-Functional Criteria

| ID | Criterion | Target |
|----|-----------|--------|
| NFC-1 | Extraction time for 1000-commit repo | < 30 seconds |
| NFC-2 | Memory usage for 1000-commit repo | < 500 MB |
| NFC-3 | Observation store query time | < 1ms per query |
| NFC-4 | Adapter translation time | < 100ms |
| NFC-5 | JSON serialization of 10K observations | < 1 second |

### 37.3 Scientific Criteria

| ID | Criterion | Verification |
|----|-----------|-------------|
| SC-1 | D-01 KS test produces valid p-values | Statistical validation |
| SC-2 | D-02 Pearson r in [-1, 1] range | Statistical validation |
| SC-3 | D-03 bootstrap CI coverage ≥ 90% | Simulation study |
| SC-4 | Cross-metric correlation computed on matched pairs | Unit test |
| SC-5 | Temporal ordering preserved in observations | Unit test |

---

## 38. Success Metrics

### 38.1 Quantitative Metrics

| Metric | v1.0 Value | v1.5 Target | Measurement |
|--------|-----------|-------------|-------------|
| D-01 execution rate | 0% (always skipped) | 100% | % of analyses where D-01 runs |
| D-02 execution rate | 0% (n=1) | 100% | % of analyses where D-02 runs |
| D-03 execution rate | ~0% (degenerate) | 100% | % of analyses where D-03 runs |
| Mean observations per window | 1 | 50+ | Average N across metrics |
| Benchmark accuracy (D-01) | P=0.89 R=0.94 | P≥0.85 R≥0.90 | Benchmark suite results |
| Benchmark accuracy (D-02) | P=0.82 R=0.90 | P≥0.80 R≥0.85 | Benchmark suite results |
| Benchmark accuracy (D-03) | P=0.90 R=0.90 | P≥0.90 R≥0.90 | Benchmark suite results |

### 38.2 Qualitative Metrics

| Metric | Measurement |
|--------|-------------|
| Detector output interpretability | User study with 5 researchers |
| Scientific validity | Peer review of statistical methods |
| Code maintainability | Static analysis metrics |
| Documentation completeness | 100% public API documented |

---

## 39. Future Evolution

### 39.1 v1.6 Extensions

| Feature | Description | Dependencies |
|---------|-------------|-------------|
| File-level observations | Per-file metric extraction | Observation Engine |
| Developer-event observations | Per-developer behavior tracking | Identity resolution |
| Adaptive thresholds | Per-repo calibration | Observation history |
| Cross-repo comparison | Batch analysis | Workspace management |

### 39.2 v2.0 Capabilities

| Feature | Description | Dependencies |
|---------|-------------|-------------|
| Observation Engine v2 | Persistent, queryable store | Database backend |
| Real-time monitoring | Continuous observation | Streaming pipeline |
| Causal inference | Directed dependency analysis | Cross-metric observations |
| ML-based detectors | Anomaly detection models | Training data from observations |
| Web dashboard | Interactive observation explorer | API expansion |

### 39.3 Deprecation Path

| Feature | v1.5 | v1.6 | v2.0 |
|---------|------|------|------|
| MetricDataFrame (aggregated) | Supported via adapter | Deprecated | Removed |
| Single-value extraction | Supported as fallback | Removed | N/A |
| In-memory store only | Default | Optional disk | Database |

---

## 40. Decision Log

| ID | Decision | Date | Rationale |
|----|----------|------|-----------|
| D-01 | Commit-level observation granularity | 2026-06-29 | Best balance of sample size, storage, and compatibility |
| D-02 | Hybrid commit-file model | 2026-06-29 | Commit-level primary with file metadata for extensibility |
| D-03 | In-memory store with optional persistence | 2026-06-29 | Performance primary, reproducibility secondary |
| D-04 | Adapter layer for backward compatibility | 2026-06-29 | Existing detectors work unchanged |
| D-05 | Deterministic observation IDs | 2026-06-29 | Reproducibility without UUID randomness |
| D-06 | Seed-controlled extraction | 2026-06-29 | Deterministic results for same seed |
| D-07 | Parallel extractor execution | 2026-06-29 | Performance for multi-metric extraction |
| D-08 | Temporal windowing as default | 2026-06-29 | Most general, works for all repos |
| D-09 | Minimum 10 observations per window | 2026-06-29 | Statistical test power requirement |
| D-10 | JSON serialization for reproducibility | 2026-06-29 | Human-readable, tool-independent format |

---

## 41. Open Questions

| ID | Question | Impact | Owner | Target Date |
|----|----------|--------|-------|-------------|
| Q-1 | Should the observation store support lazy extraction? | Performance | Engineering | v1.5-alpha |
| Q-2 | How should we handle repositories with < 50 commits? | Graceful degradation | Science | v1.5-beta |
| Q-3 | Should M-01 (coverage) use CI API integration? | Data quality | Engineering | v1.5-rc |
| Q-4 | What is the maximum observation count before performance degrades? | Scalability | Engineering | v1.5-beta |
| Q-5 | Should the adapter support streaming (chunked) translation? | Memory | Engineering | v1.5-alpha |
| Q-6 | How should we validate cross-metric correlation results? | Scientific validity | Science | v1.5-rc |
| Q-7 | Should observation metadata include diff hunks? | Granularity | Science | v2.0 |
| Q-8 | What is the optimal batch size for streaming extraction? | Performance | Engineering | v1.5-beta |

---

## 42. Appendix

### 42.1 Glossary

| Term | Definition |
|------|-----------|
| Observation | A single data point extracted from a repository source |
| ObservationStore | In-memory container for observations with indexing |
| ObservationWindow | A collection of observations within a time/commit window |
| Adapter Layer | Translation shim between Observation Engine and legacy detectors |
| MetricDataFrame | v1.0 data container (aggregated values, replaced by observations) |
| Deterministic extraction | Same input produces same output, always |
| Seed-controlled | Random operations use a fixed seed for reproducibility |

### 42.2 Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| RELEASE_BASELINE.md | docs/architecture/ | v1.0.1 baseline definition |
| V1_5_DEVELOPMENT_ENTRY.md | docs/roadmap/ | v1.5 development plan |
| BASELINE_CHANGE_POLICY.md | docs/governance/ | Change management rules |
| PRD (this document) | docs/architecture/observation_engine/ | Observation Engine specification |

### 42.3 Schema Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-29 | Initial PRD |

---

*End of Document*
