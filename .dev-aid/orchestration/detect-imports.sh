#!/usr/bin/env bash
#
# Script: detect-imports.sh
# Description: Scans source files for import statements and framework-specific patterns
# Usage: detect-imports.sh [directory] [max_files]
#

# Strict mode: exit on error, undefined variables, pipe failures
set -euo pipefail

# Script directory (portable way)
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Cleanup function (always runs on exit)
cleanup() {
    local exit_code=$?
    [[ -n "${TEMP_IMPORTS:-}" ]] && rm -f "$TEMP_IMPORTS" 2>/dev/null || true
    exit "$exit_code"
}
trap cleanup EXIT INT TERM

# Configuration
readonly PROJECT_DIR="${1:-.}"
readonly MAX_FILES="${2:-100}"
readonly MAX_IMPORTS=200

# Temporary file for collecting imports
TEMP_IMPORTS=$(mktemp) || exit 1
chmod 600 "$TEMP_IMPORTS"

# Extract Python imports
extract_python_imports() {
    local project_dir="$1"

    # Find Python files (limit to MAX_FILES for performance)
    while IFS= read -r file; do
        [[ ! -f "$file" ]] && continue

        # Extract import statements
        grep -hE "^(import |from .* import)" "$file" 2>/dev/null | \
            sed -E 's/^import //; s/^from ([^ ]+).*/\1/; s/ as .*//' | \
            cut -d'.' -f1 | \
            head -20 >> "$TEMP_IMPORTS" || true

    done < <(find -- "$project_dir" -name "*.py" -type f 2>/dev/null | head -"$MAX_FILES")
}

# Extract JavaScript/TypeScript imports
extract_js_ts_imports() {
    local project_dir="$1"

    # Find JS/TS files
    while IFS= read -r file; do
        [[ ! -f "$file" ]] && continue

        # Extract import statements (ES6 and require)
        # import ... from "package"
        grep -hE "^import .* from ['\"]" "$file" 2>/dev/null | \
            sed -E "s/^import .* from ['\"]([^'\"]+)['\"].*/\1/" | \
            cut -d'/' -f1 | \
            sed 's/@//' | \
            head -20 >> "$TEMP_IMPORTS" || true

        # const ... = require("package")
        grep -hE "= require\(['\"]" "$file" 2>/dev/null | \
            sed -E "s/.*require\(['\"]([^'\"]+)['\"].*/\1/" | \
            cut -d'/' -f1 | \
            sed 's/@//' | \
            head -20 >> "$TEMP_IMPORTS" || true

    done < <(find -- "$project_dir" -type f \( -name "*.js" -o -name "*.ts" -o -name "*.tsx" -o -name "*.jsx" \) 2>/dev/null | head -"$MAX_FILES")
}

# Extract Rust dependencies from Cargo.toml
extract_rust_deps() {
    local project_dir="$1"
    local cargo_file="$project_dir/Cargo.toml"

    if [[ -f "$cargo_file" ]]; then
        # Extract crate names from [dependencies] section
        awk '/^\[dependencies\]/,/^\[/ {print}' "$cargo_file" 2>/dev/null | \
            grep -E '^[a-zA-Z]' | \
            cut -d'=' -f1 | \
            tr -d ' ' | \
            head -30 >> "$TEMP_IMPORTS" || true
    fi
}

# Extract Go imports
extract_go_imports() {
    local project_dir="$1"

    # Find Go files
    while IFS= read -r file; do
        [[ ! -f "$file" ]] && continue

        # Extract import statements
        # Single line: import "package"
        grep -hE '^import "' "$file" 2>/dev/null | \
            sed -E 's/^import "([^"]+)".*/\1/' | \
            rev | cut -d'/' -f1 | rev | \
            head -20 >> "$TEMP_IMPORTS" || true

        # Multi-line imports: extract from parentheses
        sed -n '/^import (/,/^)/p' "$file" 2>/dev/null | \
            grep -E '^\s+"' | \
            sed -E 's/^\s+"([^"]+)".*/\1/' | \
            rev | cut -d'/' -f1 | rev | \
            head -20 >> "$TEMP_IMPORTS" || true

    done < <(find -- "$project_dir" -name "*.go" -type f 2>/dev/null | head -"$MAX_FILES")
}

