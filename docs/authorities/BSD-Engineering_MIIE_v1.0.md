**Backend** **Schema** **Document** **(BSD-Engineering** **v1.0)**
**System:** Measurement Integrity Intelligence Engine (MIIE)

**Version:** 1.0.0

**Status:** Schema Authority — Ready for API Contract Specification
**Date:** 2026-06-07

**Inputs:** IPD v1.1 FINAL \| PRD v1.0 \| TFS v1.0 \| BSD v1.0
(Benchmark) \| TRD v1.0 \| AFD v1.0 **Objective:** Define every data
structure, schema, contract, manifest, storage layout, and serialization
format required for Version 1 implementation, fully traceable to frozen
source documents.

**SECTION** **1** **—** **EXECUTIVE** **SUMMARY**

**1.1** **Purpose**

The Backend Schema Document (BSD-Engineering v1.0) is the **data**
**authority** for MIIE v1.0. It governs:

> The exact structure of every domain object passed between modules.
>
> The serialization formats for all persistent artifacts.
>
> The filesystem layout for cache, output, benchmark, job, and registry
> data.
>
> The validation rules that ensure data integrity across the pipeline
> and benchmark subsystems.
>
> The versioning contracts that guarantee reproducibility and backward
> compatibility.

**1.2** **Scope**

This document defines schemas for:

> All 18 TRD modules (M-01 through M-17, plus Evidence Aggregator).
>
> All 5 frozen user workflows (WF-01 through WF-05).
>
> All 3 benchmark suites (B-01, B-02, B-03).
>
> All 7 frozen metrics (M-01 through M-07).
>
> All 3 frozen detectors (D-01, D-02, D-03).
>
> All CLI and API input/output contracts.
>
> All filesystem directories and file lifecycle rules.

**1.3** **Non-Scope**

The following are explicitly excluded:

> Database schemas (V1 is filesystem-only per TRD §1.8, §16).
>
> GUI/web interface data models (V1 is CLI/API only per TFS §1.5).
>
> Real-time streaming schemas (V1 is batch-only per TFS §1.5).
>
> SaaS/multi-tenancy data models (V1 is self-hosted per TFS §1.5).
>
> Authentication/authorization schemas (minimal API key only per TFS
> §1.5, §14.2).
>
> Future metric schemas (M-08+ deferred per TFS §3).
>
> Future detector schemas (D-04+ deferred per TFS §4).

**1.4** **Schema** **Philosophy**

> 1\. **Filesystem-first:** All persistent storage is file-based. No
> database required.
>
> 2\. **JSON-primary:** JSON is the canonical serialization format for
> structured data. JSON Schema draft-07 is the validation standard.
>
> 3\. **Deterministic** **ordering:** All collections serialized to JSON
> must use sorted keys and ordered arrays to guarantee bitwise-identical
> reproducibility.
>
> 4\. **Self-describing:** Every artifact includes a manifest or
> provenance block describing its origin, version, and dependencies.
>
> 5\. **Immutable** **benchmarks:** Benchmark datasets and ground truth
> are immutable once published. Corrections result in version bumps.

**1.5** **Versioning** **Philosophy**

> **Semantic** **versioning** **(MAJOR.MINOR.PATCH)** for all schemas,
> datasets, and benchmarks.
>
> **Major** **bump:** Breaking field changes, schema restructuring,
> removal of fields.
>
> **Minor** **bump:** Additive non-breaking changes, new optional
> fields, metadata additions.
>
> **Patch** **bump:** Documentation fixes, typo corrections, no
> structural changes.
>
> **Frozen** **schemas:** M-01–M-07, D-01–D-03, IS/CS formulas, and
> evaluation metrics are frozen for V1. No changes permitted without a
> version bump.

**1.6** **Reproducibility** **Philosophy**

> Every run produces a manifest.json with full provenance (version,
> config hash, seed, timestamp, platform, dependency hash).
>
> Every benchmark dataset includes a metadata.json with generation
> parameters and seed.
>
> Every ground truth file includes version, annotator provenance, and
> checksum.
>
> SHA-256 checksums are computed for all critical artifacts and stored
> in manifests.
>
> Config hash is SHA-256 of the final merged configuration (defaults +
> file + CLI overrides).

**1.7** **Contract** **Stability** **Rules**

> 1\. **No** **schema** **changes** **without** **version** **bump:**
> Once a schema version is published, it is
>
> immutable.
>
> 2\. **Backward** **compatibility** **within** **major** **version:**
> Consumers of schema v1.0.0 must be able to read v1.1.0 artifacts
> (additive only).
>
> 3\. **Strict** **validation:** Unknown fields in JSON are rejected by
> default (strict schema mode).
>
> 4\. **Type** **coercion** **prohibited:** Values must match declared
> types exactly. No silent coercion except metric value nullification
> (non-numeric → null with warning).
>
> 5\. **Frozen** **formulas:** Integrity Score and Confidence Score
> formulas are frozen per TFS §6–7. No schema field may permit formula
> variation without version bump.

**SECTION** **2** **—** **DATA** **ARCHITECTURE** **OVERVIEW**

**2.1** **Layered** **Data** **Architecture**

┌─────────────────────────────────────────────────────────────────────────────┐
│ INPUT LAYER │ │ Git Repositories │ Coverage Artifacts │ PR/Issue
Exports │ Config │ │ (User-provided) │ (XML/LCOV/JSON) │ (JSON/CSV) │
(YAML/JSON)│
└─────────────────────────────────────────────────────────────────────────────┘

> │ │ │ │ ▼ ▼ ▼ ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│ PROCESSING LAYER │ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
┌─────────────────────┐ │ │ │ Repository │ │ Metric │ │ Window │ │
Detector │ │ │ │ Context │ │ DataFrame │ │ Definitions │ │ Results │ │ │
│ (M-01) │ │ (M-02) │ │ (M-03) │ │ (M-05) │ │ │ └─────────────┘
└─────────────┘ └─────────────┘ └─────────────────────┘ │ │ │ │ │ │ │ │
▼ ▼ ▼ ▼ │ │
┌─────────────────────────────────────────────────────────────────────┐
│ │ │ SCORING LAYER │ │ │ │ ScorePackage (M-08) │ EvidencePackage (EVA)
│ ExplanationReport │ │ │ │ (Integrity + Confidence Scores) │ (M-09) │ │

│
└─────────────────────────────────────────────────────────────────────┘
│ │ │ │ │ ▼ │ │
┌─────────────────────────────────────────────────────────────────────┐
│ │ │ OUTPUT LAYER │ │ │ │ results.json │ report.md │ metrics.csv │
manifest.json │ evidence.json│

│
└─────────────────────────────────────────────────────────────────────┘
│
└─────────────────────────────────────────────────────────────────────────────┘

> │ ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│ BENCHMARK LAYER │ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
┌─────────────────────┐ │ │ │ Synthetic │ │ Ground │ │ Benchmark │ │
Evaluation │ │ │ │ Dataset │ │ Truth │ │ Run │ │ Result │ │ │ │ (M-03) │
│ (M-04) │ │ (M-06) │ │ (M-07) │ │ │ └─────────────┘ └─────────────┘
└─────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

> **2.2** **Data** **Creation** **and** **Flow**

||
||
||
||
||
||
||
||
||
||

> **SECTION** **3** **—** **CANONICAL** **OBJECT** **REGISTRY**
>
> **3.1** **Master** **Object** **Registry**

||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||

> **SECTION** **4** **—** **GLOBAL** **SCHEMA** **STANDARDS**
>
> **4.1** **Naming** **Conventions**
>
> **Field** **names:** snake_case for all JSON and Python fields.
>
> **Object** **IDs:** PascalCase for class names (e.g.,
> RepositoryContext).
>
> **Metric** **IDs:** M-NN format (e.g., M-01, M-07). Frozen.
>
> **Detector** **IDs:** D-NN format (e.g., D-01, D-03). Frozen.
>
> **Window** **IDs:** wNN format (e.g., w01, w12). Pattern:
> ^w\[0-9\]{2}\$.
>
> **Repository** **IDs:** repo_NNN format for synthetic datasets (e.g.,
> repo_001). Pattern: ^repo\_\[0-9\]{3}\$.
>
> **Job** **IDs:** UUID4 string, hyphenated lowercase (e.g.,
> a1b2c3d4-e5f6-7890-abcd-ef1234567890).
>
> **File** **names:** snake_case with appropriate extension (.json, .md,
> .csv, .yaml).
>
> **4.2** **Type** **Conventions**

||
||
||
||
||
||
||
||
||
||

