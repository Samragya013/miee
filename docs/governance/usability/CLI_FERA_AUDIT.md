# CLI_FERA_AUDIT.md

## Phase 6 — FERA Audit

### Runtime Verification

| Check | Result |
|-------|--------|
| `python -m miie analyze https://github.com/pallets/flask.git` exits 0 | PASS |
| JSON report generated | PASS |
| MD report generated | PASS |
| Manifest generated | PASS |
| Repository cloned and cleaned up | PASS |
| All 3 detectors executed | PASS |
| Integrity score computed | PASS |
| Confidence score computed | PASS |
| Terminal summary rendered | PASS |

### Reproducibility Verification

| Check | Result |
|-------|--------|
| Same command, same output structure | PASS |
| Seed=42 deterministic | PASS |
| Manifest contains config hash | PASS |
| Provenance recorded | PASS |

### Contract Verification

| Check | Result |
|-------|--------|
| IIngestionEngine contract preserved | PASS |
| RepositoryContext schema unchanged | PASS |
| ScorePackage schema unchanged | PASS |
| Exit codes match TFS §13.7 | PASS |
| No detector modifications | PASS |
| No pipeline stage modifications | PASS |

### CLI Verification

| Check | Result |
|-------|--------|
| `--help` shows all options | PASS |
| `--auth-token` documented | PASS |
| `--format` choices match validator | PASS |
| `--dry-run` works | PASS |
| Invalid URL produces error message | PASS |
| Missing args produces error message | PASS |

### MIIE-USABILITY-01 Assessment

> "A first-time user must be able to execute a complete repository analysis using a single command."

**Evidence:**

```bash
python -m miie analyze https://github.com/pallets/flask.git
# → Complete analysis with repo summary, detectors, scores, findings, reports
```

**VERDICT: PASS**

### FERA Audit Score

| Dimension | Score |
|-----------|-------|
| Runtime | 10/10 |
| Reproducibility | 10/10 |
| Contracts | 10/10 |
| CLI | 10/10 |
| **Overall** | **40/40 — PASS** |
