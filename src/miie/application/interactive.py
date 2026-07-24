"""Interactive Navigation Framework — Deterministic guided workflows.

This module provides the interactive layer that sits on top of the
ApplicationService and WorkflowEngine to provide guided menus, step
progression, context-sensitive prompts, and result exploration.

All interactions are deterministic: same inputs → same outputs.
"""

from __future__ import annotations

import enum
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ..workspace.engine import WorkspaceEngine
from ..workspace.persistence import WorkspacePersistence
from ..workspace.views import (
    BenchmarkView,
    ConfidenceView,
    DetectorView,
    EvidenceView,
    ExecutiveSummary,
    IntegrityView,
    MetricView,
    RecommendationView,
    SessionInfoView,
    ValidationView,
)
from . import ApplicationService, WorkflowEngine, WorkflowState, WorkflowStep
from .navigation import (
    AVAILABLE_DETECTORS,
    AVAILABLE_FORMATS,
    AVAILABLE_METRICS,
    DETECTOR_LABELS,
    METRIC_LABELS,
    Menu,
    MenuAction,
    MenuItem,
    Prompt,
    PromptResult,
    PromptType,
    build_auth_token_prompt,
    build_config_menu,
    build_detectors_selection_prompt,
    build_exploration_menu,
    build_export_menu,
    build_formats_selection_prompt,
    build_github_url_prompt,
    build_metrics_selection_prompt,
    build_output_dir_prompt,
    build_repository_path_prompt,
    build_results_menu,
    build_window_size_prompt,
    build_window_strategy_prompt,
)
from .session import SessionManager
from .workflow import WorkflowResult


class NavigationState(enum.Enum):
    """Navigation states."""

    MAIN_MENU = "main_menu"
    WORKFLOW_RUNNING = "workflow_running"
    WORKFLOW_PAUSED = "workflow_paused"
    RESULTS_VIEW = "results_view"
    EXPLORATION_VIEW = "exploration_view"
    EXPORT_VIEW = "export_view"
    CONFIG_VIEW = "config_view"
    CONFIRM_EXIT = "confirm_exit"
    WORKSPACE_VIEW = "workspace_view"


@dataclass
class InteractiveSession:
    """Manages an interactive session with navigation state."""

    app_service: ApplicationService
    workflow_engine: WorkflowEngine
    session_manager: SessionManager

    # Navigation state
    current_state: NavigationState = NavigationState.MAIN_MENU
    current_menu: Optional[Menu] = None
    menu_stack: List[Menu] = field(default_factory=list)

    # Workflow context
    active_workflow_id: Optional[str] = None
    workflow_context: Dict[str, Any] = field(default_factory=dict)
    workflow_config: Dict[str, Any] = field(default_factory=dict)

    # Results context
    last_results: Optional[Dict[str, Any]] = None
    cached_session_id: Optional[str] = None

    # Workspace
    workspace: Optional[WorkspaceEngine] = None
    workspace_persistence: Optional[WorkspacePersistence] = None

    # Display
    verbose: bool = False
    use_colors: bool = True


