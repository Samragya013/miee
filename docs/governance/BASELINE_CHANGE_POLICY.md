# MIIE Baseline Change Policy

**Created:** 2026-06-29
**Baseline:** v1.0.1
**Scope:** All changes to the frozen engineering baseline
**Authority:** RELEASE_BASELINE.md

---

## 1. Purpose

This policy governs all changes to the MIIE v1.0.1 engineering baseline. It defines what is immutable, what may change, and the rules for making changes. The goal is to protect reproducibility, backward compatibility, and scientific integrity while allowing necessary improvements.

---

## 2. Immutable Components

The following components are **immutable** for the lifetime of MIIE v1.x. They cannot be changed without a major version bump (v2.0.0) and explicit approval from the project maintainers.

### 2.1 Statistical Methods

| Component | Immutability Reason |
|-----------|-------------------|
| D-01 KS test implementation | Would break reproducibility of published analyses |
| D-02 Pearson/Spearman/Fisher-z | Would break reproducibility of published analyses |
| D-03 Excess Mass + Dip test | Would break reproducibility of published analyses |
| Scoring formula (IS/CS) | Would break scoring consistency across versions |
| Detector weights (0.40/0.35/0.25) | Would break scoring consistency |

### 2.2 Data Schemas

| Component | Immutability Reason |
|-----------|-------------------|
| ScorePackage fields | Would break JSON serialization |
| EvidencePackage fields | Would break JSON serialization |
| AnalysisResult fields | Would break JSON serialization |
| DetectorResult fields | Would break JSON serialization |
| WindowResult fields | Would break JSON serialization |
| Error hierarchy codes | Would break error handling |

### 2.3 API Contracts

| Component | Immutability Reason |
|-----------|-------------------|
| CLI command names | Would break user scripts |
| CLI exit codes | Would break automation |
| API endpoint paths | Would break client integrations |
| API response format | Would break client code |
| Config file format | Would break existing configs |

---

## 3. Changeable Components

The following components may change in minor versions (v1.x.0) or patch versions (v1.0.x) without requiring a major version bump.

### 3.1 Patch-Level Changes (v1.0.x)

These changes are allowed in patch releases without version bump discussion:

| Category | Allowed Changes |
|----------|----------------|
| Bug fixes | Correct detector edge cases, fix scoring errors |
| Performance | Optimize algorithms, reduce memory usage |
| Documentation | Fix typos, add examples, clarify descriptions |
| Testing | Add tests, improve coverage, fix flaky tests |
| CI/CD | Pipeline improvements, dependency updates |
| Error messages | Improve clarity, add context |
| Logging | Add debug information, improve output |
| Code cleanup | Remove dead code, improve comments |

### 3.2 Minor-Level Changes (v1.x.0)

These changes require a minor version bump:

| Category | Allowed Changes |
|----------|----------------|
| New detectors | Add D-04, D-05, etc. with benchmarks |
| New metrics | Add M-08, M-09, etc. with definitions |
| New CLI options | Add --new-option to existing commands |
| New API endpoints | Add /v1/new-endpoint |
| New config options | Add new-key to config format |
| Schema extensions | Add new fields (not remove existing) |
| New error types | Add new MIIEError subclasses |

### 3.3 Major-Level Changes (v2.0.0)

These changes require a major version bump:

| Category | Changes |
|----------|---------|
| Statistical method changes | Modify D-01/D-02/D-03 algorithms |
| Scoring formula changes | Modify IS/CS computation |
| Schema breaking changes | Remove fields, change types |
| API breaking changes | Remove endpoints, change response format |
| CLI breaking changes | Remove commands, change exit codes |
| Config breaking changes | Incompatible format changes |

---

## 4. Version Bumping Rules

### 4.1 When to Bump

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| Bug fix | Patch (1.0.x → 1.0.x+1) | Fix edge case in D-01 |
| New feature | Minor (1.x.0 → 1.x+1.0) | Add D-04 detector |
| Breaking change | Major (x.0.0 → x+1.0.0) | Change scoring formula |
| CI stabilization | Tag only (no bump) | Fix CI pipeline |

### 4.2 Version String Locations

When bumping, update ALL of these locations:

