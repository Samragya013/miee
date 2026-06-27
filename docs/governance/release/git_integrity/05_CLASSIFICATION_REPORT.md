# GRIMC Phase 5 — Classification Report

**Program**: MIIE v1.0 Git Repository Integrity & Metadata Certification
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Classification | Count |
|---|---|
| KEEP | 0 |
| ARCHIVE | 1 |
| REMOVE_FROM_RELEASE | 1 |
| CONVERT_TO_PLAIN_DIRECTORY | 12 |
| CONVERT_TO_BENCHMARK_FIXTURE | 0 |
| CONVERT_TO_EXAMPLE | 0 |
| MANUAL_REVIEW | 0 |

---

## Classification Details

### archive/debug_test
**Classification**: REMOVE_FROM_RELEASE
**Evidence**: No dependencies, orphaned submodule reference
**Risk**: LOW
**Rollback**: `git checkout archive/debug_test`

### archive/cli_test_repo
**Classification**: ARCHIVE
**Evidence**: Referenced by tests, but in archive directory
**Risk**: LOW
**Rollback**: `git checkout archive/cli_test_repo`

### benchmarks/datasets/candidates/candidate_001-011
**Classification**: CONVERT_TO_PLAIN_DIRECTORY
**Evidence**: Intentional benchmark fixtures, but stored as nested repos
**Risk**: MEDIUM
**Rollback**: `git checkout benchmarks/datasets/candidates/candidate_001` (and others)

### benchmarks/tmp/metric-drift/candidate_001-011
**Classification**: CONVERT_TO_PLAIN_DIRECTORY
**Evidence**: Copies of benchmark fixtures, stored as nested repos
**Risk**: LOW
**Rollback**: `git checkout benchmarks/tmp/metric-drift/candidate_001` (and others)

### archive/test_output_multiple/candidate_001
**Classification**: REMOVE_FROM_RELEASE
**Evidence**: Test output, not needed for release
**Risk**: LOW
**Rollback**: `git checkout archive/test_output_multiple/candidate_001`

### archive/test_output_single/candidate_001
**Classification**: REMOVE_FROM_RELEASE
**Evidence**: Test output, not needed for release
**Risk**: LOW
**Rollback**: `git checkout archive/test_output_single/candidate_001`

---

## Verdict

**CLASSIFICATION REPORT: COMPLETE**

All nested repositories classified. 12 convertible, 2 removable, 1 archived.

---

*Classification report completed 2026-06-26*
