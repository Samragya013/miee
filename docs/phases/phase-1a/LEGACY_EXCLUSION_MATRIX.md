# Legacy Exclusion Matrix — PR-1A

**Date:** 2026-06-29
**Scope:** Classification of non-production content

---

## Directory Exclusion Summary

| Directory | Classification | Action | Reason |
|---|---|---|---|
| `archive/` | Archive | Excluded | Historical outputs, debug artifacts — 130+ files of experimental results, test repos, and CI debugging logs. All gitignored. |
| `scripts/` | Developer Utilities | Excluded | 16 legacy utility scripts (debug_git.py, error_contracts_test.py, etc.). One-off development tools not part of the production pipeline. |
| `output/` | Generated Artifacts | Excluded | Runtime output directory — gitignored. |
| `tmp_output/` | Temporary | Excluded | Temporary output — gitignored. |
| `tmp_output_ingestion/` | Temporary | Excluded | Temporary output — gitignored. |
| `tmp_output_ingestion2/` | Temporary | Excluded | Temporary output — gitignored. |
| `.claude/` | Temporary | Excluded | AI agent session config — gitignored. |
| `.mypy_cache/` | Generated Artifact | Excluded | mypy cache — gitignored. |
| `.pytest_cache/` | Generated Artifact | Excluded | pytest cache — gitignored. |

---

## Scripts Classification

| Script | Classification | Action | Reason |
|---|---|---|---|
| `analyze_tests.py` | Developer Utility | Excluded | Test analysis helper — not production |
| `continue_day15.sh` | Developer Utility | Excluded | Shell script for development workflow |
| `debug_git.py` | Developer Utility | Excluded | Debugging tool — not production |
| `debug_init.py` | Developer Utility | Excluded | Debugging tool — not production |
| `error_contracts_test.py` | Developer Utility | Excluded | One-off error testing — not production |
| `error_contracts_test2.py` | Developer Utility | Excluded | One-off error testing — not production |
| `generate_all.py` | Developer Utility | Excluded | Generation helper — not production |
| `reproducibility_test.py` | Developer Utility | Excluded | Manual reproducibility check — not production |
| `reproducibility_test_reporting.py` | Developer Utility | Excluded | Manual reproducibility check — not production |
| `reproducibility_test_segmentation_scoring.py` | Developer Utility | Excluded | Manual reproducibility check — not production |
| `run_validation_tests` | Developer Utility | Excluded | Manual validation runner — not production |
| `test_analysis_pipeline.py` | Developer Utility | Excluded | Manual pipeline test — not production |
| `test_error.py` | Developer Utility | Excluded | Error testing — not production |
| `test_first_part.py` | Developer Utility | Excluded | Manual test — not production |
| `test_first_part_2.py` | Developer Utility | Excluded | Manual test — not production |
| `test_gen.py` | Developer Utility | Excluded | Generation test — not production |

---

## Rationale

All excluded content falls into one of these categories:

1. **Generated Artifacts** — Created by tooling or CLI execution, not source code
2. **Historical Outputs** — Past experiment results preserved for reference
3. **Developer Utilities** — One-off scripts for debugging, testing, or development workflow
4. **Temporary Files** — Runtime artifacts that should not persist in version control

None of this content affects the production pipeline, test suite, or quality gates.
