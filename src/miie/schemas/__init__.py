"""Data schemas and models for MIIE.

This package defines the core data structures used throughout MIIE:
- RepositoryContext: Repository metadata
- MetricDataFrame: Time-series metric data
- WindowDefinition: Analysis window boundaries
- DetectorResults: Output from all detectors
- ScorePackage: Integrity and confidence scores
- EvidencePackage: Traceable evidence package
- ExplanationReport: Human-readable explanations
- ReportOutput: Generated report paths

All dataclasses follow the ACS v1.0 specification and include
validation logic in their __post_init__ methods.
"""
