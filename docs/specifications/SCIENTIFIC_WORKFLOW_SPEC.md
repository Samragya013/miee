# ECP-02 Phase 2: Scientific Workflow Specification

**Generated**: 2026-07-10
**Status**: Design Complete
**Based on**: Phase 1 Workflow Audit Report

---

## 1. Design Principles

1. **Scientific Core Frozen** — No changes to metrics, detectors, scoring, evidence, confidence, observation model, benchmarks, ground truth, or statistical algorithms
2. **Application Architecture Frozen** — WorkflowEngine, SessionManager, ApplicationService contracts preserved
3. **User-Centric** — Users think "Analyze a repository" not "Run detector D-01"
4. **Deterministic** — Same inputs → same workflow execution → same results
5. **Composable** — Workflows built from canonical pipeline stages
6. **Resumable** — Every workflow supports pause/resume/cancel
7. **Observable** — Progress, state, timing visible at every step

---

## 2. Canonical Pipeline Stages (Frozen)

| Stage ID | Name | Engine | Deterministic | Resumable |
|----------|------|--------|---------------|-----------|
| `S01` | **Acquisition** | `RepositoryIngestionEngine` | ✅ | ✅ |
| `S02` | **Validation** | Inline validation | ✅ | ✅ |
| `S03` | **Extraction** | `MetricExtractionEngine` | ✅ | ✅ |
| `S04` | **Segmentation** | `WindowSegmentationEngine` | ✅ | ✅ |
| `S05` | **Detection** | `DetectorDispatcherEngine` | ✅ | ✅ |
| `S06` | **Scoring** | `ScoringEngine` | ✅ | ✅ |
| `S07` | **Evidence** | `EvidenceEngine` | ✅ | ✅ |
| `S08` | **Explanation** | `ExplanationEngine` | ✅ | ✅ |
| `S09` | **Reporting** | `ReportGenerator` | ✅ | ✅ |

---

## 3. Required Canonical Workflows

### WF-01: Repository Analysis (Primary)
**User Goal**: "Analyze a repository"
**Pipeline**: S01 → S02 → S03 → S04 → S05 → S06 → S07 → S09
**Entry**: `miie analyze` or `miie` (interactive) → "Analyze Repository"
**Outputs**: Integrity score, confidence, detector findings, evidence package, reports (JSON/MD/CSV)
**Exit Codes**: 0 (IS≥1.0), 1 (IS<1.0), 2 (system error), 3 (invalid input)

### WF-02: Repository Validation
**User Goal**: "Validate a repository before analysis"
**Pipeline**: S01 → S02
**Entry**: `miie validate` or interactive → "Validate Repository"
**Outputs**: Validation pass/fail, repository metadata, readiness assessment
**Exit Codes**: 0 (valid), 3 (invalid)

### WF-03: Benchmark Execution
**User Goal**: "Run benchmark suite"
**Pipeline**: BenchmarkEngine (independent pipeline)
**Entry**: `miie benchmark` or interactive → "Run Benchmark"
**Outputs**: BenchmarkRun (predictions, metadata)
**Exit Codes**: 0 (success), 4 (benchmark error)

### WF-04: Scientific Validation
**User Goal**: "Validate against ground truth"
**Pipeline**: EvaluationEngine (independent pipeline)
**Entry**: `miie evaluate` or interactive → "Scientific Validation"
**Inputs**: BenchmarkRun JSON + Ground Truth JSON
**Outputs**: EvaluationResult (accuracy, F1, precision, recall)
**Exit Codes**: 0 (success), 2 (system error)

### WF-05: Result Inspection
**User Goal**: "Inspect previous analysis results"
**Pipeline**: None (read-only)
**Entry**: `miie inspect` or interactive → "Inspect Results"
**Inputs**: Cached session or saved output directory
**Outputs**: Interactive exploration of metrics, detectors, evidence, scores
**Exit Codes**: 0 (success)

### WF-06: Report Generation
**User Goal**: "Generate reports from existing results"
**Pipeline**: S09 only (reads cached results)
**Entry**: `miie export` or interactive → "Generate Reports"
**Inputs**: Cached analysis results or output directory
**Outputs**: Reports in requested formats (JSON, MD, CSV, YAML)
**Exit Codes**: 0 (success), 3 (no results found)

### WF-07: Configuration Review
**User Goal**: "Review and modify configuration"
**Pipeline**: None (interactive config)
**Entry**: `miie setup` or interactive → "Configure MIIE"
**Outputs**: Updated configuration file
**Exit Codes**: 0 (saved), 1 (cancelled)

