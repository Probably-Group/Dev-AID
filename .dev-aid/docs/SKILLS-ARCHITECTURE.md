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
│   ├── expert/                      # Expert skills (auto-loaded by context)
│   │   ├── api-expert/
│   │   │   ├── SKILL.md             # Main skill (<500 lines)
│   │   │   └── references/          # Detailed documentation
│   │   │       ├── advanced-patterns.md
│   │   │       ├── anti-patterns.md
│   │   │       ├── performance-optimization.md
│   │   │       ├── security-examples.md
│   │   │       └── testing-guide.md
│   │   ├── devsecops-expert/
│   │   ├── typescript-expert/
│   │   └── ... (73 total expert skills)
│   └── registry/                    # 🆕 Hook-based auto-loading system
│       └── skills-index.json        # Activation metadata (keywords, patterns, scores)
│
├── orchestration/                   # 🆕 Skill auto-loading engine
│   ├── detect-context.sh            # Analyzes project context (tech stack, files)
│   ├── select-skills.sh             # Scores and selects relevant skills
│   └── context-detector.py          # Project context analyzer (Python)
│
├── providers/
│   ├── claude/.claude/
│   │   ├── skills -> ../../../skills  # Symlink to shared skills
│   │   └── hooks/
│   │       └── session-start.sh     # 🆕 Auto-loads skills at session start
│   ├── gemini/.gemini/
│   │   ├── skills -> ../../../skills  # Symlink to shared skills
│   │   ├── settings.json            # 🆕 Hook configuration
│   │   ├── GEMINI.md                # 🆕 Auto-generated skill references
│   │   └── hooks/
│   │       └── session-start.sh     # 🆕 Updates GEMINI.md at session start
│   ├── codex/.codex/                # 🆕 Codex CLI support
│   │   ├── skills/                  # Symlinks to shared skills
│   │   │   ├── core -> ../../../../skills/core
│   │   │   ├── expert -> ../../../../skills/expert
│   │   │   └── process -> ../../../../skills/process
│   │   └── hooks/
│   │       └── session-start.sh     # 🆕 Updates AGENTS.md at session start
│   └── openai/.openai/
│       └── skills -> ../../../skills  # Symlink to shared skills (future)
│
└── config/
    └── skill-rules.json              # Legacy auto-activation rules
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

# Codex provider (uses directory symlinks for each skill category)
.dev-aid/providers/codex/.codex/skills/core -> ../../../../skills/core
.dev-aid/providers/codex/.codex/skills/expert -> ../../../../skills/expert
.dev-aid/providers/codex/.codex/skills/process -> ../../../../skills/process

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

Use the `/dev-aid-build-skill` command:

```bash
/dev-aid-build-skill

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
Shared skills:  .dev-aid/skills/expert/ (73 skills)
Claude:         ✅ Access via symlink
Gemini:         ✅ Access via symlink
Codex:          ✅ Access via symlink
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

---

## 🆕 Hook-Based Auto-Loading System (v3.0)

**NEW as of 2025-12-05**: Intelligent skill auto-loading using SessionStart hooks for both Claude Code and Gemini CLI.

### Why Hook-Based Auto-Loading?

**Problems Solved:**
1. ❌ **Manual skill management** - Developers forget to activate relevant skills
2. ❌ **Context switching overhead** - Constantly loading/unloading skills manually
3. ❌ **GEMINI.md maintenance burden** - Updating skill list after every prompt
4. ❌ **No multi-provider consistency** - Different auto-loading for Claude vs Gemini

**Solutions Delivered:**
1. ✅ **Automatic context detection** - Scans project files, dependencies, tech stack
2. ✅ **Intelligent skill selection** - Scores skills by relevance using metadata
3. ✅ **SessionStart hooks** - Auto-loads skills once per session (not per prompt)
4. ✅ **Universal architecture** - Same logic for Claude, Gemini, and future providers

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Session Start (user runs: claude code / gemini chat)  │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────┐
│  SessionStart Hook (.claude/hooks/session-start.sh)     │
│  • Triggered automatically by provider                  │
│  • Runs ONCE per session (not per prompt)               │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────┐
│  Context Detection (detect-context.sh)                  │
│  • Scans: package.json, Cargo.toml, pyproject.toml      │
│  • Extracts: Dependencies, file patterns, technologies  │
│  • Output: "TypeScript React FastAPI Docker..."         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────┐
│  Skill Selection Engine (select-skills.sh)              │
│  • Reads: skills-index.json (activation metadata)       │
│  • Scores: Primary keywords (10pts), Technologies (8pts) │
│  • Filters: Excludes conflicts (graphql vs rest-api)    │
│  • Resolves: Auto-includes required dependencies        │
│  • Returns: Top 5 skills sorted by score                │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────┐
│  Provider Integration                                   │
│                                                          │
│  📘 Claude Code:                                         │
│     • Displays: "Auto-loading: python, bash-expert..."  │
│     • Skills available for activation when needed       │
│                                                          │
│  📗 Gemini CLI:                                          │
│     • Updates: GEMINI.md with @skill references         │
│     • GEMINI.md loaded with every prompt (but only      │
│       updated at session start)                         │
└─────────────────────────────────────────────────────────┘
```

