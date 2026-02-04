"""TOON encoder - converts Python objects to TOON format."""

from typing import Any

from toon_format import encode as toon_encode


def encode(data: Any) -> str:
    """
    Encode Python object to TOON format.

    Args:
        data: Python object (dict, list, str, int, float, bool, None)

    Returns:
        str: TOON-formatted string

    Raises:
        ValueError: If data cannot be serialized

    Example:
        >>> data = {"name": "Alice", "age": 30}
        >>> toon_str = encode(data)
        >>> print(toon_str)
        name: Alice
        age: 30
    """
    try:
        result: str = toon_encode(data)
        return result
    except (TypeError, ValueError) as e:
        raise ValueError(f"Cannot serialize data to TOON: {e}")
    except Exception as e:
        raise RuntimeError(f"TOON encoding failed: {e}")
