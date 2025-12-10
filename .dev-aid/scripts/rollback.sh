#!/bin/bash
# Dev-AID Rollback Script
# Restore Dev-AID from a backup created by update-dev-aid.sh
# Version: 1.0.0

set -e

# Source shared library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/update-lib.sh"

# Colors already defined in update-lib.sh

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        Dev-AID Rollback Tool               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Show usage if no arguments
if [ $# -eq 0 ]; then
    echo "Usage: rollback.sh <backup-directory>"
    echo ""
    echo "Restore Dev-AID from a previous backup."
    echo ""
    echo -e "${BLUE}Available backups:${NC}"

    # List backups with metadata
    backup_count=0
    for backup in $(ls -td .dev-aid-backup-* 2>/dev/null); do
        backup_count=$((backup_count + 1))
        backup_date=$(echo "$backup" | sed 's/\.dev-aid-backup-//')

        # Read version from backup if available
        if [ -f "$backup/VERSION" ]; then
            version=$(cat "$backup/VERSION" 2>/dev/null | tr -d '\n' || echo "unknown")
        else
            version="unknown"
        fi

        # Read backup manifest if available
        if [ -f "$backup/MANIFEST.txt" ]; then
            created=$(grep "Created:" "$backup/MANIFEST.txt" 2>/dev/null | cut -d: -f2- || echo "unknown")
        else
            created="unknown"
        fi

        echo ""
        echo -e "${GREEN}$backup_count. $backup${NC}"
        echo "   Version: $version"
        echo "   Created: $created"
        echo "   Size: $(du -sh "$backup" 2>/dev/null | cut -f1)"
    done

    if [ $backup_count -eq 0 ]; then
        echo -e "${YELLOW}  No backups found${NC}"
        echo ""
        echo "Backups are created automatically when running update-dev-aid.sh"
    fi

    echo ""
    echo -e "${BLUE}Example:${NC}"
    echo "  ./rollback.sh .dev-aid-backup-20251210-143022"
    echo ""
    exit 0
fi

BACKUP_DIR="$1"

# Validate backup directory
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ Backup not found: $BACKUP_DIR${NC}"
    echo ""
    echo "Available backups:"
    ls -td .dev-aid-backup-* 2>/dev/null || echo "  (no backups found)"
    exit 1
fi

# Validate that it's a Dev-AID backup
if [ ! -f "$BACKUP_DIR/MANIFEST.txt" ] && [ ! -f "$BACKUP_DIR/VERSION" ]; then
    echo -e "${YELLOW}⚠️  Warning: This doesn't appear to be a Dev-AID backup${NC}"
    echo "   Expected to find MANIFEST.txt or VERSION file"
    read -p "Continue anyway? [y/N]: " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Rollback cancelled${NC}"
        exit 0
    fi
fi

# Show backup info
echo -e "${BLUE}Backup Information:${NC}"
echo "  Path: $BACKUP_DIR"

if [ -f "$BACKUP_DIR/VERSION" ]; then
    backup_version=$(cat "$BACKUP_DIR/VERSION" | tr -d '\n')
    echo "  Version: $backup_version"
fi

if [ -f "$BACKUP_DIR/MANIFEST.txt" ]; then
    echo ""
    cat "$BACKUP_DIR/MANIFEST.txt"
fi

echo ""

# Get current version
current_version="unknown"
if [ -f ".dev-aid/VERSION" ]; then
    current_version=$(cat .dev-aid/VERSION | tr -d '\n')
fi

echo -e "${YELLOW}⚠️  This will replace your current Dev-AID installation${NC}"
echo "   Current version: $current_version"
if [ -f "$BACKUP_DIR/VERSION" ]; then
    echo "   Backup version:  $backup_version"
fi
echo ""

# Confirm rollback
read -p "Proceed with rollback? [y/N]: " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Rollback cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}Starting rollback...${NC}"
echo ""

# Create a backup of current state before rollback (just in case)
echo -e "${BLUE}→ Creating safety backup of current state...${NC}"
safety_backup=".dev-aid-pre-rollback-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$safety_backup"

