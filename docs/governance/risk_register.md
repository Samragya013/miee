# MIIE v1.0 Risk Register

**Status:** Initial Assessment  
**Date:** 2026-06-08  
**Version:** 1.0.0  
**Classification:** Governance Sprint Artifact  

---

## Risk Matrix

| Risk ID | Description | Probability | Impact | Mitigation | Owner |
|---------|-------------|-------------|--------|------------|-------|
| R-001 | Scope Creep - Additional features beyond frozen scope requested | Medium | High | Strict freeze enforcement; IPD v1.1 FINAL as scope authority; no new features without version bump | Engineering Lead |
| R-002 | Contract Drift - Module implementations diverge from ACS specifications | Medium | High | Contract tests (CT-01..CT-17) before integration; ACS v1.0 as single source of truth | Engineer A |
| R-003 | Schema Drift - Data structures diverge from BSD specifications | Medium | High | Schema tests (ST-01..ST-10) before integration; JSON schema validation in CI | Engineer C |
| R-004 | Benchmark Delay - Benchmark dataset generation takes longer than expected | High | Medium | MIFS phase dedicated to benchmark (Weeks 6-7); parallel dataset generation | Engineer B |
| R-005 | Research Delay - Detector performance does not meet benchmark targets | Medium | High | Detector tuning against benchmark; baseline comparison; iterative refinement | Engineer B |
| R-006 | Documentation Drift - Documentation not kept up to date with implementations | Low | Medium | Documentation as part of sprint planning; PR review includes docs | Engineer C |
| R-007 | AI Generated Code Risk - LLM-generated code introduces non-determinism or hidden bugs | Medium | High | No LLM code generation; code review of all implementations; reproducibility tests | All Engineers |
| R-008 | Repository Ingestion Failures - Real repositories fail validation unexpectedly | Low | Medium | Comprehensive error handling; graceful degradation for unavailable metrics | Engineer B |
| R-009 | Benchmark Generalization - Benchmark dataset does not represent real-world corruption patterns | Medium | High | Multiple annotators; Cohen's Kappa ≥0.80; manual validation of pathologies | Engineer B |
| R-010 | Performance Degradation - Analysis time exceeds acceptable thresholds | Low | Medium | Naive correct versions first; profiling only after correctness proven; performance targets as acceptance criteria | Engineer C |

---

## Detailed Risk Assessments

### R-001: Scope Creep

**Description:** Stakeholders may request additional features beyond the frozen v1.0 scope (M-01..M-07, D-01..D-03, 8 CLI commands, 6 API endpoints).

**Probability:** Medium - Stakeholders often discover new requirements during development.

**Impact:** High - Scope creep would invalidate version freeze and require version bump to v1.1.0.

**Mitigation:**
- Strict freeze enforcement via IPD v1.1 FINAL as scope authority
- All feature requests require AFD/PRD amendment
- No new features without version bump and documentation update
- Regular scope audits against frozen documents

**Owner:** Engineering Lead

---

### R-002: Contract Drift

**Description:** Module implementations may diverge from ACS interface specifications, causing integration failures.

**Probability:** Medium - Multiple engineers working on different modules may interpret contracts differently.

**Impact:** High - Contract drift causes integration failures, wasted rework, and timing delays.

**Mitigation:**
- Contract tests (CT-01..CT-17) must pass before module integration
- ACS v1.0 as single source of truth for all interfaces
- Weekly contract review sessions
- Automated contract test suites in CI

**Owner:** Engineer A

---

### R-003: Schema Drift

**Description:** Data structures may diverge from BSD specifications, causing serialization failures and schema validation errors.

**Probability:** Medium - Schema evolution without version bump causes incompatibility.

**Impact:** High - Schema drift causes data loss, integration failures, and benchmark corruption.

**Mitigation:**
- Schema tests (ST-01..ST-10) must pass before integration
- JSON schema validation in CI for all outputs
- Schema versioning: MAJOR for breaking changes, MINOR for additive changes
- No schema changes without version bump

**Owner:** Engineer C

---

### R-004: Benchmark Delay

**Description:** Benchmark dataset generation and annotation may take longer than 4-week MIFS phase.

**Probability:** High - Dataset generation is complex; annotation requires multiple experts.