### Components

#### 1. Skills Registry (skills-index.json)

External JSON database with activation metadata for all skills.

**Example entry:**
```json
{
  "api-expert": {
    "activation": {
      "primary_keywords": ["REST API", "RESTful", "OpenAPI", "Swagger"],
      "secondary_keywords": ["endpoint", "route", "HTTP method"],
      "file_patterns": ["*/routes/*", "*/api/*", "*.routes.ts"],
      "technologies": ["FastAPI", "Express", "Django REST"],
      "confidence_weights": {
        "OpenAPI": 0.3,
        "REST API": 0.25
      },
      "requires": ["devsecops-expert"],
      "exclude_with": ["graphql-expert"]
    }
  }
}
```

**Fields:**
- `primary_keywords`: High-value matches (10 points each)
- `secondary_keywords`: Supporting matches (5 points each)
- `file_patterns`: Glob patterns for file detection (8 points each)
- `technologies`: Framework/library names (8 points each)
- `confidence_weights`: Bonus scoring for specific keywords
- `requires`: Skills that must be included if this skill is selected
- `exclude_with`: Conflicting skills (e.g., GraphQL vs REST API)

#### 2. Context Detection (detect-context.sh)

Analyzes project to extract relevant keywords.

**Detection methods:**
1. **File patterns**: Dockerfile → Docker, package.json → Node.js
2. **Config parsing**: Extracts dependencies from package.json, requirements.txt
3. **Technology indicators**: Searches source code for framework imports

**Example output:**
```bash
$ .dev-aid/orchestration/detect-context.sh .
Bash scripts Python pip FastAPI Docker TypeScript Next.js
```

#### 3. Skill Selector (select-skills.sh)

Scores and ranks skills using registry metadata.

**Scoring algorithm:**
```bash
score = (primary_keyword_matches × 10) +
        (technology_matches × 8) +
        (secondary_keyword_matches × 5) +
        (confidence_weight_bonuses)
```

**Features:**
- Minimum score threshold (5 points)
- Excludes conflicting skills
- Auto-includes required dependencies
- Returns top N skills (default: 5)

**Example:**
```bash
$ context=$(.dev-aid/orchestration/detect-context.sh .)
$ .dev-aid/orchestration/select-skills.sh "$context" 5
python
bash-expert
typescript-expert
devsecops-expert
docker-expert
```

#### 4. SessionStart Hooks

**Claude Hook** (`.dev-aid/providers/claude/.claude/hooks/session-start.sh`):
```bash
#!/usr/bin/env bash
# Runs automatically when Claude Code session starts

# Detect context
context=$(.dev-aid/orchestration/detect-context.sh "$PROJECT_ROOT")

# Select skills
skills=$(.dev-aid/orchestration/select-skills.sh "$context" 5)

# Display to user
echo "✅ Auto-loading skills based on context:"
for skill in $skills; do
    echo "   📚 $skill"
done
```