class InteractiveNavigator:
    """Deterministic interactive navigator for MIIE workflows."""

    def __init__(
        self,
        app_service: Optional[ApplicationService] = None,
        workflow_engine: Optional[WorkflowEngine] = None,
        session_manager: Optional[SessionManager] = None,
    ) -> None:
        self.app_service = app_service or ApplicationService()
        self.workflow_engine = workflow_engine or WorkflowEngine()
        self.session_manager = session_manager or SessionManager()

        self.session = InteractiveSession(
            app_service=self.app_service,
            workflow_engine=self.workflow_engine,
            session_manager=self.session_manager,
        )

        # Register workflow state callbacks
        self.workflow_engine.on_state_change(self._on_workflow_state_change)

        # Command handlers
        self._menu_handlers: Dict[str, Callable[[], Any]] = {}

    def _get_default_config(self, workflow_type: str) -> Dict[str, Any]:
        """Get default configuration for a workflow type."""
        defaults = {
            "analyze": {
                "repo_path": "",
                "metrics": ["M-02", "M-06"],
                "detectors": ["D-01", "D-02", "D-03"],
                "output_dir": "./output",
                "window_strategy": "time",
                "window_size": 7,
                "since": None,
                "until": None,
                "exclude_bots": True,
                "thresholds": None,
                "formats": ["json"],
                "seed": 42,
                "forensic": False,
            },
            "validate": {
                "repo_path": "",
                "shallow": None,
            },
            "benchmark": {
                "suite": "B-01",
                "detectors": ["D-01", "D-02", "D-03"],
                "config": {"threshold": 0.05},
                "seed": 42,
            },
            "evaluate": {
                "benchmark_json": "",
                "ground_truth_json": "",
            },
        }
        return defaults.get(workflow_type, {})

    def _on_workflow_state_change(self, workflow_id: str, state: WorkflowState, step_name: Optional[str]) -> None:
        """Callback for workflow state changes."""
        self.session.active_workflow_id = workflow_id
        if state == WorkflowState.PAUSED:
            self.session.current_state = NavigationState.WORKFLOW_PAUSED
        elif state == WorkflowState.RUNNING:
            self.session.current_state = NavigationState.WORKFLOW_RUNNING
        elif state in (WorkflowState.COMPLETED, WorkflowState.FAILED, WorkflowState.CANCELLED):
            self.session.current_state = NavigationState.RESULTS_VIEW

    def run(self) -> int:
        """Run the interactive navigator main loop.

        Returns:
            Exit code (0 = success, non-zero = error/exit)
        """
        self._show_banner()

        # Check for restorable session
        if self._maybe_restore_session():
            return 0

        # Main navigation loop
        while True:
            try:
                if self.session.current_state == NavigationState.MAIN_MENU:
                    result = self._handle_main_menu()
                elif self.session.current_state == NavigationState.WORKFLOW_RUNNING:
                    result = self._handle_workflow_running()
                elif self.session.current_state == NavigationState.WORKFLOW_PAUSED:
                    result = self._handle_workflow_paused()
                elif self.session.current_state == NavigationState.RESULTS_VIEW:
                    result = self._handle_results_view()
                elif self.session.current_state == NavigationState.EXPLORATION_VIEW:
                    result = self._handle_exploration_view()
                elif self.session.current_state == NavigationState.EXPORT_VIEW:
                    result = self._handle_export_view()
                elif self.session.current_state == NavigationState.CONFIG_VIEW:
                    result = self._handle_config_view()
                elif self.session.current_state == NavigationState.CONFIRM_EXIT:
                    result = self._handle_confirm_exit()
                elif self.session.current_state == NavigationState.WORKSPACE_VIEW:
                    result = self._handle_workspace_view()
                else:
                    result = None

                if result is False:  # Exit requested
                    break
                elif isinstance(result, int):  # Exit code
                    return result

            except KeyboardInterrupt:
                if self._handle_confirm_exit():
                    break
            except EOFError:
                break
            except Exception as exc:
                self._display_error(f"Unexpected error: {exc}")
                if self.session.verbose:
                    import traceback

                    traceback.print_exc()

        return 0

    def _show_banner(self) -> None:
        """Display the MIIE banner."""
        from .. import __version__

        print(f"\n{'='*60}")
        print(f"  MIIE v{__version__} — Measurement Integrity Intelligence Engine")
        print("  Guided Scientific Analysis Workspace")
        print(f"{'='*60}\n")

    def _maybe_restore_session(self) -> bool:
        """Check for and offer to restore a previous session."""
        sessions = self.session_manager.list_sessions()
        if not sessions:
            return False

        latest = sessions[0]
        if self._prompt_yes_no(
            f"Found previous session ({latest['session_id'][:8]}... "
            f"from {latest['created_at'][:19]}, {latest['commands']} commands). Restore?",
            default=True,
        ):
            self.session_manager.load(latest["session_id"])
            self.session.cached_session_id = latest["session_id"]
            print("Session restored.")
            return True
        return False

    # -------------------------------------------------------------------------
    # Main Menu Handler
    # -------------------------------------------------------------------------

    def _handle_main_menu(self) -> Optional[bool]:
        """Handle main menu interaction."""
        menu = self._build_main_menu()
        self.session.current_menu = menu
        self._display_menu(menu)

        choice = self._get_menu_choice(menu)
        if choice is None:
            return self._handle_confirm_exit()

        return self._execute_main_menu_action(choice)

    def _build_main_menu(self) -> Menu:
        """Build the main menu."""
        return Menu(
            title="MIIE Workspace",
            subtitle="Select a workflow to begin",
            items=[
                MenuItem(
                    "1",
                    "Analyze Repository",
                    "Full 7-stage scientific analysis pipeline",
                    action=MenuAction.WORKFLOW,
                    metadata={"workflow": "analyze"},
                ),
                MenuItem(
                    "2",
                    "Validate Repository",
                    "Quick repository validation (ingestion only)",
                    action=MenuAction.WORKFLOW,
                    metadata={"workflow": "validate"},
                ),
                MenuItem(
                    "3",
                    "Run Benchmark",
                    "Execute a benchmark suite against detectors",
                    action=MenuAction.WORKFLOW,
                    metadata={"workflow": "benchmark"},
                ),
                MenuItem(
                    "4",
                    "Scientific Validation",
                    "Evaluate benchmark results against ground truth",
                    action=MenuAction.WORKFLOW,
                    metadata={"workflow": "evaluate"},
                ),
                MenuItem(
                    "5",
                    "Inspect Results",
                    "Explore cached analysis results interactively",
                    action=MenuAction.VIEW_RESULTS,
                ),
                MenuItem(
                    "6", "Generate Reports", "Export existing results to multiple formats", action=MenuAction.EXPORT
                ),
                MenuItem("7", "Configure MIIE", "Manage configuration settings", action=MenuAction.CONFIG),
                MenuItem("q", "Quit", "Exit MIIE", action=MenuAction.EXIT),
            ],
            allow_back=False,
        )

    def _execute_main_menu_action(self, item: MenuItem) -> Optional[bool]:
        """Execute a main menu action."""
        action = item.action

        if action == MenuAction.WORKFLOW:
            return self._start_workflow(item.metadata.get("workflow", "analyze"))
        elif action == MenuAction.VIEW_RESULTS:
            return self._view_results()
        elif action == MenuAction.EXPORT:
            self._export_results(
                self.session.workflow_config.get("formats", ["json"]),
                self.session.workflow_config.get("output_dir", "./output"),
            )
            return None
        elif action == MenuAction.CONFIG:
            self.session.current_state = NavigationState.CONFIG_VIEW
            return None
        elif action == MenuAction.EXIT:
            return self._handle_confirm_exit()

        return None

    # -------------------------------------------------------------------------
    # Workflow Handlers
    # -------------------------------------------------------------------------

    def _start_workflow(self, workflow_type: str) -> Optional[bool]:
        """Start a workflow with configuration prompts."""
        self.session.workflow_config = self._get_default_config(workflow_type)

        # Configuration phase
        if not self._configure_workflow(workflow_type):
            return None  # User cancelled

        # Confirm execution
        if not self._prompt_yes_no("Start analysis with above configuration?", default=True):
            return None

        # Create workflow steps
        steps = self._create_workflow_steps(workflow_type)
        self.workflow_engine.define(steps, context=self.session.workflow_config)

        # Create session
        self.session_manager.create(
            repo_path=self.session.workflow_config.get("repo_path"),
            output_dir=self.session.workflow_config.get("output_dir", "./output"),
            verbose=self.session.verbose,
            seed=self.session.workflow_config.get("seed", 42),
        )

        # Start workflow
        self.session.current_state = NavigationState.WORKFLOW_RUNNING
        return None  # Continue to workflow running handler

    def _configure_workflow(self, workflow_type: str) -> bool:
        """Run configuration prompts for a workflow."""
        config = self.session.workflow_config

        if workflow_type in ("analyze", "validate"):
            return self._configure_repository(config)
        elif workflow_type == "benchmark":
            return self._configure_benchmark(config)
        elif workflow_type == "evaluate":
            return self._configure_evaluation(config)

        return True

    def _configure_repository(self, config: Dict[str, Any]) -> bool:
        """Configure repository path and basic options."""
        # Repository path
        while True:
            if config.get("repo_path"):
                break

            print("\n--- Repository Selection ---")
            print("1. Local repository path")
            print("2. GitHub URL")

            choice = input("Select (1/2): ").strip()
            if choice == "1":
                prompt = build_repository_path_prompt()
                result = self._prompt(prompt)
                if result.cancelled:
                    return False
                config["repo_path"] = result.value
            elif choice == "2":
                prompt = build_github_url_prompt()
                result = self._prompt(prompt)
                if result.cancelled:
                    return False
                config["repo_path"] = result.value
            else:
                print("Invalid choice.")
                continue

            # Validate path/URL exists (basic check)
            if not config["repo_path"]:
                print("Repository path cannot be empty.")
                config["repo_path"] = ""
                continue
            break

        # Auth token (optional)
        if self._prompt_yes_no("Use GitHub authentication token?", default=False):
            prompt = build_auth_token_prompt()
            result = self._prompt(prompt)
            if not result.cancelled and result.value:
                config["auth_token"] = result.value

        # For validate workflow, we're done
        if "metrics" not in config:
            return True

        # Metrics selection
        print("\n--- Metrics Configuration ---")
        prompt = build_metrics_selection_prompt(AVAILABLE_METRICS, config["metrics"])
        result = self._prompt(prompt)
        if result.cancelled:
            return False
        if result.value:
            config["metrics"] = [m.strip() for m in result.value.split(",") if m.strip()]

        # Detectors selection
        print("\n--- Detectors Configuration ---")
        prompt = build_detectors_selection_prompt(AVAILABLE_DETECTORS, config["detectors"])
        result = self._prompt(prompt)
        if result.cancelled:
            return False
        if result.value:
            config["detectors"] = [d.strip() for d in result.value.split(",") if d.strip()]

        # Window strategy
        print("\n--- Window Segmentation ---")
        prompt = build_window_strategy_prompt(config["window_strategy"])
        result = self._prompt(prompt)
        if result.cancelled:
            return False
        if result.value:
            config["window_strategy"] = result.value

        # Window size
        prompt = build_window_size_prompt(config["window_size"], config["window_strategy"])
        result = self._prompt(prompt)
        if result.cancelled:
            return False
        if result.value:
            config["window_size"] = int(result.value)

        # Output directory
        print("\n--- Output Configuration ---")
        prompt = build_output_dir_prompt(config["output_dir"])
        result = self._prompt(prompt)
        if result.cancelled:
            return False
        if result.value:
            config["output_dir"] = result.value

        # Formats
        prompt = build_formats_selection_prompt(AVAILABLE_FORMATS, config["formats"])
        result = self._prompt(prompt)
        if result.cancelled:
            return False
        if result.value:
            config["formats"] = [f.strip() for f in result.value.split(",") if f.strip()]

        # Advanced options
        if self._prompt_yes_no("Configure advanced options (time range, thresholds, seed)?", default=False):
            self._configure_advanced(config)

        return True

    def _configure_advanced(self, config: Dict[str, Any]) -> None:
        """Configure advanced options."""
        # Time range
        since = input(f"Since (ISO 8601, blank for all) [{config.get('since') or ''}]: ").strip()
        if since:
            config["since"] = since

        until = input(f"Until (ISO 8601, blank for all) [{config.get('until') or ''}]: ").strip()
        if until:
            config["until"] = until

        # Exclude bots
        config["exclude_bots"] = self._prompt_yes_no(
            "Exclude bot-generated commits?", default=config.get("exclude_bots", True)
        )

        # Thresholds
        if self._prompt_yes_no("Custom detector thresholds (JSON)?", default=False):
            thresholds_str = input("Thresholds JSON: ").strip()
            if thresholds_str:
                import json

                try:
                    config["thresholds"] = json.loads(thresholds_str)
                except json.JSONDecodeError:
                    print("Invalid JSON, ignoring.")

        # Seed
        seed = input(f"Random seed [{config.get('seed', 42)}]: ").strip()
        if seed.isdigit():
            config["seed"] = int(seed)

        # Forensic
        config["forensic"] = self._prompt_yes_no("Include forensic evidence package?", default=False)

    def _configure_benchmark(self, config: Dict[str, Any]) -> bool:
        """Configure benchmark execution."""
        print("\n--- Benchmark Configuration ---")

        suite = input(f"Benchmark suite ID [{config['suite']}]: ").strip()
        if suite:
            config["suite"] = suite

        detectors = input(f"Detectors (comma-separated) [{','.join(config['detectors'])}]: ").strip()
        if detectors:
            config["detectors"] = [d.strip() for d in detectors.split(",") if d.strip()]

        seed = input(f"Random seed [{config['seed']}]: ").strip()
        if seed.isdigit():
            config["seed"] = int(seed)

        return True

    def _configure_evaluation(self, config: Dict[str, Any]) -> bool:
        """Configure scientific validation."""
        print("\n--- Scientific Validation Configuration ---")

        while not config.get("benchmark_json"):
            path = input("Path to BenchmarkRun JSON: ").strip()
            if not path:
                print("Required.")
                continue
            from pathlib import Path

            if not Path(path).exists():
                print(f"File not found: {path}")
                continue
            config["benchmark_json"] = path

        while not config.get("ground_truth_json"):
            path = input("Path to ground truth JSON: ").strip()
            if not path:
                print("Required.")
                continue
            from pathlib import Path

            if not Path(path).exists():
                print(f"File not found: {path}")
                continue
            config["ground_truth_json"] = path

        return True

    def _create_workflow_steps(self, workflow_type: str) -> List[WorkflowStep]:
        """Create workflow steps for the given type."""
        config = self.session.workflow_config

        if workflow_type == "analyze":
            return self._create_analyze_steps(config)
        elif workflow_type == "validate":
            return self._create_validate_steps(config)
        elif workflow_type == "benchmark":
            return self._create_benchmark_steps(config)
        elif workflow_type == "evaluate":
            return self._create_evaluate_steps(config)

        return []

    def _create_analyze_steps(self, config: Dict[str, Any]) -> List[WorkflowStep]:
        """Create steps for full analysis workflow."""

        def step_acquire(ctx):
            import os

            from ..processing.ingestion import RepositoryIngestionEngine

            token = config.get("auth_token") or os.environ.get("GITHUB_TOKEN")
            engine = RepositoryIngestionEngine(auth_token=token)
            repo_ctx = engine.ingest(repo_path=config["repo_path"], shallow_depth=config.get("shallow"))
            if not engine.validate(repo_ctx):
                raise RuntimeError("Repository context validation failed")
            ctx["repository_context"] = repo_ctx
            return {
                "commits": getattr(repo_ctx, "total_commits", "?"),
                "contributors": getattr(repo_ctx, "contributor_count", "?"),
            }

        def step_validate(ctx):
            # Validation already done in acquire
            return {"status": "validated"}

        def step_extract(ctx):
            from datetime import datetime

            from ..processing.extraction import MetricExtractionEngine

            engine = MetricExtractionEngine()
            since = datetime.fromisoformat(config["since"]) if config.get("since") else None
            until = datetime.fromisoformat(config["until"]) if config.get("until") else None
            mdf = engine.extract(
                context=ctx["repository_context"],
                metric_list=config["metrics"],
                since=since,
                until=until,
                exclude_bots=config.get("exclude_bots", True),
            )
            ctx["metric_dataframe"] = mdf
            metric_names = list(getattr(mdf, "metrics", {}).keys()) if mdf else config["metrics"]
            return {"metrics": metric_names, "windows": "pending"}

        def step_segment(ctx):
            from ..processing.segmentation import WindowSegmentationEngine

            engine = WindowSegmentationEngine()
            windows = engine.segment(
                metric_dataframe=ctx["metric_dataframe"],
                strategy=config["window_strategy"],
                size=config["window_size"],
                repository_context=ctx["repository_context"],
            )
            ctx["windows"] = windows
            return {"window_count": len(windows), "strategy": config["window_strategy"]}

        def step_detect(ctx):
            from ..processing.detection.correlation_breakdown_detector import (
                CorrelationBreakdownDetector,
            )
            from ..processing.detection.dispatcher import DetectorDispatcherEngine
            from ..processing.detection.distribution_drift_detector import (
                DistributionDriftDetector,
            )
            from ..processing.detection.registry import DetectorRegistry
            from ..processing.detection.threshold_compression_detector import (
                ThresholdCompressionDetector,
            )

            registry = DetectorRegistry()
            registry.register(DistributionDriftDetector())
            registry.register(CorrelationBreakdownDetector())
            registry.register(ThresholdCompressionDetector())

            dispatcher = DetectorDispatcherEngine(registry)
            det_results = dispatcher.invoke(
                metric_dataframe=ctx["metric_dataframe"],
                windows=ctx["windows"],
                detector_config=config.get("thresholds"),
                enabled_detectors=config["detectors"],
            )
            ctx["detector_results"] = det_results
            return {"detectors": config["detectors"]}

        def step_score(ctx):
            from ..processing.scoring.engine import ScoringEngine

            engine = ScoringEngine()
            score_pkg = engine.compute_integrity_score(
                detector_results=ctx["detector_results"],
                metric_dataframe=ctx["metric_dataframe"],
                windows=ctx["windows"],
            )
            ctx["score_package"] = score_pkg
            integrity = score_pkg.integrity
            confidence = score_pkg.confidence
            integ_val = (
                integrity.get("overall", 0.0) if isinstance(integrity, dict) else getattr(integrity, "overall", 0.0)
            )
            conf_val = (
                confidence.get("overall", 0.0) if isinstance(confidence, dict) else getattr(confidence, "overall", 0.0)
            )
            return {"integrity": integ_val, "confidence": conf_val}

        def step_evidence(ctx):
            from ..processing.evidence import EvidenceEngine
            from ..processing.explanation.engine import ExplanationEngine

            evidence_engine = EvidenceEngine()
            evidence = evidence_engine.generate(
                repository_context=ctx["repository_context"],
                metric_dataframe=ctx["metric_dataframe"],
                windows=ctx["windows"],
                detector_results=ctx["detector_results"],
                score_package=ctx["score_package"],
                configuration={
                    "metric_list": config["metrics"],
                    "since": config.get("since"),
                    "until": config.get("until"),
                    "exclude_bots": config.get("exclude_bots", True),
                    "segmentation_strategy": config["window_strategy"],
                    "segmentation_size": config["window_size"],
                },
            )
            ctx["evidence_package"] = evidence

            explanation_engine = ExplanationEngine()
            explanation = explanation_engine.generate(evidence, ctx["score_package"])
            ctx["explanation_report"] = explanation
            return {"evidence_items": len(evidence.items) if hasattr(evidence, "items") else "?"}

        def step_report(ctx):
            from pathlib import Path

            from ..processing.reporting.engine import ReportGenerator

            analysis_results = {
                "repository_context": ctx["repository_context"],
                "metric_dataframe": ctx["metric_dataframe"],
                "windows": ctx["windows"],
                "detector_results": ctx["detector_results"],
                "score_package": ctx["score_package"],
                "evidence_package": ctx["evidence_package"],
                "explanation_report": ctx["explanation_report"],
            }
            generator = ReportGenerator()
            generator.generate(
                analysis_result=analysis_results,
                output_formats=config["formats"],
                output_dir=Path(config["output_dir"]),
            )
            return {"output_dir": config["output_dir"], "formats": config["formats"]}

        return [
            WorkflowStep(
                "acquire", "Repository Acquisition", "Clone/fetch repository and extract metadata", step_acquire, 0
            ),
            WorkflowStep(
                "validate", "Repository Validation", "Verify repository integrity and structure", step_validate, 1
            ),
            WorkflowStep("extract", "Metric Extraction", "Extract configured metrics from repository", step_extract, 2),
            WorkflowStep("segment", "Window Segmentation", "Segment history into analysis windows", step_segment, 3),
            WorkflowStep("detect", "Detector Execution", "Run selected detectors on segmented data", step_detect, 4),
            WorkflowStep("score", "Integrity Scoring", "Compute integrity and confidence scores", step_score, 5),
            WorkflowStep("evidence", "Evidence Generation", "Generate evidence and explanations", step_evidence, 6),
            WorkflowStep("report", "Report Generation", "Write output reports in selected formats", step_report, 7),
        ]

    def _create_validate_steps(self, config: Dict[str, Any]) -> List[WorkflowStep]:
        """Create steps for validation workflow."""

        def step_acquire(ctx):
            import os

            from ..processing.ingestion import RepositoryIngestionEngine

            token = config.get("auth_token") or os.environ.get("GITHUB_TOKEN")
            engine = RepositoryIngestionEngine(auth_token=token)
            repo_ctx = engine.ingest(repo_path=config["repo_path"], shallow_depth=config.get("shallow"))
            if not engine.validate(repo_ctx):
                raise RuntimeError("Repository context validation failed")
            ctx["repository_context"] = repo_ctx
            return {
                "commits": getattr(repo_ctx, "total_commits", "?"),
                "contributors": getattr(repo_ctx, "contributor_count", "?"),
            }

        def step_validate(ctx):
            return {"status": "validated", "message": "Repository is valid for analysis"}

        return [
            WorkflowStep(
                "acquire", "Repository Acquisition", "Clone/fetch repository and extract metadata", step_acquire, 0
            ),
            WorkflowStep("validate", "Repository Validation", "Verify repository integrity", step_validate, 1),
        ]

    def _create_benchmark_steps(self, config: Dict[str, Any]) -> List[WorkflowStep]:
        """Create steps for benchmark workflow."""

        def step_setup(ctx):
            from ..processing.benchmark.engine import BenchmarkEngine

            engine = BenchmarkEngine()
            ctx["benchmark_engine"] = engine
            return {"suite": config["suite"]}

        def step_execute(ctx):
            result = ctx["benchmark_engine"].execute(
                suite_id=config["suite"],
                detector_ids=config["detectors"],
                config=config["config"],
                seed=config["seed"],
            )
            ctx["benchmark_result"] = result
            return {"metadata": result.metadata}

        def step_save(ctx):
            # Results are already in context, just confirm
            return {"status": "completed", "run_id": getattr(ctx.get("benchmark_result"), "run_id", "?")}

        return [
            WorkflowStep("setup", "Benchmark Setup", "Load benchmark suite configuration", step_setup, 0),
            WorkflowStep("execute", "Benchmark Execution", "Run detectors on benchmark candidates", step_execute, 1),
            WorkflowStep("save", "Save Results", "Persist benchmark run", step_save, 2),
        ]

    def _create_evaluate_steps(self, config: Dict[str, Any]) -> List[WorkflowStep]:
        """Create steps for evaluation workflow."""

        def step_load_benchmark(ctx):
            import json

            from ..schemas.models import BenchmarkRun

            with open(config["benchmark_json"]) as f:
                br_data = json.load(f)
            benchmark_run = BenchmarkRun(
                predictions=br_data.get("predictions", {}),
                metadata=br_data.get("metadata", {}),
            )
            ctx["benchmark_run"] = benchmark_run
            return {"run_id": getattr(benchmark_run, "run_id", "?")}

        def step_load_truth(ctx):
            import json

            with open(config["ground_truth_json"]) as f:
                gt_data = json.load(f)
            ctx["ground_truth"] = gt_data
            return {"loaded": True}

        def step_evaluate(ctx):
            from ..processing.evaluation.engine import EvaluationEngine

            result = EvaluationEngine().evaluate(ctx["benchmark_run"], ctx["ground_truth"])
            ctx["evaluation_result"] = result
            return {
                "accuracy": result.accuracy,
                "f1": result.f1_score,
                "precision": result.precision,
                "recall": result.recall,
            }

        return [
            WorkflowStep("load_benchmark", "Load Benchmark", "Load benchmark run from JSON", step_load_benchmark, 0),
            WorkflowStep("load_truth", "Load Ground Truth", "Load ground truth from JSON", step_load_truth, 1),
            WorkflowStep("evaluate", "Evaluate", "Compute evaluation metrics", step_evaluate, 2),
        ]

    def _handle_workflow_running(self) -> Optional[bool]:
        """Handle workflow execution with progress display."""
        print(f"\n{'='*60}")
        print(f"  Executing Workflow: {self.workflow_engine.workflow_id}")
        print(f"{'='*60}\n")

        # Register progress callback for real-time updates
        def progress_callback(workflow_id: str, state: WorkflowState, step_name: Optional[str]):
            if state == WorkflowState.RUNNING:
                progress = self.workflow_engine.get_progress()
                self._display_workflow_progress(progress, show_stage_detail=True)

        self.workflow_engine.on_state_change(progress_callback)

        # Execute workflow
        result = self.workflow_engine.execute()

        # Display final progress
        progress = self.workflow_engine.get_progress()
        self._display_workflow_progress(progress, show_stage_detail=True)

        if result.state == WorkflowState.COMPLETED:
            print(f"\n✓ Workflow completed successfully in {result.total_duration_seconds:.1f}s")
            self._cache_results(result)
            self.session.current_state = NavigationState.RESULTS_VIEW
        elif result.state == WorkflowState.FAILED:
            print(f"\n✗ Workflow failed: {result.error}")
            self.session.current_state = NavigationState.MAIN_MENU
        elif result.state == WorkflowState.CANCELLED:
            print("\n⊘ Workflow cancelled")
            self.session.current_state = NavigationState.MAIN_MENU

        # Show step summary
        self._display_step_summary(result)

        input("\nPress Enter to continue...")
        return None

    def _handle_workflow_paused(self) -> Optional[bool]:
        """Handle paused workflow."""
        print("\n⏸ Workflow Paused")
        print("1. Resume")
        print("2. Cancel")
        print("3. View Progress")

        choice = input("Select (1/2/3): ").strip()
        if choice == "1":
            self.workflow_engine.resume()
            self.session.current_state = NavigationState.WORKFLOW_RUNNING
        elif choice == "2":
            self.workflow_engine.cancel()
            self.session.current_state = NavigationState.MAIN_MENU
        elif choice == "3":
            progress = self.workflow_engine.get_progress()
            self._display_workflow_progress(progress)
            input("Press Enter to continue...")
        return None

    # -------------------------------------------------------------------------
    # Results View Handler
    # -------------------------------------------------------------------------

    def _view_results(self) -> Optional[bool]:
        """View cached or saved results."""
        # Try to load from current session
        if self.session_manager.current and self.session_manager.current.cached_results:
            self.session.last_results = dict(self.session_manager.current.cached_results)
            self.session.current_state = NavigationState.RESULTS_VIEW
            return None

        # Try to load from session files
        sessions = self.session_manager.list_sessions()
        if not sessions:
            print("No saved sessions found.")
            input("Press Enter to continue...")
            return None

        print("\n--- Saved Sessions ---")
        for i, s in enumerate(sessions, 1):
            print(
                f"  {i}. {s['session_id'][:8]}... | {s['created_at'][:19]} | {s['commands']} cmds | {s['repo_path'] or 'N/A'}"
            )

        choice = input("\nSelect session (number) or Enter to cancel: ").strip()
        if not choice:
            return None

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(sessions):
                self.session_manager.load(sessions[idx]["session_id"])
                self.session.last_results = dict(self.session_manager.current.cached_results)
                self.session.current_state = NavigationState.RESULTS_VIEW
        except (ValueError, IndexError):
            print("Invalid selection.")

        return None

    def _handle_results_view(self) -> Optional[bool]:
        """Handle results exploration with workspace views."""
        if not self.session.last_results:
            print("No results to display.")
            input("Press Enter to continue...")
            self.session.current_state = NavigationState.MAIN_MENU
            return None

        # Use workspace if available
        if self.session.workspace and self.session.workspace.is_initialized:
            return self._handle_workspace_view()

        # Fallback to legacy menu
        menu = build_results_menu(
            integrity_score=self._get_integrity_score(),
            confidence_score=self._get_confidence_score(),
            verdict=self._get_verdict(),
            risk_level=self._get_risk_level(),
            triggered_count=self._get_triggered_count(),
            total_detectors=self._get_total_detectors(),
            has_cached=True,
        )

        self.session.current_menu = menu
        self._display_menu(menu)

        choice = self._get_menu_choice(menu)
        if choice is None:
            self.session.current_state = NavigationState.MAIN_MENU
            return None

        if choice.action == MenuAction.EXPORT:
            self.session.current_state = NavigationState.EXPORT_VIEW
        elif choice.action == MenuAction.EXPLORE:
            self.session.current_state = NavigationState.EXPLORATION_VIEW
            self.session.workflow_context["explore_category"] = choice.metadata.get("category")
        elif choice.action == MenuAction.BACK:
            self.session.current_state = NavigationState.MAIN_MENU
        elif choice.action == MenuAction.NEW:
            self.session.current_state = NavigationState.MAIN_MENU

        return None

    def _handle_workspace_view(self) -> Optional[bool]:
        """Handle workspace navigation with scientific views."""
        workspace = self.session.workspace
        if workspace is None:
            return None

        section = workspace.state.current_section

        # Render current section
        view_map = {
            "overview": lambda: ExecutiveSummary().render(workspace),
            "repository": lambda: SessionInfoView().render(workspace),
            "metrics": lambda: MetricView().render(workspace),
            "detectors": lambda: DetectorView().render(workspace),
            "evidence": lambda: EvidenceView().render(workspace),
            "confidence": lambda: ConfidenceView().render(workspace),
            "integrity": lambda: IntegrityView().render(workspace),
            "validation": lambda: ValidationView().render(workspace),
            "benchmark": lambda: BenchmarkView().render(workspace),
            "recommendations": lambda: RecommendationView().render(workspace),
            "session": lambda: SessionInfoView().render(workspace),
        }

        view_renderer = view_map.get(section)
        if view_renderer:
            result = view_renderer()
            self._display_workspace_view(result)
        else:
            print(f"Unknown section: {section}")
            workspace.navigate_to("overview")

        # Show navigation menu
        return self._handle_workspace_navigation()

    def _handle_exploration_view(self) -> Optional[bool]:
        """Handle detailed result exploration."""
        category = self.session.workflow_context.get("explore_category", "metrics")

        # Get items for category
        items = self._get_exploration_items(category)

        menu = build_exploration_menu(category, items)
        self.session.current_menu = menu
        self._display_menu(menu)

        choice = self._get_menu_choice(menu)
        if choice is None or choice.action == MenuAction.BACK:
            self.session.current_state = NavigationState.RESULTS_VIEW
            return None

        # Show detail
        self._display_exploration_detail(choice.metadata.get("detail", {}))
        input("\nPress Enter to continue...")

        return None

    def _display_workspace_view(self, result) -> None:
        """Display a workspace view result."""
        print("\n" + "=" * 60)
        for line in result.lines:
            print(line)
        print("=" * 60)

    def _handle_workspace_navigation(self) -> Optional[bool]:
        """Handle workspace navigation menu."""
        workspace = self.session.workspace
        if workspace is None:
            return None

        print("\nWorkspace Navigation:")
        print("  1. Overview      6. Confidence    11. Recommendations")
        print("  2. Repository    7. Integrity     12. Traceability")
        print("  3. Metrics       8. Validation    13. Export")
        print("  4. Detectors     9. Benchmark     14. Save & Return")
        print("  5. Evidence     10. Session       15. New Analysis")
        print("  b) Back")

        choice = input("\nSelect section: ").strip().lower()

        section_map = {
            "1": "overview",
            "2": "repository",
            "3": "metrics",
            "4": "detectors",
            "5": "evidence",
            "6": "confidence",
            "7": "integrity",
            "8": "validation",
            "9": "benchmark",
            "10": "session",
            "11": "recommendations",
            "12": "traceability",
        }

        if choice in section_map:
            workspace.navigate_to(section_map[choice])
            return None
        elif choice == "13":
            self.session.current_state = NavigationState.EXPORT_VIEW
            return None
        elif choice == "14":
            self._save_workspace()
            self.session.current_state = NavigationState.MAIN_MENU
            return None
        elif choice == "15":
            self.session.current_state = NavigationState.MAIN_MENU
            return None
        elif choice == "b":
            if workspace.navigate_back():
                return None
            self.session.current_state = NavigationState.MAIN_MENU
            return None

        print("Invalid selection.")
        return None

    def _save_workspace(self) -> None:
        """Save workspace to disk."""
        workspace = self.session.workspace
        persistence = self.session.workspace_persistence
        if workspace and persistence:
            path = persistence.save(workspace)
            print(f"Workspace saved to {path}")
        else:
            print("No workspace to save.")

    def _handle_export_view(self) -> Optional[bool]:
        """Handle export workflow."""
        menu = build_export_menu(AVAILABLE_FORMATS)
        self.session.current_menu = menu
        self._display_menu(menu)

        choice = self._get_menu_choice(menu)
        if choice is None or choice.action == MenuAction.BACK:
            self.session.current_state = NavigationState.RESULTS_VIEW
            return None

        if choice.metadata.get("format") == "all":
            formats = AVAILABLE_FORMATS
        else:
            formats = [choice.metadata.get("format", "json")]

        output_dir = input("Output directory [./export]: ").strip() or "./export"

        self._export_results(formats, output_dir)
        print(f"\nExported to {output_dir}")
        input("Press Enter to continue...")

        self.session.current_state = NavigationState.RESULTS_VIEW
        return None

    def _handle_config_view(self) -> Optional[bool]:
        """Handle configuration management."""
        from .config import DEFAULT_CONFIG, load_config, save_config

        config = load_config()

        menu = build_config_menu(config)
        self.session.current_menu = menu
        self._display_menu(menu)

        choice = self._get_menu_choice(menu)
        if choice is None or choice.action == MenuAction.BACK:
            self.session.current_state = NavigationState.MAIN_MENU
            return None

        action = choice.label.lower()
        if action == "view current config":
            self._display_config(config)
        elif action == "edit config":
            self._edit_config(config)
        elif action == "reset to defaults":
            if self._prompt_yes_no("Reset all configuration to defaults?", default=False):
                save_config(DEFAULT_CONFIG.copy())
                print("Configuration reset.")
        elif action == "save config":
            save_config(config)
            print("Configuration saved.")
        elif action == "import config":
            self._import_config(config)
        elif action == "export config":
            self._export_config(config)

        input("Press Enter to continue...")
        return None

    def _handle_confirm_exit(self) -> bool:
        """Confirm exit."""
        return self._prompt_yes_no("Exit MIIE?", default=True)

    # -------------------------------------------------------------------------
    # Display Helpers
    # -------------------------------------------------------------------------

    def _display_menu(self, menu: Menu) -> None:
        """Display a menu."""
        print(f"\n{menu.title}")
        if menu.subtitle:
            print(f"  {menu.subtitle}")
        print("-" * 50)

        for item in menu.items:
            if not item.enabled:
                print(f"  {item.key}) {item.label} (disabled)")
            else:
                desc = f" — {item.description}" if item.description else ""
                print(f"  {item.key}) {item.label}{desc}")

        if menu.allow_back:
            print("  b) Back")

    def _get_menu_choice(self, menu: Menu) -> Optional[MenuItem]:
        """Get user's menu choice."""
        valid_keys = [item.key for item in menu.items if item.enabled]
        if menu.allow_back:
            valid_keys.append("b")

        while True:
            choice = input("\nSelect: ").strip().lower()
            if choice in valid_keys:
                for item in menu.items:
                    if item.key == choice:
                        return item
                if choice == "b" and menu.allow_back:
                    return MenuItem("b", "Back", "Return", action=MenuAction.BACK)
            print(f"Invalid choice. Valid: {', '.join(valid_keys)}")

    def _display_workflow_progress(self, progress: Dict[str, Any], show_stage_detail: bool = False) -> None:
        """Display workflow progress bar with stage details."""
        pct = progress.get("progress_percent", 0)
        bar_len = 40
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        current = progress.get("current_step", "Waiting...")
        state = progress.get("state", "unknown")
        steps_completed = progress.get("steps_completed", 0)
        steps_total = progress.get("steps_total", 0)

        # State indicator
        state_icon = {
            "created": "○",
            "running": "▶",
            "paused": "⏸",
            "completed": "✓",
            "failed": "✗",
            "cancelled": "⊘",
        }.get(state, "?")

        print(f"\n[{bar}] {pct:.0f}%  {state_icon} {state.upper()} — Step {steps_completed}/{steps_total}: {current}")

        if show_stage_detail:
            # Stage descriptions
            stage_info = {
                "acquire": ("Repository Acquisition", "Cloning/fetching repository, extracting metadata"),
                "validate": ("Repository Validation", "Verifying repository integrity and structure"),
                "extract": ("Metric Extraction", "Extracting configured metrics from repository history"),
                "segment": ("Window Segmentation", "Segmenting history into analysis windows"),
                "detect": ("Detector Execution", "Running selected detectors on segmented data"),
                "score": ("Integrity Scoring", "Computing integrity and confidence scores"),
                "evidence": ("Evidence Generation", "Generating evidence package and explanations"),
                "report": ("Report Generation", "Writing output reports in selected formats"),
            }

            step_id = progress.get("current_step", "").lower()
            if step_id in stage_info:
                name, desc = stage_info[step_id]
                print(f"  Stage: {name}")
                print(f"  Description: {desc}")

            # Show completed stages
            if self.session.verbose:
                print("\n  Stage Status:")
                for i, step in enumerate(self.workflow_engine.steps):
                    if i < steps_completed:
                        status = "✓"
                    elif i == steps_completed:
                        status = "▶"
                    else:
                        status = "○"
                    step_name = step.step_id
                    sname, sdesc = stage_info.get(step_name, (step.name, ""))
                    print(f"    {status} {sname} ({step.name})")

            # Show timing
            if hasattr(self.workflow_engine, "_step_results") and self.workflow_engine._step_results:
                print("\n  Timing:")
                for sr in self.workflow_engine._step_results:
                    status = "✓" if sr.success else "✗"
                    print(f"    {status} {sr.step_id}: {sr.duration_seconds:.1f}s")

    def _display_step_summary(self, result) -> None:
        """Display workflow step summary."""
        print("\n--- Step Summary ---")
        for sr in result.step_results:
            status = "✓" if sr.success else "✗"
            print(f"  {status} {sr.step_id}: {sr.duration_seconds:.1f}s")
            if not sr.success:
                print(f"      Error: {sr.error}")

    def _display_error(self, message: str) -> None:
        """Display an error message."""
        print(f"\n[ERROR] {message}", file=sys.stderr)

    def _display_config(self, config: Dict[str, Any]) -> None:
        """Display configuration."""
        import json

        print("\n--- Current Configuration ---")
        print(json.dumps(config, indent=2, sort_keys=True))

    def _edit_config(self, config: Dict[str, Any]) -> None:
        """Interactively edit configuration."""
        print("\n--- Edit Configuration ---")
        print("Enter new values (Enter to keep current):")

        for key, value in config.items():
            if isinstance(value, dict):
                continue
            new_val = input(f"  {key} [{value}]: ").strip()
            if new_val:
                try:
                    if isinstance(value, bool):
                        config[key] = new_val.lower() in ("true", "yes", "1", "y")
                    elif isinstance(value, int):
                        config[key] = int(new_val)
                    elif isinstance(value, list):
                        config[key] = [v.strip() for v in new_val.split(",")]
                    else:
                        config[key] = new_val
                except ValueError:
                    print(f"    Invalid value for {key}, keeping current.")

    def _import_config(self, config: Dict[str, Any]) -> None:
        """Import configuration from file."""
        path = input("Path to config file: ").strip()
        if not path:
            return
        import json
        from pathlib import Path

        import yaml

        try:
            content = Path(path).read_text()
            if path.endswith((".yaml", ".yml")):
                imported = yaml.safe_load(content)
            elif path.endswith(".json"):
                imported = json.loads(content)
            else:
                print("Unsupported format.")
                return
            config.update(imported)
            print("Configuration imported.")
        except Exception as exc:
            print(f"Import failed: {exc}")

    def _export_config(self, config: Dict[str, Any]) -> None:
        """Export configuration to file."""
        from pathlib import Path as PathLib

        path = input("Export path [miie-config.yaml]: ").strip() or "miie-config.yaml"
        import yaml

        try:
            PathLib(path).write_text(yaml.dump(config, sort_keys=True))
            print(f"Configuration exported to {path}")
        except Exception as exc:
            print(f"Export failed: {exc}")

    # -------------------------------------------------------------------------
    # Prompt Helpers
    # -------------------------------------------------------------------------

    def _prompt(self, prompt: Prompt) -> PromptResult:
        """Execute a prompt and return result."""
        if prompt.prompt_type == PromptType.TEXT:
            return self._prompt_text(prompt)
        elif prompt.prompt_type == PromptType.CONFIRM:
            return self._prompt_confirm(prompt)
        elif prompt.prompt_type == PromptType.CHOICE:
            return self._prompt_choice(prompt)
        elif prompt.prompt_type == PromptType.PATH:
            return self._prompt_path(prompt)
        elif prompt.prompt_type == PromptType.INT:
            return self._prompt_int(prompt)
        else:
            return PromptResult(cancelled=True, value="", error="Unknown prompt type")

    def _prompt_text(self, prompt: Prompt) -> PromptResult:
        """Prompt for text input."""
        default_str = f" [{prompt.default}]" if prompt.default else ""
        help_str = f" ({prompt.help_text})" if prompt.help_text else ""
        while True:
            val = input(f"{prompt.message}{default_str}{help_str}: ").strip()
            if not val and prompt.default:
                val = prompt.default
            if prompt.validator:
                ok, err = prompt.validator(val)
                if not ok:
                    print(f"  {err}")
                    continue
            return PromptResult(cancelled=False, value=val)

    def _prompt_confirm(self, prompt: Prompt) -> PromptResult:
        """Prompt for yes/no confirmation."""
        default_str = "Y/n" if prompt.default == "y" else "y/N"
        while True:
            val = input(f"{prompt.message} [{default_str}]: ").strip().lower()
            if not val:
                val = prompt.default
            if val in ("y", "yes"):
                return PromptResult(cancelled=False, value=True)
            elif val in ("n", "no"):
                return PromptResult(cancelled=False, value=False)
            print("  Please enter y or n.")

    def _prompt_choice(self, prompt: Prompt) -> PromptResult:
        """Prompt for choice from list."""
        print(f"\n{prompt.message}")
        if prompt.help_text:
            print(f"  {prompt.help_text}")
        for i, (key, desc) in enumerate(prompt.choices, 1):
            print(f"  {i}. {key} — {desc}")
        if prompt.default:
            print(f"  Default: {prompt.default}")

        while True:
            val = input("Select (comma-separated for multiple): ").strip()
            if not val and prompt.default:
                val = prompt.default
            choices = [v.strip() for v in val.split(",") if v.strip()]
            valid_keys = [c[0] for c in prompt.choices]
            if all(c in valid_keys for c in choices):
                return PromptResult(cancelled=False, value=",".join(choices))
            print(f"  Invalid. Valid keys: {', '.join(valid_keys)}")

    def _prompt_path(self, prompt: Prompt) -> PromptResult:
        """Prompt for file/directory path."""
        while True:
            val = input(f"{prompt.message} [{prompt.default or ''}]: ").strip()
            if not val and prompt.default:
                val = prompt.default
            if prompt.validator:
                ok, err = prompt.validator(val)
                if not ok:
                    print(f"  {err}")
                    continue
            return PromptResult(cancelled=False, value=val)

    def _prompt_int(self, prompt: Prompt) -> PromptResult:
        """Prompt for integer."""
        while True:
            val = input(f"{prompt.message} [{prompt.default or ''}]: ").strip()
            if not val and prompt.default:
                val = prompt.default
            if val.isdigit():
                return PromptResult(cancelled=False, value=int(val))
            print("  Must be a positive integer.")

    def _prompt_yes_no(self, message: str, default: bool = True) -> bool:
        """Simple yes/no prompt."""
        default_str = "Y/n" if default else "y/N"
        while True:
            val = input(f"{message} [{default_str}]: ").strip().lower()
            if not val:
                return default
            if val in ("y", "yes"):
                return True
            if val in ("n", "no"):
                return False
            print("  Please enter y or n.")

    # -------------------------------------------------------------------------
    # Result Helpers
    # -------------------------------------------------------------------------

    def _cache_results(self, result: WorkflowResult) -> None:
        """Cache workflow results in session.

        Stores the full workflow context (all step outputs) so that
        result exploration and export can access the data.
        """
        # Pull context from the workflow engine (contains all step outputs)
        context = dict(self.workflow_engine._context)
        repo_path = self.session.workflow_config.get("repo_path", "unknown")

        # Extract key summary data from context
        cache_data = {
            "timestamp": time.time(),
            "repo_path": repo_path,
            "workflow_id": result.workflow_id,
            "state": result.state.value,
            "steps_completed": result.steps_completed,
            "total_duration_seconds": result.total_duration_seconds,
        }

        # Extract score_package data if present
        score_package = context.get("score_package")
        if score_package is not None:
            try:
                cache_data["integrity_score"] = score_package.integrity.overall
                cache_data["integrity_per_metric"] = dict(score_package.integrity.per_metric)
                cache_data["confidence_score"] = score_package.confidence.overall
                cache_data["confidence_band"] = score_package.confidence.band
                cache_data["confidence_factors"] = dict(score_package.confidence.factors)
            except (AttributeError, TypeError):
                pass

        # Store detector_results summary
        detector_results = context.get("detector_results")
        if detector_results is not None:
            try:
                triggered_count = 0
                total_detectors = 0
                detector_summary = {}
                for attr in ("d_01", "d_02", "d_03"):
                    det_data = getattr(detector_results, attr, None)
                    if det_data:
                        total_detectors += 1
                        # Check if any window triggered
                        has_triggered = any(
                            (
                                any(getattr(output, "triggered", False) for output in window_outputs.values())
                                if isinstance(window_outputs, dict)
                                else False
                            )
                            for window_outputs in det_data.values()
                        )
                        if has_triggered:
                            triggered_count += 1
                        detector_summary[attr] = {
                            "metrics": list(det_data.keys()),
                            "triggered": has_triggered,
                        }
                cache_data["triggered_count"] = triggered_count
                cache_data["total_detectors"] = total_detectors
                cache_data["detector_summary"] = detector_summary
            except (AttributeError, TypeError):
                pass

        # Store evidence package summary
        evidence_package = context.get("evidence_package")
        if evidence_package is not None:
            try:
                cache_data["evidence_items"] = (
                    len(evidence_package.warnings) if hasattr(evidence_package, "warnings") else 0
                )
                cache_data["evidence_windows"] = (
                    len(evidence_package.windows) if hasattr(evidence_package, "windows") else 0
                )
            except (AttributeError, TypeError):
                pass

        # Store explanation report summary
        explanation = context.get("explanation_report")
        if explanation is not None:
            try:
                cache_data["explanation_count"] = len(explanation) if hasattr(explanation, "__len__") else 0
            except (AttributeError, TypeError):
                pass

        # Store full context for exploration
        cache_data["full_context"] = context

        # Cache the result
        result_id = f"analyze:{repo_path}"
        self.session_manager.cache_result(result_id, cache_data)
        self.session.last_results = cache_data

        # Initialize workspace from workflow results
        self._initialize_workspace(result, context)

    def _initialize_workspace(self, result: WorkflowResult, context: Dict[str, Any]) -> None:
        """Initialize workspace from completed workflow results.

        Args:
            result: The completed workflow result
            context: The workflow context containing all step outputs
        """
        workspace = WorkspaceEngine()
        workspace.initialize_from_workflow(result, context, self.session.workflow_config)
        self.session.workspace = workspace
        self.session.workspace_persistence = WorkspacePersistence()

    def _get_integrity_score(self) -> float:
        """Extract integrity score from cached results."""
        if self.session.last_results:
            return self.session.last_results.get("integrity_score", 0.0)
        return 0.0

    def _get_confidence_score(self) -> float:
        """Extract confidence score from cached results."""
        if self.session.last_results:
            return self.session.last_results.get("confidence_score", 0.0)
        return 0.0

    def _get_verdict(self) -> str:
        """Extract verdict from cached results."""
        integrity = self._get_integrity_score()
        if integrity >= 1.0:
            return "PASS"
        elif integrity >= 0.7:
            return "WARN"
        elif integrity > 0.0:
            return "FAIL"
        return "UNKNOWN"

    def _get_risk_level(self) -> str:
        """Extract risk level from cached results."""
        if self.session.last_results:
            return self.session.last_results.get("confidence_band", "UNKNOWN")
        return "UNKNOWN"

    def _get_triggered_count(self) -> int:
        """Get number of triggered detectors."""
        if self.session.last_results:
            return self.session.last_results.get("triggered_count", 0)
        return 0

    def _get_total_detectors(self) -> int:
        """Get total number of detectors run."""
        if self.session.last_results:
            return self.session.last_results.get("total_detectors", 0)
        return 0

    def _get_exploration_items(self, category: str) -> List[Dict[str, Any]]:
        """Get exploration items for a category from real results."""
        if not self.session.last_results:
            return []

        results = self.session.last_results
        full_context = results.get("full_context", {})

        if category == "metrics":
            return self._get_metric_exploration_items(full_context)
        elif category == "detectors":
            return self._get_detector_exploration_items(full_context)
        elif category == "evidence":
            return self._get_evidence_exploration_items(full_context)
        elif category == "confidence":
            return self._get_confidence_exploration_items(results)
        elif category == "integrity":
            return self._get_integrity_exploration_items(results, full_context)
        elif category == "validation":
            return self._get_validation_exploration_items(full_context)
        elif category == "benchmark":
            return self._get_benchmark_exploration_items(full_context)

        return [{"title": f"No items for category: {category}", "description": ""}]

    def _get_metric_exploration_items(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get metric exploration items from MetricDataFrame."""
        items = []
        mdf = context.get("metric_dataframe")
        if mdf is None:
            return [{"title": "No metric data available", "description": "Run an analysis first"}]

        try:
            metrics = getattr(mdf, "metrics", {})
            for metric_id, metric_data in metrics.items():
                items.append(
                    {
                        "title": f"{metric_id} — {METRIC_LABELS.get(metric_id, 'Unknown')}",
                        "description": f"Data points: {len(metric_data) if hasattr(metric_data, '__len__') else '?'}",
                        "detail": {
                            "metric_id": metric_id,
                            "label": METRIC_LABELS.get(metric_id, "Unknown"),
                            "data_summary": str(metric_data)[:200] if metric_data else "Empty",
                        },
                    }
                )
        except (AttributeError, TypeError):
            items.append({"title": "Error reading metric data", "description": "Data may be corrupted"})

        if not items:
            items.append({"title": "No metrics extracted", "description": "Check metric configuration"})
        return items

    def _get_detector_exploration_items(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get detector exploration items from DetectorResults."""
        items = []
        det_results = context.get("detector_results")
        if det_results is None:
            return [{"title": "No detector results available", "description": "Run analysis first"}]

        detector_map = {"d_01": "D-01", "d_02": "D-02", "d_03": "D-03"}
        for attr, det_id in detector_map.items():
            det_data = getattr(det_results, attr, None)
            if not det_data:
                continue

            label = DETECTOR_LABELS.get(det_id, "Unknown")
            metric_count = len(det_data)
            triggered = False
            details = []

            for metric_key, window_outputs in det_data.items():
                if isinstance(window_outputs, dict):
                    for window_id, output in window_outputs.items():
                        was_triggered = getattr(output, "triggered", False)
                        if was_triggered:
                            triggered = True
                        details.append(
                            {
                                "window": window_id,
                                "metric": metric_key,
                                "triggered": was_triggered,
                                "score": getattr(output, "score", None),
                            }
                        )

            items.append(
                {
                    "title": f"{det_id} — {label}",
                    "description": f"Metrics: {metric_count} | Triggered: {'YES' if triggered else 'No'}",
                    "detail": {
                        "detector_id": det_id,
                        "label": label,
                        "triggered": triggered,
                        "metrics_analyzed": list(det_data.keys()),
                        "sample_outputs": details[:5],
                    },
                }
            )

        if not items:
            items.append({"title": "No detector outputs found", "description": "All detectors may have been skipped"})
        return items

    def _get_evidence_exploration_items(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get evidence exploration items from EvidencePackage."""
        items = []
        evidence = context.get("evidence_package")
        if evidence is None:
            return [{"title": "No evidence package available", "description": "Run analysis first"}]

        try:
            # Warnings
            warnings = getattr(evidence, "warnings", [])
            if warnings:
                items.append(
                    {
                        "title": f"Evidence Warnings ({len(warnings)})",
                        "description": f"{len(warnings)} warnings in evidence package",
                        "detail": {"warnings": [str(w) for w in warnings[:10]]},
                    }
                )

            # Windows analyzed
            windows = getattr(evidence, "windows", [])
            items.append(
                {
                    "title": f"Windows Analyzed ({len(windows)})",
                    "description": f"Evidence covers {len(windows)} analysis windows",
                    "detail": {"window_count": len(windows)},
                }
            )

            # Observation summary
            obs_summary = getattr(evidence, "observation_summary", {})
            if obs_summary:
                items.append(
                    {
                        "title": "Observation Summary",
                        "description": f"Total observations: {obs_summary.get('total_observations', '?')}",
                        "detail": obs_summary,
                    }
                )

            # Detector execution metadata
            exec_meta = getattr(evidence, "detector_execution_metadata", {})
            if exec_meta:
                items.append(
                    {
                        "title": "Detector Execution Metadata",
                        "description": f"{len(exec_meta)} detectors with execution metadata",
                        "detail": exec_meta,
                    }
                )
        except (AttributeError, TypeError):
            items.append({"title": "Error reading evidence data", "description": "Evidence package may be incomplete"})

        if not items:
            items.append({"title": "Evidence package empty", "description": "No evidence items found"})
        return items

    def _get_confidence_exploration_items(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get confidence exploration items from ScorePackage."""
        items = []
        band = results.get("confidence_band", "UNKNOWN")
        overall = results.get("confidence_score", 0.0)
        factors = results.get("confidence_factors", {})

        items.append(
            {
                "title": f"Overall Confidence: {overall:.4f} ({band})",
                "description": f"Confidence band: {band}",
                "detail": {"overall": overall, "band": band},
            }
        )

        factor_labels = {
            "sample_size": "Sample Size",
            "variance": "Variance Stability",
            "missing_data": "Missing Data",
            "window_balance": "Window Balance",
            "detector_success": "Detector Success Rate",
        }
        for factor_key, factor_value in factors.items():
            label = factor_labels.get(factor_key, factor_key)
            items.append(
                {
                    "title": f"{label}: {factor_value:.4f}",
                    "description": "Factor contribution to confidence",
                    "detail": {"factor": factor_key, "value": factor_value},
                }
            )

        if not items:
            items.append({"title": "No confidence data available", "description": "Run analysis first"})
        return items

    def _get_integrity_exploration_items(
        self, results: Dict[str, Any], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get integrity exploration items from ScorePackage."""
        items = []
        overall = results.get("integrity_score", 0.0)
        per_metric = results.get("integrity_per_metric", {})

        items.append(
            {
                "title": f"Overall Integrity: {overall:.4f}",
                "description": f"Verdict: {'PASS' if overall >= 1.0 else 'FAIL'}",
                "detail": {"overall": overall},
            }
        )

        for metric_id, score in per_metric.items():
            label = METRIC_LABELS.get(metric_id, "Unknown")
            items.append(
                {
                    "title": f"{metric_id} — {label}: {score:.4f}",
                    "description": "Per-metric integrity score",
                    "detail": {"metric_id": metric_id, "score": score, "label": label},
                }
            )

        if not items:
            items.append({"title": "No integrity data available", "description": "Run analysis first"})
        return items

    def _get_validation_exploration_items(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get validation exploration items."""
        items = []
        repo_ctx = context.get("repository_context")
        if repo_ctx:
            items.append(
                {
                    "title": "Repository Validated",
                    "description": f"Total commits: {getattr(repo_ctx, 'total_commits', '?')}",
                    "detail": {
                        "total_commits": getattr(repo_ctx, "total_commits", "?"),
                        "contributors": getattr(repo_ctx, "contributor_count", "?"),
                    },
                }
            )
        else:
            items.append({"title": "No validation data", "description": "Repository context not available"})
        return items

    def _get_benchmark_exploration_items(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get benchmark exploration items."""
        items = []
        benchmark = context.get("benchmark_result")
        if benchmark:
            items.append(
                {
                    "title": "Benchmark Results",
                    "description": f"Run ID: {getattr(benchmark, 'run_id', '?')}",
                    "detail": {"run_id": getattr(benchmark, "run_id", "?")},
                }
            )
        else:
            items.append({"title": "No benchmark results", "description": "Run a benchmark first"})
        return items

    def _display_exploration_detail(self, detail: Dict[str, Any]) -> None:
        """Display detailed exploration view."""
        import json

        print("\n--- Detail ---")
        print(json.dumps(detail, indent=2, default=str))

    def _export_results(self, formats: List[str], output_dir: str) -> None:
        """Export results to specified formats using ReportGenerator."""
        from pathlib import Path

        from ..processing.reporting.engine import ReportGenerator

        if not self.session.last_results:
            print("No results to export.")
            return

        full_context = self.session.last_results.get("full_context", {})
        if not full_context:
            print("No analysis context available for export.")
            return

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        try:
            generator = ReportGenerator()
            generator.generate(
                analysis_result=full_context,
                output_formats=formats,
                output_dir=Path(output_dir),
            )
            print(f"Exported to {output_dir} in formats: {', '.join(formats)}")
        except Exception as exc:
            print(f"Export failed: {exc}")
            # Fallback: write raw JSON
            if "json" in formats:
                import json

                out_path = Path(output_dir) / "results.json"
                try:
                    # Filter non-serializable objects
                    serializable = {
                        k: v
                        for k, v in full_context.items()
                        if isinstance(v, (dict, list, str, int, float, bool, type(None)))
                    }
                    out_path.write_text(json.dumps(serializable, indent=2, default=str))
                    print(f"Fallback JSON exported to {out_path}")
                except Exception as fallback_exc:
                    print(f"Fallback export also failed: {fallback_exc}")


def run_interactive(
    app_service: Optional[ApplicationService] = None,
    workflow_engine: Optional[WorkflowEngine] = None,
    session_manager: Optional[SessionManager] = None,
) -> int:
    """Entry point for interactive mode.

    Args:
        app_service: Optional ApplicationService instance
        workflow_engine: Optional WorkflowEngine instance
        session_manager: Optional SessionManager instance

    Returns:
        Exit code
    """
    navigator = InteractiveNavigator(
        app_service=app_service,
        workflow_engine=workflow_engine,
        session_manager=session_manager,
    )
    return navigator.run()
