# Observation Validation Rules (OVR) v1.0

**MIIE Specification — Observation Validation Layer**

| Field | Value |
|-------|-------|
| Document ID | OVR-v1.0 |
| MIIE Version | 1.6 |
| Status | Draft |
| Last Updated | 2026-07-03 |
| Author | MIIE Engineering |

---

## 1. Purpose and Scope

This document specifies the per-observation validation rules, quality state machine, and confidence scoring model for all metric observations within the MIIE v1.6 system. It defines the contract between observation providers, the validation pipeline, and downstream consumers.

### 1.1 Scope

This specification covers:

- Validation rules for each metric observation (M-01 through M-07)
- Quality state definitions and legal transition paths
- Confidence scoring model including base scores, adjustments, and decay
- Validation pipeline composition and ordering
- Error handling, rejection criteria, and recovery behavior

### 1.2 Out of Scope

- Observation storage schemas (see OSMS v1.0)
- Observation aggregation patterns (see OPC v1.0)
- Observation processing orchestration (see OPA v1.0)
- Metric computation algorithms (see individual metric specifications)

### 1.3 Normative References

| Reference | Document |
|-----------|----------|
| OSMS | Observation Storage and Management Specification |
| OPA | Observation Processing Architecture |
| OPC | Observation Processing and Composition |

---

## 2. Validation Architecture

### 2.1 Overview

Every observation enters the system through a validation pipeline. The pipeline applies a sequence of validators to each observation before it is accepted into storage. Observations that fail validation are rejected with structured error codes.

```
Provider → [Schema Validator] → [Field Validator] → [Range Validator] → [Quality Validator] → [Confidence Validator] → Storage
                 ↓                     ↓                   ↓                    ↓                       ↓
              Reject/Pass          Reject/Pass          Reject/Pass         Annotate/Pass           Annotate/Pass
```

### 2.2 Validator Types

| Validator | Phase | Behavior on Failure |
|-----------|-------|---------------------|
| Schema Validator | 1 | **Hard reject** — observation discarded |
| Field Validator | 2 | **Hard reject** — observation discarded |
| Range Validator | 3 | **Hard reject** — observation discarded |
| Quality Validator | 4 | **Soft reject** — quality state adjusted to MISSING |
| Confidence Validator | 5 | **Annotate** — confidence floor applied, observation accepted with degraded confidence |

### 2.3 Validator Ordering

Validators execute in fixed phase order (1–5). A hard reject at any phase terminates processing; the observation is not passed to subsequent validators. Soft rejects and annotations allow continued processing.

---

## 3. Per-Metric Validation Rules

### 3.1 Summary Table

| Metric | Required Fields | Optional Fields | Quality States | Base Confidence | Value Constraint | Unit |
|--------|----------------|-----------------|----------------|-----------------|------------------|------|
| M-01 | `source_repo`, `timestamp` | `author_email` | COMPLETE | 0.8 | `source_repo` non-empty | — |
| M-02 | `value`, `source_id`, `timestamp`, `author_email` | — | COMPLETE | 1.0 | `value > 0`, `source_id` valid SHA | commits |
| M-03 | `value`, `source_id`, `timestamp` | — | COMPLETE, ESTIMATED | 0.9 | `value ≥ 0` | changes |
| M-04 | `value`, `source_id`, `timestamp` | — | COMPLETE, ESTIMATED | 0.7 | `0 ≤ value < 1000` | complexity_score |
| M-05 | `value`, `source_id`, `timestamp` | — | COMPLETE, ESTIMATED | 0.8 | `0.0 ≤ value ≤ 100.0` | percentage |
| M-06 | `value`, `source_id`, `timestamp` | — | COMPLETE | 1.0 | `value ≥ 0` | days |
| M-07 | `value`, `source_id`, `timestamp` | — | COMPLETE, ESTIMATED | 0.8 | `value ∈ {0.0, 1.0}` | status |

### 3.2 M-01: Repository Metadata

**Metric ID:** M-01
**Description:** Static and derived metadata about a repository.

#### Fields

| Field | Required | Type | Constraint |
|-------|----------|------|------------|
| `source_repo` | Yes | string | Non-empty, valid repository identifier |
| `timestamp` | Yes | datetime | Valid ISO 8601 timestamp |
| `author_email` | No | string \| null | May be `None` for repo-level metadata |

