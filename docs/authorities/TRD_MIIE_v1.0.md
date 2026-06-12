> **MIIE** **Technical** **Requirements** **Document** **(TRD**
> **v1.0)** **System:** Measurement Integrity Intelligence Engine (MIIE)
>
> **Version:** 1.0.0
>
> **Status:** Implementation Authority **Date:** 2026-06-07
>
> **Inputs:** IPD v1.1 FINAL \| PRD v1.0 \| TFS v1.0 \| BSD v1.0
>
> **Objective:** Define exact engineering specifications such that three
> independent teams produce functionally equivalent systems.
>
> **SECTION** **1** **—** **Executive** **Technical** **Summary**
>
> **1.1** **System** **Name**
>
> **Measurement** **Integrity** **Intelligence** **Engine** **(MIIE)**
> *Code* *namespace:* miie
>
> *Package* *name:* miie *CLI* *entry* *point:* miie
>
> **1.2** **Version**
>
> **1.0.0** — Frozen. No minor or patch versions may introduce new
> capabilities. Only bug fixes and documentation updates are permitted
> within v1.0.x.
>
> **1.3** **Mission**
>
> Evaluate whether software engineering metrics remain trustworthy
> representations of the constructs they claim to measure, by ingesting
> Git repositories, extracting frozen metrics, segmenting history into
> windows, running frozen detectors, and producing deterministic
> Integrity Scores, Confidence Scores, evidence packages, and rule-based
> explanations.
>
> **1.4** **Technical** **Objectives**

||
||
||
||
||
||
||
||

||
||
||
||
||

> **1.5** **Supported** **Capabilities**

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **1.6** **Unsupported** **Capabilities**

||
||
||
||
||
||
||
||
||
||
||
||
||

> **1.7** **System** **Boundaries**
>
> ┌─────────────────────────────────────────────────────────────┐ │
> EXTERNAL ENVIRONMENT │ │ Git Repositories │ Coverage Artifacts │
> PR/Issue Exports │ │ (User-provided) │ (In repo or path) │
> (User-provided) │
> └──────────────────┬────────────────────┬────────────────────┘
>
> │ │ ▼ ▼
>
> ┌─────────────────────────────────────────────────────────────┐ │ MIIE
> SYSTEM BOUNDARY │ │ │ │ ┌─────────────┐ ┌─────────────┐
> ┌─────────────────────┐│ │ │ CLI Layer │ │ REST API │ │ Config /
> Registry ││ │ │ (Primary) │ │ (Secondary) │ │ (YAML/JSON) ││ │
> └──────┬──────┘ └──────┬──────┘ └─────────────────────┘│
>
> │ │ │ │ │ ┌──────┴────────────────┴────────────────────────────────┐│
>
> │ │ CORE PROCESSING PIPELINE ││ │ │ Ingestion → Extraction →
> Segmentation → Detection ││ │ │ → Scoring → Evidence → Explanation →
> Export ││ │
> └─────────────────────────────────────────────────────────┘│ │ │ │ │
> ┌──────┴──────────────────────────────────────────────────┐│ │ │
> BENCHMARK SUBSYSTEM ││ │ │ Dataset Generation → Ground Truth → Runner
> → Eval ││ │
> └─────────────────────────────────────────────────────────┘│ │ │ │ │
> ┌──────┴──────────────────────────────────────────────────┐│ │ │
> OUTPUT BOUNDARY ││ │ │ JSON / Markdown / CSV → User filesystem ││ │
> └─────────────────────────────────────────────────────────┘│
> └─────────────────────────────────────────────────────────────┘
>
> **1.8** **Technology** **Constraints**

||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **1.9** **Success** **Criteria**

||
||
||
||
||
||
||
||
||
||

> **SECTION** **2** **—** **System** **Architecture** **Overview**
>
> **2.1** **High-Level** **Architecture**
>
> ┌─────────────────────────────────────────────────────────────────────────────┐
> │ MIIE v1.0 Architecture │
> ├─────────────────────────────────────────────────────────────────────────────┤
> │ │ │
> ┌─────────────────────────────────────────────────────────────────────────┐│

│ │ INTERFACE LAYER ││ │ │ ┌──────────────┐ ┌──────────────┐
┌──────────────┐ ┌────────────┐ ││

│ │ │ CLI Parser │ │ API Server │ │ Config Loader│ │ Registry │ ││ │ │ │
(M-10) │ │ (M-11) │ │ (M-12) │ │ (M-13) │ ││ │ │ └──────┬───────┘
└──────┬───────┘ └──────┬───────┘ └─────┬──────┘ ││ │
└─────────┼────────────────┼──────────────────┼────────────────┼──────────┘│
│ │ │ │ │ │ │ ▼ ▼ ▼ ▼ │ │
┌─────────────────────────────────────────────────────────────────────────┐│

│ │ ORCHESTRATION LAYER ││ │ │ ┌──────────────┐ ┌──────────────┐
┌──────────────┐ ┌────────────┐ ││

│ │ │ Job Manager │ │ Pipeline │ │ State │ │ Workflow │ ││ │ │ │ (M-14)
│ │ Controller │ │ Manager │ │ Engine │ ││ │ │ │ │ │ (M-15) │ │ (M-16) │
│ (M-17) │ ││ │ │ └──────────────┘ └──────────────┘ └──────────────┘
└────────────┘ ││ │
└─────────────────────────────────────────────────────────────────────────┘│
│ │ │ │ ▼ │ │
┌─────────────────────────────────────────────────────────────────────────┐│
│ │ PROCESSING LAYER ││ │ │ ┌──────────────┐ ┌──────────────┐
┌──────────────┐ ┌────────────┐ ││ │ │ │ Repository │ │ Metric │ │
Window │ │ Detector │ ││ │ │ │ Ingestion │ │ Extraction │ │ Segmentation
│ │ Engine │ ││ │ │ │ (M-01) │ │ (M-02) │ │ (M-03) │ │ (M-05) │ ││ │ │
└──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ ││ │ │
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ ││ │ │
│ Scoring │ │ Evidence │ │ Explanation │ │ Report │ ││ │ │ │ Engine │ │
Aggregator │ │ Generator │ │ Generator │ ││ │ │ │ (M-08) │ │ (M-09) │ │
(M-09) │ │ (M-09) │ ││ │ │ └──────────────┘ └──────────────┘
└──────────────┘ └────────────┘ ││ │
└─────────────────────────────────────────────────────────────────────────┘│
│ │ │ │ ▼ │ │
┌─────────────────────────────────────────────────────────────────────────┐│
│ │ BENCHMARK SUBSYSTEM ││ │ │ ┌──────────────┐ ┌──────────────┐
┌──────────────┐ ┌────────────┐ ││ │ │ │ Dataset │ │ Ground Truth │ │
Benchmark │ │ Evaluation │ ││ │ │ │ Generator │ │ Manager │ │ Runner │ │
Engine │ ││ │ │ │ (M-03) │ │ (M-04) │ │ (M-06) │ │ (M-07) │ ││ │ │
└──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ ││ │
└─────────────────────────────────────────────────────────────────────────┘│
│ │ │ │ ▼ │ │
┌─────────────────────────────────────────────────────────────────────────┐│
│ │ STORAGE LAYER ││ │ │ ┌──────────────┐ ┌──────────────┐
┌──────────────┐ ┌────────────┐ ││ │ │ │ Output Dir │ │ Cache Dir │ │
Benchmark │ │ Config Dir │ ││ │ │ │ (User-spec) │ │ (~/.miie/) │ │ Dir │
│ (~/.miie/) │ ││ │ │ └──────────────┘ └──────────────┘ └──────────────┘
└────────────┘ ││ │
└─────────────────────────────────────────────────────────────────────────┘│
│ │
└─────────────────────────────────────────────────────────────────────────────┘

**2.2** **Layer** **Responsibilities**

***Data*** ***Layer*** ***(Storage)***

> **Responsibility:** Persistent storage of all inputs, intermediate
> results, and outputs.
>
> **Components:** Output directory, cache directory (~/.miie/cache/),
> benchmark directory (~/.miie/benchmarks/), config directory
> (~/.miie/).
>
> **Technology:** Filesystem only; JSON, YAML, CSV, Markdown files.
>
> **Constraints:** No database; no network storage required for core
> operation.
>
> ***Processing*** ***Layer*** ***(Core)***
>
> **Responsibility:** Execute the analysis pipeline: ingestion →
> extraction → segmentation → detection → scoring → evidence →
> explanation → export.
>
> **Components:** M-01 through M-09.
>
> **Communication:** In-memory data structures (pandas DataFrames,
> dictionaries) passed between modules; no inter-process communication
> required.
>
> **Constraints:** Single-threaded by default; optional multiprocessing
> for window-level parallelism.
>
> ***Detection*** ***Layer***
>
> **Responsibility:** Execute statistical tests for drift, correlation
> breakdown, and threshold compression.
>
> **Components:** D-01, D-02, D-03 implementations.
>
> **Constraints:** Deterministic; fixed seeds; no machine learning
> training on benchmark data.
>
> ***Evaluation*** ***Layer*** ***(Benchmark)***
>
> **Responsibility:** Execute benchmark suites, collect predictions,
> compute evaluation metrics.
>
> **Components:** M-06, M-07.
>
> **Constraints:** Isolated from ground truth during detection; standard
> classification metrics only.
>
> ***Export*** ***Layer***
>
> **Responsibility:** Render analysis results into JSON, Markdown, and
> CSV formats.
>
> **Components:** M-09 (Report Generator).
>
> **Constraints:** Self-contained outputs; no external dependencies to
> interpret.
>
> ***CLI*** ***Layer***
>
> **Responsibility:** Parse user input, dispatch to pipeline or
> benchmark subsystem, handle errors, report progress.
>
> **Components:** M-10 (CLI Interface).
>
> **Constraints:** Primary interface; all capabilities accessible
> without API.
>
> **2.3** **Dependencies**

