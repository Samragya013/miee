# MIIE DAY 11-20 EXECUTION OPERATING PLAN

**Status:** PREPARED FOR REVIEW  
**Date:** 2026-06-14  
**Version:** 1.0.0  
**Classification:** Execution Plan - Day 11-20 Continuation

---

## EXECUTIVE SUMMARY

This document outlines the Day 11-20 execution plan for the MIIE v1.0 project. The plan is derived from actual repository state analysis as of Day 11, which indicates that Days 0-10 have been substantially completed with full validation.

### Current Repository State (Day 11 Assessment)

**Repository:** `miie`  
**Version:** 1.0.0  
**Status:** Day 10 Foundation Complete, Ready for Day 11 Extension

**Completed:**
- ✅ Day 0: Governance foundation (freeze_register.md, terminology_registry.md, authority_matrix.md)
- ✅ Day 1: Repository setup (Poetry project, CI/CD, testing framework)
- ✅ Day 2: Architecture scaffolding (module structure, layer separation, import rules)
- ✅ Day 3: Core schema foundation (RepositoryContext, MetricDataFrame, DetectorResult, EvidencePackage)
- ✅ Day 4: Contract layer (ACS Protocols, DTOs, validators, error model)
- ✅ Day 5: Pipeline skeleton (AnalysisPipeline, WorkflowDispatcher with mocks)
- ✅ Day 6: Repository ingestion (RepositoryIngestionEngine - M-01)
- ✅ Day 7: Metric extraction foundation (MetricExtractionEngine - M-02 with M-02 and M-06)
- ✅ Day 8: Detector framework (partial foundation, D-01..D-03 framework ready)
- ✅ Day 9: Evidence framework (EvidencePackage with provenance, traceability)

**Partially Completed:**
- ⚠️ Day 8: Detector implementation (framework exists, detector algorithms deferred to benchmark phase)
- ⚠️ Day 9: Evidence builder (schema ready, integration with detector output pending)
- ⚠️ Day 10: End-to-end dry run (mock artifacts generated, real detector integration pending)

**Deferred Until After Day 20:**
- Real detector algorithms (D-01: KS+PSI, D-02: Pearson+Spearman, D-03: excess mass+dip)
- Full seven-metric extraction (M-03..M-07)
- Scoring engine implementation (M-08: IS/CS formulas)
- Benchmark generation (120 datasets)
- Full report generation beyond mock dry-run

### Plan Overview

Day 11-20 focuses on completing the Day 10 dry-run capability and establishing the foundation for:
1. Window segmentation (M-03)
2. Scoring engine (M-08)
3. Evidence integration with detector outputs
4. Report generator templates
5. Benchmark candidate expansion (from 30 to 120 candidates)
6. Ground truth workflow

**Key Constraint:** All detector algorithms (D-01, D-02, D-03) are DEFERRED until benchmark readiness gates are passed per the MIFS (Measurement Integrity Foundation Sequence) workflow in IMP.

---

## DAY 11: WINDOW SEGMENTATION FOUNDATION

### Objective

Implement window segmentation foundation (M-03) for partitioning metric data into analysis windows. This enables time-based, commit-based, and custom window strategies for drift detection.

### Required Inputs

| Input | Source | Status |
|-------|--------|--------|
| MetricDataFrame | M-02 output | ✅ Available (Day 7) |
| RepositoryContext | M-01 output | ✅ Available (Day 6) |
| Segmentation protocol | TRD Section 9 | ✅ Documented |

### Authority Documents

| Document | Section | Requirement |
|----------|---------|-------------|
| TRD | Section 9 | Window generation strategies |
| BSD-Engineering | Section 7 | WindowDefinition schema |
| AFD | Section 5.2 | Pipeline execution order |
| IMP | Section 3 | M-03 ownership (Engineer B) |

### Tasks

| Task ID | Purpose | Implementation Steps | Input Objects | Output Objects | Files Modified/Created | Tests Required | Expected Deliverables | Definition Of Done |
|---------|---------|---------------------|---------------|----------------|------------------------|----------------|----------------------|-------------------|
| T-11.1 | Implement WindowDefinition schema | Create dataclass with start_date, end_date, id, commit_count fields | BSD Section 7 | WindowDefinition dataclass | `src/miie/schemas/models.py` | Schema validation tests (ST-07) | WindowDefinition class | Schema validates, no circular deps |
| T-11.2 | Implement time-based segmentation | Create time-window partitioner using ISO 8601 intervals | RepositoryContext, MetricDataFrame | List[WindowDefinition] | `src/miie/processing/segmentation.py` | Unit tests for window boundaries | Time segmenter | Windows non-overlapping, ordered |
| T-11.3 | Implement commit-based segmentation | Create commit-count window partitioner | RepositoryContext, commit history | List[WindowDefinition] | same | Unit tests for commit counts | Commit segmenter | Fixed window sizes per config |
| T-11.4 | Implement custom segmentation | Create boundary-based partitioner with user-defined ranges | User-provided boundaries | List[WindowDefinition] | same | Integration tests | Custom segmenter | Boundary validation passes |
| T-11.5 | Integrate segmentation into pipeline | Connect M-03 to M-02 → M-03 pipeline chain | AnalysisPipeline | Pipeline stage | `src/miie/orchestration/pipeline.py` | Integration test (M-02→M-03) | Segmentation stage | Schema-valid output, ordered windows |

