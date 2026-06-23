# MIIE v1.0.0 — Release Notes

**Version:** 1.0.0
**Date:** 2026-06-24
**Status:** Stable Release

---

## Overview

Measurement Integrity Intelligence Engine (MIIE) v1.0.0 is the first stable release of the platform for evaluating the validity of software engineering metrics. It provides automated detection of metric pathologies (distributional drift, correlation breakdown, threshold compression) with statistical rigor, reproducible scoring, and multi-format reporting.

---

## Frozen Metrics (7)

| ID | Name | Unit |
|----|------|------|
| M-01 | Code Coverage | % |
| M-02 | Commit Frequency | commits/day |
| M-03 | Code Churn | lines/commit |
| M-04 | Review Participation | reviewers/PR |
| M-05 | Review Latency | hours |
| M-06 | Issue Resolution Time | days |
| M-07 | Cyclomatic Complexity | count |

All 7 metrics are frozen per TFS §2 with exact ranges, units, and missing-data handling strategies.

---

## Frozen Detectors (3)

| ID | Name | Statistical Tests |
|----|------|-------------------|
| D-01 | Distributional Drift | KS test, PSI |
| D-02 | Correlation Breakdown | Pearson/Spearman trajectory, Fisher z-transform |
| D-03 | Threshold Compression | Bootstrap, Hartigan's dip test |

All 3 detectors are frozen per TFS §4–5 with exact thresholds (α=0.05, ψ=0.25, r=0.3, margin=0.02).

---

## CLI Commands (8)

| Command | Purpose | Exit Codes |
|---------|---------|------------|
| `miie ingest` | Validate and ingest a repository | 0, 2, 3 |
| `miie analyze` | Full analysis pipeline | 0, 1, 2, 3 |
| `miie detect` | Run detectors on a repository | 0, 2, 3 |
| `miie benchmark` | Execute benchmark suite | 0, 4 |
| `miie evaluate` | Evaluate benchmark vs ground truth | 0, 2, 3 |
| `miie explain` | Generate explanations | 0, 3 |
| `miie export` | Export results in formats | 0, 3 |
| `miie generate` | Generate synthetic benchmarks | 0, 2, 3 |

Global options: `--config`, `--output`, `--verbose`, `--version`, `--help`.

---

## API Endpoints (6)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/analyze` | POST | Full analysis |
| `/v1/benchmark` | POST | Benchmark execution |
| `/v1/explain` | POST | Explanation generation |
| `/v1/export` | POST | Export results |
| `/v1/jobs/{job_id}` | GET | Job status |
| `/v1/health` | GET | Health check |

---

## Benchmark Datasets

- **120** benchmark datasets across 3 suites (B-01 metric-drift, B-02 correlation-breakdown, B-03 threshold-compression)
- 40 datasets per suite (20 positive, 20 negative ground truth labels)
- Cohen's Kappa ≥ 0.65 inter-rater agreement

---

## Scoring

- **Integrity Score (IS):** Weighted combination of detector severities, range [0.0, 1.0]
- **Confidence Score (CS):** Factor-based reliability assessment with band classification (high/medium/low/critical)
- Default detector weights: D-01=0.40, D-02=0.35, D-03=0.25

---

## Known Limitations

1. **Batch-only processing** — No real-time streaming or WebSocket support (V1 scope per TFS §1.5)
2. **No GUI** — CLI and API only; no web interface
3. **No multi-tenancy** — Self-hosted single-tenant deployment
4. **Filesystem storage** — No SQL database; all state persisted as files
5. **No auth beyond API key** — No OAuth, JWT, or RBAC (V1 scope per TFS §14.2)
6. **No plugin architecture** — Detectors are hardcoded; extensibility planned for V2
7. **No causal inference** — Correlation only; causation analysis deferred to V2
8. **Single-process execution** — Benchmark runner uses sequential processing (max 4 parallel workers)
9. **Git only** — No support for Mercurial, SVN, or other VCS
10. **Shallow clone caveat** — Some metrics may be incomplete with shallow clones

---

## Breaking Changes from Pre-release

None — this is the first stable release.

---

## Upgrade Path

N/A — initial release.

---

## Dependencies

| Package | Version |
|---------|---------|
| Python | ^3.10, <3.13 |
| NumPy | 1.24.3 |
| pandas | 2.0.3 |
| SciPy | 1.11.1 |
| Jinja2 | 3.1.2 |
| Click | 8.1.3 |
| PyYAML | 6.0.1 |
| FastAPI | 0.100.0 |

---

## License

MIT
