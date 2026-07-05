# MIIE v1.6 Implementation Backlog

| Field          | Value                                   |
| -------------- | --------------------------------------- |
| **Document**   | V1_6_IMPLEMENTATION_BACKLOG             |
| **Spec ID**    | IMS-v1.6-PR10..PR13                     |
| **Version**    | 1.0                                     |
| **Status**     | DRAFT                                   |
| **Created**    | 2026-07-03                              |
| **Owner**      | MIIE Engineering                        |
| **Depends On** | PR-9 (Architecture Specifications)     |

---

## 1. Purpose

This document defines the implementation backlog for MIIE v1.6, covering pull requests **PR-10** through **PR-13**. It translates the architectural specifications produced by PR-9 (OSMS, OPA, OPC, OPR, OVR, OBSERVATION_LIFECYCLE) into discrete, testable, merge-ready units of work.

Each PR specifies:

- **Goal** — the single outcome delivered.
- **Scope** — files created, modified, and tested.
- **Acceptance Criteria** — binary pass/fail conditions.
- **Dependencies** — prerequisite PRs and specifications.
- **Estimated Scope** — lines of code (LOC) new/modified.

---

## 2. Scope

| In Scope                                     | Out of Scope                                    |
| -------------------------------------------- | ----------------------------------------------- |
| Provider interface definitions (PR-10)       | New providers beyond GitProvider (PR-11 only)   |
| GitProvider extraction refactor (PR-11)      | Detector, scoring, or evidence engine changes   |
| Observation validation pipeline (PR-12)      | Performance optimization or caching             |
| Documentation and release finalization (PR-13) | CI/CD pipeline changes                          |

---

## 3. PR-9 Status Summary

PR-9 (Architecture Specifications) is currently in progress (Phases 2–10). It produces seven specification documents under `docs/specifications/v1.6/`:

| Spec Document                         | Content                                              | Status      |
| ------------------------------------- | ---------------------------------------------------- | ----------- |
| `OSMS.md`                            | Observation System Module Specification              | In Progress |
| `OPA.md`                             | Observation Provider Architecture                    | In Progress |
| `OPC.md`                             | Observation Provider Contracts                       | In Progress |
| `OPR.md`                             | Observation Provider Registry Specification          | In Progress |
| `OVR.md`                             | Observation Validation Rules                         | In Progress |
| `OBSERVATION_LIFECYCLE.md`           | End-to-end observation lifecycle documentation       | In Progress |
| `V1_6_IMPLEMENTATION_BACKLOG.md`     | This document                                       | Draft       |

PR-10 through PR-13 cannot begin until PR-9 delivers finalized specifications. This backlog assumes PR-9 is complete before any implementation work starts.

---

## 4. Pull Request Specifications

### 4.1 PR-10: Provider Interface Foundation

**Goal**: Define and implement the core provider interfaces and registry that all observation providers must implement.

#### 4.1.1 Rationale

The current extraction pipeline hardcodes `CommitExtractor` as the sole data source (`src/miie/processing/extraction/engine.py:22`). PR-10 introduces an abstraction layer so that additional providers (future file, branch, tag, or external-data providers) can be registered and discovered without modifying the extraction engine.

This directly implements the contracts defined in **OPC** (Observation Provider Contracts) and the registry pattern specified in **OPR** (Observation Provider Registry).

#### 4.1.2 Scope

| Action   | File                                                         | LOC Est. |
| -------- | ------------------------------------------------------------ | -------- |
| **New**  | `src/miie/contracts/observation_providers.py`               | ~200     |
| **New**  | `src/miie/processing/observation/registry.py`               | ~150     |
| **Modify** | `src/miie/contracts/interfaces.py` (add INT-19 through INT-23) | ~50      |
| **New**  | `tests/contracts/test_observation_providers.py`             | ~100     |
| **New**  | `tests/processing/observation/test_registry.py`             | ~100     |

**Estimated total**: ~400 LOC new, ~50 LOC modified.

#### 4.1.3 Interface Definitions

New interfaces follow existing conventions: `I` prefix, `@runtime_checkable` decorator, `Protocol` base class, Google-style docstrings with `Args`/`Returns`/`Raises` sections (see `src/miie/contracts/interfaces.py:26-60` for reference).

