"""
MIIE CLI — Measurement Integrity Intelligence Engine.

Commands:
    miie analyze    Run the full analysis pipeline on a repository
    miie ingest     Validate and ingest a repository
    miie detect     Run detectors on a repository
    miie benchmark  Execute a benchmark suite
    miie evaluate   Evaluate benchmark results against ground truth
    miie explain    Generate explanations from analysis
    miie export     Export results in specified formats
    miie generate   Generate synthetic benchmark candidates
    miie status     Show system status
    miie validate   Validate config file or analysis output

Exit codes (AFD §9.2, TFS §13.7):
    0 - Success (IS=1.0, no failures)
    1 - Integrity failures detected (IS<1.0)
    2 - System error (pipeline crashes, file not found, etc.)
    3 - Invalid arguments (bad CLI args, validation failure)
    4 - Benchmark failure
"""

import sys
import json as _json
import click
from pathlib import Path
from datetime import datetime, timezone

# Load .env file before anything else (secrets never in code)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed; rely on shell env vars only

from . import __version__


@click.group()
@click.version_option(version=__version__)
@click.option("--config", "-c", "config_file", type=click.Path(exists=True),
              default=None, help="Path to configuration file (YAML/JSON).")
@click.option("--output", "-o", "global_output", type=click.Path(),
              default=None, help="Global output directory.")
@click.option("--verbose", "-V", is_flag=True, default=False,
              help="Enable verbose output.")
@click.pass_context
def cli(ctx, config_file, global_output, verbose):
    """Measurement Integrity Intelligence Engine (MIIE)."""
    ctx.ensure_object(dict)
    ctx.obj["config_file"] = config_file
    ctx.obj["global_output"] = global_output
    ctx.obj["verbose"] = verbose


# ---------------------------------------------------------------------------
# miie analyze
# ---------------------------------------------------------------------------
@cli.command()
@click.argument("repo_path", type=str)
@click.option("--metrics", "-m", multiple=True, default=["M-02", "M-06"],
               help="Metric IDs to extract (repeatable). Default: M-02 M-06")
@click.option("--detectors", "-d", multiple=True, default=["D-01", "D-02", "D-03"],
               help="Detector IDs to enable (repeatable). Default: D-01 D-02 D-03")
@click.option("--output-dir", "-o", default="./output", help="Output directory for reports. Default: ./output")
@click.option("--window-strategy", "-w", default="time",
               type=click.Choice(["time", "commit", "release", "custom"]),
               help="Window segmentation strategy. Default: time")
@click.option("--window-size", "-s", default=7, type=int,
               help="Window size in days/commits. Default: 7")
@click.option("--since", default=None, help="Extract metrics since (ISO 8601)")
@click.option("--until", default=None, help="Extract metrics until (ISO 8601)")
@click.option("--exclude-bots", is_flag=True, help="Exclude bot-generated commits")
@click.option("--thresholds", default=None, type=str,
               help="Custom detector thresholds as JSON string, e.g. '{\"D-01\": {\"alpha\": 0.05}}'")
@click.option("--dry-run", is_flag=True,
               help="Validate inputs and show plan without executing the pipeline")
@click.option("--seed", default=42, type=int, help="Random seed for reproducibility. Default: 42")
@click.option("--format", "-f", "formats", multiple=True, default=["json"],
              type=click.Choice(["json", "md", "csv"]),
              help="Output format(s). Default: json")
@click.option("--auth-token", default=None, type=str,
              help="GitHub personal access token for private repos. Falls back to GITHUB_TOKEN env var.")
@click.option("--forensic", is_flag=True, default=False,
              help="Include full evidence package in output (advanced users).")
@click.option("--verbose", "-V", is_flag=True, default=False,
              help="Show detector IDs and timing details.")
