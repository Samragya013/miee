# MIIE Day 0-10 Requirement Matrix

Extracted from: MIIE Day 0-10 Execution Operating Plan

This matrix contains all requirements, objectives, tasks, inputs, outputs, deliverables, files, modules, tests, milestones, and validation criteria for each day.

## Day 0: Document Reconciliation & Freeze

### Objectives
- Reconcile the frozen documents into executable authority rules, terminology, scope boundaries, and conflict-resolution procedures
- Produce the operating documents that prevent the team from reinterpreting MIIE v1.0 during implementation

### Tasks
1. Create `freeze_register.md`
2. Create `terminology_registry.md` 
3. Create `authority_matrix.md`

### Inputs
- Frozen document PDFs or canonical Markdown copies
- Previous Day 1-10 execution plan PDF as historical input only
- Team roster: Engineer A, Engineer B, Engineer C
- Repository name: `miie`

### Outputs
- `docs/governance/freeze_register.md`
- `docs/governance/terminology_registry.md`
- `docs/governance/authority_matrix.md`
- Day 0 signoff note in `docs/governance/day0_signoff.md`

### Deliverables
| File | Purpose | Owner |
|------|---------|-------|
| `docs/governance/freeze_register.md` | Frozen scope and deferred scope | Engineer A |
| `docs/governance/terminology_registry.md` | Canonical naming | Engineer C |
| `docs/governance/authority_matrix.md` | Decision authority guide | Engineer A |
| `docs/governance/day0_signoff.md` | Team approval note | Engineer B |

### Modules
- None (documentation only)

### Tests
- Validation through peer review (reviewed by all three engineers)

### Milestones
- Day 0 signoff completion

### Validation Criteria
- Pass: every frozen item maps to TRD, ACS, BSD, TFS, AFD, IMP, and MIBS where applicable
- Fail: any V2, dashboard, SaaS, or enterprise item appears
- Recovery: remove item, cite the violated authority, and add it to forbidden scope
- Definition of Done:
  - Reviewed by all three engineers
  - No uncited capability appears
  - Includes explicit "not implemented by Day 10" section

## Day 1: Repository Setup

### Objectives
- Create the repository, Poetry project, Git/GitHub controls, CI/CD, pre-commit, linting, and testing framework

### Tasks
| Task | Purpose | Inputs | Processing | Outputs |
|------|---------|--------|------------|---------|
| Initialize Git repository | Establish controlled implementation base | Day 0 governance docs, IMP repo structure | Create repo, protect `main`, add branch rules, add PR templates | GitHub repo with protected branch |
| Create Poetry project | Make dependency state reproducible | IMP dependency list | Create `pyproject.toml`, add pinned runtime/dev deps, lock | Poetry project |
| Add package entry points | Establish TRD package identity | TRD namespace and CLI entry | Add `src/miie/__init__.py`, `__main__.py`, `cli.py` version command | Importable package |
| Add CI/CD | Make every change reviewable | Poetry project | Add GitHub Actions for install, lint, type check, tests | CI workflow |
| Add pre-commit and linting | Enforce style before review | IMP coding standards | Configure black, isort, flake8, mypy | Local quality gate |
| Add testing framework | Prepare deterministic verification | IMP testing strategy | Create test folders and first version/import tests | Test scaffold |

### Outputs
- `pyproject.toml`, `poetry.lock`, `requirements.txt`
- `.github/workflows/ci.yml`
- `.pre-commit-config.yaml`
- `src/miie/__init__.py`, `src/miie/__main__.py`, `src/miie/cli.py`
- `tests/unit/test_version.py`

### Deliverables
| File | Purpose |
|------|---------|
| `pyproject.toml`, `poetry.lock`, `requirements.txt` | Dependency management |
| `.github/workflows/ci.yml` | CI/CD pipeline |
| `.pre-commit-config.yaml` | Pre-commit hooks |
| `src/miie/__init__.py`, `src/miie/__main__.py`, `src/miie/cli.py` | Package entry points |
| `tests/unit/test_version.py` | Version test |