### Contracts Used

| Contract ID | Module | Purpose |
|-------------|--------|---------|
| INT-03 | Segmentation Engine | WindowDefinition input/output |

### Schemas Used

| Schema ID | File | Description |
|-----------|------|-------------|
| WindowDefinition | BSD Section 7, models.py | Window metadata structure |

### Files Modified

- `src/miie/schemas/models.py` - Add WindowDefinition dataclass
- `src/miie/processing/segmentation.py` - Create new (placeholder until Day 11)
- `src/miie/orchestration/pipeline.py` - Add segmentation stage
- `tests/unit/test_segmentation.py` - Create new
- `tests/integration/test_segmentation_integration.py` - Create new

### Tests Required

| Test Type | Test File | Purpose |
|-----------|-----------|---------|
| Unit | `test_segmentation.py::test_time_window_basic` | Verify time-based window creation |
| Unit | `test_segmentation.py::test_commit_window_basic` | Verify commit-based window creation |
| Unit | `test_segmentation.py::test_custom_boundaries` | Verify user-defined boundary handling |
| Integration | `test_segmentation_integration.py` | Verify M-02→M-03 pipeline chain |

### Validation Rules

- Windows must be non-overlapping and ordered chronologically
- Window IDs must be stable across runs (deterministic)
- Empty metric data must return empty window list (not error)
- Invalid boundary conditions must raise SegmentationError

### Expected Deliverables

- `src/miie/processing/segmentation.py` - Segmentation engine implementation
- `src/miie/schemas/models.py` - WindowDefinition dataclass
- `tests/unit/test_segmentation.py` - 10+ unit tests
- `tests/integration/test_segmentation_integration.py` - 3+ integration tests
- `research/segmentation_strategies.md` - Strategy documentation

### Failure Conditions

- Segmentation creates overlapping windows
- Window IDs are non-deterministic
- Window list is empty when data exists
- Custom boundaries are not validated

### Recovery Actions

- Revert segmentation strategy implementation
- Review boundary calculation logic
- Verify window ordering and uniqueness

### Kiro Instructions

Generate WindowDefinition schema, time/commit/custom segmentation engines, integration with AnalysisPipeline. NO real detector algorithms. NO benchmark execution. Mock-only pipeline stages.

### Claude Code Instructions

Review segmentation logic against TRD Section 9. Validate WindowDefinition schema against BSD-Engineering Section 7. Ensure deterministic window IDs. Test non-overlapping constraint.

### Commands

```bash
poetry run pytest tests/unit/test_segmentation.py
poetry run pytest tests/integration/test_segmentation_integration.py
poetry run mypy src/miie/processing/segmentation.py
```

### Unit Tests

- test_time_window_basic
- test_commit_window_basic
- test_custom_boundaries_validation
- test_empty_data_handling
- test_window_ordering
- test_window_id_determinism
- test_boundary_overlap_detection
- test_commit_count_calculation

### Integration Tests

- test_m02_to_m03_pipeline
- test_repository_context_flow
- test_metric_dataframe_segmentation

### Validation Checklist

- [ ] WindowDefinition schema validates
- [ ] Windows non-overlapping verified
- [ ] Window IDs deterministic
- [ ] Boundary validation works
- [ ] Empty data returns empty list
- [ ] Pipeline integration passes

### Deliverables

- segmentation.py (implementation)
- test_segmentation.py (10+ tests)
- test_segmentation_integration.py (3+ tests)
- segmentation_strategies.md (documentation)

### Definition Of Done

All tests passing, schema validates, deterministic output, TRD Section 9 compliant, BSD Section 7 compliant.

### Estimated Hours

12 hours (3 days × 4 hours)

### Engineer Ownership

- Primary: Engineer B (M-03)
- Secondary: Engineer C (review)

###Claude Code Instructions

Review segmentation logic against TRD Section 9. Validate WindowDefinition schema against BSD-Engineering Section 7. Ensure deterministic window IDs. Test non-overlapping constraint.

### Unit Tests

- test_time_window_basic
- test_commit_window_basic
- test_custom_boundaries_validation
- test_empty_data_handling
- test_window_ordering
- test_window_id_determinism
- test_boundary_overlap_detection
- test_commit_count_calculation

### Integration Tests

- test_m02_to_m03_pipeline
- test_repository_context_flow
- test_metric_dataframe_segmentation

### Validation Checklist

- [ ] WindowDefinition schema validates
- [ ] Windows non-overlapping verified
- [ ] Window IDs deterministic
- [ ] Boundary validation works
- [ ] Empty data returns empty list
- [ ] Pipeline integration passes

### Deliverables

- segmentation.py (implementation)
- test_segmentation.py (10+ tests)
- test_segmentation_integration.py (3+ tests)
- segmentation_strategies.md (documentation)

### Definition Of Done

All tests passing, schema validates, deterministic output, TRD Section 9 compliant, BSD Section 7 compliant.

### Estimated Hours

12 hours (3 days × 4 hours)

### Engineer Ownership

- Primary: Engineer B (M-03)
- Secondary: Engineer C (review)
---

## DAY 12: SCORING ENGINE FOUNDATION

### Objective

Implement scoring engine foundation (M-08) with integrity score (IS) and confidence score (CS) framework. Define the multiplicative factor model for confidence scores as specified in TFS Section 7.

