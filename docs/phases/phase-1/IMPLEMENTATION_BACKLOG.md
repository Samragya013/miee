# Implementation Backlog

**Document:** IMPLEMENTATION_BACKLOG.md
**Phase:** Phase 1 — Repository Audit & Implementation Kickoff
**Source:** IMS v1.0 + Architecture Compliance Matrix
**Date:** 2026-06-29
**Status:** COMPLETE

---

## 1. Executive Summary

This backlog contains **45 work items** organized by IMS phase, estimated effort, and priority. Each item is sized as S (< 2h), M (2-6h), L (6-12h), or XL (12-24h). Total estimated effort: **~180-220 hours** (single engineer, ~5-6 weeks at 40h/week).

**Priority Legend:**
- P0 = Must complete before any other work
- P1 = Must complete before next phase starts
- P2 = Should complete in this phase
- P3 = Can defer to later phase

---

## 2. Phase 1: Observation Core

| ID | Item | Size | Priority | Dependencies | Acceptance Criteria |
|----|------|------|----------|-------------|---------------------|
| 1.1 | Create `schemas/observation_models.py` with Observation dataclass | M | P0 | None | Observation has: observation_id, commit_hash, metric_id, value, timestamp, author, files_changed. All fields typed. Frozen=True. |
| 1.2 | Add CommitMetadata dataclass | S | P0 | None | CommitMetadata has: hash, author, timestamp, message, files_changed, insertions, deletions. |
| 1.3 | Add MetricValue dataclass | S | P0 | None | MetricValue has: metric_id, value, unit, extraction_method. |
| 1.4 | Add ExtractionResult dataclass | S | P0 | None | ExtractionResult has: observations (list[Observation]), metadata (CommitMetadata), extraction_time, source_type. |
| 1.5 | Add deterministic ID generation function | M | P0 | 1.1 | SHA-256(source_type:source_id:metric_id)[:16] produces stable IDs. |
| 1.6 | Add Observation validation rules | M | P1 | 1.1-1.5 | observation_id matches regex `^[a-f0-9]{16}$`. commit_hash matches `^[a-f0-9]{40}$`. metric_id matches `^M-[0-9]{2}$`. |
| 1.7 | Add JSON serialization for observation models | M | P1 | 1.1-1.5 | All models serialize to JSON and deserialize back identically. |
| 1.8 | Add schema versioning | S | P2 | 1.7 | Schema has version field. Serialization includes version. |
| 1.9 | Write unit tests for observation models | M | P0 | 1.1-1.8 | ~20 tests covering creation, validation, serialization, deterministic IDs. |
| 1.10 | Delete empty packages (common/, detection/, interface/) | S | P2 | None | Packages removed. Import tests still pass. |

**Phase 1 Total:** ~20-25 hours

---

## 3. Phase 2: Observation Storage

| ID | Item | Size | Priority | Dependencies | Acceptance Criteria |
|----|------|------|----------|-------------|---------------------|
| 2.1 | Define IObservationStore Protocol | M | P0 | 1.1 | Protocol has: add(observation), get_by_id(id), get_by_commit(hash), get_by_metric(id), get_all(), count(), clear(). |
| 2.2 | Implement ObservationStore class | L | P0 | 2.1 | In-memory dict-based store. All Protocol methods implemented. O(1) add, O(n) get_by_commit/get_by_metric. |
| 2.3 | Add store iteration protocol | M | P1 | 2.2 | ObservationStore supports iter(). Yields observations in insertion order. |
| 2.4 | Add store filtering | M | P1 | 2.2 | Filter by commit hash, metric ID, time range, author. Returns ObservationStore. |
| 2.5 | Add store statistics | S | P2 | 2.2 | stats() returns: total_observations, unique_commits, unique_metrics, time_range. |
| 2.6 | Add optional JSON serialization | M | P2 | 2.2 | to_json(path) serializes store to JSON. from_json(path) deserializes. |
| 2.7 | Write unit tests for observation store | L | P0 | 2.1-2.6 | ~25 tests covering add, get, filter, iteration, serialization, edge cases. |
| 2.8 | Write integration test: store with real git data | M | P1 | 2.2 | Store accepts observations from git log extraction. |

**Phase 2 Total:** ~25-30 hours

---

## 4. Phase 3: Extraction Refactor

