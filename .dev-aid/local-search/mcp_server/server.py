"""Dev-AID Local Search MCP Server

Provides code search capabilities via MCP (Model Context Protocol)
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from embeddings.embedder import CodeEmbedder
from chunking.chunker import MultiLanguageChunker
from search.index import CodeSearchIndex, SearchResult
from utils.storage import StorageManager


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
            self.embedder = CodeEmbedder(cache_dir=str(self.storage.models_dir))

    def _ensure_index(self, project_path: str):
        """Ensure index is loaded for project"""
        if self.current_project != project_path or self.index is None:
            self.current_project = project_path
            project_dir = self.storage.get_project_dir(project_path)

            self._ensure_embedder()
            self.index = CodeSearchIndex(
                index_dir=str(project_dir),
                embedding_dim=self.embedder.embedding_dim
            )

    def search_code(self, query: str, project_path: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search code with natural language query

        Args:
            query: Natural language search query
            project_path: Path to project being searched
            top_k: Number of results to return

        Returns:
            List of search results with code chunks
        """
        try:
            # Ensure index is loaded
            self._ensure_index(project_path)

            if self.index is None or len(self.index.chunks) == 0:
                # No index exists, try to build it
                print(f"No index found for {project_path}, building...")
                self.index_directory(project_path)

            # Generate query embedding
            query_embedding = self.embedder.embed_query(query)

            # Search
            results = self.index.search(query_embedding, top_k=top_k)

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result.chunk.content,
                    "file_path": result.chunk.file_path,
                    "start_line": result.chunk.start_line,
                    "end_line": result.chunk.end_line,
                    "language": result.chunk.language,
                    "score": round(result.score, 4),
                    "rank": result.rank
                })

            return formatted_results

        except Exception as e:
            return [{"error": str(e)}]

    def index_directory(self, directory: str) -> Dict[str, Any]:
        """
        Index a directory for code search

        Args:
            directory: Path to directory

        Returns:
            Index statistics
        """
        try:
            directory = os.path.abspath(directory)
            print(f"Indexing directory: {directory}")

            # Ensure embedder is loaded
            self._ensure_embedder()

            # Chunk all code files
            print("Chunking code files...")
            chunks = self.chunker.chunk_directory(directory)

            if not chunks:
                return {"error": "No supported code files found"}

            print(f"Found {len(chunks)} code chunks")

            # Generate embeddings
            print("Generating embeddings...")
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = self.embedder.embed(chunk_texts)

            # Build index
            print("Building search index...")
            self._ensure_index(directory)
            self.index.build(chunks, embeddings)

            # Save index
            self.index.save()

            return self.index.get_stats()

        except Exception as e:
            return {"error": str(e)}

    def get_index_status(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get index status

        Args:
            project_path: Path to project (optional)

        Returns:
            Index statistics
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
                "current_project": self.current_project
            }

        except Exception as e:
            return {"error": str(e)}

    def list_projects(self) -> Dict[str, Any]:
        """List all indexed projects"""
        try:
            projects = self.storage.list_projects()
            return {
                "total_projects": len(projects),
                "projects": [{"path": path, "hash": hash_val} for path, hash_val in projects.items()]
            }
        except Exception as e:
            return {"error": str(e)}

    def clear_index(self, project_path: str) -> Dict[str, str]:
        """
        Clear index for a project

        Args:
            project_path: Path to project

        Returns:
            Status message
        """
        try:
            self._ensure_index(project_path)
            if self.index:
                self.index.clear()
            return {"status": "Index cleared successfully"}
        except Exception as e:
            return {"error": str(e)}


def handle_mcp_request(server: CodeSearchServer, request: Dict[str, Any]) -> Dict[str, Any]:
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

    try:
        # Handle different methods
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "devaid-code-search",
                    "version": "1.0.0"
                }
            }

        elif method == "tools/list":
            result = {
                "tools": [
                    {
                        "name": "search_code",
                        "description": "Search codebase using natural language query",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Natural language search query"},
                                "project_path": {"type": "string", "description": "Path to project"},
                                "top_k": {"type": "integer", "description": "Number of results (default: 10)"}
                            },
                            "required": ["query", "project_path"]
                        }
                    },
                    {
                        "name": "index_directory",
                        "description": "Index a directory for code search",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "directory": {"type": "string", "description": "Directory path to index"}
                            },
                            "required": ["directory"]
                        }
                    },
                    {
                        "name": "get_index_status",
                        "description": "Get status of code search index",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_path": {"type": "string", "description": "Optional project path"}
                            }
                        }
                    },
                    {
                        "name": "list_projects",
                        "description": "List all indexed projects",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "clear_index",
                        "description": "Clear index for a project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_path": {"type": "string", "description": "Project path"}
                            },
                            "required": ["project_path"]
                        }
                    }
                ]
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name == "search_code":
                result = server.search_code(**arguments)
            elif tool_name == "index_directory":
                result = server.index_directory(**arguments)
            elif tool_name == "get_index_status":
                result = server.get_index_status(**arguments)
            elif tool_name == "list_projects":
                result = server.list_projects()
            elif tool_name == "clear_index":
                result = server.clear_index(**arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        else:
            raise ValueError(f"Unknown method: {method}")

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }


def main():
    """Main entry point for stdio MCP server"""
    server = CodeSearchServer()

    # Read JSON-RPC requests from stdin
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_mcp_request(server, request)
            print(json.dumps(response), flush=True)
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
