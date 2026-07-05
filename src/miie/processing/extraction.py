"""
Metric Extraction Engine for MIIE v1.0 (DEPRECATED).

.. deprecated::
    This module is deprecated. Use ``miie.processing.extraction`` package
    instead::

        from miie.processing.extraction import ExtractionEngine

The ``ExtractionEngine`` orchestrates ``GitObservationProvider`` and
``MetricExtractor`` to produce ``ObservationCollection`` and
``MetricDataFrame`` in a single pass.

The legacy ``MetricExtractionEngine`` class below is retained for
backward compatibility with existing tests and CLI commands.
It delegates M-02 / M-06 extraction to ``ExtractionEngine`` (which
uses ``GitObservationProvider``) and handles other metrics directly
from external data sources.
"""

import warnings as _warnings

_warnings.warn(
    "miie.processing.extraction (module) is deprecated. " "Use miie.processing.extraction.ExtractionEngine instead.",
    DeprecationWarning,
    stacklevel=2,
)

import datetime
import json
import subprocess
import uuid
from pathlib import Path
from typing import Any, List, Optional
from xml.etree import ElementTree

from miie.contracts.errors import ExtractionError
from miie.contracts.interfaces import IExtractionEngine
from miie.schemas.models import MetricDataFrame, RepositoryContext


def validate_metric_ids(metric_list: List[str]) -> None:
    """
    Validate that all metric IDs are in the frozen registry.

    Args:
        metric_list: List of metric IDs to validate

    Raises:
        ExtractionError: If any metric ID is not in the frozen registry
    """
    try:
        from miie.schemas.metric_registry import (
            validate_metric_ids as schema_validate_metric_ids,
        )

        schema_validate_metric_ids(metric_list)
    except ValueError as e:
        raise ExtractionError(str(e))


# Metrics that are now extracted via GitObservationProvider / ExtractionEngine
# Metrics available from GitObservationProvider (git-native, no external data needed)
_PROVIDER_METRICS = frozenset({"M-01", "M-02", "M-03", "M-04", "M-06", "M-07"})


