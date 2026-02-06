"""
API Clients for Different AI Providers

Provides unified interface for:
- Anthropic (Claude)
- Google (Gemini)
- OpenAI (GPT)

Supports both API key and session-based authentication.
"""

from typing import Any, Dict

from ..auth_detector import AuthCredentials
from .anthropic_client import AnthropicClient
from .base import APIClientError, APIResponse, BaseAIClient, Message, track_api_call
from .google_client import GoogleClient
from .openai_client import OpenAIClient

# Re-export all public symbols for backward compatibility
__all__ = [
    "APIClientError",
    "APIResponse",
    "BaseAIClient",
    "Message",
    "track_api_call",
    "AnthropicClient",
    "GoogleClient",
    "OpenAIClient",
    "create_client",
]


def create_client(
    provider: str,
    auth: AuthCredentials,
    model_config: Dict[str, Any],
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
    from ..local_client import LocalLLMClient

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
