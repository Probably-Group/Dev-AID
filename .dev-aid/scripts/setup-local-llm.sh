#!/usr/bin/env bash
#
# Dev-AID Local LLM Setup Wizard
#
# Interactive setup for local LLM inference with:
# - Hardware auto-detection
# - Backend selection (Ollama, LM Studio, llama.cpp)
# - Model recommendations
# - Automatic model download
# - Configuration update
#
# Usage: ./setup-local-llm.sh
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_DIR="$PROJECT_ROOT/.dev-aid/config"

# Print colored message
print_color() {
    local color="$1"
    shift
    echo -e "${color}$*${NC}"
}

print_header() {
    echo ""
    print_color "$CYAN" "======================================"
    print_color "$CYAN" "$1"
    print_color "$CYAN" "======================================"
    echo ""
}

print_success() {
    print_color "$GREEN" "✓ $1"
}

print_warning() {
    print_color "$YELLOW" "⚠ $1"
}

print_error() {
    print_color "$RED" "✗ $1"
}

print_info() {
    print_color "$BLUE" "ℹ $1"
}

# Check if Python is available
check_python() {
    if command -v python3 &>/dev/null; then
        PYTHON="python3"
    elif command -v python &>/dev/null; then
        PYTHON="python"
    else
        print_error "Python not found. Please install Python 3.8+"
        exit 1
    fi
    print_success "Found Python: $($PYTHON --version)"
}

# Detect hardware
detect_hardware() {
    print_header "Hardware Detection"

    print_info "Detecting your hardware..."
    echo ""

    # Use Python hardware detector
    HARDWARE_INFO=$($PYTHON -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/.dev-aid/orchestration')
try:
    from router.hardware_detector import detect_hardware
    hw = detect_hardware()
    print(f'CPU: {hw.cpu_name}')
    print(f'RAM: {hw.ram_gb} GB')
    print(f'GPU: {hw.gpu.name if hw.gpu else \"None\"}')
    print(f'VRAM: {hw.available_vram_gb} GB')
    print(f'TIER: {hw.recommended_tier}')
except Exception as e:
    print(f'ERROR: {e}')
" 2>/dev/null || echo "DETECTION_FAILED")

    if [[ "$HARDWARE_INFO" == "DETECTION_FAILED" ]] || [[ "$HARDWARE_INFO" == ERROR:* ]]; then
        print_warning "Automatic hardware detection failed."
        echo ""
        read -p "Enter your GPU VRAM in GB (0 for CPU-only): " MANUAL_VRAM
        read -p "Enter your system RAM in GB: " MANUAL_RAM

        VRAM_GB="${MANUAL_VRAM:-0}"
        RAM_GB="${MANUAL_RAM:-16}"

        if (( $(echo "$VRAM_GB >= 80" | bc -l) )); then
            HW_TIER="enterprise"
        elif (( $(echo "$VRAM_GB >= 48" | bc -l) )); then
            HW_TIER="pro"
        elif (( $(echo "$VRAM_GB >= 20" | bc -l) )); then
            HW_TIER="high"
        elif (( $(echo "$VRAM_GB >= 14" | bc -l) )); then
            HW_TIER="mid"
        elif (( $(echo "$VRAM_GB >= 3" | bc -l) )); then
            HW_TIER="entry"
        else
            HW_TIER="cpu_only"
        fi
    else
        echo "$HARDWARE_INFO"
        echo ""

        # Parse tier from output
        HW_TIER=$(echo "$HARDWARE_INFO" | grep "TIER:" | cut -d: -f2 | tr -d ' ')
        VRAM_GB=$(echo "$HARDWARE_INFO" | grep "VRAM:" | cut -d: -f2 | tr -d ' GB')
    fi

    print_info "Detected tier: $HW_TIER"
}

# Select backend
select_backend() {
    print_header "Backend Selection"

    echo "Choose your local LLM backend:"
    echo ""
    echo "  1) Ollama (Recommended) - Easy to use, great model library"
    echo "  2) LM Studio - GUI app with model browser"
    echo "  3) llama.cpp - Lightweight, manual model management"
    echo ""

    while true; do
        read -p "Select backend [1-3, default=1]: " BACKEND_CHOICE
        BACKEND_CHOICE="${BACKEND_CHOICE:-1}"

        case "$BACKEND_CHOICE" in
            1)
                BACKEND="ollama"
                BACKEND_PORT=11434
                break
                ;;
            2)
                BACKEND="lm_studio"
                BACKEND_PORT=1234
                break
                ;;
            3)
                BACKEND="llama_cpp"
                BACKEND_PORT=8080
                break
                ;;
            *)
                print_error "Invalid selection. Please choose 1, 2, or 3."
                ;;
        esac
    done

    print_success "Selected: $BACKEND"
}

