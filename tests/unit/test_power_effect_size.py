"""
Unit tests for power.py and effect_size.py (PR-16B).

Tests the statistical power analysis and effect size computation frameworks
that resolve SDV2 Finding G-01.
"""

import numpy as np

from miie.processing.detection.effect_size import (
    EffectSizeLabel,
    cliffs_delta,
    cohens_d,
    correlation_effect_size,
    effect_size_summary,
    interpret_effect_size,
    jensen_shannon_divergence,
    ks_effect_size,
    rank_biserial,
)
from miie.processing.detection.power import (
    ci_width_correlation,
    ci_width_mean,
    ci_width_proportion,
    mde_correlation,
    mde_ks,
    mde_proportion,
    mde_t_test,
    observed_power,
    power_correlation_test,
    power_ks_test,
    power_proportion_test,
    power_t_test,
    sample_size_correlation,
    sample_size_ks,
    sample_size_proportion,
    sample_size_t_test,
)

# ---------------------------------------------------------------------------
# Power functions
# ---------------------------------------------------------------------------


class TestPowerKsTest:
    """Tests for power_ks_test."""

    def test_power_increases_with_effect_size(self):
        p1 = power_ks_test(50, 50, 0.1)
        p2 = power_ks_test(50, 50, 0.3)
        p3 = power_ks_test(50, 50, 0.5)
        assert p1 < p2 < p3

    def test_power_increases_with_sample_size(self):
        p1 = power_ks_test(20, 20, 0.3)
        p2 = power_ks_test(50, 50, 0.3)
        p3 = power_ks_test(100, 100, 0.3)
        assert p1 < p2 < p3

    def test_power_decreases_with_alpha(self):
        p1 = power_ks_test(50, 50, 0.3, alpha=0.01)
        p2 = power_ks_test(50, 50, 0.3, alpha=0.05)
        p3 = power_ks_test(50, 50, 0.3, alpha=0.10)
        assert p1 < p2 < p3

    def test_power_bounds(self):
        p = power_ks_test(50, 50, 0.3)
        assert 0.0 <= p <= 1.0

    def test_zero_effect_gives_zero_power(self):
        p = power_ks_test(50, 50, 0.0)
        assert p == 0.0

    def test_invalid_inputs_give_zero(self):
        assert power_ks_test(1, 50, 0.3) == 0.0  # n1 too small
        assert power_ks_test(50, 1, 0.3) == 0.0  # n2 too small
        assert power_ks_test(50, 50, 0.0) == 0.0  # d=0
        assert power_ks_test(50, 50, -0.1) == 0.0  # negative d
        assert power_ks_test(50, 50, 0.3, alpha=0.0) == 0.0
        assert power_ks_test(50, 50, 0.3, alpha=1.0) == 0.0

    def test_high_effect_high_sample_near_one(self):
        p = power_ks_test(200, 200, 0.5, alpha=0.05)
        assert p > 0.95


class TestPowerTTest:
    """Tests for power_t_test."""

    def test_power_increases_with_effect_size(self):
        p1 = power_t_test(50, 0.2)
        p2 = power_t_test(50, 0.5)
        p3 = power_t_test(50, 0.8)
        assert p1 < p2 < p3

    def test_two_sample_requires_more_n(self):
        p1s = power_t_test(100, 0.5, two_sample=False)
        p2s = power_t_test(100, 0.5, two_sample=True)
        # One-sample is more powerful for same n
        assert p1s > p2s

    def test_one_sided_vs_two_sided(self):
        p_two = power_t_test(50, 0.5, alternative="two-sided")
        p_one = power_t_test(50, 0.5, alternative="one-sided")
        assert p_one > p_two  # One-sided is more powerful

    def test_power_bounds(self):
        p = power_t_test(50, 0.5)
        assert 0.0 <= p <= 1.0


