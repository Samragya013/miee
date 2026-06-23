"""
M-12: Configuration Loader — YAML/JSON config with CLI override merging.

Provides a frozen Config dataclass validated against the frozen schema from
BSD S17, and a ConfigLoader that reads YAML/JSON files, merges CLI overrides,
and computes a deterministic config_hash (SHA-256).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from miie.contracts.errors import MIIEError


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------
class ConfigError(MIIEError):
    """Configuration validation or loading error."""

    def __init__(
        self,
        message: str,
        error_code: str = "CONFIG-ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)


# ---------------------------------------------------------------------------
# Frozen configuration schema (BSD S17)
# ---------------------------------------------------------------------------
VALID_METRICS = [f"M-{i:02d}" for i in range(1, 8)] + ["all"]
VALID_WINDOW_STRATEGIES = ("time", "commit", "release", "custom")
VALID_DETECTOR_IDS = [f"D-{i:02d}" for i in range(1, 4)]
VALID_OUTPUT_FORMATS = ("json", "md", "csv", "html")

DEFAULT_DETECTOR_WEIGHTS: Dict[str, float] = {
    "D-01": 0.40,
    "D-02": 0.35,
    "D-03": 0.25,
}


@dataclass(frozen=True)
class Config:
    """Immutable MIIE analysis configuration.

    All fields are typed with defaults per BSD S17.
    The ``frozen=True`` flag makes instances hashable and immutable once
    constructed.

    Attributes:
        repo: Repository path or URL (required).
        since: Start of extraction window (ISO 8601 string or None).
        until: End of extraction window (ISO 8601 string or None).
        metrics: Metric IDs to extract.
        window_strategy: Segmentation strategy.
        window_size: Window size in the unit implied by the strategy.
        detectors: Detector IDs to enable.
        output_formats: Report output formats.
        exclude_bots: Whether to exclude bot-authored commits.
        thresholds: Per-metric detection thresholds.
        detector_weights: Weight assigned to each detector in scoring.
        seed: Random seed for reproducibility.
        output_dir: Directory to write reports.
        verbose: Enable verbose logging.
        keep_cache: Preserve the Git object cache after ingestion.
        shallow_depth: Depth for shallow clones (1 = shallowest).
        config_hash: SHA-256 of the canonical JSON of the config dict.
    """

    repo: str
    since: Optional[str] = None
    until: Optional[str] = None
    metrics: List[str] = field(default_factory=lambda: ["M-02", "M-06"])
    window_strategy: str = "time"
    window_size: int = 90
    detectors: List[str] = field(
        default_factory=lambda: ["D-01", "D-02", "D-03"]
    )
    output_formats: List[str] = field(default_factory=lambda: ["json", "md"])
    exclude_bots: bool = False
    thresholds: Dict[str, float] = field(default_factory=dict)
    detector_weights: Dict[str, float] = field(
        default_factory=lambda: dict(DEFAULT_DETECTOR_WEIGHTS)
    )
    seed: int = 42
    output_dir: str = "./output"
    verbose: bool = False
    keep_cache: bool = False
    shallow_depth: int = 1
    config_hash: str = ""


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_metrics(metrics: List[str]) -> None:
    """Raise ConfigError if any metric ID is invalid."""
    for m in metrics:
        if m not in VALID_METRICS:
            raise ConfigError(
                f"Invalid metric ID: {m!r}",
                details={"allowed": VALID_METRICS, "value": m},
            )


def _validate_window_strategy(strategy: str) -> None:
    """Raise ConfigError if strategy is not one of the allowed values."""
    if strategy not in VALID_WINDOW_STRATEGIES:
        raise ConfigError(
            f"Invalid window_strategy: {strategy!r}",
            details={"allowed": list(VALID_WINDOW_STRATEGIES), "value": strategy},
        )


def _validate_detectors(detectors: List[str]) -> None:
    """Raise ConfigError if any detector ID is invalid."""
    for d in detectors:
        if d not in VALID_DETECTOR_IDS:
            raise ConfigError(
                f"Invalid detector ID: {d!r}",
                details={"allowed": VALID_DETECTOR_IDS, "value": d},
            )


def _validate_output_formats(formats: List[str]) -> None:
    """Raise ConfigError if any output format is invalid."""
    for f in formats:
        if f not in VALID_OUTPUT_FORMATS:
            raise ConfigError(
                f"Invalid output format: {f!r}",
                details={"allowed": list(VALID_OUTPUT_FORMATS), "value": f},
            )


def _validate_detector_weights(weights: Dict[str, float]) -> None:
    """Raise ConfigError if keys or values are invalid."""
    for key in weights:
        if key not in VALID_DETECTOR_IDS:
            raise ConfigError(
                f"Invalid detector_weights key: {key!r}",
                details={"allowed": VALID_DETECTOR_IDS, "value": key},
            )
    for key, val in weights.items():
        if not isinstance(val, (int, float)):
            raise ConfigError(
                f"detector_weights[{key!r}] must be numeric",
                details={"value": val},
            )


def _validate_config_dict(data: Dict[str, Any]) -> None:
    """Run all field-level validations against a raw config dict."""
    if "repo" not in data:
        raise ConfigError("Required field 'repo' is missing")

    if not isinstance(data["repo"], str) or not data["repo"].strip():
        raise ConfigError("'repo' must be a non-empty string")

    if "metrics" in data:
        _validate_metrics(data["metrics"])
    if "window_strategy" in data:
        _validate_window_strategy(data["window_strategy"])
    if "detectors" in data:
        _validate_detectors(data["detectors"])
    if "output_formats" in data:
        _validate_output_formats(data["output_formats"])
    if "detector_weights" in data:
        _validate_detector_weights(data["detector_weights"])
    if "window_size" in data and data["window_size"] <= 0:
        raise ConfigError(
            "'window_size' must be a positive integer",
            details={"value": data["window_size"]},
        )
    if "seed" in data and not isinstance(data["seed"], int):
        raise ConfigError(
            "'seed' must be an integer",
            details={"value": data["seed"]},
        )


# ---------------------------------------------------------------------------
# Deterministic JSON serialisation + hashing
# ---------------------------------------------------------------------------

def _canonical_json(data: Dict[str, Any]) -> str:
    """Return sorted-key JSON with no extra whitespace."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def _compute_config_hash(data: Dict[str, Any]) -> str:
    """SHA-256 of the canonical JSON of *data*."""
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# YAML / JSON loading
# ---------------------------------------------------------------------------

