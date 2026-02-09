#!/usr/bin/env bash
# Dev-AID Provider Setup Library
# Creates provider directories, hooks configs, and command symlinks.
# Sourced by setup-dev-aid.sh — not run directly.
#
# Requires: PROJECT_ROOT, DEV_AID_DIR, ENABLED_PROVIDERS[], colors

# ============================================================================
# Provider directory setup
# ============================================================================

# Create the dot-directory for a provider (e.g., .claude/, .gemini/)
# and symlink commands/skills into it.
setup_provider_directory() {
    local provider="$1"
    local project_root="$2"
    local dev_aid_dir="$project_root/.dev-aid"

    case "$provider" in
        claude)
            _setup_claude_dir "$project_root" "$dev_aid_dir"
            ;;
        gemini)
            _setup_gemini_dir "$project_root" "$dev_aid_dir"
            ;;
        openai)
            _setup_codex_dir "$project_root" "$dev_aid_dir"
            ;;
        cursor)
            _setup_cursor_dir "$project_root" "$dev_aid_dir"
            ;;
    esac
}

_setup_claude_dir() {
    local project_root="$1"
    local dev_aid_dir="$2"
    local target_dir="$project_root/.claude"
    local source_dir="$dev_aid_dir/providers/claude/.claude"

    mkdir -p "$target_dir"

    # Symlink commands directory
    if [ -d "$source_dir/commands" ] && [ ! -e "$target_dir/commands" ]; then
        ln -sf "../.dev-aid/providers/claude/.claude/commands" "$target_dir/commands"
        echo -e "  ${GREEN:-}Linked .claude/commands${NC:-}"
    fi

    # Copy hooks.json (not symlink — user may customize)
    if [ -f "$source_dir/hooks.json" ] && [ ! -f "$target_dir/hooks.json" ]; then
        cp "$source_dir/hooks.json" "$target_dir/hooks.json"
        echo -e "  ${GREEN:-}Created .claude/hooks.json${NC:-}"
    fi

    # Copy settings.json
    if [ -f "$source_dir/settings.json" ] && [ ! -f "$target_dir/settings.json" ]; then
        cp "$source_dir/settings.json" "$target_dir/settings.json"
        echo -e "  ${GREEN:-}Created .claude/settings.json${NC:-}"
    fi

    # Symlink hooks scripts directory
    if [ -d "$source_dir/hooks" ] && [ ! -e "$target_dir/hooks" ]; then
        ln -sf "../.dev-aid/providers/claude/.claude/hooks" "$target_dir/hooks"
        echo -e "  ${GREEN:-}Linked .claude/hooks/${NC:-}"
    fi

    # Copy skill-rules.json
    if [ -f "$source_dir/skill-rules.json" ] && [ ! -f "$target_dir/skill-rules.json" ]; then
        cp "$source_dir/skill-rules.json" "$target_dir/skill-rules.json"
        echo -e "  ${GREEN:-}Created .claude/skill-rules.json${NC:-}"
    fi
}

_setup_gemini_dir() {
    local project_root="$1"
    local dev_aid_dir="$2"
    local target_dir="$project_root/.gemini"
    local source_dir="$dev_aid_dir/providers/gemini/.gemini"

    mkdir -p "$target_dir"

    # Symlink commands directory
    if [ -d "$source_dir/commands" ] && [ ! -e "$target_dir/commands" ]; then
        ln -sf "../.dev-aid/providers/gemini/.gemini/commands" "$target_dir/commands"
        echo -e "  ${GREEN:-}Linked .gemini/commands${NC:-}"
    fi

    # Copy hooks.toml
    if [ -f "$source_dir/hooks.toml" ] && [ ! -f "$target_dir/hooks.toml" ]; then
        cp "$source_dir/hooks.toml" "$target_dir/hooks.toml"
        echo -e "  ${GREEN:-}Created .gemini/hooks.toml${NC:-}"
    fi

    # Copy settings.json
    if [ -f "$source_dir/settings.json" ] && [ ! -f "$target_dir/settings.json" ]; then
        cp "$source_dir/settings.json" "$target_dir/settings.json"
        echo -e "  ${GREEN:-}Created .gemini/settings.json${NC:-}"
    fi

    # Symlink hooks scripts directory
    if [ -d "$source_dir/hooks" ] && [ ! -e "$target_dir/hooks" ]; then
        ln -sf "../.dev-aid/providers/gemini/.gemini/hooks" "$target_dir/hooks"
        echo -e "  ${GREEN:-}Linked .gemini/hooks/${NC:-}"
    fi
}

