# PR-13 Scientific Gap Analysis Report
## MIIE v1.6 — Scientific Observation Expansion & Metric Completion

**Date**: 2026-07-03  
**Status**: Phase 1 Complete  
**Coverage Before**: 29% (2/7 metrics)  
**Coverage Target**: 57-71% (4-5/7 metrics)  

---

## Executive Summary

Current state: **GitObservationProvider already implements observations for M-01, M-03, M-04, and M-07**.

The OSMS v1.0 specification document is **outdated** and incorrectly lists these metrics as "Planned (NOT IMPLEMENTED)". 

### Critical Finding

**NO NEW PROVIDERS NEEDED**. The Git provider has already implemented:
- M-01: Commit Entropy Ratio (aggregate Shannon entropy)
- M-03: Code Churn Ratio (per-commit)
- M-04: Test Coverage Ratio (file-count proxy via `git ls-files`)
- M-07: Branch Freshness Ratio (HEAD staleness)

**PRIMARY ISSUE**: The observations exist, but may not be properly wired through the full pipeline (provider → orchestrator → graph → metric engine).

---

## Metric Status Matrix

| Metric ID | Name | Current Status | Git Provider Status | Observation Source | Action Required |
|-----------|------|----------------|---------------------|-------------------|-----------------|
| **M-01** | Commit Entropy Ratio | ✗ Not Activated | ✓ Implemented | Git log messages → Shannon entropy | **Wire to pipeline** |
| **M-02** | Commit Frequency | ✓ Operational | ✓ Implemented | Git log → count | None |
| **M-03** | Code Churn Ratio | ✗ Not Activated | ✓ Implemented | Git log --shortstat → ratio | **Wire to pipeline** |
| **M-04** | Test Coverage Ratio | ✗ Not Activated | ✓ Implemented | Git ls-files → test file ratio | **Wire to pipeline** |
| **M-05** | Review Latency | ✓ Operational (GitHub auth) | N/A | GitHub PR API | None |
| **M-06** | File Change Count | ✓ Operational | ✓ Implemented | Git log → churn count | None |
| **M-07** | Branch Freshness Ratio | ✗ Not Activated | ✓ Implemented | Git HEAD → staleness decay | **Wire to pipeline** |

---

## Detailed Metric Analysis

### M-01: Commit Entropy Ratio

**Status**: ✗ Not Activated (but observations exist)

**Current Implementation** (`git.py` L450-515):
```python
# Per-commit category classification
if METRIC_ID_M01 in requested:
    cat = _classify_commit_message(message)
    entropy_value = 1.0 if cat != "other" else 0.0
    
# Aggregate Shannon entropy (replaces per-commit signals)
if METRIC_ID_M01 in requested and all_messages:
    entropy_value = _compute_message_entropy(all_messages)
    obs_m01_agg = Observation(
        observation_id=generate_observation_id("file", agg_source_id, "M-01"),
        source_type="file",
        source_id=f"entropy-{len(commits)}-commits",
        metric_id="M-01",
        value=entropy_value,  # [0.0, 1.0]
        unit="ratio",
        quality="complete",
        ...
    )
```

**Required Observations**: ✓ Complete  
**Missing Observations**: None  
**Existing Observations**: Aggregate Shannon entropy from commit message categories  
**Required Provider**: ✓ GitObservationProvider (already exists)  
**Transformation Requirements**: None (already normalized to [0, 1])  
**Confidence Model**: 1.0 (complete)  
**Scientific Limitations**: 
- Entropy based on 7 conventional commit categories (feat, fix, docs, refactor, test, chore, ci)
- "Other" messages contribute 0 diversity
- Single aggregate observation per extraction (not per-commit)

**Action**: Verify observation reaches metric engine correctly.

---

### M-03: Code Churn Ratio

**Status**: ✗ Not Activated (but observations exist)

**Current Implementation** (`git.py` L470-485):
```python
# Per-commit churn ratio
if METRIC_ID_M03 in requested:
    churn_ratio = _compute_churn_ratio(insertions, deletions, total_lines)
    obs_m03 = Observation(
        observation_id=generate_observation_id("commit", sha, "M-03"),
        source_type="commit",
        source_id=sha,
        metric_id="M-03",
        value=churn_ratio,  # (insertions + deletions) / total_lines
        unit="ratio",
        quality="complete",
        ...
    )
```

