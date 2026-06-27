# RACA Phase 2 — Directory Responsibility Report

**Program**: MIIE v1.0 Repository Architecture Cohesion Audit
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Category | Count |
|---|---|
| Production | 15 |
| Documentation | 11 |
| Research | 3 |
| Benchmark | 1 |
| Packaging | 1 |
| Runtime | 1 |
| Archive | 1 |
| Temporary | 3 |

---

## Directory Responsibility Analysis

### Production Directories

| Directory | Purpose | Files |
|---|---|---|
| src/miie/ | Main package | 70 |
| src/miie/api/ | FastAPI server | 4 |
| src/miie/benchmark/ | Benchmark execution | 3 |
| src/miie/config/ | Configuration | 2 |
| src/miie/contracts/ | Data contracts | 4 |
| src/miie/orchestration/ | Pipeline orchestration | 3 |
| src/miie/processing/ | Core processing | 1 |
| src/miie/processing/detection/ | 3 detectors | 8 |
| src/miie/processing/evaluation/ | Evaluation engine | 2 |
| src/miie/processing/explanation/ | Explanation engine | 3 |
| src/miie/processing/reporting/ | Report generation | 2 |
| src/miie/processing/scoring/ | Scoring engine | 3 |
| src/miie/schemas/ | Data models | 7 |
| src/miie/utils/ | Utilities | 4 |
| src/miie/validation/ | Validation service | 2 |

### Documentation Directories

| Directory | Purpose | Files |
|---|---|---|
| docs/adr/ | Architecture decisions | — |
| docs/architecture/ | Architecture docs | — |
| docs/audits/ | Audit reports | — |
| docs/authorities/ | Authority documents | 13 |
| docs/contracts/ | Contract docs | — |
| docs/execution/ | Execution reports | — |
| docs/governance/ | Release & FUC reports | 39 |
| docs/paper/ | Research paper | — |
| docs/prompts/ | Agent prompts | — |
| docs/reports/ | Audit & progress reports | — |
| docs/research/ | Research materials | — |

### Research Directories

| Directory | Purpose | Files |
|---|---|---|
| docs/paper/ | Research paper | — |
| docs/research/ | Research materials | — |
| docs/prompts/ | Agent prompts | — |

### Benchmark Directories

| Directory | Purpose | Files |
|---|---|---|
| benchmarks/ | Benchmark data | 3,962 |

### Packaging Directories

| Directory | Purpose | Files |
|---|---|---|
| scripts/ | Utility scripts | 16 |

### Runtime Directories

| Directory | Purpose | Files |
|---|---|---|
| output/ | Runtime outputs | 84 |

### Archive Directories

| Directory | Purpose | Files |
|---|---|---|
| archive/ | Historical | 153 |

### Temporary Directories

| Directory | Purpose | Files |
|---|---|---|
| tmp_output/ | Temp outputs | 2 |
| tmp_output_ingestion/ | Temp outputs | 2 |
| tmp_output_ingestion2/ | Temp outputs | 2 |

---

## Verdict

**RESPONSIBILITY ANALYSIS: COMPLETE**

All directories classified. No unknown categories.

---

*Responsibility analysis completed 2026-06-26*
