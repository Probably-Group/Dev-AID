---
name: dev-aid-review-staged
description: Review staged changes before committing (Rubber Duck Pre-Reviewer)
category: quality
version: 1.0.0
author: Dev-AID Team
---

# Review Staged Changes - Rubber Duck Pre-Reviewer

Comprehensive pre-commit review of staged changes by a simulated senior developer.

## Purpose

Catch issues before they enter the codebase:
- Debug code left behind (console.log, debugger, print statements)
- Poor naming (a, tmp, data, thing, stuff)
- Missing tests for new functionality
- Security vulnerabilities (hardcoded secrets, SQL injection)
- Performance anti-patterns (N+1 queries, unnecessary loops)
- Code smells (long functions, deep nesting, duplicated code)

## Task

1. **Get staged changes:**
   ```bash
   git diff --cached --stat
   git diff --cached
   ```

2. **Analyze changes by focus area (if specified):**

   **Default (comprehensive review):**
   - Code quality (naming, structure, complexity)
   - Security (secrets, injection, auth)
   - Tests (coverage, missing tests)
   - Performance (obvious bottlenecks)
   - Best practices (language-specific idioms)

   **Focus areas (via --focus flag):**
   - `--focus security`: Security-only review (secrets, injection, auth)
   - `--focus tests`: Test coverage and quality
   - `--focus performance`: Performance anti-patterns
   - `--focus style`: Code style and naming

3. **Review persona:**
   Act as a senior developer doing code review:
   - Constructive, not critical
   - Explain WHY issues matter
   - Suggest concrete fixes
   - Prioritize by severity (🔴 Blocker, 🟡 Warning, 🔵 Suggestion)

4. **Output format:**
   ```
   📊 Staged Changes Review
   ═══════════════════════════════════════

   Files: 5 modified, 2 added (+247, -83 lines)

   🔴 BLOCKERS (must fix before commit):

   1. Hardcoded API key detected
      📍 auth-service.ts:45
      const API_KEY = "sk_live_abc123..."

      ❌ Problem: Credentials will be exposed in git history
      ✅ Fix: Use environment variables
      ```typescript
      const API_KEY = process.env.STRIPE_API_KEY
      ```

   2. SQL injection vulnerability
      📍 user-controller.ts:23
      db.query(`SELECT * FROM users WHERE id = ${userId}`)

      ❌ Problem: Allows arbitrary SQL execution
      ✅ Fix: Use parameterized queries
      ```typescript
      db.query('SELECT * FROM users WHERE id = ?', [userId])
      ```

   🟡 WARNINGS (should fix):

   3. Missing tests for new feature
      📍 payment-processor.ts (new file)

      ❌ Problem: 156 lines of untested code
      ✅ Fix: Add unit tests for happy path + edge cases

   4. Debug code left behind
      📍 checkout.ts:78, cart.ts:123, inventory.ts:45
      console.log(...) × 3 instances

      ❌ Problem: Clutters production logs
      ✅ Fix: Remove or replace with proper logging

   🔵 SUGGESTIONS (nice to have):

   5. Long function (87 lines)
      📍 order-service.ts:processOrder()

      💡 Consider: Extract to smaller functions
      - validateOrder()
      - calculateTotal()
      - chargePayment()
      - sendConfirmation()

   ═══════════════════════════════════════
   Summary:
   - 🔴 2 blockers (fix before committing)
   - 🟡 2 warnings (strongly recommended)
   - 🔵 1 suggestion (optional improvement)

   ✅ Ready to commit? Run: git commit -m "your message"
   ❌ Found blockers? Fix them first, then review again
   ```

5. **If no staged changes:**
   ```
   ℹ️  No staged changes to review

   💡 Stage changes first:
   git add <files>

   Or review unstaged changes:
   git diff
   ```

## Focus Examples

**Security focus:**
```bash
/dev-aid-review-staged --focus security
```
Only checks for:
- Hardcoded secrets (API keys, passwords, tokens)
- SQL/NoSQL injection
- XSS vulnerabilities
- Missing authentication/authorization
- Insecure crypto usage

**Test focus:**
```bash
/dev-aid-review-staged --focus tests
```
Only checks for:
- Missing tests for new code
- Insufficient test coverage
- Missing edge cases
- Test quality issues

**Performance focus:**
```bash
/dev-aid-review-staged --focus performance
```
Only checks for:
- N+1 query patterns
- Unnecessary loops
- Blocking operations in async code
- Missing indexes hints
- Memory leaks

## Integration with Git Hooks

Can be added to pre-commit hook:
```bash
# .git/hooks/pre-commit
#!/bin/bash
claude run /dev-aid-review-staged --focus security

# If blockers found, prompt user
read -p "Found security issues. Commit anyway? (y/N) " -n 1 -r
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi
```

## Comparison to code-reviewer Core Skill

| Feature | code-reviewer (core skill) | /dev-aid-review-staged |
|---------|---------------------------|------------------------|
| **When** | On file save (automatic) | On demand (before commit) |
| **Scope** | Single file | All staged changes |
| **Detail** | Quick suggestions (~250 tokens) | Comprehensive review |
| **Focus** | Real-time feedback | Pre-commit gate |
| **Blocking** | Non-blocking | Optional (can block commit) |

## Best Practices

1. **Run before every commit**
   - Catches issues early
   - Saves review time later
   - Prevents broken builds

2. **Use focus flags for speed**
   - Security-critical commits → `--focus security`
   - Feature work → `--focus tests`
   - Performance work → `--focus performance`

3. **Don't ignore warnings**
   - Warnings become blockers in production
   - Fix them while context is fresh

4. **Add to pre-commit hook**
   - Automatic gate for security issues
   - Consistent quality across team

## Value Proposition

**Time savings:**
- 5-10 min/commit catching issues early
- 30-60 min saved in PR review time
- Prevents production incidents (priceless)

**For 100 developers:**
- 5 commits/day/dev × 5 min = 25 min/day/dev
- 100 devs × 25 min = 2,500 min/day = 42 hours/day
- Annual: 42 hrs/day × 250 days = 10,500 hours
- At $100/hr: **$1,050,000/year** in prevented rework

## Related Commands

- `/dev-aid-code-health` - Overall codebase quality
- `/dev-aid-debt-analysis` - Technical debt assessment
- `/dev-aid-vulnerability-scan` - Deep security scanning
