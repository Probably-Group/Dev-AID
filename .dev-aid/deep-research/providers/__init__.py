"""Research providers for Dev-AID Deep Research"""

from .base import (
    ProviderError,
    ProviderNotAvailableError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ResearchDepth,
    ResearchProvider,
    ResearchResult,
)
from .gemini_deep import GeminiDeepResearchProvider
from .perplexity import PerplexityProvider
from .tavily import TavilyProvider

__all__ = [
    # Base classes
    "ResearchProvider",
    "ResearchResult",
    "ResearchDepth",
    # Errors
    "ProviderError",
    "ProviderNotAvailableError",
    "ProviderRateLimitError",
    "ProviderTimeoutError",
    # Providers
    "TavilyProvider",
    "PerplexityProvider",
    "GeminiDeepResearchProvider",
]
