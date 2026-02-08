#!/usr/bin/env bash
# Dev-AID Git Hooks Installer
# Installs pre-commit and pre-push hooks for automated security checks

set -euo pipefail

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly GIT_HOOKS_DIR="$(git rev-parse --git-path hooks 2>/dev/null || echo ".git/hooks")"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Cleanup handler
cleanup() {
    local exit_code=$?
    # No resources to clean up, but trap is good practice
    exit "$exit_code"
}

trap cleanup EXIT INT TERM

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Dev-AID Git Hooks Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if in git repo
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Not in a git repository!"
    exit 1
fi

log_info "Installing to: $GIT_HOOKS_DIR"
echo ""

# Backup existing hooks
backup_hook() {
    local hook_name="$1"
    local hook_path="$GIT_HOOKS_DIR/$hook_name"

    if [[ -f "$hook_path" ]] && [[ ! -L "$hook_path" ]]; then
        log_warning "Backing up existing $hook_name hook..."
        mv "$hook_path" "$hook_path.backup-$(date +%Y%m%d-%H%M%S)"
    fi
}

# Install hook
install_hook() {
    local hook_name="$1"
    local source_hook="$SCRIPT_DIR/$hook_name"
    local target_hook="$GIT_HOOKS_DIR/$hook_name"

    if [[ ! -f "$source_hook" ]]; then
        log_error "Source hook not found: $source_hook"
        return 1
    fi

    backup_hook "$hook_name"

    # Create symlink
    ln -sf "$source_hook" "$target_hook"
    chmod +x "$target_hook"

    log_success "✓ Installed $hook_name hook"
}

# Install hooks
log_info "Installing hooks..."
install_hook "pre-commit"
install_hook "pre-push"
echo ""

# Verify
log_info "Verifying installation..."
if [[ -x "$GIT_HOOKS_DIR/pre-commit" ]] && [[ -x "$GIT_HOOKS_DIR/pre-push" ]]; then
    log_success "✓ Git hooks installed successfully!"
else
    log_error "✗ Hook installation failed"
    exit 1
fi
echo ""

# Check if tools are installed
log_info "Checking security tools..."
TOOLS_MISSING=0

check_tool() {
    local cmd="$1"
    local name="$2"
    local type="${3:-required}"

    if command -v "$cmd" &> /dev/null; then
        log_success "✓ $name installed"
    else
        if [[ "$type" == "optional" ]]; then
            log_warning "○ $name not installed (optional)"
        else
            log_warning "✗ $name NOT installed"
            TOOLS_MISSING=$((TOOLS_MISSING + 1))
        fi
    fi
}

log_info "Required tools:"
check_tool "gitleaks" "Gitleaks"
check_tool "trivy" "Trivy"
check_tool "opengrep" "Opengrep"
echo ""

log_info "Language-specific tools (optional):"
check_tool "shellcheck" "ShellCheck (Shell SAST)" "optional"
check_tool "bandit" "Bandit (Python SAST)" "optional"
check_tool "pip-audit" "pip-audit (Python deps)" "optional"
check_tool "flawfinder" "Flawfinder (C/C++ SAST)" "optional"
check_tool "mobsfscan" "mobsfscan (Swift SAST)" "optional"
check_tool "cargo-audit" "cargo-audit (Rust deps)" "optional"
check_tool "govulncheck" "govulncheck (Go vulns)" "optional"
echo ""

if [[ $TOOLS_MISSING -gt 0 ]]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_warning "$TOOLS_MISSING required tool(s) missing!"
    echo ""
    log_info "Install security tools:"
    echo "  ./.dev-aid/automation/tools/install-security-tools.sh"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_success "All required tools installed! Hooks are ready to use."
    log_info "Optional language-specific tools enhance scanning coverage."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi
echo ""

log_info "Hook behavior:"
echo "  • pre-commit: Fast checks (~10s) - secrets, critical issues"
echo "  • pre-push: Thorough checks (~60s) - full security scan"
echo ""
log_info "To bypass hooks: git commit --no-verify"
echo ""
