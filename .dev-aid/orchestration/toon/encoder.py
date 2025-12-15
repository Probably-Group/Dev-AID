"""TOON encoder - converts Python objects to TOON format."""

import json
import subprocess
from pathlib import Path
from typing import Any


def encode(data: Any) -> str:
    """
    Encode Python object to TOON format using Node.js SDK.

    Args:
        data: Python object (dict, list, str, int, float, bool, None)

    Returns:
        str: TOON-formatted string

    Raises:
        ValueError: If data cannot be serialized to JSON
        RuntimeError: If TOON encoding fails

    Example:
        >>> data = {"name": "Alice", "age": 30}
        >>> toon_str = encode(data)
        >>> print(toon_str)
        name: Alice
        age: 30
    """
    try:
        # Convert Python object to JSON string
        json_str = json.dumps(data)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Cannot serialize data to JSON: {e}")

    # Escape single quotes for shell safety
    escaped_json = json_str.replace("'", "'\\''")

    # Path to the orchestration directory (where node_modules is)
    orchestration_dir = Path(__file__).parent.parent

    try:
        # Call Node.js to encode using TOON SDK
        result = subprocess.run(
            [
                "node",
                "-e",
                f"""
                const toon = require('@toon-format/toon');
                const data = JSON.parse('{escaped_json}');
                console.log(toon.encode(data));
                """,
            ],
            cwd=str(orchestration_dir),
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )

        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"TOON encoding failed: {e.stderr if e.stderr else 'unknown error'}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("TOON encoding timed out after 10 seconds")
