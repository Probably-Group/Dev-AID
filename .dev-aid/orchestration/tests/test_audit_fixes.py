"""
Tests for codebase audit fixes (security, code quality, type safety).

Covers:
- CWE-89: SQL injection prevention in data-factory.py
- CWE-22: Path traversal prevention in context_builder.py memory bank loader
- CWE-636: Silent exception handling fixes (cost_tracker, hardware_detector, mcp_registry)
- ModeConfigProtocol type safety in mode files
- validators.py is_relative_to fix
"""

import logging
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# CWE-89: SQL Injection Prevention — data-factory.py
# ---------------------------------------------------------------------------


class TestDataFactorySQLEscaping:
    """Tests for SQL escaping methods in DataFactory (CWE-89 fix)."""

    @pytest.fixture
    def factory(self):
        """Create DataFactory instance with deterministic seed."""
        import sys

        sys.path.insert(0, str(Path(__file__).parent.parent))
        from importlib import import_module

        mod = import_module("data-factory")
        return mod.DataFactory(seed=42)

    def test_sql_escape_single_quotes(self, factory: Any) -> None:
        """Single quotes in values must be doubled."""
        assert factory._sql_escape("O'Brien") == "O''Brien"

    def test_sql_escape_no_quotes(self, factory: Any) -> None:
        """Strings without quotes pass through unchanged."""
        assert factory._sql_escape("hello") == "hello"

    def test_sql_escape_multiple_quotes(self, factory: Any) -> None:
        """Multiple single quotes are all doubled."""
        assert factory._sql_escape("it's a 'test'") == "it''s a ''test''"

    def test_sql_identifier_valid(self, factory: Any) -> None:
        """Valid identifiers are quoted."""
        assert factory._sql_identifier("user_name") == '"user_name"'

    def test_sql_identifier_rejects_semicolon(self, factory: Any) -> None:
        """Identifiers with dangerous chars are rejected."""
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            factory._sql_identifier("table; DROP TABLE users--")

    def test_sql_identifier_rejects_spaces(self, factory: Any) -> None:
        """Identifiers with spaces are rejected."""
        with pytest.raises(ValueError, match="Invalid SQL identifier"):
            factory._sql_identifier("my table")

    def test_output_sql_escapes_values(self, factory: Any) -> None:
        """SQL output properly escapes string values."""
        records = [{"name": "O'Brien", "age": 30}]
        sql = factory.output_sql(records, table_name="users")
        assert "O''Brien" in sql
        assert "INSERT INTO" in sql

    def test_output_sql_handles_none(self, factory: Any) -> None:
        """NULL values are output as SQL NULL."""
        records = [{"name": "Alice", "email": None}]
        sql = factory.output_sql(records)
        assert "NULL" in sql

    def test_output_sql_handles_bool(self, factory: Any) -> None:
        """Boolean values are output as TRUE/FALSE."""
        records = [{"active": True, "deleted": False}]
        sql = factory.output_sql(records)
        assert "TRUE" in sql
        assert "FALSE" in sql

    def test_output_sql_empty_records(self, factory: Any) -> None:
        """Empty records list returns empty string."""
        assert factory.output_sql([]) == ""

    def test_output_sql_injection_attempt(self, factory: Any) -> None:
        """SQL injection in values is safely escaped."""
        records = [{"comment": "'; DROP TABLE users; --"}]
        sql = factory.output_sql(records)
        # The dangerous single quote should be escaped
        assert "'';" in sql
        assert "DROP TABLE" in sql  # String is preserved but escaped


# ---------------------------------------------------------------------------
# CWE-22: Path Traversal Prevention — context_builder.py memory bank
# ---------------------------------------------------------------------------


