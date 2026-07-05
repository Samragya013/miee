# MIIE Observation Source Matrix Specification (OSMS) v1.0

| Field | Value |
|-------|-------|
| **Document ID** | OSMS-v1.0 |
| **MIIE Version** | 1.6 |
| **Status** | Canonical Specification |
| **Classification** | Internal — Engineering |
| **Last Updated** | 2026-07-03 |
| **Owner** | MIIE Core Engineering |

---

## 1. Purpose

This document defines the canonical Observation Source Matrix for MIIE v1.6. It specifies every metric, its observation sources, extraction methods, quality rules, and validation criteria. This document is the single source of truth for "what observations exist and where they come from."

All observation creation, validation, and consumption code MUST conform to the contracts defined herein. Deviations require an approved ADR referencing this document.

## 2. Scope

This specification covers:

- **M-01** through **M-07**: All metric definitions, extraction pipelines, observation field contracts, and validation rules.
- **Observation data model**: Field-level semantics for `Observation`, `ObservationCollection`, `ObservationWindow`, and `MetricDataFrame`.
- **Quality lifecycle**: State definitions, transitions, and enforcement rules for `ObservationQuality`.
- **Detector consumption contracts**: Minimum requirements, quality handling, and value semantics expected by D-01, D-02, and D-03.
- **Scoring integration**: How observations feed into Integrity Score and Confidence Score calculations.
- **Sampling readiness**: How observation completeness determines detector eligibility.

This specification does NOT cover:

- Detector algorithms (see OPA — Observation Processing Architecture).
- Scoring formulas in detail (see OPC — Observation Processing & Scoring).
- Validation framework internals (see OVR — Observation Validation Rules).

## 3. Definitions

| Term | Definition |
|------|------------|
| **Observation** | A single, immutable data point extracted from a repository source, associated with exactly one metric. |
| **Observation Window** | A time-bounded or count-bounded interval containing a set of observations used for statistical analysis. |
| **Source Type** | The origin class of an observation: COMMIT, FILE, BRANCH, or TAG. |
| **Quality State** | The completeness classification of an observation: COMPLETE, ESTIMATED, MISSING, or DERIVED. |
| **Confidence** | A float in [0.0, 1.0] representing the extraction system's certainty in the observation value. |
| **Metric ID** | A stable identifier of the form `M-XX` where XX is a two-digit metric number. |
| **Detector** | A statistical analysis module that consumes observations to detect behavioral anomalies. |

---

## 4. Metric Definitions

### 4.1 Summary Table

| Metric ID | Name | Source Type | Extractable from git alone | Quality Default | Confidence | Severity | Status |
|-----------|------|-------------|----------------------------|-----------------|------------|----------|--------|
| M-01 | Repository Metadata | COMMIT | No | DERIVED | 1.0 | 0.5 | Implemented |
| M-02 | Commit Frequency | COMMIT | Yes | COMPLETE | 1.0 | 1.0 | Implemented |
| M-03 | Code Churn | COMMIT | Partially | — | — | 1.2 | Planned |
| M-04 | Code Complexity | FILE | No | — | — | 1.5 | Planned |
| M-05 | Code Coverage | FILE | No | — | — | 2.0 | Planned |
| M-06 | Dependency Health | COMMIT | Yes | COMPLETE | 1.0 | 1.0 | Implemented |
| M-07 | Build Health | COMMIT | No | — | — | 1.8 | Planned |

**Severity**: Multiplier applied during Integrity Score calculation. Higher severity amplifies the impact of quality deficiencies for that metric.

**Status**: `Implemented` means observation extraction code exists and is operational. `Planned` means the metric is defined but has no observation creation pipeline.

### 4.2 Detection Purpose Matrix

| Metric ID | D-01 (Distribution Drift) | D-02 (Correlation Breakdown) | D-03 (Threshold Compression) |
|-----------|---------------------------|------------------------------|------------------------------|
| M-01 | — | — | — |
| M-02 | ✓ | ✓ | ✓ |
| M-03 | ✓ | — | ✓ |
| M-04 | ✓ | — | ✓ |
| M-05 | ✓ | ✓ | ✓ |
| M-06 | ✓ | ✓ | ✓ |
| M-07 | ✓ | — | ✓ |

---

## 5. Per-Metric Specification

### 5.1 M-01: Repository Metadata

