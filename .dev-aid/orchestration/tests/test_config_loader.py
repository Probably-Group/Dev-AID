"""
Tests for ConfigLoader
"""

import json
import pytest
from pathlib import Path

from router.config_loader import ConfigLoader


class TestConfigLoader:
    """Test configuration loading"""

    def test_load_valid_config(self, mock_dev_aid_root):
        """Test loading valid configuration"""
        config = ConfigLoader(mock_dev_aid_root)

        assert config.root == mock_dev_aid_root
        assert config.get_orchestration_mode() == "solo"
        assert config.get_default_model() == "claude-sonnet"
        assert "claude" in config.get_enabled_providers()

    def test_path_validation(self, mock_dev_aid_root):
        """Test path validation in config loader"""
        config = ConfigLoader(mock_dev_aid_root)

        # Try to load with path traversal
        with pytest.raises(ValueError, match="Invalid filename"):
            config._load_json("../../etc/passwd")

    def test_load_nonexistent_file(self, mock_dev_aid_root):
        """Test loading nonexistent file"""
        config = ConfigLoader(mock_dev_aid_root)

        with pytest.raises(FileNotFoundError):
            config._load_json("nonexistent.json")

    def test_load_invalid_json(self, mock_dev_aid_root):
        """Test loading invalid JSON"""
        config = ConfigLoader(mock_dev_aid_root)

        # Create invalid JSON file
        bad_file = config.config_dir / "bad.json"
        bad_file.write_text("{invalid json")

        with pytest.raises(ValueError, match="Invalid JSON"):
            config._load_json("bad.json")

    def test_get_api_key(self, mock_dev_aid_root, monkeypatch):
        """Test API key retrieval"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")

        config = ConfigLoader(mock_dev_aid_root)
        key = config.get_api_key("claude")

        assert key == "test-key-123"

    def test_validate_provider_success(self, mock_dev_aid_root, monkeypatch):
        """Test successful provider validation"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")

        config = ConfigLoader(mock_dev_aid_root)
        is_valid, error = config.validate_provider("claude")

        assert is_valid
        assert error == ""

    def test_validate_provider_missing_key(self, mock_dev_aid_root, monkeypatch):
        """Test provider validation with missing API key"""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        config = ConfigLoader(mock_dev_aid_root)
        is_valid, error = config.validate_provider("claude")

        assert not is_valid
        assert "API key not set" in error

    def test_get_model_config(self, mock_dev_aid_root):
        """Test retrieving model configuration"""
        config = ConfigLoader(mock_dev_aid_root)
        model_config = config.get_model_config("claude-sonnet")

        assert model_config is not None
        assert model_config["provider"] == "claude"

    def test_get_fallback_chain(self, mock_dev_aid_root):
        """Test fallback chain retrieval"""
        config = ConfigLoader(mock_dev_aid_root)
        fallback = config.get_fallback_chain()

        assert isinstance(fallback, list)
        assert len(fallback) > 0

    def test_get_cost_limit(self, mock_dev_aid_root):
        """Test cost limit retrieval"""
        config = ConfigLoader(mock_dev_aid_root)
        limit = config.get_cost_limit()

        assert limit == 100.0

    def test_safe_path_validation(self, mock_dev_aid_root):
        """Test safe path validation method"""
        config = ConfigLoader(mock_dev_aid_root)

        # Valid path within config_dir
        valid_path = config.config_dir / "settings.json"
        safe_path = config._validate_safe_path(valid_path, config.config_dir)
        assert safe_path.exists()

        # Invalid path outside config_dir
        invalid_path = mock_dev_aid_root / "outside.txt"
        with pytest.raises(ValueError, match="traversal"):
            config._validate_safe_path(invalid_path, config.config_dir)


class TestConfigAutodetection:
    """Test automatic Dev-AID root detection"""

    def test_find_dev_aid_root_current(self, mock_dev_aid_root, monkeypatch):
        """Test finding Dev-AID root in current directory"""
        monkeypatch.chdir(mock_dev_aid_root)

        config = ConfigLoader()
        assert config.root == mock_dev_aid_root

    def test_find_dev_aid_root_parent(self, mock_dev_aid_root, monkeypatch):
        """Test finding Dev-AID root in parent directory"""
        subdir = mock_dev_aid_root / "subdir"
        subdir.mkdir()
        monkeypatch.chdir(subdir)

        config = ConfigLoader()
        assert config.root == mock_dev_aid_root
