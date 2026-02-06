#!/usr/bin/env bash
# Dev-AID Update Script
# Safely updates Dev-AID to the latest version in existing repositories

set -euo pipefail  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        Dev-AID Update Tool                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in a Dev-AID enabled repository
if [ ! -d ".dev-aid" ]; then
    echo -e "${RED}✗ Error: Not in a Dev-AID repository${NC}"
    echo "  Expected to find .dev-aid/ directory"
    exit 1
fi

# Get current version
CURRENT_VERSION="unknown"
if [ -f ".dev-aid/VERSION" ]; then
    CURRENT_VERSION=$(cat .dev-aid/VERSION | tr -d '\n')
fi

echo -e "${BLUE}→ Current Dev-AID version: ${CURRENT_VERSION}${NC}"
echo ""

# Ask for update source
echo -e "${YELLOW}Update source options:${NC}"
echo "  1. Pull from official repository (recommended)"
echo "  2. Copy from local Dev-AID installation"
echo "  3. Manual update (guide only)"
echo ""
read -p "Choose option [1-3]: " -n 1 -r UPDATE_SOURCE
echo ""

# Create backup
echo ""
echo -e "${GREEN}Creating backup...${NC}"
BACKUP_DIR=".dev-aid-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup critical files that should NEVER be overwritten
echo -e "${BLUE}→ Backing up user data...${NC}"
cp -r .dev-aid/config/.env* "$BACKUP_DIR/" 2>/dev/null || true
cp -r .dev-aid/memory-bank "$BACKUP_DIR/" 2>/dev/null || true
cp -r .dev-aid/logs "$BACKUP_DIR/" 2>/dev/null || true
cp .dev-aid/VERSION "$BACKUP_DIR/" 2>/dev/null || true

echo -e "${GREEN}✓ Backup created: ${BACKUP_DIR}${NC}"
echo ""

# Update based on chosen method
case $UPDATE_SOURCE in
    1)
        echo -e "${GREEN}Updating from official repository...${NC}"
        echo ""

        # Check if git remote for dev-aid-upstream exists
        if ! git remote | grep -q "dev-aid-upstream"; then
            echo -e "${BLUE}→ Adding Dev-AID remote...${NC}"
            read -p "Enter Dev-AID repository URL: " DEV_AID_REPO
            git remote add dev-aid-upstream "$DEV_AID_REPO"
        fi

        echo -e "${BLUE}→ Fetching latest Dev-AID...${NC}"
        git fetch dev-aid-upstream main

        echo -e "${BLUE}→ Extracting .dev-aid/ directory...${NC}"
        # Use git archive to extract only .dev-aid folder
        git archive --remote=dev-aid-upstream main .dev-aid/ | tar -x

        echo -e "${GREEN}✓ Updated from repository${NC}"
        ;;

    2)
        echo -e "${GREEN}Copying from local installation...${NC}"
        echo ""
        read -p "Enter path to Dev-AID repository: " DEV_AID_PATH

        if [ ! -d "$DEV_AID_PATH/.dev-aid" ]; then
            echo -e "${RED}✗ Error: Invalid path (no .dev-aid/ found)${NC}"
            exit 1
        fi

        echo -e "${BLUE}→ Copying .dev-aid/ directory...${NC}"
        # Copy everything except user data
        rsync -av --exclude='.env*' --exclude='memory-bank/' --exclude='logs/' \
              --exclude='.venv/' "$DEV_AID_PATH/.dev-aid/" ".dev-aid/"

        echo -e "${GREEN}✓ Copied from local installation${NC}"
        ;;

    3)
        echo -e "${YELLOW}Manual update mode${NC}"
        echo ""
        echo "To manually update Dev-AID:"
        echo "1. Download latest Dev-AID release"
        echo "2. Copy .dev-aid/ folder to your project (except .env and memory-bank/)"
        echo "3. Run this script again to verify"
        echo ""
        echo "Backup created at: ${BACKUP_DIR}"
        exit 0
        ;;

    *)
        echo -e "${RED}✗ Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Restoring user data...${NC}"

