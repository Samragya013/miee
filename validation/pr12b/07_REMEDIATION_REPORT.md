# 07 — Remediation Report

**PR-12B — Scientific Readiness Remediation**

## Remediation Summary

| ID | Finding | Severity | Status | Resolution |
|----|---------|----------|--------|-----------|
| P0 | M-06 unit="ratio" in Git provider | Critical | ✅ RESOLVED | Changed to unit="count" |
| P0 | M-06 unit="ratio" in Observation model | Critical | ✅ RESOLVED | Changed to unit="count" |
| P1 | Auth: single env var (GITHUB_TOKEN only) | Environment | ✅ RESOLVED | Multi-source discovery |
| P1 | Auth: no diagnostics | Environment | ✅ RESOLVED | Added diagnostics() |
| P2 | M-01, M-03, M-04, M-07 no providers | Architectural | DOCUMENTED | Not in scope for PR-12B |

## Files Modified

| File | Change | Lines Changed |
|------|--------|--------------|
| `src/miie/providers/git.py` | M-06 unit: "ratio" → "count" | 1 line |
| `src/miie/processing/observation/models.py` | M-06 unit: "ratio" → "count" | 1 line |
| `src/miie/providers/github/authentication.py` | Multi-source token discovery, diagnostics | ~40 lines added |
| `tests/providers/test_github_auth.py` | Updated source assertion | 1 line |
| `tests/test_observation_graph.py` | M-06 unit: "ratio" → "count" | 1 line |
| `tests/unit/test_detector_observations.py` | M-06 unit: "ratio" → "count" | 1 line |
| `tests/unit/test_extraction_engine.py` | M-06 unit: "ratio" → "count" | 1 line |
| `tests/unit/test_sampling_framework.py` | M-06 unit: "ratio" → "count" | 1 line |
| `validation/metric_campaign/run_campaign.py` | Auth diagnostics, PR-12B banner | ~5 lines |

## Root Cause Analysis

### P0: M-06 Unit Mismatch

**Timeline:**
1. M-06 metric definition created with `unit="count"` (correct)
2. METRIC_BOUNDS defined with `unit="count"` (correct)
3. Git provider created M-06 observations with `unit="ratio"` (incorrect)
4. Observation model `_METRIC_UNITS` defined M-06 as `"ratio"` (incorrect)
5. Metric Engine validation silently rejected M-06 observations

**Root cause:** The Git provider was designed to measure "churn ratio" (lines changed / total lines) but the metric definition counts "file change count" (sum of insertions + deletions). The implementation actually computes the sum (count), but the unit label was set to "ratio" by mistake.

**Fix:** Changed both the provider and the model mapping to use `unit="count"`.

### P1: Authentication Limitations

**Root cause:** The original `GitHubAuth` only checked `GITHUB_TOKEN`. Many CI/CD systems use `GH_TOKEN` (GitHub CLI) or custom variable names.

**Fix:** Added multi-source discovery with `_TOKEN_ENV_VARS` tuple and `diagnostics()` method.

## Validation

- All 1302 tests pass (excluding pre-existing `test_cli_usability.py` error)
- M-06 observations now pass Observation model validation
- M-06 observations now accepted by Metric Engine
- Auth diagnostics produce structured output
- Backward compatibility maintained
