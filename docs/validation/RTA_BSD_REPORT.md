# MIIE Repository Implementation vs BSD-Engineering v1.0 Comparison Report

## Overview

This report compares the MIIE repository implementation (JSON schemas and Python dataclasses) against the BSD-Engineering v1.0 specification for the following core objects:
- RepositoryContext
- MetricDataFrame
- DetectorResult (DetectorResults in BSD)
- EvidencePackage

Comparison criteria include field names, field types, required fields, serialization rules, and validation constraints.

## 1. RepositoryContext

### BSD-Engineering v1.0 Specification (Section 5)

**JSON Schema:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RepositoryContext",
  "type": "object",
  "required": [
    "repo_id",
    "local_path",
    "is_remote",
    "total_commits",
    "first_commit_date",
    "last_commit_date",
    "contributor_count",
    "is_shallow",
    "is_fork"
  ],
  "properties": {
    "repo_id": {"type": "string", "description": "SHA-256 of remote URL or absolute path. Unique within analysis."},
    "local_path": {"type": "string", "format": "uri-reference", "description": "Absolute path to repository root."},
    "is_remote": {"type": "boolean", "description": "True if cloned from remote URL."},
    "remote_url": {"type": "string", "format": "uri", "description": "Original remote URL if applicable."},
    "total_commits": {"type": "integer", "minimum": 10, "description": "Total non-merge commits in history."},
    "first_commit_date": {"type": "string", "format": "date-time", "description": "Timestamp of first commit (UTC)."},
    "last_commit_date": {"type": "string", "format": "date-time", "description": "Timestamp of last commit (UTC)."},
    "contributor_count": {"type": "integer", "minimum": 1, "description": "Unique Git authors."},
    "is_shallow": {"type": "boolean", "description": "True if shallow clone detected."},
    "is_fork": {"type": "boolean", "description": "True if fork detected via remote heuristic."},
    "language_distribution": {"type": "object", "description": "Optional map of language -> file count."}
  },
  "additionalProperties": false
}
```

**Python Dataclass (Reference):** Not explicitly defined in BSD; implementation language agnostic.

### MIIE Implementation

**JSON Schema:** `src/miie/schemas/repository_context.schema.json`

**Python Dataclass:** `src/miie/schemas/models.py` (RepositoryContext class)

**Key Fields:**
- `repo_id`: string (no format constraint)
- `local_path`: string (no uri-reference format)
- `is_remote`: boolean
- `remote_url`: `string | null` (explicitly nullable)
- `total_commits`: integer (minimum 10)
- `first_commit_date`: datetime.datetime (timezone-aware UTC)
- `last_commit_date`: datetime.datetime (timezone-aware UTC)
- `contributor_count`: integer (minimum 1)
- `is_shallow`: boolean
- `is_fork`: boolean
- `language_distribution`: `Optional[Dict[str, int]]` (language -> byte count)

**Validation:**
- `total_commits >= 10`
- `contributor_count >= 1`
- Datetimes must be timezone-aware UTC
- `first_commit_date <= last_commit_date`

**Serialization:** Uses `MIIEJSONEncoder` (ISO 8601 UTC with Z suffix, sorted keys, 6+ decimal places for floats).

### Comparison

| Aspect | BSD Specification | MIIE Implementation | Status |
|--------|-------------------|---------------------|--------|
| Field Names | Matches exactly | Matches exactly | ✅ |
| Field Types | `repo_id`: string (SHA-256)<br>`local_path`: string (uri-reference)<br>`remote_url`: string (uri)<br>`language_distribution`: object (language -> file count) | `repo_id`: string (no format)<br>`local_path`: string (no format)<br>`remote_url`: string \| null<br>`language_distribution`: object (language -> byte count) | ⚠️ Minor differences: missing format constraints, nullable remote_url, semantic difference in language_distribution (byte count vs file count) |
| Required Fields | 9 fields as listed | Same 9 fields | ✅ |
| Additional Properties | `additionalProperties: false` (implied by strict mode) | `additionalProperties: false` | ✅ |
| Validation | Implicit via schema (minimums, formats) | Explicit `__post_init__` validation plus JSON schema validation | ✅ (more exhaustive) |
| Serialization | JSON-primary, UTF-8, sorted keys, 6+ decimal places, ISO 8600 UTC with Z | Implemented via `MIIEJSONEncoder` and `json_dumps` | ✅ |

**Verdict:** Mostly compliant. Minor deviations in field semantics and format constraints that do not affect core interoperability but should be aligned for strict compliance.

---

## 2. MetricDataFrame

### BSD-Engineering v1.0 Specification (Section 6)

**Canonical Structure:** pandas DataFrame with columns per metric per window.

**JSON Serialization (Column-Oriented) Example (Section 6.3):**
```json
{
  "repo_id": "string",
  "run_id": "string",
  "timestamp": "2026-06-07T10:31:00Z",
  "metrics": {
    "M-01": {
      "w01": [82.5, 85.0, 88.2, ...],
      "w02": [90.1, 91.3, ...]
    },
    "M-02": { ... },
    // ... M-03 through M-07
  }
}
```

**Field Definitions:**
- Top-level: `repo_id` (string), `run_id` (string), `timestamp` (string, date-time)
- `metrics`: object mapping metric ID (M-01..M-07) to object mapping window ID (w01, w02, ...) to array of numbers (float/int). Missing data strategy allows nulls or omission per Section 6.4.

**Validation:** 
- Only frozen metrics (M-01..M-07) allowed.
- Timestamps must be ISO 8601 UTC with Z.
- Arrays represent time-series values per window.

### MIIE Implementation

**JSON Schema:** `src/miie/schemas/metric_dataframe.schema.json`

**Python Dataclass:** `src/miie/schemas/models.py` (MetricDataFrame class)

**Key Fields:**
- `repo_id`: string
- `run_id`: string
- `timestamp`: string (ISO 8601 UTC with Z validated via regex)
- `metrics`: `Dict[str, Dict[str, List[Optional[float]]]]`

**Validation (`__post_init__`):**
- Only metrics M-01 through M-07 allowed.
- Timestamp must match pattern `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$`.

**Serialization:** Uses deterministic JSON with sorted keys.

### Comparison

| Aspect | BSD Specification | MIIE Implementation | Status |
|--------|-------------------|---------------------|--------|
| Field Names | `repo_id`, `run_id`, `timestamp`, `metrics` | Matches exactly | ✅ |
| Field Types | `repo_id`: string<br>`run_id`: string<br>`timestamp`: string (date-time)<br>`metrics`: object of object of array of numbers | `repo_id`: string<br>`run_id`: string<br>`timestamp`: string (validated ISO 8601 UTC)<br>`metrics`: Dict mapping metric ID to Dict mapping window ID to List of Optional[float] | ✅ (allows nulls in arrays and null arrays) |
| Required Fields | `repo_id`, `run_id`, `timestamp`, `metrics` | Same | ✅ |
| Additional Properties | Implicitly forbidden (strict mode) | `additionalProperties: false` | ✅ |
| Validation | Implied by schema and BSD sections | Explicit validation of metric IDs and timestamp format | ✅ |
| Serialization | JSON-primary, sorted keys, 6+ decimal places | Implemented | ✅ |

**Verdict:** Fully compliant. The MIIE implementation accurately captures the BSD specification, including support for missing data via nulls.

---

## 3. DetectorResult (DetectorResults in BSD)

### BSD-Engineering v1.0 Specification (Section 8)

**JSON Schema (Section 8.1):**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DetectorResults",
  "type": "object",
  "required": ["detector_outputs"],
  "properties": {
    "detector_outputs": {
      "type": "object",
      "properties": {
        "D-01": {"type": "object"},
        "D-02": {"type": "object"},
        "D-03": {"type": "object"}
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

**Field Definitions:**
- `detector_outputs`: object with optional keys D-01, D-02, D-03 (each mapping to an object containing detector-specific results).
- No additional properties allowed.

**Storage Patterns (Sections 8.2-8.4):**
- D-01: `detector_outputs["D-01"][metric_id][window_pair_key]` where `window_pair_key` = `{w_a}-{w_b}`
- D-02: `detector_outputs["D-02"][metric_pair_key][window_pair_key]` where `metric_pair_key` = `{M_i}-{M_j}` (i < j)
- D-03: `detector_outputs["D-03"][metric_id][threshold_key][window_id]` where `threshold_key` is string representation of threshold.

### MIIE Implementation

**JSON Schema:** `src/miie/schemas/detector_result.schema.json`

**Python Dataclass:** `src/miie/schemas/models.py` (DetectorResult class)

**Key Fields:**
- `detector_outputs`: `Dict[str, Dict]` (validated to only contain D-01, D-02, D-03)

**Validation (`__post_init__`):**
- Only detector IDs D-01, D-02, D-03 allowed.

**Serialization:** Uses deterministic JSON.

### Comparison

| Aspect | BSD Specification | MIIE Implementation | Status |
|--------|-------------------|---------------------|--------|
| Field Names | `detector_outputs` | Matches exactly | ✅ |
| Field Types | `detector_outputs`: object with properties D-01, D-02, D-03 (each object) | `detector_outputs`: Dict[str, Dict] (validated) | ✅ |
| Required Fields | `detector_outputs` | Same | ✅ |
| Additional Properties | `additionalProperties: false` (both levels) | `additionalProperties: false` (both levels) | ✅ |
| Validation | Implicit via schema | Explicit validation of detector IDs | ✅ |
| Serialization | JSON-primary, sorted keys | Implemented | ✅ |

**Verdict:** Fully compliant.

---

## 4. EvidencePackage

### BSD-Engineering v1.0 Specification (Section 10)

**JSON Schema (Section 10.1):**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EvidencePackage",
  "type": "object",
  "required": ["provenance", "windows", "metrics", "detector_outputs", "scores"],
  "properties": {
    "provenance": {
      "type": "object",
      "required": ["miie_version", "config_hash", "timestamp"],
      "properties": {
        "miie_version": {"type": "string"},
        "config_hash": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "seed": {"type": "integer"},
        "platform": {"type": "string"},
        "python_version": {"type": "string"},
        "dependency_hash": {"type": "string"}
      },
      "additionalProperties": false
    },
    "windows": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "start", "end", "commits"],
        "properties": {
          "id": {"type": "string"},
          "start": {"type": "string", "format": "date-time"},
          "end": {"type": "string", "format": "date-time"},
          "commits": {"type": "integer"}
        },
        "additionalProperties": false
      }
    },
    "metrics": {
      "type": "object",
      "description": "Map of metric_id to window_id to array of values"
    },
    "detector_outputs": {
      "type": "object",
      "properties": {
        "D-01": {"type": "object"},
        "D-02": {"type": "object"},
        "D-03": {"type": "object"}
      },
      "additionalProperties": false
    },
    "scores": {
      "type": "object",
      "required": ["integrity", "confidence"],
      "properties": {
        "integrity": {
          "type": "object",
          "required": ["overall", "per_metric"],
          "properties": {
            "overall": {"type": "number", "minimum": 0, "maximum": 1},
            "per_metric": {"type": "object"}
          },
          "additionalProperties": false
        },
        "confidence": {
          "type": "object",
          "required": ["overall", "factors"],
          "properties": {
            "overall": {"type": "number", "minimum": 0, "maximum": 1},
            "factors": {"type": "object"}
          },
          "additionalProperties": false
        }
      },
      "additionalProperties": false
    },
    "warnings": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "stage": {"type": "string"},
          "message": {"type": "string"},
          "metric_id": {"type": "string"},
          "detector_id": {"type": "string"}
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

**Validation Rules:** Defined in Section 25 (Validation Framework) – strict JSON Schema validation, type coercion prohibited, format validation, etc.

### MIIE Implementation

**JSON Schema:** `src/miie/schemas/evidence_package.schema.json`

**Python Dataclass:** `src/miie/schemas/models.py` (EvidencePackage class) – note: this implementation includes additional fields not in the BSD schema (evidence_id, score_package_id, etc.) and appears to be a hybrid with ACS v1.0. For a pure BSD comparison, we focus on the JSON schema.

**Key Fields (from JSON schema):**
- `provenance`: object with fields miie_version (string), config_hash (string), timestamp (string, date-time), seed (integer), platform (string), python_version (string), dependency_hash (string)
- `windows`: array of objects with id (string), start (string, date-time), end (string, date-time), commits (integer)
- `metrics`: object mapping metric ID to window ID to array of numbers (or null)
- `detector_outputs`: object with keys D-01, D-02, D-03 (each object)
- `scores`: object with integrity (overall number 0-1, per_metric object of numbers 0-1) and confidence (overall number 0-1, factors object of numbers)
- `warnings`: array of objects with stage (string), message (string), metric_id (string), detector_id (string)

**Validation:** JSON schema validation plus potential runtime validation in dataclass `__post_init__` (though the dataclass in models.py diverges).

**Serialization:** Uses `json_dumps` with sorted keys, UTC datetime formatting.

### Comparison

| Aspect | BSD Specification | MIIE Implementation (JSON Schema) | Status |
|--------|-------------------|-----------------------------------|--------|
| Field Names | `provenance`, `windows`, `metrics`, `detector_outputs`, `scores`, `warnings` | Matches exactly | ✅ |
| Field Types | `provenance`: object (with subfields)<br>`windows`: array of window objects<br>`metrics`: object of object of array of numbers<br>`detector_outputs`: object with D-01/D-02/D-03<br>`scores`: object with integrity/confidence subobjects<br>`warnings`: array of warning objects | Matches exactly (note: BSD metrics does not explicitly allow nulls, but missing data strategy may permit) | ✅ |
| Required Fields | All six top-level fields | Same | ✅ |
| Additional Properties | `additionalProperties: false` at all levels | Same | ✅ |
| Validation | Strict JSON Schema validation, format checks, type safety | JSON schema validation enforced; dataclass validation present but diverges (see note) | ✅ (schema level) |
| Serialization | JSON-primary, UTF-8, sorted keys, 6+ decimal places, ISO 8601 UTC with Z | Implemented via `MIIEJSONEncoder` | ✅ |

**Note on Dataclass Divergence:** The `EvidencePackage` dataclass in `src/miie/schemas/models.py` includes additional fields (`evidence_id`, `score_package_id`, `detector_results_ids`, `metrics_used`, `windows_analyzed`, `integrity_verification`, `confidence_indicators`, `reproducibility_info`, `das_notation`) and omits some BSD fields (e.g., `provenance` is a dict but not structured per BSD). This dataclass appears to be an ACS v1.0 or extended implementation. For strict BSD-Engineering v1.0 compliance, the JSON schema is the authoritative source, and the dataclass should be realigned.

**Verdict:** The JSON schema is fully compliant with BSD-Engineering v1.0. The Python dataclass diverges and should be updated to match the BSD schema if strict compliance is required.

## Overall Conclusion

The MIIE repository implementation demonstrates strong alignment with the BSD-Engineering v1.0 specification for the four core objects:

- **RepositoryContext:** Mostly compliant; minor deviations in field semantics (remote_url nullable, language_distribution byte count vs file count, missing format constraints) that should be addressed for strict compliance.
- **MetricDataFrame:** Fully compliant; accurately captures the column-oriented JSON structure and validation rules.
- **DetectorResult:** Fully compliant; matches the BSD DetectorResults schema exactly.
- **EvidencePackage:** JSON schema is fully compliant; however, the associated Python dataclass diverges significantly and includes ACS v1.0 fields. To achieve full compliance, the dataclass should be refactored to match the BSD schema.

**Recommendations:**
1. Align RepositoryContext field definitions with BSD semantics (e.g., add format constraints, reconsider remote_url nullability, clarify language_distribution unit).
2. Ensure EvidencePackage Python dataclass mirrors the BSD JSON schema (remove ACS-specific fields, adopt BSD field structure).
3. Continue using the existing JSON serialization utilities (`json_dumps`, `MIIEJSONEncoder`) as they correctly implement BSD serialization rules.
4. Maintain strict JSON Schema validation (`additionalProperties: false`) across all schemas.

All compared objects satisfy the core requirements for deterministic, reproducible data interchange as mandated by BSD-Engineering v1.0.

---
*Report generated: 2026-06-20*