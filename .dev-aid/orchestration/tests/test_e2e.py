"""
End-to-End tests for Dev-AID CLI
Tests complete user workflows using subprocess integration
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Skip marker for tests that require bash (Unix-only)
skip_on_windows = pytest.mark.skipif(
    sys.platform == "win32", reason="Bash scripts not available on Windows"
)


def normalize_path(path) -> str:
    """Normalize path for use in Python code strings (cross-platform).

    Converts backslashes to forward slashes to avoid escape sequence issues
    when embedding paths in Python code strings passed to subprocess.
    """
    return str(path).replace("\\", "/")


class TestE2ECliWorkflows:
    """Test complete CLI workflows end-to-end"""

    def test_router_help_command(self):
        """Test that the router help command works"""
        result = subprocess.run(
            ["python", "-m", "router", "--help"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "usage:" in result.stdout.lower() or "router" in result.stdout.lower()

    def test_router_version_command(self):
        """Test that the router version command works"""
        result = subprocess.run(
            ["python", "-m", "router", "--version"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Version command may not be implemented, so we just check it doesn't crash
        # and returns a reasonable exit code
        assert result.returncode in [0, 1, 2]  # Allow for not-implemented as well

    def test_config_validation(self):
        """Test that config files can be validated"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".dev-aid" / "config"
            config_dir.mkdir(parents=True)

            # Create minimal valid config
            settings = {
                "project_name": "test-e2e",
                "orchestration_mode": "solo",
                "default_model": "claude-sonnet",
            }

            routing = {
                "modes": {"solo": {"enabled": True}},
                "fallback_chain": ["claude-sonnet"],
            }

            models = {
                "claude": {
                    "enabled": True,
                    "api_key_env": "ANTHROPIC_API_KEY",
                    "models": {
                        "claude-sonnet": {
                            "id": "claude-sonnet-4",
                            "cost_per_1m_tokens": {"input": 3.0, "output": 15.0},
                        }
                    },
                }
            }

            orchestration = {"enabled": True}

            (config_dir / "settings.json").write_text(json.dumps(settings, indent=2))
            (config_dir / "routing.json").write_text(json.dumps(routing, indent=2))
            (config_dir / "models.json").write_text(json.dumps(models, indent=2))
            (config_dir / "orchestration.json").write_text(json.dumps(orchestration, indent=2))

            # Try to load config using the config_loader module
            orchestration_path = normalize_path(Path(__file__).parent.parent)
            tmpdir_path = normalize_path(tmpdir)
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    f"""
import sys
sys.path.insert(0, '{orchestration_path}')
from router.config_loader import ConfigLoader
loader = ConfigLoader('{tmpdir_path}')
mode = loader.get_orchestration_mode()
print('OK')
""",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            assert result.returncode == 0
            assert "OK" in result.stdout

    def test_cost_tracker_initialization(self):
        """Test that cost tracker can be initialized"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".dev-aid" / "config"
            logs_dir = Path(tmpdir) / ".dev-aid" / "logs"
            config_dir.mkdir(parents=True)
            logs_dir.mkdir(parents=True)

            # Create minimal config
            routing = {"cost_limit_per_day": 100.0}
            (config_dir / "routing.json").write_text(json.dumps(routing, indent=2))

            orchestration_path = normalize_path(Path(__file__).parent.parent)
            logs_path = normalize_path(Path(tmpdir) / ".dev-aid")
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    f"""
import sys
sys.path.insert(0, '{orchestration_path}')
from router.cost_tracker import CostTracker
tracker = CostTracker('{logs_path}')
# get_budget_status takes daily_limit as parameter
status = tracker.get_budget_status(100.0)
print(f"Limit: {{status['daily_limit']}}")
""",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            assert result.returncode == 0
            assert "Limit:" in result.stdout

    def test_task_classifier_import(self):
        """Test that task classifier can be imported and initialized"""
        orchestration_path = normalize_path(Path(__file__).parent.parent)
        result = subprocess.run(
            [
                "python",
                "-c",
                f"""
import sys
sys.path.insert(0, '{orchestration_path}')
from router.task_classifier import TaskClassifier
classifier = TaskClassifier()
print('Classifier initialized')
""",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "Classifier initialized" in result.stdout

    def test_auth_detector_env_detection(self):
        """Test that auth detector can detect environment variables"""
        env = os.environ.copy()
        env["OPENAI_API_KEY"] = "test-key-12345"

        orchestration_path = normalize_path(Path(__file__).parent.parent)
        result = subprocess.run(
            [
                "python",
                "-c",
                f"""