```python
# src/miie/contracts/observation_providers.py
# OPC §3–§7: Observation Provider Interfaces

@runtime_checkable
class IObservationProvider(Protocol):
    """OPC §3 — Core provider interface for observation extraction.

    Every data source (git, file system, external API) implements this
    protocol to produce ObservationCollections from a RepositoryContext.
    """

    PROVIDER_ID: str
    SUPPORTED_METRICS: frozenset[str]

    def extract(
        self,
        context: RepositoryContext,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        exclude_bots: bool = False,
        seed: Optional[int] = None,
    ) -> ObservationCollection:
        """Extract observations from the source.

        Args:
            context: RepositoryContext from ingestion.
            since: Inclusive start date filter.
            until: Inclusive end date filter.
            exclude_bots: Whether to exclude bot-authored sources.
            seed: Optional seed for deterministic provenance.

        Returns:
            ObservationCollection containing extracted observations.

        Raises:
            ExtractionError: If extraction fails.
        """
        ...

    def get_provider_id(self) -> str:
        """Return the unique provider identifier."""
        ...

    def get_supported_metrics(self) -> frozenset[str]:
        """Return the set of metric IDs this provider can produce."""
        ...


@runtime_checkable
class IObservationValidator(Protocol):
    """OPC §4 — Validation interface for post-extraction quality checks.

    Validates observations against per-metric rules defined in OVR.
    """

    def validate(self, observation: Observation) -> ValidationResult:
        """Validate a single observation.

        Args:
            observation: The observation to validate.

        Returns:
            ValidationResult with pass/fail and quality adjustment.
        """
        ...

    def validate_collection(
        self, collection: ObservationCollection
    ) -> ValidationReport:
        """Validate all observations in a collection.

        Args:
            collection: The collection to validate.

        Returns:
            ValidationReport with per-observation results.
        """
        ...


@runtime_checkable
class IObservationTransformer(Protocol):
    """OPC §5 — Transformation interface for observation post-processing.

    Applies quality adjustments, normalization, or derived-observation
    generation after validation.
    """

    def transform(
        self, observation: Observation, context: dict
    ) -> Observation:
        """Transform a single observation.

        Args:
            observation: The observation to transform.
            context: Additional context for transformation decisions.

        Returns:
            Transformed observation (may be the same instance if unchanged).
        """
        ...


@runtime_checkable
class IProviderHealthReporter(Protocol):
    """OPC §6 — Health reporting interface for provider monitoring.

    Providers implement this to expose operational health signals:
    success rate, latency, error counts, last successful extraction.
    """

    def report_health(self) -> ProviderHealth:
        """Return current provider health status.

        Returns:
            ProviderHealth with operational metrics.
        """
        ...

    def record_extraction(
        self, success: bool, duration_ms: float, error: Optional[str] = None
    ) -> None:
        """Record an extraction attempt for health tracking.

        Args:
            success: Whether the extraction succeeded.
            duration_ms: Extraction duration in milliseconds.
            error: Error message if the extraction failed.
        """
        ...


@runtime_checkable
class IProviderRegistry(Protocol):
    """OPC §7 / OPR §4 — Registry for observation provider discovery.

    Manages registration, lookup, and health-aware routing of providers.
    """

    def register(self, provider: IObservationProvider) -> None:
        """Register a provider.

        Args:
            provider: Provider instance to register.

        Raises:
            ValueError: If a provider with the same ID is already registered.
        """
        ...

    def get_by_metric(self, metric_id: str) -> List[IObservationProvider]:
        """Return providers that support the given metric, ordered by health.

        Args:
            metric_id: The metric identifier (e.g., 'M-02').

        Returns:
            List of providers supporting this metric.
        """
        ...

    def get_primary(self, metric_id: str) -> Optional[IObservationProvider]:
        """Return the healthiest provider for a metric.

        Args:
            metric_id: The metric identifier.

        Returns:
            The primary provider, or None if no provider supports this metric.
        """
        ...

    def get_fallback(self, metric_id: str) -> Optional[IObservationProvider]:
        """Return a fallback provider when the primary is unhealthy.

        Args:
            metric_id: The metric identifier.

        Returns:
            A fallback provider, or None.
        """
        ...

    def health_check(self) -> Dict[str, ProviderHealth]:
        """Run health checks on all registered providers.

        Returns:
            Mapping of provider ID to health status.
        """
        ...
```

