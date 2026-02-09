#!/usr/bin/env bash
#
# Script: session-start.sh
# Description: Codex CLI SessionStart hook - updates AGENTS.md with relevant skills
# Usage: Called automatically by Codex CLI at session start
#
# Architecture:
#   1. Reads AGENTS.md.template (source of truth with all triggers + guidelines)
#   2. Replaces the <!-- AUTO-GENERATED SKILLS START/END --> block with
#      dynamically selected skill @file references
#   3. Writes the result as .codex/AGENTS.md
#   Falls back to minimal from-scratch generation if template is missing.

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
readonly CODEX_PROVIDER_DIR="$PROJECT_ROOT/.dev-aid/providers/codex"
readonly AGENTS_MD_TEMPLATE="$CODEX_PROVIDER_DIR/AGENTS.md.template"
readonly AGENTS_MD="$CODEX_PROVIDER_DIR/.codex/AGENTS.md"

# Markers for the auto-generated skills block
readonly MARKER_START="<!-- AUTO-GENERATED SKILLS START -->"
readonly MARKER_END="<!-- AUTO-GENERATED SKILLS END -->"

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

# Build the skill @file references block from a newline-separated skill list
build_skill_refs() {
    local skills="$1"
    local refs=""

    if [[ -z "$skills" ]]; then
        echo "<!-- No skills auto-loaded for current project context -->"
        return
    fi

    while IFS= read -r skill; do
        [[ -z "$skill" ]] && continue

        # Try expert directory first, then core, then process
        if [[ -f "$SKILLS_DIR/expert/$skill/SKILL.md" ]]; then
            refs+="@../../../skills/expert/$skill/SKILL.md"$'\n'
        elif [[ -f "$SKILLS_DIR/core/$skill/SKILL.md" ]]; then
            refs+="@../../../skills/core/$skill/SKILL.md"$'\n'
        elif [[ -f "$SKILLS_DIR/process/$skill/SKILL.md" ]]; then
            refs+="@../../../skills/process/$skill/SKILL.md"$'\n'
        else
            log_error "Skill file not found: $skill"
        fi
    done <<< "$skills"

    # Trim trailing newline
    printf '%s' "$refs" | sed '/^$/d'
}

# Update AGENTS.md using the template (preferred path)
update_agents_md_from_template() {
    local skills="$1"

    if [[ ! -f "$AGENTS_MD_TEMPLATE" ]]; then
        return 1  # Signal caller to use fallback
    fi

    # Build the skill references block
    local skill_block
    skill_block=$(build_skill_refs "$skills")

    # Create temporary file
    TEMP_AGENTS_MD=$(mktemp) || return 1
    chmod 600 "$TEMP_AGENTS_MD"

    # Read template and replace the marker block with dynamic skills
    local in_marker_block=false
    local marker_found=false

    while IFS= read -r line || [[ -n "$line" ]]; do
        if [[ "$line" == "$MARKER_START" ]]; then
            in_marker_block=true
            marker_found=true
            # Write the start marker
            echo "$line" >> "$TEMP_AGENTS_MD"
            # Write a comment noting when skills were injected
            echo "<!-- Updated by session-start.sh at $(date -u '+%Y-%m-%dT%H:%M:%SZ') -->" >> "$TEMP_AGENTS_MD"
            echo "" >> "$TEMP_AGENTS_MD"
            # Write the dynamic skill references
            echo "$skill_block" >> "$TEMP_AGENTS_MD"
            echo "" >> "$TEMP_AGENTS_MD"
            continue
        fi

        if [[ "$line" == "$MARKER_END" ]]; then
            in_marker_block=false
            echo "$line" >> "$TEMP_AGENTS_MD"
            continue
        fi

        # Skip lines inside the marker block (they get replaced)
        if $in_marker_block; then
            continue
        fi

        echo "$line" >> "$TEMP_AGENTS_MD"
    done < "$AGENTS_MD_TEMPLATE"

    if ! $marker_found; then
        log_error "Template is missing $MARKER_START / $MARKER_END markers"
        rm -f "$TEMP_AGENTS_MD"
        return 1
    fi

    # Ensure output directory exists
    mkdir -p "$(dirname "$AGENTS_MD")"

    # Move temporary file to final location
    mv "$TEMP_AGENTS_MD" "$AGENTS_MD" || {
        log_error "Failed to update AGENTS.md"
        return 1
    }

    log_success "Updated AGENTS.md from template with selected skills"
    return 0
}

