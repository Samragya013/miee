# 04 — Scientific Readiness Matrix

**PR-12B — Scientific Readiness Remediation**

## Metric → Provider → Observation → Computation → Status

| Metric | Provider | Observation Coverage | Metric Computation | Scientific Status |
|--------|----------|---------------------|-------------------|-------------------|
| M-01 Entropy Ratio | None | 0 observations | Not computed | NOT IMPLEMENTED |
| M-02 Commit Count | git.observation.v1 | Per-commit (unlimited) | Sum aggregation | ✅ READY |
| M-02 Commit Count | github.pr.observation.v1 | Per-PR creation | Sum aggregation | ✅ READY (requires API) |
| M-02 Commit Count | repository.metadata.observation.v1 | Stars/forks/watchers | Sum aggregation | ✅ READY (requires API) |
| M-03 Churn Ratio | None | 0 observations | Depends on M-07 | BLOCKED (no M-07 provider) |
| M-04 Test Coverage | None | 0 observations | Not computed | NOT IMPLEMENTED |
| M-05 Review Latency | github.pr.observation.v1 | Per-PR merge/close | Mean aggregation | ✅ READY (requires API) |
| M-05 Review Latency | repository.metadata.observation.v1 | Last push/update | Mean aggregation | ✅ READY (requires API) |
| M-06 File Change Count | git.observation.v1 | Per-commit churn | Sum aggregation | ✅ READY (PR-12B fix) |
| M-07 Branch Freshness | None (normalization exists) | 0 observations (not wired) | Not computed | NOT IMPLEMENTED |

## Status Definitions

| Status | Definition |
|--------|-----------|
| ✅ READY | Provider exists, observations available, metric engine can compute |
| ⚠️ PARTIAL | Provider exists but observations may be limited (e.g., requires API token) |
| BLOCKED | Metric depends on another metric that is not available |
| NOT IMPLEMENTED | No provider exists for this metric |

## Dependency Graph

```
M-01 (Entropy Ratio)     → No provider
M-02 (Commit Count)      → Git provider ✅
M-03 (Churn Ratio)       → Depends on M-07 → No provider for M-07
M-04 (Test Coverage)     → No provider
M-05 (Review Latency)    → GitHub PR provider ✅ (requires API)
M-06 (File Change Count) → Git provider ✅ (PR-12B fix)
M-07 (Branch Freshness)  → No provider (normalization exists, not wired)
```

## Readiness Summary

| Status | Count | Metrics |
|--------|-------|---------|
| ✅ READY | 3 | M-02, M-05, M-06 |
| ⚠️ PARTIAL | 0 | — |
| BLOCKED | 1 | M-03 (depends on M-07) |
| NOT IMPLEMENTED | 3 | M-01, M-04, M-07 |

## PR-12B Impact

| Before PR-12B | After PR-12B | Change |
|---------------|-------------|--------|
| M-06: silently rejected (unit mismatch) | M-06: accepted and computed | +1 metric READY |
| Auth: single env var | Auth: multi-source discovery | Improved reliability |
| Auth: no diagnostics | Auth: diagnostics + summary | Improved observability |
| Readiness: 2/7 READY | Readiness: 3/7 READY | +1 metric |
