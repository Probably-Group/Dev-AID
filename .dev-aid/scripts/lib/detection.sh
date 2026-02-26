#!/usr/bin/env bash
# Dev-AID State Detection Library
# Detects existing project state to enable idempotent re-initialization.
# Sourced by setup-dev-aid.sh — not run directly.

# Note: This script is designed to be sourced. Strict mode should be set by the sourcing script.
# Setting it here as a safety net.
set -euo pipefail

# Detect the full project state and populate global associative arrays.
# Sets: STATE_DIRS, STATE_CONFIGS, STATE_PROVIDERS, STATE_INFRA
detect_project_state() {
    local project_root="$1"
    local dev_aid_dir="$project_root/.dev-aid"

    # --- Directory structure ---
    STATE_DIR_LOGS=false
    STATE_DIR_CONFIG=false
    STATE_DIR_MEMORY=false
    STATE_DIR_SKILLS=false
    STATE_DIR_BACKUPS=false
    STATE_DIR_ANALYSIS=false
    STATE_DIR_TEMP=false

    [ -d "$dev_aid_dir/logs" ]           && STATE_DIR_LOGS=true
    [ -d "$dev_aid_dir/config" ]         && STATE_DIR_CONFIG=true
    [ -d "$dev_aid_dir/memory-bank" ]    && STATE_DIR_MEMORY=true
    [ -d "$dev_aid_dir/skills/expert" ]  && STATE_DIR_SKILLS=true
    [ -d "$dev_aid_dir/backups" ]        && STATE_DIR_BACKUPS=true
    [ -d "$dev_aid_dir/analysis" ]       && STATE_DIR_ANALYSIS=true
    [ -d "$dev_aid_dir/temp" ]           && STATE_DIR_TEMP=true

    # --- Config files ---
    STATE_HAS_ROUTING_JSON=false
    STATE_HAS_MODELS_JSON=false
    STATE_HAS_SETTINGS_JSON=false
    STATE_HAS_ENV=false
    STATE_HAS_ORCHESTRATION_JSON=false
    STATE_HAS_GITIGNORE=false

    [ -f "$dev_aid_dir/config/routing.json" ]       && STATE_HAS_ROUTING_JSON=true
    [ -f "$dev_aid_dir/config/models.json" ]         && STATE_HAS_MODELS_JSON=true
    [ -f "$dev_aid_dir/config/settings.json" ]       && STATE_HAS_SETTINGS_JSON=true
    [ -f "$dev_aid_dir/config/.env" ]                && STATE_HAS_ENV=true
    [ -f "$dev_aid_dir/config/orchestration.json" ]  && STATE_HAS_ORCHESTRATION_JSON=true
    [ -f "$dev_aid_dir/.gitignore" ]                 && STATE_HAS_GITIGNORE=true

    # --- Provider context files ---
    STATE_CLAUDE_SYMLINK=false
    STATE_CLAUDE_FILE=false
    STATE_GEMINI_SYMLINK=false
    STATE_GEMINI_FILE=false
    STATE_OPENAI_SYMLINK=false
    STATE_OPENAI_FILE=false

    if [ -L "$project_root/CLAUDE.md" ]; then
        STATE_CLAUDE_SYMLINK=true
    elif [ -f "$project_root/CLAUDE.md" ]; then
        STATE_CLAUDE_FILE=true
    fi

    if [ -L "$project_root/GEMINI.md" ]; then
        STATE_GEMINI_SYMLINK=true
    elif [ -f "$project_root/GEMINI.md" ]; then
        STATE_GEMINI_FILE=true
    fi

    if [ -L "$project_root/OPENAI.md" ]; then
        STATE_OPENAI_SYMLINK=true
    elif [ -f "$project_root/OPENAI.md" ]; then
        STATE_OPENAI_FILE=true
    fi

    # --- Provider directories ---
    STATE_HAS_CLAUDE_DIR=false
    STATE_HAS_GEMINI_DIR=false
    STATE_HAS_CODEX_DIR=false
    STATE_HAS_CURSOR_DIR=false

    [ -d "$project_root/.claude" ]  && STATE_HAS_CLAUDE_DIR=true
    [ -d "$project_root/.gemini" ]  && STATE_HAS_GEMINI_DIR=true
    [ -d "$project_root/.codex" ]   && STATE_HAS_CODEX_DIR=true
    [ -d "$project_root/.cursor" ]  && STATE_HAS_CURSOR_DIR=true

    # --- Infrastructure ---
    STATE_HAS_ROUTER_VENV=false
    STATE_HAS_RAG=false
    STATE_HAS_SECURITY_TOOLS=false
    STATE_HAS_GIT_HOOKS=false

    [ -d "$dev_aid_dir/orchestration/venv" ]     && STATE_HAS_ROUTER_VENV=true
    [ -d "$dev_aid_dir/local-search" ] && [ -f "$dev_aid_dir/local-search/pyproject.toml" ] && STATE_HAS_RAG=true
    command -v gitleaks &>/dev/null && command -v trivy &>/dev/null && STATE_HAS_SECURITY_TOOLS=true
    [ -f "$project_root/.git/hooks/pre-commit" ] && STATE_HAS_GIT_HOOKS=true

    # --- Preset state ---
    STATE_HAS_PRESET=false
    STATE_PRESET_NAME=""
    STATE_HAS_RULES_DIR=false
    STATE_HAS_PLAN_TEMPLATE=false

    if [ -f "$dev_aid_dir/config/settings.json" ] && command -v jq &>/dev/null; then
        local preset_val
        preset_val="$(jq -r '.project_preset // ""' "$dev_aid_dir/config/settings.json" 2>/dev/null)" || preset_val=""
        if [ -n "$preset_val" ] && [ "$preset_val" != "null" ]; then
            STATE_HAS_PRESET=true
            STATE_PRESET_NAME="$preset_val"
        fi
    fi

    # Check for provider rules directories
    [ -d "$dev_aid_dir/providers/claude/.claude/rules" ] && STATE_HAS_RULES_DIR=true
    [ -d "$dev_aid_dir/providers/gemini/.gemini/rules" ] && STATE_HAS_RULES_DIR=true

    # Check for plan template
    [ -f "$project_root/docs/plans/.plan-template.md" ] && STATE_HAS_PLAN_TEMPLATE=true

    # --- Memory bank ---
    STATE_MEMORY_BANK_COMPLETE=true
    local expected_files=(activeContext.md patterns.md decisions.md security.md performance.md testing.md chaos.md)
    for f in "${expected_files[@]}"; do
        if [ ! -f "$dev_aid_dir/memory-bank/$f" ]; then
            STATE_MEMORY_BANK_COMPLETE=false
            break
        fi
    done
}

