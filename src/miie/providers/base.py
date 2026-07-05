"""
MIIE v1.6 Observation Provider Framework — Base provider abstractions.

Provides common base classes, mixins, and lifecycle management shared
across all observation providers. Implements OPA §9.3 and OPA §11.
"""

from __future__ import annotations

import logging
import subprocess
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from miie.providers.context import (
    ExtractionResult,
    HealthStatus,
    ProviderCapability,
    ProviderContext,
    ProviderHealth,
    ProviderState,
)
from miie.providers.exceptions import (
    ExtractionError,
    ProviderDisposedError,
    ProviderNotInitializedError,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mixin — ProviderMixin (OPA §11.2)
# ---------------------------------------------------------------------------


class ProviderMixin:
    """OPA §11.2 — Common utility methods for providers.

    Provides timing instrumentation and error-handling context managers
    that concrete provider implementations can use internally.
    """

    @contextmanager  # type: ignore[misc]
    def timing_context(self, operation: str = "operation"):  # type: ignore[type-arg]
        """Context manager that measures wall-clock duration of a block.

        Args:
            operation: Human-readable name for the timed operation.

        Yields:
            Dict that will be populated with timing metadata on exit.

        Example::

            with self.timing_context("extract_commits") as timer:
                result = self._run_git(...)
            print(timer["elapsed_ms"])
        """
        timer: Dict[str, Any] = {"operation": operation, "elapsed_ms": 0.0}
        start = time.monotonic()
        try:
            yield timer
        finally:
            elapsed = (time.monotonic() - start) * 1000.0
            timer["elapsed_ms"] = round(elapsed, 3)

    @contextmanager  # type: ignore[misc]
    def error_handler(  # type: ignore[type-arg]
        self,
        provider_id: str,
        metric_id: str = "",
        phase: str = "extract",
    ):
        """Context manager that wraps a block with structured error handling.

        Catches exceptions, logs them, and re-raises as provider-specific
        error types when appropriate.

        Args:
            provider_id: ID of the provider for error context.
            metric_id: Metric being processed, if applicable.
            phase: Extraction phase (health_check, extract, transform).

        Yields:
            None.

        Raises:
            ExtractionError: On any caught exception.
        """
        try:
            yield
        except (ProviderNotInitializedError, ProviderDisposedError):
            raise
        except subprocess.TimeoutExpired as exc:
            logger.error(
                "Provider %s timed out during %s (metric=%s)",
                provider_id,
                phase,
                metric_id,
            )
            raise ExtractionError(
                f"Provider {provider_id} timed out during {phase}",
                error_code="TIMEOUT",
                cause=exc,
            ) from exc
        except subprocess.CalledProcessError as exc:
            logger.error(
                "Provider %s command failed during %s (metric=%s, rc=%s)",
                provider_id,
                phase,
                metric_id,
                exc.returncode,
            )
            raise ExtractionError(
                f"Provider {provider_id} command failed during {phase}: " f"exit code {exc.returncode}",
                error_code="COMMAND_FAILED",
                cause=exc,
            ) from exc
        except Exception as exc:
            logger.error(
                "Provider %s failed during %s (metric=%s): %s",
                provider_id,
                phase,
                metric_id,
                exc,
            )
            raise ExtractionError(
                f"Provider {provider_id} failed during {phase}: {exc}",
                error_code="EXTRACTION_FAILED",
                cause=exc,
            ) from exc


# ---------------------------------------------------------------------------
# ABC — BaseObservationProvider (OPA §9.3)
# ---------------------------------------------------------------------------


class BaseObservationProvider(ABC, ProviderMixin):
    """OPA §9.3 — Abstract base for all observation providers.

    Manages provider lifecycle (state transitions), capability queries,
    and defines the extraction interface that concrete providers must
    implement.
    """

    def __init__(self, provider_id: str, capabilities: ProviderCapability) -> None:
        if not provider_id:
            raise ValueError("provider_id must not be empty")
        self._provider_id = provider_id
        self._capabilities = capabilities
        self._state = ProviderState.UNINITIALIZED

    # -- Properties ---------------------------------------------------------

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        return self._provider_id

    @property
    def state(self) -> ProviderState:
        """Current lifecycle state of the provider."""
        return self._state

    # -- Capability queries -------------------------------------------------

    def supports_metric(self, metric_id: str) -> bool:
        """Check if this provider supports the given metric."""
        return self._capabilities.supports_metric(metric_id)

    def get_capabilities(self) -> ProviderCapability:
        """Get the full capability declaration for this provider."""
        return self._capabilities

    # -- Lifecycle ----------------------------------------------------------

    def initialize(self, context: ProviderContext) -> None:
        """Transition to READY state.

        Override in subclasses to perform provider-specific initialization
        (e.g. validating the repo path, checking git availability).

        Args:
            context: Extraction context providing repo path and config.

        Raises:
            ProviderError: If initialization fails.
        """
        if self._state == ProviderState.DISPOSED:
            raise ProviderDisposedError(f"Provider {self._provider_id} has been disposed")
        self._state = ProviderState.READY
        logger.info("Provider %s initialized", self._provider_id)

    def health_check(self) -> ProviderHealth:
        """Return current health snapshot.

        Override in subclasses for deeper health probes (e.g. running
        a test git command).
        """
        status_map = {
            ProviderState.READY: HealthStatus.HEALTHY,
            ProviderState.ACTIVE: HealthStatus.HEALTHY,
            ProviderState.DEGRADED: HealthStatus.DEGRADED,
            ProviderState.FAILED: HealthStatus.UNHEALTHY,
        }
        status = status_map.get(self._state, HealthStatus.UNKNOWN)
        return ProviderHealth(
            status=status,
            health_score=1.0 if status == HealthStatus.HEALTHY else 0.5,
            last_check=datetime.now(timezone.utc),
        )

    def dispose(self) -> None:
        """Transition to DISPOSED state and release resources.

        Override in subclasses to close file handles, connections, etc.
        """
        self._state = ProviderState.DISPOSED
        logger.info("Provider %s disposed", self._provider_id)

    # -- Abstract -----------------------------------------------------------

    @abstractmethod
    def extract(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        """Extract observations for the requested metrics.

        Args:
            context: Extraction context with repo path, time bounds, config.
            metric_ids: Which metrics to extract.

        Returns:
            ExtractionResult with observations and quality metadata.
        """
        ...


# ---------------------------------------------------------------------------
# ABC — BaseGitProvider (OPA §9.4)
# ---------------------------------------------------------------------------


class BaseGitProvider(BaseObservationProvider):
    """OPA §9.4 — Abstract base for Git-based observation providers.

    Adds git-specific utilities: command execution and log parsing.
    Subclasses implement specific metric extraction logic.
    """

    def _run_git_command(
        self,
        args: List[str],
        cwd: str,
        timeout_seconds: float = 30.0,
    ) -> str:
        """Execute a git command and return its stdout.

        Args:
            args: Git subcommand and arguments (e.g. ["log", "--oneline"]).
            cwd: Working directory (repository root).
            timeout_seconds: Maximum seconds before timeout.

        Returns:
            Decoded stdout string (UTF-8).

        Raises:
            ExtractionError: On timeout or non-zero exit.
        """
        cmd = ["git"] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",  # Replace invalid UTF-8 with ?
                timeout=timeout_seconds,
                check=True,
            )
            return result.stdout
        except subprocess.TimeoutExpired as exc:
            raise ExtractionError(
                f"Git command timed out: {' '.join(cmd)}",
                error_code="GIT_TIMEOUT",
                cause=exc,
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise ExtractionError(
                f"Git command failed (rc={exc.returncode}): {' '.join(cmd)}\n" f"stderr: {exc.stderr.strip()}",
                error_code="GIT_COMMAND_FAILED",
                cause=exc,
            ) from exc

    @staticmethod
    def _parse_git_log(output: str) -> List[Dict[str, str]]:
        """Parse ``git log`` output into structured commit records.

        Expects the default format produced by ``git log --format`` with
        hash, author, date, and subject fields separated by newlines.

        Args:
            output: Raw stdout from a git log command.

        Returns:
            List of dicts, each with keys: hash, author, date, subject.
            Empty lines in the output are skipped.
        """
        commits: List[Dict[str, str]] = []
        current: Optional[Dict[str, str]] = None

        for line in output.splitlines():
            stripped = line.strip()
            if not stripped:
                if current is not None:
                    commits.append(current)
                    current = None
                continue

            if current is None:
                current = {"hash": stripped, "author": "", "date": "", "subject": ""}
            elif not current["author"]:
                current["author"] = stripped
            elif not current["date"]:
                current["date"] = stripped
            elif not current["subject"]:
                current["subject"] = stripped

        if current is not None:
            commits.append(current)

        return commits

    def extract(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        """Delegate to extract_observations.

        Subclasses must implement extract_observations to provide
        metric-specific logic.
        """
        return self.extract_observations(context, metric_ids)

    @abstractmethod
    def extract_observations(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        """Extract observations for the requested metrics.

        Args:
            context: Extraction context with repo path and time bounds.
            metric_ids: Which metrics to extract.

        Returns:
            ExtractionResult with observations and quality metadata.
        """
        ...
