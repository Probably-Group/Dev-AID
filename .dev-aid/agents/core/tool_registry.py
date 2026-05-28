"""
Tool registry for discovering, registering, and executing tools.

Manages tool definitions, their handler callables, and exports
tool schemas in provider-specific formats (OpenAI, Anthropic, Gemini).
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from .models import ToolCall, ToolDefinition, ToolResult
from .safety import SafetyConfig

logger = logging.getLogger(__name__)

# Type for tool handler functions: (arguments) -> str
ToolHandler = Callable[..., str]


class ToolRegistry:
    """Registry for agent tools with safety enforcement."""

    def __init__(self, safety: Optional[SafetyConfig] = None) -> None:
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, ToolHandler] = {}
        self._safety = safety or SafetyConfig()

    def register(
        self,
        definition: ToolDefinition,
        handler: ToolHandler,
    ) -> None:
        """Register a tool with its definition and handler."""
        if definition.name in self._tools:
            logger.warning("Overwriting existing tool: %s", definition.name)
        self._tools[definition.name] = definition
        self._handlers[definition.name] = handler

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool definition by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def get_definitions(
        self, tool_names: Optional[List[str]] = None
    ) -> List[ToolDefinition]:
        """Get tool definitions, optionally filtered by name."""
        if tool_names is None:
            return list(self._tools.values())
        return [self._tools[n] for n in tool_names if n in self._tools]

    def execute(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call with safety checks."""
        name = tool_call.name

        # Check if tool exists
        if name not in self._tools:
            return ToolResult(
                call_id=tool_call.id,
                name=name,
                output="",
                success=False,
                error=f"Unknown tool: {name}",
            )

        definition = self._tools[name]

        # Safety check
        check = self._safety.check_tool_execution(
            tool_name=name,
            arguments=tool_call.arguments,
            risk_level=definition.risk_level,
        )
        if not check.allowed:
            logger.warning(
                "SECURITY: Tool '%s' blocked by safety check: %s", name, check.reason
            )
            return ToolResult(
                call_id=tool_call.id,
                name=name,
                output="",
                success=False,
                error=f"Safety check failed: {check.reason}",
            )

        # Execute handler
        handler = self._handlers[name]
        try:
            output = handler(**tool_call.arguments)
            return ToolResult(
                call_id=tool_call.id,
                name=name,
                output=str(output),
                success=True,
            )
        except Exception as e:
            logger.error("Tool '%s' execution failed: %s", name, e, exc_info=True)
            safe_error = type(e).__name__
            return ToolResult(
                call_id=tool_call.id,
                name=name,
                output="",
                success=False,
                error=f"Tool execution failed ({safe_error})",
            )

    # ── Provider-specific format exports ──────────────────────────────

    def to_openai_format(
        self,
        tool_names: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Export tool definitions in OpenAI function-calling format."""
        definitions = self.get_definitions(tool_names)
        tools: List[Dict[str, Any]] = []
        for defn in definitions:
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": defn.name,
                        "description": defn.description,
                        "parameters": {
                            "type": "object",
                            "properties": defn.parameters,
                            "required": defn.required_params,
                        },
                    },
                }
            )
        return tools

    def to_anthropic_format(
        self,
        tool_names: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Export tool definitions in Anthropic tool-use format."""
        definitions = self.get_definitions(tool_names)
        tools: List[Dict[str, Any]] = []
        for defn in definitions:
            tools.append(
                {
                    "name": defn.name,
                    "description": defn.description,
                    "input_schema": {
                        "type": "object",
                        "properties": defn.parameters,
                        "required": defn.required_params,
                    },
                }
            )
        return tools

    def to_gemini_format(
        self,
        tool_names: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Export tool definitions in Gemini FunctionDeclaration format."""
        definitions = self.get_definitions(tool_names)
        declarations: List[Dict[str, Any]] = []
        for defn in definitions:
            declarations.append(
                {
                    "name": defn.name,
                    "description": defn.description,
                    "parameters": {
                        "type": "object",
                        "properties": defn.parameters,
                        "required": defn.required_params,
                    },
                }
            )
        return declarations
