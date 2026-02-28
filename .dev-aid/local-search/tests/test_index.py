"""Tests for FAISS search index"""

import json
import pickle
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch

from search.index import CodeSearchIndex, SearchResult
from chunking.chunker import CodeChunk


class TestSearchResult:
    """Test SearchResult dataclass"""

    def test_create_search_result(self):
        """Test creating a search result"""
        chunk = CodeChunk(
            content="def test(): pass",
            file_path="/path/file.py",
            start_line=1,
            end_line=1,
            chunk_type="function",
            language="python"
        )
        result = SearchResult(chunk=chunk, score=0.95, rank=1)

        assert result.chunk == chunk
        assert result.score == 0.95
        assert result.rank == 1


class TestCodeSearchIndex:
    """Test CodeSearchIndex"""

    @pytest.fixture
    def index_dir(self, temp_dir):
        """Create temporary index directory"""
        return str(temp_dir / "index")

    @pytest.fixture
    def sample_chunks(self):
        """Create sample code chunks"""
        return [
            CodeChunk(
                content="def add(a, b): return a + b",
                file_path="/test/math.py",
                start_line=1,
                end_line=1,
                chunk_type="function",
                language="python"
            ),
            CodeChunk(
                content="def subtract(a, b): return a - b",
                file_path="/test/math.py",
                start_line=3,
                end_line=3,
                chunk_type="function",
                language="python"
            ),
            CodeChunk(
                content="class Calculator: pass",
                file_path="/test/calc.py",
                start_line=1,
                end_line=1,
                chunk_type="class",
                language="python"
            ),
        ]

    @pytest.fixture
    def sample_embeddings(self):
        """Create sample embeddings"""
        # Create 3 embeddings of dimension 768
        np.random.seed(42)
        return np.random.rand(3, 768).astype('float32')

    def test_init(self, index_dir):
        """Test index initialization"""
        index = CodeSearchIndex(index_dir, embedding_dim=768)

        assert index.index_dir == Path(index_dir)
        assert index.embedding_dim == 768
        assert index.index is None
        assert index.chunks == []
        assert index.metadata["total_chunks"] == 0

    def test_init_creates_directory(self, temp_dir):
        """Test that index directory is created"""
        index_dir = temp_dir / "new_index"
        assert not index_dir.exists()

        index = CodeSearchIndex(str(index_dir))

        assert index_dir.exists()
        assert index_dir.is_dir()

    def test_build_index(self, index_dir, sample_chunks, sample_embeddings):
        """Test building search index"""
        index = CodeSearchIndex(index_dir)
        index.build(sample_chunks, sample_embeddings)

        assert index.index is not None
        assert len(index.chunks) == 3
        assert index.metadata["total_chunks"] == 3
        assert len(index.metadata["indexed_files"]) == 2  # math.py and calc.py

    def test_build_index_mismatch_error(self, index_dir, sample_chunks):
        """Test error when chunks and embeddings don't match"""
        index = CodeSearchIndex(index_dir)
        wrong_embeddings = np.random.rand(2, 768).astype('float32')  # Only 2 embeddings

        with pytest.raises(ValueError, match="must match"):
            index.build(sample_chunks, wrong_embeddings)

    def test_search_empty_index(self, index_dir):
        """Test searching an empty index"""
        index = CodeSearchIndex(index_dir)
        query_embedding = np.random.rand(768).astype('float32')

        results = index.search(query_embedding, top_k=5)

        assert results == []

    def test_search(self, index_dir, sample_chunks, sample_embeddings):
        """Test searching the index"""
        index = CodeSearchIndex(index_dir)
        index.build(sample_chunks, sample_embeddings)

        # Use first embedding as query (should match first chunk best)
        query = sample_embeddings[0]
        results = index.search(query, top_k=2)

        assert len(results) <= 2
        assert all(isinstance(r, SearchResult) for r in results)
        assert all(r.rank >= 1 for r in results)
        assert all(0.0 <= r.score <= 1.0 for r in results)

        # Results should be ordered by rank
        for i in range(len(results) - 1):
            assert results[i].rank < results[i + 1].rank

    def test_search_top_k_larger_than_index(self, index_dir, sample_chunks, sample_embeddings):
        """Test search when top_k is larger than index size"""
        index = CodeSearchIndex(index_dir)
        index.build(sample_chunks, sample_embeddings)

        query = sample_embeddings[0]
        results = index.search(query, top_k=100)

        # Should return all chunks, not more
        assert len(results) == 3

    def test_save_index(self, index_dir, sample_chunks, sample_embeddings):
        """Test saving index to disk"""
        index = CodeSearchIndex(index_dir)
        index.build(sample_chunks, sample_embeddings)
        index.save()

        # Verify files exist
        index_path = Path(index_dir)
        assert (index_path / "index.faiss").exists()
        assert (index_path / "chunks.json").exists()
        assert (index_path / "metadata.json").exists()

    def test_save_empty_index(self, index_dir):
        """Test saving empty index does nothing"""
        index = CodeSearchIndex(index_dir)
        index.save()

        # No files should be created
        index_path = Path(index_dir)
        assert not (index_path / "index.faiss").exists()

    def test_load_index(self, index_dir, sample_chunks, sample_embeddings):
        """Test loading index from disk"""
        # Build and save
        index1 = CodeSearchIndex(index_dir)
        index1.build(sample_chunks, sample_embeddings)
        index1.save()

        # Load in new instance
        index2 = CodeSearchIndex(index_dir)

        assert index2.index is not None
        assert len(index2.chunks) == 3
        assert index2.metadata["total_chunks"] == 3

    def test_load_nonexistent_index(self, index_dir):
        """Test loading when no index exists"""
        index = CodeSearchIndex(index_dir)

        # Should not raise error, just have empty index
        assert index.index is None
        assert index.chunks == []

    def test_pickle_migration(self, index_dir, sample_chunks, sample_embeddings):
        """Test that legacy pickle format is refused for security (CWE-502)"""
        # Build index
        index = CodeSearchIndex(index_dir)
        index.build(sample_chunks, sample_embeddings)

        # Save FAISS index
        index_path = Path(index_dir)
        import faiss
        faiss.write_index(index.index, str(index_path / "index.faiss"))

        # Save chunks as pickle (legacy format) -- no JSON file
        chunks_pkl_file = index_path / "chunks.pkl"
        with open(chunks_pkl_file, 'wb') as f:
            pickle.dump(sample_chunks, f)

        # Save metadata
        with open(index_path / "metadata.json", 'w') as f:
            json.dump(index.metadata, f)

        # Remove any JSON chunks file so only pickle is available
        chunks_json_file = index_path / "chunks.json"
        if chunks_json_file.exists():
            chunks_json_file.unlink()

        # Verify pickle file exists
        assert chunks_pkl_file.exists()

        # Load index -- should refuse pickle deserialization
        index2 = CodeSearchIndex(index_dir)

        # Verify security hardening: pickle is NOT loaded
        assert len(index2.chunks) == 0
        assert index2.index is None
        # Pickle file should still exist (not deleted, just refused)
        assert chunks_pkl_file.exists()

    def test_json_format_security(self, index_dir, sample_chunks, sample_embeddings):
        """Test that JSON format is used (not pickle) for security"""
        index = CodeSearchIndex(index_dir)
        index.build(sample_chunks, sample_embeddings)
        index.save()

        index_path = Path(index_dir)

        # Verify JSON file exists and pickle doesn't
        assert (index_path / "chunks.json").exists()
        assert not (index_path / "chunks.pkl").exists()

        # Verify JSON is valid
        with open(index_path / "chunks.json", 'r') as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) == 3

    def test_get_stats(self, index_dir, sample_chunks, sample_embeddings):
        """Test getting index statistics"""
        index = CodeSearchIndex(index_dir)
        index.build(sample_chunks, sample_embeddings)

        stats = index.get_stats()

        assert stats["total_chunks"] == 3
        assert stats["index_loaded"] is True
        assert stats["storage_path"] == str(index.index_dir)
        assert len(stats["indexed_files"]) == 2

    def test_clear_index(self, index_dir, sample_chunks, sample_embeddings):
        """Test clearing the index"""
        index = CodeSearchIndex(index_dir)
        index.build(sample_chunks, sample_embeddings)
        index.save()

        # Clear index
        index.clear()

        # Verify index is cleared
        assert index.index is None
        assert index.chunks == []
        assert index.metadata["total_chunks"] == 0

        # Verify files are deleted
        index_path = Path(index_dir)
        assert not (index_path / "index.faiss").exists()
        assert not (index_path / "chunks.json").exists()

    def test_load_corrupted_json(self, index_dir):
        """Test handling of corrupted JSON file"""
        index_path = Path(index_dir)
        index_path.mkdir(parents=True, exist_ok=True)

        # Create corrupted JSON file
        (index_path / "chunks.json").write_text("{ invalid json")
        (index_path / "index.faiss").touch()

        # Should handle gracefully
        index = CodeSearchIndex(index_dir)

        assert index.index is None
        assert index.chunks == []

    def test_search_score_calculation(self, index_dir, sample_chunks, sample_embeddings):
        """Test that search scores are calculated correctly"""
        index = CodeSearchIndex(index_dir)
        index.build(sample_chunks, sample_embeddings)

        query = sample_embeddings[0]
        results = index.search(query, top_k=3)

        # All scores should be between 0 and 1
        for result in results:
            assert 0.0 <= result.score <= 1.0

        # Higher ranked results should have higher or equal scores
        for i in range(len(results) - 1):
            assert results[i].score >= results[i + 1].score
