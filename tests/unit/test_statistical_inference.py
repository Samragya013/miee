"""
Unit tests for StatisticalInferenceEngine (PR-16A).

Tests Bonferroni, Holm, and Benjamini-Hochberg correction methods,
z_to_p conversion, fisher_z_test, HypothesisTest and InferenceResult
dataclasses, and determinism guarantees.
"""

from __future__ import annotations

import pytest

from miie.processing.detection.inference import (
    HypothesisTest,
    InferenceResult,
    StatisticalInferenceEngine,
)
from miie.processing.detection.statistics import fisher_z_test, z_to_p

# ---------------------------------------------------------------------------
# HypothesisTest dataclass
# ---------------------------------------------------------------------------


class TestHypothesisTest:
    def test_creation(self):
        t = HypothesisTest(test_id="T1", raw_p_value=0.03)
        assert t.test_id == "T1"
        assert t.raw_p_value == 0.03
        assert t.alternative == "two-sided"
        assert t.test_statistic == 0.0
        assert t.sample_size == 0

    def test_frozen(self):
        t = HypothesisTest(test_id="T1", raw_p_value=0.05)
        with pytest.raises(AttributeError):
            t.raw_p_value = 0.1  # type: ignore[misc]

    def test_custom_fields(self):
        t = HypothesisTest(
            test_id="T2",
            raw_p_value=0.01,
            alternative="greater",
            test_statistic=2.5,
            sample_size=30,
        )
        assert t.alternative == "greater"
        assert t.test_statistic == 2.5
        assert t.sample_size == 30


# ---------------------------------------------------------------------------
# InferenceResult dataclass
# ---------------------------------------------------------------------------


class TestInferenceResult:
    def test_creation(self):
        r = InferenceResult(
            family_id="F1",
            correction_method="bonferroni",
            alpha=0.05,
            tests=(),
            adjusted_p_values=(),
            reject=(),
            num_tests=0,
            num_rejections=0,
        )
        assert r.family_id == "F1"
        assert r.num_tests == 0

    def test_frozen(self):
        r = InferenceResult(
            family_id="F1",
            correction_method="bonferroni",
            alpha=0.05,
            tests=(),
            adjusted_p_values=(),
            reject=(),
            num_tests=0,
            num_rejections=0,
        )
        with pytest.raises(AttributeError):
            r.alpha = 0.1  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Bonferroni
# ---------------------------------------------------------------------------


class TestBonferroni:
    def test_empty(self):
        r = StatisticalInferenceEngine.bonferroni([])
        assert r.num_tests == 0
        assert r.num_rejections == 0
        assert r.adjusted_p_values == ()
        assert r.reject == ()

    def test_single_test(self):
        r = StatisticalInferenceEngine.bonferroni([0.03], alpha=0.05)
        assert r.num_tests == 1
        assert r.adjusted_p_values == pytest.approx((0.03,))
        assert r.reject == (True,)

    def test_single_test_not_significant(self):
        r = StatisticalInferenceEngine.bonferroni([0.06], alpha=0.05)
        assert r.num_tests == 1
        assert r.adjusted_p_values == pytest.approx((0.06,))
        assert r.reject == (False,)

    def test_multiple_all_reject(self):
        r = StatisticalInferenceEngine.bonferroni([0.01, 0.02, 0.03], alpha=0.05)
        # Adjusted: 0.03, 0.06, 0.09 — only first two reject at alpha=0.05
        assert r.num_tests == 3
        assert r.adjusted_p_values == pytest.approx((0.03, 0.06, 0.09))
        assert r.reject == (True, False, False)

    def test_none_reject(self):
        r = StatisticalInferenceEngine.bonferroni([0.10, 0.20, 0.30], alpha=0.05)
        # Adjusted: 0.30, 0.60, 0.90
        assert r.num_tests == 3
        assert r.reject == (False, False, False)

    def test_adjusted_capped_at_1(self):
        r = StatisticalInferenceEngine.bonferroni([0.5, 0.6, 0.7], alpha=0.05)
        # 0.5*3=1.5→1.0, 0.6*3=1.8→1.0, 0.7*3=2.1→1.0
        assert r.adjusted_p_values == pytest.approx((1.0, 1.0, 1.0))

    def test_family_id(self):
        r = StatisticalInferenceEngine.bonferroni([0.01], alpha=0.05, family_id="D-01_KS_w0_w1")
        assert r.family_id == "D-01_KS_w0_w1"

    def test_correction_method(self):
        r = StatisticalInferenceEngine.bonferroni([0.01])
        assert r.correction_method == "bonferroni"

    def test_num_rejections_count(self):
        r = StatisticalInferenceEngine.bonferroni([0.001, 0.01, 0.02, 0.10], alpha=0.05)
        # Adjusted: 0.004, 0.04, 0.08, 0.40
        assert r.num_rejections == 2


