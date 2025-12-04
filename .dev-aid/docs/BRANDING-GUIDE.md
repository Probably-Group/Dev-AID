# DevAID Branding Guide

**Official Name**: DevAID
**Technical Name**: dev-aid (in paths/code)
**Local Search**: DevAID Local Search

---

## Naming Conventions

### User-Facing (Marketing/Documentation)
- ✅ **"DevAID"** - Clean, professional, no hyphen
- ✅ **"DevAID Local Search"** - Our RAG feature name
- ✅ **"DevAID Router"** - Multi-AI orchestration
- ✅ **"DevAID Memory Bank"** - Persistent context storage

### Technical (Paths/Code)
- ✅ **`dev-aid`** - Directory names, file paths (lowercase with hyphen)
- ✅ **`.dev-aid/`** - Configuration directory
- ✅ **`dev-aid-search`** - Standalone commands (lowercase with hyphen)
- ✅ **`/aid-*`** - Slash commands (just "aid" prefix, e.g., `/aid-router-challenger`)

### Examples

**Correct Usage**:
```markdown
# User-facing documentation
Welcome to DevAID! DevAID brings enterprise-grade AI capabilities...

# Installation paths
cd .dev-aid/scripts
./setup-venv.sh

# Standalone command usage
dev-aid-search index .

# Slash command usage
/aid-router-challenger "Implement auth"
/aid-audit
```

**Incorrect Usage**:
```markdown
# Avoid these
Dev-AID (old branding with hyphen in marketing)
DEV-AID (all caps)
DevAid (mixed inconsistently)
dev-aid (in marketing docs - use DevAID)
DevAID/scripts/ (in paths - use .dev-aid/)
devaid-search (missing hyphen - use dev-aid-search)
```

---

## Component Naming

### DevAID Local Search (RAG Component)

**User-Facing Name**: "DevAID Local Search"
**Attribution**: "Powered by claude-context-local by [FarhanAliRaza](https://github.com/FarhanAliRaza)"

**Why the rename?**
- ✅ "DevAID Local Search" is tool-agnostic (works with Claude, Gemini, Cursor)
- ✅ "claude-context-local" implies Claude-only (confusing for multi-tool users)
- ✅ Gives proper credit to original project while using clear branding
- ✅ Users see "DevAID Local Search" in documentation and UI
- ✅ Developers still use `claude-context-local` command (underlying engine)

**Implementation**:
- Documentation refers to "DevAID Local Search"
- Attribution links to claude-context-local project
- Wrapper command: `dev-aid-search` (user-friendly, follows naming convention)
- Underlying tool: `claude-context-local` (technical)

---

## Attribution Policy

### Required Attribution

Whenever mentioning DevAID Local Search in documentation:

**Short form**:
```markdown
DevAID Local Search - 100% local semantic code search
Powered by claude-context-local by FarhanAliRaza
```

**Full form** (in acknowledgments):
```markdown
**[claude-context-local](https://github.com/FarhanAliRaza/claude-context-local)**
by [FarhanAliRaza](https://github.com/FarhanAliRaza) - Powers DevAID Local Search
with 100% local semantic code search using EmbeddingGemma
```

### In Code Comments

```bash
#!/bin/bash
# Setup script for DevAID Local Search
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
❌ .DevAID/
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
❌ DevAIDSearch             # Wrong: CamelCase
❌ devaidSearch             # Wrong: camelCase
❌ devaid-search            # Wrong: missing hyphen after dev
```

**Slash commands** (just "aid" prefix):
```bash
✅ /aid-router-challenger   # Slash command
✅ /aid-audit               # Slash command
✅ /aid-build-skill         # Slash command
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
# DevAID (use official branding)
## DevAID Local Search
## DevAID Router
```

### Body Text

First mention:
```markdown
**DevAID** is an AI development framework...
```

Subsequent mentions:
```markdown
DevAID integrates with Claude Code, Cursor, and Gemini CLI...
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
Use `/aid-router-challenger "task"` for two-AI review.
Run `/aid-audit` to scan for security issues.
```

---

## Code Examples

### Bash Scripts

```bash
#!/bin/bash
# DevAID Setup Script
# Part of DevAID (Development AI Driver)

echo "Installing DevAID Local Search..."
# Uses .dev-aid/ paths
cd .dev-aid/scripts
./setup-rag.sh
```

### Documentation Code Blocks

````markdown
```bash
# Install DevAID Local Search
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
DevAID
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
- Content: `1.0.0` (semantic versioning)
- Reference: "DevAID v1.0.0" (in documentation)

### Changelog Headers
```markdown
# DevAID Changelog

## [1.0.0] - 2025-12-04

This is the first production-ready release of DevAID...
```

---

## Migration from Old Branding

### What Changed
- ❌ **Old**: "Dev-AID" (with hyphen)
- ✅ **New**: "DevAID" (no hyphen)
- ❌ **Old**: "claude-context-local" (in user docs)
- ✅ **New**: "DevAID Local Search" (with attribution)

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
| **Marketing** | DevAID |
| **Documentation headers** | DevAID |
| **Directory paths** | `.dev-aid/` |
| **Standalone commands** | `dev-aid-search` |
| **Slash commands** | `/aid-router-*` |
| **RAG feature** | DevAID Local Search |
| **Router feature** | DevAID Router |
| **File references** | `.dev-aid/config/routing.json` |
| **Attribution** | Powered by claude-context-local by FarhanAliRaza |

---

**Version**: 1.0.0
**Last Updated**: 2025-12-04
**Status**: ✅ Official branding guidelines
