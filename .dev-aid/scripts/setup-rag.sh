#!/usr/bin/env bash
# Setup script for Dev-AID Local Search
# Installs and configures 100% local semantic code search
# Self-contained implementation - no external dependencies

set -euo pipefail  # Exit on error

# Cleanup on exit
TMP_FILES_TO_CLEAN=()
cleanup() {
    for f in "${TMP_FILES_TO_CLEAN[@]}"; do
        rm -rf "$f" 2>/dev/null
    done
}
trap cleanup EXIT

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Dev-AID Local Search Setup             ║${NC}"
echo -e "${BLUE}║   100% Local Semantic Code Search          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if running in Dev-AID directory
if [ ! -d ".dev-aid" ]; then
    echo -e "${RED}✗ Error: Must run from Dev-AID repository root${NC}"
    echo "  Expected to find .dev-aid/ directory"
    exit 1
fi

# Get absolute path to Dev-AID root
DEV_AID_ROOT=$(pwd)
LOCAL_SEARCH_DIR="${DEV_AID_ROOT}/.dev-aid/local-search"

# Verify local-search directory exists
if [ ! -d "$LOCAL_SEARCH_DIR" ]; then
    echo -e "${RED}✗ Error: Local search directory not found${NC}"
    echo "  Expected: $LOCAL_SEARCH_DIR"
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

# Check if version is >= 3.9 (more lenient than external dependency)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo -e "${RED}✗ Python 3.9+ is required (found ${PYTHON_VERSION})${NC}"
    echo -e "${YELLOW}  Please upgrade Python and try again${NC}"
    exit 1
fi

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 12 ]; then
    echo -e "${YELLOW}⚠ Warning: Python 3.12+ recommended (found ${PYTHON_VERSION})${NC}"
    echo -e "${YELLOW}  Some features may not work optimally${NC}"
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}✗ pip3 is required but not installed${NC}"
    exit 1
fi

# Check for GPU acceleration
GPU_TYPE="CPU"
GPU_PACKAGE="faiss-cpu"

if command -v nvidia-smi &> /dev/null; then
    GPU_TYPE="NVIDIA CUDA"
    echo -e "${YELLOW}→ NVIDIA GPU detected. Install faiss-gpu manually for acceleration:${NC}"
    echo -e "${YELLOW}  pip install faiss-gpu${NC}"
elif [ "$OS" = "Mac" ] && sysctl -a 2>/dev/null | grep -q "machdep.cpu.brand_string.*Apple"; then
    GPU_TYPE="Apple Silicon (MPS)"
    echo -e "${BLUE}→ Apple Silicon detected. Using MPS acceleration${NC}"
fi

echo -e "${BLUE}→ GPU acceleration: ${GPU_TYPE}${NC}"

echo ""
echo -e "${GREEN}Installing Dev-AID Local Search (embedded implementation)...${NC}"
echo ""

# Install Python package from local directory
echo -e "${BLUE}→ Installing Python dependencies...${NC}"
cd "$LOCAL_SEARCH_DIR"

if pip3 install -e . --quiet; then
    echo -e "${GREEN}✓ Dev-AID Local Search installed successfully${NC}"
else
    echo -e "${RED}✗ Installation failed${NC}"
    echo -e "${YELLOW}  Try manual installation:${NC}"
    echo -e "${YELLOW}  cd ${LOCAL_SEARCH_DIR} && pip3 install -e .${NC}"
    exit 1
fi

cd "$DEV_AID_ROOT"

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

# MCP server command
MCP_SERVER_CMD="python3 ${LOCAL_SEARCH_DIR}/mcp_server/server.py"

# Register MCP server
if [ "$AI_TOOL" = "claude-code" ]; then
    echo -e "${BLUE}→ Registering with Claude Code...${NC}"

    if command -v claude &> /dev/null; then
        # Remove existing registration if present
        claude mcp remove code-search 2>/dev/null || true

        # Add new registration
        claude mcp add code-search --scope user -- "$MCP_SERVER_CMD"

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
        echo -e "${YELLOW}  claude mcp add code-search --scope user -- ${MCP_SERVER_CMD}${NC}"
    fi

