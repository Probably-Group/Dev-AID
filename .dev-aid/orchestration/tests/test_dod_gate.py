"""Tests for the DoD Gate agent definition and verdict parsing."""

from agents.agents.dod_gate import DOD_GATE
from agents.cli import (
    AGENTS,
    _extract_dod_suggestions,
    _extract_dod_summary,
    _parse_dod_verdict,
    build_parser,
)


class TestDoDGateDefinition:
    """Test the DOD_GATE agent definition."""

    def test_name(self) -> None:
        assert DOD_GATE.name == "dod-gate"

    def test_risk_level(self) -> None:
        assert DOD_GATE.risk_level == "safe"

    def test_max_iterations(self) -> None:
        assert DOD_GATE.max_iterations == 5

    def test_temperature(self) -> None:
        assert DOD_GATE.temperature == 0.1

    def test_tools_are_read_only(self) -> None:
        expected_tools = {"read_file", "glob_files", "grep_search"}
        assert set(DOD_GATE.tools) == expected_tools

    def test_no_skills(self) -> None:
        assert DOD_GATE.skills == []

    def test_system_prompt_has_verification_checks(self) -> None:
        prompt = DOD_GATE.system_prompt_extra
        assert "Request Addressed" in prompt
        assert "Concrete Artifacts" in prompt
        assert "Verification Story" in prompt
        assert "Risk Assessment" in prompt

    def test_system_prompt_has_verdict_format(self) -> None:
        prompt = DOD_GATE.system_prompt_extra
        assert "Overall Verdict" in prompt
        assert "PASS" in prompt
        assert "WARN" in prompt
        assert "FAIL" in prompt

    def test_output_format(self) -> None:
        assert DOD_GATE.output_format == "markdown"


class TestDoDVerdictParsing:
    """Test the DoD verdict parsing helpers."""

    def test_parse_pass(self) -> None:
        output = "Some text\n\n**Overall Verdict**: PASS\n\nMore text"
        assert _parse_dod_verdict(output) == "PASS"

    def test_parse_fail(self) -> None:
        output = "**Overall Verdict**: FAIL"
        assert _parse_dod_verdict(output) == "FAIL"

    def test_parse_warn(self) -> None:
        output = "**Overall Verdict**: WARN"
        assert _parse_dod_verdict(output) == "WARN"

    def test_parse_unknown_when_missing(self) -> None:
        output = "No verdict here"
        assert _parse_dod_verdict(output) == "UNKNOWN"

    def test_parse_case_insensitive(self) -> None:
        output = "**Overall Verdict**: pass"
        assert _parse_dod_verdict(output) == "PASS"

    def test_extract_summary(self) -> None:
        output = "**Summary**: The agent output meets all criteria.\n\n" "Some other text"
        assert _extract_dod_summary(output) == "The agent output meets all criteria."

    def test_extract_summary_empty(self) -> None:
        output = "No summary here"
        assert _extract_dod_summary(output) == ""

    def test_extract_suggestions(self) -> None:
        output = (
            "**Suggestions**:\n"
            "- Add unit tests for edge cases\n"
            "- Include error handling\n"
            "\n## Next Section"
        )
        suggestions = _extract_dod_suggestions(output)
        assert len(suggestions) == 2
        assert suggestions[0] == "Add unit tests for edge cases"
        assert suggestions[1] == "Include error handling"

    def test_extract_suggestions_empty(self) -> None:
        output = "No suggestions section"
        assert _extract_dod_suggestions(output) == []

    def test_extract_suggestions_stops_at_heading(self) -> None:
        output = (
            "**Suggestions** (if WARN or FAIL):\n"
            "- Fix the test\n"
            "## Another Section\n"
            "- Not a suggestion"
        )
        suggestions = _extract_dod_suggestions(output)
        assert len(suggestions) == 1
        assert suggestions[0] == "Fix the test"


class TestDoDGateCLI:
    """Test DoD gate CLI integration."""

    def test_registered_in_agents(self) -> None:
        assert "dod-gate" in AGENTS
        assert AGENTS["dod-gate"] is DOD_GATE

    def test_dod_flag_exists(self) -> None:
        parser = build_parser()
        # Parse with --dod flag for a known agent
        args = parser.parse_args(["--dod", "pr-reviewer", "--pr", "42"])
        assert args.dod is True

    def test_dod_flag_default_false(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["pr-reviewer", "--pr", "42"])
        assert args.dod is False

    def test_lessons_subcommand_exists(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["lessons", "list"])
        assert args.agent == "lessons"
        assert args.lessons_action == "list"

    def test_lessons_add_args(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "lessons",
                "add",
                "--agent",
                "pr-reviewer",
                "--failure-mode",
                "timeout",
                "--detection-signal",
                "exceeded 60s",
                "--prevention-rule",
                "set shorter timeout",
            ]
        )
        assert args.agent == "pr-reviewer"
        assert args.failure_mode == "timeout"

    def test_lessons_resolve_args(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "lessons",
                "resolve",
                "abc123",
                "--note",
                "fixed",
            ]
        )
        assert args.lesson_id == "abc123"
        assert args.note == "fixed"
