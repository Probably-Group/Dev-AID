---
name: aid-router-challenger-rag
description: Challenger mode with local semantic code search (100% local, $0 cost)
tags: [routing, multi-ai, security, review, rag, semantic-search]
---

# Challenger Mode with Local RAG

Execute the request with **Challenger mode + Semantic Search**: search the codebase for relevant context, generate with that context, then review for security issues.

## Step 1: MUST call `search_code` MCP tool

Before generating anything, you MUST invoke the `search_code` tool from the `code-search` MCP server to find relevant code context.

**Tool call:**
```
Tool: search_code
Arguments: { "query": "<extract key terms from the user's request>", "limit": 10 }
```

Extract meaningful search terms from the user's request. For example:
- "Implement OAuth2 authentication" → query: "OAuth2 authentication JWT token"
- "Add password reset" → query: "password reset email verification"
- "Fix payment processing" → query: "payment processing Stripe checkout"

**If `search_code` is not available**, fall back to reading memory bank files directly:
- `.dev-aid/memory-bank/security.md`
- `.dev-aid/memory-bank/patterns.md`
- `.dev-aid/memory-bank/activeContext.md`

## Step 2: Generate implementation

Using the search results as context:
- Follow existing patterns found in the codebase
- Reference similar implementations from search results
- Apply security best practices from memory bank

## Step 3: Self-review for security issues

Review your own implementation against:
- **OWASP Top 10** vulnerabilities (injection, broken auth, XSS, etc.)
- **Logic errors** (race conditions, edge cases, off-by-one)
- **Performance issues** (N+1 queries, memory leaks)
- **Consistency** with existing codebase patterns from search results

## Step 4: Refine if issues found

Address any issues identified in the review. Provide the improved implementation.

## Step 5: Output format

```markdown
## Relevant Context Found
[Code snippets from search_code results]

## Implementation
[Your solution, following existing patterns]

## Security Review
ISSUES FOUND: <number>
SEVERITY: <LOW|MEDIUM|HIGH|CRITICAL>

1. [Issue] — Location: [where] — Risk: [what could go wrong]
   Fix: [specific remediation]

POSITIVE: [What follows best practices]

## Final Implementation
[Refined version addressing all issues, or original if no issues found]
```

Begin the RAG-enhanced challenger workflow now with the user's request: $ARGUMENTS
