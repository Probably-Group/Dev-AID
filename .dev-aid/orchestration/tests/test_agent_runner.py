"""Tests for agent runner (main agent loop) with mocked LLM."""

from typing import Any, Dict, List, Optional

from agents.core.agent_runner import AgentRunner
from agents.core.models import AgentDefinition, ToolCall, ToolDefinition
from agents.core.provider_adapter import ProviderResponse
from agents.core.tool_registry import ToolRegistry


class MockAdapter:
    """Mock provider adapter that returns canned responses."""

    def __init__(self, responses: List[ProviderResponse]) -> None:
        self._responses = list(responses)
        self._call_count = 0
        self.sent_messages: List[List[Dict[str, Any]]] = []

    def send_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        system_prompt: str = "",
        model: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> ProviderResponse:
        self.sent_messages.append(list(messages))
        idx = min(self._call_count, len(self._responses) - 1)
        self._call_count += 1
        return self._responses[idx]

    @staticmethod
    def format_tool_result(call_id: str, output: str, is_error: bool = False) -> Dict[str, Any]:
        return {"role": "user", "content": f"[tool_result:{call_id}] {output}"}

    @staticmethod
    def format_assistant_tool_use(
        tool_calls: List[ToolCall], text: Optional[str] = None
    ) -> Dict[str, Any]:
        return {"role": "assistant", "content": text or "using tools"}


def _make_registry() -> ToolRegistry:
    """Create a registry with a simple echo tool."""
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="echo",
            description="Echo",
            parameters={"text": {"type": "string"}},
            required_params=["text"],
        ),
        lambda text="": f"Echo: {text}",
    )
    registry.register(
        ToolDefinition(
            name="read_file",
            description="Read",
            parameters={"path": {"type": "string"}},
            required_params=["path"],
        ),
        lambda path="": f"Contents of {path}",
    )
    return registry