class TestMemoryBankPathTraversal:
    """Tests for path traversal prevention in ContextBuilder._load_memory_bank."""

    @pytest.fixture
    def mock_config(self, temp_dir: Path) -> MagicMock:
        """Create a mock config loader."""
        config = MagicMock()
        config.root = temp_dir
        config.settings = {"project_name": "test"}
        config.get_orchestration_mode.return_value = "solo"
        config.get_enabled_providers.return_value = ["claude"]
        config.get_on_demand_files.return_value = []
        config.get_standing_context_tokens.return_value = 1000

        memory_bank_dir = temp_dir / ".dev-aid" / "memory-bank"
        memory_bank_dir.mkdir(parents=True, exist_ok=True)
        config.get_memory_bank_path.return_value = memory_bank_dir

        return config

    @pytest.fixture
    def context_builder(self, mock_config: MagicMock) -> Any:
        """Create ContextBuilder with mocked config."""
        from router.context_builder import ContextBuilder

        return ContextBuilder(config_loader=mock_config)

    def test_normal_file_loads(self, context_builder: Any, mock_config: MagicMock) -> None:
        """Normal filenames are loaded successfully."""
        memory_dir = mock_config.get_memory_bank_path()
        (memory_dir / "context.md").write_text("# Context")
        mock_config.get_memory_bank_files.return_value = ["context.md"]

        result, _metadata = context_builder._load_memory_bank()
        assert "context.md" in result
        assert result["context.md"] == "# Context"

    def test_traversal_with_dotdot_blocked(
        self, context_builder: Any, mock_config: MagicMock
    ) -> None:
        """Filenames with '..' are blocked."""
        mock_config.get_memory_bank_files.return_value = ["../../etc/passwd"]

        result, _metadata = context_builder._load_memory_bank()
        assert len(result) == 0

    def test_absolute_path_blocked(self, context_builder: Any, mock_config: MagicMock) -> None:
        """Absolute filenames are blocked."""
        mock_config.get_memory_bank_files.return_value = ["/etc/passwd"]

        result, _metadata = context_builder._load_memory_bank()
        assert len(result) == 0

    def test_traversal_logged(
        self, context_builder: Any, mock_config: MagicMock, caplog: Any
    ) -> None:
        """Path traversal attempts are logged as warnings."""
        mock_config.get_memory_bank_files.return_value = ["../secret.txt"]

        with caplog.at_level(logging.WARNING):
            context_builder._load_memory_bank()

        assert any("unsafe memory bank filename" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# CWE-636: Silent Exception Handling Fixes
# ---------------------------------------------------------------------------


class TestCostTrackerLogging:
    """Tests that cost_tracker no longer silently swallows errors."""

    def test_get_recent_decisions_logs_io_error(self, temp_dir: Path, caplog: Any) -> None:
        """IOError in get_recent_decisions is logged, not silently swallowed."""
        from router.cost_tracker import CostTracker

        tracker = CostTracker(logs_dir=temp_dir)

        # Create a routing log with bad permissions (simulate IOError)
        log_file = temp_dir / "routing.log"
        log_file.write_text("some content")

        with patch("builtins.open", side_effect=IOError("permission denied")):
            with caplog.at_level(logging.DEBUG):
                result = tracker.get_recent_decisions()

        assert result == []
        assert any("Could not read routing decisions log" in r.message for r in caplog.records)


class TestHardwareDetectorExceptionNarrowing:
    """Tests that hardware_detector uses specific exception types."""

    def test_cpu_cores_logs_specific_error(self, caplog: Any) -> None:
        """CPU core detection failure is logged with specific exception."""
        from router.hardware_detector import HardwareDetector

        detector = HardwareDetector()

        with patch("router.hardware_detector.PSUTIL_AVAILABLE", True):
            with patch("router.hardware_detector.psutil") as mock_psutil:
                mock_psutil.cpu_count.side_effect = OSError("test error")

                with caplog.at_level(logging.DEBUG):
                    result = detector._detect_cpu_cores()

        assert result == 1
        assert any("CPU core detection failed" in r.message for r in caplog.records)

    def test_cpu_threads_logs_specific_error(self, caplog: Any) -> None:
        """CPU thread detection failure is logged with specific exception."""
        from router.hardware_detector import HardwareDetector

        detector = HardwareDetector()

        with patch("router.hardware_detector.PSUTIL_AVAILABLE", True):
            with patch("router.hardware_detector.psutil") as mock_psutil:
                mock_psutil.cpu_count.side_effect = AttributeError("test error")

                with caplog.at_level(logging.DEBUG):
                    result = detector._detect_cpu_threads()

        assert result == 1
        assert any("CPU thread detection failed" in r.message for r in caplog.records)


class TestMCPRegistryExceptionNarrowing:
    """Tests that mcp_registry uses specific exception types and logging."""

    def test_null_byte_in_config_path_rejected(self) -> None:
        """Config path with null bytes is rejected."""
        from router.mcp_registry import MCPRegistry

        with pytest.raises(ValueError, match="null bytes"):
            MCPRegistry(config_path="/tmp/test\0evil.json")

    def test_config_path_resolved_to_absolute(self, temp_dir: Path) -> None:
        """Config path is resolved to absolute path."""
        from router.mcp_registry import MCPRegistry

        config_path = str(temp_dir / "mcp-config.json")
        registry = MCPRegistry(config_path=config_path)
        assert Path(registry.config_path).is_absolute()

    def test_gemini_config_error_logged(self, temp_dir: Path, caplog: Any) -> None:
        """Gemini config read errors use logger.warning, not print()."""
        from router.mcp_registry import MCPRegistry

        registry = MCPRegistry(config_path=str(temp_dir / "mcp-config.json"))

        # Create invalid Gemini config
        gemini_path = temp_dir / "gemini-mcp.json"
        gemini_path.write_text("invalid json{{{")

        with patch("os.path.expanduser", return_value=str(gemini_path)):
            with patch("os.path.exists", return_value=True):
                with caplog.at_level(logging.WARNING):
                    registry._discover_gemini()

        # Verify logger was used (not print)
        assert any("Failed to read Gemini config" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# validators.py: is_relative_to fix
# ---------------------------------------------------------------------------


class TestValidatorsIsRelativeTo:
    """Tests that SafePath uses is_relative_to instead of startswith."""

    def test_prefix_collision_rejected(self, temp_dir: Path) -> None:
        """Prefix collision (e.g., /tmp/user vs /tmp/userX) is caught."""
        from pydantic import ValidationError

        from router.validators import SafePath

        # Create sibling directory that has base_dir as prefix
        base_dir = temp_dir / "mydir"
        base_dir.mkdir()
        sibling = temp_dir / "mydirX"
        sibling.mkdir()
        sibling_file = sibling / "secret.txt"
        sibling_file.write_text("secret")

        # This should be rejected — path resolves outside base_dir
        # We need a path that resolves to sibling_file when joined with base_dir
        # The `..` traversal is checked first, so we test the is_relative_to directly
        with pytest.raises(ValidationError, match="not within"):
            SafePath(path=str(sibling_file), base_dir=str(base_dir))


# ---------------------------------------------------------------------------
# ModeConfigProtocol type safety
# ---------------------------------------------------------------------------


class TestModeConfigProtocol:
    """Tests that ModeConfigProtocol is properly defined and structural."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """Protocol can be used with isinstance checks."""
        from router.modes._protocol import ModeConfigProtocol

        assert hasattr(ModeConfigProtocol, "__protocol_attrs__") or hasattr(
            ModeConfigProtocol, "__abstractmethods__"
        )

    def test_config_loader_satisfies_protocol(self, mock_dev_aid_root: Path) -> None:
        """Actual ConfigLoader satisfies ModeConfigProtocol."""
        from router.config_loader import ConfigLoader
        from router.modes._protocol import ModeConfigProtocol

        config = ConfigLoader(dev_aid_root=mock_dev_aid_root)
        assert isinstance(config, ModeConfigProtocol)

    def test_protocol_imported_from_modes_package(self) -> None:
        """Protocol is re-exported from modes/__init__.py."""
        from router.modes import ModeConfigProtocol

        assert ModeConfigProtocol is not None

    def test_solo_mode_init_signature(self) -> None:
        """SoloMode.__init__ accepts ModeConfigProtocol."""
        import inspect

        from router.modes.solo import SoloMode

        sig = inspect.signature(SoloMode.__init__)
        params = sig.parameters
        assert "config_loader" in params
        # The annotation should reference ModeConfigProtocol, not Any
        annotation = params["config_loader"].annotation
        assert (
            "ModeConfigProtocol" in str(annotation) or annotation.__name__ == "ModeConfigProtocol"
        )
