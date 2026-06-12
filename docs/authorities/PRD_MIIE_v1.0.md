> **Product** **Requirements** **Document** **(PRD** **v1.0)**
>
> **Measurement** **Integrity** **Intelligence** **Engine** **(MIIE)**
>
> **Document** **Version:** 1.0
>
> **Status:** Draft — Pending TRD Generation **Date:** 2026-06-07
>
> **Aligned** **With:** IPD v1.1 FINAL (Frozen)
>
> **SECTION** **1** **—** **Executive** **Summary**
>
> **1.1** **Product** **Overview**
>
> The **Measurement** **Integrity** **Intelligence** **Engine**
> **(MIIE)** is a command-line and programmatic research tool designed
> to evaluate whether software engineering metrics remain trustworthy
> representations of the constructs they claim to measure. MIIE does not
> produce dashboards, rankings, or productivity scores. It produces
> **integrity** **assessments**, **evidence** **packages**, and
> **explanations** that help researchers and repository maintainers
> understand when and why a metric has stopped measuring what it
> purports to measure.
>
> **1.2** **Product** **Purpose**
>
> Software engineering metrics (e.g., code coverage, review turnaround
> time, commit frequency) are widely used in research and practice. Over
> time, these metrics can suffer from:
>
> **Distributional** **drift**: The statistical distribution of a metric
> changes in ways that invalidate historical baselines.
>
> **Correlation** **breakdown**: A metric no longer correlates with
> related constructs as expected.
>
> **Threshold** **compression**: A metric collapses toward an artificial
> boundary (e.g., 100% coverage), reducing its discriminative power.
>
> MIIE detects these pathologies, quantifies their severity, and
> generates transparent, rule-based explanations so that human judgment
> can decide whether a metric remains valid for a given research or
> engineering context.
>
> **1.3** **Version** **1** **Scope**
>
> Version 1 of MIIE is strictly scoped to:

||
||
||
||
||
||

||
||
||
||
||
||
||
||
||

> **1.4** **Expected** **Outcomes**
>
> Researchers can publish papers with explicit integrity checks on their
> metric choices.
>
> Repository maintainers can receive early warnings when repository
> metrics become unreliable for research sampling.
>
> The software analytics community gains a reproducible, open-source
> tool for metric validation.
>
> Detector algorithms are validated against public benchmarks with
> published precision, recall, and AUC.
>
> **SECTION** **2** **—** **Problem** **Definition**
>
> **2.1** **Current** **State** **of** **Software** **Metrics**
>
> Software engineering research and practice rely heavily on
> quantifiable proxies for complex constructs:
>
> **Test** **coverage** as a proxy for test effectiveness
>
> **Code** **review** **participation** as a proxy for collaboration
> quality
>
> **Commit** **frequency** as a proxy for development velocity
>
> **Issue** **resolution** **time** as a proxy for team responsiveness
>
> These proxies are cheap to compute and widely available through Git
> APIs, static analysis tools, and CI/CD pipelines. However, their
> validity is rarely questioned once adopted.
>
> **2.2** **Why** **Metric** **Validity** **Matters** Invalid metrics
> produce:
>
> **False** **research** **conclusions**: Studies generalize findings
> based on corrupted measurements.
>
> **Harmful** **policy** **decisions**: Organizations optimize for
> metrics that no longer reflect desired outcomes.
>
> **Wasted** **engineering** **effort**: Teams game metrics rather than
> improve underlying practices.
>
> **Reproducibility** **crises**: Subsequent studies cannot replicate
> findings because the metric semantics have shifted.
>
> **2.3** **Concrete** **Examples** **of** **Metric** **Pathologies**
>
> ***Coverage*** ***Inflation***
>
> A project enforces 80% coverage via CI gate. Over time, developers
> write trivial tests to satisfy the gate. Coverage remains ≥80%, but
> the metric no longer correlates with defect density. The distribution
> compresses toward the threshold; variance collapses.
>
> ***Review*** ***Metric*** ***Distortion***
>
> A repository introduces mandatory review policies. Review counts
> spike, but many reviews are rubber-stamp approvals. The correlation
> between "review count" and "defect reduction" breaks down.
>
> ***Threshold*** ***Compression***
>
> A team is measured on "zero open bugs older than 30 days." Bugs are
> closed and reopened, or arbitrarily recategorized. The metric clusters
> at the threshold (30 days), destroying its power to discriminate team
> performance.
>
> ***Correlation*** ***Breakdown***
>
> In a longitudinal study, "cyclomatic complexity" and "bug density"
> correlate at r=0.6 for years. After a refactoring initiative, the
> correlation drops to r=0.1 without any change in the underlying
> construct relationship—because the complexity metric now counts
> auto-generated code differently.
>
> **2.4** **Why** **Existing** **Analytics** **Tools** **Fail**

