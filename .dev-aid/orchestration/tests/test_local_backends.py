"""Tests for shared local_backends module"""

from unittest.mock import Mock, patch

from router.local_backends import (
    DEFAULT_PORTS,
    LOCAL_BACKENDS,
    BackendConfig,
    detect_available_backend,
)


class TestBackendConfig:
    """Tests for BackendConfig dataclass"""

    def test_create_config(self):
        """Test creating a backend config"""
        config = BackendConfig(name="test", port=1234, health_path="/health")
        assert config.name == "test"
        assert config.port == 1234
        assert config.health_path == "/health"


class TestLocalBackends:
    """Tests for LOCAL_BACKENDS constant"""

    def test_has_ollama(self):
        """Test Ollama is in backends"""
        names = [b.name for b in LOCAL_BACKENDS]
        assert "ollama" in names

    def test_has_lm_studio(self):
        """Test LM Studio is in backends"""
        names = [b.name for b in LOCAL_BACKENDS]
        assert "lm_studio" in names

    def test_has_llama_cpp(self):
        """Test llama.cpp is in backends"""
        names = [b.name for b in LOCAL_BACKENDS]
        assert "llama_cpp" in names


class TestDefaultPorts:
    """Tests for DEFAULT_PORTS dict"""

    def test_ollama_port(self):
        """Test Ollama default port"""
        assert DEFAULT_PORTS["ollama"] == 11434

    def test_lm_studio_port(self):
        """Test LM Studio default port"""
        assert DEFAULT_PORTS["lm_studio"] == 1234

    def test_llama_cpp_port(self):
        """Test llama.cpp default port"""
        assert DEFAULT_PORTS["llama_cpp"] == 8080


class TestDetectAvailableBackend:
    """Tests for detect_available_backend"""

    @patch("router.local_backends.requests.get")
    def test_detect_ollama(self, mock_get):
        """Test detecting Ollama"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = detect_available_backend()
        assert result is not None
        assert result["backend"] == "ollama"
        assert result["port"] == 11434

    @patch("router.local_backends.requests.get")
    def test_no_server_detected(self, mock_get):
        """Test when no server is running"""
        mock_get.side_effect = Exception("Connection refused")

        result = detect_available_backend()
        assert result is None

    @patch("router.local_backends.requests.get")
    def test_preferred_backend_checked_first(self, mock_get):
        """Test preferred backend is checked first"""
        call_order = []

        def side_effect(url, **kwargs):
            call_order.append(url)
            raise Exception("Not running")

        mock_get.side_effect = side_effect

        detect_available_backend(preferred="llama_cpp")

        # llama_cpp URL should be first
        assert "8080" in call_order[0]

    @patch("router.local_backends.requests.get")
    def test_custom_url(self, mock_get):
        """Test custom URL for backend"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = detect_available_backend(custom_urls={"ollama": "http://custom:9999/v1"})
        assert result is not None
        assert result["base_url"] == "http://custom:9999/v1"

    @patch("router.local_backends.requests.get")
    def test_timeout_handling(self, mock_get):
        """Test that timeouts are handled gracefully"""
        import requests as req

        mock_get.side_effect = req.exceptions.Timeout("timed out")

        result = detect_available_backend(timeout=0.1)
        assert result is None
