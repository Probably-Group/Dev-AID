"""
Provider adapter protocol and factory.

Defines the ProviderAdapter protocol that all provider adapters must implement,
and a factory function to create the appropriate adapter.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from .models import ToolCall

logger = logging.getLogger(__name__)


@dataclass
class ProviderResponse:
    """Response from a provider's tool-calling API."""

    content: Optional[str] = None  # Text content (None if only tool calls)
    tool_calls: List[ToolCall] = field(default_factory=list)
    stop_reason: str = "end_turn"  # "end_turn", "tool_use", "max_tokens"
    tokens_used: Dict[str, int] = field(
        default_factory=lambda: {"input": 0, "output": 0}
    )
    cost: float = 0.0


@runtime_checkable
class ProviderAdapter(Protocol):
    """Protocol for provider-specific adapters."""

    def send_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        system_prompt: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.3,
    ) -> ProviderResponse:
        """Send messages with tool definitions to the provider."""
        ...


def create_adapter(
    provider: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs: Any,
) -> ProviderAdapter:
    """
    Factory function to create the appropriate provider adapter.

    Args:
        provider: Provider name (anthropic, openai, google, local)
        api_key: API key for authentication
        base_url: Base URL override (for local models)

    Returns:
        Configured ProviderAdapter instance
    """
    provider_lower = provider.lower()

    if provider_lower == "anthropic":
        from ..adapters.anthropic_adapter import AnthropicAdapter

        return AnthropicAdapter(api_key=api_key)

    elif provider_lower in ("openai", "local"):
        from ..adapters.openai_adapter import OpenAIAdapter

        return OpenAIAdapter(
            api_key=api_key or "not-needed",
            base_url=base_url,
        )

    elif provider_lower == "google":
        from ..adapters.google_adapter import GoogleAdapter

        return GoogleAdapter(api_key=api_key)

    else:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported: anthropic, openai, google, local"
        )