#### Validation Rules

| Rule ID | Phase | Field | Condition | Error Code |
|---------|-------|-------|-----------|------------|
| M01-R01 | 2 | `source_repo` | Must be non-empty string | `M01_MISSING_REPO` |
| M01-R02 | 2 | `source_repo` | Must match repository identifier pattern | `M01_INVALID_REPO` |
| M01-R03 | 2 | `timestamp` | Must be valid ISO 8601 datetime | `M01_INVALID_TIMESTAMP` |
| M01-R04 | 2 | `author_email` | If present, must be valid email format or null | `M01_INVALID_AUTHOR` |

#### Quality and Confidence

- **Default quality:** COMPLETE (direct metadata extraction)
- **Base confidence:** 0.8
- **Confidence notes:** Drops to 0.7 when `author_email` is inferred rather than extracted directly from commit metadata.

---

### 3.3 M-02: Commit Frequency

**Metric ID:** M-02
**Description:** Count of commits within a defined time window.

#### Fields

| Field | Required | Type | Constraint |
|-------|----------|------|------------|
| `value` | Yes | integer | > 0 |
| `source_id` | Yes | string | Valid git SHA (40-hex or 7-hex prefix) |
| `timestamp` | Yes | datetime | Valid ISO 8601 timestamp |
| `author_email` | Yes | string | Non-empty, valid email |

#### Validation Rules

| Rule ID | Phase | Field | Condition | Error Code |
|---------|-------|-------|-----------|------------|
| M02-R01 | 2 | `value` | Must be present and non-null | `M02_MISSING_VALUE` |
| M02-R02 | 3 | `value` | Must be > 0 | `M02_INVALID_VALUE` |
| M02-R03 | 2 | `source_id` | Must be valid hex SHA (40 or 7 chars) | `M02_INVALID_SOURCE_ID` |
| M02-R04 | 2 | `timestamp` | Must be valid ISO 8601 datetime | `M02_INVALID_TIMESTAMP` |
| M02-R05 | 2 | `author_email` | Must be non-empty, valid email format | `M02_INVALID_AUTHOR` |

#### Quality and Confidence

- **Default quality:** COMPLETE (git log is authoritative source)
- **Base confidence:** 1.0
- **Confidence notes:** Never estimated; always directly measured from version control.

---

### 3.4 M-03: Code Churn

**Metric ID:** M-03
**Description:** Volume of code changes (lines added/removed or files changed) within a time window.

#### Fields

| Field | Required | Type | Constraint |
|-------|----------|------|------------|
| `value` | Yes | float | ≥ 0 |
| `source_id` | Yes | string | Valid identifier |
| `timestamp` | Yes | datetime | Valid ISO 8601 timestamp |

#### Validation Rules

| Rule ID | Phase | Field | Condition | Error Code |
|---------|-------|-------|-----------|------------|
| M03-R01 | 2 | `value` | Must be present and non-null | `M03_MISSING_VALUE` |
| M03-R02 | 3 | `value` | Must be ≥ 0 | `M03_NEGATIVE_VALUE` |
| M03-R03 | 3 | `value` | Must be < 1,000,000 (sanity ceiling) | `M03_VALUE_EXCEEDS_CEILING` |
| M03-R04 | 2 | `source_id` | Must be non-empty | `M03_MISSING_SOURCE_ID` |
| M03-R05 | 2 | `timestamp` | Must be valid ISO 8601 datetime | `M03_INVALID_TIMESTAMP` |

#### Quality and Confidence

- **Default quality:** COMPLETE (direct diff analysis) or ESTIMATED (inferred from commit messages)
- **Base confidence:** 0.9
- **Confidence adjustment:** 0.85 when ESTIMATED, 1.0 when COMPLETE with direct diff

---

### 3.5 M-04: Code Complexity

**Metric ID:** M-04
**Description:** Aggregate complexity measure (e.g., cyclomatic complexity) for a codebase or module.

#### Fields

| Field | Required | Type | Constraint |
|-------|----------|------|------------|
| `value` | Yes | float | ≥ 0, < 1000 |
| `source_id` | Yes | string | Valid identifier |
| `timestamp` | Yes | datetime | Valid ISO 8601 timestamp |

