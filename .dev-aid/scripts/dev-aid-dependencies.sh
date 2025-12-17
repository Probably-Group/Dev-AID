#!/bin/bash
# Dev-AID Dependencies Tree
# Show import/dependency tree for a file

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    cat <<EOF
Usage: $0 [OPTIONS] <file>

Show dependency tree for a Python/JavaScript/TypeScript file.

Examples:
    $0 src/main.py                      # Show what main.py imports
    $0 --reverse src/utils.py           # Show what imports utils.py
    $0 --depth 2 src/app.ts             # Limit depth to 2 levels

Options:
    -r, --reverse        Show reverse dependencies (what imports this)
    -d, --depth <n>      Maximum depth (default: 3)
    -f, --format <fmt>   Output format: tree (default), list, mermaid
    -h, --help           Show this help message

Output Formats:
    tree     - Tree view with indentation
    list     - Flat list of all dependencies
    mermaid  - Mermaid diagram (copy to docs)
EOF
    exit 1
}

REVERSE=false
DEPTH=3
FORMAT="tree"

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--reverse) REVERSE=true; shift ;;
        -d|--depth) DEPTH="$2"; shift 2 ;;
        -f|--format) FORMAT="$2"; shift 2 ;;
        -h|--help) usage ;;
        -*) echo "Unknown option: $1"; usage ;;
        *) break ;;
    esac
done

if [ $# -lt 1 ]; then
    echo "Error: Missing file path"
    usage
fi

FILE="$1"

if [ ! -f "$FILE" ]; then
    echo -e "${RED}Error: File not found: $FILE${NC}"
    exit 1
fi

# Detect language
EXT="${FILE##*.}"
case $EXT in
    py) LANG="python" ;;
    js|jsx|ts|tsx) LANG="javascript" ;;
    *) echo "Unsupported file type: $EXT"; exit 1 ;;
esac

echo -e "${BLUE}Dependency tree for: $FILE${NC}"
echo ""

# Function to extract imports
extract_imports() {
    local file="$1"

    case $LANG in
        python)
            # Extract Python imports
            grep -E "^(import|from) " "$file" 2>/dev/null | \
                sed -E 's/from ([^ ]+) import .*/\1/' | \
                sed -E 's/import ([^ ,]+).*/\1/' | \
                grep -v "^#" | \
                sort -u
            ;;
        javascript)
            # Extract JS/TS imports
            grep -E "^import.*from" "$file" 2>/dev/null | \
                sed -E 's/.*from ['"'"'"]([^'"'"'"]+)['"'"'"].*/\1/' | \
                sort -u
            ;;
    esac
}

# Recursive dependency finder
declare -A SEEN
find_deps() {
    local file="$1"
    local depth="$2"
    local prefix="$3"

    if [ "$depth" -gt "$DEPTH" ]; then
        return
    fi

    if [ -n "${SEEN[$file]}" ]; then
        return
    fi
    SEEN["$file"]=1

    local imports=$(extract_imports "$file")

    if [ -z "$imports" ]; then
        return
    fi

    while IFS= read -r import; do
        # Skip standard library
        if [[ "$import" =~ ^(os|sys|json|typing|pathlib)$ ]]; then
            continue
        fi

        # Try to find the actual file
        local import_file=""
        if [[ "$import" =~ ^\.\.?/ ]]; then
            # Relative import
            local dir=$(dirname "$file")
            import_file="${dir}/${import}.${EXT}"
        else
            # Absolute import - search for it
            import_file=$(find . -type f -name "${import}.${EXT}" -not -path "./venv/*" -not -path "./.venv/*" | head -1)
        fi

        if [ "$FORMAT" = "tree" ]; then
            if [ -f "$import_file" ]; then
                echo -e "${prefix}${GREEN}├─ $import${NC} → $import_file"
                find_deps "$import_file" $((depth + 1)) "${prefix}│  "
            else
                echo -e "${prefix}${YELLOW}├─ $import${NC} (external)"
            fi
        elif [ "$FORMAT" = "list" ]; then
            echo "$import"
        elif [ "$FORMAT" = "mermaid" ]; then
            echo "    $(basename "$file" .$EXT) --> $import"
        fi
    done <<< "$imports"
}

# Reverse dependencies (what imports this file)
find_reverse_deps() {
    local file="$1"
    local basename=$(basename "$file" .$EXT)

    echo -e "${YELLOW}Files that import $basename:${NC}"
    echo ""

    if command -v rg &> /dev/null; then
        rg --type py --type js --type ts -l "(import|from).*$basename" . 2>/dev/null | \
            grep -v "$file" | \
            while read -r referrer; do
                echo -e "  ${GREEN}$referrer${NC}"
            done
    else
        echo "ripgrep (rg) not found - install for reverse dependency search"
    fi
}

# Execute based on mode
if [ "$REVERSE" = true ]; then
    find_reverse_deps "$FILE"
else
    if [ "$FORMAT" = "mermaid" ]; then
        echo "```mermaid"
        echo "graph LR"
    fi

    find_deps "$FILE" 1 ""

    if [ "$FORMAT" = "mermaid" ]; then
        echo "```"
    fi
fi

# Summary
if [ "$FORMAT" = "tree" ] && [ "$REVERSE" = false ]; then
    echo ""
    echo -e "${BLUE}Total unique dependencies: ${#SEEN[@]}${NC}"
fi
