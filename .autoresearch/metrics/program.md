# Experiment: All 7 Metrics Functional

## Goal
Make all 7 MIIE metrics (M-01 through M-07) extract successfully from real GitHub repositories with meaningful data.

## Current State
- M-01 (Specification Entropy): WORKING — git log classification
- M-02 (Commit Frequency): WORKING — git log count
- M-03 (Code Churn): WORKING — insertions + deletions
- M-04 (Test Coverage): WORKING — Cobertura/lcov/.coverage parser + git ls-files fallback
- M-05 (PR Review Latency): WORKING — GitHub PR API (requires GITHUB_TOKEN)
- M-06 (File Activity Breadth): WORKING — git log --stat file count
- M-07 (Branch Activity Recency): WORKING — git log branch freshness

## Strategy
1. Run full pipeline against test repos every 5 minutes
2. Verify all 7 metrics return data
3. Verify D-01 and D-02 detectors pass
4. Verify integrity score > 0.5
5. If any metric fails, investigate and fix

## Constraints
- DO NOT modify frozen core (detectors, scoring, evidence, contracts)
- DO NOT modify metric extraction logic in metrics/ directory
- Only modify extraction pipeline, providers, and CLI
- All 2757+ tests must continue passing

## Evaluation
- `python .autoresearch/metrics/scripts/evaluate.py` runs the full pipeline
- Returns number of metrics working (0-7)
- Success = 7 metrics working with non-null values
