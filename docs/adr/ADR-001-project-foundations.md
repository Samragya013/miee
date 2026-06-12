# ADR-001: Project Foundations

**Date:** 2026-06-08  
**Status:** Accepted  
**Author:** Governance Sprint Team  
**Version:** 1.0.0  

---

## Context

The Measurement Integrity Intelligence Engine (MIIE) is a research-grade system that evaluates whether software engineering metrics remain trustworthy representations of the constructs they claim to measure. This decision addresses the fundamental architectural principles that define v1.0 of the system.

---

## Decision

MIIE Version 1.0 is:

### CLI-First

**Decision:** The command-line interface is the primary user interface for all capabilities. The REST API is secondary and must be built on top of CLI logic.

**Rationale:**

1. **Research reproducibility:** CLI commands can be scripted, versioned, and documented in papers with exact reproducibility.
2. **Deterministic execution:** CLI ensures consistent argument parsing without HTTP layer complexity.
3. **Transparency:** Users see exactly what command they ran and can reproduce it.
4. **Simplicity:** Single entry point reduces code paths and potential failure modes.
5. **Community expectation:** Research tools are expected to be CLI-first for reproducibility.

**Consequences:**

- **Positive:** Deterministic, reproducible execution; simple architecture; easy documentation.
- **Negative:** API must be built on CLI logic (not direct module calls); REST API is derivative.
- **Obligation:** All CLI commands must have exact API equivalents; CLI must not contain business logic.

### Offline-First

**Decision:** The system must execute all core capabilities without network access, external SaaS, or database connectivity.

**Rationale:**

1. **Reproducibility:** Network access introduces non-determinism (timeouts, rate limits, changed endpoints).
2. **Accessibility:** Researchers often work in air-gapped environments (conferences, secure facilities).
3. **Privacy:** Repository data may be sensitive; users may not want to send it to external services.
4. **Simplicity:** Filesystem-only storage reduces complexity and failure modes.
5. **Longevity:** Research artifacts must be reproducible years later; network dependencies may break.

**Consequences:**

- **Positive:** Bitwise-identical reproducibility; no external dependencies; works in air-gapped environments.
- **Negative:** No real-time analytics; no collaborative features; no cloud backups.
- **Obligation:** All analysis must work with local Git repositories only; remote clone is the only network operation.

### Deterministic

**Decision:** Every analysis must be bitwise-identical when re-run with identical inputs, configuration, and random seed.

**Rationale:**

1. **Scientific validity:** Research findings must be reproducible by independent teams.
2. **Auditability:** Users must be able to verify that their analysis was correct.
3. **Debugging:** Identical inputs → identical outputs simplifies troubleshooting.
4. **Benchmarking:** Detector performance must be measured on identical runs.
5. **Trust:** Users must trust that outputs are not arbitrarily changing.

**Consequences:**

- **Positive:** Reproducible research; auditable results; debuggable system.
- **Negative:** Must sort all collections before iteration; must use fixed random seeds; platform variance must be mitigated.
- **Obligation:** All random operations use numpy.random.RandomState(seed) or random.seed(seed); seed is required parameter in all stochastic modules; dependency versions must be pinned.

### Benchmark-Driven

**Decision:** Detector algorithms are validated exclusively through standardized benchmark suites before deployment.

**Rationale:**

1. **Scientific rigor:** Detectors must be validated against ground truth, not intuition.
2. **Objectivity:** Benchmarks provide objective criteria for precision, recall, and F1.
3. **Transparency:** Benchmark results are published and auditable.
4. **Regression prevention:** Benchmarks catch performance degradation.
5. **Credibility:** Research community expects benchmark-validated methods.

**Consequences:**

- **Positive:** Objectively validated detectors; regression-free evolution; transparent performance metrics.
- **Negative:** Detector development cannot begin before benchmark exists; benchmark development is slow.
- **Obligation:** No detector code is written before benchmark dataset exists; all detector thresholds tuned against benchmark; benchmark results published with paper.

### Research-Oriented

**Decision:** The system is built as research infrastructure, not as a product or service. Prioritize scientific validity, transparency, and extensibility over user convenience or commercial features.

**Rationale:**

1. **Mission alignment:** MIIE exists to advance measurement integrity research, not to build a commercial product.
2. **Community expectations:** Research tools are expected to be open-source, transparent, and extensible.
3. **Long-term sustainability:** Open-source research tools have longer lifespan than commercial products.
4. **Reproducibility:** Open-source enables independent verification of results.
5. **Academic credit:** Researchers need citable, open-source artifacts.

**Consequences:**

- **Positive:** Open-source codebase; transparent algorithms; community contribution; academic citability.
- **Negative:** No GUI investment; no SaaS features; limited commercialization options.
- **Obligation:** CLI is primary interface; no GUI investment; all outputs suitable for papers; extensibility via registry pattern, not plugin marketplace.

---

## Rejected Alternatives

### Alternative 1: Web Interface First

**Rejected Because:**
- Web interfaces introduce state management complexity
- Web apps are harder to reproduce in academic papers
- Web interfaces require authentication and session management
- Research community expects CLI tools for reproducibility

### Alternative 2: SaaS/Cloud Service

**Rejected Because:**
- Network dependencies break reproducibility
- SaaS requires multi-tenancy architecture
- SaaS introduces billing and subscription management
- Research data may be sensitive and cannot be sent to external services

### Alternative 3: Real-Time Streaming

**Rejected Because:**
- Streaming introduces async complexity
- Real-time analysis conflicts with deterministic requirements
- Streaming requires persistent queues and databases
- Research analyses are batch-oriented, not streaming

### Alternative 4: AI/LLM-First Approach

**Rejected Because:**
- AI explanations are not transparent or auditable
- LLM outputs are non-deterministic (conflicts with reproducibility)
- AI models are black boxes (conflicts with explainability)
- Research community requires rule-based, explainable methods

### Alternative 5: Product-First (UX-Optimized)

**Rejected Because:**
- Product priorities (dashboard, easy UI) conflict with research priorities (reproducibility, transparency)
- Commercial features (multi-tenancy, SaaS) conflict with offline-first requirements
- Product development encourages feature creep beyond frozen scope

---

## Meta

- **Decision:** CLI-First, Offline-First, Deterministic, Benchmark-Driven, Research-Oriented
- **Status:** Accepted and Frozen for v1.0
- **Next Review:** v2.0 (only if research priorities shift significantly)
- **References:** TRD §1.5, TFS §1.5, PRD §5.1