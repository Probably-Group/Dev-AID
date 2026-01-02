#!/usr/bin/env bash
# CLAUDE.md Content Validation
# Detects outdated, conflicting, and invalid content

set -euo pipefail

# Issue types
declare -A ISSUE_TYPES=(
    [OUTDATED_VERSION]="Outdated technology version"
    [MISSING_TECH]="Missing technology from stack"
    [WRONG_FRAMEWORK]="Incorrect framework mentioned"
    [DEPRECATED_TOOL]="Deprecated tool mentioned"
    [CONFLICTING_INSTRUCTION]="Instruction conflicts with project"
    [INVALID_PATH]="Invalid file path reference"
    [DEPRECATED_PATTERN]="Deprecated code pattern"
    [DUPLICATE_SECTION]="Duplicate content section"
    [SECURITY_ISSUE]="Potential security issue"
    [CONTRADICTION]="Contradictory instructions"
)

# Global arrays for tracking issues (exported for persistence)
declare -a VALIDATION_ISSUES
declare -a AUTO_FIXES
VALIDATION_ISSUES=()
AUTO_FIXES=()

# Add validation issue
# Args: type, line_num, description, severity, auto_fix
add_issue() {
    local type="$1"
    local line_num="$2"
    local description="$3"
    local severity="${4:-medium}"
    local auto_fix="${5:-false}"

    local issue_json=$(cat <<EOF
{
  "type": "$type",
  "line": $line_num,
  "description": "$description",
  "severity": "$severity",
  "auto_fix": $auto_fix
}
EOF
)
    VALIDATION_ISSUES+=("$issue_json")
}

# Detect project technology stack
# Args: $1: project_root
detect_actual_tech_stack() {
    local project_root="$1"
    local tech_stack=""

    # Frontend detection
    if [ -f "$project_root/package.json" ]; then
        local package_json=$(cat "$project_root/package.json")

        # React
        if echo "$package_json" | grep -q '"react"'; then
            local version=$(echo "$package_json" | grep '"react"' | head -1 | sed 's/.*"react": *"\^*\([0-9.]*\).*/\1/')
            tech_stack+="React:$version,"
        fi

        # Vue
        if echo "$package_json" | grep -q '"vue"'; then
            local version=$(echo "$package_json" | grep '"vue"' | head -1 | sed 's/.*"vue": *"\^*\([0-9.]*\).*/\1/')
            tech_stack+="Vue:$version,"
        fi

        # Angular
        if echo "$package_json" | grep -q '"@angular/core"'; then
            local version=$(echo "$package_json" | grep '"@angular/core"' | head -1 | sed 's/.*"@angular\/core": *"\^*\([0-9.]*\).*/\1/')
            tech_stack+="Angular:$version,"
        fi

        # TypeScript
        if echo "$package_json" | grep -q '"typescript"'; then
            local version=$(echo "$package_json" | grep '"typescript"' | head -1 | sed 's/.*"typescript": *"\^*\([0-9.]*\).*/\1/')
            tech_stack+="TypeScript:$version,"
        fi

        # Next.js
        if echo "$package_json" | grep -q '"next"'; then
            local version=$(echo "$package_json" | grep '"next"' | head -1 | sed 's/.*"next": *"\^*\([0-9.]*\).*/\1/')
            tech_stack+="Next.js:$version,"
        fi
    fi

    # Python detection
    if [ -f "$project_root/requirements.txt" ] || [ -f "$project_root/setup.py" ] || [ -f "$project_root/pyproject.toml" ]; then
        tech_stack+="Python:true,"

        if [ -f "$project_root/requirements.txt" ]; then
            if grep -q "django" "$project_root/requirements.txt"; then
                tech_stack+="Django:true,"
            fi
            if grep -q "flask" "$project_root/requirements.txt"; then
                tech_stack+="Flask:true,"
            fi
            if grep -q "fastapi" "$project_root/requirements.txt"; then
                tech_stack+="FastAPI:true,"
            fi
        fi
    fi

    # Go detection
    if [ -f "$project_root/go.mod" ]; then
        tech_stack+="Go:true,"
    fi

    # Rust detection
    if [ -f "$project_root/Cargo.toml" ]; then
        tech_stack+="Rust:true,"
    fi

    # Database detection
    if [ -f "$project_root/docker-compose.yml" ]; then
        if grep -q "postgres" "$project_root/docker-compose.yml"; then
            tech_stack+="PostgreSQL:true,"
        fi
        if grep -q "mysql" "$project_root/docker-compose.yml"; then
            tech_stack+="MySQL:true,"
        fi
        if grep -q "mongodb" "$project_root/docker-compose.yml"; then
            tech_stack+="MongoDB:true,"
        fi
        if grep -q "redis" "$project_root/docker-compose.yml"; then
            tech_stack+="Redis:true,"
        fi
    fi

    echo "$tech_stack"
}

