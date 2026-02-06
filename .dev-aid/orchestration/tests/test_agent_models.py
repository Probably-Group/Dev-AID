"""Tests for agent framework data models."""

import pytest

from agents.core.models import (
    AgentDefinition,
    AgentResult,
    StopWatch,
    ToolCall,
    ToolDefinition,
    ToolResult,
)


class TestToolDefinition:
    """Tests for ToolDefinition dataclass."""

    def test_create_basic(self) -> None:
        td = ToolDefinition(
            name="test_tool",
            description="A test tool",
            parameters={"arg1": {"type": "string"}},
        )
        assert td.name == "test_tool"
        assert td.risk_level == "safe"
        assert td.required_params == []

    def test_create_with_all_fields(self) -> None:
        td = ToolDefinition(
            name="dangerous_tool",
            description="Risky",
            parameters={"cmd": {"type": "string"}},
            required_params=["cmd"],
            risk_level="dangerous",
        )
        assert td.risk_level == "dangerous"
        assert td.required_params == ["cmd"]

    def test_invalid_risk_level(self) -> None:
        with pytest.raises(ValueError, match="Invalid risk_level"):
            ToolDefinition(
                name="bad",
                description="Bad",
                parameters={},
                risk_level="extreme",
            )

    def test_valid_risk_levels(self) -> None:
        for level in ("safe", "moderate", "dangerous"):
            td = ToolDefinition(
                name="t",
                description="d",
                parameters={},
                risk_level=level,
            )
            assert td.risk_level == level


class TestToolCall:
    """Tests for ToolCall dataclass."""

    def test_create(self) -> None:
        tc = ToolCall(id="tc_123", name="read_file", arguments={"path": "/tmp/test"})
        assert tc.id == "tc_123"
        assert tc.name == "read_file"
        assert tc.arguments == {"path": "/tmp/test"}

    def test_default_arguments(self) -> None:
        tc = ToolCall(id="tc_456", name="git_status")
        assert tc.arguments == {}

    def test_generate_id(self) -> None:
        id1 = ToolCall.generate_id()
        id2 = ToolCall.generate_id()
        assert id1.startswith("tc_")
        assert len(id1) == 15  # "tc_" + 12 hex chars
        assert id1 != id2


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_success(self) -> None:
        tr = ToolResult(
            call_id="tc_123",
            name="read_file",
            output="file contents",
            success=True,
        )
        assert tr.success
        assert tr.error is None

    def test_failure(self) -> None:
        tr = ToolResult(
            call_id="tc_123",
            name="read_file",
            output="",
            success=False,
            error="File not found",
        )
        assert not tr.success
        assert tr.error == "File not found"


class TestAgentDefinition:
    """Tests for AgentDefinition dataclass."""

    def test_create_minimal(self) -> None:
        ad = AgentDefinition(name="test", description="Test agent")
        assert ad.name == "test"
        assert ad.skills == []
        assert ad.tools == []
        assert ad.max_iterations == 25
        assert ad.temperature == 0.3
        assert ad.risk_level == "safe"
        assert ad.output_format is None

    def test_create_full(self) -> None:
        ad = AgentDefinition(
            name="pr-reviewer",
            description="Reviews PRs",
            skills=["appsec-expert"],
            tools=["read_file", "git_diff"],
            system_prompt_extra="Extra instructions",
            max_iterations=15,
            temperature=0.5,
            risk_level="moderate",
            output_format="markdown",
        )
        assert ad.skills == ["appsec-expert"]
        assert ad.output_format == "markdown"

    def test_invalid_risk_level(self) -> None:
        with pytest.raises(ValueError, match="Invalid risk_level"):
            AgentDefinition(name="bad", description="d", risk_level="nuclear")

    def test_invalid_max_iterations(self) -> None:
        with pytest.raises(ValueError, match="max_iterations must be at least 1"):
            AgentDefinition(name="bad", description="d", max_iterations=0)

    def test_invalid_temperature(self) -> None:
        with pytest.raises(ValueError, match="temperature must be between"):
            AgentDefinition(name="bad", description="d", temperature=3.0)


class TestAgentResult:
    """Tests for AgentResult dataclass."""

    def test_success_result(self) -> None:
        ar = AgentResult(
            agent_name="test",
            success=True,
            output="Done!",
            tool_calls_made=5,
            iterations=3,
        )
        assert ar.success
        assert ar.total_tokens == {"input": 0, "output": 0}
        assert ar.total_cost == 0.0

    def test_failure_result(self) -> None:
        ar = AgentResult(
            agent_name="test",
            success=False,
            output="Error occurred",
            total_tokens={"input": 1000, "output": 500},
            total_cost=0.05,
        )
        assert not ar.success
        assert ar.total_tokens["input"] == 1000


class TestStopWatch:
    """Tests for StopWatch timing utility."""

    def test_elapsed(self) -> None:
        import time

        sw = StopWatch()
        time.sleep(0.05)
        elapsed = sw.elapsed_ms()
        assert elapsed >= 40  # Allow some tolerance
        assert elapsed < 500  # But not too much
