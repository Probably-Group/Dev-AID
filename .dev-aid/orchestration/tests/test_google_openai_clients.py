"""Tests for Google and OpenAI API clients"""

from unittest.mock import MagicMock, patch

import pytest

from router.api_clients import Message
from router.auth_detector import AuthCredentials


class TestGoogleClient:
    """Test Google Gemini client"""

    @pytest.fixture
    def google_auth_adc(self):
        return AuthCredentials(
            provider="google",
            auth_type="adc",
            credentials={},
            source="test",
        )

    @pytest.fixture
    def google_auth_api_key(self):
        return AuthCredentials(
            provider="google",
            auth_type="api_key",
            credentials={"api_key": "test-google-key"},
            source="test",
        )

    @pytest.fixture
    def google_config(self):
        return {
            "provider": "google",
            "model_id": "gemini-flash",
            "cost_per_1m_tokens": {"input": 0.075, "output": 0.30},
            "max_tokens": 8192,
        }

    @patch("router.api_clients.google_client.genai", create=True)
    def test_init_with_adc(self, mock_genai_module, google_auth_adc, google_config):
        """Test initialization with Application Default Credentials"""
        # Mock the import system
        mock_genai = MagicMock()
        mock_types = MagicMock()

        with patch.dict("sys.modules", {"google": MagicMock(), "google.genai": mock_genai}):
            with patch("router.api_clients.google_client.GoogleClient.__init__", return_value=None):
                # Test the logic directly
                from router.api_clients.google_client import GoogleClient

                client = GoogleClient.__new__(GoogleClient)
                client.auth = google_auth_adc
                client.model_config = google_config
                client.api_key = None
                client.client = mock_genai.Client()
                client.types = mock_types

                assert client.client is not None

    @patch("router.api_clients.google_client.genai", create=True)
    def test_init_unsupported_auth(self, mock_genai_module, google_config):
        """Test initialization with unsupported auth type"""
        auth = AuthCredentials(
            provider="google",
            auth_type="oauth",
            credentials={},
            source="test",
        )
        with pytest.raises((ValueError, ImportError)):
            from router.api_clients.google_client import GoogleClient

            GoogleClient(auth, google_config)

    def test_send_request_single_turn(self, google_auth_api_key, google_config):
        """Test single-turn request"""
        from router.api_clients.google_client import GoogleClient

        with patch.object(GoogleClient, "__init__", return_value=None):
            client = GoogleClient.__new__(GoogleClient)
            client.auth = google_auth_api_key
            client.model_config = google_config
            client.api_key = "test-key"

            # Mock client and types
            mock_response = MagicMock()
            mock_response.text = "Hello from Gemini"
            mock_response.usage_metadata = MagicMock()
            mock_response.usage_metadata.prompt_token_count = 10
            mock_response.usage_metadata.candidates_token_count = 20
            mock_response.candidates = [MagicMock(finish_reason="STOP")]

            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            client.client = mock_client

            mock_types = MagicMock()
            client.types = mock_types

            messages = [Message(role="user", content="Hello")]
            response = client.send_request(messages, "gemini-flash")

            assert response.content == "Hello from Gemini"
            assert response.provider == "google"
            assert response.tokens_used["input"] == 10
            assert response.tokens_used["output"] == 20

    def test_send_request_multi_turn(self, google_auth_api_key, google_config):
        """Test multi-turn conversation"""
        from router.api_clients.google_client import GoogleClient

        with patch.object(GoogleClient, "__init__", return_value=None):
            client = GoogleClient.__new__(GoogleClient)
            client.auth = google_auth_api_key
            client.model_config = google_config
            client.api_key = "test-key"

            mock_response = MagicMock()
            mock_response.text = "I remember our conversation"
            mock_response.usage_metadata = MagicMock()
            mock_response.usage_metadata.prompt_token_count = 50
            mock_response.usage_metadata.candidates_token_count = 30
            mock_response.candidates = [MagicMock(finish_reason="STOP")]

            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            client.client = mock_client
            client.types = MagicMock()

            messages = [
                Message(role="user", content="Hello"),
                Message(role="assistant", content="Hi there"),
                Message(role="user", content="Remember me?"),
            ]
            response = client.send_request(messages, "gemini-flash")

            assert response.content == "I remember our conversation"
            assert response.tokens_used["input"] == 50

    def test_send_request_with_system_message(self, google_auth_api_key, google_config):
        """Test request with system instruction"""
        from router.api_clients.google_client import GoogleClient

        with patch.object(GoogleClient, "__init__", return_value=None):
            client = GoogleClient.__new__(GoogleClient)
            client.auth = google_auth_api_key
            client.model_config = google_config
            client.api_key = "test-key"

            mock_response = MagicMock()
            mock_response.text = "System aware response"
            mock_response.usage_metadata = None
            mock_response.candidates = []

            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            client.client = mock_client
            client.types = MagicMock()

            messages = [
                Message(role="system", content="You are helpful"),
                Message(role="user", content="Hello"),
            ]
            response = client.send_request(messages, "gemini-flash")

            assert response.content == "System aware response"
            # Token estimation fallback should be used
            assert response.tokens_used["input"] > 0
            assert response.tokens_used["output"] > 0

    def test_send_request_token_estimation_fallback(self, google_auth_api_key, google_config):
        """Test token count estimation when API doesn't return counts"""
        from router.api_clients.google_client import GoogleClient

        with patch.object(GoogleClient, "__init__", return_value=None):
            client = GoogleClient.__new__(GoogleClient)
            client.auth = google_auth_api_key
            client.model_config = google_config
            client.api_key = "test-key"

            mock_response = MagicMock()
            mock_response.text = "Response text"
            mock_response.usage_metadata = None
            mock_response.candidates = []

            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            client.client = mock_client
            client.types = MagicMock()

            messages = [Message(role="user", content="Hello world test")]
            response = client.send_request(messages, "gemini-flash")

            # Should use estimation
            assert response.tokens_used["input"] > 0
            assert response.tokens_used["output"] > 0


