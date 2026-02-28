"""
Cassette-based replay configuration for API client testing.

Loads recorded HTTP responses from YAML cassette files and replays them
via unittest.mock, giving deterministic tests without real API calls.

This approach is more robust than HTTP-level VCR interception because
it works regardless of SDK transport changes (httpx, urllib3, etc.).
"""

import functools
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast
from unittest.mock import MagicMock

import yaml  # type: ignore[import-untyped]

F = TypeVar("F", bound=Callable[..., Any])

# Cassettes directory
CASSETTES_DIR = Path(__file__).parent / "cassettes"


def _load_cassette(cassette_name: str) -> List[Dict[str, Any]]:
    """
    Load interactions from a YAML cassette file.

    Args:
        cassette_name: Name of the cassette YAML file

    Returns:
        List of interaction dicts with request/response pairs

    Raises:
        FileNotFoundError: If cassette does not exist
    """
    path = CASSETTES_DIR / cassette_name
    if not path.exists():
        raise FileNotFoundError(
            f"Cassette not found: {path}\n" "Record cassettes by running tests with real API keys."
        )
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    result: List[Dict[str, Any]] = data.get("interactions", [])
    return result


def _find_response_for_provider(
    interactions: List[Dict[str, Any]], provider: str
) -> Optional[Dict[str, Any]]:
    """
    Find the response body for a specific provider from cassette interactions.

    Args:
        interactions: List of cassette interactions
        provider: Provider name ('anthropic', 'google', 'openai')

    Returns:
        Parsed response body dict, or None if not found
    """
    uri_patterns: Dict[str, str] = {
        "anthropic": "api.anthropic.com",
        "google": "generativelanguage.googleapis.com",
        "openai": "api.openai.com",
    }
    pattern = uri_patterns.get(provider, "")

    for interaction in interactions:
        uri = interaction.get("request", {}).get("uri", "")
        if pattern in uri:
            body_str = interaction.get("response", {}).get("body", {}).get("string", "{}")
            parsed: Dict[str, Any] = json.loads(body_str)
            return parsed
    return None


def _build_anthropic_mock(response_data: Dict[str, Any]) -> MagicMock:
    """Build a mock Anthropic API response object from cassette data."""
    mock_response = MagicMock()
    content_block = MagicMock()
    content_block.text = response_data["content"][0]["text"]
    mock_response.content = [content_block]
    mock_response.model = response_data["model"]
    mock_response.stop_reason = response_data.get("stop_reason", "end_turn")
    mock_response.id = response_data.get("id", "msg_test")
    mock_response.usage = MagicMock()
    mock_response.usage.input_tokens = response_data["usage"]["input_tokens"]
    mock_response.usage.output_tokens = response_data["usage"]["output_tokens"]
    return mock_response


def _build_google_mock(response_data: Dict[str, Any]) -> MagicMock:
    """Build a mock Google Gemini API response object from cassette data."""
    mock_response = MagicMock()
    candidate_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
    mock_response.text = candidate_text

    # Usage metadata
    usage = response_data.get("usageMetadata", {})
    mock_response.usage_metadata = MagicMock()
    mock_response.usage_metadata.prompt_token_count = usage.get("promptTokenCount", 0)
    mock_response.usage_metadata.candidates_token_count = usage.get("candidatesTokenCount", 0)

    # Candidates for finish_reason
    mock_candidate = MagicMock()
    mock_candidate.finish_reason = response_data["candidates"][0].get("finishReason", "STOP")
    mock_response.candidates = [mock_candidate]

    return mock_response


def _build_openai_mock(response_data: Dict[str, Any]) -> MagicMock:
    """Build a mock OpenAI API response object from cassette data."""
    mock_response = MagicMock()
    choice = MagicMock()
    choice.message = MagicMock()
    choice.message.content = response_data["choices"][0]["message"]["content"]
    choice.finish_reason = response_data["choices"][0].get("finish_reason", "stop")
    choice.index = 0
    mock_response.choices = [choice]
    mock_response.id = response_data.get("id", "chatcmpl-test")
    mock_response.model = response_data.get("model", "gpt-4o")

    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = response_data["usage"]["prompt_tokens"]
    mock_response.usage.completion_tokens = response_data["usage"]["completion_tokens"]

    return mock_response


class CassetteContext:
    """
    Context manager that patches SDK clients to return cassette-recorded responses.

    Replaces real API calls with mock responses loaded from YAML cassette files,
    producing the same objects that the real SDKs would return.
    """

    def __init__(self, cassette_name: str) -> None:
        self.cassette_name = cassette_name
        self.interactions: List[Dict[str, Any]] = []
        self._patches: List[Any] = []

    def __enter__(self) -> "CassetteContext":
        from unittest.mock import patch

        self.interactions = _load_cassette(self.cassette_name)

        # Build provider-specific mocks
        anthropic_data = _find_response_for_provider(self.interactions, "anthropic")
        google_data = _find_response_for_provider(self.interactions, "google")
        openai_data = _find_response_for_provider(self.interactions, "openai")

        # Patch Anthropic SDK
        if anthropic_data:
            mock_anthropic_response = _build_anthropic_mock(anthropic_data)
            p = patch("anthropic.Anthropic")
            mock_cls = p.start()
            mock_cls.return_value.messages.create.return_value = mock_anthropic_response
            self._patches.append(p)

        # Patch Google SDK
        if google_data:
            mock_google_response = _build_google_mock(google_data)
            p = patch("google.genai.Client")
            mock_cls = p.start()
            mock_cls.return_value.models.generate_content.return_value = mock_google_response
            self._patches.append(p)

            # Also patch the types import
            p2 = patch("google.genai.types")
            mock_types = p2.start()
            mock_types.GenerateContentConfig.return_value = MagicMock()
            self._patches.append(p2)

        # Patch OpenAI SDK
        if openai_data:
            mock_openai_response = _build_openai_mock(openai_data)
            p = patch("openai.OpenAI")
            mock_cls = p.start()
            mock_cls.return_value.chat.completions.create.return_value = mock_openai_response
            self._patches.append(p)

        return self

    def __exit__(self, *args: Any) -> None:
        for p in self._patches:
            p.stop()
        self._patches.clear()


def use_cassette(cassette_name: str) -> Callable[[F], F]:
    """
    Decorator to replay recorded API responses from a YAML cassette file.

    Usage:
        @use_cassette('anthropic_simple_request.yaml')
        def test_anthropic_api(self, ...):
            # SDK calls are mocked with cassette data
            pass
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with CassetteContext(cassette_name):
                return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator
