**Implementation** **Master** **Plan** **(IMP** **v1.0)**
**Measurement** **Integrity** **Intelligence** **Engine** **(MIIE)**

**Version:** 1.0.0 **Date:** 2026-06-07

**Status:** Implementation Authority — Ready for Development **Team**
**Size:** 3 FTEs

**Build** **Window:** 16 Weeks (4 weeks MIFS + 12 weeks Engineering)

**Sources:** IPD v1.1 FINAL \| PRD v1.0 \| TFS v1.0 \| BSD v1.0 \| TRD
v1.0 \| AFD v1.0 \| BSD-Engineering v1.0 \| ACS v1.0

**SECTION** **1** **—** **Executive** **Summary**

**1.1** **Project** **Name**

Measurement Integrity Intelligence Engine (MIIE) Version 1.0.0

**1.2** **Mission**

Build the first open-source, research-grade system that automatically
detects when software engineering metrics cease to be trustworthy
representations of the constructs they claim to measure. MIIE v1.0
produces deterministic Integrity Scores (IS), Confidence Scores (CS),
evidence packages, and rule-based explanations for seven frozen metrics
using three frozen statistical detectors.

**1.3** **Implementation** **Objective**

Deliver a pip-installable Python package (miie) with a CLI-first
interface, optional REST API, and three frozen benchmark suites (B-01,
B-02, B-03) that enable peer-reviewed validation of detector
performance. The system must achieve bitwise-identical reproducibility
given identical inputs, configuration, and seed.

**1.4** **Version** **Scope** **(Frozen)** **In** **Scope:**

> Repository ingestion (M-01) for Git local/remote repos
>
> Metric extraction (M-02) for 7 frozen metrics (M-01..M-07)
>
> Window segmentation (M-03) with time/commit/release/custom strategies
>
> Three frozen detectors (D-01: KS+PSI drift, D-02: Pearson+Spearman
> breakdown, D-03: excess mass+dip compression)
>
> Integrity Score and Confidence Score computation (M-08)
>
> Evidence aggregation and rule-based explanation generation (M-09)
>
> Report generation in JSON, Markdown, and CSV (M-09)
>
> CLI interface with 8 commands (M-10)
>
> REST API with 6 endpoints (M-11)
>
> Configuration loader (M-12), Registry manager (M-13), Job manager
> (M-14), Pipeline controller (M-15), State manager (M-16), Workflow
> engine (M-17)
>
> Dataset generator (M-03 GEN variant) and Ground Truth manager (M-04)
>
> Benchmark runner (M-06) and Evaluation engine (M-07)
>
> 120 synthetic datasets across 3 benchmark suites (B-01: 50, B-02: 40,
> B-03: 30)

**Explicitly** **Excluded** **(Frozen):**

> Productivity tracking, developer ranking, employee monitoring
>
> Real-time streaming, SaaS/multi-tenancy, database persistence
>
> GUI/web interface, authentication systems beyond minimal API key
>
> Automated enforcement (CI gates), KPI dashboards
>
> LLM-based explanations
>
> Additional metrics beyond M-01..M-07 or detectors beyond D-01..D-03

**1.5** **Expected** **Deliverables**

> 1\. miie Python package (PyPI) with CLI entry point
>
> 2\. Docker image with frozen dependencies
>
> 3\. Three benchmark suites in ~/.miie/benchmarks/
>
> 4\. Complete test suite (\>90% coverage on core engine)
>
> 5\. Documentation: README, usage guide, API reference, benchmark
> handbook
>
> 6\. Paper 1 artifact package (ICSE/MSR-ready)
>
> 7\. Open-source repository with CI/CD, issue templates, and
> contribution guidelines

**1.6** **Final** **Success** **Definition**

Three engineers can start on Day 1 using only this IMP and the approved
document stack, build functionally equivalent modules that integrate
correctly, pass all contract tests (CT-01..CT-17), schema tests
(ST-01..ST-10), workflow tests (WT-01..WT-07), benchmark tests
(BT-01..BT-05), and achieve the following hard targets:

> D-01: Precision ≥ 0.80, Recall ≥ 0.75 on B-01
>
> D-02: Precision ≥ 0.75, Recall ≥ 0.70 on B-02
>
> D-03: Precision ≥ 0.85, Recall ≥ 0.80 on B-03
>
> Cohen's Kappa ≥ 0.80 on all benchmark suites
>
> Test coverage ≥ 90% on core engine
>
> Bitwise-identical reproducibility on all benchmark re-runs
>
> CLI passes usability test: new user runs first analysis in \< 15
> minutes

**SECTION** **2** **—** **Implementation** **Philosophy**

**2.1** **Benchmark** **First**

**Rule:** No detector code is written before the benchmark dataset
exists.

**Execution:** Weeks 1-4 (MIFS) freeze the benchmark dataset before
detector development begins. All detector calibration, threshold tuning,
and weight optimization occurs against the frozen benchmark. This
prevents overfitting and ensures detectors are validated against ground
truth, not intuition.

**2.2** **Reproducibility** **First**

**Rule:** Every analysis must be bitwise-identical when re-run with
identical inputs, configuration, and seed.

**Execution:** Pin all dependencies in poetry.lock. Use
numpy.random.default_rng(seed) and random.seed(seed) explicitly. Sort
all collections before iteration. Use math.fsum() for floating-point
summation. Include config_hash and seed in every output artifact. CI
verifies reproducibility via MD5 comparison of results.json.

**2.3** **Contract** **First** **Development**

**Rule:** Modules are built to their ACS v1.0 interface contracts before
integration.

**Execution:** Every module owner writes contract tests (CT-01..CT-17)
before implementation. Request/response schemas from ACS §3 are
implemented as dataclasses or Pydantic models first. Integration occurs
only after individual contract tests pass.

**2.4** **Test** **Before** **Integration**

**Rule:** No module is integrated into the pipeline until its unit tests
and contract tests pass independently.

**Execution:** Each module has a dedicated test file in tests/unit/ and
tests/integration/. The pipeline controller (M-15) is not wired until
M-01 through M-09 pass isolation tests. Benchmark runner (M-06) is not
wired until M-03, M-04, M-05, M-07 pass independently.

**2.5** **Evidence** **Before** **Optimization**

**Rule:** Correctness and transparency are prioritized over performance.

**Execution:** Implement naive, correct versions of all statistical
tests first. Profile only after all tests pass. Performance targets
(e.g., \< 5 min for 1k commits) are treated as acceptance criteria, not
development constraints. Do not parallelize until sequential correctness
is proven.

**2.6** **Simplicity** **Before** **Scale**

**Rule:** V1 is single-threaded by default; complexity is only added
when justified by benchmark data. **Execution:** No multiprocessing in
the analysis pipeline. Optional parallelization is restricted to the
benchmark runner (M-06) with multiprocessing.Pool and deterministic
derived seeds. No async/await in core processing. API uses single-worker
model (V1.1 may introduce multi-worker).

**SECTION** **3** **—** **Team** **Structure**

**3.1** **Engineer** **A** **—** **Principal** **Engineer** **/**
**Interface** **&** **Pipeline** **Architect**

**Role:** Principal Engineer (40% research, 60% engineering) **Primary**
**Responsibilities:**

> System architecture and layer design (Layers 1, 2, 8)
>
> CLI implementation (M-10), API implementation (M-11)
>
> Configuration loader (M-12), Registry manager (M-13)
>
> Pipeline controller (M-15), Job manager (M-14), State manager (M-16),
> Workflow engine (M-17)
>
> Report generator (M-09), Evidence aggregator integration
>
> CI/CD infrastructure, packaging, Docker
>
> Code review and engineering standards enforcement

**Primary** **Ownership:** M-09, M-10, M-11, M-12, M-13, M-14, M-15,
M-16, M-17 **Secondary** **Ownership:** M-01, M-02 (integration layer)

**Review** **Responsibilities:** M-03, M-04, M-06, M-07, M-08

**Integration** **Responsibilities:** Orchestrates end-to-end pipeline
integration in Milestones 8-9.

**3.2** **Engineer** **B** **—** **Research** **Scientist** **/**
**Processing** **&** **Benchmark** **Lead**

**Role:** Research Scientist / ML Engineer (70% research, 30%
engineering) **Primary** **Responsibilities:**

> Repository ingestion (M-01) and Metric extraction (M-02)
>
> Window segmentation (M-03)
>
> Dataset generator (M-03 benchmark variant) and Ground truth manager
> (M-04)
>
> Detector engine (M-05): D-01, D-02, D-03 implementation
>
> Statistical validation, threshold tuning, and calibration
>
> Benchmark dataset construction and annotation protocol
>
> Explanation engine templates and rule-based narrative generation
>
> Paper 1 writing and experimental design

