"""
GitHub Pull Request data models for the observation provider.

Defines typed dataclasses for GitHub API responses and internal
representation of pull requests and reviews.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, FrozenSet, Optional


class PullRequestState(str, Enum):
    """Pull request state as reported by GitHub API."""

    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


class ReviewState(str, Enum):
    """Pull request review state as reported by GitHub API."""

    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    COMMENTED = "commented"
    DISMISSED = "dismissed"
    PENDING = "pending"


class MergeStrategy(str, Enum):
    """Merge method used for a pull request."""

    MERGE = "merge"
    SQUASH = "squash"
    REBASE = "rebase"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class GitHubUser:
    """Normalized GitHub user."""

    login: str
    id: int
    user_type: str = "User"

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> GitHubUser:
        """Create from GitHub API user object."""
        return cls(
            login=data.get("login", ""),
            id=data.get("id", 0),
            user_type=data.get("type", "User"),
        )


@dataclass(frozen=True)
class PullRequest:
    """Normalized pull request from GitHub API."""

    number: int
    state: PullRequestState
    title: str
    created_at: datetime
    updated_at: datetime
    merged: bool
    merged_at: Optional[datetime]
    merged_by: Optional[GitHubUser]
    closed_at: Optional[datetime]
    user: GitHubUser
    head_sha: str
    base_branch: str
    draft: bool
    changed_files: int
    additions: int
    deletions: int
    review_comments: int
    commits: int
    merged_mergeable: Optional[bool]
    merge_strategy: MergeStrategy
    labels: FrozenSet[str] = frozenset()
    requested_reviewers: FrozenSet[str] = frozenset()
    body_length: int = 0

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> PullRequest:
        """Create from GitHub API pull request object."""
        state_str = data.get("state", "open")
        merged = data.get("merged", False)
        if merged:
            state = PullRequestState.MERGED
        elif state_str == "closed":
            state = PullRequestState.CLOSED
        else:
            state = PullRequestState.OPEN

        merge_method = data.get("merge_method") or "unknown"
        try:
            merge_strategy = MergeStrategy(merge_method)
        except ValueError:
            merge_strategy = MergeStrategy.UNKNOWN

        def _parse_dt(val: Optional[str]) -> Optional[datetime]:
            if not val:
                return None
            return datetime.fromisoformat(val.replace("Z", "+00:00"))

        user_data = data.get("user") or {}
        merged_by_data = data.get("merged_by")

        head = data.get("head") or {}
        base = data.get("base") or {}

        labels = frozenset(label.get("name", "") for label in data.get("labels") or [])

        requested = frozenset(r.get("login", "") for r in data.get("requested_reviewers") or [])

        body = data.get("body") or ""

        return cls(
            number=data.get("number", 0),
            state=state,
            title=data.get("title", ""),
            created_at=_parse_dt(data.get("created_at")) or datetime.now(),
            updated_at=_parse_dt(data.get("updated_at")) or datetime.now(),
            merged=merged,
            merged_at=_parse_dt(data.get("merged_at")),
            merged_by=GitHubUser.from_api(merged_by_data) if merged_by_data else None,
            closed_at=_parse_dt(data.get("closed_at")),
            user=GitHubUser.from_api(user_data),
            head_sha=head.get("sha", ""),
            base_branch=base.get("ref", ""),
            draft=data.get("draft", False),
            changed_files=data.get("changed_files", 0),
            additions=data.get("additions", 0),
            deletions=data.get("deletions", 0),
            review_comments=data.get("review_comments", 0),
            commits=data.get("commits", 0),
            merged_mergeable=data.get("mergeable"),
            merge_strategy=merge_strategy,
            labels=labels,
            requested_reviewers=requested,
            body_length=len(body),
        )


@dataclass(frozen=True)
class Review:
    """Normalized pull request review from GitHub API."""

    id: int
    state: ReviewState
    user: GitHubUser
    submitted_at: Optional[datetime]
    body_length: int
    pull_request_number: int

    @classmethod
    def from_api(cls, data: Dict[str, Any], pr_number: int) -> Review:
        """Create from GitHub API review object."""
        state_str = data.get("state", "commented").lower()
        try:
            state = ReviewState(state_str)
        except ValueError:
            state = ReviewState.COMMENTED

        submitted = data.get("submitted_at")
        submitted_at = None
        if submitted:
            submitted_at = datetime.fromisoformat(submitted.replace("Z", "+00:00"))

        user_data = data.get("user") or {}
        body = data.get("body") or ""

        return cls(
            id=data.get("id", 0),
            state=state,
            user=GitHubUser.from_api(user_data),
            submitted_at=submitted_at,
            body_length=len(body),
            pull_request_number=pr_number,
        )


@dataclass(frozen=True)
class RateLimitInfo:
    """GitHub API rate limit information."""

    limit: int
    remaining: int
    reset_at: Optional[datetime]
    used: int = 0

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> RateLimitInfo:
        """Create from HTTP response headers.

        Header lookup is case-insensitive because ``urllib`` preserves
        the casing sent by the server (e.g. ``X-RateLimit-Limit``),
        not the lowercase form GitHub documents.
        """
        lower = {k.lower(): v for k, v in headers.items()}
        limit = int(lower.get("x-ratelimit-limit", "0"))
        remaining = int(lower.get("x-ratelimit-remaining", "0"))
        used = int(lower.get("x-ratelimit-used", "0"))
        reset_ts = lower.get("x-ratelimit-reset")
        reset_at = None
        if reset_ts:
            try:
                reset_at = datetime.fromtimestamp(int(reset_ts))
            except (ValueError, OSError):
                pass
        return cls(limit=limit, remaining=remaining, reset_at=reset_at, used=used)

    @property
    def is_exhausted(self) -> bool:
        """Check if rate limit is exhausted."""
        return self.remaining <= 0
