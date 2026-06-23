# FERA Repository Inventory

## Overview
This document provides an inventory of the MIIE repository structure as part of the FERA audit Phase 2. It includes directories, files, and key components.

## Root Level
### Directories
- `.autoresearch` - Auto-research related files
- `.claude` - Claude Code settings
- `.github` - GitHub workflows (CI/CD)
- `.pytest_cache` - Pytest cache
- `benchmarks` - Benchmarking suite
- `debug_test` - Debug test project
- `docs` - Documentation
- `dry_run_output` - Dry run output files
- `memory` - Memory artifacts
- `output` - Output files
- `paper` - Paper drafts
- `prompts` - Prompt templates
- `research` - Research notes and materials
- `scripts` - Utility scripts
- `src` - Source code
- `test_output` - Test output
- `test_output_dryrun` - Dry run test output
- `tests` - Test suite
- `tmp_output` - Temporary output
- `tmp_output_ingestion` - Temporary ingestion output
- `tmp_output_ingestion2` - Second temporary ingestion output

### Files
- Configuration: `.gitignore`, `.pre-commit-config.yaml`, `pyproject.toml`, `poetry.lock`
- Documentation: `README.md`, `MEMORY.md`, `FERA_REQUIREMENT_MATRIX.md`, and various audit reports (e.g., `ARCHITECTURE_AUDIT.md`, `BACKEND_PROGRESS_AUDIT.md`, etc.)
- Scripts: `generate_all.py`, `run_validation_tests`, `debug_git.py`, `debug_init.py`, `reproducibility_test.py`, etc.
- Other: `DAY0_TO_DAY10_REQUIREMENT_MATRIX.md`, `DAY0_TO_DAY10_TRACEABILITY_MATRIX.md`, and many day-specific audit reports.

## Source Code Structure (src/)
The src directory contains the main Python package `miie` with the following modules:
- `miie/__init__.py` - Package initializer
- `miie/__main__.py` - Main entry point
- `miie/cli.py` - Command-line interface
- `miie/benchmark/` - Benchmarking components
- `miie/common/` - Common utilities
- `miie/contracts/` - Contract definitions (interfaces, validators, DTOs, errors)
- `miie/detection/` - Detection algorithms
- `miie/interface/` - Interface definitions
- `miie/orchestration/` - Workflow and pipeline orchestration
- `miie/processing/` - Data processing (ingestion, extraction)
- `miie/reporting/` - Report generation
- `miie/schemas/` - Data schemas and validation
- `miie/storage/` - Storage mechanisms
- `miie/validation/` - Validation utilities

Each module contains `__init__.py` and relevant Python files.

## Test Structure (tests/)
The tests directory mirrors the source code structure with unit, integration, and other test types:
- `tests/unit/` - Unit tests for each module
- `tests/integration/` - Integration tests
- `tests/contract/` - Contract tests
- `tests/schema/` - Schema validation tests
- `tests/architecture/` - Architecture and dependency tests
- `tests/benchmark/` - Benchmark tests
- `tests/fixtures/` - Test fixtures and mock services
- `tests/performance/` - Performance tests
- `tests/workflow/` - Workflow tests
- `tests/conftest.py` - Pytest configuration

## Documentation Structure (docs/)
The docs directory contains:
- `docs/adr/` - Architecture Decision Records
- `docs/architecture/` - Architecture diagrams and guidelines
- `docs/audits/` - Audit reports and compliance documents
- `docs/authorities` - Authority documents (PRD, TRD, etc.)
- `docs/contracts` - Contract specifications
- `docs/execution` - Day-by-day execution logs and checklists
- `docs/governance` - Governance documents (signoffs, validation, risk registers, etc.)
- `docs/research` - Research-related documentation

## Other Key Directories
- `benchmarks/` - Contains benchmarking configurations, datasets, annotations, ground truth, and metadata.
- `scripts/` - Utility scripts for execution and automation.
- `research/` - Research notes, literature, rationales, threats, and traceability.
- `prompts/` - Prompt templates for various execution days and audits.

## Configuration Files
- `pyproject.toml` - Poetry project configuration and dependencies.
- `poetry.lock` - Locked dependencies.
- `.gitignore` - Git ignore rules.
- `.pre-commit-config.yaml` - Pre-commit hook configuration.
- `.github/workflows/ci.yml` - GitHub Actions CI/CD workflow.

## Notes
- The repository contains numerous audit-related markdown files in the root directory, generated during the FERA audit process.
- Temporary and output directories (like `output`, `tmp_output`, `test_output`) are used for storing intermediate and final results.