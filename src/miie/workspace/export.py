"""Workspace Exporter.

Exports workspace results in multiple formats:
- Markdown (MD)
- JSON
- YAML
- HTML

All exports are deterministic and derived from frozen scientific outputs.
"""

from __future__ import annotations

import html as html_mod
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .engine import WorkspaceEngine
from .recommendations import RecommendationEngine
from .traceability import TraceabilityEngine
from .views import (
    BenchmarkView,
    ConfidenceView,
    DetectorView,
    EvidenceView,
    ExecutiveSummary,
    IntegrityView,
    MetricView,
    SessionInfoView,
    ValidationView,
)


class WorkspaceExporter:
    """Export workspace results in multiple formats."""

    def __init__(self, workspace: WorkspaceEngine) -> None:
        self.workspace = workspace

    def export_markdown(
        self,
        output_path: str,
        sections: Optional[List[str]] = None,
    ) -> str:
        """Export workspace to Markdown file.

        Args:
            output_path: Path to output file
            sections: Sections to export (None = all)

        Returns:
            Path to exported file
        """
        if sections is None:
            sections = [
                "executive_summary",
                "metrics",
                "detectors",
                "evidence",
                "confidence",
                "integrity",
                "validation",
                "benchmark",
                "recommendations",
                "traceability",
                "session",
            ]

        lines = []
        lines.append("# MIIE Analysis Report")
        lines.append("")
        lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
        lines.append("")

        # Executive Summary
        if "executive_summary" in sections:
            view = ExecutiveSummary()
            result = view.render(self.workspace)
            lines.extend(result.lines)
            lines.append("")

        # Metrics
        if "metrics" in sections:
            view = MetricView()
            result = view.render(self.workspace)
            lines.extend(result.lines)
            lines.append("")

        # Detectors
        if "detectors" in sections:
            view = DetectorView()
            result = view.render(self.workspace)
            lines.extend(result.lines)
            lines.append("")

        # Evidence
        if "evidence" in sections:
            view = EvidenceView()
            result = view.render(self.workspace)
            lines.extend(result.lines)
            lines.append("")

        # Confidence
        if "confidence" in sections:
            view = ConfidenceView()
            result = view.render(self.workspace)
            lines.extend(result.lines)
            lines.append("")

        # Integrity
        if "integrity" in sections:
            view = IntegrityView()
            result = view.render(self.workspace)
            lines.extend(result.lines)
            lines.append("")

        # Validation
        if "validation" in sections:
            view = ValidationView()
            result = view.render(self.workspace)
            lines.extend(result.lines)
            lines.append("")

        # Benchmark
        if "benchmark" in sections:
            view = BenchmarkView()
            result = view.render(self.workspace)
            lines.extend(result.lines)
            lines.append("")

        # Recommendations
        if "recommendations" in sections:
            engine = RecommendationEngine(self.workspace)
            recs = engine.generate_all()
            lines.append("=" * 72)
            lines.append("RECOMMENDATIONS")
            lines.append("=" * 72)
            lines.append("")
            lines.append(f"Total Recommendations: {len(recs)}")
            lines.append("")
            for rec in recs:
                lines.append(f"### [{rec.priority.upper()}] {rec.title}")
                lines.append("")
                lines.append(rec.description)
                lines.append("")
                lines.append(f"**Reason:** {rec.reason}")
                lines.append(f"**Confidence:** {rec.confidence:.2f}")
                lines.append(f"**Specification:** {rec.spec_reference}")
                if rec.evidence_refs:
                    lines.append("**Evidence:**")
                    for ref in rec.evidence_refs:
                        lines.append(f"  - {ref}")
                lines.append("")

        # Traceability
        if "traceability" in sections:
            trace_engine = TraceabilityEngine(self.workspace)
            chains = trace_engine.get_all_chains()
            lines.append("=" * 72)
            lines.append("TRACEABILITY CHAINS")
            lines.append("=" * 72)
            lines.append("")
            lines.append(f"Total Chains: {len(chains)}")
            lines.append("")
            for i, chain in enumerate(chains, 1):
                lines.append(f"### Chain {i}")
                lines.append("")
                chain_lines = chain.render_lines()
                lines.extend(chain_lines)
                lines.append("")

        # Session Info
        if "session" in sections:
            view = SessionInfoView()
            result = view.render(self.workspace)
            lines.extend(result.lines)
            lines.append("")

        # Write file
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("\n".join(lines), encoding="utf-8")

        # Record export
        self.workspace.add_export_record("markdown", str(output), sections)

        return str(output)

    def export_json(
        self,
        output_path: str,
        sections: Optional[List[str]] = None,
    ) -> str:
        """Export workspace to JSON file.

        Args:
            output_path: Path to output file
            sections: Sections to export (None = all)

        Returns:
            Path to exported file
        """
        if sections is None:
            sections = [
                "executive_summary",
                "metrics",
                "detectors",
                "evidence",
                "confidence",
                "integrity",
                "validation",
                "benchmark",
                "recommendations",
                "traceability",
                "session",
            ]

        export_data: Dict[str, Any] = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "workspace_id": self.workspace.state.workspace_id,
                "sections": sections,
            },
        }

        # Executive Summary
        if "executive_summary" in sections:
            view = ExecutiveSummary()
            result = view.render(self.workspace)
            export_data["executive_summary"] = {
                "title": result.title,
                "lines": result.lines,
                "actions": result.actions,
            }

        # Metrics
        if "metrics" in sections:
            view = MetricView()
            result = view.render(self.workspace)
            export_data["metrics"] = {
                "title": result.title,
                "lines": result.lines,
            }

        # Detectors
        if "detectors" in sections:
            view = DetectorView()
            result = view.render(self.workspace)
            export_data["detectors"] = {
                "title": result.title,
                "lines": result.lines,
            }

        # Evidence
        if "evidence" in sections:
            view = EvidenceView()
            result = view.render(self.workspace)
            export_data["evidence"] = {
                "title": result.title,
                "lines": result.lines,
            }

        # Confidence
        if "confidence" in sections:
            view = ConfidenceView()
            result = view.render(self.workspace)
            export_data["confidence"] = {
                "title": result.title,
                "lines": result.lines,
            }

        # Integrity
        if "integrity" in sections:
            view = IntegrityView()
            result = view.render(self.workspace)
            export_data["integrity"] = {
                "title": result.title,
                "lines": result.lines,
            }

        # Validation
        if "validation" in sections:
            view = ValidationView()
            result = view.render(self.workspace)
            export_data["validation"] = {
                "title": result.title,
                "lines": result.lines,
            }

        # Benchmark
        if "benchmark" in sections:
            view = BenchmarkView()
            result = view.render(self.workspace)
            export_data["benchmark"] = {
                "title": result.title,
                "lines": result.lines,
            }

        # Recommendations
        if "recommendations" in sections:
            engine = RecommendationEngine(self.workspace)
            recs = engine.generate_all()
            export_data["recommendations"] = {
                "total": len(recs),
                "items": [r.to_dict() for r in recs],
            }

        # Traceability
        if "traceability" in sections:
            trace_engine = TraceabilityEngine(self.workspace)
            chains = trace_engine.get_all_chains()
            export_data["traceability"] = {
                "total": len(chains),
                "chains": [c.to_dict() for c in chains],
            }

        # Session Info
        if "session" in sections:
            view = SessionInfoView()
            result = view.render(self.workspace)
            export_data["session"] = {
                "title": result.title,
                "lines": result.lines,
            }

        # Write file
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(export_data, indent=2, default=str), encoding="utf-8")

        # Record export
        self.workspace.add_export_record("json", str(output), sections)

        return str(output)

    def export_yaml(
        self,
        output_path: str,
        sections: Optional[List[str]] = None,
    ) -> str:
        """Export workspace to YAML file.

        Args:
            output_path: Path to output file
            sections: Sections to export (None = all)

        Returns:
            Path to exported file
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for YAML export. Install with: pip install pyyaml")

        # Build same structure as JSON export
        json_path = output_path.replace(".yaml", ".json").replace(".yml", ".json")
        self.export_json(json_path, sections)

        # Read JSON and convert to YAML
        json_data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(yaml.dump(json_data, default_flow_style=False), encoding="utf-8")

        # Clean up temp JSON
        Path(json_path).unlink(missing_ok=True)

        # Record export
        self.workspace.add_export_record("yaml", str(output), sections or [])

        return str(output)

    def export_html(
        self,
        output_path: str,
        sections: Optional[List[str]] = None,
    ) -> str:
        """Export workspace to HTML file.

        Args:
            output_path: Path to output file
            sections: Sections to export (None = all)

        Returns:
            Path to exported file
        """
        # Build markdown first
        md_lines = []
        md_lines.append("# MIIE Analysis Report")
        md_lines.append("")
        md_lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
        md_lines.append("")

        if sections is None:
            sections = [
                "executive_summary",
                "metrics",
                "detectors",
                "evidence",
                "confidence",
                "integrity",
                "validation",
                "benchmark",
                "recommendations",
                "traceability",
                "session",
            ]

        # Add all sections
        for section in sections:
            if section == "recommendations":
                engine = RecommendationEngine(self.workspace)
                recs = engine.generate_all()
                md_lines.append(f"## Recommendations ({len(recs)})")
                md_lines.append("")
                for rec in recs:
                    md_lines.append(f"### {rec.title}")
                    md_lines.append(rec.description)
                    md_lines.append("")
            elif section == "traceability":
                trace_engine = TraceabilityEngine(self.workspace)
                chains = trace_engine.get_all_chains()
                md_lines.append(f"## Traceability ({len(chains)} chains)")
                md_lines.append("")
                for i, chain in enumerate(chains, 1):
                    md_lines.append(f"### Chain {i}")
                    md_lines.extend(chain.render_lines())
                    md_lines.append("")
            else:
                view_map = {
                    "executive_summary": ExecutiveSummary,
                    "metrics": MetricView,
                    "detectors": DetectorView,
                    "evidence": EvidenceView,
                    "confidence": ConfidenceView,
                    "integrity": IntegrityView,
                    "validation": ValidationView,
                    "benchmark": BenchmarkView,
                    "session": SessionInfoView,
                }
                view_class = view_map.get(section)
                if view_class is not None:
                    view_instance = view_class()
                    result = view_instance.render(self.workspace)  # type: ignore[attr-defined]
                    md_lines.extend(result.lines)
                    md_lines.append("")

        # Convert to simple HTML
        html_content = self._markdown_to_html("\n".join(md_lines))

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(html_content, encoding="utf-8")

        # Record export
        self.workspace.add_export_record("html", str(output), sections)

        return str(output)

    def _markdown_to_html(self, md: str) -> str:
        """Convert markdown to simple HTML."""
        lines = md.split("\n")
        html_lines = []
        html_lines.append("<!DOCTYPE html>")
        html_lines.append("<html><head>")
        html_lines.append("<title>MIIE Analysis Report</title>")
        html_lines.append("<style>")
        html_lines.append("body { font-family: monospace; max-width: 900px; margin: 0 auto; padding: 20px; }")
        html_lines.append("h1 { border-bottom: 2px solid #333; }")
        html_lines.append("h2 { color: #333; }")
        html_lines.append("pre { background: #f5f5f5; padding: 10px; }")
        html_lines.append("</style>")
        html_lines.append("</head><body>")

        for line in lines:
            if line.startswith("# "):
                html_lines.append(f"<h1>{html_mod.escape(line[2:])}</h1>")
            elif line.startswith("## "):
                html_lines.append(f"<h2>{html_mod.escape(line[3:])}</h2>")
            elif line.startswith("### "):
                html_lines.append(f"<h3>{html_mod.escape(line[4:])}</h3>")
            elif line.startswith("- "):
                html_lines.append(f"<li>{html_mod.escape(line[2:])}</li>")
            elif line.startswith("=" * 40):
                html_lines.append("<hr>")
            elif line.strip():
                html_lines.append(f"<p>{html_mod.escape(line)}</p>")

        html_lines.append("</body></html>")
        return "\n".join(html_lines)
