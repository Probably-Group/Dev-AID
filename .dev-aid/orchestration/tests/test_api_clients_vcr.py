"""
VCR-based replay tests for API clients

These tests use recorded HTTP interactions (cassettes) stored as YAML files
to test API clients without making real API calls or incurring costs.

Cassettes are YAML files in tests/cassettes/ containing synthetic but
realistic API response data. The vcr_config module patches SDK clients
to return these recorded responses.

## Replaying Cassettes

Tests run entirely from cassettes (no API keys needed):
    pytest tests/test_api_clients_vcr.py -v

## Updating Cassettes

To update cassette data, edit the YAML files in tests/cassettes/ directly.
The format follows VCR conventions: each file has an `interactions` list
with `request` and `response` dicts.

API keys in cassettes are redacted placeholders (REDACTED).
"""

from pathlib import Path
from typing import Any, Dict

import pytest

from router.api_clients import AnthropicClient, GoogleClient, Message, OpenAIClient
from router.auth_detector import AuthCredentials

from .vcr_config import use_cassette

# Cassettes directory
CASSETTES_DIR = Path(__file__).parent / "cassettes"
HAS_CASSETTES = CASSETTES_DIR.exists() and any(CASSETTES_DIR.glob("*.yaml"))

skip_if_no_cassettes = pytest.mark.skipif(
    not HAS_CASSETTES, reason="No cassettes available in tests/cassettes/"
)


def _make_auth(provider: str) -> AuthCredentials:
    """Create test AuthCredentials for a given provider."""
    return AuthCredentials(
        provider=provider,
        auth_type="api_key",
        credentials={"api_key": "test-key-redacted"},
        source="vcr-test-fixture",
    )


class TestAnthropicClientVCR:
    """VCR-based replay tests for Anthropic client"""

    @skip_if_no_cassettes
    @use_cassette("anthropic_simple_request.yaml")
    def test_simple_request(self, mock_model_config: Dict[str, Any]) -> None:
        """Test a simple request to Anthropic API via cassette replay"""
        auth = _make_auth("anthropic")
        client = AnthropicClient(auth, mock_model_config)
        messages = [Message(role="user", content="Say 'Hello' in one word.")]

        response = client.send_request(messages, "claude-sonnet-4")

        assert response.content is not None
        assert len(response.content) > 0
        assert response.content == "Hello"
        assert response.provider == "anthropic"
        assert response.tokens_used["input"] > 0
        assert response.tokens_used["output"] > 0
        assert response.cost is not None
        assert response.cost > 0

    @skip_if_no_cassettes
    @use_cassette("anthropic_long_context.yaml")
    def test_long_context(self, mock_model_config: Dict[str, Any]) -> None:
        """Test handling large context windows via cassette replay"""
        auth = _make_auth("anthropic")
        client = AnthropicClient(auth, mock_model_config)

        # Create a longer conversation
        messages = [
            Message(role="user", content="Explain quantum computing in simple terms."),
            Message(
                role="assistant",
                content="Quantum computing uses quantum mechanics principles...",
            ),
            Message(role="user", content="Can you give a practical example?"),
        ]

        response = client.send_request(messages, "claude-sonnet-4")

        assert response.content is not None
        assert "quantum" in response.content.lower() or "drug" in response.content.lower()
        assert response.provider == "anthropic"
        # Should have higher token count due to context
        assert response.tokens_used["input"] > 50

    @skip_if_no_cassettes
    @use_cassette("anthropic_simple_request.yaml")
    def test_response_metadata(self, mock_model_config: Dict[str, Any]) -> None:
        """Test that response includes metadata fields"""
        auth = _make_auth("anthropic")
        client = AnthropicClient(auth, mock_model_config)
        messages = [Message(role="user", content="Say 'Hello' in one word.")]

        response = client.send_request(messages, "claude-sonnet-4")

        assert response.metadata is not None
        assert "stop_reason" in response.metadata
        assert "response_id" in response.metadata
        assert response.latency_ms is not None
        assert response.latency_ms >= 0


class TestGoogleClientVCR:
    """VCR-based replay tests for Google (Gemini) client"""

    @skip_if_no_cassettes
    @use_cassette("google_simple_request.yaml")
    def test_simple_request(self, mock_google_config: Dict[str, Any]) -> None:
        """Test a simple request to Google Gemini API via cassette replay"""
        auth = _make_auth("google")
        client = GoogleClient(auth, mock_google_config)
        messages = [Message(role="user", content="Say 'Hello' in one word.")]

        response = client.send_request(messages, "gemini-flash")

        assert response.content is not None
        assert response.content == "Hello"
        assert response.provider == "google"
        assert response.tokens_used["input"] > 0
        assert response.tokens_used["output"] > 0
        assert response.cost is not None
        assert response.cost >= 0

    @skip_if_no_cassettes
    @use_cassette("google_simple_request.yaml")
    def test_response_structure(self, mock_google_config: Dict[str, Any]) -> None:
        """Test that Google response follows the unified structure"""
        auth = _make_auth("google")
        client = GoogleClient(auth, mock_google_config)
        messages = [Message(role="user", content="Say 'Hello' in one word.")]

        response = client.send_request(messages, "gemini-flash")

        assert hasattr(response, "content")
        assert hasattr(response, "provider")
        assert hasattr(response, "tokens_used")
        assert hasattr(response, "cost")
        assert hasattr(response, "latency_ms")
        assert hasattr(response, "metadata")
        assert isinstance(response.tokens_used, dict)
        assert "input" in response.tokens_used
        assert "output" in response.tokens_used