| Field | Value |
|-------|-------|
| **Metric ID** | M-01 |
| **Name** | Repository Metadata |
| **Source Type** | COMMIT |
| **Extractable from git alone** | No (requires README, LICENSE file, etc.) |
| **Status** | Implemented |
| **Severity** | 0.5 (low) |

**Purpose**: Provides repository-level context for other metrics. Not a behavioral metric itself — a foundation metric.

**Extraction Pipeline**:
- Module: `RepositoryIngestionEngine`
- Method: Direct repository metadata extraction, NOT via observation creation from git log.
- Observation fields used: `author_email`, `confidence`.

**Observation Fields**:
- `source_type`: SourceType.COMMIT
- `quality`: ObservationQuality.DERIVED
- `confidence`: 1.0
- `unit`: `"repository_metadata"`

**Observation Creation**: None. M-01 is extracted directly as repository context and injected into `ObservationCollection.metadata`. It does not produce individual `Observation` records in the observation stream.

**Validation**:
- MUST have a non-empty `author_email` field.
- MUST have `confidence` ∈ [0.8, 1.0].
- Extraction MUST complete before any metric extraction that depends on repository context.

---

### 5.2 M-02: Commit Frequency

| Field | Value |
|-------|-------|
| **Metric ID** | M-02 |
| **Name** | Commit Frequency |
| **Source Type** | COMMIT |
| **Extractable from git alone** | Yes |
| **Status** | Implemented |
| **Severity** | 1.0 (normal) |

**Purpose**: Measures commit activity per author within a time window. Serves D-01 (distribution drift) and D-02 (correlation breakdown).

**Extraction Pipeline**:
- Module: `CommitExtractor`
- Git command: `git log --all --format='%H %ae %aI %s'`
- Transform: `_commit_to_observations()` creates one `Observation` per commit.
- Output: `ObservationCollection`

**Observation Fields**:

| Field | Value / Rule |
|-------|-------------|
| `observation_id` | 16-char hex, SHA-256 deterministic from content |
| `source_type` | SourceType.COMMIT |
| `source_id` | 40-char SHA of the commit |
| `metric_id` | `"M-02"` |
| `value` | `1.0` (one observation per commit; aggregation happens at window level) |
| `quality` | ObservationQuality.COMPLETE |
| `timestamp` | Author date from `git log` (`%aI`) |
| `author_email` | Author email from `git log` (`%ae`) |
| `confidence` | `1.0` |
| `unit` | `"commits"` |
| `uncertainty` | `None` |
| `relationships` | `[]` (no inter-observation relationships) |
| `metadata` | `{}` |

**Window Strategy**:
- Default: Time-based, 30-day windows (`DEFAULT_WINDOW_SIZE_DAYS = 30`).
- Alternative: Commit-count-based (configurable).
- Window boundaries are inclusive of start_date, exclusive of end_date.

**Value Semantics**: Each observation has `value = 1.0`. The `ObservationWindow` aggregates by counting observations per author. The window-level metric value is the total commit count by that author within the window.

**Quality Rules**:
- Quality is always COMPLETE for M-02 because git log is authoritative.
- If a commit has an unparseable author email, the observation is created with quality COMPLETE but `author_email` is set to `"unknown@repository"`.
- If the git command fails entirely, NO observations are returned (empty collection), not MISSING observations.

**Validation**:
- `observation.value` MUST be `1.0`.
- `observation.quality` MUST be COMPLETE.
- `observation.confidence` MUST be `1.0`.
- `observation.timestamp` MUST be a valid datetime.
- `observation.author_email` MUST be non-empty.

---

### 5.3 M-03: Code Churn

| Field | Value |
|-------|-------|
| **Metric ID** | M-03 |
| **Name** | Code Churn |
| **Source Type** | COMMIT |
| **Extractable from git alone** | Partially (file-level change counts via `git log --stat`) |
| **Status** | Planned (NOT IMPLEMENTED) |
| **Severity** | 1.2 (moderate) |

**Purpose**: Measures the rate and magnitude of code changes. Serves D-01 (distribution drift).

**Extraction Pipeline**: NOT IMPLEMENTED. When called in sampling, returns `None`.

**Planned Extraction Method**: `git diff --stat` between consecutive commits, or `git log --stat` parsing to extract per-file line change counts.

**Planned Observation Fields**:

