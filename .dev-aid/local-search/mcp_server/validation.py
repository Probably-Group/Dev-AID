"""Pydantic validation models for MCP server requests"""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SearchCodeRequest(BaseModel):
    """Validated search code request"""

    query: str = Field(min_length=1, max_length=10000, description="Search query")
    project_path: str = Field(description="Absolute path to project directory")
    top_k: int = Field(
        default=10, ge=1, le=100, description="Number of results to return"
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate query is not empty after stripping"""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

    @field_validator("project_path")
    @classmethod
    def validate_project_path(cls, v: str) -> str:
        """Validate project path is absolute and exists"""
        path = Path(v)

        if not path.is_absolute():
            raise ValueError(f"Project path must be absolute: {v}")

        # Note: Path might not exist yet (e.g., for indexing)
        # Existence check is done in the actual operation

        return str(path.resolve())


class IndexDirectoryRequest(BaseModel):
    """Validated index directory request"""

    directory: str = Field(description="Directory path to index")

    @field_validator("directory")
    @classmethod
    def validate_directory(cls, v: str) -> str:
        """Validate directory path"""
        path = Path(v)

        try:
            resolved = path.resolve()
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid directory path: {e}")

        if not resolved.exists():
            raise ValueError(f"Directory does not exist: {v}")

        if not resolved.is_dir():
            raise ValueError(f"Path is not a directory: {v}")

        return str(resolved)


class GetIndexStatusRequest(BaseModel):
    """Validated get index status request"""

    project_path: Optional[str] = Field(
        default=None, description="Optional project path"
    )

    @field_validator("project_path")
    @classmethod
    def validate_project_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate project path if provided"""
        if v is None:
            return None

        path = Path(v)

        if not path.is_absolute():
            raise ValueError(f"Project path must be absolute: {v}")

        return str(path.resolve())


class ClearIndexRequest(BaseModel):
    """Validated clear index request"""

    project_path: str = Field(description="Project path")

    @field_validator("project_path")
    @classmethod
    def validate_project_path(cls, v: str) -> str:
        """Validate project path"""
        path = Path(v)

        if not path.is_absolute():
            raise ValueError(f"Project path must be absolute: {v}")

        return str(path.resolve())
