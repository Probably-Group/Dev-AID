---
name: type-checker
description: Auto-check types on file save
version: 1.0.0
category: core
auto_load: true
token_budget: 250
triggers:
  - file_save
  - edit_complete
tools:
  - Bash
  - Read
---

# Type Checker - Compact

**Purpose**: Real-time type checking (catch errors before runtime)

## Type System Detection

### TypeScript
- **tsc** (`tsconfig.json`)
- Run: `tsc --noEmit` (check only, no output)
- Fast incremental checking

### Python
- **mypy** (`mypy.ini`, `pyproject.toml`)
- **pyright** (`.pyrightconfig.json`)
- **pyre** (`.pyre_configuration`)

### Rust
- **cargo check** (faster than `cargo build`)
- Type errors from compiler

### Go
- **go build** (type checking built-in)
- No additional config needed

## Execution Strategy
- Incremental checks (changed files only)
- Use project's tsconfig/mypy config
- Cache results for performance
- Skip if no type system detected

## Output Format
```
✅ No type errors
```

```
🔴 3 type errors found:
📍 user.ts:45 - Property 'role' is missing in type 'User'
📍 auth.ts:23 - Argument of type 'string' is not assignable to 'number'
📍 db.ts:12 - Cannot find name 'Databse' (typo?)

💡 Fix type errors to prevent runtime crashes
```

## When to Skip
- No type system config found
- JavaScript without TypeScript
- Python without type hints
- File explicitly marked `# type: ignore`

**Token Budget**: ~250 tokens
**Mode**: Non-blocking warnings
**Full Check**: `/type-check` command for complete project check
