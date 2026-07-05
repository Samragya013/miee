# FERA Phase 8 — Testing Audit

**Audit ID:** FERA-P8-TEST  
**Date:** 2026-06-23  
**Auditor:** Independent Audit Authority  
**Scope:** Full pytest execution (collection + run), per-file pass/fail, collection errors, coverage assessment  

---

## 1. Test Execution Summary

**Command:** `python -m pytest tests/ -v --tb=short`  
**Result:** 78 failed, 273 passed, 9 collection errors  
**Total collected:** 351 tests  
**Pass rate (among collectable):** 77.8% (273/351)  
**Pass rate (including collection errors):** 77.8% (273/351)  

---

## 2. Collection Errors (9 tests, 3 files)

| File | Error | Cause |
|------|-------|-------|
| `tests/integration/test_reproducibility.py` | `ImportError: cannot import name 'MockIngestionEngine' from 'src.miie.processing.ingestion'` | `MockIngestionEngine` removed from `ingestion.py` (HEAD commit) |
| `tests/integration/test_workflows.py` | Same ImportError | Same cause |
| `tests/integration/test_profiling.py` | Same ImportError | Same cause |
| `tests/integration/test_segmentation_integration.py` | Same ImportError | Same cause |

**Root cause:** HEAD commit (`a12830c`) message: "removed MockIngestionEngine from ingestion.py, cleaned up mock references" — but test files still import it. 4 integration test modules are now broken.

---

## 3. Per-File Test Results

### FAILING (78 failures across 17 files)

| File | Failures | Root Cause |
|------|----------|------------|
| `tests/processing/test_validators.py` | 13 | Validation logic errors |
| `tests/processing/test_evidence.py` | 8 | Evidence package format/structure |
| `tests/processing/test_validation.py` | 7 | Validation service bugs |
| `tests/test_report_generator.py` | 6 | Report generation failures |
| `tests/integration/test_evidence_integration.py` | 5 | Evidence integration pipeline |
| `tests/integration/test_workflow.py` | 5 | Workflow orchestration |
| `tests/test_report_generation.py` | 4 | Report generation (alternate) |
| `tests/test_mock_explanation.py` | 4 | Mock explanation engine |
| `tests/processing/test_explanation_engine.py` | 4 | Explanation engine logic |
| `tests/processing/test_generator.py` | 4 | Generator output |
| `tests/benchmarks/reproducibility_test.py` | 4 | Benchmark reproducibility |
| `tests/processing/test_validation_service.py` | 4 | Validation service |
| `tests/integration/test_pipeline_skeleton.py` | 3 | Pipeline skeleton |
| `tests/integration/test_evidence_package.py` | 3 | Evidence package assembly |
| `tests/integration/test_ingestion_to_pipeline.py` | 3 | Ingestion→pipeline handoff |
| `tests/processing/test_scoring_engine.py` | 2 | Scoring engine (NameError bugs) |
| `tests/benchmarks/test_candidate_manifest.py` | 2 | Manifest validation (malformed JSON) |
| `tests/test_day10_dry_run_pipeline.py` | 1 | Day 10 dry-run (no CLI `analyze` command) |

### PASSING (273 tests across remaining files)

All other test files pass. Key passing modules:
- `tests/contracts/` — all contract/interface tests pass
- `tests/schemas/` — all schema validation tests pass
- `tests/processing/test_ingestion.py` — ingestion tests pass
- `tests/processing/test_segmentation.py` — segmentation tests pass
- `tests/orchestration/` — pipeline orchestration tests pass
- `tests/analysis/` — analysis tests pass

---

## 4. Coverage Assessment

No coverage report was generated (pytest-cov not configured). Based on manual assessment:

| Module | Test Coverage | Quality |
|--------|--------------|---------|
| `src/miie/contracts/` | HIGH | Tests pass, interfaces enforced |
| `src/miie/schemas/` | HIGH | Schema validation tests pass |
| `src/miie/processing/ingestion.py` | MEDIUM | Core tests pass, but MockIngestionEngine removed |
| `src/miie/processing/segmentation.py` | MEDIUM | Tests pass but single-window strategy |
| `src/miie/processing/scoring/engine.py` | LOW | 2 failures + NameError bugs |
| `src/miie/processing/evidence.py` | LOW | 8 failures + non-determinism |
| `src/miie/processing/validation/` | LOW | 13+7+4 failures |
| `src/miie/orchestration/pipeline.py` | MEDIUM | Integration tests pass |
| `src/miie/cli.py` | NONE | No tests exist for 14-line stub |
| `src/miie/detection/` | LOW | D-02 out-of-authority, no test coverage |
| `benchmarks/` | LOW | 2 failures, malformed manifest |

---

## 5. Test Quality Observations

- **No negative tests for scoring engine NameError paths** — the 2 scoring test failures are unrelated to the NameError bug; the bug is in magnitude extraction which no test exercises
- **No test for CLI `analyze` command** — because it doesn't exist
- **No test for byte-identical reproducibility** — evidence engine non-determinism not tested
- **Integration tests broken** — 4 modules can't even collect due to removed mock

---

## Summary

| Check | Status | Severity |
|-------|--------|----------|
| Test collection | **WARN** (9 errors) | HIGH |
| Test pass rate | **77.8%** | MEDIUM |
| Scoring engine tests | **FAIL** (2 failures) | CRITICAL |
| Evidence tests | **FAIL** (8 failures) | HIGH |
| Validation tests | **FAIL** (24 failures) | HIGH |
| Integration tests | **FAIL** (4 modules broken) | HIGH |
| CLI tests | **NONE** | HIGH |
| Coverage report | **NOT GENERATED** | MEDIUM |

**Overall Testing Audit: FAIL** — 78 test failures, 9 collection errors, no coverage report, critical modules untested.
