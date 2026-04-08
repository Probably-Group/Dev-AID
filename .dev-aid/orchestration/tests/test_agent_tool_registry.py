"""Tests for agent tool registry."""

from typing import Any

import pytest
from agents.core.models import ToolCall, ToolDefinition
from agents.core.safety import SafetyConfig
from agents.core.tool_registry import ToolRegistry


@pytest.fixture
def sample_tool_def() -> ToolDefinition:
    return ToolDefinition(
        name="echo",
        description="Echoes input back",
        parameters={"text": {"type": "string", "description": "Text to echo"}},
        required_params=["text"],
        risk_level="safe",
    )


@pytest.fixture
def echo_handler() -> Any:
    def handler(text: str = "default") -> str:
        return f"Echo: {text}"

    return handler


@pytest.fixture
def registry(sample_tool_def: ToolDefinition, echo_handler: Any) -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(sample_tool_def, echo_handler)
    return reg


class TestToolRegistry:
    """Tests for ToolRegistry."""

    def test_register_and_list(self, registry: ToolRegistry) -> None:
        tools = registry.list_tools()
        assert "echo" in tools

    def test_get_tool(self, registry: ToolRegistry) -> None:
        tool = registry.get_tool("echo")
        assert tool is not None
        assert tool.name == "echo"

    def test_get_tool_not_found(self, registry: ToolRegistry) -> None:
        tool = registry.get_tool("nonexistent")
        assert tool is None

    def test_get_definitions(self, registry: ToolRegistry) -> None:
        defs = registry.get_definitions()
        assert len(defs) == 1
        assert defs[0].name == "echo"

    def test_get_definitions_filtered(self, registry: ToolRegistry) -> None:
        defs = registry.get_definitions(["echo"])
        assert len(defs) == 1
        defs = registry.get_definitions(["nonexistent"])
        assert len(defs) == 0

    def test_execute_success(self, registry: ToolRegistry) -> None:
        tc = ToolCall(id="tc_1", name="echo", arguments={"text": "hello"})
        result = registry.execute(tc)
        assert result.success
        assert result.output == "Echo: hello"
        assert result.call_id == "tc_1"

    def test_execute_unknown_tool(self, registry: ToolRegistry) -> None:
        tc = ToolCall(id="tc_1", name="unknown", arguments={})
        result = registry.execute(tc)
        assert not result.success
        assert "Unknown tool" in (result.error or "")

    def test_execute_handler_error(self) -> None:
        def bad_handler(**kwargs: Any) -> str:
            raise RuntimeError("Tool exploded")

        reg = ToolRegistry()
        reg.register(
            ToolDefinition(name="bad", description="Bad", parameters={}),
            bad_handler,
        )
        tc = ToolCall(id="tc_1", name="bad", arguments={})
        result = reg.execute(tc)
        assert not result.success
        assert "Tool exploded" in (result.error or "")

    def test_execute_safety_blocked(self) -> None:
        safety = SafetyConfig(allowed_tools={"read_file"})
        reg = ToolRegistry(safety=safety)
        reg.register(
            ToolDefinition(
                name="run_bash",
                description="Bash",
                parameters={},
                risk_level="dangerous",
            ),
            lambda **kw: "output",
        )
        tc = ToolCall(id="tc_1", name="run_bash", arguments={"command": "ls"})
        result = reg.execute(tc)
        assert not result.success
        assert "not in the allowed tools list" in (result.error or "")

    def test_execute_dry_run(self) -> None:
        safety = SafetyConfig(dry_run=True)
        reg = ToolRegistry(safety=safety)
        reg.register(
            ToolDefinition(
                name="write_file",
                description="Write",
                parameters={},
                risk_level="moderate",
            ),
            lambda **kw: "wrote",
        )
        tc = ToolCall(id="tc_1", name="write_file", arguments={"path": "/tmp/t", "content": "x"})
        result = reg.execute(tc)
        assert not result.success
        assert "Dry-run mode" in (result.error or "")


class TestProviderFormats:
    """Tests for provider-specific format exports."""

    def test_openai_format(self, registry: ToolRegistry) -> None:
        tools = registry.to_openai_format()
        assert len(tools) == 1
        tool = tools[0]
        assert tool["type"] == "function"
        assert tool["function"]["name"] == "echo"
        assert tool["function"]["parameters"]["required"] == ["text"]

    def test_anthropic_format(self, registry: ToolRegistry) -> None:
        tools = registry.to_anthropic_format()
        assert len(tools) == 1
        tool = tools[0]
        assert tool["name"] == "echo"
        assert "input_schema" in tool
        assert tool["input_schema"]["required"] == ["text"]

    def test_gemini_format(self, registry: ToolRegistry) -> None:
        tools = registry.to_gemini_format()
        assert len(tools) == 1
        tool = tools[0]
        assert tool["name"] == "echo"
        assert tool["parameters"]["required"] == ["text"]

    def test_format_filtered(self, registry: ToolRegistry) -> None:
        tools = registry.to_openai_format(["echo"])
        assert len(tools) == 1
        tools = registry.to_openai_format(["nonexistent"])
        assert len(tools) == 0
