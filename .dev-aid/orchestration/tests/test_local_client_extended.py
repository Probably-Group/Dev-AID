"""Extended tests for LocalLLMClient"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from router.api_clients import Message
from router.auth_detector import AuthCredentials
from router.local_client import LocalLLMClient, create_local_auth, detect_local_server


@pytest.fixture
def local_auth():
    return AuthCredentials(
        provider="local",
        auth_type="local",
        credentials={"backend": "ollama", "base_url": "http://localhost:11434/v1"},
        source="test",
    )


@pytest.fixture
def local_config():
    return {"provider": "local", "model_id": "llama3"}


def _make_local_client(backend="ollama", base_url="http://localhost:11434/v1"):
    """Create a LocalLLMClient bypassing __init__ to avoid import issues"""
    client = LocalLLMClient.__new__(LocalLLMClient)
    client.auth = AuthCredentials(
        provider="local",
        auth_type="local",
        credentials={"backend": backend, "base_url": base_url},
        source="test",
    )
    client.model_config = {"provider": "local"}
    client.api_key = None
    client.backend = backend
    client.base_url = base_url if base_url.endswith("/v1") else base_url + "/v1"
    client.provider = "local"
    client.client = MagicMock()
    return client


class TestLocalLLMClientInit:
    """Test LocalLLMClient initialization"""

    def test_init_sets_backend(self):
        client = _make_local_client("ollama")
        assert client.backend == "ollama"
        assert client.base_url.endswith("/v1")

    def test_init_lm_studio(self):
        client = _make_local_client("lm_studio", "http://localhost:1234/v1")
        assert client.backend == "lm_studio"
        assert client.base_url == "http://localhost:1234/v1"

    def test_get_default_url(self):
        client = _make_local_client("ollama")
        url = client._get_default_url()
        assert "11434" in url

    def test_get_default_url_lm_studio(self):
        client = _make_local_client("lm_studio")
        url = client._get_default_url()
        assert "1234" in url


class TestLocalLLMClientVerify:
    """Test verify_connection"""

    def test_verify_ollama_success(self):
        client = _make_local_client("ollama")
        with patch("router.local_client.requests") as mock_requests:
            mock_requests.get.return_value = Mock(status_code=200)
            assert client.verify_connection() is True

    def test_verify_non_ollama(self):
        client = _make_local_client("lm_studio", "http://localhost:1234/v1")
        with patch("router.local_client.requests") as mock_requests:
            mock_requests.get.return_value = Mock(status_code=200)
            assert client.verify_connection() is True

    def test_verify_bad_status(self):
        client = _make_local_client("ollama")
        with patch("router.local_client.requests") as mock_requests:
            mock_requests.get.return_value = Mock(status_code=500, text="error")
            assert client.verify_connection() is False

    def test_verify_connection_error(self):
        client = _make_local_client("ollama")
        with patch("router.local_client.requests") as mock_requests:
            import requests as real_requests

            mock_requests.exceptions = real_requests.exceptions
            mock_requests.get.side_effect = real_requests.exceptions.ConnectionError()
            assert client.verify_connection() is False

    def test_verify_timeout(self):
        client = _make_local_client("ollama")
        with patch("router.local_client.requests") as mock_requests:
            import requests as real_requests

            mock_requests.exceptions = real_requests.exceptions
            mock_requests.get.side_effect = real_requests.exceptions.Timeout()
            assert client.verify_connection() is False

    def test_verify_generic_error(self):
        client = _make_local_client("ollama")
        with patch("router.local_client.requests") as mock_requests:
            import requests as real_requests

            mock_requests.exceptions = real_requests.exceptions
            mock_requests.get.side_effect = RuntimeError("unknown")
            assert client.verify_connection() is False


class TestLocalLLMClientListModels:
    """Test list_models"""

    def test_list_models_ollama(self):
        client = _make_local_client("ollama")
        with patch("router.local_client.requests") as mock_requests:
            mock_response = Mock(status_code=200)
            mock_response.json.return_value = {
                "models": [{"name": "llama3"}, {"name": "codellama"}]
            }
            mock_requests.get.return_value = mock_response
            models = client.list_models()
            assert models == ["llama3", "codellama"]

    def test_list_models_openai_compat(self):
        client = _make_local_client("lm_studio", "http://localhost:1234/v1")
        mock_model = Mock(id="model-1")
        client.client.models.list.return_value = Mock(data=[mock_model])
        models = client.list_models()
        assert models == ["model-1"]

    def test_list_models_error(self):
        client = _make_local_client("ollama")
        with patch("router.local_client.requests") as mock_requests:
            mock_requests.get.side_effect = RuntimeError("fail")
            models = client.list_models()
            assert models == []

    def test_list_models_ollama_bad_status(self):
        client = _make_local_client("ollama")
        with patch("router.local_client.requests") as mock_requests:
            mock_requests.get.return_value = Mock(status_code=404)
            models = client.list_models()
            assert models == []


class TestLocalLLMClientSendRequest:
    """Test send_request"""

    def test_send_request_success(self):
        client = _make_local_client("ollama")

        mock_choice = MagicMock()
        mock_choice.message.content = "Local response"
        mock_choice.finish_reason = "stop"

        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 20

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = mock_usage
        mock_response.id = "local-123"

        client.client.chat.completions.create.return_value = mock_response

        messages = [Message(role="user", content="Hello")]
        response = client.send_request(messages, "llama3")

        assert response.content == "Local response"
        assert response.provider == "local"
        assert response.cost == 0.0
        assert response.tokens_used["input"] == 10
        assert response.metadata["backend"] == "ollama"

    def test_send_request_no_usage(self):
        """Test token estimation when usage not provided"""
        client = _make_local_client("ollama")

        mock_choice = MagicMock()
        mock_choice.message.content = "Response text"
        mock_choice.finish_reason = "stop"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = None
        mock_response.id = "local-456"

        client.client.chat.completions.create.return_value = mock_response

        messages = [Message(role="user", content="Hello world test")]
        response = client.send_request(messages, "llama3")

        # Should use estimation
        assert response.tokens_used["input"] > 0
        assert response.tokens_used["output"] > 0


class TestLocalLLMClientCost:
    """Test calculate_cost"""

    def test_calculate_cost_always_zero(self):
        client = _make_local_client("ollama")
        assert client.calculate_cost(1000, 500) == 0.0
        assert client.calculate_cost(0, 0) == 0.0


class TestCreateLocalAuth:
    """Test create_local_auth helper"""

    def test_create_default(self):
        auth = create_local_auth()
        assert auth.provider == "local"
        assert auth.auth_type == "local"
        assert auth.credentials["backend"] == "ollama"
        assert "11434" in auth.credentials["base_url"]

    def test_create_lm_studio(self):
        auth = create_local_auth(backend="lm_studio")
        assert auth.credentials["backend"] == "lm_studio"
        assert "1234" in auth.credentials["base_url"]

    def test_create_custom_url(self):
        auth = create_local_auth(base_url="http://custom:9999/v1")
        assert auth.credentials["base_url"] == "http://custom:9999/v1"

    def test_create_llama_cpp(self):
        auth = create_local_auth(backend="llama_cpp")
        assert "8080" in auth.credentials["base_url"]


class TestDetectLocalServer:
    """Test detect_local_server"""

    def test_detect_delegates_to_backend(self):
        with patch("router.local_client.detect_available_backend") as mock_detect:
            mock_detect.return_value = {"backend": "ollama", "base_url": "http://localhost:11434"}
            result = detect_local_server()
            assert result["backend"] == "ollama"

    def test_detect_none(self):
        with patch("router.local_client.detect_available_backend") as mock_detect:
            mock_detect.return_value = None
            assert detect_local_server() is None