||
||
||
||

||
||
||
||
||
||
||
||

> **2.4** **Communication** **Paths**
>
> 1\. **CLI** **→** **Orchestration:** Direct Python function calls (not
> RPC).
>
> 2\. **Orchestration** **→** **Processing:** Module imports and
> function calls.
>
> 3\. **Processing** **→** **Data** **Layer:** File system I/O via
> pathlib.
>
> 4\. **API** **→** **Orchestration:** FastAPI route handlers call
> orchestration functions.
>
> 5\. **Benchmark** **→** **Processing:** Benchmark runner imports
> detector engine directly.
>
> 6\. **All** **layers** **→** **Logging:** Python logging module to
> stderr/file.
>
> **SECTION** **3** **—** **Architecture** **Principles**
>
> **3.1** **Reproducibility** **First**
>
> **Principle:** Every analysis must be bitwise-identical when re-run
> with identical inputs, configuration, and random seed.
>
> **Implementation** **Impact:**
>
> All random operations use numpy.random.RandomState(seed) or
> random.seed(seed) explicitly.
>
> Seed is a required parameter in all stochastic modules; default is 42.
>
> Dependency versions are pinned in poetry.lock.
>
> Configuration files are hashed (SHA-256) and included in output
> metadata.
>
> No use of system time or process IDs in filenames or computations.
>
> **3.2** **Determinism** **First**
>
> **Principle:** The system must produce deterministic outputs given
> deterministic inputs, even across different operating systems and
> Python patch versions.
>
> **Implementation** **Impact:**
>
> Sort all intermediate collections before iteration (e.g.,
> sorted(os.listdir()) rather than arbitrary order).
>
> Use math.fsum() for floating-point summation to reduce platform
> variance.
>
> Avoid hash-based iteration order dependencies (e.g., set iteration is
> non-deterministic; convert to sorted() lists).
>
> Pin all transitive dependencies.
>
> Document known sources of non-determinism (e.g., scipy.stats.ks_2samp
> exact method may vary by SciPy version) and mitigate by using
> asymptotic approximations where specified.

**3.3** **Explainability** **First**

**Principle:** Every score, flag, and conclusion must be traceable to a
specific detector, statistical test, data window, and rule.

**Implementation** **Impact:**

> Evidence package includes full provenance: detector ID, test name,
> statistic value, window IDs, timestamp.
>
> Explanation generator uses Jinja2 templates with deterministic
> rule-to-template mapping.
>
> Every Integrity Score component is stored individually before
> aggregation.
>
> Rule engine logs which rule fired for every explanation.
>
> No opaque machine learning models in the explanation path.

**3.4** **Offline** **First**

**Principle:** The system must execute all core capabilities without
network access, external SaaS, or database connectivity.

**Implementation** **Impact:**

> Repository ingestion supports local paths without network.
>
> Remote repository cloning is the only network operation; after clone,
> all processing is offline.
>
> No API calls to GitHub, GitLab, or coverage services during analysis.
>
> All benchmark data is local.
>
> REST API is self-contained; no external queue or database.

**3.5** **Research** **Infrastructure** **First**

**Principle:** The system is built as research infrastructure, not as a
product or service. Prioritize scientific validity, transparency, and
extensibility over user convenience or commercial features.

**Implementation** **Impact:**

> CLI is the primary interface; no GUI investment.
>
> Outputs are designed for inclusion in papers (Markdown reports, JSON
> for programmatic analysis).
>
> All algorithms are documented with publication references.
>
> Code is open-source and licensed for academic use.
>
> No telemetry, tracking, or usage analytics.
>
> Extensibility via registry pattern (metrics, detectors, benchmarks)
> rather than plugin marketplace.
>
> **SECTION** **4** **—** **System** **Context**
>
> **4.1** **Context** **Diagram**
>
> ┌─────────────────┐ │ Researcher │ │ (SER, SAR, │ │ RM, EER) │
> └────────┬────────┘ │
>
> ┌──────────────┼──────────────┐ │ │ │ ▼ ▼ ▼
>
> ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │ CLI │ │ API │ │
> Config │ │ Terminal │ │ Client │ │ Files │ └──────┬──────┘
> └──────┬──────┘ └──────┬──────┘ │ │ │
> └───────────────┼───────────────┘ │ ▼
>
> ┌─────────────────────────────┐ │ MIIE SYSTEM │ │
> ┌─────────────────────┐ │ │ │ Analysis Pipeline │ │ │ │ Benchmark
> System │ │ │ └─────────────────────┘ │ └─────────────┬─────────────┘
>
> │ ┌─────────────┼─────────────┐ │ │ │ ▼ ▼ ▼
>
> ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │ JSON │ │ Markdown │
> │ CSV │ │ Reports │ │ Reports │ │ Data │ └─────────────┘
> └─────────────┘ └─────────────┘
>
> **4.2** **External** **Inputs**

||
||
||
||
||
||

||
||
||
||
||
||

> **4.3** **External** **Outputs**

||
||
||
||
||
||
||

> **4.4** **Actors**

||
||
||
||
||
||
||
||
||

> **4.5** **Dependencies**

||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **4.6** **Interaction** **Model**
>
> 1\. **Synchronous** **(CLI):** User invokes command; system processes;
> results written to disk; exit code returned. No daemon process.
>
> 2\. **Asynchronous** **(API):** Client submits job; system queues job;
> client polls for status; results available via download URL. No
> persistent connection.
>
> 3\. **Batch** **(Benchmark):** User submits benchmark job; system
> processes all datasets sequentially or in parallel; aggregated results
> written to disk.
>
> **SECTION** **5** **—** **Core** **Modules**
>
> **5.1** **Module** **Inventory**

||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **5.2** **M-01:** **Repository** **Ingestion** **Engine**

||
||
||
||
||
||
||
||
||

||
||
||
||
||

> **5.3** **M-02:** **Metric** **Extraction** **Engine**

||
||
||
||
||
||
||
||
||
||
||

> **5.4** **M-03:** **Dataset** **Generator**

||
||
||
||
||

||
||
||
||
||
||
||
||
||
||

> **5.5** **M-04:** **Ground** **Truth** **Manager**

||
||
||
||
||
||
||
||
||
||
||

> **5.6** **M-05:** **Detector** **Engine**

||
||
||
||
||
||
||
||
||
||
||

> **5.7** **M-06:** **Benchmark** **Runner**

||
||
||
||
||
||
||

||
||
||
||
||
||
||
||

> **5.8** **M-07:** **Evaluation** **Engine**

||
||
||
||
||
||
||
||
||
||
||

> **5.9** **M-08:** **Scoring** **Engine**

||
||
||
||

||
||
||
||
||
||
||
||
||
||

> **5.10** **M-09:** **Report** **Generator**

||
||
||
||
||
||
||
||
||

||
||
||
||
||
||

> **5.11** **M-10:** **CLI** **Interface**

||
||
||
||
||
||
||
||
||
||
||

> **5.12** **M-11:** **API** **Server**

||
||
||
||
||
||
||

||
||
||
||
||
||
||
||

> **5.13** **M-12:** **Config** **Loader**

||
||
||
||
||
||
||
||
||
||
||

> **5.14** **M-13:** **Registry** **Manager**

||
||
||
||
||
||
||
||
||
||
||

> **5.15** **M-14:** **Job** **Manager**

||
||
||
||
||
||
||
||
||
||

||
||
||
||

> **5.16** **M-15:** **Pipeline** **Controller**

||
||
||
||
||
||
||
||
||
||
||

> **5.17** **M-16:** **State** **Manager**

||
||
||
||
||
||
||
||
||

||
||
||
||
||
||

> **5.18** **M-17:** **Workflow** **Engine**

||
||
||
||
||
||
||
||
||
||
||

> **SECTION** **6** **—** **Data** **Flow** **Architecture**
>
> **6.1** **Analysis** **Pipeline** **Data** **Flow**
>
> User Input (CLI/API) │
>
> ▼ ┌─────────────────┐
>
> │ Config Loader │ ──→ Validated Configuration │ (M-12) │
>
> └────────┬────────┘ │

▼ ┌─────────────────┐

│ Pipeline Ctrl │ ──→ Orchestration │ (M-15) │ └────────┬────────┘

> │ ┌────┴────┐ ▼ ▼

┌────────┐ ┌────────┐ │ Ingest │ │ Registry│ │ (M-01) │ │ (M-13) │
└───┬────┘ └────────┘

> │ ▼

┌─────────────────┐

│ Extract │ ──→ MetricDataFrame │ (M-02) │ └────────┬────────┘

> │ ▼

┌─────────────────┐

│ Segment │ ──→ Window Definitions │ (M-03) │

└────────┬────────┘ │ ▼

┌─────────────────┐

│ Detect │ ──→ DetectorResults │ (M-05) │ └────────┬────────┘

> │ ▼

┌─────────────────┐

│ Score │ ──→ ScorePackage │ (M-08) │ └────────┬────────┘

