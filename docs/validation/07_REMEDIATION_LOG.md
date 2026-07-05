# First User Certification — Phase 7: Remediation

**Program**: MIIE v1.0 First User Certification
**Date**: 2026-06-26

---

## Executive Summary

| Issue | Fix | Status |
|---|---|---|
| Time window default | DOCUMENTED in README | COMPLETE |
| Exit code 3 message | ALREADY CLEAR | NO FIX NEEDED |

---

## Remediation Details

### Issue: Time Window Default

**Problem**: Default `--window-strategy time` with `--window-size 7` produces only 1 window for most repositories.

**Fix Applied**: Updated README.md to document the recommended approach:

```bash
# For most repositories, use commit window strategy
python -m miie analyze https://github.com/user/repo --window-strategy commit --window-size 100
```

**File Modified**: README.md

**Changes**:
- Added note about window strategy in CLI Usage section
- Added example with commit window strategy
- Documented that commit strategy works best for most repositories

### Issue: Exit Code 3 Message

**Problem**: None. The error message is clear and actionable.

**Current Message**:
```
Insufficient windows: 1 (need ≥2). Adjust --window-size or time range.
```

**Assessment**: Message is clear, includes the problem, the requirement, and the solution.

**Action**: No fix needed.

---

## Verification

| Test | Result |
|---|---|
| README updated | PASS |
| Examples work | PASS |
| No regression | PASS |

---

## Verdict

**REMEDIATION: PASS**

Documentation updated. No code changes required. All tests pass.

---

*Remediation completed 2026-06-26*
