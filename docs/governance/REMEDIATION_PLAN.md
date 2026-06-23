# MIIE Remediation Plan — Target: 95%+ on Next FERA Audit

**Plan ID:** REMEDIATE-MIIE-001  
**Date:** 2026-06-23  
**Current Score:** 40.5% raw / ~25% risk-adjusted  
**Target Score:** ≥95% raw  
**Methodology:** Evidence-based (code + tests + runtime), phased by blast radius  

---

## Root Cause Analysis

78 test failures + 9 collection errors trace to **7 root causes**. Fixing these root causes resolves ~90% of all failures:

| # | Root Cause | Failures | Fix Type | Effort |
|---|---|---|---|---|
| RC-1 | `WindowDefinition` constructor changed (tests use `id=`, need `window_id` + `commits` + `strategy`) | ~35 | Test fix (bulk) | 1 hr |
| RC-2 | `EvidencePackage` tests expect old flat attributes (`evidence_id`, `detector_results_ids`, etc.) | ~14 | Test rewrite | 2 hr |
| RC-3 | `ScorePackage` constructor needs positional args (`IntegrityScore`, `ConfidenceScore`, `timestamp`, `config_hash`) | ~5 | Test fix | 30 min |
| RC-4 | `json_dumps()` doesn't accept `indent` kwarg (production bug) | ~14 | Production fix | 15 min |
| RC-5 | `ReportOutput` attribute mismatch (`file_paths` vs `report_paths`) | ~10 | Test fix | 1 hr |
| RC-6 | `MockIngestionEngine` not exported from `ingestion.py` | 4 modules | Import fix | 15 min |
| RC-7 | Malformed `candidate_manifest.json` (24 lines missing closing `"`) | 9 | Data fix | 15 min |

**Fixing RC-1 through RC-7 resolves ~91 failures (all but ~2-3 edge cases).**

---

## Phase 1: Quick Wins (Blast Radius Fixes) — Day 1

**Goal:** Fix the 7 root causes. Expected result: test pass rate jumps from 77.8% → ~98%.

### 1.1 Fix `json_dumps()` to accept `indent` parameter
**File:** `src/miie/schemas/serialization.py:16`  
**Change:** Add `indent: Optional[int] = None` parameter, forward to `json.dumps()`  
**Impact:** Fixes 14 failures (benchmark generator + report generator)  
**Effort:** 15 min  
**Verification:** `python -m pytest tests/benchmark/test_generator.py tests/unit/test_report_generator.py -v`

### 1.2 Fix `candidate_manifest.json` malformed JSON
**File:** `benchmarks/metadata/candidate_manifest.json`  
**Change:** Add closing `"` to 24 path values (lines 92, 104, 116, 128, 140, 152, 164, 176, 188, 200, 212, 224, 236, 248, 260, 272, 284, 296, 308, 320, 332, 344, 352, 364)  
**Impact:** Fixes 9 failures (manifest validation tests)  
**Effort:** 15 min  
**Verification:** `python -c "import json; json.load(open('benchmarks/metadata/candidate_manifest.json'))"`

### 1.3 Fix `MockIngestionEngine` import errors
**Files:** 4 test files with collection errors  
**Change:** Update import path from `src.miie.processing.ingestion` to `tests.fixtures.mock_services` (or add `MockIngestionEngine` to production module)  
**Impact:** Unblocks 4 test modules (unknown test count)  
**Effort:** 15 min  
**Verification:** `python -m pytest tests/integration/test_reproducibility.py tests/integration/test_workflows.py tests/performance/test_profiling.py tests/integration/test_segmentation_integration.py --collect-only`

### 1.4 Bulk-fix `WindowDefinition` constructor calls (~35 failures)
**Files:** 20+ test files  
**Change:** Replace all `WindowDefinition(start_date=..., end_date=...)` and `WindowDefinition(id=..., ...)` with:
```python
WindowDefinition(
    window_id="w01",  # or w02, w03, etc.
    start_date=datetime.date(2026, 1, 1),
    end_date=datetime.date(2026, 2, 1),
    commits=30,
    strategy="fixed_size"
)
```
Also fix `tests/fixtures/mock_services.py:126` (MockSegmentationEngine).  
**Impact:** Fixes ~35 failures  
**Effort:** 1 hr  
**Verification:** `python -m pytest tests/ -v --tb=line 2>&1 | grep -c "WindowDefinition"`