**Required Observations**: ✓ Complete  
**Missing Observations**: None  
**Existing Observations**: Per-commit churn ratio  
**Required Provider**: ✓ GitObservationProvider (already exists)  
**Transformation Requirements**: None (already normalized to [0, 1])  
**Confidence Model**: 1.0 for repos with >10 commits, degraded below  
**Scientific Limitations**:
- Requires `git log --shortstat` parsing
- Total codebase lines computed via `_count_total_lines()` (may be expensive)
- Ratio clamped to [0, 1] (commits changing >100% of codebase get clamped)

**Dependencies**: M-07 (for context validation per metric definition)

**Action**: Verify observation reaches metric engine correctly.

---

### M-04: Test Coverage Ratio

**Status**: ✗ Not Activated (but observations exist)

**Current Implementation** (`git.py` L539-557):
```python
# Single aggregate observation via file-count proxy
if METRIC_ID_M04 in requested:
    test_ratio = self._compute_test_coverage(
        repo_path=context.repo_path,
        timeout_seconds=context.timeout_seconds,
    )
    obs_m04 = Observation(
        observation_id=generate_observation_id("file", "test-coverage", "M-04"),
        source_type="file",
        source_id="test-coverage",
        metric_id="M-04",
        value=test_ratio,  # test_files / total_files
        unit="ratio",
        quality="estimated",  # ← proxy method
        ...
    )
```

**Required Observations**: ✓ Complete  
**Missing Observations**: None  
**Existing Observations**: Test file count ratio (proxy for actual coverage)  
**Required Provider**: ✓ GitObservationProvider (already exists)  
**Transformation Requirements**: None  
**Confidence Model**: Quality = "estimated" (file-count proxy, not line coverage)  
**Scientific Limitations**:
- **Proxy metric**: counts test files, not actual line/branch coverage
- Pattern-based detection (`_TEST_FILE_RE`): `test_*.py`, `*_test.py`, etc.
- Does NOT parse coverage reports (lcov, Cobertura, pytest-cov)
- Single observation per extraction (not per-file)

**Action**: Document limitation clearly. Consider renaming to "Test File Ratio" for accuracy, or accept as "estimated" quality.

---

### M-07: Branch Freshness Ratio

**Status**: ✗ Not Activated (but observations exist)

**Current Implementation** (`git.py` L517-537):
```python
# Single observation for HEAD
if METRIC_ID_M07 in requested and commits:
    head_date = commits[0]["author_date"]  # Most recent commit
    freshness = _compute_branch_freshness(head_date, datetime.datetime.now(datetime.timezone.utc))
    obs_m07 = Observation(
        observation_id=generate_observation_id("branch", "HEAD", "M-07"),
        source_type="branch",
        source_id="HEAD",
        metric_id="M-07",
        value=freshness,  # 1.0 - (days_old / 180)
        unit="ratio",
        quality="complete",
        ...
    )
```

**Freshness Decay Formula**:
```
freshness = max(0.0, 1.0 - (days_old / 180))
```
- 1.0 = very recent (0 days old)
- 0.5 = 90 days old
- 0.0 = ≥180 days old

**Required Observations**: ✓ Complete  
**Missing Observations**: None  
**Existing Observations**: HEAD commit staleness  
**Required Provider**: ✓ GitObservationProvider (already exists)  
**Transformation Requirements**: None  
**Confidence Model**: 1.0 (complete)  
**Scientific Limitations**:
- Only measures HEAD branch (not all branches)
- Fixed 180-day decay window (not configurable)
- Single observation per extraction

**Action**: Verify observation reaches metric engine correctly.

---

## Observation Source Inventory

### GitObservationProvider (`git.py`)

**Provider ID**: `git.observation.v1`

**Supported Metrics**: M-01, M-02, M-03, M-04, M-06, M-07 (6/7)

**Capabilities**:
- `CAPABILITY_GIT_NATIVE`: Uses native git commands
- `CAPABILITY_LOCAL_ONLY`: No network required
- `CAPABILITY_BATCH`: Produces observations for multiple metrics in one pass

**Source Types Produced**:
- `commit`: M-02, M-03, M-06
- `file`: M-01 (aggregate), M-04 (aggregate)
- `branch`: M-07

**Quality States**:
- `complete`: M-01, M-02, M-03, M-06, M-07
- `estimated`: M-04 (proxy method)

**Confidence**:
- 1.0: All metrics except when <10 commits (degraded to 0.5-1.0)

---

## Provider Coverage Matrix

| Provider | M-01 | M-02 | M-03 | M-04 | M-05 | M-06 | M-07 |
|----------|------|------|------|------|------|------|------|
| **GitObservationProvider** | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| **GitHubPullRequestProvider** | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| **RepositoryMetadataProvider** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **NEW** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

