"""
Google (Gemini) provider adapter.

Implements tool-calling via the Gemini API with FunctionDeclaration format.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from ..core.models import ToolCall
from ..core.provider_adapter import ProviderResponse

logger = logging.getLogger(__name__)


class GoogleAdapter:
    """Adapter for Google's Gemini function-calling API."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key
        self._client: Any = None

    def _get_client(self) -> Any:
        """Lazily initialize the Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai  # type: ignore[import-untyped]

                if self._api_key:
                    genai.configure(api_key=self._api_key)
                self._client = genai
            except ImportError:
                raise ImportError(
                    "google-generativeai package not installed. "
                    "Install with: pip install google-generativeai"
                )
        return self._client

    def send_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        system_prompt: str = "",
        model: str = "gemini-2.0-flash",
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> ProviderResponse:
        """Send messages with tools to Gemini's API."""
        genai = self._get_client()

        # Build Gemini model with system instruction
        model_kwargs: Dict[str, Any] = {}
        if system_prompt:
            model_kwargs["system_instruction"] = system_prompt

        gemini_model = genai.GenerativeModel(model, **model_kwargs)

        # Convert tools to Gemini format
        gemini_tools = None
        if tools:
            gemini_tools = [genai.types.Tool(function_declarations=tools)]

        # Convert messages to Gemini content format
        contents = self._convert_messages(messages)

        # Generate
        start = time.monotonic()
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        response = gemini_model.generate_content(
            contents,
            tools=gemini_tools,
            generation_config=generation_config,
        )
        _ = (time.monotonic() - start) * 1000  # latency tracked externally

        # Parse response
        content_text: Optional[str] = None
        tool_calls: List[ToolCall] = []

        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    content_text = part.text
                elif hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    args = dict(fc.args) if fc.args else {}
                    tool_calls.append(
                        ToolCall(
                            id=ToolCall.generate_id(),
                            name=fc.name,
                            arguments=args,
                        )
                    )

        stop_reason = "tool_use" if tool_calls else "end_turn"

        # Gemini doesn't always expose token counts directly
        tokens_used = {"input": 0, "output": 0}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            um = response.usage_metadata
            tokens_used = {
                "input": getattr(um, "prompt_token_count", 0) or 0,
                "output": getattr(um, "candidates_token_count", 0) or 0,
            }

        return ProviderResponse(
            content=content_text,
            tool_calls=tool_calls,
            stop_reason=stop_reason,
            tokens_used=tokens_used,
            cost=0.0,
        )

    @staticmethod
    def _convert_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert standard message format to Gemini content format."""
        contents: List[Dict[str, Any]] = []
        for msg in messages:
            role = "user" if msg.get("role") in ("user", "tool") else "model"
            parts: List[Dict[str, str]] = []

            content = msg.get("content", "")
            if isinstance(content, str):
                parts.append({"text": content})
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and "text" in item:
                        parts.append({"text": item["text"]})

            if parts:
                contents.append({"role": role, "parts": parts})
        return contents

    @staticmethod
    def format_tool_result(call_id: str, output: str, is_error: bool = False) -> Dict[str, Any]:
        """Format a tool result for Gemini's format."""
        return {
            "role": "user",
            "content": f"Tool result for {call_id}: {output}",
        }

    @staticmethod
    def format_assistant_tool_use(
        tool_calls: List[ToolCall],
        text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Format assistant message with function calls for Gemini."""
        parts: List[Dict[str, Any]] = []
        if text:
            parts.append({"text": text})
        for tc in tool_calls:
            parts.append(
                {
                    "function_call": {
                        "name": tc.name,
                        "args": tc.arguments,
                    }
                }
            )
        return {"role": "model", "parts": parts}
