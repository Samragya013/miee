"""
MIIE v1.6 Quality State Machine — State transitions for observation quality.

Implements OVR-v1.0 §8 quality state machine.
Manages quality state transitions with validation.

Reference: OVR-v1.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Set, Tuple

from miie.contracts.observation_types import (
    VALID_QUALITY_TRANSITIONS,
    QualityState,
    QualityStateTransition,
)

# ---------------------------------------------------------------------------
# Quality State Machine (OVR §8.2)
# ---------------------------------------------------------------------------


class QualityStateMachine:
    """OVR §8.2 — Quality state machine for observation quality.

    Manages state transitions with validation and history tracking.
    """

    def __init__(
        self,
        initial_state: QualityState = QualityState.COMPLETE,
        transitions: Optional[List[QualityStateTransition]] = None,
    ) -> None:
        """Initialize the quality state machine.

        Args:
            initial_state: Initial quality state.
            transitions: Optional list of valid transitions.
                         If None, uses default transitions.
        """
        self._state = initial_state
        self._transitions = transitions or VALID_QUALITY_TRANSITIONS
        self._history: List[Tuple[QualityState, QualityState, str, datetime]] = []
        self._transition_map = self._build_transition_map()

    def _build_transition_map(self) -> Dict[Tuple[QualityState, str], QualityState]:
        """Build lookup map for valid transitions.

        Returns:
            Dict mapping (source_state, trigger) to target_state.
        """
        transition_map: Dict[Tuple[QualityState, str], QualityState] = {}
        for transition in self._transitions:
            key = (transition.source, transition.trigger)
            transition_map[key] = transition.target
        return transition_map

    @property
    def state(self) -> QualityState:
        """Get current quality state."""
        return self._state

    @property
    def history(self) -> List[Tuple[QualityState, QualityState, str, datetime]]:
        """Get transition history.

        Returns:
            List of (from_state, to_state, trigger, timestamp) tuples.
        """
        return list(self._history)

    def can_transition(self, trigger: str) -> bool:
        """Check if a transition is valid from current state.

        Args:
            trigger: Transition trigger name.

        Returns:
            True if transition is valid.
        """
        key = (self._state, trigger)
        return key in self._transition_map

    def get_valid_triggers(self) -> List[str]:
        """Get list of valid triggers from current state.

        Returns:
            List of valid trigger names.
        """
        return [trigger for (state, trigger) in self._transition_map.keys() if state == self._state]

    def transition(self, trigger: str) -> QualityState:
        """Execute a state transition.

        Args:
            trigger: Transition trigger name.

        Returns:
            New quality state after transition.

        Raises:
            InvalidTransitionError: If transition is not valid.
        """
        key = (self._state, trigger)
        if key not in self._transition_map:
            valid_triggers = self.get_valid_triggers()
            raise InvalidTransitionError(
                f"Invalid transition: {self._state.value} + '{trigger}'. " f"Valid triggers: {valid_triggers}"
            )

        new_state = self._transition_map[key]
        old_state = self._state
        timestamp = datetime.now(timezone.utc)

        self._state = new_state
        self._history.append((old_state, new_state, trigger, timestamp))

        return new_state

    def reset(self, state: QualityState = QualityState.COMPLETE) -> None:
        """Reset state machine to a specific state.

        Args:
            state: State to reset to.
        """
        self._state = state
        self._history.clear()

    def get_duration_in_state(self) -> float:
        """Get duration in current state in seconds.

        Returns:
            Duration in seconds since last transition.
        """
        if not self._history:
            return 0.0

        last_transition_time = self._history[-1][3]
        now = datetime.now(timezone.utc)
        return (now - last_transition_time).total_seconds()

    def get_state_counts(self) -> Dict[QualityState, int]:
        """Get count of each state in history.

        Returns:
            Dict mapping state to count.
        """
        counts: Dict[QualityState, int] = {state: 0 for state in QualityState}
        for from_state, _, _, _ in self._history:
            counts[from_state] += 1
        # Count current state
        counts[self._state] += 1
        return counts


# ---------------------------------------------------------------------------
# Invalid Transition Error
# ---------------------------------------------------------------------------


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    pass


# ---------------------------------------------------------------------------
# Quality State Machine Factory
# ---------------------------------------------------------------------------


def create_quality_state_machine(
    initial_state: QualityState = QualityState.COMPLETE,
) -> QualityStateMachine:
    """Create a quality state machine with default transitions.

    Args:
        initial_state: Initial quality state.

    Returns:
        Configured QualityStateMachine instance.
    """
    return QualityStateMachine(initial_state=initial_state)


# ---------------------------------------------------------------------------
# Quality State Utilities (OVR §8.3)
# ---------------------------------------------------------------------------


def is_terminal_state(state: QualityState) -> bool:
    """Check if a state is terminal (no outgoing transitions).

    Args:
        state: Quality state to check.

    Returns:
        True if state is terminal.
    """
    terminal_states = {QualityState.MISSING}
    return state in terminal_states


def is_recoverable_state(state: QualityState) -> bool:
    """Check if a state can recover to COMPLETE.

    Args:
        state: Quality state to check.

    Returns:
        True if state can eventually reach COMPLETE.
    """
    recoverable_states = {
        QualityState.COMPLETE,
        QualityState.DEGRADED,
        QualityState.UNCERTAIN,
        QualityState.RECOVERING,
        QualityState.MISSING,
    }
    return state in recoverable_states


def get_recovery_path(
    from_state: QualityState,
    transitions: Optional[List[QualityStateTransition]] = None,
) -> List[Tuple[QualityState, str]]:
    """Get the path from a state back to COMPLETE.

    Args:
        from_state: Starting state.
        transitions: Optional list of transitions.
                     If None, uses default transitions.

    Returns:
        List of (state, trigger) tuples representing recovery path.
    """
    transitions = transitions or VALID_QUALITY_TRANSITIONS
    transition_map: Dict[Tuple[QualityState, str], QualityState] = {}
    for t in transitions:
        key = (t.source, t.trigger)
        transition_map[key] = t.target

    # BFS to find path to COMPLETE
    from collections import deque

    queue: deque[Tuple[QualityState, List[Tuple[QualityState, str]]]] = deque()
    queue.append((from_state, []))
    visited: Set[QualityState] = {from_state}

    while queue:
        current_state, path = queue.popleft()

        if current_state == QualityState.COMPLETE:
            return path

        for (state, trigger), target in transition_map.items():
            if state == current_state and target not in visited:
                visited.add(target)
                new_path = path + [(current_state, trigger)]
                queue.append((target, new_path))

    # No path found
    return []


def calculate_quality_score(state: QualityState) -> float:
    """Calculate a numeric score for a quality state.

    Args:
        state: Quality state.

    Returns:
        Score between 0.0 and 1.0.
    """
    scores = {
        QualityState.COMPLETE: 1.0,
        QualityState.RECOVERING: 0.8,
        QualityState.DEGRADED: 0.6,
        QualityState.UNCERTAIN: 0.4,
        QualityState.STALE: 0.2,
        QualityState.MISSING: 0.0,
    }
    return scores.get(state, 0.0)
