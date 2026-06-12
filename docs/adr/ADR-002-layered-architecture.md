# ADR-002: Layered Architecture

## Status
Accepted

## Context
MIIE v1.0 requires a clean, maintainable architecture that separates concerns and enforces module boundaries. The Technical Requirements Document (TRD) defines a 6-layer architecture with specific responsibilities for each layer. Without enforcing these boundaries through actual code structure and import rules, the system risks becoming a tangled monolith where changes in one area unexpectedly affect others, violating the principles of determinism, reproducibility, and research infrastructure first outlined in ADR-001.

## Decision
We will implement a strict layered architecture with the following layers, ordered from highest (most external) to lowest (most internal):

1. **Interface Layer** - Handles external interactions (CLI, API, configuration, registry)
2. **Orchestration Layer** - Manages workflow execution, job state, and pipeline coordination
3. **Processing Layer** - Executes the core analysis pipeline (ingestion → extraction → segmentation → detection → scoring → evidence → explanation → export)
4. **Benchmark Subsystem** - Manages benchmark dataset generation, ground truth, execution, and evaluation
5. **Storage Layer** - Provides filesystem abstraction for persistent storage
6. **Common Layer** - Provides shared utilities, constants, and cross-cutting concerns

Additionally, we will implement two dependency-free layers:
- **Contracts Layer** - Defines DTOs, interfaces, and validation rules for layer communication
- **Schemas Layer** - Defines JSON schemas and dataclasses for data validation and serialization

## Alternatives Considered

### Alternative 1: Monolithic Structure
Keep all code in a flat structure or few large modules.
- **Rejected because:** Violates TRD-defined module boundaries, makes code difficult to understand and maintain, increases risk of unintended side effects, and hinders independent team development.

### Alternative 2: Traditional 3-Layer Architecture (Presentation-Business-Data)
Standard web application architecture.
- **Rejected because:** Does not align with TRD's specific layer definitions, doesn't accommodate the benchmark subsystem as a first-class concern, and fails to separate processing concerns adequately.

### Alternative 3: Plugin-Based Architecture
Core system with pluggable components for metrics, detectors, etc.
- **Rejected because:** While extensibility is valued, the TRD specifies a frozen set of metrics and detectors for v1.0. Plugin architecture would add unnecessary complexity for the v1.0 scope and could violate the deterministic requirement if not carefully implemented.

### Alternative 4: Hexagonal Architecture (Ports and Adapters)
Separate core application logic from external concerns via ports and adapters.
- **Rejected because:** Although aligned with principles of separation, it doesn't map cleanly to the TRD's specific layer definitions and would require significant reinterpretation of the requirements.

## Consequences

### Positive
- **Clear Separation of Concerns:** Each layer has a single, well-defined responsibility
- **Enforced Module Boundaries:** Import rules prevent inappropriate coupling between layers
- **Improved Maintainability:** Changes within a layer are less likely to affect other layers
- **Better Testability:** Layers can be tested in isolation with mocks for dependencies
- **Aligns with TRD:** Directly implements the architecture defined in TRD Section 2.1
- **Supports Team Organization:** Clear ownership boundaries match the responsibility matrix in TRD Section 27
- **Enables Independent Development:** Teams can work on different layers with minimal coordination
- **Reduces Cognitive Load:** Developers only need to understand their layer and its direct dependencies

### Negative
- **Initial Overhead:** Requires upfront investment in defining layers and import rules
- **Potential for Indirection:** Simple operations may require crossing multiple layers
- **Refactoring Effort:** Existing code (if any) may need restructuring to fit layers
- **Strictness May Feel Constraining:** Developers may perceive limitations on "quick fixes"

### Mitigations
- **Architecture Documentation:** Clear docs (this ADR, dependency_rules.md, import_policy.md) reduce confusion
- **Automated Enforcement:** Architecture tests prevent violations from entering codebase
- **Gradual Migration:** For existing code, apply rule opportunistically when files are modified
- **Well-Defined Escape Hatches:** ADR-XXX-import-exception.md process for justified exceptions
- **Training:** Onboarding includes architecture overview and import policy

## Related Documents
- TRD_MIIE_v1.0.md Section 2.1 (High-Level Architecture)
- ADR-001-project-foundations.md (Project Foundations)
- dependency_rules.md (Formal Layer Dependency Specifications)
- import_policy.md (Import Statement Governance)
- module_responsibilities.detailed responsibility definitions per layer
- tests/architecture/ (Automated architecture validation tests)

## Implications
- All new code must comply with this layered structure
- Architecture compliance is gates for merging code (via CI/CD)
- Violations require architectural review and justification
- This ADR may be superseded only by formal architecture change process