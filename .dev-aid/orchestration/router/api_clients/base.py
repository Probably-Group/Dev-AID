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
        # perf_counter (not time.time): time.time() is wall clock and can
        # jump backwards on NTP adjustments, producing negative latencies.
        # perf_counter is monotonic and has sub-microsecond resolution on
        # every supported platform — including Windows, where time.monotonic
        # only has ~15 ms granularity. See StopWatch in agents/core/models.py.
        start_time = time.perf_counter()

        try:
            # Call the actual send_request implementation
            response = func(self, *args, **kwargs)

            # Calculate and attach latency if not already set
            if response.latency_ms is None:
                response.latency_ms = (time.perf_counter() - start_time) * 1000

            return response

        except APIClientError:
            # Already a safe error, re-raise as-is
            raise

        except Exception as e:
            # Log full error internally with provider context
            provider = getattr(self, "provider", "unknown")
            logger.error(
                f"{provider.title()} API error: {type(e).__name__}: {str(e)}",
                exc_info=True,
            )
            # Raise a safe error (no sensitive details) but preserve enough
            # classification for callers to act correctly: an auth/bad-request
            # failure must not be reported as "please try again" (audit H4/M16).
            status = getattr(e, "status_code", None)
            status = status if isinstance(status, int) else None
            if _is_auth_error(e, status):
                message = "Authentication failed for the AI provider. Check the API key."
                retryable = False
            elif status in _FATAL_STATUS:
                message = "The AI provider rejected the request."
                retryable = False
            elif _is_transient_error(e, status):
                message = "The AI provider is temporarily unavailable. Please retry."
                retryable = True
            else:
                message = "Failed to communicate with AI provider. Please try again."
                retryable = True
            raise APIClientError(message, retryable=retryable, status_code=status) from e

    return cast(F, wrapper)


# HTTP statuses that are never worth retrying (permanent).
_FATAL_STATUS = frozenset({400, 401, 403, 404, 405, 422})
_TRANSIENT_STATUS = frozenset({408, 409, 425, 429, 500, 502, 503, 504, 529})


def _is_auth_error(exc: BaseException, status: Optional[int]) -> bool:
    if status in (401, 403):
        return True
    name = type(exc).__name__.lower()
    return "authentication" in name or "permissiondenied" in name


def _is_transient_error(exc: BaseException, status: Optional[int]) -> bool:
    if status in _TRANSIENT_STATUS:
        return True
    name = type(exc).__name__.lower()
    return any(h in name for h in ("ratelimit", "timeout", "connection", "overloaded"))


class APIClientError(Exception):
    """Safe API client error that doesn't leak details.

    Carries a coarse ``retryable`` flag and ``status_code`` so callers can
    distinguish a transient outage from a permanent config error without
    seeing provider internals.
    """

    def __init__(
        self,
        message: str,
        *,
        retryable: bool = False,
        status_code: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.status_code = status_code


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
    # Parsed tool_calls when the model emits structured function calls.
    # Each entry is shaped like the OpenAI tool-calls spec:
    #   {"id": str, "type": "function",
    #    "function": {"name": str, "arguments": str}}
    # where `arguments` is a JSON-encoded string (consumers parse it). Cloud
    # clients that don't yet populate this leave it as None — see issue #140
    # for the local-client implementation that surfaces it from Ollama.
    tool_calls: Optional[List[Dict[str, Any]]] = None


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
