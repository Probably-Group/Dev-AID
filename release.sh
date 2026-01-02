#!/usr/bin/env bash
# Release Script for Smart Context File Initialization
# Run this script to complete the PR and beta release

set -euo pipefail

echo "🚀 Dev-AID Release Helper"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check git status
echo "📊 Current Status:"
echo "  Branch: $(git rev-parse --abbrev-ref HEAD)"
echo "  Latest commit: $(git log -1 --oneline)"
echo "  Remote status: $(git status -sb | head -1)"
echo ""

# Create beta tag
echo "🏷️  Creating beta tag..."
if git tag -l | grep -q "v1.0.0-beta.1"; then
    echo "  ⚠️  Tag v1.0.0-beta.1 already exists locally"
    read -p "  Delete and recreate? [y/N]: " recreate
    if [[ "$recreate" =~ ^[Yy] ]]; then
        git tag -d v1.0.0-beta.1
        echo "  ✓ Deleted local tag"
    fi
fi

if ! git tag -l | grep -q "v1.0.0-beta.1"; then
    git tag -a v1.0.0-beta.1 -m "Beta release: Smart context file initialization

Features:
- Smart initialization for CLAUDE.md, GEMINI.md, OPENAI.md
- Zero data loss with automatic backups
- Content validation and auto-fixing
- Progressive disclosure for files >500 lines
- Pre-commit hooks for code quality
- Provider-specific templates
- Comprehensive migration reports"
    echo "  ✓ Created tag v1.0.0-beta.1"
else
    echo "  ℹ️  Using existing tag v1.0.0-beta.1"
fi

# Push tag
echo ""
echo "📤 Pushing tag to remote..."
if git push origin v1.0.0-beta.1 2>&1; then
    echo "  ✓ Tag pushed successfully"
else
    echo "  ⚠️  Failed to push tag (you may need to do this manually)"
    echo "  Run: git push origin v1.0.0-beta.1"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Local setup complete!"
echo ""
echo "📋 Next Steps (Click these links):"
echo ""
echo "1️⃣  Create Pull Request:"
echo "   https://github.com/martinholovsky/Dev-AID/pull/new/claude/claude-md-initialization-plan-blJSY"
echo ""
echo "   Title: Smart Context File Initialization for All Providers"
echo "   Copy description from: PR_DESCRIPTION.md"
echo ""
echo "2️⃣  Create Beta Release:"
echo "   https://github.com/martinholovsky/Dev-AID/releases/new?tag=v1.0.0-beta.1&target=claude/claude-md-initialization-plan-blJSY"
echo ""
echo "   Tag: v1.0.0-beta.1"
echo "   Title: v1.0.0-beta.1 - Smart Context File Initialization"
echo "   Copy description from: BETA_RELEASE_NOTES.md"
echo "   ✅ Check 'This is a pre-release'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
