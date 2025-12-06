#!/usr/bin/env python3
"""
Optimized context detection and skill selection for Dev-AID.
Replaces detect-context.sh and select-skills.sh with efficient single-pass implementation.

Usage:
    context-detector.py detect [directory]        # Detect context keywords
    context-detector.py select "keywords" [max]   # Select skills based on context
    context-detector.py auto [directory] [max]    # Detect context and select skills
"""

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class ContextDetector:
    """Efficient context detection using single-pass file scanning."""

    def __init__(self, registry_path: str):
        """Initialize detector with skills registry."""
        with open(registry_path, "r") as f:
            self.registry = json.load(f)

        # Pre-compile patterns for efficiency
        self.file_extensions = self._build_extension_map()
        self.config_files = {
            "package.json": self._extract_package_json,
            "Cargo.toml": self._extract_cargo_toml,
            "pyproject.toml": self._extract_python_deps,
            "requirements.txt": self._extract_python_deps,
            "go.mod": self._extract_go_mod,
            "Gemfile": self._extract_gemfile,
        }

    def _build_extension_map(self) -> Dict[str, str]:
        """Build extension to technology mapping."""
        return {
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript React",
            ".jsx": "React",
            ".py": "Python",
            ".rs": "Rust",
            ".go": "Go",
            ".rb": "Ruby",
            ".sh": "Bash",
            ".graphql": "GraphQL",
            ".vue": "Vue",
            ".svelte": "Svelte",
        }

    def detect_context(self, project_dir: str, max_files: int = 1000) -> Set[str]:
        """
        Detect project context in a single pass.
        Returns set of context keywords.
        """
        context = set()
        project_path = Path(project_dir).resolve()

        if not project_path.exists():
            raise ValueError(f"Directory does not exist: {project_dir}")

        # Check for specific config files (high-value signals)
        for config_file, extractor in self.config_files.items():
            config_path = project_path / config_file
            if config_path.exists():
                try:
                    keywords = extractor(config_path)
                    context.update(keywords)
                except Exception:
                    pass  # Skip files that can't be parsed

        # Check for Docker
        if (project_path / "Dockerfile").exists():
            context.add("Docker")
        if (project_path / "docker-compose.yml").exists():
            context.add("Docker Compose")

        # Check for GitHub Actions
        gh_workflows = project_path / ".github" / "workflows"
        if gh_workflows.exists():
            context.add("GitHub Actions")

        # Single-pass file scanning (limit to prevent slowdown on large repos)
        file_count = 0
        for file_path in project_path.rglob("*"):
            if file_count >= max_files:
                break

            if not file_path.is_file():
                continue

            # Skip common ignore patterns
            if any(part.startswith(".") for part in file_path.parts[len(project_path.parts) :]):
                if not any(part in [".github", ".dev-aid"] for part in file_path.parts):
                    continue

            if any(
                part in ["node_modules", "venv", "__pycache__", "target", "dist", "build"]
                for part in file_path.parts
            ):
                continue

            # Extract technology from extension
            ext = file_path.suffix.lower()
            if ext in self.file_extensions:
                context.add(self.file_extensions[ext])

            file_count += 1

        return context

    def _extract_package_json(self, path: Path) -> Set[str]:
        """Extract dependencies from package.json."""
        with open(path, "r") as f:
            data = json.load(f)

        keywords = {"Node.js", "JavaScript"}
        for dep_type in ["dependencies", "devDependencies"]:
            if dep_type in data:
                keywords.update(data[dep_type].keys())

        return keywords

    def _extract_cargo_toml(self, path: Path) -> Set[str]:
        """Extract dependencies from Cargo.toml."""
        keywords = {"Rust"}
        with open(path, "r") as f:
            in_deps = False
            for line in f:
                line = line.strip()
                if line.startswith("[dependencies]"):
                    in_deps = True
                elif line.startswith("["):
                    in_deps = False
                elif in_deps and "=" in line:
                    dep_name = line.split("=")[0].strip()
                    keywords.add(dep_name)
        return keywords

    def _extract_python_deps(self, path: Path) -> Set[str]:
        """Extract dependencies from Python files."""
        keywords = {"Python"}
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Extract package name before version specifier
                    pkg = re.split(r"[=<>~!\[]", line)[0].strip()
                    if pkg:
                        keywords.add(pkg)
        return keywords

    def _extract_go_mod(self, path: Path) -> Set[str]:
        """Extract dependencies from go.mod."""
        keywords = {"Go"}
        with open(path, "r") as f:
            for line in f:
                if line.strip().startswith("require"):
                    continue
                parts = line.strip().split()
                if len(parts) >= 2:
                    keywords.add(parts[0])
        return keywords

    def _extract_gemfile(self, path: Path) -> Set[str]:
        """Extract dependencies from Gemfile."""
        keywords = {"Ruby"}
        with open(path, "r") as f:
            for line in f:
                match = re.match(r"gem\s+['\"]([^'\"]+)['\"]", line)
                if match:
                    keywords.add(match.group(1))
        return keywords


