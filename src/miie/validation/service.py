"""
Centralized validation service for MIIE using JSON Schema draft-07.
Provides a single authority path for schema validation.
"""

import json
import os
from typing import Any, Dict, Optional

import jsonschema
from jsonschema import ValidationError as JsonschemaValidationError

from miie.contracts.errors import ValidationError


class ValidationService:
    """
    Centralized validation service that loads JSON schemas and validates
    data against them using jsonschema library (draft-07).
    """

    def __init__(self, schemas_dir: Optional[str] = None):
        """
        Initialize the validation service by loading schemas from the given directory.

        Args:
            schemas_dir: Path to directory containing .schema.json files.
                        If None, defaults to src/miie/schemas/
        """
        if schemas_dir is None:
            # Default to the schemas directory relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            schemas_dir = os.path.join(base_dir, "schemas")

        self.schemas_dir = schemas_dir
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._validators: Dict[str, jsonschema.Draft7Validator] = {}

        self._load_schemas()

    def _load_schemas(self) -> None:
        """Load all .schema.json files from the schemas directory."""
        if not os.path.exists(self.schemas_dir):
            raise FileNotFoundError(f"Schemas directory not found: {self.schemas_dir}")

        for filename in os.listdir(self.schemas_dir):
            if filename.endswith(".schema.json"):
                schema_name = filename[: -len(".schema.json")]
                schema_path = os.path.join(self.schemas_dir, filename)

                try:
                    with open(schema_path, "r", encoding="utf-8") as f:
                        schema = json.load(f)

                    # Validate that the schema itself is a valid draft-07 schema
                    jsonschema.Draft7Validator.check_schema(schema)

                    # Compile the schema for validation
                    validator = jsonschema.Draft7Validator(schema)

                    self._schemas[schema_name] = schema
                    self._validators[schema_name] = validator
                except json.JSONDecodeError as e:
                    raise ValidationError(f"Invalid JSON in schema file {filename}: {e}")
                except jsonschema.SchemaError as e:
                    raise ValidationError(f"Invalid JSON Schema in {filename}: {e}")
                except Exception as e:
                    raise ValidationError(f"Failed to load schema {filename}: {e}")

    def validate(self, data: Any, schema_name: str) -> None:
        """
        Validate data against a named schema.

        Args:
            data: The data to validate (should be JSON-serializable)
            schema_name: Name of the schema (without .schema.json extension)

        Raises:
            ValidationError: If validation fails
            KeyError: If schema_name is not found
        """
        if schema_name not in self._validators:
            raise KeyError(f"Schema '{schema_name}' not found. Available schemas: {list(self._schemas.keys())}")

        validator = self._validators[schema_name]
        try:
            validator.validate(data)
        except JsonschemaValidationError as e:
            # Convert jsonschema ValidationError to our ValidationError
            raise ValidationError(f"Schema validation failed for '{schema_name}': {e.message}")

    def get_schema(self, schema_name: str) -> Dict[str, Any]:
        """
        Get the raw schema dictionary by name.

        Args:
            schema_name: Name of the schema

        Returns:
            The schema dictionary

        Raises:
            KeyError: If schema_name is not found
        """
        if schema_name not in self._schemas:
            raise KeyError(f"Schema '{schema_name}' not found")
        return self._schemas[schema_name].copy()

    def list_schemas(self) -> list[str]:
        """List all available schema names."""
        return list(self._schemas.keys())

    def validate_all_schemas(self) -> Dict[str, list[str]]:
        """
        Validate all loaded schemas against the draft-07 meta-schema.
        This is a sanity check to ensure all schemas are valid.

        Returns:
            Dictionary with schema names as keys and list of errors (empty if valid)
        """
        errors = {}
        for name, schema in self._schemas.items():
            try:
                jsonschema.Draft7Validator.check_schema(schema)
                errors[name] = []
            except jsonschema.SchemaError as e:
                errors[name] = [str(e)]
        return errors


# Global instance for convenience
validation_service = ValidationService()


def validate_data(data: Any, schema_name: str) -> None:
    """
    Convenience function to validate data using the global validation service.

    Args:
        data: The data to validate
        schema_name: Name of the schema to validate against

    Raises:
        ValidationError: If validation fails
    """
    validation_service.validate(data, schema_name)
