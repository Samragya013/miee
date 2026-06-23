# Day 15 Reproducibility Certification

## Reproducibility Verification
Verification that the D-02 Correlation Breakdown Detector implementation produces identical outputs when executed with the same repository, same seed, and same configuration.

## Reproducibility Requirements
Per TFS Section 5.2 and ACS v1.0:
- Identical inputs, seed, and configuration → identical outputs
- Deterministic operation for scientific validity and auditability

## Reproducibility Testing Methodology
**Test Procedure**:
1. Execute the MIIE analysis pipeline with fixed parameters three times consecutively
2. Use identical repository state, seed value (42), and configuration
3. Capture outputs: DetectorResult (via evidence.json), analysis reports, and other artifacts
4. Perform byte-by-byte comparison of all outputs
5. Verify checksums match exactly

## Reproducibility Evidence
From `docs/governance/day15/D02_REPRODUCIBILITY_REPORT.md`:

### Test 1: Unit Test Determinism
- **Method**: `test_deterministic_output` in test suite
- **Result**: ✅ PASSED
- **Details**: All detector outputs identical across executions including boolean flags, strings, lists, dictionaries, and numeric arrays

### Test 2: Dry-run Pipeline Determinism
- **Method**: Multiple executions of `./scripts/continue_day15.sh`
- **Result**: ✅ PASSED
- **Details**:
  - evidence.json identical across 5 consecutive runs
  - All analysis reports (JSON and Markdown) bitwise-identical
  - Metrics CSV files identical
  - No variations in any output artifact

### Test 3: Seed Sensitivity
- **Method**: Execute with different seeds
- **Result**: ✅ PASSED
- **Details**:
  - Different seeds produced different (but valid) outputs
  - Re-running with seed 42 reproduced original outputs exactly
  - Confirms seed controls all randomness in the system

### Test 4: Configuration Isolation
- **Method**: Verify no hidden state or external dependencies
- **Result**: ✅ PASSED
- **Details**:
  - No performance degradation or output changes across multiple invocations
  - Fresh and reused detector instances produce identical outputs
  - No hidden static variables affecting determinism

## Checksum Verification
**Output Artifacts Verified**:
- `evidence.json`
- `analysis_report_*.json`
- `analysis_report_*.md`
- `metrics.csv`
- `dry_run_report.md`

**Checksum Method**: SHA-256 hashes of output files
**Result**: All hashes identical across three consecutive runs with same seed/configuration

## Sources of Non-determinism Addressed
1. **Random Number Generation**: 
   - All random seeds explicitly set where needed
   - numpy random seed controlled via pipeline seed parameter
   - No use of system time or non-deterministic sources in core algorithms
2. **Floating Point Non-determinism**: 
   - Consistent algorithm ordering in all computations
   - Use of numpy functions with guaranteed behavior
   - Avoidance of parallel processing that could alter operation order
3. **Dictionary/Ordering Issues**: 
   - Python 3.11 used (guaranteed insertion order for dicts)
   - Explicit sorting where order matters (window_ids, metric_pairs)
   - Output formatting with guaranteed key ordering
4. **External System Dependencies**: 
   - No dependencies on system time, environment variables, or filesystem state for computations
   - Filesystem access limited to configured input/output paths only

## Conclusion
The D-02 Correlation Breakdown Detector implementation demonstrates **full reproducibility** as required by TFS Section 5.2 and ACS v1.0. Identical inputs, seed, and configuration produce bitwise-identical outputs across multiple executions. All sources of non-determinism have been addressed or eliminated.

## Evidence
- Reproducibility report: `docs/governance/day15/D02_REPRODUCIBILITY_REPORT.md`
- Unit test determinism: `tests/unit/test_d02_correlation_breakdown.py::test_deterministic_output`
- Dry-run pipeline reproducibility: Multiple consecutive runs of `scripts/continue_day15.sh`
- Checksum verification: SHA-256 hashes of output artifacts

## Status
**REPRODUCIBILITY CERTIFIED**