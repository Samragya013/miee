# Phase 2 — Failure Correlation

**Date**: 2026-06-27

## Dependency Graph

```
pyproject.toml modified (b6bcf94)
        │
        ▼
poetry.lock stale (not regenerated)
        │
        ▼
poetry install fails
        │
        ├──▶ unit-tests FAILS (667 tests not executed)
        ├──▶ integration-tests FAILS (38 tests not executed)
        ├──▶ regression FAILS (25 tests not executed)
        └──▶ detector-regression FAILS (grep not executed)
```

## Correlation Analysis

| Failing Job | Shared Root Cause | Independent Root Cause |
|-------------|-------------------|----------------------|
| unit-tests (3.11) | poetry.lock stale | None |
| integration-tests | poetry.lock stale | None |
| regression | poetry.lock stale | None |
| detector-regression | poetry.lock stale | None |

## Cluster Assessment

**All 4 failures belong to the same cluster**: Dependency resolution failure (Category B).

The failures are NOT independent. They all originate from a single root cause:
- pyproject.toml was modified in commit `b6bcf94`
- poetry.lock was not regenerated
- All jobs that depend on `poetry install` fail identically

## Non-Failing Jobs

| Job | Why it passes |
|-----|---------------|
| lint | Uses `pip install` (not poetry) |
| typecheck | Uses `pip install` (not poetry) |
| security | Uses `pip install` (not poetry) |

## Conclusion

**Single root cause**: Stale `poetry.lock` after `pyproject.toml` modification.

**Minimum remediation**: Regenerate `poetry.lock` with `poetry lock`.
