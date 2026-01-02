#!/usr/bin/env bash

# Dev-AID Interactive Installer v2.0
# Configures Dev-AID with granular model selection and flexible orchestration

set -euo pipefail

# Source shared security library
readonly INSTALL_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LIB_DIR="${INSTALL_SCRIPT_DIR}/../lib"

# shellcheck source=/dev/null
if [[ -f "${LIB_DIR}/bash-common.sh" ]]; then
    source "${LIB_DIR}/bash-common.sh"
fi

# Temp files tracking for cleanup
declare -a TEMP_FILES=()

# Cleanup handler
cleanup() {
    local exit_code=$?

    # Clean up temp files securely
    for temp_file in "${TEMP_FILES[@]}"; do
        if [[ -f "$temp_file" ]]; then
            if command -v shred >/dev/null 2>&1; then
                shred -u "$temp_file" 2>/dev/null || rm -f "$temp_file"
            else
                rm -f "$temp_file"
            fi
        fi
    done

    exit "$exit_code"
}

trap cleanup EXIT INT TERM

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly MAGENTA='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Configuration variables
PROJECT_ROOT=""
DEV_AID_DIR=""
STANDING_CONTEXT_BUDGET=""
AUTO_ACTIVATION=""
ORCHESTRATION_MODE=""
ENABLED_PROVIDERS=()
COLLECTED_API_KEYS=()
SECURITY_TOOLS_INSTALLED=false
SECURITY_HOOKS_INSTALLED=false

# Model assignments for different task types
declare -A TASK_MODEL_MAPPING

# Print colored message
print_color() {
    local color="$1"
    shift
    echo -e "${color}$*${NC}"
}

# Print section header
print_header() {
    echo ""
    print_color "$CYAN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_color "$CYAN" "$1"
    print_color "$CYAN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Welcome message
show_welcome() {
    clear
    print_color "$MAGENTA" "
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║       🚀 Dev-AID (Development AI Driver) Installer 🚀         ║
║                                                                ║
║     Multi-Model AI Orchestration for Elite Development        ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"
    print_color "$YELLOW" "Welcome to Dev-AID setup!"
    echo ""
    echo "This installer will configure AI-powered development assistance"
    echo "for your project with support for multiple AI models."
    echo ""
    print_color "$CYAN" "You'll choose:"
    echo "  • Which AI providers to use"
    echo "  • Which models for which tasks"
    echo "  • How models work together (or independently)"
    echo "  • Your token budget and preferences"
    echo ""
    print_color "$YELLOW" "💡 Tip: You can reconfigure anytime with .dev-aid/scripts/reconfigure.sh"
    echo ""
    read -p "Press Enter to begin setup..."
}

# Question 1: Standing Context Budget
ask_context_budget() {
    print_header "Step 1/6: Standing Context Budget"

    echo "How much token budget for standing context?"
    echo ""
    print_color "$GREEN" "A. Minimal (~500 tokens)"
    echo "   • Fastest startup (<1s)"
    echo "   • Only essential auto-loads"
    echo "   • Best for: Quick tasks, small projects"
    echo ""
    print_color "$YELLOW" "B. Balanced (~1,000 tokens) [RECOMMENDED]"
    echo "   • Fast startup (~2s)"
    echo "   • Memory bank + 2 essential skills"
    echo "   • Best for: Most projects"
    echo ""
    print_color "$BLUE" "C. Comprehensive (~1,500 tokens)"
    echo "   • Slower startup (~3s)"
    echo "   • Full memory bank + 3-4 skills"
    echo "   • Best for: Complex enterprise projects"
    echo ""

    while true; do
        read -p "Your choice [A/B/C]: " choice
        case $choice in
            [Aa])
                STANDING_CONTEXT_BUDGET="minimal"
                STANDING_CONTEXT_TOKENS=500
                break
                ;;
            [Bb])
                STANDING_CONTEXT_BUDGET="balanced"
                STANDING_CONTEXT_TOKENS=1000
                break
                ;;
            [Cc])
                STANDING_CONTEXT_BUDGET="comprehensive"
                STANDING_CONTEXT_TOKENS=1500
                break
                ;;
            *)
                print_color "$RED" "Invalid choice. Please enter A, B, or C."
                ;;
        esac
    done

    print_color "$GREEN" "✓ Selected: $STANDING_CONTEXT_BUDGET (~$STANDING_CONTEXT_TOKENS tokens)"
}