### Modules
- `miie` (root package)
  - `__init__.py`
  - `__main__.py`
  - `cli.py`

### Tests
- `tests/unit/test_version.py`

### Milestones
- Clean initial commit
- Lockfile committed
- Green CI on initial PR
- Hook docs in README
- CI runs pytest

### Validation Criteria
- Clean install on Python 3.10
- Both `poetry run miie --version` and `poetry run python -m miie --version` return `1.0.0`
- Version smoke test passes
- CI fails on test/type/lint errors
- Hooks run locally
- Unit smoke tests pass

## Day 2: Architecture Scaffolding

### Objectives
- Create TRD-driven module structure, dependency boundaries, package layout, import rules, and architecture validation tests

### Tasks
| Task | Purpose | Inputs | Processing | Outputs |
|------|---------|--------|------------|---------|
| Create module structure | Encode TRD module inventory | TRD M-01..M-17, IMP repo tree | Create processing, benchmark, reporting, orchestration, contracts, schemas packages | Importable package tree |
| Define dependency boundaries | Prevent architecture drift | TRD layers, AFD flows | Write allowed import graph and layer rules | Architecture guide |
| Add import validation | Make architecture executable | Package tree | AST-based or simple import rule tests | Boundary tests |
| Add placeholder Protocol map | Prepare ACS without behavior | ACS service contracts | Define Protocol names only; no logic | Typed interfaces |

### Outputs
- `docs/architecture.md`
- `src/miie/contracts/interfaces.py`
- `tests/unit/test_imports.py`
- `tests/unit/test_architecture_boundaries.py`

### Deliverables
| File | Purpose |
|------|---------|
| `docs/architecture.md` | Architecture documentation |
| `src/miie/contracts/interfaces.py` | Protocol definitions |
| `tests/unit/test_imports.py` | Import validation tests |
| `tests/unit/test_architecture_boundaries.py` | Architecture boundary tests |

### Modules
- `src/miie/processing/`
- `src/miie/benchmark/`
- `src/miie/reporting/`
- `src/miie/orchestration/`
- `src/miie/contracts/`
- `src/miie/schemas/`

### Tests
- `tests/unit/test_imports.py`
- `tests/unit/test_architecture_boundaries.py`

### Milestones
- Module scaffold completion
- No non-frozen module

### Validation Criteria
- All modules import without side effects
- Forbidden imports fail test
- `processing` cannot import `cli` or `api`
- Architecture tests pass
- Test enforced in CI

## Day 3: Core Schema Foundation

### Objectives
- Implement only the four schemas needed for the Day 10 dry-run slice: `RepositoryContext`, `MetricDataFrame`, `DetectorResult`, and `EvidencePackage`

### Tasks
| Task | Purpose | Inputs | Processing | Outputs |
|------|---------|--------|------------|---------|
| Implement `RepositoryContext` | Make M-01 output executable | BSD Section 5, TRD ingestion | Dataclass plus JSON schema | Repo context model |
| Implement `MetricDataFrame` | Make M-02 output executable | BSD Section 6, TFS metrics | Dataclass plus JSON schema; metric ID enum M-01..M-07 | Metric model |
| Implement `DetectorResult` | Make D-01..D-03 mock output valid | BSD Section 8, TFS detector freeze | Dataclass plus JSON schema; detector ID enum D-01..D-03 | Detector result model |
| Implement `EvidencePackage` | Make Day 9 evidence traceable | BSD Section 10, PRD evidence principle | Dataclass plus JSON schema with trace fields | Evidence model |
| Implement deterministic serialization | Support reproducibility | BSD serialization rules | Sorted keys, stable separators, checksum helper, no generated time | Serialization helper |

### Outputs
- `src/miie/schemas/models.py`
- `repository_context.schema.json`
- `metric_dataframe.schema.json`
- `detector_result.schema.json`
- `evidence_package.schema.json`
- `src/miie/schemas/serialization.py`

