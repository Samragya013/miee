# FERA Repository Inventory

> Phase 2 — Repository Inventory
> Agent: BackendArchitect · Skills: codebase-investigator, filesystem-analyzer
> Method: actual filesystem scan. No reports trusted.

## 1. Repository identity

- Path: `C:\Users\Samragya\Downloads\MIEE`
- Git: YES. Branch: `autoresearch/miie/validation`
- HEAD: `a12830c experiment: Skip problematic test files that fail to collect due to missing MockIngestionEngine`
- Working tree: dirty (modified `output/`, `tmp_output*`, `src/miie/schemas/models.py`; deleted `test_output_multiple/candidate_005/src/metric_*.txt`; untracked `.autoresearch/`, multiple root audit `.md`)

## 2. Source modules (`src/miie/`) — actual files

```
cli.py                       (14 lines — STUB: click group + --version only)
__init__.py, __main__.py
benchmark/      evaluation.py, generator.py, runner.py, __init__.py
common/         __init__.py  (empty)
contracts/      dataclasses.py, errors.py, interfaces.py,
                interfaces_clean.py    ← scratch leftover
                interfaces_clean2.py   ← scratch leftover
                validators.py, __init__.py
detection/      __init__.py  (empty — duplicate of processing/detection/)
interface/       __init__.py  (empty)
orchestration/   pipeline.py (261 lines), workflow.py, __init__.py
processing/      evidence.py (128 lines), extraction.py, ingestion.py (340 lines),
                segmentation.py (190 lines), __init__.py
  benchmark/     engine.py, __init__.py
  detection/     base.py, correlation_breakdown_detector.py (314 lines),
                  dispatcher.py, distribution_drift_detector.py,
                  mock_detectors.py, registry.py, runner.py,
                  threshold_compression_detector.py, __init__.py
  evaluation/    engine.py, __init__.py
  explanation/    engine.py, mock_explanation.py, __init__.py
  reporting/      engine.py, __init__.py
  scoring/        engine.py (544 lines), mock_scoring.py, __init__.py
reporting/       __init__.py  (empty — duplicate of processing/reporting/)
schemas/         metric_registry.py, models.py, models_temp.py ← scratch leftover,
                serialization.py, __init__.py +
                *.schema.json ×4 (detector_result, evidence_package,
                                   metric_dataframe, repository_context)
storage/         __init__.py  (empty)
validation/      service.py, test_validation_service.py  ← TEST FILE INSIDE src
```

## 3. Test files (`tests/`) — actual

```
conftest.py, __init__.py
architecture/   test_layer_dependencies.py, test_no_circular_imports.py,
                test_package_structure.py        (8 tests PASS)
benchmark/       test_candidate_manifest.py, test_evaluation.py,
                test_evaluation_integration.py, test_generator.py,
                test_runner.py, test_validation.py
contract/        conftest.py, test_dtos.py, test_errors.py,
                test_interfaces.py, test_validators.py
fixtures/        mock_services.py
integration/     test_evidence_integration.py, test_extraction_to_detection.py,
                test_extraction_to_detection_to_scoring.py,
                test_ingestion_to_extraction.py, test_ingestion_to_pipeline.py,
                test_pipeline_skeleton.py, test_report_generation.py,
                test_segmentation_integration.py
performance/     test_profiling.py
schema/          test_detector_result.py, test_evidence_package.py,
                test_metric_dataframe.py, test_repository_context.py
unit/            test_benchmark_engine.py, test_cache_paths.py,
                test_d02_correlation_breakdown.py, test_d03_threshold_compression.py,
                test_day10_dry_run_pipeline.py, test_detector_dispatcher.py,
                test_detector_registry.py, test_detector_runner.py,
                test_evaluation_engine.py, test_evidence.py, test_explanation_engine.py,
                test_ingestion.py, test_metric_extraction.py, test_metric_registry.py,
                test_mock_explanation.py, test_report_generator.py,
                test_repository_context_extraction.py, test_scoring_engine.py,
                test_segmentation.py, test_serialization.py, test_version.py,
                test_workflow.py
workflow/         test_reproducibility.py, test_workflows.py
```

Plus **scratch test files at repo root** polluting collection: `error_contracts_test.py`, `error_contracts_test2.py`, `test_analysis_pipeline.py`, `test_error.py`, `test_first_part.py`, `test_first_part_2.py`, `test_gen.py`, `reproducibility_test*.py`, `analyze_tests.py`, `debug_*.py`.

## 4. Benchmark data inventory

- `benchmarks/datasets/candidates/` — **11 candidate dirs** on disk (candidate_001 … candidate_011)
- `benchmarks/metadata/candidate_manifest.json` — EXISTS but **claims 30** and is **malformed JSON** (`JSONDecodeError: Invalid control character at line 92 col 60`)
- `benchmarks/tmp/metric-drift/` — 11 candidate dirs (scratch duplicates)
- `benchmarks/README.md`, `benchmarks/annotations/annotation_workflow.md` — EXISTS
- `benchmarks/runners/` — **MISSING**
- `benchmarks/candidate_acceptance_criteria.md`, `repository_fixture_requirements.md`, `metric_availability_matrix.md` — EXISTS; `evidence_expectation_matrix.md` — MISSING

## 5. Autoresearch experiment artifacts

```
.autoresearch/miie/validation/   config.cfg, loop.json, program.md, results.tsv, run.log
day15_loop.json                 cron_id 182cc34e, "Every 10 minutes",
                                "Day 15 D02 Correlation Breakdown Detector implementation"
```
A malformed duplicate dir `CUsersSamragyaDownloadsMIEE.autoresearchmiievalidation/` exists at root (path-join bug from a misconfigured run).

## 6. Governance / docs inventory

- `docs/governance/` — freeze_register.md, terminology_registry.md, authority_matrix.md, day0_signoff.md all **EXISTS** ✓; extensive signoff/readiness-gate tree present (claims, untrusted)
- `docs/architecture.md` — **MISSING** (Day 2 deliverable)
- `docs/day_10_review.md` — **MISSING** (Day 10 deliverable)
- `docs/execution/completion_reports/` — present (claims)
- `research/` — literature_notes.md, repository_selection_notes.md, research_traceability.md, threats_to_validity.md, dataset_registry.md **EXISTS**; segmentation_strategies.md, metric_extraction_rationale.md, evidence_publication_mapping.md **MISSING**

## 7. Project / tooling

- `pyproject.toml` — Poetry, name=miie, version=1.0.0, entry `miie=miie.cli:cli`, deps numpy/pandas/scipy/jinja2/click/fastapi (pinned)
- `poetry.lock` — EXISTS
- `requirements.txt` — **MISSING** (Day 1 deliverable)
- `.pre-commit-config.yaml` — EXISTS
- `.github/workflows/ci.yml` — EXISTS (content not verified to run install/lint/type/test per plan)
- `LICENSE` — **MISSING** (pyproject declares MIT; no LICENSE file committed)
- `CONTRIBUTING.md` — **MISSING**

## 8. Red flags / hygiene

1. Scratch files in production source: `interfaces_clean.py`, `interfaces_clean2.py`, `models_temp.py`.
2. Test file inside source tree: `src/miie/validation/test_validation_service.py`.
3. Duplicate parallel package layout: top-level `benchmark/`, `reporting/`, `detection/`, `interface/`, `storage/`, `common/` (empty) vs `processing/{benchmark,reporting,detection}` — incomplete refactor.
4. Root-level scratch test files pollute pytest collection (32 collection errors).
5. Branch is an `autoresearch/*` experiment branch, not `main`.

## 9. State

```
inventory_complete = true
```
