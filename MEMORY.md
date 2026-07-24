# MEMORY.md -- Agent Working Memory

## Repository State

- **Version**: 1.6.0
- **Package**: `miie` (src layout: `src/miie/`)
- **Tests**: 2775 passing (pytest), 2 pre-existing failures (architecture), 6 skipped
- **Python**: 3.10-3.12
- **Platform**: **Windows-only** (no Linux/macOS CI, no cross-platform guarantees)
- **License**: MIT

## Current Status: Scientific Remediation COMPLETE — All 6 Fixes Applied

End-to-end limitations investigation completed. 5 critical, 8 high, 7 medium issues identified. Immediate fixes applied: git timeout, disk cleanup, bare except cleanup, CLI knobs, network retry, token validation, API auth. War-room fixes applied: confidence band surfaced first, `--fail-on-low-confidence` flag, data quality section, evidence compression, monorepo hint. Unicode encoding fix (cp1252) applied. Platform locked to Windows-only. Scientific remediation: 6 audit findings resolved (severity extraction, KS p-value, Holm-Bonferroni, D-02 max correlation, effect sizes, vectorized Cliff's delta). 2775 tests passing, 2 pre-existing architecture failures, 6 skipped.

## Recent Work

- **Scientific Remediation**: 6 audit findings resolved — severity extraction, KS p-value, Holm-Bonferroni, D-02 max correlation, effect sizes, vectorized Cliff's delta
- **End-to-end hardening**: Full system limitations investigation + fixes applied
- **Git timeout**: Added 60s timeout to all subprocess.run calls in git.py and ingestion.py
- **Disk cleanup**: Implemented proper shutil.rmtree cleanup in GitCloner.clone() when cleanup_after=True
- **Bare except cleanup**: Replaced 6 bare except: clauses with except Exception: across ingestion.py, git.py, cli/__init__.py, api/server.py
- **CLI knobs**: Added --max-commits (5000 default), --workers (2 default), --timeout (60s default) to analyze command
- **Network retry**: Added exponential backoff (3 attempts) for git clone failures
- **Token validation**: Early GitHub token validation on analyze startup — fails fast with clear error
- **API auth**: Added X-API-Key middleware for POST endpoints on FastAPI server
- **Empty repo guard**: Early exit with clear error when repo has 0 commits
- **War-room fixes**: Confidence band surfaced first, `--fail-on-low-confidence` flag, data quality section, evidence compression, monorepo hint — ALL COMPLETE
- **Unicode encoding fix**: `─` box-drawing character replaced with ASCII `-` in premium_tui.py and brand_header.py to prevent cp1252 crash
- **CLAUDE.md updated**: Platform locked to Windows-only, test count corrected to 2775, scientific remediation documented
- **MEMORY.md updated**: Platform decision documented, recent work captured, scientific remediation recorded
- **FTEMP-01**: Premium TUI transformation — 15 phases complete, 11 deliverable docs
- **FTEMP-01**: 8 new modules: design_tokens, brand_header, semantic_colors, responsive, navigation, scientific_dashboard, accessibility, performance
- **FTEMP-01**: Rewritten premium_tui.py using semantic_colors, design_tokens, responsive
- **FTEMP-01**: CLI now supports TUI mode (`miie` with no args), command mode (`:` or `/`), 8 shell commands
- **FTEMP-01**: 65 E2E tests (20 CLI usability + 45 E2E), all passing
- **FTEMP-01**: All 8 modules verified importable, no circular dependencies
- **Scalability Phases 1–5**: O(N) windowing 348x, parallel extraction 1.8x, memory __slots__ 2.1x, numstat bottleneck fixed
- **Observation path fix**: CLI `_run_pipeline_rich` now uses ExtractionEngine + ObservationWindowBuilder + dispatcher.invoke_observations()
- **Report encoding fix**: Added `encoding="utf-8"` to tempfile.NamedTemporaryFile in reporting/engine.py
- **Detector triggers verified**: D-01 correctly detects drift when given per-commit observation data
- **All 7 metrics functional**: M-01 through M-07 verified on 6 repos, confidence 1.0/1.0
- **Full test suite**: 2775 passed, 6 skipped, 2 pre-existing failures
- **OIAP-01**: Output Intelligence Audit — 14 reports, 39 gaps, ~52% intelligence hidden
- **PGP-01**: Platform governance — 8 extension points, 5 API surfaces, 8 lifecycle phases
- **RPP-01**: Scientific artifact evaluation — CITATION.cff created, OpenAPI exported
- **IVP-01**: Industrial validation — 12 repos, 4 languages, CONDITIONALLY CERTIFIED up to ~16K commits

## Frozen Core (DO NOT MODIFY)

- Metrics: M-01 through M-07 (`src/miie/metrics/`)
- Detectors: D-01, D-02, D-03 (`src/miie/processing/detection/`)
- Evidence: EvidencePackage (`src/miie/processing/evidence.py`)
- Confidence/Integrity: `src/miie/schemas/models.py`
- Statistics: `src/miie/processing/detection/statistics.py`
- WorkflowEngine: `src/miie/application/workflow.py`
- SessionManager: `src/miie/application/session.py`
- ApplicationService: `src/miie/application/service.py`
- All contracts: `src/miie/contracts/interfaces.py`

## Repository Structure

```
src/miie/
├── api/                    # FastAPI REST (6 frozen endpoints)
├── application/            # Interactive layer, workflow, session
├── benchmark/              # Benchmark execution engine
├── cli/                    # Click CLI (16 commands + TUI)
├── config/                 # Configuration loader
├── contracts/              # Interfaces (frozen)
├── experimental/           # Non-production code
├── metrics/                # M-01 through M-07
├── observation_graph/      # Observation graph data structures
├── orchestration/          # Workflow orchestration
├── processing/             # Core scientific processing
│   ├── detection/          # D-01, D-02, D-03 + statistics
│   ├── evidence.py         # EvidencePackage
│   ├── evaluation/         # Evaluation engine
│   ├── explanation/        # Explanation engine
│   ├── extraction/         # Data extraction
│   ├── observation/        # Observation processing
│   ├── reporting/          # Report generation (14+ types)
│   └── scoring/            # Integrity + Confidence scoring
├── providers/              # External data providers
├── reporting/              # Legacy reporting (templates)
├── sampling/               # Sampling strategies
├── schemas/                # Data models (frozen)
├── scientific/             # Scientific validation
├── storage/                # Storage interfaces
├── utils/                  # Utilities
├── validation/             # Validation framework
└── workspace/              # Persistent workspace (ECP-03)
```

## Key Commands

- `pytest` -- Run all tests
- `black --line-length 120 .` -- Format
- `isort --profile black .` -- Sort imports
- `flake8 .` -- Lint
- `mypy src/miie/` -- Type check
- `make lint` -- Run all linters
- `make test` -- Run tests with coverage

## Directory Purposes

| Directory | Purpose |
|-----------|---------|
| `docs/` | 200+ documentation files (specs, guides, API docs) |
| `docs/specifications/` | Numbered scientific/engineering specifications |
| `tests/` | Test suite (2756 tests) |
| `tests/architecture/` | Layer dependency, package structure tests |
| `benchmarks/` | Benchmark results + cloned repos |
| `reports/` | Generated analysis reports (FFP-01 through SXP-01) |
| `archive/` | Historical code and outputs |
| `schemas/` | YAML/JSON schema definitions |
| `scripts/` | Development scripts (gitignored) |

## Program History

| # | Program | Status | Tests | Reports | Verdict |
|---|---------|--------|-------|---------|---------|
| 1 | RSP-01 | Complete | — | 10 | Stabilized |
| 2 | RSP-02 | Complete | 2733 | 10 | Healthy |
| 3 | FFP-01 | Complete | 2705 | 11 | FROZEN |
| 4 | SCCP-01 | Complete | 2707 | 10 | COMPLETE |
| 5 | SCCP-02 | Complete | 2733 | 10 | COMPLETE |
| 6 | RRP-01 | Complete | 2733 | 10 | RELEASE READY |
| 7 | IVP-01 | Complete | 2733 | 10 | CONDITIONALLY CERTIFIED |
| 8 | RPP-01 | Complete | 2733 | 10 | ARTIFACT COMPLETE |
| 9 | PGP-01 | Complete | 2733 | 10 | PLATFORM GOVERNANCE COMPLETE |
| 10 | OIAP-01 | Complete | 2733 | 14 | NO (audit-only) |
| 11 | SXP-01 | Complete | 2735 | 14 | CONDITIONALLY CERTIFIED |

**Total Programs**: 11 complete
**Total Reports**: 129
**Current Tests**: 2775 passing

## Development Rules

1. No modifications to frozen core
2. All interactions are deterministic
3. Evidence-first: every finding backed by statistical test
4. Statistical validity before convenience
5. Test before code
6. One module per concern
7. No secrets in code
8. Pre-commit hooks must pass