# Extract technology mentions from CLAUDE.md
# Args: $1: claude_md_content
extract_tech_mentions() {
    local content="$1"
    local mentions=""

    # Extract React mentions with versions
    if echo "$content" | grep -qi "react"; then
        local react_versions=$(echo "$content" | grep -oiE "react [0-9]+(\.[0-9]+)*" | sed 's/[Rr]eact //')
        if [ -n "$react_versions" ]; then
            while IFS= read -r version; do
                mentions+="React:$version,"
            done <<< "$react_versions"
        fi
    fi

    # Extract Vue mentions
    if echo "$content" | grep -qi "vue"; then
        local vue_versions=$(echo "$content" | grep -oiE "vue [0-9]+(\.[0-9]+)*" | sed 's/[Vv]ue //')
        if [ -n "$vue_versions" ]; then
            while IFS= read -r version; do
                mentions+="Vue:$version,"
            done <<< "$vue_versions"
        fi
    fi

    # Extract Angular mentions
    if echo "$content" | grep -qi "angular"; then
        mentions+="Angular:true,"
    fi

    # Extract TypeScript mentions
    if echo "$content" | grep -qi "typescript"; then
        mentions+="TypeScript:true,"
    fi

    # Extract deprecated tools
    if echo "$content" | grep -qi "bower"; then
        mentions+="Bower:deprecated,"
    fi
    if echo "$content" | grep -qi "grunt"; then
        mentions+="Grunt:deprecated,"
    fi
    if echo "$content" | grep -qi "gulp"; then
        mentions+="Gulp:deprecated,"
    fi

    # Extract Python mentions
    if echo "$content" | grep -qi "python"; then
        mentions+="Python:true,"
    fi
    if echo "$content" | grep -qi "django"; then
        mentions+="Django:true,"
    fi
    if echo "$content" | grep -qi "flask"; then
        mentions+="Flask:true,"
    fi

    echo "$mentions"
}

