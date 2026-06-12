# Day 7 Authority Matrix

## 1. TFS (Technical Freeze Sheet)
Controls: Frozen metrics M-01..M-07 definitions, missing data policy, metric registration rules
For Day 7 Metric Extraction Foundation:
- Defines which metrics are frozen (M-01 through M-07) and thus must be registered in the metric registry.
- Specifies the missing data policy that dictates how unimplemented metrics (M-01, M-03, M-04, M-05, M-07) should be encoded (as unavailable/null with warning metadata, not as zero or fake values).
- Provides the metric registration rules that the metric registry implementation must follow (e.g., metric ID enum, names, ranges).
- Sets the definitions for M-02 (Commit Frequency) and M-06 (Code Churn) that the extraction implementations must adhere to.
- Lists frozen detectors (D-01..D-03) which are relevant for the integration step where extracted metrics are fed to the detector mock.

## 2. ACS (API Contract Specification)
Controls: Internal interfaces (INT-02 for Metric Extraction), validation rules, error handling contracts, data exchange standards
For Day 7 Metric Extraction Foundation:
- Governs the internal interface INT-02 for Metric Extraction, defining the contract between the Metric Extractor and other pipeline components (e.g., Repository Loader, Detector Engine).
- Specifies validation rules for metric IDs, input data, and output formats that the metric extraction functions must enforce (e.g., rejecting unsupported metrics).
- Defines error handling contracts that dictate how errors (e.g., invalid repository, missing data) should be propagated and represented in the system (using ACS error DTOs).
- Establishes data exchange standards for the MetricDataFrame schema (as refined by BSD) and the serialization format used when passing metrics between pipeline stages.
- Requires that contract tests exist for the metric extraction layer to validate DTOs, validators, and error responses.

## 3. BSD (BSD-Engineering)
Controls: MetricDataFrame schema structure, validation rules, serialization requirements
For Day 7 Metric Extraction Foundation:
- Defines the exact structure of the MetricDataFrame schema that must be used to represent extracted metrics (including fields for metric ID, value, window ID, timestamp, and metadata).
- Specifies validation rules that the MetricDataFrame must satisfy (e.g., required fields, prohibited extra fields, data types) which extraction implementations must comply with.
- Sets serialization requirements (e.g., deterministic JSON with sorted keys, stable separators) that must be used when persisting or transmitting MetricDataFrame instances.
- Provides the schema for related artifacts like RepositoryContext and EvidencePackage that interact with the metric extraction foundation.
- Mandates that JSON schema files for MetricDataFrame pass draft-07 validation and that unknown fields are rejected.

## 4. TRD (Technical Requirements Document)
Controls: Module responsibilities (M-02 Metric Extraction, M-06 Benchmark Runner), Section 8 metric extraction guidelines, storage architecture
For Day 7 Metric Extraction Foundation:
- Assigns responsibility for Metric Extraction to module M-02 (and M-06 for Benchmark Runner, though Benchmark Runner is not the focus of Day 7).
- Provides Section 8 metric extraction guidelines that dictate how metric extraction should be implemented (e.g., using Git history for Commit Frequency and Code Churn, avoiding fabrication of metrics).
- Defines the storage architecture that influences where extracted metrics are temporarily stored (e.g., cache paths) and how they flow through the pipeline.
- Specifies that the Metric Extraction module (M-02) must not import CLI/API modules, maintaining architectural boundaries.
- Requires that the metric extraction foundation adheres to the TRD-defined module structure and dependency boundaries.

## 5. AFD (Application Flow Definition)
Controls: Workflow WF-02 (Metric Extraction), invocation order, state/error flows
For Day 7 Metric Extraction Foundation:
- Defines Workflow WF-02 (Metric Extraction) which outlines the specific steps for metric extraction in the Day 0-10 pipeline.
- Specifies the invocation order of metric extraction relative to other workflow stages (e.g., after Repository Ingestion, before Detector Engine).
- Governs state and error flows for the metric extraction process, including how to handle missing data or extraction failures.
- Requires that the metric extraction foundation be integrated into the workflow dispatcher such that WF-02 is correctly triggered.
- Mandates that any errors during metric extraction follow the state/error flows defined in AFD (e.g., propagating as ACS errors to the pipeline controller).

## 6. Operating Plan (MIIE_Day_0_to_Day_10_Execution_Operating_Plan.md)
Controls: Specific Day 7 tasks, deliverables, validation methods, hour estimates, ownership assignments
For Day 7 Metric Extraction Foundation:
- Lists the specific tasks for Day 7: implement metric registry, extract Commit Frequency (M-02), extract Code Churn (M-06), encode unavailable metrics, integrate extraction.
- Defines the deliverables: a MetricDataFrame containing M-02 and M-06 real fixture-backed values, unavailable markers for non-implemented metrics, and tests proving no extra metrics exist.
- Specifies validation methods: unit tests for each extraction function, integration tests, contract tests, and validation against failure modes (e.g., no fake values, deterministic output).
- Provides hour estimates for each task (e.g., 2 hours for metric registry, 3 hours for each extraction, 2 hours for missing metric policy, 2 hours for integration).
- Assigns ownership: Engineer A for metric registry, Engineer B for Commit Frequency and Code Churn extraction, Engineer C for unavailable metrics encoding and integration.