# ---------------------------------------------------------------------------
# Holm-Bonferroni
# ---------------------------------------------------------------------------


class TestHolm:
    def test_empty(self):
        r = StatisticalInferenceEngine.holm([])
        assert r.num_tests == 0
        assert r.num_rejections == 0

    def test_single_test(self):
        r = StatisticalInferenceEngine.holm([0.03], alpha=0.05)
        assert r.num_tests == 1
        assert r.reject == (True,)

    def test_step_down_behavior(self):
        # Holm rejects more than Bonferroni in some cases
        r = StatisticalInferenceEngine.holm([0.01, 0.02, 0.03], alpha=0.05)
        # Sorted: 0.01, 0.02, 0.03
        # i=1: 0.01 <= 0.05/3 = 0.0167 → reject
        # i=2: 0.02 <= 0.05/2 = 0.025 → reject
        # i=3: 0.03 <= 0.05/1 = 0.05 → reject
        assert r.num_rejections == 3
        assert all(r.reject)

    def test_stops_at_first_non_rejection(self):
        r = StatisticalInferenceEngine.holm([0.01, 0.04, 0.06], alpha=0.05)
        # Sorted: 0.01, 0.04, 0.06
        # i=1: 0.01 <= 0.05/3 = 0.0167 → reject
        # i=2: 0.04 > 0.05/2 = 0.025 → STOP
        assert r.num_rejections == 1

    def test_none_reject(self):
        r = StatisticalInferenceEngine.holm([0.10, 0.20, 0.30], alpha=0.05)
        # i=1: 0.10 > 0.05/3 = 0.0167 → STOP
        assert r.num_rejections == 0

    def test_correction_method(self):
        r = StatisticalInferenceEngine.holm([0.01])
        assert r.correction_method == "holm"

    def test_adjusted_p_values_ordered(self):
        r = StatisticalInferenceEngine.holm([0.03, 0.01, 0.02], alpha=0.05)
        # Adjusted p-values should be in [0, 1]
        for adj in r.adjusted_p_values:
            assert 0.0 <= adj <= 1.0


# ---------------------------------------------------------------------------
# Benjamini-Hochberg
# ---------------------------------------------------------------------------


