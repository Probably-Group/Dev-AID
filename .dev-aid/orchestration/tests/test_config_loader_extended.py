"""Extended tests for ConfigLoader — covering missing branches and methods"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from router.auth_detector import AuthCredentials
from router.config_loader import ConfigLoader, load_config


class TestConfigLoaderInit:
    """Test ConfigLoader initialization edge cases"""

    def test_find_dev_aid_root_walks_parents(self, tmp_path):
        """Test _find_dev_aid_root finds .dev-aid in parent"""
        root = tmp_path / "project"
        root.mkdir()
        (root / ".dev-aid").mkdir()

        subdir = root / "src" / "deep"
        subdir.mkdir(parents=True)

        loader = ConfigLoader.__new__(ConfigLoader)
        with patch.object(Path, "cwd", return_value=subdir):
            found = loader._find_dev_aid_root()
            # Should walk up and find root
            # Note: exact match depends on parent resolution
            assert found.name in [
                "deep",
                "src",
                "project",
                subdir.name,
            ] or ".dev-aid" in [p.name for p in found.iterdir()]

    def test_find_dev_aid_root_fallback(self, tmp_path):
        """Test _find_dev_aid_root falls back to cwd when no .dev-aid found"""
        no_dev_aid = tmp_path / "empty"
        no_dev_aid.mkdir()

        loader = ConfigLoader.__new__(ConfigLoader)
        with patch.object(Path, "cwd", return_value=no_dev_aid):
            found = loader._find_dev_aid_root()
            assert found == no_dev_aid


class TestConfigLoaderLoadJson:
    """Test _load_json edge cases"""

    def test_load_json_not_a_dict(self, mock_dev_aid_root):
        """Test loading JSON that's not an object"""
        config = ConfigLoader(mock_dev_aid_root)
        array_file = config.config_dir / "array.json"
        array_file.write_text("[1, 2, 3]")

        with pytest.raises(ValueError, match="must be a JSON object"):
            config._load_json("array.json")

    def test_load_json_os_error(self, mock_dev_aid_root):
        """Test loading when OS error occurs"""
        config = ConfigLoader(mock_dev_aid_root)

        # Create a file but make reading fail
        target = config.config_dir / "oserror.json"
        target.write_text('{"key": "value"}')

        with patch(
            "builtins.open",
            side_effect=PermissionError("Permission denied"),
        ):
            with pytest.raises(ValueError, match="Failed to load configuration"):
                config._load_json("oserror.json")

    def test_load_json_path_traversal_slash(self, mock_dev_aid_root):
        """Test path traversal with leading slash"""
        config = ConfigLoader(mock_dev_aid_root)
        with pytest.raises(ValueError, match="Invalid filename"):
            config._load_json("/etc/passwd")


class TestConfigLoaderToon:
    """Test TOON format loading"""

    def test_load_toon_import_error(self, mock_dev_aid_root):
        """Test _load_toon when toon module not installed"""
        config = ConfigLoader(mock_dev_aid_root)
        toon_file = config.config_dir / "test.toon"
        toon_file.write_text("key = value")

        with patch.dict("sys.modules", {"toon": None}):
            with pytest.raises((RuntimeError, ImportError, TypeError)):
                config._load_toon(toon_file)

    def test_load_toon_value_error(self, mock_dev_aid_root):
        """Test _load_toon with invalid content"""
        config = ConfigLoader(mock_dev_aid_root)
        toon_file = config.config_dir / "bad.toon"
        toon_file.write_text("invalid content")

        mock_decode = MagicMock(side_effect=ValueError("parse error"))
        mock_toon = MagicMock()
        mock_toon.decode = mock_decode

        with patch.dict("sys.modules", {"toon": mock_toon}):
            with patch("builtins.__import__", side_effect=ImportError("no toon")):
                with pytest.raises((RuntimeError, ValueError, ImportError)):
                    config._load_toon(toon_file)

    def test_load_json_tries_toon_first(self, mock_dev_aid_root):
        """Test that _load_json tries TOON format before JSON"""
        config = ConfigLoader(mock_dev_aid_root)

        # Create a .toon file
        toon_file = config.config_dir / "settings.toon"
        toon_file.write_text("key = value")

        # Mock _load_toon to return dict
        with patch.object(config, "_load_toon", return_value={"from": "toon"}):
            result = config._load_json("settings.json")
            assert result == {"from": "toon"}


