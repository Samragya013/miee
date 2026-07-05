# FERA Runtime Execution Audit

> Phase 4 — Runtime Execution Audit
> Agent: TestEngineer · Skills: test-runner, debugger
> Method: actual `pytest` execution on the repository. No reports trusted.

## 1. Execution environment
- Python 3.11.2544.0 (Windows); deps from `pyproject.toml` (numpy/pandas/scipy/jinja2/click/fastapi). `pytest` 7.x.
- Invocation: `python -m pytest --continue-on-collection-errors -q -o addopts="" --ignore=benchmarks --ignore=debug_test --ignore=test_output* --ignore=tmp_output*` (generated benchmark/test_output dirs ignored to isolate the MIIE codebase).

## 2. Headline result
```
351 tests collected, 32 errors during collection
78 failed, 273 passed, 4 warnings, 9 errors
runtime: 76.8 s
```
- Collectable pass rate: **273 / (273+78) = 77.8 %**
- Including collection errors as failures: **273 / 360 = 75.8 %**
- Plan target (Day 10): ≥ 70 % scaffold coverage → *collection count* meets target, but **22.5 % of collectable tests fail and 9 modules cannot be imported.**

## 3. Collection errors (modules that cannot be imported) — 9

| File | Root cause |
|---|---|
| `tests/workflow/test_reproducibility.py` | `ImportError: cannot import name 'MockIngestionEngine' from src.miie.processing.ingestion` |
| `tests/workflow/test_workflows.py` | same `MockIngestionEngine` ImportError |
| `tests/performance/test_profiling.py` | same `MockIngestionEngine` ImportError |
| `tests/integration/test_segmentation_integration.py` | same `MockIngestionEngine` ImportError |
| `error_contracts_test.py`, `test_analysis_pipeline.py`, `test_error.py`, `test_first_part_2.py`, `test_gen.py` | root-level scratch test files polluting collection (`test_gen.py` also raises `PermissionError WinError 5`) |

**Interpretation:** `ingestion.py` exports only `RepositoryIngestionEngine`. The `MockIngestionEngine` that Day-19 workflow/reproducibility/profiling tests import was removed/renamed. **Day 19's core deliverables cannot run.** This is the single most damaging runtime defect — it is why an autoresearch commit explicitly "Skip problematic test files that fail to collect due to missing MockIngestionEngine".

## 4. Failures by file (78 failures)

| Test file | Failures |
|---|---|
| `tests/contract/test_validators.py` | 13 |
| `tests/unit/test_evidence.py` | 8 |
| `tests/benchmark/test_validation.py` | 7 |
| `tests/unit/test_report_generator.py` | 6 |
| `tests/integration/test_evidence_integration.py` | 5 |
| `tests/unit/test_workflow.py` | 5 |
| `tests/integration/test_report_generation.py` | 4 |
| `tests/unit/test_mock_explanation.py` | 4 |
| `tests/unit/test_explanation_engine.py` | 4 |
| `tests/benchmark/test_generator.py` | 4 |
| `reproducibility_test.py` (root scratch) | 4 |
| `src/miie/validation/test_validation_service.py` (test-in-src) | 4 |
| `tests/integration/test_pipeline_skeleton.py` | 3 |
| `tests/schema/test_evidence_package.py` | 3 |
| `tests/integration/test_ingestion_to_pipeline.py` | 3 |
| `tests/unit/test_scoring_engine.py` | 2 |
| `tests/benchmark/test_candidate_manifest.py` | 2 |
| `tests/unit/test_day10_dry_run_pipeline.py` | 1 |

## 5. Pass confirmations (verified)

| Area | Result |
|---|---|
| `tests/unit/test_version.py` | 2 PASS (`miie --version` = 1.0.0) |
| `tests/architecture/` (layer deps, circular imports, package structure) | 8 PASS |
| `tests/unit/test_ingestion.py`, `test_repository_context_extraction.py`, `test_cache_paths.py` | PASS |
| `tests/unit/test_segmentation.py` | PASS |
| `tests/unit/test_metric_registry.py`, `test_metric_extraction.py` | PASS |
| `tests/unit/test_detector_{registry,runner,dispatcher}.py` | PASS |
| `tests/benchmark/test_evaluation.py`, `test_runner.py`, `test_evaluation_integration.py` | 35 PASS |
| `tests/unit/test_serialization.py`, schema tests (19/22) | mostly PASS |

## 6. CLI runtime verification (Day 10)
```
$ python -m miie --help
Usage: python -m miie [OPTIONS] COMMAND [ARGS]...
Options: --version  --help
```
There is **no `analyze` subcommand and no `--dry-run` option.** Day 10's primary deliverable (`miie analyze --dry-run --repo <path> --output <dir> --seed 42`) is **not executable at runtime.** Dry-run artifacts (manifest.json/results.json/dry_run_report.md/metrics.csv/evidence.json/run_metrics.json) cannot be produced via the CLI.

## 7. Runtime defects confirmed by code inspection

| Defect | Location | Impact |
|---|---|---|
| `NameError: detector_output` (undefined; loop var is `det_output`) | `src/miie/processing/scoring/engine.py:175,188,228,281,294` | Scoring engine crashes whenever a detector fires with a magnitude field → scoring tests fail |
| Non-deterministic evidence IDs | `src/miie/processing/evidence.py:42,50` (`evidence_id=f"evidence_{seed}_{int(now.timestamp())}"`, `das_notation` same) | Violates Day 9/10 "two runs byte-identical / no current timestamp" |
| `Provenance.timestamp = now` | `evidence.py:66` | Same |
| f₁ uses sum-of-abs-values as proxy for sample-size n | `scoring/engine.py:383-394` | Mathematically wrong confidence factor |
| Manifest malformed JSON | `benchmarks/metadata/candidate_manifest.json:92` | `JSONDecodeError`; breaks any loader |

## 8. Verdict
Runtime status: **FAIL.** The CLI dry-run does not exist; 9 test modules cannot be imported; 78 tests fail; the scoring and evidence engines contain runtime-crashing and non-determinism defects. Only the ingestion/segmentation/detector-framework/schema/architecture/evaluation-fruit slices are runtime-healthy.

## State
```
runtime_verified = true   (verification outcome: FAIL)
```
