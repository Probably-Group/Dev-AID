#!/usr/bin/env bash
# Dev-AID update notification (non-blocking, throttled)
# Called from session-start hooks. Checks at most once per day.
# Outputs a message to stdout if an update is available, nothing otherwise.

set -euo pipefail

PROJECT_ROOT="${1:-.}"
VERSION_FILE="$PROJECT_ROOT/.dev-aid/VERSION"
CACHE_DIR="$PROJECT_ROOT/.dev-aid/temp"
CACHE_FILE="$CACHE_DIR/.update-check-cache"
REPO="Probably-Group/Dev-AID"
CHECK_INTERVAL=86400  # 24 hours in seconds

# Silent exit if no VERSION file
[ -f "$VERSION_FILE" ] || exit 0

LOCAL_VERSION="$(cat "$VERSION_FILE" | tr -d '[:space:]')"

# Throttle: skip if checked recently
mkdir -p "$CACHE_DIR"
if [ -f "$CACHE_FILE" ]; then
    last_check="$(cat "$CACHE_FILE" | head -1)"
    now="$(date +%s)"
    elapsed=$((now - last_check))
    if [ "$elapsed" -lt "$CHECK_INTERVAL" ]; then
        # Show cached result if update was available
        cached_version="$(sed -n '2p' "$CACHE_FILE" 2>/dev/null || echo "")"
        if [ -n "$cached_version" ] && [ "$cached_version" != "$LOCAL_VERSION" ]; then
            echo "Update available: $LOCAL_VERSION -> $cached_version (run: gh dev-aid update)"
        fi
        exit 0
    fi
fi

# Check remote version via GitHub API
if ! command -v gh >/dev/null 2>&1; then
    exit 0
fi

# Run gh api in background with a 3s watchdog to avoid blocking session start
REMOTE_VERSION=""
gh api "repos/$REPO/contents/.dev-aid/VERSION" --jq '.content' 2>/dev/null > "$CACHE_DIR/.version-fetch" &
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
    rm -f "$CACHE_DIR/.version-fetch"
    exit 0
fi

if [ -f "$CACHE_DIR/.version-fetch" ]; then
    REMOTE_VERSION="$(base64 -d < "$CACHE_DIR/.version-fetch" 2>/dev/null | tr -d '[:space:]')" || true
    rm -f "$CACHE_DIR/.version-fetch"
fi

[ -n "$REMOTE_VERSION" ] || exit 0

# Cache the result
echo "$(date +%s)" > "$CACHE_FILE"
if [ -n "$REMOTE_VERSION" ] && [ "$REMOTE_VERSION" != "$LOCAL_VERSION" ]; then
    echo "$REMOTE_VERSION" >> "$CACHE_FILE"
    echo "Update available: $LOCAL_VERSION -> $REMOTE_VERSION (run: gh dev-aid update)"
else
    echo "" >> "$CACHE_FILE"
fi
