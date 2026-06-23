# Day 4 Requirement Matrix

Based on MIIE_Day_0_to_Day_10_Execution_Operating_Plan.md (lines 381-407) and governance documents

## Day 4 Requirement Matrix

| Requirement | Required | Implemented | Evidence | Status |
| ----------- | -------- | ----------- | -------- | ------ |
| **Contract Package** | | | | |
| Create contracts package (`src/miie/contracts/`) | Yes | Yes | Directory exists with `__init__.py`, `dataclasses.py`, `errors.py`, `interfaces.py`, `validators.py` | Complete |
| Contracts do not import engines (processing/orchestration layers) | Yes | Partial | Need to verify imports | To verify |
| **DTOs (Data Transfer Objects)** | | | | |
| IngestionInputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| ExtractionInputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| SegmentationInputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| DetectionInputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| D01InputDTO/D01OutputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| D02InputDTO/D02OutputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| D03InputDTO/D03OutputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| ScoringInputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| EvidenceInputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| ExplanationInputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| BenchmarkInputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| EvaluationInputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| ReportInputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| CLIErrorInfo | Yes | Yes | In `dataclasses.py` | Complete |
| IngestionOutputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| AnalyzeOutputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| DetectOutputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| BenchmarkOutputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| EvaluateOutputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| ExplainOutputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| ExportOutputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| GenerateOutputDTO | Yes | Yes | In `dataclasses.py` | Complete |
| DTOs use Day 3 schemas where applicable | Yes | Partial | Need to verify usage of RepositoryContext, MetricDataFrame, etc. | To verify |
| Missing required fields fail validation | Yes | Partial | Need to verify in tests | To verify |
| **Protocols (Interfaces)** | | | | |
| IIngestionEngine (RepositoryLoader) | Yes | Yes | In `interfaces.py` | Complete |
| IExtractionEngine (MetricExtractor) | Yes | Yes | In `interfaces.py` | Complete |
| ISegmentationEngine | Yes | Yes | In `interfaces.py` | Complete |
| IDetectorEngine (DetectorEngine) | Yes | Yes | In `interfaces.py` | Complete |
| IScoringEngine | Yes | Yes | In `interfaces.py` | Complete |
| IEvidenceEngine (EvidenceEngine) | Yes | Yes | In `interfaces.py` | Complete |
| IExplanationEngine | Yes | Yes | In `interfaces.py` | Complete |
| IBenchmarkEngine | Yes | Yes | In `interfaces.py` | Complete |
| IEvaluationEngine | Yes | Yes | In `interfaces.py` | Complete |
| IReportGenerator (ReportEngine) | Yes | Yes | In `interfaces.py` | Complete |
| IDataExporter | Yes | Yes | In `interfaces.py` | Complete |
| IDatasetGenerator | Yes | Yes | In `interfaces.py` | Complete |
| Protocols use typing.Protocol and @runtime_checkable | Yes | Partial | Need to verify implementation | To verify |
| Proper method signatures matching ACS specifications | Yes | Partial | Need to verify signatures | To verify |
| No implementation logic in Protocols | Yes | Partial | Need to verify | To verify |
| Pipeline can depend on Protocols (decoupling) | Yes | Partial | Need to verify | To verify |
| **Validators** | | | | |
| validate_repository_inputs | Yes | Yes | In `validators.py` | Complete |
| validate_extraction_inputs | Yes | Yes | In `validators.py` | Complete |
| validate_segmentation_inputs | Yes | Yes | In `validators.py` | Complete |
| validate_detection_inputs | Yes | Yes | In `validators.py` | Complete |
| validate_d01_input | Yes | Yes | In `validators.py` | Complete |
| validate_d02_input | Yes | Yes | In `validators.py` | Complete |
| validate_d03_input | Yes | Yes | In `validators.py` | Complete |
| validate_scoring_inputs | Yes | Yes | In `validators.py` | Complete |
| validate_evidence_inputs | Yes | Yes | In `validators.py` | Complete |
| validate_explanation_inputs | Yes | Yes | In `validators.py` | Complete |
| validate_benchmark_inputs | Yes | Yes | In `validators.py` | Complete |
| validate_evaluation_inputs | Yes | Yes | In `validators.py` | Complete |
| validate_report_inputs | Yes | Yes | In `validators.py` | Complete |
| validate_cli_ingest_inputs | Yes | Yes | In `validators.py` | Complete |
| validate_cli_analyze_inputs | Yes | Yes | In `validators.py` | Complete |
| Metric ID validation (M-01 through M-07) | Yes | Partial | Need to verify in validators | To verify |
| Detector ID validation (D-01 through D-03) | Yes | Partial | Need to verify in validators | To verify |
| Path validation | Yes | Partial | Need to verify in validators | To verify |
| Output format validation | Yes | Partial | Need to verify in validators | To verify |
| Seed validation | Yes | Partial | Need to verify in validators | To verify |
| Dry-run flag validation | Yes | Partial | Need to verify in validators | To verify |
| Invalid IDs fail before processing | Yes | Partial | Need to verify in tests | To verify |
| No silent coercion of invalid values | Yes | Partial | Need to verify in tests | To verify |
| **Error Model** | | | | |
| MIIEError base class | Yes | Yes | In `errors.py` | Complete |
| ValidationError | Yes | Yes | In `errors.py` | Complete |
| IngestionError | Yes | Yes | In `errors.py` | Complete |
| ExtractionError | Yes | Yes | In `errors.py` | Complete |
| SegmentationError | Yes | Yes | In `errors.py` | Complete |
| DetectionError | Yes | Yes | In `errors.py` | Complete |
| ScoreError | Yes | Yes | In `errors.py` | Complete |
| EvidenceError | Yes | Yes | In `errors.py` | Complete |
| ExplanationError | Yes | Yes | In `errors.py` | Complete |
| BenchmarkError | Yes | Yes | In `errors.py` | Complete |
| EvaluationError | Yes | Yes | In `errors.py` | Complete |
| SerializationError | Yes | Yes | In `errors.py` | Complete |
| ReportError | Yes | Yes | In `errors.py` | Complete |
| TemplateError | Yes | Yes | In `errors.py` | Complete |
| CLIError base class | Yes | Yes | In `errors.py` | Complete |
| Specific CLI error classes (IngestionCLIError, etc.) | Yes | Yes | In `errors.py` | Complete |
| Error factories (validation_error, ingestion_error, etc.) | Yes | Yes | In `errors.py` | Complete |
| Error category, severity, message, recovery_action fields | Yes | Partial | Need to verify implementation | To verify |
| Invalid contract returns explicit error | Yes | Partial | Need to verify in tests | To verify |
| Error payload schema-valid | Yes | Partial | Need to verify in tests | To verify |
| **Contract Tests** | | | | |
| tests/contract/test_dtos.py | Yes | Yes | File exists | Complete |
| tests/contract/test_validators.py | Yes | Yes | File exists | Complete |
| tests/contract/test_errors.py | Yes | Yes | File exists | Complete |
| Positive test cases (valid inputs) | Yes | Partial | Need to verify test content | To verify |
| Negative test cases (invalid inputs) | Yes | Partial | Need to verify test content | To verify |
| Contract tests pass | Yes | Partial | Need to run tests | To verify |
| **Architecture & Compliance** | | | | |
| Contracts layer depends ONLY on schemas layer | Yes | Partial | Need to verify imports | To verify |
| No detector logic in contracts | Yes | Partial | Need to verify | To verify |
| No scoring logic in contracts | Yes | Partial | Need to verify | To verify |
| No benchmark logic in contracts | Yes | Partial | Need to verify | To verify |
| No report logic in contracts | Yes | Partial | Need to verify | To verify |
| No ingestion logic in contracts | Yes | Partial | Need to verify | To verify |
| No workflow logic in contracts | Yes | Partial | Need to verify | To verify |
| No evidence generation logic in contracts | Yes | Partial | Need to verify | To verify |
| No REST API logic in contracts | Yes | Partial | Need to verify | To verify |
| No database logic in contracts | Yes | Partial | Need to verify | To verify |
| No V2 capabilities in contracts | Yes | Partial | Need to verify | To verify |
| **Day 0-4 Regression** | | | | |
| Day 1 tests still pass | Yes | Partial | Need to run tests | To verify |
| Day 2 tests still pass | Yes | Partial | Need to run tests | To verify |
| Day 3 tests still pass | Yes | Partial | Need to run tests | To verify |
| Day 4 tests pass | Yes | Partial | Need to run tests | To verify |