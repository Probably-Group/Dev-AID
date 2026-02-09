"""Tests for TeamRunner multi-agent orchestration engine."""

from typing import Any, Dict, List, Optional

import pytest
from agents.core.models import AgentDefinition, AgentResult, ToolCall, ToolDefinition, ToolResult
from agents.core.provider_adapter import ProviderResponse
from agents.core.safety import SafetyConfig
from agents.core.shared_state import MessageBus
from agents.core.team_models import AgentMessage, AgentSlot, TeamDefinition
from agents.core.team_runner import TeamRunner, _aggregate_concatenate, _aggregate_vote
from agents.core.tool_registry import ToolRegistry

# ── Test Fixtures ────────────────────────────────────────────────────


class MockAdapter:
    """Mock provider adapter that returns canned responses."""

    tool_format: str = "anthropic"

    def __init__(self, responses: Optional[List[ProviderResponse]] = None) -> None:
        self._responses = list(responses or [])
        self._call_count = 0

    def send_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        system_prompt: str = "",
        model: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> ProviderResponse:
        if not self._responses:
            return ProviderResponse(
                content="Mock response",
                tokens_used={"input": 100, "output": 50},
                cost=0.01,
            )
        idx = min(self._call_count, len(self._responses) - 1)
        self._call_count += 1
        return self._responses[idx]

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


# Patch create_adapter to return MockAdapter
_mock_adapter_instance: Optional[MockAdapter] = None


def _make_registry(safety: Optional[SafetyConfig] = None) -> ToolRegistry:
    """Create a simple test registry."""
    registry = ToolRegistry(safety=safety)
    registry.register(
        ToolDefinition(
            name="echo",
            description="Echo",
            parameters={"text": {"type": "string"}},
            required_params=["text"],
        ),
        lambda text="": f"Echo: {text}",
    )
    return registry


MOCK_AGENTS: Dict[str, AgentDefinition] = {
    "pr-reviewer": AgentDefinition(
        name="pr-reviewer",
        description="Review PRs",
        system_prompt_extra="You review code.",
    ),
    "test-generator": AgentDefinition(
        name="test-generator",
        description="Generate tests",
        system_prompt_extra="You write tests.",
    ),
    "research": AgentDefinition(
        name="research",
        description="Research topics",
        system_prompt_extra="You research.",
    ),
}


def _make_runner(
    on_agent_start: Optional[Any] = None,
    on_agent_complete: Optional[Any] = None,
    on_message: Optional[Any] = None,
) -> TeamRunner:
    """Create a TeamRunner with mock dependencies."""
    return TeamRunner(
        registry_factory=lambda safety: _make_registry(safety),
        skill_loader=None,
        agents_registry=MOCK_AGENTS,
        on_agent_start=on_agent_start,
        on_agent_complete=on_agent_complete,
        on_message=on_message,
    )


def _make_team(
    workflow: str = "parallel",
    agents: Optional[List[AgentSlot]] = None,
    aggregation: str = "concatenate",
    budget: float = 5.0,
) -> TeamDefinition:
    """Create a test team definition."""
    if agents is None:
        agents = [
            AgentSlot(name="reviewer-1", agent_def_name="pr-reviewer"),
            AgentSlot(name="reviewer-2", agent_def_name="pr-reviewer"),
        ]
    return TeamDefinition(
        name="test-team",
        description="Test team",
        agents=agents,
        workflow=workflow,
        max_budget_usd=budget,
        aggregation_strategy=aggregation,
    )


# ── Tests ────────────────────────────────────────────────────────────


