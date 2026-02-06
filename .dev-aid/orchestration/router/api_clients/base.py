"""
Base classes, data models, and decorators for AI provider clients.

Contains:
- Message, APIResponse, APIClientError data classes
- BaseAIClient abstract base class
- track_api_call decorator for consistent timing and error handling
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

from ..auth_detector import AuthCredentials

F = TypeVar("F", bound=Callable[..., Any])

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
