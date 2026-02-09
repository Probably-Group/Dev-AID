#!/usr/bin/env bash
# Dev-AID update notification (non-blocking, throttled)
# Called from session-start hooks. Checks at most once per day.
# Uses a GLOBAL cache (~/.cache/dev-aid/) so multiple projects share one API call.
# Outputs a message to stdout if an update is available, nothing otherwise.

set -euo pipefail

cleanup() { rm -f "${FETCH_TMP:-}" 2>/dev/null; }
trap cleanup EXIT

PROJECT_ROOT="${1:-.}"
VERSION_FILE="$PROJECT_ROOT/.dev-aid/VERSION"
REPO="Probably-Group/Dev-AID"
CHECK_INTERVAL=86400  # 24 hours in seconds

# Global cache — one API call per day regardless of how many projects use Dev-AID
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/dev-aid"
CACHE_FILE="$CACHE_DIR/.update-check-cache"

# Silent exit if no VERSION file
[ -f "$VERSION_FILE" ] || exit 0

LOCAL_VERSION="$(tr -d '[:space:]' < "$VERSION_FILE")"

# Read cached remote version (may be from another project's session)
cached_remote=""
need_fetch=true

mkdir -p "$CACHE_DIR"
if [ -f "$CACHE_FILE" ]; then
    last_check="$(head -1 "$CACHE_FILE")"
    now="$(date +%s)"
    elapsed=$((now - last_check))
    if [ "$elapsed" -lt "$CHECK_INTERVAL" ]; then
        need_fetch=false
        cached_remote="$(sed -n '2p' "$CACHE_FILE" 2>/dev/null || echo "")"
    fi
fi

if [ "$need_fetch" = true ]; then
    # Check remote version via GitHub API
    if ! command -v gh >/dev/null 2>&1; then
        exit 0
    fi

    # Run gh api in background with a 3s watchdog to avoid blocking session start
    FETCH_TMP=$(mktemp "$CACHE_DIR/.version-fetch.XXXXXX")
    gh api "repos/$REPO/contents/.dev-aid/VERSION" --jq '.content' 2>/dev/null > "$FETCH_TMP" &
    GH_PID=$!

    # Wait up to 3 seconds
    for _ in 1 2 3; do
        if ! kill -0 "$GH_PID" 2>/dev/null; then
            break
        fi
        sleep 1
    done

    # Kill if still running
    if kill -0 "$GH_PID" 2>/dev/null; then
        kill "$GH_PID" 2>/dev/null || true
        rm -f "$FETCH_TMP"
        exit 0
    fi

    if [ -f "$FETCH_TMP" ]; then
        cached_remote="$(base64 -d < "$FETCH_TMP" 2>/dev/null | tr -d '[:space:]')" || true
        rm -f "$FETCH_TMP"
    fi

    # Write global cache (timestamp + remote version)
    echo "$(date +%s)" > "$CACHE_FILE"
    echo "${cached_remote:-}" >> "$CACHE_FILE"
fi

# Compare this project's local version against the cached remote
if [ -n "$cached_remote" ] && [ "$cached_remote" != "$LOCAL_VERSION" ]; then
    echo "Update available: $LOCAL_VERSION -> $cached_remote (run: gh dev-aid update)"
fi
