# PR-7B Sampling Framework Validation Campaign
**Date:** 2026-07-02 20:07
**Repos Analyzed:** 25/28 (3 failed)

## Executive Summary

The sampling framework was validated across **25 real-world repositories** spanning 6 categories.
Every repository produced a deterministic strategy choice and structured readiness analysis.

---

## Strategy Distribution

| Strategy | Count |
|----------|-------|
| commit_count | 22 |
| temporal | 2 |
| hybrid | 1 |

## Confidence Distribution

| Confidence | Count |
|------------|-------|
| high | 12 |
| low | 9 |
| medium | 4 |

## Overall Readiness State

| State | Count |
|-------|-------|
| PARTIAL | 19 |
| READY | 6 |

## Detector Readiness by Detector

### D-01

| State | Count |
|-------|-------|
| READY | 11 |
| SKIPPED | 14 |

### D-02

| State | Count |
|-------|-------|
| READY | 11 |
| SKIPPED | 14 |

### D-03

| State | Count |
|-------|-------|
| PARTIAL | 2 |
| READY | 6 |
| SKIPPED | 17 |


## Category Breakdown

| Category | Repos | OK | Strategies | Confidence |
|----------|-------|----|-----------:|-----------:|
| A | 4 | 3 | commit_count:3 | high:1, low:2 |
| B | 5 | 5 | commit_count:5 | low:4, medium:1 |
| C | 5 | 5 | commit_count:5 | high:5 |
| D | 5 | 4 | commit_count:4 | high:2, low:1, medium:1 |
| E | 5 | 5 | commit_count:2, hybrid:1, temporal:2 | high:1, low:2, medium:2 |
| F | 4 | 3 | commit_count:3 | high:3 |

---

## Per-Repository Detail

| ID | Repo | Strategy | Window | Score | Confidence | D-01 | D-02 | D-03 | Overall |
|----|------|----------|--------|-------|------------|------|------|------|---------|
| A-02 | git | commit_count | 20 | 0.98 | high | SKIPPED | SKIPPED | SKIPPED | PARTIAL |
| A-03 | cpython | commit_count | 10 | 0.27 | low | SKIPPED | SKIPPED | SKIPPED | PARTIAL |
| A-04 | rust |  |  | - |  |  |  |  |  |
| A-05 | go | commit_count | 10 | 0.34 | low | SKIPPED | SKIPPED | SKIPPED | PARTIAL |
| B-01 | transformers | commit_count | 10 | 0.3 | low | SKIPPED | SKIPPED | SKIPPED | PARTIAL |
| B-02 | langchain | commit_count | 10 | 0.3 | low | SKIPPED | SKIPPED | SKIPPED | PARTIAL |
| B-03 | ollama | commit_count | 10 | 0.63 | medium | SKIPPED | SKIPPED | SKIPPED | PARTIAL |
| B-04 | next.js | commit_count | 10 | 0.3 | low | SKIPPED | SKIPPED | SKIPPED | PARTIAL |
| B-05 | deno | commit_count | 10 | 0.3 | low | SKIPPED | SKIPPED | SKIPPED | PARTIAL |
| C-01 | gym | commit_count | 20 | 0.97 | high | READY | READY | PARTIAL | PARTIAL |
| C-02 | ParlAI | commit_count | 20 | 0.97 | high | READY | READY | READY | READY |
| C-03 | yapf | commit_count | 20 | 0.97 | high | READY | READY | PARTIAL | PARTIAL |
| C-04 | openoffice | commit_count | 20 | 0.95 | high | READY | READY | READY | READY |
| C-05 | annotations | commit_count | 20 | 0.98 | high | READY | READY | SKIPPED | PARTIAL |
| D-01 | core |  |  | - |  |  |  |  |  |
| D-02 | OpenSearch | commit_count | 10 | 0.34 | low | SKIPPED | SKIPPED | SKIPPED | PARTIAL |
| D-03 | server | commit_count | 20 | 0.98 | high | READY | READY | SKIPPED | PARTIAL |
| D-04 | server | commit_count | 20 | 0.98 | high | READY | READY | SKIPPED | PARTIAL |
| D-05 | opentofu | commit_count | 10 | 0.65 | medium | SKIPPED | SKIPPED | SKIPPED | PARTIAL |
| E-01 | autogen | commit_count | 20 | 0.96 | high | READY | READY | READY | READY |
| E-02 | ComfyUI | temporal | 14 | 0.36 | low | SKIPPED | SKIPPED | SKIPPED | PARTIAL |
| E-03 | llama_index | hybrid | 30 | 0.75 | medium | SKIPPED | SKIPPED | SKIPPED | PARTIAL |
| E-04 | semantic-kernel | commit_count | 20 | 0.87 | medium | READY | READY | READY | READY |
| E-05 | crewAI | temporal | 14 | 0.28 | low | SKIPPED | SKIPPED | SKIPPED | PARTIAL |
| F-01 | stable-diffusion-webui | commit_count | 20 | 0.96 | high | READY | READY | READY | READY |
| F-02 | NiceHashQuickMiner | commit_count | 20 | 0.98 | high | SKIPPED | SKIPPED | SKIPPED | PARTIAL |
| F-04 | core |  |  | - |  |  |  |  |  |
| F-05 | public-apis | commit_count | 20 | 0.97 | high | READY | READY | READY | READY |

---

## Scientific Assessment

### Determinism
All strategy selections are deterministic (seed=42). Same repo always produces same strategy.

### Readiness Accuracy
Readiness states are computed from actual window counts and observation counts.
Skip reasons cite exact thresholds (e.g., 'Need 10 obs/window, got 5').

### Fallback Behavior
When primary strategy produces insufficient observations, the adaptive window builder
automatically falls back to larger windows or commit-based slicing.

### Key Findings

- **14 repos** have all detectors SKIPPED (insufficient observations)
- **11 repos** have at least one detector READY

---

## Certification Recommendation

Based on the validation results:

**REQUIRES REMEDIATION** -- Significant failures detected.