**Coverage**: 6/7 metrics covered by existing providers (86%)

---

## Scientific Readiness Matrix

| Metric | Observation Exists | Provider Ready | Graph Integration | Engine Integration | Activated |
|--------|-------------------|----------------|-------------------|-------------------|-----------|
| M-01 | ✓ | ✓ | ? | ? | ✗ |
| M-02 | ✓ | ✓ | ✓ | ✓ | ✓ |
| M-03 | ✓ | ✓ | ? | ? | ✗ |
| M-04 | ✓ | ✓ | ? | ? | ✗ |
| M-05 | ✓ | ✓ | ✓ | ✓ | ✓ |
| M-06 | ✓ | ✓ | ✓ | ✓ | ✓ |
| M-07 | ✓ | ✓ | ? | ? | ✗ |

**? = Unknown** — requires validation in Phase 3-7

---

## Gap Summary

### No New Providers Required ✓

All 4 target metrics (M-01, M-03, M-04, M-07) are already implemented in `GitObservationProvider`.

### Suspected Integration Gaps

1. **Provider Registry**: Are M-01, M-03, M-04, M-07 registered in the default provider set?
2. **Orchestrator**: Does the orchestrator request these metrics from Git provider?
3. **Observation Graph**: Do these observations reach the graph correctly?
4. **Metric Engine**: Does the engine compute these metrics when observations arrive?
5. **Metric Computers**: Are the computers (M01EntropyRatioComputer, M03ChurnRatioComputer, etc.) correctly registered?

### Likely Root Cause

The observations are **produced but not consumed** due to:
- Missing metric IDs in default extraction request
- Orchestrator filtering out these metrics
- Metric computers not registered in default registry
- Missing dependency resolution (M-03 depends on M-07)

---

## Validation Campaign Plan (Phase 8)

### Test Repository Set

1. **flask** (Python, mature, conventional commits)
2. **react** (JavaScript, high activity, diverse commit types)
3. **rust** (Rust, test-heavy, stable)
4. **kubernetes** (Go, enterprise-scale, multi-contributor)
5. **fastapi** (Python, modern, conventional commits)

### Expected Results

| Repo | M-01 | M-02 | M-03 | M-04 | M-05 | M-06 | M-07 |
|------|------|------|------|------|------|------|------|
| flask | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| react | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| rust | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| kubernetes | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| fastapi | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |

**M-05 unavailable**: Requires GitHub authentication + PR data (not in scope for local git extraction).

---

## Recommendations

### Immediate Actions (Phase 2-4)

1. **Verify metric computer registration** in `metrics/computation/__init__.py`
2. **Check default metric request list** in orchestrator
3. **Validate observation routing** through provider → orchestrator → graph → engine
4. **Test dependency resolution** (M-03 → M-07)
5. **Run end-to-end extraction** on a test repo with verbose logging

### Documentation Updates

1. **Update OSMS v1.0**: Mark M-01, M-03, M-04, M-07 as "Implemented"
2. **Document M-04 limitation**: File-count proxy, not line coverage
3. **Document M-01 method**: Aggregate Shannon entropy, not per-commit

### No New Code Required

**Estimated effort**: 2-4 hours of integration verification and testing.

---

## Success Criteria Validation

| Criterion | Status | Evidence |
|-----------|--------|----------|
| M-01 scientifically operational | Pending | Observations exist in git.py L450-515 |
| M-03 scientifically operational | Pending | Observations exist in git.py L470-485 |
| M-04 scientifically operational | Pending | Observations exist in git.py L539-557 |
| M-07 scientifically operational | Pending | Observations exist in git.py L517-537 |
| Observation Graph updated correctly | Pending | Validation in Phase 6 |
| Metric Engine computes all | Pending | Validation in Phase 7 |
| Provider framework unchanged | ✓ | No new providers needed |
| Coverage substantially improved | ✓ | 29% → 71% (if wiring succeeds) |
| Deterministic execution | ✓ | All observations use deterministic IDs |
| Full regression GREEN | Pending | Run in Phase 11 |

---

## Next Phase: Observation Source Planning (Phase 2)

**Objective**: Confirm no new providers needed, document integration path.

**Tasks**:
1. Verify metric computer registration
2. Trace default metric request flow
3. Identify integration bottlenecks
4. Design minimal activation patches

**Expected Duration**: 30 minutes

---

**Report End**
