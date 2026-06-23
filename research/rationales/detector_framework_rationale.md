# Detector Framework Rationale

## Overview
This document outlines the reasoning behind the MIIE v1.0 Detector Framework design decisions for Day 8 implementation.

## Framework Design Principles

### Separation of Concerns
The Detector Framework follows a clean separation of concerns:
- **BaseDetector**: Defines the contract for all detectors
- **DetectorRegistry**: Manages detector lifecycle and lookup
- **DetectorDispatcher**: Handles routing and orchestration
- **DetectorRunner**: Executes detectors and collects results
- **MockDetectors**: Provide testable implementations

### Contract-First Development
All components adhere strictly to defined interfaces:
- BaseDetector follows the detection contract pattern
- Registry maintains strict validation of detector IDs (D-01 through D-03 only)
- Dispatcher and Router operate on abstractions, not concrete implementations

### Extensibility without Modification
The framework is designed to be extensible:
- New detectors can be added by implementing BaseDetector
- Registry prevents invalid detector IDs while allowing future expansion
- Dispatcher and Runner require no changes for new detectors

## Why This Design?

### Infrastructure-First Approach
Day 8 focuses exclusively on establishing the detector infrastructure:
- No detection mathematics are implemented
- No scoring, evidence generation, or explanation capabilities
- Pure routing, validation, and execution mechanisms

### Testability
The mock detector implementations enable comprehensive testing:
- Registry validation tests
- Dispatcher routing tests  
- Runner execution tests
- Integration tests with extraction pipeline

### Deterministic Behavior
All framework components maintain deterministic behavior:
- Detector execution order is predictable
- Registry lookup is consistent
- Dispatcher routing follows defined rules
- Runner processes detectors in sorted order

## Framework Components

### BaseDetector
Provides the abstract foundation for all detectors:
- Standardized interface (detector_id, name, supported_metrics)
- Input validation contract
- Execution contract returning DetectorResult
- No implementation details (pure abstraction)

### DetectorRegistry
Manages the detector ecosystem:
- Strict validation of allowed detector IDs (D-01-D-03)
- Prevention of duplicate registrations
- Lookup capabilities by ID
- Enumeration of all registered detectors

### DetectorDispatcher
Routes metric data to appropriate detectors:
- Accepts MetricDataFrame input
- Supports selective detector enabling
- Returns DetectorResults container
- Handles validation delegation to detectors

### DetectorRunner
Executes detectors and manages results:
- Runs all registered detectors
- Handles execution failures gracefully
- Maintains deterministic result ordering
- Provides selective detector execution

### Mock Detectors
Enable testing without actual detection logic:
- MockDistributionDriftDetector (D-01)
- MockCorrelationBreakdownDetector (D-02)
- MockThresholdCompressionDetector (D-03)
- Each returns schema-valid DetectorResult with deterministic placeholder values
- No actual detection mathematics implemented

## Integration Points

### Input: MetricDataFrame
- Consumes output from MetricExtractionEngine (Day 7)
- Requires M-02 (Commit Frequency) and M-06 (Code Churn) metrics
- Follows missing data policy (unavailable metrics return None)

### Output: DetectorResult
- Produces schema-compliant detector outputs
- Ready for consumption by scoring framework (Day 9)
- Contains detector-specific output dictionaries
- Maintains traceability through timestamps

## Compliance with Standards

### BSD-Engineering v1.0
- Follows Section 8 detector class patterns
- Uses JSON serialization compatible formats
- Maintains deterministic run IDs and timestamps

### TFS v1.0
- Implements trust-minimized verification through validation
- Maintains transparent, auditable component interactions

### ACS v1.0
- Uses standardized data structures
- Follows entity-extraction patterns
- Maintains schema validation

## Assumptions and Limitations

### Assumptions
- MetricExtractionEngine provides valid MetricDataFrame
- Required metrics (M-02, M-06) are available for detector validation
- Downstream components will consume DetectorResult outputs

### Limitations
- Framework does not implement actual detection algorithms
- No error propagation beyond basic validation handling
- Limited to three specific detector types (D-01-D-03) in initial implementation
- No configuration system for detector parameters

## Future Extensions

### Phase 2 Enhensions
- Configuration management for detector parameters
- Plugin architecture for dynamic detector loading
- Performance monitoring and metrics collection
- Detailed error reporting and logging

### Standards Compliance
- Full ACS v1.0 DetectorResults implementation
- TFS v1.0 trust minimization enhancements
- BSD-Engineering v1.0 feature completeness

## Conclusion
The Detector Framework provides a solid infrastructure foundation for Day 8 that:
- Establishes clear separation of concerns
- Follows contract-first development principles
- Enables comprehensive testing through mock implementations
- Maintains deterministic behavior and strict validation
- Prepares the system for Day 9 scoring framework integration
- Complies with all relevant standards (TFS, ACS, BSD-Engineering)
