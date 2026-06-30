"""
Detector Dispatcher Engine Implementation.

Implements the IDetectorEngine interface for invoking detectors on metric data.

Extended in v1.5 with observation-aware routing: when ObservationWindows are
provided, detectors that implement detect_observations() receive them directly.

Reference: IMS-v1.0 Phase 5, DES-v2.0 §24
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from miie.contracts.interfaces import IDetectorEngine
from miie.processing.detection.registry import DetectorRegistry
from miie.schemas.models import DetectorResults, MetricDataFrame


class DetectorDispatcherEngine(IDetectorEngine):
    """
    Dispatches metric data to detectors and orchestrates detection execution.

    Responsibilities:
    - Routing: Direct MetricDataFrame or ObservationWindows to detectors
    - Orchestration: Manage detector execution flow
    - Validation: Validate inputs and outputs
    - No detector mathematics: Only routing and coordination
    """

    def __init__(self, registry: DetectorRegistry):
        """
        Initialize detector dispatcher.

        Args:
            registry: DetectorRegistry containing registered detectors
        """
        self._registry = registry

    def invoke(
        self,
        metric_dataframe: MetricDataFrame,
        windows: List[object],  # List[WindowDefinition] but avoiding circular import
        detector_config: Optional[Dict[str, Dict[str, Any]]] = None,
        enabled_detectors: Optional[List[str]] = None,
    ) -> DetectorResults:
        """Invoke detectors on metric data.

        Args:
            metric_dataframe: Extracted metrics from ingestion
            windows: List of window definitions used for analysis
            detector_config: Optional configuration for detectors
            enabled_detectors: Optional list of detector IDs to enable (None for all)

        Returns:
            DetectorResults: Container for detector outputs
        """
        return self._dispatch(metric_dataframe, windows, detector_config, enabled_detectors)

    def invoke_observations(
        self,
        observation_windows: List[Any],
        detector_config: Optional[Dict[str, Dict[str, Any]]] = None,
        enabled_detectors: Optional[List[str]] = None,
    ) -> DetectorResults:
        """Invoke detectors using ObservationWindow data (v1.5 path).

        Routes to detect_observations() on detectors that support it,
        falling back to the legacy MetricDataFrame path via adapter.

        Args:
            observation_windows: List of ObservationWindow objects.
            detector_config: Optional configuration for detectors.
            enabled_detectors: Optional list of detector IDs to enable.

        Returns:
            DetectorResults: Container for detector outputs.
        """
        detector_outputs: Dict[str, Any] = {}

        if enabled_detectors is not None:
            detector_items = [
                (det_id, self._registry.get(det_id))
                for det_id in self._registry.get_registered_ids()
                if det_id in enabled_detectors and self._registry.get(det_id) is not None
            ]
        else:
            detector_items = [
                (det_id, self._registry.get(det_id))
                for det_id in self._registry.get_registered_ids()
                if self._registry.get(det_id) is not None
            ]

        for detector_id, detector in detector_items:
            try:
                # Get detector-specific config
                det_specific_config = detector_config.get(detector_id, {}) if detector_config else {}

                # Check if detector has observation-aware method
                if hasattr(detector, "detect_observations"):
                    detector_result = detector.detect_observations(observation_windows, det_specific_config)
                    if hasattr(detector_result, "detector_outputs"):
                        detector_outputs.update(detector_result.detector_outputs)
                    else:
                        detector_outputs[detector_id] = {
                            "status": "executed",
                            "result": str(detector_result),
                        }
                else:
                    # Fallback: use legacy path via adapter
                    from miie.processing.observation.adapter import DetectorAdapter

                    adapter = DetectorAdapter()
                    metric_df = adapter.to_metric_dataframe(observation_windows, None)

                    if hasattr(detector, "validate_input") and detector.validate_input(metric_df):
                        detector_result = detector.execute(metric_df)
                        if hasattr(detector_result, "detector_outputs"):
                            detector_outputs.update(detector_result.detector_outputs)
                        else:
                            detector_outputs[detector_id] = {
                                "status": "executed",
                                "result": str(detector_result),
                            }
                    else:
                        detector_outputs[detector_id] = {
                            "status": "skipped",
                            "reason": "input validation failed",
                        }
            except Exception as e:
                detector_outputs[detector_id] = {"status": "error", "reason": str(e)}

        return DetectorResults(detector_outputs=detector_outputs)

    def _dispatch(
        self,
        metric_dataframe: MetricDataFrame,
        windows: List[object],
        detector_config: Optional[Dict[str, Dict[str, Any]]] = None,
        enabled_detectors: Optional[List[str]] = None,
    ) -> DetectorResults:
        """Dispatch metric data to all registered detectors (legacy path).

        Args:
            metric_dataframe: Container for extracted metrics
            windows: List of window definitions used for analysis
            detector_config: Optional configuration for detectors
            enabled_detectors: Optional list of detector IDs to enable (None for all)

        Returns:
            DetectorResults: Collection of detector outputs from all registered detectors
        """
        detector_outputs = {}

        # Determine which detectors to invoke
        if enabled_detectors is not None:
            detector_items = [
                (det_id, self._registry.get(det_id))
                for det_id in self._registry.get_registered_ids()
                if det_id in enabled_detectors and self._registry.get(det_id) is not None
            ]
        else:
            detector_items = [
                (det_id, self._registry.get(det_id))
                for det_id in self._registry.get_registered_ids()
                if self._registry.get(det_id) is not None
            ]

        # Invoke each registered detector
        for detector_id, detector in detector_items:
            try:
                # Validate input metrics
                if hasattr(detector, "validate_input") and detector.validate_input(metric_dataframe):
                    # Execute detector
                    detector_result = detector.execute(metric_dataframe)
                    # Extract detector outputs
                    if hasattr(detector_result, "detector_outputs"):
                        detector_outputs.update(detector_result.detector_outputs)
                    else:
                        # Fallback if detector doesn't return standard DetectorResult
                        detector_outputs[detector_id] = {
                            "status": "executed",
                            "result": str(detector_result),
                        }
                else:
                    # Detector input validation failed
                    detector_outputs[detector_id] = {
                        "status": "skipped",
                        "reason": "input validation failed",
                    }
            except Exception as e:
                # Detector execution failed
                detector_outputs[detector_id] = {"status": "error", "reason": str(e)}

        return DetectorResults(detector_outputs=detector_outputs)
