# 01 — Provider Validation Matrix

**PR-12B — Scientific Readiness Remediation**

## Provider → Metric → Unit Validation

| Provider | Metric | Declared Unit | Expected Unit | Match | Aggregation | Confidence |
|----------|--------|--------------|--------------|-------|-------------|-----------|
| git.observation.v1 | M-02 | count | count | ✅ | sum | 1.0 |
| git.observation.v1 | M-06 | count | count | ✅ (PR-12B fix) | sum | 1.0 |
| github.pr.observation.v1 | M-02 | count | count | ✅ | sum | 1.0 |
| github.pr.observation.v1 | M-05 | hours | hours | ✅ | mean | 1.0 |
| repository.metadata.observation.v1 | M-02 | count | count | ✅ | sum | 1.0 |
| repository.metadata.observation.v1 | M-05 | hours | hours | ✅ | mean | 1.0 |

## Provider Capability Declarations

| Provider | Supported Metrics | Source Types | Requires Network | Requires Token |
|----------|------------------|-------------|-----------------|---------------|
| git.observation.v1 | M-02, M-06 | commit | No | No |
| github.pr.observation.v1 | M-02, M-05 | pull_request, review | Yes | No (improved with token) |
| repository.metadata.observation.v1 | M-02, M-05 | repository | Yes | No (improved with token) |

## Observation Schema Compliance

| Provider | observation_id | source_type | source_id | metric_id | value | unit | timestamp | quality | provenance |
|----------|---------------|-------------|-----------|-----------|-------|------|-----------|---------|-----------|
| git.observation.v1 | ✅ 16-char hex | ✅ "commit" | ✅ 40-char SHA | ✅ M-02/M-06 | ✅ float | ✅ count | ✅ ISO-8601 | ✅ complete | ✅ extractor_id + timestamp |
| github.pr.observation.v1 | ✅ 16-char hex | ✅ "branch" | ✅ pr-{n} | ✅ M-02/M-05 | ✅ float | ✅ count/hours | ✅ ISO-8601 | ✅ complete | ✅ extractor_id + timestamp |
| repository.metadata.observation.v1 | ✅ 16-char hex | ✅ "branch" | ✅ full_name | ✅ M-02/M-05 | ✅ float | ✅ count/hours | ✅ ISO-8601 | ✅ complete | ✅ extractor_id + timestamp |

## PR-12B Remediation Applied

| Finding | Provider | Status | Fix |
|---------|----------|--------|-----|
| M-06 unit="ratio" | git.observation.v1 | ✅ RESOLVED | Changed to unit="count" in git.py:287 |
| M-06 unit="ratio" | observation models | ✅ RESOLVED | Changed to unit="count" in models.py:45 |
| Auth token discovery | GitHubAuth | ✅ RESOLVED | Multi-source env var discovery |
| Auth diagnostics | GitHubAuth | ✅ RESOLVED | Added diagnostics() and summarize_auth_status() |

## Validation Summary

- **Total provider-metric pairs:** 6
- **Unit matches:** 6/6 (100%)
- **Schema compliance:** 3/3 providers (100%)
- **PR-12B fixes applied:** 4
