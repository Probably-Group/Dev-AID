#!/bin/bash
# Install Dev-AID git hooks
#
# Usage:
#   ./install-hooks.sh

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🔧 Installing Dev-AID Git Hooks${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# Get the repository root
REPO_ROOT=$(git rev-parse --show-toplevel)
HOOKS_DIR="$REPO_ROOT/.dev-aid/automation/git-hooks"
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"

# Check if we're in a git repository
if [ ! -d "$REPO_ROOT/.git" ]; then
    echo -e "${YELLOW}❌ Not in a git repository${NC}"
    exit 1
fi

# Create .git/hooks directory if it doesn't exist
mkdir -p "$GIT_HOOKS_DIR"

# Install available hooks
HOOKS_INSTALLED=0

for hook_file in "$HOOKS_DIR"/*; do
    # Skip this installation script
    if [ "$(basename "$hook_file")" = "install-hooks.sh" ]; then
        continue
    fi

    # Skip if not a file
    if [ ! -f "$hook_file" ]; then
        continue
    fi

    hook_name=$(basename "$hook_file")
    target="$GIT_HOOKS_DIR/$hook_name"

    # Check if hook already exists
    if [ -e "$target" ] || [ -L "$target" ]; then
        echo -e "${YELLOW}⚠️  $hook_name already exists - skipping${NC}"
        echo "   To reinstall: rm $target && ./install-hooks.sh"
        continue
    fi

    # Create symlink
    ln -s "$hook_file" "$target"
    chmod +x "$target"

    echo -e "${GREEN}✅ Installed: $hook_name${NC}"
    HOOKS_INSTALLED=$((HOOKS_INSTALLED + 1))
done

echo
if [ $HOOKS_INSTALLED -eq 0 ]; then
    echo -e "${YELLOW}No new hooks installed${NC}"
else
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ Installed $HOOKS_INSTALLED hook(s)${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
fi

echo
echo -e "${BLUE}💡 Configuration:${NC}"
echo "   Enable auto-conflict resolution:"
echo "     export DEV_AID_AUTO_RESOLVE=true"
echo

echo -e "${GREEN}Done!${NC}"
