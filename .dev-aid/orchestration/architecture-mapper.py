#!/usr/bin/env python3
"""
Architecture Mapper - Visual Understanding

Generates Mermaid.js diagrams from codebase analysis to help developers
understand system relationships, data flow, and dependencies.
"""

import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set


class ArchitectureMapper:
    """Analyzes code and generates architecture diagrams"""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.output_dir = project_dir / "docs" / "architecture"
        self.classes = {}
        self.functions = {}
        self.imports = defaultdict(set)
        self.calls = defaultdict(set)

    def analyze_python_file(self, file_path: Path):
        """Analyze a Python file using AST"""
        try:
            code = file_path.read_text()
            tree = ast.parse(code, filename=str(file_path))

            module_name = file_path.stem

            for node in ast.walk(tree):
                # Track classes
                if isinstance(node, ast.ClassDef):
                    self.classes[f"{module_name}.{node.name}"] = {
                        "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                        "bases": [
                            base.id if isinstance(base, ast.Name) else str(base)
                            for base in node.bases
                        ],
                        "file": str(file_path.relative_to(self.project_dir)),
                    }

                # Track functions
                if isinstance(node, ast.FunctionDef) and not isinstance(node, ast.AsyncFunctionDef):
                    self.functions[f"{module_name}.{node.name}"] = {
                        "args": [arg.arg for arg in node.args.args],
                        "file": str(file_path.relative_to(self.project_dir)),
                    }

                # Track imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports[module_name].add(alias.name)

                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.imports[module_name].add(node.module)

        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")

    def analyze_typescript_file(self, file_path: Path):
        """Simple regex-based analysis for TypeScript/JavaScript"""
        try:
            code = file_path.read_text()
            module_name = file_path.stem

            # Find class declarations
            class_pattern = r"class\s+(\w+)(?:\s+extends\s+(\w+))?"
            for match in re.finditer(class_pattern, code):
                class_name = match.group(1)
                base_class = match.group(2)
                self.classes[f"{module_name}.{class_name}"] = {
                    "methods": [],
                    "bases": [base_class] if base_class else [],
                    "file": str(file_path.relative_to(self.project_dir)),
                }

            # Find function declarations
            func_pattern = r"(?:function|const|let|var)\s+(\w+)\s*=?\s*(?:async\s*)?\([^)]*\)"
            for match in re.finditer(func_pattern, code):
                func_name = match.group(1)
                self.functions[f"{module_name}.{func_name}"] = {
                    "args": [],
                    "file": str(file_path.relative_to(self.project_dir)),
                }

            # Find imports
            import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
            for match in re.finditer(import_pattern, code):
                imported_module = match.group(1)
                self.imports[module_name].add(imported_module)

        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")

    def scan_directory(self, directory: Path, extensions: List[str] = None):
        """Scan directory for code files"""
        if extensions is None:
            extensions = [".py", ".ts", ".tsx", ".js", ".jsx"]

        files_scanned = 0
        for ext in extensions:
            for file_path in directory.rglob(f"*{ext}"):
                # Skip common directories
                if any(
                    part in file_path.parts
                    for part in ["node_modules", "venv", ".venv", "__pycache__", "dist", "build"]
                ):
                    continue

                if ext == ".py":
                    self.analyze_python_file(file_path)
                elif ext in [".ts", ".tsx", ".js", ".jsx"]:
                    self.analyze_typescript_file(file_path)

                files_scanned += 1
                if files_scanned >= 100:  # Limit for performance
                    break

        return files_scanned

    def generate_class_diagram(self) -> str:
        """Generate Mermaid class diagram"""
        lines = ["```mermaid", "classDiagram"]

        for class_name, details in self.classes.items():
            # Add class
            simple_name = class_name.split(".")[-1]
            lines.append(f"    class {simple_name} {{")

            # Add methods
            for method in details["methods"][:10]:  # Limit to 10 methods
                lines.append(f"        +{method}()")

            lines.append("    }")

            # Add inheritance
            for base in details["bases"]:
                if base:
                    lines.append(f"    {base} <|-- {simple_name}")

        lines.append("```")
        return "\n".join(lines)

    def generate_dependency_diagram(self) -> str:
        """Generate Mermaid flowchart for module dependencies"""
        lines = ["```mermaid", "graph TD"]

        for module, imported_modules in self.imports.items():
            for imported in list(imported_modules)[:5]:  # Limit connections
                # Sanitize names for Mermaid
                safe_module = module.replace("-", "_").replace(".", "_")
                safe_imported = imported.replace("-", "_").replace(".", "_").replace("/", "_")
                lines.append(f"    {safe_module}[{module}] --> {safe_imported}[{imported}]")

        lines.append("```")
        return "\n".join(lines)

    def generate_component_diagram(self) -> str:
        """Generate C4 component diagram"""
        lines = ["```mermaid", "C4Component"]
        lines.append("    title Component Diagram")
        lines.append("")

        # Group by directory
        components = defaultdict(list)
        for class_name, details in self.classes.items():
            file_path = Path(details["file"])
            component = file_path.parts[0] if len(file_path.parts) > 1 else "core"
            components[component].append(class_name.split(".")[-1])

        for component, classes in list(components.items())[:10]:  # Limit components
            class_list = ", ".join(classes[:3])
            lines.append(f'    Component({component}, "{component}", "Contains: {class_list}")')

        lines.append("```")
        return "\n".join(lines)

    def generate_report(self, diagram_type: str = "all") -> str:
        """Generate markdown report with diagrams"""
        report = ["# Architecture Diagram", ""]
        report.append(f"**Generated from:** `{self.project_dir}`")
        report.append(
            f"**Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report.append("")

        stats = [
            "## Statistics",
            "",
            f"- **Classes:** {len(self.classes)}",
            f"- **Functions:** {len(self.functions)}",
            f"- **Modules with imports:** {len(self.imports)}",
            "",
        ]
        report.extend(stats)

        if diagram_type in ["all", "class"]:
            report.append("## Class Diagram")
            report.append("")
            report.append(self.generate_class_diagram())
            report.append("")

        if diagram_type in ["all", "dependency"]:
            report.append("## Module Dependencies")
            report.append("")
            report.append(self.generate_dependency_diagram())
            report.append("")

        if diagram_type in ["all", "component"]:
            report.append("## Component Overview")
            report.append("")
            report.append(self.generate_component_diagram())
            report.append("")

        return "\n".join(report)

    def run(
        self,
        target: Optional[Path] = None,
        diagram_type: str = "all",
        output_file: Optional[Path] = None,
    ):
        """Main execution"""
        print("🔍 Analyzing codebase...")

        # Determine target
        if target is None:
            target = self.project_dir

        if target.is_file():
            # Analyze single file
            if target.suffix == ".py":
                self.analyze_python_file(target)
            elif target.suffix in [".ts", ".tsx", ".js", ".jsx"]:
                self.analyze_typescript_file(target)
            files_scanned = 1
        else:
            # Scan directory
            files_scanned = self.scan_directory(target)

        print(f"✅ Scanned {files_scanned} files")
        print(f"   Found {len(self.classes)} classes, {len(self.functions)} functions")

        # Generate report
        print("\n🎨 Generating diagrams...")
        report = self.generate_report(diagram_type)

        # Write output
        if output_file is None:
            output_file = self.output_dir / "generated-diagram.md"

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report)

        print(f"✅ Generated: {output_file}")
        print(f"   Size: {len(report)} chars")
        print("\n📊 Diagram types included:")
        if diagram_type == "all":
            print("   - Class diagram")
            print("   - Module dependencies")
            print("   - Component overview")
        else:
            print(f"   - {diagram_type.title()} diagram")

        return 0


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate architecture diagrams from codebase")
    parser.add_argument(
        "target",
        nargs="?",
        type=Path,
        help="File or directory to analyze (default: current directory)",
    )
    parser.add_argument(
        "-t",
        "--type",
        choices=["all", "class", "dependency", "component"],
        default="all",
        help="Diagram type to generate",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (default: docs/architecture/generated-diagram.md)",
    )

    args = parser.parse_args()

    # Default to current directory
    target = args.target if args.target else Path(".")
    project_dir = target if target.is_dir() else target.parent

    mapper = ArchitectureMapper(project_dir)
    return mapper.run(target, args.type, args.output)


if __name__ == "__main__":
    sys.exit(main())