_setup_codex_dir() {
    local project_root="$1"
    local dev_aid_dir="$2"
    local target_dir="$project_root/.codex"

    mkdir -p "$target_dir"

    # Codex uses a simple hooks.json (session-start for update check)
    if [ ! -f "$target_dir/hooks.json" ]; then
        cat > "$target_dir/hooks.json" << 'HOOKS_EOF'
{
  "on_session_start": [
    {
      "command": "./.dev-aid/scripts/check-update-notify.sh --silent",
      "description": "Check for Dev-AID updates (weekly, cached)"
    }
  ],
  "on_stop": [
    {
      "command": "DEV_AID_PROVIDER=codex ./.dev-aid/scripts/save-session-progress.sh",
      "description": "Save session progress for persistence"
    }
  ]
}
HOOKS_EOF
        echo -e "  ${GREEN:-}Created .codex/hooks.json${NC:-}"
    fi
}

_setup_cursor_dir() {
    local project_root="$1"
    local dev_aid_dir="$2"
    local target_dir="$project_root/.cursor"

    mkdir -p "$target_dir"

    # Cursor only needs a rules directory — no hooks system
    if [ ! -d "$target_dir/rules" ]; then
        mkdir -p "$target_dir/rules"
        echo -e "  ${GREEN:-}Created .cursor/rules/${NC:-}"
    fi
}

# ============================================================================
# Context file setup (uses provider-context-init.sh)
# ============================================================================

# Setup context file for a provider. Handles:
# - Missing: create from template
# - Exists as symlink: skip
# - Exists as regular file: smart migration
setup_context_file() {
    local project_root="$1"
    local provider="$2"
    local non_interactive="${3:-false}"

    local context_filename=""
    case "$provider" in
        claude) context_filename="CLAUDE.md" ;;
        gemini) context_filename="GEMINI.md" ;;
        openai) context_filename="OPENAI.md" ;;
        *) return 0 ;;  # OpenRouter etc. — no context file
    esac

    local context_file="$project_root/$context_filename"

    # Already a symlink — skip
    if [ -L "$context_file" ]; then
        echo -e "  ${GREEN:-}$context_filename already configured (symlink)${NC:-}"
        return 0
    fi

    # Source the smart init library if available
    local lib_dir="$project_root/.dev-aid/scripts/lib"
    if [ -f "$lib_dir/provider-context-init.sh" ]; then
        # shellcheck source=/dev/null
        source "$lib_dir/provider-context-init.sh"

        if [ -f "$context_file" ]; then
            # Existing regular file — smart migration
            if [ "$non_interactive" = true ]; then
                # Auto-merge without prompting
                init_context_file "$project_root" "$provider"
            else
                init_context_file_interactive "$project_root" "$provider"
            fi
        else
            # Missing — create from template
            create_new_context_file "$project_root" "$provider"
        fi
    else
        # Fallback: simple symlink
        _setup_simple_symlink "$project_root" "$provider" "$context_filename"
    fi
}

_setup_simple_symlink() {
    local project_root="$1"
    local provider="$2"
    local context_filename="$3"
    local dev_aid_dir="$project_root/.dev-aid"

    if [ -f "$dev_aid_dir/providers/$provider/$context_filename" ]; then
        echo -e "  ${CYAN:-}Creating symlink for $context_filename...${NC:-}"

        # Validate path containment
        local target_file="$project_root/$context_filename"
        if [ -e "$target_file" ] || [ -L "$target_file" ]; then
            local resolved_target_dir resolved_project_root
            resolved_target_dir="$(cd "$(dirname "$target_file")" && pwd)"
            resolved_project_root="$(cd "$project_root" && pwd)"

            if [[ "$resolved_target_dir" == "$resolved_project_root"* ]]; then
                rm -f "$target_file"
            else
                echo -e "  ${RED:-}Error: Path traversal detected for $context_filename${NC:-}"
                return 1
            fi
        fi

        ln -s ".dev-aid/providers/$provider/$context_filename" "$project_root/$context_filename"
        echo -e "  ${GREEN:-}$context_filename -> .dev-aid/providers/$provider/$context_filename${NC:-}"
    fi
}

# ============================================================================
# Setup all enabled providers
# ============================================================================

setup_all_providers() {
    local project_root="$1"
    local non_interactive="${2:-false}"

    echo ""
    echo -e "${CYAN:-}Setting up provider directories and context files...${NC:-}"
    echo ""

    for provider in "${ENABLED_PROVIDERS[@]}"; do
        echo -e "${BLUE:-}Provider: $provider${NC:-}"

        # Create provider directory (.claude/, .gemini/, etc.)
        setup_provider_directory "$provider" "$project_root"

        # Setup context file (CLAUDE.md, GEMINI.md, etc.)
        setup_context_file "$project_root" "$provider" "$non_interactive"

        echo ""
    done
}
