# Dev-AID Branding Guide

**Official Name**: Dev-AID
**Technical Name**: dev-aid (in paths/code)
**Local Search**: Dev-AID Local Search

---

## Naming Conventions

### User-Facing (Marketing/Documentation)
- ✅ **"Dev-AID"** - Clean, professional, no hyphen
- ✅ **"Dev-AID Local Search"** - Our RAG feature name
- ✅ **"Dev-AID Router"** - Multi-AI orchestration
- ✅ **"Dev-AID Memory Bank"** - Persistent context storage

### Technical (Paths/Code)
- ✅ **`dev-aid`** - Directory names, file paths (lowercase with hyphen)
- ✅ **`.dev-aid/`** - Configuration directory
- ✅ **`dev-aid-search`** - Standalone commands (lowercase with hyphen)
- ✅ **`/dev-aid-*`** - Slash commands (just "aid" prefix, e.g., `/dev-aid-router-challenger`)

### Examples

**Correct Usage**:
```markdown
# User-facing documentation
Welcome to Dev-AID! Dev-AID brings enterprise-grade AI capabilities...

# Installation paths
cd .dev-aid/scripts
./setup-venv.sh

# Standalone command usage
dev-aid-search index .

# Slash command usage
/dev-aid-router-challenger "Implement auth"
/dev-aid-audit
```

**Incorrect Usage**:
```markdown
# Avoid these
Dev-AID (old branding with hyphen in marketing)
DEV-AID (all caps)
DevAid (mixed inconsistently)
dev-aid (in marketing docs - use Dev-AID)
Dev-AID/scripts/ (in paths - use .dev-aid/)
devaid-search (missing hyphen - use dev-aid-search)
```

---

## Component Naming

### Dev-AID Local Search (RAG Component)

**User-Facing Name**: "Dev-AID Local Search"
**Attribution**: "Powered by claude-context-local by [FarhanAliRaza](https://github.com/FarhanAliRaza)"

**Why the rename?**
- ✅ "Dev-AID Local Search" is tool-agnostic (works with Claude, Gemini, Cursor)
- ✅ "claude-context-local" implies Claude-only (confusing for multi-tool users)
- ✅ Gives proper credit to original project while using clear branding
- ✅ Users see "Dev-AID Local Search" in documentation and UI
- ✅ Developers still use `claude-context-local` command (underlying engine)

**Implementation**:
- Documentation refers to "Dev-AID Local Search"
- Attribution links to claude-context-local project
- Wrapper command: `dev-aid-search` (user-friendly, follows naming convention)
- Underlying tool: `claude-context-local` (technical)

---

## Attribution Policy

### Required Attribution

Whenever mentioning Dev-AID Local Search in documentation:

**Short form**:
```markdown
Dev-AID Local Search - 100% local semantic code search
Powered by claude-context-local by FarhanAliRaza
```

**Full form** (in acknowledgments):
```markdown
**[claude-context-local](https://github.com/FarhanAliRaza/claude-context-local)**
by [FarhanAliRaza](https://github.com/FarhanAliRaza) - Powers Dev-AID Local Search
with 100% local semantic code search using EmbeddingGemma
```

### In Code Comments

```bash
#!/bin/bash
# Setup script for Dev-AID Local Search
# Installs and configures 100% local semantic code search
# Powered by claude-context-local by FarhanAliRaza
```

---

## File Naming

### Configuration Directory

Always use `.dev-aid/` (lowercase with hyphen):
```
✅ .dev-aid/config/
✅ .dev-aid/scripts/
✅ .dev-aid/memory-bank/
❌ .Dev-AID/
❌ .devaid/
```

**Why lowercase with hyphen?**
- ✅ Unix/Linux convention for hidden directories
- ✅ Readable and conventional
- ✅ Easy to type in terminal

### Command Names

**Standalone commands** (lowercase with hyphen):
```bash
✅ dev-aid-search           # Executable command
✅ router-cli.sh            # Script file
✅ setup-venv.sh            # Script file
❌ Dev-AIDSearch             # Wrong: CamelCase
❌ devaidSearch             # Wrong: camelCase
❌ devaid-search            # Wrong: missing hyphen after dev
```

