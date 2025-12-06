#!/usr/bin/env bash
# Onboarding Buddy - Interactive Setup
# Helps new developers get started quickly

set -euo pipefail

readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

check_tool() {
    local tool=$1
    if command -v "$tool" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $tool"
        return 0
    else
        echo -e "${RED}✗${NC} $tool (not installed)"
        return 1
    fi
}

main() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🚀 Dev-AID Onboarding Buddy${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    echo -e "${YELLOW}Step 1: Environment Check${NC}\n"

    # Check required tools
    check_tool git
    check_tool python3
    check_tool node || check_tool bun || echo -e "${YELLOW}⚠${NC}  No Node.js runtime (optional)"
    check_tool docker || echo -e "${YELLOW}⚠${NC}  Docker not found (optional)"

    echo ""
    echo -e "${YELLOW}Step 2: Project Structure${NC}\n"

    if [ -f "package.json" ]; then
        echo "📦 Node.js project detected"
        if [ -f "bun.lockb" ]; then
            echo "   → Package manager: bun"
            echo "   → Install: bun install"
        elif [ -f "pnpm-lock.yaml" ]; then
            echo "   → Package manager: pnpm"
            echo "   → Install: pnpm install"
        elif [ -f "yarn.lock" ]; then
            echo "   → Package manager: yarn"
            echo "   → Install: yarn install"
        else
            echo "   → Package manager: npm"
            echo "   → Install: npm install"
        fi
    fi

    if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
        echo "🐍 Python project detected"
        if grep -q "tool.poetry" pyproject.toml 2>/dev/null; then
            echo "   → Package manager: poetry"
            echo "   → Install: poetry install"
        elif grep -q "tool.uv" pyproject.toml 2>/dev/null; then
            echo "   → Package manager: uv"
            echo "   → Install: uv sync"
        else
            echo "   → Package manager: pip"
            echo "   → Install: pip install -r requirements.txt"
        fi
    fi

    if [ -f "Cargo.toml" ]; then
        echo "🦀 Rust project detected"
        echo "   → Build: cargo build"
    fi

    if [ -f "go.mod" ]; then
        echo "🐹 Go project detected"
        echo "   → Build: go build"
    fi

    echo ""
    echo -e "${YELLOW}Step 3: Dev-AID Features${NC}\n"

    echo "Available tools:"
    echo "  • .dev-aid/scripts/generate-ci.sh        Auto-generate CI/CD"
    echo "  • .dev-aid/scripts/map-architecture.sh   Visualize codebase"
    echo "  • .dev-aid/scripts/fabricate-data.sh     Generate test data"
    echo "  • .dev-aid/scripts/sync-docs.sh          Check doc drift"
    echo "  • .dev-aid/scripts/dev-aid-guide.sh      Interactive guide"

    echo ""
    echo -e "${YELLOW}Step 4: Next Steps${NC}\n"

    echo "1. Install dependencies (see above)"
    echo "2. Copy .env.example to .env (if exists)"
    echo "3. Read README.md for project-specific setup"
    echo "4. Run: .dev-aid/scripts/dev-aid-guide.sh for more help"

    echo ""
    echo -e "${GREEN}✅ Onboarding complete! Happy coding!${NC}\n"
}

main "$@"
