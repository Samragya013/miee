# FERA Architecture Audit

> Phase 5 — Architecture Audit
> Agent: TRDArchitect · Skills: architecture-reviewer, dependency-analyzer
> Method: source structure + import graph + architecture tests. No reports trusted.

## 1. Layer model (TRD M-01..M-17)
Implemented package tree maps to the TRD layering as follows:

```
contracts/   (DTOs, Protocols, errors, validators)   ── foundation, no logic
schemas/      (dataclasses + JSON schemas + serialization) ── foundation
processing/   (ingestion, extraction, segmentation, evidence,
               detection/{base,registry,runner,3 detectors},
               scoring, evaluation, explanation, reporting, benchmark) ── domain layer
orchestration/(pipeline, workflow)                   ── orchestration layer
benchmark/    (generator, runner, evaluation)        ── benchmark layer
cli.py        (entry)                                 ── interface layer
```

## 2. Dependency-direction validation
- `orchestration/pipeline.py` imports engines **via Protocols** (`IIngestionEngine`, `IExtractionEngine`, … `IEvaluationEngine`) from `contracts/interfaces.py` — **correct inversion of dependencies.** Constructor injection of 9 engines. This is the strongest architectural property in the codebase.
- `processing/*` import only from `schemas` and `contracts` (e.g. `segmentation.py` imports `..schemas.models`, `miie.contracts.errors`). No `processing` module imports `cli` or `api`. ✓ Day 2 boundary rule held.
- `architecture/` tests (layer dependencies, no circular imports, package structure): **8/8 PASS** → dependency rules are enforced and green at runtime.

## 3. Architectural defects

| # | Defect | Severity | Evidence |
|---|---|---|---|
| A1 | **Duplicate parallel package layout** — empty top-level `benchmark/`, `reporting/`, `detection/`, `interface/`, `storage/`, `common/` coexist with `processing/{benchmark,reporting,detection}` | High | `src/miie/{benchmark,reporting,detection,interface,storage,common}/__init__.py` all empty; real impls under `processing/` |
| A2 | **Scratch files in production source** | Medium | `contracts/interfaces_clean.py`, `contracts/interfaces_clean2.py`, `schemas/models_temp.py` |
| A3 | **Test file inside source tree** | Medium | `src/miie/validation/test_validation_service.py` (collected as test, `PytestReturnNotNoneWarning`) |
| A4 | **Two `interfaces` definitions** | Medium | `contracts/interfaces.py` + `interfaces_clean*.py` — ambiguous which is canonical |
| A5 | **Renamed Day-2 architecture tests** | Low | Plan required `tests/unit/test_imports.py`, `test_architecture_boundaries.py`; actual `tests/architecture/test_{layer_dependencies,no_circular_imports,package_structure}.py` |
| A6 | **Day-4 DTO split incomplete** | Medium | Plan required `contracts/{requests,responses}.py`; absent (DTOs only in `dataclasses.py`) |
| A7 | **`src.miie` import style mixed** | Low | Some modules use `from src.miie...` (e.g. `correlation_breakdown_detector.py:7`, `scoring/engine.py:8`), others relative `..schemas` — inconsistent but functional |
| A8 | **Root-level scratch tests pollute collection** | Medium | 9 collection errors from `error_contracts_test.py`, `test_analysis_pipeline.py`, `test_error.py`, `test_first_part_2.py`, `test_gen.py`, `reproducibility_test*.py` |

## 4. Contract / Protocol coverage
Protocols defined for: Ingestion, Extraction, Segmentation, Detector, Scoring, Evidence, Explanation, Report, Benchmark, Evaluation (10). All wired through `AnalysisPipeline.__init__`. ✓ Matches ACS INT-03..INT-10 expectations.

## 5. Module maturity matrix (TRD M-IDs)

| Module | Status | Evidence |
|---|---|---|
| M-01 Repository Ingestion | ✅ real | `ingestion.py` 340 lines, git subprocess |
| M-02 Metric Extraction | ✅ real (partial) | `extraction.py` M-02 + M-06 only (per plan) |
| M-03 Window Segmentation | ⚠️ partial | `segmentation.py` framework present, time strategy = single window |
| M-05 Detector Framework | ✅ framework / ⚠️ algos | framework real; D-02 algo present but failing (corr≈0) |
| M-08 Scoring | ❌ broken | NameError bugs + wrong f₁ proxy |
| M-09 Evidence | ❌ broken | non-deterministic; no per-item traceability |
| M-09 Report Generator | ⚠️ framework | templates + engine present, runtime tests fail |
| M-06 Benchmark Runner | ✅ framework | runner + tests pass |
| M-07 Evaluation Engine | ✅ framework | evaluation + tests pass |
| M-17 Workflow Engine | ⚠️ partial | dispatcher exists, workflow tests fail / can't import |
| M-10 CLI | ❌ stub | 14 lines, version only |
| M-04 Ground Truth | ❌ missing | no `ground_truth.py` |

## 6. Verdict
Architecture status: **PARTIAL.** Core layering and Protocol-based dependency inversion are sound and enforced by passing architecture tests. However the implementation is undermined by a duplicate-package refactor (A1), scratch files (A2/A3), missing DTO split (A6), and several modules that are architecturally present but runtime-broken (M-08, M-09, M-10).

## State
```
architecture_verified = true   (outcome: PARTIAL)
```
