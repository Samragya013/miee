"""
GitHub authentication for the observation provider.

Supports Personal Access Tokens via environment variable or explicit
configuration. Anonymous access is allowed for public repositories.

PR-12B: Enhanced with multi-source token discovery, environment
diagnostics, and rate-limit reporting.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

# Ordered list of environment variables to check for tokens.
# First non-empty value wins.
_TOKEN_ENV_VARS: tuple[str, ...] = (
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "GITHUB_PAT",
)


def _discover_token() -> tuple[Optional[str], str]:
    """Auto-discover a GitHub token from environment variables.

    Returns:
        (token, source_name) — token is None if no env var is set.
    """
    for env_var in _TOKEN_ENV_VARS:
        val = os.environ.get(env_var)
        if val:
            return val, f"env:{env_var}"
    return None, "none"


@dataclass(frozen=True)
class GitHubAuth:
    """GitHub authentication configuration.

    Resolution order:
      1. Explicit ``token`` parameter
      2. ``GITHUB_TOKEN`` environment variable
      3. ``GH_TOKEN`` environment variable
      4. ``GITHUB_PAT`` environment variable
      5. Anonymous access (public repos only)
    """

    token: Optional[str] = None
    source: str = "none"

    def __post_init__(self) -> None:
        if self.token is None:
            env_token, env_source = _discover_token()
            if env_token:
                object.__setattr__(self, "token", env_token)
                object.__setattr__(self, "source", env_source)

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> GitHubAuth:
        """Create from a provider config dict.

        Keys: ``token``, ``github_token``.
        """
        token = config.get("token") or config.get("github_token")
        if token:
            return cls(token=str(token), source="config")
        return cls()

    @property
    def is_authenticated(self) -> bool:
        """Whether a token is present."""
        return self.token is not None and len(self.token) > 0

    @property
    def is_anonymous(self) -> bool:
        """Whether this is anonymous access."""
        return not self.is_authenticated

    @property
    def token_preview(self) -> str:
        """Masked token preview for diagnostics (never exposes full token)."""
        if not self.is_authenticated:
            return "(none)"
        return f"{self.token[:4]}...{self.token[-4:]}" if len(self.token) > 8 else "****"

    def to_header_dict(self) -> Dict[str, str]:
        """Return HTTP headers for GitHub API requests."""
        headers: Dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.is_authenticated:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def validate_permissions(self, headers: Dict[str, str]) -> Optional[str]:
        """Check rate-limit / auth headers for permission issues.

        Returns an error message if access is denied, or ``None`` if OK.
        """
        lower = {k.lower(): v for k, v in headers.items()}
        status = lower.get("x-ratelimit-remaining")
        if status is not None and int(status) <= 0:
            return "GitHub API rate limit exhausted"
        return None

    def diagnostics(self) -> Dict[str, Any]:
        """Return authentication diagnostics for logging and reporting.

        Never exposes the full token — only source, masked preview,
        and authentication status.
        """
        return {
            "authenticated": self.is_authenticated,
            "anonymous": self.is_anonymous,
            "source": self.source,
            "token_preview": self.token_preview,
            "searched_env_vars": list(_TOKEN_ENV_VARS),
        }


def summarize_auth_status(auth: GitHubAuth) -> str:
    """Return a one-line human-readable auth status string."""
    if auth.is_authenticated:
        return f"Authenticated via {auth.source} (token: {auth.token_preview})"
    return f"Anonymous — searched {', '.join(_TOKEN_ENV_VARS)} (none found)"