---

## 4. Workflow Definitions (WorkflowEngine Steps)

### WF-01: Repository Analysis Steps

| Step | Stage | Handler | Optional | Description |
|------|-------|---------|----------|-------------|
| `acquire` | S01 | `ingestion.ingest()` | ❌ | Clone/fetch repository, extract metadata |
| `validate` | S02 | `ingestion.validate()` | ❌ | Verify repository context integrity |
| `extract` | S03 | `extraction.extract()` | ❌ | Extract configured metrics |
| `segment` | S04 | `segmentation.segment()` | ❌ | Segment into analysis windows |
| `detect` | S05 | `dispatcher.invoke()` | ❌ | Run enabled detectors |
| `score` | S06 | `scoring.compute_integrity_score()` | ❌ | Compute integrity & confidence |
| `evidence` | S07 | `evidence.generate()` | ❌ | Generate evidence package |
| `report` | S09 | `reporting.generate()` | ❌ | Write output reports |

### WF-02: Repository Validation Steps

| Step | Stage | Handler | Optional | Description |
|------|-------|---------|----------|-------------|
| `acquire` | S01 | `ingestion.ingest()` | ❌ | Clone/fetch repository |
| `validate` | S02 | `ingestion.validate()` | ❌ | Verify repository context |

### WF-03: Benchmark Execution Steps

| Step | Stage | Handler | Optional | Description |
|------|-------|---------|----------|-------------|
| `setup` | — | `benchmark.load_suite()` | ❌ | Load benchmark suite |
| `execute` | — | `benchmark.execute()` | ❌ | Run detectors on suite |
| `save` | — | `benchmark.save_results()` | ❌ | Persist BenchmarkRun |

### WF-04: Scientific Validation Steps

| Step | Stage | Handler | Optional | Description |
|------|-------|---------|----------|-------------|
| `load_benchmark` | — | `load_benchmark_json()` | ❌ | Load BenchmarkRun |
| `load_truth` | — | `load_ground_truth_json()` | ❌ | Load ground truth |
| `evaluate` | — | `evaluation.evaluate()` | ❌ | Compute metrics |
| `report` | — | `format_evaluation()` | ❌ | Display results |

### WF-05: Result Inspection Steps

| Step | Stage | Handler | Optional | Description |
|------|-------|---------|----------|-------------|
| `load_session` | — | `session.load()` | ❌ | Load session or output dir |
| `show_summary` | — | `format_summary()` | ❌ | Display overview |
| `explore_metrics` | — | `browse_metrics()` | ✅ | Interactive metric browser |
| `explore_detectors` | — | `browse_detectors()` | ✅ | Interactive detector browser |
| `explore_evidence` | — | `browse_evidence()` | ✅ | Interactive evidence browser |
| `explore_scores` | — | `browse_scores()` | ✅ | Interactive score browser |

### WF-06: Report Generation Steps

| Step | Stage | Handler | Optional | Description |
|------|-------|---------|----------|-------------|
| `load_results` | — | `load_analysis_results()` | ❌ | Load cached/exported results |
| `select_formats` | — | `prompt_formats()` | ✅ | Choose output formats |
| `generate_reports` | S09 | `reporting.generate()` | ❌ | Write reports |

### WF-07: Configuration Review Steps

| Step | Stage | Handler | Optional | Description |
|------|-------|---------|----------|-------------|
| `load_config` | — | `config.load()` | ❌ | Load current config |
| `review_sections` | — | `config.review_interactive()` | ✅ | Review each section |
| `save_config` | — | `config.save()` | ❌ | Persist changes |

---

## 5. Workflow State Machine

```
                    ┌─────────────┐
                    │   CREATED   │
                    └──────┬──────┘
                           │ define()
                           ▼
                    ┌─────────────┐
         ┌──────────│   RUNNING   │──────────┐
         │          └──────┬──────┘          │
         │                 │                 │
    pause()           complete()         cancel()
         │                 │                 │
         ▼                 ▼                 ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   PAUSED    │    │  COMPLETED  │    │  CANCELLED  │
└──────┬──────┘    └─────────────┘    └─────────────┘
       │
       │ resume()
       ▼
┌─────────────┐
│   RUNNING   │
└─────────────┘

On step failure (non-optional): RUNNING → FAILED
On exception: RUNNING → FAILED
```

---

## 6. Configuration Schema (Per Workflow)

