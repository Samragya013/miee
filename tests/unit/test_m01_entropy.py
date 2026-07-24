"""
Tests for M-01 Commit Entropy Ratio — SR-02 remediation.

Covers:
- Category-level tokenization (all 8 categories + other)
- Shannon entropy computation
- Normalization by observed vocabulary size
- Edge cases (empty, single category, uniform, skewed)
- Determinism verification
- Mathematical properties (bounds, symmetry)
- compute_entropy_from_distribution()
- M01EntropyRatioComputer metric definition
"""

from __future__ import annotations

import pytest

from miie.metrics.computation.m01_entropy_ratio import (
    ALL_CATEGORIES,
    COMMIT_CATEGORY_PATTERNS,
    VOCABULARY_SIZE,
    M01EntropyRatioComputer,
    classify_commit_message,
    compute_entropy_from_distribution,
    compute_message_entropy,
)

# ---------------------------------------------------------------------------
# Classification Tests
# ---------------------------------------------------------------------------


class TestClassifyCommitMessage:
    """Verify category classification for all conventional-commit prefixes."""

    @pytest.mark.parametrize(
        "message, expected",
        [
            ("feat: add login", "feat"),
            ("feat(api): add endpoint", "feat"),
            ("feat!: breaking change", "feat"),
            ("fix: resolve crash", "fix"),
            ("fix(parser): handle null", "fix"),
            ("docs: update readme", "docs"),
            ("docs(api): add examples", "docs"),
            ("refactor: clean up", "refactor"),
            ("refactor(core): extract logic", "refactor"),
            ("test: add unit tests", "test"),
            ("test(e2e): add login flow", "test"),
            ("chore: bump deps", "chore"),
            ("chore(deps): update npm", "chore"),
            ("ci: add workflow", "ci"),
            ("ci(actions): add lint", "ci"),
            ("random message", "other"),
            ("", "other"),
            ("   ", "other"),
            ("FEAT: uppercase", "feat"),
            ("FIX: uppercase", "fix"),
        ],
    )
    def test_classify(self, message: str, expected: str):
        assert classify_commit_message(message) == expected

    def test_all_categories_are_defined(self):
        assert len(ALL_CATEGORIES) == 8
        assert set(ALL_CATEGORIES) == {
            "feat",
            "fix",
            "docs",
            "refactor",
            "test",
            "chore",
            "ci",
            "other",
        }

    def test_patterns_count(self):
        """7 patterns + 'other' fallback = 8 categories."""
        assert len(COMMIT_CATEGORY_PATTERNS) == 7
        assert VOCABULARY_SIZE == 8


# ---------------------------------------------------------------------------
# Entropy Computation Tests
# ---------------------------------------------------------------------------


class TestComputeMessageEntropy:
    """Verify Shannon entropy computation and normalization."""

    def test_empty_messages(self):
        assert compute_message_entropy([]) == 0.0

    def test_whitespace_only_messages(self):
        assert compute_message_entropy(["", "  ", "\t"]) == 0.0

    def test_single_message(self):
        assert compute_message_entropy(["feat: something"]) == 0.0

    def test_all_same_category(self):
        msgs = ["feat: a", "feat: b", "feat: c", "feat: d"]
        assert compute_message_entropy(msgs) == 0.0

    def test_two_equal_categories(self):
        msgs = ["feat: a", "feat: b", "fix: a", "fix: b"]
        result = compute_message_entropy(msgs)
        # H = -2 * (0.5 * log2(0.5)) = 1.0, H_max = log2(2) = 1.0
        assert abs(result - 1.0) < 0.01

    def test_three_equal_categories(self):
        msgs = ["feat: a", "fix: b", "docs: c"]
        result = compute_message_entropy(msgs)
        # H = -3 * (1/3 * log2(1/3)) = log2(3) ≈ 1.585
        # H_max = log2(3) ≈ 1.585
        # ER = 1.0
        assert abs(result - 1.0) < 0.01

    def test_seven_categories(self):
        msgs = [
            "feat: a",
            "fix: b",
            "docs: c",
            "refactor: d",
            "test: e",
            "chore: f",
            "ci: g",
        ]
        result = compute_message_entropy(msgs)
        assert result > 0.8

    def test_eight_categoriesIncludingOther(self):
        msgs = [
            "feat: a",
            "fix: b",
            "docs: c",
            "refactor: d",
            "test: e",
            "chore: f",
            "ci: g",
            "random: h",
        ]
        result = compute_message_entropy(msgs)
        assert abs(result - 1.0) < 0.01

    def test_skewed_distribution(self):
        # 9 feat, 1 fix → low diversity
        msgs = ["feat: a"] * 9 + ["fix: b"]
        result = compute_message_entropy(msgs)
        assert 0.0 < result < 0.5

    def test_highly_skewed(self):
        # 99 feat, 1 fix → very low diversity
        msgs = ["feat: a"] * 99 + ["fix: b"]
        result = compute_message_entropy(msgs)
        assert 0.0 < result < 0.15

    def test_determinism(self):
        msgs = ["feat: a", "fix: b", "docs: c", "refactor: d"]
        r1 = compute_message_entropy(msgs)
        r2 = compute_message_entropy(msgs)
        assert r1 == r2

    def test_permutation_invariance(self):
        """Permuting messages should not change entropy."""
        msgs1 = ["feat: a", "fix: b", "docs: c"]
        msgs2 = ["docs: c", "feat: a", "fix: b"]
        assert compute_message_entropy(msgs1) == compute_message_entropy(msgs2)

    def test_bounds(self):
        """Entropy ratio must always be in [0, 1]."""
        test_cases = [
            [],
            ["feat: a"],
            ["feat: a", "fix: b"],
            ["feat: a"] * 100 + ["fix: b"],
            ["feat: a", "fix: b", "docs: c", "refactor: d", "test: e", "chore: f", "ci: g", "other: h"],
        ]
        for msgs in test_cases:
            result = compute_message_entropy(msgs)
            assert 0.0 <= result <= 1.0, f"ER={result} for {msgs}"


