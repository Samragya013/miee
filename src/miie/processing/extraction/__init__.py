"""MIIE Observation Extraction — ExtractionEngine, MetricExtractor, MetricExtractionEngine (deprecated)."""

import warnings

from miie.processing.extraction.engine import ExtractionEngine
from miie.processing.extraction.metric_extractor import MetricExtractor

__all__ = [
    "ExtractionEngine",
    "MetricExtractor",
    "MetricExtractionEngine",
]


def __getattr__(name: str):
    """Lazy import for deprecated MetricExtractionEngine and CommitExtractor."""
    if name == "MetricExtractionEngine":
        warnings.warn(
            "MetricExtractionEngine is deprecated. Use ExtractionEngine instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        # Import from the legacy module file (extraction.py is shadowed by the
        # package directory, so we use importlib to access it directly).
        import importlib
        import importlib.util
        import pathlib

        legacy_path = pathlib.Path(__file__).resolve().parent.parent / "extraction.py"
        if legacy_path.exists():
            spec = importlib.util.spec_from_file_location("miie.processing.extraction._legacy", str(legacy_path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.MetricExtractionEngine
        raise ImportError("Legacy extraction.py not found")

    if name == "CommitExtractor":
        warnings.warn(
            "CommitExtractor is deprecated. Use ExtractionEngine with GitObservationProvider instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from miie.processing.extraction.commit_extractor import CommitExtractor

        return CommitExtractor

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
