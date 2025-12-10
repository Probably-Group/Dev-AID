#!/usr/bin/env python3
"""
Unit tests for CI Generator

Tests the CI/CD workflow generator including:
- Project type detection (Node.js, Python, Rust, Go, etc.)
- Package manager detection
- Docker detection
- Workflow generation with template substitution
- Optimization flag behavior
"""

import tempfile
import unittest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import module with hyphen in name using importlib
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "ci_generator", Path(__file__).parent.parent / "ci-generator.py"
)
ci_generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci_generator)
CIGenerator = ci_generator.CIGenerator


class TestProjectDetection(unittest.TestCase):
    """Test project type and configuration detection"""

    def setUp(self):
        """Create temporary project directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_detect_nodejs_with_npm(self):
        """Test Node.js project detection with npm"""
        # Create package.json
        (self.project_dir / "package.json").write_text('{"name": "test-project"}')

        generator = CIGenerator(self.project_dir)
        context = generator.detect_project_type()

        self.assertEqual(context["language"], "nodejs")
        self.assertEqual(context["package_manager"], "npm")
        self.assertEqual(context["commands"]["install"], "npm ci")
        self.assertEqual(context["commands"]["test"], "npm test")

    def test_detect_nodejs_with_yarn(self):
        """Test Node.js project detection with Yarn"""
        (self.project_dir / "package.json").write_text('{"name": "test-project"}')
        (self.project_dir / "yarn.lock").touch()

        generator = CIGenerator(self.project_dir)
        context = generator.detect_project_type()

        self.assertEqual(context["language"], "nodejs")
        self.assertEqual(context["package_manager"], "yarn")
        self.assertEqual(context["commands"]["install"], "yarn install")

    def test_detect_nodejs_with_pnpm(self):
        """Test Node.js project detection with pnpm"""
        (self.project_dir / "package.json").write_text('{"name": "test-project"}')
        (self.project_dir / "pnpm-lock.yaml").touch()

        generator = CIGenerator(self.project_dir)
        context = generator.detect_project_type()

        self.assertEqual(context["language"], "nodejs")
        self.assertEqual(context["package_manager"], "pnpm")
        self.assertEqual(context["commands"]["install"], "pnpm install")

    def test_detect_nodejs_with_bun(self):
        """Test Node.js project detection with Bun"""
        (self.project_dir / "package.json").write_text('{"name": "test-project"}')
        (self.project_dir / "bun.lockb").touch()

        generator = CIGenerator(self.project_dir)
        context = generator.detect_project_type()

        self.assertEqual(context["language"], "nodejs")
        self.assertEqual(context["package_manager"], "bun")
        self.assertEqual(context["commands"]["install"], "bun install")
        self.assertEqual(context["commands"]["test"], "bun test")

    def test_detect_typescript(self):
        """Test TypeScript detection"""
        (self.project_dir / "package.json").write_text('{"name": "test-project"}')
        (self.project_dir / "tsconfig.json").write_text("{}")

        generator = CIGenerator(self.project_dir)
        context = generator.detect_project_type()

        self.assertEqual(context["language"], "nodejs")
        self.assertIn("type_check", context["commands"])
        self.assertEqual(context["commands"]["type_check"], "npx tsc --noEmit")

    def test_detect_nodejs_lint_script(self):
        """Test Node.js lint script detection"""
        (self.project_dir / "package.json").write_text(
            '{"name": "test-project", "scripts": {"lint": "eslint ."}}'
        )

        generator = CIGenerator(self.project_dir)
        context = generator.detect_project_type()

        self.assertEqual(context["language"], "nodejs")
        self.assertIn("lint", context["commands"])
        self.assertIn("lint", context["commands"]["lint"])

    def test_detect_python_with_pip(self):
        """Test Python project detection with pip"""
        (self.project_dir / "requirements.txt").write_text("pytest==7.4.0")
        # Create empty pyproject.toml to avoid FileNotFoundError
        (self.project_dir / "pyproject.toml").write_text("")

        generator = CIGenerator(self.project_dir)
        context = generator.detect_project_type()

        self.assertEqual(context["language"], "python")
        self.assertEqual(context["package_manager"], "pip")
        self.assertEqual(context["commands"]["install"], "pip install -r requirements.txt")

    def test_detect_python_with_poetry(self):
        """Test Python project detection with Poetry"""
        (self.project_dir / "pyproject.toml").write_text("[tool.poetry]\nname = 'test-project'")

        generator = CIGenerator(self.project_dir)
        context = generator.detect_project_type()

        self.assertEqual(context["language"], "python")
        self.assertEqual(context["package_manager"], "poetry")
        self.assertEqual(context["commands"]["install"], "poetry install")

    def test_detect_rust(self):
        """Test Rust project detection"""
        (self.project_dir / "Cargo.toml").write_text("[package]\nname = 'test-project'")

        generator = CIGenerator(self.project_dir)
        context = generator.detect_project_type()

        self.assertEqual(context["language"], "rust")
        self.assertEqual(context["package_manager"], "cargo")
        self.assertEqual(context["commands"]["build"], "cargo build")

    def test_detect_go(self):
        """Test Go project detection"""
        (self.project_dir / "go.mod").write_text("module test-project")

        generator = CIGenerator(self.project_dir)
        context = generator.detect_project_type()

        self.assertEqual(context["language"], "go")
        self.assertEqual(context["commands"]["build"], "go build ./...")

    def test_detect_docker(self):
        """Test Docker detection"""
        (self.project_dir / "package.json").write_text('{"name": "test-project"}')
        (self.project_dir / "Dockerfile").write_text("FROM node:18")

        generator = CIGenerator(self.project_dir)
        context = generator.detect_project_type()

        self.assertTrue(context["has_docker"])

    def test_detect_no_language(self):
        """Test detection when no supported language found"""
        generator = CIGenerator(self.project_dir)
        context = generator.detect_project_type()

        self.assertIsNone(context["language"])


class TestWorkflowGeneration(unittest.TestCase):
    """Test workflow YAML generation"""

    def setUp(self):
        """Create temporary project and template directories"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir)
        self.templates_dir = Path(self.temp_dir) / "templates" / "ci"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Create a simple Node.js project
        (self.project_dir / "package.json").write_text('{"name": "test-project"}')

    def tearDown(self):
        """Clean up temporary directory"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_generate_workflow_basic(self):
        """Test basic workflow generation"""
        # Create a simple template
        template = """name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: {{INSTALL_COMMAND}}
      - run: {{TEST_COMMAND}}