# Check if backend is installed
check_backend() {
    print_header "Backend Check"

    case "$BACKEND" in
        ollama)
            if command -v ollama &>/dev/null; then
                print_success "Ollama is installed"
                OLLAMA_VERSION=$(ollama --version 2>/dev/null || echo "unknown")
                print_info "Version: $OLLAMA_VERSION"
            else
                print_warning "Ollama is not installed"
                echo ""
                echo "Install Ollama:"
                echo "  macOS/Linux: curl -fsSL https://ollama.ai/install.sh | sh"
                echo "  Windows: Download from https://ollama.ai/download"
                echo ""
                read -p "Press Enter after installing Ollama, or 'q' to quit: " INSTALL_RESP
                if [[ "$INSTALL_RESP" == "q" ]]; then
                    exit 0
                fi
            fi
            ;;
        lm_studio)
            print_info "LM Studio is a GUI application"
            echo "Download from: https://lmstudio.ai/"
            echo ""
            read -p "Is LM Studio installed and running? [y/N]: " LMS_RUNNING
            if [[ "$LMS_RUNNING" != "y" && "$LMS_RUNNING" != "Y" ]]; then
                print_error "Please install and start LM Studio before continuing"
                exit 1
            fi
            ;;
        llama_cpp)
            if command -v llama-server &>/dev/null || command -v server &>/dev/null; then
                print_success "llama.cpp server found"
            else
                print_warning "llama.cpp server not found in PATH"
                echo "Build from source: https://github.com/ggerganov/llama.cpp"
                echo ""
            fi
            ;;
    esac
}

# Get model recommendations
get_recommendations() {
    print_header "Model Recommendations"

    print_info "Based on your hardware ($HW_TIER tier):"
    echo ""

    # Model recommendations by tier
    case "$HW_TIER" in
        enterprise)
            echo "  ★ kimi-k2-thinking (Score: 83, 80GB VRAM)"
            echo "    Best-in-class reasoning and code generation"
            echo ""
            echo "  ○ glm-4.7-thinking (Score: 74, 48GB VRAM)"
            echo "    Excellent reasoning with lower requirements"
            echo ""
            echo "  ○ qwen2.5-coder-32b (Score: 68, 20GB VRAM)"
            echo "    Best value for code-focused tasks"
            RECOMMENDED_MODEL="kimi-k2"
            ;;
        pro)
            echo "  ★ glm-4.7-thinking (Score: 74, 48GB VRAM)"
            echo "    Excellent reasoning and long context"
            echo ""
            echo "  ○ qwen2.5-coder-32b (Score: 68, 20GB VRAM)"
            echo "    Best value for code-focused tasks"
            RECOMMENDED_MODEL="glm4:9b"
            ;;
        high)
            echo "  ★ qwen2.5-coder-32b (Score: 68, 20GB VRAM)"
            echo "    Best 'bang for buck' - excellent for coding"
            echo ""
            echo "  ○ codestral-22b (Score: 72, 14GB VRAM)"
            echo "    Great mid-tier option"
            RECOMMENDED_MODEL="qwen2.5-coder:32b"
            ;;
        mid)
            echo "  ★ codestral-22b (Score: 72, 14GB VRAM)"
            echo "    Strong coding performance at mid-tier"
            echo ""
            echo "  ○ phi-4-mini (Score: 58, 3GB VRAM)"
            echo "    Faster for quick iterations"
            RECOMMENDED_MODEL="codestral:22b"
            ;;
        entry)
            echo "  ★ phi-4-mini (Score: 58, 3GB VRAM)"
            echo "    Best for entry-level hardware"
            RECOMMENDED_MODEL="phi4-mini"
            ;;
        cpu_only)
            echo "  ★ phi-4-mini (Score: 58)"
            echo "    Smallest model, runs on CPU (will be slow)"
            print_warning "CPU-only mode will be significantly slower"
            RECOMMENDED_MODEL="phi4-mini"
            ;;
    esac

    echo ""
}

