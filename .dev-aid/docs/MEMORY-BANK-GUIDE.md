# Memory Bank Guide

## What is the Memory Bank?

The memory bank is a **shared knowledge base** that AI assistants (Claude, Gemini, Cursor, Copilot, etc.) read to understand your project's conventions, patterns, and decisions. Instead of repeating the same context every session, you document it once and all AI assistants follow it.

```
.dev-aid/memory-bank/
├── patterns.md       # Coding conventions and style guide
├── security.md       # Security rules AI must follow
├── decisions.md      # Architecture Decision Records (ADRs)
├── testing.md        # Testing standards
├── performance.md    # Performance guidelines
├── chaos.md          # Error handling and resilience patterns
└── activeContext.md  # Current sprint/focus (optional)
```

---

## Why Use It?

**Without memory-bank:**
```
You: "Add a new API endpoint"
AI: Creates endpoint with different style than existing code
You: "No, we use camelCase for functions"
AI: Fixes it
You: "Also we always validate input with Zod"
AI: Adds Zod
You: "And we use our custom error classes"
AI: Updates error handling
... (repeat every session)
```

**With memory-bank:**
```
You: "Add a new API endpoint"
AI: (reads patterns.md and security.md first)
AI: Creates endpoint matching your conventions, with Zod validation,
    using your error classes, following your naming patterns
```

---

## How AI Assistants Read It

### Claude Code

The generated `CLAUDE.md` includes file references that auto-load memory-bank:

```markdown
@.dev-aid/memory-bank/patterns.md
@.dev-aid/memory-bank/security.md
@.dev-aid/memory-bank/decisions.md
```

The `@` prefix tells Claude Code to include these files in context automatically.

### Gemini / Other AI

For AI assistants that don't support `@` references, the generated context file instructs them to read the files first:

```markdown
## Project Knowledge Base (READ FIRST)

**MUST READ** before starting work:
- `.dev-aid/memory-bank/patterns.md` - Coding conventions
- `.dev-aid/memory-bank/security.md` - Security rules
- `.dev-aid/memory-bank/decisions.md` - Architecture decisions
```

### Manual Loading

You can also explicitly ask any AI to read the files:

```
You: "Read .dev-aid/memory-bank/patterns.md and follow those conventions"
```

---

## Setting Up Memory Bank

### 1. Initialize Dev-AID

```bash
./.dev-aid/scripts/setup-dev-aid.sh
```

This creates the memory-bank directory with template files.

### 2. Customize the Files

Edit each file to match your project:

**patterns.md** - Define your coding conventions:
```markdown
## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | kebab-case | `user-service.ts` |
| Functions | camelCase | `getUserById` |
| Classes | PascalCase | `UserService` |
```

**security.md** - Define security rules:
```markdown
## Security Rules

- Never hardcode API keys (use environment variables)
- Always validate input with Zod at API boundaries
- Use parameterized queries (never string concatenation)
```

**decisions.md** - Document architecture choices:
```markdown
## ADR-001: Use PostgreSQL over MongoDB

**Status**: Accepted

**Context**: Need ACID compliance for financial transactions

**Decision**: Use PostgreSQL with Prisma ORM

**Consequences**: Better data integrity, but less flexible schema
```

### 3. Regenerate Context File (if needed)

If you set up Dev-AID before customizing memory-bank:

```bash
./.dev-aid/scripts/reconfigure.sh
```

This regenerates `CLAUDE.md` with updated memory-bank references.

---

## File Reference

### patterns.md

**Purpose**: Coding conventions AI must follow

**Contents**:
- Naming conventions (files, variables, functions)
- Code style patterns
- File organization
- Anti-patterns to avoid
- Example code snippets

**AI reads this to**: Write code that matches your existing style

### security.md

**Purpose**: Security rules that are non-negotiable

**Contents**:
- Input validation requirements
- Authentication/authorization patterns
- Secret management rules
- Common vulnerabilities to avoid
- Security scanning tools used

**AI reads this to**: Generate secure code by default

### decisions.md

**Purpose**: Architecture Decision Records (ADRs)

**Contents**:
- Technical decisions and rationale
- Alternatives considered
- Trade-offs accepted

**AI reads this to**: Understand why things are built a certain way and respect those decisions

### testing.md

**Purpose**: Testing standards

**Contents**:
- Test structure patterns
- Coverage goals
- What to test / what not to test
- Testing tools used

**AI reads this to**: Write tests that match your standards

### performance.md

**Purpose**: Performance guidelines

**Contents**:
- Performance targets (P95, LCP, etc.)
- Optimization patterns
- Caching strategies
- Known bottlenecks

**AI reads this to**: Write performant code and avoid common pitfalls

### chaos.md

**Purpose**: Error handling and resilience

**Contents**:
- Error handling patterns
- Circuit breaker configurations
- Retry strategies
- Logging guidelines

**AI reads this to**: Implement proper error handling

### activeContext.md

**Purpose**: Current sprint/session state (optional)

**Contents**:
- Current sprint goals
- Active work items
- Known blockers
- Quick reference commands

**AI reads this to**: Understand what you're currently working on

---

