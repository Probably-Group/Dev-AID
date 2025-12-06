"""Storage utilities for Dev-AID Local Search"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional


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
        """
        # Use MD5 hash of path for directory name
        path_hash = hashlib.md5(project_path.encode()).hexdigest()[:16]
        project_dir = self.index_dir / path_hash
        project_dir.mkdir(parents=True, exist_ok=True)

        # Store mapping
        mapping_file = project_dir / "project.json"
        if not mapping_file.exists():
            with open(mapping_file, 'w') as f:
                json.dump({
                    "path": project_path,
                    "hash": path_hash,
                    "created": str(Path(project_path).stat().st_ctime)
                }, f, indent=2)

        return project_dir

    def load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self, config: Dict[str, Any]):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

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
                    with open(mapping_file, 'r') as f:
                        info = json.load(f)
                        projects[info["path"]] = info["hash"]
        return projects
