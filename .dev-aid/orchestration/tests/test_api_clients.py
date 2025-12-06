"""
Tests for API clients
"""

import pytest
from unittest.mock import Mock, patch

from router.api_clients import Message, APIResponse, AnthropicClient, create_client, APIClientError


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

    def test_calculate_cost(self, mock_api_key, mock_model_config):
        """Test cost calculation"""
        client = AnthropicClient(mock_api_key, mock_model_config)

        cost = client.calculate_cost(input_tokens=1000000, output_tokens=1000000)

        # $3 per 1M input + $15 per 1M output = $18
        assert cost == 18.0

    def test_cost_calculation_fractional(self, mock_api_key, mock_model_config):
        """Test cost calculation with fractional millions"""
        client = AnthropicClient(mock_api_key, mock_model_config)

        # 500k input (0.5M) and 200k output (0.2M)
        cost = client.calculate_cost(input_tokens=500000, output_tokens=200000)

        # $3 * 0.5 + $15 * 0.2 = $1.5 + $3.0 = $4.5
        assert cost == 4.5

    @patch("router.api_clients.anthropic")
    def test_send_request_error_handling(self, mock_anthropic, mock_api_key, mock_model_config):
        """Test that errors don't leak API details"""
        # Mock anthropic to raise an exception
        mock_anthropic.Anthropic.return_value.messages.create.side_effect = Exception(
            "API key invalid: sk-ant-secret-key"
        )

        client = AnthropicClient(mock_api_key, mock_model_config)

        messages = [Message(role="user", content="test")]

        # Should raise our safe error, not the raw exception
        with pytest.raises(APIClientError, match="Failed to communicate"):
            client.send_request(messages, "claude-sonnet-4")


class TestCreateClient:
    """Test client factory function"""

    def test_create_anthropic_client(self, mock_api_key, mock_model_config):
        """Test creating Anthropic client"""
        client = create_client("anthropic", mock_api_key, mock_model_config)
        assert isinstance(client, AnthropicClient)

    def test_create_unsupported_provider(self, mock_api_key, mock_model_config):
        """Test creating client for unsupported provider"""
        with pytest.raises(ValueError, match="Unsupported provider"):
            create_client("unsupported", mock_api_key, mock_model_config)

    def test_create_client_case_insensitive(self, mock_api_key, mock_model_config):
        """Test that provider name is case-insensitive"""
        client = create_client("ANTHROPIC", mock_api_key, mock_model_config)
        assert isinstance(client, AnthropicClient)