> │ ▼

┌─────────────────┐

│ Evidence │ ──→ EvidencePackage │ Aggregate │ └────────┬────────┘

> │ ▼

┌─────────────────┐

│ Explain │ ──→ ExplanationReport │ (M-09) │

└────────┬────────┘ │ ▼

┌─────────────────┐

│ Export │ ──→ JSON / Markdown / CSV │ (M-09) │

└─────────────────┘

**6.2** **Benchmark** **Pipeline** **Data** **Flow**

User Input (CLI/API) │

▼ ┌─────────────────┐

│ Benchmark │ ──→ BenchmarkRun │ Runner (M-06) │

> └────────┬────────┘ │ ┌────┴────┐ ▼ ▼
>
> ┌────────┐ ┌────────┐ │ Load │ │ Ground │ │ Dataset│ │ Truth │ │(M-03)
> │ │(M-04) │ └───┬────┘ └────────┘
>
> │ ▼
>
> ┌─────────────────┐
>
> │ Detect │ ──→ Predictions │ (M-05) │ └────────┬────────┘
>
> │ ▼
>
> ┌─────────────────┐
>
> │ Evaluate │ ──→ EvaluationResult │ (M-07) │
>
> └────────┬────────┘ │ ▼
>
> ┌─────────────────┐
>
> │ Report │ ──→ Benchmark Report │ (M-09) │
>
> └─────────────────┘
>
> **6.3** **State** **Transitions**
>
> ***Job*** ***State*** ***Machine*** ***(API*** ***Mode)***
>
> \[CREATED\] ──→ \[QUEUED\] ──→ \[RUNNING\] ──→ \[COMPLETED\] │
>
> ├──→ \[FAILED\] │
>
> └──→ \[CANCELLED\]

||
||
||
||
||
||
||
||
||

> ***Analysis*** ***Stage*** ***State*** ***Machine***
>
> \[INIT\] ──→ \[INGEST\] ──→ \[EXTRACT\] ──→ \[SEGMENT\] ──→ \[DETECT\]
>
> │ ┌──────────────────────────────────────────┘ │
>
> ▼
>
> \[EXPORT\] ←── \[EXPLAIN\] ←── \[EVIDENCE\] ←── \[SCORE\]

||
||
||
||
||
||
||
||
||
||
||
||

> **6.4** **Sequence** **Diagram:** **Repository** **Analysis**
>
> User CLI(M-10) Config(M-12) Pipeline(M-15) Ingest(M-01) Extract(M-02)
> Segment(M-03) Detect(M-05) Score(M-08) Report(M-09)
>
> │ │ │ │ │ │ │ │ │ │
>
> │──analyze──▶│ │ │ │ │ │ │ │ │
>
> │ │──load───▶│ │ │ │ │ │ │ │
>
> │ │◀──config─│ │ │ │ │ │ │ │
>
> │ │───────────│───run──────▶│ │ │ │ │ │ │
>
> │ │ │ │────ingest────▶│ │ │ │ │ │
>
> │ │ │ │◀──repo_ctx────│ │ │ │ │ │
>
> │ │ │ │────extract─────│─────────────▶│ │ │ │ │
>
> │ │ │ │◀─metric_df─────│◀─────────────│ │ │ │ │
>
> │ │ │
>
> │────segment─────│──────────────│──────────────▶│ │ │ │
>
> │ │ │
>
> │◀──windows──────│──────────────│◀─────────────│ │ │ │
>
> │ │ │ │────detect────│──────────────│──────────────│──────────────▶│ │
> │
>
> │ │ │ │◀─det_results──│──────────────│──────────────│◀─────────────│ │
> │
>
> │ │ │
> │────score──────│──────────────│──────────────│──────────────│─────────────▶│
> │
>
> │ │ │
> │◀──scores──────│──────────────│──────────────│──────────────│◀────────────│
> │
>
> │ │ │
> │────evidence───│──────────────│──────────────│──────────────│──────────────│───
> ────────▶│
>
> │ │ │
>
> │◀──package─────│──────────────│──────────────│──────────────│──────────────│◀──
> ─────────│
>
> │ │ │
> │────explain────│──────────────│──────────────│──────────────│──────────────│───
> ────────▶│
>
> │ │ │
> │◀──report──────│──────────────│──────────────│──────────────│──────────────│◀──
> ─────────│
>
> │ │ │
> │────export────│──────────────│──────────────│──────────────│──────────────│────
> ───────▶│
>
> │
> │◀──────────│◀────────────│◀──────────────│──────────────│──────────────│───────
> ───────│──────────────│◀───────────│
>
> │◀──done────│ │ │ │ │ │ │ │ │
>
> **SECTION** **7** **—** **Repository** **Ingestion** **Engine**
>
> **7.1** **Supported** **Sources**

||
||
||
||
||
||

> **7.2** **Repository** **Validation** **Rules**
>
> def validate_repository(path: Path) -\> RepositoryContext: \# Step 1:
> Assert path.exists()
>
> \# Step 2: Assert (path / '.git').is_dir()
>
> \# Step 3: Run 'git rev-parse --git-dir' → must return '.git' \# Step
> 4: Run 'git log --oneline -n 1' → must return non-empty \# Step 5: Run
> 'git log --format=%H' → count commits ≥ 10
>
> \# Step 6: Extract date range: first commit date, last commit date
>
> \# Step 7: Extract contributor count: 'git log --format=%an \| sort -u
> \| wc -l' ≥ 1
>
> \# Step 8: If any check fails → raise specific RepositoryError
>
> **7.3** **Metadata** **Extraction**

||
||
||
||
||

||
||
||
||
||
||
||
||

> **7.4** **Window** **Generation**
>
> Window generation is implemented in M-03 (Segmentation), but ingestion
> provides the raw commit stream. See Section 8 for window strategies.
>
> **7.5** **Time** **Partitioning**
>
> Ingestion extracts all commits with timestamps. Time partitioning is
> performed during segmentation. Ingestion ensures:
>
> All commits have parseable timestamps (ISO 8601).
>
> Commits are sorted chronologically.
>
> Merge commits are optionally excluded based on config.
>
> **7.6** **Error** **Handling**

||
||
||
||
||
||

||
||
||
||
||
||

> **7.7** **Input** **Contracts**
>
> @dataclass
>
> class IngestionInput:
>
> repo_path: str \# Local path or URL
>
> cache_dir: Path = Path.home() / ".miie" / "cache" keep_cache: bool =
> False
>
> shallow_depth: Optional\[int\] = None
>
> **7.8** **Output** **Contracts**
>
> @dataclass
>
> class RepositoryContext: repo_id: str local_path: Path is_remote: bool
> total_commits: int
>
> first_commit_date: datetime last_commit_date: datetime
> contributor_count: int is_shallow: bool
>
> is_fork: bool
>
> **7.9** **Performance** **Constraints**

||
||
||
||
||
||

> **SECTION** **8** **—** **Metric** **Extraction** **Engine**
>
> **8.1** **Extraction** **Logic** **Overview**
>
> The Metric Extraction Engine (M-02) processes a RepositoryContext and
> produces a MetricDataFrame. Extraction is performed metric-by-metric.
> Missing metrics are logged but do not abort extraction.
>
> **8.2** **M-01:** **Code** **Coverage**

||
||
||
||
||
||
||
||
||

> **8.3** **M-02:** **Commit** **Frequency**

||
||
||
||
||
||
||
||

||
||
||
||

> **8.4** **M-03:** **Review** **Participation**

||
||
||
||
||
||
||
||
||

> **8.5** **M-04:** **Review** **Latency**

||
||
||
||
||
||
||
||
||

> **8.6** **M-05:** **Issue** **Resolution** **Time**

||
||
||
||

||
||
||
||
||
||
||
||

> **8.7** **M-06:** **Code** **Churn**

||
||
||
||
||
||
||
||
||

> **8.8** **M-07:** **Cyclomatic** **Complexity**

||
||
||
||
||

||
||
||
||
||
||
||
||

> **8.9** **Missing** **Data** **Handling** **Summary**

||
||
||
||
||
||
||
||
||
||

> **SECTION** **9** **—** **Dataset** **Generation** **Engine**
>
> **9.1** **Synthetic** **Dataset** **Generator**
>
> The Dataset Generator (M-03) creates synthetic repository metric
> histories for benchmark construction. It is used by benchmark
> maintainers, not by end users during standard analysis.
>
> **9.2** **Generation** **Parameters**
>
> @dataclass
>
> class GenerationParameters: \# Repository profile
>
> category: RepositoryCategory \# Enum: small_active, medium_active,
> etc. language: str \# python, java, cpp, javascript, typescript
> duration_days: int \# 90–730
>
> total_commits: int \# 60–2400 contributors: int \# 1–50 bot_ratio:
> float \# 0.0–0.3 window_count: int \# 6–12 window_size_days: int \#
> 30–90
>
> \# Randomness
>
> seed: int \# Default 42
>
> \# Metric generation coverage_mean: float \# 0–100 coverage_std: float
> \# 0–20
>
> commit_freq_lambda: float \# Poisson parameter
> review_participation_mean: float \# 1–5 review_latency_median: float
> \# 1–168 hours issue_resolution_median: float \# 1–90 days churn_mean:
> float \# 10–5000 lines complexity_mean: float \# 1–50

**9.3** **Repository** **Profiles**

