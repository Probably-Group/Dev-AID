"""Bidirectional TOON ↔ JSON converter."""

import json
from typing import Any

from .decoder import decode
from .encoder import encode


def json_to_toon(json_str: str) -> str:
    """
    Convert JSON string to TOON format.

    Args:
        json_str: Valid JSON string

    Returns:
        str: TOON-formatted string

    Raises:
        ValueError: If JSON string is invalid
        RuntimeError: If conversion fails

    Example:
        >>> json_str = '{"name": "Bob", "age": 25}'
        >>> toon_str = json_to_toon(json_str)
        >>> print(toon_str)
        name: Bob
        age: 25
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON input: {e}")

    return encode(data)


def toon_to_json(toon_str: str, pretty: bool = False) -> str:
    """
    Convert TOON format to JSON string.

    Args:
        toon_str: TOON-formatted string
        pretty: If True, format JSON with indentation

    Returns:
        str: JSON string

    Raises:
        ValueError: If TOON string is invalid
        RuntimeError: If conversion fails

    Example:
        >>> toon_str = '''
        ... name: Carol
        ... age: 35
        ... '''
        >>> json_str = toon_to_json(toon_str, pretty=True)
        >>> print(json_str)
        {
          "name": "Carol",
          "age": 35
        }
    """
    data = decode(toon_str)

    indent = 2 if pretty else None
    return json.dumps(data, indent=indent)


def estimate_token_savings(data: Any) -> dict:
    """
    Estimate token savings when using TOON vs JSON.

    Args:
        data: Python object to analyze

    Returns:
        dict: {
            'json_tokens': estimated tokens for JSON,
            'toon_tokens': estimated tokens for TOON,
            'savings_tokens': tokens saved,
            'savings_percent': percentage saved
        }

    Example:
        >>> data = {"items": [{"id": i, "value": i*10} for i in range(20)]}
        >>> savings = estimate_token_savings(data)
        >>> print(f"Saves {savings['savings_percent']:.1f}% tokens")
    """
    # Generate both formats
    json_str = json.dumps(data)
    toon_str = encode(data)

    # Approximate token count (1 token ≈ 4 characters is a rough estimate)
    json_tokens = len(json_str) / 4
    toon_tokens = len(toon_str) / 4

    savings_tokens = json_tokens - toon_tokens
    savings_percent = (savings_tokens / json_tokens * 100) if json_tokens > 0 else 0

    return {
        "json_tokens": int(json_tokens),
        "toon_tokens": int(toon_tokens),
        "savings_tokens": int(savings_tokens),
        "savings_percent": round(savings_percent, 1),
        "json_size": len(json_str),
        "toon_size": len(toon_str),
    }
