"""FAISS-based code search index"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import faiss
import numpy as np
from chunking.chunker import CodeChunk

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result with relevance score"""

    chunk: CodeChunk
    score: float
    rank: int


class CodeSearchIndex:
    """FAISS-based search index for code chunks"""

    def __init__(self, index_dir: str, embedding_dim: int = 768):
        """
        Initialize search index

        Args:
            index_dir: Directory to store index
            embedding_dim: Dimensionality of embeddings
        """
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.embedding_dim = embedding_dim
        self.index: Optional[faiss.Index] = None
        self.chunks: List[CodeChunk] = []
        self.metadata: Dict[str, Any] = {
            "total_chunks": 0,
            "indexed_files": [],
            "embedding_dim": embedding_dim,
        }

        # Load existing index if available
        self.load()

    def build(self, chunks: List[CodeChunk], embeddings: np.ndarray):
        """
        Build search index from chunks and embeddings

        Args:
            chunks: List of code chunks
            embeddings: Embedding vectors for chunks (N x embedding_dim)
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match")

        # Create FAISS index (using L2 distance, normalized embeddings give cosine similarity)
        self.index = faiss.IndexFlatL2(self.embedding_dim)

        # Add embeddings to index
        self.index.add(embeddings.astype("float32"))

        # Store chunks
        self.chunks = chunks

        # Update metadata
        self.metadata["total_chunks"] = len(chunks)
        self.metadata["indexed_files"] = list(set(chunk.file_path for chunk in chunks))

        logger.info(
            f"Built index with {len(chunks)} chunks from {len(self.metadata['indexed_files'])} files"
        )

    def search(
        self, query_embedding: np.ndarray, top_k: int = 10
    ) -> List[SearchResult]:
        """
        Search for similar code chunks

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of search results ordered by relevance
        """
        if self.index is None or len(self.chunks) == 0:
            return []

        # Reshape query for FAISS
        query = query_embedding.astype("float32").reshape(1, -1)

        # Search
        distances, indices = self.index.search(query, min(top_k, len(self.chunks)))

        # Convert to results
        results = []
        for rank, (idx, distance) in enumerate(zip(indices[0], distances[0])):
            if idx < len(self.chunks):
                # Convert distance to similarity score (lower distance = higher similarity)
                score = 1.0 / (1.0 + distance)
                results.append(
                    SearchResult(chunk=self.chunks[idx], score=score, rank=rank + 1)
                )

        return results

    def save(self):
        """Save index to disk (using JSON instead of pickle for security)"""
        if self.index is None:
            return

        # Save FAISS index
        index_file = self.index_dir / "index.faiss"
        faiss.write_index(self.index, str(index_file))

        # Save chunks as JSON (SECURITY: avoid pickle RCE vulnerability)
        chunks_file = self.index_dir / "chunks.json"
        chunks_data = [asdict(chunk) for chunk in self.chunks]
        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, indent=2)

        # Save metadata
        metadata_file = self.index_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2)

        logger.info(f"Index saved to {self.index_dir}")

    def load(self):
        """Load index from disk (using JSON instead of pickle for security)"""
        index_file = self.index_dir / "index.faiss"
        chunks_file_json = self.index_dir / "chunks.json"
        chunks_file_pkl = self.index_dir / "chunks.pkl"  # Legacy format
        metadata_file = self.index_dir / "metadata.json"

        if not index_file.exists():
            return

        try:
            # Load FAISS index
            self.index = faiss.read_index(str(index_file))

            # Load chunks (prefer JSON, fallback to pickle for migration)
            if chunks_file_json.exists():
                # Secure JSON format
                with open(chunks_file_json, "r", encoding="utf-8") as f:
                    chunks_data = json.load(f)

                # Validate and reconstruct CodeChunk objects
                self.chunks = []
                for chunk_dict in chunks_data:
                    try:
                        chunk = CodeChunk(**chunk_dict)
                        self.chunks.append(chunk)
                    except (TypeError, KeyError) as e:
                        logger.warning(f"Skipping invalid chunk: {e}")
                        continue

                logger.info(
                    f"Loaded index with {len(self.chunks)} chunks (JSON format)"
                )

            elif chunks_file_pkl.exists():
                # SECURITY: Refuse to load pickle files (CWE-502 deserialization risk)
                logger.error(
                    "Found legacy pickle file %s. "
                    "Pickle deserialization is unsafe. "
                    "Please re-index to generate a JSON chunks file.",
                    chunks_file_pkl,
                )
                self.index = None
                self.chunks = []
                return

            else:
                logger.error("No chunks file found")
                self.index = None
                self.chunks = []
                return

            # Load metadata
            with open(metadata_file, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in index files: {e}")
            self.index = None
            self.chunks = []
        except OSError as e:
            logger.error(f"I/O error loading index: {e}")
            self.index = None
            self.chunks = []
        except Exception as e:
            logger.error(f"Unexpected error loading index: {e}")
            self.index = None
            self.chunks = []

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            **self.metadata,
            "index_loaded": self.index is not None,
            "storage_path": str(self.index_dir),
        }

    def clear(self):
        """Clear the index"""
        self.index = None
        self.chunks = []
        self.metadata = {
            "total_chunks": 0,
            "indexed_files": [],
            "embedding_dim": self.embedding_dim,
        }

        # Delete files
        for file in self.index_dir.glob("*"):
            if file.is_file():
                file.unlink()

        logger.info("Index cleared")
