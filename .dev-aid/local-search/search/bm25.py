"""BM25 lexical search implementation for code search"""

import json
import logging
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from chunking.chunker import CodeChunk

logger = logging.getLogger(__name__)

# Pre-compiled regex patterns for tokenization (avoid re-compiling on every call)
_CODE_DELIMITER_RE = re.compile(
    r"[\s\.\,\;\:\(\)\[\]\{\}\<\>\=\+\-\*\/\|\&\!\@\#\$\%\^\~\`\'\"\\\n\r\t]+"
)
_CAMEL_CASE_RE = re.compile(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+")


@dataclass
class BM25Result:
    """BM25 search result"""

    chunk: CodeChunk
    score: float
    rank: int
    matched_terms: List[str]


class CodeTokenizer:
    """Tokenizer optimized for code content"""

    def __init__(
        self,
        camel_case_split: bool = True,
        snake_case_split: bool = True,
        lowercase: bool = False,
    ):
        self.camel_case_split = camel_case_split
        self.snake_case_split = snake_case_split
        self.lowercase = lowercase

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize code text into searchable terms.

        Args:
            text: Code text to tokenize

        Returns:
            List of tokens
        """
        tokens = []

        # Split on whitespace and common code delimiters
        raw_tokens = _CODE_DELIMITER_RE.split(text)

        for token in raw_tokens:
            if not token or len(token) < 2:
                continue

            # Add original token
            tokens.append(token)

            # Split camelCase
            if self.camel_case_split:
                camel_parts = _CAMEL_CASE_RE.findall(token)
                if len(camel_parts) > 1:
                    tokens.extend(camel_parts)

            # Split snake_case (already split by underscore, but handle explicitly)
            if self.snake_case_split and "_" in token:
                snake_parts = [p for p in token.split("_") if p and len(p) >= 2]
                tokens.extend(snake_parts)

        # Lowercase if configured
        if self.lowercase:
            tokens = [t.lower() for t in tokens]

        # Filter out very short tokens and duplicates while preserving order
        seen = set()
        filtered = []
        for t in tokens:
            t_normalized = t.lower()
            if len(t) >= 2 and t_normalized not in seen:
                filtered.append(t)
                seen.add(t_normalized)

        return filtered


class BM25Index:
    """
    BM25 (Okapi BM25) search index for code chunks.

    BM25 is a lexical/keyword-based ranking function that scores documents
    based on term frequency, inverse document frequency, and document length.
    """

    def __init__(
        self,
        index_dir: str,
        k1: float = 1.2,
        b: float = 0.75,
        tokenizer: Optional[CodeTokenizer] = None,
    ):
        """
        Initialize BM25 index.

        Args:
            index_dir: Directory to store index
            k1: Term frequency saturation parameter (default 1.2)
            b: Document length normalization parameter (default 0.75)
            tokenizer: Custom tokenizer (defaults to CodeTokenizer)
        """
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.k1 = k1
        self.b = b
        self.tokenizer = tokenizer or CodeTokenizer()

        # Index data structures
        self.chunks: List[CodeChunk] = []
        self.doc_term_freqs: List[Counter] = []  # Term frequencies per document
        self.doc_lengths: List[int] = []  # Document lengths in tokens
        self.avg_doc_length: float = 0.0
        self.df: Counter = Counter()  # Document frequency per term
        self.total_docs: int = 0

        # Load existing index
        self.load()

    def build(self, chunks: List[CodeChunk]):
        """
        Build BM25 index from code chunks.

        Args:
            chunks: List of code chunks to index
        """
        self.chunks = chunks
        self.doc_term_freqs = []
        self.doc_lengths = []
        self.df = Counter()
        self.total_docs = len(chunks)

        if self.total_docs == 0:
            logger.warning("No chunks to index")
            return

        total_length = 0

        for chunk in chunks:
            # Tokenize chunk content
            content = f"{chunk.file_path} {chunk.content}"
            tokens = self.tokenizer.tokenize(content)

            # Calculate term frequencies for this document
            tf = Counter(t.lower() for t in tokens)
            self.doc_term_freqs.append(tf)

            # Track document length
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_length += doc_len

            # Update document frequencies
            unique_terms = set(t.lower() for t in tokens)
            for term in unique_terms:
                self.df[term] += 1

        # Calculate average document length
        self.avg_doc_length = (
            total_length / self.total_docs if self.total_docs > 0 else 0
        )

        logger.info(
            f"Built BM25 index: {self.total_docs} docs, "
            f"{len(self.df)} unique terms, "
            f"avg doc length: {self.avg_doc_length:.1f}"
        )

    def _idf(self, term: str) -> float:
        """
        Calculate IDF (Inverse Document Frequency) for a term.

        Uses the standard BM25 IDF formula with smoothing.
        """
        df = self.df.get(term.lower(), 0)
        if df == 0:
            return 0.0

        # BM25 IDF formula
        return math.log((self.total_docs - df + 0.5) / (df + 0.5) + 1.0)

    def _score_document(
        self, doc_idx: int, query_terms: List[str]
    ) -> tuple[float, List[str]]:
        """
        Calculate BM25 score for a document given query terms.

        Returns:
            Tuple of (score, matched_terms)
        """
        if doc_idx >= len(self.doc_term_freqs):
            return 0.0, []

        tf = self.doc_term_freqs[doc_idx]
        doc_len = self.doc_lengths[doc_idx]

        score = 0.0
        matched_terms = []

        for term in query_terms:
            term_lower = term.lower()
            term_tf = tf.get(term_lower, 0)

            if term_tf == 0:
                continue

            matched_terms.append(term)

            # BM25 scoring formula
            idf = self._idf(term_lower)
            numerator = term_tf * (self.k1 + 1)
            denominator = term_tf + self.k1 * (
                1 - self.b + self.b * (doc_len / self.avg_doc_length)
            )

            score += idf * (numerator / denominator)

        return score, matched_terms

    def search(self, query: str, top_k: int = 10) -> List[BM25Result]:
        """
        Search for code chunks matching the query.

        Args:
            query: Search query string
            top_k: Number of results to return

        Returns:
            List of BM25 results ordered by score
        """
        if self.total_docs == 0:
            return []

        # Tokenize query
        query_terms = self.tokenizer.tokenize(query)
        if not query_terms:
            return []

        # Score all documents
        scores = []
        for doc_idx in range(self.total_docs):
            score, matched = self._score_document(doc_idx, query_terms)
            if score > 0:
                scores.append((doc_idx, score, matched))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        # Build results
        results = []
        for rank, (doc_idx, score, matched) in enumerate(scores[:top_k]):
            results.append(
                BM25Result(
                    chunk=self.chunks[doc_idx],
                    score=score,
                    rank=rank + 1,
                    matched_terms=matched,
                )
            )

        return results

    def save(self):
        """Save BM25 index to disk."""
        if self.total_docs == 0:
            return

        # Save chunks
        chunks_file = self.index_dir / "bm25_chunks.json"
        chunks_data = []
        for chunk in self.chunks:
            chunks_data.append(
                {
                    "file_path": chunk.file_path,
                    "content": chunk.content,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "chunk_type": chunk.chunk_type,
                    "language": chunk.language,
                }
            )

        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, indent=2)

        # Save index data
        index_file = self.index_dir / "bm25_index.json"
        index_data = {
            "k1": self.k1,
            "b": self.b,
            "total_docs": self.total_docs,
            "avg_doc_length": self.avg_doc_length,
            "df": dict(self.df),
            "doc_lengths": self.doc_lengths,
            "doc_term_freqs": [dict(tf) for tf in self.doc_term_freqs],
        }

        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)

        logger.info(f"BM25 index saved to {self.index_dir}")

    def load(self):
        """Load BM25 index from disk."""
        chunks_file = self.index_dir / "bm25_chunks.json"
        index_file = self.index_dir / "bm25_index.json"

        if not chunks_file.exists() or not index_file.exists():
            return

        try:
            # Load chunks
            with open(chunks_file, "r", encoding="utf-8") as f:
                chunks_data = json.load(f)

            self.chunks = []
            for cd in chunks_data:
                self.chunks.append(
                    CodeChunk(
                        file_path=cd["file_path"],
                        content=cd["content"],
                        start_line=cd["start_line"],
                        end_line=cd["end_line"],
                        chunk_type=cd.get("chunk_type", "code"),
                        language=cd.get("language", ""),
                    )
                )

            # Load index data
            with open(index_file, "r", encoding="utf-8") as f:
                index_data = json.load(f)

            self.k1 = index_data.get("k1", 1.2)
            self.b = index_data.get("b", 0.75)
            self.total_docs = index_data.get("total_docs", 0)
            self.avg_doc_length = index_data.get("avg_doc_length", 0.0)
            self.df = Counter(index_data.get("df", {}))
            self.doc_lengths = index_data.get("doc_lengths", [])
            self.doc_term_freqs = [
                Counter(tf) for tf in index_data.get("doc_term_freqs", [])
            ]

            logger.info(f"Loaded BM25 index: {self.total_docs} docs")

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Error loading BM25 index: {e}")
            self.chunks = []
            self.total_docs = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get BM25 index statistics."""
        return {
            "total_docs": self.total_docs,
            "unique_terms": len(self.df),
            "avg_doc_length": self.avg_doc_length,
            "k1": self.k1,
            "b": self.b,
            "storage_path": str(self.index_dir),
        }

    def clear(self):
        """Clear the BM25 index."""
        self.chunks = []
        self.doc_term_freqs = []
        self.doc_lengths = []
        self.avg_doc_length = 0.0
        self.df = Counter()
        self.total_docs = 0

        # Delete files
        for pattern in ["bm25_*.json"]:
            for file in self.index_dir.glob(pattern):
                file.unlink()

        logger.info("BM25 index cleared")
