# Repository Evolution Matrix

**Document:** REPOSITORY_EVOLUTION_MATRIX.md
**Phase:** Phase 1 — Repository Audit & Implementation Kickoff
**Source:** IMS v1.0 file migration mapping
**Date:** 2026-06-29
**Status:** COMPLETE

---

## 1. Executive Summary

This matrix maps every file in the repository to its v1.5 evolution: **CREATE** (new file), **MODIFY** (existing file changes), **RETAIN** (no change), **DELETE** (remove), or **RESERVE** (do not touch). It ensures no file is accidentally deleted, modified, or left orphaned.

**Summary:** 8 CREATE, 9 MODIFY, 43 RETAIN, 3 DELETE, 1 RESERVE

---

## 2. Source Tree Evolution

### 2.1 New Files (CREATE)

| File | Package | Purpose | Lines Est. |
|------|---------|---------|------------|
| `src/miie/schemas/observation_models.py` | schemas | Observation, ObservationWindow, ObservationCollection, CommitMetadata, MetricValue, ExtractionResult dataclasses | ~300 |
| `src/miie/processing/observation/__init__.py` | processing/observation | Package init | ~5 |
| `src/miie/processing/observation/store.py` | processing/observation | IObservationStore Protocol, ObservationStore class | ~200 |
| `src/miie/processing/observation/adapter.py` | processing/observation | IAdapterLayer Protocol, AdapterLayer class | ~250 |
| `src/miie/processing/extraction/__init__.py` | processing/extraction | Package init | ~5 |
| `src/miie/processing/extraction/commit_extractor.py` | processing/extraction | CommitExtractor class | ~200 |
| `src/miie/processing/extraction/metric_extractor.py` | processing/extraction | MetricExtractor class | ~200 |
| `src/miie/processing/extraction/engine.py` | processing/extraction | Refactored ExtractionEngine | ~150 |

**Total new files:** 8
**Total new lines:** ~1,310

### 2.2 Modified Files (MODIFY)

| File | Change Type | Impact | Risk |
|------|-------------|--------|------|
| `src/miie/contracts/interfaces.py` | ADD | +2 Protocols (IObservationStore, IAdapterLayer) | LOW — additive only |
| `src/miie/contracts/errors.py` | ADD | +2 error types (ObservationError, ObservationStoreError) | LOW — additive only |
| `src/miie/orchestration/pipeline.py` | MODIFY | Wire observation store into pipeline stages | MEDIUM — core pipeline |
| `src/miie/processing/segmentation.py` | MODIFY | Accept ObservationStore instead of MetricDataFrame | MEDIUM — segmentation |
| `src/miie/cli.py` | ADD | +observation-level flags (--observation-level, --store-format) | LOW — additive only |
| `src/miie/config/loader.py` | ADD | +observation config options | LOW — additive only |
| `src/miie/processing/extraction.py` | DEPRECATE | Replace with processing/extraction/ package | HIGH — extraction refactor |
| `src/miie/processing/__init__.py` | MODIFY | Import new subpackages | LOW — additive only |
| `pyproject.toml` | MODIFY | +jsonschema dependency (already present) | LOW — no change needed |

**Total modified files:** 9
**Risk level:** 2 HIGH, 2 MEDIUM, 5 LOW

### 2.3 Retained Files (RETAIN — No Change)

