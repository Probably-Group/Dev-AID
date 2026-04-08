#!/usr/bin/env bash
# Dev-AID Wizard Functions Library
# Extracted from install.sh — interactive configuration wizard.
# Sourced by setup-dev-aid.sh — not run directly.
#
# Requires: NON_INTERACTIVE (bool), colors (RED, GREEN, YELLOW, BLUE, CYAN, MAGENTA, NC)
# Sets: STANDING_CONTEXT_BUDGET, STANDING_CONTEXT_TOKENS, AUTO_ACTIVATION,
#        ORCHESTRATION_MODE, ENABLED_PROVIDERS[], COLLECTED_API_KEYS[],
#        TASK_MODEL_MAPPING (associative array)

# ============================================================================
# Defaults for non-interactive mode
# ============================================================================

apply_wizard_defaults() {
    STANDING_CONTEXT_BUDGET="balanced"
    STANDING_CONTEXT_TOKENS=1000
    AUTO_ACTIVATION="conservative"
    ORCHESTRATION_MODE="solo"
    ENABLED_PROVIDERS=("claude")
    COLLECTED_API_KEYS=()
    SELECTED_PRESET="generic"
    SELECTED_PRESET_PATH=""
    declare -gA TASK_MODEL_MAPPING
    TASK_MODEL_MAPPING["default"]="claude-sonnet-4-6"
}

# ============================================================================
# Print helpers
# ============================================================================

print_color() {
    local color="$1"
    shift
    echo -e "${color}$*${NC}"
}

