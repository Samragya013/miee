# Document Classification Matrix — MIIE v1.5.0

**Date:** 2026-07-02
**Auditor:** Information Architecture Engineer

---

## Classification Categories

| Category | Description |
|---|---|
| **Source Code** | Production Python source files |
| **Tests** | Unit, integration, architecture, regression tests |
| **Architecture** | Technical specifications, ADRs, design docs |
| **Scientific Specifications** | OEAS, ODSS, DES, DSVP, IMS, PRD |
| **Implementation Reports** | Day-by-day execution reports |
| **Validation Reports** | Audit, validation, verification reports |
| **Benchmark Reports** | Benchmark evaluation results |
| **Release Engineering** | Release notes, changelogs, migration guides |
| **Generated Data** | CSV, JSON, HTML outputs |
| **Temporary Outputs** | Debug scripts, campaign outputs |
| **Archive** | Historical, experimental, debug files |
| **Developer Scripts** | Utility scripts, debug tools |
| **Configuration** | pyproject.toml, .gitignore, Dockerfile |
| **Documentation** | README, CONTRIBUTING, LICENSE |
| **Assets** | Templates, fixtures |

---

## Classification Matrix

### Source Code (68 files)

| Path | Category | Status |
|---|---|---|
| `src/miie/__init__.py` | Source Code | TRACKED |
| `src/miie/__main__.py` | Source Code | TRACKED |
| `src/miie/cli.py` | Source Code | MODIFIED |
| `src/miie/api/*.py` (4 files) | Source Code | TRACKED |
| `src/miie/benchmark/*.py` (4 files) | Source Code | TRACKED |
| `src/miie/config/*.py` (2 files) | Source Code | TRACKED |
| `src/miie/contracts/*.py` (5 files) | Source Code | TRACKED |
| `src/miie/orchestration/*.py` (3 files) | Source Code | TRACKED |
| `src/miie/processing/*.py` (22 files) | Source Code | TRACKED |
| `src/miie/reporting/*.py` (6 files) | Source Code | TRACKED |
| `src/miie/sampling/*.py` (8 files) | Source Code | UNTRACKED |
| `src/miie/schemas/*.py` (7 files) | Source Code | TRACKED |
| `src/miie/scientific/*.py` (4 files) | Source Code | UNTRACKED |
| `src/miie/storage/*.py` (1 file) | Source Code | TRACKED |
| `src/miie/utils/*.py` (4 files) | Source Code | TRACKED |
| `src/miie/validation/*.py` (1 file) | Source Code | TRACKED |

### Tests (78 files)

| Path | Category | Status |
|---|---|---|
| `tests/unit/*.py` (35 files) | Tests | TRACKED |
| `tests/integration/*.py` (8 files) | Tests | TRACKED |
| `tests/architecture/*.py` (3 files) | Tests | TRACKED |
| `tests/benchmark/*.py` (8 files) | Tests | TRACKED |
| `tests/contract/*.py` (5 files) | Tests | TRACKED |
| `tests/schema/*.py` (6 files) | Tests | TRACKED |
| `tests/performance/*.py` (1 file) | Tests | TRACKED |
| `tests/regression/*.py` (1 file) | Tests | TRACKED |
| `tests/reproducibility/*.py` (1 file) | Tests | TRACKED |
| `tests/workflow/*.py` (2 files) | Tests | TRACKED |
| `tests/unit/test_sampling_framework.py` | Tests | UNTRACKED |

### Architecture (10 files)

| Path | Category | Status |
|---|---|---|
| `docs/adr/ADR-001-project-foundations.md` | Architecture | TRACKED |
| `docs/adr/ADR-002-layered-architecture.md` | Architecture | TRACKED |
| `docs/architecture.md` | Architecture | TRACKED |
| `docs/architecture/RELEASE_BASELINE.md` | Architecture | TRACKED |
| `docs/architecture/dependency_rules.md` | Architecture | TRACKED |
| `docs/architecture/import_policy.md` | Architecture | TRACKED |
| `docs/architecture/module_responsibilities.md` | Architecture | TRACKED |
| `docs/architecture/trd_architecture_mapping.md` | Architecture | TRACKED |

### Scientific Specifications (6 files)

