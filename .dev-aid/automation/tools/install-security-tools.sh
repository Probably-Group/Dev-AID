#!/bin/bash
# Dev-AID Security Tools Installer
# Installs all security scanning tools for automated workflows

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${HOME}/.dev-aid/bin"
mkdir -p "$INSTALL_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect OS and architecture
detect_platform() {
    OS="$(uname -s)"
    ARCH="$(uname -m)"

    case "$OS" in
        Linux*)   OS_TYPE="linux" ;;
        Darwin*)  OS_TYPE="darwin" ;;
        *)        log_error "Unsupported OS: $OS"; exit 1 ;;
    esac

    case "$ARCH" in
        x86_64)  ARCH_TYPE="amd64" ;;
        aarch64|arm64) ARCH_TYPE="arm64" ;;
        *)       log_error "Unsupported architecture: $ARCH"; exit 1 ;;
    esac

    log_info "Detected platform: $OS_TYPE/$ARCH_TYPE"
}

# Check if tool is already installed
is_installed() {
    command -v "$1" &> /dev/null
}

# Install Opengrep
install_opengrep() {
    log_info "Installing Opengrep..."

    if is_installed opengrep; then
        log_warning "Opengrep already installed, checking version..."
        opengrep --version || true
        return 0
    fi

    # Install via official script
    if command -v curl &> /dev/null; then
        curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash
        log_success "Opengrep installed successfully"
    else
        log_error "curl not found. Please install curl first."
        return 1
    fi
}

# Install Gitleaks
install_gitleaks() {
    log_info "Installing Gitleaks..."

    if is_installed gitleaks; then
        log_warning "Gitleaks already installed: $(gitleaks version)"
        return 0
    fi

    VERSION="8.18.4"  # Latest stable as of 2025
    BINARY_URL="https://github.com/gitleaks/gitleaks/releases/download/v${VERSION}/gitleaks_${VERSION}_${OS_TYPE}_${ARCH_TYPE}.tar.gz"

    TMP_DIR=$(mktemp -d)
    cd "$TMP_DIR"

    log_info "Downloading Gitleaks v${VERSION}..."
    curl -sL "$BINARY_URL" | tar xz

    chmod +x gitleaks
    mv gitleaks "$INSTALL_DIR/"

    cd - > /dev/null
    rm -rf "$TMP_DIR"

    log_success "Gitleaks v${VERSION} installed to $INSTALL_DIR/gitleaks"
}

# Install Trivy
install_trivy() {
    log_info "Installing Trivy..."

    if is_installed trivy; then
        log_warning "Trivy already installed: $(trivy --version | head -1)"
        return 0
    fi

    # Install via official script
    if command -v curl &> /dev/null; then
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b "$INSTALL_DIR"
        log_success "Trivy installed successfully"
    else
        log_error "curl not found. Please install curl first."
        return 1
    fi
}

# Update Trivy database
update_trivy_db() {
    log_info "Updating Trivy vulnerability database..."
    if is_installed trivy; then
        trivy image --download-db-only 2>/dev/null || true
        log_success "Trivy database updated"
    fi
}

# Update PATH
update_path() {
    log_info "Updating PATH..."

    SHELL_RC=""
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    fi

    if [ -n "$SHELL_RC" ]; then
        if ! grep -q "\.dev-aid/bin" "$SHELL_RC"; then
            echo "" >> "$SHELL_RC"
            echo "# Dev-AID Security Tools" >> "$SHELL_RC"
            echo "export PATH=\"\$HOME/.dev-aid/bin:\$PATH\"" >> "$SHELL_RC"
            log_success "Added $INSTALL_DIR to PATH in $SHELL_RC"
            log_warning "Please run: source $SHELL_RC"
        else
            log_info "PATH already includes $INSTALL_DIR"
        fi
    fi

    # Add to current session
    export PATH="$INSTALL_DIR:$PATH"
}

# Verify installations
verify_tools() {
    log_info "Verifying installations..."

    TOOLS=(
        "opengrep:Opengrep:required"
        "gitleaks:Gitleaks:required"
        "trivy:Trivy:required"
    )

    SUCCESS_COUNT=0
    FAIL_COUNT=0

    for tool_info in "${TOOLS[@]}"; do
        IFS=':' read -r cmd name type <<< "$tool_info"

        if is_installed "$cmd"; then
            log_success "✓ $name installed"
            ((SUCCESS_COUNT++))
        else
            if [ "$type" = "required" ]; then
                log_error "✗ $name NOT installed (required)"
                ((FAIL_COUNT++))
            else
                log_warning "✗ $name NOT installed (optional)"
            fi
        fi
    done

    echo ""
    log_info "Summary: $SUCCESS_COUNT tools installed, $FAIL_COUNT required tools missing"

    if [ $FAIL_COUNT -gt 0 ]; then
        return 1
    fi

    return 0
}

# Main installation flow
main() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Dev-AID Security Tools Installer"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    detect_platform
    echo ""

    log_info "Starting installation to: $INSTALL_DIR"
    echo ""

    # Install tools
    install_opengrep
    echo ""

    install_gitleaks
    echo ""

    install_trivy
    echo ""

    update_trivy_db
    echo ""

    update_path
    echo ""

    # Verify
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    verify_tools
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    log_success "Installation complete!"
    echo ""
    log_info "Next steps:"
    echo "  1. Run: source ~/.bashrc  (or ~/.zshrc)"
    echo "  2. Install git hooks: ./.dev-aid/automation/git-hooks/install.sh"
    echo "  3. Read docs: ./.dev-aid/docs/AUTOMATION-GUIDE.md"
    echo ""
}

# Run main
main "$@"
