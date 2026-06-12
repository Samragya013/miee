**API** **Contract** **Specification** **(ACS** **v1.0)** **System:**
Measurement Integrity Intelligence Engine (MIIE) **Version:** 1.0.0

**Status:** Contract Authority — Ready for Implementation Plan **Date:**
2026-06-07

**Inputs:** IPD v1.1 FINAL \| PRD v1.0 \| TFS v1.0 \| BSD v1.0 \| TRD
v1.0 \| AFD v1.0 \| BSD-Engineering v1.0

**Objective:** Define every communication contract, request/response
schema, validation rule, module interface, CLI contract, and internal
API such that three independent engineering teams build compatible
modules without additional clarification.

**SECTION** **1** **—** **EXECUTIVE** **SUMMARY**

**1.1** **Purpose**

The API Contract Specification (ACS v1.0) is the **integration**
**authority** for MIIE v1.0. It governs:

> How modules communicate via function calls, HTTP requests, and CLI
> invocations.
>
> The exact shape of every request payload, response payload, and error
> payload.
>
> The validation rules that must be applied before a contract is
> accepted.
>
> The error responses that must be returned when a contract is violated.
>
> The versioning rules that ensure backward and forward compatibility.
>
> The security boundaries that prevent injection, traversal, and data
> leakage.

**1.2** **Scope**

This document defines contracts for:

> **18** **internal** **module** **interfaces** (INT-01 through INT-18)
> covering the full processing pipeline and benchmark subsystem.
>
> **8** **CLI** **commands** (ingest, analyze, detect, benchmark,
> evaluate, explain, export, generate) with frozen arguments, flags,
> exit codes, and error formats.
>
> **6** **REST** **API** **endpoints** (/v1/analyze, /v1/benchmark,
> /v1/explain, /v1/export, /v1/jobs/{job_id}, /v1/health) with frozen
> request/response schemas and HTTP status codes.
>
> **3** **detector** **invocation** **contracts** (D-01, D-02, D-03)
> with frozen input/output schemas and statistical thresholds.
>
> **7** **metric** **extraction** **contracts** (M-01 through M-07) with
> frozen input/output schemas and validation rules.
>
> **5** **workflow** **dispatch** **contracts** (WF-01 through WF-05)
> with frozen orchestration sequences.
>
> **Error** **contract** **framework** with unified error model,
> severity levels, recovery strategies, and user visibility rules.
>
> **Validation** **contract** **framework** covering input, output,
> schema, manifest, benchmark, evidence, and report validation.
>
> **Performance** **contracts** with response time budgets, payload size
> limits, memory constraints, and timeout rules.
>
> **Observability** **contracts** with logging, tracing, audit, and
> diagnostic telemetry.

**1.3** **Non-Scope**

The following are explicitly excluded from ACS v1.0:

> **Implementation** **details:** Class hierarchies, dependency
> injection frameworks, or specific library choices (governed by TRD).
>
> **UI** **contracts:** No GUI or web interface contracts (V1 is CLI/API
> only per TFS §1.5).
>
> **Database** **contracts:** No SQL schemas, ORM mappings, or query
> contracts (V1 is filesystem-only per TRD §1.8).
>
> **Real-time** **streaming** **contracts:** No WebSocket, SSE, or
> streaming protocols (V1 is batch-only per TFS §1.5).
>
> **Authentication/authorization** **contracts:** Beyond minimal API key
> header (TFS §14.2). No OAuth, JWT, RBAC, or session management.
>
> **Future** **version** **contracts:** No speculative interfaces for V2
> features (causal inference, real-time monitoring, plugin
> architecture).
>
> **SaaS/multi-tenancy** **contracts:** No tenant isolation, billing, or
> subscription APIs (V1 is self-hosted per TFS §1.5).

**1.4** **Contract** **Philosophy**

> 1\. **Explicit** **over** **implicit:** Every contract parameter is
> named, typed, and validated. No optional behavior without explicit
> default.
>
> 2\. **Fail-fast:** Invalid inputs are rejected at the contract
> boundary before any processing begins.
>
> 3\. **Deterministic:** Given identical inputs, every contract must
> produce identical outputs (bitwise-identical where applicable per TFS
> §3.1).
>
> 4\. **Self-describing:** Every response includes metadata about the
> contract version, schema version, and provenance.
>
> 5\. **Immutable** **contracts:** Once frozen in ACS v1.0, a contract
> cannot be modified without a version bump.
>
> 6\. **No** **silent** **coercion:** Type mismatches are errors, not
> warnings. Missing required fields are errors.

**1.5** **Versioning** **Philosophy**

> **Contract** **versions** **match** **MIIE** **versions:** ACS v1.0
> corresponds to MIIE v1.0.0.
>
> **Schema** **versions** **are** **independent:** JSON schemas
> versioned per BSD-Engineering §24.
>
> **Breaking** **changes** **require** **major** **version** **bump:**
> New required fields, removed fields, or changed types.
>
> **Additive** **changes** **are** **minor:** New optional fields, new
> enum values, new endpoints.
>
> **Documentation** **fixes** **are** **patch:** No contract changes.
>
> **Backward** **compatibility:** Consumers of v1.0.0 must read v1.1.0
> responses (additive only). Producers of v1.1.0 must accept v1.0.0
> requests.

**1.6** **Backward** **Compatibility** **Policy**

> 1\. **Request** **compatibility:** A v1.0.0 client sending a request
> to a v1.1.0 server must succeed if the request is valid per v1.0.0
> schema.
>
> 2\. **Response** **compatibility:** A v1.1.0 server responding to a
> v1.0.0 client must not include required fields that the client cannot
> parse. New fields must be optional.
>
> 3\. **Error** **compatibility:** Error codes and status codes from
> v1.0.0 must remain valid in v1.1.0. New error codes may be added but
> old ones cannot change meaning.
>
> 4\. **CLI** **compatibility:** Command names, argument names, and exit
> codes from v1.0.0 are frozen. New flags may be added as optional.

**1.7** **Integration** **Philosophy**

> 1\. **Direct** **invocation:** Internal module contracts use direct
> Python function calls (not RPC, not message queues) per TRD §2.4.
>
> 2\. **Filesystem** **as** **the** **database:** All persistent state
> is stored in files. Contracts read from and write to specific paths.
>
> 3\. **No** **shared** **mutable** **state:** Parallel execution
> (benchmark runner only) uses process isolation with no shared memory.
>
> 4\. **Atomic** **writes:** All file writes use temp-file-then-rename
> pattern to prevent corruption.
>
> 5\. **Checksum** **verification:** Critical artifacts include SHA-256
> checksums for integrity verification.

**SECTION** **2** **—** **COMMUNICATION** **ARCHITECTURE**

**2.1** **Module** **Communication** **Model**

┌─────────────────────────────────────────────────────────────────────────────┐
│ COMMUNICATION LAYERS

│
├─────────────────────────────────────────────────────────────────────────────┤
│ │

> │ LAYER 1: USER INTERFACE │
>
> │ ├── CLI (M-10) → Direct Python function calls to Layer 2 │ │ └──
> REST API (M-11) → HTTP routing to Layer 2 via FastAPI/stdio
>
> │
>
> │ │ │ LAYER 2: ORCHESTRATION │ │ ├── Workflow Engine (M-17) →
> Dispatches to Layer 3 per workflow ID │ │ ├── Pipeline Controller
> (M-15) → Sequences Layer 3 modules │ │ ├── Job Manager (M-14) →
> Manages async job lifecycle │ │ └── State Manager (M-16) → Atomic
> state read/write │ │ │ │ LAYER 3: PROCESSING │ │ ├── Repository
> Ingestion (M-01) → Returns RepositoryContext │ │ ├── Metric Extraction
> (M-02) → Returns MetricDataFrame │ │ ├── Window Segmentation (M-03) →
> Returns List\[Window\] │ │ ├── Detector Engine (M-05) → Returns
> DetectorResults │ │ ├── Scoring Engine (M-08) → Returns ScorePackage │
> │ ├── Evidence Aggregator → Returns EvidencePackage │ │ └──
> Explanation Generator (M-09) → Returns ExplanationReport │ │ │ │ LAYER
> 4: BENCHMARK │ │ ├── Dataset Generator (M-03) → Returns
> SyntheticDataset │ │ ├── Ground Truth Manager (M-04) → Returns
> GroundTruth │ │ ├── Benchmark Runner (M-06) → Returns BenchmarkRun │ │
> └── Evaluation Engine (M-07) → Returns EvaluationResult │ │ │ │ LAYER
> 5: OUTPUT │ │ └── Report Generator (M-09) → Writes files to filesystem
> │ │ │
> └─────────────────────────────────────────────────────────────────────────────┘
>
> **2.2** **Synchronous** **Flows**

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

> **2.3** **Asynchronous** **Flows**

||
||
||
||
||
||
||
||

> **2.4** **Internal** **APIs**

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

> **2.5** **External** **Interfaces**

||
||
||
||
||
||
||
||

> **2.6** **CLI** **Interfaces**

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

> **2.7** **Data** **Exchange** **Standards**

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

> **2.8** **Contract** **Lifecycle**

||
||
||
||
||
||
||
||

> **SECTION** **3** **—** **INTERFACE** **REGISTRY**
>
> **3.1** **Master** **Interface** **Registry**

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
||

> **SECTION** **4** **—** **GLOBAL** **API** **STANDARDS**
>
> **4.1** **Naming** **Convention**
>
> **Field** **names:** snake_case for all JSON, Python, and CLI
> arguments.
>
> **Interface** **IDs:** INT-NN format (e.g., INT-01, INT-18).
>
> **Flow** **IDs:** SYNC-NN or ASYNC-NN format.
>
> **API** **endpoint** **paths:** /v1/{resource}/{action} or
> /v1/{resource}/{id}/{action}.
>
> **HTTP** **headers:** Content-Type, Authorization, Accept. Custom
> headers prefixed with X-MIIE-.
>
> **File** **names:** snake_case with appropriate extension.
>
> **4.2** **Version** **Convention**
>
> **URL** **path** **versioning:** /v1/ prefix mandatory for all API
> endpoints.
>
> **Version** **in** **response** **body:** Every JSON response includes
> miie_version field.
>
> **Schema** **version:** Every schema-validated artifact includes
> schema_version field where applicable.
>
> **API** **version** **header:** Response includes X-MIIE-API-Version:
> 1.0.0.

