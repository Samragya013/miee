# Missing Data Policy Audit

## 1. Verify unavailable metrics return: None (not 0, fake values, estimated values)
**Status**: PASS

**Evidence**:
- `src/miie/processing/extraction.py` lines 99-101:
  ```python
  else:
      # Unavailable metrics - return None per missing data policy
      metrics[metric_id] = None
  ```
- Exception handlers in `_extract_commit_frequency` (lines 138-140) and `_extract_code_churn` (lines 166-168) both return `None` on failure with comments stating "Per missing data policy, unavailable metrics return None, not zero or fake values"
- Unit test `tests/unit/test_metric_extraction.py::test_extract_with_unavailable_metrics` lines 125-126: `assert result.metrics["M-01"] is None`
- Unit test `tests/unit/test_metric_extraction.py::test_extract_with_unavailable_metrics` implicitly tests M-03 as unavailable (it's in the metric list with M-01 and M-06)
- Integration test `tests/integration/test_ingestion_to_extraction.py::TestIngestionToExtractionIntegration::test_ingestion_extraction_with_unavailable_metrics` lines 194-195:
  ```python
  # Unavailable metrics should be None (not zero or fake values)
  assert result.metrics["M-01"] is None
  assert result.metrics["M-03"] is None
  ```
- Integration test `tests/integration/test_ingestion_to_extraction.py::TestIngestionToExtractionIntegration::test_ingestion_extraction_with_unavailable_context` verifies that when repository context points to non-existent repository, M-02 returns None

## 2. Verify policy is documented
**Status**: PASS

**Evidence**:
- File header in `src/miie/processing/extraction.py` line 6: "Handles unavailable metrics per BSD/TFS missing data policy."
- Comments in code explicitly reference the missing data policy:
  - Line 100: "# Unavailable metrics - return None per missing data policy"
  - Line 139: "# Per missing data policy, unavailable metrics return None, not zero or fake values"
  - Line 167: "# Per missing data policy, unavailable metrics return None, not zero or fake values"
- The Operating Plan documentation in `docs/authorities/MIIE_Day_0_to_Day_10_Execution_Operating_Plan.md` line 515 references the missing data policy task: "Encode unavailable metrics - Avoid fake values"

## Overall Missing Data Policy Audit Result: **PASS**
The implementation correctly handles unavailable metrics by returning None (not zero, fake, or estimated values) and the policy is properly documented in code comments and references.