#### Validation Rules

| Rule ID | Phase | Field | Condition | Error Code |
|---------|-------|-------|-----------|------------|
| M04-R01 | 2 | `value` | Must be present and non-null | `M04_MISSING_VALUE` |
| M04-R02 | 3 | `value` | Must be ≥ 0 | `M04_NEGATIVE_VALUE` |
| M04-R03 | 3 | `value` | Must be < 1000 (sanity check) | `M04_VALUE_EXCEEDS_CEILING` |
| M04-R04 | 2 | `source_id` | Must be non-empty | `M04_MISSING_SOURCE_ID` |
| M04-R05 | 2 | `timestamp` | Must be valid ISO 8601 datetime | `M04_INVALID_TIMESTAMP` |

#### Quality and Confidence

- **Default quality:** COMPLETE (direct AST/tool measurement) or ESTIMATED (inferred from file characteristics)
- **Base confidence:** 0.7
- **Confidence adjustment:** 0.6 when ESTIMATED, 0.9 when COMPLETE with validated tool

---

### 3.6 M-05: Code Coverage

**Metric ID:** M-05
**Description:** Test coverage percentage for a codebase or module.

#### Fields

| Field | Required | Type | Constraint |
|-------|----------|------|------------|
| `value` | Yes | float | 0.0 ≤ value ≤ 100.0 |
| `source_id` | Yes | string | Valid identifier |
| `timestamp` | Yes | datetime | Valid ISO 8601 timestamp |

#### Validation Rules

| Rule ID | Phase | Field | Condition | Error Code |
|---------|-------|-------|-----------|------------|
| M05-R01 | 2 | `value` | Must be present and non-null | `M05_MISSING_VALUE` |
| M05-R02 | 3 | `value` | Must be ≥ 0.0 | `M05_VALUE_BELOW_RANGE` |
| M05-R03 | 3 | `value` | Must be ≤ 100.0 | `M05_VALUE_ABOVE_RANGE` |
| M05-R04 | 2 | `source_id` | Must be non-empty | `M05_MISSING_SOURCE_ID` |
| M05-R05 | 2 | `timestamp` | Must be valid ISO 8601 datetime | `M05_INVALID_TIMESTAMP` |

#### Quality and Confidence

- **Default quality:** COMPLETE (direct CI/coverage tool data) or ESTIMATED (inferred from test file presence)
- **Base confidence:** 0.8
- **Confidence adjustment:** 0.7 when ESTIMATED, 0.95 when COMPLETE from primary CI source

---

### 3.7 M-06: Dependency Health

**Metric ID:** M-06
**Description:** Measure of dependency freshness, expressed as days since last change or update.

#### Fields

| Field | Required | Type | Constraint |
|-------|----------|------|------------|
| `value` | Yes | float | ≥ 0 |
| `source_id` | Yes | string | Valid identifier |
| `timestamp` | Yes | datetime | Valid ISO 8601 timestamp |

#### Validation Rules

| Rule ID | Phase | Field | Condition | Error Code |
|---------|-------|-------|-----------|------------|
| M06-R01 | 2 | `value` | Must be present and non-null | `M06_MISSING_VALUE` |
| M06-R02 | 3 | `value` | Must be ≥ 0 | `M06_NEGATIVE_VALUE` |
| M06-R03 | 3 | `value` | Must be < 3650 (sanity: < 10 years) | `M06_VALUE_EXCEEDS_CEILING` |
| M06-R04 | 2 | `source_id` | Must be non-empty | `M06_MISSING_SOURCE_ID` |
| M06-R05 | 2 | `timestamp` | Must be valid ISO 8601 datetime | `M06_INVALID_TIMESTAMP` |

#### Quality and Confidence

- **Default quality:** COMPLETE (direct file change detection)
- **Base confidence:** 1.0
- **Confidence notes:** Always directly measured; never estimated.

---

### 3.8 M-07: Build Health

**Metric ID:** M-07
**Description:** Binary build status indicator for the most recent CI build.

#### Fields

| Field | Required | Type | Constraint |
|-------|----------|------|------------|
| `value` | Yes | float | 0.0 or 1.0 |
| `source_id` | Yes | string | Valid identifier |
| `timestamp` | Yes | datetime | Valid ISO 8601 timestamp |

