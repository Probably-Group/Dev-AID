#!/usr/bin/env bash
# Dev-AID Update Checker
# Checks for available Dev-AID updates (used by automated checks)
# Version: 1.0.0

set -euo pipefail

# Source shared library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/update-lib.sh"

# Configuration
CACHE_FILE=".dev-aid/.update-check-cache"
CACHE_TTL=604800  # 7 days in seconds (configurable)
STATUS_FILE=".dev-aid/.update-status"

# Parse arguments
SILENT=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --silent)
            SILENT=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help|-h)
            echo "Usage: check-updates.sh [options]"
            echo ""
            echo "Options:"
            echo "  --silent   Silent mode (no output, writes to status file)"
            echo "  --force    Force check (ignore cache)"
            echo "  --help     Show this help"
            echo ""
            echo "Cache TTL: $CACHE_TTL seconds ($(($CACHE_TTL / 86400)) days)"
            echo "Cache location: $CACHE_FILE"
            echo "Status file: $STATUS_FILE"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if cache is still valid
if [ -f "$CACHE_FILE" ] && [ "$FORCE" = false ]; then
    # Get cache age (cross-platform)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        CACHE_MOD_TIME=$(stat -f %m "$CACHE_FILE" 2>/dev/null || echo "0")
    else
        # Linux
        CACHE_MOD_TIME=$(stat -c %Y "$CACHE_FILE" 2>/dev/null || echo "0")
    fi

    CURRENT_TIME=$(date +%s)
    CACHE_AGE=$((CURRENT_TIME - CACHE_MOD_TIME))

    if [ $CACHE_AGE -lt $CACHE_TTL ]; then
        # Cache is valid
        if [ "$SILENT" = false ]; then
            echo -e "${BLUE}Using cached update check ($(($CACHE_AGE / 3600)) hours old)${NC}"
            echo "Use --force to check now"
        fi

        # Read cached status if available
        if [ -f "$STATUS_FILE" ]; then
            if grep -q "update_available=true" "$STATUS_FILE"; then
                LATEST_VERSION=$(grep "latest_version=" "$STATUS_FILE" | cut -d= -f2)
                if [ "$SILENT" = false ]; then
                    echo ""
                    echo -e "${YELLOW}💡 Dev-AID update available: $LATEST_VERSION${NC}"
                    echo "   Run: ./.dev-aid/scripts/update-dev-aid.sh"
                fi
            fi
        fi

        exit 0
    fi
fi

# Validate Dev-AID repository
if ! validate_dev_aid_repo; then
    exit 1
fi

# Get current version
CURRENT_VERSION=$(cat .dev-aid/VERSION | tr -d '\n')

if [ "$SILENT" = false ]; then
    echo -e "${BLUE}Checking for Dev-AID updates...${NC}"
    echo "  Current version: $CURRENT_VERSION"
fi

# Fetch latest release from GitHub
if [ "$SILENT" = false ]; then
    echo -e "${BLUE}→ Fetching latest release from GitHub...${NC}"
fi

LATEST_VERSION=$(python3 .dev-aid/orchestration/github_client.py get-latest-version 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$LATEST_VERSION" ]; then
    if [ "$SILENT" = false ]; then
        echo -e "${RED}❌ Failed to check for updates${NC}"
        echo "   Check your internet connection or GitHub API status"
    fi
    exit 1
fi

# Update cache
echo "$LATEST_VERSION" > "$CACHE_FILE"
echo "last_check=$(date +%s)" >> "$CACHE_FILE"

# Compare versions
if is_version_greater "$LATEST_VERSION" "$CURRENT_VERSION"; then
    # Update available
    if [ "$SILENT" = true ]; then
        # Silent mode: write to status file
        cat > "$STATUS_FILE" <<EOF
update_available=true
current_version=$CURRENT_VERSION
latest_version=$LATEST_VERSION
checked_at=$(date -Iseconds)
EOF
    else
        # Interactive mode: show notification
        echo ""
        echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║    💡 Dev-AID Update Available!           ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${BLUE}  Current: $CURRENT_VERSION${NC}"
        echo -e "${GREEN}  Latest:  $LATEST_VERSION${NC}"
        echo ""

        # Check for breaking changes
        if has_breaking_changes "$CURRENT_VERSION" "$LATEST_VERSION"; then
            echo -e "${YELLOW}  ⚠️  Major version change (may have breaking changes)${NC}"
            echo ""
        fi

        # Fetch release notes preview
        echo -e "${BLUE}Release Notes:${NC}"
        RELEASE_NOTES=$(python3 .dev-aid/orchestration/github_client.py get-release-notes 2>/dev/null | head -10)
        if [ -n "$RELEASE_NOTES" ]; then
            echo "$RELEASE_NOTES"
            echo "  ..."
        fi
        echo ""

        echo -e "${GREEN}To update:${NC}"
        echo "  ./.dev-aid/scripts/update-dev-aid.sh"
        echo ""
        echo -e "${BLUE}To preview changes:${NC}"
        echo "  ./.dev-aid/scripts/update-dev-aid.sh --dry-run"
        echo ""
    fi
else
    # No update available
    if [ "$SILENT" = true ]; then
        cat > "$STATUS_FILE" <<EOF
update_available=false
current_version=$CURRENT_VERSION
latest_version=$LATEST_VERSION
checked_at=$(date -Iseconds)
EOF
    else
        echo ""
        echo -e "${GREEN}✅ Dev-AID is up to date ($CURRENT_VERSION)${NC}"
        echo ""
    fi
fi