# Validate technology stack
# Args: $1: claude_md_file, $2: project_root
validate_tech_stack() {
    local claude_md_file="$1"
    local project_root="$2"

    local actual_stack=$(detect_actual_tech_stack "$project_root")
    local content=$(cat "$claude_md_file")
    local mentioned_stack=$(extract_tech_mentions "$content")

    # Check React version mismatches
    if [[ "$actual_stack" == *"React:"* ]] && [[ "$mentioned_stack" == *"React:"* ]]; then
        local actual_version=$(echo "$actual_stack" | grep -o 'React:[^,]*' | cut -d: -f2)
        local mentioned_version=$(echo "$mentioned_stack" | grep -o 'React:[^,]*' | cut -d: -f2 | head -1)

        if [ -n "$actual_version" ] && [ -n "$mentioned_version" ] && [ "$actual_version" != "$mentioned_version" ]; then
            local line_num=$(grep -n -i "react $mentioned_version" "$claude_md_file" | head -1 | cut -d: -f1)
            line_num=${line_num:-0}
            add_issue "OUTDATED_VERSION" "$line_num" "Mentions React $mentioned_version but project uses React $actual_version" "medium" "true"
        fi
    fi

    # Check for deprecated tools
    if [[ "$mentioned_stack" == *"Bower:deprecated"* ]]; then
        local line_num=$(grep -n -i "bower" "$claude_md_file" | head -1 | cut -d: -f1)
        line_num=${line_num:-0}
        add_issue "DEPRECATED_TOOL" "$line_num" "Bower is deprecated, project should use npm/yarn" "low" "true"
    fi

    if [[ "$mentioned_stack" == *"Grunt:deprecated"* ]]; then
        local line_num=$(grep -n -i "grunt" "$claude_md_file" | head -1 | cut -d: -f1)
        line_num=${line_num:-0}
        add_issue "DEPRECATED_TOOL" "$line_num" "Grunt is deprecated, project likely uses Webpack/Vite" "low" "false"
    fi

    if [[ "$mentioned_stack" == *"Gulp:deprecated"* ]]; then
        local line_num=$(grep -n -i "gulp" "$claude_md_file" | head -1 | cut -d: -f1)
        line_num=${line_num:-0}
        add_issue "DEPRECATED_TOOL" "$line_num" "Gulp is deprecated, project likely uses Webpack/Vite" "low" "false"
    fi

    # Check TypeScript conflicts
    if [[ "$actual_stack" == *"TypeScript:"* ]]; then
        if echo "$content" | grep -qi "avoid.*typescript\|never.*typescript\|don't.*use.*typescript"; then
            local line_num=$(grep -n -i "typescript" "$claude_md_file" | grep -i "avoid\|never\|don't" | head -1 | cut -d: -f1)
            line_num=${line_num:-0}
            add_issue "CONFLICTING_INSTRUCTION" "$line_num" "Says to avoid TypeScript but project is TypeScript-based" "high" "true"
        fi
    fi
}