# Question 2: Auto-Activation Strategy
ask_auto_activation() {
    print_header "Step 2/6: Auto-Activation Strategy"

    echo "How should Dev-AID auto-load skills/capabilities?"
    echo ""
    print_color "$GREEN" "A. Suggest Only (0 tokens)"
    echo "   • No auto-loading"
    echo "   • Manual activation only"
    echo "   • Best for: Explicit control"
    echo ""
    print_color "$YELLOW" "B. Conservative Load (file patterns) [RECOMMENDED]"
    echo "   • Pattern matching (*.test.* → TDD)"
    echo "   • Max 2-3 skills per prompt"
    echo "   • Best for: Predictable workflows"
    echo ""
    print_color "$BLUE" "C. Smart Load (AI decides)"
    echo "   • AI analyzes context"
    echo "   • Auto-loads relevant skills"
    echo "   • Best for: Experienced users"
    echo ""

    while true; do
        read -p "Your choice [A/B/C]: " choice
        case $choice in
            [Aa])
                AUTO_ACTIVATION="suggest"
                break
                ;;
            [Bb])
                AUTO_ACTIVATION="conservative"
                break
                ;;
            [Cc])
                AUTO_ACTIVATION="smart"
                break
                ;;
            *)
                print_color "$RED" "Invalid choice. Please enter A, B, or C."
                ;;
        esac
    done

    print_color "$GREEN" "✓ Selected: $AUTO_ACTIVATION mode"
}

# Question 3: AI Provider Selection
ask_providers() {
    print_header "Step 3/6: AI Provider Selection"

    echo "Which AI providers do you have access to?"
    echo "(Select all that apply)"
    echo ""

    # Claude
    print_color "$CYAN" "1. Claude (Anthropic)"
    echo "   • Strengths: Precise code generation, security analysis"
    echo "   • Context: 200K tokens"
    echo "   • Cost: \$3/1M tokens (Sonnet)"
    read -p "   Enable Claude? [Y/n]: " enable_claude
    if [[ $enable_claude =~ ^[Yy]$ ]] || [ -z "$enable_claude" ]; then
        ENABLED_PROVIDERS+=("claude")
        print_color "$GREEN" "   ✓ Claude enabled"
    fi
    echo ""

    # Gemini
    print_color "$CYAN" "2. Gemini (Google)"
    echo "   • Strengths: Massive context (2M tokens), fast processing"
    echo "   • Context: 2,000K tokens"
    echo "   • Cost: \$0.075/1M tokens (Flash)"
    read -p "   Enable Gemini? [y/N]: " enable_gemini
    if [[ $enable_gemini =~ ^[Yy]$ ]]; then
        ENABLED_PROVIDERS+=("gemini")
        print_color "$GREEN" "   ✓ Gemini enabled"
    fi
    echo ""

    # OpenAI
    print_color "$CYAN" "3. OpenAI (ChatGPT)"
    echo "   • Strengths: General tasks, documentation, versatile"
    echo "   • Context: 128K tokens"
    echo "   • Cost: \$5/1M tokens (GPT-4o)"
    read -p "   Enable OpenAI? [y/N]: " enable_openai
    if [[ $enable_openai =~ ^[Yy]$ ]]; then
        ENABLED_PROVIDERS+=("openai")
        print_color "$GREEN" "   ✓ OpenAI enabled"
    fi
    echo ""

    # OpenRouter
    print_color "$CYAN" "4. OpenRouter (Multi-provider)"
    echo "   • Strengths: Access to multiple models, automatic routing"
    echo "   • Provides fallback options"
    read -p "   Enable OpenRouter? [y/N]: " enable_openrouter
    if [[ $enable_openrouter =~ ^[Yy]$ ]]; then
        ENABLED_PROVIDERS+=("openrouter")
        print_color "$GREEN" "   ✓ OpenRouter enabled"
    fi
    echo ""

    # Ensure at least one provider is enabled
    if [ ${#ENABLED_PROVIDERS[@]} -eq 0 ]; then
        print_color "$YELLOW" "⚠  No providers enabled. Defaulting to Claude."
        ENABLED_PROVIDERS=("claude")
    fi

    print_color "$CYAN" "→ Enabled providers: ${ENABLED_PROVIDERS[*]}"
}

# Question 4: Orchestration Mode
ask_orchestration_mode() {
    print_header "Step 4/6: Orchestration Mode"

    echo "How should AI models work together?"
    echo ""
    print_color "$GREEN" "A. None (Manual Selection)"
    echo "   • You explicitly choose which AI for each task"
    echo "   • No automatic routing"
    echo "   • Best for: Maximum control, single AI usage"
    echo ""
    print_color "$YELLOW" "B. Solo Mode"
    echo "   • Single default model handles all tasks"
    echo "   • Simple, straightforward"
    echo "   • Best for: Single AI subscription"
    echo ""
    print_color "$BLUE" "C. Ensemble Mode [RECOMMENDED for multi-AI]"
    echo "   • Automatic routing based on task type"
    echo "   • Cost optimization"
    echo "   • Best for: Multiple AI subscriptions"
    echo ""
    print_color "$MAGENTA" "D. Challenger Mode"
    echo "   • Primary generates, challenger reviews"
    echo "   • Multi-perspective analysis"
    echo "   • Best for: High-security, critical code"
    echo ""

    # If only one provider, recommend None or Solo
    if [ ${#ENABLED_PROVIDERS[@]} -eq 1 ]; then
        print_color "$YELLOW" "💡 Note: You enabled only one provider. 'None' or 'Solo' recommended."
    fi

    while true; do
        read -p "Your choice [A/B/C/D]: " choice
        case $choice in
            [Aa])
                ORCHESTRATION_MODE="none"
                break
                ;;
            [Bb])
                ORCHESTRATION_MODE="solo"
                break
                ;;
            [Cc])
                ORCHESTRATION_MODE="ensemble"
                break
                ;;
            [Dd])
                ORCHESTRATION_MODE="challenger"
                break
                ;;
            *)
                print_color "$RED" "Invalid choice. Please enter A, B, C, or D."
                ;;
        esac
    done

    print_color "$GREEN" "✓ Selected: $ORCHESTRATION_MODE mode"
}

