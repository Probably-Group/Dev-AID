"""Tests for code chunker"""

import pytest
from pathlib import Path
from chunking.chunker import MultiLanguageChunker, CodeChunk


class TestCodeChunk:
    """Test CodeChunk dataclass"""

    def test_create_chunk(self):
        """Test creating a code chunk"""
        chunk = CodeChunk(
            content="def test(): pass",
            file_path="/path/to/file.py",
            start_line=1,
            end_line=1,
            chunk_type="function",
            language="python"
        )
        assert chunk.content == "def test(): pass"
        assert chunk.file_path == "/path/to/file.py"
        assert chunk.start_line == 1
        assert chunk.end_line == 1
        assert chunk.chunk_type == "function"
        assert chunk.language == "python"


class TestMultiLanguageChunker:
    """Test MultiLanguageChunker"""

    @pytest.fixture
    def chunker(self):
        """Create chunker instance"""
        return MultiLanguageChunker()

    def test_init(self, chunker):
        """Test chunker initialization"""
        assert chunker.parsers == {}
        assert chunker.LANGUAGE_MAP is not None

    def test_language_detection_python(self, chunker):
        """Test language detection for Python files"""
        assert chunker.LANGUAGE_MAP['.py'] == 'python'

    def test_language_detection_javascript(self, chunker):
        """Test language detection for JavaScript files"""
        assert chunker.LANGUAGE_MAP['.js'] == 'javascript'
        assert chunker.LANGUAGE_MAP['.jsx'] == 'javascript'

    def test_language_detection_typescript(self, chunker):
        """Test language detection for TypeScript files"""
        assert chunker.LANGUAGE_MAP['.ts'] == 'typescript'
        assert chunker.LANGUAGE_MAP['.tsx'] == 'typescript'

    def test_is_supported_file(self):
        """Test file support detection"""
        assert MultiLanguageChunker.is_supported_file("test.py") is True
        assert MultiLanguageChunker.is_supported_file("test.js") is True
        assert MultiLanguageChunker.is_supported_file("test.txt") is False
        assert MultiLanguageChunker.is_supported_file("README.md") is False

    def test_chunk_python_file(self, chunker, sample_python_file):
        """Test chunking a Python file"""
        chunks = chunker.chunk_file(sample_python_file)

        assert len(chunks) > 0
        assert all(isinstance(chunk, CodeChunk) for chunk in chunks)
        assert all(chunk.language == "python" for chunk in chunks)
        assert all(chunk.file_path == sample_python_file for chunk in chunks)

    def test_chunk_javascript_file(self, chunker, sample_javascript_file):
        """Test chunking a JavaScript file"""
        chunks = chunker.chunk_file(sample_javascript_file)

        assert len(chunks) > 0
        assert all(isinstance(chunk, CodeChunk) for chunk in chunks)
        assert all(chunk.language == "javascript" for chunk in chunks)

    def test_chunk_file_with_size_limit(self, chunker, sample_python_file):
        """Test chunking with custom max_chunk_size"""
        chunks = chunker.chunk_file(sample_python_file, max_chunk_size=5)

        # Should create multiple chunks due to small chunk size
        assert len(chunks) >= 2

        # Verify chunk sizes
        for chunk in chunks:
            # Each chunk should have at most 5 lines
            assert chunk.end_line - chunk.start_line <= 5

    def test_chunk_empty_file(self, chunker, temp_dir):
        """Test chunking an empty file"""
        empty_file = temp_dir / "empty.py"
        empty_file.write_text("")

        chunks = chunker.chunk_file(str(empty_file))

        # Empty file should produce no chunks
        assert len(chunks) == 0

    def test_chunk_file_line_numbers(self, chunker, sample_python_file):
        """Test that line numbers are correct"""
        chunks = chunker.chunk_file(sample_python_file)

        # First chunk should start at line 1
        assert chunks[0].start_line == 1

        # Check consecutive chunks don't overlap
        for i in range(len(chunks) - 1):
            assert chunks[i].end_line <= chunks[i + 1].start_line

    def test_chunk_directory(self, chunker, sample_codebase):
        """Test chunking an entire directory"""
        chunks = chunker.chunk_directory(sample_codebase)

        assert len(chunks) > 0

        # Should have chunks from multiple files
        file_paths = set(chunk.file_path for chunk in chunks)
        assert len(file_paths) >= 3  # At least main.py, utils.py, helper.py, app.js

    def test_chunk_directory_excludes_patterns(self, chunker, sample_codebase):
        """Test that excluded patterns are not chunked"""
        chunks = chunker.chunk_directory(sample_codebase)

        # Verify node_modules is excluded
        for chunk in chunks:
            assert "node_modules" not in chunk.file_path

    def test_chunk_directory_custom_exclusions(self, chunker, sample_codebase):
        """Test chunking with custom exclusion patterns"""
        chunks = chunker.chunk_directory(
            sample_codebase,
            exclude_patterns=['module']
        )

        # Verify 'module' directory is excluded
        for chunk in chunks:
            assert "module" not in chunk.file_path

    def test_chunk_nonexistent_file(self, chunker):
        """Test chunking a file that doesn't exist"""
        chunks = chunker.chunk_file("/nonexistent/file.py")

        # Should return empty list, not raise exception
        assert chunks == []

    def test_chunk_content_not_empty(self, chunker, sample_python_file):
        """Test that chunks have non-empty content"""
        chunks = chunker.chunk_file(sample_python_file)

        for chunk in chunks:
            assert chunk.content.strip() != ""
            assert len(chunk.content) > 0