**4.3** **Response** **Convention**

> **Success** **(200):** Synchronous completion. Body contains full
> result.
>
> **Accepted** **(202):** Async job accepted. Body contains job_id and
> poll_url.
>
> **Error** **(4xx/5xx):** RFC 7807 Problem Details format. Body
> contains type, title, status, detail, instance.
>
> **Content-Type:** application/json for all API responses.
>
> **Encoding:** UTF-8.

**4.4** **Error** **Convention**

> **CLI** **errors:** \[ERROR-CODE\] Description. Suggestion: Action.
> (per TFS §13.8).
>
> **API** **errors:** RFC 7807 Problem Details (type, title, status,
> detail, instance).
>
> **Internal** **errors:** Python exceptions caught at boundary, logged
> with traceback (if --verbose), mapped to user-facing error.
>
> **Error** **codes:** Uppercase with hyphens (e.g., INVALID-REPO,
> DETECTOR-CRASH).

**4.5** **Pagination** **Rules**

> **V1** **scope:** Pagination not required for V1. All results returned
> in single response.
>
> **Future:** If pagination added in V2, use cursor-based pagination
> with limit and after parameters.
>
> **Max** **payload:** 10MB for API responses. If exceeded, return 413
> Payload Too Large with suggestion to use CLI.

**4.6** **Timestamp** **Rules**

> **Format:** ISO 8601 UTC with Z suffix: YYYY-MM-DDTHH:MM:SSZ.
>
> **Precision:** Second-level.
>
> **Timezone:** All timestamps UTC. Offsets converted to UTC internally.
>
> **Range:** Valid dates between 1970-01-01 and 2099-12-31.

**4.7** **Identifier** **Rules**

> **UUID:** UUID4, lowercase, hyphenated. Used for job IDs.
>
> **Repo** **ID:** SHA-256 hex string (64 chars). Used for cache
> directory naming.
>
> **Metric** **ID:** M-NN format (e.g., M-01). Frozen.
>
> **Detector** **ID:** D-NN format (e.g., D-01). Frozen.
>
> **Window** **ID:** wNN format (e.g., w01). Zero-padded to 2 digits.
>
> **Suite** **ID:** {name}-v{version} format (e.g.,
> metric-drift-v1.0.0).

**4.8** **Serialization** **Rules**

> **JSON:** UTF-8, no BOM, sorted keys alphabetically, 2-space indent
> for pretty-print, compact for storage.
>
> **Null** **handling:** Explicit null for required nullable fields;
> optional fields may be omitted.
>
> **Float** **handling:** Full double precision internally; 6 decimal
> places minimum in JSON; 4 decimal places in display.
>
> **Boolean** **handling:** JSON true/false only. No string booleans.
>
> **Array** **handling:** Ordered arrays. No sparse arrays.

**4.9** **Validation** **Rules**

> **Strict** **schema:** Unknown fields rejected.
>
> **Required** **fields:** All required arrays enforced.
>
> **Type** **validation:** No coercion. Wrong type → validation error.
>
> **Format** **validation:** date-time, date, uuid, uri validated via
> format checker.
>
> **Range** **validation:** Numeric fields validated against
> minimum/maximum.
>
> **Pattern** **validation:** String fields validated against pattern
> regex.
>
> **Enum** **validation:** String fields validated against enum arrays.

**SECTION** **5** **—** **REPOSITORY** **INGESTION** **CONTRACTS**

**5.1** **INT-01:** **Repository** **Ingestion**

***Request*** ***Contract***

@dataclass

class IngestionInput:

> repo_path: str \# Local path or HTTPS/SSH URL cache_dir: Path =
> Path.home() / ".miie" / "cache" keep_cache: bool = False
>
> shallow_depth: Optional\[int\] = None

**JSON** **Schema** **(for** **API):**

{

> "type": "object", "required": \["repo_path"\], "properties": {
>
> "repo_path": {"type": "string", "minLength": 1}, "cache_dir": {"type":
> "string"},
>
> "keep_cache": {"type": "boolean", "default": false}, "shallow_depth":
> {"type": "integer", "minimum": 1}

} }

> ***Validation*** ***Rules***
>
> 1\. repo_path must be non-empty string.
>
> 2\. If repo_path is URL: scheme must be https:// or ssh:// (regex
> validation).
>
> 3\. If repo_path is local path: must exist and contain .git directory.
>
> 4\. cache_dir must be writable path.
>
> 5\. shallow_depth if provided must be ≥ 1.
>
> ***Response*** ***Contract***
>
> @dataclass
>
> class RepositoryContext: repo_id: str local_path: Path is_remote: bool
>
> remote_url: Optional\[str\] total_commits: int \# ≥ 10
> first_commit_date: datetime last_commit_date: datetime
> contributor_count: int \# ≥ 1 is_shallow: bool
>
> is_fork: bool
>
> language_distribution: Optional\[Dict\[str, int\]\]
>
> **JSON** **Schema:**
>
> {
>
> "type": "object",
>
> "required": \["repo_id", "local_path", "is_remote", "total_commits",
> "first_commit_date", "last_commit_date", "contributor_count",
> "is_shallow", "is_fork"\],
>
> "properties": {
>
> "repo_id": {"type": "string", "pattern": "^\[a-f0-9\]{64}\$"},
> "local_path": {"type": "string"},
>
> "is_remote": {"type": "boolean"},
>
> "remote_url": {"type": "string", "format": "uri"}, "total_commits":
> {"type": "integer", "minimum": 10}, "first_commit_date": {"type":
> "string", "format": "date-time"}, "last_commit_date": {"type":
> "string", "format": "date-time"}, "contributor_count": {"type":
> "integer", "minimum": 1}, "is_shallow": {"type": "boolean"},
>
> "is_fork": {"type": "boolean"},
>
> "language_distribution": {"type": "object", "additionalProperties":
> {"type": "integer"}}
>
> } }
>
> ***Error*** ***Codes***

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

> ***Example*** ***Payloads*** **Request:**
>
> {
>
> "repo_path": "https://github.com/org/repo.git", "keep_cache": false,
>
> "shallow_depth": 100 }
>
> **Response:**

{

> "repo_id":
> "a1b2c3d4e5f6789012345678901234567890abcd1234567890abcdef12345678",
> "local_path": "/home/user/.miie/cache/repos/a1b2c3d4.../",
>
> "is_remote": true,
>
> "remote_url": "https://github.com/org/repo.git", "total_commits":
> 1250,
>
> "first_commit_date": "2023-01-15T08:30:00Z", "last_commit_date":
> "2026-06-01T14:22:00Z", "contributor_count": 15,
>
> "is_shallow": false, "is_fork": false

}

**SECTION** **6** **—** **METRIC** **EXTRACTION** **CONTRACTS**

**6.1** **INT-02:** **Metric** **Extraction**

***Request*** ***Contract***

@dataclass

class ExtractionInput: repository_context: RepositoryContext

> metric_list: List\[str\] \# Items from {M-01..M-07, "all"} since:
> Optional\[datetime\] = None
>
> until: Optional\[datetime\] = None exclude_bots: bool = False

**JSON** **Schema:**

{

> "type": "object",
>
> "required": \["repository_context", "metric_list"\], "properties": {
>
> "repository_context": {"\$ref": "#/RepositoryContext"},

"metric_list": {"type": "array", "items": {"enum": \["M-01", "M-02",
"M-03", "M-04", "M-05", "M-06", "M-07", "all"\]}},

> "since": {"type": "string", "format": "date-time"}, "until": {"type":
> "string", "format": "date-time"}, "exclude_bots": {"type": "boolean",
> "default": false}

} }

***Validation*** ***Rules***

> 1\. repository_context must be valid RepositoryContext object.
>
> 2\. metric_list must contain valid metric IDs or "all". If "all",
> expanded to \[M-01..M-07\].
>
> 3\. since ≤ until if both provided.
>
> 4\. exclude_bots must be boolean.

***Response*** ***Contract***

\# MetricDataFrame is a pandas DataFrame with columns:

\# commit_hash (str), timestamp (datetime), metric_id (str), value
(float\|None),

> window_id (str\|None) \# When serialized: @dataclass
>
> class MetricDataFrameSchema: repo_id: str
>
> run_id: str timestamp: str
>
> metrics: Dict\[str, Dict\[str, List\[Optional\[float\]\]\]\] \#
> metric_id -\> window_id -\> values
>
> **JSON** **Schema:**
>
> {
>
> "type": "object",
>
> "required": \["repo_id", "run_id", "timestamp", "metrics"\],
> "properties": {
>
> "repo_id": {"type": "string"}, "run_id": {"type": "string"},
>
> "timestamp": {"type": "string", "format": "date-time"}, "metrics": {
>
> "type": "object", "properties": {
>
> "M-01": {"type": "object", "additionalProperties": {"type": "array",
> "items": {"type": \["number", "null"\]}}},
>
> "M-02": {"type": "object", "additionalProperties": {"type": "array",
> "items": {"type": \["number", "null"\]}}},
>
> "M-03": {"type": "object", "additionalProperties": {"type": "array",
> "items": {"type": \["number", "null"\]}}},
>
> "M-04": {"type": "object", "additionalProperties": {"type": "array",
> "items": {"type": \["number", "null"\]}}},
>
> "M-05": {"type": "object", "additionalProperties": {"type": "array",
> "items": {"type": \["number", "null"\]}}},
>
> "M-06": {"type": "object", "additionalProperties": {"type": "array",
> "items": {"type": \["number", "null"\]}}},
>
> "M-07": {"type": "object", "additionalProperties": {"type": "array",
> "items": {"type": \["number", "null"\]}}}
>
> } }
>
> } }
>
> ***Per-Metric*** ***Validation***

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