class TestOpenAIClientVCR:
    """VCR-based replay tests for OpenAI client"""

    @skip_if_no_cassettes
    @use_cassette("openai_simple_request.yaml")
    def test_simple_request(self, mock_openai_config: Dict[str, Any]) -> None:
        """Test a simple request to OpenAI API via cassette replay"""
        auth = _make_auth("openai")
        client = OpenAIClient(auth, mock_openai_config)
        messages = [Message(role="user", content="Say 'Hello' in one word.")]

        response = client.send_request(messages, "gpt-4o")

        assert response.content is not None
        assert response.content == "Hello"
        assert response.provider == "openai"
        assert response.tokens_used["input"] > 0
        assert response.tokens_used["output"] > 0
        assert response.cost is not None
        assert response.cost > 0

    @skip_if_no_cassettes
    @use_cassette("openai_simple_request.yaml")
    def test_response_metadata(self, mock_openai_config: Dict[str, Any]) -> None:
        """Test that OpenAI response includes metadata"""
        auth = _make_auth("openai")
        client = OpenAIClient(auth, mock_openai_config)
        messages = [Message(role="user", content="Say 'Hello' in one word.")]

        response = client.send_request(messages, "gpt-4o")

        assert response.metadata is not None
        assert "finish_reason" in response.metadata
        assert "response_id" in response.metadata


class TestCrossProviderConsistency:
    """Test that all providers return consistent response formats via cassettes"""

    @skip_if_no_cassettes
    @use_cassette("cross_provider_consistency.yaml")
    def test_response_structure(
        self,
        mock_model_config: Dict[str, Any],
        mock_google_config: Dict[str, Any],
        mock_openai_config: Dict[str, Any],
    ) -> None:
        """Verify all providers return the same response structure"""
        prompt = [Message(role="user", content="Count to 3.")]

        providers_and_clients = [
            (
                "anthropic",
                AnthropicClient(_make_auth("anthropic"), mock_model_config),
                "claude-sonnet-4",
            ),
            (
                "google",
                GoogleClient(_make_auth("google"), mock_google_config),
                "gemini-flash",
            ),
            (
                "openai",
                OpenAIClient(_make_auth("openai"), mock_openai_config),
                "gpt-4o",
            ),
        ]

        responses = []
        for provider_name, client, model in providers_and_clients:
            response = client.send_request(prompt, model)
            responses.append(response)

            # Verify unified structure
            assert hasattr(response, "content"), f"{provider_name}: missing content"
            assert hasattr(response, "provider"), f"{provider_name}: missing provider"
            assert hasattr(response, "tokens_used"), f"{provider_name}: missing tokens_used"
            assert hasattr(response, "cost"), f"{provider_name}: missing cost"
            assert isinstance(response.tokens_used, dict), f"{provider_name}: tokens_used not dict"
            assert "input" in response.tokens_used, f"{provider_name}: missing input tokens"
            assert "output" in response.tokens_used, f"{provider_name}: missing output tokens"

        # Verify we tested all three providers
        assert len(responses) == 3
        providers_tested = {r.provider for r in responses}
        assert providers_tested == {"anthropic", "google", "openai"}

    @skip_if_no_cassettes
    @use_cassette("cross_provider_consistency.yaml")
    def test_all_providers_return_content(
        self,
        mock_model_config: Dict[str, Any],
        mock_google_config: Dict[str, Any],
        mock_openai_config: Dict[str, Any],
    ) -> None:
        """Verify all providers return non-empty content for the same prompt"""
        prompt = [Message(role="user", content="Count to 3.")]

        configs = {
            "anthropic": (
                AnthropicClient(_make_auth("anthropic"), mock_model_config),
                "claude-sonnet-4",
            ),
            "google": (
                GoogleClient(_make_auth("google"), mock_google_config),
                "gemini-flash",
            ),
            "openai": (
                OpenAIClient(_make_auth("openai"), mock_openai_config),
                "gpt-4o",
            ),
        }

        for provider_name, (client, model) in configs.items():
            response = client.send_request(prompt, model)
            assert response.content, f"{provider_name} returned empty content"
            assert response.provider == provider_name
            assert response.tokens_used["input"] > 0, f"{provider_name}: zero input tokens"
            assert response.tokens_used["output"] > 0, f"{provider_name}: zero output tokens"
