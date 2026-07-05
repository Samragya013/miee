# FUSC Phase 8 — Report Exposure Audit

**Program**: MIIE v1.0 First User Security & Experience Certification
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Category | Status |
|---|---|
| Developer internals | HIDDEN |
| Implementation details | HIDDEN |
| Private paths | HIDDEN |
| Temporary files | HIDDEN |
| Configuration | HIDDEN |
| Scientific internals | HIDDEN |

---

## Report Content Analysis

### JSON Report

| Field | Shown | Classification |
|---|---|---|
| repository_context | YES | ALLOWED |
| metric_dataframe | YES | ALLOWED |
| windows | YES | ALLOWED |
| detector_results | YES | ALLOWED |
| score_package | YES | ALLOWED |
| evidence_package | YES | ALLOWED |
| explanation_report | YES | ALLOWED |
| repo_id | FILTERED | CORRECT |
| local_path | FILTERED | CORRECT |
| temp_path | FILTERED | CORRECT |

### Terminal Report

| Section | Shown | Classification |
|---|---|---|
| Analysis Coverage | YES | ALLOWED |
| Integrity Findings | YES | ALLOWED |
| Confidence | YES | ALLOWED |
| Risk Assessment | YES | ALLOWED |
| Overall Verdict | YES | ALLOWED |
| Summary | YES | ALLOWED |
| Recommended Action | YES | ALLOWED |
| Reports Saved | YES | ALLOWED |

---

## Privacy Filtering

| Field | Default | Verbose | Forensic |
|---|---|---|---|
| repo_id | FILTERED | SHOWN | SHOWN |
| local_path | FILTERED | SHOWN | SHOWN |
| temp_path | FILTERED | SHOWN | SHOWN |

---

## Issues Found

| # | Issue | Severity | Status |
|---|---|---|---|
| 1 | JSON report contains full evidence | LOW | ALLOWED (user-generated) |

---

## Verdict

**REPORT EXPOSURE AUDIT: PASS**

Reports filter sensitive fields in default mode. Full evidence available in forensic mode.

---

*Report exposure audit completed 2026-06-26*
