"""
Unit Tests for Authentication Detection Module

Tests session-based and API key authentication for all providers:
- Claude (session tokens and API keys)
- Gemini (ADC and API keys)
- OpenAI (API keys only)
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from router.auth_detector import AuthCredentials, AuthDetector

# Skip marker for tests that use Unix-specific permissions
skip_on_windows = pytest.mark.skipif(
    sys.platform == "win32", reason="Unix file permissions not available on Windows"
)


class TestAuthCredentials:
    """Test AuthCredentials dataclass"""

    def test_auth_credentials_creation(self):
        """Test creating AuthCredentials"""
        auth = AuthCredentials(
            provider="claude",
            auth_type="session",
            credentials={"session_token": "sk-test-123"},
            source="~/.config/claude/config.json",
        )

        assert auth.provider == "claude"
        assert auth.auth_type == "session"
        assert auth.credentials["session_token"] == "sk-test-123"
        assert auth.source == "~/.config/claude/config.json"


class TestClaudeAuthDetection:
    """Test Claude authentication detection"""

    def test_detect_claude_session_token(self, tmp_path):
        """Test detecting Claude session token from config.json"""
        # Create mock Claude config
        claude_config_dir = tmp_path / ".config" / "claude"
        claude_config_dir.mkdir(parents=True)
        config_file = claude_config_dir / "config.json"

        config_data = {"sessionToken": "sk-ant-session-123"}
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Mock home directory
        with patch.object(Path, "home", return_value=tmp_path):
            detector = AuthDetector()
            auth = detector.detect_claude_auth()

            assert auth is not None
            assert auth.provider == "claude"
            assert auth.auth_type == "session"
            assert auth.credentials["session_token"] == "sk-ant-session-123"
            assert "config.json" in auth.source

    def test_detect_claude_session_token_alternative_key(self, tmp_path):
        """Test detecting Claude session token with alternative key name"""
        claude_config_dir = tmp_path / ".config" / "claude"
        claude_config_dir.mkdir(parents=True)
        config_file = claude_config_dir / "config.json"

        # Try different key names
        for key in ["session_token", "sessionKey", "session_key"]:
            config_data = {key: f"token-{key}"}
            with open(config_file, "w") as f:
                json.dump(config_data, f)

            with patch.object(Path, "home", return_value=tmp_path):
                detector = AuthDetector()
                auth = detector.detect_claude_auth()

                assert auth is not None
                assert auth.auth_type == "session"
                assert auth.credentials["session_token"] == f"token-{key}"

    def test_detect_claude_api_key_fallback(self, tmp_path):
        """Test falling back to Claude API key when no session found"""
        # No config file, but API key is set
        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-api-456"}):
                detector = AuthDetector()
                auth = detector.detect_claude_auth()

                assert auth is not None
                assert auth.provider == "claude"
                assert auth.auth_type == "api_key"
                assert auth.credentials["api_key"] == "sk-ant-api-456"
                assert "ANTHROPIC_API_KEY" in auth.source

    def test_detect_claude_no_auth(self, tmp_path):
        """Test when no Claude authentication is available"""
        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {}, clear=True):
                detector = AuthDetector()
                auth = detector.detect_claude_auth()

                assert auth is None

    def test_detect_claude_windows_path(self, tmp_path):
        """Test detecting Claude config from Windows AppData path"""
        appdata_dir = tmp_path / "AppData" / "Roaming" / "claude"
        appdata_dir.mkdir(parents=True)
        config_file = appdata_dir / "config.json"

        config_data = {"sessionToken": "sk-ant-windows-789"}
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        with patch.object(Path, "home", return_value=tmp_path):
            detector = AuthDetector()
            auth = detector.detect_claude_auth()

            assert auth is not None
            assert auth.auth_type == "session"
            assert auth.credentials["session_token"] == "sk-ant-windows-789"

    def test_detect_claude_invalid_json(self, tmp_path):
        """Test handling invalid JSON in Claude config"""
        claude_config_dir = tmp_path / ".config" / "claude"
        claude_config_dir.mkdir(parents=True)
        config_file = claude_config_dir / "config.json"

        # Write invalid JSON
        with open(config_file, "w") as f:
            f.write("{ invalid json }")

        # Should fall back to API key
        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-fallback"}):
                detector = AuthDetector()
                auth = detector.detect_claude_auth()

                assert auth is not None
                assert auth.auth_type == "api_key"


class TestGeminiAuthDetection:
    """Test Google/Gemini authentication detection"""

    def test_detect_gemini_adc(self, tmp_path):
        """Test detecting Google ADC credentials"""
        gcloud_dir = tmp_path / ".config" / "gcloud"
        gcloud_dir.mkdir(parents=True)
        adc_file = gcloud_dir / "application_default_credentials.json"

        adc_data = {
            "type": "authorized_user",
            "refresh_token": "refresh-token-123",
            "client_id": "client-id",
            "client_secret": "client-secret",
        }
        with open(adc_file, "w") as f:
            json.dump(adc_data, f)

        with patch.object(Path, "home", return_value=tmp_path):
            detector = AuthDetector()
            auth = detector.detect_gemini_auth()

            assert auth is not None
            assert auth.provider == "gemini"
            assert auth.auth_type == "adc"
            assert "application_default_credentials.json" in auth.source

    def test_detect_gemini_api_key_fallback(self, tmp_path):
        """Test falling back to Google API key when no ADC found"""
        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {"GOOGLE_API_KEY": "AIza-google-key"}):
                detector = AuthDetector()
                auth = detector.detect_gemini_auth()

                assert auth is not None
                assert auth.provider == "gemini"
                assert auth.auth_type == "api_key"
                assert auth.credentials["api_key"] == "AIza-google-key"
                assert "GOOGLE_API_KEY" in auth.source

    def test_detect_gemini_no_auth(self, tmp_path):
        """Test when no Gemini authentication is available"""
        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {}, clear=True):
                detector = AuthDetector()
                auth = detector.detect_gemini_auth()

                assert auth is None

    def test_detect_gemini_adc_service_account(self, tmp_path):
        """Test detecting Google ADC with service account"""
        gcloud_dir = tmp_path / ".config" / "gcloud"
        gcloud_dir.mkdir(parents=True)
        adc_file = gcloud_dir / "application_default_credentials.json"

        adc_data = {
            "type": "service_account",
            "project_id": "my-project",
            "private_key": "-----BEGIN PRIVATE KEY-----\n...",
        }
        with open(adc_file, "w") as f:
            json.dump(adc_data, f)

        with patch.object(Path, "home", return_value=tmp_path):
            detector = AuthDetector()
            auth = detector.detect_gemini_auth()

            assert auth is not None
            assert auth.auth_type == "adc"


class TestOpenAIAuthDetection:
    """Test OpenAI authentication detection"""

    def test_detect_openai_api_key(self, tmp_path):
        """Test detecting OpenAI API key"""
        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-openai-key-123"}):
                detector = AuthDetector()
                auth = detector.detect_openai_auth()

                assert auth is not None
                assert auth.provider == "openai"
                assert auth.auth_type == "api_key"
                assert auth.credentials["api_key"] == "sk-openai-key-123"
                assert "OPENAI_API_KEY" in auth.source

    def test_detect_openai_no_auth(self, tmp_path):
        """Test when no OpenAI authentication is available"""
        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {}, clear=True):
                detector = AuthDetector()
                auth = detector.detect_openai_auth()

                assert auth is None


class TestDetectAll:
    """Test detecting authentication for all providers"""

    def test_detect_all_providers(self, tmp_path):
        """Test detecting auth for all providers at once"""
        # Setup Claude config
        claude_config_dir = tmp_path / ".config" / "claude"
        claude_config_dir.mkdir(parents=True)
        with open(claude_config_dir / "config.json", "w") as f:
            json.dump({"sessionToken": "claude-session"}, f)

        # Setup Gemini ADC
        gcloud_dir = tmp_path / ".config" / "gcloud"
        gcloud_dir.mkdir(parents=True)
        with open(gcloud_dir / "application_default_credentials.json", "w") as f:
            json.dump({"type": "authorized_user", "refresh_token": "refresh"}, f)

        # Setup OpenAI API key
        env_vars = {"OPENAI_API_KEY": "sk-openai-key"}

        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, env_vars, clear=True):
                detector = AuthDetector()
                all_auth = detector.detect_all()

                assert "claude" in all_auth
                assert "gemini" in all_auth
                assert "openai" in all_auth

                assert all_auth["claude"] is not None
                assert all_auth["claude"].auth_type == "session"

                assert all_auth["gemini"] is not None
                assert all_auth["gemini"].auth_type == "adc"

                assert all_auth["openai"] is not None
                assert all_auth["openai"].auth_type == "api_key"

    def test_detect_all_no_auth(self, tmp_path):
        """Test when no authentication is available for any provider"""
        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {}, clear=True):
                detector = AuthDetector()
                all_auth = detector.detect_all()

                assert all_auth["claude"] is None
                assert all_auth["gemini"] is None
                assert all_auth["openai"] is None

    def test_detect_all_mixed_auth(self, tmp_path):
        """Test with some providers configured, some not"""
        # Only Claude has auth
        claude_config_dir = tmp_path / ".config" / "claude"
        claude_config_dir.mkdir(parents=True)
        with open(claude_config_dir / "config.json", "w") as f:
            json.dump({"sessionToken": "claude-only"}, f)

        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {}, clear=True):
                detector = AuthDetector()
                all_auth = detector.detect_all()

                assert all_auth["claude"] is not None
                assert all_auth["claude"].auth_type == "session"
                assert all_auth["gemini"] is None
                assert all_auth["openai"] is None


class TestKeyringSupport:
    """Test keyring/keychain integration"""

    @patch("router.auth_detector.KEYRING_AVAILABLE", True)
    @patch("router.auth_detector.keyring")
    def test_detect_claude_from_keyring(self, mock_keyring, tmp_path):
        """Test detecting Claude session token from system keychain"""
        # Mock keyring.get_password to return a token
        mock_keyring.get_password.return_value = "sk-ant-keychain-token-123"

        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {}, clear=True):
                detector = AuthDetector()
                auth = detector.detect_claude_auth()

                assert auth is not None
                assert auth.provider == "claude"
                assert auth.auth_type == "session"
                assert auth.credentials["session_token"] == "sk-ant-keychain-token-123"
                assert "keychain" in auth.source.lower()

                # Verify keyring was called with expected service/username pairs
                assert mock_keyring.get_password.called

    @patch("router.auth_detector.KEYRING_AVAILABLE", True)
    @patch("router.auth_detector.keyring")
    def test_keyring_fallback_when_no_token(self, mock_keyring, tmp_path):
        """Test that keyring returns None gracefully when no token found"""
        # Mock keyring to return None (no token found)
        mock_keyring.get_password.return_value = None

        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fallback-key"}):
                detector = AuthDetector()
                auth = detector.detect_claude_auth()

                # Should fall back to API key
                assert auth is not None
                assert auth.auth_type == "api_key"

    @patch("router.auth_detector.KEYRING_AVAILABLE", True)
    @patch("router.auth_detector.keyring")
    def test_keyring_handles_exceptions(self, mock_keyring, tmp_path):
        """Test that keyring exceptions are handled gracefully"""
        # Mock keyring to raise exception
        mock_keyring.get_password.side_effect = Exception("Keyring access denied")

        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fallback-key"}):
                detector = AuthDetector()
                auth = detector.detect_claude_auth()

                # Should fall back to API key despite keyring error
                assert auth is not None
                assert auth.auth_type == "api_key"

    @patch("router.auth_detector.KEYRING_AVAILABLE", False)
    def test_keyring_not_available(self, tmp_path):
        """Test behavior when keyring library is not installed"""
        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-api-key"}):
                detector = AuthDetector()
                auth = detector.detect_claude_auth()

                # Should work fine with API key even without keyring
                assert auth is not None
                assert auth.auth_type == "api_key"

    @patch("router.auth_detector.KEYRING_AVAILABLE", True)
    @patch("router.auth_detector.keyring")
    def test_keyring_priority_before_api_key(self, mock_keyring, tmp_path):
        """Test that keyring is checked before falling back to API key"""
        # Both keyring and API key available
        mock_keyring.get_password.return_value = "keychain-token"

        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-api-key"}):
                detector = AuthDetector()
                auth = detector.detect_claude_auth()

                # Should prefer keyring over API key
                assert auth.auth_type == "session"
                assert auth.credentials["session_token"] == "keychain-token"

    @patch("router.auth_detector.KEYRING_AVAILABLE", True)
    @patch("router.auth_detector.keyring")
    def test_keyring_ignores_short_tokens(self, mock_keyring, tmp_path):
        """Test that very short strings from keyring are ignored"""
        # Return a suspiciously short string
        mock_keyring.get_password.return_value = "short"

        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "proper-api-key"}):
                detector = AuthDetector()
                auth = detector.detect_claude_auth()

                # Should ignore short token and use API key
                assert auth.auth_type == "api_key"


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_config_file(self, tmp_path):
        """Test handling empty config file"""
        claude_config_dir = tmp_path / ".config" / "claude"
        claude_config_dir.mkdir(parents=True)
        config_file = claude_config_dir / "config.json"

        with open(config_file, "w") as f:
            f.write("")

        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {}, clear=True):
                detector = AuthDetector()
                auth = detector.detect_claude_auth()
                assert auth is None

    def test_config_with_no_session_key(self, tmp_path):
        """Test config file without session token keys"""
        claude_config_dir = tmp_path / ".config" / "claude"
        claude_config_dir.mkdir(parents=True)
        config_file = claude_config_dir / "config.json"

        config_data = {"someOtherKey": "value", "preferences": {}}
        with open(config_file, "w") as f:
            json.dump(config_data, f)

        with patch.object(Path, "home", return_value=tmp_path):
            with patch.dict(os.environ, {}, clear=True):
                detector = AuthDetector()
                auth = detector.detect_claude_auth()
                assert auth is None

    @skip_on_windows
    def test_permission_denied_on_config(self, tmp_path):
        """Test handling permission denied errors"""
        # Skip this test if running as root (root can read files with 000 permissions)
        if os.geteuid() == 0:
            pytest.skip("Cannot test permission denied when running as root")

        claude_config_dir = tmp_path / ".config" / "claude"
        claude_config_dir.mkdir(parents=True)
        config_file = claude_config_dir / "config.json"

        with open(config_file, "w") as f:
            json.dump({"sessionToken": "token"}, f)

        # Make file unreadable
        os.chmod(config_file, 0o000)

        try:
            with patch.object(Path, "home", return_value=tmp_path):
                with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fallback-key"}):
                    detector = AuthDetector()
                    auth = detector.detect_claude_auth()

                    # Should fall back to API key
                    assert auth is not None
                    assert auth.auth_type == "api_key"
        finally:
            # Restore permissions for cleanup
            os.chmod(config_file, 0o644)
