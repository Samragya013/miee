**Application** **Flow** **Document** **(AFD** **v1.0)** **System:**
Measurement Integrity Intelligence Engine (MIIE) **Version:** 1.0.0

**Status:** Workflow Authority — Ready for Backend Schema Design
**Date:** 2026-06-07

**Inputs:** IPD v1.1 FINAL \| PRD v1.0 \| TFS v1.0 \| BSD v1.0 \| TRD
v1.0

**Objective:** Define complete execution behavior such that three
independent engineering teams reading only the frozen documents and this
AFD produce functionally equivalent workflow behavior.

**SECTION** **1** **—** **EXECUTIVE** **SUMMARY**

**1.1** **Purpose** **of** **the** **AFD**

The Application Flow Document (AFD) is the **behavioral** **authority**
for MIIE v1.0. It governs:

> How users interact with the system to accomplish goals.
>
> How frozen modules (TRD §5) invoke one another during execution.
>
> How data moves through the pipeline and benchmark subsystems.
>
> How the system transitions between states, handles errors, recovers,
> and reports progress.
>
> How concurrent operations are isolated and synchronized.

**1.2** **Relationship** **to** **TRD**

> **TRD** **governs** **structure:** module interfaces, class contracts,
> directory layout, technology constraints, and performance budgets.
>
> **AFD** **governs** **behavior:** the exact order of module
> invocation, the data passed between them, the conditions for
> branching, and the handling of every failure mode.

**1.3** **Relationship** **to** **Implementation**

This document is **implementation-ready**. Backend developers may begin
schema design immediately because every workflow is decomposed into
unambiguous steps with defined inputs, outputs, validations, and state
transitions.

**1.4** **Relationship** **to** **Testing**

> **Unit** **tests** validate individual module contracts defined in
> TRD.
>
> **Integration** **tests** validate the orchestration sequences defined
> in this AFD (Sections 5–6).
>
> **System** **tests** validate end-to-end user journeys (Section 4).
>
> **Acceptance** **tests** validate traceability to PRD requirements
> (Section 16).
>
> **SECTION** **2** **—** **ACTOR** **MODEL**
>
> **2.1** **Human** **Actors**

||
||
||
||
||
||
||
||

> **2.2** **System** **Actors**

||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||

||
||
||
||
||
||

> **2.3** **External** **Actors**

||
||
||
||
||

**SECTION** **3** **—** **SYSTEM** **CONTEXT** **FLOW**

**3.1** **Context** **Diagram** **Summary**

┌─────────────────────────────────────────────────────────────────────────────┐
│ EXTERNAL ENVIRONMENT │ │ Git Repositories │ Coverage Artifacts │
PR/Issue Exports │ Config │ │ (User-provided) │ (In repo or path) │
(User-provided) │ Files │
└─────────────────────────────────────────────────────────────────────────────┘

> │ │ │ │ ▼ ▼ ▼ ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│ MIIE SYSTEM BOUNDARY │ │ ┌──────────┐ ┌──────────┐ ┌──────────┐
┌──────────┐ │ │ │ CLI │ │ REST API │ │ Config │ │ Registry │ │ │ │
(M-10) │ │ (M-11) │ │ (M-12) │ │ (M-13) │ │ │ └────┬─────┘ └────┬─────┘
└────┬─────┘ └────┬─────┘ │ │ │ │ │ │ │ │
└─────────────┴─────────────┴─────────────┘ │ │ │ │ │ ▼ │ │
┌─────────────────────────────────────────────────────────────────────┐
│ │ │ ORCHESTRATION LAYER │ │ │ │ Job Manager (M-14) │ Pipeline
Controller (M-15) │ State (M-16) │ │ │ │ Workflow Engine (M-17) │ │ │
└─────────────────────────────────────────────────────────────────────┘
│ │ │ │ │ ▼ │ │
┌─────────────────────────────────────────────────────────────────────┐
│ │ │ PROCESSING LAYER │ │ │ │ Ingest (M-01) → Extract (M-02) → Segment
(M-03) → Detect (M-05) │ │ │ │ → Score (M-08) → Evidence → Explain
(M-09) → Export (M-09) │ │ │
└─────────────────────────────────────────────────────────────────────┘
│ │ │ │ │ ▼ │ │
┌─────────────────────────────────────────────────────────────────────┐
│ │ │ BENCHMARK SUBSYSTEM │ │ │ │ Dataset Gen (M-03) → Ground Truth
(M-04) → Runner (M-06) → Eval │ │ │ │ (M-07) │ │ │
└─────────────────────────────────────────────────────────────────────┘
│ │ │ │ │ ▼ │ │
┌─────────────────────────────────────────────────────────────────────┐
│ │ │ OUTPUT BOUNDARY │ │ │ │ JSON / Markdown / CSV → User filesystem │
│ │
└─────────────────────────────────────────────────────────────────────┘
│
└─────────────────────────────────────────────────────────────────────────────┘

**3.2** **Actor** **Flow** **Definitions**

***User*** ***(SER*** ***/*** ***SAR*** ***/*** ***RM*** ***/***
***EER*** ***/*** ***BM)***

> **Incoming** **flows:** None (initiates all flows).
>
> **Outgoing** **flows:**
>
> To CLI: sys.argv strings, config file paths, repo paths.
>
> To API: HTTP POST JSON bodies (AnalyzeRequest, BenchmarkRequest).
>
> **Data** **exchanged:** Commands, parameters, file paths, JSON
> payloads.
>
> **Trigger** **conditions:** User decides to analyze a repo, run a
> benchmark, or export results.
>
> **Expected** **responses:** Exit code + files on disk (CLI); HTTP
> 202 + poll URL (API).

***CLI*** ***(M-10)***

> **Incoming** **flows:** From User (sys.argv).
>
> **Outgoing** **flows:**
>
> To CFG: config_path, cli_overrides.
>
> To WFE: workflow_id, workflow_params.
>
> To PLC: Configuration object (for analyze).
>
> To BRN: BenchmarkRequest (for benchmark).
>
> To FS: Write output files, logs.
>
> **Data** **exchanged:** Parsed arguments, configuration objects, exit
> codes (0–4).

***API*** ***(M-11)***

> **Incoming** **flows:** From User/API Client (HTTP requests).
>
> **Outgoing** **flows:**
>
> To JOB: job_type, job_params.
>
> To STM: State read/write requests.
>
> To PLC/BRN: Indirectly via JOB dispatch.
>
> **Data** **exchanged:** HTTP JSON bodies, job IDs, status JSON.

