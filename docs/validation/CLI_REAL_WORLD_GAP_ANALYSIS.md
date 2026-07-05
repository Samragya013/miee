# CLI_REAL_WORLD_GAP_ANALYSIS.md

## Phase 1 — Forensic Verification

### A. Does `python -m miie analyze https://github.com/pallets/flask.git` work?

**RESULT: PASS (after remediation)**

### B. Gaps Found (Before Remediation)

| # | Gap | Severity | Status |
|---|-----|----------|--------|
| 1 | `--format both` not in validator valid set | BLOCKER | FIXED — CLI aligned to `json/md/csv` |
| 2 | `--format markdown` vs validator `md` mismatch | BLOCKER | FIXED — CLI uses `md` |
| 3 | Windows `cp1252` encoding crash on git subprocess | BLOCKER | FIXED — `encoding='utf-8'` added |
| 4 | `shallow_depth=None` TypeError in GitCloner | BLOCKER | FIXED — `None` guard added |
| 5 | Terminal output minimal (no repo info, detectors, scores) | HIGH | FIXED — Rich summary renderer added |
| 6 | `.env` not git-ignored | HIGH | FIXED — `.gitignore` updated |
| 7 | No `--auth-token` CLI option | MEDIUM | FIXED — Added to analyze/detect/ingest |
| 8 | No `GITHUB_TOKEN` env var fallback | MEDIUM | FIXED — dotenv + os.environ |
| 9 | No unit tests for GitURLParser/GitCloner | MEDIUM | FIXED — 37 tests added |

### C. Missing Modules / Contracts / Schemas

| Component | Status |
|-----------|--------|
| `src/miie/utils/git.py` | CREATED — GitURLParser + GitCloner |
| GitHub URL detection | IMPLEMENTED in `validate_repository`, `ingest`, CLI |
| Temp clone workflow | IMPLEMENTED via GitCloner with atexit cleanup |
| Repository URL ingestion adapter | IMPLEMENTED in `RepositoryIngestionEngine.ingest()` |
| Terminal summary renderer | IMPLEMENTED in CLI `analyze` command |

### Files Modified

| File | Change |
|------|--------|
| `src/miie/utils/git.py` | NEW — URL parser + cloner |
| `src/miie/cli.py` | `--auth-token`, `--format` fix, rich output, dotenv |
| `src/miie/processing/ingestion.py` | `auth_token` param, UTF-8 encoding |
| `src/miie/processing/extraction.py` | UTF-8 encoding |
| `src/miie/contracts/validators.py` | URL validation in `validate_cli_analyze_inputs` |
| `.gitignore` | `.env` block |
| `.env` | NEW — `GITHUB_TOKEN` (git-ignored) |
| `tests/unit/test_git.py` | NEW — 37 tests |
