#!/usr/bin/env bash
# Progressive Disclosure for Large CLAUDE.md Files
# Splits files >500 lines into manageable chunks with cross-references

set -euo pipefail

# Configuration
MAX_MAIN_LINES=450  # Keep buffer for headers/footers
TARGET_MAIN_LINES=400  # Target size for main file

# Check if content needs splitting
# Args: $1: content
needs_splitting() {
    local content="$1"
    local line_count=$(echo "$content" | grep -c '^' || true)

    if [ "$line_count" -gt 500 ]; then
        echo "true"
    else
        echo "false"
    fi
}

# Prioritize content sections for main file
# Returns: section_name:priority (higher number = higher priority)
get_section_priorities() {
    cat <<EOF
Role & Responsibilities:100
Memory Bank Integration:90
Memory Bank:90
Tech Stack:80
Critical Guidelines:70
Best Practices:60
Guidelines:50
Custom Project Instructions:40
Development Workflow:30
Communication:20
EOF
}

# Extract section with context
# Args: $1: content, $2: section_header
extract_full_section() {
    local content="$1"
    local header="$2"
    local in_section=false
    local result=""
    local header_level=""

    while IFS= read -r line; do
        # Detect section start
        if [[ "$line" =~ ^(#{1,3})[[:space:]]+(.*)$ ]]; then
            local level="${BASH_REMATCH[1]}"
            local title="${BASH_REMATCH[2]}"

            if [ "$title" = "$header" ]; then
                in_section=true
                header_level="$level"
                result+="$line\n"
                continue
            elif [ "$in_section" = true ] && [ "$level" = "$header_level" ]; then
                # Hit next section of same level, stop
                break
            fi
        fi

        if [ "$in_section" = true ]; then
            result+="$line\n"
        fi
    done <<< "$content"

    echo -e "$result"
}

# Create summary of a section (first N lines)
# Args: $1: section_content, $2: max_lines
create_section_summary() {
    local content="$1"
    local max_lines="${2:-10}"

    local summary=$(echo "$content" | head -n "$max_lines")
    local total_lines=$(echo "$content" | grep -c '^' || true)

    if [ "$total_lines" -gt "$max_lines" ]; then
        summary+="\n\n📖 *See extended documentation for complete details*\n"
    fi

    echo -e "$summary"
}

# Build main CLAUDE.md (prioritized content)
# Args: $1: full_content, $2: max_lines
build_main_file() {
    local content="$1"
    local max_lines="${2:-$TARGET_MAIN_LINES}"
    local result=""
    local current_lines=0

    # Get all section headers from content
    local headers=$(echo "$content" | grep -E '^## ' | sed 's/^## //')

    # Get priorities
    local priorities=$(get_section_priorities)

    # Sort headers by priority
    local sorted_headers=""
    while IFS= read -r header; do
        if [ -z "$header" ]; then continue; fi

        local priority=0
        while IFS=':' read -r pname ppriority; do
            if [ "$pname" = "$header" ]; then
                priority=$ppriority
                break
            fi
        done <<< "$priorities"

        sorted_headers+="${priority}:${header}\n"
    done <<< "$headers"

    sorted_headers=$(echo -e "$sorted_headers" | sort -rn)

    # Add sections in priority order until we hit max_lines
    while IFS=':' read -r priority header; do
        if [ -z "$header" ]; then continue; fi

        local section=$(extract_full_section "$content" "$header")
        local section_lines=$(echo "$section" | grep -c '^' || true)

        # Check if adding this section would exceed limit
        if [ $((current_lines + section_lines)) -gt "$max_lines" ]; then
            # Add summary instead
            local summary=$(create_section_summary "$section" 15)
            result+="$summary\n\n"
            current_lines=$((current_lines + 20))
        else
            # Add full section
            result+="$section\n\n"
            current_lines=$((current_lines + section_lines))
        fi

        # Stop if we're close to limit
        if [ "$current_lines" -ge "$max_lines" ]; then
            break
        fi
    done <<< "$sorted_headers"

    echo -e "$result"
}

# Build extended file (detailed content)
# Args: $1: full_content, $2: main_content
build_extended_file() {
    local full_content="$1"
    local main_content="$2"

    # Extract sections that are NOT fully in main_content
    local result="# CLAUDE.md Extended Documentation\n\n"
    result+="This file contains detailed information that didn't fit in the main CLAUDE.md.\n\n"
    result+="---\n\n"

    # Get all section headers
    local headers=$(echo "$full_content" | grep -E '^## ' | sed 's/^## //')

    while IFS= read -r header; do
        if [ -z "$header" ]; then continue; fi

        local full_section=$(extract_full_section "$full_content" "$header")
        local main_section=$(extract_full_section "$main_content" "$header")

        # If section is summarized or missing in main, add full version here
        local full_lines=$(echo "$full_section" | grep -c '^' || true)
        local main_lines=$(echo "$main_section" | grep -c '^' || true)

        if [ "$full_lines" -gt "$((main_lines + 5))" ]; then
            result+="$full_section\n\n---\n\n"
        fi
    done <<< "$headers"

    echo -e "$result"
}

# Build custom file (user's original content)
# Args: $1: custom_content
build_custom_file() {
    local custom_content="$1"

    cat <<EOF
# Custom Project Instructions

This file contains your original CLAUDE.md instructions, preserved during Dev-AID migration.

---

$custom_content

---

*These instructions are referenced from the main CLAUDE.md file*
EOF
}

# Add cross-references to main file
# Args: $1: main_content, $2: has_extended, $3: has_custom
add_cross_references() {
    local content="$1"
    local has_extended="${2:-false}"
    local has_custom="${3:-false}"

    local footer="\n\n---\n\n## Additional Documentation\n\n"

    if [ "$has_extended" = "true" ]; then
        footer+="📖 **Extended Documentation**: See [CLAUDE_extended.md](.dev-aid/providers/claude/CLAUDE_extended.md) for complete details on all sections.\n\n"
    fi

    if [ "$has_custom" = "true" ]; then
        footer+="📝 **Custom Instructions**: See [CLAUDE_custom.md](.dev-aid/providers/claude/CLAUDE_custom.md) for your original project-specific guidelines.\n\n"
    fi

    footer+="---\n\n"
    footer+="*This file is managed by Dev-AID. Original content preserved in backup.*\n"

    echo -e "${content}${footer}"
}

# Apply progressive disclosure
# Args: $1: full_content, $2: custom_content, $3: output_dir
apply_progressive_disclosure() {
    local full_content="$1"
    local custom_content="$2"
    local output_dir="$3"

    local total_lines=$(echo "$full_content" | grep -c '^' || true)

    echo "Content size: $total_lines lines" >&2
    echo "Applying progressive disclosure..." >&2

    # Build main file (prioritized, ≤450 lines)
    local main_content=$(build_main_file "$full_content" "$MAX_MAIN_LINES")
    local main_lines=$(echo "$main_content" | grep -c '^' || true)
    echo "Main file: $main_lines lines" >&2

    # Build extended file (everything not in main)
    local extended_content=$(build_extended_file "$full_content" "$main_content")
    local extended_lines=$(echo "$extended_content" | grep -c '^' || true)
    echo "Extended file: $extended_lines lines" >&2

    # Determine what files to create
    local has_extended="false"
    local has_custom="false"

    if [ "$extended_lines" -gt 20 ]; then
        has_extended="true"
    fi

    if [ -n "$custom_content" ] && [ "$(echo "$custom_content" | grep -c '^')" -gt 5 ]; then
        has_custom="true"
    fi

    # Add cross-references to main
    main_content=$(add_cross_references "$main_content" "$has_extended" "$has_custom")

    # Write files
    mkdir -p "$output_dir"

    echo -e "$main_content" > "$output_dir/CLAUDE.md"
    echo "✓ Created main file: $output_dir/CLAUDE.md" >&2

    if [ "$has_extended" = "true" ]; then
        echo -e "$extended_content" > "$output_dir/CLAUDE_extended.md"
        echo "✓ Created extended file: $output_dir/CLAUDE_extended.md" >&2
    fi

    if [ "$has_custom" = "true" ]; then
        local custom_file=$(build_custom_file "$custom_content")
        echo -e "$custom_file" > "$output_dir/CLAUDE_custom.md"
        echo "✓ Created custom file: $output_dir/CLAUDE_custom.md" >&2
    fi

    # Return stats
    cat <<EOF
{
  "main_lines": $main_lines,
  "extended_lines": $extended_lines,
  "has_extended": $has_extended,
  "has_custom": $has_custom,
  "files_created": ["CLAUDE.md"$([ "$has_extended" = "true" ] && echo ", \"CLAUDE_extended.md\"")$([ "$has_custom" = "true" ] && echo ", \"CLAUDE_custom.md\"")]
}
EOF
}

# Simple split (no prioritization, just split at line count)
# Args: $1: content, $2: output_dir
simple_split() {
    local content="$1"
    local output_dir="$2"

    mkdir -p "$output_dir"

    local main=$(echo "$content" | head -n "$MAX_MAIN_LINES")
    local extended=$(echo "$content" | tail -n "+$((MAX_MAIN_LINES + 1))")

    main=$(add_cross_references "$main" "true" "false")

    echo -e "$main" > "$output_dir/CLAUDE.md"
    echo -e "# CLAUDE.md Extended\n\n$extended" > "$output_dir/CLAUDE_extended.md"

    echo "Split complete: Main ($MAX_MAIN_LINES lines) + Extended" >&2
}

# Get file size info
# Args: $1: file_path
get_file_info() {
    local file="$1"

    if [ ! -f "$file" ]; then
        echo "File not found"
        return 1
    fi

    local lines=$(wc -l < "$file" | tr -d ' ')
    local size=$(du -h "$file" | cut -f1)

    echo "Lines: $lines, Size: $size"
}
