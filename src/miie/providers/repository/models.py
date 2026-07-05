"""
Repository metadata data models for the observation provider.

Defines typed dataclasses for GitHub repository API responses and
internal representation of repository characteristics.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, FrozenSet, Optional


@dataclass(frozen=True)
class RepositoryMetadata:
    """Normalized repository metadata from GitHub API."""

    name: str
    full_name: str
    description: Optional[str]
    homepage: Optional[str]
    default_branch: str
    primary_language: Optional[str]
    languages: Dict[str, int]
    license: Optional[str]
    visibility: str
    is_archived: bool
    is_fork: bool
    fork_count: int
    stars: int
    watchers: int
    open_issues: int
    size: int
    topics: FrozenSet[str]
    created_at: datetime
    updated_at: datetime
    pushed_at: Optional[datetime]
    default_branch_protection: Optional[bool] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> RepositoryMetadata:
        """Create from GitHub API repository object."""
        license_data = data.get("license")
        license_key = license_data.get("key") if license_data else None

        languages = data.get("languages") or {}
        if not languages and data.get("language"):
            languages = {data["language"]: data.get("size", 0)}

        topics = frozenset(data.get("topics") or [])

        def _parse_dt(val: Optional[str]) -> Optional[datetime]:
            if not val:
                return None
            return datetime.fromisoformat(val.replace("Z", "+00:00"))

        created_at = _parse_dt(data.get("created_at")) or datetime.now(datetime.timezone.utc)
        updated_at = _parse_dt(data.get("updated_at")) or datetime.now(datetime.timezone.utc)
        pushed_at = _parse_dt(data.get("pushed_at"))

        return cls(
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            description=data.get("description"),
            homepage=data.get("homepage"),
            default_branch=data.get("default_branch", "main"),
            primary_language=data.get("language"),
            languages=languages,
            license=license_key,
            visibility=data.get("visibility", "public"),
            is_archived=data.get("archived", False),
            is_fork=data.get("fork", False),
            fork_count=data.get("forks_count", 0),
            stars=data.get("stargazers_count", 0),
            watchers=data.get("watchers_count", 0),
            open_issues=data.get("open_issues_count", 0),
            size=data.get("size", 0),
            topics=topics,
            created_at=created_at,
            updated_at=updated_at,
            pushed_at=pushed_at,
        )
