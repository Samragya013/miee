# Repository Boundary Report — PR-1A

**Date:** 2026-06-29
**Author:** Principal Software Architect
**Scope:** Repository tooling stabilization for MIIE v1.5

---

## Executive Summary

This report classifies every top-level directory in the MIIE repository into its role, defines the official production source tree, and establishes boundaries for tooling participation.

**Result:** The repository now has explicit boundaries. All production source code passes black, isort, flake8, mypy, and pytest. Non-production directories are excluded from tooling and documented.

---

## 1. Top-Level Directory Classification

| Directory | Classification | Tooling Participation | Justification |
|---|---|---|---|
| `src/` | **Production Source** | Full | Core library — all production code lives here |
| `tests/` | **Production Tests** | Full | Test suite — 1010 tests, all passing |
| `benchmarks/` | **Benchmark Assets** | None | Static datasets, ground truth files, benchmark results — not Python source |
| `docs/` | **Documentation** | None | Architecture specs, governance docs, phase reports — Markdown only |
| `scripts/` | **Developer Utilities** | None | Legacy utility scripts — not part of production pipeline |
| `archive/` | **Archive** | None | Historical outputs, debug artifacts, experimental results — gitignored content |
| `.github/` | **CI Workflows** | None | GitHub Actions CI definition — YAML only |
| `.claude/` | **Temporary** | None | AI agent session config — gitignored |
| `.mypy_cache/` | **Generated Artifact** | None | mypy cache — gitignored |
| `.pytest_cache/` | **Generated Artifact** | None | pytest cache — gitignored |
| `output/` | **Generated Artifacts** | None | Runtime output directory — gitignored |
| `tmp_output/` | **Temporary** | None | Temporary output — gitignored |
| `tmp_output_ingestion/` | **Temporary** | None | Temporary output — gitignored |
| `tmp_output_ingestion2/` | **Temporary** | None | Temporary output — gitignored |

---

## 2. Production Source Tree

The supported production repository consists of:

```
src/miie/              — 62 Python files (production library)
tests/                 — 77 Python files (test suite)
benchmarks/            — Benchmark datasets and ground truth
docs/                  — Architecture documentation
scripts/               — Developer utilities (excluded from tooling)
```

### Source Tree Breakdown

| Package | Files | Status |
|---|---|---|
| `src/miie/api/` | 3 | Production |
| `src/miie/benchmark/` | 4 | Production |
| `src/miie/cli.py` | 1 | Production |
| `src/miie/config/` | 1 | Production |
| `src/miie/contracts/` | 4 | Production |
| `src/miie/orchestration/` | 1 | Production |
| `src/miie/processing/` | 13 | Production |
| `src/miie/processing/detection/` | 8 | Production |
| `src/miie/processing/observation/` | 3 | **NEW — v1.5** |
| `src/miie/processing/scoring/` | 2 | Production |
| `src/miie/processing/explanation/` | 2 | Production |
| `src/miie/processing/reporting/` | 1 | Production |
| `src/miie/processing/benchmark/` | 1 | Production |
| `src/miie/processing/evaluation/` | 1 | Production |
| `src/miie/reporting/` | 1 | Production |
| `src/miie/schemas/` | 8 | Production |
| `src/miie/storage/` | 1 | Reserved (v2.0) |
| `src/miie/utils/` | 3 | Production |
| `src/miie/validation/` | 1 | Production |

**Total: 62 production Python files, 77 test files**

---

## 3. Excluded Directories Detail

### `archive/` — Archive
Contains historical analysis outputs, debug test repos, experimental results from CI debugging, and legacy scripts. 130+ files. All gitignored under `archive/*` patterns. No tooling participation.

### `scripts/` — Developer Utilities
Contains 16 legacy utility scripts (analyze_tests.py, debug_git.py, error_contracts_test.py, etc.). These are one-off development/debugging tools not part of the production pipeline. Excluded from tooling to avoid false positives from experimental code.

### `output/`, `tmp_output/`, `tmp_output_ingestion/`, `tmp_output_ingestion2/` — Generated Artifacts
Runtime output directories created by CLI execution. All gitignored. No tooling participation.

### `.claude/` — Temporary
AI agent session configuration. Gitignored. No tooling participation.

### `.mypy_cache/`, `.pytest_cache/` — Generated Artifacts
Tool caches. Gitignored. No tooling participation.

---

## 4. Boundary Enforcement

Tooling is configured to operate only on the production source tree:

- **black**: `src/ tests/`
- **isort**: `src/ tests/`
- **flake8**: `src/ tests/`
- **mypy**: `src/miie/`
- **pytest**: `tests/`

Non-production directories (`archive/`, `scripts/`, `output/`, etc.) are explicitly outside these paths and do not participate in quality gates.
