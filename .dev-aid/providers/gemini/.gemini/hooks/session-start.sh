#!/usr/bin/env bash
#
# Script: session-start.sh
# Description: Gemini CLI SessionStart hook - updates GEMINI.md with relevant skills
# Usage: Called automatically by Gemini CLI at session start
#

# Strict mode: exit on error, undefined variables, pipe failures
set -euo pipefail

# Script directory (portable way)
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Cleanup function (always runs on exit)
cleanup() {
    local exit_code=$?
    # Cleanup temporary files if any
    [[ -n "${TEMP_GEMINI_MD:-}" ]] && rm -f "$TEMP_GEMINI_MD" 2>/dev/null || true
    exit "$exit_code"
}
trap cleanup EXIT INT TERM

# Configuration
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
readonly ORCHESTRATION_DIR="$PROJECT_ROOT/.dev-aid/orchestration"
readonly SKILLS_DIR="$PROJECT_ROOT/.dev-aid/skills"
readonly GEMINI_MD="$PROJECT_ROOT/.dev-aid/providers/gemini/.gemini/GEMINI.md"

# Logging function
log_info() {
    echo "🔍 Gemini SessionStart: $*"
}

log_success() {
    echo "✅ $*"
}

log_error() {
    echo "❌ Error: $*" >&2
}

# Validate required scripts exist
validate_dependencies() {
    local -a required_scripts=(
        "$ORCHESTRATION_DIR/detect-context.sh"
        "$ORCHESTRATION_DIR/select-skills.sh"
    )

    for script in "${required_scripts[@]}"; do
        if [[ ! -f "$script" ]]; then
            log_error "Required script not found: $script"
            return 1
        fi
        if [[ ! -x "$script" ]]; then
            log_error "Script is not executable: $script"
            return 1
        fi
    done

    return 0
}

# Update GEMINI.md with selected skills
update_gemini_md() {
    local skills="$1"

    # Create temporary file for new GEMINI.md
    TEMP_GEMINI_MD=$(mktemp) || return 1
    chmod 600 "$TEMP_GEMINI_MD"

    # Write header
    cat > "$TEMP_GEMINI_MD" <<'EOF'
# Gemini Context - Auto-Generated at Session Start

You are JARVIS, an expert AI coding assistant with access to specialized skills.

## Active Skills

The following skills have been auto-loaded based on project context:

<!-- AUTO-GENERATED: Don't edit manually -->
EOF

    # Add skill references
    if [[ -n "$skills" ]]; then
        while IFS= read -r skill; do
            [[ -z "$skill" ]] && continue

            # Try expert directory first, then core
            local skill_file
            if [[ -f "$SKILLS_DIR/expert/$skill/SKILL.md" ]]; then
                # Calculate relative path from GEMINI.md to skill file
                echo "@../../../skills/expert/$skill/SKILL.md" >> "$TEMP_GEMINI_MD"
            elif [[ -f "$SKILLS_DIR/core/$skill/SKILL.md" ]]; then
                echo "@../../../skills/core/$skill/SKILL.md" >> "$TEMP_GEMINI_MD"
            else
                log_error "Skill file not found: $skill"
            fi
        done <<< "$skills"
    else
        echo "<!-- No skills auto-loaded -->" >> "$TEMP_GEMINI_MD"
    fi

    # Write footer
    cat >> "$TEMP_GEMINI_MD" <<'EOF'
<!-- END AUTO-GENERATED -->

## Project Context

This file is automatically updated at the start of each Gemini CLI session based on detected project context.

To manually refresh skills, restart the Gemini CLI session or run:
```bash
.dev-aid/providers/gemini/.gemini/hooks/session-start.sh
```
EOF

    # Ensure GEMINI.md directory exists
    local gemini_md_dir
    gemini_md_dir="$(dirname "$GEMINI_MD")"
    mkdir -p "$gemini_md_dir"

    # Move temporary file to final location
    mv "$TEMP_GEMINI_MD" "$GEMINI_MD" || {
        log_error "Failed to update GEMINI.md"
        return 1
    }

    log_success "Updated GEMINI.md with selected skills"
    return 0
}

# Main hook logic
main() {
    log_info "Analyzing project context..."

    # Validate dependencies
    if ! validate_dependencies; then
        log_error "Hook validation failed"
        exit 1
    fi

    # Detect project context
    local context
    context=$("$ORCHESTRATION_DIR/detect-context.sh" "$PROJECT_ROOT" 2>/dev/null) || {
        log_error "Failed to detect project context"
        exit 1
    }

    # Skip if no context detected
    if [[ -z "$context" ]]; then
        log_info "No specific context detected, creating minimal GEMINI.md"
        update_gemini_md "" || exit 1
        exit 0
    fi

    log_info "Context detected: ${context:0:100}..."

    # Select relevant skills based on context
    local skills
    skills=$("$ORCHESTRATION_DIR/select-skills.sh" "$context" 5 2>/dev/null) || {
        log_error "Failed to select skills"
        exit 1
    }

    # Update GEMINI.md with selected skills
    if ! update_gemini_md "$skills"; then
        log_error "Failed to update GEMINI.md"
        exit 1
    fi

    # Display auto-loaded skills
    if [[ -n "$skills" ]]; then
        log_success "Auto-loaded skills for this session:"
        while IFS= read -r skill; do
            [[ -z "$skill" ]] && continue
            echo "   📚 $skill"
        done <<< "$skills"
        echo ""
        log_info "GEMINI.md has been updated and will be loaded with every prompt"
    else
        log_info "No highly relevant skills found for current context"
    fi
}

# Check for Dev-AID updates (non-blocking, once per day)
check_update() {
    local update_script="$PROJECT_ROOT/.dev-aid/scripts/check-update-notify.sh"
    if [[ -x "$update_script" ]]; then
        local msg
        msg=$("$update_script" "$PROJECT_ROOT" 2>/dev/null) || true
        if [[ -n "$msg" ]]; then
            echo "⬆️  $msg"
        fi
    fi
}

# Run main function
main
check_update
