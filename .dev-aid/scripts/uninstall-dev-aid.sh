#!/usr/bin/env bash
# Dev-AID Uninstall Script
#
# Removes Dev-AID from the current project:
#   - .dev-aid/                       (entire infrastructure dir)
#   - CLAUDE.md, GEMINI.md, OPENAI.md (provider symlinks/files at project root)
#   - .claude/, .gemini/, .codex/     (provider config dirs)
#   - .cursor/rules/dev-aid*          (Cursor rules added by Dev-AID)
#
# Offers to export the memory bank before deletion so user notes are preserved.
#
# Usage:
#   ./.dev-aid/scripts/uninstall-dev-aid.sh             # interactive
#   ./.dev-aid/scripts/uninstall-dev-aid.sh --yes       # non-interactive
#   ./.dev-aid/scripts/uninstall-dev-aid.sh --dry-run   # show what would be removed
#
# Exit codes:
#   0 — success (uninstalled or dry-run completed)
#   1 — user cancelled or error

set -euo pipefail

# Resolve the project root: this script lives at .dev-aid/scripts/, so the
# project root is two directories up. Use a portable approach.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

NON_INTERACTIVE=false
DRY_RUN=false

for arg in "$@"; do
    case "$arg" in
        --yes|-y) NON_INTERACTIVE=true ;;
        --dry-run|-n) DRY_RUN=true ;;
        --help|-h)
            sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "Unknown argument: $arg" >&2
            echo "Run with --help for usage." >&2
            exit 1
            ;;
    esac
done

echo ""
echo -e "${BOLD}${CYAN}╔════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║      Dev-AID Uninstall                     ║${NC}"
echo -e "${BOLD}${CYAN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Project root: ${BOLD}${PROJECT_ROOT}${NC}"
echo ""

# Build the list of things that exist and would be removed.
declare -a TO_REMOVE=()

_maybe_add() {
    local path="$1"
    if [ -e "$path" ] || [ -L "$path" ]; then
        TO_REMOVE+=("$path")
    fi
}

_maybe_add "$PROJECT_ROOT/.dev-aid"
_maybe_add "$PROJECT_ROOT/CLAUDE.md"
_maybe_add "$PROJECT_ROOT/GEMINI.md"
_maybe_add "$PROJECT_ROOT/OPENAI.md"
_maybe_add "$PROJECT_ROOT/.claude"
_maybe_add "$PROJECT_ROOT/.gemini"
_maybe_add "$PROJECT_ROOT/.codex"

# Cursor rules: only remove rule files that mention dev-aid, not the whole dir
# (the user may have other Cursor rules unrelated to Dev-AID).
CURSOR_DEVAID_RULES=()
if [ -d "$PROJECT_ROOT/.cursor/rules" ]; then
    while IFS= read -r -d '' rule; do
        CURSOR_DEVAID_RULES+=("$rule")
    done < <(find "$PROJECT_ROOT/.cursor/rules" -maxdepth 1 -type f \( -name "*dev-aid*" -o -name "*devaid*" \) -print0 2>/dev/null)
fi

if [ ${#TO_REMOVE[@]} -eq 0 ] && [ ${#CURSOR_DEVAID_RULES[@]} -eq 0 ]; then
    echo -e "${GREEN}No Dev-AID artifacts found in this project. Nothing to uninstall.${NC}"
    exit 0
fi

echo -e "${YELLOW}The following Dev-AID artifacts will be removed:${NC}"
echo ""
for path in "${TO_REMOVE[@]}"; do
    if [ -L "$path" ]; then
        echo "  🔗 $path  (symlink)"
    elif [ -d "$path" ]; then
        echo "  📁 $path/"
    else
        echo "  📄 $path"
    fi
done
for rule in "${CURSOR_DEVAID_RULES[@]}"; do
    echo "  📄 $rule"
done
echo ""

# Memory bank export
MEMORY_BANK="$PROJECT_ROOT/.dev-aid/memory-bank"
if [ -d "$MEMORY_BANK" ]; then
    echo -e "${CYAN}Memory bank found at:${NC} $MEMORY_BANK"
    echo "  Contains your project context, decisions, and patterns."
    echo "  Recommend exporting before deletion."
    echo ""

    if [ "$DRY_RUN" = false ] && [ "$NON_INTERACTIVE" = false ]; then
        read -r -p "Export memory bank to ~/dev-aid-memory-export-$(date +%Y%m%d-%H%M%S)/? [Y/n] " export_reply
        if [[ ! "$export_reply" =~ ^[Nn]$ ]]; then
            export_dir="$HOME/dev-aid-memory-export-$(date +%Y%m%d-%H%M%S)"
            mkdir -p "$export_dir"
            cp -R "$MEMORY_BANK"/. "$export_dir/"
            echo -e "${GREEN}Exported to $export_dir${NC}"
            echo ""
        fi
    elif [ "$NON_INTERACTIVE" = true ]; then
        echo -e "${YELLOW}--yes mode: skipping memory bank export prompt.${NC}"
        echo "         (Memory bank will be deleted with the rest of .dev-aid/)"
        echo ""
    fi
fi

if [ "$DRY_RUN" = true ]; then
    echo -e "${CYAN}Dry-run mode: nothing was removed.${NC}"
    exit 0
fi

# Confirm
if [ "$NON_INTERACTIVE" = false ]; then
    echo -e "${RED}This is destructive and cannot be undone.${NC}"
    read -r -p "Proceed with uninstall? [y/N] " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 1
    fi
    echo ""
fi

# Remove
for path in "${TO_REMOVE[@]}"; do
    if [ -L "$path" ]; then
        rm -- "$path"
    else
        rm -rf -- "$path"
    fi
    echo -e "  ${GREEN}removed${NC} $path"
done
for rule in "${CURSOR_DEVAID_RULES[@]}"; do
    rm -- "$rule"
    echo -e "  ${GREEN}removed${NC} $rule"
done

echo ""
echo -e "${GREEN}✅ Dev-AID uninstalled.${NC}"
echo ""
echo -e "${CYAN}Suggested follow-up:${NC}"
echo "  git add -u && git status     # see what changed"
echo "  git commit -m 'chore: remove Dev-AID'"
echo ""
echo "Thanks for trying Dev-AID. Feedback: https://github.com/Probably-Group/Dev-AID/issues"
echo ""