### Deliverables
| File | Purpose |
|------|---------|
| `src/miie/schemas/models.py` | Schema dataclass implementations |
| `repository_context.schema.json` | RepositoryContext JSON schema |
| `metric_dataframe.schema.json` | MetricDataFrame JSON schema |
| `detector_result.schema.json` | DetectorResult JSON schema |
| `evidence_package.schema.json` | EvidencePackage JSON schema |
| `src/miie/schemas/serialization.py` | Deterministic serialization helper |

### Modules
- `src/miie/schemas/`

### Tests
- `tests/schema/test_repository_context.py`
- `tests/schema/test_metric_dataframe.py`
- `tests/schema/test_detector_result.py`
- `tests/schema/test_evidence_package.py`
- `tests/unit/test_serialization.py`

### Milestones
- Schema 1, 2, 3, 4 completion
- Valid/invalid tests pass
- Frozen metric inventory enforced
- No detector math
- Evidence requires detector/metric links
- Checksum stable

### Validation Criteria
- JSON Schema files pass draft-07 validation
- Unknown fields fail
- Invalid metric and detector IDs fail
- Serialization is deterministic
- Evidence without traceability fails

## Day 4: Contract Layer

### Objectives
- Implement ACS contracts as DTOs, interfaces, Protocols, validation rules, and contract tests for the Day 0-10 execution slice

### Tasks
| Task | Purpose | Inputs | Processing | Outputs |
|------|---------|--------|------------|---------|
| Create contracts package | Keep communication separate from implementation | ACS Sections 4-18 | Add requests, responses, errors, validators, interfaces | Contract package |
| Add DTOs | Make payloads typed | Day 3 schemas, ACS contracts | Add ingestion, metric extraction, detector invocation, evidence generation, dry-run report DTOs | Typed DTOs |
| Add Protocols | Decouple pipeline from concrete modules | ACS internal service contracts | Define RepositoryLoader, MetricExtractor, DetectorEngine, EvidenceEngine, ScoringEngine, ReportEngine, BenchmarkEngine Protocols | Service Protocols |
| Add validation rules | Reject bad inputs early | TFS IDs, BSD strictness | Validate metric IDs, detector IDs, paths, output formats, seeds, dry-run flag | Validators |
| Add error model | Standardize contract failures | ACS error framework | Add error category, severity, recovery action, user-visible message | Error DTOs |

### Outputs
- `src/miie/contracts/*`
- `requests.py`, `responses.py`
- `interfaces.py`
- `validators.py`
- `errors.py`

### Deliverables
| File | Purpose |
|------|---------|
| `src/miie/contracts/*` | Contract package |
| `requests.py`, `responses.py` | DTOs |
| `interfaces.py` | Protocol definitions |
| `validators.py` | Validation rules |
| `errors.py` | Error model |

### Modules
- `src/miie/contracts/`

### Tests
- `tests/contract/`

### Milestones
- Contract base completion
- Import rules pass
- DTO suite completion
- Protocol suite completion
- Validation suite completion
- Error suite completion

### Validation Criteria
- DTOs use Day 3 schemas where applicable
- Invalid IDs fail before processing
- Unknown fields fail
- Contract tests include positive and negative cases
- No detector, scoring, benchmark, or report logic appears in contracts

## Day 5: Pipeline Skeleton

### Objectives
- Implement orchestration-only pipeline skeleton with mock implementations for Repository Loader, Metric Extractor, Detector Engine, Evidence Engine, Scoring Engine, Report Engine, and Benchmark Engine