#### Validation Rules

| Rule ID | Phase | Field | Condition | Error Code |
|---------|-------|-------|-----------|------------|
| M07-R01 | 2 | `value` | Must be present and non-null | `M07_MISSING_VALUE` |
| M07-R02 | 3 | `value` | Must be exactly 0.0 or 1.0 | `M07_INVALID_STATUS` |
| M07-R03 | 2 | `source_id` | Must be non-empty | `M07_MISSING_SOURCE_ID` |
| M07-R04 | 2 | `timestamp` | Must be valid ISO 8601 datetime | `M07_INVALID_TIMESTAMP` |

#### Quality and Confidence

- **Default quality:** COMPLETE (direct CI data) or ESTIMATED (inferred from recent build history)
- **Base confidence:** 0.8
- **Confidence adjustment:** 0.7 when ESTIMATED, 0.95 when COMPLETE from primary CI source

---

## 4. Quality State Machine

### 4.1 State Definitions

| State | Definition | Example Source |
|-------|------------|----------------|
| `COMPLETE` | Direct measurement from an authoritative source | Git log commit count, CI coverage report |
| `ESTIMATED` | Inferred from incomplete data or heuristic analysis | Coverage inferred from test file presence |
| `DERIVED` | Computed from other observations, not a direct measurement | Aggregated churn rate from individual commits |
| `MISSING` | Data not available; default state for unpopulated observations | Provider failure, missing CI pipeline |

### 4.2 State Transition Rules

The following transitions are permitted. All other transitions are illegal and MUST be rejected by the quality validator.

```
                  ┌──────────────────────────────────────────────┐
                  │                                              │
                  ▼                                              │
              ┌─────────┐    provider succeeds    ┌──────────┐  │
              │ MISSING │ ──────────────────────→ │ COMPLETE │  │
              │         │                         │          │  │
              │         │    provider uses        └────┬─────┘  │
              │         │    inference                  │        │
              │         │ ──────────────────────→ ┌─────┴──────┐ │
              └────┬────┘                         │ ESTIMATED  │ │
                   │                              │            │ │
                   │                              └─────┬──────┘ │
                   │                                    │        │
                   │          better data               │        │
                   │         becomes available          │        │
                   │ ←─────────────────────────────────┘        │
                   │                                            │
                   │     recomputed from other observations     │
                   │ ──────────────────────→ ┌──────────┐       │
                   │                         │ DERIVED  │       │
                   │                         │          │       │
                   │                         └──────────┘       │
                   │                                            │
                   │◀───────────────────────────────────────────┘
                   │     data source unavailable
                   │     (provider failure)
                   └─────────────────────────────────────────────┘
```

### 4.3 Formal Transition Table

| From State | To State | Trigger Condition | Validator |
|------------|----------|-------------------|-----------|
| `MISSING` | `COMPLETE` | Provider successfully extracts data from authoritative source | Quality Validator |
| `MISSING` | `ESTIMATED` | Provider applies inference or heuristic to incomplete data | Quality Validator |
| `COMPLETE` | `DERIVED` | Observation is recomputed from other observations | Quality Validator |
| `ESTIMATED` | `COMPLETE` | Higher-fidelity data source becomes available | Quality Validator |
| `COMPLETE` | `MISSING` | Data source becomes unavailable (provider failure, source corruption) | Quality Validator |
| `ESTIMATED` | `MISSING` | Estimated data source becomes unavailable | Quality Validator |
| `DERIVED` | `MISSING` | Underlying source observations become unavailable | Quality Validator |

### 4.4 Illegal Transitions

The following transitions are prohibited:

| From | To | Reason |
|------|----|--------|
| `COMPLETE` | `ESTIMATED` | Downgrade without source change is not permitted |
| `DERIVED` | `COMPLETE` | Derived observations cannot become direct measurements |
| `DERIVED` | `ESTIMATED` | Derived observations cannot become estimated |
| `MISSING` | `DERIVED` | Cannot derive from nothing |

### 4.5 State Persistence

Quality states are recorded as metadata on each observation. The transition log must include:

- `from_state`: Previous quality state
- `to_state`: New quality state
- `transition_trigger`: Human-readable reason for the transition
- `timestamp`: ISO 8601 timestamp of the transition
- `validator_id`: Identifier of the validator that performed the transition

---

## 5. Confidence Scoring Model

### 5.1 Base Confidence Scores

Each metric has a base confidence score reflecting the inherent reliability of its primary data source.

| Metric | Base Confidence | Rationale |
|--------|-----------------|-----------|
| M-01 | 0.8 | Metadata extraction involves inference from commit history |
| M-02 | 1.0 | Git log is an authoritative, tamper-resistant source |
| M-03 | 0.9 | Diff analysis is direct but may miss semantic changes |
| M-04 | 0.7 | AST parsing tools vary in accuracy across languages |
| M-05 | 0.8 | CI coverage data is authoritative but tooling varies |
| M-06 | 1.0 | File change detection is deterministic |
| M-07 | 0.8 | CI data is authoritative but pipeline configurations vary |

### 5.2 Quality Multiplier

The quality state of an observation modifies its effective confidence:

| Quality State | Multiplier |
|---------------|------------|
| `COMPLETE` | 1.0 |
| `DERIVED` | 0.8 |
| `ESTIMATED` | 0.7 |
| `MISSING` | 0.0 |

### 5.3 Freshness Penalty

Confidence decays as observation age increases. The penalty applies linearly from the observation timestamp.

```
freshness_penalty = floor((now - observation_timestamp) / 30_days) × 0.1
```

| Age (days) | Penalty | Effective Range |
|------------|---------|-----------------|
| 0–30 | 0.0 | Full confidence |
| 31–60 | -0.1 | Slight degradation |
| 61–90 | -0.2 | Moderate degradation |
| 91–120 | -0.3 | Significant degradation |
| 121–150 | -0.4 | Severe degradation |
| > 150 | -0.5 (capped) | Floor applies |

**Floor:** Confidence never drops below 0.1 due to freshness alone. Observations older than 150 days receive a capped penalty of -0.5.

### 5.4 Source Reliability Factor

Each observation provider has a health score between 0.0 and 1.0. This score is multiplied into the confidence calculation.

```
source_reliability = provider.health_score  # 0.0 – 1.0
```

Providers with degraded health reduce the confidence of all observations they produce.

### 5.5 Final Confidence Formula

```
effective_confidence = base_confidence × quality_multiplier × source_reliability − freshness_penalty
effective_confidence = clamp(effective_confidence, 0.0, 1.0)
```

**Clamping:** The final confidence value is clamped to the range [0.0, 1.0]. Negative values are clamped to 0.0; values exceeding 1.0 are clamped to 1.0.

### 5.6 Confidence Thresholds

| Threshold | Value | Behavior |
|-----------|-------|----------|
| Minimum acceptable | 0.3 | Observations below this threshold are flagged for review |
| Minimum for aggregation | 0.5 | Observations below this threshold are excluded from derived computations |
| Full confidence | ≥ 0.9 | Observation treated as authoritative for all downstream use |

### 5.7 Worked Examples

**Example 1: Fresh commit frequency observation**

```
base_confidence    = 1.0  (M-02)
quality_multiplier = 1.0  (COMPLETE)
source_reliability = 0.95 (healthy provider)
freshness_penalty  = 0.0  (extracted today)

effective = 1.0 × 1.0 × 0.95 − 0.0 = 0.95
```

**Example 2: Stale estimated code complexity observation**

```
base_confidence    = 0.7  (M-04)
quality_multiplier = 0.7  (ESTIMATED)
source_reliability = 0.8  (degraded provider)
freshness_penalty  = 0.3  (90 days old)

effective = 0.7 × 0.7 × 0.8 − 0.3 = 0.392 − 0.3 = 0.092
→ clamped to 0.1 (freshness floor)
```

**Example 3: Derived coverage observation**

```
base_confidence    = 0.8  (M-05)
quality_multiplier = 0.8  (DERIVED)
source_reliability = 1.0  (healthy provider)
freshness_penalty  = 0.1  (40 days old)

effective = 0.8 × 0.8 × 1.0 − 0.1 = 0.64 − 0.1 = 0.54
```

---

## 6. Validation Pipeline