class SkillSelector:
    """Efficient skill selection with optimized scoring."""

    def __init__(self, registry_path: str):
        """Initialize selector with skills registry."""
        with open(registry_path, "r") as f:
            self.registry = json.load(f)

    def select_skills(
        self, context: Set[str], max_skills: int = 5, min_score: int = 5
    ) -> List[str]:
        """
        Select skills based on context keywords.
        Returns list of skill names sorted by relevance.
        """
        # Normalize context for case-insensitive matching
        context_lower = {kw.lower() for kw in context}

        # Calculate scores for all skills in one pass
        scores = {}
        for skill_name, skill_data in self.registry.items():
            score = self._calculate_score(skill_name, skill_data, context_lower)
            if score >= min_score:
                scores[skill_name] = score

        # Sort by score descending
        sorted_skills = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Select top skills respecting exclusions
        selected = []
        selected_set = set()

        for skill_name, score in sorted_skills:
            # Check exclusions
            activation = self.registry[skill_name].get("activation", {})
            exclude_with = set(activation.get("exclude_with", []))

            if exclude_with & selected_set:
                continue  # Skip if conflicts with already selected skill

            selected.append(skill_name)
            selected_set.add(skill_name)

            if len(selected) >= max_skills:
                break

        # Add required dependencies
        final_skills = selected.copy()
        for skill_name in selected:
            activation = self.registry[skill_name].get("activation", {})
            requires = activation.get("requires", [])
            for required_skill in requires:
                if required_skill not in final_skills:
                    final_skills.append(required_skill)

        return final_skills

    def _calculate_score(self, skill_name: str, skill_data: Dict, context_lower: Set[str]) -> int:
        """Calculate relevance score for a skill."""
        activation = skill_data.get("activation", {})
        score = 0

        # Primary keywords: 10 points each
        for keyword in activation.get("primary_keywords", []):
            if keyword.lower() in context_lower:
                score += 10

        # Secondary keywords: 5 points each
        for keyword in activation.get("secondary_keywords", []):
            if keyword.lower() in context_lower:
                score += 5

        # Technologies: 8 points each
        for tech in activation.get("technologies", []):
            if tech.lower() in context_lower:
                score += 8

        # Confidence weights: boost score
        weights = activation.get("confidence_weights", {})
        for keyword, weight in weights.items():
            if keyword.lower() in context_lower:
                score += int(weight * 100)

        return score


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    script_dir = Path(__file__).parent.resolve()
    registry_path = script_dir / "../skills/registry/skills-index.json"

    if not registry_path.exists():
        print(f"Error: Registry file not found: {registry_path}", file=sys.stderr)
        sys.exit(1)

    if command == "detect":
        # Detect context only
        project_dir = sys.argv[2] if len(sys.argv) > 2 else "."
        detector = ContextDetector(str(registry_path))
        context = detector.detect_context(project_dir)
        print(" ".join(sorted(context)))

    elif command == "select":
        # Select skills from context keywords
        if len(sys.argv) < 3:
            print('Usage: context-detector.py select "keywords" [max_skills]', file=sys.stderr)
            sys.exit(1)

        context_str = sys.argv[2]
        max_skills = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        context = set(context_str.split())

        selector = SkillSelector(str(registry_path))
        skills = selector.select_skills(context, max_skills)
        for skill in skills:
            print(skill)

    elif command == "auto":
        # Detect context and select skills in one go
        project_dir = sys.argv[2] if len(sys.argv) > 2 else "."
        max_skills = int(sys.argv[3]) if len(sys.argv) > 3 else 5

        detector = ContextDetector(str(registry_path))
        context = detector.detect_context(project_dir)

        selector = SkillSelector(str(registry_path))
        skills = selector.select_skills(context, max_skills)
        for skill in skills:
            print(skill)

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