||
||
||
||
||
||
||
||

||
||
||
||

> No existing tool systematically asks: *"Does* *this* *metric* *still*
> *mean* *what* *we* *think* *it* *means?"* MIIE exists to answer that
> question.
>
> **SECTION** **3** **—** **User** **Personas**
>
> **3.1** **Persona** **Evaluation** **Criteria** A persona is included
> in V1 if and only if:
>
> 1\. They directly interact with metric integrity assessment.
>
> 2\. They require CLI or programmatic interfaces (not dashboards).
>
> 3\. Their workflow aligns with one of the four V1 capabilities:
> Repository Analysis, Integrity Assessment, Explanation, Benchmark
> Evaluation.
>
> **3.2** **Approved** **Personas**
>
> ***Persona*** ***1:*** ***Software*** ***Engineering***
> ***Researcher*** ***(SER)***

||
||
||
||
||
||
||
||
||

> ***Persona*** ***2:*** ***Software*** ***Analytics*** ***Researcher***
> ***(SAR)***

||
||
||
||

||
||
||
||
||
||
||
||
||

> ***Persona*** ***3:*** ***Repository*** ***Maintainer*** ***(RM)***

||
||
||
||
||
||
||
||
||

> ***Persona*** ***4:*** ***Engineering*** ***Effectiveness***
> ***Researcher*** ***(EER)***

||
||
||
||
||

||
||
||
||
||
||
||
||

> **3.3** **Rejected** **Personas**

||
||
||
||
||
||
||

> **SECTION** **4** **—** **Jobs** **To** **Be** **Done**
>
> **4.1** **Persona** **1:** **Software** **Engineering** **Researcher**
>
> ***Primary*** ***Jobs***

||
||
||
||
||

||
||
||
||
||

> ***Secondary*** ***Jobs***

||
||
||
||
||

> ***Rejected*** ***Jobs***

||
||
||
||
||

> **4.2** **Persona** **2:** **Software** **Analytics** **Researcher**
>
> ***Primary*** ***Jobs***

||
||
||
||
||

||
||
||
||
||

> ***Secondary*** ***Jobs***

||
||
||
||
||

> ***Rejected*** ***Jobs***

||
||
||
||
||

> **4.3** **Persona** **3:** **Repository** **Maintainer**
>
> ***Primary*** ***Jobs***

||
||
||
||
||

||
||
||
||
||

> ***Secondary*** ***Jobs***

||
||
||
||
||

> ***Rejected*** ***Jobs***

||
||
||
||
||

> **4.4** **Persona** **4:** **Engineering** **Effectiveness**
> **Researcher**
>
> ***Primary*** ***Jobs***

||
||
||
||

||
||
||
||
||
||

> ***Secondary*** ***Jobs***

||
||
||
||
||

> ***Rejected*** ***Jobs***

||
||
||
||
||

**SECTION** **5** **—** **Product** **Principles**

**5.1** **Integrity** **over** **Productivity**

