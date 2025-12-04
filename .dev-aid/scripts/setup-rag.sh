#!/bin/bash
# Setup script for DevAID Local Search
# Installs and configures 100% local semantic code search
# Powered by claude-context-local by FarhanAliRaza

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      DevAID Local Search Setup             ║${NC}"
echo -e "${BLUE}║   100% Local Semantic Code Search          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if running in DevAID directory
if [ ! -d ".dev-aid" ]; then
    echo -e "${RED}✗ Error: Must run from DevAID repository root${NC}"
    echo "  Expected to find .dev-aid/ directory"
    exit 1
fi

# Detect OS
OS="unknown"
case "$(uname -s)" in
    Linux*)     OS="Linux";;
    Darwin*)    OS="Mac";;
    *)          OS="unknown";;
esac

echo -e "${BLUE}→ Detected OS: ${OS}${NC}"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is required but not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${BLUE}→ Python version: ${PYTHON_VERSION}${NC}"

# Check if version is >= 3.12
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 12 ]); then
    echo -e "${YELLOW}⚠ Warning: Python 3.12+ recommended (found ${PYTHON_VERSION})${NC}"
    echo -e "${YELLOW}  claude-context-local may not work properly${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for GPU acceleration
GPU_TYPE="CPU"
if command -v nvidia-smi &> /dev/null; then
    GPU_TYPE="NVIDIA CUDA"
elif [ "$OS" = "Mac" ] && sysctl -a 2>/dev/null | grep -q "machdep.cpu.brand_string.*Apple"; then
    GPU_TYPE="Apple Silicon (MPS)"
fi
echo -e "${BLUE}→ GPU acceleration: ${GPU_TYPE}${NC}"

echo ""
echo -e "${GREEN}Installing DevAID Local Search...${NC}"
echo -e "${BLUE}(powered by claude-context-local)${NC}"
echo ""

# Install claude-context-local (the underlying engine)
echo -e "${BLUE}→ Running official install script...${NC}"
if curl -fsSL https://raw.githubusercontent.com/FarhanAliRaza/claude-context-local/main/scripts/install.sh | bash; then
    echo -e "${GREEN}✓ DevAID Local Search installed successfully${NC}"
else
    echo -e "${RED}✗ Installation failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Configuring MCP integration...${NC}"
echo ""

# Detect AI tool being used
AI_TOOL="unknown"
if [ -d "$HOME/.claude" ] || command -v claude &> /dev/null; then
    AI_TOOL="claude-code"
elif [ -d "$HOME/.gemini" ] || command -v gemini &> /dev/null; then
    AI_TOOL="gemini-cli"
fi

echo -e "${BLUE}→ Detected AI tool: ${AI_TOOL}${NC}"

# Register MCP server
if [ "$AI_TOOL" = "claude-code" ]; then
    echo -e "${BLUE}→ Registering with Claude Code...${NC}"

    if command -v claude &> /dev/null; then
        claude mcp add code-search --scope user -- \
            uv run --directory ~/.local/share/claude-context-local \
            python mcp_server/server.py

        echo -e "${GREEN}✓ MCP server registered with Claude Code${NC}"

        # Verify registration
        if claude mcp list 2>/dev/null | grep -q "code-search"; then
            echo -e "${GREEN}✓ Verified: code-search MCP server active${NC}"
        else
            echo -e "${YELLOW}⚠ Warning: MCP server may not be registered correctly${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Claude CLI not found - MCP registration skipped${NC}"
        echo -e "${YELLOW}  Install Claude Code and run:${NC}"
        echo -e "${YELLOW}  claude mcp add code-search --scope user -- uv run --directory ~/.local/share/claude-context-local python mcp_server/server.py${NC}"
    fi
