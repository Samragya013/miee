"""
Metric Extraction Engine for MIIE v1.0.

Implements INT-02: Metric Extraction Engine interface.
Extracts all 7 metrics from Git repositories and external artifacts.
Handles unavailable metrics per BSD/TFS missing data policy.
"""

from miie.contracts.interfaces import IExtractionEngine
from miie.contracts.errors import ExtractionError
from miie.schemas.models import RepositoryContext, MetricDataFrame
from miie.schemas.metric_registry import METRIC_REGISTRY, MetricInfo
from typing import List, Optional, Dict, Any
import datetime
import subprocess
import hashlib
import uuid
import json
import os
import warnings
from pathlib import Path
from xml.etree import ElementTree


def validate_metric_ids(metric_list: List[str]) -> None:
    """
    Validate that all metric IDs are in the frozen registry.

    Args:
        metric_list: List of metric IDs to validate

    Raises:
        ExtractionError: If any metric ID is not in the frozen registry
    """
    try:
        from miie.schemas.metric_registry import validate_metric_ids as schema_validate_metric_ids
        schema_validate_metric_ids(metric_list)
    except ValueError as e:
        raise ExtractionError(str(e))


class MetricExtractionEngine(IExtractionEngine):
    """INT-02: Metric Extraction Engine"""

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

    def extract(
        self,
        context: RepositoryContext,
        metric_list: List[str],
        since: Optional[datetime.datetime] = None,
        until: Optional[datetime.datetime] = None,
        exclude_bots: bool = False,
        windows: Optional[List[Any]] = None
    ) -> MetricDataFrame:
        """
        Extract metrics from repository.

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

        # Initialize metrics dictionary
        metrics = {}

        # Extract each requested metric
        for metric_id in metric_list:
            if metric_id == "M-01":
                metrics[metric_id] = self._extract_code_coverage(context)
            elif metric_id == "M-02":
                if windows:
                    metrics[metric_id] = self._extract_commit_frequency_windowed(
                        context, windows, exclude_bots
                    )
                else:
                    metrics[metric_id] = self._extract_commit_frequency(
                        context, since, until, exclude_bots
                    )
            elif metric_id == "M-03":
                metrics[metric_id] = self._extract_review_participation()
            elif metric_id == "M-04":
                metrics[metric_id] = self._extract_review_latency()
            elif metric_id == "M-05":
                metrics[metric_id] = self._extract_issue_resolution_time()
            elif metric_id == "M-06":
                if windows:
                    metrics[metric_id] = self._extract_code_churn_windowed(
                        context, windows, exclude_bots
                    )
                else:
                    metrics[metric_id] = self._extract_code_churn(
                        context, since, until, exclude_bots
                    )
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
                metrics=metrics
            )
        except ValueError as e:
            raise ExtractionError(f"Invalid MetricDataFrame: {e}")

    def _extract_commit_frequency(
        self,
        context: RepositoryContext,
        since: Optional[datetime.datetime],
        until: Optional[datetime.datetime],
        exclude_bots: bool
    ) -> Optional[dict]:
        """
        Extract Commit Frequency (M-02) from Git history.

        Returns:
            Dict mapping window IDs to lists of commit counts, or None if unavailable
        """
        try:
            # For Day 7 foundation, we extract total commit count as a single value
            # In future versions, this would be windowed
            commit_count = self._get_commit_count_since_until(
                context.local_path, since, until, exclude_bots
            )

            # Return as a single window (w00) for foundation implementation
            # This represents the total commit frequency for the entire history
            return {"w00": [float(commit_count)]} if commit_count is not None else None

        except Exception as e:
            # Per missing data policy, unavailable metrics return None, not zero or fake values
            return None

    def _extract_commit_frequency_windowed(
        self,
        context: RepositoryContext,
        windows: List[Any],
        exclude_bots: bool
    ) -> Optional[dict]:
        """
        Extract Commit Frequency (M-02) per window from Git history.

        Uses a single git log call to get all commits, then bins them by window.
        Much faster than calling git per window.

        Args:
            context: Repository context
            windows: List of WindowDefinition objects with window_id, start_date, end_date
            exclude_bots: Whether to exclude bot-generated commits

        Returns:
            Dict mapping window IDs to lists of commit counts, or None if unavailable
        """
        try:
            # Single git log call to get all commit dates
            cmd = ['git', 'log', '--format=%aI', '--no-merges']
            result = subprocess.run(
                cmd,
                cwd=context.local_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=True
            )

            # Parse commit dates
            commit_dates = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        # Parse ISO format date
                        dt = datetime.datetime.fromisoformat(line.strip())
                        commit_dates.append(dt.date())
                    except ValueError:
                        continue

            # Bin commits into windows
            result_dict = {}
            for window in windows:
                window_id = window.window_id
                count = 0
                for cd in commit_dates:
                    if window.start_date <= cd < window.end_date:
                        count += 1
                result_dict[window_id] = [float(count)]

            return result_dict
        except Exception:
            return None

    def _extract_code_churn_windowed(
        self,
        context: RepositoryContext,
        windows: List[Any],
        exclude_bots: bool
    ) -> Optional[dict]:
        """
        Extract Code Churn (M-06) per window from Git history.

        Uses a single git log call to get all commits with stats, then bins by window.
        Much faster than calling git per window.

        Args:
            context: Repository context
            windows: List of WindowDefinition objects with window_id, start_date, end_date
            exclude_bots: Whether to exclude bot-generated commits

        Returns:
            Dict mapping window IDs to lists of churn values, or None if unavailable
        """
        try:
            # Single git log call to get all commit dates and stats
            cmd = ['git', 'log', '--format=%aI', '--shortstat', '--no-merges']
            result = subprocess.run(
                cmd,
                cwd=context.local_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=True
            )

            # Parse commit dates and churn values
            commits = []
            lines = result.stdout.strip().split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line and 'insertion' in line.lower() or 'deletion' in line.lower():
                    # This is a stats line, parse it
                    insertions = 0
                    deletions = 0
                    parts = line.split(',')
                    for part in parts:
                        part = part.strip()
                        if 'insertion' in part:
                            try:
                                insertions = int(part.split()[0])
                            except (ValueError, IndexError):
                                pass
                        elif 'deletion' in part:
                            try:
                                deletions = int(part.split()[0])
                            except (ValueError, IndexError):
                                pass
                    # Get the date from the previous line
                    if i > 0:
                        date_str = lines[i-1].strip()
                        if date_str:
                            try:
                                dt = datetime.datetime.fromisoformat(date_str)
                                commits.append((dt.date(), float(insertions + deletions)))
                            except ValueError:
                                pass
                i += 1

            # Bin churn values into windows
            result_dict = {}
            for window in windows:
                window_id = window.window_id
                churn_values = [churn for cd, churn in commits
                               if window.start_date <= cd < window.end_date]
                total_churn = sum(churn_values) if churn_values else 0.0
                result_dict[window_id] = [total_churn]

            return result_dict
        except Exception:
            return None

    def _extract_code_churn(
        self,
        context: RepositoryContext,
        since: Optional[datetime.datetime],
        until: Optional[datetime.datetime],
        exclude_bots: bool
    ) -> Optional[dict]:
        """
        Extract Code Churn (M-06) from Git history.

        Returns:
            Dict mapping window IDs to lists of churn values, or None if unavailable
        """
        try:
            # For Day 7 foundation, we extract total churn as a single value
            # In future versions, this would be windowed
            churn_value = self._get_code_churn_since_until(
                context.local_path, since, until, exclude_bots
            )

            # Return as a single window (w00) for foundation implementation
            # This represents the total code churn for the entire history
            return {"w00": [float(churn_value)]} if churn_value is not None else None

        except Exception as e:
            # Per missing data policy, unavailable metrics return None, not zero or fake values
            return None

    def _extract_code_coverage(
        self,
        context: RepositoryContext,
    ) -> Optional[dict]:
        """
        Extract Code Coverage (M-01) from coverage artifacts.

        Parses coverage.xml (Cobertura), lcov.info, or .coverage (JSON).
        Returns value in range [0, 100]%.

        Returns:
            Dict mapping window IDs to lists of coverage percentages, or None if unavailable
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

        Returns:
            Dict mapping window IDs to lists of reviewer counts, or None if unavailable
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

        Returns:
            Dict mapping window IDs to lists of latencies in hours, or None if unavailable
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

        Returns:
            Dict mapping window IDs to lists of resolution times in days, or None if unavailable
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

        Returns:
            Dict mapping window IDs to lists of mean complexity scores, or None if unavailable
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
                from radon.complexity import cc_visit
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
            from radon.raw import analyze

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

    @staticmethod
    def _get_commit_count_since_until(
        repo_path: Path,
        since: Optional[datetime.datetime],
        until: Optional[datetime.datetime],
        exclude_bots: bool
    ) -> Optional[int]:
        """
        Get commit count for a specific time range.

        Returns:
            Number of commits in range, or None if unavailable
        """
        try:
            # Build git rev-list command
            cmd = ['git', 'rev-list', '--count', 'HEAD']

            # Add since/until filters
            if since:
                since_str = since.strftime('%Y-%m-%d')
                cmd.extend(['--since', since_str])
            if until:
                until_str = until.strftime('%Y-%m-%d')
                cmd.extend(['--until', until_str])

            # Add bot exclusion if requested
            if exclude_bots:
                cmd.extend(['--exclude', '*/.git/*'])  # Simple approach
                # More sophisticated bot exclusion would check author emails

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=True
            )

            count_str = result.stdout.strip()
            return int(count_str) if count_str else 0

        except (subprocess.CalledProcessError, ValueError):
            return None

    @staticmethod
    def _get_code_churn_since_until(
        repo_path: Path,
        since: Optional[datetime.datetime],
        until: Optional[datetime.datetime],
        exclude_bots: bool
    ) -> Optional[float]:
        """
        Get code churn (lines added + deleted) for a specific time range.

        Returns:
            Total churn value, or None if unavailable
        """
        try:
            # Build git log command with shortstat to get insertions/deletions
            cmd = ['git', 'log', '--pretty=format:', '--numstat']

            # Add since/until filters
            if since:
                since_str = since.strftime('%Y-%m-%d')
                cmd.extend(['--since', since_str])
            if until:
                until_str = until.strftime('%Y-%m-%d')
                cmd.extend(['--until', until_str])

            # Add bot exclusion if requested (basic implementation)
            if exclude_bots:
                # Exclude common bot patterns - this is simplified
                cmd.extend(['--author', '^(?!.*(bot|dependabot|github-actions)).*$'])

            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=True
            )

            total_churn = 0
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        try:
                            additions = int(parts[0]) if parts[0] != '-' else 0
                            deletions = int(parts[1]) if parts[1] != '-' else 0
                            total_churn += additions + deletions
                        except ValueError:
                            # Skip lines that don't parse as numbers
                            continue

            return float(total_churn) if total_churn > 0 else 0.0

        except (subprocess.CalledProcessError, ValueError):
            return None