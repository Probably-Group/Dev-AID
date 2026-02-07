"""
OpenAI (and compatible) provider adapter.

Implements tool-calling via the OpenAI Chat Completions API.
Also works with local models (Ollama, LM Studio) that expose
an OpenAI-compatible endpoint.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from ..core.cost import estimate_cost
from ..core.models import ToolCall, ToolResult
from ..core.provider_adapter import ProviderResponse

logger = logging.getLogger(__name__)


class OpenAIAdapter:
    """Adapter for OpenAI's function-calling Chat Completions API."""

    tool_format: str = "openai"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        self._api_key = api_key or "not-needed"
        self._base_url = base_url
        self._client: Any = None

    def _get_client(self) -> Any:
        """Lazily initialize the OpenAI client."""
        if self._client is None:
            try:
                import openai  # type: ignore[import-untyped]

                kwargs: Dict[str, Any] = {"api_key": self._api_key}
                if self._base_url:
                    kwargs["base_url"] = self._base_url
                self._client = openai.OpenAI(**kwargs)
            except ImportError:
                raise ImportError(
                    "openai package not installed. "
                    "Install with: pip install openai"
                )
        return self._client

    def send_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        system_prompt: str = "",
        model: str = "gpt-4o",
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> ProviderResponse:
        """Send messages with tools to OpenAI's API."""
        client = self._get_client()

        # Build message list with system prompt
        full_messages: List[Dict[str, Any]] = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": full_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools

        response = client.chat.completions.create(**kwargs)

        choice = response.choices[0]
        message = choice.message

        # Parse tool calls
        tool_calls: List[ToolCall] = []
        if message.tool_calls:
            for tc in message.tool_calls:
                try:
                    arguments = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, AttributeError):
                    arguments = {}
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=arguments,
                    )
                )

        # Map stop reason
        stop_reason = "end_turn"
        if choice.finish_reason == "tool_calls":
            stop_reason = "tool_use"
        elif choice.finish_reason == "length":
            stop_reason = "max_tokens"

        # Token usage and cost
        tokens_used = {"input": 0, "output": 0}
        if response.usage:
            tokens_used = {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
            }
        cost = estimate_cost(model, tokens_used["input"], tokens_used["output"])

        return ProviderResponse(
            content=message.content,
            tool_calls=tool_calls,
            stop_reason=stop_reason,
            tokens_used=tokens_used,
            cost=cost,
        )

    @staticmethod
    def format_tool_result(call_id: str, output: str, is_error: bool = False) -> Dict[str, Any]:
        """Format a tool result for OpenAI's messages format."""
        return {
            "role": "tool",
            "tool_call_id": call_id,
            "content": output,
        }

    @staticmethod
    def format_tool_results(results: List[ToolResult]) -> List[Dict[str, Any]]:
        """Format multiple tool results as separate messages.

        OpenAI expects each tool result as a separate message with role='tool'.
        """
        return [
            {
                "role": "tool",
                "tool_call_id": r.call_id,
                "content": r.output if r.success else (r.error or ""),
            }
            for r in results
        ]

    @staticmethod
    def format_assistant_tool_use(
        tool_calls: List[ToolCall],
        text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Format assistant message with tool calls."""
        msg: Dict[str, Any] = {
            "role": "assistant",
            "content": text or "",
        }
        if tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments),
                    },
                }
                for tc in tool_calls
            ]
        return msg
