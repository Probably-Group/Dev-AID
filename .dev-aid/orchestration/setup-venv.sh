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
            # NOTE: Use plain `realpath` (no -m) for macOS BSD compatibility.
            # The directory exists at this point (verified by the -d check above).
            local resolved_venv
            resolved_venv="$(realpath "$VENV_DIR")"
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

    # ------------------------------------------------------------------
    # Reassure the user about isolation BEFORE pip starts spamming output.
    # Beta testers seeing "Collecting anthropic, Collecting google-genai,
    # Collecting openai, ..." for 100+ packages have legitimately
    # complained that it looks like Dev-AID is installing AI SDKs into
    # their system Python. It's NOT — everything goes into the venv at
    # $VENV_DIR — but the wall of pip output makes that easy to miss.
    # ------------------------------------------------------------------
    # Compute a short, relative-looking venv path for display so the
    # banner doesn't overflow on terminals with long absolute paths.
    local _short_venv
    _short_venv=".dev-aid/orchestration/.venv"

    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔒  ISOLATION NOTICE${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "  All Python packages will be installed into an ${GREEN}isolated virtual env${NC}:"
    echo "    ${_short_venv}"
    echo ""
    echo -e "  Your system Python and any other projects on this machine are"
    echo -e "  ${GREEN}NOT touched${NC}. To completely uninstall everything below later, run:"
    echo "    rm -rf ${_short_venv}"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    unset _short_venv

    # Count what we're about to install for a clearer "X packages" message.
    local total_pinned
    total_pinned=$(grep -cE '^[a-zA-Z]' "$REQUIREMENTS" 2>/dev/null || echo "?")

    print_info "Upgrading pip (silent)..."
    pip install --upgrade pip > /dev/null 2>&1 || true

    # Log directory for the verbose pip output. Users can inspect this
    # if anything goes wrong, and we dump it on failure.
    local log_dir="${VENV_DIR%/.venv}/logs"
    mkdir -p "$log_dir" 2>/dev/null || true
    local pip_log="$log_dir/pip-install-$(date +%Y%m%d-%H%M%S).log"

    print_info "Installing ${total_pinned} pinned packages into the venv (this takes ~30–90s)..."
    print_info "Verbose log: ${pip_log}"
    echo ""

    # CRITICAL: capture pip's exit code so we don't falsely report success
    # when wheels failed to build (e.g., pydantic-core against a Python
    # version newer than the pyo3 binding supports).
    #
    # Use --quiet to suppress the "Collecting / Using cached / Downloading"
    # spam. pip still prints one line per warning + the final
    # "Successfully installed ..." summary, which is enough signal.
    # Full output goes to the log so we can dump it on failure.
    if pip install --quiet --progress-bar=on -r "$REQUIREMENTS" 2>&1 | tee "$pip_log"; then
        echo ""
        print_success "All ${total_pinned} packages installed into venv"
        print_success "Venv lives at: ${VENV_DIR}"
        print_success "Total venv size: $(du -sh "$VENV_DIR" 2>/dev/null | cut -f1 || echo unknown)"
    else
        local pip_exit=${PIPESTATUS[0]:-1}
        echo ""
        print_error "pip install failed (exit code $pip_exit)"
        print_error ""
        print_error "Common causes:"
        print_error "  - Python version too new for one or more pinned dependencies"
        print_error "    (e.g., pydantic-core requires pyo3 wheels for your Python version)"
        print_error "  - Network issue downloading wheels"
        print_error "  - Disk full or permission denied"
        print_error ""
        print_error "Last 30 lines of pip log (full log: $pip_log):"
        echo ""
        tail -30 "$pip_log" 2>/dev/null | sed 's/^/  /' || true
        echo ""
        print_error "Setup will continue but the orchestration router will not work"
        print_error "until you resolve the install failure above."
        deactivate
        return 1
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

    # Test the critical packages — the ones the router actually needs to
    # function. We don't test every transitive dep (too noisy and not
    # informative) and we don't test dev-only tools like pytest/mypy/black
    # at this stage (they're verified by the test suite later).
    #
    # Map of "display name" → "import statement". This is curated, not
    # generated, so hyphenated PyPI names map cleanly to dotted module
    # imports (anthropic, google.genai, openai, pydantic, etc.).
    local -a critical_packages=(
        "anthropic|anthropic"
        "google-genai|google.genai"
        "openai|openai"
        "pydantic|pydantic"
        "httpx|httpx"
        "requests|requests"
        "rich|rich"
        "typer|typer"
        "keyring|keyring"
        "python-dotenv|dotenv"
    )

    print_info "Testing ${#critical_packages[@]} critical imports in venv..."

    local failed_imports=()
    local passed=0
    for entry in "${critical_packages[@]}"; do
        local display_name="${entry%%|*}"
        local import_name="${entry##*|}"
        if python3 -c "import ${import_name}" 2>/dev/null; then
            passed=$((passed + 1))
        else
            failed_imports+=("$display_name")
        fi
    done

    deactivate

    echo ""
    if [ ${#failed_imports[@]} -eq 0 ]; then
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}✅  Dev-AID router is ready to use${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "  All ${passed} critical packages import cleanly inside the venv."
        echo "  Dev-AID's router, agents, and slash commands will work normally."
        echo ""
        echo "  (Dev-only tools like pytest/mypy/black are not import-tested here;"
        echo "   they're verified by the orchestration test suite if/when you run it.)"
        echo ""
        return 0
    else
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}❌  Dev-AID router will NOT work — ${#failed_imports[@]} critical package(s) broken${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "  ${passed} of ${#critical_packages[@]} critical imports passed."
        echo "  ${#failed_imports[@]} failed:"
        local fp
        for fp in "${failed_imports[@]}"; do
            echo "    ✗ ${fp}"
        done
        echo ""
        echo "  ${YELLOW}What this means:${NC}"
        echo "    • The orchestration router (solo / ensemble / challenger modes) will fail."
        echo "    • The autonomous agents (/aid-pr, /aid-test, /aid-debt, etc.) will fail."
        echo "    • Slash commands that don't need the venv (/aid-help, /aid-skills) still work."
        echo "    • Skills, security hooks, and local search are not affected."
        echo ""
        echo "  ${YELLOW}How to fix:${NC}"
        echo "    1. Read the pip install log printed above (full log in"
        echo "       .dev-aid/orchestration/logs/pip-install-*.log)"
        echo "    2. The most common cause is a Python version mismatch — try"
        echo "       installing Python 3.13 via pyenv or brew and re-running setup."
        echo "    3. After fixing the root cause:"
        echo "       rm -rf .dev-aid/orchestration/.venv"
        echo "       ./.dev-aid/orchestration/setup-venv.sh"
        echo ""
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
