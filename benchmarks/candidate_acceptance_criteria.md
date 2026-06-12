# Benchmark Candidate Acceptance Criteria - Day 5

## Objective
Define benchmark candidate acceptance criteria, not datasets yet, as specified in the Day 5 parallel research track.

## Acceptance Criteria Framework
For Day 5, we establish the structural and procedural criteria for evaluating benchmark candidates. Actual dataset population and validation will occur in subsequent days.

### 1. Structural Criteria

#### 1.1 Folder Structure Compliance
- **Criterion:** Candidate must follow the prescribed benchmark folder structure
- **Required Structure:**
  ```
  benchmarks/
    suites/
      <suite_id>/
        manifest.json
        schema.json  
        ground_truth.json
        data/
          <candidate_id>/
            metrics.json
            windows.json
  ```
- **Validation:** Automated folder structure test
- **Authority:** MIBS Section 4.2 (Benchmark Organization)

#### 1.2 Manifest Requirements
- **Criterion:** manifest.json must contain required metadata fields
- **Required Fields:**
  - suite_id (string)
  - candidate_id (string) 
  - version (string)
  - generated_at (ISO 8601 timestamp)
  - metadata_seed (integer)
  - pathology_injection_windows (list of window identifiers)
- **Validation:** JSON Schema validation against manifest.schema.json
- **Authority:** MIBS Section 5.1 (Manifest Specification)

#### 1.3 Schema Definitions
- **Criterion:** schema.json must define valid JSON Schema draft-07 for metrics and windows
- **Required Definitions:**
  - Metric format matching MetricDataFrame structure
  - Window format matching WindowDefinition structure
  - Detector result format matching DetectorResults structure
- **Validation:** JSON Schema validation; schema compilation test
- **Authority:** BSD-Engineering Section 3 (Schema Standards)

### 2. Procedural Criteria

#### 2.1 Generation Determinism
- **Criterion:** Candidate generation must be deterministic given fixed inputs
- **Requirements:**
  - Same seed + same parameters → identical output
  - No dependence on system time, network state, or external randomness
  - Pseudorandom generators must be seedable
- **Validation:** Run generation twice with identical inputs; byte-wise comparison
- **Authority:** IMP Section 7.3 (Deterministic Operations)

#### 2.2 Pathology Injection Controls
- **Criterion:** Synthetic pathologies must be injectable at specified windows
- **Requirements:**
  - Configurable pathology type and magnitude
  - Window-specific injection capability
  - Documentation of injection methodology
- **Validation:** Verify pathologies appear only in designated windows
- **Authority:** TFS Section 9.2 (Pathology Injection Framework)

#### 2.3 Metadata Completeness
- **Criterion:** All required metadata fields must be populated with valid values
- **Requirements:**
  - No placeholder or TODO values in final manifest
  - Appropriate data types for all fields
  - Consistent cross-referencing between files
- **Validation:** Schema validation; manual spot-check of samples
- **Authority:** MIBS Section 5.3 (Metadata Requirements)

### 3. Content Criteria (For Future Dataset Population)

#### 3.1 Metric Value Plausibility
- **Criterion:** Metric values should fall within empirically observed ranges
- **Guidelines (to be refined in Day 7+):**
  - Commit frequency: non-negative integers
  - Code churn: non-negative integers representing lines
  - Coverage metrics: 0-100 percentage values
- **Validation:** Range checking against empirically derived bounds
- **Authority:** TFS Section 2 (Metric Definitions)

#### 3.2 Window Consistency
- **Criterion:** Temporal windows must be non-overlapping and chronologically ordered
- **Requirements:**
  - No temporal gaps unless intentionally modeled
  - Consistent window size unless variable windows explicitly specified
  - Chronological ordering of window identifiers
- **Validation:** Temporal ordering and gap analysis
- **Authority:** AFD Section 3.1 (Windowing Strategy)

#### 3.3 Pathology Realism
- **Criterion:** Injected pathologies should resemble realistic anomalies
- **Guidelines (to be refined with domain expertise):**
  - Magnitude consistent with observed incident reports
  - Duration matching typical anomaly persistence
  - Temporal patterns resembling real-world events
- **Validation:** Subject matter expert review; comparison to incident databases
- **Authority:** FSR Section 4.3 (Anomaly Characterization)

## Acceptance Process

### 3.1 Structural Validation (Day 5-6)
- Automated folder structure testing
- Manifest JSON Schema validation  
- Schema JSON Schema validation
- Determinism testing with fixed seeds

### 3.2 Content Validation (Day 7+) 
- Metric range validation
- Window consistency checking  
- Pathology documentation review
- Cross-suite compatibility assessment

### 3.3 Approval Workflow
1. Candidate generation with documented parameters
2. Structural validation pass
3. Content validation review (Day 7+)
4. Pathology injection verification
5. Manifest approval and versioning
6. Archive to immutable storage

## Exclusions (Not Required for Day 5)
- Actual dataset population (begins Day 8)
- Ground truth establishment (begins Day 9) 
- Inter-rater agreement measurement (begins Day 10)
- Suite-level coherence validation (begins Day 11)

## Connection to Day 5 Orchestration Work
These criteria support the Day 5 objectives by:
1. Establishing validation boundaries for benchmark mocks
2. Defining structure that benchmark engines must consume/produce
3. Creating evaluation criteria for future benchmark implementation
4. Ensuring mock benchmark engines produce structurally valid output

## Review Criteria
Acceptance criteria will be reviewed against:
- MIBS_MIIE_v1.0.md (Benchmark Assumptions)
- TFS_MIIE_v1.0.md (Frozen Metrics/Detectors/Algorithms)
- AFD_MIIE_v1.0.md (Workflow Behavior)
- BSD-Engineering_MIIE_v1.0.md (Data Schemas)

## Next Steps
1. Implement structural validation scripts (Day 6)
2. Create candidate generation framework (Day 8)  
3. Establish pathology injection tooling (Day 8)
4. Begin actual candidate population (Day 8+)