"""Interactive Navigation — guided menus, step progression, context-sensitive prompts.

Provides deterministic interactive workflows for MIIE guided analysis.
All interactions are pure functions with no side effects on scientific logic.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


class MenuAction(enum.Enum):
    """Possible actions from a menu."""

    SELECT = "select"
    BACK = "back"
    QUIT = "quit"
    HELP = "help"
    CANCEL = "cancel"
    CONFIRM = "confirm"
    WORKFLOW = "workflow"
    VIEW_RESULTS = "view_results"
    EXPORT = "export"
    CONFIG = "config"
    EXIT = "exit"
    EXPLORE = "explore"
    NEW = "new"


class WorkflowPhase(enum.Enum):
    """Phases of the guided analysis workflow."""

    WELCOME = "welcome"
    REPOSITORY_SELECT = "repository_select"
    CONFIGURATION_REVIEW = "configuration_review"
    CONFIRMATION = "confirmation"
    EXECUTION = "execution"
    PROGRESS = "progress"
    RESULTS = "results"
    EXPLORATION = "exploration"
    EXPORT = "export"
    COMPLETE = "complete"


@dataclass
class MenuItem:
    """A single menu item."""

    key: str
    label: str
    description: str
    action: MenuAction = MenuAction.SELECT
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Menu:
    """A menu with items and context."""

    title: str
    subtitle: Optional[str] = None
    items: List[MenuItem] = field(default_factory=list)
    allow_back: bool = True
    allow_quit: bool = True
    default_item: Optional[str] = None


@dataclass
class Prompt:
    """A context-sensitive prompt."""

    message: str
    prompt_type: str = "text"  # text, choice, confirm, path, int
    choices: Optional[List[Tuple[str, str]]] = None  # (value, label)
    default: Optional[str] = None
    validator: Optional[Callable[[str], Tuple[bool, str]]] = None
    help_text: Optional[str] = None


class PromptType(enum.Enum):
    """Types of prompts."""

    TEXT = "text"
    CHOICE = "choice"
    CONFIRM = "confirm"
    PATH = "path"
    INT = "int"


@dataclass
class PromptResult:
    """Result of a prompt interaction."""

    cancelled: bool
    value: Any = None
    error: Optional[str] = None


@dataclass
class NavigationState:
    """Current navigation state."""

    current_phase: WorkflowPhase = WorkflowPhase.WELCOME
    history: List[WorkflowPhase] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    workflow_id: Optional[str] = None


class InteractiveNavigator:
    """Manages guided interactive navigation through workflows.

    This class is a pure navigation controller — it contains NO scientific
    logic. It only manages menus, prompts, and phase transitions.
    """

    def __init__(self) -> None:
        self.state = NavigationState()
        self._phase_handlers: Dict[WorkflowPhase, Callable] = {}
        self._callbacks: List[Callable[[WorkflowPhase, WorkflowPhase], None]] = []

    def register_phase_handler(self, phase: WorkflowPhase, handler: Callable[[], MenuAction]) -> None:
        """Register a handler for a workflow phase."""
        self._phase_handlers[phase] = handler

    def register_transition_callback(self, callback: Callable[[WorkflowPhase, WorkflowPhase], None]) -> None:
        """Register a callback for phase transitions."""
        self._callbacks.append(callback)

    def transition_to(self, phase: WorkflowPhase) -> None:
        """Transition to a new phase."""
        old_phase = self.state.current_phase
        if old_phase != phase:
            self.state.history.append(old_phase)
            self.state.current_phase = phase
            for cb in self._callbacks:
                try:
                    cb(old_phase, phase)
                except Exception:
                    pass  # Callbacks must not break navigation

    def go_back(self) -> bool:
        """Go back to previous phase."""
        if self.state.history:
            previous = self.state.history.pop()
            self.state.current_phase = previous
            return True
        return False

    def get_current_phase(self) -> WorkflowPhase:
        """Get the current phase."""
        return self.state.current_phase

    def set_context(self, key: str, value: Any) -> None:
        """Set a context value."""
        self.state.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value."""
        return self.state.context.get(key, default)

    def clear_context(self) -> None:
        """Clear all context."""
        self.state.context.clear()

    def run_phase(self) -> MenuAction:
        """Run the current phase handler."""
        handler = self._phase_handlers.get(self.state.current_phase)
        if handler:
            return handler()
        return MenuAction.QUIT

    def create_menu(self, **kwargs) -> Menu:
        """Factory for creating menus."""
        return Menu(**kwargs)

    def create_prompt(self, **kwargs) -> Prompt:
        """Factory for creating prompts."""
        return Prompt(**kwargs)


