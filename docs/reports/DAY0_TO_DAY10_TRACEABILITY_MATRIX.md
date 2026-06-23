# MIIE Day 0-10 Traceability Matrix

Maps requirements from the operating plan to actual implementation evidence.
Each requirement is verified against repository evidence only (source code, tests, configurations, etc.).

## Day 0: Document Reconciliation & Freeze

| Requirement | Expected Location | Actual Location | Verification Status | Evidence |
|-------------|-------------------|-----------------|---------------------|----------|
| Create `freeze_register.md` | `docs/governance/freeze_register.md` | `docs/governance/freeze_register.md` | VERIFIED | File exists with frozen scope content |
| Create `terminology_registry.md` | `docs/governance/terminology_registry.md` | `docs/governance/terminology_registry.md` | VERIFIED | File exists with terminology definitions |
| Create `authority_matrix.md` | `docs/governance/authority_matrix.md` | `docs/governance/authority_matrix.md` | VERIFIED | File exists with authority mappings |
| Day 0 signoff note | `docs/governance/day0_signoff.md` | `docs/governance/signoffs/day0_signoff.md` | VERIFIED | File exists with placeholder signatures |
| Peer review validation | Review process | Not explicitly in code | PARTIAL | File exists but no automated review mechanism |

## Day 1: Repository Setup

| Requirement | Expected Location | Actual Location | Verification Status | Evidence |
|-------------|-------------------|-----------------|---------------------|----------|
| Initialize Git repository | GitHub repo with protected branch | Local git repository | VERIFIED | `.git` directory exists, GitHub remote configured |
| Create Poetry project | `pyproject.toml`, `poetry.lock` | `pyproject.toml`, `poetry.lock` | VERIFIED | Both files exist and contain dependency specifications |
| Add package entry points | `src/miie/__init__.py`, `__main__.py`, `cli.py` | `src/miie/__init__.py`, `__main__.py`, `cli.py` | VERIFIED | Files exist with proper package structure |
| Add CI/CD | `.github/workflows/ci.yml` | `.github/workflows/ci.yml` | VERIFIED | File exists with CI workflow definition |
| Add pre-commit and linting | `.pre-commit-config.yaml` | `.pre-commit-config.yaml` | VERIFIED | File exists with pre-commit hook configuration |
| Add testing framework | `tests/unit/test_version.py` | `tests/unit/test_version.py` | VERIFIED | File exists with version test |

## Day 2: Architecture Scaffolding

| Requirement | Expected Location | Actual Location | Verification Status | Evidence |
|-------------|-------------------|-----------------|---------------------|----------|
| Create module structure | `src/miie/processing/`, `benchmark/`, `reporting/`, `orchestration/`, `contracts/`, `schemas/` | Same as expected | VERIFIED | All directories exist with __init__.py files |
| Define dependency boundaries | `docs/architecture.md` | Not found | NOT_STARTED | Architecture documentation missing |
| Add import validation | `tests/unit/test_imports.py`, `test_architecture_boundaries.py` | Not found | NOT_STARTED | Import validation tests missing |
| Add placeholder Protocol map | `src/miie/contracts/interfaces.py` | `src/miie/contracts/interfaces.py` | VERIFIED | File exists with Protocol definitions |

## Day 3: Core Schema Foundation

| Requirement | Expected Location | Actual Location | Verification Status | Evidence |
|-------------|-------------------|-----------------|---------------------|----------|
| Implement `RepositoryContext` | `src/miie/schemas/models.py` | `src/miie/schemas/models.py` | VERIFIED | File exists with RepositoryContext dataclass |
| Implement `MetricDataFrame` | `src/miie/schemas/models.py` | `src/miie/schemas/models.py` | VERIFIED | File exists with MetricDataFrame dataclass |
| Implement `DetectorResult` | `src/miie/schemas/models.py` | `src/miie/schemas/models.py` | VERIFIED | File exists with DetectorResult dataclass |
| Implement `EvidencePackage` | `src/miie/schemas/models.py` | `src/miie/schemas/models.py` | VERIFIED | File exists with EvidencePackage dataclass |
| Implement deterministic serialization | `src/miie/schemas/serialization.py` | Not found | NOT_STARTED | Serialization helper missing |
| JSON Schema files | `*.schema.json` in schemas/ | Not found | NOT_STARTED | JSON Schema files missing |
| Schema tests | `tests/schema/` directory | Not found | NOT_STARTED | Schema test directory missing |

