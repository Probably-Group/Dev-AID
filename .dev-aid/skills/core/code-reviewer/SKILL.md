---
name: code-reviewer
description: Real-time code quality checks during development
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