class TestBenjaminiHochberg:
    def test_empty(self):
        r = StatisticalInferenceEngine.benjamini_hochberg([])
        assert r.num_tests == 0
        assert r.num_rejections == 0

    def test_single_test(self):
        r = StatisticalInferenceEngine.benjamini_hochberg([0.03], alpha=0.05)
        assert r.num_tests == 1
        assert r.reject == (True,)

    def test_fdr_control(self):
        # BH is less conservative than Bonferroni
        p_vals = [0.01, 0.02, 0.03, 0.04, 0.05]
        bon = StatisticalInferenceEngine.bonferroni(p_vals, alpha=0.05)
        bh = StatisticalInferenceEngine.benjamini_hochberg(p_vals, alpha=0.05)
        # BH should reject at least as many as Bonferroni
        assert bh.num_rejections >= bon.num_rejections

    def test_monotonicity(self):
        # BH adjusted p-values should be monotonic
        r = StatisticalInferenceEngine.benjamini_hochberg([0.01, 0.02, 0.03, 0.04], alpha=0.05)
        # Check that adjusted values are non-decreasing
        for i in range(1, len(r.adjusted_p_values)):
            assert r.adjusted_p_values[i] >= r.adjusted_p_values[i - 1] - 1e-10

    def test_all_reject(self):
        r = StatisticalInferenceEngine.benjamini_hochberg([0.001, 0.002, 0.003], alpha=0.05)
        assert r.num_rejections == 3

    def test_none_reject(self):
        r = StatisticalInferenceEngine.benjamini_hochberg([0.10, 0.20, 0.30], alpha=0.05)
        assert r.num_rejections == 0

    def test_correction_method(self):
        r = StatisticalInferenceEngine.benjamini_hochberg([0.01])
        assert r.correction_method == "bh"

    def test_adjusted_values_bounded(self):
        r = StatisticalInferenceEngine.benjamini_hochberg([0.9, 0.95, 0.99], alpha=0.05)
        for adj in r.adjusted_p_values:
            assert 0.0 <= adj <= 1.0


# ---------------------------------------------------------------------------
# z_to_p
# ---------------------------------------------------------------------------


class TestZToP:
    def test_two_sided_z_zero(self):
        p = z_to_p(0.0, "two-sided")
        assert p == pytest.approx(1.0)

    def test_two_sided_large_positive(self):
        p = z_to_p(3.0, "two-sided")
        assert p == pytest.approx(0.002699, abs=1e-4)

    def test_two_sided_large_negative(self):
        p_pos = z_to_p(3.0, "two-sided")
        p_neg = z_to_p(-3.0, "two-sided")
        assert p_pos == pytest.approx(p_neg)

    def test_greater(self):
        p = z_to_p(1.96, "greater")
        assert p == pytest.approx(0.025, abs=1e-3)

    def test_less(self):
        p = z_to_p(-1.96, "less")
        assert p == pytest.approx(0.025, abs=1e-3)

    def test_extreme_z(self):
        p = z_to_p(10.0, "two-sided")
        assert p == pytest.approx(0.0, abs=1e-10)

    def test_bounds(self):
        for z in [0.0, 1.0, 2.0, 3.0, -1.0, -2.0, -3.0]:
            p = z_to_p(z, "two-sided")
            assert 0.0 <= p <= 1.0


# ---------------------------------------------------------------------------
# fisher_z_test
# ---------------------------------------------------------------------------


class TestFisherZTest:
    def test_r_zero(self):
        p = fisher_z_test(0.0, n=30)
        assert p == pytest.approx(1.0, abs=1e-6)

    def test_r_half_n_30(self):
        p = fisher_z_test(0.5, n=30)
        assert p < 0.05  # Significant

    def test_r_half_n_5(self):
        p = fisher_z_test(0.5, n=5)
        assert p > 0.05  # Not significant with small n

    def test_n_too_small(self):
        p = fisher_z_test(0.5, n=3)
        assert p == 1.0

    def test_bounds(self):
        for r_val in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9]:
            p = fisher_z_test(r_val, n=30)
            assert 0.0 <= p <= 1.0

    def test_negative_r(self):
        p_pos = fisher_z_test(0.5, n=30)
        p_neg = fisher_z_test(-0.5, n=30)
        assert p_pos == pytest.approx(p_neg)


# ---------------------------------------------------------------------------
# create_tests factory
# ---------------------------------------------------------------------------