| Location | File | Line |
|----------|------|------|
| Package version | `pyproject.toml` | `version = "x.y.z"` |
| Package init | `src/miie/__init__.py` | `__version__ = "x.y.z"` |
| API init | `src/miie/api/__init__.py` | `__version__ = "x.y.z"` |
| README badge | `README.md` | Badge URL |
| Mock scoring | `src/miie/processing/scoring/mock_scoring.py` | `__version__` |
| Reporting engine | `src/miie/processing/reporting/engine.py` | 7 instances |
| Evidence engine | `src/miie/processing/evidence.py` | 2 instances |
| Benchmark engine | `src/miie/processing/benchmark/engine.py` | 2 instances |
| Benchmark generator | `src/miie/benchmark/generator.py` | 1 instance |
| Benchmark runner | `src/miie/benchmark/runner.py` | 2 instances |
| Schema models | `src/miie/schemas/models.py` | `formula_version` |

### 4.3 Git Tagging

After version bump:

1. Update all version strings
2. Commit changes
3. Create git tag: `git tag -a vX.Y.Z -m "MIIE vX.Y.Z"`
4. Push tag: `git push origin vX.Y.Z`
5. Update README badge to point to new tag

---

## 5. Branch Management

### 5.1 Branch Strategy

| Branch | Purpose | Protection |
|--------|---------|------------|
| `main` | Stable release | Protected, CI required |
| `develop` | Active development | CI required |
| `feature/*` | Feature work | From develop |
| `fix/*` | Bug fixes | From develop or main |
| `release/*` | Release prep | From develop |
| `baseline/v1.0.x` | v1.0.x maintenance | Protected |

### 5.2 Branch Rules

| Rule | Description |
|------|-------------|
| No force push | Never rewrite history on main/develop |
| No direct commits | All changes via PR |
| CI required | All jobs must pass before merge |
| Review required | At least 1 review before merge |
| Squash merge | Clean history for features |
| Rebase merge | Clean history for fixes |

### 5.3 Tag Protection

| Rule | Description |
|------|-------------|
| No tag deletion | Tags are permanent once pushed |
| No tag rewriting | Never move a tag to a different commit |
| Annotated tags | Always use `git tag -a` with message |
| Version format | Always `vX.Y.Z` (no pre-release in baseline) |

---

## 6. Documentation Rules

### 6.1 Documentation Updates

| Change Type | Documentation Required |
|-------------|----------------------|
| New detector | Detector docstring, README, examples |
| New metric | Metric definition, README, examples |
| New CLI option | CLI help text, README, examples |
| New API endpoint | API docstring, README, examples |
| Breaking change | Migration guide, CHANGELOG |
| Bug fix | CHANGELOG entry |

### 6.2 Documentation Locations

| Document | Location | Purpose |
|----------|----------|---------|
| README | `README.md` | Project overview, quick start |
| CLI help | `miie --help` | Command reference |
| API docs | OpenAPI/Swagger | Endpoint reference |
| Architecture | `docs/architecture/` | Design decisions |
| Governance | `docs/governance/` | Process rules |
| Roadmap | `docs/roadmap/` | Future plans |
| Release notes | `docs/release_notes_vX.Y.Z.md` | Version changes |

### 6.3 CHANGELOG Format

```markdown
## [vX.Y.Z] - YYYY-MM-DD

### Added
- Feature A (D-04 detector)
- Feature B (extended metrics)

### Changed
- Improved algorithm X

### Fixed
- Bug in detector Y

### Deprecated
- Feature Z (will be removed in v2.0)

### Removed
- (none)

### Security
- Fixed vulnerability in dependency X
```

---

## 7. Testing Rules

### 7.1 Test Requirements

| Change Type | Test Requirement |
|-------------|-----------------|
| New detector | Unit tests + benchmark suite |
| New metric | Unit tests + integration test |
| Bug fix | Regression test added |
| Performance | Benchmark before/after |
| Breaking change | Migration test |

### 7.2 Coverage Requirements

| Code Type | Minimum Coverage |
|-----------|-----------------|
| New detector code | 90% |
| New metric code | 85% |
| New CLI option | 80% |
| Bug fix | 80% |
| Documentation | N/A |

### 7.3 Test Execution

| Command | Purpose |
|---------|---------|
| `make test-unit` | Unit tests |
| `make test-integration` | Integration tests |
| `make test-benchmark` | Benchmark validation |
| `make test-all` | All tests |
| `make check` | Lint + typecheck + tests |

---

## 8. Review Rules

