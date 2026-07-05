# Observation Lifecycle Specification — MIIE v1.6

**Document ID:** OBS-LIFECYCLE-v1.6  
**Status:** Draft  
**Version:** 1.6.0  
**Last Updated:** 2026-07-03  
**Scope:** End-to-end observation flow from data ingestion to explanation output  

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
2. [Pipeline Architecture Overview](#2-pipeline-architecture-overview)
3. [Stage 1: Extraction](#3-stage-1-extraction)
4. [Stage 2: Transformation](#4-stage-2-transformation)
5. [Stage 3: Detection](#5-stage-3-detection)
6. [Stage 4: Scoring](#6-stage-4-scoring)
7. [Stage 5: Evidence](#7-stage-5-evidence)
8. [Stage 6: Explanation](#8-stage-6-explanation)
9. [Stage 7: Reporting](#9-stage-7-reporting)
10. [State Transition Diagrams](#10-state-transition-diagrams)
11. [Error Recovery Strategies](#11-error-recovery-strategies)
12. [Provenance Tracking](#12-provenance-tracking)
13. [Quality Assurance Checkpoints](#13-quality-assurance-checkpoints)
14. [Cross-References](#14-cross-references)

---

## 1. Purpose and Scope

This document specifies the complete lifecycle of an observation through the MIIE pipeline. An observation is the atomic unit of data in MIIE — a single measurement extracted from a monitored system, validated against schema rules, and carried through detection, scoring, evidence construction, and explanation generation.

**Scope:** Covers all data flows, state transitions, error recovery paths, and provenance tracking from provider extraction through final report output.

**Invariants:**

- Every observation carries a unique identifier (`observation_id`) for traceability across all stages.
- Every state transition is recorded with a timestamp and stage identifier.
- Observations are immutable after creation; quality corrections produce new observation records with `parent_observation_id` references.
- No stage may silently discard observations; discards must be logged and attributed.

---

## 2. Pipeline Architecture Overview

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌───────────┐
│  Stage 1    │───▶│   Stage 2    │───▶│   Stage 3   │───▶│  Stage 4  │
│ Extraction  │    │ Transformation│    │  Detection  │    │  Scoring  │
└─────────────┘    └──────────────┘    └─────────────┘    └───────────┘
                                                                  │
┌─────────────┐    ┌──────────────┐    ┌─────────────┐          │
│  Stage 7    │◀───│   Stage 6    │◀───│   Stage 5   │◀─────────┘
│  Reporting  │    │  Explanation │    │   Evidence  │
└─────────────┘    └──────────────┘    └─────────────┘
```

### Stage Summary

| Stage | Entry Point | Primary Input | Primary Output | Key Class |
|-------|------------|---------------|----------------|-----------|
| 1. Extraction | `ExtractionEngine.create_observations()` | Repository / data source | `ObservationCollection` | `RepositoryIngestionEngine` |
| 2. Transformation | `MetricExtractor.transform(observation_collection)` | `ObservationCollection` | `MetricDataFrame` | `MetricExtractor` |
| 3. Detection | `DetectorDispatcherEngine.detect_observations(windows)` | `MetricDataFrame` (windowed) | `DetectorResults` | `DetectorDispatcherEngine` |
| 4. Scoring | `ScoringEngine.score(detection_results)` | `DetectorResults` | `ScorePackage` | `ScoringEngine` |
| 5. Evidence | `EvidenceEngine.build(score_package)` | `ScorePackage` | `EvidencePackage` | `EvidenceEngine` |
| 6. Explanation | `ExplanationEngine.generate(evidence_package)` | `EvidencePackage` | `ExplanationReport` | `ExplanationEngine` |
| 7. Reporting | `explain()` CLI / API endpoint | `ExplanationReport` | Formatted output (JSON, text, etc.) | CLI / API handler |

---

## 3. Stage 1: Extraction

### 3.1 Purpose

Ingests raw data from configured providers, validates repository identity, parses source records (e.g., git logs), and produces a collection of typed observations.

### 3.2 Entry Point

```python
ExtractionEngine.create_observations(
    source_config: SourceConfig,
    window_segmentation: WindowSegmentation
) -> ObservationCollection
```

### 3.3 Process

1. **Repository Validation** — `RepositoryIngestionEngine` confirms the source repository is recognized and accessible. Validation checks:
   - Repository URL resolves.
   - Authentication credentials are valid (if required).
   - Repository type matches the expected provider type (git, API, etc.).
   - Repository is not in a banned/excluded list.

2. **Provider Dispatch** — Based on `source_config.provider_type`, the engine selects the appropriate data provider (e.g., `GitCommitProvider`). Provider resolution follows the fallback chain defined in the provider registry.

3. **Raw Record Extraction** — The provider queries the data source within the boundaries defined by `window_segmentation`. For git, this is `git log --format=...` between commit SHAs. For APIs, this is paginated query within time bounds.

4. **Record Validation** — Each raw record is validated against the provider's schema. Invalid records (malformed, missing required fields, type mismatches) are logged and excluded. Partial records proceed with NULL sentinel values for missing optional fields.

5. **Observation Construction** — Valid records are converted to `Observation` objects:

```
Observation:
  observation_id: UUID (generated)
  provider_id: str
  metric_id: str (derived from provider + record type)
  source_timestamp: datetime (from record)
  extraction_timestamp: datetime (UTC now)
  window_id: str (assigned by WindowSegmentationEngine)
  value: Any (raw extracted value)
  quality_state: QualityState (COMPLETE | MISSING | ESTIMATED | DERIVED)
  parent_observation_id: UUID | None
  metadata: dict (provider-specific provenance fields)
```

6. **Collection Assembly** — Observations are grouped into an `ObservationCollection`:

```
ObservationCollection:
  collection_id: UUID
  source_config: SourceConfig
  window_segmentation: WindowSegmentation
  observations: list[Observation]
  extraction_summary: ExtractionSummary
```

### 3.4 Output

| Field | Type | Description |
|-------|------|-------------|
| `collection_id` | UUID | Unique identifier for this extraction run |
| `observations` | `list[Observation]` | All extracted observations with assigned window IDs |
| `extraction_summary.providers_used` | `list[str]` | Providers that successfully extracted data |
| `extraction_summary.providers_failed` | `list[str]` | Providers that failed (with failure reasons) |
| `extraction_summary.total_records` | `int` | Total raw records examined |
| `extraction_summary.valid_records` | `int` | Records that passed validation |
| `extraction_summary.invalid_records` | `int` | Records excluded by validation |
| `extraction_summary.observations_created` | `int` | Observations added to collection |

### 3.5 Quality Checkpoints

- **CP-E1:** Every observation must have a non-null `observation_id`, `metric_id`, and `source_timestamp`.
- **CP-E2:** `quality_state` must be set at construction time; defaults to `COMPLETE` for valid records, `ESTIMATED` for inferred values.
- **CP-E3:** `extraction_timestamp` must be within 60 seconds of actual extraction time (clock skew guard).

---

## 4. Stage 2: Transformation

### 4.1 Purpose

Converts the flat `ObservationCollection` into a structured `MetricDataFrame` that groups observations by metric and time window, preparing data for detector consumption.

### 4.2 Entry Point

```python
MetricExtractor.transform(
    observation_collection: ObservationCollection
) -> MetricDataFrame
```

### 4.3 Process

1. **Grouping** — Observations are grouped by `(metric_id, window_id)`. Each group becomes a cell in the `MetricDataFrame`.

2. **Aggregation** — Within each group, observations are aggregated according to the metric's aggregation rule:
   - **latest** — Most recent observation by `source_timestamp`.
   - **sum** — Sum of all observation values.
   - **mean** — Arithmetic mean of observation values.
   - **count** — Count of observations in group.
   - **custom** — Provider-specific aggregation function.

3. **Window Population** — The `MetricDataFrame` is a matrix indexed by `window_id` and `metric_id`. Empty cells are filled with `NaN` (not zero).

4. **Type Coercion** — Values are coerced to the metric's declared type (`float`, `int`, `bool`, `categorical`). Coercion failures produce `NaN` and are logged.

5. **Metadata Propagation** — Each cell retains a reference to the originating `observation_id`s for provenance tracking.

### 4.4 Output

```
MetricDataFrame:
  frame_id: UUID
  collection_id: UUID (references extraction stage)
  windows: list[Window]
  metrics: list[MetricDefinition]
  data: dict[tuple[str, str], DataCell]  # (window_id, metric_id) -> DataCell
  transformation_log: list[TransformEvent]
```

```
DataCell:
  value: float | int | bool | str | None
  observation_ids: list[UUID]  # contributing observation IDs
  aggregation_method: str
  type_coerced: bool
  nan_filled: bool
```

### 4.5 Quality Checkpoints

- **CP-T1:** Every `(window_id, metric_id)` pair present in `observation_collection` must exist in the `MetricDataFrame`, even if value is `NaN`.
- **CP-T2:** `observation_ids` in each `DataCell` must be non-empty for non-`NaN` values.
- **CP-T3:** `type_coerced` must be `False` for values that did not require coercion.

---

## 5. Stage 3: Detection

### 5.1 Purpose

Runs statistical detectors against windowed metric data to identify anomalies, trends, and patterns. Produces structured detection results with per-detector scores and classifications.

### 5.2 Entry Point

```python
DetectorDispatcherEngine.detect_observations(
    windows: list[Window],
    metric_frame: MetricDataFrame
) -> DetectorResults
```

### 5.3 Process

1. **Window Preparation** — The dispatcher iterates over all windows from `WindowSegmentationEngine`. For each window:
   - Checks if the window is `SUFFICIENT` (meets detector minimum observation count).
   - If `INSUFFICIENT`, assigns `PARTIAL` or `SKIPPED` status based on observation availability.

2. **Detector Validation** — For each detector in the configured set:
   - Validates that the detector's required metrics are present in the `MetricDataFrame`.
   - Validates minimum sample size (`min_observations`) is met.
   - Validates data types match detector expectations.

3. **Statistical Test Execution** — Each validated detector runs its statistical test on the windowed data:
   - **d_01 (commit message anomaly):** Checks commit message entropy, length distribution, pattern deviations.
   - **d_02 (temporal anomaly):** Checks commit timing distribution, burst detection, idle period detection.
   - **d_03 (metric anomaly):** Checks metric value distributions against historical baselines.
   - Additional detectors as configured.

4. **Result Construction** — Each detector produces a result object:

```
DetectorResult:
  detector_id: str
  window_id: str
  classification: str (ANOMALY | NORMAL | INCONCLUSIVE | SKIPPED)
  score: float | None  # 0.0-1.0, None for SKIPPED
  confidence: float | None  # 0.0-1.0, None for SKIPPED
  test_statistic: float | None
  p_value: float | None
  observations_used: int
  observations_excluded: int
  exclusion_reasons: list[str]
  warning: str | None
  timestamp: datetime
```

5. **Result Assembly** — All detector results are collected into `DetectorResults`.

### 5.4 Output

```
DetectorResults:
  results_id: UUID
  frame_id: UUID (references transformation stage)
  results: dict[str, dict[str, DetectorResult]]  # (detector_id, window_id) -> result
  detectors_run: list[str]
  detectors_skipped: list[str]
  windows_analyzed: int
  windows_skipped: int
  summary: DetectionSummary
```

### 5.5 Quality Checkpoints

- **CP-D1:** `classification` must be one of: `ANOMALY`, `NORMAL`, `INCONCLUSIVE`, `SKIPPED`.
- **CP-D2:** If `classification` is `SKIPPED`, `score` and `confidence` must be `None`.
- **CP-D3:** `observations_used` must be ≥ 1 for non-SKIPPED results.
- **CP-D4:** `p_value` must be in range [0.0, 1.0] when present.

---

## 6. Stage 4: Scoring

### 6.1 Purpose

Computes composite integrity and confidence scores from detection results. The Integrity Score (IS) reflects the overall anomaly level; the Confidence Score (CS) reflects how reliable the IS value is given available data.

### 6.2 Entry Point

```python
ScoringEngine.score(
    detection_results: DetectorResults
) -> ScorePackage
```

### 6.3 Process

1. **Detector Weight Resolution** — Each detector is assigned a weight based on its configured priority and the number of windows it successfully analyzed. Weights are normalized to sum to 1.0 across all detectors with results.

2. **Per-Detector Scoring** — For each detector with valid results:
   - Aggregate scores across windows (weighted by window size).
   - Compute detector-level IS contribution and CS contribution.

3. **Integrity Score (IS) Computation:**

```
IS = Σ(detector_weight_i × detector_score_i) / Σ(detector_weight_i)
```

   - Range: [0.0, 1.0]
   - Interpretation: 0.0 = severe anomaly, 1.0 = fully intact
   - If no detectors produced valid results: IS = 1.0 (no anomalies detected)

4. **Confidence Score (CS) Computation:**

```
CS = Σ(detector_weight_i × detector_confidence_i × windows_analyzed_i / windows_total_i) / Σ(detector_weight_i)
```

   - Range: [0.0, 1.0]
   - Interpretation: 0.0 = no confidence, 1.0 = full confidence
   - If no detectors produced valid results: CS = 0.0 (no confidence)
   - CS is penalized for missing detectors, skipped windows, and low observation counts.

5. **Anomaly Level Classification:**

| IS Range | Classification |
|----------|---------------|
| 0.0 – 0.3 | CRITICAL |
| 0.3 – 0.6 | WARNING |
| 0.6 – 0.8 | NOTICE |
| 0.8 – 1.0 | CLEAR |

### 6.4 Output

```
ScorePackage:
  score_id: UUID
  results_id: UUID (references detection stage)
  integrity_score: float  # [0.0, 1.0]
  confidence_score: float  # [0.0, 1.0]
  anomaly_level: str  # CRITICAL | WARNING | NOTICE | CLEAR
  detector_scores: dict[str, DetectorScore]
  computation_timestamp: datetime
  score_rationale: str  # human-readable computation summary
```

```
DetectorScore:
  detector_id: str
  weight: float
  score: float
  confidence: float
  windows_analyzed: int
  windows_total: int
  contribution_to_is: float
```

### 6.5 Quality Checkpoints

- **CP-S1:** `integrity_score` must be in range [0.0, 1.0].
- **CP-S2:** `confidence_score` must be in range [0.0, 1.0].
- **CP-S3:** `anomaly_level` must match the IS range classification table.
- **CP-S4:** Sum of `detector_scores[*].weight` must equal 1.0 (within floating-point tolerance 1e-9).
- **CP-S5:** If `confidence_score < 0.3`, the `score_rationale` must explicitly state low-confidence conditions.

---

## 7. Stage 5: Evidence

### 7.1 Purpose

Constructs an evidence chain that links scoring results back to the original observations. Provides provenance and supporting details for the explanation stage.

### 7.2 Entry Point

```python
EvidenceEngine.build(
    score_package: ScorePackage
) -> EvidencePackage
```

### 7.3 Process

1. **Evidence Item Construction** — For each detector with results:
   - Create an evidence item containing the detection result, contributing observations, and scoring contribution.
   - Attach observation-level references with extraction provenance.

2. **Observation Reference Assembly** — For each observation referenced by detection results:
   - Record `observation_id`, `metric_id`, `window_id`, `quality_state`, `provider_id`, `source_timestamp`.
   - Record the detection context: which detector consumed it, what role it played.

3. **Provenance Chain** — Each evidence item links:
   - `extraction_run_id` → Stage 1 extraction collection
   - `transformation_run_id` → Stage 2 metric frame
   - `detection_run_id` → Stage 3 detector results
   - `scoring_run_id` → Stage 4 score package

4. **Evidence Validation** — Validates that all referenced observations exist and that provenance links are unbroken. Broken links are flagged but do not block pipeline execution.

### 7.4 Output

```
EvidencePackage:
  evidence_id: UUID
  score_id: UUID (references scoring stage)
  evidence_items: list[EvidenceItem]
  observation_references: dict[UUID, ObservationReference]
  provenance_chain: ProvenanceChain
  validation_warnings: list[str]
```

```
EvidenceItem:
  item_id: UUID
  detector_id: str
  classification: str
  score: float
  confidence: float
  observation_ids: list[UUID]
  supporting_data: dict
  rationale: str
```

```
ObservationReference:
  observation_id: UUID
  metric_id: str
  window_id: str
  quality_state: str
  provider_id: str
  source_timestamp: datetime
  extraction_timestamp: datetime
  role_in_detection: str  # e.g., "input", "baseline", "excluded"
```

### 7.5 Quality Checkpoints

- **CP-V1:** Every `EvidenceItem` must reference at least one `observation_id` that exists in `observation_references`.
- **CP-V2:** `provenance_chain` must contain non-null references for all four run IDs when the full pipeline executed.
- **CP-V3:** `validation_warnings` must be empty for a clean evidence chain; non-empty warrants review.

---

## 8. Stage 6: Explanation

### 8.1 Purpose

Generates a human-readable narrative from the evidence chain, translating statistical results and scores into actionable findings and recommendations.

### 8.2 Entry Point

```python
ExplanationEngine.generate(
    evidence_package: EvidencePackage
) -> ExplanationReport
```

### 8.3 Process

1. **Finding Extraction** — Rule-based extraction of findings from evidence items:
   - Each detector result with `classification = ANOMALY` or `classification = INCONCLUSIVE` produces a finding.
   - Findings are ordered by severity (ANOMALY > INCONCLUSIVE > NORMAL).
   - Duplicate findings (same detector, same type across windows) are deduplicated with occurrence counts.

2. **Recommendation Generation** — Each finding maps to one or more recommendations via the recommendation rule table. Recommendations are prioritized by anomaly level and detector weight.

3. **Confidence Narrative** — A narrative paragraph explaining the overall confidence level:
   - High confidence (CS ≥ 0.7): "The analysis is based on sufficient data across all monitored metrics."
   - Medium confidence (0.3 ≤ CS < 0.7): "Some monitoring windows had insufficient data; results should be interpreted with caution."
   - Low confidence (CS < 0.3): "Data availability is limited; findings may not represent the full picture."

4. **Executive Summary** — A concise summary including:
   - Anomaly level and scores.
   - Number and severity of findings.
   - Top recommendation.

### 8.4 Output

```
ExplanationReport:
  report_id: UUID
  evidence_id: UUID (references evidence stage)
  integrity_score: float
  confidence_score: float
  anomaly_level: str
  executive_summary: str
  findings: list[Finding]
  recommendations: list[Recommendation]
  confidence_narrative: str
  generated_timestamp: datetime
  explanation_version: str  # e.g., "1.6.0"
```

```
Finding:
  finding_id: UUID
  detector_id: str
  severity: str  # HIGH | MEDIUM | LOW
  title: str
  description: str
  affected_windows: list[str]
  occurrence_count: int
  evidence_item_ids: list[UUID]
```

```
Recommendation:
  recommendation_id: UUID
  finding_ids: list[UUID]
  priority: str  # IMMEDIATE | SOONER | MONITOR
  action: str
  rationale: str
```

### 8.5 Quality Checkpoints

- **CP-X1:** Every `Finding` must reference at least one `EvidenceItem` that exists in the evidence package.
- **CP-X2:** `executive_summary` must be non-empty and ≤ 500 words.
- **CP-X3:** `confidence_narrative` must match the CS range thresholds.
- **CP-X4:** Recommendations must not reference non-existent finding IDs.

---

## 9. Stage 7: Reporting

### 9.1 Purpose

Formats the `ExplanationReport` into the requested output format and delivers it to the caller.

### 9.2 Entry Points

```python
# CLI
explain(
    report_id: UUID,
    format: str  # "json" | "text" | "markdown"
) -> str

# API
GET /api/v1/reports/{report_id}?format={format}
```

### 9.3 Process

1. **Report Retrieval** — Fetches the `ExplanationReport` by `report_id`.

2. **Format Application** — Applies the requested format:
   - **json:** Full structured serialization of `ExplanationReport`.
   - **text:** Plain-text narrative with headings, findings, and recommendations.
   - **markdown:** Markdown with headers, tables, and code blocks.

3. **Output Delivery** — Returns formatted content to the caller.

### 9.4 Output

| Format | Content |
|--------|---------|
| `json` | Complete `ExplanationReport` serialized as JSON with all fields. |
| `text` | Narrative summary, numbered findings, prioritized recommendations. |
| `markdown` | Structured document with headers, tables for scores, and blockquoted findings. |

---

## 10. State Transition Diagrams

### 10.1 Observation States

```
  ┌──────────┐
  │ CREATED  │ ◄── ExtractionEngine creates observation
  └────┬─────┘
       │
       ▼
  ┌──────────┐
  │VALIDATED │ ◄── Observation passes OVR validation rules
  └────┬─────┘
       │
       ▼
  ┌──────────────┐
  │TRANSFORMED   │ ◄── Observation converted to MetricDataFrame format
  └────┬─────────┘
       │
       ▼
  ┌──────────────┐
  │ CONSUMED     │ ◄── Observation used by detector in statistical test
  └────┬─────────┘
       │
       ▼
  ┌──────────────┐
  │ SCORED       │ ◄── Observation factored into IS/CS computation
  └────┬─────────┘
       │
       ▼
  ┌──────────────┐
  │ EXPLAINED    │ ◄── Observation included in narrative explanation
  └──────────────┘
```

**Transition Rules:**

| From | To | Condition |
|------|-----|-----------|
| CREATED | VALIDATED | Observation passes all OVR validation rules for its metric type |
| CREATED | (discarded) | Observation fails validation; logged and excluded |
| VALIDATED | TRANSFORMED | MetricExtractor includes observation in MetricDataFrame |
| TRANSFORMED | CONSUMED | Detector includes observation in statistical test input |
| TRANSFORMED | (excluded) | Detector excludes observation (insufficient quality, wrong type); logged |
| CONSUMED | SCORED | ScoringEngine uses detection result containing this observation |
| SCORED | EXPLAINED | ExplanationEngine includes this observation in a finding or summary |
| SCORED | (not explained) | Observation does not contribute to any finding; still recorded in provenance |

### 10.2 Quality State Transitions

```
  ┌──────────┐
  │ MISSING  │ ◄── Initial state when provider cannot extract data
  └────┬─────┘
       │
       ├─── provider succeeds ──────▶ ┌──────────┐
       │                              │ COMPLETE │
       ├─── provider uses inference ──▶│          │
       │                              └──────────┘
       │
       ▼
  ┌────────────┐
  │ ESTIMATED  │ ◄── Provider uses inference or interpolation
  └────────────┘

  ┌──────────┐
  │ COMPLETE │ ◄── Observation has full data from provider
  └────┬─────┘
       │
       ├─── recomputed / derived ────▶ ┌─────────┐
       │                              │ DERIVED │
       │                              └─────────┘
       │
       ├─── data source unavailable ──▶ ┌──────────┐
       │                               │ MISSING  │
       │                               └──────────┘
```

**Transition Rules:**

| From | To | Trigger |
|------|-----|---------|
| MISSING | COMPLETE | Provider successfully extracts data from source |
| MISSING | ESTIMATED | Provider uses inference, interpolation, or default values |
| COMPLETE | DERIVED | Observation is recomputed or derived from other observations |
| COMPLETE | MISSING | Data source becomes unavailable or returns empty |
| ESTIMATED | COMPLETE | Provider re-extracts and gets actual data |
| ESTIMATED | MISSING | Data source becomes unavailable |
| DERIVED | MISSING | Upstream observations become unavailable |

### 10.3 Window States

```
  ┌──────────┐
  │ DEFINED  │ ◄── WindowSegmentationEngine sets boundaries
  └────┬─────┘
       │
       ▼
  ┌──────────────┐
  │ POPULATED    │ ◄── Observations assigned to window
  └────┬─────────┘
       │
       ├─── meets minimum ──────▶ ┌─────────────┐
       │    requirements          │ SUFFICIENT  │
       │                          └──────┬──────┘
       │                                 │
       │    fails minimum ──────▶ ┌──────────────────┐
       │    requirements          │ INSUFFICIENT     │
       │                          │ (PARTIAL/SKIPPED)│
       │                          └──────────────────┘
       │
       ▼
  ┌──────────┐
  │ ANALYZED │ ◄── Detector has processed window data
  └────┬─────┘
       │
       ▼
  ┌──────────┐
  │ SCORED   │ ◄── Window results factored into IS/CS
  └──────────┘
```

**Transition Rules:**

| From | To | Condition |
|------|-----|-----------|
| DEFINED | POPULATED | At least one observation is assigned to the window |
| DEFINED | INSUFFICIENT | No observations are assigned to the window |
| POPULATED | SUFFICIENT | Observation count ≥ detector's `min_observations` threshold |
| POPULATED | INSUFFICIENT | Observation count < detector's `min_observations` threshold |
| INSUFFICIENT | POPULATED | Additional observations arrive, meeting minimum |
| SUFFICIENT | ANALYZED | Detector completes statistical test on window |
| ANALYZED | SCORED | ScoringEngine incorporates window results |

---

## 11. Error Recovery Strategies

### 11.1 Provider Failures

| Scenario | Recovery | Impact on Window |
|----------|----------|-----------------|
| Primary provider fails | Fallback provider executes | None if fallback succeeds |
| All providers fail | Window marked `SKIPPED` | All observations in window: `quality_state = MISSING` |
| Partial provider failure | Successful providers contribute | Window marked `PARTIAL` with available observations |
| Provider timeout | Retry with exponential backoff (max 3 retries) | None if retry succeeds |
| Provider returns empty data | Window receives zero observations | Window: `INSUFFICIENT` |

**Fallback Chain:**
```
Primary Provider → Fallback Provider 1 → Fallback Provider 2 → (fail)
```

Each fallback must be of the same provider type or an equivalent adapter.

### 11.2 Detector Failures

| Scenario | Recovery | Output |
|----------|----------|--------|
| Insufficient observations | Detector returns `None` (not an error) | `classification = SKIPPED` |
| Statistical test throws exception | Detector catches, logs, returns `None` | `classification = SKIPPED` with warning |
| Invalid data type in input | Detector excludes invalid observations, proceeds | `classification` based on remaining data |
| Detector configuration error | Engine skips detector, logs error | `classification = SKIPPED` |
| All detectors skip | Scoring uses defaults (IS = 1.0, CS = 0.0) | Pipeline continues to evidence and explanation |

**Detector Resilience Rules:**
- Detectors must never raise uncaught exceptions.
- Detectors must return `None` for any condition they cannot handle.
- `None` results are treated as `SKIPPED`, not as failures.
- All detector warnings are propagated to the `DetectorResult.warning` field.

### 11.3 Scoring Failures

| Scenario | Recovery | Output |
|----------|----------|--------|
| No detection results | IS = 1.0, CS = 0.0 | `anomaly_level = CLEAR` with low confidence |
| Partial results (some detectors skipped) | IS computed with available detectors | CS penalized proportionally to missing detectors |
| All detectors return `ANOMALY` | IS computed normally, no special case | CS based on data quality |
| Weight normalization fails (all weights zero) | Equal weights assigned to available detectors | Logged as scoring anomaly |

### 11.4 Evidence and Explanation Failures

| Scenario | Recovery | Output |
|----------|----------|--------|
| Broken provenance link | Evidence item flagged with warning | Warning included in `EvidencePackage.validation_warnings` |
| No evidence items | Empty findings, default recommendation | Report states "No anomalous conditions detected" |
| Explanation rule mismatch | Fallback to generic template | Explanation includes disclaimer about rule coverage |

---

## 12. Provenance Tracking

### 12.1 Provenance Chain

Every output artifact carries a provenance chain linking it back through the pipeline:

```
ExplanationReport
  └── evidence_id ──▶ EvidencePackage
        ├── score_id ──▶ ScorePackage
        │     └── results_id ──▶ DetectorResults
        │           └── frame_id ──▶ MetricDataFrame
        │                 └── collection_id ──▶ ObservationCollection
        └── observation_references: list[ObservationReference]
              └── Each ObservationReference links to:
                    ├── provider_id
                    ├── source_timestamp
                    ├── extraction_timestamp
                    └── quality_state history
```

### 12.2 Provenance Record Structure

```python
ProvenanceChain:
    extraction_run_id: UUID
    transformation_run_id: UUID
    detection_run_id: UUID
    scoring_run_id: UUID
    evidence_run_id: UUID
    explanation_run_id: UUID
    pipeline_version: str  # e.g., "1.6.0"
    execution_timestamp: datetime
    execution_context: dict  # environment, config hash, etc.
```

### 12.3 Traceability Requirements

- Any finding in an `ExplanationReport` must be traceable to specific detector results.
- Any detector result must be traceable to specific observations in a `MetricDataFrame`.
- Any observation in a `MetricDataFrame` must be traceable to an extraction run and source record.
- Provenance links must not be broken at any pipeline stage boundary.

---

## 13. Quality Assurance Checkpoints

### 13.1 Checkpoint Registry

| Checkpoint | Stage | Condition | Action on Failure |
|-----------|-------|-----------|-------------------|
| CP-E1 | Extraction | `observation_id`, `metric_id`, `source_timestamp` non-null | Reject observation |
| CP-E2 | Extraction | `quality_state` set at construction | Default to `COMPLETE` |
| CP-E3 | Extraction | `extraction_timestamp` within 60s of clock | Log clock skew warning |
| CP-T1 | Transformation | All `(window_id, metric_id)` pairs present | Fill missing with `NaN` |
| CP-T2 | Transformation | `observation_ids` non-empty for non-`NaN` values | Log provenance gap |
| CP-T3 | Transformation | `type_coerced` reflects actual coercion | Log coercion event |
| CP-D1 | Detection | `classification` in valid set | Reject result |
| CP-D2 | Detection | `score`/`confidence` null for SKIPPED | Enforce null constraint |
| CP-D3 | Detection | `observations_used` ≥ 1 for non-SKIPPED | Set to SKIPPED |
| CP-D4 | Detection | `p_value` in [0.0, 1.0] | Reject result |
| CP-S1 | Scoring | `integrity_score` in [0.0, 1.0] | Clamp and log |
| CP-S2 | Scoring | `confidence_score` in [0.0, 1.0] | Clamp and log |
| CP-S3 | Scoring | `anomaly_level` matches IS range | Recompute |
| CP-S4 | Scoring | Detector weights sum to 1.0 | Normalize |
| CP-S5 | Scoring | Low CS triggers rationale requirement | Generate rationale |
| CP-V1 | Evidence | Evidence items reference valid observations | Flag broken link |
| CP-V2 | Evidence | Provenance chain fully populated | Log missing links |
| CP-V3 | Evidence | Validation warnings empty | Log review required |
| CP-X1 | Explanation | Findings reference valid evidence items | Exclude invalid finding |
| CP-X2 | Explanation | Executive summary ≤ 500 words | Truncate |
| CP-X3 | Explanation | Confidence narrative matches CS | Recompute narrative |
| CP-X4 | Explanation | Recommendations reference valid findings | Exclude invalid recommendation |

### 13.2 Checkpoint Execution

- All checkpoints execute at stage boundary (after stage output, before next stage input).
- Checkpoint failures are recorded in the stage's output metadata.
- Critical checkpoints (CP-E1, CP-D1, CP-S1, CP-S2) block pipeline progression on failure.
- Advisory checkpoints (CP-E3, CP-T3, CP-V3) log warnings but do not block.

---

## 14. Cross-References

| Document | Relationship | Reference |
|----------|-------------|-----------|
| **OSMS** (Observation Schema and Metadata Specification) | Defines `Observation` schema, field types, and validation rules used in Stage 1 | OBS-SCHEMA-v1.6 |
| **OPA** (Observation Provider Adapter) | Defines provider interfaces, fallback chains, and adapter contracts used in Stage 1 | OPA-ADAPTER-v1.6 |
| **OVR** (Observation Validation Rules) | Defines validation rules applied at CP-E1 through CP-E3 in Stage 1 | OVR-RULES-v1.6 |
| **MDS** (Metric DataFrame Specification) | Defines `MetricDataFrame` structure and aggregation rules used in Stage 2 | MDS-FRAME-v1.6 |
| **DRS** (Detection Results Specification) | Defines `DetectorResults` schema and detector classification rules used in Stage 3 | DRS-RESULTS-v1.6 |
| **SCS** (Scoring Computation Specification) | Defines IS/CS formulas and anomaly level thresholds used in Stage 4 | SCS-SCORING-v1.6 |
| **ECH** (Evidence Chain Handbook) | Defines evidence item structure and provenance requirements used in Stage 5 | ECH-EVIDENCE-v1.6 |
| **EXR** (Explanation Rule Reference) | Defines finding extraction rules and recommendation mappings used in Stage 6 | EXR-RULES-v1.6 |

---

*End of Observation Lifecycle Specification v1.6*
