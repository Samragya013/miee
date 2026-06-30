"""
MIIE v1.0 Orchestration Pipeline
Implements the pipeline controller for orchestrating analysis engines.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from miie.contracts.interfaces import (
    IBenchmarkEngine,
    IDetectorEngine,
    IEvaluationEngine,
    IEvidenceEngine,
    IExplanationEngine,
    IExtractionEngine,
    IIngestionEngine,
    IReportGenerator,
    IScoringEngine,
    ISegmentationEngine,
)
from miie.schemas.models import BenchmarkRun, EvaluationResult


class AnalysisPipeline:
    """Orchestrates the execution of MIIE analysis engines."""

    def __init__(
        self,
        ingestion_engine: IIngestionEngine,
        extraction_engine: IExtractionEngine,
        segmentation_engine: ISegmentationEngine,
        detection_engine: IDetectorEngine,
        scoring_engine: IScoringEngine,
        evidence_engine: IEvidenceEngine,
        explanation_engine: IExplanationEngine,
        report_generator: IReportGenerator,
        benchmark_engine: Optional[IBenchmarkEngine] = None,
        evaluation_engine: Optional[IEvaluationEngine] = None,
    ):
        """Initialize pipeline with engine implementations.

        Args:
            ingestion_engine: Repository ingestion engine
            extraction_engine: Metric extraction engine
            segmentation_engine: Window segmentation engine
            detection_engine: Detector engine
            scoring_engine: Scoring engine
            evidence_engine: Evidence generation engine
            explanation_engine: Explanation generation engine
            report_generator: Report generation engine
            benchmark_engine: Optional benchmark engine
            evaluation_engine: Optional evaluation engine
        """
        self.ingestion_engine = ingestion_engine
        self.extraction_engine = extraction_engine
        self.segmentation_engine = segmentation_engine
        self.detection_engine = detection_engine
        self.scoring_engine = scoring_engine
        self.evidence_engine = evidence_engine
        self.explanation_engine = explanation_engine
        self.report_generator = report_generator
        self.benchmark_engine = benchmark_engine
        self.evaluation_engine = evaluation_engine

    def run_analysis(
        self,
        repo_path: str,
        metric_list: List[str],
        cache_dir: Optional[Path] = None,
        keep_cache: bool = False,
        shallow_depth: Optional[int] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        exclude_bots: bool = False,
        segmentation_strategy: str = "time",
        segmentation_size: int = 7,
        detector_config: Optional[Dict[str, Dict[str, Any]]] = None,
        enabled_detectors: Optional[List[str]] = None,
        detector_weights: Optional[Dict[str, float]] = None,
        output_formats: List[str] = None,
        output_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Run complete analysis pipeline.

        Args:
            repo_path: Path to repository (local or URL)
            metric_list: List of metric IDs to extract
            cache_dir: Optional directory to cache Git objects
            keep_cache: Whether to keep cache after ingestion
            shallow_depth: Depth for shallow clone (None for full clone)
            since: Extract metrics since this timestamp (inclusive)
            until: Extract metrics until this timestamp (inclusive)
            exclude_bots: Whether to exclude bot-generated commits
            segmentation_strategy: Window segmentation strategy
            segmentation_size: Window size for segmentation
            detector_config: Optional configuration for detectors
            enabled_detectors: Optional list of detector IDs to enable
            detector_weights: Optional weights for detectors
            output_formats: List of output formats for report generation
            output_dir: Directory to write output files

        Returns:
            Dictionary containing all analysis results
        """
        # Step 1: Ingestion
        repository_context = self.ingestion_engine.ingest(
            repo_path=repo_path,
            cache_dir=cache_dir,
            keep_cache=keep_cache,
            shallow_depth=shallow_depth,
        )

        # Validate repository context
        if not self.ingestion_engine.validate(repository_context):
            raise ValueError("Repository context validation failed")

        # Step 2: Extraction
        metric_dataframe = self.extraction_engine.extract(
            context=repository_context,
            metric_list=metric_list,
            since=since,
            until=until,
            exclude_bots=exclude_bots,
        )

        # Step 3: Segmentation
        windows = self.segmentation_engine.segment(
            metric_dataframe=metric_dataframe,
            strategy=segmentation_strategy,
            size=segmentation_size,
        )

        # AFD §Step 8: Minimum window gate
        # "total windows ≥ 2 (required for drift detection). If <2 valid windows: abort."
        if len(windows) < 2:
            return {
                "repository_context": repository_context,
                "metric_dataframe": metric_dataframe,
                "windows": windows,
                "detector_results": None,
                "score_package": None,
                "evidence_package": None,
                "explanation_report": None,
                "report_output": None,
                "error": f"Insufficient windows: {len(windows)} (need ≥2). " "Adjust window_size or time range.",
                "exit_code": 3,
            }

        # Step 3b: Re-extract per-window data for accurate confidence calculation
        # The initial extraction produces aggregated data; we need per-window values
        # for the confidence sample_size factor (f₁ = min(1, mean_n/50))
        metric_dataframe = self.extraction_engine.extract(
            context=repository_context,
            metric_list=metric_list,
            since=since,
            until=until,
            exclude_bots=exclude_bots,
            windows=windows,
        )

        # Step 4: Detection
        detector_results = self.detection_engine.invoke(
            metric_dataframe=metric_dataframe,
            windows=windows,
            detector_config=detector_config,
            enabled_detectors=enabled_detectors,
        )

        # Step 5: Generate partial evidence (observation-level metadata only)
        # This enables observation-aware scoring without circular dependency
        partial_evidence_package = self.evidence_engine.generate_observation_evidence(
            repository_context=repository_context,
            metric_dataframe=metric_dataframe,
            windows=windows,
            detector_results=detector_results,
            configuration={
                "metric_list": metric_list,
                "since": since,
                "until": until,
                "exclude_bots": exclude_bots,
                "segmentation_strategy": segmentation_strategy,
                "segmentation_size": segmentation_size,
                "detector_config": detector_config or {},
                "enabled_detectors": enabled_detectors or ["D-01", "D-02", "D-03"],
            },
        )

        # Step 6: Scoring (with observation-aware evidence)
        score_package = self.scoring_engine.compute_integrity_score(
            detector_results=detector_results,
            metric_dataframe=metric_dataframe,
            windows=windows,
            detector_weights=detector_weights,
            evidence_package=partial_evidence_package,
        )

        # Step 7: Generate full evidence package with scores
        evidence_package = self.evidence_engine.generate(
            repository_context=repository_context,
            metric_dataframe=metric_dataframe,
            windows=windows,
            detector_results=detector_results,
            score_package=score_package,
            configuration={
                "metric_list": metric_list,
                "since": since,
                "until": until,
                "exclude_bots": exclude_bots,
                "segmentation_strategy": segmentation_strategy,
                "segmentation_size": segmentation_size,
                "detector_config": detector_config or {},
                "enabled_detectors": enabled_detectors or ["D-01", "D-02", "D-03"],
            },
        )

        # Step 8: Explanation Generation
        explanation_report = self.explanation_engine.generate(
            evidence_package=evidence_package, score_package=score_package
        )

        # Step 9: Report Generation
        analysis_results = {
            "repository_context": repository_context,
            "metric_dataframe": metric_dataframe,
            "windows": windows,
            "detector_results": detector_results,
            "score_package": score_package,
            "evidence_package": evidence_package,
            "explanation_report": explanation_report,
        }

        report_output = self.report_generator.generate(
            analysis_result=analysis_results,
            output_formats=output_formats or ["json", "md"],
            output_dir=output_dir or Path("./output"),
        )

        # Return all results
        return {
            "repository_context": repository_context,
            "metric_dataframe": metric_dataframe,
            "windows": windows,
            "detector_results": detector_results,
            "score_package": score_package,
            "evidence_package": evidence_package,
            "explanation_report": explanation_report,
            "report_output": report_output,
        }

    def run_benchmark(
        self,
        suite_id: str,
        detector_ids: List[str],
        config: Dict[str, Any],
        seed: int = 42,
    ) -> BenchmarkRun:
        """Run benchmark suite (if benchmark engine available).

        Args:
            suite_id: Benchmark suite identifier
            detector_ids: List of detector IDs to benchmark
            config: Benchmark configuration
            seed: Random seed for reproducibility

        Returns:
            BenchmarkRun: Container for benchmark execution results
        """
        if self.benchmark_engine is None:
            raise RuntimeError("Benchmark engine not available")

        return self.benchmark_engine.execute(suite_id=suite_id, detector_ids=detector_ids, config=config, seed=seed)

    def evaluate_benchmark(self, benchmark_run: BenchmarkRun, ground_truth: Dict[str, Any]) -> EvaluationResult:
        """Evaluate benchmark results (if evaluation engine available).

        Args:
            benchmark_run: Container for benchmark execution results
            ground_truth: Ground truth data for evaluation

        Returns:
            EvaluationResult: Container for evaluation metrics
        """
        if self.evaluation_engine is None:
            raise RuntimeError("Evaluation engine not available")

        return self.evaluation_engine.evaluate(benchmark_run=benchmark_run, ground_truth=ground_truth)