### Required Inputs

| Input | Source | Status |
|-------|--------|--------|
| DetectorResults | M-05 output | ⚠️ Framework exists (Day 8), algorithms deferred |
| MetricDataFrame | M-02 output | ✅ Available (Day 7) |
| WindowDefinition | M-03 output | ⚠️ Created in Day 11 |
| TFS formulas | TFS Section 6-7 | ✅ Documented |

### Authority Documents

| Document | Section | Requirement |
|----------|---------|-------------|
| TRD | Section 15 | Scoring Engine specification |
| TFS | Section 6 | Integrity Score formula |
| TFS | Section 7 | Confidence Score formula (5 multiplicative factors) |
| BSD-Engineering | Section 9 | ScorePackage schema |

### Tasks

| Task ID | Purpose | Implementation Steps | Input Objects | Output Objects | Files Modified/Created | Tests Required | Expected Deliverables |
|---------|---------|---------------------|---------------|----------------|------------------------|----------------|----------------------|
| T-12.1 | Implement ScorePackage schema | Create dataclass with integrity and confidence fields | BSD Section 9 | ScorePackage dataclass | `src/miie/schemas/models.py` | Schema validation tests |
| T-12.2 | Implement integrity score framework | Create weighted aggregation function | DetectorResults, weights | IntegrityScore | `src/miie/processing/scoring.py` | Unit tests for aggregation |
| T-12.3 | Implement confidence score framework | Create multiplicative factor model (sample size, variance, missing data, window balance, detector success) | ScorePackage | ConfidenceScore | same | Unit tests for factors |
| T-12.4 | Integrate scoring into pipeline | Connect M-08 to M-05 → M-08 pipeline chain | AnalysisPipeline | Scoring stage | `src/miie/orchestration/pipeline.py` | Integration test |
| T-12.5 | Create weight redistribution logic | Implement proportional weight adjustment for failed detectors | Config | Weight distribution | same | Edge case tests |

### Contracts Used

| Contract ID | Module | Purpose |
|-------------|--------|---------|
| INT-05 | Scoring Engine | ScorePackage input/output |

### Schemas Used

| Schema ID | File | Description |
|-----------|------|-------------|
| ScorePackage | BSD Section 9, models.py | Score output structure |

### Files Modified

- `src/miie/schemas/models.py` - Add ScorePackage dataclass
- `src/miie/processing/scoring.py` - Create new
- `src/miie/orchestration/pipeline.py` - Add scoring stage
- `tests/unit/test_scoring.py` - Create new
- `tests/integration/test_scoring_integration.py` - Create new

### Tests Required

| Test Type | Test File | Purpose |
|-----------|-----------|---------|
| Unit | `test_scoring.py::test_integrity_aggregation` | Verify weighted aggregation |
| Unit | `test_scoring.py::test_confidence_multiplicative` | Verify factor multiplication |
| Unit | `test_scoring.py::test_weight_redistribution` | Verify proportional adjustment |
| Integration | `test_scoring_integration.py` | Verify M-05→M-08 pipeline chain |

### Validation Rules

- Integrity scores must be in range [0.0, 1.0]
- Confidence scores must be in range [0.0, 1.0]
- All multiplicative factors must be in [0.0, 1.0]
- Weight redistribution must preserve total weight = 1.0
- Failed detectors must receive zero weight

### Expected Deliverables

- `src/miie/processing/scoring.py` - Scoring engine implementation
- `src/miie/schemas/models.py` - ScorePackage dataclass
- `tests/unit/test_scoring.py` - 10+ unit tests
- `tests/integration/test_scoring_integration.py` - 3+ integration tests

### Failure Conditions

- Scores outside valid ranges
- Weight redistribution produces non-normalized weights
- Confidence factors produce values outside [0,1]

### Recovery Actions

- Revert scoring implementation
- Review formula implementations
- Verify edge case handling

### Kiro Instructions

Generate ScorePackage schema, integrity/confidence score calculations, weight redistribution logic. NO real detector algorithms. Mock detector results for testing.

### Claude Code Instructions

Review scoring formulas against TFS Section 6-7. Validate ScorePackage schema against BSD-Engineering Section 9. Test deterministic output. Verify edge cases (all metrics unavailable, single metric).

### Commands

```bash
poetry run pytest tests/unit/test_scoring.py
poetry run pytest tests/integration/test_scoring_integration.py
poetry run mypy src/miie/processing/scoring.py
```

### Estimated Hours

16 hours (4 days × 4 hours)

### Engineer Ownership

- Primary: Engineer C (M-08)
- Secondary: Engineer B (review)

---

## DAY 13: EVIDENCE INTEGRATION

### Objective

Complete evidence framework integration by connecting detector outputs to evidence generation. Implement evidence builder that creates traceable evidence items linking detector results to metrics and windows.

### Required Inputs

| Input | Source | Status |
|-------|--------|--------|
| RepositoryContext | M-01 output | ✅ Available (Day 6) |
| MetricDataFrame | M-02 output | ✅ Available (Day 7) |
| DetectorResults | M-05 output | ⚠️ Framework exists (Day 8) |
| ScorePackage | M-08 output | ⚠️ Created in Day 12 |

### Authority Documents

| Document | Section | Requirement |
|----------|---------|-------------|
| TRD | Section 10 | Evidence aggregator specification |
| BSD-Engineering | Section 10 | EvidencePackage schema |
| TFS | Appendix A | Evidence traceability rules |

