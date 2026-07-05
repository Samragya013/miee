"""Tests for miie.providers.lifecycle module."""

from unittest.mock import MagicMock

from miie.providers.context import ProviderContext, ProviderState
from miie.providers.lifecycle import (
    LifecycleState,
    LifecycleTransition,
    ProviderLifecycleAudit,
    ProviderLifecycleManager,
)


class TestLifecycleState:
    def test_uninitialized(self):
        assert LifecycleState.UNINITIALIZED.value == "uninitialized"

    def test_initializing(self):
        assert LifecycleState.INITIALIZING.value == "initializing"

    def test_configuring(self):
        assert LifecycleState.CONFIGURING.value == "configuring"

    def test_validating(self):
        assert LifecycleState.VALIDATING.value == "validating"

    def test_ready(self):
        assert LifecycleState.READY.value == "ready"

    def test_executing(self):
        assert LifecycleState.EXECUTING.value == "executing"

    def test_normalizing(self):
        assert LifecycleState.NORMALIZING.value == "normalizing"

    def test_disposed(self):
        assert LifecycleState.DISPOSED.value == "disposed"

    def test_failed(self):
        assert LifecycleState.FAILED.value == "failed"


class TestLifecycleTransition:
    def test_creation(self):
        transition = LifecycleTransition(
            provider_id="git",
            from_state=LifecycleState.UNINITIALIZED,
            to_state=LifecycleState.READY,
            trigger="test",
        )
        assert transition.provider_id == "git"
        assert transition.from_state == LifecycleState.UNINITIALIZED
        assert transition.to_state == LifecycleState.READY
        assert transition.success

    def test_to_dict(self):
        transition = LifecycleTransition(
            provider_id="git",
            from_state=LifecycleState.UNINITIALIZED,
            to_state=LifecycleState.READY,
            trigger="test",
        )
        d = transition.to_dict()
        assert d["provider_id"] == "git"
        assert d["from_state"] == "uninitialized"
        assert d["to_state"] == "ready"
        assert d["success"]


class TestProviderLifecycleAudit:
    def test_record_and_get_transitions(self):
        audit = ProviderLifecycleAudit()
        transition = LifecycleTransition(
            provider_id="git",
            from_state=LifecycleState.UNINITIALIZED,
            to_state=LifecycleState.READY,
            trigger="test",
        )
        audit.record(transition)
        transitions = audit.get_transitions("git")
        assert len(transitions) == 1

    def test_get_current_state(self):
        audit = ProviderLifecycleAudit()
        transition = LifecycleTransition(
            provider_id="git",
            from_state=LifecycleState.UNINITIALIZED,
            to_state=LifecycleState.READY,
            trigger="test",
        )
        audit.record(transition)
        assert audit.get_current_state("git") == LifecycleState.READY

    def test_get_current_state_default(self):
        audit = ProviderLifecycleAudit()
        assert audit.get_current_state("git") == LifecycleState.UNINITIALIZED

    def test_get_audit_trail(self):
        audit = ProviderLifecycleAudit()
        transition = LifecycleTransition(
            provider_id="git",
            from_state=LifecycleState.UNINITIALIZED,
            to_state=LifecycleState.READY,
            trigger="test",
        )
        audit.record(transition)
        trail = audit.get_audit_trail("git")
        assert len(trail) == 1
        assert trail[0]["provider_id"] == "git"

    def test_clear(self):
        audit = ProviderLifecycleAudit()
        transition = LifecycleTransition(
            provider_id="git",
            from_state=LifecycleState.UNINITIALIZED,
            to_state=LifecycleState.READY,
            trigger="test",
        )
        audit.record(transition)
        audit.clear("git")
        assert audit.get_current_state("git") == LifecycleState.UNINITIALIZED

    def test_tracked_providers(self):
        audit = ProviderLifecycleAudit()
        transition = LifecycleTransition(
            provider_id="git",
            from_state=LifecycleState.UNINITIALIZED,
            to_state=LifecycleState.READY,
            trigger="test",
        )
        audit.record(transition)
        assert "git" in audit.tracked_providers


class TestProviderLifecycleManager:
    def test_initialization(self):
        health_monitor = MagicMock()
        mgr = ProviderLifecycleManager(health_monitor)
        assert mgr.audit is not None

    def test_initialize(self):
        health_monitor = MagicMock()
        mgr = ProviderLifecycleManager(health_monitor)
        provider = MagicMock()
        provider.provider_id = "test"
        provider.state = ProviderState.UNINITIALIZED
        context = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-1",
            analysis_id="analysis-1",
        )
        result = mgr.initialize(provider, context)
        assert result
        provider.initialize.assert_called_once_with(context)

    def test_configure(self):
        health_monitor = MagicMock()
        mgr = ProviderLifecycleManager(health_monitor)
        provider = MagicMock()
        provider.provider_id = "test"
        provider.state = ProviderState.UNINITIALIZED
        context = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-1",
            analysis_id="analysis-1",
        )
        mgr.initialize(provider, context)
        provider.state = ProviderState.READY
        result = mgr.configure(provider, {"key": "value"})
        assert result

    def test_validate(self):
        health_monitor = MagicMock()
        mgr = ProviderLifecycleManager(health_monitor)
        provider = MagicMock()
        provider.provider_id = "test"
        provider.state = ProviderState.UNINITIALIZED
        context = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-1",
            analysis_id="analysis-1",
        )
        mgr.initialize(provider, context)
        provider.state = ProviderState.READY
        result = mgr.validate(provider)
        assert result.is_valid

    def test_execute_success(self):
        health_monitor = MagicMock()
        mgr = ProviderLifecycleManager(health_monitor)
        provider = MagicMock()
        provider.provider_id = "test"
        provider.state = ProviderState.UNINITIALIZED
        context = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-1",
            analysis_id="analysis-1",
        )
        mgr.initialize(provider, context)
        provider.state = ProviderState.READY
        from miie.providers.context import ExtractionResult, QualityState

        mock_result = ExtractionResult(
            provider_id="test",
            metric_id="M-02",
            observations=(1, 2, 3),
            quality_state=QualityState.COMPLETE,
            confidence=0.9,
        )
        provider.extract_observations.return_value = mock_result
        result = mgr.execute(provider, context, ["M-02"])
        assert result.observation_count == 3

    def test_cleanup(self):
        health_monitor = MagicMock()
        mgr = ProviderLifecycleManager(health_monitor)
        provider = MagicMock()
        provider.provider_id = "test"
        provider.state = ProviderState.UNINITIALIZED
        context = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-1",
            analysis_id="analysis-1",
        )
        mgr.initialize(provider, context)
        provider.state = ProviderState.READY
        mgr.cleanup(provider)
        provider.dispose.assert_called_once()

    def test_shutdown(self):
        health_monitor = MagicMock()
        mgr = ProviderLifecycleManager(health_monitor)
        provider = MagicMock()
        provider.provider_id = "test"
        provider.state = ProviderState.UNINITIALIZED
        context = ProviderContext(
            repo_path="/tmp/repo",
            repository_id="repo-1",
            analysis_id="analysis-1",
        )
        mgr.initialize(provider, context)
        provider.state = ProviderState.READY
        mgr.shutdown(provider)
        provider.dispose.assert_called_once()

    def test_get_audit(self):
        health_monitor = MagicMock()
        mgr = ProviderLifecycleManager(health_monitor)
        audit = mgr.audit
        assert audit is not None
        assert isinstance(audit, ProviderLifecycleAudit)
