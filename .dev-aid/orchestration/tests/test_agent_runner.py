"""Tests for agent runner (main agent loop) with mocked LLM."""

from typing import Any, Dict, List, Optional

from agents.core.agent_runner import AgentRunner
from agents.core.models import AgentDefinition, ToolCall, ToolDefinition, ToolResult
from agents.core.provider_adapter import ProviderResponse
from agents.core.tool_registry import ToolRegistry


class MockAdapter:
    """Mock provider adapter that returns canned responses."""

    tool_format: str = "anthropic"

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
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": call_id,
                    "content": output,
                    "is_error": is_error,
                }
            ],
        }

    @staticmethod
    def format_tool_results(results: List[ToolResult]) -> List[Dict[str, Any]]:
        content: List[Dict[str, Any]] = []
        for r in results:
            content.append(
                {
                    "type": "tool_result",
                    "tool_use_id": r.call_id,
                    "content": r.output if r.success else (r.error or ""),
                    "is_error": not r.success,
                }
            )
        return [{"role": "user", "content": content}]

    @staticmethod
    def format_assistant_tool_use(
        tool_calls: List[ToolCall], text: Optional[str] = None
    ) -> Dict[str, Any]:
        content: List[Dict[str, Any]] = []
        if text:
            content.append({"type": "text", "text": text})
        for tc in tool_calls:
            content.append(
                {
                    "type": "tool_use",
                    "id": tc.id,
                    "name": tc.name,
                    "input": tc.arguments,
                }
            )
        return {"role": "assistant", "content": content}


class FailOnceAdapter(MockAdapter):
    """Adapter that fails on first call then succeeds."""

    def __init__(self, responses: List[ProviderResponse], fail_count: int = 1) -> None:
        super().__init__(responses)
        self._fail_count = fail_count
        self._attempt = 0

    def send_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        system_prompt: str = "",
        model: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> ProviderResponse:
        self._attempt += 1
        if self._attempt <= self._fail_count:
            raise RuntimeError("Transient API error")
        return super().send_with_tools(
            messages, tools, system_prompt, model, max_tokens, temperature
        )


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

    def test_multiple_tool_calls_batched(self) -> None:
        """Multiple tool calls in one turn are batched into a single result message."""
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

        # Verify tool results were batched (single user message with both results)
        second_call_messages = adapter.sent_messages[1]
        # Messages: user + assistant + batched_tool_results = 3
        assert len(second_call_messages) == 3
        tool_result_msg = second_call_messages[2]
        assert tool_result_msg["role"] == "user"
        # Batched: content should be a list with 2 tool_result blocks
        assert isinstance(tool_result_msg["content"], list)
        assert len(tool_result_msg["content"]) == 2

    def test_max_iterations_reached(self) -> None:
        """Agent hits max iterations without finishing."""
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

    def test_provider_error_after_retries(self) -> None:
        """Agent handles provider API error after exhausting retries."""

        class AlwaysFailAdapter(MockAdapter):
            def send_with_tools(self, **kwargs: Any) -> ProviderResponse:
                raise RuntimeError("API rate limited")

        registry = _make_registry()
        agent_def = AgentDefinition(name="test", description="Test")

        runner = AgentRunner(
            adapter=AlwaysFailAdapter([]),  # type: ignore[arg-type]
            registry=registry,
            max_retries=1,  # Only 1 attempt
        )
        result = runner.run(agent_def, "Test")

        assert not result.success
        assert "Provider error" in result.output

    def test_retry_succeeds_after_transient_error(self) -> None:
        """Agent retries on transient error and succeeds."""
        adapter = FailOnceAdapter(
            [ProviderResponse(content="Done!", tokens_used={"input": 50, "output": 10})],
            fail_count=1,
        )
        registry = _make_registry()
        agent_def = AgentDefinition(name="test", description="Test")

        runner = AgentRunner(
            adapter=adapter,  # type: ignore[arg-type]
            registry=registry,
            max_retries=3,
        )
        result = runner.run(agent_def, "Test")

        assert result.success
        assert result.output == "Done!"

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

        assert len(adapter.sent_messages) == 1
        assert result.success

    def test_cost_accumulated(self) -> None:
        """Cost is accumulated across iterations."""
        adapter = MockAdapter(
            [
                ProviderResponse(
                    content=None,
                    tool_calls=[ToolCall(id="tc_1", name="echo", arguments={"text": "hi"})],
                    stop_reason="tool_use",
                    tokens_used={"input": 100, "output": 50},
                    cost=0.001,
                ),
                ProviderResponse(
                    content="Done",
                    tokens_used={"input": 200, "output": 100},
                    cost=0.002,
                ),
            ]
        )
        registry = _make_registry()
        agent_def = AgentDefinition(name="test", description="Test")

        runner = AgentRunner(adapter=adapter, registry=registry)
        result = runner.run(agent_def, "Test")

        assert result.success
        assert result.total_cost == 0.003
        assert result.total_tokens["input"] == 300
        assert result.total_tokens["output"] == 150


