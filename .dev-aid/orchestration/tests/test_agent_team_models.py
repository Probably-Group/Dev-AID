"""Tests for team models (data classes, validation, workflows)."""

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

    def test_values(self) -> None:
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.CLAIMED.value == "claimed"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.BLOCKED.value == "blocked"


class TestAgentStatus:
    """Tests for AgentStatus enum."""

    def test_values(self) -> None:
        assert AgentStatus.IDLE.value == "idle"
        assert AgentStatus.RUNNING.value == "running"
        assert AgentStatus.COMPLETED.value == "completed"
        assert AgentStatus.FAILED.value == "failed"


class TestTeamTask:
    """Tests for TeamTask dataclass."""

    def test_create_basic(self) -> None:
        task = TeamTask(
            id="task-1",
            title="Review the code",
        )
        assert task.id == "task-1"
        assert task.title == "Review the code"
        assert task.status == TaskStatus.PENDING
        assert task.depends_on == []
        assert task.blocked_by == []
        assert task.assigned_agent is None

    def test_generate_id(self) -> None:
        tid = TeamTask.generate_id()
        assert tid.startswith("tt_")
        assert len(tid) == 15  # "tt_" + 12 hex chars

    def test_is_ready_no_deps(self) -> None:
        task = TeamTask(id="t1", title="Do something")
        assert task.is_ready()

    def test_is_ready_no_blockers(self) -> None:
        task = TeamTask(id="t2", title="Do next", depends_on=["t1"], blocked_by=[])
        assert task.is_ready()

    def test_not_ready_with_blockers(self) -> None:
        task = TeamTask(id="t2", title="Do next", depends_on=["t1"], blocked_by=["t1"])
        assert not task.is_ready()

    def test_not_ready_wrong_status(self) -> None:
        task = TeamTask(id="t1", title="Done")
        task.status = TaskStatus.COMPLETED
        assert not task.is_ready()

    def test_ready_when_claimed(self) -> None:
        task = TeamTask(id="t1", title="Claimed task")
        task.status = TaskStatus.CLAIMED
        assert task.is_ready()

    def test_metadata(self) -> None:
        task = TeamTask(id="t1", title="Task", metadata={"priority": "high"})
        assert task.metadata["priority"] == "high"


class TestAgentMessage:
    """Tests for AgentMessage dataclass."""

    def test_create(self) -> None:
        msg = AgentMessage(
            id="msg-1",
            from_agent="researcher",
            to_agent="fixer",
            content="Found root cause: null pointer",
            message_type="finding",
        )
        assert msg.from_agent == "researcher"
        assert msg.to_agent == "fixer"
        assert msg.message_type == "finding"

    def test_generate_id(self) -> None:
        mid = AgentMessage.generate_id()
        assert mid.startswith("msg_")
        assert len(mid) == 16  # "msg_" + 12 hex chars

    def test_broadcast_message(self) -> None:
        msg = AgentMessage(
            id="msg-2",
            from_agent="coordinator",
            to_agent="*",
            content="All agents ready",
            message_type="status",
        )
        assert msg.to_agent == "*"

    def test_default_message_type(self) -> None:
        msg = AgentMessage(
            id="msg-3",
            from_agent="a",
            to_agent="b",
            content="test",
        )
        assert msg.message_type == "finding"

    def test_metadata(self) -> None:
        msg = AgentMessage(
            id="msg-4",
            from_agent="a",
            to_agent="b",
            content="test",
            metadata={"severity": "high"},
        )
        assert msg.metadata["severity"] == "high"


class TestAgentSlot:
    """Tests for AgentSlot dataclass."""

    def test_create_minimal(self) -> None:
        slot = AgentSlot(
            name="reviewer",
            agent_def_name="pr-reviewer",
        )
        assert slot.name == "reviewer"
        assert slot.agent_def_name == "pr-reviewer"
        assert slot.provider is None
        assert slot.model is None
        assert slot.role_prompt == ""
        assert slot.depends_on == []

    def test_create_with_overrides(self) -> None:
        slot = AgentSlot(
            name="reviewer",
            agent_def_name="pr-reviewer",
            provider="openai",
            model="gpt-4o",
            role_prompt="Review code for security issues",
            depends_on=["architect"],
        )
        assert slot.provider == "openai"
        assert slot.model == "gpt-4o"
        assert slot.role_prompt == "Review code for security issues"
        assert slot.depends_on == ["architect"]


