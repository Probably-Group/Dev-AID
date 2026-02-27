"""Tests for execution trace collection (JSONL recording)."""

import json
from pathlib import Path

from agents.core.models import AgentDefinition, AgentResult
from agents.core.trace_collector import TraceCollector, TraceConfig


def _make_agent_def(name: str = "test-agent") -> AgentDefinition:
    """Create a minimal AgentDefinition for testing."""
    return AgentDefinition(
        name=name,
        description="Test agent",
        tools=["read_file", "grep_search"],
        max_iterations=10,
        temperature=0.3,
    )


def _make_result(
    name: str = "test-agent",
    success: bool = True,
    output: str = "Done",
) -> AgentResult:
    """Create a minimal AgentResult for testing."""
    return AgentResult(
        agent_name=name,
        success=success,
        output=output,
        tool_calls_made=2,
        iterations=3,
        total_tokens={"input": 1000, "output": 200},
        total_cost=0.05,
    )


class TestTraceConfig:
    """Tests for TraceConfig dataclass."""

    def test_defaults(self) -> None:
        config = TraceConfig()
        assert not config.enabled
        assert isinstance(config.trace_dir, Path)
        assert config.include_output_preview is True
        assert config.output_preview_length == 500

    def test_enabled(self, tmp_path: Path) -> None:
        config = TraceConfig(enabled=True, trace_dir=tmp_path / "traces")
        assert config.enabled


class TestTraceCollector:
    """Tests for TraceCollector."""

    def test_start_and_end_trace(self, tmp_path: Path) -> None:
        config = TraceConfig(enabled=True, trace_dir=tmp_path)
        collector = TraceCollector(config=config, agent_name="pr-reviewer", model="claude-sonnet")

        agent_def = _make_agent_def("pr-reviewer")
        collector.start_trace(
            agent_def=agent_def,
            user_message="Review PR #42",
            system_prompt="You are a PR reviewer.",
            model="claude-sonnet",
        )
        collector.end_trace(_make_result("pr-reviewer"))

        # Verify trace file was created
        trace_dir = tmp_path / "pr-reviewer"
        trace_files = list(trace_dir.glob("*.jsonl"))
        assert len(trace_files) == 1

        # Verify content
        lines = trace_files[0].read_text().strip().split("\n")
        assert len(lines) >= 2  # At least start + end events

        start_event = json.loads(lines[0])
        assert start_event["event"] == "run_start"
        assert start_event["agent_name"] == "pr-reviewer"
        assert start_event["model"] == "claude-sonnet"
        assert "system_prompt_hash" in start_event

        end_event = json.loads(lines[-1])
        assert end_event["event"] == "run_end"
        assert end_event["success"] is True

    def test_record_iteration(self, tmp_path: Path) -> None:
        config = TraceConfig(enabled=True, trace_dir=tmp_path)
        collector = TraceCollector(config=config, agent_name="test", model="gpt-4o")

        agent_def = _make_agent_def("test")
        collector.start_trace(
            agent_def=agent_def,
            user_message="Do something",
            system_prompt="You are a test agent.",
            model="gpt-4o",
        )
        collector.record_iteration(
            iteration=1,
            tool_calls=[{"name": "read_file", "args": {"path": "x.py"}}],
            tokens_used={"input": 500, "output": 100},
            cost=0.02,
            stop_reason="tool_use",
            latency_ms=1234.5,
        )
        collector.end_trace(_make_result("test"))

        trace_files = list((tmp_path / "test").glob("*.jsonl"))
        lines = trace_files[0].read_text().strip().split("\n")

        # Find iteration event
        iter_event = json.loads(lines[1])
        assert iter_event["event"] == "iteration"
        assert iter_event["iteration"] == 1
        assert iter_event["cost"] == 0.02
        assert iter_event["stop_reason"] == "tool_use"

    def test_record_tool_result(self, tmp_path: Path) -> None:
        config = TraceConfig(enabled=True, trace_dir=tmp_path)
        collector = TraceCollector(config=config, agent_name="test", model="test")

        agent_def = _make_agent_def("test")
        collector.start_trace(
            agent_def=agent_def,
            user_message="Test",
            system_prompt="Test",
            model="test",
        )
        collector.record_tool_result(
            iteration=1,
            tool_name="read_file",
            success=True,
            output_length=1024,
            error=None,
            latency_ms=42.0,
        )
        collector.end_trace(_make_result("test"))

        trace_files = list((tmp_path / "test").glob("*.jsonl"))
        lines = trace_files[0].read_text().strip().split("\n")

        tool_event = json.loads(lines[1])
        assert tool_event["event"] == "tool_result"
        assert tool_event["tool_name"] == "read_file"
        assert tool_event["success"] is True
        assert tool_event["output_length"] == 1024
        assert tool_event["iteration"] == 1

    def test_no_trace_without_start(self, tmp_path: Path) -> None:
        """Without calling start_trace, _write_line is a no-op (no trace_path)."""
        config = TraceConfig(enabled=False, trace_dir=tmp_path)
        collector = TraceCollector(config=config, agent_name="test", model="test")

        # Calling record/end without start should not create files
        # (start_trace sets _trace_path; without it, _write_line returns early)
        collector.record_iteration(
            iteration=1,
            tool_calls=[],
            tokens_used={},
            cost=0.0,
            stop_reason="end_turn",
            latency_ms=0.0,
        )

        trace_files = list(tmp_path.glob("**/*.jsonl"))
        assert len(trace_files) == 0

    def test_creates_agent_subdirectory(self, tmp_path: Path) -> None:
        config = TraceConfig(enabled=True, trace_dir=tmp_path)
        collector = TraceCollector(config=config, agent_name="my-agent", model="test")

        agent_def = _make_agent_def("my-agent")
        collector.start_trace(
            agent_def=agent_def,
            user_message="Test",
            system_prompt="Test",
            model="test",
        )
        collector.end_trace(_make_result("my-agent"))

        assert (tmp_path / "my-agent").is_dir()

    def test_start_trace_returns_id(self, tmp_path: Path) -> None:
        config = TraceConfig(enabled=True, trace_dir=tmp_path)
        collector = TraceCollector(config=config, agent_name="test", model="test")
        agent_def = _make_agent_def("test")
        trace_id = collector.start_trace(
            agent_def=agent_def,
            user_message="Test",
            system_prompt="Test",
            model="test",
        )
        assert isinstance(trace_id, str)
        assert len(trace_id) == 12
        collector.end_trace(_make_result("test"))

    def test_output_preview_in_end_trace(self, tmp_path: Path) -> None:
        config = TraceConfig(enabled=True, trace_dir=tmp_path, output_preview_length=10)
        collector = TraceCollector(config=config, agent_name="test", model="test")
        agent_def = _make_agent_def("test")
        collector.start_trace(
            agent_def=agent_def,
            user_message="Test",
            system_prompt="Test",
            model="test",
        )
        result = _make_result("test", output="A" * 100)
        collector.end_trace(result)

        trace_files = list((tmp_path / "test").glob("*.jsonl"))
        lines = trace_files[0].read_text().strip().split("\n")
        end_event = json.loads(lines[-1])
        assert len(end_event["output_preview"]) == 10
        assert end_event["output_length"] == 100