Profiles define parameter distributions. See BSD §6.2 for category
definitions. Generation uses these profiles as priors; actual parameters
are sampled from truncated normal distributions around profile means.

**9.4** **Pathology** **Injection** **Framework**

@dataclass

class PathologyConfig:

> event_type: str \# MDE-01, MDE-02, MDE-03 metric_id: str \# M-01 to
> M-07
>
> target_window: int \# Window index where pathology begins severity:
> str \# mild, moderate, severe
>
> \# MDE-01 specific
>
> drift_direction: str \# mean_shift, variance_collapse, shape_change
> drift_magnitude: float \# Effect size
>
> \# MDE-02 specific
>
> metric_pair: Tuple\[str, str\] \# (M-i, M-j)
>
> breakdown_type: str \# sudden_drop, sign_reversal, gradual_erosion
> correlation_change: float \# Delta r
>
> \# MDE-03 specific
>
> threshold: float \# Target threshold value compression_ratio: float \#
> Proportion to compress

**Injection** **Logic:**

> Step 1: Generate clean baseline time series for all metrics across all
> windows.
>
> Step 2: At target_window, modify metric values according to event_type
> and severity.
>
> Step 3: Ensure post-injection values remain in plausible ranges (clamp
> to \[min, max\]).
>
> Step 4: Verify that injected pathology is detectable by reference
> implementation (D-01/D-02/D-03).
>
> Step 5: If not detectable, adjust magnitude and retry (max 10 retries,
> then reject dataset).

**9.5** **Seed** **Handling**

> numpy.random.default_rng(seed) is used for all NumPy random
> operations.
>
> random.seed(seed) is used for Python standard library random
> operations.
>
> Seed is set once at the start of generation and never changed.
>
> Same seed + same parameters → bitwise-identical metrics.json.
>
> **9.6** **Randomness** **Control**
>
> No use of os.urandom() or system entropy for generation.
>
> No multiprocessing that could introduce race conditions in random
> state.
>
> If parallel generation is implemented, each worker gets a derived
> seed: seed + worker_id.
>
> **9.7** **Reproducibility** **Controls**
>
> Generation script is versioned and published.
>
> All parameters are logged in metadata.json.
>
> Output files include generation timestamp and script version.
>
> Checksum (SHA-256) of metrics.json is computed and stored in
> metadata.json.
>
> **9.8** **Dataset** **Export** **Logic**
>
> def export_dataset(dataset: SyntheticDataset, output_dir: Path) -\>
> None: \# Step 1: Write metrics.json per BSD Metric Schema
>
> \# Step 2: Write windows.json per BSD Repository Schema \# Step 3:
> Write metadata.json per BSD Metadata Schema \# Step 4: Compute and
> store checksums
>
> \# Step 5: Validate all files against JSON schemas
>
> **9.9** **Dataset** **Validation**
>
> def validate_dataset(dataset_dir: Path) -\> ValidationResult: \# Step
> 1: Check all required files exist
>
> \# Step 2: Validate JSON schemas
>
> \# Step 3: Verify metric values are in expected ranges
>
> \# Step 4: Verify windows are non-overlapping and ordered \# Step 5:
> Verify checksums match
>
> \# Step 6: Return pass/fail with detailed errors
>
> **SECTION** **10** **—** **Measurement** **Distortion** **Event**
> **Engine**
>
> **10.1** **Event** **Class** **Architecture**
>
> The MDE Engine implements the four frozen event classes from BSD §9.
> It is part of the Detector Engine (M-05) but is architecturally
> separated for clarity.
>
> **10.2** **MDE-01:** **Distributional** **Drift**

||
||
||
||

||
||
||
||
||
||
||
||

> **10.3** **MDE-02:** **Correlation** **Breakdown**

||
||
||
||
||
||
||
||
||

> **10.4** **MDE-03:** **Threshold** **Compression**

||
||
||
||
||

||
||
||
||
||
||
||

> **10.5** **MDE-04:** **No** **Distortion** **Event**

||
||
||
||
||
||
||
||
||

> **SECTION** **11** **—** **Ground** **Truth** **Management**
> **System**
>
> **11.1** **Label** **Lifecycle**
>
> \[INJECTED\] ──→ \[CANDIDATE\] ──→ \[REVIEWED_A\] ──→ \[REVIEWED_B\]
> ──→ \[RESOLVED\] │ │ │ │ │
>
> │ │ │ │ └──→ \[APPROVED\]
>
> │ │ │ │ │
>
> │ │ │ │ └──→ \[REJECTED\]
>
> │ │ │ │
>
> │ │ │ └──→ \[DISAGREEMENT\] ──→ \[ADJUDICATED\]
>
> │ │ │
>
> │ │ └──→ \[MODIFIED\] ──→ \[REVIEWED_B\] │ │
>
> │ └──→ \[AUTO-VALIDATED\] ──→ \[APPROVED\] (if injection verified

by script) │

> └──→ \[REJECTED\] (if injection fails verification)

**11.2** **Annotation** **Storage**

Annotations are stored in annotations.json per dataset:

{

> "repo_id": "repo_001", "annotations": \[
>
> {
>
> "annotation_id": "ann_001", "metric_id": "M-01", "window_id": "w04",
> "event_type": "MDE-01", "label": true,
>
> "severity": "moderate", "evidence": {
>
> "statistical": {"ks_statistic": 0.42, "ks_p_value": 0.003}, "visual":
> \["cdf_w03_w04.png"\],
>
> "rationale": "Clear distribution shift from N(75,10) to N(98,2)." },
>
> "annotator_id": "expert_01", "timestamp": "2026-01-15T10:00:00Z"
>
> } \]

}

**11.3** **Evidence** **Storage**

Evidence files are stored in evidence/ subdirectory:

> cdf_plots/ — CDF comparisons for MDE-01
>
> scatter_plots/ — Correlation scatter plots for MDE-02
>
> histograms/ — Distribution histograms for MDE-03
>
> statistics/ — JSON files with computed test statistics

**11.4** **Reviewer** **Attribution** Every label includes:

> annotator_id: unique identifier of the human annotator.
>
> reviewer_a_id: primary reviewer.
>
> reviewer_b_id: secondary reviewer (blind).
>
> adjudicator_id: third expert (if needed).

**11.5** **Version** **Control**

> Ground truth files are versioned: ground_truth-v1.0.0.json.
>
> Versions are immutable; corrections result in new versions.
>
> Git tags mark benchmark releases: v1.0.0, v1.1.0, etc.
>
> VERSION file in benchmark root records current version.

**11.6** **Conflict** **Resolution** Implemented per BSD §10.4:

> Disagreements trigger adjudication workflow.
>
> Adjudicator decision is final and binding.
>
> Disagreement cases are logged for guideline refinement.

**11.7** **Audit** **Trail**

Every ground truth file includes:

> created_at: timestamp of initial generation.
>
> modified_at: timestamp of last modification.
>
> modification_history: list of all changes with author and rationale.
>
> checksum: SHA-256 of the ground truth data.

**11.8** **Approval** **Workflow**

def approve_ground_truth(annotations: List\[Annotation\]) -\>
GroundTruth: \# Step 1: Verify all positive labels have evidence

> \# Step 2: Compute Cohen's Kappa between reviewers \# Step 3: IF kappa
> \>= 0.80: auto-approve
>
> \# Step 4: IF 0.65 \<= kappa \< 0.80: flag for adjudication \# Step 5:
> IF kappa \< 0.65: reject dataset
>
> \# Step 6: Write approved ground_truth.json with provenance

**SECTION** **12** **—** **Detector** **Engine**

**12.1** **Detector** **Architecture**

All detectors implement a common interface:

class Detector(ABC): @property @abstractmethod

> def detector_id(self) -\> str: ...
>
> @abstractmethod

def detect(self, data: MetricDataFrame, windows: List\[Window\], config:
dict) -\> DetectorResult: ...

> @abstractmethod
>
> def explain(self, result: DetectorResult) -\> ExplanationFragment: ...
>
> **12.2** **D-01:** **Distributional** **Drift** **Detector**

||
||
||
||
||
||
||
||
||
||
||
||

> **12.3** **D-02:** **Correlation** **Breakdown** **Detector**

||
||
||
||
||
||
||

||
||
||
||
||
||
||
||

> **12.4** **D-03:** **Threshold** **Compression** **Detector**

||
||
||
||
||
||
||
||
||
||
||
||

**SECTION** **13** **—** **Benchmark** **Runner**

**13.1** **Execution** **Workflow**

def run_benchmark(suite_id: str, detector_ids: List\[str\], config:
dict, seed: int) -\> BenchmarkRun:

> \# Step 1: Load suite manifest and validate existence \# Step 2: Load
> all datasets in suite
>
> \# Step 3: Load ground truth (hidden from detectors) \# Step 4: For
> each detector:
>
> \# a. Validate compatibility with suite schema \# b. For each dataset:
>
> \# i. Load metrics and windows
>
> \# ii. Run detector (isolated from other datasets) \# iii. Record
> predictions
>
> \# c. Aggregate predictions
>
> \# Step 5: Collect timing and metadata \# Step 6: Return BenchmarkRun

**13.2** **Task** **Scheduling**

> Datasets are processed **sequentially** by default.
>
> Optional: process datasets in parallel using multiprocessing.Pool with
> processes=min(4, cpu_count()).
>
> Each dataset is independent; no shared state between dataset
> processes.
>
> If parallel, each worker gets seed + worker_id to maintain
> determinism.