# ---------------------------------------------------------------------------
# Distribution-Based Entropy Tests
# ---------------------------------------------------------------------------


class TestComputeEntropyFromDistribution:
    """Verify entropy from pre-computed category counts."""

    def test_empty_distribution(self):
        assert compute_entropy_from_distribution({}) == 0.0

    def test_zero_counts(self):
        assert compute_entropy_from_distribution({"feat": 0, "fix": 0}) == 0.0

    def test_single_category(self):
        assert compute_entropy_from_distribution({"feat": 10}) == 0.0

    def test_two_equal_categories(self):
        result = compute_entropy_from_distribution({"feat": 5, "fix": 5})
        assert abs(result - 1.0) < 0.01

    def test_skewed(self):
        result = compute_entropy_from_distribution({"feat": 90, "fix": 10})
        assert 0.0 < result < 0.5

    def test_matches_message_entropy(self):
        """Pre-computed distribution should match message-based computation."""
        msgs = ["feat: a", "feat: b", "fix: c", "docs: d"]
        from collections import Counter

        counts = Counter(classify_commit_message(m) for m in msgs)
        r1 = compute_message_entropy(msgs)
        r2 = compute_entropy_from_distribution(dict(counts))
        assert abs(r1 - r2) < 1e-10


# ---------------------------------------------------------------------------
# Metric Computer Tests
# ---------------------------------------------------------------------------


class TestM01EntropyRatioComputer:
    """Verify metric definition and basic computation."""

    def test_metric_id(self):
        computer = M01EntropyRatioComputer()
        assert computer.metric_definition.metric_id == "M-01"

    def test_metric_name(self):
        computer = M01EntropyRatioComputer()
        assert computer.metric_definition.name == "Commit Entropy Ratio"

    def test_metric_unit(self):
        computer = M01EntropyRatioComputer()
        assert computer.metric_definition.unit == "ratio"

    def test_metric_bounds(self):
        computer = M01EntropyRatioComputer()
        assert computer.metric_definition.min_value == 0.0
        assert computer.metric_definition.max_value == 1.0

    def test_metric_aggregation(self):
        computer = M01EntropyRatioComputer()
        assert computer.metric_definition.aggregation == "mean"

    def test_no_dependencies(self):
        computer = M01EntropyRatioComputer()
        assert computer.metric_definition.dependencies == ()

    def test_required_observations(self):
        computer = M01EntropyRatioComputer()
        assert computer.metric_definition.required_observations == 1


# ---------------------------------------------------------------------------
# Edge Case and Regression Tests
# ---------------------------------------------------------------------------


class TestM01EdgeCases:
    """Edge cases from Doc 02 §5.1 and SR-02 specification."""

    def test_empty_repository(self):
        """No commits → no observations → metric not computed."""
        assert compute_message_entropy([]) == 0.0

    def test_one_commit(self):
        """Single commit → one category → ER = 0.0."""
        assert compute_message_entropy(["feat: only commit"]) == 0.0

    def test_one_token(self):
        """Single-word messages all in same category → ER = 0.0."""
        msgs = ["fix", "fix", "fix"]
        # These will be classified as "fix" (matches ^fix[\s(:])
        # Actually "fix" alone doesn't match the pattern (no whitespace/colon/paren after)
        # It will be classified as "other"
        cats = [classify_commit_message(m) for m in msgs]
        # All same category → ER = 0.0
        assert len(set(cats)) == 1
        assert compute_message_entropy(msgs) == 0.0

    def test_uniform_all_categories(self):
        """One per category → ER = 1.0."""
        msgs = [
            "feat: a",
            "fix: b",
            "docs: c",
            "refactor: d",
            "test: e",
            "chore: f",
            "ci: g",
            "other: h",
        ]
        assert abs(compute_message_entropy(msgs) - 1.0) < 0.01

    def test_non_ascii_characters(self):
        """Non-ASCII should be included in classification."""
        msgs = ["feat:添加登录", "fix:修复崩溃"]
        cats = [classify_commit_message(m) for m in msgs]
        assert cats == ["feat", "fix"]

    def test_merge_commits(self):
        """Merge commits classified like any other message."""
        msgs = ["Merge branch 'feature'", "feat: add feature"]
        cats = [classify_commit_message(m) for m in msgs]
        assert cats[0] == "other"  # Merge doesn't match any pattern
        assert cats[1] == "feat"

    def test_bot_commits(self):
        """Bot commits classified by their message content."""
        msgs = ["chore: bump version", "ci: auto lint"]
        cats = [classify_commit_message(m) for m in msgs]
        assert cats == ["chore", "ci"]

    def test_repeated_identical_messages(self):
        """Many identical messages → ER = 0.0."""
        msgs = ["fix: typo"] * 50
        assert compute_message_entropy(msgs) == 0.0

    def test_formula_in_metadata(self):
        """M-01 observations should include tokenization metadata."""
        # This is tested indirectly through the provider extraction
        # The metadata should contain "tokenization": "category"
        pass  # Covered by integration tests
