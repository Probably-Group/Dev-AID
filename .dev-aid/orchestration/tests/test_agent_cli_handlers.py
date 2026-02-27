"""Tests for CLI subcommand handlers (team, APO, lessons, DoD gate)."""

from agents.cli import (
    _build_user_message,
    _extract_dod_suggestions,
    _extract_dod_summary,
    _parse_dod_verdict,
    build_parser,
)


class TestDoDGateParsing:
    """Tests for DoD gate output parsing."""

    def test_parse_verdict_pass(self) -> None:
        output = "## Results\n\n**Overall Verdict**: PASS\n\nAll checks passed."
        assert _parse_dod_verdict(output) == "PASS"

    def test_parse_verdict_fail(self) -> None:
        output = "**Overall Verdict**: FAIL\n\nMissing artifacts."
        assert _parse_dod_verdict(output) == "FAIL"

    def test_parse_verdict_warn(self) -> None:
        output = "**Overall Verdict**: WARN\n\nPartial completion."
        assert _parse_dod_verdict(output) == "WARN"

    def test_parse_verdict_unknown(self) -> None:
        output = "No verdict here."
        assert _parse_dod_verdict(output) == "UNKNOWN"

    def test_parse_verdict_case_insensitive(self) -> None:
        output = "**Overall Verdict**: pass"
        assert _parse_dod_verdict(output) == "PASS"

    def test_extract_summary(self) -> None:
        output = "**Summary**: All requirements met with good test coverage.\n\n## Details"
        summary = _extract_dod_summary(output)
        assert "requirements met" in summary

    def test_extract_summary_empty(self) -> None:
        output = "No summary here."
        assert _extract_dod_summary(output) == ""

    def test_extract_suggestions(self) -> None:
        output = (
            "## Review\n\n"
            "**Suggestions**\n"
            "- Add integration tests\n"
            "- Check error handling\n"
            "- Update documentation\n"
            "\n## End"
        )
        suggestions = _extract_dod_suggestions(output)
        assert len(suggestions) == 3
        assert "Add integration tests" in suggestions[0]

    def test_extract_suggestions_none(self) -> None:
        output = "No suggestions section."
        assert _extract_dod_suggestions(output) == []


class TestBuildUserMessage:
    """Tests for user message construction from CLI args."""

    def test_tech_debt_default_path(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["tech-debt-hunter", "--severity", "high"])
        msg = _build_user_message("tech-debt-hunter", args)
        assert "high" in msg
        assert "project" in msg.lower()

    def test_tech_debt_custom_path(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["tech-debt-hunter", "--severity", "medium", "--path", "src/auth/"]
        )
        msg = _build_user_message("tech-debt-hunter", args)
        assert "src/auth/" in msg

    def test_ci_fixer_with_run_id(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["ci-fixer", "--run-id", "12345"])
        msg = _build_user_message("ci-fixer", args)
        assert "12345" in msg

    def test_ci_fixer_with_pr(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["ci-fixer", "--pr", "42"])
        msg = _build_user_message("ci-fixer", args)
        assert "#42" in msg

    def test_conflict_resolver_default(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["conflict-resolver"])
        msg = _build_user_message("conflict-resolver", args)
        assert "smart" in msg
        assert "conflict" in msg.lower()

    def test_conflict_resolver_with_pr(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["conflict-resolver", "--pr", "99", "--strategy", "theirs"])
        msg = _build_user_message("conflict-resolver", args)
        assert "#99" in msg
        assert "theirs" in msg

    def test_doc_auditor_custom_scope(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["doc-auditor", "--path", "docs/", "--scope", "docs-only"])
        msg = _build_user_message("doc-auditor", args)
        assert "docs/" in msg
        assert "docs-only" in msg

    def test_onboarding_message(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["onboarding"])
        msg = _build_user_message("onboarding", args)
        assert "onboarding" in msg.lower()

    def test_unknown_agent_fallback(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["onboarding"])
        msg = _build_user_message("unknown-agent", args)
        assert msg != ""  # Should return fallback message


class TestTeamParser:
    """Tests for team subcommand argument parsing."""

    def test_parse_team_basic(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["team", "pr-review-team", "-m", "Review auth code"])
        assert args.agent == "team"
        assert args.team_name == "pr-review-team"
        assert args.message == "Review auth code"

    def test_parse_team_list(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["team", "--list-teams"])
        assert args.list_teams is True

    def test_parse_team_overrides(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "team",
                "security-audit-team",
                "-m",
                "Audit",
                "--budget",
                "5.0",
                "--workflow",
                "sequential",
            ]
        )
        assert args.budget == 5.0
        assert args.workflow == "sequential"


class TestAPOParser:
    """Tests for APO subcommand argument parsing."""

    def test_parse_apo_optimize(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["apo", "optimize", "pr-reviewer", "--beam-width", "5"])
        assert args.agent == "apo"
        assert args.apo_action == "optimize"
        assert args.agent_name == "pr-reviewer"
        assert args.beam_width == 5

    def test_parse_apo_rollback(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["apo", "rollback", "test-generator", "--version", "3"])
        assert args.apo_action == "rollback"
        assert args.agent_name == "test-generator"
        assert args.version == 3

    def test_parse_apo_history(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["apo", "history", "ci-fixer"])
        assert args.apo_action == "history"
        assert args.agent_name == "ci-fixer"

    def test_parse_apo_status(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["apo", "status"])
        assert args.apo_action == "status"


class TestLessonsParser:
    """Tests for lessons subcommand argument parsing."""

    def test_parse_lessons_list(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["lessons", "list"])
        assert args.agent == "lessons"
        assert args.lessons_action == "list"

    def test_parse_lessons_add(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            [
                "lessons",
                "add",
                "--agent",
                "pr-reviewer",
                "--failure-mode",
                "missed_xss",
                "--detection-signal",
                "innerHTML usage",
                "--prevention-rule",
                "Always check for XSS",
            ]
        )
        assert args.lessons_action == "add"
        assert args.agent == "pr-reviewer"
        assert args.failure_mode == "missed_xss"

    def test_parse_lessons_resolve(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["lessons", "resolve", "L001", "--note", "Fixed in v2.0"])
        assert args.lessons_action == "resolve"
        assert args.lesson_id == "L001"
        assert args.note == "Fixed in v2.0"

    def test_parse_lessons_clear_resolved(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["lessons", "clear-resolved"])
        assert args.lessons_action == "clear-resolved"


class TestGlobalOptions:
    """Tests for global CLI options applied to agents."""

    def test_trace_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--trace", "pr-reviewer", "--pr", "42"])
        assert args.trace is True

    def test_trace_dir(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["--trace", "--trace-dir", "/tmp/traces", "pr-reviewer", "--pr", "1"]
        )
        assert args.trace_dir == "/tmp/traces"

    def test_dod_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--dod", "pr-reviewer", "--pr", "42"])
        assert args.dod is True

    def test_json_output(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--json", "onboarding"])
        assert args.json_output is True

    def test_dry_run(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--dry-run", "research", "--topic", "async"])
        assert args.dry_run is True
