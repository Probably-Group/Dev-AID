#!/usr/bin/env python3
"""
Living README - Documentation Drift Detector

Detects when documentation (README, CONTRIBUTING) drifts out of sync with reality.
Compares documentation claims against actual code, config files, and CLIs.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class DocSync:
    """Detects documentation drift"""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.issues: List[Dict[str, Any]] = []

    def extract_truth_from_package_json(self) -> Dict:
        """Extract ground truth from package.json"""
        pkg_file = self.project_dir / "package.json"
        if not pkg_file.exists():
            return {}

        pkg_data = json.loads(pkg_file.read_text())
        return {
            "package_manager": self.detect_node_package_manager(),
            "scripts": pkg_data.get("scripts", {}),
            "dependencies": list(pkg_data.get("dependencies", {}).keys()),
            "name": pkg_data.get("name"),
            "version": pkg_data.get("version"),
        }

    def detect_node_package_manager(self) -> str:
        """Detect which Node package manager is used"""
        if (self.project_dir / "bun.lockb").exists():
            return "bun"
        elif (self.project_dir / "pnpm-lock.yaml").exists():
            return "pnpm"
        elif (self.project_dir / "yarn.lock").exists():
            return "yarn"
        elif (self.project_dir / "package-lock.json").exists():
            return "npm"
        return "npm"  # default

    def extract_truth_from_pyproject(self) -> Dict:
        """Extract ground truth from pyproject.toml"""
        pyproject_file = self.project_dir / "pyproject.toml"
        if not pyproject_file.exists():
            return {}

        content = pyproject_file.read_text()

        # Detect Python package manager
        package_manager = "pip"
        if "[tool.poetry]" in content:
            package_manager = "poetry"
        elif "[tool.uv]" in content or "uv" in content:
            package_manager = "uv"

        return {"package_manager": package_manager, "is_python": True}

    def extract_truth_from_docker(self) -> Dict[str, Any]:
        """Extract truth from Docker files"""
        docker_file = self.project_dir / "Dockerfile"
        compose_file = self.project_dir / "docker-compose.yml"

        truth: Dict[str, Any] = {}
        if docker_file.exists():
            truth["has_dockerfile"] = True
            # Extract exposed ports
            content = docker_file.read_text()
            ports = re.findall(r"EXPOSE\s+(\d+)", content)
            truth["exposed_ports"] = ports

        if compose_file.exists():
            truth["has_compose"] = True

        return truth

    def extract_commands_from_readme(self, readme_path: Path) -> List[Dict]:
        """Extract command examples from README"""
        if not readme_path.exists():
            return []

        content = readme_path.read_text()
        commands = []

        # Find code blocks
        code_blocks = re.findall(r"```(?:bash|sh|shell)?\n(.*?)```", content, re.DOTALL)

        for block in code_blocks:
            for line in block.split("\n"):
                line = line.strip()
                # Skip comments and empty lines
                if line.startswith("#") or not line:
                    continue

                # Extract commands
                if any(
                    cmd in line
                    for cmd in [
                        "npm",
                        "yarn",
                        "pnpm",
                        "bun",
                        "pip",
                        "poetry",
                        "uv",
                        "docker",
                        "make",
                    ]
                ):
                    commands.append(
                        {
                            "command": line,
                            "type": "install" if "install" in line else "run",
                        }
                    )

        return commands

    def check_package_manager_consistency(self, readme_path: Path) -> List[Dict[str, Any]]:
        """Check if README uses correct package manager"""
        issues: List[Dict[str, Any]] = []

        # Get ground truth
        node_truth = self.extract_truth_from_package_json()
        python_truth = self.extract_truth_from_pyproject()

        if node_truth:
            actual_pm = node_truth["package_manager"]
            commands = self.extract_commands_from_readme(readme_path)

            # Check for wrong package manager commands
            wrong_pms = {"npm", "yarn", "pnpm", "bun"} - {actual_pm}

            for cmd_data in commands:
                cmd = cmd_data["command"]
                for wrong_pm in wrong_pms:
                    if wrong_pm in cmd and actual_pm not in cmd:
                        issues.append(
                            {
                                "severity": "HIGH",
                                "type": "package_manager_mismatch",
                                "claim": cmd,
                                "reality": f"Project uses {actual_pm}, not {wrong_pm}",
                                "suggestion": cmd.replace(wrong_pm, actual_pm),
                            }
                        )

        if python_truth:
            actual_pm = python_truth["package_manager"]
            commands = self.extract_commands_from_readme(readme_path)

            wrong_pms = {"pip", "poetry", "uv"} - {actual_pm}

            for cmd_data in commands:
                cmd = cmd_data["command"]
                for wrong_pm in wrong_pms:
                    if wrong_pm in cmd and actual_pm not in cmd:
                        issues.append(
                            {
                                "severity": "MEDIUM",
                                "type": "python_pm_mismatch",
                                "claim": cmd,
                                "reality": f"Project uses {actual_pm}, not {wrong_pm}",
                                "suggestion": cmd.replace(wrong_pm, actual_pm),
                            }
                        )

        return issues

    def check_docker_port_consistency(self, readme_path: Path) -> List[Dict[str, Any]]:
        """Check if documented ports match Dockerfile"""
        issues: List[Dict[str, Any]] = []
        docker_truth = self.extract_truth_from_docker()

        if docker_truth.get("exposed_ports"):
            readme_content = readme_path.read_text()
            actual_ports = docker_truth["exposed_ports"]

            for port in actual_ports:
                # Check if port is mentioned
                if port not in readme_content:
                    issues.append(
                        {
                            "severity": "LOW",
                            "type": "missing_port_documentation",
                            "reality": f"Dockerfile exposes port {port}",
                            "suggestion": f"Document that the application uses port {port}",
                        }
                    )

        return issues

    def check_script_consistency(self, readme_path: Path) -> List[Dict[str, Any]]:
        """Check if package.json scripts are documented"""
        issues: List[Dict[str, Any]] = []
        node_truth = self.extract_truth_from_package_json()

        if node_truth.get("scripts"):
            readme_content = readme_path.read_text()
            pm = node_truth["package_manager"]

            for script_name in node_truth["scripts"].keys():
                # Check if common scripts are documented
                if script_name in ["start", "build", "test", "dev"]:
                    command = f"{pm} {'run ' if pm != 'bun' else ''}{script_name}"
                    if command not in readme_content and script_name not in readme_content:
                        issues.append(
                            {
                                "severity": "MEDIUM",
                                "type": "undocumented_script",
                                "reality": f"package.json has '{script_name}' script",
                                "suggestion": f"Document how to run: {command}",
                            }
                        )

        return issues

    def run(self, readme_path: Optional[Path] = None, fix: bool = False):
        """Main execution"""
        if readme_path is None:
            readme_path = self.project_dir / "README.md"

        if not readme_path.exists():
            print(f"❌ README not found: {readme_path}")
            return 1

        print("🔍 Checking documentation consistency...")
        print(f"   README: {readme_path}")
        print()

        # Run checks
        all_issues = []
        all_issues.extend(self.check_package_manager_consistency(readme_path))
        all_issues.extend(self.check_docker_port_consistency(readme_path))
        all_issues.extend(self.check_script_consistency(readme_path))

        if not all_issues:
            print("✅ No documentation drift detected!")
            print("   README is in sync with project reality.")
            return 0

        # Report issues
        print(f"⚠️  Found {len(all_issues)} documentation drift issue(s):\n")

        high_count = len([i for i in all_issues if i["severity"] == "HIGH"])
        medium_count = len([i for i in all_issues if i["severity"] == "MEDIUM"])
        low_count = len([i for i in all_issues if i["severity"] == "LOW"])

        print(f"   🔴 HIGH: {high_count}")
        print(f"   🟡 MEDIUM: {medium_count}")
        print(f"   🟢 LOW: {low_count}")
        print()

        for idx, issue in enumerate(all_issues, 1):
            severity_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[issue["severity"]]
            print(
                f"{idx}. {severity_icon} {issue['severity']} - {issue['type'].replace('_', ' ').title()}"
            )

            if "claim" in issue:
                print(f"   Documented: {issue['claim']}")
            print(f"   Reality: {issue['reality']}")

            if "suggestion" in issue:
                print(f"   Fix: {issue['suggestion']}")
            print()

        return 1 if all_issues else 0


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Detect documentation drift in README")
    parser.add_argument(
        "project_dir",
        nargs="?",
        type=Path,
        default=Path("."),
        help="Project directory (default: current directory)",
    )
    parser.add_argument(
        "--readme", type=Path, help="README file path (default: README.md in project)"
    )
    parser.add_argument(
        "--fix", action="store_true", help="Attempt to auto-fix issues (experimental)"
    )

    args = parser.parse_args()

    sync = DocSync(args.project_dir)
    return sync.run(args.readme, args.fix)


if __name__ == "__main__":
    sys.exit(main())
