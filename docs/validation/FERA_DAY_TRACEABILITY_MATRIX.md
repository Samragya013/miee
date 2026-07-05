# FERA Day Traceability Matrix

> Phase 3 — Day Traceability Matrix
> Agent: DocumentationEngineer
> Each required deliverable mapped to actual repository evidence (file path or verified-absent).

Legend: ✅ present & verified · ⚠️ present but defective/renamed · ❌ missing

## Day 0 — Document Reconciliation & Freeze
| Required | Evidence | Status |
|---|---|---|
| `docs/governance/freeze_register.md` | exists | ✅ |
| `docs/governance/terminology_registry.md` | exists | ✅ |
| `docs/governance/authority_matrix.md` | exists | ✅ |
| `docs/governance/day0_signoff.md` | exists | ✅ |

## Day 1 — Repository Setup
| Required | Evidence | Status |
|---|---|---|
| `pyproject.toml` | exists, version=1.0.0, entry `miie=miie.cli:cli` | ✅ |
| `poetry.lock` | exists | ✅ |
| `requirements.txt` | absent | ❌ |
| `.github/workflows/ci.yml` | exists (steps not content-verified) | ✅ |
| `.pre-commit-config.yaml` | exists | ✅ |
| `src/miie/{__init__,__main__,cli}.py` | exist | ✅ |
| `tests/unit/test_version.py` | exists, 2 tests PASS | ✅ |
| `miie --version` returns 1.0.0 | `python -m miie --version` → `1.0.0` | ✅ |
| `LICENSE`, `CONTRIBUTING.md` | both absent | ❌ |

## Day 2 — Architecture Scaffolding
| Required | Evidence | Status |
|---|---|---|
| `docs/architecture.md` | absent | ❌ |
| `src/miie/contracts/interfaces.py` | exists | ✅ |
| `tests/unit/test_imports.py` | absent (renamed) | ❌ |
| `tests/unit/test_architecture_boundaries.py` | absent (renamed to `tests/architecture/test_{layer_dependencies,no_circular_imports,package_structure}.py`, 8 PASS) | ⚠️ |
| `processing` cannot import `cli`/`api` | architecture tests PASS | ✅ |

## Day 3 — Core Schema Foundation
| Required | Evidence | Status |
|---|---|---|
| `src/miie/schemas/models.py` | exists | ✅ |
| 4 JSON schema files | all 4 exist, draft-07, `additionalProperties:false` | ✅ |
| `serialization.py` | exists; `test_serialization.py` PASS | ✅ |
| draft-07 + unknown fields fail | verified `additionalProperties:false` on all 4 | ✅ |

## Day 4 — Contract Layer
| Required | Evidence | Status |
|---|---|---|
| `contracts/requests.py`, `responses.py` | both absent | ❌ |
| `contracts/{interfaces,validators,errors,dataclasses}.py` | exist | ✅ |
| `tests/contract/` | exists; `test_validators.py` has **13 failures** | ⚠️ |

## Day 5 — Pipeline Skeleton
| Required | Evidence | Status |
|---|---|---|
| `orchestration/pipeline.py` | exists (261 lines, 9 protocol-injected engines) | ✅ |
| `orchestration/workflow.py` | exists | ✅ |
| `tests/fixtures/mock_services.py` | exists | ✅ |
| `tests/fixtures/mock_benchmark.py` | absent | ❌ |
| `tests/unit/test_benchmark_mock.py` | absent | ❌ |
| `tests/integration/test_pipeline_skeleton.py` | exists, **3 failures** | ⚠️ |
| `tests/unit/test_workflow.py` | exists, **5 failures** | ⚠️ |

## Day 6 — Repository Ingestion
| Required | Evidence | Status |
|---|---|---|
| `processing/ingestion.py` | exists (340 lines, real git subprocess metadata) | ✅ |
| `validate_repository`, `cache_path_for_repository` | exist, traversal-safe | ✅ |
| `tests/unit/test_ingestion.py`, `test_repository_context_extraction.py`, `test_cache_paths.py` | exist, PASS | ✅ |
| `tests/integration/test_ingestion_to_pipeline.py` | exists, **3 failures** | ⚠️ |
| `MockIngestionEngine` export | **NOT exported** (only `RepositoryIngestionEngine`) | ❌ (breaks Day 19) |

