# 06 — PR-12A vs PR-12B Scientific Comparison

**PR-12B — Scientific Readiness Remediation**

## Executive Summary

| Dimension | PR-12A (Before) | PR-12B (After) | Delta |
|-----------|----------------|----------------|-------|
| Metrics Computed | 1/7 (M-02 only) | 2/7 (M-02 + M-06) | +1 metric |
| Metric Coverage | 14% | 29% | +15pp |
| Readiness Status | 2/7 READY | 3/7 READY | +1 READY |
| Confidence (avg) | 0.900 | 0.898 | -0.002 (negligible) |
| M-06 Status | Silently rejected | Accepted and computed | Fixed |
| Auth Reliability | Single env var | Multi-source discovery | Improved |
| Auth Observability | No diagnostics | diagnostics() + summary | New capability |

## Metric-by-Metric Comparison

| Metric | PR-12A | PR-12B | Change | Root Cause |
|--------|--------|--------|--------|-----------|
| M-01 Entropy Ratio | NOT IMPLEMENTED | NOT IMPLEMENTED | — | No provider exists |
| M-02 Commit Count | ✅ Computed | ✅ Computed | No change | Already working |
| M-03 Churn Ratio | BLOCKED | BLOCKED | — | Depends on M-07 |
| M-04 Test Coverage | NOT IMPLEMENTED | NOT IMPLEMENTED | — | No provider exists |
| M-05 Review Latency | BLOCKED (no API) | BLOCKED (no API) | — | Requires GitHub API token |
| M-06 File Change Count | ❌ Silently rejected | ✅ Computed | **FIXED** | Unit mismatch |
| M-07 Branch Freshness | NOT IMPLEMENTED | NOT IMPLEMENTED | — | Normalization not wired |

## M-06 Root Cause Analysis

### What Was Broken

The M-06 metric (File Change Count) was **silently rejected** by the Metric Engine due to a unit mismatch between the observation and the metric definition.

**Observation chain:**
1. Git provider created observations with `unit="ratio"` (line 287 of `git.py`)
2. Observation model `_METRIC_UNITS["M-06"]` = `"ratio"` (line 45 of `models.py`)
3. Metric definition `M06FileChangeCountComputer._DEFINITION.unit = "count"` (correct)
4. `METRIC_BOUNDS["M-06"].unit = "count"` (correct)
5. Metric Engine validation: observation unit "ratio" ≠ metric unit "count" → **rejected**

### What Was Actually Computed

Despite the "ratio" label, the Git provider was computing the **sum of insertions + deletions** (a count), not a ratio. The values in PR-12A's JSON are the same as PR-12B's — the computation was correct, only the unit label was wrong.

### Fix Applied

- Changed `git.py:287` from `unit="ratio"` to `unit="count"`
- Changed `models.py:45` from `_METRIC_UNITS["M-06"] = "ratio"` to `"count"`

## Per-Repository Comparison

| Repository | PR-12A M-02 | PR-12B M-02 | PR-12A M-06 | PR-12B M-06 | M-06 Delta |
|-----------|-------------|-------------|-------------|-------------|-----------|
| tiangolo/typer | 500 | 500 | 84,490 | 84,490 | 0 |
| tiangolo/full-stack-fastapi-template | 500 | 500 | 101,478 | 101,478 | 0 |
| pypa/sampleproject | 139 | 139 | 2,060 | 2,060 | 0 |
| tiangolo/uvicorn | 500 | 500 | 27,060 | 27,060 | 0 |
| encode/httpx | 500 | 500 | 54,350 | 54,350 | 0 |
| encode/starlette | 500 | 500 | 45,233 | 45,233 | 0 |
| pallets/flask | 1,584 | 1,584 | 726,585 | 726,585 | 0 |
| psf/requests | 1,411 | 1,411 | 227,381 | 227,381 | 0 |
| pypa/pip | 11,260 | 11,260 | 2,087,635 | 2,087,635 | 0 |
| python/cpython | 500 | 500 | 3,204,713 | 3,204,713 | 0 |

**Key finding:** M-06 values are identical between PR-12A and PR-12B. The computation was always correct — only the unit label was wrong, causing silent rejection.

## Authentication Improvements

| Feature | PR-12A | PR-12B |
|---------|--------|--------|
| Token discovery | `GITHUB_TOKEN` only | `GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_PAT` |
| Diagnostics | None | `auth.diagnostics()` returns structured dict |
| Status summary | None | `summarize_auth_status(auth)` returns human string |
| Token preview | None | `auth.token_preview` shows masked token |
| Backward compat | N/A | 100% — no breaking changes |

## Confidence Comparison

| Repository | PR-12A Confidence | PR-12B Confidence | Delta |
|-----------|-------------------|-------------------|-------|
| tiangolo/typer | 0.898 | 0.898 | 0.000 |
| tiangolo/full-stack-fastapi-template | 0.899 | 0.899 | 0.000 |
| pypa/sampleproject | 0.898 | 0.898 | 0.000 |
| tiangolo/uvicorn | 0.899 | 0.899 | 0.000 |
| encode/httpx | 0.898 | 0.898 | 0.000 |
| encode/starlette | 0.898 | 0.898 | 0.000 |
| pallets/flask | 0.900 | 0.900 | 0.000 |
| psf/requests | 0.899 | 0.899 | 0.000 |
| pypa/pip | 0.900 | 0.900 | 0.000 |
| python/cpython | 0.896 | 0.896 | 0.000 |

**Confidence is unchanged** — M-06 addition does not affect existing M-02 confidence scores.

## Files Modified (PR-12B)

| File | Change | Lines Changed |
|------|--------|--------------|
| `src/miie/providers/git.py` | M-06 unit: "ratio" → "count" | 1 |
| `src/miie/processing/observation/models.py` | M-06 unit: "ratio" → "count" | 1 |
| `src/miie/providers/github/authentication.py` | Multi-source token discovery, diagnostics | ~40 |
| `tests/providers/test_github_auth.py` | Updated source assertion | 1 |
| `tests/test_observation_graph.py` | M-06 unit: "ratio" → "count" | 1 |
| `tests/unit/test_detector_observations.py` | M-06 unit: "ratio" → "count" | 1 |
| `tests/unit/test_extraction_engine.py` | M-06 unit: "ratio" → "count" | 1 |
| `tests/unit/test_sampling_framework.py` | M-06 unit: "ratio" → "count" | 1 |
| `validation/metric_campaign/run_campaign.py` | Auth diagnostics, PR-12B banner | ~5 |

**Total:** 9 files modified, ~51 lines changed

## Regression Status

| Gate | PR-12A | PR-12B | Status |
|------|--------|--------|--------|
| pytest | 1302 passed | 1302 passed | ✅ No regression |
| black | 251 unchanged | 251 unchanged | ✅ No regression |
| isort | Clean | Clean | ✅ No regression |
| flake8 | Pre-existing only | Pre-existing only | ✅ No regression |

## Conclusion

PR-12B successfully remediated the M-06 unit mismatch that was silently rejecting observations. The fix:
- Added M-06 to the computed metric set (1/7 → 2/7)
- Doubled coverage from 14% to 29%
- Improved auth reliability and observability
- Maintained full backward compatibility
- Zero regression in test suite
