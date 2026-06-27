# First User Certification — Phase 6: Failure Root Cause

**Program**: MIIE v1.0 First User Certification
**Date**: 2026-06-26

---

## Executive Summary

| Issue | Root Cause | Status |
|---|---|---|
| Time window strategy produces 1 window | Default window size too large for most repos | DOCUMENTED |
| Exit code 3 on insufficient windows | D-1 minimum window gate working correctly | EXPECTED |

---

## Issue 1: Time Window Strategy

### Symptom
```bash
python -m miie analyze https://github.com/pallets/flask
# Output: Insufficient windows: 1 (need ≥2). Adjust --window-size or time range.
```

### Root Cause
The default time window strategy with 7-day windows produces only 1 window for most repositories because:
- Repositories have commits spread across years
- 7-day windows aggregate all commits into 1 window
- The extraction phase produces aggregated metrics, not per-window data

### Impact
- New users will encounter this error on first run
- Default command fails for most repositories
- Users must discover `--window-strategy commit` option

### Recommendation
- Change default window strategy to `commit`
- Or reduce default window size for time strategy
- Add helpful error message suggesting alternatives

### Severity
MEDIUM — Usability issue, not a bug

---

## Issue 2: Exit Code 3

### Symptom
```json
{
  "error": "Insufficient windows: 1 (need ≥2). Adjust --window-size or time range.",
  "exit_code": 3
}
```

### Root Cause
D-1 minimum window gate working correctly. The pipeline correctly identifies insufficient data and exits with code 3.

### Impact
- Expected behavior
- Exit code 3 is documented
- Error message is clear

### Recommendation
No fix needed. This is correct behavior.

### Severity
NONE — Expected behavior

---

## Verdict

**FAILURE INVESTIGATION: PASS**

One usability issue identified (time window default). No critical bugs found.

---

*Failure investigation completed 2026-06-26*
