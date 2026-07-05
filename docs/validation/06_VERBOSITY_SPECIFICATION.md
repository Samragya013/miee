# FUSC Phase 6 — Verbosity Specification

**Program**: MIIE v1.0 First User Security & Experience Certification
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Level | Purpose | Audience |
|---|---|---|
| DEFAULT | User-relevant information | Normal users |
| VERBOSE | Scientific reasoning | Researchers |
| DEBUG | Implementation diagnostics | Maintainers |

---

## DEFAULT Mode

**Purpose**: Only information useful to normal users.

| Element | Shown | Hidden |
|---|---|---|
| Version | YES | — |
| Repository name | YES | — |
| Commit count | YES | — |
| Contributor count | YES | — |
| Date range | YES | — |
| Window count | YES | — |
| Detector count | YES | — |
| Integrity verdict | YES | — |
| Confidence level | YES | — |
| Risk level | YES | — |
| Summary | YES | — |
| Recommended action | YES | — |
| Report paths | YES | — |
| Detector IDs | — | YES |
| Metric IDs | — | YES |
| Timing | — | YES |
| Window details | — | YES |
| Evidence packages | — | YES |
| Configuration | — | YES |
| Pipeline internals | — | YES |

---

## VERBOSE Mode

**Purpose**: Scientific reasoning, window statistics, detector summaries, confidence reasoning, timing.

| Element | Shown | Hidden |
|---|---|---|
| All DEFAULT items | YES | — |
| Detector IDs | YES | — |
| Metric IDs | YES | — |
| Timing per stage | YES | — |
| Total timing | YES | — |
| Window details | — | YES |
| Evidence packages | — | YES |
| Configuration | — | YES |
| Pipeline internals | — | YES |
| Stack traces | — | YES |

---

## DEBUG Mode

**Purpose**: Everything else — stack traces, evidence, JSON, internal objects, pipeline, diagnostics, developer information.

| Element | Shown | Hidden |
|---|---|---|
| All VERBOSE items | YES | — |
| Window details | YES | — |
| Evidence packages | YES | — |
| Configuration | YES | — |
| Pipeline internals | YES | — |
| Stack traces | YES | — |
| JSON output | YES | — |
| Internal objects | YES | — |
| Developer information | YES | — |

---

## Implementation

| Mode | Flag | Current Status |
|---|---|---|
| DEFAULT | (none) | IMPLEMENTED |
| VERBOSE | `--verbose` | IMPLEMENTED |
| DEBUG | `--forensic` | IMPLEMENTED |

---

## Verdict

**VERBOSITY SPECIFICATION: PASS**

Three levels defined and implemented. Default hides developer information.

---

*Verbosity specification completed 2026-06-26*
