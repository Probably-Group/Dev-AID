"""Tests for team orchestration data models."""

import pytest

from agents.core.team_models import (
    AgentMessage,
    AgentSlot,
    AgentStatus,
    TaskStatus,
    TeamDefinition,
    TeamResult,
    TeamTask,
)


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_all_statuses_exist(self) -> None:
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.CLAIMED.value == "claimed"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.BLOCKED.value == "blocked"


class TestAgentStatus:
    """Tests for AgentStatus enum."""

    def test_all_statuses_exist(self) -> None:
        assert AgentStatus.IDLE.value == "idle"
        assert AgentStatus.RUNNING.value == "running"
        assert AgentStatus.COMPLETED.value == "completed"
        assert AgentStatus.FAILED.value == "failed"


class TestTeamTask:
    """Tests for TeamTask dataclass."""

    def test_generate_id_uniqueness(self) -> None:
        ids = {TeamTask.generate_id() for _ in range(100)}
        assert len(ids) == 100

    def test_generate_id_prefix(self) -> None:
        task_id = TeamTask.generate_id()
        assert task_id.startswith("tt_")

    def test_is_ready_no_blockers(self) -> None:
        task = TeamTask(id="t1", title="Test task")
        assert task.is_ready()

    def test_is_ready_with_blockers(self) -> None:
        task = TeamTask(id="t1", title="Test", blocked_by=["t0"])
        assert not task.is_ready()

    def test_is_ready_when_completed(self) -> None:
        task = TeamTask(id="t1", title="Test", status=TaskStatus.COMPLETED)
        assert not task.is_ready()

    def test_is_ready_when_failed(self) -> None:
        task = TeamTask(id="t1", title="Test", status=TaskStatus.FAILED)
        assert not task.is_ready()

    def test_is_ready_when_claimed(self) -> None:
        task = TeamTask(id="t1", title="Test", status=TaskStatus.CLAIMED)
        assert task.is_ready()

    def test_default_values(self) -> None:
        task = TeamTask(id="t1", title="Test")
        assert task.description == ""
        assert task.assigned_agent is None
        assert task.status == TaskStatus.PENDING
        assert task.depends_on == []
        assert task.blocked_by == []
        assert task.result is None
        assert task.metadata == {}


class TestAgentMessage:
    """Tests for AgentMessage dataclass."""

    def test_generate_id_uniqueness(self) -> None:
        ids = {AgentMessage.generate_id() for _ in range(100)}
        assert len(ids) == 100

    def test_generate_id_prefix(self) -> None:
        msg_id = AgentMessage.generate_id()
        assert msg_id.startswith("msg_")

    def test_broadcast_message(self) -> None:
        msg = AgentMessage(
            id="m1",
            from_agent="reviewer",
            to_agent="*",
            content="Found a bug",
            message_type="finding",
        )
        assert msg.to_agent == "*"
        assert msg.message_type == "finding"

    def test_targeted_message(self) -> None:
        msg = AgentMessage(
            id="m1",
            from_agent="reviewer",
            to_agent="fixer",
            content="Please fix this",
            message_type="request",
        )
        assert msg.to_agent == "fixer"

    def test_default_message_type(self) -> None:
        msg = AgentMessage(id="m1", from_agent="a", to_agent="b", content="test")
        assert msg.message_type == "finding"


class TestAgentSlot:
    """Tests for AgentSlot dataclass."""

    def test_minimal_slot(self) -> None:
        slot = AgentSlot(name="reviewer", agent_def_name="pr-reviewer")
        assert slot.name == "reviewer"
        assert slot.agent_def_name == "pr-reviewer"
        assert slot.provider is None
        assert slot.model is None
        assert slot.role_prompt == ""
        assert slot.depends_on == []

    def test_slot_with_overrides(self) -> None:
        slot = AgentSlot(
            name="fast-reviewer",
            agent_def_name="pr-reviewer",
            provider="google",
            model="gemini-2.0-flash",
            role_prompt="Focus on security only.",
            depends_on=["architect"],
        )
        assert slot.provider == "google"
        assert slot.model == "gemini-2.0-flash"
        assert slot.role_prompt == "Focus on security only."
        assert slot.depends_on == ["architect"]


