"""Tests for GitHub PR provider normalization."""

from __future__ import annotations

import datetime

import pytest

from miie.processing.observation.models import ObservationProvenance
from miie.providers.github.models import (
    GitHubUser,
    MergeStrategy,
    PullRequest,
    PullRequestState,
    Review,
    ReviewState,
)
from miie.providers.github.normalization import (
    _hours_between,
    normalize_pr_close,
    normalize_pr_creation,
    normalize_pr_draft,
    normalize_pr_merge,
    normalize_pr_reopened,
    normalize_review,
    normalize_review_iterations,
    normalize_reviewer_count,
)


def _provenance() -> ObservationProvenance:
    return ObservationProvenance(
        extractor_id="test",
        extraction_timestamp="2025-01-15T10:00:00+00:00",
    )


def _make_pr(**overrides) -> PullRequest:
    defaults = dict(
        number=1,
        state=PullRequestState.OPEN,
        title="Test PR",
        created_at=datetime.datetime(2025, 1, 15, 10, 0, tzinfo=datetime.timezone.utc),
        updated_at=datetime.datetime(2025, 1, 15, 12, 0, tzinfo=datetime.timezone.utc),
        merged=False,
        merged_at=None,
        merged_by=None,
        closed_at=None,
        user=GitHubUser(login="author", id=1),
        head_sha="abc123",
        base_branch="main",
        draft=False,
        changed_files=5,
        additions=100,
        deletions=30,
        review_comments=3,
        commits=2,
        merged_mergeable=True,
        merge_strategy=MergeStrategy.MERGE,
    )
    defaults.update(overrides)
    return PullRequest(**defaults)


def _make_review(**overrides) -> Review:
    defaults = dict(
        id=100,
        state=ReviewState.APPROVED,
        user=GitHubUser(login="reviewer1", id=2),
        submitted_at=datetime.datetime(2025, 1, 15, 14, 0, tzinfo=datetime.timezone.utc),
        body_length=4,
        pull_request_number=1,
    )
    defaults.update(overrides)
    return Review(**defaults)


class TestHoursBetween:
    def test_positive(self):
        a = datetime.datetime(2025, 1, 15, 10, 0, tzinfo=datetime.timezone.utc)
        b = datetime.datetime(2025, 1, 15, 14, 0, tzinfo=datetime.timezone.utc)
        assert _hours_between(a, b) == pytest.approx(4.0)

    def test_reversed(self):
        a = datetime.datetime(2025, 1, 15, 14, 0, tzinfo=datetime.timezone.utc)
        b = datetime.datetime(2025, 1, 15, 10, 0, tzinfo=datetime.timezone.utc)
        assert _hours_between(a, b) == pytest.approx(0.0)

    def test_none_values(self):
        assert _hours_between(None, None) == 0.0
        assert _hours_between(datetime.datetime.now(datetime.timezone.utc), None) == 0.0


class TestNormalizePRCreation:
    def test_basic(self):
        pr = _make_pr()
        obs = normalize_pr_creation(pr, _provenance())
        assert obs.metric_id == "M-02"
        assert obs.value == 1.0
        assert obs.unit == "count"
        assert obs.source_type == "branch"
        assert obs.source_id == "pr-1"
        assert obs.quality == "complete"

    def test_metadata(self):
        pr = _make_pr(number=42, title="Fix bug", draft=True)
        obs = normalize_pr_creation(pr, _provenance())
        assert obs.metadata["pr_number"] == "42"
        assert obs.metadata["title"] == "Fix bug"
        assert obs.metadata["draft"] == "True"


class TestNormalizePRMerge:
    def test_basic(self):
        pr = _make_pr(
            merged=True,
            merged_at=datetime.datetime(2025, 1, 16, 10, 0, tzinfo=datetime.timezone.utc),
        )
        obs = normalize_pr_merge(pr, _provenance())
        assert obs.metric_id == "M-05"
        assert obs.unit == "hours"
        assert obs.value == pytest.approx(24.0)
        assert obs.metadata["event_type"] == "merge"


class TestNormalizePRClose:
    def test_basic(self):
        pr = _make_pr(
            state=PullRequestState.CLOSED,
            closed_at=datetime.datetime(2025, 1, 20, 10, 0, tzinfo=datetime.timezone.utc),
        )
        obs = normalize_pr_close(pr, _provenance())
        assert obs.metric_id == "M-05"
        assert obs.unit == "hours"
        assert obs.value == pytest.approx(120.0)
        assert obs.metadata["event_type"] == "close"


class TestNormalizePRDraft:
    def test_basic(self):
        pr = _make_pr(draft=True)
        obs = normalize_pr_draft(pr, _provenance())
        assert obs.metric_id == "M-02"
        assert obs.metadata["event_type"] == "draft"
        assert obs.metadata["is_draft"] == "True"


class TestNormalizePRReopened:
    def test_basic(self):
        pr = _make_pr()
        obs = normalize_pr_reopened(pr, _provenance())
        assert obs.metric_id == "M-02"
        assert obs.metadata["event_type"] == "reopened"


class TestNormalizeReview:
    def test_approved(self):
        review = _make_review()
        pr = _make_pr()
        obs = normalize_review(review, pr, _provenance())
        assert obs.metric_id == "M-05"
        assert obs.unit == "hours"
        assert obs.value == pytest.approx(4.0)
        assert obs.metadata["review_state"] == "approved"
        assert obs.metadata["reviewer"] == "reviewer1"
        assert obs.quality == "complete"

    def test_pending_review(self):
        review = _make_review(state=ReviewState.PENDING, submitted_at=None)
        pr = _make_pr()
        obs = normalize_review(review, pr, _provenance())
        assert obs.quality == "estimated"


class TestNormalizeReviewerCount:
    def test_basic(self):
        pr = _make_pr()
        obs = normalize_reviewer_count(pr, 3, _provenance())
        assert obs.value == 3.0
        assert obs.metadata["unique_reviewers"] == "3"


class TestNormalizeReviewIterations:
    def test_basic(self):
        pr = _make_pr()
        obs = normalize_review_iterations(pr, 5, _provenance())
        assert obs.value == 5.0
        assert obs.metadata["review_count"] == "5"
