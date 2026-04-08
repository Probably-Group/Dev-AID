"""Multi-language code chunker with tree-sitter AST chunking and line-based fallback.

For supported languages (python, javascript, typescript, java, go, rust, c, cpp)
this chunker walks the AST and emits one CodeChunk per top-level function, class,
or method. Class chunks include their full body; method chunks are emitted
separately so they can be retrieved independently. For unsupported languages or
files that fail to parse, the chunker falls back to fixed line-window chunking.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from tree_sitter import Language, Parser


@dataclass
class CodeChunk:
    """Represents a chunk of code"""

    content: str
    file_path: str
    start_line: int
    end_line: int
    chunk_type: str  # "function", "class", "method", "block"
    language: str


# Per-language node types that mark a definition we want to emit as its own chunk.
# Each entry is (function_types, class_types, method_types).
# - function_types: top-level callables (functions, free functions)
# - class_types:    type definitions whose body should be one chunk AND walked
#                   for nested methods
# - method_types:   callables defined inside a class body
_FUNCTION_NODES: Dict[str, Set[str]] = {
    "python": {"function_definition"},
    "javascript": {"function_declaration"},
    "typescript": {"function_declaration"},
    "java": set(),
    "go": {"function_declaration", "method_declaration"},
    "rust": {"function_item"},
    "c": {"function_definition"},
    "cpp": {"function_definition"},
}

_CLASS_NODES: Dict[str, Set[str]] = {
    "python": {"class_definition"},
    "javascript": {"class_declaration"},
    "typescript": {"class_declaration", "interface_declaration"},
    "java": {"class_declaration", "interface_declaration", "enum_declaration"},
    "go": {"type_declaration"},
    "rust": {"struct_item", "enum_item", "trait_item", "impl_item"},
    "c": {"struct_specifier"},
    "cpp": {"class_specifier", "struct_specifier"},
}

_METHOD_NODES: Dict[str, Set[str]] = {
    "python": {"function_definition"},
    "javascript": {"method_definition"},
    "typescript": {"method_definition", "method_signature"},
    "java": {"method_declaration", "constructor_declaration"},
    "go": set(),  # methods are top-level method_declaration in Go
    "rust": {"function_item"},  # functions inside impl_item
    "c": set(),
    "cpp": {"function_definition"},
}


def _load_languages() -> Dict[str, Language]:
    """Best-effort load of tree-sitter language grammars.

    Each language is loaded independently inside a try/except so a missing
    or broken grammar package only disables that language, not the chunker.
    """
    languages: Dict[str, Language] = {}

    def _try(name: str, loader: Any) -> None:
        try:
            languages[name] = Language(loader())
        except Exception:
            # Grammar package missing or incompatible — silently skip;
            # files in this language will fall back to line-based chunking.
            pass

    try:
        import tree_sitter_python as ts_python

        _try("python", ts_python.language)
    except ImportError:
        pass

    try:
        import tree_sitter_javascript as ts_javascript

        _try("javascript", ts_javascript.language)
    except ImportError:
        pass

    try:
        import tree_sitter_typescript as ts_typescript

        # The typescript grammar parses .ts and most .tsx files; TSX-specific
        # JSX syntax may yield parse errors, in which case the chunker falls
        # back to line-based chunking transparently.
        _try("typescript", ts_typescript.language_typescript)
    except ImportError:
        pass

    try:
        import tree_sitter_java as ts_java

        _try("java", ts_java.language)
    except ImportError:
        pass

    try:
        import tree_sitter_go as ts_go

        _try("go", ts_go.language)
    except ImportError:
        pass

    try:
        import tree_sitter_rust as ts_rust

        _try("rust", ts_rust.language)
    except ImportError:
        pass

    try:
        import tree_sitter_c as ts_c

        _try("c", ts_c.language)
    except ImportError:
        pass

    try:
        import tree_sitter_cpp as ts_cpp

        _try("cpp", ts_cpp.language)
    except ImportError:
        pass

    return languages


class MultiLanguageChunker:
    """Chunks code files using tree-sitter parsers with line-based fallback."""

    # File extensions mapped to languages
    LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".c": "c",
        ".h": "c",
        ".cpp": "cpp",
        ".hpp": "cpp",
        ".cc": "cpp",
    }

    def __init__(self) -> None:
        """Initialize chunker with tree-sitter parsers for all available languages."""
        languages = _load_languages()
        self.parsers: Dict[str, Parser] = {
            name: Parser(lang) for name, lang in languages.items()
        }

    def chunk_file(self, file_path: str, max_chunk_size: int = 512) -> List[CodeChunk]:
        """
        Chunk a code file.

        Tries tree-sitter AST chunking first. Falls back to fixed line-window
        chunking if no parser is available, the file fails to parse, or no
        definitions were found (e.g. a bare script).

        Args:
            file_path: Path to code file
            max_chunk_size: Maximum lines per chunk (used by line-based chunking
                and to split oversized AST nodes)

        Returns:
            List of code chunks
        """
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower()
        language = self.LANGUAGE_MAP.get(extension, "text")

        # SECURITY: Try UTF-8 first (strict), fall back to latin-1 only on
        # decode errors. FileNotFoundError, PermissionError, etc. propagate.
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read()

        if not content.strip():
            return []

        # Try AST chunking for supported languages.
        parser = self.parsers.get(language)
        if parser is not None:
            try:
                ast_chunks = self._chunk_with_ast(
                    content=content,
                    parser=parser,
                    language=language,
                    file_path=str(file_path),
                    max_chunk_size=max_chunk_size,
                )
                if ast_chunks:
                    return ast_chunks
            except Exception as e:
                # Parse failure → fall back to line-based chunking.
                print(
                    f"AST chunking failed for {file_path}: {e}; using line-based fallback"
                )

        # Line-based fallback.
        return self._chunk_by_lines(
            content=content,
            file_path=str(file_path),
            language=language,
            max_chunk_size=max_chunk_size,
        )

    def _chunk_with_ast(
        self,
        content: str,
        parser: Parser,
        language: str,
        file_path: str,
        max_chunk_size: int,
    ) -> List[CodeChunk]:
        """Walk the tree-sitter AST and emit a chunk per definition."""
        tree = parser.parse(content.encode("utf-8"))
        lines = content.splitlines(keepends=True)

        function_types = _FUNCTION_NODES.get(language, set())
        class_types = _CLASS_NODES.get(language, set())
        method_types = _METHOD_NODES.get(language, set())

        if not (function_types or class_types):
            return []

        # Collect (start_line_0idx, end_line_0idx, chunk_type) for each definition.
        definitions: List[Tuple[int, int, str]] = []

        def visit(node: Any, parent_is_class: bool) -> None:
            node_type = node.type

            if node_type in class_types:
                start = node.start_point[0]
                end = node.end_point[0]
                definitions.append((start, end, "class"))
                # Walk into the class body to surface methods as their own chunks.
                for child in node.children:
                    visit(child, parent_is_class=True)
                return

            is_method = parent_is_class and node_type in method_types
            is_function = (not parent_is_class) and node_type in function_types

            if is_method or is_function:
                start = node.start_point[0]
                end = node.end_point[0]
                definitions.append((start, end, "method" if is_method else "function"))
                # Don't recurse into function bodies — avoids over-chunking on
                # nested closures.
                return

            for child in node.children:
                visit(child, parent_is_class)

        visit(tree.root_node, parent_is_class=False)

        if not definitions:
            return []

        # Build chunks. tree-sitter line numbers are 0-indexed; CodeChunk uses
        # 1-indexed inclusive ranges to match the line-based fallback.
        chunks: List[CodeChunk] = []
        for start_0, end_0, chunk_type in definitions:
            span_lines = end_0 - start_0 + 1
            if span_lines <= max_chunk_size:
                chunk_text = "".join(lines[start_0 : end_0 + 1])
                if chunk_text.strip():
                    chunks.append(
                        CodeChunk(
                            content=chunk_text,
                            file_path=file_path,
                            start_line=start_0 + 1,
                            end_line=end_0 + 1,
                            chunk_type=chunk_type,
                            language=language,
                        )
                    )
            else:
                # Oversized definition — split into max_chunk_size sub-chunks
                # but preserve the chunk_type so callers know they belong to
                # the same logical unit.
                cursor = start_0
                while cursor <= end_0:
                    sub_end = min(cursor + max_chunk_size - 1, end_0)
                    sub_text = "".join(lines[cursor : sub_end + 1])
                    if sub_text.strip():
                        chunks.append(
                            CodeChunk(
                                content=sub_text,
                                file_path=file_path,
                                start_line=cursor + 1,
                                end_line=sub_end + 1,
                                chunk_type=chunk_type,
                                language=language,
                            )
                        )
                    cursor = sub_end + 1

        return chunks

    def _chunk_by_lines(
        self,
        content: str,
        file_path: str,
        language: str,
        max_chunk_size: int,
    ) -> List[CodeChunk]:
        """Fallback: emit fixed-size line-window chunks."""
        lines = content.splitlines(keepends=True)
        total_lines = len(lines)
        chunks: List[CodeChunk] = []

        cursor = 0
        while cursor < total_lines:
            chunk_end = min(cursor + max_chunk_size, total_lines)
            chunk_text = "".join(lines[cursor:chunk_end])
            if chunk_text.strip():
                chunks.append(
                    CodeChunk(
                        content=chunk_text,
                        file_path=file_path,
                        start_line=cursor + 1,
                        end_line=chunk_end,
                        chunk_type="block",
                        language=language,
                    )
                )
            cursor = chunk_end

        return chunks

    def chunk_directory(
        self,
        directory: str,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[CodeChunk]:
        """
        Chunk all code files in a directory.

        Args:
            directory: Root directory to scan
            exclude_patterns: Patterns to exclude (e.g., node_modules, .git)

        Returns:
            List of all code chunks
        """
        if exclude_patterns is None:
            exclude_patterns = [
                ".git",
                "__pycache__",
                "node_modules",
                "venv",
                ".venv",
                "dist",
                "build",
                ".pytest_cache",
                ".mypy_cache",
                "coverage",
                ".coverage",
                ".tox",
                "htmlcov",
            ]

        all_chunks: List[CodeChunk] = []
        directory_path = Path(directory)

        for file_path in directory_path.rglob("*"):
            if file_path.is_dir():
                continue
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue
            if file_path.suffix.lower() in self.LANGUAGE_MAP:
                chunks = self.chunk_file(str(file_path))
                all_chunks.extend(chunks)

        return all_chunks

    @staticmethod
    def is_supported_file(file_path: str) -> bool:
        """Check if file type is supported"""
        return Path(file_path).suffix.lower() in MultiLanguageChunker.LANGUAGE_MAP
