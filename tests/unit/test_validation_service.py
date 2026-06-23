"""
Test script for the validation service.
Validates schemas and sample data.
"""
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from miie.validation.service import validation_service, ValidationError

def test_schema_loading():
    """Test that all schemas are loaded and valid."""
    print("=== Testing Schema Loading ===")
    schemas = validation_service.list_schemas()
    print(f"Loaded schemas: {schemas}")
    assert len(schemas) > 0, "No schemas loaded"
    for schema_name in schemas:
        schema = validation_service.get_schema(schema_name)
        print(f"  - {schema_name}: {schema.get('title', 'No title')}")
    return schemas

def test_schema_validity():
    """Test that all schemas are valid draft-07."""
    print("\n=== Testing Schema Validity (draft-07) ===")
    errors = validation_service.validate_all_schemas()
    all_valid = True
    for schema_name, err_list in errors.items():
        if err_list:
            print(f"  {schema_name}: INVALID - {err_list}")
            all_valid = False
        else:
            print(f"  {schema_name}: VALID")
    return all_valid

def test_validation_with_sample_data():
    """Test validation with sample data for each schema."""
    print("\n=== Testing Validation with Sample Data ===")
    # We'll create minimal valid data for each schema based on the schema requirements
    test_data = {
        "repository_context": {
            "repo_id": "repo_001",
            "local_path": "/path/to/repo",
            "is_remote": False,
            "total_commits": 100,
            "first_commit_date": "2020-01-01T12:00:00Z",
            "last_commit_date": "2020-12-31T12:00:00Z",
            "contributor_count": 5,
            "is_shallow": False,
            "is_fork": False,
            "language_distribution": {"Python": 10000}
        },
        "metric_dataframe": {
            "repo_id": "repo_001",
            "run_id": "run_001",
            "timestamp": "2021-01-01T12:00:00Z",
            "metrics": {
                "M-01": {
                    "w01": [1.0, 2.0, 3.0],
                    "w02": [4.0, 5.0, 6.0]
                }
            }
        },
        "detector_result": {
            "detector_outputs": {
                "D-01": {"some_key": "some_value"},
                "D-02": {},
                "D-03": {}
            }
        },
        "evidence_package": {
            "provenance": {
                "miie_version": "1.0.0",
                "config_hash": "abc123",
                "timestamp": "2021-01-01T12:00:00Z",
                "seed": 42,
                "platform": "linux",
                "python_version": "3.10.0",
                "dependency_hash": "def456"
            },
            "windows": [
                {
                    "id": "w01",
                    "start": "2020-01-01T00:00:00Z",
                    "end": "2020-01-31T23:59:59Z",
                    "commits": 100
                }
            ],
            "metrics": {
                "M-01": {
                    "w01": [1.0, 2.0, 3.0]
                }
            },
            "detector_outputs": {
                "D-01": {"result": 0.5}
            },
            "scores": {
                "integrity": {
                    "overall": 0.8,
                    "per_metric": {
                        "M-01": 0.7
                    }
                },
                "confidence": {
                    "overall": 0.9,
                    "factors": {
                        "factor1": 0.8
                    }
                }
            },
            "warnings": []
        }
    }

    all_passed = True
    for schema_name, data in test_data.items():
        try:
            validation_service.validate(data, schema_name)
            print(f"  {schema_name}: VALID")
        except ValidationError as e:
            print(f"  {schema_name}: INVALID - {e}")
            all_passed = False
        except Exception as e:
            print(f"  {schema_name}: ERROR - {e}")
            all_passed = False
    return all_passed

def test_invalid_data():
    """Test that invalid data is correctly rejected."""
    print("\n=== Testing Invalid Data Rejection ===")
    # Test with missing required field
    invalid_data = {
        "repo_id": "repo_001"
        # missing local_path, etc.
    }
    try:
        validation_service.validate(invalid_data, "repository_context")
        print("  repository_context (invalid): INCORRECTLY VALIDATED")
        return False
    except ValidationError as e:
        print(f"  repository_context (invalid): CORRECTLY REJECTED - {e}")
        return True

def main():
    print("Validation Service Test")
    print("=" * 50)

    try:
        schemas = test_schema_loading()
        schemas_valid = test_schema_validity()
        validation_works = test_validation_with_sample_data()
        invalid_rejected = test_invalid_data()

        print("\n=== Summary ===")
        print(f"Schemas loaded: {len(schemas)}")
        print(f"All schemas valid: {schemas_valid}")
        print(f"Validation works with sample data: {validation_works}")
        print(f"Invalid data correctly rejected: {invalid_rejected}")

        if schemas_valid and validation_works and invalid_rejected:
            print("\nRESULT: All tests PASSED")
            return 0
        else:
            print("\nRESULT: Some tests FAILED")
            return 1
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())