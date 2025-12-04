#!/bin/bash
# Setup Python Virtual Environment for Dev-AID Router
# Isolates dependencies from system Python

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Python 3 is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not found"
        echo "Please install Python 3.9 or higher:"
        echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
        echo "  macOS: brew install python3"
        echo "  Windows: Download from https://www.python.org/downloads/"
        return 1
    fi

    # Check Python version
    local py_version=$(python3 --version | cut -d' ' -f2)
    local major=$(echo "$py_version" | cut -d'.' -f1)
    local minor=$(echo "$py_version" | cut -d'.' -f2)

    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 9 ]); then
        print_error "Python 3.9 or higher required (found $py_version)"
        return 1
    fi

    print_success "Python $py_version found"
    return 0
}

# Create virtual environment
create_venv() {
    print_header "Creating Virtual Environment"

    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at $VENV_DIR"
        read -p "Remove and recreate? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing venv..."
            rm -rf "$VENV_DIR"
        else
            print_info "Keeping existing venv"
            return 0
        fi
    fi

    print_info "Creating venv at $VENV_DIR"

    if ! python3 -m venv "$VENV_DIR"; then
        print_error "Failed to create virtual environment"
        echo "Try installing python3-venv:"
        echo "  Ubuntu/Debian: sudo apt install python3-venv"
        return 1
    fi

    print_success "Virtual environment created"
    return 0
}

# Install dependencies
install_dependencies() {
    print_header "Installing Dependencies"

    if [ ! -f "$REQUIREMENTS" ]; then
        print_error "requirements.txt not found at $REQUIREMENTS"
        return 1
    fi

    # Activate venv
    source "$VENV_DIR/bin/activate"

    print_info "Upgrading pip..."
    pip install --upgrade pip > /dev/null 2>&1

    print_info "Installing dependencies from requirements.txt..."
    echo ""

    # Install with progress
    pip install -r "$REQUIREMENTS"

    print_success "All dependencies installed"

    # Show installed packages
    echo ""
    print_info "Installed packages:"
    pip list | grep -E "(anthropic|google-generativeai|openai|python-dotenv|pydantic|rich|typer)" || true

    deactivate
    return 0
}

# Test installation
test_installation() {
    print_header "Testing Installation"

    # Activate venv
    source "$VENV_DIR/bin/activate"

    print_info "Testing imports..."

    # Test each package
    local packages=("anthropic" "google.generativeai" "openai" "dotenv" "pydantic" "rich" "typer")
    local failed=0

    for package in "${packages[@]}"; do
        if python3 -c "import ${package}" 2>/dev/null; then
            print_success "$package"
        else
            print_error "$package (import failed)"
            ((failed++))
        fi
    done

    deactivate

    if [ $failed -eq 0 ]; then
        print_success "All packages import successfully"
        return 0
    else
        print_error "$failed package(s) failed to import"
        return 1
    fi
}

# Show usage instructions
show_usage() {
    print_header "Setup Complete!"

    echo ""
    echo "Virtual environment created at: $VENV_DIR"
    echo ""
    echo "To use the router:"
    echo ""
    echo "  1. The venv will be automatically activated when using router-cli.sh"
    echo "  2. Or manually activate with:"
    echo "     ${GREEN}source .dev-aid/orchestration/.venv/bin/activate${NC}"
    echo ""
    echo "To test the router:"
    echo "  ${GREEN}cd .dev-aid/orchestration${NC}"
    echo "  ${GREEN}./router-cli.sh test${NC}"
    echo ""
    echo "To install more packages:"
    echo "  ${GREEN}source .dev-aid/orchestration/.venv/bin/activate${NC}"
    echo "  ${GREEN}pip install <package>${NC}"
    echo "  ${GREEN}deactivate${NC}"
    echo ""
    echo "To remove the venv:"
    echo "  ${GREEN}rm -rf .dev-aid/orchestration/.venv${NC}"
    echo ""
}

# Main execution
main() {
    print_header "Dev-AID Router - Virtual Environment Setup"
    echo ""
    echo "This script will:"
    echo "  1. Check Python version (3.9+ required)"
    echo "  2. Create isolated virtual environment"
    echo "  3. Install all router dependencies"
    echo "  4. Test the installation"
    echo ""
    print_warning "Dependencies will be installed in a virtual environment"
    print_warning "Your system Python will NOT be affected"
    echo ""
    read -p "Continue? [Y/n]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "Setup cancelled"
        exit 0
    fi

    echo ""

    # Check Python
    if ! check_python; then
        exit 1
    fi

    echo ""

    # Create venv
    if ! create_venv; then
        exit 1
    fi

    echo ""

    # Install dependencies
    if ! install_dependencies; then
        exit 1
    fi

    echo ""

    # Test installation
    if ! test_installation; then
        print_warning "Some packages failed to import, but setup is complete"
        print_info "You can still try using the router"
    fi

    echo ""

    # Show usage
    show_usage
}

# Run
main "$@"
