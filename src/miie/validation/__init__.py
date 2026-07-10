"""Validation service for MIIE.

Provides centralized schema validation using JSON Schema draft-07.
All data validation should flow through this package to ensure
consistent validation rules across the codebase.

Usage:
    from miie.validation import ValidationService

    service = ValidationService()
    errors = service.validate_data("analysis_result", data)
    if errors:
        raise ValidationError(errors)
"""

from .service import ValidationService

__all__ = ["ValidationService"]
