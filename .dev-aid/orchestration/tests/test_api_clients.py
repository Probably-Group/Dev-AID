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

    def test_create_system_message(self):
        """Test creating system message"""
        msg = Message(role="system", content="You are a helpful assistant")
        assert msg.role == "system"
        assert msg.content == "You are a helpful assistant"

    def test_create_assistant_message(self):
        """Test creating assistant message"""
        msg = Message(role="assistant", content="I can help you with that")
        assert msg.role == "assistant"


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

    def test_response_with_metadata(self):
        """Test creating response with additional metadata"""
        response = APIResponse(
            content="Test response",
            model="claude-3-opus",
            provider="anthropic",
            tokens_used={"input": 1000, "output": 500},
            cost=0.1,
            metadata={"stop_reason": "end_turn"},
        )
        assert response.metadata == {"stop_reason": "end_turn"}

    def test_response_tokens_used(self):
        """Test token usage tracking"""
        response = APIResponse(
            content="Test",
            model="claude-sonnet-4",
            provider="anthropic",
            tokens_used={"input": 250, "output": 750},
            cost=0.03,
        )
        assert response.tokens_used["input"] == 250
        assert response.tokens_used["output"] == 750


class TestAnthropicClient:
    """Test Anthropic client"""

    def test_init(self, mock_auth_credentials, mock_model_config):
        """Test client initialization"""
        client = AnthropicClient(mock_auth_credentials, mock_model_config)
        assert client.api_key == "test-api-key-1234567890"
        assert client.model_config == mock_model_config

    def test_calculate_cost(self, mock_auth_credentials, mock_model_config):
        """Test cost calculation"""
        client = AnthropicClient(mock_auth_credentials, mock_model_config)

        cost = client.calculate_cost(input_tokens=1000000, output_tokens=1000000)

        # $3 per 1M input + $15 per 1M output = $18
        assert cost == 18.0

    def test_cost_calculation_fractional(self, mock_auth_credentials, mock_model_config):
        """Test cost calculation with fractional millions"""
        client = AnthropicClient(mock_auth_credentials, mock_model_config)

        # 500k input (0.5M) and 200k output (0.2M)
        cost = client.calculate_cost(input_tokens=500000, output_tokens=200000)

        # $3 * 0.5 + $15 * 0.2 = $1.5 + $3.0 = $4.5
        assert cost == 4.5

    def test_cost_calculation_small_amounts(self, mock_auth_credentials, mock_model_config):
        """Test cost calculation with small token amounts"""
        client = AnthropicClient(mock_auth_credentials, mock_model_config)

        # 100 input, 50 output
        cost = client.calculate_cost(input_tokens=100, output_tokens=50)

        # Should still calculate correctly for small amounts
        assert cost > 0
        assert cost < 0.01

    def test_cost_calculation_zero_tokens(self, mock_auth_credentials, mock_model_config):
        """Test cost calculation with zero tokens"""
        client = AnthropicClient(mock_auth_credentials, mock_model_config)

        cost = client.calculate_cost(input_tokens=0, output_tokens=0)
        assert cost == 0.0

    @patch("anthropic.Anthropic")
    def test_send_request_success(
        self, mock_anthropic_class, mock_auth_credentials, mock_model_config
    ):
        """Test successful API request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.content = [Mock(text="This is the response")]
        mock_response.model = "claude-sonnet-4"
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)

        mock_client = mock_anthropic_class.return_value
        mock_client.messages.create.return_value = mock_response

        client = AnthropicClient(mock_auth_credentials, mock_model_config)
        messages = [Message(role="user", content="Hello")]

        result = client.send_request(messages, "claude-sonnet-4")

        assert isinstance(result, APIResponse)
        assert result.content == "This is the response"
        assert result.model == "claude-sonnet-4"
        assert result.provider == "anthropic"
        assert result.tokens_used["input"] == 100
        assert result.tokens_used["output"] == 50

    @patch("anthropic.Anthropic")
    def test_send_request_with_system_message(
        self, mock_anthropic_class, mock_auth_credentials, mock_model_config
    ):
        """Test request with system message in messages list"""
        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_response.model = "claude-sonnet-4"
        mock_response.usage = Mock(input_tokens=200, output_tokens=100)

        mock_client = mock_anthropic_class.return_value
        mock_client.messages.create.return_value = mock_response

        client = AnthropicClient(mock_auth_credentials, mock_model_config)
        messages = [
            Message(role="system", content="You are helpful"),
            Message(role="user", content="Test"),
        ]

        result = client.send_request(messages, "claude-sonnet-4")

        assert result.content == "Response"
        # Verify system message was extracted and passed
        call_args = mock_client.messages.create.call_args
        assert call_args[1]["system"] == "You are helpful"
        # User message should be in api_messages
        assert len(call_args[1]["messages"]) == 1

    @patch("anthropic.Anthropic")
    def test_send_request_with_max_tokens(
        self, mock_anthropic_class, mock_auth_credentials, mock_model_config
    ):
        """Test request with custom max_tokens"""
        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_response.model = "claude-sonnet-4"
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)

        mock_client = mock_anthropic_class.return_value
        mock_client.messages.create.return_value = mock_response

        client = AnthropicClient(mock_auth_credentials, mock_model_config)
        messages = [Message(role="user", content="Test")]

        client.send_request(messages, "claude-sonnet-4", max_tokens=8192)

        # Verify max_tokens was passed
        call_args = mock_client.messages.create.call_args
        assert call_args[1]["max_tokens"] == 8192

    @patch("anthropic.Anthropic")
    def test_send_request_error_handling(
        self, mock_anthropic_class, mock_auth_credentials, mock_model_config
    ):
        """Test that errors don't leak API details"""
        # Mock anthropic client to raise an exception
        mock_client = mock_anthropic_class.return_value
        mock_client.messages.create.side_effect = Exception("API key invalid: sk-ant-secret-key")

        client = AnthropicClient(mock_auth_credentials, mock_model_config)
        messages = [Message(role="user", content="test")]

        # Should raise our safe error, not the raw exception
        with pytest.raises(APIClientError, match="Failed to communicate"):
            client.send_request(messages, "claude-sonnet-4")

    @patch("anthropic.Anthropic")
    def test_send_request_api_error(
        self, mock_anthropic_class, mock_auth_credentials, mock_model_config
    ):
        """Test handling Anthropic API errors"""
        mock_client = mock_anthropic_class.return_value
        mock_client.messages.create.side_effect = Exception("Rate limit exceeded")

        client = AnthropicClient(mock_auth_credentials, mock_model_config)
        messages = [Message(role="user", content="test")]

        with pytest.raises(APIClientError):
            client.send_request(messages, "claude-sonnet-4")

    @patch("anthropic.Anthropic")
    def test_send_request_multiple_messages(
        self, mock_anthropic_class, mock_auth_credentials, mock_model_config
    ):
        """Test sending multiple messages in conversation"""
        mock_response = Mock()
        mock_response.content = [Mock(text="Response")]
        mock_response.model = "claude-sonnet-4"
        mock_response.usage = Mock(input_tokens=300, output_tokens=150)

        mock_client = mock_anthropic_class.return_value
        mock_client.messages.create.return_value = mock_response

        client = AnthropicClient(mock_auth_credentials, mock_model_config)
        messages = [
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there!"),
            Message(role="user", content="How are you?"),
        ]

        result = client.send_request(messages, "claude-sonnet-4")

        assert result.content == "Response"
        # Verify all messages were passed
        call_args = mock_client.messages.create.call_args
        assert len(call_args[1]["messages"]) == 3