class TestTeamRunnerParallel:
    """Tests for parallel execution strategy."""

    @pytest.mark.asyncio
    async def test_parallel_basic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """All agents run and return results."""
        monkeypatch.setattr(
            "agents.core.team_runner.create_adapter",
            lambda **kwargs: MockAdapter(),  # type: ignore[arg-type]
        )
        runner = _make_runner()
        team = _make_team(workflow="parallel")
        result = await runner.run(team, "Review the code")

        assert result.success
        assert result.team_name == "test-team"
        assert len(result.agent_results) == 2
        assert "reviewer-1" in result.agent_results
        assert "reviewer-2" in result.agent_results
        assert result.tasks_completed == 2
        assert result.tasks_failed == 0
        assert not result.partial

    @pytest.mark.asyncio
    async def test_parallel_one_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """One agent fails but team continues (graceful degradation)."""
        call_count = 0

        def mock_create(**kwargs: Any) -> MockAdapter:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First agent gets adapter that will fail
                return MockAdapter(
                    [ProviderResponse(content="Good review", cost=0.01)]
                )  # type: ignore[return-value]
            else:
                # Second agent gets adapter that raises
                adapter = MockAdapter()

                def fail_send(**kw: Any) -> ProviderResponse:
                    raise RuntimeError("API timeout")

                adapter.send_with_tools = fail_send  # type: ignore[assignment]
                return adapter  # type: ignore[return-value]

        monkeypatch.setattr("agents.core.team_runner.create_adapter", mock_create)
        runner = _make_runner()
        team = _make_team(workflow="parallel")
        result = await runner.run(team, "Review")

        assert result.success  # At least one succeeded
        assert result.partial  # But not all
        assert result.tasks_completed >= 1
        assert result.tasks_failed >= 1

    @pytest.mark.asyncio
    async def test_parallel_callbacks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Callbacks fire for agent start and complete."""
        monkeypatch.setattr(
            "agents.core.team_runner.create_adapter",
            lambda **kwargs: MockAdapter(),  # type: ignore[arg-type]
        )
        starts: List[str] = []
        completes: List[str] = []

        runner = _make_runner(
            on_agent_start=lambda name: starts.append(name),
            on_agent_complete=lambda name, result: completes.append(name),
        )
        team = _make_team()
        await runner.run(team, "Test")

        assert set(starts) == {"reviewer-1", "reviewer-2"}
        assert set(completes) == {"reviewer-1", "reviewer-2"}


class TestTeamRunnerSequential:
    """Tests for sequential execution strategy."""

    @pytest.mark.asyncio
    async def test_sequential_basic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Agents run in order and results accumulate."""
        monkeypatch.setattr(
            "agents.core.team_runner.create_adapter",
            lambda **kwargs: MockAdapter(),  # type: ignore[arg-type]
        )
        runner = _make_runner()
        team = _make_team(workflow="sequential")
        result = await runner.run(team, "Review the code")

        assert result.success
        assert result.tasks_completed == 2
        assert result.messages_exchanged == 2  # Each agent broadcasts

    @pytest.mark.asyncio
    async def test_sequential_budget_exhaustion(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Budget exhaustion skips remaining agents."""
        monkeypatch.setattr(
            "agents.core.team_runner.create_adapter",
            lambda **kwargs: MockAdapter(  # type: ignore[arg-type]
                [ProviderResponse(content="Expensive", cost=3.0)]
            ),
        )
        runner = _make_runner()
        agents = [
            AgentSlot(name="agent-1", agent_def_name="pr-reviewer"),
            AgentSlot(name="agent-2", agent_def_name="pr-reviewer"),
            AgentSlot(name="agent-3", agent_def_name="pr-reviewer"),
        ]
        team = _make_team(workflow="sequential", agents=agents, budget=3.0)
        result = await runner.run(team, "Review")

        # First agent uses $3.0 which hits budget, rest skipped
        assert result.tasks_completed >= 1
        # At least one should be skipped
        skipped = [
            name
            for name, r in result.agent_results.items()
            if "budget" in r.get("output", "").lower()
        ]
        assert len(skipped) >= 1


class TestTeamRunnerDAG:
    """Tests for DAG execution strategy."""

    @pytest.mark.asyncio
    async def test_dag_basic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DAG executes in dependency order."""

        def mock_create(**kwargs: Any) -> MockAdapter:
            return MockAdapter()  # type: ignore[return-value]

        monkeypatch.setattr("agents.core.team_runner.create_adapter", mock_create)

        starts: List[str] = []
        runner = _make_runner(on_agent_start=lambda name: starts.append(name))

        agents = [
            AgentSlot(name="architect", agent_def_name="research"),
            AgentSlot(
                name="implementer",
                agent_def_name="test-generator",
                depends_on=["architect"],
            ),
            AgentSlot(
                name="reviewer",
                agent_def_name="pr-reviewer",
                depends_on=["implementer"],
            ),
        ]
        team = _make_team(workflow="dag", agents=agents)
        result = await runner.run(team, "Plan and implement")

        assert result.success
        assert result.tasks_completed == 3
        # Architect must start before implementer, implementer before reviewer
        assert starts.index("architect") < starts.index("implementer")
        assert starts.index("implementer") < starts.index("reviewer")

    @pytest.mark.asyncio
    async def test_dag_parallel_batch(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Independent agents in DAG run in parallel."""
        monkeypatch.setattr(
            "agents.core.team_runner.create_adapter",
            lambda **kwargs: MockAdapter(),  # type: ignore[arg-type]
        )
        runner = _make_runner()

        agents = [
            AgentSlot(name="agent-a", agent_def_name="pr-reviewer"),
            AgentSlot(name="agent-b", agent_def_name="pr-reviewer"),
            AgentSlot(
                name="agent-c",
                agent_def_name="pr-reviewer",
                depends_on=["agent-a", "agent-b"],
            ),
        ]
        team = _make_team(workflow="dag", agents=agents)
        result = await runner.run(team, "Test")

        assert result.success
        assert result.tasks_completed == 3

    @pytest.mark.asyncio
    async def test_dag_messages_broadcast(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Completed agents broadcast their results."""
        monkeypatch.setattr(
            "agents.core.team_runner.create_adapter",
            lambda **kwargs: MockAdapter(),  # type: ignore[arg-type]
        )
        runner = _make_runner()

        agents = [
            AgentSlot(name="first", agent_def_name="research"),
            AgentSlot(
                name="second",
                agent_def_name="pr-reviewer",
                depends_on=["first"],
            ),
        ]
        team = _make_team(workflow="dag", agents=agents)
        result = await runner.run(team, "Test")

        assert result.messages_exchanged >= 2


class TestResolveAgentDef:
    """Tests for agent definition resolution."""

    def test_resolve_existing(self) -> None:
        runner = _make_runner()
        slot = AgentSlot(name="rev", agent_def_name="pr-reviewer")
        agent_def = runner._resolve_agent_def(slot)
        assert agent_def.name == "pr-reviewer"

    def test_resolve_with_role_prompt(self) -> None:
        runner = _make_runner()
        slot = AgentSlot(
            name="security-rev",
            agent_def_name="pr-reviewer",
            role_prompt="Focus on security vulnerabilities.",
        )
        agent_def = runner._resolve_agent_def(slot)
        assert "Focus on security" in agent_def.system_prompt_extra
        assert "You review code" in agent_def.system_prompt_extra

    def test_resolve_unknown_raises(self) -> None:
        runner = _make_runner()
        slot = AgentSlot(name="bad", agent_def_name="nonexistent")
        with pytest.raises(ValueError, match="not found"):
            runner._resolve_agent_def(slot)


class TestBuildTeamContext:
    """Tests for team context building."""

    def test_empty_context(self) -> None:
        bus = MessageBus()
        ctx = TeamRunner._build_team_context("agent-a", "", bus, {})
        assert ctx == ""

    def test_extra_context_included(self) -> None:
        bus = MessageBus()
        ctx = TeamRunner._build_team_context("agent-a", "Project info", bus, {})
        assert "Project info" in ctx

    def test_prior_results_included(self) -> None:
        bus = MessageBus()
        prior = {
            "reviewer-1": AgentResult(
                agent_name="reviewer-1",
                success=True,
                output="Looks good!",
            )
        }
        ctx = TeamRunner._build_team_context("agent-b", "", bus, prior)
        assert "reviewer-1" in ctx
        assert "Looks good!" in ctx
        assert "completed" in ctx

    def test_messages_included(self) -> None:
        bus = MessageBus()
        bus.send(
            AgentMessage(
                id="m1",
                from_agent="reviewer-1",
                to_agent="*",
                content="Found a bug in auth module",
                message_type="finding",
            )
        )
        ctx = TeamRunner._build_team_context("agent-b", "", bus, {})
        assert "Found a bug" in ctx
        assert "reviewer-1" in ctx

    def test_max_messages_limit(self) -> None:
        bus = MessageBus()
        for i in range(10):
            bus.send(
                AgentMessage(
                    id=f"m{i}",
                    from_agent="sender",
                    to_agent="*",
                    content=f"Message {i}",
                )
            )
        ctx = TeamRunner._build_team_context("receiver", "", bus, {})
        # Should only include last 5 messages
        assert "Message 9" in ctx
        assert "Message 5" in ctx
        assert "Message 4" not in ctx


class TestAggregation:
    """Tests for result aggregation strategies."""

    @pytest.mark.asyncio
    async def test_concatenate_strategy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "agents.core.team_runner.create_adapter",
            lambda **kwargs: MockAdapter(),  # type: ignore[arg-type]
        )
        runner = _make_runner()
        team = _make_team(aggregation="concatenate")
        result = await runner.run(team, "Test")

        assert "reviewer-1" in result.aggregated_output
        assert "reviewer-2" in result.aggregated_output

    @pytest.mark.asyncio
    async def test_vote_strategy(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "agents.core.team_runner.create_adapter",
            lambda **kwargs: MockAdapter(),  # type: ignore[arg-type]
        )
        runner = _make_runner()
        team = _make_team(aggregation="vote")
        result = await runner.run(team, "Test")

        assert "Vote Tally" in result.aggregated_output
        assert "2/2" in result.aggregated_output

    def test_concatenate_fn(self) -> None:
        results = {
            "agent-a": AgentResult(agent_name="agent-a", success=True, output="Output A"),
            "agent-b": AgentResult(agent_name="agent-b", success=False, output="Error B"),
        }
        output = _aggregate_concatenate(results)
        assert "agent-a (Completed)" in output
        assert "agent-b (Failed)" in output
        assert "Output A" in output
        assert "Error B" in output

    def test_vote_fn(self) -> None:
        results = {
            "a": AgentResult(agent_name="a", success=True, output="Good"),
            "b": AgentResult(agent_name="b", success=False, output="Bad"),
        }
        output = _aggregate_vote(results)
        assert "1/2 passed" in output
        assert "a: PASS" in output
        assert "b: FAIL" in output


class TestTeamRunnerMetrics:
    """Tests for result metrics collection."""

    @pytest.mark.asyncio
    async def test_cost_tracked(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "agents.core.team_runner.create_adapter",
            lambda **kwargs: MockAdapter(  # type: ignore[arg-type]
                [
                    ProviderResponse(
                        content="Done",
                        cost=0.05,
                        tokens_used={"input": 100, "output": 50},
                    )
                ]
            ),
        )
        runner = _make_runner()
        team = _make_team()
        result = await runner.run(team, "Test")

        assert result.total_cost == 0.10  # 2 agents * $0.05
        assert result.total_tokens["input"] == 200
        assert result.total_tokens["output"] == 100
        assert result.total_latency_ms > 0
