# MIIE Architecture

## Overview

MIIE (Measurement Integrity Intelligence Engine) is a pipeline-based system for analyzing software repository metrics and detecting integrity anomalies.

## Pipeline Stages

1. **Ingestion** (INT-01): Validates and ingests Git repositories
2. **Extraction** (INT-02): Extracts metric data (M-01 through M-07)
3. **Segmentation** (INT-03): Segments data into analysis windows
4. **Detection** (INT-04): Runs anomaly detectors (D-01, D-02, D-03)
5. **Scoring** (INT-05): Computes integrity and confidence scores
6. **Evidence** (INT-06): Generates traceable evidence packages
7. **Explanation** (INT-07): Produces human-readable explanations
8. **Reporting** (INT-08): Generates reports in multiple formats

## Key Components

- `src/miie/orchestration/pipeline.py` — Pipeline orchestrator
- `src/miie/processing/` — All processing engines
- `src/miie/schemas/` — Data models and serialization
- `src/miie/contracts/` — Interface protocols (ACS Section 3)

## Detectors

- **D-01**: Distribution Drift (KS test, PSI)
- **D-02**: Correlation Breakdown (Pearson delta)
- **D-03**: Threshold Compression (compression index)

## Metrics

- **M-01**: Lines of Code
- **M-02**: Commit Frequency
- **M-03**: Issue Count
- **M-04**: Review Coverage
- **M-05**: Test Coverage
- **M-06**: Code Churn
- **M-07**: Dependency Count