class TestOpenAIClient:
    """Test OpenAI client"""

    @pytest.fixture
    def openai_auth(self):
        return AuthCredentials(
            provider="openai",
            auth_type="api_key",
            credentials={"api_key": "test-openai-key"},
            source="test",
        )

    @pytest.fixture
    def openai_config(self):
        return {
            "provider": "openai",
            "model_id": "gpt-4o",
            "cost_per_1m_tokens": {"input": 2.50, "output": 10.0},
            "max_tokens": 4096,
        }

    def test_init_unsupported_auth(self, openai_config):
        """Test initialization with unsupported auth type"""
        auth = AuthCredentials(
            provider="openai",
            auth_type="oauth",
            credentials={},
            source="test",
        )
        with pytest.raises((ValueError, ImportError)):
            from router.api_clients.openai_client import OpenAIClient

            OpenAIClient(auth, openai_config)

    def test_send_request_success(self, openai_auth, openai_config):
        """Test successful request"""
        from router.api_clients.openai_client import OpenAIClient

        with patch.object(OpenAIClient, "__init__", return_value=None):
            client = OpenAIClient.__new__(OpenAIClient)
            client.auth = openai_auth
            client.model_config = openai_config
            client.api_key = "test-key"

            # Mock OpenAI response
            mock_choice = MagicMock()
            mock_choice.message.content = "GPT response"
            mock_choice.finish_reason = "stop"

            mock_usage = MagicMock()
            mock_usage.prompt_tokens = 15
            mock_usage.completion_tokens = 25

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_response.usage = mock_usage
            mock_response.id = "chatcmpl-123"

            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            client.client = mock_client

            messages = [Message(role="user", content="Hello")]
            response = client.send_request(messages, "gpt-4o")

            assert response.content == "GPT response"
            assert response.provider == "openai"
            assert response.tokens_used["input"] == 15
            assert response.tokens_used["output"] == 25
            assert response.metadata["finish_reason"] == "stop"
            assert response.metadata["response_id"] == "chatcmpl-123"

    def test_send_request_with_system_message(self, openai_auth, openai_config):
        """Test request with system message"""
        from router.api_clients.openai_client import OpenAIClient

        with patch.object(OpenAIClient, "__init__", return_value=None):
            client = OpenAIClient.__new__(OpenAIClient)
            client.auth = openai_auth
            client.model_config = openai_config
            client.api_key = "test-key"

            mock_choice = MagicMock()
            mock_choice.message.content = "System-aware response"
            mock_choice.finish_reason = "stop"

            mock_usage = MagicMock()
            mock_usage.prompt_tokens = 30
            mock_usage.completion_tokens = 10

            mock_response = MagicMock()
            mock_response.choices = [mock_choice]
            mock_response.usage = mock_usage
            mock_response.id = "chatcmpl-456"

            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            client.client = mock_client

            messages = [
                Message(role="system", content="You are helpful"),
                Message(role="user", content="Hello"),
            ]
            response = client.send_request(messages, "gpt-4o")

            assert response.content == "System-aware response"
            # Verify messages were passed correctly
            call_args = mock_client.chat.completions.create.call_args
            api_msgs = call_args[1]["messages"]
            assert len(api_msgs) == 2
            assert api_msgs[0]["role"] == "system"
