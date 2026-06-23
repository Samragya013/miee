# FERA Requirement Matrix

> Phase 1 — Operating Plan Extraction
> Agent: DocumentationEngineer · Skill: filesystem-analyzer
> Authority source: repository evidence only. Completion/certification/readiness reports are NOT trusted.

## 1. Authority Documents Located (source of truth for requirements)

| Document | Path | Status |
|---|---|---|
| Day 0–10 Operating Plan | `docs/authorities/MIIE_Day_0_to_Day_10_Execution_Operating_Plan.md` | EXISTS |
| Day 0–10 Requirement Matrix | `DAY0_TO_DAY10_REQUIREMENT_MATRIX.md` | EXISTS |
| Day 11–20 Operating Plan | `docs/authorities/MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md` | EXISTS |
| Authority specs | `docs/authorities/{ACS,AFD,BSD-Engineering,IMP,MES,PRD,TFS,TRD}_*.md`, `day7/day9_authority_matrix.md` | EXISTS |

Note: a second, lowercase copy `docs/authorities/miie_day0_to_day10_execution_operating_plan.md` also exists (duplicate — minor hygiene issue).

## 2. Certification / Readiness packages located (CLAIMS — not trusted as evidence)

The repository contains a large volume of self-reported completion/certification artifacts. Per the FERA mandate these are treated as **claims to verify**, not evidence:

`Day_0_to_Day_10_Completion_Report.md`, `DAY15_COMPLETE.md`, `DAY16_COMPLETE.md`, `DAY17_COMPLETE.md`, `DAY18_COMPLETE.md`, `DAY19_COMPLETE.md`, `DAY15_CERTIFICATION_PACKAGE.md`, `DAY15_TRD_CERTIFICATION.md`, `DAY15_MATHEMATICAL_CERTIFICATION.md`, `DAY15_REPRODUCIBILITY_CERTIFICATION.md`, `DAY15_TEST_CERTIFICATION.md`, `DAY15_READINESS_GATE.md`, `READY_FOR_DAY16.md`, `DAY7_EXECUTION_READINESS_SCORE.md`, plus prior `FERA_*.md` / `FERA_LOOP_STATE.json` at repo root.

These are **excluded from the evidence base**. Their claims are tested against source/tests/runtime in Phases 4–10.

## 3. Day 0–10 Requirements (extracted verbatim from authority)

| Day | Required deliverables (authoritative) |
|---|---|
| 0 | `docs/governance/{freeze_register,terminology_registry,authority_matrix}.md`, `day0_signoff.md` |
| 1 | `pyproject.toml`, `poetry.lock`, `requirements.txt`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, `src/miie/{__init__,__main__,cli}.py`, `tests/unit/test_version.py`; version `1.0.0`; `poetry run miie --version` returns 1.0.0 |
| 2 | `docs/architecture.md`, `src/miie/contracts/interfaces.py`, `tests/unit/test_imports.py`, `tests/unit/test_architecture_boundaries.py`; `processing` cannot import `cli`/`api` |
| 3 | `src/miie/schemas/models.py`, 4 JSON schemas (`repository_context`,`metric_dataframe`,`detector_result`,`evidence_package`), `serialization.py`; draft-07; unknown fields fail |
| 4 | `src/miie/contracts/{requests,responses,interfaces,validators,errors}.py`, `tests/contract/` |
| 5 | `orchestration/{pipeline,workflow}.py`, `tests/fixtures/{mock_services,mock_benchmark}.py`, `tests/integration/test_pipeline_skeleton.py`, `tests/unit/test_workflow.py`, `tests/unit/test_benchmark_mock.py` |
| 6 | `processing/ingestion.py`, `tests/unit/{test_ingestion,test_repository_context_extraction,test_cache_paths}.py`, `tests/integration/test_ingestion_to_pipeline.py` |
| 7 | `schemas/metric_registry.py`, `processing/extraction.py`, `tests/unit/{test_metric_registry,test_commit_frequency,test_code_churn,test_missing_metric_policy}.py`, `tests/integration/test_ingestion_to_extraction.py` |
| 8 | `processing/detection/{base,registry,runner}.py`, `benchmarks/README.md`, `benchmarks/metadata/candidate_manifest.json` (30), `benchmarks/annotations/annotation_workflow.md`, `tests/benchmark/test_candidate_manifest.py` |
| 9 | `processing/evidence.py`, `tests/unit/{test_evidence_builder,test_evidence_validator,test_evidence_serializer}.py`, `tests/integration/test_detector_to_evidence.py`; every evidence item links run_id/detector_id/metric_id |
| 10 | `cli.py` with `miie analyze --dry-run`; artifacts `{manifest,results}.json,dry_run_report.md,metrics.csv,evidence.json,run_metrics.json`; `tests/workflow/test_day10_dry_run.py`; `docs/day_10_review.md`; two runs byte-identical, no current timestamp |

## 4. Day 11–20 Requirements (extracted from authority)

| Day | Required deliverables |
|---|---|
| 11 | `processing/segmentation.py` (time/commit/custom), `WindowDefinition` in `models.py`, `tests/unit/test_segmentation.py` (10+), `tests/integration/test_segmentation_integration.py` (3+), `research/segmentation_strategies.md` |
| 12 | `processing/scoring.py` + `ScorePackage`, `tests/unit/test_scoring.py` (10+), `tests/integration/test_scoring_integration.py` (3+); IS/CS in [0,1], weights normalize to 1.0 |
| 13 | `processing/evidence.py` builder+serializer, `tests/unit/test_evidence.py` (8+), `tests/integration/test_evidence_integration.py` (2+) |
| 14 | `reporting/generator.py`, `reporting/templates/{dry_run_report,drift,correlation,compression}_explanation.j2`, `tests/unit/test_report_generator.py` (6+), `tests/integration/test_report_generation.py` (2+) |
| 15 | `benchmark/generator.py`, `benchmarks/candidates/` **120 dirs**, manifest **120 entries**, `tests/benchmark/{test_generator,test_validation}.py` |
| 16 | `benchmark/ground_truth.py`, `GroundTruth` schema, `tests/benchmark/test_ground_truth.py` (4+), `benchmarks/annotations/` |
| 17 | `benchmark/runner.py`, `BenchmarkRun` schema, `tests/benchmark/test_runner.py` (6+), `benchmarks/runners/` |
| 18 | `benchmark/evaluation.py`, `EvaluationResult` schema, `tests/benchmark/test_evaluation.py` (8+), `tests/benchmark/test_evaluation_integration.py` |
| 19 | `tests/workflow/test_workflows.py` (WF-01..05), `tests/workflow/test_reproducibility.py`, `tests/performance/test_profiling.py`; byte-identical outputs |
| 20 | Day 20 milestone review |

## 5. Note on detector deferral (fairness)

Both plans explicitly **defer real detector algorithms (D-01/D-02/D-03) to Days 21–25**. Therefore "mock detectors" is **not** a defect for Days 0–20. However, the repo *does* contain detector implementation files and an `autoresearch/miie/validation` branch with 118 "Correlation breakdown commit N: corr=0.0X" iterations — meaning detectors were started anyway and are failing. This is audited in Phases 7 and 10.

## 6. State

```
requirements_extracted = true
```
