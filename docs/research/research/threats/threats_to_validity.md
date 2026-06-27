# Threats to Validity Log - Day 5 and Day 6

## Objective
Create initial internal/external/construct/conclusion validity risk log for the orchestration-only pipeline skeleton.

## Internal Validity Threats

### 1. Mock Determinism Compromised by Mutable Defaults
- **Description:** Mock services might inadvertently use mutable defaults or current time, causing non-deterministic test results
- **Mitigation:** All mocks use fixed seeds, explicit parameters, and avoid datetime.now() without injection
- **Evidence Review:** Checked mock_services.py - uses fixed run ID "test-run-001", explicit seed 42, deterministic calculations

### 2. Workflow History Contamination Between Tests
- **Description:** WorkflowDispatcher's history list might retain state between test runs
- **Mitigation:** Each test creates fresh WorkflowDispatcher instance; clear_workflow_history() available
- **Evidence Review:** Unit tests verify history isolation through separate instances

### 3. Protocol Interface Drift
- **Description:** Accidental addition of methods to protocols that concrete implementations don't satisfy
- **Mitigation:** Contract tests verify protocol compliance; mypy strict mode
- **Evidence Review:** Contract test suite passes; mypy配置 in pyproject.toml

## External Validity Threats (Day 5)

### 1. Overfitting to Specific Mock Implementation
- **Description:** Orchestration logic might depend on specific mock behaviors rather than protocol contracts
- **Mitigation:** Pipeline uses only protocol interfaces; multiple mock implementations possible
- **Evidence Review:** AnalysisPipeline.py shows zero references to mock classes, only protocol types

### 2. Limited Workflow Scope
- **Description:** WF-01 through WF-05 may not represent all realistic workflow combinations
- **Mitigation:** Based on AFD-defined workflows; extensible design allows adding new workflow types
- **Evidence Review:** WorkflowType enum maps directly to AFD workflow definitions

### 3. Missing Error Propagation Realism
- **Description:** Mock engines don't simulate realistic failure modes (timeouts, partial results, etc.)
- **Mitigation:** Error handling tested through ACS error model; real implementations will provide realistic errors
- **Evidence Review:** Contract tests include error validation; WorkflowDispatcher captures error results

## External Validity Threats (Day 6)

### 1. Shallow Clone Risks
- **Description:** Repository ingestion using shallow clones may truncate history, affecting metrics that rely on full commit history (e.g., churn, developer count).
- **Mitigation:** Use --depth=full or ensure minimum depth configurable; validate history depth during ingestion.
- **Evidence Review:** To be implemented in Day 6 ingestion pipeline.

### 2. Missing History Risks
- **Description:** Incomplete Git history due to shallow clones, partial mirrors, or corrupted repositories leading to biased metrics.
- **Mitigation:** Implement history verification checks; flag repositories with missing objects; fallback to available history with caveats.
- **Evidence Review:** To be implemented in Day 6 ingestion pipeline.

---

# Threats to Validity Log - Day 7

## Objective
Add construct validity risks for Git-derived metrics relevant to metric extraction foundation.

## Construct Validity Threats (Day 7)

### 1. Commit Frequency Misinterpretation Risk
- **Description:** M-02 (Commit Frequency) may be misinterpreted as a measure of developer productivity or work quality when it only measures commit count frequency
- **Mitigation:** Documentation emphasizes M-02 as a raw activity metric; missing data policy prevents fabrication; research notes document limitations
- **Evidence Review:** research/metric_extraction_rationale.md documents why M-02 is selected first despite limitations; literature_notes.md cites Zimmermann et al. on commit frequency limitations

### 2. Code Churn Semantic Ambiguity Risk
- **Description:** M-06 (Code Churn) measurements may not accurately reflect meaningful code changes due to whitespace changes, formatting adjustments, or generated code fluctuations
- **Mitigation:** Implementation follows standard Git numstat approach; documentation notes limitations; missing data policy prevents false precision
- **Evidence Review:** research/threats_to_validity.md documents this specific threat; extraction implementation uses standard git log --numstat approach

### 3. Git-Derived Metric Context Collapse Risk
- **Description:** Extracting metrics from Git history loses contextual information about commit intent, review processes, and collaborative aspects that affect metric interpretation
- **Mitigation:** Clear separation between available and unavailable metrics; documentation of extraction limitations; foundation-only implementation avoids overclaiming
- **Evidence Review:** research/literature_notes.md updates include Hassan (2009) and Kawaguchi & Jones (2008) on Git mining limitations; metric registry clearly marks M-01, M-03, M-04, M-05, M-07 as unavailable

### 4. Repository Heterogeneity Bias Risk
- **Description:** Different teams, projects, and workflows create non-comparable Git histories that threaten cross-repository metric validity (e.g., squash merging vs. feature branching strategies)
- **Mitigation:** Time-range filtering allows comparison of equivalent periods; exclude_bots option reduces automation noise; documentation notes repository-specific interpretation needs
- **Evidence Review:** Implementation includes since/until parameters and exclude_bots flag; research notes document workflow considerations