@click.pass_context
def analyze(ctx, repo_path, metrics, detectors, output_dir, window_strategy,
             window_size, since, until, exclude_bots, thresholds, dry_run, seed, formats, auth_token, forensic, verbose):
    """Run the full analysis pipeline on a repository.

    Example:
        miie analyze ./my-repo --dry-run
        miie analyze ./my-repo -m M-02 -m M-06 -d D-01 -d D-02
        miie analyze ./my-repo --thresholds '{"D-01": {"alpha": 0.05}}'
        miie analyze https://github.com/pallets/flask --dry-run
        miie analyze ./my-repo --verbose
        miie analyze ./my-repo --forensic --format json --format md
    """
    from .contracts.validators import validate_cli_analyze_inputs, ValidationError
    from .schemas.serialization import json_dumps
    from .utils.git import GitURLParser

    # Parse thresholds JSON
    detector_config = None
    if thresholds:
        try:
            detector_config = _json.loads(thresholds)
        except _json.JSONDecodeError as exc:
            click.echo(f"[INVALID-INPUT] --thresholds must be valid JSON: {exc}", err=True)
            sys.exit(3)

    # --- Input validation (exit 3: invalid arguments) ---
    try:
        validate_cli_analyze_inputs(
            repo_path=repo_path,
            since=since,
            until=until,
            metrics=list(metrics),
            window_strategy=window_strategy,
            window_size=window_size,
            output_dir=Path(output_dir),
            detectors=list(detectors),
            format=list(formats),
            exclude_bots=exclude_bots,
        )
    except ValidationError as exc:
        click.echo(f"[INVALID-INPUT] {exc}", err=True)
        sys.exit(3)

    # Command-level --verbose overrides parent group --verbose
    verbose = verbose or ctx.obj.get("verbose", False)

    # --- Dry-run mode ---
    if dry_run:
        click.echo("=== MIIE Dry Run ===")
        click.echo(f"  Repository : {repo_path}")
        click.echo(f"  Metrics    : {', '.join(metrics)}")
        click.echo(f"  Detectors  : {', '.join(detectors)}")
        click.echo(f"  Window     : strategy={window_strategy} size={window_size}")
        click.echo(f"  Time range : since={since or '(none)'}  until={until or '(none)'}")
        click.echo(f"  Exclude bots: {exclude_bots}")
        if detector_config:
            click.echo(f"  Thresholds : {_json.dumps(detector_config)}")
        click.echo(f"  Output dir : {output_dir}")
        click.echo(f"  Formats    : {', '.join(formats)}")
        click.echo(f"  Seed       : {seed}")
        click.echo("  Validation : PASSED")
        click.echo("=== Pipeline would execute 8 stages ===")
        click.echo("  1. Ingestion  2. Extraction  3. Segmentation  4. Detection")
        click.echo("  5. Scoring    6. Evidence    7. Explanation   8. Reporting")
        click.echo("=== Dry run complete (no work performed) ===")
        return

    # --- Full pipeline execution with progress ---
    import time
    from . import __version__

    # Resolve auth token: CLI arg > env var
    import os
    resolved_token = auth_token or os.environ.get("GITHUB_TOKEN")

    # Detect if URL for clone messaging
    from .utils.git import GitURLParser
    is_url = GitURLParser.is_github_url(repo_path)
    display_name = repo_path if is_url else str(Path(repo_path).resolve())

    # --- Progress helper ---
    total_stages = 7
    _timings = {}

    def _progress_start(stage_num, label):
        click.echo(f"\n[{stage_num}/{total_stages}] {label}")

    def _progress_complete(stage_num, label, start_time):
        elapsed = time.perf_counter() - start_time
        _timings[label] = elapsed
        click.echo(f"      [DONE] ({elapsed:.1f}s)")

    def _progress_action(msg):
        click.echo(f"      {msg}")

    # --- Banner ---
    click.echo("")
    click.echo("=" * 55)
    click.echo(f"  MIIE v{__version__}")
    click.echo("  Measurement Integrity Analysis")
    click.echo("=" * 55)
    click.echo("")
    click.echo(f"  Repository:  {display_name}")

    from .processing.ingestion import RepositoryIngestionEngine
    from .processing.extraction import MetricExtractionEngine
    from .processing.segmentation import WindowSegmentationEngine
    from .processing.detection.dispatcher import DetectorDispatcherEngine
    from .processing.detection.registry import DetectorRegistry
    from .processing.detection.distribution_drift_detector import DistributionDriftDetector
    from .processing.detection.correlation_breakdown_detector import CorrelationBreakdownDetector
    from .processing.detection.threshold_compression_detector import ThresholdCompressionDetector
    from .processing.scoring.engine import ScoringEngine
    from .processing.evidence import EvidenceEngine
    from .processing.explanation.engine import ExplanationEngine
    from .processing.reporting.engine import ReportGenerator

    # Wrap entire pipeline in try/except for clean error handling (exit 2)
    try:
        _run_pipeline(
            repo_path=repo_path, display_name=display_name, is_url=is_url,
            resolved_token=resolved_token, metrics=metrics, since=since, until=until,
            exclude_bots=exclude_bots, window_strategy=window_strategy,
            window_size=window_size, detectors=detectors, thresholds=thresholds,
            formats=formats, output_dir=output_dir, verbose=verbose, forensic=forensic,
            _progress_start=_progress_start, _progress_complete=_progress_complete,
            _progress_action=_progress_action, _timings=_timings,
            total_stages=total_stages, __version__=__version__,
        )
    except Exception as exc:
        click.echo(f"\n[SYSTEM-ERROR] {exc}", err=True)
        try:
            partial_path = Path(output_dir) / "partial_results.json"
            partial_path.parent.mkdir(parents=True, exist_ok=True)
            partial_path.write_text(_json.dumps(
                {"error": str(exc), "partial": True}, default=str, indent=2
            ))
            click.echo(f"Partial results saved to {partial_path}", err=True)
        except Exception:
            pass
        sys.exit(2)


def _filter_sensitive_fields(obj):
    """Remove internal IDs and paths from JSON output for default mode.

    Removes: repo_id, run_id, local_path, temp_path
    Preserves: all scientific results, scores, detector outputs, explanations
    """
    _SENSITIVE_KEYS = {"repo_id", "run_id", "local_path", "temp_path"}
    if isinstance(obj, dict):
        keys_to_remove = [k for k in obj if k in _SENSITIVE_KEYS]
        for k in keys_to_remove:
            del obj[k]
        for v in obj.values():
            _filter_sensitive_fields(v)
    elif isinstance(obj, list):
        for item in obj:
            _filter_sensitive_fields(item)


