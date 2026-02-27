"""Tests for the Lessons Ledger module."""

from pathlib import Path
from typing import List

import pytest
from agents.core.lessons import (
    Lesson,
    LessonsConfig,
    LessonsLedger,
    _parse_lessons_markdown,
    _render_lessons_markdown,
    get_lessons_context,
)


class TestLessonDataclass:
    """Test the Lesson dataclass."""

    def test_create_lesson(self) -> None:
        lesson = Lesson(
            id="abcdef01",
            timestamp="2026-01-15T10:00:00Z",
            agent_name="pr-reviewer",
            failure_mode="provider_error",
            detection_signal="API key expired",
            prevention_rule="Validate API key before run",
        )
        assert lesson.id == "abcdef01"
        assert lesson.agent_name == "pr-reviewer"
        assert lesson.failure_mode == "provider_error"
        assert lesson.resolved is False
        assert lesson.source == "auto"
        assert lesson.metadata == {}

    def test_defaults(self) -> None:
        lesson = Lesson(
            id="00000000",
            timestamp="2026-01-01T00:00:00Z",
            agent_name="test",
            failure_mode="test",
            detection_signal="test",
            prevention_rule="test",
        )
        assert lesson.resolved is False
        assert lesson.resolution_note == ""
        assert lesson.source == "auto"
        assert lesson.metadata == {}

    def test_valid_sources(self) -> None:
        for source in ("auto", "manual", "dod-gate"):
            lesson = Lesson(
                id="00000000",
                timestamp="2026-01-01T00:00:00Z",
                agent_name="test",
                failure_mode="test",
                detection_signal="test",
                prevention_rule="test",
                source=source,
            )
            assert lesson.source == source

    def test_invalid_source_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid source"):
            Lesson(
                id="00000000",
                timestamp="2026-01-01T00:00:00Z",
                agent_name="test",
                failure_mode="test",
                detection_signal="test",
                prevention_rule="test",
                source="invalid",
            )


class TestLessonsConfig:
    """Test the LessonsConfig dataclass."""

    def test_defaults(self) -> None:
        config = LessonsConfig()
        assert config.ledger_path == Path(".dev-aid/memory-bank/lessons-ledger.md")
        assert config.max_lessons_in_prompt == 10
        assert config.auto_record_on_failure is True

    def test_custom_path(self, tmp_path: Path) -> None:
        config = LessonsConfig(
            ledger_path=tmp_path / "custom-ledger.md",
            max_lessons_in_prompt=5,
            auto_record_on_failure=False,
        )
        assert config.ledger_path == tmp_path / "custom-ledger.md"
        assert config.max_lessons_in_prompt == 5
        assert config.auto_record_on_failure is False


