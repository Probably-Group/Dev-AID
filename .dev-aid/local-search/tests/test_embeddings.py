"""Tests for code embedder"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from embeddings.embedder import CodeEmbedder


class TestCodeEmbedder:
    """Test CodeEmbedder"""

    @pytest.fixture
    def mock_model(self):
        """Mock SentenceTransformer model"""
        model = Mock()
        model.encode = Mock(return_value=np.random.rand(2, 768).astype('float32'))
        model.get_sentence_embedding_dimension = Mock(return_value=768)
        return model

    def test_init_default_cache(self, temp_dir):
        """Test embedder initialization with default cache"""
        with patch('embeddings.embedder.SentenceTransformer') as mock_st:
            with patch('os.path.expanduser', return_value=str(temp_dir / ".devaid-search" / "models")):
                embedder = CodeEmbedder()

                # Verify model was loaded
                mock_st.assert_called_once()

    def test_init_custom_cache(self, temp_dir):
        """Test embedder initialization with custom cache directory"""
        cache_dir = str(temp_dir / "custom_cache")

        with patch('embeddings.embedder.SentenceTransformer') as mock_st:
            embedder = CodeEmbedder(cache_dir=cache_dir)

            # Verify cache directory was used
            call_kwargs = mock_st.call_args[1]
            assert call_kwargs['cache_folder'] == cache_dir

    def test_device_selection_cuda(self):
        """Test CUDA device selection when available"""
        with patch('torch.cuda.is_available', return_value=True):
            with patch('embeddings.embedder.SentenceTransformer') as mock_st:
                embedder = CodeEmbedder()

                # Verify CUDA device was selected
                call_kwargs = mock_st.call_args[1]
                assert call_kwargs['device'] == 'cuda'

    def test_device_selection_mps(self):
        """Test MPS (Apple Silicon) device selection"""
        with patch('torch.cuda.is_available', return_value=False):
            # Mock MPS availability
            mock_mps = MagicMock()
            mock_mps.is_available.return_value = True

            with patch('torch.backends.mps', mock_mps, create=True):
                with patch('embeddings.embedder.SentenceTransformer') as mock_st:
                    embedder = CodeEmbedder()

                    # Verify MPS device was selected
                    call_kwargs = mock_st.call_args[1]
                    assert call_kwargs['device'] == 'mps'

    def test_device_selection_cpu(self):
        """Test CPU fallback when no accelerator available"""
        with patch('torch.cuda.is_available', return_value=False):
            with patch('hasattr', return_value=False):  # No MPS
                with patch('embeddings.embedder.SentenceTransformer') as mock_st:
                    embedder = CodeEmbedder()

                    # Verify CPU device was selected
                    call_kwargs = mock_st.call_args[1]
                    assert call_kwargs['device'] == 'cpu'

    def test_embed_texts(self, mock_model):
        """Test embedding multiple texts"""
        with patch('embeddings.embedder.SentenceTransformer', return_value=mock_model):
            embedder = CodeEmbedder()
            texts = ["def hello(): pass", "class World: pass"]

            embeddings = embedder.embed(texts)

            # Verify encode was called
            mock_model.encode.assert_called_once()

            # Verify return type
            assert isinstance(embeddings, np.ndarray)

    def test_embed_empty_list(self, mock_model):
        """Test embedding empty list"""
        with patch('embeddings.embedder.SentenceTransformer', return_value=mock_model):
            embedder = CodeEmbedder()

            embeddings = embedder.embed([])

            # Should return empty array
            assert isinstance(embeddings, np.ndarray)
            assert len(embeddings) == 0

    def test_embed_with_progress_bar(self, mock_model):
        """Test that progress bar is shown for large batches"""
        with patch('embeddings.embedder.SentenceTransformer', return_value=mock_model):
            embedder = CodeEmbedder()
            texts = ["text"] * 150  # More than 100 texts

            embedder.embed(texts)

            # Verify show_progress_bar was enabled
            call_kwargs = mock_model.encode.call_args[1]
            assert call_kwargs['show_progress_bar'] is True

    def test_embed_without_progress_bar(self, mock_model):
        """Test that progress bar is hidden for small batches"""
        with patch('embeddings.embedder.SentenceTransformer', return_value=mock_model):
            embedder = CodeEmbedder()
            texts = ["text"] * 50  # Less than 100 texts

            embedder.embed(texts)

            # Verify show_progress_bar was disabled
            call_kwargs = mock_model.encode.call_args[1]
            assert call_kwargs['show_progress_bar'] is False

    def test_embed_normalization(self, mock_model):
        """Test that embeddings are normalized"""
        with patch('embeddings.embedder.SentenceTransformer', return_value=mock_model):
            embedder = CodeEmbedder()

            embedder.embed(["test"])

            # Verify normalization was enabled
            call_kwargs = mock_model.encode.call_args[1]
            assert call_kwargs['normalize_embeddings'] is True

    def test_embed_query(self, mock_model):
        """Test embedding a search query"""
        mock_model.encode.return_value = np.random.rand(1, 768).astype('float32')

        with patch('embeddings.embedder.SentenceTransformer', return_value=mock_model):
            embedder = CodeEmbedder()
            query = "find authentication function"

            embedding = embedder.embed_query(query)

            # Verify encode was called with query
            mock_model.encode.assert_called_once()
            call_args = mock_model.encode.call_args[0]
            assert call_args[0] == [query]

            # Verify return type (should be 1D array)
            assert isinstance(embedding, np.ndarray)
            assert len(embedding.shape) == 1

    def test_embedding_dim_property(self, mock_model):
        """Test embedding dimension property"""
        with patch('embeddings.embedder.SentenceTransformer', return_value=mock_model):
            embedder = CodeEmbedder()

            dim = embedder.embedding_dim

            assert dim == 768
            mock_model.get_sentence_embedding_dimension.assert_called_once()

    def test_batch_size_parameter(self, mock_model):
        """Test custom batch size"""
        with patch('embeddings.embedder.SentenceTransformer', return_value=mock_model):
            embedder = CodeEmbedder()

            embedder.embed(["text1", "text2"], batch_size=64)

            # Verify batch size was passed
            call_kwargs = mock_model.encode.call_args[1]
            assert call_kwargs['batch_size'] == 64

    def test_numpy_conversion(self, mock_model):
        """Test that embeddings are converted to numpy"""
        with patch('embeddings.embedder.SentenceTransformer', return_value=mock_model):
            embedder = CodeEmbedder()

            embedder.embed(["test"])

            # Verify numpy conversion was enabled
            call_kwargs = mock_model.encode.call_args[1]
            assert call_kwargs['convert_to_numpy'] is True
