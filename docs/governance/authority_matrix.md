# MIIE v1.0 Authority Matrix

**Status:** FROZEN  
**Date:** 2026-06-08  
**Version:** 1.0.0  
**Classification:** Governance Sprint Artifact  

---

## Decision Type Authority

| Decision Type | Authority Document | Reason |
|---------------|-------------------|--------|
| Architecture Overview | TRD §2 | Defines layer structure, module boundaries, and data flow |
| Technology Stack | TRD §1.8 | Specifies Python 3.10, Poetry, dependencies, and tooling |
| Core Modules | TRD §5 | Defines module inventory (M-01 through M-17) |
| Repository Validation | TRD §7 | Specifies validation rules for Git repositories |
| Metric Extraction Logic | TRD §8 | Defines extraction methods for M-01 through M-07 |
| Window Segmentation | TRD §9 | Specifies window generation strategies and constraints |
| Ground Truth Management | TRD §11 | Defines annotation workflow and label lifecycle |
| Detector Algorithms | TFS §5 | Specifies D-01, D-02, D-03 algorithms and thresholds |
| Integrity Score Formula | TFS §6 | Frozen formula for composite integrity assessment |
| Confidence Score Formula | TFS §7 | Frozen formula for score reliability assessment |
| Benchmark Structure | TFS §8 | Defines suite structure, datasets, and evaluation metrics |
| Data Formats | BSD-Engineering §4 | Specifies JSON schemas, naming conventions, timestamps |
| RepositoryContext Schema | BSD-Engineering §5 | Defines repository metadata structure |
| MetricDataFrame Schema | BSD-Engineering §6 | Defines metric data structure |
| WindowDefinition Schema | BSD-Engineering §7 | Defines window metadata structure |
| DetectorResults Schema | BSD-Engineering §8 | Defines detector output structure |
| ScorePackage Schema | BSD-Engineering §9 | Defines score output structure |
| EvidencePackage Schema | BSD-Engineering §10 | Defines evidence structure |
| ExplanationReport Schema | BSD-Engineering §11 | Defines explanation structure |
| AnalysisResult Schema | BSD-Engineering §12 | Defines final output structure |
| Dataset Schema | BSD-Engineering §13 | Defines synthetic dataset structure |
| Ground Truth Schema | BSD-Engineering §14 | Defines label structure |
| Workflow Dispatch | AFD §4 | Defines user journeys and workflow sequences |
| Pipeline Execution Flow | AFD §5.2 | Specifies module invocation order for WF-01 |
| Benchmark Execution Flow | AFD §5.3 | Specifies module invocation order for WF-03 |
| State Transitions | AFD §8 | Defines state machine for jobs and analysis stages |
| Error Handling | AFD §9 | Specifies error taxonomy and propagation rules |
| CLI Commands | PRD §11 | Defines miie commands: analyze, benchmark, explain, export |
| API Endpoints | PRD §12 | Defines REST API endpoints and request/response schemas |
| Config Loading | PRD §15 | Specifies configuration management and precedence |
| Registry Management | PRD §16 | Defines metric and detector registries |
| Job Management | PRD §17 | Specifies job state machine and lifecycle |
| Performance Targets | PRD §8 | Defines performance acceptance criteria |
| Reproducibility Requirements | TFS §3 | Specifies deterministic execution requirements |

---

## Interface Contracts (ACS §3)

| Interface ID | Module | Authority Document | Reason |
|--------------|--------|-------------------|--------|
| INT-01 | Repository Ingestion | ACS §5 | Input/output contracts for repository analysis |
| INT-02 | Metric Extraction | ACS §6 | Input/output contracts for metric extraction |
| INT-03 | Window Generation | ACS §7 | Input/output contracts for window segmentation |
| INT-04 | Detector Invocation | ACS §8 | Input/output contracts for D-01, D-02, D-03 |
| INT-05 | Score Calculation | ACS §9 | Input/output contracts for integrity/confidence scores |
| INT-06 | Evidence Aggregation | ACS §10 | Input/output contracts for evidence packages |
| INT-07 | Explanation Generation | ACS §11 | Input/output contracts for explanation reports |
| INT-08 | Report Generation | ACS §12 | Input/output contracts for final outputs |
| INT-09 | CLI Interface | ACS §13 | Input/output contracts for command-line interface |
| INT-10 | API Server | ACS §14 | Input/output contracts for REST endpoints |
| INT-11 | Config Loader | ACS §15 | Input/output contracts for configuration loading |
| INT-12 | Registry Manager | ACS §16 | Input/output contracts for registry lookups |
| INT-13 | Job Manager | ACS §17 | Input/output contracts for job lifecycle |
| INT-14 | Pipeline Controller | ACS §18 | Input/output contracts for pipeline orchestration |
| INT-15 | State Manager | ACS §19 | Input/output contracts for state persistence |
| INT-16 | Workflow Engine | ACS §20 | Input/output contracts for workflow dispatch |
| INT-17 | Benchmark Runner | ACS §21 | Input/output contracts for benchmark execution |
| INT-18 | Evaluation Engine | ACS §22 | Input/output contracts for evaluation results |

---

## Module Ownership (IMP §3)

