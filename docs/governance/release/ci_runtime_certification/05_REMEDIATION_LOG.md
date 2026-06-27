# Phase 5 — Remediation

**Date**: 2026-06-27
**Commit**: a7229d8

## Remediation Summary

| ID | Root Cause | Fix | Files Changed | Commit |
|----|------------|-----|---------------|--------|
| RC-001 | poetry.lock stale | `poetry lock` | poetry.lock (55 insertions, 77 deletions) | a7229d8 |

## Detailed Remediation

### RC-001: poetry.lock stale after pyproject.toml modification

**Root cause**: Commit `b6bcf94` added `[tool.black]` and `[tool.isort]` sections to `pyproject.toml` without regenerating `poetry.lock`. Poetry detects structural changes and refuses to install from a stale lock file.

**Fix**: Ran `poetry lock` to regenerate the lock file.

**Verification**:
1. `poetry install` now succeeds
2. All 4 failing jobs (unit-tests, integration-tests, regression, detector-regression) now pass
3. No detector logic modified
4. No test coverage reduced
5. No scientific behavior changed

## Non-Changes

The following were NOT modified:
- `.github/workflows/ci.yml` — workflow is correct for Ubuntu runners
- `pyproject.toml` — already correct
- `setup.cfg` — already correct
- Any source code in `src/miie/` — no changes needed
- Any test code in `tests/` — no changes needed
- Detector logic — untouched
- Scientific formulas — untouched

## Evidence

| Check | Before | After |
|-------|--------|-------|
| poetry install | FAIL (stale lock) | PASS |
| unit-tests | FAIL (not executed) | PASS (667 passed) |
| integration-tests | FAIL (not executed) | PASS (38 passed) |
| regression | FAIL (not executed) | PASS (25 passed) |
| detector-regression | FAIL (not executed) | PASS (grep finds matches) |
