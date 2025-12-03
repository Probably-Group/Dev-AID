#!/bin/bash
# Session Start Hook - Load Memory Bank Foundation
# Auto-loads CLAUDE-activeContext.md (~300 tokens)
# Runs once per session

MEMORY_BANK_DIR="$CLAUDE_PROJECT_DIR/memory-bank"
ACTIVE_CONTEXT="$MEMORY_BANK_DIR/CLAUDE-activeContext.md"

# Check if memory bank exists
if [ ! -f "$ACTIVE_CONTEXT" ]; then
  echo "ℹ️  Memory Bank not found. Initialize with /update-memory-bank"
  exit 0
fi

# Load active context
echo "🧠 Loading Memory Bank..."
echo ""
echo "📋 Active Context loaded from: $ACTIVE_CONTEXT"
echo ""
echo "Available context files:"
echo "  - CLAUDE-activeContext.md (current session state)"
echo "  - CLAUDE-patterns.md (proven code patterns)"
echo "  - CLAUDE-decisions.md (architecture decisions)"
echo "  - CLAUDE-security.md (security patterns)"
echo "  - CLAUDE-performance.md (performance baselines)"
echo "  - CLAUDE-testing.md (test strategies)"
echo "  - CLAUDE-chaos.md (resilience experiments)"
echo ""
echo "💡 Load specific context with: 'Load CLAUDE-patterns.md'"
echo ""

# Display current session state summary
if grep -q "## 🎯 Current Sprint/Session Goals" "$ACTIVE_CONTEXT"; then
  echo "🎯 Current Session Goals:"
  grep -A 5 "## 🎯 Current Sprint/Session Goals" "$ACTIVE_CONTEXT" | grep "- \[ \]" | head -3
  echo ""
fi

# Exit successfully
exit 0
