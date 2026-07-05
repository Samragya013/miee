# CLI Reference

## Usage

```bash
miie [OPTIONS] COMMAND [ARGS]...
```

## Global Options

| Option | Description |
|---|---|
| `--version` | Show version and exit |
| `-c, --config PATH` | Path to configuration file |
| `-o, --output PATH` | Output directory |
| `-V, --verbose` | Enable verbose output |
| `--debug` | Enable debug mode with stack traces |
| `--help` | Show help and exit |

## Commands

### analyze

Run the full analysis pipeline on a repository.

```bash
miie analyze REPOSITORY [OPTIONS]
```

| Option | Description |
|---|---|
| `--dry-run` | Show what would be analyzed |
| `--metrics TEXT` | Comma-separated metric IDs |
| `--detectors TEXT` | Comma-separated detector IDs |
| `--window-size INT` | Time window size in days |
| `--window-strategy TEXT` | Windowing strategy (time/count/adaptive) |
| `--format TEXT` | Output format (json/text) |
| `--export-markdown` | Export as Markdown report |
| `--export-json` | Export as JSON report |
| `--export-csv` | Export as CSV report |
| `--export-html` | Export as HTML report |
| `--auth-token TEXT` | GitHub authentication token |
| `--seed INT` | Random seed for reproducibility |

**Examples:**

```bash
miie analyze /path/to/repo
miie analyze /path/to/repo --metrics M-01,M-02 --detectors D-01
miie analyze /path/to/repo --dry-run
miie analyze https://github.com/user/repo --auth-token ghp_xxx
miie analyze /path/to/repo --export-markdown --export-json
```

### ingest

Validate and ingest a repository (checks Git validity).

```bash
miie ingest REPOSITORY [OPTIONS]
```

### detect

Run detection on a repository (ingestion + extraction + detection).

```bash
miie detect REPOSITORY [OPTIONS]
```

### explain

Run analysis and generate explanation report.

```bash
miie explain REPOSITORY [OPTIONS]
```

### export

Run analysis and export results in specified formats.

```bash
miie export REPOSITORY [OPTIONS]
```

### evaluate

Evaluate benchmark results against ground truth.

```bash
miie evaluate [OPTIONS]
```

### generate

Generate synthetic benchmark candidates.

```bash
miie generate [OPTIONS]
```

### benchmark

Execute a benchmark suite against detectors.

```bash
miie benchmark [OPTIONS]
```

### validate

Validate a config file, analysis output, or benchmark artifact.

```bash
miie validate [OPTIONS]
```

### status

Show MIIE project and pipeline status.

```bash
miie status [OPTIONS]
```

### setup

Interactive configuration wizard.

```bash
miie setup [OPTIONS]
```

## Pipeline Stages

The analysis pipeline runs 9 stages:

1. **Ingestion** — Clone/parse git history
2. **Extraction** — Compute metric values
3. **Segmentation** — Split into time windows
4. **Detection** — Run anomaly detectors
5. **Scoring** — Compute integrity/confidence scores
6. **Evidence** — Package forensic evidence
7. **Sampling** — Apply sampling strategies
8. **Observation** — Observation framework
9. **Reporting** — Generate output

## Detectors

| ID | Name | Description |
|---|---|---|
| D-01 | Distribution Drift | Detects shifts in commit frequency distributions |
| D-02 | Correlation Breakdown | Detects broken metric correlations |
| D-03 | Threshold Compression | Detects loss of metric variability |

## Metrics

| ID | Name | Description |
|---|---|---|
| M-01 | Commit Frequency | Commits per time window |
| M-02 | Code Churn | Lines added/removed per window |
| M-06 | Author Count | Unique authors per window |

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | General error |
| 2 | Analysis failed (with partial results saved) |
