#!/usr/bin/env bash
set -euo pipefail
# User Prompt Submit Hook - Conservative Skill Suggestions
# File pattern matching, max 2-3 suggestions
# High confidence only.
#
# This hook prints skill suggestions to stdout based on file/keyword patterns.
# Claude Code surfaces this output as session context — Claude can then decide
# whether to load the suggested skills. The hook itself does not load skills.

# Default environment variables to empty to prevent crashes under set -u
CLAUDE_USER_PROMPT="${CLAUDE_USER_PROMPT:-}"
CLAUDE_CONTEXT_FILES="${CLAUDE_CONTEXT_FILES:-}"
CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"

# Get current files from context (if available in CLAUDE_CONTEXT env var)
CURRENT_FILES="${CLAUDE_CONTEXT_FILES:-}"

# Simple pattern matching based on file extensions and names
suggestions=""
suggestion_count=0
max_suggestions=3

# Testing context (high confidence)
if echo "$CURRENT_FILES" | grep -qE '\.(test|spec)\.(ts|js|tsx|jsx|py)$|__tests__|tests/'; then
  if [ $suggestion_count -lt $max_suggestions ]; then
    suggestions+="💡 Suggested skill: tdd-master (test file detected)\n"
    suggestion_count=$((suggestion_count + 1))
  fi
fi

# Security context (high confidence)
if echo "$CURRENT_FILES" | grep -qE 'auth|login|security|crypto|password|\.env'; then
  if [ $suggestion_count -lt $max_suggestions ]; then
    suggestions+="💡 Suggested skill: devsecops-expert (security file detected)\n"
    suggestion_count=$((suggestion_count + 1))
  fi
  if [ $suggestion_count -lt $max_suggestions ]; then
    suggestions+="💡 Suggested skill: owasp-guardian (security context)\n"
    suggestion_count=$((suggestion_count + 1))
  fi
fi

# Database context (high confidence)
if echo "$CURRENT_FILES" | grep -qE 'migration|schema|model|entity|repository'; then
  if [ $suggestion_count -lt $max_suggestions ]; then
    suggestions+="💡 Suggested skill: database-design (database file detected)\n"
    suggestion_count=$((suggestion_count + 1))
  fi
fi

# API context (high confidence)
if echo "$CURRENT_FILES" | grep -qE 'route|controller|endpoint|api/'; then
  if [ $suggestion_count -lt $max_suggestions ]; then
    suggestions+="💡 Suggested skill: api-expert (API file detected)\n"
    suggestion_count=$((suggestion_count + 1))
  fi
fi

# Frontend context (high confidence)
if echo "$CURRENT_FILES" | grep -qE '\.(tsx|jsx)$|component|pages/'; then
  if [ $suggestion_count -lt $max_suggestions ]; then
    suggestions+="💡 Suggested skill: frontend-dev-guidelines (React file detected)\n"
    suggestion_count=$((suggestion_count + 1))
  fi
fi

# CI/CD context (high confidence)
if echo "$CURRENT_FILES" | grep -qE '\.github/workflows/|\.gitlab-ci\.yml|Jenkinsfile|pipeline'; then
  if [ $suggestion_count -lt $max_suggestions ]; then
    suggestions+="💡 Suggested skill: cicd-expert (CI/CD file detected)\n"
    suggestion_count=$((suggestion_count + 1))
  fi
fi

# Output suggestions
if [ -n "$suggestions" ]; then
  echo ""
  echo "🎯 Skill Suggestions (Conservative Strategy):"
  echo -e "$suggestions"
  echo ""
  echo "💡 Available commands:"
  echo "  - @agent-name for deep analysis"
  echo "  - /command-name for workflows"
  echo ""
fi

# Medium confidence suggestions (don't auto-load)
if echo "$CLAUDE_USER_PROMPT" | grep -qiE 'performance|slow|optimize|bottleneck'; then
  echo "💡 Suggestion: Consider loading performance-expert skill"
fi

if echo "$CLAUDE_USER_PROMPT" | grep -qiE 'refactor|clean code|SOLID|design pattern'; then
  echo "💡 Suggestion: Consider clean-code and design-patterns skills"
fi

exit 0