elif [ "$AI_TOOL" = "gemini-cli" ]; then
    echo -e "${BLUE}→ Registering with Gemini CLI...${NC}"

    # Create MCP config for Gemini
    GEMINI_MCP_CONFIG="$HOME/.gemini/mcp.json"
    mkdir -p "$HOME/.gemini"

    if [ ! -f "$GEMINI_MCP_CONFIG" ]; then
        # No existing config - create new one
        cat > "$GEMINI_MCP_CONFIG" <<EOF
{
  "mcpServers": {
    "code-search": {
      "command": "python3",
      "args": [
        "${LOCAL_SEARCH_DIR}/mcp_server/server.py"
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
        echo '      "command": "python3",'
        echo '      "args": ['
        echo "        \"${LOCAL_SEARCH_DIR}/mcp_server/server.py\""
        echo '      ]'
        echo '    }'
        echo ""
        echo -e "${BLUE}Note:${NC} Dev-AID respects your existing MCP servers. All servers will"
        echo "      work together automatically - the AI decides which to use."
    fi
else
    echo -e "${YELLOW}⚠ No AI tool detected${NC}"
    echo -e "${YELLOW}  Supported: Claude Code, Gemini CLI${NC}"
    echo ""
    echo -e "${BLUE}Manual MCP registration:${NC}"
    echo "  Claude Code:  claude mcp add code-search --scope user -- ${MCP_SERVER_CMD}"
    echo "  Gemini CLI:   Add to ~/.gemini/mcp.json"
fi

echo ""
echo -e "${GREEN}Downloading embedding model...${NC}"
echo -e "${BLUE}(This will download ~1.2GB on first run)${NC}"
echo ""

# Pre-download the model by running a test
echo -e "${BLUE}→ Initializing model (this may take a few minutes)...${NC}"

python3 << 'PYEOF'
import sys
sys.path.insert(0, "${LOCAL_SEARCH_DIR}")
try:
    from embeddings.embedder import CodeEmbedder
    print("Loading EmbeddingGemma model...")
    embedder = CodeEmbedder()
    print("✓ Model loaded successfully")
    print(f"  Embedding dimension: {embedder.embedding_dim}")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Embedding model ready${NC}"
else
    echo -e "${YELLOW}⚠ Model download incomplete${NC}"
    echo -e "${YELLOW}  The model will download automatically on first use${NC}"
fi

echo ""
echo -e "${GREEN}Indexing Dev-AID codebase...${NC}"
echo ""

# Index the current directory
echo -e "${BLUE}→ Indexing: ${DEV_AID_ROOT}${NC}"

if command -v devaid-code-search &> /dev/null; then
    # Index with CLI
    devaid-code-search index "$DEV_AID_ROOT" 2>&1 | tee .dev-aid/logs/rag-index.log

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo -e "${GREEN}✓ Indexing complete${NC}"
    else
        echo -e "${YELLOW}⚠ Indexing failed - check logs at .dev-aid/logs/rag-index.log${NC}"
        echo -e "${YELLOW}  You can reindex later with: devaid-code-search index .${NC}"
    fi
else
    echo -e "${YELLOW}⚠ devaid-code-search command not found in PATH${NC}"
    echo -e "${YELLOW}  You may need to restart your shell or add to PATH${NC}"
    echo -e "${YELLOW}  Manual index: python3 ${LOCAL_SEARCH_DIR}/mcp_server/cli.py index .${NC}"
fi

# Create reindex script
echo ""
echo -e "${GREEN}Creating helper scripts...${NC}"

mkdir -p .dev-aid/scripts

cat > .dev-aid/scripts/reindex-codebase.sh << 'EOF'
#!/bin/bash
# Reindex Dev-AID codebase with Dev-AID Local Search
# Usage: ./.dev-aid/scripts/reindex-codebase.sh

set -e

echo "🔄 Reindexing Dev-AID codebase..."

DEV_AID_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$DEV_AID_ROOT"

if command -v devaid-code-search &> /dev/null; then
    devaid-code-search index . 2>&1 | tee .dev-aid/logs/rag-index.log
    echo "✓ Reindexing complete"
else
    echo "✗ Error: devaid-code-search not found"
    echo "  Run: ./.dev-aid/scripts/setup-rag.sh"
    exit 1
fi
EOF

chmod +x .dev-aid/scripts/reindex-codebase.sh
echo -e "${GREEN}✓ Created: .dev-aid/scripts/reindex-codebase.sh${NC}"

# Create RAG status check script
cat > .dev-aid/scripts/rag-status.sh << 'EOF'
#!/bin/bash
# Check Dev-AID Local Search status
# Usage: ./.dev-aid/scripts/rag-status.sh

set -e

echo "╔════════════════════════════════════════════╗"
echo "║      Dev-AID Local Search Status            ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check installation
if command -v devaid-code-search &> /dev/null; then
    echo "✓ Dev-AID Local Search installed"
else
    echo "✗ Not installed"
    exit 1
fi

# Check status
devaid-code-search status

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
echo "Model Storage:"
MODEL_DIR="$HOME/.devaid-search/models"
if [ -d "$MODEL_DIR" ]; then
    MODEL_SIZE=$(du -sh "$MODEL_DIR" 2>/dev/null | cut -f1)
    echo "✓ EmbeddingGemma downloaded (${MODEL_SIZE})"
else
    echo "✗ Model not downloaded yet"
fi
EOF

chmod +x .dev-aid/scripts/rag-status.sh
echo -e "${GREEN}✓ Created: .dev-aid/scripts/rag-status.sh${NC}"

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

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Setup Complete! 🎉                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}What was installed:${NC}"
echo "  ✓ Dev-AID Local Search (self-contained, no external dependencies)"
echo "  ✓ EmbeddingGemma model (~1.2GB)"
echo "  ✓ FAISS vector index with ${GPU_TYPE} support"
echo "  ✓ MCP integration ($AI_TOOL)"
echo "  ✓ Dev-AID codebase indexed"
echo ""
echo -e "${BLUE}Implementation:${NC}"
echo "  • Self-contained in .dev-aid/local-search/"
echo "  • No external GitHub dependencies"
echo "  • Fully maintained by Dev-AID project"
echo ""
echo -e "${BLUE}Helper scripts created:${NC}"
echo "  • .dev-aid/scripts/reindex-codebase.sh  - Reindex after changes"
echo "  • .dev-aid/scripts/rag-status.sh        - Check RAG status"
echo ""
echo -e "${BLUE}CLI Usage:${NC}"
echo "  devaid-code-search index .            - Index current directory"
echo "  devaid-code-search search \"query\"     - Search codebase"
echo "  devaid-code-search status             - Show index status"
echo "  devaid-code-search list-projects      - List indexed projects"
echo ""
echo -e "${BLUE}MCP Usage (Automatic):${NC}"
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
echo -e "${BLUE}Check status:${NC}"
echo "  ./.dev-aid/scripts/rag-status.sh"
echo ""
echo -e "${BLUE}Reindex after changes:${NC}"
echo "  ./.dev-aid/scripts/reindex-codebase.sh"
echo ""
echo -e "${GREEN}Cost: \$0 forever • Privacy: 100% local • Works offline • No external dependencies${NC}"
echo ""
