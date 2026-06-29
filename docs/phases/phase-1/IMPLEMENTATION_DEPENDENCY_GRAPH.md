# Implementation Dependency Graph

**Document:** IMPLEMENTATION_DEPENDENCY_GRAPH.md
**Phase:** Phase 1 — Repository Audit & Implementation Kickoff
**Source:** Codebase analysis + IMS v1.0 dependency mapping
**Date:** 2026-06-29
**Status:** COMPLETE

---

## 1. Executive Summary

This document maps every implementation dependency for v1.5 Observation Engine. Dependencies are categorized as: **hard** (blocks next phase), **soft** (recommended but not blocking), and **optional** (nice-to-have). The graph ensures no circular dependencies and identifies the critical path.

**Critical Path:** Observation Models → Observation Store → CommitExtractor → MetricExtractor → Adapter Layer → Pipeline Integration

---

## 2. Dependency Categories

### 2.1 Hard Dependencies (Must Complete Before Next Phase)

| Phase | Depends On | Reason |
|-------|-----------|--------|
| Phase 1: Observation Core | None | Foundation — no prerequisites |
| Phase 2: Observation Storage | Phase 1 | Store requires observation models |
| Phase 3: Extraction Refactor | Phase 1, 2 | Extractors need models + store |
| Phase 4: Window Builder | Phase 1, 2 | Windows need models + store |
| Phase 5: Detector Refactor | Phase 1, 2, 3, 4 | Detectors need adapter (needs all prior) |
| Phase 6: Evidence Refactor | Phase 1, 2, 3 | Evidence needs extraction results |
| Phase 7: Scoring Refactor | Phase 1, 2, 3, 5 | Scoring needs detector output |
| Phase 8: Explanation Integration | Phase 1, 2, 3, 5, 7 | Explanation needs scoring |
| Phase 9: Benchmark Upgrade | Phase 1, 2, 3, 5 | Benchmarks need detector output |
| Phase 10: CLI Integration | Phase 1, 2, 3, 5, 7, 8 | CLI needs all engines |
| Phase 11: Scientific Validation | Phase 1, 2, 3, 5, 9 | Validation needs benchmarks |
| Phase 12: Performance Optimization | Phase 1, 2, 3, 5, 7, 8, 10 | Optimization needs full pipeline |
| Phase 13: Documentation Sync | All prior | Docs reflect final state |
| Phase 14: Release Candidate | All prior | RC needs everything |
| Phase 15: v1.5 Release | Phase 14 | Release needs RC approval |

### 2.2 Soft Dependencies (Recommended But Not Blocking)

| Phase | Soft Dependency | Reason |
|-------|----------------|--------|
| Phase 3: Extraction Refactor | Phase 2 (store) | Can work without store but less efficient |
| Phase 4: Window Builder | Phase 3 (extraction) | Can accept raw observations |
| Phase 5: Detector Refactor | Phase 4 (windows) | Can accept observation store directly |
| Phase 6: Evidence Refactor | Phase 5 (detectors) | Can use old detector output format |
| Phase 7: Scoring Refactor | Phase 6 (evidence) | Can use old evidence format |
| Phase 8: Explanation Integration | Phase 7 (scoring) | Can use old scoring format |
| Phase 9: Benchmark Upgrade | Phase 5 (detectors) | Can benchmark old format |
| Phase 10: CLI Integration | Phase 8 (explanation) | Can integrate partial pipeline |

### 2.3 Optional Dependencies (Nice-to-Have)

| Phase | Optional Dependency | Reason |
|-------|-------------------|--------|
| Phase 12: Performance Optimization | Phase 11 (validation) | Can optimize without validation |
| Phase 13: Documentation Sync | Phase 12 (optimization) | Docs can reflect pre-optimization |
| Phase 14: Release Candidate | Phase 13 (docs) | RC can have draft docs |

---

## 3. Critical Path Analysis

### 3.1 Critical Path (Longest Dependency Chain)

```
Phase 1 (Observation Core)
  → Phase 2 (Observation Storage)
    → Phase 3 (Extraction Refactor)
      → Phase 4 (Window Builder)
        → Phase 5 (Detector Refactor)
          → Phase 7 (Scoring Refactor)
            → Phase 8 (Explanation Integration)
              → Phase 10 (CLI Integration)
                → Phase 12 (Performance Optimization)
                  → Phase 13 (Documentation Sync)
                    → Phase 14 (Release Candidate)
                      → Phase 15 (v1.5 Release)
```

