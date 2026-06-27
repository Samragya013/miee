# MIIE — Measurement Integrity Intelligence Engine

[![CI](https://github.com/Samragya013/miie/actions/workflows/ci.yml/badge.svg)](https://github.com/Samragya013/miie/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](https://github.com/Samragya013/miie/releases/tag/v1.0.0)

A research tool for evaluating whether software engineering metrics remain trustworthy representations of the constructs they claim to measure.

---

## Overview

MIIE analyzes git repositories to detect anomalies in development patterns using statistical methods. It identifies distribution drift, correlation breakdown, and threshold compression in commit frequency metrics.

### Mission

To provide a reproducible, open-source tool for metric validation in software engineering research.

### Scope

- CLI-first
- Offline-first
- Deterministic
- Benchmark-driven
- Research-oriented

### Non-Goals

- Not a SaaS platform
- Not a dashboard
- Not a web platform
- Not an enterprise analytics suite
- Not a developer productivity system
- Not an employee ranking platform

---

## Architecture

```
┌─────────────┐
│   CLI       │  10 commands, 3-tier output
└──────┬──────┘
       │
┌──────▼──────┐
│  Pipeline   │  9 stages: ingest → extract → segment → detect → score → explain → report
└──────┬──────┘
       │
┌──────▼──────┐
│  Detectors  │  D-01 (Drift) | D-02 (Correlation) | D-03 (Compression)
└──────┬──────┘
       │
┌──────▼──────┐
│   Output    │  JSON | Text | Forensic evidence packages
└─────────────┘
```

### Key Components

| Component | Description |
|---|---|
| `src/miie/cli.py` | CLI interface with 10 commands |
| `src/miie/orchestration/pipeline.py` | 9-stage analysis pipeline |
| `src/miie/processing/detection/` | 3 anomaly detectors |
| `src/miie/processing/scoring/` | Health score computation |
| `src/miie/processing/evidence.py` | Evidence packaging |
| `src/miie/processing/explanation/` | Human-readable explanations |

---

## Installation

### From Source

```bash
git clone https://github.com/Samragya013/miie.git
cd miie
pip install .
```

### Development Setup

```bash
git clone https://github.com/Samragya013/miie.git
cd miie
pip install poetry
poetry install
poetry run pre-commit install
```

### Verify Installation

```bash
python -m miie --version
```

---

## CLI Usage

### Commands

| Command | Description |
|---|---|
| `analyze` | Full pipeline analysis |
| `ingest` | Ingest commits from repository |
| `detect` | Run anomaly detection |
| `explain` | Generate explanations |
| `export` | Export results in specified formats |
| `evaluate` | Evaluate benchmark results |
| `generate` | Generate synthetic benchmark candidates |
| `benchmark` | Execute benchmark suite |
| `validate` | Validate config or output |
| `status` | Show project status |

### Options

| Option | Description |
|---|---|
| `--verbose` | Show detector IDs + timing |
| `--forensic` | Show full evidence package |
| `--format json` | Machine-readable JSON output |
| `--auth-token` | GitHub authentication token |

### Example Commands

```bash
# Analyze a local repository
python -m miie analyze /path/to/repo

# Analyze with verbose output
python -m miie analyze /path/to/repo --verbose

# Analyze with forensic output
python -m miie analyze /path/to/repo --forensic

# Analyze with JSON output
python -m miie analyze /path/to/repo --format json

# Analyze a GitHub repository
python -m miie analyze https://github.com/user/repo --auth-token YOUR_TOKEN

# Show version
python -m miie --version
```

### Example Output

```
$ python -m miie analyze flask --verbose

Stage 1/7: Ingesting commits... done (2.3s)
Stage 2/7: Extracting metrics... done (5.1s)
Stage 3/7: Segmenting time-series... done (0.2s)
Stage 4/7: Detecting anomalies... done (1.8s)
Stage 5/7: Computing scores... done (0.3s)
Stage 6/7: Generating explanations... done (0.1s)
Stage 7/7: Building report... done (0.2s)

Analysis Complete
═══════════════════════════════════════════
Repository: flask
Integrity: 1.000 (Very High)
Confidence: 0.993 (Very High)
Risk: Very Low

Detectors:
  D-01 (Distribution Drift): PASS
  D-02 (Correlation Breakdown): PASS
  D-03 (Threshold Compression): PASS
═══════════════════════════════════════════
```

---

## Detector Explanation

### D-01 — Distribution Drift Detector

Identifies shifts in commit frequency distributions between time windows.

- **Statistical Test**: Kolmogorov-Smirnov two-sample test
- **Supplementary**: Population Stability Index (PSI)
- **Threshold**: α=0.05 (KS), PSI=0.25
- **Minimum Sample**: n≥10 per window

### D-02 — Correlation Breakdown Detector

Detects broken relationships between metrics across time windows.

- **Statistical Tests**: Pearson r, Spearman ρ, Fisher-z transform
- **Breakdown Types**: sudden_drop, sign_reversal, gradual_erosion, confidence_exclusion
- **Minimum Sample**: n≥10

### D-03 — Threshold Compression Detector

Finds compression in metric distributions indicating loss of variability.

- **Statistical Tests**: Excess Mass, Hartigan's Dip Test (KS approximation)
- **Threshold**: z=1.645 (one-sided)
- **Minimum Sample**: n≥20

---

## Limitations

| Limitation | Workaround |
|---|---|
| Repos with >100K commits may timeout | Increase timeout or reduce time window |
| Windows file locking on some repos | Run on Linux/Mac |
| Minimum sample size gates | Use repositories with sufficient history |

---

## Roadmap

### V1.1 (Planned)

- Configurable timeout for large repositories
- Cross-platform CI testing
- Additional anomaly detectors
- REST API endpoints

### V2.0 (Future)

- Observation Engine
- Real-time monitoring
- Multi-repository batch analysis
- Custom detector plugins

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding conventions, and pull request workflow.

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## Support

- **Documentation**: `docs/` directory
- **Architecture**: `docs/architecture/`
- **Authority Documents**: `docs/authority/`
- **Release Notes**: `docs/governance/release/15_RELEASE_NOTES.md`
- **Issues**: [GitHub Issues](https://github.com/Samragya013/miie/issues)
