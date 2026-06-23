# FERA Phase 9 — Reproducibility Audit

**Audit ID:** FERA-P9-REPRO  
**Date:** 2026-06-23  
**Auditor:** Independent Audit Authority  
**Scope:** Evidence engine determinism, CLI absence, byte-identical reproducibility criterion, timestamp contamination  

---

## 1. Evidence Engine Non-Determinism

### Evidence
`src/miie/processing/evidence.py`:

| Line | Code | Violation |
|------|------|-----------|
| 42 | `evidence_id = f"EV-{int(now.timestamp())}-{hash(...)}"` | Embeds `now.timestamp()` in evidence ID — changes every run |
| 50 | `das_notation = f"DAS-{int(now.timestamp())}-..."` | Embeds `now.timestamp()` in DAS notation — changes every run |
| 66 | `Provenance.timestamp = now` | Uses current time as provenance timestamp |

**Impact:** Evidence IDs and DAS notations are **non-deterministic** — the same inputs produce different evidence packages on each run. This violates:
- Day 9 requirement: "Byte-identical output for same input"
- Day 10 requirement: "No timestamps in evidence IDs"

### Verdict
**FAIL** — Evidence engine violates determinism requirement. Every run produces unique evidence IDs.

---

## 2. CLI Absence

### Evidence
`src/miie/cli.py` is a 14-line stub:

```python
import click

@click.group()
def cli():
    """MIIE - Measurement Integrity Intelligence Engine"""
    pass

@cli.command()
@click.version_option(version="0.1.0")
def version():
    """Show version."""
    click.echo("MIIE v0.1.0")

if __name__ == "__main__":
    cli()
```

**Missing commands:** `analyze`, `--dry-run`, `validate`, `report`  
**Day 10 requirement:** CLI with `--dry-run` mode for end-to-end pipeline validation

### Verdict
**NOT IMPLEMENTED** — CLI is a stub. No `analyze` command exists. Day 10 dry-run requirement unmet.

---

## 3. Byte-Identical Reproducibility

### Evidence
- **Requirement (Day 9/10):** Running the same pipeline on the same input must produce byte-identical output
- **Current state:** Evidence engine embeds `int(now.timestamp())` in IDs (line 42, 50), making output non-deterministic
- **Test:** `tests/benchmarks/reproducibility_test.py` — 4 failures, confirming reproducibility is not achieved
- **Autoresearch:** No iterations logged any reproducibility metric; all iterations crashed or returned 0.0

### Verdict
**FAIL** — Byte-identical reproducibility is not achievable with timestamp-contaminated evidence IDs.

---

## 4. Random Seed Control

### Evidence
- `src/miie/processing/segmentation.py` does not use explicit random seeds
- `src/miie/processing/detection/` detectors do not seed random generators
- No `random.seed()` or `numpy.random.seed()` calls found in production code
- Benchmark candidates use deterministic seeds (`seed: 1001`, `seed: 1002`, etc.) in manifest — this is correct

### Verdict
**PARTIAL** — Benchmark candidates have seeds, but production code does not enforce seed control for any stochastic operations.

---

## 5. Reproducibility Test Results

| Test | Status | Notes |
|------|--------|-------|
| `tests/benchmarks/reproducibility_test.py` (4 tests) | **FAIL** | Evidence ID non-determinism |
| `tests/integration/test_reproducibility.py` | **COLLECTION ERROR** | `MockIngestionEngine` removed |
| Autoresearch iterations | **0% success** | All crashed or returned 0.0 |

---

## Summary

| Check | Status | Severity |
|-------|--------|----------|
| Evidence engine determinism | **FAIL** | CRITICAL |
| CLI `--dry-run` | **NOT IMPLEMENTED** | HIGH |
| Byte-identical output | **FAIL** | HIGH |
| Random seed control | **PARTIAL** | MEDIUM |
| Reproducibility tests | **FAIL** | HIGH |

**Overall Reproducibility Audit: FAIL** — Timestamp contamination in evidence IDs, no CLI, byte-identical criterion unmet.
