#!/bin/bash
# Dev-AID Repository Initialization Script
# Sets up Dev-AID environment with optional features

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Dev-AID Repository Initialization     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if in Dev-AID directory
if [ ! -d ".dev-aid" ]; then
    echo -e "${RED}✗ Error: Must run from Dev-AID repository root${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${GREEN}Setting up directory structure...${NC}"
mkdir -p .dev-aid/logs
mkdir -p .dev-aid/scripts
mkdir -p .dev-aid/config
mkdir -p .dev-aid/memory-bank
mkdir -p .dev-aid/skills/expert
echo -e "${GREEN}✓ Directory structure created${NC}"

# Initialize config files if they don't exist
if [ ! -f ".dev-aid/config/routing.json" ]; then
    echo -e "${BLUE}→ Creating default routing.json...${NC}"
    cat > .dev-aid/config/routing.json << 'EOF'
{
  "default_mode": "solo",
  "modes": {
    "challenger": {
      "enabled": true,
      "primary_model": "claude-sonnet",
      "challenger_model": "gemini-flash",
      "auto_refine_on": ["HIGH", "CRITICAL"],
      "review_triggers": [
        "auth", "authentication", "password", "crypto",
        "encryption", "token", "session", "oauth", "jwt",
        "payment", "financial", "sensitive"
      ]
    },
    "ensemble": {
      "enabled": true,
      "routing_strategy": "semantic",
      "task_routes": {
        "massive_context": "gemini-flash",
        "code_generation": "claude-sonnet",
        "security_audit": "claude-sonnet",
        "documentation": "gpt-4o",
        "debugging": "claude-sonnet",
        "complex_reasoning": "claude-opus"
      }
    }
  },
  "fallback_chain": ["claude-sonnet", "gpt-4o", "gemini-flash"],
  "cost_limit_per_day": 100.0
}
EOF
    echo -e "${GREEN}✓ Created routing.json${NC}"
fi

if [ ! -f ".dev-aid/config/models.json" ]; then
    echo -e "${BLUE}→ Creating default models.json...${NC}"
    cat > .dev-aid/config/models.json << 'EOF'
{
  "models": {
    "claude-sonnet": {
      "provider": "anthropic",
      "model": "claude-sonnet-4.5-20250929",
      "cost_per_mtok": {"input": 3.0, "output": 15.0},
      "max_context": 200000,
      "strengths": ["code_generation", "security", "reasoning"],
      "description": "Balanced model - best for most code generation"
    },
    "claude-opus": {
      "provider": "anthropic",
      "model": "claude-opus-4",
      "cost_per_mtok": {"input": 15.0, "output": 75.0},
      "max_context": 200000,
      "strengths": ["complex_reasoning", "architecture", "design"],
      "description": "Most capable - for complex tasks"
    },
    "gemini-flash": {
      "provider": "google",
      "model": "gemini-2.0-flash-exp",
      "cost_per_mtok": {"input": 0.075, "output": 0.30},
      "max_context": 2000000,
      "strengths": ["massive_context", "cost_effective", "review"],
      "description": "2M context window - perfect for large codebases"
    },
    "gpt-4o": {
      "provider": "openai",
      "model": "gpt-4o-2024-11-20",
      "cost_per_mtok": {"input": 2.5, "output": 10.0},
      "max_context": 128000,
      "strengths": ["documentation", "explanation", "balanced"],
      "description": "Good all-rounder"
    }
  }
}
EOF
    echo -e "${GREEN}✓ Created models.json${NC}"
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo -e "${YELLOW}   Optional Feature: Local Semantic Search${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo ""
echo "claude-context-local provides:"
echo "  ✓ 100% local semantic code search"
echo "  ✓ Zero API costs for RAG"
echo "  ✓ Privacy-first (code never leaves machine)"
echo "  ✓ Works offline"
echo "  ✓ AST-based code understanding"
echo ""
echo "Requirements:"
echo "  • Python 3.12+"
echo "  • 1.2GB model download"
echo "  • 2-5 minutes setup time"
echo ""
read -p "Install claude-context-local? (Y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo ""
    echo -e "${GREEN}Installing claude-context-local...${NC}"
    if [ -f ".dev-aid/scripts/setup-rag.sh" ]; then
        ./.dev-aid/scripts/setup-rag.sh
    else
        echo -e "${RED}✗ setup-rag.sh not found${NC}"
        echo "  Please ensure Dev-AID is properly installed"
    fi
else
    echo -e "${BLUE}→ Skipped claude-context-local installation${NC}"
    echo "  You can install it later with: ./.dev-aid/scripts/setup-rag.sh"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      Dev-AID Initialization Complete!      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}What's configured:${NC}"
echo "  ✓ Directory structure"
echo "  ✓ Routing configuration"
echo "  ✓ Model registry"
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "  ✓ Local semantic search (claude-context-local)"
fi
echo ""
echo -e "${BLUE}Available router commands:${NC}"
echo "  • /aid-router-challenger       - Two-AI review workflow"
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "  • /aid-router-challenger-rag   - With local semantic search"
fi
echo "  • /aid-router-ensemble         - Smart model routing"
echo "  • /aid-router-status           - View routing stats"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Configure API keys (ANTHROPIC_API_KEY, GOOGLE_API_KEY)"
echo "  2. Try a router command in Claude Code or Gemini CLI"
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "  3. Check RAG status: ./.dev-aid/scripts/rag-status.sh"
fi
echo ""
echo -e "${GREEN}Happy coding with Dev-AID! 🚀${NC}"
echo ""
