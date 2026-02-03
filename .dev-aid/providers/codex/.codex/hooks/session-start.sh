#!/usr/bin/env bash
#
# Script: session-start.sh
# Description: Codex CLI SessionStart hook - updates AGENTS.md with relevant skills
# Usage: Called automatically by Codex CLI at session start
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
    [[ -n "${TEMP_AGENTS_MD:-}" ]] && rm -f "$TEMP_AGENTS_MD" 2>/dev/null || true
    exit "$exit_code"
}
trap cleanup EXIT INT TERM

# Configuration
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
readonly ORCHESTRATION_DIR="$PROJECT_ROOT/.dev-aid/orchestration"
readonly SKILLS_DIR="$PROJECT_ROOT/.dev-aid/skills"
readonly AGENTS_MD="$PROJECT_ROOT/.dev-aid/providers/codex/.codex/AGENTS.md"

# Logging function
log_info() {
    echo "🔍 Codex SessionStart: $*"
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

# Update AGENTS.md with selected skills
update_agents_md() {
    local skills="$1"

    # Create temporary file for new AGENTS.md
    TEMP_AGENTS_MD=$(mktemp) || return 1
    chmod 600 "$TEMP_AGENTS_MD"

    # Write header
    cat > "$TEMP_AGENTS_MD" <<'EOF'
# Codex Context - Auto-Generated at Session Start

You are an expert AI coding assistant with access to specialized skills from Dev-AID.

## Active Skills

The following skills have been auto-loaded based on project context:

<!-- AUTO-GENERATED: Don't edit manually -->
EOF

    # Add skill references using Codex's @file syntax
    if [[ -n "$skills" ]]; then
        while IFS= read -r skill; do
            [[ -z "$skill" ]] && continue

            # Try expert directory first, then core, then process
            if [[ -f "$SKILLS_DIR/expert/$skill/SKILL.md" ]]; then
                # Use relative path from AGENTS.md to skill file
                echo "@../../../skills/expert/$skill/SKILL.md" >> "$TEMP_AGENTS_MD"
            elif [[ -f "$SKILLS_DIR/core/$skill/SKILL.md" ]]; then
                echo "@../../../skills/core/$skill/SKILL.md" >> "$TEMP_AGENTS_MD"
            elif [[ -f "$SKILLS_DIR/process/$skill/SKILL.md" ]]; then
                echo "@../../../skills/process/$skill/SKILL.md" >> "$TEMP_AGENTS_MD"
            else
                log_error "Skill file not found: $skill"
            fi
        done <<< "$skills"
    else
        echo "<!-- No skills auto-loaded -->" >> "$TEMP_AGENTS_MD"
    fi

    # Write footer
    cat >> "$TEMP_AGENTS_MD" <<'EOF'
<!-- END AUTO-GENERATED -->

## Project Context

This file is automatically updated at the start of each Codex CLI session based on detected project context.

To manually refresh skills, restart the Codex CLI session or run:
```bash
.dev-aid/providers/codex/.codex/hooks/session-start.sh
```

## Dev-AID Integration

Dev-AID provides:
- **5 Core Skills**: Automated checking (test-runner, linter, type-checker, code-reviewer, secret-scanner)
- **73 Expert Skills**: Domain expertise (DevSecOps, TDD, API design, databases, etc.)
- **7 Process Skills**: Behavioral protocols (TDD, verification, systematic debugging)
- **Multi-AI Router**: Challenger mode, ensemble routing, cost optimization
- **Local RAG**: 100% private semantic code search ($0 forever)

Skills are loaded via symlinks - the same skills work across Claude Code, Gemini CLI, and Codex CLI.

## Skill Reference Syntax

Codex uses the `@file` syntax to include external content:
- `@path/to/file.md` - Include entire file
- Skills are organized in: core/, expert/, process/

For more information, see: https://developers.openai.com/codex/guides/agents-md
EOF

    # Ensure AGENTS.md directory exists
    local agents_md_dir
    agents_md_dir="$(dirname "$AGENTS_MD")"
    mkdir -p "$agents_md_dir"

    # Move temporary file to final location
    mv "$TEMP_AGENTS_MD" "$AGENTS_MD" || {
        log_error "Failed to update AGENTS.md"
        return 1
    }

    log_success "Updated AGENTS.md with selected skills"
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
        log_info "No specific context detected, creating minimal AGENTS.md"
        update_agents_md "" || exit 1
        exit 0
    fi

    log_info "Context detected: ${context:0:100}..."

    # Select relevant skills based on context
    local skills
    skills=$("$ORCHESTRATION_DIR/select-skills.sh" "$context" 5 2>/dev/null) || {
        log_error "Failed to select skills"
        exit 1
    }

    # Update AGENTS.md with selected skills
    if ! update_agents_md "$skills"; then
        log_error "Failed to update AGENTS.md"
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
        log_info "AGENTS.md has been updated and will be loaded with every prompt"
    else
        log_info "No highly relevant skills found for current context"
    fi
}

# Run main function
main