def _safe_load_yaml(path: Path) -> Dict[str, Any]:
    """Load a YAML file using the safe loader only."""
    try:
        import yaml
    except ImportError as exc:
        raise ConfigError(
            "pyyaml is required to load YAML config files. "
            "Install it with: pip install pyyaml"
        ) from exc

    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)

    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ConfigError(
            f"Config file must contain a YAML mapping, got {type(raw).__name__}",
            details={"path": str(path)},
        )
    return raw


def _safe_load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)

    if not isinstance(raw, dict):
        raise ConfigError(
            f"Config file must contain a JSON object, got {type(raw).__name__}",
            details={"path": str(path)},
        )
    return raw


def _load_file(path: Path) -> Dict[str, Any]:
    """Dispatch to the appropriate loader based on file extension."""
    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        return _safe_load_yaml(path)
    if suffix == ".json":
        return _safe_load_json(path)
    raise ConfigError(
        f"Unsupported config file format: {suffix!r}",
        details={"path": str(path), "supported": [".yaml", ".yml", ".json"]},
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class ConfigLoader:
    """Load, validate, merge, and freeze MIIE configuration.

    Usage::

        loader = ConfigLoader()
        config = loader.load(
            config_path=Path("miie.yaml"),
            overrides={"verbose": True, "seed": 99},
        )
        print(config.config_hash)
    """

    def load(
        self,
        config_path: Optional[Path] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Config:
        """Load configuration from a file, merge overrides, validate, and freeze.

        Args:
            config_path: Path to a YAML or JSON config file.  If *None*,
                only defaults + overrides are used.
            overrides: CLI overrides to merge on top of file config.
                Values here take precedence over file values.

        Returns:
            A frozen ``Config`` dataclass with a populated ``config_hash``.

        Raises:
            ConfigError: If the config is invalid or the file cannot be read.
        """
        # 1. Load file defaults (empty dict if no file)
        file_data: Dict[str, Any] = {}
        if config_path is not None:
            if not config_path.exists():
                raise ConfigError(
                    f"Config file not found: {config_path}",
                    details={"path": str(config_path)},
                )
            file_data = _load_file(config_path)

        # 2. Merge overrides on top of file data
        merged = {**file_data}
        if overrides:
            # Filter out None values so we don't clobber file defaults with
            # absent CLI flags.
            for key, value in overrides.items():
                if value is not None:
                    merged[key] = value

        # 3. Validate
        _validate_config_dict(merged)

        # 4. Compute config_hash on the final merged dict (excluding the hash
        #    field itself so the hash is self-consistent).
        hash_payload = {k: v for k, v in merged.items() if k != "config_hash"}
        config_hash = _compute_config_hash(hash_payload)

        # 5. Build the frozen Config
        try:
            config = Config(
                repo=merged["repo"],
                since=merged.get("since"),
                until=merged.get("until"),
                metrics=merged.get("metrics", ["M-02", "M-06"]),
                window_strategy=merged.get("window_strategy", "time"),
                window_size=merged.get("window_size", 90),
                detectors=merged.get("detectors", ["D-01", "D-02", "D-03"]),
                output_formats=merged.get("output_formats", ["json", "md"]),
                exclude_bots=merged.get("exclude_bots", False),
                thresholds=merged.get("thresholds", {}),
                detector_weights=merged.get(
                    "detector_weights", dict(DEFAULT_DETECTOR_WEIGHTS)
                ),
                seed=merged.get("seed", 42),
                output_dir=merged.get("output_dir", "./output"),
                verbose=merged.get("verbose", False),
                keep_cache=merged.get("keep_cache", False),
                shallow_depth=merged.get("shallow_depth", 1),
                config_hash=config_hash,
            )
        except (TypeError, KeyError) as exc:
            raise ConfigError(
                f"Failed to construct Config: {exc}",
                details={"merged_keys": sorted(merged.keys())},
            ) from exc

        return config
