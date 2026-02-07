"""
Dev-AID Agent Framework

Provider-agnostic autonomous agent framework powered by Dev-AID's
expert skills. Supports Claude, Gemini, OpenAI, and local models.
"""

__version__ = "0.1.0"
__author__ = "Dev-AID Contributors"

from .core.models import (
    AgentDefinition,
    AgentResult,
    ToolCall,
    ToolDefinition,
    ToolResult,
)
from .core.safety import SafetyConfig
from .core.team_models import AgentSlot, TeamDefinition, TeamResult
from .core.team_runner import TeamRunner
from .core.tool_registry import ToolRegistry

__all__ = [
    "AgentDefinition",
    "AgentResult",
    "AgentSlot",
    "TeamDefinition",
    "TeamResult",
    "TeamRunner",
    "ToolCall",
    "ToolDefinition",
    "ToolResult",
    "SafetyConfig",
    "ToolRegistry",
]