def _run_pipeline(
    repo_path, display_name, is_url, resolved_token, metrics, since, until,
    exclude_bots, window_strategy, window_size, detectors, thresholds,
    formats, output_dir, verbose, forensic,
    _progress_start, _progress_complete, _progress_action, _timings,
    total_stages, __version__,
):
    """Execute all pipeline stages with progress feedback."""
    import time
    from .processing.ingestion import RepositoryIngestionEngine
    from .processing.extraction import MetricExtractionEngine
    from .processing.segmentation import WindowSegmentationEngine
    from .processing.detection.dispatcher import DetectorDispatcherEngine
    from .processing.detection.registry import DetectorRegistry
    from .processing.detection.distribution_drift_detector import DistributionDriftDetector
    from .processing.detection.correlation_breakdown_detector import CorrelationBreakdownDetector
    from .processing.detection.threshold_compression_detector import ThresholdCompressionDetector
    from .processing.scoring.engine import ScoringEngine
    from .processing.evidence import EvidenceEngine
    from .processing.explanation.engine import ExplanationEngine
    from .processing.reporting.engine import ReportGenerator

    # --- Stage 1: Acquisition ---
    t_total = time.perf_counter()
    _progress_start(1, "Repository Acquisition")
    t1 = time.perf_counter()
    ingestion = RepositoryIngestionEngine(auth_token=resolved_token)
    if is_url:
        _progress_action("Cloning repository...")
    else:
        _progress_action("Loading local repository...")
    repository_context = ingestion.ingest(
        repo_path=repo_path,
        shallow_depth=None,
    )
    if not ingestion.validate(repository_context):
        raise ValueError("Repository context validation failed")
    total_commits = getattr(repository_context, "total_commits", "?")
    contributor_count = getattr(repository_context, "contributor_count", "?")
    first_commit = getattr(repository_context, "first_commit_date", None)
    last_commit = getattr(repository_context, "last_commit_date", None)
    remote_url = getattr(repository_context, "remote_url", None) or display_name
    _progress_action(f"{total_commits} commits, {contributor_count} contributors")
    _progress_complete(1, "Acquisition", t1)

    # --- Stage 2: Validation ---
    _progress_start(2, "Repository Validation")
    t2 = time.perf_counter()
    _progress_action("Validating repository metadata...")
    _progress_complete(2, "Validation", t2)

    # --- Stage 3: Metric Extraction ---
    _progress_start(3, "Metric Extraction")
    t3 = time.perf_counter()
    extraction = MetricExtractionEngine()
    since_dt = datetime.fromisoformat(since) if since else None
    until_dt = datetime.fromisoformat(until) if until else None
    _progress_action(f"Extracting {', '.join(metrics)}...")
    metric_dataframe = extraction.extract(
        context=repository_context,
        metric_list=list(metrics),
        since=since_dt,
        until=until_dt,
        exclude_bots=exclude_bots,
    )
    metric_names = list(getattr(metric_dataframe, "metrics", {}).keys()) if metric_dataframe else list(metrics)
    _progress_action(f"{len(metric_names)} metrics extracted")
    _progress_complete(3, "Extraction", t3)

    # --- Stage 4: Window Generation ---
    _progress_start(4, "Window Generation")
    t4 = time.perf_counter()
    segmentation = WindowSegmentationEngine()
    windows = segmentation.segment(
        metric_dataframe=metric_dataframe,
        strategy=window_strategy,
        size=window_size,
        repository_context=repository_context,
    )
    window_count = len(windows)
    _progress_action(f"{window_count} windows ({window_strategy}, size={window_size})")
    _progress_complete(4, "Segmentation", t4)

    # --- Stage 5: Detector Execution ---
    _progress_start(5, "Detector Execution")
    t5 = time.perf_counter()
    registry = DetectorRegistry()
    registry.register(DistributionDriftDetector())
    registry.register(CorrelationBreakdownDetector())
    registry.register(ThresholdCompressionDetector())
    dispatcher = DetectorDispatcherEngine(registry)
    detector_config = None
    if thresholds:
        try:
            detector_config = _json.loads(thresholds)
        except _json.JSONDecodeError:
            detector_config = None
    _progress_action(f"Running {len(detectors)} detectors...")
    detector_results = dispatcher.invoke(
        metric_dataframe=metric_dataframe,
        windows=windows,
        detector_config=detector_config,
        enabled_detectors=list(detectors),
    )
    _progress_complete(5, "Detection", t5)

    # --- Stage 6: Evidence Generation ---
    _progress_start(6, "Evidence Generation")
    t6 = time.perf_counter()
    scoring = ScoringEngine()
    score_package = scoring.compute_integrity_score(
        detector_results=detector_results,
        metric_dataframe=metric_dataframe,
        windows=windows,
    )
    evidence_engine = EvidenceEngine()
    evidence_package = evidence_engine.generate(
        repository_context=repository_context,
        metric_dataframe=metric_dataframe,
        windows=windows,
        detector_results=detector_results,
        score_package=score_package,
        configuration={
            "metric_list": list(metrics),
            "since": since_dt,
            "until": until_dt,
            "exclude_bots": exclude_bots,
            "segmentation_strategy": window_strategy,
            "segmentation_size": window_size,
        },
    )
    explanation_engine = ExplanationEngine()
    explanation_report = explanation_engine.generate(
        evidence_package=evidence_package,
        score_package=score_package,
    )
    _progress_complete(6, "Evidence", t6)

    # --- Stage 7: Final Assessment ---
    _progress_start(7, "Final Assessment")
    t7 = time.perf_counter()
    report_generator = ReportGenerator()
    analysis_results = {
        "repository_context": repository_context,
        "metric_dataframe": metric_dataframe,
        "windows": windows,
        "detector_results": detector_results,
        "score_package": score_package,
        "evidence_package": evidence_package,
        "explanation_report": explanation_report,
    }

    # --- Privacy filtering (default mode hides internal IDs) ---
    if not forensic:
        from .schemas.serialization import json_dumps
        # Serialize, filter, re-parse to remove sensitive fields
        serialized = report_generator._serialize_for_json(analysis_results)
        _filter_sensitive_fields(serialized)
        analysis_results = serialized

    report_output = report_generator.generate(
        analysis_result=analysis_results,
        output_formats=list(formats),
        output_dir=Path(output_dir),
    )
    _progress_complete(7, "Reporting", t7)

    t_total_elapsed = time.perf_counter() - t_total

    # --- Extract scores ---
    integrity = score_package.integrity
    confidence = score_package.confidence
    integrity_overall = integrity.get("overall", 0.0) if isinstance(integrity, dict) else integrity.overall
    confidence_overall = confidence.get("overall", 0.0) if isinstance(confidence, dict) else confidence.overall

    # --- Extract detector results ---
    detector_outputs = {}
    if detector_results:
        detector_outputs = getattr(detector_results, "detector_outputs", {})
        if not detector_outputs and hasattr(detector_results, "d_01"):
            detector_outputs = {
                "D-01": getattr(detector_results, "d_01", {}),
                "D-02": getattr(detector_results, "d_02", {}),
                "D-03": getattr(detector_results, "d_03", {}),
            }

    # --- Extract explanation ---
    narratives = getattr(explanation_report, "narratives", []) if explanation_report else []
    recommendations = getattr(explanation_report, "recommendations", []) if explanation_report else []

    # ============================================================
    # FINAL TERMINAL REPORT (3-tier output)
    # ============================================================

    # --- Risk Classification (Phase 8) ---
    triggered_count = sum(
        1 for det_id, det_data in detector_outputs.items()
        if isinstance(det_data, dict) and (
            det_data.get("drift_detected") or
            det_data.get("breakdown_detected") or
            det_data.get("compression_detected", False)
        )
    )
    if triggered_count == 0:
        risk_level = "Very Low"
    elif triggered_count == 1:
        risk_level = "Low"
    elif triggered_count == 2:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    # --- Confidence Label ---
    if confidence_overall >= 0.9:
        confidence_label = "Very High"
    elif confidence_overall >= 0.7:
        confidence_label = "High"
    elif confidence_overall >= 0.5:
        confidence_label = "Moderate"
    else:
        confidence_label = "Low"

    # --- Integrity Label ---
    if integrity_overall >= 0.9:
        integrity_label = "Very High"
    elif integrity_overall >= 0.7:
        integrity_label = "High"
    elif integrity_overall >= 0.5:
        integrity_label = "Moderate"
    else:
        integrity_label = "Low"

    # --- Confidence Explanation (Phase 7) ---
    confidence_factors = {}
    if isinstance(confidence, dict):
        confidence_factors = confidence.get("factors", {})
    elif hasattr(confidence, 'factors'):
        confidence_factors = confidence.factors if isinstance(confidence.factors, dict) else {}

    sample_size_f = confidence_factors.get("sample_size", 1.0)
    variance_f = confidence_factors.get("variance", 1.0)
    missing_data_f = confidence_factors.get("missing_data", 1.0)
    window_balance_f = confidence_factors.get("window_balance", 1.0)
    detector_success_f = confidence_factors.get("detector_success", 1.0)

    confidence_reasons = []
    if sample_size_f < 0.5:
        confidence_reasons.append(
            f"Only {len(windows)} analysis window(s) could be constructed "
            f"(sample factor: {sample_size_f:.2f})"
        )
    if variance_f < 0.8:
        confidence_reasons.append("High variance in metric values across windows")
    if missing_data_f < 0.8:
        confidence_reasons.append("Some metric-window data pairs are missing")
    if window_balance_f < 0.8:
        confidence_reasons.append("Analysis windows are unevenly sized")
    if detector_success_f < 0.8:
        confidence_reasons.append("Some detectors failed to produce results")

    if not confidence_reasons:
        if confidence_overall >= 0.9:
            confidence_reasons.append("Sufficient data and detector coverage for high confidence")
        elif confidence_overall >= 0.5:
            confidence_reasons.append("Adequate data, though more analysis windows would improve confidence")
        else:
            confidence_reasons.append("Limited analysis windows reduce confidence in results")

    # --- One-Sentence Summary (Phase 9) ---
    if triggered_count == 0 and integrity_overall >= 0.9:
        summary_sentence = (
            "No evidence was found that repository metrics have become "
            "distorted, unstable, or misleading."
        )
    elif triggered_count == 0 and integrity_overall >= 0.7:
        summary_sentence = (
            "Repository metrics appear generally stable with minor variations "
            "that are within expected ranges."
        )
    elif triggered_count == 1:
        summary_sentence = (
            "One metric anomaly was detected, but overall measurement "
            "integrity remains acceptable."
        )
    else:
        summary_sentence = (
            "Multiple metric anomalies were detected. Manual investigation "
            "of repository measurement integrity is recommended."
        )

    # --- Banner ---
    click.echo("")
    click.echo("=" * 55)
    click.echo(f"  MIIE v{__version__}")
    click.echo("  Measurement Integrity Analysis")
    click.echo("=" * 55)
    click.echo("")
    click.echo(f"  Repository:  {remote_url}")
    click.echo("")

    # --- Analysis Coverage (Phase 3) ---
    click.echo("  Analysis Coverage")
    click.echo("  " + "-" * 40)
    click.echo(f"  {total_commits} commits from {contributor_count} contributors")
    if first_commit and last_commit:
        click.echo(f"  {first_commit.strftime('%Y-%m-%d')} to {last_commit.strftime('%Y-%m-%d')}")
    click.echo(f"  {len(windows)} analysis window(s) ({window_strategy}, size={window_size})")
    click.echo(f"  {len(detectors)} detector(s) executed")
    click.echo("")

    # --- Integrity Findings ---
    click.echo("  Integrity Findings")
    click.echo("  " + "-" * 40)

    _detector_human = {
        "D-01": "No significant metric drift detected",
        "D-02": "Historical metric relationships remain stable",
        "D-03": "No threshold compression patterns detected",
    }
    _detector_triggered_human = {
        "D-01": "Significant metric drift detected",
        "D-02": "Historical metric relationships have shifted",
        "D-03": "Threshold compression patterns detected",
    }

    for det_id in sorted(detector_outputs.keys()):
        det_data = detector_outputs[det_id]
        if isinstance(det_data, dict):
            triggered = det_data.get("drift_detected") or det_data.get("breakdown_detected") or det_data.get("compression_detected", False)
        else:
            triggered = False

        if verbose or forensic:
            status = "FAIL" if triggered else "PASS"
            click.echo(f"  [{det_id}] {status}")
        else:
            if triggered:
                click.echo(f"  [X]  {_detector_triggered_human.get(det_id, 'Issue detected')}")
            else:
                click.echo(f"  [OK]  {_detector_human.get(det_id, 'Check passed')}")

    click.echo("")

    # --- Confidence Explanation (Phase 7) ---
    click.echo("  Confidence")
    click.echo("  " + "-" * 40)
    click.echo(f"  Level:  {confidence_label}")
    click.echo(f"  Reason: {'; '.join(confidence_reasons)}")
    click.echo("")

    # --- Risk Assessment (Phase 8) ---
    click.echo("  Risk Assessment")
    click.echo("  " + "-" * 40)
    click.echo(f"  Risk Level:  {risk_level}")
    if triggered_count > 0:
        click.echo(f"  Findings:    {triggered_count} anomaly(ies) detected")
    else:
        click.echo(f"  Findings:    No anomalies detected")
    click.echo("")

    # --- Overall Verdict ---
    click.echo("  Overall Verdict")
    click.echo("  " + "-" * 40)
    click.echo(f"  Metric Integrity:  {integrity_label}")
    click.echo(f"  Confidence:        {confidence_label}")
    click.echo(f"  Risk:              {risk_level}")
    click.echo("")

    # --- One-Sentence Summary (Phase 9) ---
    click.echo("  Summary")
    click.echo("  " + "-" * 40)
    click.echo(f"  {summary_sentence}")
    click.echo("")

    # --- Recommended Action ---
    click.echo("  Recommended Action")
    click.echo("  " + "-" * 40)
    if triggered_count == 0 and integrity_overall >= 0.9:
        action = "No action required. Repository metrics appear trustworthy."
    elif triggered_count == 0:
        action = "No immediate action. Consider analyzing a longer time range for higher confidence."
    elif triggered_count == 1:
        action = "Review the flagged metric for context. Monitor for continued anomalies."
    else:
        action = "Investigate flagged metrics. Review contributor activity and development patterns."
    click.echo(f"  {action}")
    click.echo("")

    # --- Timing (verbose only) ---
    if verbose or forensic:
        click.echo("  Stage Timing")
        click.echo("  " + "-" * 40)
        for label, elapsed in _timings.items():
            click.echo(f"    {label}: {elapsed:.2f}s")
        click.echo(f"    Total: {t_total_elapsed:.2f}s")
        click.echo("")

    # --- Forensic details (forensic only) ---
    if forensic:
        click.echo("  Forensic Details")
        click.echo("  " + "-" * 40)
        click.echo(f"  Window Count:    {len(windows)}")
        for w in windows:
            wid = getattr(w, 'window_id', '?')
            sd = getattr(w, 'start_date', '?')
            ed = getattr(w, 'end_date', '?')
            clicks_count = getattr(w, 'commits', '?')
            click.echo(f"    {wid}: {sd} to {ed} ({clicks_count} commits)")
        click.echo(f"  Metrics:         {', '.join(metrics)}")
        click.echo(f"  Detectors:       {', '.join(detectors)}")
        click.echo(f"  Window Strategy: {window_strategy}")
        click.echo(f"  Window Size:     {window_size}")
        click.echo(f"  Seed:            42")
        click.echo("")

    # --- Reports ---
    report_out = report_output
    if report_out and report_out.report_paths:
        click.echo("  Reports Saved:")
        click.echo("  " + "-" * 40)
        for fmt, path in report_out.report_paths.items():
            click.echo(f"    {fmt}: {path}")
    click.echo("")

    # --- Footer ---
    click.echo("=" * 55)
    click.echo("  Analysis Complete")
    click.echo("=" * 55)
    click.echo("")

    # Exit 1 if integrity score < 1.0 (integrity failures detected)
    if integrity_overall < 1.0:
        sys.exit(1)


