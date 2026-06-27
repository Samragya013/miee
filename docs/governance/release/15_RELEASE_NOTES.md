# MIIE v1.0.0 Release Notes

**Release Date**: 2026-06-25
**Version**: 1.0.0

---

## What is MIIE?

MIIE (Mutual Information Ingestion Engine) is a software health analysis tool that analyzes git repositories to detect anomalies in development patterns. It uses statistical methods to identify distribution drift, correlation breakdown, and threshold compression.

---

## Key Features

### 3 Anomaly Detectors
- **D-01**: Distribution Drift Detector — Identifies shifts in commit frequency distributions
- **D-02**: Correlation Breakdown Detector — Detects broken relationships between metrics
- **D-03**: Threshold Compression Detector — Finds compression in metric distributions

### CLI Interface
- **10 commands**: analyze, ingest, extract, segment, detect, score, explain, report, validate, version
- **3-tier output**: Default (human-readable), Verbose (detector IDs + timing), Forensic (full evidence)
- **JSON format**: Machine-readable output via --format json
- **Auth support**: GitHub authentication via --auth-token

### Scientific Validation
- **Benchmark targets exceeded**: D-01 P=0.8889/R=0.9412, D-02 P=0.8182/R=0.9000, D-03 P=0.9000/R=0.9000
- **Real-world tested**: 25/30 repositories analyzed successfully
- **Performance scaling**: O(n^0.85) sub-linear

---

## Quick Start

### Installation
```bash
pip install miie
```

### Basic Usage
```bash
# Analyze a repository
python -m miie analyze <repo>

# Analyze with verbose output
python -m miie analyze <repo> --verbose

# Analyze with forensic output
python -m miie analyze <repo> --forensic

# Analyze with JSON output
python -m miie analyze <repo> --format json
```

### GitHub Repositories
```bash
# Analyze a GitHub repository
python -m miie analyze https://github.com/user/repo --auth-token YOUR_TOKEN
```

---

## System Requirements

- Python 3.10+
- Git
- 50-300MB RAM (depending on repository size)

---

## Known Limitations

| Limitation | Workaround |
|---|---|
| Repos with >100K commits timeout | Reduce time window or increase timeout |
| Windows file locking on some repos | Run on Linux/Mac |
| AutoGPT/AutoGen fail on Windows | Run on Linux/Mac |

---

## Upgrade Notes

This is the initial v1.0 release. No upgrade path required.

---

## Support

- **Documentation**: `docs/` directory
- **Authority Documents**: `docs/authority/` directory
- **Test Suite**: 911 tests (100% pass rate)

---

## License

See LICENSE file.

---

## Acknowledgments

Built with:
- Python 3.10+
- scipy (statistical tests)
- numpy (numerical operations)
- click (CLI framework)

---

*MIIE v1.0.0 — Release certified 2026-06-25*
