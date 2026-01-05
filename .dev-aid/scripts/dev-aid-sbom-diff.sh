#!/bin/bash
# Dev-AID SBOM Diff Tool
# Compare Software Bill of Materials between two releases

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Usage
usage() {
    cat <<EOF
Usage: $0 [OPTIONS] <old-version> <new-version>

Compare SBOM dependencies between two releases.

Examples:
    $0 v1.2.0 v1.3.0                    # Compare two release tags
    $0 v1.2.0 HEAD                      # Compare release with current code
    $0 --format spdx v1.2.0 v1.3.0      # Use SPDX format instead of CycloneDX

Options:
    -f, --format <format>    SBOM format: cyclonedx (default) or spdx
    -o, --output <file>      Save diff to file instead of stdout
    -h, --help               Show this help message

Description:
    This tool downloads SBOMs from GitHub releases and compares them to show:
    - New dependencies added
    - Dependencies removed
    - Dependencies with version changes
    - Summary of changes

Requirements:
    - gh (GitHub CLI) installed and authenticated
    - jq for JSON processing
EOF
    exit 1
}

# Parse arguments
FORMAT="cyclonedx"
OUTPUT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--format)
            FORMAT="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        -*)
            echo "Unknown option: $1"
            usage
            ;;
        *)
            break
            ;;
    esac
done

# Check arguments
if [ $# -lt 2 ]; then
    echo "Error: Missing required arguments"
    usage
fi

OLD_VERSION="$1"
NEW_VERSION="$2"

# Check dependencies
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install: brew install gh"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is not installed${NC}"
    echo "Install: brew install jq"
    exit 1
fi

# Determine SBOM filename based on format
if [ "$FORMAT" = "spdx" ]; then
    SBOM_FILE="sbom-spdx.json"
else
    SBOM_FILE="sbom-cyclonedx.json"
fi

# Create temp directory
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

OLD_SBOM="$TEMP_DIR/old-sbom.json"
NEW_SBOM="$TEMP_DIR/new-sbom.json"

echo -e "${BLUE}Fetching SBOM for $OLD_VERSION...${NC}"

# Handle HEAD special case
if [ "$NEW_VERSION" = "HEAD" ]; then
    echo -e "${YELLOW}Generating SBOM for current code...${NC}"

    # Check if trivy is installed
    if ! command -v trivy &> /dev/null; then
        echo -e "${RED}Error: trivy is not installed${NC}"
        echo "Install: brew install trivy"
        exit 1
    fi

    # Generate SBOM for current code
    if [ "$FORMAT" = "spdx" ]; then
        trivy fs --format spdx-json --output "$NEW_SBOM" .
    else
        trivy fs --format cyclonedx --output "$NEW_SBOM" .
    fi
else
    # Download from release
    if ! gh release download "$NEW_VERSION" --pattern "$SBOM_FILE" --output "$NEW_SBOM" 2>/dev/null; then
        echo -e "${RED}Error: Failed to download SBOM for $NEW_VERSION${NC}"
        echo "Make sure the release exists and includes SBOM files"
        exit 1
    fi
fi

# Download old SBOM
if ! gh release download "$OLD_VERSION" --pattern "$SBOM_FILE" --output "$OLD_SBOM" 2>/dev/null; then
    echo -e "${RED}Error: Failed to download SBOM for $OLD_VERSION${NC}"
    echo "Make sure the release exists and includes SBOM files"
    exit 1
fi

echo -e "${GREEN}✓ SBOMs downloaded${NC}"
echo ""

# Extract dependencies
echo -e "${BLUE}Analyzing dependencies...${NC}"

if [ "$FORMAT" = "spdx" ]; then
    # SPDX format parsing
    OLD_DEPS=$(jq -r '.packages[] | "\(.name)@\(.versionInfo // "unknown")"' "$OLD_SBOM" | sort)
    NEW_DEPS=$(jq -r '.packages[] | "\(.name)@\(.versionInfo // "unknown")"' "$NEW_SBOM" | sort)
else
    # CycloneDX format parsing
    OLD_DEPS=$(jq -r '.components[] | "\(.name)@\(.version // "unknown")"' "$OLD_SBOM" | sort)
    NEW_DEPS=$(jq -r '.components[] | "\(.name)@\(.version // "unknown")"' "$NEW_SBOM" | sort)
fi

# Save to temp files
echo "$OLD_DEPS" > "$TEMP_DIR/old.txt"
echo "$NEW_DEPS" > "$TEMP_DIR/new.txt"

# Find differences
ADDED=$(comm -13 "$TEMP_DIR/old.txt" "$TEMP_DIR/new.txt")
REMOVED=$(comm -23 "$TEMP_DIR/old.txt" "$TEMP_DIR/new.txt")

# Find version changes (same package, different version)
OLD_NAMES=$(echo "$OLD_DEPS" | cut -d@ -f1 | sort)
NEW_NAMES=$(echo "$NEW_DEPS" | cut -d@ -f1 | sort)
COMMON_NAMES=$(comm -12 <(echo "$OLD_NAMES") <(echo "$NEW_NAMES"))

CHANGED=""
while IFS= read -r pkg; do
    OLD_VER=$(echo "$OLD_DEPS" | grep "^${pkg}@" | cut -d@ -f2)
    NEW_VER=$(echo "$NEW_DEPS" | grep "^${pkg}@" | cut -d@ -f2)
    if [ "$OLD_VER" != "$NEW_VER" ]; then
        CHANGED+="${pkg}: ${OLD_VER} → ${NEW_VER}"$'\n'
    fi
done <<< "$COMMON_NAMES"

# Generate report
REPORT=$(cat <<EOF
# 📦 SBOM Diff Report

**Comparing:** $OLD_VERSION → $NEW_VERSION
**Format:** $FORMAT
**Date:** $(date +"%Y-%m-%d %H:%M:%S")

---

## 📊 Summary

- **Added:** $(echo "$ADDED" | grep -c . || echo 0) dependencies
- **Removed:** $(echo "$REMOVED" | grep -c . || echo 0) dependencies
- **Changed:** $(echo "$CHANGED" | grep -c . || echo 0) version updates
- **Total (old):** $(echo "$OLD_DEPS" | wc -l | tr -d ' ')
- **Total (new):** $(echo "$NEW_DEPS" | wc -l | tr -d ' ')

---

EOF
)

if [ -n "$ADDED" ]; then
    REPORT+=$(cat <<EOF
## ➕ Added Dependencies

\`\`\`
$ADDED
\`\`\`

EOF
)
fi

if [ -n "$REMOVED" ]; then
    REPORT+=$(cat <<EOF
## ➖ Removed Dependencies

\`\`\`
$REMOVED
\`\`\`

EOF
)
fi

if [ -n "$CHANGED" ]; then
    REPORT+=$(cat <<EOF
## 🔄 Version Changes

\`\`\`
$CHANGED
\`\`\`

EOF
)
fi

if [ -z "$ADDED" ] && [ -z "$REMOVED" ] && [ -z "$CHANGED" ]; then
    REPORT+="✅ No dependency changes detected"
fi

# Output
if [ -n "$OUTPUT" ]; then
    echo "$REPORT" > "$OUTPUT"
    echo -e "${GREEN}✓ Diff saved to $OUTPUT${NC}"
else
    echo "$REPORT"
fi