**Slash commands** (just "aid" prefix):
```bash
✅ /dev-aid-router-challenger   # Slash command
✅ /dev-aid-audit               # Slash command
✅ /dev-aid-build-skill         # Slash command
❌ /devaid-router           # Wrong: don't use "devaid"
❌ /dev-aid-router          # Wrong: too long for slash commands
```

**Why different?**
- Standalone commands need full `dev-aid-*` for clarity when executed
- Slash commands use short `aid-*` prefix (already namespaced by `/`)

---

## Documentation Style

### Headers

```markdown
# Dev-AID (use official branding)
## Dev-AID Local Search
## Dev-AID Router
```

### Body Text

First mention:
```markdown
**Dev-AID** is an AI development framework...
```

Subsequent mentions:
```markdown
Dev-AID integrates with Claude Code, Cursor, Gemini CLI, and Codex CLI...
```

### Technical References

```markdown
# When referencing paths
The `.dev-aid/` directory contains...
Edit `.dev-aid/config/routing.json`...

# When referencing standalone commands
Run `dev-aid-search index .` to index your code.
Use `./.dev-aid/scripts/setup-rag.sh` to install.

# When referencing slash commands
Use `/dev-aid-router-challenger "task"` for two-AI review.
Run `/dev-aid-audit` to scan for security issues.
```

---

## Code Examples

### Bash Scripts

```bash
#!/bin/bash
# Dev-AID Setup Script
# Part of Dev-AID (Development AI Driver)

echo "Installing Dev-AID Local Search..."
# Uses .dev-aid/ paths
cd .dev-aid/scripts
./setup-rag.sh
```

### Documentation Code Blocks

````markdown
```bash
# Install Dev-AID Local Search
./.dev-aid/scripts/setup-rag.sh

# Index your codebase
dev-aid-search index .

# Check status
dev-aid-search status
```
````

---

## Logo and Visual Assets

### Text Logo
```
Dev-AID
```
- Font: Clean sans-serif
- No hyphen
- Capital D, A, I, D

### Icon
- Use existing dev-aid-logo-small.png
- Path: `./img/dev-aid-logo-small.png` (keep path as-is)

---

## Changelog and Versioning

### Version Files
- File: `.dev-aid/VERSION` (technical path)
- Content: `1.5.1` (semantic versioning, current)
- Reference: "Dev-AID v1.5.1" (in documentation)

### Changelog Headers
```markdown
# Dev-AID Changelog

## [1.5.1] - 2026-04-08

Current release of Dev-AID...
```

---

## Migration from Old Branding

### What Changed
- ❌ **Old**: "Dev-AID" (with hyphen)
- ✅ **New**: "Dev-AID" (no hyphen)
- ❌ **Old**: "claude-context-local" (in user docs)
- ✅ **New**: "Dev-AID Local Search" (with attribution)

### What Stayed the Same
- ✅ Technical paths: `.dev-aid/` (unchanged)
- ✅ Repository name: Can stay as "Dev-AID" (GitHub URL)
- ✅ Underlying tool: Still uses `claude-context-local`

### Update Checklist
- [x] README.md (all references updated)
- [x] CHANGELOG.md
- [x] FAQ.md
- [x] STORAGE-LOCATIONS.md
- [x] UPDATING.md
- [x] DEPENDENCY-ISOLATION.md
- [x] setup-rag.sh script
- [x] Acknowledgments section
- [x] Created devaid-search wrapper

---

## Quick Reference Card

| Context | Use |
|---------|-----|
| **Marketing** | Dev-AID |
| **Documentation headers** | Dev-AID |
| **Directory paths** | `.dev-aid/` |
| **Standalone commands** | `dev-aid-search` |
| **Slash commands** | `/dev-aid-router-*` |
| **RAG feature** | Dev-AID Local Search |
| **Router feature** | Dev-AID Router |
| **File references** | `.dev-aid/config/routing.json` |
| **Attribution** | Powered by claude-context-local by FarhanAliRaza |

---

**Version**: 1.0.0
**Last Updated**: 2025-12-04
**Status**: ✅ Official branding guidelines
