# Phase 3 — Root Cause Classification

**Date**: 2026-06-27

## Root Cause Register

| ID | Category | Description | Affected Jobs | Severity | Status |
|----|----------|-------------|---------------|----------|--------|
| RC-001 | B — Dependency | poetry.lock stale after pyproject.toml modification | unit-tests, integration-tests, regression, detector-regression | Critical | FIXED |

## Category Mapping

- **B — Dependency**: poetry.lock file does not match pyproject.toml
  - Root cause: pyproject.toml modified (added `[tool.black]` and `[tool.isort]` sections) without running `poetry lock`
  - Evidence: `poetry install` fails with "pyproject.toml changed significantly since poetry.lock was last generated"
  - Fix: `poetry lock` regenerates the lock file

## Excluded Categories

| Category | Reason for Exclusion |
|----------|---------------------|
| A — Packaging | pyproject.toml is valid, package installs correctly |
| C — GitHub Actions Workflow | Workflow YAML is correct for Ubuntu runners |
| D — Python Version Compatibility | All 3 Python versions (3.10, 3.11, 3.12) work |
| E — Test Infrastructure | pytest discovers and runs all tests correctly |
| F — Integration Environment | No external services required |
| G — Regression Harness | All regression tests pass when dependencies installed |
| H — Detector Regression Harness | grep command works on Ubuntu (CI runner) |
| I — Repository Layout | No path issues |
| J — External Service | No external API calls |
| K — Unknown | Root cause identified |

## Conclusion

**Minimum root causes**: 1 (RC-001)

**All 4 failing jobs** trace back to the same dependency resolution failure.