# Detect framework-specific patterns
detect_framework_patterns() {
    local project_dir="$1"

    # Vue/Nuxt: Look for <template>, <script setup>, defineComponent
    if find -- "$project_dir" -name "*.vue" -type f 2>/dev/null | head -1 | grep -q .; then
        echo "Vue" >> "$TEMP_IMPORTS"

        # Check for Nuxt-specific patterns
        if grep -rq --no-messages "useAsyncData\|useFetch\|defineNuxtConfig" "$project_dir" --include="*.vue" --include="*.ts" 2>/dev/null; then
            echo "Nuxt" >> "$TEMP_IMPORTS"
        fi
    fi

    # React: Look for JSX syntax, React hooks
    if find -- "$project_dir" -type f \( -name "*.jsx" -o -name "*.tsx" \) 2>/dev/null | head -1 | grep -q .; then
        echo "React" >> "$TEMP_IMPORTS"

        # Check for Next.js specific files/patterns
        if [[ -f "$project_dir/next.config.js" ]] || [[ -f "$project_dir/next.config.ts" ]]; then
            echo "Next.js" >> "$TEMP_IMPORTS"
        fi
    fi

    # FastAPI: Look for @app decorator patterns
    if grep -rq --no-messages "@app\\.\\(get\\|post\\|put\\|delete\\)" "$project_dir" --include="*.py" 2>/dev/null; then
        echo "FastAPI" >> "$TEMP_IMPORTS"
    fi

    # Express: Look for express() calls
    if grep -rq --no-messages "express()" "$project_dir" --include="*.js" --include="*.ts" 2>/dev/null; then
        echo "Express" >> "$TEMP_IMPORTS"
    fi

    # GraphQL: Look for type Query, type Mutation
    if grep -rq --no-messages "type \\(Query\\|Mutation\\)" "$project_dir" --include="*.graphql" --include="*.gql" 2>/dev/null; then
        echo "GraphQL" >> "$TEMP_IMPORTS"
    fi

    # Tauri: Check for src-tauri directory
    if [[ -d "$project_dir/src-tauri" ]]; then
        echo "Tauri" >> "$TEMP_IMPORTS"
    fi

    # Electron: Check for electron in main process
    if grep -rq --no-messages "app\\.whenReady\\|BrowserWindow" "$project_dir" --include="*.js" --include="*.ts" 2>/dev/null; then
        echo "Electron" >> "$TEMP_IMPORTS"
    fi
}

# Detect testing frameworks
detect_testing_frameworks() {
    local project_dir="$1"

    # Python testing
    if find -- "$project_dir" -name "test_*.py" -type f 2>/dev/null | head -1 | grep -q .; then
        echo "pytest" >> "$TEMP_IMPORTS"
    fi

    # JavaScript testing
    if grep -rq --no-messages "describe\\|it\\|test\\|expect" "$project_dir" --include="*.test.js" --include="*.test.ts" --include="*.spec.js" --include="*.spec.ts" 2>/dev/null; then
        echo "Jest" >> "$TEMP_IMPORTS"
    fi

    # Check for specific test runners in files
    if grep -rq --no-messages "vitest" "$project_dir" --include="*.js" --include="*.ts" 2>/dev/null; then
        echo "Vitest" >> "$TEMP_IMPORTS"
    fi
}

# Detect database ORMs and libraries
detect_database_patterns() {
    local project_dir="$1"

    # SQLAlchemy (Python)
    if grep -rq --no-messages "from sqlalchemy import\\|import sqlalchemy" "$project_dir" --include="*.py" 2>/dev/null; then
        echo "SQLAlchemy" >> "$TEMP_IMPORTS"
    fi

    # Prisma (TypeScript)
    if [[ -f "$project_dir/prisma/schema.prisma" ]]; then
        echo "Prisma" >> "$TEMP_IMPORTS"
    fi

    # TypeORM
    if grep -rq --no-messages "@Entity\\|@Column" "$project_dir" --include="*.ts" 2>/dev/null; then
        echo "TypeORM" >> "$TEMP_IMPORTS"
    fi
}

# Main detection logic
main() {
    # Validate project directory
    if [[ ! -d "$PROJECT_DIR" ]]; then
        echo "Error: Directory does not exist: $PROJECT_DIR" >&2
        exit 1
    fi

    # Extract imports from different languages
    extract_python_imports "$PROJECT_DIR"
    extract_js_ts_imports "$PROJECT_DIR"
    extract_rust_deps "$PROJECT_DIR"
    extract_go_imports "$PROJECT_DIR"

    # Detect framework-specific patterns
    detect_framework_patterns "$PROJECT_DIR"
    detect_testing_frameworks "$PROJECT_DIR"
    detect_database_patterns "$PROJECT_DIR"

    # Output unique imports (deduplicated and sorted)
    sort -u "$TEMP_IMPORTS" 2>/dev/null | head -"$MAX_IMPORTS" | tr '\n' ' '
    echo  # Final newline
}

# Run main function
main