| Module ID | Primary Owner | Secondary Owner | Authority Document |
|-----------|--------------|-----------------|-------------------|
| M-01 | Engineer B | Engineer A | IMP §3.2 |
| M-02 | Engineer B | Engineer A | IMP §3.2 |
| M-03 | Engineer B | Engineer C | IMP §3.2 |
| M-04 | Engineer B | Engineer C | IMP §3.2 |
| M-05 | Engineer B | Engineer A | IMP §3.2 |
| M-06 | Engineer C | Engineer B | IMP §3.3 |
| M-07 | Engineer C | Engineer B | IMP §3.3 |
| M-08 | Engineer C | Engineer B | IMP §3.3 |
| M-09 | Engineer A | Engineer B | IMP §3.1 |
| M-10 | Engineer A | Engineer C | IMP §3.1 |
| M-11 | Engineer A | Engineer C | IMP §3.1 |
| M-12 | Engineer A | Engineer B | IMP §3.1 |
| M-13 | Engineer A | Engineer B | IMP §3.1 |
| M-14 | Engineer A | Engineer C | IMP §3.1 |
| M-15 | Engineer A | Engineer B | IMP §3.1 |
| M-16 | Engineer A | Engineer B | IMP §3.1 |
| M-17 | Engineer A | Engineer B | IMP §3.1 |

---

## Test Authority

| Test Type | Authority Document | Reason |
|-----------|-------------------|--------|
| Contract Tests (CT-01..CT-17) | IMP §6.7 | Validates ACS interface contracts |
| Schema Tests (ST-01..ST-10) | IMP §6.7 | Validates BSD schema compliance |
| Workflow Tests (WT-01..WT-07) | IMP §6.7 | Validates AFD workflow behavior |
| Benchmark Tests (BT-01..BT-05) | IMP §6.7 | Validates TFS benchmark requirements |
| Unit Tests | IMP §6.7 | Validates individual module functionality |
| Integration Tests | IMP §6.7 | Validates module-pair integration |
| Reproducibility Tests | IMP §2.2 | Validates bitwise-identical outputs |

---

## Performance Targets (IMP §1.6)

| Metric | Target | Authority Document |
|--------|--------|-------------------|
| D-01 Precision | ≥0.80 | IMP §1.6 |
| D-01 Recall | ≥0.75 | IMP §1.6 |
| D-02 Precision | ≥0.75 | IMP §1.6 |
| D-02 Recall | ≥0.70 | IMP §1.6 |
| D-03 Precision | ≥0.85 | IMP §1.6 |
| D-03 Recall | ≥0.80 | IMP §1.6 |
| Test Coverage | ≥90% | IMP §1.6 |
| CLI First Analysis | <15 minutes | IMP §1.6 |
| Benchmark Execution | <10 minutes | IMP §7 |

---

## Version Scope

| Capability | Version | Authority Document |
|------------|---------|-------------------|
| Repository Ingestion | v1.0 | PRD §1.3, TFS §1.3 |
| Metric Extraction (7 metrics) | v1.0 | PRD §1.3, TFS §2.1 |
| Window Segmentation | v1.0 | PRD §1.3, TFS §3 |
| Distributional Drift Detection | v1.0 | PRD §1.3, TFS §4.1 |
| Correlation Breakdown Detection | v1.0 | PRD §1.3, TFS §4.2 |
| Threshold Compression Detection | v1.0 | PRD §1.3, TFS §4.3 |
| Integrity Score | v1.0 | PRD §1.3, TFS §6 |
| Confidence Score | v1.0 | PRD §1.3, TFS §7 |
| Evidence Package | v1.0 | PRD §1.3, TFS §8 |
| Explanation Generation | v1.0 | PRD §1.3, TFS §9 |
| CLI (8 commands) | v1.0 | PRD §11, AFD §4 |
| REST API (6 endpoints) | v1.0 | PRD §12, AFD §4 |
| Benchmark Runner | v1.0 | PRD §13, AFD §4 |
| Evaluation Engine | v1.0 | PRD §13, TFS §8 |

---

## Out-of-Scope Capabilities

| Capability | Version | Authority Document |
|------------|---------|-------------------|
| GUI/web interface | v2.0 | TFS §1.5, PRD §1.4 |
| Database persistence | v2.0 | TRD §1.8 |
| Real-time streaming | v2.0 | TFS §1.5, PRD §1.4 |
| SaaS/multi-tenancy | v2.0 | TFS §1.5, PRD §1.4 |
| Authentication beyond API key | v2.0 | TFS §1.5, PRD §1.4 |
| Productivity tracking | v2.0 | PRD §1.4, MES §1.2 |
| AI explanations | v2.0 | PRD §1.4, MES §1.2 |
| Additional metrics (M-08+) | v2.0 | TFS §3, PRD §1.4 |
| Additional detectors (D-04+) | v2.0 | TFS §4, PRD §1.4 |
| Cross-repository analysis | v2.0 | PRD §1.4 |
| Recommendation engine | v2.0 | PRD §1.4 |

---

*This authority matrix is authoritative. When conflicts arise between documents, the higher authority in this matrix overrides lower authority.*