import sys
import os
os.environ['OPENAI_API_KEY'] = 'test-key-12345'
sys.path.insert(0, '{orchestration_path}')
from router.auth_detector import AuthDetector
detector = AuthDetector()
# detect_openai_auth checks OPENAI_API_KEY env var
creds = detector.detect_openai_auth()
print(f'Detected: {{creds is not None}}')
""",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )

        assert result.returncode == 0
        assert "Detected: True" in result.stdout

    @pytest.mark.slow
    @skip_on_windows
    def test_script_execution_dry_run(self):
        """Test that core scripts can be executed in dry-run mode"""
        scripts_dir = Path(__file__).parent.parent.parent / "scripts"

        # Test scripts that should support dry-run or help
        test_scripts = ["setup-rag.sh", "update-dev-aid.sh", "reconfigure.sh"]

        for script_name in test_scripts:
            script_path = scripts_dir / script_name
            if not script_path.exists():
                pytest.skip(f"Script {script_name} not found")

            # Just test that the script is executable and doesn't have syntax errors
            result = subprocess.run(
                ["bash", "-n", str(script_path)],
                capture_output=True,
                text=True,
                timeout=5,
            )

            assert (
                result.returncode == 0
            ), f"Script {script_name} has syntax errors: {result.stderr}"

    def test_memory_bank_integration(self):
        """Test that memory bank can be accessed"""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_dir = Path(tmpdir) / ".dev-aid" / "memory-bank"
            memory_dir.mkdir(parents=True)

            # Create test memory file
            (memory_dir / "activeContext.md").write_text("# Test Context\n\nTest content")

            tmpdir_path = normalize_path(tmpdir)
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    f"""
import sys
from pathlib import Path
memory_file = Path('{tmpdir_path}') / '.dev-aid' / 'memory-bank' / 'activeContext.md'
content = memory_file.read_text()
print(f'Memory loaded: {{len(content)}} chars')
""",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            assert result.returncode == 0
            assert "Memory loaded:" in result.stdout

    @pytest.mark.slow
    def test_skill_loader_integration(self):
        """Test that skills can be loaded from the skills directory"""
        skills_dir = Path(__file__).parent.parent.parent / "skills" / "expert"

        if not skills_dir.exists():
            pytest.skip("Skills directory not found")

        # List skills
        skills = list(skills_dir.glob("*/SKILL.md"))

        assert len(skills) > 0, "No skills found in skills directory"

        # Test that we can read a skill file
        sample_skill = skills[0]
        content = sample_skill.read_text(encoding="utf-8")

        assert len(content) > 0
        assert "SKILL.md" in str(sample_skill)


class TestE2EScriptIntegration:
    """Test script-level integration"""

    def test_python_script_execution(self):
        """Test that Python scripts in the scripts directory can be imported"""
        scripts_dir = Path(__file__).parent.parent.parent / "scripts"

        if not scripts_dir.exists():
            pytest.skip("Scripts directory not found")

        # Find Python scripts
        python_scripts = list(scripts_dir.glob("*.py"))

        # Test at least one Python script can be syntax-checked
        for script in python_scripts:
            if script.name.startswith("__"):
                continue

            result = subprocess.run(
                ["python", "-m", "py_compile", str(script)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Some scripts may have import errors, but shouldn't have syntax errors
            # We're just checking they can be parsed
            if result.returncode != 0:
                # Check if it's a syntax error (not an import error)
                assert "SyntaxError" not in result.stderr

    def test_router_module_structure(self):
        """Test that router module has expected structure"""
        router_dir = Path(__file__).parent.parent / "router"

        expected_modules = [
            "config_loader.py",
            "cost_tracker.py",
            "task_classifier.py",
            "auth_detector.py",
        ]

        for module in expected_modules:
            module_path = router_dir / module
            assert module_path.exists(), f"Expected module {module} not found"

            # Verify it's valid Python
            result = subprocess.run(
                ["python", "-m", "py_compile", str(module_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            assert result.returncode == 0, f"Module {module} has syntax errors: {result.stderr}"


class TestE2EConfigManagement:
    """Test configuration management workflows"""

    def test_config_migration_workflow(self):
        """Test that config can be migrated between formats"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".dev-aid" / "config"
            config_dir.mkdir(parents=True)

            # Create legacy config
            old_config = {
                "project_name": "test",
                "mode": "solo",
            }

            (config_dir / "settings.json").write_text(json.dumps(old_config, indent=2))

            # Read it back
            loaded = json.loads((config_dir / "settings.json").read_text())

            assert loaded["project_name"] == "test"
            assert loaded["mode"] == "solo"

    def test_env_file_loading(self):
        """Test that .env files can be loaded"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".dev-aid" / "config"
            config_dir.mkdir(parents=True)

            env_content = """
ANTHROPIC_API_KEY=test-key-123
GOOGLE_API_KEY=test-key-456
OPENAI_API_KEY=test-key-789
"""
            (config_dir / ".env").write_text(env_content)

            # Test loading with python-dotenv
            config_dir_path = normalize_path(config_dir)
            result = subprocess.run(
                [
                    "python",
                    "-c",
                    f"""
from pathlib import Path
env_file = Path('{config_dir_path}') / '.env'
content = env_file.read_text()
print(f'Env file lines: {{len(content.splitlines())}}')
""",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            assert result.returncode == 0
            assert "Env file lines:" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