# Restore API keys
if [ -d "$BACKUP_DIR" ]; then
    echo -e "${BLUE}→ Restoring .env files...${NC}"
    cp -r "$BACKUP_DIR/.env"* .dev-aid/config/ 2>/dev/null || echo -e "${YELLOW}  (no .env files to restore)${NC}"

    echo -e "${BLUE}→ Merging memory bank...${NC}"
    # Keep newer versions of memory bank files
    if [ -d "$BACKUP_DIR/memory-bank" ]; then
        for file in "$BACKUP_DIR/memory-bank"/*.md; do
            filename=$(basename "$file")

            # If backup is newer, ask user
            if [ -f ".dev-aid/memory-bank/$filename" ]; then
                if [ "$file" -nt ".dev-aid/memory-bank/$filename" ]; then
                    echo -e "${YELLOW}  Your $filename is newer than default${NC}"
                    read -p "  Keep your version? [Y/n]: " -n 1 -r
                    echo
                    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                        cp "$file" ".dev-aid/memory-bank/$filename"
                    fi
                fi
            else
                # New file in backup, restore it
                cp "$file" ".dev-aid/memory-bank/"
            fi
        done
    fi

    echo -e "${BLUE}→ Restoring logs...${NC}"
    cp -r "$BACKUP_DIR/logs"/* .dev-aid/logs/ 2>/dev/null || echo -e "${YELLOW}  (no logs to restore)${NC}"
fi

echo -e "${GREEN}✓ User data restored${NC}"
echo ""

# Update dependencies
echo -e "${GREEN}Updating dependencies...${NC}"
echo ""

if [ -d ".dev-aid/orchestration/.venv" ]; then
    echo -e "${BLUE}→ Updating router virtual environment...${NC}"
    cd .dev-aid/orchestration

    source .venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt --upgrade -q
    deactivate

    cd ../..
    echo -e "${GREEN}✓ Router dependencies updated${NC}"
else
    echo -e "${YELLOW}⚠ No router venv found - run setup-venv.sh if needed${NC}"
fi

# Check new version
NEW_VERSION="unknown"
if [ -f ".dev-aid/VERSION" ]; then
    NEW_VERSION=$(cat .dev-aid/VERSION | tr -d '\n')
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Update Complete! 🎉                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Version: ${CURRENT_VERSION} → ${NEW_VERSION}${NC}"
echo ""
echo -e "${BLUE}What was updated:${NC}"
echo "  ✓ Router code (.dev-aid/orchestration/router/)"
echo "  ✓ Scripts (.dev-aid/scripts/)"
echo "  ✓ Documentation (.dev-aid/docs/)"
echo "  ✓ Provider configs (skills, commands)"
echo "  ✓ Dependencies (requirements.txt)"
echo ""
echo -e "${BLUE}What was preserved:${NC}"
echo "  ✓ Your API keys (.env)"
echo "  ✓ Your memory bank (patterns, decisions)"
echo "  ✓ Your logs (routing history, costs)"
echo ""
echo -e "${BLUE}Backup location:${NC}"
echo "  ${BACKUP_DIR}"
echo "  (delete this after verifying everything works)"
echo ""

# Check for breaking changes
if [ -f ".dev-aid/CHANGELOG.md" ]; then
    echo -e "${YELLOW}Recent changes:${NC}"
    grep -A 5 "## \[${NEW_VERSION}\]" .dev-aid/CHANGELOG.md 2>/dev/null || echo "  (check CHANGELOG.md for details)"
    echo ""
fi

echo -e "${GREEN}Test your setup:${NC}"
echo "  ./.dev-aid/orchestration/router-cli.sh status"
echo ""
echo -e "${GREEN}View changelog:${NC}"
echo "  cat .dev-aid/CHANGELOG.md"
echo ""
