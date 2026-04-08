"""Tests for research cache."""

import time
from pathlib import Path

import pytest
from cache.research_cache import ResearchCache
from providers.base import ResearchDepth, ResearchResult


class TestResearchCache:
    """Tests for ResearchCache."""

    @pytest.fixture
    def cache(self, temp_cache_dir):
        """Create cache instance with temp directory."""
        return ResearchCache(cache_dir=temp_cache_dir)

    @pytest.fixture
    def sample_result(self):
        """Create sample research result."""
        return ResearchResult(
            query="What is Python?",
            content="Python is a programming language.",
            sources=[
                {"title": "Python.org", "url": "https://python.org", "snippet": ""}
            ],
            provider="tavily",
            depth=ResearchDepth.QUICK,
            citations=["https://python.org"],
            confidence_score=0.8,
            processing_time_ms=1000,
        )

    def test_compute_key_deterministic(self, cache):
        """Test cache key computation is deterministic."""
        key1 = cache._compute_key("test query", "tavily", ResearchDepth.QUICK)
        key2 = cache._compute_key("test query", "tavily", ResearchDepth.QUICK)
        assert key1 == key2

    def test_compute_key_different_for_different_inputs(self, cache):
        """Test different inputs produce different keys."""
        key1 = cache._compute_key("query 1", "tavily", ResearchDepth.QUICK)
        key2 = cache._compute_key("query 2", "tavily", ResearchDepth.QUICK)
        key3 = cache._compute_key("query 1", "perplexity-sonar", ResearchDepth.QUICK)
        key4 = cache._compute_key("query 1", "tavily", ResearchDepth.DEEP)

        assert key1 != key2
        assert key1 != key3
        assert key1 != key4

    def test_set_and_get(self, cache, sample_result):
        """Test caching and retrieving result."""
        cache.set(sample_result)

        retrieved = cache.get(
            sample_result.query,
            sample_result.provider,
            sample_result.depth,
        )

        assert retrieved is not None
        assert retrieved.query == sample_result.query
        assert retrieved.content == sample_result.content
        assert retrieved.provider == sample_result.provider
        assert retrieved.cached is True

    def test_get_returns_none_for_missing(self, cache):
        """Test get returns None for missing entry."""
        result = cache.get("nonexistent query", "tavily", ResearchDepth.QUICK)
        assert result is None

    def test_cache_expiry(self, cache, sample_result):
        """Test cache entry expiry."""
        # Set with very short TTL
        cache.set(sample_result, ttl_hours=0)

        # Entry should be "expired" (0 hours TTL)
        # Force expiry by manipulating created_at
        key = cache._compute_key(
            sample_result.query,
            sample_result.provider,
            sample_result.depth,
        )
        if key in cache._index:
            cache._index[key].created_at = time.time() - 3700  # 1+ hour ago
            cache._save_index()

        # Should return None for expired entry
        retrieved = cache.get(
            sample_result.query,
            sample_result.provider,
            sample_result.depth,
        )
        assert retrieved is None

    def test_cleanup_expired(self, cache, sample_result):
        """Test cleanup of expired entries."""
        cache.set(sample_result)

        # Force all entries to be expired
        for key in cache._index:
            cache._index[key].created_at = time.time() - 200000  # Way past TTL
        cache._save_index()

        cleaned = cache.cleanup_expired()
        assert cleaned >= 1
        assert len(cache._index) == 0

    def test_invalidate_by_provider(self, cache, sample_result):
        """Test invalidation by provider."""
        cache.set(sample_result)

        count = cache.invalidate(provider="tavily")
        assert count >= 1

        # Should be gone
        retrieved = cache.get(
            sample_result.query,
            sample_result.provider,
            sample_result.depth,
        )
        assert retrieved is None

    def test_clear_all(self, cache, sample_result):
        """Test clearing all cache entries."""
        cache.set(sample_result)
        assert len(cache._index) > 0

        count = cache.clear_all()
        assert count >= 1
        assert len(cache._index) == 0

    def test_get_stats(self, cache, sample_result):
        """Test getting cache statistics."""
        cache.set(sample_result)

        stats = cache.get_stats()

        assert stats["total_entries"] >= 1
        assert "cache_directory" in stats
        assert "providers" in stats
        assert "tavily" in stats["providers"]
