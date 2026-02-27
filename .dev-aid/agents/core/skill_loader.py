"""
SKILL.md parser and system prompt builder.

Loads Dev-AID skills from SKILL.md files, extracts YAML frontmatter
metadata and markdown body, and builds combined system prompts.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Shared preamble injected once at the top of combined system prompts,
# instead of repeating Section 0.1/0.3 in every SKILL.md file.
SHARED_PREAMBLE = (
    "Before generating code or guidance: verify patterns exist in official docs, "
    "check version compatibility, never invent method names or parameters. "
    "If unsure, state uncertainty explicitly.\n\n"
    "For HIGH/CRITICAL risk skills: test all generated code before presenting, "
    "include error handling for edge cases, validate security implications."
)

# Try to use PyYAML for robust parsing, fall back to custom parser
try:
    import yaml as _yaml  # type: ignore[import-untyped]

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# Regex for YAML frontmatter delimited by ---
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Simple YAML key-value parser (fallback when PyYAML unavailable)
_YAML_KV_RE = re.compile(r"^(\w[\w_-]*)\s*:\s*(.+)$", re.MULTILINE)


@dataclass
class SkillMetadata:
    """Parsed metadata from SKILL.md frontmatter."""

    name: str
    version: str = "1.0.0"
    description: str = ""
    risk_level: str = "LOW"
    category: Optional[str] = None
    auto_load: bool = False
    token_budget: Optional[int] = None
    triggers: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadedSkill:
    """A fully loaded skill with metadata and prompt content."""

    metadata: SkillMetadata
    body: str  # Markdown content after frontmatter
    source_path: Path = field(default_factory=lambda: Path("."))
    sections: Dict[str, str] = field(default_factory=dict)


# Section priority for budget-aware loading (lower number = higher priority).
# Maps section heading patterns to priority tier.
SECTION_PRIORITY: List[tuple] = [
    (re.compile(r"^## 0"), 0),  # Anti-hallucination / security patterns
    (re.compile(r"^## 1"), 1),  # Principles
    (re.compile(r"^## 2"), 2),  # Version requirements
    (re.compile(r"^## 3"), 3),  # Code patterns
    (re.compile(r"^## 4"), 4),  # Anti-patterns
    (re.compile(r"^## 5"), 5),  # Testing
    (re.compile(r"^## 6"), 6),  # Checklists
]


def _parse_sections(body: str) -> Dict[str, str]:
    """Split skill body into sections keyed by ## header text."""
    sections: Dict[str, str] = {}
    current_header: Optional[str] = None
    current_lines: List[str] = []

    for line in body.split("\n"):
        if line.startswith("## "):
            # Flush previous section
            if current_header is not None:
                sections[current_header] = "\n".join(current_lines).strip()
            current_header = line.strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Flush last section
    if current_header is not None:
        sections[current_header] = "\n".join(current_lines).strip()

    return sections


def _section_priority(header: str) -> int:
    """Return the priority tier for a section header (lower = higher priority)."""
    for pattern, priority in SECTION_PRIORITY:
        if pattern.match(header):
            return priority
    return 99  # Unknown sections get lowest priority


def _parse_yaml_value(value: str) -> Any:
    """Parse a simple YAML value (string, bool, number, list)."""
    stripped = value.strip().strip('"').strip("'")

    # Boolean
    if stripped.lower() in ("true", "yes"):
        return True
    if stripped.lower() in ("false", "no"):
        return False

    # Integer
    try:
        return int(stripped)
    except ValueError:
        pass

    # Float
    try:
        return float(stripped)
    except ValueError:
        pass

    return stripped


def _parse_frontmatter(text: str) -> Dict[str, Any]:
    """Parse YAML frontmatter into a dictionary.

    Uses PyYAML if available, otherwise falls back to a simple
    key-value parser that handles basic frontmatter.
    """
    if _HAS_YAML:
        try:
            parsed = _yaml.safe_load(text)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            logger.debug("PyYAML failed, falling back to custom parser")

    result: Dict[str, Any] = {}
    current_list_key: Optional[str] = None
    current_list: List[str] = []

    for line in text.split("\n"):
        stripped = line.strip()

        # List continuation (indented "- item")
        if stripped.startswith("- ") and current_list_key is not None:
            current_list.append(stripped[2:].strip())
            continue

        # Flush previous list
        if current_list_key is not None:
            result[current_list_key] = current_list
            current_list_key = None
            current_list = []

        # Key-value pair or key-only (for list start)
        colon_idx = stripped.find(":")
        if colon_idx > 0:
            key = stripped[:colon_idx].strip()
            value = stripped[colon_idx + 1 :].strip()

            if not key.replace("_", "").replace("-", "").isalnum():
                continue

            # Check if this starts a list or is empty value
            if value == "" or value == "~" or value == "null":
                current_list_key = key
                current_list = []
            elif value == "[]":
                result[key] = []
            elif value.startswith("[") and value.endswith("]"):
                # Inline list: [a, b, c]
                items = value[1:-1].split(",")
                result[key] = [item.strip().strip('"').strip("'") for item in items if item.strip()]
            else:
                result[key] = _parse_yaml_value(value)

    # Flush final list
    if current_list_key is not None:
        result[current_list_key] = current_list

    return result