print_header() {
    echo ""
    print_color "$CYAN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_color "$CYAN" "$1"
    print_color "$CYAN" "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# ============================================================================
# Welcome
# ============================================================================

show_welcome() {
    if [ "$NON_INTERACTIVE" = true ]; then
        return
    fi

    print_color "$MAGENTA" "
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║       Dev-AID (Development AI Driver) Setup                    ║
║                                                                ║
║     Multi-Model AI Orchestration for Elite Development        ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"
    print_color "$YELLOW" "Welcome to Dev-AID setup!"
    echo ""
    echo "This will configure AI-powered development assistance"
    echo "for your project with support for multiple AI models."
    echo ""
    print_color "$CYAN" "You'll choose:"
    echo "  * Which AI providers to use"
    echo "  * Which models for which tasks"
    echo "  * How models work together (or independently)"
    echo "  * Your token budget and preferences"
    echo ""
    print_color "$YELLOW" "Tip: You can reconfigure anytime with .dev-aid/scripts/reconfigure.sh"
    echo ""
    read -p "Press Enter to begin setup..."
}

# ============================================================================
# Step 1: Standing Context Budget
# ============================================================================

ask_context_budget() {
    if [ "$NON_INTERACTIVE" = true ]; then
        return
    fi

    print_header "Step 1/7: Standing Context Budget"

    echo "How much token budget for standing context?"
    echo ""
    print_color "$GREEN" "A. Minimal (~500 tokens)"
    echo "   * Fastest startup (<1s)"
    echo "   * Only essential auto-loads"
    echo "   * Best for: Quick tasks, small projects"
    echo ""
    print_color "$YELLOW" "B. Balanced (~1,000 tokens) [RECOMMENDED]"
    echo "   * Fast startup (~2s)"
    echo "   * Memory bank + 2 essential skills"
    echo "   * Best for: Most projects"
    echo ""
    print_color "$BLUE" "C. Comprehensive (~1,500 tokens)"
    echo "   * Slower startup (~3s)"
    echo "   * Full memory bank + 3-4 skills"
    echo "   * Best for: Complex enterprise projects"
    echo ""

    # Show existing default if re-init
    local default_hint=""
    if [ -n "${EXISTING_CONTEXT_BUDGET:-}" ]; then
        default_hint=" [current: ${EXISTING_CONTEXT_BUDGET}]"
    fi

    while true; do
        read -p "Your choice [A/B/C]${default_hint}: " choice
        case ${choice:-B} in
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

    print_color "$GREEN" "Selected: $STANDING_CONTEXT_BUDGET (~$STANDING_CONTEXT_TOKENS tokens)"
}

# ============================================================================
# Step 2: Auto-Activation Strategy
# ============================================================================

ask_auto_activation() {
    if [ "$NON_INTERACTIVE" = true ]; then
        return
    fi

    print_header "Step 2/7: Auto-Activation Strategy"

    echo "How should Dev-AID auto-load skills/capabilities?"
    echo ""
    print_color "$GREEN" "A. Suggest Only (0 tokens)"
    echo "   * No auto-loading"
    echo "   * Manual activation only"
    echo "   * Best for: Explicit control"
    echo ""
    print_color "$YELLOW" "B. Conservative Load (file patterns) [RECOMMENDED]"
    echo "   * Pattern matching (*.test.* -> TDD)"
    echo "   * Max 2-3 skills per prompt"
    echo "   * Best for: Predictable workflows"
    echo ""
    print_color "$BLUE" "C. Smart Load (AI decides)"
    echo "   * AI analyzes context"
    echo "   * Auto-loads relevant skills"
    echo "   * Best for: Experienced users"
    echo ""

    while true; do
        read -p "Your choice [A/B/C]: " choice
        case ${choice:-B} in
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

    print_color "$GREEN" "Selected: $AUTO_ACTIVATION mode"
}

# ============================================================================
# Step 3: Project Preset
# ============================================================================

ask_project_preset() {
    if [ "$NON_INTERACTIVE" = true ]; then
        return
    fi

    # Requires preset-functions.sh to be sourced
    if ! type detect_preset &>/dev/null; then
        return
    fi

    print_header "Step 3/7: Project Preset"

    echo "Dev-AID can generate stack-specific rules, troubleshooting playbooks,"
    echo "smoke tests, and session recovery plans for your project."
    echo ""

    echo -e "${CYAN}Detecting project type...${NC}"
    local detected
    detected=$(detect_preset "$PROJECT_ROOT") || true
    echo -e "${GREEN}Detected: ${detected}${NC}"
    echo ""

    prompt_preset "$detected"
    echo ""

    if [[ -n "${SELECTED_PRESET:-}" ]] && [[ "$SELECTED_PRESET" != "generic" ]]; then
        load_preset "$SELECTED_PRESET"
        echo -e "${GREEN}Loaded preset: ${preset_name:-$SELECTED_PRESET} — ${preset_description:-}${NC}"
    elif [[ "${SELECTED_PRESET:-}" == "generic" ]]; then
        load_preset "generic"
        echo -e "${GREEN}Loaded preset: generic — ${preset_description:-Minimal scaffolding}${NC}"
    fi
}

# ============================================================================
# Step 4: AI Provider Selection
# ============================================================================

ask_providers() {
    if [ "$NON_INTERACTIVE" = true ]; then
        return
    fi

    print_header "Step 4/7: AI Provider Selection"

    echo "Which AI providers do you have access to?"
    echo "(Select all that apply)"
    echo ""

    # Claude
    print_color "$CYAN" "1. Claude (Anthropic)"
    echo "   * Strengths: Precise code generation, security analysis"
    echo "   * Context: 200K tokens"
    echo "   * Cost: \$3/1M tokens (Sonnet)"
    read -p "   Enable Claude? [Y/n]: " enable_claude
    if [[ $enable_claude =~ ^[Yy]$ ]] || [ -z "$enable_claude" ]; then
        ENABLED_PROVIDERS+=("claude")
        print_color "$GREEN" "   Claude enabled"
    fi
    echo ""

    # Gemini
    print_color "$CYAN" "2. Gemini (Google)"
    echo "   * Strengths: Massive context (2M tokens), fast processing"
    echo "   * Context: 2,000K tokens"
    echo "   * Cost: \$0.075/1M tokens (Flash)"
    read -p "   Enable Gemini? [y/N]: " enable_gemini
    if [[ $enable_gemini =~ ^[Yy]$ ]]; then
        ENABLED_PROVIDERS+=("gemini")
        print_color "$GREEN" "   Gemini enabled"
    fi
    echo ""

    # OpenAI
    print_color "$CYAN" "3. OpenAI (ChatGPT)"
    echo "   * Strengths: General tasks, documentation, versatile"
    echo "   * Context: 128K tokens"
    echo "   * Cost: \$5/1M tokens (GPT-4o)"
    read -p "   Enable OpenAI? [y/N]: " enable_openai
    if [[ $enable_openai =~ ^[Yy]$ ]]; then
        ENABLED_PROVIDERS+=("openai")
        print_color "$GREEN" "   OpenAI enabled"
    fi
    echo ""

    # OpenRouter
    print_color "$CYAN" "4. OpenRouter (Multi-provider)"
    echo "   * Strengths: Access to multiple models, automatic routing"
    echo "   * Provides fallback options"
    read -p "   Enable OpenRouter? [y/N]: " enable_openrouter
    if [[ $enable_openrouter =~ ^[Yy]$ ]]; then
        ENABLED_PROVIDERS+=("openrouter")
        print_color "$GREEN" "   OpenRouter enabled"
    fi
    echo ""

    # AI/ML API
    print_color "$CYAN" "5. AI/ML API (200+ models, single key)"
    echo "   * Strengths: Access to 200+ AI models from all major providers"
    echo "   * Single API key for Claude, GPT, Gemini, Llama, and more"
    echo "   * Affiliate: Dev-AID may receive a referral commission at no extra cost to you"
    read -p "   Enable AI/ML API? [y/N]: " enable_aimlapi
    if [[ $enable_aimlapi =~ ^[Yy]$ ]]; then
        ENABLED_PROVIDERS+=("aimlapi")
        print_color "$GREEN" "   AI/ML API enabled"
    fi
    echo ""

    # Ensure at least one provider
    if [ ${#ENABLED_PROVIDERS[@]} -eq 0 ]; then
        print_color "$YELLOW" "No providers enabled. Defaulting to Claude."
        ENABLED_PROVIDERS=("claude")
    fi

    print_color "$CYAN" "Enabled providers: ${ENABLED_PROVIDERS[*]}"
}

# ============================================================================
# Step 4: Orchestration Mode
# ============================================================================

ask_orchestration_mode() {
    if [ "$NON_INTERACTIVE" = true ]; then
        return
    fi

    print_header "Step 5/7: Orchestration Mode"

    echo "How should AI models work together?"
    echo ""
    print_color "$GREEN" "A. None (Manual Selection)"
    echo "   * You explicitly choose which AI for each task"
    echo "   * No automatic routing"
    echo "   * Best for: Maximum control, single AI usage"
    echo ""
    print_color "$YELLOW" "B. Solo Mode"
    echo "   * Single default model handles all tasks"
    echo "   * Simple, straightforward"
    echo "   * Best for: Single AI subscription"
    echo ""
    print_color "$BLUE" "C. Ensemble Mode [RECOMMENDED for multi-AI]"
    echo "   * Automatic routing based on task type"
    echo "   * Cost optimization"
    echo "   * Best for: Multiple AI subscriptions"
    echo ""
    print_color "$MAGENTA" "D. Challenger Mode"
    echo "   * Primary generates, challenger reviews"
    echo "   * Multi-perspective analysis"
    echo "   * Best for: High-security, critical code"
    echo ""

    if [ ${#ENABLED_PROVIDERS[@]} -eq 1 ]; then
        print_color "$YELLOW" "Note: You enabled only one provider. 'None' or 'Solo' recommended."
    fi

    while true; do
        read -p "Your choice [A/B/C/D]: " choice
        case ${choice:-B} in
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

    print_color "$GREEN" "Selected: $ORCHESTRATION_MODE mode"
}

# ============================================================================
# Step 5: Model Assignment
# ============================================================================

# Resolve the path to models.json relative to this script. Compute purely from
# BASH_SOURCE so we don't accidentally inherit a stale parent SCRIPT_DIR.
# This lib lives at .dev-aid/scripts/lib/wizard-functions.sh, so models.json
# is at ../../config/models.json.
_wizard_models_json_path() {
    local lib_dir
    lib_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    echo "$lib_dir/config/models.json"
}

# Format a context window value for display: 1000000 → "1M", 128000 → "128K".
_wizard_format_context() {
    local ctx="${1:-0}"
    if [ "$ctx" -ge 1000000 ]; then
        echo "$((ctx / 1000000))M"
    elif [ "$ctx" -ge 1000 ]; then
        echo "$((ctx / 1000))K"
    else
        echo "$ctx"
    fi
}

# Print one line per model for the given provider, formatted as
#   "<model_id>|<input_cost>|<output_cost>|<context_window>"
# Reads dynamically from models.json so the wizard never goes stale relative
# to the source-of-truth model registry. Prints nothing if jq is missing or
# the provider has no entries.
_wizard_models_for_provider() {
    local provider="$1"
    local models_json
    models_json="$(_wizard_models_json_path)"

    if [ ! -f "$models_json" ]; then
        return 1
    fi
    if ! command -v jq &>/dev/null; then
        return 1
    fi

    jq -r --arg p "$provider" '
        .[$p].models // {}
        | to_entries[]
        | "\(.value.id)|\(.value.cost_per_1m_tokens.input // 0)|\(.value.cost_per_1m_tokens.output // 0)|\(.value.context_window // 0)"
    ' "$models_json"
}

select_model_for_task() {
    local task_type="$1"
    local default_model="$2"

    echo ""
    echo "Available models:"

    local i=1
    local available_models=()
    local model_id input_cost output_cost ctx ctx_human

    for provider in "${ENABLED_PROVIDERS[@]}"; do
        while IFS='|' read -r model_id input_cost output_cost ctx; do
            [ -z "$model_id" ] && continue
            available_models+=("$model_id")
            ctx_human="$(_wizard_format_context "$ctx")"
            echo "  $i) $model_id (\$${input_cost}/\$${output_cost} per 1M, ${ctx_human} ctx)"
            i=$((i + 1))
        done < <(_wizard_models_for_provider "$provider")
    done

    if [ ${#available_models[@]} -eq 0 ]; then
        print_color "$YELLOW" "   -> No models found in models.json for enabled providers; using default: $default_model"
        TASK_MODEL_MAPPING[$task_type]="$default_model"
        return 0
    fi

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

    if [ "$selection" -ge 1 ] 2>/dev/null && [ "$selection" -lt "$i" ] 2>/dev/null; then
        local selected_model="${available_models[$((selection-1))]}"
        TASK_MODEL_MAPPING[$task_type]="$selected_model"
        print_color "$GREEN" "   -> $task_type: $selected_model"
    else
        print_color "$YELLOW" "   -> Using default: $default_model"
        TASK_MODEL_MAPPING[$task_type]="$default_model"
    fi
}

select_default_model() {
    local i=1
    local available_models=()
    local model_id input_cost output_cost ctx ctx_human

    for provider in "${ENABLED_PROVIDERS[@]}"; do
        while IFS='|' read -r model_id input_cost output_cost ctx; do
            [ -z "$model_id" ] && continue
            available_models+=("$model_id")
            ctx_human="$(_wizard_format_context "$ctx")"
            if [ $i -eq 1 ]; then
                echo "  $i) $model_id (Recommended — \$${input_cost}/\$${output_cost} per 1M, ${ctx_human} ctx)"
            else
                echo "  $i) $model_id (\$${input_cost}/\$${output_cost} per 1M, ${ctx_human} ctx)"
            fi
            i=$((i + 1))
        done < <(_wizard_models_for_provider "$provider")
    done

    if [ ${#available_models[@]} -eq 0 ]; then
        print_color "$YELLOW" "No models found in models.json for enabled providers."
        TASK_MODEL_MAPPING["default"]="claude-sonnet-4-6"
        return 0
    fi

    read -p "Select default model [1-$((i-1))]: " selection

    if [ "$selection" -ge 1 ] 2>/dev/null && [ "$selection" -lt "$i" ] 2>/dev/null; then
        TASK_MODEL_MAPPING["default"]="${available_models[$((selection-1))]}"
        print_color "$GREEN" "Default model: ${available_models[$((selection-1))]}"
    else
        TASK_MODEL_MAPPING["default"]="${available_models[0]}"
        print_color "$GREEN" "Default model: ${available_models[0]}"
    fi
}

ask_model_assignment() {
    if [ "$NON_INTERACTIVE" = true ]; then
        return
    fi

    if [ ${#ENABLED_PROVIDERS[@]} -eq 1 ] || [ "$ORCHESTRATION_MODE" == "none" ]; then
        return
    fi

    if [ "$ORCHESTRATION_MODE" == "solo" ]; then
        print_header "Step 6/7: Default Model Selection"
        echo "Select your default model for all tasks:"
        echo ""
        select_default_model
        return
    fi

    print_header "Step 6/7: Model Assignment per Task Type"

    echo "Assign AI models to specific task types for optimal performance."
    echo ""
    print_color "$YELLOW" "Tip: This optimizes costs and leverages each AI's strengths."
    echo ""

    echo "---"
    print_color "$CYAN" "1. Code Generation & Refactoring"
    echo "   (Writing code, refactoring, implementing features)"
    select_model_for_task "code_generation" "claude-sonnet-4-6"

    if [[ " ${ENABLED_PROVIDERS[*]} " =~ " gemini " ]]; then
        echo ""
        echo "---"
        print_color "$CYAN" "2. Massive Context Analysis"
        echo "   (Reading 100+ files, repository-wide analysis)"
        select_model_for_task "massive_context" "gemini-3.1-pro"
    fi

    echo ""
    echo "---"
    print_color "$CYAN" "3. Documentation & Explanations"
    echo "   (Writing READMEs, docs, code comments)"
    if [[ " ${ENABLED_PROVIDERS[*]} " =~ " openai " ]]; then
        select_model_for_task "documentation" "gpt-5.4"
    else
        select_model_for_task "documentation" "claude-sonnet-4-6"
    fi

    echo ""
    echo "---"
    print_color "$CYAN" "4. Security Analysis & Audits"
    echo "   (Security reviews, vulnerability detection)"
    select_model_for_task "security" "claude-opus-4-6"

    if [ "$ORCHESTRATION_MODE" == "challenger" ]; then
        echo ""
        echo "---"
        print_color "$CYAN" "5. Challenger Model"
        echo "   (Reviews and challenges primary model's output)"
        select_model_for_task "challenger" "gemini-3.1-pro"
    fi

    echo ""
    print_color "$GREEN" "Model assignments complete"
}

# ============================================================================
# Step 6: API Keys
# ============================================================================

ask_api_keys() {
    if [ "$NON_INTERACTIVE" = true ]; then
        return
    fi

    print_header "Step 7/7: API Key Configuration"

    echo "Enter API keys for your enabled providers."
    print_color "$YELLOW" "Tip: Keys are stored in .dev-aid/config/.env (gitignored)"
    echo ""

    for provider in "${ENABLED_PROVIDERS[@]}"; do
        case $provider in
            claude)
                print_color "$CYAN" "Claude (Anthropic) authentication"

                # Detect Claude Code session auth so users with Claude Pro/Max
                # subscriptions don't have to enter an additional API key.
                # Three signals (any one is enough):
                #   1. `claude` CLI is on PATH
                #   2. ~/.claude/{config,settings}.json exists
                #   3. ~/.config/claude/config.json exists
                local _claude_session_detected=false
                if command -v claude >/dev/null 2>&1; then
                    _claude_session_detected=true
                elif [ -f "$HOME/.claude/config.json" ] || [ -f "$HOME/.claude/settings.json" ] || [ -f "$HOME/.config/claude/config.json" ]; then
                    _claude_session_detected=true
                fi

                if [ "$_claude_session_detected" = true ]; then
                    echo ""
                    print_color "$GREEN" "✓ Claude Code session detected on this machine."
                    echo "  You can use Dev-AID with your existing Claude Code session"
                    echo "  (no API key needed) — that's the recommended path for"
                    echo "  Claude Pro / Max / Team / Enterprise subscribers."
                    echo ""
                    echo "  Options:"
                    echo "    [s] Use Claude Code session auth (recommended)"
                    echo "    [k] Enter an Anthropic API key instead"
                    echo "    [Enter] Skip for now (you can add a key later)"
                    echo ""
                    read -p "Your choice [s/k/Enter]: " -r _claude_choice
                    case "$_claude_choice" in
                        s|S|"")
                            print_color "$GREEN" "Using Claude Code session auth — no API key collected"
                            ;;
                        k|K)
                            echo "Get your key from: https://console.anthropic.com/"
                            read -sp "ANTHROPIC_API_KEY: " claude_key
                            echo ""
                            if [ -n "$claude_key" ]; then
                                COLLECTED_API_KEYS+=("ANTHROPIC_API_KEY=$claude_key")
                                unset claude_key
                                print_color "$GREEN" "Claude API key saved"
                            else
                                print_color "$YELLOW" "Skipped — to add later, edit .dev-aid/config/.env or run:"
                                print_color "$YELLOW" "  echo 'ANTHROPIC_API_KEY=sk-ant-...' >> .dev-aid/config/.env"
                            fi
                            ;;
                        *)
                            print_color "$YELLOW" "Skipped — Dev-AID will fall back to your Claude Code session at runtime."
                            ;;
                    esac
                    unset _claude_choice _claude_session_detected
                else
                    echo "No Claude Code session detected on this machine."
                    echo "If you have Claude Code installed, log in once with: claude login"
                    echo "Otherwise, get an API key from: https://console.anthropic.com/"
                    echo ""
                    read -sp "ANTHROPIC_API_KEY (Enter to skip): " claude_key
                    echo ""
                    if [ -n "$claude_key" ]; then
                        COLLECTED_API_KEYS+=("ANTHROPIC_API_KEY=$claude_key")
                        unset claude_key
                        print_color "$GREEN" "Claude API key saved"
                    else
                        print_color "$YELLOW" "Skipped — to add later, edit .dev-aid/config/.env or run:"
                        print_color "$YELLOW" "  echo 'ANTHROPIC_API_KEY=sk-ant-...' >> .dev-aid/config/.env"
                    fi
                fi
                echo ""
                ;;
            gemini)
                print_color "$CYAN" "Gemini (Google) authentication"

                # Detect Google ADC (Application Default Credentials) so users
                # who already ran `gcloud auth application-default login` don't
                # have to also enter an API key.
                local _gemini_adc_detected=false
                if [ -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
                    _gemini_adc_detected=true
                elif command -v gemini >/dev/null 2>&1; then
                    _gemini_adc_detected=true
                fi

                if [ "$_gemini_adc_detected" = true ]; then
                    echo ""
                    print_color "$GREEN" "✓ Google ADC / Gemini CLI session detected on this machine."
                    echo "  You can use Dev-AID with your existing Google credentials"
                    echo "  (no API key needed)."
                    echo ""
                    echo "  Options:"
                    echo "    [s] Use existing Google session/ADC (recommended)"
                    echo "    [k] Enter a Google API key instead"
                    echo "    [Enter] Skip for now"
                    echo ""
                    read -p "Your choice [s/k/Enter]: " -r _gemini_choice
                    case "$_gemini_choice" in
                        s|S|"")
                            print_color "$GREEN" "Using Google session/ADC — no API key collected"
                            ;;
                        k|K)
                            echo "Get your key from: https://aistudio.google.com/app/apikey"
                            read -sp "GOOGLE_API_KEY: " gemini_key
                            echo ""
                            if [ -n "$gemini_key" ]; then
                                COLLECTED_API_KEYS+=("GOOGLE_API_KEY=$gemini_key")
                                unset gemini_key
                                print_color "$GREEN" "Gemini API key saved"
                            else
                                print_color "$YELLOW" "Skipped — to add later, edit .dev-aid/config/.env or run:"
                                print_color "$YELLOW" "  echo 'GOOGLE_API_KEY=...' >> .dev-aid/config/.env"
                            fi
                            ;;
                        *)
                            print_color "$YELLOW" "Skipped — Dev-AID will fall back to your Google session at runtime."
                            ;;
                    esac
                    unset _gemini_choice _gemini_adc_detected
                else
                    echo "No Google ADC or Gemini CLI session detected."
                    echo "Run 'gcloud auth application-default login' to set up ADC, OR"
                    echo "get an API key from: https://aistudio.google.com/app/apikey"
                    echo ""
                    read -sp "GOOGLE_API_KEY (Enter to skip): " gemini_key
                    echo ""
                    if [ -n "$gemini_key" ]; then
                        COLLECTED_API_KEYS+=("GOOGLE_API_KEY=$gemini_key")
                        unset gemini_key
                        print_color "$GREEN" "Gemini API key saved"
                    else
                        print_color "$YELLOW" "Skipped — to add later, edit .dev-aid/config/.env or run:"
                        print_color "$YELLOW" "  echo 'GOOGLE_API_KEY=...' >> .dev-aid/config/.env"
                    fi
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
                    unset openai_key
                    print_color "$GREEN" "OpenAI API key saved"
                else
                    print_color "$YELLOW" "Skipped — to add later, edit .dev-aid/config/.env or run:"
                    print_color "$YELLOW" "  echo 'KEY_NAME=your-key-value' >> .dev-aid/config/.env"
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
                    unset openrouter_key
                    print_color "$GREEN" "OpenRouter API key saved"
                else
                    print_color "$YELLOW" "Skipped — to add later, edit .dev-aid/config/.env or run:"
                    print_color "$YELLOW" "  echo 'KEY_NAME=your-key-value' >> .dev-aid/config/.env"
                fi
                echo ""
                ;;
            aimlapi)
                print_color "$CYAN" "AI/ML API Key"
                echo "Get your key from: https://aimlapi.com/?via=dev-aid"
                read -sp "AIMLAPI_API_KEY: " aimlapi_key
                echo ""
                if [ -n "$aimlapi_key" ]; then
                    COLLECTED_API_KEYS+=("AIMLAPI_API_KEY=$aimlapi_key")
                    unset aimlapi_key
                    print_color "$GREEN" "AI/ML API key saved"
                else
                    print_color "$YELLOW" "Skipped — to add later, edit .dev-aid/config/.env or run:"
                    print_color "$YELLOW" "  echo 'KEY_NAME=your-key-value' >> .dev-aid/config/.env"
                fi
                echo ""
                ;;
        esac
    done
}

# ============================================================================
# Config file generation helpers
# ============================================================================

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

# Run the full interactive wizard (steps 1-6)
run_wizard() {
    # Initialize arrays
    ENABLED_PROVIDERS=()
    COLLECTED_API_KEYS=()
    declare -gA TASK_MODEL_MAPPING

    if [ "$NON_INTERACTIVE" = true ]; then
        apply_wizard_defaults
        return
    fi

    show_welcome
    ask_context_budget
    ask_auto_activation
    ask_project_preset
    ask_providers
    ask_orchestration_mode
    ask_model_assignment
    ask_api_keys
}