# Question 5: Model Assignment (for Ensemble/Challenger modes)
ask_model_assignment() {
    # Only ask if multiple providers and ensemble/challenger mode
    if [ ${#ENABLED_PROVIDERS[@]} -eq 1 ] || [ "$ORCHESTRATION_MODE" == "none" ]; then
        return
    fi

    if [ "$ORCHESTRATION_MODE" == "solo" ]; then
        print_header "Step 5/6: Default Model Selection"
        echo "Select your default model for all tasks:"
        echo ""
        select_default_model
        return
    fi

    print_header "Step 5/6: Model Assignment per Task Type"

    echo "Assign AI models to specific task types for optimal performance."
    echo ""
    print_color "$YELLOW" "💡 Tip: This optimizes costs and leverages each AI's strengths."
    echo ""

    # Code Generation
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_color "$CYAN" "1. Code Generation & Refactoring"
    echo "   (Writing code, refactoring, implementing features)"
    select_model_for_task "code_generation" "claude-sonnet-4.5"

    # Massive Context
    if [[ " ${ENABLED_PROVIDERS[*]} " =~ " gemini " ]]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_color "$CYAN" "2. Massive Context Analysis"
        echo "   (Reading 100+ files, repository-wide analysis)"
        select_model_for_task "massive_context" "gemini-2.0-flash"
    fi

    # Documentation
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_color "$CYAN" "3. Documentation & Explanations"
    echo "   (Writing READMEs, docs, code comments)"
    if [[ " ${ENABLED_PROVIDERS[*]} " =~ " openai " ]]; then
        select_model_for_task "documentation" "gpt-4o"
    else
        select_model_for_task "documentation" "claude-sonnet-4.5"
    fi

    # Security Analysis
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_color "$CYAN" "4. Security Analysis & Audits"
    echo "   (Security reviews, vulnerability detection)"
    select_model_for_task "security" "claude-sonnet-4.5"

    # Challenger mode additional assignment
    if [ "$ORCHESTRATION_MODE" == "challenger" ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_color "$CYAN" "5. Challenger Model"
        echo "   (Reviews and challenges primary model's output)"
        select_model_for_task "challenger" "gemini-2.0-pro"
    fi

    echo ""
    print_color "$GREEN" "✓ Model assignments complete"
}

# Helper: Select model for specific task
select_model_for_task() {
    local task_type="$1"
    local default_model="$2"

    echo ""
    echo "Available models:"

    local i=1
    local available_models=()

    # List available models from enabled providers
    for provider in "${ENABLED_PROVIDERS[@]}"; do
        case $provider in
            claude)
                available_models+=("claude-sonnet-4.5")
                echo "  $i) claude-sonnet-4.5 (Balanced, ${3}/1M)"
                ((i++))
                available_models+=("claude-opus-4.5")
                echo "  $i) claude-opus-4.5 (Most capable, \$15/1M)"
                ((i++))
                available_models+=("claude-haiku-4.5")
                echo "  $i) claude-haiku-4.5 (Fastest, $0.25/1M)"
                ((i++))
                ;;
            gemini)
                available_models+=("gemini-2.0-flash")
                echo "  $i) gemini-2.0-flash (1M context, $0.075/1M)"
                ((i++))
                available_models+=("gemini-2.0-pro")
                echo "  $i) gemini-2.0-pro (2M context, $1.25/1M)"
                ((i++))
                ;;
            openai)
                available_models+=("gpt-4o")
                echo "  $i) gpt-4o (Versatile, $5/1M)"
                ((i++))
                available_models+=("gpt-4-turbo")
                echo "  $i) gpt-4-turbo (Capable, \$10/1M)"
                ((i++))
                ;;
        esac
    done

    # Find default index
    local default_idx=1
    for idx in "${!available_models[@]}"; do
        if [ "${available_models[$idx]}" == "$default_model" ]; then
            default_idx=$((idx + 1))
            break
        fi
    done

    echo ""
    read -p "Select model [1-$((i-1)), default: $default_idx]: " selection

    if [ -z "$selection" ]; then
        selection=$default_idx
    fi

    if [ "$selection" -ge 1 ] && [ "$selection" -lt "$i" ]; then
        local selected_model="${available_models[$((selection-1))]}"
        TASK_MODEL_MAPPING[$task_type]="$selected_model"
        print_color "$GREEN" "   → $task_type: $selected_model"
    else
        print_color "$YELLOW" "   → Using default: $default_model"
        TASK_MODEL_MAPPING[$task_type]="$default_model"
    fi
}