| Path | Category | Status |
|---|---|---|
| `docs/architecture/observation_engine/OEAS_v1.5_Observation_Engine.md` | Scientific Spec | TRACKED |
| `docs/architecture/observation_engine/ODSS_v1.0_Observation_Data_Schema_Specification.md` | Scientific Spec | TRACKED |
| `docs/architecture/detectors/DES_v2.0_Detector_Execution_Specification.md` | Scientific Spec | TRACKED |
| `docs/architecture/detectors/DSVP_v1.0_Detector_Scientific_Validation_Protocol.md` | Scientific Spec | TRACKED |
| `docs/architecture/implementation/IMS_v1.0_Implementation_and_Migration_Specification.md` | Scientific Spec | TRACKED |
| `docs/architecture/observation_engine/PRD_v1.5_Observation_Engine.md` | Scientific Spec | TRACKED |
| `docs/architecture/benchmarking/BES_v1.0_Benchmark_Evolution_Specification.md` | Scientific Spec | TRACKED |

### Implementation Reports (15+ files)

| Path | Category | Status |
|---|---|---|
| `docs/execution/*.md` (5 files) | Implementation Report | TRACKED |
| `docs/execution/completion_reports/*.md` (3 files) | Implementation Report | TRACKED |
| `docs/day_0_completion_checklist.md` | Implementation Report | TRACKED |
| `docs/day_1_execution.md` | Implementation Report | TRACKED |
| `docs/day_2_execution.md` | Implementation Report | TRACKED |
| `docs/day_10_review.md` | Implementation Report | TRACKED |

### Validation Reports (100+ files)

| Path | Category | Status |
|---|---|---|
| `docs/governance/validation/*.md` (40+ files) | Validation Report | TRACKED |
| `docs/governance/audit/*.md` (15+ files) | Validation Report | TRACKED |
| `docs/governance/audits/*.md` (3 files) | Validation Report | TRACKED |
| `docs/governance/release/*.md` (100+ files) | Validation Report | TRACKED |
| `docs/audits/**/*.md` (14 files) | Validation Report | TRACKED |

### Benchmark Reports (4 files)

| Path | Category | Status |
|---|---|---|
| `benchmarks/results/D-01_evaluation.json` | Benchmark Report | TRACKED |
| `benchmarks/results/D-02_evaluation.json` | Benchmark Report | TRACKED |
| `benchmarks/results/D-03_evaluation.json` | Benchmark Report | TRACKED |
| `benchmarks/results/benchmark_summary.json` | Benchmark Report | MODIFIED |

### Release Engineering (12 files)

| Path | Category | Status |
|---|---|---|
| `CHANGELOG.md` | Release Engineering | UNTRACKED |
| `RELEASE_NOTES_v1.5.md` | Release Engineering | UNTRACKED |
| `MIGRATION_GUIDE.md` | Release Engineering | UNTRACKED |
| `KNOWN_LIMITATIONS.md` | Release Engineering | UNTRACKED |
| `VERSION_HISTORY.md` | Release Engineering | UNTRACKED |
| `COMMIT_READINESS_REPORT.md` | Release Engineering | UNTRACKED |
| `RELEASE_READINESS_REPORT.md` | Release Engineering | UNTRACKED |
| `FINAL_RELEASE_CERTIFICATION.md` | Release Engineering | UNTRACKED |
| `DIRECTORY_HEALTH_REPORT.md` | Release Engineering | UNTRACKED |
| `REPOSITORY_STRUCTURE_REPORT.md` | Release Engineering | UNTRACKED |
| `DOCUMENTATION_AUDIT.md` | Release Engineering | UNTRACKED |
| `PACKAGING_REPORT.md` | Release Engineering | UNTRACKED |
| `REPOSITORY_INVENTORY.md` | Release Engineering | UNTRACKED |

### Generated Data (20+ files)

| Path | Category | Status |
|---|---|---|
| `validation/sampling/campaign_detailed.json` | Generated Data | UNTRACKED |
| `validation/sampling/campaign_report.md` | Generated Data | UNTRACKED |
| `validation/sampling/campaign_summary.csv` | Generated Data | UNTRACKED |
| `validation/scientific/*.json` (1 file) | Generated Data | UNTRACKED |
| `validation/scientific/*.csv` (6 files) | Generated Data | UNTRACKED |
| `validation/scientific/*.md` (10 files) | Generated Data | UNTRACKED |

