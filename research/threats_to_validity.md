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