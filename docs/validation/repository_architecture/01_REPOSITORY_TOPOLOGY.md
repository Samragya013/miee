# RACA Phase 1 — Repository Topology

**Program**: MIIE v1.0 Repository Architecture Cohesion Audit
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Category | Count |
|---|---|
| Top-level directories | 12 |
| Source packages | 15 |
| Test categories | 12 |
| Documentation categories | 11 |
| Total files | 4,955 |

---

## Top-Level Structure

```
MIEE/
├── src/miie/           (70 files) — Production source
├── tests/              (78 files) — Test suite
├── docs/               (405 files) — Documentation
├── benchmarks/         (3,962 files) — Benchmark data
├── archive/            (153 files) — Historical
├── scripts/            (16 files) — Utilities
├── output/             (84 files) — Runtime outputs
├── .github/            — CI/CD
├── .claude/            — Claude config
├── .pytest_cache/      — Test cache
├── tmp_output/         — Temp outputs
├── tmp_output_ingestion/ — Temp outputs
└── tmp_output_ingestion2/ — Temp outputs
```

---

## Source Package Structure

```
src/miie/
├── api/                — FastAPI server
├── benchmark/          — Benchmark execution
├── cli.py              — CLI entry point
├── common/             — Common utilities
├── config/             — Configuration
├── contracts/          — Data contracts
├── detection/          — Detection init
├── interface/          — Interface init
├── orchestration/      — Pipeline orchestration
├── processing/         — Core processing
│   ├── benchmark/      — Benchmark engine
│   ├── detection/      — 3 detectors
│   ├── evaluation/     — Evaluation engine
│   ├── explanation/    — Explanation engine
│   ├── extraction.py   — Metric extraction
│   ├── ingestion.py    — Data ingestion
│   ├── reporting/      — Report generation
│   ├── scoring/        — Scoring engine
│   └── segmentation.py — Window generation
├── reporting/          — Reporting templates
├── schemas/            — Data models
├── storage/            — Storage init
├── utils/              — Utilities
└── validation/         — Validation service
```

---

## Test Structure

```
tests/
├── api/                — API tests
├── architecture/       — Architecture compliance
├── benchmark/          — Benchmark validation
├── contract/           — Interface contracts
├── fixtures/           — Test fixtures
├── integration/        — Integration tests
├── performance/        — Performance tests
├── regression/         — Regression tests
├── reproducibility/    — Reproducibility tests
├── schema/             — Schema validation
├── unit/               — Unit tests
└── workflow/           — End-to-end workflows
```

---

## Documentation Structure

```
docs/
├── adr/                — Architecture decisions
├── architecture/       — Architecture docs
├── audits/             — Audit reports
├── authorities/        — Authority documents
├── contracts/          — Contract docs
├── execution/          — Execution reports
├── governance/         — Release & FUC reports
├── paper/              — Research paper
├── prompts/            — Agent prompts
├── reports/            — Audit & progress reports
└── research/           — Research materials
```

---

## Verdict

**REPOSITORY TOPOLOGY: COMPLETE**

12 top-level directories, 15 source packages, 12 test categories, 11 documentation categories.

---

*Repository topology completed 2026-06-26*