***Pipeline*** ***Controller*** ***(M-15)***

> **Incoming** **flows:** From CLI/WFE (Configuration); from REG
> (registry lookups).
>
> **Outgoing** **flows:**
>
> To ING: repo_path, cache_dir, keep_cache.
>
> To EXT: RepositoryContext, metric_list, since, until.
>
> To SEG: MetricDataFrame, window_strategy, window_size.
>
> To DET: MetricDataFrame, window_definitions, detector_config.
>
> To SCR: DetectorResults, MetricDataFrame, windows, weights.
>
> To EVA: All intermediate results.
>
> To EXP: EvidencePackage.
>
> To RPT: AnalysisResult, output_formats.
>
> **Data** **exchanged:** Domain objects (RepositoryContext,
> MetricDataFrame, Window, DetectorResults, ScorePackage,
> EvidencePackage, ExplanationReport).
>
> ***Benchmark*** ***Runner*** ***(M-06)***
>
> **Incoming** **flows:** From CLI/WFE (suite_id, detector_ids, config,
> seed).
>
> **Outgoing** **flows:**
>
> To GEN (indirect): Suite may reference generated datasets.
>
> To DET: Per-dataset metric data and windows.
>
> To EVL: BenchmarkRun object.
>
> **Data** **exchanged:** Dataset objects, prediction booleans, timing
> metadata.
>
> **SECTION** **4** **—** **CORE** **USER** **JOURNEYS**
>
> **4.1** **Workflow** **Inventory**

||
||
||
||
||
||
||
||
||

||
||
||
||
||

> **4.2** **WF-01:** **Analyze** **Repository**

||
||
||
||
||
||
||
||
||
||
||

||
||
||
||
||

> **4.3** **WF-02:** **Investigate** **Integrity** **Failure**

||
||
||
||
||
||
||
||
||
||
||
||
||

> **4.4** **WF-03:** **Run** **Benchmark** **Evaluation**

||
||
||
||
||
||
||
||
||
||
||
||
||

> **4.5** **WF-04:** **Export** **Results**

||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||

> **4.6** **WF-05:** **Compare** **Time** **Windows**

||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||

> **4.7** **WF-06:** **Generate** **Synthetic** **Dataset**

||
||
||
||
||
||
||
||
||
||
||

> **4.8** **WF-07:** **Manage** **Ground** **Truth**

||
||
||
||
||

||
||
||
||
||
||
||
||
||

> **SECTION** **5** **—** **END-TO-END** **EXECUTION** **FLOWS**
>
> **5.1** **Execution** **Flow** **Notation** Every step is defined as:
>
> **Step** **N:** Sequential number.
>
> **Actor:** The executing actor.
>
> **Action:** What the actor does.
>
> **Input:** Data consumed.
>
> **Output:** Data produced.
>
> **Validation:** Acceptance criteria before proceeding.
>
> **Next** **State:** The subsequent step or state.
>
> **5.2** **WF-01:** **Analyze** **Repository** **—** **Primary**
> **Success** **Path** **Step** **1:**
>
> **Actor:** User (SER/RM/EER)
>
> **Action:** Invoke CLI with miie analyze --repo \<path\> \[options\].
>
> **Input:** sys.argv string array.
>
> **Output:** None (triggers system).
>
> **Validation:** Shell accepts command.
>
> **Next** **State:** Step 2

**Step** **2:**

> **Actor:** CLI (M-10)
>
> **Action:** Parse global options (--config, --output, --verbose) and
> subcommand arguments (--repo, --since, --until, --metrics,
> --window-strategy, --detectors, --format).
>
> **Input:** sys.argv.
>
> **Output:** Parsed args dict; exit code 3 if invalid.
>
> **Validation:** All required arguments present (--repo); unknown flags
> rejected; --since ≤ --until if both provided.
>
> **Next** **State:** Step 3

**Step** **3:**

> **Actor:** CFG (M-12)
>
> **Action:** Load YAML/JSON config file; merge CLI overrides (CLI takes
> precedence); apply defaults; validate against strict schema (reject
> unknown fields); validate metric IDs and detector IDs against REG.
>
> **Input:** config_path (default ~/.miie/config.yaml), cli_overrides
> dict.
>
> **Output:** Configuration object; config_hash (SHA-256).
>
> **Validation:** Schema validation passes; all metric IDs ∈
> {M-01..M-07, all}; all detector IDs ∈ {D-01..D-03, all};
> window_strategy ∈ {time, commit, release, custom}.
>
> **Next** **State:** Step 4

**Step** **4:**

> **Actor:** CLI / WFE (M-17)
>
> **Action:** Dispatch to Workflow 1 (Analyze Repository). WFE validates
> workflow inputs and invokes PLC.
>
> **Input:** Configuration object.
>
> **Output:** Workflow dispatch confirmation.
>
> **Validation:** Workflow params valid; no missing prior analysis.
>
> **Next** **State:** Step 5

**Step** **5:**

> **Actor:** PLC (M-15)
>
> **Action:** Begin pipeline execution. Stage: INIT. Register progress
> callback. Invoke ING.
>
> **Input:** Configuration object.
>
> **Output:** Pipeline session context.
>
> **Validation:** Configuration object non-null.
>
> **Next** **State:** Step 6

**Step** **6:**

> **Actor:** ING (M-01)
>
> **Action:** Stage: INGEST. Validate repo path/URL. If remote: clone to
> ~/.miie/cache/repos/{repo_id}/. If local: validate .git directory. Run
> git rev-parse --git-dir, git log --oneline -n 1, git log --format=%H
> (count ≥ 10). Extract metadata: total_commits, first_commit_date,
> last_commit_date, contributor_count, is_shallow, is_fork. Compute
> repo_id = SHA-256 of remote URL or absolute path.
>
> **Input:** repo_path, cache_dir, keep_cache, shallow_depth.
>
> **Output:** RepositoryContext object.
>
> **Validation:** Path exists; .git readable; ≥10 commits; ≥1
> contributor; git commands return 0. If any fail: raise specific
> RepositoryError.
>
> **Next** **State:** Step 7 (on success) or Error Flow E-01 (on
> failure).

**Step** **7:**

