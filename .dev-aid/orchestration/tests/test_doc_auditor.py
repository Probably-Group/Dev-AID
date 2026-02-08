"""Tests for the doc-auditor agent definition and CLI integration."""

from typing import Set

import pytest

from agents.agents.doc_auditor import DOC_AUDITOR
from agents.cli import AGENTS, _build_user_message, build_parser
from agents.core.models import AgentDefinition


# Tools that should never appear on a safe/read-only agent
WRITE_TOOLS: Set[str] = {"write_file", "run_bash", "git_commit", "git_add"}


class TestDocAuditorDefinition:
    """Validate the AgentDefinition for doc-auditor."""

    def test_name(self) -> None:
        assert DOC_AUDITOR.name == "doc-auditor"

    def test_description(self) -> None:
        assert DOC_AUDITOR.description
        assert len(DOC_AUDITOR.description) > 10

    def test_risk_level_is_safe(self) -> None:
        assert DOC_AUDITOR.risk_level == "safe"

    def test_output_format_is_markdown(self) -> None:
        assert DOC_AUDITOR.output_format == "markdown"

    def test_no_write_tools(self) -> None:
        """A safe agent must not have write/execute tools."""
        for tool in DOC_AUDITOR.tools:
            assert (
                tool not in WRITE_TOOLS
            ), f"doc-auditor has write tool '{tool}' but is risk_level=safe"

    def test_has_required_read_tools(self) -> None:
        required = {"read_file", "glob_files", "grep_search"}
        agent_tools = set(DOC_AUDITOR.tools)
        assert required.issubset(agent_tools), f"Missing required tools: {required - agent_tools}"

    def test_system_prompt_mentions_audit(self) -> None:
        prompt = DOC_AUDITOR.system_prompt_extra or ""
        assert "audit" in prompt.lower()

    def test_system_prompt_mentions_severity(self) -> None:
        prompt = DOC_AUDITOR.system_prompt_extra or ""
        assert "critical" in prompt.lower()
        assert "warning" in prompt.lower()

    def test_system_prompt_mentions_report_sections(self) -> None:
        prompt = DOC_AUDITOR.system_prompt_extra or ""
        for section in [
            "Executive Summary",
            "Broken Links",
            "Missing Documentation",
            "Recommendations",
        ]:
            assert section in prompt, f"Missing report section: {section}"

    def test_max_iterations_reasonable(self) -> None:
        assert 10 <= DOC_AUDITOR.max_iterations <= 50

    def test_temperature_reasonable(self) -> None:
        assert 0.0 <= DOC_AUDITOR.temperature <= 1.0

    def test_copy_creates_independent_instance(self) -> None:
        copy = DOC_AUDITOR.copy(max_iterations=99)
        assert copy.max_iterations == 99
        assert DOC_AUDITOR.max_iterations != 99
        assert copy.name == DOC_AUDITOR.name

    def test_is_agent_definition(self) -> None:
        assert isinstance(DOC_AUDITOR, AgentDefinition)

    def test_has_skills(self) -> None:
        assert DOC_AUDITOR.skills
        assert len(DOC_AUDITOR.skills) >= 1


class TestDocAuditorCLI:
    """Validate CLI integration for doc-auditor."""

    def test_registered_in_agents_dict(self) -> None:
        assert "doc-auditor" in AGENTS
        assert AGENTS["doc-auditor"] is DOC_AUDITOR

    def test_parser_accepts_subcommand(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["doc-auditor"])
        assert args.agent == "doc-auditor"

    def test_scope_defaults_to_full(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["doc-auditor"])
        assert args.scope == "full"

    def test_scope_accepts_docs_only(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["doc-auditor", "--scope", "docs-only"])
        assert args.scope == "docs-only"

    def test_scope_accepts_code_only(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["doc-auditor", "--scope", "code-only"])
        assert args.scope == "code-only"

    def test_scope_rejects_invalid(self) -> None:
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["doc-auditor", "--scope", "invalid"])

    def test_path_optional(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["doc-auditor"])
        assert args.path is None

    def test_path_accepted(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["doc-auditor", "--path", "/some/project"])
        assert args.path == "/some/project"

    def test_build_user_message_default(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["doc-auditor"])
        msg = _build_user_message("doc-auditor", args)
        assert "the project" in msg
        assert "full" in msg

    def test_build_user_message_with_path(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["doc-auditor", "--path", "/my/repo"])
        msg = _build_user_message("doc-auditor", args)
        assert "/my/repo" in msg

    def test_build_user_message_with_scope(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["doc-auditor", "--scope", "docs-only"])
        msg = _build_user_message("doc-auditor", args)
        assert "docs-only" in msg

    def test_build_user_message_mentions_audit(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["doc-auditor"])
        msg = _build_user_message("doc-auditor", args)
        assert "audit" in msg.lower()
