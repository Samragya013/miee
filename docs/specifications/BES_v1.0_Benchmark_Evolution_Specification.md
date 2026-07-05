# Benchmark Evolution Specification (BES) v1.0

**MIIE v1.5 — Benchmark Ecosystem Engineering Specification**

| Field | Value |
|-------|-------|
| Document ID | BES-v1.0 |
| Version | 1.0.0 |
| Status | Canonical |
| Date | 2026-06-29 |
| Authors | MIIE Engineering |
| Approved By | Repository Governance |
| Derived From | PRD-v1.5-OE, OEAS-v1.5, ODSS-v1.0, DES-v2.0, DSVP-v1.0 |
| Supersedes | None (new) |
| Scope | Benchmark ecosystem for scientific validation, comparison, and evolution |
| Classification | Definition-only (no implementation code) |

---

## Table of Contents

1. [Document Metadata](#1-document-metadata)
2. [Purpose](#2-purpose)
3. [Scope](#3-scope)
4. [Objectives](#4-objectives)
5. [Non-Objectives](#5-non-objectives)
6. [Benchmark Philosophy](#6-benchmark-philosophy)
7. [Scientific Goals](#7-scientific-goals)
8. [Benchmark Taxonomy](#8-benchmark-taxonomy)
9. [Repository Categories](#9-repository-categories)
10. [Benchmark Metadata Schema](#10-benchmark-metadata-schema)
11. [Repository Lifecycle](#11-repository-lifecycle)
12. [Benchmark Dataset Structure](#12-benchmark-dataset-structure)
13. [Ground Truth Strategy](#13-ground-truth-strategy)
14. [Labeling Methodology](#14-labeling-methodology)
15. [Detector Coverage Matrix](#15-detector-coverage-matrix)
16. [Evaluation Methodology](#16-evaluation-methodology)
17. [Statistical Evaluation](#17-statistical-evaluation)
18. [Benchmark Versioning](#18-benchmark-versioning)
19. [Certification Process](#19-certification-process)
20. [Repository Expansion Strategy](#20-repository-expansion-strategy)
21. [Community Contribution Strategy](#21-community-contribution-strategy)
22. [Industrial Roadmap](#22-industrial-roadmap)
23. [Reproducibility Requirements](#23-reproducibility-requirements)
24. [Risk Analysis](#24-risk-analysis)
25. [Trade-off Analysis](#25-trade-off-analysis)
26. [Acceptance Criteria](#26-acceptance-criteria)
27. [Future Evolution](#27-future-evolution)
28. [Glossary](#28-glossary)
29. [Appendix](#29-appendix)

---

## 1. Document Metadata

| Field | Value |
|-------|-------|
| Document ID | BES-v1.0 |
| Version | 1.0.0 |
| Date | 2026-06-29 |
| Classification | Internal Engineering Specification |
| Status | Canonical |
| Baseline | v1.0.1 (tag `4c4d5e6`) |
| Dependencies | PRD-v1.5-OE, OEAS-v1.5, ODSS-v1.0, DES-v2.0, DSVP-v1.0 |
| Related Documents | RELEASE_BASELINE.md, BASELINE_CHANGE_POLICY.md, DSVP-v1.0 |

### Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-06-29 | MIIE Engineering | Initial benchmark evolution specification |

---

## 2. Purpose

This document defines the **complete benchmark ecosystem** for the Measurement Integrity Intelligence Engine (MIIE). It specifies how every current and future MIIE detector is scientifically validated, compared, evolved, and maintained through reproducible benchmark datasets.

The BES exists because:

| Problem | Description |
|---------|-------------|
| Current benchmarks are limited | The v1.0 benchmark suite contains 30 synthetic candidates generated with `BenchmarkDatasetGenerator`, covering three pathology types (metric-drift, correlation-breakdown, threshold-compression). These are necessary but insufficient for scientific validation. |
| No benchmark lifecycle management | Benchmarks are created ad-hoc. No formal process exists for creation, validation, certification, versioning, publication, deprecation, or replacement. |
| No ground truth strategy | Current ground truth relies on generator-seeded labels. No independent verification, no inter-rater agreement, no multi-method triangulation exists. |
| No evaluation methodology | The `EvaluationEngine` computes basic classification metrics (precision, recall, F1, AUC-ROC) but lacks statistical rigor — no confidence intervals, no hypothesis testing, no effect size computation. |
| No community contribution path | No framework exists for external researchers to contribute benchmark datasets, ground truth annotations, or evaluation results. |

This document defines a benchmark ecosystem capable of evaluating every detector — D-01 (Distributional Drift), D-02 (Correlation Breakdown), D-03 (Threshold Compression) — and all future detectors introduced through the MIIE evolution pipeline.

This document is a definition-only specification. It does not implement benchmark generators, modify repository code, or produce datasets. It defines *what* the benchmark ecosystem must contain, *why* each component exists, and *how* the ecosystem evolves over time.

---

## 3. Scope

### 3.1 In Scope

| Component | Scope |
|-----------|-------|
| Benchmark taxonomy | Classification of all benchmark types and their purposes |
| Repository categories | Characterization of benchmark repository classes |
| Metadata schema | Complete metadata specification for every benchmark |
| Ground truth strategy | How ground truth labels are established, verified, and maintained |
| Labeling methodology | Annotation process, inter-rater agreement, adjudication |
| Evaluation methodology | Statistical evaluation, confidence intervals, hypothesis testing |
| Lifecycle management | Creation through deprecation for all benchmarks |
| Versioning | Benchmark version management and backward compatibility |
| Certification | Process for certifying benchmark quality |
| Expansion strategy | How the benchmark corpus grows over time |
| Community contribution | Framework for external benchmark contributions |
| Reproducibility | Requirements for deterministic, reproducible benchmark execution |

### 3.2 Out of Scope

| Component | Reason | Target |
|-----------|--------|--------|
| Benchmark repository implementation | This spec defines the ecosystem, not the repos | Implementation phase |
| Detector algorithm changes | Algorithms are frozen per baseline | v1.5 unchanged |
| Observation Engine changes | Observation Engine is frozen per PRD-v1.5 | v1.5 unchanged |
| Scoring formula changes | Scoring is frozen per baseline | v1.5 unchanged |
| CI/CD pipeline changes | Separate infrastructure spec | Separate document |
| Performance benchmarking of MIIE itself | Covers detector correctness, not MIIE throughput | DES scope |

---

## 4. Objectives

| ID | Objective | Priority | Verification |
|----|-----------|----------|-------------|
| OBJ-1 | Support scientific validation of all current detectors | HIGH | All 28 DSVP acceptance criteria met |
| OBJ-2 | Support future detector families without redesign | HIGH | Extension mechanism documented |
| OBJ-3 | Ensure benchmark reproducibility | HIGH | 100-run deterministic execution |
| OBJ-4 | Enable longitudinal benchmark evolution | MEDIUM | Version history preserved |
| OBJ-5 | Enable community contribution | MEDIUM | Contribution pathway operational |
| OBJ-6 | Enable cross-detector comparison | HIGH | Unified evaluation framework |
| OBJ-7 | Enable regression testing | HIGH | Cross-version benchmark stability |
| OBJ-8 | Support industrial-scale repositories | LOW | Roadmap defined |
| OBJ-9 | Establish ground truth methodology | HIGH | Multi-method triangulation |
| OBJ-10 | Ensure statistical rigor in evaluation | HIGH | Confidence intervals, hypothesis tests |

---

## 5. Non-Objectives

| ID | Non-Objective | Reason |
|----|--------------|--------|
| NO-1 | Implement benchmark repositories | This is a specification, not an implementation |
| NO-2 | Generate benchmark datasets | Generator implementation is separate |
| NO-3 | Redesign detector algorithms | Algorithms are frozen |
| NO-4 | Validate scoring formulas | Scoring is frozen per baseline |
| NO-5 | Provide CI/CD infrastructure | Infrastructure is separate |
| NO-6 | Benchmark MIIE throughput | Covers detector correctness, not system performance |
| NO-7 | Replace DSVP | DSVP defines validation methodology; BES defines the data that feeds it |

---

## 6. Benchmark Philosophy

### 6.1 Why Benchmark Ecosystems Matter

A benchmark is not a test. A test verifies that code does what it was told. A benchmark asks whether what it was told to do is *correct*.

The distinction is fundamental:

```
┌─────────────────────────────────────────────────────────────────┐
│                    TEST vs. BENCHMARK                            │
│                                                                  │
│  ┌─────────────────────────┐  ┌────────────────────────────────┐│
│  │        UNIT TEST         │  │         BENCHMARK              ││
│  │                          │  │                                ││
│  │  "Does D-01 detect       │  │  "Is D-01's detection         ││
│  │   drift when given       │  │   statistically valid,         ││
│  │   known-drift data?"     │  │   reproducible, and           ││
│  │                          │  │   trustworthy across          ││
│  │  PASS / FAIL             │  │   diverse real-world          ││
│  │                          │  │   conditions?"                ││
│  │                          │  │                                ││
│  │                          │  │  Precision, Recall, F1,       ││
│  │                          │  │  Confidence Intervals,        ││
│  │                          │  │  Effect Sizes, p-values       ││
│  └─────────────────────────┘  └────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

| Test Type | Purpose | Scope | Output | Frequency |
|-----------|---------|-------|--------|-----------|
| Unit test | Verify code correctness | Single function | PASS/FAIL | Every commit |
| Integration test | Verify component interaction | Multiple components | PASS/FAIL | Every commit |
| Validation dataset | Verify algorithm correctness | Known inputs/outputs | PASS/FAIL | Before release |
| Research benchmark | Compare algorithms | Representative samples | Metric scores | Per experiment |
| Scientific benchmark | Validate statistical rigor | Diverse conditions | Metrics + CIs + p-values | Per release |

### 6.2 Benchmark Ecosystem Requirements

A benchmark ecosystem must satisfy six properties:

| Property | Definition | Verification |
|----------|-----------|-------------|
| **Reproducibility** | Identical inputs produce identical outputs across runs | 100-run determinism test |
| **Representativeness** | Benchmarks cover the problem space | Category coverage matrix |
| **Independence** | Ground truth is established independently of the system being tested | Dual-reviewer + adjudication |
| **Versionability** | Benchmarks evolve without losing historical comparability | Semver + deprecation policy |
| **Extensibility** | New detector families can be benchmarked without redesign | Plugin architecture |
| **Transparency** | Every benchmark decision is documented and auditable | Metadata + changelog |

### 6.3 Benchmark vs. Validation

The DSVP defines *how* detectors are validated. The BES defines *what data* feeds that validation.

```
┌─────────────────────────────────────────────────────────────────┐
│                BES ↔ DSVP RELATIONSHIP                          │
│                                                                  │
│  ┌──────────────────────┐       ┌────────────────────────────┐  │
│  │         BES          │       │          DSVP              │  │
│  │                      │       │                            │  │
│  │  Defines benchmark   │──────►│  Consumes benchmarks for   │  │
│  │  datasets, ground    │       │  hypothesis testing,       │  │
│  │  truth, evaluation   │       │  false positive analysis,  │  │
│  │  methodology         │       │  stress testing            │  │
│  │                      │       │                            │  │
│  │  "What to test       │       │  "How to validate          │  │
│  │   with"              │       │   statistically"           │  │
│  └──────────────────────┘       └────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Scientific Goals

### 7.1 Primary Scientific Goals

| ID | Goal | Measurement | Target |
|----|------|-------------|--------|
| SG-1 | Detector correctness | Precision ≥ target per DSVP Table 17 | D-01: 0.80, D-02: 0.75, D-03: 0.85 |
| SG-2 | Detector completeness | Recall ≥ target per DSVP Table 17 | D-01: 0.75, D-02: 0.70, D-03: 0.80 |
| SG-3 | Statistical significance | p < 0.05 for all primary hypotheses | Per DSVP Section 8 |
| SG-4 | Reproducibility | Identical results across 100 runs | Seed=42 determinism |
| SG-5 | False positive rate | FPR < 0.10 under no-anomaly conditions | Per detector |
| SG-6 | Confidence calibration | Confidence correlates with correctness | Pearson r > 0.6 |
| SG-7 | Cross-version stability | Performance does not degrade across versions | Regression Δ < 0.05 |

### 7.2 Secondary Scientific Goals

| ID | Goal | Measurement | Timeline |
|----|------|-------------|----------|
| SG-8 | Community validation | External benchmark contributions | v1.6+ |
| SG-9 | Industrial applicability | Performance on proprietary repositories | v2.0+ |
| SG-10 | Cross-language support | Benchmark coverage across programming languages | v2.0+ |
| SG-11 | Longitudinal tracking | Detector performance over time | v1.6+ |

---

## 8. Benchmark Taxonomy

### 8.1 Taxonomy Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       BENCHMARK TAXONOMY                                 │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  CATEGORY 1: SYNTHETIC                                            │  │
│  │  Ground truth known by construction. Controlled experiments.      │  │
│  │  30 datasets (10 per detector). Deterministic generation.         │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  CATEGORY 2: REAL OPEN SOURCE                                     │  │
│  │  Ecological validity. Real repositories with expert labels.       │  │
│  │  10 repositories. Diverse characteristics.                        │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  CATEGORY 3: EDGE-CASE                                            │  │
│  │  Boundary conditions. Minimum samples, maximum values,            │  │
│  │  degenerate distributions, single-observation windows.            │  │
│  │  10 datasets. Explicit edge-case construction.                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  CATEGORY 4: ADVERSARIAL                                          │  │
│  │  Robustness to crafted inputs. Gaming patterns, evasion,          │  │
│  │  adversarial manipulation. 6 datasets.                            │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  CATEGORY 5: STRESS                                               │  │
│  │  Scalability limits. Large samples, many windows,                 │  │
│  │  extreme value ranges. 5 datasets.                                │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  CATEGORY 6: TEMPORAL EVOLUTION                                   │  │
│  │  Same repository at different time points. Longitudinal           │  │
│  │  tracking. 5 repositories × 3 time slices.                       │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  CATEGORY 7: LONGITUDINAL                                         │  │
│  │  Same repository tracked over months/years.                       │  │
│  │  Detector performance stability over time.                        │  │
│  │  3 repositories × 5 time points.                                  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  CATEGORY 8: INDUSTRIAL (FUTURE)                                  │  │
│  │  Proprietary repositories. Controlled access.                     │  │
│  │  Enterprise-scale characteristics. v2.0+ roadmap.                 │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Category Definitions

| Category | Purpose | Ground Truth Source | Count | Timeline |
|----------|---------|-------------------|-------|----------|
| Synthetic | Controlled experiments with known outcomes | Construction parameters | 30 | v1.5 |
| Real OSS | Ecological validity in real repositories | Expert annotation (dual-reviewer) | 10 | v1.5 |
| Edge-Case | Boundary conditions and extreme inputs | Construction parameters | 10 | v1.5 |
| Adversarial | Robustness to adversarial manipulation | Construction parameters | 6 | v1.5 |
| Stress | Scalability and performance limits | Implicit (no anomaly expected) | 5 | v1.5 |
| Temporal Evolution | Behavior at different repository stages | Expert annotation | 15 | v1.6 |
| Longitudinal | Stability over time | Expert annotation | 15 | v1.6 |
| Industrial | Enterprise-scale repositories | Proprietary (NDA) | TBD | v2.0+ |

---

## 9. Repository Categories

### 9.1 Category 1: Synthetic Repositories

| Field | Specification |
|-------|--------------|
| **Purpose** | Controlled experiments where ground truth is known by construction |
| **Characteristics** | Deterministic generation, seed-controlled, pathology injection at specified windows |
| **Observation Profile** | Configurable: M-02 (always), M-06 (always), M-01/M-03/M-04/M-05/M-07 (optional artifacts) |
| **Detector Expectations** | D-01/D-02/D-03 detect injected anomalies with known severity |
| **Ground Truth** | Explicit: anomaly type, injection window, severity, expected metrics |
| **Validation Process** | Generator determinism test (same seed → identical output), injection verification |
| **Expansion Policy** | New pathology types added as new detectors are introduced |
| **Maintenance Policy** | Regenerate on detector algorithm changes; freeze on release |

### 9.2 Category 2: Real Open Source Repositories

| Field | Specification |
|-------|--------------|
| **Purpose** | Ecological validity — do detectors work on real software projects? |
| **Characteristics** | Public Git repositories, diverse languages, diverse project sizes, real commit histories |
| **Observation Profile** | M-02 and M-06 always; M-01 (if coverage artifacts), M-03/M-04 (if PR data), M-07 (if AST available) |
| **Detector Expectations** | Detectors produce meaningful results; no expected anomaly type (exploratory) |
| **Ground Truth** | Expert annotation via dual-reviewer + adjudication process |
| **Validation Process** | Annotation consistency (Cohen's κ ≥ 0.70), adjudication for disagreements |
| **Expansion Policy** | Add 2-3 repositories per minor release; diversify languages and sizes |
| **Maintenance Policy** | Pin to specific commit hash; re-annotate only on major version changes |

### 9.3 Category 3: Edge-Case Repositories

| Field | Specification |
|-------|--------------|
| **Purpose** | Boundary conditions that may cause detector failure |
| **Characteristics** | Minimum samples (n=1, n=10, n=20), identical values, constant time series, single-commit windows |
| **Observation Profile** | Minimal: M-02 only (for D-01/D-02/D-03 edge cases) |
| **Detector Expectations** | Detectors handle gracefully — abort with exit 3 (validation error) or produce degenerate-but-defined results |
| **Ground Truth** | Explicit: expected behavior (abort, degenerate, normal) |
| **Validation Process** | Verify expected behavior matches actual behavior |
| **Expansion Policy** | Add edge cases discovered during validation or production use |
| **Maintenance Policy** | Regenerate on detector minimum-sample gate changes |

### 9.4 Category 4: Adversarial Repositories

| Field | Specification |
|-------|--------------|
| **Purpose** | Robustness to crafted inputs designed to evade detection |
| **Characteristics** | Gaming patterns, gradual drift below threshold, adversarial noise injection, metric manipulation |
| **Observation Profile** | M-02 and M-06 with adversarial manipulation |
| **Detector Expectations** | Detectors detect adversarial patterns or fail securely |
| **Ground Truth** | Explicit: adversarial pattern type, injection method, expected detection |
| **Validation Process** | Verify adversarial patterns are detected or handled gracefully |
| **Expansion Policy** | Add new adversarial patterns as they are discovered |
| **Maintenance Policy** | Update on detector threshold changes |

### 9.5 Category 5: Stress Repositories

| Field | Specification |
|-------|--------------|
| **Purpose** | Scalability and performance limits |
| **Characteristics** | Large sample sizes (n=100K), many windows (1000+), extreme value ranges |
| **Observation Profile** | M-02 and M-06 at scale |
| **Detector Expectations** | Detectors complete within performance targets (DES Section 26) |
| **Ground Truth** | Implicit: no anomaly expected; detector should complete without error |
| **Validation Process** | Execution time measurement, memory profiling, completion verification |
| **Expansion Policy** | Increase scale as MIIE performance improves |
| **Maintenance Policy** | Update performance targets per release |

### 9.6 Category 6: Temporal Evolution Repositories

| Field | Specification |
|-------|--------------|
| **Purpose** | Same repository at different development stages |
| **Characteristics** | Same repo sliced at 3+ time points (e.g., v1.0, v2.0, v3.0) |
| **Observation Profile** | Full metric set at each time point |
| **Detector Expectations** | Detectors produce stable results for similar stages, different results for different stages |
| **Ground Truth** | Expert annotation per time slice |
| **Validation Process** | Cross-slice consistency check |
| **Expansion Policy** | Add new time slices for repositories with major releases |
| **Maintenance Policy** | Re-annotate on detector threshold changes |

### 9.7 Category 7: Longitudinal Repositories

| Field | Specification |
|-------|--------------|
| **Purpose** | Detector performance stability over months/years |
| **Characteristics** | Same repository tracked at 5+ time points over 12+ months |
| **Observation Profile** | Full metric set at each time point |
| **Detector Expectations** | Detector performance is stable (Δ < 0.05) across time points |
| **Ground Truth** | Expert annotation per time point; drift labels for transitions |
| **Validation Process** | Longitudinal consistency: performance variance < 0.05 across time points |
| **Expansion Policy** | Add new time points quarterly |
| **Maintenance Policy** | Update with each minor release |

### 9.8 Category 8: Industrial Repositories (Future)

| Field | Specification |
|-------|--------------|
| **Purpose** | Enterprise-scale validation under real-world conditions |
| **Characteristics** | Proprietary repositories, large-scale, multi-team, CI/CD integrated |
| **Observation Profile** | Full metric set with proprietary extensions |
| **Detector Expectations** | Detectors perform at or above OSS benchmarks |
| **Ground Truth** | Proprietary expert annotation under NDA |
| **Validation Process** | Controlled access, embargo periods, anonymized results |
| **Expansion Policy** | Add via partnership agreements |
| **Maintenance Policy** | Per-partnership agreement |

---

## 10. Benchmark Metadata Schema

### 10.1 Metadata Overview

Every benchmark repository MUST define a complete metadata record. The metadata schema ensures consistent documentation, reproducibility, and machine-readability across the entire benchmark corpus.

### 10.2 Schema Definition

```
┌─────────────────────────────────────────────────────────────────┐
│                  BENCHMARK METADATA SCHEMA                       │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  SECTION 1: Identity                                        ││
│  │  ├── repository_id      (string, required)                  ││
│  │  ├── repository_name    (string, required)                  ││
│  │  ├── category           (enum, required)                    ││
│  │  ├── version            (semver, required)                  ││
│  │  └── license            (string, required)                  ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  SECTION 2: Description                                     ││
│  │  ├── description        (string, required)                  ││
│  │  ├── purpose            (string, required)                  ││
│  │  └── target_detectors   (list[string], required)            ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  SECTION 3: Characteristics                                 ││
│  │  ├── language           (string, required)                  ││
│  │  ├── commit_count       (integer, required)                 ││
│  │  ├── contributor_count  (integer, required)                 ││
│  │  ├── file_count         (integer, required)                 ││
│  │  ├── loc_count          (integer, optional)                 ││
│  │  ├── duration_days      (integer, required)                 ││
│  │  └── size_tier          (enum: small|medium|large)          ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  SECTION 4: Observation Profile                             ││
│  │  ├── available_metrics  (list[metric_id], required)         ││
│  │  ├── extraction_sources (list[string], required)            ││
│  │  └── window_config      (object, required)                  ││
│  │       ├── strategy      (enum: time|commit|hybrid)          ││
│  │       ├── window_size   (integer, required)                 ││
│  │       └── window_count  (integer, required)                 ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  SECTION 5: Ground Truth                                    ││
│  │  ├── ground_truth_method (enum: synthetic|expert|hybrid)    ││
│  │  ├── expected_findings   (list[finding], required)          ││
│  │  │    ├── anomaly_type    (string, required)                ││
│  │  │    ├── severity_range  (float[2], required)              ││
│  │  │    ├── affected_metrics (list[metric_id], required)      ││
│  │  │    └── affected_windows (list[window_id], required)      ││
│  │  └── ground_truth_version (semver, required)                ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  SECTION 6: Complexity                                      ││
│  │  ├── difficulty          (enum: trivial|easy|medium|hard)   ││
│  │  ├── expected_tp         (integer, required)                ││
│  │  ├── expected_fp         (integer, required)                ││
│  │  ├── expected_fn         (integer, required)                ││
│  │  └── expected_tn         (integer, required)                ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  SECTION 7: Provenance                                      ││
│  │  ├── source_url          (string, optional)                 ││
│  │  ├── commit_hash         (string, required)                 ││
│  │  ├── generation_seed     (integer, optional)                ││
│  │  ├── generation_timestamp (ISO 8601, optional)              ││
│  │  └── maintenance_owner   (string, required)                 ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  SECTION 8: Annotations                                     ││
│  │  ├── annotation_method   (enum: dual-reviewer|expert|auto)  ││
│  │  ├── inter_rater_kappa   (float, optional)                  ││
│  │  ├── adjudication_count  (integer, optional)                ││
│  │  └── annotation_date     (ISO 8601, required)               ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 10.3 Metadata Field Definitions

#### 10.3.1 Identity Fields

| Field | Data Type | Required | Constraints | Description |
|-------|-----------|----------|-------------|-------------|
| `repository_id` | string | Yes | Pattern: `^[a-z0-9-]+$`, unique | Canonical identifier |
| `repository_name` | string | Yes | 1-200 characters | Human-readable name |
| `category` | enum | Yes | One of: synthetic, real_oss, edge_case, adversarial, stress, temporal, longitudinal, industrial | Benchmark category |
| `version` | semver | Yes | ≥ 1.0.0 | Metadata schema version |
| `license` | string | Yes | OSI-approved SPDX identifier | Repository license |

#### 10.3.2 Description Fields

| Field | Data Type | Required | Constraints | Description |
|-------|-----------|----------|-------------|-------------|
| `description` | string | Yes | 10-1000 characters | Plain-language description |
| `purpose` | string | Yes | 10-500 characters | Why this benchmark exists |
| `target_detectors` | list[string] | Yes | Non-empty, valid detector IDs | Which detectors this benchmark targets |

#### 10.3.3 Characteristic Fields

| Field | Data Type | Required | Constraints | Description |
|-------|-----------|----------|-------------|-------------|
| `language` | string | Yes | Primary programming language | Repository language |
| `commit_count` | integer | Yes | ≥ 1 | Total commits in repository |
| `contributor_count` | integer | Yes | ≥ 1 | Distinct contributors |
| `file_count` | integer | Yes | ≥ 1 | Total tracked files |
| `loc_count` | integer | Optional | ≥ 0 | Lines of code (excluding blanks/comments) |
| `duration_days` | integer | Yes | ≥ 1 | Repository history span in days |
| `size_tier` | enum | Yes | small, medium, large | Size classification per fixture requirements |

#### 10.3.4 Observation Profile Fields

| Field | Data Type | Required | Constraints | Description |
|-------|-----------|----------|-------------|-------------|
| `available_metrics` | list[metric_id] | Yes | Subset of M-01 through M-07 | Metrics extractable from this repo |
| `extraction_sources` | list[string] | Yes | Valid extraction source types | Data sources used for extraction |
| `window_config.strategy` | enum | Yes | time, commit, hybrid | Windowing strategy |
| `window_config.window_size` | integer | Yes | ≥ 2 | Size of each window |
| `window_config.window_count` | integer | Yes | ≥ 2 | Number of windows |

#### 10.3.5 Ground Truth Fields

| Field | Data Type | Required | Constraints | Description |
|-------|-----------|----------|-------------|-------------|
| `ground_truth_method` | enum | Yes | synthetic, expert, hybrid | How ground truth was established |
| `expected_findings` | list[finding] | Yes | Non-empty for anomaly-bearing repos | List of expected anomalies |
| `expected_findings.anomaly_type` | string | Yes | Valid anomaly type | Type of expected anomaly |
| `expected_findings.severity_range` | float[2] | Yes | [0.0, 1.0], min ≤ max | Expected severity range |
| `expected_findings.affected_metrics` | list[metric_id] | Yes | Non-empty | Metrics affected by anomaly |
| `expected_findings.affected_windows` | list[window_id] | Yes | Non-empty | Windows affected by anomaly |
| `ground_truth_version` | semver | Yes | ≥ 1.0.0 | Ground truth dataset version |

#### 10.3.6 Complexity Fields

| Field | Data Type | Required | Constraints | Description |
|-------|-----------|----------|-------------|-------------|
| `difficulty` | enum | Yes | trivial, easy, medium, hard | Assessment difficulty |
| `expected_tp` | integer | Yes | ≥ 0 | Expected true positives |
| `expected_fp` | integer | Yes | ≥ 0 | Expected false positives |
| `expected_fn` | integer | Yes | ≥ 0 | Expected false negatives |
| `expected_tn` | integer | Yes | ≥ 0 | Expected true negatives |

#### 10.3.7 Provenance Fields

| Field | Data Type | Required | Constraints | Description |
|-------|-----------|----------|-------------|-------------|
| `source_url` | string | Optional | Valid URL | Repository URL (for real OSS) |
| `commit_hash` | string | Yes | Valid Git SHA | Pinned commit for reproducibility |
| `generation_seed` | integer | Optional | ≥ 0 | Seed used for generation (synthetic) |
| `generation_timestamp` | ISO 8601 | Optional | Valid datetime | When generated |
| `maintenance_owner` | string | Yes | Valid contact | Responsible party |

#### 10.3.8 Annotation Fields

| Field | Data Type | Required | Constraints | Description |
|-------|-----------|----------|-------------|-------------|
| `annotation_method` | enum | Yes | dual-reviewer, expert, auto | Annotation approach |
| `inter_rater_kappa` | float | Optional | [0.0, 1.0] | Cohen's κ (dual-reviewer only) |
| `adjudication_count` | integer | Optional | ≥ 0 | Number of adjudicated disagreements |
| `annotation_date` | ISO 8601 | Yes | Valid datetime | When annotation was completed |

---

## 11. Repository Lifecycle

### 11.1 Lifecycle Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    REPOSITORY LIFECYCLE                               │
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐  │
│  │  CREATE   │───►│ VALIDATE │───►│CERTIFY   │───►│  PUBLISH     │  │
│  │           │    │          │    │          │    │              │  │
│  │ Generate  │    │ Verify   │    │ Approve  │    │ Release to   │  │
│  │ or select │    │ quality  │    │ for use  │    │ benchmark    │  │
│  │ repository│    │ criteria │    │ criteria │    │ corpus       │  │
│  └──────────┘    └────┬─────┘    └──────────┘    └──────┬───────┘  │
│                       │                                  │          │
│                       │ FAIL                             │          │
│                       ▼                                  │          │
│                 ┌──────────┐                             │          │
│                 │  REJECT   │                             │          │
│                 │           │                             │          │
│                 │ Document  │                             │          │
│                 │ failure   │                             │          │
│                 │ reason    │                             │          │
│                 └──────────┘                             │          │
│                                                          │          │
│  ┌──────────────────────────────────────────────────────▼───────┐  │
│  │                     ACTIVE USE                               │  │
│  │                                                              │  │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────────────────┐  │  │
│  │  │ VERSION   │───►│DEPRECATE │───►│    REPLACE           │  │  │
│  │  │           │    │          │    │                      │  │  │
│  │  │ Update    │    │ Mark as  │    │ Substitute with      │  │  │
│  │  │ metadata, │    │ superseded│   │ newer version        │  │  │
│  │  │ ground    │    │ by newer │    │                      │  │  │
│  │  │ truth     │    │ version  │    │                      │  │  │
│  │  └──────────┘    └──────────┘    └──────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 11.2 Lifecycle States

| State | Definition | Entry Criteria | Exit Criteria |
|-------|-----------|---------------|---------------|
| **Created** | Repository generated or selected | Generation script executed or repository cloned | Structural validation passed |
| **Validated** | Quality criteria verified | All metadata fields populated, ground truth verified | Certification criteria met |
| **Certified** | Approved for benchmark use | All acceptance criteria met (Section 26) | Published to corpus |
| **Published** | Active in benchmark corpus | Published with version tag | Deprecated or versioned |
| **Versioned** | Updated with new metadata/ground truth | New version committed | Re-certified |
| **Deprecated** | Superseded by newer version | Deprecation notice published | Replaced or archived |
| **Rejected** | Failed validation | Validation failure documented | N/A (terminal state) |

### 11.3 Lifecycle Transitions

| From | To | Trigger | Authority |
|------|----|---------|-----------|
| Created | Validated | Structural validation passes | Automated |
| Created | Rejected | Structural validation fails | Automated |
| Validated | Certified | All acceptance criteria met | Benchmark Architect |
| Validated | Rejected | Acceptance criteria not met | Benchmark Architect |
| Certified | Published | Published to corpus | Release Engineer |
| Published | Versioned | New version committed | Benchmark Architect |
| Published | Deprecated | Deprecation notice published | Benchmark Architect |
| Deprecated | Replaced | Newer version published | Benchmark Architect |

---

## 12. Benchmark Dataset Structure

### 12.1 Directory Structure

```
benchmarks/
├── datasets/
│   ├── synthetic/
│   │   ├── SYN-D01/                    # D-01 targeted synthetic datasets
│   │   │   ├── SYN-D01-01/
│   │   │   │   ├── metadata.json
│   │   │   │   ├── ground_truth.json
│   │   │   │   ├── observations/
│   │   │   │   └── repository/          # Git repository
│   │   │   ├── SYN-D01-02/
│   │   │   └── ...
│   │   ├── SYN-D02/                    # D-02 targeted synthetic datasets
│   │   └── SYN-D03/                    # D-03 targeted synthetic datasets
│   ├── real_oss/
│   │   ├── ROSS-001/
│   │   │   ├── metadata.json
│   │   │   ├── ground_truth.json
│   │   │   ├── observations/
│   │   │   └── repository/              # Pinned commit
│   │   └── ...
│   ├── edge_case/
│   │   ├── EC-001/
│   │   └── ...
│   ├── adversarial/
│   │   ├── ADV-001/
│   │   └── ...
│   ├── stress/
│   │   ├── STR-001/
│   │   └── ...
│   ├── temporal/
│   │   ├── TMP-001/
│   │   │   ├── TMP-001-t0/
│   │   │   ├── TMP-001-t1/
│   │   │   └── TMP-001-t2/
│   │   └── ...
│   └── longitudinal/
│       ├── LNG-001/
│       │   ├── LNG-001-t0/
│       │   ├── LNG-001-t1/
│       │   ├── LNG-001-t2/
│       │   ├── LNG-001-t3/
│       │   └── LNG-001-t4/
│       └── ...
├── ground_truth/
│   ├── synthetic/
│   │   ├── ground_truth_v1.0.0.json
│   │   └── ground_truth_v1.1.0.json
│   ├── real_oss/
│   │   └── ground_truth_v1.0.0.json
│   ├── annotations/
│   │   ├── reviewer_a/
│   │   ├── reviewer_b/
│   │   └── adjudication/
│   └── inter_rater/
│       └── kappa_scores.json
├── metadata/
│   ├── benchmark_manifest.json
│   ├── category_index.json
│   └── detector_coverage.json
├── results/
│   ├── evaluation_results/
│   │   ├── v1.0.0/
│   │   └── v1.1.0/
│   └── benchmark_summary.json
└── BES_v1.0_Benchmark_Evolution_Specification.md
```

### 12.2 File Specifications

#### 12.2.1 metadata.json

Every benchmark repository MUST contain a `metadata.json` file conforming to the schema in Section 10. This file is the canonical record of the repository's characteristics, ground truth, and provenance.

#### 12.2.2 ground_truth.json

Every benchmark repository MUST contain a `ground_truth.json` file defining expected findings. This file is the authoritative source for evaluation.

#### 12.2.3 observations/ Directory

The `observations/` directory contains pre-extracted observation data conforming to the ODSS. This directory is optional for synthetic repositories (observations can be extracted at evaluation time) but required for real OSS repositories (to pin extraction results).

#### 12.2.4 repository/ Directory

The `repository/` directory contains the Git repository itself, pinned to a specific commit hash. For synthetic repositories, this is the generated repository. For real OSS repositories, this is a shallow clone at the pinned commit.

---

## 13. Ground Truth Strategy

### 13.1 Ground Truth Philosophy

Ground truth is the foundation of benchmark evaluation. Without reliable ground truth, evaluation metrics are meaningless. The BES establishes a multi-method ground truth strategy that triangulates from multiple independent sources.

```
┌─────────────────────────────────────────────────────────────────┐
│                GROUND TRUTH STRATEGY                             │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │    CONSTRUCTION   │  │    EXPERT        │  │  STATISTICAL  │ │
│  │    (Synthetic)    │  │    LABELING      │  │  VALIDATION   │ │
│  │                   │  │    (Real OSS)    │  │  (Cross-check)│ │
│  │  Ground truth     │  │  Dual-reviewer   │  │  Independent  │ │
│  │  known by         │  │  adjudication    │  │  statistical  │ │
│  │  construction     │  │  process         │  │  verification │ │
│  └────────┬──────────┘  └────────┬─────────┘  └──────┬────────┘ │
│           │                      │                    │          │
│           └──────────────────────┼────────────────────┘          │
│                                  │                               │
│                         ┌────────▼────────┐                      │
│                         │  GROUND TRUTH   │                      │
│                         │  CONSOLIDATED   │                      │
│                         │  (Final labels) │                      │
│                         └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

### 13.2 Ground Truth Methods

| Method | Applicability | Reliability | Cost | Maintenance |
|--------|-------------|-------------|------|-------------|
| Construction | Synthetic repos | HIGH (deterministic) | LOW | Regenerate on parameter change |
| Expert labeling | Real OSS repos | HIGH (if κ ≥ 0.70) | HIGH | Re-label on major changes |
| Statistical validation | All repos | MEDIUM (corroborative) | MEDIUM | Automatic |
| Community contribution | Future repos | VARIABLE | MEDIUM | Review required |

### 13.3 Ground Truth for Each Category

| Category | Primary Method | Secondary Method | Verification |
|----------|---------------|-----------------|-------------|
| Synthetic | Construction | Statistical validation | Determinism test |
| Real OSS | Expert labeling | Statistical validation | Inter-rater κ |
| Edge-Case | Construction | — | Behavioral verification |
| Adversarial | Construction | Expert review | Detection verification |
| Stress | Implicit (no anomaly) | — | Completion verification |
| Temporal | Expert labeling | Cross-slice consistency | Longitudinal stability |
| Longitudinal | Expert labeling | Cross-time consistency | Performance stability |
| Industrial | Expert labeling (NDA) | Statistical validation | Controlled access |

### 13.4 Ground Truth Versioning

Ground truth datasets are versioned independently from benchmark repositories:

| Version Component | Increment When | Example |
|------------------|----------------|---------|
| Major | Ground truth methodology changes | 1.0.0 → 2.0.0 |
| Minor | New labels added, labels corrected | 1.0.0 → 1.1.0 |
| Patch | Documentation, formatting | 1.0.0 → 1.0.1 |

---

## 14. Labeling Methodology

### 14.1 Annotation Process

The labeling methodology follows a three-stage process:

```
┌─────────────────────────────────────────────────────────────────┐
│                  ANNOTATION PROCESS                              │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │   STAGE 1        │  │   STAGE 2        │  │   STAGE 3     │ │
│  │   REVIEWER A     │  │   REVIEWER B     │  │   ADJUDICATION│ │
│  │                  │  │                  │  │               │ │
│  │  Independent     │  │  Independent     │  │  Resolve      │ │
│  │  annotation of   │  │  annotation of   │  │  discrepancies│ │
│  │  each candidate  │  │  same candidates │  │  between A/B  │ │
│  │                  │  │  (no A access)   │  │               │ │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬────────┘ │
│           │                     │                    │          │
│           │  ┌──────────────────┴──────────┐         │          │
│           │  │  Cohen's κ Computation      │         │          │
│           │  │  κ ≥ 0.70: Accept           │         │          │
│           │  │  κ < 0.70: Re-annotate      │         │          │
│           │  └─────────────────────────────┘         │          │
│           │                                          │          │
│           └──────────────────┬───────────────────────┘          │
│                              │                                   │
│                     ┌────────▼────────┐                          │
│                     │  FINAL LABELS   │                          │
│                     │  Published to   │                          │
│                     │  ground_truth/  │                          │
│                     └─────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

### 14.2 Annotation Schema

Each annotation follows this schema:

| Field | Data Type | Required | Description |
|-------|-----------|----------|-------------|
| `candidate_id` | string | Yes | Benchmark candidate identifier |
| `annotator` | string | Yes | Annotator identifier |
| `timestamp` | ISO 8601 | Yes | Annotation timestamp |
| `anomaly_present` | boolean | Yes | Whether anomaly is present |
| `anomaly_types` | list[string] | Yes | Types of anomalies detected |
| `severity` | enum | Yes | low, medium, high |
| `confidence` | float | Yes | Annotator confidence [0.0, 1.0] |
| `metrics_affected` | list[string] | Yes | MIIE metrics affected |
| `windows_affected` | list[string] | Yes | Windows where anomaly detected |
| `notes` | string | Optional | Free-text notes |

### 14.3 Inter-Rater Agreement

| Metric | Target | Action if Below Target |
|--------|--------|----------------------|
| Cohen's κ | ≥ 0.70 | Re-annotate with calibration session |
| Percent agreement | ≥ 0.80 | Adjudicate all disagreements |
| Disagreement rate | ≤ 0.20 | Review annotation guidelines |

### 14.4 Adjudication Process

When Reviewer A and Reviewer B disagree:

1. Adjudicator reviews both annotations independently
2. Adjudicator examines the benchmark repository evidence
3. Adjudicator produces a final label with justification
4. Disagreement is logged for annotation guideline improvement
5. Final label is published to `ground_truth/annotations/adjudication/`

---

## 15. Detector Coverage Matrix

### 15.1 Coverage Definition

The detector coverage matrix specifies which benchmarks target which detectors. Every detector must have sufficient benchmark coverage to satisfy DSVP acceptance criteria.

### 15.2 Current Detector Coverage

| Benchmark Category | D-01 (Distributional Drift) | D-02 (Correlation Breakdown) | D-03 (Threshold Compression) |
|-------------------|---------------------------|---------------------------|---------------------------|
| Synthetic | SYN-D01-01 through SYN-D01-10 | SYN-D02-01 through SYN-D02-10 | SYN-D03-01 through SYN-D03-10 |
| Real OSS | ROSS-001 through ROSS-010 | ROSS-001 through ROSS-010 | ROSS-001 through ROSS-010 |
| Edge-Case | EC-001 through EC-004 | EC-005 through EC-007 | EC-008 through EC-010 |
| Adversarial | ADV-001 through ADV-002 | ADV-003 through ADV-004 | ADV-005 through ADV-006 |
| Stress | STR-001 | STR-002 | STR-003 |
| Temporal | TMP-001 through TMP-005 | TMP-001 through TMP-005 | TMP-001 through TMP-005 |
| Longitudinal | LNG-001 through LNG-003 | LNG-001 through LNG-003 | LNG-001 through LNG-003 |

### 15.3 Coverage Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Synthetic datasets per detector | 10 | 15 |
| Real OSS repositories per detector | 5 | 10 |
| Edge-case scenarios per detector | 3 | 5 |
| Adversarial scenarios per detector | 2 | 4 |
| Stress tests per detector | 1 | 2 |
| Temporal evolution repos per detector | 3 | 5 |
| Longitudinal repos per detector | 2 | 3 |

### 15.4 Coverage Gaps and Future Expansion

| Gap | Current State | Target State | Timeline |
|-----|-------------|-------------|----------|
| Cross-language coverage | Python-dominant | Python, Java, JavaScript, TypeScript | v1.6 |
| Industrial coverage | None | 5+ enterprise repositories | v2.0 |
| Community-contributed | None | 10+ external contributions | v1.6 |

---

## 16. Evaluation Methodology

### 16.1 Evaluation Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      EVALUATION PIPELINE                                 │
│                                                                          │
│  ┌──────────────┐                                                        │
│  │  1. SELECT   │  Choose benchmark dataset by category, detector       │
│  │  BENCHMARK   │  target, difficulty                                    │
│  └──────┬───────┘                                                        │
│         │                                                                │
│  ┌──────▼───────┐                                                        │
│  │  2. EXTRACT  │  Run Observation Engine over benchmark repository     │
│  │  OBSERVATIONS│  Produce ObservationCollection per ODSS               │
│  └──────┬───────┘                                                        │
│         │                                                                │
│  ┌──────▼───────┐                                                        │
│  │  3. BUILD    │  WindowBuilder creates ObservationWindows             │
│  │  WINDOWS     │  per OEAS L4 specification                            │
│  └──────┬───────┘                                                        │
│         │                                                                │
│  ┌──────▼───────┐                                                        │
│  │  4. EXECUTE  │  DetectorAdapter translates to MetricDataFrame        │
│  │  DETECTORS   │  Detectors execute per DES specification              │
│  └──────┬───────┘                                                        │
│         │                                                                │
│  ┌──────▼───────┐                                                        │
│  │  5. COMPARE  │  Detector outputs compared to ground truth labels     │
│  │  GROUND TRUTH│  TP/FP/FN/TN computed per window                     │
│  └──────┬───────┘                                                        │
│         │                                                                │
│  ┌──────▼───────┐                                                        │
│  │  6. COMPUTE  │  Precision, Recall, F1, AUC-ROC, FPR, FNR,          │
│  │  METRICS     │  Confidence intervals, Effect sizes                   │
│  └──────┬───────┘                                                        │
│         │                                                                │
│  ┌──────▼───────┐                                                        │
│  │  7. STATISTICAL EVALUATION                                           │
│  │              │  Hypothesis tests, p-values, power analysis           │
│  └──────┬───────┘                                                        │
│         │                                                                │
│  ┌──────▼───────┐                                                        │
│  │  8. CERTIFY  │  Compare to acceptance criteria (Section 26)          │
│  │  RESULTS     │  PASS / CONDITIONAL PASS / FAIL                       │
│  └──────────────┘                                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

### 16.2 Evaluation Metrics

#### 16.2.1 Classification Metrics

| Metric | Formula | Target | Interpretation |
|--------|---------|--------|---------------|
| Precision | TP / (TP + FP) | Per DSVP Table 17 | How many detected anomalies are real |
| Recall | TP / (TP + FN) | Per DSVP Table 17 | How many real anomalies are detected |
| F1 | 2 × (P × R) / (P + R) | ≥ 0.75 | Harmonic mean of precision and recall |
| Accuracy | (TP + TN) / (TP + TN + FP + FN) | ≥ 0.80 | Overall correctness |
| FPR | FP / (FP + TN) | < 0.10 | False alarm rate |
| FNR | FN / (FN + TP) | < 0.20 | Miss rate |

#### 16.2.2 Advanced Metrics

| Metric | Purpose | Computation |
|--------|---------|-------------|
| AUC-ROC | Threshold-independent performance | Area under ROC curve |
| AUC-PR | Performance on imbalanced datasets | Area under Precision-Recall curve |
| Cohen's κ | Agreement beyond chance | (p_o - p_e) / (1 - p_e) |
| Matthews Correlation Coefficient | Balanced measure for imbalanced classes | (TP×TN - FP×FN) / √((TP+FP)(TP+FN)(TN+FP)(TN+FN)) |

### 16.3 Baseline Comparisons

Every evaluation MUST include comparison against four baselines:

| Baseline | Description | Implementation |
|----------|-------------|---------------|
| Random | 50/50 random prediction | `random_baseline()` |
| Majority Class | Always predict the majority class | `majority_class_baseline()` |
| Statistical | Sample according to class priors | `statistical_baseline()` |
| Rule-Based | Simple heuristic rules | `rule_based_baseline()` |

---

## 17. Statistical Evaluation

### 17.1 Statistical Rigor Requirements

| Requirement | Specification |
|-------------|--------------|
| Confidence intervals | 95% CI for all primary metrics |
| Hypothesis tests | Per DSVP Section 8 |
| Effect size | Cohen's d for pairwise comparisons |
| Multiple comparisons | Bonferroni correction for family-wise error |
| Power analysis | Post-hoc power computation for all tests |

### 17.2 Confidence Interval Computation

For each metric (precision, recall, F1), compute 95% confidence intervals using the Wilson score interval:

```
CI = (p̂ + z²/2n ± z√(p̂(1-p̂)/n + z²/4n²)) / (1 + z²/n)
```

where p̂ is the sample proportion, n is the sample size, and z = 1.96 for 95% confidence.

### 17.3 Hypothesis Testing Framework

| Test | When to Use | Significance Level | Correction |
|------|------------|-------------------|------------|
| Two-proportion z-test | Comparing detection rates across conditions | α = 0.05 | Bonferroni |
| One-sided t-test | Comparing metric means (PSI, z-scores) | α = 0.05 | Bonferroni |
| Binomial test | Classification accuracy vs. chance | α = 0.05 | None |
| Kolmogorov-Smirnov test | Distribution comparison | α = 0.05 | None |
| Fisher's exact test | Small-sample contingency tables | α = 0.05 | None |

### 17.4 Effect Size Computation

| Effect Size | When to Use | Thresholds |
|-------------|------------|------------|
| Cohen's d | Comparing two means | Small: 0.2, Medium: 0.5, Large: 0.8 |
| Cohen's h | Comparing two proportions | Small: 0.2, Medium: 0.5, Large: 0.8 |
| Odds Ratio | Association strength | OR > 2.0 meaningful |

---

## 18. Benchmark Versioning

### 18.1 Versioning Strategy

Benchmarks follow semantic versioning (semver):

```
┌─────────────────────────────────────────────────────────────────┐
│                    BENCHMARK VERSIONING                           │
│                                                                  │
│  MAJOR.MINOR.PATCH                                               │
│                                                                  │
│  MAJOR: Breaking changes in ground truth methodology,            │
│         annotation schema, or evaluation framework               │
│         (v1.0.0 → v2.0.0)                                       │
│                                                                  │
│  MINOR: New benchmarks added, new categories introduced,         │
│         ground truth labels corrected, metadata extended         │
│         (v1.0.0 → v1.1.0)                                       │
│                                                                  │
│  PATCH: Documentation fixes, metadata corrections,               │
│         annotation clarifications                                │
│         (v1.0.0 → v1.0.1)                                       │
└─────────────────────────────────────────────────────────────────┘
```

### 18.2 Version Compatibility

| Change Type | Version Impact | Backward Compatible |
|-------------|---------------|-------------------|
| Add new benchmark repository | Minor | Yes |
| Modify ground truth labels | Minor | No (re-evaluate all results) |
| Change annotation schema | Major | No |
| Add new benchmark category | Minor | Yes |
| Modify evaluation metrics | Major | No |
| Fix metadata documentation | Patch | Yes |
| Change benchmark directory structure | Major | No |

### 18.3 Version History

| Version | Date | Changes | Impact |
|---------|------|---------|--------|
| 1.0.0 | 2026-06-29 | Initial benchmark ecosystem | None (new) |

---

## 19. Certification Process

### 19.1 Certification Overview

Every benchmark must be certified before inclusion in the active corpus. Certification verifies that the benchmark meets quality standards for scientific validation.

### 19.2 Certification Criteria

| ID | Criterion | Priority | Verification |
|----|-----------|----------|-------------|
| CERT-1 | Metadata is complete and valid | HIGH | Schema validation |
| CERT-2 | Ground truth is established | HIGH | Ground truth file exists and is non-empty |
| CERT-3 | Ground truth is verified | HIGH | Dual-reviewer OR construction verified |
| CERT-4 | Inter-rater agreement meets threshold | HIGH (if expert) | κ ≥ 0.70 |
| CERT-5 | Repository is reproducible | HIGH | Determinism test (synthetic) or commit pin (real OSS) |
| CERT-6 | Detector coverage is sufficient | MEDIUM | ≥ 1 target detector |
| CERT-7 | Difficulty is correctly assessed | MEDIUM | Assessment matches actual evaluation |
| CERT-8 | License permits benchmarking | HIGH | OSI-approved license |
| CERT-9 | No sensitive data present | HIGH | Manual review |
| CERT-10 | Metadata version matches | LOW | Semver consistency |

### 19.3 Certification Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                  CERTIFICATION WORKFLOW                           │
│                                                                  │
│  ┌──────────────┐                                                │
│  │  SUBMIT      │  Benchmark author submits with metadata       │
│  └──────┬───────┘                                                │
│         │                                                        │
│  ┌──────▼───────┐                                                │
│  │  AUTOMATED   │  Schema validation, structural checks         │
│  │  VALIDATION  │  Determinism test (synthetic)                  │
│  └──────┬───────┘                                                │
│         │                                                        │
│  ┌──────▼───────┐                                                │
│  │  PEER        │  Independent reviewer verifies ground truth    │
│  │  REVIEW      │  Checks metadata accuracy                      │
│  └──────┬───────┘                                                │
│         │                                                        │
│  ┌──────▼───────┐                                                │
│  │  CERTIFY     │  Benchmark Architect approves                  │
│  │              │  Certification ID assigned                     │
│  └──────┬───────┘                                                │
│         │                                                        │
│  ┌──────▼───────┐                                                │
│  │  PUBLISH     │  Added to benchmark_manifest.json              │
│  │              │  Version tag applied                           │
│  └──────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 20. Repository Expansion Strategy

### 20.1 Expansion Principles

| Principle | Description |
|-----------|-------------|
| Coverage before quantity | Ensure each detector has sufficient coverage before adding more |
| Diversity over similarity | Prefer repositories with different characteristics |
| Quality over speed | Every addition must pass certification |
| Maintainability | Every addition must have a defined maintenance owner |

### 20.2 Expansion Roadmap

#### v1.5 (Current)

| Category | Current Count | Target Count | Priority |
|----------|-------------|-------------|----------|
| Synthetic | 30 | 30 | COMPLETE |
| Real OSS | 0 | 10 | HIGH |
| Edge-Case | 0 | 10 | HIGH |
| Adversarial | 0 | 6 | HIGH |
| Stress | 0 | 5 | MEDIUM |
| Temporal | 0 | 15 | MEDIUM |
| Longitudinal | 0 | 15 | LOW |

#### v1.6

| Category | Additions | Priority |
|----------|----------|----------|
| Real OSS | +5 repositories (diverse languages) | HIGH |
| Cross-language | +5 repositories (Java, JavaScript, TypeScript) | MEDIUM |
| Community-contributed | Accept external contributions | MEDIUM |

#### v2.0

| Category | Additions | Priority |
|----------|----------|----------|
| Industrial | +5 enterprise repositories (NDA) | MEDIUM |
| Large-scale | +3 repositories (100K+ commits) | LOW |

### 20.3 Repository Selection Criteria

When selecting new repositories for inclusion:

| Criterion | Weight | Minimum |
|-----------|--------|---------|
| Language diversity | 0.20 | ≥ 2 languages represented |
| Size diversity | 0.20 | All size tiers represented |
| Commit frequency diversity | 0.15 | Low, medium, high represented |
| Contributor diversity | 0.15 | Solo and multi-contributor |
| Metric availability | 0.15 | ≥ 3 metrics available |
| License compatibility | 0.15 | OSI-approved |

---

## 21. Community Contribution Strategy

### 21.1 Contribution Framework

The BES establishes a structured framework for community benchmark contributions:

| Contribution Type | Process | Review Requirements |
|------------------|---------|-------------------|
| New benchmark repository | Submit PR with metadata + ground truth | Peer review + certification |
| Ground truth correction | Submit issue with evidence | Benchmark Architect review |
| New benchmark category | RFC process | Architecture review |
| Evaluation methodology improvement | RFC with statistical justification | Methodology review |

### 21.2 Contribution Requirements

| Requirement | Specification |
|-------------|--------------|
| Metadata | Complete per Section 10 |
| Ground truth | Established per Section 13-14 |
| License | OSI-approved, permits benchmarking |
| Documentation | Purpose, characteristics, expected findings |
| Reproducibility | Deterministic (synthetic) or pinned commit (real OSS) |
| Maintenance | Contributor commits to 12-month maintenance |

### 21.3 Contribution Review Process

| Stage | Reviewer | Criteria |
|-------|---------|----------|
| Structural validation | Automated | Schema compliance, completeness |
| Ground truth verification | Peer reviewer | Label accuracy, inter-rater agreement |
| Scientific review | Benchmark Architect | Statistical validity, coverage contribution |
| Integration review | Release Engineer | Directory structure, manifest update |

---

## 22. Industrial Roadmap

### 22.1 Industrial Benchmark Vision

Industrial benchmarks provide enterprise-scale validation under real-world conditions. This is a v2.0+ capability requiring NDA frameworks, controlled access, and anonymized result publication.

### 22.2 Industrial Benchmark Requirements

| Requirement | Specification |
|-------------|--------------|
| Access control | NDA-gated, time-limited access |
| Anonymization | No proprietary code or data in published results |
| Evaluation | Controlled environment, reproducible |
| Publication | Aggregate metrics only, no repository-specific results |
| Maintenance | Per-partnership agreement |

### 22.3 Industrial Roadmap Timeline

| Phase | Timeline | Deliverable |
|-------|----------|-------------|
| Framework design | v1.6 | NDA template, access control design |
| Pilot partnerships | v1.7 | 2-3 enterprise partnerships |
| Initial benchmarks | v2.0 | 5+ industrial repositories |
| Scale | v2.1 | 15+ industrial repositories |

---

## 23. Reproducibility Requirements

### 23.1 Reproducibility Definition

A benchmark is reproducible if identical execution produces identical results across:

| Dimension | Requirement |
|-----------|-------------|
| Time | Same results on different days |
| Platform | Same results on Linux, macOS, Windows |
| Seed | Same results with same random seed |
| Configuration | Same results with same config |
| Version | Same results with same MIIE version |

### 23.2 Reproducibility Verification

| Verification | Method | Acceptance |
|-------------|--------|------------|
| Determinism test | Run 100 times with seed=42 | Identical results in all 100 runs |
| Cross-platform test | Run on Linux, macOS, Windows | Identical results (within floating-point tolerance) |
| Version pinning | Pin to specific MIIE version | Results reproducible with pinned version |
| Configuration pinning | Pin all configuration parameters | Results reproducible with pinned config |

### 23.3 Reproducibility Artifacts

| Artifact | Content | Storage |
|----------|---------|---------|
| Execution log | Complete execution trace | `results/execution_log.json` |
| Configuration snapshot | All parameters used | `results/config_snapshot.json` |
| Environment snapshot | Python version, OS, dependencies | `results/environment.json` |
| Seed log | All random seeds used | `results/seeds.json` |

---

## 24. Risk Analysis

### 24.1 Risk Register

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|-----------|
| R-1 | Ground truth labels are incorrect | MEDIUM | HIGH | Dual-reviewer process, adjudication, statistical validation |
| R-2 | Synthetic benchmarks do not represent real repositories | MEDIUM | MEDIUM | Real OSS benchmarks, cross-validation |
| R-3 | Benchmark corpus becomes stale | MEDIUM | MEDIUM | Expansion roadmap, community contributions |
| R-4 | Inter-rater agreement is low | LOW | HIGH | Calibration sessions, clear annotation guidelines |
| R-5 | Benchmark certification is too slow | MEDIUM | LOW | Automated validation, clear criteria |
| R-6 | Community contributions are low quality | MEDIUM | MEDIUM | Strict review process, maintenance requirements |
| R-7 | Industrial benchmarks are infeasible | LOW | LOW | NDA framework, pilot partnerships |
| R-8 | Evaluation metrics are misleading | LOW | HIGH | Multiple metrics, confidence intervals, effect sizes |
| R-9 | Benchmark versioning causes confusion | LOW | MEDIUM | Clear semver policy, deprecation notices |
| R-10 | Cross-platform reproducibility fails | LOW | MEDIUM | CI testing on multiple platforms |

---

## 25. Trade-off Analysis

### 25.1 Key Trade-offs

| Decision | Option A | Option B | Rationale |
|----------|---------|---------|-----------|
| Ground truth method | Expert-only (high quality, high cost) | Hybrid (expert + construction, balanced) | Hybrid: Synthetic for controlled experiments, expert for ecological validity |
| Annotation process | Single reviewer (fast, low cost) | Dual-reviewer + adjudication (slow, high quality) | Dual-reviewer: Scientific rigor requires independent verification |
| Benchmark count | Few benchmarks (low maintenance, low coverage) | Many benchmarks (high maintenance, high coverage) | Balanced: 61 benchmarks is sufficient for current detectors |
| Versioning strategy | Independent versioning (flexible, complex) | Tied to MIIE version (simple, less flexible) | Independent: Benchmarks evolve independently from MIIE |
| Community contribution | Closed (quality control, no external input) | Open (diverse input, quality risk) | Structured open: Quality control with clear contribution path |

### 25.2 Alternative Approaches Considered

| Approach | Rejected Because |
|----------|----------------|
| crowdsourced labeling | Quality control is too expensive for scientific benchmarks |
| automated ground truth generation only | Cannot validate ecological validity |
| single-reviewer annotation | Insufficient for scientific rigor |
| benchmark-per-commit | Too many benchmarks; impractical to maintain |
| continuous evaluation | Not yet; batch evaluation is sufficient for current scale |

---

## 26. Acceptance Criteria

### 26.1 Benchmark Acceptance Criteria

| ID | Criterion | Priority | Verification |
|----|-----------|----------|-------------|
| AC-1 | Metadata conforms to Section 10 schema | HIGH | Schema validation |
| AC-2 | Ground truth is established per Section 13 | HIGH | Ground truth file exists |
| AC-3 | Ground truth labels are verified | HIGH | Dual-reviewer OR construction verified |
| AC-4 | Inter-rater κ ≥ 0.70 (if expert-labeled) | HIGH | κ computation |
| AC-5 | Repository is reproducible (synthetic) | HIGH | 100-run determinism test |
| AC-6 | Repository is pinned (real OSS) | HIGH | Commit hash verified |
| AC-7 | ≥ 1 target detector specified | MEDIUM | Metadata field |
| AC-8 | Difficulty assessment is correct | MEDIUM | Post-evaluation verification |
| AC-9 | License permits benchmarking | HIGH | OSI-approved license |
| AC-10 | No sensitive data present | HIGH | Manual review |

### 26.2 Evaluation Acceptance Criteria

| ID | Criterion | Priority | Verification |
|----|-----------|----------|-------------|
| EAC-1 | Precision ≥ target per DSVP Table 17 | HIGH | Evaluation report |
| EAC-2 | Recall ≥ target per DSVP Table 17 | HIGH | Evaluation report |
| EAC-3 | F1 ≥ 0.75 | HIGH | Evaluation report |
| EAC-4 | FPR < 0.10 under no-anomaly conditions | HIGH | Evaluation report |
| EAC-5 | 95% CI computed for all primary metrics | MEDIUM | Evaluation report |
| EAC-6 | All baseline comparisons included | MEDIUM | Evaluation report |
| EAC-7 | Results are reproducible (100-run test) | HIGH | Reproducibility report |
| EAC-8 | Statistical significance achieved (p < 0.05) | HIGH | Hypothesis test results |

---

## 27. Future Evolution

### 27.1 Evolution Roadmap

| Version | Benchmark Evolution | Detector Support | Evaluation Evolution |
|---------|-------------------|-----------------|---------------------|
| v1.5 | Core corpus: 61 benchmarks | D-01, D-02, D-03 | Basic metrics + baselines |
| v1.6 | +10 real OSS, +5 cross-language | D-01, D-02, D-03 | +Confidence intervals, effect sizes |
| v1.7 | Community contributions enabled | D-01, D-02, D-03 | +Hypothesis testing framework |
| v2.0 | Industrial benchmarks | Future detectors | +Automated certification |
| v2.1 | Scale (100+ benchmarks) | All detectors | +Longitudinal tracking dashboard |

### 27.2 Future Detector Families

The benchmark ecosystem is designed to support future detector families without redesign:

| Future Detector | Benchmark Requirements | Category Impact |
|----------------|----------------------|----------------|
| Temporal pattern detector | Time-series benchmarks | Expand temporal category |
| Cross-metric dependency detector | Multi-metric benchmarks | Expand synthetic category |
| Anomaly severity estimator | Severity-labeled benchmarks | Extend ground truth schema |
| Multi-repository detector | Cross-repository benchmarks | New cross-repository category |

### 27.3 Evaluation Evolution

| Current | Future | Rationale |
|---------|--------|-----------|
| Binary classification metrics | Ordinal severity metrics | More granular evaluation |
| Per-detector evaluation | Cross-detector evaluation | System-level assessment |
| Static benchmarks | Adaptive benchmarks | Self-improving benchmark corpus |
| Manual certification | Automated certification | Scalability |

---

## 28. Glossary

| Term | Definition |
|------|-----------|
| **Anomaly** | A deviation from expected repository behavior detected by a MIIE detector |
| **Benchmark** | A standardized dataset with known characteristics used for detector evaluation |
| **Benchmark Corpus** | The complete collection of benchmark datasets |
| **Certification** | The process of verifying a benchmark meets quality standards |
| **Confidence Interval** | A range of values likely to contain the true metric value |
| **Construct Validity** | The degree to which a measurement measures what it claims to measure |
| **Ecological Validity** | The degree to which findings generalize to real-world settings |
| **Effect Size** | A quantitative measure of the magnitude of a phenomenon |
| **Ground Truth** | The authoritative set of labels defining expected detector behavior |
| **Inter-Rater Agreement** | The degree of agreement between independent annotators |
| **Observation** | A single data point extracted from a repository (per ODSS) |
| **Pathology** | An injected or naturally occurring anomaly in a benchmark repository |
| **Precision** | The proportion of detected anomalies that are real |
| **Recall** | The proportion of real anomalies that are detected |
| **Reproducibility** | The ability to reproduce identical results given identical inputs |
| **Synthetic Repository** | A repository generated programmatically with controlled characteristics |
| **Temporal Evolution** | Changes in repository behavior over time |
| **Window** | A time-bounded subset of observations used for detector analysis |

---

## 29. Appendix

### 29.1 Current Benchmark Inventory

#### Synthetic Benchmarks (30 candidates)

| ID | Pathology Type | Target Detector | Category | Difficulty |
|----|---------------|----------------|----------|------------|
| candidate_001-040 | metric-drift | D-01 | synthetic | medium |
| candidate_041-080 | correlation-breakdown | D-02 | synthetic | medium |
| candidate_081-120 | threshold-compression | D-03 | synthetic | medium |

#### Existing Benchmark Infrastructure

| Component | File | Purpose |
|-----------|------|---------|
| Generator | `src/miie/benchmark/generator.py` | Synthetic repository generation |
| Runner | `src/miie/benchmark/runner.py` | Benchmark suite execution |
| Evaluation | `src/miie/benchmark/evaluation.py` | Classification metric computation |
| Ground Truth | `benchmarks/ground_truth/ground_truth.py` | Ground truth loading and evaluation |
| Manifest | `benchmarks/metadata/candidate_manifest.json` | Benchmark candidate metadata |
| Annotation Workflow | `benchmarks/annotations/annotation_workflow.md` | Dual-reviewer annotation process |

### 29.2 Mapping to DSVP Validation Datasets

| DSVP Dataset Category | BES Category | Count | Mapping |
|----------------------|-------------|-------|---------|
| SYN-D01-01 through SYN-D01-10 | Synthetic (D-01 targeted) | 10 | Direct mapping |
| SYN-D02-01 through SYN-D02-10 | Synthetic (D-02 targeted) | 10 | Direct mapping |
| SYN-D03-01 through SYN-D03-10 | Synthetic (D-03 targeted) | 10 | Direct mapping |
| Real OSS (D-01) | Real OSS (ROSS) | 10 | Direct mapping |
| Real OSS (D-02) | Real OSS (ROSS) | 10 | Shared with D-01 |
| Real OSS (D-03) | Real OSS (ROSS) | 10 | Shared with D-01 |
| Edge-Case (D-01) | Edge-Case (EC) | 10 | Direct mapping |
| Edge-Case (D-02) | Edge-Case (EC) | 10 | Shared with D-01 |
| Edge-Case (D-03) | Edge-Case (EC) | 10 | Shared with D-01 |
| Adversarial | Adversarial (ADV) | 6 | Direct mapping |
| Stress | Stress (STR) | 5 | Direct mapping |

### 29.3 Mapping to Existing Benchmark Infrastructure

| BES Component | Existing Implementation | Gap |
|--------------|------------------------|-----|
| Benchmark Generator | `BenchmarkDatasetGenerator` in `generator.py` | No lifecycle management |
| Benchmark Runner | `BenchmarkRunner` in `runner.py` | No reproducibility verification |
| Evaluation Engine | `EvaluationEngine` in `evaluation.py` | No confidence intervals, no hypothesis testing |
| Ground Truth | `GroundTruthDataset` in `ground_truth.py` | No dual-reviewer process implemented |
| Annotation Workflow | `annotation_workflow.md` | No automated adjudication |
| Metadata | `candidate_manifest.json` | Schema not formalized |

### 29.4 Benchmark IDs Convention

| Category | ID Pattern | Example |
|----------|-----------|---------|
| Synthetic (D-01) | SYN-D01-{NNN} | SYN-D01-001 |
| Synthetic (D-02) | SYN-D02-{NNN} | SYN-D02-001 |
| Synthetic (D-03) | SYN-D03-{NNN} | SYN-D03-001 |
| Real OSS | ROSS-{NNN} | ROSS-001 |
| Edge-Case | EC-{NNN} | EC-001 |
| Adversarial | ADV-{NNN} | ADV-001 |
| Stress | STR-{NNN} | STR-001 |
| Temporal | TMP-{NNN}-{TNN} | TMP-001-T0 |
| Longitudinal | LNG-{NNN}-{TNN} | LNG-001-T0 |
| Industrial | IND-{NNN} | IND-001 |

---

*End of Benchmark Evolution Specification v1.0*