| Field | Expected Value / Rule |
|-------|----------------------|
| `observation_id` | 16-char hex, SHA-256 deterministic |
| `source_type` | SourceType.COMMIT |
| `source_id` | 40-char SHA of the commit |
| `metric_id` | `"M-03"` |
| `value` | Total lines changed (additions + deletions) in the commit |
| `quality` | ObservationQuality.COMPLETE |
| `confidence` | 1.0 |
| `unit` | `"lines_changed"` |

**Gap**: No observation creation code exists. No `_churn_to_observations()` method.

---

### 5.4 M-04: Code Complexity

| Field | Value |
|-------|-------|
| **Metric ID** | M-04 |
| **Name** | Code Complexity |
| **Source Type** | FILE |
| **Extractable from git alone** | No (requires AST parsing of source files) |
| **Status** | Planned (NOT IMPLEMENTED) |
| **Severity** | 1.5 (high) |

**Purpose**: Measures cyclomatic or cognitive complexity of source files. Serves D-01 (distribution drift).

**Extraction Pipeline**: NOT IMPLEMENTED.

**Planned Extraction Method**: External tools (e.g., `lizard`, `radon`) for cyclomatic complexity analysis. AST parsing of source files at a point-in-time snapshot.

**Planned Observation Fields**:

| Field | Expected Value / Rule |
|-------|----------------------|
| `observation_id` | 16-char hex, SHA-256 deterministic |
| `source_type` | SourceType.FILE |
| `source_id` | 40-char SHA of the file content |
| `metric_id` | `"M-04"` |
| `value` | Complexity score (float, tool-dependent) |
| `quality` | ObservationQuality.COMPLETE |
| `confidence` | Tool-dependent (0.0–1.0) |
| `unit` | `"cyclomatic_complexity"` |

**Gap**: Needs external tool integration. No observation creation code exists.

---

### 5.5 M-05: Code Coverage

| Field | Value |
|-------|-------|
| **Metric ID** | M-05 |
| **Name** | Code Coverage |
| **Source Type** | FILE |
| **Extractable from git alone** | No (requires CI/CD pipeline data) |
| **Status** | Planned (NOT IMPLEMENTED) |
| **Severity** | 2.0 (critical) |

**Purpose**: Measures test coverage percentage per file or module. Serves D-01 (distribution drift) and D-02 (correlation breakdown).

**Extraction Pipeline**: NOT IMPLEMENTED.

**Planned Extraction Method**: CI/CD pipeline integration (Jest coverage reports, pytest-cov, lcov, Cobertura XML parsing).

**Planned Observation Fields**:

| Field | Expected Value / Rule |
|-------|----------------------|
| `observation_id` | 16-char hex, SHA-256 deterministic |
| `source_type` | SourceType.FILE |
| `source_id` | 40-char SHA of the file |
| `metric_id` | `"M-05"` |
| `value` | Coverage percentage (0.0–100.0) |
| `quality` | ObservationQuality.COMPLETE |
| `confidence` | 1.0 (CI-generated data is authoritative) |
| `unit` | `"coverage_percent"` |

**Gap**: Needs CI/CD API integration. No observation creation code exists.

---

### 5.6 M-06: Dependency Health

| Field | Value |
|-------|-------|
| **Metric ID** | M-06 |
| **Name** | Dependency Health |
| **Source Type** | COMMIT |
| **Extractable from git alone** | Yes (via file change detection on dependency manifests) |
| **Status** | Implemented |
| **Severity** | 1.0 (normal) |

**Purpose**: Measures the freshness of dependency declarations. Serves D-01 (distribution drift) and D-02 (correlation breakdown).

**Extraction Pipeline**:
- Module: `CommitExtractor._extract_dependency_health()`
- Detection: File-level commit tracking on dependency manifest files.

**Tracked Files**:
- `package.json`
- `package-lock.json`
- `yarn.lock`
- `requirements.txt`
- `Pipfile`
- `Pipfile.lock`
- `pyproject.toml`
- `Cargo.toml`
- `Cargo.lock`
- `go.mod`
- `go.sum`
- `Gemfile`
- `Gemfile.lock`
- `pom.xml`
- `build.gradle`
- `build.gradle.kts`

**Observation Fields**:

| Field | Value / Rule |
|-------|-------------|
| `observation_id` | 16-char hex, SHA-256 deterministic |
| `source_type` | SourceType.COMMIT |
| `source_id` | 40-char SHA of the commit |
| `metric_id` | `"M-06"` |
| `value` | Number of days since last change to the dependency manifest file |
| `quality` | ObservationQuality.COMPLETE |
| `confidence` | `1.0` |
| `unit` | `"days_since_update"` |
| `relationships` | `[]` |

