# DAY 15 PRE-IMPLEMENTATION ANALYSIS
## Repository Reality Check for D02 Correlation Breakdown Detector

### Existing Detector Framework
- **Location**: `src/miie/processing/detection/`
- **Components**:
  - `base.py`: Abstract `BaseDetector` class defining the detector interface
  - `registry.py`: `DetectorRegistry` for managing detector instances (validates D-01, D-02, D-03)
  - `dispatcher.py`: `DetectorDispatcherEngine` implementing `IDetectorEngine` interface
  - `runner.py`: `DetectorRunner` for executing detectors through registry
  - `mock_detectors.py`: Mock implementations for testing (D-01, D-02, D-03)
  - `__init__.py`: Exports detector framework components

### Existing Detector Interfaces
- **Base Interface**: `BaseDetector` (in `base.py`) requires:
  - `detector_id` (string, e.g., "D-02")
  - `detector_name` (human-readable name)
  - `supported_metrics` (list of metric IDs this detector supports)
  - `validate_input(MetricDataFrame) -> bool` method
  - `execute(MetricDataFrame) -> DetectorResult` method
- **Detector Result Schema**: Defined in `src/miie/schemas/models.py`:
  - `DetectorResult`: Contains `detector_outputs` dict mapping detector IDs to result dicts
  - `DetectorResults`: Container for multiple detector results

### Existing Detector Registry
- **Implementation**: `DetectorRegistry` class in `registry.py`
- **Functionality**:
  - Registers detectors by ID (validates against allowed set: {"D-01", "D-02", "D-03"})
  - Prevents duplicate registrations
  - Provides lookup by ID (`get()`)
  - Lists all registered detectors (`get_all()`)
  - Used by `DetectorDispatcherEngine` and `DetectorRunner`

### Existing Evidence Integration
- **Location**: `src/miie/processing/evidence.py`
- **Integration Points**:
  - EvidenceEngine.generate() accepts `detector_results: DetectorResults` parameter
  - Extracts detector IDs via `list(detector_results.detector_outputs.keys())`
  - Stores detector outputs in evidence package under `detector_outputs` field
  - Requires detector outputs to be dict structure compatible with EvidencePackage schema

### Existing Pipeline Integration
- **Location**: `src/miie/orchestration/pipeline.py`
- **Integration Points**:
  - AnalysisPipeline constructor accepts `detection_engine: IDetectorEngine`
  - Step 4: `detector_results = self.detection_engine.invoke(...)`
  - Invokes detection engine with:
    - `metric_dataframe`: Extracted metrics
    - `windows`: List of window definitions
    - `detector_config`: Optional detector configuration
    - `enabled_detectors`: Optional list of detector IDs to enable
  - Passes detector results to scoring engine (Step 5)
  - Includes detector results in evidence package (Step 6)
  - Includes detector results in explanation generation (Step 7)
  - Includes detector results in final analysis result for reporting (Step 10)

### Current Implementation Status
- **Detector Framework**: Complete (interfaces, registry, dispatcher, runner)
- **Mock Detectors**: Complete (D-01, D-02, D-03 mocks in `mock_detectors.py`)
- **Real Detectors**: 
  - D-01 (Distribution Drift): **MISSING** (only mock exists)
  - D-02 (Correlation Breakdown): **MISSING** (only mock exists)
  - D-03 (Threshold Compression): **MISSING** (only mock exists)
- **CLI Integration**: 
  - Dry-run mode: Uses `MockDetectorEngine` (functional)
  - Non-dry-run mode: **BROKEN** - calls `DetectorDispatcherEngine()` without required `registry` argument
- **Evidence Package Compatibility**: 
  - EvidencePackage schema expects `detector_outputs` as `Dict[str, Dict]`
  - Current mock detectors return compatible structure
  - Real detectors must return same structure

### Required Work for Day 15
1. **Implement Real Detectors**:
   - `DistributionDriftDetector` (D-01) per TFS Section 5.1
   - `CorrelationBreakdownDetector` (D-02) per TFS Section 5.2 (primary focus)
   - `ThresholdCompressionDetector` (D-03) per TFS Section 5.3
2. **Fix CLI Detector Initialization**:
   - In `src/miie/cli.py`, non-dry-run mode must instantiate `DetectorDispatcherEngine` with a registry containing real detectors
3. **Ensure Deterministic Output**:
   - All detectors must use seeded randomness where applicable (none for D-02 per TFS)
   - Output must be identical for same input/seed/configuration
4. **Maintain Interface Compliance**:
   - All real detectors must inherit from `BaseDetector`
   - Implement `validate_input()` and `execute()` per base class contract
   - Return `DetectorResult` with proper `detector_outputs` structure

### Validation Criteria
- **Authority Compliance**: Detector algorithms must match TFS Section 5.2 exactly
- **Interface Compliance**: Must work with existing `DetectorDispatcherEngine` and `DetectorRunner`
- **Evidence Integration**: Output must be compatible with `EvidencePackage` schema
- **Pipeline Integration**: Must complete dry-run and non-dry-run execution without errors
- **Determinism**: Same input + seed must produce identical detector outputs
- **Detector Registration**: Real detectors must be registrable with `DetectorRegistry`

### Blocking Issues
1. **Missing Real Detectors**: No implementation of D-01, D-02, or D-03
2. **CLI Initialization Bug**: Non-dry-run mode fails with `TypeError` due to missing registry argument
3. **Detector Registration**: Non-dry-run mode lacks logic to instantiate and register real detectors

### Recommended Implementation Order
1. Fix CLI detector engine initialization to properly handle non-dry-run mode
2. Implement `DistributionDriftDetector` (D-01) per TFS Section 5.1
3. Implement `CorrelationBreakdownDetector` (D-02) per TFS Section 5.2 (Day 15 focus)
4. Implement `ThresholdCompressionDetector` (D-03) per TFS Section 5.3
5. Verify all three detectors register successfully with `DetectorRegistry`
6. Test deterministic output with fixed seed
7. Validate against TFS example calculations and evidence requirements

### Non-Blocking Work
- Performance optimization of correlation calculations
- Enhanced error handling and logging
- Additional input validation edge cases