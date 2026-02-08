"""Tests for CLI argument parsing, config loading, and setup."""

from typing import Any, Dict

import pytest

from agents.cli import (
    AGENTS,
    _apply_config_overrides,
    _build_user_message,
    _resolve_api_key,
    build_parser,
)
from agents.core.models import AgentDefinition


class TestBuildParser:
    """Tests for CLI argument parser."""

    def test_parser_creates(self) -> None:
        parser = build_parser()
        assert parser is not None

    def test_parse_pr_reviewer(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["pr-reviewer", "--pr", "42"])
        assert args.agent == "pr-reviewer"
        assert args.pr == 42

    def test_parse_test_generator(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["test-generator", "--path", "src/main.py"])
        assert args.agent == "test-generator"
        assert args.path == "src/main.py"

    def test_parse_research(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["research", "--topic", "async patterns"])
        assert args.agent == "research"
        assert args.topic == "async patterns"
        assert args.depth == "standard"

    def test_parse_global_options(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "--provider",
                "openai",
                "--model",
                "gpt-4o",
                "--dry-run",
                "--verbose",
                "--json",
                "--max-iterations",
                "10",
                "onboarding",
            ]
        )
        assert args.provider == "openai"
        assert args.model == "gpt-4o"
        assert args.dry_run
        assert args.verbose
        assert args.json_output
        assert args.max_iterations == 10
        assert args.agent == "onboarding"


class TestBuildUserMessage:
    """Tests for user message construction."""

    def test_pr_reviewer_message(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["pr-reviewer", "--pr", "99"])
        msg = _build_user_message("pr-reviewer", args)
        assert "#99" in msg
        assert "review" in msg.lower()

    def test_test_generator_message(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["test-generator", "--path", "src/app.py", "--framework", "jest"])
        msg = _build_user_message("test-generator", args)
        assert "src/app.py" in msg
        assert "jest" in msg

    def test_research_message(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["research", "--topic", "WebSocket patterns", "--depth", "deep"])
        msg = _build_user_message("research", args)
        assert "WebSocket patterns" in msg
        assert "deep" in msg


class TestApplyConfigOverrides:
    """Tests for config override application."""

    def test_no_overrides(self) -> None:
        agent_def = AgentDefinition(name="test", description="Test", max_iterations=10)
        config: Dict[str, Any] = {}
        result = _apply_config_overrides(agent_def, config)
        assert result.max_iterations == 10
        # Should return the same object when no overrides
        assert result is agent_def

    def test_max_iterations_override(self) -> None:
        agent_def = AgentDefinition(name="test", description="Test", max_iterations=10)
        config: Dict[str, Any] = {
            "agents": {"test": {"max_iterations": 30}},
        }
        result = _apply_config_overrides(agent_def, config)
        assert result.max_iterations == 30
        # Original should be unchanged
        assert agent_def.max_iterations == 10

    def test_temperature_override(self) -> None:
        agent_def = AgentDefinition(name="test", description="Test", temperature=0.3)
        config: Dict[str, Any] = {
            "agents": {"test": {"temperature": 0.7}},
        }
        result = _apply_config_overrides(agent_def, config)
        assert result.temperature == 0.7
        assert agent_def.temperature == 0.3

    def test_no_matching_agent(self) -> None:
        agent_def = AgentDefinition(name="test", description="Test")
        config: Dict[str, Any] = {
            "agents": {"other-agent": {"max_iterations": 50}},
        }
        result = _apply_config_overrides(agent_def, config)
        assert result is agent_def


class TestResolveApiKey:
    """Tests for API key resolution."""

    def test_anthropic_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-123")
        assert _resolve_api_key("anthropic") == "sk-test-123"

    def test_openai_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-456")
        assert _resolve_api_key("openai") == "sk-openai-456"

    def test_local_returns_none(self) -> None:
        assert _resolve_api_key("local") is None

    def test_missing_key_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        assert _resolve_api_key("anthropic") is None


class TestAgentRegistry:
    """Tests for the agent registry."""

    def test_all_agents_registered(self) -> None:
        expected = {
            "pr-reviewer",
            "test-generator",
            "tech-debt-hunter",
            "ci-fixer",
            "conflict-resolver",
            "research",
            "onboarding",
            "doc-auditor",
        }
        assert set(AGENTS.keys()) == expected

    def test_agents_are_valid_definitions(self) -> None:
        for name, agent_def in AGENTS.items():
            assert isinstance(agent_def, AgentDefinition)
            assert agent_def.name == name
            assert agent_def.description
            assert agent_def.max_iterations >= 1


class TestSingletonSafety:
    """Tests that CLI operations don't mutate singletons."""

    def test_copy_prevents_mutation(self) -> None:
        original = AGENTS["pr-reviewer"]
        original_iterations = original.max_iterations

        # Simulate CLI override via copy
        modified = original.copy(max_iterations=99)
        assert modified.max_iterations == 99
        assert original.max_iterations == original_iterations
