"""Anthropic (Claude) API client implementation."""

import logging
from typing import Any, Dict, List

from .base import APIResponse, BaseAIClient, Message, track_api_call
from ..auth_detector import AuthCredentials

logger = logging.getLogger(__name__)


class AnthropicClient(BaseAIClient):
    """Client for Anthropic Claude API"""

    def __init__(self, auth: AuthCredentials, model_config: Dict[str, Any]):
        super().__init__(auth, model_config)

        try:
            import anthropic

            if auth.auth_type == "session":
                # Use session token (experimental)
                # Note: Anthropic SDK doesn't officially support session tokens yet
                # This is a workaround that may need adjustment
                logger.warning(
                    "Using Claude session token (experimental). "
                    "If requests fail, please set ANTHROPIC_API_KEY or run 'claude login'"
                )
                # Try to use session token in Authorization header
                self.client = anthropic.Anthropic(
                    api_key="session-token",  # SDK requires api_key parameter
                    default_headers={
                        "Authorization": f"Bearer {auth.credentials['session_token']}"
                    },
                )
            elif auth.auth_type == "api_key":
                # Traditional API key auth
                self.client = anthropic.Anthropic(api_key=auth.credentials["api_key"])
            else:
                raise ValueError(f"Unsupported auth type for Anthropic: {auth.auth_type}")

        except ImportError:
            raise ImportError(
                "anthropic package not installed. " "Install with: pip install anthropic"
            )

    @track_api_call
    def send_request(
        self,
        messages: List[Message],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> APIResponse:
        """Send request to Anthropic API"""

        # Convert messages to Anthropic format
        api_messages = []
        system_message = None

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                api_messages.append({"role": msg.role, "content": msg.content})

        # Prepare request parameters
        request_params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": api_messages,
        }

        if system_message:
            request_params["system"] = system_message

        # Add any additional kwargs
        request_params.update(kwargs)

        # Make API call (timing and error handling via decorator)
        response = self.client.messages.create(**request_params)  # type: ignore

        # Extract response data
        content = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        # Calculate cost
        cost = self.calculate_cost(input_tokens, output_tokens)

        return APIResponse(
            content=content,
            model=model,
            provider="anthropic",
            tokens_used={"input": input_tokens, "output": output_tokens},
            cost=cost,
            latency_ms=None,  # Set by decorator
            metadata={"stop_reason": response.stop_reason, "response_id": response.id},
        )
