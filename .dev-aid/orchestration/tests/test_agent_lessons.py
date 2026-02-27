"""Tests for the lessons ledger (failure pattern tracking)."""

from pathlib import Path
from typing import Generator

import pytest
from agents.core.lessons import Lesson, LessonsConfig, LessonsLedger


@pytest.fixture
def tmp_ledger(tmp_path: Path) -> Generator[LessonsLedger, None, None]:
    """Create a temporary lessons ledger."""
    ledger_path = tmp_path / "test-ledger.md"
    config = LessonsConfig(ledger_path=ledger_path)
    yield LessonsLedger(config)


class TestLesson:
    """Tests for Lesson dataclass."""

    def test_create(self) -> None:
        lesson = Lesson(
            id="L001",
            timestamp="2025-01-01T00:00:00Z",
            agent_name="pr-reviewer",
            failure_mode="missed_xss",
            detection_signal="No XSS check in form handler",
            prevention_rule="Always check for innerHTML usage",
            source="dod-gate",
        )
        assert lesson.id == "L001"
        assert lesson.timestamp == "2025-01-01T00:00:00Z"
        assert not lesson.resolved
        assert lesson.resolution_note == ""

    def test_defaults(self) -> None:
        lesson = Lesson(
            id="L002",
            timestamp="2025-01-01T00:00:00Z",
            agent_name="test",
            failure_mode="test",
            detection_signal="test",
            prevention_rule="test",
        )
        assert lesson.source == "auto"
        assert not lesson.resolved
        assert lesson.metadata == {}

    def test_invalid_source(self) -> None:
        with pytest.raises(ValueError, match="Invalid source"):
            Lesson(
                id="L003",
                timestamp="2025-01-01T00:00:00Z",
                agent_name="test",
                failure_mode="test",
                detection_signal="test",
                prevention_rule="test",
                source="invalid",
            )

    def test_valid_sources(self) -> None:
        for source in ("auto", "manual", "dod-gate"):
            lesson = Lesson(
                id="L004",
                timestamp="2025-01-01T00:00:00Z",
                agent_name="test",
                failure_mode="test",
                detection_signal="test",
                prevention_rule="test",
                source=source,
            )
            assert lesson.source == source


class TestLessonsConfig:
    """Tests for LessonsConfig."""

    def test_defaults(self) -> None:
        config = LessonsConfig()
        assert config.max_lessons_in_prompt == 10
        assert config.auto_record_on_failure is True

    def test_custom(self, tmp_path: Path) -> None:
        config = LessonsConfig(
            ledger_path=tmp_path / "custom.md",
            max_lessons_in_prompt=5,
        )
        assert config.max_lessons_in_prompt == 5


