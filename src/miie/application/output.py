"""Output Formatter — standardized terminal output and reporting.

The output formatter provides consistent display across all CLI commands.
It standardizes:
- Terminal formatting (panels, tables, progress)
- Scientific summaries (scores, detectors, verdicts)
- Error presentation
- Warning display
- Report generation

The formatter is a presentation layer — it never modifies data,
it only formats it for display.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Domain labels (frozen — derived from scientific specification)
# ---------------------------------------------------------------------------

DETECTOR_NAMES: Dict[str, str] = {
    "D-01": "Distribution Drift",
    "D-02": "Correlation Breakdown",
    "D-03": "Threshold Compression",
}

METRIC_NAMES: Dict[str, str] = {
    "M-01": "Commit Frequency",
    "M-02": "Code Churn",
    "M-03": "Review Coverage",
    "M-04": "Review Latency",
    "M-05": "Test Coverage Delta",
    "M-06": "Defect Ratio",
    "M-07": "Complexity Trend",
}


def score_label(score: float) -> str:
    """Map a 0-1 score to a human-readable label."""
    if score >= 0.95:
        return "Excellent"
    elif score >= 0.85:
        return "Good"
    elif score >= 0.70:
        return "Fair"
    elif score >= 0.50:
        return "Poor"
    else:
        return "Critical"


def score_color(score: float) -> str:
    """Map a 0-1 score to a color name."""
    if score >= 0.95:
        return "green"
    elif score >= 0.85:
        return "blue"
    elif score >= 0.70:
        return "yellow"
    elif score >= 0.50:
        return "red"
    else:
        return "bright_red"


def risk_level(triggered_count: int) -> str:
    """Map triggered detector count to a risk level."""
    if triggered_count == 0:
        return "NONE"
    elif triggered_count == 1:
        return "LOW"
    elif triggered_count == 2:
        return "MEDIUM"
    else:
        return "HIGH"


def detector_status_text(detector_output: Dict[str, Any]) -> str:
    """Generate a one-line status for a detector."""
    if detector_output.get("status") == "error":
        return "ERROR"
    if detector_output.get("status") == "skipped":
        return "SKIPPED"

    triggered = (
        detector_output.get("drift_detected")
        or detector_output.get("breakdown_detected")
        or detector_output.get("compression_detected", False)
    )
    return "TRIGGERED" if triggered else "CLEAR"


@dataclass
class FormattedOutput:
    """Structured output ready for rendering.

    Attributes:
        sections: List of (title, content) tuples.
        exit_code: Recommended exit code.
        json_data: Optional JSON data for --format json.
    """

    sections: List[tuple]
    exit_code: int = 0
    json_data: Optional[Dict[str, Any]] = None


class OutputFormatter:
    """Formats analysis results for terminal display.

    The formatter produces structured output that can be rendered
    by any display backend (Rich, plain text, JSON). It contains
    no scientific logic — it only formats data.
    """

    def format_analysis_result(
        self,
        integrity_score: float,
        confidence_score: float,
        detector_outputs: Dict[str, Any],
        metric_names: List[str],
        window_count: int,
        total_commits: Any,
        contributor_count: Any,
        timings: Optional[Dict[str, float]] = None,
        verbose: bool = False,
    ) -> FormattedOutput:
        """Format a complete analysis result for display."""
        sections: List[tuple] = []

        # Coverage section
        coverage_lines = [
            f"  Commits:        {total_commits}",
            f"  Contributors:   {contributor_count}",
            f"  Windows:        {window_count}",
            f"  Metrics:        {', '.join(metric_names)}",
        ]
        sections.append(("Analysis Coverage", "\n".join(coverage_lines)))

        # Findings section
        triggered_count = 0
        failed_detectors: List[str] = []
        finding_lines: List[str] = []
        for det_id, det_data in detector_outputs.items():
            if not isinstance(det_data, dict):
                continue
            status = detector_status_text(det_data)
            det_name = DETECTOR_NAMES.get(det_id, det_id)
            if status == "ERROR":
                finding_lines.append(f"  {det_id} ({det_name}): ERROR")
                failed_detectors.append(det_id)
            elif status == "SKIPPED":
                finding_lines.append(f"  {det_id} ({det_name}): SKIPPED")
            elif status == "TRIGGERED":
                triggered_count += 1
                finding_lines.append(f"  {det_id} ({det_name}): TRIGGERED")
            else:
                finding_lines.append(f"  {det_id} ({det_name}): CLEAR")

        if not finding_lines:
            finding_lines = ["  No detector results available"]
        sections.append(("Integrity Findings", "\n".join(finding_lines)))

        # Scores section
        rl = risk_level(triggered_count)
        score_lines = [
            f"  Integrity:      {integrity_score:.4f} ({score_label(integrity_score)})",
            f"  Confidence:     {confidence_score:.4f} ({score_label(confidence_score)})",
            f"  Risk Level:     {rl}",
        ]
        sections.append(("Scores", "\n".join(score_lines)))

        # Verdict section
        verdict = "PASS" if integrity_score >= 1.0 else "FAIL"
        action = "No action required." if integrity_score >= 1.0 else "Investigate triggered detectors."
        verdict_lines = [
            f"  Verdict:        {verdict}",
            f"  Action:         {action}",
        ]
        sections.append(("Verdict", "\n".join(verdict_lines)))

        # Timing section (verbose)
        if verbose and timings:
            timing_lines = []
            for stage, duration in timings.items():
                timing_lines.append(f"  {stage:<20} {duration:.2f}s")
            sections.append(("Timing", "\n".join(timing_lines)))

        # Exit code
        exit_code = 0 if integrity_score >= 1.0 else 1

        # JSON data
        json_data = {
            "integrity_score": integrity_score,
            "confidence_score": confidence_score,
            "risk_level": rl,
            "verdict": verdict,
            "triggered_count": triggered_count,
            "detector_outputs": detector_outputs,
            "metric_names": metric_names,
            "window_count": window_count,
        }

        return FormattedOutput(
            sections=sections,
            exit_code=exit_code,
            json_data=json_data,
        )

    def format_status(
        self,
        version: str,
        detectors: List[str],
        metrics: List[str],
    ) -> FormattedOutput:
        """Format system status for display."""
        lines = [
            f"  Version:        {version}",
            f"  Detectors:      {', '.join(detectors)}",
            f"  Metrics:        {', '.join(metrics)}",
        ]
        return FormattedOutput(
            sections=[("System Status", "\n".join(lines))],
            exit_code=0,
        )

    def format_error(self, message: str, details: Optional[str] = None) -> FormattedOutput:
        """Format an error for display."""
        lines = [f"  {message}"]
        if details:
            lines.append(f"  Details: {details}")
        return FormattedOutput(
            sections=[("Error", "\n".join(lines))],
            exit_code=2,
        )

    def format_warning(self, message: str) -> FormattedOutput:
        """Format a warning for display."""
        return FormattedOutput(
            sections=[("Warning", f"  {message}")],
            exit_code=0,
        )

    def to_json(self, output: FormattedOutput) -> str:
        """Serialize formatted output to JSON."""
        return json.dumps(
            {
                "sections": [{"title": t, "content": c} for t, c in output.sections],
                "exit_code": output.exit_code,
                "data": output.json_data,
            },
            indent=2,
            sort_keys=True,
        )

    def to_markdown(self, output: FormattedOutput) -> str:
        """Serialize formatted output to Markdown."""
        lines = []
        for title, content in output.sections:
            lines.append(f"## {title}")
            lines.append("")
            lines.append(content)
            lines.append("")
        return "\n".join(lines)