### Tasks
| Task | Purpose | Inputs | Processing | Outputs |
|------|---------|--------|------------|---------|
| Implement pipeline controller | Prove AFD stage order | ACS Protocols, AFD WF-01 | Constructor-inject services; call loader, extractor, detector, evidence, scoring mock, report mock | Pipeline skeleton |
| Add deterministic mocks | Enable integration without algorithms | Day 3 schemas | Fixed run ID, timestamp, seed, metric values, detector output | Test mocks |
| Implement workflow dispatcher | Prepare frozen workflow routing | AFD workflow inventory | Register WF-01..WF-05; reject unknown workflows | Workflow skeleton |
| Add mock benchmark engine | Reserve benchmark boundary | MIBS, ACS benchmark contract | Mock accepts candidate list and returns placeholder status only | Benchmark mock |

### Outputs
- `src/miie/orchestration/pipeline.py`
- `tests/fixtures/mock_services.py`
- `src/miie/orchestration/workflow.py`
- `tests/fixtures/mock_benchmark.py`

### Deliverables
| File | Purpose |
|------|---------|
| `src/miie/orchestration/pipeline.py` | Pipeline controller |
| `tests/fixtures/mock_services.py` | Deterministic mocks |
| `src/miie/orchestration/workflow.py` | Workflow dispatcher |
| `tests/fixtures/mock_benchmark.py` | Mock benchmark engine |

### Modules
- `src/miie/orchestration/`

### Tests
- `tests/integration/test_pipeline_skeleton.py`
- `tests/fixtures/`
- `tests/unit/test_workflow.py`
- `tests/unit/test_benchmark_mock.py`

### Milestones
- Pipeline shell completion
- Mock suite completion
- Workflow shell completion
- Benchmark placeholder completion

### Validation Criteria
- Pipeline uses Protocols, not concrete implementation coupling
- Mock output is schema-valid
- Research files cite which authority document motivated each note
- Unknown workflow fails
- Frozen workflows only
- Does not claim performance

### Parallel Research Track
| Track | Day 5 Work | Expected Output Files |
|-------|------------|----------------------|
| Research Tasks | Create publication-readiness log and research question traceability notes | `research/research_traceability.md` |
| Paper Review Tasks | Start annotated bibliography for metric validity, Goodhart effects, detector validation, benchmark construction | `research/literature_notes.md` |
| Threats-To-Validity Tasks | Create initial internal/external/construct/conclusion validity risk log | `research/threats_to_validity.md` |
| Benchmark Tasks | Define benchmark candidate acceptance criteria, not datasets yet | `benchmarks/candidate_acceptance_criteria.md` |

## Day 6: Repository Ingestion

### Objectives
- Build M-01 repository ingestion foundation: local Git validation, repository metadata extraction, path safety, cache path planning, tests, and integration with the pipeline skeleton

### Tasks
| Task | Purpose | Inputs | Processing | Outputs |
|------|---------|--------|------------|---------|
| Validate local Git repository | Prevent invalid input entering pipeline | Local Git fixture, bad path fixture | Check path existence, directory type, Git validity, traversal safety | Validated repository input |
| Extract repository metadata | Produce `RepositoryContext` | Valid Git fixture | Extract repo ID, commit count, first/last commit date, contributor count, shallow/fork flags where available | `RepositoryContext` |
| Plan cache path safely | Respect TRD storage layout | Repo ID, cache root | Resolve `~/.miie/cache/repos/{repo_id}` without writing in unit test | Cache path helper |
| Integrate M-01 into pipeline | Replace mock loader where safe | Pipeline skeleton, M-01 output | Feed real `RepositoryContext` to mock extractor | Integration pass |

### Outputs
- `src/miie/processing/ingestion.py`
- Same as input for extraction tests
- Same as input for cache path tests
- `tests/integration/test_ingestion_to_pipeline.py`

### Deliverables
| File | Purpose |
|------|---------|
| `src/miie/processing/ingestion.py` | Repository ingestion engine |
| Same as input for extraction tests | Repository context extraction tests |
| Same as input for cache path tests | Cache path helper tests |
| `tests/integration/test_ingestion_to_pipeline.py` | Ingestion to pipeline integration test |

### Modules
- `src/miie/processing/`