### Tasks

| Task ID | Purpose | Implementation Steps | Input Objects | Output Objects | Files Modified/Created | Tests Required |
|---------|---------|---------------------|---------------|----------------|------------------------|----------------|
| T-13.1 | Implement EvidenceBuilder | Create builder that traces detector results to metrics/windows | RepositoryContext, MetricDataFrame, DetectorResults | EvidenceItem | `src/miie/processing/evidence.py` | Unit tests |
| T-13.2 | Integrate evidence into pipeline | Connect M-09 (evidence) to M-05/M-08 pipeline chain | AnalysisPipeline | Evidence stage | `src/miie/orchestration/pipeline.py` | Integration test |
| T-13.3 | Implement EvidenceSerializer | Create deterministic serialization for evidence | EvidencePackage | JSON string | same | Serialization tests |

### Contracts Used

| Contract ID | Module | Purpose |
|-------------|--------|---------|
| INT-06 | Evidence Engine | EvidencePackage input/output |

### Schemas Used

| Schema ID | File | Description |
|-----------|------|-------------|
| EvidencePackage | BSD Section 10, models.py | Evidence structure |

### Files Modified

- `src/miie/processing/evidence.py` - Create new
- `src/miie/orchestration/pipeline.py` - Add evidence stage
- `tests/unit/test_evidence.py` - Create new
- `tests/integration/test_evidence_integration.py` - Create new

### Tests Required

| Test Type | Test File | Purpose |
|-----------|-----------|---------|
| Unit | `test_evidence.py::test_traceability` | Verify detector→metric→window links |
| Unit | `test_evidence.py::test_serialization` | Verify deterministic JSON |
| Integration | `test_evidence_integration.py` | Verify pipeline chain |

### Validation Rules

- Every evidence item must reference run_id, detector_id, metric_id
- Window reference required (or explicit "mock-window" placeholder)
- Evidence text must describe mock data only during Day 11-20

### Expected Deliverables

- `src/miie/processing/evidence.py` - Evidence engine implementation
- `tests/unit/test_evidence.py` - 8+ unit tests
- `tests/integration/test_evidence_integration.py` - 2+ integration tests

### Estimated Hours

12 hours (3 days × 4 hours)

### Engineer Ownership

- Primary: Engineer A (M-09)
- Secondary: Engineer B (review)

---

## DAY 14: REPORT GENERATOR FOUNDATION

### Objective

Implement report generator foundation with template system and export formats. Create Jinja2 templates for mock detector outputs (no real detector results).

### Required Inputs

| Input | Source | Status |
|-------|--------|--------|
| AnalysisResults | Pipeline output | ⚠️ Mock data (Day 5) |
| EvidencePackage | M-09 output | ⚠️ Created in Day 13 |

### Authority Documents

| Document | Section | Requirement |
|----------|---------|-------------|
| TRD | Section 18 | Report Generator specification |
| BSD-Engineering | Section 12 | AnalysisResult schema |
| AFD | Section 5.4 | Output formats |

### Tasks

| Task ID | Purpose | Implementation Steps | Input Objects | Output Objects | Files Modified/Created | Tests Required |
|---------|---------|---------------------|---------------|----------------|------------------------|----------------|
| T-14.1 | Implement ReportOutput schema | Create dataclass for export paths | BSD Section 12 | ReportOutput dataclass | `src/miie/schemas/models.py` | Schema validation |
| T-14.2 | Create Jinja2 templates | Create dry-run templates for D-01..D-03 | TFS Section 9 | Jinja2 files | `src/miie/reporting/templates/` | Template rendering tests |
| T-14.3 | Implement report generation | Create JSON/Markdown/CSV export engine | AnalysisResults | Export files | `src/miie/reporting/generator.py` | Integration tests |
| T-14.4 | Integrate report generation | Connect M-09 to pipeline | AnalysisPipeline | Report stage | `src/miie/orchestration/pipeline.py` | End-to-end test |

### Contracts Used

| Contract ID | Module | Purpose |
|-------------|--------|---------|
| INT-08 | Report Generator | ReportOutput input/output |

### Schemas Used

| Schema ID | File | Description |
|-----------|------|-------------|
| ReportOutput | BSD Section 12, models.py | Report output structure |

### Files Modified

- `src/miie/schemas/models.py` - Add ReportOutput dataclass
- `src/miie/reporting/generator.py` - Create new
- `src/miie/orchestration/pipeline.py` - Add report stage
- `src/miie/reporting/templates/` - Create directory with templates
- `tests/unit/test_report_generator.py` - Create new
- `tests/integration/test_report_generation.py` - Create new

### Templates Required

| Template | Purpose |
|----------|---------|
| dry_run_report.j2 | Mock dry-run output |
| drift_explanation.j2 | D-01 template (mock) |
| correlation_explanation.j2 | D-02 template (mock) |
| compression_explanation.j2 | D-03 template (mock) |

### Tests Required

| Test Type | Test File | Purpose |
|-----------|-----------|---------|
| Unit | `test_report_generator.py::test_json_export` | Verify JSON export |
| Unit | `test_report_generator.py::test_markdown_export` | Verify Markdown export |
| Integration | `test_report_generation.py` | Verify end-to-end |

### Expected Deliverables

