# Benchmark Metric Availability Matrix - Day 7

## Objective
Define candidate metric availability matrix for benchmark repositories to understand which MIIE v1.0 metrics can be extracted from different types of software projects.

## Matrix Overview

This matrix defines expected metric availability for different repository types and configurations, informing benchmark candidate selection and interpretation of extraction results.

## Metric Availability by Repository Type

| Metric ID | Metric Name | Available From | Typical Availability | Notes |
|-----------|-------------|----------------|----------------------|-------|
| **M-01** | Code Coverage | Coverage artifacts (cobertura.xml, jacoco.xml, lcov.info, etc.) | Rare | Requires build/test execution with coverage collection |
| **M-02** | Commit Frequency | Git history | **Always** | Extractable from any Git repository |
| **M-03** | Review Participation | Pull request/merge request comments, review systems | Variable | Requires platform API access (GitHub, GitLab, etc.) |
| **M-04** | Review Latency | Pull request/merge request timestamps | Variable | Requires platform API access |
| **M-05** | Issue Resolution Time | Issue tracking systems (Jira, Bugzilla, etc.) | Rare | Requires external tool integration |
| **M-06** | Code Churn | Git history | **Always** | Extractable from any Git repository |
| **M-07** | Cyclomatic Complexity | Source code analysis (linters, AST parsers) | Variable | Requires static analysis tools |

## Availability Classification

### ✅ Always Available (Git-Based)
- **M-02 (Commit Frequency)**: Available from any Git repository via `git rev-list`
- **M-06 (Code Churn)**: Available from any Git repository via `git log --numstat`

### ⚠️ Variable Availability (Artifact/Platform Dependent)
- **M-01 (Code Coverage)**: Requires coverage collection during test execution
- **M-03 (Review Participation)**: Requires access to review/comment systems
- **M-04 (Review Latency)**: Requires access to review timestamp data
- **M-05 (Issue Resolution Time)**: Requires integration with issue tracking systems
- **M-07 (Cyclomatic Complexity)**: Requires static analysis tool execution

### ❌ Never Available (Not Implemented in V1)
*(All MIIE v1.0 metrics M-01 through M-07 are registered in the frozen registry)*

## Benchmark Candidate Selection Guidelines

For the 30 synthetic benchmark candidates, repositories should be classified by:

### Type A: Git-Only Repositories
- Contain meaningful commit history and file changes
- Enable extraction of M-02 and M-06
- Represent baseline for metric extraction validation
- **Expected Count**: 10-15 candidates

### Type B: Git + Coverage Repositories
- Include coverage artifacts alongside Git history
- Enable extraction of M-01, M-02, M-06
- **Expected Count**: 5-8 candidates

### Type C: Git + Platform Integration Repositories
- Include synthetic platform data (PRs, issues, etc.)
- Enable extraction of M-02, M-03, M-04, M-05, M-06
- **Expected Count**: 5-8 candidates

### Type D: Full Artifact Repositories
- Include coverage, platform data, and analysis tool outputs
- Enable extraction of all metrics when tools are available
- **Expected Count**: 2-5 candidates

## Interpretation Framework

When evaluating benchmark results:

1. **Availability Hierarchy**: Git-based metrics (M-02, M-06) form the foundation
2. **Artifact Dependence**: Other metrics require additional repository assets
3. **Missing Data Policy**: Unavailable metrics return `None`, not zero or estimated values
4. **Comparative Analysis**: Comparisons should account for availability differences
5. **Trend Analysis**: Longitudinal studies should track availability changes over time

## Connection to Extraction Implementation

This matrix informs:
- **Test Design**: Unit and integration tests verify availability-based extraction
- **Missing Data Policy**: Confirms unavailable metrics return `None`
- **Benchmark Expectations**: Sets realistic expectations for metric extraction scores
- **Research Guidance**: Identifies gaps requiring external tool integration for full metric coverage

## Maintenance
This matrix should be reviewed and updated as:
- New extraction capabilities are implemented
- Benchmark candidate generation processes evolve
- External validity studies inform availability patterns