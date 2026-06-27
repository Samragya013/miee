# MIIE v1.0 Dataset Registry

**Status:** Registry Structure Only  
**Date:** 2026-06-08  
**Version:** 1.0.0  
**Classification:** Governance Sprint Artifact  

---

## Dataset Registry

This registry defines the structure for benchmark datasets. Datasets will be populated in Phase 2 (Dataset Generation).

| Dataset ID | Dataset Name | Dataset Type | Synthetic / Real | Version | Purpose | Status | Owner | Notes |
|------------|--------------|--------------|------------------|---------|---------|--------|-------|-------|
| TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

---

## Dataset Type Definitions

| Type | Description | Use Case |
|------|-------------|----------|
| Synthetic | Generated with controlled parameters and injected pathologies | Detector validation, benchmark testing |
| Real | Extracted from actual repositories | Real-world validation, case studies |
| Hybrid | Synthetic base with real-world annotations | Ground truth for real repositories |

---

## Dataset Properties

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| dataset_id | string | Unique identifier (e.g., repo_001, dataset-v1-001) |
| suite_id | string | Benchmark suite identifier (e.g., metric-drift-v1.0.0) |
| version | string | Dataset version (e.g., 1.0.0) |
| type | string | Dataset type (synthetic, real, hybrid) |
| generated_at | string | Generation timestamp (ISO 8601) |
| repository_url | string | Original repository URL (for real datasets) |
| metadata_seed | integer | Random seed for synthetic generation |

### Synthetic Dataset Properties

| Property | Type | Description |
|----------|------|-------------|
| category | string | Repository category (small_active, medium_active, etc.) |
| language | string | Primary language (python, java, cpp, etc.) |
| duration_days | integer | Repository duration in days |
| total_commits | integer | Total commits in dataset |
| contributors | integer | Number of unique contributors |
| bot_ratio | float | Bot commit ratio (0.0-0.3) |
| window_count | integer | Number of time windows |
| window_size_days | integer | Window size in days |
| pathology_ratio | float | Proportion of datasets with injected pathologies |

### Annotation Properties

| Property | Type | Description |
|----------|------|-------------|
| annotation_kappa | float | Cohen's Kappa for inter-annotator agreement |
| annotator_count | integer | Number of annotators |
| annotation_date | string | Annotation completion date |
| review_status | string | Annotation status (raw, reviewed, approved) |

---

## Benchmark Suite Mappings

### metric-drift-v1.0.0

| Property | Value |
|----------|-------|
| Suite ID | metric-drift-v1.0.0 |
| Target Detector | D-01 (Distributional Drift) |
| Dataset Type | Synthetic |
| Dataset Count | 50 |
| Metrics Included | M-01, M-02, M-06, M-07 |
| Window Strategy | time |
| Window Size | 30 days |
| Random Seed | 42 |

### correlation-breakdown-v1.0.0

| Property | Value |
|----------|-------|
| Suite ID | correlation-breakdown-v1.0.0 |
| Target Detector | D-02 (Correlation Breakdown) |
| Dataset Type | Synthetic |
| Dataset Count | 40 |
| Metrics Included | M-01, M-02, M-03, M-04, M-05, M-06, M-07 |
| Window Strategy | time |
| Window Size | 30 days |
| Random Seed | 42 |

### threshold-compression-v1.0.0

| Property | Value |
|----------|-------|
| Suite ID | threshold-compression-v1.0.0 |
| Target Detector | D-03 (Threshold Compression) |
| Dataset Type | Synthetic |
| Dataset Count | 30 |
| Metrics Included | M-01, M-02, M-06, M-07 |
| Window Strategy | time |
| Window Size | 30 days |
| Random Seed | 42 |

---

## Dataset Lifecycle

```
[GENERATION] → [VALIDATION] → [ANNOTATION] → [REVIEW] → [APPROVAL] → [FREEZE]
```

### Generation
- Synthetic datasets generated with controlled parameters
- Pathologies injected at specified windows
- Metadata and checksums computed

### Validation
- Schema validation (JSON Schema draft-07)
- Metric value range validation
- Window non-overlap validation
- Checksum verification

### Annotation
- Multiple annotators label datasets
- Cohen's Kappa computed for agreement
- Disagreements resolved through adjudication

### Review
- Expert review of annotations
- Evidence requirements verified
- Ground truth finalized

### Approval
- All annotations approved
- Dataset frozen for benchmark use
- No further modifications permitted

---

## Dataset Access

### Storage Location

```
~/.miie/benchmarks/
├── metric-drift-v1.0.0/
│   ├── manifest.json
│   ├── schema.json
│   ├── ground_truth.json
│   ├── data/
│   │   ├── repo_001/
│   │   │   ├── metrics.json
│   │   │   └── windows.json
│   │   ├── repo_002/
│   │   └── ...
│   └── README.md
├── correlation-breakdown-v1.0.0/
└── threshold-compression-v1.0.0/
```

### Access Requirements

| Requirement | Description |
|-------------|-------------|
| Read Access | All benchmark datasets are publicly readable |
| Write Access | Only dataset generator with version bump |
| Update Access | Only through benchmark version bump |
| Deletion Access | Not permitted (immutable archives) |

---

*This dataset registry is a template. Populate dataset entries during Phase 2 (Dataset Generation).*