> **4.3** **Timestamp** **Standard**
>
> **Format:** ISO 8601 UTC with Z suffix: YYYY-MM-DDTHH:MM:SSZ.
>
> **Precision:** Second-level precision sufficient for V1.
>
> **Timezone:** All timestamps stored and compared in UTC. Git author
> dates with timezone offsets converted to UTC internally.
>
> **Example:** "2026-06-07T10:31:00Z".
>
> **4.4** **UUID** **Standard**
>
> **Format:** UUID4 (random), lowercase, hyphenated.
>
> **Example:** "a1b2c3d4-e5f6-7890-abcd-ef1234567890".
>
> **Generation:** Python uuid.uuid4().
>
> **4.5** **Version** **Standard**
>
> **Schema:** Semantic versioning MAJOR.MINOR.PATCH.
>
> **Example:** "1.0.0".
>
> **MIIE** **version:** Matches release tag (e.g., v1.0.0).
>
> **Benchmark** **version:** Independent of MIIE version (e.g.,
> metric-drift-v1.0.0).
>
> **Ground** **truth** **version:** Independent of suite version (e.g.,
> ground_truth-v1.0.0.json).
>
> **4.6** **Null** **Handling**
>
> **Explicit** **null:** JSON null used for missing metric values,
> optional fields absent.
>
> **No** **omission:** Required fields must be present (even if null
> where nullable). Optional fields may be omitted entirely.
>
> **Metric** **null:** Non-numeric metric values coerced to null with
> warning logged.
>
> **4.7** **Missing** **Data** **Handling**

||
||
||
||
||
||
||

