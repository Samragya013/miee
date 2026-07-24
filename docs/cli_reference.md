# MIIE — CLI Reference

## Commands

### `miie analyze`
Full analysis pipeline on a repository.

```bash
miie analyze /path/to/repo [OPTIONS]
```

Options:
- `--windows INT`: Number of time windows (default: auto)
- `--window-size TEXT`: Window size (default: 7d)
- `--since DATE`: Start date filter
- `--until DATE`: End date filter
- `--no-bots`: Exclude bot commits
- `--format TEXT`: Output format (json/markdown/csv)
- `--output PATH`: Output directory
- `--dry-run`: Preview without running
- `--verbose`: Verbose output
- `--json`: JSON output

### `miie tui`
Interactive terminal UI with dashboard, menus, and visualizations.

```bash
miie tui [REPOSITORY]
```

### `miie doctor`
System health checks.

```bash
miie doctor
```

Checks:
- Python version
- Core dependencies (numpy, scipy, pandas, click, rich, pydantic, defusedxml)
- Optional dependencies (pyyaml, prompt_toolkit)
- GitHub token
- .env file
- Frozen contracts
- Config loader

### `miie ingest`
Validate and ingest a repository.

```bash
miie ingest /path/to/repo
```

### `miie detect`
Run detectors on a repository.

```bash
miie detect /path/to/repo [OPTIONS]
```

### `miie benchmark`
Execute a benchmark suite.

```bash
miie benchmark [OPTIONS]
```

### `miie evaluate`
Evaluate benchmark results.

```bash
miie evaluate [OPTIONS]
```

### `miie explain`
Generate explanations from analysis.

```bash
miie explain [OPTIONS]
```

### `miie export`
Export results in specified formats.

```bash
miie export [OPTIONS]
```

### `miie generate`
Generate synthetic benchmark candidates.

```bash
miie generate [OPTIONS]
```

### `miie status`
Show system status.

```bash
miie status
```

### `miie validate`
Validate config file or analysis output.

```bash
miie validate [OPTIONS]
```

### `miie shell`
Interactive shell mode.

```bash
miie shell
```

### `miie interactive`
Full-screen interactive mode.

```bash
miie interactive
```

## Global Options

| Option | Description |
|--------|-------------|
| `--version` | Show version |
| `--help` | Show help |
| `--config PATH` | Config file path |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Integrity failures detected |
| 2 | System error |
| 3 | Invalid arguments |
| 4 | Benchmark failure |