class TestLessonsLedger:
    """Tests for LessonsLedger operations."""

    def test_add_lesson(self, tmp_ledger: LessonsLedger) -> None:
        lesson = tmp_ledger.add_lesson(
            agent_name="pr-reviewer",
            failure_mode="missed_sql_injection",
            detection_signal="Raw SQL concatenation in query",
            prevention_rule="Check for parameterized queries",
            source="dod-gate",
        )
        assert lesson.id != ""
        assert lesson.agent_name == "pr-reviewer"
        assert lesson.timestamp != ""

    def test_get_lessons(self, tmp_ledger: LessonsLedger) -> None:
        tmp_ledger.add_lesson(
            agent_name="a1",
            failure_mode="f1",
            detection_signal="d1",
            prevention_rule="p1",
            source="manual",
        )
        tmp_ledger.add_lesson(
            agent_name="a2",
            failure_mode="f2",
            detection_signal="d2",
            prevention_rule="p2",
            source="auto",
        )
        lessons = tmp_ledger.get_lessons()
        assert len(lessons) == 2

    def test_get_lessons_filters_resolved(self, tmp_ledger: LessonsLedger) -> None:
        lesson = tmp_ledger.add_lesson(
            agent_name="a1",
            failure_mode="f1",
            detection_signal="d1",
            prevention_rule="p1",
            source="manual",
        )
        tmp_ledger.mark_resolved(lesson.id, "Fixed now")

        active = tmp_ledger.get_lessons(include_resolved=False)
        all_lessons = tmp_ledger.get_lessons(include_resolved=True)
        assert len(active) == 0
        assert len(all_lessons) == 1

    def test_get_lessons_for_agent(self, tmp_ledger: LessonsLedger) -> None:
        tmp_ledger.add_lesson(
            agent_name="pr-reviewer",
            failure_mode="f1",
            detection_signal="d1",
            prevention_rule="p1",
        )
        tmp_ledger.add_lesson(
            agent_name="ci-fixer",
            failure_mode="f2",
            detection_signal="d2",
            prevention_rule="p2",
        )
        pr_lessons = tmp_ledger.get_lessons_for_agent("pr-reviewer")
        assert len(pr_lessons) == 1
        assert pr_lessons[0].agent_name == "pr-reviewer"

    def test_mark_resolved(self, tmp_ledger: LessonsLedger) -> None:
        lesson = tmp_ledger.add_lesson(
            agent_name="test",
            failure_mode="test_fail",
            detection_signal="signal",
            prevention_rule="rule",
            source="manual",
        )
        result = tmp_ledger.mark_resolved(lesson.id, "Issue no longer relevant")
        assert result is True

        lessons = tmp_ledger.get_lessons(include_resolved=True)
        resolved = [entry for entry in lessons if entry.resolved]
        assert len(resolved) == 1
        assert resolved[0].resolution_note == "Issue no longer relevant"

    def test_mark_resolved_nonexistent(self, tmp_ledger: LessonsLedger) -> None:
        result = tmp_ledger.mark_resolved("NONEXISTENT", "note")
        assert result is False

    def test_clear_resolved(self, tmp_ledger: LessonsLedger) -> None:
        l1 = tmp_ledger.add_lesson(
            agent_name="a",
            failure_mode="f",
            detection_signal="d",
            prevention_rule="p",
            source="manual",
        )
        tmp_ledger.add_lesson(
            agent_name="b",
            failure_mode="f",
            detection_signal="d",
            prevention_rule="p",
            source="manual",
        )
        tmp_ledger.mark_resolved(l1.id, "done")

        removed = tmp_ledger.clear_resolved()
        assert removed == 1

        remaining = tmp_ledger.get_lessons(include_resolved=True)
        assert len(remaining) == 1
        assert remaining[0].agent_name == "b"

    def test_format_for_prompt(self, tmp_ledger: LessonsLedger) -> None:
        tmp_ledger.add_lesson(
            agent_name="pr-reviewer",
            failure_mode="missed_auth_check",
            detection_signal="No authorization in endpoint",
            prevention_rule="Verify authorization decorators on all routes",
            source="dod-gate",
        )
        prompt = tmp_ledger.format_for_prompt("pr-reviewer")
        assert "missed_auth_check" in prompt
        assert "authorization" in prompt.lower()

    def test_format_for_prompt_empty(self, tmp_ledger: LessonsLedger) -> None:
        prompt = tmp_ledger.format_for_prompt("nonexistent-agent")
        assert prompt == ""

    def test_format_for_prompt_all_agents(self, tmp_ledger: LessonsLedger) -> None:
        tmp_ledger.add_lesson(
            agent_name="a1",
            failure_mode="f1",
            detection_signal="d1",
            prevention_rule="p1",
        )
        prompt = tmp_ledger.format_for_prompt()
        assert "f1" in prompt

    def test_persistence(self, tmp_path: Path) -> None:
        """Lessons persist across ledger instances."""
        ledger_path = tmp_path / "persist-test.md"
        config = LessonsConfig(ledger_path=ledger_path)

        # Write with first instance
        ledger1 = LessonsLedger(config)
        ledger1.add_lesson(
            agent_name="test",
            failure_mode="persist_test",
            detection_signal="signal",
            prevention_rule="rule",
            source="manual",
        )

        # Read with second instance
        ledger2 = LessonsLedger(config)
        lessons = ledger2.get_lessons()
        assert len(lessons) == 1
        assert lessons[0].failure_mode == "persist_test"

    def test_add_lesson_with_metadata(self, tmp_ledger: LessonsLedger) -> None:
        lesson = tmp_ledger.add_lesson(
            agent_name="test",
            failure_mode="f",
            detection_signal="d",
            prevention_rule="p",
            metadata={"severity": "high", "count": 3},
        )
        assert lesson.metadata["severity"] == "high"
