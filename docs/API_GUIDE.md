# Python API Guide

## Quick Start

```python
from miie.config.loader import load_config, ConfigLoader

# Load default configuration
loader = ConfigLoader()
config = loader.load()
```

## Configuration

The `ConfigLoader` reads YAML/JSON configuration files and merges CLI overrides.

```python
from miie.config.loader import load_config, ConfigLoader

# Load with defaults + overrides
config = load_config(
    repo="/path/to/repo",
    window_size=14,
    detectors=["D-01", "D-02"],
)

# Load from file
loader = ConfigLoader()
config = loader.load(
    config_path="/path/to/config.yaml",
    overrides={"verbose": True},
)
print(config.config_hash)
```

## Pipeline

```python
from miie.orchestration.pipeline import AnalysisPipeline
from miie.config.loader import ConfigLoader

# Create configuration
loader = ConfigLoader()
config = loader.load(overrides={"repo": "/path/to/repo"})

# Create and run pipeline
pipeline = AnalysisPipeline(config)
results = pipeline.run("/path/to/repo")
```

## Results Structure

```python
{
    "integrity_score": 0.95,
    "confidence_score": 0.85,
    "detector_outputs": {
        "D-01": {"drift_detected": False, "p_value": 0.12},
        "D-02": {"breakdown_detected": False},
        "D-03": {"compression_detected": False},
    },
    "metric_results": {
        "M-01": {"status": "ok", "values": [...]},
        "M-02": {"status": "ok", "values": [...]},
    },
    "windows": [...],
    "evidence": {...},
}
```

## Individual Components

### Detectors

```python
from miie.processing.detection import (
    DistributionDriftDetector,
    CorrelationBreakdownDetector,
    ThresholdCompressionDetector,
)

# Create detector
detector = DistributionDriftDetector(config)

# Run detection
result = detector.detect(windows)
print(result.drift_detected)
```

### Metrics

```python
from miie.metrics import MetricEngine

engine = MetricEngine(config)
metrics = engine.compute(commits, window)
```

### Scoring

```python
from miie.processing.scoring.engine import ScoringEngine

engine = ScoringEngine(config)
scores = engine.compute(detector_outputs)
print(f"IS: {scores['integrity_score']}")
print(f"CS: {scores['confidence_score']}")
```

## Error Handling

```python
from miie.cli.errors import display_error, save_partial_results

try:
    results = pipeline.run("/path/to/repo")
except Exception as e:
    save_partial_results("./output", e)
    display_error(e, verbose=True)
```
