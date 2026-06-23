# FERA Architecture Audit Report

## Overview
This document presents the findings of the Architecture review phase of the FERA audit for the MIIE (Measurement Integrity Intelligence Engine) system. The audit examines the system architecture, dependency boundaries between layers, architectural decisions and patterns, and identifies any violations or concerns.

## Architectural Layers and Responsibilities

The MIIE system is organized into the following layers, each with distinct responsibilities:

1. **Ingestion Layer** (`src/miie/processing/ingestion.py`)
   - Responsible for validating and ingesting repository metadata.
   - Implements `IIngestionEngine` interface.
   - Produces `RepositoryContext` objects.

2. **Extraction Layer** (`src/miie/processing/extraction.py`)
   - Responsible for extracting metrics (M-02, M-06) from Git repositories.
   - Implements `IExtractionEngine` interface.
   - Produces `MetricDataFrame` objects.

3. **Segmentation Layer** (`src/miie/processing/segmentation.py`)
   - Responsible for segmenting metric data into analysis windows.
   - Implements `ISegmentationEngine` interface.
   - Produces lists of `WindowDefinition` objects.

4. **Detection Layer** (`src/miie/processing/detection/`)
   - Responsible for running detectors (D-01, D-02, D-03) on metric data.
   - Implements `IDetectorEngine` interface via `DetectorDispatcherEngine`.
   - Uses `DetectorRegistry`, `DetectorRunner`, and specific detector implementations.
   - Produces `DetectorResults` objects.

5. **Scoring Layer** (`src/miie/processing/scoring/engine.py`)
   - Responsible for computing integrity and confidence scores.
   - Implements `IScoringEngine` interface.
   - Produces `ScorePackage` objects.

6. **Evidence Layer** (`src/miie/processing/evidence.py`)
   - Responsible for building traceable evidence packages.
   - Implements `IEvidenceEngine` interface.
   - Produces `EvidencePackage` objects.

7. **Explanation Layer** (`src/miie/processing/explanation/engine.py`)
   - Responsible for generating explanation narratives and recommendations.
   - Implements `IExplanationEngine` interface.
   - Produces `ExplanationReport` objects.

8. **Reporting Layer** (`src/miie/processing/reporting/engine.py`)
   - Responsible for generating analysis reports in various formats.
   - Implements `IReportGenerator` interface.
   - Produces `ReportOutput` objects.

9. **Orchestration Layer**
   - **Pipeline** (`src/miie/orchestration/pipeline.py`)
     - Orchestrates the execution of analysis engines.
     - Implements `AnalysisPipeline` class that coordinates all engines.
   - **Workflow Dispatcher** (`src/miie/orchestration/workflow.py`)
     - Dispatches different analysis workflows (basic, with evidence, full analysis, benchmark only, evaluation only).
     - Implements `WorkflowDispatcher` class.

10. **Benchmark Layer** (`src/miie/benchmark/`)
    - Responsible for generating synthetic benchmark datasets and running benchmarks.
    - `BenchmarkDatasetGenerator` (`src/miie/benchmark/generator.py`) implements `IDatasetGenerator`.
    - `BenchmarkRunner` (`src/miie/benchmark/runner.py`) implements `IBenchmarkEngine`.
    - `EvaluationEngine` (`src/miie/benchmark/evaluation.py`) implements `IEvaluationEngine`.

11. **Evaluation Layer** (part of Benchmark layer)
    - Responsible for computing classification metrics and baseline comparisons.
    - Implements `IEvaluationEngine` interface.

12. **Validation Layer** (`src/miie/validation/service.py`)
    - Provides centralized JSON Schema validation service.
    - Implements `ValidationService` class.

13. **CLI Layer** (`src/miie/cli.py`, `src/miie/__main__.py`)
    - Command-line interface entry point.
    - Uses Click framework for command grouping.

14. **Contracts and Schemas** (Cross-cutting)
    - `src/miie/contracts/` - Interface definitions and error types.
    - `src/miie/schemas/` - Data models, serialization, and schema definitions.

## Dependency Direction Analysis

The architecture follows a **strict downward dependency principle**: higher layers depend on lower layers, but lower layers do not depend on higher layers. This ensures separation of concerns and maintainability.

### Verified Dependency Flow

- **Orchestration → Engines**: The `AnalysisPipeline` depends on all engine interfaces (ingestion, extraction, segmentation, detection, scoring, evidence, explanation, reporting, benchmark, evaluation). Engines do not depend on the pipeline.
- **Engines → Contracts/Schemas**: Engines depend on interface contracts (`src/miie/contracts/interfaces.py`) and data models (`src/miie/schemas/models.py`). Contracts and schemas do not depend on engine implementations.
- **Detection Sub‑layers**: 
  - `DetectorDispatcherEngine` depends on `DetectorRegistry` and `BaseDetector`.
  - `DetectorRegistry` depends on `BaseDetector`.
  - `DetectorRunner` depends on `DetectorRegistry` and `BaseDetector`.
  - Specific detectors (e.g., `CorrelationBreakdownDetector`) depend on `BaseDetector`.
  - No upward dependencies within detection.