"""
        (self.templates_dir / "nodejs.yml").write_text(template)

        generator = CIGenerator(self.project_dir)
        generator.templates_dir = self.templates_dir
        context = generator.detect_project_type()
        workflow = generator.generate_workflow(context)

        self.assertIn("npm ci", workflow)
        self.assertIn("npm test", workflow)
        self.assertNotIn("{{INSTALL_COMMAND}}", workflow)
        self.assertNotIn("{{TEST_COMMAND}}", workflow)

    def test_generate_workflow_with_optimize(self):
        """Test workflow generation with optimization"""
        # Create both standard and optimized templates
        standard_template = """name: CI
steps:
  - run: {{INSTALL_COMMAND}}
"""
        optimized_template = """name: CI (Optimized)
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
steps:
  - run: {{INSTALL_COMMAND}}
"""
        (self.templates_dir / "nodejs.yml").write_text(standard_template)
        optimized_dir = self.templates_dir / "optimized"
        optimized_dir.mkdir(exist_ok=True)
        (optimized_dir / "nodejs.yml").write_text(optimized_template)

        generator = CIGenerator(self.project_dir)
        generator.templates_dir = self.templates_dir
        context = generator.detect_project_type()

        # Test standard template
        workflow_standard = generator.generate_workflow(context, optimize=False)
        self.assertNotIn("Optimized", workflow_standard)
        self.assertNotIn("concurrency", workflow_standard)

        # Test optimized template
        workflow_optimized = generator.generate_workflow(context, optimize=True)
        self.assertIn("Optimized", workflow_optimized)
        self.assertIn("concurrency", workflow_optimized)

    def test_generate_workflow_docker_conditional(self):
        """Test Docker conditional template handling"""
        template = """name: CI
