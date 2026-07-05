"""Tests for GitHub PR provider models."""

from __future__ import annotations

from miie.providers.github.models import (
    GitHubUser,
    MergeStrategy,
    PullRequest,
    PullRequestState,
    RateLimitInfo,
    Review,
    ReviewState,
)


class TestGitHubUser:
    def test_from_api(self):
        data = {"login": "octocat", "id": 1, "type": "User"}
        user = GitHubUser.from_api(data)
        assert user.login == "octocat"
        assert user.id == 1
        assert user.user_type == "User"

    def test_from_api_defaults(self):
        user = GitHubUser.from_api({})
        assert user.login == ""
        assert user.id == 0
        assert user.user_type == "User"


class TestPullRequest:
    def _make_pr_data(self, **overrides):
        base = {
            "number": 42,
            "state": "open",
            "title": "Add feature",
            "created_at": "2025-01-15T10:00:00Z",
            "updated_at": "2025-01-15T12:00:00Z",
            "merged": False,
            "merged_at": None,
            "merged_by": None,
            "closed_at": None,
            "user": {"login": "author", "id": 10, "type": "User"},
            "head": {"sha": "abc123"},
            "base": {"ref": "main"},
            "draft": False,
            "changed_files": 5,
            "additions": 100,
            "deletions": 30,
            "review_comments": 3,
            "commits": 2,
            "mergeable": True,
            "merge_method": "merge",
            "labels": [{"name": "bug"}],
            "requested_reviewers": [{"login": "reviewer1"}],
            "body": "Fix the bug",
        }
        base.update(overrides)
        return base

    def test_from_api_open(self):
        pr = PullRequest.from_api(self._make_pr_data())
        assert pr.number == 42
        assert pr.state == PullRequestState.OPEN
        assert pr.merged is False
        assert pr.user.login == "author"
        assert pr.head_sha == "abc123"
        assert pr.base_branch == "main"
        assert pr.draft is False
        assert pr.merge_strategy == MergeStrategy.MERGE
        assert pr.labels == frozenset({"bug"})
        assert pr.requested_reviewers == frozenset({"reviewer1"})

    def test_from_api_merged(self):
        data = self._make_pr_data(
            merged=True,
            merged_at="2025-01-16T10:00:00Z",
            merged_by={"login": "merger", "id": 20, "type": "User"},
        )
        pr = PullRequest.from_api(data)
        assert pr.state == PullRequestState.MERGED
        assert pr.merged is True
        assert pr.merged_at is not None
        assert pr.merged_by.login == "merger"

    def test_from_api_closed(self):
        data = self._make_pr_data(state="closed")
        pr = PullRequest.from_api(data)
        assert pr.state == PullRequestState.CLOSED

    def test_from_api_draft(self):
        data = self._make_pr_data(draft=True)
        pr = PullRequest.from_api(data)
        assert pr.draft is True

    def test_from_api_squash_merge(self):
        data = self._make_pr_data(merge_method="squash")
        pr = PullRequest.from_api(data)
        assert pr.merge_strategy == MergeStrategy.SQUASH

    def test_from_api_unknown_merge(self):
        data = self._make_pr_data(merge_method="custom")
        pr = PullRequest.from_api(data)
        assert pr.merge_strategy == MergeStrategy.UNKNOWN

    def test_from_api_empty_user(self):
        data = self._make_pr_data(user={})
        pr = PullRequest.from_api(data)
        assert pr.user.login == ""

    def test_from_api_body_length(self):
        data = self._make_pr_data(body="x" * 500)
        pr = PullRequest.from_api(data)
        assert pr.body_length == 500


class TestReview:
    def _make_review_data(self, **overrides):
        base = {
            "id": 100,
            "state": "APPROVED",
            "user": {"login": "reviewer1", "id": 30, "type": "User"},
            "submitted_at": "2025-01-15T14:00:00Z",
            "body": "LGTM",
        }
        base.update(overrides)
        return base

    def test_from_api_approved(self):
        review = Review.from_api(self._make_review_data(), pr_number=42)
        assert review.id == 100
        assert review.state == ReviewState.APPROVED
        assert review.user.login == "reviewer1"
        assert review.pull_request_number == 42
        assert review.body_length == 4

    def test_from_api_changes_requested(self):
        review = Review.from_api(self._make_review_data(state="CHANGES_REQUESTED"), pr_number=42)
        assert review.state == ReviewState.CHANGES_REQUESTED

    def test_from_api_commented(self):
        review = Review.from_api(self._make_review_data(state="COMMENTED"), pr_number=42)
        assert review.state == ReviewState.COMMENTED

    def test_from_api_pending(self):
        review = Review.from_api(self._make_review_data(state="PENDING"), pr_number=42)
        assert review.state == ReviewState.PENDING

    def test_from_api_unknown_state(self):
        review = Review.from_api(self._make_review_data(state="UNKNOWN"), pr_number=42)
        assert review.state == ReviewState.COMMENTED

    def test_from_api_no_submitted_at(self):
        review = Review.from_api(self._make_review_data(submitted_at=None), pr_number=42)
        assert review.submitted_at is None


class TestRateLimitInfo:
    def test_from_headers(self):
        headers = {
            "x-ratelimit-limit": "5000",
            "x-ratelimit-remaining": "4999",
            "x-ratelimit-used": "1",
            "x-ratelimit-reset": "1700000000",
        }
        info = RateLimitInfo.from_headers(headers)
        assert info.limit == 5000
        assert info.remaining == 4999
        assert info.used == 1
        assert info.is_exhausted is False

    def test_from_headers_exhausted(self):
        headers = {
            "x-ratelimit-limit": "5000",
            "x-ratelimit-remaining": "0",
            "x-ratelimit-used": "5000",
        }
        info = RateLimitInfo.from_headers(headers)
        assert info.is_exhausted is True

    def test_from_headers_missing(self):
        info = RateLimitInfo.from_headers({})
        assert info.limit == 0
        assert info.remaining == 0
        assert info.is_exhausted is True

    def test_from_headers_invalid_reset(self):
        headers = {
            "x-ratelimit-limit": "5000",
            "x-ratelimit-remaining": "4999",
            "x-ratelimit-reset": "not-a-number",
        }
        info = RateLimitInfo.from_headers(headers)
        assert info.reset_at is None