### Tests
- `tests/unit/test_ingestion.py`
- `tests/unit/test_repository_context_extraction.py`
- `tests/unit/test_cache_paths.py`
- `tests/integration/test_ingestion_to_pipeline.py`

### Milestones
- M-01 validation completion
- Metadata extractor completion
- Path helper completion
- Integration pass

### Validation Criteria
- Valid local Git repository accepted
- Missing path rejected
- Non-Git directory rejected
- Path traversal rejected
- Metadata validates against `RepositoryContext`
- Cache path cannot escape configured root
- M-01 output accepted by mock M-02
- M-01 error propagates through pipeline as ACS error

### Parallel Research Track
| Track | Day 6 Work | Output File |
|-------|------------|-------------|
| Research Tasks | Record repository selection assumptions and risks | `research/repository_selection_notes.md` |
| Paper Review Tasks | Summarize repository mining reproducibility papers | `research/literature_notes.md` |
| Threats-To-Validity Tasks | Add threats from Git history incompleteness, shallow repos, bot commits | `research/threats_to_validity.md` |
| Benchmark Tasks | Draft fixture repository requirements | `benchmarks/repository_fixture_requirements.md` |

## Day 7: Metric Extraction Foundation

### Objectives
- Implement only Commit Frequency and Code Churn extraction foundations. Do not implement all seven metrics.

### Tasks
| Task | Purpose | Inputs | Processing | Outputs |
|------|---------|--------|------------|---------|
| Implement metric registry | Freeze M-01..M-07 inventory | TFS metric table | Register metric IDs, names, ranges, missing-data policy | Frozen metric registry |
| Extract Commit Frequency | Implement Git-backed M-02 | `RepositoryContext`, Git fixture | Count commits per window or fixed dry-run window | M-02 metric rows |
| Extract Code Churn | Implement Git-backed M-06 foundation | Git fixture | Compute added/deleted lines from fixture commits with deterministic bounds | M-06 metric rows |
| Encode unavailable metrics | Avoid fake values | Missing artifact policy | Return unavailable/null with warning metadata for M-01, M-03, M-04, M-05, M-07 when artifacts absent | Valid missing-data records |
| Integrate extraction | Feed detector mock | M-01 output, M-02 output | `RepositoryContext -> MetricDataFrame -> mock DetectorEngine` | Integration pass |

### Outputs
- `src/miie/registry.py` or `src/miie/schemas/metric_registry.py`
- `src/miie/processing/extraction.py`
- Same as input for code churn tests
- Same as input for missing metric policy tests
- Integration test

### Deliverables
| File | Purpose |
|------|---------|
| `src/miie/registry.py` or `src/miie/schemas/metric_registry.py` | Metric registry |
| `src/miie/processing/extraction.py` | Metric extraction engine |
| Same as input for code churn tests | Code churn extraction tests |
| Same as input for missing metric policy tests | Missing metric policy tests |
| Integration test | Extraction to detection integration test |

### Modules
- `src/miie/schemas/` or `src/miie/`
- `src/miie/processing/`

### Tests
- `tests/unit/test_metric_registry.py`
- `tests/unit/test_commit_frequency.py`
- `tests/unit/test_code_churn.py`
- `tests/unit/test_missing_metric_policy.py`
- `tests/integration/test_ingestion_to_extraction.py`

### Milestones
- Registry completion
- M-02 extractor completion
- M-06 extractor completion
- Missing policy completion
- Pipeline slice completion

### Validation Criteria
- Unsupported metrics fail
- Deterministic count
- Fixture value stable
- Unavailable is not zero
- Schema validates
- Detector mock accepts metrics

### Parallel Research Track
| Track | Day 7 Work | Output File |
|-------|------------|-------------|
| Research Tasks | Document why M-02/M-06 are first extraction targets | `research/metric_extraction_rationale.md` |
| Paper Review Tasks | Add notes on commit frequency and churn validity limitations | `research/literature_notes.md` |
| Threats-To-Validity Tasks | Add construct validity risks for Git-derived metrics | `research/threats_to_validity.md` |
| Benchmark Tasks | Define candidate metric availability matrix | `benchmarks/metric_availability_matrix.md` |