> ***Error*** ***Codes***

||
||
||
||
||
||
||

> ***Example*** ***Payloads*** **Request:**
>
> {
>
> "repository_context": {"repo_id": "abc...", "local_path": "/path",
> ...}, "metric_list": \["M-01", "M-02", "M-07"\],
>
> "since": "2025-01-01T00:00:00Z", "until": "2025-12-31T23:59:59Z",
> "exclude_bots": true
>
> }
>
> **Response** **(excerpt):**
>
> {
>
> "repo_id": "abc...",
>
> "run_id": "run_20260607_103100", "timestamp": "2026-06-07T10:31:00Z",
> "metrics": {
>
> "M-01": {
>
> "w01": \[82.5, 85.0, 88.2, null, 90.1\], "w02": \[91.3, 92.0, 93.5,
> 94.1, 95.0\]
>
> },
>
> "M-02": {
>
> "w01": \[5.2, 4.8, 6.1, 5.5, 4.9\], "w02": \[3.2, 3.5, 3.1, 3.8, 3.0\]
>
> } }

}

**SECTION** **7** **—** **WINDOW** **GENERATION** **CONTRACTS**

**7.1** **INT-03:** **Window** **Generation**

***Request*** ***Contract***

@dataclass

class SegmentationInput: metric_dataframe: MetricDataFrame

> strategy: str \# "time" \| "commit" \| "release" \| "custom"
>
> size: int \# days (time), commits (commit), or custom config
> custom_boundaries: Optional\[List\[Tuple\[datetime, datetime\]\]\] =
> None

**JSON** **Schema:**

{

> "type": "object",
>
> "required": \["metric_dataframe", "strategy", "size"\], "properties":
> {
>
> "metric_dataframe": {"type": "object"},
>
> "strategy": {"enum": \["time", "commit", "release", "custom"\]},
> "size": {"type": "integer", "minimum": 1}, "custom_boundaries": {
>
> "type": "array", "items": {
>
> "type": "array",
>
> "items": {"type": "string", "format": "date-time"}, "minItems": 2,
>
> "maxItems": 2 }
>
> } }

}

***Validation*** ***Rules***

> 1\. strategy must be one of the four frozen values.
>
> 2\. size ≥ 1.
>
> 3\. custom_boundaries required only if strategy="custom". Each
> boundary must be \[start, end\] with start \< end.
>
> 4\. Resulting windows must be non-overlapping and chronologically
> ordered.
>
> 5\. Minimum 2 windows required for drift detection (D-01, D-02).
>
> ***Response*** ***Contract***
>
> @dataclass
>
> class WindowDefinition:
>
> window_id: str \# "w01", "w02", ... pattern ^w\[0-9\]{2}\$ start_date:
> date
>
> end_date: date
>
> commits: int \# ≥ 1 strategy: str
>
> size_config: Optional\[Dict\[str, Any\]\]
>
> **JSON** **Schema:**
>
> {
>
> "type": "array", "items": {
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
> "strategy": {"type": "string"}, "size_config": {"type": "object"}
>
> } }
>
> }
>
> ***Error*** ***Codes***

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

> ***Example*** ***Payloads*** **Request:**
>
> {
>
> "metric_dataframe": {"repo_id": "abc...", "metrics": {...}},
> "strategy": "time",
>
> "size": 30 }
>
> **Response:**
>
> \[
>
> {"window_id": "w01", "start_date": "2025-01-01", "end_date":
> "2025-01-31", "commits": 45, "strategy": "time", "size_config":
> {"days": 30}},
>
> {"window_id": "w02", "start_date": "2025-02-01", "end_date":
> "2025-02-28", "commits": 38, "strategy": "time", "size_config":
> {"days": 30}},
>
> {"window_id": "w03", "start_date": "2025-03-01", "end_date":
> "2025-03-31", "commits": 52, "strategy": "time", "size_config":
> {"days": 30}}
>
> \]
>
> **SECTION** **8** **—** **DETECTOR** **INVOCATION** **CONTRACTS**
>
> **8.1** **INT-04:** **Detector** **Invocation**
>
> ***Request*** ***Contract***
>
> @dataclass
>
> class DetectionInput: metric_dataframe: MetricDataFrame windows:
> List\[WindowDefinition\]
>
> detector_config: Dict\[str, Dict\[str, Any\]\]
>
> enabled_detectors: List\[str\] \# Items from {D-01, D-02, D-03, "all"}
>
> **JSON** **Schema:**
>
> {
>
> "type": "object",
>
> "required": \["metric_dataframe", "windows", "enabled_detectors"\],
>
> "properties": {
>
> "metric_dataframe": {"type": "object"},
>
> "windows": {"type": "array", "items": {"type": "object"}},
> "detector_config": {
>
> "type": "object", "properties": {
>
> "D-01": {"type": "object"}, "D-02": {"type": "object"}, "D-03":
> {"type": "object"}
>
> } },

"enabled_detectors": {"type": "array", "items": {"enum": \["D-01",
"D-02", "D-03", "all"\]}}

} }

***Validation*** ***Rules***

> 1\. enabled_detectors must contain valid detector IDs or "all". If
> "all", expanded to \[D-01, D-02, D-03\].
>
> 2\. detector_config must contain configuration objects for each
> enabled detector.
>
> 3\. windows must be non-empty, ordered, non-overlapping.
>
> 4\. metric_dataframe must contain data for at least one metric.

**8.2** **D-01:** **Distributional** **Drift** **Detector** **Contract**

***Input*** ***Sub-contract***

@dataclass class D01Input:

> metric_values_window_a: List\[float\] metric_values_window_b:
> List\[float\] metric_id: str
>
> window_pair: Tuple\[str, str\]

config: Dict\[str, Any\] = field(default_factory=lambda: {"alpha": 0.05,
"psi_threshold": 0.25})

***Output*** ***Sub-contract***

@dataclass class D01Output:

> detected: bool
>
> ks_statistic: float \# \[0.0, 1.0\] ks_p_value: float \# \[0.0, 1.0\]
> psi_value: float \# ≥ 0.0

direction: str \# "mean_shift" \| "variance_collapse" \| "shape_change"

> severity: float \# \[0.0, 1.0\]; min(1.0, ks_statistic / 0.5)
> mean_shift: Optional\[float\]
>
> variance_ratio: Optional\[float\]
>
> sample_sizes: List\[int\] \# \[n_a, n_b\], each ≥ 10 window_pair:
> List\[str\]
>
> metric_id: str

**Validation:**

> sample_sizes each ≥ 10 (skip if not).
>
> alpha = 0.05 (frozen).
>
> psi_threshold = 0.25 (frozen).
>
> direction classified per TFS §5.1 logic.
>
> Severity computed per TFS §5.1 formula.

**8.3** **D-02:** **Correlation** **Breakdown** **Detector**
**Contract**

***Input*** ***Sub-contract***

@dataclass class D02Input:

> values_a: List\[float\] values_b: List\[float\] metric_a: str
> metric_b: str
>
> window_history: List\[WindowDefinition\]

config: Dict\[str, Any\] = field(default_factory=lambda:
{"correlation_threshold": 0.3})

***Output*** ***Sub-contract***

@dataclass class D02Output:

> detected: bool

breakdown_type: str \# "sudden_drop" \| "sign_reversal" \|
"gradual_erosion" \| "confidence_exclusion"

> pearson_trajectory: List\[float\] \# Per window, \[-1.0, 1.0\]
> spearman_trajectory: List\[float\] \# Per window, \[-1.0, 1.0\]
> window_pairs_flagged: List\[List\[str\]\]
>
> confidence_intervals: List\[List\[float\]\] \# \[\[lower, upper\],
> ...\] severity: float \# \[0.0, 1.0\]; min(1.0, \|delta_r\| / 0.3)
> metric_pair: List\[str\] \# \[M_i, M_j\], i \< j

**Validation:**

> Paired observations ≥ 10 per window (skip if not).
>
> correlation_threshold = 0.3 (frozen).
>
> Breakdown types classified per TFS §5.2 logic.
>
> Severity computed per TFS §5.2 formula.

**8.4** **D-03:** **Threshold** **Compression** **Detector**
**Contract**

***Input*** ***Sub-contract***

@dataclass class D03Input:

> metric_values: List\[float\] thresholds: List\[float\] metric_id: str
>
> window_id: str

config: Dict\[str, Any\] = field(default_factory=lambda: {"margin":
0.02, "bootstrap_iterations": 1000, "bootstrap_seed": 42})

***Output*** ***Sub-contract***

@dataclass class D03Output:

> detected: bool threshold: float margin: float compression_index: float
>
> excess_mass_z_score: float dip_test_statistic: float dip_test_p_value:
> float hypothesized_cause: str

"POLICY_MANDATE" \| "UNKNOWN" sample_size: int window_id: str metric_id:
str

> \# max(0.02\*T, 0.01\*range) \# \[0.0, 1.0\]

\# ≥ 0.0 \# ≥ 0.0

> \# \[0.0, 1.0\]
>
> \# "THRESHOLD_GAMING" \| "SLA_COMPLIANCE" \|

\# ≥ 20

**Validation:**

> sample_size ≥ 20 (skip if not).
>
> margin = max(0.02×T, 0.01×range) (frozen).
>
> z_score threshold = 1.645 (one-tailed, α=0.05) (frozen).
>
> bootstrap_iterations = 1000, bootstrap_seed = 42 (frozen).
>
> p_hat dominance threshold = 0.5 (frozen).
>
> p_0 sanity cap = 0.5 (frozen).

**8.5** **Detector** **Results** **Aggregation** **Combined**
**Response** **Contract:**

@dataclass

class DetectorResults:

d_01: Dict\[str, Dict\[str, D01Output\]\] \# metric_id -\>
window_pair_key -\> output

d_02: Dict\[str, Dict\[str, D02Output\]\] \# metric_pair_key -\>
window_pair_key -\> output

