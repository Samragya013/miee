# 07 — Range Analysis
## Per-Metric Value Distribution

### M-01 — Commit Entropy Ratio
- Unit: ratio
- Expected range: [0.0, 1.0]
- Aggregation: mean

| Repository | Value |
|-----------|-------|
| `tiangolo/typer` | 0.0 |
| `tiangolo/full-stack-fastapi-template` | 0.0 |
| `pypa/sampleproject` | 0.33547986458912915 |
| `tiangolo/uvicorn` | 0.260564207076941 |
| `encode/httpx` | 0.2360586869533947 |
| `encode/starlette` | 0.39100477382493365 |
| `pallets/flask` | 0.30603378492641403 |
| `psf/requests` | 0.2165354773957376 |
| `pypa/pip` | 0.2119920263519558 |
| `python/cpython` | 0.16299975545164558 |

- Min: 0.0
- Max: 0.39100477382493365
- Mean: 0.2121

### M-02 — Commit Count
- Unit: count
- Expected range: [0.0, inf]
- Aggregation: sum

| Repository | Value |
|-----------|-------|
| `tiangolo/typer` | 500.0 |
| `tiangolo/full-stack-fastapi-template` | 500.0 |
| `pypa/sampleproject` | 139.0 |
| `tiangolo/uvicorn` | 500.0 |
| `encode/httpx` | 500.0 |
| `encode/starlette` | 500.0 |
| `pallets/flask` | 1584.0 |
| `psf/requests` | 1411.0 |
| `pypa/pip` | 11260.0 |
| `python/cpython` | 500.0 |

- Min: 139.0
- Max: 11260.0
- Mean: 1739.4000

### M-03 — Code Churn Ratio
- Unit: ratio
- Expected range: [0.0, 1.0]
- Aggregation: mean

| Repository | Value |
|-----------|-------|
| `tiangolo/typer` | 0.00429769130998704 |
| `tiangolo/full-stack-fastapi-template` | 0.014223096234309595 |
| `pypa/sampleproject` | 0.024700239808153474 |
| `tiangolo/uvicorn` | 0.009306666666666661 |
| `encode/httpx` | 0.011866880000000026 |
| `encode/starlette` | 0.009784806201550426 |
| `pallets/flask` | 0.018725656993665418 |
| `psf/requests` | 0.008919042686583311 |
| `pypa/pip` | 0.0034850141561721592 |
| `python/cpython` | 0.0024714077587667253 |

- Min: 0.0024714077587667253
- Max: 0.024700239808153474
- Mean: 0.0108

### M-04 — Test Coverage Ratio
- Unit: ratio
- Expected range: [0.0, 1.0]
- Aggregation: mean

| Repository | Value |
|-----------|-------|
| `tiangolo/typer` | 0.38780804150453957 |
| `tiangolo/full-stack-fastapi-template` | 0.09623430962343096 |
| `pypa/sampleproject` | 0.16666666666666666 |
| `tiangolo/uvicorn` | 0.2647058823529412 |
| `encode/httpx` | 0.296 |
| `encode/starlette` | 0.2558139534883721 |
| `pallets/flask` | 0.2033898305084746 |
| `psf/requests` | 0.11538461538461539 |
| `pypa/pip` | 0.21710526315789475 |
| `python/cpython` | 0.15009317296290023 |

- Min: 0.09623430962343096
- Max: 0.38780804150453957
- Mean: 0.2153

### M-05 — Review Latency
- Unit: hours
- Expected range: [0.0, inf]
- Aggregation: mean

- No values computed

### M-06 — File Change Count
- Unit: count
- Expected range: [0.0, inf]
- Aggregation: sum

| Repository | Value |
|-----------|-------|
| `tiangolo/typer` | 84490.0 |
| `tiangolo/full-stack-fastapi-template` | 101478.0 |
| `pypa/sampleproject` | 2060.0 |
| `tiangolo/uvicorn` | 27060.0 |
| `encode/httpx` | 54350.0 |
| `encode/starlette` | 45233.0 |
| `pallets/flask` | 726585.0 |
| `psf/requests` | 227381.0 |
| `pypa/pip` | 2087635.0 |
| `python/cpython` | 3204713.0 |

- Min: 2060.0
- Max: 3204713.0
- Mean: 656098.5000

### M-07 — Branch Freshness Ratio
- Unit: ratio
- Expected range: [0.0, 1.0]
- Aggregation: mean

| Repository | Value |
|-----------|-------|
| `tiangolo/typer` | 0.9965294491680813 |
| `tiangolo/full-stack-fastapi-template` | 0.9625673242908951 |
| `pypa/sampleproject` | 0.0 |
| `tiangolo/uvicorn` | 0.0 |
| `encode/httpx` | 0.27801142566525217 |
| `encode/starlette` | 0.9165163448370628 |
| `pallets/flask` | 0.8178335677679398 |
| `psf/requests` | 0.979617828777199 |
| `pypa/pip` | 0.9980944596150977 |
| `python/cpython` | 0.9991794024364069 |

- Min: 0.0
- Max: 0.9991794024364069
- Mean: 0.6948