- **Benchmark Layer**: 
  - `BenchmarkRunner` depends on `processing.benchmark.engine` (the core benchmark engine implementation) – this is a **downward** dependency (benchmark uses the processing benchmark engine).
  - `BenchmarkDatasetGenerator` depends on schemas and contracts only.
  - `EvaluationEngine` depends on schemas only.
- **Validation Layer**: Depend only on contracts, schemas, and external `jsonschema` library.
- **CLI Layer**: Currently only contains command group definitions; actual command logic would be implemented by importing from orchestration or other layers (downward dependency).

No upward dependencies (lower depending on higher) were detected in the reviewed code.

## Circular Dependency Check

A thorough review of import statements across all layers revealed **no circular dependencies**. Each layer’s imports are confined to:
- Same layer
- Lower layers
- Cross‑cutting abstractions (contracts, schemas, standard libraries)

Examples of checked pairs:
- Ingestion ↔ Extraction: No circularity.
- Detection ↔ Scoring: Detection does not import scoring; scoring depends on detection results (downward).
- Orchestration ↔ Engines: Orchestration depends on engines; engines do not import orchestration.
- Benchmark → Processing: Benchmark depends on processing benchmark engine (downward); processing does not depend on benchmark.

## Architectural Patterns Observed

- **Layered Architecture**: Clear separation of concerns with well‑defined layer responsibilities.
- **Dependency Injection**: The `AnalysisPipeline` constructor accepts engine implementations, allowing inversion of control and easy substitution (e.g., with mocks for testing).
- **Interface‑Based Programming**: All engine interactions occur through interfaces defined in `src/miie/contracts/interfaces.py`.
- **Registry Pattern**: The `DetectorRegistry` manages registration and lookup of detector instances.
- **Pipeline Pattern**: The `AnalysisPipeline` executes a fixed sequence of steps (ingestion → extraction → segmentation → detection → scoring → evidence → explanation → reporting).
- **Mock Implementations**: Each layer provides mock implementations (prefixed with `Mock`) for testing, ensuring deterministic behavior.

## Findings and Concerns

### ✅ Strengths
- Clean layering with no upward dependencies.
- Proper use of interfaces and dependency injection.
- Comprehensive encapsulation of responsibilities.
- Extensible design (easy to add new detectors, metrics, or workflows).
- Clear separation between core processing and benchmark/evaluation concerns.

### ⚠️ Minor Concerns
1. **BenchmarkRunner’s dependency on `processing.benchmark.engine`**: While this is a downward dependency (acceptable), it creates a tight coupling between the benchmark layer and a specific implementation of the benchmark engine. Ideally, the benchmark layer should depend only on the `IBenchmarkEngine` interface, with the concrete implementation provided via dependency injection (similar to other engines). However, the current `BenchmarkRunner` already receives an `IBenchmarkEngine` instance via composition (see `BenchmarkRunner.__init__` which creates an internal `ProcessingBenchmarkEngine`). This is acceptable but could be refined to accept the engine externally for greater flexibility.
2. **Detector Dispatcher’s `windows` parameter typing**: In `DetectorDispatcherEngine.invoke`, the `windows` parameter is typed as `List[object]` to avoid circular import with `WindowDefinition`. This is a common workaround and does not affect functionality, but it reduces type safety. Consider refactoring to break the circular dependency (e.g., by moving `WindowDefinition` to a shared schema layer already used by both parties).
3. **Missing explicit evidence engine interface in contracts**: Although `IEvidenceEngine` is referenced in the pipeline and implementation exists, a double‑check of the contracts interface file confirms it is present (found in `src/miie/contracts/interfaces.py`). No issue.

### ❌ Violations
- **None detected**: No violations of architectural boundaries (e.g., no processing layer accessing CLI or orchestration layers directly inappropriately). All dependencies respect the layered hierarchy.

## Recommendations

1. **Consider Dependency Injection for Benchmark Engine**: Modify `BenchmarkRunner` to accept an `IBenchmarkEngine` instance in its constructor (defaulting to a `ProcessingBenchmarkEngine` if none provided), aligning it with the pattern used by `AnalysisPipeline`.
2. **Refactor Window Definition Sharing**: Ensure `WindowDefinition` resides in a truly shared layer (it already does in `src/miie/schemas/models.py`) and adjust any import workarounds to use proper typing.
3. **Document Layering Rules**: Add architectural decision records (ADRs) or comments in layer root files to clarify allowed dependencies (e.g., “Layer X may only depend on layers Y and Z or cross‑cutting contracts”).

## Conclusion

The MIIE system exhibits a well‑structured layered architecture with clear separation of responsibilities, proper dependency direction, and no circular dependencies or architectural violations. The system adheres to established architectural principles and is ready for further development and scaling.

**Audit Completed**: 2026-06-20  
**Auditor**: TRDArchitect Agent (FERA Audit Phase 5)