**Value Semantics**: `observation.value` = number of days since the most recent commit that modified a tracked dependency file. A value of 0.0 means the dependency file was changed in the current window.

**Quality Rules**:
- Quality is COMPLETE because detection is based on direct file change records in git.
- If no dependency manifest files exist in the repository, the metric produces NO observations (empty collection, not MISSING).
- If a dependency file is added for the first time, the observation value is 0.0.

**Validation**:
- `observation.value` MUST be ≥ 0.0.
- `observation.quality` MUST be COMPLETE.
- `observation.confidence` MUST be 1.0.
- `observation.source_type` MUST be SourceType.COMMIT.

---

### 5.7 M-07: Build Health

| Field | Value |
|-------|-------|
| **Metric ID** | M-07 |
| **Name** | Build Health |
| **Source Type** | COMMIT |
| **Extractable from git alone** | No (requires CI/CD pipeline status) |
| **Status** | Planned (NOT IMPLEMENTED) |
| **Severity** | 1.8 (high) |

**Purpose**: Measures CI/CD build success/failure rates. Serves D-01 (distribution drift).

**Extraction Pipeline**: NOT IMPLEMENTED.

**Planned Extraction Method**: CI/CD API integration (GitHub Actions, Jenkins, GitLab CI, CircleCI, etc.).

**Planned Observation Fields**:

| Field | Expected Value / Rule |
|-------|----------------------|
| `observation_id` | 16-char hex, SHA-256 deterministic |
| `source_type` | SourceType.COMMIT |
| `source_id` | 40-char SHA of the commit |
| `metric_id` | `"M-07"` |
| `value` | `1.0` for success, `0.0` for failure |
| `quality` | ObservationQuality.COMPLETE |
| `confidence` | 1.0 (CI status is authoritative) |
| `unit` | `"build_status"` |

**Gap**: Needs CI/CD API integration. No observation creation code exists.

---

## 6. Source Types

### 6.1 SourceType Enum

| Source Type | Description | Extraction Method | Observation Fields Populated |
|-------------|-------------|-------------------|------------------------------|
| `COMMIT` | A git commit | `git log` parsing | `source_id` = commit SHA; `timestamp` = author date; `author_email` = author |
| `FILE` | A file at a point-in-time | File system or git snapshot | `source_id` = file content SHA; `timestamp` = extraction time |
| `BRANCH` | A git branch | `git branch` parsing | `source_id` = HEAD commit SHA; `timestamp` = latest commit on branch |
| `TAG` | A git tag | `git tag` parsing | `source_id` = tagged commit SHA; `timestamp` = tag date |

### 6.2 Source Type Usage by Metric

| Metric ID | Primary Source Type | Secondary Source Types |
|-----------|---------------------|----------------------|
| M-01 | COMMIT | — |
| M-02 | COMMIT | — |
| M-03 | COMMIT | — |
| M-04 | FILE | — |
| M-05 | FILE | — |
| M-06 | COMMIT | — |
| M-07 | COMMIT | — |

---

## 7. Quality States and Transition Rules

### 7.1 Quality State Definitions

| State | Definition | When Produced |
|-------|------------|---------------|
| `COMPLETE` | Observation was directly extracted from an authoritative source with no approximation. | Git log parsing (M-02, M-06), CI/CD API response (M-07), AST tool output (M-04) |
| `ESTIMATED` | Observation value was inferred or interpolated from incomplete data. | Gap-filling when a window has partial data; linear interpolation between known points |
| `MISSING` | Observation is expected but could not be produced (e.g., extraction failed, data unavailable). | Git command failure, CI/CD API timeout, dependency file absent |
| `DERIVED` | Observation was computed from other observations, not directly extracted. | M-01 repository metadata, cross-metric computations |

### 7.2 Transition Rules

```
COMPLETE  → (never transitions; frozen at creation)
ESTIMATED → (never transitions; frozen at creation)
DERIVED   → (never transitions; frozen at creation)
MISSING   → (never transitions; frozen at creation)
```

Observations are **immutable** (frozen dataclass). Quality state is set at creation time and does not change. If a previously MISSING observation is re-extracted successfully, it produces a NEW observation with quality COMPLETE — it does not mutate the original.

