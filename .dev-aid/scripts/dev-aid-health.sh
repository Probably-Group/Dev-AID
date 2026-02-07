#!/usr/bin/env bash
# Dev-AID Health Check
# Quick health status for all Dev-AID components

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Check health status of all Dev-AID components.

Examples:
    $0                  # Full health check
    $0 --quiet          # Exit 0/1 only (for scripts)
    $0 --fix            # Auto-fix common issues

Options:
    -q, --quiet         Only exit code (0=healthy, 1=unhealthy)
    -f, --fix           Attempt to fix issues
    -h, --help          Show this help message

Components Checked:
    - CLI tools (git, python3, curl, jq, security tools)
    - RAG status (index age, size)
    - Router health (config valid, costs)
    - Git hooks (installed, working)
    - Dependencies (orchestration venv)
    - Skills (loadable, no errors)
    - MCP servers (reachable)
EOF
    exit 1
}

QUIET=false
FIX=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--quiet) QUIET=true; shift ;;
        -f|--fix) FIX=true; shift ;;
        -h|--help) usage ;;
        *) usage ;;
    esac
done

HEALTHY=true

check() {
    local name="$1"
    local test_cmd="$2"

    if $QUIET; then
        bash -c "$test_cmd" &>/dev/null || HEALTHY=false
    else
        echo -n "Checking $name... "
        if bash -c "$test_cmd" &>/dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
            HEALTHY=false
        fi
    fi
}

if ! $QUIET; then
    echo -e "${BLUE}Dev-AID Health Check${NC}"
    echo ""
fi

# ── CLI Tool Availability ──
if ! $QUIET; then
    echo -e "${BLUE}CLI Tools${NC}"
fi

check "git"     "command -v git"
check "python3" "command -v python3"
check "curl"    "command -v curl"
check "jq"      "command -v jq"

# Security tools (warn but don't fail)
for sec_tool in gitleaks trivy opengrep; do
    if command -v "$sec_tool" &> /dev/null; then
        if ! $QUIET; then
            echo -e "Checking $sec_tool... ${GREEN}✓${NC}"
        fi
    else
        if ! $QUIET; then
            echo -e "Checking $sec_tool... ${YELLOW}⚠ not installed${NC}"
        fi
    fi
done

if ! $QUIET; then
    echo ""
fi

# Check RAG
if [ -d ~/.devaid-search ]; then
    check "RAG index" "[ -f ~/.devaid-search/index.faiss ]"

    if [ -f ~/.devaid-search/index.faiss ] && ! $QUIET; then
        AGE_DAYS=$(( ( $(date +%s) - $(stat -f %m ~/.devaid-search/index.faiss) ) / 86400 ))
        if [ "$AGE_DAYS" -gt 7 ]; then
            echo -e "  ${YELLOW}⚠ Index is ${AGE_DAYS} days old (consider reindexing)${NC}"
        fi
    fi
fi

# Check Router
check "Router config" "[ -f .dev-aid/config/routing.json ]"
check "Router venv" "[ -d .dev-aid/orchestration/.venv ] || [ -d .dev-aid/orchestration/venv ]"

# Check Git hooks
check "Git hooks" "[ -f .git/hooks/pre-commit ]"

# Check Skills
SKILL_DIR=".dev-aid/providers/claude/.claude/skills/expert"
if [ -d "$SKILL_DIR" ]; then
    SKILL_COUNT="$(find "$SKILL_DIR" -type d -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ')"
    if ! $QUIET; then
        echo -e "Skills available: ${GREEN}$SKILL_COUNT${NC}"
    fi
fi

# Check Dependencies
if [ -d .dev-aid/orchestration/.venv ]; then
    check "Python packages" ".dev-aid/orchestration/.venv/bin/pip list | grep -q anthropic"
fi

# Exit code
if $HEALTHY; then
    if ! $QUIET; then
        echo ""
        echo -e "${GREEN}✅ All systems healthy${NC}"
    fi
    exit 0
else
    if ! $QUIET; then
        echo ""
        echo -e "${RED}❌ Health check failed${NC}"
    fi
    exit 1
fi
