# MIIE v1.0 Freeze Register

**Status:** FROZEN  
**Date:** 2026-06-08  
**Version:** 1.0.0  
**Classification:** Governance Sprint Artifact  

---

## Module Registry

| Module ID | Module Name | Owner | Authority Document |
|-----------|-------------|-------|-------------------|
| M-01 | Repository Ingestion Engine | Engineer B | TRD §7, AFD §5.2 |
| M-02 | Metric Extraction Engine | Engineer B | TRD §8, AFD §5.2 |
| M-03 | Dataset Generator (M-03) | Engineer B | TRD §9, AFD §5.2 |
| M-04 | Ground Truth Manager | Engineer B | TRD §11, AFD §5.2 |
| M-05 | Detector Engine | Engineer B | TRD §10, AFD §5.2 |
| M-06 | Benchmark Runner | Engineer C | TRD §16, AFD §5.2 |
| M-07 | Evaluation Engine | Engineer C | TRD §16, AFD §5.2 |
| M-08 | Scoring Engine | Engineer C | TRD §15, AFD §5.2 |
| M-09 | Report Generator | Engineer A | TRD §18, AFD §5.2 |
| M-10 | CLI Interface | Engineer A | TRD §19, AFD §5.2 |
| M-11 | API Server | Engineer A | TRD §21, AFD §5.2 |
| M-12 | Config Loader | Engineer A | TRD §22, AFD §5.2 |
| M-13 | Registry Manager | Engineer A | TRD §23, AFD §5.2 |
| M-14 | Job Manager | Engineer A | TRD §24, AFD §5.2 |
| M-15 | Pipeline Controller | Engineer A | TRD §25, AFD §5.2 |
| M-16 | State Manager | Engineer A | TRD §26, AFD §5.2 |
| M-17 | Workflow Engine | Engineer A | TRD §27, AFD §5.2 |

---

## Detector Registry

| Detector ID | Detector Name | Authority Document |
|-------------|---------------|-------------------|
| D-01 | Distributional Drift Detector | TFS §5.1, AFD §5.2 |
| D-02 | Correlation Breakdown Detector | TFS §5.2, AFD §5.2 |
| D-03 | Threshold Compression Detector | TFS §5.3, AFD §5.2 |

---

## Metric Registry

| Metric ID | Metric Name | Authority Document |
|-----------|-------------|-------------------|
| M-01 | Code Coverage | TFS §2.1, PRD §2.1 |
| M-02 | Commit Frequency | TFS §2.1, PRD §2.1 |
| M-03 | Review Participation | TFS §2.1, PRD §2.1 |
| M-04 | Review Latency | TFS §2.1, PRD §2.1 |
| M-05 | Issue Resolution Time | TFS §2.1, PRD §2.1 |
| M-06 | Code Churn | TFS §2.1, PRD §2.1 |
| M-07 | Cyclomatic Complexity | TFS §2.1, PRD §2.1 |

---

## Workflow Registry

| Workflow ID | Workflow Name | Authority Document |
|-------------|---------------|-------------------|
| WF-01 | Analyze Repository | AFD §4.2 |
| WF-02 | Investigate Integrity Failure | AFD §4.3 |
| WF-03 | Run Benchmark Evaluation | AFD §4.4 |
| WF-04 | Export Results | AFD §4.5 |
| WF-05 | Compare Time Windows | AFD §4.6 |

---

## Schema Registry

| Schema ID | Schema Name | Authority Document |
|-----------|-------------|-------------------|
| RepositoryContext | Repository Context Schema | BSD §5 |
| MetricDataFrame | Metric Data Frame Schema | BSD §6 |
| WindowDefinition | Window Definition Schema | BSD §7 |
| DetectorResults | Detector Results Schema | BSD §8 |
| ScorePackage | Score Package Schema | BSD §9 |
| EvidencePackage | Evidence Package Schema | BSD §10 |
| ExplanationReport | Explanation Report Schema | BSD §11 |
| AnalysisResult | Analysis Result Schema | BSD §12 |

---

## Version Freeze

| Field | Value |
|-------|-------|
| Frozen Version | 1.0.0 |
| Freeze Date | 2026-06-08 |
| Authority Documents | TRD, ACS, BSD-Engineering, TFS, AFD, IMP, PRD, MES |

### Frozen Capabilities

1. Repository Analysis (ingest, extract, segment, detect, score, explain, export)
2. Benchmark Execution (3 suites: B-01, B-02, B-03)
3. CLI Interface (8 commands)
4. REST API (6 endpoints)
5. Configuration Management (YAML/JSON)
6. Registry Management (metrics, detectors, workflows)
7. State Management (job state machine)
8. Report Generation (JSON, Markdown, CSV)

### Out-of-Scope Capabilities

1. GUI/web interface
2. Database persistence
3. Real-time streaming
4. SaaS/multi-tenancy
5. Authentication beyond minimal API key
6. Productivity tracking or developer ranking
7. AI-generated explanations
8. Additional metrics beyond M-01..M-07
9. Additional detectors beyond D-01..D-03
10. Continuous monitoring (point-in-time only)
11. Cross-repository comparison
12. Recommendation engine
13. Knowledge graph
14. Predictive capabilities

---

*This freeze register is authoritative. No implementation may add capabilities outside this frozen scope without a version bump to v1.1.0 and update to this document.*