#### 4.1.4 Registry Implementation

The `ObservationProviderRegistry` in `src/miie/processing/observation/registry.py` implements `IProviderRegistry`. It follows the same pattern as the existing `DetectorRegistry` (`src/miie/processing/detection/registry.py`):

- Internal `_providers: Dict[str, IObservationProvider]` keyed by `PROVIDER_ID`.
- Internal `_metric_index: Dict[str, List[str]]` mapping metric IDs to provider IDs.
- `register()` validates `PROVIDER_ID` uniqueness and indexes `SUPPORTED_METRICS`.
- `get_by_metric()` returns providers sorted by health score (descending).
- `get_primary()` returns the first result from `get_by_metric()`.
- `get_fallback()` returns the second result, or `None`.
- `health_check()` delegates to each provider's `IProviderHealthReporter.report_health()`.

#### 4.1.5 Data Types

New dataclasses added to `src/miie/contracts/observation_providers.py`:

```python
@dataclass(frozen=True)
class ValidationResult:
    """Result of validating a single observation."""
    observation_id: str
    passed: bool
    quality_adjustment: Optional[str]  # e.g., "complete" → "estimated"
    confidence_delta: float  # [-1.0, 1.0]
    error_message: Optional[str] = None

@dataclass(frozen=True)
class ValidationReport:
    """Aggregate result of validating an ObservationCollection."""
    total_validated: int
    total_passed: int
    total_failed: int
    results: List[ValidationResult]
    warnings: List[str]

@dataclass(frozen=True)
class ProviderHealth:
    """Health status of an observation provider."""
    provider_id: str
    is_healthy: bool
    success_rate: float  # [0.0, 1.0]
    avg_latency_ms: float
    last_success_timestamp: Optional[str]
    consecutive_failures: int
```

#### 4.1.6 Acceptance Criteria

| # | Criterion                                                     | Verification           |
| - | ------------------------------------------------------------- | ---------------------- |
| 1 | `IObservationProvider` Protocol defined with typed signatures | Code review, mypy      |
| 2 | `ObservationProviderRegistry` implements register/get_by_metric/get_primary/get_fallback/health_check | Unit tests |
| 3 | All new interfaces follow I-prefix, Protocol base conventions | Code review            |
| 4 | 100% test coverage for new interfaces                         | `pytest --cov`         |
| 5 | All existing tests still pass (44/44)                         | `pytest tests/`        |
| 6 | Black, isort, flake8 clean                                    | `black --check .`, `isort --check .`, `flake8` |

#### 4.1.7 Dependencies

- **PR-9 complete** — all specification documents finalized.
- **No code dependencies** — entirely new files; no existing behavior is modified.

---

### 4.2 PR-11: Git Provider Extraction

**Goal**: Extract the existing `CommitExtractor` logic into a `GitProvider` class that implements `IObservationProvider`, then wire the extraction engine to use the provider registry.

#### 4.2.1 Rationale

`CommitExtractor` (`src/miie/processing/extraction/commit_extractor.py`) currently owns both the git-parsing logic and the `ObservationCollection` construction. PR-11 separates these concerns:

1. `GitProvider` wraps the git-parsing logic and implements `IObservationProvider`.
2. `CommitExtractor` is refactored to delegate to `GitProvider` internally, preserving its existing public API for backward compatibility.
3. `ExtractionEngine` is modified to discover `GitProvider` through the registry, with a hardcoded fallback for v1.5 compatibility.

This implements the extraction flow defined in **OPA** (Observation Provider Architecture) §5.

#### 4.2.2 Scope

| Action    | File                                                              | LOC Est. |
| --------- | ----------------------------------------------------------------- | -------- |
| **New**   | `src/miie/processing/observation/providers/__init__.py`          | ~5       |
| **New**   | `src/miie/processing/observation/providers/git_provider.py`      | ~300     |
| **Modify** | `src/miie/processing/extraction/commit_extractor.py`             | ~100 refactored |
| **Modify** | `src/miie/processing/extraction/engine.py`                       | ~100 modified |
| **New**   | `tests/processing/observation/providers/__init__.py`             | ~1       |
| **New**   | `tests/processing/observation/providers/test_git_provider.py`    | ~150     |
| **Modify** | `tests/unit/test_extraction_engine.py`                           | ~50 modified |