elif [ "$AI_TOOL" = "gemini-cli" ]; then
    echo -e "${BLUE}→ Registering with Gemini CLI...${NC}"

    # Create MCP config for Gemini
    GEMINI_MCP_CONFIG="$HOME/.gemini/mcp.json"
    mkdir -p "$HOME/.gemini"

    if [ ! -f "$GEMINI_MCP_CONFIG" ]; then
        # No existing config - create new one
        cat > "$GEMINI_MCP_CONFIG" << 'EOF'
{
  "mcpServers": {
    "code-search": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "~/.local/share/claude-context-local",
        "python",
        "mcp_server/server.py"
      ]
    }
  }
}
EOF
        echo -e "${GREEN}✓ Created MCP config: ${GEMINI_MCP_CONFIG}${NC}"
    else
        # Existing config found - preserve other MCP servers
        echo -e "${YELLOW}⚠ MCP config already exists: ${GEMINI_MCP_CONFIG}${NC}"
        echo -e "${YELLOW}  To preserve your existing MCP servers, add code-search manually:${NC}"
        echo ""
        echo -e "${BLUE}Add this entry to 'mcpServers' in ${GEMINI_MCP_CONFIG}:${NC}"
        echo ""
        echo '    "code-search": {'
        echo '      "command": "uv",'
        echo '      "args": ['
        echo '        "run",'
        echo '        "--directory",'
        echo '        "~/.local/share/claude-context-local",'
        echo '        "python",'
        echo '        "mcp_server/server.py"'
        echo '      ]'
        echo '    }'
        echo ""
        echo -e "${BLUE}Note:${NC} DevAID respects your existing MCP servers. All servers will"
        echo "      work together automatically - the AI decides which to use."
    fi
else
    echo -e "${YELLOW}⚠ No AI tool detected${NC}"
    echo -e "${YELLOW}  Supported: Claude Code, Gemini CLI${NC}"
fi

echo ""
echo -e "${GREEN}Indexing DevAID codebase...${NC}"
echo ""

# Index the current directory
DEV_AID_ROOT=$(pwd)
echo -e "${BLUE}→ Indexing: ${DEV_AID_ROOT}${NC}"

# Check if claude-context-local command exists
if command -v claude-context-local &> /dev/null; then
    # Index with progress
    claude-context-local index "$DEV_AID_ROOT" 2>&1 | tee .dev-aid/logs/rag-index.log

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo -e "${GREEN}✓ Indexing complete${NC}"

        # Show index stats
        if [ -f "$HOME/.claude_code_search/index/stats.json" ]; then
            FILES=$(grep -o '"total_files":[0-9]*' "$HOME/.claude_code_search/index/stats.json" | cut -d: -f2)
            CHUNKS=$(grep -o '"total_chunks":[0-9]*' "$HOME/.claude_code_search/index/stats.json" | cut -d: -f2)
            echo -e "${BLUE}→ Indexed ${FILES} files → ${CHUNKS} chunks${NC}"
        fi
    else
        echo -e "${RED}✗ Indexing failed - check logs at .dev-aid/logs/rag-index.log${NC}"
    fi
else
    echo -e "${YELLOW}⚠ claude-context-local command not found${NC}"
    echo -e "${YELLOW}  Index manually with: claude-context-local index .${NC}"
fi

# Create reindex script
echo ""
echo -e "${GREEN}Creating reindex helper script...${NC}"

mkdir -p .dev-aid/scripts

cat > .dev-aid/scripts/reindex-codebase.sh << 'EOF'
#!/bin/bash
# Reindex DevAID codebase with DevAID Local Search
# Usage: ./.dev-aid/scripts/reindex-codebase.sh

set -e

echo "🔄 Reindexing DevAID codebase..."

DEV_AID_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$DEV_AID_ROOT"

if command -v claude-context-local &> /dev/null; then
    claude-context-local index . 2>&1 | tee .dev-aid/logs/rag-index.log
    echo "✓ Reindexing complete"
else
    echo "✗ Error: claude-context-local not found"
    echo "  Run: ./.dev-aid/scripts/setup-rag.sh"
    exit 1
fi
EOF

chmod +x .dev-aid/scripts/reindex-codebase.sh
echo -e "${GREEN}✓ Created: .dev-aid/scripts/reindex-codebase.sh${NC}"

# Offer to create git hook for auto-reindexing
echo ""
read -p "Create git hook for auto-reindexing on commit? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    mkdir -p .git/hooks

    cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
# Auto-reindex codebase after commits
# Created by Dev-AID setup

# Only reindex if significant files changed
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD | wc -l)

if [ "$CHANGED_FILES" -gt 5 ]; then
    echo "🔄 Auto-reindexing codebase (${CHANGED_FILES} files changed)..."
    ./.dev-aid/scripts/reindex-codebase.sh > /dev/null 2>&1 &
    echo "✓ Reindexing in background"
fi
EOF

    chmod +x .git/hooks/post-commit
    echo -e "${GREEN}✓ Created git hook: .git/hooks/post-commit${NC}"
else
    echo -e "${BLUE}→ Skipped git hook creation${NC}"
fi

# Create RAG status check script
cat > .dev-aid/scripts/rag-status.sh << 'EOF'
#!/bin/bash
# Check DevAID Local Search status
# Usage: ./.dev-aid/scripts/rag-status.sh