### 7.3 Detector Quality Handling

| Detector | Accepted Qualities | Excluded Qualities | Preference |
|----------|-------------------|-------------------|------------|
| D-01 (Distribution Drift) | COMPLETE, ESTIMATED, DERIVED | MISSING | COMPLETE preferred |
| D-02 (Correlation Breakdown) | COMPLETE, ESTIMATED, DERIVED | MISSING | COMPLETE preferred |
| D-03 (Threshold Compression) | COMPLETE, ESTIMATED, DERIVED | MISSING | COMPLETE and DERIVED both accepted |

**Rule**: MISSING observations are ALWAYS excluded from detector analysis. A warning is logged. If exclusion causes the window to fall below the detector's minimum observation count, the detector returns a SKIPPED status for that window.

---

## 8. Observation Data Model

### 8.1 Observation (Frozen Dataclass)

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `observation_id` | `str` | 16-char hex, SHA-256 deterministic | Unique identifier derived from observation content |
| `source_type` | `SourceType` | One of: COMMIT, FILE, BRANCH, TAG | Origin class of the observation |
| `source_id` | `str` | 40-char SHA | Identifier of the source entity (commit SHA, file SHA, etc.) |
| `metric_id` | `str` | Pattern `M-\d{2}` | Metric this observation measures |
| `value` | `Optional[float]` | `None` only for MISSING quality | The observation value |
| `quality` | `ObservationQuality` | One of: COMPLETE, ESTIMATED, MISSING, DERIVED | Completeness classification |
| `timestamp` | `datetime` | Valid datetime | When the observation was produced or the source event occurred |
| `author_email` | `Optional[str]` | Valid email or `None` | Author of the source change |
| `provenance` | `ObservationProvenance` | Non-null | Extraction pipeline metadata |
| `relationships` | `list[ObservationRelationship]` | `[]` default | Links to related observations |
| `confidence` | `float` | [0.0, 1.0] | Extraction certainty |
| `unit` | `str` | Non-empty | Unit of measurement |
| `uncertainty` | `Optional[float]` | `None` if not computed | Standard deviation or CI half-width |
| `metadata` | `dict` | `{}` default | Arbitrary key-value pairs for pipeline metadata |

### 8.2 ObservationCollection

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `source_repo` | `str` | Non-empty | Repository identifier |
| `schema_version` | `str` | `"1.0.0"` | Schema version for serialization compatibility |
| `observations` | `list[Observation]` | Ordered by timestamp | All observations in the collection |
| `windows` | `list[ObservationWindow]` | Pre-partitioned | Windows for detector consumption |
| `provenance` | `ObservationProvenance` | Non-null | Collection-level extraction metadata |
| `metadata` | `dict` | `{}` default | Repository-level metadata (M-01 context) |

### 8.3 ObservationWindow

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `window_id` | `str` | Non-empty | Unique window identifier |
| `start_date` | `datetime` | < end_date | Window start (inclusive) |
| `end_date` | `datetime` | > start_date | Window end (exclusive) |
| `observations` | `Dict[str, List[Observation]]` | Keyed by metric_id | Observations in this window, grouped by metric |
| `commit_count` | `int` | ≥ 0 | Total commits in this window |
| `strategy` | `str` | "time_based" or "count_based" | Windowing strategy used |

### 8.4 MetricDataFrame

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `repo_id` | `str` | Non-empty | Repository identifier |
| `run_id` | `str` | Non-empty | Unique run identifier |
| `timestamp` | `datetime` | Valid datetime | When the frame was produced |
| `metrics` | `Dict[str, Dict[str, List[Optional[float]]]]` | metric_id → window_id → values | Aggregated metric values per window |

---

## 9. Validation Rules

### 9.1 Universal Validation (All Metrics)

| Rule ID | Rule | Severity | Enforced At |
|---------|------|----------|-------------|
| V-ALL-01 | `observation_id` MUST be exactly 16 hex characters | FATAL | Creation |
| V-ALL-02 | `source_id` MUST be exactly 40 hex characters | FATAL | Creation |
| V-ALL-03 | `metric_id` MUST match pattern `M-\d{2}` | FATAL | Creation |
| V-ALL-04 | `confidence` MUST be in [0.0, 1.0] | FATAL | Creation |
| V-ALL-05 | `quality` MUST be a valid ObservationQuality enum | FATAL | Creation |
| V-ALL-06 | `source_type` MUST be a valid SourceType enum | FATAL | Creation |
| V-ALL-07 | `timestamp` MUST be a valid datetime | FATAL | Creation |
| V-ALL-08 | If `quality` = COMPLETE, `value` MUST NOT be None | WARNING | Validation |
| V-ALL-09 | If `quality` = MISSING, `value` MUST be None | WARNING | Validation |
| V-ALL-10 | `observation_id` MUST be deterministic (same input → same ID) | FATAL | Creation |

