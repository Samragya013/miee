"""
Metric Extraction Engine (M-02) for MIIE v1.0.

Implements INT-02: Metric Extraction Engine interface.
Extracts Commit Frequency (M-02) and Code Churn (M-06) from Git repositories.
Handles unavailable metrics per BSD/TFS missing data policy.
"""

from miie.contracts.interfaces import IExtractionEngine
from miie.contracts.errors import ExtractionError
from miie.schemas.models import RepositoryContext, MetricDataFrame
from miie.schemas.metric_registry import METRIC_REGISTRY, validate_metric_ids, MetricInfo
from typing import List, Optional
import datetime
import subprocess
import hashlib
import uuid
from pathlib import Path


def validate_metric_ids(metric_list: List[str]) -> None:
    """
    Validate that all metric IDs are in the frozen registry.

    Args:
        metric_list: List of metric IDs to validate

    Raises:
        ExtractionError: If any metric ID is not in the frozen registry
    """
    try:
        # Use the schema-level validation function
        from miie.schemas.metric_registry import validate_metric_ids as schema_validate_metric_ids
        schema_validate_metric_ids(metric_list)
    except ValueError as e:
        # Convert ValueError to ExtractionError as expected by the extraction layer
        raise ExtractionError(str(e))


class MetricExtractionEngine(IExtractionEngine):
    """INT-02: Metric Extraction Engine"""

    def extract(
        self,
        context: RepositoryContext,
        metric_list: List[str],
        since: Optional[datetime.datetime] = None,
        until: Optional[datetime.datetime] = None,
        exclude_bots: bool = False
    ) -> MetricDataFrame:
        """
        Extract metrics from repository.

        Args:
            context: Repository context from ingestion
            metric_list: List of metric IDs to extract (e.g., ["M-01", "M-06"])
            since: Extract metrics since this timestamp (inclusive)
            until: Extract metrics until this timestamp (inclusive)
            exclude_bots: Whether to exclude bot-generated commits

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
            if metric_id == "M-02":
                # Commit Frequency - Git-backed
                metrics[metric_id] = self._extract_commit_frequency(
                    context, since, until, exclude_bots
                )
            elif metric_id == "M-06":
                # Code Churn - Git-backed
                metrics[metric_id] = self._extract_code_churn(
                    context, since, until, exclude_bots
                )
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