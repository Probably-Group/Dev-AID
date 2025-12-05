# Skills Architecture

## Overview

Dev-AID uses a **provider-agnostic shared skills architecture** that allows all AI providers (Claude, Gemini, OpenAI, etc.) to access the same expert skills without duplication.

## Directory Structure

```
.dev-aid/
├── skills/                          # Shared skills (provider-agnostic)
│   ├── core/                        # Core skills (always loaded)
│   │   ├── code-reviewer/
│   │   │   └── SKILL.md
│   │   └── secret-scanner/
│   │       └── SKILL.md
│   └── expert/                      # Expert skills (auto-loaded by context)
│       ├── api-expert/
│       │   ├── SKILL.md             # Main skill (<500 lines)
│       │   └── references/          # Detailed documentation
│       │       ├── advanced-patterns.md
│       │       ├── anti-patterns.md
│       │       ├── performance-optimization.md
│       │       ├── security-examples.md
│       │       └── testing-guide.md
│       ├── devsecops-expert/
│       ├── typescript-expert/
│       └── ... (66 total expert skills)
│
├── providers/
│   ├── claude/.claude/
│   │   └── skills -> ../../../skills  # Symlink to shared skills
│   ├── gemini/.gemini/
│   │   └── skills -> ../../../skills  # Symlink to shared skills
│   └── openai/.openai/
│       └── skills -> ../../../skills  # Symlink to shared skills (future)
│
└── config/
    └── skill-rules.json              # Auto-activation rules
```

## Key Principles

### 1. Single Source of Truth

Skills are stored once in `.dev-aid/skills/` and referenced by all providers:

- ✅ **No duplication** - Update once, all providers benefit
- ✅ **Consistent behavior** - Same skill logic across all AIs
- ✅ **Easier maintenance** - Single location for updates
- ✅ **Version control friendly** - Track skills in one place

### 2. Provider Agnostic

Providers access skills via symlinks:

```bash
# Claude provider
.dev-aid/providers/claude/.claude/skills -> ../../../skills

# Gemini provider
.dev-aid/providers/gemini/.gemini/skills -> ../../../skills

# Future providers follow same pattern
.dev-aid/providers/openai/.openai/skills -> ../../../skills
```

### 3. Auto-Activation Rules

Skills auto-load based on file patterns and context (configured in `skill-rules.json`):

```json
{
  "id": "security-context",
  "trigger": {
    "files": ["*auth*", "*security*", "*.env*"],
    "patterns": ["security", "authentication", "crypto"]
  },
  "skills": ["devsecops-expert", "owasp-guardian"],
  "reason": "Security-sensitive code detected"
}
```

## Skill Structure Requirements

### File Size Constraint

**⚠️ CRITICAL:** Main `SKILL.md` files **MUST be under 500 lines**.

**Why?** Claude Code cannot load files over 500 lines, making oversized skills unusable.

**Solution:** Extract verbose content to `references/` directory:

```
skill-name/
├── SKILL.md                           # Core concepts, workflow (<500 lines)
└── references/                        # Detailed documentation
    ├── advanced-patterns.md           # Complex implementation patterns
    ├── anti-patterns.md               # Common mistakes to avoid
    ├── performance-optimization.md    # Performance strategies
    ├── security-examples.md           # Security implementations
    ├── testing-guide.md               # Comprehensive testing
    └── threat-model.md                # Security analysis (if applicable)
```

### Required Sections

Every `SKILL.md` must include:

1. **Section 0: Anti-Hallucination Protocol**
   - Verification requirements before implementing code
   - Common hallucination traps for this domain
   - Self-check checklist

2. **Core Principles**
   - TDD first
   - Security by default
   - Performance aware

3. **Implementation Workflow**
   - Test-first development approach
   - Essential patterns

4. **References Section**
   - Links to detailed documentation in `references/`

## Creating New Skills

Use the `/aid-build-skill` command:

```bash
/aid-build-skill

→ Skill name: mongodb-expert
→ Technology: MongoDB database design
→ Expertise: schema design, indexing, aggregation
→ Risk level: MEDIUM
→ Security sensitive: Y
→ Model: Sonnet

✅ Skill created at: .dev-aid/skills/expert/mongodb-expert/
```

The command automatically:
- Creates skill in shared location (`.dev-aid/skills/expert/`)
- Enforces 500-line limit with validation
- Creates standard reference files
- Updates skill activation rules

## Migration from Provider-Specific Skills

Skills were migrated from provider-specific locations to shared architecture:

**Before:**
```
.dev-aid/providers/claude/.claude/skills/expert/api-expert/
```