### 9.2 Metric-Specific Validation

#### M-02: Commit Frequency

| Rule ID | Rule | Severity |
|---------|------|----------|
| V-M02-01 | `value` MUST be 1.0 | FATAL |
| V-M02-02 | `quality` MUST be COMPLETE | FATAL |
| V-M02-03 | `unit` MUST be "commits" | FATAL |
| V-M02-04 | `author_email` MUST be non-empty string | WARNING |
| V-M02-05 | `timestamp` MUST be within extraction window ±1 day | WARNING |

#### M-06: Dependency Health

| Rule ID | Rule | Severity |
|---------|------|----------|
| V-M06-01 | `value` MUST be ≥ 0.0 | FATAL |
| V-M06-02 | `quality` MUST be COMPLETE | FATAL |
| V-M06-03 | `unit` MUST be "days_since_update" | FATAL |
| V-M06-04 | `source_type` MUST be SourceType.COMMIT | FATAL |
| V-M06-05 | If no dependency files exist, collection MUST be empty (not MISSING) | WARNING |

#### M-01: Repository Metadata

| Rule ID | Rule | Severity |
|---------|------|----------|
| V-M01-01 | Extraction MUST complete before M-02/M-06 extraction begins | FATAL |
| V-M01-02 | `metadata` MUST contain non-empty `author_email` | WARNING |
| V-M01-03 | `confidence` MUST be in [0.8, 1.0] | WARNING |

---

## 10. Sampling Readiness

### 10.1 Readiness States

| State | Definition |
|-------|------------|
| `READY` | All detector minimum requirements are met for the observation set |
| `PARTIAL` | Some detectors are eligible, others are not |
| `SKIPPED` | No detectors are eligible due to insufficient observations |
| `NOT_APPLICABLE` | The metric is not applicable to the repository (e.g., no dependency files for M-06) |

### 10.2 Detector Minimum Requirements

| Detector | Min Observations/Window | Min Windows | Min Metrics |
|----------|------------------------|-------------|-------------|
| D-01 (Distribution Drift) | 10 | 2 | 1 |
| D-02 (Correlation Breakdown) | 10 (paired) | 2 | 2 |
| D-03 (Threshold Compression) | 20 | 1 | 1 |

### 10.3 Readiness Evaluation

Readiness is computed per metric-detector pair. A metric is READY for a detector if and only if:

1. The observation set contains ≥ `min_observations_per_window` non-MISSING observations in each of ≥ `min_windows` windows.
2. The number of distinct metrics with observations ≥ `min_metrics`.
3. For D-02: observations for at least 2 metrics exist as pairs within the same windows.

---

## 11. Scoring Integration

### 11.1 Integrity Score (IS)

```
IS = 1.0 - (w₁ × d₁ + w₂ × d₂ + w₃ × d₃)
```

Where:
- `w₁ = 0.4`, `w₂ = 0.35`, `w₃ = 0.25`
- `d₁`, `d₂`, `d₃` are detector-specific deficiency scores

**Observation Severity Multipliers**:

| Metric ID | Multiplier | Rationale |
|-----------|------------|-----------|
| M-01 | 0.5 | Low — context metric, not behavioral |
| M-02 | 1.0 | Normal — core behavioral metric |
| M-03 | 1.2 | Moderate — change magnitude indicator |
| M-04 | 1.5 | High — complexity is a leading indicator of issues |
| M-05 | 2.0 | Critical — coverage directly affects detection reliability |
| M-06 | 1.0 | Normal — dependency staleness is a standard signal |
| M-07 | 1.8 | High — build health is a strong production signal |

### 11.2 Confidence Score (CS)

```
CS = f₁ × f₂ × f₃ × f₄ × f₅ × f₆
```

