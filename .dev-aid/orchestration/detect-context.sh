#!/usr/bin/env bash
#
# Script: detect-context.sh
# Description: Detects project context by analyzing files, keywords, and technologies
# Usage: detect-context.sh [directory]
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
    [[ -n "${TEMP_FILE:-}" ]] && rm -f "$TEMP_FILE" 2>/dev/null || true
    exit "$exit_code"
}
trap cleanup EXIT INT TERM

# Configuration
readonly PROJECT_DIR="${1:-.}"
readonly MAX_FILES=100
readonly MAX_KEYWORDS=50

# Temporary file for collecting context
TEMP_FILE=$(mktemp) || exit 1
chmod 600 "$TEMP_FILE"

# Detect file types and patterns
detect_file_patterns() {
    local project_dir="$1"

    # Security: Validate path containment
    local resolved_path
    resolved_path="$(realpath -m "$project_dir")" || return 1

    # Common file patterns that indicate technologies
    local -a patterns=(
        "package.json|Node.js JavaScript"
        "tsconfig.json|TypeScript"
        "Cargo.toml|Rust"
        "requirements.txt|Python pip"
        "pyproject.toml|Python poetry"
        "Gemfile|Ruby"
        "go.mod|Go"
        "Dockerfile|Docker"
        "docker-compose.yml|Docker Compose"
        ".github/workflows|GitHub Actions"
        "openapi.yaml|OpenAPI"
        "swagger.json|Swagger"
        "*.graphql|GraphQL"
        "*.sh|Bash scripts"
    )

    for pattern_entry in "${patterns[@]}"; do
        IFS='|' read -r pattern tech <<< "$pattern_entry"
        # Use find with proper quoting and limits
        if find "$resolved_path" -name "$pattern" -type f 2>/dev/null | head -1 | grep -q .; then
            echo "$tech" >> "$TEMP_FILE"
        fi
    done
}

# Extract keywords from common config files
extract_keywords() {
    local project_dir="$1"
    local -a config_files=(
        "package.json"
        "Cargo.toml"
        "pyproject.toml"
        "requirements.txt"
    )

    for config_file in "${config_files[@]}"; do
        local file_path="$project_dir/$config_file"
        if [[ -f "$file_path" && -r "$file_path" ]]; then
            # Extract technology names from config files
            case "$config_file" in
                package.json)
                    # Extract dependency names
                    if command -v jq >/dev/null 2>&1; then
                        jq -r '.dependencies // {} | keys[]' "$file_path" 2>/dev/null | head -"$MAX_KEYWORDS" >> "$TEMP_FILE" || true
                        jq -r '.devDependencies // {} | keys[]' "$file_path" 2>/dev/null | head -"$MAX_KEYWORDS" >> "$TEMP_FILE" || true
                    fi
                    ;;
                Cargo.toml)
                    # Extract Rust crate names
                    grep -E '^\[dependencies\]' -A 20 "$file_path" 2>/dev/null | grep -E '^[a-zA-Z]' | cut -d'=' -f1 | head -"$MAX_KEYWORDS" >> "$TEMP_FILE" || true
                    ;;
                pyproject.toml|requirements.txt)
                    # Extract Python package names
                    grep -E '^[a-zA-Z]' "$file_path" 2>/dev/null | cut -d'=' -f1 | cut -d'[' -f1 | head -"$MAX_KEYWORDS" >> "$TEMP_FILE" || true
                    ;;
            esac
        fi
    done
}

# Detect common technology indicators in source files
detect_technologies() {
    local project_dir="$1"

    # Technology indicators to search for
    local -a indicators=(
        "FastAPI|fastapi"
        "Express|express"
        "GraphQL|graphql"
        "React|react"
        "Vue|vue"
        "Angular|angular"
        "Django|django"
        "Flask|flask"
        "Svelte|svelte"
        "Next.js|next"
        "Nuxt|nuxt"
    )

    for indicator_entry in "${indicators[@]}"; do
        IFS='|' read -r tech pattern <<< "$indicator_entry"
        # Search for technology mentions (case-insensitive)
        if find "$project_dir" -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.tsx" \) \
            -exec grep -l -i "$pattern" {} \; 2>/dev/null | head -1 | grep -q .; then
            echo "$tech" >> "$TEMP_FILE"
        fi
    done
}

# Main context detection
main() {
    # Validate project directory
    if [[ ! -d "$PROJECT_DIR" ]]; then
        echo "Error: Directory does not exist: $PROJECT_DIR" >&2
        exit 1
    fi

    # Detect various context signals
    detect_file_patterns "$PROJECT_DIR"
    extract_keywords "$PROJECT_DIR"
    detect_technologies "$PROJECT_DIR"

    # Output unique context keywords (deduplicated and sorted)
    sort -u "$TEMP_FILE" | head -"$MAX_KEYWORDS" | tr '\n' ' '
    echo  # Final newline
}

# Run main function
main