**Estimated total**: ~300 LOC new, ~200 LOC refactored/modified.

#### 4.2.3 GitProvider Design

```python
# src/miie/processing/observation/providers/git_provider.py

class GitProvider:
    """IObservationProvider backed by git commit history.

    Extracts M-02 (Commit Frequency) and M-06 (Code Churn) observations
    from the git log. This is the primary provider for commit-derived metrics.

    Implements IObservationProvider and IProviderHealthReporter.
    """

    PROVIDER_ID = "git_provider.v1"
    SUPPORTED_METRICS = frozenset({"M-02", "M-06"})

    def __init__(self) -> None:
        self._health = ProviderHealth(
            provider_id=self.PROVIDER_ID,
            is_healthy=True,
            success_rate=1.0,
            avg_latency_ms=0.0,
            last_success_timestamp=None,
            consecutive_failures=0,
        )
        self._extraction_count = 0
        self._total_duration_ms = 0.0

    def extract(
        self,
        context: RepositoryContext,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        exclude_bots: bool = False,
        seed: Optional[int] = None,
    ) -> ObservationCollection:
        """Extract observations from git commit history.

        Delegates git parsing to internal methods (migrated from
        CommitExtractor._parse_git_log and _parse_log_output).
        """
        ...

    def get_provider_id(self) -> str:
        return self.PROVIDER_ID

    def get_supported_metrics(self) -> frozenset[str]:
        return self.SUPPORTED_METRICS

    def report_health(self) -> ProviderHealth:
        return self._health

    def record_extraction(
        self, success: bool, duration_ms: float, error: Optional[str] = None
    ) -> None:
        """Update health tracking after an extraction attempt."""
        ...
```

#### 4.2.4 CommitExtractor Refactor

The existing `CommitExtractor` class is refactored to delegate to `GitProvider` internally:

```python
class CommitExtractor:
    """Extract observations from git commit history.

    v1.6: Delegates to GitProvider internally. Public API unchanged.
    """

    EXTRACTOR_ID = "commit_extractor.v1"

    def __init__(self, *, provider: Optional[GitProvider] = None) -> None:
        self._provider = provider or GitProvider()

    def extract_commits(
        self,
        context: Any,
        since: Optional[datetime.datetime] = None,
        until: Optional[datetime.datetime] = None,
        exclude_bots: bool = False,
        seed: Optional[int] = None,
    ) -> ObservationCollection:
        """Extract observations — delegates to GitProvider."""
        return self._provider.extract(
            context, since=since, until=until,
            exclude_bots=exclude_bots, seed=seed,
        )
```

Internal git-parsing methods (`_parse_git_log`, `_parse_log_output`, `_build_window`, `_empty_collection`) are migrated to `GitProvider`. The `CommitExtractor` class retains its public interface unchanged so existing callers and tests continue to work.

#### 4.2.5 ExtractionEngine Modification

The `ExtractionEngine` (`src/miie/processing/extraction/engine.py`) is modified to accept an optional `IProviderRegistry`:

```python
class ExtractionEngine:
    def __init__(
        self,
        *,
        store: Optional[ObservationStore] = None,
        commit_extractor: Optional[CommitExtractor] = None,
        metric_extractor: Optional[MetricExtractor] = None,
        provider_registry: Optional[IProviderRegistry] = None,
    ) -> None:
        self._store = store
        self._commit_extractor = commit_extractor or CommitExtractor()
        self._metric_extractor = metric_extractor or MetricExtractor()
        self._provider_registry = provider_registry

    def extract(self, context, metric_list, ...):
        # Phase 1: Discover provider from registry, fallback to CommitExtractor
        if self._provider_registry is not None:
            provider = self._provider_registry.get_primary("M-02")
            if provider is not None:
                collection = provider.extract(
                    context, since=since, until=until,
                    exclude_bots=exclude_bots, seed=seed,
                )
            else:
                collection = self._commit_extractor.extract_commits(...)
        else:
            collection = self._commit_extractor.extract_commits(...)
        # ... rest unchanged
```

Backward compatibility: When `provider_registry` is `None` (the default), the engine behaves identically to v1.5.

