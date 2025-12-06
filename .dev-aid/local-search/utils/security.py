"""Security utilities for Dev-AID Local Search"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def safe_resolve_path(base_dir: Path, user_path: str, must_exist: bool = False) -> Path:
    """
    Safely resolve path within base directory to prevent path traversal attacks

    Args:
        base_dir: Base directory that resolved path must be contained within
        user_path: User-provided path (relative or absolute)
        must_exist: If True, raise error if path doesn't exist

    Returns:
        Safely resolved Path object

    Raises:
        ValueError: If path traversal detected or validation fails

    Security:
        - Prevents ../ traversal attacks
        - Prevents absolute path escapes
        - Ensures resolved path is within base_dir
    """
    # Reject obvious attacks
    if '..' in user_path:
        raise ValueError(f"Path traversal detected: {user_path}")

    # Convert to Path object
    user_path_obj = Path(user_path)

    # If absolute, verify it's within base_dir
    if user_path_obj.is_absolute():
        try:
            resolved = user_path_obj.resolve()
            base_resolved = base_dir.resolve()

            # Check containment
            if not str(resolved).startswith(str(base_resolved)):
                raise ValueError(f"Path outside base directory: {user_path}")

        except (OSError, RuntimeError) as e:
            raise ValueError(f"Cannot resolve path {user_path}: {e}")
    else:
        # Relative path - resolve against base_dir
        try:
            resolved = (base_dir / user_path).resolve()
            base_resolved = base_dir.resolve()

            # Check containment using is_relative_to (Python 3.9+)
            try:
                if not resolved.is_relative_to(base_resolved):
                    raise ValueError(f"Path traversal detected: {user_path}")
            except AttributeError:
                # Fallback for Python < 3.9
                if not str(resolved).startswith(str(base_resolved)):
                    raise ValueError(f"Path traversal detected: {user_path}")

        except (OSError, RuntimeError) as e:
            raise ValueError(f"Cannot resolve path {user_path}: {e}")

    # Check existence if required
    if must_exist and not resolved.exists():
        raise ValueError(f"Path does not exist: {user_path}")

    return resolved


def validate_directory_path(directory: str, must_exist: bool = True) -> Path:
    """
    Validate that path is a valid directory

    Args:
        directory: Directory path to validate
        must_exist: If True, directory must exist

    Returns:
        Validated Path object

    Raises:
        ValueError: If validation fails
    """
    try:
        path = Path(directory).resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid directory path: {e}")

    if must_exist and not path.exists():
        raise ValueError(f"Directory does not exist: {directory}")

    if must_exist and not path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    return path
