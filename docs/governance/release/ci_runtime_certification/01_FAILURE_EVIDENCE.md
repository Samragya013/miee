# Phase 1 — Complete Failure Evidence

**Date**: 2026-06-27
**Method**: Local simulation of GitHub Actions CI workflows

## Summary

All 4 failing GitHub Actions jobs share a single root cause: `poetry.lock` is stale after `pyproject.toml` was modified in commit `b6bcf94` (added `[tool.black]` and `[tool.isort]` sections).

## Failure Evidence Per Job

### unit-tests (3.11)

| Field | Value |
|-------|-------|
| First failing step | `poetry install` |
| First failing command | `pip install poetry && poetry install` |
| Exact exception | `RuntimeError` |
| Stack trace | N/A (poetry error) |
| Exit code | 1 |
| Failed module | poetry |
| Failed dependency | poetry.lock validation |
| Failed import | N/A |
| Failed assertion | N/A |
| Failed installation | poetry install |
| Failed environment setup | poetry.lock mismatch |

**Error message**:
```
pyproject.toml changed significantly since poetry.lock was last generated.
Run `poetry lock` to fix the lock file.
```

### integration-tests

| Field | Value |
|-------|-------|
| First failing step | `poetry install` |
| Exact exception | Same as unit-tests |
| Exit code | 1 |

### regression

| Field | Value |
|-------|-------|
| First failing step | `poetry install` |
| Exact exception | Same as unit-tests |
| Exit code | 1 |

### detector-regression

| Field | Value |
|-------|-------|
| First failing step | `poetry install` |
| Exact exception | Same as unit-tests |
| Exit code | 1 |

## Root Cause Evidence

1. **pyproject.toml modified**: Commit `b6bcf94` added `[tool.black]` and `[tool.isort]` sections
2. **poetry.lock not regenerated**: The committed lock file was generated before these sections existed
3. **Poetry validation**: Poetry detects structural changes to pyproject.toml and refuses to install from a stale lock file
4. **Reproduction**: `poetry install` with stale lock produces: "pyproject.toml changed significantly since poetry.lock was last generated"
5. **Fix verification**: `poetry lock` regenerates the lock file, then `poetry install` succeeds