## Day 4: Contract Layer

| Requirement | Expected Location | Actual Location | Verification Status | Evidence |
|-------------|-------------------|-----------------|---------------------|----------|
| Create contracts package | `src/miie/contracts/` | `src/miie/contracts/` | VERIFIED | Directory exists |
| Add DTOs | `requests.py`, `responses.py` | Not found | NOT_STARTED | DTO files missing |
| Add Protocols | `interfaces.py` | `src/miie/contracts/interfaces.py` | PARTIAL | Exists but may not contain all required Protocols |
| Add validation rules | `validators.py` | Not found | NOT_STARTED | Validators file missing |
| Add error model | `errors.py` | Not found | NOT_STARTED | Errors file missing |
| Contract tests | `tests/contract/` directory | Not found | NOT_STARTED | Contract test directory missing |

## Day 5: Pipeline Skeleton

| Requirement | Expected Location | Actual Location | Verification Status | Evidence |
|-------------|-------------------|-----------------|---------------------|--------__|
| Implement pipeline controller | `src/miie/orchestration/pipeline.py` | `src/miie/orchestration/pipeline.py` | VERIFIED | File exists with pipeline implementation |
| Add deterministic mocks | `tests/fixtures/mock_services.py` | `tests/fixtures/mock_services.py` | VERIFIED | File exists with mock implementations |
| Implement workflow dispatcher | `src/miie/orchestration/workflow.py` | Not found | NOT_STARTED | Workflow dispatcher file missing |
| Add mock benchmark engine | `tests/fixtures/mock_benchmark.py` | Not found | NOT_STARTED | Mock benchmark file missing |
| Pipeline integration tests | `tests/integration/test_pipeline_skeleton.py` | Not found | NOT_STARTED | Pipeline skeleton test missing |
| Workflow unit tests | `tests/unit/test_workflow.py` | Not found | NOT_STARTED | Workflow test missing |
| Benchmark mock tests | `tests/unit/test_benchmark_mock.py` | Not found | NOT_STARTED | Benchmark mock test missing |

## Day 6: Repository Ingestion

| Requirement | Expected Location | Actual Location | Verification Status | Evidence |
|-------------|-------------------|-----------------|---------------------|----------|
| Validate local Git repository | `src/miie/processing/ingestion.py` | `src/miie/processing/ingestion.py` | VERIFIED | File exists with ingestion implementation |
| Extract repository metadata | Same as above | Same as above | VERIFIED | Metadata extraction implemented |
| Plan cache path safely | Same as above | Same as above | VERIFIED | Cache path planning implemented |
| Integrate M-01 into pipeline | `tests/integration/test_ingestion_to_pipeline.py` | Not found | NOT_STARTED | Ingestion-to-pipeline test missing |
| Ingestion unit tests | `tests/unit/test_ingestion.py` | Not found | NOT_STARTED | Ingestion unit test missing |
| Repository context extraction tests | `tests/unit/test_repository_context_extraction.py` | Not found | NOT_STARTED | Extraction test missing |
| Cache path tests | `tests/unit/test_cache_paths.py` | Not found | NOT_STARTED | Cache path test missing |

## Day 7: Metric Extraction Foundation