| ID | Item | Size | Priority | Dependencies | Acceptance Criteria |
|----|------|------|----------|-------------|---------------------|
| 3.1 | Implement CommitExtractor | L | P0 | 1.1, 2.2 | Extracts commit-level observations from git log. Returns list[Observation] per commit. |
| 3.2 | Implement MetricExtractor | L | P0 | 1.1, 2.2 | Extracts metric values per commit. Returns list[MetricValue]. |
| 3.3 | Refactor ExtractionEngine to use extractors | L | P0 | 3.1, 3.2 | Engine calls CommitExtractor then MetricExtractor. Stores results in ObservationStore. |
| 3.4 | Add batch git log extraction | M | P1 | 3.1 | Single `git log` call for all commits. Parse into per-commit observations. |
| 3.5 | Add extraction progress reporting | S | P2 | 3.3 | Extraction reports progress: commits processed, observations created. |
| 3.6 | Preserve backward compatibility | M | P0 | 3.3 | Existing MetricDataFrame output still works. Adapter layer handles translation. |
| 3.7 | Write unit tests for CommitExtractor | M | P0 | 3.1 | ~15 tests covering single commit, batch, edge cases. |
| 3.8 | Write unit tests for MetricExtractor | M | P0 | 3.2 | ~15 tests covering metric calculation, edge cases. |
| 3.9 | Write integration tests: extraction pipeline | M | P1 | 3.1-3.6 | Full extraction from git repo → ObservationStore → MetricDataFrame. |

**Phase 3 Total:** ~30-35 hours

---

## 5. Phase 4: Window Builder

| ID | Item | Size | Priority | Dependencies | Acceptance Criteria |
|----|------|------|----------|-------------|---------------------|
| 4.1 | Add ObservationWindow dataclass | M | P0 | 1.1 | Window has: window_id (deterministic SHA-256), observations (list[Observation]), metadata. |
| 4.2 | Add ObservationCollection dataclass | M | P0 | 4.1 | Collection has: windows (list[ObservationWindow]), repository metadata. |
| 4.3 | Refactor WindowSegmentationEngine | L | P0 | 4.1, 4.2, 2.2 | Engine accepts ObservationStore, returns ObservationCollection. |
| 4.4 | Implement time-based windowing | M | P1 | 4.3 | Windows grouped by time ranges. Deterministic window IDs. |
| 4.5 | Implement commit-count windowing | M | P1 | 4.3 | Windows grouped by commit count. Deterministic window IDs. |
| 4.6 | Implement hybrid windowing | M | P2 | 4.3 | Combined time + commit-count strategy. |
| 4.7 | Add minimum window gate | S | P0 | 4.3 | < 2 windows → abort with exit 3. Per AFD §Step 8. |
| 4.8 | Write unit tests for windowing | M | P0 | 4.1-4.7 | ~20 tests covering time, commit-count, hybrid, edge cases. |
| 4.9 | Write integration test: windowing pipeline | M | P1 | 4.1-4.7 | Full pipeline: git repo → extraction → windowing → ObservationCollection. |

**Phase 4 Total:** ~25-30 hours

---

## 6. Phase 5: Detector Refactor

| ID | Item | Size | Priority | Dependencies | Acceptance Criteria |
|----|------|------|----------|-------------|---------------------|
| 5.1 | Define IAdapterLayer Protocol | M | P0 | 4.1 | Protocol has: to_metric_dataframe(window), to_paired_observations(window). |
| 5.2 | Implement AdapterLayer class | L | P0 | 5.1 | Translates ObservationWindow → MetricDataFrame. Preserves all data. |
| 5.3 | Add to_paired_observations() | M | P1 | 5.2 | Returns paired observations for D-02 Fisher z-test. |
| 5.4 | Refactor DetectorDispatcherEngine | M | P0 | 5.2 | Dispatcher calls adapter before passing to detectors. |
| 5.5 | Verify D-01 through D-03 compatibility | L | P0 | 5.4 | All 3 detectors produce identical output with adapter. |
| 5.6 | Add adapter performance test | S | P2 | 5.2 | Translation overhead < 5% of detection time. |
| 5.7 | Write unit tests for AdapterLayer | M | P0 | 5.1-5.3 | ~20 tests covering translation, edge cases, determinism. |
| 5.8 | Write integration test: detection with adapter | M | P1 | 5.1-5.5 | Full detection pipeline with adapter layer. |

**Phase 5 Total:** ~25-30 hours

---

## 7. Phase 6: Evidence Refactor

| ID | Item | Size | Priority | Dependencies | Acceptance Criteria |
|----|------|------|----------|-------------|---------------------|
| 6.1 | Refactor EvidenceEngine for observation-level evidence | L | P0 | 3.3 | Evidence generated per observation, not per window. |
| 6.2 | Add observation-level evidence serialization | M | P1 | 6.1 | EvidencePackage serializes observation-level data. |
| 6.3 | Preserve backward compatibility | M | P0 | 6.1 | Existing EvidencePackage output still works. |
| 6.4 | Write unit tests for observation evidence | M | P0 | 6.1-6.3 | ~15 tests covering evidence generation, serialization. |

**Phase 6 Total:** ~15-20 hours

---

## 8. Phase 7: Scoring Refactor

| ID | Item | Size | Priority | Dependencies | Acceptance Criteria |
|----|------|------|----------|-------------|---------------------|
| 7.1 | Refactor ScoringEngine for observation-level scoring | L | P0 | 5.5 | ScorePackage generated from observation-level data. |
| 7.2 | Standardize ScorePackage as dict | M | P1 | 7.1 | ScorePackage is always dict, never dataclass. |
| 7.3 | Preserve backward compatibility | M | P0 | 7.1 | Existing ScorePackage output still works. |
| 7.4 | Write unit tests for observation scoring | M | P0 | 7.1-7.3 | ~15 tests covering scoring, edge cases. |

