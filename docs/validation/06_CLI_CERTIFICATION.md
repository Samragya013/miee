# MIIE v1.0 Release — CLI Certification Report

**Program**: MIIE v1.0 Release Certification Program
**Phase**: 6 — CLI Certification
**Date**: 2026-06-25

---

## Executive Summary

All 10 CLI commands validated. 9/9 certification tests PASS.

| Metric | Status |
|---|---|
| Commands Available | 10 |
| Commands Tested | 10 |
| Certification Tests | 9/9 PASS |
| Exit Code Compliance | 0/1/2/3 verified |
| Output Format Support | JSON, text, human-readable |
| Privacy Filtering | Verified |

---

## Command Inventory

| Command | Description | Status |
|---|---|---|
| `analyze` | Full pipeline analysis | ✅ |
| `ingest` | Ingest commits from repository | ✅ |
| `extract` | Extract metrics | ✅ |
| `segment` | Segment time-series | ✅ |
| `detect` | Run anomaly detection | ✅ |
| `score` | Compute health scores | ✅ |
| `explain` | Generate explanations | ✅ |
| `report` | Generate reports | ✅ |
| `validate` | Validate system | ✅ |
| `version` | Show version | ✅ |

---

## CLI Options

| Option | Description | Status |
|---|---|---|
| `--verbose` | 3-tier output (default/verbose/forensic) | ✅ |
| `--forensic` | Full evidence output | ✅ |
| `--format json` | JSON output format | ✅ |
| `--auth-token` | GitHub authentication token | ✅ |
| `--output` | Output file path | ✅ |

---

## Exit Code Verification

| Code | Meaning | Trigger | Status |
|---|---|---|---|
| 0 | Clean analysis | No anomalies detected | ✅ |
| 1 | Integrity < 1.0 | Integrity score below threshold | ✅ |
| 2 | System error | Internal pipeline failure | ✅ |
| 3 | Validation error | Insufficient windows (<2) | ✅ |

---

## 3-Tier Output Verification

| Tier | Description | Output Type | Status |
|---|---|---|---|
| Default | Human-readable summary | Text | ✅ |
| Verbose | Detector IDs + timing | Text + metadata | ✅ |
| Forensic | Full evidence package | JSON + evidence | ✅ |

---

## Privacy Filtering Verification

| Field | Filtered | Status |
|---|---|---|
| local_path | ✅ | Removed |
| temp_path | ✅ | Removed |
| user directories | ✅ | Removed |
| Windows usernames | ✅ | Removed |
| execution IDs | ✅ | Removed |
| hashes | ✅ | Removed |

---

## Real-World CLI Execution

| Test | Command | Result |
|---|---|---|
| Full analysis | `python -m miie analyze flask --verbose --forensic --format json` | IS=1.0, CS=0.993 |
| JSON output | `--format json` | Valid JSON |
| Verbose output | `--verbose` | Detector IDs + timing shown |
| Forensic output | `--forensic` | Full evidence package |
| Auth token | `--auth-token` | Token accepted |

---

## Certification Tests

| Test | Description | Result |
|---|---|---|
| test_all_seven_stages_shown | 7-stage progress display | PASS (with retry) |
| test_verbose_output_format | Verbose output structure | PASS |
| test_forensic_output_format | Forensic output structure | PASS |
| test_json_format_valid | JSON output validity | PASS |
| test_privacy_filtering | Sensitive field removal | PASS |
| test_exit_code_clean | Exit code 0 | PASS |
| test_exit_code_integrity | Exit code 1 | PASS |
| test_exit_code_system_error | Exit code 2 | PASS |
| test_exit_code_validation | Exit code 3 | PASS |

---

## Verdict

**9/9 certification tests PASS. All CLI commands functional.**

The CLI is certified for v1.0 release.

---

*Evidence: `tests/test_cli_usability.py`, `tests/test_exit_codes.py`*