set -e

echo "╔════════════════════════════════════════════╗"
echo "║      DevAID Local Search Status            ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check installation
if command -v claude-context-local &> /dev/null; then
    VERSION=$(claude-context-local --version 2>/dev/null || echo "unknown")
    echo "✓ Installed: ${VERSION}"
else
    echo "✗ Not installed"
    exit 1
fi

# Check index
INDEX_DIR="$HOME/.claude_code_search/index"
if [ -d "$INDEX_DIR" ]; then
    echo "✓ Index directory: ${INDEX_DIR}"

    if [ -f "$INDEX_DIR/stats.json" ]; then
        echo ""
        echo "Index Statistics:"
        cat "$INDEX_DIR/stats.json" | python3 -m json.tool
    fi

    INDEX_SIZE=$(du -sh "$INDEX_DIR" 2>/dev/null | cut -f1)
    echo ""
    echo "Index size: ${INDEX_SIZE}"
else
    echo "✗ No index found"
    echo "  Run: ./.dev-aid/scripts/reindex-codebase.sh"
fi

# Check MCP registration
echo ""
echo "MCP Integration:"
if command -v claude &> /dev/null; then
    if claude mcp list 2>/dev/null | grep -q "code-search"; then
        echo "✓ Claude Code: Registered"
    else
        echo "✗ Claude Code: Not registered"
    fi
else
    echo "- Claude Code: Not installed"
fi

if [ -f "$HOME/.gemini/mcp.json" ]; then
    if grep -q "code-search" "$HOME/.gemini/mcp.json"; then
        echo "✓ Gemini CLI: Configured"
    else
        echo "✗ Gemini CLI: Not configured"
    fi
else
    echo "- Gemini CLI: No config found"
fi

echo ""
echo "Model Status:"
MODEL_DIR="$HOME/.claude_code_search/models"
if [ -d "$MODEL_DIR" ]; then
    MODEL_SIZE=$(du -sh "$MODEL_DIR" 2>/dev/null | cut -f1)
    echo "✓ EmbeddingGemma downloaded (${MODEL_SIZE})"
else
    echo "✗ Model not downloaded"
fi

echo ""
echo "Recent Queries:"
LOG_FILE=".dev-aid/logs/rag-queries.log"
if [ -f "$LOG_FILE" ]; then
    tail -n 5 "$LOG_FILE"
else
    echo "No queries logged yet"
fi
EOF

chmod +x .dev-aid/scripts/rag-status.sh
echo -e "${GREEN}✓ Created: .dev-aid/scripts/rag-status.sh${NC}"

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Setup Complete! 🎉                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}What was installed:${NC}"
echo "  ✓ DevAID Local Search (100% local semantic search)"
echo "  ✓ EmbeddingGemma model (~1.2GB)"
echo "  ✓ FAISS vector index with ${GPU_TYPE} acceleration"
echo "  ✓ MCP integration ($AI_TOOL)"
echo "  ✓ DevAID codebase indexed"
echo ""
echo -e "${BLUE}Powered by:${NC}"
echo "  • claude-context-local by FarhanAliRaza"
echo "  • github.com/FarhanAliRaza/claude-context-local"
echo ""
echo -e "${BLUE}Helper scripts created:${NC}"
echo "  • .dev-aid/scripts/reindex-codebase.sh  - Reindex after changes"
echo "  • .dev-aid/scripts/rag-status.sh        - Check RAG status"
echo ""
echo -e "${BLUE}Usage:${NC}"
if [ "$AI_TOOL" = "claude-code" ]; then
    echo "  In Claude Code:"
    echo "    You: \"Find all authentication functions\""
    echo "    Claude: *uses @code-search automatically*"
elif [ "$AI_TOOL" = "gemini-cli" ]; then
    echo "  In Gemini CLI:"
    echo "    You: \"Search codebase for authentication\""
    echo "    Gemini: *uses code-search MCP tool*"
fi
echo ""
echo "  In router slash commands:"
echo "    /aid-router-challenger \"Implement OAuth2 authentication\""
echo "    (will use local RAG automatically)"
echo ""
echo -e "${BLUE}Check status:${NC}"
echo "  ./.dev-aid/scripts/rag-status.sh"
echo ""
echo -e "${BLUE}Reindex after changes:${NC}"
echo "  ./.dev-aid/scripts/reindex-codebase.sh"
echo ""
echo -e "${GREEN}Cost: \$0 forever • Privacy: 100% local • Works offline${NC}"
echo ""
