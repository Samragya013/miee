"""
Detector Dispatcher Engine Implementation.

Implements the IDetectorEngine interface for invoking detectors on metric data.
"""

from typing import Any, Dict, List, Optional

from miie.contracts.interfaces import IDetectorEngine
from miie.processing.detection.registry import DetectorRegistry
from miie.schemas.models import DetectorResults, MetricDataFrame


class DetectorDispatcherEngine(IDetectorEngine):
    """
    Dispatches metric data to detectors and orchestrates detection execution.

    Responsibilities:
    - Routing: Direct MetricDataFrame to appropriate detectors
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
        # For Day 8 foundation, we use a simple dispatcher that invokes all registered detectors
        # In future versions, this would implement more sophisticated dispatching logic
        return self._dispatch(metric_dataframe, windows, detector_config, enabled_detectors)

    def _dispatch(
        self,
        metric_dataframe: MetricDataFrame,
        windows: List[object],
        detector_config: Optional[Dict[str, Dict[str, Any]]] = None,
        enabled_detectors: Optional[List[str]] = None,
    ) -> DetectorResults:
        """Dispatch metric data to all registered detectors.

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