**13.3** **Dataset** **Loading**

def load_dataset(dataset_dir: Path) -\> Dataset: \# Step 1: Read
metrics.json

> \# Step 2: Read windows.json \# Step 3: Read metadata.json
>
> \# Step 4: Validate against JSON schemas \# Step 5: Return Dataset
> object

**13.4** **Detector** **Invocation**

> Detectors are instantiated once per benchmark run.
>
> Detector configuration is passed at initialization.
>
> Detector receives one dataset at a time.
>
> Detector must not access filesystem outside dataset directory.
>
> Detector must not access ground_truth.json.

**13.5** **Metric** **Collection**

> Benchmark runner collects: prediction (bool), confidence (float,
> optional), execution time (float), memory usage (int, optional).
>
> Predictions are stored in BenchmarkRun.predictions\[dataset_id\]
> \[metric_id\]\[context\].

**13.6** **Result** **Aggregation**

> Per-dataset results are aggregated into per-suite results.
>
> Aggregation is deterministic: sort dataset IDs before iterating.

**13.7** **Benchmark** **Validation**

Before evaluation, the benchmark runner validates:

> All datasets load successfully.
>
> All ground truth labels are present.
>
> Detector predictions match ground truth structure (same keys).
>
> No leakage detected (detector did not access ground truth).

**13.8** **Benchmark** **Reporting**

> Benchmark runner produces benchmark_run.json containing: suite_id,
> detector_id, seed, timestamp
>
> predictions: nested dict of all predictions
>
> timing: per-dataset execution times
>
> metadata: detector version, environment info

**SECTION** **14** **—** **Evaluation** **Engine**

**14.1** **Calculation** **Workflow**

def evaluate(benchmark_run: BenchmarkRun, ground_truth: GroundTruth) -\>
EvaluationResult:

> \# Step 1: Match predictions to labels by (dataset_id, metric_id,
> context) \# Step 2: Compute confusion matrix:
>
> \# TP = predicted=True and label=True \# FP = predicted=True and
> label=False \# TN = predicted=False and label=False \# FN =
> predicted=False and label=True \# Step 3: Compute metrics:
>
> \# accuracy = (TP + TN) / total
>
> \# precision = TP / (TP + FP) if (TP + FP) \> 0 else 0.0 \# recall =
> TP / (TP + FN) if (TP + FN) \> 0 else 0.0

\# f1 = 2 \* precision \* recall / (precision + recall) if (precision +
recall) \> 0 else 0.0

> \# fpr = FP / (FP + TN) if (FP + TN) \> 0 else 0.0 \# fnr = FN / (FN +
> TP) if (FN + TP) \> 0 else 0.0
>
> \# Step 4: Compute AUC-ROC and AUC-PR using sklearn.metrics \# Step 5:
> Aggregate per-dataset and overall
>
> \# Step 6: Return EvaluationResult
>
> **14.2** **Aggregation** **Rules**

||
||
||
||
||
||

> **14.3** **Cross-Dataset** **Aggregation**
>
> All datasets contribute equally to suite-level metrics
> (macro-average).
>
> No dataset is excluded unless it failed to load.
>
> **14.4** **Cross-Task** **Aggregation**
>
> B-01, B-02, B-03 are evaluated independently.
>
> No cross-task metrics are computed in V1.
>
> Future versions may compute aggregate rankings.
>
> **14.5** **Validation** **Checks**
>
> Assert all evaluation metrics ∈ \[0.0, 1.0\].
>
> Assert confusion matrix values are non-negative integers.
>
> Assert TP + FP + TN + FN equals total evaluation instances.
>
> Assert AUC-ROC ≥ 0.5 for any non-random detector.
>
> **SECTION** **15** **—** **Integrity** **Scoring** **Engine**
>
> **15.1** **Architecture**
>
> The Scoring Engine (M-08) is a pure computation module with no
> external dependencies. It receives DetectorResults and produces
> ScorePackage.
>
> **15.2** **Inputs**
>
> @dataclass
>
> class ScoreEngineInput: detector_results: DetectorResults
> metric_dataframe: MetricDataFrame windows: List\[Window\]
>
> detector_weights: Dict\[str, float\] \# {"D-01": 0.40, "D-02": 0.35,
> "D-03": 0.25}

**15.3** **Normalization** **Pipeline**

> 1\. **Severity** **Extraction:** For each detector and metric, extract
> raw severity from detector results.
>
> 2\. **Severity** **Normalization:** Cap severity at 1.0. Ensure
> non-negative.
>
> 3\. **Weight** **Validation:** Sum of weights for enabled detectors
> must equal 1.0. If not, normalize or raise error.
>
> 4\. **Weight** **Redistribution:** If a detector is skipped on a
> metric, redistribute its weight proportionally to other detectors.

**15.4** **Aggregation** **Workflow**

def compute_integrity_score(input: ScoreEngineInput) -\> IntegrityScore:
\# Step 1: For each metric M:

> \# a. Get severity d_1, d_2, d_3 from detector results
>
> \# b. Get weights w_1, w_2, w_3 (redistributed if needed) \# c.
> IS_metric = 1.0 - (w_1\*d_1 + w_2\*d_2 + w_3\*d_3)
>
> \# d. Clamp to \[0, 1\]
>
> \# Step 2: IS_overall = mean(IS_metric for all available M)
>
> \# Step 3: Return IntegrityScore(overall, per_metric, formula_version)

**15.5** **Confidence** **Score** **Pipeline**

def compute_confidence_score(input: ScoreEngineInput) -\>
ConfidenceScore: \# Step 1: Compute f_1 = min(1.0, mean_n / 50.0)

> \# Step 2: Compute f_2 = 1.0 - min(1.0, mean_CV / 0.5)
>
> \# Step 3: Compute f_3 = 1.0 - missing_pairs / total_pairs
>
> \# Step 4: Compute f_4 = 1.0 - min(1.0, std_sizes / mean_sizes) \#
> Step 5: Compute f_5 = successful_runs / total_attempts
>
> \# Step 6: CS = f_1 \* f_2 \* f_3 \* f_4 \* f_5

\# Step 7: Return ConfidenceScore(overall, factors, warnings,
recommendations)

**15.6** **Output** **Schema**

@dataclass

class ScorePackage: integrity: IntegrityScore

> confidence: ConfidenceScore timestamp: datetime config_hash: str

**15.7** **Storage** **Model**

Scores are stored in-memory during analysis and serialized to
results.json by the Report Generator. No separate score database.

**15.8** **Versioning** **Rules**

> Score formula version is included in output: formula_version:
> "v1.0.0".
>
> Formula changes require MIIE version bump and TFS amendment.
>
> Backward compatibility: old results include old formula version; new
> analyses use new version.
>
> **SECTION** **16** **—** **Storage** **Architecture**
>
> **16.1** **Directory** **Structure**
>
> ~/.miie/
>
> ├── config.yaml \# User configuration ├── cache/
>
> │ ├── repos/
>
> │ │ ├── {repo_id}/ \# Cloned repositories │ │ └── ...
>
> │ └── cleanup.log \# Auto-cleanup timestamps ├── benchmarks/
>
> │ ├── metric-drift-v1.0.0/

│ ├── correlation-breakdown-v1.0.0/ │ └── threshold-compression-v1.0.0/

> ├── jobs/ \# API job state (if API used) │ └── {job_id}/
>
> │ ├── manifest.json │ ├── state.json
>
> │ └── results/ ├── registries/
>
> │ ├── metrics.json │ └── detectors.json └── logs/
>
> └── miie.log
>
> User-specified output directory:
>
> {output_dir}/ ├── manifest.json ├── results.json ├── report.md ├──
> metrics.csv ├── evidence.json
>
> └── run_metrics.json

\# Run metadata

\# Full structured result \# Human-readable report \# Tabular raw data

\# Evidence package

\# Performance metrics

> **16.2** **Data** **Layout**

||
||
||
||
||
||
||
||
||
||

**16.3** **Cache** **Strategy**

> Cache directory size limit: 5GB (configurable).
>
> LRU eviction when limit exceeded.
>
> --keep-cache flag prevents eviction for specific repo.
>
> Cleanup runs on startup if cache \> limit.

**16.4** **Backup** **Strategy**

> No automatic backup of user output directories.
>
> Job state is transient; users must download results before cleanup.
>
> Benchmark suites should be backed up by maintainers (Git repository).

**SECTION** **17** **—** **Data** **Schemas**

**17.1** **Repository** **Metadata** **Schema**

{

> "repo_id": "string (required)", "local_path": "string (required)",
> "is_remote": "boolean (required)", "remote_url": "string (optional)",
> "total_commits": "integer (required, \>= 10)",
>
> "first_commit_date": "string (ISO 8601, required)",
> "last_commit_date": "string (ISO 8601, required)",
> "contributor_count": "integer (required, \>= 1)", "is_shallow":
> "boolean (required)",
>
> "is_fork": "boolean (required)", "language_distribution": "object
> (optional)"

}

**17.2** **Metrics** **Schema**

{

> "repo_id": "string (required)", "run_id": "string (required)",
>
> "timestamp": "string (ISO 8601, required)", "metrics": \[
>
> {
>
> "metric_id": "string (enum: M-01..M-07, required)", "commit_hash":
> "string (optional)",
>
> "window_id": "string (optional)", "timestamp": "string (ISO 8601,
> optional)", "value": "number or null (required)", "unit": "string
> (optional)"
>
> } \]

}

