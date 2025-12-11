---
name: linter
description: Auto-lint code on file save
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

# Linter - Compact

**Purpose**: Real-time linting feedback (catch issues immediately)

## Linter Detection

### JavaScript/TypeScript
- **ESLint** (`.eslintrc.*`, `eslint.config.*`)
- **Prettier** (`.prettierrc`, `prettier.config.*`)
- **Biome** (`biome.json`)

### Python
- **Flake8** (`setup.cfg`, `.flake8`)
- **Ruff** (`ruff.toml`, `pyproject.toml`)
- **Black** (auto-format)

### Rust
- **Clippy** (`cargo clippy`)
- **Rustfmt** (`rustfmt`)

### Go
- **golangci-lint** (`.golangci.yml`)
- **gofmt** (auto-format)

### Other
- **ShellCheck** (bash scripts)
- **Rubocop** (Ruby)

## Execution Strategy
- Check for config file existence
- Run linter on changed file only
- Auto-fix if supported (`--fix` flag)
- Report unfixable issues

## Output Format
```
✅ No lint issues
```

```
⚠️  3 lint issues found:
📍 user.ts:23 - Unused variable 'role'
📍 auth.ts:45 - Missing return type
📍 db.ts:12 - Prefer const over let

💡 Run with --fix: eslint --fix user.ts
```

## When to Skip
- No linter config found
- File in `.lintignore`
- `--no-lint` flag in commit message

**Token Budget**: ~250 tokens
**Mode**: Non-blocking suggestions
**Manual Override**: `/lint` command for full project lint
