#!/usr/bin/env bash
# Dev-AID Prerequisite Checker
# Verifies that required tools are installed before Dev-AID setup
#
# Usage:
#   ./check-prerequisites.sh              # Interactive check with install prompts
#   ./check-prerequisites.sh --quiet      # Exit 0/1 only (for scripts)
#   ./check-prerequisites.sh --install    # Auto-install missing tools (no prompts)

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

QUIET=false
AUTO_INSTALL=false
MISSING_CRITICAL=()
MISSING_RECOMMENDED=()
MISSING_SECURITY=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--quiet) QUIET=true; shift ;;
        --install) AUTO_INSTALL=true; shift ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Check and optionally install Dev-AID prerequisites."
            echo ""
            echo "Options:"
            echo "  -q, --quiet     Exit 0/1 only (for scripts)"
            echo "  --install       Auto-install missing tools without prompts"
            echo "  -h, --help      Show this help message"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ============================================================================
# Helpers
# ============================================================================

log_header() {
    if ! $QUIET; then
        echo ""
        echo -e "${BOLD}$1${NC}"
        echo -e "${BLUE}$(printf '%.0s─' {1..50})${NC}"
    fi
}

check_tool() {
    local cmd="$1"
    local name="$2"
    local category="$3"         # critical | recommended | security
    local version_flag="${4:---version}"
    local min_version="${5:-}"   # optional minimum version

    if command -v "$cmd" &> /dev/null; then
        if ! $QUIET; then
            local ver=""
            ver=$($cmd $version_flag 2>&1 | head -1 | sed 's/.*version //; s/[,)].*//') || ver="installed"
            echo -e "  ${GREEN}✓${NC} ${name} (${ver})"
        fi
        return 0
    else
        if ! $QUIET; then
            echo -e "  ${RED}✗${NC} ${name} — ${RED}not found${NC}"
        fi
        case "$category" in
            critical)    MISSING_CRITICAL+=("$cmd") ;;
            recommended) MISSING_RECOMMENDED+=("$cmd") ;;
            security)    MISSING_SECURITY+=("$cmd") ;;
        esac
        return 1
    fi
}

check_python_version() {
    if ! command -v python3 &> /dev/null; then
        return 1
    fi

    local py_ver
    py_ver=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null) || return 1

    local major minor
    major=$(echo "$py_ver" | cut -d. -f1)
    minor=$(echo "$py_ver" | cut -d. -f2)

    if [[ "$major" -lt 3 ]] || { [[ "$major" -eq 3 ]] && [[ "$minor" -lt 9 ]]; }; then
        if ! $QUIET; then
            echo -e "  ${YELLOW}⚠${NC}  Python $py_ver found, but 3.9+ required"
        fi
        return 1
    fi
    return 0
}

check_python_venv() {
    if ! command -v python3 &> /dev/null; then
        return 1
    fi

    if python3 -c "import venv" &> /dev/null; then
        if ! $QUIET; then
            echo -e "  ${GREEN}✓${NC} python3 -m venv (available)"
        fi
        return 0
    else
        if ! $QUIET; then
            echo -e "  ${RED}✗${NC} python3 -m venv — ${RED}not available${NC}"
            echo -e "      Install: ${YELLOW}apt install python3-venv${NC} (Debian/Ubuntu)"
        fi
        MISSING_CRITICAL+=("python3-venv")
        return 1
    fi
}

# Detect package manager
detect_pkg_manager() {
    if command -v brew &> /dev/null; then
        echo "brew"
    elif command -v apt-get &> /dev/null; then
        echo "apt"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    else
        echo "none"
    fi
}