#### 4.2.6 Acceptance Criteria

| #  | Criterion                                                                       | Verification           |
| -- | ------------------------------------------------------------------------------- | ---------------------- |
| 1  | `GitProvider` implements `IObservationProvider` fully                           | `isinstance()` check, tests |
| 2  | `GitProvider` produces identical `ObservationCollection` to current `CommitExtractor` | Parity test (diff output) |
| 3  | `ExtractionEngine` uses provider registry to discover `GitProvider`             | Unit test with mock registry |
| 4  | `ExtractionEngine` falls back to hardcoded `CommitExtractor` if registry empty  | Unit test with `None` registry |
| 5  | All existing extraction tests pass unchanged                                    | `pytest tests/unit/test_extraction_engine.py` |
| 6  | New `GitProvider` tests cover: happy path, missing repo, invalid git, timeout   | `tests/processing/observation/providers/test_git_provider.py` |
| 7  | Black, isort, flake8 clean                                                      | Linting tools          |

#### 4.2.7 Dependencies

- **PR-10** — `IObservationProvider`, `IProviderRegistry`, `ProviderHealth` interfaces and `ObservationProviderRegistry` implementation.
- **PR-11 can begin immediately after PR-10 merges.**

---

### 4.3 PR-12: Observation Validation Pipeline

**Goal**: Implement the observation validation system per the OVR (Observation Validation Rules) specification.

#### 4.3.1 Rationale

Currently, observations pass through `Observation.__post_init__` validation (schema-level constraints in `src/miie/processing/observation/models.py:221-266`) but receive no semantic validation. OVR defines per-metric rules that enforce quality guarantees beyond schema correctness — for example, M-02 observations must have integer values, M-06 observations must be non-negative, and quality transitions must follow a defined state machine.

PR-12 adds a validation layer that runs after observation creation and before downstream consumption.

#### 4.3.2 Scope

| Action    | File                                                    | LOC Est. |
| --------- | ------------------------------------------------------- | -------- |
| **New**   | `src/miie/processing/observation/validation.py`         | ~200     |
| **New**   | `src/miie/processing/observation/quality.py`            | ~150     |
| **Modify** | `src/miie/processing/extraction/commit_extractor.py`   | ~30      |
| **Modify** | `src/miie/processing/extraction/metric_extractor.py`   | ~20      |
| **New**   | `tests/processing/observation/test_validation.py`       | ~150     |
| **New**   | `tests/processing/observation/test_quality.py`          | ~100     |

**Estimated total**: ~350 LOC new, ~100 LOC modified.

#### 4.3.3 Validation Rules (per OVR)

The `ObservationValidator` implements per-metric validation rules. Each rule returns a `ValidationResult` with pass/fail, quality adjustment, and confidence delta.

| Metric | Rule ID | Validation Rule                                                                                       | Failure Action           |
| ------ | ------- | ----------------------------------------------------------------------------------------------------- | ------------------------ |
| M-01   | VR-01   | Value must be in [0.0, 1.0]; unit must be "ratio"                                                    | quality → "estimated"    |
| M-02   | VR-02   | Value must be a non-negative integer; unit must be "count"                                            | quality → "estimated"    |
| M-03   | VR-03   | Value must be in [0.0, 1.0]; unit must be "ratio"                                                    | quality → "estimated"    |
| M-04   | VR-04   | Value must be in [0.0, 1.0]; unit must be "ratio"                                                    | quality → "estimated"    |
| M-05   | VR-05   | Value must be >= 0.0; unit must be "hours"                                                            | quality → "estimated"    |
| M-06   | VR-06   | Value must be >= 0.0; unit must be "ratio"                                                            | quality → "estimated"    |
| M-07   | VR-07   | Value must be in [0.0, 1.0]; unit must be "ratio"                                                    | quality → "estimated"    |
| All    | VR-08   | Timestamp must be parseable ISO-8601; must not be in the future                                       | reject observation       |
| All    | VR-09   | Provenance extractor_id must be non-empty                                                             | quality → "estimated"    |
| All    | VR-10   | Observation ID must match deterministic SHA-256 derivation (ODSS §10.2)                              | reject observation       |

#### 4.3.4 Validation Implementation

