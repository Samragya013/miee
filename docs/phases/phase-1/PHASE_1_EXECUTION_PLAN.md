# Phase 1 Execution Plan

**Document:** PHASE_1_EXECUTION_PLAN.md
**Phase:** Phase 1 — Repository Audit & Implementation Kickoff
**Source:** All Phase 1 audit deliverables
**Date:** 2026-06-29
**Status:** COMPLETE

---

## 1. Executive Summary

This document defines the execution plan for Phase 1 (Observation Core) of the v1.5 Observation Engine implementation. It specifies the exact steps, file changes, test requirements, and acceptance criteria for each PR.

**Phase 1 Scope:** Create observation models, observation store, adapter layer, extraction refactor, and pipeline integration. **15 work items**, **~80-100 hours**, **4 PRs**.

**Phase 1 Deliverable:** A working observation pipeline that extracts per-commit observations, stores them, and translates them to MetricDataFrame for existing detectors.

---

## 2. Phase 1 Objectives

| Objective | Success Criteria | Evidence |
|-----------|-----------------|----------|
| Observation models exist | `schemas/observation_models.py` created with 6 dataclasses | File exists, imports work |
| Deterministic IDs work | SHA-256 IDs are reproducible | Test: 100 runs produce identical IDs |
| Observation store works | `IObservationStore` Protocol + `ObservationStore` class | All Protocol methods implemented |
| Adapter layer works | `IAdapterLayer` Protocol + `AdapterLayer` class | Translation produces valid MetricDataFrame |
| Extraction refactored | `CommitExtractor` + `MetricExtractor` classes | Extraction produces ObservationStore |
| All tests pass | 730 existing + ~140 new = ~870 total | `poetry run pytest` all green |
| CI green | 9/9 jobs passing | GitHub Actions green |

---

## 3. PR Sequence

### PR-1: Observation Models + Store (Foundation)

**Scope:** Create observation models and observation store. No pipeline changes.

| File | Action | Lines | Tests |
|------|--------|-------|-------|
| `src/miie/schemas/observation_models.py` | CREATE | ~300 | — |
| `src/miie/processing/observation/__init__.py` | CREATE | ~5 | — |
| `src/miie/processing/observation/store.py` | CREATE | ~200 | — |
| `src/miie/contracts/interfaces.py` | MODIFY | +30 | — |
| `src/miie/contracts/errors.py` | MODIFY | +20 | — |
| `tests/unit/test_observation_models.py` | CREATE | — | ~20 |
| `tests/unit/test_observation_store.py` | CREATE | — | ~25 |

**Total new lines:** ~555
**Total new tests:** ~45

**Acceptance Criteria:**
- [ ] Observation dataclass: observation_id, commit_hash, metric_id, value, timestamp, author, files_changed
- [ ] ObservationWindow dataclass: window_id, observations, metadata
- [ ] ObservationCollection dataclass: windows, repository metadata
- [ ] CommitMetadata dataclass: hash, author, timestamp, message, files_changed, insertions, deletions
- [ ] MetricValue dataclass: metric_id, value, unit, extraction_method
- [ ] ExtractionResult dataclass: observations, metadata, extraction_time, source_type
- [ ] Deterministic ID function: SHA-256(source_type:source_id:metric_id)[:16]
- [ ] IObservationStore Protocol: add, get_by_id, get_by_commit, get_by_metric, get_all, count, clear
- [ ] ObservationStore class: in-memory dict-based, all Protocol methods
- [ ] ObservationError, ObservationStoreError added to contracts/errors.py
- [ ] All 45 new tests passing
- [ ] All 730 existing tests still passing
- [ ] CI green

**Estimated effort:** 20-25 hours

---

### PR-2: Adapter Layer + Extraction Refactor

**Scope:** Create adapter layer and refactor extraction to produce observations.

| File | Action | Lines | Tests |
|------|--------|-------|-------|
| `src/miie/processing/observation/adapter.py` | CREATE | ~250 | — |
| `src/miie/processing/extraction/__init__.py` | CREATE | ~5 | — |
| `src/miie/processing/extraction/commit_extractor.py` | CREATE | ~200 | — |
| `src/miie/processing/extraction/metric_extractor.py` | CREATE | ~200 | — |
| `src/miie/processing/extraction/engine.py` | CREATE | ~150 | — |
| `tests/unit/test_adapter_layer.py` | CREATE | — | ~20 |
| `tests/unit/test_commit_extractor.py` | CREATE | — | ~15 |
| `tests/unit/test_metric_extractor.py` | CREATE | — | ~15 |
| `tests/unit/test_extraction_engine_v2.py` | CREATE | — | ~20 |

**Total new lines:** ~805
**Total new tests:** ~70

