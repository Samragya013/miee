# SRP-03 WP3: Legacy Bridge Lifecycle Inventory

**Status:** Complete  
**Date:** 2026-07-10  
**SRP:** SRP-03 (Severity Classification)  
**Work Package:** WP3 (Legacy Path Audit)

---

## Lifecycle Classification

| ID | Bridge | Location | Classification | Status | Action |
|----|--------|----------|---------------|--------|--------|
| B1 | `MetricExtractionEngine` | `processing/extraction.py` | DEPRECATED | Active in tests | Migrate tests to `ExtractionEngine` |
| B2 | Lazy-import shim | `processing/extraction/__init__.py` | DEPRECATED | Active | Remove after B1 migration |
| B3 | `DetectorAdapter` | `processing/observation/adapter.py` | PRODUCTION | Active | Keep until detectors migrate |
| B4 | `MetricExtractor` | `processing/extraction/metric_extractor.py` | PRODUCTION | Active | Keep until detectors migrate |
| B5 | Dispatcher dual-path | `processing/detection/dispatcher.py` | PRODUCTION | Active | Keep until all detectors implement `detect_observations()` |
| B6 | Dual-path detectors | D-01, D-02, D-03 | PRODUCTION | Active | Keep legacy path until dispatcher fully migrates |
| B7 | CLI legacy bridge | `cli/__init__.py` | PRODUCTION | Active | Keep for CLI UI/UX requirements |
| B8 | Schema legacy fields | `schemas/models.py` | PRODUCTION | Active | Keep for backward compatibility |
| B9 | `BaseDetector` dual API | `processing/detection/base.py` | PRODUCTION | Active | Architectural foundation |
| B10 | ScoringEngine enhancement | `processing/scoring/engine.py` | PRODUCTION | Active | Optional enhancement path |

---

## Detailed Classification

### DEPRECATED — Should be migrated

**B1: `MetricExtractionEngine`**
- **File:** `processing/extraction.py`
- **Status:** Deprecated per docstring and deprecation warning
- **Still used in:** 5+ test files, 40+ instantiations
- **Blocker:** Test dependency
- **Recommended action:** Migrate tests to `ExtractionEngine`, then remove

**B2: Lazy-import shim**
- **File:** `processing/extraction/__init__.py`
- **Status:** Deprecated, provides backward-compatible imports
- **Still used in:** Every import of `MetricExtractionEngine`
- **Blocker:** B1 removal
- **Recommended action:** Remove after B1 is migrated

### PRODUCTION — Keep (documented architectural decision)

**B3: `DetectorAdapter`**
- **File:** `processing/observation/adapter.py`
- **Status:** Transitional adapter for detectors without `detect_observations()`
- **Justification:** Allows gradual detector migration
- **Removal condition:** When all detectors implement `detect_observations()`

**B4: `MetricExtractor`**
- **File:** `processing/extraction/metric_extractor.py`
- **Status:** Core extraction pipeline component
- **Justification:** Converts ObservationCollection to MetricDataFrame for downstream consumers
- **Removal condition:** When detectors natively consume ObservationWindow objects

**B5: Dispatcher dual-path**
- **File:** `processing/detection/dispatcher.py`
- **Status:** Routes to observation or legacy path based on detector capability
- **Justification:** Enables gradual migration without breaking existing detectors
- **Removal condition:** When all detectors implement `detect_observations()`

**B6: Dual-path detectors**
- **Files:** D-01, D-02, D-03
- **Status:** Both `detect_observations()` (v1.5) and `execute()` (legacy) methods
- **Justification:** Backward compatibility during migration period
- **Removal condition:** When dispatcher fully migrates to observation path

**B7: CLI legacy bridge**
- **File:** `cli/__init__.py`
- **Status:** Converts legacy WindowData to ObservationWindow for sampling framework
- **Justification:** CLI needs UI/UX-specific logic not in AnalysisPipeline
- **Removal condition:** When CLI migrated to use AnalysisPipeline (future SRP)

**B8: Schema legacy fields**
- **File:** `schemas/models.py`
- **Status:** Legacy dict-based fields alongside new typed fields
- **Justification:** Backward compatibility with existing consumers
- **Removal condition:** Major version bump (v2.0)

**B9: `BaseDetector` dual API**
- **File:** `processing/detection/base.py`
- **Status:** Abstract foundation for all detectors
- **Justification:** Architectural decision for gradual migration
- **Removal condition:** When observation path is the only path

**B10: ScoringEngine enhancement**
- **File:** `processing/scoring/engine.py`
- **Status:** Optional EvidencePackage parameter for enhanced scoring
- **Justification:** Backward compatible enhancement
- **Removal condition:** When EvidencePackage is always available

---

## Key Findings

1. **No deprecation timelines defined** — None of the legacy bridges have target removal dates or version milestones.

2. **Test dependency is the primary blocker** — `MetricExtractionEngine` is used in 40+ test instantiations across 5+ test files.

3. **Dual path is architecturally intentional** — The `BaseDetector` design explicitly allows gradual migration.

4. **Two adapter patterns in parallel** — `DetectorAdapter` (dispatch time) and `MetricExtractor` (extraction time) serve different roles but both produce MetricDataFrame.

---

## Recommended Actions

| Priority | Action | Dependencies |
|----------|--------|--------------|
| HIGH | Add deprecation timelines to all DEPRECATED bridges | None |
| HIGH | Migrate test suite from `MetricExtractionEngine` to `ExtractionEngine` | None |
| MEDIUM | Document removal conditions for PRODUCTION bridges | None |
| LOW | Remove B1 and B2 after test migration | B1 migration complete |
| LOW | Remove B3-B6 after full detector migration | All detectors implement `detect_observations()` |
