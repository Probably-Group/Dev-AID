"""Bidirectional TOON ↔ JSON converter (Pure Python implementation)."""

import json

from .decoder import decode
from .encoder import encode


def json_to_toon(json_str: str) -> str:
    """
    Convert JSON string to TOON format.

    Args:
        json_str: JSON-formatted string

    Returns:
        str: TOON-formatted string

    Raises:
        ValueError: If JSON is invalid

    Example:
        >>> json_str = '{"name": "Alice", "age": 30}'
        >>> toon_str = json_to_toon(json_str)
        >>> print(toon_str)
        name: Alice
        age: 30
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    return encode(data)


def toon_to_json(toon_str: str, pretty: bool = False) -> str:
    """
    Convert TOON format to JSON string.

    Args:
        toon_str: TOON-formatted string
        pretty: If True, format JSON with indentation

    Returns:
        str: JSON-formatted string

    Raises:
        ValueError: If TOON is invalid

    Example:
        >>> toon_str = '''
        ... name: Alice
        ... age: 30
        ... '''
        >>> json_str = toon_to_json(toon_str, pretty=True)
        >>> print(json_str)
        {
          "name": "Alice",
          "age": 30
        }
    """
    data = decode(toon_str)
    indent = 2 if pretty else None
    return json.dumps(data, indent=indent)


def estimate_token_savings(data: dict) -> dict:
    """
    Estimate token savings from using TOON vs JSON.

    Args:
        data: Python dict to analyze

    Returns:
        dict: Savings report with token counts and percentages

    Example:
        >>> data = {"items": [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]}
        >>> savings = estimate_token_savings(data)
        >>> print(f"Savings: {savings['savings_percent']}%")
    """
    json_str = json.dumps(data)
    toon_str = encode(data)

    # Approximate token count (1 token ≈ 4 characters for English text)
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
