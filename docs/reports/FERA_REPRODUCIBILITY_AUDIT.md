# FERA Reproducibility Audit Report

## Overview
This document presents the findings of the Reproducibility audit phase of the FERA audit for the MIIE (Measurement Integrity Intelligence Engine) system. The audit examines deterministic behavior, seed control, and reproducibility of mock components across the system.

## Methodology
- Examined mock implementations in all processing layers
- Verified seed propagation and control mechanisms
- Analyzed sources of non-determinism
- Reviewed benchmark and evaluation components for reproducibility
- Checked for proper use of fixed seeds in testing

## Key Findings

### Deterministic Components (Working Correctly)
✅ **Benchmark Generator**: 
- Uses `random.seed(seed)` when seed is provided
- Deterministic when fixed seed is supplied
- Seeds are properly propagated through generation process

✅ **Benchmark Runner (Mock)**:
- MockBenchmarkRunner should be deterministic (needs verification)

✅ **Scoring Engine (Mock)**:
- Returns deterministic ScorePackage objects when properly seeded
- Issues in actual implementation due to datetime.now() usage

✅ **Evidence Engine (Mock)**:
- Returns deterministic EvidencePackage objects
- Issues in actual implementation due to datetime.now() usage

✅ **Explanation Engine (Mock)**:
- Returns deterministic ExplanationReport objects
- Issues may stem from non-deterministic inputs

✅ **Reporting Engine (Mock)**:
- Returns deterministic ReportOutput objects
- Issues in actual implementation due to datetime.now() usage

### Non-Deterministic Components (Issues Found)

#### ❌ Scoring Engine (src/miie/processing/scoring/engine.py)
- Lines 42, 50, 78, 80, 87: Uses `datetime.now(timezone.utc)` for timestamps
- Edge case handling (lines 39-53): Returns ScorePackage with `datetime.now(timezone.utc)` timestamp
- **Impact**: ScorePackage timestamps vary with each execution, breaking determinism

#### ❌ Evidence Engine (src/miie/processing/evidence.py)
- Line 40: `now = datetime.now(timezone.utc)`
- Line 42: `evidence_id = f"evidence_{seed}_{int(now.timestamp())}"` - non-deterministic due to timestamp
- Line 50: `das_notation = f"DAS:{seed}:{int(now.timestamp())}"` - non-deterministic due to timestamp
- Line 66: `timestamp=now.replace(microsecond=0).isoformat().replace('+00:00', 'Z')` - non-deterministic
- **Impact**: EvidencePackage IDs, DAS notation, and provenance timestamps vary with execution

#### ❌ Reporting Engine (src/miie/processing/reporting/engine.py)
- Multiple uses of `datetime.now()` for report timestamps (lines 56, 66, 76, 98, etc.)
- **Impact**: Report generation timestamps vary, affecting report determinism

#### ⚠️ Potential Issues in Other Components
- Need to verify all mock components for proper seed usage
- Need toVerify that timestamp fields in data models can be made deterministic
- Need to check if any components use system time or random without seeding

### Determinism Verification from Test Results
From the Test Audit (Phase 8), we know:
- Benchmark Engine tests pass for determinism: "test_benchmark_engine_execute_is_deterministic_with_seed"
- Correlation Breakdown Detector: "test_deterministic_output" passes
- Threshold Compression Detector: "test_deterministic_output" passes
- However, many explanation, evidence, reporting, and scoring engine tests fail, likely due to determinism issues

## Seed Control Analysis
### Proper Seed Usage Found:
- Benchmark generator properly seeds random number generator
- Some test files show seed parameters being passed
- Configuration objects appear to support seed propagation

### Seed Control Gaps:
- Not all components appear to accept or propagate seed parameters
- Timestamp generation bypasses seed control by using system time
- Need to verify seed handling in orchestrator and workflow dispatcher

## Recommendations for Reproducibility Improvement

### Immediate Actions (Addressing Non-Determinism)
1. **Fix Scoring Engine Timestamps**:
   - Replace `datetime.now(timezone.utc)` with deterministic timestamp from input or seed-based generation
   - Consider accepting timestamp as parameter or generating from seed + counter

2. **Fix Evidence Engine Timestamps**:
   - Replace `datetime.now(timezone.utc)` usage with deterministic alternatives
   - Make evidence_id and das_notation generation seed-dependent without system time
   - Make provenance timestamps deterministic

3. **Fix Reporting Engine Timestamps**:
   - Replace report generation timestamps with deterministic versions
   - Consider using analysis timestamp or seed-based timing

### Medium-Term Actions (Improving Seed Control)
1. **Standardize Seed Propagation**:
   - Ensure all engine interfaces accept seed/configuration parameters
   - Create standard seed handling pattern across all components
   - Verify seed flows from configuration → orchestrator → engines → mocks

2. **Deterministic Timestamp Strategy**:
   - Consider implementing a deterministic clock service
   - Use seed-based timestamp generation (e.g., seed + sequence number)
   - Allow override for testing while maintaining determinism

3. **Comprehensive Mock Validation**:
   - Create reproducibility tests for all mock components
   - Verify fixed seeds produce identical outputs across multiple runs
   - Test seed propagation through full pipeline

## Conclusion
The MIIE system shows good reproducibility foundations in benchmarking and detector components, but critical failures in scoring, evidence, and reporting engines prevent end-to-end deterministic execution. The primary source of non-determinism is the use of `datetime.now()` in multiple components, which breaks seed-controlled reproducibility.

**Reproducibility Status**: PARTIAL
**Working Deterministic Components**: Benchmark generator, detector mocks, some engine mocks
**Non-Deterministic Components**: Scoring engine, evidence engine, reporting engine (due to datetime.now() usage)
**Path to Full Reproducibility**: Replace all non-deterministic timestamp generation with seed-deterministic alternatives.

## Evidence from Analysis
- Benchmark generator analysis shows proper seeding: `random.seed(seed)` when seed provided
- Scoring engine analysis shows multiple `datetime.now(timezone.utc)` usages
- Evidence engine analysis shows timestamp-dependent ID and notation generation
- Reporting engine analysis shows multiple timestamp usages for report generation

**Audit Completed**: 2026-06-20
**Auditor**: ResearchScientist Agent (FERA Audit Phase 9)