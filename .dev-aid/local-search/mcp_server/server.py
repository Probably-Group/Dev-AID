"""Dev-AID Local Search MCP Server

Provides code search capabilities via MCP (Model Context Protocol)
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

# Add parent directory to path for imports (only when run as script)
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from chunking.chunker import MultiLanguageChunker
from embeddings.embedder import CodeEmbedder
from mcp_server.validation import (
    ClearIndexRequest,
    GetIndexStatusRequest,
    IndexDirectoryRequest,
    SearchCodeRequest,
)
from search.index import CodeSearchIndex, SearchResult
from utils.security import validate_directory_path
from utils.storage import StorageManager

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error with safe messaging"""

    def __init__(self, message: str, internal: Optional[str] = None):
        self.message = message
        if internal:
            logger.error(f"{message}: {internal}")
        super().__init__(message)

    def to_response(self) -> Dict[str, str]:
        """Convert to safe error response"""
        return {"error": self.message}


class CodeSearchServer:
    """MCP Server for code search"""

    def __init__(self):
        """Initialize code search server"""
        self.storage = StorageManager()
        self.embedder: Optional[CodeEmbedder] = None
        self.chunker = MultiLanguageChunker()
        self.current_project: Optional[str] = None
        self.index: Optional[CodeSearchIndex] = None

    def _ensure_embedder(self):
        """Lazy-load embedder (downloads model on first use)"""
        if self.embedder is None:
            logger.info("Loading embedding model...")
            self.embedder = CodeEmbedder(cache_dir=str(self.storage.models_dir))

    def _ensure_index(self, project_path: str):
        """Ensure index is loaded for project"""
        if self.current_project != project_path or self.index is None:
            self.current_project = project_path
            project_dir = self.storage.get_project_dir(project_path)

            self._ensure_embedder()
            if self.embedder is None:
                raise AppError("Embedder not initialized")
            self.index = CodeSearchIndex(
                index_dir=str(project_dir), embedding_dim=self.embedder.embedding_dim
            )

    def search_code(
        self, query: str, project_path: str, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search code with natural language query

        Args:
            query: Natural language search query
            project_path: Path to project being searched
            top_k: Number of results to return

        Returns:
            List of search results with code chunks

        Raises:
            AppError: If search fails
        """
        try:
            # Ensure index is loaded
            self._ensure_index(project_path)

            if self.index is None or len(self.index.chunks) == 0:
                # No index exists, try to build it
                logger.info(f"No index found for {project_path}, building...")
                self.index_directory(project_path)

            # Generate query embedding
            if self.embedder is None:
                raise AppError("Embedder not initialized")
            query_embedding = self.embedder.embed_query(query)

            # Search
            if self.index is None:
                raise AppError("Index not initialized")
            results = self.index.search(query_embedding, top_k=top_k)

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append(
                    {
                        "content": result.chunk.content,
                        "file_path": result.chunk.file_path,
                        "start_line": result.chunk.start_line,
                        "end_line": result.chunk.end_line,
                        "language": result.chunk.language,
                        "score": round(result.score, 4),
                        "rank": result.rank,
                    }
                )

            logger.info(
                f"Search completed: {len(formatted_results)} results for '{query[:50]}...'"
            )
            return formatted_results

        except Exception as e:
            raise AppError("Search failed", str(e))

    def index_directory(self, directory: str) -> Dict[str, Any]:
        """
        Index a directory for code search

        Args:
            directory: Path to directory

        Returns:
            Index statistics

        Raises:
            AppError: If indexing fails
        """
        try:
            # SECURITY: Validate directory path
            validated_dir = validate_directory_path(directory, must_exist=True)
            directory = str(validated_dir)

            logger.info(f"Indexing directory: {directory}")

            # Ensure embedder is loaded
            self._ensure_embedder()

            # Chunk all code files
            logger.info("Chunking code files...")
            chunks = self.chunker.chunk_directory(directory)

            if not chunks:
                raise AppError("No supported code files found")

            logger.info(f"Found {len(chunks)} code chunks")

            # Generate embeddings
            logger.info("Generating embeddings...")
            chunk_texts = [chunk.content for chunk in chunks]
            if self.embedder is None:
                raise AppError("Embedder not initialized")
            embeddings = self.embedder.embed(chunk_texts)

            # Build index
            logger.info("Building search index...")
            self._ensure_index(directory)
            if self.index is None:
                raise AppError("Index not initialized")
            self.index.build(chunks, embeddings)

            # Save index
            self.index.save()

            return self.index.get_stats()

        except AppError:
            raise
        except Exception as e:
            raise AppError("Indexing failed", str(e))

    def get_index_status(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get index status

        Args:
            project_path: Path to project (optional)

        Returns:
            Index statistics

        Raises:
            AppError: If status check fails
        """
        try:
            if project_path:
                self._ensure_index(project_path)
                if self.index:
                    return self.index.get_stats()

            # List all projects
            projects = self.storage.list_projects()
            return {
                "indexed_projects": len(projects),
                "projects": projects,
                "current_project": self.current_project,
            }

        except Exception as e:
            raise AppError("Failed to get index status", str(e))

    def list_projects(self) -> Dict[str, Any]:
        """
        List all indexed projects

        Returns:
            Dictionary with project list

        Raises:
            AppError: If listing fails
        """
        try:
            projects = self.storage.list_projects()
            return {
                "total_projects": len(projects),
                "projects": [
                    {"path": path, "hash": hash_val}
                    for path, hash_val in projects.items()
                ],
            }
        except Exception as e:
            raise AppError("Failed to list projects", str(e))

    def clear_index(self, project_path: str) -> Dict[str, str]:
        """
        Clear index for a project

        Args:
            project_path: Path to project

        Returns:
            Status message

        Raises:
            AppError: If clearing fails
        """
        try:
            self._ensure_index(project_path)
            if self.index:
                self.index.clear()
            logger.info(f"Cleared index for {project_path}")
            return {"status": "Index cleared successfully"}
        except Exception as e:
            raise AppError("Failed to clear index", str(e))


class MCPRequestHandler:
    """Handler for MCP requests with validation"""

    def __init__(self, server: CodeSearchServer):
        self.server = server

    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "devaid-code-search", "version": "1.0.0"},
        }

    def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {
            "tools": [
                {
                    "name": "search_code",
                    "description": "Search codebase using natural language query",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language search query",
                            },
                            "project_path": {
                                "type": "string",
                                "description": "Path to project",
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results (default: 10)",
                            },
                        },
                        "required": ["query", "project_path"],
                    },
                },
                {
                    "name": "index_directory",
                    "description": "Index a directory for code search",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory path to index",
                            }
                        },
                        "required": ["directory"],
                    },
                },
                {
                    "name": "get_index_status",
                    "description": "Get status of code search index",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Optional project path",
                            }
                        },
                    },
                },
                {
                    "name": "list_projects",
                    "description": "List all indexed projects",
                    "inputSchema": {"type": "object", "properties": {}},
                },
                {
                    "name": "clear_index",
                    "description": "Clear index for a project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Project path",
                            }
                        },
                        "required": ["project_path"],
                    },
                },
            ]
        }

    def handle_tools_call(self, params: Dict[str, Any]) -> Any:
        """Handle tools/call request with Pydantic validation"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "search_code":
                # SECURITY: Validate with Pydantic
                search_req = SearchCodeRequest(**arguments)
                return self.server.search_code(
                    query=search_req.query,
                    project_path=search_req.project_path,
                    top_k=search_req.top_k,
                )
            elif tool_name == "index_directory":
                index_req = IndexDirectoryRequest(**arguments)
                return self.server.index_directory(directory=index_req.directory)
            elif tool_name == "get_index_status":
                status_req = GetIndexStatusRequest(**arguments)
                return self.server.get_index_status(
                    project_path=status_req.project_path
                )
            elif tool_name == "list_projects":
                return self.server.list_projects()
            elif tool_name == "clear_index":
                clear_req = ClearIndexRequest(**arguments)
                return self.server.clear_index(project_path=clear_req.project_path)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        except ValidationError as e:
            # Pydantic validation error
            error_msg = f"Invalid request: {e.errors()[0]['msg']}"
            raise AppError(error_msg, str(e))
        except AppError:
            raise
        except Exception as e:
            raise AppError(f"Tool execution failed", str(e))


def handle_mcp_request(
    server: CodeSearchServer, request: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle MCP JSON-RPC request

    Args:
        server: CodeSearchServer instance
        request: JSON-RPC request

    Returns:
        JSON-RPC response
    """
    method = request.get("method", "")
    params = request.get("params", {})
    request_id = request.get("id")

    handler = MCPRequestHandler(server)

    try:
        # Route to appropriate handler
        if method == "initialize":
            result = handler.handle_initialize(params)
        elif method == "tools/list":
            result = handler.handle_tools_list(params)
        elif method == "tools/call":
            result = handler.handle_tools_call(params)
        else:
            raise ValueError(f"Unknown method: {method}")

        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    except AppError as e:
        # Application error with safe message
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": e.message},  # Safe message only
        }
    except Exception as e:
        # Unexpected error
        logger.exception(f"Unexpected error handling {method}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": "Internal server error",  # Don't leak details
            },
        }


def configure_logging(verbose: bool = False):
    """Configure logging for MCP server"""
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(
                sys.stderr
            )  # Log to stderr, not stdout (JSON-RPC uses stdout)
        ],
    )

    # Reduce noise from libraries
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)


def main():
    """Main entry point for stdio MCP server"""
    # Configure logging
    configure_logging(verbose=os.getenv("DEBUG") == "1")

    logger.info("Starting Dev-AID Code Search MCP Server")

    server = CodeSearchServer()

    # Read JSON-RPC requests from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_mcp_request(server, request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
            }
            print(json.dumps(error_response), flush=True)
        except Exception as e:
            logger.exception("Unexpected error in main loop")
            error_response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "Internal error"},
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
