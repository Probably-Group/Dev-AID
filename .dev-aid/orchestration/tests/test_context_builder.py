"""
Unit tests for context_builder.py
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from router.context_builder import ContextBuilder, DevAIDContext


class TestContextBuilder:
    """Test suite for ContextBuilder"""

    @pytest.fixture
    def mock_config_loader(self, tmp_path):
        """Create a mock config loader"""
        config = Mock()
        config.root = tmp_path
        config.get_memory_bank_path.return_value = tmp_path / ".dev-aid" / "memory-bank"
        config.settings = {"project_name": "test-project"}
        config.get_orchestration_mode.return_value = "solo"
        config.get_enabled_providers.return_value = ["claude"]
        config.get_memory_bank_files.return_value = ["activeContext.md"]
        return config

    @pytest.fixture
    def context_builder(self, mock_config_loader):
        """Create a ContextBuilder instance"""
        return ContextBuilder(mock_config_loader)

    def test_build_context_basic(self, context_builder):
        """Test basic context building"""
        context = context_builder.build_context(include_memory=False)

        assert isinstance(context, DevAIDContext)
        assert context.project_info["name"] == "test-project"
        assert context.project_info["orchestration_mode"] == "solo"
        assert context.memory_bank == {}

    def test_load_memory_bank(self, context_builder, tmp_path):
        """Test memory bank loading"""
        # Create test memory bank file
        memory_bank_dir = tmp_path / ".dev-aid" / "memory-bank"
        memory_bank_dir.mkdir(parents=True, exist_ok=True)

        test_file = memory_bank_dir / "activeContext.md"
        test_file.write_text("# Test Context\nThis is a test")

        memory_bank = context_builder._load_memory_bank()

        assert "activeContext.md" in memory_bank
        assert "Test Context" in memory_bank["activeContext.md"]

    def test_get_project_info(self, context_builder):
        """Test project info extraction"""
        project_info = context_builder._get_project_info()

        assert project_info["name"] == "test-project"
        assert project_info["orchestration_mode"] == "solo"
        assert "claude" in project_info["enabled_providers"]

    @patch("subprocess.check_output")
    def test_get_git_context_success(self, mock_subprocess, context_builder):
        """Test git context extraction when git is available"""
        mock_subprocess.side_effect = [
            "main\n",  # branch
            "abc123 Initial commit\n",  # last commit
            ""  # status (clean)
        ]

        git_context = context_builder._get_git_context()

        assert git_context is not None
        assert git_context["branch"] == "main"
        assert "Initial commit" in git_context["last_commit"]
        assert git_context["status"] == "(clean)"

    @patch("subprocess.check_output")
    def test_get_git_context_failure(self, mock_subprocess, context_builder):
        """Test git context when git is not available"""
        mock_subprocess.side_effect = FileNotFoundError()

        git_context = context_builder._get_git_context()

        assert git_context is None

    @patch("subprocess.check_output")
    def test_detect_active_skills(self, mock_subprocess, context_builder, tmp_path):
        """Test active skills detection"""
        # Create mock scripts
        orchestration_dir = tmp_path / ".dev-aid" / "orchestration"
        orchestration_dir.mkdir(parents=True, exist_ok=True)

        detect_script = orchestration_dir / "detect-context.sh"
        detect_script.write_text("#!/bin/bash\necho 'Python FastAPI'")
        detect_script.chmod(0o755)

        select_script = orchestration_dir / "select-skills.sh"
        select_script.write_text("#!/bin/bash\necho 'python\nfastapi\nbash-expert'")
        select_script.chmod(0o755)

        # Mock subprocess calls
        mock_subprocess.side_effect = [
            "Python FastAPI\n",  # detect-context output
            "python\nfastapi\nbash-expert\n"  # select-skills output
        ]

        skills = context_builder._detect_active_skills()

        assert skills is not None
        assert "python" in skills
        assert "fastapi" in skills
        assert "bash-expert" in skills

    def test_format_context_for_ai(self, context_builder):
        """Test context formatting for AI"""
        context = DevAIDContext(
            memory_bank={"activeContext.md": "# Test\nActive work"},
            project_info={"name": "test", "orchestration_mode": "solo", "enabled_providers": ["claude"]},
            git_context={"branch": "main", "last_commit": "abc123 Test", "status": "(clean)"},
            active_skills=["python", "fastapi"]
        )

        formatted = context_builder.format_context_for_ai(context)

        assert "Project Context" in formatted
        assert "test" in formatted
        assert "Active Skills" in formatted
        assert "python" in formatted
        assert "fastapi" in formatted
        assert "Git Context" in formatted
        assert "main" in formatted
        assert "Memory Bank" in formatted

    def test_get_minimal_context(self, context_builder, tmp_path):
        """Test minimal context retrieval"""
        # Create activeContext.md
        memory_bank_dir = tmp_path / ".dev-aid" / "memory-bank"
        memory_bank_dir.mkdir(parents=True, exist_ok=True)

        active_context = memory_bank_dir / "activeContext.md"
        active_context.write_text("# Current Sprint\nWorking on feature X")

        minimal = context_builder.get_minimal_context()

        assert "Current Sprint" in minimal
        assert "feature X" in minimal

    def test_validate_safe_path(self, context_builder, tmp_path):
        """Test path validation"""
        # Valid path
        safe_path = context_builder._validate_safe_path(tmp_path)
        assert safe_path.is_absolute()

        # Path with null bytes should raise
        with pytest.raises(ValueError):
            context_builder._validate_safe_path(Path("/tmp\x00/bad"))


class TestDevAIDContext:
    """Test DevAIDContext dataclass"""

    def test_context_creation(self):
        """Test creating DevAIDContext"""
        context = DevAIDContext(
            memory_bank={"test.md": "content"},
            project_info={"name": "test"},
            git_context=None,
            active_skills=["python"]
        )

        assert context.memory_bank == {"test.md": "content"}
        assert context.project_info == {"name": "test"}
        assert context.git_context is None
        assert context.active_skills == ["python"]

    def test_context_with_mcp(self):
        """Test DevAIDContext with MCP context"""
        context = DevAIDContext(
            memory_bank={},
            project_info={"name": "test"},
            mcp_context={"code_search": {"results": []}}
        )

        assert "code_search" in context.mcp_context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
