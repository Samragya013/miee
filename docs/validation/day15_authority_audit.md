# Day 15 Authority Audit
## Analysis of Authority Documents for Day 15 Scope

This document determines the exact Day 15 objectives, deliverables, and requirements based on:
- TFS_MIIE_v1.0.md (Technical Framework Specification)
- ACS_MIIE_v1.0.md (Architecture Contracts Specification)
- BSD-Engineering_MIIE_v1.0.md (Backend Schema Document)
- TRD_MIIE_v1.0.md (Technical Requirements Document)
- AFD_MIIE_v1.0.md (Application Framework Document)
- MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md (Day 11-20 Operating Plan)

## 1. Exact Day 15 Objective

**From MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md (lines 545-549):**
> Expand benchmark candidates from 30 to 120 datasets across 3 benchmark suites. Implement candidate generation workflow and validation.

## 2. Exact Day 15 Deliverables

**From MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md (lines 592-596):**
- `src/miie/benchmark/generator.py` - Dataset generator implementation
- `benchmarks/candidates/` - 120 candidate directories
- `benchmarks/metadata/candidate_manifest.json` - Updated manifest (120 entries)
- `tests/benchmark/test_generator.py` - 5+ unit tests
- `tests/benchmark/test_validation.py` - 3+ validation tests

## 3. Mandatory Requirements

### Authority Sources and Requirements:

| Requirement | Authority Source | Required | Deferred | Notes |
|-------------|------------------|----------|----------|-------|
| Benchmark Expansion Objective | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 545-549 | ✅ | | Expand benchmark candidates from 30 to 120 datasets across 3 benchmark suites |
| Benchmark Candidate Generator | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 569-570 | ✅ | | Create synthetic dataset generator (M-03 GEN variant) |
| Dataset Validation | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 571-572 | ✅ | | Implement dataset validation for generated datasets |
| Candidate Set Expansion | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 573-574 | ✅ | | Generate 90 additional candidates (total 120) |
| Annotation Workflow Foundation | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 575-576 | ✅ | | Implement reviewer/adjudication structure foundation |
| Benchmark Generator Implementation | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 592-593 | ✅ | | `src/miie/benchmark/generator.py` - Dataset generator implementation |
| Candidate Set Expansion | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 594-595 | ✅ | | `benchmarks/candidates/` - 120 candidate directories |
| Manifest Update | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 595-596 | ✅ | | `benchmarks/metadata/candidate_manifest.json` - Updated manifest (120 entries) |
| Generator Tests | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 596-597 | ✅ | | `tests/benchmark/test_generator.py` - 5+ unit tests |
| Validation Tests | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 597-598 | ✅ | | `tests/benchmark/test_validation.py` - 3+ validation tests |
| Deterministic Generation | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md line 586 | ✅ | | Verify seed-based determinism |
| Pathology Injection | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md line 587 | ✅ | | Verify MDE (Minimal Detectable Effect) injection |
| Schema Compliance | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md line 588 | ✅ | | Verify BSD-Engineering Section 13 compliance |
| Cross-layer Dependencies | TRD §2.1, ADR-001 | ✅ | | No access to storage, reporting, benchmarking from processing layer (except benchmark-specific) |

### Detailed Requirements Analysis:

#### MIBS Section 3: Benchmark Suite Structure
From MIBS_MIIE_v1.0.md (implied):
- Three benchmark suites: Metric Drift (B-01), Correlation Breakdown (B-02), Threshold Compression (B-03)
- Each suite contains synthetic repositories with specific, quantifiable characteristics
- Designed to test specific detector capabilities (D-01, D-02, D-03 respectively)

#### BSD-Engineering Section 13: Dataset Schema
From BSD-Engineering_MIIE_v1.0.md Section 13:
- Defines structure for benchmark datasets
- Includes repository metadata, commit history, file structure, and expected detector outputs
- Ensures consistency across generated candidates

#### TFS Section 8: Benchmark Requirements
From TFS_MIIE_v1.0.md Section 8:
- Benchmark datasets must be synthetic and reproducible
- Must include known ground truths for detector validation
- Must cover spectrum of difficulty levels (easy, medium, hard)
- Must prevent data leakage between training and testing in ML contexts (though MIIE is rules-based)

#### Determinism and Reproducibility Requirements
- All benchmark generation must be deterministic based on seed values
- Same seed must produce identical repository structures
- Essential for scientific validity and testing