# Check if this is a fresh install (no meaningful state exists)
is_fresh_install() {
    if [ "$STATE_HAS_SETTINGS_JSON" = false ] && \
       [ "$STATE_CLAUDE_SYMLINK" = false ] && \
       [ "$STATE_HAS_ROUTING_JSON" = false ]; then
        return 0
    fi
    return 1
}

# Load existing settings.json values as defaults for the wizard
# Sets global variables: EXISTING_* that wizard-functions.sh can use
load_existing_settings() {
    local settings_file="$1"

    if [ ! -f "$settings_file" ]; then
        return 1
    fi

    if ! command -v jq &>/dev/null; then
        return 1
    fi

    EXISTING_CONTEXT_BUDGET="$(jq -r '.standing_context_budget // "balanced"' "$settings_file" 2>/dev/null)" || EXISTING_CONTEXT_BUDGET="balanced"
    EXISTING_AUTO_ACTIVATION="$(jq -r '.auto_activation // "conservative"' "$settings_file" 2>/dev/null)" || EXISTING_AUTO_ACTIVATION="conservative"
    EXISTING_ORCHESTRATION_MODE="$(jq -r '.orchestration_mode // "solo"' "$settings_file" 2>/dev/null)" || EXISTING_ORCHESTRATION_MODE="solo"

    # Read enabled providers as space-separated string
    EXISTING_PROVIDERS="$(jq -r '.enabled_providers // [] | join(" ")' "$settings_file" 2>/dev/null)" || EXISTING_PROVIDERS="claude"

    return 0
}

# Print a summary of detected state
print_state_summary() {
    echo ""
    echo -e "${CYAN:-}Detected project state:${NC:-}"

    # Configs
    local configs_found=0
    [ "$STATE_HAS_SETTINGS_JSON" = true ] && ((configs_found++))
    [ "$STATE_HAS_ROUTING_JSON" = true ]  && ((configs_found++))
    [ "$STATE_HAS_MODELS_JSON" = true ]   && ((configs_found++))
    [ "$STATE_HAS_ENV" = true ]           && ((configs_found++))
    echo "  Config files:    $configs_found/4"

    # Providers
    local providers_found=0
    [ "$STATE_CLAUDE_SYMLINK" = true ] && ((providers_found++))
    [ "$STATE_GEMINI_SYMLINK" = true ] && ((providers_found++))
    echo "  Provider links:  $providers_found configured"

    # Infrastructure
    local infra_found=0
    [ "$STATE_HAS_ROUTER_VENV" = true ]    && ((infra_found++))
    [ "$STATE_HAS_RAG" = true ]            && ((infra_found++))
    [ "$STATE_HAS_SECURITY_TOOLS" = true ] && ((infra_found++))
    [ "$STATE_HAS_GIT_HOOKS" = true ]      && ((infra_found++))
    echo "  Infrastructure:  $infra_found/4"

    # Memory bank
    if [ "$STATE_MEMORY_BANK_COMPLETE" = true ]; then
        echo "  Memory bank:     complete"
    else
        echo "  Memory bank:     incomplete"
    fi
    echo ""
}
