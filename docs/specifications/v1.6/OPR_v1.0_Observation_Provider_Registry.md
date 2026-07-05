# Observation Provider Registry (OPR) v1.0

**MIIE v1.6 — Provider Registration, Discovery, Prioritization, and Health Monitoring**

| Field | Value |
|-------|-------|
| Document ID | OPR-v1.0 |
| Version | 1.0.0 |
| Date | 2026-07-03 |
| Classification | Internal Engineering Architecture Specification |
| Status | Canonical |
| Baseline | v1.5 (tag `4c4d5e6` evolution) |
| Supersedes | None (new) |
| Dependencies | OEAS-v1.5, ODSS-v1.0, DES-v2.0, IMS-v1.0 |
| Related Documents | OPA-v1.0 (Observation Provider Architecture), OPC-v1.0 (Observation Provider Contracts), OSMS-v1.0 (Observation System Management Specification) |

---

## Table of Contents

1. [Document Metadata](#1-document-metadata)
2. [Purpose and Scope](#2-purpose-and-scope)
3. [Motivation](#3-motivation)
4. [Architectural Principles](#4-architectural-principles)
5. [Registry Architecture](#5-registry-architecture)
6. [Provider Interface](#6-provider-interface)
7. [Registration Protocol](#7-registration-protocol)
8. [Discovery Protocol](#8-discovery-protocol)
9. [Prioritization Model](#9-prioritization-model)
10. [Health Monitoring System](#10-health-monitoring-system)
11. [Lifecycle Management](#11-lifecycle-management)
12. [Integration with ExtractionEngine](#12-integration-with-extractionengine)
13. [Error Handling and Fallback Strategy](#13-error-handling-and-fallback-strategy)
14. [Concurrency Model](#14-concurrency-model)
15. [Configuration](#15-configuration)
16. [Architectural Invariants](#16-architectural-invariants)
17. [Performance Targets](#17-performance-targets)
18. [Security Considerations](#18-security-considerations)
19. [Compatibility with v1.5](#19-compatibility-with-v15)
20. [Migration Strategy](#20-migration-strategy)
21. [Future Evolution](#21-future-evolution)
22. [Decision Log](#22-decision-log)
23. [Risk Register](#23-risk-register)
24. [Acceptance Criteria](#24-acceptance-criteria)
25. [Glossary](#25-glossary)
26. [Appendix — Cross-References](#26-appendix--cross-references)

---

## 1. Document Metadata

### 1.1 Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-07-03 | MIIE Engineering | Initial specification |

### 1.2 Derivation Chain

```
PRD-v1.5-OE (§39.1: v1.6 Extensions)
  └─→ OEAS-v1.5 (§14.1–§14.5: Planned Extractors)
       └─→ OPR-v1.0 (this document)
            ├─→ OPA-v1.0 (Provider Architecture)
            ├─→ OPC-v1.0 (Provider Contracts)
            └─→ OSMS-v1.0 (System Management)
```

---

## 2. Purpose and Scope

### 2.1 Purpose

This document defines the **Observation Provider Registry** — the component responsible for registering, discovering, prioritizing, and health-monitoring observation providers within the MIIE v1.6 Observation Engine.

The OPR exists because MIIE v1.5 hardcodes `CommitExtractor` as the sole observation creator within `ExtractionEngine` (`src/miie/processing/extraction/engine.py:40–56`). There is no provider abstraction, no registration mechanism, no fallback if extraction fails, and no health monitoring. The v1.6 Observation Engine must support multiple observation providers (commit-level, file-level, pull-request, issue, complexity, coverage) with prioritized fallback and health-aware routing.

### 2.2 Scope

| In Scope | Out of Scope |
|----------|-------------|
| Provider registration and deregistration | Provider implementation details (see OPA-v1.0) |
| Provider discovery by metric, capability, priority | Observation data schema (see ODSS-v1.0) |
| Priority-based provider selection | Detector execution (see DES-v2.0) |
| Health status tracking and monitoring | Scoring and reporting (see existing specs) |
| Fallback chain management | CLI interface changes |
| Latency and confidence tracking | Real-time streaming (v2.0) |
| Periodic health check orchestration | Multi-repo workspace management |
| Graceful provider shutdown and drain | Database-backed persistence |

### 2.3 Non-Objectives

| ID | Non-Objective | Reason |
|----|--------------|--------|
| NO-1 | Provider algorithm implementation | Providers implement their own logic (OPA-v1.0) |
| NO-2 | Provider authentication/authorization | Offline-first philosophy; no remote providers in v1.6 |
| NO-3 | Dynamic provider loading from plugins | Plugin architecture deferred to v2.0 |
| NO-4 | Distributed provider coordination | Single-process only; distributed deferred to v2.0 |
| NO-5 | Provider versioning and compatibility | Semver for providers deferred to v2.0 |

---

## 3. Motivation

### 3.1 Current System Limitations (v1.5)

The v1.5 `ExtractionEngine` creates observations via a single, hardcoded `CommitExtractor`:

```
ExtractionEngine.__init__():
    self._commit_extractor = commit_extractor or CommitExtractor()
```

This design has four structural deficiencies:

| Deficiency | Impact | v1.6 Requirement |
|-----------|--------|-----------------|
| No provider abstraction | Cannot add new extractors without modifying ExtractionEngine | Pluggable provider interface |
| No registration/discovery | Providers must be manually wired in constructor | Registry-based discovery |
| No fallback mechanism | If CommitExtractor fails, entire extraction fails | Priority-based fallback chains |
| No health monitoring | Silent failures; no latency or confidence tracking | Health status tracking with eviction |

### 3.2 DetectorRegistry as Reference Pattern

The existing `DetectorRegistry` (`src/miie/processing/detection/registry.py`) demonstrates a working registry pattern within MIIE:

```python
class DetectorRegistry:
    def register(self, detector: BaseDetector) -> None: ...
    def get(self, detector_id: str) -> Optional[BaseDetector]: ...
    def get_all(self) -> List[BaseDetector]: ...
    def get_registered_ids(self) -> List[str]: ...
    def is_registered(self, detector_id: str) -> bool: ...
```

The OPR extends this pattern with:
- Multi-key registration (metric_id(s), capabilities)
- Priority-based selection
- Health monitoring and eviction
- Lifecycle management (drain, restart)

### 3.3 Required Provider Coverage

MIIE v1.6 introduces new observation sources that require independent providers:

| Provider | Metric IDs | Source Type | Priority | Status |
|----------|-----------|-------------|----------|--------|
| CommitExtractor | M-02, M-06 | commit | PRIMARY | Implemented (v1.5) |
| CoverageExtractor | M-01 | file | SECONDARY | Planned (v1.5 OEAS §14.2) |
| ReviewExtractor | M-03, M-04 | pull_request | SECONDARY | Planned (v1.5 OEAS §14.3) |
| IssueExtractor | M-05 | issue | SECONDARY | Planned (v1.5 OEAS §14.4) |
| ComplexityExtractor | M-07 | file | FALLBACK | Planned (v1.5 OEAS §14.5) |

---

## 4. Architectural Principles

### 4.1 Registry as Single Source of Truth

**Statement:** All provider lookup, selection, and routing flows through the OPR. No component may hold direct references to provider instances outside the registry.

**Rationale:** Centralized registration enables uniform health monitoring, priority enforcement, and lifecycle management.

**Implementation:** ExtractionEngine obtains providers exclusively via `Registry.get_providers_for_metric()`.

### 4.2 Provider Independence

**Statement:** Providers have no knowledge of each other. They do not coordinate, communicate, or depend on sibling providers.

**Rationale:** Independent providers can be registered, unregistered, and health-checked without side effects on other providers.

**Implementation:** Provider interface contains no references to Registry or other providers.

### 4.3 Fail-Over, Not Fail-Safe

**Statement:** When a primary provider fails, the registry promotes the next-priority provider. The system degrades gracefully rather than failing entirely.

**Rationale:** Observation extraction should succeed whenever any viable provider exists for a metric.

**Implementation:** Fallback chains are constructed at registration time based on priority ordering.

### 4.4 Deterministic Provider Selection

**Statement:** Given the same set of registered providers with the same health states, the registry always selects the same provider for a given metric.

**Rationale:** Reproducibility requires deterministic behavior at every pipeline stage (OEAS §6.2).

**Implementation:** Priority ordering is deterministic; health state transitions are logged and idempotent.

### 4.5 Health as a First-Class Signal

**Statement:** Provider health is not an afterthought. It is tracked continuously and influences every extraction decision.

**Rationale:** Unhealthy providers produce low-confidence or invalid observations that corrupt downstream detectors.

**Implementation:** Every extraction updates health metrics; unhealthy providers are evicted automatically.

---

## 5. Registry Architecture

### 5.1 Component Position

```
┌─────────────────────────────────────────────────────────────────┐
│ Observation Engine (v1.6)                                       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  Extraction Layer                       │    │
│  │                                                         │    │
│  │  ┌──────────────────────────────────────────────────┐   │    │
│  │  │         Observation Provider Registry            │   │    │
│  │  │                                                  │   │    │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐      │   │    │
│  │  │  │Registration│ │ Discovery│  │  Health  │      │   │    │
│  │  │  │  Module   │  │  Module  │  │ Monitor  │      │   │    │
│  │  │  └──────────┘  └──────────┘  └──────────┘      │   │    │
│  │  │                                                  │   │    │
│  │  │  ┌──────────┐  ┌──────────┐                     │   │    │
│  │  │  │ Priority │  │ Lifecycle│                     │   │    │
│  │  │  │  Engine  │  │ Manager  │                     │   │    │
│  │  │  └──────────┘  └──────────┘                     │   │    │
│  │  └──────────────────────────────────────────────────┘   │    │
│  │                         │                                │    │
│  │                         ▼                                │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │    │
│  │  │  Commit   │ │ Coverage │  │  Review  │  ...        │    │
│  │  │Extractor │ │Extractor │  │Extractor │             │    │
│  │  └──────────┘  └──────────┘  └──────────┘             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Internal Module Structure

```
ObservationProviderRegistry
├── RegistrationModule
│   ├── _providers: Dict[str, ProviderEntry]
│   ├── _metric_index: Dict[str, List[str]]      # metric_id → [provider_ids]
│   ├── _capability_index: Dict[str, List[str]]   # capability → [provider_ids]
│   └── _priority_index: Dict[Priority, List[str]] # priority → [provider_ids]
│
├── DiscoveryModule
│   ├── get_providers_for_metric(metric_id) → List[ProviderEntry]
│   ├── get_providers_by_capability(capability) → List[ProviderEntry]
│   ├── get_primary_provider(metric_id) → Optional[ProviderEntry]
│   ├── get_fallback_chain(metric_id) → List[ProviderEntry]
│   └── get_all_providers() → List[ProviderEntry]
│
├── PriorityEngine
│   ├── resolve_chain(metric_id) → List[ProviderEntry]
│   ├── promote(provider_id) → None
│   ├── demote(provider_id) → None
│   └── set_priority(provider_id, priority) → None
│
├── HealthMonitor
│   ├── _health_status: Dict[str, HealthStatus]
│   ├── _latency_tracker: Dict[str, LatencyStats]
│   ├── _confidence_tracker: Dict[str, ConfidenceStats]
│   ├── check_health(provider_id) → HealthStatus
│   ├── record_extraction(provider_id, latency, confidence) → None
│   ├── should_evict(provider_id) → bool
│   └── periodic_check() → List[HealthEvent]
│
└── LifecycleManager
    ├── shutdown() → None              # drain in-flight
    ├── restart_provider(id) → None    # recovery
    ├── evict_provider(id) → None      # remove unhealthy
    └── promote_fallback(id) → None    # auto-promote
```

### 5.3 Data Model

#### ProviderEntry

The canonical record for a registered provider.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider_id` | `str` | Yes | Unique identifier (e.g., `"commit-extractor"`, `"coverage-extractor"`) |
| `provider` | `IObservationProvider` | Yes | Provider instance implementing the interface |
| `metric_ids` | `frozenset[str]` | Yes | Set of metric IDs this provider can produce |
| `priority` | `Priority` | Yes | Priority level (PRIMARY, SECONDARY, FALLBACK) |
| `capabilities` | `frozenset[str]` | Yes | Set of capability strings (e.g., `"git-native"`, `"api-required"`) |
| `health_check` | `Optional[Callable[[], bool]]` | No | Callable that returns True if provider is healthy |
| `metadata` | `Dict[str, Any]` | No | Arbitrary provider metadata (version, author, etc.) |
| `registered_at` | `datetime` | Yes | Timestamp of registration |
| `last_extraction_at` | `Optional[datetime]` | No | Timestamp of last successful extraction |
| `is_draining` | `bool` | Yes | Whether provider is in drain state |

#### HealthStatus

| Field | Type | Description |
|-------|------|-------------|
| `status` | `HealthState` | Current health state enum |
| `last_check` | `datetime` | Timestamp of last health check |
| `consecutive_failures` | `int` | Number of consecutive health check failures |
| `uptime_ratio` | `float` | Ratio of successful checks to total checks |

#### HealthState (Enum)

| Value | Description | Eviction Threshold |
|-------|-------------|-------------------|
| `HEALTHY` | Provider operating normally | N/A |
| `DEGRADED` | Provider operational but with elevated latency or reduced confidence | After 5 consecutive degraded checks |
| `UNHEALTHY` | Provider failing health checks or returning invalid data | Evicted after 3 consecutive failures |
| `DRAINING` | Provider shutting down; no new extractions assigned | Evicted when drain complete |
| `UNKNOWN` | Health not yet assessed | Treated as HEALTHY until first check |

#### LatencyStats

| Field | Type | Description |
|-------|------|-------------|
| `p50` | `float` | Median latency in milliseconds |
| `p95` | `float` | 95th percentile latency in milliseconds |
| `p99` | `float` | 99th percentile latency in milliseconds |
| `sample_count` | `int` | Number of latency samples |
| `last_updated` | `datetime` | Timestamp of last update |

#### ConfidenceStats

| Field | Type | Description |
|-------|------|-------------|
| `mean` | `float` | Mean confidence score (0.0–1.0) |
| `min` | `float` | Minimum observed confidence |
| `max` | `float` | Maximum observed confidence |
| `sample_count` | `int` | Number of confidence samples |
| `below_threshold_count` | `int` | Number of extractions below confidence threshold |

---

## 6. Provider Interface

### 6.1 IObservationProvider Protocol

Every observation provider must implement this interface. The protocol is defined using `typing.Protocol` for structural subtyping (OEAS §6.4).

```python
@runtime_checkable
class IObservationProvider(Protocol):
    """OPR §6.1 — Observation Provider interface.

    Every provider that registers with the ObservationProviderRegistry
    must implement this protocol.
    """

    def get_provider_id(self) -> str:
        """Return unique provider identifier."""
        ...

    def get_metric_ids(self) -> frozenset[str]:
        """Return set of metric IDs this provider can produce."""
        ...

    def get_capabilities(self) -> frozenset[str]:
        """Return set of capability strings."""
        ...

    def extract(
        self,
        context: RepositoryContext,
        metric_list: List[str],
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        exclude_bots: bool = False,
        seed: Optional[int] = None,
    ) -> Tuple[ObservationCollection, MetricDataFrame]:
        """Extract observations from repository data.

        Args:
            context: RepositoryContext from ingestion.
            metric_list: Subset of this provider's metrics to extract.
            since: Inclusive start date filter.
            until: Inclusive end date filter.
            exclude_bots: Whether to exclude bot-generated data.
            seed: Optional seed for deterministic extraction.

        Returns:
            Tuple of (ObservationCollection, MetricDataFrame).

        Raises:
            ExtractionError: If extraction fails.
        """
        ...

    def check_health(self) -> bool:
        """Perform a lightweight health check.

        Returns:
            True if provider is operational, False otherwise.
        """
        ...
```

### 6.2 Capability Enumeration

Capabilities are free-form strings that describe provider characteristics. The registry uses capabilities for filtering during discovery.

| Capability | Description | Example Providers |
|-----------|-------------|-------------------|
| `"git-native"` | Extracts data from local Git operations only | CommitExtractor |
| `"file-based"` | Reads local files for data | CoverageExtractor, ComplexityExtractor |
| `"api-required"` | Requires external API access (GitHub, GitLab) | ReviewExtractor, IssueExtractor |
| `"deterministic"` | Produces identical output for identical input + seed | All built-in providers |
| `"streaming"` | Supports chunked/streaming extraction | Future providers |
| `"offline"` | Works without network connectivity | CommitExtractor, ComplexityExtractor |

### 6.3 Provider Validation

Upon registration, the registry validates:

| Check | Rule | Failure |
|-------|------|---------|
| Interface compliance | `isinstance(provider, IObservationProvider)` | `RegistrationError` |
| Unique provider_id | Not already registered | `RegistrationError` |
| Non-empty metric_ids | `len(metric_ids) > 0` | `RegistrationError` |
| Valid metric_ids | All IDs match `M-\d{2}` pattern | `RegistrationError` |
| Health check callable | If provided, `callable(health_check)` | `RegistrationError` |

---

## 7. Registration Protocol

### 7.1 Registration Flow

```
Provider Instance
       │
       ▼
┌─────────────────────────────────────────────┐
│ Registry.register(provider, priority, ...)  │
│                                             │
│  1. Validate interface (IObservationProvider)│
│  2. Validate provider_id uniqueness          │
│  3. Validate metric_ids non-empty            │
│  4. Validate metric_ids format               │
│  5. Build ProviderEntry                      │
│  6. Insert into _providers dict              │
│  7. Update _metric_index                     │
│  8. Update _capability_index                 │
│  9. Update _priority_index                   │
│ 10. Initialize health status (UNKNOWN)       │
│ 11. Log registration event                   │
└─────────────────────────────────────────────┘
```

### 7.2 Registration Interface

```python
class ObservationProviderRegistry:
    def register(
        self,
        provider: IObservationProvider,
        *,
        priority: Priority = Priority.SECONDARY,
        health_check: Optional[Callable[[], bool]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register an observation provider.

        Args:
            provider: Instance implementing IObservationProvider.
            priority: Priority level for this provider.
            health_check: Optional callable for health checking.
            metadata: Optional arbitrary metadata.

        Raises:
            RegistrationError: If validation fails.
        """
        ...

    def unregister(self, provider_id: str) -> None:
        """Remove a provider from the registry.

        Args:
            provider_id: ID of provider to remove.

        Raises:
            KeyError: If provider_id not registered.
        """
        ...
```

### 7.3 Registration Timing

| Mode | When | Use Case |
|------|------|----------|
| Startup registration | During engine initialization, before first extraction | Built-in providers (CommitExtractor, etc.) |
| Dynamic registration | At any time during engine lifetime | Extension providers loaded after startup |
| Deferred registration | After first extraction, on first demand | Lazy-loaded providers requiring external resources |

### 7.4 Registration Order

When multiple providers serve the same metric, registration order combined with priority determines the default fallback chain:

```
Registration order:  CommitExtractor (PRIMARY), CoverageExtractor (SECONDARY), ComplexityExtractor (FALLBACK)
Fallback chain for M-01: [CoverageExtractor, ComplexityExtractor]
Fallback chain for M-02: [CommitExtractor]
Fallback chain for M-07: [ComplexityExtractor]
```

### 7.5 Batch Registration

The registry supports registering multiple providers in a single call for atomicity:

```python
def register_batch(
    self,
    providers: List[Tuple[IObservationProvider, Priority]],
    **kwargs,
) -> None:
    """Register multiple providers atomically.

    If any provider fails validation, no providers are registered
    (transactional rollback).

    Args:
        providers: List of (provider, priority) tuples.
        **kwargs: Additional keyword arguments passed to register().

    Raises:
        RegistrationError: If any provider fails validation.
    """
    ...
```

---

## 8. Discovery Protocol

### 8.1 Discovery Interface

```python
class ObservationProviderRegistry:
    def get_providers_for_metric(
        self,
        metric_id: str,
        *,
        include_unhealthy: bool = False,
    ) -> List[ProviderEntry]:
        """Get all providers that can produce observations for a metric.

        Results are ordered by priority (PRIMARY first, then SECONDARY, then FALLBACK).
        Within the same priority, order follows registration order.

        Args:
            metric_id: Metric identifier (e.g., "M-02").
            include_unhealthy: Whether to include UNHEALTHY providers.

        Returns:
            List of ProviderEntry objects, ordered by priority.
        """
        ...

    def get_primary_provider(
        self,
        metric_id: str,
    ) -> Optional[ProviderEntry]:
        """Get the highest-priority HEALTHY provider for a metric.

        Args:
            metric_id: Metric identifier.

        Returns:
            ProviderEntry if a healthy provider exists, None otherwise.
        """
        ...

    def get_fallback_chain(
        self,
        metric_id: str,
    ) -> List[ProviderEntry]:
        """Get the ordered fallback chain for a metric.

        Returns providers ordered by priority, excluding UNHEALTHY providers.
        If the primary is HEALTHY, the chain includes the primary plus
        all lower-priority healthy providers.

        Args:
            metric_id: Metric identifier.

        Returns:
            Ordered list of ProviderEntry objects forming the fallback chain.
        """
        ...

    def get_providers_by_capability(
        self,
        capability: str,
    ) -> List[ProviderEntry]:
        """Get all providers with a given capability.

        Args:
            capability: Capability string (e.g., "git-native").

        Returns:
            List of ProviderEntry objects with the specified capability.
        """
        ...

    def get_all_providers(self) -> List[ProviderEntry]:
        """Get all registered providers.

        Returns:
            List of all ProviderEntry objects.
        """
        ...

    def get_registered_ids(self) -> List[str]:
        """Get list of all registered provider IDs.

        Returns:
            List of provider_id strings.
        """
        ...

    def is_registered(self, provider_id: str) -> bool:
        """Check if a provider is registered.

        Args:
            provider_id: Provider identifier.

        Returns:
            True if registered, False otherwise.
        """
        ...
```

### 8.2 Discovery Query Semantics

| Query | Returns | Ordering |
|-------|---------|----------|
| `get_providers_for_metric("M-02")` | All providers serving M-02 | By priority, then registration order |
| `get_primary_provider("M-02")` | Highest-priority HEALTHY provider for M-02 | Single result or None |
| `get_fallback_chain("M-02")` | Ordered chain of HEALTHY providers for M-02 | PRIMARY → SECONDARY → FALLBACK |
| `get_providers_by_capability("git-native")` | All providers with git-native capability | By priority |
| `get_all_providers()` | All registered providers | By priority |

### 8.3 Index Maintenance

The registry maintains three secondary indexes for O(1) lookup:

| Index | Key | Value | Updated On |
|-------|-----|-------|-----------|
| `_metric_index` | `metric_id` | `List[str]` (provider_ids) | register/unregister |
| `_capability_index` | `capability` | `List[str]` (provider_ids) | register/unregister |
| `_priority_index` | `Priority` | `List[str]` (provider_ids) | register/unregister/promote/demote |

---

## 9. Prioritization Model

### 9.1 Priority Levels

| Level | Value | Description | Behavior |
|-------|-------|-------------|----------|
| `PRIMARY` | 0 | Default provider for a metric | Always attempted first |
| `SECONDARY` | 1 | Backup provider with full capability | Used when PRIMARY fails or is unhealthy |
| `FALLBACK` | 2 | Last-resort provider | Used when both PRIMARY and SECONDARY fail |

### 9.2 Priority Resolution Algorithm

When extracting observations for a metric, the registry resolves the provider chain as follows:

```
FUNCTION resolve_chain(metric_id):
    candidates = _metric_index[metric_id]
    healthy = filter(candidates, status != UNHEALTHY)
    sorted = sort_by_priority(healthy)
    RETURN sorted
```

### 9.3 Priority Adjustment

Priority can be adjusted at runtime without unregistering/reregistering:

```python
def set_priority(self, provider_id: str, new_priority: Priority) -> None:
    """Change a provider's priority at runtime.

    Args:
        provider_id: ID of provider to adjust.
        new_priority: New priority level.

    Raises:
        KeyError: If provider_id not registered.
    """
    ...
```

### 9.4 Promotion and Demotion

| Action | Trigger | Effect |
|--------|---------|--------|
| Auto-promote | Primary provider becomes UNHEALTHY | Highest-priority SECONDARY promoted to effective primary |
| Auto-promote | All SECONDARY providers become UNHEALTHY | Highest-priority FALLBACK promoted |
| Manual promote | `promote(provider_id)` | Priority level decreased by one (FALLBACK→SECONDARY, SECONDARY→PRIMARY) |
| Manual demote | `demote(provider_id)` | Priority level increased by one (PRIMARY→SECONDARY, SECONDARY→FALLBACK) |

### 9.5 Same-Priority Tiebreaking

When multiple providers share the same priority level, the registry uses:

1. **Registration order** — earlier-registered providers are preferred.
2. **Health status** — HEALTHY preferred over DEGRADED.
3. **Latency** — lower p95 latency preferred.
4. **Provider ID** — lexicographic order as final tiebreaker (deterministic).

### 9.6 Priority Enforcement Rules

| Rule | Description |
|------|-------------|
| PE-1 | At most one provider can be PRIMARY per metric_id |
| PE-2 | If multiple providers are PRIMARY for the same metric, registration order determines precedence |
| PE-3 | Priority changes are logged and auditable |
| PE-4 | Priority cannot be set to a value outside the Priority enum |

---

## 10. Health Monitoring System

### 10.1 Health States

```
                    ┌──────────┐
            ┌──────►│ HEALTHY  │◄──────┐
            │       └────┬─────┘       │
            │            │             │
   check passes    check fails   check passes
            │            │             │
            │            ▼             │
            │       ┌──────────┐       │
            │       │ DEGRADED │───────┘
            │       └────┬─────┘
            │            │
            │     3 consecutive
            │       failures
            │            │
            │            ▼
   recovery  │       ┌──────────┐
  + check    │       │UNHEALTHY │
   passes    │       └────┬─────┘
            │            │
            │     3 consecutive
            │       failures
            │            │
            │            ▼
            │       ┌──────────┐
            └───────│ DRAINING │
                    └──────────┘
```

### 10.2 Health Check Triggers

| Trigger | Timing | Scope |
|---------|--------|-------|
| Post-extraction check | After every successful extraction | Targeted (extracting provider only) |
| Periodic check | Configurable interval (default: 60s) | All registered providers |
| Pre-extraction check | Before attempting extraction from a provider | Targeted (candidate provider) |
| Manual check | Explicit `check_health(provider_id)` call | Targeted |
| Recovery check | After provider restart | Targeted |

### 10.3 Health Check Implementation

```python
class HealthMonitor:
    def check_health(self, provider_id: str) -> HealthStatus:
        """Execute health check for a provider.

        Health check sequence:
        1. If provider has health_check callable, invoke it
        2. Otherwise, attempt a lightweight extraction (dry-run)
        3. Record result and update health status

        Args:
            provider_id: ID of provider to check.

        Returns:
            Updated HealthStatus.
        """
        ...

    def record_extraction(
        self,
        provider_id: str,
        latency_ms: float,
        confidence: float,
        success: bool,
    ) -> None:
        """Record extraction outcome for health tracking.

        Args:
            provider_id: ID of provider that performed extraction.
            latency_ms: Extraction latency in milliseconds.
            confidence: Confidence score of produced observations (0.0–1.0).
            success: Whether extraction succeeded.
        """
        ...

    def periodic_check(self) -> List[HealthEvent]:
        """Run health checks on all registered providers.

        Returns:
            List of HealthEvent objects for state transitions.
        """
        ...
```

### 10.4 Health Event

| Field | Type | Description |
|-------|------|-------------|
| `provider_id` | `str` | Affected provider |
| `previous_state` | `HealthState` | State before transition |
| `new_state` | `HealthState` | State after transition |
| `timestamp` | `datetime` | When transition occurred |
| `reason` | `str` | Human-readable reason |
| `consecutive_failures` | `int` | Failure count at transition |

### 10.5 Eviction Rules

| Condition | Action | Recovery |
|-----------|--------|----------|
| `consecutive_failures >= 3` | Transition to UNHEALTHY | Manual restart required |
| `consecutive_failures >= 5` | Evict from registry | Re-register after fix |
| `mean_confidence < 0.3` for 10+ extractions | Transition to DEGRADED | Automatic on improvement |
| `p99_latency > 30000ms` | Transition to DEGRADED | Automatic on improvement |
| Provider in DRAINING state + drain complete | Evict from registry | N/A |

### 10.6 Latency Tracking

The registry maintains a rolling window of latency measurements (last 100 extractions) and computes:

| Metric | Calculation | Use |
|--------|-------------|-----|
| p50 | Median of rolling window | Baseline performance |
| p95 | 95th percentile of rolling window | SLA monitoring |
| p99 | 99th percentile of rolling window | Outlier detection |
| trend | Slope of latency over time | Degradation detection |

### 10.7 Confidence Tracking

| Metric | Calculation | Use |
|--------|-------------|-----|
| mean | Average confidence across extractions | Overall quality |
| min | Minimum observed confidence | Worst-case quality |
| below_threshold_count | Extractions with confidence < 0.5 | Consistency check |
| trend | Slope of confidence over time | Quality degradation detection |

---

## 11. Lifecycle Management

### 11.1 Provider Lifecycle States

```
┌──────────┐    register()    ┌──────────┐
│   None   │ ────────────────►│REGISTERED│
└──────────┘                  └────┬─────┘
                                   │
                        ┌──────────┼──────────┐
                        │          │          │
                   extract()   health_check  unregister()
                        │          │          │
                        ▼          ▼          ▼
                  ┌──────────┐ ┌──────────┐ ┌──────────┐
                  │EXTRACTING│ │ CHECKING │ │REMOVED   │
                  └────┬─────┘ └────┬─────┘ └──────────┘
                       │            │
                  done  │       done │
                       │            │
                       ▼            ▼
                  ┌──────────────────────┐
                  │     REGISTERED       │
                  │  (idle, healthy)     │
                  └──────────────────────┘
```

### 11.2 Graceful Shutdown

When the registry shuts down (e.g., pipeline completion or explicit shutdown call):

```python
def shutdown(self, timeout_seconds: float = 30.0) -> None:
    """Gracefully shut down all providers.

    Shutdown sequence:
    1. Set all providers to DRAINING state
    2. Wait for in-flight extractions to complete (up to timeout)
    3. Call provider.shutdown() if available
    4. Evict all providers
    5. Log shutdown completion

    Args:
        timeout_seconds: Maximum time to wait for drain.
    """
    ...
```

### 11.3 Provider Restart

```python
def restart_provider(self, provider_id: str) -> None:
    """Restart a provider after failure recovery.

    Restart sequence:
    1. Verify provider is registered and UNHEALTHY
    2. Call provider.restart() if available, else re-initialize
    3. Run health check
    4. If healthy, restore to previous priority level
    5. If unhealthy, remain UNHEALTHY

    Args:
        provider_id: ID of provider to restart.

    Raises:
        KeyError: If provider_id not registered.
    """
    ...
```

### 11.4 Drain Protocol

| Phase | Action | Duration |
|-------|--------|----------|
| 1. Announce drain | Set `is_draining = True` | Instant |
| 2. Stop new work | Registry stops assigning new extractions | Instant |
| 3. Wait for in-flight | Existing extractions complete | Up to `timeout_seconds` |
| 4. Finalize | Provider performs cleanup | Provider-dependent |
| 5. Evict | Remove from registry | Instant |

### 11.5 Recovery Protocol

| Phase | Action | Condition |
|-------|--------|-----------|
| 1. Detect failure | Health check fails | Automatic |
| 2. Mark UNHEALTHY | Update health status | Automatic |
| 3. Promote fallback | Next-priority provider takes over | Automatic |
| 4. Attempt restart | `restart_provider()` called | Manual or scheduled |
| 5. Verify recovery | Health check passes | Automatic |
| 6. Restore priority | Return to previous priority level | Automatic |

---

## 12. Integration with ExtractionEngine

### 12.1 Updated ExtractionEngine

The v1.6 `ExtractionEngine` replaces direct `CommitExtractor` usage with registry-mediated provider selection:

```python
class ExtractionEngine:
    def __init__(
        self,
        *,
        registry: ObservationProviderRegistry,
        store: Optional[ObservationStore] = None,
        metric_extractor: Optional[MetricExtractor] = None,
    ) -> None:
        self._registry = registry
        self._store = store
        self._metric_extractor = metric_extractor or MetricExtractor()

    def extract(
        self,
        context: RepositoryContext,
        metric_list: List[str],
        since: Optional[datetime.datetime] = None,
        until: Optional[datetime.datetime] = None,
        exclude_bots: bool = False,
        seed: Optional[int] = None,
    ) -> Tuple[ObservationCollection, MetricDataFrame]:
        """Extract observations using registry-mediated provider selection.

        For each metric in metric_list:
          1. Query registry for fallback chain
          2. Attempt extraction with highest-priority provider
          3. On failure, attempt next provider in chain
          4. Record health metrics for each attempt
          5. Merge results from all successful extractions
        """
        ...
```

### 12.2 Extraction Flow

```
metric_list: ["M-01", "M-02", "M-06"]
       │
       ▼
┌──────────────────────────────────────────────────────┐
│ For each metric_id in metric_list:                   │
│                                                      │
│  chain = registry.get_fallback_chain(metric_id)      │
│                                                      │
│  for provider_entry in chain:                        │
│    try:                                              │
│      start = time.monotonic()                        │
│      collection, mdf = provider.extract(context, ...)│
│      latency = time.monotonic() - start              │
│      confidence = compute_confidence(collection)     │
│      registry.record_extraction(provider_id, ...)    │
│      merge into result_collection                    │
│      break  # success, stop trying fallbacks         │
│    except ExtractionError:                           │
│      registry.record_extraction(provider_id, ...,    │
│                                 success=False)       │
│      continue  # try next provider in chain          │
│                                                      │
└──────────────────────────────────────────────────────┘
       │
       ▼
  Merge all per-metric collections into unified result
```

### 12.3 Multi-Metric Extraction Strategy

When a provider serves multiple metrics, the registry avoids redundant extraction:

| Strategy | Description |
|----------|-------------|
| Single-pass extraction | Provider extracts all requested metrics in one call |
| Per-metric delegation | Registry splits metrics across providers, each extracting independently |
| Hybrid | Provider extracts its full metric set; registry filters to requested subset |

The default strategy is **single-pass extraction** — the registry selects the highest-priority provider that covers the most requested metrics and delegates extraction to it. Remaining metrics are handled by lower-priority providers.

### 12.4 Observation Merging

When multiple providers contribute observations for the same metric (e.g., fallback scenarios), the registry ensures:

| Rule | Description |
|------|-------------|
| No duplicate observation IDs | Deterministic IDs prevent collisions (ODSS §10.2) |
| Provenance preserved | Each observation retains its source provider_id |
| Temporal ordering maintained | Merged observations sorted by timestamp |
| Confidence weighted | Lower-priority provider observations flagged with reduced confidence |

---

## 13. Error Handling and Fallback Strategy

### 13.1 Error Taxonomy

| Error Class | Description | Registry Response |
|------------|-------------|-------------------|
| `RegistrationError` | Provider validation failed during registration | Reject registration, log error |
| `ExtractionError` | Provider failed during extraction | Attempt next provider in fallback chain |
| `HealthCheckError` | Health check itself failed | Treat as UNHEALTHY, do not evict immediately |
| `ProviderNotFoundError` | Requested provider_id not registered | Raise `KeyError` |
| `MetricNotServedError` | No registered provider serves the requested metric | Raise `ExtractionError` with clear message |
| `DrainTimeoutError` | Provider did not complete drain within timeout | Force-evict provider |

### 13.2 Fallback Strategy

```
extract(metric_id="M-02"):
    chain = registry.get_fallback_chain("M-02")
    # chain = [CommitExtractor (PRIMARY)]

    for provider in chain:
        try:
            result = provider.extract(...)
            return result
        except ExtractionError as e:
            log.warning(f"Provider {provider.provider_id} failed: {e}")
            registry.record_extraction(
                provider.provider_id,
                success=False,
                ...
            )
            continue

    # All providers failed
    raise ExtractionError(
        f"No provider could extract metric {metric_id}. "
        f"Attempted: {[p.provider_id for p in chain]}"
    )
```

### 13.3 Confidence-Based Fallback

Even when extraction succeeds, the registry may trigger fallback if confidence is below threshold:

| Confidence | Action |
|-----------|--------|
| >= 0.7 | Accept observations, record confidence |
| 0.5 – 0.7 | Accept observations, log warning, record confidence |
| 0.3 – 0.5 | Accept observations, attempt fallback provider for comparison |
| < 0.3 | Reject observations, attempt fallback provider |

### 13.4 Error Propagation Rules

| Rule | Description |
|------|-------------|
| EP-1 | ExtractionError from a provider does not propagate to caller if fallback succeeds |
| EP-2 | ExtractionError propagates only if all providers in chain fail |
| EP-3 | RegistrationError always propagates immediately |
| EP-4 | All errors are logged with provider_id, metric_id, and timestamp |
| EP-5 | Error counts are tracked in provider health stats |

---

## 14. Concurrency Model

### 14.1 Thread Safety

The registry is thread-safe for the following operations:

| Operation | Thread-Safe | Mechanism |
|-----------|------------|-----------|
| `register()` | Yes | Lock on `_providers` dict |
| `unregister()` | Yes | Lock on `_providers` dict |
| `get_*()` | Yes | Read-only access; snapshot semantics |
| `record_extraction()` | Yes | Lock on health stats |
| `check_health()` | Yes | Lock on health status |
| `set_priority()` | Yes | Lock on `_priority_index` |
| `shutdown()` | Yes | Lock on entire registry |

### 14.2 Extraction Concurrency

Multiple metrics can be extracted concurrently. The registry supports concurrent extraction by:

| Mechanism | Description |
|-----------|-------------|
| Per-metric isolation | Each metric extraction is independent |
| Health stat atomicity | Extraction recording uses atomic operations |
| Provider locking | Individual provider extraction is serialized (provider-level lock) |

### 14.3 Read-Write Isolation

Discovery operations (reads) do not block on registration operations (writes). The registry uses a copy-on-write strategy for index updates:

1. Reads operate on the current snapshot of indexes.
2. Writes build new index copies atomically.
3. Atomic swap replaces the old snapshot with the new one.

---

## 15. Configuration

### 15.1 Registry Configuration Schema

```yaml
observation_provider_registry:
  health_check:
    enabled: true
    interval_seconds: 60
    timeout_seconds: 5
    unhealthy_threshold: 3
    eviction_threshold: 5
    degraded_confidence_threshold: 0.5
    degraded_latency_threshold_ms: 10000

  fallback:
    enabled: true
    confidence_threshold: 0.5
    max_retries_per_provider: 1
    retry_delay_ms: 100

  latency_tracking:
    enabled: true
    window_size: 100

  confidence_tracking:
    enabled: true
    window_size: 100
    low_confidence_threshold: 0.3

  shutdown:
    drain_timeout_seconds: 30
    force_evict_on_timeout: true

  logging:
    log_registrations: true
    log_extractions: true
    log_health_transitions: true
    log_priority_changes: true
```

### 15.2 Configuration Defaults

| Parameter | Default | Description |
|-----------|---------|-------------|
| `health_check.interval_seconds` | `60` | Seconds between periodic health checks |
| `health_check.timeout_seconds` | `5` | Timeout for individual health check |
| `health_check.unhealthy_threshold` | `3` | Consecutive failures before UNHEALTHY |
| `health_check.eviction_threshold` | `5` | Consecutive failures before eviction |
| `fallback.confidence_threshold` | `0.5` | Minimum confidence to accept observations |
| `latency_tracking.window_size` | `100` | Rolling window for latency percentiles |
| `shutdown.drain_timeout_seconds` | `30` | Maximum time to wait for drain |

---

## 16. Architectural Invariants

| ID | Invariant | Rationale | Verification |
|----|-----------|-----------|-------------|
| INV-1 | Every metric_id with observations has at least one registered provider | No orphaned data | Registration validation |
| INV-2 | Provider priority changes are logged and auditable | Debuggability | Audit log inspection |
| INV-3 | Health state transitions are idempotent | Determinism (OEAS §6.2) | Idempotency test |
| INV-4 | Registry queries return consistent results within a single extraction pass | Reproducibility | Snapshot isolation |
| INV-5 | Provider extraction is serialized per provider | Data integrity | Per-provider lock |
| INV-6 | Evicted providers cannot receive new extraction assignments | Safety | Eviction check in resolve_chain |
| INV-7 | Graceful shutdown drains all in-flight extractions | No data loss | Shutdown test |
| INV-8 | No provider has knowledge of other providers | Independence (§4.2) | Interface inspection |

---

## 17. Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Registration latency | < 1ms | Time to register a single provider |
| Discovery latency | < 0.1ms | Time to resolve fallback chain for one metric |
| Health check latency | < 5ms per provider | Time to execute one health check |
| Index rebuild time | < 1ms | Time to rebuild indexes after registration change |
| Extraction overhead | < 1% of extraction time | Registry overhead vs. direct extraction |
| Memory overhead | < 10KB per registered provider | Registry memory footprint |

---

## 18. Security Considerations

| Consideration | Approach |
|--------------|----------|
| Provider isolation | Providers cannot access registry internals or other providers |
| No remote providers | v1.6 is offline-only; no network-based provider loading |
| No code execution | Health checks use pre-registered callables, not arbitrary code |
| Audit trail | All registration, extraction, and health events are logged |
| No secrets in metadata | Provider metadata must not contain credentials |

---

## 19. Compatibility with v1.5

### 19.1 Backward Compatibility

| v1.5 Component | v1.6 Compatibility | Mechanism |
|----------------|-------------------|-----------|
| CommitExtractor | Fully compatible | Implements IObservationProvider |
| ExtractionEngine | Breaking change | Constructor requires `registry` parameter |
| DetectorRegistry | Unchanged | Independent registry |
| ObservationStore | Unchanged | Independent component |

### 19.2 Adapter for v1.5 ExtractionEngine

For migration, a compatibility adapter allows the v1.6 registry to wrap the v1.5 `ExtractionEngine` behavior:

```python
class LegacyExtractionAdapter:
    """Wrap v1.5 ExtractionEngine as an IObservationProvider.

    Enables gradual migration: existing code continues working
    while new providers are registered alongside.
    """
    def __init__(self, legacy_engine: ExtractionEngine): ...
```

### 19.3 Deprecation Schedule

| Feature | v1.5 | v1.6 | v2.0 |
|---------|------|------|------|
| Direct CommitExtractor usage | Default | Deprecated | Removed |
| Hardcoded provider wiring | Default | Deprecated | Removed |
| Registry-mediated extraction | N/A | Default | Default |

---

## 20. Migration Strategy

### 20.1 Phase 1: Registry Foundation

| Task | Dependency | Deliverable |
|------|-----------|-------------|
| Define IObservationProvider protocol | None | Protocol definition |
| Implement ProviderEntry dataclass | None | Data model |
| Implement RegistrationModule | IObservationProvider | Registration logic |
| Implement DiscoveryModule | RegistrationModule | Discovery queries |
| Implement PriorityEngine | RegistrationModule | Priority resolution |
| Implement HealthMonitor | RegistrationModule | Health tracking |
| Implement LifecycleManager | All modules | Lifecycle orchestration |

### 20.2 Phase 2: CommitExtractor Adaptation

| Task | Dependency | Deliverable |
|------|-----------|-------------|
| Adapt CommitExtractor to IObservationProvider | IObservationProvider | Wrapped provider |
| Register CommitExtractor as PRIMARY for M-02, M-06 | CommitExtractor adapter | Registration |
| Integration test: extraction via registry | Registration | Test suite |

### 20.3 Phase 3: ExtractionEngine Refactor

| Task | Dependency | Deliverable |
|------|-----------|-------------|
| Refactor ExtractionEngine to accept registry | Registry | Updated engine |
| Implement fallback chain extraction | ExtractionEngine | Fallback logic |
| Implement confidence-based fallback | Fallback logic | Confidence routing |
| Unit and integration tests | All components | Test suite |

### 20.4 Phase 4: New Provider Registration

| Task | Dependency | Deliverable |
|------|-----------|-------------|
| Adapt CoverageExtractor to IObservationProvider | IObservationProvider | Provider |
| Adapt ReviewExtractor to IObservationProvider | IObservationProvider | Provider |
| Adapt IssueExtractor to IObservationProvider | IObservationProvider | Provider |
| Adapt ComplexityExtractor to IObservationProvider | IObservationProvider | Provider |
| Register all providers with appropriate priorities | All adapters | Registration config |

---

## 21. Future Evolution

### 21.1 v1.6 Planned Extensions

| Feature | Description | Dependencies |
|---------|-------------|-------------|
| Provider plugins | Load providers from external packages | Plugin architecture |
| Provider versioning | Semver for provider compatibility | Version negotiation |
| Metrics dashboard | Real-time provider health visualization | API expansion |
| Provider analytics | Historical performance tracking | Persistent storage |

### 21.2 v2.0 Capabilities

| Feature | Description | Dependencies |
|---------|-------------|-------------|
| Distributed providers | Providers across network boundaries | RPC framework |
| Provider marketplace | Community-contributed providers | Auth and trust model |
| Adaptive priority | ML-based priority adjustment | Training data |
| Provider composition | Chain providers for complex extraction | DAG execution |

### 21.3 Deprecation Path

| Feature | v1.5 | v1.6 | v2.0 |
|---------|------|------|------|
| In-memory registry only | N/A (new) | Default | Optional persistent |
| Single-process only | N/A (new) | Default | Distributed |
| Manual health checks | N/A (new) | Default | Auto-calibrated |

---

## 22. Decision Log

| ID | Decision | Date | Rationale |
|----|----------|------|-----------|
| OPR-001 | Protocol-based provider interface | 2026-07-03 | Structural subtyping, no inheritance coupling |
| OPR-002 | Three-level priority model | 2026-07-03 | Balances simplicity with adequate fallback depth |
| OPR-003 | Rolling-window latency tracking | 2026-07-03 | Captures recent performance without unbounded memory |
| OPR-004 | Confidence-based fallback trigger | 2026-07-03 | Low-confidence data is worse than no data |
| OPR-005 | Transactional batch registration | 2026-07-03 | Prevents partial registration on validation failure |
| OPR-006 | No remote provider support in v1.6 | 2026-07-03 | Offline-first philosophy; network providers deferred |
| OPR-007 | Per-provider extraction serialization | 2026-07-03 | Prevents concurrent state mutation in providers |
| OPR-008 | Copy-on-write index updates | 2026-07-03 | Read-write isolation without blocking discovery |

---

## 23. Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|----|------|------------|--------|------------|
| R-1 | Provider deadlock during extraction | LOW | HIGH | Per-provider timeout, watchdog timer |
| R-2 | Health check overhead degrades performance | LOW | MEDIUM | Async health checks, configurable interval |
| R-3 | Priority inversion causes suboptimal routing | LOW | MEDIUM | Priority enforcement rules (§9.6) |
| R-4 | Fallback chain exhaustion (all providers fail) | MEDIUM | HIGH | Clear error message, metric-level fallback to null observations |
| R-5 | Race condition during registration + extraction | LOW | HIGH | Copy-on-write indexes, atomic snapshots |
| R-6 | Memory growth from latency/confidence history | LOW | LOW | Rolling window with max size |

---

## 24. Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-1 | Providers register successfully with valid inputs | Unit test: register + get |
| AC-2 | Registration rejects invalid providers | Unit test: RegistrationError raised |
| AC-3 | Discovery returns providers ordered by priority | Unit test: ordering verification |
| AC-4 | Fallback chain excludes UNHEALTHY providers | Integration test: evict + query |
| AC-5 | Health status transitions correctly | Unit test: state machine |
| AC-6 | Latency tracking computes accurate percentiles | Unit test: known values |
| AC-7 | ExtractionEngine uses registry for provider selection | Integration test: full pipeline |
| AC-8 | Fallback triggers on primary failure | Integration test: mock failure |
| AC-9 | Graceful shutdown drains in-flight extractions | Integration test: concurrent extraction + shutdown |
| AC-10 | Registry handles 100+ providers without performance degradation | Load test: registration + discovery latency |
| AC-11 | All v1.5 tests continue to pass | Regression test suite |
| AC-12 | CommitExtractor works through registry | Integration test: extraction via registry |

---

## 25. Glossary

| Term | Definition |
|------|-----------|
| Observation Provider | A component that extracts observations from a data source and produces ObservationCollection + MetricDataFrame |
| Provider Registry | Central component managing registration, discovery, and lifecycle of observation providers |
| Fallback Chain | Ordered list of providers for a metric, from highest to lowest priority, excluding unhealthy providers |
| Priority Level | Classification of provider precedence: PRIMARY, SECONDARY, or FALLBACK |
| Health Status | Current operational state of a provider: HEALTHY, DEGRADED, UNHEALTHY, DRAINING, UNKNOWN |
| Eviction | Automatic removal of a provider from the registry due to sustained health failures |
| Drain | Graceful shutdown state where a provider completes in-flight work without accepting new assignments |
| Confidence Score | Numeric measure (0.0–1.0) of observation quality produced by a provider |
| Provider Entry | Registry record containing provider instance, metadata, and health state |
| Capability | Free-form string describing provider characteristics (e.g., "git-native", "api-required") |

---

## 26. Appendix — Cross-References

### 26.1 Referenced MIIE Specifications

| Document ID | Document Title | Relevance to OPR |
|------------|---------------|-----------------|
| OEAS-v1.5 | Observation Engine Architecture Specification | Defines extraction layer that OPR enhances; §14.1–§14.5 specify planned extractors |
| ODSS-v1.0 | Observation Data Schema Specification | Defines Observation model that providers produce; §10 defines deterministic IDs |
| DES-v2.0 | Detector Execution Specification | Downstream consumer of provider output; §19 defines confidence contracts |
| IMS-v1.0 | Implementation and Migration Specification | Migration phases that OPR Phase 1–4 extend |
| PRD-v1.5 | Observation Engine PRD | §39.1 defines v1.6 extensions that OPR fulfills |
| DSVP-v1.0 | Detector Scientific Validation Protocol | Validation methodology applicable to provider confidence |
| BES-v1.0 | Benchmark Evolution Specification | Benchmark suites that will exercise provider extraction |

### 26.2 Planned v1.6 Companion Specifications

| Document ID | Document Title | Relationship to OPR |
|------------|---------------|-------------------|
| OPA-v1.0 | Observation Provider Architecture | Defines how providers are architecturally structured; OPR defines the registry that manages them |
| OPC-v1.0 | Observation Provider Contracts | Defines interface contracts for providers; OPR validates against these contracts at registration |
| OSMS-v1.0 | Observation System Management Specification | Defines operational management of the full observation system; OPR provides the registry subsystem |

### 26.3 Referenced Source Code

| File | Component | OPR Reference |
|------|-----------|---------------|
| `src/miie/processing/detection/registry.py` | DetectorRegistry | Reference pattern for registry design (§3.2) |
| `src/miie/processing/extraction/engine.py` | ExtractionEngine | Target for registry integration (§12) |
| `src/miie/processing/extraction/commit_extractor.py` | CommitExtractor | First provider to register with OPR |
| `src/miie/contracts/interfaces.py` | Protocol definitions | OPR protocol extends this pattern (§6.1) |
| `src/miie/processing/observation/models.py` | Observation data model | Output contract for all providers (§6.1) |

---

*End of Document*
