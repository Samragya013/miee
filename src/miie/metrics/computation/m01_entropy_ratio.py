"""
MIIE v1.6 — M-01 Commit Entropy Ratio Computer.

Computes the normalized Shannon entropy of commit message category
distribution as a ratio in [0, 1].

Scientific Definition (Doc 02 §5.1):
    M-01 quantifies the diversity of commit message content within an
    analysis window. It measures how varied the commit messages are,
    providing a proxy for the breadth of development activity.

Tokenization Strategy (SR-02 / CF-02 remediation):
    Tokens are conventional-commit categories: feat, fix, docs, refactor,
    test, chore, ci, other. Each commit message is classified into exactly
    one category by regex pattern matching against the conventional commit
    specification (https://www.conventionalcommits.org/).

    Category-level tokenization is chosen over word-level because:
    - Deterministic: same input always produces same output
    - Reproducible: no stemming, stopword removal, or language dependencies
    - Meaningful: maps directly to development activity types
    - Standardized: follows conventional commit conventions

Mathematical Formulation:
    Given a set of commit messages C = {c₁, c₂, ..., cₙ}:

    1. Classify each message: cat(cᵢ) → {feat, fix, docs, refactor, test,
       chore, ci, other}
    2. Count category frequencies: nₖ = |{cᵢ : cat(cᵢ) = k}|
    3. Compute proportions: pₖ = nₖ / n
    4. Shannon entropy: H = -Σₖ pₖ · log₂(pₖ)
    5. Maximum entropy: H_max = log₂(|V|) where |V| = number of categories
       with nₖ > 0 (observed vocabulary)
    6. Entropy ratio: ER = H / H_max

    When |V| ≤ 1: ER = 0.0 (no diversity possible)

Edge Cases:
    - Empty message list: ER = 0.0 (no data)
    - All identical messages: ER = 0.0 (single category)
    - Uniform across all 8 categories: ER = 1.0 (maximum diversity)
    - Uniform across k < 8 categories: ER = 1.0 (maximum for observed set)
    - Empty commit messages: Excluded from computation (not classified)
    - Non-ASCII characters: Included in classification; regex is Unicode-aware

Aggregation:
    Within window: mean of per-window ER values.
    Across windows: mean of per-window ER values.

Reference: 02_METRIC_FORMAL_SPECIFICATION.md §5.1
           01_CONFIDENCE_MODEL_UNIFICATION.md
           SR-02 remediation for CF-02
"""

from __future__ import annotations

import math
import re
from typing import Dict, List, Tuple

from miie.metrics.computation.base import BaseMetricComputer
from miie.metrics.models import MetricDefinition

# ---------------------------------------------------------------------------
# Conventional-Commit Category Classification
# ---------------------------------------------------------------------------

# Ordered pairs: (category_name, compiled_regex).
# Order matters: first match wins. Patterns match the start of the lowercased,
# stripped message. The regex requires the category token followed by a
# whitespace, colon, or parenthesis — matching the conventional commit spec.
COMMIT_CATEGORY_PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    ("feat", re.compile(r"^feat[!]?[\s(:]")),
    ("fix", re.compile(r"^fix[!]?[\s(:]")),
    ("docs", re.compile(r"^docs[!]?[\s(:]")),
    ("refactor", re.compile(r"^refactor[!]?[\s(:]")),
    ("test", re.compile(r"^test[!]?[\s(:]")),
    ("chore", re.compile(r"^chore[!]?[\s(:]")),
    ("ci", re.compile(r"^ci[!]?[\s(:]")),
)

# All possible categories (for documentation and H_max computation)
ALL_CATEGORIES: Tuple[str, ...] = tuple(cat for cat, _ in COMMIT_CATEGORY_PATTERNS) + ("other",)

# Number of possible categories
VOCABULARY_SIZE: int = len(ALL_CATEGORIES)  # 8


# ---------------------------------------------------------------------------
# Core Functions
# ---------------------------------------------------------------------------


def classify_commit_message(message: str) -> str:
    """Classify a commit message into a conventional-commit category.

    Classification is deterministic: the same input always produces the
    same output. The algorithm is:

    1. Lowercase and strip the message
    2. Match against conventional-commit patterns in priority order
    3. Return the first matching category, or "other" if no match

    Args:
        message: Raw commit message string.

    Returns:
        One of: feat, fix, docs, refactor, test, chore, ci, other.
    """
    msg_lower = message.lower().strip()
    for category, pattern in COMMIT_CATEGORY_PATTERNS:
        if pattern.match(msg_lower):
            return category
    return "other"


