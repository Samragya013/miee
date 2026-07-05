# MIIE v1.0 CI Workflow Inventory

**Program**: MIIE v1.0 GitHub Actions Certification
**Date**: 2026-06-27
**Mode**: READ-ONLY AUDIT

---

## Executive Summary

| Category | Count |
|---|---|
| Workflow files | 1 |
| Total jobs | 7 |
| Unique jobs | 7 |
| Matrix jobs | 3 (Python versions) |

---

## Workflow File: `.github/workflows/ci.yml`

### Trigger Configuration

| Trigger | Branches |
|---|---|
| push | main, develop |
| pull_request | main |

### Job Inventory

| Job | Runner | Python | Dependencies | Build | Test | Cache | Matrix |
|---|---|---|---|---|---|---|---|
| lint | ubuntu-latest | 3.12 | pip install black isort flake8 flake8-bugbear | N/A | black --check, isort --check-only, flake8 | None | None |
| typecheck | ubuntu-latest | 3.12 | pip install mypy types-PyYAML | N/A | mypy src/miie/ --ignore-missing-imports | None | None |
| unit-tests | ubuntu-latest | 3.10, 3.11, 3.12 | pip install poetry && poetry install | N/A | pytest tests/unit/ tests/schema/ tests/contract/ tests/architecture/ -x -q --tb=short | None | Python versions |
| integration-tests | ubuntu-latest | 3.12 | pip install poetry && poetry install | N/A | pytest tests/integration/ -x -q --tb=short | None | None |
| regression | ubuntu-latest | 3.12 | pip install poetry && poetry install | N/A | pytest tests/regression/ tests/workflow/ -x -q --tb=short | None | None |
| security | ubuntu-latest | 3.12 | pip install pip-audit safety | N/A | pip-audit --ignore-vulnerabilities \|\| true, safety check \|\| true | None | None |
| detector-regression | ubuntu-latest | 3.12 | pip install poetry && poetry install | N/A | grep -r "detector_output" src/ tests/ | None | None |

### Detailed Job Analysis

#### Job: lint

| Attribute | Value |
|---|---|
| Runner | ubuntu-latest |
| Python | 3.12 |
| Dependencies | black, isort, flake8, flake8-bugbear |
| Commands | black --check src/ tests/, isort --check-only src/ tests/, flake8 src/ tests/ |
| Cache | None |
| Matrix | None |

#### Job: typecheck

| Attribute | Value |
|---|---|
| Runner | ubuntu-latest |
| Python | 3.12 |
| Dependencies | mypy, types-PyYAML |
| Commands | mypy src/miie/ --ignore-missing-imports |
| Cache | None |
| Matrix | None |

#### Job: unit-tests

| Attribute | Value |
|---|---|
| Runner | ubuntu-latest |
| Python | 3.10, 3.11, 3.12 |
| Dependencies | poetry |
| Commands | poetry install, pytest tests/unit/ tests/schema/ tests/contract/ tests/architecture/ -x -q --tb=short |
| Cache | None |
| Matrix | Python versions |

#### Job: integration-tests

| Attribute | Value |
|---|---|
| Runner | ubuntu-latest |
| Python | 3.12 |
| Dependencies | poetry |
| Commands | poetry install, pytest tests/integration/ -x -q --tb=short |
| Cache | None |
| Matrix | None |

#### Job: regression

| Attribute | Value |
|---|---|
| Runner | ubuntu-latest |
| Python | 3.12 |
| Dependencies | poetry |
| Commands | poetry install, pytest tests/regression/ tests/workflow/ -x -q --tb=short |
| Cache | None |
| Matrix | None |

#### Job: security

| Attribute | Value |
|---|---|
| Runner | ubuntu-latest |
| Python | 3.12 |
| Dependencies | pip-audit, safety |
| Commands | pip-audit --ignore-vulnerabilities \|\| true, safety check \|\| true |
| Cache | None |
| Matrix | None |

#### Job: detector-regression

| Attribute | Value |
|---|---|
| Runner | ubuntu-latest |
| Python | 3.12 |
| Dependencies | poetry |
| Commands | poetry install, grep -r "detector_output" src/ tests/ |
| Cache | None |
| Matrix | None |

---

## Verdict

**CI WORKFLOW INVENTORY: COMPLETE**

1 workflow file, 7 jobs, 3 matrix configurations.

---

*CI workflow inventory completed 2026-06-27*