- `src/miie/reporting/generator.py` - Report generator implementation
- `src/miie/reporting/templates/` - 4 Jinja2 templates
- `tests/unit/test_report_generator.py` - 6+ unit tests
- `tests/integration/test_report_generation.py` - 2+ integration tests

### Estimated Hours

16 hours (4 days × 4 hours)

### Engineer Ownership

- Primary: Engineer A (M-09)
- Secondary: Engineer C (review)

---

## DAY 15: BENCHMARK EXPANSION

### Objective

Expand benchmark candidates from 30 to 120 datasets across 3 benchmark suites. Implement candidate generation workflow and validation.

### Required Inputs

| Input | Source | Status |
|-------|--------|--------|
| Repository fixture | benchmarks/ | ✅ 30 candidates (Day 8) |

### Authority Documents

| Document | Section | Requirement |
|----------|---------|-------------|
| MIBS | Section 3 | Benchmark suite structure |
| BSD-Engineering | Section 13 | Dataset schema |
| TFS | Section 8 | Benchmark requirements |

### Tasks

| Task ID | Purpose | Implementation Steps | Input Objects | Output Objects | Files Modified/Created | Tests Required |
|---------|---------|---------------------|---------------|----------------|------------------------|----------------|
| T-15.1 | Create synthetic dataset generator | Create M-03 GEN variant for benchmark datasets | Fixed seed, config | Synthetic repository | `src/miie/benchmark/generator.py` | Generator tests |
| T-15.2 | Implement dataset validation | Create schema validation for generated datasets | Dataset | Validation result | same | Validation tests |
| T-15.3 | Expand candidate set | Generate 90 additional candidates (total 120) | Existing 30 | 90 new candidates | benchmarks/ | Expansion tests |
| T-15.4 | Implement annotation workflow | Create reviewer/adjudication structure | Candidates | Annotation queue | benchmarks/ | Workflow tests |

### Files Modified

- `src/miie/benchmark/generator.py` - Create new
- `benchmarks/candidates/` - Add 90 new directories
- `benchmarks/metadata/candidate_manifest.json` - Update manifest
- `tests/benchmark/test_generator.py` - Create new
- `tests/benchmark/test_validation.py` - Create new

### Tests Required

| Test Type | Test File | Purpose |
|-----------|-----------|---------|
| Unit | `test_generator.py::test_deterministic_generation` | Verify seed-based determinism |
| Unit | `test_generator.py::test_pathology_injection` | Verify MDE injection |
| Unit | `test_validation.py::test_schema_compliance` | Verify BSD compliance |

### Expected Deliverables

- `src/miie/benchmark/generator.py` - Dataset generator implementation
- `benchmarks/candidates/` - 120 candidate directories
- `benchmarks/metadata/candidate_manifest.json` - Updated manifest (120 entries)
- `tests/benchmark/test_generator.py` - 5+ unit tests
- `tests/benchmark/test_validation.py` - 3+ validation tests

### Estimated Hours

20 hours (5 days × 4 hours)

### Engineer Ownership

- Primary: Engineer B (M-03 GEN, M-04)
- Secondary: Engineer C (review)

---

## DAY 16: GROUND TRUTH WORKFLOW

### Objective

Implement ground truth annotation workflow with Cohen's Kappa computation and adjudication process.

### Required Inputs

| Input | Source | Status |
|-------|--------|--------|
| Benchmark candidates | M-03 GEN | ⚠️ Created in Day 15 (120 candidates) |

### Authority Documents

| Document | Section | Requirement |
|----------|---------|-------------|
| TRD | Section 11 | Ground Truth Manager specification |
| BSD-Engineering | Section 14 | GroundTruth schema |
| MIBS | Section 4 | Annotation protocol |

### Tasks

| Task ID | Purpose | Implementation Steps | Input Objects | Output Objects | Files Modified/Created | Tests Required |
|---------|---------|---------------------|---------------|----------------|------------------------|----------------|
| T-16.1 | Implement GroundTruth schema | Create dataclass for labels | BSD Section 14 | GroundTruth dataclass | `src/miie/schemas/models.py` | Schema validation |
| T-16.2 | Implement annotation workflow | Create reviewer interface with conflict resolution | Candidates | Annotation results | `src/miie/benchmark/ground_truth.py` | Workflow tests |
| T-16.3 | Implement Cohen's Kappa | Create inter-rater agreement computation | Annotations | Kappa value | same | Agreement tests |
| T-16.4 | Implement adjudication | Create conflict resolution process | Disagreements | Final labels | same | Adjudication tests |

### Contracts Used

| Contract ID | Module | Purpose |
|-------------|--------|---------|
| INT-06 | Evidence Engine | GroundTruth input/output |

### Schemas Used

| Schema ID | File | Description |
|-----------|------|-------------|
| GroundTruth | BSD Section 14, models.py | Label structure |

### Files Modified

- `src/miie/schemas/models.py` - Add GroundTruth dataclass
- `src/miie/benchmark/ground_truth.py` - Create new
- `tests/benchmark/test_ground_truth.py` - Create new

### Tests Required

| Test Type | Test File | Purpose |
|-----------|-----------|---------|
| Unit | `test_ground_truth.py::test_cohens_kappa` | Verify agreement computation |
| Unit | `test_ground_truth.py::test_adjudication` | Verify conflict resolution |

### Expected Deliverables