# -----------------------------------------------------------------------------
# Standard Menu Builders
# -----------------------------------------------------------------------------


def build_welcome_menu(version: str) -> Menu:
    """Build the welcome/entry menu."""
    return Menu(
        title="MIIE — Measurement Integrity Intelligence Engine",
        subtitle=f"Version {version} | Guided Scientific Analysis",
        items=[
            MenuItem(
                "1",
                "Analyze Repository",
                "Run full scientific analysis pipeline on a Git repository",
                metadata={"workflow": "analyze"},
            ),
            MenuItem(
                "2",
                "Validate Repository",
                "Check repository validity without full analysis",
                metadata={"workflow": "validate"},
            ),
            MenuItem(
                "3",
                "Inspect Previous Results",
                "Explore cached analysis results without re-running",
                metadata={"workflow": "inspect"},
            ),
            MenuItem(
                "4",
                "Run Benchmark",
                "Execute benchmark suite against detectors",
                metadata={"workflow": "benchmark"},
            ),
            MenuItem(
                "5",
                "Configuration",
                "View and modify MIIE configuration",
                metadata={"workflow": "config"},
            ),
            MenuItem(
                "6",
                "System Status",
                "Show engine and detector status",
                metadata={"workflow": "status"},
            ),
            MenuItem(
                "?",
                "Help & Documentation",
                "Show help, shortcuts, and documentation links",
                action=MenuAction.HELP,
            ),
        ],
        allow_quit=True,
        default_item="1",
    )


def build_repository_select_menu(recent_repos: List[Dict[str, str]], has_cached: bool) -> Menu:
    """Build the repository selection menu."""
    items = []

    if recent_repos:
        items.append(
            MenuItem(
                "r",
                "Recent Repositories",
                f"Select from {len(recent_repos)} recently analyzed repositories",
                metadata={"submenu": "recent"},
            )
        )

    items.extend(
        [
            MenuItem(
                "l",
                "Local Path",
                "Enter path to a local Git repository",
                metadata={"input_type": "local_path"},
            ),
            MenuItem(
                "g",
                "GitHub URL",
                "Enter a GitHub repository URL (https://github.com/owner/repo)",
                metadata={"input_type": "github_url"},
            ),
            MenuItem(
                "c",
                "Clone & Analyze",
                "Clone a remote repository to a temporary directory and analyze",
                metadata={"input_type": "clone"},
            ),
        ]
    )

    if has_cached:
        items.append(
            MenuItem(
                "s",
                "Cached Session",
                "Resume from a saved session",
                metadata={"input_type": "session"},
            )
        )

    items.append(MenuItem("b", "Back", "Return to main menu", action=MenuAction.BACK))

    return Menu(
        title="Select Repository",
        subtitle="Choose the repository to analyze",
        items=items,
        allow_back=True,
    )


def build_configuration_review_menu(config: Dict[str, Any]) -> Menu:
    """Build the configuration review menu."""
    items = []

    # Display current config as read-only items
    config_items = [
        ("Metrics", ", ".join(config.get("metrics", ["M-02", "M-06"]))),
        ("Detectors", ", ".join(config.get("detectors", ["D-01", "D-02", "D-03"]))),
        ("Window Strategy", config.get("window_strategy", "time")),
        ("Window Size", f"{config.get('window_size', 7)} days"),
        ("Output Directory", config.get("output_dir", "./output")),
        ("Output Formats", ", ".join(config.get("formats", ["json"]))),
        ("Exclude Bots", "Yes" if config.get("exclude_bots") else "No"),
        ("Forensic Mode", "Yes" if config.get("forensic") else "No"),
        ("Random Seed", str(config.get("seed", 42))),
    ]

    for label, value in config_items:
        items.append(
            MenuItem(
                key="",
                label=f"{label}: {value}",
                description="",
                enabled=False,  # Read-only display
            )
        )

    items.extend(
        [
            MenuItem("m", "Modify Metrics", "Change which metrics to extract"),
            MenuItem("d", "Modify Detectors", "Change which detectors to run"),
            MenuItem("w", "Modify Windowing", "Change segmentation strategy/size"),
            MenuItem("o", "Modify Output", "Change output directory/formats"),
            MenuItem("a", "Advanced Options", "Thresholds, auth token, forensic mode"),
            MenuItem("c", "Continue", "Proceed with current configuration", action=MenuAction.CONFIRM),
            MenuItem("b", "Back", "Return to repository selection", action=MenuAction.BACK),
        ]
    )

    return Menu(
        title="Review Configuration",
        subtitle="Verify analysis parameters before execution",
        items=items,
        allow_back=True,
        default_item="c",
    )