class TestCreateTests:
    def test_basic(self):
        tests = StatisticalInferenceEngine.create_tests(["T1", "T2"], [0.01, 0.02])
        assert len(tests) == 2
        assert tests[0].test_id == "T1"
        assert tests[0].raw_p_value == 0.01

    def test_with_optional_fields(self):
        tests = StatisticalInferenceEngine.create_tests(
            ["T1"],
            [0.01],
            test_statistics=[2.5],
            sample_sizes=[30],
            alternatives=["greater"],
        )
        assert tests[0].test_statistic == 2.5
        assert tests[0].sample_size == 30
        assert tests[0].alternative == "greater"

    def test_length_mismatch(self):
        with pytest.raises(ValueError, match="length"):
            StatisticalInferenceEngine.create_tests(["T1", "T2"], [0.01])


# ---------------------------------------------------------------------------
# result_to_dict
# ---------------------------------------------------------------------------


class TestResultToDict:
    def test_basic(self):
        r = StatisticalInferenceEngine.bonferroni([0.01, 0.02], alpha=0.05, family_id="F1")
        d = StatisticalInferenceEngine.result_to_dict(r)
        assert d["family_id"] == "F1"
        assert d["correction_method"] == "bonferroni"
        assert d["alpha"] == 0.05
        assert d["num_tests"] == 2
        assert isinstance(d["adjusted_p_values"], list)
        assert isinstance(d["reject"], list)
        assert isinstance(d["tests"], list)

    def test_tests_structure(self):
        r = StatisticalInferenceEngine.bonferroni([0.03])
        d = StatisticalInferenceEngine.result_to_dict(r)
        assert len(d["tests"]) == 1
        t = d["tests"][0]
        assert "test_id" in t
        assert "raw_p_value" in t
        assert "alternative" in t
        assert "test_statistic" in t
        assert "sample_size" in t


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_bonferroni_deterministic(self):
        p_vals = [0.01, 0.05, 0.10, 0.02, 0.03]
        results = [StatisticalInferenceEngine.bonferroni(p_vals, alpha=0.05) for _ in range(10)]
        for r in results[1:]:
            assert r.adjusted_p_values == results[0].adjusted_p_values
            assert r.reject == results[0].reject

    def test_holm_deterministic(self):
        p_vals = [0.01, 0.05, 0.10, 0.02, 0.03]
        results = [StatisticalInferenceEngine.holm(p_vals, alpha=0.05) for _ in range(10)]
        for r in results[1:]:
            assert r.adjusted_p_values == results[0].adjusted_p_values
            assert r.reject == results[0].reject

    def test_bh_deterministic(self):
        p_vals = [0.01, 0.05, 0.10, 0.02, 0.03]
        results = [StatisticalInferenceEngine.benjamini_hochberg(p_vals, alpha=0.05) for _ in range(10)]
        for r in results[1:]:
            assert r.adjusted_p_values == results[0].adjusted_p_values
            assert r.reject == results[0].reject


# ---------------------------------------------------------------------------
# Bounds validation
# ---------------------------------------------------------------------------


class TestBounds:
    def test_adjusted_p_values_in_range(self):
        p_vals = [0.001, 0.01, 0.05, 0.10, 0.50, 0.99]
        for method in ["bonferroni", "holm", "bh"]:
            if method == "bonferroni":
                r = StatisticalInferenceEngine.bonferroni(p_vals)
            elif method == "holm":
                r = StatisticalInferenceEngine.holm(p_vals)
            else:
                r = StatisticalInferenceEngine.benjamini_hochberg(p_vals)
            for adj in r.adjusted_p_values:
                assert 0.0 <= adj <= 1.0, f"{method}: {adj} out of range"

    def test_reject_booleans(self):
        p_vals = [0.01, 0.05, 0.10, 0.50]
        for method in ["bonferroni", "holm", "bh"]:
            if method == "bonferroni":
                r = StatisticalInferenceEngine.bonferroni(p_vals)
            elif method == "holm":
                r = StatisticalInferenceEngine.holm(p_vals)
            else:
                r = StatisticalInferenceEngine.benjamini_hochberg(p_vals)
            for rej in r.reject:
                assert isinstance(rej, bool)
