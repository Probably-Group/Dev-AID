"""Google (Gemini) API client implementation."""

import logging
from typing import Any, Dict, List

from ..auth_detector import AuthCredentials
from ..token_estimation import estimate_tokens
from .base import APIResponse, BaseAIClient, Message, track_api_call

logger = logging.getLogger(__name__)


class GoogleClient(BaseAIClient):
    """Client for Google Gemini API"""

    def __init__(self, auth: AuthCredentials, model_config: Dict[str, Any]):
        super().__init__(auth, model_config)

        try:
            from google import genai
            from google.genai import types

            if auth.auth_type == "adc":
                # Use Application Default Credentials
                # Google SDK automatically detects ADC from gcloud auth
                logger.info("Using Google Application Default Credentials (ADC)")
                self.client = genai.Client()  # No api_key needed!
            elif auth.auth_type == "api_key":
                # Traditional API key auth
                self.client = genai.Client(api_key=auth.credentials["api_key"])
            else:
                raise ValueError(f"Unsupported auth type for Google: {auth.auth_type}")

            self.types = types
        except ImportError:
            raise ImportError(
                "google-genai package not installed. " "Install with: pip install google-genai"
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
        """Send request to Google Gemini API"""

        # Convert messages to Gemini format
        # Gemini uses a different format - combine messages into conversation
        conversation_parts: List[Dict[str, Any]] = []
        system_instruction = None

        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            elif msg.role == "user":
                conversation_parts.append({"role": "user", "parts": [{"text": msg.content}]})
            elif msg.role == "assistant":
                conversation_parts.append({"role": "model", "parts": [{"text": msg.content}]})

        # Build generation config
        config = self.types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_instruction if system_instruction else None,
        )

        # For simple single-turn requests
        if len(conversation_parts) == 1 and conversation_parts[0]["role"] == "user":
            prompt = conversation_parts[0]["parts"][0]["text"]

            # Make API call (timing and error handling via decorator)
            response = self.client.models.generate_content(
                model=model, contents=prompt, config=config
            )

            # Extract response
            content = response.text

            # Try to get token counts from response
            input_tokens = getattr(
                getattr(response, "usage_metadata", None), "prompt_token_count", 0
            )
            output_tokens = getattr(
                getattr(response, "usage_metadata", None), "candidates_token_count", 0
            )

            # Fallback to estimation if not available
            if input_tokens == 0:
                input_tokens = estimate_tokens(prompt)
            if output_tokens == 0:
                output_tokens = estimate_tokens(content)

            # Calculate cost
            cost = self.calculate_cost(int(input_tokens), int(output_tokens))

            return APIResponse(
                content=content,
                model=model,
                provider="google",
                tokens_used={"input": int(input_tokens), "output": int(output_tokens)},
                cost=cost,
                latency_ms=None,  # Set by decorator
                metadata={
                    "finish_reason": (
                        getattr(response.candidates[0], "finish_reason", None)
                        if hasattr(response, "candidates") and response.candidates
                        else None
                    )
                },
            )

        else:
            # Multi-turn conversation - send full history
            # Make API call (timing and error handling via decorator)
            response = self.client.models.generate_content(
                model=model, contents=conversation_parts, config=config
            )

            content = response.text

            # Try to get token counts
            input_tokens = getattr(
                getattr(response, "usage_metadata", None), "prompt_token_count", 0
            )
            output_tokens = getattr(
                getattr(response, "usage_metadata", None), "candidates_token_count", 0
            )

            # Fallback to estimation
            if input_tokens == 0:
                total_input = " ".join([p["parts"][0]["text"] for p in conversation_parts])
                input_tokens = estimate_tokens(total_input)
            if output_tokens == 0:
                output_tokens = estimate_tokens(content)

            cost = self.calculate_cost(int(input_tokens), int(output_tokens))

            return APIResponse(
                content=content,
                model=model,
                provider="google",
                tokens_used={"input": int(input_tokens), "output": int(output_tokens)},
                cost=cost,
                latency_ms=None,  # Set by decorator
                metadata={
                    "finish_reason": (
                        getattr(response.candidates[0], "finish_reason", None)
                        if hasattr(response, "candidates") and response.candidates
                        else None
                    )
                },
            )