> **Actor:** EXT (M-02)
>
> **Action:** Stage: EXTRACT. Iterate over enabled metrics. For each:
>
> M-01: Parse coverage artifacts (priority: coverage.xml \> lcov.info \>
> .coverage \> cobertura.xml). Extract line coverage %.
>
> M-02: git log --since --until --format=%H,%aI,%ae --no-merges. Count
> per day. Exclude bots if configured.
>
> M-03: Parse PR export; count reviewers per PR; mean per window.
>
> M-04: Parse PR export; compute first_review_at - created_at hours;
> median per window.
>
> M-05: Parse issue export; compute closed_at - created_at days for
> closed issues; median per window.
>
> M-06: git log --numstat --no-merges; sum additions+deletions; exclude
> binary files; mean per window.
>
> M-07: Checkout each commit; run lizard or radon on source files; mean
> complexity per commit; aggregate per window.
>
> **Input:** RepositoryContext, metric_list, since, until, exclude_bots.
>
> **Output:** MetricDataFrame (pandas DataFrame: commit_hash, timestamp,
> metric_id, value).
>
> **Validation:** All values numeric or null; values in plausible ranges
> (M-01: \[0,100\], M-02: ≥0, etc.). Non-numeric coerced to null with
> warning. Missing metrics logged but do not abort.
>
> **Next** **State:** Step 8 (if at least one metric extracted) or Error
> Flow E-05 (if zero metrics).

**Step** **8:**

> **Actor:** SEG (M-03)
>
> **Action:** Stage: SEGMENT. Apply window_strategy to MetricDataFrame.
> Produce non-overlapping, chronologically ordered windows. Strategies:
>
> time: Fixed duration (e.g., 30 days).
>
> commit: Fixed commit count per window.
>
> release: Split at git tags matching release pattern.
>
> custom: User-defined boundaries.
>
> **Input:** MetricDataFrame, window_strategy, window_size.
>
> **Output:** List\[Window\] (each with window_id, start_date, end_date,
> commit_count).
>
> **Validation:** Windows non-overlapping; ordered; each window has ≥1
> commit; total windows ≥ 2 (required for drift detection). If \<2 valid
> windows: abort.
>
> **Next** **State:** Step 9

**Step** **9:**

> **Actor:** DET (M-05)
>
> **Action:** Stage: DETECT. For each enabled detector:
>
> **D-01:** For each metric, for each consecutive window pair (Wi,
> Wi+1): Check sample size ≥ 10. Run scipy.stats.ks_2samp. Compute PSI
> with 10 equal-width bins. Classify direction (mean_shift,
> variance_collapse, shape_change). Severity = min(1.0, ks_statistic /
> 0.5).
>
> **D-02:** For each metric pair (i \< j), for each window: Check paired
> observations ≥ 10. Compute Pearson and Spearman. Check sudden drop
> (Δ\|r\| \> 0.3), sign reversal, gradual erosion (slope \< -0.1), CI
> exclusion. Severity = min(1.0, \|delta_r\| / 0.3).
>
> **D-03:** For each metric, for each window: Check sample size ≥ 20.
> Determine thresholds (explicit + auto-detected). Compute margin ε =
> max(0.02×T, 0.01×range). Run excess mass binomial test. Run Hartigans'
> dip test (bootstrap n=1000, seed=42). Flag if excess mass significant
> AND (multimodal OR p_hat \> 0.5). Severity = compression_index.
>
> **Input:** MetricDataFrame, window_definitions, detector_config,
> enabled_detectors.
>
> **Output:** DetectorResults object (nested dict per
> detector/metric/window).
>
> **Validation:** All statistical values in valid ranges (p-values ∈
> \[0,1\], PSI ≥ 0, etc.). Insufficient data → skip with warning; zero
> variance → skip with warning; numerical error → skip with warning. At
> least one detector must produce results for at least one metric.
>
> **Next** **State:** Step 10

**Step** **10:**

> **Actor:** SCR (M-08)
>
> **Action:** Stage: SCORE. Compute per-metric Integrity Score:
>
> For each metric M: extract severities d1, d2, d3 from DetectorResults.
>
> If detector skipped on M: redistribute its weight proportionally to
> other detectors for that metric.
>
> IS_metric = 1.0 - (w1×d1 + w2×d2 + w3×d3); clamp to \[0,1\].
>
> IS_overall = mean(IS_metric for all available M).
>
> Compute Confidence Score factors: f1 = min(1.0, mean_n / 50.0)
>
> f2 = 1.0 - min(1.0, mean_CV / 0.5)
>
> f3 = 1.0 - missing_pairs / total_pairs
>
> f4 = 1.0 - min(1.0, std_sizes / mean_sizes)
>
> f5 = successful_runs / total_attempts
>
> CS = f1 × f2 × f3 × f4 × f5; clamp to \[0,1\].
>
> **Input:** DetectorResults, MetricDataFrame, window_definitions,
> detector_weights.
>
> **Output:** ScorePackage (integrity: overall + per_metric; confidence:
> overall + factors).
>
> **Validation:** IS ∈ \[0,1\]; CS ∈ \[0,1\]; weight sum = 1.0
> (normalized if not). If all metrics unavailable: raise ScoreError →
> abort.
>
> **Next** **State:** Step 11

**Step** **11:**

> **Actor:** EVA (Evidence Aggregator)
>
> **Action:** Stage: EVIDENCE. Collect all intermediate artifacts into
> structured EvidencePackage:
>
> Provenance: miie_version, config_hash, timestamp, seed, platform.
>
> Windows: definitions with commit counts.
>
> Metrics: raw MetricDataFrame summary.
>
> Detector outputs: full statistical metadata (test names, statistics,
> p-values, window
>
> IDs, sample sizes, directions, CIs).
>
> Scores: IS and CS with formulas.
>
> **Input:** All intermediate objects from Steps 6–10.
>
> **Output:** EvidencePackage object.
>
> **Validation:** Evidence package schema valid (JSON Schema draft-07).
> All positive detector flags have associated statistical evidence.
>
> **Next** **State:** Step 12

**Step** **12:**

> **Actor:** EXP (M-09)
>
> **Action:** Stage: EXPLAIN. Apply deterministic rule-to-template
> mapping using Jinja2:
>
> IF D-01 fired → load drift_explanation.j2 template with metric, window
> pair, test name, statistic, p-value, direction.
>
> IF D-02 fired → load correlation_explanation.j2 with metric pair,
> trajectory, breakdown type.
>
> IF D-03 fired → load compression_explanation.j2 with metric,
> threshold, compression index, hypothesized cause.
>
> Include confidence band interpretation (High/Medium/Low/Critical per
> TFS §7.6).
>
> Append disclaimer: human oversight required.
>
> **Input:** EvidencePackage, ScorePackage.
>
> **Output:** ExplanationReport (structured object + Markdown string).
>
> **Validation:** Every explanation cites specific detector, test, and
> threshold. No opaque ML model references. Templates must exist
> (TemplateNotFoundError → abort if missing).
>
> **Next** **State:** Step 13

