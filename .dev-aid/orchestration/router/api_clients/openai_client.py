"""OpenAI (GPT) API client implementation."""

import logging
from typing import Any, Dict, List

from ..auth_detector import AuthCredentials
from .base import APIResponse, BaseAIClient, Message, track_api_call

logger = logging.getLogger(__name__)


class OpenAIClient(BaseAIClient):
    """Client for OpenAI API"""

    def __init__(self, auth: AuthCredentials, model_config: Dict[str, Any]):
        super().__init__(auth, model_config)

        try:
            import openai

            if auth.auth_type == "api_key":
                # OpenAI only supports API key authentication
                self.client = openai.OpenAI(api_key=auth.credentials["api_key"])
            else:
                raise ValueError(
                    f"Unsupported auth type for OpenAI: {auth.auth_type}. "
                    "OpenAI only supports API key authentication. "
                    "Note: ChatGPT Plus subscription does NOT include API access."
                )
        except ImportError:
            raise ImportError("openai package not installed. " "Install with: pip install openai")

    @track_api_call
    def send_request(
        self,
        messages: List[Message],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> APIResponse:
        """Send request to OpenAI API"""

        # Convert messages to OpenAI format
        api_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        # Make API call (timing and error handling via decorator)
        response = self.client.chat.completions.create(
            model=model,
            messages=api_messages,  # type: ignore[arg-type]
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

        # Extract response data. The OpenAI SDK types `message.content` and
        # `response.usage` as Optional — content is None when the model
        # emits only tool_calls, and usage can be None on streaming chunks.
        # Coerce both to safe defaults so the APIResponse contract holds.
        content = response.choices[0].message.content or ""
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0

        # Calculate cost
        cost = self.calculate_cost(input_tokens, output_tokens)

        return APIResponse(
            content=content,
            model=model,
            provider="openai",
            tokens_used={"input": input_tokens, "output": output_tokens},
            cost=cost,
            latency_ms=None,  # Set by decorator
            metadata={
                "finish_reason": response.choices[0].finish_reason,
                "response_id": response.id,
            },
        )
