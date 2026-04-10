#!/usr/bin/env bash
# CLAUDE.md Content Merger
# Intelligently merges existing CLAUDE.md with Dev-AID template

set -euo pipefail

# Extract custom sections from existing CLAUDE.md
# Args: $1: claude_md_file
extract_custom_content() {
    local claude_md_file="$1"
    local content=$(cat "$claude_md_file")

    # Remove common Dev-AID sections if they exist
    # This helps identify truly custom content
    local custom_content="$content"

    # Remove known Dev-AID patterns
    custom_content=$(echo "$custom_content" | sed '/^## Memory Bank$/,/^## [^M]/d' || echo "$custom_content")
    custom_content=$(echo "$custom_content" | sed '/^## Dev-AID Integration$/,/^## [^D]/d' || echo "$custom_content")

    # If after removal we have significant content (>10 lines), it's custom
    local line_count=$(echo "$custom_content" | grep -c '^' || true)

    if [ "$line_count" -gt 10 ]; then
        echo "$content"  # Return full content as custom
    else
        echo ""  # No significant custom content
    fi
}

# Generate Dev-AID template (provider-specific)
# Args: $1: project_root, $2: provider (claude, gemini, openai)
generate_devaid_template() {
    local project_root="$1"
    local provider="${2:-claude}"
    local project_name=$(basename "$project_root")

    # Detect tech stack (reuse from reconfigure.sh logic)
    local tech_stack=$(detect_project_tech_stack "$project_root")

    # Generate provider-specific template
    case "$provider" in
        gemini)
            generate_gemini_specific_template "$project_name" "$tech_stack"
            ;;
        openai)
            generate_openai_specific_template "$project_name" "$tech_stack"
            ;;
        *)
            generate_claude_specific_template "$project_name" "$tech_stack"
            ;;
    esac
}

