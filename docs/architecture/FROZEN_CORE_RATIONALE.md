# Frozen Core Rationale

This document explains why certain components of MIIE are frozen and cannot be modified without explicit justification.

## Why Freeze?

MIIE is a research tool. Its value depends on **reproducibility**. If the statistical methods change between versions, researchers who cited MIIE results would have their citations invalidated. The frozen core ensures:

1. **Reproducibility** — Same input always produces same output
2. **Citation integrity** — Published results remain valid
3. **Trust** — Users know the core logic won't change unexpectedly
4. **Auditability** — Every statistical choice is documented and justified

## What Is Frozen?

### Statistical Methods (D-01, D-02, D-03)

| Method | Why Frozen | Alternative Considered |
|---|---|---|
| KS test (α=0.05) | Standard non-parametric test for distribution comparison | Anderson-Darling (more powerful but less familiar) |
| PSI threshold (0.25) | Industry standard for distribution stability | Custom threshold (would require validation study) |
| Fisher z-transformation | Standard for comparing correlations | Bootstrap CI (computationally expensive) |
| Hartigan's dip test | Standard for unimodality testing | Silverman's test (less robust) |

### Confidence Scoring

| Parameter | Value | Justification |
|---|---|---|
| Bootstrap iterations | 1000 | Balances accuracy vs. speed |
| Confidence decay | 0.95 per window | Prevents overconfidence from small samples |
| Minimum sample size | 30 | Below this, statistical tests lose power |

### Integrity Scoring

| Parameter | Value | Justification |
|---|---|---|
| Weight scheme | Equal weights | No basis for weighting one metric over another |
| Aggregation | Geometric mean | penalizes weak metrics more than arithmetic mean |
| Threshold | 0.7 | Below this, metric validity is questionable |

## How to Modify Frozen Core

If you need to change a frozen component:

1. **Document the reason** — What problem does this solve?
2. **Provide evidence** — Show that the new method produces better results
3. **Maintain backward compatibility** — Old results must still be valid
4. **Get approval** — Two maintainers must review
5. **Version the change** — Bump major version number
6. **Update this document** — Explain the change and its rationale

## Related Documents

- `docs/specifications/00_SCIENTIFIC_DESIGN_VERIFICATION.md` — Original statistical design
- `docs/specifications/01_DETECTOR_SPECIFICATION.md` — Detector specifications
- `docs/architecture/` — Architecture decision records
