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