## Engine Features

### Token Budget

The orchestration router enforces a **token budget** on memory bank content to prevent context window bloat. Configure in `settings.json`:

```json
{
  "memory_bank": {
    "standing_context_tokens": 1000,
    "standing_context_budget": "balanced"
  }
}
```

**Budget modes**:

| Mode | Multiplier | Behavior |
|------|-----------|----------|
| `minimal` | 0.5x | Half budget, strict keyword matching (2+ keyword matches required) |
| `balanced` | 1.0x | Default, 1+ keyword match for on-demand files |
| `generous` | 2.0x | Double budget, loads all on-demand files regardless of query |

Auto-load files are **always included** (never dropped). If auto-load alone exceeds budget, a warning is logged but content is preserved. On-demand files are added in list order until budget is exhausted.

### On-Demand Loading

Files listed in `on_demand` are loaded based on query relevance, not unconditionally:

```json
{
  "memory_bank": {
    "auto_load": ["activeContext.md"],
    "on_demand": ["patterns.md", "decisions.md", "security.md",
                   "performance.md", "testing.md", "chaos.md"]
  }
}
```

The router uses **keyword matching** to select relevant on-demand files. For example:
- A security-related prompt loads `security.md`
- A testing prompt loads `testing.md`
- Multiple topics can load multiple files

### Section-Level Extraction

When an on-demand file exceeds the remaining token budget, the router doesn't just truncate — it **extracts the most relevant sections** based on keyword overlap with the user's prompt. Sections are scored and included in relevance order. A truncation notice is appended: `*[Truncated: X of Y sections shown]*`.

### Staleness Detection

Each loaded memory bank file gets age metadata. Files older than `staleness_warning_days` (default: 30) are annotated with a warning:

```
*Last updated: 45 days ago — WARNING: may be outdated | 245 tokens*
```

Recent files show a normal annotation:
```
*Last updated: 3 days ago | 120 tokens*
```

Configure the threshold:
```json
{
  "memory_bank": {
    "staleness_warning_days": 14
  }
}
```

### Write-Back Instructions

The system prompt automatically includes a **Memory Bank Maintenance** section when memory bank content is loaded. This instructs AI assistants to update the appropriate files when they learn something significant:

- New coding patterns → `patterns.md`
- Architecture decisions → `decisions.md`
- Security concerns → `security.md`
- Testing strategy changes → `testing.md`

Updates should be appended with timestamps (`- **YYYY-MM-DD**: [what was learned]`), never deleting existing content unless explicitly asked.

The stop hook also reminds users which files to update at session end.

---

## Best Practices

### 1. Start with patterns.md and security.md

These have the highest impact. AI assistants will immediately write better code.

### 2. Keep it concise

AI assistants have context limits. Focus on rules that matter:

```markdown
# Good - Specific and actionable
- Use `getUserById` not `get_user_by_id` (camelCase for functions)
- Always wrap external API calls in try/catch

# Bad - Too vague
- Write clean code
- Handle errors properly
```

### 3. Include examples

```markdown
## Error Handling

```typescript
// ✅ Do this
try {
  const user = await fetchUser(id);
} catch (error) {
  logger.error('Failed to fetch user', { userId: id, error });
  throw new AppError('USER_FETCH_FAILED', 'Unable to retrieve user');
}

// ❌ Don't do this
const user = await fetchUser(id); // No error handling
```
```

### 4. Update when patterns change

When you establish new conventions or make architecture decisions, add them to memory-bank.

### 5. Review periodically

Remove outdated patterns, update deprecated decisions.

---

## Troubleshooting

### AI isn't following patterns

1. **Check if files exist**: `ls -la .dev-aid/memory-bank/`
2. **Check CLAUDE.md references**: Look for `@.dev-aid/memory-bank/` lines
3. **Explicitly ask**: "Read `.dev-aid/memory-bank/patterns.md` first"

### Files not auto-loading

The `@` file reference feature requires Claude Code. For other tools:
- Add instructions to your context file to read memory-bank first
- Or paste the content manually at session start

### Too much context

If memory-bank files are too large:
- Split into must-read (patterns, security) vs. optional (performance, chaos)
- Keep each file under 500 lines
- Link to external docs for details

---

## Related Documentation

- [CONTEXT-SHARING.md](CONTEXT-SHARING.md) - Multi-model context passing
- [STORAGE-LOCATIONS.md](STORAGE-LOCATIONS.md) - Where Dev-AID stores data
- [FAQ.md](FAQ.md) - Common questions

---

## Summary

| File | Purpose | Priority |
|------|---------|----------|
| `patterns.md` | Coding conventions | **High** - Customise first |
| `security.md` | Security rules | **High** - Critical for safe code |
| `decisions.md` | Architecture decisions | **Medium** - Add as you make decisions |
| `testing.md` | Testing standards | **Medium** - Useful for test generation |
| `performance.md` | Performance guidelines | **Low** - Add when relevant |
| `chaos.md` | Error handling | **Low** - Add when relevant |
| `activeContext.md` | Current focus | **Optional** - For session continuity |

**Key takeaway**: Document your conventions once, AI follows them every session.