def build_confirmation_menu(repo_display: str, config_summary: str, estimated_stages: int) -> Menu:
    """Build the execution confirmation menu."""
    return Menu(
        title="Confirm Analysis",
        subtitle=f"Repository: {repo_display}\n{config_summary}\nEstimated stages: {estimated_stages}",
        items=[
            MenuItem(
                "y",
                "Start Analysis",
                "Begin the scientific analysis pipeline",
                action=MenuAction.CONFIRM,
            ),
            MenuItem(
                "d",
                "Dry Run",
                "Show execution plan without running",
                metadata={"dry_run": True},
            ),
            MenuItem(
                "e",
                "Edit Configuration",
                "Return to configuration review",
                action=MenuAction.BACK,
            ),
            MenuItem(
                "b",
                "Back",
                "Return to repository selection",
                action=MenuAction.BACK,
            ),
        ],
        allow_back=True,
        default_item="y",
    )


def build_progress_menu(
    current_stage: int,
    total_stages: int,
    stage_name: str,
    stage_description: str,
    elapsed: float,
    can_pause: bool = True,
    can_cancel: bool = True,
) -> Menu:
    """Build the progress monitoring menu."""
    progress_pct = (current_stage / total_stages * 100) if total_stages > 0 else 0

    items = [
        MenuItem(
            "",
            f"Progress: {current_stage}/{total_stages} ({progress_pct:.0f}%)",
            f"Stage {current_stage}: {stage_name} — {stage_description}",
            enabled=False,
        ),
        MenuItem(
            "",
            f"Elapsed: {elapsed:.1f}s",
            "",
            enabled=False,
        ),
    ]

    actions = []
    if can_pause:
        actions.append(MenuItem("p", "Pause", "Pause execution (can resume later)", metadata={"action": "pause"}))
    if can_cancel:
        actions.append(MenuItem("x", "Cancel", "Stop execution (partial results saved)", metadata={"action": "cancel"}))
    actions.append(MenuItem("", "Waiting for stage completion...", "", enabled=False))

    return Menu(
        title="Pipeline Execution",
        subtitle=f"Stage {current_stage} of {total_stages}: {stage_name}",
        items=items + actions,
        allow_back=False,
        allow_quit=False,
    )


def build_results_menu(
    integrity_score: float,
    confidence_score: float,
    verdict: str,
    risk_level: str,
    triggered_count: int = 0,
    total_detectors: int = 0,
    has_cached: bool = True,
) -> Menu:
    """Build the results exploration menu."""
    items = [
        MenuItem(
            "",
            f"Integrity Score: {integrity_score:.4f} ({verdict})",
            "",
            enabled=False,
        ),
        MenuItem(
            "",
            f"Confidence Score: {confidence_score:.4f}",
            "",
            enabled=False,
        ),
        MenuItem(
            "",
            f"Risk Level: {risk_level}",
            "",
            enabled=False,
        ),
        MenuItem(
            "",
            f"Detectors: {triggered_count}/{total_detectors} triggered",
            "",
            enabled=False,
        ),
        MenuItem("", "", "", enabled=False),  # Separator
        MenuItem(
            "1",
            "View Metrics",
            "Inspect extracted metric values and trends",
            action=MenuAction.EXPLORE,
            metadata={"category": "metrics"},
        ),
        MenuItem(
            "2",
            "View Detectors",
            "Inspect detector outputs and triggered status",
            action=MenuAction.EXPLORE,
            metadata={"category": "detectors"},
        ),
        MenuItem(
            "3",
            "View Evidence",
            "Inspect evidence package and supporting data",
            action=MenuAction.EXPLORE,
            metadata={"category": "evidence"},
        ),
        MenuItem(
            "4",
            "View Confidence",
            "Inspect confidence intervals and uncertainty",
            action=MenuAction.EXPLORE,
            metadata={"category": "confidence"},
        ),
        MenuItem(
            "5",
            "View Integrity",
            "Inspect integrity scoring breakdown",
            action=MenuAction.EXPLORE,
            metadata={"category": "integrity"},
        ),
        MenuItem(
            "6",
            "View Validation",
            "Inspect validation results and warnings",
            action=MenuAction.EXPLORE,
            metadata={"category": "validation"},
        ),
        MenuItem(
            "7",
            "View Benchmark",
            "Inspect benchmark comparison (if available)",
            action=MenuAction.EXPLORE,
            metadata={"category": "benchmark"},
        ),
        MenuItem("", "", "", enabled=False),  # Separator
        MenuItem("e", "Export Results", "Export to JSON, Markdown, YAML, or CSV", action=MenuAction.EXPORT),
        MenuItem("s", "Save Session", "Save current session for later resume"),
    ]

    if has_cached:
        items.append(MenuItem("n", "New Analysis", "Start a new analysis", action=MenuAction.NEW))

    items.append(MenuItem("b", "Back", "Return to main menu", action=MenuAction.BACK))

    return Menu(
        title="Analysis Results",
        subtitle=f"Verdict: {verdict} | Risk: {risk_level}",
        items=items,
        allow_back=True,
    )


