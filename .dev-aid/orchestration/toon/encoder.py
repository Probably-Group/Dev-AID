"""TOON encoder - converts Python objects to TOON format (Pure Python implementation)."""

from typing import Any


def encode(data: Any) -> str:
    """
    Encode Python object to TOON format using pure Python.

    Args:
        data: Python object (dict, list, str, int, float, bool, None)

    Returns:
        str: TOON-formatted string

    Raises:
        ValueError: If data cannot be encoded to TOON

    Example:
        >>> data = {"name": "Alice", "age": 30}
        >>> toon_str = encode(data)
        >>> print(toon_str)
        name: Alice
        age: 30
    """
    if data is None:
        return "null"
    elif isinstance(data, bool):
        return "true" if data else "false"
    elif isinstance(data, (int, float)):
        return str(data)
    elif isinstance(data, str):
        # Escape special characters if needed
        if any(c in data for c in ['"', "\n", ":"]):
            return f'"{data}"'
        return data
    elif isinstance(data, list):
        return _encode_list(data)
    elif isinstance(data, dict):
        return _encode_dict(data)
    else:
        raise ValueError(f"Cannot serialize type {type(data)} to JSON")


def _encode_dict(data: dict) -> str:
    """Encode a dictionary to TOON format."""
    lines = []
    for key, value in data.items():
        if isinstance(value, dict):
            # Nested object
            lines.append(f"{key}:")
            nested = _encode_dict(value)
            for line in nested.split("\n"):
                if line:
                    lines.append(f"  {line}")
        elif isinstance(value, list):
            # Check if it's a list of dicts (tabular data)
            if value and isinstance(value[0], dict):
                lines.append(_encode_tabular(key, value))
            else:
                # Simple list
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {encode(item)}")
        else:
            # Simple value
            lines.append(f"{key}: {encode(value)}")
    return "\n".join(lines)


def _encode_list(data: list) -> str:
    """Encode a list to TOON format."""
    if not data:
        return "[]"

    # Check if it's a list of dicts (tabular data)
    if isinstance(data[0], dict):
        return _encode_tabular("", data)

    # Simple list
    lines = []
    for item in data:
        lines.append(f"- {encode(item)}")
    return "\n".join(lines)


def _encode_tabular(key: str, data: list[dict]) -> str:
    """Encode a list of dictionaries as CSV-style tabular data."""
    if not data:
        return f"{key}:" if key else ""

    # Get all keys from first item (assume homogeneous)
    keys = list(data[0].keys())

    lines = []
    if key:
        lines.append(f"{key}:")

    # Header row
    header = ",".join(keys)
    lines.append(header)

    # Data rows
    for item in data:
        row_values = []
        for k in keys:
            value = item.get(k, "")
            # Escape commas and quotes in CSV values
            if isinstance(value, str) and ("," in value or '"' in value or "\n" in value):
                escaped_value = value.replace('"', '""')
                value = f'"{escaped_value}"'
            else:
                value = encode(value)
            row_values.append(str(value))
        lines.append(",".join(row_values))

    return "\n".join(lines)
