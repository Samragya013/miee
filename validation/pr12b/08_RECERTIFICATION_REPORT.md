# 08 — Re-Certification Report

**PR-12B — Scientific Readiness Remediation**

## Campaign Summary

| Field | Value |
|-------|-------|
| Campaign Date | 2026-07-03 |
| PR-12B Version | 1.0 |
| Total Repositories | 10 |
| Successful | 10 |
| Failed | 0 |
| Success Rate | 100% |
| Metrics Computed | 2/7 (M-02 + M-06) |
| Coverage | 29% |
| Overall Verdict | MINIMAL |

## Per-Repository Results

### tiangolo/typer (small)
| Metric | Value | Unit | Confidence | Obs Count | Status |
|--------|-------|------|-----------|-----------|--------|
| M-02 | 500.0 | count | 0.900 | 500 | ✅ |
| M-06 | 84,490.0 | count | 0.896 | 500 | ✅ |
| **Overall** | | | **0.898** | 1000 | 🥉 MINIMAL |

### tiangolo/full-stack-fastapi-template (small)
| Metric | Value | Unit | Confidence | Obs Count | Status |
|--------|-------|------|-----------|-----------|--------|
| M-02 | 500.0 | count | 0.900 | 500 | ✅ |
| M-06 | 101,478.0 | count | 0.897 | 500 | ✅ |
| **Overall** | | | **0.899** | 1000 | 🥉 MINIMAL |

### pypa/sampleproject (small)
| Metric | Value | Unit | Confidence | Obs Count | Status |
|--------|-------|------|-----------|-----------|--------|
| M-02 | 139.0 | count | 0.900 | 139 | ✅ |
| M-06 | 2,060.0 | count | 0.897 | 139 | ✅ |
| **Overall** | | | **0.898** | 278 | 🥉 MINIMAL |

### tiangolo/uvicorn (medium)
| Metric | Value | Unit | Confidence | Obs Count | Status |
|--------|-------|------|-----------|-----------|--------|
| M-02 | 500.0 | count | 0.900 | 500 | ✅ |
| M-06 | 27,060.0 | count | 0.897 | 500 | ✅ |
| **Overall** | | | **0.899** | 1000 | 🥉 MINIMAL |

### encode/httpx (medium)
| Metric | Value | Unit | Confidence | Obs Count | Status |
|--------|-------|------|-----------|-----------|--------|
| M-02 | 500.0 | count | 0.900 | 500 | ✅ |
| M-06 | 54,350.0 | count | 0.896 | 500 | ✅ |
| **Overall** | | | **0.898** | 1000 | 🥉 MINIMAL |

### encode/starlette (medium)
| Metric | Value | Unit | Confidence | Obs Count | Status |
|--------|-------|------|-----------|-----------|--------|
| M-02 | 500.0 | count | 0.900 | 500 | ✅ |
| M-06 | 45,233.0 | count | 0.896 | 500 | ✅ |
| **Overall** | | | **0.898** | 1000 | 🥉 MINIMAL |

### pallets/flask (large)
| Metric | Value | Unit | Confidence | Obs Count | Status |
|--------|-------|------|-----------|-----------|--------|
| M-02 | 1,584.0 | count | 0.900 | 1584 | ✅ |
| M-06 | 726,585.0 | count | 0.899 | 1584 | ✅ |
| **Overall** | | | **0.900** | 3168 | 🥉 MINIMAL |

### psf/requests (large)
| Metric | Value | Unit | Confidence | Obs Count | Status |
|--------|-------|------|-----------|-----------|--------|
| M-02 | 1,411.0 | count | 0.900 | 1411 | ✅ |
| M-06 | 227,381.0 | count | 0.898 | 1411 | ✅ |
| **Overall** | | | **0.899** | 2822 | 🥉 MINIMAL |

### pypa/pip (archived)
| Metric | Value | Unit | Confidence | Obs Count | Status |
|--------|-------|------|-----------|-----------|--------|
| M-02 | 11,260.0 | count | 0.900 | 11260 | ✅ |
| M-06 | 2,087,635.0 | count | 0.900 | 11260 | ✅ |
| **Overall** | | | **0.900** | 22520 | 🥉 MINIMAL |

### python/cpython (experimental)
| Metric | Value | Unit | Confidence | Obs Count | Status |
|--------|-------|------|-----------|-----------|--------|
| M-02 | 500.0 | count | 0.900 | 500 | ✅ |
| M-06 | 3,204,713.0 | count | 0.891 | 500 | ✅ |
| **Overall** | | | **0.896** | 1000 | 🥉 MINIMAL |

## Verdict Summary

| Verdict | Count | Repositories |
|---------|-------|-------------|
| 🥇 Certified | 0 | — |
| 🥈 Partial | 0 | — |
| 🥉 Minimal | 10 | All |
| ❌ Failed | 0 | — |

## What Would Improve the Verdict

To reach **🥈 Partial** (4/7 metrics):
1. **M-05 Review Latency** — Requires GitHub API token (set `GITHUB_TOKEN` env var)
2. **M-01 Entropy Ratio** — Requires new provider implementation
3. **M-07 Branch Freshness** — Requires wiring existing normalization to observation pipeline

To reach **🥇 Certified** (7/7 metrics):
1. All of the above, plus
2. **M-03 Churn Ratio** — Requires M-07 provider (dependency)
3. **M-04 Test Coverage** — Requires new provider (CI/CD integration)
