"""TOON decoder - converts TOON format to Python objects."""

import json
import subprocess
from pathlib import Path
from typing import Any


def decode(toon_str: str) -> Any:
    """
    Decode TOON format to Python object using Node.js SDK.

    Args:
        toon_str: TOON-formatted string

    Returns:
        Any: Python object (dict, list, str, int, float, bool, None)

    Raises:
        ValueError: If TOON string is invalid
        RuntimeError: If TOON decoding fails

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

    # Escape for shell (backticks for template literals)
    escaped = toon_str.replace("`", "\\`").replace("$", "\\$")

    # Path to the orchestration directory (where node_modules is)
    orchestration_dir = Path(__file__).parent.parent

    try:
        # Call Node.js to decode using TOON SDK
        result = subprocess.run(
            [
                "node",
                "-e",
                f"""
                const toon = require('@toon-format/toon');
                const toonStr = `{escaped}`;
                const data = toon.decode(toonStr);
                console.log(JSON.stringify(data));
                """,
            ],
            cwd=str(orchestration_dir),
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )

        # Parse the JSON output back to Python
        return json.loads(result.stdout.strip())

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"TOON decoding failed: {e.stderr if e.stderr else 'unknown error'}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("TOON decoding timed out after 10 seconds")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse TOON decoder output as JSON: {e}")
