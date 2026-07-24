# Changelog

All notable changes to MIIE will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0] - 2026-07-04

### Added
- Complete dependency list in pyproject.toml (gitpython, pydantic, rich)
- Project classifiers, keywords, and URLs metadata
- py.typed marker for PEP 561
- requirements-dev.txt for development dependencies
- docker-compose.yml for local development
- Release workflow for automated PyPI publishing
- Example gallery with 7 runnable examples
- Comprehensive CLI reference documentation
- Python API guide
- Installation guide with platform-specific instructions
- Troubleshooting FAQ
- Contributing guide with development workflow
- Measurement Intelligence Reasoning Layer (reasoning package)
- 11 reasoning dataclasses, 8 engine functions, 36 reasoning tests
- Scientific Assurance Framework (assurance package)
- Assumption validation, evidence sufficiency, threats-to-validity
- Limitation reporting, extended audit trails, assurance engine
- 28 assurance tests, 1285+ lines of assurance code

### Fixed
- requirements.txt now matches actual dependencies
- Dockerfile uses pip install for better compatibility
- CI workflow installs dependencies for lint/typecheck jobs
- Version bumped to 1.6.0

### Changed
- Dependency version constraints updated for broader compatibility
- pandas >=2.0.0 (was ^2.1.0)
- All deps now use >= instead of ^ for flexibility

## [1.5.0] - 2026-07-02

### Added
- Observation Framework with full lifecycle management
- Sampling Framework with multiple strategies
- Scientific Readiness Certification
- Pipeline expanded from 7 to 9 stages
- Validation campaigns with reproducibility testing

### Changed
- Pipeline stages: Ingestion, Extraction, Segmentation, Detection, Scoring, Evidence, Sampling, Observation, Reporting

## [1.0.0] - 2026-06-29

### Added
- Initial release
- 3 detectors: D-01 (Metric Drift), D-02 (Behavioral Breakdown), D-03 (Compression)
- 9-stage analysis pipeline
- CLI with 10 commands
- REST API with FastAPI
- Benchmark suite
- Configuration management