### 6.1 Pipeline Composition

The validation pipeline is a fixed sequence of validator phases. Each phase runs independently but may depend on data validated in prior phases.

```
Phase 1: Schema Validation
    ├── Verify observation conforms to expected JSON schema
    ├── Verify all required top-level fields are present
    └── Reject malformed observations (hard reject)

Phase 2: Field Validation
    ├── Verify field types match expected types
    ├── Verify string fields are non-empty where required
    ├── Verify email fields match email format
    ├── Verify timestamp fields are valid ISO 8601
    └── Reject observations with missing or malformed required fields (hard reject)

Phase 3: Range Validation
    ├── Verify numeric values are within valid ranges
    ├── Verify enum values are within allowed sets
    ├── Apply metric-specific sanity checks (ceilings)
    └── Reject observations with out-of-range values (hard reject)

Phase 4: Quality Validation
    ├── Verify quality state is in the set of allowed states for the metric
    ├── Verify quality state transition is legal
    ├── Record transition in observation metadata
    └── Soft reject: adjust quality to MISSING if invalid

Phase 5: Confidence Validation
    ├── Compute effective confidence using base score, quality multiplier, freshness, and source reliability
    ├── Clamp to [0.0, 1.0]
    ├── Apply minimum acceptable threshold (0.3)
    └── Annotate with computed confidence; flag if below threshold
```

### 6.2 Pipeline Execution Semantics

- **Ordering is mandatory.** Phase N+1 MUST NOT execute if phase N produced a hard reject.
- **All phases execute even on soft reject.** Soft rejections in phases 4–5 do not halt the pipeline; they annotate the observation.
- **Phase results are immutable.** Once a phase completes, its decisions (reject/annotate) cannot be reversed by subsequent phases.
- **All pipeline decisions are logged.** Every phase must emit a structured log entry with the phase number, decision, and affected fields.

### 6.3 Validator Registration

Validators are registered per-metric. The registration specifies:

| Parameter | Type | Description |
|-----------|------|-------------|
| `metric_id` | string | Metric identifier (e.g., `M-01`) |
| `required_fields` | list[string] | Fields that must be present and non-null |
| `optional_fields` | list[string] | Fields that may be absent or null |
| `field_types` | map[string, type] | Expected type for each field |
| `value_constraints` | list[constraint] | Range and validity constraints for `value` |
| `allowed_quality_states` | list[string] | Permitted quality states for this metric |
| `base_confidence` | float | Base confidence score |

### 6.4 Custom Validators

Providers MAY register custom validators for domain-specific checks. Custom validators:

- MUST run after the standard pipeline (Phase 5)
- MUST NOT override hard reject decisions from phases 1–3
- MAY annotate the observation with additional metadata
- MUST be registered in the metric's validator configuration

---

## 7. Error Handling and Rejection Rules

### 7.1 Error Categories

| Category | Severity | Pipeline Behavior | Consumer Behavior |
|----------|----------|-------------------|-------------------|
| **Hard Reject** | Critical | Observation discarded; not stored | No action required (observation never reaches storage) |
| **Soft Reject** | Warning | Quality state adjusted; observation stored with degraded quality | Consumer checks quality state before using observation |
| **Confidence Flag** | Info | Observation stored with low confidence flag | Consumer applies confidence threshold before aggregation |

### 7.2 Error Code Registry

Error codes follow the pattern `{METRIC}-{RULE}` where `METRIC` is the metric identifier and `RULE` is the rule number.

