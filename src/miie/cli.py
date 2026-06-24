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
              type=click.Choice(["json", "markdown", "both"]),
              help="Output format(s). Default: json")
@click.option("--auth-token", default=None, type=str,
              help="GitHub personal access token for private repos. Falls back to GITHUB_TOKEN env var.")
@click.pass_context
def analyze(ctx, repo_path, metrics, detectors, output_dir, window_strategy,
             window_size, since, until, exclude_bots, thresholds, dry_run, seed, formats, auth_token):
    """Run the full analysis pipeline on a repository.

    Example:
        miie analyze ./my-repo --dry-run
        miie analyze ./my-repo -m M-02 -m M-06 -d D-01 -d D-02
        miie analyze ./my-repo --thresholds '{\"D-01\": {\"alpha\": 0.05}}'
        miie analyze https://github.com/pallets/flask --dry-run
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

    verbose = ctx.obj.get("verbose", False)

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

    # --- Full pipeline execution ---
    if verbose:
        click.echo(f"Starting analysis of {repo_path} ...")
    else:
        click.echo(f"Starting analysis of {repo_path} ...")

    # Resolve auth token: CLI arg > env var
    import os
    resolved_token = auth_token or os.environ.get("GITHUB_TOKEN")

    from .orchestration.pipeline import AnalysisPipeline
    from .processing.ingestion import RepositoryIngestionEngine
    from .processing.extraction import MetricExtractionEngine
    from .processing.segmentation import WindowSegmentationEngine
    from .processing.detection.dispatcher import DetectorDispatcherEngine
    from .processing.detection.registry import DetectorRegistry
    from .processing.scoring.engine import ScoringEngine
    from .processing.evidence import EvidenceEngine
    from .processing.explanation.engine import ExplanationEngine
    from .processing.reporting.engine import ReportGenerator

    # Build detector registry with real detectors
    registry = DetectorRegistry()
    from .processing.detection.distribution_drift_detector import DistributionDriftDetector
    from .processing.detection.correlation_breakdown_detector import CorrelationBreakdownDetector
    from .processing.detection.threshold_compression_detector import ThresholdCompressionDetector
    registry.register(DistributionDriftDetector())
    registry.register(CorrelationBreakdownDetector())
    registry.register(ThresholdCompressionDetector())

    pipeline = AnalysisPipeline(
        ingestion_engine=RepositoryIngestionEngine(auth_token=resolved_token),
        extraction_engine=MetricExtractionEngine(),
        segmentation_engine=WindowSegmentationEngine(),
        detection_engine=DetectorDispatcherEngine(registry),
        scoring_engine=ScoringEngine(),
        evidence_engine=EvidenceEngine(),
        explanation_engine=ExplanationEngine(),
        report_generator=ReportGenerator(),
    )

    # Parse time args
    since_dt = datetime.fromisoformat(since) if since else None
    until_dt = datetime.fromisoformat(until) if until else None

    # Track partial results for crash recovery (AFD §9.2)
    partial_results = {}
    try:
        results = pipeline.run_analysis(
            repo_path=repo_path,
            metric_list=list(metrics),
            output_formats=list(formats),
            output_dir=Path(output_dir),
            segmentation_strategy=window_strategy,
            segmentation_size=window_size,
            since=since_dt,
            until=until_dt,
            exclude_bots=exclude_bots,
            enabled_detectors=list(detectors),
            detector_config=detector_config,
        )
        partial_results = results
    except Exception as exc:
        # Save partial results before re-raising (AFD §9.2)
        if partial_results:
            try:
                partial_path = Path(output_dir) / "partial_results.json"
                partial_path.parent.mkdir(parents=True, exist_ok=True)
                partial_path.write_text(_json.dumps(
                    {"error": str(exc), "partial": True}, default=str, indent=2
                ))
                click.echo(f"[PARTIAL-SAVED] Partial results saved to {partial_path}", err=True)
            except Exception:
                pass
        click.echo(f"[SYSTEM-ERROR] {exc}", err=True)
        sys.exit(2)

    score_pkg = results["score_package"]
    click.echo(f"Analysis complete.")
    integrity = score_pkg.integrity
    confidence = score_pkg.confidence
    integrity_overall = integrity.get("overall", 0.0) if isinstance(integrity, dict) else integrity.overall
    confidence_overall = confidence.get("overall", 0.0) if isinstance(confidence, dict) else confidence.overall
    click.echo(f"  Integrity : {integrity_overall:.4f}")
    click.echo(f"  Confidence: {confidence_overall:.4f}")

    report_out = results.get("report_output")
    if report_out and report_out.report_paths:
        click.echo("  Reports:")
        for fmt, path in report_out.report_paths.items():
            click.echo(f"    {fmt}: {path}")
    click.echo("Done.")

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
