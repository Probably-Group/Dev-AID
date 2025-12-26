#!/usr/bin/env bash
# Setup Python Virtual Environment for Dev-AID Router
# Isolates dependencies from system Python

set -euo pipefail

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Get script directory
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly VENV_DIR="$SCRIPT_DIR/.venv"
readonly REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

# Cleanup handler
cleanup() {
    local exit_code=$?

    # Deactivate venv if active
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        deactivate 2>/dev/null || true
    fi

    exit "$exit_code"
}

trap cleanup EXIT INT TERM

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

    if [[ -d "$VENV_DIR" ]]; then
        print_warning "Virtual environment already exists at $VENV_DIR"
        read -p "Remove and recreate? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing venv..."

            # Validate path containment before rm -rf (CWE-22: Path Traversal)
            local resolved_venv
            resolved_venv="$(realpath -m "$VENV_DIR")"
            local resolved_script_dir
            resolved_script_dir="$(realpath "$SCRIPT_DIR")"

            # Ensure VENV_DIR is within SCRIPT_DIR
            if [[ "$resolved_venv" != "$resolved_script_dir"* ]]; then
                print_error "Path traversal detected! VENV_DIR is outside SCRIPT_DIR"
                echo "VENV_DIR: $resolved_venv"
                echo "SCRIPT_DIR: $resolved_script_dir"
                return 1
            fi

            # Ensure VENV_DIR ends with /.venv for extra safety
            if [[ ! "$resolved_venv" =~ \/\.venv$ ]]; then
                print_error "Safety check failed! VENV_DIR must end with /.venv"
                echo "VENV_DIR: $resolved_venv"
                return 1
            fi

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

    # Validate and activate venv
    local activate_script="$VENV_DIR/bin/activate"
    if [[ ! -f "$activate_script" ]]; then
        print_error "Activate script not found at $activate_script"
        return 1
    fi

    # shellcheck source=/dev/null
    source "$activate_script"

    print_info "Upgrading pip..."
    pip install --upgrade pip > /dev/null 2>&1

    print_info "Installing dependencies from requirements.txt..."
    echo ""

    # Install with progress
    pip install -r "$REQUIREMENTS"

    print_success "All dependencies installed"

    # Show installed packages (dynamically from requirements.txt)
    echo ""
    print_info "Installed packages:"
    # Extract main package names from requirements.txt (exclude comments and dependencies section)
    local main_packages
    main_packages=$(grep -v "^#" "$REQUIREMENTS" | grep -v "^$" | sed -n '/^# AI Provider SDKs/,/^# Dependencies of above/p' | grep -E "^[a-zA-Z]" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | head -20 | tr '\n' '|' | sed 's/|$//')
    if [[ -n "$main_packages" ]]; then
        pip list | grep -E "($main_packages)" || true
    fi

    deactivate
    return 0
}

# Test installation
test_installation() {
    print_header "Testing Installation"

    # Validate and activate venv
    local activate_script="$VENV_DIR/bin/activate"
    if [[ ! -f "$activate_script" ]]; then
        print_error "Activate script not found at $activate_script"
        return 1
    fi

    # shellcheck source=/dev/null
    source "$activate_script"

    print_info "Testing imports..."

    # Dynamically extract core packages from requirements.txt
    # Note: google-generativeai imports as 'google.generativeai', python-dotenv as 'dotenv'
    local -A import_map=(
        ["google-generativeai"]="google.generativeai"
        ["python-dotenv"]="dotenv"
    )

    # Extract main package names (exclude comments, blank lines, and dependency section)
    local packages_to_test=()
    while IFS= read -r line; do
        # Skip comments, blank lines, and dependency section
        if [[ "$line" =~ ^#.*Dependencies\ of\ above ]]; then
            break
        fi
        if [[ -n "$line" && ! "$line" =~ ^# ]]; then
            # Extract package name (before ==, >=, etc.)
            local pkg_name=$(echo "$line" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | tr -d ' ')
            if [[ -n "$pkg_name" ]]; then
                # Use import name from map, or package name as-is
                local import_name="${import_map[$pkg_name]:-$pkg_name}"
                packages_to_test+=("$import_name")
            fi
        fi
    done < "$REQUIREMENTS"

    # Test each package
    local failed=0
    for package in "${packages_to_test[@]}"; do
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
    echo -e "     ${GREEN}source .dev-aid/orchestration/.venv/bin/activate${NC}"
    echo ""
    echo "To test the router:"
    echo -e "  ${GREEN}cd .dev-aid/orchestration${NC}"
    echo -e "  ${GREEN}./router-cli.sh test${NC}"
    echo ""
    echo "To install more packages:"
    echo -e "  ${GREEN}source .dev-aid/orchestration/.venv/bin/activate${NC}"
    echo -e "  ${GREEN}pip install <package>${NC}"
    echo -e "  ${GREEN}deactivate${NC}"
    echo ""
    echo "To remove the venv:"
    echo -e "  ${GREEN}rm -rf .dev-aid/orchestration/.venv${NC}"
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