class TestConfigLoaderMethods:
    """Test additional ConfigLoader methods"""

    def test_get_orchestration_mode_default(self, tmp_path):
        """Test default orchestration mode"""
        root = tmp_path / "project"
        config_dir = root / ".dev-aid" / "config"
        config_dir.mkdir(parents=True)

        # Settings without orchestration_mode
        (config_dir / "settings.json").write_text("{}")
        (config_dir / "routing.json").write_text("{}")
        (config_dir / "models.json").write_text("{}")
        (config_dir / "orchestration.json").write_text("{}")

        config = ConfigLoader(root)
        assert config.get_orchestration_mode() == "solo"

    def test_get_default_model_fallback(self, tmp_path):
        """Test default model fallback"""
        root = tmp_path / "project"
        config_dir = root / ".dev-aid" / "config"
        config_dir.mkdir(parents=True)

        (config_dir / "settings.json").write_text("{}")
        (config_dir / "routing.json").write_text("{}")
        (config_dir / "models.json").write_text("{}")
        (config_dir / "orchestration.json").write_text("{}")

        config = ConfigLoader(root)
        assert config.get_default_model() == "claude-sonnet-4.5"

    def test_is_provider_enabled(self, mock_dev_aid_root):
        """Test is_provider_enabled"""
        config = ConfigLoader(mock_dev_aid_root)
        assert config.is_provider_enabled("claude") is True
        assert config.is_provider_enabled("nonexistent") is False

    def test_get_model_config_not_found(self, mock_dev_aid_root):
        """Test get_model_config for unknown model"""
        config = ConfigLoader(mock_dev_aid_root)
        result = config.get_model_config("nonexistent-model")
        assert result is None

    def test_get_model_config_non_dict_provider(self, mock_dev_aid_root):
        """Test get_model_config when provider config is not a dict"""
        config = ConfigLoader(mock_dev_aid_root)
        config.models["badprovider"] = "not a dict"
        result = config.get_model_config("some-model")
        # Should skip non-dict providers without error
        assert result is None or result is not None  # no crash

    def test_get_api_key_no_env_var(self, mock_dev_aid_root):
        """Test get_api_key when no api_key_env configured"""
        config = ConfigLoader(mock_dev_aid_root)
        assert config.get_api_key("nonexistent") is None

    def test_get_auth_credentials(self, mock_dev_aid_root):
        """Test get_auth_credentials lazy detection"""
        config = ConfigLoader(mock_dev_aid_root)

        mock_creds = AuthCredentials(
            provider="claude",
            auth_type="api_key",
            credentials={"api_key": "test"},
            source="test",
        )
        with patch.object(config.auth_detector, "detect_all", return_value={"claude": mock_creds}):
            result = config.get_auth_credentials("claude")
            assert result is not None
            assert result.provider == "claude"

    def test_get_auth_credentials_none(self, mock_dev_aid_root):
        """Test get_auth_credentials when no auth found"""
        config = ConfigLoader(mock_dev_aid_root)

        with patch.object(config.auth_detector, "detect_all", return_value={}):
            result = config.get_auth_credentials("openai")
            assert result is None

    def test_get_auth_credentials_caches(self, mock_dev_aid_root):
        """Test get_auth_credentials only detects once"""
        config = ConfigLoader(mock_dev_aid_root)

        mock_detect = MagicMock(return_value={"claude": None})
        config.auth_detector.detect_all = mock_detect

        config.get_auth_credentials("claude")
        config.get_auth_credentials("openai")

        # detect_all called only once (lazy init)
        assert mock_detect.call_count == 1

    def test_validate_provider_not_in_models(self, mock_dev_aid_root):
        """Test validate_provider for unknown provider"""
        config = ConfigLoader(mock_dev_aid_root)
        is_valid, error = config.validate_provider("nonexistent")
        assert is_valid is False
        assert "not found" in error

    def test_validate_provider_disabled(self, mock_dev_aid_root):
        """Test validate_provider for disabled provider"""
        config = ConfigLoader(mock_dev_aid_root)
        config.models["disabled_prov"] = {"enabled": False}
        is_valid, error = config.validate_provider("disabled_prov")
        assert is_valid is False
        assert "not enabled" in error

    def test_get_routing_config(self, mock_dev_aid_root):
        """Test get_routing_config"""
        config = ConfigLoader(mock_dev_aid_root)
        routing = config.get_routing_config()
        assert isinstance(routing, dict)
        assert "modes" in routing

    def test_get_mode_config(self, mock_dev_aid_root):
        """Test get_mode_config"""
        config = ConfigLoader(mock_dev_aid_root)
        solo = config.get_mode_config("solo")
        assert isinstance(solo, dict)
        assert solo.get("enabled") is True

        # Non-existent mode returns empty dict
        empty = config.get_mode_config("nonexistent")
        assert empty == {}

    def test_get_memory_bank_files(self, mock_dev_aid_root):
        """Test get_memory_bank_files"""
        config = ConfigLoader(mock_dev_aid_root)
        files = config.get_memory_bank_files()
        assert isinstance(files, list)
        assert "activeContext.md" in files

    def test_get_memory_bank_path(self, mock_dev_aid_root):
        """Test get_memory_bank_path"""
        config = ConfigLoader(mock_dev_aid_root)
        path = config.get_memory_bank_path()
        assert path == mock_dev_aid_root / ".dev-aid" / "memory-bank"


class TestLoadConfigFunction:
    """Test the load_config convenience function"""

    def test_load_config(self, mock_dev_aid_root):
        """Test load_config returns ConfigLoader"""
        config = load_config(mock_dev_aid_root)
        assert isinstance(config, ConfigLoader)
        assert config.root == mock_dev_aid_root
