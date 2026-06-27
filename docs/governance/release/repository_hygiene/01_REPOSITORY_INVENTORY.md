# Release Engineering — Phase 1: Repository Inventory

**Program**: MIIE v1.0 Release Engineering Program
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Category | Files | Size |
|---|---|---|
| Source (src/) | 70 | Production code |
| Tests (tests/) | 78 | Test suite |
| Documentation (docs/) | 366 | Docs, reports, authority |
| Benchmarks | 3,962 | Ground truth, test data |
| Archive | 153 | Historical outputs |
| Scripts | 16 | Utility scripts |
| Config | 5 | .gitignore, pyproject, etc. |
| Root files | 10 | README, LICENSE, etc. |
| **Total** | **4,660** | — |

---

## Directory Structure

```
MIEE/
├── src/miie/           (70 files) — Production source
├── tests/              (78 files) — Test suite
├── docs/               (366 files) — Documentation
│   ├── authorities/    — 13 authority docs
│   ├── architecture/   — Architecture docs
│   ├── governance/     — Release & FUC reports
│   ├── reports/        — Audit & progress reports
│   ├── paper/          — Research paper
│   ├── prompts/        — Agent prompts
│   └── research/       — Research materials
├── benchmarks/         (3,962 files) — Test data
│   ├── ground_truth/   — Ground truth data
│   └── runners/        — Benchmark runners
├── archive/            (153 files) — Historical
├── scripts/            (16 files) — Utilities
├── .github/            — CI/CD
├── .claude/            — Claude config
└── root files          — README, LICENSE, etc.
```

---

## Source Code Inventory

| Package | Files | Purpose |
|---|---|---|
| src/miie/ | 1 | Main package |
| src/miie/api/ | 4 | FastAPI server |
| src/miie/benchmark/ | 3 | Benchmark execution |
| src/miie/cli.py | 1 | CLI entry point |
| src/miie/common/ | 1 | Common utilities |
| src/miie/config/ | 2 | Configuration |
| src/miie/contracts/ | 4 | Data contracts |
| src/miie/detection/ | 1 | Detection init |
| src/miie/interface/ | 1 | Interface init |
| src/miie/orchestration/ | 3 | Pipeline orchestration |
| src/miie/processing/ | 1 | Processing init |
| src/miie/processing/benchmark/ | 2 | Benchmark engine |
| src/miie/processing/detection/ | 8 | 3 detectors + dispatcher |
| src/miie/processing/evaluation/ | 2 | Evaluation engine |
| src/miie/processing/explanation/ | 3 | Explanation engine |
| src/miie/processing/extraction.py | 1 | Metric extraction |
| src/miie/processing/ingestion.py | 1 | Data ingestion |
| src/miie/processing/reporting/ | 2 | Report generation |
| src/miie/processing/scoring/ | 3 | Scoring engine |
| src/miie/processing/segmentation.py | 1 | Window generation |
| src/miie/reporting/ | 2 | Reporting templates |
| src/miie/schemas/ | 7 | Data models |
| src/miie/storage/ | 1 | Storage init |
| src/miie/utils/ | 4 | Utilities |
| src/miie/validation/ | 2 | Validation service |

---

## Test Inventory

| Directory | Files | Purpose |
|---|---|---|
| tests/unit/ | — | Unit tests |
| tests/schema/ | — | Schema validation |
| tests/contract/ | — | Interface contracts |
| tests/architecture/ | — | Architecture compliance |
| tests/integration/ | — | Integration tests |
| tests/workflow/ | — | End-to-end workflows |
| tests/regression/ | — | Regression tests |
| tests/performance/ | — | Performance tests |
| tests/benchmark/ | — | Benchmark validation |
| tests/reproducibility/ | — | Reproducibility tests |
| tests/api/ | — | API tests |

---

## Documentation Inventory

| Directory | Files | Purpose |
|---|---|---|
| docs/authorities/ | 13 | Authority documents |
| docs/architecture/ | — | Architecture docs |
| docs/governance/release/ | 27 | Release reports |
| docs/governance/first_user_certification/ | 12 | FUC reports |
| docs/reports/ | 100+ | Audit & progress reports |
| docs/paper/ | — | Research paper |
| docs/prompts/ | — | Agent prompts |
| docs/research/ | — | Research materials |
| docs/adr/ | — | Architecture decisions |
| docs/audits/ | — | Audit reports |
| docs/contracts/ | — | Contract docs |
| docs/execution/ | — | Execution reports |

---

## Root Files

| File | Status |
|---|---|
| README.md | EXISTS |
| LICENSE | EXISTS (MIT) |
| CONTRIBUTING.md | EXISTS |
| CODE_OF_CONDUCT.md | EXISTS |
| SECURITY.md | EXISTS |
| MEMORY.md | EXISTS (Claude memory) |
| Makefile | EXISTS |
| Dockerfile | EXISTS |
| pyproject.toml | EXISTS |
| setup.cfg | EXISTS |
| requirements.txt | EXISTS |
| poetry.lock | EXISTS |
| .gitignore | EXISTS |
| .pre-commit-config.yaml | EXISTS |
| .env | EXISTS (git-ignored) |
| .env.example | EXISTS |

---

## Verdict

**INVENTORY: COMPLETE**

4,660 files inventoried across 15 directories. Repository structure is well-organized.

---

*Inventory completed 2026-06-26*