### 1.5 Fix `EvidencePackage` test expectations (~14 failures)
**Files:** `test_evidence.py`, `test_evidence_integration.py`, `test_evidence_package.py`, `test_mock_explanation.py`  
**Change:** Rewrite tests to use actual `EvidencePackage` schema fields:
- `provenance` (Provenance instance, not dict)
- `windows` (List[WindowDefinition])
- `metrics` (Dict[str, Any])
- `detector_outputs` (DetectorResults)
- `scores` (ScorePackage)
- `warnings` (List[WarningItem])
- Remove assertions on non-existent: `evidence_id`, `timestamp`, `score_package_id`, `detector_results_ids`, `metrics_used`, `windows_analyzed`, `das_notation`
**Impact:** Fixes ~14 failures  
**Effort:** 2 hr  
**Verification:** `python -m pytest tests/unit/test_evidence.py tests/integration/test_evidence_integration.py tests/schema/test_evidence_package.py -v`

### 1.6 Fix `ScorePackage` constructor calls (~5 failures)
**Files:** `test_validators.py`, `mock_services.py`  
**Change:** Replace `ScorePackage()` with:
```python
ScorePackage(
    integrity=IntegrityScore(overall=1.0, per_metric={}, formula_version="1.0.0"),
    confidence=ConfidenceScore(overall=0.0, factors={}, band=None),
    timestamp=datetime.now(timezone.utc),
    config_hash=""
)
```
**Impact:** Fixes ~5 failures  
**Effort:** 30 min  
**Verification:** `python -m pytest tests/contract/test_validators.py -v`

### 1.7 Fix `ReportOutput` attribute mismatch (~10 failures)
**Files:** `test_report_generator.py`, `test_report_generation.py`, `test_day10_dry_run_pipeline.py`  
**Change:** Update test assertions to use `report_output.report_paths` instead of `report_output.file_paths`, `report_output.manifest_path`, `report_output.checksums`  
**Impact:** Fixes ~10 failures  
**Effort:** 1 hr  
**Verification:** `python -m pytest tests/unit/test_report_generator.py tests/integration/test_report_generation.py -v`

### Phase 1 Verification
```bash
python -m pytest tests/ -v --tb=short 2>&1 | tail -5
# Target: 0 failures, 0 collection errors
```

**Phase 1 Total Effort:** ~5 hrs  
**Expected Result:** 0-5 failures (down from 78), 0 collection errors (down from 9)

---

## Phase 2: Critical Production Bugs — Day 2

**Goal:** Fix scoring engine NameError bugs, f₁ formula, and evidence engine non-determinism.

### 2.1 Fix scoring engine NameError bugs (6 occurrences)
**File:** `src/miie/processing/scoring/engine.py`  
**Changes:**
- Line 175: `detector_output` → `det_output`
- Line 188: `detector_output` → `det_output`
- Line 228: `detector_output` → `det_output`
- Line 241: `detector_output` → `det_output`
- Line 281: `detector_output` → `det_output`
- Line 294: `detector_output` → `det_output`
**Impact:** Unblocks detector severity extraction; scoring engine now correctly computes IS when detectors fire  
**Effort:** 10 min  
**Verification:** Write test with D-01 output `{"drift_detected": True, "ks_statistic": 0.3}` → no NameError

### 2.2 Fix scoring engine f₁ sample-size factor
**File:** `src/miie/processing/scoring/engine.py:378-394`  
**Change:** Replace magnitude sum with count:
```python
# Current (WRONG):
points_sum += abs(val)
# ...
total_points += points_sum

# Correct:
# Don't accumulate points_sum at all. Use valid_points count.
total_points += valid_points
```
**Impact:** f₁ now correctly measures `min(1.0, mean_n / 50.0)` per TFS Section 7.4  
**Effort:** 15 min  
**Verification:** Test with 10 data points → f₁ = 0.2 (not 1.0)

