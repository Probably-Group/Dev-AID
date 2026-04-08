"""
Google (Gemini) provider adapter.

Implements tool-calling via the Gemini API with FunctionDeclaration format.
"""

import logging
from typing import Any, Dict, List, Optional

from ..core.cost import estimate_cost
from ..core.models import ToolCall, ToolResult
from ..core.provider_adapter import ProviderResponse

logger = logging.getLogger(__name__)


class GoogleAdapter:
    """Adapter for Google's Gemini function-calling API."""

    tool_format: str = "gemini"

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
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        response = gemini_model.generate_content(
            contents,
            tools=gemini_tools,
            generation_config=generation_config,
        )

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

        # Token usage and cost
        tokens_used = {"input": 0, "output": 0}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            um = response.usage_metadata
            tokens_used = {
                "input": getattr(um, "prompt_token_count", 0) or 0,
                "output": getattr(um, "candidates_token_count", 0) or 0,
            }
        cost = estimate_cost(model, tokens_used["input"], tokens_used["output"])

        return ProviderResponse(
            content=content_text,
            tool_calls=tool_calls,
            stop_reason=stop_reason,
            tokens_used=tokens_used,
            cost=cost,
        )

    @staticmethod
    def _convert_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert messages to Gemini content format.

        Passes through messages already in Gemini format (with 'parts' key).
        Converts generic messages (with 'content' key) to Gemini format.
        """
        contents: List[Dict[str, Any]] = []
        for msg in messages:
            # Already in Gemini format (has "parts" key)
            if "parts" in msg:
                contents.append(msg)
                continue

            # Convert from generic format
            role = "user" if msg.get("role") in ("user", "tool") else "model"
            parts: List[Dict[str, Any]] = []

            content = msg.get("content", "")
            if isinstance(content, str):
                if content:
                    parts.append({"text": content})
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        if "text" in item:
                            parts.append({"text": item["text"]})
                        elif item.get("type") == "tool_result":
                            # Convert Anthropic-style tool_result to text
                            parts.append({"text": str(item.get("content", ""))})

            if parts:
                contents.append({"role": role, "parts": parts})

        return contents

    @staticmethod
    def format_tool_result(
        call_id: str, output: str, is_error: bool = False
    ) -> Dict[str, Any]:
        """Format a single tool result for Gemini's function_response format."""
        return {
            "role": "user",
            "parts": [
                {
                    "function_response": {
                        "name": call_id,
                        "response": {"result": output, "is_error": is_error},
                    }
                }
            ],
        }

    @staticmethod
    def format_tool_results(results: List[ToolResult]) -> List[Dict[str, Any]]:
        """Format multiple tool results as a single message with function_response parts.

        Gemini expects all function responses in one 'user' message,
        each as a separate function_response part.
        """
        parts: List[Dict[str, Any]] = []
        for r in results:
            parts.append(
                {
                    "function_response": {
                        "name": r.name,
                        "response": {
                            "result": r.output if r.success else (r.error or ""),
                            "is_error": not r.success,
                        },
                    }
                }
            )
        return [{"role": "user", "parts": parts}]

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