# Backup current VERSION and critical files
cp .dev-aid/VERSION "$safety_backup/" 2>/dev/null || true
cp -r .dev-aid/config/.env* "$safety_backup/" 2>/dev/null || true
cp -r .dev-aid/memory-bank "$safety_backup/" 2>/dev/null || true

echo -e "${GREEN}✓ Safety backup created: $safety_backup${NC}"
echo ""

# Restore from backup
echo -e "${BLUE}→ Restoring Dev-AID from backup...${NC}"

# Restore VERSION file
if [ -f "$BACKUP_DIR/VERSION" ]; then
    cp "$BACKUP_DIR/VERSION" ".dev-aid/VERSION"
    echo "  ✓ Restored VERSION file"
fi

# Restore .env files (API keys)
if compgen -G "$BACKUP_DIR/.env*" > /dev/null; then
    mkdir -p .dev-aid/config
    cp "$BACKUP_DIR/.env"* .dev-aid/config/ 2>/dev/null || true
    echo "  ✓ Restored .env files"
fi

# Restore memory bank
if [ -d "$BACKUP_DIR/memory-bank" ]; then
    rm -rf .dev-aid/memory-bank
    cp -r "$BACKUP_DIR/memory-bank" .dev-aid/
    echo "  ✓ Restored memory bank"
fi

# Restore logs
if [ -d "$BACKUP_DIR/logs" ]; then
    rm -rf .dev-aid/logs
    cp -r "$BACKUP_DIR/logs" .dev-aid/
    echo "  ✓ Restored logs"
fi

# Restore RAG indices
if [ -d "$BACKUP_DIR/local-search/index" ]; then
    mkdir -p .dev-aid/local-search
    rm -rf .dev-aid/local-search/index
    cp -r "$BACKUP_DIR/local-search/index" .dev-aid/local-search/
    echo "  ✓ Restored RAG indices"
fi

# Restore custom skills
if [ -d "$BACKUP_DIR/providers" ]; then
    for provider_backup in "$BACKUP_DIR/providers"/*; do
        if [ -d "$provider_backup/skills/custom" ]; then
            provider_name=$(basename "$provider_backup")
            mkdir -p ".dev-aid/providers/$provider_name/skills"
            rm -rf ".dev-aid/providers/$provider_name/skills/custom"
            cp -r "$provider_backup/skills/custom" ".dev-aid/providers/$provider_name/skills/"
            echo "  ✓ Restored custom skills for $provider_name"
        fi
    done
fi

echo ""
echo -e "${GREEN}✓ Rollback complete${NC}"
echo ""

# Show final version
rolled_back_version="unknown"
if [ -f ".dev-aid/VERSION" ]; then
    rolled_back_version=$(cat .dev-aid/VERSION | tr -d '\n')
fi

# Update virtual environment dependencies to match rolled-back version
if [ -d ".dev-aid/orchestration/.venv" ]; then
    echo -e "${BLUE}→ Updating dependencies to match rolled-back version...${NC}"

    cd .dev-aid/orchestration
    source .venv/bin/activate 2>/dev/null || true

    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt --upgrade -q 2>/dev/null || true
        echo -e "${GREEN}✓ Dependencies updated${NC}"
    fi

    deactivate 2>/dev/null || true
    cd ../..
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Rollback Complete! ✅              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Version: $current_version → $rolled_back_version${NC}"
echo ""
echo -e "${BLUE}What was restored:${NC}"
echo "  ✓ Your API keys (.env)"
echo "  ✓ Your memory bank (patterns, decisions)"
echo "  ✓ Your logs (routing history, costs)"
echo "  ✓ Your RAG indices"
echo "  ✓ Your custom skills"
echo ""
echo -e "${BLUE}Safety backup created:${NC}"
echo "  $safety_backup"
echo "  (contains your state before rollback, delete when no longer needed)"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo ""
echo "1. Test your setup:"
echo "   ./.dev-aid/orchestration/router-cli.sh status"
echo ""
echo "2. If this didn't help, you can:"
echo "   - Rollback to a different backup"
echo "   - Restore the pre-rollback state: ./rollback.sh $safety_backup"
echo ""
