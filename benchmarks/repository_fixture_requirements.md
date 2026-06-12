# Benchmark Repository Fixture Requirements

This document defines the requirements for fixture repositories used in benchmarking tasks as part of the Day 6 parallel research track.

## 1. Size Constraints

Fixture repositories MUST be categorized into size tiers (small, medium, large) based on the following metrics:

- **Small**:
  - Disk size: 1 - 10 MB
  - Number of files: 10 - 100
  - Lines of code (excluding blanks and comments): 100 - 1,000

- **Medium**:
  - Disk size: 10 - 100 MB
  - Number of files: 100 - 1,000
  - Lines of code: 1,000 - 10,000

- **Large**:
  - Disk size: 100 - 1,000 MB
  - Number of files: 1,000 - 10,000
  - Lines of code: 10,000 - 100,000

Note: These ranges are approximate and may be adjusted based on the specific benchmark being performed.

## 2. History Depth Requirements

- Minimum number of commits:
  - Small: 50 commits
  - Medium: 500 commits
  - Large: 5,000 commits
- The history SHOULD span a sufficient time period to test performance of deep history operations (e.g., blame, log, diff between distant commits).
- The maximum age of the oldest commit SHOULD be at least:
  - Small: 3 months
  - Medium: 1 year
  - Large: 3 years

## 3. Branch Structure

- MUST contain a primary branch (named `main` or `master`).
- SHOULD contain at least one long-lived feature branch (e.g., `develop`, `feature/*`) for testing branch operations.
- MAY contain release tags (e.g., `v1.0.0`, `v1.0.1`) to test tag-related operations.
- The repository SHOULD demonstrate a realistic branching model (e.g., GitHub Flow, Git Flow) to benchmark merge and rebase operations.

## 4. Commit Frequency Expectations

- Average commit frequency (commits per week):
  - Small: 1 - 5 commits/week
  - Medium: 5 - 20 commits/week
  - Large: 20 - 100 commits/week
- The commit history SHOULD reflect a realistic development pattern, including periods of higher and lower activity.

## 5. Contributor Diversity

- Number of distinct contributors:
  - Small: 1 - 2
  - Medium: 3 - 5
  - Large: 5+
- Commits SHOULD be distributed among contributors to simulate collaboration.
- For repositories with multiple contributors, the commit history SHOULD include merge conflicts to test conflict resolution performance.

## 6. File Type Distribution

- The repository SHOULD contain a mix of file types typical to the project's language or domain.
- Suggested distribution (by file count):
  - Source code files: 60% - 80%
  - Documentation files: 10% - 20%
  - Configuration files: 5% - 15%
  - Other (assets, binary files): 0% - 10% (note: binary files should be minimized to avoid skewing size metrics)
- For language-specific benchmarks, the file type distribution SHOULD align with the target language (e.g., for a Java benchmark, .java files should dominate).

## 7. Licensing Considerations

- MUST be licensed under an OSI-approved license that permits use, modification, and redistribution for benchmarking purposes (e.g., MIT, Apache-2.0, BSD).
- The license MUST be clearly indicated in the repository (e.g., in a LICENSE file).
- Repositories with proprietary or non-redistributable licenses MUST NOT be used as fixtures.

## 8. Other Requirements

- MUST NOT contain sensitive data, proprietary information, or copyrighted material without permission.
- MUST be self-contained: all necessary dependencies for building or running the project (if applicable) SHOULD be included or available via public package managers.
- The repository generation process (if script-generated) SHOULD be documented and reproducible to allow for fixture regeneration.
- Fixture repositories SHOULD be validated for integrity (e.g., no corruption) before use in benchmarks.

---

*These requirements are intended to ensure that benchmark results are meaningful, reproducible, and comparable across different tools and environments.*