**Impact:** Medium - Delayed benchmark means delayed detector development and validation.

**Mitigation:**
- MIFS phase dedicated to benchmark (Weeks 6-7)
- Parallel dataset generation on multiple machines
- Automated pathology injection scripts
- Pre-approved annotation guidelines

**Owner:** Engineer B

---

### R-005: Research Delay

**Description:** Detector performance may not meet benchmark targets (D-01: ≥0.80 precision, ≥0.75 recall; D-02: ≥0.75 precision, ≥0.70 recall; D-03: ≥0.85 precision, ≥0.80 recall).

**Probability:** Medium - Detector tuning is iterative; ground truth may be ambiguous.

**Impact:** High - Detector performance targets are key success criteria for v1.0.

**Mitigation:**
- Detector tuning against benchmark (not intuition)
- Baseline comparison (random, majority, statistical, rule-based)
- Iterative refinement with benchmark feedback
- Pre-registered performance targets in IMP

**Owner:** Engineer B

---

### R-006: Documentation Drift

**Description:** Documentation may not be kept up to date with implementation changes.

**Probability:** Low - Documentation is often deprioritized in engineering cycles.

**Impact:** Medium - Outdated documentation causes confusion, wasted time, and user frustration.

**Mitigation:**
- Documentation as part of sprint planning
- PR review includes documentation changes
- Documentation tests in CI (dead links, format validation)
- User testing of documentation

**Owner:** Engineer C

---

### R-007: AI Generated Code Risk

**Description:** LLM-generated code may introduce non-determinism, hidden bugs, or violate frozen requirements.

**Probability:** Medium - LLM code generation is tempting for rapid development.

**Impact:** High - Non-deterministic code violates v1.0 requirements; hidden bugs cause incorrect results.

**Mitigation:**
- No LLM code generation allowed in v1.0
- Code review of all implementations
- Reproducibility tests (bitwise-identical outputs)
- Statistical tests for randomness detection

**Owner:** All Engineers

---

### R-008: Repository Ingestion Failures

**Description:** Real repositories may fail validation unexpectedly (shallow clones, missing metadata, corrupted data).

**Probability:** Low - Validation rules are comprehensive, but real repositories are diverse.

**Impact:** Medium - Ingestion failures cause analysis aborts and user frustration.

**Mitigation:**
- Comprehensive error handling for all validation steps
- Graceful degradation for unavailable metrics
- Detailed error messages with suggestions
- User testing on 100+ real repositories before release

**Owner:** Engineer B

---

### R-009: Benchmark Generalization

**Description:** Benchmark dataset may not represent real-world corruption patterns, leading to overfitting.

**Probability:** Medium - Benchmark datasets are synthetic and may not capture all corruption types.

**Impact:** High - Overfitted detectors perform poorly on real repositories.

**Mitigation:**
- Multiple annotators (≥3) for each dataset
- Cohen's Kappa ≥0.80 for annotation agreement
- Manual validation of pathologies
- External validation on real repositories

**Owner:** Engineer B

---

### R-010: Performance Degradation

**Description:** Analysis time may exceed acceptable thresholds (<5 min for 1k commits).

**Probability:** Low - Naive correct versions prioritized; performance only optimized after correctness.

**Impact:** Medium - Slow performance reduces usability and adoption.

**Mitigation:**
- Naive correct versions first
- Profiling only after correctness proven
- Performance targets as acceptance criteria
- Optimization after all tests pass

**Owner:** Engineer C

---

## Risk Response Protocol

### Low Risk (Probability: Low, Impact: Low)
- Monitor
- Review in weekly standup
- No active mitigation required

### Medium Risk (Probability: Medium, Impact: Medium or High)
- Mitigate actively
- Review in weekly standup
- Update risk register monthly

### High Risk (Probability: High, Impact: High)
- Mitigate actively
- Review in daily standup
- Escalate to Engineering Lead
- Update risk register weekly

---

## Risk Register Maintenance

**Owner:** Engineering Lead

**Frequency:** Weekly review, monthly update

**Trigger Events:**
- New risk identified
- Existing risk probability changes
- Existing risk impact changes
- Mitigation actions completed

---

*This risk register is a living document. Update it regularly as risks evolve or are mitigated.*