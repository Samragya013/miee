# MIIE Metric Requirements

This document specifies the 7 software engineering metrics (M-01 through M-07) that MIIE measures, their data sources, extraction methods, and quality constraints.

## Metric Overview

| Metric | Name | Source | Unit | Description |
|--------|------|--------|------|-------------|
| M-01 | Specification Entropy | git commits | ratio | Entropy of commit message categories across windows |
| M-02 | Raw Commit Frequency | git commits | count | Number of commits per time window |
| M-03 | Code Churn Ratio | git diffs | ratio | Additions vs deletions per commit |
| M-04 | Test Coverage | coverage reports / proxy | percentage | Test file ratio or coverage report data |
| M-05 | PR Review Latency | GitHub API | hours | Time from PR creation to merge |
| M-06 | File Activity Breadth | git diffs | count | Number of unique files modified per window |
| M-07 | Branch Activity Recency | git branches | ratio | Ratio of recently active branches |

## Data Sources

### Git-Native Metrics (M-01, M-02, M-03, M-06, M-07)
- **Source**: Local git repository via `git log` and `git diff`
- **Provider**: `GitObservationProvider` (`src/miie/providers/git.py`)
- **Requirements**: Git installed, repository initialized
- **Quality**: `complete` (all data from git history)

### External API Metrics (M-05)
- **Source**: GitHub REST API v3
- **Provider**: `GitHubPullRequestProvider` (`src/miie/providers/github/provider.py`)
- **Requirements**: `GITHUB_TOKEN` environment variable, repository must have GitHub remote
- **Quality**: `complete` when API available, `missing` when not
- **Rate Limits**: 5000 requests/hour (authenticated), 60 requests/hour (unauthenticated)

### Proxy Metrics (M-04)
- **Source**: Coverage reports or git file analysis
- **Provider**: `GitObservationProvider._compute_test_coverage()`
- **Priority**: Cobertura XML → lcov.info → .coverage JSON → git ls-files proxy
- **Quality**: `complete` when real coverage found, `estimated` for proxy

## Extraction Pipeline

### Phase 1: Git Observations
1. `GitObservationProvider.extract_observations()` runs `git log` with date filters
2. `CommitExtractor` processes each commit:
   - M-02: Increments commit count
   - M-06: Counts unique files modified
   - M-03: Parses shortstat for additions/deletions ratio
3. `RepositorySummaryExtractor` computes aggregate metrics:
   - M-01: Classifies commit messages and computes entropy
   - M-07: Analyzes branch activity recency
   - M-04: Estimates test coverage from file patterns

### Phase 2: GitHub Observations (Optional)
1. `ExtractionEngine._extract_github_pr()` resolves GitHub owner/repo
2. `GitHubPullRequestProvider` fetches merged PRs via paginated API
3. M-05 observations created with merge latency (created_at → merged_at)

### Phase 3: Window Redistribution
1. `_redistribute_to_windows()` maps observations to time windows
2. Aggregate metrics (M-01, M-04, M-07) placed in last window
3. Per-commit metrics (M-02, M-03, M-05, M-06) distributed by timestamp

## Quality Constraints

### Minimum Requirements
- **M-01**: Requires meaningful commit message variation (≥3 categories)
- **M-02**: Requires ≥1 commit in window
- **M-03**: Requires ≥1 commit with additions/deletions
- **M-04**: Proxy quality varies by repository structure
- **M-05**: Requires GitHub API access + merged PRs
- **M-06**: Requires ≥1 file modification
- **M-07**: Requires ≥1 branch reference

### Bot Filtering
- Git-native metrics exclude bot authors using `_is_bot_author()` substring matching
- Patterns: `dependabot`, `renovate`, `github-actions`, `bot`, `noreply`, `ci-bot`, `deploy-bot`
- **Note**: Git `--author !pattern` is not used (broken on all platforms)

### None Handling
- `DetectorAdapter.to_metric_dataframe()` filters out `None` values before aggregation
- Windows with no observations for a metric receive `0.0` default

## Detector Interactions

### D-01: Distribution Drift
- Input: M-02 values across time windows
- Method: Kolmogorov-Smirnov test
- Output: `drift_detected: bool`, `p_value: float`

### D-02: Correlation Breakdown
- Input: M-03 + M-06 paired observations
- Method: Pearson correlation + bootstrap CI
- Output: `breakdown_detected: bool`, `r: float`

### D-03: Threshold Compression
- Input: M-01 values with auto-thresholds
- Method: Excess mass test + dip test
- Output: `threshold_compressed: bool`, `compression_index: float`
- **Known Issue**: None values in input cause `NoneType` comparison error (fixed in adapter)

## Scoring

### Integrity Score
- Formula: `IS = w1*D-01 + w2*D-02 + w3*D-03` (weights configurable)
- Range: 0.0 (no integrity) to 1.0 (full integrity)
- Default weights: D-01=0.33, D-02=0.33, D-03=0.33

### Confidence Score
- Factors: sample_size, variance, missing_data, window_balance, detector_success
- Range: 0.0 (no confidence) to 1.0 (full confidence)
- Limiting factor: β₃ (data completeness) often dominant

## Limitations

1. **M-05 requires GitHub remote**: Repos without GitHub remotes get no M-05 data
2. **M-04 proxy quality**: Git file analysis is an approximation, not real coverage
3. **Window density**: Sparse observations reduce confidence score
4. **Aggregate metrics**: M-01, M-04, M-07 produce only 1 observation per analysis
5. **Rate limits**: Large repos may hit GitHub API rate limits (5000/hour authenticated)

## Future Enhancements

- Coverage report parsers for more formats (Jaeger, Istanbul, etc.)
- GitLab/Bitbucket PR support
- Branch-level M-07 observations
- Real-time streaming analysis