# ---------------------------------------------------------------------------
# miie ingest
# ---------------------------------------------------------------------------
@cli.command()
@click.argument("repo_path", type=str)
@click.option("--shallow", type=int, default=None, help="Shallow clone depth")
@click.option("--auth-token", default=None, type=str,
              help="GitHub personal access token for private repos. Falls back to GITHUB_TOKEN env var.")
@click.pass_context
def ingest(ctx, repo_path, shallow, auth_token):
    """Validate and ingest a repository (checks Git validity)."""
    from .contracts.validators import validate_cli_ingest_inputs, ValidationError
    from .utils.git import GitURLParser

    # Check if repo_path is a GitHub URL
    if GitURLParser.is_github_url(repo_path):
        click.echo(f"[INFO] GitHub URL detected: {repo_path}")
        click.echo(f"[INFO] Cloning repository...")
    
    try:
        validate_cli_ingest_inputs(repo_path, shallow=shallow)
    except ValidationError as exc:
        click.echo(f"[INVALID-INPUT] {exc}", err=True)
        sys.exit(3)

    # Resolve auth token: CLI arg > env var
    import os
    resolved_token = auth_token or os.environ.get("GITHUB_TOKEN")

    from .processing.ingestion import RepositoryIngestionEngine

    engine = RepositoryIngestionEngine(auth_token=resolved_token)
    try:
        ctx_result = engine.ingest(repo_path=repo_path, shallow_depth=shallow)
        click.echo(f"Ingestion successful.")
        click.echo(f"  Repo ID    : {ctx_result.repo_id}")
        click.echo(f"  Commits    : {ctx_result.total_commits}")
        click.echo(f"  Contributors: {ctx_result.contributor_count}")
        click.echo(f"  Local path : {ctx_result.local_path}")
    except Exception as exc:
        click.echo(f"[SYSTEM-ERROR] {exc}", err=True)
        sys.exit(2)