### WF-01/WF-02 Shared Config
```yaml
repository:
  path: ""              # Required: local path or GitHub URL
  auth_token: ""        # Optional: GitHub PAT
  shallow_depth: null   # Optional: shallow clone depth
  
extraction:
  metrics: ["M-02", "M-06"]
  since: null           # ISO 8601
  until: null           # ISO 8601
  exclude_bots: true
  
segmentation:
  strategy: "time"      # time|commit|release|custom
  size: 7               # days or commits
  
detection:
  detectors: ["D-01", "D-02", "D-03"]
  thresholds: {}        # JSON overrides
  
reporting:
  output_dir: "./output"
  formats: ["json"]     # json|md|csv|yaml
  forensic: false
  
execution:
  seed: 42
  dry_run: false
```

### WF-03 Benchmark Config
```yaml
benchmark:
  suite_id: "B-01"      # Required
  detectors: ["D-01", "D-02", "D-03"]
  config: {"threshold": 0.05}
  seed: 42
```

### WF-04 Evaluation Config
```yaml
evaluation:
  benchmark_json: ""    # Required: path to BenchmarkRun
  ground_truth_json: "" # Required: path to ground truth
```

---

## 7. Interactive Navigation Flow

```
miie (no args)
    │
    ▼
┌─────────────────────────────────────┐
│       MIIE Interactive Workspace    │
│  Scientific Analysis Platform v1.7  │
└─────────────────────────────────────┘
    │
    ├─► 1. Analyze Repository     ──► WF-01
    ├─► 2. Validate Repository    ──► WF-02
    ├─► 3. Run Benchmark          ──► WF-03
    ├─► 4. Scientific Validation  ──► WF-04
    ├─► 5. Inspect Results        ──► WF-05
    ├─► 6. Generate Reports       ──► WF-06
    ├─► 7. Configure MIIE         ──► WF-07
    └─► 8. Exit
```

### Step Progression (WF-01 Example)
```
Step 1/8: Acquisition
  ├─ Repository: ./my-repo (local)
  ├─ Status: Cloning... ████████░░ 80%
  └─ [Continue] [Pause] [Cancel] [Details]

Step 2/8: Validation
  ├─ Commits: 1,247
  ├─ Contributors: 23
  ├─ Status: Validated ✓
  └─ [Continue] [Pause] [Cancel] [Details]

Step 3/8: Extraction
  ├─ Metrics: M-02, M-06
  ├─ Windows: 14 (time, 7-day)
  ├─ Status: Complete ✓ (2.3s)
  └─ [Continue] [Pause] [Cancel] [Details]

... etc ...
```

---

## 8. Session Continuity

| Event | Session Behavior |
|-------|------------------|
| Start WF-01 | Create session, record config, save checkpoint after each step |
| Pause | Save workflow state, persist session |
| Resume | Load session, restore workflow state, continue from current step |
| Cancel | Save partial results, mark workflow CANCELLED, offer resume |
| Complete | Save final results, mark workflow COMPLETED, cache for inspection |
| Exit interactive | Save session, offer restore on next launch |

---

## 9. Progress Visualization Requirements

### Pipeline Progress (WF-01)
```
MIIE Analysis Pipeline          [████████████░░░░░░░░░░] 50%
├─ S01 Acquisition        ✓     1.2s  [Commits: 1247, Contributors: 23]
├─ S02 Validation         ✓     0.1s  [Valid: true]
├─ S03 Extraction         ✓     2.3s  [Metrics: M-02, M-06, Windows: 14]
├─ S04 Segmentation       ✓     0.4s  [Windows: 14, Strategy: time/7d]
├─ S05 Detection          ███   3.1s  [D-01: running, D-02: pending, D-03: pending]
├─ S06 Scoring            ⏳    --    [Waiting for detection]
├─ S07 Evidence           ⏳    --    [Waiting for scoring]
└─ S09 Reporting          ⏳    --    [Waiting for evidence]
```

### Stage Detail View (on [Details])
```
Stage: S05 Detection (3/8)
Status: Running (D-01 complete, D-02 running, D-03 pending)
Elapsed: 3.1s | ETA: ~2.5s

Detector Results:
├─ D-01 Distribution Drift     ✓ CLEAR      (p=0.34, α=0.05)  1.2s
├─ D-02 Correlation Breakdown  ███░░░ RUNNING               2.8s
└─ D-03 Threshold Compression  ⏳ PENDING                      

[Back] [Pause] [Cancel]
```

---

## 10. Result Exploration Interface

