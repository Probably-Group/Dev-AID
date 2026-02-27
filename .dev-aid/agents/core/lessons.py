"""
Lessons Ledger — structured capture of agent failure patterns.

Records failure patterns as lessons in a markdown file, then injects
relevant lessons into future agent prompts so agents avoid repeating mistakes.
"""

import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Lesson:
    """A single recorded lesson from an agent failure."""

    id: str
    timestamp: str
    agent_name: str
    failure_mode: str
    detection_signal: str
    prevention_rule: str
    resolved: bool = False
    resolution_note: str = ""
    source: str = "auto"  # "auto", "manual", "dod-gate"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        valid_sources = {"auto", "manual", "dod-gate"}
        if self.source not in valid_sources:
            raise ValueError(
                f"Invalid source '{self.source}'. Must be one of: {valid_sources}"
            )


@dataclass
class LessonsConfig:
    """Configuration for the lessons ledger."""

    ledger_path: Path = field(
        default_factory=lambda: Path(".dev-aid/memory-bank/lessons-ledger.md")
    )
    max_lessons_in_prompt: int = 10
    auto_record_on_failure: bool = True


def _generate_lesson_id() -> str:
    """Generate a unique 8-hex-char lesson ID."""
    return uuid.uuid4().hex[:8]


def _now_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class LessonsLedger:
    """Manages a ledger of agent failure lessons stored in markdown."""

    def __init__(self, config: Optional[LessonsConfig] = None) -> None:
        self._config = config or LessonsConfig()
        self._lessons: List[Lesson] = []
        self._load()

    @property
    def config(self) -> LessonsConfig:
        """Return the current config."""
        return self._config

    def _load(self) -> None:
        """Load lessons from the markdown ledger file."""
        path = self._config.ledger_path
        if not path.is_file():
            self._lessons = []
            return

        try:
            content = path.read_text(encoding="utf-8")
        except OSError as e:
            logger.warning("Failed to read lessons ledger: %s", e)
            self._lessons = []
            return

        self._lessons = _parse_lessons_markdown(content)

    def _save(self) -> None:
        """Persist lessons to the markdown ledger file."""
        path = self._config.ledger_path
        path.parent.mkdir(parents=True, exist_ok=True)

        content = _render_lessons_markdown(self._lessons)
        try:
            path.write_text(content, encoding="utf-8")
        except OSError as e:
            logger.error("Failed to write lessons ledger: %s", e)

    def add_lesson(
        self,
        agent_name: str,
        failure_mode: str,
        detection_signal: str,
        prevention_rule: str,
        source: str = "auto",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Lesson:
        """Record a new lesson and persist it."""
        lesson = Lesson(
            id=_generate_lesson_id(),
            timestamp=_now_iso(),
            agent_name=agent_name,
            failure_mode=failure_mode,
            detection_signal=detection_signal,
            prevention_rule=prevention_rule,
            source=source,
            metadata=metadata or {},
        )
        self._lessons.append(lesson)
        self._save()
        logger.info("Recorded lesson %s for agent '%s'", lesson.id, agent_name)
        return lesson

    def get_lessons(self, include_resolved: bool = False) -> List[Lesson]:
        """Return all lessons, optionally including resolved ones."""
        if include_resolved:
            return list(self._lessons)
        return [entry for entry in self._lessons if not entry.resolved]

    def get_lessons_for_agent(
        self, agent_name: str, include_resolved: bool = False
    ) -> List[Lesson]:
        """Return lessons relevant to a specific agent."""
        return [
            entry
            for entry in self.get_lessons(include_resolved=include_resolved)
            if entry.agent_name == agent_name or entry.agent_name == "*"
        ]

    def mark_resolved(self, lesson_id: str, resolution_note: str = "") -> bool:
        """Mark a lesson as resolved. Returns True if found."""
        for lesson in self._lessons:
            if lesson.id == lesson_id:
                lesson.resolved = True
                lesson.resolution_note = resolution_note
                self._save()
                return True
        return False

    def clear_resolved(self) -> int:
        """Remove all resolved lessons. Returns count removed."""
        before = len(self._lessons)
        self._lessons = [entry for entry in self._lessons if not entry.resolved]
        removed = before - len(self._lessons)
        if removed > 0:
            self._save()
        return removed

    def format_for_prompt(self, agent_name: Optional[str] = None) -> str:
        """Format lessons for injection into an agent's system prompt.

        Returns empty string if no relevant lessons exist.
        Bounded by max_lessons_in_prompt from config.
        """
        if agent_name:
            lessons = self.get_lessons_for_agent(agent_name)
        else:
            lessons = self.get_lessons()

        if not lessons:
            return ""

        # Limit to most recent N lessons
        bounded = lessons[-self._config.max_lessons_in_prompt :]

        lines = [
            "## Lessons from Past Failures",
            "",
            "The following lessons were recorded from previous runs. "
            "Apply these prevention rules to avoid repeating the same mistakes.",
            "",
        ]
        for lesson in bounded:
            lines.append(f"- **{lesson.failure_mode}**: {lesson.prevention_rule}")
            if lesson.detection_signal:
                lines.append(f"  - Detection signal: {lesson.detection_signal}")

        return "\n".join(lines)


def get_lessons_context(
    ledger_path: Path,
    agent_name: Optional[str] = None,
) -> str:
    """Convenience helper to get lessons prompt context without full config.

    Returns empty string if no lessons or ledger file doesn't exist.
    """
    config = LessonsConfig(ledger_path=ledger_path)
    ledger = LessonsLedger(config)
    return ledger.format_for_prompt(agent_name)


# ── Markdown I/O ────────────────────────────────────────────────────


_LESSON_HEADER_RE = re.compile(r"^### LESSON-([0-9a-f]{8}) \| (.+?) \| (\S+)$")


def _parse_lessons_markdown(content: str) -> List[Lesson]:
    """Parse lessons from the markdown ledger format.

    Splits on `### LESSON-` boundaries, extracts fields via line matching.
    Gracefully skips malformed entries.
    """
    lessons: List[Lesson] = []

    # Split into sections at ### LESSON- boundaries
    sections = re.split(r"(?=^### LESSON-)", content, flags=re.MULTILINE)

    for section in sections:
        section = section.strip()
        if not section.startswith("### LESSON-"):
            continue

        lines = section.split("\n")
        header_match = _LESSON_HEADER_RE.match(lines[0])
        if not header_match:
            logger.debug("Skipping malformed lesson header: %s", lines[0])
            continue

        lesson_id = header_match.group(1)
        agent_name = header_match.group(2)
        timestamp = header_match.group(3)

        # Extract fields from body lines
        fields: Dict[str, str] = {}
        for line in lines[1:]:
            line = line.strip()
            if line.startswith("- **") and "**:" in line:
                # e.g. "- **Failure Mode**: some text"
                key_end = line.index("**:", 4)
                key = line[4:key_end]
                value = line[key_end + 3 :].strip()
                fields[key] = value

        failure_mode = fields.get("Failure Mode", "")
        detection_signal = fields.get("Detection Signal", "")
        prevention_rule = fields.get("Prevention Rule", "")
        resolved_str = fields.get("Resolved", "false")
        resolved = resolved_str.lower() == "true"
        source = fields.get("Source", "auto")
        resolution_note = fields.get("Resolution Note", "")

        # Validate source
        if source not in {"auto", "manual", "dod-gate"}:
            source = "auto"

        try:
            lesson = Lesson(
                id=lesson_id,
                timestamp=timestamp,
                agent_name=agent_name,
                failure_mode=failure_mode,
                detection_signal=detection_signal,
                prevention_rule=prevention_rule,
                resolved=resolved,
                resolution_note=resolution_note,
                source=source,
            )
            lessons.append(lesson)
        except (ValueError, TypeError) as e:
            logger.debug("Skipping invalid lesson %s: %s", lesson_id, e)

    return lessons


def _render_lessons_markdown(lessons: List[Lesson]) -> str:
    """Render lessons to the markdown ledger format."""
    lines = [
        "# Lessons Ledger",
        "",
        "Auto-generated file tracking agent failure patterns and prevention rules.",
        "",
    ]

    for lesson in lessons:
        lines.append(
            f"### LESSON-{lesson.id} | {lesson.agent_name} | {lesson.timestamp}"
        )
        lines.append(f"- **Failure Mode**: {lesson.failure_mode}")
        lines.append(f"- **Detection Signal**: {lesson.detection_signal}")
        lines.append(f"- **Prevention Rule**: {lesson.prevention_rule}")
        lines.append(f"- **Resolved**: {str(lesson.resolved).lower()}")
        lines.append(f"- **Source**: {lesson.source}")
        if lesson.resolution_note:
            lines.append(f"- **Resolution Note**: {lesson.resolution_note}")
        lines.append("")

    return "\n".join(lines)
