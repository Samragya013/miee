# FERA Requirement Matrix

## Day 0–10 Operating Plan
- **File**: `docs\authorities\MIIE_Day_0_to_Day_10_Execution_Operating_Plan.md`
- **Description**: The operating plan for the first 10 days of execution, detailing objectives, tasks, and deliverables for each day. It outlines the foundational work to turn the frozen MIIE v1.0 document stack into an executable, reviewable, research-grade engineering foundation.

## Day 11–20 Operating Plan
- **File**: `docs\authorities\MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md`
- **Description**: The operating plan for days 11 through 20, focusing on completing the Day 10 dry-run capability and establishing foundations for:
  - Window segmentation (M-03)
  - Scoring engine (M-08)
  - Evidence integration with detector outputs
  - Report generator templates
  - Benchmark candidate expansion (from 30 to 120 candidates)
  - Ground truth workflow
  - Benchmark runner implementation
  - Evaluation engine implementation
  - Integration and end-to-end testing
  - Day 20 milestone review

## Certification Packages
- **File**: `DAY15_CERTIFICATION_PACKAGE.md`
- **Description**: The complete certification evidence package for the Day 15 D02 Correlation Breakdown Detector implementation. It consolidates all verification activities performed by the MIIE Loop Governance Board to determine whether Day 15 is complete and ready for transition to Day 16. Includes requirement matrix, authority reviews, architecture certification, mathematical certification, test certification, reproducibility certification, failure hunt results, risks, technical debt, and certification baseline.
- **Related File**: `DAY15_CERTIFICATION_LOOP_START.md` - Marks the beginning of the certification loop.

## Readiness Packages
- **File**: `READY_FOR_DAY16.md`
- **Description**: A readiness package that authorizes the start of the Day 16 implementation loop. It confirms that the Day 15 D02 Correlation Breakdown Detector implementation has been fully certified, outlines remaining technical debt and known risks, lists Day 16 prerequisites, and provides an approved start date (2026-06-21).
- **Related Files**: 
  - `BENCHMARK_READINESS_REPORT.md` - Assesses the readiness of benchmark infrastructure for Day 12 scoring engine foundation work.
  - `BENCHMARK_READY_SUMMARY.md` - Documents fixes to SessionStart hook error, MIIE analysis pipeline import issues, DateTime serialization issues, and EvidencePackage class definition, along with next steps for running benchmarks.
