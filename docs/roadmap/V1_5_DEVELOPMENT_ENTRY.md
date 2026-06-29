# MIIE v1.5 — Development Entry Document

**Created:** 2026-06-29
**Baseline:** v1.0.1 (tag `4c4d5e6`)
**Reference:** `docs/architecture/RELEASE_BASELINE.md`
**Status:** Development Plan

---

## 1. Mission

Transform MIIE from a static anomaly detection tool into a dynamic observation and analysis platform that understands metric relationships, tracks degradation over time, and provides actionable scientific insight into measurement integrity.

v1.5 is the **scientific upgrade**: new detectors, new metrics, cross-metric analysis, and the foundation for continuous observation — without breaking the stable v1.0.x baseline.

---

## 2. Objectives

| # | Objective | Success Criteria |
|---|-----------|-----------------|
| O-1 | New detector modules | ≥2 new detectors with benchmark suites |
| O-2 | Extended metric registry | ≥12 metrics (from 7) with pluggable architecture |
| O-3 | Cross-metric analysis | Detector can use multiple metrics simultaneously |
| O-4 | Adaptive thresholds | Per-repo calibration instead of fixed α values |
| O-5 | Longitudinal analysis | Trend detection across multiple analysis runs |
| O-6 | Bootstrap confidence | True bootstrap intervals replacing z-score approximations |
| O-7 | Causal analysis foundation | Directional dependency detection |
| O-8 | Backward compatibility | v1.0.x output format remains valid |
| O-9 | Documentation complete | All new features documented with examples |
| O-10 | Test coverage maintained | ≥80% coverage on new code |

---

## 3. Out of Scope

| Item | Reason | Target Version |
|------|--------|---------------|
| Observation Engine | Requires v1.5 detector foundation | v2.0 |
| Real-time monitoring | Requires Observation Engine | v2.0 |
| Web dashboard | Requires API expansion | v2.0 |
| Multi-repo batch | Requires workspace management | v1.6 |
| REPL/interactive mode | UX overhaul | v2.0 |
| Cloud deployment | Infrastructure work | v2.0 |
| ML-based detectors | Requires training data | v2.0 |
| True Hartigan's dip test | Requires custom implementation | v1.6 |

---

## 4. Scientific Goals

### 4.1 New Detectors

| Detector | ID | Statistical Method | Minimum Data |
|----------|----|-------------------|--------------|
| Bimodality Detector | D-04 | Hartigan's Dip Test | n≥30 |
| Multivariate Anomaly | D-05 | Mahalanobis Distance | n≥20, p≥3 |
| Trend Breakpoint | D-06 | PELT (Pruned Exact Linear Time) | n≥50 |
| Seasonal Decomposition | D-07 | STL Decomposition | n≥100 |

### 4.2 Extended Metrics

| Metric | ID | Description | Range |
|--------|----|-------------|-------|
| Test Coverage Delta | M-08 | Coverage change between windows | [-100, 100] |
| Build Success Rate | M-09 | Build pass/fail ratio | [0, 100] |
| Dependency Freshness | M-10 | Dependency age in days | [0, ∞) |
| Documentation Coverage | M-11 | Docstring coverage ratio | [0, 100] |
| Merge Conflict Rate | M-12 | PRs with conflicts / total PRs | [0, 100] |

### 4.3 Cross-Metric Analysis

| Capability | Description |
|------------|-------------|
| Correlation Matrix | Pairwise metric correlation across windows |
| Dependency Graph | How metrics influence each other |
| Leading Indicators | Which metrics predict integrity drops |
| Anomaly Clustering | Group related anomalies by root cause |

### 4.4 Adaptive Thresholds

| Approach | Description |
|----------|-------------|
| Per-repo calibration | Baseline metrics from first N windows |
| Rolling baseline | Update calibration with new data |
| Confidence-aware thresholds | Tighter thresholds for small samples |
| Industry benchmarks | Compare against similar projects |

### 4.5 Longitudinal Analysis

| Capability | Description |
|------------|-------------|
| Trend Detection | Mann-Kendall test for monotonic trends |
| Change Points | PELT algorithm for breakpoint detection |
| Seasonality | STL decomposition for periodic patterns |
| Degradation Scoring | Rate of integrity decline over time |

---

## 5. Implementation Order

### Phase 1: Foundation (Week 1-2)

| Task | Priority | Dependencies |
|------|----------|-------------|
| Extend metric registry | HIGH | None |
| Add metric plugin interface | HIGH | None |
| Bootstrap confidence for D-03 | HIGH | None |
| Unit tests for new metrics | HIGH | Metric registry |

### Phase 2: New Detectors (Week 3-4)

| Task | Priority | Dependencies |
|------|----------|-------------|
| D-04 Bimodality Detector | HIGH | Metric registry |
| D-05 Multivariate Anomaly | HIGH | Metric registry |
| D-06 Trend Breakpoint | MEDIUM | D-04, D-05 |
| Benchmark suites for D-04, D-05, D-06 | HIGH | Detectors |

