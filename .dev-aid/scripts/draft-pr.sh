#!/usr/bin/env bash
# PR Storyteller - Semantic PR Description Generator
# Analyzes git diff and generates structured PR descriptions

set -euo pipefail

readonly BLUE='\033[0;34m'
readonly GREEN='\033[0;32m'
readonly NC='\033[0m'

main() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🎨 PR Storyteller${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Check if in git repo
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "❌ Not in a git repository"
        exit 1
    fi

    echo "📊 Analyzing changes..."

    # Get diff stats
    files_changed=$(git diff --stat origin/main 2>/dev/null | tail -1 || echo "No changes")

    # Get commit messages
    commits=$(git log --oneline origin/main..HEAD 2>/dev/null || echo "No commits")

    # Generate PR template
    echo -e "\n${GREEN}━━━ PR Description Template ━━━${NC}\n"

    cat <<EOF
## Summary
[Describe the high-level intent of this PR]

## Changes
\`\`\`
$files_changed
\`\`\`

## Commits
\`\`\`
$commits
\`\`\`

## Verification
- [ ] Tests pass locally
- [ ] Lint checks pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented if present)

## Risk Assessment
[Low/Medium/High - Describe potential side effects]

---
🤖 Generated with PR Storyteller
EOF

    echo ""
    echo -e "${GREEN}✅ PR template generated!${NC}"
    echo "Copy the above to your PR description or redirect to file:"
    echo "  $0 > pr-description.md"
}

main "$@"
