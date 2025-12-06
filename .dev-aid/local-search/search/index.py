"""FAISS-based code search index"""

import os
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import faiss
from dataclasses import dataclass, asdict

from chunking.chunker import CodeChunk


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
            "embedding_dim": embedding_dim
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
        self.index.add(embeddings.astype('float32'))

        # Store chunks
        self.chunks = chunks

        # Update metadata
        self.metadata["total_chunks"] = len(chunks)
        self.metadata["indexed_files"] = list(set(chunk.file_path for chunk in chunks))

        print(f"Built index with {len(chunks)} chunks from {len(self.metadata['indexed_files'])} files")

    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[SearchResult]:
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
        query = query_embedding.astype('float32').reshape(1, -1)

        # Search
        distances, indices = self.index.search(query, min(top_k, len(self.chunks)))

        # Convert to results
        results = []
        for rank, (idx, distance) in enumerate(zip(indices[0], distances[0])):
            if idx < len(self.chunks):
                # Convert distance to similarity score (lower distance = higher similarity)
                score = 1.0 / (1.0 + distance)
                results.append(SearchResult(
                    chunk=self.chunks[idx],
                    score=score,
                    rank=rank + 1
                ))

        return results

    def save(self):
        """Save index to disk"""
        if self.index is None:
            return

        # Save FAISS index
        index_file = self.index_dir / "index.faiss"
        faiss.write_index(self.index, str(index_file))

        # Save chunks
        chunks_file = self.index_dir / "chunks.pkl"
        with open(chunks_file, 'wb') as f:
            pickle.dump(self.chunks, f)

        # Save metadata
        metadata_file = self.index_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

        print(f"Index saved to {self.index_dir}")

    def load(self):
        """Load index from disk"""
        index_file = self.index_dir / "index.faiss"
        chunks_file = self.index_dir / "chunks.pkl"
        metadata_file = self.index_dir / "metadata.json"

        if not index_file.exists():
            return

        try:
            # Load FAISS index
            self.index = faiss.read_index(str(index_file))

            # Load chunks
            with open(chunks_file, 'rb') as f:
                self.chunks = pickle.load(f)

            # Load metadata
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)

            print(f"Loaded index with {len(self.chunks)} chunks")

        except Exception as e:
            print(f"Error loading index: {e}")
            self.index = None
            self.chunks = []

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            **self.metadata,
            "index_loaded": self.index is not None,
            "storage_path": str(self.index_dir)
        }

    def clear(self):
        """Clear the index"""
        self.index = None
        self.chunks = []
        self.metadata = {
            "total_chunks": 0,
            "indexed_files": [],
            "embedding_dim": self.embedding_dim
        }

        # Delete files
        for file in self.index_dir.glob('*'):
            if file.is_file():
                file.unlink()

        print("Index cleared")