**After:**
```
.dev-aid/skills/expert/api-expert/
  ↑
  └── Referenced by all providers via symlinks
```

## Benefits for Multi-Provider Teams

### Before (Provider-Specific)
```
Claude skills:  .dev-aid/providers/claude/.claude/skills/expert/ (66 skills)
Gemini skills:  ❌ None - Gemini can't use Claude's skills
Result:         Gemini has no expert knowledge
```

### After (Shared)
```
Shared skills:  .dev-aid/skills/expert/ (66 skills)
Claude:         ✅ Access via symlink
Gemini:         ✅ Access via symlink
OpenAI:         ✅ Access via symlink (future)
Result:         All providers have same expertise
```

## Automatic Skill Loading

### Core Skills (Always Loaded)

Located in `.dev-aid/skills/core/`:
- `code-reviewer` - Reviews code quality and security
- `secret-scanner` - Detects hardcoded secrets

### Expert Skills (Context-Based)

Located in `.dev-aid/skills/expert/`:
- Auto-load based on file patterns (`.test.ts` → `tdd-master`)
- Auto-load based on keywords (`security` → `devsecops-expert`)
- Manual activation: `use api-expert skill`

## Skill Activation Flow

```
User edits file: api/routes/auth.ts
         ↓
Skill Rules Engine analyzes:
  - File path matches: */routes/*
  - Keywords: "api", "auth"
         ↓
Auto-loads skills:
  - api-expert
  - devsecops-expert
         ↓
AI Provider (Claude/Gemini/etc.):
  - Reads skills from .dev-aid/skills/
  - Applies expert knowledge
  - Follows TDD workflow
```

## Maintenance

### Adding Skills

1. Create in shared location: `.dev-aid/skills/expert/new-skill/`
2. Ensure `SKILL.md` is under 500 lines
3. Extract verbose content to `references/`
4. Update `skill-rules.json` for auto-activation

### Updating Skills

1. Edit skill in `.dev-aid/skills/expert/skill-name/`
2. Change applies to all providers automatically
3. If exceeding 500 lines, extract to `references/`

### Removing Skills

1. Delete from `.dev-aid/skills/expert/skill-name/`
2. Remove activation rules from `skill-rules.json`
3. Skills disappear for all providers

## Verification

Check skills are accessible by all providers:

```bash
# Verify shared skills
ls -la .dev-aid/skills/expert/

# Verify Claude symlink
ls -la .dev-aid/providers/claude/.claude/skills
# Should show: skills -> ../../../skills

# Verify Gemini symlink
ls -la .dev-aid/providers/gemini/.gemini/skills
# Should show: skills -> ../../../skills

# Count skills
echo "Expert skills: $(ls .dev-aid/skills/expert/ | wc -l)"
echo "Core skills: $(ls .dev-aid/skills/core/ | wc -l)"
```

Expected output:
```
Expert skills: 66
Core skills: 2
```

## Best Practices

1. **Keep SKILL.md under 500 lines** - Use `references/` for details
2. **Use shared location** - Never create provider-specific skills
3. **Follow template** - Use `/aid-build-skill` command
4. **Test across providers** - Verify skills work with Claude AND Gemini
5. **Document changes** - Update skill when domain changes

## Troubleshooting

**Problem:** New skill not auto-loading

**Solution:**
1. Check `skill-rules.json` for activation patterns
2. Verify file path/keywords match trigger conditions
3. Manually load: `use skill-name skill`

**Problem:** Skill over 500 lines won't load

**Solution:**
1. Extract verbose sections to `references/`
2. Keep only core concepts in `SKILL.md`
3. Run verification: `wc -l .dev-aid/skills/expert/skill-name/SKILL.md`

**Problem:** Skill not accessible by Gemini

**Solution:**
1. Verify symlink exists: `ls -la .dev-aid/providers/gemini/.gemini/skills`
2. If missing, create: `ln -s ../../../skills .dev-aid/providers/gemini/.gemini/skills`

## Related Documentation

- [aid-build-skill.md](../providers/claude/.claude/commands/setup/aid-build-skill.md) - Skill creation template
- [skill-rules.json](../config/skill-rules.json) - Auto-activation configuration
- [CONTEXT-SHARING.md](CONTEXT-SHARING.md) - Multi-provider collaboration
- [DEV-AID-STYLE-GUIDE.md](DEV-AID-STYLE-GUIDE.md) - Coding standards

---

**Last Updated:** 2025-12-05
**Architecture Version:** 2.0 (Shared Skills)
