"""
Deterministic JSON serialization utilities for MIIE v1.0.

Implements BSD-Engineering Sections 1.4, 1.6, 1.7, and 4:
- JSON-primary serialization format
- Deterministic ordering (sorted keys)
- Stable separators
- No non-deterministic elements
"""

import json
import sys
from typing import Any, Union


def json_dumps(obj: Any, *, sort_keys: bool = True, indent: int = None, default=None) -> str:
    """
    Serialize object to JSON string with deterministic ordering.

    Args:
        obj: Object to serialize
        sort_keys: Whether to sort dictionary keys (default: True for determinism)
        indent: Number of spaces for pretty-printing (default: None for compact output)
        default: Fallback serializer for non-JSON-native types (e.g., default=str)

    Returns:
        JSON string with sorted keys and compact separators
    """
    kwargs = dict(
        obj=obj,
        sort_keys=sort_keys,
        ensure_ascii=False,
    )
    if default is not None:
        kwargs['default'] = default
    if indent is not None:
        kwargs['indent'] = indent
        return json.dumps(**kwargs)
    kwargs['separators'] = (',', ':')  # Eliminate whitespace for determinism
    return json.dumps(**kwargs)


def json_loads(s: Union[str, bytes]) -> Any:
    """
    Deserialize JSON string to object.

    Args:
        s: JSON string or bytes to deserialize

    Returns:
        Deserialized Python object
    """
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    return json.loads(s)


def deterministic_dict(
    data: dict,
    sort_keys: bool = True
) -> dict:
    """
    Create a dictionary with deterministic key ordering.

    Args:
        data: Dictionary to make deterministic
        sort_keys: Whether to sort keys (default: True)

    Returns:
        New dictionary with keys sorted (if sort_keys=True)
    """
    if not sort_keys:
        return data.copy()

    # Recursively sort keys in nested dictionaries
    result = {}
    for key in sorted(data.keys()):
        value = data[key]
        if isinstance(value, dict):
            result[key] = deterministic_dict(value, sort_keys=sort_keys)
        elif isinstance(value, list):
            result[key] = [
                deterministic_dict(item, sort_keys=sort_keys)
                if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    return result