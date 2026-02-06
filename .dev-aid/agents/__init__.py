"""
Dev-AID Agent Framework

Provider-agnostic autonomous agent framework powered by Dev-AID's
expert skills. Supports Claude, Gemini, OpenAI, and local models.
"""

__version__ = "0.1.0"
__author__ = "Dev-AID Contributors"

from .core.models import AgentDefinition, AgentResult, ToolCall, ToolDefinition, ToolResult
from .core.safety import SafetyConfig
from .core.tool_registry import ToolRegistry

__all__ = [
    "AgentDefinition",
    "AgentResult",
    "ToolCall",
    "ToolDefinition",
    "ToolResult",
    "SafetyConfig",
    "ToolRegistry",
]