# ---------------------------------------------------------------------------
# miie detect
# ---------------------------------------------------------------------------
@cli.command()
@click.argument("repo_path", type=str)
@click.option("--metrics", "-m", multiple=True, default=["M-02", "M-06"],
               help="Metric IDs to extract (repeatable).")
@click.option("--detectors", "-d", multiple=True, default=["D-01", "D-02", "D-03"],
               help="Detector IDs to enable (repeatable).")
@click.option("--seed", default=42, type=int, help="Random seed.")
@click.option("--auth-token", default=None, type=str,
              help="GitHub personal access token for private repos. Falls back to GITHUB_TOKEN env var.")
@click.pass_context
def detect(ctx, repo_path, metrics, detectors, seed, auth_token):
    """Run detection on a repository (ingestion + extraction + detection only)."""
    from .utils.git import GitURLParser

    # Check if repo_path is a GitHub URL
    if GitURLParser.is_github_url(repo_path):
        click.echo(f"[INFO] GitHub URL detected: {repo_path}")
        click.echo(f"[INFO] Cloning repository...")

    # Resolve auth token: CLI arg > env var
    import os
    resolved_token = auth_token or os.environ.get("GITHUB_TOKEN")

    from .processing.ingestion import RepositoryIngestionEngine
    from .processing.extraction import MetricExtractionEngine
    from .processing.segmentation import WindowSegmentationEngine
    from .processing.detection.dispatcher import DetectorDispatcherEngine
    from .processing.detection.registry import DetectorRegistry

    registry = DetectorRegistry()
    from .processing.detection.distribution_drift_detector import DistributionDriftDetector
    from .processing.detection.correlation_breakdown_detector import CorrelationBreakdownDetector
    from .processing.detection.threshold_compression_detector import ThresholdCompressionDetector
    registry.register(DistributionDriftDetector())
    registry.register(CorrelationBreakdownDetector())
    registry.register(ThresholdCompressionDetector())

    click.echo(f"Running detection on {repo_path} ...")
    try:
        ctx_ingested = RepositoryIngestionEngine(auth_token=resolved_token).ingest(repo_path)
        mdf = MetricExtractionEngine().extract(ctx_ingested, list(metrics))
        wins = WindowSegmentationEngine().segment(mdf, strategy="time", size=7)
        results = DetectorDispatcherEngine(registry).invoke(mdf, wins)
        click.echo(f"Detection complete. {len(results.detector_outputs)} detector(s) ran:")
        for det_id, output in results.detector_outputs.items():
            click.echo(f"  {det_id}: {list(output.keys()) if isinstance(output, dict) else type(output).__name__}")
    except Exception as exc:
        click.echo(f"[SYSTEM-ERROR] {exc}", err=True)
        sys.exit(2)