**Step** **13:**

> **Actor:** RPT (M-09)
>
> **Action:** Stage: EXPORT. Render outputs:
>
> JSON: Full structured result per Evidence Package Schema (TFS Appendix
> A).
>
> Markdown: Narrative report per report.j2 template (Header, Executive
> Summary, Per-Metric Analysis, Evidence Details, Recommendations,
> Disclaimer, Appendix).
>
> CSV: Tabular raw metrics and scores per window.
>
> Include manifest.json with provenance and checksums.
>
> **Input:** ScorePackage, DetectorResults, EvidencePackage,
> ExplanationReport, output_formats.
>
> **Output:** Files written to --output directory (results.json,
> report.md, metrics.csv, manifest.json, evidence.json,
> run_metrics.json).
>
> **Validation:** JSON schema validation passes; Markdown non-empty; CSV
> has header row. Disk space check before writing. If disk full: partial
> save attempted; raise IOError.
>
> **Next** **State:** Step 14

**Step** **14:**

> **Actor:** CLI (M-10)
>
> **Action:** Return exit code to shell. Write final progress to stderr.
>
> **Input:** IS_overall from ScorePackage.
>
> **Output:** Exit code 0 if IS_overall = 1.0; Exit code 1 if IS_overall
> \< 1.0.
>
> **Validation:** All files exist in output directory.
>
> **Next** **State:** Terminal (workflow complete).

**5.3** **WF-03:** **Run** **Benchmark** **Evaluation** **—**
**Primary** **Success** **Path** **Step** **1:**

> **Actor:** User (SAR)
>
> **Action:** miie benchmark --suite metric-drift-v1 --detectors D-01
> --seed 42
>
> **Next** **State:** Step 2

**Step** **2:**

> **Actor:** CLI (M-10)
>
> **Action:** Parse args; validate --suite is provided.
>
> **Next** **State:** Step 3

**Step** **3:**

> **Actor:** CFG (M-12)
>
> **Action:** Load config; validate detector IDs.
>
> **Next** **State:** Step 4

**Step** **4:**

> **Actor:** WFE (M-17)
>
> **Action:** Dispatch Workflow 3. Validate that suite exists in
> ~/.miie/benchmarks/.
>
> **Next** **State:** Step 5

**Step** **5:**

> **Actor:** BRN (M-06)
>
> **Action:** Load suite manifest (manifest.json). Validate schema
> version compatible with detector. Load all dataset directories. Load
> ground truth (hidden from detector logic).
>
> **Input:** suite_id, detector_ids, config, seed.
>
> **Output:** Suite manifest, list of Dataset objects, GroundTruth
> object.
>
> **Validation:** Suite exists; all datasets load successfully; ground
> truth labels present; detector declares compatible benchmark version
> range.
>
> **Next** **State:** Step 6

**Step** **6:**

> **Actor:** BRN (M-06)
>
> **Action:** For each detector in detector_ids: Instantiate detector
> once with config.
>
> For each dataset in suite:
>
> Load metrics.json and windows.json.
>
> Validate dataset schema.
>
> Invoke DET on isolated dataset (no cross-dataset access).
>
> Record prediction (bool), confidence (float), execution time, memory.
>
> **Input:** Dataset objects, detector config, seed.
>
> **Output:** BenchmarkRun object (predictions, timing, metadata).
>
> **Validation:** Predictions match ground truth structure (same keys).
> No ground truth leakage (enforced by runner sandboxing). Temporal
> isolation: no future window access.
>
> **Next** **State:** Step 7

**Step** **7:**

> **Actor:** EVL (M-07)
>
> **Action:** Match predictions to labels by (dataset_id, metric_id,
> context). Compute:
>
> TP = predicted=True and label=True
>
> FP = predicted=True and label=False
>
> TN = predicted=False and label=False
>
> FN = predicted=False and label=True
>
> accuracy = (TP+TN)/total
>
> precision = TP/(TP+FP) or 0.0
>
> recall = TP/(TP+FN) or 0.0
>
> F1 = 2pr/(p+r) or 0.0
>
> AUC-ROC, AUC-PR via sklearn (trapezoidal rule)
>
> FPR = FP/(FP+TN) or 0.0
>
> FNR = FN/(FN+TP) or 0.0
>
> Aggregate per-dataset (macro) and overall (weighted by dataset size).
>
> **Input:** BenchmarkRun, GroundTruth.
>
> **Output:** EvaluationResult object.
>
> **Validation:** All metrics ∈ \[0,1\]; confusion matrix values
> non-negative integers; TP+FP+TN+FN = total instances. Division by zero
> handled (return 0.0 with warning).
>
> **Next** **State:** Step 8

**Step** **8:**

> **Actor:** RPT (M-09)
>
> **Action:** Render benchmark report: JSON with full EvaluationResult;
> Markdown with confusion matrix, metrics table, per-dataset breakdown,
> baseline comparison.
>
> **Input:** EvaluationResult, BenchmarkRun.
>
> **Output:** Benchmark report files.
>
> **Next** **State:** Step 9

**Step** **9:**

> **Actor:** CLI (M-10)
>
> **Action:** Return exit code 0.
>
> **Next** **State:** Terminal.

**SECTION** **6** **—** **MODULE** **ORCHESTRATION** **FLOWS**

**6.1** **Orchestration** **Principles**

> 1\. **Direct** **invocation:** All module calls are direct Python
> function calls (not RPC or message queues).
>
> 2\. **Single-threaded** **default:** Processing layer is
> single-threaded unless explicitly parallelized for benchmarks.
>
> 3\. **No** **circular** **dependencies:** The dependency graph is a
> DAG.
>
> 4\. **Fail-forward** **with** **degradation:** A stage failure does
> not abort the pipeline unless it is fatal (e.g., repo missing, no
> valid windows, all metrics unavailable).

**6.2** **WF-01** **Module** **Invocation** **Order**

CLI(M-10)

