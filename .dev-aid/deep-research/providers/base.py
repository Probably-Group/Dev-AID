"""Base classes for research providers.

This module defines the abstract interface that all research providers must implement,
along with standardized data structures for research results.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ResearchDepth(Enum):
    """Research depth levels for query classification.

    - QUICK: Fast, basic search for simple facts (Tavily basic, ~3s)
    - STANDARD: Normal search with citations (Tavily advanced, Perplexity, ~5-10s)
    - DEEP: Multi-step comprehensive research (Gemini Deep Research, ~2-5 min)
    """

    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


@dataclass
class ResearchSource:
    """A single source from research results."""

    title: str
    url: str
    snippet: str = ""
    relevance_score: float = 0.0


@dataclass
class ResearchResult:
    """Standardized research result from any provider.

    Attributes:
        query: The original research query
        content: Synthesized research content/answer
        sources: List of sources with metadata
        provider: Name of the provider that generated this result
        depth: Research depth level used
        citations: List of citation URLs
        confidence_score: Provider confidence in results (0.0 to 1.0)
        processing_time_ms: Time taken to generate results
        cached: Whether this result came from cache
        cache_key: Cache key if result is cacheable
        metadata: Additional provider-specific metadata
    """

    query: str
    content: str
    sources: List[Dict[str, Any]]
    provider: str
    depth: ResearchDepth
    citations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    processing_time_ms: int = 0
    cached: bool = False
    cache_key: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "query": self.query,
            "content": self.content,
            "sources": self.sources,
            "provider": self.provider,
            "depth": self.depth.value,
            "citations": self.citations,
            "confidence_score": self.confidence_score,
            "processing_time_ms": self.processing_time_ms,
            "cached": self.cached,
            "cache_key": self.cache_key,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchResult":
        """Create from dictionary."""
        return cls(
            query=data["query"],
            content=data["content"],
            sources=data["sources"],
            provider=data["provider"],
            depth=ResearchDepth(data["depth"]),
            citations=data.get("citations", []),
            confidence_score=data.get("confidence_score", 0.0),
            processing_time_ms=data.get("processing_time_ms", 0),
            cached=data.get("cached", False),
            cache_key=data.get("cache_key"),
            metadata=data.get("metadata", {}),
        )


class ResearchProvider(ABC):
    """Abstract base class for research providers.

    All research providers (Tavily, Perplexity, Gemini) must implement this interface.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider name identifier."""
        pass

    @property
    @abstractmethod
    def supported_depths(self) -> List[ResearchDepth]:
        """List of research depths this provider supports."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        depth: ResearchDepth = ResearchDepth.STANDARD,
        max_sources: int = 10,
        **kwargs: Any,
    ) -> ResearchResult:
        """Execute a research query.

        Args:
            query: The research query to execute
            depth: Research depth level
            max_sources: Maximum number of sources to return
            **kwargs: Provider-specific options

        Returns:
            ResearchResult with synthesized content and sources

        Raises:
            ProviderError: If the search fails
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is configured and available.

        Returns:
            True if API key is configured and provider is ready
        """
        pass

    def supports_depth(self, depth: ResearchDepth) -> bool:
        """Check if provider supports a specific depth level."""
        return depth in self.supported_depths


class ProviderError(Exception):
    """Base exception for provider errors."""

    def __init__(
        self,
        message: str,
        provider: str,
        internal_error: Optional[str] = None,
    ):
        self.message = message
        self.provider = provider
        self.internal_error = internal_error
        super().__init__(f"[{provider}] {message}")


class ProviderNotAvailableError(ProviderError):
    """Raised when a provider is not available (missing API key, etc)."""

    pass


class ProviderRateLimitError(ProviderError):
    """Raised when provider rate limit is exceeded."""

    pass


class ProviderTimeoutError(ProviderError):
    """Raised when provider request times out."""

    pass
