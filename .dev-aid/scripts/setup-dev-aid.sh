#!/usr/bin/env bash
# Dev-AID Unified Setup Script
# Single entry point for complete Dev-AID initialization.
#
# Usage:
#   ./setup-dev-aid.sh                    # Full interactive setup
#   ./setup-dev-aid.sh --yes              # Non-interactive with defaults
#   ./setup-dev-aid.sh --minimal          # Skip infrastructure (Phase 7)
#   ./setup-dev-aid.sh --infrastructure-only  # Phases 1,2,4,7,8 (backward compat)
#   ./setup-dev-aid.sh --wizard-only          # Phases 3,4,5,6,8 (backward compat)
#
# Phases:
#   1. Prerequisites      — check/install required tools
#   2. Directory structure — create .dev-aid subdirectories
#   3. Interactive wizard  — provider/model/orchestration choices
#   4. Config files        — routing.json, models.json, settings.json, .env
#   5. Context files       — CLAUDE.md, GEMINI.md, provider dirs, hooks, symlinks
#   6. Memory bank         — verify template files, update project name
#   7. Infrastructure      — router venv, RAG, security tools, git hooks
#   8. Validation          — compliance scan + summary

set -euo pipefail

# ============================================================================
# Resolve paths
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_AID_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(cd "$DEV_AID_DIR/.." && pwd)"