## Day 7 — Metric Extraction Foundation
| Required | Evidence | Status |
|---|---|---|
| `schemas/metric_registry.py` | exists; `test_metric_registry.py` PASS | ✅ |
| `processing/extraction.py` | exists; `test_metric_extraction.py` PASS | ✅ |
| `tests/unit/test_commit_frequency.py`, `test_code_churn.py`, `test_missing_metric_policy.py` | absent (consolidated into `test_metric_extraction.py`) | ❌ (by name) |
| `tests/integration/test_ingestion_to_extraction.py` | exists, PASS | ✅ |
| `research/metric_extraction_rationale.md` | absent | ❌ |

## Day 8 — Detector Framework + Benchmark 30
| Required | Evidence | Status |
|---|---|---|
| `processing/detection/{base,registry,runner,dispatcher}.py` | exist | ✅ |
| `tests/unit/test_detector_{registry,runner,dispatcher}.py` | exist, PASS | ✅ |
| `benchmarks/README.md` | exists | ✅ |
| `benchmarks/metadata/candidate_manifest.json` (30) | claims 30, **malformed JSON**, only **11 dirs on disk** | ❌ |
| `benchmarks/annotations/annotation_workflow.md` | exists | ✅ |
| `tests/benchmark/test_candidate_manifest.py` | exists, **2 failures** | ⚠️ |
| Detector math deferred? | **NO** — `correlation_breakdown_detector.py` (314 lines), `distribution_drift_detector.py`, `threshold_compression_detector.py` implemented (contradicts "deferred") | ⚠️ |

## Day 9 — Evidence Framework
| Required | Evidence | Status |
|---|---|---|
| `processing/evidence.py` | exists (128 lines) | ⚠️ |
| Per-item traceability (run_id/detector_id/metric_id) | **not enforced** — packages whole `detector_outputs`/`metrics` | ❌ |
| Deterministic serialization | **non-deterministic** — `evidence_id`/`das_notation` embed `int(now.timestamp())`; `Provenance.timestamp=now` | ❌ |
| `tests/unit/test_evidence_{builder,validator,serializer}.py` | absent (consolidated to `test_evidence.py`) | ❌ (by name) |
| `tests/unit/test_evidence.py` | exists, **8 failures** | ❌ |
| `tests/integration/test_detector_to_evidence.py` | absent (renamed `test_evidence_integration.py`, **5 failures**) | ❌ |
| `research/evidence_publication_mapping.md` | absent | ❌ |

## Day 10 — End-to-End Dry Run
| Required | Evidence | Status |
|---|---|---|
| `cli.py` `miie analyze --dry-run` | **NOT IMPLEMENTED** — `cli.py` is 14-line stub (`--version`/`--help` only) | ❌ |
| Dry-run artifacts (6 files) | cannot be produced via CLI | ❌ |
| `tests/workflow/test_day10_dry_run.py` | absent (renamed `tests/unit/test_day10_dry_run_pipeline.py`, **1 failure**) | ❌ |
| `docs/day_10_review.md` | absent | ❌ |
| Two runs byte-identical, no timestamp | not demonstrable (no CLI; evidence engine injects timestamp) | ❌ |

## Day 11 — Window Segmentation
| Required | Evidence | Status |
|---|---|---|
| `processing/segmentation.py` (time/commit/custom) | exists (190 lines) | ✅ |
| `WindowDefinition` in `models.py` | exists | ✅ |
| `tests/unit/test_segmentation.py` | exists, PASS | ✅ |
| `tests/integration/test_segmentation_integration.py` | exists, **collection ERROR** (MockIngestionEngine import) | ❌ |
| `research/segmentation_strategies.md` | absent | ❌ |
| Non-overlapping ordered windows | `time` strategy yields **single** window; `commit` uses 1-day range | ⚠️ |