| Code | Category | Description |
|------|----------|-------------|
| `M01_MISSING_REPO` | Hard Reject | Repository identifier is missing or empty |
| `M01_INVALID_REPO` | Hard Reject | Repository identifier does not match expected pattern |
| `M01_INVALID_TIMESTAMP` | Hard Reject | Timestamp is not valid ISO 8601 |
| `M01_INVALID_AUTHOR` | Hard Reject | Author email format is invalid |
| `M02_MISSING_VALUE` | Hard Reject | Commit frequency value is missing |
| `M02_INVALID_VALUE` | Hard Reject | Commit frequency value is not > 0 |
| `M02_INVALID_SOURCE_ID` | Hard Reject | Source ID is not a valid hex SHA |
| `M02_INVALID_TIMESTAMP` | Hard Reject | Timestamp is not valid ISO 8601 |
| `M02_INVALID_AUTHOR` | Hard Reject | Author email is missing or invalid |
| `M03_MISSING_VALUE` | Hard Reject | Code churn value is missing |
| `M03_NEGATIVE_VALUE` | Hard Reject | Code churn value is negative |
| `M03_VALUE_EXCEEDS_CEILING` | Hard Reject | Code churn value exceeds sanity ceiling |
| `M03_MISSING_SOURCE_ID` | Hard Reject | Source ID is missing |
| `M03_INVALID_TIMESTAMP` | Hard Reject | Timestamp is not valid ISO 8601 |
| `M04_MISSING_VALUE` | Hard Reject | Complexity value is missing |
| `M04_NEGATIVE_VALUE` | Hard Reject | Complexity value is negative |
| `M04_VALUE_EXCEEDS_CEILING` | Hard Reject | Complexity value exceeds 1000 |
| `M04_MISSING_SOURCE_ID` | Hard Reject | Source ID is missing |
| `M04_INVALID_TIMESTAMP` | Hard Reject | Timestamp is not valid ISO 8601 |
| `M05_MISSING_VALUE` | Hard Reject | Coverage value is missing |
| `M05_VALUE_BELOW_RANGE` | Hard Reject | Coverage value is below 0.0 |
| `M05_VALUE_ABOVE_RANGE` | Hard Reject | Coverage value is above 100.0 |
| `M05_MISSING_SOURCE_ID` | Hard Reject | Source ID is missing |
| `M05_INVALID_TIMESTAMP` | Hard Reject | Timestamp is not valid ISO 8601 |
| `M06_MISSING_VALUE` | Hard Reject | Dependency health value is missing |
| `M06_NEGATIVE_VALUE` | Hard Reject | Dependency health value is negative |
| `M06_VALUE_EXCEEDS_CEILING` | Hard Reject | Dependency health value exceeds 3650 |
| `M06_MISSING_SOURCE_ID` | Hard Reject | Source ID is missing |
| `M06_INVALID_TIMESTAMP` | Hard Reject | Timestamp is not valid ISO 8601 |
| `M07_MISSING_VALUE` | Hard Reject | Build health value is missing |
| `M07_INVALID_STATUS` | Hard Reject | Build health value is not 0.0 or 1.0 |
| `M07_MISSING_SOURCE_ID` | Hard Reject | Source ID is missing |
| `M07_INVALID_TIMESTAMP` | Hard Reject | Timestamp is not valid ISO 8601 |
| `QSTATE_ILLEGAL_TRANSITION` | Soft Reject | Quality state transition is not in the allowed set |
| `QSTATE_INVALID_VALUE` | Soft Reject | Quality state is not a recognized value |
| `CONF_LOW` | Confidence Flag | Effective confidence is below 0.3 |
| `CONF_EXCLUDED` | Confidence Flag | Effective confidence is below 0.5 (excluded from aggregation) |

### 7.3 Error Response Format

Rejected observations produce a structured error response:

```json
{
  "observation_id": "obs_abc123",
  "metric_id": "M-03",
  "phase": 3,
  "error_code": "M03_NEGATIVE_VALUE",
  "error_category": "hard_reject",
  "field": "value",
  "received_value": -5,
  "constraint": "value must be >= 0",
  "timestamp": "2026-07-03T12:00:00Z"
}
```

### 7.4 Recovery and Retry

- **Hard rejects** are not retried. The provider must correct the observation and resubmit.
- **Soft rejects** may be retried if the provider can supply a valid quality state.
- **Confidence flags** do not prevent storage; they are metadata annotations consumed downstream.

---

## 8. Cross-References

| Document | Relationship | Description |
|----------|--------------|-------------|
| OSMS v1.0 | Storage contract | Defines how validated observations are stored, indexed, and retrieved |
| OPA v1.0 | Processing architecture | Defines how the validation pipeline integrates with the broader processing orchestration |
| OPC v1.0 | Composition rules | Defines how validated observations are combined into derived metrics |
| Provider Specifications | Source contract | Each provider specifies its extraction method, data sources, and quality guarantees |

---

## 9. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-03 | MIIE Engineering | Initial specification |
