"""
Anthropic (Claude) provider adapter.

Implements tool-calling via the Anthropic Messages API.
"""

import logging
from typing import Any, Dict, List, Optional

from ..core.cost import estimate_cost
from ..core.models import ToolCall, ToolResult
from ..core.provider_adapter import ProviderResponse

logger = logging.getLogger(__name__)


class AnthropicAdapter:
    """Adapter for Anthropic's tool-use Messages API."""

    tool_format: str = "anthropic"

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key
        self._client: Any = None

    def _get_client(self) -> Any:
        """Lazily initialize the Anthropic client."""
        if self._client is None:
            try:
                import anthropic  # type: ignore[import-untyped]

                self._client = anthropic.Anthropic(api_key=self._api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package not installed. "
                    "Install with: pip install anthropic"
                )
        return self._client

    def send_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        system_prompt: str = "",
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> ProviderResponse:
        """Send messages with tools to Anthropic's API."""
        client = self._get_client()

        kwargs: Dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        if system_prompt:
            kwargs["system"] = system_prompt
        if tools:
            kwargs["tools"] = tools

        response = client.messages.create(**kwargs)

        # Parse response
        content_text: Optional[str] = None
        tool_calls: List[ToolCall] = []

        for block in response.content:
            if block.type == "text":
                content_text = block.text
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input if isinstance(block.input, dict) else {},
                    )
                )

        # Map stop reason
        stop_reason = "end_turn"
        if response.stop_reason == "tool_use":
            stop_reason = "tool_use"
        elif response.stop_reason == "max_tokens":
            stop_reason = "max_tokens"

        # Token usage and cost
        tokens_used = {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
        }
        cost = estimate_cost(
            model,
            tokens_used["input"],
            tokens_used["output"],
        )

        return ProviderResponse(
            content=content_text,
            tool_calls=tool_calls,
            stop_reason=stop_reason,
            tokens_used=tokens_used,
            cost=cost,
        )

    @staticmethod
    def format_tool_result(
        call_id: str, output: str, is_error: bool = False
    ) -> Dict[str, Any]:
        """Format a tool result for the Anthropic messages format."""
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": call_id,
                    "content": output,
                    "is_error": is_error,
                }
            ],
        }

    @staticmethod
    def format_tool_results(results: List[ToolResult]) -> List[Dict[str, Any]]:
        """Format multiple tool results into a single batched message.

        Anthropic requires all tool results from one turn to be in
        a single 'user' message with multiple tool_result blocks.
        """
        content: List[Dict[str, Any]] = []
        for r in results:
            content.append(
                {
                    "type": "tool_result",
                    "tool_use_id": r.call_id,
                    "content": r.output if r.success else (r.error or ""),
                    "is_error": not r.success,
                }
            )
        return [{"role": "user", "content": content}]

    @staticmethod
    def format_assistant_tool_use(
        tool_calls: List[ToolCall],
        text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Format assistant message with tool use blocks."""
        content: List[Dict[str, Any]] = []
        if text:
            content.append({"type": "text", "text": text})
        for tc in tool_calls:
            content.append(
                {
                    "type": "tool_use",
                    "id": tc.id,
                    "name": tc.name,
                    "input": tc.arguments,
                }
            )
        return {"role": "assistant", "content": content}
