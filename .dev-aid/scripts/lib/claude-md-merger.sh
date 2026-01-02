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
    local line_count=$(echo "$custom_content" | grep -c '^' || echo "0")

    if [ "$line_count" -gt 10 ]; then
        echo "$content"  # Return full content as custom
    else
        echo ""  # No significant custom content
    fi
}

# Generate Dev-AID template (simplified version)
# Args: $1: project_root
generate_devaid_template() {
    local project_root="$1"
    local project_name=$(basename "$project_root")

    # Detect tech stack (reuse from reconfigure.sh logic)
    local tech_stack=$(detect_project_tech_stack "$project_root")

    cat <<EOF
# ${project_name} - AI Assistant Context

## Role & Responsibilities

You are an AI assistant helping with the **${project_name}** project. Your role includes:

- Understanding and working within the existing codebase architecture
- Suggesting improvements while respecting project conventions
- Writing clean, maintainable code that follows project standards
- Utilizing the memory bank system for persistent context
- Staying within the configured context budget

## Memory Bank Integration

This project uses Dev-AID's memory bank system for persistent context management:

- **activeContext.md**: Current session context and goals
- **progress.md**: Track milestones and achievements
- **learnings.md**: Document insights and patterns
- **challenges.md**: Record obstacles and solutions

Always reference memory bank files for historical context before making changes.

## Tech Stack

${tech_stack}

## Best Practices

### Code Quality
- Follow existing code style and patterns
- Write self-documenting code with clear naming
- Add comments only where logic isn't self-evident
- Keep functions small and focused

### Development Workflow
- Review memory bank before starting new tasks
- Update progress.md after significant changes
- Document learnings and patterns
- Test changes thoroughly

### Communication
- Be concise and technical
- Focus on facts over speculation
- Explain trade-offs when suggesting alternatives
- Ask clarifying questions when requirements are unclear

## Guidelines

1. **Read before writing**: Always review relevant code before making changes
2. **Respect conventions**: Follow existing patterns and style
3. **Update memory**: Keep memory bank files current
4. **Test thoroughly**: Verify changes work as expected
5. **Document learnings**: Record insights for future reference

---

*This file is managed by Dev-AID. See .dev-aid/docs/CONTEXT-SHARING.md for details.*
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
    echo "$content" | grep -c '^' || echo "0"
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

# Create merged CLAUDE.md
# Args: $1: original_file, $2: project_root, $3: validation_issues_json
create_merged_claude_md() {
    local original_file="$1"
    local project_root="$2"
    local validation_issues="${3:-[]}"

    # Extract custom content
    local custom_content=$(extract_custom_content "$original_file")

    # Generate Dev-AID template
    local devaid_template=$(generate_devaid_template "$project_root")

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
