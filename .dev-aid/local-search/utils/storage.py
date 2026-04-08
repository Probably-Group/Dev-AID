"""Storage utilities for Dev-AID Local Search"""

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class StorageManager:
    """Manages storage locations for models, indexes, and configuration"""

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize storage manager

        Args:
            base_dir: Base directory for storage (default: ~/.devaid-search)
        """
        if base_dir is None:
            base_dir = os.path.expanduser("~/.devaid-search")

        self.base_dir = Path(base_dir)
        self.models_dir = self.base_dir / "models"
        self.index_dir = self.base_dir / "index"
        self.config_file = self.base_dir / "config.json"

        # Create directories
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def get_project_dir(self, project_path: str) -> Path:
        """
        Get storage directory for a specific project

        Args:
            project_path: Absolute path to project

        Returns:
            Path to project storage directory

        Raises:
            ValueError: If project_path is not absolute or doesn't exist
        """
        # SECURITY: Validate that project_path is absolute
        project_path_obj = Path(project_path)
        if not project_path_obj.is_absolute():
            raise ValueError(f"project_path must be absolute, got: {project_path}")

        # SECURITY: Use SHA-256 instead of weak MD5
        path_hash = hashlib.sha256(project_path.encode()).hexdigest()[:16]
        project_dir = self.index_dir / path_hash
        project_dir.mkdir(parents=True, exist_ok=True)

        # Store mapping
        mapping_file = project_dir / "project.json"
        if not mapping_file.exists():
            try:
                # Safely get creation time
                created_time = (
                    str(project_path_obj.stat().st_ctime)
                    if project_path_obj.exists()
                    else "unknown"
                )
            except OSError as e:
                logger.warning(f"Cannot stat {project_path}: {e}")
                created_time = "unknown"

            with open(mapping_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"path": project_path, "hash": path_hash, "created": created_time},
                    f,
                    indent=2,
                )

        return project_dir

    def load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Failed to load config: {e}")
                return {}
        return {}

    def save_config(self, config: Dict[str, Any]):
        """Save configuration"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except (OSError, TypeError) as e:
            logger.error(f"Failed to save config: {e}")
            raise

    def list_projects(self) -> Dict[str, str]:
        """
        List all indexed projects

        Returns:
            Dict mapping project path to hash
        """
        projects = {}
        for project_dir in self.index_dir.iterdir():
            if project_dir.is_dir():
                mapping_file = project_dir / "project.json"
                if mapping_file.exists():
                    try:
                        with open(mapping_file, "r", encoding="utf-8") as f:
                            info = json.load(f)
                            projects[info["path"]] = info["hash"]
                    except (json.JSONDecodeError, OSError, KeyError) as e:
                        logger.warning(
                            f"Cannot read project info from {mapping_file}: {e}"
                        )
                        continue
        return projects
