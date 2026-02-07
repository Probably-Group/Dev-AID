"""
Data models for multi-agent team orchestration.

Defines team composition (AgentSlot, TeamDefinition), shared tasks (TeamTask),
inter-agent messaging (AgentMessage), and aggregated results (TeamResult).
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """Status of a shared task within a team."""

    PENDING = "pending"
    CLAIMED = "claimed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class AgentStatus(Enum):
    """Status of an agent within a team run."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TeamTask:
    """A shared task within a team execution.

    Tasks can have dependencies (depends_on) and are tracked
    through the SharedTaskList for coordination.
    """

    id: str
    title: str
    description: str = ""
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    depends_on: List[str] = field(default_factory=list)
    blocked_by: List[str] = field(default_factory=list)
    result: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def generate_id() -> str:
        """Generate a unique task ID."""
        return f"tt_{uuid.uuid4().hex[:12]}"

    def is_ready(self) -> bool:
        """Check if this task is ready to be worked on.

        A task is ready when it has no unresolved blockers
        and is in a pending or claimed state.
        """
        return len(self.blocked_by) == 0 and self.status in (
            TaskStatus.PENDING,
            TaskStatus.CLAIMED,
        )


@dataclass
class AgentMessage:
    """Inter-agent message for coordination.

    Messages flow through the MessageBus. Use to_agent="*" for broadcasts.
    """

    id: str
    from_agent: str
    to_agent: str  # "*" = broadcast to all
    content: str
    message_type: str = "finding"  # "finding", "request", "handoff", "vote"
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def generate_id() -> str:
        """Generate a unique message ID."""
        return f"msg_{uuid.uuid4().hex[:12]}"


@dataclass
class AgentSlot:
    """One agent within a team definition.

    Maps a unique slot name to a base agent definition (from the AGENTS
    registry) with optional overrides for provider, model, and role prompt.
    """

    name: str  # Unique within the team
    agent_def_name: str  # References AGENTS registry key
    provider: Optional[str] = None  # Override default provider
    model: Optional[str] = None  # Override default model
    role_prompt: str = ""  # Extra role-specific instructions
    depends_on: List[str] = field(default_factory=list)  # For DAG workflows


@dataclass
class TeamDefinition:
    """Defines a team of agents and how they collaborate.

    Attributes:
        name: Unique team identifier.
        description: Human-readable description.
        agents: List of agent slots in the team.
        workflow: Execution strategy ("parallel", "sequential", "dag").
        max_budget_usd: Maximum total spend in USD (0 = unlimited).
        default_provider: Fallback provider for agents without overrides.
        default_model: Fallback model for agents without overrides.
        aggregation_strategy: How to combine agent outputs
            ("concatenate", "merge_sections", "vote").
        timeout_seconds: Maximum total execution time.
    """

    name: str
    description: str
    agents: List[AgentSlot]
    workflow: str = "parallel"  # "parallel", "sequential", "dag"
    max_budget_usd: float = 5.0
    default_provider: str = "anthropic"
    default_model: str = "claude-sonnet-4-5-20250929"
    aggregation_strategy: str = "concatenate"
    timeout_seconds: int = 600

    def __post_init__(self) -> None:
        if not self.agents:
            raise ValueError("TeamDefinition must have at least one agent")

        # Validate unique agent names
        names = [a.name for a in self.agents]
        if len(names) != len(set(names)):
            raise ValueError(
                "Agent names must be unique within a team. "
                f"Duplicates found in: {names}"
            )

        # Validate workflow
        valid_workflows = {"parallel", "sequential", "dag"}
        if self.workflow not in valid_workflows:
            raise ValueError(
                f"Invalid workflow '{self.workflow}'. "
                f"Must be one of: {valid_workflows}"
            )

        # Validate aggregation strategy
        valid_strategies = {"concatenate", "merge_sections", "vote"}
        if self.aggregation_strategy not in valid_strategies:
            raise ValueError(
                f"Invalid aggregation_strategy '{self.aggregation_strategy}'. "
                f"Must be one of: {valid_strategies}"
            )

        # Validate budget
        if self.max_budget_usd < 0:
            raise ValueError("max_budget_usd must be non-negative")

        # Validate DAG dependencies reference valid agent names
        if self.workflow == "dag":
            valid_names = set(names)
            for agent in self.agents:
                for dep in agent.depends_on:
                    if dep not in valid_names:
                        raise ValueError(
                            f"Agent '{agent.name}' depends on unknown agent "
                            f"'{dep}'. Valid names: {valid_names}"
                        )


@dataclass
class TeamResult:
    """Aggregated result from a team execution."""

    team_name: str
    success: bool
    aggregated_output: str
    agent_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_cost: float = 0.0
    total_tokens: Dict[str, int] = field(
        default_factory=lambda: {"input": 0, "output": 0}
    )
    total_latency_ms: float = 0.0
    messages_exchanged: int = 0
    partial: bool = False  # True if some agents failed but team continued