class TestToolFormatSelection:
    """Tests that the runner selects the correct tool format."""

    def test_openai_format_used(self) -> None:
        """When adapter has tool_format='openai', OpenAI format is used."""

        class OpenAIMockAdapter(MockAdapter):
            tool_format: str = "openai"

        adapter = OpenAIMockAdapter(
            [ProviderResponse(content="Done", tokens_used={"input": 50, "output": 10})]
        )
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
        agent_def = AgentDefinition(name="test", description="Test", tools=["echo"])
        runner = AgentRunner(adapter=adapter, registry=registry)  # type: ignore[arg-type]

        # The runner should use openai format internally
        tool_defs = runner._get_tool_definitions(agent_def)
        assert tool_defs[0]["type"] == "function"
        assert "function" in tool_defs[0]

    def test_gemini_format_used(self) -> None:
        """When adapter has tool_format='gemini', Gemini format is used."""

        class GeminiMockAdapter(MockAdapter):
            tool_format: str = "gemini"

        adapter = GeminiMockAdapter(
            [ProviderResponse(content="Done", tokens_used={"input": 50, "output": 10})]
        )
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
        agent_def = AgentDefinition(name="test", description="Test", tools=["echo"])
        runner = AgentRunner(adapter=adapter, registry=registry)  # type: ignore[arg-type]

        tool_defs = runner._get_tool_definitions(agent_def)
        # Gemini format: {name, description, parameters}
        assert tool_defs[0]["name"] == "echo"
        assert "parameters" in tool_defs[0]
        assert "type" not in tool_defs[0]  # No "type": "function" wrapper

    def test_default_anthropic_format(self) -> None:
        """Default format is Anthropic when tool_format not set."""

        class NoFormatAdapter:
            """Adapter without tool_format attribute."""

            def __init__(self) -> None:
                pass

            def send_with_tools(self, **kwargs: Any) -> ProviderResponse:
                return ProviderResponse(content="Done", tokens_used={"input": 50, "output": 10})

        adapter = NoFormatAdapter()
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
        agent_def = AgentDefinition(name="test", description="Test", tools=["echo"])
        runner = AgentRunner(adapter=adapter, registry=registry)  # type: ignore[arg-type]

        tool_defs = runner._get_tool_definitions(agent_def)
        assert tool_defs[0]["name"] == "echo"
        assert "input_schema" in tool_defs[0]


class TestContextManagement:
    """Tests for context trimming."""

    def test_estimate_message_tokens(self) -> None:
        """Token estimation is roughly correct."""
        messages = [
            {"role": "user", "content": "a" * 400},  # ~100 tokens
        ]
        estimate = AgentRunner._estimate_message_tokens(messages)
        assert estimate == 100

    def test_context_trimming_triggers(self) -> None:
        """Context is trimmed when exceeding token budget."""
        adapter = MockAdapter(
            [ProviderResponse(content="Done", tokens_used={"input": 50, "output": 10})]
        )
        registry = _make_registry()

        runner = AgentRunner(
            adapter=adapter,
            registry=registry,
            max_context_tokens=50,  # Very low budget
        )

        # Build a large messages list
        messages: List[Dict[str, Any]] = [
            {"role": "user", "content": "Task description"},
            {"role": "assistant", "content": "x" * 1000},
            {"role": "user", "content": "y" * 1000},
            {"role": "assistant", "content": "z" * 1000},
            {"role": "user", "content": "w" * 1000},
            {"role": "assistant", "content": "v" * 1000},
            {"role": "user", "content": "u" * 1000},
            {"role": "assistant", "content": "Recent context"},
        ]

        runner._trim_context(messages)

        # First and last messages should be intact
        assert messages[0]["content"] == "Task description"
        assert messages[-1]["content"] == "Recent context"

        # Middle messages should be truncated
        assert len(messages[1]["content"]) < 1000
        assert "[truncated]" in messages[1]["content"]

    def test_no_trim_under_budget(self) -> None:
        """Context is not trimmed when under budget."""
        adapter = MockAdapter(
            [ProviderResponse(content="Done", tokens_used={"input": 50, "output": 10})]
        )
        registry = _make_registry()
        runner = AgentRunner(
            adapter=adapter,
            registry=registry,
            max_context_tokens=100_000,
        )

        messages: List[Dict[str, Any]] = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
        original_content = messages[1]["content"]
        runner._trim_context(messages)
        assert messages[1]["content"] == original_content
