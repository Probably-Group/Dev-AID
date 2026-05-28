"""Aggressive caching layer for research results.

Implements file-based caching with 24-48 hour TTL to minimize API calls
and reduce costs across repeated queries.
"""

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from providers.base import ResearchDepth, ResearchResult

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry metadata."""

    query_hash: str
    provider: str
    depth: str
    created_at: float
    ttl_hours: int
    query_preview: str  # First 100 chars of query for debugging


class ResearchCache:
    """File-based research cache with TTL.

    Cache is stored in ~/.dev-aid/cache/research/ with:
    - index.json: Cache entry metadata
    - {hash}.json: Individual cached results
    """

    DEFAULT_TTL_HOURS = 24
    MAX_TTL_HOURS = 48

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize cache.

        Args:
            cache_dir: Cache directory. Defaults to ~/.dev-aid/cache/research/
        """
        self.cache_dir = cache_dir or Path.home() / ".dev-aid" / "cache" / "research"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "index.json"
        self._index: Dict[str, CacheEntry] = {}
        self._load_index()

    def _compute_key(self, query: str, provider: str, depth: ResearchDepth) -> str:
        """Compute cache key from query parameters.

        Args:
            query: The research query
            provider: Provider name
            depth: Research depth

        Returns:
            16-character hash key
        """
        # Normalize query for better cache hits
        normalized = query.lower().strip()
        # Remove extra whitespace
        normalized = " ".join(normalized.split())

        key_input = f"{normalized}:{provider}:{depth.value}"
        return hashlib.sha256(key_input.encode()).hexdigest()[:16]

    def get(
        self, query: str, provider: str, depth: ResearchDepth
    ) -> Optional[ResearchResult]:
        """Get cached result if valid.

        Args:
            query: The research query
            provider: Provider name
            depth: Research depth

        Returns:
            Cached ResearchResult or None if not found/expired
        """
        key = self._compute_key(query, provider, depth)

        if key not in self._index:
            return None

        entry = self._index[key]

        # Check TTL
        age_hours = (time.time() - entry.created_at) / 3600
        if age_hours > entry.ttl_hours:
            logger.debug(f"Cache expired for key {key} (age: {age_hours:.1f}h)")
            self._evict(key)
            return None

        # Load result from file
        cache_file = self.cache_dir / f"{key}.json"
        if not cache_file.exists():
            logger.warning(f"Cache file missing for key {key}")
            self._evict(key)
            return None

        try:
            with open(cache_file, "r") as f:
                data = json.load(f)

            # Mark as cached
            data["cached"] = True
            data["cache_key"] = key

            result = ResearchResult.from_dict(data)

            logger.info(
                f"Cache hit: {key} (age: {age_hours:.1f}h, provider: {provider})"
            )
            return result

        except Exception as e:
            logger.warning(f"Cache read error for {key}: {e}")
            self._evict(key)
            return None

    def set(
        self,
        result: ResearchResult,
        ttl_hours: int = DEFAULT_TTL_HOURS,
    ) -> str:
        """Cache research result.

        Args:
            result: The research result to cache
            ttl_hours: Time-to-live in hours (max 48)

        Returns:
            Cache key
        """
        ttl_hours = min(ttl_hours, self.MAX_TTL_HOURS)
        key = self._compute_key(result.query, result.provider, result.depth)

        # Serialize result
        data = result.to_dict()

        # Write to cache file
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write cache file {key}: {e}")
            return key

        # Update index
        self._index[key] = CacheEntry(
            query_hash=key,
            provider=result.provider,
            depth=result.depth.value,
            created_at=time.time(),
            ttl_hours=ttl_hours,
            query_preview=result.query[:100],
        )
        self._save_index()

        logger.info(
            f"Cached result: {key} (provider: {result.provider}, TTL: {ttl_hours}h)"
        )
        return key

    def invalidate(
        self,
        query: Optional[str] = None,
        provider: Optional[str] = None,
        depth: Optional[ResearchDepth] = None,
    ) -> int:
        """Invalidate cache entries matching criteria.

        Args:
            query: Specific query to invalidate
            provider: Invalidate all entries from this provider
            depth: Invalidate all entries at this depth

        Returns:
            Number of entries invalidated
        """
        to_evict = []

        for key, entry in self._index.items():
            should_evict = False

            if query:
                # Compute key for this query/provider/depth combo
                if provider and depth:
                    target_key = self._compute_key(query, provider, depth)
                    should_evict = key == target_key

            if provider and entry.provider == provider:
                should_evict = True

            if depth and entry.depth == depth.value:
                should_evict = True

            if should_evict:
                to_evict.append(key)

        for key in to_evict:
            self._evict(key)

        return len(to_evict)

    def cleanup_expired(self) -> int:
        """Remove all expired entries.

        Returns:
            Number of entries cleaned up
        """
        expired = []
        current_time = time.time()

        for key, entry in self._index.items():
            age_hours = (current_time - entry.created_at) / 3600
            if age_hours > entry.ttl_hours:
                expired.append(key)

        for key in expired:
            self._evict(key)

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired cache entries")

        return len(expired)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total_size = 0
        for cache_file in self.cache_dir.glob("*.json"):
            if cache_file.name != "index.json":
                total_size += cache_file.stat().st_size

        return {
            "total_entries": len(self._index),
            "cache_directory": str(self.cache_dir),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "providers": self._count_by_provider(),
        }

    def _count_by_provider(self) -> Dict[str, int]:
        """Count entries by provider."""
        counts: Dict[str, int] = {}
        for entry in self._index.values():
            counts[entry.provider] = counts.get(entry.provider, 0) + 1
        return counts

    def _evict(self, key: str) -> None:
        """Remove cache entry.

        Args:
            key: Cache key to remove
        """
        if key in self._index:
            del self._index[key]

        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete cache file {key}: {e}")

        self._save_index()

    def _load_index(self) -> None:
        """Load cache index from disk."""
        if not self.index_file.exists():
            self._index = {}
            return

        try:
            with open(self.index_file, "r") as f:
                data = json.load(f)

            self._index = {k: CacheEntry(**v) for k, v in data.items()}

            logger.debug(f"Loaded cache index with {len(self._index)} entries")

        except Exception as e:
            logger.warning(f"Failed to load cache index: {e}")
            self._index = {}

    def _save_index(self) -> None:
        """Save cache index to disk."""
        try:
            data = {k: asdict(v) for k, v in self._index.items()}
            with open(self.index_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")

    def clear_all(self) -> int:
        """Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        count = len(self._index)

        # Delete all cache files
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete {cache_file}: {e}")

        self._index = {}

        logger.info(f"Cleared all {count} cache entries")
        return count
