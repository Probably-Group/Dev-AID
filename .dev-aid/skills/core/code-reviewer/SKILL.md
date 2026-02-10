---
name: code-reviewer
description: "Provides real-time lightweight code quality feedback on file save covering smells, security, and performance. Key capabilities: long function/deep nesting detection, N+1 query patterns, SQL injection/XSS checks, missing error handling alerts. Use when completing code changes, saving edited files. Do NOT use for documentation-only changes, config files, or non-code assets."
version: 1.0.0
category: core
auto_load: true
token_budget: 250
triggers:
  - file_save
  - edit_complete
tools:
  - Read
  - Grep
---

# Code Reviewer - Compact

**Purpose**: Real-time code quality feedback (lightweight, non-blocking)

## Quick Checks

### Code Smells
- Long functions (>50 lines)
- Deep nesting (>3 levels)
- Duplicated code
- Magic numbers
- God classes

### Common Issues
- Missing error handling
- No input validation
- Hardcoded values
- TODO comments
- Console.log statements

### Performance
- N+1 query patterns
- Unnecessary loops
- Missing indexes hints
- Blocking operations

### Security Quick Wins
- SQL injection risks
- XSS vulnerabilities
- Hardcoded secrets
- Missing authentication checks

## Suggestions Format
```
💡 Suggestion: [Issue]
📍 Location: file.ts:45
✨ Fix: [Quick fix]
```

**Token Budget**: ~250 tokens
**Mode**: Non-blocking suggestions only
**Deep Analysis**: Use `@config-safety-reviewer` agent