### Temporary Outputs (0 files)

All temporary outputs deleted in PR-8 cleanup.

### Archive (0 files)

Archive directory removed — contained only test repos, debug scripts, and generated outputs.

### Developer Scripts (14 files)

| Path | Category | Status |
|---|---|---|
| `scripts/analyze_tests.py` | Developer Script | TRACKED |
| `scripts/continue_day15.sh` | Developer Script | TRACKED |
| `scripts/debug_git.py` | Developer Script | TRACKED |
| `scripts/debug_init.py` | Developer Script | TRACKED |
| `scripts/error_contracts_test.py` | Developer Script | TRACKED |
| `scripts/error_contracts_test2.py` | Developer Script | TRACKED |
| `scripts/generate_all.py` | Developer Script | TRACKED |
| `scripts/reproducibility_test.py` | Developer Script | TRACKED |
| `scripts/reproducibility_test_reporting.py` | Developer Script | TRACKED |
| `scripts/reproducibility_test_segmentation_scoring.py` | Developer Script | TRACKED |
| `scripts/run_validation_tests` | Developer Script | TRACKED |
| `scripts/test_analysis_pipeline.py` | Developer Script | TRACKED |
| `scripts/test_error.py` | Developer Script | TRACKED |
| `scripts/test_first_part.py` | Developer Script | TRACKED |
| `scripts/test_first_part_2.py` | Developer Script | TRACKED |
| `scripts/test_gen.py` | Developer Script | TRACKED |

### Configuration (8 files)

| Path | Category | Status |
|---|---|---|
| `.gitignore` | Configuration | MODIFIED |
| `.pre-commit-config.yaml` | Configuration | TRACKED |
| `Dockerfile` | Configuration | TRACKED |
| `Makefile` | Configuration | TRACKED |
| `pyproject.toml` | Configuration | MODIFIED |
| `requirements.txt` | Configuration | TRACKED |
| `setup.cfg` | Configuration | TRACKED |
| `.env` | Configuration | TRACKED |
| `.env.example.example` | Configuration | TRACKED |

### Documentation (5 files)

| Path | Category | Status |
|---|---|---|
| `README.md` | Documentation | MODIFIED |
| `CODE_OF_CONDUCT.md` | Documentation | TRACKED |
| `CONTRIBUTING.md` | Documentation | TRACKED |
| `LICENSE` | Documentation | TRACKED |
| `SECURITY.md` | Documentation | TRACKED |

### Assets (4 files)

| Path | Category | Status |
|---|---|---|
| `src/miie/reporting/templates/*.j2` (4 files) | Assets | TRACKED |

---

## Misplacement Analysis

| Issue | Location | Recommended Action |
|---|---|---|
| 12 release engineering docs | Root `/` | Move to `docs/release/` |
| 12 sampling source files | `src/miie/sampling/` | Correct location |
| 4 scientific source files | `src/miie/scientific/` | Correct location |
| 1 test file | `tests/unit/test_sampling_framework.py` | Correct location |
| 20+ validation outputs | `validation/` | Correct location |
| 14 developer scripts | `scripts/` | Correct location |
| Benchmark tmp outputs | `benchmarks/tmp/` | Consider cleanup |
| Benchmark candidate datasets | `benchmarks/datasets/` | Correct location |
| Audit reports mixed with governance | `docs/audits/` | Consider consolidation |
| Day-by-day execution reports | `docs/execution/` | Consider consolidation |

---

## Classification Summary

| Category | Files | Status |
|---|---|---|
| Source Code | 68 | ALL CORRECT |
| Tests | 78 | ALL CORRECT |
| Architecture | 10 | ALL CORRECT |
| Scientific Specifications | 6 | ALL CORRECT |
| Implementation Reports | 15+ | ALL CORRECT |
| Validation Reports | 100+ | ALL CORRECT |
| Benchmark Reports | 4 | ALL CORRECT |
| Release Engineering | 12 | MISPLACED (root) |
| Generated Data | 20+ | ALL CORRECT |
| Archive | 0 | DELETED |
| Developer Scripts | 14 | ALL CORRECT |
| Configuration | 8 | ALL CORRECT |
| Documentation | 5 | ALL CORRECT |
| Assets | 4 | ALL CORRECT |
