"""Tests for provider adapters (format conversion, no real API calls)."""

import json

import pytest
from agents.core.models import ToolCall, ToolResult
from agents.core.provider_adapter import create_adapter


class TestAnthropicAdapter:
    """Tests for AnthropicAdapter format helpers."""

    def test_tool_format(self) -> None:
        from agents.adapters.anthropic_adapter import AnthropicAdapter

        adapter = AnthropicAdapter(api_key="test")
        assert adapter.tool_format == "anthropic"

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

    def test_format_tool_results_batched(self) -> None:
        from agents.adapters.anthropic_adapter import AnthropicAdapter

        results = [
            ToolResult(call_id="tc_1", name="read_file", output="contents", success=True),
            ToolResult(call_id="tc_2", name="echo", output="hi", success=True),
        ]
        messages = AnthropicAdapter.format_tool_results(results)
        # Should be a single message with both results
        assert len(messages) == 1
        msg = messages[0]
        assert msg["role"] == "user"
        assert len(msg["content"]) == 2
        assert msg["content"][0]["tool_use_id"] == "tc_1"
        assert msg["content"][1]["tool_use_id"] == "tc_2"

    def test_format_tool_results_with_error(self) -> None:
        from agents.adapters.anthropic_adapter import AnthropicAdapter

        results = [
            ToolResult(
                call_id="tc_1", name="read_file", output="", success=False, error="Not found"
            ),
        ]
        messages = AnthropicAdapter.format_tool_results(results)
        assert messages[0]["content"][0]["is_error"] is True
        assert messages[0]["content"][0]["content"] == "Not found"

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

    def test_tool_format(self) -> None:
        from agents.adapters.openai_adapter import OpenAIAdapter

        adapter = OpenAIAdapter(api_key="test")
        assert adapter.tool_format == "openai"

    def test_format_tool_result(self) -> None:
        from agents.adapters.openai_adapter import OpenAIAdapter

        result = OpenAIAdapter.format_tool_result("call_1", "output data")
        assert result["role"] == "tool"
        assert result["tool_call_id"] == "call_1"
        assert result["content"] == "output data"

    def test_format_tool_results_separate_messages(self) -> None:
        from agents.adapters.openai_adapter import OpenAIAdapter

        results = [
            ToolResult(call_id="call_1", name="read_file", output="file data", success=True),
            ToolResult(call_id="call_2", name="echo", output="echoed", success=True),
        ]
        messages = OpenAIAdapter.format_tool_results(results)
        # OpenAI: each result is a separate message
        assert len(messages) == 2
        assert messages[0]["role"] == "tool"
        assert messages[0]["tool_call_id"] == "call_1"
        assert messages[1]["tool_call_id"] == "call_2"

    def test_format_tool_results_error(self) -> None:
        from agents.adapters.openai_adapter import OpenAIAdapter

        results = [
            ToolResult(
                call_id="call_1", name="read_file", output="", success=False, error="Not found"
            ),
        ]
        messages = OpenAIAdapter.format_tool_results(results)
        assert messages[0]["content"] == "Not found"

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

    def test_tool_format(self) -> None:
        from agents.adapters.google_adapter import GoogleAdapter

        adapter = GoogleAdapter(api_key="test")
        assert adapter.tool_format == "gemini"

    def test_format_tool_result_uses_function_response(self) -> None:
        from agents.adapters.google_adapter import GoogleAdapter

        result = GoogleAdapter.format_tool_result("read_file", "output")
        assert result["role"] == "user"
        assert "parts" in result
        assert "function_response" in result["parts"][0]
        assert result["parts"][0]["function_response"]["name"] == "read_file"
        assert result["parts"][0]["function_response"]["response"]["result"] == "output"

    def test_format_tool_results_batched(self) -> None:
        from agents.adapters.google_adapter import GoogleAdapter

        results = [
            ToolResult(call_id="tc_1", name="read_file", output="contents", success=True),
            ToolResult(call_id="tc_2", name="echo", output="hi", success=True),
        ]
        messages = GoogleAdapter.format_tool_results(results)
        # Gemini: single message with multiple function_response parts
        assert len(messages) == 1
        msg = messages[0]
        assert msg["role"] == "user"
        assert len(msg["parts"]) == 2
        assert msg["parts"][0]["function_response"]["name"] == "read_file"
        assert msg["parts"][1]["function_response"]["name"] == "echo"

    def test_format_tool_results_error(self) -> None:
        from agents.adapters.google_adapter import GoogleAdapter

        results = [
            ToolResult(
                call_id="tc_1", name="read_file", output="", success=False, error="Not found"
            ),
        ]
        messages = GoogleAdapter.format_tool_results(results)
        resp = messages[0]["parts"][0]["function_response"]["response"]
        assert resp["result"] == "Not found"
        assert resp["is_error"] is True

    def test_format_assistant_tool_use(self) -> None:
        from agents.adapters.google_adapter import GoogleAdapter

        tc = ToolCall(id="tc_1", name="read_file", arguments={"path": "/tmp"})
        result = GoogleAdapter.format_assistant_tool_use([tc], "Reading")
        assert result["role"] == "model"
        assert len(result["parts"]) == 2  # text + function_call
        assert result["parts"][0]["text"] == "Reading"
        assert result["parts"][1]["function_call"]["name"] == "read_file"

    def test_convert_messages_generic(self) -> None:
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

    def test_convert_messages_passthrough_gemini_format(self) -> None:
        from agents.adapters.google_adapter import GoogleAdapter

        messages = [
            {"role": "user", "content": "Hello"},
            {
                "role": "model",
                "parts": [{"function_call": {"name": "echo", "args": {"text": "hi"}}}],
            },
            {
                "role": "user",
                "parts": [
                    {
                        "function_response": {
                            "name": "echo",
                            "response": {"result": "Echo: hi"},
                        }
                    }
                ],
            },
        ]
        result = GoogleAdapter._convert_messages(messages)
        assert len(result) == 3
        # First message converted from generic
        assert result[0]["parts"][0]["text"] == "Hello"
        # Second and third already in Gemini format - passed through
        assert "function_call" in result[1]["parts"][0]
        assert "function_response" in result[2]["parts"][0]


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