> **4.8** **Boolean** **Handling**
>
> JSON true/false only. No string booleans (e.g., no "true" or "false").
>
> Python: strict bool type. No truthy/falsy coercion in schema
> validation.
>
> **4.9** **Numeric** **Precision** **Rules**
>
> **Floats:** IEEE 754 double precision. Serialized with 6 decimal
> places minimum in JSON.
>
> **Reproducibility:** Use math.fsum() for floating-point summation.
> Sort collections before iteration.
>
> **Score** **precision:** Integrity Score and Confidence Score computed
> and stored with full double precision. Displayed to 4 decimal places
> in reports.
>
> **Bitwise-identical** **requirement:** Three teams must produce
> identical scores to \|Δ\| \< 1e-9 (TFS §6.9, §7.8).
>
> **4.10** **Serialization** **Rules**
>
> **JSON:** UTF-8 encoding, no BOM. Deterministic key ordering (sorted
> alphabetically). No
>
> trailing commas. 2-space indentation for pretty-printing; compact for
> internal storage.
>
> **CSV:** UTF-8 encoding, comma-delimited, quoted strings per RFC 4180.
> Header row mandatory. Consistent column ordering.
>
> **YAML:** YAML 1.2 strict subset. No anchors, no tags, no custom
> types. Used for config files only.
>
> **Markdown:** GitHub-Flavored Markdown. Used for human-readable
> reports only.
>
> **SECTION** **5** **—** **REPOSITORYCONTEXT** **SCHEMA**
>
> **5.1** **Schema** **Definition**
>
> **Source:** TRD §7.8, TFS §9.1–9.3, BSD §14.1
>
> {
>
> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "RepositoryContext",
>
> "type": "object",
>
> "required": \["repo_id", "local_path", "is_remote", "total_commits",
> "first_commit_date", "last_commit_date", "contributor_count",
> "is_shallow", "is_fork"\],
>
> "properties": {
>
> "repo_id": {"type": "string", "description": "SHA-256 of remote URL or
> absolute path. Unique within analysis."},
>
> "local_path": {"type": "string", "format": "uri-reference",
> "description": "Absolute path to repository root."},
>
> "is_remote": {"type": "boolean", "description": "True if cloned from
> remote URL."},
>
> "remote_url": {"type": "string", "format": "uri", "description":
> "Original remote URL if applicable."},
>
> "total_commits": {"type": "integer", "minimum": 10, "description":
> "Total non-merge commits in history."},
>
> "first_commit_date": {"type": "string", "format": "date-time",
> "description": "Timestamp of first commit (UTC)."},
>
> "last_commit_date": {"type": "string", "format": "date-time",
> "description": "Timestamp of last commit (UTC)."},
>
> "contributor_count": {"type": "integer", "minimum": 1, "description":
> "Unique Git authors."},
>
> "is_shallow": {"type": "boolean", "description": "True if shallow
> clone detected."},
>
> "is_fork": {"type": "boolean", "description": "True if fork detected
> via remote heuristic."},
>
> "language_distribution": {"type": "object", "description": "Optional
> map of language -\> file count."}
>
> } }
>
> **5.2** **Field** **Definitions**

||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||
||

||
||
||
||

> **5.3** **Python** **Dataclass**
>
> @dataclass
>
> class RepositoryContext: repo_id: str local_path: Path is_remote: bool
>
> remote_url: Optional\[str\] = None total_commits: int
> first_commit_date: datetime last_commit_date: datetime
> contributor_count: int is_shallow: bool
>
> is_fork: bool
>
> language_distribution: Optional\[Dict\[str, int\]\] = None
>
> **SECTION** **6** **—** **METRICDATAFRAME** **SCHEMA**
>
> **6.1** **Canonical** **Structure** **Source:** TRD §8, TFS §2, BSD
> §14.2

The MetricDataFrame is a pandas DataFrame with the following canonical
columns. When serialized to JSON, it is represented as an array of row
objects or a column-oriented object.

||
||
||
||
||
||
||
||

> **6.2** **Per-Metric** **Field** **Definitions**
>
> ***M-01:*** ***Code*** ***Coverage***

||
||
||
||
||

> ***M-02:*** ***Commit*** ***Frequency***

||
||
||
||
||

> ***M-03:*** ***Review*** ***Participation***

||
||
||
||
||

> ***M-04:*** ***Review*** ***Latency***

||
||
||
||
||

> ***M-05:*** ***Issue*** ***Resolution*** ***Time***

||
||
||
||

||
||
||
||
||

> ***M-06:*** ***Code*** ***Churn***

||
||
||
||
||
||

> ***M-07:*** ***Cyclomatic*** ***Complexity***

||
||
||
||
||
||

> **6.3** **JSON** **Serialization** **(Column-Oriented)**
>
> {
>
> "repo_id": "string", "run_id": "string",
>
> "timestamp": "2026-06-07T10:31:00Z", "metrics": {
>
> "M-01": {
>
> "w01": \[82.5, 85.0, 88.2, ...\], "w02": \[90.1, 91.3, ...\]
>
> },
>
> "M-02": { ... }, "M-03": { ... }, "M-04": { ... }, "M-05": { ... },
> "M-06": { ... }, "M-07": { ... }
>
> } }
>
> **6.4** **Missing** **Data** **Strategy** **Summary**

||
||
||
||
||
||
||
||
||
||

> **SECTION** **7** **—** **WINDOWDEFINITION** **SCHEMA**
>
> **7.1** **Schema** **Definition**
>
> **Source:** TRD §7.4, TFS §12, BSD §14.1
>
> {
>
> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "WindowDefinition",
>
> "type": "object",
>
> "required": \["window_id", "start_date", "end_date", "commits"\],
> "properties": {
>
> "window_id": {"type": "string", "pattern": "^w\[0-9\]{2}\$"},
> "start_date": {"type": "string", "format": "date"}, "end_date":
> {"type": "string", "format": "date"}, "commits": {"type": "integer",
> "minimum": 1},
>
> "strategy": {"type": "string", "enum": \["time", "commit", "release",
> "custom"\]},
>
> "size_config": {"type": "object"} }
>
> }
>
> **7.2** **Field** **Definitions**

||
||
||
||

||
||
||
||
||
||
||
||

> **7.3** **Window** **Ordering** **Rules**
>
> 1\. Windows must be non-overlapping: end_date(w_i) \<
> start_date(w\_{i+1}).
>
> 2\. Windows must be chronologically ordered: w01, w02, ..., wNN.
>
> 3\. Minimum 2 windows required for drift detection (D-01, D-02).
>
> 4\. Minimum 1 window required for threshold compression (D-03), but 2+
> recommended.
>
> **7.4** **Python** **Dataclass**
>
> @dataclass class Window:
>
> window_id: str start_date: date end_date: date commits: int
>
> strategy: Optional\[str\] = None
>
> size_config: Optional\[Dict\[str, Any\]\] = None
>
> **SECTION** **8** **—** **DETECTORRESULT** **SCHEMA**
>
> **8.1** **Top-Level** **Structure** **Source:** TRD §10, TFS §4–5, BSD
> §9
>
> {
>
> "\$schema": "http://json-schema.org/draft-07/schema#",
>
> "title": "DetectorResults", "type": "object",
>
> "required": \["detector_outputs"\], "properties": {
>
> "detector_outputs": { "type": "object", "properties": {
>
> "D-01": {"type": "object"}, "D-02": {"type": "object"}, "D-03":
> {"type": "object"}
>
> } }
>
> } }
>
> **8.2** **D-01:** **Distributional** **Drift** **Detector** **Result**

||
||
||
||
||
||
||
||
||
||
||
||
||

||
||
||
||

> **Storage:**
> detector_outputs\["D-01"\]\[metric_id\]\[window_pair_key\] where
> window_pair_key is "{w_a}-{w_b}".
>
> **8.3** **D-02:** **Correlation** **Breakdown** **Detector**
> **Result**

||
||
||
||
||
||
||
||
||
||
||

> **Storage:**
> detector_outputs\["D-02"\]\[metric_pair_key\]\[window_pair_key\] where
> metric_pair_key is "{M_i}-{M_j}" (i \< j).
>
> **8.4** **D-03:** **Threshold** **Compression** **Detector**
> **Result**

||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **Storage:** detector_outputs\["D-03"\]\[metric_id\]\[threshold_key\]
> \[window_id\] where threshold_key is string representation of
> threshold (e.g., "1.0").
>
> **8.5** **Python** **Dataclass**
>
> @dataclass
>
> class DetectorResults:
>
> d_01: Dict\[str, Dict\[str, DriftResult\]\] \# metric -\> window_pair
> -\> result
>
> d_02: Dict\[str, Dict\[str, BreakdownResult\]\] \# metric_pair -\>
> window_pair -\> result
>
> d_03: Dict\[str, Dict\[str, Dict\[str, CompressionResult\]\]\] \#
> metric -\> threshold -\> window -\> result
>
> **SECTION** **9** **—** **SCOREPACKAGE** **SCHEMA**
>
> **9.1** **Schema** **Definition** **Source:** TRD §15.6, TFS §6–7
>
> {
>
> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "ScorePackage",
>
> "type": "object",
>
> "required": \["integrity", "confidence", "timestamp", "config_hash",
> "formula_version"\],
>
> "properties": { "integrity": {
>
> "type": "object",
>
> "required": \["overall", "per_metric"\], "properties": {
>
> "overall": {"type": "number", "minimum": 0, "maximum": 1},
> "per_metric": {"type": "object", "additionalProperties": {"type":
>
> "number", "minimum": 0, "maximum": 1}} }
>
> }, "confidence": {
>
> "type": "object",
>
> "required": \["overall", "factors"\], "properties": {
>
> "overall": {"type": "number", "minimum": 0, "maximum": 1}, "factors":
> {
>
> "type": "object", "properties": {
>
> "sample_size": {"type": "number"}, "variance": {"type": "number"},
> "missing_data": {"type": "number"}, "window_balance": {"type":
> "number"}, "detector_success": {"type": "number"}
>
> } }
>
> } },
>
> "timestamp": {"type": "string", "format": "date-time"}, "config_hash":
> {"type": "string"},
>
> "formula_version": {"type": "string"} }
>
> }
>
> **9.2** **Field** **Definitions**
>
> ***Integrity*** ***Score***

||
||
||
||

||
||
||
||
||
||

> ***Confidence*** ***Score***

||
||
||
||
||
||
||
||
||
||

> ***Provenance***

||
||
||
||

||
||
||
||
||
||

> **9.3** **Validation** **Rules**
>
> 1\. IS_overall must equal mean(IS_metric for all available metrics)
> within floating-point tolerance.
>
> 2\. CS must equal f1 × f2 × f3 × f4 × f5 within floating-point
> tolerance.
>
> 3\. All factors must be in \[0.0, 1.0\].
>
> 4\. If all metrics unavailable: ScorePackage is invalid (ScoreError).
>
> **9.4** **Python** **Dataclass**
>
> @dataclass
>
> class IntegrityScore: overall: float
>
> per_metric: Dict\[str, float\] formula_version: str
>
> @dataclass
>
> class ConfidenceScore: overall: float
>
> factors: Dict\[str, float\] band: Optional\[str\] = None
>
> @dataclass
>
> class ScorePackage: integrity: IntegrityScore
>
> confidence: ConfidenceScore timestamp: datetime config_hash: str
> formula_version: str = "1.0.0"
>
> **SECTION** **10** **—** **EVIDENCEPACKAGE** **SCHEMA**
>
> **10.1** **Schema** **Definition**
>
> **Source:** TFS Appendix A (Evidence Package Schema), TRD §10.5, §20.1
>
> {
>
> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "EvidencePackage",
>
> "type": "object",
>
> "required": \["provenance", "windows", "metrics", "detector_outputs",

"scores"\], "properties": {

> "provenance": { "type": "object",
>
> "required": \["miie_version", "config_hash", "timestamp"\],
> "properties": {
>
> "miie_version": {"type": "string"}, "config_hash": {"type": "string"},
>
> "timestamp": {"type": "string", "format": "date-time"}, "seed":
> {"type": "integer"},
>
> "platform": {"type": "string"}, "python_version": {"type": "string"},
> "dependency_hash": {"type": "string"}
>
> } },
>
> "windows": { "type": "array", "items": {
>
> "type": "object",
>
> "required": \["id", "start", "end", "commits"\], "properties": {
>
> "id": {"type": "string"},
>
> "start": {"type": "string", "format": "date-time"}, "end": {"type":
> "string", "format": "date-time"}, "commits": {"type": "integer"}
>
> } }
>
> }, "metrics": {
>
> "type": "object",
>
> "description": "Map of metric_id to window_id to array of values" },
>
> "detector_outputs": { "type": "object", "properties": {
>
> "D-01": {"type": "object"}, "D-02": {"type": "object"}, "D-03":
> {"type": "object"}
>
> } },
>
> "scores": { "type": "object",
>
> "required": \["integrity", "confidence"\], "properties": {
>
> "integrity": { "type": "object",
>
> "required": \["overall", "per_metric"\], "properties": {
>
> "overall": {"type": "number", "minimum": 0, "maximum": 1},
> "per_metric": {"type": "object"}
>
> } },
>
> "confidence": { "type": "object",
>
> "required": \["overall", "factors"\], "properties": {
>
> "overall": {"type": "number", "minimum": 0, "maximum": 1}, "factors":
> {"type": "object"}
>
> } }
>
> } },
>
> "warnings": { "type": "array",
>
> "items": {
>
> "type": "object", "properties": {
>
> "stage": {"type": "string"}, "message": {"type": "string"},
> "metric_id": {"type": "string"}, "detector_id": {"type": "string"}
>
> } }
>
> } }
>
> }
>
> **10.2** **Field** **Definitions**

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **10.3** **Traceability** **Requirements**
>
> Every positive detector flag in detector_outputs must have
> corresponding statistical evidence in the evidence package.
>
> Every score value must be traceable to specific detector outputs and
> formulas.
>
> Every warning must identify the stage and affected metric/detector.
>
> **SECTION** **11** **—** **EXPLANATIONREPORT** **SCHEMA**
>
> **11.1** **Schema** **Definition** **Source:** TRD §20.3, TFS §12, IPD
> §19
>
> {
>
> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "ExplanationReport",
>
> "type": "object",
>
> "required": \["explanations", "summary", "recommendations"\],
> "properties": {
>
> "explanations": { "type": "array", "items": {
>
> "type": "object",
>
> "required": \["metric_id", "detector_id", "narrative", "severity",
> "evidence_refs"\],
>
> "properties": {
>
> "metric_id": {"type": "string"}, "detector_id": {"type": "string"},
> "narrative": {"type": "string"},
>
> "severity": {"type": "string", "enum": \["mild", "moderate",
> "severe"\]},
>
> "evidence_refs": {"type": "array", "items": {"type": "string"}},
> "confidence": {"type": "string", "enum": \["high", "medium", "low"\]},
> "rule_fired": {"type": "string"}
>
> } }
>
> },
>
> "summary": {"type": "string"},
>
> "recommendations": {"type": "array", "items": {"type": "string"}},
> "disclaimer": {"type": "string"}
>
> } }
>
> **11.2** **Field** **Definitions**

||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||

> **11.3** **Template** **Mapping** **(Deterministic)**

||
||
||
||

||
||
||
||
||
||

> **SECTION** **12** **—** **ANALYSISRESULT** **SCHEMA**
>
> **12.1** **Schema** **Definition**
>
> **Source:** TRD §20.1, AFD §5.2, TFS Appendix A
>
> {
>
> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "AnalysisResult",
>
> "type": "object",
>
> "required": \["miie_version", "generated_at", "config_hash",
> "repository", "windows", "metrics", "detector_results", "scores",
> "evidence", "explanations"\],
>
> "properties": {
>
> "miie_version": {"type": "string"},
>
> "generated_at": {"type": "string", "format": "date-time"},
> "config_hash": {"type": "string"},
>
> "repository": {"\$ref": "#/definitions/RepositoryContext"}, "windows":
> {"type": "array", "items": {"\$ref":
>
> "#/definitions/WindowDefinition"}}, "metrics": {"type": "object"},
> "detector_results": {"type": "object"}, "scores": {"type": "object"},
> "evidence": {"type": "object"}, "explanations": {"type": "array"},
> "run_metadata": {"type": "object"}
>
> } }
>
> **12.2** **Field** **Definitions**

||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||

> **12.3** **Run** **Metadata** **Sub-schema**

||
||
||
||
||
||
||
||
||

**SECTION** **13** **—** **BENCHMARK** **DATASET** **SCHEMA**

**13.1** **Dataset** **Manifest** **Schema** **Source:** BSD §14.6, TRD
§17.9

{

> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "DatasetManifest",
>
> "type": "object",

"required": \["suite_id", "version", "description", "num_datasets",
"metrics_included"\],

> "properties": {
>
> "suite_id": {"type": "string"}, "version": {"type": "string"},
> "description": {"type": "string"},
>
> "created_at": {"type": "string", "format": "date-time"}, "author":
> {"type": "string"},
>
> "license": {"type": "string"},
>
> "num_datasets": {"type": "integer", "minimum": 1},
>
> "detector_target": {"type": "string", "enum": \["D-01", "D-02",
> "D-03"\]}, "metrics_included": {"type": "array", "items": {"type":
> "string", "enum":

\["M-01", "M-02", "M-03", "M-04", "M-05", "M-06", "M-07"\]}},

"window_strategy": {"type": "string", "enum": \["time", "commit",
"release", "custom"\]},

> "window_size_days": {"type": "integer"}, "random_seed": {"type":
> "integer"},
>
> "pathology_ratio": {"type": "number", "minimum": 0, "maximum": 1},
> "annotation_kappa": {"type": "number", "minimum": 0, "maximum": 1}

} }

**13.2** **Synthetic** **Repository** **Metadata** **Schema**
**Source:** BSD §14.1, TRD §9.2

{

> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "SyntheticRepositoryMetadata",
>
> "type": "object",
>
> "required": \["repo_id", "category", "parameters", "windows"\],
> "properties": {
>
> "repo_id": {"type": "string", "pattern": "^repo\_\[0-9\]{3}\$"},
> "category": {"enum": \["small_active", "medium_active",
> "large_active",

"seasonal", "monotonic_growth", "declining", "stable"\]},

> "language": {"enum": \["python", "java", "cpp", "javascript",
> "typescript"\]}, "parameters": {
>
> "type": "object",

"required": \["duration_days", "total_commits", "contributors",
"bot_ratio"\],

> "properties": {
>
> "duration_days": {"type": "integer", "minimum": 90, "maximum": 730},
> "total_commits": {"type": "integer", "minimum": 60, "maximum": 2400},
> "contributors": {"type": "integer", "minimum": 1, "maximum": 50},
> "bot_ratio": {"type": "number", "minimum": 0.0, "maximum": 0.3},
> "window_count": {"type": "integer", "minimum": 6, "maximum": 12},
> "window_size_days": {"type": "integer", "minimum": 30, "maximum": 90}
>
> } },
>
> "windows": { "type": "array", "items": {
>
> "type": "object",
>
> "required": \["window_id", "start_date", "end_date", "commits"\],
> "properties": {
>
> "window_id": {"type": "string", "pattern": "^w\[0-9\]{2}\$"},
> "start_date": {"type": "string", "format": "date"}, "end_date":
> {"type": "string", "format": "date"}, "commits": {"type": "integer",
> "minimum": 10}
>
> } }
>
> },
>
> "generation_seed": {"type": "integer"},
>
> "generation_timestamp": {"type": "string", "format": "date-time"} }

}

**13.3** **Pathology** **Metadata** **Schema** **Source:** BSD §9.4, TRD
§9.3

{

> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "PathologyMetadata",
>
> "type": "object",
>
> "required": \["event_type", "metric_id", "target_window",
> "severity"\], "properties": {
>
> "event_type": {"enum": \["MDE-01", "MDE-02", "MDE-03"\]},

"metric_id": {"enum": \["M-01", "M-02", "M-03", "M-04", "M-05", "M-06",
"M-07"\]},

> "target_window": {"type": "string", "pattern": "^w\[0-9\]{2}\$"},
> "severity": {"enum": \["mild", "moderate", "severe"\]},
> "drift_direction": {"enum": \["mean_shift", "variance_collapse",

"shape_change"\]},

> "drift_magnitude": {"type": "number"},

"metric_pair": {"type": "array", "items": {"type": "string"},
"minItems": 2, "maxItems": 2},

"breakdown_type": {"enum": \["sudden_drop", "sign_reversal",
"gradual_erosion"\]},

> "correlation_change": {"type": "number"}, "threshold": {"type":
> "number"},
>
> "compression_ratio": {"type": "number", "minimum": 0, "maximum": 1} }

}

**SECTION** **14** **—** **GROUNDTRUTH** **SCHEMA**

**14.1** **Schema** **Definition** **Source:** BSD §14.4, TFS §10, TRD
§11

{

> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "GroundTruth",
>
> "type": "object",
>
> "required": \["suite_id", "version", "labels"\], "properties": {
>
> "suite_id": {"type": "string"}, "version": {"type": "string"},
>
> "created_at": {"type": "string", "format": "date-time"}, "labels": {
>
> "type": "array", "items": {
>
> "type": "object",
>
> "required": \["repo_id", "metric_id", "label", "event_type"\],
> "properties": {
>
> "repo_id": {"type": "string", "pattern": "^repo\_\[0-9\]{3}\$"},
> "metric_id": {"type": "string"},
>
> "window_id": {"type": "string"},
>
> "window_pair": {"type": "array", "items": {"type": "string"}},
> "metric_pair": {"type": "array", "items": {"type": "string"}},
> "threshold": {"type": "number"},
>
> "label": {"type": "boolean"},
>
> "event_type": {"enum": \["MDE-01", "MDE-02", "MDE-03", "MDE-04"\]},
> "severity": {"enum": \["mild", "moderate", "severe"\]}, "confidence":
> {"enum": \["high", "medium", "low"\]}, "evidence_refs": {"type":
> "array", "items": {"type": "string"}},
>
> "annotator_agreement": {"type": "number", "minimum": 0, "maximum": 1}
> }
>
> } }
>
> } }
>
> **14.2** **Field** **Definitions**

||
||
||
||
||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||

> **14.3** **Annotation** **Schema** **(Per-Label** **Detail)**
> **Source:** BSD §14.3, §11.2
>
> {
>
> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "Annotation",
>
> "type": "object",
>
> "required": \["annotation_id", "metric_id", "event_type", "label",
> "annotator_id", "timestamp"\],
>
> "properties": {
>
> "annotation_id": {"type": "string"}, "metric_id": {"type": "string"},
> "window_id": {"type": "string"},
>
> "window_pair": {"type": "array", "items": {"type": "string"}},
> "metric_pair": {"type": "array", "items": {"type": "string"}},
> "threshold": {"type": "number"},
>
> "event_type": {"enum": \["MDE-01", "MDE-02", "MDE-03", "MDE-04"\]},
> "label": {"type": "boolean"},
>
> "severity": {"enum": \["mild", "moderate", "severe"\]}, "evidence": {
>
> "type": "object", "properties": {
>
> "statistical": {"type": "object"},
>
> "visual": {"type": "array", "items": {"type": "string"}}, "rationale":
> {"type": "string"}
>
> } },
>
> "annotator_id": {"type": "string"},
>
> "timestamp": {"type": "string", "format": "date-time"} }
>
> }
>
> **SECTION** **15** **—** **BENCHMARKRUN** **SCHEMA**
>
> **15.1** **Schema** **Definition**
>
> **Source:** BSD §14.5, TRD §17.8, TFS §8.8
>
> {
>
> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "BenchmarkRun",
>
> "type": "object",
>
> "required": \["run_id", "suite_id", "detector_id", "detector_version",
> "seed", "started_at", "completed_at", "predictions", "timing",
> "environment"\],
>
> "properties": {
>
> "run_id": {"type": "string"}, "suite_id": {"type": "string"},
>
> "detector_id": {"type": "string", "enum": \["D-01", "D-02", "D-03"\]},
> "detector_version": {"type": "string"},
>
> "seed": {"type": "integer"},
>
> "started_at": {"type": "string", "format": "date-time"},
> "completed_at": {"type": "string", "format": "date-time"},
> "predictions": {
>
> "type": "object",
>
> "description": "Nested dict: dataset_id -\> metric_id -\> context -\>
> prediction"
>
> }, "timing": {
>
> "type": "object",
>
> "description": "Per-dataset execution times in seconds" },
>
> "environment": { "type": "object",
>
> "required": \["miie_version", "python_version", "platform"\],
> "properties": {
>
> "miie_version": {"type": "string"}, "python_version": {"type":
> "string"}, "platform": {"type": "string"}, "dependency_hash": {"type":
> "string"}
>
> } }
>
> } }
>
> **15.2** **Field** **Definitions**

||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||

> **SECTION** **16** **—** **EVALUATIONRESULT** **SCHEMA**
>
> **16.1** **Schema** **Definition**
>
> **Source:** BSD §14.5, TFS §8.7, TRD §14.2
>
> {
>
> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "EvaluationResult",
>
> "type": "object",
>
> "required": \["suite_id", "detector_id", "detector_version",
> "metrics",
>
> "confusion_matrix"\], "properties": {
>
> "suite_id": {"type": "string"}, "detector_id": {"type": "string"},
> "detector_version": {"type": "string"},
>
> "evaluation_timestamp": {"type": "string", "format": "date-time"},
> "random_seed": {"type": "integer"},
>
> "metrics": { "type": "object",
>
> "required": \["accuracy", "precision", "recall", "f1", "auc_roc",
> "auc_pr", "fpr", "fnr"\],
>
> "properties": {
>
> "accuracy": {"type": "number", "minimum": 0, "maximum": 1},
> "precision": {"type": "number", "minimum": 0, "maximum": 1}, "recall":
> {"type": "number", "minimum": 0, "maximum": 1}, "f1": {"type":
> "number", "minimum": 0, "maximum": 1}, "auc_roc": {"type": "number",
> "minimum": 0, "maximum": 1}, "auc_pr": {"type": "number", "minimum":
> 0, "maximum": 1}, "fpr": {"type": "number", "minimum": 0, "maximum":
> 1}, "fnr": {"type": "number", "minimum": 0, "maximum": 1}
>
> } },
>
> "confusion_matrix": { "type": "object",
>
> "required": \["tp", "fp", "tn", "fn"\], "properties": {
>
> "tp": {"type": "integer", "minimum": 0}, "fp": {"type": "integer",
> "minimum": 0}, "tn": {"type": "integer", "minimum": 0}, "fn": {"type":
> "integer", "minimum": 0}
>
> } },
>
> "per_dataset_results": { "type": "array", "items": {
>
> "type": "object", "properties": {
>
> "repo_id": {"type": "string"}, "predicted": {"type": "boolean"},
> "actual": {"type": "boolean"}, "correct": {"type": "boolean"}
>
> } }
>
> } }
>
> }
>
> **16.2** **Field** **Definitions**

||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **16.3** **Validation** **Rules**
>
> 1\. TP + FP + TN + FN must equal total evaluation instances.
>
> 2\. All evaluation metrics must be in \[0.0, 1.0\].
>
> 3\. AUC-ROC must be ≥ 0.5 for any non-random detector (enforced as
> sanity check, not hard fail).
>
> 4\. Division by zero in precision/recall/F1 must return 0.0 with
> warning (not NaN).
>
> **SECTION** **17** **—** **CONFIGURATION** **SCHEMA**
>
> **17.1** **CLI** **Configuration** **Schema**
>
> **Source:** TFS Appendix A (Configuration Schema), TRD §5.13
>
> {
>
> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "MIIEConfiguration",
>
> "type": "object", "required": \["repo"\], "properties": {
>
> "repo": {"type": "string"},
>
> "since": {"type": "string", "format": "date-time"}, "until": {"type":
> "string", "format": "date-time"},
>
> "metrics": {"type": "array", "items": {"enum": \["M-01", "M-02",
> "M-03", "M-04", "M-05", "M-06", "M-07", "all"\]}},
>
> "window_strategy": {"enum": \["time", "commit", "release",
> "custom"\]}, "window_size": {"type": "integer", "minimum": 1},
>
> "detectors": {"type": "array", "items": {"enum": \["D-01", "D-02",
> "D-03", "all"\]}},
>
> "output_formats": {"type": "array", "items": {"enum": \["json", "md",
> "csv"\]}},
>
> "exclude_bots": {"type": "boolean"},
>
> "thresholds": {"type": "object", "additionalProperties": {"type":
> "array", "items": {"type": "number"}}},
>
> "detector_weights": { "type": "object", "properties": {
>
> "D-01": {"type": "number"}, "D-02": {"type": "number"}, "D-03":
> {"type": "number"}
>
> } },
>
> "seed": {"type": "integer"}, "config_path": {"type": "string"},
> "output_dir": {"type": "string"}, "verbose": {"type": "boolean"},
> "keep_cache": {"type": "boolean"},
>
> "shallow_depth": {"type": "integer", "minimum": 1} }
>
> }
>
> **17.2** **Field** **Definitions**

||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **17.3** **Detector** **Configuration** **Sub-schema**
>
> {
>
> "detector_config": { "type": "object", "properties": {
>
> "D-01": {
>
> "type": "object", "properties": {
>
> "alpha": {"type": "number", "default": 0.05}, "psi_threshold":
> {"type": "number", "default": 0.25}
>
> } },
>
> "D-02": {
>
> "type": "object", "properties": {
>
> "correlation_threshold": {"type": "number", "default": 0.3} }
>
> },
>
> "D-03": {
>
> "type": "object", "properties": {
>
> "margin": {"type": "number", "default": 0.02}, "bootstrap_iterations":
> {"type": "integer", "default": 1000}, "bootstrap_seed": {"type":
> "integer", "default": 42}
>
> } }
>
> } }

}

**17.4** **Benchmark** **Configuration** **Sub-schema**

{

> "benchmark_config": { "type": "object", "required": \["suite"\],
> "properties": {
>
> "suite": {"type": "string"},
>
> "detectors": {"type": "array", "items": {"type": "string"}},
> "config_overrides": {"type": "object"},
>
> "seed": {"type": "integer", "default": 42},
>
> "output_formats": {"type": "array", "items": {"enum": \["json",
> "md"\]}} }

} }

**17.5** **Validation** **Rules**

> 1\. **Strict** **schema:** Unknown fields rejected.
>
> 2\. **Date** **ordering:** since ≤ until if both provided.
>
> 3\. **Weight** **normalization:** If detector_weights provided and sum
> ≠ 1.0, normalize or raise ConfigValidationError.
>
> 4\. **Metric/detector** **validation:** All IDs must exist in Registry
> (M-13).
>
> 5\. **Path** **validation:** repo must be valid path or URL;
> output_dir must be writable.

**SECTION** **18** **—** **JOB** **MANIFEST** **SCHEMA**

**18.1** **Schema** **Definition** **Source:** TRD §5.14, AFD §8.1

{

> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "JobManifest",
>
> "type": "object",
>
> "required": \["job_id", "job_type", "job_params", "output_dir",
> "created_at", "status"\],
>
> "properties": {
>
> "job_id": {"type": "string", "format": "uuid"},
>
> "job_type": {"enum": \["analyze", "benchmark", "explain", "export",
> "generate"\]},
>
> "job_params": {"type": "object"}, "output_dir": {"type": "string"},
>
> "created_at": {"type": "string", "format": "date-time"},
>
> "status": {"enum": \["created", "queued", "running", "completed",
> "failed", "cancelled"\]},
>
> "progress": {"type": "number", "minimum": 0, "maximum": 1},
> "current_stage": {"type": "string"},
>
> "result_paths": {"type": "object"}, "error_metadata": {"type":
> "object"}
>
> } }
>
> **18.2** **Field** **Definitions**

||
||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||

> **18.3** **Python** **Dataclass**
>
> @dataclass
>
> class JobManifest: job_id: str job_type: str
>
> job_params: Dict\[str, Any\] output_dir: Path created_at: datetime
> status: str
>
> progress: float = 0.0 current_stage: Optional\[str\] = None
>
> result_paths: Optional\[Dict\[str, str\]\] = None error_metadata:
> Optional\[Dict\[str, str\]\] = None
>
> **SECTION** **19** **—** **STATE** **OBJECT** **SCHEMA**
>
> **19.1** **Schema** **Definition** **Source:** TRD §5.16, AFD §8.1
>
> {
>
> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "StateObject",
>
> "type": "object",
>
> "required": \["job_id", "current_status", "history"\], "properties": {
>
> "job_id": {"type": "string", "format": "uuid"},
>
> "current_status": {"enum": \["created", "queued", "running",
> "completed", "failed", "cancelled"\]},
>
> "history": { "type": "array", "items": {
>
> "type": "object",
>
> "required": \["status", "timestamp"\], "properties": {
>
> "status": {"type": "string"},
>
> "timestamp": {"type": "string", "format": "date-time"}, "stage":
> {"type": "string"},
>
> "progress": {"type": "number"} }
>
> } },
>
> "recovery_metadata": { "type": "object", "properties": {
>
> "last_completed_stage": {"type": "string"}, "checkpoint_path":
> {"type": "string"}, "retry_count": {"type": "integer", "minimum": 0}
>
> } },
>
> "checkpoint_metadata": { "type": "object", "properties": {
>
> "has_checkpoint": {"type": "boolean"}, "checkpoint_stage": {"type":
> "string"},
>
> "checkpoint_files": {"type": "array", "items": {"type": "string"}} }
>
> } }
>
> }
>
> **19.2** **Field** **Definitions**

||
||
||
||
||
||
||
||
||
||
||
||

> **19.3** **Atomic** **Write** **Contract**
>
> State files are written atomically: create temp file in same
> directory, write JSON, then os.rename() to target.
>
> Target path: ~/.miie/jobs/{job_id}/state.json.
>
> Read on every poll request; write on every state transition.

**SECTION** **20** **—** **REPORT** **SCHEMAS**

**20.1** **results.json** **Schema** **Source:** TRD §20.1, TFS Appendix
A

{

> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "results.json",
>
> "type": "object",

"required": \["miie_version", "generated_at", "config_hash",
"repository", "windows", "metrics", "detector_results", "scores",
"evidence", "explanations"\],

> "properties": {
>
> "miie_version": {"type": "string"},
>
> "generated_at": {"type": "string", "format": "date-time"},
> "config_hash": {"type": "string"},
>
> "repository": {"type": "object"}, "windows": {"type": "array"},
> "metrics": {"type": "object"}, "detector_results": {"type": "object"},
> "scores": {"type": "object"}, "evidence": {"type": "object"},
> "explanations": {"type": "array"}, "run_metadata": {"type": "object"}

} }

**20.2** **benchmark_run.json** **Schema** **Source:** TRD §17.8, BSD
§14.5

Identical to BenchmarkRun schema (Section 15).

**20.3** **evaluation.json** **Schema** **Source:** BSD §14.5, TFS §8.7

Identical to EvaluationResult schema (Section 16).

**20.4** **evidence.json** **Schema** **Source:** TFS Appendix A

Identical to EvidencePackage schema (Section 10).

**20.5** **manifest.json** **Schema** **Source:** TRD §21.4, §21.6

{

> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "manifest.json",
>
> "type": "object",

"required": \["miie_version", "git_commit", "python_version",
"dependency_hash", "config_hash", "seed", "timestamp", "platform"\],

> "properties": {
>
> "miie_version": {"type": "string"}, "git_commit": {"type": "string"},
> "python_version": {"type": "string"}, "dependency_hash": {"type":
> "string"}, "config_hash": {"type": "string"}, "seed": {"type":
> "integer"},
>
> "timestamp": {"type": "string", "format": "date-time"}, "platform":
> {"type": "string"},
>
> "run_id": {"type": "string"}, "artifact_checksums": {
>
> "type": "object", "properties": {
>
> "results.json": {"type": "string"}, "evidence.json": {"type":
> "string"}, "metrics.csv": {"type": "string"}
>
> } }

} }

**20.6** **run_metrics.json** **Schema** **Source:** TRD §21.6

{

> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "run_metrics.json",
>
> "type": "object",

"required": \["duration_seconds", "memory_peak_mb", "cpu_time_seconds",
"stage_timings"\],

> "properties": {
>
> "duration_seconds": {"type": "number"}, "memory_peak_mb": {"type":
> "number"}, "cpu_time_seconds": {"type": "number"}, "stage_timings":
> {"type": "object"}, "detector_timings": {"type": "object"},
> "extraction_timings": {"type": "object"}

} }

**20.7** **comparison_report.json** **Schema** **Source:** AFD §4.6

{

> "\$schema": "http://json-schema.org/draft-07/schema#", "title":
> "comparison_report.json",
>
> "type": "object",

"required": \["miie_version", "generated_at", "config_a", "config_b",
"delta_scores", "narrative"\],

> "properties": {
>
> "miie_version": {"type": "string"},
>
> "generated_at": {"type": "string", "format": "date-time"}, "config_a":
> {"type": "object"},
>
> "config_b": {"type": "object"}, "delta_scores": {
>
> "type": "object", "properties": {
>
> "overall_delta": {"type": "number"},
>
> "per_metric_delta": {"type": "object"} }
>
> },
>
> "narrative": {"type": "string"} }

}

**20.8** **explanation.json** **Schema** **Source:** TRD §20.3

Identical to ExplanationReport schema (Section 11).

**SECTION** **21** **—** **EXPORT** **CONTRACTS**

**21.1** **JSON** **Export** **Contract**

> **Format:** JSON Schema draft-07 compliant.
>
> **Encoding:** UTF-8, no BOM.
>
> **Indentation:** 2 spaces for readability.
>
> **Key** **ordering:** Alphabetical (sorted) for deterministic output.
>
> **Null** **handling:** Explicit null for missing values; optional
> fields may be omitted.
>
> **Numeric** **precision:** Floats serialized with 6 decimal places
> minimum.
>
> **Validation:** All JSON exports validated against their schema before
> writing. Schema violation → abort with error.
>
> **Compatibility:** JSON exports from v1.0.0 must be readable by v1.1.0
> parsers (additive only).

**21.2** **CSV** **Export** **Contract**

> **Format:** RFC 4180 compliant.
>
> **Encoding:** UTF-8.
>
> **Delimiter:** Comma ,.
>
> **Quote** **character:** Double quote ".
>
> **Header** **row:** Mandatory; column names in snake_case.
>
> **Column** **ordering:** Deterministic per schema definition
> (alphabetical within logical groups).
>
> **Null** **handling:** Empty string '' for null values.
>
> **Boolean** **handling:** true/false lowercase strings.
>
> **Timestamp** **handling:** ISO 8601 format in UTC.
>
> **File** **naming:** metrics.csv for raw metrics; scores.csv for
> scores (if exported separately).

**21.3** **Markdown** **Export** **Contract**

> **Format:** GitHub-Flavored Markdown.
>
> **Sections:** Frozen order per TRD §20.3: 1. Header (title, timestamp,
> version)
>
> 2\. Executive Summary (overall scores, failure count)
>
> 3\. Per-Metric Analysis (score, detectors, explanations)
>
> 4\. Evidence Details (test statistics, window comparisons)
>
> 5\. Recommendations (actions based on findings)
>
> 6\. Disclaimer (human oversight required)
>
> 7\. Appendix (configuration, provenance, formulas)
>
> **Table** **formatting:** Pipe tables with alignment indicators.
>
> **Code** **blocks:** JSON snippets in fenced code blocks with language
> tag.
>
> **File** **naming:** report.md for analysis; benchmark_report.md for
> benchmarks; comparison_report.md for comparisons.

**21.4** **Validation** **Rules**

> **Pre-write** **validation:** All exports pass schema validation
> before filesystem write.
>
> **Post-write** **validation:** Optional checksum computed and stored
> in manifest.
>
> **Disk** **space** **check:** Estimated size computed before write;
> abort if insufficient space.
>
> **Partial** **save:** On disk-full error, attempt to save completed
> files; report which files were saved.

**SECTION** **22** **—** **DIRECTORY** **ARCHITECTURE**

**22.1** **Complete** **Filesystem** **Layout** **Source:** TRD §16.1,
§25.1, AFD §22

~/.miie/

├── config.yaml \# User configuration (YAML 1.2 strict) ├── cache/

│ ├── repos/

│ │ └── {repo_id}/ \# Cloned repositories (Git object model) │ │ ├──
.git/

│ │ └── ...

│ └── cleanup.log \# Auto-cleanup timestamps ├── benchmarks/

│ ├── metric-drift-v1.0.0/

│ │ ├── manifest.json \# Suite metadata (DatasetManifest) │ │ ├──
schema.json \# Suite-specific schema reference │ │ ├──
ground_truth-v1.0.0.json \# Ground truth labels (GroundTruth) │ │ ├──
data/

│ │ │ ├── repo_001/

> │ │ │ │ ├── metrics.json \# Metric time series (BSD Metric Schema) │ │
> │ │ ├── windows.json \# Window definitions
>
> │ │ │ │ └── metadata.json \# Repository metadata
> (SyntheticRepositoryMetadata)
>
> │ │ │ ├── repo_002/ │ │ │ └── ...
>
> │ │ ├── evidence/
>
> │ │ │ ├── repo_001/
>
> │ │ │ │ ├── cdf_plots/ \# MDE-01 visual evidence │ │ │ │ ├──
> scatter_plots/ \# MDE-02 visual evidence │ │ │ │ └── histograms/ \#
> MDE-03 visual evidence │ │ │ └── ...
>
> │ │ └── documentation/

│ │ ├── generation_log.md │ │ └── annotation_log.md

> │ ├── correlation-breakdown-v1.0.0/ │ │ └── ... (same structure)
>
> │ └── threshold-compression-v1.0.0/ │ └── ... (same structure)
>
> ├── jobs/ \# API job state (if API used) │ └── {job_id}/

│ ├── manifest.json \# JobManifest │ ├── state.json \# StateObject

> │ └── results/ \# Job-specific output files │ ├── results.json
>
> │ ├── report.md │ └── ...
>
> ├── registries/
>
> │ ├── metrics.json \# Frozen metric definitions (M-01..M-07) │ └──
> detectors.json \# Frozen detector definitions (D-01..D-03) └── logs/
>
> └── {timestamp}.log \# Application logs (text)
>
> User-specified output directory (default: ./miie-output/):
>
> ├── results.json \# Full AnalysisResult (JSON)
>
> ├── report.md \# Human-readable report (Markdown) ├── metrics.csv \#
> Tabular raw metrics (CSV)
>
> ├── evidence.json \# EvidencePackage (JSON)
>
> ├── manifest.json \# Run manifest with checksums └── run_metrics.json
> \# Performance metrics (JSON)
>
> **22.2** **Directory** **Definitions**

||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||

> **SECTION** **23** **—** **FILE** **LIFECYCLE** **RULES**
>
> **23.1** **Creation** **Rules**
>
> **Atomic** **creation:** All files written to temp file in target
> directory, then renamed.
>
> **Directory** **creation:** Directories created with exist_ok=True and
> correct permissions (0o700 for cache/jobs, 0o755 for
> benchmarks/output).
>
> **Manifest** **first:** manifest.json is the last file written in any
> output set (after all data files are complete and checksummed).
>
> **23.2** **Update** **Rules**
>
> **Immutable** **artifacts:** Benchmark datasets, ground truth, and
> published suite manifests are immutable. No updates permitted.
>
> **Mutable** **state:** state.json updated atomically during API job
> execution.
>
> **Config** **updates:** config.yaml is user-managed; MIIE reads but
> does not modify.
>
> **Log** **updates:** Log files appended; rotation at 10MB.
>
> **23.3** **Archival** **Rules**
>
> **Job** **archival:** Jobs older than 30 days moved to
> ~/.miie/jobs/archive/ (if implemented) or deleted.
>
> **Log** **archival:** Logs older than 90 days compressed to .gz or
> deleted.
>
> **Cache** **archival:** Repositories evicted from cache based on LRU;
> no explicit archive.
>
> **23.4** **Deletion** **Rules**
>
> **Cache** **cleanup:** Triggered on startup if cache \> 5GB. LRU
> eviction removes oldest repos.
>
> --keep-cache flag prevents deletion for specific repo.
>
> **Job** **cleanup:** Configurable retention (default 30 days). Manual
> cleanup via rm -rf ~/.miie/jobs/{job_id}/.
>
> **Output** **deletion:** User-managed; MIIE never deletes user output
> directories.
>
> **23.5** **Recovery** **Rules**
>
> **Partial** **results:** On fatal error, all artifacts from completed
> stages are preserved in output directory.
>
> **State** **recovery:** If state.json corrupted, attempt to read from
> state.json.bak (if exists). If both corrupted, mark job as failed.
>
> **Cache** **recovery:** If cache corrupted, delete and re-clone on
> next analysis.
>
> **23.6** **Retention** **Summary**

||
||
||
||
||
||
||
||
||
||

> **SECTION** **24** **—** **VERSIONING** **STRATEGY**
>
> **24.1** **Schema** **Versioning**
>
> **Format:** MAJOR.MINOR.PATCH (e.g., 1.0.0).
>
> **Major** **bump:** Breaking field changes, removal of required
> fields, schema restructuring.
>
> **Minor** **bump:** Additive non-breaking changes, new optional
> fields, new object types.
>
> **Patch** **bump:** Documentation fixes, description updates, no
> structural changes.
>
> **Schema** **version** **manifest:** Every schema file includes
> "\$schema_version" field.
>
> **Compatibility:** Consumers must read their declared major version.
> Unknown major version → error.
>
> **24.2** **Dataset** **Versioning**
>
> **Synthetic** **datasets:** Versioned with their parent suite (e.g.,
> metric-drift-v1.0.0).
>
> **Minor** **bump:** Additional datasets added to suite; existing
> datasets unchanged.
>
> **Major** **bump:** Existing dataset modified (regenerated,
> re-labeled); all previous evaluation results invalidated.
>
> **24.3** **Benchmark** **Versioning**
>
> **Suite** **version:** Independent of MIIE version. Format:
> {suite_name}-v{major}. {minor}.{patch}.
>
> **Bump** **rules** **per** **BSD** **§15:**
>
> Major: Ground truth label changes, schema changes, dataset removal.
>
> Minor: New datasets added, non-breaking metadata additions.
>
> Patch: Documentation fixes, plot regeneration.
>
> **Compatibility** **matrix:**

||
||
||
||
||
||

> **24.4** **Ground** **Truth** **Versioning**
>
> **Format:** ground_truth-v{major}.{minor}.{patch}.json.
>
> **Independent** **of** **suite** **version:** Ground truth may be
> updated without changing suite datasets.
>
> **Major** **bump:** Label changes, schema changes.
>
> **Minor** **bump:** Evidence additions, metadata corrections.
>
> **Patch** **bump:** Documentation updates.

**24.5** **Manifest** **Versioning**

> **Run** **manifest:** Versioned by MIIE release (e.g., manifest from
> MIIE 1.0.0 has schema version 1.0.0).
>
> **Job** **manifest:** Versioned by MIIE release.
>
> **Dataset** **manifest:** Versioned with suite.

**24.6** **Backward** **Compatibility**

> **Within** **major** **version:** All v1.x.x schemas must be readable
> by v1.y.y parsers (y ≥ x).
>
> **Breaking** **changes:** Require new major version and explicit
> migration guide.
>
> **Deprecation:** Deprecated fields marked with deprecated: true in
> schema; supported for 1 major version, then removed.

**SECTION** **25** **—** **VALIDATION** **FRAMEWORK**

**25.1** **Schema** **Validation** **Rules**

> **Validator:** JSON Schema draft-07 compliant validator (e.g.,
> jsonschema Python library).
>
> **Strict** **mode:** additionalProperties: false on all objects unless
> explicitly extensible.
>
> **Required** **fields:** All required arrays enforced. Missing field →
> validation error.
>
> **Type** **coercion:** Disabled. Wrong type → validation error (not
> coercion).
>
> **Format** **validation:** date-time, date, uuid, uri formats
> validated via format_checker.

**25.2** **Export** **Validation**

> **Pre-write:** All export objects validated against their schema
> before filesystem write.
>
> **Post-write:** Optional checksum verification (SHA-256) against
> manifest.
>
> **CSV** **validation:** Header row matches schema column names; row
> count matches expected; no empty required fields.
>
> **Markdown** **validation:** Non-empty report; all required sections
> present; template rendering successful.

**25.3** **Manifest** **Validation**

> **Checksum** **verification:** manifest.json includes SHA-256 of
> results.json, evidence.json, metrics.csv. Optional verification on
> load.
>
> **Dependency** **hash:** dependency_hash in manifest compared against
> current environment on load (warning if mismatch, not error).
>
> **Config** **hash:** config_hash compared against current config on
> re-run (for reproducibility verification).

**25.4** **Benchmark** **Artifact** **Validation**

> **Dataset** **validation:** On load, validate metrics.json,
> windows.json, metadata.json against BSD schemas.
>
> **Ground** **truth** **validation:** Validate ground_truth.json
> against BSD Ground Truth Schema. Check that all labels reference
> existing datasets.
>
> **Checksum** **validation:** Dataset metadata.json includes checksum
> of metrics.json; verify on load.
>
> **Suite** **manifest** **validation:** Validate manifest.json against
> BSD Metadata Schema on suite load.

**25.5** **Evidence** **Validation**

> **Evidence** **completeness:** Every positive label in ground truth
> must have corresponding evidence files (plots, statistics) in
> evidence/ directory.
>
> **Evidence** **schema:** Annotation files (annotations.json) validated
> against BSD Annotation Schema.
>
> **Provenance:** Every evidence item includes annotator_id, timestamp,
> and annotation_id.

**25.6** **Error** **Response** **Validation**

> **CLI** **errors:** Format \[ERROR-CODE\] Description. Suggestion:
> Action. (per TFS §13.8).
>
> **API** **errors:** RFC 7807 Problem Details format (type, title,
> status, detail, instance).
>
> **Validation** **error** **messages:** Include specific field name,
> expected type, actual type/value, and line number if applicable.

**SECTION** **26** **—** **REPRODUCIBILITY** **FRAMEWORK**

**26.1** **Hashing** **Strategy**

> **Algorithm:** SHA-256 for all checksums.
>
> **Config** **hash:** SHA-256 of JSON-serialized final merged
> configuration (sorted keys, no whitespace variation).
>
> **Dependency** **hash:** SHA-256 of poetry.lock or requirements.txt
> content.
>
> **Evidence** **hash:** SHA-256 of evidence.json file content.
>
> **Metric** **hash:** SHA-256 of metrics.csv or raw metric JSON
> content.

**26.2** **Checksums**

> **Manifest** **checksums:** manifest.json contains artifact_checksums
> object mapping filename → SHA-256 hex string.
>
> **Benchmark** **checksums:** metadata.json contains metrics_checksum
> (SHA-256 of metrics.json).
>
> **Ground** **truth** **checksums:** ground_truth.json includes
> checksum field (SHA-256 of file content).
>
> **Verification** **function:** verify_checksum(file_path, expected)
> uses hmac.compare_digest() for timing-safe comparison.

**26.3** **Manifest** **Tracking**

> **Run** **manifest:** Every analysis produces manifest.json with:
>
> miie_version, git_commit, python_version, dependency_hash,
> config_hash, seed, timestamp, platform, run_id.
>
> **Benchmark** **manifest:** Every benchmark run produces
> run_manifest.json with:
>
> detector_id, detector_version, suite_id, suite_version, seed,
> timestamp, environment_hash.
>
> **Job** **manifest:** API jobs produce manifest.json in job directory
> with full job parameters and status history.

**26.4** **Dataset** **Fingerprints**

> **Synthetic** **dataset** **fingerprint:** SHA-256 of metrics.json +
> windows.json + metadata.json concatenated and sorted by key.
>
> **Fingerprint** **storage:** Stored in metadata.json as
> dataset_fingerprint.
>
> **Fingerprint** **use:** Verify dataset integrity before benchmark
> execution; detect corruption or modification.

**26.5** **Benchmark** **Fingerprints**

> **Suite** **fingerprint:** SHA-256 of all dataset fingerprints sorted
> by repo_id.
>
> **Fingerprint** **storage:** Stored in suite manifest.json as
> suite_fingerprint.
>
> **Fingerprint** **use:** Verify suite integrity on load; detect
> missing or corrupted datasets.

**26.6** **Experiment** **Reproduction** To reproduce any published
result:

> 1\. Install exact dependency versions: pip install -r requirements.txt
> (or poetry install).
>
> 2\. Verify MIIE version matches manifest.json.
>
> 3\. Run with exact config and seed: miie analyze --repo {repo}
> --config {config} --seed 42.
>
> 4\. Compare manifest.json checksums and results.json MD5.
>
> **26.7** **Artifact** **Integrity**
>
> **Immutable** **releases:** Once published, benchmark artifacts
> (datasets, ground truth, suite manifests) are immutable.
>
> **Version** **control:** All benchmark artifacts tracked in version
> control (Git) with tags.
>
> **Backup:** Benchmark suites backed up by maintainers to secondary
> storage.
>
> **SECTION** **27** **—** **STORAGE** **RISK** **ASSESSMENT**
>
> **27.1** **Schema** **Risks**

||
||
||
||
||
||

> **27.2** **Migration** **Risks**

||
||
||
||

||
||
||
||
||
||

> **27.3** **Data** **Corruption** **Risks**

||
||
||
||
||
||
||

> **27.4** **Version** **Drift** **Risks**

||
||
||
||

||
||
||
||
||
||

> **27.5** **Serialization** **Risks**

||
||
||
||
||
||
||

> **SECTION** **28** **—** **TRACEABILITY** **MATRIX**
>
> **28.1** **Schema-to-Source** **Traceability**

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

**28.2** **Requirement** **Coverage** **Verification**

> **PRD** **§7** **(In** **Scope):** All 10 core metric schemas, 3
> detector schemas, IS/CS schemas, evidence, explanation, and export
> schemas trace directly to PRD.
>
> **PRD** **§9** **(Version** **1** **Freeze):** All 5 frozen workflows
> (WF-01–WF-05) plus maintainer workflows (WF-06–WF-07) have
> corresponding schema definitions.
>
> **TFS** **§2** **(Metric** **Freeze):** M-01–M-07 field definitions,
> ranges, and missing data strategies frozen in Section 6.
>
> **TFS** **§4–5** **(Detector** **Freeze):** D-01–D-03 output schemas,
> thresholds, and statistical fields frozen in Section 8.
>
> **TFS** **§6–7** **(Score** **Freeze):** IS/CS formulas, factors,
> weights, and edge cases frozen in Section 9.
>
> **TFS** **§12** **(Data** **Freeze):** Input formats, required fields,
> optional fields, missing data policy, and validation rules frozen in
> Sections 6, 17.
>
> **TFS** **§13** **(CLI** **Freeze):** Configuration schema includes
> all frozen CLI arguments and exit codes mapped in Section 17.
>
> **TFS** **§14** **(API** **Freeze):** Job manifest and state object
> schemas support all frozen API endpoints and status codes (Section
> 18–19).
>
> **BSD** **§5** **(Benchmark** **Tasks):** BenchmarkRun,
> EvaluationResult, and DatasetManifest schemas support B-01, B-02, B-03
> (Sections 13–16).
>
> **BSD** **§9** **(Pathology** **Injection):** PathologyMetadata schema
> captures all injection parameters (Section 13.3).
>
> **BSD** **§10–11** **(Ground** **Truth):** GroundTruth and Annotation
> schemas capture label lifecycle, evidence requirements, and
> inter-rater reliability (Section 14).
>
> **BSD** **§13** **(Benchmark** **Runner):** BenchmarkRun schema
> captures predictions, timing, and environment (Section 15).
>
> **BSD** **§14** **(Evaluation):** EvaluationResult schema captures all
> 8 frozen metrics and confusion matrix (Section 16).
>
> **TRD** **§16** **(Storage):** Directory architecture and file
> lifecycle rules trace to TRD §16.1–16.4 (Section 22–23).
>
> **TRD** **§21** **(Reproducibility):** Manifest, checksum, and
> fingerprint schemas trace to TRD §21.4–21.8 (Section 26).
>
> **AFD** **§8** **(State** **Machine):** StateObject and JobManifest
> schemas support all defined states and transitions (Section 18–19).
>
> **AFD** **§9** **(Error** **Flow):** Error metadata structures in
> JobManifest and EvidencePackage support all defined error categories
> (Section 9, 18).
>
> **SECTION** **29** **—** **SCHEMA** **COMPLETENESS** **AUDIT**
>
> **29.1** **Missing** **Fields** **Audit**

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **Result:** No missing fields identified. All required fields from
> source documents are present.
>
> **29.2** **Redundancy** **Audit**

||
||
||
||

||
||
||
||
||
||
||
||

> **Result:** No redundancy identified. All repeated fields serve
> distinct purposes in their contexts.
>
> **29.3** **Ambiguity** **Audit**

||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||

> **29.4** **Inconsistency** **Audit**

||
||
||
||
||
||
||
||
||
||

> **29.5** **Contract** **Violations** **Audit**

||
||
||
||
||

||
||
||
||
||
||
||
||
||

> **SECTION** **30** **—** **FINAL** **BSD** **VERDICT**
>
> **30.1** **Primary** **Question**
>
> Can three independent engineering teams generate identical data
> structures and storage layouts using this document?
>
> **30.2** **Answer** **YES.**
>
> **30.3** **Justification**
>
> Three independent engineering teams using the frozen source documents
> (IPD, PRD, TFS, BSD, TRD, AFD) and this BSD-Engineering v1.0 would
> produce identical data structures and storage layouts because:
>
> 1\. **Object** **Registry** **Completeness:** Section 3 defines all 19
> canonical objects (OBJ-01 through OBJ-19) with unique IDs, producers,
> consumers, storage locations, serialization formats, lifecycles, and
> versioning rules. No object is undefined or ambiguous.
>
> 2\. **Schema** **Precision:** Sections 5–20 provide JSON Schema
> draft-07 definitions, Python dataclass equivalents, and field-level
> documentation (name, type, required, description, validation, example)
> for every domain object. No field lacks a type or validation rule.
>
> 3\. **Global** **Standards:** Section 4 establishes unambiguous naming
> conventions, type conventions, timestamp/UUID/version standards, null
> handling, numeric precision rules, and serialization rules. These
> standards prevent divergent encoding decisions.
>
> 4\. **Directory** **Architecture** **Frozen:** Section 22 provides a
> complete filesystem layout with directory purposes, contents,
> retention policies, ownership, and permissions. Three teams would
> create identical directory structures.
>
> 5\. **File** **Lifecycle** **Rules:** Section 23 defines creation,
> update, archival, deletion, recovery, and retention rules for every
> data type. Teams would implement identical lifecycle behavior.
>
> 6\. **Versioning** **Strategy:** Section 24 defines schema, dataset,
> benchmark, ground truth, and manifest versioning with bump rules and
> backward compatibility contracts. Teams would version artifacts
> identically.
>
> 7\. **Validation** **Framework:** Section 25 defines validation rules
> for all schemas, exports, manifests, benchmark artifacts, and evidence
> artifacts. Teams would enforce identical validation boundaries.
>
> 8\. **Reproducibility** **Framework:** Section 26 defines hashing,
> checksums, manifest tracking, dataset fingerprints, benchmark
> fingerprints, and experiment reproduction procedures. Teams would
> produce identical fingerprints for identical inputs.
>
> 9\. **Traceability:** Section 28 maps every schema to PRD
> requirements, TRD modules, AFD workflows, BSD components, and TFS
> constructs. Every schema is justified by source documents; no orphan
> schemas exist.
>
> 10.**Ambiguity** **Resolution:** Section 29 audits and resolves
> missing fields, redundancy, ambiguity, inconsistency, and contract
> violations. No residual ambiguity permits divergent implementations.
>
> 11.**Storage** **Risk** **Assessment:** Section 27 identifies and
> mitigates schema, migration, corruption, version drift, and
> serialization risks. Teams would implement identical safeguards.
>
> 12.**Benchmark** **Alignment:** Sections 13–16 align exactly with BSD
> v1.0 benchmark schemas (Repository, Metric, Annotation, Ground Truth,
> Evaluation, Metadata). Teams would produce bitwise-identical benchmark
> artifacts.

**30.4** **Declaration**

**Backend** **Schema** **Document** **(BSD-Engineering** **v1.0)**
**Status:** **Schema** **Authority**

**Verdict:** **SCHEMA** **DESIGN** **APPROVED** **Ready** **for**
**API** **Contract** **Specification**

This document provides sufficient data structure detail for three
independent engineering teams to implement the MIIE v1.0 backend such
that:

> All domain objects have identical fields, types, and validation rules.
>
> All persistent artifacts have identical serialization formats and
> schemas.
>
> All filesystem layouts have identical directory structures and file
> lifecycles.
>
> All versioning and reproducibility contracts produce identical
> behavior.
>
> All benchmark and ground truth schemas are scientifically rigorous and
> publication-ready.
>
> **Backend** **development** **may** **commence** **immediately.**
>
> **APPENDIX** **A** **—** **Document** **Control**

||
||
||
||

> **APPENDIX** **B** **—** **Glossary**

||
||
||
||
||
||
||
||
||
||
||
||
||

> **APPENDIX** **C** **—** **JSON** **Schema** **Quick** **Reference**

||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> *END* *OF* *BACKEND* *SCHEMA* *DOCUMENT* *(BSD-Engineering* *v1.0)*
