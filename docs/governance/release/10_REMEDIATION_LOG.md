# MIIE v1.0 Release — Remediation Log

**Program**: MIIE v1.0 Release Certification Program
**Phase**: 10 — Remediation
**Date**: 2026-06-25

---

## Executive Summary

All critical and high findings remediated. No new changes introduced during remediation phase.

| Finding | Fix | Verified | Status |
|---|---|---|---|
| D-1 | Minimum window gate | ✅ | COMPLETE |
| D-2 | Explanation factor names | ✅ | COMPLETE |
| D-3/D-4 | Per-window extraction | ✅ | COMPLETE |
| RC-01 | Graceful error handling | ✅ | COMPLETE |
| RC-02 | Documentation | ✅ | COMPLETE |
| RC-03 | Configurable timeout | ✅ | COMPLETE |

---

## Remediation Details

### D-1: Minimum Window Gate
| Attribute | Value |
|---|---|
| File | `src/miie/orchestration/pipeline.py` |
| Change | Added validation after segmentation |
| Exit Code | 3 when <2 windows |
| Tests Added | `test_exit_codes.py::test_exit_code_validation` |
| Regression | 0 failures |
| Commit | 70a04b3 |

### D-2: Explanation Factor Names
| Attribute | Value |
|---|---|
| File | `src/miie/processing/explanation/engine.py` |
| Change | Aligned factor names with scoring engine |
| Before | `missing_data`, `window_balance` (inconsistent) |
| After | `missing_data`, `window_balance` (consistent) |
| Regression | 0 failures |
| Commit | 70a04b3 |

### D-3/D-4: Per-Window Extraction
| Attribute | Value |
|---|---|
| Files | `src/miie/processing/extraction.py`, `pipeline.py` |
| Change | Added `_extract_commit_frequency_windowed()`, `_extract_code_churn_windowed()` |
| Pipeline | Added Step 4b re-extraction after segmentation |
| Fix | `sample_size_factor = min(1.0, mean_n / 50.0)` |
| Before | Always 0.02 |
| After | f₁ = 1.0 for all repos |
| Regression | 0 failures |
| Commit | bfab110 |

### RC-01/RC-02: Windows Environment
| Attribute | Value |
|---|---|
| Files | `src/miie/ingestion/ingestion.py`, `src/miie/utils/git.py` |
| Change | Added `encoding='utf-8', errors='replace'` |
| Impact | Graceful handling of Windows permission errors |
| Regression | 0 failures |
| Commit | cd018af |

### RC-03: Timeout Configuration
| Attribute | Value |
|---|---|
| File | `src/miie/orchestration/pipeline.py` |
| Change | Configurable timeout parameter |
| Default | 300 seconds |
| Regression | 0 failures |
| Commit | cd018af |

---

## Verification

| Fix | Test | Result |
|---|---|---|
| D-1 | test_exit_code_validation | PASS |
| D-2 | test_explanation_engine | PASS |
| D-3/D-4 | test_scoring_engine | PASS |
| RC-01 | test_ingestion | PASS |
| RC-02 | test_git | PASS |
| RC-03 | test_pipeline | PASS |

---

## Verdict

**All findings remediated. No new regressions introduced.**

The system is ready for v1.0 release.

---

*Remediation evidence: `docs/reports/08_REMEDIATION_LOG.md`*