### 2.3 Fix evidence engine timestamp contamination
**File:** `src/miie/processing/evidence.py:42, 50`  
**Changes:**
- Line 42: `evidence_id = f"EV-{int(now.timestamp())}-..."` → `evidence_id = f"EV-{seed}-..."` (deterministic from seed)
- Line 50: `das_notation = f"DAS-{int(now.timestamp())}-..."` → `das_notation = f"DAS-{seed}-..."` (deterministic from seed)
- Remove dead variables on lines 42-50 (computed but never used in EvidencePackage)
- Line 46: Add guard `if windows and hasattr(windows[0], 'window_id'):` to prevent IndexError  
**Impact:** Evidence engine now produces deterministic output for same inputs  
**Effort:** 30 min  
**Verification:** Run same evidence generation twice → identical `evidence_id` and `das_notation`

### 2.4 Write new tests for scoring engine detection paths
**File:** `tests/unit/test_scoring_engine.py` (new tests)  
**Add tests:**
1. `test_d01_drift_detected_with_ks_statistic` — D-01 with `{"drift_detected": True, "ks_statistic": 0.3}` → no crash, severity = 0.6
2. `test_d01_drift_detected_with_score_field` — D-01 with `{"score": 0.7}` → no crash, severity = 0.7
3. `test_d02_breakdown_detected_with_delta_r` — D-02 with `{"correlation_breakdown": True, "delta_r": 0.4}` → severity = 1.33 (capped at 1.0)
4. `test_d03_compression_detected_with_index` — D-03 with `{"threshold_compressed": True, "compression_index": 0.8}` → severity = 0.8
5. `test_f1_sample_size_factor_uses_count` — 10 data points → f₁ = 0.2
6. `test_f1_sample_size_factor_empty_data` → f₁ = 0.0
**Effort:** 1 hr  
**Verification:** All 6 new tests pass

### 2.5 Write determinism tests for evidence engine
**File:** `tests/unit/test_evidence.py` (new tests)  
**Add tests:**
1. `test_evidence_id_deterministic_for_same_seed` — Same seed → same evidence_id
2. `test_das_notation_deterministic_for_same_seed` — Same seed → same das_notation
3. `test_different_seeds_produce_different_ids` — Different seeds → different evidence_ids
**Effort:** 30 min  
**Verification:** All 3 new tests pass

### Phase 2 Verification
```bash
python -m pytest tests/unit/test_scoring_engine.py tests/unit/test_evidence.py -v
# Target: All pass, including new tests
```

**Phase 2 Total Effort:** ~3 hrs  
**Expected Result:** Scoring engine functional, evidence engine deterministic, 9 new tests passing

---

## Phase 3: CLI Implementation — Days 3-4

**Goal:** Implement `miie analyze --dry-run` (Day 10 requirement) + essential subcommands.

### 3.1 Implement `miie analyze` with `--dry-run`
**File:** `src/miie/cli.py`  
**Change:** Implement the `analyze` subcommand per `ICLIAnalyze` Protocol:
- `--repo PATH` (required): Repository path
- `--output DIR` (default: `./output`): Output directory  
- `--seed INT` (default: 42): Random seed
- `--dry-run` flag: Run pipeline without writing output
- `--metrics TEXT` (optional): Comma-separated metric filter
- Exit codes: 0=success, 2=error, 3=invalid input  
**Pipeline integration:** Wire through `PipelineOrchestrator.run_analysis()`  
**Effort:** 4 hr  
**Verification:** `miie analyze --dry-run --repo . --output ./test_output --seed 42` completes without error

### 3.2 Implement `miie ingest` subcommand
**File:** `src/miie/cli.py`  
**Change:** Per `ICLIIngest` Protocol:
- `--repo PATH` (required)
- `--cache-dir PATH` (optional)
- `--keep-cache` flag
- `--shallow-depth INT` (default: 100)  
**Effort:** 1.5 hr  
**Verification:** `miie ingest --repo .` produces ingestion output

### 3.3 Implement remaining subcommands (detect, benchmark, evaluate, explain, export, generate)
**File:** `src/miie/cli.py`  
**Change:** Implement 6 subcommands per their respective Protocol contracts  
**Effort:** 6 hr (1 hr each)  
**Verification:** `python -m miie --help` shows all subcommands; each `--help` works

### 3.4 Write CLI tests
**File:** `tests/unit/test_cli.py` (new file)  
**Tests:**
1. `test_cli_version` — `miie --version` shows version
2. `test_cli_help` — `miie --help` shows all subcommands
3. `test_analyze_dry_run` — `miie analyze --dry-run --repo .` exits 0
4. `test_analyze_missing_repo` — `miie analyze` exits 3 (invalid input)
5. `test_ingest_runs` — `miie ingest --repo .` exits 0
6. `test_all_subcommands_help` — Each subcommand `--help` works  
**Effort:** 2 hr  
**Verification:** `python -m pytest tests/unit/test_cli.py -v` — all pass

