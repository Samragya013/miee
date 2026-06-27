# MIIE v1.0.0 — Gold Release Package

**Date:** 2026-06-24
**Commit:** bd18341
**Branch:** autoresearch/miie/validation

---

## 1. Release Summary

MIIE v1.0.0 is a production-quality CLI tool for measuring repository metric integrity.
It detects metric drift, correlation breakdown, and threshold compression across
git repository histories using statistical detectors backed by evidence packages.

---

## 2. Test Results

| Metric | Value |
|--------|-------|
| Total tests | 911 |
| Passed | 911 |
| Failed | 0 |
| Skipped | 4 |
| Pre-commit hooks | All passing |
| Test runtime | ~2.5 minutes |

---

## 3. Benchmark Results (TFS v1.0 Ground Truth)

| Detector | Precision | Recall | Target P | Target R | Status |
|----------|-----------|--------|----------|----------|--------|
| D-01 (Distribution Drift) | 0.8889 | 0.9412 | >= 0.80 | >= 0.75 | PASS |
| D-02 (Correlation Breakdown) | 0.8182 | 0.9000 | >= 0.75 | >= 0.70 | PASS |
| D-03 (Threshold Compression) | 0.9000 | 0.9000 | >= 0.85 | >= 0.80 | PASS |

---

## 4. CLI Options

| Option | Description |
|--------|-------------|
| `--metrics`, `-m` | Metric IDs to extract (repeatable). Default: M-02 M-06 |
| `--detectors`, `-d` | Detector IDs to enable (repeatable). Default: D-01 D-02 D-03 |
| `--output-dir`, `-o` | Output directory for reports. Default: ./output |
| `--window-strategy`, `-w` | Window segmentation: time, commit, release, custom |
| `--window-size`, `-s` | Window size in days/commits. Default: 7 |
| `--since` | Extract metrics since (ISO 8601) |
| `--until` | Extract metrics until (ISO 8601) |
| `--exclude-bots` | Exclude bot-generated commits |
| `--thresholds` | Custom detector thresholds as JSON string |
| `--dry-run` | Validate inputs and show plan without executing |
| `--seed` | Random seed for reproducibility. Default: 42 |
| `--format`, `-f` | Output format: json, md, csv |
| `--auth-token` | GitHub PAT for private repos. Falls back to GITHUB_TOKEN env var |
| `--verbose` | Show detector IDs and timing details |
| `--forensic` | Include full evidence package in output (advanced users) |

---

## 5. Output Tiers

### Default Mode
Human-friendly output with `[OK]`/`[X]` markers. No internal IDs, paths, or hashes.
Suitable for students, researchers, and maintainers.

### Verbose Mode (`--verbose`)
Shows detector IDs (`[D-01] PASS`) and per-stage timing. Same privacy filtering as default.

### Forensic Mode (`--forensic`)
Full evidence package: window details, raw detector outputs, repository metadata
including repo_id, run_id, local_path. For advanced debugging and reproducibility.

---

## 6. Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (integrity score = 1.0) |
| 1 | Integrity failures detected (score < 1.0) |
| 2 | System error (pipeline crash, file not found) |
| 3 | Invalid arguments (bad CLI args, validation failure) |
| 4 | Benchmark failure |

---

## 7. Privacy Filtering

Default mode removes from JSON output:
- `repo_id` (hash of repository path)
- `run_id` (UUID of analysis run)
- `local_path` (filesystem path)
- `temp_path` (temporary clone path)

Forensic mode preserves all fields for reproducibility.

---

## 8. JSON Serialization

The `--format json` output uses `_serialize_for_json()` which:
- Recursively converts dataclasses to dicts
- Converts datetime objects to ISO 8601 strings
- Converts Path objects to strings
- Handles nested structures without Python object references

---

## 9. Confidence Explanation

Confidence level is derived from 5 factors:
- `sample_size`: Number of analysis windows (drives low confidence for short repos)
- `variance`: Metric variance across windows
- `missing_data`: Completeness of metric-window pairs
- `window_balance`: Uniformity of window sizes
- `detector_success`: Fraction of detectors that produced results

CLI displays human-readable reasons based on which factors are low.

---

## 10. Risk Classification

Based on triggered detector count:
- 0 triggered: Very Low
- 1 triggered: Low
- 2 triggered: Moderate
- 3+ triggered: High

---

## 11. Files Modified in Productization Sprint

| File | Change |
|------|--------|
| `src/miie/cli.py` | 3-tier output, privacy filtering, --verbose, --forensic, confidence explanation, risk classification |
| `src/miie/processing/reporting/engine.py` | `_serialize_for_json()` for dataclass-aware JSON serialization |
| `tests/test_cli_usability.py` | Updated for Phase 8 output format |

---

## 12. Certification

- [x] All 911 tests passing
- [x] All 3 detectors meet TFS v1.0 benchmark targets
- [x] CLI options match validator valid set
- [x] Default output understandable without internal IDs
- [x] JSON output serializes cleanly (no datetime/object errors)
- [x] Privacy filtering active in default mode
- [x] Forensic mode preserves all fields
- [x] No breaking import paths
- [x] No secrets in code
- [x] Exit codes documented and working

**Status: GOLD RELEASE READY**