**Critical Path Length:** 13 phases (Phase 6, 9, 11 are parallel branches)

### 3.2 Parallel Branches

```
Branch A (Evidence):
  Phase 3 → Phase 6 (Evidence Refactor)

Branch B (Benchmarks):
  Phase 5 → Phase 9 (Benchmark Upgrade)
    → Phase 11 (Scientific Validation)

Branch C (Explanation):
  Phase 5 → Phase 7 → Phase 8 (Explanation Integration)
```

**Branch A:** Can run in parallel with Branch B and C
**Branch B:** Can run in parallel with Branch A and C
**Branch C:** Must wait for Phase 5, then runs in parallel with A and B

### 3.3 Convergence Points

| Convergence | Phases Merging | Next Phase |
|-------------|---------------|------------|
| CP-1 | Phase 1 → Phase 2 | Phase 3 |
| CP-2 | Phase 3 → Phase 4 | Phase 5 |
| CP-3 | Phase 5 → Phase 7 | Phase 8 |
| CP-4 | Phase 8 → Phase 10 | Phase 12 |
| CP-5 | Phase 6, 9, 11 → Phase 13 | Phase 14 |

---

## 4. Module Dependency Map

### 4.1 New Modules (v1.5)

```
schemas/observation_models.py
  ├── Observation
  ├── ObservationWindow
  ├── ObservationCollection
  ├── CommitMetadata
  ├── MetricValue
  └── ExtractionResult

processing/observation/store.py
  ├── IObservationStore (interface)
  └── ObservationStore (implementation)
  └── Depends on: schemas/observation_models.py

processing/observation/adapter.py
  ├── IAdapterLayer (interface)
  └── AdapterLayer (implementation)
  └── Depends on: schemas/observation_models.py, schemas/models.py

processing/extraction/commit_extractor.py
  ├── CommitExtractor
  └── Depends on: schemas/observation_models.py, processing/observation/store.py

processing/extraction/metric_extractor.py
  ├── MetricExtractor
  └── Depends on: schemas/observation_models.py, processing/observation/store.py

processing/extraction/engine.py
  ├── ExtractionEngine (refactored)
  └── Depends on: commit_extractor.py, metric_extractor.py, store.py
```

### 4.2 Modified Modules (v1.5)

```
contracts/interfaces.py
  ├── +IObservationStore
  └── +IAdapterLayer

contracts/errors.py
  ├── +ObservationError
  └── +ObservationStoreError

orchestration/pipeline.py
  └── Modify: wire observation store into pipeline stages

processing/segmentation.py
  └── Modify: accept ObservationStore instead of MetricDataFrame

cli.py
  └── Modify: add observation-level flags

config/loader.py
  └── Modify: add observation config options
```

### 4.3 Unchanged Modules (v1.5)

```
processing/detection/  (all 8 files)
  └── Adapters handle translation — no changes needed

processing/scoring/    (all 3 files)
  └── Adapters handle translation — no changes needed

processing/explanation/ (all 3 files)
  └── Adapters handle translation — no changes needed

processing/reporting/  (all 3 files)
  └── Adapters handle translation — no changes needed

processing/benchmark/  (1 file)
  └── Benchmark evolution deferred

processing/evaluation/ (1 file)
  └── No changes needed

schemas/models.py      (1 file)
  └── Existing models unchanged — new models in new file

utils/                 (all 3 files)
  └── No changes needed

api/                   (all 5 files)
  └── No changes needed

storage/               (reserved for v2.0)
  └── DO NOT MODIFY
```

---

## 5. Import Dependency Graph

### 5.1 Current Import Structure

```
miie.cli → miie.orchestration.pipeline
miie.orchestration.pipeline → miie.processing.*
miie.processing.* → miie.schemas.models
miie.processing.* → miie.contracts.interfaces
miie.processing.* → miie.contracts.errors
miie.processing.* → miie.config.loader
miie.schemas.models → (stdlib only)
miie.contracts.* → (stdlib only)
miie.config.* → (stdlib only)
miie.utils.* → (stdlib + gitpython)
```

### 5.2 v1.5 Import Structure (Additions)

