"""
MIIE v1.0 Workflow Dispatcher
Implements workflow routing for different analysis types.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from miie.orchestration.pipeline import AnalysisPipeline


class WorkflowType(Enum):
    """Types of analysis workflows."""

    WF_01 = "basic_analysis"  # Repository -> Metrics -> Windows -> Detection -> Scoring
    WF_02 = "with_evidence"  # WF_01 + Evidence Generation
    WF_03 = "full_analysis"  # WF_02 + Explanation + Reporting
    WF_04 = "benchmark_only"  # Benchmark execution only
    WF_05 = "evaluation_only"  # Evaluation of benchmark results


class WorkflowDispatcher:
    """Dispatches and routes different analysis workflows."""

    def __init__(self, pipeline: AnalysisPipeline):
        """Initialize workflow dispatcher with pipeline.

        Args:
            pipeline: Analysis pipeline to use for workflow execution
        """
        self.pipeline = pipeline
        self.workflow_history: List[Dict[str, Any]] = []

    def execute_workflow(
        self,
        workflow_type: WorkflowType,
        repo_path: Optional[str] = None,
        metric_list: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute a specific workflow type.

        Args:
            workflow_type: Type of workflow to execute
            repo_path: Path to repository (required for analysis workflows)
            metric_list: List of metric IDs to extract (required for analysis workflows)
            **kwargs: Additional arguments passed to pipeline methods

        Returns:
            Dictionary containing workflow results
        """
        # Validate that workflow_type is a WorkflowType enum
        if not isinstance(workflow_type, WorkflowType):
            raise ValueError(f"Unknown workflow type: {workflow_type}")

        result = {
            "workflow_type": workflow_type.value,
            "timestamp": datetime.now().isoformat(),
            "status": "started",
        }

        try:
            if workflow_type == WorkflowType.WF_01:
                result.update(self._execute_wf_01(repo_path, metric_list, **kwargs))
            elif workflow_type == WorkflowType.WF_02:
                result.update(self._execute_wf_02(repo_path, metric_list, **kwargs))
            elif workflow_type == WorkflowType.WF_03:
                result.update(self._execute_wf_03(repo_path, metric_list, **kwargs))
            elif workflow_type == WorkflowType.WF_04:
                result.update(self._execute_wf_04(**kwargs))
            elif workflow_type == WorkflowType.WF_05:
                result.update(self._execute_wf_05(**kwargs))
            else:
                raise ValueError(f"Unknown workflow type: {workflow_type}")

            result["status"] = "completed"
            self._record_workflow(result)

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self._record_workflow(result)
            raise

        return result

    def _execute_wf_01(self, repo_path: str, metric_list: List[str], **kwargs) -> Dict[str, Any]:
        """WF_01: Basic analysis workflow.

        Steps: Ingestion -> Extraction -> Segmentation -> Detection -> Scoring
        """
        # Run analysis but stop before evidence generation
        # We'll reuse the pipeline but intercept before evidence step

        # For simplicity in Day-5 mock, we'll run full pipeline and return subset
        # In a full implementation, we might want to short-circuit earlier
        full_result = self.pipeline.run_analysis(repo_path=repo_path, metric_list=metric_list, **kwargs)

        return {
            "repository_context": full_result["repository_context"],
            "metric_dataframe": full_result["metric_dataframe"],
            "windows": full_result["windows"],
            "detector_results": full_result["detector_results"],
            "score_package": full_result["score_package"],
            "workflow_steps": [
                "ingestion",
                "extraction",
                "segmentation",
                "detection",
                "scoring",
            ],
        }

    def _execute_wf_02(self, repo_path: str, metric_list: List[str], **kwargs) -> Dict[str, Any]:
        """WF_02: Analysis with evidence generation.

        Steps: WF_01 + Evidence Generation
        """
        full_result = self.pipeline.run_analysis(repo_path=repo_path, metric_list=metric_list, **kwargs)

        return {
            "repository_context": full_result["repository_context"],
            "metric_dataframe": full_result["metric_dataframe"],
            "windows": full_result["windows"],
            "detector_results": full_result["detector_results"],
            "score_package": full_result["score_package"],
            "evidence_package": full_result["evidence_package"],
            "workflow_steps": [
                "ingestion",
                "extraction",
                "segmentation",
                "detection",
                "scoring",
                "evidence_generation",
            ],
        }

    def _execute_wf_03(self, repo_path: str, metric_list: List[str], **kwargs) -> Dict[str, Any]:
        """WF_03: Full analysis workflow.

        Steps: WF_02 + Explanation + Reporting
        """
        output_dir = kwargs.get("output_dir")
        output_formats = kwargs.get("output_formats", ["json", "md"])

        full_result = self.pipeline.run_analysis(
            repo_path=repo_path,
            metric_list=metric_list,
            output_dir=output_dir,
            output_formats=output_formats,
            **{k: v for k, v in kwargs.items() if k not in ["output_dir", "output_formats"]},
        )

        return {
            "repository_context": full_result["repository_context"],
            "metric_dataframe": full_result["metric_dataframe"],
            "windows": full_result["windows"],
            "detector_results": full_result["detector_results"],
            "score_package": full_result["score_package"],
            "evidence_package": full_result["evidence_package"],
            "explanation_report": full_result["explanation_report"],
            "report_output": full_result["report_output"],
            "workflow_steps": [
                "ingestion",
                "extraction",
                "segmentation",
                "detection",
                "scoring",
                "evidence_generation",
                "explanation_generation",
                "report_generation",
            ],
        }

    def _execute_wf_04(self, **kwargs) -> Dict[str, Any]:
        """WF_04: Benchmark execution only."""
        suite_id = kwargs.get("suite_id", "default-suite")
        detector_ids = kwargs.get("detector_ids", ["D-01"])
        config = kwargs.get("config", {})
        seed = kwargs.get("seed", 42)

        benchmark_run = self.pipeline.run_benchmark(
            suite_id=suite_id, detector_ids=detector_ids, config=config, seed=seed
        )

        return {
            "benchmark_run": benchmark_run,
            "workflow_steps": ["benchmark_execution"],
        }

    def _execute_wf_05(self, **kwargs) -> Dict[str, Any]:
        """WF_05: Evaluation of benchmark results."""
        benchmark_run = kwargs.get("benchmark_run")
        ground_truth = kwargs.get("ground_truth", {})

        if benchmark_run is None:
            raise ValueError("benchmark_run is required for WF_05")

        evaluation_result = self.pipeline.evaluate_benchmark(benchmark_run=benchmark_run, ground_truth=ground_truth)

        return {
            "evaluation_result": evaluation_result,
            "workflow_steps": ["benchmark_evaluation"],
        }

    def _record_workflow(self, result: Dict[str, Any]) -> None:
        """Record workflow execution in history."""
        history_entry = {
            "timestamp": result["timestamp"],
            "workflow_type": result.get("workflow_type"),
            "status": result.get("status"),
            "steps_count": len(result.get("workflow_steps", [])),
        }
        if "error" in result:
            history_entry["error"] = result["error"]
        self.workflow_history.append(history_entry)

    def get_workflow_history(self) -> List[Dict[str, Any]]:
        """Get history of executed workflows."""
        return self.workflow_history.copy()

    def clear_workflow_history(self) -> None:
        """Clear workflow execution history."""
        self.workflow_history.clear()
