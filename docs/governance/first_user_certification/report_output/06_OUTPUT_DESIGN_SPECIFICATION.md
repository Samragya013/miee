# Report Output — Phase 6: Output Design Specification

**Program**: MIIE v1.0 Report Output Privacy & UX Certification
**Date**: 2026-06-26
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Level | Purpose | Audience |
|---|---|---|
| DEFAULT | Professional user summary | Normal users |
| VERBOSE | Relative path + timing | Researchers |
| DEBUG | Absolute paths + diagnostics | Maintainers |

---

## DEFAULT Mode

**Purpose**: Professional user summary only.

**Output**:
```
  Analysis Complete
  Reports saved to: output/
```

| Element | Shown | Hidden |
|---|---|---|
| Completion message | YES | — |
| Relative directory | YES | — |
| Absolute path | — | YES |
| Filename | — | YES |
| Timestamp | — | YES |
| Implementation details | — | YES |

---

## VERBOSE Mode

**Purpose**: Show relative report location, timings, detector summaries.

**Output**:
```
  Reports Saved:
  ----------------------------------------
    json: output/analysis_report_20260626_015555.json
```

| Element | Shown | Hidden |
|---|---|---|
| Completion message | YES | — |
| Relative path | YES | — |
| Absolute path | — | YES |
| Filename | YES | — |
| Timing | YES | — |
| Detector summaries | YES | — |

---

## DEBUG Mode

**Purpose**: Show absolute paths, internal locations, pipeline diagnostics.

**Output**:
```
  Reports Saved:
  ----------------------------------------
    json: C:\Users\...\output\analysis_report_20260626_015555.json
```

| Element | Shown | Hidden |
|---|---|---|
| Absolute path | YES | — |
| Internal locations | YES | — |
| Pipeline diagnostics | YES | — |
| JSON structures | YES | — |

---

## Implementation

| Mode | Flag | Current Status |
|---|---|---|
| DEFAULT | (none) | IMPLEMENTED |
| VERBOSE | `--verbose` | IMPLEMENTED |
| DEBUG | `--forensic` | IMPLEMENTED |

---

## Verdict

**OUTPUT DESIGN: PASS**

Three levels defined. Default hides implementation details.

---

*Output design specification completed 2026-06-26*