class MetricExtractionEngine(IExtractionEngine):
    """INT-02: Metric Extraction Engine (legacy wrapper).

    Delegates M-02 (Commit Frequency) and M-06 (Code Churn) to the
    new ``ExtractionEngine`` backed by ``GitObservationProvider``.
    Handles M-01, M-03, M-04, M-05, M-07 directly from external data
    sources (coverage reports, PR/issue exports, static analysis).
    """

    def __init__(
        self,
        pr_export_path: Optional[Path] = None,
        issue_export_path: Optional[Path] = None,
    ):
        """
        Initialize the extraction engine with optional external data paths.

        Args:
            pr_export_path: Path to PR/MR export JSON for M-03/M-04
            issue_export_path: Path to issue export JSON for M-05
        """
        self._pr_export_path = pr_export_path
        self._issue_export_path = issue_export_path
        # Lazy-created ExtractionEngine for provider-backed metrics
        self._engine: Optional[Any] = None

    def _get_engine(self) -> Any:
        """Return or create the ExtractionEngine for provider-backed metrics."""
        if self._engine is None:
            from miie.processing.extraction.engine import ExtractionEngine

            self._engine = ExtractionEngine()
        return self._engine

    def extract(
        self,
        context: RepositoryContext,
        metric_list: List[str],
        since: Optional[datetime.datetime] = None,
        until: Optional[datetime.datetime] = None,
        exclude_bots: bool = False,
        windows: Optional[List[Any]] = None,
    ) -> MetricDataFrame:
        """
        Extract metrics from repository.

        M-02 and M-06 are delegated to ExtractionEngine (backed by
        GitObservationProvider).  All other metrics are extracted
        directly from external data sources.

        Args:
            context: Repository context from ingestion
            metric_list: List of metric IDs to extract (e.g., ["M-01", "M-06"])
            since: Extract metrics since this timestamp (inclusive)
            until: Extract metrics until this timestamp (inclusive)
            exclude_bots: Whether to exclude bot-generated commits
            windows: Optional list of WindowDefinition objects for per-window extraction

        Returns:
            MetricDataFrame: Container for extracted metrics

        Raises:
            ExtractionError: If extraction fails or validation fails
        """
        # Validate metric IDs against frozen registry
        validate_metric_ids(metric_list)

        # Generate unique run ID
        run_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now(datetime.timezone.utc)

        # Split metrics: provider-backed vs externally-sourced
        provider_metrics = [m for m in metric_list if m in _PROVIDER_METRICS]
        external_metrics = [m for m in metric_list if m not in _PROVIDER_METRICS]

        # Initialize metrics dictionary
        metrics = {}

        # --- Phase 1: Provider-backed metrics (M-01-M-04, M-06-M-07: git-native) ---
        if provider_metrics:
            try:
                engine = self._get_engine()
                _collection, mdf = engine.extract(
                    context,
                    provider_metrics,
                    since=since,
                    until=until,
                    exclude_bots=exclude_bots,
                )
                metrics.update(mdf.metrics)
            except Exception as exc:
                # Fallback: mark provider metrics as unavailable
                for metric_id in provider_metrics:
                    metrics[metric_id] = None

        # --- Phase 2: Externally-sourced metrics (M-05 requires PR/issue data) ---
        for metric_id in external_metrics:
            if metric_id == "M-01":
                metrics[metric_id] = self._extract_code_coverage(context)
            elif metric_id == "M-03":
                metrics[metric_id] = self._extract_review_participation()
            elif metric_id == "M-04":
                metrics[metric_id] = self._extract_review_latency()
            elif metric_id == "M-05":
                metrics[metric_id] = self._extract_issue_resolution_time()
            elif metric_id == "M-07":
                metrics[metric_id] = self._extract_cyclomatic_complexity(context)
            else:
                # Unavailable metrics - return None per missing data policy
                metrics[metric_id] = None

        # Create and return MetricDataFrame
        try:
            return MetricDataFrame(
                repo_id=context.repo_id,
                run_id=run_id,
                timestamp=timestamp,
                metrics=metrics,
            )
        except ValueError as e:
            raise ExtractionError(f"Invalid MetricDataFrame: {e}")

    # ------------------------------------------------------------------
    # External data source extractors (M-01, M-03-M-05, M-07)
    # ------------------------------------------------------------------

    def _extract_code_coverage(
        self,
        context: RepositoryContext,
    ) -> Optional[dict]:
        """
        Extract Code Coverage (M-01) from coverage artifacts.

        Parses coverage.xml (Cobertura), lcov.info, or .coverage (JSON).
        Returns value in range [0, 100]%.
        """
        try:
            repo_path = context.local_path
            coverage_value = None

            # Try coverage.xml (Cobertura format)
            coverage_xml = repo_path / "coverage.xml"
            if coverage_xml.exists():
                coverage_value = self._parse_cobertura_xml(coverage_xml)

            # Try lcov.info
            if coverage_value is None:
                lcov_files = list(repo_path.rglob("lcov.info"))
                if lcov_files:
                    coverage_value = self._parse_lcov(lcov_files[0])

            # Try .coverage (JSON)
            if coverage_value is None:
                dot_coverage = repo_path / ".coverage"
                if dot_coverage.exists():
                    coverage_value = self._parse_dot_coverage(dot_coverage)

            if coverage_value is not None:
                return {"w00": [coverage_value]}
            return None

        except Exception:
            return None

    @staticmethod
    def _parse_cobertura_xml(xml_path: Path) -> Optional[float]:
        """Parse Cobertura XML and return line-rate as percentage."""
        try:
            if not xml_path.exists():
                return None
            tree = ElementTree.parse(xml_path)
            root = tree.getroot()
            line_rate = root.get("line-rate")
            if line_rate is not None:
                return float(line_rate) * 100.0
            return None
        except (ElementTree.ParseError, ValueError, TypeError):
            return None

    @staticmethod
    def _parse_lcov(lcov_path: Path) -> Optional[float]:
        """Parse lcov.info and return coverage percentage."""
        try:
            if not lcov_path.exists():
                return None
            lines_hit = 0
            lines_found = 0
            with open(lcov_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("LH:"):
                        lines_hit = int(line[3:])
                    elif line.startswith("LF:"):
                        lines_found = int(line[3:])
            if lines_found > 0:
                return (lines_hit / lines_found) * 100.0
            return None
        except (ValueError, IOError):
            return None

    @staticmethod
    def _parse_dot_coverage(coverage_path: Path) -> Optional[float]:
        """Parse .coverage JSON and return coverage percentage."""
        try:
            if not coverage_path.exists():
                return None
            with open(coverage_path, "r") as f:
                data = json.load(f)
            # Support common .coverage JSON formats
            if "totals" in data and "percent_covered" in data["totals"]:
                return float(data["totals"]["percent_covered"])
            if "coverage" in data:
                # Flat dict of filename -> list of coverage hits
                total = 0
                covered = 0
                for filename, hits in data["coverage"].items():
                    for h in hits:
                        total += 1
                        if h is not None and h > 0:
                            covered += 1
                if total > 0:
                    return (covered / total) * 100.0
            return None
        except (json.JSONDecodeError, KeyError, ValueError, IOError):
            return None

    def _extract_review_participation(self) -> Optional[dict]:
        """
        Extract Review Participation (M-03) from PR/MR export JSON.

        Calculates: reviewers_per_pr = total_unique_reviewers / total_prs
        """
        try:
            if self._pr_export_path is None or not self._pr_export_path.exists():
                return None

            with open(self._pr_export_path, "r") as f:
                prs = json.load(f)

            if not isinstance(prs, list) or len(prs) == 0:
                return None

            total_reviewers = 0
            for pr in prs:
                reviewers = pr.get("reviewers", [])
                total_reviewers += len(reviewers)

            total_prs = len(prs)
            reviewers_per_pr = total_reviewers / total_prs

            return {"w00": [reviewers_per_pr]}

        except (json.JSONDecodeError, KeyError, ValueError, IOError):
            return None

    def _extract_review_latency(self) -> Optional[dict]:
        """
        Extract Review Latency (M-04) from PR/MR export JSON.

        Calculates: mean(first_review_at - created_at) in hours for each PR.
        """
        try:
            if self._pr_export_path is None or not self._pr_export_path.exists():
                return None

            with open(self._pr_export_path, "r") as f:
                prs = json.load(f)

            if not isinstance(prs, list) or len(prs) == 0:
                return None

            latencies = []
            for pr in prs:
                created_at = pr.get("created_at")
                first_review_at = pr.get("first_review_at")
                if created_at and first_review_at:
                    try:
                        created = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        reviewed = datetime.datetime.fromisoformat(first_review_at.replace("Z", "+00:00"))
                        delta = reviewed - created
                        hours = delta.total_seconds() / 3600.0
                        latencies.append(hours)
                    except (ValueError, TypeError):
                        continue

            if not latencies:
                return None

            mean_latency = sum(latencies) / len(latencies)
            return {"w00": [mean_latency]}

        except (json.JSONDecodeError, KeyError, ValueError, IOError):
            return None

    def _extract_issue_resolution_time(self) -> Optional[dict]:
        """
        Extract Issue Resolution Time (M-05) from issue export JSON.

        Calculates: mean(closed_at - created_at) in days for each closed issue.
        """
        try:
            if self._issue_export_path is None or not self._issue_export_path.exists():
                return None

            with open(self._issue_export_path, "r") as f:
                issues = json.load(f)

            if not isinstance(issues, list) or len(issues) == 0:
                return None

            resolution_times = []
            for issue in issues:
                created_at = issue.get("created_at")
                closed_at = issue.get("closed_at")
                if created_at and closed_at:
                    try:
                        created = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        closed = datetime.datetime.fromisoformat(closed_at.replace("Z", "+00:00"))
                        delta = closed - created
                        days = delta.total_seconds() / 86400.0
                        resolution_times.append(days)
                    except (ValueError, TypeError):
                        continue

            if not resolution_times:
                return None

            mean_resolution = sum(resolution_times) / len(resolution_times)
            return {"w00": [mean_resolution]}

        except (json.JSONDecodeError, KeyError, ValueError, IOError):
            return None

    def _extract_cyclomatic_complexity(
        self,
        context: RepositoryContext,
    ) -> Optional[dict]:
        """
        Extract Cyclomatic Complexity (M-07) using lizard or radon.

        Falls back to None with warning if neither tool is available.
        """
        try:
            repo_path = context.local_path

            # Try lizard first
            try:
                import lizard

                return self._extract_complexity_lizard(lizard, repo_path)
            except ImportError:
                pass

            # Try radon as fallback
            try:
                return self._extract_complexity_radon(repo_path)
            except ImportError:
                pass

            # Neither tool available
            return None

        except Exception:
            return None

    @staticmethod
    def _extract_complexity_lizard(lizard_module, repo_path: Path) -> Optional[dict]:
        """Extract complexity using lizard."""
        try:
            # Find Python files in the repo
            py_files = list(repo_path.rglob("*.py"))
            if not py_files:
                # Also try JS/TS files
                py_files = list(repo_path.rglob("*.js")) + list(repo_path.rglob("*.ts"))

            if not py_files:
                return None

            total_complexity = 0
            func_count = 0

            for filepath in py_files:
                try:
                    result = lizard_module.analyze_file(str(filepath))
                    for func in result.function_list:
                        total_complexity += func.cyclomatic_complexity
                        func_count += 1
                except Exception:
                    continue

            if func_count == 0:
                return None

            mean_complexity = total_complexity / func_count
            return {"w00": [mean_complexity]}

        except Exception:
            return None

    @staticmethod
    def _extract_complexity_radon(repo_path: Path) -> Optional[dict]:
        """Extract complexity using radon."""
        try:
            from radon.complexity import cc_visit

            py_files = list(repo_path.rglob("*.py"))
            if not py_files:
                return None

            total_complexity = 0
            func_count = 0

            for filepath in py_files:
                try:
                    source = filepath.read_text(encoding="utf-8", errors="replace")
                    blocks = cc_visit(source)
                    for block in blocks:
                        total_complexity += block.complexity
                        func_count += 1
                except Exception:
                    continue

            if func_count == 0:
                return None

            mean_complexity = total_complexity / func_count
            return {"w00": [mean_complexity]}

        except Exception:
            return None
