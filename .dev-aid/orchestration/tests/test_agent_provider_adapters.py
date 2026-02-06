"""Tests for provider adapters (format conversion, no real API calls)."""

import json

import pytest

from agents.core.models import ToolCall
from agents.core.provider_adapter import create_adapter


class TestAnthropicAdapter:
    """Tests for AnthropicAdapter format helpers."""

    def test_format_tool_result(self) -> None:
        from agents.adapters.anthropic_adapter import AnthropicAdapter

        result = AnthropicAdapter.format_tool_result("tc_1", "file contents")
        assert result["role"] == "user"
        assert result["content"][0]["type"] == "tool_result"
        assert result["content"][0]["tool_use_id"] == "tc_1"
        assert result["content"][0]["content"] == "file contents"
        assert result["content"][0]["is_error"] is False

    def test_format_tool_result_error(self) -> None:
        from agents.adapters.anthropic_adapter import AnthropicAdapter

        result = AnthropicAdapter.format_tool_result("tc_1", "Error!", is_error=True)
        assert result["content"][0]["is_error"] is True

    def test_format_assistant_tool_use(self) -> None:
        from agents.adapters.anthropic_adapter import AnthropicAdapter

        tc = ToolCall(id="tc_1", name="read_file", arguments={"path": "/tmp/x"})
        result = AnthropicAdapter.format_assistant_tool_use([tc], "Let me read that")
        assert result["role"] == "assistant"
        assert len(result["content"]) == 2  # text + tool_use
        assert result["content"][0]["type"] == "text"
        assert result["content"][1]["type"] == "tool_use"
        assert result["content"][1]["name"] == "read_file"

    def test_format_assistant_tool_use_no_text(self) -> None:
        from agents.adapters.anthropic_adapter import AnthropicAdapter

        tc = ToolCall(id="tc_1", name="echo", arguments={"text": "hi"})
        result = AnthropicAdapter.format_assistant_tool_use([tc])
        assert result["role"] == "assistant"
        assert len(result["content"]) == 1  # tool_use only
        assert result["content"][0]["type"] == "tool_use"


class TestOpenAIAdapter:
    """Tests for OpenAIAdapter format helpers."""

    def test_format_tool_result(self) -> None:
        from agents.adapters.openai_adapter import OpenAIAdapter

        result = OpenAIAdapter.format_tool_result("call_1", "output data")
        assert result["role"] == "tool"
        assert result["tool_call_id"] == "call_1"
        assert result["content"] == "output data"

    def test_format_assistant_tool_use(self) -> None:
        from agents.adapters.openai_adapter import OpenAIAdapter

        tc = ToolCall(id="call_1", name="read_file", arguments={"path": "/tmp/x"})
        result = OpenAIAdapter.format_assistant_tool_use([tc], "Reading file")
        assert result["role"] == "assistant"
        assert result["content"] == "Reading file"
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["function"]["name"] == "read_file"
        # Arguments should be JSON-encoded
        args = json.loads(result["tool_calls"][0]["function"]["arguments"])
        assert args["path"] == "/tmp/x"

    def test_format_assistant_no_tools(self) -> None:
        from agents.adapters.openai_adapter import OpenAIAdapter

        result = OpenAIAdapter.format_assistant_tool_use([], "Just text")
        assert result["role"] == "assistant"
        assert result["content"] == "Just text"
        assert "tool_calls" not in result


class TestGoogleAdapter:
    """Tests for GoogleAdapter format helpers."""

    def test_format_tool_result(self) -> None:
        from agents.adapters.google_adapter import GoogleAdapter

        result = GoogleAdapter.format_tool_result("tc_1", "output")
        assert result["role"] == "user"
        assert "tc_1" in result["content"]

    def test_format_assistant_tool_use(self) -> None:
        from agents.adapters.google_adapter import GoogleAdapter

        tc = ToolCall(id="tc_1", name="read_file", arguments={"path": "/tmp"})
        result = GoogleAdapter.format_assistant_tool_use([tc], "Reading")
        assert result["role"] == "model"
        assert len(result["parts"]) == 2  # text + function_call
        assert result["parts"][0]["text"] == "Reading"
        assert result["parts"][1]["function_call"]["name"] == "read_file"

    def test_convert_messages(self) -> None:
        from agents.adapters.google_adapter import GoogleAdapter

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "user", "content": "Thanks"},
        ]
        result = GoogleAdapter._convert_messages(messages)
        assert len(result) == 3
        assert result[0]["role"] == "user"
        assert result[1]["role"] == "model"
        assert result[2]["role"] == "user"


class TestCreateAdapter:
    """Tests for the adapter factory function."""

    def test_create_anthropic(self) -> None:
        adapter = create_adapter("anthropic", api_key="test-key")
        from agents.adapters.anthropic_adapter import AnthropicAdapter

        assert isinstance(adapter, AnthropicAdapter)

    def test_create_openai(self) -> None:
        adapter = create_adapter("openai", api_key="test-key")
        from agents.adapters.openai_adapter import OpenAIAdapter

        assert isinstance(adapter, OpenAIAdapter)

    def test_create_local(self) -> None:
        adapter = create_adapter("local", base_url="http://localhost:11434/v1")
        from agents.adapters.openai_adapter import OpenAIAdapter

        assert isinstance(adapter, OpenAIAdapter)

    def test_create_google(self) -> None:
        adapter = create_adapter("google", api_key="test-key")
        from agents.adapters.google_adapter import GoogleAdapter

        assert isinstance(adapter, GoogleAdapter)

    def test_create_unsupported(self) -> None:
        with pytest.raises(ValueError, match="Unsupported provider"):
            create_adapter("bedrock")

    def test_case_insensitive(self) -> None:
        adapter = create_adapter("Anthropic", api_key="key")
        from agents.adapters.anthropic_adapter import AnthropicAdapter

        assert isinstance(adapter, AnthropicAdapter)