class TestPowerCorrelation:
    """Tests for power_correlation_test."""

    def test_power_increases_with_rho(self):
        p1 = power_correlation_test(50, 0.2)
        p2 = power_correlation_test(50, 0.4)
        p3 = power_correlation_test(50, 0.6)
        assert p1 < p2 < p3

    def test_power_increases_with_n(self):
        p1 = power_correlation_test(20, 0.3)
        p2 = power_correlation_test(50, 0.3)
        p3 = power_correlation_test(100, 0.3)
        assert p1 < p2 < p3

    def test_zero_rho_gives_alpha_power(self):
        p = power_correlation_test(50, 0.0)
        assert abs(p - 0.05) < 0.01  # power = alpha when rho=0

    def test_power_bounds(self):
        p = power_correlation_test(50, 0.3)
        assert 0.0 <= p <= 1.0


class TestPowerProportion:
    """Tests for power_proportion_test."""

    def test_power_increases_with_difference(self):
        p1 = power_proportion_test(100, 0.55, 0.50)
        p2 = power_proportion_test(100, 0.65, 0.50)
        p3 = power_proportion_test(100, 0.75, 0.50)
        assert p1 < p2 < p3

    def test_power_bounds(self):
        p = power_proportion_test(100, 0.6, 0.5)
        assert 0.0 <= p <= 1.0

    def test_invalid_inputs(self):
        assert power_proportion_test(100, 0.0, 0.5) == 0.0
        assert power_proportion_test(100, 1.0, 0.5) == 0.0
        assert power_proportion_test(100, 0.6, 0.0) == 0.0
        assert power_proportion_test(100, 0.6, 1.0) == 0.0


class TestObservedPower:
    """Tests for observed_power."""

    def test_observed_power_increases_with_p_value_significance(self):
        p1 = observed_power(0.04, 50)
        p2 = observed_power(0.01, 50)
        p3 = observed_power(0.001, 50)
        assert p1 < p2 < p3

    def test_observed_power_bounds(self):
        p = observed_power(0.03, 100)
        assert 0.0 <= p <= 1.0

    def test_boundary_p_values(self):
        assert observed_power(0.0, 50) == 0.0
        assert observed_power(1.0, 50) == 0.0


# ---------------------------------------------------------------------------
# Sample size estimation
# ---------------------------------------------------------------------------


class TestSampleSizeKs:
    """Tests for sample_size_ks."""

    def test_larger_effect_smaller_n(self):
        r1 = sample_size_ks(0.3)
        r2 = sample_size_ks(0.5)
        r3 = sample_size_ks(0.8)
        assert r1.required_n > r2.required_n > r3.required_n

    def test_higher_power_needs_more_n(self):
        r1 = sample_size_ks(0.3, power=0.80)
        r2 = sample_size_ks(0.3, power=0.90)
        assert r1.required_n < r2.required_n

    def test_minimum_n_is_at_least_10(self):
        r = sample_size_ks(0.99)
        assert r.required_n >= 10

    def test_interpretation_populated(self):
        r = sample_size_ks(0.3)
        assert "Need" in r.interpretation
        assert "KS D=" in r.interpretation


class TestSampleSizeTTest:
    """Tests for sample_size_t_test."""

    def test_larger_effect_smaller_n(self):
        r1 = sample_size_t_test(0.2)
        r2 = sample_size_t_test(0.5)
        assert r1.required_n > r2.required_n

    def test_two_sample_needs_more_n(self):
        r1 = sample_size_t_test(0.5, two_sample=False)
        r2 = sample_size_t_test(0.5, two_sample=True)
        assert r1.required_n < r2.required_n


class TestSampleSizeCorrelation:
    """Tests for sample_size_correlation."""

    def test_larger_r_smaller_n(self):
        r1 = sample_size_correlation(0.2)
        r2 = sample_size_correlation(0.5)
        assert r1.required_n > r2.required_n

    def test_minimum_n(self):
        r = sample_size_correlation(0.9)
        assert r.required_n >= 4


class TestSampleSizeProportion:
    """Tests for sample_size_proportion."""

    def test_larger_delta_smaller_n(self):
        r1 = sample_size_proportion(0.6, 0.5, 0.05)
        r2 = sample_size_proportion(0.6, 0.5, 0.10)
        assert r1.required_n > r2.required_n