MIIE never measures, ranks, or scores productivity. It assesses whether
metrics are valid proxies for their claimed constructs. A metric can
have perfect integrity while measuring something useless; MIIE will
report that honestly. Conversely, a widely used "productivity" metric
that has lost construct validity will be flagged regardless of its
organizational popularity.

**5.2** **Explainability** **over** **Black** **Boxes**

Every detection result must be explainable through deterministic,
auditable rules. If a drift detector fires, the user must be able to
trace the exact statistical test, threshold, and data window that
triggered it. Machine learning may be used internally for benchmark
ranking or feature extraction, but the final explanation layer must be
rule-based and human-interpretable.

**5.3** **Evidence** **before** **Conclusions**

MIIE separates evidence generation from conclusion generation. The
system always produces an evidence package (raw statistics, test
outputs, distributions) alongside any score or flag. A user must be able
to inspect the evidence and arrive at a different conclusion without
re-running the analysis.

**5.4** **Research** **Reproducibility**

All analyses must be reproducible given the same inputs and
configuration. This requires:

> Deterministic algorithms (fixed random seeds where stochasticity is
> unavoidable)
>
> Version-pinned dependencies
>
> Exported configuration files that fully parameterize the analysis
>
> Documented data preprocessing steps

**5.5** **Transparency** **of** **Detection** **Logic**

The logic for every detector must be documented in human-readable form,
accessible without reading source code. This includes:

> The statistical test employed
>
> The null hypothesis
>
> The threshold or decision boundary
>
> The assumptions and their validation checks
>
> Known limitations and false-positive rates from benchmark evaluation

**5.6** **Human** **Oversight** **Required**

MIIE does not autonomously reject data, block commits, or trigger
operational alerts. It produces assessments and explanations for human
review. The human operator decides whether a detected pathology is
actionable, acceptable, or a false positive. MIIE is an intelligence
engine, not an autonomous control system.

> **SECTION** **6** **—** **User** **Stories**
>
> **6.1** **Repository** **Analysis** **Stories**
>
> ***US-001:*** ***Analyze*** ***Single*** ***Repository***

||
||
||
||
||
||
||
||
||
||

> ***US-002:*** ***Analyze*** ***Multiple*** ***Repositories***

||
||
||
||
||
||
||
||

||
||
||
||
||
||

> **6.2** **Drift** **Investigation** **Stories**
>
> ***US-003:*** ***Investigate*** ***Distributional*** ***Drift***

||
||
||
||
||
||
||
||
||
||

> ***US-004:*** ***Investigate*** ***Correlation*** ***Breakdown***

||
||
||
||
||
||
||
||

||
||
||
||
||
||

> ***US-005:*** ***Investigate*** ***Threshold*** ***Compression***

||
||
||
||
||
||
||
||
||
||

> **6.3** **Benchmark** **Evaluation** **Stories**
>
> ***US-006:*** ***Run*** ***Standard*** ***Benchmark***

||
||
||
||
||
||
||

||
||
||
||
||
||

> ***US-007:*** ***Compare*** ***Detectors*** ***on*** ***Benchmark***

||
||
||
||
||
||
||
||
||
||

> **6.4** **Detector** **Evaluation** **Stories**
>
> ***US-008:*** ***Evaluate*** ***Detector*** ***Configuration***

||
||
||
||
||

||
||
||
||
||
||
||
||

> **6.5** **Explanation** **Review** **Stories**
>
> ***US-009:*** ***Review*** ***Explanation*** ***for*** ***Integrity***
> ***Failure***

||
||
||
||
||
||
||
||
||
||

> ***US-010:*** ***Export*** ***Evidence*** ***Package*** ***for***
> ***Manual*** ***Review***

||
||
||
||
||

||
||
||
||
||
||
||
||
||

> **SECTION** **7** **—** **Functional** **Requirements**
>
> **7.1** **Requirement** **Inventory**
>
> ***FR-001:*** ***Repository*** ***Ingestion***

