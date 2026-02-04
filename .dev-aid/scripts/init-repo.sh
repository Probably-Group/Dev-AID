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
echo -e "${YELLOW}   Optional Feature: Multi-AI Router${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo ""
echo "The router enables intelligent orchestration across AI providers:"
echo "  ✓ Anthropic (Claude), Google (Gemini), OpenAI (GPT)"
echo "  ✓ Automatic model selection based on task type"
echo "  ✓ Cost optimization (97% savings on large context)"
echo "  ✓ Two-model review workflow (Challenger mode)"
echo "  ✓ Real-time cost tracking and budgets"
echo ""
echo "Requirements:"
echo "  • Python 3.9+"
echo "  • Virtual environment (recommended)"
echo "  • Authentication: Session auth (claude login/gcloud auth) OR API keys"
echo ""
read -p "Setup router with virtual environment? (Y/n) " -n 1 -r
echo

ROUTER_SETUP_REPLY=$REPLY

if [[ $ROUTER_SETUP_REPLY =~ ^[Yy]$ ]] || [[ -z $ROUTER_SETUP_REPLY ]]; then
    echo ""
    echo -e "${GREEN}Setting up router with virtual environment...${NC}"
    if [ -f ".dev-aid/orchestration/setup-venv.sh" ]; then
        ./.dev-aid/orchestration/setup-venv.sh
    else
        echo -e "${RED}✗ setup-venv.sh not found${NC}"
        echo "  Please ensure Dev-AID is properly installed"
    fi
else
    echo -e "${BLUE}→ Skipped router setup${NC}"
    echo "  You can set it up later with: ./.dev-aid/orchestration/setup-venv.sh"
    echo "  Or manually: pip install -r .dev-aid/orchestration/requirements.txt"
fi

echo ""
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo -e "${YELLOW}   Optional: Dev-AID Local Search${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}What is it?${NC}"
echo "  Search your codebase with natural language - completely local!"
echo ""
echo -e "${BLUE}Example:${NC}"
echo "  You ask: \"Find all authentication functions\""
echo "  AI searches YOUR code locally and finds them instantly"
echo ""
echo -e "${GREEN}Benefits:${NC}"
echo "  ✓ $0 cost (runs on your machine, not cloud API)"
echo "  ✓ 100% private (code never leaves your computer)"
echo "  ✓ Works offline (no internet needed)"
echo "  ✓ Instant results (semantic code search)"
echo ""
echo -e "${BLUE}Tool Support (MCP protocol):${NC}"
echo "  ✓ Auto-configured: Claude Code, Gemini CLI"
echo "  ✓ Compatible: VS Code Copilot, Cursor, Windsurf, Cline, Zed, JetBrains"
echo ""
echo -e "${BLUE}How it works:${NC}"
echo "  1. Indexes your code once (~5 minutes)"
echo "  2. AI automatically uses it when you ask code questions"
echo "  3. Returns real code from YOUR project"
echo ""
echo -e "${YELLOW}Requirements:${NC}"
echo "  • Python 3.12+"
echo "  • 1.2GB model download (EmbeddingGemma)"
echo "  • 2-5 minutes initial setup"
echo ""
echo -e "${BLUE}Powered by:${NC} claude-context-local (by FarhanAliRaza)"
echo ""
read -p "Install Dev-AID Local Search? (Y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo ""
    echo -e "${GREEN}Installing Dev-AID Local Search...${NC}"
    if [ -f ".dev-aid/scripts/setup-rag.sh" ]; then
        ./.dev-aid/scripts/setup-rag.sh
    else
        echo -e "${RED}✗ setup-rag.sh not found${NC}"
        echo "  Please ensure Dev-AID is properly installed"
    fi
else
    echo -e "${BLUE}→ Skipped Dev-AID Local Search installation${NC}"
    echo "  You can install it later with: ./.dev-aid/scripts/setup-rag.sh"
fi

# ============================================================================
# Optional: Security Tools Installation
# ============================================================================
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}   Optional Feature: Security Scanning Tools${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Dev-AID includes 5 security tools for pre-commit scanning:"
echo "  • Gitleaks  - Secret detection"
echo "  • Trivy     - Vulnerability scanning"
echo "  • Hadolint  - Dockerfile linting"
echo "  • Checkov   - IaC security"
echo "  • Opengrep  - SAST code analysis"
echo ""
echo -e "${BLUE}Requirements:${NC}"
echo "  • Homebrew (macOS) or curl (Linux)"
echo "  • ~500MB disk space"
echo "  • 2-5 minutes installation"
echo ""
read -p "Install security scanning tools? (Y/n) " -n 1 -r SECURITY_REPLY
echo

if [[ $SECURITY_REPLY =~ ^[Yy]$ ]] || [[ -z $SECURITY_REPLY ]]; then
    echo ""
    echo -e "${GREEN}Installing security tools...${NC}"
    if [ -f ".dev-aid/automation/tools/install-security-tools.sh" ]; then
        ./.dev-aid/automation/tools/install-security-tools.sh
    else
        echo -e "${YELLOW}⚠ install-security-tools.sh not found${NC}"
        echo "  Attempting Homebrew installation..."
        if command -v brew &> /dev/null; then
            brew install gitleaks trivy hadolint 2>/dev/null || true
            brew install pipx && pipx install checkov 2>/dev/null || true
            echo -e "${GREEN}✓ Installed via Homebrew${NC}"
        else
            echo -e "${RED}✗ Please install manually:${NC}"
            echo "  brew install gitleaks trivy hadolint"
            echo "  pipx install checkov"
            echo "  curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash"
        fi
    fi
else
    echo -e "${BLUE}→ Skipped security tools installation${NC}"
    echo "  You can install later with: ./.dev-aid/automation/tools/install-security-tools.sh"
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
if [[ $ROUTER_SETUP_REPLY =~ ^[Yy]$ ]] || [[ -z $ROUTER_SETUP_REPLY ]]; then
    echo "  ✓ Multi-AI router (Python venv)"
fi
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "  ✓ Dev-AID Local Search"
fi
if [[ $SECURITY_REPLY =~ ^[Yy]$ ]] || [[ -z $SECURITY_REPLY ]]; then
    echo "  ✓ Security scanning tools (Gitleaks, Trivy, Hadolint, Checkov, Opengrep)"
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
if [[ $ROUTER_SETUP_REPLY =~ ^[Yy]$ ]] || [[ -z $ROUTER_SETUP_REPLY ]]; then
    echo -e "${BLUE}Router CLI commands:${NC}"
    echo "  • .dev-aid/orchestration/router-cli.sh test"
    echo "  • .dev-aid/orchestration/router-cli.sh execute \"Your request\""
    echo "  • .dev-aid/orchestration/router-cli.sh status"
    echo ""
fi
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Add API keys to .dev-aid/config/.env"
echo "     ANTHROPIC_API_KEY=sk-ant-..."
echo "     GOOGLE_API_KEY=..."
echo "  2. Enable providers in .dev-aid/config/models.json"
if [[ $ROUTER_SETUP_REPLY =~ ^[Yy]$ ]] || [[ -z $ROUTER_SETUP_REPLY ]]; then
    echo "  3. Test router: .dev-aid/orchestration/router-cli.sh test"
fi
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "  4. Check RAG status: ./.dev-aid/scripts/rag-status.sh"
fi
echo ""
echo -e "${GREEN}Happy coding with Dev-AID! 🚀${NC}"
echo ""
