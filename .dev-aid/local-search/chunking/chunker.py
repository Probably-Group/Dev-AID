"""Multi-language code chunker using tree-sitter"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import tree_sitter
from dataclasses import dataclass


@dataclass
class CodeChunk:
    """Represents a chunk of code"""
    content: str
    file_path: str
    start_line: int
    end_line: int
    chunk_type: str  # "function", "class", "method", "block"
    language: str


class MultiLanguageChunker:
    """Chunks code files using tree-sitter parsers"""

    # File extensions mapped to languages
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.c': 'c',
        '.h': 'c',
        '.cpp': 'cpp',
        '.hpp': 'cpp',
        '.cc': 'cpp',
    }

    def __init__(self):
        """Initialize chunker with tree-sitter parsers"""
        self.parsers = {}
        self._init_parsers()

    def _init_parsers(self):
        """Initialize tree-sitter parsers for supported languages"""
        # Note: tree-sitter parsers require language-specific setup
        # For now, we'll use a simple line-based approach as fallback
        # Full tree-sitter integration can be added later
        pass

    def chunk_file(self, file_path: str, max_chunk_size: int = 512) -> List[CodeChunk]:
        """
        Chunk a code file

        Args:
            file_path: Path to code file
            max_chunk_size: Maximum lines per chunk

        Returns:
            List of code chunks
        """
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower()
        language = self.LANGUAGE_MAP.get(extension, 'text')

        chunks: List[CodeChunk] = []

        try:
            # SECURITY: Try UTF-8 first (strict), fallback to detection if needed
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # Fallback to latin-1 which never fails (but may produce garbage)
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                return chunks

        try:
            # Simple line-based chunking (can be enhanced with tree-sitter later)
            total_lines = len(lines)
            current_line = 0

            while current_line < total_lines:
                chunk_end = min(current_line + max_chunk_size, total_lines)
                chunk_content = ''.join(lines[current_line:chunk_end])

                if chunk_content.strip():  # Only add non-empty chunks
                    chunks.append(CodeChunk(
                        content=chunk_content,
                        file_path=str(file_path),
                        start_line=current_line + 1,
                        end_line=chunk_end,
                        chunk_type="block",
                        language=language
                    ))

                current_line = chunk_end

        except Exception as e:
            print(f"Error chunking {file_path}: {e}")

        return chunks

    def chunk_directory(self, directory: str, exclude_patterns: Optional[List[str]] = None) -> List[CodeChunk]:
        """
        Chunk all code files in a directory

        Args:
            directory: Root directory to scan
            exclude_patterns: Patterns to exclude (e.g., node_modules, .git)

        Returns:
            List of all code chunks
        """
        if exclude_patterns is None:
            exclude_patterns = [
                '.git', '__pycache__', 'node_modules', 'venv', '.venv',
                'dist', 'build', '.pytest_cache', '.mypy_cache',
                'coverage', '.coverage', '.tox', 'htmlcov'
            ]

        all_chunks = []
        directory_path = Path(directory)

        for file_path in directory_path.rglob('*'):
            # Skip directories and excluded patterns
            if file_path.is_dir():
                continue

            # Check exclusions
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue

            # Only process supported file types
            if file_path.suffix.lower() in self.LANGUAGE_MAP:
                chunks = self.chunk_file(str(file_path))
                all_chunks.extend(chunks)

        return all_chunks

    @staticmethod
    def is_supported_file(file_path: str) -> bool:
        """Check if file type is supported"""
        return Path(file_path).suffix.lower() in MultiLanguageChunker.LANGUAGE_MAP