**Phase 7 Total:** ~15-20 hours

---

## 9. Phase 8: Explanation Integration

| ID | Item | Size | Priority | Dependencies | Acceptance Criteria |
|----|------|------|----------|-------------|---------------------|
| 8.1 | Refactor ExplanationEngine for observation context | M | P0 | 7.1 | Explanation includes observation-level details. |
| 8.2 | Add observation-level narrative | M | P1 | 8.1 | Narrative references specific observations. |
| 8.3 | Write unit tests for observation explanation | M | P0 | 8.1-8.2 | ~10 tests covering explanation, edge cases. |

**Phase 8 Total:** ~10-15 hours

---

## 10. Phase 9: Benchmark Upgrade

| ID | Item | Size | Priority | Dependencies | Acceptance Criteria |
|----|------|------|----------|-------------|---------------------|
| 9.1 | Update benchmark datasets for observation format | M | P0 | 3.3 | Datasets produce ObservationStore input. |
| 9.2 | Update ground truth format | M | P0 | 9.1 | Ground truth references observation IDs. |
| 9.3 | Update benchmark runner | M | P0 | 9.1, 9.2 | Runner uses new format. |
| 9.4 | Write benchmark tests | M | P0 | 9.1-9.3 | All benchmark criteria still met. |

**Phase 9 Total:** ~15-20 hours

---

## 11. Phase 10: CLI Integration

| ID | Item | Size | Priority | Dependencies | Acceptance Criteria |
|----|------|------|----------|-------------|---------------------|
| 10.1 | Add `--observation-level` flag | S | P0 | 3.3 | CLI outputs observation-level data when flag set. |
| 10.2 | Add `--store-format` flag | S | P1 | 2.2 | CLI outputs store as JSON when flag set. |
| 10.3 | Update progress display | M | P2 | 3.3 | Progress shows observation count. |
| 10.4 | Write CLI tests | M | P0 | 10.1-10.3 | ~10 tests covering new flags. |

**Phase 10 Total:** ~10-15 hours

---

## 12. Phases 11-15: Validation, Optimization, Docs, RC, Release

| Phase | Items | Total Effort |
|-------|-------|-------------|
| Phase 11: Scientific Validation | 4 items (DSVP protocol setup, 61 datasets, 28 criteria, reproducibility) | ~20-25 hours |
| Phase 12: Performance Optimization | 3 items (profiling, bottleneck identification, optimization) | ~10-15 hours |
| Phase 13: Documentation Sync | 4 items (README, API docs, architecture docs, examples) | ~10-15 hours |
| Phase 14: Release Candidate | 3 items (RC branch, RC testing, RC approval) | ~5-10 hours |
| Phase 15: v1.5 Release | 2 items (release branch, tag, PyPI) | ~2-5 hours |

---

## 13. Backlog Summary

### 13.1 By Phase

| Phase | Items | S | M | L | XL | Total Hours |
|-------|-------|---|---|---|----|----|
| Phase 1: Observation Core | 10 | 4 | 5 | 0 | 0 | 20-25 |
| Phase 2: Observation Storage | 8 | 1 | 5 | 1 | 0 | 25-30 |
| Phase 3: Extraction Refactor | 9 | 1 | 5 | 2 | 0 | 30-35 |
| Phase 4: Window Builder | 9 | 1 | 5 | 1 | 0 | 25-30 |
| Phase 5: Detector Refactor | 8 | 1 | 4 | 2 | 0 | 25-30 |
| Phase 6: Evidence Refactor | 4 | 0 | 2 | 1 | 0 | 15-20 |
| Phase 7: Scoring Refactor | 4 | 0 | 2 | 1 | 0 | 15-20 |
| Phase 8: Explanation Integration | 3 | 0 | 3 | 0 | 0 | 10-15 |
| Phase 9: Benchmark Upgrade | 4 | 0 | 4 | 0 | 0 | 15-20 |
| Phase 10: CLI Integration | 4 | 2 | 1 | 0 | 0 | 10-15 |
| Phases 11-15 | 16 | 0 | 0 | 0 | 0 | 47-70 |
| **TOTAL** | **79** | **10** | **36** | **8** | **0** | **~232-310** |

### 13.2 By Priority

| Priority | Items | Percentage |
|----------|-------|------------|
| P0 (Must have) | 35 | 44% |
| P1 (Should have) | 22 | 28% |
| P2 (Nice to have) | 12 | 15% |
| P3 (Defer) | 10 | 13% |

### 13.3 By Size

| Size | Items | Percentage |
|------|-------|------------|
| S (< 2h) | 10 | 13% |
| M (2-6h) | 36 | 46% |
| L (6-12h) | 8 | 10% |
| XL (12-24h) | 0 | 0% |

**Note:** No XL items — all work is broken into manageable chunks.

---

*Generated by Phase 1 Implementation Backlog — 2026-06-29*