# Helper: Select default model
select_default_model() {
    local i=1
    local available_models=()

    for provider in "${ENABLED_PROVIDERS[@]}"; do
        case $provider in
            claude)
                available_models+=("claude-sonnet-4.5")
                echo "  $i) claude-sonnet-4.5 (Recommended)"
                ((i++))
                ;;
            gemini)
                available_models+=("gemini-2.0-flash")
                echo "  $i) gemini-2.0-flash"
                ((i++))
                ;;
            openai)
                available_models+=("gpt-4o")
                echo "  $i) gpt-4o"
                ((i++))
                ;;
        esac
    done

    read -p "Select default model [1-$((i-1))]: " selection

    if [ "$selection" -ge 1 ] && [ "$selection" -lt "$i" ]; then
        TASK_MODEL_MAPPING["default"]="${available_models[$((selection-1))]}"
        print_color "$GREEN" "✓ Default model: ${available_models[$((selection-1))]}"
    else
        TASK_MODEL_MAPPING["default"]="${available_models[0]}"
        print_color "$GREEN" "✓ Default model: ${available_models[0]}"
    fi
}

# Question 6: API Keys
ask_api_keys() {
    print_header "Step 6/6: API Key Configuration"

    echo "Enter API keys for your enabled providers."
    print_color "$YELLOW" "💡 Tip: Keys are stored in .dev-aid/config/.env (gitignored)"
    echo ""

    for provider in "${ENABLED_PROVIDERS[@]}"; do
        case $provider in
            claude)
                print_color "$CYAN" "Claude (Anthropic) API Key"
                echo "Get your key from: https://console.anthropic.com/"
                read -sp "ANTHROPIC_API_KEY: " claude_key
                echo ""
                if [ -n "$claude_key" ]; then
                    COLLECTED_API_KEYS+=("ANTHROPIC_API_KEY=$claude_key")
                    print_color "$GREEN" "✓ Claude API key saved"
                else
                    print_color "$YELLOW" "⚠  Skipped (you can add it later)"
                fi
                echo ""
                ;;
            gemini)
                print_color "$CYAN" "Gemini (Google) API Key"
                echo "Get your key from: https://aistudio.google.com/app/apikey"
                read -sp "GOOGLE_API_KEY: " gemini_key
                echo ""
                if [ -n "$gemini_key" ]; then
                    COLLECTED_API_KEYS+=("GOOGLE_API_KEY=$gemini_key")
                    print_color "$GREEN" "✓ Gemini API key saved"
                else
                    print_color "$YELLOW" "⚠  Skipped (you can add it later)"
                fi
                echo ""
                ;;
            openai)
                print_color "$CYAN" "OpenAI API Key"
                echo "Get your key from: https://platform.openai.com/api-keys"
                read -sp "OPENAI_API_KEY: " openai_key
                echo ""
                if [ -n "$openai_key" ]; then
                    COLLECTED_API_KEYS+=("OPENAI_API_KEY=$openai_key")
                    print_color "$GREEN" "✓ OpenAI API key saved"
                else
                    print_color "$YELLOW" "⚠  Skipped (you can add it later)"
                fi
                echo ""
                ;;
            openrouter)
                print_color "$CYAN" "OpenRouter API Key"
                echo "Get your key from: https://openrouter.ai/keys"
                read -sp "OPENROUTER_API_KEY: " openrouter_key
                echo ""
                if [ -n "$openrouter_key" ]; then
                    COLLECTED_API_KEYS+=("OPENROUTER_API_KEY=$openrouter_key")
                    print_color "$GREEN" "✓ OpenRouter API key saved"
                else
                    print_color "$YELLOW" "⚠  Skipped (you can add it later)"
                fi
                echo ""
                ;;
        esac
    done
}

