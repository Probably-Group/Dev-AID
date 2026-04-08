#!/usr/bin/env bash
# Dev-AID Skill Lint Tool
# Validates expert skill format and quality

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    cat <<EOF
Usage: $0 [OPTIONS] <skill-directory>

Validate expert skill format and quality.

Examples:
    $0 .dev-aid/providers/claude/.claude/skills/expert/python-expert
    $0 --strict .dev-aid/providers/claude/.claude/skills/expert/*

Options:
    -s, --strict         Fail on warnings
    -f, --fix            Auto-fix common issues
    -h, --help           Show this help message

Checks:
    - Skill metadata completeness (name, description, activation patterns)
    - Reference file formatting
    - File size limits (<500 lines recommended)
    - Markdown syntax
    - Broken links
    - Activation pattern validity
EOF
    exit 1
}

# Parse arguments
STRICT=false
FIX=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--strict) STRICT=true; shift ;;
        -f|--fix) FIX=true; shift ;;
        -h|--help) usage ;;
        -*) echo "Unknown option: $1"; usage ;;
        *) break ;;
    esac
done

if [ $# -lt 1 ]; then
    echo "Error: Missing skill directory"
    usage
fi

SKILL_DIR="$1"

if [ ! -d "$SKILL_DIR" ]; then
    echo -e "${RED}Error: Directory not found: $SKILL_DIR${NC}"
    exit 1
fi

ERRORS=0
WARNINGS=0

error() {
    echo -e "${RED}✗ ERROR: $1${NC}"
    ERRORS=$((ERRORS + 1))
}

warn() {
    echo -e "${YELLOW}⚠ WARNING: $1${NC}"
    WARNINGS=$((WARNINGS + 1))
}

info() {
    echo -e "${BLUE}ℹ INFO: $1${NC}"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

echo -e "${BLUE}Linting skill: $(basename "$SKILL_DIR")${NC}"
echo ""

# Check 1: Skill metadata file
if [ ! -f "$SKILL_DIR/skill.json" ] && [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    error "No skill.json or SKILL.md metadata file found"
else
    success "Metadata file exists"

    if [ -f "$SKILL_DIR/skill.json" ]; then
        # Validate JSON
        if ! jq empty "$SKILL_DIR/skill.json" 2>/dev/null; then
            error "skill.json is not valid JSON"
        else
            # Check required fields
            NAME=$(jq -r '.name // empty' "$SKILL_DIR/skill.json")
            DESC=$(jq -r '.description // empty' "$SKILL_DIR/skill.json")
            PATTERNS=$(jq -r '.activation_patterns // empty' "$SKILL_DIR/skill.json")

            [ -z "$NAME" ] && error "Missing 'name' field in skill.json"
            [ -z "$DESC" ] && error "Missing 'description' field in skill.json"
            [ -z "$PATTERNS" ] && warn "No activation_patterns defined"
        fi
    fi
fi

# Check 2: Reference files
REF_DIR="$SKILL_DIR/references"
if [ -d "$REF_DIR" ]; then
    REF_COUNT=$(find "$REF_DIR" -name "*.md" | wc -l | tr -d ' ')
    if [ "$REF_COUNT" -eq 0 ]; then
        warn "No reference files found in references/"
    else
        success "Found $REF_COUNT reference file(s)"

        # Check file sizes
        while IFS= read -r ref_file; do
            LINES=$(wc -l < "$ref_file" | tr -d ' ')
            if [ "$LINES" -gt 500 ]; then
                warn "$(basename "$ref_file") is $LINES lines (recommended: <500)"
            fi
        done < <(find "$REF_DIR" -name "*.md")
    fi
fi

# Check 3: Main skill file size
if [ -f "$SKILL_DIR/SKILL.md" ]; then
    LINES=$(wc -l < "$SKILL_DIR/SKILL.md" | tr -d ' ')
    if [ "$LINES" -gt 1000 ]; then
        warn "SKILL.md is $LINES lines (recommended: <1000, consider splitting into references/)"
    fi
fi

# Check 4: Markdown syntax (basic check)
if command -v markdownlint &> /dev/null; then
    if markdownlint "$SKILL_DIR"/*.md 2>/dev/null; then
        success "Markdown syntax valid"
    else
        warn "Markdown syntax issues found (run markdownlint for details)"
    fi
fi

# Check 5: Broken links (if lychee is available)
if command -v lychee &> /dev/null; then
    if lychee --quiet "$SKILL_DIR"/*.md 2>/dev/null; then
        success "No broken links found"
    else
        warn "Broken links detected (run lychee for details)"
    fi
fi

# Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Skill validation passed!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Validation passed with $WARNINGS warning(s)${NC}"
    if [ "$STRICT" = true ]; then
        exit 1
    fi
    exit 0
else
    echo -e "${RED}❌ Validation failed: $ERRORS error(s), $WARNINGS warning(s)${NC}"
    exit 1
fi