class TestCreateClient:
    """Test client factory function"""

    def test_create_anthropic_client(self, mock_auth_credentials, mock_model_config):
        """Test creating Anthropic client"""
        client = create_client("anthropic", mock_auth_credentials, mock_model_config)
        assert isinstance(client, AnthropicClient)

    def test_create_unsupported_provider(self, mock_auth_credentials, mock_model_config):
        """Test creating client for unsupported provider"""
        with pytest.raises(ValueError, match="Unsupported provider"):
            create_client("unsupported", mock_auth_credentials, mock_model_config)

    def test_create_client_case_insensitive(self, mock_auth_credentials, mock_model_config):
        """Test that provider name is case-insensitive"""
        client = create_client("ANTHROPIC", mock_auth_credentials, mock_model_config)
        assert isinstance(client, AnthropicClient)

    def test_create_client_with_different_cases(self, mock_auth_credentials, mock_model_config):
        """Test that provider name is case-insensitive"""
        # Different cases should all work
        client1 = create_client("anthropic", mock_auth_credentials, mock_model_config)
        assert isinstance(client1, AnthropicClient)

        client2 = create_client("Anthropic", mock_auth_credentials, mock_model_config)
        assert isinstance(client2, AnthropicClient)

        client3 = create_client("ANTHROPIC", mock_auth_credentials, mock_model_config)
        assert isinstance(client3, AnthropicClient)