## Day 8: Detector Framework

### Objectives
- Implement `BaseDetector`, `DetectorRegistry`, `DetectorExecutionFlow`, and `DetectorResult` usage. No detector mathematics. No scoring.

### Tasks
| Task | Purpose | Inputs | Processing | Outputs |
|------|---------|--------|------------|---------|
| Implement `BaseDetector` | Stable detector contract | ACS detector invocation, BSD `DetectorResult` | Abstract base or Protocol with `run` | Base class |
| Implement registry | Freeze D-01..D-03 | TFS detector inventory | Register metadata for D-01, D-02, D-03; reject D-04 | Detector registry |
| Implement execution flow | Deterministic detector dispatch | MetricDataFrame, detector IDs | Validate inputs; execute mocks in D-01,D-02,D-03 order | Result list |
| Add tests | Lock no-math framework | Mock metric data | Test registry, order, invalid detector, schema result | Test suite |

### Outputs
- `src/miie/processing/detection.py`
- Same as input for registry tests
- Same as input for execution flow tests
- Tests

### Deliverables
| File | Purpose |
|------|---------|
| `src/miie/processing/detection.py` | Detection processing |
| Same as input for registry tests | Detector registry tests |
| Same as input for execution flow tests | Detector execution tests |
| Tests | Detector test suite |

### Modules
- `src/miie/processing/detection/`

### Tests
- `tests/unit/test_detector_registry.py`
- `tests/unit/test_detector_execution.py`
- `tests/unit/test_detector_*`

### Milestones
- Detector base completion
- Registry completion
- Execution flow completion
- Test suite completion

### Validation Criteria
- Cannot instantiate without run
- Frozen only (D-04 rejected)
- Order stable
- Schema-valid mock results
- No algorithm assertions
- CI pass

### Parallel Research Track
| Track | Day 8 Work | Output File |
|-------|------------|-------------|
| Research Tasks | Document why M-02/M-06 are first extraction targets | `research/metric_extraction_rationale.md` |
| Paper Review Tasks | Add notes on commit frequency and churn validity limitations | `research/literature_notes.md` |
| Threats-To-Validity Tasks | Add construct validity risks for Git-derived metrics | `research/threats_to_validity.md` |
| Benchmark Tasks | Define candidate metric availability matrix | `benchmarks/metric_availability_matrix.md` |

### Day 8 Parallel Benchmark Track

#### Objectives
- Create benchmark folder foundations and 30 synthetic benchmark candidates only. Do not create the full 120-dataset benchmark suite.

#### Tasks
| Task | Purpose | Inputs | Processing | Outputs |
|------|---------|--------|------------|---------|
| Create benchmark folders | Reserve MIBS structure | MIBS, TFS, BSD benchmark storage | Add directories and README files | Benchmark skeleton |
| Create 30 candidates | Test candidate workflow | Fixed seed, candidate spec | Generate or stub 30 candidate folders with metadata; mark as candidates | Candidate set |
| Draft annotation workflow | Prepare ground truth discipline | MIBS, TFS ground truth rules | Create reviewer/adjudication procedure | Annotation guide |
| Validate candidate metadata | Prevent benchmark chaos | Candidate manifest | Check IDs, seeds, pathology labels, checksums placeholders | Validation script/test |

#### Expected Deliverables
- `benchmarks/README.md`
- `benchmarks/metadata/candidate_manifest.json`
- `benchmarks/annotations/annotation_workflow.md`
- `tests/benchmark/test_candidate_manifest.py`

#### Validation
- Paths match planned structure
- Manifest count is 30
- No benchmark performance claim
- Invalid candidate fails

