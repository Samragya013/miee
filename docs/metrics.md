# MIIE — Metrics Specification

## Overview

MIIE measures 7 software engineering metrics (M-01 through M-07) extracted from Version Control System histories.

## Metric Definitions

### M-01: Specification Entropy
- **Source**: Git commit messages
- **Unit**: ratio (0.0-1.0)
- **Description**: Entropy of commit message categories across time windows
- **Extraction**: Classifies commits into categories (feature, fix, refactor, docs, test, chore), computes Shannon entropy
- **Quality**: complete (all data from git history)
- **Aggregate**: Yes (1 observation per analysis)

### M-02: Raw Commit Frequency
- **Source**: Git commits
- **Unit**: count
- **Description**: Number of commits per time window
- **Extraction**: Counts commits in each window
- **Quality**: complete
- **Aggregate**: No (per-commit observations)

### M-03: Code Churn Ratio
- **Source**: Git diffs
- **Unit**: ratio (0.0-1.0)
- **Description**: Additions vs deletions per commit
- **Extraction**: Parses `git diff --shortstat` for insertions/deletions
- **Quality**: complete
- **Aggregate**: No (per-commit observations)

### M-04: Test Coverage
- **Source**: Coverage reports or proxy
- **Unit**: percentage (0.0-1.0)
- **Description**: Test coverage percentage
- **Extraction Priority**:
  1. Cobertura XML (coverage.xml)
  2. lcov.info
  3. .coverage JSON
  4. Git ls-files proxy (test file ratio)
- **Quality**: complete (real) or estimated (proxy)
- **Aggregate**: Yes (1 observation per analysis)

### M-05: PR Review Latency
- **Source**: GitHub REST API
- **Unit**: hours
- **Description**: Time from PR creation to merge
- **Extraction**: Fetches merged PRs via paginated API, computes merge latency
- **Quality**: complete (when API available) or missing (no GitHub remote)
- **Aggregate**: No (per-PR observations)
- **Requirements**: `GITHUB_TOKEN` environment variable

### M-06: File Activity Breadth
- **Source**: Git diffs
- **Unit**: count
- **Description**: Number of unique files modified per window
- **Extraction**: Counts unique file paths in git diff output
- **Quality**: complete
- **Aggregate**: No (per-commit observations)

### M-07: Branch Activity Recency
- **Source**: Git branches
- **Unit**: ratio (0.0-1.0)
- **Description**: Ratio of recently active branches
- **Extraction**: Analyzes branch references and their recency
- **Quality**: complete
- **Aggregate**: Yes (1 observation per analysis)

## Data Sources

| Metric | Source | Provider |
|--------|--------|----------|
| M-01 | git commits | GitObservationProvider |
| M-02 | git commits | GitObservationProvider |
| M-03 | git diffs | GitObservationProvider |
| M-04 | coverage files / proxy | GitObservationProvider |
| M-05 | GitHub API | GitHubPullRequestProvider |
| M-06 | git diffs | GitObservationProvider |
| M-07 | git branches | GitObservationProvider |

## Quality Levels

- **complete**: All data available from source
- **estimated**: Approximated from available data
- **missing**: No data available for this metric

## Limitations

1. **M-05 requires GitHub remote**: Repos without GitHub remotes get no M-05 data
2. **M-04 proxy quality**: Git file analysis is an approximation, not real coverage
3. **Window density**: Sparse observations reduce confidence score
4. **Aggregate metrics**: M-01, M-04, M-07 produce only 1 observation per analysis
5. **Rate limits**: Large repos may hit GitHub API rate limits (5000/hour authenticated)
