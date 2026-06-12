# MIIE v1.0 Terminology Registry

**Status:** FROZEN  
**Date:** 2026-06-08  
**Version:** 1.0.0  
**Classification:** Governance Sprint Artifact  

---

## Metric

**Definition:** A quantifiable measure extracted from a software repository (e.g., code coverage percentage, commit frequency, cyclomatic complexity). Metrics are the fundamental data points that MIIE evaluates for integrity.

**Source Document:** PRD §2.1, TFS §2.1, TRD §8

**Allowed Usage:**
- M-01 through M-07 only in V1
- All metrics must be extracted from Git repositories or associated artifacts
- Metrics are evaluated for integrity, not for productivity or quality assessment

**Forbidden Usage:**
- Additional metrics beyond M-01..M-07
- Metrics used for developer ranking or productivity tracking
- Metrics used for real-time decision making
- Metrics with unknown or undocumented extraction methods

---

## Detector

**Definition:** A statistical algorithm that identifies when a metric has lost validity due to distributional drift, correlation breakdown, or threshold compression. Detectors produce flags indicating integrity failures.

**Source Document:** TFS §4, AFD §5.2, TRD §10

**Allowed Usage:**
- D-01, D-02, D-03 only in V1
- All three detectors run by default for every analysis
- Detectors may be explicitly disabled via configuration

**Forbidden Usage:**
- Additional detectors beyond D-01..D-03
- Machine learning models trained on benchmark data
- Dynamic detector selection based on data characteristics
- Detectors without documented statistical basis

---

## Integrity Score

**Definition:** A composite metric (range [0.0, 1.0]) that quantifies the overall construct validity of a metric or set of metrics by aggregating detector outputs. An Integrity Score of 1.0 indicates no detectors fired; 0.0 indicates all detectors fired at maximum severity.

**Source Document:** TFS §6, TRD §15.6, BSD §9

**Allowed Usage:**
- Per-metric and repository-level integrity scores
- Weighted aggregation of detector severities
- Transparency through evidence packages

**Forbidden Usage:**
- Non-deterministic computation (must be bitwise-identical across runs)
- Machine learning models in score computation
- Intentional distortion to make scores appear more favorable
- Score aggregation without documented weight redistribution

---

## Confidence Score

**Definition:** A composite metric (range [0.0, 1.0]) that measures the reliability of the Integrity Score assessment, not the quality of the repository. It answers: "How much should we trust the Integrity Score given the data we had?"

**Source Document:** TFS §7, TRD §15.6, BSD §9

**Allowed Usage:**
- Five multiplicative factors: sample size, variance, missing data, window balance, detector success
- Computed only after Integrity Score calculation
- Used to qualify Integrity Score interpretation

**Forbidden Usage:**
- Confidence Score as a substitute for Integrity Score
- Confidence Score used to make decisions without Integrity Score context
- Non-deterministic computation

---

## Evidence

**Definition:** Raw statistical outputs from detector executions, including test statistics, p-values, effect sizes, and window metadata. Evidence is the foundational data that supports all integrity assessments.

**Source Document:** TRD §10.5, BSD §10, TFS Appendix A

**Allowed Usage:**
- Full provenance for every detected failure
- Independent verification of integrity conclusions
- Statistical audit trail

**Forbidden Usage:**
- Evidence selectively withheld from public output
- Evidence modified after detection
- Evidence without timestamp, seed, or configuration provenance

---

## Evidence Package

**Definition:** A structured collection of all intermediate artifacts from analysis, including provenance metadata, window definitions, metric data, detector outputs, scores, and warnings. The evidence package enables reproducibility and independent verification.

**Source Document:** BSD §10, TRD §15.6, TFS Appendix A

**Allowed Usage:**
- Full analysis reproducibility given inputs and seed
- Independent verification of all conclusions
- Export to JSON and Markdown formats

**Forbidden Usage:**
- Omission of detector outputs or statistical details
- Evidence package without config_hash and seed
- Evidence package that cannot be validated against JSON schemas

---

## Benchmark

**Definition:** A standardized dataset with known integrity status (ground truth) used to evaluate detector performance. Benchmarks enable objective assessment of detector precision and recall.

**Source Document:** TFS §8, AFD §4.4, BSD §13

**Allowed Usage:**
- Three frozen suites: metric-drift-v1.0.0, correlation-breakdown-v1.0.0, threshold-compression-v1.0.0
- Deterministic execution with fixed seed
- Benchmark evaluation as the sole method for detector validation