# Validate PROJECT_ROOT is not a system directory
_validate_project_root() {
    local resolved
    resolved="$(cd "$PROJECT_ROOT" && pwd)"
    local unsafe_paths=("/" "/etc" "/usr" "/bin" "/sbin" "/boot" "/sys" "/proc" "/dev")
    for unsafe_path in "${unsafe_paths[@]}"; do
        if [[ "$resolved" == "$unsafe_path" ]] || [[ "$resolved" == "$unsafe_path"/* ]]; then
            echo "Error: PROJECT_ROOT points to a system directory: $resolved"
            exit 1
        fi
    done
}
_validate_project_root

# ============================================================================
# Colors
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ============================================================================
# Parse flags
# ============================================================================

NON_INTERACTIVE=false
MINIMAL=false
INFRASTRUCTURE_ONLY=false
WIZARD_ONLY=false

# Initialize arrays that wizard-functions.sh populates
ENABLED_PROVIDERS=()
COLLECTED_API_KEYS=()
STANDING_CONTEXT_BUDGET=""
STANDING_CONTEXT_TOKENS=""
AUTO_ACTIVATION=""
ORCHESTRATION_MODE=""
SELECTED_PRESET=""
SELECTED_PRESET_PATH=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --yes|-y)
            NON_INTERACTIVE=true
            shift
            ;;
        --minimal)
            MINIMAL=true
            shift
            ;;
        --infrastructure-only)
            INFRASTRUCTURE_ONLY=true
            shift
            ;;
        --wizard-only)
            WIZARD_ONLY=true
            shift
            ;;
        -h|--help)
            echo "Usage: $(basename "$0") [OPTIONS]"
            echo ""
            echo "Unified Dev-AID setup — initializes everything in one pass."
            echo ""
            echo "Options:"
            echo "  --yes, -y              Non-interactive mode (apply defaults, no prompts)"
            echo "  --minimal              Skip infrastructure setup (Phase 7)"
            echo "  --infrastructure-only  Run only Phases 1,2,4,7,8 (backward compat for init-repo.sh)"
            echo "  --wizard-only          Run only Phases 3,4,5,6,8 (backward compat for install.sh)"
            echo "  -h, --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ============================================================================
# Source libraries
# ============================================================================

LIB_DIR="$SCRIPT_DIR/lib"

# shellcheck source=/dev/null
source "$LIB_DIR/detection.sh"

# shellcheck source=/dev/null
source "$LIB_DIR/wizard-functions.sh"

# shellcheck source=/dev/null
source "$LIB_DIR/provider-setup.sh"

# shellcheck source=/dev/null
source "$LIB_DIR/preset-functions.sh"

# shellcheck source=/dev/null
source "$LIB_DIR/prd-functions.sh"

# Source shared security library if available
if [[ -f "$DEV_AID_DIR/lib/bash-common.sh" ]]; then
    # shellcheck source=/dev/null
    source "$DEV_AID_DIR/lib/bash-common.sh"
fi

# Temp files tracking for cleanup
declare -a TEMP_FILES=()
cleanup() {
    local exit_code=$?
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

# ============================================================================
# Phase helpers
# ============================================================================

# Determine which phases to run based on flags
should_run_phase() {
    local phase="$1"

    if [ "$INFRASTRUCTURE_ONLY" = true ]; then
        case "$phase" in
            1|2|4|7|8) return 0 ;;
            *) return 1 ;;
        esac
    fi

    if [ "$WIZARD_ONLY" = true ]; then
        case "$phase" in
            3|4|5|6|8) return 0 ;;
            *) return 1 ;;
        esac
    fi

    # Phase 7 (infrastructure) skipped with --minimal
    if [ "$MINIMAL" = true ] && [ "$phase" -eq 7 ]; then
        return 1
    fi

    return 0
}

# ============================================================================
# Banner
# ============================================================================

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Dev-AID Unified Setup                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Detect existing state
detect_project_state "$PROJECT_ROOT"

if is_fresh_install; then
    echo -e "${CYAN}Mode: Fresh installation${NC}"
else
    echo -e "${CYAN}Mode: Re-initialization / repair${NC}"
    if [ "$NON_INTERACTIVE" = false ]; then
        print_state_summary
    fi
fi

# Load existing settings as wizard defaults (for re-init)
if [ "$STATE_HAS_SETTINGS_JSON" = true ]; then
    load_existing_settings "$DEV_AID_DIR/config/settings.json" || true
fi

echo ""

# ============================================================================
# Phase 1: Prerequisites
# ============================================================================

if should_run_phase 1; then
    echo -e "${YELLOW}Phase 1/8: Prerequisites${NC}"
    echo -e "${BLUE}$(printf '%.0s─' {1..50})${NC}"

    if [ -f "$SCRIPT_DIR/check-prerequisites.sh" ]; then
        local_prereq_args=()
        if [ "$NON_INTERACTIVE" = true ]; then
            local_prereq_args+=("--quiet")
        fi
        if ! bash "$SCRIPT_DIR/check-prerequisites.sh" "${local_prereq_args[@]}"; then
            echo ""
            echo -e "${RED}Prerequisite check failed. Please install missing tools and re-run.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}check-prerequisites.sh not found, skipping${NC}"
    fi
    echo ""
fi

# ============================================================================
# Phase 2: Directory Structure
# ============================================================================

if should_run_phase 2; then
    echo -e "${YELLOW}Phase 2/8: Directory Structure${NC}"
    echo -e "${BLUE}$(printf '%.0s─' {1..50})${NC}"

    mkdir -p "$DEV_AID_DIR/logs"
    mkdir -p "$DEV_AID_DIR/config"
    mkdir -p "$DEV_AID_DIR/memory-bank"
    mkdir -p "$DEV_AID_DIR/skills/expert"
    mkdir -p "$DEV_AID_DIR/backups"
    mkdir -p "$DEV_AID_DIR/analysis"
    mkdir -p "$DEV_AID_DIR/temp"
    mkdir -p "$DEV_AID_DIR/agent-traces"
    mkdir -p "$DEV_AID_DIR/agent-prompts"

    echo -e "${GREEN}Directory structure created${NC}"
    echo ""
fi

# ============================================================================
# Phase 3: Interactive Wizard
# ============================================================================

if should_run_phase 3; then
    echo -e "${YELLOW}Phase 3/8: Configuration Wizard${NC}"
    echo -e "${BLUE}$(printf '%.0s─' {1..50})${NC}"

    # Initialize wizard state
    declare -A TASK_MODEL_MAPPING

    run_wizard

    echo ""
fi

# ============================================================================
# Phase 4: Config Files
# ============================================================================

if should_run_phase 4; then
    echo -e "${YELLOW}Phase 4/8: Configuration Files${NC}"
    echo -e "${BLUE}$(printf '%.0s─' {1..50})${NC}"

    # --- routing.json (create if missing) ---
    if [ ! -f "$DEV_AID_DIR/config/routing.json" ]; then
        echo -e "${CYAN}Creating routing.json...${NC}"
        cat > "$DEV_AID_DIR/config/routing.json" << 'EOF'
{
  "default_mode": "solo",
  "modes": {
    "challenger": {
      "enabled": true,
      "primary_model": "claude-sonnet",
      "challenger_model": "gemini-flash",
      "auto_refine_on": ["HIGH", "CRITICAL"],
      "review_triggers": [
        "auth", "authentication", "password", "crypto",
        "encryption", "token", "session", "oauth", "jwt",
        "payment", "financial", "sensitive"
      ]
    },
    "ensemble": {
      "enabled": true,
      "routing_strategy": "semantic",
      "task_routes": {
        "massive_context": "gemini-flash",
        "code_generation": "claude-sonnet",
        "security_audit": "claude-sonnet",
        "documentation": "gpt-4o",
        "debugging": "claude-sonnet",
        "complex_reasoning": "claude-opus"
      }
    }
  },
  "fallback_chain": ["claude-sonnet", "gpt-4o", "gemini-flash"],
  "cost_limit_per_day": 100.0
}
EOF
        echo -e "${GREEN}Created routing.json${NC}"
    else
        echo -e "${GREEN}routing.json already exists${NC}"
    fi

    # --- models.json (create if missing) ---
    if [ ! -f "$DEV_AID_DIR/config/models.json" ]; then
        echo -e "${CYAN}Creating models.json...${NC}"
        cat > "$DEV_AID_DIR/config/models.json" << 'EOF'
{
  "models": {
    "claude-sonnet": {
      "provider": "anthropic",
      "model": "claude-sonnet-4.5-20250929",
      "cost_per_mtok": {"input": 3.0, "output": 15.0},
      "max_context": 200000,
      "strengths": ["code_generation", "security", "reasoning"],
      "description": "Balanced model - best for most code generation"
    },
    "claude-opus": {
      "provider": "anthropic",
      "model": "claude-opus-4",
      "cost_per_mtok": {"input": 15.0, "output": 75.0},
      "max_context": 200000,
      "strengths": ["complex_reasoning", "architecture", "design"],
      "description": "Most capable - for complex tasks"
    },
    "gemini-flash": {
      "provider": "google",
      "model": "gemini-2.0-flash-exp",
      "cost_per_mtok": {"input": 0.075, "output": 0.30},
      "max_context": 2000000,
      "strengths": ["massive_context", "cost_effective", "review"],
      "description": "2M context window - perfect for large codebases"
    },
    "gpt-4o": {
      "provider": "openai",
      "model": "gpt-4o-2024-11-20",
      "cost_per_mtok": {"input": 2.5, "output": 10.0},
      "max_context": 128000,
      "strengths": ["documentation", "explanation", "balanced"],
      "description": "Good all-rounder"
    }
  }
}
EOF
        echo -e "${GREEN}Created models.json${NC}"
    else
        echo -e "${GREEN}models.json already exists${NC}"
    fi

    # --- settings.json (always overwrite with wizard output) ---
    # Only write if wizard was run (Phase 3)
    if [ -n "${ORCHESTRATION_MODE:-}" ]; then
        echo -e "${CYAN}Writing settings.json...${NC}"
        cat > "$DEV_AID_DIR/config/settings.json" << EOF
{
  "dev_aid_version": "2.0.0",
  "project_name": "$(basename "$PROJECT_ROOT")",
  "installed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",

  "project_preset": "${SELECTED_PRESET:-}",

  "standing_context_budget": "${STANDING_CONTEXT_BUDGET:-balanced}",
  "standing_context_tokens": ${STANDING_CONTEXT_TOKENS:-1000},

  "auto_activation": "${AUTO_ACTIVATION:-conservative}",
  "auto_load_max_skills": 3,

  "orchestration_mode": "${ORCHESTRATION_MODE:-solo}",

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
        echo -e "${GREEN}Created settings.json${NC}"
    fi

    # --- .env (protect existing) ---
    if [ ! -f "$DEV_AID_DIR/config/.env" ]; then
        echo -e "${CYAN}Creating .env...${NC}"
        touch "$DEV_AID_DIR/config/.env"
        chmod 600 "$DEV_AID_DIR/config/.env"
        cat > "$DEV_AID_DIR/config/.env" << 'EOF'
# Dev-AID API Keys
# This file is gitignored for security
# Add your API keys below:
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=...
# OPENAI_API_KEY=sk-...
# OPENROUTER_API_KEY=sk-or-...
EOF
        chmod 600 "$DEV_AID_DIR/config/.env"

        # Append collected API keys if any
        if [ ${#COLLECTED_API_KEYS[@]} -gt 0 ]; then
            printf '\n%s\n' "${COLLECTED_API_KEYS[@]}" >> "$DEV_AID_DIR/config/.env"
            chmod 600 "$DEV_AID_DIR/config/.env"
        fi

        echo -e "${GREEN}Created .env (permissions: 600)${NC}"
    else
        echo -e "${GREEN}.env already exists (preserved)${NC}"
        # Append new keys if collected (interactive re-init)
        if [ ${#COLLECTED_API_KEYS[@]} -gt 0 ] && [ "$NON_INTERACTIVE" = false ]; then
            echo ""
            echo -e "${YELLOW}You entered new API keys. Existing .env contains:${NC}"
            echo "  $(wc -l < "$DEV_AID_DIR/config/.env") lines"
            read -p "Append new keys to existing .env? [y/N]: " append_keys
            if [[ "$append_keys" =~ ^[Yy]$ ]]; then
                printf '\n%s\n' "${COLLECTED_API_KEYS[@]}" >> "$DEV_AID_DIR/config/.env"
                chmod 600 "$DEV_AID_DIR/config/.env"
                echo -e "${GREEN}API keys appended${NC}"
            fi
        fi
    fi

    # --- orchestration.json (update mode if exists) ---
    if [ -f "$DEV_AID_DIR/config/orchestration.json" ] && [ -n "${ORCHESTRATION_MODE:-}" ]; then
        echo -e "${CYAN}Updating orchestration.json...${NC}"
        if command -v jq &>/dev/null; then
            jq ".mode = \"${ORCHESTRATION_MODE}\"" \
                "$DEV_AID_DIR/config/orchestration.json" > "$DEV_AID_DIR/config/orchestration.json.tmp"
            mv "$DEV_AID_DIR/config/orchestration.json.tmp" "$DEV_AID_DIR/config/orchestration.json"
        else
            sed -i.bak "s/\"mode\": \".*\"/\"mode\": \"${ORCHESTRATION_MODE}\"/" \
                "$DEV_AID_DIR/config/orchestration.json" 2>/dev/null || true
            rm -f "$DEV_AID_DIR/config/orchestration.json.bak"
        fi
        echo -e "${GREEN}Updated orchestration.json${NC}"
    fi

    # --- .gitignore (create if missing) ---
    if [ ! -f "$DEV_AID_DIR/.gitignore" ]; then
        echo -e "${CYAN}Creating .gitignore...${NC}"
        cat > "$DEV_AID_DIR/.gitignore" << 'EOF'
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
        echo -e "${GREEN}Created .gitignore${NC}"
    fi

    echo ""
fi

# ============================================================================
# Phase 5: Context Files + Provider Setup
# ============================================================================

if should_run_phase 5; then
    echo -e "${YELLOW}Phase 5/8: Provider Setup & Context Files${NC}"
    echo -e "${BLUE}$(printf '%.0s─' {1..50})${NC}"

    # Use ENABLED_PROVIDERS from wizard, or default to claude
    if [ ${#ENABLED_PROVIDERS[@]} -eq 0 ]; then
        ENABLED_PROVIDERS=("claude")
    fi

    setup_all_providers "$PROJECT_ROOT" "$NON_INTERACTIVE"

    # Apply preset rules, smoke tests, lint hook, and docs
    if [[ -n "${SELECTED_PRESET:-}" ]]; then
        echo ""
        echo -e "${CYAN}Applying preset: ${SELECTED_PRESET}...${NC}"

        # Load preset if not already loaded (e.g., --yes mode)
        if [[ -z "${preset_name:-}" ]]; then
            load_preset "$SELECTED_PRESET"
        fi

        apply_preset_rules "$PROJECT_ROOT" "${ENABLED_PROVIDERS[@]}"
        apply_preset_smoke_tests "$PROJECT_ROOT"
        apply_preset_docs "$PROJECT_ROOT"
        echo -e "${GREEN}Preset rules, smoke tests, and docs applied${NC}"
    fi

    echo ""
fi

# ============================================================================
# Phase 6: Memory Bank
# ============================================================================

if should_run_phase 6; then
    echo -e "${YELLOW}Phase 6/8: Memory Bank${NC}"
    echo -e "${BLUE}$(printf '%.0s─' {1..50})${NC}"

    local_expected_files=(activeContext.md patterns.md decisions.md security.md performance.md testing.md chaos.md)
    local_missing=()
    for f in "${local_expected_files[@]}"; do
        if [ ! -f "$DEV_AID_DIR/memory-bank/$f" ]; then
            local_missing+=("$f")
        fi
    done

    if [ ${#local_missing[@]} -eq 0 ]; then
        echo -e "${GREEN}All 7 memory bank files present${NC}"
    else
        echo -e "${YELLOW}Missing memory bank files: ${local_missing[*]}${NC}"
        echo "  These should be part of the Dev-AID distribution."
    fi

    # Update project name in activeContext.md
    local_active_context="$DEV_AID_DIR/memory-bank/activeContext.md"
    if [ -f "$local_active_context" ]; then
        if command -v sed &>/dev/null; then
            sed -i.bak "s/\*\*Project\*\*:.*/\*\*Project\*\*: $(basename "$PROJECT_ROOT")/" \
                "$local_active_context" 2>/dev/null || true
            rm -f "${local_active_context}.bak"
        fi
        echo -e "${GREEN}Updated activeContext.md with project name${NC}"
    fi

    # Apply preset memory topics (write_if_missing)
    if [[ -n "${SELECTED_PRESET:-}" ]]; then
        if [[ -z "${preset_name:-}" ]]; then
            load_preset "$SELECTED_PRESET"
        fi
        apply_preset_memory "$PROJECT_ROOT"
        echo -e "${GREEN}Preset memory topics applied${NC}"
    fi

    # --- PRD Check (sub-step of Phase 6) ---
    suggest_prd_mode "$PROJECT_ROOT"
    if [ "$STATE_HAS_PRD" = true ]; then
        echo -e "${GREEN}PRD.md found${NC}"
        echo "  Tip: /dev-aid-prd-validate to check completeness"
    elif [ "$NON_INTERACTIVE" = false ]; then
        case "$SUGGESTED_PRD_MODE" in
            build)
                read -p "No PRD.md found. Create one now? (y/N) " -n 1 -r local_prd_reply
                echo
                if [[ $local_prd_reply =~ ^[Yy]$ ]]; then
                    run_prd_wizard "$PROJECT_ROOT"
                fi
                ;;
            choose)
                echo -e "${YELLOW}No PRD.md found, but code exists.${NC}"
                echo "  Tip: /dev-aid-prd --build to create from scratch"
                echo "  Tip: /dev-aid-prd --reverse-engineer to generate from codebase"
                ;;
            reverse-engineer)
                echo -e "${YELLOW}No PRD.md found.${NC}"
                echo "  Tip: /dev-aid-prd --reverse-engineer to generate from existing code"
                ;;
        esac
    fi

    echo ""
