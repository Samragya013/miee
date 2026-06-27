# RACA Phase 7 — Restructure Plan

**Program**: MIIE v1.0 Repository Architecture Cohesion Audit
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Action | Count |
|---|---|
| KEEP | 12 |
| MOVE | 2 |
| MERGE | 0 |
| SPLIT | 0 |
| ARCHIVE | 1 |
| MANUAL REVIEW | 0 |

---

## Proposed Changes

### MOVE: output/ → .gitignore

**Current**: `output/` in root directory
**Proposed**: Add to `.gitignore`, remove from tracking
**Reason**: Runtime outputs should not be tracked in version control
**Architectural Benefit**: Cleaner root directory, no accidental commits
**Regression Risk**: LOW
**Import Impact**: NONE
**Documentation Impact**: Update README.md
**Rollback Strategy**: Remove from .gitignore, `git checkout output/`

### MOVE: tmp_output*/ → .gitignore

**Current**: `tmp_output/`, `tmp_output_ingestion/`, `tmp_output_ingestion2/` in root
**Proposed**: Add to `.gitignore`, remove from tracking
**Reason**: Temporary outputs should not be tracked
**Architectural Benefit**: Cleaner root directory
**Regression Risk**: LOW
**Import Impact**: NONE
**Documentation Impact**: NONE
**Rollback Strategy**: Remove from .gitignore

### ARCHIVE: docs/paper/ → archive/paper/

**Current**: `docs/paper/` in documentation root
**Proposed**: Move to `archive/paper/`
**Reason**: Research paper is historical, not active documentation
**Architectural Benefit**: Cleaner documentation root
**Regression Risk**: LOW
**Import Impact**: NONE
**Documentation Impact**: Update README.md
**Rollback Strategy**: Move back to docs/paper/

---

## Verdict

**RESTRUCTURE PLAN: COMPLETE**

3 proposed changes. All low risk.

---

*Restructure plan completed 2026-06-26*