||
||
||
||
||
||
||
||
||

> ***FR-002:*** ***Metric*** ***Extraction***

||
||
||
||
||
||
||
||
||

> ***FR-003:*** ***Window*** ***Segmentation***

||
||
||
||
||
||
||
||
||

> ***FR-004:*** ***Distributional*** ***Drift*** ***Detection***

||
||
||
||
||
||
||
||
||

> ***FR-005:*** ***Correlation*** ***Analysis***

||
||
||
||
||
||
||
||
||

> ***FR-006:*** ***Threshold*** ***Compression*** ***Detection***

||
||
||
||
||
||
||
||
||

> ***FR-007:*** ***Integrity*** ***Score*** ***Generation***

||
||
||
||
||
||
||
||
||

> ***FR-008:*** ***Confidence*** ***Score*** ***Generation***

||
||
||
||

||
||
||
||
||
||
||
||

> ***FR-009:*** ***Evidence*** ***Aggregation***

||
||
||
||
||
||
||
||
||

> ***FR-010:*** ***Explanation*** ***Generation***

||
||
||
||
||
||

||
||
||
||
||
||
||

> ***FR-011:*** ***CLI*** ***Interface***

||
||
||
||
||
||
||
||
||

> ***FR-012:*** ***REST*** ***API***

||
||
||
||
||
||
||

||
||
||
||
||

> ***FR-013:*** ***Benchmark*** ***Execution***

||
||
||
||
||
||
||
||
||

> ***FR-014:*** ***Result*** ***Export***

||
||
||
||
||
||
||

||
||
||
||
||

> ***FR-015:*** ***Configuration*** ***Management***

||
||
||
||
||
||
||
||
||

> ***FR-016:*** ***Metric*** ***Registry***

||
||
||
||
||
||
||
||
||

> ***FR-017:*** ***Detector*** ***Registry***

||
||
||
||
||
||
||
||
||

> ***FR-018:*** ***Cross-Window*** ***Comparison***

||
||
||
||
||
||
||
||
||

> ***FR-019:*** ***Batch*** ***Benchmark*** ***Execution***

||
||
||
||
||
||

||
||
||
||
||
||

> **SECTION** **8** **—** **Non-Functional** **Requirements**
>
> **8.1** **Performance**

||
||
||
||
||
||

> **8.2** **Scalability**

||
||
||
||
||
||

> **8.3** **Reliability**

||
||
||
||

||
||
||
||
||
||

> **8.4** **Security**

||
||
||
||
||
||

> **8.5** **Maintainability**

||
||
||
||
||
||
||

> **8.6** **Reproducibility**

||
||
||
||
||

||
||
||
||
||

> **8.7** **Usability**

||
||
||
||
||
||

> **8.8** **Portability**

||
||
||
||
||
||

> **8.9** **Observability**

||
||
||
||
||
||

> **SECTION** **9** **—** **User** **Workflow** **Definitions**
>
> **9.1** **Workflow** **1:** **Analyze** **Repository**

||
||
||
||
||
||
||
||
||

> **9.2** **Workflow** **2:** **Investigate** **Integrity** **Failure**

||
||
||
||
||

||
||
||
||
||
||
||

> **9.3** **Workflow** **3:** **Run** **Benchmark** **Evaluation**

||
||
||
||
||
||
||
||

||
||
||
||

> **9.4** **Workflow** **4:** **Export** **Results**

||
||
||
||
||
||
||
||
||

> **9.5** **Workflow** **5:** **Compare** **Time** **Windows**

||
||
||
||
||
||

||
||
||
||
||
||
||

> **SECTION** **10** **—** **Product** **Outputs**
>
> **10.1** **Integrity** **Score**

||
||
||
||
||
||
||
||

> **10.2** **Confidence** **Score**

||
||
||
||
||
||
||
||

> **10.3** **Drift** **Report**

||
||
||
||
||
||