| Package | Files | Lines | Reason |
|---------|-------|-------|--------|
| `src/miie/__init__.py` | 1 | ~20 | Package root — no change |
| `src/miie/version.py` | 1 | ~10 | Version — no change |
| `src/miie/api.py` | 1 | ~200 | API — no change |
| `src/miie/api/server.py` | 1 | ~200 | API server — no change |
| `src/miie/api/dependencies.py` | 1 | ~100 | API deps — no change |
| `src/miie/api/models.py` | 1 | ~80 | API models — no change |
| `src/miie/api/middleware.py` | 1 | ~50 | API middleware — no change |
| `src/miie/benchmark/generator.py` | 1 | ~530 | Benchmark generator — no change |
| `src/miie/benchmark/runner.py` | 1 | ~200 | Benchmark runner — no change |
| `src/miie/benchmark/evaluation.py` | 1 | ~100 | Benchmark evaluation — no change |
| `src/miie/benchmark/candidates.py` | 1 | ~100 | Benchmark candidates — no change |
| `src/miie/benchmark/utils.py` | 1 | ~80 | Benchmark utils — no change |
| `src/miie/config/defaults.py` | 1 | ~50 | Config defaults — no change |
| `src/miie/config/logging.py` | 1 | ~50 | Config logging — no change |
| `src/miie/contracts/dataclasses.py` | 1 | ~100 | Contract dataclasses — no change |
| `src/miie/contracts/validators.py` | 1 | ~80 | Contract validators — no change |
| `src/miie/processing/detection/base.py` | 1 | ~73 | BaseDetector ABC — no change |
| `src/miie/processing/detection/dispatcher.py` | 1 | ~116 | Dispatcher — no change |
| `src/miie/processing/detection/registry.py` | 1 | ~50 | Registry — no change |
| `src/miie/processing/detection/runner.py` | 1 | ~80 | Runner — no change |
| `src/miie/processing/detection/distribution_drift_detector.py` | 1 | ~288 | D-01 — no change |
| `src/miie/processing/detection/correlation_breakdown_detector.py` | 1 | ~329 | D-02 — no change |
| `src/miie/processing/detection/threshold_compression_detector.py` | 1 | ~373 | D-03 — no change |
| `src/miie/processing/detection/mock_detectors.py` | 1 | ~100 | Mock detectors — no change |
| `src/miie/processing/detection/__init__.py` | 1 | ~5 | Detection init — no change |
| `src/miie/processing/scoring/__init__.py` | 1 | ~5 | Scoring init — no change |
| `src/miie/processing/scoring/engine.py` | 1 | ~557 | Scoring engine — no change |
| `src/miie/processing/scoring/mock_scoring.py` | 1 | ~80 | Mock scoring — no change |
| `src/miie/processing/explanation/__init__.py` | 1 | ~5 | Explanation init — no change |
| `src/miie/processing/explanation/engine.py` | 1 | ~183 | Explanation engine — no change |
| `src/miie/processing/explanation/mock_explanation.py` | 1 | ~80 | Mock explanation — no change |
| `src/miie/processing/reporting/__init__.py` | 1 | ~5 | Reporting init — no change |
| `src/miie/processing/reporting/engine.py` | 1 | ~564 | Report generator — no change |
| `src/miie/processing/reporting/formatter.py` | 1 | ~200 | Report formatter — no change |
| `src/miie/processing/reporting/utils.py` | 1 | ~100 | Reporting utils — no change |
| `src/miie/processing/benchmark/__init__.py` | 1 | ~5 | Benchmark init — no change |
| `src/miie/processing/benchmark/engine.py` | 1 | ~162 | Benchmark engine — no change |
| `src/miie/processing/evaluation/__init__.py` | 1 | ~5 | Evaluation init — no change |
| `src/miie/processing/evaluation/engine.py` | 1 | ~85 | Evaluation engine — no change |
| `src/miie/schemas/metric_registry.py` | 1 | ~200 | Metric registry — no change |
| `src/miie/schemas/serialization.py` | 1 | ~150 | Serialization — no change |
| `src/miie/schemas/__init__.py` | 1 | ~5 | Schemas init — no change |
| `src/miie/utils/git.py` | 1 | ~200 | Git utilities — no change |
| `src/miie/utils/hashing.py` | 1 | ~80 | Hashing utilities — no change |
| `src/miie/utils/seed.py` | 1 | ~50 | Seed management — no change |
| `src/miie/utils/__init__.py` | 1 | ~5 | Utils init — no change |
| `src/miie/validation/__init__.py` | 1 | ~5 | Validation init — no change |
| `src/miie/validation/service.py` | 1 | ~80 | Validation service — no change |

**Total retained files:** 48
**Total retained lines:** ~6,500

### 2.4 Deleted Files (DELETE)

| File | Package | Reason |
|------|---------|--------|
| `src/miie/common/__init__.py` | common | Empty package — no code |
| `src/miie/detection/__init__.py` | detection | Empty package — detection logic in processing/detection/ |
| `src/miie/interface/__init__.py` | interface | Empty package — no code |

**Total deleted files:** 3
**Total deleted lines:** 39 (3 × 13)

### 2.5 Reserved Files (RESERVE — DO NOT TOUCH)

| File | Package | Reason |
|------|---------|--------|
| `src/miie/storage/__init__.py` | storage | Reserved for v2.0 |

**Total reserved files:** 1

---

## 3. Test Tree Evolution

### 3.1 New Test Files (CREATE)