class TestLessonsLedger:
    """Test the LessonsLedger class."""

    def _make_ledger(self, tmp_path: Path) -> LessonsLedger:
        config = LessonsConfig(ledger_path=tmp_path / "ledger.md")
        return LessonsLedger(config)

    def test_add_lesson(self, tmp_path: Path) -> None:
        ledger = self._make_ledger(tmp_path)
        lesson = ledger.add_lesson(
            agent_name="pr-reviewer",
            failure_mode="timeout",
            detection_signal="exceeded 60s",
            prevention_rule="set shorter timeout",
        )
        assert lesson.agent_name == "pr-reviewer"
        assert lesson.failure_mode == "timeout"
        assert len(lesson.id) == 8
        assert lesson.source == "auto"

    def test_get_lessons_empty(self, tmp_path: Path) -> None:
        ledger = self._make_ledger(tmp_path)
        assert ledger.get_lessons() == []

    def test_get_lessons_excludes_resolved(self, tmp_path: Path) -> None:
        ledger = self._make_ledger(tmp_path)
        lesson = ledger.add_lesson(
            agent_name="test",
            failure_mode="fail",
            detection_signal="signal",
            prevention_rule="rule",
        )
        ledger.mark_resolved(lesson.id)
        assert ledger.get_lessons(include_resolved=False) == []
        assert len(ledger.get_lessons(include_resolved=True)) == 1

    def test_get_lessons_for_agent(self, tmp_path: Path) -> None:
        ledger = self._make_ledger(tmp_path)
        ledger.add_lesson(
            agent_name="pr-reviewer",
            failure_mode="fail1",
            detection_signal="s1",
            prevention_rule="r1",
        )
        ledger.add_lesson(
            agent_name="ci-fixer",
            failure_mode="fail2",
            detection_signal="s2",
            prevention_rule="r2",
        )
        pr_lessons = ledger.get_lessons_for_agent("pr-reviewer")
        assert len(pr_lessons) == 1
        assert pr_lessons[0].agent_name == "pr-reviewer"

    def test_get_lessons_for_agent_includes_wildcard(self, tmp_path: Path) -> None:
        ledger = self._make_ledger(tmp_path)
        ledger.add_lesson(
            agent_name="*",
            failure_mode="global-fail",
            detection_signal="everywhere",
            prevention_rule="always check",
        )
        result = ledger.get_lessons_for_agent("any-agent")
        assert len(result) == 1
        assert result[0].agent_name == "*"

    def test_mark_resolved(self, tmp_path: Path) -> None:
        ledger = self._make_ledger(tmp_path)
        lesson = ledger.add_lesson(
            agent_name="test",
            failure_mode="fail",
            detection_signal="signal",
            prevention_rule="rule",
        )
        assert ledger.mark_resolved(lesson.id, "fixed it") is True
        lessons = ledger.get_lessons(include_resolved=True)
        assert lessons[0].resolved is True
        assert lessons[0].resolution_note == "fixed it"

    def test_mark_resolved_not_found(self, tmp_path: Path) -> None:
        ledger = self._make_ledger(tmp_path)
        assert ledger.mark_resolved("nonexistent") is False

    def test_clear_resolved(self, tmp_path: Path) -> None:
        ledger = self._make_ledger(tmp_path)
        l1 = ledger.add_lesson(
            agent_name="a",
            failure_mode="f",
            detection_signal="s",
            prevention_rule="r",
        )
        ledger.add_lesson(
            agent_name="b",
            failure_mode="f",
            detection_signal="s",
            prevention_rule="r",
        )
        ledger.mark_resolved(l1.id)
        removed = ledger.clear_resolved()
        assert removed == 1
        assert len(ledger.get_lessons(include_resolved=True)) == 1

    def test_format_for_prompt_empty(self, tmp_path: Path) -> None:
        ledger = self._make_ledger(tmp_path)
        assert ledger.format_for_prompt() == ""

    def test_format_for_prompt_content(self, tmp_path: Path) -> None:
        ledger = self._make_ledger(tmp_path)
        ledger.add_lesson(
            agent_name="pr-reviewer",
            failure_mode="timeout",
            detection_signal="exceeded 60s",
            prevention_rule="set shorter timeout",
        )
        result = ledger.format_for_prompt("pr-reviewer")
        assert "Lessons from Past Failures" in result
        assert "timeout" in result
        assert "set shorter timeout" in result

    def test_format_for_prompt_bounded(self, tmp_path: Path) -> None:
        config = LessonsConfig(
            ledger_path=tmp_path / "ledger.md",
            max_lessons_in_prompt=2,
        )
        ledger = LessonsLedger(config)
        for i in range(5):
            ledger.add_lesson(
                agent_name="test",
                failure_mode=f"fail-{i}",
                detection_signal=f"signal-{i}",
                prevention_rule=f"rule-{i}",
            )
        result = ledger.format_for_prompt("test")
        # Should only contain the last 2 lessons
        assert "fail-3" in result
        assert "fail-4" in result
        assert "fail-0" not in result

    def test_persistence_roundtrip(self, tmp_path: Path) -> None:
        """Verify lessons survive save/load cycle."""
        config = LessonsConfig(ledger_path=tmp_path / "ledger.md")
        ledger1 = LessonsLedger(config)
        ledger1.add_lesson(
            agent_name="agent-a",
            failure_mode="crash",
            detection_signal="segfault",
            prevention_rule="check memory bounds",
            source="manual",
        )
        # Create new ledger from same file
        ledger2 = LessonsLedger(config)
        lessons = ledger2.get_lessons()
        assert len(lessons) == 1
        assert lessons[0].agent_name == "agent-a"
        assert lessons[0].failure_mode == "crash"
        assert lessons[0].source == "manual"


class TestMarkdownIO:
    """Test the markdown parsing and rendering functions."""

    def test_roundtrip(self) -> None:
        lessons: List[Lesson] = [
            Lesson(
                id="aabbccdd",
                timestamp="2026-01-15T10:00:00Z",
                agent_name="pr-reviewer",
                failure_mode="timeout",
                detection_signal="exceeded 60s",
                prevention_rule="set shorter timeout",
                source="auto",
            ),
            Lesson(
                id="11223344",
                timestamp="2026-01-16T12:00:00Z",
                agent_name="ci-fixer",
                failure_mode="wrong branch",
                detection_signal="branch not found",
                prevention_rule="verify branch exists",
                resolved=True,
                resolution_note="fixed branch name",
                source="manual",
            ),
        ]
        markdown = _render_lessons_markdown(lessons)
        parsed = _parse_lessons_markdown(markdown)
        assert len(parsed) == 2
        assert parsed[0].id == "aabbccdd"
        assert parsed[0].agent_name == "pr-reviewer"
        assert parsed[1].id == "11223344"
        assert parsed[1].resolved is True
        assert parsed[1].resolution_note == "fixed branch name"

    def test_parse_empty(self) -> None:
        assert _parse_lessons_markdown("") == []

    def test_parse_malformed_skipped(self) -> None:
        content = "### LESSON-badheader this is not valid\n- something\n"
        result = _parse_lessons_markdown(content)
        assert result == []


class TestGetLessonsContext:
    """Test the convenience helper function."""

    def test_no_file(self, tmp_path: Path) -> None:
        result = get_lessons_context(tmp_path / "nonexistent.md")
        assert result == ""

    def test_with_lessons(self, tmp_path: Path) -> None:
        ledger_path = tmp_path / "ledger.md"
        config = LessonsConfig(ledger_path=ledger_path)
        ledger = LessonsLedger(config)
        ledger.add_lesson(
            agent_name="test",
            failure_mode="fail",
            detection_signal="sig",
            prevention_rule="rule",
        )
        result = get_lessons_context(ledger_path, "test")
        assert "Lessons from Past Failures" in result