| Requment | Expected Location | Actual Location | Verification Status | Evidence |
|----------|-------------------|-----------------|---------------------|----------|
| Implement metric registry | `src/miie/registry.py` or `src/miie/schemas/metric_registry.py` | Not found | NOT_STARTED | Metric registry missing |
| Extract Commit Frequency | `src/miie/processing/extraction.py` | `src/miie/processing/extraction.py` | VERIFIED | File exists with extraction implementation |
| Extract Code Churn | Same as above | Same as above | VERIFIED | Code churn extraction implemented |
| Encode unavailable metrics | Same as above | Same as above | VERIFIED | Missing metric policy implemented |
| Integrate extraction | Integration test | Not found | NOT_STARTED | Extraction-to-detection test missing |
| Metric registry unit tests | `tests/unit/test_metric_registry.py` | Not found | NOT_STARTED | Registry test missing |
| Commit frequency tests | `tests/unit/test_commit_frequency.py` | Not found | NOT_STARTED | Commit frequency test missing |
| Code churn tests | `tests/unit/test_code_churn.py` | Not found | NOT_STARTED | Code churn test missing |
| Missing metric policy tests | `tests/unit/test_missing_metric_policy.py` | Not found | NOT_STARTED | Missing metric policy test missing |
| Ingestion-to-extraction tests | `tests/integration/test_ingestion_to_extraction.py` | Not found | NOT_STARTED | Integration test missing |

## Day 8: Detector Framework

| Requirement | Expected Location | Actual Location | Verification Status | Evidence |
|-------------|-------------------|-----------------|---------------------|----------|
| Implement `BaseDetector` | `src/miie/processing/detection.py` | `src/miie/processing/detection.py` | VERIFIED | File exists with detection implementation |
| Implement registry | Same as above | Same as above | VERIFIED | Detector registry implemented |
| Implement execution flow | Same as above | Same as above | VERIFIED | Execution flow implemented |
| Add tests | `tests/unit/test_detector_registry.py`, `test_detector_execution.py`, `test_detector_*` | Not found | NOT_STARTED | Detector unit tests missing |

## Day 8 Parallel Benchmark Track

| Requirement | Expected Location | Actual Location | Verification Status | Evidence |
|-------------|-------------------|-----------------|---------------------|----------|
| Create benchmark folders | `benchmarks/` directory with subdirectories | `benchmarks/` directory exists but empty/subdirs missing | PARTIAL | Benchmarks directory exists but structure incomplete |
| Create 30 candidates | `benchmarks/metadata/candidate_manifest.json` | Not found | NOT_STARTED | Candidate manifest missing |
| Draft annotation workflow | `benchmarks/annotations/annotation_workflow.md` | Not found | NOT_STARTED | Annotation workflow missing |
| Validate candidate metadata | `tests/benchmark/test_candidate_manifest.py` | Not found | NOT_STARTED | Validation test missing |
| Benchmark README | `benchmarks/README.md` | Not found | NOT_STARTED | README missing |

## Day 9: Evidence Framework

| Requirement | Expected Location | Actual Location | Verification Status | Evidence |
|-------------|-------------------|-----------------|---------------------|----------|
| Implement `EvidenceBuilder` | `src/miie/processing/evidence.py` | `src/miie/processing/evidence.py` | VERIFIED | File exists with evidence implementation |
| Implement `EvidenceValidator` | Same as above | Same as above | VERIFIED | Evidence validation implemented |
| Implement `EvidenceSerializer` | Same as above | Same as above | VERIFIED | Evidence serialization implemented |
| Integrate detector to evidence | `tests/integration/test_detector_to_evidence.py` | Not found | NOT_STARTED | Detector-to-evidence integration test missing |
| Evidence builder unit tests | `tests/unit/test_evidence_builder.py` | Not found | NOT_STARTED | Builder test missing |
| Evidence validator unit tests | `tests/unit/test_evidence_validator.py` | Not found | NOT_STARTED | Validator test missing |
| Evidence serializer unit tests | `tests/unit/test_evidence_serializer.py` | Not found | NOT_STARTED | Serializer test missing |

## Day 10: End-To-End Dry Run

| Requirement | Expected Location | Actual Location | Verification Status | Evidence |
|-------------|-------------------|-----------------|---------------------|----------|
| Add dry-run CLI command | `src/miie/cli.py` | `src/miie/cli.py` | VERIFIED | CLI exists with analyze command supporting --dry-run |
| Generate mock artifacts | Output directory contents | Not tested (requires execution) | UNKNOWN | CLI command exists but output not verified |
| Add reproducibility test | `tests/workflow/test_day10_dry_run.py` | Not found | NOT_STARTED | Dry run reproducibility test missing |
| Write Day 10 review | `docs/day_10_review.md` | Not found | NOT_STARTED | Day 10 review document missing |
| CLI dry run tests | Functional test of CLI | Not executed | UNKNOWN | CLI command present but not tested for dry-run functionality |

