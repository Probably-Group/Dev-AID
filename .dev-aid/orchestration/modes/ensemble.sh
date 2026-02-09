#!/usr/bin/env bash

# Dev-AID Ensemble Mode
# Multiple models collaborate based on task capabilities

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_AID_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CONFIG_DIR="$DEV_AID_ROOT/.dev-aid/config"

# Determine best model for task
route_by_capability() {
    local task_type="${1:-general}"
    local context_size="${2:-0}"
    local keywords="${3:-}"

    # Massive context tasks → Gemini
    if [ "$context_size" -gt 100000 ] || \
       printf '%s\n' "$keywords" | grep -qiE "(analyze entire|read all files|repository-wide)"; then
        echo "gemini-2.0-flash"
        return
    fi

    # Code generation tasks → Claude
    if printf '%s\n' "$task_type" | grep -qiE "(code|refactor|implement|fix)"; then
        echo "claude-sonnet-4.5"
        return
    fi

    # Documentation tasks → OpenAI
    if printf '%s\n' "$task_type" | grep -qiE "(docs|readme|comments|explain)"; then
        echo "gpt-4o"
        return
    fi

    # Security tasks → Claude
    if printf '%s\n' "$keywords" | grep -qiE "(security|audit|vulnerability|owasp)"; then
        echo "claude-sonnet-4.5"
        return
    fi

    # Quick tasks → Haiku or GPT-3.5
    if printf '%s\n' "$keywords" | grep -qiE "(quick|simple|fast)"; then
        echo "claude-haiku-4"
        return
    fi

    # Default to Claude
    echo "claude-sonnet-4.5"
}

# Check if model is enabled
is_model_enabled() {
    local model="$1"

    # Extract provider from model name
    local provider=""
    case "$model" in
        claude-*) provider="claude" ;;
        gemini-*) provider="gemini" ;;
        gpt-*) provider="openai" ;;
        *) provider="unknown" ;;
    esac

    if [ "$provider" == "unknown" ]; then
        return 1
    fi

    # Check if provider is enabled
    if command -v jq &> /dev/null; then
        local enabled=$(jq -r --arg p "$provider" '.[$p].enabled' "$CONFIG_DIR/models.json")
        [ "$enabled" == "true" ]
    else
        # Fallback: grep for enabled status
        grep -qF "\"${provider}\"" "$CONFIG_DIR/models.json" && grep -q '"enabled": *true' "$CONFIG_DIR/models.json"
    fi
}

# Get fallback model for capability
get_fallback_model() {
    local capability="$1"

    case "$capability" in
        massive_context)
            echo "claude-sonnet-4.5"
            ;;
        code_generation)
            echo "gpt-4o"
            ;;
        documentation)
            echo "claude-sonnet-4.5"
            ;;
        *)
            echo "claude-sonnet-4.5"
            ;;
    esac
}

# Ensemble mode main logic
ensemble_mode() {
    local task_type="${1:-general}"
    local context_size="${2:-0}"
    local keywords="${3:-}"

    echo "🎭 Ensemble Mode: Capability-Based Routing"
    echo ""

    # Determine best model
    local selected_model=$(route_by_capability "$task_type" "$context_size" "$keywords")

    # Check if model is enabled
    if is_model_enabled "$selected_model"; then
        echo "✅ Selected Model: $selected_model"
        echo "   Reason: Best suited for this task type"
        echo ""
        echo "   Task Type: $task_type"
        echo "   Context Size: $context_size tokens"
        if [ -n "$keywords" ]; then
            echo "   Keywords: $keywords"
        fi
    else
        echo "⚠️  Preferred Model: $selected_model (NOT ENABLED)"

        # Determine capability
        local capability=""
        case "$selected_model" in
            gemini-*) capability="massive_context" ;;
            gpt-*) capability="documentation" ;;
            *) capability="code_generation" ;;
        esac

        # Get fallback
        local fallback=$(get_fallback_model "$capability")
        echo "   Fallback Model: $fallback"
        echo ""
        echo "   💡 Tip: Enable $selected_model in .dev-aid/config/models.json"
        echo "           for optimal performance on this task type."
    fi

    echo ""
    echo "📋 Capability Matrix:"
    echo "   • Massive Context (100K+ tokens) → Gemini 2.0 Flash"
    echo "   • Code Generation              → Claude Sonnet 4.5"
    echo "   • Documentation                → GPT-4o"
    echo "   • Security Analysis            → Claude Sonnet 4.5"
    echo "   • Quick Tasks                  → Claude Haiku / GPT-3.5"
    echo ""
}

# Main execution
main() {
    local task_type="${1:-general}"
    local context_size="${2:-0}"
    local keywords="${3:-}"

    ensemble_mode "$task_type" "$context_size" "$keywords"
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
