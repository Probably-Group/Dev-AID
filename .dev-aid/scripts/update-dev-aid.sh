#!/bin/bash
# Dev-AID Enhanced Update Script
# Safely updates Dev-AID with conflict detection, checksums, and rollback
# Version: 2.0.0

set -e

# Source shared library
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/update-lib.sh"

# Parse arguments
DRY_RUN=false
FORCE=false
SKIP_CONFLICTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --skip-conflicts)
            SKIP_CONFLICTS=true
            shift
            ;;
        --help|-h)
            cat <<EOF
Usage: update-dev-aid.sh [options]

Options:
  --dry-run         Preview changes without applying them
  --force           Skip conflict resolution (take all upstream)
  --skip-conflicts  Skip files with conflicts (don't update)
  --help, -h        Show this help message

Examples:
  # Preview update
  ./update-dev-aid.sh --dry-run

  # Interactive update with conflict resolution
  ./update-dev-aid.sh

  # Force update (overwrite all conflicts)
  ./update-dev-aid.sh --force

For more information, see: .dev-aid/docs/UPDATE-SYSTEM-GUIDE.md
EOF
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Header
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Dev-AID Enhanced Update Tool           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

if $DRY_RUN; then
    echo -e "${CYAN}🔍 DRY RUN MODE (no changes will be made)${NC}"
    echo ""
fi

# Validate Dev-AID repository
if ! validate_dev_aid_repo; then
    exit 1
fi

# Check dependencies
if ! check_dependencies; then
    exit 1
fi

# Get current version
CURRENT_VERSION=$(cat .dev-aid/VERSION | tr -d '\n')
echo -e "${BLUE}→ Current Dev-AID version: ${CURRENT_VERSION}${NC}"
echo ""

# Fetch latest version from GitHub
echo -e "${BLUE}→ Checking for updates...${NC}"

LATEST_VERSION=$(python3 .dev-aid/orchestration/github_client.py get-latest-version 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$LATEST_VERSION" ]; then
    echo -e "${YELLOW}⚠️  Could not fetch latest version from GitHub${NC}"
    echo "   Proceeding with manual update..."
    LATEST_VERSION="unknown"
else
    echo -e "${GREEN}✓ Latest version: ${LATEST_VERSION}${NC}"

    # Check if update is needed
    if [ "$LATEST_VERSION" != "unknown" ]; then
        if ! is_version_greater "$LATEST_VERSION" "$CURRENT_VERSION"; then
            echo ""
            echo -e "${GREEN}✅ Dev-AID is already up to date!${NC}"
            echo "   Current version: $CURRENT_VERSION"
            echo "   Latest version:  $LATEST_VERSION"
            echo ""
            exit 0
        fi

        # Check for breaking changes
        check_breaking_changes "$CURRENT_VERSION" "$LATEST_VERSION"
    fi
fi

echo ""

# Ask for update source
echo -e "${YELLOW}Update source options:${NC}"
echo "  1. Download from GitHub (recommended)"
echo "  2. Pull from git remote"
echo "  3. Copy from local Dev-AID installation"
echo ""
read -p "Choose option [1-3]: " -n 1 -r UPDATE_SOURCE
echo ""
echo ""

# Create backup
if ! $DRY_RUN; then
    BACKUP_DIR=$(create_backup)

    # Set up error trap for automatic rollback
    setup_error_trap "$BACKUP_DIR"
else
    BACKUP_DIR=".dev-aid-backup-dry-run"
    echo -e "${CYAN}[DRY-RUN] Would create backup: $BACKUP_DIR${NC}"
fi

# Temporary directory for download/extraction
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Update based on chosen method
case $UPDATE_SOURCE in
    1)
        echo -e "${GREEN}Downloading from GitHub...${NC}"
        echo ""

        # Download latest release
        if ! $DRY_RUN; then
            echo -e "${BLUE}→ Fetching release assets...${NC}"

            # Download main archive (assumes dev-aid.tar.gz or similar)
            # Note: This is a placeholder - actual implementation would download specific assets
            echo -e "${YELLOW}  Note: GitHub download not yet fully implemented${NC}"
            echo -e "${YELLOW}  Please use option 2 (git remote) or 3 (local copy)${NC}"
            exit 1
        else
            echo -e "${CYAN}[DRY-RUN] Would download from GitHub${NC}"
        fi
        ;;

    2)
        echo -e "${GREEN}Updating from git remote...${NC}"
        echo ""

        # Check if git remote for dev-aid-upstream exists
        if ! git remote | grep -q "dev-aid-upstream"; then
            echo -e "${BLUE}→ Adding Dev-AID remote...${NC}"

            if ! $DRY_RUN; then
                read -p "Enter Dev-AID repository URL: " DEV_AID_REPO
                git remote add dev-aid-upstream "$DEV_AID_REPO"
            else
                echo -e "${CYAN}[DRY-RUN] Would add dev-aid-upstream remote${NC}"
            fi
        fi

        echo -e "${BLUE}→ Fetching latest Dev-AID...${NC}"

        if ! $DRY_RUN; then
            git fetch dev-aid-upstream main

            echo -e "${BLUE}→ Extracting .dev-aid/ directory...${NC}"
            # Extract to temporary directory
            mkdir -p "$TEMP_DIR/.dev-aid"
            git archive dev-aid-upstream/main .dev-aid/ | tar -x -C "$TEMP_DIR"

            echo -e "${GREEN}✓ Fetched from git remote${NC}"
        else
            echo -e "${CYAN}[DRY-RUN] Would fetch from dev-aid-upstream/main${NC}"
            echo -e "${CYAN}[DRY-RUN] Would extract .dev-aid/ to temp directory${NC}"
        fi
        ;;

    3)
        echo -e "${GREEN}Copying from local installation...${NC}"
        echo ""

        if ! $DRY_RUN; then
            read -p "Enter path to Dev-AID repository: " DEV_AID_PATH

            if [ ! -d "$DEV_AID_PATH/.dev-aid" ]; then
                echo -e "${RED}✗ Error: Invalid path (no .dev-aid/ found)${NC}"
                exit 1
            fi

            echo -e "${BLUE}→ Copying .dev-aid/ directory...${NC}"
            cp -r "$DEV_AID_PATH/.dev-aid" "$TEMP_DIR/"

            echo -e "${GREEN}✓ Copied from local installation${NC}"
        else
            echo -e "${CYAN}[DRY-RUN] Would copy from local path${NC}"
        fi
        ;;

    *)
        echo -e "${RED}✗ Invalid option${NC}"
        exit 1
        ;;