> → CFG(M-12) \[loads config, returns Configuration\] → WFE(M-17)
> \[dispatches WF-01\]
>
> → PLC(M-15) \[orchestrates pipeline\]
>
> → REG(M-13) \[lookup metric/detector definitions\] → ING(M-01)
> \[returns RepositoryContext\]
>
> → EXT(M-02) \[returns MetricDataFrame\] → SEG(M-03) \[returns
> List\[Window\]\]
>
> → DET(M-05) \[returns DetectorResults\] → SCR(M-08) \[returns
> ScorePackage\]
>
> → EVA \[returns EvidencePackage\]
>
> → EXP(M-09) \[returns ExplanationReport\] → RPT(M-09) \[writes files\]
>
> **6.3** **WF-03** **Module** **Invocation** **Order**
>
> CLI(M-10)
>
> → CFG(M-12)
>
> → WFE(M-17) \[dispatches WF-03\]
>
> → BRN(M-06) \[loads suite, iterates datasets\] → DET(M-05) \[per
> dataset\]
>
> → EVL(M-07) \[post-run\]
>
> → RPT(M-09) \[writes benchmark report\]
>
> **6.4** **Module** **Dependency** **Matrix**

||
||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **SECTION** **7** **—** **DATA** **FLOW** **ARCHITECTURE**
>
> **7.1** **Analysis** **Pipeline** **Data** **Lineage**

||
||
||
||

||
||
||
||
||
||
||
||
||
||
||

> **7.2** **Benchmark** **Pipeline** **Data** **Lineage**

||
||
||
||
||
||
||

> **7.3** **Data** **Retention** **and** **Deletion**

||
||
||
||
||
||
||
||
||
||
||

> **SECTION** **8** **—** **STATE** **MACHINE** **MODEL**
>
> **8.1** **API** **Job** **State** **Machine**
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

> **8.2** **Analysis** **Stage** **State** **Machine**
>
> \[INIT\] ──→ \[INGEST\] ──→ \[EXTRACT\] ──→ \[SEGMENT\] ──→ \[DETECT\]
>
> │ \[EXPORT\] ←── \[EXPLAIN\] ←── \[EVIDENCE\] ←── \[SCORE\]

||
||
||
||
||
||
||
||
||
||
||
||

> **8.3** **State** **Transition** **Rules**
>
> 1\. **Forward-only:** Analysis stages progress monotonically from INIT
> to EXPORT. No backward transitions.
>
> 2\. **Graceful** **degradation:** A non-fatal failure in a stage does
> not block progression to the next stage; the failure is recorded in
> the evidence package.
>
> 3\. **Fatal** **abort:** Fatal failures (INGEST, SEGMENT, SCORE,
> EXPORT disk full) abort the pipeline. Partial results up to the
> previous stage are saved to the output directory if possible.
>
> 4\. **State** **persistence** **(API):** Every transition is
> atomically written to state.json (write to temp file, then rename).
>
> **SECTION** **9** **—** **ERROR** **FLOW** **ARCHITECTURE**
>
> **9.1** **Error** **Taxonomy**

||
||
||
||

||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||

> **9.2** **Error** **Propagation** **Rules**
>
> 1\. **CLI** **boundary:** All exceptions are caught at the CLI/API
> boundary. No uncaught exceptions reach the user.
>
> 2\. **Exit** **code** **mapping:**
>
> Invalid input / user error → Exit 3
>
> System error / unexpected exception → Exit 2
>
> Benchmark-specific failure → Exit 4
>
> Success with integrity failures → Exit 1
>
> Success with no failures → Exit 0
>
> 3\. **Partial** **results:** If a fatal error occurs after stage N,
> all artifacts from stages 1..(N-1) are written to the output directory
> before aborting.
>
> 4\. **Evidence** **integrity:** Every error is recorded in the
> evidence package with: error code, timestamp, stage, affected
> metric/detector, and recovery action taken.

**SECTION** **10** **—** **WORKFLOW** **SEQUENCE** **DIAGRAMS**

**10.1** **WF-01:** **Repository** **Analysis** **(CLI** **Mode)**

User

> → CLI(M-10): analyze --repo ./repo --since 2025-01-01 CLI → CFG(M-12):
> load_config(path, overrides)
>
> CFG → REG(M-13): validate_metric_ids(), validate_detector_ids() CFG →
> CLI: Configuration object
>
> CLI → WFE(M-17): dispatch("WF-01", Configuration) WFE → PLC(M-15):
> run_analysis(Configuration)
>
> PLC → ING(M-01): ingest(repo_path, cache_dir) ING → GIT: git clone /
> git log
>
> GIT → ING: commit stream, metadata ING → PLC: RepositoryContext
>
> PLC → EXT(M-02): extract(RepositoryContext, metrics, since, until) EXT
> → GIT: git log --numstat
>
> EXT → FS: parse coverage.xml, pr_export.json, issue_export.json EXT →
> PLC: MetricDataFrame
>
> PLC → SEG(M-03): segment(MetricDataFrame, strategy, size) SEG → PLC:
> List\[Window\]
>
> PLC → DET(M-05): detect(MetricDataFrame, Windows, config) DET → PLC:
> DetectorResults

PLC → SCR(M-08): score(DetectorResults, MetricDataFrame, Windows,
weights)

> SCR → PLC: ScorePackage
>
> PLC → EVA: aggregate(all intermediates) EVA → PLC: EvidencePackage
>
> PLC → EXP(M-09): explain(EvidencePackage, ScorePackage) EXP → PLC:
> ExplanationReport
>
> PLC → RPT(M-09): export(AnalysisResult, formats)
>
> RPT → FS: write results.json, report.md, metrics.csv RPT → PLC: file
> paths
>
> PLC → WFE: AnalysisResult WFE → CLI: workflow complete
>
> CLI → User: Exit code 0/1 + files in ./miie-output/

**10.2** **WF-03:** **Benchmark** **Evaluation**

User

> → CLI(M-10): benchmark --suite metric-drift-v1 --detectors D-01 CLI →
> CFG(M-12): load_config
>
> CLI → WFE(M-17): dispatch("WF-03", params)
>
> WFE → BRN(M-06): run_benchmark(suite_id, detectors, config, seed) BRN
> → FS: load suite manifest, datasets, ground_truth.json (hidden) BRN →
> DET(M-05): for each dataset:
>
> DET → BRN: predictions per dataset
>
> BRN → EVL(M-07): evaluate(BenchmarkRun, GroundTruth) EVL → BRN:
> EvaluationResult
>
> BRN → RPT(M-09): render_benchmark_report(EvaluationResult) RPT → FS:
> write benchmark_run.json, benchmark_report.md
>
> BRN → WFE: BenchmarkRun + EvaluationResult WFE → CLI: workflow
> complete
>
> CLI → User: Exit code 0 + files in ./miie-output/

