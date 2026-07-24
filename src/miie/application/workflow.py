"""Workflow Engine — deterministic step-by-step pipeline execution.

The workflow engine manages guided execution of analysis pipelines.
It supports step navigation, resume, cancel, status, and progress
without containing any scientific logic.

Each workflow is a sequence of WorkflowSteps. Steps are executed
deterministically. The engine tracks state and allows interruption
and resumption.
"""

from __future__ import annotations

import enum
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


class WorkflowState(enum.Enum):
    """Workflow lifecycle states."""

    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """A single step in a workflow.

    Attributes:
        step_id: Unique identifier for the step.
        name: Human-readable name.
        description: What this step does.
        handler: Callable that executes the step. Receives context dict.
        order: Execution order (0-indexed).
        optional: If True, failure does not abort the workflow.
    """

    step_id: str
    name: str
    description: str
    handler: Callable[..., Any]
    order: int
    optional: bool = False


@dataclass
class StepResult:
    """Result of executing a single step."""

    step_id: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_seconds: float = 0.0


@dataclass
class WorkflowResult:
    """Complete result of a workflow execution."""

    workflow_id: str
    state: WorkflowState
    steps_completed: int
    steps_total: int
    step_results: List[StepResult] = field(default_factory=list)
    total_duration_seconds: float = 0.0
    error: Optional[str] = None


class WorkflowEngine:
    """Deterministic workflow execution engine.

    Manages step-by-step execution with:
    - Sequential step execution
    - Progress tracking
    - Pause/resume support
    - Cancel support
    - Step-level error isolation

    The engine contains NO scientific logic. It executes callables
    that are provided by the application service.
    """

    def __init__(self) -> None:
        self._steps: List[WorkflowStep] = []
        self._state: WorkflowState = WorkflowState.CREATED
        self._current_step_index: int = 0
        self._step_results: List[StepResult] = []
        self._context: Dict[str, Any] = {}
        self._workflow_id: str = ""
        self._start_time: float = 0.0
        self._callbacks: List[Callable[[str, WorkflowState, Optional[str]], None]] = []

    @property
    def state(self) -> WorkflowState:
        return self._state

    @property
    def current_step_index(self) -> int:
        return self._current_step_index

    @property
    def steps(self) -> List[WorkflowStep]:
        return list(self._steps)

    @property
    def workflow_id(self) -> str:
        return self._workflow_id

    def on_state_change(self, callback: Callable[[str, WorkflowState, Optional[str]], None]) -> None:
        """Register a callback for state changes.

        The callback receives (workflow_id, new_state, step_name).
        """
        self._callbacks.append(callback)

    def define(self, steps: List[WorkflowStep], context: Optional[Dict[str, Any]] = None) -> str:
        """Define a workflow with the given steps.

        Steps are sorted by order. Returns the workflow ID.
        """
        self._steps = sorted(steps, key=lambda s: s.order)
        self._context = context or {}
        self._state = WorkflowState.CREATED
        self._current_step_index = 0
        self._step_results = []
        self._workflow_id = uuid.uuid4().hex[:12]
        self._start_time = 0.0
        return self._workflow_id

    def execute(self) -> WorkflowResult:
        """Execute all steps sequentially.

        Returns a WorkflowResult with the outcome of each step.
        """
        if self._state == WorkflowState.RUNNING:
            raise RuntimeError("Workflow is already running")

        self._state = WorkflowState.RUNNING
        self._start_time = time.perf_counter()
        self._notify("running")

        try:
            while self._current_step_index < len(self._steps):
                step = self._steps[self._current_step_index]
                result = self._execute_step(step)
                self._step_results.append(result)

                if not result.success and not step.optional:
                    self._state = WorkflowState.FAILED
                    self._notify("failed", step.name)
                    return self._build_result()

                self._current_step_index += 1

            self._state = WorkflowState.COMPLETED
            self._notify("completed")
            return self._build_result()

        except Exception as exc:
            self._state = WorkflowState.FAILED
            self._notify("failed", str(exc))
            return self._build_result()

    def pause(self) -> None:
        """Pause the workflow. Can be resumed later."""
        if self._state != WorkflowState.RUNNING:
            raise RuntimeError("Can only pause a running workflow")
        self._state = WorkflowState.PAUSED
        self._notify("paused")

    def resume(self) -> WorkflowResult:
        """Resume a paused workflow."""
        if self._state != WorkflowState.PAUSED:
            raise RuntimeError("Can only resume a paused workflow")
        return self.execute()

    def cancel(self) -> None:
        """Cancel the workflow."""
        if self._state not in (WorkflowState.RUNNING, WorkflowState.PAUSED):
            raise RuntimeError("Can only cancel a running or paused workflow")
        self._state = WorkflowState.CANCELLED
        self._notify("cancelled")

    def get_progress(self) -> Dict[str, Any]:
        """Get current workflow progress."""
        total = len(self._steps)
        completed = len(self._step_results)
        return {
            "workflow_id": self._workflow_id,
            "state": self._state.value,
            "steps_completed": completed,
            "steps_total": total,
            "current_step": self._steps[self._current_step_index].name if self._current_step_index < total else None,
            "progress_percent": (completed / total * 100) if total > 0 else 0.0,
        }

    def _execute_step(self, step: WorkflowStep) -> StepResult:
        """Execute a single step and return its result."""
        t_start = time.perf_counter()
        try:
            output = step.handler(self._context)
            duration = time.perf_counter() - t_start
            return StepResult(
                step_id=step.step_id,
                success=True,
                output=output,
                duration_seconds=duration,
            )
        except Exception as exc:
            duration = time.perf_counter() - t_start
            return StepResult(
                step_id=step.step_id,
                success=False,
                error=str(exc),
                duration_seconds=duration,
            )

    def _build_result(self) -> WorkflowResult:
        """Build the final workflow result."""
        return WorkflowResult(
            workflow_id=self._workflow_id,
            state=self._state,
            steps_completed=len(self._step_results),
            steps_total=len(self._steps),
            step_results=self._step_results,
            total_duration_seconds=time.perf_counter() - self._start_time if self._start_time else 0.0,
        )

    def _notify(self, state: str, step_name: Optional[str] = None) -> None:
        """Notify callbacks of state change."""
        try:
            ws = WorkflowState(state)
        except ValueError:
            return
        for cb in self._callbacks:
            try:
                cb(self._workflow_id, ws, step_name)
            except Exception:
                pass