```python
# src/miie/processing/observation/validation.py

class ObservationValidator:
    """Per-metric observation validation per OVR specification.

    Runs validation rules after observation creation. Invalid observations
    are logged with full provenance and excluded from the downstream pipeline.
    """

    def __init__(self, strict: bool = False) -> None:
        """Initialize validator.

        Args:
            strict: If True, invalid observations raise ObservationError.
                    If False (default), they are logged and quality-adjusted.
        """
        self._strict = strict
        self._rules: Dict[str, List[Callable]] = self._build_rule_table()

    def validate(self, observation: Observation) -> ValidationResult:
        """Validate a single observation against metric-specific rules.

        Args:
            observation: The observation to validate.

        Returns:
            ValidationResult with pass/fail, quality_adjustment, confidence_delta.
        """
        ...

    def validate_collection(
        self, collection: ObservationCollection
    ) -> ValidationReport:
        """Validate all observations across all windows in a collection.

        Args:
            collection: The ObservationCollection to validate.

        Returns:
            ValidationReport with per-observation results and aggregate stats.
        """
        ...
```

#### 4.3.5 Quality State Machine

The `QualityStateMachine` (`src/miie/processing/observation/quality.py`) enforces valid quality transitions:

```
Quality States: complete, estimated, missing, derived

Valid Transitions:
  complete   → estimated    (confidence downgrade on rule failure)
  complete   → missing      (data gap detected)
  estimated  → complete     (data verified post-hoc)
  estimated  → missing      (data gap detected)
  missing    → estimated    (inference applied)
  missing    → derived      (derived from other observations)
  derived    → estimated    (source data becomes available)
  derived    → complete     (source data verified)

Invalid Transitions (raise QualityTransitionError):
  complete   → derived      (skip estimated/missing)
  estimated  → derived      (must go through missing)
  missing    → complete     (skip estimated)
```

```python
# src/miie/processing/observation/quality.py

class QualityStateMachine:
    """ODSS §14 — Enforces valid quality state transitions.

    Tracks quality state per observation and validates that transitions
    follow the defined state machine rules.
    """

    _VALID_TRANSITIONS: Dict[str, frozenset[str]] = {
        "complete":  frozenset({"estimated", "missing"}),
        "estimated": frozenset({"complete", "missing"}),
        "missing":   frozenset({"estimated", "derived"}),
        "derived":   frozenset({"estimated", "complete"}),
    }

    def transition(
        self,
        observation_id: str,
        current_quality: str,
        target_quality: str,
    ) -> str:
        """Attempt a quality transition.

        Args:
            observation_id: ID of the observation (for error messages).
            current_quality: Current quality state.
            target_quality: Desired quality state.

        Returns:
            The resulting quality state (may differ from target if transition
            is invalid and strict=False).

        Raises:
            QualityTransitionError: If strict=True and transition is invalid.
        """
        ...

    def get_valid_targets(self, current_quality: str) -> frozenset[str]:
        """Return valid target states from the given current state."""
        ...
```

#### 4.3.6 Integration Points

Validation is integrated into the extraction pipeline at two points:

1. **After `CommitExtractor` / `GitProvider` extraction** (`commit_extractor.py`): Validate each observation immediately after creation, before appending to the window.

2. **Before `MetricExtractor` transformation** (`metric_extractor.py`): Validate the full collection before aggregation, filtering out invalid observations.

Invalid observations are:
- Logged with full provenance (observation ID, metric, rule ID, failure reason).
- Quality-adjusted (e.g., "complete" → "estimated") or excluded.
- Excluded from downstream MetricDataFrame generation.
- Added `confidence_adjustment` field to observation extensions.

#### 4.3.7 Acceptance Criteria

| #  | Criterion                                                                    | Verification           |
| -- | ---------------------------------------------------------------------------- | ---------------------- |
| 1  | `ObservationValidator` validates all 7 metrics per OVR rules                | Unit tests per metric  |
| 2  | `QualityStateMachine` handles all valid quality transitions                 | Unit tests per transition |
| 3  | Validation runs automatically after observation creation                     | Integration test       |
| 4  | Invalid observations logged with provenance and excluded from pipeline       | Integration test       |
| 5  | Validation adds `confidence_adjustment` field to observations                | Unit test              |
| 6  | All existing tests pass unchanged                                            | `pytest tests/`        |
| 7  | New validation tests cover all metrics, all quality states, edge cases       | Coverage report        |
| 8  | Black, isort, flake8 clean                                                   | Linting tools          |