**10.3** **WF-02:** **Investigate** **Integrity** **Failure**

User

> → CLI(M-10): explain --input ./analysis-2025/ --metric M-01 CLI →
> WFE(M-17): dispatch("WF-02", params)
>
> WFE → FS: validate input directory exists
>
> WFE → EVA: load EvidencePackage from evidence.json
>
> WFE → EXP(M-09): explain(EvidencePackage, metric_filter=M-01) EXP →
> WFE: ExplanationReport
>
> WFE → RPT(M-09): write_explanation(ExplanationReport) RPT → FS:
> overwrite report.md in input directory
>
> WFE → CLI: workflow complete
>
> CLI → User: Exit code 0 + updated report.md

**10.4** **WF-05:** **Compare** **Time** **Windows**

User

> → CLI(M-10): analyze --repo ./repo --window-strategy time
> --window-size 30 CLI → WFE: dispatch("WF-01", Config A)
>
> WFE → PLC: run Analysis A → Result A User
>
> → CLI(M-10): analyze --repo ./repo --window-strategy time
> --window-size 90 CLI → WFE: dispatch("WF-01", Config B)
>
> WFE → PLC: run Analysis B → Result B User

→ CLI(M-10): compare --input-a ./out-a --input-b ./out-b (or internal
WFE command)

> CLI → WFE: dispatch("WF-05", {result_a, result_b}) WFE → SCR: load
> ScorePackage A, ScorePackage B WFE → EVA: compute_delta_scores(A, B)
>
> WFE → RPT: render_comparison_report(delta, explanations) RPT → FS:
> write comparison_report.md
>
> WFE → CLI: workflow complete
>
> CLI → User: Exit code 0 + comparison_report.md

**10.5** **API** **Async** **Job** **Flow**

API Client

> → API(M-11): POST /v1/analyze {repo, since, until, ...} API →
> JOB(M-14): create_job("analyze", params)
>
> JOB → STM(M-16): write_job_manifest(job_id, params)
>
> JOB → API: {job_id, status: "queued", poll_url: "/v1/jobs/{job_id}"}
> API → API Client: HTTP 202 Accepted

API Client

> → API(M-11): GET /v1/jobs/{job_id} API → STM(M-16): read_state(job_id)
>
> STM → API: JobState {status: "running", progress: 0.45, stage:
> "detect"} API → API Client: HTTP 200 OK

(Background Worker)

> JOB → PLC(M-15): run_analysis(params) PLC → ... (same as WF-01
> sequence) ... PLC → JOB: AnalysisResult
>
> JOB → STM: update_state(job_id, "completed", results_path) JOB → FS:
> write results to job-specific subdirectory
>
> API Client
>
> → API(M-11): GET /v1/jobs/{job_id}/results API → FS: read results.json
>
> API → API Client: HTTP 200 OK + JSON body
>
> **SECTION** **11** **—** **CONCURRENCY** **MODEL**
>
> **11.1** **Concurrency** **Scope**
>
> MIIE v1.0 is **single-threaded** **by** **default** for the analysis
> pipeline. Concurrency is explicitly introduced only in:
>
> 1\. **Benchmark** **Runner** **(M-06):** Optional parallel dataset
> processing.
>
> 2\. **API** **Mode** **(M-11/M-14):** Multiple jobs may be queued; a
> single worker processes one job at a time (V1 simplicity).
>
> **11.2** **Parallel** **Workflow:** **Benchmark** **Execution**
>
> **Trigger:** miie benchmark with --parallel flag or default
> processes=min(4, cpu_count()).
>
> **Shared** **resources:** None between dataset processes. Each worker
> receives an isolated dataset directory.
>
> **Synchronization:** Main process collects results via
> multiprocessing.Pool. No locks required.
>
> **Race-condition** **prevention:** Each worker gets a derived seed
> (seed + worker_id) to maintain deterministic random state. No shared
> RNG state.
>
> **Thread/process** **behavior:** Processes, not threads, to bypass
> Python GIL and isolate memory.
>
> **11.3** **Safe** **Parallel** **Execution** **Rules**
>
> 1\. **No** **shared** **mutable** **state:** Workers receive read-only
> dataset objects and write to separate result slots in the parent
> process.
>
> 2\. **Filesystem** **isolation:** Workers write to temporary
> subdirectories if needed; final aggregation is sequential.
>
> 3\. **Determinism:** Parallel execution must produce identical
> BenchmarkRun objects as sequential execution (verified by sorting
> dataset IDs before aggregation).
>
> **11.4** **Shared** **Resources** **and** **Locking**

||
||
||
||

||
||
||
||
||
||
||

> **11.5** **Concurrency** **Restrictions**
>
> **No** **parallel** **analysis** **pipelines:** A single repository
> analysis runs in one thread/process.
>
> **No** **concurrent** **API** **job** **workers** **in** **V1:** The
> API uses a single worker model. Jobs are queued and processed
> sequentially. This avoids state manager complexity.
>
> **Future:** V1.1 may introduce multi-worker API processing with
> file-based locking.
>
> **SECTION** **12** **—** **PERFORMANCE** **FLOWS**
>
> **12.1** **Workflow** **Runtime** **Targets**

||
||
||
||
||
||
||

||
||
||
||
||
||

> **12.2** **Detector** **Runtime** **Targets**

||
||
||
||
||
||

> **12.3** **Scaling** **Behavior**
>
> **Commits:** Processing scales linearly with commit count up to 50k.
> Beyond 50k, auto-sampling triggers.
>
> **Metrics:** Fixed at 7 frozen metrics. Extraction is O(M × C) where C
> = commits.
>
> **Windows:** Segmentation is O(C). Detection is O(M × W × n) where n =
> values per window.
>
> **Memory:** Peak memory \< 4GB for 100k commits. Streaming extraction
> (generators) used if \>50k commits.
>
> **12.4** **Optimization** **Opportunities**
>
> 1\. **Incremental** **extraction:** Cache parsed PR/issue exports
> between runs (V1.1).
>
> 2\. **Parallel** **window** **processing:** For D-01 and D-02, windows
> are independent and could be processed in parallel (V1.1).
>
> 3\. **Lazy** **checkout:** For M-07, use git show {commit}:file
> instead of full checkout to reduce I/O.
>
> 4\. **Checkpointing:** Save MetricDataFrame to disk after extraction
> to allow resume (V1.1).
>
> **SECTION** **13** **—** **OBSERVABILITY** **FLOW**
>
> **13.1** **Log** **Flow**

||
||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||