# Create configuration files
create_config_files() {
    print_header "Creating Configuration Files"

    # Create .env file for API keys
    print_color "$CYAN" "→ Creating .dev-aid/config/.env..."

    # Create with secure permissions
    touch "$DEV_AID_DIR/config/.env"
    chmod 600 "$DEV_AID_DIR/config/.env"

    cat > "$DEV_AID_DIR/config/.env" <<EOF
# Dev-AID API Keys
# This file is gitignored for security

$(printf '%s\n' "${COLLECTED_API_KEYS[@]}")
EOF

    # Ensure permissions are set (in case cat reset them)
    chmod 600 "$DEV_AID_DIR/config/.env"

    print_color "$GREEN" "✓ API keys saved to .dev-aid/config/.env (permissions: 600)"

    # Update settings.json
    print_color "$CYAN" "→ Updating .dev-aid/config/settings.json..."

    cat > "$DEV_AID_DIR/config/settings.json" <<EOF
{
  "dev_aid_version": "2.0.0",
  "project_name": "$(basename "$PROJECT_ROOT")",
  "installed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",

  "standing_context_budget": "$STANDING_CONTEXT_BUDGET",
  "standing_context_tokens": $STANDING_CONTEXT_TOKENS,

  "auto_activation": "$AUTO_ACTIVATION",
  "auto_load_max_skills": 3,

  "orchestration_mode": "$ORCHESTRATION_MODE",

  "enabled_providers": [$(printf '"%s",' "${ENABLED_PROVIDERS[@]}" | sed 's/,$//')],

  "task_model_mapping": $(generate_task_mapping_json),

  "memory_bank": {
    "auto_load": ["activeContext.md"],
    "on_demand": [
      "patterns.md",
      "decisions.md",
      "security.md",
      "performance.md",
      "testing.md",
      "chaos.md"
    ]
  },

  "context_sharing": {
    "enabled": true,
    "logging": {
      "enabled": true,
      "log_file": ".dev-aid/logs/context-sharing.log",
      "log_level": "info"
    }
  },

  "hooks": {
    "enabled": true,
    "session_start": true,
    "user_prompt_submit": true,
    "post_tool_use": false,
    "stop": true
  }
}
EOF

    print_color "$GREEN" "✓ Settings configured"

    # Update orchestration.json mode
    print_color "$CYAN" "→ Updating .dev-aid/config/orchestration.json..."

    if command -v jq &> /dev/null; then
        jq ".mode = \"$ORCHESTRATION_MODE\"" \
            "$DEV_AID_DIR/config/orchestration.json" > "$DEV_AID_DIR/config/orchestration.json.tmp"
        mv "$DEV_AID_DIR/config/orchestration.json.tmp" "$DEV_AID_DIR/config/orchestration.json"
    else
        sed -i "s/\"mode\": \".*\"/\"mode\": \"$ORCHESTRATION_MODE\"/" \
            "$DEV_AID_DIR/config/orchestration.json" 2>/dev/null || true
    fi

    print_color "$GREEN" "✓ Orchestration configured"

    # Create .gitignore
    print_color "$CYAN" "→ Creating .dev-aid/.gitignore..."
    cat > "$DEV_AID_DIR/.gitignore" <<EOF
# API Keys (NEVER commit these!)
config/.env
config/.env.*

# Logs
logs/
*.log

# Temporary files
*.tmp
.DS_Store
EOF

    print_color "$GREEN" "✓ .gitignore created"

    # Create logs directory
    mkdir -p "$DEV_AID_DIR/logs"
    print_color "$GREEN" "✓ Logs directory created"
}

# Helper: Generate task mapping JSON
generate_task_mapping_json() {
    echo "{"
    local first=true
    for task in "${!TASK_MODEL_MAPPING[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        echo -n "    \"$task\": \"${TASK_MODEL_MAPPING[$task]}\""
    done
    echo ""
    echo "  }"
}

# Setup provider symlinks
setup_provider_symlinks() {
    print_header "Setting Up Provider Context Files"

    # Source the smart CLAUDE.md initialization library
    local lib_dir="$DEV_AID_DIR/scripts/lib"
    if [ -f "$lib_dir/claude-md-init.sh" ]; then
        source "$lib_dir/claude-md-init.sh"
    fi

    for provider in "${ENABLED_PROVIDERS[@]}"; do
        local context_file=""
        case $provider in
            claude) context_file="CLAUDE.md" ;;
            gemini) context_file="GEMINI.md" ;;
            openai) context_file="OPENAI.md" ;;
            openrouter) context_file="OPENROUTER.md" ;;
        esac

        if [[ -n "$context_file" ]]; then
            # Special handling for CLAUDE.md with smart initialization
            if [[ "$provider" == "claude" ]] && [[ -f "$lib_dir/claude-md-init.sh" ]]; then
                # Use smart initialization for CLAUDE.md
                init_claude_md_interactive "$PROJECT_ROOT" "$provider" || {
                    # Fallback to simple symlink on error
                    print_color "$YELLOW" "⚠ Smart initialization failed, using simple mode"
                    setup_simple_symlink "$provider" "$context_file"
                }
            else
                # Use simple symlink for other providers
                setup_simple_symlink "$provider" "$context_file"
            fi
        fi
    done
}

