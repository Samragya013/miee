"""
Normalizes GitHub PR / review API data into MIIE Observation objects.

Every observation produced by the provider passes through this module
to ensure consistent structure and provenance.
"""

from __future__ import annotations

import datetime
from typing import Dict, Optional

from miie.processing.observation.models import (
    Observation,
    ObservationProvenance,
    generate_observation_id,
)
from miie.providers.github.models import (
    PullRequest,
    Review,
    ReviewState,
)


def _ts(dt: Optional[datetime.datetime]) -> str:
    """Return ISO-8601 string for a datetime, or current time."""
    if dt is not None:
        return dt.isoformat()
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _hours_between(
    earlier: Optional[datetime.datetime],
    later: Optional[datetime.datetime],
) -> float:
    """Hours between two datetimes (always positive)."""
    if earlier is None or later is None:
        return 0.0
    delta = later - earlier
    return max(delta.total_seconds() / 3600.0, 0.0)


# ------------------------------------------------------------------
# PR-level observations
# ------------------------------------------------------------------


def normalize_pr_creation(
    pr: PullRequest,
    provenance: ObservationProvenance,
) -> Observation:
    """M-02 style: each PR counts as 1 creation event."""
    return Observation(
        observation_id=generate_observation_id("branch", f"pr-{pr.number}", "M-02"),
        source_type="branch",
        source_id=f"pr-{pr.number}",
        metric_id="M-02",
        value=1.0,
        unit="count",
        timestamp=_ts(pr.created_at),
        quality="complete",
        provenance=provenance,
        metadata=_pr_metadata(pr),
    )


def normalize_pr_merge(
    pr: PullRequest,
    provenance: ObservationProvenance,
) -> Observation:
    """Record merge latency (hours) for a merged PR."""
    merge_latency = _hours_between(pr.created_at, pr.merged_at)
    return Observation(
        observation_id=generate_observation_id("branch", f"pr-{pr.number}", "M-05"),
        source_type="branch",
        source_id=f"pr-{pr.number}",
        metric_id="M-05",
        value=merge_latency,
        unit="hours",
        timestamp=_ts(pr.merged_at),
        quality="complete",
        provenance=provenance,
        metadata={
            **_pr_metadata(pr),
            "event_type": "merge",
        },
    )


def normalize_pr_close(
    pr: PullRequest,
    provenance: ObservationProvenance,
) -> Observation:
    """Record close latency for a closed (non-merged) PR."""
    close_latency = _hours_between(pr.created_at, pr.closed_at)
    return Observation(
        observation_id=generate_observation_id("branch", f"pr-{pr.number}", "M-05"),
        source_type="branch",
        source_id=f"pr-{pr.number}",
        metric_id="M-05",
        value=close_latency,
        unit="hours",
        timestamp=_ts(pr.closed_at),
        quality="complete",
        provenance=provenance,
        metadata={
            **_pr_metadata(pr),
            "event_type": "close",
        },
    )


def normalize_pr_draft(
    pr: PullRequest,
    provenance: ObservationProvenance,
) -> Observation:
    """Record draft PR status."""
    return Observation(
        observation_id=generate_observation_id("branch", f"pr-{pr.number}", "M-02"),
        source_type="branch",
        source_id=f"pr-{pr.number}",
        metric_id="M-02",
        value=1.0,
        unit="count",
        timestamp=_ts(pr.created_at),
        quality="complete",
        provenance=provenance,
        metadata={
            **_pr_metadata(pr),
            "event_type": "draft",
            "is_draft": str(pr.draft),
        },
    )


def normalize_pr_reopened(
    pr: PullRequest,
    provenance: ObservationProvenance,
) -> Observation:
    """Record PR reopen event."""
    return Observation(
        observation_id=generate_observation_id("branch", f"pr-{pr.number}", "M-02"),
        source_type="branch",
        source_id=f"pr-{pr.number}",
        metric_id="M-02",
        value=1.0,
        unit="count",
        timestamp=_ts(pr.updated_at),
        quality="complete",
        provenance=provenance,
        metadata={
            **_pr_metadata(pr),
            "event_type": "reopened",
        },
    )


# ------------------------------------------------------------------
# Review-level observations
# ------------------------------------------------------------------


def normalize_review(
    review: Review,
    pr: PullRequest,
    provenance: ObservationProvenance,
) -> Observation:
    """Record a review event with latency and participation data."""
    review_latency = _hours_between(pr.created_at, review.submitted_at)

    event_type = "review_" + review.state.value
    quality = "complete" if review.state != ReviewState.PENDING else "estimated"

    return Observation(
        observation_id=generate_observation_id("commit", f"pr-{pr.number}-r-{review.id}", "M-05"),
        source_type="branch",
        source_id=f"pr-{pr.number}-r-{review.id}",
        metric_id="M-05",
        value=review_latency,
        unit="hours",
        timestamp=_ts(review.submitted_at),
        quality=quality,
        provenance=provenance,
        metadata={
            "pr_number": str(pr.number),
            "reviewer": review.user.login,
            "review_state": review.state.value,
            "event_type": event_type,
            "body_length": str(review.body_length),
        },
    )


def normalize_reviewer_count(
    pr: PullRequest,
    unique_reviewers: int,
    provenance: ObservationProvenance,
) -> Observation:
    """Record the number of unique reviewers on a PR."""
    return Observation(
        observation_id=generate_observation_id("branch", f"pr-{pr.number}-reviewers", "M-02"),
        source_type="branch",
        source_id=f"pr-{pr.number}",
        metric_id="M-02",
        value=float(unique_reviewers),
        unit="count",
        timestamp=_ts(pr.updated_at),
        quality="complete",
        provenance=provenance,
        metadata={
            **_pr_metadata(pr),
            "event_type": "reviewer_count",
            "unique_reviewers": str(unique_reviewers),
        },
    )


def normalize_review_iterations(
    pr: PullRequest,
    review_count: int,
    provenance: ObservationProvenance,
) -> Observation:
    """Record the number of review iterations on a PR."""
    return Observation(
        observation_id=generate_observation_id("branch", f"pr-{pr.number}-iterations", "M-02"),
        source_type="branch",
        source_id=f"pr-{pr.number}",
        metric_id="M-02",
        value=float(review_count),
        unit="count",
        timestamp=_ts(pr.updated_at),
        quality="complete",
        provenance=provenance,
        metadata={
            **_pr_metadata(pr),
            "event_type": "review_iterations",
            "review_count": str(review_count),
        },
    )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _pr_metadata(pr: PullRequest) -> Dict[str, str]:
    """Build common PR metadata dict."""
    return {
        "pr_number": str(pr.number),
        "title": pr.title,
        "author": pr.user.login,
        "state": pr.state.value,
        "merged": str(pr.merged),
        "draft": str(pr.draft),
        "base_branch": pr.base_branch,
        "head_sha": pr.head_sha,
        "changed_files": str(pr.changed_files),
        "additions": str(pr.additions),
        "deletions": str(pr.deletions),
        "review_comments": str(pr.review_comments),
        "commits": str(pr.commits),
        "merge_strategy": pr.merge_strategy.value,
    }