**17.3** **Ground** **Truth** **Schema** See BSD §14.4 (identical).

**17.4** **Annotations** **Schema** See BSD §14.3 (identical).

**17.5** **Detectors** **Schema**

{

> "detector_id": "string (enum: D-01..D-03, required)", "detector_name":
> "string (required)",
>
> "description": "string (required)", "statistical_method": "string
> (required)", "assumptions": \["string"\], "configurable_parameters": {
>
> "parameter_name": { "type": "string", "default": "any",
>
> "range": "string (optional)" }
>
> },

"version": "string (required)" }

**17.6** **Evaluation** **Results** **Schema** See BSD §14.5
(identical).

**17.7** **Reports** **Schema**

{

> "report_type": "string (enum: analysis, benchmark, explanation,
> required)", "miie_version": "string (required)",
>
> "generated_at": "string (ISO 8601, required)", "config_hash": "string
> (required)", "content": {
>
> "json": "object (optional)", "markdown": "string (optional)", "csv":
> "string (optional)"

} }

**17.8** **Benchmark** **Runs** **Schema**

{

> "run_id": "string (required)", "suite_id": "string (required)",
> "detector_id": "string (required)", "detector_version": "string
> (required)", "seed": "integer (required)",
>
> "started_at": "string (ISO 8601, required)", "completed_at": "string
> (ISO 8601, required)", "predictions": "object (required)",
>
> "timing": "object (required)", "environment": "object (required)"

}

**17.9** **Version** **Manifests** **Schema**

{

> "miie_version": "string (required)", "release_date": "string (ISO
> 8601, required)",
>
> "commit_hash": "string (required)", "compatible_benchmarks":
> \["string"\], "schema_versions": {
>
> "repository": "string", "metrics": "string", "ground_truth": "string",
> "evaluation": "string"

} }

**SECTION** **18** **—** **API** **Architecture**

**18.1** **Internal** **API** **Design**

Even though V1 is CLI-primary, internal APIs are defined for modularity
and to support the optional REST layer.

**18.2** **Service:** **AnalysisService**

class AnalysisService:

> def analyze(self, request: AnalyzeRequest) -\> AnalysisResult: \#
> Execute full analysis pipeline.

def explain(self, job_id: str, metric_id: Optional\[str\], detector_id:
Optional\[str\]) -\> ExplanationReport:

> \# Generate explanation from existing analysis.

def export(self, job_id: str, formats: List\[str\], filter:
Optional\[str\]) -\> ExportResult:

> \# Export existing analysis in specified formats.

**18.3** **Service:** **BenchmarkService**

class BenchmarkService:

> def run_benchmark(self, request: BenchmarkRequest) -\> BenchmarkRun:
> \# Execute benchmark suite against detector.
>
> def evaluate(self, run_id: str) -\> EvaluationResult: \# Evaluate
> benchmark run against ground truth.
>
> def list_suites(self) -\> List\[SuiteInfo\]: \# List available
> benchmark suites.

**18.4** **Service:** **RegistryService**

class RegistryService:

> def get_metric(self, metric_id: str) -\> MetricDefinition: \# Lookup
> metric definition.
>
> def get_detector(self, detector_id: str) -\> DetectorDefinition: \#
> Lookup detector definition.
>
> def list_metrics(self) -\> List\[MetricDefinition\]: \# List all
> registered metrics.
>
> def list_detectors(self) -\> List\[DetectorDefinition\]: \# List all
> registered detectors.
>
> **18.5** **Endpoint** **Specifications**
>
> See TFS §14.3 for REST endpoint mapping. Internal APIs use the same
> request/response schemas.
>
> **18.6** **Error** **Responses**
>
> All services return Result\[T, Error\] pattern:
>
> @dataclass
>
> class Result(Generic\[T\]): value: Optional\[T\] error:
> Optional\[Error\]
>
> @dataclass class Error:
>
> code: str \# e.g., "INVALID_REPO", "DETECTOR_FAILED" message: str
>
> suggestion: str
>
> **18.7** **Validation** **Rules**
>
> All inputs validated against JSON schemas before processing.
>
> Unknown fields rejected (strict schema).
>
> Missing required fields raise ValidationError.
>
> Type coercion attempted for numeric fields; failure raises
> ValidationError.
>
> **18.8** **Versioning** **Rules**
>
> Internal API versions match MIIE version.
>
> Breaking changes require major version bump.
>
> All schemas versioned independently.
>
> **SECTION** **19** **—** **CLI** **Architecture**
>
> **19.1** **Command** **Structure**
>
> miie \[global-options\] \<command\> \[command-options\] \[arguments\]
>
> **19.2** **Global** **Options**

||
||
||
||
||
||
||

||
||
||
||

> **19.3** **miie** **ingest**
>
> **Purpose:** Ingest and validate a repository without running
> analysis.

||
||
||
||
||
||

> **Output:** RepositoryContext printed as JSON to stdout.
>
> **Exit** **Codes:** 0 (success), 2 (system error), 3 (invalid repo).
>
> **Example:**
>
> miie ingest --repo https://github.com/org/repo.git --shallow 100
>
> **19.4** **miie** **analyze**
>
> See TFS §13.3 for full specification. Summary:

||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **Exit** **Codes:** 0 (no failures), 1 (failures detected), 2 (error),
> 3 (invalid args).
>
> **Example:**
>
> miie analyze --repo ./my-repo --since 2025-01-01 --metrics M-01,M-02
> --window-
>
> strategy time --window-size 90 -o ./output/
>
> **19.5** **miie** **generate**
>
> **Purpose:** Generate synthetic benchmark datasets (maintainer
> command).

||
||
||
||
||
||
||
||

> **Exit** **Codes:** 0 (success), 2 (error), 3 (invalid args).
>
> **Example:**
>
> miie generate --profile medium_active --count 10 --output
> ./benchmarks/ --seed 42
>
> **19.6** **miie** **detect**
>
> **Purpose:** Run detectors on pre-extracted metrics
> (debugging/advanced).

||
||
||
||
||
||
||

> **Exit** **Codes:** 0 (success), 2 (error), 3 (invalid args).
>
> **Example:**
>
> miie detect --input ./metrics.json --windows ./windows.json
> --detectors D-01,D-03
>
> **19.7** **miie** **benchmark**
>
> See TFS §13.4 for full specification.

||
||
||
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
> **19.8** **miie** **evaluate**
>
> **Purpose:** Evaluate a benchmark run against ground truth.

||
||
||
||
||
||

> **Exit** **Codes:** 0 (success), 2 (error), 3 (invalid args).
>
> **Example:**
>
> miie evaluate --run ./benchmark-run.json --ground-truth
> ./ground-truth.json
>
> **19.9** **miie** **explain**
>
> See TFS §13.5 for full specification.

||
||
||
||
||
||
||

> **Exit** **Codes:** 0 (success), 3 (invalid input).
>
> **19.10** **miie** **export**
>
> See TFS §13.6 for full specification.

||
||
||
||
||
||
||

> **Exit** **Codes:** 0 (success), 3 (invalid args).
>
> **19.11** **Exit** **Codes** **Summary**

||
||
||
||
||
||
||
||

> **SECTION** **20** **—** **Reporting** **Engine**
>
> **20.1** **JSON** **Reports**
>
> **Template:** report_json.jinja2 (not used — JSON is serialized
> directly)
>
> **Structure:**
>
> {
>
> "miie_version": "1.0.0", "generated_at": "2026-06-07T00:00:00Z",
> "config_hash": "a1b2c3...", "repository": { ... },
>
> "windows": \[ ... \], "metrics": { ... }, "detector_results": { ... },
> "scores": {
>
> "integrity": { "overall": 0.72, "per_metric": { ... } }, "confidence":
> { "overall": 0.68, "factors": { ... } }
>
> },
>
> "evidence": { ... }, "explanations": \[ ... \]
>
> }

**20.2** **CSV** **Reports**

**Template:** report_csv.jinja2

**Structure:**

metric_id,window_id,value,integrity_score,confidence_score,drift_detected,correl
ation_breakdown,threshold_compression

M-01,w01,0.85,0.72,0.68,false,false,false ...

**20.3** **Markdown** **Reports** **Template:** report_md.jinja2

**Sections:**

> 1\. Header (title, timestamp, version)
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

**20.4** **Benchmark** **Reports** **Template:** benchmark_md.jinja2

**Sections:**

> 1\. Benchmark Summary (suite, detector, seed)
>
> 2\. Confusion Matrix (table)
>
> 3\. Metrics Table (accuracy, precision, recall, F1, AUC-ROC, AUC-PR,
> FPR, FNR)
>
> 4\. Per-Dataset Breakdown (table)
>
> 5\. Baseline Comparison (table)
>
> 6\. Methodology Notes

**20.5** **Detector** **Reports** **Template:** detector_md.jinja2

**Sections:**

> 1\. Detector Configuration
>
> 2\. Detection Results (per metric/window)
>
> 3\. Statistical Evidence
>
> 4\. Runtime Performance

**20.6** **Evaluation** **Reports** **Template:** evaluation_md.jinja2

**Sections:**

> 1\. Evaluation Summary
>
> 2\. Metric Definitions
>
> 3\. Results Tables
>
> 4\. ROC/PR Curve Data (JSON for external plotting)

**20.7** **Version** **Reports** **Template:** version_md.jinja2

**Sections:**

