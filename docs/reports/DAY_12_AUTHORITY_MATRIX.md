# DAY 12 AUTHORITY MATRIX

| Requirement | Source Authority | Mandatory | Deferred | Out Of Scope |
|-------------|------------------|-----------|----------|--------------|
| Scoring Engine Foundation (M-08) Implementation | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 261-375 | ✅ YES |  |  |
| ScorePackage Schema Implementation | BSD-Engineering Section 9 | ✅ YES |  |  |
| Integrity Score Framework (weighted aggregation) | TFS Section 6 | ✅ YES |  |  |
| Confidence Score Framework (5 multiplicative factors) | TFS Section 7 | ✅ YES |  |  |
| Weight Redistribution Logic | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 289-293 | ✅ YES |  |  |
| Pipeline Integration (M-05 → M-08) | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 292-293 | ✅ YES |  |  |
| Real Detector Algorithms (D-01: KS+PSI, D-02: Pearson+Spearman, D-03: excess mass+dip) | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 33-36, 38, 54, 898-900, 912-914 |  | ✅ YES (Deferred to Days 21-25) |  |
| Full Seven-Metric Extraction (M-03..M-07) | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md line 38 |  | ✅ YES (Deferred Until After Day 20) |  |
| Scoring Engine Implementation (M-08: IS/CS formulas) | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md line 38 |  | ✅ YES (Deferred Until After Day 20) |  |
| Benchmark Generation (120 datasets) | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md line 38 |  | ✅ YES (Deferred Until After Day 20) |  |
| Full Report Generation beyond mock dry-run | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md line 38 |  | ✅ YES (Deferred Until After Day 20) |  |
| Detector Mathematics Implementation | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 33-36, 38, 54, 898-900, 912-914 |  | ✅ YES (Deferred to Days 21-25) |  |
| D-01, D-02, D-03 Detector Implementation | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 898-900, 912-914 |  | ✅ YES (Deferred to Days 21-25) |  |
| Actual detector algorithms requiring benchmark validation | MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 54, 898-900, 912-914 |  | ✅ YES (Deferred to Days 21-25) |  |

## EXPLICIT ANSWERS TO AUTHORITY QUESTIONS:

1. **Is detector mathematics authorized?** ❌ NO - Explicitly deferred to Days 21-25 per MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 33-36, 38, 54, 898-900, 912-914.

2. **Which detectors are authorized?** NONE - All detector algorithms (D-01, D-02, D-03) are deferred until benchmark readiness gates are passed.

3. **Which formulas are frozen?** 
   - Integrity Score formula: TFS Section 6
   - Confidence Score formula (5 multiplicative factors): TFS Section 7
   - ScorePackage schema: BSD-Engineering Section 9

4. **Which thresholds are frozen?** None specified for Day 12 - thresholds would be part of detector algorithms which are deferred.

5. **Which benchmark prerequisites must exist?** 
   - 30 synthetic benchmark candidates (from Day 8 foundation)
   - Benchmark directories and annotation workflow documented
   - Per MIEE_DAY11_TO_DAY20_OPERATING_PLAN.md lines 20-21: "Benchmark directories exist; 30 synthetic benchmark candidates exist as candidates only"

6. **Which ground truth requirements must exist?** 
   - Ground truth workflow is part of Day 16 (per lines 609-677), not required for Day 12
   - Day 12 only requires the scoring engine foundation, not ground truth

7. **Which validations are mandatory before implementation?**
   - Day 11 completion verified by: day11_signoff.md, day11_final_validation.md, day11_project_snapshot.md, day11_readiness_gate.md
   - All Day 0-11 tests must be passing (as evidenced by existing governance artifacts)
   - Architecture compliance must be maintained (Processing → Contracts → Schemas only)