# Simple symlink setup (for non-Claude providers or fallback)
setup_simple_symlink() {
    local provider="$1"
    local context_file="$2"

    if [[ -f "$DEV_AID_DIR/providers/$provider/$context_file" ]]; then
        print_color "$CYAN" "→ Creating symlink for $context_file..."

        # Validate target path before removal
        local target_file="$PROJECT_ROOT/$context_file"
        if [[ -e "$target_file" ]] || [[ -L "$target_file" ]]; then
            # Validate path containment (prevent deletion outside project)
            local target_dir
            target_dir="$(dirname "$target_file")"
            local resolved_target_dir
            resolved_target_dir="$(realpath -m "$target_dir")"
            local resolved_project_root
            resolved_project_root="$(realpath "$PROJECT_ROOT")"

            if [[ "$resolved_target_dir" == "$resolved_project_root"* ]]; then
                rm -f "$target_file"
            else
                print_color "$RED" "Error: Path traversal detected for $context_file"
                return 1
            fi
        fi

        # Create symlink
        ln -s ".dev-aid/providers/$provider/$context_file" "$PROJECT_ROOT/$context_file"

        print_color "$GREEN" "✓ $context_file → .dev-aid/providers/$provider/$context_file"
    fi
}

# Initialize memory bank
init_memory_bank() {
    print_header "Initializing Memory Bank"

    local active_context="$DEV_AID_DIR/memory-bank/activeContext.md"

    if [ -f "$active_context" ]; then
        # Update project name in activeContext
        if command -v sed &> /dev/null; then
            sed -i "s/\*\*Project\*\*:.*/\*\*Project\*\*: $(basename "$PROJECT_ROOT")/" "$active_context" 2>/dev/null || true
        fi
        print_color "$GREEN" "✓ Memory bank initialized with project name"
    fi
}

# Ask about codebase analysis
ask_codebase_analysis() {
    print_header "Step 7/7: Codebase Analysis (Optional)"

    echo "Dev-AID can analyze your entire codebase and generate a detailed"
    echo "adaptation plan with specific recommendations for:"
    echo ""
    echo "  • Memory bank content tailored to your project"
    echo "  • Provider context files with project-specific information"
    echo "  • Recommended skills and agents to activate"
    echo "  • Custom hooks for your workflow"
    echo "  • Documentation improvements"
    echo "  • Code organization suggestions"
    echo "  • CI/CD integration points"
    echo ""
    echo "This analysis will:"
    echo "  1. Explore your codebase structure"
    echo "  2. Detect tech stack and patterns"
    echo "  3. Generate a phased implementation plan"
    echo "  4. Create a quick-start checklist"
    echo ""
    print_color "$YELLOW" "⏱️  Analysis takes 2-5 minutes depending on codebase size."
    echo ""

    read -p "Would you like to run codebase analysis now? (y/N): " run_analysis

    if [[ "$run_analysis" =~ ^[Yy]$ ]]; then
        print_color "$CYAN" "🔍 Starting codebase analysis..."
        echo ""
        echo "Analysis will be saved to:"
        echo "  • .dev-aid/analysis/adaptation-plan.md (comprehensive)"
        echo "  • .dev-aid/analysis/quick-start-checklist.md (condensed)"
        echo ""

        # Create analysis directory
        mkdir -p "$DEV_AID_DIR/analysis"

        print_color "$GREEN" "✓ Analysis directory created"
        echo ""
        print_color "$CYAN" "To run the analysis, use one of these methods:"
        echo ""
        echo "Method 1: Use the slash command (recommended)"
        print_color "$YELLOW" "  /aid-analyze"
        echo ""
        echo "Method 2: Activate the agent"
        print_color "$YELLOW" '  "analyze my project for dev-aid"'
        echo ""
        echo "Method 3: Use Claude Code directly"
        print_color "$YELLOW" "  claude code"
        echo '  Then say: "Run /aid-analyze"'
        echo ""

        print_color "$GREEN" "📄 Style Guide Reference:"
        echo "  For details on Dev-AID best practices, see:"
        echo "  .dev-aid/docs/DEV-AID-STYLE-GUIDE.md"
        echo ""

    else
        print_color "$CYAN" "ℹ️  You can run codebase analysis anytime by:"
        echo ""
        echo "  1. Running the slash command:"
        print_color "$YELLOW" "     /aid-analyze"
        echo ""
        echo "  2. Or saying to Claude:"
        print_color "$YELLOW" '     "analyze my project for dev-aid"'
        echo ""
        echo "  3. Review the style guide:"
        print_color "$YELLOW" "     .dev-aid/docs/DEV-AID-STYLE-GUIDE.md"
        echo ""
    fi
}