||
||
||
||
||
||

> **10.4** **Evidence** **Package**

||
||
||
||
||
||
||
||

> **10.5** **Explanation** **Report**

||
||
||
||
||

||
||
||
||
||
||
||

> **10.6** **Benchmark** **Report**

||
||
||
||
||
||

||
||
||
||
||
||

> **SECTION** **11** **—** **CLI** **Requirements**
>
> **11.1** **Command** **Structure**
>
> miie \[global-options\] \<command\> \[command-options\]
>
> **11.2** **Global** **Options**

||
||
||
||
||
||
||
||

> **11.3** **Commands**
>
> ***miie*** ***analyze***
>
> Analyze a repository for metric integrity.

||
||
||
||
||
||
||
||
||
||

||
||
||
||

> **Example:**
>
> miie analyze --repo https://github.com/org/repo.git --since 2025-01-01
> --until 2025-12-31 --metrics coverage,complexity,commit_frequency
> --window-strategy time --window-size 90 --output ./analysis-2025/
>
> ***miie*** ***benchmark***
>
> Run a benchmark suite against one or more detectors.

||
||
||
||
||
||
||
||

> **Example:**
>
> miie benchmark --suite metric-drift-v1 --detectors ks_drift,psi_drift
> --seed 42 --output ./benchmark-results/
>
> ***miie*** ***explain***
>
> Generate or re-generate explanations from an existing analysis.

||
||
||
||
||
||
||

> **Example:**
>
> miie explain --input ./analysis-2025/ --metric coverage --format md
>
> ***miie*** ***export***
>
> Export results from an existing analysis in specified formats.

||
||
||
||
||
||
||

> **Example:**
>
> miie export --input ./analysis-2025/ --format csv --filter
> failures_only
>
> **11.4** **Exit** **Codes**

||
||
||
||
||
||
||
||

> **11.5** **Error** **Handling**
>
> All errors are written to **stderr**.
>
> Error messages follow the format: \[ERROR-CODE\] Human-readable
> description. Suggestion: actionable fix.
>
> Fatal errors include a traceback only when --verbose is enabled.
>
> Partial results are saved on graceful shutdown (SIGINT, OOM warning)
> when possible.

**SECTION** **12** **—** **REST** **API** **Requirements**

**12.1** **Base** **URL** **and** **Versioning**

> Base URL: http://localhost:8000 (default, configurable)
>
> Versioning: URL path prefix /v1/
>
> All endpoints return JSON unless otherwise specified.

**12.2** **Endpoints**

***POST*** ***/v1/analyze***

Submit a repository analysis job.

**Request** **Model:**

{

> "repo": "https://github.com/org/repo.git", "since": "2025-01-01",
>
> "until": "2025-12-31",
>
> "metrics": \["coverage", "complexity", "commit_frequency"\],
> "window_strategy": "time",
>
> "window_size": 90,

"detectors": \["ks_drift", "psi_drift", "correlation_breakdown",
"threshold_compression"\],

"output_formats": \["json", "md"\] }

**Response** **Model** **(202** **Accepted):**

{

> "job_id": "uuid-1234", "status": "queued",

"poll_url": "/v1/jobs/uuid-1234" }

***GET*** ***/v1/jobs/{job_id}***

Poll job status and retrieve results.

**Response** **Models:**

> 200 OK (completed):

{

> "job_id": "uuid-1234", "status": "completed",
>
> "created_at": "2026-06-07T00:00:00Z", "completed_at":
> "2026-06-07T00:04:00Z", "results_url": "/v1/jobs/uuid-1234/results",
> "summary": {
>
> "overall_integrity_score": 0.72, "overall_confidence": 0.68,
> "failures_detected": 3

} }

> 202 Accepted (running):

{

> "job_id": "uuid-1234", "status": "running", "progress": 0.45,

"stage": "detector_execution" }

***GET*** ***/v1/jobs/{job_id}/results*** Download full results.

