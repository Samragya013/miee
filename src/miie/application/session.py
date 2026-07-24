"""Session Manager — CLI session lifecycle and workspace state.

The session manager tracks:
- Session context (current repo, config, output dir)
- Workspace state (cached results, history)
- Configuration state
- Session persistence for resume

Sessions are deterministic: given the same inputs, a session produces
the same state. This supports reproducible CLI workflows.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SessionContext:
    """Immutable snapshot of session context."""

    repo_path: Optional[str] = None
    output_dir: str = "./output"
    config_file: Optional[str] = None
    verbose: bool = False
    debug: bool = False
    forensic: bool = False
    seed: int = 42


@dataclass
class CachedResult:
    """A cached analysis result."""

    result_id: str
    repo_path: str
    timestamp: str
    data: Dict[str, Any]
    ttl_seconds: int = 3600

    @property
    def is_expired(self) -> bool:
        ts = datetime.fromisoformat(self.timestamp)
        age = (datetime.now(timezone.utc) - ts).total_seconds()
        return age > self.ttl_seconds


@dataclass
class Session:
    """A CLI session with state management.

    Attributes:
        session_id: Unique session identifier.
        context: Current session context.
        created_at: ISO 8601 creation timestamp.
        history: List of executed commands.
        cached_results: Map of result_id to cached results.
        workspace_dir: Session workspace directory.
    """

    session_id: str
    context: SessionContext
    created_at: str
    history: List[Dict[str, Any]] = field(default_factory=list)
    cached_results: Dict[str, CachedResult] = field(default_factory=dict)
    workspace_dir: Optional[str] = None


class SessionManager:
    """Manages CLI session lifecycle.

    Supports:
    - Session creation with context
    - Command history tracking
    - Result caching with TTL
    - Session persistence to disk
    - Session restoration from disk
    - Deterministic replay of command history

    The session manager is stateless between CLI invocations.
    Persistence is opt-in via save/load.
    """

    SESSION_DIR = Path.home() / ".miie" / "sessions"

    def __init__(self) -> None:
        self._current: Optional[Session] = None

    @property
    def current(self) -> Optional[Session]:
        return self._current

    def create(
        self,
        repo_path: Optional[str] = None,
        output_dir: str = "./output",
        config_file: Optional[str] = None,
        verbose: bool = False,
        debug: bool = False,
        forensic: bool = False,
        seed: int = 42,
    ) -> Session:
        """Create a new session with the given context."""
        context = SessionContext(
            repo_path=repo_path,
            output_dir=output_dir,
            config_file=config_file,
            verbose=verbose,
            debug=debug,
            forensic=forensic,
            seed=seed,
        )
        session = Session(
            session_id=uuid.uuid4().hex[:12],
            context=context,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._current = session
        return session

    def record_command(self, command: str, args: Optional[Dict[str, Any]] = None) -> None:
        """Record a command execution in the session history."""
        if self._current is None:
            return
        entry = {
            "command": command,
            "args": args or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._current.history.append(entry)

    def cache_result(self, result_id: str, data: Dict[str, Any], ttl_seconds: int = 3600) -> None:
        """Cache an analysis result with a TTL."""
        if self._current is None:
            return
        cached = CachedResult(
            result_id=result_id,
            repo_path=self._current.context.repo_path or "",
            timestamp=datetime.now(timezone.utc).isoformat(),
            data=data,
            ttl_seconds=ttl_seconds,
        )
        self._current.cached_results[result_id] = cached

    def get_cached(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Get a cached result if it exists and is not expired."""
        if self._current is None:
            return None
        cached = self._current.cached_results.get(result_id)
        if cached is None or cached.is_expired:
            return None
        return cached.data

    def save(self, path: Optional[Path] = None) -> Path:
        """Save the current session to disk."""
        if self._current is None:
            raise RuntimeError("No active session to save")

        if path is None:
            self.SESSION_DIR.mkdir(parents=True, exist_ok=True)
            path = self.SESSION_DIR / f"{self._current.session_id}.json"

        data = {
            "session_id": self._current.session_id,
            "context": {
                "repo_path": self._current.context.repo_path,
                "output_dir": self._current.context.output_dir,
                "config_file": self._current.context.config_file,
                "verbose": self._current.context.verbose,
                "debug": self._current.context.debug,
                "forensic": self._current.context.forensic,
                "seed": self._current.context.seed,
            },
            "created_at": self._current.created_at,
            "history": self._current.history,
            "workspace_dir": self._current.workspace_dir,
        }
        path.write_text(json.dumps(data, indent=2, sort_keys=True))
        return path

    def load(self, path: Path) -> Session:
        """Load a session from disk."""
        data = json.loads(path.read_text())
        context = SessionContext(
            repo_path=data["context"].get("repo_path"),
            output_dir=data["context"].get("output_dir", "./output"),
            config_file=data["context"].get("config_file"),
            verbose=data["context"].get("verbose", False),
            debug=data["context"].get("debug", False),
            forensic=data["context"].get("forensic", False),
            seed=data["context"].get("seed", 42),
        )
        session = Session(
            session_id=data["session_id"],
            context=context,
            created_at=data["created_at"],
            history=data.get("history", []),
            workspace_dir=data.get("workspace_dir"),
        )
        self._current = session
        return session

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all saved sessions."""
        if not self.SESSION_DIR.exists():
            return []
        sessions = []
        for p in self.SESSION_DIR.glob("*.json"):
            try:
                data = json.loads(p.read_text())
                sessions.append(
                    {
                        "session_id": data.get("session_id", p.stem),
                        "created_at": data.get("created_at", "unknown"),
                        "repo_path": data.get("context", {}).get("repo_path"),
                        "commands": len(data.get("history", [])),
                    }
                )
            except (json.JSONDecodeError, KeyError):
                continue
        return sorted(sessions, key=lambda s: s["created_at"], reverse=True)

    def clear(self) -> None:
        """Clear the current session."""
        self._current = None
