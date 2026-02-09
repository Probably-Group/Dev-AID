#!/usr/bin/env python3
"""
Auto-Generate CI/CD Workflows

Detects project context and generates production-ready GitHub Actions workflows
with comprehensive, auto-updating security scanning (3 tools):
- Gitleaks (secrets, git history + current files, 160+ patterns)
- Trivy (CVE + Misconfig + Secrets: dependencies, Dockerfiles, IaC)
- Opengrep (SAST with 340+ rules: OWASP Top 10, CWE Top 25, CI/CD security)

All critical findings FAIL the workflow (no continue-on-error bypasses).
All tools auto-update their databases/rules for latest threat detection.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Maximum size for config files to prevent memory issues (10 MB)
MAX_CONFIG_FILE_SIZE = 10 * 1024 * 1024


class CIGenerator:
    """Generates GitHub Actions workflows based on project context"""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.templates_dir = Path(__file__).parent.parent / "templates" / "ci"

    def detect_project_type(self) -> Dict[str, Any]:
        """Detect project type and build configuration"""
        context: Dict[str, Any] = {
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
            raw_content = (self.project_dir / "package.json").read_text()
            if len(raw_content) > MAX_CONFIG_FILE_SIZE:
                raise ValueError(
                    f"package.json exceeds maximum size ({MAX_CONFIG_FILE_SIZE} bytes)"
                )
            try:
                pkg_json = json.loads(raw_content)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in package.json: {e}")

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
                context["commands"]["lint"] = "flake8 . --exclude .venv,venv,.env"

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

        # Check for Java
        elif (self.project_dir / "pom.xml").exists():
            context["language"] = "java"
            context["package_manager"] = "maven"
            context["commands"]["install"] = "mvn dependency:resolve"
            context["commands"]["build"] = "mvn clean compile"
            context["commands"]["test"] = "mvn test"
            context["commands"]["lint"] = "mvn checkstyle:check"
            context["commands"]["coverage"] = "mvn jacoco:report"

        elif (self.project_dir / "build.gradle").exists() or (
            self.project_dir / "build.gradle.kts"
        ).exists():
            context["language"] = "java"
            context["package_manager"] = "gradle"
            context["commands"]["install"] = "./gradlew build --no-daemon"
            context["commands"]["build"] = "./gradlew assemble"
            context["commands"]["test"] = "./gradlew test"
            context["commands"]["lint"] = "./gradlew checkstyleMain"
            context["commands"]["coverage"] = "./gradlew jacocoTestReport"

        # Check for C#/.NET
        elif (
            any((self.project_dir / f).exists() for f in ["*.csproj", "*.sln"])
            or list(self.project_dir.glob("*.csproj"))
            or list(self.project_dir.glob("*.sln"))
        ):
            context["language"] = "csharp"
            context["package_manager"] = "dotnet"
            context["commands"]["install"] = "dotnet restore"
            context["commands"]["build"] = "dotnet build --configuration Release"
            context["commands"]["test"] = "dotnet test --configuration Release"
            context["commands"]["lint"] = "dotnet format --verify-no-changes"
            context["commands"]["coverage"] = 'dotnet test --collect:"XPlat Code Coverage"'

        # Check for PHP
        elif (self.project_dir / "composer.json").exists():
            context["language"] = "php"
            context["package_manager"] = "composer"
            context["commands"]["install"] = "composer install --prefer-dist --no-progress"
            context["commands"]["build"] = "echo 'No build needed for PHP'"
            context["commands"]["test"] = "vendor/bin/phpunit"
            context["commands"]["lint"] = "vendor/bin/phpcs"
            context["commands"]["coverage"] = "vendor/bin/phpunit --coverage-clover coverage.xml"

        # Check for Ruby
        elif (self.project_dir / "Gemfile").exists():
            context["language"] = "ruby"
            context["package_manager"] = "bundler"
            context["commands"]["install"] = "bundle install"
            context["commands"]["build"] = "echo 'No build needed for Ruby'"
            context["commands"]["test"] = "bundle exec rspec"
            context["commands"]["lint"] = "bundle exec rubocop"
            context["commands"]["coverage"] = "bundle exec rspec"

        # Check for C++
        elif (self.project_dir / "CMakeLists.txt").exists():
            context["language"] = "cpp"
            context["package_manager"] = "cmake"
            context["commands"]["install"] = "echo 'Dependencies managed by CMake'"
            context["commands"]["build"] = "cmake -B build -DCMAKE_BUILD_TYPE=Release"
            context["commands"]["test"] = "ctest --output-on-failure"
            context["commands"]["lint"] = "clang-tidy src/*.cpp"

        # Check for Docker
        if (self.project_dir / "Dockerfile").exists():
            context["has_docker"] = True

        return context

    def get_frequency_config(self, frequency: str) -> Dict[str, Any]:
        """Get CI execution frequency configuration

        Args:
            frequency: 'aggressive', 'balanced', or 'minimal'

        Returns:
            Dictionary with frequency settings
        """
        configs = {
            "aggressive": {
                "description": "Run on every push/PR (most thorough, highest cost)",
                "triggers": ["push", "pull_request"],
                "branches": ["main", "master", "develop"],
                "skip_draft_prs": False,
                "cross_platform": ["ubuntu-22.04", "windows-latest", "macos-latest"],
                "path_filters": None,  # Run on all changes
                "concurrency_cancel": False,  # Don't cancel, run everything
                "estimated_cost": "High (100% baseline)",
            },
            "balanced": {
                "description": "Run on PRs with path filters (good balance, recommended)",
                "triggers": ["pull_request"],
                "branches": ["main", "master", "develop"],
                "skip_draft_prs": True,
                "cross_platform": ["ubuntu-22.04"],  # Single OS for PRs
                "path_filters": ["**.py", "**.js", "**.ts", "**.go", "**.rs"],
                "concurrency_cancel": True,  # Cancel outdated runs
                "estimated_cost": "Medium (~15-30% of aggressive)",
            },
            "minimal": {
                "description": "Run only on main branch pushes (lowest cost)",
                "triggers": ["push"],
                "branches": ["main", "master"],
                "skip_draft_prs": True,
                "cross_platform": ["ubuntu-22.04"],
                "path_filters": ["**.py", "**.js", "**.ts", "**.go", "**.rs"],
                "concurrency_cancel": True,
                "estimated_cost": "Low (~5-10% of aggressive)",
            },
        }

        if frequency not in configs:
            raise ValueError(f"Invalid frequency: {frequency}. Choose from: {list(configs.keys())}")

        return configs[frequency]

    def _apply_frequency_config(self, workflow: str, freq_config: Dict[str, Any]) -> str:
        """Apply frequency configuration to workflow YAML

        Args:
            workflow: Original workflow content
            freq_config: Frequency configuration dictionary

        Returns:
            Modified workflow with frequency settings applied
        """
        lines = workflow.splitlines()
        result = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Add frequency comment at the top
            if i == 0 and line.startswith("name:"):
                result.append(line)
                result.append("")
                result.append(f"# CI Frequency: {freq_config['description']}")
                result.append(f"# Estimated cost: {freq_config['estimated_cost']}")
                i += 1
                continue

            # Modify 'on:' section
            if line.strip() == "on:":
                result.append(line)
                i += 1

                # Build trigger configuration
                result.append("  # Triggers:")
                for trigger in freq_config["triggers"]:
                    result.append(f"  {trigger}:")
                    if trigger == "pull_request":
                        result.append(f"    branches: {freq_config['branches']}")
                        if freq_config["path_filters"]:
                            result.append("    paths:")
                            for path in freq_config["path_filters"]:
                                result.append(f"      - '{path}'")
                    elif trigger == "push":
                        result.append(f"    branches: {freq_config['branches']}")
                        if freq_config["path_filters"]:
                            result.append("    paths:")
                            for path in freq_config["path_filters"]:
                                result.append(f"      - '{path}'")

                # Add concurrency group if enabled
                if freq_config["concurrency_cancel"]:
                    result.append("")
                    result.append("# Cancel outdated workflow runs")
                    result.append("concurrency:")
                    result.append("  group: ${{ github.workflow }}-${{ github.ref }}")
                    result.append("  cancel-in-progress: true")

                # Skip existing 'on:' configuration
                while i < len(lines) and not lines[i].strip().startswith("jobs:"):
                    i += 1
                continue

            # Add draft PR skip and OS configuration to jobs
            if line.strip().startswith("runs-on:") and "${{ matrix.os }}" in line:
                # Add draft PR skip before runs-on
                if freq_config["skip_draft_prs"]:
                    result.append("    # Skip draft PRs to save CI minutes")
                    result.append("    if: github.event.pull_request.draft == false")
                result.append(line)
                i += 1
                continue

            # Modify matrix OS configuration
            if "os: [" in line and "matrix" in workflow[: workflow.find(line)]:
                indent = len(line) - len(line.lstrip())
                os_list = ", ".join(freq_config["cross_platform"])
                result.append(" " * indent + f"os: [{os_list}]")
                i += 1
                continue

            result.append(line)
            i += 1

        return "\n".join(result)

    def generate_workflow(
        self,
        context: Dict[str, Any],
        output_path: Optional[Path] = None,
        optimize: bool = False,
        frequency: str = "balanced",
    ) -> str:
        """Generate GitHub Actions workflow from template

        Args:
            context: Project context dictionary
            output_path: Optional path to write workflow file
            optimize: If True, use optimized templates with caching, concurrency, parallel execution
            frequency: CI execution frequency ('aggressive', 'balanced', or 'minimal')
        """

        if not context["language"]:
            raise ValueError("Could not detect project language")

        # Get frequency configuration
        freq_config = self.get_frequency_config(frequency)

        # Load template (optimized or standard)
        if optimize:
            template_file = self.templates_dir / "optimized" / f"{context['language']}.yml"
            if not template_file.exists():
                print(
                    f"⚠️  No optimized template for {context['language']}, using standard template"
                )
                template_file = self.templates_dir / f"{context['language']}.yml"
        else:
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

        # Apply frequency configuration
        workflow = self._apply_frequency_config(workflow, freq_config)

        # Write to file if output path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(workflow)

        return workflow

    def run(
        self, output_file: Optional[str] = None, optimize: bool = False, frequency: str = "balanced"
    ):
        """Main execution

        Args:
            output_file: Optional output file path
            optimize: If True, use optimized templates with performance enhancements
            frequency: CI execution frequency ('aggressive', 'balanced', or 'minimal')
        """
        print("🔍 Detecting project context...")
        context = self.detect_project_type()

        if not context["language"]:
            print("❌ Could not detect project language")
            print("Supported: Node.js, Python, Rust, Go, Java, C#/.NET, PHP, Ruby, C++")
            return 1

        print(f"✅ Detected: {context['language']}")
        print(f"   Package Manager: {context['package_manager']}")
        print(f"   Docker: {'Yes' if context['has_docker'] else 'No'}")

        # Get frequency configuration
        freq_config = self.get_frequency_config(frequency)
        print(f"\n📊 CI Frequency: {frequency.upper()}")
        print(f"   {freq_config['description']}")
        print(f"   Estimated cost: {freq_config['estimated_cost']}")

        if optimize:
            print("\n⚡ Using optimized template with:")
            print("   - Concurrency groups (cancel outdated runs)")
            print("   - Advanced caching (dependencies + build artifacts)")
            print("   - Parallel execution (linting, testing)")
            print("   - Explicit ubuntu-22.04 (faster startup)")
            print("   - Expected speedup: 40-70% faster CI runs")

        print("\n🛠️  Generating CI workflow...")

        output_path = None
        if output_file:
            output_path = self.project_dir / output_file
        else:
            output_path = self.project_dir / ".github" / "workflows" / "ci.yml"

        workflow = self.generate_workflow(
            context, output_path, optimize=optimize, frequency=frequency
        )

        print(f"✅ Generated: {output_path}")
        print(f"   Lines: {len(workflow.splitlines())}")
        print("\n📋 Commands configured:")
        for cmd_type, cmd in context["commands"].items():
            print(f"   {cmd_type}: {cmd}")

        print("\n✅ Done! Workflow includes:")
        print("   - 🔒 Comprehensive security scanning (3 tools, auto-updating):")
        print("     • Gitleaks - Secret scanning (git history + current, 160+ patterns)")
        print("     • Trivy - CVE + Misconfig + Secrets (deps, Dockerfiles, IaC)")
        print("     • Opengrep - SAST with 340+ rules (OWASP, CWE Top 25, CI/CD)")
        print("   - 🔍 Linting and type checking")
        print("   - 🧪 Testing across multiple versions")
        if context["has_docker"]:
            print("   - Docker build and scan")
        if optimize:
            print("\n⚡ Optimization features:")
            print("   - Concurrency control for faster iteration")
            print("   - Comprehensive caching for reduced build times")
            print("   - Parallel execution where possible")
            print("   📖 See .dev-aid/docs/CI-OPTIMIZATION-GUIDE.md for details")

        # Show frequency configuration details
        print(f"\n📊 CI Frequency Configuration ({frequency}):")
        print(f"   Triggers: {', '.join(freq_config['triggers'])}")
        print(f"   Branches: {', '.join(freq_config['branches'])}")
        print(f"   Platforms: {', '.join(freq_config['cross_platform'])}")
        print(f"   Draft PRs: {'Skipped' if freq_config['skip_draft_prs'] else 'Included'}")
        print(
            f"   Concurrency cancel: {'Enabled' if freq_config['concurrency_cancel'] else 'Disabled'}"
        )
        if freq_config["path_filters"]:
            print(f"   Path filters: {', '.join(freq_config['path_filters'][:3])}...")
        else:
            print("   Path filters: None (runs on all changes)")

        return 0


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate GitHub Actions CI/CD workflows",
        epilog="Example: python ci-generator.py --optimize  # Generate optimized workflow",
    )
    parser.add_argument(
        "project_dir", nargs="?", default=".", help="Project directory (default: current directory)"
    )
    parser.add_argument(
        "-o", "--output", help="Output file path (default: .github/workflows/ci.yml)"
    )
    parser.add_argument(
        "--optimize",
        action="store_true",
        help="Use optimized template with caching, concurrency, and parallel execution (40-70%% faster)",
    )
    parser.add_argument(
        "--frequency",
        choices=["aggressive", "balanced", "minimal"],
        default="balanced",
        help=(
            "CI execution frequency (default: balanced). "
            "aggressive: Run on every push/PR (100%% cost). "
            "balanced: Run on PRs only, single OS (15-30%% cost). "
            "minimal: Run on main branch only (5-10%% cost)."
        ),
    )

    args = parser.parse_args()

    generator = CIGenerator(Path(args.project_dir))
    return generator.run(args.output, optimize=args.optimize, frequency=args.frequency)


if __name__ == "__main__":
    sys.exit(main())