# ---------------------------------------------------------------------------
# miie benchmark
# ---------------------------------------------------------------------------
@cli.command()
@click.option("--suite", "-s", required=True, help="Benchmark suite ID (e.g. B-01)")
@click.option("--detectors", "-d", multiple=True, default=["D-01", "D-02", "D-03"],
              help="Detector IDs to benchmark.")
@click.option("--config", "-cfg", default=None, help="JSON config string.")
@click.option("--seed", default=42, type=int, help="Random seed.")
@click.pass_context
def benchmark(ctx, suite, detectors, config, seed):
    """Execute a benchmark suite against detectors."""
    from .processing.benchmark.engine import BenchmarkEngine

    cfg = _json.loads(config) if config else {"threshold": 0.05}
    click.echo(f"Running benchmark suite {suite} ...")
    try:
        engine = BenchmarkEngine()
        result = engine.execute(suite_id=suite, detector_ids=list(detectors), config=cfg, seed=seed)
        click.echo(f"Benchmark complete. Metadata: {result.metadata}")
    except Exception as exc:
        click.echo(f"[BENCHMARK-ERROR] {exc}", err=True)
        sys.exit(4)


# ---------------------------------------------------------------------------
# miie evaluate
# ---------------------------------------------------------------------------
@cli.command()
@click.option("--benchmark-json", "-b", required=True, type=click.Path(exists=True),
              help="Path to BenchmarkRun JSON file.")
@click.option("--ground-truth", "-g", required=True, type=click.Path(exists=True),
              help="Path to ground truth JSON file.")
@click.pass_context
def evaluate(ctx, benchmark_json, ground_truth):
    """Evaluate benchmark results against ground truth."""
    from .schemas.models import BenchmarkRun
    from .processing.evaluation.engine import EvaluationEngine

    click.echo(f"Evaluating benchmark ...")
    try:
        with open(benchmark_json) as f:
            br_data = _json.load(f)
        benchmark_run = BenchmarkRun(
            predictions=br_data.get("predictions", {}),
            metadata=br_data.get("metadata", {})
        )
        with open(ground_truth) as f:
            gt_data = _json.load(f)
        result = EvaluationEngine().evaluate(benchmark_run, gt_data)
        click.echo(f"  Accuracy : {result.accuracy:.4f}")
        click.echo(f"  F1 Score : {result.f1_score:.4f}")
        click.echo(f"  Precision: {result.precision:.4f}")
        click.echo(f"  Recall   : {result.recall:.4f}")
    except Exception as exc:
        click.echo(f"[SYSTEM-ERROR] {exc}", err=True)
        sys.exit(2)


