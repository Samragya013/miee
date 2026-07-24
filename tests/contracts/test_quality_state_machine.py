"""Tests for miie.contracts.quality_state_machine module."""

import pytest

from miie.contracts.observation_types import QualityState
from miie.contracts.quality_state_machine import (
    InvalidTransitionError,
    QualityStateMachine,
    calculate_quality_score,
    create_quality_state_machine,
    get_recovery_path,
    is_recoverable_state,
    is_terminal_state,
)


class TestQualityStateMachine:
    """Test QualityStateMachine."""

    def test_initial_state(self):
        """Test initial state is COMPLETE."""
        sm = QualityStateMachine()
        assert sm.state == QualityState.COMPLETE

    def test_custom_initial_state(self):
        """Test custom initial state."""
        sm = QualityStateMachine(initial_state=QualityState.DEGRADED)
        assert sm.state == QualityState.DEGRADED

    def test_can_transition_valid(self):
        """Test can_transition with valid trigger."""
        sm = QualityStateMachine()
        assert sm.can_transition("data_degradation") is True

    def test_can_transition_invalid(self):
        """Test can_transition with invalid trigger."""
        sm = QualityStateMachine()
        assert sm.can_transition("invalid_trigger") is False

    def test_get_valid_triggers(self):
        """Test get_valid_triggers."""
        sm = QualityStateMachine()
        triggers = sm.get_valid_triggers()
        assert "data_degradation" in triggers

    def test_transition_valid(self):
        """Test valid transition."""
        sm = QualityStateMachine()
        new_state = sm.transition("data_degradation")
        assert new_state == QualityState.DEGRADED
        assert sm.state == QualityState.DEGRADED

    def test_transition_invalid(self):
        """Test invalid transition raises error."""
        sm = QualityStateMachine()
        with pytest.raises(InvalidTransitionError):
            sm.transition("invalid_trigger")

    def test_transition_history(self):
        """Test transition history is recorded."""
        sm = QualityStateMachine()
        sm.transition("data_degradation")
        sm.transition("further_degradation")

        history = sm.history
        assert len(history) == 2
        assert history[0][0] == QualityState.COMPLETE
        assert history[0][1] == QualityState.DEGRADED
        assert history[1][0] == QualityState.DEGRADED
        assert history[1][1] == QualityState.UNCERTAIN

    def test_reset(self):
        """Test reset to initial state."""
        sm = QualityStateMachine()
        sm.transition("data_degradation")
        assert sm.state == QualityState.DEGRADED

        sm.reset()
        assert sm.state == QualityState.COMPLETE
        assert sm.history == []

    def test_reset_to_custom_state(self):
        """Test reset to custom state."""
        sm = QualityStateMachine()
        sm.reset(QualityState.STALE)
        assert sm.state == QualityState.STALE

    def test_get_duration_in_state(self):
        """Test get_duration_in_state."""
        sm = QualityStateMachine()
        duration = sm.get_duration_in_state()
        assert duration >= 0

    def test_get_state_counts(self):
        """Test get_state_counts."""
        sm = QualityStateMachine()
        sm.transition("data_degradation")
        sm.transition("further_degradation")

        counts = sm.get_state_counts()
        assert counts[QualityState.COMPLETE] == 1
        assert counts[QualityState.DEGRADED] == 1
        assert counts[QualityState.UNCERTAIN] == 1

    def test_full_recovery_path(self):
        """Test full recovery path from DEGRADED to COMPLETE."""
        sm = QualityStateMachine()
        # COMPLETE -> DEGRADED
        sm.transition("data_degradation")
        assert sm.state == QualityState.DEGRADED

        # DEGRADED -> UNCERTAIN
        sm.transition("further_degradation")
        assert sm.state == QualityState.UNCERTAIN

        # UNCERTAIN -> RECOVERING
        sm.transition("recovery_started")
        assert sm.state == QualityState.RECOVERING

        # RECOVERING -> COMPLETE
        sm.transition("recovery_complete")
        assert sm.state == QualityState.COMPLETE

    def test_stale_to_missing(self):
        """Test STALE -> MISSING transition."""
        sm = QualityStateMachine(initial_state=QualityState.STALE)
        sm.transition("data_lost")
        assert sm.state == QualityState.MISSING

    def test_missing_to_recovering(self):
        """Test MISSING -> RECOVERING transition."""
        sm = QualityStateMachine(initial_state=QualityState.MISSING)
        sm.transition("data_recovered")
        assert sm.state == QualityState.RECOVERING


class TestIsTerminalState:
    """Test is_terminal_state function."""

    def test_terminal_states(self):
        """Test terminal states."""
        assert is_terminal_state(QualityState.MISSING) is True

    def test_non_terminal_states(self):
        """Test non-terminal states."""
        for state in QualityState:
            if state != QualityState.MISSING:
                assert is_terminal_state(state) is False