## Connection to Day 8+ Work
These construct validity threats inform:
- Detector design: Metrics as proxy inputs requiring validation against external criteria
- Benchmark requirements: Synthetic repositories should represent diverse workflow patterns
- Research agenda: Need for studies correlating Git-derived metrics with validated external measures of software engineering constructs
## Day 8: Detector Framework Threats to Validity

### False Framework Assumptions
- **Assumption**: Detector framework will adequately support future detection algorithms
  - **Threat**: Framework may be too rigid or too loose for actual detection needs
  - **Mitigation**: Framework designed with minimal assumptions; actual detectors implement specific logic
  
- **Assumption**: Three detectors (D-01-D-03) represent sufficient initial detector set
  - **Threat**: May not represent the full spectrum of needed detection capabilities
  - **Mitigation**: Framework designed for easy extension; additional detectors can be added

### Detector Coupling Risks
- **Temporal Coupling**: Detectors assuming specific execution order
  - **Risk**: Detectors may inadvertently depend on execution sequence
  - **Mitigation**: Framework documentation specifies detectors should be order-independent
  
- **Data Coupling**: Detectors sharing internal state through metric dataframe
  - **Risk**: Detectors modifying shared metric data causing interference
  - **Mitigation**: MetricDataFrame is immutable; detectors receive read-only access
  
- **Interface Coupling**: Over-reliance on specific detector interface methods
  - **Risk**: Changes to BaseDetector breaking all detectors
  - **Mitigation**: Interface standardized; changes require coordinated updates

### Registry Bias Risks
- **Registration Order Bias**: Assuming registry ordering reflects priority or importance
  - **Risk**: Users may interpret D-01 as more important than D-03
  - **Mitigation**: Documentation clarifies IDs are arbitrary identifiers, not priority indicators
  
- **Registry Lookup Performance**: Assuming constant-time lookup remains sufficient
  - **Risk**: Performance degradation with large numbers of detectors
  - **Mitigation**: Current implementation uses dictionary lookup; scalability addressed in future versions
  
- **Registry Security**: Assuming all registered detectors are trustworthy
  - **Risk**: Malicious detector registration in extensible version
  - **Mitigation**: Initial version has fixed registry; security considerations for plugin architecture

### Framework Completeness Risks
- **Insufficient Abstraction**: Framework missing key detector capabilities
  - **Risk**: Need to modify framework for actual detector implementation
  - **Mitigation**: Minimal viable framework; actual detection logic resides in detector implementations
  
- **Over-Engineering**: Framework providing more abstraction than needed
  - **Risk**: Unnecessary complexity for simple detection needs
  - **Mitigation**: Framework implements only essential routing, validation, and execution functions
  
- **Performance Overhead**: Framework introducing unacceptable latency
  - **Risk**: Indirection through interfaces impacting detection performance
  - **Mitigation**: Minimal interface dispatch; actual detector logic dominates performance

### Testing Threats
- **Mock Detector Fidelity**: Mock detectors not representing real detector behavior
  - **Risk**: Tests passing with mocks but failing with real implementations
  - **Mitigation**: Mocks validate schema compliance and execution contracts, not detection logic
  
- **Integration Test Completeness**: Extraction-to-detection tests not covering edge cases
  - **Risk**: Integration issues only appearing in production
  - **Mitigation**: Tests cover validation failures, missing metrics, and exception handling

### Standards Compliance Risks
- **BSD-Engineering Conformance**: Framework not fully meeting detector specifications
  - **Risk**: Incompatibility with BSD-Engineering v1.0 detector expectations
  - **Mitigation**: Framework aligned with Section 8 detector class patterns and JSON serialization
  
- **ACS v1.0 DetectorResults**: Output not fully compliant with ACS specifications
  - **Risk**: Downstream components unable to consume detector outputs
  - **Mitigation**: DetectorResult structure follows ACS patterns for detection outputs
  
- **TFS v1.0 Trust Minimization**: Framework not providing sufficient verification capabilities
  - **Risk**: Inability to verify detector correctness in trust-minimized environment
  - **Mitigation**: Framework validation and verification hooks support trust minimization principles

### Scalability Threats
- **Detector Count Scalability**: Framework performance degrading with many detectors
  - **Risk**: Registry lookup or dispatcher routing becoming bottleneck
  - **Mitigation**: O(1) lookup and O(n) dispatch where n is enabled detectors (typically small)
  
- **Metric Dataframe Size**: Framework not handling large metric datasets efficiently
  - **Risk**: Memory or performance issues with large-scale metric extraction
  - **Mitigation: Framework passes metric dataframe by reference; detectors responsible for efficient processing
