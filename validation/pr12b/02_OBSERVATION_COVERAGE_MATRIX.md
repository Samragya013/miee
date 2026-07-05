# 02 — Observation Coverage Matrix

**PR-12B — Scientific Readiness Remediation**

## Metric → Provider → Observation Coverage

| Metric | Required Provider | Available Provider | Observation Source | Coverage Status |
|--------|------------------|-------------------|-------------------|----------------|
| M-01 Entropy Ratio | None (no provider) | — | — | NOT IMPLEMENTED |
| M-02 Commit Count | Git provider | git.observation.v1 | Per-commit observation | ✅ AVAILABLE |
| M-02 Commit Count | GitHub PR provider | github.pr.observation.v1 | Per-PR creation observation | ✅ AVAILABLE (requires API) |
| M-02 Commit Count | Metadata provider | repository.metadata.observation.v1 | Stars/forks/watchers/issues observations | ✅ AVAILABLE (requires API) |
| M-03 Churn Ratio | None (no provider) | — | — | NOT IMPLEMENTED |
| M-04 Test Coverage | None (no provider) | — | — | NOT IMPLEMENTED |
| M-05 Review Latency | GitHub PR provider | github.pr.observation.v1 | Per-PR merge/close latency | ✅ AVAILABLE (requires API) |
| M-05 Review Latency | Metadata provider | repository.metadata.observation.v1 | Last push/update latency | ✅ AVAILABLE (requires API) |
| M-06 File Change Count | Git provider | git.observation.v1 | Per-commit churn observation | ✅ AVAILABLE (PR-12B fix) |
| M-07 Branch Freshness | None (no provider) | — | — | NOT IMPLEMENTED (normalization exists, not wired) |

## Observation Availability by Provider Success

| Scenario | M-01 | M-02 | M-03 | M-04 | M-05 | M-06 | M-07 |
|----------|------|------|------|------|------|------|------|
| Git only (no API) | — | ✅ | — | — | — | ✅ | — |
| Git + GitHub API | — | ✅ | — | — | ✅ | ✅ | — |
| All providers | — | ✅ | — | — | ✅ | ✅ | — |

## Minimum Observation Requirements

| Metric | Min Obs | Aggregation | Source Available | Meets Minimum? |
|--------|---------|-------------|-----------------|---------------|
| M-01 | 1 | mean | No provider | ❌ NO |
| M-02 | 1 | sum | Git (unlimited) | ✅ YES |
| M-03 | 5 | mean | No provider | ❌ NO |
| M-04 | 1 | mean | No provider | ❌ NO |
| M-05 | 2 | mean | GitHub PR (per PR) | ✅ YES (with API) |
| M-06 | 1 | sum | Git (per commit) | ✅ YES (PR-12B fix) |
| M-07 | 1 | mean | No provider | ❌ NO |

## Coverage Summary

- **Metrics with at least one provider:** 3/7 (M-02, M-05, M-06)
- **Metrics without any provider:** 4/7 (M-01, M-03, M-04, M-07)
- **Improvement from PR-12B:** M-06 now accepted by Metric Engine (was silently rejected)
