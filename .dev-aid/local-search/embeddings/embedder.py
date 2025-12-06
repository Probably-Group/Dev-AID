"""Code embedding generation using SentenceTransformers"""

import os
import torch
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from pathlib import Path


class CodeEmbedder:
    """Generates embeddings for code chunks"""

    def __init__(self, model_name: str = "google/embeddinggemma-300m", cache_dir: Optional[str] = None):
        """
        Initialize code embedder

        Args:
            model_name: HuggingFace model name
            cache_dir: Directory to cache model (default: ~/.devaid-search/models)
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.devaid-search/models")

        Path(cache_dir).mkdir(parents=True, exist_ok=True)

        # Device selection
        if torch.cuda.is_available():
            self.device = "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            self.device = "mps"  # Apple Silicon
        else:
            self.device = "cpu"

        print(f"Loading embedding model on {self.device}...")
        self.model = SentenceTransformer(
            model_name,
            cache_folder=cache_dir,
            device=self.device
        )
        print("Model loaded successfully")

    def embed(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for text chunks

        Args:
            texts: List of text chunks to embed
            batch_size: Batch size for embedding generation

        Returns:
            Numpy array of embeddings (N x embedding_dim)
        """
        if not texts:
            return np.array([])

        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 100,
            convert_to_numpy=True,
            normalize_embeddings=True  # Normalize for cosine similarity
        )

        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for search query

        Args:
            query: Search query

        Returns:
            Embedding vector
        """
        embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding[0]

    @property
    def embedding_dim(self) -> int:
        """Get embedding dimensionality"""
        return self.model.get_sentence_embedding_dimension()


# Import typing
from typing import Optional
