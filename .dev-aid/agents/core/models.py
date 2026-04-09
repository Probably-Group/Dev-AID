"""
Data models for the agent framework.

All core data structures used across the agent system:
tool definitions, tool calls/results, agent definitions, and agent results.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToolDefinition:
    """Schema definition for a tool available to agents."""

    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema
    required_params: List[str] = field(default_factory=list)
    risk_level: str = "safe"  # "safe", "moderate", "dangerous"

    def __post_init__(self) -> None:
        valid_risks = {"safe", "moderate", "dangerous"}
        if self.risk_level not in valid_risks:
            raise ValueError(
                f"Invalid risk_level '{self.risk_level}'. Must be one of: {valid_risks}"
            )


@dataclass
class ToolCall:
    """A tool invocation requested by the LLM."""

    id: str
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def generate_id() -> str:
        """Generate a unique tool call ID."""
        return f"tc_{uuid.uuid4().hex[:12]}"


@dataclass
class ToolResult:
    """Result from executing a tool."""

    call_id: str
    name: str
    output: str
    success: bool
    error: Optional[str] = None


@dataclass
class AgentDefinition:
    """Configuration for a built-in agent."""

    name: str
    description: str
    skills: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    system_prompt_extra: str = ""
    max_iterations: int = 25
    temperature: float = 0.3
    risk_level: str = "safe"
    output_format: Optional[str] = None  # "markdown", "json", "diff"

    def __post_init__(self) -> None:
        valid_risks = {"safe", "moderate", "dangerous"}
        if self.risk_level not in valid_risks:
            raise ValueError(
                f"Invalid risk_level '{self.risk_level}'. Must be one of: {valid_risks}"
            )
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")
        if not (0.0 <= self.temperature <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")

    def copy(self, **overrides: Any) -> "AgentDefinition":
        """Create a deep copy with optional field overrides."""
        from copy import deepcopy

        clone = deepcopy(self)
        for key, value in overrides.items():
            if not hasattr(clone, key):
                raise ValueError(f"Unknown field: {key}")
            setattr(clone, key, value)
        clone.__post_init__()
        return clone


@dataclass
class AgentResult:
    """Result from an agent execution run."""

    agent_name: str
    success: bool
    output: str
    tool_calls_made: int = 0
    iterations: int = 0
    total_tokens: Dict[str, int] = field(
        default_factory=lambda: {"input": 0, "output": 0}
    )
    total_cost: float = 0.0
    total_latency_ms: float = 0.0


class StopWatch:
    """Simple timing utility for measuring agent execution.

    Uses ``time.perf_counter`` (not ``time.monotonic``) because the latter has
    ~15.6 ms granularity on Windows (it wraps GetTickCount64), which makes
    short agent runs measure as 0.0 ms — see issue surfaced by
    ``test_team_runner.py::TestTeamRunnerMetrics::test_cost_tracked`` failing
    on Windows CI with ``assert 0.0 > 0``. ``perf_counter`` wraps
    QueryPerformanceCounter on Windows and has sub-microsecond resolution
    on every supported platform, so the same code path produces meaningful
    latency telemetry everywhere.
    """

    def __init__(self) -> None:
        self._start: float = time.perf_counter()

    def elapsed_ms(self) -> float:
        """Return elapsed time in milliseconds."""
        return (time.perf_counter() - self._start) * 1000.0
