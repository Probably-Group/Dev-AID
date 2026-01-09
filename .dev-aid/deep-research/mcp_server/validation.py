"""Pydantic validation models for Deep Research MCP server.

These models validate incoming MCP tool requests to ensure
proper input before processing.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ResearchRequest(BaseModel):
    """Validated research request."""

    query: str = Field(
        min_length=3,
        max_length=5000,
        description="Research query (3-5000 characters)",
    )
    depth: str = Field(
        default="auto",
        description="Research depth: quick, standard, deep, or auto",
    )
    provider: Optional[str] = Field(
        default=None,
        description="Specific provider to use (tavily, perplexity-sonar, gemini-deep-research)",
    )
    max_sources: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum sources to return (1-50)",
    )
    use_cache: bool = Field(
        default=True,
        description="Use cached results if available",
    )
    cache_ttl_hours: int = Field(
        default=24,
        ge=1,
        le=48,
        description="Cache TTL in hours (1-48)",
    )
    prefer_speed: bool = Field(
        default=False,
        description="Prefer faster providers even for complex queries",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and normalize query."""
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty or whitespace only")
        return v

    @field_validator("depth")
    @classmethod
    def validate_depth(cls, v: str) -> str:
        """Validate depth value."""
        valid = ["quick", "standard", "deep", "auto"]
        v_lower = v.lower()
        if v_lower not in valid:
            raise ValueError(f"Depth must be one of: {', '.join(valid)}")
        return v_lower

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: Optional[str]) -> Optional[str]:
        """Validate provider name."""
        if v is None:
            return None

        valid = ["tavily", "perplexity-sonar", "gemini-deep-research"]
        v_lower = v.lower()
        if v_lower not in valid:
            raise ValueError(f"Provider must be one of: {', '.join(valid)}")
        return v_lower


class CacheStatusRequest(BaseModel):
    """Request for cache status."""

    include_entries: bool = Field(
        default=False,
        description="Include individual entry details",
    )


class ClearCacheRequest(BaseModel):
    """Request to clear cache."""

    query: Optional[str] = Field(
        default=None,
        description="Specific query to clear",
    )
    provider: Optional[str] = Field(
        default=None,
        description="Clear all entries from this provider",
    )
    clear_all: bool = Field(
        default=False,
        description="Clear all cache entries",
    )

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: Optional[str]) -> Optional[str]:
        """Validate provider name."""
        if v is None:
            return None

        valid = ["tavily", "perplexity-sonar", "gemini-deep-research"]
        v_lower = v.lower()
        if v_lower not in valid:
            raise ValueError(f"Provider must be one of: {', '.join(valid)}")
        return v_lower


class ProvidersStatusRequest(BaseModel):
    """Request for providers status."""

    # No parameters needed
    pass


class QuickResearchRequest(BaseModel):
    """Simplified research request for quick lookups."""

    query: str = Field(
        min_length=3,
        max_length=1000,
        description="Quick research query",
    )
    use_cache: bool = Field(
        default=True,
        description="Use cached results if available",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and normalize query."""
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty")
        return v


class DeepResearchRequest(BaseModel):
    """Request for deep, comprehensive research."""

    query: str = Field(
        min_length=10,
        max_length=5000,
        description="Deep research query (requires more detail)",
    )
    use_cache: bool = Field(
        default=True,
        description="Use cached results if available",
    )
    timeout_seconds: int = Field(
        default=300,
        ge=60,
        le=600,
        description="Max wait time for deep research (60-600 seconds)",
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate query for deep research."""
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty")
        if len(v.split()) < 3:
            raise ValueError("Deep research queries should have at least 3 words")
        return v
