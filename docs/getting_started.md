# MIIE — Getting Started

## Quick Start

### 1. Install

```bash
git clone https://github.com/your-org/miee.git
cd miee
pip install -e ".[dev]"
```

### 2. Configure

```bash
# Copy template
cp .env.example .env

# Edit .env with your GitHub token
GITHUB_TOKEN=ghp_your_token_here
```

### 3. Analyze

```bash
# Interactive mode
miie tui

# CLI mode
miie analyze /path/to/repo

# With options
miie analyze /path/to/repo --windows 30 --window-size 7d --format json
```

### 4. Check Health

```bash
miie doctor
```

## Prerequisites

- Python 3.10-3.12
- Git installed and in PATH
- GitHub token (for M-05 PR latency metric)

## Available Commands

| Command | Description |
|---------|-------------|
| `miie analyze` | Full analysis pipeline |
| `miie tui` | Interactive terminal UI |
| `miie doctor` | System health checks |
| `miie ingest` | Validate and ingest repository |
| `miie detect` | Run detectors on repository |
| `miie benchmark` | Execute benchmark suite |
| `miie evaluate` | Evaluate benchmark results |
| `miie explain` | Generate explanations |
| `miie export` | Export results |
| `miie generate` | Generate synthetic candidates |
| `miie status` | Show system status |
| `miie validate` | Validate config/output |
| `miie shell` | Interactive shell mode |
| `miie interactive` | Full-screen interactive mode |

## Output

Analysis produces:
- **Integrity Score** (0.0-1.0): How trustworthy the metrics are
- **Confidence Score** (0.0-1.0): How confident we are in the analysis
- **Metric Values**: M-01 through M-07 observations
- **Detector Results**: D-01/D-02/D-03 findings
- **Recommendations**: Actions to improve metric integrity

## Configuration

See `docs/configuration.md` for all options.

Key settings:
- `window_size`: Time window duration (default: 7d)
- `max_windows`: Maximum number of windows (default: 52)
- `exclude_bots`: Filter bot commits (default: true)
- `format`: Output format (json/markdown/csv)
