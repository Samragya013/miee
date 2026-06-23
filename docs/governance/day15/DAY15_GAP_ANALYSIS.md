# DAY 15 GAP ANALYSIS
## D02 CORRELATION BREAKDOWN DETECTOR IMPLEMENTATION

### Repository Structure Analysis

#### Implemented Components
- Detector framework base classes (`src/miie/processing/detection/base.py`)
- Detector registry (`src/miie/processing/detection/registry.py`)
- Detector dispatcher (`src/miie/processing/detection/dispatcher.py`)
- Detector runner (`src/miie/processing/detection/runner.py`)
- Mock detectors for testing (`src/miie/processing/detection/mock_detectors.py`)
- Mock detector engine for dry-run (`src/miie/processing/detection/mock_detectors.py`)
- Pipeline orchestration (`src/miie/orchestration/pipeline.py`)
- CLI command structure (`src/miie/cli.py`)

#### Partial Components
- **Detector Engine Initialization (CLI)**: 
  - In `src/miie/cli.py` line 65, `detection_engine = DetectorDispatcherEngine()` is called without required `registry` argument
  - This will cause a `TypeError` when running in non-dry-run mode
  - MockDetectorEngine correctly initializes its own registry with mock detectors (lines 179-184 in mock_detectors.py)

#### Missing Components
- **Real D-02 Detector Implementation**: 
  - No implementation of `CorrelationBreakdownDetector` class in `src/miie/processing/detection/`
  - Required per TFS Section 5.2 for Correlation Breakdown Detector algorithm
- **Real D-01 Detector Implementation**: 
  - No implementation of `DistributionDriftDetector` class (though implied by verification passing)
  - Required per TFS Section 5.1 for Distributional Drift Detector algorithm
- **Real D-03 Detector Implementation**: 
  - No implementation of `ThresholdCompressionDetector` class
  - Required per TFS Section 5.3 for Threshold Compression Detector algorithm
- **Detector Registration in CLI**:
  - Non-dry-run mode lacks detector registration logic (should register D-01, D-02, D-03 with DetectorRegistry)
- **Unit Tests for D-02**:
  - No test file for D-02 detector (`tests/unit/test_d02_correlation_breakdown.py` missing)
  - No integration tests for D-02 in pipeline
- **Benchmark Validation Artifacts**:
  - No correlation-breakdown-v1.0.0 benchmark suite in `~/.miie/benchmarks/` (would be created by benchmark maintainers)
  - No ground truth files for correlation breakdown validation

#### Broken Components
- **Non-Dry-Run Detector Engine Initialization**:
  - `DetectorDispatcherEngine()` called without required `DetectiveRegistry` argument in `src/miie/cli.py:65`
  - Will cause `TypeError: __init__() missing 1 required positional argument: 'registry'` when `--dry-run` flag is not used
  - Blocks execution of real detector pipeline

### Required Work for Day 15
1. Implement real `CorrelationBreakdownDetector` class per TFS Section 5.2 algorithm
2. Implement real `DistributionDriftDetector` class per TFS Section 5.1 (if missing)
3. Implement real `ThresholdCompressionDetector` class per TFS Section 5.3 (if missing)
4. Fix detector engine initialization in `src/miie/cli.py` to properly register real detectors
5. Create unit tests for D-02 detector (`tests/unit/test_d02_correlation_breakdown.py`)
6. Create integration tests for D-02 in pipeline
7. Verify detector outputs match TFS example calculations
8. Ensure reproducibility with fixed seed
9. Validate against TFS precision/recall requirements

### Optional Work
- Performance optimization of correlation calculations
- Additional edge case handling in detector validation
- Enhanced error messaging for detector failures

### Forbidden Work
- Modifying detector algorithms beyond TFS Section 5.2 specification
- Implementing additional detectors (D-04+) beyond frozen V1 set
- Changing Integrity Score formula (TFS Section 6.3)
- Changing Confidence Score formula (TFS Section 7.4)
- Modifying detector weights (w₁=0.40, w₂=0.35, w₃=0.25) without configuration mechanism
- Implementing machine learning components in detectors
- Changing detector interface contracts in `src/miie/contracts/interfaces.py`

### Immediate Next Step (Loop 1)
Create `D02_AUTHORITY_SPEC.md` by extracting exact requirements from TFS Section 5.2