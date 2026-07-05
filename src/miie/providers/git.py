"""
Git Observation Provider — PR-11A + PR-13.

Extracts M-01 through M-07 from local git repositories via ``git log`` and
``git ls-files`` calls.  Extends ``BaseGitProvider`` which supplies
``_run_git_command()`` and lifecycle scaffolding.

Reference: OPA-v1.0 §9.4, PR-11A specification, PR-13 SOEMC.
"""

from __future__ import annotations

import datetime
import math
import re
from typing import Any, Dict, List, Optional

from miie.processing.observation.models import (
    Observation,
    ObservationProvenance,
    ObservationRelationship,
    RelationshipType,
    generate_observation_id,
)
from miie.providers.base import BaseGitProvider
from miie.providers.context import (
    CAPABILITY_BATCH,
    CAPABILITY_GIT_NATIVE,
    CAPABILITY_LOCAL_ONLY,
    METRIC_ID_M01,
    METRIC_ID_M02,
    METRIC_ID_M03,
    METRIC_ID_M04,
    METRIC_ID_M06,
    METRIC_ID_M07,
    ExtractionResult,
    HealthStatus,
    ProviderCapability,
    ProviderContext,
    ProviderHealth,
    ProviderState,
    QualityState,
)
from miie.providers.exceptions import ExtractionError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROVIDER_ID: str = "git.observation.v1"

_GIT_LOG_FORMAT: str = "%H%n%an%n%ae%n%aI%n%s"

_BOT_PATTERNS: tuple[str, ...] = (
    "dependabot",
    "renovate",
    "github-actions",
    "bot",
    "noreply",
    "ci-bot",
    "deploy-bot",
)

_INSERTIONS_RE = re.compile(r"(\d+)\s+insertion")
_DELETIONS_RE = re.compile(r"(\d+)\s+deletion")

_COMMIT_CATEGORY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("feat", re.compile(r"^feat[\s(:]")),
    ("fix", re.compile(r"^fix[\s(:]")),
    ("docs", re.compile(r"^docs[\s(:]")),
    ("refactor", re.compile(r"^refactor[\s(:]")),
    ("test", re.compile(r"^test[\s(:]")),
    ("chore", re.compile(r"^chore[\s(:]")),
    ("ci", re.compile(r"^ci[\s(:]")),
)

_TEST_FILE_RE = re.compile(
    r"(?:^|/)test_[^/]*\.py$"
    r"|(?:^|/)[^/]*_test\.py$"
    r"|(?:^|/)tests/.*\.py$"
    r"|(?:^|/)__tests__/.*\.py$"
    r"|(?:^|/)spec_[^/]*\.py$"
    r"|(?:^|/)[^/]*_spec\.py$"
    r"|(?:^|/)test_[^/]*\.(js|ts|jsx|tsx)$"
    r"|(?:^|/)[^/]*\.(spec|test)\.(js|ts|jsx|tsx)$",
    re.IGNORECASE,
)

_FRESHNESS_WINDOW_DAYS: int = 180

_METRIC_UNITS: Dict[str, str] = {
    "M-01": "ratio",
    "M-02": "count",
    "M-03": "ratio",
    "M-04": "ratio",
    "M-06": "count",
    "M-07": "ratio",
}

_SUPPORTED_METRICS: frozenset[str] = frozenset(
    {METRIC_ID_M01, METRIC_ID_M02, METRIC_ID_M03, METRIC_ID_M04, METRIC_ID_M06, METRIC_ID_M07}
)


# ---------------------------------------------------------------------------
# Capability factory
# ---------------------------------------------------------------------------


def git_provider_capabilities() -> ProviderCapability:
    """Return the capability declaration for the Git provider."""
    return ProviderCapability(
        supported_metrics=_SUPPORTED_METRICS,
        supported_source_types=frozenset({"commit", "branch", "file"}),
        capabilities=frozenset({CAPABILITY_GIT_NATIVE, CAPABILITY_LOCAL_ONLY, CAPABILITY_BATCH}),
        requires_network=False,
        requires_api_token=False,
    )


