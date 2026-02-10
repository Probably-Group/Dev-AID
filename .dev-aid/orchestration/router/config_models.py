"""Pydantic models for Dev-AID Router configuration validation.

Provides optional validation for settings.json, routing.json, and
memory-bank configuration. Used by ConfigLoader to log warnings
on invalid configs without failing hard.
"""

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class MemoryBankConfig(BaseModel):
    """Configuration for memory bank"""

    auto_load: List[str] = Field(default_factory=lambda: ["activeContext.md"])
    on_demand: List[str] = Field(default_factory=list)
    max_files: Optional[int] = None
    standing_context_tokens: int = 1000
    standing_context_budget: str = "balanced"
    staleness_warning_days: int = 30

    @field_validator("standing_context_budget")
    @classmethod
    def validate_budget(cls, v: str) -> str:
        valid_budgets = {"minimal", "balanced", "generous"}
        if v not in valid_budgets:
            raise ValueError(
                f"Invalid standing_context_budget: {v}. Must be one of {valid_budgets}"
            )
        return v


class SettingsConfig(BaseModel):
    """Validated settings.json structure"""

    orchestration_mode: str = "solo"
    default_model: str = "claude-sonnet-4.5"
    enabled_providers: List[str] = Field(default_factory=lambda: ["claude"])
    project_name: Optional[str] = None
    memory_bank: Optional[MemoryBankConfig] = None

    @field_validator("orchestration_mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        valid_modes = {"solo", "ensemble", "challenger", "architect"}
        if v not in valid_modes:
            raise ValueError(f"Invalid orchestration mode: {v}. Must be one of {valid_modes}")
        return v


class RoutingConfig(BaseModel):
    """Validated routing.json structure"""

    modes: Optional[Dict[str, Any]] = None
    fallback_chain: List[str] = Field(
        default_factory=lambda: ["claude-sonnet", "gpt-4o", "gemini-flash"]
    )
    cost_limit_per_day: float = 100.0

    @field_validator("cost_limit_per_day")
    @classmethod
    def validate_cost_limit(cls, v: float) -> float:
        if v < 0:
            raise ValueError("cost_limit_per_day must be non-negative")
        return v


def validate_settings(data: Dict[str, Any]) -> Optional[SettingsConfig]:
    """Validate settings data, returning model or None on failure."""
    try:
        return SettingsConfig(**data)
    except Exception as e:
        logger.warning("Settings validation warning: %s", e)
        return None


def validate_routing(data: Dict[str, Any]) -> Optional[RoutingConfig]:
    """Validate routing data, returning model or None on failure."""
    try:
        return RoutingConfig(**data)
    except Exception as e:
        logger.warning("Routing validation warning: %s", e)
        return None