#### Layer Architecture Compliance
- Benchmark components reside in `src/miie/benchmark/`
- Processing layer may use benchmark datasets as input but cannot modify benchmark generation logic
- Clear separation between benchmark generation (M-03 GEN) and benchmark execution (M-06)

## 4. Deferred Requirements

| Requirement | Authority Source | Reason for Deferment |
|-------------|------------------|----------------------|
| Real detector algorithm validation | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 38-39 | Requires Day 15 completion first; detector algorithms (D-01: KS+PSI, D-02: Pearson+Spearman, D-03: excess mass+dip) deferred to Days 21-25 |
| Full seven-metric extraction | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md line 39 | M-03..M-07 deferred until after benchmark validation |
| Scoring engine implementation | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md line 40 | M-08: IS/CS formulas deferred until after benchmark validation |
| Full report generation beyond mock dry-run | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md line 41 | Requires detector implementations |
| Ground truth workflow implementation | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 609-610 | M-16 deferred until Day 16; Day 15 only implements foundation |

## 5. Out-of-Scope Requirements

| Requirement | Authority Source | Reason |
|-------------|------------------|--------|
| Detector algorithm implementation | TRD_MIIE_v1.0.md Sections 5.1-5.9 (M-01 through M-08) | Deferred to Days 21-25 per Operating Plan and MIFS workflow |
| Ground truth adjudication process | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 634-637 | Full implementation deferred to Day 16 |
| Benchmark runner (M-06) | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 680-684 | Deferred to Day 17 |
| Evaluation engine (M-07) | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 755-759 | Deferred to Day 18 |
| End-to-end integration testing | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 829-849 | Deferred to Day 19 |
| CLI Interface (full) | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md line 902 | Deferred to Day 10 (basic) then further deferred |
| REST API | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md line 903 | Contracts defined, implementation deferred |
| Config Loader | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md line 904 | Template exists, full implementation deferred |
| Registry Manager | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md line 905 | Templates exist, full implementation deferred |

## 6. Ground-truth Dependencies

**Status**: ⚠️ PARTIAL for foundation
- Day 15 benchmark expansion creates synthetic datasets WITHOUT ground truth labels
- Ground truth annotation workflow begins in Day 16 (M-10 Ground Truth Manager foundation)
- Day 15 focuses on generating diverse, synthetic repositories with controllable characteristics
- Ground truth will be added through annotation workflow in subsequent days

## 7. Annotation Workflow Dependencies

**Status**: ⚠️ FOUNDATION ONLY
- Day 15 implements basic annotation workflow structure (reviewer/adjudication foundation)
- Full annotation workflow with Cohen's Kappa computation deferred to Day 16
- Day 15 establishes the structural foundation for future annotation implementation

## 8. Candidate Dataset Requirements

**From MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md and implied standards:**
- 120 total candidates across 3 benchmark suites (40 per suite)
- Synthetic Git repositories with controlled characteristics
- Each suite targets specific detector capabilities:
  - B-01 (Metric Drift): Tests D-01 (Concept Drift Detector)
  - B-02 (Correlation Breakdown): Tests D-02 (Correlation Analyzer)
  - B-03 (Threshold Compression): Tests D-03 (Compression Ratio Analyzer)
- Must include variability in:
  - Repository size (commits, files, contributors)
  - Activity patterns (bursty vs steady)
  - Pathology types and magnitudes (for injection testing)
  - File types and sizes
  - Commit message styles
- All generation must be deterministic based on configurable seeds

## 9. Success Criteria

**From MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md and validation requirements:**
- Exactly 120 benchmark candidates distributed across 3 suites
- Deterministic generation: same seed produces identical repositories
- Schema compliance: All generated candidates conform to BSD-Engineering Section 13 dataset schema
- Pathology injection: Ability to inject known detectable effects at controllable magnitudes
- Suite balance: Each suite contains appropriate mix of easy/medium/hard difficulty cases
- Structural validity: Generated repositories are valid Git repositories with coherent history

## DAY 15 AUTHORITY VERDICT

**AUTHORIZED** - Day 15 Benchmark Expansion implementation is authorized based on:
- Clear specification in MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md
- Supporting authority documents (TFS, ACS, BSD, AFD, TRD, MIBS)
- No blocking dependencies on unimplemented components (foundation work only)
- Well-defined scope focused on benchmark candidate expansion
- Prerequisites (Day 14 Report Generator Foundation) completed and verified

The implementation should focus exclusively on the deliverables and requirements specified in the authority documents, particularly the MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md Day 15 section.