"""
MIIE v1.5 Scientific Readiness Certification — Engine (PR-7C-3).

Runs the sampling diagnostics pipeline on each repository and produces
ScientificExecutionReports with per-detector verdicts and aggregate
certification.

Reference: PR-7C-3, OEAS SS21, DES v2.0
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from miie.sampling.diagnostics import DiagnosticsEngine
from miie.sampling.models import SamplingDiagnostics

from .interpreter import VerdictInterpreter
from .models import (
    AggregateCertification,
    RepositoryCertification,
    ScientificExecutionReport,
)

logger = logging.getLogger(__name__)

# Repository metadata mapping (ID -> human name)
_REPO_NAMES: Dict[str, str] = {
    "A-01": "torvalds/linux",
    "A-02": "git/git",
    "A-03": "golang/go",
    "A-04": "rust-lang/rust",
    "A-05": "golang/go (golang)",
    "B-01": "kubernetes/kubernetes",
    "B-02": "ansible/ansible",
    "B-03": "docker/cli",
    "B-04": "hashicorp/terraform",
    "B-05": "grafana/grafana",
    "C-01": "django/django",
    "C-02": "facebookresearch/ParlAI",
    "C-03": "pallets/flask",
    "C-04": "pallets/jinja",
    "C-05": "encode/httpx",
    "D-01": "spring-projects/spring-boot",
    "D-02": "oracle/node",
    "D-03": "phpmyadmin/phpmyadmin",
    "D-04": "Homebrew/brew",
    "E-01": "vuejs/vue",
    "E-02": "angular/angular",
    "E-03": "sveltejs/svelte",
    "E-04": "emberjs/ember.js",
    "E-05": "preactjs/preact",
    "F-01": "microsoft/vscode",
    "F-02": "atom/atom",
    "F-03": "torvalds/linux",
    "F-04": "torvalds/linux",
}


class ScientificReadinessEngine:
    """Engine for scientific readiness certification (PR-7C-3).

    Responsibilities:
    - Run sampling diagnostics on each repository
    - Produce ScientificExecutionReport per repository
    - Interpret detector verdicts
    - Produce aggregate certification across all repos
    """

    def __init__(self) -> None:
        self._diagnostics_engine = DiagnosticsEngine()
        self._interpreter = VerdictInterpreter()

    def certify_repository(
        self,
        repo_id: str,
        sampling_diagnostics: SamplingDiagnostics,
    ) -> ScientificExecutionReport:
        """Certify a single repository from its sampling diagnostics.

        Args:
            repo_id: Repository identifier.
            sampling_diagnostics: Pre-computed SamplingDiagnostics.

        Returns:
            ScientificExecutionReport with verdicts.
        """
        repo_name = _REPO_NAMES.get(repo_id, repo_id)

        # Interpret detector readiness into verdicts
        detector_verdicts = self._interpreter.interpret_readiness(sampling_diagnostics.readiness)

        # Compute overall certification
        certification = self._interpreter.certify_repo(
            repo_id=repo_id,
            repo_name=repo_name,
            detector_verdicts=detector_verdicts,
            sampling_diagnostics=sampling_diagnostics,
        )

        # Build detector summary
        detector_summary = {v.detector_id: v.state for v in detector_verdicts}

        return ScientificExecutionReport(
            repo_id=repo_id,
            repo_name=repo_name,
            certification=certification,
            sampling_diagnostics_raw=self._diagnostics_engine.to_dict(sampling_diagnostics),
            detector_summary=detector_summary,
            is_valid=certification.verdict == "READY",
        )

    def certify_batch(
        self,
        repo_results: Dict[str, SamplingDiagnostics],
    ) -> AggregateCertification:
        """Certify a batch of repositories and produce aggregate results.

        Args:
            repo_results: Mapping of repo_id -> SamplingDiagnostics.

        Returns:
            AggregateCertification across all repos.
        """
        certifications: List[RepositoryCertification] = []
        warnings: List[str] = []

        for repo_id, diagnostics in repo_results.items():
            try:
                report = self.certify_repository(repo_id, diagnostics)
                certifications.append(report.certification)
            except Exception as e:
                warnings.append(f"Failed to certify {repo_id}: {e}")
                logger.warning("Certification failed for %s: %s", repo_id, e)

        # Compute aggregate stats
        total = len(certifications)
        ready = sum(1 for c in certifications if c.verdict == "READY")
        partial = sum(1 for c in certifications if c.verdict == "PARTIAL")
        skipped = sum(1 for c in certifications if c.verdict == "SKIPPED")
        failed = len(repo_results) - total

        # Overall verdict
        if total == 0:
            overall_verdict = "NOT_ASSESSED"
        elif ready == total:
            overall_verdict = "READY"
        elif ready + partial == total:
            overall_verdict = "PARTIAL"
        else:
            overall_verdict = "PARTIAL"

        # Mean confidence
        confidences = [c.overall_confidence for c in certifications]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return AggregateCertification(
            total_repos=total,
            ready_count=ready,
            partial_count=partial,
            skipped_count=skipped,
            failed_count=failed,
            overall_verdict=overall_verdict,
            overall_confidence=round(overall_confidence, 4),
            certifications=tuple(certifications),
            warnings=warnings,
        )

    def load_diagnostics_from_json(
        self,
        json_path: Path,
    ) -> Optional[SamplingDiagnostics]:
        """Load SamplingDiagnostics from a JSON report file.

        Args:
            json_path: Path to analysis_report JSON file.

        Returns:
            SamplingDiagnostics if valid, None otherwise.
        """
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            sd_data = data.get("analysis_result", {}).get("sampling_diagnostics", {})
            if not sd_data:
                return None

            # Reconstruct minimal SamplingDiagnostics from dict
            from miie.sampling.models import (
                ReadinessReport,
                RepositoryProfile,
                SamplingPlan,
                StrategyCandidate,
            )

            # Profile
            p_data = sd_data.get("profile", {})
            profile = RepositoryProfile(
                commit_count=p_data.get("commit_count", 0),
                repo_age_days=p_data.get("repo_age_days", 0),
                observation_count=p_data.get("observation_count", 0),
                observation_density=p_data.get("observation_density", 0.0),
                commit_density=p_data.get("commit_density", 0.0),
                avg_commits_per_day=p_data.get("commit_density", 0.0),
                window_density=0.0,
                avg_obs_per_window=0.0,
                min_obs_per_window=0,
                max_obs_per_window=0,
                median_obs_per_window=0.0,
                variance=0.0,
                cv=0.0,
                window_balance=0.0,
                activity_class=p_data.get("activity_class", "moderate"),
                scale=p_data.get("scale", "medium"),
                volatility=p_data.get("volatility", "stable"),
                metrics_available=tuple(p_data.get("metrics_available", [])),
                time_span_days=p_data.get("time_span_days", 0),
                m02_observation_count=0,
            )

            # Plan
            plan_data = sd_data.get("plan", {})
            chosen = StrategyCandidate(
                strategy=plan_data.get("chosen_strategy", "temporal"),
                window_size=plan_data.get("chosen_window_size", 30),
                score=plan_data.get("chosen_score", 0.0),
                expected_windows=plan_data.get("expected_windows", 0),
                expected_obs_per_window=plan_data.get("expected_obs_per_window", 0.0),
            )
            plan = SamplingPlan(
                chosen=chosen,
                scientific_confidence=plan_data.get("scientific_confidence", "low"),
                selection_rationale=plan_data.get("selection_rationale", ""),
                profile=profile,
                prediction_error=plan_data.get("prediction_error", 0.0),
                window_difference=plan_data.get("window_difference", 0),
            )

            # Readiness
            readiness_data = sd_data.get("readiness", {})
            readiness = ReadinessReport(
                overall_state=readiness_data.get("overall_state", "SKIPPED"),
                ready_count=readiness_data.get("ready_count", 0),
                partial_count=readiness_data.get("partial_count", 0),
                skipped_count=readiness_data.get("skipped_count", 0),
            )

            # Window summary
            ws = sd_data.get("window_summary", {})

            return SamplingDiagnostics(
                profile=profile,
                plan=plan,
                readiness=readiness,
                strategy_used=ws.get("strategy_used", ""),
                total_windows=ws.get("total_windows", 0),
                total_observations=ws.get("total_observations", 0),
                unassigned_observations=ws.get("unassigned_observations", 0),
                warnings=sd_data.get("warnings", []),
            )

        except Exception as e:
            logger.warning("Failed to load diagnostics from %s: %s", json_path, e)
            return None
