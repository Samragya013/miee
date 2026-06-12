# TRD Architecture Mapping

## Layers and Modules from TRD Section 2.1

| Layer | Module | Purpose | Inputs | Outputs | Dependencies | Authority Source |
|-------|--------|---------|--------|---------|--------------|------------------|
| Interface Layer | M-10: CLI Interface | Parse user input, dispatch to pipeline or benchmark subsystem, handle errors, report progress | User commands, configuration | Orchestration layer calls | Orchestration Layer | TRD §2.1, §19 |
| Interface Layer | M-11: API Server | Handle REST API requests, route to internal analysis service | HTTP requests | Orchestration layer calls | Orchestration Layer | TRD §2.1, §18 |
| Interface Layer | M-12: Config Loader | Load and validate configuration from YAML/JSON files | Configuration files | Validated configuration | Orchestration Layer | TRD §2.1, §18 |
| Interface Layer | M-13: Registry Manager | Manage metric and detector definitions | None | Metric/detector definitions | Orchestration Layer | TRD §2.1, §18 |
| Orchestration Layer | M-14: Job Manager | Manage job state for API mode (if used) | Orchestration requests | Job status updates | Processing Layer | TRD §2.1, §6.3 |
| Orchestration Layer | M-15: Pipeline Controller | Orchestrate the analysis pipeline stages | Validated configuration, repository context | Processing layer results | Processing Layer | TRD §2.1, §6.1 |
| Orchestration Layer | M-16: State Manager | Manage filesystem-based job state | Processing results | Persistent job state | Storage Layer | TRD §2.1, §6.3 |
| Orchestration Layer | M-17: Workflow Engine | Execute predefined workflows (WF-01..WF-05) | Orchestration requests | Workflow execution results | Processing Layer | TRD §2.1, AFD |
| Processing Layer | M-01: Repository Ingestion Engine | Validate and ingest Git repositories, extract repository metadata | Repository path/URL | RepositoryContext | Storage Layer | TRD §2.1, §7 |
| Processing Layer | M-02: Metric Extraction Engine | Extract metrics from repository context | RepositoryContext | MetricDataFrame | Storage Layer | TRD §2.1, §8 |
| Processing Layer | M-03: Dataset Generator (Window Segmentation) | Segment history into windows, generate synthetic datasets | MetricDataFrame | Window Definitions | Storage Layer | TRD §2.1, §9 |
| Processing Layer | M-05: Detector Engine | Execute statistical tests for drift, correlation breakdown, threshold compression | MetricDataFrame, Window Definitions | DetectorResult | Storage Layer | TRD §2.1, §10, §12 |
| Processing Layer | M-08: Scoring Engine | Compute Integrity Scores and Confidence Scores | DetectorResults, MetricDataFrame, Windows | ScorePackage | Storage Layer | TRD §2.1, §15 |
| Processing Layer | M-09: Evidence Aggregator | Aggregate detector results into evidence packages | DetectorResults, MetricDataFrame | EvidencePackage | Storage Layer | TRD §2.1, §11 |
| Processing Layer | M-09: Report Generator | Render analysis results into JSON, Markdown, CSV formats | ScorePackage, EvidencePackage | Analysis reports | Storage Layer | TRD §2.1, §16, §20 |
| Processing Layer | M-09: Explanation Generator | Generate rule-based explanations for findings | EvidencePackage | ExplanationReport | Storage Layer | TRD §2.1, §11 |
| Benchmark Subsystem | M-03: Dataset Generator (Benchmark variant) | Create synthetic repository metric histories for benchmark construction | None | Synthetic benchmark datasets | Storage Layer | TRD §2.1, §9 |
| Benchmark Subsystem | M-04: Ground Truth Manager | Manage ground truth data and annotation workflow | Synthetic datasets | Ground truth labels | Storage Layer | TRD §2.1, §11 |
| Benchmark Subsystem | M-06: Benchmark Runner | Execute benchmark suites, collect predictions | Ground truth, synthetic datasets | BenchmarkRun | Storage Layer | TRD §2.1, §13 |
| Benchmark Subsystem | M-07: Evaluation Engine | Evaluate benchmark runs against ground truth | BenchmarkRun, Ground truth | EvaluationResult | Storage Layer | TRD §2.1, §14 |
| Storage Layer | Output Directory | User-specified output for analysis results | Analysis results | JSON/Markdown/CSV files | None | TRD §2.1, §16 |
| Storage Layer | Cache Directory (~/.miie/cache/) | Clone repositories, cache intermediate data | Repository data | Cached repositories | None | TRD §2.1, §16 |
| Storage Layer | Benchmark Directory (~/.miie/benchmarks/) | Store benchmark datasets, ground truth | Benchmark data | Dataset files | None | TRD §2.1, §16 |
| Storage Layer | Config Directory (~/.miie/) | User configuration files | User preferences | Configuration files | None | TRD §2.1, §16 |