- `src/miie/benchmark/ground_truth.py` - Ground truth manager implementation
- `tests/benchmark/test_ground_truth.py` - 4+ unit tests
- `benchmarks/annotations/` - Annotation workflow structure

### Estimated Hours

16 hours (4 days × 4 hours)

### Engineer Ownership

- Primary: Engineer B (M-04)
- Secondary: Engineer C (review)

---

## DAY 17: BENCHMARK RUNNER IMPLEMENTATION

### Objective

Implement benchmark runner (M-06) for executing detector evaluations across synthetic datasets with leakage prevention.

### Required Inputs

| Input | Source | Status |
|-------|--------|--------|
| Benchmark datasets | M-03 GEN | ⚠️ Created in Day 15 (120 candidates) |
| Detector framework | M-05 | ⚠️ Framework exists (Day 8) |

### Authority Documents

| Document | Section | Requirement |
|----------|---------|-------------|
| TRD | Section 16 | Benchmark Runner specification |
| BSD-Engineering | Section 13 | BenchmarkRun schema |
| TFS | Section 8 | Benchmark requirements |

### Tasks

| Task ID | Purpose | Implementation Steps | Input Objects | Output Objects | Files Modified/Created | Tests Required |
|---------|---------|---------------------|---------------|----------------|------------------------|----------------|
| T-17.1 | Implement BenchmarkRun schema | Create dataclass for execution results | BSD Section 13 | BenchmarkRun dataclass | `src/miie/schemas/models.py` | Schema validation |
| T-17.2 | Implement suite loader | Create benchmark suite loader | Suite ID | Suite data | `src/miie/benchmark/runner.py` | Loader tests |
| T-17.3 | Implement detector isolation | Create test isolation for detector evaluation | Detector, suite | Isolated run | same | Isolation tests |
| T-17.4 | Implement temporal isolation | Create time-based test separation | Run metadata | Temporal separation | same | Temporal tests |
| T-17.5 | Implement leakage prevention | Create cross-dataset leakage detection | Predictions | Leakage report | same | Leakage tests |

### Contracts Used

| Contract ID | Module | Purpose |
|-------------|--------|---------|
| INT-09 | Benchmark Engine | BenchmarkRun input/output |

### Schemas Used

| Schema ID | File | Description |
|-----------|------|-------------|
| BenchmarkRun | BSD Section 13, models.py | Benchmark output structure |

### Files Modified

- `src/miie/schemas/models.py` - Add BenchmarkRun dataclass
- `src/miie/benchmark/runner.py` - Create new
- `tests/benchmark/test_runner.py` - Create new

### Tests Required

| Test Type | Test File | Purpose |
|-----------|-----------|---------|
| Unit | `test_runner.py::test_suite_loading` | Verify suite loading |
| Unit | `test_runner.py::test_detector_isolation` | Verify isolation |
| Unit | `test_runner.py::test_temporal_isolation` | Verify time separation |
| Unit | `test_runner.py::test_leakage_detection` | Verify leakage check |

### Expected Deliverables

- `src/miie/benchmark/runner.py` - Benchmark runner implementation
- `tests/benchmark/test_runner.py` - 6+ unit tests
- `benchmarks/runners/` - Runner configuration

### Estimated Hours

24 hours (6 days × 4 hours)

### Engineer Ownership

- Primary: Engineer C (M-06)
- Secondary: Engineer B (review)

---

## DAY 18: EVALUATION ENGINE IMPLEMENTATION

### Objective

Implement evaluation engine (M-07) for computing classification metrics and baseline comparisons.

### Required Inputs

| Input | Source | Status |
|-------|--------|--------|
| BenchmarkRun | M-06 output | ⚠️ Created in Day 17 |

### Authority Documents

| Document | Section | Requirement |
|----------|---------|-------------|
| TRD | Section 16 | Evaluation Engine specification |
| TFS | Section 8 | Evaluation metrics |
| IMP | Section 1.6 | Performance targets |

### Tasks

| Task ID | Purpose | Implementation Steps | Input Objects | Output Objects | Files Modified/Created | Tests Required |
|---------|---------|---------------------|---------------|----------------|------------------------|----------------|
| T-18.1 | Implement EvaluationResult schema | Create dataclass for evaluation metrics | BSD Section 12 | EvaluationResult dataclass | `src/miie/schemas/models.py` | Schema validation |
| T-18.2 | Implement confusion matrix | Create binary classification confusion matrix | Predictions, ground truth | Confusion matrix | `src/miie/benchmark/evaluation.py` | Matrix tests |
| T-18.3 | Implement evaluation metrics | Create 8 metrics (accuracy, precision, recall, F1, AUC-ROC, AUC-PR, FPR, FNR) | Confusion matrix | Evaluation metrics | same | Metric tests |
| T-18.4 | Implement baseline systems | Create 4 baseline implementations (random, majority, statistical, rule-based) | Baseline config | Baseline predictions | same | Baseline tests |
| T-18.5 | Integrate evaluation into benchmark | Connect M-07 to benchmark pipeline | BenchmarkRun | EvaluationResult | same | Integration tests |

### Contracts Used

| Contract ID | Module | Purpose |
|-------------|--------|---------|
| INT-10 | Evaluation Engine | EvaluationResult input/output |

### Schemas Used