## Success Criteria Verification

### Repository Status
| Criteria | Expected | Actual | Status | Evidence |
|----------|----------|--------|--------|----------|
| `miie` repository exists | Repository root | Current directory | VERIFIED | We are in the miie repository |
| IMP-aligned structure | Standard Python package | `src/miie/` structure | VERIFIED | Standard src-layout package |
| Poetry, lockfile | `pyproject.toml`, `poetry.lock` | Both files exist | VERIFIED | Dependency management files present |
| GitHub Actions CI | `.github/workflows/ci.yml` | File exists | VERIFIED | CI workflow configured |
| Pre-commit | `.pre-commit-config.yaml` | File exists | VERIFIED | Pre-commit hooks configured |
| README, license, contribution files | Standard files | Not fully verified | PARTIAL | Some files may exist |
| Package version `1.0.0` | `__version__ = "1.0.0"` | In `src/miie/__init__.py` | VERIFIED | Version correctly set |

### Architecture Status
| Criteria | Expected | Actual | Status | Evidence |
|----------|----------|--------|--------|----------|
| TRD module boundaries exist | Defined boundaries | Not documented | NOT_STARTED | Architecture boundaries not documented |
| Import rules documented/tested | Tests/enforcement | Missing tests | NOT_STARTED | Import validation missing |
| No processing -> CLI/API imports | Layer isolation | Cannot verify without tests | UNKNOWN | No import validation tests |
| No non-frozen module appears | Frozen scope compliance | Cannot verify without docs | UNKNOWN | No architecture documentation |

### Schema Status
| Criteria | Expected | Actual | Status | Evidence |
|----------|----------|--------|--------|----------|
| Only 4 schemas implemented | RepositoryContext, MetricDataFrame, DetectorResult, EvidencePackage | All 4 present in models.py | VERIFIED | Four core schemas implemented |
| JSON Schema draft-07 validation | *.schema.json files | Missing | NOT_STARTED | JSON Schema files not generated |
| Deferred schemas documented | Documentation with reasons | Missing | NOT_STARTED | Deferred schema documentation missing |

### Contract Status
| Criteria | Expected | Actual | Status | Evidence |
|----------|----------|--------|--------|----------|
| ACS DTOs exist | requests.py, responses.py | Missing | NOT_STARTED | DTO files not present |
| Protocols exist | interfaces.py | Partially present | PARTIAL | Some Protocol definitions present |
| Validators exist | validators.py | Missing | NOT STARTED | Validation rules missing |
| Error model exists | errors.py | Missing | NOT STARTED | Error handling missing |
| Contract tests exist | tests/contract/ directory | Missing | NOT STARTED | Contract test suite missing |

### Pipeline Status
| Criteria | Expected | Actual | Status | Evidence |
|----------|----------|--------|--------|----------|
| Pipeline skeleton executes in AFD order | orchestrates loader→extractor→detector→evidence→scoring→report→benchmark | Pipeline exists but completeness unknown | PARTIAL | Pipeline controller exists but mock completeness unverified |
| Repository loader mock | Part of pipeline | In mock_services.py | VERIFIED | Loader mock present |
| Metric extractor mock | Part of pipeline | In mock_services.py | VERIFIED | Extractor mock present |
| Detector engine mock | Part of pipeline | In mock_services.py | VERIFIED | Detector mock present |
| Evidence engine mock | Part of pipeline | In mock_services.py | VERIFIED | Evidence mock present |
| Scoring engine mock | Part of pipeline | In mock_services.py | VERIFIED | Scoring mock present |
| Report engine mock | Part of pipeline | In mock_services.py | VERIFIED | Report mock present |
| Benchmark engine mock | Part of pipeline | Missing | NOT STARTED | Benchmark mock missing |

