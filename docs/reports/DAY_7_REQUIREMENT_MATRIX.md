# Day 7 Requirement Matrix: Metric Extraction Foundation (M-02/M-06)

| Requirement | Authority | Deliverable | Validation Method | Completion Status |
|-------------|-----------|-------------|-------------------|-------------------|
| Implement metric registry (freeze M-01..M-07 inventory) | TFS_MIIE_v1.0.md (metric table), ACS_MIIE_v1.0.md (protocol INT-02), BSD-Engineering_MIIE_v1.0.md (metric ID validation) | Frozen metric registry (src/miie/registry.py or src/miie/schemas/metric_registry.py) | Unsupported metrics fail validation tests | Not Started (0%) |
| Extract Commit Frequency (implement Git-backed M-02) | TRD_MIIE_v1.0.md (§8), TFS_MIIE_v1.0.md (§2), BSD-Engineering_MIIE_v1.0.md (§6) | M-02 extractor (src/miie/processing/extraction.py) | Deterministic commit count from Git history | Not Started (0%) |
| Extract Code Churn (implement Git-backed M-06 foundation) | TRD_MIIE_v1.0.md (§8), TFS_MIIE_v1.0.md (§2), BSD-Engineering_MIIE_v1.0.md (§6) | M-06 extractor (src/miie/processing/extraction.py) | Fixture value stable (deterministic output) | Not Started (0%) |
| Encode unavailable metrics (avoid fake values) | BSD-Engineering_MIIE_v1.0.md (missing data policy), TFS_MIIE_v1.0.md (missing artifact policy), ACS_MIIE_v1.0.md (validation) | Valid missing-data records (handled in extraction layer) | Unavailable is not zero (explicit null/unavailable markers) | Not Started (0%) |
| Integrate extraction (feed detector mock) | AFD_MIIE_v1.0.md (workflow WF-02), ACS_MIIE_v1.0.md (interfaces, validation) | Pipeline slice (ingestion → extraction → mock detector) | Schema validation of MetricDataFrame output | Not Started (0%) |

## Notes
- Completion status is based on Day 6 completion status, as Day 7 work has not yet begun
- Authority columns list the primary source documents that define each requirement
- Deliverable and Validation Method are taken directly from the DAY 7 tasks table in the Operating Plan
- All requirements are explicitly for Day 7 only (Metric Extraction Foundation - M-02/M-06)
- No Day 8+ work is included in this matrix as per scope lock requirements