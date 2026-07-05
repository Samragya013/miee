# GRIMC Phase 6 — Remediation Plan

**Program**: MIIE v1.0 Git Repository Integrity & Metadata Certification
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Action | Count |
|---|---|
| Convert to plain directory | 12 |
| Remove from release | 3 |
| Archive | 1 |

---

## Remediation Plan

### Step 1: Convert benchmark fixtures to plain directories

**Current**: `benchmarks/datasets/candidates/candidate_001-011` are nested Git repos
**Target**: Convert to plain directories with just the data files
**Reason**: Reduce clone size, remove orphaned submodule references
**Risk**: MEDIUM
**Impact**: Benchmark tests may need adjustment
**Rollback**: `git checkout benchmarks/datasets/candidates/candidate_001` (and others)

### Step 2: Convert metric-drift copies to plain directories

**Current**: `benchmarks/tmp/metric-drift/candidate_001-011` are nested Git repos
**Target**: Convert to plain directories
**Reason**: Reduce clone size, remove orphaned submodule references
**Risk**: LOW
**Impact**: None
**Rollback**: `git checkout benchmarks/tmp/metric-drift/candidate_001` (and others)

### Step 3: Remove test outputs from release

**Current**: `archive/test_output_multiple/candidate_001` and `archive/test_output_single/candidate_001` are nested repos
**Target**: Remove from Git tracking
**Reason**: Not needed for release
**Risk**: LOW
**Impact**: None
**Rollback**: `git checkout archive/test_output_multiple/candidate_001`

### Step 4: Archive debug_test

**Current**: `archive/debug_test` is a nested repo
**Target**: Convert to plain directory
**Reason**: No dependencies, orphaned submodule reference
**Risk**: LOW
**Impact**: None
**Rollback**: `git checkout archive/debug_test`

---

## Verdict

**REMEDIATION PLAN: COMPLETE**

4 steps identified. All low/medium risk.

---

*Remediation plan completed 2026-06-26*