install_tool() {
    local cmd="$1"
    local pkg_mgr
    pkg_mgr=$(detect_pkg_manager)

    case "$pkg_mgr" in
        brew)
            case "$cmd" in
                python3)     brew install python@3.12 ;;
                git)         brew install git ;;
                curl)        brew install curl ;;
                jq)          brew install jq ;;
                gh)          brew install gh ;;
                shellcheck)  brew install shellcheck ;;
                gitleaks)    brew install gitleaks ;;
                trivy)       brew install trivy ;;
                opengrep)
                    echo "Installing Opengrep via official script..."
                    curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash
                    ;;
                *) echo "  No brew formula known for: $cmd"; return 1 ;;
            esac
            ;;
        apt)
            case "$cmd" in
                python3)      sudo apt-get install -y python3 python3-pip ;;
                python3-venv) sudo apt-get install -y python3-venv ;;
                git)          sudo apt-get install -y git ;;
                curl)         sudo apt-get install -y curl ;;
                jq)           sudo apt-get install -y jq ;;
                gh)           sudo apt-get install -y gh ;;
                shellcheck)   sudo apt-get install -y shellcheck ;;
                gitleaks)
                    echo "Installing Gitleaks via binary release..."
                    curl -sL "https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_$(uname -s)_$(uname -m).tar.gz" | sudo tar xz -C /usr/local/bin/
                    ;;
                trivy)
                    echo "Installing Trivy via official script..."
                    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sudo sh -s -- -b /usr/local/bin
                    ;;
                opengrep)
                    echo "Installing Opengrep via official script..."
                    curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash
                    ;;
                *) echo "  No apt package known for: $cmd"; return 1 ;;
            esac
            ;;
        dnf)
            case "$cmd" in
                python3)     sudo dnf install -y python3 python3-pip ;;
                git)         sudo dnf install -y git ;;
                curl)        sudo dnf install -y curl ;;
                jq)          sudo dnf install -y jq ;;
                shellcheck)  sudo dnf install -y ShellCheck ;;
                *) echo "  No dnf package known for: $cmd"; return 1 ;;
            esac
            ;;
        *)
            echo -e "  ${RED}No supported package manager found.${NC}"
            echo "  Please install $cmd manually."
            return 1
            ;;
    esac
}

# ============================================================================
# Checks
# ============================================================================

if ! $QUIET; then
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║      Dev-AID Prerequisite Check                ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
fi

# --- Critical tools (Dev-AID won't work without these) ---
log_header "Critical Prerequisites"

check_tool "git"     "Git"        critical "--version"
check_tool "python3" "Python 3"   critical "--version"
check_python_version
check_python_venv
check_tool "curl"    "curl"       critical "--version"
check_tool "bash"    "Bash"       critical "--version"

# --- Recommended tools (degraded experience without these) ---
log_header "Recommended Tools"

check_tool "jq"         "jq (JSON processor)"    recommended "--version"
check_tool "gh"         "GitHub CLI"             recommended "--version"
check_tool "shellcheck" "ShellCheck"             recommended "--version"

# --- Security tools (for security scanning features) ---
log_header "Security Scanning Tools"

check_tool "gitleaks" "Gitleaks (secret detection)"       security "version"
check_tool "trivy"    "Trivy (vulnerability scanner)"     security "--version"
check_tool "opengrep" "Opengrep (SAST)"                   security "--version"

# ============================================================================
# Summary & Installation
# ============================================================================