fi

# ============================================================================
# Phase 7: Infrastructure
# ============================================================================

if should_run_phase 7; then
    echo -e "${YELLOW}Phase 7/8: Infrastructure Setup${NC}"
    echo -e "${BLUE}$(printf '%.0s─' {1..50})${NC}"
    echo ""

    INSTALLED_ROUTER=false
    INSTALLED_RAG=false
    INSTALLED_SECURITY=false
    INSTALLED_HOOKS=false

    # --- Router venv ---
    if [ "${ORCHESTRATION_MODE:-solo}" != "none" ]; then
        if [ "$STATE_HAS_ROUTER_VENV" = true ]; then
            echo -e "${GREEN}Router venv already installed${NC}"
            INSTALLED_ROUTER=true
        else
            local_prompt="Setup router with virtual environment?"
            if [ "$NON_INTERACTIVE" = true ]; then
                local_do_it=true
            else
                read -p "$local_prompt (Y/n) " -n 1 -r local_reply
                echo
                local_do_it=false
                if [[ $local_reply =~ ^[Yy]$ ]] || [[ -z $local_reply ]]; then
                    local_do_it=true
                fi
            fi
            if [ "$local_do_it" = true ]; then
                if [ -f "$DEV_AID_DIR/orchestration/setup-venv.sh" ]; then
                    "$DEV_AID_DIR/orchestration/setup-venv.sh" && INSTALLED_ROUTER=true
                else
                    echo -e "${YELLOW}setup-venv.sh not found${NC}"
                fi
            fi
        fi
    fi
    echo ""

    # --- RAG / Local Search ---
    if [ "$STATE_HAS_RAG" = true ]; then
        echo -e "${GREEN}Local search already installed${NC}"
        INSTALLED_RAG=true
    else
        local_prompt="Install Dev-AID Local Search (semantic code search)?"
        if [ "$NON_INTERACTIVE" = true ]; then
            local_do_it=true
        else
            read -p "$local_prompt (Y/n) " -n 1 -r local_reply
            echo
            local_do_it=false
            if [[ $local_reply =~ ^[Yy]$ ]] || [[ -z $local_reply ]]; then
                local_do_it=true
            fi
        fi
        if [ "$local_do_it" = true ]; then
            if [ -f "$SCRIPT_DIR/setup-rag.sh" ]; then
                "$SCRIPT_DIR/setup-rag.sh" && INSTALLED_RAG=true
            else
                echo -e "${YELLOW}setup-rag.sh not found${NC}"
            fi
        fi
    fi
    echo ""

    # --- Security tools ---
    if [ "$STATE_HAS_SECURITY_TOOLS" = true ]; then
        echo -e "${GREEN}Security tools already installed${NC}"
        INSTALLED_SECURITY=true
    else
        local_prompt="Install security scanning tools (Gitleaks, Trivy, Opengrep)?"
        if [ "$NON_INTERACTIVE" = true ]; then
            local_do_it=true
        else
            read -p "$local_prompt (Y/n) " -n 1 -r local_reply
            echo
            local_do_it=false
            if [[ $local_reply =~ ^[Yy]$ ]] || [[ -z $local_reply ]]; then
                local_do_it=true
            fi
        fi
        if [ "$local_do_it" = true ]; then
            if [ -f "$DEV_AID_DIR/automation/tools/install-security-tools.sh" ]; then
                "$DEV_AID_DIR/automation/tools/install-security-tools.sh" && INSTALLED_SECURITY=true
            else
                echo -e "${YELLOW}install-security-tools.sh not found${NC}"
            fi
        fi
    fi
    echo ""

    # --- Git hooks ---
    if [ "$STATE_HAS_GIT_HOOKS" = true ]; then
        echo -e "${GREEN}Git hooks already installed${NC}"
        INSTALLED_HOOKS=true
    else
        local_prompt="Setup git hooks (pre-commit, pre-push)?"
        if [ "$NON_INTERACTIVE" = true ]; then
            local_do_it=true
        else
            read -p "$local_prompt (Y/n) " -n 1 -r local_reply
            echo
            local_do_it=false
            if [[ $local_reply =~ ^[Yy]$ ]] || [[ -z $local_reply ]]; then
                local_do_it=true
            fi
        fi
        if [ "$local_do_it" = true ]; then
            if [ -f "$SCRIPT_DIR/setup-git-hooks.sh" ]; then
                "$SCRIPT_DIR/setup-git-hooks.sh" && INSTALLED_HOOKS=true
            else
                echo -e "${YELLOW}setup-git-hooks.sh not found${NC}"
            fi
        fi
    fi
    echo ""