### Phase 3: Cross-Metric (Week 5-6)

| Task | Priority | Dependencies |
|------|----------|-------------|
| Correlation matrix engine | HIGH | Metric registry |
| Dependency graph analysis | MEDIUM | Correlation matrix |
| Leading indicator detection | MEDIUM | Longitudinal data |
| Anomaly clustering | LOW | Cross-metric data |

### Phase 4: Adaptive (Week 7-8)

| Task | Priority | Dependencies |
|------|----------|-------------|
| Per-repo baseline calibration | HIGH | Metric registry |
| Rolling baseline updater | MEDIUM | Calibration |
| Industry benchmark data | LOW | External data |
| Confidence-aware thresholds | HIGH | Calibration |

### Phase 5: Longitudinal (Week 9-10)

| Task | Priority | Dependencies |
|------|----------|-------------|
| Trend detection (Mann-Kendall) | HIGH | Metric history |
| Change point detection (PELT) | HIGH | Metric history |
| STL decomposition | MEDIUM | Metric history |
| Degradation scoring | HIGH | Trend + change point |

### Phase 6: Integration (Week 11-12)

| Task | Priority | Dependencies |
|------|----------|-------------|
| CLI integration for new detectors | HIGH | All detectors |
| Output format for new features | HIGH | All analysis |
| Documentation | HIGH | All features |
| Release preparation | HIGH | All tasks |

---

## 6. Milestones

| Milestone | Target Date | Deliverables |
|-----------|-------------|-------------|
| M1: Metric Registry | Week 2 | Extended metrics, plugin interface |
| M2: New Detectors | Week 4 | D-04, D-05, D-06 with benchmarks |
| M3: Cross-Metric | Week 6 | Correlation matrix, dependency graph |
| M4: Adaptive Thresholds | Week 8 | Per-repo calibration, rolling baseline |
| M5: Longitudinal | Week 10 | Trend detection, change points, STL |
| M6: v1.5 Release | Week 12 | All features integrated, documented, tested |

---

## 7. Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Scientific accuracy | New detectors produce false positives | MEDIUM | Extensive benchmarking, peer review |
| Performance | Cross-metric analysis slow on large repos | MEDIUM | Optimize algorithms, add progress indicators |
| Backward compatibility | New output format breaks v1.0.x consumers | LOW | Strict schema versioning, additive changes only |
| Dependency conflicts | New scientific packages conflict with existing | LOW | Careful version pinning, testing |
| Scope creep | v1.5 grows beyond 12 weeks | MEDIUM | Strict prioritization, defer low-priority items |
| Testing complexity | New detectors hard to test | MEDIUM | Property-based testing, synthetic data |

---

## 8. Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| New detectors | Count of new detector modules | ≥3 |
| Benchmark accuracy | New detectors meet accuracy targets | P≥0.75, R≥0.70 |
| Metric coverage | Total metrics available | ≥12 |
| Test coverage | Coverage on new code | ≥80% |
| Performance | Analysis time for 1000-commit repo | <60 seconds |
| Documentation | New features documented | 100% |
| Backward compatibility | v1.0.x output remains valid | 100% |
| CI/CD | All tests pass | 730+ tests green |

---

## 9. Exit Criteria

v1.5 development exits when:

1. All 6 milestones completed
2. All success criteria met
3. CI/CD pipeline passes (all jobs green)
4. Documentation complete
5. Release notes prepared
6. Version bumped to 1.5.0
7. Git tag `v1.5.0` created
8. Baseline updated to v1.5.0

---

## 10. Dependencies on v1.0.x Baseline

| Component | v1.0.x Status | v1.5 Impact |
|-----------|---------------|-------------|
| Pipeline architecture | Frozen | Extend (not replace) |
| Scoring model | Frozen | Add new factors |
| Schema definitions | Frozen | Add new fields (not remove) |
| CLI interface | Frozen | Add new commands |
| API endpoints | Frozen | Add new endpoints |
| Error model | Frozen | Add new error types |
| Config format | Frozen | Add new options |
| Benchmark suites | Frozen | Add new suites |

---

## 11. Version Strategy

| Version | Purpose | Timeline |
|---------|---------|----------|
| v1.0.1 | CI stabilization (current) | Released |
| v1.1.0 | Metric registry + bootstrap confidence | Week 2 |
| v1.2.0 | New detectors (D-04, D-05) | Week 4 |
| v1.3.0 | Cross-metric analysis | Week 6 |
| v1.4.0 | Adaptive thresholds | Week 8 |
| v1.5.0 | Longitudinal + full integration | Week 12 |

---

*This document defines the scope and approach for v1.5 scientific development. All work begins from the v1.0.1 baseline.*