**Acceptance Criteria:**
- [ ] IAdapterLayer Protocol: to_metric_dataframe(window), to_paired_observations(window)
- [ ] AdapterLayer class: translates ObservationWindow → MetricDataFrame
- [ ] CommitExtractor class: extracts per-commit observations from git log
- [ ] MetricExtractor class: extracts metric values per commit
- [ ] ExtractionEngine refactored: uses CommitExtractor + MetricExtractor, stores in ObservationStore
- [ ] Backward compatibility: existing MetricDataFrame output still works
- [ ] All 70 new tests passing
- [ ] All 730 existing tests still passing
- [ ] CI green

**Estimated effort:** 30-35 hours

---

### PR-3: Pipeline Integration + Window Builder

**Scope:** Integrate observation store into pipeline and add window building.

| File | Action | Lines | Tests |
|------|--------|-------|-------|
| `src/miie/orchestration/pipeline.py` | MODIFY | ~50 | — |
| `src/miie/processing/segmentation.py` | MODIFY | ~30 | — |
| `src/miie/cli.py` | MODIFY | +40 | — |
| `src/miie/config/loader.py` | MODIFY | +20 | — |
| `tests/integration/test_observation_pipeline.py` | CREATE | — | ~15 |
| `tests/contract/test_observation_interfaces.py` | CREATE | — | ~10 |

**Total new lines:** ~155
**Total new tests:** ~25

**Acceptance Criteria:**
- [ ] Pipeline wires observation store into stages
- [ ] Segmentation accepts ObservationStore
- [ ] CLI has --observation-level and --store-format flags
- [ ] Config has observation options
- [ ] Full pipeline test: git repo → extraction → observation store → windowing → MetricDataFrame → detection
- [ ] All 25 new tests passing
- [ ] All 730 existing tests still passing
- [ ] CI green

**Estimated effort:** 15-20 hours

---

### PR-4: Cleanup + Documentation

**Scope:** Delete empty packages, update documentation, final verification.

| File | Action | Lines | Tests |
|------|--------|-------|-------|
| `src/miie/common/__init__.py` | DELETE | -13 | — |
| `src/miie/detection/__init__.py` | DELETE | -13 | — |
| `src/miie/interface/__init__.py` | DELETE | -13 | — |
| `README.md` | MODIFY | +20 | — |
| `docs/architecture/observation_engine/OBSERVATION_MODELS.md` | CREATE | ~100 | — |
| `docs/architecture/observation_engine/OBSERVATION_STORE.md` | CREATE | ~80 | — |
| `docs/architecture/observation_engine/ADAPTER_LAYER.md` | CREATE | ~80 | — |

**Total new lines:** ~254
**Total deleted lines:** -39

**Acceptance Criteria:**
- [ ] Empty packages deleted (common/, detection/, interface/)
- [ ] Import tests still pass after deletion
- [ ] Documentation created for observation models, store, adapter
- [ ] README updated with v1.5 features
- [ ] All tests passing
- [ ] CI green
- [ ] No regressions

**Estimated effort:** 5-10 hours

---

## 4. Execution Timeline

### 4.1 Gantt Chart (Text)

```
Week 1: PR-1 (Observation Models + Store)
  Mon-Tue: Create observation models (schemas/observation_models.py)
  Wed-Thu: Create observation store (processing/observation/store.py)
  Fri: Write tests, run CI, verify

Week 2: PR-2 (Adapter Layer + Extraction Refactor)
  Mon-Tue: Create adapter layer (processing/observation/adapter.py)
  Wed: Create CommitExtractor + MetricExtractor
  Thu: Refactor ExtractionEngine
  Fri: Write tests, run CI, verify

Week 3: PR-3 (Pipeline Integration + Window Builder)
  Mon-Tue: Integrate observation store into pipeline
  Wed: Add CLI flags
  Thu: Write integration tests
  Fri: Run CI, verify

Week 4: PR-4 (Cleanup + Documentation)
  Mon: Delete empty packages
  Tue-Wed: Write documentation
  Thu: Final verification
  Fri: Phase 1 complete
```

### 4.2 Milestones

| Milestone | Target Date | Criteria |
|-----------|-------------|----------|
| M1: Observation models created | Week 1, Day 2 | All 6 dataclasses exist and import |
| M2: Observation store created | Week 1, Day 4 | IObservationStore + ObservationStore working |
| M3: PR-1 merged | Week 1, Friday | All tests pass, CI green |
| M4: Adapter layer created | Week 2, Day 2 | Translation works correctly |
| M5: Extraction refactored | Week 2, Day 4 | Extraction produces ObservationStore |
| M6: PR-2 merged | Week 2, Friday | All tests pass, CI green |
| M7: Pipeline integrated | Week 3, Day 2 | Full pipeline works with observations |
| M8: PR-3 merged | Week 3, Friday | All tests pass, CI green |
| M9: Phase 1 complete | Week 4, Friday | All objectives met, documentation done |