def compute_message_entropy(messages: List[str]) -> float:
    """Compute normalized Shannon entropy of commit message categories.

    This is the authoritative M-01 computation. It operates on the
    category-level tokenization defined in SR-02.

    Algorithm:
        1. Filter out empty/whitespace-only messages
        2. Classify each message into a category
        3. Count category frequencies
        4. Compute Shannon entropy: H = -Σ p·log₂(p)
        5. Normalize by H_max = log₂(|V_observed|)
        6. Return ER = H / H_max

    Args:
        messages: List of raw commit message strings.

    Returns:
        Entropy ratio in [0.0, 1.0].

    Mathematical Properties:
        - ER = 0.0 when all messages are in the same category
        - ER = 1.0 when messages are uniformly distributed across all
          observed categories
        - ER is bounded: 0.0 ≤ ER ≤ 1.0 for all valid inputs
        - ER is deterministic: identical inputs always produce identical outputs
        - ER is symmetric: permuting the message list does not change ER
    """
    # Step 1: Filter empty messages
    valid_messages = [m for m in messages if m and m.strip()]

    if not valid_messages:
        return 0.0

    # Step 2: Classify each message
    categories: Dict[str, int] = {}
    for msg in valid_messages:
        cat = classify_commit_message(msg)
        categories[cat] = categories.get(cat, 0) + 1

    # Step 3: Compute Shannon entropy
    n = len(valid_messages)
    entropy = 0.0
    for count in categories.values():
        if count > 0:
            p = count / n
            entropy -= p * math.log2(p)

    # Step 4: Normalize by observed vocabulary size
    num_observed_categories = len(categories)
    if num_observed_categories <= 1:
        return 0.0

    max_entropy = math.log2(num_observed_categories)
    return entropy / max_entropy if max_entropy > 0 else 0.0


def compute_entropy_from_distribution(
    category_counts: Dict[str, int],
) -> float:
    """Compute normalized Shannon entropy from a pre-computed distribution.

    This is a lower-level function for cases where the category counts
    are already available (e.g., from metadata).

    Args:
        category_counts: Mapping of category name to count.
            Example: {"feat": 5, "fix": 3, "other": 2}

    Returns:
        Entropy ratio in [0.0, 1.0].
    """
    total = sum(category_counts.values())
    if total <= 0:
        return 0.0

    entropy = 0.0
    for count in category_counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    num_categories = sum(1 for c in category_counts.values() if c > 0)
    if num_categories <= 1:
        return 0.0

    max_entropy = math.log2(num_categories)
    return entropy / max_entropy if max_entropy > 0 else 0.0


# ---------------------------------------------------------------------------
# Metric Computer
# ---------------------------------------------------------------------------


class M01EntropyRatioComputer(BaseMetricComputer):
    """Computer for M-01 Commit Entropy Ratio.

    The metric engine receives pre-computed entropy values from the
    observation provider (git.py). This computer validates and aggregates
    those observations using the standard BaseMetricComputer pipeline.

    The actual entropy computation happens in the provider layer because:
    1. The provider has direct access to raw commit messages
    2. Aggregating across all messages in a window is more meaningful
       than per-commit binary signals
    3. The provider can include category distribution metadata

    This computer's role:
    1. Validate observations (unit, range, quality)
    2. Aggregate via mean (standard metric aggregation)
    3. Compute confidence (standard C_m formula)
    """

    _DEFINITION = MetricDefinition(
        metric_id="M-01",
        name="Commit Entropy Ratio",
        unit="ratio",
        min_value=0.0,
        max_value=1.0,
        description=(
            "Normalized Shannon entropy of commit message category distribution. "
            "Categories: feat, fix, docs, refactor, test, chore, ci, other. "
            "Formula: ER = H / log₂(|V|) where H is Shannon entropy and |V| "
            "is the number of observed categories."
        ),
        aggregation="mean",
        required_observations=1,
        dependencies=(),
    )

    @property
    def metric_definition(self) -> MetricDefinition:
        return self._DEFINITION