> 1\. MIIE Version
>
> 2\. Compatible Benchmarks
>
> 3\. Schema Versions
>
> 4\. Dependency Versions

**SECTION** **21** **—** **Reproducibility** **Framework**

**21.1** **Seed** **Management**

class SeedManager:

> def \_\_init\_\_(self, seed: int = 42): self.seed = seed
>
> self.rng = np.random.default_rng(seed) random.seed(seed)
>
> def get_rng(self) -\> np.random.Generator: return self.rng
>
> def get_seed(self) -\> int: return self.seed
>
> Seed is set at application startup.
>
> All stochastic modules receive SeedManager instance.
>
> No module creates independent random state without seed.

**21.2** **Environment** **Control**

> requirements.txt and poetry.lock pin all dependencies.
>
> Docker image (optional) provides frozen environment.
>
> CI tests verify reproducibility on clean environments.

**21.3** **Dependency** **Locking**

\[tool.poetry.dependencies\] python = "^3.10"

numpy = "1.24.3" pandas = "2.0.3" scipy = "1.11.1" jinja2 = "3.1.2"
click = "8.1.3" fastapi = "0.100.0"

**21.4** **Artifact** **Tracking**

Every run produces manifest.json:

{

> "miie_version": "1.0.0", "git_commit": "abc123", "python_version":
> "3.10.12", "dependency_hash": "sha256:...", "config_hash":
> "sha256:...", "seed": 42,
>
> "timestamp": "2026-06-07T00:00:00Z", "platform": "linux-x86_64"

}

**21.5** **Dataset** **Versioning**

> Datasets include metadata.json with generation parameters and
> checksums.
>
> Benchmark suites include manifest.json with version and schema info.
>
> Ground truth includes version and annotation metadata.

**21.6** **Experiment** **Tracking**

> No external experiment tracking service (MLflow, WandB).
>
> Tracking is file-based: run_metrics.json in output directory.
>
> run_metrics.json includes: duration, memory peak, CPU time, stage
> timings.

**21.7** **Result** **Reproduction** To reproduce any result:

\# Step 1: Install exact versions pip install -r requirements.txt

\# Step 2: Run with exact config and seed

miie analyze --repo {repo} --config {config} --seed 42

\# Step 3: Compare manifest.json and results.json

**21.8** **Audit** **Process**

> **CI** **Reproducibility** **Test:** Re-run analysis twice; compare
> MD5 of results.json.
>
> **Benchmark** **Reproducibility** **Test:** Re-run benchmark twice;
> compare evaluation metrics.
>
> **Quarterly** **Audit:** Full regeneration of one benchmark suite;
> compare checksums.
>
> **SECTION** **22** **—** **Performance** **Requirements**
>
> **22.1** **Maximum** **Dataset** **Size**

||
||
||
||
||
||
||

> **22.2** **Maximum** **Runtime**

||
||
||
||
||
||
||
||

> **22.3** **Maximum** **Memory**

||
||
||
||
||
||

> **22.4** **Expected** **Throughput**

||
||
||
||
||
||
||

> **22.5** **Benchmark** **Runtime** **Targets**

||
||
||
||
||
||

> **22.6** **Detector** **Runtime** **Targets**

||
||
||
||
||
||

> **SECTION** **23** **—** **Reliability** **Requirements**
>
> **23.1** **Availability** **Requirements**
>
> CLI tool: No availability requirement (batch execution).
>
> API server: If running, must respond to /health within 1 second.
>
> No SLA guarantees; this is research infrastructure, not production
> service.
>
> **23.2** **Recovery** **Requirements**
>
> **Partial** **results:** If analysis aborts mid-pipeline, save
> completed stages to output directory.
>
> **Resume:** Not supported in V1. User must re-run from start.
>
> **Cache** **recovery:** If cache corrupted, delete and re-clone.
>
> **23.3** **Validation** **Requirements**
>
> All inputs validated against JSON schemas before processing.
>
> All outputs validated against schemas before writing.
>
> All metric values validated for range and type.
>
> All detector results validated for consistency.
>
> **23.4** **Data** **Integrity** **Requirements**
>
> Output files include checksums in manifest.
>
> JSON outputs use deterministic key ordering (sort_keys=True).
>
> CSV outputs use consistent column ordering.
>
> No data mutation after initial extraction.

**23.5** **Error** **Handling** **Standards**

> All exceptions caught at CLI/API boundary.
>
> Error messages include: code, description, suggestion.
>
> Fatal errors exit with non-zero code; partial results saved if
> possible.
>
> Warnings logged but do not abort execution.

**23.6** **Logging** **Standards**

> Log format: {timestamp} \[{level}\] {module}: {message}
>
> Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
>
> DEBUG: detailed progress, statistical values, internal state
>
> INFO: stage transitions, high-level progress
>
> WARNING: skipped metrics, insufficient data, non-fatal issues
>
> ERROR: failed stages, exceptions, validation failures
>
> CRITICAL: unrecoverable errors, data corruption
>
> Logs written to stderr (CLI) and file (API).

**23.7** **Audit** **Standards**

> Every analysis run produces manifest.json with full provenance.
>
> Every benchmark run produces run_manifest.json with environment info.
>
> All configuration changes logged.
>
> All detector skips logged with reason.

**SECTION** **24** **—** **Security** **Requirements**

**24.1** **Input** **Validation**

> All file paths resolved via pathlib.Path.resolve() to prevent
> traversal.
>
> URL validation: scheme must be https or ssh; no file:// or
> javascript://.
>
> JSON/YAML parsing uses safe loaders (no arbitrary code execution).
>
> Metric values validated as numeric before statistical operations.

**24.2** **File** **Validation**

> Coverage artifact parsers validate XML structure before extraction.
>
> PR/issue exports validated against expected schema.
>
> Unknown fields rejected (strict mode).
>
> File size limits: JSON exports \< 1GB; abort if exceeded.

**24.3** **Execution** **Safety**

> No eval(), exec(), or dynamic code execution of user input.
>
> Git commands executed via subprocess with sanitized arguments.
>
> Static analysis tools (radon, lizard) run in subprocess isolation.
>
> No network requests during analysis (except initial clone).

**24.4** **Dependency** **Security**

> All dependencies from PyPI with verified hashes.
>
> No dependencies with known CVEs (checked via safety or pip-audit).
>
> Minimum supported versions specified to avoid vulnerable old versions.

**24.5** **Artifact** **Integrity**

> results.json includes SHA-256 of evidence and raw metrics.
>
> Benchmark datasets include checksums in metadata.
>
> Ground truth files include checksums.
>
> Checksum verification optional but recommended.

**24.6** **Checksum** **Verification**

def verify_checksum(file_path: Path, expected: str) -\> bool: actual =
hashlib.sha256(file_path.read_bytes()).hexdigest() return
hmac.compare_digest(actual, expected)

**SECTION** **25** **—** **Open** **Source** **Architecture**

**25.1** **Repository** **Structure**

miie/

├── .github/

│ ├── workflows/

│ │ ├── ci.yml \# Test, lint, coverage │ │ └── release.yml \# PyPI
publish

│ ├── ISSUE_TEMPLATE/

│ └── PULL_REQUEST_TEMPLATE.md ├── src/

│ └── miie/

│ ├── \_\_init\_\_.py

│ ├── \_\_main\_\_.py \# python -m miie

│ ├── cli.py \# M-10: CLI Interface │ ├── api.py \# M-11: API Server

> │ ├── config.py \# M-12: Config Loader
>
> │ ├── registry.py \# M-13: Registry Manager │ ├── orchestration/
>
> │ │ ├── \_\_init\_\_.py
>
> │ │ ├── pipeline.py \# M-15: Pipeline Controller │ │ ├── job.py \#
> M-14: Job Manager
>
> │ │ ├── state.py \# M-16: State Manager │ │ └── workflow.py \# M-17:
> Workflow Engine │ ├── processing/
>
> │ │ ├── \_\_init\_\_.py
>
> │ │ ├── ingestion.py \# M-01: Repository Ingestion │ │ ├──
> extraction.py \# M-02: Metric Extraction │ │ ├── segmentation.py \#
> Window Segmentation
>
> │ │ ├── detection.py \# M-05: Detector Engine │ │ ├── scoring.py \#
> M-08: Scoring Engine │ │ └── evidence.py \# Evidence Aggregation │ ├──
> benchmark/
>
> │ │ ├── \_\_init\_\_.py
>
> │ │ ├── generator.py \# M-03: Dataset Generator
>
> │ │ ├── ground_truth.py \# M-04: Ground Truth Manager │ │ ├──
> runner.py \# M-06: Benchmark Runner
>
> │ │ └── evaluation.py \# M-07: Evaluation Engine │ ├── reporting/
>
> │ │ ├── \_\_init\_\_.py
>
> │ │ ├── templates/ \# Jinja2 templates
>
> │ │ └── generator.py \# M-09: Report Generator │ └── schemas/ \# JSON
> schemas
>
> ├── tests/
>
> │ ├── unit/
>
> │ ├── integration/ │ └── benchmark/ ├── docs/
>
> │ ├── usage.md │ ├── api.md
>
> │ └── benchmark.md
>
> ├── benchmarks/ \# MIB-SE suites (git submodule or separate repo) ├──
> pyproject.toml
>
> ├── poetry.lock
>
> ├── requirements.txt ├── README.md
>
> ├── LICENSE
>
> ├── CONTRIBUTING.md └── CODE_OF_CONDUCT.md
>
> **25.2** **Documentation** **Structure**