Where:
- `f₁`: observation_completeness — fraction of non-MISSING observations
- `f₂`: metric_coverage — fraction of metrics with observations
- `f₃`: detector_agreement — agreement between detector results
- `f₄`: sample_sufficiency — whether sample sizes meet detector minimums
- `f₅`: temporal_consistency — consistency of observation timestamps
- `f₆`: statistical_power — achieved power given sample size and effect size

---

## 12. Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `MAX_WINDOWS` | 20 | Maximum number of observation windows per collection |
| `MIN_OBSERVATIONS_PER_WINDOW` | 10 | Minimum non-MISSING observations for a window to be usable |
| `MAX_OBSERVATIONS_PER_WINDOW` | 1000 | Hard cap on observations per window (prevents memory exhaustion) |
| `DEFAULT_WINDOW_SIZE_DAYS` | 30 | Default time-based window size |
| `DEFAULT_CONFIDENCE_THRESHOLD` | 0.8 | Minimum confidence for an observation to be considered reliable |
| `DEFAULT_SIGNIFICANCE_LEVEL` | 0.05 | Alpha for statistical tests (KS test, Fisher z, etc.) |

---

## 13. Cross-References

| Document | Abbreviation | Relationship |
|----------|-------------|-------------|
| Observation Processing Architecture | OPA | Defines how observations are processed, windowed, and fed to detectors |
| Observation Processing & Scoring | OPC | Defines scoring formulas that consume observation quality and confidence |
| Observation Validation Rules | OVR | Defines the validation framework implementation and error handling |
| Detection Matrix Specification | DMS | Defines detector algorithms and their observation consumption contracts |
| Sampling Readiness Specification | SRS | Defines readiness evaluation logic and state machine |

---

## Appendix A: Metric-to-Detector Mapping

```
Metric    D-01 (Drift)  D-02 (Corr.)  D-03 (Comp.)
--------  ------------  ------------  ------------
M-01      —             —             —
M-02      ✓             ✓             ✓
M-03      ✓             —             ✓
M-04      ✓             —             ✓
M-05      ✓             ✓             ✓
M-06      ✓             ✓             ✓
M-07      ✓             —             ✓
```

## Appendix B: Observation Field Population Matrix

| Field | M-01 | M-02 | M-03 | M-04 | M-05 | M-06 | M-07 |
|-------|------|------|------|------|------|------|------|
| `observation_id` | N/A | ✓ | Planned | Planned | Planned | ✓ | Planned |
| `source_type` | COMMIT | COMMIT | COMMIT | FILE | FILE | COMMIT | COMMIT |
| `source_id` | N/A | SHA | SHA | SHA | SHA | SHA | SHA |
| `metric_id` | — | M-02 | M-03 | M-04 | M-05 | M-06 | M-07 |
| `value` | N/A | 1.0 | lines | score | % | days | 0/1 |
| `quality` | DERIVED | COMPLETE | — | — | — | COMPLETE | — |
| `timestamp` | ✓ | ✓ | — | — | — | ✓ | — |
| `author_email` | ✓ | ✓ | — | — | — | — | — |
| `confidence` | 1.0 | 1.0 | — | tool | 1.0 | 1.0 | 1.0 |
| `unit` | meta | commits | lines_changed | complexity | coverage_pct | days_since | build_status |
| `uncertainty` | — | — | — | tool | — | — | — |

**Legend**: `✓` = populated with specified value; `—` = default/empty; `N/A` = not applicable (M-01 does not create Observation records); `Planned` = defined but not implemented.

## Appendix C: Extraction Pipeline Inventory

| Pipeline Module | Metric(s) | Method | Status |
|----------------|-----------|--------|--------|
| `RepositoryIngestionEngine` | M-01 | Direct file/repo inspection | Implemented |
| `CommitExtractor` | M-02 | `git log --all --format='%H %ae %aI %s'` | Implemented |
| `CommitExtractor._commit_to_observations()` | M-02 | Observation creation from parsed commits | Implemented |
| `CommitExtractor._extract_dependency_health()` | M-06 | Dependency file change detection | Implemented |
| (Planned) ChurnExtractor | M-03 | `git diff --stat` / `git log --stat` | Planned |
| (Planned) ComplexityExtractor | M-04 | External tool (lizard/radon) | Planned |
| (Planned) CoverageExtractor | M-05 | CI/CD coverage report parsing | Planned |
| (Planned) BuildStatusExtractor | M-07 | CI/CD API integration | Planned |

---

*End of OSMS v1.0.*