# Fallback: generate minimal AGENTS.md from scratch (no template)
update_agents_md_minimal() {
    local skills="$1"

    TEMP_AGENTS_MD=$(mktemp) || return 1
    chmod 600 "$TEMP_AGENTS_MD"

    # Build skill references
    local skill_block
    skill_block=$(build_skill_refs "$skills")

    cat > "$TEMP_AGENTS_MD" <<EOF
# Codex Context - Auto-Generated at Session Start

You are an expert AI coding assistant with access to specialized skills from Dev-AID.

## Active Skills

The following skills have been auto-loaded based on project context:

$MARKER_START
$skill_block
$MARKER_END

## Project Context

This file is automatically generated because AGENTS.md.template was not found.
To get the full experience (agent triggers, team workflows, utility commands),
ensure AGENTS.md.template exists at:
  $AGENTS_MD_TEMPLATE

To manually refresh skills, restart the Codex CLI session or run:
\`\`\`bash
.dev-aid/providers/codex/.codex/hooks/session-start.sh
\`\`\`

## Dev-AID Integration

Dev-AID provides:
- **5 Core Skills**: Automated checking (test-runner, linter, type-checker, code-reviewer, secret-scanner)
- **73 Expert Skills**: Domain expertise (DevSecOps, TDD, API design, databases, etc.)
- **7 Process Skills**: Behavioral protocols (TDD, verification, systematic debugging)
- **Multi-AI Router**: Challenger mode, ensemble routing, cost optimization
- **Local RAG**: 100% private semantic code search (\$0 forever)

For more information, see: https://github.com/Probably-Group/Dev-AID
EOF

    mkdir -p "$(dirname "$AGENTS_MD")"

    mv "$TEMP_AGENTS_MD" "$AGENTS_MD" || {
        log_error "Failed to update AGENTS.md"
        return 1
    }

    log_success "Updated AGENTS.md (minimal — template not found)"
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

    # Select skills (empty string if no context)
    local skills=""
    if [[ -n "$context" ]]; then
        log_info "Context detected: ${context:0:100}..."
        skills=$("$ORCHESTRATION_DIR/select-skills.sh" "$context" 5 2>/dev/null) || {
            log_error "Failed to select skills"
            exit 1
        }
    else
        log_info "No specific context detected, using default skills"
    fi

    # Try template-based generation first, fall back to minimal
    if ! update_agents_md_from_template "$skills"; then
        log_info "Template not found at $AGENTS_MD_TEMPLATE, using minimal fallback"
        if ! update_agents_md_minimal "$skills"; then
            log_error "Failed to update AGENTS.md"
            exit 1
        fi
    fi

    # Display auto-loaded skills
    if [[ -n "$skills" ]]; then
        log_success "Auto-loaded skills for this session:"
        while IFS= read -r skill; do
            [[ -z "$skill" ]] && continue
            echo "   📚 $skill"
        done <<< "$skills"
        echo ""
    else
        log_info "No highly relevant skills found for current context"
    fi

    # Report file size (Codex has a 32 KiB limit)
    if [[ -f "$AGENTS_MD" ]]; then
        local size
        size=$(wc -c < "$AGENTS_MD" | tr -d ' ')
        local limit=32768
        if [[ "$size" -gt "$limit" ]]; then
            log_error "AGENTS.md is ${size} bytes — exceeds Codex 32 KiB limit!"
        else
            log_info "AGENTS.md: ${size} bytes (limit: ${limit})"
        fi
    fi
}

# Run main function
main