d_03: Dict\[str, Dict\[str, Dict\[str, D03Output\]\]\] \# metric_id -\>
threshold_key -\> window_id -\> output

**JSON** **Schema:**

{

> "type": "object",
>
> "required": \["detector_outputs"\], "properties": {
>
> "detector_outputs": { "type": "object", "properties": {
>
> "D-01": {"type": "object"}, "D-02": {"type": "object"}, "D-03":
> {"type": "object"}
>
> } }

} }

> ***Error*** ***Codes***

||
||
||
||
||
||
||

> **SECTION** **9** **—** **INTEGRITY** **SCORE** **CONTRACTS**
>
> **9.1** **INT-05:** **Score** **Calculation**
>
> ***Request*** ***Contract***
>
> @dataclass
>
> class ScoringInput: detector_results: DetectorResults
> metric_dataframe: MetricDataFrame windows: List\[WindowDefinition\]
>
> detector_weights: Dict\[str, float\] = field(default_factory=lambda:
> {"D-01": 0.40, "D-02": 0.35, "D-03": 0.25})

**JSON** **Schema:**

{

> "type": "object",
>
> "required": \["detector_results", "metric_dataframe", "windows"\],
> "properties": {
>
> "detector_results": {"type": "object"}, "metric_dataframe": {"type":
> "object"},
>
> "windows": {"type": "array", "items": {"type": "object"}},
> "detector_weights": {
>
> "type": "object", "properties": {
>
> "D-01": {"type": "number", "default": 0.40}, "D-02": {"type":
> "number", "default": 0.35}, "D-03": {"type": "number", "default":
> 0.25}
>
> } }

} }

***Validation*** ***Rules***

> 1\. detector_weights must contain keys for all enabled detectors. If
> sum ≠ 1.0, normalize proportionally.
>
> 2\. If detector skipped on metric, redistribute weight proportionally
> to other detectors for that metric.
>
> 3\. All severity values must be in \[0.0, 1.0\].
>
> 4\. If all metrics unavailable: raise ScoreError → abort.

***Response*** ***Contract***

@dataclass

class ScorePackage: integrity: IntegrityScore

> confidence: ConfidenceScore timestamp: datetime config_hash: str
> formula_version: str = "1.0.0"

@dataclass

class IntegrityScore:

> overall: float \# \[0.0, 1.0\]
>
> per_metric: Dict\[str, float\] \# metric_id -\> \[0.0, 1.0\]
> formula_version: str

@dataclass

class ConfidenceScore:

> overall: float \# \[0.0, 1.0\]

factors: Dict\[str, float\] \# sample_size, variance, missing_data,
window_balance, detector_success

> band: Optional\[str\] \# "high" \| "medium" \| "low" \| "critical"

**JSON** **Schema:**

{

> "type": "object",

"required": \["integrity", "confidence", "timestamp", "config_hash",
"formula_version"\],

> "properties": { "integrity": {
>
> "type": "object",
>
> "required": \["overall", "per_metric", "formula_version"\],
> "properties": {
>
> "overall": {"type": "number", "minimum": 0, "maximum": 1},
> "per_metric": {"type": "object", "additionalProperties": {"type":
>
> "number", "minimum": 0, "maximum": 1}}, "formula_version": {"type":
> "string"}
>
> } },
>
> "confidence": { "type": "object",
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
> } },
>
> "band": {"enum": \["high", "medium", "low", "critical"\]} }
>
> },
>
> "timestamp": {"type": "string", "format": "date-time"}, "config_hash":
> {"type": "string"},
>
> "formula_version": {"type": "string"} }
>
> }
>
> ***Error*** ***Codes***

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

> ***Example*** ***Payloads*** **Request:**
>
> {
>
> "detector_results": {"detector_outputs": {"D-01": {...}, "D-02":
> {...}, "D-03": {...}}},
>
> "metric_dataframe": {"repo_id": "abc...", "metrics": {...}},
> "windows": \[{"window_id": "w01", ...}, {"window_id": "w02", ...}\],
> "detector_weights": {"D-01": 0.40, "D-02": 0.35, "D-03": 0.25}
>
> }
>
> **Response:**
>
> {
>
> "integrity": { "overall": 0.72,
>
> "per_metric": {"M-01": 0.5725, "M-02": 1.0, "M-03": 0.85, "M-04":
> 0.92, "M-05": 0.78, "M-06": 0.88, "M-07": 0.95},
>
> "formula_version": "1.0.0" },
>
> "confidence": { "overall": 0.68,
>
> "factors": {"sample_size": 1.0, "variance": 0.8, "missing_data": 0.9,
> "window_balance": 0.85, "detector_success": 1.0},
>
> "band": "medium" },
>
> "timestamp": "2026-06-07T10:31:00Z", "config_hash": "a1b2c3d4...",
> "formula_version": "1.0.0"
>
> }
>
> **SECTION** **10** **—** **EVIDENCE** **CONTRACTS**
>
> **10.1** **INT-06:** **Evidence** **Generation**
>
> ***Request*** ***Contract***
>
> @dataclass
>
> class EvidenceInput:
>
> repository_context: RepositoryContext metric_dataframe:
> MetricDataFrame windows: List\[WindowDefinition\]
>
> detector_results: DetectorResults score_package: ScorePackage
> configuration: ConfigurationObject

***Response*** ***Contract***

@dataclass

class EvidencePackage: provenance: Provenance

> windows: List\[WindowDefinition\]
>
> metrics: Dict\[str, Any\] \# Summary of metric data detector_outputs:
> DetectorResults
>
> scores: ScorePackage warnings: List\[WarningItem\]

@dataclass

class Provenance: miie_version: str config_hash: str timestamp: str
seed: Optional\[int\]

> platform: Optional\[str\] python_version: Optional\[str\]
> dependency_hash: Optional\[str\]

@dataclass

class WarningItem: stage: str message: str

> metric_id: Optional\[str\] detector_id: Optional\[str\]

**JSON** **Schema:**