class TestTeamDefinition:
    """Tests for TeamDefinition validation."""

    def _make_agents(self, count: int = 2) -> list:  # type: ignore[type-arg]
        return [AgentSlot(name=f"agent-{i}", agent_def_name="pr-reviewer") for i in range(count)]

    def test_valid_team(self) -> None:
        team = TeamDefinition(
            name="test-team",
            description="A test team",
            agents=self._make_agents(3),
        )
        assert team.name == "test-team"
        assert len(team.agents) == 3

    def test_empty_agents_raises(self) -> None:
        with pytest.raises(ValueError, match="at least one agent"):
            TeamDefinition(name="empty", description="No agents", agents=[])

    def test_duplicate_agent_names_raises(self) -> None:
        agents = [
            AgentSlot(name="same", agent_def_name="pr-reviewer"),
            AgentSlot(name="same", agent_def_name="test-generator"),
        ]
        with pytest.raises(ValueError, match="unique"):
            TeamDefinition(name="dup", description="Dups", agents=agents)

    def test_invalid_workflow_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid workflow"):
            TeamDefinition(
                name="bad",
                description="Bad",
                agents=self._make_agents(),
                workflow="random",
            )

    def test_invalid_aggregation_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid aggregation_strategy"):
            TeamDefinition(
                name="bad",
                description="Bad",
                agents=self._make_agents(),
                aggregation_strategy="sum",
            )

    def test_negative_budget_raises(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            TeamDefinition(
                name="bad",
                description="Bad",
                agents=self._make_agents(),
                max_budget_usd=-1.0,
            )

    def test_zero_budget_allowed(self) -> None:
        team = TeamDefinition(
            name="free",
            description="Unlimited",
            agents=self._make_agents(),
            max_budget_usd=0.0,
        )
        assert team.max_budget_usd == 0.0

    def test_valid_dag_dependencies(self) -> None:
        agents = [
            AgentSlot(name="architect", agent_def_name="research"),
            AgentSlot(
                name="implementer",
                agent_def_name="test-generator",
                depends_on=["architect"],
            ),
        ]
        team = TeamDefinition(
            name="dag-team",
            description="DAG",
            agents=agents,
            workflow="dag",
        )
        assert team.workflow == "dag"

    def test_invalid_dag_dependency_raises(self) -> None:
        agents = [
            AgentSlot(
                name="implementer",
                agent_def_name="test-generator",
                depends_on=["nonexistent"],
            ),
        ]
        with pytest.raises(ValueError, match="unknown agent"):
            TeamDefinition(
                name="bad-dag",
                description="Bad DAG",
                agents=agents,
                workflow="dag",
            )

    def test_dag_validation_only_for_dag_workflow(self) -> None:
        """depends_on is not validated for non-DAG workflows."""
        agents = [
            AgentSlot(
                name="agent",
                agent_def_name="pr-reviewer",
                depends_on=["nonexistent"],
            ),
        ]
        # Should not raise for parallel workflow
        team = TeamDefinition(
            name="parallel",
            description="Parallel",
            agents=agents,
            workflow="parallel",
        )
        assert team.workflow == "parallel"

    def test_default_values(self) -> None:
        team = TeamDefinition(
            name="defaults",
            description="Test defaults",
            agents=self._make_agents(),
        )
        assert team.workflow == "parallel"
        assert team.max_budget_usd == 5.0
        assert team.default_provider == "anthropic"
        assert team.aggregation_strategy == "concatenate"
        assert team.timeout_seconds == 600


class TestTeamResult:
    """Tests for TeamResult dataclass."""

    def test_default_values(self) -> None:
        result = TeamResult(
            team_name="test",
            success=True,
            aggregated_output="All good",
        )
        assert result.agent_results == {}
        assert result.tasks_completed == 0
        assert result.tasks_failed == 0
        assert result.total_cost == 0.0
        assert result.total_tokens == {"input": 0, "output": 0}
        assert result.total_latency_ms == 0.0
        assert result.messages_exchanged == 0
        assert not result.partial

    def test_partial_result(self) -> None:
        result = TeamResult(
            team_name="test",
            success=True,
            aggregated_output="Partial",
            partial=True,
            tasks_completed=2,
            tasks_failed=1,
        )
        assert result.partial
        assert result.tasks_completed == 2
        assert result.tasks_failed == 1
