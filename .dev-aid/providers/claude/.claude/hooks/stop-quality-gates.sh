#!/usr/bin/env bash
set -euo pipefail
# Stop Hook - Quality Gates + Memory Bank Sync
# Runs when Claude Code stops responding

PROJECT_DIR="$CLAUDE_PROJECT_DIR"
MEMORY_BANK="$PROJECT_DIR/memory-bank"

echo ""
echo "🎯 Session Complete - Running Quality Checks..."
echo ""

# Quality Gate 1: Check for common issues
issues_found=0

# Check for TODO comments added
if git diff --cached 2>/dev/null | grep -q "TODO"; then
  echo "ℹ️  TODO comments added (remember to address them)"
fi

# Check for console.log/print statements
if git diff --cached 2>/dev/null | grep -qE "console\.log|print\("; then
  echo "⚠️  Debug statements detected (consider removing)"
  issues_found=$((issues_found + 1))
fi

# Check for .env or secrets
if git diff --cached 2>/dev/null | grep -qE "API_KEY|SECRET|PASSWORD"; then
  echo "🚨 WARNING: Potential secrets detected!"
  echo "   Review before committing"
  issues_found=$((issues_found + 1))
fi

# Quality Gate 2: Memory Bank Sync Reminder
if [ -f "$MEMORY_BANK/CLAUDE-activeContext.md" ]; then
  echo ""
  echo "💡 Consider updating memory bank:"
  echo "   Run: /update-memory-bank"
  echo ""
fi

# Summary
if [ $issues_found -eq 0 ]; then
  echo "✅ No quality issues detected"
else
  echo ""
  echo "⚠️  $issues_found potential issue(s) found - please review"
fi

echo ""
echo "📊 Session Summary:"
echo "  - Modified files: Check git status"
echo "  - Memory bank: Run /update-memory-bank if significant changes"
echo "  - Next steps: Check CLAUDE-activeContext.md"
echo ""

exit 0