{

> "type": "object",

"required": \["provenance", "windows", "metrics", "detector_outputs",
"scores"\],

> "properties": { "provenance": {
>
> "type": "object",
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
> "windows": {"type": "array", "items": {"type": "object"}}, "metrics":
> {"type": "object"},
>
> "detector_outputs": {"type": "object"}, "scores": {"type": "object"},
> "warnings": {
>
> "type": "array", "items": {
>
> "type": "object", "properties": {
>
> "stage": {"type": "string"}, "message": {"type": "string"},
>
> "metric_id": {"type": "string"}, "detector_id": {"type": "string"}
>
> } }
>
> } }
>
> }
>
> ***Validation*** ***Rules***
>
> 1\. All nested objects must match their respective schemas.
>
> 2\. Every positive detector flag must have corresponding statistical
> evidence in detector_outputs.
>
> 3\. provenance.timestamp must be ISO 8601 UTC.
>
> 4\. warnings array captures all non-fatal issues from pipeline
> execution.
>
> ***Error*** ***Codes***

||
||
||
||
||

**SECTION** **11** **—** **EXPLANATION** **CONTRACTS**

**11.1** **INT-07:** **Explanation** **Generation**

***Request*** ***Contract***

@dataclass

class ExplanationInput: evidence_package: EvidencePackage score_package:
ScorePackage metric_filter: Optional\[str\] = None

all

detector_filter: Optional\[str\] = None all

\# Specific metric_id or None for

> \# Specific detector_id or None for

**JSON** **Schema:**

{

> "type": "object",
>
> "required": \["evidence_package", "score_package"\], "properties": {
>
> "evidence_package": {"type": "object"}, "score_package": {"type":
> "object"},

"metric_filter": {"type": "string", "enum": \["M-01", "M-02", "M-03",
"M-04", "M-05", "M-06", "M-07"\]},

> "detector_filter": {"type": "string", "enum": \["D-01", "D-02",
> "D-03"\]} }

}

***Response*** ***Contract***

@dataclass

class ExplanationReport:

> explanations: List\[ExplanationItem\] summary: str
>
> recommendations: List\[str\] disclaimer: Optional\[str\]

@dataclass

class ExplanationItem: metric_id: str detector_id: str narrative: str
severity: str evidence_refs: List\[str\]

> confidence: Optional\[str\] rule_fired: Optional\[str\]

\# "mild" \| "moderate" \| "severe"

\# Dot-delimited paths into EvidencePackage \# "high" \| "medium" \|
"low"

**JSON** **Schema:**

{

> "type": "object",
>
> "required": \["explanations", "summary", "recommendations"\],
> "properties": {
>
> "explanations": { "type": "array", "items": {
>
> "type": "object",

"required": \["metric_id", "detector_id", "narrative", "severity",
"evidence_refs"\],

> "properties": {
>
> "metric_id": {"type": "string"}, "detector_id": {"type": "string"},
> "narrative": {"type": "string"},
>
> "severity": {"enum": \["mild", "moderate", "severe"\]},
> "evidence_refs": {"type": "array", "items": {"type": "string"}},
> "confidence": {"enum": \["high", "medium", "low"\]}, "rule_fired":
> {"type": "string"}
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
> ***Validation*** ***Rules***
>
> 1\. Templates must exist in src/miie/reporting/templates/.
>
> 2\. Every explanation must cite at least one evidence_ref.
>
> 3\. severity must match detector output severity.
>
> 4\. narrative must be non-empty string.
>
> 5\. Templates rendered in detector priority order: D-01, D-02, D-03.
>
> ***Error*** ***Codes***

||
||
||
||
||
||

**SECTION** **12** **—** **BENCHMARK** **CONTRACTS**

**12.1** **INT-09:** **Benchmark** **Execution**

***Request*** ***Contract***

@dataclass

class BenchmarkInput: suite_id: str detector_ids: List\[str\] config:
Dict\[str, Any\] seed: int = 42

**JSON** **Schema:**

{

> "type": "object", "required": \["suite_id"\], "properties": {
>
> "suite_id": {"type": "string"},

"detector_ids": {"type": "array", "items": {"enum": \["D-01", "D-02",
"D-03", "all"\]}},

> "config": {"type": "object"},
>
> "seed": {"type": "integer", "default": 42} }

}

***Validation*** ***Rules***

> 1\. suite_id must match directory name in ~/.miie/benchmarks/.
>
> 2\. detector_ids must be valid and compatible with suite schema
> version.
>
> 3\. seed must be integer (default 42).
>
> 4\. Suite manifest must exist and be valid.

***Response*** ***Contract***

@dataclass

class BenchmarkRun: run_id: str suite_id: str detector_id: str
detector_version: str seed: int started_at: str completed_at: str

predictions: Dict\[str, Dict\[str, Any\]\] \# dataset_id -\> metric_id
-\> context -\> prediction

> timing: Dict\[str, float\] \# dataset_id -\> seconds environment:
> EnvironmentMetadata

@dataclass

class EnvironmentMetadata: miie_version: str python_version: str
platform: str

> dependency_hash: Optional\[str\]
>
> **JSON** **Schema:**
>
> {
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
> "detector_id": {"type": "string"}, "detector_version": {"type":
> "string"}, "seed": {"type": "integer"},
>
> "started_at": {"type": "string", "format": "date-time"},
> "completed_at": {"type": "string", "format": "date-time"},
> "predictions": {"type": "object"},
>
> "timing": {"type": "object", "additionalProperties": {"type":
> "number"}}, "environment": {
>
> "type": "object",
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
> ***Error*** ***Codes***

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

> **12.2** **INT-10:** **Evaluation**
>
> ***Request*** ***Contract***
>
> @dataclass
>
> class EvaluationInput: benchmark_run: BenchmarkRun ground_truth:
> GroundTruth
>
> ***Response*** ***Contract***
>
> @dataclass
>
> class EvaluationResult: suite_id: str detector_id: str
> detector_version: str evaluation_timestamp: str random_seed: int
>
> metrics: EvaluationMetrics confusion_matrix: ConfusionMatrix
>
> per_dataset_results: Optional\[List\[PerDatasetResult\]\]
>
> @dataclass
>
> class EvaluationMetrics:
>
> accuracy: float \# \[0.0, 1.0\] precision: float \# \[0.0, 1.0\]
> recall: float \# \[0.0, 1.0\] f1: float \# \[0.0, 1.0\] auc_roc: float
> \# \[0.0, 1.0\] auc_pr: float \# \[0.0, 1.0\] fpr: float \# \[0.0,
> 1.0\] fnr: float \# \[0.0, 1.0\]
>
> @dataclass
>
> class ConfusionMatrix: tp: int
>
> fp: int tn: int fn: int
>
> @dataclass
>
> class PerDatasetResult: repo_id: str predicted: bool actual: bool
> correct: bool
>
> **Validation** **Rules:**
>
> 1\. All metrics in \[0.0, 1.0\].
>
> 2\. TP + FP + TN + FN = total instances.
>
> 3\. Division by zero in precision/recall/F1 returns 0.0 with warning.
>
> 4\. AUC-ROC ≥ 0.5 sanity check (warning if below, not error).
>
> ***Error*** ***Codes***

||
||
||
||
||

> **SECTION** **13** **—** **GROUND** **TRUTH** **CONTRACTS**
>
> **13.1** **INT-12:** **Ground** **Truth** **Management**
>
> ***Label*** ***Submission*** ***Contract***
>
> @dataclass
>
> class GroundTruthInput: dataset_id: str
>
> annotations: List\[Annotation\] suite_id: str

**JSON** **Schema:**

{

> "type": "object",
>
> "required": \["dataset_id", "annotations", "suite_id"\], "properties":
> {
>
> "dataset_id": {"type": "string", "pattern": "^repo\_\[0-9\]{3}\$"},
> "annotations": {"type": "array", "items": {"\$ref": "#/Annotation"}},
> "suite_id": {"type": "string"}

} }

***Annotation*** ***Sub-contract***

@dataclass

class Annotation: annotation_id: str metric_id: str window_id:
Optional\[str\]

> window_pair: Optional\[List\[str\]\] metric_pair:
> Optional\[List\[str\]\] threshold: Optional\[float\]
>
> event_type: str \# "MDE-01" \| "MDE-02" \| "MDE-03" \| "MDE-04" label:
> bool
>
> severity: Optional\[str\] \# "mild" \| "moderate" \| "severe"
> evidence: EvidenceBlock
>
> annotator_id: str timestamp: str

@dataclass

class EvidenceBlock: statistical: Dict\[str, Any\]

> visual: List\[str\] \# File paths rationale: str

***Conflict*** ***Resolution*** ***Contract***

@dataclass

class ConflictResolutionInput: annotation_a: Annotation annotation_b:
Annotation adjudicator_id: str

@dataclass

class ConflictResolutionOutput: resolved_label: bool resolved_severity:
Optional\[str\] adjudicator_rationale: str adjudicator_id: str

> timestamp: str

***Validation*** ***Rules***

> 1\. Positive labels (label=true) must have evidence block with
> statistical and rationale.
>
> 2\. event_type must match context: MDE-01 requires window_pair; MDE-02
> requires metric_pair and window_pair; MDE-03 requires threshold and
> window_id; MDE-04 has no additional context.
>
> 3\. Cohen's Kappa between annotators must be ≥ 0.65 (dataset accepted)
> or ≥ 0.80 (auto-approved).
>
> 4\. Inter-rater agreement computed on binary labels per dataset.
>
> ***Error*** ***Codes***

||
||
||
||
||
||

> **SECTION** **14** **—** **EVALUATION** **CONTRACTS**
>
> **14.1** **Precision** **Evaluation** **Contract**
>
> **Definition:** Proportion of positive predictions that are correct.
>
> **Formula:** TP / (TP + FP) if (TP + FP) \> 0, else 0.0.
>
> **Target:** ≥ 0.80 (B-01), ≥ 0.75 (B-02), ≥ 0.85 (B-03).
>
> **Validation:** Result in \[0.0, 1.0\].

**14.2** **Recall** **Evaluation** **Contract**

> **Definition:** Proportion of actual positives correctly identified.
>
> **Formula:** TP / (TP + FN) if (TP + FN) \> 0, else 0.0.
>
> **Target:** ≥ 0.75 (B-01), ≥ 0.70 (B-02), ≥ 0.80 (B-03).
>
> **Validation:** Result in \[0.0, 1.0\].

**14.3** **F1** **Evaluation** **Contract**

> **Definition:** Harmonic mean of precision and recall.
>
> **Formula:** 2 \* (precision \* recall) / (precision + recall) if
> (precision + recall) \> 0, else 0.0.
>
> **Validation:** Result in \[0.0, 1.0\].

**14.4** **AUC** **Evaluation** **Contract**

> **AUC-ROC:** Area under ROC curve (TPR vs FPR). Computed via
> trapezoidal rule.
>
> **AUC-PR:** Area under precision-recall curve. Computed via
> trapezoidal rule.
>
> **Target:** ≥ 0.85 for all detectors.
>
> **Validation:** Result in \[0.0, 1.0\]; sanity check ≥ 0.5.

**14.5** **Aggregate** **Evaluation** **Contract**

> **Per-dataset:** Macro-average across all metric-contexts in dataset.
>
> **Per-suite:** Macro-average across all datasets.
>
> **Overall:** Weighted average by dataset size (number of evaluation
> instances).
>
> **Validation:** All aggregation levels must produce values in \[0.0,
> 1.0\].

**SECTION** **15** **—** **REPORT** **GENERATION** **CONTRACTS**

**15.1** **INT-08:** **Report** **Generation**

***Request*** ***Contract***

@dataclass

class ReportInput: analysis_result: AnalysisResult

> output_formats: List\[str\] \# \["json", "md", "csv"\] output_dir:
> Path
>
> ***Response*** ***Contract***
>
> @dataclass
>
> class ReportOutput: file_paths: Dict\[str, Path\] manifest_path: Path
> checksums: Dict\[str, str\]

\# format -\> path

\# filename -\> SHA-256

> ***Validation*** ***Rules***
>
> 1\. output_formats must contain valid format strings.
>
> 2\. output_dir must be writable.
>
> 3\. Disk space check before write.
>
> 4\. All files written atomically (temp + rename).
>
> 5\. manifest.json written last with checksums of all other files.
>
> ***Error*** ***Codes***

||
||
||
||
||
||

**SECTION** **16** **—** **EXPORT** **CONTRACTS**

**16.1** **JSON** **Export** **Contract**

> **Schema:** Validated against results.json schema (BSD-Engineering
> §20.1).
>
> **Encoding:** UTF-8, no BOM, sorted keys, 2-space indent.
>
> **Null** **handling:** Explicit null for missing values.
>
> **Numeric** **precision:** 6 decimal places minimum.
>
> **File** **naming:** results.json.

**16.2** **CSV** **Export** **Contract**

> **Format:** RFC 4180, UTF-8, comma-delimited, quoted strings.
>
> **Header:** Mandatory; column names in snake_case.
>
> **Column** **order:** metric_id, window_id, value, integrity_score,
> confidence_score, drift_detected, correlation_breakdown,
> threshold_compression.
>
> **Null** **handling:** Empty string for null values.
>
> **Boolean** **handling:** true/false lowercase strings.
>
> **File** **naming:** metrics.csv.

**16.3** **Markdown** **Export** **Contract**

> **Format:** GitHub-Flavored Markdown.
>
> **Sections:** Frozen order per TRD §20.3: 1. Header
>
> 2\. Executive Summary
>
> 3\. Per-Metric Analysis
>
> 4\. Evidence Details
>
> 5\. Recommendations
>
> 6\. Disclaimer
>
> 7\. Appendix
>
> **File** **naming:** report.md.

**16.4** **Compatibility** **Rules**

> **V1.0** **→** **V1.1:** V1.0 consumers can read V1.1 JSON (additive
> fields ignored). V1.1 producers must accept V1.0 requests.
>
> **CSV** **compatibility:** Column order frozen. New columns added at
> end in minor versions.
>
> **Markdown** **compatibility:** Section order frozen. New sections
> added at end in minor versions.
>
> **SECTION** **17** **—** **CLI** **CONTRACTS**
>
> **17.1** **Global** **Options** **(All** **Commands)**

||
||
||
||
||
||
||
||

> **17.2** **CLI-01:** **miie** **ingest**
>
> **Purpose:** Ingest and validate a repository without running
> analysis.

||
||
||
||
||
||

> **Output:** RepositoryContext printed as JSON to stdout. **Exit**
> **Codes:** 0 (success), 2 (system error), 3 (invalid input).
>
> **Example:**
>
> miie ingest --repo https://github.com/org/repo.git --shallow 100
>
> **17.3** **CLI-02:** **miie** **analyze** **Purpose:** Full repository
> analysis pipeline.

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

> **Output:** Files in --output directory. **Exit** **Codes:** 0
> (IS=1.0), 1 (IS\<1.0), 2 (error), 3 (invalid input).
>
> **Example:**
>
> miie analyze --repo ./my-repo --since 2025-01-01 --metrics M-01,M-02
> --window-strategy time --window-size 90 -o ./output
>
> **17.4** **CLI-03:** **miie** **detect**
>
> **Purpose:** Run detectors on pre-extracted metrics.

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

> **Exit** **Codes:** 0 (success), 2 (error), 3 (invalid input).
>
> **17.5** **CLI-04:** **miie** **benchmark** **Purpose:** Run benchmark
> suite against detectors.

||
||
||
||
||
||
||
||

> **Exit** **Codes:** 0 (success), 4 (benchmark failure).
>
> **Example:**
>
> miie benchmark --suite metric-drift-v1 --detectors D-01 --seed 42
>
> **17.6** **CLI-05:** **miie** **evaluate**
>
> **Purpose:** Evaluate benchmark run against ground truth.

||
||
||
||
||
||

> **Exit** **Codes:** 0 (success), 2 (error), 3 (invalid input).
>
> **17.7** **CLI-06:** **miie** **explain**
>
> **Purpose:** Generate explanations from existing analysis.

||
||
||
||
||
||
||

> **Exit** **Codes:** 0 (success), 3 (invalid input).
>
> **17.8** **CLI-07:** **miie** **export**
>
> **Purpose:** Re-export results in specified formats.

||
||
||
||
||
||
||

> **Exit** **Codes:** 0 (success), 3 (invalid input).
>
> **17.9** **CLI-08:** **miie** **generate** **Purpose:** Generate
> synthetic benchmark datasets.

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

> **Exit** **Codes:** 0 (success), 2 (error), 3 (invalid input).
>
> **17.10** **Exit** **Code** **Summary**

||
||
||
||
||
||
||
||

> **SECTION** **18** **—** **INTERNAL** **SERVICE** **CONTRACTS**
>
> **18.1** **Repository** **Engine** **Contract** **(M-01)**
>
> class RepositoryIngestionEngine:
>
> def ingest(self, request: IngestionInput) -\>
> Result\[RepositoryContext, IngestionError\]
>
> def validate(self, path: Path) -\> Result\[RepositoryContext,
> ValidationError\] def clone(self, url: str, cache_dir: Path, depth:
> Optional\[int\]) -\>
>
> Result\[Path, CloneError\]
>
> def extract_metadata(self, repo_path: Path) -\>
> Result\[RepositoryMetadata, MetadataError\]
>
> **18.2** **Metric** **Engine** **Contract** **(M-02)**
>
> class MetricExtractionEngine:
>
> def extract(self, request: ExtractionInput) -\>
> Result\[MetricDataFrame, ExtractionError\]

def extract_coverage(self, repo: RepositoryContext, since: datetime,
until: datetime) -\> Result\[Series, MetricError\]

def extract_commit_frequency(self, repo: RepositoryContext, since:
datetime, until: datetime, exclude_bots: bool) -\> Result\[Series,
MetricError\]

\# ... extract_review_participation, extract_review_latency,
extract_issue_resolution, extract_churn, extract_complexity

**18.3** **Window** **Engine** **Contract** **(M-03)**

class WindowSegmentationEngine:

def segment(self, request: SegmentationInput) -\>
Result\[List\[WindowDefinition\], SegmentationError\]

def segment_by_time(self, df: MetricDataFrame, days: int) -\>
Result\[List\[WindowDefinition\], SegmentationError\]

def segment_by_commit(self, df: MetricDataFrame, commits: int) -\>
Result\[List\[WindowDefinition\], SegmentationError\]

def segment_by_release(self, df: MetricDataFrame, tag_pattern: str) -\>
Result\[List\[WindowDefinition\], SegmentationError\]

def segment_custom(self, df: MetricDataFrame, boundaries:
List\[Tuple\[datetime, datetime\]\]) -\>
Result\[List\[WindowDefinition\], SegmentationError\]

**18.4** **Detector** **Engine** **Contract** **(M-05)**

class DetectorEngine:

def detect(self, request: DetectionInput) -\> Result\[DetectorResults,
DetectionError\]

def detect_drift(self, metric_values_a: List\[float\], metric_values_b:
List\[float\], config: Dict) -\> Result\[D01Output, DriftError\]

def detect_breakdown(self, values_a: List\[float\], values_b:
List\[float\], windows: List\[WindowDefinition\], config: Dict) -\>
Result\[D02Output, BreakdownError\]

def detect_compression(self, metric_values: List\[float\], thresholds:
List\[float\], window_id: str, config: Dict) -\> Result\[D03Output,
CompressionError\]

**18.5** **Scoring** **Engine** **Contract** **(M-08)**

class ScoringEngine:

def compute_integrity_score(self, request: ScoringInput) -\>
Result\[IntegrityScore, ScoreError\]

def compute_confidence_score(self, request: ScoringInput) -\>
Result\[ConfidenceScore, ScoreError\]

def normalize_weights(self, weights: Dict\[str, float\], enabled:
List\[str\]) -\> Result\[Dict\[str, float\], WeightError\]

**18.6** **Evidence** **Engine** **Contract** **(EVA)**

class EvidenceAggregator:

def aggregate(self, request: EvidenceInput) -\> Result\[EvidencePackage,
EvidenceError\]

def validate_completeness(self, package: EvidencePackage) -\>
Result\[bool, ValidationError\]

def add_provenance(self, package: EvidencePackage, config:
ConfigurationObject) -\> EvidencePackage

**18.7** **Explanation** **Engine** **Contract** **(M-09)**

class ExplanationGenerator:

> def generate(self, request: ExplanationInput) -\>
> Result\[ExplanationReport,

ExplanationError\]

def render_template(self, template_name: str, context: Dict) -\>
Result\[str, TemplateError\]

def filter_explanations(self, report: ExplanationReport, metric:
Optional\[str\], detector: Optional\[str\]) -\> ExplanationReport

**18.8** **Benchmark** **Engine** **Contract** **(M-06)**

class BenchmarkRunner:

def run_benchmark(self, request: BenchmarkInput) -\>
Result\[BenchmarkRun, BenchmarkError\]

> def load_suite(self, suite_id: str) -\> Result\[Suite, SuiteError\]

def validate_detector_compatibility(self, detector_id: str, suite:
Suite) -\> Result\[bool, CompatibilityError\]

def run_dataset(self, dataset: Dataset, detector: Detector, config:
Dict) -\> Result\[DatasetPredictions, DatasetError\]

**18.9** **Evaluation** **Engine** **Contract** **(M-07)**

class EvaluationEngine:

def evaluate(self, request: EvaluationInput) -\>
Result\[EvaluationResult, EvaluationError\]

def compute_confusion_matrix(self, predictions: List\[bool\], labels:
List\[bool\]) -\> ConfusionMatrix

> def compute_metrics(self, cm: ConfusionMatrix) -\> EvaluationMetrics
> def aggregate_per_dataset(self, results: List\[PerDatasetResult\]) -\>

EvaluationMetrics

**18.10** **Report** **Engine** **Contract** **(M-09)**

class ReportGenerator:

def generate(self, request: ReportInput) -\> Result\[ReportOutput,
ReportError\]

def render_json(self, result: AnalysisResult) -\> Result\[str,
SerializationError\]

def render_markdown(self, result: AnalysisResult) -\> Result\[str,
TemplateError\]

> def render_csv(self, result: AnalysisResult) -\> Result\[str,
> CSVError\] def write_manifest(self, output_dir: Path, checksums:
> Dict\[str, str\]) -\>

Result\[Path, IOError\]

**SECTION** **19** **—** **ERROR** **CONTRACT** **FRAMEWORK**

**19.1** **Unified** **Error** **Model**

@dataclass

class ErrorContract:

> error_id: str \# Uppercase with hyphens: INVALID-REPO severity: str \#
> "fatal" \| "error" \| "warning" \| "info"

category: str \# "input" \| "system" \| "statistical" \| "schema" \|
"benchmark" \| "network"

> stage: Optional\[str\] \# Pipeline stage where error occurred message:
> str \# Human-readable description suggestion: str \# Actionable fix

context: Dict\[str, Any\] \# Additional context (metric_id, detector_id,
path, etc.)

> traceback: Optional\[str\] \# Full traceback if --verbose
>
> **19.2** **Error** **Severity** **Levels**

||
||
||
||
||
||
||

> **19.3** **Error** **Categories**

||
||
||
||
||
||
||
||
||

> **19.4** **Recovery** **Strategy** **Matrix**

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

> **19.5** **Error** **Response** **Examples** **CLI** **Error:**
>
> \[INVALID-REPO\] Cannot access repository at /nonexistent. Suggestion:
> verify path or URL.
>
> **API** **Error** **(RFC** **7807):**

{

> "type": "https://miie.dev/errors/invalid-repo", "title": "Invalid
> Repository",
>
> "status": 400,
>
> "detail": "The provided path /nonexistent is not a valid Git
> repository.", "instance": "/v1/analyze"

}

**Internal** **Error** **(logged):**

2026-06-07T10:31:00Z \[ERROR\] detection: DETECTOR-CRASH on D-03/M-01:
ValueError: math domain error

Traceback (most recent call last):

> File "src/miie/processing/detection.py", line 245, in
> detect_compression ...

**SECTION** **20** **—** **VALIDATION** **CONTRACT** **FRAMEWORK**

**20.1** **Input** **Validation**

> **Schema** **validation:** All inputs validated against JSON Schema
> before processing.
>
> **Unknown** **fields:** Rejected in strict mode.
>
> **Missing** **required** **fields:** Raise ValidationError with field
> name.
>
> **Type** **coercion:** Disabled. Wrong type → ValidationError.
>
> **Range** **validation:** Numeric values checked against min/max.
>
> **Pattern** **validation:** Strings checked against regex patterns.
>
> **Enum** **validation:** Strings checked against allowed values.
>
> **Path** **validation:** File paths resolved via
> pathlib.Path.resolve() to prevent traversal.
>
> **URL** **validation:** Schemes restricted to https:// and ssh://.

**20.2** **Output** **Validation**

> **Schema** **validation:** All outputs validated against JSON Schema
> before writing.
>
> **Determinism** **check:** Collections sorted before serialization.
>
> **Checksum** **computation:** SHA-256 computed for critical artifacts.
>
> **Manifest** **validation:** Manifest includes checksums of all output
> files.
>
> **File** **integrity:** Optional post-write verification.

**20.3** **Schema** **Validation**

> **Validator:** JSON Schema draft-07 compliant (e.g., jsonschema
> library).
>
> **Strict** **mode:** additionalProperties: false unless explicitly
> extensible.
>
> **Format** **checking:** date-time, date, uuid, uri formats validated.
>
> **Custom** **validators:** Metric ID validator, detector ID validator,
> window ID pattern validator.

**20.4** **Manifest** **Validation**

> **Required** **fields:** miie_version, git_commit, python_version,
> dependency_hash, config_hash, seed, timestamp, platform.
>
> **Checksum** **verification:** Optional but recommended.
>
> **Dependency** **hash** **check:** Warning if current environment
> differs from manifest.
>
> **Config** **hash** **check:** Used for reproducibility verification.

**20.5** **Benchmark** **Validation**

> **Dataset** **validation:** metrics.json, windows.json, metadata.json
> validated against BSD schemas.
>
> **Ground** **truth** **validation:** ground_truth.json validated
> against BSD Ground Truth Schema.
>
> **Suite** **manifest** **validation:** manifest.json validated against
> BSD Metadata Schema.
>
> **Checksum** **validation:** Dataset checksums verified on load.
>
> **Leakage** **detection:** Benchmark runner enforces no ground truth
> access.

**20.6** **Evidence** **Validation**

> **Completeness:** Every positive label has evidence.
>
> **Schema:** annotations.json validated against BSD Annotation Schema.
>
> **Provenance:** Every evidence item has annotator_id, timestamp,
> annotation_id.
>
> **Visual** **evidence:** Referenced files must exist in evidence/
> directory.

**20.7** **Report** **Validation**

> **JSON** **report:** Validated against results.json schema.
>
> **CSV** **report:** Header row matches schema; row count consistent.
>
> **Markdown** **report:** Non-empty; all required sections present.
>
> **Template** **validation:** All Jinja2 templates render without
> error.

**SECTION** **21** **—** **CONTRACT** **VERSIONING** **STRATEGY**

**21.1** **Major** **Versions**

> **Bump** **rule:** Breaking changes to contract interface (new
> required fields, removed fields,
>
> changed types, new error codes replacing old meanings).
>
> **Impact:** Consumers must update to new major version.
>
> **Example:** v1.0.0 → v2.0.0: Removed M-07 metric; changed
> ScorePackage structure.

**21.2** **Minor** **Versions**

> **Bump** **rule:** Additive non-breaking changes (new optional fields,
> new enum values, new endpoints, new CLI flags).
>
> **Impact:** Backward-compatible. v1.0.0 consumers work with v1.1.0
> producers.
>
> **Example:** v1.0.0 → v1.1.0: Added run_metadata.memory_peak_mb to
> AnalysisResult.

**21.3** **Patch** **Versions**

> **Bump** **rule:** Documentation fixes, description updates, typo
> corrections. No contract changes.
>
> **Impact:** No functional change.
>
> **Example:** v1.0.0 → v1.0.1: Fixed schema description string.

**21.4** **Deprecation** **Policy**

> **Deprecated** **fields:** Marked with deprecated: true in schema.
>
> **Support** **period:** Deprecated fields supported for 1 major
> version (minimum 12 months).
>
> **Sunset** **header:** API responses include Sunset: \<date\> header
> for deprecated endpoints.
>
> **Migration** **guide:** Major version bumps include migration guide
> with before/after examples.

**21.5** **Compatibility** **Policy**

> **Request** **compatibility:** Old clients → new servers: Must succeed
> if request valid per old schema.
>
> **Response** **compatibility:** New servers → old clients: Must not
> include new required fields.
>
> **CLI** **compatibility:** Old scripts → new CLI: Must work with same
> arguments and exit codes.
>
> **Benchmark** **compatibility:** Detector v1.0.0 must run on benchmark
> v1.1.0 (if backward-compatible).

**21.6** **Migration** **Policy**

> **Automated** **migration:** Where possible, provide scripts to
> convert old artifacts to new schema.
>
> **Manual** **migration:** Document all breaking changes with explicit
> transformation steps.
>
> **Community** **feedback:** 30-day comment period before major version
> finalization.

**SECTION** **22** **—** **SECURITY** **CONTRACTS**

**22.1** **Input** **Sanitization**

> **Path** **sanitization:** All paths resolved via
> pathlib.Path.resolve() to prevent directory traversal (../ attacks).
>
> **URL** **sanitization:** Schemes restricted to https:// and ssh://.
> No file://, javascript://, or data URIs.
>
> **JSON/YAML** **sanitization:** Safe loaders only. No
> yaml.load(unsafe). No arbitrary code execution.
>
> **Metric** **value** **sanitization:** Non-numeric values coerced to
> null with warning. No eval() or exec() on metric values.

**22.2** **Path** **Validation**

> **Repository** **path:** Must exist (local) or be valid URL (remote).
> No traversal outside intended directories.
>
> **Output** **path:** Must be writable. No writing to system
> directories.
>
> **Cache** **path:** Created with 0o700 permissions. No world-readable
> cache.
>
> **Benchmark** **path:** Read-only during detection. Detectors cannot
> write outside dataset directory.

**22.3** **File** **Validation**

> **Coverage** **artifacts:** XML structure validated before parsing.
> File size \< 1GB.
>
> **PR/issue** **exports:** JSON/CSV validated against expected schema.
> Unknown fields rejected.
>
> **Config** **files:** Strict schema validation. Unknown fields
> rejected.
>
> **Benchmark** **datasets:** Checksum verification on load.

**22.4** **Artifact** **Verification**

> **Checksums:** SHA-256 computed for all critical artifacts.
>
> **Manifest** **verification:** manifest.json includes checksums of
> output files.
>
> **Ground** **truth** **verification:** ground_truth.json includes
> checksum of content.
>
> **Verification** **function:** hmac.compare_digest() for timing-safe
> comparison.

**22.5** **Checksum** **Validation** **Algorithm:** SHA-256.

> **Coverage:** results.json, evidence.json, metrics.csv,
> benchmark_run.json, ground_truth.json.
>
> **Optional:** Verification on load enabled via --verify-checksums flag
> (V1.1).
>
> **Mandatory:** Verification in benchmark runner before evaluation.
>
> **22.6** **Execution** **Safety**
>
> **No** **dynamic** **code** **execution:** No eval(), exec(), or
> compile() on user input.
>
> **Git** **subprocess:** Arguments passed as list (no shell=True).
> Sanitized via regex.
>
> **Static** **analysis** **tools:** Run in subprocess isolation with
> timeout (60s).
>
> **No** **network** **during** **analysis:** After initial clone, all
> processing offline.
>
> **Detector** **sandboxing:** Benchmark runner prevents filesystem
> access outside dataset directory.
>
> **SECTION** **23** **—** **PERFORMANCE** **CONTRACTS**
>
> **23.1** **Expected** **Response** **Times**

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

> **23.2** **Maximum** **Payload** **Sizes**

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

> **23.3** **Memory** **Constraints**

||
||
||
||
||
||
||

> **23.4** **Runtime** **Constraints**

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

> **23.5** **Timeout** **Rules**
>
> **Default** **timeout:** 10 minutes for repository analysis; 10
> minutes for benchmark execution.
>
> **Configurable:** --timeout flag (seconds) for future versions (V1.1).
>
> **Timeout** **action:** Abort pipeline, save partial results, return
> exit code 2.
>
> **Detector** **timeout:** Individual detectors have no separate
> timeout (enforced by pipeline timeout).
>
> **23.6** **Benchmark** **Execution** **Limits**
>
> **Max** **datasets** **per** **suite:** 100 (process sequentially).
>
> **Max** **parallel** **workers:** min(4, cpu_count()) for benchmark
> runner only.
>
> **Max** **detector** **runtime** **per** **dataset:** 60 seconds (skip
> if exceeded).
>
> **Max** **total** **benchmark** **runtime:** 10 minutes per suite.
>
> **SECTION** **24** **—** **OBSERVABILITY** **CONTRACTS**
>
> **24.1** **Logging** **Contracts**

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

> **24.2** **Trace** **Contracts**
>
> **Execution** **trace:** Embedded in evidence.json as
> provenance.execution_trace: ordered list of stages with timestamps and
> durations.
>
> **Benchmark** **trace:** benchmark_run.json includes timing object
> with per-dataset durations.
>
> **API** **trace:** state.json history array records all state
> transitions with timestamps.
>
> **Trace** **format:** JSON array of objects: {"stage": "detect",
> "timestamp": "...", "duration_ms": 450, "progress": 0.45}.
>
> **24.3** **Audit** **Contracts**
>
> **Manifest** **audit:** Every run produces manifest.json with full
> provenance.
>
> **Benchmark** **audit:** Every benchmark run produces
> run_manifest.json with environment info.
>
> **Config** **audit:** All configuration changes logged in state.json
> history.
>
> **Detector** **skip** **audit:** Every detector skip logged with
> metric, window, reason.
>
> **Ground** **truth** **audit:** Every label includes annotator_id,
> timestamp, modification_history, checksum.
>
> **24.4** **Execution** **Metadata** **Contracts**
>
> **Run** **metadata:** run_metrics.json includes duration_seconds,
> memory_peak_mb, cpu_time_seconds, stage_timings.
>
> **Benchmark** **metadata:** benchmark_run.json includes environment
> block with miie_version, python_version, platform, dependency_hash.
>
> **Job** **metadata:** JobManifest includes job_type, created_at,
> status, progress, current_stage.
>
> **24.5** **Diagnostic** **Telemetry**
>
> **Error** **telemetry:** Error code, stage, metric/detector context,
> traceback (if verbose).
>
> **Performance** **telemetry:** Stage durations, detector execution
> times, memory peaks.
>
> **Validation** **telemetry:** Schema validation failures with field
> names and expected vs actual types.
>
> **No** **external** **telemetry:** No data transmitted to external
> services. All telemetry is file-based.
>
> **SECTION** **25** **—** **TRACEABILITY** **MATRIX**
>
> **25.1** **Contract-to-Source** **Traceability**

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

> **25.2** **Requirement** **Coverage** **Verification**
>
> **PRD** **§7** **(In** **Scope):** All 18 interfaces and 8 CLI
> commands cover repository analysis, metric extraction, detection,
> scoring, evidence, explanation, and reporting.
>
> **PRD** **§9** **(Version** **1** **Freeze):** All 5 frozen workflows
> (WF-01–WF-05) plus maintainer workflows (WF-06–WF-07) have
> corresponding INT and CLI contracts.
>
> **TFS** **§2** **(Metric** **Freeze):** M-01–M-07 contracts frozen
> with exact ranges, units, and missing data strategies.
>
> **TFS** **§4–5** **(Detector** **Freeze):** D-01–D-03 contracts frozen
> with exact statistical thresholds, input/output schemas, and severity
> formulas.
>
> **TFS** **§6–7** **(Score** **Freeze):** INT-05 contract frozen with
> exact IS/CS formulas, weight defaults, and edge case handling.
>
> **TFS** **§12** **(Data** **Freeze):** All input/output formats,
> required fields, optional fields, and validation rules mapped to INT
> contracts.
>
> **TFS** **§13** **(CLI** **Freeze):** All 8 CLI commands with exact
> arguments, flags, exit codes, and error formats.
>
> **TFS** **§14** **(API** **Freeze):** All 6 REST API endpoints with
> exact request/response schemas and status codes.
>
> **BSD** **§5** **(Benchmark** **Tasks):** INT-09 and INT-10 contracts
> support B-01, B-02, B-03 with frozen evaluation metrics.
>
> **BSD** **§9** **(Pathology** **Injection):** INT-11 contract captures
> all injection parameters.
>
> **BSD** **§10–11** **(Ground** **Truth):** INT-12 contract captures
> label lifecycle, evidence requirements, and inter-rater reliability.
>
> **TRD** **§5** **(Modules):** All 18 TRD modules have corresponding
> INT contracts with exact inputs, outputs, and validation rules.
>
> **TRD** **§16** **(Storage):** Directory architecture and file
> lifecycle rules mapped to output contracts.
>
> **TRD** **§21** **(Reproducibility):** Manifest, checksum, and
> fingerprint contracts mapped to evidence and benchmark outputs.
>
> **AFD** **§8** **(State** **Machine):** INT-15 and INT-16 contracts
> support all defined states and transitions.
>
> **AFD** **§9** **(Error** **Flow):** Error contract framework covers
> all defined error categories with exact codes, severity, and recovery.
>
> **BSD-Engineering** **§4–26:** All schemas, validation rules, and
> storage contracts referenced and enforced by INT contracts.
>
> **SECTION** **26** **—** **INTEGRATION** **TESTING** **FRAMEWORK**
>
> **26.1** **Contract** **Tests**

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

> **26.2** **Schema** **Tests**

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

> **26.3** **Workflow** **Tests**

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

> **26.4** **Benchmark** **Tests**

||
||
||
||
||
||
||
||

> **26.5** **Compatibility** **Tests**

||
||
||
||
||
||
||

> **26.6** **Regression** **Tests**

||
||
||
||
||
||
||

> **26.7** **Acceptance** **Criteria**

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

> **SECTION** **27** **—** **CONTRACT** **AUDIT**
>
> **27.1** **Ambiguity** **Audit**

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

> **27.2** **Redundancy** **Audit**

||
||
||
||
||
||
||
||

> **27.3** **Missing** **Interfaces** **Audit**

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

> **Result:** No missing interfaces identified that are required for V1
> scope.
>
> **27.4** **Version** **Risks**

||
||
||
||
||
||
||
||

> **27.5** **Compatibility** **Risks**

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

> **SECTION** **28** **—** **FINAL** **ACS** **VERDICT**
>
> **28.1** **Primary** **Question**
>
> Can three independent engineering teams build compatible modules that
> integrate successfully using only this document and the previously
> frozen artifacts (IPD, PRD, TFS, BSD, TRD, AFD, BSD-Engineering)?
>
> **28.2** **Answer** **YES.**
>
> **28.3** **Justification**
>
> Three independent engineering teams using the frozen artifacts and
> this ACS v1.0 would build compatible modules because:
>
> 1\. **Interface** **Completeness:** Section 3 defines all 18 internal
> interfaces (INT-01 through INT-18) with exact producer, consumer,
> input contracts, output contracts, version, dependencies, and
> validation rules. No module interaction is undefined.
>
> 2\. **Communication** **Clarity:** Section 2 defines synchronous
> flows, asynchronous flows, internal APIs, external interfaces, CLI
> interfaces, data exchange standards, and contract lifecycles. Teams
> would implement identical communication patterns.
>
> 3\. **Global** **Standards:** Section 4 freezes naming conventions,
> version conventions, response conventions, error conventions,
> pagination, timestamps, identifiers, serialization, and validation
> rules. Teams would produce identically formatted artifacts.
>
> 4\. **Module** **Contracts:** Sections 5–16 define request/response
> schemas, validation rules, error codes, and example payloads for every
> module interaction (ingestion, extraction, windows, detectors,
> scoring, evidence, explanations, benchmarks, ground truth, evaluation,
> reports, exports). Teams would implement identical contract
> boundaries.
>
> 5\. **CLI** **Contracts:** Section 17 freezes all 8 CLI commands with
> exact arguments, flags, defaults, validation, output formats, exit
> codes, and error messages. Teams would implement identical CLI
> behavior.
>
> 6\. **Internal** **Service** **Contracts:** Section 18 defines Python
> class interfaces for all 10 engines with exact method signatures,
> input types, and output types. Teams would implement identical
> internal APIs.
>
> 7\. **Error** **Framework:** Section 19 defines a unified error model
> with severity levels, categories, recovery strategies, logging rules,
> and user visibility. Teams would handle errors identically.
>
> 8\. **Validation** **Framework:** Section 20 defines input, output,
> schema, manifest, benchmark, evidence, and report validation rules.
> Teams would enforce identical validation boundaries.
>
> 9\. **Versioning** **Strategy:** Section 21 defines major/minor/patch
> bump rules, deprecation policy, backward compatibility policy, and
> migration policy. Teams would version contracts identically.
>
> 10.**Security** **Contracts:** Section 22 defines input sanitization,
> path validation, file validation, artifact verification, checksum
> validation, and execution safety. Teams would implement identical
> security boundaries.
>
> 11.**Performance** **Contracts:** Section 23 defines response time
> budgets, payload size limits, memory constraints, runtime constraints,
> timeout rules, and benchmark limits. Teams would implement identical
> performance guards.
>
> 12.**Observability** **Contracts:** Section 24 defines logging,
> tracing, audit, execution metadata, and diagnostic telemetry. Teams
> would produce identical observability artifacts.
>
> 13.**Traceability:** Section 25 maps every contract to PRD
> requirements, TRD modules, AFD workflows, BSD schemas, and TFS
> specifications. Every contract is justified by source documents.
>
> 14.**Integration** **Testing:** Section 26 defines contract tests,
> schema tests, workflow tests, benchmark tests, compatibility tests,
> regression tests, and acceptance criteria. Teams would test the same
> behaviors.
>
> 15.**Ambiguity** **Resolution:** Section 27 audits and resolves
> ambiguity, redundancy, missing interfaces, version risks, and
> compatibility risks. No residual ambiguity permits divergent
> implementations.

**28.4** **Declaration**

**API** **Contract** **Specification** **(ACS** **v1.0)** **Status:**
**Contract** **Authority**

**Verdict:** **API** **CONTRACTS** **APPROVED** **READY** **FOR**
**IMPLEMENTATION** **PLAN**

This document provides sufficient contract detail for three independent
engineering teams to implement the MIIE v1.0 system such that:

> All modules communicate via identical interfaces with identical
> request/response schemas.
>
> All CLI commands accept identical arguments and produce identical exit
> codes and outputs.
>
> All API endpoints accept identical requests and produce identical
> responses and error formats.
>
> All error conditions are handled with identical severity, recovery,
> and user visibility.
>
> All validation rules enforce identical boundaries on inputs and
> outputs.
>
> All security contracts prevent identical classes of injection,
> traversal, and leakage.
>
> All performance contracts enforce identical response times and
> resource limits.
>
> **Implementation** **may** **commence** **immediately.**
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
||

||
||
||
||

> **APPENDIX** **C** **—** **Interface** **Quick** **Reference**

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

> *END* *OF* *API* *CONTRACT* *SPECIFICATION* *(ACS* *v1.0)*
