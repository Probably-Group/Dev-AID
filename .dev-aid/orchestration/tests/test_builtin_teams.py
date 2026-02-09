"""Tests for built-in team definitions."""

from typing import Dict, Set

import pytest
from agents.core.team_models import AgentSlot, TeamDefinition
from agents.teams.builtin_teams import (
    ARCHITECT_IMPLEMENT_TEAM,
    BUILTIN_TEAMS,
    ISSUE_RESOLUTION_TEAM,
    PR_REVIEW_TEAM,
    SECURITY_AUDIT_TEAM,
)

# Known agent names from the AGENTS registry in cli.py
KNOWN_AGENTS: Set[str] = {
    "pr-reviewer",
    "test-generator",
    "tech-debt-hunter",
    "ci-fixer",
    "conflict-resolver",
    "research",
    "onboarding",
    "doc-auditor",
}


class TestBuiltinTeamsLoad:
    """Verify all built-in teams load without errors."""

    def test_pr_review_team_loads(self) -> None:
        assert PR_REVIEW_TEAM.name == "pr-review-team"
        assert len(PR_REVIEW_TEAM.agents) == 3
        assert PR_REVIEW_TEAM.workflow == "parallel"

    def test_security_audit_team_loads(self) -> None:
        assert SECURITY_AUDIT_TEAM.name == "security-audit-team"
        assert len(SECURITY_AUDIT_TEAM.agents) == 3
        assert SECURITY_AUDIT_TEAM.workflow == "parallel"

    def test_architect_implement_team_loads(self) -> None:
        assert ARCHITECT_IMPLEMENT_TEAM.name == "architect-implement-team"
        assert len(ARCHITECT_IMPLEMENT_TEAM.agents) == 3
        assert ARCHITECT_IMPLEMENT_TEAM.workflow == "dag"

    def test_issue_resolution_team_loads(self) -> None:
        assert ISSUE_RESOLUTION_TEAM.name == "issue-resolution-team"
        assert len(ISSUE_RESOLUTION_TEAM.agents) == 3
        assert ISSUE_RESOLUTION_TEAM.workflow == "dag"

    def test_all_teams_in_registry(self) -> None:
        assert len(BUILTIN_TEAMS) == 4
        assert "pr-review-team" in BUILTIN_TEAMS
        assert "security-audit-team" in BUILTIN_TEAMS
        assert "architect-implement-team" in BUILTIN_TEAMS
        assert "issue-resolution-team" in BUILTIN_TEAMS


class TestAgentDefReferences:
    """Verify all agent_def_name references exist in AGENTS registry."""

    @pytest.mark.parametrize(
        "team_name",
        list(BUILTIN_TEAMS.keys()),
    )
    def test_agent_def_names_valid(self, team_name: str) -> None:
        team = BUILTIN_TEAMS[team_name]
        for slot in team.agents:
            assert slot.agent_def_name in KNOWN_AGENTS, (
                f"Team '{team_name}' agent '{slot.name}' references "
                f"unknown agent_def_name '{slot.agent_def_name}'. "
                f"Valid: {KNOWN_AGENTS}"
            )


class TestDAGNoCycles:
    """Verify DAG workflows have no circular dependencies."""

    @pytest.mark.parametrize(
        "team_name,team",
        [(name, team) for name, team in BUILTIN_TEAMS.items() if team.workflow == "dag"],
    )
    def test_no_cycles(self, team_name: str, team: TeamDefinition) -> None:
        """Topological sort should succeed (no cycles)."""
        slots_by_name: Dict[str, AgentSlot] = {s.name: s for s in team.agents}
        visited: Set[str] = set()
        in_stack: Set[str] = set()

        def visit(name: str) -> None:
            if name in in_stack:
                raise AssertionError(f"Cycle detected in team '{team_name}' at agent '{name}'")
            if name in visited:
                return
            in_stack.add(name)
            slot = slots_by_name.get(name)
            if slot:
                for dep in slot.depends_on:
                    visit(dep)
            in_stack.discard(name)
            visited.add(name)

        for name in slots_by_name:
            visit(name)

    @pytest.mark.parametrize(
        "team_name,team",
        [(name, team) for name, team in BUILTIN_TEAMS.items() if team.workflow == "dag"],
    )
    def test_depends_on_references_valid(self, team_name: str, team: TeamDefinition) -> None:
        """All depends_on references point to valid agent names in the team."""
        valid_names = {s.name for s in team.agents}
        for slot in team.agents:
            for dep in slot.depends_on:
                assert dep in valid_names, (
                    f"Team '{team_name}' agent '{slot.name}' depends on "
                    f"'{dep}' which is not in the team. Valid: {valid_names}"
                )


class TestTeamProperties:
    """Verify team-level properties are sensible."""

    @pytest.mark.parametrize("team_name", list(BUILTIN_TEAMS.keys()))
    def test_positive_budget(self, team_name: str) -> None:
        team = BUILTIN_TEAMS[team_name]
        assert team.max_budget_usd > 0

    @pytest.mark.parametrize("team_name", list(BUILTIN_TEAMS.keys()))
    def test_positive_timeout(self, team_name: str) -> None:
        team = BUILTIN_TEAMS[team_name]
        assert team.timeout_seconds > 0

    @pytest.mark.parametrize("team_name", list(BUILTIN_TEAMS.keys()))
    def test_unique_agent_names(self, team_name: str) -> None:
        team = BUILTIN_TEAMS[team_name]
        names = [s.name for s in team.agents]
        assert len(names) == len(set(names))

    @pytest.mark.parametrize("team_name", list(BUILTIN_TEAMS.keys()))
    def test_has_description(self, team_name: str) -> None:
        team = BUILTIN_TEAMS[team_name]
        assert len(team.description) > 10

    @pytest.mark.parametrize("team_name", list(BUILTIN_TEAMS.keys()))
    def test_agents_have_role_prompts(self, team_name: str) -> None:
        """Every agent slot should have a role prompt for differentiation."""
        team = BUILTIN_TEAMS[team_name]
        for slot in team.agents:
            assert (
                len(slot.role_prompt) > 0
            ), f"Agent '{slot.name}' in team '{team_name}' has no role_prompt"
