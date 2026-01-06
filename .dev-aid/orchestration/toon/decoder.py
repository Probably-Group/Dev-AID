"""TOON decoder - converts TOON format to Python objects."""

from typing import Any

from toon_format import decode as toon_decode


def decode(toon_str: str) -> Any:
    """
    Decode TOON format to Python object.

    Args:
        toon_str: TOON-formatted string

    Returns:
        Any: Python object (dict, list, str, int, float, bool, None)

    Raises:
        ValueError: If TOON string is invalid

    Example:
        >>> toon_str = '''
        ... name: Alice
        ... age: 30
        ... '''
        >>> data = decode(toon_str)
        >>> print(data)
        {'name': 'Alice', 'age': 30}
    """
    if not isinstance(toon_str, str):
        raise ValueError("TOON input must be a string")

    if not toon_str.strip():
        raise ValueError("TOON input cannot be empty")

    try:
        return toon_decode(toon_str)
    except Exception as e:
        raise ValueError(f"TOON decoding failed: {e}")
