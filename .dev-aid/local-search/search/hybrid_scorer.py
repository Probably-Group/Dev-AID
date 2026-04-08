"""Hybrid search combining BM25 lexical search with vector semantic search"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from chunking.chunker import CodeChunk
from search.bm25 import BM25Index, BM25Result
from search.index import CodeSearchIndex, SearchResult

logger = logging.getLogger(__name__)


@dataclass
class HybridResult:
    """Hybrid search result combining BM25 and vector scores"""

    chunk: CodeChunk
    combined_score: float
    bm25_score: float
    vector_score: float
    rank: int
    matched_terms: List[str]  # Terms matched by BM25


class HybridSearcher:
    """
    Hybrid search combining BM25 (lexical) and vector (semantic) search.

    Uses Reciprocal Rank Fusion (RRF) or weighted combination to merge
    results from both search methods.
    """

    def __init__(
        self,
        index_dir: str,
        alpha: float = 0.5,
        fusion_method: str = "reciprocal_rank",
        normalize_scores: bool = True,
        embedding_dim: int = 384,
    ):
        """
        Initialize hybrid searcher.

        Args:
            index_dir: Directory containing search indices
            alpha: Weight for vector search (0.0 = pure BM25, 1.0 = pure vector)
            fusion_method: 'reciprocal_rank' or 'weighted_sum'
            normalize_scores: Whether to normalize scores before fusion
            embedding_dim: Dimension of embedding vectors
        """
        self.index_dir = Path(index_dir)
        self.alpha = alpha
        self.fusion_method = fusion_method
        self.normalize_scores = normalize_scores

        # Initialize both indices
        self.vector_index = CodeSearchIndex(str(index_dir), embedding_dim)
        self.bm25_index = BM25Index(str(index_dir))

        # Load config if available
        self._load_config()

    def _load_config(self):
        """Load configuration from search.json if available."""
        # Look for config in parent directories
        config_paths = [
            self.index_dir.parent.parent / "config" / "search.json",
            self.index_dir.parent / "config" / "search.json",
            Path.cwd() / ".dev-aid" / "config" / "search.json",
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, "r") as f:
                        config = json.load(f)

                    hybrid_config = config.get("hybrid", {})
                    self.alpha = hybrid_config.get("alpha", self.alpha)
                    self.fusion_method = hybrid_config.get(
                        "fusion_method", self.fusion_method
                    )
                    self.normalize_scores = hybrid_config.get(
                        "normalize_scores", self.normalize_scores
                    )

                    logger.info(
                        f"Loaded hybrid search config: alpha={self.alpha}, fusion={self.fusion_method}"
                    )
                    return
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Error loading search config: {e}")

    def build(self, chunks: List[CodeChunk], embeddings: np.ndarray):
        """
        Build both indices from chunks.

        Args:
            chunks: List of code chunks
            embeddings: Embedding vectors for vector search
        """
        # Build vector index
        self.vector_index.build(chunks, embeddings)

        # Build BM25 index
        self.bm25_index.build(chunks)

        logger.info(f"Built hybrid index with {len(chunks)} chunks")

    def search(
        self,
        query: str,
        query_embedding: np.ndarray,
        top_k: int = 10,
        alpha: Optional[float] = None,
    ) -> List[HybridResult]:
        """
        Perform hybrid search combining BM25 and vector results.

        Args:
            query: Text query for BM25
            query_embedding: Query embedding for vector search
            top_k: Number of results to return
            alpha: Override alpha weight (optional)

        Returns:
            List of hybrid results ordered by combined score
        """
        alpha = alpha if alpha is not None else self.alpha

        # Get more results from each method for better fusion
        fetch_k = min(top_k * 3, max(50, top_k))

        # Vector search
        vector_results = self.vector_index.search(query_embedding, fetch_k)

        # BM25 search
        bm25_results = self.bm25_index.search(query, fetch_k)

        # Combine results
        if self.fusion_method == "reciprocal_rank":
            combined = self._reciprocal_rank_fusion(vector_results, bm25_results, alpha)
        else:
            combined = self._weighted_sum_fusion(vector_results, bm25_results, alpha)

        # Sort by combined score and take top_k
        combined.sort(key=lambda x: x.combined_score, reverse=True)
        results = combined[:top_k]

        # Assign ranks
        for i, result in enumerate(results):
            result.rank = i + 1

        return results

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[SearchResult],
        bm25_results: List[BM25Result],
        alpha: float,
        k: int = 60,  # RRF constant
    ) -> List[HybridResult]:
        """
        Combine results using Reciprocal Rank Fusion.

        RRF formula: score(d) = sum(1 / (k + rank(d)))

        Args:
            vector_results: Results from vector search
            bm25_results: Results from BM25 search
            alpha: Weight for vector scores
            k: RRF smoothing constant

        Returns:
            List of hybrid results
        """
        # Build lookup maps
        chunk_scores: Dict[str, Dict[str, Any]] = {}

        # Process vector results
        for vec_result in vector_results:
            chunk_id = self._chunk_id(vec_result.chunk)
            rrf_score = 1.0 / (k + vec_result.rank)

            if chunk_id not in chunk_scores:
                chunk_scores[chunk_id] = {
                    "chunk": vec_result.chunk,
                    "vector_rrf": 0.0,
                    "bm25_rrf": 0.0,
                    "vector_score": vec_result.score,
                    "bm25_score": 0.0,
                    "matched_terms": [],
                }
            chunk_scores[chunk_id]["vector_rrf"] = rrf_score
            chunk_scores[chunk_id]["vector_score"] = vec_result.score

        # Process BM25 results
        for bm25_result in bm25_results:
            chunk_id = self._chunk_id(bm25_result.chunk)
            rrf_score = 1.0 / (k + bm25_result.rank)

            if chunk_id not in chunk_scores:
                chunk_scores[chunk_id] = {
                    "chunk": bm25_result.chunk,
                    "vector_rrf": 0.0,
                    "bm25_rrf": 0.0,
                    "vector_score": 0.0,
                    "bm25_score": bm25_result.score,
                    "matched_terms": bm25_result.matched_terms,
                }
            else:
                chunk_scores[chunk_id]["bm25_rrf"] = rrf_score
                chunk_scores[chunk_id]["bm25_score"] = bm25_result.score
                chunk_scores[chunk_id]["matched_terms"] = bm25_result.matched_terms

        # Calculate combined scores
        results = []
        for chunk_id, data in chunk_scores.items():
            # Weighted combination of RRF scores
            combined = alpha * data["vector_rrf"] + (1 - alpha) * data["bm25_rrf"]

            results.append(
                HybridResult(
                    chunk=data["chunk"],
                    combined_score=combined,
                    bm25_score=data["bm25_score"],
                    vector_score=data["vector_score"],
                    rank=0,  # Will be set after sorting
                    matched_terms=data["matched_terms"],
                )
            )

        return results

    def _weighted_sum_fusion(
        self,
        vector_results: List[SearchResult],
        bm25_results: List[BM25Result],
        alpha: float,
    ) -> List[HybridResult]:
        """
        Combine results using weighted sum of normalized scores.

        Args:
            vector_results: Results from vector search
            bm25_results: Results from BM25 search
            alpha: Weight for vector scores

        Returns:
            List of hybrid results
        """
        # Normalize scores if configured
        if self.normalize_scores:
            vector_scores = [r.score for r in vector_results]
            bm25_scores = [r.score for r in bm25_results]

            vector_max = max(vector_scores) if vector_scores else 1.0
            bm25_max = max(bm25_scores) if bm25_scores else 1.0
        else:
            vector_max = 1.0
            bm25_max = 1.0

        # Build lookup maps
        chunk_scores: Dict[str, Dict[str, Any]] = {}

        # Process vector results
        for vec_result in vector_results:
            chunk_id = self._chunk_id(vec_result.chunk)
            norm_score = vec_result.score / vector_max if vector_max > 0 else 0

            if chunk_id not in chunk_scores:
                chunk_scores[chunk_id] = {
                    "chunk": vec_result.chunk,
                    "vector_score": norm_score,
                    "bm25_score": 0.0,
                    "matched_terms": [],
                }
            else:
                chunk_scores[chunk_id]["vector_score"] = norm_score

        # Process BM25 results
        for bm25_result in bm25_results:
            chunk_id = self._chunk_id(bm25_result.chunk)
            norm_score = bm25_result.score / bm25_max if bm25_max > 0 else 0

            if chunk_id not in chunk_scores:
                chunk_scores[chunk_id] = {
                    "chunk": bm25_result.chunk,
                    "vector_score": 0.0,
                    "bm25_score": norm_score,
                    "matched_terms": bm25_result.matched_terms,
                }
            else:
                chunk_scores[chunk_id]["bm25_score"] = norm_score
                chunk_scores[chunk_id]["matched_terms"] = bm25_result.matched_terms

        # Calculate combined scores
        results = []
        for chunk_id, data in chunk_scores.items():
            combined = alpha * data["vector_score"] + (1 - alpha) * data["bm25_score"]

            results.append(
                HybridResult(
                    chunk=data["chunk"],
                    combined_score=combined,
                    bm25_score=data["bm25_score"],
                    vector_score=data["vector_score"],
                    rank=0,
                    matched_terms=data["matched_terms"],
                )
            )

        return results

    def _chunk_id(self, chunk: CodeChunk) -> str:
        """Generate unique identifier for a chunk."""
        return f"{chunk.file_path}:{chunk.start_line}-{chunk.end_line}"

    def search_vector_only(
        self, query_embedding: np.ndarray, top_k: int = 10
    ) -> List[SearchResult]:
        """Pure vector search."""
        return self.vector_index.search(query_embedding, top_k)

    def search_bm25_only(self, query: str, top_k: int = 10) -> List[BM25Result]:
        """Pure BM25 search."""
        return self.bm25_index.search(query, top_k)

    def save(self):
        """Save both indices."""
        self.vector_index.save()
        self.bm25_index.save()

    def load(self):
        """Load both indices."""
        self.vector_index.load()
        self.bm25_index.load()

    def get_stats(self) -> Dict[str, Any]:
        """Get combined statistics."""
        return {
            "alpha": self.alpha,
            "fusion_method": self.fusion_method,
            "normalize_scores": self.normalize_scores,
            "vector_index": self.vector_index.get_stats(),
            "bm25_index": self.bm25_index.get_stats(),
        }

    def clear(self):
        """Clear both indices."""
        self.vector_index.clear()
        self.bm25_index.clear()


def compare_search_methods(
    searcher: HybridSearcher, query: str, query_embedding: np.ndarray, top_k: int = 5
) -> Dict[str, Any]:
    """
    Compare results from different search methods.

    Useful for tuning alpha and evaluating search quality.

    Args:
        searcher: Hybrid searcher instance
        query: Text query
        query_embedding: Query embedding
        top_k: Number of results per method

    Returns:
        Comparison data with results from each method
    """
    vector_results = searcher.search_vector_only(query_embedding, top_k)
    bm25_results = searcher.search_bm25_only(query, top_k)
    hybrid_results = searcher.search(query, query_embedding, top_k)

    return {
        "query": query,
        "vector": [
            {
                "file": r.chunk.file_path,
                "score": r.score,
                "lines": f"{r.chunk.start_line}-{r.chunk.end_line}",
            }
            for r in vector_results
        ],
        "bm25": [
            {"file": r.chunk.file_path, "score": r.score, "terms": r.matched_terms[:5]}
            for r in bm25_results
        ],
        "hybrid": [
            {
                "file": r.chunk.file_path,
                "combined": r.combined_score,
                "vector": r.vector_score,
                "bm25": r.bm25_score,
                "terms": r.matched_terms[:3],
            }
            for r in hybrid_results
        ],
    }
