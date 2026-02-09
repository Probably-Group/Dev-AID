# Dev-AID Local Search

100% local semantic code search with MCP (Model Context Protocol) integration.

## Features

- **100% Local**: All processing happens on your machine, code never leaves
- **Semantic Search**: Uses EmbeddingGemma for intelligent code understanding
- **Fast**: FAISS vector indexing for instant results
- **Multi-Language**: Supports Python, JavaScript, TypeScript, Java, Go, Rust, C, C++
- **MCP Integration**: Works with Claude Code, Gemini CLI, and other MCP-compatible tools
- **Incremental**: Only re-indexes changed files

## Architecture

- **Embeddings**: SentenceTransformers with google/embeddinggemma-300m model
- **Indexing**: FAISS vector database (CPU by default, GPU optional)
- **Chunking**: Tree-sitter for intelligent code parsing
- **Protocol**: MCP (Model Context Protocol) for AI tool integration

## Installation

Automatically installed via Dev-AID's `setup-dev-aid.sh` script or manually:

```bash
cd .dev-aid/local-search
pip install -e .
```

## Usage

### Via MCP (Automatic in Claude Code/Gemini)

The MCP server runs automatically when you ask code questions:

```
You: "Find all authentication functions"
AI: *uses code-search MCP tool automatically*
```

### CLI (Manual)

```bash
# Index current directory
devaid-code-search index .

# Search
devaid-code-search search "authentication functions"

# Status
devaid-code-search status
```

## Storage

- **Models**: `~/.devaid-search/models/` (1.2GB EmbeddingGemma)
- **Index**: `~/.devaid-search/index/` (project-specific)
- **Config**: `~/.devaid-search/config.json`

## MCP Server

The MCP server provides these tools:

1. **search_code** - Search codebase with natural language
2. **index_directory** - Index a directory for search
3. **get_index_status** - View index statistics
4. **list_projects** - Show all indexed projects
5. **clear_index** - Clear index for current project

## Credits

Inspired by claude-context-local by FarhanAliRaza, reimplemented as self-contained
Dev-AID component for independence and further development.

## License

MIT License
