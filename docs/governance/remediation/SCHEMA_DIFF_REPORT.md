# Schema Diff Report: BSD-Engineering Compliance Updates

This report shows the changes made to `src/miie/schemas/models.py` to align the four core schemas (RepositoryContext, MetricDataFrame, DetectorResult, EvidencePackage) with the BSD-Engineering_MIIE_v1.0.md authority document.

## Summary of Changes

### RepositoryContext
- Removed default values for `total_commits`, `first_commit_date`, `last_commit_date`, `contributor_count` (now required)
- Changed `first_commit_date` and `last_commit_date` from `Optional[datetime.datetime]` to `str` (ISO 8601 UTC timestamps)
- Added validation for timestamp format (YYYY-MM-DDTHH:MM:SSZ) and chronological order

### MetricDataFrame
- Changed `timestamp` from `datetime.datetime` to `str` (ISO 8601 UTC timestamps)
- Added validation for timestamp format

### DetectorResult
- No changes required; already compliant with BSD-Engineering Section 8 (only `detector_outputs` field with keys D-01, D-02, D-03)

### EvidencePackage
- Stripped down to match BSD-Engineering Section 10.1 exactly:
  - Removed extra fields: `evidence_id`, `timestamp`, `score_package_id`, `detector_results_ids`, `metrics_used`, `windows_analyzed`, `integrity_verification`, `confidence_indicators`, `reproducibility_info`, `das_notation`
  - Kept only: `provenance`, `windows`, `metrics`, `detector_outputs`, `scores`, `warnings`
  - Updated `windows` structure to match BSD: list of objects with `id` (str), `start` (str, date-time), `end` (str, date-time), `commits` (int)
  - Added comprehensive validation for all fields per BSD JSON Schema draft-07

### Additional Updates
- Added `import re` for timestamp validation
- Updated import from `miie.schemas.serialization` to `src.miie.schemas.serialization` (corrected module path)
- Added `Any` to typing imports for flexibility in provenance and scores fields
- Updated deferred schema classes (WindowDefinition, DetectorResults, ScorePackage, ExplanationReport, BenchmarkRun, EvaluationResult, ReportOutput, GroundTruthInput, Annotation) from placeholder implementations to full validation implementations (these were already updated in the working copy prior to this task; changes shown for completeness)

## Full Diff

```diff