### 8.1 Review Checklist

Before approving a baseline change:

- [ ] All tests pass
- [ ] CI/CD pipeline green
- [ ] Documentation updated
- [ ] Version bumped (if applicable)
- [ ] CHANGELOG updated
- [ ] Breaking changes documented
- [ ] Migration guide provided (if breaking)
- [ ] Benchmark results included (if detector change)
- [ ] Performance impact assessed

### 8.2 Approval Requirements

| Change Type | Approval Required |
|-------------|------------------|
| Bug fix | 1 maintainer |
| New feature | 1 maintainer |
| Breaking change | 2 maintainers |
| Statistical method | 2 maintainers + benchmark |
| Version bump | 1 maintainer |
| Major version | All maintainers |

### 8.3 Merge Strategy

| Change Type | Merge Strategy |
|-------------|---------------|
| Feature | Squash merge |
| Bug fix | Rebase merge |
| Release | Merge commit |
| Hotfix | Cherry-pick |

---

## 9. Migration Rules

### 9.1 Backward Compatibility

| Rule | Description |
|------|-------------|
| Additive only | New fields added, not removed |
| Deprecation period | 2 minor versions before removal |
| Deprecation warnings | Logged when deprecated feature used |
| Migration scripts | Provided for breaking changes |

### 9.2 Deprecation Process

1. Mark feature as deprecated in code
2. Add deprecation warning
3. Document in CHANGELOG
4. Update README
5. Wait 2 minor versions
6. Remove feature in next major version

### 9.3 Migration Guide Format

```markdown
# Migration from vX.Y to vX.Z

## Breaking Changes

### Change 1: [Description]
- Old behavior: [description]
- New behavior: [description]
- Migration: [steps]

### Change 2: [Description]
- Old behavior: [description]
- New behavior: [description]
- Migration: [steps]

## Deprecated Features

### Feature 1: [Description]
- Status: Deprecated in vX.Y, will be removed in v2.0
- Alternative: [description]

## New Features

### Feature 1: [Description]
- Usage: [examples]
```

---

## 10. Emergency Rules

### 10.1 Hotfix Process

For critical bugs in production:

1. Create hotfix branch from `main`
2. Fix the bug
3. Add regression test
4. Ensure CI passes
5. Get 1 review
6. Merge to `main`
7. Cherry-pick to `develop`
8. Create patch release

### 10.2 Rollback Rules

If a release causes issues:

1. Do NOT delete the tag
2. Create new patch release fixing the issue
3. Document in CHANGELOG
4. Update README

### 10.3 Security Fixes

For security vulnerabilities:

1. Create private fork if needed
2. Fix vulnerability
3. Assess impact
4. Create patch release
5. Publish security advisory

---

## 11. Compliance Rules

### 11.1 Evidence Requirements

| Change Type | Evidence Required |
|-------------|------------------|
| Bug fix | Test results showing fix |
| New feature | Benchmark results, test results |
| Performance | Before/after benchmarks |
| Breaking change | Migration test results |

### 11.2 Audit Trail

All baseline changes must be traceable:

1. Git commit with clear message
2. PR with description
3. Review approval
4. CI/CD pass
5. Version tag
6. CHANGELOG entry
7. Release notes

### 11.3 Release Certification

Before releasing a new version:

- [ ] All tests pass (730+ tests)
- [ ] CI/CD pipeline green (9 jobs)
- [ ] Documentation complete
- [ ] CHANGELOG updated
- [ ] Version strings consistent
- [ ] Git tag created
- [ ] Release notes published
- [ ] Baseline document updated

---

## 12. Exceptions

### 12.1 Exception Process

If a change requires deviation from this policy:

1. Document the exception request
2. Explain why it's necessary
3. Get approval from 2 maintainers
4. Document in CHANGELOG
5. Update this policy if permanent

### 12.2 Emergency Exceptions

For time-critical fixes:

1. Fix the issue
2. Document the exception
3. Get retroactive approval
4. Update policy if needed

---

## 13. Policy Updates

This policy may be updated when:

1. New types of changes are needed
2. Process improvements are identified
3. Regulatory requirements change
4. Community feedback suggests improvements

### Update Process

1. Propose change via PR
2. Review from 2 maintainers
3. Merge to main
4. Update version
5. Document in CHANGELOG

---

*This policy is authoritative. All baseline changes must comply with these rules.*
