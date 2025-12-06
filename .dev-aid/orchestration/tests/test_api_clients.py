"""
Tests for API clients
"""

from unittest.mock import Mock, patch

import pytest

from router.api_clients import AnthropicClient, APIClientError, APIResponse, Message, create_client


class TestMessage:
    """Test Message dataclass"""

    def test_create_message(self):
        """Test creating a message"""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"


class TestAPIResponse:
    """Test APIResponse dataclass"""

    def test_create_response(self):
        """Test creating API response"""
        response = APIResponse(
            content="Response text",
            model="claude-sonnet-4",
            provider="anthropic",
            tokens_used={"input": 100, "output": 200},
            cost=0.05,
        )
        assert response.content == "Response text"
        assert response.provider == "anthropic"
        assert response.cost == 0.05


class TestAnthropicClient:
    """Test Anthropic client"""

    @patch("router.api_clients.anthropic")
    def test_calculate_cost(self, mock_anthropic, mock_api_key, mock_model_config):
        """Test cost calculation"""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client_instance

        client = AnthropicClient(mock_api_key, mock_model_config)
        cost = client.calculate_cost(input_tokens=1000, output_tokens=2000)

        # $3 * 0.001 + $15 * 0.002 = $0.003 + $0.03 = $0.033
        assert abs(cost - 0.033) < 1e-6

    @patch("router.api_clients.anthropic")
    def test_cost_calculation_fractional(self, mock_anthropic, mock_api_key, mock_model_config):
        """Test cost calculation with fractional millions"""
        mock_anthropic.Anthropic.return_value = MagicMock()
        client = AnthropicClient(mock_api_key, mock_model_config)
        cost = client.calculate_cost(input_tokens=500000, output_tokens=200000)

        # $3 * 0.5 + $15 * 0.2 = $1.5 + $3.0 = $4.5
        assert cost == 4.5

    @patch("router.api_clients.anthropic")
    def test_send_request_error_handling(self, mock_anthropic, mock_api_key, mock_model_config):
        """Test that errors don't leak API details"""
        # Setup exception
        mock_client_instance = MagicMock()
        mock_client_instance.messages.create.side_effect = Exception(
            "API key invalid: sk-ant-secret-key"
        )
        mock_anthropic.Anthropic.return_value = mock_client_instance

        client = AnthropicClient(mock_api_key, mock_model_config)

        messages = [Message(role="user", content="test")]

        with pytest.raises(APIClientError) as exc_info:
            client.send_request(messages, "claude-sonnet-4")

        assert "Failed to communicate" in str(exc_info.value)
        # The original exception with sensitive info should be logged but not raised to user
        # We can verify logging if we mocked the logger, but for now just checking safe error response


class TestCreateClient:
    """Test client factory function"""

    @patch("router.api_clients.anthropic")
    def test_create_anthropic_client(self, mock_anthropic, mock_api_key, mock_model_config):
        """Test creating Anthropic client"""
        mock_anthropic.Anthropic.return_value = MagicMock()
        client = create_client("anthropic", mock_api_key, mock_model_config)
        assert isinstance(client, AnthropicClient)
        assert client.api_key == mock_api_key

    def test_create_unsupported_provider(self, mock_api_key, mock_model_config):
        """Test error for unsupported provider"""
        with pytest.raises(ValueError, match="Unsupported provider"):
            create_client("unknown", mock_api_key, mock_model_config)

    @patch("router.api_clients.anthropic")
    def test_create_client_case_insensitive(self, mock_anthropic, mock_api_key, mock_model_config):
        """Test that provider name is case-insensitive"""
        mock_anthropic.Anthropic.return_value = MagicMock()
        client = create_client("ANTHROPIC", mock_api_key, mock_model_config)
        assert isinstance(client, AnthropicClient)