---

## 5. Quality Gates

### 5.1 Per-PR Quality Gates

| Gate | Criteria | Evidence |
|------|----------|----------|
| Test pass rate | 100% (0 failures) | `poetry run pytest` output |
| New test count | ≥ minimum specified | Test count from pytest output |
| Existing test count | 730 (no regressions) | Test count from pytest output |
| CI status | All 9 jobs green | GitHub Actions status |
| Code style | Black, isort, flake8 pass | Pre-commit hooks |
| Type checking | mypy pass | mypy output |
| PR size | ≤ 500 lines changed | `git diff --stat` |
| File count | ≤ 3 new + 2 modified | `git status` |

### 5.2 Phase 1 Quality Gates

| Gate | Criteria | Evidence |
|------|----------|----------|
| All PRs merged | 4/4 merged | GitHub PR status |
| All tests pass | ~870 total (730 existing + ~140 new) | `poetry run pytest` |
| CI green | 9/9 jobs passing | GitHub Actions |
| No regressions | 0 existing test failures | Test comparison before/after |
| Documentation complete | 3 new docs created | File existence check |
| Empty packages deleted | common/, detection/, interface/ removed | `ls src/miie/` |
| Phase 1 objectives met | All 7 objectives achieved | Evidence collected |

---

## 6. Risk Mitigation Plan

### 6.1 Per-PR Risk Mitigation

| PR | Risk | Mitigation | Trigger |
|----|------|------------|---------|
| PR-1 | Observation model design wrong | Review against IMS §4.1 before coding | Design review |
| PR-1 | Deterministic ID collision | SHA-256 16-char hex = 2^64 space; collision negligible | N/A |
| PR-2 | Adapter translation wrong | Compare adapter output with direct extraction | Test comparison |
| PR-2 | Extraction refactor breaks tests | Run full test suite after each change | Test failure |
| PR-3 | Pipeline integration fails | Incremental integration; test after each step | Test failure |
| PR-3 | CLI flags break existing commands | Test all 10 existing commands | Test failure |
| PR-4 | Deleting packages breaks imports | Run import tests after deletion | Test failure |

### 6.2 Rollback Strategy

| Scenario | Action | Recovery |
|----------|--------|----------|
| PR fails CI | Fix issues, re-push | Re-run CI |
| PR breaks existing tests | Revert PR, investigate | `git revert` |
| Phase 1 exceeds timeline | Prioritize PR-1 and PR-2; defer PR-3 and PR-4 | Scope reduction |
| Architecture docs wrong | Stop, review, update docs, resume | Documentation update |

---

## 7. Success Criteria

### 7.1 Phase 1 is COMPLETE when:

- [ ] All 4 PRs merged to main
- [ ] ~870 tests passing (730 existing + ~140 new)
- [ ] CI green (9/9 jobs)
- [ ] No regressions in existing functionality
- [ ] Observation models, store, adapter, extraction all working
- [ ] Pipeline integrated with observation store
- [ ] CLI has observation-level flags
- [ ] Empty packages deleted
- [ ] Documentation created
- [ ] Phase 1 objectives all met

### 7.2 Phase 1 is NOT COMPLETE when:

- Any existing test fails
- CI has any failing job
- Observation models are incomplete
- Adapter layer doesn't produce valid MetricDataFrame
- Extraction doesn't produce ObservationStore
- Pipeline doesn't wire observation store
- Documentation is missing

---

## 8. Handoff to Phase 2

### 8.1 What Phase 2 Receives

| Artifact | Status | Notes |
|----------|--------|-------|
| Observation models | ✅ CREATED | schemas/observation_models.py |
| Observation store | ✅ CREATED | processing/observation/store.py |
| Adapter layer | ✅ CREATED | processing/observation/adapter.py |
| CommitExtractor | ✅ CREATED | processing/extraction/commit_extractor.py |
| MetricExtractor | ✅ CREATED | processing/extraction/metric_extractor.py |
| ExtractionEngine | ✅ REFACTORED | processing/extraction/engine.py |
| Pipeline integration | ✅ COMPLETE | orchestration/pipeline.py modified |
| All tests | ✅ PASSING | ~870 tests |
| CI | ✅ GREEN | 9/9 jobs |

### 8.2 What Phase 2 Needs to Do

1. Create ObservationWindow builder (accepts ObservationStore, returns ObservationCollection)
2. Implement time-based and commit-count windowing strategies
3. Add minimum window gate (< 2 windows → abort)
4. Integrate windowing into pipeline
5. Write windowing tests

---

*Generated by Phase 1 Execution Plan — 2026-06-29*
