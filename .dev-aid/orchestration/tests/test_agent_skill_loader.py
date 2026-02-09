"""Tests for agent skill loader (SKILL.md parsing)."""

from pathlib import Path

import pytest
from agents.core.skill_loader import SkillLoader, _parse_frontmatter, parse_skill_file


class TestParseFrontmatter:
    """Tests for YAML frontmatter parsing."""

    def test_simple_key_value(self) -> None:
        result = _parse_frontmatter("name: test-skill\nversion: 2.0.0")
        assert result["name"] == "test-skill"
        assert result["version"] == "2.0.0"

    def test_quoted_values(self) -> None:
        result = _parse_frontmatter('description: "A test skill"')
        assert result["description"] == "A test skill"

    def test_boolean_values(self) -> None:
        result = _parse_frontmatter("auto_load: true\nenabled: false")
        assert result["auto_load"] is True
        assert result["enabled"] is False

    def test_integer_values(self) -> None:
        result = _parse_frontmatter("token_budget: 250")
        assert result["token_budget"] == 250

    def test_inline_list(self) -> None:
        result = _parse_frontmatter("tools: [Read, Grep, Write]")
        assert result["tools"] == ["Read", "Grep", "Write"]

    def test_multiline_list(self) -> None:
        text = "triggers:\n  - file_save\n  - edit_complete"
        result = _parse_frontmatter(text)
        assert result["triggers"] == ["file_save", "edit_complete"]

    def test_empty_list(self) -> None:
        result = _parse_frontmatter("items: []")
        assert result["items"] == []


class TestParseSkillFile:
    """Tests for parsing SKILL.md files."""

    def test_parse_full_skill(self, tmp_path: Path) -> None:
        content = """---
name: test-skill
version: 2.0.0
description: "A test skill for testing"
risk_level: MEDIUM
category: expert
auto_load: true
token_budget: 250
triggers:
  - file_save
tools: [Read, Grep]
---

# Test Skill

This is the skill body content.

## Section 1
Some instructions here.
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(content)

        skill = parse_skill_file(skill_file)
        assert skill.metadata.name == "test-skill"
        assert skill.metadata.version == "2.0.0"
        assert skill.metadata.description == "A test skill for testing"
        assert skill.metadata.risk_level == "MEDIUM"
        assert skill.metadata.category == "expert"
        assert skill.metadata.auto_load is True
        assert skill.metadata.token_budget == 250
        assert skill.metadata.triggers == ["file_save"]
        assert skill.metadata.tools == ["Read", "Grep"]
        assert "# Test Skill" in skill.body
        assert "## Section 1" in skill.body

    def test_parse_no_frontmatter(self, tmp_path: Path) -> None:
        content = "# Just Markdown\n\nNo frontmatter here."
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(content)

        skill = parse_skill_file(skill_file)
        assert skill.metadata.name == tmp_path.name  # Falls back to dir name
        assert skill.body == "# Just Markdown\n\nNo frontmatter here."

    def test_parse_minimal_frontmatter(self, tmp_path: Path) -> None:
        content = """---
name: minimal
---

Body text.
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(content)

        skill = parse_skill_file(skill_file)
        assert skill.metadata.name == "minimal"
        assert skill.metadata.version == "1.0.0"
        assert skill.metadata.risk_level == "LOW"


class TestSkillLoader:
    """Tests for SkillLoader."""

    @pytest.fixture
    def skills_dir(self, tmp_path: Path) -> Path:
        """Create a mock skills directory."""
        skills = tmp_path / "skills"
        skills.mkdir()

        # Create expert category
        expert = skills / "expert"
        expert.mkdir()

        # Skill 1
        s1 = expert / "appsec-expert"
        s1.mkdir()
        (s1 / "SKILL.md").write_text(
            "---\nname: appsec-expert\ndescription: App security\n---\n\n# AppSec\nSecurity stuff."
        )

        # Skill 2
        s2 = expert / "senior-architect"
        s2.mkdir()
        (s2 / "SKILL.md").write_text(
            "---\nname: senior-architect\ndescription: Architecture\n---\n\n# Architect\nPatterns."
        )

        # Create core category
        core = skills / "core"
        core.mkdir()
        s3 = core / "code-reviewer"
        s3.mkdir()
        (s3 / "SKILL.md").write_text(
            "---\nname: code-reviewer\ndescription: Code review\n---\n\n# Reviewer\nReview stuff."
        )

        return skills

    def test_discover_skills(self, skills_dir: Path) -> None:
        loader = SkillLoader(skills_dir)
        skills = loader.discover_skills()
        assert "appsec-expert" in skills
        assert "senior-architect" in skills
        assert "code-reviewer" in skills
        assert len(skills) == 3

    def test_load_skill(self, skills_dir: Path) -> None:
        loader = SkillLoader(skills_dir)
        skill = loader.load_skill("appsec-expert")
        assert skill is not None
        assert skill.metadata.name == "appsec-expert"
        assert "Security stuff" in skill.body

    def test_load_skill_caching(self, skills_dir: Path) -> None:
        loader = SkillLoader(skills_dir)
        s1 = loader.load_skill("appsec-expert")
        s2 = loader.load_skill("appsec-expert")
        assert s1 is s2  # Same object from cache

    def test_load_skill_not_found(self, skills_dir: Path) -> None:
        loader = SkillLoader(skills_dir)
        skill = loader.load_skill("nonexistent-skill")
        assert skill is None

    def test_load_skills_multiple(self, skills_dir: Path) -> None:
        loader = SkillLoader(skills_dir)
        skills = loader.load_skills(["appsec-expert", "senior-architect"])
        assert len(skills) == 2

    def test_load_skills_partial(self, skills_dir: Path) -> None:
        loader = SkillLoader(skills_dir)
        skills = loader.load_skills(["appsec-expert", "nonexistent"])
        assert len(skills) == 1

    def test_build_system_prompt(self, skills_dir: Path) -> None:
        loader = SkillLoader(skills_dir)
        prompt = loader.build_system_prompt(["appsec-expert", "senior-architect"])
        assert "## Skill: appsec-expert" in prompt
        assert "## Skill: senior-architect" in prompt
        assert "---" in prompt  # Separator

    def test_build_system_prompt_empty(self, skills_dir: Path) -> None:
        loader = SkillLoader(skills_dir)
        prompt = loader.build_system_prompt([])
        assert prompt == ""

    def test_build_system_prompt_nonexistent(self, skills_dir: Path) -> None:
        loader = SkillLoader(skills_dir)
        prompt = loader.build_system_prompt(["nonexistent"])
        assert prompt == ""