| Schema ID | File | Description |
|-----------|------|-------------|
| EvaluationResult | BSD Section 12, models.py | Evaluation output structure |

### Files Modified

- `src/miie/schemas/models.py` - Add EvaluationResult dataclass
- `src/miie/benchmark/evaluation.py` - Create new
- `tests/benchmark/test_evaluation.py` - Create new

### Tests Required

| Test Type | Test File | Purpose |
|-----------|-----------|---------|
| Unit | `test_evaluation.py::test_confusion_matrix` | Verify matrix computation |
| Unit | `test_evaluation.py::test_metrics_calculation` | Verify 8 metrics |
| Unit | `test_evaluation.py::test_baseline_comparison` | Verify baseline implementations |
| Integration | `test_evaluation_integration.py` | Verify end-to-end |

### Expected Deliverables

- `src/miie/benchmark/evaluation.py` - Evaluation engine implementation
- `tests/benchmark/test_evaluation.py` - 8+ unit tests
- `tests/benchmark/test_evaluation_integration.py` - 2+ integration tests

### Estimated Hours

24 hours (6 days × 4 hours)

### Engineer Ownership

- Primary: Engineer C (M-07)
- Secondary: Engineer B (review)

---

## DAY 19: INTEGRATION AND END-TO-END TESTING

### Objective

Perform end-to-end integration testing of the complete pipeline with mock detector results and validate reproducibility.

### Required Inputs

| Input | Source | Status |
|-------|--------|--------|
| All modules | Days 11-18 | ⚠️ Created in previous days |

### Tasks

| Task ID | Purpose | Implementation Steps | Input Objects | Output Objects | Files Modified/Created | Tests Required |
|---------|---------|---------------------|---------------|----------------|------------------------|----------------|
| T-19.1 | Pipeline integration | Wire all modules into complete pipeline | AnalysisPipeline | Integrated pipeline | `src/miie/orchestration/pipeline.py` | Integration tests |
| T-19.2 | End-to-end workflow tests | Create WT-01..WT-05 workflow tests | Pipeline | Workflow results | `tests/workflow/test_workflows.py` | Workflow tests |
| T-19.3 | Reproducibility verification | Run identical analyses and verify byte-identical outputs | Fixed seed | Output comparison | `tests/workflow/test_reproducibility.py` | Reproducibility tests |
| T-19.4 | Performance profiling | Profile end-to-end execution time | Pipeline | Timing data | `tests/performance/test_profiling.py` | Profiling tests |

### Tests Required

| Test Type | Test File | Purpose |
|-----------|-----------|---------|
| Integration | `test_workflows.py::test_wf01_analyze_repository` | Verify WF-01 execution |
| Integration | `test_workflows.py::test_wf02_investigate_failure` | Verify WF-02 execution |
| Reproducibility | `test_reproducibility.py::test_byte_identical_outputs` | Verify deterministic execution |

### Expected Deliverables

- `tests/workflow/test_workflows.py` - 5+ workflow tests
- `tests/workflow/test_reproducibility.py` - 2+ reproducibility tests
- `tests/performance/test_profiling.py` - 1+ profiling tests

### Estimated Hours

20 hours (5 days × 4 hours)

### Engineer Ownership

- All engineers (integration effort)

---

## DAY 20: DAY 20 MILESTONE REVIEW

### Objective

Complete Day 20 milestone review with repository state assessment, completion status, and next-phase planning.

### Repository State Assessment

#### Completed Modules

| Module ID | Module Name | Status | Evidence |
|-----------|-------------|--------|----------|
| M-01 | Repository Ingestion Engine | ✅ Complete | Day 6 signoff, 100% tests passing |
| M-02 | Metric Extraction Engine | ✅ Complete | Day 7 signoff, M-02/M-06 extraction |
| M-03 | Window Segmentation Engine | ✅ Complete | Day 11 implementation |
| M-05 | Detector Engine Framework | ✅ Complete | Day 8 framework, algorithms deferred |
| M-06 | Benchmark Runner | ✅ Complete | Day 17 implementation |
| M-07 | Evaluation Engine | ✅ Complete | Day 18 implementation |
| M-08 | Scoring Engine | ✅ Complete | Day 12 implementation |
| M-09 | Report Generator | ✅ Complete | Day 14 implementation |
| M-17 | Workflow Engine | ✅ Complete | Day 5 implementation, Day 19 integration |

#### Remaining Modules

| Module ID | Module Name | Status | Notes |
|-----------|-------------|--------|-------|
| D-01, D-02, D-03 | Detectors | ⚠️ Deferred | Algorithms require benchmark validation (Days 21-25) |
| M-04 | Ground Truth Manager | ⚠️ Partial | Annotation workflow complete, final ground truth deferred |
| M-10 | CLI Interface | ⚠️ Basic | Version command only, full CLI deferred |
| M-11 | REST API | ⚠️ Placeholder | Contracts defined, implementation deferred |
| M-12 | Config Loader | ⚠️ Basic | Template exists, full implementation deferred |
| M-13 | Registry Manager | ⚠️ Basic | Templates exist, full implementation deferred |
| M-14 | Job Manager | ⚠️ Placeholder | State machine defined, implementation deferred |
| M-15 | Pipeline Controller | ⚠️ Mock | Skeleton exists, Day 19 integration |
| M-16 | State Manager | ⚠️ Placeholder | State machine defined, implementation deferred |