**Response:** 200 OK with JSON body identical to CLI JSON export.

***POST*** ***/v1/benchmark*** Submit a benchmark job.

**Request** **Model:**

{

> "suite": "metric-drift-v1", "detectors": \["ks_drift", "psi_drift"\],
>
> "config_overrides": {"ks_drift": {"alpha": 0.01}}, "seed": 42,

"output_formats": \["json", "md"\] }

**Response** **Model** **(202** **Accepted):**

{

> "job_id": "uuid-5678", "status": "queued",

"poll_url": "/v1/jobs/uuid-5678" }

***POST*** ***/v1/explain***

Generate explanations from existing results.

**Request** **Model:**

{

> "job_id": "uuid-1234", "metric": "coverage",
>
> "detector": "threshold_compression", "format": "md"

}

**Response** **Model** **(200** **OK):**

{

> "explanation": "# Coverage — Threshold Compression\n...",
> "rule_fired": "THRESHOLD-001",

"evidence_refs": \["evidence-42", "evidence-43"\] }

***POST*** ***/v1/export*** Export existing results.

**Request** **Model:**

> {
>
> "job_id": "uuid-1234", "formats": \["csv"\], "filter": "failures_only"
>
> }
>
> **Response** **Model** **(200** **OK):**
>
> {
>
> "download_urls": {
>
> "csv": "/v1/jobs/uuid-1234/export/csv" }
>
> }
>
> ***GET*** ***/v1/health*** Health check.
>
> **Response** **Model** **(200** **OK):**
>
> {
>
> "status": "healthy", "version": "1.0.0", "uptime_seconds": 3600
>
> }
>
> **12.3** **Status** **Codes**

||
||
||
||
||
||
||
||
||

> **12.4** **Error** **Handling**
>
> Error responses follow RFC 7807 (Problem Details):
>
> {
>
> "type": "https://miie.dev/errors/invalid-repo", "title": "Invalid
> Repository",
>
> "status": 400,
>
> "detail": "The provided URL is not a valid Git repository.",
> "instance": "/v1/analyze"
>
> }
>
> **12.5** **Versioning** **Strategy**
>
> URL path versioning (/v1/).
>
> Breaking changes require a new version prefix (/v2/).
>
> Non-breaking additions (new optional fields, new endpoints) are
> backward-compatible within /v1/.
>
> Deprecation notices are returned in response headers: Deprecation:
> true and Sunset: \<date\>.
>
> **12.6** **Authentication** **Strategy**
>
> **Local** **mode:** No authentication. API binds to localhost only.
>
> **Networked** **mode** **(optional):** API key via Authorization:
> Bearer \<token\> header.
>
> API keys are managed outside MIIE (e.g., reverse proxy, environment
> variable).
>
> MIIE itself does not implement user management, sessions, or
> role-based access control.
>
> **SECTION** **13** **—** **Data** **Requirements**
>
> **13.1** **Input** **Sources**

||
||
||
||
||
||
||
||

> **13.2** **Data** **Formats**

||
||
||
||

||
||
||
||
||
||
||

> **13.3** **Validation** **Rules**
>
> **Repository** **validation:** Must contain .git directory; git log
> must return non-empty history.
>
> **Metric** **data** **validation:** Values must be numeric or null;
> timestamps must be ISO 8601; no duplicate commits.
>
> **Configuration** **validation:** Strict schema; unknown fields
> rejected; required fields enforced.
>
> **Benchmark** **validation:** Ground truth labels must be boolean or
> categorical; dataset rows must match detector input schema.
>
> **13.4** **Data** **Retention**
>
> MIIE does not maintain a database.
>
> All outputs are written to the user-specified output directory.
>
> Users are responsible for retention and deletion of output files.
>
> Temporary clone directories are cleaned up after analysis unless
> --keep-cache is specified.
>
> No telemetry or usage data is collected by default.
>
> **13.5** **Benchmark** **Storage**
>
> Default benchmark directory: ~/.miie/benchmarks/
>
> Each suite is a subdirectory containing:
>
> manifest.json — suite metadata, version, description
>
> data.json or data.csv — labeled dataset
>
> schema.json — expected input/output schema for detectors
>
> Benchmark suites are versioned independently of MIIE.
>
> Users can add custom suites by creating a compliant subdirectory.
>
> **13.6** **Export** **Formats**