# Ask about security automation setup
ask_security_automation() {
    print_header "Step 8/8: Security Automation (Recommended)"

    echo "Dev-AID includes automated security scanning that runs automatically:"
    echo ""
    echo "  🔒 3-Tier Defense System:"
    echo "  • Pre-commit hook (~10s): Fast critical checks"
    echo "  • Pre-push hook (~60s): Thorough security scan"
    echo "  • CI/CD templates: Complete security suite"
    echo ""
    echo "  🛡️ Security Tools (all open source):"
    echo "  • Opengrep - SAST (code vulnerabilities)"
    echo "  • Gitleaks - Secret scanning"
    echo "  • Trivy - Dependencies + containers + IaC"
    echo "  • Hadolint - Dockerfile linting"
    echo "  • Checkov - Infrastructure-as-Code scanning"
    echo ""
    echo "  ✨ Benefits:"
    echo "  • Never forget to run security checks"
    echo "  • Catches secrets before commit"
    echo "  • Blocks critical vulnerabilities automatically"
    echo "  • $0 cost (all open source tools)"
    echo ""
    print_color "$YELLOW" "⏱️  Installation takes ~2-3 minutes"
    echo ""

    read -p "Install security automation now? (Y/n): " install_security

    if [[ ! "$install_security" =~ ^[Nn]$ ]]; then
        print_color "$CYAN" "🔧 Installing security tools..."
        echo ""

        # Run security tools installer
        if [ -x "$DEV_AID_DIR/automation/tools/install-security-tools.sh" ]; then
            "$DEV_AID_DIR/automation/tools/install-security-tools.sh"
            SECURITY_TOOLS_INSTALLED=true
        else
            print_color "$YELLOW" "⚠️  Security tools installer not found"
            print_color "$YELLOW" "  You can install later: ./.dev-aid/automation/tools/install-security-tools.sh"
            SECURITY_TOOLS_INSTALLED=false
        fi

        echo ""
        print_color "$CYAN" "🪝 Installing git hooks..."
        echo ""

        # Install git hooks
        if [ -x "$DEV_AID_DIR/automation/git-hooks/install.sh" ]; then
            cd "$PROJECT_ROOT"
            "$DEV_AID_DIR/automation/git-hooks/install.sh"
            SECURITY_HOOKS_INSTALLED=true
        else
            print_color "$YELLOW" "⚠️  Git hooks installer not found"
            print_color "$YELLOW" "  You can install later: ./.dev-aid/automation/git-hooks/install.sh"
            SECURITY_HOOKS_INSTALLED=false
        fi

        echo ""
        if [ "$SECURITY_TOOLS_INSTALLED" = true ] && [ "$SECURITY_HOOKS_INSTALLED" = true ]; then
            print_color "$GREEN" "✅ Security automation installed successfully!"
            echo ""
            print_color "$CYAN" "📚 Documentation:"
            echo "  • Complete Guide: .dev-aid/docs/AUTOMATION-GUIDE.md"
            echo "  • Tool Reference: .dev-aid/docs/SECURITY-TOOLS-REFERENCE.md"
            echo ""
        fi
    else
        print_color "$CYAN" "ℹ️  You can install security automation anytime:"
        echo ""
        echo "  1. Install tools:"
        print_color "$YELLOW" "     ./.dev-aid/automation/tools/install-security-tools.sh"
        echo ""
        echo "  2. Install git hooks:"
        print_color "$YELLOW" "     ./.dev-aid/automation/git-hooks/install.sh"
        echo ""
        echo "  3. Read the guide:"
        print_color "$YELLOW" "     ./.dev-aid/docs/AUTOMATION-GUIDE.md"
        echo ""
        SECURITY_TOOLS_INSTALLED=false
        SECURITY_HOOKS_INSTALLED=false
    fi
}

