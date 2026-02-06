"""Shared security utilities for path validation across Dev-AID Router"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_safe_path(
    path: Path,
    base_dir: Path | None = None,
    require_absolute: bool = False,
) -> Path:
    """
    Validate and resolve a filesystem path safely.

    Prevents path traversal attacks by:
    - Resolving symlinks
    - Using os.path.commonpath() for containment checks (immune to prefix collisions)
    - Checking for null bytes

    Args:
        path: Path to validate
        base_dir: If provided, ensure resolved path is within this directory
        require_absolute: If True, reject relative paths before resolution

    Returns:
        Resolved safe path

    Raises:
        ValueError: If path is unsafe, contains traversal, or is outside base_dir
    """
    try:
        if require_absolute and not path.is_absolute():
            raise ValueError(f"Path must be absolute: {path}")

        resolved = path.resolve(strict=False)

        # Check for null bytes
        if "\0" in str(resolved):
            raise ValueError("Path contains null bytes")

        # Check containment if base_dir is specified
        if base_dir is not None:
            resolved_base = base_dir.resolve(strict=False)
            try:
                common = os.path.commonpath([str(resolved), str(resolved_base)])
            except ValueError:
                raise ValueError(f"Path outside base directory: {path}")
            if common != str(resolved_base):
                raise ValueError(f"Path outside base directory: {path}")

            # Log symlink resolution
            if path != resolved:
                logger.debug("Path resolved via symlink: %s -> %s", path, resolved)

        return resolved

    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid path: {e}")