def parse_skill_file(path: Path) -> LoadedSkill:
    """Parse a SKILL.md file into metadata and body content."""
    content = path.read_text(encoding="utf-8")

    # Extract frontmatter
    fm_match = _FRONTMATTER_RE.match(content)
    if fm_match:
        raw_frontmatter = fm_match.group(1)
        body = content[fm_match.end() :].strip()
        raw = _parse_frontmatter(raw_frontmatter)
    else:
        raw = {}
        body = content.strip()

    metadata = SkillMetadata(
        name=raw.get("name", path.parent.name),
        version=str(raw.get("version", "1.0.0")),
        description=str(raw.get("description", "")),
        risk_level=str(raw.get("risk_level", "LOW")).upper(),
        category=raw.get("category"),
        auto_load=bool(raw.get("auto_load", False)),
        token_budget=raw.get("token_budget") if isinstance(raw.get("token_budget"), int) else None,
        triggers=raw.get("triggers", []) if isinstance(raw.get("triggers"), list) else [],
        tools=raw.get("tools", []) if isinstance(raw.get("tools"), list) else [],
        raw=raw,
    )

    sections = _parse_sections(body)

    return LoadedSkill(metadata=metadata, body=body, source_path=path, sections=sections)


class SkillLoader:
    """Discovers and loads SKILL.md files from Dev-AID skill directories."""

    def __init__(self, skills_root: Path) -> None:
        self.skills_root = skills_root
        self._cache: Dict[str, LoadedSkill] = {}

    def discover_skills(self) -> List[str]:
        """Discover all available skill names."""
        skills: List[str] = []
        for category_dir in sorted(self.skills_root.iterdir()):
            if not category_dir.is_dir():
                continue
            for skill_dir in sorted(category_dir.iterdir()):
                skill_file = skill_dir / "SKILL.md"
                if skill_file.is_file():
                    skills.append(skill_dir.name)
        return skills

    def load_skill(self, name: str) -> Optional[LoadedSkill]:
        """Load a single skill by name, with caching."""
        if name in self._cache:
            return self._cache[name]

        # Search across all category directories
        for category_dir in self.skills_root.iterdir():
            if not category_dir.is_dir():
                continue
            skill_file = category_dir / name / "SKILL.md"
            if skill_file.is_file():
                try:
                    skill = parse_skill_file(skill_file)
                    self._cache[name] = skill
                    return skill
                except Exception as e:
                    logger.error("Failed to load skill '%s': %s", name, e)
                    return None

        logger.warning("Skill '%s' not found in %s", name, self.skills_root)
        return None

    def load_skills(self, names: List[str]) -> List[LoadedSkill]:
        """Load multiple skills by name."""
        loaded: List[LoadedSkill] = []
        for name in names:
            skill = self.load_skill(name)
            if skill:
                loaded.append(skill)
        return loaded

    def build_system_prompt(self, skill_names: List[str]) -> str:
        """Build a combined system prompt from multiple skills.

        Injects the shared preamble once at the top, then appends
        each skill's unique body content.
        """
        skills = self.load_skills(skill_names)
        if not skills:
            return ""

        sections: List[str] = [SHARED_PREAMBLE]
        for skill in skills:
            header = f"## Skill: {skill.metadata.name}"
            if skill.metadata.description:
                header += f"\n*{skill.metadata.description}*"
            sections.append(f"{header}\n\n{skill.body}")

        return "\n\n---\n\n".join(sections)

    def build_system_prompt_with_budget(
        self,
        skill_names: List[str],
        max_tokens: int = 16000,
    ) -> str:
        """Build a system prompt that fits within a token budget.

        Loads sections in priority order (security > principles > code patterns
        > testing > checklists) until the budget is exhausted. The shared
        preamble is always included.

        Args:
            skill_names: Skill names to load.
            max_tokens: Maximum estimated token budget for the combined prompt.

        Returns:
            Combined system prompt within the budget.
        """
        skills = self.load_skills(skill_names)
        if not skills:
            return ""

        preamble_tokens = len(SHARED_PREAMBLE) // 4
        remaining = max_tokens - preamble_tokens

        # Collect all (priority, header, content, skill_name) tuples
        candidates: List[tuple] = []
        for skill in skills:
            # Title header is always included
            header_text = f"## Skill: {skill.metadata.name}"
            if skill.metadata.description:
                header_text += f"\n*{skill.metadata.description}*"

            # If skill has no parsed sections, include full body
            if not skill.sections:
                candidates.append((0, header_text, skill.body, skill.metadata.name))
                continue

            # Add title header as priority 0
            candidates.append((-1, header_text, "", skill.metadata.name))

            # Add each section with its priority
            for section_header, section_body in skill.sections.items():
                priority = _section_priority(section_header)
                full_section = f"{section_header}\n\n{section_body}"
                candidates.append(
                    (priority, section_header, full_section, skill.metadata.name)
                )

        # Sort by priority (headers first, then sections by priority)
        candidates.sort(key=lambda c: c[0])

        # Greedily add sections within budget
        parts: List[str] = [SHARED_PREAMBLE]
        included_by_skill: Dict[str, List[str]] = {}
        for _priority, header, content, skill_name in candidates:
            if not content and header:
                # This is a skill title header — always include
                parts.append(header)
                continue

            tokens = len(content) // 4
            if tokens <= remaining:
                parts.append(content)
                remaining -= tokens
                included_by_skill.setdefault(skill_name, []).append(header)
            else:
                logger.info(
                    "Budget exceeded: skipping section '%s' from '%s' "
                    "(%d tokens, %d remaining)",
                    header,
                    skill_name,
                    tokens,
                    remaining,
                )

        return "\n\n---\n\n".join(parts)
