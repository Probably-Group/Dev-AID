"""
Input Validation Models for Dev-AID Router

Provides Pydantic models for validating all external inputs:
- CLI arguments
- API requests
- Configuration files
- User prompts
"""

import re
from pathlib import Path
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class SecureInput(BaseModel):
    """Base model with security defaults"""

    model_config = {"extra": "forbid", "str_strip_whitespace": True}

    @field_validator("*", mode="before")
    @classmethod
    def reject_null_bytes(cls, v: Any) -> Any:
        """Reject null bytes in all string fields"""
        if isinstance(v, str) and "\x00" in v:
            raise ValueError("Null bytes not allowed")
        return v


class ExecuteRequest(SecureInput):
    """Validated execute request from CLI or API"""

    request: str = Field(
        min_length=1,
        max_length=50000,
        description="User request to execute",
    )
    mode: Optional[Literal["solo", "ensemble", "challenger"]] = Field(
        None, description="Orchestration mode override"
    )
    context_size: int = Field(
        default=0, ge=0, le=10_000_000, description="Estimated context size in tokens"
    )
    use_mcp: bool = Field(default=True, description="Whether to use MCP context gathering")

    @field_validator("request")
    @classmethod
    def validate_request_content(cls, v: str) -> str:
        """Validate request doesn't contain suspicious patterns"""
        # Check for common injection patterns
        suspicious_patterns = [
            r"__import__",
            r"eval\(",
            r"exec\(",
            r"compile\(",
            r"\.\.\/",  # Path traversal
            r"\$\{",  # Template injection
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Request contains potentially unsafe pattern: {pattern}")

        return v


class ModelConfig(SecureInput):
    """Validated model configuration"""

    provider: Literal["anthropic", "google", "openai"] = Field(description="AI provider name")
    model_id: str = Field(min_length=1, max_length=200, description="Model identifier")
    max_tokens: int = Field(default=4096, ge=1, le=1_000_000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    cost_per_1m_tokens: Dict[str, float] = Field(
        default_factory=dict, description="Cost per million tokens (input/output)"
    )

    @field_validator("model_id")
    @classmethod
    def validate_model_id(cls, v: str) -> str:
        """Ensure model ID is alphanumeric with allowed chars"""
        if not re.match(r"^[a-zA-Z0-9_\-\.]+$", v):
            raise ValueError(
                "Model ID must contain only alphanumeric characters, hyphens, underscores, and dots"
            )
        return v


class APIKeyConfig(SecureInput):
    """Validated API key configuration"""

    provider: Literal["anthropic", "google", "openai"]
    api_key: str = Field(min_length=10, max_length=500)

    @field_validator("api_key")
    @classmethod
    def validate_api_key_format(cls, v: str) -> str:
        """Basic API key format validation"""
        # Check it's not empty/whitespace
        if not v.strip():
            raise ValueError("API key cannot be empty")

        # Check for suspicious patterns
        if any(char in v for char in ["\n", "\r", "\0"]):
            raise ValueError("API key contains invalid characters")

        return v


class SafePath(SecureInput):
    """Validated file path with traversal protection"""

    path: str = Field(min_length=1, max_length=4096)
    base_dir: Optional[str] = Field(None, min_length=1, max_length=4096)

    @field_validator("path")
    @classmethod
    def validate_no_traversal(cls, v: str) -> str:
        """Check for path traversal attempts"""
        # Reject obvious traversal patterns
        if ".." in v:
            raise ValueError("Path traversal detected: '..' not allowed")

        if v.startswith("/") and cls.base_dir:
            raise ValueError("Absolute paths not allowed when base_dir is set")

        # Reject null bytes and other suspicious chars
        if any(char in v for char in ["\0", "\n", "\r"]):
            raise ValueError("Path contains invalid characters")

        return v

    @model_validator(mode="after")
    def validate_path_containment(self) -> "SafePath":
        """Ensure resolved path is within base_dir"""
        if self.base_dir:
            base = Path(self.base_dir).resolve()
            target = (base / self.path).resolve()

            if not str(target).startswith(str(base)):
                raise ValueError(f"Path traversal detected: {target} is not within {base}")

        return self


class SubprocessCommand(SecureInput):
    """Validated subprocess command with allowlist"""

    program: Literal["git", "python", "python3", "pip", "pip3"] = Field(
        description="Allowed program name"
    )
    args: list[str] = Field(default_factory=list, max_length=50)
    cwd: Optional[str] = Field(None, max_length=4096)

    @field_validator("args")
    @classmethod
    def validate_args(cls, v: list[str]) -> list[str]:
        """Validate command arguments don't contain injection attempts"""
        for arg in v:
            # Reject arguments with shell metacharacters
            if any(char in arg for char in [";", "|", "&", "$", "`", "\n", "\r"]):
                raise ValueError(f"Argument contains shell metacharacters: {arg}")

            # Reject null bytes
            if "\0" in arg:
                raise ValueError("Argument contains null bytes")

        return v

    @field_validator("cwd")
    @classmethod
    def validate_cwd(cls, v: Optional[str]) -> Optional[str]:
        """Validate working directory path"""
        if v is None:
            return v

        # Use SafePath validation
        try:
            SafePath(path=v, base_dir=None)
        except ValueError as e:
            raise ValueError(f"Invalid cwd: {e}")

        return v


class MCPServerConfig(SecureInput):
    """Validated MCP server configuration"""

    name: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_\-]+$")
    command: str = Field(min_length=1, max_length=500)
    args: list[str] = Field(default_factory=list, max_length=50)
    env: Optional[Dict[str, str]] = Field(None, max_length=100)

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: str) -> str:
        """Validate command is safe"""
        # Only allow specific commands or executables
        allowed_prefixes = ["node", "python", "python3", "npx", "/usr/", "/opt/"]

        if not any(v.startswith(prefix) for prefix in allowed_prefixes):
            raise ValueError(f"Command must start with one of: {', '.join(allowed_prefixes)}")

        return v


class CostLimit(SecureInput):
    """Validated cost limit configuration"""

    daily_limit: float = Field(ge=0.0, le=10000.0, description="Daily cost limit in USD")
    warning_threshold: float = Field(
        ge=0.0, le=1.0, default=0.8, description="Warning threshold (0.0-1.0)"
    )

    @model_validator(mode="after")
    def validate_threshold(self) -> "CostLimit":
        """Ensure warning threshold is reasonable"""
        if self.warning_threshold >= 1.0:
            raise ValueError("Warning threshold must be less than 1.0")

        return self