#### 4.3.8 Dependencies

- **PR-10** — `IObservationValidator` interface, `ValidationResult`, `ValidationReport` types.
- **PR-11** — `GitProvider` needed for realistic integration testing (validation is tested against actual extraction output).

---

### 4.4 PR-13: Documentation and Release

**Goal**: Finalize v1.6 documentation, update changelog, bump version, and prepare for release.

#### 4.4.1 Scope

| Action    | File                                      | LOC Est. |
| --------- | ----------------------------------------- | -------- |
| **Modify** | `CHANGELOG.md`                           | ~80      |
| **Modify** | `README.md`                              | ~20      |
| **New**   | `docs/OBSERVATION_ENGINE.md`             | ~200     |
| **Modify** | `src/miie/__init__.py`                   | ~1       |
| **Verify** | Full test suite                           | 0        |

**Estimated total**: ~200 LOC documentation, ~10 LOC version bump.

#### 4.4.2 Changelog Entries

```markdown
## [1.6.0] - 2026-XX-XX

### Added
- Provider interface foundation (INT-19 through INT-23):
  - `IObservationProvider` protocol for data source abstraction
  - `IObservationValidator` protocol for observation validation
  - `IObservationTransformer` protocol for post-validation transformation
  - `IProviderHealthReporter` protocol for provider health monitoring
  - `IProviderRegistry` protocol for provider discovery and routing
- `ObservationProviderRegistry` implementation with metric-indexed lookup
- `GitProvider` implementing `IObservationProvider` for git commit extraction
- `ObservationValidator` with per-metric validation rules (VR-01 through VR-10)
- `QualityStateMachine` enforcing valid quality state transitions
- Observation engine documentation (`docs/OBSERVATION_ENGINE.md`)

### Changed
- `ExtractionEngine` now accepts optional `IProviderRegistry` for provider discovery
- `CommitExtractor` delegates to `GitProvider` internally (public API unchanged)
- Validation runs automatically after observation creation
- Version bumped to 1.6.0

### Fixed
- (none)

### Deprecated
- (none)

### Removed
- (none)
```

#### 4.4.3 Observation Engine Documentation

`docs/OBSERVATION_ENGINE.md` covers:

1. **Overview** — what the observation engine does and why it matters.
2. **Metrics** — table of all 7 metrics (M-01 through M-07) with units, sources, and validation rules.
3. **Providers** — how to implement `IObservationProvider`, register with the registry, and handle health reporting.
4. **Lifecycle** — end-to-end flow from extraction through validation to MetricDataFrame.
5. **Quality States** — state machine diagram and transition rules.
6. **Validation** — per-metric rules (VR-01 through VR-10) and failure handling.
7. **Troubleshooting** — common issues, error codes, and debugging steps.
8. **Migration from v1.5** — what changed and how to update existing code.

#### 4.4.4 Version Bump

```python
# src/miie/__init__.py
__version__ = "1.6.0"
```

#### 4.4.5 Acceptance Criteria

| #  | Criterion                                                            | Verification              |
| -- | -------------------------------------------------------------------- | ------------------------- |
| 1  | `CHANGELOG.md` documents all v1.6 changes with proper categorization | Manual review             |
| 2  | `README.md` links to new observation engine documentation            | Link check                |
| 3  | `OBSERVATION_ENGINE.md` covers metrics, providers, lifecycle, troubleshooting | Manual review       |
| 4  | Version bumped to 1.6.0                                             | `python -c "import miie; print(miie.__version__)"` |
| 5  | All 44+ tests pass                                                  | `pytest tests/`           |
| 6  | Documentation builds without errors                                  | Build verification        |
| 7  | Black, isort, flake8 clean                                          | Linting tools             |

#### 4.4.6 Dependencies

- **PR-10, PR-11, PR-12 all complete** — documentation describes the implemented system.

---

## 5. Dependency Graph

```
PR-9 (Architecture)
    │
    ▼
PR-10 (Provider Interfaces)
    │
    ├──► PR-11 (Git Provider Extraction)
    │         │
    │         ▼
    └──► PR-12 (Validation Pipeline)
              │
              ▼
         PR-13 (Documentation & Release)
```

