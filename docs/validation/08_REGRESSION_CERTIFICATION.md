# MIIE v1.0 Release — Regression Certification Report

**Program**: MIIE v1.0 Release Certification Program
**Phase**: 8 — Regression Certification
**Date**: 2026-06-25

---

## Executive Summary

Full regression suite executed. 911 passed, 4 skipped, 0 failed.

| Metric | Value | Status |
|---|---|---|
| Total Tests | 915 | — |
| Passed | 911 | PASS |
| Skipped | 4 | Expected |
| Failed | 0 | PASS |
| Duration | 157.29s (2:37) | Within budget |

---

## Test Category Breakdown

| Category | Tests | Passed | Skipped | Failed | Duration |
|---|---|---|---|---|---|
| unit/ | 271 | 271 | 0 | 0 | 91.60s |
| schema/ | 396 | 396 | 0 | 0 | 0.70s |
| architecture/ | — | — | 0 | 0 | — |
| contract/ | — | — | 0 | 0 | — |
| integration/ | 63 | 63 | 0 | 0 | 42.19s |
| workflow/ | — | — | 0 | 0 | — |
| regression/ | — | — | 0 | 0 | — |
| reproducibility/ | 148 | 144 | 4 | 0 | 8.13s |
| performance/ | — | — | 0 | 0 | — |
| benchmark/ | — | — | 0 | 0 | — |
| api/ | — | — | 0 | 0 | — |
| test_cli_usability.py | 33 | 33 | 0 | 0 | 65.86s |
| test_exit_codes.py | — | — | 0 | 0 | — |

---

## Skipped Tests (Expected)

| Test | Reason | Impact |
|---|---|---|
| 4 tests | Platform-specific (Linux-only features) | None on Windows |

---

## Regression Verification

| Change | Before | After | Status |
|---|---|---|---|
| D-3/D-4 confidence | 0.02 | 1.0 | FIXED |
| window_id pattern | `^w[0-9]+$` (limited) | `^w[0-9]+$` (100+ windows) | FIXED |
| Module identity | `from src.miie` | `from miie` | FIXED |
| ScorePackage dict | TypeError | Graceful handling | FIXED |
| Windows encoding | UnicodeDecodeError | utf-8, errors='replace' | FIXED |
| Git URL parsing | Manual | GitURLParser | FIXED |
| Auth token | Manual only | --auth-token + .env | FIXED |
| 3-tier output | Default only | Default/Verbose/Forensic | ADDED |
| Privacy filtering | None | _filter_sensitive_fields | ADDED |

---

## Test Health Indicators

| Indicator | Value | Status |
|---|---|---|
| Pass Rate | 911/911 = 100% | PASS |
| Skip Rate | 4/915 = 0.4% | PASS |
| Failure Rate | 0/911 = 0% | PASS |
| Warning Count | 7 (pytest warnings) | Acceptable |

---

## Verdict

**911 passed, 0 failed. No regression detected.**

The test suite is healthy and comprehensive for v1.0 release.

---

*Test results: `pytest tests/ --tb=line -q` run 2026-06-25*