esac

echo ""

# Detect conflicts
if [ -d "$TEMP_DIR/.dev-aid" ] || $DRY_RUN; then
    echo -e "${BLUE}🔍 Checking for conflicts...${NC}"

    # Create file list for conflict detection
    FILE_LIST="$TEMP_DIR/files.txt"

    if ! $DRY_RUN; then
        # Generate list of files that will be updated
        find "$TEMP_DIR/.dev-aid" -type f -printf "%P\n" > "$FILE_LIST"
    else
        echo -e "${CYAN}[DRY-RUN] Would scan for conflicts${NC}"
        # Create dummy file list for dry-run
        echo "scripts/update-dev-aid.sh" > "$FILE_LIST"
        echo "templates/ci/python.yml" >> "$FILE_LIST"
    fi

    # Run conflict resolver
    if $FORCE; then
        echo -e "${YELLOW}⚠️  Force mode: All conflicts will be overwritten${NC}"
        CONFLICTS=0
    elif $SKIP_CONFLICTS; then
        echo -e "${YELLOW}⚠️  Skip mode: Conflicting files will not be updated${NC}"
        CONFLICTS=0
    else
        # Interactive conflict resolution
        if ! $DRY_RUN; then
            python3 .dev-aid/orchestration/conflict_resolver.py \
                "$BACKUP_DIR" \
                "$TEMP_DIR" \
                "$FILE_LIST"

            CONFLICTS=$(cat /tmp/dev-aid-conflict-count.txt 2>/dev/null || echo "0")
        else
            python3 .dev-aid/orchestration/conflict_resolver.py \
                "$BACKUP_DIR" \
                "$TEMP_DIR" \
                "$FILE_LIST" \
                --dry-run

            CONFLICTS=$(cat /tmp/dev-aid-conflict-count.txt 2>/dev/null || echo "2")
        fi

        echo ""
        if [ "$CONFLICTS" -gt 0 ]; then
            echo -e "${YELLOW}📊 Resolved $CONFLICTS conflicts${NC}"
        else
            echo -e "${GREEN}✓ No conflicts detected${NC}"
        fi
    fi
fi

echo ""

# Apply update
if ! $DRY_RUN; then
    echo -e "${GREEN}Applying update...${NC}"

    # Copy updated files (excluding protected paths)
    echo -e "${BLUE}→ Copying updated files...${NC}"

    # Use rsync with exclusions for protected paths
    PROTECTED_PATHS=$(get_protected_paths)
    EXCLUDE_ARGS=""
    while IFS= read -r path; do
        EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude=$path"
    done <<< "$PROTECTED_PATHS"

    rsync -av $EXCLUDE_ARGS "$TEMP_DIR/.dev-aid/" ".dev-aid/"

    echo -e "${GREEN}✓ Files updated${NC}"
else
    echo -e "${CYAN}[DRY-RUN] Would copy files with rsync (excluding protected paths)${NC}"
fi

echo ""

# Restore user data
if ! $DRY_RUN; then
    echo -e "${GREEN}Restoring protected data...${NC}"

    # Restore from backup
    restore_from_backup "$BACKUP_DIR"

    echo -e "${GREEN}✓ Protected data restored${NC}"
else
    echo -e "${CYAN}[DRY-RUN] Would restore protected data from backup${NC}"
fi

echo ""

# Update dependencies
if ! $DRY_RUN; then
    update_python_deps ".dev-aid/orchestration/.venv"
else
    echo -e "${CYAN}[DRY-RUN] Would update Python dependencies${NC}"
fi

# Get new version
NEW_VERSION="unknown"
if [ -f ".dev-aid/VERSION" ]; then
    NEW_VERSION=$(cat .dev-aid/VERSION | tr -d '\n')
fi

# Show summary
echo ""
if ! $DRY_RUN; then
    show_update_summary "$CURRENT_VERSION" "$NEW_VERSION" "$BACKUP_DIR"
    show_next_steps "$BACKUP_DIR"

    # Cleanup old backups
    cleanup_old_backups 3
else
    echo -e "${CYAN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║       Dry Run Complete! ✅                 ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"
    echo ""
    echo "No changes were made to your installation."
    echo ""
    echo "To apply this update, run:"
    echo "  ./update-dev-aid.sh"
    echo ""
fi

exit 0