#### Parallel Research Track
- Research Tasks: define candidate-to-detector traceability
- Paper Review Tasks: summarize synthetic benchmark validity concerns
- Threats-To-Validity Tasks: add synthetic-data external validity risks
- Benchmark Tasks: create 30 candidate manifest entries

## Day 9: Evidence Framework

### Objectives
- Implement `EvidencePackage`, `EvidenceBuilder`, `EvidenceValidator`, `EvidenceSerializer`, and traceability rules

### Tasks
| Task | Purpose | Inputs | Processing | Outputs |
|------|---------|--------|------------|---------|
| Implement `EvidenceBuilder` | Convert detector results into evidence | RepositoryContext, MetricDataFrame, DetectorResult | Build traceable evidence items | EvidencePackage |
| Implement `EvidenceValidator` | Reject incomplete evidence | EvidencePackage | Validate IDs, references, provenance, schema | Validation result |
| Implement `EvidenceSerializer` | Preserve reproducibility | EvidencePackage | Sorted JSON, stable checksum | Evidence JSON |
| Integrate detector to evidence | Prove pipeline link | Mock DetectorResult | Feed mock result into evidence builder | Integration pass |

### Outputs
- `src/miie/processing/evidence.py`
- Same as input for validator tests
- Same as input for serializer tests
- Integration test

### Deliverables
| File | Purpose |
|------|---------|
| `src/miie/processing/evidence.py` | Evidence processing |
| Same as input for validator tests | Evidence validator tests |
| Same as input for serializer tests | Evidence serializer tests |
| Integration test | Detector to evidence integration test |

### Modules
- `src/miie/processing/`

### Tests
- `tests/unit/test_evidence_builder.py`
- `tests/unit/test_evidence_validator.py`
- `tests/unit/test_evidence_serializer.py`
- `tests/integration/test_detector_to_evidence.py`

### Milestones
- Builder completion
- Validator completion
- Serializer completion
- Integration pass

### Validation Criteria
- Every item links detector/metric/window
- No ungrounded claims
- Missing trace fails
- Strict validation
- Two serializations equal
- Schema-valid output
- Pipeline order preserved

### Traceability Rules
- Every evidence item must reference `run_id`
- Every evidence item must reference `detector_id`
- Every detector evidence item must reference `metric_id`
- Window reference is required when windowed data exists; if mock data has no real window, the evidence item must explicitly mark `window_id: "mock-window-001"`
- Evidence text must describe observed mock data only; it must not claim real corruption

### Parallel Research Track
| Track | Day 9 Work | Output File |
|-------|------------|-------------|
| Research Tasks | Map evidence fields to publication artifact needs | `research/evidence_publication_mapping.md` |
| Paper Review Tasks | Add notes on explainability and statistical evidence reporting | `research/literature_notes.md` |
| Threats-To-Validity Tasks | Add evidence interpretation risks | `research/threats_to_validity.md` |
| Benchmark Tasks | Map candidate benchmark labels to evidence expectations | `benchmarks/evidence_expectation_matrix.md` |

## Day 10: End-To-End Dry Run

### Objectives
- Execute a deterministic dry run using mock repository, mock metrics, mock detector results, mock evidence, mock reports, and pipeline execution

### Tasks
| Task | Purpose | Inputs | Processing | Outputs |
|------|---------|--------|------------|---------|
| Add dry-run CLI command | Let team execute Day 10 slice | CLI DTOs, pipeline skeleton | `miie analyze --dry-run --repo <path> --output <dir> --seed 42` | Dry-run execution |
| Generate mock artifacts | Validate TRD output layout | Mock pipeline result | Write manifest, results, metrics, evidence, run metrics, dry report | Output dir |
| Add reproducibility test | Prove deterministic output | Same repo, seed, fixed metadata | Run twice and compare outputs | Workflow test |
| Write Day 10 review | Document built/mocked/unbuilt status | Test results, module status | Create review and next-focus list | Review doc |