# ---------------------------------------------------------------------------
# MDE functions
# ---------------------------------------------------------------------------


class TestMdeKs:
    def test_mde_decreases_with_n(self):
        m1 = mde_ks(20)
        m2 = mde_ks(50)
        m3 = mde_ks(100)
        assert m1 > m2 > m3

    def test_mde_bounds(self):
        m = mde_ks(50)
        assert 0.0 <= m <= 1.0


class TestMdeTCorrelation:
    def test_mde_decreases_with_n(self):
        m1 = mde_t_test(20)
        m2 = mde_t_test(50)
        assert m1 > m2


class TestMdeCorrelation:
    def test_mde_decreases_with_n(self):
        m1 = mde_correlation(20)
        m2 = mde_correlation(50)
        m3 = mde_correlation(100)
        assert m1 > m2 > m3

    def test_mde_bounds(self):
        m = mde_correlation(50)
        assert 0.0 <= m <= 1.0


class TestMdeProportion:
    def test_mde_decreases_with_n(self):
        m1 = mde_proportion(20, 0.5)
        m2 = mde_proportion(50, 0.5)
        assert m1 > m2


# ---------------------------------------------------------------------------
# CI width diagnostics
# ---------------------------------------------------------------------------


class TestCiWidthProportion:
    def test_wilson_vs_wald(self):
        r_wilson = ci_width_proportion(100, 0.3, method="wilson")
        r_wald = ci_width_proportion(100, 0.3, method="wald")
        # Wilson should be similar but slightly different
        assert abs(r_wilson.ci_width - r_wald.ci_width) < 0.1

    def test_larger_n_narrower_ci(self):
        r1 = ci_width_proportion(30, 0.3)
        r2 = ci_width_proportion(100, 0.3)
        assert r2.ci_width < r1.ci_width

    def test_precision_is_1_minus_width(self):
        r = ci_width_proportion(100, 0.3)
        assert abs(r.precision - (1.0 - r.ci_width)) < 1e-10

    def test_bounds(self):
        r = ci_width_proportion(100, 0.3)
        assert 0.0 <= r.ci_lower <= r.ci_upper <= 1.0
        assert r.ci_width >= 0


class TestCiWidthCorrelation:
    def test_larger_n_narrower_ci(self):
        r1 = ci_width_correlation(0.3, 20)
        r2 = ci_width_correlation(0.3, 100)
        assert r2.ci_width < r1.ci_width

    def test_zero_sample_gives_empty(self):
        r = ci_width_correlation(0.3, 2)
        assert "too small" in r.interpretation


class TestCiWidthMean:
    def test_larger_n_narrower_ci(self):
        r1 = ci_width_mean(10.0, 2.0, 20)
        r2 = ci_width_mean(10.0, 2.0, 100)
        assert r2.ci_width < r1.ci_width

    def test_zero_std(self):
        r = ci_width_mean(10.0, 0.0, 50)
        assert r.ci_width == 0.0


# ---------------------------------------------------------------------------
# Effect size functions
# ---------------------------------------------------------------------------


class TestCohensD:
    def test_identical_distributions(self):
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        d = cohens_d(x, y)
        assert abs(d.value) < 0.01

    def test_separated_distributions(self):
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([10.0, 11.0, 12.0, 13.0, 14.0])
        d = cohens_d(x, y)
        assert d.value < -3.0  # Large negative effect
        assert d.label == EffectSizeLabel.VERY_LARGE

    def test_ci_populated(self):
        x = np.random.normal(0, 1, 50)
        y = np.random.normal(0.5, 1, 50)
        d = cohens_d(x, y)
        assert d.ci_lower is not None
        assert d.ci_upper is not None
        assert d.ci_lower < d.value < d.ci_upper

    def test_insufficient_data(self):
        d = cohens_d(np.array([1.0]), np.array([2.0]))
        assert "Insufficient" in d.interpretation