#### Blocked Modules

| Module ID | Module Name | Reason |
|-----------|-------------|--------|
| D-01, D-02, D-03 | Detectors | Detector algorithms require benchmark readiness gates (post-benchmark validation) |
| Full CLI (M-10) | Command-line interface | Requires detector implementations |
| Full API (M-11) | REST API | Requires detector implementations |
| Full Config (M-12) | Configuration loader | Requires detector implementations |

### Technical Debt

| Debt Item | Impact | Mitigation Plan |
|-----------|--------|-----------------|
| Mock detectors | Day 11-20 functionality limited | Address post-benchmark validation (Days 21-25) |
| Partial registry managers | Limited runtime flexibility | Deferred until post-benchmark |
| Basic state management | Limited job persistence | Deferred until post-benchmark |

### Known Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Detector algorithm validation pending | High | Benchmark validation required before detector deployment (Days 21-25) |
| Git-derived metrics may have cross-platform variance | Medium | Documented in Day 7 threats_to_validity.md |
| Synthetic dataset representativeness | Medium | Benchmark suites must be validated against real repositories (Days 21-25) |

### Validation Status

| Validation Type | Status | Notes |
|-----------------|--------|-------|
| Schema validation | ✅ Complete | All schemas validate, BSD-compliant |
| Contract tests | ⚠️ Partial | M-01, M-02, M-03, M-05, M-06, M-07, M-08, M-09 contracts complete |
| Workflow tests | ⚠️ Mock | End-to-end tests pass with mock detectors (Day 19) |
| Reproducibility tests | ✅ Complete | Day 19 reproducibility verification |
| Benchmark tests | ⚠️ Framework | Benchmark runner and evaluation engine ready (Days 17-18) |

### Benchmark Readiness

| Benchmark Suite | Status | Candidates | Notes |
|-----------------|--------|------------|-------|
| Metric drift (B-01) | ⚠️ Framework | 30 → 120 | Full suite requires detector validation |
| Correlation breakdown (B-02) | ⚠️ Framework | 30 → 120 | Full suite requires detector validation |
| Threshold compression (B-03) | ⚠️ Framework | 30 → 120 | Full suite requires detector validation |

### Publication Readiness

| Artifact | Status | Notes |
|----------|--------|-------|
| Artifact package | ⚠️ Partial | Day 10 dry-run artifacts complete, full package requires detector validation |
| Reproducibility evidence | ✅ Complete | Day 19 reproducibility verification complete |
| Evidence traceability | ✅ Complete | Evidence packages include full provenance |

### Open Source Readiness

| Requirement | Status | Notes |
|-------------|--------|-------|
| Code quality | ✅ Complete | CI/CD, tests, linting, type checking |
| Documentation | ⚠️ Partial | Day 0-10 docs complete, Day 11-20 docs in progress |
| License | ✅ Complete | MIT license in repository |
| Contribution guidelines | ⚠️ Basic | Template exists, needs expansion |

### Next Recommended Milestone

**Milestone: Detector Validation (Days 21-25)**

Objective: Implement and validate D-01, D-02, D-03 detectors against benchmark suites.

Prerequisites:
- ✅ All Day 11-20 modules complete
- ✅ Benchmark suites expanded to 120 candidates
- ✅ Ground truth annotation workflow complete
- ✅ Benchmark runner and evaluation engine operational

Success Criteria:
- D-01 precision ≥ 0.80, recall ≥ 0.75 on B-01
- D-02 precision ≥ 0.75, recall ≥ 0.70 on B-02
- D-03 precision ≥ 0.85, recall ≥ 0.80 on B-03
- Cohen's Kappa ≥ 0.80 on all suites

### Day 21 Entry Conditions

Before proceeding to Day 21, verify:

1. **All Day 11-20 tests passing**: `poetry run pytest` returns 100% pass rate
2. **All schemas validate**: `poetry run pytest tests/schema/` returns 100% pass rate
3. **Reproducibility verified**: Day 19 reproducibility test passes
4. **Benchmark candidates expanded**: 120 candidates in benchmarks/candidates/
5. **Ground truth annotation workflow operational**: Annotation tooling ready
6. **Pipeline integration complete**: Day 19 end-to-end tests pass

### Version 1 Completion Estimate

**Current Estimate**: 10-12 weeks total (6 weeks completed in Days 0-20)

Remaining work:
- Days 21-25: Detector implementation and validation (5 weeks)
- Days 26-28: Documentation, testing, hardening (3 weeks)
- Days 29-30: Release preparation, PyPI publishing (2 weeks)

**Projected Completion**: Week 30 (end of Sprint 15)

### MES Transition Readiness

| Transition Item | Status | Notes |
|-----------------|--------|-------|
| v1.1.0 features | ❌ Not ready | Detector implementations pending |
| V2 capabilities | ❌ Not ready | v1 must be complete first |
| Evolution strategy | ✅ Documented | MES document defines v1.1+ features |

---

## END OF DAY 11-20 EXECUTION PLAN

**Prepared by**: Kiro Orchestrator  
**Date**: 2026-06-14  
**Repository**: Day 7 Signoff Repository (miie v1.0)  
**Status**: Day 11-20 execution plan prepared for review and authorization

*This plan is derived from actual repository state and follows the frozen MIIE v1.0 specification. All deferrals are justified by authority documents (TFS, MES, IMP).*