||
||
||
||
||
||

> **SECTION** **14** **—** **Success** **Metrics**
>
> **14.1** **Product** **Success**

||
||
||
||
||
||
||

> **14.2** **Research** **Success**

||
||
||
||
||
||
||
||

> **14.3** **Engineering** **Success**

||
||
||
||
||
||
||

> **14.4** **Open** **Source** **Success**

||
||
||
||
||
||
||

> **SECTION** **15** **—** **Risks** **&** **Assumptions**
>
> **15.1** **Product** **Risks**

||
||
||
||
||
||

||
||
||
||

> **15.2** **Research** **Risks**

||
||
||
||
||
||

> **15.3** **Technical** **Risks**

||
||
||
||
||

||
||
||
||

> **15.4** **Data** **Risks**

||
||
||
||
||
||

> **15.5** **Operational** **Risks**

||
||
||
||
||
||

||
||
||
||

> **SECTION** **16** **—** **Version** **1** **Release** **Scope**
> **(MoSCoW)**
>
> **16.1** **Must** **Have**

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **16.2** **Should** **Have**

||
||
||
||
||
||
||
||

||
||
||
||
||

> **16.3** **Could** **Have**

||
||
||
||
||
||
||

> **16.4** **Won't** **Have**

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **SECTION** **17** **—** **Traceability** **Matrix**

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||

> **SECTION** **18** **—** **Final** **Product** **Definition**
>
> **18.1** **What** **exactly** **is** **MIIE?**
>
> MIIE is a **command-line** **research** **tool** that evaluates
> whether software engineering metrics remain valid representations of
> the constructs they claim to measure. It does this by:
>
> 1\. Ingesting Git repositories.
>
> 2\. Extracting software engineering metrics from history and
> artifacts.
>
> 3\. Segmenting history into temporal windows.
>
> 4\. Running statistical detectors for distributional drift,
> correlation breakdown, and threshold compression.
>
> 5\. Aggregating evidence into structured packages.
>
> 6\. Computing composite Integrity and Confidence Scores.
>
> 7\. Generating transparent, rule-based explanations for every detected
> failure.
>
> 8\. Validating detectors against standardized benchmarks.

MIIE produces **files** (JSON, Markdown, CSV) that researchers and
maintainers can inspect, share, and include in publications.

**18.2** **What** **is** **MIIE** **not?**

> MIIE is **not** a productivity tracking tool.
>
> MIIE is **not** a developer ranking or performance evaluation system.
>
> MIIE is **not** an employee monitoring or surveillance platform.
>
> MIIE is **not** a KPI dashboard or business intelligence tool.
>
> MIIE is **not** a project management or sprint planning system.
>
> MIIE is **not** a real-time monitoring or alerting system.
>
> MIIE is **not** a generic analytics platform.
>
> MIIE is **not** a SaaS product with user management, billing, or
> multi-tenancy.
>
> MIIE is **not** a GUI application or web dashboard.
>
> MIIE is **not** an autonomous control system that blocks commits or
> enforces gates.
>
> MIIE is **not** a database or data warehouse.

**18.3** **Who** **should** **use** **MIIE?**

> **Software** **engineering** **researchers** who need to defend
> construct validity in quantitative studies.
>
> **Software** **analytics** **researchers** who develop and validate
> metric detectors.
>
> **Repository** **maintainers** who want to ensure their data remains
> trustworthy for research.
>
> **Engineering** **effectiveness** **researchers** who need objective
> evidence to validate or challenge metric usage in organizations.