# ---------------------------------------------------------------------------
# miie explain
# ---------------------------------------------------------------------------
@cli.command()
@click.argument("repo_path", type=click.Path(exists=True))
@click.option("--metrics", "-m", multiple=True, default=["M-02", "M-06"])
@click.option("--metric-filter", default=None, help="Specific metric to explain.")
@click.option("--detector-filter", default=None, help="Specific detector to explain.")
@click.option("--seed", default=42, type=int)
@click.pass_context
def explain(ctx, repo_path, metrics, metric_filter, detector_filter, seed):
    """Run analysis and generate explanation report."""
    from .processing.ingestion import RepositoryIngestionEngine
    from .processing.extraction import MetricExtractionEngine
    from .processing.segmentation import WindowSegmentationEngine
    from .processing.detection.dispatcher import DetectorDispatcherEngine
    from .processing.detection.registry import DetectorRegistry
    from .processing.scoring.engine import ScoringEngine
    from .processing.evidence import EvidenceEngine
    from .processing.explanation.engine import ExplanationEngine

    registry = DetectorRegistry()
    from .processing.detection.distribution_drift_detector import DistributionDriftDetector
    from .processing.detection.correlation_breakdown_detector import CorrelationBreakdownDetector
    from .processing.detection.threshold_compression_detector import ThresholdCompressionDetector
    registry.register(DistributionDriftDetector())
    registry.register(CorrelationBreakdownDetector())
    registry.register(ThresholdCompressionDetector())

    click.echo(f"Running analysis and explanation on {repo_path} ...")
    try:
        ctx_ingested = RepositoryIngestionEngine().ingest(repo_path)
        mdf = MetricExtractionEngine().extract(ctx_ingested, list(metrics))
        wins = WindowSegmentationEngine().segment(mdf, strategy="time", size=7)
        det_results = DetectorDispatcherEngine(registry).invoke(mdf, wins)
        score_pkg = ScoringEngine().compute_integrity_score(det_results, mdf, wins)
        evidence = EvidenceEngine().generate(ctx_ingested, mdf, wins, det_results, score_pkg, {"seed": seed})
        explanation = ExplanationEngine().generate(evidence, score_pkg,
                                                   metric_filter=metric_filter,
                                                   detector_filter=detector_filter)
        click.echo(f"Explanation complete. {len(explanation.narratives)} narrative(s)")
        for i, n in enumerate(explanation.narratives, 1):
            click.echo(f"  {i}. {n}")
    except Exception as exc:
        click.echo(f"[SYSTEM-ERROR] {exc}", err=True)
        sys.exit(2)


# ---------------------------------------------------------------------------
# miie export
# ---------------------------------------------------------------------------
@cli.command()
@click.argument("repo_path", type=click.Path(exists=True))
@click.option("--formats", "-f", multiple=True, default=["json", "csv"],
              help="Export formats.")