class TestCliffsDelta:
    def test_identical_distributions(self):
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([1.0, 2.0, 3.0])
        d = cliffs_delta(x, y)
        assert abs(d.value) < 0.01

    def test_x_larger_than_y(self):
        x = np.array([5.0, 6.0, 7.0])
        y = np.array([1.0, 2.0, 3.0])
        d = cliffs_delta(x, y)
        assert d.value > 0.9

    def test_x_smaller_than_y(self):
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([5.0, 6.0, 7.0])
        d = cliffs_delta(x, y)
        assert d.value < -0.9


class TestRankBiserial:
    def test_identical_distributions(self):
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([1.0, 2.0, 3.0])
        r = rank_biserial(x, y)
        assert abs(r.value) < 0.01

    def test_separated_distributions(self):
        x = np.array([10.0, 11.0, 12.0])
        y = np.array([1.0, 2.0, 3.0])
        r = rank_biserial(x, y)
        assert r.value > 0.9


class TestKsEffectSize:
    def test_identical_distributions(self):
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        d = ks_effect_size(x, y)
        assert d.value < 0.01

    def test_separated_distributions(self):
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([10.0, 11.0, 12.0])
        d = ks_effect_size(x, y)
        assert d.value > 0.9

    def test_label_interpretation(self):
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([10.0, 11.0, 12.0])
        d = ks_effect_size(x, y)
        assert d.label in [EffectSizeLabel.LARGE, EffectSizeLabel.VERY_LARGE]


class TestCorrelationEffectSize:
    def test_zero_correlation(self):
        r = correlation_effect_size(0.0, 50)
        assert r.label == EffectSizeLabel.NEGLIGIBLE

    def test_strong_correlation(self):
        r = correlation_effect_size(0.7, 50)
        assert r.label == EffectSizeLabel.LARGE

    def test_r_squared_populated(self):
        r = correlation_effect_size(0.5, 50)
        assert abs(r.value**2 - 0.25) < 1e-10

    def test_ci_populated(self):
        r = correlation_effect_size(0.3, 50)
        assert r.ci_lower is not None
        assert r.ci_upper is not None


class TestJensenShannonDivergence:
    def test_identical_distributions(self):
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        d = jensen_shannon_divergence(x, y)
        assert d.value < 0.001

    def test_different_distributions(self):
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([10.0, 11.0, 12.0])
        d = jensen_shannon_divergence(x, y)
        assert d.value > 0.01


class TestEffectSizeSummary:
    def test_summary_has_all_keys(self):
        x = np.random.normal(0, 1, 50)
        y = np.random.normal(0.5, 1, 50)
        s = effect_size_summary(x, y)
        assert "cohens_d" in s
        assert "cliffs_delta" in s
        assert "rank_biserial" in s
        assert "ks_effect_size" in s
        assert "jensen_shannon" in s
        assert "overall_label" in s
        assert "summary" in s

    def test_summary_contains_label(self):
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([10.0, 11.0, 12.0])
        s = effect_size_summary(x, y)
        assert isinstance(s["overall_label"], EffectSizeLabel)


# ---------------------------------------------------------------------------
# Interpret function
# ---------------------------------------------------------------------------


class TestInterpretEffectSize:
    def test_general_bands(self):
        assert interpret_effect_size(0.005, "general") == EffectSizeLabel.NEGLIGIBLE
        assert interpret_effect_size(0.1, "general") == EffectSizeLabel.SMALL
        assert interpret_effect_size(0.3, "general") == EffectSizeLabel.MEDIUM
        assert interpret_effect_size(0.6, "general") == EffectSizeLabel.LARGE
        assert interpret_effect_size(0.9, "general") == EffectSizeLabel.VERY_LARGE

    def test_correlation_bands(self):
        assert interpret_effect_size(0.05, "correlation") == EffectSizeLabel.NEGLIGIBLE
        assert interpret_effect_size(0.15, "correlation") == EffectSizeLabel.SMALL
        assert interpret_effect_size(0.35, "correlation") == EffectSizeLabel.MEDIUM
        assert interpret_effect_size(0.55, "correlation") == EffectSizeLabel.LARGE