# Display summary
show_summary() {
    print_header "🎉 Installation Complete!"

    echo "Dev-AID has been configured for your project:"
    echo ""

    print_color "$CYAN" "📊 Configuration Summary:"
    echo ""
    echo "  Context Budget:     $STANDING_CONTEXT_BUDGET (~$STANDING_CONTEXT_TOKENS tokens)"
    echo "  Auto-Activation:    $AUTO_ACTIVATION"
    echo "  Orchestration:      $ORCHESTRATION_MODE mode"
    echo "  Enabled Providers:  ${ENABLED_PROVIDERS[*]}"
    echo ""

    if [ ${#TASK_MODEL_MAPPING[@]} -gt 0 ]; then
        print_color "$CYAN" "🎯 Model Assignments:"
        echo ""
        for task in "${!TASK_MODEL_MAPPING[@]}"; do
            printf "  %-20s → %s\n" "$task" "${TASK_MODEL_MAPPING[$task]}"
        done
        echo ""
    fi

    print_color "$CYAN" "📁 Files Created:"
    echo "  • .dev-aid/config/.env (API keys - gitignored)"
    echo "  • .dev-aid/config/settings.json"
    echo "  • .dev-aid/config/orchestration.json (updated)"
    echo "  • .dev-aid/.gitignore"
    for provider in "${ENABLED_PROVIDERS[@]}"; do
        case $provider in
            claude) echo "  • CLAUDE.md (symlink)" ;;
            gemini) echo "  • GEMINI.md (symlink)" ;;
            openai) echo "  • OPENAI.md (symlink)" ;;
        esac
    done
    echo ""

    if [ "$SECURITY_TOOLS_INSTALLED" = true ] || [ "$SECURITY_HOOKS_INSTALLED" = true ]; then
        print_color "$CYAN" "🔒 Security Automation:"
        echo ""
        if [ "$SECURITY_TOOLS_INSTALLED" = true ]; then
            echo "  ✅ Security tools installed (Opengrep, Gitleaks, Trivy, Hadolint, Checkov)"
        fi
        if [ "$SECURITY_HOOKS_INSTALLED" = true ]; then
            echo "  ✅ Git hooks installed (pre-commit, pre-push)"
            echo "  • Pre-commit: Fast critical checks (~10s)"
            echo "  • Pre-push: Thorough security scan (~60s)"
        fi
        echo ""
        echo "  📚 Documentation:"
        echo "     .dev-aid/docs/AUTOMATION-GUIDE.md"
        echo ""
    fi

    print_color "$CYAN" "🔄 Reconfiguration:"
    echo "  You can change these settings anytime by running:"
    print_color "$YELLOW" "  ./.dev-aid/scripts/reconfigure.sh"
    echo ""
    echo "  This preserves your memory bank and existing context!"
    echo ""

    print_color "$CYAN" "📝 Context Sharing & Logging:"
    echo "  When models collaborate, context is passed via:"
    print_color "$YELLOW" "  .dev-aid/logs/context-sharing.log"
    echo ""
    echo "  You can view:"
    echo "  • Which models handled which tasks"
    echo "  • Context passed between models"
    echo "  • Performance metrics"
    echo ""

    print_color "$CYAN" "🚀 Next Steps:"
    echo ""
    echo "1. Source API keys (if not entered during setup):"
    echo "   source .dev-aid/config/.env"
    echo ""
    echo "2. Review memory bank:"
    echo "   vim .dev-aid/memory-bank/activeContext.md"
    echo ""
    echo "3. Start your AI-powered development:"
    print_color "$GREEN" "   claude code"
    echo ""

    print_color "$CYAN" "📚 Documentation:"
    echo "  • Full Guide:         ../DEV-AID-IMPLEMENTATION-PLAN.md"
    echo "  • Usage Examples:     README.md"
    echo "  • Reconfiguration:    .dev-aid/scripts/reconfigure.sh --help"
    echo ""

    print_color "$MAGENTA" "Happy coding with Dev-AID! 🚀"
    echo ""
}

# Main installation flow
main() {
    # Determine project root
    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

    # Validate PROJECT_ROOT is within safe bounds (e.g., not system directories)
    local resolved_project_root
    resolved_project_root="$(realpath "$PROJECT_ROOT")"

    # Ensure PROJECT_ROOT is not a system directory
    local unsafe_paths=("/" "/etc" "/usr" "/bin" "/sbin" "/boot" "/sys" "/proc" "/dev")
    for unsafe_path in "${unsafe_paths[@]}"; do
        if [[ "$resolved_project_root" == "$unsafe_path" ]] || [[ "$resolved_project_root" == "$unsafe_path"/* ]]; then
            print_color "$RED" "Error: PROJECT_ROOT points to a system directory: $resolved_project_root"
            echo "This installer should be run from a user project directory."
            exit 1
        fi
    done

    DEV_AID_DIR="$PROJECT_ROOT/.dev-aid"

    # Check if .dev-aid exists
    if [[ ! -d "$DEV_AID_DIR" ]]; then
        print_color "$RED" "Error: .dev-aid directory not found!"
        echo "Please ensure you're running this from a Dev-AID installation."
        exit 1
    fi

    # Show welcome
    show_welcome

    # Run configuration wizard
    ask_context_budget
    ask_auto_activation
    ask_providers
    ask_orchestration_mode
    ask_model_assignment
    ask_api_keys

    # Create configurations
    create_config_files

    # Setup provider symlinks
    setup_provider_symlinks

    # Initialize memory bank
    init_memory_bank

    # Ask about codebase analysis
    ask_codebase_analysis

    # Ask about security automation
    ask_security_automation

    # Show summary
    show_summary
}

# Run installer
main "$@"