```
miie.schemas.observation_models → (stdlib only)
miie.processing.observation.store → miie.schemas.observation_models
miie.processing.observation.adapter → miie.schemas.observation_models
miie.processing.observation.adapter → miie.schemas.models
miie.processing.extraction.commit_extractor → miie.schemas.observation_models
miie.processing.extraction.commit_extractor → miie.processing.observation.store
miie.processing.extraction.metric_extractor → miie.schemas.observation_models
miie.processing.extraction.metric_extractor → miie.processing.observation.store
miie.processing.extraction.engine → miie.processing.extraction.commit_extractor
miie.processing.extraction.engine → miie.processing.extraction.metric_extractor
miie.contracts.interfaces → miie.schemas.observation_models (for type hints)
miie.contracts.errors → (no change)
```

### 5.3 Circular Dependency Check

**No circular dependencies detected.** The dependency graph is a DAG (Directed Acyclic Graph):

```
schemas/observation_models.py (leaf — no miie imports)
  ↑
processing/observation/store.py
  ↑
processing/extraction/commit_extractor.py
processing/extraction/metric_extractor.py
  ↑
processing/extraction/engine.py
  ↑
processing/observation/adapter.py
  ↑
orchestration/pipeline.py (modified)
```

All arrows point upward — no cycles.

---

## 6. Test Dependency Map

### 6.1 New Test Files Needed

| Test File | Tests | Depends On |
|-----------|-------|------------|
| `tests/unit/test_observation_models.py` | ~20 | schemas/observation_models.py |
| `tests/unit/test_observation_store.py` | ~25 | processing/observation/store.py |
| `tests/unit/test_adapter_layer.py` | ~20 | processing/observation/adapter.py |
| `tests/unit/test_commit_extractor.py` | ~15 | processing/extraction/commit_extractor.py |
| `tests/unit/test_metric_extractor.py` | ~15 | processing/extraction/metric_extractor.py |
| `tests/unit/test_extraction_engine_v2.py` | ~20 | processing/extraction/engine.py |
| `tests/integration/test_observation_pipeline.py` | ~15 | All observation modules |
| `tests/contract/test_observation_interfaces.py` | ~10 | IObservationStore, IAdapterLayer |

**Total new tests:** ~140

### 6.2 Existing Test Impact

| Existing Test | Impact | Action |
|---------------|--------|--------|
| All 667 unit tests | MUST PASS | No changes allowed |
| All 63 integration tests | MUST PASS | No changes allowed |
| All contract tests | MUST PASS | Only additions, no modifications |
| All schema tests | MUST PASS | Only additions, no modifications |

---

## 7. Risk Dependencies

### 7.1 High-Risk Dependencies

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Observation store serialization at scale | MEDIUM | HIGH | Lazy evaluation, batch commits |
| Adapter layer translation overhead | MEDIUM | MEDIUM | Profile before optimizing |
| Extraction refactoring breaks existing tests | LOW | HIGH | Strict TDD, run tests after each change |
| Circular import introduced | LOW | HIGH | Dependency graph enforced |

### 7.2 Medium-Risk Dependencies

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Window builder depends on extraction | HIGH | LOW | Soft dependency, can accept raw observations |
| Scoring depends on detector output format | HIGH | LOW | Adapter handles translation |
| CLI integration depends on all engines | HIGH | LOW | Integrate incrementally |

---

## 8. Implementation Sequencing

### 8.1 Recommended PR Sequence

| PR | Content | Files Changed | Tests |
|----|---------|---------------|-------|
| PR-1 | Observation models + tests | 3 new files | ~20 new tests |
| PR-2 | Observation store + tests | 3 new files | ~25 new tests |
| PR-3 | Adapter layer + tests | 3 new files | ~20 new tests |
| PR-4 | CommitExtractor + tests | 3 new files | ~15 new tests |
| PR-5 | MetricExtractor + tests | 3 new files | ~15 new tests |
| PR-6 | Extraction engine refactor + tests | 2 modified + 1 new | ~20 new tests |
| PR-7 | Pipeline integration + tests | 2 modified + 1 new | ~15 new tests |
| PR-8 | CLI observation flags + tests | 2 modified + 1 new | ~10 new tests |

**Total PRs:** 8 (each passing all existing tests)

### 8.2 PR Size Constraints

- Maximum **500 lines changed** per PR (including tests)
- Maximum **3 new files** per PR (excluding tests)
- Maximum **2 modified files** per PR (excluding tests)
- Each PR must pass **all 730 existing tests** + new tests

---

*Generated by Phase 1 Implementation Dependency Graph — 2026-06-29*