def build_exploration_menu(category: str, items: List[Dict[str, Any]]) -> Menu:
    """Build a result exploration submenu."""
    menu_items = []

    for i, item in enumerate(items, 1):
        menu_items.append(
            MenuItem(
                str(i),
                item.get("title", f"Item {i}"),
                item.get("description", ""),
                metadata={"detail": item},
            )
        )

    menu_items.append(MenuItem("b", "Back", "Return to results menu", action=MenuAction.BACK))

    return Menu(
        title=f"Explore: {category}",
        subtitle=f"{len(items)} items available",
        items=menu_items,
        allow_back=True,
    )


def build_export_menu(available_formats: List[str]) -> Menu:
    """Build the export format selection menu."""
    items = []

    format_info = {
        "json": ("JSON", "Complete structured data with all scientific results"),
        "md": ("Markdown", "Human-readable report with findings and recommendations"),
        "yaml": ("YAML", "Structured data in YAML format"),
        "csv": ("CSV", "Tabular metrics and scores for spreadsheet analysis"),
    }

    for fmt in available_formats:
        label, desc = format_info.get(fmt, (fmt.upper(), f"Export as {fmt}"))
        items.append(MenuItem(fmt, f"Export as {label}", desc, metadata={"format": fmt}))

    items.append(MenuItem("a", "All Formats", "Export in all available formats"))
    items.append(MenuItem("b", "Back", "Return to results menu", action=MenuAction.BACK))

    return Menu(
        title="Export Results",
        subtitle="Choose output format(s)",
        items=items,
        allow_back=True,
    )


def build_config_menu(current_config: Dict[str, Any]) -> Menu:
    """Build the configuration management menu."""
    items = [
        MenuItem("v", "View Current Config", "Display all configuration values"),
        MenuItem("e", "Edit Config", "Interactively modify configuration"),
        MenuItem("r", "Reset to Defaults", "Restore factory default configuration"),
        MenuItem("s", "Save Config", "Persist configuration to disk"),
        MenuItem("i", "Import Config", "Load configuration from file"),
        MenuItem("x", "Export Config", "Save configuration to file"),
        MenuItem("b", "Back", "Return to main menu", action=MenuAction.BACK),
    ]

    return Menu(
        title="Configuration",
        subtitle="Manage MIIE settings",
        items=items,
        allow_back=True,
    )


# -----------------------------------------------------------------------------
# Prompt Builders
# -----------------------------------------------------------------------------


def build_repository_path_prompt() -> Prompt:
    """Prompt for local repository path."""
    return Prompt(
        message="Enter path to local Git repository",
        prompt_type="path",
        help_text="Absolute or relative path to a directory containing a .git folder",
        validator=lambda p: (len(p) > 0, "Path cannot be empty"),
    )


def build_github_url_prompt() -> Prompt:
    """Prompt for GitHub URL."""
    return Prompt(
        message="Enter GitHub repository URL",
        prompt_type="text",
        help_text="Format: https://github.com/owner/repo or git@github.com:owner/repo.git",
        validator=lambda u: (
            u.startswith(("https://github.com/", "git@github.com:")),
            "Must be a valid GitHub URL",
        ),
    )