# Validate file paths mentioned in CLAUDE.md
# Args: $1: claude_md_file, $2: project_root
validate_file_paths() {
    local claude_md_file="$1"
    local project_root="$2"
    local content=$(cat "$claude_md_file")

    # Extract path-like patterns (e.g., /src/, ./components/, etc.)
    local paths=$(echo "$content" | grep -oE '/?[a-zA-Z0-9_-]+(/[a-zA-Z0-9_-]+)+' || true)

    if [ -n "$paths" ]; then
        while IFS= read -r path; do
            # Skip common non-path patterns
            if [[ "$path" =~ ^https?:// ]] || [[ "$path" =~ ^mailto: ]]; then
                continue
            fi

            # Check if path exists
            local full_path="${project_root}${path}"
            if [ ! -e "$full_path" ] && [ ! -e "${project_root}/${path}" ]; then
                local line_num=$(grep -n -F "$path" "$claude_md_file" | head -1 | cut -d: -f1)
                line_num=${line_num:-0}

                # Try to suggest a correction
                local suggestion=""
                local dirname=$(dirname "$path")
                local basename=$(basename "$path")

                if [ -d "${project_root}/src/${basename}" ]; then
                    suggestion="/src/${basename}"
                elif [ -d "${project_root}/${basename}" ]; then
                    suggestion="/${basename}"
                fi

                if [ -n "$suggestion" ]; then
                    add_issue "INVALID_PATH" "$line_num" "Path '$path' not found. Did you mean '$suggestion'?" "medium" "true"
                else
                    add_issue "INVALID_PATH" "$line_num" "Path '$path' not found in project" "medium" "false"
                fi
            fi
        done <<< "$paths"
    fi
}

# Check for duplicate sections
# Args: $1: claude_md_file
validate_duplicate_sections() {
    local claude_md_file="$1"
    local content=$(cat "$claude_md_file")

    # Extract headers
    local headers=$(echo "$content" | grep -E '^#{1,3} ' || true)

    if [ -n "$headers" ]; then
        # Find duplicates
        local seen=()
        local line_num=1

        while IFS= read -r line; do
            if [[ "$line" =~ ^#{1,3}[[:space:]] ]]; then
                local header=$(echo "$line" | sed 's/^#* *//')
                for seen_header in "${seen[@]}"; do
                    if [ "$header" = "$seen_header" ]; then
                        add_issue "DUPLICATE_SECTION" "$line_num" "Duplicate section header: '$header'" "low" "true"
                        break
                    fi
                done
                seen+=("$header")
            fi
            ((line_num++))
        done < "$claude_md_file"
    fi
}

# Check for contradictory instructions
# Args: $1: claude_md_file
validate_contradictions() {
    local claude_md_file="$1"
    local content=$(cat "$claude_md_file")

    # Pattern: "Always use X" followed by "Never use X"
    local always_patterns=$(echo "$content" | grep -in "always use\|must use\|should use" || true)

    if [ -n "$always_patterns" ]; then
        while IFS= read -r always_line; do
            local line_num=$(echo "$always_line" | cut -d: -f1)
            local text=$(echo "$always_line" | cut -d: -f2-)

            # Extract the thing they say to "always use"
            local thing=$(echo "$text" | sed -n 's/.*always use \([a-zA-Z0-9 ]*\).*/\1/ip' | head -1)

            if [ -n "$thing" ]; then
                # Check if there's a "never use" for the same thing
                if echo "$content" | grep -iq "never use $thing\|avoid $thing\|don't use $thing"; then
                    add_issue "CONTRADICTION" "$line_num" "Says to 'always use $thing' but also says to avoid it" "high" "false"
                fi
            fi
        done <<< "$always_patterns"
    fi
}

# Check for security issues
# Args: $1: claude_md_file
validate_security() {
    local claude_md_file="$1"
    local content=$(cat "$claude_md_file")

    # Check for hardcoded credentials patterns
    if echo "$content" | grep -qE 'password.*=.*["\047][^"\047]+["\047]|api[_-]?key.*=.*["\047][^"\047]+["\047]|token.*=.*["\047][^"\047]+["\047]'; then
        local line_num=$(echo "$content" | grep -nE 'password.*=|api[_-]?key.*=|token.*=' | head -1 | cut -d: -f1)
        line_num=${line_num:-0}
        add_issue "SECURITY_ISSUE" "$line_num" "Potential hardcoded credential in example code" "high" "false"
    fi

    # Check for dangerous patterns
    if echo "$content" | grep -qE 'eval\(|exec\(|system\('; then
        local line_num=$(echo "$content" | grep -nE 'eval\(|exec\(|system\(' | head -1 | cut -d: -f1)
        line_num=${line_num:-0}
        add_issue "SECURITY_ISSUE" "$line_num" "Example shows potentially dangerous function (eval/exec/system)" "medium" "false"
    fi
}

# Run all validations
# Args: $1: claude_md_file, $2: project_root
run_all_validations() {
    local claude_md_file="$1"
    local project_root="$2"

    # Clear previous issues
    VALIDATION_ISSUES=()
    AUTO_FIXES=()

    # Run validations
    validate_tech_stack "$claude_md_file" "$project_root"
    validate_file_paths "$claude_md_file" "$project_root"
    validate_duplicate_sections "$claude_md_file"
    validate_contradictions "$claude_md_file"
    validate_security "$claude_md_file"

    # Return issue count
    echo "${#VALIDATION_ISSUES[@]}"
}

# Get validation issues as JSON
get_validation_issues_json() {
    if [ ${#VALIDATION_ISSUES[@]} -eq 0 ]; then
        echo "[]"
        return
    fi

    local json="["
    for issue in "${VALIDATION_ISSUES[@]}"; do
        json+="$issue,"
    done
    json="${json%,}]"  # Remove trailing comma and close array

    echo "$json"
}

# Get validation summary
get_validation_summary() {
    local total=${#VALIDATION_ISSUES[@]}
    local high=0
    local medium=0
    local low=0
    local auto_fixable=0

    for issue in "${VALIDATION_ISSUES[@]}"; do
        if echo "$issue" | grep -q '"severity": "high"'; then
            ((high++))
        elif echo "$issue" | grep -q '"severity": "medium"'; then
            ((medium++))
        else
            ((low++))
        fi

        if echo "$issue" | grep -q '"auto_fix": true'; then
            ((auto_fixable++))
        fi
    done

    cat <<EOF
Total Issues: $total
  High Priority: $high
  Medium Priority: $medium
  Low Priority: $low
Auto-fixable: $auto_fixable
EOF
}