**18.4** **Who** **should** **not** **use** **MIIE?**

> **Engineering** **managers** seeking to rank developers or track
> productivity.
>
> **HR** **or** **compliance** **officers** seeking surveillance or
> monitoring tools.
>
> **Executives** seeking KPI dashboards or high-level operational
> metrics.
>
> **DevOps** **engineers** seeking real-time system monitoring or
> alerting.
>
> **Casual** **users** who need a point-and-click GUI without
> statistical literacy.
>
> **18.5** **What** **unique** **value** **does** **MIIE** **create?**
>
> MIIE is the **first** **open-source** **tool** **dedicated**
> **exclusively** **to** **measurement** **integrity** in software
> engineering. Unlike analytics platforms that assume metrics are valid,
> MIIE questions that assumption. It provides:
>
> **Statistical** **rigor**: Detectors grounded in established
> statistical tests.
>
> **Transparency**: Rule-based explanations, not black-box alerts.
>
> **Reproducibility**: Deterministic, versioned, configuration-driven
> analysis.
>
> **Research** **alignment**: Outputs designed for inclusion in
> peer-reviewed publications.
>
> **Ethical** **clarity**: Explicitly rejects surveillance and
> productivity tracking.
>
> **18.6** **Why** **does** **MIIE** **deserve** **to** **exist?**
>
> Software engineering research and practice are increasingly
> metric-driven. Yet the validity of these metrics is rarely tested.
> Coverage inflation, review metric distortion, and threshold
> compression are widespread but undiagnosed. Without a tool to detect
> these pathologies, researchers publish invalid findings, organizations
> optimize for corrupted signals, and the field accumulates technical
> debt in its measurement infrastructure.
>
> MIIE exists to **make** **metric** **integrity** **a** **first-class**
> **concern**—not an afterthought. It gives the research community a
> shared, reproducible, and transparent tool to ask the most important
> question about any metric: *Does* *it* *still* *mean* *what* *we*
> *think* *it* *means?*
>
> **SECTION** **19** **—** **PRD** **Approval** **Verdict**
>
> **19.1** **Scoring**

||
||
||
||
||
||

||
||
||
||
||
||

> **19.2** **Final** **Recommendation** **Ready** **for** **TRD?**
> **YES**
>
> The PRD v1.0 is complete, aligned with IPD v1.1 FINAL, and ready to
> serve as the source document for:
>
> Technical Requirements Document (TRD)
>
> Application Flow Design
>
> Backend Schema Design
>
> API Design Specification
>
> UI/UX Design Brief (CLI + Report Formatting)
>
> **19.3** **Minor** **Notes** **for** **TRD** **Phase**
>
> 1\. **Performance** **targets** (Section 8.1) should be validated with
> a prototype on 3–5 real-world repositories before finalizing.
>
> 2\. **Benchmark** **suite** **schema** (Section 13.5) needs a formal
> JSON Schema definition in TRD.
>
> 3\. **Explanation** **rule** **engine** (FR-010) needs a template
> language specification; consider Jinja2 or a custom lightweight DSL.
>
> 4\. **REST** **API** **job** **state** **management** (FR-012) needs a
> decision on whether to use filesystem, SQLite, or external queue for
> job persistence.
>
> 5\. **Security** **model** (Section 8.4) should be expanded with a
> threat model document in TRD.
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

> **APPENDIX** **C** **—** **References**
>
> IPD v1.1 FINAL (Frozen) — Measurement Integrity Intelligence Engine
> Initiative Document
>
> IEEE Standard for Software Engineering Metrics (IEEE 1061)
>
> ISO/IEC 25010:2011 Systems and software quality models
>
> Campbell, D.T., & Fiske, D.W. (1959). Convergent and discriminant
> validation by the multitrait-multimethod matrix.

**END** **OF** **PRD** **v1.0**
