# MIIE — Configuration Reference

## Overview

MIIE uses a layered configuration system:
1. Defaults (hardcoded)
2. Config file (TOML/YAML)
3. Environment variables
4. CLI arguments

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | Yes (for M-05) | — | GitHub personal access token |
| `MIIE_API_KEY` | No | — | API authentication key |
| `MIIE_CONFIG` | No | — | Path to config file |
| `PYTHONIOENCODING` | No | utf-8 | Encoding (set to utf-8 on Windows) |

## Config File

Create `miie.toml` in project root:

```toml
[analysis]
window_size = "7d"
max_windows = 52
exclude_bots = true

[analysis.time]
since = "2023-01-01"
until = "2024-01-01"

[detection]
enabled = ["D-01", "D-02", "D-03"]

[detection.thresholds]
ks_alpha = 0.05
psi_threshold = 0.25

[scoring]
integrity_weights = { D-01 = 0.33, D-02 = 0.33, D-03 = 0.33 }

[output]
format = "json"
directory = "./output"
```

## CLI Arguments

```bash
miie analyze [OPTIONS] REPOSITORY

Options:
  -c, --config PATH       Config file path
  -o, --output PATH       Output directory
  -f, --format TEXT       Output format (json/markdown/csv)
  -w, --windows INT       Number of time windows
  -W, --window-size TEXT  Window size (e.g., 7d, 30d, 1y)
  --since DATE            Start date (YYYY-MM-DD)
  --until DATE            End date (YYYY-MM-DD)
  --no-bots               Exclude bot commits
  --dry-run               Preview without running analysis
  --verbose               Verbose output
  --json                  JSON output
```

## GitHub Token Setup

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Create token with `repo` scope
3. Add to `.env`:
   ```
   GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
   ```

## Windows Encoding

On Windows, set encoding to prevent crashes:
```powershell
$env:PYTHONIOENCODING="utf-8"
```

Or add to PowerShell profile:
```powershell
# Add to $PROFILE
$env:PYTHONIOENCODING = "utf-8"
```
