"""
VCR-based tests for API clients

These tests use recorded HTTP interactions (cassettes) to test API clients
without making real API calls or incurring costs.

## Recording Cassettes

To record new cassettes with real API calls:

1. Set environment variables with real API keys:
   export ANTHROPIC_API_KEY=sk-ant-...
   export OPENAI_API_KEY=sk-...
   export GOOGLE_API_KEY=...

2. Delete existing cassettes (optional):
   rm -rf tests/cassettes/*.yaml

3. Run tests (VCR will record in 'once' mode):
   pytest tests/test_api_clients_vcr.py -v

4. Verify cassettes are created:
   ls tests/cassettes/

5. Commit cassettes to repo for CI testing

## Replaying Cassettes

In CI or without API keys, tests will replay from cassettes:
   pytest tests/test_api_clients_vcr.py -v

API keys in cassettes are automatically redacted.
"""

import os
from pathlib import Path

import pytest


from .vcr_config import use_cassette

# Skip VCR tests if no API keys AND no cassettes exist
# This allows CI to run with cassettes but developers to skip if no setup
CASSETTES_DIR = Path(__file__).parent / "cassettes"
HAS_CASSETTES = CASSETTES_DIR.exists() and any(CASSETTES_DIR.glob("*.yaml"))
HAS_API_KEYS = bool(
    os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")
)

skip_if_no_setup = pytest.mark.skipif(
    not (HAS_CASSETTES or HAS_API_KEYS), reason="No cassettes or API keys available"
)


class TestAnthropicClientVCR:
    """VCR-based tests for Anthropic client"""

    @skip_if_no_setup
    @use_cassette("anthropic_simple_request.yaml")
    def test_simple_request(self, mock_model_config):
        """Test a simple request to Anthropic API"""
        # Use real or recorded API key
        api_key = os.getenv("ANTHROPIC_API_KEY", "test-key")

        client = AnthropicClient(api_key, mock_model_config)
        messages = [Message(role="user", content="Say 'Hello' in one word.")]

        response = client.send_request(messages, "claude-sonnet-4")

        assert response.content is not None
        assert len(response.content) > 0
        assert response.provider == "anthropic"
        assert response.tokens_used["input"] > 0
        assert response.tokens_used["output"] > 0
        assert response.cost > 0

    @skip_if_no_setup
    @use_cassette("anthropic_long_context.yaml")
    def test_long_context(self, mock_model_config):
        """Test handling large context windows"""
        api_key = os.getenv("ANTHROPIC_API_KEY", "test-key")

        client = AnthropicClient(api_key, mock_model_config)

        # Create a longer conversation
        messages = [
            Message(role="user", content="Explain quantum computing in simple terms."),
            Message(
                role="assistant", content="Quantum computing uses quantum mechanics principles..."
            ),
            Message(role="user", content="Can you give a practical example?"),
        ]

        response = client.send_request(messages, "claude-sonnet-4")

        assert response.content is not None
        assert response.provider == "anthropic"
        # Should have higher token count due to context
        assert response.tokens_used["input"] > 50


class TestGoogleClientVCR:
    """VCR-based tests for Google (Gemini) client"""

    @skip_if_no_setup
    @use_cassette("google_simple_request.yaml")
    def test_simple_request(self, mock_google_config):
        """Test a simple request to Google Gemini API"""
        api_key = os.getenv("GOOGLE_API_KEY", "test-key")

        client = GoogleClient(api_key, mock_google_config)
        messages = [Message(role="user", content="Say 'Hello' in one word.")]

        response = client.send_request(messages, "gemini-flash")

        assert response.content is not None
        assert response.provider == "google"
        assert response.tokens_used["input"] > 0


class TestOpenAIClientVCR:
    """VCR-based tests for OpenAI client"""

    @skip_if_no_setup
    @use_cassette("openai_simple_request.yaml")
    def test_simple_request(self, mock_openai_config):
        """Test a simple request to OpenAI API"""
        api_key = os.getenv("OPENAI_API_KEY", "test-key")

        client = OpenAIClient(api_key, mock_openai_config)
        messages = [Message(role="user", content="Say 'Hello' in one word.")]

        response = client.send_request(messages, "gpt-4o")

        assert response.content is not None
        assert response.provider == "openai"
        assert response.tokens_used["input"] > 0


class TestCrossProviderConsistency:
    """Test that all providers return consistent response formats"""

    @skip_if_no_setup
    @use_cassette("cross_provider_consistency.yaml")
    def test_response_structure(self, mock_model_config, mock_google_config, mock_openai_config):
        """Verify all providers return same response structure"""
        prompt = [Message(role="user", content="Count to 3.")]

        # Test with whichever providers have keys/cassettes
        providers = []

        if (
            os.getenv("ANTHROPIC_API_KEY")
            or (CASSETTES_DIR / "anthropic_simple_request.yaml").exists()
        ):
            providers.append(
                (
                    "anthropic",
                    AnthropicClient(os.getenv("ANTHROPIC_API_KEY", "test"), mock_model_config),
                )
            )

        if os.getenv("GOOGLE_API_KEY") or (CASSETTES_DIR / "google_simple_request.yaml").exists():
            providers.append(
                ("google", GoogleClient(os.getenv("GOOGLE_API_KEY", "test"), mock_google_config))
            )

        if os.getenv("OPENAI_API_KEY") or (CASSETTES_DIR / "openai_simple_request.yaml").exists():
            providers.append(
                ("openai", OpenAIClient(os.getenv("OPENAI_API_KEY", "test"), mock_openai_config))
            )

        responses = []
        for provider_name, client in providers:
            model = {"anthropic": "claude-sonnet-4", "google": "gemini-flash", "openai": "gpt-4o"}[
                provider_name
            ]

            response = client.send_request(prompt, model)
            responses.append(response)

            # Verify structure
            assert hasattr(response, "content")
            assert hasattr(response, "provider")
            assert hasattr(response, "tokens_used")
            assert hasattr(response, "cost")
            assert isinstance(response.tokens_used, dict)
            assert "input" in response.tokens_used
            assert "output" in response.tokens_used