# Download/pull model
download_model() {
    print_header "Model Download"

    echo "Recommended model: $RECOMMENDED_MODEL"
    echo ""
    read -p "Download this model? [Y/n]: " DOWNLOAD_CHOICE

    if [[ "$DOWNLOAD_CHOICE" == "n" || "$DOWNLOAD_CHOICE" == "N" ]]; then
        read -p "Enter custom model name: " CUSTOM_MODEL
        SELECTED_MODEL="${CUSTOM_MODEL:-$RECOMMENDED_MODEL}"
    else
        SELECTED_MODEL="$RECOMMENDED_MODEL"
    fi

    case "$BACKEND" in
        ollama)
            print_info "Downloading $SELECTED_MODEL via Ollama..."
            echo ""

            # Start ollama if not running
            if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
                print_info "Starting Ollama server..."
                ollama serve &>/dev/null &
                sleep 3
            fi

            ollama pull "$SELECTED_MODEL"

            if [[ $? -eq 0 ]]; then
                print_success "Model downloaded successfully!"
            else
                print_error "Failed to download model"
                exit 1
            fi
            ;;
        lm_studio)
            print_info "Please download $SELECTED_MODEL in LM Studio's model browser"
            echo "Search for: $SELECTED_MODEL"
            read -p "Press Enter when the model is downloaded..."
            ;;
        llama_cpp)
            print_info "For llama.cpp, download the GGUF model manually:"
            echo "  https://huggingface.co/models?search=$SELECTED_MODEL+gguf"
            echo ""
            read -p "Enter path to downloaded .gguf file: " GGUF_PATH
            if [[ ! -f "$GGUF_PATH" ]]; then
                print_error "File not found: $GGUF_PATH"
                exit 1
            fi
            print_success "Model file found"
            ;;
    esac
}

# Update configuration
update_config() {
    print_header "Configuration Update"

    # Update .env file
    ENV_FILE="$CONFIG_DIR/.env"

    if [[ ! -f "$ENV_FILE" ]]; then
        cp "$CONFIG_DIR/.env.example" "$ENV_FILE" 2>/dev/null || true
    fi

    # Add or update local LLM settings
    if [[ -f "$ENV_FILE" ]]; then
        # Remove existing local settings
        grep -v "^LOCAL_" "$ENV_FILE" > "$ENV_FILE.tmp" || true
        mv "$ENV_FILE.tmp" "$ENV_FILE"

        # Add new settings
        cat >> "$ENV_FILE" << EOF

# Local LLM Settings (added by setup-local-llm.sh)
LOCAL_INFERENCE_BACKEND=$BACKEND
LOCAL_DEFAULT_MODEL=$SELECTED_MODEL
EOF

        print_success "Updated $ENV_FILE"
    fi

    print_info "Configuration complete!"
}

# Verify setup
verify_setup() {
    print_header "Verification"

    print_info "Testing local LLM connection..."
    echo ""

    # Use Python to verify
    VERIFY_RESULT=$($PYTHON -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/.dev-aid/orchestration')
try:
    from router.local_client import detect_local_server, create_local_auth, LocalLLMClient
    from router.api_clients import Message

    server = detect_local_server()
    if not server:
        print('ERROR: No local server detected')
        sys.exit(1)

    print(f'Server: {server[\"backend\"]} at {server[\"base_url\"]}')

    auth = create_local_auth(server['backend'], server['base_url'])
    client = LocalLLMClient(auth, {'provider': 'local'})

    if client.verify_connection():
        print('Connection: OK')

        models = client.list_models()
        if models:
            print(f'Available models: {len(models)}')

            # Quick test
            response = client.send_request(
                messages=[Message(role='user', content='Say hello')],
                model=models[0],
                max_tokens=20
            )
            print(f'Test response: {response.content[:50]}...')
            print('Status: SUCCESS')
        else:
            print('WARNING: No models found')
    else:
        print('ERROR: Connection failed')
        sys.exit(1)

except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
" 2>&1)

    echo "$VERIFY_RESULT"
    echo ""

    if echo "$VERIFY_RESULT" | grep -q "SUCCESS"; then
        print_success "Local LLM setup complete!"
    elif echo "$VERIFY_RESULT" | grep -q "WARNING"; then
        print_warning "Setup complete but some issues detected"
    else
        print_error "Setup verification failed"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Ensure $BACKEND is running"
        echo "  2. Check if model $SELECTED_MODEL is downloaded"
        echo "  3. Try: curl http://localhost:$BACKEND_PORT/api/tags"
    fi
}

# Main setup flow
main() {
    print_header "Dev-AID Local LLM Setup"

    echo "This wizard will help you set up local LLM inference for Dev-AID."
    echo "You'll be able to run AI models offline, privately, at zero cost!"
    echo ""

    # Check Python
    check_python

    # Install psutil if needed
    print_info "Checking Python dependencies..."
    $PYTHON -c "import psutil" 2>/dev/null || {
        print_info "Installing psutil for hardware detection..."
        $PYTHON -m pip install psutil -q
    }

    # Run setup steps
    detect_hardware
    select_backend
    check_backend
    get_recommendations
    download_model
    update_config
    verify_setup

    print_header "Setup Complete!"

    echo "Next steps:"
    echo "  1. Enable local provider in .dev-aid/config/models.json"
    echo "     Set \"enabled\": true under \"local\""
    echo ""
    echo "  2. Use Dev-AID with local models!"
    echo ""
    echo "Documentation: .dev-aid/docs/LOCAL-LLM-GUIDE.md"
}

# Run main
main "$@"