**Gemini Hook** (`.dev-aid/providers/gemini/.gemini/hooks/session-start.sh`):
```bash
#!/usr/bin/env bash
# Runs automatically when Gemini CLI session starts

# Detect context
context=$(.dev-aid/orchestration/detect-context.sh "$PROJECT_ROOT")

# Select skills
skills=$(.dev-aid/orchestration/select-skills.sh "$context" 5)

# Update GEMINI.md ONCE at session start
cat > .gemini/GEMINI.md <<EOF
# Gemini Context - Auto-Generated at Session Start

## Active Skills
@../../../skills/expert/python/SKILL.md
@../../../skills/expert/bash-expert/SKILL.md
@../../../skills/expert/typescript-expert/SKILL.md
EOF

echo "✅ GEMINI.md updated and will be loaded with every prompt"
```

**Key difference**:
- Claude displays skills (user can activate manually)
- Gemini updates GEMINI.md (skills auto-loaded with every prompt)
- Codex updates AGENTS.md (skills loaded via @file references)

### Configuration

**Gemini settings.json** (`.dev-aid/providers/gemini/.gemini/settings.json`):
```json
{
  "hooks": {
    "SessionStart": {
      "command": ".dev-aid/providers/gemini/.gemini/hooks/session-start.sh",
      "enabled": true,
      "description": "Auto-loads relevant skills based on project context"
    }
  }
}
```

### Benefits

| Aspect | Before (Manual) | After (Hook-Based) |
|--------|----------------|-------------------|
| **Skill Loading** | Manual: `use api-expert skill` | Automatic at session start |
| **Context Awareness** | User must remember relevant skills | AI analyzes project and selects |
| **GEMINI.md Updates** | Manual edits every time | Auto-generated ONCE per session |
| **Multi-Provider** | Different logic per provider | Universal hook architecture |
| **Maintenance** | Update activation rules manually | Update registry once, works everywhere |
| **Performance** | N/A | GEMINI.md updated once (not per prompt) |

### Compliance & Validation

All scripts follow their respective skill guidelines, enforced by the **Validator Framework**:

**Bash scripts** (bash-expert skill — 14 checks):
- ✅ Strict mode (`set -euo pipefail`), IFS, cleanup traps
- ✅ Proper variable quoting, `[[ ]]` test brackets
- ✅ No dangerous patterns (eval, backticks, curl pipe)
- ✅ Local variables in functions, readonly constants

**Python files** (python skill — 8 AST checks):
- ✅ No `shell=True`, `eval()`/`exec()`, `pickle.load()`
- ✅ No hardcoded secrets, generic exceptions
- ✅ Type annotations, logging instead of print

**Running validators:**
```bash
# All validators (auto-discovered from skills)
python3 .dev-aid/scripts/run-validators.py --target-dir .

# Context-aware (only runs validators matching your tech stack)
python3 .dev-aid/scripts/run-validators.py --filter-context --target-dir .
```

**Extending:** Any skill can include a `validate.py` — the runner auto-discovers it. See [VALIDATOR-FRAMEWORK.md](VALIDATOR-FRAMEWORK.md).

---

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
3. **Follow template** - Use `/dev-aid-build-skill` command
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

- [aid-build-skill.md](../providers/claude/.claude/commands/setup/dev-aid-build-skill.md) - Skill creation template
- [skill-rules.json](../config/skill-rules.json) - Auto-activation configuration
- [CONTEXT-SHARING.md](CONTEXT-SHARING.md) - Multi-provider collaboration
- [DEV-AID-STYLE-GUIDE.md](DEV-AID-STYLE-GUIDE.md) - Coding standards

---

**Last Updated:** 2026-02-03
**Architecture Version:** 3.1 (Hook-Based Auto-Loading + Shared Skills + Codex CLI Support)
