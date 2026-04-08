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
# These are convenience symlinks Dev-AID drops at project root pointing
# into .dev-aid/backups/. They become broken symlinks after we remove
# .dev-aid/, so clean them up explicitly.
_maybe_add "$PROJECT_ROOT/CLAUDE_original-backup.md"
_maybe_add "$PROJECT_ROOT/GEMINI_original-backup.md"
_maybe_add "$PROJECT_ROOT/OPENAI_original-backup.md"

# ─────────────────────────────────────────────────────────────────────
# Find user's pre-Dev-AID originals so we can restore them.
#
# When Dev-AID installs, it moves any pre-existing CLAUDE.md / GEMINI.md
# / OPENAI.md to .dev-aid/backups/<NAME>_original-backup_TIMESTAMP.md
# and replaces the project-root file with a symlink into .dev-aid/. If
# we just remove .dev-aid/ without restoring, the user PERMANENTLY
# LOSES their original context file. That's a data-loss bug, so we
# rescue the originals before destroying the backup directory.
#
# Strategy: pick the OLDEST timestamped backup for each provider — the
# oldest one is the user's true pre-Dev-AID original. Subsequent
# backups are Dev-AID-modified versions from later re-installs.
# ─────────────────────────────────────────────────────────────────────
declare -A RESTORE_MAP=()  # provider_name → backup_path_to_restore_from

_find_oldest_backup() {
    # Print the path to the oldest backup file matching the pattern.
    # Args: $1 = backup directory, $2 = filename glob (e.g. "CLAUDE_original-backup_*.md")
    local backup_dir="$1"
    local glob="$2"
    [ -d "$backup_dir" ] || return 1
    # Sort filenames (timestamps embedded in name) and take first.
    # Resolve any nested symlinks and verify the target is a real file.
    local first
    first=$(find "$backup_dir" -maxdepth 1 -type f -name "$glob" 2>/dev/null | sort | head -1)
    if [ -n "$first" ] && [ -s "$first" ]; then
        echo "$first"
        return 0
    fi
    return 1
}

if [ -d "$PROJECT_ROOT/.dev-aid/backups" ]; then
    for provider in CLAUDE GEMINI OPENAI; do
        backup_path=$(_find_oldest_backup "$PROJECT_ROOT/.dev-aid/backups" "${provider}_original-backup_*.md") || continue
        RESTORE_MAP["$provider"]="$backup_path"
    done
fi

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

# Show what we're going to restore from backups
if [ ${#RESTORE_MAP[@]} -gt 0 ]; then
    echo -e "${GREEN}Pre-Dev-AID originals that will be RESTORED before removal:${NC}"
    echo ""
    for provider in "${!RESTORE_MAP[@]}"; do
        local_target="$PROJECT_ROOT/${provider}.md"
        local_source="${RESTORE_MAP[$provider]}"
        echo "  📥 $local_source"
        echo "      → ${local_target} (your pre-Dev-AID version)"
    done
    echo ""
fi

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

# ─────────────────────────────────────────────────────────────────────
# STEP 1: Rescue the user's pre-Dev-AID originals BEFORE we touch
# anything destructive. We copy them to a safe temp location first,
# then restore after the symlinks/.dev-aid are gone.
# ─────────────────────────────────────────────────────────────────────
declare -A RESTORE_TEMP=()
if [ ${#RESTORE_MAP[@]} -gt 0 ]; then
    echo ""
    echo -e "${CYAN}Rescuing pre-Dev-AID originals to a temp directory...${NC}"
    rescue_dir=$(mktemp -d "${TMPDIR:-/tmp}/dev-aid-rescue-XXXXXX")
    for provider in "${!RESTORE_MAP[@]}"; do
        src="${RESTORE_MAP[$provider]}"
        tmp_copy="$rescue_dir/${provider}.md"
        if cp -- "$src" "$tmp_copy"; then
            RESTORE_TEMP["$provider"]="$tmp_copy"
            echo -e "  ${GREEN}rescued${NC} ${provider}.md (${src})"
        else
            echo -e "  ${RED}WARNING${NC}: failed to rescue $src — ${provider}.md will be LOST"
        fi
    done
    echo ""
fi

# ─────────────────────────────────────────────────────────────────────
# STEP 2: Remove all Dev-AID artifacts (the destructive part).
# ─────────────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────────────
# STEP 3: Restore the rescued originals to project root.
# ─────────────────────────────────────────────────────────────────────
if [ ${#RESTORE_TEMP[@]} -gt 0 ]; then
    echo ""
    echo -e "${CYAN}Restoring pre-Dev-AID originals to project root...${NC}"
    for provider in "${!RESTORE_TEMP[@]}"; do
        target="$PROJECT_ROOT/${provider}.md"
        src="${RESTORE_TEMP[$provider]}"
        if mv -- "$src" "$target"; then
            echo -e "  ${GREEN}restored${NC} $target"
        else
            echo -e "  ${RED}WARNING${NC}: failed to restore $target from $src"
            echo -e "  ${YELLOW}Your original is at:${NC} $src"
            echo -e "  ${YELLOW}Recover with:${NC} mv '$src' '$target'"
        fi
    done
    # Clean up rescue dir if it's empty
    rmdir "$rescue_dir" 2>/dev/null || true
    echo ""
fi

echo ""
echo -e "${GREEN}✅ Dev-AID uninstalled.${NC}"
echo ""
echo -e "${CYAN}Suggested follow-up:${NC}"
echo "  git add -u && git status     # see what changed"
echo "  git commit -m 'chore: remove Dev-AID'"
echo ""
echo "Thanks for trying Dev-AID. Feedback: https://github.com/Probably-Group/Dev-AID/issues"
echo ""