### Outputs
- `src/miie/cli.py`
- Output directory contents: `manifest.json`, `results.json`, `dry_run_report.md`, `metrics.csv`, `evidence.json`, `run_metrics.json`
- `tests/workflow/test_day10_dry_run.py`
- `docs/day_10_review.md`

### Deliverables
| File | Purpose |
|------|---------|
| `src/miie/cli.py` | CLI with dry-run command |
| Output directory contents | Dry-run artifacts |
| `tests/workflow/test_day10_dry_run.py` | Reproducibility test |
| `docs/day_10_review.md` | Day 10 review document |

### Modules
- `src/miie/cli.py` (CLI command)
- Various processing modules (through mocks)

### Tests
- `tests/workflow/test_day10_dry_run.py`

### Milestones
- CLI dry run completion
- Artifact set completion
- Repro test completion
- Review completion

### Validation Criteria
- Pass: dry run produces all files, JSON validates, evidence validates, dry report states mock-only, two runs are byte-identical
- Fail: output omits artifact, claims real detector result, contains current timestamp, or differs across identical runs
- Recovery Steps: inject fixed metadata, remove real-analysis claims, repair writer, rerun reproducibility test
- Definition of Done:
  - No bypass (CLI command routes through pipeline)
  - Report says "mock detector output" instead of "detected corruption"
  - Path fields identical across two temporary directories for byte comparison
  - Scoring mock does not appear to implement real TFS formula

### Parallel Research Track
| Track | Day 10 Work | Output File |
|-------|-------------|-------------|
| Research Tasks | Finalize Day 10 research readiness note | (not specified) |
| Paper Review Tasks | Summarize open literature gaps | (not specified) |
| Threats-To-Validity Tasks | Rank top risks for Days 11-20 | (not specified) |
| Benchmark Tasks | Review 30 candidate manifest and decide next candidate expansion gate | (not specified) |

## Success Criteria By Day 10

### Area: Repository Status
- Measurable Day 10 Criteria: `miie` repository exists with IMP-aligned structure, Poetry, lockfile, GitHub Actions CI, pre-commit, README, license, contribution files, and package version `1.0.0`.

### Area: Architecture Status
- Measurable Day 10 Criteria: TRD module boundaries exist; import rules are documented and tested; no processing module imports CLI/API; no non-frozen module appears.

### Area: Schema Status
- Measurable Day 10 Criteria: Only `RepositoryContext`, `MetricDataFrame`, `DetectorResult`, and `EvidencePackage` are implemented; JSON Schema draft-07 validation exists; deferred schemas are documented with reasons.

### Area: Contract Status
- Measurable Day 10 Criteria: ACS DTOs, Protocols, validators, error model, and contract tests exist for Days 0-10 execution surfaces.

### Area: Pipeline Status
- Measurable Day 10 Criteria: Pipeline skeleton executes repository loader, metric extractor, detector engine, evidence engine, scoring mock, report mock, and benchmark mock in AFD order.

### Area: Benchmark Status
- Measurable Day 10 Criteria: Benchmark directories exist; 30 synthetic benchmark candidates exist as candidates only; no claim of complete B-01/B-02/B-03 coverage; annotation workflow is documented.

### Area: Research Status
- Measurable Day 10 Criteria: Literature notes, threats-to-validity log, benchmark decision log, and evidence traceability notes exist from Day 5 onward.

### Area: Testing Status
- Measurable Day 10 Criteria: Unit, integration, contract, schema, architecture-boundary, dry-run, and reproducibility tests exist; scaffold coverage target is at least 70 percent.

### Area: Documentation Status
- Measurable Day 10 Criteria: `freeze_register.md`, `terminology_registry.md`, `authority_matrix.md`, `docs/architecture.md`, `docs/day_10_review.md`, and dry-run usage docs exist.

### Area: CI/CD Status
- Measurable Day 10 Criteria: CI runs install, lint, type check, schema tests, contract tests, unit tests, integration tests, dry-run reproducibility check, and fails on nondeterministic output.

---