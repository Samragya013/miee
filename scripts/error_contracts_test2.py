            output_dir: Directory to write generated datasets
            seed: Random seed for reproducibility

        Returns:
            Exit code (0=success, 2=error, 3=invalid input)
        """
        ...


# Error contracts for internal service layer
class IngestionError(Exception):
    """INT-01: Repository Ingestion Error"""
    pass


class ExtractionError(Exception):
    """INT-02: Metric Extraction Error"""
    pass


class SegmentationError(Exception):
    """INT-03: Window Segmentation Error"""
    pass


class DetectionError(Exception):
    """INT-04: Detector Engine Error"""
    pass


class ScoreError(Exception):
    """INT-05: Scoring Engine Error"""
    pass


class EvidenceError(Exception):
    """INT-06: Evidence Generation Error"""
    pass


class ExplanationError(Exception):
    """INT-07: Explanation Generation Error"""
    pass


class BenchmarkError(Exception):
    """INT-09: Benchmark Execution Error"""
    pass


class EvaluationError(Exception):
    """INT-10: Evaluation Error"""
    pass


class SerializationError(Exception):
    """INT-16: Export Error"""
    pass


class ReportError(Exception):
    """INT-08: Report Generation Error"""
    pass


class TemplateError(Exception):
    """INT-09: Template Rendering Error"""
    pass


class ValidationError(Exception):
    """General validation error"""
    pass


# Configuration object type hint
ConfigurationObject = Dict[str, Any]