> **13.2** **Metrics** **Flow**
>
> **Runtime** **metrics:** run_metrics.json records per-stage duration,
> memory peak, CPU time.
>
> **Benchmark** **metrics:** benchmark_run.json records per-dataset
> execution time and memory.
>
> **Detector** **metrics:** Per-detector success rate, skip rate,
> average execution time.
>
> **API** **metrics:** Request count, queue depth, job completion time
> (if API enabled).
>
> **13.3** **Execution** **Traces**
>
> **Analysis** **trace:** Embedded in evidence.json as
> provenance.execution_trace: ordered list of stages with timestamps and
> durations.
>
> **Benchmark** **trace:** benchmark_run.json includes timing object
> with per-dataset durations.
>
> **API** **trace:** state.json history array records all state
> transitions with timestamps.

**13.4** **Audit** **Records**

> **Manifest:** Every run produces manifest.json with:
>
> miie_version, git_commit, python_version, dependency_hash,
> config_hash, seed, timestamp, platform.
>
> **Benchmark** **manifest:** run_manifest.json with detector version,
> benchmark version, environment hash.
>
> **Ground** **truth** **audit:** Every label includes annotator_id,
> timestamp, modification_history, checksum.

**13.5** **Diagnostic** **Artifacts**

> **Evidence** **package:** evidence.json is the primary diagnostic
> artifact for failure investigation.
>
> **Partial** **results:** On abort, the output directory contains all
> artifacts from completed stages.
>
> **Job** **logs:** API jobs write dedicated log files to
> ~/.miie/jobs/{job_id}/log.txt.

**13.6** **Failure** **Investigation** **Workflow** 1. User observes
exit code 2 or 1.

> 2\. User reads stderr for error code and suggestion.
>
> 3\. If --verbose was used, user inspects detailed debug logs.
>
> 4\. User opens evidence.json to identify which stage failed and which
> metric/detector was affected.
>
> 5\. User opens manifest.json to verify environment and config.
>
> 6\. User re-runs with identical --seed and --config to reproduce.
>
> 7\. If reproducible, user files bug report with manifest.json,
> evidence.json, and stderr output.

**SECTION** **14** **—** **SECURITY** **FLOW**

**14.1** **Input** **Validation**

> **Path** **resolution:** All file paths resolved via
> pathlib.Path.resolve() to prevent directory traversal.
>
> **URL** **validation:** Only https:// and ssh:// schemes permitted for
> remote repos. file://, javascript://, and other schemes rejected.
>
> **Config** **validation:** Strict JSON/YAML schema; unknown fields
> rejected. Safe loaders only (no yaml.load(unsafe)).
>
> **Metric** **value** **validation:** All values validated as numeric
> before statistical operations. Non-
>
> numeric coerced to null.
>
> **Threshold** **validation:** D-03 thresholds must be within data
> range; margin ≤ 5% of data range.

**14.2** **Permission** **Checks**

> **CLI** **mode:** Runs with user's OS permissions. No privilege
> escalation.
>
> **API** **mode:** Binds to 127.0.0.1 by default. Optional API key via
> Authorization: Bearer \<token\> header for networked mode. No user
> management or sessions.
>
> **Filesystem:** Output directory must be writable. Cache directory
> created with 0o700 permissions.

**14.3** **File** **Handling**

> **Coverage** **artifact** **parsers:** Validate XML structure before
> parsing. File size limit: 1GB per artifact. Abort if exceeded.
>
> **PR/issue** **exports:** Validate against expected JSON schema.
> Unknown fields rejected (strict mode).
>
> **Benchmark** **datasets:** Checksum verification (SHA-256) on load.
> Corrupted datasets rejected.
>
> **No** **arbitrary** **file** **execution:** No eval(), exec(), or
> dynamic code execution of user input.

**14.4** **Execution** **Isolation**

> **Git** **commands:** Executed via subprocess with sanitized arguments
> (no shell=True). Arguments passed as list.
>
> **Static** **analysis** **tools:** radon and lizard run in subprocess
> isolation. Timeout enforced (60s per call).
>
> **No** **network** **during** **analysis:** After initial clone, all
> processing is offline. No API calls to GitHub/GitLab during
> detection/scoring.
>
> **Detector** **sandboxing:** Benchmark runner prevents detectors from
> accessing files outside the dataset directory or reading
> ground_truth.json.

**14.5** **Artifact** **Protection**

> **Checksums:** results.json includes SHA-256 of evidence.json and raw
> metrics. manifest.json includes checksums.
>
> **Integrity** **verification:** Optional verify_checksum() function
> using hmac.compare_digest().
>
> **Ground** **truth** **isolation:** Positive labels require evidence.
> No label without documented statistical and visual evidence.
>
> **14.6** **Data** **Leakage** **Prevention**
>
> **Temporal** **isolation:** Detectors cannot access future windows
> when evaluating past windows.
>
> **Cross-dataset** **isolation:** Benchmark detectors cannot share
> information across datasets.
>
> **Ground** **truth** **isolation:** Detector code is blocked from
> reading ground_truth.json by the benchmark runner.
>
> **Post-hoc** **threshold** **prohibition:** Detector thresholds frozen
> by TFS; no tuning on benchmark labels permitted.
>
> **SECTION** **15** **—** **TESTABILITY** **FLOW**
>
> **15.1** **Unit** **Test** **Boundaries**

||
||
||
||
||
||
||
||
||
||

||
||
||
||
||

> **15.2** **Integration** **Test** **Boundaries**

||
||
||
||
||
||
||
||
||

> **15.3** **System** **Test** **Boundaries**

||
||
||
||
||
||
||
||
||

> **15.4** **Acceptance** **Test** **Boundaries**

||
||
||
||
||
||
||
||
||
||
||

> **15.5** **Required** **Mock** **Components**
>
> **MockGit:** Simulates git clone, git log, git rev-parse with
> deterministic output.
>
> **MockRepository:** In-memory repository with known commit history,
> PRs, issues, coverage artifacts.
>
> **MockDetector:** Deterministic detector that returns pre-configured
> results for testing SCR/EVA/EXP.
>
> **MockFilesystem:** Fake filesystem for testing RPT output without
> disk I/O.
>
> **MockBenchmarkSuite:** Minimal 3-dataset suite with known ground
> truth for fast EVL testing.
>
> **MockAPIClient:** HTTP client simulator for testing M-11 endpoints
> without server startup.
>
> **SECTION** **16** **—** **IMPLEMENTATION** **TRACEABILITY**
>
> **16.1** **Traceability** **Matrix:** **Workflows** **→** **Modules**
> **→** **Requirements** **→** **Specs** **→** **Benchmarks**

