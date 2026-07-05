# Phase 4 — Local Reproduction

**Date**: 2026-06-27
**Method**: Brand-new virtual environment, exact CI commands

## Environment

| Property | Value |
|----------|-------|
| OS | Windows 11 |
| Python | 3.11.9 |
| Poetry | 2.4.1 |
| Virtual env | Fresh (C:\Users\Samragya\AppData\Local\Temp\ci_sim) |

## Reproduction Results

### Step 1: Restore stale poetry.lock (simulating CI checkout)

```bash
git stash -- poetry.lock  # Restore committed (stale) lock file
```

### Step 2: Run `poetry install` (CI command)

```bash
poetry install
```

**Result**: FAILURE
```
pyproject.toml changed significantly since poetry.lock was last generated.
Run `poetry lock` to fix the lock file.
```

### Step 3: Run `poetry lock` (remediation)

```bash
poetry lock
```

**Result**: SUCCESS
```
Resolving dependencies...
Writing lock file
```

### Step 4: Run `poetry install` again

```bash
poetry install
```

**Result**: SUCCESS
```
Installing dependencies from lock file
No dependencies to install or update
Installing the current project: miie (1.0.0)
```

## Test Results After Fix

| Job | Result | Tests | Duration |
|-----|--------|-------|----------|
| unit-tests | PASS | 667 passed | 23.37s |
| integration-tests | PASS | 38 passed | 19.37s |
| regression | PASS | 25 passed | 0.64s |
| detector-regression | PASS | grep finds matches | <1s |
| lint | PASS | 0 errors | <5s |
| typecheck | PASS | 0 errors | <10s |
| CLI smoke | PASS | version 1.0.0 | <1s |

## OS-Specific Behavior

None. The failure is OS-independent — poetry validates pyproject.toml against poetry.lock on all platforms.

## Python-Version-Specific Behavior

None. The failure occurs at the dependency resolution stage, before any Python-version-specific code is executed.

## Conclusion

**Failure reproduced successfully** in a clean virtual environment using exact CI commands.

**Fix verified**: `poetry lock` resolves the issue.
