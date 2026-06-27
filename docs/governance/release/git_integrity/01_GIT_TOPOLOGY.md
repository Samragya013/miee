# GRIMC Phase 1 — Git Topology

**Program**: MIIE v1.0 Git Repository Integrity & Metadata Certification
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Category | Count |
|---|---|
| Primary Repository | 1 |
| Nested Repositories | 14 |
| Orphaned Submodule References | 16 |
| Submodules | 0 |
| Gitmodules | 0 |
| Worktrees | 0 |

---

## Git Topology Map

```
MIEE/ (PRIMARY)
├── .git/
├── archive/
│   ├── cli_test_repo/.git/          (nested)
│   ├── debug_test/.git/             (nested)
│   └── ... (other directories)
├── benchmarks/
│   └── datasets/
│       └── candidates/
│           ├── candidate_001/.git/  (nested)
│           ├── candidate_002/.git/  (nested)
│           ├── candidate_003/.git/  (nested)
│           ├── candidate_004/.git/  (nested)
│           ├── candidate_005/.git/  (nested)
│           ├── candidate_006/.git/  (nested)
│           ├── candidate_007/.git/  (nested)
│           ├── candidate_008/.git/  (nested)
│           ├── candidate_009/.git/  (nested)
│           ├── candidate_010/.git/  (nested)
│           └── candidate_011/.git/  (nested)
└── ... (other directories)
```

---

## Orphaned Submodule References

| Path | Mode | Commit |
|---|---|---|
| archive/debug_test | 160000 | 679b438f |
| archive/test_output_multiple/candidate_001 | 160000 | f5afa440 |
| archive/test_output_single/candidate_001 | 160000 | c40f04d0 |
| benchmarks/datasets/candidates/candidate_001 | 160000 | cf06dfd8 |
| benchmarks/datasets/candidates/candidate_002 | 160000 | cb0f5a96 |
| benchmarks/datasets/candidates/candidate_003 | 160000 | f7550a10 |
| benchmarks/datasets/candidates/candidate_004 | 160000 | 97240a5d |
| benchmarks/datasets/candidates/candidate_005 | 160000 | 764fd9be |
| benchmarks/datasets/candidates/candidate_006 | 160000 | 92630856 |
| benchmarks/datasets/candidates/candidate_007 | 160000 | db592d5a |
| benchmarks/datasets/candidates/candidate_008 | 160000 | cf13b652 |
| benchmarks/datasets/candidates/candidate_009 | 160000 | 4c918819 |
| benchmarks/datasets/candidates/candidate_010 | 160000 | 731bcc3b |
| benchmarks/datasets/candidates/candidate_011 | 160000 | b59eac09 |
| benchmarks/tmp/metric-drift/candidate_001 | 160000 | cf06dfd8 |
| benchmarks/tmp/metric-drift/candidate_002 | 160000 | cb0f5a96 |
| benchmarks/tmp/metric-drift/candidate_003 | 160000 | f7550a10 |
| benchmarks/tmp/metric-drift/candidate_004 | 160000 | 97240a5d |
| benchmarks/tmp/metric-drift/candidate_005 | 160000 | 764fd9be |
| benchmarks/tmp/metric-drift/candidate_006 | 160000 | 92630856 |
| benchmarks/tmp/metric-drift/candidate_007 | 160000 | db592d5a |
| benchmarks/tmp/metric-drift/candidate_008 | 160000 | cf13b652 |
| benchmarks/tmp/metric-drift/candidate_009 | 160000 | 4c918819 |
| benchmarks/tmp/metric-drift/candidate_010 | 160000 | 731bcc3b |
| benchmarks/tmp/metric-drift/candidate_011 | 160000 | b59eac09 |

---

## Verdict

**GIT TOPOLOGY: COMPLETE**

1 primary repository, 14 nested repositories, 16 orphaned submodule references.

---

*Git topology completed 2026-06-26*
