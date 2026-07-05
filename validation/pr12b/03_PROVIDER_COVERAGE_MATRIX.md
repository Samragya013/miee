# 03 — Provider Coverage Matrix

**PR-12B — Scientific Readiness Remediation**

## Provider Coverage Detail

| Provider | Supported Metrics | Observed Metrics | Coverage | Validation Status | Confidence |
|----------|------------------|-----------------|----------|-------------------|-----------|
| git.observation.v1 | M-02, M-06 | M-02, M-06 | 100% (2/2) | ✅ All units valid | 1.0 |
| github.pr.observation.v1 | M-02, M-05 | M-02, M-05 | 100% (2/2) | ✅ All units valid | 1.0 (authenticated) / 0.0 (rate-limited) |
| repository.metadata.observation.v1 | M-02, M-05 | M-02, M-05 | 100% (2/2) | ✅ All units valid | 1.0 (authenticated) / 0.0 (rate-limited) |

## Provider Auth Status Impact

| Provider | Anonymous Access | Authenticated Access | Rate Limit Impact |
|----------|-----------------|---------------------|-------------------|
| git.observation.v1 | ✅ Full access | N/A (local) | None |
| github.pr.observation.v1 | ⚠️ 60 req/hr | ✅ 5000 req/hr | Exhausted without token |
| repository.metadata.observation.v1 | ⚠️ 60 req/hr | ✅ 5000 req/hr | Exhausted without token |

## PR-12B Authentication Improvements

| Improvement | Before | After |
|------------|--------|-------|
| Token discovery | GITHUB_TOKEN only | GITHUB_TOKEN, GH_TOKEN, GITHUB_PAT |
| Source tracking | "environment" | "env:GITHUB_TOKEN" (specific) |
| Diagnostics | None | auth.diagnostics() dict |
| Human-readable status | None | summarize_auth_status() |
| Token preview | None | Masked (first4...last4) |

## Provider Failure Modes

| Provider | Failure Mode | Error Message | Recovery |
|----------|-------------|---------------|----------|
| git.observation.v1 | Empty repo | "Only N commits (minimum 10)" | N/A |
| github.pr.observation.v1 | Rate limit | "Rate limit exhausted" | Set GITHUB_TOKEN |
| github.pr.observation.v1 | Repo not found | "Repository not found: owner/repo" | Check repo ID |
| repository.metadata.observation.v1 | Rate limit | "Rate limit exhausted" | Set GITHUB_TOKEN |

## Coverage Summary

- **Providers with 100% metric coverage:** 3/3
- **Providers requiring API token for full operation:** 2/3
- **Providers with auth diagnostics:** 3/3 (PR-12B improvement)