@click.option("--output-dir", "-o", type=click.Path(), default="./export")
@click.option("--seed", default=42, type=int)
@click.pass_context
def export(ctx, repo_path, formats, output_dir, seed):
    """Run analysis and export results in specified formats."""
    from pathlib import Path as _P
    from .processing.ingestion import RepositoryIngestionEngine
    from .processing.extraction import MetricExtractionEngine
    from .processing.segmentation import WindowSegmentationEngine
    from .processing.detection.dispatcher import DetectorDispatcherEngine
    from .processing.detection.registry import DetectorRegistry
    from .processing.scoring.engine import ScoringEngine

    registry = DetectorRegistry()
    from .processing.detection.distribution_drift_detector import DistributionDriftDetector
    from .processing.detection.correlation_breakdown_detector import CorrelationBreakdownDetector
    from .processing.detection.threshold_compression_detector import ThresholdCompressionDetector
    registry.register(DistributionDriftDetector())
    registry.register(CorrelationBreakdownDetector())
    registry.register(ThresholdCompressionDetector())

    out = _P(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    click.echo(f"Exporting analysis of {repo_path} ...")
    try:
        ctx_ingested = RepositoryIngestionEngine().ingest(repo_path)
        mdf = MetricExtractionEngine().extract(ctx_ingested, ["M-02", "M-06"])
        wins = WindowSegmentationEngine().segment(mdf, strategy="time", size=7)
        det_results = DetectorDispatcherEngine(registry).invoke(mdf, wins)
        score_pkg = ScoringEngine().compute_integrity_score(det_results, mdf, wins)

        data = {
            "repo_id": ctx_ingested.repo_id,
            "integrity": score_pkg.integrity.overall,
            "confidence": score_pkg.confidence.overall,
        }
        exported = {}
        for fmt in formats:
            p = out / f"export.{fmt}"
            if fmt == "json":
                p.write_text(_json.dumps(data, indent=2))
            elif fmt == "csv":
                p.write_text("metric,value\n")
                for k, v in data.items():
                    p.write_text(f"{k},{v}\n")
            exported[fmt] = p
        click.echo(f"Exported to {out}:")
        for fmt, p in exported.items():
            click.echo(f"  {fmt}: {p}")
    except Exception as exc:
        click.echo(f"[SYSTEM-ERROR] {exc}", err=True)
        sys.exit(2)


# ---------------------------------------------------------------------------
# miie generate
# ---------------------------------------------------------------------------
@cli.command()
@click.option("--type", "-t", "dataset_type", default="metric-drift",
              help="Dataset type (metric-drift, correlation-breakdown, threshold-compression).")
@click.option("--count", "-n", default=5, type=int, help="Number of candidates to generate.")
@click.option("--output-dir", "-o", type=click.Path(), default="./benchmarks/generated")
@click.option("--seed", default=42, type=int)
@click.pass_context
def generate(ctx, dataset_type, count, output_dir, seed):
    """Generate synthetic benchmark candidates."""
    from pathlib import Path as _P
    from .benchmark.generator import BenchmarkDatasetGenerator

    click.echo(f"Generating {count} {dataset_type} candidates ...")
    try:
        gen = BenchmarkDatasetGenerator()
        paths = gen.generate(dataset_type, count, _P(output_dir), seed=seed)
        click.echo(f"Generated {len(paths)} candidate(s):")
        for p in paths:
            click.echo(f"  {p}")
    except Exception as exc:
        click.echo(f"[SYSTEM-ERROR] {exc}", err=True)
        sys.exit(2)


# ---------------------------------------------------------------------------
# miie status
# ---------------------------------------------------------------------------
@cli.command()
@click.pass_context
def status(ctx):
    """Show MIIE project and pipeline status."""
    click.echo(f"MIIE v{__version__}")

    engines = {
        "IngestionEngine":    ("miie.processing.ingestion", "RepositoryIngestionEngine"),
        "ExtractionEngine":   ("miie.processing.extraction", "MetricExtractionEngine"),
        "SegmentationEngine": ("miie.processing.segmentation", "WindowSegmentationEngine"),
        "ScoringEngine":      ("miie.processing.scoring.engine", "ScoringEngine"),
        "EvidenceEngine":     ("miie.processing.evidence", "EvidenceEngine"),
        "ExplanationEngine":  ("miie.processing.explanation.engine", "ExplanationEngine"),
        "ReportGenerator":    ("miie.processing.reporting.engine", "ReportGenerator"),
        "BenchmarkEngine":    ("miie.processing.benchmark.engine", "BenchmarkEngine"),
        "EvaluationEngine":   ("miie.processing.evaluation.engine", "EvaluationEngine"),
    }

    click.echo("Engine status:")
    for name, (mod_path, cls_name) in engines.items():
        try:
            mod = __import__(mod_path, fromlist=[cls_name])
            getattr(mod, cls_name)
            click.echo(f"  {name:25s} OK")
        except Exception:
            click.echo(f"  {name:25s} MISSING")

    click.echo("Detectors:")
    try:
        from .processing.detection.registry import DetectorRegistry
        from .processing.detection.distribution_drift_detector import DistributionDriftDetector
        from .processing.detection.correlation_breakdown_detector import CorrelationBreakdownDetector
        from .processing.detection.threshold_compression_detector import ThresholdCompressionDetector
        reg = DetectorRegistry()
        for det_cls in [DistributionDriftDetector, CorrelationBreakdownDetector, ThresholdCompressionDetector]:
            try:
                reg.register(det_cls())
            except Exception:
                pass
        click.echo(f"  Registered: {len(reg._detectors)} detector(s)")
    except Exception:
        click.echo("  Registry unavailable")

    config_file = ctx.obj.get("config_file")
    if config_file:
        click.echo(f"Config file: {config_file}")
    verbose = ctx.obj.get("verbose", False)
    if verbose:
        click.echo("Verbose mode: enabled")


# ---------------------------------------------------------------------------
# miie validate
# ---------------------------------------------------------------------------
@cli.command()
@click.argument("target", type=click.Path(exists=True))
@click.option("--type", "-t", "validate_type", default="config",
              type=click.Choice(["config", "analysis", "benchmark", "manifest"]),
              help="Type of artifact to validate. Default: config")
@click.pass_context
def validate(ctx, target, validate_type):
    """Validate a config file, analysis output, or benchmark artifact.

    Example:
        miie validate ./config.yaml --type config
        miie validate ./output/results.json --type analysis
    """
    target_path = Path(target)
    click.echo(f"Validating {target_path} (type={validate_type}) ...")

    try:
        if validate_type == "config":
            _validate_config(target_path)
        elif validate_type == "analysis":
            _validate_analysis(target_path)
        elif validate_type == "benchmark":
            _validate_benchmark(target_path)
        elif validate_type == "manifest":
            _validate_manifest(target_path)
        click.echo("Validation PASSED")
    except Exception as exc:
        click.echo(f"[VALIDATION-FAILED] {exc}", err=True)
        sys.exit(3)


def _validate_config(path: Path) -> None:
    """Validate a configuration file (YAML or JSON)."""
    import yaml
    content = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        data = yaml.safe_load(content)
    elif path.suffix == ".json":
        data = _json.loads(content)
    else:
        raise ValueError(f"Unsupported config format: {path.suffix}")

    if not isinstance(data, dict):
        raise ValueError("Config must be a JSON/YAML object")

    required_fields = {"repo"}
    missing = required_fields - set(data.keys())
    if missing:
        raise ValueError(f"Missing required fields: {missing}")


def _validate_analysis(path: Path) -> None:
    """Validate analysis output (results.json)."""
    data = _json.loads(path.read_text(encoding="utf-8"))
    required = {"score_package", "repository_context"}
    missing = required - set(data.keys())
    if missing:
        raise ValueError(f"Missing required fields in analysis output: {missing}")


def _validate_benchmark(path: Path) -> None:
    """Validate a benchmark run JSON file."""
    data = _json.loads(path.read_text(encoding="utf-8"))
    required = {"run_id", "suite_id", "detector_id", "predictions"}
    missing = required - set(data.keys())
    if missing:
        raise ValueError(f"Missing required fields in benchmark output: {missing}")


def _validate_manifest(path: Path) -> None:
    """Validate a manifest.json file."""
    data = _json.loads(path.read_text(encoding="utf-8"))
    required = {"miie_version", "python_version", "platform", "timestamp"}
    missing = required - set(data.keys())
    if missing:
        raise ValueError(f"Missing required fields in manifest: {missing}")


if __name__ == "__main__":
    cli()
