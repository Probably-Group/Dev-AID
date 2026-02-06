#!/usr/bin/env bash
# Dev-AID Impact Analysis
# Find all code that depends on a function/class

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    cat <<EOF
Usage: $0 [OPTIONS] <symbol-name>

Find all code that uses a function, class, or variable.

Examples:
    $0 getUserById                    # Find all callers of function
    $0 --type class User              # Find imports of User class
    $0 --scope file utils/auth.py     # Find imports of this file

Options:
    -t, --type <type>    Symbol type: function (default), class, file
    -s, --scope <file>   Limit search to specific file
    -f, --format <fmt>   Output format: text (default), json, markdown
    -h, --help           Show this help message

Output:
    - Files that call/import the symbol
    - Line numbers and context
    - Suggested test files to run
    - Change impact summary
EOF
    exit 1
}

TYPE="function"
SCOPE=""
FORMAT="text"

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type) TYPE="$2"; shift 2 ;;
        -s|--scope) SCOPE="$2"; shift 2 ;;
        -f|--format) FORMAT="$2"; shift 2 ;;
        -h|--help) usage ;;
        -*) echo "Unknown option: $1"; usage ;;
        *) break ;;
    esac
done

if [ $# -lt 1 ]; then
    echo "Error: Missing symbol name"
    usage
fi

SYMBOL="$1"

# Check dependencies
if ! command -v rg &> /dev/null; then
    echo -e "${RED}Error: ripgrep (rg) is required${NC}"
    echo "Install: brew install ripgrep"
    exit 1
fi

echo -e "${BLUE}Analyzing impact of: $SYMBOL${NC}"
echo ""

# Build search pattern based on type
case $TYPE in
    function)
        PATTERN="${SYMBOL}\s*\("
        ;;
    class)
        PATTERN="(import|from).*${SYMBOL}|class.*${SYMBOL}"
        ;;
    file)
        FILENAME=$(basename "$SYMBOL")
        PATTERN="(import|from).*${FILENAME%.py}"
        ;;
    *)
        echo "Unknown type: $TYPE"
        usage
        ;;
esac

# Search for usage
TEMP_FILE=$(mktemp)
trap 'rm -f "$TEMP_FILE"' EXIT

if [ -n "$SCOPE" ]; then
    rg --line-number --color never "$PATTERN" "$SCOPE" > "$TEMP_FILE" || true
else
    rg --line-number --color never --type py --type js --type ts "$PATTERN" . > "$TEMP_FILE" || true
fi

# Count occurrences
TOTAL=$(wc -l < "$TEMP_FILE" | tr -d ' ')

if [ "$TOTAL" -eq 0 ]; then
    echo -e "${GREEN}✓ No direct dependencies found${NC}"
    echo "This $TYPE appears to be unused or only used internally."
    exit 0
fi

# Parse results
declare -A FILE_COUNTS
while IFS=: read -r file line content; do
    FILE_COUNTS["$file"]=$((${FILE_COUNTS["$file"]:-0} + 1))
done < "$TEMP_FILE"

# Output based on format
if [ "$FORMAT" = "json" ]; then
    echo "{"
    echo "  \"symbol\": \"$SYMBOL\","
    echo "  \"type\": \"$TYPE\","
    echo "  \"total_references\": $TOTAL,"
    echo "  \"files\": ["
    for file in "${!FILE_COUNTS[@]}"; do
        count="${FILE_COUNTS[$file]}"
        echo "    {\"file\": \"$file\", \"count\": $count},"
    done | sed '$ s/,$//'
    echo "  ]"
    echo "}"
elif [ "$FORMAT" = "markdown" ]; then
    echo "# Impact Analysis: $SYMBOL"
    echo ""
    echo "**Type:** $TYPE"
    echo "**Total References:** $TOTAL"
    echo "**Affected Files:** ${#FILE_COUNTS[@]}"
    echo ""
    echo "## Files Using This $TYPE"
    echo ""
    for file in "${!FILE_COUNTS[@]}"; do
        count="${FILE_COUNTS[$file]}"
        echo "- [$file]($file) ($count occurrence(s))"
    done
else
    # Text format
    echo -e "${YELLOW}Found $TOTAL reference(s) in ${#FILE_COUNTS[@]} file(s)${NC}"
    echo ""
    echo "Affected files:"
    for file in "${!FILE_COUNTS[@]}"; do
        count="${FILE_COUNTS[$file]}"
        echo -e "  ${GREEN}$file${NC} (${count} occurrence(s))"
    done

    echo ""
    echo "Suggested test files to run:"
    # Find test files related to affected files
    for file in "${!FILE_COUNTS[@]}"; do
        dir=$(dirname "$file")
        base=$(basename "$file" .py)
        test_file="${dir}/test_${base}.py"
        if [ -f "$test_file" ]; then
            echo -e "  ${BLUE}$test_file${NC}"
        fi
    done

    echo ""
    echo -e "${YELLOW}⚠️  Impact Summary:${NC}"
    echo "Changing this $TYPE will affect $TOTAL location(s) in ${#FILE_COUNTS[@]} file(s)."
    echo "Consider:"
    echo "  1. Run suggested tests before merging"
    echo "  2. Check for breaking API changes"
    echo "  3. Update documentation if public API"
fi
