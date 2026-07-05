"""
Statistical Inference Engine for MIIE v1.6.

Provides multiple-testing correction methods for detector hypothesis tests.
Resolves SDV-2 Finding G-02 (no family-wise error rate or FDR control).

Implements Bonferroni, Holm-Bonferroni, and Benjamini-Hochberg procedures.
Each method is a pure function with no detector-specific state.

Reference: PR-16A, Doc 01 §8, DSVP-v1.0 §7.11
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class HypothesisTest:
    """Single hypothesis test result.

    Attributes:
        test_id: Unique identifier (e.g., "M-01_w0_w1").
        raw_p_value: Uncorrected p-value in [0, 1].
        alternative: Hypothesis direction ("two-sided", "greater", "less").
        test_statistic: Observed test statistic value.
        sample_size: Number of observations used.
    """

    test_id: str
    raw_p_value: float
    alternative: str = "two-sided"
    test_statistic: float = 0.0
    sample_size: int = 0


@dataclass(frozen=True)
class InferenceResult:
    """Corrected inference for a family of hypothesis tests.

    Attributes:
        family_id: Family identifier (e.g., "D-01_KS_w0_w1").
        correction_method: Method name ("bonferroni", "holm", "bh").
        alpha: Family-wise significance level.
        tests: Original hypothesis tests.
        adjusted_p_values: Corrected p-values (same order as tests).
        reject: Decision per test after correction.
        num_tests: Number of tests k.
        num_rejections: Number of rejections.
    """

    family_id: str
    correction_method: str
    alpha: float
    tests: Tuple[HypothesisTest, ...]
    adjusted_p_values: Tuple[float, ...]
    reject: Tuple[bool, ...]
    num_tests: int
    num_rejections: int


class StatisticalInferenceEngine:
    """Reusable multiple-testing correction engine.

    All methods are static — no instance state. Each takes a list of
    raw p-values and returns an InferenceResult with corrected decisions.

    Example::

        engine = StatisticalInferenceEngine()
        result = engine.bonferroni([0.01, 0.04, 0.03], alpha=0.05)
        # result.reject == (True, True, True)
    """

    @staticmethod
    def bonferroni(
        p_values: List[float],
        alpha: float = 0.05,
        family_id: str = "unknown",
    ) -> InferenceResult:
        """Bonferroni correction for family-wise error rate control.

        Adjusted p-value: p_adj = min(p * k, 1.0)
        Reject if p_adj <= alpha.

        Very conservative but requires no assumptions about test dependence.
        Controls FWER at exactly alpha.

        Args:
            p_values: Raw (uncorrected) p-values.
            alpha: Family-wise significance level (default 0.05).
            family_id: Identifier for this family of tests.

        Returns:
            InferenceResult with corrected decisions.
        """
        k = len(p_values)
        if k == 0:
            return InferenceResult(
                family_id=family_id,
                correction_method="bonferroni",
                alpha=alpha,
                tests=(),
                adjusted_p_values=(),
                reject=(),
                num_tests=0,
                num_rejections=0,
            )

        adjusted = tuple(min(p * k, 1.0) for p in p_values)
        reject = tuple(a <= alpha for a in adjusted)
        tests = tuple(HypothesisTest(test_id=f"test_{i}", raw_p_value=p) for i, p in enumerate(p_values))

        return InferenceResult(
            family_id=family_id,
            correction_method="bonferroni",
            alpha=alpha,
            tests=tests,
            adjusted_p_values=adjusted,
            reject=reject,
            num_tests=k,
            num_rejections=sum(reject),
        )

    @staticmethod
    def holm(
        p_values: List[float],
        alpha: float = 0.05,
        family_id: str = "unknown",
    ) -> InferenceResult:
        """Holm-Bonferroni step-down procedure for FWER control.

        Uniformly more powerful than Bonferroni. No assumptions needed.
        Procedure:
            1. Sort p-values: p(1) <= p(2) <= ... <= p(k)
            2. For i = 1..k: reject if p(i) <= alpha / (k - i + 1)
            3. Stop at first non-rejection; reject all previous.

        Args:
            p_values: Raw (uncorrected) p-values.
            alpha: Family-wise significance level (default 0.05).
            family_id: Identifier for this family of tests.

        Returns:
            InferenceResult with corrected decisions.
        """
        k = len(p_values)
        if k == 0:
            return InferenceResult(
                family_id=family_id,
                correction_method="holm",
                alpha=alpha,
                tests=(),
                adjusted_p_values=(),
                reject=(),
                num_tests=0,
                num_rejections=0,
            )

        indexed = sorted(enumerate(p_values), key=lambda x: x[1])
        adjusted = [0.0] * k
        reject_list = [False] * k

        for rank, (orig_idx, p) in enumerate(indexed):
            threshold = alpha / (k - rank)
            adj_p = min(p * (k - rank), 1.0)
            adjusted[orig_idx] = adj_p

            if p <= threshold:
                reject_list[orig_idx] = True
            else:
                # Step-down: reject all previously tested
                break

        tests = tuple(HypothesisTest(test_id=f"test_{i}", raw_p_value=p) for i, p in enumerate(p_values))

        return InferenceResult(
            family_id=family_id,
            correction_method="holm",
            alpha=alpha,
            tests=tests,
            adjusted_p_values=tuple(adjusted),
            reject=tuple(reject_list),
            num_tests=k,
            num_rejections=sum(reject_list),
        )

    @staticmethod
    def benjamini_hochberg(
        p_values: List[float],
        alpha: float = 0.05,
        family_id: str = "unknown",
    ) -> InferenceResult:
        """Benjamini-Hochberg procedure for false discovery rate control.

        Less conservative than FWER methods. Appropriate when tests are
        independent or positively correlated (which holds for MIIE detectors
        testing the same metrics across windows).

        Procedure:
            1. Sort p-values: p(1) <= p(2) <= ... <= p(k)
            2. Find largest i such that p(i) <= (i/k) * alpha
            3. Reject H(1)..H(i)

        Args:
            p_values: Raw (uncorrected) p-values.
            alpha: False discovery rate level (default 0.05).
            family_id: Identifier for this family of tests.

        Returns:
            InferenceResult with corrected decisions.
        """
        k = len(p_values)
        if k == 0:
            return InferenceResult(
                family_id=family_id,
                correction_method="bh",
                alpha=alpha,
                tests=(),
                adjusted_p_values=(),
                reject=(),
                num_tests=0,
                num_rejections=0,
            )

        indexed = sorted(enumerate(p_values), key=lambda x: x[1])
        adjusted = [0.0] * k
        reject_list = [False] * k

        # Find largest i where p(i) <= (i/k) * alpha
        max_reject_idx = -1
        for rank, (orig_idx, p) in enumerate(indexed):
            threshold = ((rank + 1) / k) * alpha
            adj_p = min(p * k / (rank + 1), 1.0)
            adjusted[orig_idx] = adj_p

            if p <= threshold:
                max_reject_idx = rank

        # Reject all tests up to and including max_reject_idx
        for rank in range(max_reject_idx + 1):
            orig_idx = indexed[rank][0]
            reject_list[orig_idx] = True

        tests = tuple(HypothesisTest(test_id=f"test_{i}", raw_p_value=p) for i, p in enumerate(p_values))

        return InferenceResult(
            family_id=family_id,
            correction_method="bh",
            alpha=alpha,
            tests=tests,
            adjusted_p_values=tuple(adjusted),
            reject=tuple(reject_list),
            num_tests=k,
            num_rejections=sum(reject_list),
        )

    @staticmethod
    def create_tests(
        test_ids: List[str],
        p_values: List[float],
        test_statistics: List[float] | None = None,
        sample_sizes: List[int] | None = None,
        alternatives: List[str] | None = None,
    ) -> List[HypothesisTest]:
        """Create a list of HypothesisTest objects from parallel arrays.

        Convenience factory for building test lists to pass to correction methods.

        Args:
            test_ids: Unique identifiers for each test.
            p_values: Raw p-values (same length as test_ids).
            test_statistics: Optional observed statistics.
            sample_sizes: Optional sample sizes.
            alternatives: Optional hypothesis directions.

        Returns:
            List of HypothesisTest objects.

        Raises:
            ValueError: If input lengths don't match.
        """
        n = len(test_ids)
        if len(p_values) != n:
            raise ValueError(f"test_ids length {n} != p_values length {len(p_values)}")

        stats = test_statistics or [0.0] * n
        sizes = sample_sizes or [0] * n
        alts = alternatives or ["two-sided"] * n

        if len(stats) != n or len(sizes) != n or len(alts) != n:
            raise ValueError("All input arrays must have the same length")

        return [
            HypothesisTest(
                test_id=tid,
                raw_p_value=p,
                test_statistic=s,
                sample_size=sz,
                alternative=alt,
            )
            for tid, p, s, sz, alt in zip(test_ids, p_values, stats, sizes, alts)
        ]

    @staticmethod
    def result_to_dict(result: InferenceResult) -> Dict[str, Any]:
        """Convert an InferenceResult to a JSON-serializable dictionary.

        Useful for embedding inference metadata in detector output dicts.

        Args:
            result: InferenceResult to convert.

        Returns:
            Dictionary with all inference fields.
        """
        return {
            "family_id": result.family_id,
            "correction_method": result.correction_method,
            "alpha": result.alpha,
            "num_tests": result.num_tests,
            "num_rejections": result.num_rejections,
            "adjusted_p_values": list(result.adjusted_p_values),
            "reject": list(result.reject),
            "tests": [
                {
                    "test_id": t.test_id,
                    "raw_p_value": t.raw_p_value,
                    "alternative": t.alternative,
                    "test_statistic": t.test_statistic,
                    "sample_size": t.sample_size,
                }
                for t in result.tests
            ],
        }