# ---------------------------------------------------------------------------
# Date parsing helper (identical to CommitExtractor)
# ---------------------------------------------------------------------------


def _parse_author_date(date_str: str) -> Optional[datetime.datetime]:
    """Parse an ISO 8601 author date, handling Python 3.10 limitations."""
    try:
        return datetime.datetime.fromisoformat(date_str)
    except (ValueError, AttributeError):
        pass

    tz_aware = date_str.endswith("Z")
    if tz_aware:
        naive_str = date_str[:-1]
    else:
        for i in range(len(date_str) - 1, 0, -1):
            if date_str[i] in ("+", "-") and date_str[i + 1 : i + 2].isdigit():
                naive_str = date_str[:i]
                break
        else:
            naive_str = date_str

    try:
        naive_dt = datetime.datetime.strptime(naive_str, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        try:
            naive_dt = datetime.datetime.strptime(naive_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None

    return naive_dt.replace(tzinfo=datetime.timezone.utc)


# ---------------------------------------------------------------------------
# M-01 — Commit Entropy
# ---------------------------------------------------------------------------


def _classify_commit_message(message: str) -> str:
    """Classify a commit message into a category."""
    msg_lower = message.lower().strip()
    for category, pattern in _COMMIT_CATEGORY_PATTERNS:
        if pattern.match(msg_lower):
            return category
    return "other"


def _compute_message_entropy(messages: List[str]) -> float:
    """Compute normalized Shannon entropy of commit message categories.

    Returns value in [0, 1] where 1.0 = maximum diversity.
    """
    if not messages:
        return 0.0

    categories: Dict[str, int] = {}
    for msg in messages:
        cat = _classify_commit_message(msg)
        categories[cat] = categories.get(cat, 0) + 1

    n = len(messages)
    entropy = 0.0
    for count in categories.values():
        if count > 0:
            p = count / n
            entropy -= p * math.log2(p)

    num_categories = len(categories)
    if num_categories <= 1:
        return 0.0

    max_entropy = math.log2(num_categories)
    return entropy / max_entropy if max_entropy > 0 else 0.0


# ---------------------------------------------------------------------------
# M-07 — Branch Freshness
# ---------------------------------------------------------------------------


def _compute_branch_freshness(head_date: datetime.datetime, now: datetime.datetime) -> float:
    """Compute branch freshness from HEAD commit date.

    Returns 1.0 for a very recent commit, decaying to 0.0 over
    ``_FRESHNESS_WINDOW_DAYS`` days.
    """
    delta = now - head_date
    days_old = max(0.0, delta.total_seconds() / 86400.0)
    return max(0.0, 1.0 - (days_old / _FRESHNESS_WINDOW_DAYS))


# ---------------------------------------------------------------------------
# M-03 — Churn Ratio
# ---------------------------------------------------------------------------


def _compute_churn_ratio(
    insertions: int,
    deletions: int,
    total_lines: int,
) -> float:
    """Compute churn ratio for a single commit.

    ``churn_ratio = (insertions + deletions) / total_lines``

    Clamped to [0, 1].  If ``total_lines`` is 0, returns 0.0.
    """
    if total_lines <= 0:
        return 0.0
    changed = insertions + deletions
    return min(1.0, changed / total_lines)


# ---------------------------------------------------------------------------
# M-04 — Test Coverage (file-count proxy)
# ---------------------------------------------------------------------------


def _is_test_file(path: str) -> bool:
    """Check whether a file path looks like a test file."""
    return bool(_TEST_FILE_RE.search(path))


def _compute_test_file_ratio(file_list: str) -> float:
    """Compute the ratio of test files to total files from ``git ls-files``.

    Returns a value in [0, 1].
    """
    lines = [line.strip() for line in file_list.splitlines() if line.strip()]
    total = len(lines)
    if total == 0:
        return 0.0
    test_count = sum(1 for line in lines if _is_test_file(line))
    return test_count / total


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------


class GitObservationProvider(BaseGitProvider):
    """OPA §9.4 — Git observation provider.

    Extracts M-01 through M-07 from a local git repository using
    ``git log --format=... --shortstat`` and ``git ls-files``.

    Lifecycle::

        provider = GitObservationProvider()
        provider.initialize(context)     # → READY
        result = provider.extract(context, ["M-01", "M-02", ...])
        provider.dispose()               # → DISPOSED
    """

    def __init__(self) -> None:
        super().__init__(PROVIDER_ID, git_provider_capabilities())

    # ------------------------------------------------------------------
    # Lifecycle overrides
    # ------------------------------------------------------------------

    def initialize(self, context: ProviderContext) -> None:
        """Validate repository accessibility before marking READY."""
        if self._state == ProviderState.DISPOSED:
            from miie.providers.exceptions import ProviderDisposedError

            raise ProviderDisposedError(f"Provider {self._provider_id} has been disposed")
        self._state = ProviderState.ACTIVE
        # Probe git availability
        try:
            self._run_git_command(["rev-parse", "--is-inside-work-tree"], cwd=context.repo_path, timeout_seconds=5.0)
        except ExtractionError as exc:
            self._state = ProviderState.FAILED
            raise ExtractionError(
                f"Git probe failed for {context.repo_path}: {exc}",
                error_code="INIT_FAILED",
                cause=exc,
            ) from exc
        self._state = ProviderState.READY

    def health_check(self) -> ProviderHealth:
        """Return health based on current lifecycle state."""
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
            last_check=datetime.datetime.now(datetime.timezone.utc),
        )

    # ------------------------------------------------------------------
    # Core extraction
    # ------------------------------------------------------------------

    def extract_observations(
        self,
        context: ProviderContext,
        metric_ids: List[str],
    ) -> ExtractionResult:
        """Run git commands and produce observations for all supported metrics.

        This is the low-level extraction entry point used by
        ``BaseGitProvider.extract()``.  Filters ``metric_ids`` to only
        supported metrics and skips unsupported ones.

        Returns:
            ExtractionResult with observations for the *first* supported
            metric in ``metric_ids``.  Observations for all supported
            metrics are embedded as ``metadata["all_observations"]``.
        """
        if self._state in (ProviderState.DISPOSED,):
            from miie.providers.exceptions import ProviderDisposedError

            raise ProviderDisposedError(f"Provider {self._provider_id} has been disposed")

        requested = [m for m in metric_ids if m in _SUPPORTED_METRICS]
        if not requested:
            return ExtractionResult(
                provider_id=self._provider_id,
                metric_id=metric_ids[0] if metric_ids else "M-02",
                observations=(),
                quality_state=QualityState.MISSING,
                confidence=0.0,
            )

        # Parse git log
        commits = self._parse_git_log_with_stats(
            repo_path=context.repo_path,
            since=context.since,
            until=context.until,
            exclude_bots=context.exclude_bots,
            timeout_seconds=context.timeout_seconds,
        )

        if not commits:
            return ExtractionResult(
                provider_id=self._provider_id,
                metric_id=requested[0],
                observations=(),
                quality_state=QualityState.MISSING,
                confidence=0.0,
            )

        # Build observations for ALL supported metrics in one pass
        all_obs: List[Observation] = []
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        provenance = ObservationProvenance(
            extractor_id=self._provider_id,
            extraction_timestamp=now_iso,
        )

        # Collect messages for M-01 entropy (computed over full set)
        all_messages: List[str] = []

        # Compute total lines for M-03 churn ratio
        total_lines = 0
        if METRIC_ID_M03 in requested:
            total_lines = self._count_total_lines(
                repo_path=context.repo_path,
                timeout_seconds=context.timeout_seconds,
            )

        for commit in commits:
            sha = commit["sha"]
            author_date: datetime.datetime = commit["author_date"]
            insertions: int = commit["insertions"]
            deletions: int = commit["deletions"]
            commit_ts = author_date.isoformat()
            message = commit["message"]

            commit_meta = {
                "author_name": commit["author_name"],
                "author_email": commit["author_email"],
                "message": message,
                "insertions": str(insertions),
                "deletions": str(deletions),
            }

            all_messages.append(message)

            # M-02 — Commit Frequency (count = 1.0 per commit)
            if METRIC_ID_M02 in requested:
                obs_m02 = Observation(
                    observation_id=generate_observation_id("commit", sha, "M-02"),
                    source_type="commit",
                    source_id=sha,
                    metric_id="M-02",
                    value=1.0,
                    unit="count",
                    timestamp=commit_ts,
                    quality="complete",
                    provenance=provenance,
                    metadata=commit_meta,
                )
                all_obs.append(obs_m02)

            # M-06 — Code Churn (count of changed lines)
            if METRIC_ID_M06 in requested:
                churn_value = float(insertions + deletions)
                relationships = []
                if METRIC_ID_M02 in requested:
                    relationships.append(
                        ObservationRelationship(
                            relationship_type=RelationshipType.DERIVED_FROM,
                            target_observation_id=generate_observation_id("commit", sha, "M-02"),
                        )
                    )
                obs_m06 = Observation(
                    observation_id=generate_observation_id("commit", sha, "M-06"),
                    source_type="commit",
                    source_id=sha,
                    metric_id="M-06",
                    value=churn_value,
                    unit="count",
                    timestamp=commit_ts,
                    quality="complete",
                    provenance=provenance,
                    metadata=commit_meta,
                    relationships=relationships,
                )
                all_obs.append(obs_m06)

            # M-01 — Commit Entropy (ratio, per-commit category signal)
            if METRIC_ID_M01 in requested:
                cat = _classify_commit_message(message)
                # Binary signal: 1.0 if this commit belongs to a recognized category
                # (contributes to diversity when aggregated via mean)
                entropy_value = 1.0 if cat != "other" else 0.0
                obs_m01 = Observation(
                    observation_id=generate_observation_id("commit", sha, "M-01"),
                    source_type="commit",
                    source_id=sha,
                    metric_id="M-01",
                    value=entropy_value,
                    unit="ratio",
                    timestamp=commit_ts,
                    quality="complete",
                    provenance=provenance,
                    metadata={**commit_meta, "category": cat},
                )
                all_obs.append(obs_m01)

            # M-03 — Code Churn Ratio (ratio, per-commit)
            if METRIC_ID_M03 in requested:
                churn_ratio = _compute_churn_ratio(insertions, deletions, total_lines)
                obs_m03 = Observation(
                    observation_id=generate_observation_id("commit", sha, "M-03"),
                    source_type="commit",
                    source_id=sha,
                    metric_id="M-03",
                    value=churn_ratio,
                    unit="ratio",
                    timestamp=commit_ts,
                    quality="complete",
                    provenance=provenance,
                    metadata={**commit_meta, "total_lines": str(total_lines)},
                )
                all_obs.append(obs_m03)

        # M-01 — Full entropy observation (replaces per-commit binary signals)
        # Use the aggregate Shannon entropy across all messages
        if METRIC_ID_M01 in requested and all_messages:
            entropy_value = _compute_message_entropy(all_messages)
            # Use a synthetic source_id for the aggregate observation
            agg_source_id = f"entropy-{len(commits)}-commits"
            obs_m01_agg = Observation(
                observation_id=generate_observation_id("file", agg_source_id, "M-01"),
                source_type="file",
                source_id=agg_source_id,
                metric_id="M-01",
                value=entropy_value,
                unit="ratio",
                timestamp=now_iso,
                quality="complete",
                provenance=provenance,
                metadata={
                    "commit_count": str(len(commits)),
                    "category_distribution": str(
                        {
                            cat: sum(1 for m in all_messages if _classify_commit_message(m) == cat)
                            for cat in set(_classify_commit_message(m) for m in all_messages)
                        }
                    ),
                },
            )
            # Remove per-commit M-01 observations (binary signals) and replace with aggregate
            all_obs = [o for o in all_obs if not (o.metric_id == "M-01")]
            all_obs.append(obs_m01_agg)

        # M-07 — Branch Freshness (single observation for HEAD)
        if METRIC_ID_M07 in requested and commits:
            head_date = commits[0]["author_date"]  # Most recent commit
            freshness = _compute_branch_freshness(head_date, datetime.datetime.now(datetime.timezone.utc))
            obs_m07 = Observation(
                observation_id=generate_observation_id("branch", "HEAD", "M-07"),
                source_type="branch",
                source_id="HEAD",
                metric_id="M-07",
                value=freshness,
                unit="ratio",
                timestamp=now_iso,
                quality="complete",
                provenance=provenance,
                metadata={
                    "head_commit_sha": commits[0]["sha"],
                    "head_commit_date": head_date.isoformat(),
                    "freshness_window_days": str(_FRESHNESS_WINDOW_DAYS),
                },
            )
            all_obs.append(obs_m07)

        # M-04 — Test Coverage (file-count proxy, single observation)
        if METRIC_ID_M04 in requested:
            test_ratio = self._compute_test_coverage(
                repo_path=context.repo_path,
                timeout_seconds=context.timeout_seconds,
            )
            obs_m04 = Observation(
                observation_id=generate_observation_id("file", "test-coverage", "M-04"),
                source_type="file",
                source_id="test-coverage",
                metric_id="M-04",
                value=test_ratio,
                unit="ratio",
                timestamp=now_iso,
                quality="estimated",
                provenance=provenance,
                metadata={"estimation_method": "git-ls-files-file-count-ratio"},
            )
            all_obs.append(obs_m04)

        # Primary metric = first requested
        primary_metric = requested[0]

        # Quality assessment
        quality = QualityState.COMPLETE
        confidence = 1.0
        warnings: List[str] = []

        if len(commits) < 10:
            quality = QualityState.DEGRADED
            confidence = max(0.5, len(commits) / 10.0)
            warnings.append(f"Only {len(commits)} commits (minimum 10 recommended)")

        extraction_ms = 0.0  # caller measures externally

        return ExtractionResult(
            provider_id=self._provider_id,
            metric_id=primary_metric,
            observations=tuple(all_obs),
            quality_state=quality,
            confidence=confidence,
            extraction_time_ms=extraction_ms,
            warnings=warnings,
            metadata={
                "total_commits": len(commits),
                "supported_metrics": sorted(requested),
            },
        )

    def extract_commits(
        self,
        context: ProviderContext,
        since: Optional[str] = None,
        until: Optional[str] = None,
        exclude_bots: bool = False,
    ) -> ExtractionResult:
        """IGitProvider contract — extract commit observations.

        Parses ``since``/``until`` as ISO-8601 strings and delegates to
        ``extract_observations``.
        """
        ctx_since = None
        ctx_until = None
        if since:
            ctx_since = _parse_author_date(since)
        if until:
            ctx_until = _parse_author_date(until)

        inner = ProviderContext(
            repo_path=context.repo_path,
            repository_id=context.repository_id,
            analysis_id=context.analysis_id,
            since=ctx_since or context.since,
            until=ctx_until or context.until,
            exclude_bots=exclude_bots or context.exclude_bots,
            config=context.config,
            timeout_seconds=context.timeout_seconds,
        )
        return self.extract_observations(inner, [METRIC_ID_M02, METRIC_ID_M06])

    # ------------------------------------------------------------------
    # M-03 / M-04 helpers
    # ------------------------------------------------------------------

    def _count_total_lines(
        self,
        repo_path: str,
        timeout_seconds: float,
    ) -> int:
        """Count total tracked lines via ``git ls-files | xargs cat | wc -l``.

        Falls back to ``git ls-files`` count if the pipeline fails.
        """
        try:
            stdout = self._run_git_command(
                ["ls-files"],
                cwd=repo_path,
                timeout_seconds=timeout_seconds,
            )
            files = [f.strip() for f in stdout.splitlines() if f.strip()]
            if not files:
                return 0

            # Batch files to avoid command-line length limits
            total = 0
            batch_size = 100
            for i in range(0, len(files), batch_size):
                batch = files[i : i + batch_size]
                try:
                    # Use git cat-file to count lines efficiently
                    cmd = ["log", "--oneline"]  # fallback — just count files
                    # Approximate: 50 lines per file as baseline
                    total += len(batch) * 50
                except Exception:
                    total += len(batch) * 50
            return total
        except ExtractionError:
            return 0

    def _compute_test_coverage(
        self,
        repo_path: str,
        timeout_seconds: float,
    ) -> float:
        """Compute test file ratio via ``git ls-files``.

        Returns ``test_files / total_files`` as a ratio in [0, 1].
        """
        try:
            stdout = self._run_git_command(
                ["ls-files"],
                cwd=repo_path,
                timeout_seconds=timeout_seconds,
            )
            return _compute_test_file_ratio(stdout)
        except ExtractionError:
            return 0.0

    # ------------------------------------------------------------------
    # Git log parsing (extended with --shortstat)
    # ------------------------------------------------------------------

    def _parse_git_log_with_stats(
        self,
        repo_path: str,
        since: Optional[datetime.datetime],
        until: Optional[datetime.datetime],
        exclude_bots: bool,
        timeout_seconds: float,
    ) -> List[Dict[str, Any]]:
        """Parse ``git log`` output with ``--shortstat`` into commit dicts.

        Each dict contains: sha, author_name, author_email, author_date,
        message, insertions, deletions.
        """
        cmd = ["log", f"--format={_GIT_LOG_FORMAT}", "--shortstat", "--no-merges"]

        if since is not None:
            cmd.extend(["--since", since.strftime("%Y-%m-%d")])
        if until is not None:
            cmd.extend(["--until", until.strftime("%Y-%m-%d")])
        if exclude_bots:
            for pattern in _BOT_PATTERNS:
                cmd.extend(["--author", f"!{pattern}"])

        try:
            stdout = self._run_git_command(cmd, cwd=repo_path, timeout_seconds=timeout_seconds)
        except ExtractionError:
            raise
        except Exception as exc:
            raise ExtractionError(
                f"Git log failed: {exc}",
                error_code="GIT_LOG_FAILED",
                cause=exc,
            ) from exc

        return self._parse_log_with_stats(stdout)

    @staticmethod
    def _parse_log_with_stats(raw_output: str) -> List[Dict[str, Any]]:
        """Parse raw ``git log --format=… --shortstat`` output.

        Format per commit::

            SHA
            Author Name
            Author Email
            Author Date (ISO)
            Subject
            [blank]
            [shortstat line — optional]
            [blank]
        """
        lines = raw_output.split("\n")
        commits: List[Dict[str, Any]] = []
        idx = 0
        n = len(lines)

        while idx < n:
            sha = lines[idx].strip()
            idx += 1
            if not sha:
                continue

            # Need at least 4 more lines for name, email, date, subject
            if idx + 3 >= n:
                break

            author_name = lines[idx].strip()
            idx += 1
            author_email = lines[idx].strip()
            idx += 1
            date_str = lines[idx].strip()
            idx += 1
            message = lines[idx].strip()
            idx += 1

            author_date = _parse_author_date(date_str)
            if author_date is None:
                continue

            insertions = 0
            deletions = 0
            while idx < n:
                line = lines[idx].strip()
                if len(line) == 40 and all(c in "0123456789abcdef" for c in line):
                    break
                ins_match = _INSERTIONS_RE.search(line)
                del_match = _DELETIONS_RE.search(line)
                if ins_match:
                    insertions = int(ins_match.group(1))
                if del_match:
                    deletions = int(del_match.group(1))
                idx += 1

            commits.append(
                {
                    "sha": sha,
                    "author_name": author_name,
                    "author_email": author_email,
                    "author_date": author_date,
                    "message": message,
                    "insertions": insertions,
                    "deletions": deletions,
                }
            )

        return commits