# Claude-specific template
generate_claude_specific_template() {
    local project_name="$1"
    local tech_stack="$2"

    cat <<EOF
# ${project_name} - AI Assistant Context

## Project Knowledge Base

**IMPORTANT**: Before starting work, read the memory-bank files for project conventions:

@.dev-aid/memory-bank/patterns.md - Coding conventions
@.dev-aid/memory-bank/security.md - Security rules
@.dev-aid/memory-bank/decisions.md - Architecture decisions

Optional context (read when relevant):
- \`.dev-aid/memory-bank/activeContext.md\` - Current sprint/focus
- \`.dev-aid/memory-bank/testing.md\` - Testing standards
- \`.dev-aid/memory-bank/performance.md\` - Performance guidelines

> **Note on default content:** Memory-bank files ship with generic Dev-AID
> defaults. Files that still contain the HTML comment
> \`<!-- DEV-AID-DEFAULT-UNCHANGED -->\` at the bottom have NOT been
> customized for this project — treat them as soft guidance, not binding
> conventions. Once the user removes that marker (or edits the file), treat
> the content as authoritative project rules.

## Tech Stack

${tech_stack}

## Core Guidelines

### Code Quality
- Follow patterns defined in \`patterns.md\`
- Write self-documenting code with clear naming
- Keep functions small and focused
- Add comments only where logic isn't self-evident

### Security (Non-negotiable)
- Follow ALL rules in \`security.md\`
- Never hardcode secrets or credentials
- Always validate user input
- Use parameterized queries

### Testing
- Write tests for new functionality
- Follow patterns in \`testing.md\`
- Test edge cases and error conditions

### Architecture
- Check \`decisions.md\` before suggesting architectural changes
- Respect existing ADRs (Architecture Decision Records)
- Propose new ADRs for significant changes

## Workflow

1. **Read first**: Check memory-bank for relevant context
2. **Respect conventions**: Follow established patterns
3. **Implement carefully**: Small, focused changes
4. **Test thoroughly**: Verify changes work
5. **Update context**: Note significant changes in activeContext.md

## Memory Bank Updates

Update the appropriate file when you learn something significant:

| File | Update When |
|------|-------------|
| \`activeContext.md\` | Sprint focus changes, session ends with progress |
| \`patterns.md\` | New coding pattern established |
| \`decisions.md\` | Architecture decision made (add ADR entry) |
| \`security.md\` | Security requirement or vulnerability identified |
| \`testing.md\` | Testing strategy changes |
| \`performance.md\` | Performance baselines change |

**How**: Read the file first. Append under the appropriate section with timestamp:
\`- **YYYY-MM-DD**: [what was learned]\`
Do NOT delete existing content unless explicitly asked.

\`\`\`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⬆ DEV-AID SCAFFOLD INSTRUCTIONS ABOVE
⬇ HOST-PROJECT INSTRUCTIONS BELOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
\`\`\`

> **Scope reminder for AI assistants:** Everything above this divider is
> Dev-AID scaffold guidance (managed by the addon — see
> \`.dev-aid/HOST_PROJECT.md\`). Default to editing host-project files, not
> \`.dev-aid/\` files, unless the user explicitly asks to contribute to
> Dev-AID itself.
EOF
}

# Gemini-specific template
generate_gemini_specific_template() {
    local project_name="$1"
    local tech_stack="$2"

    cat <<EOF
# ${project_name} - Gemini Context

## Project Knowledge Base (READ FIRST)

Before starting work, read these memory-bank files for project conventions:

**Read first**:
- \`.dev-aid/memory-bank/patterns.md\` - Coding conventions and style guide
- \`.dev-aid/memory-bank/security.md\` - Security rules
- \`.dev-aid/memory-bank/decisions.md\` - Architecture decisions (ADRs)

**Read when relevant**:
- \`.dev-aid/memory-bank/activeContext.md\` - Current sprint/focus
- \`.dev-aid/memory-bank/testing.md\` - Testing standards
- \`.dev-aid/memory-bank/performance.md\` - Performance guidelines

> **Note on default content:** Memory-bank files ship with generic Dev-AID
> defaults. Files containing \`<!-- DEV-AID-DEFAULT-UNCHANGED -->\` at the
> bottom have NOT been customized — treat as soft guidance, not binding rules.
> Once the marker is removed, treat as authoritative project conventions.

## Tech Stack

${tech_stack}

## Core Guidelines

### Code Quality
- Follow patterns defined in \`patterns.md\`
- Use your large context to maintain consistency across files
- Write self-documenting code
- Keep functions small and focused

### Security (Non-negotiable)
- Follow ALL rules in \`security.md\`
- Never hardcode secrets
- Always validate input
- Use parameterized queries

### Architecture
- Check \`decisions.md\` before suggesting changes
- Respect existing ADRs
- Propose new ADRs for significant changes

## Workflow

1. **Read memory-bank**: Check for relevant context first
2. **Holistic analysis**: Use large context for full scope
3. **Follow conventions**: Respect established patterns
4. **Implement carefully**: Small, focused changes
5. **Update context**: Note changes in activeContext.md

## Memory Bank Updates

Update the appropriate file when you learn something significant:

| File | Update When |
|------|-------------|
| \`activeContext.md\` | Sprint focus changes, session ends with progress |
| \`patterns.md\` | New coding pattern established |
| \`decisions.md\` | Architecture decision made (add ADR entry) |
| \`security.md\` | Security requirement or vulnerability identified |
| \`testing.md\` | Testing strategy changes |
| \`performance.md\` | Performance baselines change |

**How**: Read the file first. Append under the appropriate section with timestamp:
\`- **YYYY-MM-DD**: [what was learned]\`
Do NOT delete existing content unless explicitly asked.

\`\`\`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⬆ DEV-AID SCAFFOLD INSTRUCTIONS ABOVE
⬇ HOST-PROJECT INSTRUCTIONS BELOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
\`\`\`

> **Scope reminder for AI assistants:** Everything above this divider is
> Dev-AID scaffold guidance (managed by the addon — see
> \`.dev-aid/HOST_PROJECT.md\`). Default to editing host-project files, not
> \`.dev-aid/\` files, unless the user explicitly asks to contribute to
> Dev-AID itself.
EOF
}

# OpenAI-specific template
generate_openai_specific_template() {
    local project_name="$1"
    local tech_stack="$2"

    cat <<EOF
# ${project_name} - OpenAI Context

## Project Knowledge Base (READ FIRST)

Before starting work, read these memory-bank files for project conventions:

**Read first**:
- \`.dev-aid/memory-bank/patterns.md\` - Coding conventions and style guide
- \`.dev-aid/memory-bank/security.md\` - Security rules
- \`.dev-aid/memory-bank/decisions.md\` - Architecture decisions (ADRs)

**Read when relevant**:
- \`.dev-aid/memory-bank/activeContext.md\` - Current sprint/focus
- \`.dev-aid/memory-bank/testing.md\` - Testing standards
- \`.dev-aid/memory-bank/performance.md\` - Performance guidelines

> **Note on default content:** Memory-bank files ship with generic Dev-AID
> defaults. Files containing \`<!-- DEV-AID-DEFAULT-UNCHANGED -->\` at the
> bottom have NOT been customized — treat as soft guidance, not binding rules.
> Once the marker is removed, treat as authoritative project conventions.

## Tech Stack

${tech_stack}

## Core Guidelines

### Code Quality
- Follow patterns defined in \`patterns.md\`
- Write self-documenting code
- Keep functions small and focused

### Security
- Follow rules in \`security.md\`
- Never hardcode secrets
- Always validate input
- Use parameterized queries

### Architecture
- Check \`decisions.md\` before suggesting changes
- Respect existing ADRs
- Propose new ADRs for significant changes

## Workflow

1. **Read memory-bank**: Check for relevant context first
2. **Follow conventions**: Respect established patterns
3. **Implement efficiently**: Use rapid iteration
4. **Test thoroughly**: Verify changes work
5. **Update context**: Note changes in activeContext.md

## Memory Bank Updates

Update the appropriate file when you learn something significant:

| File | Update When |
|------|-------------|
| \`activeContext.md\` | Sprint focus changes, session ends with progress |
| \`patterns.md\` | New coding pattern established |
| \`decisions.md\` | Architecture decision made (add ADR entry) |
| \`security.md\` | Security requirement or vulnerability identified |
| \`testing.md\` | Testing strategy changes |
| \`performance.md\` | Performance baselines change |

**How**: Read the file first. Append under the appropriate section with timestamp:
\`- **YYYY-MM-DD**: [what was learned]\`
Do NOT delete existing content unless explicitly asked.

\`\`\`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⬆ DEV-AID SCAFFOLD INSTRUCTIONS ABOVE
⬇ HOST-PROJECT INSTRUCTIONS BELOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
\`\`\`

> **Scope reminder for AI assistants:** Everything above this divider is
> Dev-AID scaffold guidance (managed by the addon — see
> \`.dev-aid/HOST_PROJECT.md\`). Default to editing host-project files, not
> \`.dev-aid/\` files, unless the user explicitly asks to contribute to
> Dev-AID itself.
EOF
}

# Detect project tech stack (simple version)
# Args: $1: project_root
detect_project_tech_stack() {
    local project_root="$1"
    local stack=""

    # Frontend
    if [ -f "$project_root/package.json" ]; then
        if grep -q '"react"' "$project_root/package.json"; then
            stack+="- Frontend: React\n"
        elif grep -q '"vue"' "$project_root/package.json"; then
            stack+="- Frontend: Vue.js\n"
        elif grep -q '"@angular/core"' "$project_root/package.json"; then
            stack+="- Frontend: Angular\n"
        fi

        if grep -q '"typescript"' "$project_root/package.json"; then
            stack+="- Language: TypeScript\n"
        else
            stack+="- Language: JavaScript\n"
        fi

        if grep -q '"next"' "$project_root/package.json"; then
            stack+="- Framework: Next.js\n"
        fi
    fi

    # Backend
    if [ -f "$project_root/requirements.txt" ] || [ -f "$project_root/setup.py" ]; then
        stack+="- Backend: Python\n"

        if [ -f "$project_root/requirements.txt" ]; then
            if grep -q "django" "$project_root/requirements.txt"; then
                stack+="- Framework: Django\n"
            elif grep -q "flask" "$project_root/requirements.txt"; then
                stack+="- Framework: Flask\n"
            elif grep -q "fastapi" "$project_root/requirements.txt"; then
                stack+="- Framework: FastAPI\n"
            fi
        fi
    fi

    if [ -f "$project_root/go.mod" ]; then
        stack+="- Backend: Go\n"
    fi

    if [ -f "$project_root/Cargo.toml" ]; then
        stack+="- Backend: Rust\n"
    fi

    if [ -f "$project_root/composer.json" ]; then
        stack+="- Backend: PHP\n"
    fi

    # Database
    if [ -f "$project_root/docker-compose.yml" ]; then
        if grep -q "postgres" "$project_root/docker-compose.yml"; then
            stack+="- Database: PostgreSQL\n"
        fi
        if grep -q "mysql" "$project_root/docker-compose.yml"; then
            stack+="- Database: MySQL\n"
        fi
        if grep -q "mongodb" "$project_root/docker-compose.yml"; then
            stack+="- Database: MongoDB\n"
        fi
    fi

    if [ -z "$stack" ]; then
        stack="- To be determined (run 'dev-aid reconfigure' to update)"
    fi

    echo -e "$stack"
}

# Merge custom content into Dev-AID template
# Args: $1: devaid_template, $2: custom_content
merge_content() {
    local devaid_template="$1"
    local custom_content="$2"

    if [ -z "$custom_content" ]; then
        # No custom content, use template as-is
        echo "$devaid_template"
        return
    fi

    # Append custom content to template
    cat <<EOF
$devaid_template

## Custom Project Instructions

The following instructions were preserved from your original CLAUDE.md:

---

$custom_content

---

*Custom instructions end here*
EOF
}

# Apply auto-fixes based on validation issues
# Args: $1: content, $2: validation_issues_json
apply_auto_fixes() {
    local content="$1"
    local issues_json="$2"
    local fixed_content="$content"

    # Parse JSON and apply fixes (simplified version)
    # In a real implementation, this would parse the JSON and apply specific fixes

    # For now, just return content (fixes would be applied by parsing issues)
    echo "$fixed_content"
}

# Count lines in content
# Args: $1: content (string)
count_content_lines() {
    local content="$1"
    echo "$content" | grep -c '^' || true
}

# Remove duplicate sections
# Args: $1: content
remove_duplicates() {
    local content="$1"
    local result=""
    local seen_headers=()
    local current_section=""
    local in_duplicate=false

    while IFS= read -r line; do
        # Check if this is a header
        if [[ "$line" =~ ^#{1,3}[[:space:]] ]]; then
            local header=$(echo "$line" | sed 's/^#* *//')

            # Check if we've seen this header before
            local is_duplicate=false
            for seen in "${seen_headers[@]}"; do
                if [ "$seen" = "$header" ]; then
                    is_duplicate=true
                    break
                fi
            done

            if [ "$is_duplicate" = true ]; then
                in_duplicate=true
                continue
            else
                in_duplicate=false
                seen_headers+=("$header")
                result+="$line\n"
            fi
        else
            if [ "$in_duplicate" = false ]; then
                result+="$line\n"
            fi
        fi
    done <<< "$content"

    echo -e "$result"
}

# Create merged context file
# Args: $1: original_file, $2: project_root, $3: provider, $4: validation_issues_json
create_merged_context() {
    local original_file="$1"
    local project_root="$2"
    local provider="${3:-claude}"
    local validation_issues="${4:-[]}"

    # Extract custom content
    local custom_content=$(extract_custom_content "$original_file")

    # Generate Dev-AID template
    local devaid_template=$(generate_devaid_template "$project_root" "$provider")

    # Merge content
    local merged=$(merge_content "$devaid_template" "$custom_content")

    # Apply auto-fixes if validation issues provided
    if [ "$validation_issues" != "[]" ]; then
        merged=$(apply_auto_fixes "$merged" "$validation_issues")
    fi

    # Remove duplicates
    merged=$(remove_duplicates "$merged")

    # Return merged content
    echo "$merged"
}

# Legacy wrapper for backward compatibility
create_merged_claude_md() {
    create_merged_context "$1" "$2" "claude" "${3:-[]}"
}

# Split content by line count
# Args: $1: content, $2: line_number
split_at_line() {
    local content="$1"
    local line_num="$2"

    local before=$(echo "$content" | head -n "$line_num")
    local after=$(echo "$content" | tail -n +"$((line_num + 1))")

    echo "$before"
    echo "---SPLIT---"
    echo "$after"
}

# Extract section by header
# Args: $1: content, $2: header_name
extract_section() {
    local content="$1"
    local header="$2"

    # Find the section and extract until next same-level header
    local in_section=false
    local result=""

    while IFS= read -r line; do
        if [[ "$line" =~ ^##[[:space:]]$header ]]; then
            in_section=true
            result+="$line\n"
            continue
        fi

        if [ "$in_section" = true ]; then
            # Stop at next ## header
            if [[ "$line" =~ ^##[[:space:]] ]]; then
                break
            fi
            result+="$line\n"
        fi
    done <<< "$content"

    echo -e "$result"
}
