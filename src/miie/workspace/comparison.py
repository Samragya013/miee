"""Session Comparison Engine.

Compares analysis results across different runs or time periods.
All comparisons are deterministic and based on frozen scientific outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ComparisonResult:
    """Result of comparing two workspace states."""

    metric_name: str
    current_value: float
    previous_value: float
    change: float
    change_percent: float
    direction: str  # "improved", "degraded", "unchanged"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "previous_value": self.previous_value,
            "change": self.change,
            "change_percent": self.change_percent,
            "direction": self.direction,
        }


class ComparisonEngine:
    """Compare workspace states for session comparison."""

    def compare(
        self,
        current: Dict[str, Any],
        previous: Dict[str, Any],
    ) -> List[ComparisonResult]:
        """Compare two workspace cache data dictionaries.

        Args:
            current: Current workspace cache data
            previous: Previous workspace cache data

        Returns:
            List of comparison results
        """
        results = []

        # Compare integrity scores
        integrity_current = self._get_score(current, "integrity")
        integrity_previous = self._get_score(previous, "integrity")
        if integrity_current is not None and integrity_previous is not None:
            results.append(self._compare_values("integrity_score", integrity_current, integrity_previous))

        # Compare confidence scores
        confidence_current = self._get_score(current, "confidence")
        confidence_previous = self._get_score(previous, "confidence")
        if confidence_current is not None and confidence_previous is not None:
            results.append(self._compare_values("confidence_score", confidence_current, confidence_previous))

        # Compare finding counts
        findings_current = self._get_finding_count(current)
        findings_previous = self._get_finding_count(previous)
        if findings_current is not None and findings_previous is not None:
            results.append(self._compare_values("finding_count", float(findings_current), float(findings_previous)))

        # Compare per-metric integrity scores
        metric_scores_current = self._get_metric_scores(current)
        metric_scores_previous = self._get_metric_scores(previous)
        all_metrics = set(metric_scores_current.keys()) | set(metric_scores_previous.keys())
        for metric in sorted(all_metrics):
            curr = metric_scores_current.get(metric)
            prev = metric_scores_previous.get(metric)
            if curr is not None and prev is not None:
                results.append(self._compare_values(f"metric_{metric}_integrity", curr, prev))

        return results

    def render_comparison(
        self,
        results: List[ComparisonResult],
        current_label: str = "Current",
        previous_label: str = "Previous",
    ) -> List[str]:
        """Render comparison results as human-readable lines."""
        lines = []
        lines.append("=" * 72)
        lines.append("SESSION COMPARISON")
        lines.append("=" * 72)
        lines.append("")
        lines.append(f"Current: {current_label}")
        lines.append(f"Previous: {previous_label}")
        lines.append("")

        if not results:
            lines.append("No comparable data found.")
            return lines

        lines.append(f"{'Metric':<35} {'Current':>10} {'Previous':>10} {'Change':>10} {'Status':>10}")
        lines.append("-" * 72)

        for r in results:
            direction_icon = {
                "improved": "^",
                "degraded": "v",
                "unchanged": "=",
            }.get(r.direction, "?")

            lines.append(
                f"{r.metric_name:<35} {r.current_value:>10.4f} "
                f"{r.previous_value:>10.4f} {r.change:>+10.4f} "
                f"{direction_icon:>10}"
            )

        lines.append("")

        # Summary
        improved = sum(1 for r in results if r.direction == "improved")
        degraded = sum(1 for r in results if r.direction == "degraded")
        unchanged = sum(1 for r in results if r.direction == "unchanged")

        lines.append(f"Summary: {improved} improved, {degraded} degraded, {unchanged} unchanged")

        return lines

    def _get_score(self, data: Dict[str, Any], score_type: str) -> Optional[float]:
        """Extract score from cache data."""
        full_context = data.get("full_context", {})
        score_package = full_context.get("score_package")
        if score_package is None:
            return None

        if hasattr(score_package, score_type):
            score_obj = getattr(score_package, score_type)
            if score_obj is not None:
                return getattr(score_obj, "score", None)

        return None

    def _get_finding_count(self, data: Dict[str, Any]) -> Optional[int]:
        """Extract finding count from cache data."""
        full_context = data.get("full_context", {})
        score_package = full_context.get("score_package")
        if score_package is None:
            return None

        integrity = getattr(score_package, "integrity", None)
        if integrity is None:
            return None

        findings = getattr(integrity, "findings", []) or []
        return len(findings)

    def _get_metric_scores(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract per-metric scores from cache data."""
        full_context = data.get("full_context", {})
        score_package = full_context.get("score_package")
        if score_package is None:
            return {}

        integrity = getattr(score_package, "integrity", None)
        if integrity is None:
            return {}

        metric_scores = getattr(integrity, "metric_scores", {}) or {}
        result = {}
        for metric_name, ms in metric_scores.items():
            if ms is not None:
                score = getattr(ms, "score", None)
                if score is not None:
                    result[metric_name] = float(score)

        return result

    def _compare_values(self, name: str, current: float, previous: float) -> ComparisonResult:
        """Compare two numeric values."""
        change = current - previous
        if previous != 0:
            change_percent = (change / abs(previous)) * 100
        else:
            change_percent = 0.0

        if change > 0.01:
            direction = "improved"
        elif change < -0.01:
            direction = "degraded"
        else:
            direction = "unchanged"

        return ComparisonResult(
            metric_name=name,
            current_value=current,
            previous_value=previous,
            change=change,
            change_percent=change_percent,
            direction=direction,
        )