| File | Tests | Covers |
|------|-------|--------|
| `tests/unit/test_observation_models.py` | ~20 | Observation, ObservationWindow, ObservationCollection, CommitMetadata, MetricValue, ExtractionResult |
| `tests/unit/test_observation_store.py` | ~25 | IObservationStore, ObservationStore |
| `tests/unit/test_adapter_layer.py` | ~20 | IAdapterLayer, AdapterLayer |
| `tests/unit/test_commit_extractor.py` | ~15 | CommitExtractor |
| `tests/unit/test_metric_extractor.py` | ~15 | MetricExtractor |
| `tests/unit/test_extraction_engine_v2.py` | ~20 | Refactored ExtractionEngine |
| `tests/integration/test_observation_pipeline.py` | ~15 | Full observation pipeline |
| `tests/contract/test_observation_interfaces.py` | ~10 | IObservationStore, IAdapterLayer conformance |

**Total new test files:** 8
**Total new tests:** ~140

### 3.2 Modified Test Files (MODIFY)

| File | Change | Risk |
|------|--------|------|
| `tests/conftest.py` | Add observation fixtures | LOW — additive |
| `tests/unit/test_cli.py` | Add observation-level flag tests | LOW — additive |
| `tests/integration/test_pipeline.py` | Add observation pipeline integration | LOW — additive |

**Total modified test files:** 3

### 3.3 Retained Test Files (RETAIN)

All 67 existing test files — **NO CHANGES ALLOWED** to existing test logic.

**Total retained test files:** 67

---

## 4. Documentation Tree Evolution

### 4.1 New Documentation (CREATE)

| File | Purpose |
|------|---------|
| `docs/architecture/observation_engine/OBSERVATION_MODELS.md` | Observation model reference |
| `docs/architecture/observation_engine/OBSERVATION_STORE.md` | Store API reference |
| `docs/architecture/observation_engine/ADAPTER_LAYER.md` | Adapter layer reference |
| `docs/guides/observation_pipeline.md` | User guide for observation pipeline |
| `docs/guides/extraction_refactor.md` | Migration guide for extraction refactor |

**Total new docs:** 5

### 4.2 Modified Documentation (MODIFY)

| File | Change |
|------|--------|
| `README.md` | Add v1.5 features section |
| `docs/README.md` | Add observation engine docs link |
| `CHANGELOG.md` | Add v1.5 changes |

**Total modified docs:** 3

### 4.3 Retained Documentation (RETAIN)

All existing documentation — **NO CHANGES ALLOWED** to frozen architecture docs.

**Total retained docs:** 45+

---

## 5. CI/CD Evolution

### 5.1 Modified CI Files

| File | Change | Risk |
|------|--------|------|
| `.github/workflows/ci.yml` | Add observation test job | LOW — additive |
| `setup.cfg` | Add observation markers | LOW — additive |
| `pyproject.toml` | Verify jsonschema dependency | LOW — already present |

**Total modified CI files:** 3

### 5.2 Retained CI Files

All existing CI configuration — **NO CHANGES ALLOWED** to existing jobs.

---

## 6. Evolution Summary

### 6.1 File Count Changes

| Category | v1.0 | v1.5 | Delta |
|----------|------|------|-------|
| Source files | 60 | 65 | +5 (8 new - 3 deleted) |
| Test files | 67 | 75 | +8 |
| Documentation | 45+ | 50+ | +5 |
| CI/CD files | 3 | 3 | 0 |
| Config files | 4 | 4 | 0 |
| **Total** | **179+** | **197+** | **+18** |

### 6.2 Line Count Changes

| Category | v1.0 | v1.5 | Delta |
|----------|------|------|-------|
| Source lines | ~9,390 | ~10,700 | +1,310 |
| Test lines | ~9,500 | ~11,000 | +1,500 |
| Doc lines | ~15,000 | ~16,000 | +1,000 |
| **Total** | **~33,890** | **~37,700** | **+3,810** |

### 6.3 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Extraction refactor breaks tests | LOW | HIGH | Strict TDD, run tests after each change |
| Adapter layer introduces bugs | MEDIUM | MEDIUM | Comprehensive adapter tests |
| Pipeline integration fails | LOW | HIGH | Incremental integration, test after each step |
| Import paths broken | LOW | HIGH | Only add new modules, never move existing ones |

---

*Generated by Phase 1 Repository Evolution Matrix — 2026-06-29*
