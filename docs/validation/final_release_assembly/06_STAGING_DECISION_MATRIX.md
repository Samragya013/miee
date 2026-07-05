# FRASC Phase 6 — Staging Decision Matrix

**Program**: MIIE v1.0 Final Release Assembly & Staging Certification
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Action | Count |
|---|---|
| STAGE | 78 |
| KEEP_UNTRACKED | 97 |
| REMOVE_FROM_GIT | 0 |
| IGNORE | 0 |
| ARCHIVE | 0 |
| MANUAL_REVIEW | 0 |

---

## Staging Decisions

### STAGE (78 files)

| Category | Files | Evidence |
|---|---|---|
| Deletions (Python cache) | 21 | .pyc files removed from tracking |
| Deletions (output files) | 8 | output files removed from tracking |
| Deletions (research files) | 15 | research files moved to docs/ |
| Deletions (prompt files) | 3 | prompt files moved to docs/ |
| Deletions (demo files) | 6 | demo files removed |
| Deletions (benchmark candidates) | 11 | benchmark candidates converted to plain dirs |
| Deletions (benchmark metric-drift) | 11 | metric-drift copies removed |
| Deletions (archive files) | 3 | archive files removed |
| Documentation updates | 3 | README.md, CONTRIBUTING.md, benchmark_summary.json |
| Release governance | 56 | docs/governance/release/* |

### KEEP_UNTRACKED (97 files)

| Category | Files | Evidence |
|---|---|---|
| Archive directories | 44 | Historical data, not for release |
| Internal governance | 25 | Internal audit records |
| Benchmark tmp | 13 | Temporary outputs |
| Documentation | 9 | Research, prompts, paper |
| First user certification | 14 | User certifications |

---

## Verdict

**STAGING DECISION MATRIX: COMPLETE**

78 files staged, 97 files kept untracked. All decisions documented.

---

*Staging decision matrix completed 2026-06-26*