PR-11 and PR-12 can be developed in **parallel** after PR-10 merges, as they touch different files:

| PR-11 files                        | PR-12 files                         |
| ---------------------------------- | ----------------------------------- |
| `providers/git_provider.py`        | `validation.py`                     |
| `extraction/commit_extractor.py`   | `quality.py`                        |
| `extraction/engine.py`             | `extraction/commit_extractor.py`    |

**Note**: Both PR-11 and PR-12 modify `commit_extractor.py`. If developed in parallel, PR-12 should branch from PR-11's branch to avoid merge conflicts, or the modifications should be coordinated to touch different sections of the file.

**Recommended merge order**: PR-10 → PR-11 → PR-12 → PR-13 (sequential to avoid conflicts).

---

## 6. Estimated Scope and Timeline

| PR     | New LOC | Modified LOC | Files Created | Files Modified | Risk   | Est. Days |
| ------ | ------- | ------------ | ------------- | -------------- | ------ | --------- |
| PR-10  | ~400    | ~50          | 4             | 1              | Low    | 2–3       |
| PR-11  | ~300    | ~200         | 3             | 3              | Medium | 3–4       |
| PR-12  | ~350    | ~100         | 4             | 2              | Low    | 2–3       |
| PR-13  | ~200    | ~10          | 1             | 3              | Low    | 1–2       |
| **Total** | **~1250** | **~360**  | **12**        | **9**          |        | **8–12**  |

---

## 7. Risk Assessment

### 7.1 PR-10: Low Risk

- **Nature**: Entirely new interfaces; no existing behavior changes.
- **Mitigation**: Follow existing interface conventions exactly; comprehensive unit tests.

### 7.2 PR-11: Medium Risk

- **Nature**: Refactoring extraction engine and commit extractor.
- **Key Risk**: Breaking the extraction pipeline, which is exercised by 6+ integration tests.
- **Mitigation**:
  - Parity test: `GitProvider.extract()` must produce byte-identical `ObservationCollection` to current `CommitExtractor.extract_commits()`.
  - Backward compatibility: `ExtractionEngine` defaults to `CommitExtractor` when no registry is provided.
  - All existing extraction tests must pass unchanged before merging.

### 7.3 PR-12: Low Risk

- **Nature**: New validation layer; additive only.
- **Mitigation**: Validation is opt-in at the engine level; defaults to non-strict mode (log-and-adjust, not raise).

### 7.4 PR-13: Low Risk

- **Nature**: Documentation and version bump.
- **Mitigation**: Full test suite verification; documentation reviewed for accuracy against implemented code.

---

## 8. Success Criteria

The v1.6 release is successful when:

1. All 44+ existing tests pass without modification (backward compatibility preserved).
2. New test suite adds 30+ tests for provider interfaces, registry, GitProvider, validation, and quality state machine.
3. `GitProvider` produces identical output to `CommitExtractor` for the same input.
4. Validation pipeline catches all OVR-defined rule violations.
5. Documentation accurately describes the implemented system.
6. Version is 1.6.0.
7. All linting tools pass (black, isort, flake8).

---

## 9. Cross-References

| Specification | Abbreviation | Relevant PR | Section in This Document |
| ------------- | ------------ | ----------- | ------------------------ |
| Observation System Module Specification | OSMS | PR-10, PR-11, PR-12 | §4.1–§4.3 |
| Observation Provider Architecture | OPA | PR-10, PR-11 | §4.1.1, §4.2.1 |
| Observation Provider Contracts | OPC | PR-10 | §4.1.3 |
| Observation Provider Registry | OPR | PR-10 | §4.1.4 |
| Observation Validation Rules | OVR | PR-12 | §4.3.3 |
| Observation Lifecycle | OBSERVATION_LIFECYCLE | PR-11, PR-12 | §4.2.5, §4.3.6 |
| Interface Contract Specification (ACS) | ACS | PR-10 | §4.1.3 (INT-19 through INT-23) |
| Observation Data Schema Specification (ODSS) | ODSS | PR-11, PR-12 | §4.2.3, §4.3.5 |

---

*End of V1_6_IMPLEMENTATION_BACKLOG.md*