||
||
||
||
||
||
||
||

> **25.3** **Contribution** **Workflow** 1. Fork repository.
>
> 2\. Create feature branch: feature/description or fix/description.
>
> 3\. Write code with tests (≥80% coverage).
>
> 4\. Run linting: black, flake8, mypy.
>
> 5\. Submit pull request with description and test results.
>
> 6\. CI runs tests and linting.
>
> 7\. Maintainer review (minimum 1 approval).
>
> 8\. Merge to main.
>
> **25.4** **Release** **Workflow**
>
> 1\. Update VERSION and CHANGELOG.md.
>
> 2\. Create release branch: release/v1.0.x.
>
> 3\. Run full test suite and benchmark validation.
>
> 4\. Tag release: git tag v1.0.0.
>
> 5\. Build package: poetry build.
>
> 6\. Publish to PyPI: poetry publish.
>
> 7\. Create GitHub release with notes.
>
> 8\. Announce on mailing list.
>
> **25.5** **Version** **Governance**
>
> MIIE version follows semantic versioning: MAJOR.MINOR.PATCH.
>
> Major: breaking changes to CLI, API, or schemas.
>
> Minor: new features (not permitted in V1 freeze).
>
> Patch: bug fixes, documentation updates.
>
> V1 is frozen; only patch releases expected.
>
> **25.6** **Issue** **Workflow**

||
||
||
||
||
||
||
||
||

> **SECTION** **26** **—** **Risks** **And** **Technical** **Debt**
>
> **26.1** **Architecture** **Risks**

||
||
||
||
||
||

> **26.2** **Performance** **Risks**

||
||
||
||
||
||

> **26.3** **Benchmark** **Risks**

||
||
||
||
||

||
||
||
||
||

> **26.4** **Reproducibility** **Risks**

||
||
||
||
||
||

> **26.5** **Maintenance** **Risks**

||
||
||
||
||
||

> **SECTION** **27** **—** **Team** **Execution** **Mapping**
>
> **27.1** **Team** **Composition**

||
||
||
||
||
||

> **27.2** **Ownership** **Matrix**

||
||
||
||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||

> **27.3** **Milestones**

||
||
||
||
||
||
||
||
||
||
||
||
||

> **27.4** **Review** **Responsibilities**
>
> **Engineer** **A** **reviews:** M-03, M-04, M-06, M-07, M-08
>
> **Engineer** **B** **reviews:** M-09, M-10, M-11, M-12, M-13, M-14,
> M-15, M-16, M-17
>
> **Engineer** **C** **reviews:** M-01, M-02, M-05

**SECTION** **28** **—** **Build** **Roadmap**

**28.1** **Phase** **1:** **Core** **Infrastructure** **(Weeks**
**1–2)** **Deliverables:**

> Project scaffolding (Poetry, pytest, black, mypy, CI)
>
> M-12 (Config Loader) with full schema validation
>
> M-13 (Registry Manager) with frozen M-01–M-07 and D-01–D-03
>
> M-15 (Pipeline Controller) with stage orchestration
>
> M-16 (State Manager) with filesystem-based job state
>
> CI pipeline with matrix testing (Linux, macOS, WSL)

**Dependencies:** None

**Exit** **Criteria:**

> pytest passes with ≥80% coverage on scaffolding.
>
> Config loader validates all TFS configuration examples.
>
> Registry loads without errors.

**28.2** **Phase** **2:** **Dataset** **System** **(Weeks** **3–4)**
**Deliverables:**

> M-01 (Repository Ingestion) with clone, validation, metadata
> extraction
>
> M-02 (Metric Extraction) with all 7 metrics
>
> M-03 (Window Segmentation) with time/commit/release/custom strategies
>
> Synthetic dataset generator (M-03 benchmark variant) with 5 sample
> datasets

**Dependencies:** Phase 1

**Exit** **Criteria:**

> Successfully ingest and extract metrics from 10 real repositories.
>
> All 7 metrics produce valid DataFrames.
>
> Window segmentation produces non-overlapping, ordered windows.

**28.3** **Phase** **3:** **Detector** **Engine** **(Weeks** **5–7)**
**Deliverables:**

> D-01 implementation with KS + PSI
>
> D-02 implementation with Pearson + Spearman + Fisher z
>
> D-03 implementation with excess mass + dip test
>
> M-05 (Detector Engine) with common interface and error handling
>
> Evidence aggregation pipeline

**Dependencies:** Phase 2

**Exit** **Criteria:**

> All detectors run on sample datasets without errors.
>
> Detector outputs match TFS example calculations (within 1e-9).
>
> Evidence packages include all required fields.

**28.4** **Phase** **4:** **Benchmark** **Engine** **(Weeks** **8–10)**
**Deliverables:**

> M-03 (Dataset Generator) full implementation with all 7 categories
>
> M-04 (Ground Truth Manager) with annotation workflow
>
> M-06 (Benchmark Runner) with suite loading and detector invocation
>
> M-07 (Evaluation Engine) with all 8 metrics
>
> 3 complete benchmark suites (B-01, B-02, B-03) with 50/40/30 datasets

**Dependencies:** Phase 3

**Exit** **Criteria:**

> All 120 datasets generated and validated.
>
> Ground truth κ ≥ 0.80 on all suites.
>
> Benchmark runner completes full suite in \< 10 minutes.
>
> Evaluation engine produces correct metrics on known test cases.

**28.5** **Phase** **5:** **Evaluation** **System** **(Weeks**
**11–13)** **Deliverables:**

> M-08 (Scoring Engine) with IS and CS formulas
>
> M-09 (Report Generator) with JSON, Markdown, CSV exports
>
> M-10 (CLI Interface) with all commands
>
> M-17 (Workflow Engine) with 5 frozen workflows
>
> End-to-end integration tests

**Dependencies:** Phase 4

> **Exit** **Criteria:**
>
> Integrity and Confidence Scores match TFS example calculations
> exactly.
>
> CLI commands produce correct exit codes and outputs.
>
> Reports are human-readable and machine-parseable.
>
> Integration tests cover all 5 workflows.
>
> **28.6** **Phase** **6:** **Release** **Candidate** **(Weeks**
> **14–16)** **Deliverables:**
>
> M-11 (API Server) with all endpoints
>
> M-14 (Job Manager) with async execution
>
> Full documentation (README, usage guide, API docs)
>
> Performance optimization and profiling
>
> Security audit (dependency check, input validation)
>
> Reproducibility verification (bitwise-identical re-runs)
>
> Open source release (PyPI, GitHub)
>
> **Dependencies:** Phase 5
>
> **Exit** **Criteria:**
>
> All 19 TFS functional requirements implemented and tested.
>
> All 3 BSD benchmark suites pass with target precision/recall.
>
> Test coverage ≥ 80%.
>
> Reproducibility test passes (bitwise-identical JSON).
>
> CI passes on all platforms.
>
> Documentation complete.
>
> **SECTION** **29** **—** **TRD** **Readiness** **Audit**
>
> **29.1** **Audit** **Results**

||
||
||
||
||

||
||
||
||
||
||
||
||
||

> **29.2** **Residual** **Items**
>
> The following are engineering decisions, not ambiguities:

||
||
||
||
||
||
||

||
||
||
||
||
||

> **SECTION** **30** **—** **FINAL** **ENGINEERING** **VERDICT**
>
> **30.1** **Question**
>
> **Can** **three** **independent** **teams** **build** **equivalent**
> **MIIE** **systems** **using** **this** **TRD?**
>
> **30.2** **Answer** **YES**
>
> **30.3** **Justification**

Three independent engineering teams using IPD v1.1, PRD v1.0, TFS v1.0,
BSD v1.0, and this TRD v1.0 would produce systems that are functionally
equivalent in the following dimensions:

> 1\. **Architecture:** All teams would implement the same 6-layer
> architecture with the same 18 modules and responsibilities.
>
> 2\. **Data** **Flow:** All teams would implement the same pipeline
> sequence: ingestion → extraction → segmentation → detection → scoring
> → evidence → explanation → export.
>
> 3\. **Detectors:** All teams would implement D-01, D-02, D-03 with the
> same statistical methods, thresholds, and pseudocode from TFS §5.
>
> 4\. **Scoring:** All teams would compute identical Integrity Scores
> and Confidence Scores using the frozen formulas from TFS §6–7.
>
> 5\. **CLI:** All teams would implement the same commands, flags,
> arguments, exit codes, and error messages from TFS §13.
>
> 6\. **API:** All teams would expose the same endpoints,
> request/response schemas, and status codes from TFS §14.
>
> 7\. **Benchmarks:** All teams would generate/evaluate the same 120
> datasets, 3 suites, and 8 evaluation metrics per BSD.
>
> 8\. **Storage:** All teams would use the same directory structure and
> file formats.
>
> 9\. **Reproducibility:** All teams would achieve bitwise-identical
> outputs given identical inputs, seeds, and configurations.
>
> 10.**Reports:** All teams would produce the same JSON, Markdown, and
> CSV output structures.
>
> **30.4** **Declaration**
>
> **IMPLEMENTATION** **PHASE** **APPROVED.**
>
> MIIE v1.0 is ready for implementation. The TRD provides sufficient
> detail for three independent engineering teams to build functionally
> equivalent systems without further clarification.
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

> **APPENDIX** **C** **—** **Module-to-Document** **Traceability**

||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **END** **OF** **TRD** **v1.0**
