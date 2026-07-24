# MIIE — Flagship Architecture

## System Overview

MIIE (Measurement Integrity Intelligence Engine) is a Python research tool that evaluates the validity and integrity of software engineering metrics extracted from Version Control System (VCS) histories.

## Architecture Principles

1. **Frozen Scientific Core** — Detectors, metrics, evidence, scoring, confidence are immutable
2. **Progressive Disclosure** — Start simple, reveal complexity as needed
3. **Evidence-First** — Every finding backed by statistical test with p-value or effect size
4. **Deterministic** — Same inputs produce same outputs always

## Package Structure

```
src/miie/
├── api/                    # FastAPI REST endpoints (6 frozen)
├── application/            # CLI interactive layer, workflow, session
├── benchmark/              # Benchmark execution engine
├── cli/                    # Click CLI commands (14 commands)
├── config/                 # Configuration loader
├── contracts/              # Interfaces (frozen contracts)
├── experimental/           # Non-production code
├── metrics/                # Metric extraction (M-01 through M-07)
├── observation_graph/      # Observation graph data structures
├── orchestration/          # Workflow orchestration
├── processing/             # Core scientific processing
│   ├── benchmark/          # Benchmark evaluation
│   ├── detection/          # Detectors (D-01, D-02, D-03)
│   ├── evaluation/         # Evaluation engine
│   ├── explanation/        # Explanation engine with recommendations
│   ├── extraction/         # Data extraction
│   ├── observation/        # Observation processing
│   ├── reporting/          # Report generation (14+ types)
│   └── scoring/            # Integrity + Confidence scoring
├── providers/              # External data providers
├── reporting/              # Legacy reporting (templates)
├── sampling/               # Sampling strategies
├── schemas/                # Data models (frozen)
├── scientific/             # Scientific validation
├── storage/                # Storage interfaces
├── utils/                  # Utilities (hashing, etc.)
├── validation/             # Validation framework
└── workspace/              # Persistent workspace (ECP-03)
```

## Data Flow

```
Repository → Ingestion → Extraction → Observation → Detection → Scoring → Reporting
     ↓           ↓            ↓            ↓            ↓          ↓          ↓
  Git clone   Context    7 metrics    Windows     D-01/D-02   IS/CS    Dashboard
              creation   extracted    created     /D-03       scores   + exports
```

## Key Components

### ExtractionEngine (`processing/extraction/engine.py`)
- Orchestrates GitObservationProvider and GitHubPullRequestProvider
- Produces ObservationCollection and MetricDataFrame
- Handles bot filtering, time windows, GitHub PR extraction

### DetectorRunner (`processing/detection/runner.py`)
- Runs D-01 (Distribution Drift), D-02 (Correlation Breakdown), D-03 (Threshold Compression)
- Uses DetectorAdapter to translate observations to detector inputs
- Produces DetectorResult with per-detector outputs

### ScoringEngine (`processing/scoring/engine.py`)
- Computes Integrity Score (weighted detector results)
- Computes Confidence Score (5 factors: sample_size, variance, missing_data, window_balance, detector_success)

### WorkspaceEngine (`workspace/engine.py`)
- Manages persistent post-analysis state
- Provides views: ExecutiveSummary, MetricView, DetectorView, EvidenceView, etc.
- Supports save/load, comparison, export

## Frozen Core (DO NOT MODIFY)

| Component | Location | Reason |
|-----------|----------|--------|
| M-01 through M-07 | `metrics/` | Statistical validity |
| D-01, D-02, D-03 | `processing/detection/` | Scientific methods |
| EvidencePackage | `processing/evidence.py` | Provenance tracking |
| ConfidenceScore | `schemas/models.py` | Scoring formula |
| IntegrityScore | `schemas/models.py` | Scoring formula |
| Statistical methods | `processing/detection/statistics.py` | Mathematical correctness |
| All contracts | `contracts/interfaces.py` | API stability |
