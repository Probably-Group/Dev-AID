"""Regression tests for audit Sprint-2 budget/timeout/truncation fixes (H8, M17)."""

from typing import Any, Dict, List

from agents.core.agent_runner import AgentRunner
from agents.core.models import AgentDefinition, ToolCall
from agents.core.provider_adapter import ProviderResponse
from agents.core.tool_registry import ToolRegistry


class _Adapter:
    """Returns one canned ProviderResponse for every call."""

    tool_format = "anthropic"

    def __init__(self, response: ProviderResponse) -> None:
        self._response = response
        self.calls = 0

    def send_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        system_prompt: str = "",
        model: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> ProviderResponse:
        self.calls += 1
        return self._response


def _runner(response: ProviderResponse) -> AgentRunner:
    return AgentRunner(adapter=_Adapter(response), registry=ToolRegistry())


# --------------------------------------------------------------------------- #
# M17 — malformed tool arguments are rejected, not run with {}
# --------------------------------------------------------------------------- #
def test_registry_rejects_parse_error_tool_call():
    registry = ToolRegistry()
    call = ToolCall(id="1", name="run_bash", parse_error="JSONDecodeError: {oops")
    result = registry.execute(call)
    assert result.success is False
    assert "Invalid tool arguments" in (result.error or "")


# --------------------------------------------------------------------------- #
# H8 — truncated final answer is not reported as a clean success
# --------------------------------------------------------------------------- #
def test_max_tokens_truncation_marks_failure():
    runner = _runner(ProviderResponse(content="partial", tool_calls=[], stop_reason="max_tokens"))
    result = runner.run(AgentDefinition(name="t", description="d"), "hi")
    assert result.success is False
    assert "max_tokens" in result.output


# --------------------------------------------------------------------------- #
# H8 — wall-clock deadline stops the loop
# --------------------------------------------------------------------------- #
def test_deadline_stops_before_first_call():
    adapter = _Adapter(ProviderResponse(content="done", tool_calls=[], stop_reason="end_turn"))
    runner = AgentRunner(adapter=adapter, registry=ToolRegistry())
    result = runner.run(AgentDefinition(name="t", description="d"), "hi", deadline_seconds=0.0)
    assert result.success is False
    assert "Time budget" in result.output
    assert adapter.calls == 0  # never even called the provider


# --------------------------------------------------------------------------- #
# H8 — cost budget stops the loop
# --------------------------------------------------------------------------- #
def test_cost_budget_stops_loop():
    runner = _runner(
        ProviderResponse(
            content="x",
            tool_calls=[],
            stop_reason="end_turn",
            tokens_used={"input": 10, "output": 10},
            cost=1.0,
        )
    )
    result = runner.run(AgentDefinition(name="t", description="d"), "hi", max_cost_usd=0.001)
    assert result.success is False
    assert "Cost budget" in result.output