### Benchmark Status
| Criteria | Expected | Actual | Status | Evidence |
|----------|----------|--------|--------|----------|
| Benchmark directories exist | benchmarks/ structure | Directory exists but incomplete | PARTIAL | Benchmarks directory present but missing substructure |
| 30 synthetic benchmark candidates | candidate_manifest.json with 30 entries | Missing | NOT STARTED | Candidate manifest not created |
| No claim of complete coverage | Documentation states candidates only | Cannot verify without docs | UNKNOWN | No benchmark documentation to verify claims |
| Annotation workflow documented | annotation_workflow.md | Missing | NOT STARTED | Annotation workflow not documented |

### Research Status
| Criteria | Expected | Actual | Status | Evidence |
|----------|----------|--------|--------|----------|
| Literature notes exist | research/literature_notes.md | Not found | NOT STARTED | Literature notes missing |
| Threats-to-validity log | research/threats_to_validity.md | Not found | NOT STARTED | Threats log missing |
| Benchmark decision log | Not specified | Not found | NOT STARTED | Benchmark decisions missing |
| Evidence traceability notes | research/evidence_publication_mapping.md etc. | Not found | NOT STARTED | Evidence mapping missing |

### Testing Status
| Criteria | Expected | Actual | Status | Evidence |
|----------|----------|--------|--------|----------|
| Unit tests exist | tests/unit/ directory | Some missing | PARTIAL | Some unit tests present, many missing |
| Integration tests exist | tests/integration/ directory | Missing | NOT STARTED | Integration tests largely missing |
| Contract tests exist | tests/contract/ directory | Missing | NOT STARTED | Contract test suite missing |
| Schema tests exist | tests/schema/ directory | Missing | NOT STARTED | Schema test suite missing |
| Architecture-boundary tests | Specific test files | Missing | NOT STARTED | Architecture validation tests missing |
| Dry-run tests | tests/workflow/test_day10_dry_run.py | Missing | NOT STARTED | Dry run reproducibility test missing |
| Reproducibility tests | Same as above | Missing | NOT STARTED | No reproducibility verification |
| Scaffold coverage ≥70% | Coverage report | Cannot measure without tests | UNKNOWN | Insufficient tests to measure coverage |

### Documentation Status
| Criteria | Expected | Actual | Status | Evidence |
|----------|----------|--------|--------|----------|
| freeze_register.md | docs/governance/freeze_register.md | File exists | VERIFIED | Freeze register present |
| terminology_registry.md | docs/governance/terminology_registry.md | File exists | VERIFIED | Terminology registry present |
| authority_matrix.md | docs/governance/authority_matrix.md | File exists | VERIFIED | Authority matrix present |
| docs/architecture.md | docs/architecture.md | Not found | NOT STARTED | Architecture documentation missing |
| docs/day_10_review.md | docs/day_10_review.md | Not found | NOT STARTED | Day 10 review missing |
| Dry-run usage docs | Documentation for --dry-run | Not found | NOT STARTED | Dry-run usage documentation missing |

### CI/CD Status
| Criteria | Expected | Actual | Status | Evidence |
|----------|----------|--------|--------|----------|
| CI runs install | .github/workflows/ci.yml | Verified in file | VERIFIED | Install step present |
| CI runs lint | Same | Verified in file | VERIFIED | Lint step present |
| CI runs type check | Same | Verified in file | VERIFIED | Type checking step present |
| CI runs schema tests | Same | Not verified | UNKNOWN | Schema tests missing from CI |
| CI runs contract tests | Same | Not verified | UNKNOWN | Contract tests missing from CI |
| CI runs unit tests | Same | Verified in file | VERIFIED | Unit tests present in CI |
| CI runs integration tests | Same | Not verified | UNKNOWN | Integration tests missing from CI |
| CI runs dry-run reproducibility check | Same | Not verified | UNKNOWN | Dry-run reproducibility check missing |
| CI fails on nondeterministic output | Same | Not verified | UNKNOWN | No mechanism to detect nondeterminism |

---