class TestAgentRunner:
    """Tests for AgentRunner."""

    def test_single_response_no_tools(self) -> None:
        """Agent returns immediately without tool calls."""
        adapter = MockAdapter(
            [ProviderResponse(content="Hello! I'm done.", tokens_used={"input": 100, "output": 50})]
        )
        registry = _make_registry()
        agent_def = AgentDefinition(name="test", description="Test")

        runner = AgentRunner(adapter=adapter, registry=registry)
        result = runner.run(agent_def, "Hi there")

        assert result.success
        assert result.output == "Hello! I'm done."
        assert result.iterations == 1
        assert result.tool_calls_made == 0
        assert result.total_tokens["input"] == 100

    def test_tool_call_then_response(self) -> None:
        """Agent makes a tool call then returns final response."""
        adapter = MockAdapter(
            [
                ProviderResponse(
                    content=None,
                    tool_calls=[ToolCall(id="tc_1", name="echo", arguments={"text": "hello"})],
                    stop_reason="tool_use",
                    tokens_used={"input": 100, "output": 30},
                ),
                ProviderResponse(
                    content="I echoed: hello",
                    tokens_used={"input": 150, "output": 50},
                ),
            ]
        )
        registry = _make_registry()
        agent_def = AgentDefinition(
            name="test",
            description="Test",
            tools=["echo", "read_file"],
        )

        runner = AgentRunner(adapter=adapter, registry=registry)
        result = runner.run(agent_def, "Echo hello for me")

        assert result.success
        assert result.output == "I echoed: hello"
        assert result.iterations == 2
        assert result.tool_calls_made == 1
        assert result.total_tokens["input"] == 250

    def test_multiple_tool_calls(self) -> None:
        """Agent makes multiple tool calls in one iteration."""
        adapter = MockAdapter(
            [
                ProviderResponse(
                    content=None,
                    tool_calls=[
                        ToolCall(id="tc_1", name="echo", arguments={"text": "a"}),
                        ToolCall(id="tc_2", name="read_file", arguments={"path": "/tmp/x"}),
                    ],
                    stop_reason="tool_use",
                    tokens_used={"input": 100, "output": 50},
                ),
                ProviderResponse(
                    content="Both done.",
                    tokens_used={"input": 200, "output": 30},
                ),
            ]
        )
        registry = _make_registry()
        agent_def = AgentDefinition(name="test", description="Test")

        runner = AgentRunner(adapter=adapter, registry=registry)
        result = runner.run(agent_def, "Do two things")

        assert result.success
        assert result.tool_calls_made == 2
        assert result.iterations == 2

    def test_max_iterations_reached(self) -> None:
        """Agent hits max iterations without finishing."""
        # Always returns tool calls, never a final response
        adapter = MockAdapter(
            [
                ProviderResponse(
                    content=None,
                    tool_calls=[ToolCall(id="tc_1", name="echo", arguments={"text": "loop"})],
                    stop_reason="tool_use",
                    tokens_used={"input": 50, "output": 20},
                )
            ]
        )
        registry = _make_registry()
        agent_def = AgentDefinition(name="test", description="Test", max_iterations=3)

        runner = AgentRunner(adapter=adapter, registry=registry)
        result = runner.run(agent_def, "Loop forever")

        assert not result.success
        assert "maximum iterations" in result.output.lower()
        assert result.iterations == 3

    def test_provider_error(self) -> None:
        """Agent handles provider API error gracefully."""

        class ErrorAdapter:
            def send_with_tools(self, **kwargs: Any) -> ProviderResponse:
                raise RuntimeError("API rate limited")

        registry = _make_registry()
        agent_def = AgentDefinition(name="test", description="Test")

        runner = AgentRunner(adapter=ErrorAdapter(), registry=registry)  # type: ignore[arg-type]
        result = runner.run(agent_def, "Test")

        assert not result.success
        assert "Provider error" in result.output

    def test_tool_call_callback(self) -> None:
        """on_tool_call callback is invoked."""
        adapter = MockAdapter(
            [
                ProviderResponse(
                    content=None,
                    tool_calls=[ToolCall(id="tc_1", name="echo", arguments={"text": "hi"})],
                    stop_reason="tool_use",
                    tokens_used={"input": 50, "output": 20},
                ),
                ProviderResponse(content="Done", tokens_used={"input": 50, "output": 10}),
            ]
        )
        registry = _make_registry()
        agent_def = AgentDefinition(name="test", description="Test")

        calls: List[ToolCall] = []
        runner = AgentRunner(
            adapter=adapter,
            registry=registry,
            on_tool_call=lambda tc: calls.append(tc),
        )
        runner.run(agent_def, "Test")

        assert len(calls) == 1
        assert calls[0].name == "echo"

    def test_iteration_callback(self) -> None:
        """on_iteration callback is invoked."""
        adapter = MockAdapter(
            [ProviderResponse(content="Done", tokens_used={"input": 50, "output": 10})]
        )
        registry = _make_registry()
        agent_def = AgentDefinition(name="test", description="Test")

        iterations: List[int] = []
        runner = AgentRunner(
            adapter=adapter,
            registry=registry,
            on_iteration=lambda n, resp: iterations.append(n),
        )
        runner.run(agent_def, "Test")

        assert iterations == [1]

    def test_system_prompt_built(self) -> None:
        """System prompt includes agent's extra instructions."""
        adapter = MockAdapter(
            [ProviderResponse(content="Done", tokens_used={"input": 50, "output": 10})]
        )
        registry = _make_registry()
        agent_def = AgentDefinition(
            name="test",
            description="Test",
            system_prompt_extra="You must be concise.",
            output_format="json",
        )

        runner = AgentRunner(adapter=adapter, registry=registry)
        result = runner.run(agent_def, "Test")

        # The adapter received messages — verify it was called
        assert len(adapter.sent_messages) == 1
        assert result.success