### Phase 3 Verification
```bash
miie --version
miie analyze --dry-run --repo . --output ./test_output --seed 42
python -m pytest tests/unit/test_cli.py -v
```

**Phase 3 Total Effort:** ~13.5 hr  
**Expected Result:** CLI fully functional, `--dry-run` works, 6+ CLI tests passing

---

## Phase 4: Missing Deliverables — Days 5-7

**Goal:** Implement missing Day 16/17 deliverables and generate benchmark candidates.

### 4.1 Implement `benchmarks/ground_truth.py` (Day 16)
**File:** `benchmarks/ground_truth.py` or `src/miie/benchmark/ground_truth.py`  
**Change:** Implement `IGroundTruthManager` Protocol:
- `submit_annotation(candidate_id, annotator_id, label, confidence)`
- `resolve_conflict(candidate_id)` → Cohen's Kappa adjudication
- `get_ground_truth(candidate_id)` → GroundTruth schema  
**Schema:** Enhance `GroundTruthInput` in `models.py`  
**Tests:** `tests/benchmark/test_ground_truth.py` (4+ tests)  
**Effort:** 6 hr  
**Verification:** `python -m pytest tests/benchmark/test_ground_truth.py -v`

### 4.2 Implement `benchmarks/runners/` (Day 17)
**File:** `src/miie/benchmark/runner.py`, `benchmarks/runners/config.yaml`  
**Change:** Implement `IBenchmarkRunner` Protocol:
- `run_benchmark(suite_id, detectors, config)` → BenchmarkRun
- Suite loading from `benchmarks/datasets/candidates/`
- Detector isolation
- Temporal isolation  
**Tests:** `tests/benchmark/test_runner.py` (6+ tests)  
**Effort:** 8 hr  
**Verification:** `python -m pytest tests/benchmark/test_runner.py -v`

### 4.3 Generate remaining benchmark candidates (Day 15)
**Change:** Generate 109 additional candidate directories (candidates 012-120) across 3 benchmark suites:
- B-01: Metric drift candidates (40)
- B-02: Correlation breakdown candidates (40)  
- B-03: Threshold compression candidates (29)
**Update manifest:** Fix existing 30 entries, add 90 new entries  
**Effort:** 6 hr (scripted generation)  
**Verification:** `ls benchmarks/datasets/candidates/ | wc -l` → 120

### 4.4 Create missing documentation files
**Files:**
- `requirements.txt` (Day 0)
- `LICENSE` (Day 0)
- `CONTRIBUTING.md` (Day 0)
- `docs/architecture.md` (Day 2)
- `docs/day_10_review.md` (Day 10)
**Effort:** 2 hr  
**Verification:** All files exist and are non-empty

### 4.5 Clean up scratch files
**Files to delete:**
- `src/miie/contracts/interfaces_clean.py`
- `src/miie/contracts/interfaces_clean2.py`
- `src/miie/schemas/models_temp.py`
- `src/miie/validation/test_validation_service.py` (or refactor into proper test)
**Files to merge:** Merge CLI Protocols from `interfaces_clean.py` into production `interfaces.py`  
**Effort:** 1 hr  
**Verification:** `find src/miie -name "*_clean*" -o -name "*_temp*" | wc -l` → 0

### Phase 4 Verification
```bash
python -m pytest tests/benchmark/ -v
ls benchmarks/datasets/candidates/ | wc -l  # → 120
ls requirements.txt LICENSE CONTRIBUTING.md docs/architecture.md docs/day_10_review.md
```

**Phase 4 Total Effort:** ~23 hr  
**Expected Result:** All missing deliverables present, 120 benchmark candidates, scratch files cleaned

---

## Phase 5: Test Suite Hardening — Days 8-9

**Goal:** Achieve ≥95% test pass rate with no flaky tests.

### 5.1 Run full test suite and fix remaining failures
**Command:** `python -m pytest tests/ -v --tb=short`  
**Action:** Fix any remaining failures (estimated 2-5 edge cases)  
**Effort:** 3 hr  
**Verification:** 0 failures