**Primary** **Ownership:** M-01, M-02, M-03 (both variants), M-04, M-05

> **Secondary** **Ownership:** M-08 (scoring formulas), M-09
> (explanation templates) **Review** **Responsibilities:** M-09, M-10,
> M-11, M-12, M-13, M-14, M-15, M-16, M-17
>
> **Integration** **Responsibilities:** Integrates processing layer into
> pipeline; delivers benchmark suites.
>
> **3.3** **Engineer** **C** **—** **Data** **Engineer** **/**
> **Scoring** **&** **Evaluation** **Lead**
>
> **Role:** Data Engineer / Platform Engineer (80% engineering, 20%
> research) **Primary** **Responsibilities:**
>
> Scoring engine (M-08): IS and CS formula implementation
>
> Benchmark runner (M-06) and Evaluation engine (M-07)
>
> Git mining pipeline optimization, storage layer
>
> CLI implementation support, Docker deployment
>
> Benchmark dataset construction support
>
> Open source repository management and documentation
>
> Performance profiling and optimization
>
> Test infrastructure and benchmark automation
>
> **Primary** **Ownership:** M-06, M-07, M-08
>
> **Secondary** **Ownership:** M-01 (Git mining), M-02 (extraction
> optimization), M-03 (segmentation) **Review** **Responsibilities:**
> M-01, M-02, M-05
>
> **Integration** **Responsibilities:** Integrates benchmark subsystem;
> validates detector performance against BSD targets.
>
> **SECTION** **4** **—** **Ownership** **Matrix**

||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||

> **SECTION** **5** **—** **Repository** **Structure**
>
> miie/
>
> ├── .github/
>
> │ ├── workflows/
>
> │ │ ├── ci.yml \# Test, lint, coverage, reproducibility check │ │ └──
> release.yml \# PyPI publish, Docker Hub push
>
> │ ├── ISSUE_TEMPLATE/
>
> │ └── PULL_REQUEST_TEMPLATE.md ├── src/
>
> │ └── miie/

│ ├── \_\_init\_\_.py \# Version string │ ├── \_\_main\_\_.py \# python
-m miie

> │ ├── cli.py \# M-10: CLI Interface │ ├── api.py \# M-11: API Server
>
> │ ├── config.py \# M-12: Config Loader
>
> │ ├── registry.py \# M-13: Registry Manager

│ ├── orchestration/ │ │ ├── \_\_init\_\_.py

│ │ ├── pipeline.py \# M-15: Pipeline Controller │ │ ├── job.py \# M-14:
Job Manager

│ │ ├── state.py \# M-16: State Manager │ │ └── workflow.py \# M-17:
Workflow Engine │ ├── processing/

│ │ ├── \_\_init\_\_.py

│ │ ├── ingestion.py \# M-01: Repository Ingestion │ │ ├── extraction.py
\# M-02: Metric Extraction

│ │ ├── segmentation.py \# M-03: Window Segmentation │ │ ├──
detection.py \# M-05: Detector Engine

│ │ ├── scoring.py \# M-08: Scoring Engine

│ │ └── evidence.py \# EVA: Evidence Aggregator │ ├── benchmark/

│ │ ├── \_\_init\_\_.py

│ │ ├── generator.py \# M-03: Dataset Generator

│ │ ├── ground_truth.py \# M-04: Ground Truth Manager │ │ ├── runner.py
\# M-06: Benchmark Runner

│ │ └── evaluation.py \# M-07: Evaluation Engine │ ├── reporting/

│ │ ├── \_\_init\_\_.py

│ │ ├── generator.py \# M-09: Report + Explanation Generator │ │ └──
templates/ \# Jinja2 templates

│ │ ├── report.j2

│ │ ├── drift_explanation.j2

│ │ ├── correlation_explanation.j2 │ │ └── compression_explanation.j2

│ └── schemas/ \# JSON schemas (BSD-Engineering) ├── tests/

│ ├── unit/ \# Per-module unit tests

│ ├── integration/ \# Module-pair integration tests │ ├── benchmark/ \#
Benchmark validation tests

│ ├── contract/ \# ACS contract tests (CT-01..CT-17) │ ├── schema/ \#
JSON schema tests (ST-01..ST-10)

│ ├── workflow/ \# End-to-end workflow tests (WT-01..WT-07) │ └──
conftest.py \# Shared fixtures, mock components

├── docs/

│ ├── usage.md │ ├── api.md

│ ├── benchmark.md

│ ├── architecture.md

│ └── annotation_handbook.md

├── benchmarks/ \# MIB-SE suites (git submodule or separate repo) │ ├──
metric-drift-v1.0.0/

│ ├── correlation-breakdown-v1.0.0/ │ └── threshold-compression-v1.0.0/
├── scripts/

│ ├── generate_synthetic.py │ ├── inject_pathologies.py │ ├──
compute_statistics.py │ └── visualize.py

├── pyproject.toml ├── poetry.lock

├── requirements.txt ├── README.md

├── LICENSE

├── CONTRIBUTING.md ├── CODE_OF_CONDUCT.md └── Dockerfile

**Directory** **Rules:**

> src/miie/: Owner Engineer A; immutable module boundaries enforced by
> mypy
>
> tests/: Owner rotates per module; ≥90% core coverage required
>
> benchmarks/: Owner Engineer B; versioned independently; checksums on
> all datasets
>
> docs/: Owner Engineer C; must be complete before Beta release
>
> scripts/: Owner Engineer B; deterministic (seed=42); used for dataset
> generation only
>
> **SECTION** **6** **—** **Development** **Environment** **Setup**
>
> **6.1** **Python** **Version**
>
> **Python** **3.10+** (frozen). All developers use Python 3.10.12 for
> V1 to avoid patch-level variance.
>
> **6.2** **Package** **Manager**
>
> **Poetry** (primary). poetry.lock is the dependency authority.
> requirements.txt is generated from Poetry for fallback installation.
>
> **6.3** **Core** **Dependencies** **(Frozen** **Versions)**

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

**6.4** **Virtual** **Environment**

Poetry-managed virtual environment. All developers activate poetry shell
before work.

**6.5** **Linting** **&** **Formatting**

> **black**: Line length 88, target Python 3.10
>
> **flake8**: Compatible with black (max-line-length 88, extend-ignore
> E203)
>
> **mypy**: Strict mode, all modules must pass before PR merge
>
> **isort**: Profile black, sort imports automatically

**6.6** **Type** **Checking**

All functions must have type hints. All module interfaces
(INT-01..INT-18) are typed as dataclasses or Protocol classes. mypy must
pass with zero errors.

**6.7** **Testing** **Framework**

pytest with fixtures in tests/conftest.py. Mock components: MockGit,
MockRepository, MockDetector, MockFilesystem, MockBenchmarkSuite,
MockAPIClient.

**6.8** **Documentation** **Framework**

Sphinx for API docs. Markdown for user docs. README must enable new-user
first analysis in \< 15 minutes.

**6.9** **Git** **Standards**

> **Branching:** main is protected. Feature branches:
> feature/{module-id}-{description} or fix/{description}.
>
> **Commits:** Conventional Commits format. Every commit must reference
> a module ID (e.g., feat(M-05): implement D-03 dip test).
>
> **PRs:** Minimum 1 reviewer (2 for code changes). CI must pass (tests,
> lint, coverage, reproducibility).

**SECTION** **7** **—** **Milestone** **Structure**

**Milestone** **0:** **Environment** **Setup** **(Week** **1)**

**Objective:** All developers have identical environments, CI is
running, repository scaffold is complete.

**Deliverables:**

> Poetry project scaffold with pyproject.toml
>
> CI pipeline (GitHub Actions): test, lint, coverage, reproducibility
> check
>
> Pre-commit hooks (black, flake8, mypy)
>
> Hello-world CLI (miie --version returns 1.0.0)
>
> Docker skeleton **Exit** **Criteria:** All 3 engineers can run poetry
> install && pytest successfully on clean clones.

**Milestone** **1:** **Core** **Infrastructure** **(Weeks** **2-3)**

**Objective:** Interface layer, orchestration layer, and config/registry
systems are operational. **Deliverables:**

> M-12 (Config Loader): strict schema validation, hash computation
>
> M-13 (Registry Manager): frozen M-01..M-07, D-01..D-03 definitions
> loaded
>
> M-15 (Pipeline Controller): stage orchestration skeleton with progress
> callbacks
>
> M-16 (State Manager): atomic JSON writes, job state machine
>
> M-17 (Workflow Engine): dispatches WF-01..WF-05 **Exit** **Criteria:**
> pytest passes with ≥80% coverage on scaffolding; config loader
> validates all TFS examples.

**Milestone** **2:** **Metric** **Pipeline** **(Weeks** **4-5)**

**Objective:** Repository ingestion through window segmentation produces
valid data structures. **Deliverables:**

> M-01 (Repository Ingestion): clone, validate, extract metadata
>
> M-02 (Metric Extraction): all 7 metrics with range validation
>
> M-03 (Window Segmentation): time/commit/release/custom strategies
>
> Integration tests: M-01 → M-02 → M-03 **Exit** **Criteria:**
> Successfully ingest and extract metrics from 10 real repositories; all
> 7 metrics produce valid DataFrames; segmentation produces
> non-overlapping ordered windows.

**Milestone** **3:** **Dataset** **System** **(Weeks** **6-7)**

**Objective:** Synthetic dataset generator and ground truth manager
produce frozen benchmark suites. **Deliverables:**

> M-03 (Dataset Generator): 7 repository profiles, pathology injection,
> schema export
>
> M-04 (Ground Truth Manager): annotation workflow, Cohen's Kappa
> computation, adjudication
>
> 120 synthetic datasets generated and validated
>
> 3 benchmark suites: B-01 (50), B-02 (40), B-03 (30) **Exit**
> **Criteria:** All datasets pass schema validation; κ ≥ 0.80 on all
> suites; pathologies verifiable by independent script.

**Milestone** **4:** **Detector** **System** **(Weeks** **8-10)**

**Objective:** All three frozen detectors are implemented, tested, and
meet benchmark targets. **Deliverables:**

> M-05 (Detector Engine): D-01 (KS+PSI), D-02 (Pearson+Spearman), D-03
> (excess
>
> mass+dip)
>
> Evidence aggregator (EVA) collects intermediate artifacts
>
> All detectors pass contract tests CT-07, CT-08
>
> Benchmark tests BT-01, BT-02, BT-03 show targets met **Exit**
> **Criteria:** D-01 precision ≥ 0.80, recall ≥ 0.75; D-02 precision ≥
> 0.75, recall ≥ 0.70; D-03 precision ≥ 0.85, recall ≥ 0.80; all on
> frozen benchmarks.

**Milestone** **5:** **Benchmark** **System** **(Weeks** **11-12)**

**Objective:** Benchmark runner and evaluation engine produce
standardized performance reports. **Deliverables:**

> M-06 (Benchmark Runner): suite loading, detector isolation, leakage
> prevention
>
> M-07 (Evaluation Engine): 8 metrics (accuracy, precision, recall, F1,
> AUC-ROC, AUC-PR, FPR, FNR)
>
> 4 baseline implementations (random, majority, statistical, rule-based)
>
> Benchmark reports in JSON and Markdown **Exit** **Criteria:** Full
> suite execution \< 10 minutes; evaluation metrics match manual
> calculation; reproducibility test passes (bitwise-identical JSON).

**Milestone** **6:** **Scoring** **System** **(Week** **13)**

**Objective:** Integrity Score and Confidence Score formulas are
implemented and validated. **Deliverables:**

> M-08 (Scoring Engine): IS and CS computation per TFS §6-7
>
> Weight redistribution logic (proportional)
>
> Edge case handling (all metrics unavailable, single metric, detector
> skipped) **Exit** **Criteria:** CT-09 passes; IS/CS match TFS example
> calculations to 1e-9; scores monotonically decrease with injected
> failures.

**Milestone** **7:** **Reporting** **System** **(Weeks** **14-15)**

**Objective:** Explanation generator and report generator produce
human-readable and machine-readable outputs.

**Deliverables:**

> M-09 (Explanation Generator): Jinja2 templates for D-01, D-02, D-03
>
> M-09 (Report Generator): JSON, Markdown, CSV exports with provenance
>
> Manifest system with SHA-256 checksums
>
> Explanation reports include "human oversight required" disclaimer
> **Exit** **Criteria:** CT-11, CT-12 pass; every detected failure has
> an explanation; reports are schema-valid; new user understands
> integrity status without re-running.

**Milestone** **8:** **Integration** **(Weeks** **16-17)**

**Objective:** All modules integrate into a functioning pipeline and
benchmark subsystem. **Deliverables:**

> M-10 (CLI): all 8 commands implemented
>
> M-11 (API): all 6 endpoints implemented
>
> End-to-end workflow tests WT-01..WT-07 pass
>
> System tests on real repositories (100+ repos)
>
> Performance profiling and optimization **Exit** **Criteria:** miie
> analyze --repo \<url\> completes end-to-end; API accepts POST
> /v1/analyze and returns 202; all workflow tests pass.

**Milestone** **9:** **Testing** **&** **Hardening** **(Weeks**
**18-20)**

**Objective:** Test coverage targets met, documentation complete,
release candidate ready. **Deliverables:**

> ≥90% test coverage on core engine
>
> All contract tests, schema tests, workflow tests, benchmark tests pass
>
> Documentation complete (README, usage, API, benchmark, architecture)
>
> Docker image builds and runs
>
> Reproducibility verification: 10 identical runs produce
> bitwise-identical outputs **Exit** **Criteria:** CI passes on Linux,
> macOS, WSL; no critical bugs; Paper 1 draft complete.

**SECTION** **8** **—** **Sprint** **Plan**

**Sprint** **0:** **Environment** **&** **Scaffold** **(Week** **1)**

**Goals:** Development environment identical across team; CI running.
**Tasks:**

> A: Set up Poetry, CI/CD, pre-commit hooks, Docker skeleton
>
> B: Define mock component interfaces (MockGit, MockRepository)
>
> C: Set up test infrastructure, fixtures, conftest.py **Deliverables:**
> Running CI, hello-world CLI, dev environment docs.
>
> **Acceptance** **Criteria:** All engineers can run pytest and miie
> --version on Day 1.

**Sprint** **1:** **Config,** **Registry,** **Pipeline** **Skeleton**
**(Week** **2)**

**Goals:** Core infrastructure operational. **Tasks:**

> A: M-12 (Config Loader), M-13 (Registry Manager), M-16 (State Manager)
>
> B: M-15 (Pipeline Controller) stage sequencing, progress callbacks
>
> C: M-17 (Workflow Engine) dispatch logic, input validation
> **Deliverables:** Config loads and validates; registry returns frozen
> definitions; pipeline runs empty stages.
>
> **Acceptance** **Criteria:** CT-15, CT-16, CT-17 pass; config hash
> computed; state transitions atomic.

**Sprint** **2:** **Repository** **Ingestion** **(Week** **3)**

**Goals:** Clone and validate repositories. **Tasks:**

> B: M-01 implementation; git subprocess handling; metadata extraction
>
> C: Review M-01; build MockGit fixture; test edge cases (shallow,
> empty, corrupted)
>
> A: Integrate M-01 into pipeline skeleton **Deliverables:** miie ingest
> works; RepositoryContext schema valid.
>
> **Acceptance** **Criteria:** CT-01, CT-02 pass; 10 real repos ingested
> successfully.

**Sprint** **3:** **Metric** **Extraction** **(Week** **4)**

**Goals:** Extract 7 frozen metrics. **Tasks:**

> B: M-02 implementation; coverage parsers (XML/LCOV); git log parsers;
> PR/issue CSV parsers
>
> C: Review M-02; test missing data paths; validate ranges
>
> A: Integrate M-02 into pipeline; build extraction progress callbacks
> **Deliverables:** MetricDataFrame produced for all 7 metrics; missing
> metrics logged gracefully. **Acceptance** **Criteria:** CT-03, CT-04
> pass; all values in valid ranges; non-numeric coerced to null.

**Sprint** **4:** **Window** **Segmentation** **(Week** **5)**

**Goals:** Partition history into analysis windows. **Tasks:**

> B: M-03 implementation; time/commit/release/custom strategies
>
> C: Review M-03; test boundary conditions; validate non-overlap
>
> A: Integrate M-03 into pipeline; wire M-02 → M-03 → pipeline
> **Deliverables:** List\[Window\] valid; non-overlapping; ordered; ≥2
> windows for drift detection. **Acceptance** **Criteria:** CT-05, CT-06
> pass; 10 real repos segmented correctly.

**Sprint** **5:** **MIFS** **—** **Repository** **Curation** **(Week**
**6)**

**Goals:** Select candidate repositories; establish baseline
characterization. **Tasks:**

> B: Select 100 candidate repos; mine commit history; compute baseline
> distributions
>
> C: Build data pipeline for MIFS; storage optimization
>
> A: Support B with tooling; document MIFS protocol **Deliverables:**
> 100 candidate repos with baseline metrics; 20+ known dysfunction
> events catalogued.
>
> **Acceptance** **Criteria:** Baseline metrics computed for all 100;
> dysfunction events documented.

**Sprint** **6:** **MIFS** **—** **Ground** **Truth** **&**
**Feasibility** **(Week** **7)**

**Goals:** Annotate repositories; freeze benchmark dataset. **Tasks:**

> B: Develop annotation guidelines; recruit 3 external annotators;
> compute Cohen's Kappa
>
> C: Build annotation tooling; compute inter-rater agreement
>
> A: Build prototype drift detection (KS-test) on annotated repos;
> measure
>
> recall **Deliverables:** Frozen benchmark dataset (50 repos);
> annotation guidelines; MIFS feasibility report.
>
> **Acceptance** **Criteria:** κ ≥ 0.7; ≥60% prototype recall on labeled
> failures; benchmark frozen.

**Sprint** **7:** **Dataset** **Generator** **(Week** **8)**

**Goals:** Generate 120 synthetic datasets with controlled pathologies.
**Tasks:**

> B: M-03 (GEN) implementation; 7 profiles; pathology injection; schema
> export
>
> C: Review generator; build validation scripts; verify detectability
>
> A: Integrate generator into CLI (miie generate) **Deliverables:** 120
> synthetic datasets; metrics.json, windows.json, metadata.json per
> dataset.
>
> **Acceptance** **Criteria:** WT-06 pass; all datasets schema-valid;
> pathologies verifiable.

**Sprint** **8:** **Ground** **Truth** **Manager** **(Week** **9)**

**Goals:** Expert annotation workflow and ground truth finalization.
**Tasks:**

> B: M-04 implementation; label versioning; conflict resolution;
> adjudication
>
> C: Build annotation interface; compute κ; validate evidence
> requirements
>
> A: Integrate M-04 into benchmark subsystem **Deliverables:**
> ground_truth.json for all 3 suites; κ ≥ 0.80 per suite.
>
> **Acceptance** **Criteria:** WT-07 pass; positive labels have
> evidence; Cohen's Kappa ≥ 0.80.

**Sprint** **9:** **D-01** **&** **D-02** **Detectors** **(Week**
**10)**

**Goals:** Implement distributional drift and correlation breakdown
detectors. **Tasks:**

> B: M-05 D-01 (KS + PSI); D-02 (Pearson + Spearman + Fisher z)
>
> C: Review detectors; test against synthetic data; validate thresholds
>
> A: Build evidence collection for D-01/D-02 outputs **Deliverables:**
> D-01 and D-02 implemented; pass contract tests.
>
> **Acceptance** **Criteria:** CT-07, CT-08 pass; BT-01 precision ≥
> 0.80, recall ≥ 0.75; BT-02 precision ≥ 0.75, recall ≥ 0.70.

**Sprint** **10:** **D-03** **Detector** **&** **Evidence** **(Week**
**11)**

**Goals:** Implement threshold compression detector and evidence
aggregator. **Tasks:**

> B: M-05 D-03 (excess mass + Hartigans' dip test); custom dip
> implementation
>
> C: Review D-03; validate bootstrap with seed=42; test edge cases
>
> A: EVA implementation; schema validation; provenance attachment
> **Deliverables:** D-03 implemented; EvidencePackage schema valid.
>
> **Acceptance** **Criteria:** BT-03 precision ≥ 0.85, recall ≥ 0.80;
> CT-10 pass; every positive flag has evidence.

**Sprint** **11:** **Scoring** **Engine** **(Week** **12)**

**Goals:** Compute IS and CS with frozen formulas. **Tasks:**

> C: M-08 implementation; IS weighted aggregation; CS multiplicative
> factors
>
> B: Review scoring; validate weight redistribution; test edge cases
>
> A: Integrate scoring into pipeline; wire EVA → M-08 → M-09
> **Deliverables:** ScorePackage with IS and CS; per-metric and overall
> scores.
>
> **Acceptance** **Criteria:** CT-09 pass; IS/CS match TFS calculations
> to 1e-9; scores in \[0,1\].

**Sprint** **12:** **Benchmark** **Runner** **(Week** **13)**

**Goals:** Execute benchmark suites and collect predictions. **Tasks:**

> C: M-06 implementation; suite loading; detector isolation;
> temporal/cross-dataset isolation
>
> A: Review runner; implement optional parallelization; build baseline
> systems
>
> B: Validate detector compatibility; test leakage prevention
> **Deliverables:** BenchmarkRun objects; predictions collected; timing
> metadata.
>
> **Acceptance** **Criteria:** CT-13 pass; no leakage detected;
> sequential default; optional parallel.

**Sprint** **13:** **Evaluation** **Engine** **&** **Baselines**
**(Week** **14)**

**Goals:** Compute classification metrics and baseline comparisons.
**Tasks:**

> C: M-07 implementation; confusion matrix; 8 evaluation metrics; AUC
> computation
>
> A: Implement 4 baselines (random, majority, statistical, rule-based)
>
> B: Validate evaluation against manual calculations; test
> division-by-zero
>
> handling **Deliverables:** EvaluationResult with all 8 metrics;
> baseline reports.
>
> **Acceptance** **Criteria:** CT-14 pass; metrics match manual calc;
> AUC-ROC ≥ 0.85; baselines included.

**Sprint** **14:** **Explanation** **&** **Report** **Generation**
**(Week** **15)**

**Goals:** Human-readable explanations and machine-readable exports.
**Tasks:**

> A: M-09 explanation templates (Jinja2); rule-based narrative
> generation; disclaimer
>
> C: Review explanations; validate template rendering; test CSV/JSON
> exports
>
> B: Validate explanation accuracy; ensure deterministic rule mapping
> **Deliverables:** ExplanationReport; JSON/Markdown/CSV exports;
> manifest.json with checksums. **Acceptance** **Criteria:** CT-11,
> CT-12 pass; explanations cite evidence; disclaimer present; schema
> valid.

**Sprint** **15:** **CLI** **&** **API** **(Week** **16)**

**Goals:** User interfaces complete. **Tasks:**

> A: M-10 (CLI) all 8 commands; M-11 (API) all 6 endpoints;
> FastAPI/uvicorn
>
> C: Review CLI; test exit codes; validate error messages
>
> B: Review API; test RFC 7807 errors; validate async job flow
> **Deliverables:** miie analyze, miie benchmark, miie explain, miie
> export, miie ingest, miie detect, miie evaluate, miie generate; API at
> localhost:8000. **Acceptance** **Criteria:** All CLI commands pass;
> API returns correct status codes; \< 500ms acceptance.

**Sprint** **16:** **Integration** **&** **System** **Tests** **(Week**
**17)**

**Goals:** End-to-end pipeline and benchmark subsystem integration.
**Tasks:**

> A: Wire all modules; implement WF-01..WF-05; system tests
>
> B: Run 100 real repos through pipeline; validate detector behavior
>
> C: Performance profiling; optimize hot paths; memory profiling
> **Deliverables:** Integrated system; workflow tests WT-01..WT-05 pass;
> performance report.
>
> **Acceptance** **Criteria:** WT-01..WT-05 pass; analysis \< 5 min for
> 1k commits; benchmark \< 10 min for 50 datasets.

**Sprint** **17:** **Testing** **&** **Hardening** **(Week** **18)**

**Goals:** Coverage targets, bug fixes, documentation. **Tasks:**

> C: Drive coverage to ≥90%; fix critical bugs; optimize test suite
>
> A: Complete documentation; polish CLI help; build quickstart
>
> B: Finalize benchmark datasets; validate all κ targets; draft Paper 1
> **Deliverables:** ≥90% coverage; complete docs; Docker image; Paper 1
> draft.
>
> **Acceptance** **Criteria:** CI passes on all platforms; no critical
> bugs; new user \< 15 min to first analysis.
>
> **Sprint** **18:** **Release** **Candidate** **(Week** **19)**
>
> **Goals:** Release candidate ready for community testing. **Tasks:**
>
> A: Version bump to v1.0.0-rc1; build release pipeline; tag
>
> C: Final reproducibility verification; checksum all outputs
>
> B: Community outreach; friendly researcher alpha testing
> **Deliverables:** v1.0.0-rc1 on PyPI; Docker Hub image; release notes.
>
> **Acceptance** **Criteria:** pip install miie==1.0.0rc1 works; Docker
> runs; alpha testers provide feedback.
>
> **Sprint** **19:** **Stable** **Release** **(Week** **20)**
>
> **Goals:** v1.0.0 stable release. **Tasks:**
>
> A: Final bug fixes; merge to main; tag v1.0.0; publish to PyPI
>
> C: Final CI verification; cross-platform tests; security audit
>
> B: Submit Paper 1 to target venue; publish preprint if desired
> **Deliverables:** v1.0.0 stable; complete artifact package; Paper 1
> submitted.
>
> **Acceptance** **Criteria:** All success criteria from Section 1.6
> met.
>
> **SECTION** **9** **—** **Week-by-Week** **Execution** **Plan**

||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

||
||
||
||

> **SECTION** **10** **—** **Development** **Order**
>
> M-12 (Config) + M-13 (Registry) + M-16 (State) ↓
>
> M-01 (Ingestion) ↓
>
> M-02 (Extraction) ↓
>
> M-03 (Segmentation) ↓
>
> M-03 (GEN) + M-04 (Ground Truth) \[Benchmark track, parallel to
> detection\] ↓
>
> M-05 (Detector Engine: D-01 → D-02 → D-03) ↓
>
> EVA (Evidence Aggregator) ↓
>
> M-08 (Scoring Engine) ↓
>
> M-06 (Benchmark Runner) + M-07 (Evaluation Engine) ↓
>
> M-09 (Explanation + Report Generator) ↓
>
> M-10 (CLI) + M-11 (API) ↓
>
> M-15 (Pipeline Controller) + M-17 (Workflow Engine) + M-14 (Job
> Manager) ↓
>
> Integration & System Tests
>
> **Dependency** **Justifications:**
>
> 1\. **Config/Registry/State** **first:** All downstream modules depend
> on configuration validation and registry lookups.
>
> 2\. **Ingestion** **before** **Extraction:** Metrics require a valid
> repository context.
>
> 3\. **Extraction** **before** **Segmentation:** Windows are computed
> over metric data.
>
> 4\. **Segmentation** **before** **Detection:** Detectors operate on
> window pairs or window-level data.
>
> 5\. **Dataset/Truth** **parallel** **to** **Detection:** Benchmark
> construction is independent of detector implementation but must freeze
> before detector tuning.
>
> 6\. **Detection** **before** **Scoring:** IS/CS aggregate detector
> outputs.
>
> 7\. **Scoring** **before** **Reporting:** Reports include scores.
>
> 8\. **Benchmark** **before** **CLI/API:** User-facing commands invoke
> benchmark runner; runner must be correct first.
>
> 9\. **Pipeline/Workflow** **last:** Orchestration layers wire correct
> modules; building them first creates unstable integration targets.

**SECTION** **11** **—** **Coding** **Standards**

**11.1** **Code** **Style**

> **black** formatting, line length 88
>
> **isort** import sorting (profile black)
>
> **flake8** with black-compatible settings

**11.2** **Naming**

> Modules: snake_case.py (e.g., ingestion.py)
>
> Classes: PascalCase (e.g., RepositoryContext)
>
> Functions/variables: snake_case (e.g., extract_coverage)
>
> Constants: UPPER_SNAKE_CASE (e.g., DEFAULT_SEED = 42)
>
> Interface IDs: referenced in docstrings (e.g., Implements ACS INT-01)

**11.3** **Documentation**

> Every module file has a module docstring citing PRD, TFS, TRD, ACS
> sections
>
> Every public function has a Google-style docstring with Args, Returns,
> Raises
>
> Every dataclass has field descriptions

**11.4** **Comments**

> Comments explain "why", not "what"
>
> Statistical formulas reference TFS section numbers (e.g., \# TFS §6.3:
> IS formula)
>
> Complex thresholds reference BSD or TFS

**11.5** **Type** **Hints**

> All function signatures must have type hints
>
> Return types use Result\[T, Error\] pattern or explicit unions
>
> mypy --strict must pass with zero errors

**11.6** **Error** **Handling**

> All exceptions caught at module boundary
>
> Internal errors use custom exception hierarchy (e.g., RepositoryError,
> ScoreError)
>
> User-facing errors follow ACS §19 format
>
> No bare except: clauses

**11.7** **Logging**

> Format: {timestamp} \[{level}\] {module}: {message}
>
> Levels: DEBUG (per-window stats), INFO (stage transitions), WARNING
> (skipped metrics), ERROR (failed stages), CRITICAL (unrecoverable)
>
> All stages log entry and exit with duration
>
> --verbose enables DEBUG to stderr + file

**11.8** **Testing** **Requirements**

> Unit tests: every public function has ≥1 test
>
> Contract tests: every INT has corresponding test in tests/contract/
>
> Mock external dependencies (git, filesystem, HTTP)
>
> Property-based tests for statistical functions where applicable

**11.9** **Review** **Requirements**

> PR requires 1 reviewer minimum (2 for core engine changes)
>
> CI must pass (tests, lint, coverage, reproducibility)
>
> No merge without approval from module reviewer (see Ownership Matrix)

**SECTION** **12** **—** **Definition** **Of** **Done**

**12.1** **Module** **DoD**

> ☐ Code implements ACS contract exactly (input schema, output schema,
> error codes)
>
> ☐ All public functions have type hints and docstrings
>
> ☐ Unit tests pass (≥90% branch coverage for module)
>
> ☐ Contract tests pass (CT-XX for this module)
>
> ☐ mypy passes with zero errors
>
> ☐ black/flake8 pass
>
> ☐ Integration tests pass with upstream/downstream modules
>
> ☐ Performance meets target budget (ACS §23)
>
> ☐ Documentation updated (architecture.md, module docstrings)
>
> ☐ Reviewer approval obtained

**12.2** **Feature** **DoD**

> ☐ PRD requirement traceability documented
>
> ☐ TFS specification compliance verified
>
> ☐ BSD benchmark targets met (if applicable)
>
> ☐ End-to-end workflow test passes (WT-XX)
>
> ☐ CLI command implemented and tested (if user-facing)
>
> ☐ API endpoint implemented and tested (if user-facing)
>
> ☐ Error messages follow ACS §19 format
>
> ☐ No regression in existing tests

**12.3** **Sprint** **DoD**

> ☐ All sprint tasks complete
>
> ☐ All module/feature DoDs for sprint deliverables met
>
> ☐ CI passes on feature branch
>
> ☐ Integration tests for new modules pass
>
> ☐ Demo to team (15 min walkthrough)
>
> ☐ Sprint retrospective completed
>
> ☐ Next sprint plan approved

**12.4** **Milestone** **DoD**

> ☐ All sprint DoDs within milestone met
>
> ☐ Milestone exit criteria achieved (quantitative)
>
> ☐ Benchmark tests pass (if milestone includes detectors/benchmarks)
>
> ☐ Documentation complete for milestone scope
>
> ☐ No critical or high bugs open
>
> ☐ Performance targets verified
>
> ☐ Milestone demo to stakeholders
>
> ☐ Go/no-go decision recorded

**12.5** **Release** **DoD**

> ☐ All milestone DoDs met
>
> ☐ ≥90% test coverage on core engine
>
> ☐ All workflow tests (WT-01..WT-07) pass
>
> ☐ All benchmark tests (BT-01..BT-05) pass
>
> ☐ Reproducibility verification: 10 runs produce identical outputs
>
> ☐ Cross-platform CI passes (Linux, macOS, WSL)
>
> ☐ Documentation complete (README, usage, API, benchmark, architecture)
>
> ☐ Docker image builds and runs
>
> ☐ PyPI package installable in clean environment
>
> ☐ Security audit passed (no known CVEs in dependencies)
>
> ☐ Paper 1 draft complete (if applicable)
>
> ☐ Release notes written
>
> ☐ Version tagged (semantic versioning)

**SECTION** **13** **—** **Testing** **Strategy**

**13.1** **Unit** **Testing**

**Scope:** Individual functions and classes in isolation.

**Coverage** **Goal:** ≥90% branch coverage on core engine (src/miie/).
**Ownership:** Module owner writes tests; reviewer verifies.

**Execution** **Frequency:** Every commit (pre-commit) and every PR
(CI). **Exit** **Criteria:** All unit tests pass; coverage does not
decrease.

**13.2** **Integration** **Testing**

**Scope:** Module pairs (e.g., M-01 → M-02, M-02 → M-03, M-05 → M-08).
**Coverage** **Goal:** All 18 INT contracts have integration tests.

**Ownership:** Module owner + upstream/downstream owners. **Execution**
**Frequency:** Every PR.

**Exit** **Criteria:** All integration tests pass; data flows correctly
between modules.

**13.3** **Contract** **Testing**

**Scope:** ACS v1.0 contract compliance (CT-01..CT-17).

**Coverage** **Goal:** 100% of INT contracts, CLI contracts, and API
endpoint contracts. **Ownership:** Engineer A leads; all engineers
contribute.

**Execution** **Frequency:** Every PR and nightly.

**Exit** **Criteria:** All CT tests pass; request/response schemas match
ACS exactly.

**13.4** **Benchmark** **Testing**

**Scope:** Detector performance against frozen benchmark suites
(BT-01..BT-05). **Coverage** **Goal:** All 3 suites evaluated; all 4
baselines run.

**Ownership:** Engineer C leads; Engineer B validates.

**Execution** **Frequency:** Weekly during Milestones 4-5; nightly
during Milestone 9.

**Exit** **Criteria:** BT-01 (D-01 precision ≥ 0.80, recall ≥ 0.75);
BT-02 (D-02 precision ≥ 0.75, recall ≥ 0.70); BT-03 (D-03 precision ≥
0.85, recall ≥ 0.80); BT-04 (bitwise-identical re-runs); BT-05 (leakage
prevention).

**13.5** **Regression** **Testing**

**Scope:** Known inputs produce known outputs (RT-01..RT-04).

**Coverage** **Goal:** IS formula, CS formula, D-01 thresholds, D-03 dip
test with seed=42. **Ownership:** Engineer C.

**Execution** **Frequency:** Every PR.

**Exit** **Criteria:** IS/CS match manual calculation to 1e-9; D-03
bootstrap produces identical results across runs.

**13.6** **Acceptance** **Testing**

**Scope:** End-to-end user journeys (WT-01..WT-07).

**Coverage** **Goal:** All 5 frozen workflows plus generation and ground
truth workflows. **Ownership:** Engineer A leads.

**Execution** **Frequency:** Milestone boundaries and release candidate.

**Exit** **Criteria:** WT-01 (full analyze on real repo); WT-02 (explain
prior analysis); WT-03 (benchmark B-01 vs D-01); WT-04 (export to CSV);
WT-05 (compare windows); WT-06 (generate 5 datasets); WT-07 (annotate
and adjudicate).

**13.7** **Artifact** **Validation** **Testing**

**Scope:** JSON schema validation for all output artifacts
(ST-01..ST-10). **Coverage** **Goal:** All output schemas validated.

**Ownership:** Engineer A. **Execution** **Frequency:** Every PR.

**Exit** **Criteria:** All artifacts pass JSON Schema draft-07
validation; checksums verified.

**SECTION** **14** **—** **CI/CD** **Strategy**

**14.1** **Git** **Workflow**

> main: protected, release-ready state only
>
> develop: integration branch for milestone work
>
> feature/\*: individual module work
>
> release/v1.0.x: release preparation

**14.2** **Pull** **Requests**

> All changes via PR; no direct push to main or develop
>
> PR template requires: module ID, change summary, test plan, checklist
>
> Minimum 1 approval; 2 approvals for core engine changes

**14.3** **Automated** **Checks** **(CI** **Pipeline)** 1. **Lint:**
black, flake8, isort, mypy — must pass

> 2\. **Unit** **Tests:** pytest with coverage — must pass, ≥90% core
>
> 3\. **Contract** **Tests:** CT-01..CT-17 — must pass
>
> 4\. **Schema** **Tests:** ST-01..ST-10 — must pass
>
> 5\. **Integration** **Tests:** module pair tests — must pass
>
> 6\. **Benchmark** **Tests:** BT-01..BT-03 (fast subset) — must pass
>
> 7\. **Reproducibility** **Test:** Run identical analysis twice;
> compare MD5 of results.json — must match
>
> 8\. **Security** **Scan:** pip-audit or safety — no known CVEs

**14.4** **Build** **Pipeline**

> Poetry build: poetry build produces wheel and sdist
>
> Docker build: multi-stage build, Python 3.10-slim base
>
> Benchmark artifact build: generate and validate 120 datasets (weekly)

**14.5** **Test** **Pipeline**

> Matrix: Python 3.10, 3.11 on Ubuntu 22.04; Python 3.10 on macOS 13,
> Windows WSL2
>
> Fast feedback: lint + unit tests on every PR (\< 5 min)
>
> Full suite: all tests on develop and main (\< 30 min)
>
> Nightly: full benchmark suite + reproducibility verification

**14.6** **Artifact** **Pipeline**

> PyPI: publish on release tag (manual trigger)
>
> Docker Hub: publish on release tag
>
> Benchmarks: versioned separately; checksums published

**14.7** **Release** **Pipeline**

> 1\. Feature freeze announced 2 weeks before release
>
> 2\. release/v1.0.x branch created from develop
>
> 3\. RC published for community testing
>
> 4\. Bug fixes cherry-picked to release branch
>
> 5\. Final version bump and changelog
>
> 6\. GitHub release created with artifacts
>
> 7\. PyPI and Docker Hub publish

**14.8** **Versioning** **Rules**

> MIIE follows semantic versioning: MAJOR.MINOR.PATCH
>
> V1 is frozen: only patch releases (bug fixes, docs) within v1.0.x
>
> Major/minor bumps require IPD/PRD/TFS amendment
>
> **SECTION** **15** **—** **Integration** **Strategy**
>
> **15.1** **Integration** **Sequence**
>
> 1\. **Vertical** **Slice** **1:** M-12 → M-13 → M-01 → M-02 → M-03
> (data pipeline)
>
> 2\. **Vertical** **Slice** **2:** M-03 (GEN) → M-04 → M-06 → M-07
> (benchmark subsystem)
>
> 3\. **Vertical** **Slice** **3:** M-05 → EVA → M-08 → M-09 (detection
> and reporting)
>
> 4\. **Horizontal** **Layer:** M-15 → M-17 → M-14 → M-16
> (orchestration)
>
> 5\. **User** **Interface:** M-10 → M-11 (CLI and API)
>
> **15.2** **Integration** **Gates**

||
||
||
||
||
||
||
||
||
||
||

> **15.3** **Dependency** **Management**
>
> Poetry lockfile is authority; updates require PR and CI verification
>
> Dependabot alerts monitored weekly
>
> No dependency updates during release candidate phase
>
> **15.4** **Conflict** **Resolution**
>
> Module interface conflicts: resolved by ACS v1.0 authority (Engineer A
> decides)
>
> Schema conflicts: resolved by TFS/BSD authority (Engineer B decides)
>
> Performance conflicts: resolved by evidence (profile data wins)
>
> Schedule conflicts: scope reduction per MoSCoW (Must have protected,
> Should have negotiable)

**15.5** **Rollback** **Rules**

> If benchmark targets not met by Milestone 4: extend Milestone 4 by 1
> week; reduce Milestone 7 scope
>
> If κ \< 0.80 by Milestone 3: regenerate datasets with clearer
> pathologies; extend by 1 week
>
> If coverage \< 90% by Milestone 9: defer non-core features; focus on
> critical paths
>
> If reproducibility fails: halt release; fix determinism before
> proceeding

**15.6** **Verification** **Process**

> Every integration gate requires a demo + test report
>
> Gate decisions recorded in GitHub milestone comments
>
> No module proceeds past a gate until all criteria are green

**SECTION** **16** **—** **Benchmark** **Build** **Plan**

**16.1** **Repository** **Selection**

> **Source:** Synthetic generation (not real GitHub repos for V1)
>
> **Categories:** small_active (20), medium_active (30), large_active
> (20), seasonal (15), monotonic_growth (15), declining (10), stable
> (10)
>
> **Total:** 120 datasets
>
> **Seed:** 42 (frozen)

**16.2** **Dataset** **Generation**

> **Tool:** scripts/generate_synthetic.py (Engineer B)
>
> **Parameters:** Truncated normal distributions around profile priors
> (BSD §6.2, §9.2)
>
> **Pathologies:** Injected at predefined windows per BSD §9.4
>
> **Validation:** Automated sanity checks (no NaN, no empty windows,
> valid ranges)
>
> **Retries:** Max 10 retries per pathology injection; reject if
> undetectable

**16.3** **Ground** **Truth** **Construction**

> **Primary** **annotator:** Engineer B (with statistical evidence)
>
> **Secondary** **annotator:** External SE researcher (blind)
>
> **Adjudicator:** Senior researcher (if κ \< 0.80)
>
> **Tool:** src/miie/benchmark/ground_truth.py
>
> **Evidence** **requirement:** Every positive label requires
> statistical evidence + visual evidence + rationale
>
> **Acceptance:** κ ≥ 0.80 auto-approves; 0.65 ≤ κ \< 0.80 adjudicates;
> κ \< 0.65 rejects dataset

**16.4** **Annotation** **Protocol**

> 1\. Generate candidate labels from injection script
>
> 2\. Primary annotator reviews + confirms/modifies
>
> 3\. Secondary annotator blind reviews
>
> 4\. Compute Cohen's Kappa
>
> 5\. Adjudicate if needed
>
> 6\. Write ground_truth.json with provenance

**16.5** **Validation**

> Schema validation against BSD §14.4
>
> Checksum verification (SHA-256)
>
> Temporal consistency: pathologies only after injection point
>
> Metric consistency: no MDE-01 and MDE-03 in same window

**16.6** **Versioning**

> Benchmark suites versioned independently: metric-drift-v1.0.0
>
> Major bump: label changes, schema changes, dataset removal
>
> Minor bump: additional datasets, metadata corrections
>
> Patch bump: documentation, plot regeneration

**16.7** **Release** **Strategy**

> Benchmarks released with MIIE v1.0.0
>
> Stored in ~/.miie/benchmarks/ or as git submodule
>
> Quarterly audit: regenerate 5% random sample, compare checksums

**SECTION** **17** **—** **Detector** **Build** **Plan**

**17.1** **D-01:** **Distributional** **Drift** **Detector**
**Implementation** **Steps:**

> 1\. Implement scipy.stats.ks_2samp wrapper (two-sample KS test)
>
> 2\. Implement PSI with 10 equal-width bins
>
> 3\. Implement direction classification: mean_shift, variance_collapse,
> shape_change
>
> 4\. Implement severity: min(1.0, ks_statistic / 0.5)
>
> 5\. Handle insufficient data (\< 10 samples): skip with warning
>
> 6\. Handle zero variance: skip with warning

**Dependencies:** M-02, M-03, SciPy ≥ 1.11 **Validation:** BT-01
(precision ≥ 0.80, recall ≥ 0.75)

**Acceptance** **Criteria:** CT-07, CT-08 pass; runs \< 1s for 10
metrics × 10 windows; deterministic with seed=42.

**17.2** **D-02:** **Correlation** **Breakdown** **Detector**
**Implementation** **Steps:**

> 1\. Implement Pearson and Spearman correlation per window
>
> 2\. Implement Fisher z-transformation for confidence intervals
>
> 3\. Detect sudden drop: Δ\|r\| \> 0.3
>
> 4\. Detect sign reversal: sign change + \|r\| \> 0.2 both sides
>
> 5\. Detect gradual erosion: slope \< -0.1 per window, r drops from \>
> 0.3 to \< 0.1
>
> 6\. Detect confidence interval exclusion: non-overlapping 95% CIs
>
> 7\. Implement severity: min(1.0, \|delta_r\| / 0.3)

**Dependencies:** M-02, M-03, SciPy

**Validation:** BT-02 (precision ≥ 0.75, recall ≥ 0.70)

**Acceptance** **Criteria:** CT-07 pass; metric pairs processed in
lexicographic order; deterministic.

**17.3** **D-03:** **Threshold** **Compression** **Detector**
**Implementation** **Steps:**

> 1\. Implement auto-threshold detection (round numbers: 1, 5, 10, 20,
> 25, 50, 75, 80, 90, 95, 100, 1000)
>
> 2\. Implement excess mass binomial test with margin ε = max(0.02×T,
> 0.01×range)
>
> 3\. Implement Hartigans' dip test (custom implementation, bootstrap
> n=1000, seed=42)
>
> 4\. Flag if excess mass significant AND (multimodal OR p_hat \> 0.5)
>
> 5\. Compute severity = compression_index
>
> 6\. Handle insufficient data (\< 20 samples): skip

**Dependencies:** M-02, M-03, NumPy

**Validation:** BT-03 (precision ≥ 0.85, recall ≥ 0.80)

**Acceptance** **Criteria:** CT-07 pass; dip test bitwise-identical
across runs; \< 2s for 10 metrics × 10 windows.

**17.4** **Testing**

> **Unit** **tests:** Each detector method tested with synthetic data
> fixtures
>
> **Contract** **tests:** D01Output, D02Output, D03Output schema
> validation
>
> **Benchmark** **tests:** BT-01, BT-02, BT-03
>
> **Regression** **tests:** RT-03 (D-01 thresholds), RT-04 (D-03 dip
> test seed=42)

**17.5** **Performance** **Targets**

> D-01: \< 1s per full analysis (10 metrics × 10 windows)
>
> D-02: \< 1s per full analysis (21 pairs × 10 windows)
>
> D-03: \< 2s per full analysis (10 metrics × 10 windows)

**SECTION** **18** **—** **Documentation** **Plan**

**18.1** **Developer** **Documentation**

> **Architecture** **Guide:** Layer-by-layer design rationale (Engineer
> A, Week 18)
>
> **API** **Reference:** Auto-generated from FastAPI OpenAPI spec
> (Engineer A, Week 16)
>
> **Module** **Reference:** Docstring-generated docs for all 18 modules
> (All, ongoing)
>
> **Contribution** **Guidelines:** PR template, code style, test
> requirements (Engineer A, Week 1)

**18.2** **User** **Documentation**

> **README.md:** Quick start, installation, basic usage (Engineer C,
> Week 18)
>
> **usage.md:** Comprehensive CLI and API guide (Engineer A, Week 18)
>
> **benchmark.md:** How to run benchmarks, interpret results (Engineer
> B, Week 18)
>
> **annotation_handbook.md:** Training for benchmark annotators
> (Engineer B, Week 7)

**18.3** **Benchmark** **Documentation**

> **threat_analysis.md:** Threats to validity and mitigations (Engineer
> B, Week 18)
>
> **generation_log.md:** Dataset generation parameters and provenance
> (Engineer B, Week 8)
>
> **annotation_log.md:** Annotator decisions and disagreements (Engineer
> B, Week 9)

**18.4** **API** **Documentation**

> **OpenAPI** **3.0** **spec:** Auto-generated from FastAPI (Engineer A,
> Week 16)
>
> **api.md:** Human-readable endpoint descriptions (Engineer A, Week 18)

**18.5** **Artifact** **Documentation**

> **manifest.json** **schema:** Documented in architecture.md
>
> **results.json** **schema:** Documented in usage.md
>
> **evidence.json** **schema:** Documented in benchmark.md
>
> **18.6** **Release** **Documentation**
>
> **CHANGELOG.md:** Conventional commit-based (Engineer A, release time)
>
> **release_notes.md:** User-facing changes per version (Engineer A,
> release time)
>
> **18.7** **Ownership** **&** **Completion** **Criteria** All docs in
> docs/ directory
>
> README must enable new-user first analysis in \< 15 minutes (validated
> by team member not involved in development)
>
> All external links validated
>
> All code examples tested and working
>
> **SECTION** **19** **—** **Risk** **Management** **Plan**

||
||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||
||
||

||
||
||
||
||

> **SECTION** **20** **—** **Resource** **Allocation** **Plan**
>
> **20.1** **Time** **Allocation** **(per** **engineer,** **40**
> **hrs/week)**

||
||
||
||
||
||
||
||
||

> **20.2** **Milestone** **Allocation**
>
> **Milestones** **0-2** **(Weeks** **1-5):** 60% infrastructure, 40%
> processing pipeline
>
> **Milestones** **3-5** **(Weeks** **6-14):** 50% benchmark/detectors,
> 30% scoring/evaluation, 20% integration
>
> **Milestones** **6-9** **(Weeks** **15-20):** 40%
> reporting/interfaces, 30% testing, 20% documentation, 10% release
>
> **20.3** **Buffer** **Allocation**
>
> **Schedule** **buffer:** 2 weeks (Weeks 19-20) as explicit buffer
>
> **Scope** **buffer:** "Could have" features (parallel processing,
> additional export formats) deferred to V1.1
>
> **Personnel** **buffer:** Cross-training ensures any 2 engineers can
> continue if 1 departs
>
> **SECTION** **21** **—** **Release** **Plan**
>
> **21.1** **Alpha** **(Week** **14** **—** **v0.1.0-alpha)**
>
> **Requirements:** Core pipeline functional; detectors implemented;
> benchmark suites generated.

**Deliverables:** Internal tag; alpha usable by team; 10 critical bugs
fixed.

**Validation:** Team dogfooding; 3 team members use daily for 1 week
without crashes. **Exit** **Criteria:** All P0 features complete; no
data corruption bugs; CLI stable.

**21.2** **Beta** **(Week** **16** **—** **v0.5.0-beta)**

**Requirements:** CLI and API complete; documentation draft; benchmark
datasets frozen. **Deliverables:** Public GitHub repo; beta release;
issue templates; outreach to 5 research groups. **Validation:** External
testers provide feedback; at least 1 external contributor opens a PR.

**Exit** **Criteria:** New user can install and run in \< 15 minutes;
API responds correctly; benchmark tests pass.

**21.3** **Release** **Candidate** **(Week** **19** **—**
**v1.0.0-rc1)**

**Requirements:** All tests pass; documentation complete; Docker image
ready. **Deliverables:** RC on PyPI; Docker Hub image; release notes;
Paper 1 draft. **Validation:** Community testing; reproducibility
verification; security audit.

**Exit** **Criteria:** No critical bugs; ≥90% coverage; CI passes all
platforms; Paper 1 draft complete.

**21.4** **Version** **1.0** **(Week** **20** **—** **v1.0.0)**

**Requirements:** All acceptance criteria met; community feedback
addressed.

**Deliverables:** Stable release on PyPI and Docker Hub; tagged on
GitHub; Paper 1 submitted. **Validation:** Final reproducibility check;
benchmark targets confirmed; success framework evaluation.

**Exit** **Criteria:** All Section 1.6 success criteria met.

**SECTION** **22** **—** **Open** **Source** **Release** **Plan**

**22.1** **Repository** **Publication** **Platform:** GitHub (public)

> **License:** Apache 2.0 (code); CC-BY-4.0 (benchmark datasets,
> documentation)
>
> **Timing:** Beta at Week 16; stable at Week 20

**22.2** **Contribution** **Guidelines**

> CONTRIBUTING.md defines: bug reports, dataset proposals, baseline
> submissions, code style, test requirements
>
> PR template includes: module ID, test plan, checklist, benchmark
> impact
>
> Code style: PEP 8 + black + mypy
>
> Test requirement: ≥80% coverage on new code

**22.3** **Issue** **Templates**

> Bug Report: module, reproduction steps, expected vs actual,
> environment
>
> Dataset Proposal: profile, pathology type, justification
>
> Label Challenge: dataset ID, metric, evidence for challenge
>
> Feature Request: evaluated against V1 scope (likely deferred to V2)

**22.4** **Roadmap** **Publication**

> ROADMAP.md published at Beta release
>
> V1.1, V1.2, V2.0 directions outlined (no commitments)
>
> Community call for detectors and benchmark contributions at Month 8

**22.5** **Artifact** **Packaging**

> **PyPI:** pip install miie installs CLI and all core dependencies
>
> **Docker:** docker run miie:latest miie analyze --repo \<url\>
>
> **Benchmarks:** Download via mibse download metric-drift-v1.0.0 or
> manual

**22.6** **Community** **Readiness**

> README includes: quickstart, installation, basic usage, citation info
>
> Documentation site (Sphinx) hosted on ReadTheDocs or GitHub Pages
>
> Mailing list or GitHub Discussions for community support
>
> Code of Conduct: Contributor Covenant v2.1

**SECTION** **23** **—** **Publication** **Support** **Plan**

**23.1** **MSR** **Submission** **Support** **(Paper** **2** **target)**

> **Dataset:** 500+ repositories from GitHub, temporal analysis
> 2015-2025
>
> **Support:** Benchmark datasets, evaluation scripts, replication
> package
>
> **Timing:** Draft by Month 10, submit by Month 12

**23.2** **ICSE** **Submission** **Support** **(Paper** **1**
**target)** **Contribution:** Framework + taxonomy + tool + MIFS

> **Support:** Complete artifact package with Docker, benchmark
> datasets, evaluation scripts
>
> **Timing:** Draft by Month 5, submit by Month 7
>
> **Badge** **target:** ACM "Artifacts Evaluated — Reusable"

**23.3** **Artifact** **Evaluation** **Support**

> **Package** **contents:**
>
> Source code with build instructions
>
> Frozen benchmark datasets with ground truth labels
>
> Reproducible scripts for all reported results
>
> Step-by-step reproduction guide
>
> Pre-built Docker image with all dependencies
>
> **Validation:** Independent re-run by external researcher produces
> identical results
>
> **23.4** **Reproducibility** **Package**
>
> reproduce.sh script: installs dependencies, runs benchmark, generates
> figures
>
> requirements.txt and poetry.lock pinned
>
> Dockerfile with fixed base image
>
> manifest.json in every output directory with config_hash, seed,
> versions
>
> **23.5** **Benchmark** **Package**
>
> Benchmark suites versioned and hosted separately (git submodule)
>
> Checksums for all dataset files
>
> Annotation guidelines and ground truth provenance included
>
> Baseline implementations included for comparison
>
> **SECTION** **24** **—** **Progress** **Tracking** **Framework**
>
> **24.1** **KPIs**

||
||
||
||
||
||
||
||
||
||
||

> **24.2** **Engineering** **Metrics**
>
> Commits per week per engineer
>
> PR review turnaround time (target: \< 24 hours)
>
> Bug open/close rate
>
> Performance regression tracking (stage durations)

**24.3** **Quality** **Metrics**

> mypy error count (target: 0)
>
> lint violation count (target: 0)
>
> test flake rate (target: 0%)
>
> security vulnerability count (target: 0)

**24.4** **Benchmark** **Metrics**

> Per-detector precision, recall, F1, AUC-ROC, AUC-PR
>
> Per-suite execution time
>
> Baseline comparison tables
>
> Leakage detection pass/fail

**24.5** **Completion** **Metrics** Modules complete: 18/18

> CLI commands complete: 8/8
>
> API endpoints complete: 6/6
>
> Workflows complete: 7/7
>
> Benchmark suites complete: 3/3

**24.6** **Sprint** **Metrics**

> Story points completed vs planned
>
> Sprint goal achievement (pass/fail)
>
> Carryover tasks (target: \< 10%)

**24.7** **Milestone** **Metrics**

> Exit criteria achieved (percentage)
>
> Deliverables completed (count)
>
> Blockers resolved (count)
>
> Go/no-go decision
>
> **SECTION** **25** **—** **Implementation** **Readiness** **Audit**

||
||
||
||
||
||
||
||
||
||
||

> **Residual** **Items** **(Engineering** **Decisions,** **Not**
> **Ambiguities):**
>
> Poetry vs pip: Team selects Poetry; pip fallback documented
>
> Click vs argparse: Team selects Click; argparse acceptable per TRD
>
> FastAPI vs stdlib: FastAPI recommended; stdlib http.server acceptable
> for minimal API
>
> Jinja2 template location: src/miie/reporting/templates/ (frozen)
>
> Test fixture strategy: pytest fixtures in tests/conftest.py
>
> Docker packaging: Optional but recommended; not required for V1
> functionality

**SECTION** **26** **—** **FINAL** **IMPLEMENTATION** **VERDICT**

**26.1** **Primary** **Question**

If three engineers start tomorrow using this IMP v1.0 and the approved
document stack (IPD v1.1 FINAL, PRD v1.0, TFS v1.0, BSD v1.0, TRD v1.0,
AFD v1.0, BSD-Engineering v1.0, ACS v1.0), can they build MIIE Version 1
without requiring additional planning documents?

**26.2** **Answer** **YES.**

**26.3** **Justification**

This IMP provides sufficient execution detail for three independent
engineers to begin development immediately because:

> 1\. **Team** **Structure:** Roles, responsibilities, ownership, and
> review assignments are unambiguous (Section 3, 4).
>
> 2\. **Build** **Sequence:** Exact module development order with
> dependency justifications is specified (Section 10).
>
> 3\. **Week-by-Week** **Plan:** Every week has assigned tasks per
> engineer with expected outputs (Section 9).
>
> 4\. **Milestone** **Gates:** Quantitative exit criteria define when
> work is complete (Section 7, 12).
>
> 5\. **Contracts:** All 18 module interfaces, 8 CLI commands, and 6 API
> endpoints are traceable to ACS v1.0 (Section 4, 13).
>
> 6\. **Benchmarks:** Dataset generation, annotation protocol, and
> ground truth construction are specified (Section 16).
>
> 7\. **Detectors:** Implementation steps, statistical thresholds, and
> acceptance targets are frozen per TFS (Section 17).
>
> 8\. **Testing:** Unit, integration, contract, benchmark, regression,
> and acceptance test strategies are defined with ownership and
> frequency (Section 13).
>
> 9\. **Risk** **Management:** Identified risks have probabilities,
> impacts, mitigations, contingencies, and owners (Section 19).
>
> 10.**Release:** Alpha, Beta, RC, and stable release criteria are
> defined (Section 21).

**26.4** **Declaration**

**Implementation** **Master** **Plan** **(IMP** **v1.0)** **Status:**
**Implementation** **Authority**

**Verdict:** **IMPLEMENTATION** **APPROVED** **—** **READY** **FOR**
**DEVELOPMENT**

Three engineers starting tomorrow with only this document and the
approved frozen document stack can build the Measurement Integrity
Intelligence Engine (MIIE) v1.0 such that:

> All modules integrate via identical contracts
>
> All workflows produce identical outputs given identical inputs
>
> All benchmarks meet precision/recall targets
>
> All reproducibility requirements are satisfied
>
> All documentation enables immediate usage

**Implementation** **may** **commence** **immediately.**

*End* *of* *Implementation* *Master* *Plan* *(IMP* *v1.0)* *Measurement*
*Integrity* *Intelligence* *Engine* *(MIIE)* *Version* *1.0.0* *\|*
*2026-06-07*