||
||
||
||
||
||
||
||
||
||
||
||
||
||

||
||
||
||
||
||
||
||
||
||
||
||
||
||

> **16.2** **Requirement** **Coverage** **Verification**
>
> **PRD** **§7** **(In** **Scope):** All items covered by WF-01 modules
> (M-01, M-02, M-03, M-05, M-08, M-09).
>
> **PRD** **§9** **(Version** **1** **Freeze):** All 5 frozen workflows
> (WF-01–WF-05) mapped to M-17.
>
> **TFS** **§13** **(CLI** **Freeze):** All commands (analyze,
> benchmark, explain, export, generate, detect, evaluate, ingest) mapped
> to M-10.
>
> **TFS** **§14** **(API** **Freeze):** All endpoints (/v1/analyze,
> /v1/benchmark, /v1/explain, /v1/export, /v1/jobs, /v1/health) mapped
> to M-11.
>
> **BSD** **§5** **(Benchmark** **Tasks):** B-01, B-02, B-03 mapped to
> WF-03 via M-06 and M-07.
>
> **BSD** **§9** **(Pathology** **Injection):** Mapped to WF-06 via M-03
> (Dataset Generator).
>
> **BSD** **§10–11** **(Ground** **Truth):** Mapped to WF-07 via M-04.
>
> **SECTION** **17** **—** **AMBIGUITY** **AUDIT**
>
> **17.1** **Workflow** **Ambiguity**

||
||
||
||
||
||
||

> **17.2** **State** **Ambiguity**

||
||
||
||
||

||
||
||
||

> **17.3** **Error** **Ambiguity**

||
||
||
||
||
||

> **17.4** **Data** **Ambiguity**

||
||
||
||
||
||

||
||
||
||
||

> **17.5** **Execution** **Ambiguity**

||
||
||
||
||
||
||

**SECTION** **18** **—** **FINAL** **AFD** **VERDICT**

**18.1** **Primary** **Question**

If three independent engineering teams read only:

> IPD v1.1 FINAL
>
> PRD v1.0
>
> TFS v1.0
>
> BSD v1.0
>
> TRD v1.0
>
> **This** **AFD** **v1.0**

Would they design the same workflow behavior?

**18.2** **Answer** **YES.**

**18.3** **Justification**

Three independent engineering teams using the frozen documents and this
AFD would produce functionally equivalent execution behavior in the
following dimensions:

> 1\. **User** **Journey** **Equivalence:** All five frozen workflows
> (WF-01 through WF-05) are defined with identical preconditions,
> triggers, primary success paths, alternative paths, failure paths,
> exit conditions, and expected outputs. The sixth and seventh
> maintainer workflows (WF-06, WF-07) are similarly unambiguous.
>
> 2\. **Module** **Orchestration** **Equivalence:** Section 6 defines
> the exact invocation order, caller/callee relationships, input/output
> contracts, and failure/recovery behavior for every module interaction.
> The dependency graph is a DAG with no ambiguity about which module
> calls which.
>
> 3\. **State** **Transition** **Equivalence:** Section 8 defines all
> system states (API job states and analysis stage states) with precise
> entry/exit conditions, valid/invalid transitions, and progress ranges.
> No team could implement a different state machine without violating
> the AFD.
>
> 4\. **Error** **Flow** **Equivalence:** Section 9 enumerates every
> major failure category with trigger, detection mechanism, response,
> logging behavior, recovery behavior, and user visibility. Exit codes
> are mapped unambiguously to error conditions.
>
> 5\. **Data** **Flow** **Equivalence:** Section 7 provides complete
> data lineage for both the analysis pipeline and benchmark pipeline,
> including source data, transformation stages, intermediate artifacts,
> temporary storage, final outputs, lifecycle, and retention policies.
>
> 6\. **Sequence** **Diagram** **Equivalence:** Section 10 provides
> textual sequence diagrams for every major workflow, covering CLI mode,
> API async mode, benchmark mode, and investigation mode. The message
> order and actors are fully specified.
>
> 7\. **Concurrency** **Equivalence:** Section 11 explicitly states that
> V1 is single-threaded by default, with parallel processing restricted
> to the benchmark runner under specific rules (processes, derived
> seeds, no shared state). No team could introduce unintended
> concurrency.
>
> 8\. **Performance** **Equivalence:** Section 12 defines expected
> runtime, performance targets, scaling behavior, bottlenecks, and
> failure thresholds for every workflow. Teams would implement the same
> performance guards.
>
> 9\. **Observability** **Equivalence:** Section 13 defines log levels,
> content, destinations, and formats; execution traces; audit records;
> and the failure investigation workflow. All teams would produce
> identical observability artifacts.
>
> 10.**Security** **Equivalence:** Section 14 defines input validation,
> permission checks, file handling, execution isolation, and data
> leakage prevention rules. All teams would implement the same security
> boundaries.
>
> 11.**Testability** **Equivalence:** Section 15 defines unit-test
> boundaries, integration-test boundaries, system-test boundaries,
> acceptance-test boundaries, and required mock components. All teams
> would test the same behaviors.
>
> 12.**Traceability** **Equivalence:** Section 16 maps every workflow to
> TRD modules, PRD requirements, TFS specifications, and BSD benchmarks,
> proving complete coverage of frozen requirements.
>
> 13.**Ambiguity** **Resolution:** Section 17 audits and resolves all
> identified workflow, state, error, data, and execution ambiguities. No
> residual ambiguity remains that would permit divergent
> implementations.

**18.4** **AFD** **Approval** **Verdict**

**Application** **Flow** **Document** **(AFD** **v1.0)** **Status:**
**Workflow** **Authority**

**Verdict:** **APPROVED** **for** **Backend** **Schema** **Design.**

This AFD provides sufficient behavioral detail for three independent
engineering teams to implement the MIIE v1.0 system such that:

> All user workflows produce identical outputs given identical inputs.
>
> All state machines transition through identical states under identical
> conditions.
>
> All error conditions are handled with identical responses, exit codes,
> and user messages.
>
> All data flows preserve identical lineage, retention, and deletion
> behavior.
>
> All module orchestration sequences invoke identical modules in
> identical order with identical inputs.

**Implementation** **may** **commence** **immediately.**

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

> *END* *OF* *APPLICATION* *FLOW* *DOCUMENT* *(AFD* *v1.0)*