fi

# ============================================================================
# Phase 8: Validation & Summary
# ============================================================================

if should_run_phase 8; then
    echo -e "${YELLOW}Phase 8/8: Validation & Summary${NC}"
    echo -e "${BLUE}$(printf '%.0s─' {1..50})${NC}"
    echo ""

    # Run compliance scan (non-blocking)
    if [ -f "$SCRIPT_DIR/run-validators.py" ]; then
        echo -e "${CYAN}Running compliance scan...${NC}"
        python3 "$SCRIPT_DIR/run-validators.py" \
            --filter-context --target-dir "$PROJECT_ROOT" 2>/dev/null || true
        echo ""
    fi

    # Summary
    echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║       Dev-AID Setup Complete!              ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
    echo ""

    echo -e "${CYAN}Configuration Summary:${NC}"
    echo ""

    if [ -n "${ORCHESTRATION_MODE:-}" ]; then
        echo "  Context Budget:     ${STANDING_CONTEXT_BUDGET:-balanced}"
        echo "  Auto-Activation:    ${AUTO_ACTIVATION:-conservative}"
        echo "  Orchestration:      ${ORCHESTRATION_MODE:-solo} mode"
        echo "  Enabled Providers:  ${ENABLED_PROVIDERS[*]}"
        if [[ -n "${SELECTED_PRESET:-}" ]]; then
            echo "  Project Preset:     ${SELECTED_PRESET}"
        fi
        echo ""
    fi

    echo -e "${CYAN}Files:${NC}"
    [ -f "$DEV_AID_DIR/config/routing.json" ]  && echo "  routing.json"
    [ -f "$DEV_AID_DIR/config/models.json" ]   && echo "  models.json"
    [ -f "$DEV_AID_DIR/config/settings.json" ] && echo "  settings.json"
    [ -f "$DEV_AID_DIR/config/.env" ]          && echo "  .env (gitignored)"

    for provider in "${ENABLED_PROVIDERS[@]}"; do
        case "$provider" in
            claude) [ -L "$PROJECT_ROOT/CLAUDE.md" ] && echo "  CLAUDE.md (symlink)" ;;
            gemini) [ -L "$PROJECT_ROOT/GEMINI.md" ] && echo "  GEMINI.md (symlink)" ;;
            openai) [ -L "$PROJECT_ROOT/OPENAI.md" ] && echo "  OPENAI.md (symlink)" ;;
        esac
    done
    echo ""

    if should_run_phase 7; then
        echo -e "${CYAN}Infrastructure:${NC}"
        [ "${INSTALLED_ROUTER:-false}" = true ]   && echo "  Router venv"
        [ "${INSTALLED_RAG:-false}" = true ]       && echo "  Local search (RAG)"
        [ "${INSTALLED_SECURITY:-false}" = true ]  && echo "  Security tools"
        [ "${INSTALLED_HOOKS:-false}" = true ]     && echo "  Git hooks"
        echo ""
    fi

    echo -e "${CYAN}Next steps:${NC}"
    echo "  1. Add API keys: .dev-aid/config/.env"
    echo "  2. Review memory bank: .dev-aid/memory-bank/activeContext.md"
    echo "  3. Start coding: claude code"
    echo ""
    echo -e "${CYAN}Reconfigure anytime:${NC}"
    echo "  ./.dev-aid/scripts/setup-dev-aid.sh"
    echo ""
    echo -e "${GREEN}Happy coding with Dev-AID!${NC}"
    echo ""
fi