steps:
  - run: {{INSTALL_COMMAND}}
  {{#DOCKER}}
  - name: Build Docker image
    run: docker build .
  {{/DOCKER}}
"""
        (self.templates_dir / "nodejs.yml").write_text(template)

        generator = CIGenerator(self.project_dir)
        generator.templates_dir = self.templates_dir

        # Test without Docker
        context = generator.detect_project_type()
        workflow_no_docker = generator.generate_workflow(context)
        self.assertNotIn("docker build", workflow_no_docker)
        self.assertNotIn("{{#DOCKER}}", workflow_no_docker)

        # Test with Docker
        (self.project_dir / "Dockerfile").write_text("FROM node:18")
        context = generator.detect_project_type()
        workflow_with_docker = generator.generate_workflow(context)
        self.assertIn("docker build", workflow_with_docker)
        self.assertNotIn("{{#DOCKER}}", workflow_with_docker)

    def test_generate_workflow_missing_template(self):
        """Test error handling for missing template"""
        generator = CIGenerator(self.project_dir)
        generator.templates_dir = self.templates_dir
        context = generator.detect_project_type()

        with self.assertRaises(ValueError) as cm:
            generator.generate_workflow(context)

        self.assertIn("No template found", str(cm.exception))

    def test_generate_workflow_missing_language(self):
        """Test error handling for missing language"""
        generator = CIGenerator(self.project_dir)
        generator.templates_dir = self.templates_dir
        context = {"language": None}

        with self.assertRaises(ValueError) as cm:
            generator.generate_workflow(context)

        self.assertIn("Could not detect project language", str(cm.exception))

    def test_generate_workflow_fallback_to_standard(self):
        """Test fallback to standard template when optimized missing"""
        # Only create standard template
        template = """name: CI
steps:
  - run: {{INSTALL_COMMAND}}
"""
        (self.templates_dir / "nodejs.yml").write_text(template)

        generator = CIGenerator(self.project_dir)
        generator.templates_dir = self.templates_dir
        context = generator.detect_project_type()

        # Request optimized but should fallback to standard
        workflow = generator.generate_workflow(context, optimize=True)
        self.assertIn("npm ci", workflow)


class TestTemplateSubstitution(unittest.TestCase):
    """Test template placeholder substitution"""

    def test_all_placeholders_replaced(self):
        """Test that all placeholders are properly replaced"""
        temp_dir = tempfile.mkdtemp()
        project_dir = Path(temp_dir)
        templates_dir = Path(temp_dir) / "templates" / "ci"
        templates_dir.mkdir(parents=True, exist_ok=True)

        # Create project
        (project_dir / "package.json").write_text('{"name": "test"}')

        # Create template with all placeholders
        template = """
{{PACKAGE_MANAGER}}
{{INSTALL_COMMAND}}
{{BUILD_COMMAND}}
{{TEST_COMMAND}}
{{LINT_COMMAND}}
{{TYPE_CHECK_COMMAND}}
"""
        (templates_dir / "nodejs.yml").write_text(template)

        generator = CIGenerator(project_dir)
        generator.templates_dir = templates_dir
        context = generator.detect_project_type()
        workflow = generator.generate_workflow(context)

        # Verify no placeholders remain
        self.assertNotIn("{{", workflow)
        self.assertNotIn("}}", workflow)

        # Verify actual commands present
        self.assertIn("npm", workflow)

        import shutil

        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