### Navigation Tree
```
Analysis Result: my-repo (IS=0.87, CF=0.92)
├─ 📊 Metrics
│  ├─ M-02 Code Churn        [mean=0.23, trend=+0.02]
│  └─ M-06 Defect Ratio      [mean=0.04, trend=-0.01]
├─ 🔍 Detectors
│  ├─ D-01 Distribution Drift  [CLEAR, p=0.34]
│  ├─ D-02 Correlation Breakdown [TRIGGERED, p=0.02]
│  └─ D-03 Threshold Compression [CLEAR, p=0.67]
├─ 📈 Scores
│  ├─ Integrity: 0.87 (Poor)
│  ├─ Confidence: 0.92 (Good)
│  └─ Risk Level: MEDIUM
├─ 📋 Evidence
│  ├─ E-01 Drift Evidence      [window=7, severity=low]
│  └─ E-02 Breakdown Evidence  [window=3, severity=medium]
└─ 📝 Explanations
   ├─ Narrative 1: "Correlation breakdown in window 3..."
   └─ Recommendation: "Investigate review process changes..."
```

---

## 11. Export Workflow Outputs

| Format | WF-01 | WF-06 | Content |
|--------|-------|-------|---------|
| JSON | ✅ | ✅ | Full analysis result (scores, detectors, evidence, metrics) |
| Markdown | ✅ | ✅ | Human-readable report with findings & recommendations |
| CSV | ✅ | ✅ | Metrics & detector outputs tabular |
| YAML | ❌ | ✅ | Configurable structured export |

---

## 12. Backward Compatibility Matrix

| Legacy Command | New Implementation | Exit Codes Preserved | Output Schema Preserved |
|----------------|-------------------|---------------------|------------------------|
| `miie analyze` | WF-01 via ApplicationService | ✅ | ✅ |
| `miie detect` | WF-01 (stages 1-5 only) | ✅ | ✅ |
| `miie ingest` | WF-02 (stages 1-2) | ✅ | ✅ |
| `miie benchmark` | WF-03 | ✅ | ✅ |
| `miie evaluate` | WF-04 | ✅ | ✅ |
| `miie explain` | WF-01 + WF-05 (explanation) | ✅ | ✅ |
| `miie export` | WF-06 | ✅ | ✅ (adds YAML) |
| `miie generate` | Unchanged (separate) | ✅ | ✅ |
| `miie status` | Unchanged | ✅ | ✅ |
| `miie validate` | WF-02 / WF-06 | ✅ | ✅ |
| `miie setup` | WF-07 | ✅ | ✅ |

---

## 13. Implementation Architecture

### New Files to Create
```
src/miie/application/
├── workflows/
│   ├── __init__.py
│   ├── repository_analysis.py    # WF-01
│   ├── repository_validation.py  # WF-02
│   ├── benchmark_execution.py    # WF-03
│   ├── scientific_validation.py  # WF-04
│   ├── result_inspection.py      # WF-05
│   ├── report_generation.py      # WF-06
│   └── configuration_review.py   # WF-07
├── interactive/
│   ├── __init__.py
│   ├── navigator.py              # Menu navigation
│   ├── progress.py               # Progress visualization
│   ├── explorer.py               # Result exploration
│   └── prompts.py                # Confirmation checkpoints
└── cli_integration.py            # Wire CLI → ApplicationService → Workflows
```

### Modified Files
```
src/miie/application/service.py       # Add workflow execution methods
src/miie/cli/__init__.py              # Replace direct processing calls with ApplicationService
src/miie/application/output.py        # Add exploration formatting methods
```

---

## 14. Determinism Guarantees

1. **WorkflowEngine** ensures same step order for same workflow definition
2. **SessionManager** caches results with TTL; cache key includes all config
3. **Random seed** (default 42) propagated to all stochastic engines
4. **Configuration frozen** at workflow start; no mid-flight changes
5. **Progress callbacks** pure observation; no side effects on execution

---

## 15. Acceptance Criteria

| Criterion | Verification |
|-----------|--------------|
| WF-01 executes all 8 stages in order | Integration test |
| WF-01 pause/resume preserves state | Unit test: pause at S04, resume → S05 |
| WF-01 cancel saves partial results | Unit test: cancel at S05 → inspect cached |
| WF-05 loads cached results without re-run | Integration test: run WF-01, exit, run WF-05 |
| All legacy commands produce identical output | Regression test suite |
| Interactive mode launches without args | Manual test: `miie` |
| Progress displays correctly at each stage | Visual regression test |
| Export produces deterministic JSON/MD/CSV | Byte-for-byte comparison |

---

*End of Phase 2 Scientific Workflow Specification*