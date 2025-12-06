#!/usr/bin/env python3
"""
Auto-Generate CI/CD Workflows

Detects project context and generates production-ready GitHub Actions workflows
with security scanning (Gitleaks, Trivy) by default.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Optional


class CIGenerator:
    """Generates GitHub Actions workflows based on project context"""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.templates_dir = Path(__file__).parent.parent / "templates" / "ci"

    def detect_project_type(self) -> Dict[str, any]:
        """Detect project type and build configuration"""
        context = {
            "language": None,
            "package_manager": None,
            "build_tool": None,
            "has_docker": False,
            "test_framework": None,
            "commands": {},
        }

        # Check for Node.js/TypeScript
        if (self.project_dir / "package.json").exists():
            context["language"] = "nodejs"
            pkg_json = json.loads((self.project_dir / "package.json").read_text())

            # Detect package manager
            if (self.project_dir / "bun.lockb").exists():
                context["package_manager"] = "bun"
                context["commands"]["install"] = "bun install"
                context["commands"]["build"] = "bun run build"
                context["commands"]["test"] = "bun test"
            elif (self.project_dir / "pnpm-lock.yaml").exists():
                context["package_manager"] = "pnpm"
                context["commands"]["install"] = "pnpm install"
                context["commands"]["build"] = "pnpm build"
                context["commands"]["test"] = "pnpm test"
            elif (self.project_dir / "yarn.lock").exists():
                context["package_manager"] = "yarn"
                context["commands"]["install"] = "yarn install"
                context["commands"]["build"] = "yarn build"
                context["commands"]["test"] = "yarn test"
            else:
                context["package_manager"] = "npm"
                context["commands"]["install"] = "npm ci"
                context["commands"]["build"] = "npm run build"
                context["commands"]["test"] = "npm test"

            # Detect linter
            scripts = pkg_json.get("scripts", {})
            if "lint" in scripts:
                context["commands"][
                    "lint"
                ] = f"{context['package_manager']} {'run ' if context['package_manager'] != 'bun' else ''}lint"
            else:
                context["commands"]["lint"] = "echo 'No lint script found, skipping'"

            # Detect TypeScript
            if (self.project_dir / "tsconfig.json").exists():
                context["commands"]["type_check"] = "npx tsc --noEmit"
            else:
                context["commands"]["type_check"] = "echo 'No TypeScript, skipping'"

        # Check for Python
        elif (
            (self.project_dir / "pyproject.toml").exists()
            or (self.project_dir / "requirements.txt").exists()
            or (self.project_dir / "setup.py").exists()
        ):

            context["language"] = "python"

            # Detect package manager
            if (self.project_dir / "pyproject.toml").exists():
                pyproject = (self.project_dir / "pyproject.toml").read_text()
                if "[tool.poetry]" in pyproject:
                    context["package_manager"] = "poetry"
                    context["commands"]["install"] = "poetry install"
                    context["commands"]["test"] = "poetry run pytest"
                elif "[tool.uv]" in pyproject or "uv" in pyproject:
                    context["package_manager"] = "uv"
                    context["commands"]["install"] = "uv sync"
                    context["commands"]["test"] = "uv run pytest"
                else:
                    context["package_manager"] = "pip"
                    context["commands"]["install"] = "pip install -r requirements.txt"
                    context["commands"]["test"] = "pytest"
            else:
                context["package_manager"] = "pip"
                context["commands"]["install"] = "pip install -r requirements.txt"
                context["commands"]["test"] = "pytest"

            # Detect linter
            if (self.project_dir / "ruff.toml").exists() or "tool.ruff" in (
                self.project_dir / "pyproject.toml"
            ).read_text():
                context["commands"]["lint"] = "ruff check ."
            else:
                context["commands"]["lint"] = "flake8 ."

            # Detect type checker
            if (self.project_dir / "mypy.ini").exists() or "[tool.mypy]" in (
                self.project_dir / "pyproject.toml"
            ).read_text():
                context["commands"]["type_check"] = "mypy ."
            else:
                context["commands"]["type_check"] = "echo 'No type checker configured'"

        # Check for Rust
        elif (self.project_dir / "Cargo.toml").exists():
            context["language"] = "rust"
            context["package_manager"] = "cargo"
            context["commands"]["install"] = "cargo fetch"
            context["commands"]["build"] = "cargo build"
            context["commands"]["test"] = "cargo test"
            context["commands"]["lint"] = "cargo clippy"
            context["commands"]["type_check"] = "cargo check"

        # Check for Go
        elif (self.project_dir / "go.mod").exists():
            context["language"] = "go"
            context["package_manager"] = "go"
            context["commands"]["install"] = "go mod download"
            context["commands"]["build"] = "go build ./..."
            context["commands"]["test"] = "go test ./..."
            context["commands"]["lint"] = "go vet ./..."
            context["commands"]["type_check"] = "go fmt -l ."

        # Check for Docker
        if (self.project_dir / "Dockerfile").exists():
            context["has_docker"] = True

        return context

    def generate_workflow(self, context: Dict[str, any], output_path: Optional[Path] = None) -> str:
        """Generate GitHub Actions workflow from template"""

        if not context["language"]:
            raise ValueError("Could not detect project language")

        # Load template
        template_file = self.templates_dir / f"{context['language']}.yml"
        if not template_file.exists():
            raise ValueError(f"No template found for {context['language']}")

        template = template_file.read_text()

        # Simple template substitution
        replacements = {
            "{{PACKAGE_MANAGER}}": context.get("package_manager", ""),
            "{{INSTALL_COMMAND}}": context["commands"].get("install", ""),
            "{{BUILD_COMMAND}}": context["commands"].get("build", ""),
            "{{TEST_COMMAND}}": context["commands"].get("test", ""),
            "{{LINT_COMMAND}}": context["commands"].get("lint", ""),
            "{{TYPE_CHECK_COMMAND}}": context["commands"].get("type_check", ""),
        }

        workflow = template
        for placeholder, value in replacements.items():
            workflow = workflow.replace(placeholder, value)

        # Handle Docker conditional
        if context["has_docker"]:
            workflow = re.sub(
                r"\{\{#DOCKER\}\}(.*?)\{\{/DOCKER\}\}", r"\1", workflow, flags=re.DOTALL
            )
        else:
            workflow = re.sub(r"\{\{#DOCKER\}\}.*?\{\{/DOCKER\}\}", "", workflow, flags=re.DOTALL)

        # Write to file if output path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(workflow)

        return workflow

    def run(self, output_file: Optional[str] = None):
        """Main execution"""
        print("🔍 Detecting project context...")
        context = self.detect_project_type()

        if not context["language"]:
            print("❌ Could not detect project language")
            print("Supported: Node.js, Python, Rust, Go")
            return 1

        print(f"✅ Detected: {context['language']}")
        print(f"   Package Manager: {context['package_manager']}")
        print(f"   Docker: {'Yes' if context['has_docker'] else 'No'}")

        print("\n🛠️  Generating CI workflow...")

        output_path = None
        if output_file:
            output_path = self.project_dir / output_file
        else:
            output_path = self.project_dir / ".github" / "workflows" / "ci.yml"

        workflow = self.generate_workflow(context, output_path)

        print(f"✅ Generated: {output_path}")
        print(f"   Lines: {len(workflow.splitlines())}")
        print("\n📋 Commands configured:")
        for cmd_type, cmd in context["commands"].items():
            print(f"   {cmd_type}: {cmd}")

        print("\n✅ Done! Workflow includes:")
        print("   - Security scanning (Gitleaks + Trivy)")
        print("   - Linting and type checking")
        print("   - Testing across multiple versions")
        if context["has_docker"]:
            print("   - Docker build and scan")

        return 0


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate GitHub Actions CI/CD workflows")
    parser.add_argument(
        "project_dir", nargs="?", default=".", help="Project directory (default: current directory)"
    )
    parser.add_argument(
        "-o", "--output", help="Output file path (default: .github/workflows/ci.yml)"
    )

    args = parser.parse_args()

    generator = CIGenerator(Path(args.project_dir))
    return generator.run(args.output)


if __name__ == "__main__":
    sys.exit(main())
