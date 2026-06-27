"""
Tests for deterministic serialization utilities.
"""

from miie.schemas.serialization import deterministic_dict, json_dumps, json_loads


def test_json_dumps_deterministic_ordering():
    """Test that json_dumps produces deterministic key ordering."""
    # Dictionary with intentionally non-sorted keys
    data = {"zebra": 1, "apple": 2, "banana": 3}

    json_str = json_dumps(data)
    # Should be sorted: apple, banana, zebra
    expected = '{"apple":2,"banana":3,"zebra":1}'
    assert json_str == expected


def test_json_dumps_compact_separators():
    """Test that json_dumps uses compact separators."""
    data = {"a": 1, "b": 2}
    json_str = json_dumps(data)
    # Should not contain spaces
    assert " " not in json_str
    assert "\t" not in json_str
    assert "\n" not in json_str


def test_json_loads_roundtrip():
    """Test that json_loads correctly parses JSON."""
    original = {"name": "test", "value": 42}
    json_str = '{"name":"test","value":42}'
    parsed = json_loads(json_str)
    assert parsed == original


def test_deterministic_dict():
    """Test deterministic_dict function."""
    data = {"zebra": 1, "apple": {"dog": 2, "cat": 3}, "banana": [{"x": 1}, {"y": 2}]}

    result = deterministic_dict(data)

    # Check top-level keys are sorted
    assert list(result.keys()) == ["apple", "banana", "zebra"]

    # Check nested dict keys are sorted
    assert list(result["apple"].keys()) == ["cat", "dog"]

    # Check list of dicts has sorted keys
    assert result["banana"][0]["x"] == 1
    assert result["banana"][1]["y"] == 2


def test_deterministic_dict_no_sort():
    """Test deterministic_dict with sort_keys=False."""
    data = {"zebra": 1, "apple": 2}
    result = deterministic_dict(data, sort_keys=False)
    # Should preserve original order
    assert list(result.keys()) == ["zebra", "apple"]


def test_json_dumps_preserves_data():
    """Test that json_dumps preserves all data correctly."""
    original = {
        "string": "test",
        "number": 42,
        "float": 3.14,
        "boolean": True,
        "null": None,
        "list": [1, 2, 3],
        "nested": {"inner": "value"},
    }

    json_str = json_dumps(original)
    parsed = json_loads(json_str)
    assert parsed == original
