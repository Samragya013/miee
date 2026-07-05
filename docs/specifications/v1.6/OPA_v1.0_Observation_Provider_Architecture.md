# Observation Provider Architecture (OPA) v1.0

**MIIE v1.6 — Provider Abstraction Layer Specification**

| Field | Value |
|-------|-------|
| Document ID | OPA-v1.0 |
| Version | 1.0.0 |
| Date | 2026-07-03 |
| Classification | Internal Engineering Architecture Specification |
| Status | Canonical Architecture Standard |
| Baseline | v1.0.1 (tag `4c4d5e6`) |
| Supersedes | None (new) |
| Dependencies | OEAS-v1.5, ODSS-v1.0, DES-v2.0, IMS-v1.0 |
| Related Documents | OSMS-v1.0, OPC-v1.0, OPR-v1.0 |

### Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-07-03 | MIIE Engineering | Initial specification |

---

## Table of Contents

1. [Document Metadata](#1-document-metadata)
2. [Purpose](#2-purpose)
3. [Scope](#3-scope)
4. [Objectives](#4-objectives)
5. [Non-Objectives](#5-non-objectives)
6. [Architectural Principles](#6-architectural-principles)
7. [Current System Analysis](#7-current-system-analysis)
8. [Provider Abstraction Layer Design](#8-provider-abstraction-layer-design)
9. [Provider Contract (`IObservationProvider`)](#9-provider-contract-iobservationprovider)
10. [Provider Lifecycle](#10-provider-lifecycle)
11. [Provider Type Hierarchy](#11-provider-type-hierarchy)
12. [Provider Registry](#12-provider-registry)
13. [Dependency Injection and IoC](#13-dependency-injection-and-ioc)
14. [Integration with ExtractionEngine](#14-integration-with-extractionengine)
15. [Provider Observability](#15-provider-observability)
16. [Provider Health and Fallback](#16-provider-health-and-fallback)
17. [Error Handling](#17-error-handling)
18. [Backward Compatibility Strategy](#18-backward-compatibility-strategy)
19. [Security Considerations](#19-security-considerations)
20. [Performance Architecture](#20-performance-architecture)
21. [Configuration Architecture](#21-configuration-architecture)
22. [Architectural Invariants](#22-architectural-invariants)
23. [Tradeoff Analysis](#23-tradeoff-analysis)
24. [Risk Analysis](#24-risk-analysis)
25. [Acceptance Criteria](#25-acceptance-criteria)
26. [Glossary](#26-glossary)
27. [Appendix](#27-appendix)

---

## 1. Document Metadata

### 1.1 Cross-Reference Matrix

This specification is derived from and references the following MIIE architecture documents:

| Document | Relationship | Referenced Sections |
|----------|-------------|---------------------|
| OEAS-v1.5 | Observation Engine layer the providers feed | §14, §21, §29 |
| ODSS-v1.0 | Observation data model providers must produce | §7, §8, §9, §19, §22 |
| DES-v2.0 | Detector execution consuming provider output | §9, §13, §16 |
| IMS-v1.0 | Implementation phases this architecture extends | Phase 3 |
| OSMS-v1.0 | Observation Schema Management (schema evolution) | §3, §5 |
| OPC-v1.0 | Observation Pipeline Configuration | §4, §7 |
| OPR-v1.0 | Observation Processing Runtime | §6, §8 |

### 1.2 Interface Identifier Registry

| Interface | ID | Section | Status |
|-----------|-----|---------|--------|
| `IObservationProvider` | PRV-01 | §9 | New (v1.6) |
| `IGitProvider` | PRV-02 | §11.1 | New (v1.6) |
| `IStaticAnalysisProvider` | PRV-03 | §11.2 | New (v1.6) |
| `ICICDProvider` | PRV-04 | §11.3 | New (v1.6) |
| `IRepositoryMetadataProvider` | PRV-05 | §11.4 | New (v1.6) |
| `IFileAnalysisProvider` | PRV-06 | §11.5 | New (v1.6) |
| `IProviderRegistry` | PRV-07 | §12 | New (v1.6) |
| `IExtractionEngine` | INT-02 | interfaces.py:63 | Existing |
| `IObservationStore` | STR-01 | interfaces.py:363 | Existing |

---

## 2. Purpose

This document specifies the **Observation Provider Architecture** for MIIE v1.6. It defines:

- The typed provider abstraction layer that decouples the Observation Engine from specific data sources
- The `IObservationProvider` Protocol interface that all providers implement
- The provider lifecycle from registration through health check, extraction, transformation, and validation
- The provider type hierarchy covering git, static analysis, CI/CD, repository metadata, and file analysis sources
- The provider registry for discovery, priority ordering, and health monitoring
- The dependency injection pattern that enables provider composition
- The integration contract with the existing `ExtractionEngine`
- The backward compatibility strategy that preserves existing `CommitExtractor` behavior

The OPA exists because MIIE v1.5 hardcodes observation creation to a single data source — git commit history via `CommitExtractor`. This limits the system to metrics derivable from git log output alone (M-02, M-06), leaving five of seven metrics (M-01, M-03, M-04, M-05, M-07) without observation-level extraction. The v1.6 provider architecture generalizes observation creation so any data source can participate in the observation pipeline through a typed, composable, observable interface.

This document is implementation-independent. It specifies *what* must exist and *why*, not *how* to code it. An engineer implementing the provider system must follow this specification precisely. Deviations require an Architecture Decision Record (ADR) and approval from the architecture owner.

---

## 3. Scope

### 3.1 In Scope

| Component | Scope |
|-----------|-------|
| `IObservationProvider` Protocol | Complete interface contract for all observation providers |
| Provider type hierarchy | Typed specializations for each data source class |
| Provider registry | Central discovery, registration, priority, and health tracking |
| Provider lifecycle | Full lifecycle from registration to extraction to validation |
| ExtractionEngine integration | How providers compose within the existing orchestration layer |
| Backward compatibility | CommitExtractor preserved as `IGitProvider` implementation |
| Error handling | Provider failure modes, partial extraction, graceful degradation |
| Observability | Provider health, latency, confidence, and provenance tracking |

### 3.2 Out of Scope

| Component | Reason |
|-----------|--------|
| Individual provider implementations | Each provider has its own implementation specification |
| Window Builder modifications | Covered by OSMS-v1.0 |
| Detector changes | Covered by DES-v2.0 |
| Schema evolution | Covered by OSMS-v1.0 |
| Pipeline configuration | Covered by OPC-v1.0 |
| Runtime orchestration details | Covered by OPR-v1.0 |

---

## 4. Objectives

1. **Provider Agnosticism**: The Observation Engine must operate identically regardless of which providers are registered.
2. **Typed Contracts**: Every provider implements a strict `Protocol` interface with compile-time type checking.
3. **Composability**: Multiple providers can contribute observations to the same `ObservationCollection`.
4. **Observability**: Provider health, extraction latency, and observation confidence are tracked and queryable.
5. **Backward Compatibility**: Existing `CommitExtractor` behavior is preserved as a provider implementation.
6. **Extensibility**: New data sources can be added without modifying the Observation Engine core.

---

## 5. Non-Objectives

1. **Provider implementations**: This document specifies interfaces and contracts, not concrete implementations beyond the backward-compatible `CommitExtractor` adapter.
2. **Metric redefinition**: Metric definitions (M-01 through M-07) are defined by ODSS-v1.0 §11 and are not modified here.
3. **Window construction**: How providers' observations are partitioned into windows is the responsibility of the Window Builder (OEAS §18, OSMS-v1.0).
4. **Detector adaptation**: How detector adapters consume provider output is defined by DES-v2.0 §16.

---

## 6. Architectural Principles

### P1 — Inversion of Control (IoC)

The Observation Engine must never depend on concrete provider implementations. It depends only on the `IObservationProvider` Protocol. Providers are injected into the engine, not discovered at import time.

**Rationale**: Enables testing with mock providers, swapping providers without engine changes, and independent provider development.

### P2 — Single Responsibility

Each provider produces observations for exactly one data source type. A git provider extracts from git; a CI/CD provider extracts from pipeline APIs. No provider combines multiple data sources.

**Rationale**: Simplifies testing, reasoning about failure modes, and understanding data provenance.

### P3 — Provider Agnosticism

The Observation Engine cannot distinguish between observations from different providers. Once extracted, an observation is an observation regardless of its source.

**Rationale**: Enables detector code to remain unchanged as new providers are added.

### P4 — Typed Contracts

Every provider-to-engine interaction uses typed Protocol interfaces. No `Dict[str, Any]` passes across provider boundaries. All data structures are frozen dataclasses or typed containers.

**Rationale**: Compile-time type checking catches interface violations before runtime.

### P5 — Composability

Multiple providers can feed observations into the same `ObservationCollection`. The engine merges observations from all providers, deduplicates by `(source_type, source_id, metric_id)`, and presents a unified view.

**Rationale**: Real-world repositories have data from multiple sources (git, CI, static analysis) that all contribute to the same metrics.

### P6 — Observable Health

Every provider tracks its own health status, extraction latency, and observation confidence. The registry aggregates these for monitoring and fallback decisions.

**Rationale**: A failing provider must not silently produce incomplete data. Health visibility enables proactive intervention.

### P7 — Backward Compatibility

Existing `CommitExtractor` behavior is preserved as an `IGitProvider` implementation. No existing tests, CLI commands, or pipeline stages break due to the provider abstraction.

**Rationale**: The v1.6 provider layer is additive, not transformative. The system continues to work identically for git-only extraction.

---

## 7. Current System Analysis

### 7.1 ExtractionPipeline (v1.5)

The v1.5 extraction pipeline is a two-phase process:

```
Phase 1: CommitExtractor.extract_commits()
    ├── Input: RepositoryContext
    ├── Process: git log → parse commits → create Observation objects
    ├── Output: ObservationCollection
    └── Metrics: M-02 (commit frequency), M-06 (code churn)

Phase 2: MetricExtractor.extract_metrics()
    ├── Input: ObservationCollection, metric_list
    ├── Process: group observations → compute aggregated values
    └── Output: MetricDataFrame
```

The `ExtractionEngine` (`src/miie/processing/extraction/engine.py:28`) orchestrates both phases in sequence.

### 7.2 Limitations

| Limitation | Impact |
|-----------|--------|
| `CommitExtractor` is hardcoded to git log via subprocess | No way to inject alternative data sources |
| `EXTRACTOR_ID = "commit_extractor.v1"` is a single fixed string | Cannot distinguish between providers of the same metric |
| `_GIT_METRICS = frozenset({"M-02", "M-06"})` is hardcoded | M-01, M-03–M-05, M-07 have no provider |
| No health tracking or fallback mechanism | A failing provider produces empty collections silently |
| No confidence tracking per observation | Downstream detectors cannot weight observations by source reliability |

### 7.3 Existing Interface Contracts

The v1.5 codebase defines 18 Protocol interfaces in `src/miie/contracts/interfaces.py`:

| Interface | ID | Purpose |
|-----------|-----|---------|
| `IIngestionEngine` | INT-01 | Repository ingestion |
| `IExtractionEngine` | INT-02 | Metric extraction |
| `ISegmentationEngine` | INT-03 | Window segmentation |
| `IDetectorEngine` | INT-04 | Detector invocation |
| `IScoringEngine` | INT-05 | Score computation |
| `IEvidenceEngine` | INT-06 | Evidence generation |
| `IExplanationEngine` | INT-07 | Explanation generation |
| `IReportGenerator` | INT-08 | Report generation |
| `IBenchmarkEngine` | INT-09 | Benchmark execution |
| `IEvaluationEngine` | INT-10 | Evaluation |
| `IObservationStore` | STR-01 | Observation storage |
| `IWindowBuilder` | WIN-01 | Window construction |
| `IDetectorAdapter` | ADP-01 | Detector translation |

**Not yet defined**: `IObservationProvider` — this is what OPA v1.0 adds (PRV-01).

---

## 8. Provider Abstraction Layer Design

### 8.1 Architectural Position

The provider abstraction layer sits between the `ExtractionEngine` and individual data source extractors:

```
┌─────────────────────────────────────────────────────────┐
│                    ExtractionEngine                      │
│              (src/miie/processing/extraction/engine.py)  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌───────────────────────────────────────────┐         │
│   │        ProviderRegistry (PRV-07)          │         │
│   │  ┌─────────┐ ┌──────────┐ ┌───────────┐  │         │
│   │  │ Provider │ │ Provider │ │ Provider  │  │         │
│   │  │  M-02    │ │  M-03    │ │  M-04     │  │         │
│   │  └────┬─────┘ └────┬─────┘ └─────┬─────┘  │         │
│   └───────┼─────────────┼──────────────┼───────┘         │
│           │             │              │                 │
│           ▼             ▼              ▼                 │
│   ┌─────────────────────────────────────────────┐       │
│   │    ObservationCollection (ODSS §7)          │       │
│   │    ├── Observation (ODSS §9) × N            │       │
│   │    ├── ObservationWindow (ODSS §8) × M      │       │
│   │    └── Provenance (ODSS §19)                │       │
│   └─────────────────────────────────────────────┘       │
│           │                                             │
│           ▼                                             │
│   ┌──────────────────────────────────────┐              │
│   │   MetricExtractor → MetricDataFrame  │              │
│   └──────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────┘
```

### 8.2 Layer Responsibilities

| Layer | Responsibility | Input | Output |
|-------|---------------|-------|--------|
| `ExtractionEngine` | Orchestrate providers, merge collections | `RepositoryContext`, `metric_list` | `ObservationCollection`, `MetricDataFrame` |
| `ProviderRegistry` | Discover, select, health-check providers | Metric ID | Ordered provider list |
| `IObservationProvider` | Extract observations from a specific data source | `ProviderContext` | `ObservationCollection` |
| `MetricExtractor` | Translate observations to `MetricDataFrame` | `ObservationCollection` | `MetricDataFrame` |

### 8.3 Data Flow

1. `ExtractionEngine.extract()` receives a `RepositoryContext` and `metric_list`.
2. For each metric in `metric_list`, the engine queries the `ProviderRegistry` for ordered providers.
3. Each provider is invoked with a `ProviderContext` derived from the `RepositoryContext`.
4. Each provider returns an `ObservationCollection` containing its observations.
5. The engine merges all `ObservationCollection` objects into a single unified collection.
6. The merged collection is passed to `MetricExtractor` for `MetricDataFrame` translation.
7. Provenance metadata records which provider produced each observation.

---

## 9. Provider Contract (`IObservationProvider`)

### 9.1 Protocol Definition

```python
from __future__ import annotations
from typing import Protocol, runtime_checkable, List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ProviderStatus(str, Enum):
    """Provider health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ProviderCapability(str, Enum):
    """What a provider can produce."""
    OBSERVATIONS = "observations"      # Produces Observation objects
    METRICS = "metrics"                # Directly produces MetricDataFrame
    WINDOWS = "windows"                # Pre-computes windows


@dataclass(frozen=True)
class ProviderHealth:
    """Health snapshot for a provider."""
    status: ProviderStatus
    last_check: str                    # ISO-8601
    consecutive_failures: int
    last_latency_ms: Optional[float]
    error_message: Optional[str]


@dataclass(frozen=True)
class ProviderContext:
    """Context passed to a provider during extraction.

    Derived from RepositoryContext by the ExtractionEngine.
    Contains only what a provider needs, not the full context.

    Attributes:
        repository_id: Repository identifier.
        repo_path: Local filesystem path to the repository.
        analysis_id: Unique identifier for this analysis run.
        since: Inclusive start date filter (optional).
        until: Inclusive end date filter (optional).
        exclude_bots: Whether to exclude bot-authored sources.
        seed: Random seed for deterministic extraction.
        config: Provider-specific configuration overrides.
    """
    repository_id: str
    repo_path: str
    analysis_id: str
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    exclude_bots: bool = False
    seed: Optional[int] = None
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderResult:
    """Result of a provider extraction.

    Wraps the ObservationCollection with provider-specific metadata.

    Attributes:
        collection: The extracted ObservationCollection.
        provider_id: Identifier of the provider that produced this result.
        latency_ms: Extraction latency in milliseconds.
        confidence: Extraction confidence (0.0 to 1.0).
        warnings: Non-fatal warnings during extraction.
    """
    collection: ObservationCollection
    provider_id: str
    latency_ms: float
    confidence: float
    warnings: List[str] = field(default_factory=list)


@runtime_checkable
class IObservationProvider(Protocol):
    """PRV-01: Observation Provider interface.

    Every data source that produces observations implements this Protocol.
    The Observation Engine depends only on this interface, never on
    concrete implementations.

    Providers are stateless — all state lives in the returned
    ObservationCollection. Providers may be instantiated once and
    reused across multiple extractions.
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider.

        Must be a stable, versioned string (e.g., 'git_extractor.v1').
        Used for provenance tracking and registry lookup.
        """
        ...

    @property
    def supported_metrics(self) -> frozenset[str]:
        """Set of metric IDs this provider can extract.

        A provider must declare every metric it may produce.
        The registry uses this for provider-to-metric routing.
        """
        ...

    @property
    def capabilities(self) -> frozenset[ProviderCapability]:
        """Provider capabilities.

        At minimum, every provider must support OBSERVATIONS.
        """
        ...

    def extract(
        self,
        context: ProviderContext,
        metric_list: List[str],
    ) -> ProviderResult:
        """Extract observations for the requested metrics.

        Args:
            context: Provider context with repository path and filters.
            metric_list: Metric IDs to extract. Must be a subset of
                         self.supported_metrics.

        Returns:
            ProviderResult containing the ObservationCollection.

        Raises:
            ProviderExtractionError: If extraction fails completely.
            ProviderPartialError: If some observations could not be
                                  extracted (partial results in result).
        """
        ...

    def health_check(self) -> ProviderHealth:
        """Check provider health and availability.

        Called by the registry periodically and before extraction.
        Must be lightweight (< 100ms).

        Returns:
            ProviderHealth with current status.
        """
        ...

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate provider-specific configuration.

        Args:
            config: Configuration dict to validate.

        Returns:
            True if configuration is valid for this provider.
        """
        ...
```

### 9.2 Contract Guarantees

| Guarantee | Description |
|-----------|-------------|
| **Determinism** | Same `ProviderContext` produces identical `ObservationCollection` (given same seed) |
| **Immutability** | Providers do not mutate the `ProviderContext` or any shared state |
| **Metric Honesty** | A provider only produces observations for metrics in `supported_metrics` |
| **Provenance** | Every observation carries `ObservationProvenance.extractor_id = self.provider_id` |
| **Health Transparency** | `health_check()` reflects the provider's actual ability to extract |
| **Schema Compliance** | All produced `Observation` objects comply with ODSS-v1.0 §9 |

### 9.3 Invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| INV-01 | `provider_id` is unique across all registered providers | Registry validation at registration time |
| INV-02 | `supported_metrics` is a subset of `{"M-01", ..., "M-07"}` | Registry validation at registration time |
| INV-03 | `extract()` returns observations only for requested metrics | Postcondition check by ExtractionEngine |
| INV-04 | `extract()` never returns `None` — empty results use empty `ObservationCollection` | Protocol contract |
| INV-05 | `health_check()` completes within 100ms | Runtime enforcement (logged, not blocked) |
| INV-06 | Every observation's `provenance.extractor_id` matches `provider_id` | Postcondition check by ExtractionEngine |

---

## 10. Provider Lifecycle

### 10.1 Lifecycle Phases

```
Registration → Discovery → Health Check → Extraction → Transformation → Validation
     │              │            │              │               │              │
     ▼              ▼            ▼              ▼               ▼              ▼
  Register      Select       Probe        Extract         Transform       Validate
  provider      providers    health       observations    to collection   output
```

### 10.2 Phase 1 — Registration

Providers register themselves with the `ProviderRegistry` before extraction begins.

**Registration Contract:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | `IObservationProvider` | Yes | The provider instance |
| `priority` | `int` | Yes | Lower number = higher priority (default: 100) |
| `enabled` | `bool` | Yes | Whether the provider is active (default: True) |
| `config` | `Dict[str, Any]` | No | Provider-specific configuration |

**Registration Rules:**

1. A provider with `provider_id` already in the registry must be rejected (INV-01).
2. A provider whose `supported_metrics` overlaps with an existing provider for the same metric at the same priority is rejected.
3. A provider whose `validate_config()` returns `False` for the provided config is rejected.
4. Registration order among providers with the same priority for the same metric is undefined.

### 10.3 Phase 2 — Discovery

Discovery maps a requested metric to an ordered list of providers:

```
Discovery("M-02") → [GitProvider.v1 (priority=10), FutureGitAPIProvider.v1 (priority=50)]
Discovery("M-03") → [FileAnalysisProvider.v1 (priority=10)]
Discovery("M-05") → [CICDProvider.v1 (priority=10)]
```

**Discovery Algorithm:**

1. Filter registry to providers where `metric_id in provider.supported_metrics`.
2. Filter to providers where `enabled = True`.
3. Sort by `priority` ascending (lower number = tried first).
4. Return ordered list.

### 10.4 Phase 3 — Health Check

Before extraction, the `ExtractionEngine` invokes `health_check()` on each discovered provider.

| Status | Behavior |
|--------|----------|
| `HEALTHY` | Proceed with extraction |
| `DEGRADED` | Proceed with extraction, but mark observations with reduced confidence |
| `UNHEALTHY` | Skip provider, try next in priority order, or fail if no providers remain |
| `UNKNOWN` | Attempt extraction; if it fails, mark provider as `UNHEALTHY` |

**Health Check Contract:**

- Must complete within 100ms (logged as warning if exceeded, not blocked).
- Must not have side effects (pure read operation).
- Must reflect the provider's actual ability to reach its data source.

### 10.5 Phase 4 — Extraction

Extraction is the core provider operation:

1. `ExtractionEngine` constructs a `ProviderContext` from `RepositoryContext`.
2. For each metric in `metric_list`, the engine selects the highest-priority healthy provider.
3. The engine calls `provider.extract(context, [metric_id])`.
4. The provider returns a `ProviderResult` containing the `ObservationCollection`.
5. The engine records latency and confidence in the result.

**Extraction Rules:**

| Rule | Description |
|------|-------------|
| EXR-01 | A provider may return observations for metrics not in `metric_list` — these are ignored. |
| EXR-02 | A provider may return zero observations for a requested metric — this is valid (empty collection). |
| EXR-03 | A provider may raise `ProviderExtractionError` — the engine catches and tries the next provider. |
| EXR-04 | A provider may raise `ProviderPartialError` — partial results are used. |
| EXR-05 | Extraction for a single metric must not block extraction for other metrics. |

### 10.6 Phase 5 — Transformation

Transformation is the responsibility of `MetricExtractor` (unchanged from v1.5):

1. The engine collects all `ObservationCollection` objects from all providers.
2. Collections are merged into a single `ObservationCollection`.
3. The merged collection is passed to `MetricExtractor.extract_metrics()`.
4. `MetricExtractor` produces the `MetricDataFrame`.

**Merge Rules:**

| Rule | Description |
|------|-------------|
| MER-01 | Observations are deduplicated by `(source_type, source_id, metric_id)`. |
| MER-02 | When duplicates exist, the observation from the higher-priority provider wins. |
| MER-03 | Window assignments from different providers are merged by `window_id`. |
| MER-04 | Total observation and metric counts are recomputed after merge. |

### 10.7 Phase 6 — Validation

Post-extraction validation ensures the merged collection meets downstream requirements:

| Check | Description | Failure Behavior |
|-------|-------------|-----------------|
| Schema compliance | All observations comply with ODSS-v1.0 §9 | Reject observation |
| Metric coverage | Requested metrics have at least one observation | Warning (non-fatal) |
| Confidence threshold | Observations below minimum confidence are flagged | Warning (non-fatal) |
| Provenance integrity | Every observation has valid provenance | Reject observation |
| Temporal consistency | Observation timestamps are within requested range | Reject observation |

---

## 11. Provider Type Hierarchy

### 11.1 Git Provider (`IGitProvider`)

```python
@runtime_checkable
class IGitProvider(IObservationProvider, Protocol):
    """PRV-02: Git data source provider.

    Extracts observations from git commit history, branches, and tags.
    The canonical implementation is CommitExtractor (v1.5).

    Supported metrics:
        M-02: Commit frequency (one observation per commit, value=1.0)
        M-06: Code churn (one observation per commit, value=insertions+deletions)
    """

    def extract_commits(
        self,
        context: ProviderContext,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        exclude_bots: bool = False,
    ) -> ProviderResult:
        """Extract commit-level observations from git history."""
        ...

    def extract_branches(self, context: ProviderContext) -> ProviderResult:
        """Extract branch-level observations (future: M-03 from branch metadata)."""
        ...

    def extract_tags(self, context: ProviderContext) -> ProviderResult:
        """Extract tag-level observations (future: release cadence)."""
        ...
```

**Backward Compatibility Mapping:**

| CommitExtractor method | IGitProvider method |
|----------------------|---------------------|
| `extract_commits(context, since, until, exclude_bots, seed)` | `extract_commits(context, since, until, exclude_bots)` |
| `_parse_git_log(repo_path, since, until, exclude_bots)` | Internal implementation detail |
| `_build_window(observations, commits)` | Handled by `ExtractionEngine` merge |
| `_empty_collection(repo_id, seed)` | Returns empty `ProviderResult` |

### 11.2 Static Analysis Provider (`IStaticAnalysisProvider`)

```python
@runtime_checkable
class IStaticAnalysisProvider(IObservationProvider, Protocol):
    """PRV-03: Static analysis data source provider.

    Extracts observations from AST parsing, complexity analysis,
    and code structure evaluation.

    Supported metrics:
        M-04: Code complexity (cyclomatic complexity, nesting depth)
        M-03: Code churn (from diff-based analysis, complementary to M-06)
    """

    def extract_complexity(
        self,
        context: ProviderContext,
        file_patterns: Optional[List[str]] = None,
    ) -> ProviderResult:
        """Extract complexity metrics from source files."""
        ...

    def extract_structure(
        self,
        context: ProviderContext,
    ) -> ProviderResult:
        """Extract structural metrics (module size, coupling)."""
        ...
```

### 11.3 CI/CD Provider (`ICICDProvider`)

```python
@runtime_checkable
class ICICDProvider(IObservationProvider, Protocol):
    """PRV-04: CI/CD pipeline data source provider.

    Extracts observations from continuous integration and deployment
    pipeline APIs (GitHub Actions, GitLab CI, Jenkins, etc.).

    Supported metrics:
        M-05: Build duration (from pipeline run timestamps)
        M-07: Build health (from pipeline pass/fail rates)
    """

    def extract_builds(
        self,
        context: ProviderContext,
        pipeline_filter: Optional[str] = None,
    ) -> ProviderResult:
        """Extract build duration observations."""
        ...

    def extract_pipeline_health(
        self,
        context: ProviderContext,
    ) -> ProviderResult:
        """Extract pipeline pass/fail rate observations."""
        ...
```

### 11.4 Repository Metadata Provider (`IRepositoryMetadataProvider`)

```python
@runtime_checkable
class IRepositoryMetadataProvider(IObservationProvider, Protocol):
    """PRV-05: Repository metadata provider.

    Extracts observations from repository-level metadata files
    (README, LICENSE, CONTRIBUTING, etc.).

    Supported metrics:
        M-01: Documentation quality (README completeness, license presence)
    """

    def extract_documentation(
        self,
        context: ProviderContext,
    ) -> ProviderResult:
        """Extract documentation quality observations."""
        ...

    def extract_metadata(
        self,
        context: ProviderContext,
    ) -> ProviderResult:
        """Extract repository metadata observations."""
        ...
```

### 11.5 File Analysis Provider (`IFileAnalysisProvider`)

```python
@runtime_checkable
class IFileAnalysisProvider(IObservationProvider, Protocol):
    """PRV-06: File-level analysis provider.

    Extracts observations from file-level diff analysis, including
    churn rate per file, file age, and ownership patterns.

    Supported metrics:
        M-03: Code churn (file-level churn analysis, value=ratio)
        M-06: Code churn (complementary to git provider, value=lines)
    """

    def extract_file_churn(
        self,
        context: ProviderContext,
        file_patterns: Optional[List[str]] = None,
    ) -> ProviderResult:
        """Extract file-level churn observations."""
        ...

    def extract_file_age(
        self,
        context: ProviderContext,
    ) -> ProviderResult:
        """Extract file age observations (time since last modification)."""
        ...
```

### 11.6 Type Hierarchy Diagram

```
IObservationProvider (PRV-01)
├── IGitProvider (PRV-02)              → M-02, M-06
├── IStaticAnalysisProvider (PRV-03)   → M-03, M-04
├── ICICDProvider (PRV-04)             → M-05, M-07
├── IRepositoryMetadataProvider (PRV-05) → M-01
└── IFileAnalysisProvider (PRV-06)     → M-03, M-06
```

### 11.7 Metric-to-Provider Mapping

| Metric | Description | Primary Provider | Secondary Provider |
|--------|-------------|-----------------|-------------------|
| M-01 | Documentation quality | `IRepositoryMetadataProvider` | — |
| M-02 | Commit frequency | `IGitProvider` | — |
| M-03 | Code churn | `IFileAnalysisProvider` | `IGitProvider` |
| M-04 | Code complexity | `IStaticAnalysisProvider` | — |
| M-05 | Build duration | `ICICDProvider` | — |
| M-06 | Dependency health | `IGitProvider` | `IFileAnalysisProvider` |
| M-07 | Build health | `ICICDProvider` | — |

---

## 12. Provider Registry

### 12.1 Registry Contract

```python
@runtime_checkable
class IProviderRegistry(Protocol):
    """PRV-07: Provider Registry interface.

    Central registry for all observation providers. Manages registration,
    discovery, health monitoring, and priority-based provider selection.
    """

    def register(
        self,
        provider: IObservationProvider,
        priority: int = 100,
        enabled: bool = True,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a provider with the registry.

        Args:
            provider: The provider instance to register.
            priority: Lower number = higher priority (default: 100).
            enabled: Whether the provider is active.
            config: Optional provider-specific configuration.

        Raises:
            ProviderRegistrationError: If registration fails (duplicate ID,
                overlapping metrics at same priority, invalid config).
        """
        ...

    def unregister(self, provider_id: str) -> None:
        """Remove a provider from the registry.

        Args:
            provider_id: The provider to remove.

        Raises:
            ProviderNotFoundError: If the provider is not registered.
        """
        ...

    def discover(self, metric_id: str) -> List[IObservationProvider]:
        """Discover providers for a specific metric, ordered by priority.

        Args:
            metric_id: The metric to find providers for.

        Returns:
            Ordered list of providers (highest priority first).
            Empty list if no providers serve this metric.
        """
        ...

    def get_provider(self, provider_id: str) -> Optional[IObservationProvider]:
        """Get a specific provider by ID.

        Args:
            provider_id: The provider identifier.

        Returns:
            The provider, or None if not registered.
        """
        ...

    def health_check_all(self) -> Dict[str, ProviderHealth]:
        """Run health checks on all registered providers.

        Returns:
            Dict mapping provider_id to ProviderHealth.
        """
        ...

    def list_providers(self) -> List[IObservationProvider]:
        """List all registered providers.

        Returns:
            List of all registered providers.
        """
        ...

    def list_enabled(self) -> List[IObservationProvider]:
        """List all enabled providers.

        Returns:
            List of enabled providers only.
        """
        ...

    def get_capabilities(self) -> Dict[str, frozenset[str]]:
        """Map each provider to its supported metrics.

        Returns:
            Dict mapping provider_id to supported_metrics.
        """
        ...
```

### 12.2 Registry Implementation Constraints

| Constraint | Description |
|-----------|-------------|
| Thread safety | Registry operations must be safe for concurrent read access |
| Registration order | Providers with the same priority are returned in registration order |
| Mutation isolation | `register()` and `unregister()` do not affect ongoing `discover()` calls |
| Health caching | `health_check_all()` results are cached for 60 seconds |

### 12.3 Default Registry Behavior

```python
class ProviderRegistry:
    """Default IProviderRegistry implementation."""

    def __init__(self) -> None:
        self._providers: Dict[str, Tuple[IObservationProvider, int, bool]] = {}
        self._health_cache: Dict[str, ProviderHealth] = {}
        self._health_cache_ts: float = 0.0
```

The `ExtractionEngine` owns a `ProviderRegistry` instance. The default registry is created in `ExtractionEngine.__init__()` and populated during provider registration.

---

## 13. Dependency Injection and IoC

### 13.1 Injection Pattern

The `ExtractionEngine` receives providers through constructor injection:

```python
class ExtractionEngine:
    """Orchestrate provider-based extraction pipeline.

    v1.5 behavior is preserved when no providers are registered —
    the engine falls back to CommitExtractor directly.
    """

    def __init__(
        self,
        *,
        store: Optional[ObservationStore] = None,
        registry: Optional[ProviderRegistry] = None,
        commit_extractor: Optional[CommitExtractor] = None,
        metric_extractor: Optional[MetricExtractor] = None,
    ) -> None:
        self._store = store
        self._registry = registry or ProviderRegistry()
        self._commit_extractor = commit_extractor or CommitExtractor()
        self._metric_extractor = metric_extractor or MetricExtractor()

        # Auto-register CommitExtractor if registry is empty
        if not self._registry.list_providers():
            self._register_default_providers()

    def _register_default_providers(self) -> None:
        """Register CommitExtractor as the default IGitProvider.

        This preserves v1.5 behavior when no providers are explicitly
        registered.
        """
        git_provider = _CommitExtractorAdapter(self._commit_extractor)
        self._registry.register(git_provider, priority=10)
```

### 13.2 CommitExtractor Adapter

The `CommitExtractor` is wrapped in an adapter that implements `IGitProvider`:

```python
class _CommitExtractorAdapter:
    """Adapter: CommitExtractor → IGitProvider.

    Wraps the existing CommitExtractor to conform to the IObservationProvider
    Protocol, preserving all existing behavior.
    """

    def __init__(self, extractor: CommitExtractor) -> None:
        self._extractor = extractor

    @property
    def provider_id(self) -> str:
        return self._extractor.EXTRACTOR_ID  # "commit_extractor.v1"

    @property
    def supported_metrics(self) -> frozenset[str]:
        return frozenset({"M-02", "M-06"})

    @property
    def capabilities(self) -> frozenset[ProviderCapability]:
        return frozenset({ProviderCapability.OBSERVATIONS})

    def extract(
        self,
        context: ProviderContext,
        metric_list: List[str],
    ) -> ProviderResult:
        collection = self._extractor.extract_commits(
            _provider_context_to_repository_context(context),
            since=context.since,
            until=context.until,
            exclude_bots=context.exclude_bots,
            seed=context.seed,
        )
        return ProviderResult(
            collection=collection,
            provider_id=self.provider_id,
            latency_ms=0.0,  # Measured by engine
            confidence=1.0,
        )

    def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            status=ProviderStatus.HEALTHY,
            last_check=datetime.now(timezone.utc).isoformat(),
            consecutive_failures=0,
            last_latency_ms=None,
            error_message=None,
        )

    def validate_config(self, config: Dict[str, Any]) -> bool:
        return True  # CommitExtractor has no required config
```

### 13.3 Testing Pattern

Providers can be injected as mocks for testing:

```python
# Unit test: provider-based extraction
def test_extraction_with_mock_provider():
    mock_provider = MockGitProvider(
        provider_id="mock_git.v1",
        supported_metrics=frozenset({"M-02"}),
        observations=[...],
    )
    registry = ProviderRegistry()
    registry.register(mock_provider, priority=10)

    engine = ExtractionEngine(registry=registry)
    collection, mdf = engine.extract(context, ["M-02"])

    assert collection.total_observations == expected_count
```

---

## 14. Integration with ExtractionEngine

### 14.1 Modified Extraction Flow

The `ExtractionEngine.extract()` method is extended to support providers:

```python
class ExtractionEngine:

    def extract(
        self,
        context: RepositoryContext,
        metric_list: List[str],
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        exclude_bots: bool = False,
        seed: Optional[int] = None,
    ) -> Tuple[ObservationCollection, MetricDataFrame]:
        """Extract observations and metrics from a repository.

        Provider-based flow:
            1. Build ProviderContext from RepositoryContext
            2. For each metric, discover and invoke providers
            3. Merge all provider results
            4. Translate merged collection to MetricDataFrame

        Fallback flow (no providers registered):
            1. Invoke CommitExtractor directly (v1.5 behavior)
            2. Translate to MetricDataFrame
        """
        provider_context = ProviderContext(
            repository_id=context.repo_id,
            repo_path=context.local_path,
            analysis_id=self._generate_analysis_id(context, seed),
            since=since,
            until=until,
            exclude_bots=exclude_bots,
            seed=seed,
        )

        # Phase 1: Collect observations from all providers
        collections: List[ObservationCollection] = []
        for metric_id in metric_list:
            providers = self._registry.discover(metric_id)
            if not providers:
                continue

            for provider in providers:
                health = provider.health_check()
                if health.status == ProviderStatus.UNHEALTHY:
                    continue

                try:
                    result = provider.extract(provider_context, [metric_id])
                    collections.append(result.collection)
                except ProviderExtractionError:
                    continue

        # Phase 2: Merge collections
        if collections:
            merged = self._merge_collections(collections, provider_context)
        else:
            # Fallback: direct CommitExtractor (v1.5 behavior)
            merged = self._commit_extractor.extract_commits(
                context, since=since, until=until,
                exclude_bots=exclude_bots, seed=seed,
            )

        # Phase 3: Translate to MetricDataFrame
        mdf = self._metric_extractor.extract_metrics(merged, metric_list)

        # Phase 4: Persist
        if self._store is not None:
            self._store.add(merged)

        return merged, mdf
```

### 14.2 Backward Compatibility Guarantees

| Guarantee | Description |
|-----------|-------------|
| API compatibility | `extract()` signature unchanged — all existing callers work |
| Return type compatibility | Returns same `(ObservationCollection, MetricDataFrame)` tuple |
| Behavior compatibility | With no registered providers, produces identical output to v1.5 |
| Test compatibility | All existing tests pass without modification |

### 14.3 Migration Path

| Step | Description | Risk |
|------|-------------|------|
| 1 | Add `IObservationProvider` Protocol to `interfaces.py` | None (additive) |
| 2 | Add `ProviderRegistry` implementation | None (additive) |
| 3 | Wrap `CommitExtractor` in `_CommitExtractorAdapter` | None (preserves behavior) |
| 4 | Extend `ExtractionEngine` with provider dispatch | Low (fallback to v1.5) |
| 5 | Add `ProviderContext` and `ProviderResult` types | None (additive) |
| 6 | Register additional providers (future phases) | None (additive) |

---

## 15. Provider Observability

### 15.1 Observability Data Model

Every provider extraction produces observability data:

```python
@dataclass(frozen=True)
class ProviderObservability:
    """Provider extraction observability metadata.

    Attached to ProviderResult and logged by ExtractionEngine.
    """
    provider_id: str
    metric_id: str
    latency_ms: float
    observations_produced: int
    confidence: float
    status: ProviderStatus
    warnings: List[str]
    extraction_timestamp: str
```

### 15.2 Metrics to Track

| Metric | Type | Description |
|--------|------|-------------|
| `provider_extraction_latency_ms` | Histogram | Time from `extract()` call to return |
| `provider_observations_produced` | Counter | Total observations produced per provider |
| `provider_extraction_failures` | Counter | Total extraction failures per provider |
| `provider_health_status` | Gauge | Current health status (0=UNHEALTHY, 1=DEGRADED, 2=HEALTHY) |
| `provider_confidence` | Histogram | Observation confidence distribution |
| `provider_partial_extractions` | Counter | Number of partial extraction results |

### 15.3 Logging Requirements

| Event | Log Level | Content |
|-------|-----------|---------|
| Provider registered | INFO | `provider_id`, `priority`, `supported_metrics` |
| Provider unregistered | INFO | `provider_id` |
| Health check completed | DEBUG | `provider_id`, `status`, `latency_ms` |
| Extraction started | DEBUG | `provider_id`, `metric_list` |
| Extraction completed | INFO | `provider_id`, `latency_ms`, `observations_produced` |
| Extraction failed | ERROR | `provider_id`, `error_message`, `traceback` |
| Extraction degraded | WARN | `provider_id`, `confidence`, `warnings` |
| Fallback to v1.5 | WARN | `reason`, `metric_list` |

---

## 16. Provider Health and Fallback

### 16.1 Health State Machine

```
                    ┌──────────┐
          ┌────────▶│ UNKNOWN  │◀────────┐
          │         └────┬─────┘         │
          │              │ health_check()│
          │              ▼               │
          │         ┌──────────┐         │
          │    ┌───▶│ HEALTHY  │────┐    │
          │    │    └──────────┘    │    │
          │    │         │          │    │
          │    │    extract()       │    │
          │    │    succeeds        │    │
          │    │         │          │    │
          │    │         ▼          │    │
          │    │    ┌──────────┐    │    │
          │    │    │ DEGRADED │◀───┘    │
          │    │    └────┬─────┘         │
          │    │         │               │
          │    │    extract()            │
          │    │    fails                │
          │    │         │               │
          │    │         ▼               │
          │    │    ┌──────────┐         │
          │    └────│UNHEALTHY │─────────┘
          │         └──────────┘
          │              │
          │    health_check()
          │    succeeds
          └──────────────┘
```

### 16.2 State Transitions

| From | To | Trigger |
|------|-----|---------|
| `UNKNOWN` | `HEALTHY` | `health_check()` returns OK |
| `UNKNOWN` | `DEGRADED` | `health_check()` returns partial failure |
| `UNKNOWN` | `UNHEALTHY` | `health_check()` returns failure |
| `HEALTHY` | `DEGRADED` | `extract()` succeeds with warnings |
| `HEALTHY` | `UNHEALTHY` | `extract()` raises exception |
| `DEGRADED` | `HEALTHY` | Next `health_check()` returns OK |
| `DEGRADED` | `UNHEALTHY` | `extract()` raises exception |
| `UNHEALTHY` | `HEALTHY` | `health_check()` returns OK |
| `UNHEALTHY` | `DEGRADED` | `health_check()` returns partial failure |

### 16.3 Fallback Strategy

When the primary provider for a metric is unhealthy:

1. **Try secondary provider**: If a secondary provider exists for the metric, invoke it.
2. **Skip metric**: If no secondary provider exists, skip the metric and log a warning.
3. **Produce empty observations**: The metric has zero observations — detectors handle this gracefully (DES-v2.0 §30).

**Fallback Rules:**

| Rule | Description |
|------|-------------|
| FB-01 | Never retry a provider within the same extraction run. |
| FB-02 | Never retry a provider that failed `health_check()`. |
| FB-03 | Log every fallback decision with provider_id, metric_id, and reason. |
| FB-04 | Fallback does not affect other metrics' extraction. |

---

## 17. Error Handling

### 17.1 Error Taxonomy

| Error Class | Description | Handling |
|-------------|-------------|----------|
| `ProviderRegistrationError` | Registration failed (duplicate, invalid config) | Raise immediately |
| `ProviderNotFoundError` | Provider ID not in registry | Return `None` |
| `ProviderExtractionError` | Complete extraction failure | Try next provider or fallback |
| `ProviderPartialError` | Partial extraction success | Use partial results |
| `ProviderHealthCheckError` | Health check failed | Mark provider `UNHEALTHY` |
| `ProviderMergeError` | Collection merge failed | Log error, use best available |
| `ProviderConfigError` | Invalid provider configuration | Reject at registration |

### 17.2 Error Propagation

```
Provider.extract()
    ├── ProviderExtractionError
    │       → Caught by ExtractionEngine
    │       → Try next provider in priority order
    │       → If no providers left: ProviderExtractionError to caller
    │
    ├── ProviderPartialError
    │       → Caught by ExtractionEngine
    │       → Use partial collection
    │       → Log warning with partial count
    │
    └── Unexpected exception
            → Caught by ExtractionEngine
            → Wrap in ProviderExtractionError
            → Try next provider
```

### 17.3 Error Context

Every error includes context for debugging:

```python
@dataclass(frozen=True)
class ProviderErrorContext:
    """Context attached to every provider error."""
    provider_id: str
    metric_id: str
    extraction_phase: str          # "health_check", "extract", "transform"
    repository_id: str
    analysis_id: str
    timestamp: str
    error_type: str
    error_message: str
```

---

## 18. Backward Compatibility Strategy

### 18.1 Compatibility Matrix

| Component | v1.5 Behavior | v1.6 Behavior | Breaking? |
|-----------|--------------|---------------|-----------|
| `ExtractionEngine.extract()` | Invokes `CommitExtractor` directly | Invokes providers (fallback to `CommitExtractor`) | No |
| `CommitExtractor` | Direct instantiation by engine | Wrapped in `_CommitExtractorAdapter` | No |
| `MetricExtractor.extract_metrics()` | Receives `ObservationCollection` | Receives merged `ObservationCollection` | No |
| `ObservationCollection` | Schema unchanged | Schema unchanged | No |
| `Observation` | Schema unchanged | Schema unchanged | No |
| `ObservationWindow` | Schema unchanged | Schema unchanged | No |
| `interfaces.py` | 18 interfaces | 19 interfaces (+ `IObservationProvider`) | Additive |
| CLI commands | Unchanged | Unchanged | No |
| Tests | All pass | All pass | No |

### 18.2 Backward Compatibility Invariants

| ID | Invariant |
|----|-----------|
| BC-01 | All existing v1.5 tests pass without modification. |
| BC-02 | `ExtractionEngine.extract()` with no registered providers produces identical output to v1.5. |
| BC-03 | `CommitExtractor` is not modified — only wrapped. |
| BC-04 | `ObservationCollection`, `Observation`, `ObservationWindow` schemas are unchanged. |
| BC-05 | CLI commands produce identical output when run without provider configuration. |

### 18.3 Deprecation Timeline

| Component | v1.6 | v1.7 | v2.0 |
|-----------|------|------|------|
| `_CommitExtractorAdapter` | Supported (default) | Supported | Removed (providers only) |
| Direct `CommitExtractor` instantiation | Supported (deprecated) | Removed | Removed |
| `metric_list` parameter in `extract()` | Supported | Supported | Supported |

---

## 19. Security Considerations

### 19.1 Provider Isolation

| Concern | Mitigation |
|---------|-----------|
| Provider accesses unauthorized files | `ProviderContext.repo_path` scoped to repository |
| Provider exfiltrates data | Providers run in-process, no network access by default |
| Provider modifies repository | Providers are read-only (no write operations) |
| Provider blocks extraction | Timeout enforced by `ExtractionEngine` (default: 30s per provider) |
| Malicious provider registered | Provider registration requires explicit opt-in |

### 19.2 Configuration Security

| Concern | Mitigation |
|---------|-----------|
| Secrets in provider config | Config dict must not contain secrets (logged if detected) |
| API keys in provider context | `ProviderContext.config` not logged at INFO level |
| Provider config injection | Config validated by `validate_config()` before registration |

---

## 20. Performance Architecture

### 20.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Registry registration | < 1ms | Per provider |
| Provider discovery | < 1ms | Per metric |
| Health check | < 100ms | Per provider |
| Provider extraction | < 30s | Per provider per metric |
| Collection merge | < 10ms | Per merge operation |
| Total provider overhead | < 5% | Of total extraction time |

### 20.2 Parallelism Strategy

| Operation | Parallelism | Rationale |
|-----------|------------|-----------|
| Health checks | Parallel | Independent per provider |
| Provider extraction (different metrics) | Parallel | Independent data sources |
| Provider extraction (same metric) | Sequential | Priority-ordered, first succeeds |
| Collection merge | Sequential | Deterministic ordering |

### 20.3 Caching Strategy

| Cache | TTL | Invalidation |
|-------|-----|-------------|
| Health check results | 60s | On extraction failure |
| Provider discovery results | 0s (always fresh) | N/A |
| Provider config validation | 0s (always validated) | N/A |

---

## 21. Configuration Architecture

### 21.1 Provider Configuration Schema

```yaml
# OPC-v1.0 provider configuration (example)
providers:
  git_extractor:
    enabled: true
    priority: 10
    config:
      exclude_bots: true
      bot_patterns:
        - "dependabot"
        - "renovate"
        - "github-actions"

  static_analysis:
    enabled: false
    priority: 20
    config:
      file_patterns:
        - "**/*.py"
        - "**/*.js"
      complexity_tool: "radon"

  cicd_github:
    enabled: false
    priority: 10
    config:
      api_token_env: "GITHUB_TOKEN"
      pipeline_filter: "main"
```

### 21.2 Configuration Loading Order

1. Default configuration (hardcoded in provider implementation)
2. Project-level configuration (`miie.yaml` in repository root)
3. User-level configuration (`~/.config/miie/providers.yaml`)
4. Environment variables (override specific fields)

### 21.3 Configuration Validation

Every provider validates its configuration at registration time:

| Validation | Description |
|-----------|-------------|
| Required fields | All required config keys are present |
| Type checking | Config values match expected types |
| Value ranges | Numeric values are within valid ranges |
| Secret detection | Config values do not contain API keys or tokens |
| Dependency checking | Required external tools are available |

---

## 22. Architectural Invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| INV-01 | `provider_id` is globally unique | Registry validation |
| INV-02 | `supported_metrics` ⊆ `{"M-01", ..., "M-07"}` | Registry validation |
| INV-03 | Observations produced only for declared metrics | Postcondition check |
| INV-04 | Providers never return `None` — empty results use empty collection | Protocol contract |
| INV-05 | `health_check()` completes within 100ms | Runtime logging |
| INV-06 | `provenance.extractor_id` matches `provider_id` | Postcondition check |
| INV-07 | Provider registration does not affect ongoing extractions | Registry implementation |
| INV-08 | Merge order is deterministic for same input | Deterministic sort |
| INV-09 | v1.5 behavior preserved with no providers registered | Fallback logic |
| INV-10 | All observations in merged collection comply with ODSS-v1.0 | Schema validation |

---

## 23. Tradeoff Analysis

| Decision | Alternative | Tradeoff | Rationale |
|----------|------------|---------|-----------|
| Protocol-based interface | ABC abstract class | Less enforcement, more flexibility | Aligns with existing codebase (18 Protocols in interfaces.py) |
| In-process providers | Out-of-process providers | Simpler, but no isolation | Simplicity preferred for v1.6; isolation can be added later |
| Priority-based fallback | Weighted voting | Simpler, but less sophisticated | Priority sufficient for initial provider selection |
| Centralized registry | Distributed discovery | Simpler, but single point of failure | Registry is in-process, no failure risk |
| Adapter for CommitExtractor | Rewrite as provider | Preserves behavior, more code | Backward compatibility is non-negotiable |
| Health check per provider | Global health check | More overhead, but per-provider granularity | Per-provider enables targeted fallback |

---

## 24. Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Provider implementation errors break extraction | Medium | High | Postcondition checks, fallback to v1.5 |
| Health check latency degrades extraction performance | Low | Medium | 100ms timeout, async health checks |
| Multiple providers produce duplicate observations | Medium | Low | Merge deduplication by (source_type, source_id, metric_id) |
| Provider config misconfiguration causes silent failures | Medium | Medium | Validation at registration, logging at extraction |
| Backward compatibility regression | Low | High | Invariant BC-01 enforced by test suite |

---

## 25. Acceptance Criteria

### 25.1 Functional Acceptance

| ID | Criterion |
|----|-----------|
| AC-01 | `IObservationProvider` Protocol is defined with all required methods and properties |
| AC-02 | `ProviderRegistry` supports register, unregister, discover, and health_check_all |
| AC-03 | `CommitExtractor` is wrapped in adapter conforming to `IGitProvider` |
| AC-04 | `ExtractionEngine.extract()` invokes registered providers when available |
| AC-05 | `ExtractionEngine.extract()` falls back to v1.5 behavior when no providers registered |
| AC-06 | Provider health status affects extraction flow (HEALTHY proceed, UNHEALTHY skip) |
| AC-07 | Collection merge deduplicates observations correctly |
| AC-08 | All existing v1.5 tests pass without modification |
| AC-09 | Provider observability data is logged at appropriate levels |
| AC-10 | Configuration validation rejects invalid provider configs |

### 25.2 Non-Functional Acceptance

| ID | Criterion |
|----|-----------|
| NF-01 | Registry registration completes in < 1ms |
| NF-02 | Provider discovery completes in < 1ms |
| NF-03 | Health check completes in < 100ms |
| NF-04 | Provider extraction timeout is configurable (default: 30s) |
| NF-05 | Provider overhead is < 5% of total extraction time |

---

## 26. Glossary

| Term | Definition |
|------|-----------|
| **Provider** | An implementation of `IObservationProvider` that extracts observations from a specific data source |
| **Provider Registry** | Central registry managing provider registration, discovery, and health monitoring |
| **Provider Context** | Typed context passed to a provider during extraction, derived from `RepositoryContext` |
| **Provider Result** | Wrapper around `ObservationCollection` with provider-specific metadata |
| **Provider Health** | Health snapshot reflecting a provider's current operational status |
| **Provider Priority** | Numeric ordering (lower = higher priority) for provider selection when multiple providers serve the same metric |
| **Provider Capability** | What a provider can produce (observations, metrics, windows) |
| **CommitExtractor Adapter** | Wrapper that adapts v1.5 `CommitExtractor` to `IGitProvider` |
| **Collection Merge** | Process of combining `ObservationCollection` objects from multiple providers into one |
| **Fallback** | Strategy for handling provider failures by trying alternative providers or skipping metrics |

---

## 27. Appendix

### 27.1 Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| OEAS-v1.5 | `docs/specifications/OEAS_v1.5_Observation_Engine.md` | Observation Engine architecture |
| ODSS-v1.0 | `docs/specifications/ODSS_v1.0_Observation_Data_Schema_Specification.md` | Observation data model |
| DES-v2.0 | `docs/specifications/DES_v2.0_Detector_Execution_Specification.md` | Detector execution |
| IMS-v1.0 | `docs/specifications/IMS_v1.0_Implementation_and_Migration_Specification.md` | Implementation phases |
| OSMS-v1.0 | `docs/specifications/v1.6/` | Schema management (planned) |
| OPC-v1.0 | `docs/specifications/v1.6/` | Pipeline configuration (planned) |
| OPR-v1.0 | `docs/specifications/v1.6/` | Processing runtime (planned) |

### 27.2 Interface Summary

| Interface | ID | Methods | Status |
|-----------|-----|---------|--------|
| `IObservationProvider` | PRV-01 | `extract()`, `health_check()`, `validate_config()` | New |
| `IGitProvider` | PRV-02 | `extract_commits()`, `extract_branches()`, `extract_tags()` | New |
| `IStaticAnalysisProvider` | PRV-03 | `extract_complexity()`, `extract_structure()` | New |
| `ICICDProvider` | PRV-04 | `extract_builds()`, `extract_pipeline_health()` | New |
| `IRepositoryMetadataProvider` | PRV-05 | `extract_documentation()`, `extract_metadata()` | New |
| `IFileAnalysisProvider` | PRV-06 | `extract_file_churn()`, `extract_file_age()` | New |
| `IProviderRegistry` | PRV-07 | `register()`, `unregister()`, `discover()`, `health_check_all()` | New |

### 27.3 Schema Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-07-03 | Initial specification |

### 27.4 Implementation Phases

| Phase | Description | Dependencies |
|-------|-------------|-------------|
| Phase 1 | Add `IObservationProvider`, `ProviderContext`, `ProviderResult`, `ProviderHealth` types | None |
| Phase 2 | Implement `ProviderRegistry` with register/discover/health_check | Phase 1 |
| Phase 3 | Implement `_CommitExtractorAdapter` wrapping `CommitExtractor` | Phase 1 |
| Phase 4 | Extend `ExtractionEngine` with provider dispatch and fallback | Phases 2, 3 |
| Phase 5 | Add provider observability logging and metrics | Phase 4 |
| Phase 6 | Implement `StaticAnalysisProvider`, `CICDProvider`, etc. | Phase 4 |

---

*End of Document*
