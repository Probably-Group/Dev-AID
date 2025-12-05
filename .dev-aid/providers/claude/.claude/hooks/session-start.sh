#!/usr/bin/env bash
#
# Script: session-start.sh
# Description: Claude Code SessionStart hook - auto-loads relevant skills based on project context
# Usage: Called automatically by Claude Code at session start
#

# Strict mode: exit on error, undefined variables, pipe failures
set -euo pipefail

# Script directory (portable way)
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Cleanup function (always runs on exit)
cleanup() {
    local exit_code=$?
    # No cleanup needed for this hook
    exit "$exit_code"
}
trap cleanup EXIT INT TERM

# Configuration
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
readonly ORCHESTRATION_DIR="$PROJECT_ROOT/.dev-aid/orchestration"
readonly SKILLS_DIR="$PROJECT_ROOT/.dev-aid/skills"

# Logging function
log_info() {
    echo "🔍 Claude SessionStart: $*"
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
        log_info "No specific context detected, skipping skill auto-load"
        exit 0
    fi

    log_info "Context detected: ${context:0:100}..."

    # Select relevant skills based on context
    local skills
    skills=$("$ORCHESTRATION_DIR/select-skills.sh" "$context" 5 2>/dev/null) || {
        log_error "Failed to select skills"
        exit 1
    }

    # Display auto-loaded skills
    if [[ -n "$skills" ]]; then
        log_success "Auto-loading skills based on context:"
        while IFS= read -r skill; do
            [[ -z "$skill" ]] && continue
            # Verify skill file exists
            local skill_file="$SKILLS_DIR/expert/$skill/SKILL.md"
            if [[ ! -f "$skill_file" ]]; then
                # Try other skill directories
                skill_file="$SKILLS_DIR/core/$skill/SKILL.md"
            fi
            if [[ -f "$skill_file" ]]; then
                echo "   📚 $skill"
            else
                echo "   ⚠️  $skill (file not found)"
            fi
        done <<< "$skills"

        echo ""
        log_info "Skills are available for activation when needed"
    else
        log_info "No highly relevant skills found for current context"
    fi
}

# Run main function
main