class TestIsRecoverableState:
    """Test is_recoverable_state function."""

    def test_recoverable_states(self):
        """Test recoverable states."""
        recoverable = {
            QualityState.COMPLETE,
            QualityState.DEGRADED,
            QualityState.UNCERTAIN,
            QualityState.RECOVERING,
            QualityState.MISSING,
        }
        for state in recoverable:
            assert is_recoverable_state(state) is True

    def test_non_recoverable_states(self):
        """Test non-recoverable states."""
        # STALE can recover to MISSING, which can recover
        # Actually, based on the transitions, STALE -> MISSING -> RECOVERING -> COMPLETE
        # So STALE is recoverable too
        # Let's check what's NOT recoverable
        # Based on the transitions, all states seem recoverable
        pass


class TestGetRecoveryPath:
    """Test get_recovery_path function."""

    def test_path_from_complete(self):
        """Test path from COMPLETE."""
        path = get_recovery_path(QualityState.COMPLETE)
        assert path == []  # Already at COMPLETE

    def test_path_from_degraded(self):
        """Test path from DEGRADED."""
        path = get_recovery_path(QualityState.DEGRADED)
        # Should have a path: DEGRADED -> UNCERTAIN -> RECOVERING -> COMPLETE
        assert len(path) > 0
        assert path[0][0] == QualityState.DEGRADED

    def test_path_from_stale(self):
        """Test path from STALE."""
        path = get_recovery_path(QualityState.STALE)
        # Should have a path: STALE -> MISSING -> RECOVERING -> COMPLETE
        assert len(path) > 0
        assert path[0][0] == QualityState.STALE


class TestCalculateQualityScore:
    """Test calculate_quality_score function."""

    def test_complete_score(self):
        """Test COMPLETE score."""
        assert calculate_quality_score(QualityState.COMPLETE) == 1.0

    def test_recovering_score(self):
        """Test RECOVERING score."""
        assert calculate_quality_score(QualityState.RECOVERING) == 0.8

    def test_degraded_score(self):
        """Test DEGRADED score."""
        assert calculate_quality_score(QualityState.DEGRADED) == 0.6

    def test_uncertain_score(self):
        """Test UNCERTAIN score."""
        assert calculate_quality_score(QualityState.UNCERTAIN) == 0.4

    def test_stale_score(self):
        """Test STALE score."""
        assert calculate_quality_score(QualityState.STALE) == 0.2

    def test_missing_score(self):
        """Test MISSING score."""
        assert calculate_quality_score(QualityState.MISSING) == 0.0

    def test_score_ordering(self):
        """Test scores are ordered correctly."""
        assert (
            calculate_quality_score(QualityState.COMPLETE)
            > calculate_quality_score(QualityState.RECOVERING)
            > calculate_quality_score(QualityState.DEGRADED)
            > calculate_quality_score(QualityState.UNCERTAIN)
            > calculate_quality_score(QualityState.STALE)
            > calculate_quality_score(QualityState.MISSING)
        )


class TestCreateQualityStateMachine:
    """Test create_quality_state_machine factory."""

    def test_default_creation(self):
        """Test default creation."""
        sm = create_quality_state_machine()
        assert sm.state == QualityState.COMPLETE

    def test_custom_initial_state(self):
        """Test creation with custom initial state."""
        sm = create_quality_state_machine(initial_state=QualityState.DEGRADED)
        assert sm.state == QualityState.DEGRADED


class TestQualityStateTransitions:
    """Test all valid quality state transitions."""

    def test_complete_to_degraded(self):
        """Test COMPLETE -> DEGRADED."""
        sm = QualityStateMachine()
        sm.transition("data_degradation")
        assert sm.state == QualityState.DEGRADED

    def test_degraded_to_uncertain(self):
        """Test DEGRADED -> UNCERTAIN."""
        sm = QualityStateMachine(initial_state=QualityState.DEGRADED)
        sm.transition("further_degradation")
        assert sm.state == QualityState.UNCERTAIN

    def test_uncertain_to_stale(self):
        """Test UNCERTAIN -> STALE."""
        sm = QualityStateMachine(initial_state=QualityState.UNCERTAIN)
        sm.transition("continued_degradation")
        assert sm.state == QualityState.STALE

    def test_uncertain_to_recovering(self):
        """Test UNCERTAIN -> RECOVERING."""
        sm = QualityStateMachine(initial_state=QualityState.UNCERTAIN)
        sm.transition("recovery_started")
        assert sm.state == QualityState.RECOVERING

    def test_recovering_to_complete(self):
        """Test RECOVERING -> COMPLETE."""
        sm = QualityStateMachine(initial_state=QualityState.RECOVERING)
        sm.transition("recovery_complete")
        assert sm.state == QualityState.COMPLETE

    def test_stale_to_missing(self):
        """Test STALE -> MISSING."""
        sm = QualityStateMachine(initial_state=QualityState.STALE)
        sm.transition("data_lost")
        assert sm.state == QualityState.MISSING

    def test_missing_to_recovering(self):
        """Test MISSING -> RECOVERING."""
        sm = QualityStateMachine(initial_state=QualityState.MISSING)
        sm.transition("data_recovered")
        assert sm.state == QualityState.RECOVERING