if ! $QUIET; then
    echo ""
    echo -e "${BLUE}$(printf '%.0s═' {1..50})${NC}"

    TOTAL_MISSING=$(( ${#MISSING_CRITICAL[@]} + ${#MISSING_RECOMMENDED[@]} + ${#MISSING_SECURITY[@]} ))

    if [[ $TOTAL_MISSING -eq 0 ]]; then
        echo -e "${GREEN}All prerequisites satisfied!${NC}"
        echo ""
        exit 0
    fi

    echo -e "${BOLD}Missing Tools Summary:${NC}"
    echo ""

    if [[ ${#MISSING_CRITICAL[@]} -gt 0 ]]; then
        echo -e "  ${RED}Critical (required):${NC}    ${MISSING_CRITICAL[*]}"
    fi
    if [[ ${#MISSING_RECOMMENDED[@]} -gt 0 ]]; then
        echo -e "  ${YELLOW}Recommended:${NC}            ${MISSING_RECOMMENDED[*]}"
    fi
    if [[ ${#MISSING_SECURITY[@]} -gt 0 ]]; then
        echo -e "  ${YELLOW}Security tools:${NC}         ${MISSING_SECURITY[*]}"
    fi
    echo ""
fi

# Determine what to install
ALL_MISSING=("${MISSING_CRITICAL[@]}" "${MISSING_RECOMMENDED[@]}" "${MISSING_SECURITY[@]}")

if [[ ${#ALL_MISSING[@]} -eq 0 ]]; then
    exit 0
fi

# Critical tools missing = hard stop unless we can install them
if [[ ${#MISSING_CRITICAL[@]} -gt 0 ]]; then
    if $AUTO_INSTALL; then
        echo -e "${BLUE}Auto-installing critical tools...${NC}"
        for tool in "${MISSING_CRITICAL[@]}"; do
            echo ""
            echo -e "${BLUE}→ Installing $tool...${NC}"
            if install_tool "$tool"; then
                echo -e "${GREEN}✓ $tool installed${NC}"
            else
                echo -e "${RED}✗ Failed to install $tool${NC}"
                echo -e "${RED}Dev-AID cannot proceed without critical prerequisites.${NC}"
                exit 1
            fi
        done
    elif ! $QUIET; then
        PKG_MGR=$(detect_pkg_manager)

        echo -e "${RED}Critical tools are missing. Dev-AID requires these to function.${NC}"
        echo ""

        if [[ "$PKG_MGR" != "none" ]]; then
            read -p "Install missing critical tools now? (Y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
                for tool in "${MISSING_CRITICAL[@]}"; do
                    echo ""
                    echo -e "${BLUE}→ Installing $tool...${NC}"
                    if install_tool "$tool"; then
                        echo -e "${GREEN}✓ $tool installed${NC}"
                    else
                        echo -e "${RED}✗ Failed to install $tool${NC}"
                    fi
                done
            else
                echo -e "${YELLOW}Please install the missing tools manually and re-run.${NC}"
                exit 1
            fi
        else
            echo -e "${YELLOW}No supported package manager found. Please install manually:${NC}"
            for tool in "${MISSING_CRITICAL[@]}"; do
                echo "  - $tool"
            done
            exit 1
        fi
    else
        exit 1
    fi
fi

# Recommended + Security tools
OPTIONAL_MISSING=("${MISSING_RECOMMENDED[@]}" "${MISSING_SECURITY[@]}")

if [[ ${#OPTIONAL_MISSING[@]} -gt 0 ]]; then
    if $AUTO_INSTALL; then
        echo ""
        echo -e "${BLUE}Auto-installing recommended and security tools...${NC}"
        for tool in "${OPTIONAL_MISSING[@]}"; do
            echo ""
            echo -e "${BLUE}→ Installing $tool...${NC}"
            if install_tool "$tool"; then
                echo -e "${GREEN}✓ $tool installed${NC}"
            else
                echo -e "${YELLOW}⚠ Could not install $tool (non-critical, continuing)${NC}"
            fi
        done
    elif ! $QUIET; then
        PKG_MGR=$(detect_pkg_manager)
        if [[ "$PKG_MGR" != "none" ]]; then
            echo ""
            read -p "Install missing recommended/security tools? (Y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
                for tool in "${OPTIONAL_MISSING[@]}"; do
                    echo ""
                    echo -e "${BLUE}→ Installing $tool...${NC}"
                    if install_tool "$tool"; then
                        echo -e "${GREEN}✓ $tool installed${NC}"
                    else
                        echo -e "${YELLOW}⚠ Could not install $tool (skipping)${NC}"
                    fi
                done
            else
                echo -e "${BLUE}→ Skipped optional tools. You can install later with:${NC}"
                echo "    ./.dev-aid/scripts/check-prerequisites.sh --install"
            fi
        fi
    fi
fi

if ! $QUIET; then
    echo ""
    echo -e "${GREEN}Prerequisite check complete.${NC}"
    echo ""
fi
