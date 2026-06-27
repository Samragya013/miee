"""Git URL parser and cloner for MIIE.

Parses GitHub URLs, validates ownership, and clones repositories with auth support.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

# GitHub URL patterns
GITHUB_URL_PATTERNS = [
    r"^https?://github\.com/([^/]+/[^/]+)(?:\.git)?$",
    r"^git@github\.com:([^/]+/[^/]+)\.git$",
    r"^ssh://git@github\.com/([^/]+/[^/]+)\.git$",
]


class GitURLParser:
    """Parse and validate GitHub repository URLs."""

    @staticmethod
    def parse(url: str) -> Tuple[str, str]:
        """Parse GitHub URL and return (owner, repo).

        Args:
            url: GitHub repository URL

        Returns:
            Tuple of (owner, repo)

        Raises:
            ValueError: If URL is invalid or not a GitHub URL
        """
        url = url.strip()

        # Handle SSH URLs (git@github.com:owner/repo.git)
        if url.startswith("git@github.com:"):
            url = "https://" + url.replace("git@github.com:", "github.com/")

        # Handle ssh://git@github.com/ URLs
        if url.startswith("ssh://git@github.com/"):
            url = "https://" + url[len("ssh://git@") :]

        # Handle git:// URLs
        if url.startswith("git://"):
            url = url.replace("git://", "https://")

        parsed = urlparse(url)
        # Only allow http/https schemes
        if parsed.scheme not in ("http", "https", ""):
            raise ValueError(f"Unsupported URL scheme: {parsed.scheme} — {url}")

        if parsed.netloc not in ("github.com", "www.github.com"):
            raise ValueError(f"Not a GitHub URL: {url}")

        path = parsed.path.strip("/")
        if not path:
            raise ValueError(f"Invalid GitHub URL (no path): {url}")

        # Remove .git suffix if present
        if path.endswith(".git"):
            path = path[:-4]

        parts = path.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid GitHub URL path: {path}")

        owner, repo = parts
        if not owner or not repo:
            raise ValueError(f"Invalid owner or repo in URL: {url}")

        return owner, repo

    @staticmethod
    def is_github_url(url: str) -> bool:
        """Check if URL is a GitHub repository URL."""
        try:
            GitURLParser.parse(url)
            return True
        except ValueError:
            return False


class GitCloner:
    """Clone Git repositories with auth support and cleanup."""

    def __init__(self, auth_token: Optional[str] = None, shallow_depth: int = 1):
        """Initialize Git cloner.

        Args:
            auth_token: GitHub personal access token for private repos
            shallow_depth: Depth for shallow clone (default: 1)
        """
        self.auth_token = auth_token
        self.shallow_depth = shallow_depth

    def clone(self, url: str, target_dir: Optional[Path] = None, cleanup_after: bool = False) -> Path:
        """Clone a GitHub repository.

        Args:
            url: GitHub repository URL
            target_dir: Target directory (creates temp dir if None)
            cleanup_after: Whether to clean up temp dir after analysis

        Returns:
            Path to cloned repository

        Raises:
            ValueError: If URL is invalid
            RuntimeError: If git clone fails
        """
        # Validate and parse URL
        owner, repo = GitURLParser.parse(url)

        # Determine target directory
        if target_dir is None:
            target_dir = Path(tempfile.mkdtemp(prefix=f"miiie_{owner}_{repo}_"))
        else:
            target_dir = Path(target_dir)
            target_dir.mkdir(parents=True, exist_ok=True)

        # Prepare git clone command
        clone_url = url
        if self.auth_token:
            # Use token for authentication
            if url.startswith("https://"):
                clone_url = url.replace("https://", f"https://{self.auth_token}@")
            elif url.startswith("http://"):
                clone_url = url.replace("http://", f"https://{self.auth_token}@")

        # Build git clone command
        cmd = ["git", "clone"]
        if self.shallow_depth is not None and self.shallow_depth > 0:
            cmd.extend(["--depth", str(self.shallow_depth)])
        cmd.extend([clone_url, str(target_dir)])

        # Execute git clone
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
            )
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to clone {url}\n"
            if e.stderr:
                error_msg += f"Git error: {e.stderr}"
            raise RuntimeError(error_msg)

        # Setup cleanup if requested
        if cleanup_after:
            import atexit

            atexit.register(self._cleanup_temp_dir, target_dir)

        return target_dir

    def _cleanup_temp_dir(self, temp_dir: Path) -> None:
        """Clean up temporary directory."""
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except Exception:
            pass  # Ignore cleanup errors