### 5.2 Add pytest-cov and generate coverage report
**Change:** Add `pytest-cov` to requirements, run with `--cov=src/miie --cov-report=term-missing`  
**Target:** ≥90% line coverage on `src/miie/`  
**Effort:** 2 hr (coverage gaps → write tests)  
**Verification:** Coverage report shows ≥90%

### 5.3 Add regression tests for all FERA critical findings
**File:** `tests/regression/test_fera_critical_findings.py` (new)  
**Tests:**
1. `test_scoring_engine_no_nameerror_with_all_detectors` — Regression for C1
2. `test_f1_uses_count_not_magnitude` — Regression for C2
3. `test_evidence_id_deterministic` — Regression for C3
4. `test_cli_analyze_dry_run` — Regression for C4
5. `test_candidate_manifest_valid_json` — Regression for C5
6. `test_all_30_candidates_exist` — Regression for C5
**Effort:** 2 hr  
**Verification:** All regression tests pass

### Phase 5 Verification
```bash
python -m pytest tests/ -v --cov=src/miie --cov-report=term-missing
# Target: 0 failures, ≥90% coverage
```

**Phase 5 Total Effort:** ~7 hr  
**Expected Result:** 0 failures, ≥90% coverage, regression tests for all critical findings

---

## Phase 6: Final Audit Prep — Day 10

### 6.1 Run complete FERA re-audit
**Command:** Full 12-phase FERA audit  
**Target:** ≥95% on all phases  
**Effort:** 2 hr  
**Verification:** FERA scorecard shows ≥95%

### 6.2 Update FERA_LOOP_STATE.json
**Change:** Set `audit_complete = true`, `LOOP_STATUS = TERMINATED`, new scores  
**Effort:** 15 min

---

## Effort Summary

| Phase | Description | Effort | Days |
|-------|-------------|--------|------|
| 1 | Quick Wins (root causes) | 5 hr | Day 1 |
| 2 | Critical Production Bugs | 3 hr | Day 2 |
| 3 | CLI Implementation | 13.5 hr | Days 3-4 |
| 4 | Missing Deliverables | 23 hr | Days 5-7 |
| 5 | Test Suite Hardening | 7 hr | Days 8-9 |
| 6 | Final Audit Prep | 2.25 hr | Day 10 |
| **TOTAL** | | **~54 hr** | **10 days** |

---

## Execution Sequence (Critical Path)

```
Day 1:  RC-4 (json_dumps) → RC-7 (manifest) → RC-6 (imports) → RC-1 (WindowDefinition) → RC-5 (ReportOutput) → RC-2 (EvidencePackage) → RC-3 (ScorePackage)
        ↓
Day 2:  2.1 (NameError) → 2.2 (f₁) → 2.3 (evidence timestamp) → 2.4-2.5 (new tests)
        ↓
Day 3-4: 3.1 (analyze --dry-run) → 3.2 (ingest) → 3.3 (remaining) → 3.4 (CLI tests)
        ↓
Day 5-7: 4.1 (ground_truth) → 4.2 (runners) → 4.3 (candidates) → 4.4 (docs) → 4.5 (cleanup)
        ↓
Day 8-9: 5.1 (fix remaining) → 5.2 (coverage) → 5.3 (regression tests)
        ↓
Day 10: 6.1 (re-audit) → 6.2 (loop state)
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| New tests break existing passing tests | Run full suite after each phase; fix regressions immediately |
| CLI integration reveals new bugs | Implement with mock engines first; wire to real engines last |
| Benchmark generation takes longer than estimated | Generate 60 candidates minimum (not 120) as fallback |
| Schema changes needed for ground truth | Use existing `GroundTruthInput` placeholder; enhance incrementally |

---

## Success Criteria

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Test pass rate | 77.8% | ≥98% | `pytest --tb=line` |
| Test failures | 78 | ≤5 | `pytest` summary |
| Collection errors | 9 | 0 | `pytest --collect-only` |
| CLI functional | No | Yes | `miie analyze --dry-run` exits 0 |
| Evidence deterministic | No | Yes | Same seed → same ID |
| Scoring NameError bugs | 5 | 0 | Code inspection + tests |
| Benchmark candidates | 11 | ≥60 (120 target) | `ls candidates/ | wc -l` |
| FERA score | 40.5% | ≥95% | FERA re-audit |