def build_auth_token_prompt() -> Prompt:
    """Prompt for GitHub auth token."""
    return Prompt(
        message="Enter GitHub Personal Access Token (optional)",
        prompt_type="text",
        help_text="Required for private repos. Falls back to GITHUB_TOKEN env var. Leave blank to skip.",
        default="",
    )


def build_metrics_selection_prompt(available: List[str], current: List[str]) -> Prompt:
    """Prompt for metric selection."""
    choices = [(m, f"{m} - {METRIC_LABELS.get(m, 'Unknown')}") for m in available]
    current_str = ",".join(current)
    return Prompt(
        message="Select metrics to extract (comma-separated)",
        prompt_type="choice",
        choices=choices,
        default=current_str,
        help_text=f"Available: {', '.join(available)}. Current: {current_str}",
    )


def build_detectors_selection_prompt(available: List[str], current: List[str]) -> Prompt:
    """Prompt for detector selection."""
    choices = [(d, f"{d} - {DETECTOR_LABELS.get(d, 'Unknown')}") for d in available]
    current_str = ",".join(current)
    return Prompt(
        message="Select detectors to run (comma-separated)",
        prompt_type="choice",
        choices=choices,
        default=current_str,
        help_text=f"Available: {', '.join(available)}. Current: {current_str}",
    )


def build_window_strategy_prompt(current: str) -> Prompt:
    """Prompt for window segmentation strategy."""
    choices = [
        ("time", "Time-based (days)"),
        ("commit", "Commit-count based"),
        ("release", "Release/tag based"),
        ("custom", "Custom boundaries"),
    ]
    return Prompt(
        message="Select window segmentation strategy",
        prompt_type="choice",
        choices=choices,
        default=current,
        help_text="How to segment the repository history into analysis windows",
    )


def build_window_size_prompt(current: int, strategy: str) -> Prompt:
    """Prompt for window size."""
    unit = "days" if strategy == "time" else "commits" if strategy == "commit" else "releases"
    return Prompt(
        message=f"Window size ({unit})",
        prompt_type="int",
        default=str(current),
        validator=lambda s: (
            s.isdigit() and int(s) > 0,
            f"Must be a positive integer ({unit})",
        ),
        help_text=f"Number of {unit} per analysis window",
    )


def build_output_dir_prompt(current: str) -> Prompt:
    """Prompt for output directory."""
    return Prompt(
        message="Output directory",
        prompt_type="path",
        default=current,
        help_text="Directory where reports and artifacts will be written",
    )


def build_formats_selection_prompt(available: List[str], current: List[str]) -> Prompt:
    """Prompt for output format selection."""
    choices = [(f, f"{f.upper()} format") for f in available]
    current_str = ",".join(current)
    return Prompt(
        message="Select output formats (comma-separated)",
        prompt_type="choice",
        choices=choices,
        default=current_str,
        help_text=f"Available: {', '.join(available)}. Current: {current_str}",
    )


def build_confirm_prompt(message: str, default_yes: bool = True) -> Prompt:
    """Prompt for yes/no confirmation."""
    default = "y" if default_yes else "n"
    return Prompt(
        message=message,
        prompt_type="confirm",
        default=default,
        help_text="Press Enter for default, or type y/n",
    )


# -----------------------------------------------------------------------------
# Domain Labels (from frozen scientific spec)
# -----------------------------------------------------------------------------

DETECTOR_LABELS: Dict[str, str] = {
    "D-01": "Distribution Drift",
    "D-02": "Correlation Breakdown",
    "D-03": "Threshold Compression",
}

METRIC_LABELS: Dict[str, str] = {
    "M-01": "Commit Frequency",
    "M-02": "Code Churn",
    "M-03": "Review Coverage",
    "M-04": "Review Latency",
    "M-05": "Test Coverage Delta",
    "M-06": "Defect Ratio",
    "M-07": "Complexity Trend",
}

AVAILABLE_METRICS = list(METRIC_LABELS.keys())
AVAILABLE_DETECTORS = list(DETECTOR_LABELS.keys())
AVAILABLE_FORMATS = ["json", "md", "yaml", "csv"]
AVAILABLE_WINDOW_STRATEGIES = ["time", "commit", "release", "custom"]
