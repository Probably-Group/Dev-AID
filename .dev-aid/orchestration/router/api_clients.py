"""
API Clients for Different AI Providers

Provides unified interface for:
- Anthropic (Claude)
- Google (Gemini)
- OpenAI (GPT)

Supports both API key and session-based authentication.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

from .auth_detector import AuthCredentials

F = TypeVar("F", bound=Callable[..., Any])

# Configure logger
logger = logging.getLogger(__name__)


def track_api_call(func: F) -> F:
    """
    Decorator to track API call timing and handle errors consistently.

    This eliminates code duplication across all API clients by:
    - Measuring request latency
    - Handling exceptions with logging
    - Converting provider exceptions to safe APIClientError
    """

    @wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        start_time = time.time()

        try:
            # Call the actual send_request implementation
            response = func(self, *args, **kwargs)

            # Calculate and attach latency if not already set
            if response.latency_ms is None:
                response.latency_ms = (time.time() - start_time) * 1000

            return response

        except APIClientError:
            # Already a safe error, re-raise as-is
            raise

        except Exception as e:
            # Log full error internally with provider context
            provider = getattr(self, "provider", "unknown")
            logger.error(
                f"{provider.title()} API error: {type(e).__name__}: {str(e)}", exc_info=True
            )
            # Raise safe error to user (no sensitive details)
            raise APIClientError("Failed to communicate with AI provider. Please try again.")

    return cast(F, wrapper)


class APIClientError(Exception):
    """Safe API client error that doesn't leak details"""


@dataclass
class Message:
    """Represents a chat message"""

    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class APIResponse:
    """Unified response format from all providers"""

    content: str
    model: str
    provider: str
    tokens_used: Dict[str, int]  # {"input": N, "output": M}
    cost: Optional[float] = None
    latency_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseAIClient(ABC):
    """Base class for AI provider clients"""

    def __init__(self, auth: AuthCredentials, model_config: Dict[str, Any]):
        """
        Initialize AI client

        Args:
            auth: Authentication credentials (session or API key)
            model_config: Model configuration from models.json
        """
        self.auth = auth
        self.model_config = model_config
        self.provider = model_config.get("provider", "unknown")

        # Backward compatibility: expose api_key if auth_type is api_key
        self.api_key = auth.credentials.get("api_key") if auth.auth_type == "api_key" else None

    @abstractmethod
    def send_request(
        self,
        messages: List[Message],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> APIResponse:
        """
        Send request to AI provider

        Args:
            messages: List of messages (conversation history)
            model: Model ID to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 - 1.0)
            **kwargs: Provider-specific parameters

        Returns:
            APIResponse object
        """

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost based on token usage

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        costs = self.model_config.get("cost_per_1m_tokens", {})
        input_cost_per_m = costs.get("input", 0)
        output_cost_per_m = costs.get("output", 0)

        input_cost = (input_tokens / 1_000_000) * cast(float, input_cost_per_m)
        output_cost = (output_tokens / 1_000_000) * cast(float, output_cost_per_m)

        return input_cost + output_cost


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
                input_tokens = int(len(prompt.split()) * 1.3)
            if output_tokens == 0:
                output_tokens = int(len(content.split()) * 1.3)

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
                input_tokens = int(len(total_input.split()) * 1.3)
            if output_tokens == 0:
                output_tokens = int(len(content.split()) * 1.3)

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

        # Extract response data
        content = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

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


def create_client(
    provider: str, auth: AuthCredentials, model_config: Dict[str, Any]
) -> BaseAIClient:
    """
    Factory function to create appropriate AI client

    Args:
        provider: Provider name ("anthropic", "google", "openai", "local")
        auth: Authentication credentials (session or API key)
        model_config: Model configuration

    Returns:
        Appropriate client instance

    Raises:
        ValueError: If provider is not supported
    """
    # Import LocalLLMClient lazily to avoid circular imports
    from .local_client import LocalLLMClient

    clients: Dict[str, type[BaseAIClient]] = {
        "anthropic": AnthropicClient,
        "google": GoogleClient,
        "openai": OpenAIClient,
        "local": LocalLLMClient,
    }

    client_class = clients.get(provider.lower())

    if not client_class:
        raise ValueError(
            f"Unsupported provider: {provider}\n"
            f"Supported providers: {', '.join(clients.keys())}"
        )

    return client_class(auth, model_config)


# Example usage
if __name__ == "__main__":
    # This is for testing purposes
    print("API Clients module - ready for import")
    print("Supported providers: Anthropic, Google (Gemini), OpenAI")
