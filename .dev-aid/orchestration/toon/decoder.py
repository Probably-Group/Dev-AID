"""TOON decoder - converts TOON format to Python objects (Pure Python implementation)."""

import csv
from typing import Any


def decode(toon_str: str) -> Any:
    """
    Decode TOON format to Python object using pure Python.

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

    toon_str = toon_str.strip()
    if not toon_str:
        raise ValueError("TOON input cannot be empty")

    lines = toon_str.split("\n")

    # Check if the first line is a CSV header (top-level list of dicts)
    first_line = lines[0].strip()
    if first_line and "," in first_line and ":" not in first_line:
        # This is a top-level CSV table
        result, _ = _parse_table(lines, 0, 0)
        return result

    result, _ = _parse_lines(lines, 0, 0)
    return result


def _parse_lines(lines: list[str], start_idx: int, indent_level: int) -> tuple[Any, int]:
    """
    Parse lines starting from start_idx with given indentation level.

    Returns:
        (parsed_value, next_line_index)
    """
    result = {}
    i = start_idx

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Calculate indentation
        current_indent = len(line) - len(line.lstrip())

        # If indentation decreased, return to parent level
        if current_indent < indent_level:
            break

        # Skip if indentation is too deep (will be handled by nested call)
        if current_indent > indent_level:
            break

        line = line.strip()

        # Check if this is a list item
        if line.startswith("- "):
            # Parse list starting from this line
            list_items, next_i = _parse_list(lines, i, indent_level)
            return list_items, next_i

        # Check if this is a key-value pair or table
        if ":" in line:
            key_end = line.index(":")
            key = line[:key_end].strip()
            value_part = line[key_end + 1 :].strip()

            if value_part:
                # Simple key-value pair
                result[key] = _parse_value(value_part)
                i += 1
            else:
                # Check next line to determine if it's a nested object, list, or table
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    next_indent = len(next_line) - len(next_line.lstrip())

                    if next_indent > current_indent:
                        # Check if it's a CSV table (starts with comma-separated headers)
                        next_line_stripped = next_line.strip()
                        if "," in next_line_stripped and not next_line_stripped.startswith("-"):
                            # Parse as table
                            table_data, next_i = _parse_table(lines, i + 1, next_indent)
                            result[key] = table_data
                            i = next_i
                        elif next_line_stripped.startswith("-"):
                            # Parse as list
                            list_data, next_i = _parse_list(lines, i + 1, next_indent)
                            result[key] = list_data
                            i = next_i
                        else:
                            # Parse as nested object
                            nested_data, next_i = _parse_lines(lines, i + 1, next_indent)
                            result[key] = nested_data
                            i = next_i
                    else:
                        # Empty value
                        result[key] = None
                        i += 1
                else:
                    # Empty value at end of file
                    result[key] = None
                    i += 1
        else:
            # Line doesn't contain a key-value separator, might be part of tabular data
            i += 1

    return result, i


def _parse_list(lines: list[str], start_idx: int, indent_level: int) -> tuple[list, int]:
    """Parse a list starting from start_idx."""
    result = []
    i = start_idx

    while i < len(lines):
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        current_indent = len(line) - len(line.lstrip())

        if current_indent < indent_level:
            break

        if current_indent > indent_level:
            # Nested content
            break

        line = line.strip()

        if line.startswith("- "):
            value_str = line[2:].strip()
            result.append(_parse_value(value_str))
            i += 1
        else:
            # Not a list item, stop parsing
            break

    return result, i


def _parse_table(lines: list[str], start_idx: int, indent_level: int) -> tuple[list[dict], int]:
    """Parse a CSV-style table starting from start_idx."""
    i = start_idx

    # First line is the header
    if i >= len(lines):
        return [], i

    header_line = lines[i].strip()
    # Use CSV reader to properly handle quoted fields
    headers = list(csv.reader([header_line]))[0]
    i += 1

    result = []

    while i < len(lines):
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        current_indent = len(line) - len(line.lstrip())

        if current_indent < indent_level:
            break

        data_line = line.strip()

        # Check if this looks like a data row (has commas, not a key:value pair)
        if "," in data_line and ":" not in data_line:
            # Use CSV reader to properly handle quoted fields
            values = list(csv.reader([data_line]))[0]

            # Create dict from headers and values
            row_dict = {}
            for idx, header in enumerate(headers):
                if idx < len(values):
                    row_dict[header] = _parse_value(values[idx])
                else:
                    row_dict[header] = None

            result.append(row_dict)
            i += 1
        else:
            # Not a table row, stop parsing
            break

    return result, i


def _parse_value(value_str: str) -> Any:
    """Parse a string value into appropriate Python type."""
    value_str = value_str.strip()

    if not value_str:
        return None

    # Remove quotes if present
    if value_str.startswith('"') and value_str.endswith('"'):
        return value_str[1:-1].replace('""', '"')

    # Boolean
    if value_str.lower() == "true":
        return True
    if value_str.lower() == "false":
        return False

    # Null
    if value_str.lower() in ("null", "none"):
        return None

    # Try to parse as number
    try:
        if "." in value_str:
            return float(value_str)
        else:
            return int(value_str)
    except ValueError:
        pass

    # Return as string
    return value_str