## Day 12 — Scoring Engine
| Required | Evidence | Status |
|---|---|---|
| `processing/scoring.py` / `engine.py` | exists (544 lines) | ⚠️ |
| `ScorePackage` schema | exists | ✅ |
| `tests/unit/test_scoring.py` (10+) | absent | ❌ |
| `tests/unit/test_scoring_engine.py` | exists, **2 failures** | ❌ |
| `tests/integration/test_scoring_integration.py` | absent | ❌ |
| IS/CS in [0,1], weights=1.0 | NameError bugs crash runtime; f₁ uses wrong proxy | ❌ |

## Day 13 — Evidence Integration
| Required | Evidence | Status |
|---|---|---|
| `processing/evidence.py` builder+serializer | exists but non-deterministic | ⚠️ |
| `tests/unit/test_evidence.py` (8+) | exists, **8 failures** | ❌ |
| `tests/integration/test_evidence_integration.py` | exists, **5 failures** | ❌ |

## Day 14 — Report Generator
| Required | Evidence | Status |
|---|---|---|
| `reporting/generator.py` | exists as `processing/reporting/engine.py` | ✅ (relocated) |
| 4 j2 templates | all 4 exist | ✅ |
| `tests/unit/test_report_generator.py` (6+) | exists, **6 failures** | ❌ |
| `tests/integration/test_report_generation.py` | exists, **4 failures** | ❌ |

## Day 15 — Benchmark Expansion 30→120
| Required | Evidence | Status |
|---|---|---|
| `benchmarks/candidates/` 120 dirs | **11 dirs** on disk | ❌ |
| manifest 120 entries | claims 30, malformed JSON | ❌ |
| `tests/benchmark/test_generator.py` | exists, **4 failures** | ❌ |
| `tests/benchmark/test_validation.py` | exists, **7 failures** | ❌ |

## Day 16 — Ground Truth Workflow
| Required | Evidence | Status |
|---|---|---|
| `benchmark/ground_truth.py` | **absent** | ❌ |
| `GroundTruth` schema | not in models (unverified) | ❌ |
| `tests/benchmark/test_ground_truth.py` | absent | ❌ |

## Day 17 — Benchmark Runner
| Required | Evidence | Status |
|---|---|---|
| `benchmark/runner.py` | exists | ✅ |
| `BenchmarkRun` schema | exists | ✅ |
| `tests/benchmark/test_runner.py` (6+) | exists, PASS | ✅ |
| `benchmarks/runners/` | absent | ❌ |
| Detector/temporal isolation, leakage prevention | not verified by passing tests | ⚠️ |

## Day 18 — Evaluation Engine
| Required | Evidence | Status |
|---|---|---|
| `benchmark/evaluation.py` | exists | ✅ |
| `EvaluationResult` schema | exists | ✅ |
| `tests/benchmark/test_evaluation.py` (8+) | exists, PASS (35 across eval/runner/integration) | ✅ |
| `tests/benchmark/test_evaluation_integration.py` | exists, PASS | ✅ |

## Day 19 — Integration & E2E Testing
| Required | Evidence | Status |
|---|---|---|
| `tests/workflow/test_workflows.py` (WF-01..05) | exists, **collection ERROR** | ❌ |
| `tests/workflow/test_reproducibility.py` | exists, **collection ERROR** | ❌ |
| `tests/performance/test_profiling.py` | exists, **collection ERROR** | ❌ |
| Byte-identical reproducibility | not demonstrable (evidence engine non-deterministic; CLI missing) | ❌ |
| `reproducibility_test.py` (root scratch) | **4 failures** | ❌ |

## Day 20 — Milestone Review
| Required | Evidence | Status |
|---|---|---|
| Day 20 review document | `DAY20_COMPLETE.md` exists (claim); plan's Day-20 status table is largely false per evidence | ⚠️ |

## State
```
traceability_complete = true
```
