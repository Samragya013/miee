# CRITICAL_INVESTIGATION_BASELINE.md

**Date:** 2026-06-25
**Commit:** 8c0862e
**Branch:** autoresearch/miie/validation

---

## Baseline Configuration

| Parameter | Value |
|-----------|-------|
| MIIE Version | 1.0.0 |
| Default Strategy | time |
| Default Window Size | 7 |
| Default Metrics | M-02, M-06 |
| Default Detectors | D-01, D-02, D-03 |
| Default Format | json |
| Test Suite | 911 passed, 4 skipped, 0 failed |

---

## Baseline Output — Default Mode

**Command:** `python -m miie analyze <repo> --format json`

- Windows: **1** (time, size=7)
- Confidence: **Low** (sample factor: 0.02)
- Integrity: **Very High**
- Risk: **Very Low**
- Detectors: All PASS

---

## Baseline Output — Verbose Mode

**Command:** `python -m miie analyze <repo> --verbose --format json`

- Windows: **1** (time, size=7)
- Confidence: **Low** (sample factor: 0.02)
- Integrity: **Very High**
- Risk: **Very Low**
- Stage Timing: Total 0.54s
- Detectors: [D-01] PASS, [D-02] PASS, [D-03] PASS

---

## Baseline Output — Commit Strategy

**Command:** `python -m miie analyze <repo> -w commit -s 20 --verbose`

- Windows: **12** (commit, size=20)
- Confidence: **Low** (sample factor: 0.02)
- Integrity: **Very High**
- Risk: **Very Low**
- Stage Timing: Total 0.55s
- Detectors: [D-01] PASS, [D-02] PASS, [D-03] PASS

---

## Baseline Output — Forensic Mode

**Command:** `python -m miie analyze <repo> --forensic --format json`

- Windows: **1** (time, size=7)
- Includes: Window details, raw detector outputs, repository metadata

---

## Key Observations

1. Default time strategy produces **1 window** regardless of repo size
2. Commit strategy with size=20 produces **12 windows** for 137-commit repo
3. **Both** report Confidence = Low with sample factor = 0.02
4. Sample factor appears **constant** regardless of window count
5. Flask (5539 commits) with commit strategy was blocked by window_id pattern (now fixed)

---

## Files Captured

- `output/baseline_default.txt` — Default CLI output
- `output/baseline_verbose.txt` — Verbose CLI output
- `output/baseline_commit.txt` — Commit strategy output
- `output/baseline_tests.txt` — Full test suite results