class TestTeamDefinition:
    """Tests for TeamDefinition with validation."""

    def test_create_parallel_team(self) -> None:
        team = TeamDefinition(
            name="test-team",
            description="A test team",
            agents=[
                AgentSlot(name="a1", agent_def_name="pr-reviewer"),
                AgentSlot(name="a2", agent_def_name="test-generator"),
            ],
            workflow="parallel",
        )
        assert team.name == "test-team"
        assert len(team.agents) == 2
        assert team.workflow == "parallel"
        assert team.max_budget_usd > 0

    def test_create_sequential_team(self) -> None:
        team = TeamDefinition(
            name="seq-team",
            description="Sequential team",
            agents=[
                AgentSlot(name="a1", agent_def_name="research"),
            ],
            workflow="sequential",
        )
        assert team.workflow == "sequential"

    def test_create_dag_team(self) -> None:
        team = TeamDefinition(
            name="dag-team",
            description="DAG team",
            agents=[
                AgentSlot(name="researcher", agent_def_name="research"),
                AgentSlot(
                    name="fixer",
                    agent_def_name="ci-fixer",
                    depends_on=["researcher"],
                ),
            ],
            workflow="dag",
        )
        assert team.workflow == "dag"

    def test_duplicate_agent_names_rejected(self) -> None:
        with pytest.raises(ValueError, match="[Dd]uplicate"):
            TeamDefinition(
                name="bad",
                description="d",
                agents=[
                    AgentSlot(name="a", agent_def_name="x"),
                    AgentSlot(name="a", agent_def_name="y"),
                ],
                workflow="parallel",
            )

    def test_invalid_workflow_rejected(self) -> None:
        with pytest.raises(ValueError, match="[Ww]orkflow"):
            TeamDefinition(
                name="bad",
                description="d",
                agents=[
                    AgentSlot(name="a", agent_def_name="x"),
                ],
                workflow="random",
            )

    def test_empty_agents_rejected(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            TeamDefinition(
                name="bad",
                description="d",
                agents=[],
                workflow="parallel",
            )

    def test_invalid_aggregation_strategy(self) -> None:
        with pytest.raises(ValueError, match="aggregation_strategy"):
            TeamDefinition(
                name="bad",
                description="d",
                agents=[AgentSlot(name="a", agent_def_name="x")],
                workflow="parallel",
                aggregation_strategy="unknown",
            )

    def test_negative_budget_rejected(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            TeamDefinition(
                name="bad",
                description="d",
                agents=[AgentSlot(name="a", agent_def_name="x")],
                workflow="parallel",
                max_budget_usd=-1.0,
            )

    def test_dag_invalid_dependency(self) -> None:
        with pytest.raises(ValueError, match="depends on unknown"):
            TeamDefinition(
                name="bad",
                description="d",
                agents=[
                    AgentSlot(name="a", agent_def_name="x", depends_on=["nonexistent"]),
                ],
                workflow="dag",
            )

    def test_defaults(self) -> None:
        team = TeamDefinition(
            name="t",
            description="d",
            agents=[AgentSlot(name="a", agent_def_name="x")],
        )
        assert team.default_provider == "anthropic"
        assert team.aggregation_strategy == "concatenate"
        assert team.timeout_seconds == 600


class TestTeamResult:
    """Tests for TeamResult."""

    def test_create(self) -> None:
        result = TeamResult(
            team_name="test-team",
            success=True,
            aggregated_output="All done",
            agent_results={"a1": {"output": "ok"}, "a2": {"output": "ok"}},
            tasks_completed=2,
            tasks_failed=0,
        )
        assert result.success
        assert not result.partial
        assert result.tasks_completed == 2

    def test_partial_result(self) -> None:
        result = TeamResult(
            team_name="test-team",
            success=False,
            aggregated_output="Partial",
            agent_results={"a1": {"output": "ok"}, "a2": {"error": "failed"}},
            tasks_completed=1,
            tasks_failed=1,
            partial=True,
        )
        assert not result.success
        assert result.partial

    def test_defaults(self) -> None:
        result = TeamResult(
            team_name="t",
            success=True,
            aggregated_output="ok",
        )
        assert result.total_cost == 0.0
        assert result.total_tokens == {"input": 0, "output": 0}
        assert result.total_latency_ms == 0.0
        assert result.messages_exchanged == 0
        assert result.tasks_completed == 0
        assert result.tasks_failed == 0
