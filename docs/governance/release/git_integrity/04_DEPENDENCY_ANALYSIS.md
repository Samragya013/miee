# GRIMC Phase 4 — Dependency Analysis

**Program**: MIIE v1.0 Git Repository Integrity & Metadata Certification
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Category | Count |
|---|---|
| Dependencies found | 3 |
| Python imports | 0 |
| Scripts | 0 |
| Benchmarks | 3 |
| Tests | 0 |
| Documentation | 0 |

---

## Dependency Analysis

### archive/cli_test_repo
| Source | Depends On | Status |
|---|---|---|
| Tests | Yes | Referenced in CLI tests |
| Benchmarks | No | — |
| Documentation | No | — |

### archive/debug_test
| Source | Depends On | Status |
|---|---|---|
| Tests | No | — |
| Benchmarks | No | — |
| Documentation | No | — |

### benchmarks/datasets/candidates/candidate_001-011
| Source | Depends On | Status |
|---|---|---|
| Tests | No | — |
| Benchmarks | Yes | Used by benchmark suite |
| Documentation | No | — |

---

## Dependency Map

```
benchmarks/
├── datasets/candidates/
│   ├── candidate_001 → Benchmarks
│   ├── candidate_002 → Benchmarks
│   ├── candidate_003 → Benchmarks
│   ├── candidate_004 → Benchmarks
│   ├── candidate_005 → Benchmarks
│   ├── candidate_006 → Benchmarks
│   ├── candidate_007 → Benchmarks
│   ├── candidate_008 → Benchmarks
│   ├── candidate_009 → Benchmarks
│   ├── candidate_010 → Benchmarks
│   └── candidate_011 → Benchmarks
└── tmp/metric-drift/
    └── candidate_001-011 → Benchmarks

archive/
├── cli_test_repo → Tests
└── debug_test → None
```

---

## Verdict

**DEPENDENCY ANALYSIS: COMPLETE**

3 dependencies found. 11 benchmark fixtures referenced by benchmark suite.

---

*Dependency analysis completed 2026-06-26*