**Forbidden Usage:**
- Non-standardized benchmark datasets
- Benchmark data used for detector tuning without proper isolation
- Benchmarks modified after publication

---

## Measurement Distortion Event

**Definition:** A controlled corruption injected into synthetic benchmark datasets to simulate real-world integrity failures. MDEs include distributional drift (MDE-01), correlation breakdown (MDE-02), and threshold compression (MDE-03).

**Source Document:** BSD §9.4, TRD §10, TFS §10

**Allowed Usage:**
- Synthetic dataset generation for benchmark construction
- Detector calibration and threshold tuning
- Performance validation and regression testing

**Forbidden Usage:**
- MDEs used as ground truth for real repositories
- MDE parameters modified after freeze
- MDE injection without deterministic seed control

---

## Repository Context

**Definition:** A structured object containing metadata about an analyzed repository, including identification, commit statistics, contributor counts, and temporal bounds.

**Source Document:** TRD §7.8, BSD §5, ACS §5

**Allowed Usage:**
- Input to metric extraction engine
- Provenance in all output artifacts
- Validation of repository eligibility (≥10 commits, ≥1 contributor)

**Forbidden Usage:**
- Repository context without SHA-256 repo_id
- Repository context with missing metadata
- Repository context used for purposes other than analysis orchestration

---

## Metric Data Frame

**Definition:** A structured data container holding metric values across commits and windows. The MetricDataFrame is the primary data structure moving through the processing pipeline.

**Source Document:** TRD §8, BSD §6, ACS §6

**Allowed Usage:**
- Input to window segmentation and detector engines
- Serialization in JSON, CSV, and evidence packages
- Missing metric values represented as null

**Forbidden Usage:**
- Metric DataFrame with non-numeric values (except null)
- Metric DataFrame without proper window_id assignments
- Metric DataFrame without timestamp precision

---

## Detector Result

**Definition:** The structured output from a detector execution, containing detection flags, statistical test results, severity scores, and contextual metadata.

**Source Document:** BSD §8, ACS §8, TRD §10

**Allowed Usage:**
- Input to integrity score computation
- Evidence for explanations and reports
- Benchmark prediction generation

**Forbidden Usage:**
- Detector results without statistical test metadata
- Detector results with unnormalized severity values
- Detector results that omit skipped metrics

---

## Analysis Result

**Definition:** The final structured output from a repository analysis, combining integrity scores, confidence scores, evidence, and explanations into a single consumable artifact.

**Source Document:** BSD §12, TRD §15.6, ACS §12

**Allowed Usage:**
- Primary output format for CLI and API
- Input to report generation
- Source for CSV and Markdown exports

**Forbidden Usage:**
- Analysis result without config_hash and timestamp
- Analysis result without full provenance
- Analysis result with non-deterministic content

---

## Workflow

**Definition:** A predefined sequence of module invocations that accomplishes a specific user goal (e.g., analyze repository, run benchmark). Workflows are orchestrated by the Workflow Engine (M-17).

**Source Document:** AFD §4, TRD §14, AFD §4

**Allowed Usage:**
- Five frozen workflows: WF-01 through WF-05
- Direct function call orchestration (not RPC)
- Workflow-specific validation before execution

**Forbidden Usage:**
- Additional workflows beyond WF-01..WF-05
- workflows with non-deterministic execution order
- Workflows that bypass orchestration layer

---

## Validation

**Definition:** The process of verifying that inputs conform to specified schemas, contracts, and business rules before processing begins.

**Source Document:** ACS §4, BSD §4, AFD §5.2

**Allowed Usage:**
- Strict schema validation (unknown fields rejected)
- Input validation at all module boundaries
- Fail-fast behavior for invalid inputs

**Forbidden Usage:**
- Silent coercion of invalid types
- Accepting unknown fields without rejection
- Processing with missing required fields

---

## Frozen

**Definition:** A status indicating that a specification, algorithm, or capability is locked for the current version and may not be modified without a version bump. Frozen items are immutable in v1.0.x.

**Source Document:** TFS §1, TRD §1.2, BSD §1.5

**Allowed Usage:**
- All v1.0 specifications (TRD, ACS, BSD, TFS, AFD, IMP, PRD)
- Metrics M-01..M-07
- Detectors D-01..D-03
- Integrity Score and Confidence Score formulas

**Forbidden Usage:**
- Modification of frozen items in v1.0.x releases
- Addition of new metrics or detectors without v1.1.0
- Changes to formulas without version bump

---

*This terminology registry is authoritative. All documentation and code must use these definitions consistently.*