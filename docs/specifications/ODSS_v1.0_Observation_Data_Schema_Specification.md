# Observation Data Schema Specification (ODSS) v1.0

**Canonical Observation Data Model for MIIE**

| Field | Value |
|-------|-------|
| Document ID | ODSS-v1.0 |
| Version | 1.0.0 |
| Status | Canonical |
| Date | 2026-06-29 |
| Authors | MIIE Engineering |
| Approved By | Repository Governance |
| Derived From | PRD-v1.5-Observation-Engine, OEAS-v1.5-Observation-Engine |
| Supersedes | None (new) |
| Scope | Canonical observation data model for all of MIIE |
| Classification | Definition-only (no implementation code) |

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
2. [Derivation Chain](#2-derivation-chain)
3. [Observability Principles](#3-observability-principles)
4. [Domain Model Overview](#4-domain-model-overview)
5. [Schema Hierarchy](#5-schema-hierarchy)
6. [Repository (Top-Level Container)](#6-repository-top-level-container)
7. [ObservationCollection](#7-observationcollection)
8. [ObservationWindow](#8-observationwindow)
9. [Observation (Canonical Object)](#9-observation-canonical-object)
10. [Observation Identifier](#10-observation-identifier)
11. [Observation Type](#11-observation-type)
12. [Observation Value](#12-observation-value)
13. [Observation Unit](#13-observation-unit)
14. [Observation Quality](#14-observation-quality)
15. [Observation Attributes](#15-observation-attributes)
16. [Observation Tags](#16-observation-tags)
17. [Observation Metadata](#17-observation-metadata)
18. [Observation Statistics](#18-observation-statistics)
19. [Observation Provenance](#19-observation-provenance)
20. [Observation Relationships](#20-observation-relationships)
21. [Observation Extensions](#21-observation-extensions)
22. [Extraction Source Types](#22-extraction-source-types)
23. [Extraction Context](#23-extraction-context)
24. [Window Builder Input](#24-window-builder-input)
25. [Window Builder Output](#25-window-builder-output)
26. [Detector Adapter Input](#26-detector-adapter-input)
27. [Detector Adapter Output](#27-detector-adapter-output)
28. [Adapter Translation Contract](#28-adapter-translation-contract)
29. [Observation Store Interface](#29-observation-store-interface)
30. [Observation Engine Input](#30-observation-engine-input)
31. [Observation Engine Output](#31-observation-engine-output)
32. [Serialization — JSON Canonical](#32-serialization--json-canonical)
33. [Serialization — MessagePack](#33-serialization--messagepack)
34. [Serialization — Binary (Future)](#34-serialization--binary-future)
35. [Validation — Required Fields](#35-validation--required-fields)
36. [Validation — Integrity Checks](#36-validation--integrity-checks)
37. [Validation — Normalization](#37-validation--normalization)
38. [Validation — Consistency Checks](#38-validation--consistency-checks)
39. [Validation — Cross-Field](#39-validation--cross-field)
40. [Validation — Schema Evolution](#40-validation--schema-evolution)
41. [Validation — Version Compatibility](#41-validation--version-compatibility)
42. [Schema Versioning Strategy](#42-schema-versioning-strategy)
43. [Backward Compatibility Rules](#43-backward-compatibility-rules)
44. [Forward Compatibility Rules](#44-forward-compatibility-rules)
45. [Extension Mechanism](#45-extension-mechanism)
46. [Multi-Repository Support](#46-multi-repository-support)
47. [External Data Integration](#47-external-data-integration)
48. [Plugin Support](#48-plugin-support)
49. [Performance Considerations](#49-performance-considerations)
50. [Concurrency Considerations](#50-concurrency-considerations)
51. [Security and Privacy](#51-security-and-privacy)
52. [Error Taxonomy](#52-error-taxonomy)
53. [Future Evolution](#53-future-evolution)
54. [Decision Log](#54-decision-log)
55. [Appendix A — Glossary](#55-appendix-a--glossary)
56. [Appendix B — Reference Documents](#56-appendix-b--reference-documents)
57. [Appendix C — Field Enumeration Tables](#57-appendix-c--field-enumeration-tables)
58. [Appendix D — Mapping to Existing Schemas](#58-appendix-d--mapping-to-existing-schemas)
59. [End of Document](#59-end-of-document)

---

## 1. Purpose and Scope

### 1.1 Purpose

This document defines the **canonical observation data model** for the MIIE Observation Engine (v1.5). It establishes the single authoritative schema for observation data objects that flow through the observation pipeline — from extraction through storage, windowing, adapter translation, detection, scoring, explanation, and reporting.

The ODSS exists because MIIE v1.0 stores observations as aggregated single values per metric per window (e.g., `{"M-02": {"w00": [143.0]}}`), which causes detectors to skip or produce degenerate results due to insufficient sample sizes. The v1.5 Observation Engine replaces this with per-commit observation-level extraction, and this document specifies the data schema that makes that possible.

### 1.2 Scope

This document covers:

- The canonical `Observation` object and all its constituent fields
- The container hierarchy: `Repository → ObservationCollection → ObservationWindow → Observation`
- Supporting types: `ObservationIdentifier`, `ObservationType`, `ObservationValue`, `ObservationQuality`, `ObservationMetadata`, `ObservationStatistics`, `ObservationProvenance`, `ObservationRelationships`, `ObservationExtensions`
- Extraction source types and extraction context
- Window builder input and output contracts
- Detector adapter input and output contracts
- Observation Store interface contract
- Observation Engine input and output contracts
- Serialization formats (JSON canonical, MessagePack, binary future)
- Validation rules (required fields, integrity, normalization, consistency, cross-field, schema evolution, version compatibility)
- Schema versioning strategy and compatibility rules
- Extension mechanisms for multi-repository, external data, and plugin support
- Performance, concurrency, and security considerations

### 1.3 Non-Scope

This document does NOT cover:

- Implementation code (Python dataclasses, JSON Schema files, or any executable artifact)
- Detector algorithms or statistical methods
- Pipeline orchestration logic
- CLI interface or user experience
- Deployment or infrastructure concerns
- Observation Engine v2.0 capabilities (persistent store, streaming, real-time monitoring)

### 1.4 Relationship to Other Documents

| Document | Relationship |
|----------|-------------|
| PRD-v1.5-Observation-Engine | Parent requirement; this document derives the data model from PRD sections 10-22 |
| OEAS-v1.5-Observation-Engine | Parent architecture; this document specifies the data objects that flow through OEAS layers L0-L7 |
| RELEASE_BASELINE.md | Baseline context; this document defines the v1.5 data schema that extends the v1.0 baseline |
| V1_5_DEVELOPMENT_ENTRY.md | Development plan; this document is the primary deliverable for v1.5 data architecture |

---

## 2. Derivation Chain

### 2.1 PRD Derivations

Every field in the ODSS traces to a specific PRD requirement. The following table maps ODSS entities to PRD sections.

| ODSS Entity | PRD Section | PRD Requirement |
|-------------|-------------|-----------------|
| Observation | §10 Data Model | "One observation per commit per metric" |
| Observation.id | §10.2 Deterministic IDs | "SHA-256(source_type:source_id:metric_id)[:16]" |
| Observation.source_type | §10.1 Source Types | "commit, file, branch, tag" |
| Observation.source_id | §10.2 Deterministic IDs | "commit SHA, file path, branch name" |
| Observation.metric_id | §10.3 Metric Registry | "M-01 through M-07, frozen" |
| Observation.value | §10.4 Value Domain | "Float, non-negative for most metrics" |
| Observation.unit | §10.5 Units | "Per-metric unit: count, ratio, percentage, score" |
| Observation.timestamp | §10.6 Temporal | "Commit author date in UTC" |
| Observation.quality | §10.7 Quality | "complete, estimated, missing, derived" |
| Observation.metadata | §10.8 Metadata | "Extractor-specific context" |
| Observation.provenance | §10.9 Provenance | "How observation was produced" |
| ObservationWindow | §11 Windowing | "Temporal, commit-count, hybrid strategies" |
| ObservationCollection | §12 Storage | "Indexed container for observations" |
| ObservationStore | §13 Store Interface | "In-memory with optional JSON persistence" |
| Adapter Layer | §14 Adapter | "Translation shim for backward compatibility" |

### 2.2 OEAS Derivations

| ODSS Entity | OEAS Layer | OEAS Contract |
|-------------|-----------|---------------|
| Observation | L2 Observation | Atomic data unit produced by extractors |
| ObservationCollection | L3 Storage | Indexed container managed by ObservationStore |
| ObservationWindow | L4 Window | Output of IWindowBuilder.build() |
| MetricDataFrame | L5 Adapter | Input to DetectorAdapter.to_metric_dataframe() |
| Observation | L5 Adapter | Input to DetectorAdapter.to_paired_observations() |
| ObservationStore | L3 Storage | Interface contract IObservationStore |
| Observation | L1 Extraction | Output of IObservationExtractor.extract() |

### 2.3 Invariant Derivations

| Invariant | ODSS Enforcement |
|-----------|-----------------|
| INV-1: Observation immutability | Observation object is immutable after creation; all fields are final |
| INV-2: Deterministic extraction | Same input always produces same Observation objects |
| INV-3: Stable ordering | Observations sorted by source_id within each window |
| INV-4: Window purity | Each observation belongs to exactly one window |
| INV-5: Detector isolation | Detector receives MetricDataFrame, never touches ObservationStore |
| INV-6: Reproducibility | Seed-controlled extraction produces identical results |
| INV-7: No aggregation before persistence | Raw observations stored first; aggregation is a downstream operation |
| INV-8: Schema forward compatibility | Unknown fields preserved but never interpreted |

---

## 3. Observability Principles

### 3.1 Atomic Observations

Every observation represents a single, indivisible data point extracted from a single source at a single point in time. Observations cannot be subdivided. This principle ensures that every observation carries sufficient statistical weight for detector execution.

### 3.2 Source Traceability

Every observation must be traceable to its exact source (commit SHA, file path, branch name). This enables reproducibility: given the same repository state, the same observations can be re-extracted.

### 3.3 Value Immutability

Once an observation is created, its value cannot change. If a correction is needed, a new observation is created with provenance pointing to the correction event. This ensures that detector results are always reproducible from a fixed observation set.

### 3.4 Schema as Contract

The ODSS is a contract between producers (extractors) and consumers (detectors, adapters, scoring engines). Both parties must agree on field names, types, and constraints. Violations are detected at validation time, not at runtime.

### 3.5 Forward Compatibility Unknowns Are Preserved

When a consumer encounters fields it does not recognize (from a future schema version), it must preserve those fields without interpreting them. This prevents data loss during schema evolution and enables incremental adoption of new fields.

---

## 4. Domain Model Overview

### 4.1 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Repository                              │
│  (top-level container for one analysis run)                  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐   │
│  │              ObservationCollection                     │   │
│  │  (all observations for this repository)                │   │
│  │                                                        │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │           ObservationWindow [w00]                │   │   │
│  │  │  (observations in window 00)                     │   │   │
│  │  │                                                   │   │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │   │   │
│  │  │  │Observation│  │Observation│  │Observation│ ... │   │   │
│  │  │  │ obs-a1b2  │  │ obs-c3d4  │  │ obs-e5f6  │      │   │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘      │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  │                                                        │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │           ObservationWindow [w01]                │   │   │
│  │  │  ...                                             │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Entity Summary

| Entity | Cardinality | Description |
|--------|-------------|-------------|
| Repository | 1 per analysis | Top-level container; holds one ObservationCollection |
| ObservationCollection | 1 per Repository | All observations for one repository; indexed by window, metric, source |
| ObservationWindow | 0..* per Collection | Time-bounded or commit-bounded group of observations |
| Observation | 1..* per Window | Single data point extracted from one source at one time |
| ObservationIdentifier | 1 per Observation | Deterministic ID encoding source and metric |
| ObservationType | 1 per Observation | Classification of observation source (commit, file, branch, tag) |
| ObservationValue | 1 per Observation | The numeric measurement extracted |
| ObservationUnit | 1 per Observation | Unit of measurement for the value |
| ObservationQuality | 1 per Observation | Data quality indicator (complete, estimated, missing, derived) |
| ObservationMetadata | 0..1 per Observation | Extractor-specific contextual information |
| ObservationStatistics | 0..1 per Window | Aggregated statistics for a window (mean, std, min, max, n) |
| ObservationProvenance | 1 per Observation | How this observation was produced (extractor, seed, timestamp) |
| ObservationRelationships | 0..* per Observation | Links to related observations (file→commit, derived-from) |
| ObservationExtensions | 0..* per Observation | Future extension points |

---

## 5. Schema Hierarchy

### 5.1 Layer Structure

The schema follows a strict containment hierarchy. Each layer owns the layer below it. No circular references are permitted.

```
Repository
  └── ObservationCollection
        ├── ObservationWindow [w00]
        │     ├── Observation [obs-001]
        │     │     ├── ObservationIdentifier
        │     │     ├── ObservationType
        │     │     ├── ObservationValue
        │     │     ├── ObservationUnit
        │     │     ├── ObservationQuality
        │     │     ├── ObservationMetadata (optional)
        │     │     ├── ObservationProvenance
        │     │     ├── ObservationRelationships (optional)
        │     │     └── ObservationExtensions (optional)
        │     ├── Observation [obs-002]
        │     │     └── ...
        │     └── ObservationStatistics (optional)
        ├── ObservationWindow [w01]
        │     └── ...
        └── ObservationStatistics (optional, collection-wide)
```

### 5.2 Containment Rules

| Rule | Description |
|------|-------------|
| R-1 | A Repository contains exactly one ObservationCollection |
| R-2 | An ObservationCollection contains zero or more ObservationWindows |
| R-3 | An ObservationWindow contains one or more Observations |
| R-4 | An Observation belongs to exactly one ObservationWindow |
| R-5 | An Observation contains exactly one ObservationIdentifier |
| R-6 | An Observation contains exactly one ObservationType |
| R-7 | An Observation contains exactly one ObservationValue |
| R-8 | An Observation contains exactly one ObservationUnit |
| R-9 | An Observation contains exactly one ObservationQuality |
| R-10 | An Observation contains zero or one ObservationMetadata |
| R-11 | An Observation contains exactly one ObservationProvenance |
| R-12 | An Observation contains zero or more ObservationRelationships |
| R-13 | An Observation contains zero or more ObservationExtensions |
| R-14 | An ObservationWindow contains zero or one ObservationStatistics |
| R-15 | An ObservationCollection contains zero or one collection-wide ObservationStatistics |

---

## 6. Repository (Top-Level Container)

### 6.1 Purpose

The Repository is the top-level container for one analysis run. It represents the git repository being analyzed and holds the complete ObservationCollection for that repository.

### 6.2 Fields

| Field | Data Type | Required | Description |
|-------|-----------|----------|-------------|
| repository_id | string | Yes | Unique identifier for this repository (e.g., "Samragya013/miee") |
| repository_url | string | Yes | Full URL of the git repository |
| repository_name | string | Yes | Human-readable repository name |
| repository_path | string | Yes | Local path where repository is cloned |
| default_branch | string | Yes | Default branch name (e.g., "main", "master") |
| analysis_id | string | Yes | Unique identifier for this analysis run |
| analysis_timestamp | ISO-8601 datetime | Yes | When this analysis was initiated |
| config_hash | string | Yes | SHA-256 hash of the configuration used |
| collection | ObservationCollection | Yes | The observation collection for this repository |

### 6.3 Constraints

| Constraint | Rule |
|-----------|------|
| C-1 | repository_id MUST be non-empty |
| C-2 | repository_url MUST be a valid URL |
| C-3 | repository_path MUST be a valid filesystem path |
| C-4 | analysis_id MUST be unique across all analyses |
| C-5 | config_hash MUST be a 64-character hex string |
| C-6 | collection MUST not be null |

### 6.4 Relationships

| Relationship | Target | Cardinality |
|-------------|--------|-------------|
| owns | ObservationCollection | 1:1 |
| derives_from | Configuration | 1:1 |
| analyzes | Git Repository | 1:1 |

---

## 7. ObservationCollection

### 7.1 Purpose

The ObservationCollection is the indexed container that holds all observations for one repository analysis. It provides lookup by window, by metric, and by source. It is the primary data structure managed by the ObservationStore.

### 7.2 Fields

| Field | Data Type | Required | Description |
|-------|-----------|----------|-------------|
| collection_id | string | Yes | Deterministic ID: sha256(repository_id:analysis_id)[:16] |
| repository_id | string | Yes | Reference to parent repository |
| analysis_id | string | Yes | Reference to analysis run |
| windows | list<ObservationWindow> | Yes | Ordered list of observation windows |
| total_observations | integer | Yes | Total count of observations across all windows |
| total_metrics | integer | Yes | Count of distinct metric IDs present |
| extraction_timestamp | ISO-8601 datetime | Yes | When extraction completed |
| schema_version | string | Yes | ODSS schema version (e.g., "1.0.0") |

### 7.3 Indexing

The collection maintains three internal indices for efficient lookup:

| Index | Key | Lookup Pattern |
|-------|-----|----------------|
| By Window | window_id | collection.get_window("w00") |
| By Metric | metric_id | collection.get_observations_by_metric("M-02") |
| By Source | source_type + source_id | collection.get_observations_by_source("commit", "abc123") |

### 7.4 Constraints

| Constraint | Rule |
|-----------|------|
| C-1 | windows MUST be sorted by window_id |
| C-2 | total_observations MUST equal sum of observations across all windows |
| C-3 | total_metrics MUST be >= 1 |
| C-4 | collection_id MUST be deterministic (same input → same ID) |
| C-5 | schema_version MUST follow semver |

---

## 8. ObservationWindow

### 8.1 Purpose

The ObservationWindow groups observations that fall within a specific temporal or commit-count boundary. Windows are the unit of analysis for detectors. Each window contains enough observations to support statistical inference.

### 8.2 Fields

| Field | Data Type | Required | Description |
|-------|-----------|----------|-------------|
| window_id | string | Yes | Unique window identifier (e.g., "w00", "w01", "w99") |
| window_index | integer | Yes | Zero-based index of this window in the collection |
| strategy | string | Yes | Windowing strategy: "temporal", "commit_count", "hybrid" |
| start_boundary | ISO-8601 datetime | Yes | Inclusive start of the window |
| end_boundary | ISO-8601 datetime | Yes | Inclusive end of the window |
| start_commit | string | No | First commit SHA in this window (if commit-based) |
| end_commit | string | No | Last commit SHA in this window (if commit-based) |
| observations | list<Observation> | Yes | Observations in this window |
| observation_count | integer | Yes | Count of observations in this window |
| metrics_present | list<string> | Yes | Distinct metric IDs in this window |
| statistics | ObservationStatistics | No | Aggregated statistics for this window |
| metadata | map<string, string> | No | Window-specific metadata |

### 8.3 Window ID Format

The window ID follows the pattern `^w[0-9]+$` (e.g., `w00`, `w01`, `w99`, `w100`). The pattern allows variable-length digits to support repositories with 100+ windows.

### 8.4 Constraints

| Constraint | Rule |
|-----------|------|
| C-1 | window_id MUST match `^w[0-9]+$` |
| C-2 | window_index MUST be zero-based and sequential |
| C-3 | start_boundary MUST be <= end_boundary |
| C-4 | observations MUST be sorted by observation.timestamp |
| C-5 | observation_count MUST equal len(observations) |
| C-6 | metrics_present MUST contain only valid metric IDs |
| C-7 | Each observation MUST belong to exactly one window |
| C-8 | Windows MUST NOT overlap |

### 8.5 Minimum Window Gate

Per AFD §Step 8, a window must contain at least 2 observations to be valid for detector execution. Windows with fewer than 2 observations are flagged but not removed; the detector layer enforces the minimum sample size requirement.

---

## 9. Observation (Canonical Object)

### 9.1 Purpose

The Observation is the atomic data unit of the MIIE Observation Engine. It represents a single data point extracted from a single source at a single point in time. Every detector, scoring engine, and explanation engine operates on Observations.

### 9.2 Complete Field Definition

This is the canonical definition. Every field is documented with Purpose, Data Type, Allowed Values, Required/Optional, Constraints, Validation, Default, Relationships, Serialization, and Evolution guidance.

---

#### 9.2.1 observation_id

| Property | Value |
|----------|-------|
| **Purpose** | Uniquely and reproducibly identify this observation |
| **Data Type** | string |
| **Allowed Values** | 16-character lowercase hex string |
| **Required/Optional** | Required |
| **Constraints** | Deterministic; same input always produces same ID |
| **Validation** | Must match `^[0-9a-f]{16}$` |
| **Default** | Computed at creation time |
| **Relationships** | Derived from source_type, source_id, metric_id |
| **Serialization** | JSON string |
| **Evolution** | Format is fixed; length may increase in v2.0 |

**Computation**: `observation_id = sha256(f"{source_type}:{source_id}:{metric_id}")[:16]`

---

#### 9.2.2 source_type

| Property | Value |
|----------|-------|
| **Purpose** | Classify the type of source from which this observation was extracted |
| **Data Type** | string (enum) |
| **Allowed Values** | `"commit"`, `"file"`, `"branch"`, `"tag"` |
| **Required/Optional** | Required |
| **Constraints** | Must be one of the allowed values |
| **Validation** | Must be in the set of allowed source types |
| **Default** | `"commit"` (primary extraction mode) |
| **Relationships** | Determines the format of source_id |
| **Serialization** | JSON string |
| **Evolution** | New values may be added in v1.6 (e.g., `"pull_request"`, `"issue"`) |

---

#### 9.2.3 source_id

| Property | Value |
|----------|-------|
| **Purpose** | Identify the specific source unit (commit SHA, file path, etc.) |
| **Data Type** | string |
| **Allowed Values** | Commit SHA (40-char hex), file path (relative), branch name, tag name |
| **Required/Optional** | Required |
| **Constraints** | Must be non-empty; format depends on source_type |
| **Validation** | If source_type is "commit", must match `^[0-9a-f]{40}$`. If "file", must be a valid relative path. |
| **Default** | None |
| **Relationships** | Paired with source_type to form unique source identification |
| **Serialization** | JSON string |
| **Evolution** | None anticipated |

---

#### 9.2.4 metric_id

| Property | Value |
|----------|-------|
| **Purpose** | Identify which metric this observation measures |
| **Data Type** | string (enum) |
| **Allowed Values** | `"M-01"`, `"M-02"`, `"M-03"`, `"M-04"`, `"M-05"`, `"M-06"`, `"M-07"` |
| **Required/Optional** | Required |
| **Constraints** | Must be in the frozen metric registry |
| **Validation** | Must match the metric registry (MIIE-METRIC-REGISTRY-1.0) |
| **Default** | None |
| **Relationships** | Determines allowed values, unit, and extraction method |
| **Serialization** | JSON string |
| **Evolution** | New metrics may be added in future versions via registry update |

---

#### 9.2.5 value

| Property | Value |
|----------|-------|
| **Purpose** | The numeric measurement extracted for this metric from this source |
| **Data Type** | float |
| **Allowed Values** | Any IEEE 754 double-precision float; specific ranges depend on metric_id |
| **Required/Optional** | Required |
| **Constraints** | Must be finite (not NaN, not Inf) |
| **Validation** | `math.isfinite(value)` must be True |
| **Default** | None (observation must have a value) |
| **Relationships** | Interpreted in conjunction with unit and metric_id |
| **Serialization** | JSON number |
| **Evolution** | None anticipated |

**Per-Metric Value Ranges**:

| metric_id | Typical Range | Unit | Notes |
|-----------|---------------|------|-------|
| M-01 | 0.0 – 1.0 | ratio | Code coverage proportion |
| M-02 | 0 – ∞ | count | Lines of code |
| M-03 | 0 – 1.0 | ratio | PR merge time proportion |
| M-04 | 0.0 – 1.0 | ratio | Code review coverage |
| M-05 | 0 – ∞ | count | Issue resolution time (hours) |
| M-06 | 0.0 – 1.0 | ratio | Commit message quality |
| M-07 | 0.0 – 1.0 | ratio | Test coverage ratio |

---

#### 9.2.6 unit

| Property | Value |
|----------|-------|
| **Purpose** | Specify the unit of measurement for the value |
| **Data Type** | string (enum) |
| **Allowed Values** | `"count"`, `"ratio"`, `"percentage"`, `"score"`, `"hours"`, `"lines"`, `"bytes"` |
| **Required/Optional** | Required |
| **Constraints** | Must be consistent with metric_id |
| **Validation** | Must match the expected unit for the given metric_id |
| **Default** | Determined by metric_id |
| **Relationships** | Constrains interpretation of value |
| **Serialization** | JSON string |
| **Evolution** | New units may be added for new metrics |

---

#### 9.2.7 timestamp

| Property | Value |
|----------|-------|
| **Purpose** | Record when this observation's source was created |
| **Data Type** | ISO-8601 datetime string |
| **Allowed Values** | Any valid ISO-8601 datetime with timezone |
| **Required/Optional** | Required |
| **Constraints** | Must be in UTC or have explicit timezone offset |
| **Validation** | Must parse as valid ISO-8601 datetime |
| **Default** | None |
| **Relationships** | Used for temporal windowing |
| **Serialization** | JSON string (ISO-8601 format) |
| **Evolution** | None anticipated |

---

#### 9.2.8 quality

| Property | Value |
|----------|-------|
| **Purpose** | Indicate the data quality of this observation |
| **Data Type** | string (enum) |
| **Allowed Values** | `"complete"`, `"estimated"`, `"missing"`, `"derived"` |
| **Required/Optional** | Required |
| **Constraints** | Must be one of the allowed values |
| **Validation** | Must be in the quality enum |
| **Default** | `"complete"` |
| **Relationships** | Determines how downstream consumers should interpret the value |
| **Serialization** | JSON string |
| **Evolution** | New quality levels may be added (e.g., `"interpolated"`) |

**Quality Semantics**:

| Quality | Meaning | Downstream Treatment |
|---------|---------|---------------------|
| complete | Directly extracted from source | Full weight in analysis |
| estimated | Computed from partial data | Flagged, may be downweighted |
| missing | Source data unavailable | Excluded from statistical tests |
| derived | Computed from other observations | Tracked via provenance chain |

---

#### 9.2.9 metadata (optional)

| Property | Value |
|----------|-------|
| **Purpose** | Provide extractor-specific contextual information |
| **Data Type** | map<string, any> |
| **Allowed Values** | Any JSON-serializable key-value pairs |
| **Required/Optional** | Optional |
| **Constraints** | Keys must be strings; values must be JSON-serializable |
| **Validation** | No schema validation on content (open-ended) |
| **Default** | Empty map |
| **Relationships** | Depends on source_type and extraction method |
| **Serialization** | JSON object |
| **Evolution** | Extractors may add new keys without schema changes |

**Standard Metadata Keys** (recommended, not enforced):

| Key | Type | Description |
|-----|------|-------------|
| commit_message | string | First line of commit message |
| author_name | string | Commit author name |
| author_email | string | Commit author email |
| files_changed | integer | Number of files changed in commit |
| insertions | integer | Lines added in commit |
| deletions | integer | Lines removed in commit |
| file_path | string | Relative path of file (for file-level observations) |
| file_extension | string | File extension (e.g., ".py", ".ts") |
| is_merge | boolean | Whether this commit is a merge commit |

---

#### 9.2.10 provenance

| Property | Value |
|----------|-------|
| **Purpose** | Record how this observation was produced |
| **Data Type** | ObservationProvenance (see §19) |
| **Allowed Values** | ObservationProvenance object |
| **Required/Optional** | Required |
| **Constraints** | Must not be null |
| **Validation** | Must contain valid extractor_id, extraction_timestamp, seed |
| **Default** | None |
| **Relationships** | Links observation to its production context |
| **Serialization** | JSON object (see §19) |
| **Evolution** | None anticipated |

---

#### 9.2.11 relationships (optional)

| Property | Value |
|----------|-------|
| **Purpose** | Link this observation to related observations |
| **Data Type** | list<ObservationRelationship> |
| **Allowed Values** | List of relationship objects |
| **Required/Optional** | Optional |
| **Constraints** | Each relationship must reference a valid observation_id |
| **Validation** | Referenced observation_ids must exist in the collection |
| **Default** | Empty list |
| **Relationships** | Forms a directed graph of observation dependencies |
| **Serialization** | JSON array |
| **Evolution** | New relationship types may be added |

---

#### 9.2.12 extensions (optional)

| Property | Value |
|----------|-------|
| **Purpose** | Provide extension points for future schema versions |
| **Data Type** | map<string, any> |
| **Allowed Values** | Any JSON-serializable key-value pairs |
| **Required/Optional** | Optional |
| **Constraints** | Keys must be strings; values must be JSON-serializable |
| **Validation** | No schema validation on content (open-ended) |
| **Default** | Empty map |
| **Relationships** | None (self-contained) |
| **Serialization** | JSON object |
| **Evolution** | Future versions may promote extension keys to top-level fields |

---

## 10. Observation Identifier

### 10.1 Purpose

The ObservationIdentifier uniquely and reproducibly identifies each observation. It is computed deterministically from the source and metric, ensuring that the same extraction always produces the same ID.

### 10.2 Computation

```
observation_id = sha256(f"{source_type}:{source_id}:{metric_id}")[:16]
```

### 10.3 Properties

| Property | Value |
|----------|-------|
| Algorithm | SHA-256 |
| Output format | 16-character lowercase hex string |
| Collision resistance | 2^64 (birthday bound) |
| Determinism | Same input always produces same output |
| Reversibility | Irreversible (hash function) |

### 10.4 Examples

| source_type | source_id | metric_id | observation_id |
|-------------|-----------|-----------|----------------|
| commit | a1b2c3d4e5f6789012345678901234567890abcd | M-02 | `8f4e2a1b9c7d3e5f` |
| file | src/main.py | M-07 | `3a7b9c1d5e8f2a4b` |

### 10.5 Design Rationale

| Alternative | Reason for Rejection |
|-------------|---------------------|
| UUID v4 | Non-deterministic; same extraction produces different IDs |
| Sequential integer | Not reproducible across runs; requires persistent state |
| Full SHA-256 | 64 chars is excessive for display; 16 chars provides sufficient collision resistance |
| Content hash | Changing a metric value would change the ID, breaking reproducibility |

---

## 11. Observation Type

### 11.1 Purpose

The ObservationType classifies the source from which an observation was extracted. This determines how the observation is interpreted, windowed, and used by detectors.

### 11.2 Enum Values

| Value | Description | Typical Source | Typical Metrics |
|-------|-------------|---------------|-----------------|
| commit | Extracted from git commit data | git log output | M-02, M-06, M-07 |
| file | Extracted from file-level data | git diff, file stats | M-01, M-07 |
| branch | Extracted from branch metadata | git branch | M-03, M-04 |
| tag | Extracted from release tag data | git tag | M-03, M-05 |

### 11.3 Source ID Format by Type

| source_type | source_id format | Example |
|-------------|-----------------|---------|
| commit | 40-character hex SHA | `a1b2c3d4e5f6789012345678901234567890abcd` |
| file | Relative path from repo root | `src/miie/cli.py` |
| branch | Branch name | `feature/observation-engine` |
| tag | Tag name | `v1.0.0` |

### 11.4 Evolution

| Version | Planned Types |
|---------|---------------|
| v1.5 | commit, file, branch, tag |
| v1.6 | + pull_request, issue, review |
| v2.0 | + deployment, build, alert |

---

## 12. Observation Value

### 12.1 Purpose

The ObservationValue is the numeric measurement extracted for a metric from a source. It is the core data that detectors analyze.

### 12.2 Type

IEEE 754 double-precision floating-point (64-bit).

### 12.3 Constraints

| Constraint | Rule |
|-----------|------|
| Finite | `math.isfinite(value)` must be True |
| Not NaN | NaN values must be stored as quality="missing" with value=0.0 |
| Not Inf | Infinite values must be stored as quality="estimated" with a bounded replacement |
| Non-negative | Most metrics (M-01, M-02, M-03, M-04, M-05, M-06, M-07) produce non-negative values |

### 12.4 Missing Value Handling

When an observation cannot be extracted (e.g., file not found, API timeout), the observation is stored with:

| Field | Value |
|-------|-------|
| value | 0.0 |
| quality | `"missing"` |

This ensures the observation exists in the collection (preserving sample size) while signaling to consumers that the value is not real.

---

## 13. Observation Unit

### 13.1 Purpose

The ObservationUnit specifies the unit of measurement for the observation value. This ensures correct interpretation and comparison.

### 13.2 Enum Values

| Value | Description | Typical Metrics |
|-------|-------------|-----------------|
| count | Absolute count | M-02 (lines of code), M-05 (issue resolution time) |
| ratio | Proportion (0.0–1.0) | M-01 (coverage), M-03 (merge time), M-04 (review coverage), M-06 (commit quality), M-07 (test coverage) |
| percentage | Percentage (0–100) | M-01 (if expressed as %) |
| score | Normalized score (0.0–1.0) | M-06 (commit message quality) |
| hours | Time duration | M-05 (issue resolution time) |
| lines | Line count | M-02 (lines of code) |
| bytes | Byte count | File size observations |

### 13.3 Metric-to-Unit Mapping

| metric_id | Default Unit | Alternate Units |
|-----------|-------------|-----------------|
| M-01 | ratio | percentage |
| M-02 | lines | count, bytes |
| M-03 | ratio | hours |
| M-04 | ratio | percentage |
| M-05 | hours | count |
| M-06 | score | ratio |
| M-07 | ratio | percentage |

---

## 14. Observation Quality

### 14.1 Purpose

The ObservationQuality indicates the reliability of the observation value. Consumers use quality to decide whether to include an observation in statistical analysis.

### 14.2 Enum Values

| Value | Description | Extraction Context | Downstream Treatment |
|-------|-------------|-------------------|---------------------|
| complete | Value directly extracted from source | Normal extraction | Full weight |
| estimated | Value computed from partial data | Fallback extraction | Flagged, may be downweighted |
| missing | Source data unavailable | Extraction failure | Excluded from statistical tests |
| derived | Value computed from other observations | Aggregation step | Tracked via provenance |

### 14.3 Quality Determination Rules

| Condition | Quality Assignment |
|-----------|-------------------|
| Git command succeeded, data present | complete |
| Git command succeeded, data partial | estimated |
| Git command failed or data absent | missing |
| Value computed from other observations | derived |

---

## 15. Observation Attributes

### 15.1 Purpose

Observation Attributes provide additional context about the observation that is not captured by the core fields. Attributes are extractor-specific and may vary by source_type.

### 15.2 Standard Attributes by Source Type

#### 15.2.1 Commit Attributes

| Attribute | Data Type | Description |
|-----------|-----------|-------------|
| commit_message | string | First line of commit message |
| commit_body | string | Remaining lines of commit message |
| author_name | string | Commit author name |
| author_email | string | Commit author email |
| author_date | ISO-8601 datetime | Author date |
| committer_name | string | Committer name |
| committer_email | string | Committer email |
| committer_date | ISO-8601 datetime | Committer date |
| files_changed | integer | Number of files changed |
| insertions | integer | Lines added |
| deletions | integer | Lines removed |
| is_merge | boolean | Whether this is a merge commit |
| merge_parents | list<string> | Parent commit SHAs (for merges) |
| tree_hash | string | Git tree hash |

#### 15.2.2 File Attributes

| Attribute | Data Type | Description |
|-----------|-----------|-------------|
| file_path | string | Relative path from repo root |
| file_name | string | Filename only |
| file_extension | string | File extension |
| file_size | integer | File size in bytes |
| file_lines | integer | Total lines in file |
| is_binary | boolean | Whether file is binary |
| language | string | Detected programming language |

#### 15.2.3 Branch Attributes

| Attribute | Data Type | Description |
|-----------|-----------|-------------|
| branch_name | string | Full branch name |
| branch_point | string | Commit where branch diverged |
| is_default | boolean | Whether this is the default branch |
| is_protected | boolean | Whether branch has protection rules |

#### 15.2.4 Tag Attributes

| Attribute | Data Type | Description |
|-----------|-----------|-------------|
| tag_name | string | Full tag name |
| tag_message | string | Tag annotation message |
| tagger_name | string | Tag creator name |
| tagger_date | ISO-8601 datetime | Tag creation date |
| is_annotated | boolean | Whether tag is annotated |

---

## 16. Observation Tags

### 16.1 Purpose

Observation Tags provide a lightweight mechanism for labeling observations with arbitrary categorical metadata. Tags are used for filtering, grouping, and annotation.

### 16.2 Format

Tags are stored as a list of strings. Each tag is a free-form label.

### 16.3 Standard Tags

| Tag | Description |
|-----|-------------|
| `"bot"` | Observation was produced by a bot/automated system |
| `"merge"` | Observation is from a merge commit |
| `"hotfix"` | Observation is from a hotfix commit |
| `"release"` | Observation is from a release commit |
| `"refactor"` | Observation is from a refactoring commit |
| `"test"` | Observation is from a test-related commit |
| `"docs"` | Observation is from a documentation commit |

### 16.4 Constraints

| Constraint | Rule |
|-----------|------|
| Uniqueness | Tags must be unique within an observation |
| Format | Tags must be lowercase alphanumeric with optional hyphens |
| Length | Tags must be 1-64 characters |

---

## 17. Observation Metadata

### 17.1 Purpose

Observation Metadata provides extractor-specific contextual information that enriches the observation without modifying its core value. Metadata is open-ended and may contain any JSON-serializable data.

### 17.2 Structure

Metadata is a map from string keys to JSON-serializable values.

### 17.3 Extraction Source Metadata

Each extractor may attach different metadata. The following are recommended but not required:

| Key | Source | Description |
|-----|--------|-------------|
| extractor_version | All | Version of the extractor that produced this observation |
| extraction_duration_ms | All | Time taken for extraction in milliseconds |
| git_command | Commit | The git command used for extraction |
| raw_output | All | Raw command output (truncated to 1KB) |
| error_message | All | Error message if extraction was partial |

### 17.4 Constraints

| Constraint | Rule |
|-----------|------|
| Size | Metadata must not exceed 10KB per observation |
| Keys | Must be non-empty strings |
| Values | Must be JSON-serializable |
| Immutability | Metadata is immutable after observation creation |

---

## 18. Observation Statistics

### 18.1 Purpose

Observation Statistics provide aggregated summary statistics for a window or collection. These are computed on-demand and cached. They are used by the scoring engine and reporting engine.

### 18.2 Fields

| Field | Data Type | Description |
|-------|-----------|-------------|
| count | integer | Number of observations |
| mean | float | Arithmetic mean of values |
| std | float | Standard deviation of values |
| min | float | Minimum value |
| max | float | Maximum value |
| median | float | Median value |
| q25 | float | 25th percentile |
| q75 | float | 75th percentile |
| skewness | float | Distribution skewness |
| kurtosis | float | Distribution kurtosis |
| unique_sources | integer | Count of distinct source_ids |
| unique_metrics | integer | Count of distinct metric_ids |

### 18.3 Computation Rules

| Rule | Description |
|------|-------------|
| R-1 | Statistics are computed only over observations with quality="complete" |
| R-2 | Missing-quality observations are excluded from statistics |
| R-3 | If fewer than 2 complete observations exist, std is 0.0 |
| R-4 | If fewer than 4 complete observations exist, skewness and kurtosis are 0.0 |
| R-5 | Statistics are computed once and cached |

---

## 19. Observation Provenance

### 19.1 Purpose

Observation Provenance records how an observation was produced. This enables reproducibility, debugging, and audit trails.

### 19.2 Fields

| Field | Data Type | Required | Description |
|-------|-----------|----------|-------------|
| extractor_id | string | Yes | Identifier of the extractor (e.g., "commit_extractor") |
| extractor_version | string | Yes | Version of the extractor |
| extraction_timestamp | ISO-8601 datetime | Yes | When extraction occurred |
| seed | integer | Yes | Random seed used for extraction (0 if deterministic) |
| extraction_method | string | Yes | Specific method used (e.g., "git_log_batch") |
| input_hash | string | No | Hash of the input data used for extraction |
| parent_observation_ids | list<string> | No | IDs of observations this was derived from |

### 19.3 Design Rationale

| Alternative | Reason for Rejection |
|-------------|---------------------|
| No provenance | Cannot reproduce or debug extraction |
| Free-text provenance | Not machine-readable, cannot validate |
| Full input copy | Excessive storage; hash is sufficient |

---

## 20. Observation Relationships

### 20.1 Purpose

Observation Relationships link observations to other observations, forming a directed graph of dependencies. This enables derivation tracking, impact analysis, and dependency resolution.

### 20.2 Relationship Types

| Type | Description | Example |
|------|-------------|---------|
| derived_from | This observation was computed from the referenced observation | Aggregation |
| file_of | This file observation belongs to the referenced commit observation | File→Commit |
| depends_on | This observation's extraction depends on the referenced observation | Sequential extraction |
| supersedes | This observation replaces the referenced observation | Correction |
| related_to | Generic association | Cross-metric correlation |

### 20.3 Structure

| Field | Data Type | Description |
|-------|-----------|-------------|
| target_observation_id | string | ID of the related observation |
| relationship_type | string (enum) | One of the relationship types above |
| confidence | float | Confidence in the relationship (0.0–1.0) |
| metadata | map<string, string> | Additional context |

### 20.4 Constraints

| Constraint | Rule |
|-----------|------|
| Acyclicity | Relationship graph must be acyclic |
| Self-reference | An observation cannot reference itself |
| Valid targets | Referenced observation_ids must exist in the collection |
| Bidirectionality | Relationships are directed; reverse relationships must be explicit |

---

## 21. Observation Extensions

### 21.1 Purpose

Observation Extensions provide a mechanism for future schema versions to add new fields without breaking existing consumers. Extensions are stored as a map and are not interpreted by current-version consumers.

### 21.2 Rules

| Rule | Description |
|------|-------------|
| R-1 | Extension keys must be namespaced (e.g., `"ext.v1_6.new_field"`) |
| R-2 | Extension values must be JSON-serializable |
| R-3 | Extensions must not exceed 5KB per observation |
| R-4 | Consumers must preserve unknown extensions |
| R-5 | Future versions may promote extension keys to top-level fields |

---

## 22. Extraction Source Types

### 22.1 Purpose

This section defines the extraction source types that produce observations. Each source type has a specific extractor, input requirements, and output characteristics.

### 22.2 Commit Extractor

| Property | Value |
|----------|-------|
| Source type | `"commit"` |
| Input | Git repository (local clone) |
| Method | `git log --format=...` with batch windowing |
| Output | One observation per commit per metric |
| Typical metrics | M-02, M-06, M-07 |
| Batch size | Configurable (default: 100 commits per batch) |

### 22.3 File Extractor

| Property | Value |
|----------|-------|
| Source type | `"file"` |
| Input | Git repository (local clone) |
| Method | `git show` or file system read |
| Output | One observation per file per metric |
| Typical metrics | M-01, M-07 |
| Batch size | N/A (per-file extraction) |

### 22.4 Branch Extractor

| Property | Value |
|----------|-------|
| Source type | `"branch"` |
| Input | Git repository (local clone) |
| Method | `git branch -v` |
| Output | One observation per branch per metric |
| Typical metrics | M-03, M-04 |
| Batch size | N/A (per-branch extraction) |

### 22.5 Tag Extractor

| Property | Value |
|----------|-------|
| Source type | `"tag"` |
| Input | Git repository (local clone) |
| Method | `git tag -l -n1` |
| Output | One observation per tag per metric |
| Typical metrics | M-03, M-05 |
| Batch size | N/A (per-tag extraction) |

---

## 23. Extraction Context

### 23.1 Purpose

The Extraction Context captures the parameters under which extraction occurs. This ensures reproducibility: given the same context, the same observations are produced.

### 23.2 Fields

| Field | Data Type | Required | Description |
|-------|-----------|----------|-------------|
| repository_path | string | Yes | Local path to cloned repository |
| metric_list | list<string> | Yes | Metrics to extract |
| since | ISO-8601 datetime | No | Start of extraction window |
| until | ISO-8601 datetime | No | End of extraction window |
| exclude_bots | boolean | Yes | Whether to exclude bot commits |
| seed | integer | Yes | Random seed for reproducibility |
| batch_size | integer | Yes | Number of commits per git log batch |
| max_file_size | integer | Yes | Maximum file size for file extraction (bytes) |
| file_extensions | list<string> | No | File extensions to include (if filtering) |

### 23.3 Reproducibility Contract

Given the same Extraction Context (identical field values), the extraction engine MUST produce identical Observation objects. This is enforced by:

| Mechanism | Field |
|-----------|-------|
| Temporal boundary | since, until |
| Filtering | exclude_bots, file_extensions |
| Determinism | seed |
| Batch control | batch_size |

---

## 24. Window Builder Input

### 24.1 Purpose

The Window Builder Input defines what the window builder receives from the extraction phase. This is the input to the `IWindowBuilder.build()` method.

### 24.2 Fields

| Field | Data Type | Required | Description |
|-------|-----------|----------|-------------|
| observations | list<Observation> | Yes | All extracted observations |
| strategy | string | Yes | Windowing strategy: "temporal", "commit_count", "hybrid" |
| window_size | integer | Yes | Size parameter for windowing |
| commit_threshold | integer | No | Minimum commits per window (hybrid only) |
| max_windows | integer | No | Maximum number of windows |

---

## 25. Window Builder Output

### 25.1 Purpose

The Window Builder Output defines what the window builder produces. This is the output of the `IWindowBuilder.build()` method.

### 25.2 Fields

| Field | Data Type | Required | Description |
|-------|-----------|----------|-------------|
| windows | list<ObservationWindow> | Yes | Ordered list of windows |
| unassigned_observations | list<Observation> | No | Observations that could not be assigned to any window |
| warnings | list<string> | No | Warnings generated during windowing |

### 25.3 Constraints

| Constraint | Rule |
|-----------|------|
| Coverage | Each observation must be in exactly one window or in unassigned |
| Non-overlap | Windows must not overlap |
| Ordering | Windows must be sorted by window_id |
| Minimum size | Each window should contain at least 2 observations (soft constraint) |

---

## 26. Detector Adapter Input

### 26.1 Purpose

The Detector Adapter Input defines what the adapter receives. This is the input to `IDetectorAdapter.to_metric_dataframe()` and `IDetectorAdapter.to_paired_observations()`.

### 26.2 Fields

| Field | Data Type | Required | Description |
|-------|-----------|----------|-------------|
| windows | list<ObservationWindow> | Yes | Windows to translate |
| metric_list | list<string> | Yes | Metrics to include |
| windows_to_analyze | list<string> | No | Specific window IDs to analyze (default: all) |

---

## 27. Detector Adapter Output

### 27.1 Purpose

The Detector Adapter Output defines what the adapter produces. This is the output of the adapter translation methods.

### 27.2 MetricDataFrame Output

| Field | Data Type | Required | Description |
|-------|-----------|----------|-------------|
| metrics | dict<string, dict<string, list<optional<float>>>> | Yes | Aggregated values: metric_id → window_id → [values] |
| window_ids | list<string> | Yes | Ordered window IDs |
| metadata | map<string, string> | No | Adapter metadata |

### 27.3 Paired Observations Output

| Field | Data Type | Required | Description |
|-------|-----------|----------|-------------|
| window_id | string | Yes | Window identifier |
| metric_id | string | Yes | Metric identifier |
| values | list<float> | Yes | All observation values in this window for this metric |
| timestamps | list<ISO-8601 datetime> | Yes | Corresponding timestamps |
| source_ids | list<string> | Yes | Corresponding source IDs |
| quality | list<string> | Yes | Corresponding quality indicators |

---

## 28. Adapter Translation Contract

### 28.1 Purpose

The Adapter Translation Contract defines the rules by which the adapter translates between Observation-based and legacy data formats. This ensures backward compatibility.

### 28.2 Translation Rules

| Rule | Description |
|------|-------------|
| R-1 | All observations in a window for a given metric are aggregated into a single list |
| R-2 | Missing-quality observations are excluded from aggregation |
| R-3 | Values are sorted by timestamp within each metric/window |
| R-4 | The resulting MetricDataFrame has one list per metric per window |
| R-5 | If all observations are missing, the list is empty |
| R-6 | The adapter must not modify the original observations |

### 28.3 Compatibility Guarantees

| Guarantee | Description |
|-----------|-------------|
| Backward compatible | Existing detectors receive the same data format |
| Forward compatible | New observation fields do not break existing detectors |
| Deterministic | Same observations produce the same MetricDataFrame |
| Lossless | All information is preserved in translation |

---

## 29. Observation Store Interface

### 29.1 Purpose

The Observation Store Interface defines the contract for storing and retrieving observations. This is the `IObservationStore` interface from OEAS.

### 29.2 Methods

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| add(observation) | Observation | void | Add an observation to the store |
| add_batch(observations) | list<Observation> | void | Add multiple observations |
| get_by_id(observation_id) | string | Observation | Retrieve observation by ID |
| get_by_window(window_id) | list<Observation> | All observations in a window |
| get_by_metric(metric_id) | list<Observation> | All observations for a metric |
| get_by_source(source_type, source_id) | list<Observation> | All observations for a source |
| count() | integer | Total observation count |
| count_by_window(window_id) | integer | Observation count for a window |
| query(filters) | ObservationQuery | list<Observation> | Complex query |
| serialize() | SerializedStore | Serialize the store for persistence |
| deserialize(data) | SerializedStore | ObservationStore | Restore from serialized form |

### 29.3 Constraints

| Constraint | Rule |
|-----------|------|
| Immutability | Added observations cannot be modified |
| Uniqueness | observation_id must be unique within the store |
| Ordering | Observations are returned in insertion order within each query |
| Thread safety | Store must be thread-safe for concurrent reads |

---

## 30. Observation Engine Input

### 30.1 Purpose

The Observation Engine Input defines the complete input to the Observation Engine. This is the `IObservationEngine.analyze()` method's input.

### 30.2 Fields

| Field | Data Type | Required | Description |
|-------|-----------|----------|-------------|
| context | RepositoryContext | Yes | Repository context from ingestion |
| config | Config | Yes | Analysis configuration |
| metric_list | list<string> | Yes | Metrics to extract |
| window_strategy | string | Yes | Windowing strategy |
| window_size | integer | Yes | Window size parameter |

---

## 31. Observation Engine Output

### 31.1 Purpose

The Observation Engine Output defines the complete output of the Observation Engine. This is what downstream consumers (detectors, scoring, reporting) receive.

### 31.2 Fields

| Field | Data Type | Required | Description |
|-------|-----------|----------|-------------|
| collection | ObservationCollection | Yes | Complete observation collection |
| metric_dataframes | dict<string, MetricDataFrame> | Yes | Legacy format for each detector |
| paired_observations | list<PairedObservations> | Yes | Paired format for each detector |
| statistics | ObservationStatistics | Yes | Collection-wide statistics |
| extraction_summary | ExtractionSummary | Yes | Summary of extraction process |
| warnings | list<string> | No | Warnings during extraction |

### 31.3 ExtractionSummary

| Field | Data Type | Description |
|-------|-----------|-------------|
| total_observations | integer | Total observations extracted |
| observations_by_source_type | map<string, integer> | Count by source type |
| observations_by_metric | map<string, integer> | Count by metric |
| observations_by_quality | map<string, integer> | Count by quality level |
| extraction_duration_ms | integer | Total extraction time |
| window_count | integer | Number of windows created |
| avg_observations_per_window | float | Mean observations per window |

---

## 32. Serialization — JSON Canonical

### 32.1 Purpose

JSON is the primary serialization format for observations. It is human-readable, tool-independent, and widely supported.

### 32.2 Canonical JSON Rules

| Rule | Description |
|------|-------------|
| R-1 | Keys must be sorted lexicographically |
| R-2 | Datetimes must be in ISO-8601 format with timezone |
| R-3 | Floats must use full precision (no truncation) |
| R-4 | Null values must be omitted (not serialized) |
| R-5 | Empty lists must be serialized as `[]` |
| R-6 | Empty maps must be serialized as `{}` |
| R-7 | Booleans must be lowercase (`true`, `false`) |

### 32.3 Example Observation JSON

```json
{
  "observation_id": "8f4e2a1b9c7d3e5f",
  "source_type": "commit",
  "source_id": "a1b2c3d4e5f6789012345678901234567890abcd",
  "metric_id": "M-02",
  "value": 143.0,
  "unit": "lines",
  "timestamp": "2026-06-28T14:30:00Z",
  "quality": "complete",
  "metadata": {
    "commit_message": "Add observation engine PRD",
    "author_name": "Samragya",
    "files_changed": 3,
    "insertions": 250,
    "deletions": 15,
    "is_merge": false
  },
  "provenance": {
    "extractor_id": "commit_extractor",
    "extractor_version": "1.5.0",
    "extraction_timestamp": "2026-06-29T10:00:00Z",
    "seed": 42,
    "extraction_method": "git_log_batch"
  },
  "relationships": [],
  "extensions": {}
}
```

### 32.4 Example Window JSON

```json
{
  "window_id": "w00",
  "window_index": 0,
  "strategy": "commit_count",
  "start_boundary": "2026-01-01T00:00:00Z",
  "end_boundary": "2026-06-28T23:59:59Z",
  "start_commit": "a1b2c3d4...",
  "end_commit": "z9y8x7w6...",
  "observations": [],
  "observation_count": 150,
  "metrics_present": ["M-02", "M-06", "M-07"],
  "statistics": null,
  "metadata": {}
}
```

### 32.5 Example Collection JSON

```json
{
  "collection_id": "a1b2c3d4e5f6g7h8",
  "repository_id": "Samragya013/miee",
  "analysis_id": "run-20260629-100000",
  "windows": [],
  "total_observations": 500,
  "total_metrics": 7,
  "extraction_timestamp": "2026-06-29T10:05:00Z",
  "schema_version": "1.0.0"
}
```

---

## 33. Serialization — MessagePack

### 33.1 Purpose

MessagePack is an alternative binary serialization format for high-performance scenarios. It is more compact than JSON and faster to parse.

### 33.2 Rules

| Rule | Description |
|------|-------------|
| R-1 | Field names must match JSON canonical names |
| R-2 | Datetimes must be serialized as ISO-8601 strings (same as JSON) |
| R-3 | Floats must use 64-bit double precision |
| R-4 | Extension types must use MessagePack extension mechanism |

### 33.3 Usage

MessagePack serialization is opt-in and not used by default. It is recommended for:
- Large observation collections (>10,000 observations)
- Network transfer between services
- Caching layers

---

## 34. Serialization — Binary (Future)

### 34.1 Purpose

Binary serialization is a v2.0 capability for extreme-performance scenarios. It is not part of v1.5.

### 34.2 Planned Formats

| Format | Use Case |
|--------|---------|
| Arrow / Parquet | Columnar storage for analytics |
| Protocol Buffers | gRPC service communication |
| HDF5 | Scientific data storage |

---

## 35. Validation — Required Fields

### 35.1 Purpose

Required field validation ensures every observation has the minimum information needed for downstream processing.

### 35.2 Required Fields

| Field | Validator | Error Code |
|-------|-----------|------------|
| observation_id | `len(s) == 16 and all(c in '0123456789abcdef' for c in s)` | OBS-001 |
| source_type | `s in ["commit", "file", "branch", "tag"]` | OBS-002 |
| source_id | `len(s) > 0` | OBS-003 |
| metric_id | `s in ["M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07"]` | OBS-004 |
| value | `isinstance(v, float) and math.isfinite(v)` | OBS-005 |
| unit | `s in ["count", "ratio", "percentage", "score", "hours", "lines", "bytes"]` | OBS-006 |
| timestamp | Valid ISO-8601 datetime | OBS-007 |
| quality | `s in ["complete", "estimated", "missing", "derived"]` | OBS-008 |
| provenance | Not null | OBS-009 |

---

## 36. Validation — Integrity Checks

### 36.1 Purpose

Integrity checks ensure observation IDs are correctly computed and the observation is self-consistent.

### 36.2 Checks

| Check | Rule | Error Code |
|-------|------|------------|
| ID computation | `sha256(f"{source_type}:{source_id}:{metric_id}")[:16] == observation_id` | OBS-010 |
| Timestamp timezone | Timestamp has explicit timezone or is UTC | OBS-011 |
| Unit consistency | Unit matches the expected unit for metric_id | OBS-012 |
| Source ID format | source_id format matches source_type | OBS-013 |

---

## 37. Validation — Normalization

### 37.1 Purpose

Normalization validation ensures values are within expected ranges for their metrics.

### 37.2 Rules

| Metric | Expected Range | Tolerance | Error Code |
|--------|---------------|-----------|------------|
| M-01 | 0.0 – 1.0 | ±0.001 | OBS-020 |
| M-02 | 0 – ∞ | None | OBS-021 |
| M-03 | 0.0 – 1.0 | ±0.001 | OBS-022 |
| M-04 | 0.0 – 1.0 | ±0.001 | OBS-023 |
| M-05 | 0 – ∞ | None | OBS-024 |
| M-06 | 0.0 – 1.0 | ±0.001 | OBS-025 |
| M-07 | 0.0 – 1.0 | ±0.001 | OBS-026 |

---

## 38. Validation — Consistency Checks

### 38.1 Purpose

Consistency checks ensure observations within a collection are mutually consistent.

### 38.2 Checks

| Check | Rule | Error Code |
|-------|------|------------|
| Window assignment | Each observation appears in exactly one window | OBS-030 |
| Window ordering | Windows are sorted by window_id | OBS-031 |
| Observation ordering | Observations within a window are sorted by timestamp | OBS-032 |
| Metric presence | All observations in a window have valid metric_ids | OBS-033 |
| Source type consistency | All observations with same source_type have compatible source_id formats | OBS-034 |
| Collection total | collection.total_observations == sum(w.observation_count for w in windows) | OBS-035 |

---

## 39. Validation — Cross-Field

### 39.1 Purpose

Cross-field validation ensures relationships between fields are consistent.

### 39.2 Rules

| Rule | Description | Error Code |
|------|-------------|------------|
| source_type → source_id | If source_type is "commit", source_id must be 40-char hex | OBS-040 |
| source_type → source_id | If source_type is "file", source_id must be valid relative path | OBS-041 |
| metric_id → unit | If metric_id is M-02, unit must be "lines" or "count" | OBS-042 |
| quality → value | If quality is "missing", value must be 0.0 | OBS-043 |
| quality → provenance | If quality is "derived", provenance.parent_observation_ids must be non-empty | OBS-044 |
| window → observations | Window.start_boundary <= observation.timestamp <= Window.end_boundary | OBS-045 |

---

## 40. Validation — Schema Evolution

### 40.1 Purpose

Schema evolution validation ensures new schema versions are backward and forward compatible.

### 40.2 Rules

| Rule | Description |
|------|-------------|
| R-1 | New fields must be optional (never required in existing consumers) |
| R-2 | New enum values must be added at the end (never inserted) |
| R-3 | Field types must not change |
| R-4 | Field names must not change |
| R-5 | Required fields in v1.0 must remain required in all future versions |

### 40.3 Version Check

| Version | Minimum Supported Consumer Version | Maximum Supported Producer Version |
|---------|-----------------------------------|-----------------------------------|
| 1.0.0 | 1.0.0 | 1.5.x |
| 1.1.0 | 1.0.0 | 1.6.x |
| 2.0.0 | 2.0.0 | 2.x.x |

---

## 41. Validation — Version Compatibility

### 41.1 Purpose

Version compatibility validation ensures observations produced by one version can be consumed by another.

### 41.2 Rules

| Rule | Description |
|------|-------------|
| R-1 | schema_version must be present in all serialized observations |
| R-2 | Consumers must reject observations with schema_version > consumer's supported version |
| R-3 | Consumers must accept observations with schema_version <= consumer's supported version |
| R-4 | Unknown fields are preserved but not interpreted |
| R-5 | Missing optional fields are filled with defaults |

---

## 42. Schema Versioning Strategy

### 42.1 Version Numbering

The ODSS follows semantic versioning (semver):

| Version Component | Meaning |
|-------------------|---------|
| Major (X.0.0) | Breaking changes (field removal, type change) |
| Minor (0.Y.0) | New fields, new enum values, new relationships |
| Patch (0.0.Z) | Documentation clarifications, validation rule corrections |

### 42.2 Current Version

| Property | Value |
|----------|-------|
| Version | 1.0.0 |
| Status | Canonical |
| Date | 2026-06-29 |
| Breaking changes | None (initial version) |

### 42.3 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-29 | Initial ODSS; 12 core fields, 4 source types, 4 quality levels |

---

## 43. Backward Compatibility Rules

### 43.1 Purpose

Backward compatibility ensures that newer producers can write data that older consumers can read.

### 43.2 Rules

| Rule | Description |
|------|-------------|
| R-1 | New optional fields do not break existing consumers |
| R-2 | New enum values do not break existing consumers (consumers must handle unknown values) |
| R-3 | New relationships do not break existing consumers |
| R-4 | New metadata keys do not break existing consumers |
| R-5 | New extension keys do not break existing consumers |

---

## 44. Forward Compatibility Rules

### 44.1 Purpose

Forward compatibility ensures that older consumers can read data produced by newer producers.

### 44.2 Rules

| Rule | Description |
|------|-------------|
| R-1 | Consumers must preserve unknown fields (not drop them) |
| R-2 | Consumers must not fail on unknown enum values |
| R-3 | Consumers must not fail on unknown metadata keys |
| R-4 | Consumers must not fail on unknown extension keys |
| R-5 | Consumers must use default values for missing optional fields |

---

## 45. Extension Mechanism

### 45.1 Purpose

The extension mechanism allows the ODSS to evolve without breaking existing consumers.

### 45.2 Extension Points

| Extension Point | Mechanism | Example |
|----------------|-----------|---------|
| New fields | Add to Observation as optional | Adding `branch` field in v1.6 |
| New metadata keys | Add to ObservationMetadata | Adding `ci_status` key |
| New relationship types | Add to ObservationRelationshipType | Adding `"blocked_by"` type |
| New source types | Add to ObservationSourceType | Adding `"pull_request"` type |
| New quality levels | Add to ObservationQuality | Adding `"interpolated"` level |
| New extensions | Add to ObservationExtensions | Adding `ext.v2_0.ml_features` |

### 45.3 Promotion Rules

| Rule | Description |
|------|-------------|
| R-1 | Extension fields must be promoted to top-level fields via minor version bump |
| R-2 | Promoted fields must retain their extension key as an alias for one version |
| R-3 | Deprecated fields must be marked but not removed for two minor versions |

---

## 46. Multi-Repository Support

### 46.1 Purpose

Multi-repository support enables cross-repository observation analysis.

### 46.2 Design

| Property | Value |
|----------|-------|
| Storage | One ObservationCollection per repository |
| Cross-repo query | Via workspace-level aggregation |
| Schema | Identical per-repo schema; workspace adds a wrapper |
| Window alignment | Windows are repo-specific; alignment is a workspace concern |

### 46.3 Workspace Wrapper (v2.0)

| Field | Data Type | Description |
|-------|-----------|-------------|
| workspace_id | string | Unique workspace identifier |
| repositories | list<Repository> | Repositories in this workspace |
| alignment_strategy | string | How to align windows across repos |
| cross_repo_observations | list<CrossRepoObservation> | Derived cross-repo observations |

---

## 47. External Data Integration

### 47.1 Purpose

External data integration enables observations from non-git sources (CI, issue trackers, code review).

### 47.2 Integration Points

| Source | Observation Type | Metrics | Status |
|--------|-----------------|---------|--------|
| GitHub API | commit, pull_request | M-03, M-04 | v1.6 |
| Jira API | issue | M-05 | v1.6 |
| CI/CD API | build, deployment | M-01, M-07 | v2.0 |
| Code review API | review | M-04 | v2.0 |

### 47.3 Integration Rules

| Rule | Description |
|------|-------------|
| R-1 | External observations use the same Observation schema |
| R-2 | External observations have source_type reflecting their origin |
| R-3 | External observations have provenance tracking the integration method |
| R-4 | External data does not override git-extracted data |

---

## 48. Plugin Support

### 48.1 Purpose

Plugin support enables community-contributed extractors and detectors.

### 48.2 Plugin Contract

| Property | Description |
|----------|-------------|
| Interface | Implement `IObservationExtractor` |
| Schema | Must produce observations conforming to this ODSS |
| Registration | Plugin declares supported source_types and metric_ids |
| Validation | Plugin observations are validated against this schema |
| Isolation | Plugin execution is sandboxed |

### 48.3 Plugin Metadata

| Field | Data Type | Description |
|-------|-----------|-------------|
| plugin_id | string | Unique plugin identifier |
| plugin_version | string | Plugin version |
| supported_source_types | list<string> | Source types this plugin handles |
| supported_metrics | list<string> | Metrics this plugin extracts |
| provenance_namespace | string | Namespace for provenance extractor_id |

---

## 49. Performance Considerations

### 49.1 Storage

| Metric | Target | Measurement |
|--------|--------|-------------|
| Observation size (JSON) | < 1KB | Average serialized size |
| Collection size (1000 obs) | < 1MB | Total JSON size |
| Collection size (10000 obs) | < 10MB | Total JSON size |

### 49.2 Processing

| Metric | Target | Measurement |
|--------|--------|-------------|
| Extraction throughput | > 1000 obs/second | Observations extracted per second |
| Windowing latency | < 100ms for 10000 observations | Time to compute windows |
| Adapter translation | < 50ms for 1000 observations | Time to translate to MetricDataFrame |
| Store query | < 10ms for 10000 observations | Time for single query |

### 49.3 Memory

| Metric | Target | Measurement |
|--------|--------|-------------|
| Peak memory (10000 obs) | < 100MB | Resident memory during extraction |
| Store memory (10000 obs) | < 50MB | Store memory footprint |
| Serialization memory | < 2x store memory | Memory during JSON serialization |

---

## 50. Concurrency Considerations

### 50.1 Thread Safety

| Component | Thread Safety | Mechanism |
|-----------|--------------|-----------|
| ObservationStore | Read-write lock | Concurrent reads, exclusive writes |
| Observation (immutable) | Inherently safe | No mutable state |
| ObservationWindow | Read-only after creation | Immutable after build |
| Adapter | Stateless | No shared mutable state |

### 50.2 Parallel Extraction

| Rule | Description |
|------|-------------|
| R-1 | CommitExtractor runs first (provides commit list for windowing) |
| R-2 | Remaining extractors run in parallel after commit extraction |
| R-3 | Each extractor writes to its own partition of the store |
| R-4 | Store merges partitions after all extractors complete |

---

## 51. Security and Privacy

### 51.1 Sensitive Fields

| Field | Sensitivity | Handling |
|-------|------------|----------|
| author_email | PII | Filtered in default output; visible in verbose/forensic |
| commit_message | May contain secrets | Filtered for patterns (tokens, keys) |
| repository_path | Local path | Filtered in default output |

### 51.2 Filtering Rules

| Rule | Description |
|------|-------------|
| R-1 | Default output never exposes local filesystem paths |
| R-2 | Default output never exposes author emails |
| R-3 | Forensic output may expose sensitive fields (user consent required) |
| R-4 | Serialized observations may contain sensitive metadata; protect at rest |

---

## 52. Error Taxonomy

### 52.1 Observation Errors

| Error Code | Description | Severity | Recovery |
|-----------|-------------|----------|----------|
| OBS-001 | Invalid observation_id format | Critical | Re-extract |
| OBS-002 | Invalid source_type | Critical | Re-extract |
| OBS-003 | Empty source_id | Critical | Re-extract |
| OBS-004 | Invalid metric_id | Critical | Re-extract |
| OBS-005 | Invalid value (NaN/Inf) | Warning | Set quality="estimated" |
| OBS-006 | Invalid unit | Critical | Re-extract |
| OBS-007 | Invalid timestamp | Warning | Use extraction timestamp |
| OBS-008 | Invalid quality | Critical | Re-extract |
| OBS-009 | Missing provenance | Critical | Re-extract |
| OBS-010 | ID mismatch | Critical | Re-extract |
| OBS-030 | Duplicate window assignment | Critical | Re-assign |
| OBS-035 | Collection total mismatch | Warning | Recompute |

### 52.2 Error Handling

| Rule | Description |
|------|-------------|
| R-1 | Critical errors cause extraction to fail |
| R-2 | Warnings are logged but do not fail extraction |
| R-3 | All errors are recorded in extraction warnings |
| R-4 | Error counts are reported in ExtractionSummary |

---

## 53. Future Evolution

### 53.1 v1.6 Planned Extensions

| Feature | New Fields | New Source Types | New Metrics |
|---------|-----------|-----------------|-------------|
| Pull request observations | pr_number, pr_state, pr_merged | pull_request | M-03 (enhanced) |
| Issue observations | issue_number, issue_state, issue_labels | issue | M-05 (enhanced) |
| Code review observations | review_state, review_comments | review | M-04 (enhanced) |
| File-level enrichment | file_complexity, file_churn | commit (enhanced) | New metric |

### 53.2 v2.0 Planned Capabilities

| Feature | Description | Schema Impact |
|---------|-------------|---------------|
| Persistent store | Database-backed observation storage | New serialization format |
| Streaming observations | Real-time observation ingestion | New source type: `"stream"` |
| Cross-repo observations | Workspace-level analysis | New wrapper schema |
| ML-based observations | Model-predicted observations | New quality level: `"predicted"` |
| Causal observations | Directed dependency analysis | New relationship type: `"causes"` |

### 53.3 Deprecation Schedule

| Feature | v1.5 | v1.6 | v2.0 |
|---------|------|------|------|
| MetricDataFrame adapter | Supported | Deprecated | Removed |
| Single-value extraction | Fallback | Removed | N/A |
| In-memory store only | Default | Optional disk | Database |

---

## 54. Decision Log

| ID | Decision | Date | Rationale |
|----|----------|------|-----------|
| ODSS-001 | 16-char deterministic observation IDs | 2026-06-29 | Reproducibility + collision resistance |
| ODSS-002 | 4 source types (commit, file, branch, tag) | 2026-06-29 | Covers git-native data; extensible for v1.6 |
| ODSS-003 | 4 quality levels (complete, estimated, missing, derived) | 2026-06-29 | Covers all extraction outcomes |
| ODSS-004 | Immutable observation objects | 2026-06-29 | Reproducibility, thread safety |
| ODSS-005 | JSON canonical serialization | 2026-06-29 | Human-readable, tool-independent |
| ODSS-006 | Open-ended metadata and extensions | 2026-06-29 | Forward compatibility without schema bloat |
| ODSS-007 | Separate provenance object | 2026-06-29 | Audit trail without polluting core fields |
| ODSS-008 | Relationship graph | 2026-06-29 | Dependency tracking, derivation chains |
| ODSS-009 | Semver for schema versioning | 2026-06-29 | Standard, well-understood compatibility rules |
| ODSS-010 | No implementation code in this document | 2026-06-29 | Definition-only; implementation in separate artifacts |

---

## 55. Appendix A — Glossary

| Term | Definition |
|------|-----------|
| Observation | A single data point extracted from a repository source at a single point in time |
| ObservationCollection | Indexed container holding all observations for one repository analysis |
| ObservationWindow | A group of observations within a time or commit-count boundary |
| ObservationStore | In-memory container implementing IObservationStore interface |
| ObservationIdentifier | 16-char deterministic hash uniquely identifying an observation |
| ObservationMetadata | Extractor-specific contextual information attached to an observation |
| ObservationStatistics | Aggregated summary statistics for a window or collection |
| ObservationProvenance | Record of how an observation was produced |
| ObservationRelationship | Link between related observations |
| ObservationExtensions | Future extension points for schema evolution |
| Adapter Layer | Translation shim between Observation Engine and legacy detectors |
| MetricDataFrame | v1.0 data container (aggregated values); backward-compatible target of adapter |
| Deterministic extraction | Same input always produces same output |
| Seed-controlled | Random operations use a fixed seed for reproducibility |
| Commit-level granularity | One observation per commit per metric |
| Window purity | Each observation belongs to exactly one window |
| Schema forward compatibility | Unknown fields preserved but not interpreted |

---

## 56. Appendix B — Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| PRD-v1.5-Observation-Engine | docs/architecture/observation_engine/PRD_v1.5_Observation_Engine.md | Parent requirement document |
| OEAS-v1.5-Observation-Engine | docs/architecture/observation_engine/OEAS_v1.5_Observation_Engine.md | Parent architecture specification |
| RELEASE_BASELINE.md | docs/architecture/RELEASE_BASELINE.md | v1.0.1 baseline definition |
| V1_5_DEVELOPMENT_ENTRY.md | docs/roadmap/V1_5_DEVELOPMENT_ENTRY.md | v1.5 development plan |
| BASELINE_CHANGE_POLICY.md | docs/governance/BASELINE_CHANGE_POLICY.md | Change management rules |
| MIIE Metric Registry | src/miie/schemas/metric_registry.py | Frozen metric definitions |
| MIIE Error Hierarchy | src/miie/contracts/errors.py | Error definitions |

---

## 57. Appendix C — Field Enumeration Tables

### C.1 source_type Values

| Value | Description | Added In |
|-------|-------------|----------|
| commit | Git commit | v1.0.0 |
| file | File-level data | v1.0.0 |
| branch | Branch metadata | v1.0.0 |
| tag | Release tag | v1.0.0 |
| pull_request | Pull request (planned) | v1.6.0 |
| issue | Issue tracker (planned) | v1.6.0 |
| review | Code review (planned) | v1.6.0 |

### C.2 metric_id Values

| Value | Description | Unit | Added In |
|-------|-------------|------|----------|
| M-01 | Code coverage | ratio | v1.0.0 |
| M-02 | Lines of code | lines | v1.0.0 |
| M-03 | PR merge time | ratio | v1.0.0 |
| M-04 | Code review coverage | ratio | v1.0.0 |
| M-05 | Issue resolution time | hours | v1.0.0 |
| M-06 | Commit message quality | score | v1.0.0 |
| M-07 | Test coverage ratio | ratio | v1.0.0 |

### C.3 quality Values

| Value | Description | Downstream Treatment | Added In |
|-------|-------------|---------------------|----------|
| complete | Directly extracted | Full weight | v1.0.0 |
| estimated | Partial data | Flagged | v1.0.0 |
| missing | Data unavailable | Excluded | v1.0.0 |
| derived | Computed from others | Tracked | v1.0.0 |
| interpolated | Interpolated value (planned) | Flagged | v1.6.0 |
| predicted | Model-predicted (planned) | Flagged | v2.0.0 |

### C.4 unit Values

| Value | Description | Added In |
|-------|-------------|----------|
| count | Absolute count | v1.0.0 |
| ratio | Proportion (0.0–1.0) | v1.0.0 |
| percentage | Percentage (0–100) | v1.0.0 |
| score | Normalized score | v1.0.0 |
| hours | Time duration | v1.0.0 |
| lines | Line count | v1.0.0 |
| bytes | Byte count | v1.0.0 |

### C.5 Relationship Type Values

| Value | Description | Added In |
|-------|-------------|----------|
| derived_from | Computed from another observation | v1.0.0 |
| file_of | File belongs to commit | v1.0.0 |
| depends_on | Extraction dependency | v1.0.0 |
| supersedes | Replaces another observation | v1.0.0 |
| related_to | Generic association | v1.0.0 |
| causes | Causal relationship (planned) | v2.0.0 |

### C.6 Error Code Ranges

| Range | Category |
|-------|----------|
| OBS-001 to OBS-009 | Required field validation |
| OBS-010 to OBS-019 | Integrity checks |
| OBS-020 to OBS-029 | Normalization checks |
| OBS-030 to OBS-039 | Consistency checks |
| OBS-040 to OBS-049 | Cross-field checks |

---

## 58. Appendix D — Mapping to Existing Schemas

### D.1 Mapping to v1.0 MetricDataFrame

| MetricDataFrame Field | ODSS Equivalent | Transformation |
|----------------------|-----------------|----------------|
| metrics[metric_id][window_id] | Observation.value where metric_id=X and window_id=Y | Adapter aggregates: `[obs.value for obs in window if obs.metric_id == X]` |
| metadata[metric_id] | Observation.metadata | Direct copy |
| run_id | ObservationCollection.analysis_id | Direct mapping |
| timestamp | ObservationCollection.extraction_timestamp | Direct mapping |

### D.2 Mapping to v1.0 DetectorResult

| DetectorResult Field | ODSS Source | Transformation |
|---------------------|-------------|----------------|
| detector_id | DetectorAdapter.to_metric_dataframe() metadata | Pass-through |
| anomalies | Observations with quality="complete" in anomalous windows | Adapter filtering |
| scores | ObservationStatistics fields | Adapter aggregation |

### D.3 Mapping to v1.0 EvidencePackage

| EvidencePackage Field | ODSS Source | Transformation |
|----------------------|-------------|----------------|
| metric_values | Observation.value fields | Direct extraction |
| window_ids | ObservationWindow.window_id | Direct mapping |
| detector_results | DetectorAdapter output | Pass-through |

---

*End of Document*

---

**Document History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-06-29 | MIIE Engineering | Initial ODSS; canonical observation data model |

**Approval**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Engineering Lead | | | |
| Science Lead | | | |
| Governance | | | |
