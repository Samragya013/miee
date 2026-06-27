# Release Engineering — Phase 2: File Classification Report

**Program**: MIIE v1.0 Release Engineering Program
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Class | Description | Files | Action |
|---|---|---|---|
| A | Production Source | 70 | KEEP |
| B | Permanent Documentation | 366 | KEEP |
| C | Scientific Assets | 3,962 | KEEP |
| D | Release Assets | 27 | KEEP |
| E | Example Assets | 0 | — |
| F | Runtime Outputs | 7 | REMOVE_FROM_GIT |
| G | Python Cache | 0 | REMOVE_FROM_GIT |
| H | Build Artifacts | 0 | REMOVE_FROM_GIT |
| I | Temporary Research | 153 | ARCHIVE |
| J | Unknown | 0 | — |

---

## Class A — Production Source (KEEP)

| Path | Files | Status |
|---|---|---|
| src/miie/ | 70 | KEEP |

All source files are production code. No changes required.

---

## Class B — Permanent Documentation (KEEP)

| Path | Files | Status |
|---|---|---|
| docs/authorities/ | 13 | KEEP |
| docs/architecture/ | — | KEEP |
| docs/governance/ | 39 | KEEP |
| docs/reports/ | 100+ | KEEP |
| docs/adr/ | — | KEEP |
| docs/audits/ | — | KEEP |
| docs/contracts/ | — | KEEP |
| docs/execution/ | — | KEEP |
| README.md | 1 | KEEP |
| CONTRIBUTING.md | 1 | KEEP |
| CODE_OF_CONDUCT.md | 1 | KEEP |
| SECURITY.md | 1 | KEEP |
| LICENSE | 1 | KEEP |

---

## Class C — Scientific Assets (KEEP)

| Path | Files | Status |
|---|---|---|
| benchmarks/ | 3,962 | KEEP |
| docs/paper/ | — | KEEP |
| docs/research/ | — | KEEP |

Benchmark ground truth and research materials are scientific assets. Must be preserved.

---

## Class D — Release Assets (KEEP)

| Path | Files | Status |
|---|---|---|
| docs/governance/release/ | 27 | KEEP |
| docs/governance/first_user_certification/ | 12 | KEEP |

Release certification and FUC reports are release assets.

---

## Class F — Runtime Outputs (REMOVE_FROM_GIT)

| Path | Files | Status |
|---|---|---|
| output/ | 3 | REMOVE_FROM_GIT |
| tmp_output/ | 2 | REMOVE_FROM_GIT |
| tmp_output_ingestion/ | 2 | REMOVE_FROM_GIT |
| tmp_output_ingestion2/ | 2 | REMOVE_FROM_GIT |
| .pytest_cache/ | 5 | REMOVE_FROM_GIT |

**Total**: 14 files

---

## Class I — Temporary Research (ARCHIVE)

| Path | Files | Status |
|---|---|---|
| archive/ | 153 | ARCHIVE |

Historical outputs and temporary research materials. Already in archive directory.

---

## Verdict

**CLASSIFICATION: COMPLETE**

All files classified. 14 runtime outputs identified for removal from Git.

---

*Classification completed 2026-06-26*
